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
"""Multiple ROI.

This tool allows for the creation of multiple ROIs.
"""

import numpy
from PyQt5.QtWidgets import qApp

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# add point
def add_row_to_table():
    table = cfg.dialog.ui.point_tableWidget
    table.setRowCount(table.rowCount() + 1)


# add random point
def add_point_to_table(point):
    table = cfg.dialog.ui.point_tableWidget
    count = table.rowCount()
    table.setRowCount(count + 1)
    if cfg.dock_class_dlg.ui.rapid_ROI_checkBox.isChecked() is True:
        band = str(cfg.project_registry[cfg.reg_roi_main_band])
    else:
        band = ''
    cfg.util_qt.add_table_item(table, str(point[0]), count, 0)
    cfg.util_qt.add_table_item(table, str(point[1]), count, 1)
    cfg.util_qt.add_table_item(
        table, str(
            cfg.project_registry[cfg.reg_roi_macroclass_id]
        ), count, 2
    )
    cfg.util_qt.add_table_item(
        table, str(
            cfg.project_registry[cfg.reg_roi_macroclass_name]
        ), count, 3
    )
    cfg.util_qt.add_table_item(
        table, str(cfg.project_registry[cfg.reg_roi_class_id]), count, 4
    )
    cfg.util_qt.add_table_item(
        table, str(
            cfg.project_registry[cfg.reg_roi_class_name]
        ), count, 5
    )
    cfg.util_qt.add_table_item(
        table, str(cfg.project_registry[cfg.reg_roi_min_size]), count, 6
    )
    cfg.util_qt.add_table_item(
        table, str(
            cfg.project_registry[cfg.reg_roi_max_width]
        ), count, 7
    )
    cfg.util_qt.add_table_item(
        table, str(
            cfg.project_registry[cfg.reg_roi_range_radius]
        ), count, 8
    )
    cfg.util_qt.add_table_item(table, band, count, 9)


# text changed
def expression_text_edited():
    expression = cfg.dialog.ui.stratified_lineEdit.text()
    expression_split = expression.split(';')
    check = True
    for condition in expression_split:
        try:
            cfg.dialog.ui.stratified_lineEdit.setStyleSheet('color : green')
            eval(
                condition.replace(
                    cfg.qgis_registry[cfg.reg_raster_variable_name], '1'
                )
            )
            if (condition.strip()
                    == cfg.qgis_registry[cfg.reg_raster_variable_name]):
                cfg.dialog.ui.stratified_lineEdit.setStyleSheet('color : red')
                check = False
        except Exception as err:
            cfg.logger.log.error(str(err))
            cfg.dialog.ui.stratified_lineEdit.setStyleSheet('color : red')
            check = False
    return check


# create random point
def create_random_point():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_10.value()
    bandset_x = cfg.bandset_catalog.get(bandset_number)
    cfg.logger.log.debug(
        'create_random_point bandset_number: %s' % bandset_number
    )
    if bandset_x is None:
        cfg.mx.msg_war_6(bandset_number)
        return False
    band_count = bandset_x.get_band_count()
    if band_count == 0:
        cfg.mx.msg_war_6(bandset_number)
        return False
    band_left = bandset_x.bands[0].left
    band_top = bandset_x.bands[0].top
    band_right = bandset_x.bands[0].right
    band_bottom = bandset_x.bands[0].bottom
    raster_path = bandset_x.bands[0].path
    point_number = int(cfg.dialog.ui.point_number_spinBox.value())
    if cfg.dialog.ui.point_distance_checkBox.isChecked() is True:
        min_distance = int(cfg.dialog.ui.point_distance_spinBox.value())
    else:
        min_distance = None
    stratified = None
    stratified_expression = None
    if cfg.dialog.ui.stratified_point_checkBox.isChecked() is True:
        check = expression_text_edited()
        if check is True:
            stratified = True
            stratified_expression = cfg.dialog.ui.stratified_lineEdit.text()
        else:
            cfg.mx.msg_err_7()
            return False
    points = new_points = None
    cfg.ui_utils.add_progress_bar()
    # points inside grid
    if cfg.dialog.ui.point_grid_checkBox.isChecked() is True:
        grid_size = int(cfg.dialog.ui.point_grid_spinBox.value())
        x_range = list(range(int(band_left), int(band_right), grid_size))
        y_range = list(range(int(band_bottom), int(band_top), grid_size))
        x_count = 1
        for x in x_range:
            if x_count < len(x_range):
                y_count = 1
                for y in y_range:
                    if y_count < len(y_range):
                        new_points = cfg.utils.random_points_in_grid(
                            point_number=point_number, x_min=x,
                            x_max=x + x_range[x_count],
                            y_min=y, y_max=y + y_range[y_count]
                        )
                    if points is None:
                        points = new_points
                    else:
                        points.extend(new_points)
                    y_count += 1
                x_count += 1
    elif stratified is not None:
        expression_split = stratified_expression.split(';')
        for expression in expression_split:
            new_points = cfg.utils.random_points_with_condition(
                raster_path=raster_path, point_number=point_number,
                condition=expression, x_min=band_left, y_top=band_top
            )
            if points is None:
                points = new_points
            else:
                points.extend(new_points)
    else:
        points = cfg.utils.random_points_in_grid(
            point_number=point_number, x_min=band_left,
            x_max=band_right, y_min=band_bottom, y_max=band_top
        )
    # check distance
    if min_distance is not None:
        while True:
            point_array = numpy.array(points)
            distance = cfg.utils.pair_point_distance(point_array)
            distance = distance * numpy.tril(numpy.ones(distance.shape), k=-1)
            rows, cols = numpy.where(
                (distance > 0) & (distance < min_distance)
            )
            if rows.shape[0] == 0:
                break
            else:
                points.pop(int(rows[0]))
    if points is not None:
        for point in points:
            add_point_to_table(point)
    cfg.ui_utils.remove_progress_bar()


