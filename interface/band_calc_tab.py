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
"""Band calc.

This tool allows for calculations between raster bands.
"""

try:
    from remotior_sensus.tools import band_calc as rs_calc
except Exception as error:
    str(error)

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# fill raster band table
# noinspection PyProtectedMember,PyArgumentList
def raster_band_table(bandset_number=None):
    if bandset_number is None or bandset_number is False:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    # get QGIS rasters
    layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
    input_name_list = []
    input_raster_list = []
    for x in sorted(layers, key=lambda layer_x: layer_x.name()):
        if (x.type() == cfg.util_qgis.get_qgis_map_raster()
                and x.bandCount() == 1):
            input_name_list.append(x.name())
            input_raster_list.append(x.source())
    # create list of band names from band sets
    cfg.calc_raster_variables = rs_calc._band_names_alias(
        input_raster_list=input_raster_list, input_name_list=input_name_list,
        bandset_catalog=cfg.bandset_catalog,
        bandset_number=bandset_number
    )
    table = cfg.dialog.ui.tableWidget_band_calc
    table.setSortingEnabled(False)
    cfg.util_qt.clear_table(table)
    # row counter
    b = 0
    # Add band to table
    for raster in cfg.calc_raster_variables:
        table.insertRow(b)
        cfg.util_qt.add_table_item(table, raster[1:-1], b, 0, False)
        b += 1
    # add current bandset all bands
    if cfg.bandset_catalog.get_bandset_count() > 0:
        # Add band to table
        table.insertRow(b)
        cfg.util_qt.add_table_item(
            table, '%s#b*' % cfg.variable_bandset_name, b, 0, False
        )
        b += 1
    # add current bandset bands
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    bands = bandset_x.get_band_alias()
    for band in bands:
        # Add band to table
        table.insertRow(b)
        cfg.util_qt.add_table_item(
            table, '%s#%s' % (cfg.variable_bandset_name, band), b, 0, False
        )
        b += 1
    # current bandset spectral range bands
    try:
        (blue_band, green_band, red_band, nir_band, swir_1_band,
         swir_2_band) = bandset_x.spectral_range_bands(output_as_number=False)
    except Exception as err:
        str(err)
        blue_band = green_band = red_band = nir_band = swir_1_band = None
        swir_2_band = None
    spectral_bands = [
        [cfg.rs.configurations.variable_blue_name, blue_band],
        [cfg.rs.configurations.variable_green_name, green_band],
        [cfg.rs.configurations.variable_red_name, red_band],
        [cfg.rs.configurations.variable_nir_name, nir_band],
        [cfg.rs.configurations.variable_swir1_name, swir_1_band],
        [cfg.rs.configurations.variable_swir2_name, swir_2_band]]
    for spectral_band in spectral_bands:
        if spectral_band[1] is not None:
            # Add band to table
            table.insertRow(b)
            cfg.util_qt.add_table_item(
                table, '%s' % spectral_band[0], b, 0, False
            )
            b += 1
    # add all bandset bands
    for bs_number in range(1, cfg.bandset_catalog.get_bandset_count() + 1):
        bandset_x = cfg.bandset_catalog.get_bandset_by_number(bs_number)
        bands = bandset_x.get_band_alias()
        # Add band to table
        table.insertRow(b)
        cfg.util_qt.add_table_item(
            table, '%s%ib*' % (cfg.variable_bandset_name, bs_number), b, 0,
            False
        )
        b += 1
        for band in bands:
            # Add band to table
            table.insertRow(b)
            cfg.util_qt.add_table_item(
                table, '%s%i%s' % (cfg.variable_bandset_name, bs_number, band),
                b, 0, False
            )
            b += 1
    text_changed()
    cfg.utils.refresh_raster_extent_combo()
    cfg.utils.refresh_raster_align_combo()


# text changed
def text_changed():
    expression = cfg.dialog.ui.plainTextEdit_calc.toPlainText()
    check_expression(expression=expression)


