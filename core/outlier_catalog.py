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
# Outlier catalog.
# This tool applies the outlier detection result to the signature catalog.
# The module is free of QGIS and Qt dependencies, like core/outlier_filters.py,
# so it can also be used outside the plugin. Interface dependencies are passed
# as callbacks that default to no-ops.
import os
import tempfile

import numpy as np
from osgeo import gdal, ogr
from remotior_sensus.core import table_manager as _rs_tm

from . import outlier_filters as filters


def _noop(*_args, **_kwargs):
    pass


# Detection reference scope: "roi" computes statistics from the pixels of a
# single area; "class"/"macroclass" computes them from the pooled pixels of all
# areas sharing the same class_id/macroclass_id, including areas outside the
# cleaning selection. Only the areas matched by the predicate are modified.
SCOPE_ROI = "roi"
SCOPE_CLASS = "class"
SCOPE_MACROCLASS = "macroclass"


def _default_temp_path():
    # Substitutes the temporary file mechanism of the remotior_sensus library.
    fd, path = tempfile.mkstemp(suffix=".gpkg")
    os.close(fd)
    os.remove(path)
    return path


def warp_roi_stack(source_path, geom, srs, sig_id, ogr_driver,
                   temp_path_fn=None, log_error=_noop, log_info=_noop):
    # Returns None when the cut fails.
    temp_path_fn = temp_path_fn or _default_temp_path
    geom = filters.make_valid_geometry(
        geom, context=" (input ROI sig_id=%s)" % sig_id,
        log_error=log_error, log_info=log_info,
    )
    roi_tmp = temp_path_fn()
    roi_ds = ogr_driver.CreateDataSource(roi_tmp)
    roi_layer = roi_ds.CreateLayer(
        "roi", srs=srs, geom_type=ogr.wkbMultiPolygon
    )
    new_feat = ogr.Feature(roi_layer.GetLayerDefn())
    new_feat.SetGeometry(ogr.ForceToMultiPolygon(geom))
    roi_layer.CreateFeature(new_feat)
    roi_ds.FlushCache()
    roi_ds = None

    ds_raster = filters.warp_to_memory(source_path, roi_tmp)
    try:
        os.remove(roi_tmp)
    except OSError:
        pass
    if ds_raster is None:
        log_error("warp_to_memory returned None for sig_id=%s" % sig_id)
        return None
    stack = filters.stack_from_dataset(ds_raster)
    return stack, ds_raster.GetGeoTransform(), ds_raster.GetProjection()


