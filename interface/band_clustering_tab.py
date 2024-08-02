# SemiAutomaticClassificationPlugin
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised 
# classification of remote sensing images, providing tools for the download, 
# the preprocessing and postprocessing of images.
# begin: 2012-12-29
# Copyright (C) 2012-2024 by Luca Congedo.
# Author: Luca Congedo
# Email: ing.congedoluca@gmail.com
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
"""Band clustering.

This tool allows for band clustering calculation.
"""
from PyQt5.QtWidgets import QApplication
from .scp_dock import import_library_file

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# algorithm radio
def algorithm_minimum_distance_radio():
    if cfg.dialog.ui.min_distance_radioButton.isChecked() is True:
        cfg.dialog.ui.spectral_angle_map_radioButton.blockSignals(True)
        cfg.dialog.ui.spectral_angle_map_radioButton.setChecked(0)
        cfg.dialog.ui.spectral_angle_map_radioButton.blockSignals(False)
    else:
        cfg.dialog.ui.min_distance_radioButton.blockSignals(True)
        cfg.dialog.ui.min_distance_radioButton.setChecked(1)
        cfg.dialog.ui.min_distance_radioButton.blockSignals(False)


# algorithm radio
def algorithm_sam_radio():
    if cfg.dialog.ui.spectral_angle_map_radioButton.isChecked() is True:
        cfg.dialog.ui.min_distance_radioButton.blockSignals(True)
        cfg.dialog.ui.min_distance_radioButton.setChecked(0)
        cfg.dialog.ui.min_distance_radioButton.blockSignals(False)
    else:
        cfg.dialog.ui.spectral_angle_map_radioButton.blockSignals(True)
        cfg.dialog.ui.spectral_angle_map_radioButton.setChecked(1)
        cfg.dialog.ui.spectral_angle_map_radioButton.blockSignals(False)


# radio changed
def sig_list_changed():
    cfg.dialog.ui.kmean_minmax_radioButton.blockSignals(True)
    cfg.dialog.ui.kmean_siglist_radioButton.blockSignals(True)
    cfg.dialog.ui.kmean_randomsiglist_radioButton.blockSignals(True)
    if cfg.dialog.ui.kmean_siglist_radioButton.isChecked():
        cfg.dialog.ui.kmean_minmax_radioButton.setChecked(0)
        cfg.dialog.ui.kmean_randomsiglist_radioButton.setChecked(0)
    cfg.dialog.ui.kmean_siglist_radioButton.setChecked(1)
    cfg.dialog.ui.kmean_minmax_radioButton.blockSignals(False)
    cfg.dialog.ui.kmean_siglist_radioButton.blockSignals(False)
    cfg.dialog.ui.kmean_randomsiglist_radioButton.blockSignals(False)


# radio changed
def minmax_changed():
    cfg.dialog.ui.kmean_minmax_radioButton.blockSignals(True)
    cfg.dialog.ui.kmean_siglist_radioButton.blockSignals(True)
    cfg.dialog.ui.kmean_randomsiglist_radioButton.blockSignals(True)
    if cfg.dialog.ui.kmean_minmax_radioButton.isChecked():
        cfg.dialog.ui.kmean_siglist_radioButton.setChecked(0)
        cfg.dialog.ui.kmean_randomsiglist_radioButton.setChecked(0)
    cfg.dialog.ui.kmean_minmax_radioButton.setChecked(1)
    cfg.dialog.ui.kmean_minmax_radioButton.blockSignals(False)
    cfg.dialog.ui.kmean_siglist_radioButton.blockSignals(False)
    cfg.dialog.ui.kmean_randomsiglist_radioButton.blockSignals(False)


# radio changed
def random_changed():
    cfg.dialog.ui.kmean_minmax_radioButton.blockSignals(True)
    cfg.dialog.ui.kmean_siglist_radioButton.blockSignals(True)
    cfg.dialog.ui.kmean_randomsiglist_radioButton.blockSignals(True)
    if cfg.dialog.ui.kmean_randomsiglist_radioButton.isChecked():
        cfg.dialog.ui.kmean_siglist_radioButton.setChecked(0)
        cfg.dialog.ui.kmean_minmax_radioButton.setChecked(0)
    cfg.dialog.ui.kmean_randomsiglist_radioButton.setChecked(1)
    cfg.dialog.ui.kmean_minmax_radioButton.blockSignals(False)
    cfg.dialog.ui.kmean_siglist_radioButton.blockSignals(False)
    cfg.dialog.ui.kmean_randomsiglist_radioButton.blockSignals(False)


# clustering
def band_clustering_action():
    band_clustering()


