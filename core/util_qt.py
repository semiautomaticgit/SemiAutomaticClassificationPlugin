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


from os import path

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    qApp, QWidget, QColorDialog, QFileDialog, QTableWidgetItem,
    QTableWidgetSelectionRange, QApplication, QMessageBox
)
cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# read registry keys
def read_registry_keys(key, default_value):
    setting = QSettings()
    value = setting.value(key, str(default_value))
    try:
        value = int(value)
    except Exception as err:
        str(err)
        try:
            value = eval(value)
        except Exception as err:
            str(err)
    return value


# write registry value
def write_registry_keys(key, value):
    setting = QSettings()
    setting.setValue(key, str(value))


# process events
def process_events():
    qApp.processEvents()


# Question box
# noinspection PyArgumentList
def question_box(caption, message):
    i = QWidget()
    q = QMessageBox.question(
        i, caption, message, QMessageBox.Yes,
        QMessageBox.No
    )
    if q == QMessageBox.Yes:
        return True
    elif q == QMessageBox.No:
        return False
    else:
        return False


# select color
# noinspection PyArgumentList
def select_color():
    c = QColorDialog.getColor()
    if c.isValid():
        return c


# get save file name
def get_save_file_name(
        parent, text, directory=None, filter_text=None, extension=None
):
    if directory is None:
        directory = cfg.last_saved_dir
    out = QFileDialog.getSaveFileName(
        parent, text, directory,
        filter_text
    )
    if len(out[0]) > 0:
        output = out[0].replace('\\', '/')
        output = output.replace('//', '/')
        cfg.last_saved_dir = path.dirname(output)
        if extension is not None:
            if output.lower().endswith(extension):
                return output
            else:
                output = output + '.' + extension
                return output
        else:
            return output
    else:
        return False


# get open file name
def get_open_file(parent, text, directory=None, filter_text=None):
    if directory is None:
        directory = cfg.last_saved_dir
    out = QFileDialog.getOpenFileName(
        parent, text, directory,
        filter_text
    )
    cfg.last_saved_dir = path.dirname(out[0])
    return out[0]


# get open file names
def get_open_files(parent, text, directory=None, filter_text=None):
    if directory is None:
        directory = cfg.last_saved_dir
    out = QFileDialog.getOpenFileNames(
        parent, text, directory,
        filter_text
    )
    if len(out) > 0:
        if len(out[0]) > 0:
            cfg.last_saved_dir = path.dirname(out[0][0])
    return out[0]


# get existing directory
# noinspection PyTypeChecker
def get_existing_directory(parent=None, text=None):
    if text is None:
        text = QApplication.translate(
            'semiautomaticclassificationplugin', 'Select a directory'
            )
    directory = cfg.last_saved_dir
    out = QFileDialog.getExistingDirectory(parent, text, directory)
    if len(out) > 0:
        cfg.last_saved_dir = out
        return out
    else:
        return False


# set combobox
def set_combobox_items(combobox, item_list):
    combobox.clear()
    for i in item_list:
        if len(i) > 0:
            combobox.addItem(i)


# get items in combobox
def get_all_items_in_combobox(combobox):
    it = [combobox.itemText(i) for i in range(combobox.count())]
    return it


""" table functions """


# delete all items in a table
def clear_table(table):
    table.clearContents()
    for i in range(0, table.rowCount()):
        table.removeRow(0)


# set all items to state 0 or 2
def all_items_set_state(table, value):
    table.blockSignals(True)
    rows = table.rowCount()
    for row in range(0, rows):
        table.item(row, 0).setCheckState(value)
    table.blockSignals(False)


# remove rows from table
# noinspection PyTypeChecker
def remove_rows_from_table(table):
    answer = question_box(
        QApplication.translate('semiautomaticclassificationplugin',
                               'Remove rows'),
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Are you sure you want to remove highlighted rows from the table?'
        )
    )
    if answer is True:
        table.blockSignals(True)
        # list of item to remove
        rows = []
        for index in table.selectedIndexes():
            rows.append(index.row())
        selected_rows = list(set(rows))
        # remove items
        for row in reversed(list(range(0, len(selected_rows)))):
            table.removeRow(selected_rows[row])
        table.blockSignals(False)


# select rows in table
def select_rows_in_table(table, row_list):
    count = table.columnCount()
    for row in row_list:
        table.setRangeSelected(
            QTableWidgetSelectionRange(row, 0, row, count - 1), True
        )


# add item to table
def add_table_item(
        table, item, row, column, enabled=True, color=None,
        checkbox_state=None, tooltip=None, foreground=None, bold=None
):
    item_w = QTableWidgetItem()
    if checkbox_state is not None:
        item_w.setCheckState(checkbox_state)
    if enabled is False:
        item_w.setFlags(Qt.ItemIsEnabled)
    item_w.setData(Qt.DisplayRole, item)
    table.setItem(row, column, item_w)
    if color is not None:
        table.item(row, column).setBackground(color)
    if foreground is not None:
        table.item(row, column).setForeground(foreground)
    if tooltip is not None:
        item_w.setToolTip(tooltip)
    if bold is not None:
        font = QFont()
        font.setBold(True)
        table.item(row, column).setFont(font)
    return item_w


# set table item
def set_table_item(table, row, column, value):
    table.item(row, column).setText(value)


# insert table row
def insert_table_row(table, row, height=None):
    table.insertRow(row)
    if height is not None:
        table.setRowHeight(row, height)


# insert table column
def insert_table_column(table, column, name, width=None, hide=False):
    table.insertColumn(column)
    table.setHorizontalHeaderItem(column, QTableWidgetItem(name))
    if width is not None:
        table.setColumnWidth(column, width)
    if hide is True:
        table.hideColumn(column)


# sort table column
def sort_table_column(table, column, ascending=False):
    table.sortItems(column, ascending)


# set table column width
def set_column_width_list(table, width_list):
    for value in width_list:
        table.setColumnWidth(value[0], value[1])


# set tree column width
def set_tree_column_width_list(tree, width_list):
    for value in width_list:
        tree.header().resizeSection(value[0], value[1])


def get_color_from_rgb(red, green, blue):
    return QColor(red, green, blue)


def get_color_from_text(text):
    return QColor(text)


def get_match_contains():
    return Qt.MatchContains


def get_unchecked():
    return Qt.Unchecked


def get_checked():
    return Qt.Checked
