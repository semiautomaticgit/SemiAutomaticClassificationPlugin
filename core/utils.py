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


import base64
import ctypes
import datetime
import json
import os
import random
import subprocess
import time
from pathlib import Path
from packaging.version import parse
import numpy as np

from PyQt5.QtCore import Qt, QUrl, QByteArray
from PyQt5.QtGui import QColor
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWidgets import qApp
from osgeo import ogr, osr
from qgis.core import (
    QgsNetworkAccessManager, QgsSymbol,
    QgsRendererCategory, QgsCategorizedSymbolRenderer,
    QgsPalettedRasterRenderer, QgsCoordinateReferenceSystem
)
from scipy.spatial.distance import cdist

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

""" download functions """


# check Remotior Sensus version
def check_remotior_sensus_version():
    request = QNetworkRequest(
        QUrl('https://pypi.org/pypi/remotior_sensus/json')
    )
    cfg.remotior_reply = QgsNetworkAccessManager.instance().get(request)
    cfg.remotior_reply.finished.connect(remotior_label)


# check Remotior Sensus version
def remotior_label():
    try:
        package = json.loads(
            QByteArray(cfg.remotior_reply.readAll()).data().decode('utf-8')
        )
        latest_version = package['info']['version']
        from remotior_sensus import __version__ as version
        if parse(latest_version) > parse(version):
            cfg.dock_class_dlg.ui.rs_version.setText(
                'A new version of Remotior Sensus is available.'
                '\nPlease update the Remotior Sensus package.'
            )
    except Exception as err:
        return str(err)


# download html file
def download_html(url, second_url=None):
    request = QNetworkRequest(QUrl(url))
    cfg.second_url = second_url
    cfg.first_reply = QgsNetworkAccessManager.instance().get(request)
    cfg.first_reply.finished.connect(reply_in_text_browser)


# load reply in text browser
# noinspection PyUnresolvedReferences
def reply_in_text_browser():
    cfg.first_reply.deleteLater()
    html_data = cfg.first_reply.readAll().data()
    html = bytes.decode(html_data)
    # GitHub file not found
    if '<h1>404</h1>' in html:
        second_request = QNetworkRequest(QUrl(cfg.second_url))
        cfg.second_reply = QgsNetworkAccessManager.instance().get(
            second_request
        )
        cfg.second_reply.finished.connect(reply_in_text_browser_second_request)
    if len(html) > 0:
        cfg.dock_class_dlg.ui.main_textBrowser.clear()
        cfg.dock_class_dlg.ui.main_textBrowser.setHtml(html)
    cfg.first_reply.finished.disconnect()
    cfg.first_reply.abort()
    cfg.first_reply.close()


# load reply in text browser
# noinspection PyUnresolvedReferences
def reply_in_text_browser_second_request():
    cfg.second_reply.deleteLater()
    html_data = cfg.second_reply.readAll().data()
    html = bytes.decode(html_data)
    if len(html) > 0:
        cfg.dock_class_dlg.ui.main_textBrowser.clear()
        cfg.dock_class_dlg.ui.main_textBrowser.setHtml(html)
    else:
        html_text_f = open('%s/ui/welcome.html' % cfg.plugin_dir, 'r')
        html_text = html_text_f.read()
        cfg.dock_class_dlg.ui.main_textBrowser.clear()
        cfg.dock_class_dlg.ui.main_textBrowser.setHtml(html_text)
        html_text_f.close()
    cfg.second_reply.finished.disconnect()
    cfg.second_reply.abort()
    cfg.second_reply.close()


""" encrypt functions """


# encrypt password
def encrypt_password(password):
    e = base64.b64encode(bytes(password, 'utf-8'))
    return str(e)


# decrypt password
def decrypt_password(password):
    if password is not None:
        d = base64.b64decode(password)
        return d
    else:
        return ''


""" time functions """


# get time
def get_time():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')


