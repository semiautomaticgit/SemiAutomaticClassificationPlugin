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
"""Spectral distance.

This tool allows for calculation of spectral distance between two band sets.
"""
from PyQt5.QtWidgets import QApplication

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# calculate spectral distance action
def calculate_spectral_distance_action():
    calculate_spectral_distance()


# calculate spectral distance
def calculate_spectral_distance():
    bandset_number_1 = cfg.dialog.ui.band_set_comb_spinBox_6.value()
    if bandset_number_1 > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    bandset_number_2 = cfg.dialog.ui.band_set_comb_spinBox_7.value()
    if bandset_number_2 > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    if cfg.dialog.ui.min_distance_radioButton_2.isChecked() is True:
        algorithm_name = cfg.rs.configurations.minimum_distance_a
    else:
        algorithm_name = cfg.rs.configurations.spectral_angle_mapping_a
    if cfg.dialog.ui.distance_threshold_checkBox.isChecked() is True:
        threshold = cfg.dialog.ui.thresh_doubleSpinBox_2.value()
    else:
        threshold = None
    # noinspection PyTypeChecker
    output_path = cfg.util_qt.get_save_file_name(
        None, QApplication.translate('semiautomaticclassificationplugin',
                                     'Save raster output'),
        '', 'TIF file (*.tif);;VRT file (*.vrt)'
    )
    if output_path is not False:
        virtual_output = False
        if output_path.lower().endswith('.vrt'):
            virtual_output = True
        elif not output_path.lower().endswith('.tif'):
            output_path += '.tif'
        cfg.logger.log.info('calculate_spectral_distance: %s' % output_path)
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.band_spectral_distance(
            input_bandsets=[bandset_number_1, bandset_number_2],
            output_path=output_path, algorithm_name=algorithm_name,
            virtual_output=virtual_output,
            threshold=threshold, bandset_catalog=cfg.bandset_catalog
        )
        if output.check:
            # add raster to layers
            cfg.util_qgis.add_raster_layer(output.path)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(
            smtp=str(__name__), failed=not output.check
        )


# set script button
def set_script():
    output_path = 'output_path'
    bandset_number_1 = cfg.dialog.ui.band_set_comb_spinBox_6.value()
    bandset_number_2 = cfg.dialog.ui.band_set_comb_spinBox_7.value()
    if cfg.dialog.ui.min_distance_radioButton_2.isChecked() is True:
        algorithm_name = cfg.rs.configurations.minimum_distance_a
    else:
        algorithm_name = cfg.rs.configurations.spectral_angle_mapping_a
    if cfg.dialog.ui.distance_threshold_checkBox.isChecked() is True:
        threshold = cfg.dialog.ui.thresh_doubleSpinBox_2.value()
    else:
        threshold = None
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# spectral distance\n'
               'rs.band_spectral_distance(input_bandsets=[%s, %s], '
               'output_path="%s", algorithm_name="%s", threshold=%s'
               'bandset_catalog=bandset_catalog)'
               % (str(bandset_number_1), str(bandset_number_2),
                  str(output_path), str(algorithm_name), str(threshold)))
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
