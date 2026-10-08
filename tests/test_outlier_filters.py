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
# Outlier filter tests.
# Unit tests for the computational core in core/outlier_filters.py.
# The core module is independent of QGIS, so it is tested without launching
# QGIS. The tests use synthetic data in which the position of the outliers is
# known by construction, so detection is verified to be correct and not merely
# free of crashes.
# Run with: python3 -m unittest discover -s tests -v
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import outlier_filters as filters

# Threshold-based methods determine the number of removed pixels themselves,
# whereas fraction-based methods need the expected share to be supplied. The
# parameters were chosen so that, at the assumed outlier share (8 out of 208
# pixels, about 4%), every method has a chance of detecting them.
METHODS = {
    "MAD": {"threshold": 3.5},
    "Band Z-score": {"threshold": 3.0},
    "IQR": {"multiplier": 1.5},
    "Mahalanobis": {"alpha": 0.025},
    "Robust Mahalanobis": {"alpha": 0.025},
    "HotellingT2": {"alpha": 0.05},
    "PCA": {"variance_ratio": 0.95, "alpha": 0.025},
    "Percentile": {"lower_pct": 0.05, "upper_pct": 0.95},
    "PCA Reconstruction": {"variance_ratio": 0.95, "n_components": 2,
                           "contamination": 0.05},
    "GMM": {"n_components": 2, "contamination": 0.05},
    "EllipticEnvelope": {"contamination": 0.05},
    "IsolationForest": {"contamination": 0.05},
    "LOF": {"n_neighbors": 10, "contamination": 0.05},
    "kNN": {"n_neighbors": 5, "contamination": 0.05},
    "OneClassSVM": {"nu": 0.05},
    "SAM": {"contamination": 0.05},
}
# Morphological erosion is a spatial method rather than a spectral one, so it
# is not subject to the outlier detection test in feature space.
SPATIAL_METHOD = "Erosion"

BAND_COUNT = 6
SIDE = 15                       # 15 x 15 pixel stack
OUTLIER_COUNT = 8


def synthetic_stack(seed=0):
    # Returns (stack, outlier_mask). Every outlying pixel gets its own random
    # shift direction in band space, which changes the shape of the signature
    # and not only its brightness. Shifting all bands equally would be invisible
    # to spectral angle mapping, and identical outliers would look like a
    # separate dense cluster to neighbourhood methods and to the Gaussian
    # mixture model.
    rng = np.random.default_rng(seed)
    stack = rng.normal(loc=100.0, scale=3.0,
                       size=(BAND_COUNT, SIDE, SIDE)).astype(np.float64)

    outlier_mask = np.zeros((SIDE, SIDE), dtype=bool)
    # outliers placed inside the area so that they are not confused with the
    # border effect of erosion
    positions = [(3, 3), (3, 9), (5, 6), (7, 11), (9, 4), (9, 9), (11, 7), (6, 2)]
    for y, x in positions[:OUTLIER_COUNT]:
        direction = rng.normal(size=BAND_COUNT)
        direction /= np.linalg.norm(direction)
        stack[:, y, x] = 100.0 + 35.0 * direction + rng.normal(scale=3.0,
                                                              size=BAND_COUNT)
        outlier_mask[y, x] = True
    return stack, outlier_mask