# get date
def get_date():
    return datetime.datetime.now().strftime('%Y_%m_%d')


""" QGIS map and symbology functions """


# refresh extent combo
def refresh_raster_extent_combo():
    layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
    cfg.dialog.ui.raster_extent_combo.clear()
    cfg.dialog.raster_extent_combo(cfg.union_extent)
    cfg.dialog.raster_extent_combo(cfg.map_extent)
    cfg.dialog.raster_extent_combo(cfg.intersection_extent)
    cfg.dialog.raster_extent_combo(cfg.custom_extent)
    for layer in sorted(layers, key=lambda c: c.name()):
        if layer.type() == cfg.util_qgis.get_qgis_map_raster():
            cfg.dialog.raster_extent_combo(layer.name())


# refresh raster align combo
def refresh_raster_align_combo():
    layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
    cfg.dialog.ui.raster_extent_combo_2.clear()
    cfg.dialog.raster_extent_combo_2(cfg.default_align)
    for layer in sorted(layers, key=lambda c: c.name()):
        if layer.type() == cfg.util_qgis.get_qgis_map_raster():
            cfg.dialog.raster_extent_combo_2(layer.name())


# refresh classification combo
def refresh_raster_layer():
    ls = cfg.util_qgis.get_qgis_project().mapLayers().values()
    cfg.dialog.ui.classification_name_combo.clear()
    cfg.dialog.ui.classification_name_combo_2.clear()
    cfg.dialog.ui.classification_report_name_combo.clear()
    cfg.dialog.ui.classification_vector_name_combo.clear()
    cfg.dialog.ui.reclassification_name_combo.clear()
    cfg.dialog.ui.classification_name_combo_4.clear()
    cfg.dialog.ui.reference_raster_name_combo.clear()
    cfg.dialog.ui.raster_align_comboBox.clear()
    for layer in sorted(ls, key=lambda c: c.name()):
        if layer.type() == cfg.util_qgis.get_qgis_map_raster():
            if layer.bandCount() == 1:
                cfg.dialog.classification_layer_combo(layer.name())
                cfg.dialog.classification_layer_combo_2(layer.name())
                cfg.dialog.classification_report_combo(layer.name())
                cfg.dialog.classification_to_vector_combo(layer.name())
                cfg.dialog.reclassification_combo(layer.name())
                cfg.dialog.cloud_mask_raster_combo(layer.name())
                cfg.dialog.reference_raster_combo(layer.name())
                cfg.dialog.project_raster_combo(layer.name())


# refresh vector combo
def refresh_vector_layer():
    cfg.dialog.ui.vector_name_combo.blockSignals(True)
    ls = cfg.util_qgis.get_qgis_project().mapLayers().values()
    cfg.dialog.ui.shapefile_comboBox.clear()
    cfg.dialog.ui.vector_name_combo.clear()
    for layer in sorted(ls, key=lambda c: c.name()):
        if layer.type() == cfg.util_qgis.get_qgis_map_vector():
            if ((layer.wkbType() == cfg.util_qgis.get_qgis_wkb_types().Polygon)
                    or (layer.wkbType() ==
                        cfg.util_qgis.get_qgis_wkb_types().MultiPolygon)):
                cfg.dialog.shape_clip_combo(layer.name())
                cfg.dialog.vector_to_raster_combo(layer.name())
    cfg.dialog.ui.vector_name_combo.blockSignals(False)
    refresh_vector_fields()


# reference layer name
def refresh_vector_fields():
    reference_layer = cfg.dialog.ui.vector_name_combo.currentText()
    cfg.dialog.ui.field_comboBox.clear()
    cfg.dialog.ui.select_shapefile_label.setText('')
    cfg.dialog.ui.MC_ID_combo.clear()
    cfg.dialog.ui.MC_Info_combo.clear()
    cfg.dialog.ui.C_ID_combo.clear()
    cfg.dialog.ui.C_Info_combo.clear()
    layer = cfg.util_qgis.select_layer_by_name(reference_layer)
    try:
        if layer.type() == cfg.util_qgis.get_qgis_map_vector():
            f = layer.dataProvider().fields()
            for i in f:
                if str(i.typeName()).lower() != 'string':
                    cfg.dialog.reference_field_combo(str(i.name()))
    except Exception as err:
        return str(err)


