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
"""Vector to raster.

This tool allows for the conversion of vector to raster.
"""
from PyQt5.QtWidgets import QApplication

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# reload vector list
def reload_vector_list():
    cfg.utils.refresh_vector_layer()


# convert to raster
def convert_to_raster_action():
    convert_to_raster()


# convert to raster
def convert_to_raster():
    vector = cfg.dialog.ui.vector_name_combo.currentText()
    layer = cfg.util_qgis.select_layer_by_name(vector)
    references = cfg.dialog.ui.reference_raster_name_combo.currentText()
    reference = cfg.util_qgis.select_layer_by_name(references)
    if layer is None or reference is None:
        cfg.utils.refresh_vector_layer()
        cfg.utils.refresh_raster_layer()
        return
    vector_source = cfg.util_qgis.qgis_layer_source(layer)
    reference_source = cfg.util_qgis.qgis_layer_source(reference)
    field = cfg.dialog.ui.field_comboBox.currentText()
    if cfg.dialog.ui.field_radioButton.isChecked():
        constant = None
    else:
        constant = cfg.dialog.ui.constant_value_spinBox.value()
    if len(field) == 0 and cfg.dialog.ui.field_radioButton.isChecked():
        cfg.utils.refresh_vector_layer()
        return
    if cfg.dialog.ui.conversion_type_combo.currentText() == 'pixel_center':
        conversion_type = 'pixel_center'
    elif cfg.dialog.ui.conversion_type_combo.currentText() == 'all_touched':
        conversion_type = 'all_touched'
    else:
        conversion_type = 'area_based'
    if cfg.dialog.ui.extent_checkBox_2.isChecked():
        minimum_extent = True
    else:
        minimum_extent = None
    try:
        area_precision = float(cfg.dialog.ui.area_precision_lineEdit.text())
    except Exception as err:
        str(err)
        area_precision = 20
    try:
        pixel_size = float(cfg.dialog.ui.pixel_size_lineEdit.text())
    except Exception as err:
        str(err)
        pixel_size = None
    if cfg.dialog.ui.nodata_checkBox_10.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_12.value()
    else:
        nodata = None
    output_path = cfg.util_qt.get_save_file_name(
        None, QApplication.translate('semiautomaticclassificationplugin',
                                     'Save raster output'),
        '', 'TIF file (*.tif);;VRT file (*.vrt)'
    )
    if output_path is not False:
        if output_path.lower().endswith('.tif'):
            pass
        else:
            output_path += '.tif'
        cfg.logger.log.info('convert_to_raster: %s' % output_path)
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.vector_to_raster(
            vector_path=vector_source, align_raster=reference_source,
            vector_field=field, constant=constant, pixel_size=pixel_size,
            output_path=output_path, method=conversion_type,
            area_precision=area_precision, nodata_value=nodata,
            minimum_extent=minimum_extent
        )
        if output.check:
            # add raster to layer
            cfg.util_qgis.add_raster_layer(output.path)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(
            smtp=str(__name__), failed=not output.check
        )


# set script button
def set_script():
    output_path = 'output_path'
    vector = cfg.dialog.ui.vector_name_combo.currentText()
    layer = cfg.util_qgis.select_layer_by_name(vector)
    references = cfg.dialog.ui.reference_raster_name_combo.currentText()
    reference = cfg.util_qgis.select_layer_by_name(references)
    vector_source = cfg.util_qgis.qgis_layer_source(layer)
    reference_source = cfg.util_qgis.qgis_layer_source(reference)
    field = cfg.dialog.ui.field_comboBox.currentText()
    if cfg.dialog.ui.field_radioButton.isChecked():
        constant = None
    else:
        constant = cfg.dialog.ui.constant_value_spinBox.value()
    if cfg.dialog.ui.conversion_type_combo.currentText() == 'pixel_center':
        conversion_type = 'pixel_center'
    elif cfg.dialog.ui.conversion_type_combo.currentText() == 'all_touched':
        conversion_type = 'all_touched'
    else:
        conversion_type = 'area_based'
    if cfg.dialog.ui.extent_checkBox_2.isChecked():
        minimum_extent = True
    else:
        minimum_extent = None
    try:
        area_precision = float(cfg.dialog.ui.area_precision_lineEdit.text())
    except Exception as err:
        str(err)
        area_precision = 20
    try:
        pixel_size = float(cfg.dialog.ui.area_precision_lineEdit.text())
    except Exception as err:
        str(err)
        pixel_size = None
    if cfg.dialog.ui.nodata_checkBox_10.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_12.value()
    else:
        nodata = None

    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# vector to raster \n'
               'rs.vector_to_raster(vector_path="%s", align_raster="%s", '
               'vector_field="%s", constant=%s, pixel_size=%s, '
               'output_path="%s", method="%s", area_precision=%s, '
               'nodata_value=%s, minimum_extent=%s)'
               % (str(vector_source), str(reference_source), str(field),
                  str(constant), str(pixel_size), str(output_path),
                  str(conversion_type), str(area_precision), str(nodata),
                  str(minimum_extent)))
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
