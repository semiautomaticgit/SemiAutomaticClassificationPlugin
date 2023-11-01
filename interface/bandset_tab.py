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
"""Band set.

This tool allows for band set definition.
"""

import numpy
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QFrame, QAbstractItemView, QTableWidget,
    QTableWidgetItem, QListWidgetItem
)

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# add satellite list to combo
def add_satellite_to_combo(satellite_list):
    for i in satellite_list:
        cfg.dialog.ui.wavelength_sat_combo.addItem(i)


# add unit list to combo
def add_unit_to_combo(unit_list):
    for i in unit_list:
        cfg.dialog.ui.unit_combo.addItem(i)


def satellite_wavelength():
    set_satellite_wavelength()


# set satellite wavelengths
def set_satellite_wavelength(satellite_name=None, bandset_number=None):
    cfg.logger.log.debug(
        'set_satellite_wavelength satellite_name: %s'
        % str(satellite_name)
    )
    if satellite_name is None:
        satellite_name = cfg.dialog.ui.wavelength_sat_combo.currentText()
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    cfg.bandset_catalog.set_satellite_wavelength(
        satellite_name=satellite_name, bandset_number=bandset_number
    )
    # create table
    band_set_to_table(bandset_number)


def satellite_unit():
    set_band_unit()


# set band unit
def set_band_unit(unit_name=None, bandset_number=None):
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    bands = bandset_x.bands
    if unit_name is None:
        unit_name = cfg.dialog.ui.unit_combo.currentText()
    for band in bands:
        band['wavelength_unit'] = unit_name
    # create table
    band_set_to_table(bandset_number)


# set date
def set_bandset_date():
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    q_date = cfg.dialog.ui.bandset_dateEdit.date()
    date = q_date.toPyDate().strftime('%Y-%m-%d')
    cfg.bandset_catalog.set_date(bandset_number=bandset_number, date=date)
    cfg.dialog.ui.bandset_date_lineEdit.setText(date)


# edit date
def edit_bandset_date():
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    date = cfg.dialog.ui.bandset_date_lineEdit.text()
    if len(date) > 0:
        try:
            date = numpy.array(date, dtype='datetime64[D]')
        except Exception as err:
            str(err)
            date = 'NaT'
    cfg.bandset_catalog.set_date(bandset_number=bandset_number, date=date)
    cfg.dialog.ui.bandset_date_lineEdit.blockSignals(True)
    cfg.dialog.ui.bandset_date_lineEdit.setText(str(date))
    cfg.dialog.ui.bandset_date_lineEdit.blockSignals(False)


# edit root directory
def edit_bandset_root():
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    root = cfg.dialog.ui.root_dir_lineEdit.text()
    cfg.bandset_catalog.set_root_directory(
        bandset_number=bandset_number, root_directory=root
    )
    band_set_to_table(bandset_number)


# add file to band set action
def add_file_to_band_set_action():
    files = cfg.util_qt.get_open_files(
        None, cfg.translate('Select input raster'), '', 'Raster (*.*)'
    )
    add_file_to_band_set(files)


# add file to band set action
def set_custom_wavelength_action():
    file = cfg.util_qt.get_open_file(
        None, cfg.translate('Select csv file'), '',
        'TXT file (*.txt);;CSV file (*.csv)'
    )
    if len(file) > 0:
        with open(file, 'r') as f:
            text = f.read()
        if len(text) > 0:
            values = text.split(',')
            if len(values) == 1:
                values = text.split(';')
                if len(values) == 1:
                    values = text.split('\n')
                    if len(values) == 1:
                        return
            bandset_number = cfg.project_registry[
                cfg.reg_active_bandset_number
            ]
            cfg.bandset_catalog.set_wavelength(
                wavelength_list=values, unit=cfg.rs.configurations.wl_micro,
                bandset_number=bandset_number
            )
            # create table
            band_set_to_table(bandset_number)


# change band set tab action
def change_bandset_table_action(index):
    # change spinbox value (tabs are connected)
    cfg.dialog.ui.bandset_number_spinBox.setValue(int(index.row()) + 1)


# change band set tab action
def change_bandset_tab_action():
    change_bandset_tab()


# add band set tab
def add_bandset_tab_action():
    add_band_set_tab()


