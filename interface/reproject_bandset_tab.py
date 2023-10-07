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
"""Reproject band set.

This tool allows for reprojecting band sets.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# checkbox changed
def radio_align_changed():
    cfg.dialog.ui.align_radioButton.blockSignals(True)
    cfg.dialog.ui.epsg_radioButton.blockSignals(True)
    if cfg.dialog.ui.align_radioButton.isChecked():
        cfg.dialog.ui.epsg_radioButton.setChecked(0)
    cfg.dialog.ui.align_radioButton.blockSignals(False)
    cfg.dialog.ui.epsg_radioButton.blockSignals(False)


# checkbox changed
def radio_epsg_changed():
    cfg.dialog.ui.align_radioButton.blockSignals(True)
    cfg.dialog.ui.epsg_radioButton.blockSignals(True)
    if cfg.dialog.ui.epsg_radioButton.isChecked():
        cfg.dialog.ui.align_radioButton.setChecked(0)
    cfg.dialog.ui.align_radioButton.blockSignals(False)
    cfg.dialog.ui.epsg_radioButton.blockSignals(False)


# refresh reference layer name
def refresh_reference_layer():
    # noinspection PyArgumentList
    ls = cfg.util_qgis.get_qgis_project().mapLayers().values()
    cfg.dialog.ui.raster_align_comboBox.clear()
    for layer in sorted(ls, key=lambda c: c.name()):
        if layer.type() == cfg.util_qgis.get_qgis_map_raster():
            if layer.bandCount() == 1:
                cfg.dialog.project_raster_combo(layer.name())


def reproject_bands_action():
    reproject_bands()


def reproject_bands():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_14.value()
    if bandset_number > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    output_path = cfg.util_qt.get_existing_directory(
        None, cfg.translate('Select a directory')
    )
    if output_path is not False:
        cfg.logger.log.info('band_sieve: %s' % output_path)
        cfg.logger.log.debug('bandset_number: %s' % bandset_number)
        output_name = cfg.dialog.ui.reproj_output_name_lineEdit.text()
        if cfg.dialog.ui.virtual_output_checkBox_4.isChecked():
            virtual_output = True
        else:
            virtual_output = False
        align_raster = epsg = nodata_value = resample_pixel_factor = None
        x_y_resolution = None
        same_extent = False
        if cfg.dialog.ui.align_radioButton.isChecked() is True:
            reference_layer = cfg.dialog.ui.raster_align_comboBox.currentText()
            align_raster = cfg.util_qgis.get_file_path(reference_layer)
            if cfg.dialog.ui.same_extent_raster_checkBox.isChecked() is True:
                same_extent = True
        # use EPSG
        elif cfg.dialog.ui.epsg_radioButton.isChecked() is True:
            try:
                epsg = int(cfg.dialog.ui.epsg_code_lineEdit.text())
            except Exception as err:
                str(err)
        if cfg.dialog.ui.change_nodata_checkBox.isChecked() is True:
            nodata_value = cfg.dialog.ui.nodata_spinBox_14.value()
        if cfg.dialog.ui.resample_checkBox.isChecked() is True:
            try:
                resample_pixel_factor = float(
                    cfg.dialog.ui.resample_lineEdit.text()
                )
            except Exception as err:
                str(err)
        x_resolution = cfg.dialog.ui.x_resolution_lineEdit.text()
        y_resolution = cfg.dialog.ui.y_resolution_lineEdit.text()
        if len(x_resolution) > 0 and len(y_resolution) > 0:
            try:
                x_y_resolution = [float(x_resolution), float(y_resolution)]
            except Exception as err:
                str(err)
        # resampling method
        resampling = cfg.dialog.ui.resampling_method_comboBox.currentText()
        # raster type
        raster_type = cfg.dialog.ui.raster_type_combo_2.currentText()
        if raster_type == 'Auto':
            raster_type = None
        compress_format = cfg.dialog.ui.resample_lineEdit_2.text()
        if cfg.dialog.ui.compress_checkBox.isChecked() is True:
            compress = True
        else:
            compress = False
        # resample
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.band_resample(
            input_bands=bandset_number, output_path=output_path,
            prefix=output_name, epsg_code=epsg, align_raster=align_raster,
            resampling=resampling, nodata_value=nodata_value,
            x_y_resolution=x_y_resolution,
            resample_pixel_factor=resample_pixel_factor,
            output_data_type=raster_type,
            same_extent=same_extent, virtual_output=virtual_output,
            bandset_catalog=cfg.bandset_catalog,
            compress=compress, compress_format=compress_format
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
    output_name = cfg.dialog.ui.reproj_output_name_lineEdit.text()
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_14.value()
    if cfg.dialog.ui.virtual_output_checkBox_4.isChecked():
        virtual_output = True
    else:
        virtual_output = False
    align_raster = epsg = same_extent = nodata_value = None
    resample_pixel_factor = x_y_resolution = None
    if cfg.dialog.ui.align_radioButton.isChecked() is True:
        reference_layer = cfg.dialog.ui.raster_align_comboBox.currentText()
        align_raster = cfg.util_qgis.get_file_path(reference_layer)
        if cfg.dialog.ui.same_extent_raster_checkBox.isChecked() is True:
            same_extent = True
    # use EPSG
    elif cfg.dialog.ui.epsg_radioButton.isChecked() is True:
        try:
            epsg = int(cfg.dialog.ui.epsg_code_lineEdit.text())
        except Exception as err:
            str(err)
    if cfg.dialog.ui.change_nodata_checkBox.isChecked() is True:
        nodata_value = cfg.dialog.ui.nodata_spinBox_14.value()
    if cfg.dialog.ui.resample_checkBox.isChecked() is True:
        try:
            resample_pixel_factor = float(
                cfg.dialog.ui.resample_lineEdit.text()
            )
        except Exception as err:
            str(err)
    x_resolution = cfg.dialog.ui.x_resolution_lineEdit.text()
    y_resolution = cfg.dialog.ui.y_resolution_lineEdit.text()
    if len(x_resolution) > 0 and len(y_resolution) > 0:
        try:
            x_y_resolution = [float(x_resolution), float(y_resolution)]
        except Exception as err:
            str(err)
    # resampling method
    resampling = cfg.dialog.ui.resampling_method_comboBox.currentText()
    # raster type
    raster_type = cfg.dialog.ui.raster_type_combo_2.currentText()
    if raster_type == 'Auto':
        raster_type = None
    compress_format = cfg.dialog.ui.resample_lineEdit_2.text()
    if cfg.dialog.ui.compress_checkBox.isChecked() is True:
        compress = True
    else:
        compress = False
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    if bandset_x is not None:
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
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# reproject band set (input files from bandset)\n'
               'rs.band_resample(input_bands=%s, output_path="%s", '
               'prefix="%s", epsg_code="%s", align_raster="%s", '
               'resampling="%s", nodata_value=%s, x_y_resolution=%s, '
               'resample_pixel_factor=%s, output_data_type="%s", '
               'same_extent=%s, virtual_output=%s, compress=%s, '
               'compress_format="%s")'
               % (str(paths), str(output_path), str(output_name), str(epsg),
                  str(align_raster), str(resampling), str(nodata_value),
                  str(x_y_resolution), str(resample_pixel_factor),
                  str(raster_type), str(same_extent), str(virtual_output),
                  str(compress), str(compress_format))
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