# create ROIs
def create_roi_from_points():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_10.value()
    table = cfg.dialog.ui.point_tableWidget
    count = table.rowCount()
    cfg.logger.log.debug(
        'create_roi_from_points bandset_number: %s' % bandset_number
    )
    if count > 0:
        cfg.ui_utils.add_progress_bar()
        for i in range(0, count):
            qApp.processEvents()
            if cfg.rs.configurations.action:
                cfg.ui_utils.update_bar((i + 1) * 100 / (count + 1))
                try:
                    x_coordinate = table.item(i, 0).text()
                    y_coordinate = table.item(i, 1).text()
                except Exception as err:
                    cfg.logger.log.error(str(err))
                    cfg.mx.msg_err_6()
                    break
                try:
                    point = cfg.util_qgis.create_qgis_point(
                        float(x_coordinate), float(y_coordinate)
                    )
                    point = cfg.utils.check_point_in_image(point=point)
                    if point is False:
                        cfg.mx.msg_war_3()
                        return False
                    # get ROI parameters
                    if len(table.item(i, 6).text()) > 0:
                        v = int(table.item(i, 6).text())
                        cfg.project_registry[cfg.reg_roi_min_size] = v
                    if len(table.item(i, 7).text()) > 0:
                        v = int(table.item(i, 7).text())
                        cfg.project_registry[cfg.reg_roi_max_width] = v
                    if len(table.item(i, 8).text()) > 0:
                        v = float(table.item(i, 8).text())
                        cfg.project_registry[cfg.reg_roi_range_radius] = v
                    if len(table.item(i, 9).text()) > 0:
                        v = int(table.item(i, 9).text())
                        cfg.project_registry[cfg.reg_roi_main_band] = v
                        cfg.project_registry[
                            cfg.reg_rapid_roi_check] = 2
                    cfg.scp_dock.create_region_growing_roi(
                        point=point, bandset_number=bandset_number
                    )
                    # get ROI attributes
                    v = int(table.item(i, 2).text())
                    cfg.project_registry[cfg.reg_roi_macroclass_id] = v
                    cfg.project_registry[cfg.reg_roi_macroclass_name] = (
                        table.item(i, 3).text()
                    )
                    v = int(table.item(i, 4).text())
                    cfg.project_registry[cfg.reg_roi_class_id] = v
                    cfg.project_registry[cfg.reg_roi_class_name] = (
                        table.item(i, 5).text()
                    )
                    cfg.scp_dock.save_roi_to_training(
                        bandset_number=bandset_number
                    )
                except Exception as err:
                    cfg.logger.log.error(str(err))
                    cfg.mx.msg_err_6()
                    break
        # restore settings for single ROI
        cfg.scp_dock.roi_macroclass_id_value()
        cfg.scp_dock.roi_macroclass_name_info()
        cfg.scp_dock.roi_class_id_value()
        cfg.scp_dock.roi_class_name_info()
        cfg.scp_dock.roi_min_size()
        cfg.scp_dock.max_roi_width()
        cfg.scp_dock.range_radius()
        cfg.scp_dock.rapid_roi_band()
        cfg.scp_dock.rapid_roi_checkbox()
        cfg.ui_utils.remove_progress_bar()