# add band set tab
def add_band_set_tab(position=None, create_bandset_in_catalog=True):
    cfg.logger.log.debug('add_band_set_tab position: %s' % str(position))
    if len(cfg.bandset_tabs) == 0:
        position = 1
    elif position is None or int(position) > (len(cfg.bandset_tabs)):
        position = len(cfg.bandset_tabs) + 1
        if create_bandset_in_catalog:
            # create bandset
            bandset = cfg.rs.bandset.create(catalog=cfg.bandset_catalog)
            cfg.bandset_catalog.add_bandset(
                bandset=bandset, bandset_number=position, insert=True
            )
    try:
        assert cfg.bandset_tabs[position]
        cfg.logger.log.debug('existing bandset tab')
        return
    except Exception as err:
        str(err)
    cfg.bandset_tabs[position] = bandset_uid()
    table_w_var = 'cfg.dialog.ui.tableWidget__' + str(
        cfg.bandset_tabs[position]
    )
    cfg.dialog.ui.bandset_number_spinBox.setMaximum(position)
    # noinspection PyArgumentList
    band_set_tab = QWidget()
    band_set_tab.setObjectName(table_w_var)
    grid_layout = QGridLayout(band_set_tab)
    grid_layout.setObjectName('grid_layout' + str(position))
    exec(table_w_var + ' = QTableWidget(band_set_tab)')
    table_w = eval(table_w_var)
    table_w.setFrameShape(QFrame.WinPanel)
    table_w.setFrameShadow(QFrame.Sunken)
    table_w.setAlternatingRowColors(True)
    table_w.setSelectionMode(QAbstractItemView.MultiSelection)
    table_w.setSelectionBehavior(QAbstractItemView.SelectRows)
    table_w.setColumnCount(7)
    table_w.setObjectName(table_w_var)
    table_w.setRowCount(0)
    table_w.setHorizontalHeaderItem(0, QTableWidgetItem())
    table_w.setHorizontalHeaderItem(1, QTableWidgetItem())
    table_w.setHorizontalHeaderItem(2, QTableWidgetItem())
    table_w.setHorizontalHeaderItem(3, QTableWidgetItem())
    table_w.setHorizontalHeaderItem(4, QTableWidgetItem())
    table_w.setHorizontalHeaderItem(5, QTableWidgetItem())
    table_w.setHorizontalHeaderItem(6, QTableWidgetItem())
    table_w.horizontalHeaderItem(0).setText(cfg.translate('Band name'))
    table_w.horizontalHeaderItem(1).setText(cfg.translate('Center wavelength'))
    table_w.horizontalHeaderItem(2).setText(
        cfg.translate('Multiplicative Factor')
    )
    table_w.horizontalHeaderItem(3).setText(cfg.translate('Additive Factor'))
    table_w.horizontalHeaderItem(4).setText(cfg.translate('Wavelength unit'))
    table_w.horizontalHeaderItem(5).setText(cfg.translate('Path'))
    table_w.horizontalHeaderItem(6).setText(cfg.translate('Date'))
    table_w.verticalHeader().setDefaultSectionSize(24)
    table_w.horizontalHeader().setStretchLastSection(True)
    grid_layout.addWidget(table_w, 0, 0, 1, 1)
    # connect to edited cell
    try:
        table_w.cellChanged.disconnect()
    except Exception as err:
        str(err)
    table_w.cellChanged.connect(edited_bandset)
    cfg.dialog.ui.Band_set_tabWidget.insertTab(
        int(position) - 1, band_set_tab,
        '%s %s' % (cfg.bandset_tab_name, str(position))
    )
    cfg.util_qt.set_column_width_list(
        table_w, [[0, 350], [1, 150], [2, 150], [3, 150], [4, 150], [5, 150]]
    )
    # hide tabs
    cfg.dialog.ui.Band_set_tabWidget.setStyleSheet(
        'QTabBar::tab {padding: 0px; max-height: 0px;}'
    )
    cfg.dialog.ui.bandset_tableWidget.setRowCount(position)
    cfg.util_qt.add_table_item(
        cfg.dialog.ui.bandset_tableWidget, '', int(position) - 1, 0
    )
    # change spinbox value (tabs are connected)
    cfg.dialog.ui.bandset_number_spinBox.setValue(position)
    cfg.project_registry[cfg.reg_bandset_count] = (
        cfg.bandset_catalog.get_bandset_count())
    cfg.logger.log.debug(
        'bandset_count: %s; table count: %s; current index: %s'
        % (str(cfg.project_registry[cfg.reg_bandset_count]),
           str(cfg.dialog.ui.Band_set_tabWidget.count()),
           str(cfg.dialog.ui.Band_set_tabWidget.currentIndex())
           )
    )