# check the expression and return it
# noinspection PyProtectedMember,PyArgumentList
def check_expression(expression, raster_variables=None, bandset_number=None):
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    if raster_variables is None:
        raster_variables = cfg.calc_raster_variables
    else:
        # get QGIS rasters
        layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
        input_name_list = []
        input_raster_list = []
        for x in sorted(layers, key=lambda layer_x: layer_x.name()):
            if (x.type() == cfg.util_qgis.get_qgis_map_raster()
                    and x.bandCount() == 1):
                input_name_list.append(x.name())
                input_raster_list.append(x.source())
        raster_variables = rs_calc._band_names_alias(
            input_raster_list=input_raster_list,
            input_name_list=input_name_list,
            bandset_catalog=cfg.bandset_catalog,
            bandset_number=bandset_number
        )
    if raster_variables is not None:
        (exp_list, all_out_name_list,
         output_message) = rs_calc._check_expression(
            expression_string=expression, raster_variables=raster_variables,
            bandset_catalog=cfg.bandset_catalog,
            bandset_number=bandset_number
        )
        if output_message is not None:
            if len(expression) == 0:
                cfg.dialog.ui.label_band_calc.setText(' Expression')
            else:
                message = output_message.split(':')
                try:
                    cfg.dialog.ui.label_band_calc.setText(
                        ' Expression error [line %s]: %s'
                        % (int((int(message[0]) - 1) / 2), message[1])
                    )
                except Exception as err:
                    str(err)
                    cfg.dialog.ui.label_band_calc.setText(
                        ' Expression error %s' % message
                    )
            cfg.dialog.ui.plainTextEdit_calc.setStyleSheet('color : black')
            cfg.dialog.ui.toolButton_calculate.setEnabled(False)
        else:
            cfg.dialog.ui.label_band_calc.setText(' Expression')
            cfg.dialog.ui.plainTextEdit_calc.setStyleSheet('color : green')
            cfg.dialog.ui.toolButton_calculate.setEnabled(True)
            output_name_table(name_list=all_out_name_list)
        return exp_list


# Set output name table
def output_name_table(name_list):
    table = cfg.dialog.ui.tableWidget_band_calc
    table.blockSignals(True)
    table.setSortingEnabled(False)
    c = table.rowCount()
    # remove items
    for i in reversed(range(0, c)):
        if table.item(i, 1) is not None:
            if cfg.rs.configurations.default_output_name in table.item(
                    i, 1
            ).text():
                table.removeRow(i)
            else:
                break
        else:
            break
    b = table.rowCount()
    for name in name_list:
        if len(name) > 0:
            # Add band to table
            table.insertRow(b)
            cfg.util_qt.add_table_item(table, name, b, 0, False)
            cfg.util_qt.add_table_item(
                table, cfg.rs.configurations.default_output_name, b, 1, False
            )
            b += 1
    table.setSortingEnabled(True)
    table.blockSignals(False)


# import expressions from file
def import_expression_list():
    function_file = cfg.util_qt.get_open_file(
        None, 'Select an expression file', '', 'TXT (*.txt)'
    )
    if len(function_file) > 0:
        try:
            f = open(function_file)
            sep = ';'
            if cfg.utils.check_file(function_file):
                cfg.qgis_registry[cfg.reg_custom_functions] = []
                lines = f.readlines()
                if len(lines) > 0:
                    for line in lines:
                        try:
                            splitter = line.split(sep)
                            # name and expression
                            name = splitter[0]
                            expression = splitter[1].strip()
                            cfg.qgis_registry[
                                cfg.reg_custom_functions].append(
                                [name, expression]
                            )
                        except Exception as err:
                            str(err)
                    create_expression_list(
                        cfg.qgis_registry[cfg.reg_custom_functions]
                    )
                else:
                    cfg.util_qt.clear_table(
                        cfg.dialog.ui.band_calc_function_tableWidget
                    )
                    add_functions_to_table(cfg.band_calc_functions)
                    cfg.qgis_registry[cfg.reg_custom_functions] = []
        except Exception as err:
            str(err)


# create expression list
def create_expression_list(expression_list):
    cfg.util_qt.clear_table(cfg.dialog.ui.band_calc_function_tableWidget)
    add_functions_to_table(cfg.band_calc_functions)
    add_functions_to_table(expression_list)