# band clustering
def band_clustering():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_5.value()
    if bandset_number > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    # noinspection PyTypeChecker
    output_path = cfg.util_qt.get_save_file_name(
        None, QApplication.translate('semiautomaticclassificationplugin',
                                     'Save classification'),
        '', 'TIF file (*.tif)'
    )
    if output_path is not False:
        if not output_path.lower().endswith('.tif'):
            output_path += '.tif'
        cfg.logger.log.info('band_clustering: %s' % output_path)
        cfg.logger.log.debug('bandset_number: %s' % bandset_number)
        # class number
        class_number = cfg.dialog.ui.kmeans_classes_spinBox.value()
        # maximum iterations
        max_iter = cfg.dialog.ui.kmeans_iter_spinBox.value()
        if cfg.dialog.ui.kmean_randomsiglist_radioButton.isChecked():
            seed_signatures = cfg.rs.configurations.random_pixel
        elif cfg.dialog.ui.kmean_minmax_radioButton.isChecked():
            seed_signatures = cfg.rs.configurations.band_mean
        else:
            if (cfg.scp_training.signature_catalog is None
                    or cfg.scp_training.signature_catalog is False):
                cfg.mx.msg_war_5()
                return False
            else:
                seed_signatures = cfg.scp_training.signature_catalog

        if cfg.dialog.ui.min_distance_radioButton.isChecked():
            algorithm_name = cfg.rs.configurations.minimum_distance_a
        else:
            algorithm_name = cfg.rs.configurations.spectral_angle_mapping_a
        # threshold
        if cfg.dialog.ui.kmean_threshold_checkBox.isChecked():
            threshold = cfg.dialog.ui.thresh_doubleSpinBox.value()
        else:
            threshold = None
        # nodata
        if cfg.dialog.ui.nodata_checkBox_8.isChecked() is True:
            nodata = cfg.dialog.ui.nodata_spinBox_9.value()
        else:
            nodata = None
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.band_clustering(
            input_bands=bandset_number, output_raster_path=output_path,
            class_number=class_number, algorithm_name=algorithm_name,
            seed_signatures=seed_signatures,
            max_iter=max_iter, threshold=threshold, nodata_value=nodata,
            bandset_catalog=cfg.bandset_catalog,
        )
        if output.check:
            raster = cfg.util_qgis.add_raster_layer(output.path)
            # save signatures
            signature_path = output.extra['signature_path']
            if raster is not False:
                cfg.util_qgis.move_layer_to_top(raster)
                signature_cat = cfg.rs.spectral_signatures_catalog(
                    bandset=cfg.bandset_catalog.get(bandset_number)
                )
                signature_cat.load(file_path=signature_path)
                value_color = signature_cat.macroclasses_color_string
                value_name = signature_cat.macroclasses
                cfg.utils.classification_raster_symbol(
                    classification_layer=raster,
                    value_name_dictionary=value_name,
                    value_color_dictionary=value_color
                )
            # save signatures
            if cfg.dialog.ui.kmean_save_siglist_checkBox.isChecked() is True:
                if cfg.scp_training is None:
                    cfg.mx.msg_war_5()
                    cfg.ui_utils.remove_progress_bar(smtp=str(__name__))
                else:
                    import_library_file(path=signature_path)
            else:
                cfg.ui_utils.remove_progress_bar(smtp=str(__name__))
        else:
            cfg.mx.msg_err_1()
            cfg.ui_utils.remove_progress_bar(smtp=str(__name__), failed=True)


# set script button
def set_script():
    output_path = 'output_path'
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_5.value()
    # class number
    class_number = cfg.dialog.ui.kmeans_classes_spinBox.value()
    # maximum iterations
    max_iter = cfg.dialog.ui.kmeans_iter_spinBox.value()
    if cfg.dialog.ui.kmean_randomsiglist_radioButton.isChecked():
        seed_signatures = cfg.rs.configurations.random_pixel
    elif cfg.dialog.ui.kmean_minmax_radioButton.isChecked():
        seed_signatures = cfg.rs.configurations.band_mean
    else:
        if (cfg.scp_training.signature_catalog is None
                or cfg.scp_training.signature_catalog is False):
            seed_signatures = 'training_path'
        else:
            seed_signatures = cfg.scp_training.output_path
    if cfg.dialog.ui.min_distance_radioButton.isChecked():
        algorithm_name = cfg.rs.configurations.minimum_distance_a
    else:
        algorithm_name = cfg.rs.configurations.spectral_angle_mapping_a
    # threshold
    if cfg.dialog.ui.kmean_threshold_checkBox.isChecked():
        threshold = cfg.dialog.ui.thresh_doubleSpinBox.value()
    else:
        threshold = None
    # nodata
    if cfg.dialog.ui.nodata_checkBox_8.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_9.value()
    else:
        nodata = None
    # get input band paths
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    if bandset_x is not None:
        files = bandset_x.get_absolute_paths()
        paths = '['
        for file in files:
            paths += '"%s", ' % file
        paths = paths[:-2] + ']'
        if paths == ']':
            paths = '[]'
    else:
        paths = '[]'
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# band clustering (input files from bandset)\n'
               'rs.band_clustering(input_bands=%s, output_raster_path="%s", '
               'class_number=%s, algorithm_name="%s", max_iter=%s, '
               'threshold=%s, nodata_value=%s, seed_signatures="%s")'
               % (str(paths), str(output_path), str(class_number),
                  str(algorithm_name), str(max_iter), str(threshold),
                  str(nodata), str(seed_signatures))
               )
    previous = cfg.dialog.ui.plainTextEdit_batch.toPlainText()
    if 'import remotior_sensus' in previous:
        text = '\n'.join([previous, command])
    else:
        text = '\n'.join(
            ['import remotior_sensus', session, previous, command]
        )
    cfg.dialog.ui.plainTextEdit_batch.setPlainText(
        text.replace('"None"', 'None').replace('"False"', 'False').replace(
            '"True"', 'True'
        )
    )
    cfg.input_interface.script_tab()