# add loaded band to current band set
def add_loaded_band_to_bandset():
    cfg.logger.log.info('add_loaded_band_to_bandset')
    # clear the list
    cfg.widget_dialog.ui.listWidget.clear()
    # add raster list
    # noinspection PyArgumentList
    layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
    layer_path_list = []
    for layer in sorted(layers, key=lambda c: c.name()):
        if ((layer.type() == cfg.util_qgis.get_qgis_map_raster())
                and layer.bandCount() == 1):
            item = QListWidgetItem()
            item.setCheckState(cfg.util_qt.get_unchecked())
            item.setText(layer.name())
            layer_path_list.append(layer.source().split("|layername=")[0])
            cfg.widget_dialog.ui.listWidget.addItem(item)
    cfg.dialog_accepted = False
    cfg.widget_dialog.exec()
    if cfg.dialog_accepted is True:
        checked_files = []
        for index in range(cfg.widget_dialog.ui.listWidget.count()):
            if (cfg.widget_dialog.ui.listWidget.item(index).checkState()
                    == cfg.util_qt.get_checked()):
                checked_files.append(layer_path_list[index])
        add_file_to_band_set(checked_files)


# clear the band set
def clear_bandset_action():
    clear_bandset()


# clear the bandset
def clear_bandset(question=True, bandset_number=None):
    if question:
        answer = cfg.util_qt.question_box(
            cfg.translate('Clear band set'),
            cfg.translate('Are you sure you want to clear the band set?')
        )
    else:
        answer = True
    if answer:
        if bandset_number is None:
            bandset_number = (cfg.dialog.ui.Band_set_tabWidget.currentIndex()
                              + 1)
        cfg.logger.log.debug('clear_bandset: %s' % str(bandset_number))
        cfg.bandset_catalog.clear_bandset(bandset_number)
        # create table
        band_set_to_table(bandset_number)


# band set edited
def edited_bandset(row, column):
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    table_w = eval(
        'cfg.dialog.ui.tableWidget__' + str(cfg.bandset_tabs[bandset_number])
    )
    cfg.logger.log.debug('edited_bandset column: %s' % str(column))
    if column == 0:
        band_names = cfg.bandset_catalog.get_bandset(
            bandset_number, attribute='name'
        )
        table_w.blockSignals(True)
        cfg.util_qt.set_table_item(table_w, row, column, str(band_names[row]))
        table_w.blockSignals(False)
    elif column == 1:
        try:
            value = float(table_w.item(row, column).text())
            bandset_x = cfg.bandset_catalog.get_bandset_by_number(
                bandset_number
            )
            bands = bandset_x.bands
            bands['wavelength'][bands['band_number'] == row + 1] = value
            bandset_x.sort_bands_by_wavelength()
            # create table
            band_set_to_table(bandset_number)
        except Exception as err:
            str(err)
            band_wavelength = cfg.bandset_catalog.get_bandset(
                bandset_number, attribute='wavelength'
            )
            value = band_wavelength[row]
            table_w.blockSignals(True)
            cfg.util_qt.set_table_item(table_w, row, column, str(value))
            table_w.blockSignals(False)
    elif column == 2:
        try:
            value = float(table_w.item(row, column).text())
            bandset_x = cfg.bandset_catalog.get_bandset_by_number(
                bandset_number
            )
            bands = bandset_x.bands
            bands['multiplicative_factor'][
                bands['band_number'] == row + 1] = value
        except Exception as err:
            str(err)
            band_value = cfg.bandset_catalog.get_bandset(
                bandset_number, attribute='multiplicative_factor'
            )
            value = band_value[row]
            table_w.blockSignals(True)
            cfg.util_qt.set_table_item(table_w, row, column, str(value))
            table_w.blockSignals(False)
    elif column == 3:
        try:
            value = float(table_w.item(row, column).text())
            bandset_x = cfg.bandset_catalog.get_bandset_by_number(
                bandset_number
            )
            bands = bandset_x.bands
            bands['additive_factor'][bands['band_number'] == row + 1] = value
        except Exception as err:
            str(err)
            band_value = cfg.bandset_catalog.get_bandset(
                bandset_number, attribute='additive_factor'
            )
            value = band_value[row]
            table_w.blockSignals(True)
            cfg.util_qt.set_table_item(table_w, row, column, str(value))
            table_w.blockSignals(False)
    elif column == 4:
        band_value = cfg.bandset_catalog.get_bandset(
            bandset_number, attribute='wavelength_unit'
        )
        table_w.blockSignals(True)
        cfg.util_qt.set_table_item(table_w, row, column, str(band_value[row]))
        table_w.blockSignals(False)
    elif column == 5:
        path = table_w.item(row, column).text()
        if len(path) > 0:
            bandset_x = cfg.bandset_catalog.get_bandset_by_number(
                bandset_number
            )
            bands = bandset_x.bands
            bands['path'][bands['band_number'] == row + 1] = path
        else:
            band_value = cfg.bandset_catalog.get_bandset(
                bandset_number, attribute='path'
            )
            value = band_value[row]
            table_w.blockSignals(True)
            cfg.util_qt.set_table_item(table_w, row, column, str(value))
            table_w.blockSignals(False)
    elif column == 6:
        try:
            value = table_w.item(row, column).text()
            if len(value) > 0:
                numpy.array(value, dtype='datetime64[D]')
                bandset_x = cfg.bandset_catalog.get_bandset_by_number(
                    bandset_number
                )
                bands = bandset_x.bands
                bands['date'][bands['band_number'] == row + 1] = value
            band_value = cfg.bandset_catalog.get_bandset(
                bandset_number, attribute='date'
            )
            value = band_value[row]
            if value is None:
                value = 'NaT'
            table_w.blockSignals(True)
            cfg.util_qt.set_table_item(table_w, row, column, str(value))
            table_w.blockSignals(False)
        except Exception as err:
            str(err)
            band_value = cfg.bandset_catalog.get_bandset(
                bandset_number, attribute='date'
            )
            value = band_value[row]
            if value is None:
                value = 'NaT'
            table_w.blockSignals(True)
            cfg.util_qt.set_table_item(table_w, row, column, str(value))
            table_w.blockSignals(False)


