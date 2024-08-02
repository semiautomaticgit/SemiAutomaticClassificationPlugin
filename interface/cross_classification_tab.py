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
"""Cross classification.

This tool allows for calculation of cross classification.
"""
from PyQt5.QtWidgets import QApplication

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# reference layer name
def reference_layer_name():
    reference_layer = cfg.dialog.ui.reference_name_combo_2.currentText()
    cfg.dialog.ui.class_field_comboBox_2.clear()
    layer = cfg.util_qgis.select_layer_by_name(reference_layer)
    try:
        if layer.type() == cfg.util_qgis.get_qgis_map_vector():
            fields = layer.dataProvider().fields()
            for field in fields:
                if str(field.typeName()).lower() != 'string':
                    cfg.dialog.class_field_combo_2(str(field.name()))
    except Exception as err:
        str(err)


# refresh reference layer name
def refresh_reference_layer():
    # noinspection PyArgumentList
    layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
    cfg.dialog.ui.reference_name_combo_2.clear()
    for layer in sorted(layers, key=lambda c: c.name()):
        if layer.type() == cfg.util_qgis.get_qgis_map_vector():
            if (layer.wkbType() == cfg.util_qgis.get_qgis_wkb_types().Polygon
                    or layer.wkbType() ==
                    cfg.util_qgis.get_qgis_wkb_types().MultiPolygon):
                cfg.dialog.reference_layer_combo_2(layer.name())
        elif layer.type() == cfg.util_qgis.get_qgis_map_raster():
            if layer.bandCount() == 1:
                cfg.dialog.reference_layer_combo_2(layer.name())


# calculate cross classification if click on button
def cross_classification_action():
    cross_classification()


# cross classification calculation
# noinspection PyTypeChecker
def cross_classification():
    output_path = cfg.util_qt.get_save_file_name(
        None, QApplication.translate(
            'semiautomaticclassificationplugin',
            'Save cross classification raster output'),
        '', 'TIF file (*.tif);;VRT file (*.vrt)'
    )
    if output_path is not False:
        if output_path.lower().endswith('.vrt'):
            pass
        elif not output_path.lower().endswith('.tif'):
            output_path += '.tif'
        cfg.logger.log.info('band_sieve: %s' % output_path)
        reference_layer = cfg.dialog.ui.reference_name_combo_2.currentText()
        classification_layer = (
            cfg.dialog.ui.classification_name_combo_2.currentText())
        reference = cfg.util_qgis.get_file_path(reference_layer)
        classification = cfg.util_qgis.get_file_path(classification_layer)
        field = cfg.dialog.ui.class_field_comboBox_2.currentText()
        if len(field) == 0:
            field = None
        # No data value
        if cfg.dialog.ui.nodata_checkBox_6.isChecked() is True:
            nodata = cfg.dialog.ui.nodata_spinBox_7.value()
        else:
            nodata = None
        # regression
        if cfg.dialog.ui.regression_raster_checkBox.isChecked() is True:
            regression = True
        else:
            regression = None
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.cross_classification(
            classification_path=classification, reference_path=reference,
            output_path=output_path, vector_field=field, nodata_value=nodata,
            regression_raster=regression
        )
        if output.check:
            output_raster, output_table = output.paths
            # add raster to layers
            raster = cfg.util_qgis.add_raster_layer(output_raster)
            unique_values = output.extra['unique_values']
            cfg.utils.raster_symbol_generic(
                raster, 'NoData', raster_unique_value_list=unique_values
            )
            if cfg.utils.check_file(output_table):
                with open(output_table, 'r') as f:
                    text = f.read()
                cfg.dialog.ui.cross_matrix_textBrowser.setText(
                    text.replace(',', '\t')
                )
                cfg.dialog.ui.toolBox_cross_classification.setCurrentIndex(1)
            if regression:
                regression_raster_b0 = output.extra['regression_raster_b0']
                regression_raster_b1 = output.extra['regression_raster_b1']
                if cfg.utils.check_file(regression_raster_b0):
                    cfg.util_qgis.add_raster_layer(regression_raster_b0)
                if cfg.utils.check_file(regression_raster_b1):
                    cfg.util_qgis.add_raster_layer(regression_raster_b1)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(
            smtp=str(__name__), failed=not output.check
        )


# set script button
def set_script():
    output_path = 'output_path'
    reference_layer = cfg.dialog.ui.reference_name_combo_2.currentText()
    classification_layer = (
        cfg.dialog.ui.classification_name_combo_2.currentText())
    reference = cfg.util_qgis.get_file_path(reference_layer)
    classification = cfg.util_qgis.get_file_path(classification_layer)
    field = cfg.dialog.ui.class_field_comboBox_2.currentText()
    if len(field) == 0:
        field = None
    # No data value
    if cfg.dialog.ui.nodata_checkBox_6.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_7.value()
    else:
        nodata = None
    # regression
    if cfg.dialog.ui.regression_raster_checkBox.isChecked() is True:
        regression = True
    else:
        regression = None
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# cross classification \n'
               'rs.cross_classification(classification_path="%s", '
               'reference_path="%s", output_path="%s", '
               'vector_field="%s", nodata_value=%s, regression_raster=%s)'
               % (str(classification), str(reference), str(output_path),
                  str(field), str(nodata), str(regression)))
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
