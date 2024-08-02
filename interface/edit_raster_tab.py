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
"""Edit raster.

This tool allows for direct editing of a raster.
"""
from PyQt5.QtWidgets import QApplication

try:
    from remotior_sensus.tools.raster_edit import check_expression
except Exception as error:
    str(error)

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# radio changed
def radio_vector_field_changed():
    cfg.dialog.ui.use_constant_val_radioButton.blockSignals(True)
    cfg.dialog.ui.use_expression_radioButton.blockSignals(True)
    cfg.dialog.ui.use_field_vector_radioButton.blockSignals(True)
    cfg.dialog.ui.use_expression_radioButton.setChecked(0)
    cfg.dialog.ui.use_constant_val_radioButton.setChecked(0)
    cfg.dialog.ui.use_field_vector_radioButton.setChecked(1)
    cfg.dialog.ui.use_expression_radioButton.blockSignals(False)
    cfg.dialog.ui.use_constant_val_radioButton.blockSignals(False)
    cfg.dialog.ui.use_field_vector_radioButton.blockSignals(False)
    cfg.dialog.ui.edit_val_use_vector_radioButton.setChecked(1)


# radio changed
def radio_constant_val_changed():
    cfg.dialog.ui.use_constant_val_radioButton.blockSignals(True)
    cfg.dialog.ui.use_expression_radioButton.blockSignals(True)
    cfg.dialog.ui.use_field_vector_radioButton.blockSignals(True)
    cfg.dialog.ui.use_expression_radioButton.setChecked(0)
    cfg.dialog.ui.use_constant_val_radioButton.setChecked(1)
    cfg.dialog.ui.use_field_vector_radioButton.setChecked(0)
    cfg.dialog.ui.use_expression_radioButton.blockSignals(False)
    cfg.dialog.ui.use_constant_val_radioButton.blockSignals(False)
    cfg.dialog.ui.use_field_vector_radioButton.blockSignals(False)


# checkbox changed
def radio_use_expression_changed():
    cfg.dialog.ui.use_constant_val_radioButton.blockSignals(True)
    cfg.dialog.ui.use_expression_radioButton.blockSignals(True)
    cfg.dialog.ui.use_field_vector_radioButton.blockSignals(True)
    cfg.dialog.ui.use_expression_radioButton.setChecked(1)
    cfg.dialog.ui.use_constant_val_radioButton.setChecked(0)
    cfg.dialog.ui.use_field_vector_radioButton.setChecked(0)
    cfg.dialog.ui.use_expression_radioButton.blockSignals(False)
    cfg.dialog.ui.use_constant_val_radioButton.blockSignals(False)
    cfg.dialog.ui.use_field_vector_radioButton.blockSignals(False)


# radio button changed
def radio_use_roi_polygon_changed():
    cfg.dialog.ui.edit_val_use_ROI_radioButton.blockSignals(True)
    cfg.dialog.ui.edit_val_use_vector_radioButton.blockSignals(True)
    cfg.dialog.ui.edit_val_use_vector_radioButton.setChecked(0)
    cfg.dialog.ui.edit_val_use_ROI_radioButton.setChecked(1)
    cfg.dialog.ui.edit_val_use_ROI_radioButton.blockSignals(False)
    cfg.dialog.ui.edit_val_use_vector_radioButton.blockSignals(False)


# radio button changed
def radio_use_vector_changed():
    cfg.dialog.ui.edit_val_use_ROI_radioButton.blockSignals(True)
    cfg.dialog.ui.edit_val_use_vector_radioButton.blockSignals(True)
    cfg.dialog.ui.edit_val_use_vector_radioButton.setChecked(1)
    cfg.dialog.ui.edit_val_use_ROI_radioButton.setChecked(0)
    cfg.dialog.ui.edit_val_use_ROI_radioButton.blockSignals(False)
    cfg.dialog.ui.edit_val_use_vector_radioButton.blockSignals(False)


# edit raster
def edit_raster_action():
    edit_raster()


