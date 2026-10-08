# SemiAutomaticClassificationPlugin
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised
# classification of remote sensing images, providing tools for the download,
# the preprocessing and postprocessing of images.
# begin: 2012-12-29
# Copyright (C) 2026 by Krzysztof Tyszko.
# Author: Krzysztof Tyszko
# Email: krzysztof_tyszko@outlook.com
#
# This file is part of SemiAutomaticClassificationPlugin.
# SemiAutomaticClassificationPlugin is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# SemiAutomaticClassificationPlugin is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with SemiAutomaticClassificationPlugin.
# If not, see <https://www.gnu.org/licenses/>.


# Outlier detection core of the SCP plugin.
#
# This module is intentionally QGIS-free (no cfg, no PyQt): it only depends on
# numpy/scipy/scikit-learn and GDAL/OGR, so the filter implementations can be
# imported and tested on their own. Orchestration (signature catalog handling,
# progress bars, messages) stays in interface/remove_outliers.py.

import numpy as np
from osgeo import gdal, ogr, osr
from scipy.ndimage import binary_erosion
from scipy.stats import chi2, f as f_dist
from sklearn.covariance import MinCovDet, EllipticEnvelope, EmpiricalCovariance
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import LocalOutlierFactor, NearestNeighbors
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

_RANDOM_SEED = 42
# fit-time subsample cap for superlinear estimators (IsolationForest, OneClassSVM)
SAMPLE_CAP = 10000


# Minimum number of pixels that must remain in a ROI after cleaning for the
# signature to stay usable by parametric methods: an invertible covariance
# matrix requires more than B+1 observations, and Maximum Likelihood skips
# signatures below that limit. A ROI reduced below the threshold is treated as
# removed entirely.
def min_surviving_pixels(bands):
    return bands + 2

_VSIMEM_COUNTER = [0]


def _noop(_msg):
    pass


def scale_data(data, scaler="standard"):
    # Robustness to outliers comes from the detection methods themselves, for
    # example from the MinCovDet robust covariance estimator, and not from this
    # step. scaler=None disables scaling.
    if scaler is None:
        return data, None

    if scaler == "standard":
        sc = StandardScaler()
    else:
        raise ValueError(f"Unknown scaler: {scaler}")

    data_scaled = sc.fit_transform(data)
    return data_scaled, sc


# Extracts non-NaN pixels from a band stack into a flat array.
def prepare_valid_pixels(stack):
    bands = stack.shape[0]
    data = stack.transpose(1, 2, 0).reshape(-1, bands)
    valid_mask = ~np.isnan(data).any(axis=1)
    data_valid = data[valid_mask]

    return data_valid, valid_mask


# Maps a per-valid-pixel boolean mask back to the 2D grid.
def rebuild_mask(mask_valid, valid_mask_flat, ysize, xsize):
    full_mask = np.zeros(valid_mask_flat.shape[0], dtype=bool)
    full_mask[valid_mask_flat] = mask_valid
    return full_mask.reshape(ysize, xsize)


# Strips non-alphanumeric chars and lowercases a method name for comparison.
def normalize_method_name(method_name):
    cleaned = str(method_name).lower()
    return "".join(ch for ch in cleaned if ch.isalnum())


def mad_filter_stack(stack, threshold=3.5):
    valid_mask = np.all(~np.isnan(stack), axis=0)

    median = np.nanmedian(stack, axis=(1, 2), keepdims=True)
    mad = np.nanmedian(np.abs(stack - median), axis=(1, 2), keepdims=True)
    mad = np.where(mad == 0, 1, mad)

    modified_z = 0.6745 * (stack - median) / mad
    outlier_mask = np.any(np.abs(modified_z) > threshold, axis=0)

    final_mask = valid_mask & (~outlier_mask)
    filtered_stack = np.where(final_mask[None, :, :], stack, np.nan)

    scores = np.nanmax(np.abs(modified_z), axis=0)

    return filtered_stack, final_mask, scores


# MAD variant operating on an N x B observation matrix (group mode). The median
# and MAD are computed per band from the observation pool; an observation is an
# outlier when any band exceeds the threshold. Masks are equivalent to
# mad_filter_stack for the same pixel set.
def mad_filter_flat(data, threshold=3.5):
    median = np.median(data, axis=0, keepdims=True)
    mad = np.median(np.abs(data - median), axis=0, keepdims=True)
    mad = np.where(mad == 0, 1, mad)

    modified_z = 0.6745 * (data - median) / mad
    scores = np.max(np.abs(modified_z), axis=1)
    mask = scores <= threshold
    return mask, scores


