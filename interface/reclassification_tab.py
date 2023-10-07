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
"""Reclassification.

This tool allows for raster reclassification.
"""

import numpy

try:
    from remotior_sensus.core.processor_functions import (
        raster_unique_values_with_sum
    )
except Exception as error:
    str(error)

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# reclassify
def reclassify_action():
    reclassify()


# reclassify
def reclassify():
    reference_layer = cfg.dialog.ui.reclassification_name_combo.currentText()
    reference = cfg.util_qgis.get_file_path(reference_layer)
    value_list = get_values_table()
    if reference is not None and len(value_list) > 0:
        output_path = cfg.util_qt.get_save_file_name(
            None, cfg.translate('Save raster output'), '',
            'TIF file (*.tif);;VRT file (*.vrt)'
        )
        if output_path is not False:
            if output_path.lower().endswith('.vrt'):
                pass
            elif not output_path.lower().endswith('.tif'):
                output_path += '.tif'
            cfg.logger.log.info('reclassify: %s' % output_path)
            cfg.ui_utils.add_progress_bar()
            reclassification_list = create_reclassification_string_from_list(
                value_list
            )
            output = cfg.rs.raster_reclassification(
                raster_path=reference, output_path=output_path,
                reclassification_table=reclassification_list
            )
            if output.check:
                # add raster to layers
                raster = cfg.util_qgis.add_raster_layer(output.path)
                unique_values = [value[1] for value in reclassification_list]
                cfg.utils.raster_symbol_generic(
                    raster, 'NoData', raster_unique_value_list=unique_values
                )
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


def calculate_unique_values():
    input_name = cfg.dialog.ui.reclassification_name_combo.currentText()
    i = cfg.util_qgis.select_layer_by_name(input_name, True)
    try:
        input_path = cfg.util_qgis.qgis_layer_source(i)
    except Exception as err:
        str(err)
        cfg.mx.msg_err_5()
        cfg.utils.refresh_raster_layer()
        return False
    cfg.ui_utils.add_progress_bar()
    cfg.rs.configurations.multiprocess.run(
        raster_path=input_path, function=raster_unique_values_with_sum,
        keep_output_argument=True, dummy_bands=2
    )
    cfg.rs.configurations.multiprocess.multiprocess_unique_values()
    cmb = cfg.rs.configurations.multiprocess.output
    values = numpy.unique(numpy.asarray(cmb[0])).tolist()
    if cfg.dialog.ui.CID_MCID_code_checkBox.isChecked() is True:
        if cfg.scp_training is not None:
            unique = cfg.scp_training.calculate_unique_c_id_mc_id()
        else:
            unique = create_value_list(values)
    else:
        unique = create_value_list(values)
    add_values_to_table(unique)
    cfg.ui_utils.remove_progress_bar()


def incremental_new_values():
    input_name = cfg.dialog.ui.reclassification_name_combo.currentText()
    i = cfg.util_qgis.select_layer_by_name(input_name, True)
    try:
        input_path = cfg.util_qgis.qgis_layer_source(i)
    except Exception as err:
        str(err)
        cfg.mx.msg_err_5()
        cfg.utils.refresh_raster_layer()
        return False
    cfg.ui_utils.add_progress_bar()
    cfg.rs.configurations.multiprocess.run(
        raster_path=input_path, function=raster_unique_values_with_sum,
        keep_output_argument=True, dummy_bands=2
    )
    cfg.rs.configurations.multiprocess.multiprocess_unique_values()
    cmb = cfg.rs.configurations.multiprocess.output
    values = numpy.unique(numpy.asarray(cmb[0])).tolist()
    unique = create_value_list(values, True)
    add_values_to_table(unique)
    cfg.ui_utils.remove_progress_bar()


def create_value_list(values, incremental=False):
    value_list = []
    if incremental is False:
        for i in sorted(values):
            g = str(i).split('.0')
            try:
                _t = g[1]
                p = i
            except Exception as err:
                str(err)
                p = g[0]
            value_list.append([p, p])
    else:
        v = 1
        for i in sorted(values):
            g = str(i).split('.0')
            try:
                t = g[1]
                if len(t) > 0:
                    p = i
                else:
                    p = g[0]
            except Exception as err:
                str(err)
                p = g[0]
            value_list.append([p, str(v)])
            v = v + 1
    return value_list