# set vector symbology
def vector_symbol(layer, value_name_dictionary, value_color_dictionary):
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    symbol.setColor(QColor('#000000'))
    classes = [
        QgsRendererCategory(0, symbol, '0 - ' + cfg.translate('Unclassified'))]
    for value in value_name_dictionary:
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol.setColor(QColor(value_color_dictionary[value]))
        renderer = QgsRendererCategory(
            value, symbol, '%s - %s' % (
                str(value), value_name_dictionary[value]
            )
        )
        classes.append(renderer)
    raster = QgsCategorizedSymbolRenderer('DN', classes)
    layer.setRenderer(raster)


# set classification symbology
def classification_raster_symbol(
        classification_layer, value_name_dictionary, value_color_dictionary
):
    # class list value, color, name for ramp
    class_list = [QgsPalettedRasterRenderer.Class(
        0, QColor('#000000'), '0 - ' + cfg.translate('Unclassified')
    )]
    for value in value_name_dictionary:
        class_list.append(
            QgsPalettedRasterRenderer.Class(
                value, QColor(value_color_dictionary[value]),
                '%s - %s' % (str(value), value_name_dictionary[value])
            )
        )
    # create the renderer
    renderer = QgsPalettedRasterRenderer(
        classification_layer.dataProvider(), 1, class_list
    )
    # apply the renderer to classLayer
    classification_layer.setRenderer(renderer)
    # refresh legend
    if hasattr(classification_layer, 'setCacheImage'):
        classification_layer.setCacheImage(None)
    classification_layer.triggerRepaint()
    cfg.util_qgis.refresh_layer_symbology(classification_layer)


# Define raster symbology
def raster_symbol_generic(
        raster_layer, nodata_tag='0', raster_unique_value_list=None
):
    if raster_unique_value_list is None:
        unique_value_list = raster_unique_value_list
    else:
        unique_value_list = raster_unique_value_list
    try:
        max_value = max(unique_value_list)
    except Exception as err:
        str(err)
        max_value = 1
    # Color list for ramp
    color_list = [QgsPalettedRasterRenderer.Class(
        0, QColor(0, 0, 0), nodata_tag
    )]
    for i in unique_value_list:
        if i > max_value / 2:
            c = QColor(
                int(255 * (i / max_value)),
                int(255 * (1 - (i / max_value))),
                int(255 * (1 - (i / max_value)))
            )
            color_list.append(
                QgsPalettedRasterRenderer.Class(i, c, str(i))
            )
        elif i > 0:
            c = QColor(
                int(255 * (i / max_value)),
                int(255 * (i / max_value)),
                int(255 * (1 - (i / max_value)))
            )
            color_list.append(
                QgsPalettedRasterRenderer.Class(i, c, str(i))
            )
    # create the renderer
    try:
        renderer = QgsPalettedRasterRenderer(
            raster_layer.dataProvider(), 1, color_list
        )
    except Exception as err:
        str(err)
        renderer = None
    # Apply the renderer to rasterLayer
    raster_layer.setRenderer(renderer)
    # refresh legend
    if hasattr(raster_layer, 'setCacheImage'):
        raster_layer.setCacheImage(None)
    raster_layer.triggerRepaint()
    cfg.util_qgis.refresh_layer_symbology(raster_layer)


""" process functions """


