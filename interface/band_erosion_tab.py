# SemiAutomaticClassificationPlugin
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised 
# classification of remote sensing images, providing tools for the download, 
# the preprocessing and postprocessing of images.
# begin: 2012-12-29
# Copyright (C) 2012-2023 by Luca Congedo.
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
"""Band erosion.

This tool allows for the geometric erosion of pixel values.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# value text changed
def text_changed():
    check_value_list()


# check value list
def check_value_list():
    try:
        values = cfg.utils.text_to_value_list(
            cfg.dialog.ui.erosion_classes_lineEdit.text()
        )
        cfg.dialog.ui.erosion_classes_lineEdit.setStyleSheet('color : green')
    except Exception as err:
        str(err)
        cfg.dialog.ui.erosion_classes_lineEdit.setStyleSheet('color : red')
        values = []
    return values


# band erosion
def band_erosion_action():
    band_erosion()


# band erosion
def band_erosion():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_17.value()
    if bandset_number > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    # class value list
    values = check_value_list()
    if len(values) > 0:
        output_path = cfg.util_qt.get_existing_directory(
            None, cfg.translate('Select a directory')
        )
        if output_path is not False:
            cfg.logger.log.info('band_erosion: %s' % output_path)
            cfg.logger.log.debug('bandset_number: %s' % bandset_number)
            output_name = cfg.dialog.ui.output_name_lineEdit_3.text()
            size = cfg.dialog.ui.erosion_threshold_spinBox.value()
            if cfg.dialog.ui.virtual_output_checkBox_2.isChecked():
                virtual_output = True
            else:
                virtual_output = False
            if cfg.dialog.ui.circular_structure_checkBox_3.isChecked():
                circular = True
            else:
                circular = False
            cfg.ui_utils.add_progress_bar()
            output = cfg.rs.band_erosion(
                input_bands=bandset_number, value_list=values, size=size,
                output_path=output_path, circular_structure=circular,
                prefix=output_name, bandset_catalog=cfg.bandset_catalog,
                virtual_output=virtual_output
            )
            if output.check:
                output_paths = output.paths
                for raster in output_paths:
                    # add raster to layers
                    cfg.util_qgis.add_raster_layer(raster)
            else:
                cfg.mx.msg_err_1()
            cfg.ui_utils.remove_progress_bar(smtp=str(__name__))
    else:
        cfg.mx.msg_inf_5()


# set script button
def set_script():
    output_path = 'output_path'
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_17.value()
    # class value list
    values = check_value_list()
    if len(values) == 0:
        values = '[]'
    output_name = cfg.dialog.ui.output_name_lineEdit_3.text()
    size = cfg.dialog.ui.erosion_threshold_spinBox.value()
    if cfg.dialog.ui.virtual_output_checkBox_2.isChecked():
        virtual_output = True
    else:
        virtual_output = False
    if cfg.dialog.ui.circular_structure_checkBox_3.isChecked():
        circular = True
    else:
        circular = False
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
    command = ('# band erosion (input files from bandset)\n'
               'rs.band_erosion(input_bands=%s, value_list=%s, size=%s, '
               'output_path="%s", circular_structure=%s, prefix="%s", '
               'virtual_output=%s)'
               % (str(paths), str(values), str(size), str(output_path),
                  str(circular), str(output_name), str(virtual_output)))
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
