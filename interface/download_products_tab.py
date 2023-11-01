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
"""Download products.

Allows for downloading products such as Landsat and Sentinel-2 datasets.
"""

import subprocess
from re import sub
from shlex import split

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF, QColor, QPixmap, QCursor
from qgis.core import (
    QgsGeometry, QgsCoordinateReferenceSystem, QgsRectangle
)
from qgis.gui import QgsRubberBand

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

""" Login data """


# Earthdata user
def remember_user_earthdata():
    if cfg.dialog.ui.remember_user_checkBox_3.isChecked():
        user = cfg.dialog.ui.user_earthdata_lineEdit.text()
        password = cfg.utils.encrypt_password(
            cfg.dialog.ui.password_earthdata_lineEdit.text()
        )
        cfg.qgis_registry[cfg.reg_earthdata_user] = user
        cfg.qgis_registry[cfg.reg_earthdata_pass] = password


# Earthdata user checkbox
def remember_user_earthdata_checkbox():
    if cfg.dialog.ui.remember_user_checkBox_3.isChecked():
        cfg.mx.msg_box_warning(
            cfg.translate('WARNING'),
            cfg.translate('Password is stored unencrypted')
        )
        remember_user_earthdata()
    else:
        cfg.qgis_registry[cfg.reg_earthdata_user] = ''
        cfg.qgis_registry[cfg.reg_earthdata_pass] = ''


""" Interface """


# add rubber polygon
def add_rubber_polygon(upper_left_point, lower_right_point):
    try:
        clear_canvas_poly()
    except Exception as err:
        str(err)
    cfg.download_rubber_poly = QgsRubberBand(
        cfg.map_canvas, cfg.util_qgis.get_qgis_wkb_types().LineGeometry
    )
    point_f = QPointF()
    poly_f = QPolygonF()
    point_f.setX(upper_left_point.x())
    point_f.setY(upper_left_point.y())
    poly_f.append(point_f)
    point_f.setX(lower_right_point.x())
    point_f.setY(upper_left_point.y())
    poly_f.append(point_f)
    point_f.setX(lower_right_point.x())
    point_f.setY(lower_right_point.y())
    poly_f.append(point_f)
    point_f.setX(upper_left_point.x())
    point_f.setY(lower_right_point.y())
    poly_f.append(point_f)
    point_f.setX(upper_left_point.x())
    point_f.setY(upper_left_point.y())
    poly_f.append(point_f)
    geometry = QgsGeometry().fromQPolygonF(poly_f)
    # noinspection PyTypeChecker
    cfg.download_rubber_poly.setToGeometry(geometry, None)
    clr = QColor('#ff0000')
    clr.setAlpha(50)
    cfg.download_rubber_poly.setFillColor(clr)
    cfg.download_rubber_poly.setWidth(3)


# clear canvas
def clear_canvas_poly():
    try:
        cfg.download_rubber_poly.reset()
    except Exception as err:
        str(err)
    cfg.map_canvas.refresh()


# activate pointer
def pointer_active():
    cfg.map_canvas.setMapTool(cfg.download_products_pointer)
    cursor = QCursor(QPixmap(':/pointer/icons/pointer/ROI_pointer.svg'))
    cfg.map_canvas.setCursor(cursor)


# left click pointer
def pointer_left_click(point):
    pointer_click_ul(point)


# right click pointer
def pointer_right_click(point):
    pointer_click_lr(point)