# create value list from text
def text_to_value_list(text):
    values = []
    if ',' in text:
        commas = text.split(',')
    elif '-' in text:
        dashes = text.split('-')
        for val in range(int(dashes[0]), int(dashes[-1]) + 1):
            values.append(int(val))
        commas = []
    else:
        values.append(int(text))
        commas = []
    for part in commas:
        if '-' in part:
            dashes = part.split('-')
            for val in range(int(dashes[0]), int(dashes[-1]) + 1):
                values.append(int(val))
        else:
            values.append(int(part))
    return np.unique(values).tolist()


# check if the clicked point is inside the image
def check_point_in_image(
        point, bandset_number=None, point_crs=None,
        output_crs=None
):
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    bandset_x = cfg.bandset_catalog.get(bandset_number)
    band_count = bandset_x.get_band_count()
    if band_count == 0:
        return False
    cfg.logger.log.debug(
        'point: %s; bandset_number: %s' % (str(point), str(bandset_number))
    )
    band_crs = str(
        cfg.bandset_catalog.get_bandset(bandset_number).bands[0].crs
    )
    band_left = cfg.bandset_catalog.get_bandset(bandset_number).bands[0].left
    band_top = cfg.bandset_catalog.get_bandset(bandset_number).bands[0].top
    band_right = cfg.bandset_catalog.get_bandset(bandset_number).bands[0].right
    band_bottom = cfg.bandset_catalog.get_bandset(bandset_number).bands[
        0].bottom
    if point_crs is None:
        point_crs = cfg.util_qgis.get_qgis_crs().toWkt()
    cfg.logger.log.debug(
        'point_crs: %s; band_crs: %s' % (str(point_crs), str(band_crs))
    )
    if band_crs is not None and point_crs is not None:
        if cfg.util_gdal.compare_crs(point_crs, band_crs) is False:
            try:
                # noinspection PyTypeChecker
                point = project_qgis_point_coordinates(
                    point, point_crs, band_crs
                )
                point_crs = band_crs
                if point is False:
                    cfg.util_qgis.set_qgis_crs(band_crs)
                    cfg.logger.log.error('unable to project point')
                    return False
            # Error latitude or longitude exceeded limits
            except Exception as err:
                cfg.logger.log.error(str(err))
                return False
    if (point.x() > band_right or point.x() < band_left
            or point.y() > band_top or point.y() < band_bottom):
        cfg.logger.log.debug('point check failed')
        return False
    if output_crs is not None:
        if cfg.util_gdal.compare_crs(point_crs, output_crs) is False:
            try:
                point = project_qgis_point_coordinates(
                    point, point_crs, output_crs
                )
                if point is False:
                    cfg.logger.log.error('unable to project point')
                    return False
            # Error latitude or longitude exceeded limits
            except Exception as err:
                cfg.logger.log.error(str(err))
                return False
    cfg.logger.log.debug('point check successful')
    return point


# Project point coordinates
def project_qgis_point_coordinates(
        point, input_coordinates, output_coordinates
):
    try:
        # spatial reference
        input_sr = osr.SpatialReference()
        try:
            input_sr.ImportFromWkt(input_coordinates.toWkt())
        except Exception as err:
            input_sr.ImportFromWkt(input_coordinates)
            str(err)
        output_sr = osr.SpatialReference()
        try:
            output_sr.ImportFromWkt(output_coordinates.toWkt())
        except Exception as err:
            output_sr.ImportFromWkt(output_coordinates)
            str(err)
        # required by GDAL 3 coordinate order
        try:
            input_sr.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            output_sr.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        except Exception as err:
            str(err)
        # Coordinate Transformation
        transformation = osr.CoordinateTransformation(input_sr, output_sr)
        point_proj = ogr.Geometry(ogr.wkbPoint)
        point_proj.AddPoint(point.x(), point.y())
        point_proj.Transform(transformation)
        point_qgis = cfg.util_qgis.create_qgis_point(
            point_proj.GetX(), point_proj.GetY()
        )
        return point_qgis
    except Exception as err:
        str(err)
        return False


# calculate the distance between points in array
def pair_point_distance(numpy_array):
    return cdist(numpy_array, numpy_array)