def process_catalog_features(
    new_catalog, feature_predicate, pipeline_steps, use_majority_voting,
    vote_threshold, scope=SCOPE_ROI, temp_path_fn=None, stack_cache=None,
    log_error=_noop, log_info=_noop, progress=_noop,
):
    # stack_cache memorises cut stacks as {sig_id: (stack, geotransform,
    # projection)}. Cutting is deterministic, so the cache changes nothing in
    # the result; it only avoids repeating the costly raster cut. The plugin
    # cleans a set once and skips the cache; callers that clean the same set
    # repeatedly can pass one in.
    geometry_file = new_catalog.geometry_file
    bandset = new_catalog.bandset
    if bandset is None:
        raise ValueError("No bandset attached to signature catalog")

    band_paths = bandset.get_absolute_paths()

    # the geometry attribute is collected into a dictionary once, instead of
    # scanning the whole signature_id column for every layer feature
    tbl = new_catalog.table
    has_geometry = {}
    for i in range(len(tbl)):
        has_geometry[tbl["signature_id"][i]] = tbl["geometry"][i] == 1

    ds_read = ogr.Open(geometry_file)
    if ds_read is None:
        raise ValueError("Cannot open geometry file: %s" % geometry_file)

    layer = ds_read.GetLayer()
    srs = layer.GetSpatialRef()

    all_features = []
    candidate_ids = set()
    for feat in layer:
        sig_id = feat.GetField("roi_id")
        mc_id = feat.GetField("macroclass_id")
        cl_id = feat.GetField("class_id")

        if not has_geometry.get(sig_id, False):
            continue
        geom = feat.GetGeometryRef()
        if geom is None:
            continue

        if feature_predicate(sig_id, mc_id, cl_id):
            candidate_ids.add(sig_id)
        all_features.append((sig_id, mc_id, cl_id, geom.Clone()))

    ds_read = None

    # processing groups: in ROI scope every candidate is handled separately;
    # in class/macroclass scope all areas sharing an identifier form one
    # statistics pool, provided the group holds at least one candidate
    if scope == SCOPE_ROI:
        groups = [
            [f] for f in all_features if f[0] in candidate_ids
        ]
    elif scope in (SCOPE_CLASS, SCOPE_MACROCLASS):
        key_index = 2 if scope == SCOPE_CLASS else 1
        grouped = {}
        for f in all_features:
            grouped.setdefault(f[key_index], []).append(f)
        groups = [
            members for members in grouped.values()
            if any(m[0] in candidate_ids for m in members)
        ]
    else:
        raise ValueError("Unknown scope: %s" % scope)

    ogr_driver = ogr.GetDriverByName("GPKG")
    modified_sig_ids = []
    deleted_sig_ids = []
    geometry_updates = {}
    report = []
    total = sum(
        sum(1 for m in members if m[0] in candidate_ids) for members in groups
    )
    done = 0

    # the multiband source (a VRT in /vsimem) is built once for the whole
    # catalog
    source_path = filters.build_multiband_source(band_paths)
    try:
        for members in groups:
            stacks = []
            infos = []
            for sig_id, _mc_id, _cl_id, geom in members:
                warped = (
                    None if stack_cache is None else stack_cache.get(sig_id)
                )
                if warped is None:
                    warped = warp_roi_stack(
                        source_path, geom, srs, sig_id, ogr_driver,
                        temp_path_fn=temp_path_fn,
                        log_error=log_error, log_info=log_info,
                    )
                    if warped is not None and stack_cache is not None:
                        stack_cache[sig_id] = warped
                if warped is None:
                    continue
                stacks.append(warped[0])
                infos.append((sig_id, warped[1], warped[2]))
            if not stacks:
                continue

            try:
                if scope == SCOPE_ROI:
                    _, mask, pipeline_report = filters.run_pipeline(
                        stacks[0],
                        pipeline_steps,
                        use_majority_voting=use_majority_voting,
                        vote_threshold=vote_threshold,
                        log_error=log_error,
                        log_info=log_info,
                    )
                    masks = [mask]
                else:
                    masks, pipeline_report = filters.run_pipeline_group(
                        stacks,
                        pipeline_steps,
                        use_majority_voting=use_majority_voting,
                        vote_threshold=vote_threshold,
                        log_error=log_error,
                        log_info=log_info,
                    )
            except ValueError as err:
                log_error(
                    "run_pipeline skipped group of %s: %s"
                    % ([m[0] for m in members], err)
                )
                continue

            step_report = pipeline_report["steps"]
            for (sig_id, geotransform, projection), stack, mask in zip(
                    infos, stacks, masks
            ):
                if sig_id not in candidate_ids:
                    continue
                done += 1
                step = int(done * 80 / max(total, 1))
                progress(step, done, total, "removing")

                original_valid = np.all(~np.isnan(stack), axis=0)
                roi_valid = int(original_valid.sum())
                removed = int((original_valid & ~mask).sum())
                entry = {
                    "sig_id": sig_id,
                    "removed_pixels": removed,
                    "valid_pixels": roi_valid,
                    "total_raster_pixels": int(
                        stack.shape[1] * stack.shape[2]
                    ),
                    "removed_percent": (
                        100.0 * removed / roi_valid if roi_valid > 0 else 0.0
                    ),
                    "steps": step_report,
                    "scope": scope,
                }

                surviving = roi_valid - removed
                if surviving < filters.min_surviving_pixels(stack.shape[0]):
                    # the area is an outlier as a whole with respect to its
                    # group, or has been reduced below the minimum required by
                    # parametric methods (B+2), so the signature is removed
                    # from the catalog instead of remaining as a degenerate
                    # entry skipped by, for example, Maximum Likelihood
                    entry["removed_entirely"] = True
                    deleted_sig_ids.append(sig_id)
                    report.append(entry)
                    log_info(
                        "Outliers removed | sig=%s removed entirely "
                        "(%d px left < %d)"
                        % (sig_id, surviving,
                           filters.min_surviving_pixels(stack.shape[0]))
                    )
                    continue

                union_geom = filters.mask_to_union_geometry(
                    mask, geotransform, projection,
                    context=" for sig_id=%s" % sig_id,
                    log_error=log_error,
                    log_info=log_info,
                )
                if union_geom is None:
                    log_error(
                        "Polygonize produced no geometry for sig_id=%s"
                        % sig_id
                    )
                    continue

                geometry_updates[sig_id] = union_geom
                report.append(entry)
                modified_sig_ids.append(sig_id)

                log_info(
                    "Outliers removed | sig=%s | removed=%d px (%.2f%%)"
                    % (sig_id, removed, entry["removed_percent"])
                )
    finally:
        filters.release_multiband_source(source_path)

    if geometry_updates:
        geo_ds = ogr.Open(geometry_file, 1)
        if geo_ds is not None:
            geo_layer = geo_ds.GetLayer()
            geo_layer.ResetReading()
            for geo_feat in geo_layer:
                update = geometry_updates.get(geo_feat.GetField("roi_id"))
                if update is not None:
                    geo_feat.SetGeometry(update)
                    geo_layer.SetFeature(geo_feat)
            geo_ds.FlushCache()
            geo_ds = None

    return modified_sig_ids, deleted_sig_ids, report