# edit raster
def edit_raster(toolbar_value=None):
    if (cfg.dialog.ui.edit_val_use_ROI_radioButton.isChecked()
            and cfg.temporary_roi is None):
        cfg.mx.msg_war_4()
        return
    else:
        reference_layer = cfg.dialog.ui.edit_raster_name_combo.currentText()
        layer = cfg.util_qgis.select_layer_by_name(reference_layer)
        if layer is None:
            cfg.mx.msg_err_5()
            cfg.logger.log.error('layer not found: %s' % reference_layer)
            return
        else:
            cfg.logger.log.info('edit raster: %s' % reference_layer)
            reference_path = cfg.util_qgis.qgis_layer_source(layer)
            cfg.edit_old_array = cfg.edit_column_start = None
            cfg.edit_row_start = expression = None
            cfg.dialog.ui.undo_edit_Button.setEnabled(False)
            if toolbar_value is None:
                if cfg.dialog.ui.use_expression_radioButton.isChecked():
                    expression = cfg.dialog.ui.expression_lineEdit.text()
                    constant_value = cfg.dialog.ui.value_spinBox.value()
                    check, _expression = check_expression(
                        expression, constant_value
                    )
                    if check is False:
                        cfg.mx.msg_err_6()
                        cfg.logger.log.error('invalid expression %s'
                                             % str(expression))
                        return
                else:
                    toolbar_value = cfg.dialog.ui.value_spinBox.value()
            # using vector
            if cfg.dialog.ui.edit_val_use_vector_radioButton.isChecked():
                vector_name = cfg.dialog.ui.vector_name_combo_2.currentText()
                shape = cfg.util_qgis.select_layer_by_name(vector_name)
                if shape is None:
                    cfg.mx.msg_err_5()
                    cfg.logger.log.error('layer not found: %s' % vector_name)
                    return
                vector_path = cfg.util_qgis.qgis_layer_source(shape)
                if cfg.dialog.ui.use_field_vector_radioButton.isChecked():
                    vector_field = cfg.dialog.ui.field_comboBox_2.currentText()
                else:
                    vector_field = None
            # using ROI polygon
            elif cfg.dialog.ui.edit_val_use_ROI_radioButton.isChecked():
                # get vector from ROI
                vector_path = cfg.rs.configurations.temp.temporary_file_path(
                    name_suffix='.gpkg'
                )
                vector_field = None
                cfg.util_qgis.save_memory_layer_to_geopackage(
                    cfg.temporary_roi, vector_path
                )
                # hide ROI
                cfg.show_ROI_radioButton.setChecked(False)
                cfg.scp_dock.show_hide_roi()
            else:
                return
            cfg.ui_utils.add_progress_bar()
            # perform edit
            output = cfg.rs.raster_edit(
                raster_path=reference_path, vector_path=vector_path,
                field_name=vector_field,
                expression=expression, constant_value=toolbar_value
            )
            if output.check:
                cfg.edit_old_array = output.extra['old_array']
                cfg.edit_column_start = output.extra['column_start']
                cfg.edit_row_start = output.extra['row_start']
                layer.reload()
                layer.triggerRepaint(True)
                cfg.map_canvas.refresh()
                cfg.dialog.ui.undo_edit_Button.setEnabled(True)
            cfg.ui_utils.remove_progress_bar(
                smtp=str(__name__), failed=not output.check
            )


# undo edit raster
# noinspection PyTypeChecker
def undo_edit():
    answer = cfg.util_qt.question_box(
        QApplication.translate('semiautomaticclassificationplugin',
                               'Undo raster editing'),
        QApplication.translate('semiautomaticclassificationplugin',
                               'Are you sure you want to undo?')
    )
    if answer and cfg.edit_old_array is not None:
        reference_layer = cfg.dialog.ui.edit_raster_name_combo.currentText()
        layer = cfg.util_qgis.select_layer_by_name(reference_layer)
        if layer is None:
            cfg.mx.msg_err_5()
            cfg.logger.log.error('layer not found: %s' % reference_layer)
            return
        else:
            cfg.logger.log.info('edit raster: %s' % reference_layer)
            reference_path = cfg.util_qgis.qgis_layer_source(layer)
            cfg.dialog.ui.undo_edit_Button.setEnabled(False)
            cfg.ui_utils.add_progress_bar()
            # perform edit
            output = cfg.rs.raster_edit(
                raster_path=reference_path, old_array=cfg.edit_old_array,
                column_start=cfg.edit_column_start,
                row_start=cfg.edit_row_start
            )
            if output.check:
                cfg.edit_old_array = cfg.edit_column_start = None
                cfg.edit_row_start = None
                layer.reload()
                layer.triggerRepaint(True)
                cfg.map_canvas.refresh()
            cfg.ui_utils.remove_progress_bar(
                smtp=str(__name__), failed=not output.check
            )


# set script button
def set_script():
    reference_layer = cfg.dialog.ui.edit_raster_name_combo.currentText()
    layer = cfg.util_qgis.select_layer_by_name(reference_layer)
    if layer is None:
        reference_path = 'raster_path'
    else:
        reference_path = cfg.util_qgis.qgis_layer_source(layer)
    vector_field = None
    if cfg.dialog.ui.edit_val_use_ROI_radioButton.isChecked():
        vector_path = 'vector_path'
    else:
        vector_name = cfg.dialog.ui.vector_name_combo_2.currentText()
        shape = cfg.util_qgis.select_layer_by_name(vector_name)
        if shape is None:
            vector_path = 'vector_path'
        else:
            vector_path = cfg.util_qgis.qgis_layer_source(shape)
            if cfg.dialog.ui.use_field_vector_radioButton.isChecked():
                vector_field = cfg.dialog.ui.field_comboBox_2.currentText()
    if cfg.dialog.ui.use_expression_radioButton.isChecked():
        expression = cfg.dialog.ui.expression_lineEdit.text()
        toolbar_value = None
    else:
        expression = None
        toolbar_value = cfg.dialog.ui.value_spinBox.value()
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# edit raster\n'
               'rs.raster_edit(raster_path="%s", vector_path="%s", '
               'field_name="%s", expression="%s", constant_value=%s)'
               % (str(reference_path), str(vector_path), str(vector_field),
                  str(expression), str(toolbar_value)))
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