# add function list to table
def add_functions_to_table(function_list):
    if function_list is not None:
        table = cfg.dialog.ui.band_calc_function_tableWidget
        # count table rows
        c = table.rowCount()
        for i in function_list:
            table.blockSignals(True)
            try:
                _check = i[1]
                # add list items to table
                table.setRowCount(c + 1)
                cfg.util_qt.add_table_item(table, i[0], c, 0)
                c += 1
            except Exception as err:
                str(err)
                # add list items to table
                table.setRowCount(c + 1)
                color = cfg.util_qt.get_color_from_rgb(200, 200, 200)
                cfg.util_qt.add_table_item(
                    table, i[0], c, 0, False, color, bold=True
                )
                c += 1
            table.blockSignals(False)


# set function
def set_function(index):
    cursor = cfg.dialog.ui.plainTextEdit_calc.textCursor()
    name = cfg.dialog.ui.band_calc_function_tableWidget.item(
        index.row(), 0
    ).text()
    if len(cfg.qgis_registry[cfg.reg_custom_functions]) > 0:
        functions = cfg.band_calc_functions.extend(
            cfg.qgis_registry[cfg.reg_custom_functions]
        )
    else:
        functions = cfg.band_calc_functions
    for i in functions:
        if name == i[0]:
            try:
                cursor.insertHtml(' ' + i[1])
            except Exception as err:
                str(err)
                return False


# double click
def double_click(index):
    table = cfg.dialog.ui.tableWidget_band_calc
    k = table.item(index.row(), index.column()).text()
    cursor = cfg.dialog.ui.plainTextEdit_calc.textCursor()
    cursor.insertText('"' + k + '"')
    cfg.dialog.ui.plainTextEdit_calc.setFocus()


# perform bands filter
def filter_table():
    table = cfg.dialog.ui.tableWidget_band_calc
    text = cfg.dialog.ui.bandcalc_filter_lineEdit.text()
    items = table.findItems(text, cfg.util_qt.get_match_contains())
    c = table.rowCount()
    filtered = []
    for item in items:
        if item is not None:
            if item.column() == 0:
                filtered.append(item.row())
    table.blockSignals(True)
    for i in range(0, c):
        table.setRowHidden(i, False)
        if i not in filtered:
            table.setRowHidden(i, True)
    table.blockSignals(False)


# calculate button
def calculate_button():
    calculate()


