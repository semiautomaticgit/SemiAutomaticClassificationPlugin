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
"""Mosaic band sets.

This tool allows for the mosaic of band sets.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# list band sets
def text_changed():
    check_bandset_list()


# check bandset list
def check_bandset_list():
    try:
        text = cfg.dialog.ui.mosaic_band_sets_lineEdit.text()
        if text == '*':
            values = list(
                range(1, cfg.bandset_catalog.get_bandset_count() + 1)
            )
        else:
            values = text.split(',')
        bandset_list = []
        for value in values:
            bandset_list.append(int(value))
        cfg.dialog.ui.mosaic_band_sets_lineEdit.setStyleSheet('color : green')
    except Exception as err:
        str(err)
        cfg.dialog.ui.mosaic_band_sets_lineEdit.setStyleSheet('color : red')
        bandset_list = []
    return bandset_list


# mosaic band sets
def mosaic_action():
    mosaic_bandsets()


# mosaic multiple bandsets
# noinspection PyTypeChecker
def mosaic_bandsets():
    bandset_list = check_bandset_list()
    if len(bandset_list) > 0:
        output_path = cfg.util_qt.get_existing_directory()
        if output_path is not False:
            cfg.logger.log.info('band_sieve: %s' % output_path)
            output_name = cfg.dialog.ui.mosaic_output_name_lineEdit.text()
            if len(output_name) == 0:
                output_name = None
            prefix = cfg.dialog.ui.mosaic_output_prefix.text()
            if len(prefix) == 0:
                prefix = None
            if cfg.dialog.ui.mosaic_virtual_checkBox.isChecked() is True:
                virtual_output = True
            else:
                virtual_output = False
            if cfg.dialog.ui.nodata_checkBox_9.isChecked():
                nodata_value = cfg.dialog.ui.nodata_spinBox_10.value()
            else:
                nodata_value = None
            cfg.ui_utils.add_progress_bar()
            output = cfg.rs.mosaic(
                input_bands=bandset_list, output_path=output_path,
                nodata_value=nodata_value, prefix=prefix,
                output_name=output_name, bandset_catalog=cfg.bandset_catalog,
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
    bandset_list = check_bandset_list()
    output_name = cfg.dialog.ui.mosaic_output_name_lineEdit.text()
    if len(output_name) == 0:
        output_name = None
    prefix = cfg.dialog.ui.mosaic_output_prefix.text()
    if len(prefix) == 0:
        prefix = None
    if cfg.dialog.ui.mosaic_virtual_checkBox.isChecked() is True:
        virtual_output = True
    else:
        virtual_output = False
    if cfg.dialog.ui.nodata_checkBox_9.isChecked():
        nodata_value = cfg.dialog.ui.nodata_spinBox_10.value()
    else:
        nodata_value = None
    # get input band paths
    if len(bandset_list) == 1:
        # get input band paths
        bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_list[0])
        absolute_paths = bandset_x.get_absolute_paths()
        path_list = '['
        for file in absolute_paths:
            path_list += '"%s", ' % file
        path_list = path_list[:-2] + ']'
        if path_list == ']':
            path_list = '[]'
    elif len(bandset_list) > 0:
        try:
            bandset_x = cfg.bandset_catalog.get_bandset_by_number(
                bandset_list[0]
            )
            absolute_paths = bandset_x.get_absolute_paths()
            path_list = '['
            for n in range(0, len(absolute_paths)):
                paths = '['
                for bandset_number in bandset_list:
                    bandset_x = cfg.bandset_catalog.get_bandset_by_number(
                        bandset_number
                    )
                    files = bandset_x.get_absolute_paths()
                    paths += '"%s", ' % files[n]
                paths = paths[:-2] + ']'
                if paths == ']':
                    paths = '[]'
                path_list += paths + ', '
            path_list = path_list[:-2] + ']'
            if path_list == ']':
                path_list = '[]'
        except Exception as err:
            str(err)
            path_list = '[]'
    else:
        path_list = '[]'
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# band sets mosaic (input files from bandset)\n'
               'rs.mosaic(input_bands=%s, output_path="%s", nodata_value=%s, '
               'prefix="%s", output_name="%s", virtual_output=%s)'
               % (str(path_list), str(output_path), str(nodata_value),
                  str(prefix), str(output_name), str(virtual_output))
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