# export point list to file
def export_point_list():
    output_path = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Save the point list to file'), '', '*.csv', 'csv'
    )
    separator = ';'
    if output_path is not False:
        cfg.logger.log.debug('export_point_list: %s' % output_path)
        if output_path.lower().endswith('.csv'):
            pass
        else:
            output_path = output_path + '.csv'
        text = (
                'X' + separator + 'Y' + separator + 'MC_ID' + separator
                + 'MC_Info' + separator + 'C_ID' + separator + 'C_Info'
                + separator + 'Min' + separator + 'Max' + separator + 'Dist'
                + separator + 'Rapid_ROI_band\n'
        )
        table = cfg.dialog.ui.point_tableWidget
        count = table.rowCount()
        for i in range(0, count):
            x_coordinate = table.item(i, 0).text()
            y_coordinate = table.item(i, 1).text()
            mc_id = table.item(i, 2).text()
            mc_info = table.item(i, 3).text()
            c_id = table.item(i, 4).text()
            c_info = table.item(i, 5).text()
            min_size = ''
            max_width = ''
            range_rad = ''
            roi_band = ''
            try:
                min_size = table.item(i, 6).text()
                max_width = table.item(i, 7).text()
                range_rad = table.item(i, 8).text()
                roi_band = table.item(i, 9).text()
            except Exception as err:
                str(err)
            text += (
                    x_coordinate + separator + y_coordinate + separator + mc_id
                    + separator + mc_info + separator + c_id + separator
                    + c_info + separator + min_size + separator + max_width
                    + separator + range_rad + separator + roi_band + '\n'
            )
        with open(output_path, 'w') as f:
            f.write(text)


# import points from file
def import_points_csv():
    point_file = cfg.util_qt.get_open_file(
        None, cfg.translate('Select a point list file'), '',
        'CSV (*.csv);; Point SHP .shp (*.shp);; Point GPKG .shp (*.gpkg)'
    )
    if len(point_file) > 0:
        if point_file.lower().endswith('.csv'):
            try:
                f = open(point_file)
                if cfg.utils.check_file(point_file):
                    lines = f.readlines()
                    if '\t' in lines[0]:
                        separator = '\t'
                    else:
                        separator = ';'
                    table = cfg.dialog.ui.point_tableWidget
                    for line in range(1, len(lines)):
                        # point list
                        split_line = lines[line].strip().split(separator)
                        min_size = cfg.project_registry[cfg.reg_roi_min_size]
                        max_width = cfg.project_registry[cfg.reg_roi_max_width]
                        range_rad = cfg.project_registry[
                            cfg.reg_roi_range_radius
                        ]
                        roi_band = ''
                        try:
                            min_size = split_line[6]
                            max_width = split_line[7]
                            range_rad = split_line[8]
                            roi_band = split_line[9]
                        except Exception as err:
                            str(err)
                        # add item to table
                        count = table.rowCount()
                        # add list items to table
                        table.setRowCount(count + 1)
                        cfg.util_qt.add_table_item(
                            table, split_line[0], count, 0
                        )
                        cfg.util_qt.add_table_item(
                            table, split_line[1], count, 1
                        )
                        cfg.util_qt.add_table_item(
                            table, split_line[2], count, 2
                        )
                        cfg.util_qt.add_table_item(
                            table, split_line[3], count, 3
                        )
                        cfg.util_qt.add_table_item(
                            table, split_line[4], count, 4
                        )
                        cfg.util_qt.add_table_item(
                            table, split_line[5], count, 5
                        )
                        cfg.util_qt.add_table_item(table, min_size, count, 6)
                        cfg.util_qt.add_table_item(table, max_width, count, 7)
                        cfg.util_qt.add_table_item(table, range_rad, count, 8)
                        cfg.util_qt.add_table_item(table, roi_band, count, 9)
            except Exception as err:
                cfg.logger.log.error(str(err))
                cfg.mx.msg_err_5()
        elif (point_file.lower().endswith('.shp')
              or point_file.lower().endswith('.gpkg')):
            try:
                _vector = cfg.util_gdal.open_vector(point_file)
                _layer = _vector.GetLayer()
                _feature = _layer.GetNextFeature()
                while _feature:
                    geometry = _feature.GetGeometryRef()
                    point = [geometry.GetX(), geometry.GetY()]
                    _feature.Destroy()
                    _feature = _layer.GetNextFeature()
                    add_point_to_table(point)
                _layer = None
                _vector = None
            except Exception as err:
                cfg.logger.log.error(str(err))
                cfg.mx.msg_err_5()


def remove_row_from_table():
    cfg.util_qt.remove_rows_from_table(cfg.dialog.ui.point_tableWidget)


# Activate signature calculation checkbox2
def signature_checkbox_2():
    if cfg.dialog.ui.signature_checkBox2.isChecked() is True:
        # connected checkbox
        cfg.dock_class_dlg.ui.signature_checkBox.setCheckState(2)
    else:
        cfg.dock_class_dlg.ui.signature_checkBox.setCheckState(0)