# set coordinates
def pointer_click_lr(point):
    qgis_crs = cfg.util_qgis.get_qgis_crs()
    # WGS84 EPSG 4326
    target_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    point_proj = cfg.utils.project_qgis_point_coordinates(
        point, qgis_crs,
        target_crs
    )
    if point_proj is not False:
        try:
            if float(cfg.dialog.ui.UX_lineEdit_3.text()) < point_proj.x():
                cfg.dialog.ui.LX_lineEdit_3.setText(str(point_proj.x()))
            else:
                cfg.dialog.ui.LX_lineEdit_3.setText(
                    str(
                        cfg.dialog.ui.UX_lineEdit_3.text()
                    )
                )
                cfg.dialog.ui.UX_lineEdit_3.setText(str(point_proj.x()))
            if float(cfg.dialog.ui.UY_lineEdit_3.text()) > point_proj.y():
                cfg.dialog.ui.LY_lineEdit_3.setText(str(point_proj.y()))
            else:
                cfg.dialog.ui.LY_lineEdit_3.setText(
                    str(
                        cfg.dialog.ui.UY_lineEdit_3.text()
                    )
                )
                cfg.dialog.ui.UY_lineEdit_3.setText(str(point_proj.y()))
        except Exception as err:
            str(err)
            cfg.dialog.ui.LX_lineEdit_3.setText(str(point_proj.x()))
            cfg.dialog.ui.LY_lineEdit_3.setText(str(point_proj.y()))
        show_area()


# set coordinates
def pointer_click_ul(point):
    qgis_crs = cfg.util_qgis.get_qgis_crs()
    # WGS84 EPSG 4326
    target_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    point_proj = cfg.utils.project_qgis_point_coordinates(
        point, qgis_crs, target_crs
    )
    if point_proj is not False:
        try:
            if float(cfg.dialog.ui.LX_lineEdit_3.text()) > point_proj.x():
                cfg.dialog.ui.UX_lineEdit_3.setText(str(point_proj.x()))
            else:
                cfg.dialog.ui.UX_lineEdit_3.setText(
                    str(
                        cfg.dialog.ui.LX_lineEdit_3.text()
                    )
                )
                cfg.dialog.ui.LX_lineEdit_3.setText(str(point_proj.x()))
            if float(cfg.dialog.ui.LY_lineEdit_3.text()) < point_proj.y():
                cfg.dialog.ui.UY_lineEdit_3.setText(str(point_proj.y()))
            else:
                cfg.dialog.ui.UY_lineEdit_3.setText(
                    str(
                        cfg.dialog.ui.LY_lineEdit_3.text()
                    )
                )
                cfg.dialog.ui.LY_lineEdit_3.setText(str(point_proj.y()))
        except Exception as err:
            str(err)
            cfg.dialog.ui.UX_lineEdit_3.setText(str(point_proj.x()))
            cfg.dialog.ui.UY_lineEdit_3.setText(str(point_proj.y()))
        show_area()


# show area
def show_area():
    qgis_crs = cfg.util_qgis.get_qgis_crs()
    # WGS84 EPSG 4326
    target_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    try:
        upper_left = cfg.util_qgis.create_qgis_point(
            float(cfg.dialog.ui.UX_lineEdit_3.text()),
            float(cfg.dialog.ui.UY_lineEdit_3.text())
        )
        upper_left_proj = cfg.utils.project_qgis_point_coordinates(
            upper_left, target_crs, qgis_crs
        )
        lower_right = cfg.util_qgis.create_qgis_point(
            float(cfg.dialog.ui.LX_lineEdit_3.text()),
            float(cfg.dialog.ui.LY_lineEdit_3.text())
        )
        lower_right_proj = cfg.utils.project_qgis_point_coordinates(
            lower_right, target_crs, qgis_crs
        )
        add_rubber_polygon(upper_left_proj, lower_right_proj)
    except Exception as err:
        str(err)


# show hide area radio button
def show_hide_area():
    try:
        if cfg.dialog.ui.show_area_radioButton_2.isChecked():
            show_area()
        else:
            clear_canvas_poly()
    except Exception as err:
        str(err)


# check all bands
def check_all_bands():
    if cfg.dialog.ui.checkBoxs_band_1.isChecked():
        state = 0
    else:
        state = 2
    for band in range(1, 13):
        eval(
            'cfg.dialog.ui.checkBoxs_band_%i.setCheckState(%i)'
            % (band, state)
        )
    cfg.dialog.ui.ancillary_data_checkBox.setCheckState(state)
    cfg.dialog.ui.checkBoxs_band_8A.setCheckState(state)


""" Table """


# find images
def find_images():
    perform_query()


