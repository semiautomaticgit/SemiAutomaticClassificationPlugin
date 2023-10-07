# SemiAutomaticClassificationPlugin
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised 
# classification of remote sensing images, providing tools for the download, 
# the preprocessing and postprocessing of images.
# begin: 2012-12-29
# Copyright (C) 2012-2023 self.scatter_band_y Luca Congedo.
# Author: Luca Congedo
# Email: ing.congedoluca@gmail.com
#
# This file is part of SemiAutomaticClassificationPlugin.
# SemiAutomaticClassificationPlugin is free software: you can redistribute it 
# and/or modify it under the terms of the GNU General Public License 
# as published self.scatter_band_y the Free Software Foundation, 
# either version 3 of the License, or (at your option) any later version.
# SemiAutomaticClassificationPlugin is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with SemiAutomaticClassificationPlugin. 
# If not, see <https://www.gnu.org/licenses/>.


import matplotlib.colors as mpl_colors
import matplotlib.pyplot as mpl_plot
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor, QPolygonF
from PyQt5.QtWidgets import QApplication
from matplotlib.ticker import MaxNLocator
from qgis.core import QgsVectorLayer, QgsGeometry, QgsFeature

try:
    from remotior_sensus.core.processor_functions import (
        get_values_for_scatter_plot
    )
    from remotior_sensus.core.spectral_signatures import SpectralSignaturePlot
except Exception as error:
    str(error)

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


