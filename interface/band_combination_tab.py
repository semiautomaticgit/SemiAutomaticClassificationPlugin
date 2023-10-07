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
"""Band combination.

This tool allows for calculating band combination.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# calculate band set combination if click on button
def calculate_band_combination():
    band_combination()


# band combination
def band_combination():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox.value()
    if bandset_number > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    output_path = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Save error matrix raster output'), '',
        'TIF file (*.tif);;VRT file (*.vrt)'
    )
    if output_path is not False:
        cfg.logger.log.info('band_combination: %s' % output_path)
        cfg.logger.log.debug('bandset_number: %s' % bandset_number)
        if output_path.lower().endswith('.vrt'):
            pass
        elif not output_path.lower().endswith('.tif'):
            output_path += '.tif'
        # No data value
        if cfg.dialog.ui.nodata_checkBox_12.isChecked() is True:
            nodata = cfg.dialog.ui.nodata_spinBox_16.value()
        else:
            nodata = None
        column_name_list = []
        bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
        for band in range(1, bandset_x.get_band_count() + 1):
            column_name_list.append('band_%i' % band)
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.band_combination(
            input_bands=bandset_number, output_path=output_path,
            nodata_value=nodata, column_name_list=column_name_list,
            bandset_catalog=cfg.bandset_catalog
        )
        if output.check:
            output_raster, output_table = output.paths
            # add raster to layers
            raster = cfg.util_qgis.add_raster_layer(output_raster)
            unique_values = output.extra['combinations']['new_val'].tolist()
            cfg.utils.raster_symbol_generic(
                raster, 'NoData', raster_unique_value_list=unique_values
            )
            if cfg.utils.check_file(output_table):
                with open(output_table, 'r') as f:
                    text = f.read()
                cfg.dialog.ui.band_set_comb_textBrowser.setText(
                    text.replace(',', '\t')
                )
                cfg.dialog.ui.toolBox_band_set_combination.setCurrentIndex(1)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


# set script button
def set_script():
    output_path = 'output_path'
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox.value()
    # No data value
    if cfg.dialog.ui.nodata_checkBox_12.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_16.value()
    else:
        nodata = None
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    if bandset_x is not None:
        column_name_list = '['
        for band in range(1, bandset_x.get_band_count() + 1):
            column_name_list += '"band_%i", ' % band
        column_name_list = column_name_list[:-2] + ']'
        if column_name_list == ']':
            column_name_list = '[]'
        # get input band paths
        files = bandset_x.get_absolute_paths()
        paths = '['
        for file in files:
            paths += '"%s", ' % file
        paths = paths[:-2] + ']'
        if paths == ']':
            paths = '[]'
    else:
        paths = '[]'
        column_name_list = '[]'
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# band combination (input files from bandset)\n'
               'rs.band_combination(input_bands=%s, output_path="%s", '
               'nodata_value=%s, column_name_list=%s)'
               % (str(paths), str(output_path), str(nodata),
                  str(column_name_list)))
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