# download image metadata
def perform_query():
    product_name = cfg.dialog.ui.landsat_satellite_combo.currentText()
    date_from_qt = cfg.dialog.ui.dateEdit_from.date()
    date_to_qt = cfg.dialog.ui.dateEdit_to.date()
    date_from = date_from_qt.toPyDate().strftime('%Y-%m-%d')
    date_to = date_to_qt.toPyDate().strftime('%Y-%m-%d')
    max_cloud_cover = int(cfg.dialog.ui.cloud_cover_spinBox.value())
    result_number = int(cfg.dialog.ui.result_number_spinBox_2.value())
    cfg.logger.log.info('perform_query product_name: %s' % product_name)
    try:
        QgsRectangle(
            float(cfg.dialog.ui.UX_lineEdit_3.text()),
            float(cfg.dialog.ui.UY_lineEdit_3.text()),
            float(cfg.dialog.ui.LX_lineEdit_3.text()),
            float(cfg.dialog.ui.LY_lineEdit_3.text())
        )
    except Exception as err:
        str(err)
        cfg.mx.msg_err_3()
        return False
    cfg.ui_utils.add_progress_bar()
    output = cfg.rs.download_products.search(
        product=product_name, date_from=date_from, date_to=date_to,
        max_cloud_cover=max_cloud_cover, result_number=result_number,
        coordinate_list=[float(cfg.dialog.ui.UX_lineEdit_3.text()),
                         float(cfg.dialog.ui.UY_lineEdit_3.text()),
                         float(cfg.dialog.ui.LX_lineEdit_3.text()),
                         float(cfg.dialog.ui.LY_lineEdit_3.text())]
    )
    cfg.ui_utils.remove_progress_bar()
    if output.check:
        product_table = output.extra['product_table']
        if cfg.download_table is None:
            cfg.download_table = product_table
        else:
            cfg.download_table = cfg.rs.table_manager.stack_product_table(
                product_list=[cfg.download_table, product_table]
            )
    else:
        return False
    table = cfg.dialog.ui.download_images_tableWidget
    table.blockSignals(True)
    table.setSortingEnabled(False)
    if product_table is None:
        return False
    total_products = product_table.shape[0]
    for product in range(total_products):
        # add rows
        count = table.rowCount()
        table.setRowCount(count + 1)
        n = 0
        for field in product_table.dtype.names:
            if str(product_table[field][product]) != 'None':
                cfg.util_qt.add_table_item(
                    table, str(product_table[field][product]), count, n
                )
            n += 1
    table.setSortingEnabled(True)
    table.blockSignals(False)
    clear_canvas_poly()


# clear table
def clear_table():
    answer = cfg.util_qt.question_box(
        cfg.translate('Clear the table'),
        cfg.translate('Are you sure you want to clear the table?')
    )
    if answer:
        cfg.util_qt.clear_table(cfg.dialog.ui.download_images_tableWidget)
        cfg.download_table = None


# perform filter
def filter_table():
    table = cfg.dialog.ui.download_images_tableWidget
    text = cfg.dialog.ui.products_filter_lineEdit.text()
    items = table.findItems(text, cfg.util_qt.get_match_contains())
    count = table.rowCount()
    item_list = []
    for item in items:
        item_list.append(item.row())
    table.blockSignals(True)
    for i in range(0, count):
        table.setRowHidden(i, False)
        if i not in item_list:
            table.setRowHidden(i, True)
    table.blockSignals(False)


# remove highlighted images from table
def remove_image_from_table():
    answer = cfg.util_qt.question_box(
        cfg.translate('Remove rows'),
        cfg.translate(
            'Are you sure you want to remove highlighted rows '
            'from the table?'
        )
    )
    if answer is True:
        table = cfg.dialog.ui.download_images_tableWidget
        # list of item to remove
        rows = []
        for index in table.selectedIndexes():
            rows.append(index.row())
        selected_rows = list(set(rows))
        uid_list = []
        count = table.rowCount()
        for row in range(count):
            if row not in selected_rows:
                uid_list.append(str(table.item(row, 14).text()))
        enum_list = []
        for n, uid in enumerate(cfg.download_table.uid):
            if str(uid) in uid_list:
                enum_list.append(n)
        cfg.download_table = cfg.download_table[enum_list]
        cfg.util_qt.clear_table(table)
        table.blockSignals(True)
        table.setSortingEnabled(False)
        total_products = cfg.download_table.shape[0]
        for product in range(total_products):
            # add rows
            count = table.rowCount()
            table.setRowCount(count + 1)
            n = 0
            for field in cfg.download_table.dtype.names:
                if str(cfg.download_table[field][product]) != 'None':
                    cfg.util_qt.add_table_item(
                        table, str(cfg.download_table[field][product]),
                        count, n
                    )
                n += 1
        table.setSortingEnabled(True)
        table.blockSignals(False)
        clear_canvas_poly()