class ScatterPlot:

    def __init__(self):
        try:
            canvas = cfg.scatter_plot_dlg.ui.Scatter_Widget_2.sigCanvas
            self.mouseScroll = canvas.mpl_connect(
                'scroll_event',
                self.scroll_event
            )
            self.mousePress = canvas.mpl_connect(
                'button_press_event',
                self.press_event
            )
            self.mouseRelease = canvas.mpl_connect(
                'button_release_event',
                self.release_event
            )
            self.mouseMove = canvas.mpl_connect(
                'motion_notify_event',
                self.motion_event
            )
            self.ax = canvas.ax
        except Exception as err:
            str(err)
            return
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        self.last_x_min = None
        self.last_x_max = None
        self.last_y_min = None
        self.last_y_max = None
        self.color = '#ffaa00'
        self.temp_scatter_name = 'temp_scatter'
        self.scatter_band_x = 1
        self.scatter_band_y = 2
        self.order_column = 1
        self.plot_catalog = cfg.rs.spectral_signatures_plot_catalog()
        self.press = None
        self.release = None
        self.select_all = False

    @staticmethod
    def motion_event(event):
        if event.inaxes is not None:
            cfg.scatter_plot_dlg.ui.value_label_2.setText(
                'x=%s y=%s' % (str(event.xdata)[:8].ljust(8),
                               str(event.ydata)[:8].ljust(8))
            )

    def press_event(self, event):
        if event.inaxes is None:
            self.press = None
            return 0
        self.press = [event.xdata, event.ydata]

    def release_event(self, event):
        if event.inaxes is None:
            self.release = None
            return 0
        self.release = [event.xdata, event.ydata]
        if event.button == 3:
            self.resize()
        else:
            self.move()

    def scroll_event(self, event):
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()
        zoom_x = (x_max - x_min) * 0.2
        zoom_y = (y_max - y_min) * 0.2
        if event.button == 'down':
            x_lim_min = x_min - zoom_x
            x_lim_max = x_max + zoom_x
            y_lim_min = y_min - zoom_y
            y_lim_max = y_max + zoom_y
        else:
            x_lim_min = x_min + zoom_x
            x_lim_max = x_max - zoom_x
            y_lim_min = y_min + zoom_y
            y_lim_max = y_max - zoom_y
        self.ax.set_xlim(x_lim_min, x_lim_max)
        self.ax.set_ylim(y_lim_min, y_lim_max)
        cfg.scatter_plot_dlg.ui.Scatter_Widget_2.sigCanvas.draw()
        self.last_x_min = x_lim_min
        self.last_x_max = x_lim_max
        self.last_y_min = y_lim_min
        self.last_y_max = y_lim_max

    # edited cell
    def edited_cell(self, row, column):
        table = cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget
        signature_id = table.item(row, 6).text()
        if column == 0:
            if table.item(row, column).checkState() == 2:
                self.plot_catalog.catalog[signature_id].selected = 1
            else:
                self.plot_catalog.catalog[signature_id].selected = 0
        elif column == 1:
            self.plot_catalog.catalog[signature_id].macroclass_id = int(
                table.item(row, column).text()
            )
        elif column == 2:
            self.plot_catalog.catalog[signature_id].macroclass_name = str(
                table.item(row, column).text()
            )
        elif column == 3:
            self.plot_catalog.catalog[signature_id].class_id = int(
                table.item(row, column).text()
            )
        elif column == 4:
            self.plot_catalog.catalog[signature_id].class_name = str(
                table.item(row, column).text()
            )
        self.create_scatter_plot()

    # scatter plot double click
    def scatter_plot_double_click(self, index):
        table = cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget
        if index.column() == 5:
            color = cfg.util_qt.select_color()
            if color is not None:
                cfg.scatter_plot_dlg.ui.colormap_comboBox.setCurrentIndex(0)
                selected = []
                for i in table.selectedIndexes():
                    selected.append(i.row())
                selected = list(set(selected))
                for row in selected:
                    signature_id = table.item(row, 6).text()
                    self.plot_catalog.catalog[signature_id].color = (
                        color.toRgb().name()
                    )
                    table.item(row, 5).setBackground(color)
                    del self.plot_catalog.catalog[signature_id].attributes[
                        'color_map']
        elif index.column() == 0:
            self.select_all_rois()
        self.create_scatter_plot()

    # select all signatures
    def select_all_rois(self):
        # select all
        if self.select_all is True:
            cfg.util_qt.all_items_set_state(
                cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget, 2
            )
            for signature in self.plot_catalog.catalog:
                self.plot_catalog.catalog[signature].selected = 1
            # set check all plot
            self.select_all = False
        # unselect all if previously selected all
        else:
            cfg.util_qt.all_items_set_state(
                cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget, 0
            )
            # set check all plot
            self.select_all = True
            for signature in self.plot_catalog.catalog:
                self.plot_catalog.catalog[signature].selected = 0

    # add temp ROI to scatter plot
    def add_temp_roi_to_scatter_plot(self):
        if cfg.temporary_roi is not None:
            self.calculate_vector_scatter_plot()

    # calculate polygon scatter plot
    def calculate_polygon_scatter_plot(self, polygon):
        crs = cfg.bandset_catalog.get_crs(
            cfg.project_registry[cfg.reg_active_bandset_number]
        )
        if crs is None:
            crs = cfg.util_qgis.get_qgis_crs()
        # date time for temp name
        date = cfg.utils.get_time()
        memory_layer = QgsVectorLayer(
            'MultiPolygon?crs=' + str(crs.toWkt()), 'm' + str(date), 'memory'
        )
        point_f = QPointF()
        polygon_f = QPolygonF()
        for v in polygon:
            point_f.setX(v.x())
            point_f.setY(v.y())
            polygon_f.append(point_f)
        point_f.setX(polygon[0].x())
        point_f.setY(polygon[0].y())
        polygon_f.append(point_f)
        g = QgsGeometry().fromQPolygonF(polygon_f)
        f = QgsFeature()
        f.setGeometry(g)
        memory_layer.startEditing()
        memory_layer.addFeatures([f])
        memory_layer.commitChanges()
        memory_layer.dataProvider().createSpatialIndex()
        memory_layer.updateExtents()
        vector = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix='.gpkg'
        )
        cfg.util_qgis.save_qgis_memory_layer_to_file(memory_layer, vector)
        self.calculate_vector_scatter_plot(vector=vector)

    # add vector to scatter plot
    def calculate_vector_scatter_plot(self, vector=None):
        # temporary ROI
        if vector is None:
            # get vector from ROI
            vector = cfg.rs.configurations.temp.temporary_file_path(
                name_suffix='.gpkg'
            )
            cfg.util_qgis.save_qgis_memory_layer_to_file(
                cfg.temporary_roi, vector
            )
        signature_id = self.temp_scatter_name
        color_string = cfg.rs.shared_tools.random_color()
        vector_plot = SpectralSignaturePlot(
            value=None, wavelength=None, signature_id=signature_id,
            macroclass_name=self.temp_scatter_name,
            class_name=self.temp_scatter_name, color_string=color_string,
            selected=1
        )
        self.plot_catalog.catalog[signature_id] = vector_plot
        self.plot_catalog.catalog[signature_id].attributes[
            'geometry_path'] = vector
        self.scatter_plot_list_table()

    # calculate scatter plot
    def calculate_scatter_plot(self):
        self.create_scatter_plot(calculate=True)

    # plot colormap
    def color_plot(self):
        table = cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget
        selected = []
        for i in table.selectedIndexes():
            selected.append(i.row())
        selected = list(set(selected))
        if len(selected) == 0:
            count = table.rowCount()
            selected = list(range(0, count))
        for x in selected:
            signature_id = table.item(x, 6).text()
            color_name = (
                cfg.scatter_plot_dlg.ui.colormap_comboBox.currentText()
            )
            signature = self.plot_catalog.catalog[signature_id]
            color = signature.color
            if (len(color_name) > 0
                    and color_name in cfg.scatter_color_map):
                pal = mpl_plot.get_cmap(color_name)
                pal.set_under('w', 0.0)
                signature.attributes['color_map'] = pal
            else:
                q_color = QColor(color)
                hue = q_color.hue()
                saturation = q_color.saturation()
                value = q_color.value()
                # light color
                light_color = QColor()
                higher_value = value + 60
                if higher_value > 255:
                    higher_value = 255
                light_color.setHsv(hue, saturation, higher_value)
                # dark color
                dark_color = QColor()
                lower_value = value - 60
                if lower_value < 0:
                    lower_value = 0
                dark_color.setHsv(hue, saturation, lower_value)
                pal = mpl_colors.LinearSegmentedColormap.from_list(
                    'color', [dark_color.toRgb().name(), color,
                              light_color.toRgb().name()]
                )
                pal.set_under('w', 0.0)
                signature.attributes['color_map'] = pal
        self.create_scatter_plot(skip_color=True)

    # Create scatter plot
    # noinspection PyTypeChecker,PyUnresolvedReferences
    def create_scatter_plot(self, calculate=False, skip_color=False):
        # Clear plot
        try:
            self.ax.clear()
            cfg.scatter_plot_dlg.ui.Scatter_Widget_2.sigCanvas.draw()
        except Exception as err:
            str(err)
            return None
        # Set labels
        self.ax.set_xlabel(
            '%s %s' % (
                QApplication.translate(
                    'semiautomaticclassificationplugin',
                    'Band'
                ), str(self.scatter_band_x)
            )
        )
        self.ax.set_ylabel(
            '%s %s' % (
                QApplication.translate(
                    'semiautomaticclassificationplugin',
                    'Band'
                ), str(self.scatter_band_y))
        )
        x_min_list = []
        x_max_list = []
        y_min_list = []
        y_max_list = []
        for signature_id in self.plot_catalog.catalog:
            signature = self.plot_catalog.catalog[signature_id]
            if signature.selected == 1:
                color = signature.color
                geometry_path = signature.attributes['geometry_path']
                color_name = (
                    cfg.scatter_plot_dlg.ui.colormap_comboBox.currentText()
                )
                if skip_color is False:
                    if (len(color_name) > 0
                            and color_name in cfg.scatter_color_map):
                        pal = mpl_plot.get_cmap(color_name)
                        pal.set_under('w', 0.0)
                        signature.attributes['color_map'] = pal
                    else:
                        q_color = QColor(color)
                        hue = q_color.hue()
                        saturation = q_color.saturation()
                        value = q_color.value()
                        # light color
                        light_color = QColor()
                        higher_value = value + 70
                        if higher_value > 255:
                            higher_value = 255
                        light_color.setHsv(hue, saturation, higher_value)
                        # dark color
                        dark_color = QColor()
                        lower_value = value - 70
                        if lower_value < 0:
                            lower_value = 0
                        dark_color.setHsv(hue, saturation, lower_value)
                        pal = mpl_colors.LinearSegmentedColormap.from_list(
                            'color', [dark_color.toRgb().name(), color,
                                      light_color.toRgb().name()]
                        )
                        pal.set_under('w', 0.0)
                        signature.attributes['color_map'] = pal
                # load scatter
                if 'histogram_%s_%s' % (
                        self.scatter_band_x, self.scatter_band_y
                ) in signature.attributes and calculate is False:
                    try:
                        h = signature.attributes[
                            'histogram_%s_%s' % (
                                self.scatter_band_x, self.scatter_band_y
                            )
                            ]
                        if h is not False:
                            self.ax.imshow(
                                h[0].T, origin='lower', interpolation='none',
                                extent=[h[1][0], h[1][-1], h[2][0], h[2][-1]],
                                cmap=signature.attributes['color_map'],
                                vmin=0.001
                            )
                        else:
                            return False
                    except Exception as err:
                        cfg.logger.log.error(str(err))
                        return False
                else:
                    cfg.ui_utils.add_progress_bar()
                    # calculate scatter
                    value_list = (
                        cfg.bandset_catalog.calculate_scatter_plot_histogram(
                            bandset_number=cfg.project_registry[
                                cfg.reg_active_bandset_number
                            ], band_x=self.scatter_band_x,
                            band_y=self.scatter_band_y,
                            vector_path=geometry_path
                        )
                    )
                    if cfg.scatter_plot_dlg.ui.precision_checkBox.isChecked():
                        ui = cfg.scatter_plot_dlg.ui
                        decimal_round = int(
                            ui.precision_comboBox.currentText()
                        )
                    else:
                        decimal_round = -1
                    if value_list is not False:
                        # calculate histogram
                        h = cfg.rs.shared_tools.calculate_2d_histogram(
                            x_values=value_list[0], y_values=value_list[1],
                            decimal_round=decimal_round
                        )
                        if h is not False:
                            self.ax.imshow(
                                h[0].T, origin='lower', interpolation='none',
                                extent=[h[1][0], h[1][-1], h[2][0], h[2][-1]],
                                cmap=signature.attributes['color_map'],
                                vmin=0.001
                            )
                            # preserve histogram_
                            signature.attributes[
                                'histogram_%s_%s' % (
                                    self.scatter_band_x, self.scatter_band_y)
                                ] = h
                            cfg.ui_utils.remove_progress_bar()
                        else:
                            cfg.ui_utils.remove_progress_bar()
                            return False
                    else:
                        cfg.ui_utils.remove_progress_bar()
                        return False
                x_min_list.append(h[1][0])
                x_max_list.append(h[1][-1])
                y_min_list.append(h[2][0])
                y_max_list.append(h[2][-1])
        # Grid for X and Y axes
        try:
            self.ax.xaxis.set_major_locator(MaxNLocator(5))
            self.ax.yaxis.set_major_locator(MaxNLocator(5))
        except Exception as err:
            str(err)
        try:
            self.x_min = min(x_min_list)
            self.x_max = max(x_max_list)
            self.y_min = min(y_min_list)
            self.y_max = max(y_max_list)
            if (self.last_x_min is None or self.last_x_max is None
                    or self.last_y_min is None or self.last_y_max is None):
                self.last_x_min = self.x_min
                self.last_x_max = self.x_max
                self.last_y_min = self.y_min
                self.last_y_max = self.y_max
        except Exception as err:
            str(err)
        # Draw the plot
        self.fit_plot_to_axes()

    # remove scatter plot from list
    # noinspection PyTypeChecker
    def remove_scatter(self):
        answer = cfg.util_qt.question_box(
            QApplication.translate(
                'semiautomaticclassificationplugin',
                'Delete scatter plot'
            ),
            QApplication.translate(
                'semiautomaticclassificationplugin',
                'Are you sure you want to delete highlighted scatter plots?'
            )
        )
        if answer is True:
            table = cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget
            r = []
            for i in table.selectedIndexes():
                r.append(i.row())
            v = list(set(r))
            for x in v:
                try:
                    signature_id = table.item(x, 6).text()
                except Exception as err:
                    str(err)
                    return False
                del self.plot_catalog.catalog[signature_id]
            self.scatter_plot_list_table()

    # Create signature list for plot
    def scatter_plot_list_table(self, skip_plot=False):
        table = cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget
        table.setSortingEnabled(False)
        table.blockSignals(True)
        cfg.util_qt.clear_table(table)
        # add signature_id items
        x = 0
        for signature_id in self.plot_catalog.catalog:
            selected = self.plot_catalog.catalog[signature_id].selected
            if selected == 1:
                checkbox_state = 2
            else:
                checkbox_state = 0
            color = self.plot_catalog.catalog[signature_id].color
            cfg.util_qt.insert_table_row(table, x, 20)
            cfg.util_qt.add_table_item(
                table, '', x, 0, True, None, checkbox_state
            )
            cfg.util_qt.add_table_item(
                table,
                int(self.plot_catalog.catalog[signature_id].macroclass_id),
                x, 1
            )
            cfg.util_qt.add_table_item(
                table,
                str(self.plot_catalog.catalog[signature_id].macroclass_name),
                x, 2
            )
            cfg.util_qt.add_table_item(
                table, int(self.plot_catalog.catalog[signature_id].class_id),
                x, 3
            )
            cfg.util_qt.add_table_item(
                table, str(self.plot_catalog.catalog[signature_id].class_name),
                x, 4
            )
            cfg.util_qt.add_table_item(table, '', x, 5, True, QColor(color))
            cfg.util_qt.add_table_item(table, str(signature_id), x, 6, False)
            x += 1
        table.show()
        cfg.util_qt.sort_table_column(
            table, self.order_column,
            table.horizontalHeader().sortIndicatorOrder()
        )
        table.setSortingEnabled(True)
        table.blockSignals(False)
        # Create plot
        if skip_plot is False:
            self.create_scatter_plot()

    # set band X
    def band_x_plot(self):
        # band set
        bandset_x = cfg.bandset_catalog.get_bandset_by_number(
            cfg.project_registry[cfg.reg_active_bandset_number]
        )
        count = bandset_x.get_band_count()
        if cfg.scatter_plot_dlg.ui.bandX_spinBox.value() > count:
            cfg.scatter_plot_dlg.ui.bandX_spinBox.blockSignals(True)
            cfg.scatter_plot_dlg.ui.bandX_spinBox.setValue(count)
            cfg.scatter_plot_dlg.ui.bandX_spinBox.blockSignals(False)
        self.scatter_band_x = cfg.scatter_plot_dlg.ui.bandX_spinBox.value()
        self.create_scatter_plot()

    # set band Y
    def band_y_plot(self):
        # band set
        bandset_x = cfg.bandset_catalog.get_bandset_by_number(
            cfg.project_registry[cfg.reg_active_bandset_number]
        )
        count = bandset_x.get_band_count()
        if cfg.scatter_plot_dlg.ui.bandY_spinBox.value() > count:
            cfg.scatter_plot_dlg.ui.bandY_spinBox.blockSignals(True)
            cfg.scatter_plot_dlg.ui.bandY_spinBox.setValue(count)
            cfg.scatter_plot_dlg.ui.bandY_spinBox.blockSignals(False)
        self.scatter_band_y = cfg.scatter_plot_dlg.ui.bandY_spinBox.value()
        self.create_scatter_plot()

    # resize plot
    def resize(self):
        try:
            x_lim_min = min([float(self.press[0]), float(self.release[0])])
            x_lim_max = max([float(self.press[0]), float(self.release[0])])
            y_lim_min = min([float(self.press[1]), float(self.release[1])])
            y_lim_max = max([float(self.press[1]), float(self.release[1])])
            if (((x_lim_max - x_lim_min) * (x_lim_max - x_lim_min)) < 0.000001
                    or ((y_lim_max - y_lim_min)
                        * (y_lim_max - y_lim_min)) < 0.000001):
                return
            self.ax.set_xlim(x_lim_min, x_lim_max)
            self.ax.set_ylim(y_lim_min, y_lim_max)
            cfg.scatter_plot_dlg.ui.Scatter_Widget_2.sigCanvas.draw()
            self.last_x_min = x_lim_min
            self.last_x_max = x_lim_max
            self.last_y_min = y_lim_min
            self.last_y_max = y_lim_max
        except Exception as err:
            str(err)

    # move plot
    def move(self):
        try:
            delta_x = (float(self.press[0]) - float(self.release[0]))
            delta_y = (float(self.press[1]) - float(self.release[1]))
            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()
            self.ax.set_xlim(x_min + delta_x, x_max + delta_x)
            self.ax.set_ylim(y_min + delta_y, y_max + delta_y)
            cfg.scatter_plot_dlg.ui.Scatter_Widget_2.sigCanvas.draw()
            self.last_x_min = x_min + delta_x
            self.last_x_max = x_max + delta_x
            self.last_y_min = y_min + delta_y
            self.last_y_max = y_max + delta_y
        except Exception as err:
            str(err)

    # save plot to file
    @staticmethod
    def save_plot():
        # noinspection PyTypeChecker
        image_output = cfg.util_qt.get_save_file_name(
            None, QApplication.translate(
                'semiautomaticclassificationplugin', 'Save plot to file'
            ), '', 'JPG file (*.jpg);;PNG file (*.png);;PDF file (*.pdf)',
            None
        )
        if len(image_output) > 0:
            scatter = cfg.scatter_plot_dlg.ui.Scatter_Widget_2
            if str(image_output).endswith('.png'):
                scatter.sigCanvas.figure.savefig(
                    image_output, format='png', dpi=300
                )
            elif str(image_output).endswith('.pdf'):
                scatter.sigCanvas.figure.savefig(
                    image_output, format='pdf', dpi=300
                )
            else:
                image_output = image_output + '.jpg'
                scatter.sigCanvas.figure.savefig(
                    image_output, format='jpg', dpi=300, quality=90
                )

    # fit plot to axes
    def fit_plot_to_axes(self, preserve_last=False):
        if preserve_last is True:
            x_min = self.last_x_min
            x_max = self.last_x_max
            y_min = self.last_y_min
            y_max = self.last_y_max
        else:
            x_min = self.x_min
            x_max = self.x_max
            y_min = self.y_min
            y_max = self.y_max
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.last_x_min = x_min
        self.last_x_max = x_max
        self.last_y_min = y_min
        self.last_y_max = y_max
        try:
            # Draw the plot
            cfg.scatter_plot_dlg.ui.Scatter_Widget_2.sigCanvas.draw()
        except Exception as err:
            str(err)
            return False


# add colormap list to combo
def add_colormap_to_combo(color_list):
    for i in color_list:
        cfg.scatter_plot_dlg.ui.colormap_comboBox.addItem(i)