def add_values_to_table(value_list):
    table = cfg.dialog.ui.reclass_values_tableWidget
    table.blockSignals(True)
    cfg.util_qt.clear_table(table)
    c = table.rowCount()
    for i in value_list:
        table.setRowCount(c + 1)
        cfg.util_qt.add_table_item(table, str(i[0]), c, 0)
        cfg.util_qt.add_table_item(table, str(i[1]), c, 1)
        c += 1
    table.blockSignals(False)


def get_values_table():
    table = cfg.dialog.ui.reclass_values_tableWidget
    c = table.rowCount()
    values = []
    for row in range(0, c):
        old = table.item(row, 0).text()
        new = table.item(row, 1).text()
        values.append([old, new])
    return values


def create_reclassification_string_from_list(value_list):
    reclass_list = []
    for i in value_list:
        try:
            cond = float(i[0])
        except Exception as err:
            str(err)
            cond = str(i[0])
        reclass_list.append([cond, float(i[1])])
    return reclass_list


def add_row():
    table = cfg.dialog.ui.reclass_values_tableWidget
    c = table.rowCount()
    table.blockSignals(True)
    table.setRowCount(c + 1)
    cfg.util_qt.add_table_item(table, '0', c, 0)
    cfg.util_qt.add_table_item(table, '0', c, 1)
    table.blockSignals(False)


def remove_row():
    cfg.util_qt.remove_rows_from_table(
        cfg.dialog.ui.reclass_values_tableWidget
    )


def edited_cell(row, column):
    table = cfg.dialog.ui.reclass_values_tableWidget
    val = table.item(row, column).text()
    if column == 1:
        try:
            float(val)
        except Exception as err:
            str(err)
            table.blockSignals(True)
            cfg.util_qt.set_table_item(table, row, column, '0')
            table.blockSignals(False)
    elif column == 0:
        c = val.replace(
            cfg.qgis_registry[cfg.reg_raster_variable_name], '_array'
        )
        _array = numpy.arange(9).reshape(3, 3)
        try:
            eval('numpy.where(' + c + ', 1, _array)')
        except Exception as err:
            str(err)
            table.blockSignals(True)
            cfg.util_qt.set_table_item(table, row, column, '0')
            table.blockSignals(False)
            cfg.mx.msgWar16()


# import reclass from file
def import_reclass():
    file = cfg.util_qt.get_open_file(
        None, cfg.translate('Select a reclassification file'), '',
        'CSV (*.csv)'
    )
    if len(file) > 0:
        import_reclass_file(file)


# import reclass
def import_reclass_file(file):
    try:
        f = open(file)
        if cfg.utils.check_file(file):
            file = f.readlines()
            if '\t' in file[0]:
                sep = '\t'
            else:
                sep = ','
            table = cfg.dialog.ui.reclass_values_tableWidget
            for b in range(0, len(file)):
                p = file[b].strip().split(sep)
                old_value = 0
                new_value = 0
                try:
                    old_value = p[0]
                    new_value = p[1]
                except Exception as err:
                    str(err)
                c = table.rowCount()
                table.setRowCount(c + 1)
                cfg.util_qt.add_table_item(table, old_value, c, 0)
                cfg.util_qt.add_table_item(table, new_value, c, 1)
    except Exception as err:
        str(err)


# export reclass list to file
def export_reclass():
    list_file = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Save the reclassification list to file'), '',
        '*.csv', 'csv'
    )
    try:
        if list_file.lower().endswith('.csv'):
            pass
        else:
            list_file = list_file + '.csv'
        table = cfg.dialog.ui.reclass_values_tableWidget
        c = table.rowCount()
        f = open(list_file, 'w')
        txt = ''
        sep = ','
        old_value = new_value = None
        for i in range(0, c):
            try:
                old_value = table.item(i, 0).text()
                new_value = table.item(i, 1).text()
            except Exception as err:
                str(err)
        txt += '%s%s%s\n' % (old_value, sep, new_value)
        f.write(txt)
        f.close()
    except Exception as err:
        str(err)


# set script button
def set_script():
    output_path = 'output_path'
    reference_layer = cfg.dialog.ui.reclassification_name_combo.currentText()
    reference = cfg.util_qgis.get_file_path(reference_layer)
    value_list = get_values_table()
    reclassification_list = create_reclassification_string_from_list(
        value_list
    )
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# reclassification \n'
               'rs.raster_reclassification(raster_path="%s", output_path="%s",'
               ' reclassification_table=%s)'
               % (str(reference), str(output_path), str(reclassification_list))
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