# calculate random points in grid
def random_points_in_grid(point_number, x_min, x_max, y_min, y_max):
    x_coordinates = np.random.uniform(x_min, x_max, point_number)
    y_coordinates = np.random.uniform(y_min, y_max, point_number)
    points = list(zip(x_coordinates, y_coordinates))
    return points


# calculate random points with condition
def random_points_with_condition(
        raster_path, point_number, condition, x_min, y_top
):
    # get pixel size
    x_size, y_size = cfg.util_gdal.get_pixel_size(raster_path)
    points = []
    # band array
    _array = cfg.util_gdal.read_raster(raster_path)
    condition = condition.replace(
        cfg.qgis_registry[cfg.reg_raster_variable_name], '_array'
    )
    arr = np.argwhere(eval(condition))
    rng = np.random.default_rng()
    try:
        pixels = rng.choice(arr, size=point_number)
    except Exception as err:
        cfg.logger.log.error(str(err))
        return None
    for pixel in pixels.tolist():
        points.append(
            [x_min + pixel[1] * x_size + x_size / 2,
             y_top - pixel[0] * y_size - y_size / 2]
        )
    return points


# create KML from map
# noinspection SpellCheckingInspection
def create_kml_from_map():
    cfg.ui_utils.add_progress_bar()
    cfg.ui_utils.update_bar(10)
    ext1 = cfg.map_canvas.extent()
    qgis_crs = cfg.util_qgis.get_qgis_crs()
    crs_wgs_84 = QgsCoordinateReferenceSystem(4326)
    cfg.util_qgis.set_qgis_crs(crs_wgs_84)
    cfg.map_canvas.refreshAllLayers()
    qApp.processEvents()
    cfg.ui_utils.update_bar(30)
    time.sleep(1)
    qApp.processEvents()
    ext = cfg.map_canvas.extent()
    # date time for temp name
    _time = get_time()
    png = '%s/%sSCP_kml.png' % (cfg.temp_dir, _time)
    kml = '%s/SCP_kml.kml' % cfg.temp_dir
    cfg.map_canvas.setCanvasColor(Qt.transparent)
    cfg.map_canvas.saveAsImage(png)
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
         <kml xmlns="http://www.opengis.net/kml/2.2">
          <GroundOverlay>
           <name>%s</name>
           <Icon>
            <href>%s</href>
           </Icon>
           <LatLonBox>
           <north>%.10f</north>
           <south>%.10f</south>
           <east>%.10f</east>
           <west>%.10f</west>
           </LatLonBox>
           <Camera>       
            <longitude>%.10f</longitude>       
            <latitude>%.10f</latitude>       
           <altitude>5000</altitude>
        </Camera>
          </GroundOverlay>
         </kml>
        '''
    source = xml % (
        'SCP_kml', '%sSCP_kml.png' % _time, ext.yMaximum(), ext.yMinimum(),
        ext.xMaximum(),
        ext.xMinimum(), (ext.xMaximum() + ext.xMinimum()) / 2,
        (ext.yMinimum() + ext.yMaximum()) / 2)
    layer = open(kml, 'w')
    try:
        layer.write(source)
        layer.close()
    except Exception as err:
        str(err)
    if check_file(kml):
        if cfg.system_platform == 'Darwin':
            subprocess.call(('open', kml))
        elif cfg.system_platform == 'Windows':
            os.startfile(kml)
        else:
            subprocess.call(('xdg-open', kml))
    cfg.util_qgis.set_qgis_crs(qgis_crs)
    cfg.map_canvas.setExtent(ext1)
    cfg.map_canvas.refreshAllLayers()
    cfg.ui_utils.update_bar(100)
    cfg.ui_utils.remove_progress_bar()


""" raster color composite functions """


# set RGB color composite
def set_rgb_color_composite(composite=None):
    if ((len(cfg.rgb_combo.currentText()) > 0
         and cfg.rgb_combo.currentText() != '-') or composite is not None):
        try:
            if composite is None:
                composite = cfg.rgb_combo.currentText()
            cfg.logger.log.debug(
                'set_rgb_color_composite rgb: %s' % str(composite)
            )
            if composite is not None:
                check = create_rgb_color_composite(composite)
                if check is True:
                    if composite not in cfg.project_registry[cfg.reg_rgb_list]:
                        cfg.project_registry[cfg.reg_rgb_list].append(
                            composite
                        )
                        cfg.project_registry[cfg.reg_rgb_list] = list(
                            set(cfg.project_registry[cfg.reg_rgb_list])
                        )
                    cfg.rgb_composite.rgb_table_from_list(
                        cfg.project_registry[cfg.reg_rgb_list]
                    )
                    return True
                else:
                    return False
            else:
                return False
        except Exception as err:
            if 'string index' not in str(err):
                cfg.logger.log.error(str(err))
                cfg.mx.msg_err_4()
                return False


# create RGB color composite
def create_rgb_color_composite(color_composite, bandset_number=None):
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    cfg.logger.log.debug(
        'create_rgb_color_composite bandset: %s' % bandset_number
    )
    virtual_raster_name = '%s %s' % (
        cfg.virtual_bandset_name, str(bandset_number))
    if bandset_number in cfg.virtual_bandset_dict:
        layer = cfg.util_qgis.select_layer_by_name(virtual_raster_name, True)
    else:
        bandset_x = cfg.bandset_catalog.get(bandset_number)
        band_count = bandset_x.get_band_count()
        if band_count == 0:
            cfg.logger.log.debug('empty bandset')
            return False
        # create temporary virtual raster
        virtual_raster_path = cfg.bandset_catalog.create_virtual_raster(
            bandset_number=bandset_number
        )
        cfg.util_qgis.remove_layer_by_name(virtual_raster_name)
        layer = cfg.iface.addRasterLayer(
            virtual_raster_path,
            virtual_raster_name
        )
    # get band numbers
    composite = str(color_composite).split(',')
    if len(composite) == 1:
        composite = str(color_composite).split('-')
    if len(composite) == 1:
        composite = str(color_composite).split(';')
    if len(composite) == 1:
        composite = str(color_composite)
    if layer is None:
        del cfg.virtual_bandset_dict[bandset_number]
        cfg.logger.log.error('create_rgb_color_composite')
        return False
    elif len(composite) < 3:
        cfg.logger.log.error('create_rgb_color_composite')
        return False
    else:
        cfg.virtual_bandset_dict[bandset_number] = layer
        bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
        count = bandset_x.get_band_count()
        try:
            if int(composite[0]) > count:
                composite[0] = count
            if int(composite[1]) > count:
                composite[1] = count
            if int(composite[2]) > count:
                composite[2] = count
        except Exception as err:
            cfg.logger.log.error(str(err))
            return False
        cfg.logger.log.error(
            'create_rgb_color_composite: %s-%s-%s'
            % (str(composite[0]), str(composite[1]), str(composite[2]))
        )
        qApp.processEvents()
        cfg.util_qgis.set_raster_color_composite(
            layer, int(composite[0]), int(composite[1]), int(composite[2])
        )
        return True


""" general functions """


# read variables from project instance
def read_project_variables():
    for r in cfg.project_registry:
        try:
            cfg.project_registry[r] = cfg.util_qgis.read_project_variable(
                r, cfg.project_registry[r]
            )
        except Exception as err:
            cfg.logger.log.debug('error: %s' % str(err))
    cfg.logger.log.debug('project_registry: %s' % str(cfg.project_registry))
    # set vegetation index calculation checkbox state
    cfg.dock_class_dlg.ui.display_cursor_checkBox.setCheckState(
        int(cfg.project_registry[cfg.reg_index_calculation_check])
    )
    # set custom index
    cfg.dock_class_dlg.ui.custom_index_lineEdit.setText(
        cfg.project_registry[cfg.reg_custom_index_calculation]
    )
    # set RGB list
    cfg.util_qt.set_combobox_items(
        cfg.rgb_combo, cfg.project_registry[cfg.reg_rgb_list]
    )
    # set signature calculation checkbox state
    cfg.dock_class_dlg.ui.signature_checkBox.setCheckState(
        int(cfg.project_registry[cfg.reg_signature_calculation_check])
    )
    cfg.dialog.ui.signature_checkBox2.setCheckState(
        int(cfg.project_registry[cfg.reg_signature_calculation_check])
    )
    # set rapid ROI checkbox state
    cfg.dock_class_dlg.ui.rapid_ROI_checkBox.setCheckState(
        int(cfg.project_registry[cfg.reg_rapid_roi_check])
    )
    # set save training input
    cfg.dock_class_dlg.ui.save_input_checkBox.setCheckState(
        int(cfg.project_registry[cfg.reg_save_training_input_check])
    )
    # rapid ROI band
    cfg.dock_class_dlg.ui.rapidROI_band_spinBox.setValue(
        int(cfg.project_registry[cfg.reg_roi_main_band])
    )
    # max ROI width
    cfg.max_roi_width_spin.setValue(
        int(cfg.project_registry[cfg.reg_roi_max_width])
    )
    # min ROI size
    cfg.roi_min_size_spin.setValue(
        int(cfg.project_registry[cfg.reg_roi_min_size])
    )
    # ROI range radius
    cfg.Range_radius_spin.setValue(
        float(cfg.project_registry[cfg.reg_roi_range_radius])
    )
    # ROI class ID field
    cfg.dock_class_dlg.ui.ROI_ID_spin.setValue(
        int(cfg.project_registry[cfg.reg_roi_class_id])
    )
    # ROI class info field
    cfg.dock_class_dlg.ui.ROI_Class_line.setText(
        cfg.project_registry[cfg.reg_roi_class_name]
    )
    # ROI macroclass ID field
    cfg.dock_class_dlg.ui.ROI_Macroclass_ID_spin.setValue(
        int(cfg.project_registry[cfg.reg_roi_macroclass_id])
    )
    # ROI macroclass info field
    cfg.dock_class_dlg.ui.ROI_Macroclass_line.setText(
        cfg.project_registry[cfg.reg_roi_macroclass_name]
    )
    # restore active bandset number
    active_bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    # bandset restore
    for bandset_number in range(
            1, cfg.project_registry[cfg.reg_bandset_count] + 1
    ):
        cfg.logger.log.debug('bandset restore: %s' % str(bandset_number))
        bandset_key = '%s%s' % (cfg.reg_bandset, bandset_number)
        # import xml
        xml_file = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix='.xml'
        )
        xml = cfg.util_qgis.read_project_variable(bandset_key, '')
        with open(xml_file, 'w') as output_file:
            output_file.write(xml)
        # add empty bandset
        cfg.bst.add_band_set_tab(position=bandset_number)
        try:
            cfg.bandset_catalog.import_bandset_from_xml(
                bandset_number=bandset_number, xml_path=xml_file
            )
        except Exception as err:
            str(err)
        cfg.bst.band_set_to_table(bandset_number)
    cfg.dialog.ui.bandset_number_spinBox.setValue(active_bandset_number)
    # rgb list
    cfg.rgb_composite.rgb_table_from_list(
        cfg.project_registry[cfg.reg_rgb_list]
    )
    # training path restore
    if len(cfg.project_registry[cfg.reg_training_input_path]) > 0:
        cfg.scp_dock.open_signature_catalog_file(
            cfg.project_registry[cfg.reg_training_input_path],
            cfg.project_registry[cfg.reg_training_bandset_number]
        )
    # download table restore
    cfg.download_products.open_download_table()


# find available RAM
# noinspection SpellCheckingInspection
def find_available_ram():
    try:
        if cfg.system_platform == 'Windows':
            class GlobalMemoryStatus(ctypes.Structure):
                _fields_ = [
                    ('length', ctypes.c_ulong), ('memoryLoad', ctypes.c_ulong),
                    ('totalRam', ctypes.c_ulong),
                    ('availPhys', ctypes.c_ulonglong),
                    ('totalPageFile', ctypes.c_ulonglong),
                    ('availPageFile', ctypes.c_ulonglong),
                    ('totalVirt', ctypes.c_ulonglong),
                    ('availVirt', ctypes.c_ulonglong),
                    ('availExVirt', ctypes.c_ulonglong)
                ]

            memory_status = GlobalMemoryStatus()
            ctypes.windll.kernel32.GlobalMemoryStatus(
                ctypes.byref(memory_status)
            )
            ram_value = memory_status.totalRam
            cfg.qgis_registry[cfg.reg_ram_value] = int(
                (ram_value / 1048576) / 2
            )
        elif cfg.system_platform == 'Darwin':
            cfg.qgis_registry[cfg.reg_ram_value] = 2048
        else:
            with open('/proc/meminfo') as info:
                for line in info:
                    if line.startswith('MemTotal'):
                        ram_value = line.split()[1]
                        break
            cfg.qgis_registry[cfg.reg_ram_value] = int(
                (int(ram_value) / 1000) / 2
            )
        cfg.dialog.ui.RAM_spinBox.setValue(
            cfg.qgis_registry[cfg.reg_ram_value]
        )
    except Exception as err:
        str(err)


# find available processors
def find_available_processors():
    try:
        threads = os.cpu_count()
        cfg.dialog.ui.CPU_spinBox.setValue(int((threads + 1) / 2))
    except Exception as err:
        str(err)
        cfg.dialog.ui.CPU_spinBox.setValue(2)


# numpy array from list
def numpy_array_from_list(values):
    return np.array(values)


# get random integer
def random_integer(min, max):
    return random.randint(min, max)


# get random color
def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return '#%02x%02x%02x' % (r, g, b)


# remove file
def remove_file(file_path):
    os.remove(file_path)


# check if file exists
def check_file(file_path):
    return os.path.isfile(file_path)


# get parent directory name
def directory_name(file_path):
    return os.path.dirname(file_path)


# get base name
def base_name(file_path):
    return os.path.basename(file_path)


# relative path
def absolute_to_relative(path, root=None):
    p = Path(path)
    try:
        relative = p.relative_to(root)
    except Exception as err:
        str(err)
        relative = p
    return relative.as_posix()


# absolute path
def relative_to_absolute_path(path, root=None):
    if root is None:
        absolute = path
    else:
        absolute = '/'.join([root, path]).replace('\\', '/').replace(
            '//', '/'
        ).replace('/\\', '/').replace('//', '/')
    return absolute


# Try to get GDAL for macOS
def get_gdal_path_for_mac():
    if cfg.system_platform == 'Darwin':
        gdal_line = cfg.qgis_registry[cfg.reg_gdal_path]
        if len(gdal_line) > 0:
            cfg.qgis_registry[cfg.reg_gdal_path] = gdal_line.rstrip('/') + '/'
            if not check_file(
                    cfg.qgis_registry[cfg.reg_gdal_path] + 'gdal_translate'
            ):
                cfg.qgis_registry[cfg.reg_gdal_path] = ''
        else:
            v = cfg.util_gdal.get_gdal_version()
            cfg.qgis_registry[cfg.reg_gdal_path] = (
                    '/Library/Frameworks/GDAL.framework/Versions/'
                    '%s.%s/Programs/' % (v[0], v[1])
            )
            if not check_file(
                    cfg.qgis_registry[cfg.reg_gdal_path] + 'gdal_translate'
            ):
                cfg.qgis_registry[cfg.reg_gdal_path] = ''