# delete bandset
def remove_bandsets():
    answer = cfg.util_qt.question_box(
        cfg.translate('Remove band set'),
        cfg.translate(
            'Are you sure you want to remove the selected band sets?'
        )
    )
    if answer:
        table = cfg.dialog.ui.bandset_tableWidget
        selected = table.selectedItems()
        selected_list = []
        for i in range(0, len(selected)):
            selected_list.append(selected[i].row())
        selected_list = list(set(selected_list))
        for index in reversed(selected_list):
            delete_bandset_tab(index)


# delete bandset
def delete_bandset_tab(index):
    table = cfg.dialog.ui.bandset_tableWidget
    count = cfg.dialog.ui.Band_set_tabWidget.count()
    cfg.logger.log.debug('delete_bandset_tab: %s' % str(index + 1))
    for position in range(index, count - 1):
        try:
            cfg.bandset_tabs[position + 1] = cfg.bandset_tabs[position + 2]
        except Exception as err:
            cfg.mx.msg_bar_critical(
                title='bandset', message=str(err), smtp=False
            )
            cfg.logger.log.error(str(err))
    cfg.bandset_tabs.pop(count, None)
    bandset = cfg.bandset_catalog.get_bandset(index + 1)
    if bandset is not None:
        cfg.bandset_catalog.remove_bandset(index + 1)
    cfg.logger.log.debug(
        'bandset_count: %s' % str(
            cfg.bandset_catalog.get_bandset_count()
        )
    )
    cfg.dialog.ui.Band_set_tabWidget.removeTab(index)
    cfg.dialog.ui.bandset_number_spinBox.setMaximum(count)
    table.removeRow(index)


# export bandset to file
def export_bandset():
    xml_file = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Save the bandset to file'), '', '*.xml', 'xml'
    )
    if xml_file is not False:
        cfg.logger.log.info('export_bandset: %s' % xml_file)
        if not xml_file.lower().endswith('.xml'):
            xml_file = xml_file + '.xml'
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
        cfg.bandset_catalog.export_bandset_as_xml(
            bandset_number=bandset_number, output_path=xml_file
        )


# import bandset from file
def import_bandset():
    xml_file = cfg.util_qt.get_open_file(
        None, cfg.translate('Select a bandset file'), '', 'XML (*.xml)'
    )
    if len(xml_file) > 0:
        cfg.logger.log.info('import_bandset: %s' % xml_file)
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
        try:
            cfg.bandset_catalog.import_bandset_from_xml(
                bandset_number=bandset_number, xml_path=xml_file
            )
            # create table
            band_set_to_table(bandset_number)
        except Exception as err:
            cfg.logger.log.error(str(err))
            cfg.mx.msg_err_5()


# move down selected bandset
def move_down_bandset():
    table = cfg.dialog.ui.bandset_tableWidget
    selected = table.selectedItems()
    selected_list = []
    for i in range(0, len(selected)):
        selected_list.append(selected[i].row())
    selected_list = list(set(selected_list))
    if (table.rowCount() - 1) not in selected_list:
        for index in reversed(selected_list):
            cfg.bandset_catalog.move_bandset(
                bandset_number_input=index + 1, bandset_number_output=index + 2
            )
            bandset_1 = cfg.bandset_catalog.get_bandset_by_number(index + 1)
            bandset_2 = cfg.bandset_catalog.get_bandset_by_number(index + 2)
            # band sets table
            table.blockSignals(True)
            names = str(bandset_1.get_band_attributes('name')).replace(
                "'", ''
            ).replace(
                '[', ''
            ).replace(']', '')
            if names == 'None':
                names = ''
            cfg.util_qt.add_table_item(table, str(names), int(index), 0)
            names = str(bandset_2.get_band_attributes('name')).replace(
                "'", ''
            ).replace(
                '[', ''
            ).replace(']', '')
            if names == 'None':
                names = ''
            cfg.util_qt.add_table_item(table, str(names), int(index) + 1, 0)
            table.blockSignals(False)
            # create table
            band_set_to_table(index + 1)
            band_set_to_table(index + 2)
        table.clearSelection()
        table.setSelectionMode(QAbstractItemView.MultiSelection)
        for i in selected_list:
            table.selectRow(i + 1)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)


