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


from osgeo import ogr, osr
from PyQt6.QtWidgets import QApplication

cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[""])
# pure filter mathematics plus GDAL helpers; a QGIS-free module
filters = __import__(
    str(__name__).split(".")[0] + ".core.outlier_filters", fromlist=[""]
)
# signature catalog operations, likewise QGIS-free; the whole processing
# path lives there, this module only wires it to the interface
catalog_ops = __import__(
    str(__name__).split(".")[0] + ".core.outlier_catalog", fromlist=[""]
)


def run_pipeline(
    ds, pipeline_steps, nodata_value=None, use_majority_voting=False,
    vote_threshold=2,
):
    return filters.run_pipeline(
        ds, pipeline_steps, nodata_value=nodata_value,
        use_majority_voting=use_majority_voting, vote_threshold=vote_threshold,
        log_error=cfg.logger.log.error, log_info=cfg.logger.log.info,
    )


# The detection reference scope is defined by the core module; the names are
# repeated here because the remaining plugin interface modules rely on them.
SCOPE_ROI = catalog_ops.SCOPE_ROI
SCOPE_CLASS = catalog_ops.SCOPE_CLASS
SCOPE_MACROCLASS = catalog_ops.SCOPE_MACROCLASS


def _temp_gpkg_path():
    # Temporary file from the remotior_sensus library mechanism.
    return cfg.rs.configurations.temp.temporary_file_path(name_suffix=".gpkg")


def _progress(percent, done, total, phase):
    # The messages are kept as literals so that the QGIS translation mechanism
    # can detect them.
    if phase == "removing":
        text = QApplication.translate(
            "semiautomaticclassificationplugin",
            "Removing outliers: ROI %d/%d",
        )
    else:
        text = QApplication.translate(
            "semiautomaticclassificationplugin",
            "Recalculating signature %d/%d",
        )
    cfg.ui_utils.update_bar(percent, text % (done, total), percentage=percent)


def _reload_training_catalog(new_catalog):
    cfg.scp_training.set_signature_catalog(new_catalog)
    cfg.scp_training.roi_signature_table_tree()
    if cfg.simplified:
        dock_ui = cfg.dock_class_simpl_dlg.ui
    else:
        dock_ui = cfg.dock_class_dlg.ui
    dock_ui.undo_save_Button.setEnabled(True)
    dock_ui.redo_save_Button.setEnabled(False)
    if cfg.project_registry[cfg.reg_save_training_input_check] == 2:
        cfg.scp_training.save_signature_catalog()


# Shared skeleton of catalog operations: copy the catalog, process the ROIs
# matched by the predicate, recompute the signatures and optionally attach the
# new catalog with undo support.
def _remove_outliers_impl(
    feature_predicate, pipeline_steps, use_majority_voting, vote_threshold,
    scope=SCOPE_ROI, save_undo=True, reload_catalog=True, warn_missing=True,
):
    if cfg.scp_training is None or cfg.scp_training.signature_catalog is None:
        raise ValueError("No signature catalog loaded")

    cfg.ui_utils.add_progress_bar()
    try:
        if save_undo:
            cfg.scp_training.save_temporary_signature_catalog()
        new_catalog = cfg.scp_training.signature_catalog_copy()
        # SCP 9.0 keeps the copied geometry in GDAL memory; classification
        # reads the ROIs in worker processes, which cannot see /vsimem paths
        catalog_ops.materialize_geometry_file(
            new_catalog, temp_path_fn=_temp_gpkg_path,
            log_info=cfg.logger.log.info,
        )

        # full cleaning sequence executed by the core module
        _, _, report = catalog_ops.apply_removal_to_catalog(
            new_catalog,
            feature_predicate,
            pipeline_steps,
            use_majority_voting,
            vote_threshold,
            scope=scope,
            temp_path_fn=_temp_gpkg_path,
            warn_missing=warn_missing,
            log_error=cfg.logger.log.error,
            log_info=cfg.logger.log.info,
            progress=_progress,
        )

        if reload_catalog:
            _reload_training_catalog(new_catalog)
        return new_catalog, report
    finally:
        cfg.ui_utils.remove_progress_bar(sound=False)


def build_cleaned_catalog_copy(
    pipeline_steps, use_majority_voting=False, vote_threshold=2,
    scope=SCOPE_ROI,
):
    return _remove_outliers_impl(
        lambda *_: True,
        pipeline_steps,
        use_majority_voting,
        vote_threshold,
        scope=scope,
        save_undo=False,
        reload_catalog=False,
        warn_missing=False,
    )


def remove_outliers_all_signatures(
    pipeline_steps,
    use_majority_voting=False,
    vote_threshold=2,
    scope=SCOPE_ROI,
):
    _, report = _remove_outliers_impl(
        lambda *_: True, pipeline_steps, use_majority_voting, vote_threshold,
        scope=scope,
    )
    return report