# calculate
# noinspection PyArgumentList
def calculate(output_path=None):
    expression_count = cfg.dialog.ui.plainTextEdit_calc.blockCount()
    if output_path is None:
        # multiple lines
        if expression_count > 1:
            output_path = cfg.util_qt.get_existing_directory(
                None, cfg.translate('Select a directory')
            )
            if output_path is False:
                return
            else:
                if len(output_path) == 0:
                    return
        # one line
        else:
            output_path = cfg.util_qt.get_save_file_name(
                None, cfg.translate('Save raster output'), '',
                'TIF file (*.tif);;VRT file (*.vrt)', None
            )
            if output_path is not False:
                if output_path.lower().endswith('.vrt'):
                    pass
                elif not output_path.lower().endswith('.tif'):
                    output_path += '.tif'
    if output_path is not False:
        cfg.logger.log.info('calculate: %s' % output_path)
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
        # get extent
        extent_raster = extent_list = xy_resolution_list = align_raster = None
        extent_intersection = None
        extent_type = cfg.dialog.ui.raster_extent_combo.currentText()
        if extent_type == cfg.union_extent:
            extent_intersection = False
        elif extent_type == cfg.map_extent:
            rectangle = cfg.map_canvas.extent()
            extent_list = [rectangle.xMinimum(), rectangle.yMaximum(),
                           rectangle.xMaximum(), rectangle.yMinimum()]
            extent_intersection = False
        elif extent_type == cfg.intersection_extent:
            extent_intersection = True
        elif extent_type == cfg.custom_extent:
            extent_list = [int(cfg.dialog.ui.UL_X_lineEdit.text()),
                           int(cfg.dialog.ui.UL_Y_linedit.text()),
                           int(cfg.dialog.ui.LR_X_lineEdit.text()),
                           int(cfg.dialog.ui.LR_Y_lineEdit.text())]
        else:
            # get QGIS rasters
            layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
            for x in sorted(layers, key=lambda layer_x: layer_x.name()):
                if (x.type() == cfg.util_qgis.get_qgis_map_raster()
                        and x.bandCount() == 1):
                    if extent_type == x.name():
                        extent_raster = x.source()
                        break
        # alignment
        align_type = cfg.dialog.ui.raster_extent_combo.currentText()
        if align_type == cfg.default_align:
            align_raster = False
        else:
            # get QGIS rasters
            layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
            for x in sorted(layers, key=lambda layer_x: layer_x.name()):
                if (x.type() == cfg.util_qgis.get_qgis_map_raster()
                        and x.bandCount() == 1):
                    if extent_type == x.name():
                        align_raster = x.source()
                        break
        # pixel resolution
        pixel_resolution = cfg.dialog.ui.resolution_lineEdit.text()
        if len(pixel_resolution) > 0:
            try:
                xy_resolution_list = [float(pixel_resolution),
                                      float(pixel_resolution)]
            except Exception as err:
                str(err)
                cfg.mx.msg_war_1()
        # input nodata as value
        if cfg.dialog.ui.nodata_as_value_checkBox.isChecked() is True:
            input_nodata_as_value = True
        else:
            input_nodata_as_value = None
        # use value as nodata
        if cfg.dialog.ui.nodata_checkBox_3.isChecked() is True:
            use_value_as_nodata = cfg.dialog.ui.nodata_spinBox_13.value()
        else:
            use_value_as_nodata = None
        # nodata mask
        if cfg.dialog.ui.nodata_mask_combo.currentText() == 'False':
            any_nodata_mask = False
        elif cfg.dialog.ui.nodata_mask_combo.currentText() == 'True':
            any_nodata_mask = True
        else:
            any_nodata_mask = None
        # scale
        if cfg.dialog.ui.set_scale_checkBox.isChecked() is True:
            use_scale = cfg.dialog.ui.scale_doubleSpinBox.value()
        else:
            use_scale = None
        # offset
        if cfg.dialog.ui.set_offset_checkBox.isChecked() is True:
            use_offset = cfg.dialog.ui.offset_doubleSpinBox.value()
        else:
            use_offset = None
        # output nodata
        output_nodata = cfg.dialog.ui.nodata_spinBox_4.value()
        # output datatype
        output_datatype = cfg.dialog.ui.raster_type_combo.currentText()
        # calc data type
        calc_datatype = cfg.dialog.ui.calc_type_combo.currentText()
        expression = cfg.dialog.ui.plainTextEdit_calc.toPlainText()
        cfg.ui_utils.add_progress_bar()
        # get QGIS rasters
        layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
        input_name_list = []
        input_raster_list = []
        for x in sorted(layers, key=lambda layer_x: layer_x.name()):
            if (x.type() == cfg.util_qgis.get_qgis_map_raster()
                    and x.bandCount() == 1):
                input_name_list.append(x.name())
                input_raster_list.append(x.source())
        # run calculation
        output = cfg.rs.band_calc(
            expression_string=expression, output_path=output_path,
            input_raster_list=input_raster_list,
            input_name_list=input_name_list, align_raster=align_raster,
            extent_raster=extent_raster, extent_list=extent_list,
            extent_intersection=extent_intersection,
            xy_resolution_list=xy_resolution_list,
            input_nodata_as_value=input_nodata_as_value,
            use_value_as_nodata=use_value_as_nodata,
            output_nodata=output_nodata, output_datatype=output_datatype,
            use_scale=use_scale, use_offset=use_offset,
            calc_datatype=calc_datatype, any_nodata_mask=any_nodata_mask,
            bandset_catalog=cfg.bandset_catalog, bandset_number=bandset_number
        )
        # add output rasters
        if output.check:
            paths = output.paths
            for raster in paths:
                cfg.util_qgis.add_raster_layer(raster)
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))
