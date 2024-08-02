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
"""Masking bands.

This tool allows for masking bands.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# value text changed
def text_changed():
    check_value_list()


# check value list
def check_value_list():
    try:
        # class value list
        values = cfg.utils.text_to_value_list(
            cfg.dialog.ui.cloud_mask_classes_lineEdit.text()
        )
        cfg.dialog.ui.cloud_mask_classes_lineEdit.setStyleSheet(
            'color : green'
        )
    except Exception as err:
        str(err)
        cfg.dialog.ui.cloud_mask_classes_lineEdit.setStyleSheet('color : red')
        values = []
    return values


# mask band sets
def mask_action():
    masking_bandset()


# bandset masking
# noinspection PyTypeChecker
def masking_bandset():
    # class value list
    values = check_value_list()
    if len(values) > 0:
        output_path = cfg.util_qt.get_existing_directory()
        if output_path is not False:
            cfg.logger.log.info('masking_bandset: %s' % output_path)
            output_name = cfg.dialog.ui.mask_output_name_lineEdit.text()
            if len(output_name) == 0:
                output_name = None
            bandset_number = cfg.dialog.ui.band_set_comb_spinBox_9.value()
            classification_layer = (
                cfg.dialog.ui.classification_name_combo_4.currentText())
            classification = cfg.util_qgis.get_file_path(classification_layer)
            nodata = cfg.dialog.ui.nodata_spinBox_11.value()
            if cfg.dialog.ui.cloud_buffer_checkBox.isChecked() is True:
                buffer = cfg.dialog.ui.cloud_buffer_spinBox.value()
            else:
                buffer = None
            if cfg.dialog.ui.mask_virtual_checkBox.isChecked() is True:
                virtual_output = True
            else:
                virtual_output = False
            cfg.ui_utils.add_progress_bar()
            output = cfg.rs.band_mask(
                input_bands=bandset_number, input_mask=classification,
                mask_values=values, output_path=output_path,
                prefix=output_name, buffer=buffer, nodata_value=nodata,
                bandset_catalog=cfg.bandset_catalog,
                virtual_output=virtual_output
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
    values = check_value_list()
    output_name = cfg.dialog.ui.mask_output_name_lineEdit.text()
    if len(output_name) == 0:
        output_name = None
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_9.value()
    classification_layer = (
        cfg.dialog.ui.classification_name_combo_4.currentText())
    classification = cfg.util_qgis.get_file_path(classification_layer)
    nodata = cfg.dialog.ui.nodata_spinBox_11.value()
    if cfg.dialog.ui.cloud_buffer_checkBox.isChecked() is True:
        buffer = cfg.dialog.ui.cloud_buffer_spinBox.value()
    else:
        buffer = None
    if cfg.dialog.ui.mask_virtual_checkBox.isChecked() is True:
        virtual_output = True
    else:
        virtual_output = False
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
    command = ('# masking bands (input files from bandset)\n'
               'rs.band_mask(input_bands=%s, input_mask="%s", mask_values=%s, '
               'output_path="%s", prefix="%s", buffer=%s, nodata_value=%s, '
               'virtual_output=%s)'
               % (str(paths), str(classification), str(values),
                  str(output_path), str(output_name), str(buffer),
                  str(nodata), str(virtual_output)))
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