# move the catalog geometry out of GDAL memory into a real file
def materialize_geometry_file(catalog, temp_path_fn=None, log_info=_noop):
    # SCP 9.0 copies the catalog geometry to a /vsimem path, which lives in
    # the memory of the calling process only. Classification extracts the
    # training pixels from that file in worker processes, which cannot open
    # such a path, so a cleaned catalog has to carry its geometry on disk.
    geometry_file = getattr(catalog, "geometry_file", None)
    if not geometry_file or "vsimem" not in geometry_file:
        return geometry_file
    temp_path_fn = temp_path_fn or _default_temp_path
    file_path = temp_path_fn()
    gdal.VectorTranslate(file_path, geometry_file, format="GPKG")
    catalog.geometry_file = file_path
    try:
        gdal.Unlink(geometry_file)
    except Exception as err:
        log_info("Unlink of %s failed: %s" % (geometry_file, err))
    log_info("Catalog geometry moved from memory to %s" % file_path)
    return file_path


def apply_removal_to_catalog(
    catalog, feature_predicate, pipeline_steps, use_majority_voting,
    vote_threshold, scope=SCOPE_ROI, temp_path_fn=None, stack_cache=None,
    warn_missing=True, log_error=_noop, log_info=_noop, progress=_noop,
):
    # Signatures must be recomputed before any area is dropped from the
    # catalog, so the order of the steps below matters. This is the entry
    # point of the whole cleaning sequence.
    modified_sig_ids, deleted_sig_ids, report = process_catalog_features(
        catalog, feature_predicate, pipeline_steps, use_majority_voting,
        vote_threshold, scope=scope, temp_path_fn=temp_path_fn,
        stack_cache=stack_cache,
        log_error=log_error, log_info=log_info, progress=progress,
    )

    recalculate_modified_signatures(
        catalog, modified_sig_ids, warn_missing=warn_missing,
        temp_path_fn=temp_path_fn, log_error=log_error, progress=progress,
    )

    # areas that are outliers as a whole with respect to their group are
    # dropped from the catalog
    for sig_id in deleted_sig_ids:
        try:
            catalog.remove_signature_by_id(sig_id)
        except Exception as err:
            log_error("Signature removal failed for %s: %s" % (sig_id, err))

    return modified_sig_ids, deleted_sig_ids, report