# move up selected bandset
def move_up_bandset():
    table = cfg.dialog.ui.bandset_tableWidget
    selected = table.selectedItems()
    selected_list = []
    for i in range(0, len(selected)):
        selected_list.append(selected[i].row())
    selected_list = list(set(selected_list))
    if 0 not in selected_list:
        for index in selected_list:
            cfg.bandset_catalog.move_bandset(
                bandset_number_input=index + 1, bandset_number_output=index
            )
            bandset_1 = cfg.bandset_catalog.get_bandset_by_number(index + 1)
            bandset_2 = cfg.bandset_catalog.get_bandset_by_number(index)
            # band sets table
            table.blockSignals(True)
            names = str(bandset_1.get_band_attributes('name')).replace(
                "'", ''
            ).replace(
                '[', ''
            ).replace(']', '')
            if names == 'None':
                names = ''
            cfg.util_qt.add_table_item(table, str(names), int(index), 0)
            names = str(bandset_2.get_band_attributes('name')).replace(
                "'", ''
            ).replace(
                '[', ''
            ).replace(']', '')
            if names == 'None':
                names = ''
            cfg.util_qt.add_table_item(table, str(names), int(index) - 1, 0)
            table.blockSignals(False)
            # create table
            band_set_to_table(index + 1)
            band_set_to_table(index)
        table.clearSelection()
        table.setSelectionMode(QAbstractItemView.MultiSelection)
        for i in selected_list:
            table.selectRow(i - 1)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)


# move down selected band
def move_down_band():
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    table = eval(
        'cfg.dialog.ui.tableWidget__' + str(cfg.bandset_tabs[bandset_number])
    )
    selected = table.selectedItems()
    selected_list = []
    for i in range(0, len(selected)):
        selected_list.append(selected[i].row())
    selected_list = list(set(selected_list))
    if (table.rowCount() - 1) not in selected_list:
        for index in reversed(selected_list):
            cfg.bandset_catalog.move_band_in_bandset(
                bandset_number=bandset_number,
                band_number_input=index + 1, band_number_output=index + 2
            )
        # create table
        band_set_to_table(bandset_number)
        for i in selected_list:
            table.selectRow(i + 1)


# move up selected band
def move_up_band():
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    table = eval(
        'cfg.dialog.ui.tableWidget__' + str(cfg.bandset_tabs[bandset_number])
    )
    selected = table.selectedItems()
    selected_list = []
    for i in range(0, len(selected)):
        selected_list.append(selected[i].row())
    selected_list = list(set(selected_list))
    if 0 not in selected_list:
        for index in selected_list:
            cfg.bandset_catalog.move_band_in_bandset(
                bandset_number=bandset_number, band_number_input=index + 1,
                band_number_output=index
            )
        # create table
        band_set_to_table(bandset_number)
        for i in selected_list:
            table.selectRow(i - 1)


# sort bands by name
def sort_bands_by_name():
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    try:
        cfg.bandset_catalog.sort_bands_by_name(bandset_number=bandset_number)
    except Exception as err:
        str(err)
    # create table
    band_set_to_table(bandset_number)


# remove selected band
def remove_band():
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    table_w = eval(
        'cfg.dialog.ui.tableWidget__' + str(cfg.bandset_tabs[bandset_number])
    )
    answer = cfg.util_qt.question_box(
        cfg.translate('Remove band'),
        cfg.translate(
            'Are you sure you want to remove the selected bands from band set?'
        )
    )
    if answer:
        selected_list = []
        for i in table_w.selectedItems():
            selected_list.append(i.row() + 1)
        selected_list = list(set(selected_list))
        for r in reversed(selected_list):
            cfg.bandset_catalog.remove_band_in_bandset(
                bandset_number=bandset_number, band_number=r
            )
        # create table
        band_set_to_table(bandset_number)


# sort bandsets by date
def sort_bandsets_by_date():
    cfg.bandset_catalog.sort_bandsets_by_date()
    for bandset_number in range(
            1, cfg.bandset_catalog.get_bandset_count() + 1
    ):
        # create table
        band_set_to_table(bandset_number)