# import table file
def import_table_text():
    file = cfg.util_qt.get_open_file(
        None, cfg.translate('Select a text file of product table'), '',
        'XML (*.xml)'
    )
    if len(file) > 0:
        open_download_table(file)


# export table
def export_table_to_text():
    if cfg.dialog.ui.download_images_tableWidget.rowCount() > 0:
        saved = cfg.util_qt.get_save_file_name(
            None, cfg.translate('Export table to file'), '', '*.xml', 'xml'
        )
        if saved is not False:
            if not saved.lower().endswith('.xml'):
                saved += '.xml'
            save_download_table(saved)


# save download table
def save_download_table(file=None):
    if cfg.download_table is not None:
        if file is None:
            xml = cfg.rs.download_products.export_product_table_as_xml(
                product_table=cfg.download_table
            )
            # save to project
            cfg.project_registry[cfg.reg_download_product_table] = xml
        else:
            cfg.rs.download_products.export_product_table_as_xml(
                product_table=cfg.download_table, output_path=file
            )


# open download table
def open_download_table(file=None):
    cfg.logger.log.debug('open_download_table: %s' % str(file))
    cfg.download_table = None
    if file is None:
        # replace
        xml = cfg.project_registry[cfg.reg_download_product_table]
        if len(xml) == 0:
            return False
        temp_path = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix='.xml'
        )
        with open(temp_path, 'wb') as output_file:
            output_file.write(xml)
        try:
            imported_table = cfg.rs.download_products.import_as_xml(
                xml_path=temp_path
            )
            cfg.download_table = imported_table.extra['product_table']
        except Exception as err:
            cfg.logger.log.error(str(err))
            return False
    else:
        try:
            imported_table = cfg.rs.download_products.import_as_xml(
                xml_path=file
            )
            cfg.download_table = imported_table.extra['product_table']
        except Exception as err:
            cfg.logger.log.error(str(err))
            return False
    # add rows to table
    table = cfg.dialog.ui.download_images_tableWidget
    table.blockSignals(True)
    table.setSortingEnabled(False)
    total_products = cfg.download_table.shape[0]
    for product in range(total_products):
        # add rows
        count = table.rowCount()
        table.setRowCount(count + 1)
        n = 0
        for field in cfg.download_table.dtype.names:
            if str(cfg.download_table[field][product]) != 'None':
                cfg.util_qt.add_table_item(
                    table, str(cfg.download_table[field][product]), count, n
                )
            n += 1
    table.setSortingEnabled(True)
    table.blockSignals(False)


# display images
def display_images():
    table = cfg.dialog.ui.download_images_tableWidget
    ids = []
    for image_id in table.selectedIndexes():
        ids.append(image_id.row())
    image_ids = set(ids)
    if len(image_ids) > 0:
        progress_step = 100 / len(image_ids)
        cfg.ui_utils.add_progress_bar()
        # disable map canvas render for speed
        cfg.map_canvas.setRenderFlag(False)
        progress = 0
        for image_id in image_ids:
            sat = str(table.item(image_id, 0).text())
            if sat == cfg.rs.configurations.sentinel2:
                display_sentinel2(image_id)
            elif (sat == cfg.rs.configurations.landsat_hls
                  or sat == cfg.rs.configurations.sentinel2_hls):
                display_nasa_images(image_id)
            progress = progress + progress_step
            cfg.ui_utils.update_bar(progress, cfg.translate('Downloading ...'))
        cfg.ui_utils.remove_progress_bar()
        cfg.map_canvas.setRenderFlag(True)
        cfg.map_canvas.refresh()