def erosion_filter(stack, iterations=1, log_error=_noop, log_info=_noop):
    valid_mask = np.all(~np.isnan(stack), axis=0)
    no_change = (
        stack.copy(),
        valid_mask,
        np.zeros(valid_mask.shape, dtype=np.float32),
    )

    try:
        eroded = binary_erosion(valid_mask, iterations=iterations)
    except Exception as err:
        log_error("erosion_filter failed: %s — no pixels removed" % err)
        return no_change

    if not np.any(eroded):
        log_info(
            "erosion_filter (iterations=%d) erased entire ROI — kept original mask"
            % iterations
        )
        return no_change

    final_mask = valid_mask & eroded
    filtered_stack = np.where(final_mask[None, :, :], stack, np.nan)
    scores = (~eroded & valid_mask).astype(np.float32)
    return filtered_stack, final_mask, scores


def _mahalanobis_cutoff(threshold, alpha, df):
    if alpha is not None:
        return float(chi2.ppf(1.0 - float(alpha), df))
    if threshold is None:
        threshold = 3.0
    return float(threshold) ** 2


def mahalanobis_filter(data, threshold=None, alpha=None, robust=False):
    cov = (
        MinCovDet(random_state=_RANDOM_SEED).fit(data)
        if robust
        else EmpiricalCovariance().fit(data)
    )
    md = cov.mahalanobis(data)
    cutoff = _mahalanobis_cutoff(threshold, alpha, df=data.shape[1])
    mask = md <= cutoff
    return mask, md


def _resolve_pca_components(n_components, variance_ratio, n_features):
    # A variance_ratio in (0, 1) is passed through, so scikit-learn keeps as
    # many components as that share of variance requires. Otherwise a fixed
    # number is used, clipped to the number of features.
    if variance_ratio is not None and 0.0 < float(variance_ratio) < 1.0:
        return float(variance_ratio)
    return max(1, min(int(n_components), n_features))


def pca_filter(data, n_components, threshold=None, alpha=None, variance_ratio=None):
    n_comp = _resolve_pca_components(n_components, variance_ratio, data.shape[1])
    pca = PCA(n_components=n_comp, random_state=_RANDOM_SEED)
    data_pca = pca.fit_transform(data)
    cov = MinCovDet(random_state=_RANDOM_SEED).fit(data_pca)
    md = cov.mahalanobis(data_pca)
    cutoff = _mahalanobis_cutoff(threshold, alpha, df=data_pca.shape[1])
    mask = md <= cutoff
    return mask, md


def pca_reconstruction_filter(data, n_components, contamination, variance_ratio=None):
    n_comp = _resolve_pca_components(n_components, variance_ratio, data.shape[1])
    pca = PCA(n_components=n_comp, random_state=_RANDOM_SEED)
    X_pca = pca.fit_transform(data)
    X_rec = pca.inverse_transform(X_pca)
    rec_error = np.linalg.norm(data - X_rec, axis=1)

    thr = np.quantile(rec_error, 1 - contamination)
    mask = rec_error <= thr
    return mask, rec_error


def band_zscore_filter(data, threshold=3.0):
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    std_safe = np.where(std == 0, 1.0, std)

    z = np.abs((data - mean) / std_safe)
    scores = np.max(z, axis=1)
    mask = scores <= threshold
    return mask, scores


def percentile_filter(data, lower_pct=0.01, upper_pct=0.99):
    lower = np.quantile(data, lower_pct, axis=0)
    upper = np.quantile(data, upper_pct, axis=0)

    below = data < lower
    above = data > upper
    score = np.maximum(
        np.where(below, (lower - data) / (np.abs(lower) + 1e-12), 0.0),
        np.where(above, (data - upper) / (np.abs(upper) + 1e-12), 0.0),
    )
    scores = np.max(score, axis=1)
    mask = np.all(~(below | above), axis=1)
    return mask, scores