""" Tools """


# create virtual raster
def virtual_raster_bandset(output_path=None, bandset_number=None):
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    if output_path is None:
        vrt_file = cfg.util_qt.get_save_file_name(
            None, cfg.translate(
                'Save virtual raster'
            ), '', '*.vrt', 'vrt'
        )
    else:
        vrt_file = output_path
    if vrt_file is not False:
        if not vrt_file.lower().endswith('.vrt'):
            vrt_file += '.vrt'
        try:
            cfg.bandset_catalog.create_virtual_raster(
                bandset_number=bandset_number, output_path=vrt_file
            )
        except Exception as err:
            cfg.mx.msg_err_5()
            cfg.logger.log.error(str(err))
        return vrt_file


# stack bandset
def stack_bandset(output_path=None, bandset_number=None):
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    if output_path is None:
        tif_file = cfg.util_qt.get_save_file_name(
            None, cfg.translate('Save raster'), '', '*.tif', 'tif'
        )
    else:
        tif_file = output_path
    if tif_file is not False:
        if not tif_file.lower().endswith('.tif'):
            tif_file += '.tif'
        try:
            cfg.bandset_catalog.create_bandset_stack(
                bandset_number=bandset_number, output_path=tif_file
            )
        except Exception as err:
            cfg.mx.msg_err_5()
            cfg.logger.log.error(str(err))
        return tif_file


# button perform bandset tools
def perform_bandset_tools():
    if (cfg.dialog.ui.overview_raster_bandset_checkBox.isChecked() is False
            and cfg.dialog.ui.band_calc_checkBox.isChecked() is False
            and cfg.dialog.ui.stack_raster_bandset_checkBox.isChecked() is
            False
            and cfg.dialog.ui.virtual_raster_bandset_checkBox.isChecked() is
            False):
        cfg.mx.msg_war_8()
    elif (cfg.dialog.ui.overview_raster_bandset_checkBox.isChecked() is True
          and cfg.dialog.ui.band_calc_checkBox.isChecked() is False
          and cfg.dialog.ui.stack_raster_bandset_checkBox.isChecked() is False
          and cfg.dialog.ui.virtual_raster_bandset_checkBox.isChecked() is
          False):
        # build overview
        cfg.bandset_catalog.build_bandset_band_overview(
            bandset_number=cfg.project_registry[cfg.reg_active_bandset_number]
        )
    else:
        directory = cfg.util_qt.get_existing_directory(
            None, cfg.translate('Select a directory')
        )
        if directory is not False:
            cfg.ui_utils.add_progress_bar()
            bandset_tools(directory, batch=False)
            cfg.ui_utils.remove_progress_bar()


# perform bandset tools
def bandset_tools(output_directory, bandset_number=None, batch=True):
    if batch is False:
        cfg.ui_utils.add_progress_bar()
    cfg.logger.log.info('bandset_tools: %s' % output_directory)
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    name = cfg.bandset_catalog.get_name(bandset_number)
    if cfg.rs.configurations.action:
        if cfg.dialog.ui.band_calc_checkBox.isChecked() is True:
            cfg.band_calc.raster_band_table()
            cfg.band_calc.calculate(output_directory)
    if cfg.rs.configurations.action:
        if cfg.dialog.ui.virtual_raster_bandset_checkBox.isChecked() is True:
            virtual_raster_bandset(
                ''.join(
                    [output_directory, '/', name, '_', 'virtual_rast',
                     '.vrt']
                )
            )
    if cfg.rs.configurations.action:
        if cfg.dialog.ui.stack_raster_bandset_checkBox.isChecked() is True:
            stack_bandset(
                ''.join(
                    [output_directory, '/', name, '_', 'stack_raster',
                     '.tif']
                )
            )
    if cfg.rs.configurations.action:
        if cfg.dialog.ui.overview_raster_bandset_checkBox.isChecked() is True:
            # build overview
            cfg.bandset_catalog.build_bandset_band_overview(
                bandset_number=cfg.project_registry[
                    cfg.reg_active_bandset_number]
            )
    if batch is False:
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))
        cfg.mx.msg_inf_6()


# perform bands filter
def filter_table():
    text = cfg.dialog.ui.band_set_filter_lineEdit.text()
    items = cfg.dialog.ui.bandset_tableWidget.findItems(
        text, cfg.util_qt.get_match_contains()
    )
    c = cfg.dialog.ui.bandset_tableWidget.rowCount()
    rows = []
    for item in items:
        rows.append(item.row())
    cfg.dialog.ui.bandset_tableWidget.blockSignals(True)
    for i in range(0, c):
        cfg.dialog.ui.bandset_tableWidget.setRowHidden(i, False)
        if i not in rows:
            cfg.dialog.ui.bandset_tableWidget.setRowHidden(i, True)
    cfg.dialog.ui.bandset_tableWidget.blockSignals(False)


