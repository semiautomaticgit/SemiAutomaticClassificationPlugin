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
"""Band neighbor.

This tool allows for neighbor calculation.
"""
from PyQt5.QtWidgets import QApplication

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# stat combo
def load_statistic_combo():
    cfg.dialog.ui.statistic_name_combobox_2.blockSignals(True)
    cfg.dialog.ui.statistic_name_combobox_2.clear()
    for i in cfg.rs.configurations.statistics_list:
        cfg.dialog.statistic_name_combo2(i[0])
    cfg.dialog.ui.statistic_name_combobox_2.blockSignals(False)


# neighbor
def band_neighbor_action():
    band_neighbor()


# matrix file
# noinspection PyTypeChecker
def input_matrix_file():
    m = cfg.util_qt.get_open_file(
        None, QApplication.translate('semiautomaticclassificationplugin',
                                     'Select a XML file'),
        '', 'CSV file (*.csv);;Text file (*.txt)'
    )
    cfg.dialog.ui.label_287.setText(str(m))


# band neighbor
# noinspection PyTypeChecker
def band_neighbor():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_15.value()
    if bandset_number > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    output_path = cfg.util_qt.get_existing_directory()
    if output_path is not False:
        cfg.logger.log.info('band_neighbor: %s' % output_path)
        cfg.logger.log.debug('bandset_number: %s' % bandset_number)
        if cfg.dialog.ui.neighbor_virtual_checkBox.isChecked():
            virtual_output = True
        else:
            virtual_output = False
        if cfg.dialog.ui.circular_structure_checkBox.isChecked():
            circular_structure = True
        else:
            circular_structure = False
        size = cfg.dialog.ui.class_neighbor_threshold_spinBox.value()
        output_name = cfg.dialog.ui.neighbor_output_name_lineEdit.text()
        stat_name = cfg.dialog.ui.statistic_name_combobox_2.currentText()
        structure = cfg.dialog.ui.label_287.text()
        if len(structure) == 0:
            structure = None
        stat_percentile = cfg.dialog.ui.statistic_lineEdit_2.text()
        if len(stat_percentile) == 0:
            stat_percentile = None
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.band_neighbor_pixels(
            input_bands=bandset_number, size=size, structure=structure,
            stat_percentile=stat_percentile, output_path=output_path,
            prefix=output_name, circular_structure=circular_structure,
            stat_name=stat_name, bandset_catalog=cfg.bandset_catalog,
            virtual_output=virtual_output, multiple_resolution=True
        )
        if output.check:
            output_paths = output.paths
            for raster in output_paths:
                # add raster to layers
                cfg.util_qgis.add_raster_layer(raster)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(
            smtp=str(__name__), failed=not output.check
        )


# set script button
def set_script():
    output_path = 'output_path'
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_15.value()
    output_name = cfg.dialog.ui.neighbor_output_name_lineEdit.text()
    size = cfg.dialog.ui.class_neighbor_threshold_spinBox.value()
    if cfg.dialog.ui.neighbor_virtual_checkBox.isChecked():
        virtual_output = True
    else:
        virtual_output = False
    if cfg.dialog.ui.circular_structure_checkBox.isChecked():
        circular_structure = True
    else:
        circular_structure = False
    stat_name = cfg.dialog.ui.statistic_name_combobox_2.currentText()
    structure = cfg.dialog.ui.label_287.text()
    if len(structure) == 0:
        structure = None
    stat_percentile = cfg.dialog.ui.statistic_lineEdit_2.text()
    if len(stat_percentile) == 0:
        stat_percentile = None
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
    command = ('# band neighbor (input files from bandset)\n'
               'rs.band_neighbor_pixels(input_bands=%s, size=%s, structure=%s,'
               ' stat_percentile=%s, output_path="%s", prefix="%s", '
               'circular_structure="%s", stat_name="%s", virtual_output="%s", '
               'multiple_resolution=True)'
               % (str(paths), str(size), str(structure), str(stat_percentile),
                  str(output_path), str(output_name),
                  str(circular_structure), str(stat_name), str(virtual_output))
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