def iqr_filter(data, factor=1.5):
    q1 = np.quantile(data, 0.25, axis=0)
    q3 = np.quantile(data, 0.75, axis=0)
    iqr = q3 - q1
    iqr_safe = np.where(iqr == 0, 1.0, iqr)

    lower = q1 - factor * iqr_safe
    upper = q3 + factor * iqr_safe

    below = data < lower
    above = data > upper
    score = np.maximum(
        np.where(below, (lower - data) / (iqr_safe + 1e-12), 0.0),
        np.where(above, (data - upper) / (iqr_safe + 1e-12), 0.0),
    )
    scores = np.max(score, axis=1)
    mask = np.all(~(below | above), axis=1)
    return mask, scores


def _fit_sample(data, sample_size):
    n = data.shape[0]
    if n > sample_size:
        rng = np.random.default_rng(_RANDOM_SEED)
        idx = rng.choice(n, sample_size, replace=False)
        return data[idx]
    return data


def isolation_forest_filter(data, contamination, sample_size=SAMPLE_CAP):
    sample = _fit_sample(data, sample_size)

    clf = IsolationForest(
        contamination=contamination, random_state=_RANDOM_SEED, n_jobs=-1
    )
    clf.fit(sample)

    pred = clf.predict(data)
    scores = -clf.score_samples(data)

    return pred == 1, scores


def lof_filter(data, n_neighbors, contamination):
    if data.shape[0] < 5:
        return np.ones(data.shape[0], dtype=bool), np.zeros(data.shape[0])

    clf = LocalOutlierFactor(
        n_neighbors=n_neighbors, contamination=contamination, n_jobs=-1
    )

    pred = clf.fit_predict(data)
    scores = -clf.negative_outlier_factor_

    return pred == 1, scores


def one_class_svm_filter(data, nu=0.01, gamma="scale", kernel="rbf",
                         sample_size=SAMPLE_CAP):
    # OneClassSVM fit is superlinear (O(n^2)+) — fit on a bounded subsample
    # (like isolation_forest_filter) and predict on the full pixel set
    sample = _fit_sample(data, sample_size)
    clf = OneClassSVM(nu=nu, gamma=gamma, kernel=kernel)
    clf.fit(sample)
    pred = clf.predict(data)
    scores = -clf.decision_function(data).ravel()
    return pred == 1, scores


def knn_filter(data, n_neighbors=5, contamination=0.01):
    nbrs = NearestNeighbors(n_neighbors=n_neighbors, n_jobs=-1)
    nbrs.fit(data)
    # kneighbors() without an argument skips the query point itself; called
    # with an explicit `data` the query point would otherwise be its own
    # first neighbour at distance 0, shifting the score to the (k-1)-th
    # real neighbour.
    distances, _ = nbrs.kneighbors()

    score = distances[:, -1]

    thr = np.quantile(score, 1 - contamination)
    mask = score <= thr

    return mask, score


def elliptic_filter(data, contamination=0.01):
    clf = EllipticEnvelope(contamination=contamination, random_state=_RANDOM_SEED)
    pred = clf.fit_predict(data)
    scores = -clf.decision_function(data)
    return pred == 1, scores


def hotelling_t2_filter(data, alpha=0.05, log_error=_noop):
    n, p = data.shape
    if n <= p + 1:
        log_error("hotelling_t2_filter: n=%d <= p+1=%d — kept all pixels" % (n, p + 1))
        return np.ones(n, dtype=bool), np.zeros(n)
    try:
        cov = EmpiricalCovariance().fit(data)
        t2 = cov.mahalanobis(data)
        f_crit = f_dist.ppf(1.0 - alpha, p, n - p)
        t2_crit = p * (n - 1) / (n - p) * f_crit
        mask = t2 <= t2_crit
    except Exception as err:
        log_error("hotelling_t2_filter failed: %s — kept all pixels" % err)
        return np.ones(n, dtype=bool), np.zeros(n)
    return mask, t2


def gmm_filter(data, n_components=2, contamination=0.01, log_error=_noop):
    try:
        gmm = GaussianMixture(
            n_components=n_components,
            covariance_type="full",
            random_state=_RANDOM_SEED,
        )
        gmm.fit(data)
        log_lik = gmm.score_samples(data)
        thr = np.quantile(log_lik, contamination)
        mask = log_lik >= thr
        scores = -log_lik
    except Exception as err:
        log_error("gmm_filter failed: %s — kept all pixels" % err)
        return np.ones(data.shape[0], dtype=bool), np.zeros(data.shape[0])
    return mask, scores