# band set to table
def band_set_to_table(bandset_number):
    cfg.logger.log.debug(
        'band_set_to_table bandset_number: %s' % str(bandset_number)
    )
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    # add table without adding bandset in catalog
    if bandset_number not in cfg.bandset_tabs:
        add_band_set_tab(
            position=bandset_number, create_bandset_in_catalog=False
        )
    table_w = eval(
        'cfg.dialog.ui.tableWidget__' + str(cfg.bandset_tabs[bandset_number])
    )
    bands = bandset_x.bands
    cfg.logger.log.debug('band_count: %s' % str(bandset_x.get_band_count()))
    if bands is not None:
        bands.sort(order='band_number')
        # create table
        table_w.blockSignals(True)
        cfg.util_qt.clear_table(table_w)
        table_w.setRowCount(bandset_x.get_band_count())
        for band in bands:
            # table rows
            c = band['band_number'] - 1
            cfg.logger.log.debug('band name: %s' % str(band['name']))
            cfg.util_qt.add_table_item(table_w, str(band['name']), c, 0)
            cfg.util_qt.add_table_item(table_w, str(band['wavelength']), c, 1)
            cfg.util_qt.add_table_item(
                table_w, str(band['multiplicative_factor']), c, 2
            )
            cfg.util_qt.add_table_item(
                table_w, str(band['additive_factor']), c, 3
            )
            cfg.util_qt.add_table_item(
                table_w, str(band['wavelength_unit']), c, 4
            )
            cfg.util_qt.add_table_item(table_w, str(band['path']), c, 5)
            cfg.util_qt.add_table_item(table_w, str(band['date']), c, 6)
        table_w.blockSignals(False)
        # band sets table
        cfg.dialog.ui.bandset_tableWidget.blockSignals(True)
        names = str(bandset_x.get_band_attributes('name')).replace(
            "'", ''
        ).replace('[', '').replace(']', '')
        if names == 'None':
            names = ''
        cfg.util_qt.add_table_item(
            cfg.dialog.ui.bandset_tableWidget, str(names),
            int(bandset_number) - 1, 0
        )
        cfg.dialog.ui.bandset_tableWidget.blockSignals(False)
        if bandset_number == (
                cfg.dialog.ui.Band_set_tabWidget.currentIndex() + 1):
            # set date
            date = cfg.bandset_catalog.get_date(bandset_number)
            if len(date) > 0:
                try:
                    numpy.array(date, dtype='datetime64[D]')
                except Exception as err:
                    str(err)
                    date = 'NaT'
            cfg.dialog.ui.bandset_date_lineEdit.blockSignals(True)
            cfg.dialog.ui.bandset_date_lineEdit.setText(date)
            cfg.dialog.ui.bandset_date_lineEdit.blockSignals(False)
            # set root directory
            root = cfg.bandset_catalog.get_root_directory(bandset_number)
            if root is None or root == 'None':
                root = ''
            cfg.dialog.ui.root_dir_lineEdit.blockSignals(True)
            cfg.dialog.ui.root_dir_lineEdit.setText(root)
            cfg.dialog.ui.root_dir_lineEdit.blockSignals(False)
    else:
        table_w.blockSignals(True)
        cfg.util_qt.clear_table(table_w)
        table_w.blockSignals(True)
        # band sets table
        cfg.dialog.ui.bandset_tableWidget.blockSignals(True)
        cfg.util_qt.add_table_item(
            cfg.dialog.ui.bandset_tableWidget, '', int(bandset_number) - 1, 0
        )
        cfg.dialog.ui.bandset_tableWidget.blockSignals(False)
        if bandset_number == (
                cfg.dialog.ui.Band_set_tabWidget.currentIndex() + 1):
            # set date
            date = 'NaT'
            cfg.dialog.ui.bandset_date_lineEdit.blockSignals(True)
            cfg.dialog.ui.bandset_date_lineEdit.setText(date)
            cfg.dialog.ui.bandset_date_lineEdit.blockSignals(False)
            # set root directory
            root = ''
            cfg.dialog.ui.root_dir_lineEdit.blockSignals(True)
            cfg.dialog.ui.root_dir_lineEdit.setText(root)
            cfg.dialog.ui.root_dir_lineEdit.blockSignals(False)