# table click
def table_click():
    table = cfg.dialog.ui.download_images_tableWidget
    row = table.currentRow()
    selected_ids = []
    for tI in table.selectedIndexes():
        selected_ids.append(tI.row())
    image_ids = set(selected_ids)
    if row >= 0 and not len(image_ids) > 1:
        cfg.ui_utils.add_progress_bar()
        cfg.ui_utils.update_bar(10, cfg.translate('Downloading ...'))
        sat = str(table.item(row, 0).text())
        if sat == cfg.rs.configurations.sentinel2:
            display_sentinel2(row, True)
        elif (sat == cfg.rs.configurations.landsat_hls
              or sat == cfg.rs.configurations.sentinel2_hls):
            display_nasa_images(row, True)
        cfg.ui_utils.remove_progress_bar()


""" Download """


# download images in table
def download_images_action():
    download_images(exporter=False)


# export links
def export_links():
    download_images(exporter=True)


# download images in table
def download_images(exporter=False):
    band_list = []
    if cfg.dialog.ui.checkBoxs_band_1.isChecked():
        band_list.append('01')
    if cfg.dialog.ui.checkBoxs_band_2.isChecked():
        band_list.append('02')
    if cfg.dialog.ui.checkBoxs_band_3.isChecked():
        band_list.append('03')
    if cfg.dialog.ui.checkBoxs_band_4.isChecked():
        band_list.append('04')
    if cfg.dialog.ui.checkBoxs_band_5.isChecked():
        band_list.append('05')
    if cfg.dialog.ui.checkBoxs_band_6.isChecked():
        band_list.append('06')
    if cfg.dialog.ui.checkBoxs_band_7.isChecked():
        band_list.append('07')
    if cfg.dialog.ui.checkBoxs_band_8.isChecked():
        band_list.append('08')
    if cfg.dialog.ui.checkBoxs_band_8.isChecked():
        band_list.append('08')
    if cfg.dialog.ui.checkBoxs_band_8A.isChecked():
        band_list.append('8A')
    if cfg.dialog.ui.checkBoxs_band_9.isChecked():
        band_list.append('09')
    if cfg.dialog.ui.checkBoxs_band_10.isChecked():
        band_list.append('10')
    if cfg.dialog.ui.checkBoxs_band_11.isChecked():
        band_list.append('11')
    if cfg.dialog.ui.checkBoxs_band_12.isChecked():
        band_list.append('12')
    if cfg.dialog.ui.virtual_download_checkBox.isChecked():
        virtual_download = True
        try:
            left = float(cfg.dialog.ui.UX_lineEdit_3.text())
            top = float(cfg.dialog.ui.UY_lineEdit_3.text())
            right = float(cfg.dialog.ui.LX_lineEdit_3.text())
            bottom = float(cfg.dialog.ui.LY_lineEdit_3.text())
            extent_coordinate_list = [left, top, right, bottom]
            # TODO implement coordinate projection
            extent_coordinate_list = None
        except Exception as err:
            str(err)
            extent_coordinate_list = None
    else:
        virtual_download = False
        extent_coordinate_list = None
    proxy_host = None
    proxy_port = None
    proxy_user = None
    proxy_password = None
    cfg.util_qgis.get_qgis_proxy_settings()
    if str(cfg.proxy_enabled) == 'true' and len(cfg.proxy_host) > 0:
        if len(cfg.proxy_user) > 0:
            proxy_user = cfg.proxy_user
            proxy_password = cfg.proxy_password
            proxy_host = cfg.proxy_host
            proxy_port = cfg.proxy_port
        else:
            proxy_host = cfg.proxy_host
            proxy_port = cfg.proxy_port
    nasa_user = cfg.dialog.ui.user_earthdata_lineEdit.text()
    nasa_password = cfg.dialog.ui.password_earthdata_lineEdit.text()
    table = cfg.dialog.ui.download_images_tableWidget
    count = table.rowCount()
    if count > 0:
        output_path = cfg.util_qt.get_existing_directory(
            None, cfg.translate(
                'Download the images in the table '
                '(requires internet connection)'
            )
        )
        if output_path is not False:
            preview_box = cfg.dialog.ui.download_if_preview_in_legend_checkBox
            if preview_box.isChecked():
                uid_list = []
                for row in range(count):
                    image_id = str(table.item(row, 1).text())
                    if cfg.util_qgis.select_layer_by_name(
                            image_id, True
                    ) is not None:
                        uid_list.append(str(table.item(row, 14).text()))
                enum_list = []
                for n, uid in enumerate(cfg.download_table.uid):
                    if str(uid) in uid_list:
                        enum_list.append(n)
                filtered = cfg.download_table[enum_list]
            else:
                filtered = cfg.download_table
            cfg.ui_utils.add_progress_bar()
            output = cfg.rs.download_products.download(
                product_table=filtered, output_path=output_path,
                exporter=exporter, band_list=band_list,
                virtual_download=virtual_download,
                extent_coordinate_list=extent_coordinate_list,
                proxy_host=proxy_host, proxy_port=proxy_port,
                proxy_user=proxy_user, proxy_password=proxy_password,
                nasa_user=nasa_user, nasa_password=nasa_password
            )
            if output.check:
                if cfg.dialog.ui.preprocess_checkBox.isChecked():
                    preprocess = True
                else:
                    preprocess = False
                if cfg.dialog.ui.load_in_QGIS_checkBox.isChecked():
                    load_in_qgis = True
                else:
                    load_in_qgis = False
                if preprocess:
                    if output.extra is not None:
                        # preprocess
                        directories = output.extra['directory_paths']
                        for directory in directories:
                            cfg.image_conversion.populate_table(directory)
                            base_directory = cfg.utils.directory_name(
                                directory
                            )
                            process_directory = '%s/RT_%s' % (
                                base_directory, cfg.utils.base_name(directory)
                            )
                            cfg.image_conversion.perform_conversion(
                                output_path=process_directory,
                                load_in_qgis=load_in_qgis
                            )
                            cfg.util_qt.clear_table(
                                cfg.dialog.ui.bands_tableWidget
                            )
                else:
                    if load_in_qgis:
                        if output.paths is not None:
                            for x_path in output.paths:
                                cfg.util_qgis.add_raster_layer(x_path)
            cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