def sam_filter(data, contamination=0.01, reference=None):
    if reference is None:
        reference = np.nanmean(data, axis=0)

    reference = np.asarray(reference, dtype=np.float32)

    numerator = np.sum(data * reference, axis=1)
    denominator = (np.linalg.norm(data, axis=1) * np.linalg.norm(reference)) + 1e-12

    cos_theta = np.clip(numerator / denominator, -1, 1)
    angles = np.arccos(cos_theta)

    thr = np.quantile(angles, 1 - contamination)
    mask = angles <= thr

    return mask, angles


# Detection method dispatch on a flattened N x B observation matrix; returns
# (mask_valid, scores). Shared by the per-ROI mode (remove_multivariate_outliers)
# and the group mode (run_pipeline_group), so statistics computed from a class
# pool go through exactly the same method implementations.
def _dispatch_flat(method, data_valid, kwargs, log_error=_noop):
    bands = data_valid.shape[1]
    scaler_name = kwargs.get("scaler", "standard")
    data_scaled, _ = scale_data(data_valid, scaler=scaler_name)

    if method == "mahalanobis":
        mask_valid, scores = mahalanobis_filter(
            data_scaled,
            threshold=kwargs.get("threshold"),
            alpha=kwargs.get("alpha"),
        )

    elif method == "robustmahalanobis":
        mask_valid, scores = mahalanobis_filter(
            data_scaled,
            threshold=kwargs.get("threshold"),
            alpha=kwargs.get("alpha"),
            robust=True,
        )

    elif method == "bandzscore":
        threshold = kwargs.get("threshold", 3.0)
        mask_valid, scores = band_zscore_filter(data_valid, threshold)

    elif method == "percentile":
        lower_pct = kwargs.get("lower_pct", 0.01)
        upper_pct = kwargs.get("upper_pct", 0.99)
        mask_valid, scores = percentile_filter(data_valid, lower_pct, upper_pct)

    elif method == "iqr":
        factor = kwargs.get("factor", 1.5)
        mask_valid, scores = iqr_filter(data_valid, factor)

    elif method in ("pca", "pcamahalanobis"):
        n_components = kwargs.get("n_components", min(bands, data_valid.shape[0], 5))
        mask_valid, scores = pca_filter(
            data_scaled,
            n_components,
            threshold=kwargs.get("threshold"),
            alpha=kwargs.get("alpha"),
            variance_ratio=kwargs.get("variance_ratio"),
        )

    elif method == "pcareconstruction":
        n_components = kwargs.get("n_components", min(bands, max(2, bands // 2)))
        contamination = kwargs.get("contamination", 0.01)
        mask_valid, scores = pca_reconstruction_filter(
            data_scaled, n_components, contamination,
            variance_ratio=kwargs.get("variance_ratio"),
        )

    elif method == "isolationforest":
        contamination = kwargs.get("contamination", 0.01)
        sample_size = kwargs.get("sample_size", SAMPLE_CAP)
        mask_valid, scores = isolation_forest_filter(
            data_scaled, contamination, sample_size
        )

    elif method == "lof":
        n_neighbors = min(kwargs.get("n_neighbors", 20), data_valid.shape[0] - 1)
        contamination = kwargs.get("contamination", 0.01)
        mask_valid, scores = lof_filter(data_scaled, n_neighbors, contamination)

    elif method == "oneclasssvm":
        nu = kwargs.get("nu", 0.01)
        gamma = kwargs.get("gamma", "scale")
        kernel = kwargs.get("kernel", "rbf")
        mask_valid, scores = one_class_svm_filter(data_scaled, nu, gamma, kernel)

    elif method == "knn":
        n_neighbors = min(kwargs.get("n_neighbors", 5), data_valid.shape[0] - 1)
        contamination = kwargs.get("contamination", 0.01)
        mask_valid, scores = knn_filter(data_scaled, n_neighbors, contamination)

    elif method in ("elliptic", "ellipticenvelope"):
        contamination = kwargs.get("contamination", 0.01)
        mask_valid, scores = elliptic_filter(data_scaled, contamination)

    elif method == "hotellingt2":
        alpha = kwargs.get("alpha", 0.05)
        mask_valid, scores = hotelling_t2_filter(data_scaled, alpha,
                                                 log_error=log_error)

    elif method == "gmm":
        n_components = kwargs.get("n_components", 2)
        contamination = kwargs.get("contamination", 0.01)
        mask_valid, scores = gmm_filter(data_scaled, n_components, contamination,
                                        log_error=log_error)

    elif method == "sam":
        contamination = kwargs.get("contamination", 0.01)
        reference = kwargs.get("reference", None)
        mask_valid, scores = sam_filter(data_valid, contamination, reference)

    else:
        raise ValueError(f"Unknown method: {method}")

    return mask_valid, scores


def remove_multivariate_outliers(stack, method="isolationforest", log_error=_noop,
                                 **kwargs):
    bands, ysize, xsize = stack.shape
    method = normalize_method_name(method)

    data_valid, valid_mask = prepare_valid_pixels(stack)

    if data_valid.shape[0] < max(10, bands + 2):
        raise ValueError("Too few valid pixels in ROI")

    mask_valid, scores = _dispatch_flat(method, data_valid, kwargs,
                                        log_error=log_error)

    full_mask = rebuild_mask(mask_valid, valid_mask, ysize, xsize)
    cleaned_stack = np.where(full_mask[None, :, :], stack, np.nan)

    return cleaned_stack, full_mask, scores


# Single dispatch point shared by the sequential pipeline and the voting
# ensemble: every method takes a band stack and returns
# (filtered_stack, keep_mask, scores).
def apply_filter(stack, method_name, kwargs, log_error=_noop, log_info=_noop):
    method_key = normalize_method_name(method_name)

    if method_key == "mad":
        return mad_filter_stack(stack, **kwargs)
    if method_key == "erosion":
        return erosion_filter(stack, log_error=log_error, log_info=log_info,
                              **kwargs)
    return remove_multivariate_outliers(stack, method=method_key,
                                        log_error=log_error, **kwargs)


# Reads a GDAL dataset into a float32 stack with NoData replaced by NaN.
def stack_from_dataset(ds, nodata_value=None):
    band1 = ds.GetRasterBand(1)
    if nodata_value is None:
        nodata_value = band1.GetNoDataValue()

    stack = ds.ReadAsArray().astype(np.float32)

    if stack.ndim == 2:
        stack = stack[np.newaxis, ...]

    if nodata_value is not None:
        try:
            nodata_value = float(nodata_value)
            stack[np.isclose(stack, nodata_value, equal_nan=False)] = np.nan
        except (TypeError, ValueError):
            stack[stack == nodata_value] = np.nan

    return stack


def run_pipeline(
    source, pipeline_steps, nodata_value=None, use_majority_voting=False,
    vote_threshold=2, log_error=_noop, log_info=_noop,
):
    # source: a gdal.Dataset or a ready stack (bands, y, x) carrying NaN
    # where the raster has NoData
    if hasattr(source, "ReadAsArray"):
        stack = stack_from_dataset(source, nodata_value=nodata_value)
    else:
        stack = source
        if stack.ndim == 2:
            stack = stack[np.newaxis, ...]

    total_raster_pixels = int(stack.shape[1] * stack.shape[2])
    original_valid_mask = np.all(~np.isnan(stack), axis=0)
    valid_pixels = int(np.sum(original_valid_mask))
    mask_final = original_valid_mask.copy()
    steps = []

    if use_majority_voting:
        stack, mask_final, votes = ensemble_outlier_mask(
            stack, pipeline_steps, vote_threshold=vote_threshold,
            log_error=log_error, log_info=log_info,
        )

        removed = int(np.sum(original_valid_mask & ~mask_final))
        removed_pct = 100.0 * removed / valid_pixels if valid_pixels > 0 else 0.0

        steps.append(
            {
                "step": 1,
                "method": "MajorityVoting",
                "removed_pixels": removed,
                "removed_percent": float(removed_pct),
                "vote_threshold": int(vote_threshold),
            }
        )

        log_info("MajorityVoting | removed: %d px (%.2f%%)" % (removed, removed_pct))

        return (
            stack,
            mask_final,
            {
                "total_raster_pixels": total_raster_pixels,
                "valid_pixels": valid_pixels,
                "steps": steps,
            },
        )

    for step_id, (method_name, kwargs) in enumerate(pipeline_steps, start=1):
        _, mask, _ = apply_filter(stack, method_name, kwargs,
                                  log_error=log_error, log_info=log_info)

        mask_final &= mask
        # removed pixels are set to NaN after each step, so the statistics of
        # subsequent steps are computed only from the surviving pixels
        stack = np.where(mask_final[None, :, :], stack, np.nan)

        removed = int(np.sum(original_valid_mask & ~mask_final))
        removed_pct = 100.0 * removed / valid_pixels if valid_pixels > 0 else 0.0

        steps.append(
            {
                "step": step_id,
                "method": method_name,
                "removed_pixels": removed,
                "removed_percent": float(removed_pct),
            }
        )

        log_info("%s | removed: %d px (%.2f%%)" % (method_name, removed, removed_pct))

    return (
        stack,
        mask_final,
        {
            "total_raster_pixels": total_raster_pixels,
            "valid_pixels": valid_pixels,
            "steps": steps,
        },
    )


def ensemble_outlier_mask(stack, methods_config, vote_threshold=2,
                          log_error=_noop, log_info=_noop):
    masks = []

    for method_name, kwargs in methods_config:
        _, mask, _ = apply_filter(stack, method_name, kwargs,
                                  log_error=log_error, log_info=log_info)
        masks.append(mask.astype(np.uint8))

    masks = np.stack(masks, axis=0)
    votes = np.sum(masks, axis=0)

    final_mask = votes >= vote_threshold
    cleaned_stack = np.where(final_mask[None, :, :], stack, np.nan)

    return cleaned_stack, final_mask, votes


# Group mode (scope: class / macroclass)


def _group_flatten(work_stacks):
    datas = []
    metas = []
    for w in work_stacks:
        d, vflat = prepare_valid_pixels(w)
        datas.append(d)
        metas.append((vflat, w.shape[1], w.shape[2]))
    if datas:
        pooled = np.concatenate(datas, axis=0)
    else:
        pooled = np.empty((0, 0), dtype=np.float32)
    return pooled, datas, metas


# Keep masks of a single step in group mode: spectral methods compute their
# statistics from the pixel pool of all ROIs in the group, while erosion, being
# a spatial method, is applied to each ROI separately.
def _group_step_masks(work_stacks, method_name, kwargs, log_error=_noop,
                      log_info=_noop):
    key = normalize_method_name(method_name)

    if key == "erosion":
        out = []
        for w in work_stacks:
            _, m, _ = erosion_filter(w, log_error=log_error,
                                     log_info=log_info, **kwargs)
            out.append(m)
        return out

    pooled, datas, metas = _group_flatten(work_stacks)
    bands = work_stacks[0].shape[0]

    if key == "mad":
        mask_valid, _ = mad_filter_flat(pooled, **kwargs)
    else:
        if pooled.shape[0] < max(10, bands + 2):
            raise ValueError("Too few valid pixels in group")
        mask_valid, _ = _dispatch_flat(key, pooled, kwargs,
                                       log_error=log_error)

    out = []
    offset = 0
    for d, (vflat, ys, xs) in zip(datas, metas):
        n = d.shape[0]
        out.append(rebuild_mask(mask_valid[offset:offset + n], vflat, ys, xs))
        offset += n
    return out


# Pipeline in group mode: statistics of spectral methods are computed from the
# pixel pool of all ROIs in the group (class or macroclass), while masks are
# returned separately for each ROI. Step semantics are identical to
# run_pipeline:
# sequential steps see only the pixels kept by preceding steps, while majority
# voting operates on the full data.
def run_pipeline_group(stacks, pipeline_steps, use_majority_voting=False,
                       vote_threshold=2, log_error=_noop, log_info=_noop):
    stacks = [s[np.newaxis, ...] if s.ndim == 2 else s for s in stacks]
    original_valids = [np.all(~np.isnan(s), axis=0) for s in stacks]
    total_raster_pixels = int(sum(s.shape[1] * s.shape[2] for s in stacks))
    valid_pixels = int(sum(int(v.sum()) for v in original_valids))
    steps = []

    def _removed(masks_list):
        return int(sum(
            int((original_valids[i] & ~masks_list[i]).sum())
            for i in range(len(stacks))
        ))

    if use_majority_voting:
        votes = [np.zeros(v.shape, dtype=np.int32) for v in original_valids]
        for method_name, kwargs in pipeline_steps:
            step_masks = _group_step_masks(
                stacks, method_name, kwargs, log_error, log_info
            )
            for i, m in enumerate(step_masks):
                votes[i] += (m & original_valids[i]).astype(np.int32)
        masks = [
            original_valids[i] & (votes[i] >= vote_threshold)
            for i in range(len(stacks))
        ]
        removed = _removed(masks)
        removed_pct = 100.0 * removed / valid_pixels if valid_pixels > 0 else 0.0
        steps.append(
            {
                "step": 1,
                "method": "MajorityVoting",
                "removed_pixels": removed,
                "removed_percent": float(removed_pct),
                "vote_threshold": int(vote_threshold),
            }
        )
        log_info(
            "MajorityVoting (group) | removed: %d px (%.2f%%)"
            % (removed, removed_pct)
        )
        return masks, {
            "total_raster_pixels": total_raster_pixels,
            "valid_pixels": valid_pixels,
            "steps": steps,
        }

    masks = [v.copy() for v in original_valids]
    work_stacks = list(stacks)
    for step_id, (method_name, kwargs) in enumerate(pipeline_steps, start=1):
        step_masks = _group_step_masks(
            work_stacks, method_name, kwargs, log_error, log_info
        )
        for i, m in enumerate(step_masks):
            masks[i] &= m
        work_stacks = [
            np.where(masks[i][None, :, :], stacks[i], np.nan)
            for i in range(len(stacks))
        ]
        removed = _removed(masks)
        removed_pct = 100.0 * removed / valid_pixels if valid_pixels > 0 else 0.0
        steps.append(
            {
                "step": step_id,
                "method": method_name,
                "removed_pixels": removed,
                "removed_percent": float(removed_pct),
            }
        )
        log_info(
            "%s (group) | removed: %d px (%.2f%%)"
            % (method_name, removed, removed_pct)
        )

    return masks, {
        "total_raster_pixels": total_raster_pixels,
        "valid_pixels": valid_pixels,
        "steps": steps,
    }


# GDAL/OGR helpers (pure, no cfg, no QGIS)


# Repairs invalid (self-touching) geometries in a cutline GeoPackage in place.
# MakeValid only splits the corner touches, so the clipped pixels are unchanged.
def ensure_valid_cutline(roi_gpkg):
    try:
        ds = ogr.Open(roi_gpkg, 1)
    except Exception:
        return
    if ds is None:
        return
    try:
        layer = ds.GetLayer()
        for feat in layer:
            geom = feat.GetGeometryRef()
            if geom is None or geom.IsValid():
                continue
            fixed = None
            try:
                fixed = geom.MakeValid()
            except Exception:
                fixed = None
            if fixed is None or fixed.IsEmpty():
                fixed = geom.Buffer(0)
            if fixed is not None and not fixed.IsEmpty() and fixed.IsValid():
                feat.SetGeometry(fixed)
                layer.SetFeature(feat)
        ds.FlushCache()
    finally:
        ds = None


# Clips a raster to the ROI cutline and returns the result as an in-memory GDAL dataset.
# nodata_value=None (default) warps to Float32 with NaN outside the cutline, so
# legitimate 0-valued pixels are not confused with the area outside the ROI.
def warp_to_memory(raster_in, roi_gpkg, nodata_value=None):
    ensure_valid_cutline(roi_gpkg)
    if nodata_value is None:
        warp_options = gdal.WarpOptions(
            format="MEM", cutlineDSName=roi_gpkg, cropToCutline=True,
            dstNodata=float("nan"), outputType=gdal.GDT_Float32
        )
    else:
        warp_options = gdal.WarpOptions(
            format="MEM", cutlineDSName=roi_gpkg, cropToCutline=True,
            dstNodata=nodata_value
        )

    return gdal.Warp("", raster_in, options=warp_options)


# Builds a reusable multi-band source from band paths: a single path is returned
# as-is, multiple paths are stacked into an in-memory (/vsimem) VRT. Release the
# returned path with release_multiband_source() when done.
def build_multiband_source(band_paths):
    band_paths = list(band_paths)
    unique_paths = list(dict.fromkeys(band_paths))
    if len(unique_paths) == 1:
        # band set backed by a SINGLE multiband file: the path repeats for
        # every band, and BuildVRT(separate=True) would then take N copies of
        # band 1 ("Only the first one will be taken into account"), so the file
        # is used directly, with all bands in their original order
        return unique_paths[0]
    _VSIMEM_COUNTER[0] += 1
    vrt_path = "/vsimem/outlier_filters_%d.vrt" % _VSIMEM_COUNTER[0]
    gdal.BuildVRT(vrt_path, band_paths, separate=True)
    return vrt_path


def release_multiband_source(source_path):
    if isinstance(source_path, str) and source_path.startswith("/vsimem/"):
        try:
            gdal.Unlink(source_path)
        except Exception:
            pass


# Builds a multi-band VRT from band_paths and clips it to the ROI; returns an in-memory GDAL dataset.
def warp_multiband_to_memory(band_paths, roi_gpkg, nodata_value=None):
    source = build_multiband_source(band_paths)
    try:
        return warp_to_memory(source, roi_gpkg, nodata_value)
    finally:
        release_multiband_source(source)


# Creates a single-band in-memory GDAL dataset from a 2D uint8 array with the given geotransform and projection.
def create_mask_dataset(mask_array, geotransform, projection):

    ysize, xsize = mask_array.shape

    mem_driver = gdal.GetDriverByName("MEM")

    ds = mem_driver.Create("", xsize, ysize, 1, gdal.GDT_Byte)

    ds.SetGeoTransform(geotransform)
    ds.SetProjection(projection)

    band = ds.GetRasterBand(1)
    band.WriteArray(mask_array)

    return ds, band


# Converts non-zero pixels in mask_band to vector polygons and writes them to a GeoPackage.
def polygonize_mask(mask_band, projection, output_gpkg):

    driver = ogr.GetDriverByName("GPKG")
    out_vector = driver.CreateDataSource(output_gpkg)

    srs = osr.SpatialReference()
    srs.ImportFromWkt(projection)

    layer = out_vector.CreateLayer("filtered_roi", srs=srs)

    layer.CreateField(ogr.FieldDefn("value", ogr.OFTInteger))

    gdal.Polygonize(mask_band, mask_band, layer, 0)

    out_vector = None


# Returns a valid version of a polygon geometry. Polygonizing an outlier mask and
# unioning the pixel polygons can produce self-touching ("bowtie") geometry that
# GDAL rejects as a cutline ("Cutline polygon is invalid"). MakeValid only splits
# the corner touches, so the selected pixels (the training sample) are unchanged.
def make_valid_geometry(geom, context="", log_error=_noop, log_info=_noop):
    if geom is None or geom.IsValid():
        return geom
    fixed = None
    try:
        fixed = geom.MakeValid()
    except Exception as err:
        log_error("MakeValid failed%s: %s" % (context, err))
    if fixed is None or fixed.IsEmpty():
        fixed = geom.Buffer(0)
    if fixed is not None and not fixed.IsEmpty() and fixed.IsValid():
        log_info("Repaired invalid ROI geometry%s" % context)
        return fixed
    log_error("Could not repair ROI geometry%s — using original" % context)
    return geom


# Polygonizes a keep-mask and returns a single valid (multi)polygon geometry
# covering the kept pixels, or None if the mask is empty. Polygons are collected
# into a MultiPolygon and dissolved with a single cascaded union (O(n log n))
# instead of pairwise Union() in a loop (O(n^2)).
def mask_to_union_geometry(mask, geotransform, projection, context="",
                           log_error=_noop, log_info=_noop):
    mask_ds, mask_band = create_mask_dataset(
        mask.astype(np.uint8), geotransform, projection
    )

    srs = osr.SpatialReference()
    srs.ImportFromWkt(projection)

    mem_vector = ogr.GetDriverByName("Memory").CreateDataSource("")
    layer = mem_vector.CreateLayer("mask", srs=srs, geom_type=ogr.wkbPolygon)
    layer.CreateField(ogr.FieldDefn("value", ogr.OFTInteger))
    gdal.Polygonize(mask_band, mask_band, layer, 0)
    mask_ds = None

    multi = ogr.Geometry(ogr.wkbMultiPolygon)
    count = 0
    for feat in layer:
        g = feat.GetGeometryRef()
        if g is not None:
            multi.AddGeometry(g.Clone())
            count += 1
    mem_vector = None

    if count == 0:
        return None

    try:
        union_geom = multi.UnionCascaded()
    except Exception as err:
        log_error("UnionCascaded failed%s: %s — using Buffer(0)" % (context, err))
        union_geom = multi.Buffer(0)

    if union_geom is None or union_geom.IsEmpty():
        return None

    union_geom = make_valid_geometry(union_geom, context=context,
                                     log_error=log_error, log_info=log_info)
    if union_geom is None:
        return None
    # ROI geometry layers are of type MULTIPOLYGON; forcing the type prevents
    # a GeoPackage specification mismatch when a single POLYGON is written
    return ogr.ForceToMultiPolygon(union_geom)