# change band set tab
def change_bandset_tab(bandset_number=None):
    if bandset_number is None:
        bandset_number = cfg.dialog.ui.bandset_number_spinBox.value()
    cfg.project_registry[cfg.reg_active_bandset_number] = bandset_number
    cfg.dialog.ui.Band_set_tabWidget.setCurrentIndex(bandset_number - 1)
    cfg.dialog.ui.bandset_date_lineEdit.blockSignals(True)
    cfg.dialog.ui.wavelength_sat_combo.blockSignals(True)
    cfg.dialog.ui.wavelength_sat_combo.setCurrentIndex(0)
    cfg.dialog.ui.wavelength_sat_combo.blockSignals(False)
    cfg.dialog.ui.bandset_date_lineEdit.blockSignals(False)
    # set date
    date = cfg.bandset_catalog.get_date(bandset_number)
    if len(date) > 0:
        try:
            numpy.array(date, dtype='datetime64[D]')
        except Exception as err:
            str(err)
            date = 'NaT'
    cfg.dialog.ui.bandset_date_lineEdit.blockSignals(True)
    cfg.dialog.ui.bandset_date_lineEdit.setText(date)
    cfg.dialog.ui.bandset_date_lineEdit.blockSignals(False)
    # set root directory
    root = cfg.bandset_catalog.get_root_directory(bandset_number)
    if root is None or root == 'None':
        root = ''
    cfg.dialog.ui.root_dir_lineEdit.blockSignals(True)
    cfg.dialog.ui.root_dir_lineEdit.setText(root)
    cfg.dialog.ui.root_dir_lineEdit.blockSignals(False)


# add files to band set
def add_file_to_band_set(files):
    if len(files) > 0:
        cfg.logger.log.debug('add_file_to_band_set files: %s' % str(files))
        cfg.rs.configurations.action = True
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
        unit = cfg.dialog.ui.unit_combo.currentText()
        satellite = cfg.dialog.ui.wavelength_sat_combo.currentText()
        root_directory = cfg.dialog.ui.root_dir_lineEdit.text()
        if len(root_directory) == 0:
            root_directory = None
        if root_directory is not None:
            temp_files = []
            for f in files:
                temp_files.append(
                    cfg.utils.absolute_to_relative(f, root_directory)
                )
            files = temp_files
        if satellite == cfg.rs.configurations.no_satellite:
            wavelengths = None
        else:
            wavelengths = [satellite]
            unit = None
        # check empty bandset
        bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
        cfg.logger.log.debug('bandset_x: %s' % str(bandset_x))
        if bandset_x is None:
            # create bandset
            cfg.bandset_catalog.create_bandset(
                paths=files, bandset_number=bandset_number, insert=False,
                unit=unit, root_directory=root_directory,
                wavelengths=wavelengths
            )
        else:
            bands = bandset_x.bands
            if bands is None or bands.shape[0] == 0:
                try:
                    # create bandset
                    cfg.bandset_catalog.create_bandset(
                        paths=files, bandset_number=bandset_number,
                        insert=False, unit=unit, root_directory=root_directory,
                        wavelengths=wavelengths
                    )
                except Exception as err:
                    cfg.mx.msg_err_5()
                    cfg.logger.log.error(str(err))
            else:
                for file in files:
                    cfg.bandset_catalog.add_band_to_bandset(
                        path=file, bandset_number=bandset_number,
                        raster_band=1, root_directory=root_directory
                    )
        # create table
        band_set_to_table(bandset_number)


def bandset_uid():
    times = cfg.utils.get_time()
    random_int = str(cfg.utils.random_integer(0, 1000))
    uid = '{}_{}'.format(times, random_int)
    return uid


# check accepted dialog
def check_accepted():
    cfg.dialog_accepted = True


# select all
def select_all_bands():
    if cfg.widget_dialog.ui.listWidget.count() > 0:
        if (cfg.widget_dialog.ui.listWidget.item(0).checkState()
                == cfg.util_qt.get_checked()):
            state = cfg.util_qt.get_unchecked()
        else:
            state = cfg.util_qt.get_checked()
        for index in range(cfg.widget_dialog.ui.listWidget.count()):
            if (cfg.widget_dialog.ui.listWidget.item(0).checkState()
                    == cfg.util_qt.get_checked()):
                cfg.widget_dialog.ui.listWidget.item(index).setCheckState(
                    state
                )
            else:
                cfg.widget_dialog.ui.listWidget.item(index).setCheckState(
                    state
                )


# function to explain import QTableWidget
def explain_q_table_widget():
    assert QTableWidget


# add color composite
def add_composite():
    table = cfg.dialog.ui.bandset_tableWidget
    selected = table.selectedItems()
    selected_list = []
    for i in range(0, len(selected)):
        selected_list.append(selected[i].row())
    selected_list = list(set(selected_list))
    for index in reversed(selected_list):
        cfg.utils.set_rgb_color_composite(
            composite='3-2-1', bandset_number=index + 1
        )
