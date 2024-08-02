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
"""RGB composite.

This tool allows for managing RGB composites.
"""
from PyQt5.QtWidgets import QApplication
from itertools import permutations

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# Create RGB table
def rgb_table_from_list(rgb_list):
    table = cfg.dialog.ui.RGB_tableWidget
    table.blockSignals(True)
    cfg.util_qt.clear_table(table)
    x = 0
    for rgb in rgb_list:
        if rgb != '-':
            cfg.util_qt.insert_table_row(table, x)
            cfg.util_qt.add_table_item(table, rgb, x, 0)
            x += 1
    table.blockSignals(False)


# edited table
def edited_table(row, column):
    table = cfg.dialog.ui.RGB_tableWidget
    rgb_item = table.item(row, column).text()
    try:
        check = cfg.utils.create_rgb_color_composite(rgb_item)
    except Exception as err:
        str(err)
        rgb_table_from_list(cfg.project_registry[cfg.reg_rgb_list])
        return False
    if check is True:
        rgb_list = read_rgb_table()
        cfg.project_registry[cfg.reg_rgb_list] = rgb_list
        cfg.util_qt.set_combobox_items(
            cfg.rgb_combo, cfg.project_registry[cfg.reg_rgb_list]
        )
        # update combo
        rgb_id = cfg.rgb_combo.findText(rgb_item)
        cfg.rgb_combo.setCurrentIndex(rgb_id)
    else:
        rgb_table_from_list(cfg.project_registry[cfg.reg_rgb_list])


# read RGB table
def read_rgb_table():
    table = cfg.dialog.ui.RGB_tableWidget
    count = table.rowCount()
    rgb_list = ['-']
    for row in range(0, count):
        item = table.item(row, 0).text()
        rgb_list.append(item)
    return rgb_list


# add RGB
def add_composite_to_table():
    table = cfg.dialog.ui.RGB_tableWidget
    count = table.rowCount()
    table.setRowCount(count + 1)
    cfg.util_qt.add_table_item(table, '0-0-0', count, 0)


# remove RGB
def remove_composite_from_table():
    cfg.util_qt.remove_rows_from_table(cfg.dialog.ui.RGB_tableWidget)
    rgb_list = read_rgb_table()
    cfg.project_registry[cfg.reg_rgb_list] = rgb_list
    cfg.util_qt.set_combobox_items(
        cfg.rgb_combo, cfg.project_registry[cfg.reg_rgb_list]
    )


# sort RGB
def sort_composite_names():
    rgb_list = cfg.project_registry[cfg.reg_rgb_list]
    sorted_list = sorted(rgb_list)
    cfg.project_registry[cfg.reg_rgb_list] = sorted_list
    rgb_table_from_list(cfg.project_registry[cfg.reg_rgb_list])
    cfg.util_qt.set_combobox_items(
        cfg.rgb_combo, cfg.project_registry[cfg.reg_rgb_list]
    )


def clear_table_action():
    clear_table()


# clear table
# noinspection PyTypeChecker
def clear_table(question=True):
    if question is True:
        answer = cfg.util_qt.question_box(
            QApplication.translate('semiautomaticclassificationplugin',
                                   'Reset RGB composites'),
            QApplication.translate(
                'semiautomaticclassificationplugin',
                'Are you sure you want to clear the RGB list?'
            )
        )
    else:
        answer = True
    if answer is True:
        table = cfg.dialog.ui.RGB_tableWidget
        cfg.util_qt.clear_table(table)
        rgb_list = read_rgb_table()
        cfg.project_registry[cfg.reg_rgb_list] = rgb_list
        cfg.util_qt.set_combobox_items(
            cfg.rgb_combo, cfg.project_registry[cfg.reg_rgb_list]
        )


# move up selected composite
def move_up_composite():
    table = cfg.dialog.ui.RGB_tableWidget
    table.blockSignals(True)
    count = table.rowCount()
    selected = table.selectedItems()
    selected_rows = []
    for item in range(0, len(selected)):
        selected_rows.append(selected[item].row() - 1)
    try:
        for row in range(0, count):
            if table.item(row, 0).isSelected():
                selected_item = table.item(row, 0).text()
                previous_item = table.item(row - 1, 0).text()
                table.item(row, 0).setText(str(previous_item))
                table.item(row - 1, 0).setText(str(selected_item))
        table.clearSelection()
        values = list(set(selected_rows))
        for item in range(0, len(values)):
            table.selectRow(values[item])
    except Exception as err:
        str(err)
        table.clearSelection()
    table.blockSignals(False)
    rgb_list = read_rgb_table()
    cfg.project_registry[cfg.reg_rgb_list] = rgb_list
    cfg.util_qt.set_combobox_items(
        cfg.rgb_combo, cfg.project_registry[cfg.reg_rgb_list]
    )