def remove_outliers_selected_signatures(
    signature_ids,
    pipeline_steps,
    use_majority_voting=False,
    vote_threshold=2,
    scope=SCOPE_ROI,
):
    sig_id_set = {str(s) for s in signature_ids}
    _, report = _remove_outliers_impl(
        lambda sig_id, *_: str(sig_id) in sig_id_set,
        pipeline_steps,
        use_majority_voting,
        vote_threshold,
        scope=scope,
    )
    return report


def remove_outliers_macroclasses(
    macroclass_ids,
    pipeline_steps,
    use_majority_voting=False,
    vote_threshold=2,
):
    mc_set = {int(m) for m in macroclass_ids}
    _, report = _remove_outliers_impl(
        lambda _sig, mc_id, _cl: int(mc_id) in mc_set,
        pipeline_steps,
        use_majority_voting,
        vote_threshold,
        scope=SCOPE_MACROCLASS,
    )
    return report


def remove_outliers_drawing_roi(
    pipeline_steps, use_majority_voting=False, vote_threshold=2
):
    if cfg.temporary_roi is None:
        cfg.mx.msg_war_4()
        return None
    # the band set active in the project, the same one the ROI was drawn on
    # (as in save_roi_to_training), not the Multiple ROI tab spin box
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    bandset = cfg.bandset_catalog.get(bandset_number)
    if bandset is None:
        cfg.mx.msg_war_6(bandset_number)
        return None
    cfg.ui_utils.add_progress_bar()
    try:
        band_paths = bandset.get_absolute_paths()

        roi_tmp = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix=".gpkg"
        )
        cfg.util_qgis.save_memory_layer_to_geopackage(cfg.temporary_roi, roi_tmp)

        cfg.ui_utils.update_bar(
            20,
            QApplication.translate(
                "semiautomaticclassificationplugin", "Clipping raster to ROI..."
            ),
            percentage=20,
        )
        ds = filters.warp_multiband_to_memory(band_paths, roi_tmp)
        if ds is None:
            cfg.logger.log.error(
                "warp_multiband_to_memory returned None for drawn ROI"
            )
            cfg.mx.msg_err_outliers_pipeline_failed("cannot clip raster to ROI")
            return None

        cfg.ui_utils.update_bar(
            50,
            QApplication.translate(
                "semiautomaticclassificationplugin", "Running outlier pipeline..."
            ),
            percentage=50,
        )
        stack, mask, report = run_pipeline(
            ds,
            pipeline_steps,
            use_majority_voting=use_majority_voting,
            vote_threshold=vote_threshold,
        )

        # safeguard: a drawn ROI reduced below the minimum required by
        # parametric methods is left unchanged, as there is nothing to save
        if int(mask.sum()) < filters.min_surviving_pixels(stack.shape[0]):
            cfg.logger.log.info(
                "Drawn ROI left unchanged: %d px would remain (< %d)"
                % (int(mask.sum()),
                   filters.min_surviving_pixels(stack.shape[0]))
            )
            cfg.mx.msg_war_outliers_too_few_left()
            return None

        cfg.ui_utils.update_bar(
            80,
            QApplication.translate(
                "semiautomaticclassificationplugin", "Polygonizing result..."
            ),
            percentage=80,
        )
        union_geom = filters.mask_to_union_geometry(
            mask, ds.GetGeoTransform(), ds.GetProjection(),
            context=" for drawn ROI",
            log_error=cfg.logger.log.error, log_info=cfg.logger.log.info,
        )
        if union_geom is None:
            cfg.logger.log.error("Polygonize produced no geometry for drawn ROI")
            return stack, mask, report

        srs = osr.SpatialReference()
        srs.ImportFromWkt(ds.GetProjection())

        ogr_driver = ogr.GetDriverByName("GPKG")
        merged_gpkg = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix=".gpkg"
        )
        merged_ds = ogr_driver.CreateDataSource(merged_gpkg)
        merged_layer = merged_ds.CreateLayer(
            "roi", srs=srs, geom_type=ogr.wkbMultiPolygon
        )
        new_feat = ogr.Feature(merged_layer.GetLayerDefn())
        new_feat.SetGeometry(ogr.ForceToMultiPolygon(union_geom))
        merged_layer.CreateFeature(new_feat)
        merged_ds.FlushCache()
        merged_ds = None

        cfg.temporary_roi = cfg.util_qgis.load_geopackage_to_memory_layer(merged_gpkg)
        cfg.scp_dock.clear_scp_dock_rubber()
        cfg.scp_dock.add_roi_polygon_to_map(cfg.temporary_roi, 1)

        return stack, mask, report
    finally:
        cfg.ui_utils.remove_progress_bar(sound=False)