""" Additional functions """


# display granule preview
def display_sentinel2(row, preview=False):
    table = cfg.dialog.ui.download_images_tableWidget
    image_name = str(table.item(row, 1).text())
    if image_name[0:4] == 'L1C_' or image_name[0:4] == 'L2A_':
        image_id = '%s_p.jp2' % image_name
    else:
        image_id = '%s_p.jp2' % image_name
    url = str(table.item(row, 13).text())
    # image preview
    image_output = '%s/%s' % (cfg.rs.configurations.temp.dir, image_id)
    if preview is True and cfg.utils.check_file(image_output):
        preview_in_label(image_output)
        return image_output
    if cfg.utils.check_file('%s.vrt' % image_output) or cfg.utils.check_file(
            '%s.vrt' % sub(r'\.jp2$', '.png', str(image_output))
    ):
        layer = cfg.util_qgis.select_layer_by_name(image_name)
        if layer is not None:
            cfg.util_qgis.set_layer_visible(layer, True)
            cfg.util_qgis.move_layer_to_top(layer)
        else:
            cfg.util_qgis.add_raster_layer('%s.vrt' % image_output, image_name)
    else:
        if 'storage.googleapis.com' in url:
            check, output = cfg.rs.download_tools.download_file(
                url, image_output, timeout=2
            )
            if check is not False:
                if preview is True:
                    preview_in_label(image_output)
                    return image_output
                min_lat = str(table.item(row, 7).text())
                min_lon = str(table.item(row, 8).text())
                max_lat = str(table.item(row, 9).text())
                max_lon = str(table.item(row, 10).text())
                onthefly_georef_image(
                    image_output, '%s.vrt' % image_output, min_lon, max_lon,
                    min_lat, max_lat
                )
                if cfg.utils.check_file('%s.vrt' % image_output):
                    cfg.util_qgis.add_raster_layer(
                        '%s.vrt' % image_output, image_name
                    )


