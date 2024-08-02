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
"""Band clip.

This tool allows for clipping bands.
"""

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF, QColor, QPixmap, QCursor
# noinspection PyUnresolvedReferences
from qgis.core import QgsGeometry
# noinspection PyUnresolvedReferences
from qgis.gui import QgsRubberBand

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# add rubber polygon
def add_rubber_polygon(upper_left_point, lower_right_point):
    try:
        clear_canvas_poly()
    except Exception as err:
        str(err)
    cfg.clip_rubber_poly = QgsRubberBand(
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
    cfg.clip_rubber_poly.setToGeometry(geometry, None)
    clr = QColor("#ff0000")
    clr.setAlpha(50)
    cfg.clip_rubber_poly.setFillColor(clr)
    cfg.clip_rubber_poly.setWidth(3)


# clear canvas
def clear_canvas_poly():
    cfg.clip_rubber_poly.reset()
    cfg.map_canvas.refresh()


# activate pointer
def pointer_active():
    cfg.map_canvas.setMapTool(cfg.clip_bands_pointer)
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
    cfg.dialog.ui.LX_lineEdit.setText(str(point.x()))
    cfg.dialog.ui.LY_lineEdit.setText(str(point.y()))
    show_area()


# set coordinates
def pointer_click_ul(point):
    cfg.dialog.ui.UX_lineEdit.setText(str(point.x()))
    cfg.dialog.ui.UY_lineEdit.setText(str(point.y()))
    show_area()


# show area
def show_area():
    try:
        add_rubber_polygon(
            cfg.util_qgis.create_qgis_point(
                float(cfg.dialog.ui.UX_lineEdit.text()),
                float(cfg.dialog.ui.UY_lineEdit.text())
            ),
            cfg.util_qgis.create_qgis_point(
                float(cfg.dialog.ui.LX_lineEdit.text()),
                float(cfg.dialog.ui.LY_lineEdit.text())
            )
        )
    except Exception as err:
        str(err)


# refresh shape and training list	
def refresh_layers():
    cfg.utils.refresh_vector_layer()


# show hide area radio button
def show_hide_area():
    try:
        if cfg.dialog.ui.show_area_radioButton_3.isChecked():
            show_area()
        else:
            clear_canvas_poly()
    except Exception as err:
        str(err)


# radio changed
def vector_changed():
    cfg.dialog.ui.coordinates_radioButton.blockSignals(True)
    cfg.dialog.ui.vector_radioButton.blockSignals(True)
    cfg.dialog.ui.temporary_ROI_radioButton.blockSignals(True)
    if cfg.dialog.ui.vector_radioButton.isChecked():
        cfg.dialog.ui.coordinates_radioButton.setChecked(0)
        cfg.dialog.ui.temporary_ROI_radioButton.setChecked(0)
    cfg.dialog.ui.coordinates_radioButton.blockSignals(False)
    cfg.dialog.ui.vector_radioButton.blockSignals(False)
    cfg.dialog.ui.temporary_ROI_radioButton.blockSignals(False)


# radio changed
def roi_changed():
    cfg.dialog.ui.coordinates_radioButton.blockSignals(True)
    cfg.dialog.ui.vector_radioButton.blockSignals(True)
    cfg.dialog.ui.temporary_ROI_radioButton.blockSignals(True)
    if cfg.dialog.ui.temporary_ROI_radioButton.isChecked():
        cfg.dialog.ui.vector_radioButton.setChecked(0)
        cfg.dialog.ui.coordinates_radioButton.setChecked(0)
    cfg.dialog.ui.coordinates_radioButton.blockSignals(False)
    cfg.dialog.ui.vector_radioButton.blockSignals(False)
    cfg.dialog.ui.temporary_ROI_radioButton.blockSignals(False)


# radio changed
def coordinates_changed():
    cfg.dialog.ui.coordinates_radioButton.blockSignals(True)
    cfg.dialog.ui.vector_radioButton.blockSignals(True)
    cfg.dialog.ui.temporary_ROI_radioButton.blockSignals(True)
    if cfg.dialog.ui.coordinates_radioButton.isChecked():
        cfg.dialog.ui.vector_radioButton.setChecked(0)
        cfg.dialog.ui.temporary_ROI_radioButton.setChecked(0)
    cfg.dialog.ui.coordinates_radioButton.blockSignals(False)
    cfg.dialog.ui.vector_radioButton.blockSignals(False)
    cfg.dialog.ui.temporary_ROI_radioButton.blockSignals(False)


# reference layer name
def reference_layer_name():
    reference = cfg.dialog.ui.shapefile_comboBox.currentText()
    cfg.dialog.ui.class_field_comboBox_3.clear()
    layer = cfg.util_qgis.select_layer_by_name(reference)
    try:
        if layer.type() == cfg.util_qgis.get_qgis_map_vector():
            fields = layer.dataProvider().fields()
            for field in fields:
                if str(field.typeName()).lower() != 'string':
                    cfg.dialog.class_field_combo_3(str(field.name()))
    except Exception as err:
        str(err)


# clip bands action
def clip_bands_action():
    clip_bands()


# clip bands
def clip_bands():
    # noinspection PyTypeChecker
    output_path = cfg.util_qt.get_existing_directory()
    if output_path is not False:
        cfg.logger.log.info('clip_bands: %s' % output_path)
        output_name = cfg.dialog.ui.output_clip_name_lineEdit.text()
        if len(output_name) == 0:
            output_name = None
        bandset_number = cfg.dialog.ui.band_set_comb_spinBox_2.value()
        # nodata value
        if cfg.dialog.ui.clip_virtual_checkBox.isChecked() is True:
            virtual_output = True
        else:
            virtual_output = False
        reference = vector_field = extent_list = None
        # use vector
        if cfg.dialog.ui.vector_radioButton.isChecked() is True:
            reference_layer = cfg.dialog.ui.shapefile_comboBox.currentText()
            reference = cfg.util_qgis.get_file_path(reference_layer)
            # vector EPSG
            if ('Polygon?crs=' in str(reference)
                    or 'memory?geometry=' in str(reference)
                    or '(memory)' in str(reference)):
                # temporary layer
                t_vector = cfg.utils.createTempRasterPath('gpkg')
                try:
                    selected = cfg.utls.select_layer_by_name(reference_layer)
                    s = cfg.util_qgis.save_qgis_memory_layer_to_file(
                        selected, t_vector, file_format='GPKG'
                    )
                except Exception as err:
                    str(err)
                    s = cfg.util_qgis.save_qgis_memory_layer_to_file(
                        reference, t_vector, file_format='GPKG'
                    )
                reference = cfg.util_qgis.qgis_layer_source(s)
            elif 'QgsVectorLayer' in str(reference):
                # temporary layer
                date_time = cfg.utils.get_time()
                t_vector_name = cfg.temp_roi_name + date_time + '.shp'
                t_vector = (
                        cfg.rs.configurations.temp.dir + '/' + date_time
                        + t_vector_name
                )
                # get layer crs
                crs = cfg.util_gdal.get_crs_gdal(reference)
                # create a temp shapefile with a field
                cfg.util_gdal.create_empty_shapefile_ogr(crs, t_vector)
                added_vector = cfg.util_qgis.add_vector_layer(
                    t_vector, t_vector_name
                )
                layer = cfg.util_qgis.select_layer_by_name(reference_layer)
                for f in layer.getFeatures():
                    # copy ROI to temp shapefile
                    cfg.util_qgis.copy_feature_to_qgis_layer(
                        layer, f.id(), added_vector
                    )
                reference = t_vector
            if cfg.dialog.ui.vector_field_checkBox.isChecked() is True:
                vector_field = (
                    cfg.dialog.ui.class_field_comboBox_3.currentText())
        # use temporary ROI
        elif cfg.dialog.ui.temporary_ROI_radioButton.isChecked() is True:
            if cfg.temporary_roi is not None:
                # get vector from ROI
                t_vector = cfg.rs.configurations.temp.temporary_file_path(
                    name_suffix='.shp'
                )
                cfg.util_qgis.save_qgis_memory_layer_to_file(
                    cfg.temporary_roi, t_vector
                )
                reference = t_vector
            else:
                return False
        # use coordinates
        else:
            upper_x = cfg.dialog.ui.UX_lineEdit.text()
            upper_y = cfg.dialog.ui.UY_lineEdit.text()
            lower_x = cfg.dialog.ui.LX_lineEdit.text()
            lower_y = cfg.dialog.ui.LY_lineEdit.text()
            if (len(upper_x) > 0 and len(upper_y) > 0
                    and len(lower_x) > 0 and len(lower_y) > 0):
                try:
                    clear_canvas_poly()
                    upper_left = cfg.util_qgis.create_qgis_point(
                        float(upper_x), float(upper_y)
                    )
                    lower_right = cfg.util_qgis.create_qgis_point(
                        float(lower_x), float(lower_y)
                    )
                    upper_x = lower_right.x()
                    upper_y = lower_right.y()
                    lower_x = upper_left.x()
                    lower_y = upper_left.y()
                    if float(upper_x) > float(lower_x):
                        upper_x = upper_left.x()
                        lower_x = lower_right.x()
                    if float(upper_y) < float(lower_y):
                        upper_y = upper_left.y()
                        lower_y = lower_right.y()
                except Exception as err:
                    str(err)
                bandset_x = cfg.bandset_catalog.get(bandset_number)
                crs = bandset_x.crs
                qgis_crs = cfg.util_qgis.get_qgis_crs()
                if crs is None:
                    crs = qgis_crs
                # projection of input point to bandset crs
                if cfg.util_gdal.compare_crs(crs, qgis_crs) is False:
                    upper_left_point = cfg.util_qgis.create_qgis_point(
                        upper_x, upper_y
                        )
                    lower_right_point = cfg.util_qgis.create_qgis_point(
                        lower_x, lower_y
                        )
                    try:
                        point_1 = cfg.utils.project_qgis_point_coordinates(
                            upper_left_point, qgis_crs, crs
                        )
                        point_2 = cfg.utils.project_qgis_point_coordinates(
                            lower_right_point, qgis_crs, crs
                        )
                        upper_x = point_1.x()
                        upper_y = point_1.y()
                        lower_x = point_2.x()
                        lower_y = point_2.y()
                    except Exception as err:
                        str(err)
                extent_list = [upper_x, upper_y, lower_x, lower_y]
            else:
                return False
        cfg.logger.log.debug('bandset_number: %s' % bandset_number)
        cfg.logger.log.debug('reference: %s' % reference)
        cfg.logger.log.debug('extent_list: %s' % extent_list)
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.band_clip(
            input_bands=bandset_number, output_path=output_path,
            vector_path=reference, vector_field=vector_field,
            prefix=output_name, bandset_catalog=cfg.bandset_catalog,
            extent_list=extent_list, virtual_output=virtual_output,
            multiple_resolution=True
        )
        if output.check:
            output_paths = output.paths
            for raster in output_paths:
                # add raster to layers
                cfg.util_qgis.add_raster_layer(raster)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(
            smtp=str(__name__), failed=not output.check
        )


# set script button
def set_script():
    output_path = 'output_path'
    output_name = cfg.dialog.ui.output_clip_name_lineEdit.text()
    if len(output_name) == 0:
        output_name = None
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_2.value()
    # nodata value
    if cfg.dialog.ui.clip_virtual_checkBox.isChecked() is True:
        virtual_output = True
    else:
        virtual_output = False
    reference = vector_field = extent_list = None
    # use vector
    if cfg.dialog.ui.vector_radioButton.isChecked() is True:
        reference_layer = cfg.dialog.ui.shapefile_comboBox.currentText()
        reference = cfg.util_qgis.get_file_path(reference_layer)
        # vector EPSG
        if ('Polygon?crs=' in str(reference)
                or 'memory?geometry=' in str(reference)
                or '(memory)' in str(reference)):
            # temporary layer
            t_vector = cfg.utils.createTempRasterPath('gpkg')
            try:
                selected = cfg.utls.select_layer_by_name(reference_layer)
                s = cfg.util_qgis.save_qgis_memory_layer_to_file(
                    selected, t_vector, file_format='GPKG'
                )
            except Exception as err:
                str(err)
                s = cfg.util_qgis.save_qgis_memory_layer_to_file(
                    reference, t_vector, file_format='GPKG'
                )
            reference = cfg.util_qgis.qgis_layer_source(s)
        elif 'QgsVectorLayer' in str(reference):
            # temporary layer
            date_time = cfg.utils.get_time()
            t_vector_name = cfg.temp_roi_name + date_time + '.shp'
            t_vector = (cfg.rs.configurations.temp.dir + '/' + date_time
                        + t_vector_name)
            # get layer crs
            crs = cfg.util_gdal.get_crs_gdal(reference)
            # create a temp shapefile with a field
            cfg.util_gdal.create_empty_shapefile_ogr(crs, t_vector)
            added_vector = cfg.util_qgis.add_vector_layer(
                t_vector, t_vector_name
            )
            layer = cfg.util_qgis.select_layer_by_name(reference_layer)
            for f in layer.getFeatures():
                # copy ROI to temp shapefile
                cfg.util_qgis.copy_feature_to_qgis_layer(
                    layer, f.id(), added_vector
                )
            reference = t_vector
        if cfg.dialog.ui.vector_field_checkBox.isChecked() is True:
            vector_field = cfg.dialog.ui.class_field_comboBox_3.currentText()
    # use temporary ROI
    elif cfg.dialog.ui.temporary_ROI_radioButton.isChecked() is True:
        if cfg.temporary_roi is not None:
            # temporary layer
            t_vector = cfg.utils.createTempRasterPath('gpkg')
            cfg.util_gdal.create_vector_ogr(
                cfg.temporary_roi.crs(), t_vector, vector_format='GPKG'
            )
            added_vector = cfg.util_qgis.add_vector_layer(t_vector)
            cfg.util_qgis.copy_feature_to_qgis_layer(
                cfg.temporary_roi, 1, added_vector
            )
            reference = t_vector
        else:
            return False
    # use coordinates
    else:
        upper_x = cfg.dialog.ui.UX_lineEdit.text()
        upper_y = cfg.dialog.ui.UY_lineEdit.text()
        lower_x = cfg.dialog.ui.LX_lineEdit.text()
        lower_y = cfg.dialog.ui.LY_lineEdit.text()
        try:
            clear_canvas_poly()
            upper_left = cfg.util_qgis.create_qgis_point(
                float(upper_x),
                float(upper_y)
            )
            lower_right = cfg.util_qgis.create_qgis_point(
                float(lower_x),
                float(lower_y)
            )
            upper_x = lower_right.x()
            upper_y = lower_right.y()
            lower_x = upper_left.x()
            lower_y = upper_left.y()
            if float(upper_x) > float(lower_x):
                upper_x = upper_left.x()
                lower_x = lower_right.x()
            if float(upper_y) < float(lower_y):
                upper_y = upper_left.y()
                lower_y = lower_right.y()
        except Exception as err:
            str(err)
        extent_list = [upper_x, upper_y, lower_x, lower_y]
    # get input band paths
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    if bandset_x is not None:
        files = bandset_x.get_absolute_paths()
        paths = '['
        for file in files:
            paths += '"%s", ' % file
        paths = paths[:-2] + ']'
        if paths == ']':
            paths = '[]'
    else:
        paths = '[]'
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# clip raster bands (input files from bandset)\n'
               'rs.band_clip(input_bands=%s, output_path="%s", '
               'vector_path="%s", vector_field="%s", prefix="%s", '
               'extent_list=%s, virtual_output=%s, multiple_resolution=True)'
               % (str(paths), str(output_path), str(reference),
                  str(vector_field), str(output_name),
                  str(extent_list), str(virtual_output)))
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
