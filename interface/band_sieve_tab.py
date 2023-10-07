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
"""Band sieve.

This tool allows for sieve calculation.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# sieve classification
def sieve_classification_action():
    band_sieve()


# band sieve
def band_sieve():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_18.value()
    if bandset_number > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    output_path = cfg.util_qt.get_existing_directory(
        None, cfg.translate('Select a directory')
    )
    if output_path is not False:
        cfg.logger.log.info('band_sieve: %s' % output_path)
        cfg.logger.log.debug('bandset_number: %s' % bandset_number)
        output_name = cfg.dialog.ui.output_name_lineEdit_4.text()
        size = cfg.dialog.ui.sieve_threshold_spinBox.value()
        if cfg.dialog.ui.virtual_output_checkBox_3.isChecked():
            virtual_output = True
        else:
            virtual_output = False
        if cfg.dialog.ui.sieve_connection_combo.currentText() == '8':
            connection = True
        else:
            connection = False
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.band_sieve(
            input_bands=bandset_number, size=size, output_path=output_path,
            connected=connection, prefix=output_name,
            bandset_catalog=cfg.bandset_catalog, virtual_output=virtual_output
        )
        if output.check:
            output_paths = output.paths
            for raster in output_paths:
                # add raster to layers
                cfg.util_qgis.add_raster_layer(raster)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


# set script button
def set_script():
    output_path = 'output_path'
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_18.value()
    output_name = cfg.dialog.ui.output_name_lineEdit_4.text()
    size = cfg.dialog.ui.sieve_threshold_spinBox.value()
    if cfg.dialog.ui.virtual_output_checkBox_3.isChecked():
        virtual_output = True
    else:
        virtual_output = False
    if cfg.dialog.ui.sieve_connection_combo.currentText() == '8':
        connection = True
    else:
        connection = False
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
    command = ('# band sieve (input files from bandset)\n'
               'rs.band_sieve(input_bands=%s, size=%s, output_path="%s", '
               'connected=%s, prefix="%s", virtual_output=%s)'
               % (str(paths), str(size), str(output_path), str(connection),
                  str(output_name), str(virtual_output)))

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