# display images
def display_nasa_images(row, preview=False):
    table = cfg.dialog.ui.download_images_tableWidget
    sat = str(table.item(row, 0).text())
    image_id = str(table.item(row, 1).text())
    min_lat = str(table.item(row, 7).text())
    min_lon = str(table.item(row, 8).text())
    max_lat = str(table.item(row, 9).text())
    max_lon = str(table.item(row, 10).text())
    url = str(table.item(row, 13).text())
    # image preview
    image_output = '%s/%s_thumb.jpg' % (
        cfg.rs.configurations.temp.dir, image_id
    )
    if preview is True and cfg.utils.check_file(image_output):
        preview_in_label(image_output)
        return image_output
    elif cfg.utils.check_file(
            '%s/%s.vrt' % (cfg.rs.configurations.temp.dir, image_id)
    ):
        layer = cfg.util_qgis.select_layer_by_name(image_id)
        if layer is not None:
            cfg.util_qgis.set_layer_visible(layer, True)
            cfg.util_qgis.move_layer_to_top(layer)
        else:
            r = cfg.util_qgis.add_raster_layer(
                '%s/%s.vrt' % (cfg.rs.configurations.temp.dir, image_id)
            )
            cfg.util_qgis.set_raster_color_composite(r, 1, 2, 3)
    else:
        download_nasa_thumbnail(
            image_id, min_lat, min_lon, max_lat, max_lon, url, sat, preview
        )
        if cfg.utils.check_file(
                '%s/%s.vrt' % (cfg.rs.configurations.temp.dir, image_id)
        ):
            r = cfg.util_qgis.add_raster_layer(
                '%s//%s.vrt' % (cfg.rs.configurations.temp.dir, image_id)
            )
            cfg.util_qgis.set_raster_color_composite(r, 1, 2, 3)


# display image in label
def preview_in_label(image_path):
    temp_image = sub(r'\.jp2$', '.png', str(image_path))
    if image_path.endswith('.jp2') and not cfg.utils.check_file(temp_image):
        cfg.utils.get_gdal_path_for_mac()
        # georeference thumbnail
        com = ('%sgdal_translate %s %s  -of PNG'
               % (cfg.qgis_registry[cfg.reg_gdal_path], image_path,
                  temp_image))
        if cfg.system_platform != 'Windows':
            com = split(com)
        try:
            if cfg.system_platform == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                sub_process = subprocess.Popen(
                    com, shell=False, startupinfo=startupinfo,
                    stdin=subprocess.DEVNULL
                )
            else:
                sub_process = subprocess.Popen(com, shell=False)
            sub_process.wait()
        except Exception as err:
            str(err)
    image_path = temp_image
    label = cfg.dialog.ui.image_preview_label
    pixmap = QPixmap(image_path).scaled(300, 300)
    label.setPixmap(pixmap)
    return image_path


# add OpenStreetMap to the map as described in
# https://wiki.openstreetmap.org/wiki/QGIS
# (© OpenStreetMap contributors. The cartography is licensed as CC BY-SA)
def display_osm():
    temp_path = cfg.rs.configurations.temp.temporary_file_path(
        name_suffix='.xml'
    )
    xml = """<GDAL_WMS>
        <Service name="TMS">
        <ServerUrl>http://tile.openstreetmap.org/${z}/${x}/${y}.png</ServerUrl>
        </Service>
        <DataWindow>
            <UpperLeftX>-20037508.34</UpperLeftX>
            <UpperLeftY>20037508.34</UpperLeftY>
            <LowerRightX>20037508.34</LowerRightX>
            <LowerRightY>-20037508.34</LowerRightY>
            <TileLevel>18</TileLevel>
            <TileCountX>1</TileCountX>
            <TileCountY>1</TileCountY>
            <YOrigin>top</YOrigin>
        </DataWindow>
        <Projection>EPSG:3857</Projection>
        <BlockSizeX>256</BlockSizeX>
        <BlockSizeY>256</BlockSizeY>
        <BandsCount>3</BandsCount>
        </GDAL_WMS>
        """
    with open(temp_path, 'w') as output_file:
        output_file.write(xml)
    cfg.util_qgis.add_raster_layer(temp_path, 'OpenStreetMap')