# move down selected composite
def move_down_composite():
    table = cfg.dialog.ui.RGB_tableWidget
    table.blockSignals(True)
    count = table.rowCount()
    selected = table.selectedItems()
    selected_rows = []
    for i in range(0, len(selected)):
        selected_rows.append(selected[i].row() + 1)
    try:
        for row in reversed(list(range(0, count))):
            if table.item(row, 0).isSelected():
                selected_item = table.item(row, 0).text()
                next_item = table.item(row + 1, 0).text()
                table.item(row, 0).setText(str(next_item))
                table.item(row + 1, 0).setText(str(selected_item))
        table.clearSelection()
        values = list(set(selected_rows))
        for i in range(0, len(values)):
            table.selectRow(values[i])
    except Exception as err:
        str(err)
        table.clearSelection()
    table.blockSignals(False)
    rgb_list = read_rgb_table()
    cfg.project_registry[cfg.reg_rgb_list] = rgb_list
    cfg.util_qt.set_combobox_items(
        cfg.rgb_combo, cfg.project_registry[cfg.reg_rgb_list]
    )


# calculate all RGB composites
def calculate_all_composites_action():
    calculate_all_composites()


# all RGB List 
# noinspection PyTypeChecker
def calculate_all_composites(question=True, bandset_number=None):
    if question is True:
        answer = cfg.util_qt.question_box(
            QApplication.translate('semiautomaticclassificationplugin',
                                   'RGB composite'),
            QApplication.translate('semiautomaticclassificationplugin',
                                   'Calculate all the RGB color composites?')
        )
    else:
        answer = True
    if answer is True:
        if bandset_number is None:
            bandset_number = cfg.project_registry[
                cfg.reg_active_bandset_number
            ]
        if bandset_number > cfg.bandset_catalog.get_bandset_count():
            cfg.mx.msg_err_2()
            return False
        bandset_x = cfg.bandset_catalog.get(bandset_number)
        band_count = bandset_x.get_band_count()
        rgb_permutations = list(
            permutations(list(range(1, band_count + 1)), 3)
        )
        table = cfg.dialog.ui.RGB_tableWidget
        table.blockSignals(True)
        cfg.util_qt.clear_table(table)
        for combination in rgb_permutations:
            count = table.rowCount()
            table.setRowCount(count + 1)
            cfg.util_qt.add_table_item(
                table, '%s-%s-%s' % combination, count, 0
            )
        table.blockSignals(False)
        rgb_list = read_rgb_table()
        cfg.project_registry[cfg.reg_rgb_list] = rgb_list
        cfg.util_qt.set_combobox_items(
            cfg.rgb_combo, cfg.project_registry[cfg.reg_rgb_list]
        )


# export RGB list to file
# noinspection PyTypeChecker
def export_rgb_list():
    file = cfg.util_qt.get_save_file_name(
        None, QApplication.translate('semiautomaticclassificationplugin',
                                     'Save the RGB list to file'),
        '', '*.csv', 'csv'
    )
    if file is not False:
        if file.lower().endswith('.csv'):
            pass
        else:
            file += '.csv'
        try:
            rgb_file = open(file, 'w')
            rgb_file.write('')
            rgb_file.close()
            rgb_file = open(file, 'a')
            for composite in cfg.project_registry[cfg.reg_rgb_list]:
                if composite != '-':
                    txt = composite + '\n'
                    rgb_file.write(txt)
            rgb_file.close()
        except Exception as err:
            cfg.logger.log.error(str(err))


# import RGB from file
# noinspection PyTypeChecker
def import_rgb_list_from_file():
    file = cfg.util_qt.get_open_file(
        None, QApplication.translate('semiautomaticclassificationplugin',
                                     'Select a RGB list file'),
        '', 'CSV (*.csv)'
    )
    table = cfg.dialog.ui.RGB_tableWidget
    try:
        rgb_file = open(file)
        if cfg.utils.check_file(file):
            file = rgb_file.readlines()
            table.blockSignals(True)
            for row in range(1, len(file)):
                count = table.rowCount()
                table.setRowCount(count + 1)
                cfg.util_qt.add_table_item(table, file[row].strip(), count, 0)
            table.blockSignals(False)
            rgb_list = read_rgb_table()
            cfg.project_registry[cfg.reg_rgb_list] = rgb_list
            cfg.util_qt.set_combobox_items(
                cfg.rgb_combo, cfg.project_registry[cfg.reg_rgb_list]
            )
    except Exception as err:
        cfg.logger.log.error(str(err))
        table.blockSignals(False)
        cfg.mx.msg_err_5()