class TestDetection(unittest.TestCase):
    # Every spectral method detects the injected outliers.

    def setUp(self):
        self.stack, self.outliers = synthetic_stack()

    def test_methods_detect_outliers(self):
        for name, params in METHODS.items():
            with self.subTest(method=name):
                _, keep_mask, _ = filters.apply_filter(
                    self.stack, name, dict(params)
                )
                removed = ~keep_mask
                hits = int(np.sum(removed & self.outliers))
                self.assertGreater(
                    hits, 0,
                    "%s detected none of the %d injected "
                    "outliers" % (name, OUTLIER_COUNT)
                )

    def test_methods_do_not_remove_everything(self):
        for name, params in METHODS.items():
            with self.subTest(method=name):
                _, keep_mask, _ = filters.apply_filter(
                    self.stack, name, dict(params)
                )
                remaining = int(np.sum(keep_mask))
                self.assertGreater(
                    remaining, SIDE * SIDE // 2,
                    "%s removed more than half of the pixels" % name
                )

    def test_erosion_removes_border(self):
        # Erosion is a spatial method: it removes a layer of border pixels.
        _, keep_mask, _ = filters.apply_filter(
            self.stack, SPATIAL_METHOD, {"iterations": 1}
        )
        self.assertFalse(keep_mask[0, 0], "the corner pixel should disappear")
        self.assertTrue(keep_mask[SIDE // 2, SIDE // 2],
                        "the central pixel should remain")


class TestPipelineAndVoting(unittest.TestCase):

    def setUp(self):
        self.stack, self.outliers = synthetic_stack()

    def test_pipeline_narrows_mask(self):
        # A pipeline cannot keep more pixels than its first step.
        steps = [("MAD", {"threshold": 3.5}), ("IQR", {"multiplier": 1.5})]
        _, mad_mask, _ = filters.run_pipeline(self.stack, steps[:1])
        _, pipeline_mask, _ = filters.run_pipeline(self.stack, steps)
        self.assertLessEqual(int(np.sum(pipeline_mask)), int(np.sum(mad_mask)))

    # NOTE: vote_threshold counts votes IN FAVOUR OF KEEPING a pixel. A pixel
    # survives when at least vote_threshold methods consider it valid. It
    # follows that a threshold of 1 requires the methods to be unanimous in
    # order to remove a pixel, whereas a threshold equal to the number of
    # methods allows any single method to have a pixel removed.

    def test_threshold_one_requires_unanimous_rejection(self):
        # Threshold 1: only pixels rejected by every method are removed.
        steps = [("MAD", {"threshold": 3.5}), ("Mahalanobis", {"alpha": 0.025})]
        rejected = [~filters.apply_filter(self.stack, m, dict(p))[1]
                     for m, p in steps]
        intersection = rejected[0] & rejected[1]
        _, mask, _ = filters.run_pipeline(
            self.stack, steps, use_majority_voting=True, vote_threshold=1
        )
        np.testing.assert_array_equal(~mask, intersection)

    def test_threshold_equal_to_method_count_is_union(self):
        # Threshold equal to the method count: one method suffices.
        steps = [("MAD", {"threshold": 3.5}), ("Mahalanobis", {"alpha": 0.025})]
        rejected = [~filters.apply_filter(self.stack, m, dict(p))[1]
                     for m, p in steps]
        union = rejected[0] | rejected[1]
        _, mask, _ = filters.run_pipeline(
            self.stack, steps, use_majority_voting=True, vote_threshold=2
        )
        np.testing.assert_array_equal(~mask, union)

    def test_higher_threshold_removes_no_fewer(self):
        steps = [("MAD", {"threshold": 3.5}),
                 ("Mahalanobis", {"alpha": 0.025}),
                 ("IQR", {"multiplier": 1.5})]
        previous = None
        for threshold in (1, 2, 3):
            _, mask, _ = filters.run_pipeline(
                self.stack, steps, use_majority_voting=True, vote_threshold=threshold
            )
            removed = int(np.sum(~mask))
            if previous is not None:
                self.assertGreaterEqual(removed, previous)
            previous = removed

    def test_majority_threshold_for_three_methods(self):
        # For three methods a majority equals a threshold of 2 keep votes.
        steps = [("MAD", {"threshold": 3.5}),
                 ("Mahalanobis", {"alpha": 0.025}),
                 ("IQR", {"multiplier": 1.5})]
        rejected = [~filters.apply_filter(self.stack, m, dict(p))[1]
                     for m, p in steps]
        removal_votes = sum(o.astype(int) for o in rejected)
        majority = removal_votes >= 2
        _, mask, _ = filters.run_pipeline(
            self.stack, steps, use_majority_voting=True, vote_threshold=2
        )
        np.testing.assert_array_equal(~mask, majority)


class TestReproducibility(unittest.TestCase):
    # Stochastic methods must give the same result on repeated runs.

    STOCHASTIC = ["Robust Mahalanobis", "PCA", "IsolationForest", "GMM",
              "EllipticEnvelope", "PCA Reconstruction"]

    def test_fixed_seed_gives_identical_result(self):
        stack, _ = synthetic_stack()
        for name in self.STOCHASTIC:
            with self.subTest(method=name):
                params = METHODS[name]
                _, first, _ = filters.apply_filter(
                    stack, name, dict(params))
                _, second, _ = filters.apply_filter(
                    stack, name, dict(params))
                np.testing.assert_array_equal(
                    first, second,
                    "%s returned different masks in two calls" % name
                )


class TestEdgeCases(unittest.TestCase):
    # Behaviour towards NoData values and the minimum sample size.

    def test_nodata_not_counted_as_removed(self):
        stack, _ = synthetic_stack()
        stack[:, 0, :] = np.nan          # the entire first row is NoData
        _, mask, report = filters.run_pipeline(
            stack, [("MAD", {"threshold": 3.5})]
        )
        self.assertEqual(report["valid_pixels"], SIDE * SIDE - SIDE)
        self.assertEqual(report["total_raster_pixels"], SIDE * SIDE)
        # NoData pixels must not end up in the mask of kept pixels
        self.assertEqual(int(np.sum(mask[0, :])), 0)

    def test_minimum_surviving_pixels_threshold(self):
        # Covariance matrix invertibility requires B+2 observations.
        for bands in (1, 6, 13):
            self.assertEqual(filters.min_surviving_pixels(bands), bands + 2)

    def test_scaling_standardises_data(self):
        data = np.array([[1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0]]).T
        scaled, scaler = filters.scale_data(data)
        np.testing.assert_allclose(scaled.mean(axis=0), [0.0, 0.0],
                                   atol=1e-9)
        np.testing.assert_allclose(scaled.std(axis=0), [1.0, 1.0],
                                   atol=1e-9)
        self.assertIsNotNone(scaler)

    def test_disabled_scaling_returns_data_unchanged(self):
        data = np.array([[1.0, 2.0], [3.0, 4.0]])
        unchanged, scaler = filters.scale_data(data, scaler=None)
        np.testing.assert_array_equal(unchanged, data)
        self.assertIsNone(scaler)

    def test_unknown_scaler_raises_error(self):
        with self.assertRaises(ValueError):
            filters.scale_data(np.array([[1.0, 2.0]]), scaler="robust")

    def test_unknown_method_raises_error(self):
        stack, _ = synthetic_stack()
        with self.assertRaises(Exception):
            filters.apply_filter(stack, "no such method", {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
