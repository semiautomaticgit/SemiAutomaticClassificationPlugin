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
"""Band PCA.

This tool allows for calculation of principal components.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# calculate PCA action
def calculate_pca_action():
    calculate_pca()


# calculate PCA
def calculate_pca():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_4.value()
    if bandset_number > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    components_number = cfg.dialog.ui.pca_components_spinBox.value()
    if cfg.dialog.ui.num_comp_checkBox.isChecked() is True:
        if components_number > bandset_x.get_band_count():
            components_number = bandset_x.get_band_count()
    else:
        components_number = bandset_x.get_band_count()
    if cfg.dialog.ui.nodata_checkBox_4.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_5.value()
    else:
        nodata = None
    output_path = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Save error matrix raster output'), '',
        'TIF file (*.tif);;VRT file (*.vrt)'
    )
    if output_path is not False:
        if output_path.lower().endswith('.vrt'):
            pass
        elif not output_path.lower().endswith('.tif'):
            output_path += '.tif'
        cfg.logger.log.info('calculate_pca: %s' % output_path)
        cfg.logger.log.debug('bandset_number: %s' % bandset_number)
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.band_pca(
            input_bands=bandset_number, output_path=output_path,
            nodata_value=nodata, number_components=components_number,
            bandset_catalog=cfg.bandset_catalog
        )
        if output.check:
            output_paths = output.paths
            output_table = output.extra['table']
            for raster in output_paths:
                # add raster to layers
                cfg.util_qgis.add_raster_layer(raster)
            if cfg.utils.check_file(output_table):
                with open(output_table, 'r') as f:
                    text = f.read()
                cfg.dialog.ui.report_textBrowser_2.setText(
                    text.replace(',', '\t')
                )
                cfg.dialog.ui.toolBox_PCA.setCurrentIndex(1)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


# set script button
def set_script():
    output_path = 'output_path'
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_4.value()
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    if bandset_x is not None:
        components_number = cfg.dialog.ui.pca_components_spinBox.value()
        if cfg.dialog.ui.num_comp_checkBox.isChecked() is True:
            if components_number > bandset_x.get_band_count():
                components_number = bandset_x.get_band_count()
        else:
            components_number = bandset_x.get_band_count()
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
        components_number = None
    if cfg.dialog.ui.nodata_checkBox_4.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_5.value()
    else:
        nodata = None
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# band pca (input files from bandset)\n'
               'rs.band_pca(input_bands=%s, output_path="%s", nodata_value=%s,'
               ' number_components=%s)'
               % (str(paths), str(output_path), str(nodata),
                  str(components_number)))
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