# image georeferenced on the fly based on UL and LR
def onthefly_georef_image(
        input_image, output_vrt, min_lon, max_lon, min_lat, max_lat
):
    center_lon = (float(min_lon) + float(max_lon)) / 2
    center_lat = (float(min_lat) + float(max_lat)) / 2
    # calculate UTM zone (adapted from
    # http://stackoverflow.com/questions/9186496/determining-utm-zone-to-convert-from-longitude-latitude)
    zone = 1 + int((center_lon + 180) / 6)
    # exceptions
    if 3.0 <= center_lon < 12.0 and 56.0 <= center_lat < 64.0:
        zone = 32
    elif 0.0 <= center_lon < 9.0 and 72.0 <= center_lat < 84.0:
        zone = 31
    elif 9.0 <= center_lon < 21.0 and 72.0 <= center_lat < 84.0:
        zone = 33
    elif 21.0 <= center_lon < 33.0 and 72.0 <= center_lat < 84.0:
        zone = 35
    elif 33.0 <= center_lon < 42.0 and 72.0 <= center_lat < 84.0:
        zone = 37
    upper_left = cfg.util_qgis.create_qgis_point(
        float(min_lon),
        float(max_lat)
    )
    lower_right = cfg.util_qgis.create_qgis_point(
        float(max_lon),
        float(min_lat)
    )
    # WGS84 EPSG 4326
    wgs84 = QgsCoordinateReferenceSystem('EPSG:4326')
    utm_crs = QgsCoordinateReferenceSystem()
    utm_crs.createFromProj4(
        '+proj=utm +zone=' + str(zone) + ' +datum=WGS84 +units=m +no_defs'
    )
    upper_left_proj = cfg.utils.project_qgis_point_coordinates(
        upper_left, wgs84, utm_crs
    )
    lower_right_proj = cfg.utils.project_qgis_point_coordinates(
        lower_right, wgs84, utm_crs
    )
    if upper_left_proj is not False and lower_right_proj is not False:
        cfg.utils.get_gdal_path_for_mac()
        # georeference thumbnail
        com = (('%sgdal_translate -of VRT -a_ullr %s %s %s %s -a_srs '
                '"+proj=utm +zone=%s +datum=WGS84 +units=m +no_defs" %s %s')
               % (cfg.qgis_registry[cfg.reg_gdal_path],
                  str(upper_left_proj.x()), str(upper_left_proj.y()),
                  str(lower_right_proj.x()), str(lower_right_proj.y()),
                  str(zone), input_image, output_vrt))
        if cfg.system_platform != 'Windows':
            com = split(com)
        try:
            if cfg.system_platform == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                process = subprocess.Popen(
                    com, shell=False, startupinfo=startupinfo,
                    stdin=subprocess.DEVNULL
                )
            else:
                process = subprocess.Popen(com, shell=False)
            process.wait()
        except Exception as err:
            str(err)


# download thumbnail
def download_nasa_thumbnail(
        image_id, min_lat, min_lon, max_lat, max_lon, url, sat, preview=False
):
    image_output = '%s/%s_thumb.jpg' % (
        cfg.rs.configurations.temp.dir, image_id
    )
    check = False
    if (sat == cfg.rs.configurations.landsat_hls
            or sat == cfg.rs.configurations.sentinel2_hls):
        check, output = cfg.rs.download_tools.download_file(
            url, image_output, timeout=2
        )
    if check is True:
        if preview is True:
            preview_in_label(image_output)
            return image_output
        onthefly_georef_image(
            image_output,
            '%s/%s.vrt' % (cfg.rs.configurations.temp.dir, image_id), min_lon,
            max_lon, min_lat, max_lat
        )
