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
"""Image conversion.

This tool allows for the conversion of images to reflectance such as Landsat
and Sentinel-2.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# landsat input
def input_image():
    path = cfg.util_qt.get_existing_directory(
        None, cfg.translate('Select a directory')
    )
    if path is False:
        cfg.dialog.ui.label_26.setText('')
        cfg.util_qt.clear_table(cfg.dialog.ui.bands_tableWidget)
        return
    cfg.dialog.ui.label_26.setText(str(path))
    # metadata
    cfg.dialog.ui.label_27.setText('')
    populate_table(input_path=path)


# metadata input
def input_metadata():
    metadata = cfg.util_qt.get_open_file(
        None, cfg.translate('Select a MTL file'), '',
        'MTL file .txt (*.txt);;MTL file .met (*.met);;MTD file .xml (*.xml)'
    )
    cfg.dialog.ui.label_27.setText(str(metadata))
    if len(cfg.dialog.ui.label_26.text()) > 0:
        populate_table(
            input_path=cfg.dialog.ui.label_26.text(),
            metadata_file_path=metadata
        )


# populate table
def populate_table(input_path, metadata_file_path=None):
    cfg.logger.log.info(
        'populate_table input_path: %s; metadata_file_path: %s'
        % (input_path, str(metadata_file_path))
    )
    cfg.preprocess_band_table = None
    if cfg.dialog.ui.nodata_checkBox_2.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_3.value()
    else:
        nodata = None
    cfg.preprocess_band_table = (
        cfg.rs.preprocess_products.create_product_table(
            input_path=input_path, nodata_value=nodata,
            metadata_file_path=metadata_file_path
        ))
    table = cfg.dialog.ui.bands_tableWidget
    cfg.util_qt.set_column_width_list(
        table, [[0, 150], [1, 150], [2, 150],
                [3, 350], [4, 450]]
    )
    cfg.util_qt.clear_table(table)
    table.blockSignals(True)
    table.setSortingEnabled(False)
    total_bands = cfg.preprocess_band_table.shape[0]
    if total_bands == 0:
        cfg.mx.msg_war_7()
    for band in range(total_bands):
        # add rows
        count = table.rowCount()
        table.setRowCount(count + 1)
        n = 0
        for field in cfg.preprocess_band_table.dtype.names:
            if str(cfg.preprocess_band_table[field][band]) != 'None':
                cfg.util_qt.add_table_item(
                    table, str(cfg.preprocess_band_table[field][band]),
                    count, n
                )
            n += 1
    table.setSortingEnabled(True)
    table.blockSignals(False)


# perform conversion
def perform_conversion(output_path=None, load_in_qgis=False):
    if output_path is None or output_path is False:
        output_path = cfg.util_qt.get_existing_directory(
            None, cfg.translate('Select a directory')
        )
    if output_path is not False and cfg.preprocess_band_table is not None:
        if cfg.dialog.ui.create_bandset_checkBox.isChecked() is True:
            if cfg.dialog.ui.add_new_bandset_radioButton_1.isChecked() is True:
                # added new bandset
                add_bandset = True
            else:
                # replaced bandset
                add_bandset = False
        else:
            # no added bandset
            add_bandset = None
        if cfg.dialog.ui.DOS1_checkBox.isChecked() is True:
            dos1_correction = True
        else:
            dos1_correction = False
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.preprocess_products.perform_preprocess(
            product_table=cfg.preprocess_band_table, output_path=output_path,
            dos1_correction=dos1_correction, add_bandset=add_bandset,
            bandset_catalog=cfg.bandset_catalog, output_prefix='RT_'
        )
        if output.check:
            if load_in_qgis:
                output_paths = output.paths
                for raster in output_paths:
                    # add raster to layers
                    cfg.util_qgis.add_raster_layer(raster)
        else:
            cfg.mx.msg_err_1()
        if add_bandset is True:
            bandset_number = None
            for bandset_number in range(
                    1, cfg.bandset_catalog.get_bandset_count() + 1
            ):
                cfg.bst.band_set_to_table(bandset_number)
            cfg.bst.bandset_tools(
                output_directory=output_path,
                bandset_number=bandset_number
            )
        cfg.mx.msg_inf_6()
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


# remove bands
def remove_highlighted_band():
    answer = cfg.util_qt.question_box(
        cfg.translate('Remove rows'),
        cfg.translate(
            'Are you sure you want to remove highlighted rows from the table?'
        )
    )
    if answer is True:
        table = cfg.dialog.ui.bands_tableWidget
        # list of item to remove
        rows = []
        for index in table.selectedIndexes():
            rows.append(index.row())
        selected_rows = list(set(rows))
        band_name_list = []
        count = table.rowCount()
        for row in range(count):
            if row not in selected_rows:
                band_name_list.append(str(table.item(row, 3).text()))
        enum_list = []
        for n, band_name in enumerate(cfg.preprocess_band_table.band_name):
            if str(band_name) in band_name_list:
                enum_list.append(n)
        cfg.preprocess_band_table = cfg.preprocess_band_table[enum_list]
        cfg.util_qt.clear_table(table)
        table.blockSignals(True)
        table.setSortingEnabled(False)
        total_products = cfg.preprocess_band_table.shape[0]
        for product in range(total_products):
            # add rows
            count = table.rowCount()
            table.setRowCount(count + 1)
            n = 0
            for field in cfg.preprocess_band_table.dtype.names:
                if str(cfg.preprocess_band_table[field][product]) != 'None':
                    cfg.util_qt.add_table_item(
                        table, str(cfg.preprocess_band_table[field][product]),
                        count, n
                    )
                n += 1
        table.setSortingEnabled(True)
        table.blockSignals(False)


# set script button
def set_script():
    output_path = 'output_path'
    output_prefix = 'RT_'
    input_path = cfg.dialog.ui.label_26.text()
    metadata_file_path = cfg.dialog.ui.label_27.text()
    if len(metadata_file_path) == 0:
        metadata_file_path = None
    if cfg.dialog.ui.create_bandset_checkBox.isChecked() is True:
        create_catalog = ('# crete bandset catalog\n'
                          'catalog = rs.bandset_catalog()\n')
        catalog = 'catalog'
        if cfg.dialog.ui.add_new_bandset_radioButton_1.isChecked() is True:
            add_bandset = True
        else:
            add_bandset = False
    else:
        create_catalog = ''
        catalog = 'None'
        add_bandset = None
    if cfg.dialog.ui.DOS1_checkBox.isChecked() is True:
        dos1_correction = True
    else:
        dos1_correction = False
    if cfg.dialog.ui.nodata_checkBox_2.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_3.value()
    else:
        nodata = None
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# image conversion\n'
               '%s'
               'rs.preprocess_products.preprocess(input_path="%s", '
               'output_path="%s", metadata_file_path="%s", add_bandset=%s, '
               'nodata_value=%s, dos1_correction=%s, output_prefix="%s", '
               'bandset_catalog=%s)'
               % (str(create_catalog), str(input_path), str(output_path),
                  str(metadata_file_path), str(add_bandset),
                  str(nodata), str(dos1_correction), str(output_prefix),
                  str(catalog)))
    previous = cfg.dialog.ui.plainTextEdit_batch.toPlainText()
    if 'import remotior_sensus' in previous:
        text = '\n'.join([previous, command])
    else:
        text = '\n'.join(
            ['import remotior_sensus', session, previous,
             command]
        )
    cfg.dialog.ui.plainTextEdit_batch.setPlainText(
        text.replace('"None"', 'None').replace('"False"', 'False').replace(
            '"True"', 'True'
        )
    )
    cfg.input_interface.script_tab()