def _extract_roi_vector(geometry_file, sig_id, temp_path_fn=None):
    # Replaces get_polygon_from_vector, whose ST_Union query needs SpatiaLite,
    # available only inside QGIS, which would make this module depend on it.
    # One signature is recomputed at a time, so the SQL merge is unnecessary;
    # multipart areas are merged in memory with UnionCascaded.
    temp_path_fn = temp_path_fn or _default_temp_path
    source = ogr.Open(geometry_file)
    if source is None:
        return None
    layer = source.GetLayer()
    layer.SetAttributeFilter("roi_id = '%s'" % sig_id)
    srs = layer.GetSpatialRef()
    geometries = [
        feat.GetGeometryRef().Clone() for feat in layer
        if feat.GetGeometryRef() is not None
    ]
    source = None
    if not geometries:
        return None

    if len(geometries) == 1:
        merged_geometry = geometries[0]
    else:
        multi = ogr.Geometry(ogr.wkbMultiPolygon)
        for geom in geometries:
            multi.AddGeometry(geom)
        merged_geometry = multi.UnionCascaded()

    out_path = temp_path_fn()
    driver = ogr.GetDriverByName("GPKG")
    out_ds = driver.CreateDataSource(out_path)
    out_layer = out_ds.CreateLayer(
        "roi", srs=srs, geom_type=ogr.wkbMultiPolygon
    )
    feature = ogr.Feature(out_layer.GetLayerDefn())
    feature.SetGeometry(ogr.ForceToMultiPolygon(merged_geometry))
    out_layer.CreateFeature(feature)
    out_ds.FlushCache()
    out_ds = None
    return out_path


def recalculate_modified_signatures(new_catalog, modified_sig_ids,
                                    warn_missing=True, temp_path_fn=None,
                                    log_error=_noop, progress=_noop):
    # Delegates to calculate_signature of remotior_sensus, so pixel selection
    # and statistics stay identical to the plugin. Only the SQL geometry merge
    # is skipped, as described in _extract_roi_vector.
    total = len(modified_sig_ids)
    for idx, sig_id in enumerate(modified_sig_ids):
        step = 80 + int((idx + 1) * 20 / max(total, 1))
        progress(step, idx + 1, total, "recalculating")

        # the index is looked up in the CURRENT table, because dropping an
        # area that is an outlier as a whole changes the table length while
        # processing is still running
        table = new_catalog.table
        row = np.where(table["signature_id"] == sig_id)[0]
        if len(row) == 0:
            if warn_missing:
                log_error(
                    "sig_id %s not found in table, skipping recalculation"
                    % sig_id
                )
            continue

        roi_vector = _extract_roi_vector(
            new_catalog.geometry_file, sig_id, temp_path_fn=temp_path_fn
        )
        if roi_vector is None:
            log_error("no geometry found for sig_id=%s" % sig_id)
            continue

        try:
            result = new_catalog.calculate_signature(roi_vector)
            if not result:
                log_error("calculate_signature failed for %s" % sig_id)
                continue
            values, deviations, wavelengths, pixel_count = result
            new_catalog.signatures[sig_id] = (
                _rs_tm.create_spectral_signature_table(
                    value_list=values,
                    wavelength_list=wavelengths,
                    standard_deviation_list=deviations,
                )
            )
            new_catalog.table["pixel_count"][row[0]] = int(pixel_count)
        except Exception as err:
            log_error(
                "Signature recalculation failed for %s: %s" % (sig_id, err)
            )
        finally:
            try:
                os.remove(roi_vector)
            except OSError:
                pass
