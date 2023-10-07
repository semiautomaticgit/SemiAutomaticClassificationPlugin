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


from itertools import combinations as iter_combinations

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
from matplotlib.ticker import MaxNLocator

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


class SpectralSignaturePlot:

    def __init__(self):
        try:
            canvas = cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas
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
            self.check_limits = False
            self.press = None
            self.release = None
            self.first_plot = True
            self.select_all = False
            self.sigma_check = True
            self.legend_max_chars = 15
            self.order_column = 1
            self.filled_plots = []
            self.y_minimum_value = 10000000000
            self.y_maximum_value = -10000000000
            self.x_minimum_value = 10000000000
            self.x_maximum_value = -10000000000
            self.plot_catalog = cfg.rs.spectral_signatures_plot_catalog()
            self.ax = cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.ax
            self.ax.grid(True)
        except Exception as err:
            str(err)

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

    @staticmethod
    def motion_event(event):
        if event.inaxes is not None:
            cfg.spectral_plot_dlg.ui.value_label.setText(
                'x=%s y=%s' % (str(event.xdata)[:8].ljust(8),
                               str(event.ydata)[:8].ljust(8))
            )

    # scroll
    def scroll_event(self, event):
        x_min, x_max = (self.ax.get_xlim())
        y_min, y_max = (self.ax.get_ylim())
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
        cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.draw()

    # resize plot
    def resize(self):
        try:
            x_lim_min = min([float(self.press[0]), float(self.release[0])])
            x_lim_max = max([float(self.press[0]), float(self.release[0])])
            y_lim_min = min([float(self.press[1]), float(self.release[1])])
            y_lim_max = max([float(self.press[1]), float(self.release[1])])
            if ((x_lim_max - x_lim_min) * (x_lim_max - x_lim_min) < 0.0001
                    or (y_lim_max - y_lim_min)
                    * (y_lim_max - y_lim_min) < 0.0001):
                return
            self.ax.set_xlim(x_lim_min, x_lim_max)
            self.ax.set_ylim(y_lim_min, y_lim_max)
            cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.draw()
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
            cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.draw()
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
            if str(image_output).endswith('.png'):
                cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.figure.savefig(
                    image_output, format='png', dpi=300
                )
            elif str(image_output).endswith('.pdf'):
                cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.figure.savefig(
                    image_output, format='pdf', dpi=300
                )
            else:
                image_output = image_output + '.jpg'
                cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.figure.savefig(
                    image_output, format='jpg', dpi=300, quality=90
                )

    # fit plot to axes
    def fit_plot_to_axes(self):
        self.ax.relim()
        self.ax.autoscale(True)
        self.ax.autoscale_view(True)
        try:
            self.ax.set_xlim(self.x_minimum_value, self.x_maximum_value)
            self.ax.set_ylim(self.y_minimum_value, self.y_maximum_value)
        except Exception as err:
            str(err)
        # Draw the plot
        cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.draw()

    # Add to signature list
    def add_to_signature_list(self):
        # noinspection PyTypeChecker
        answer = cfg.util_qt.question_box(
            QApplication.translate(
                'semiautomaticclassificationplugin',
                'Add to Signature list'
            ),
            QApplication.translate(
                'semiautomaticclassificationplugin',
                'Are you sure you want to add highlighted signatures '
                'to the list?'
            )
        )
        if answer is True:
            table = cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget
            selected = []
            for i in table.selectedIndexes():
                selected.append(i.row())
            selected_rows = list(set(selected))
            if len(selected_rows) == 0:
                count = table.rowCount()
                selected_rows = list(range(0, count))
            for x in selected_rows:
                signature_id = table.item(x, 6).text()
                values = self.plot_catalog.catalog[signature_id].value
                wavelengths = self.plot_catalog.catalog[
                    signature_id].wavelength
                standard_deviations = self.plot_catalog.catalog[
                    signature_id].standard_deviation
                macroclass_id = self.plot_catalog.catalog[
                    signature_id].macroclass_id
                macroclass_name = self.plot_catalog.catalog[
                    signature_id].macroclass_name
                class_name = self.plot_catalog.catalog[signature_id].class_name
                class_id = self.plot_catalog.catalog[signature_id].class_id
                color_string = self.plot_catalog.catalog[signature_id].color
                cfg.scp_training.signature_catalog.add_spectral_signature(
                    value_list=values,
                    wavelength_list=wavelengths,
                    standard_deviation_list=standard_deviations,
                    macroclass_id=macroclass_id, class_id=class_id,
                    macroclass_name=macroclass_name, class_name=class_name,
                    geometry=0, signature=1, color_string=color_string
                )
                cfg.scp_training.roi_signature_table_tree()

    # Create signature list for plot
    def signature_list_plot_table(self, skip_plot=False):
        table = cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget
        table.setSortingEnabled(False)
        table.blockSignals(True)
        cfg.util_qt.clear_table(table)
        # add signature items
        x = 0
        for signature in self.plot_catalog.catalog:
            selected = self.plot_catalog.catalog[signature].selected
            if selected == 1:
                checkbox_state = 2
            else:
                checkbox_state = 0
            color = self.plot_catalog.catalog[signature].color
            cfg.util_qt.insert_table_row(table, x, 20)
            cfg.util_qt.add_table_item(
                table, '', x, 0, True, None, checkbox_state
            )
            cfg.util_qt.add_table_item(
                table,
                int(self.plot_catalog.catalog[signature].macroclass_id), x, 1
            )
            cfg.util_qt.add_table_item(
                table,
                str(self.plot_catalog.catalog[signature].macroclass_name), x, 2
            )
            cfg.util_qt.add_table_item(
                table, int(self.plot_catalog.catalog[signature].class_id), x, 3
            )
            cfg.util_qt.add_table_item(
                table, str(self.plot_catalog.catalog[signature].class_name),
                x, 4
            )
            cfg.util_qt.add_table_item(table, '', x, 5, True, QColor(color))
            cfg.util_qt.add_table_item(table, str(signature), x, 6, False)
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
            self.signature_plot()
            self.check_limits = True

    # Create signature plot
    # noinspection PyTypeChecker
    def signature_plot(self):
        self.y_minimum_value = 10000000000
        self.y_maximum_value = -10000000000
        self.x_minimum_value = 10000000000
        self.x_maximum_value = -10000000000
        if self.first_plot is False:
            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()
        else:
            x_min = x_max = y_min = y_max = None
        try:
            for i in self.filled_plots:
                i.remove()
            self.filled_plots = []
        except Exception as err:
            str(err)
        try:
            lines = len(self.ax.lines)
        except Exception as err:
            str(err)
            return None
        if lines > 0:
            for i in reversed(list(range(0, lines))):
                self.ax.lines.pop(i)
        cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.draw()
        # Set labels
        self.ax.set_xlabel(
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Wavelength'
            )
        )
        self.ax.set_ylabel(
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Values'
            )
        )
        # Add plots and legend
        plot_legend = []
        plot_legend_name = []
        wavelengths_list = []
        # clear signature values
        cfg.spectral_plot_dlg.ui.value_textBrowser.clear()
        for signature_id in self.plot_catalog.catalog:
            signature = self.plot_catalog.get_signature(
                signature_id=signature_id
            )
            if signature.selected == 1:
                name = '%s#%s; %s#%s' % (
                    signature.macroclass_id, signature.macroclass_name,
                    signature.class_id, signature.class_name
                )
                values = signature.value
                standard_deviations = signature.standard_deviation
                wavelengths = signature.wavelength
                wavelengths_list.extend(wavelengths)
                color = signature.color
                pixel_count = signature.pixel_count
                try:
                    values = eval(str(values).replace('nan', '0'))
                except Exception as err:
                    str(err)
                try:
                    standard_deviations = eval(
                        str(standard_deviations).replace('nan', '0')
                    )
                except Exception as err:
                    str(err)
                if sum(standard_deviations) != 0:
                    mean_plus = [
                        v + s for v, s in zip(values, standard_deviations)
                    ]
                    mean_minus = [
                        v - s for v, s in zip(values, standard_deviations)
                    ]
                    minimum_value = min(mean_minus)
                    maximum_value = max(mean_plus)
                    sigma_check = True
                else:
                    minimum_value = min(values)
                    maximum_value = max(values)
                    mean_minus = mean_plus = None
                    sigma_check = False
                if minimum_value < self.y_minimum_value:
                    self.y_minimum_value = minimum_value
                if maximum_value > self.y_maximum_value:
                    self.y_maximum_value = maximum_value
                # plot
                plot, = self.ax.plot(wavelengths, values, color)
                if self.sigma_check is True and sigma_check is True:
                    # fill plot
                    self.filled_plots.append(
                        self.ax.fill_between(
                            wavelengths, mean_minus, mean_plus, color=color,
                            alpha=0.2
                        )
                    )
                # add plot to legend
                plot_legend.append(plot)
                plot_legend_name.append(name[:self.legend_max_chars])
                # signature values
                self.signature_details(
                    name, values, standard_deviations, wavelengths, color,
                    pixel_count
                )
        wavelengths_list = set(wavelengths_list)
        if len(wavelengths_list) > 0:
            x_minimum_value = min(wavelengths_list)
            x_maximum_value = max(wavelengths_list)
        else:
            x_minimum_value = self.x_minimum_value
            x_maximum_value = self.x_maximum_value
        if x_minimum_value < self.x_minimum_value:
            self.x_minimum_value = x_minimum_value
        if x_maximum_value > self.x_maximum_value:
            self.x_maximum_value = x_maximum_value
        if cfg.spectral_plot_dlg.ui.band_lines_checkBox.isChecked():
            for wave in wavelengths_list:
                self.ax.axvline(wave, color='black', linestyle='dashed')
        # place legend
        # matplotlib API Changes for 3.1.1
        try:
            self.ax.legend(
                plot_legend, plot_legend_name,
                bbox_to_anchor=(0.1, 0.0, 1.1, 1.0), loc=1, borderaxespad=0.
            ).set_draggable(True)
        except Exception as err:
            str(err)
            self.ax.legend(
                plot_legend, plot_legend_name,
                bbox_to_anchor=(0.1, 0.0, 1.1, 1.0), loc=1, borderaxespad=0.
            ).draggable()
        self.ax.set_xticks(wavelengths_list)
        self.ax.xaxis.set_major_locator(MaxNLocator(7))
        self.ax.yaxis.set_major_locator(MaxNLocator(5))
        try:
            if self.first_plot is True:
                self.first_plot = False
                self.ax.set_xlim(self.x_minimum_value, self.x_maximum_value)
                self.ax.set_ylim(self.y_minimum_value, self.y_maximum_value)
            else:
                self.ax.set_xlim(x_min, x_max)
                self.ax.set_ylim(y_min, y_max)
        except Exception as err:
            str(err)
        # Draw the plot
        cfg.spectral_plot_dlg.ui.Sig_Widget.sigCanvas.draw()
        if self.check_limits is False:
            self.fit_plot_to_axes()

    # remove signature from table
    # noinspection PyTypeChecker
    def remove_signature(self):
        answer = cfg.util_qt.question_box(
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Delete signatures'
            ),
            QApplication.translate(
                'semiautomaticclassificationplugin',
                'Are you sure you want to delete highlighted signatures?'
            )
        )
        if answer is True:
            table = cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget
            selected = []
            for i in table.selectedIndexes():
                selected.append(i.row())
            selected = list(set(selected))
            for x in selected:
                try:
                    signature_id = table.item(x, 6).text()
                except Exception as err:
                    str(err)
                    return False
                del self.plot_catalog.catalog[signature_id]
            self.signature_list_plot_table()

    # signature details
    # noinspection PyTypeChecker
    @staticmethod
    def signature_details(
            name, values, standard_deviations, wavelengths, color,
            pixel_count
    ):
        text = (
            '<table border="1" width="100%"><tr><th bgcolor={}>'
            '</th>'.format(color)
        )
        text += (
            '<th style="text-align: left" colspan={}>{}; {}={}</th></tr>'
            '<tr><th>{}</th>'.format(
                len(values), name, QApplication.translate(
                    'semiautomaticclassificationplugin', 'Pixel count'
                ), pixel_count, QApplication.translate(
                    'semiautomaticclassificationplugin', 'Wavelength'
                )
            )
        )
        for w in wavelengths:
            text += '<td width="{}%">{}</td>'.format(
                int(100 / len(wavelengths)), str(w)
            )
        text += '</tr><tr><th>%s</th>' % QApplication.translate(
            'semiautomaticclassificationplugin', 'Values'
        )
        for v in values:
            text += '<td width="{}%">{}</td>'.format(
                int(100 / len(wavelengths)), str(round(v, 5))
            )
        text += '</tr><tr><th>%s</th>' % QApplication.translate(
            'semiautomaticclassificationplugin', 'Standard deviation'
        )
        for s in standard_deviations:
            text += '<td width="{}%">{}</td>'.format(
                int(100 / len(wavelengths)), str(round(s, 5))
            )
        text += '</tr></table><br/>'
        cfg.spectral_plot_dlg.ui.value_textBrowser.append(text)

    # calculate spectral distances
    def calculate_spectral_distances(self):
        cfg.logger.log.debug('calculate_spectral_distances')
        try:
            # clear distance values
            cfg.spectral_plot_dlg.ui.distance_textBrowser.clear()
            table = cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget
            selected = []
            for i in table.selectedIndexes():
                selected.append(i.row())
            selected = list(set(selected))
            if len(selected) == 0:
                count = table.rowCount()
                selected = list(range(0, count))
            signature_id_list = []
            for row in selected:
                signature_id = table.item(row, 6).text()
                signature = self.plot_catalog.get_signature(
                    signature_id=signature_id
                )
                if signature.selected == 1:
                    signature_id_list.append(signature_id)
            # calculate distances
            combinations = list(iter_combinations(signature_id_list, 2))
            for combination in combinations:
                signature_x = self.plot_catalog.get_signature(
                    signature_id=combination[0]
                )
                signature_y = self.plot_catalog.get_signature(
                    signature_id=combination[1]
                )
                values_x = signature_x.value
                values_y = signature_y.value
                spectral_angle = cfg.rs.shared_tools.calculate_spectral_angle(
                    values_x=values_x, values_y=values_y
                )
                euclidean = cfg.rs.shared_tools.calculate_euclidean_distance(
                    values_x=values_x, values_y=values_y
                )
                (
                    bray_curtis
                ) = cfg.rs.shared_tools.calculate_bray_curtis_similarity(
                    values_x=values_x, values_y=values_y
                )
                self.output_signature_distances(
                    signature_x.macroclass_id, signature_x.macroclass_name,
                    signature_x.class_id, signature_x.class_name,
                    signature_x.color, signature_y.macroclass_id,
                    signature_y.macroclass_name, signature_y.class_id,
                    signature_y.class_name, signature_y.color, spectral_angle,
                    euclidean, bray_curtis
                )
            cfg.input_interface.select_spectral_plot_settings_tab(2)
        except Exception as err:
            cfg.logger.log.error(str(err))
            cfg.mx.msg_err_6()

    # output signature distances
    # noinspection PyTypeChecker
    @staticmethod
    def output_signature_distances(
            macroclass_x, macroclass_name_x, class_x, class_name_x, color_x,
            macroclass_y, macroclass_name_y, class_y, class_name_y, color_y,
            spectral_angle, euclidean_distance, bray_curtis_similarity
    ):
        # distance names
        euclidean_distance_name = QApplication.translate(
            'semiautomaticclassificationplugin', 'Euclidean distance'
        )
        bray_curtis_similarity_name = QApplication.translate(
            'semiautomaticclassificationplugin', 'Bray-Curtis similarity [%]'
        )
        spectral_angle_name = QApplication.translate(
            'semiautomaticclassificationplugin', 'Spectral angle'
        )
        highlight_color = 'red'
        default_color = 'black'
        if float(spectral_angle) < 10:
            spectra_angle_color = highlight_color
        else:
            spectra_angle_color = default_color
        if float(bray_curtis_similarity) > 90:
            bray_curtis_color = highlight_color
        else:
            bray_curtis_color = default_color
        if float(euclidean_distance) < 0.1:
            euclidean_distance_color = highlight_color
        else:
            euclidean_distance_color = default_color
        tbl = (
            '<table border="1" width="100%"><tr><th bgcolor={} width="30%">'
            '</th><th style="text-align: left">{}#{}; {}#{}</th></tr>'.format(
                color_x, macroclass_x, macroclass_name_x, class_x, class_name_x
            )
        )
        tbl += (
            '<tr><th bgcolor={}></th>'
            '<th style="text-align: left">{}#{}; {}#{}</th></tr>'.format(
                color_y, macroclass_y, macroclass_name_y, class_y, class_name_y
            )
        )
        tbl += (
            '<tr><th style="text-align: right">{}</th>'
            '<td><font color={}>{}</font></td></tr>'.format(
                spectral_angle_name, spectra_angle_color, spectral_angle
            )
        )
        tbl += (
            '<tr><th style="text-align: right">{}</th>'
            '<td><font color={}>{}</font></td></tr>'.format(
                euclidean_distance_name, euclidean_distance_color,
                euclidean_distance
            )
        )
        tbl += (
            '<tr><th style="text-align: right">{}</th>'
            '<td><font color={}>{}</font></td></tr>'.format(
                bray_curtis_similarity_name, bray_curtis_color,
                bray_curtis_similarity
            )
        )
        tbl += '</table><br/>'
        cfg.spectral_plot_dlg.ui.distance_textBrowser.append(tbl)

    # signature list double click
    def signature_list_double_click(self, index):
        table = cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget
        if index.column() == 5:
            color = cfg.util_qt.select_color()
            if color is not None:
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
        elif index.column() == 0:
            self.select_all_signatures()
        self.signature_plot()

    # edited cell
    def edited_cell(self, row, column):
        table = cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget
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
        self.signature_plot()

    # select all signatures
    def select_all_signatures(self):
        # select all
        if self.select_all is True:
            cfg.util_qt.all_items_set_state(
                cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget, 2
            )
            for signature in self.plot_catalog.catalog:
                self.plot_catalog.catalog[signature].selected = 1
            # set check all plot
            self.select_all = False
        # unselect all if previously selected all
        else:
            cfg.util_qt.all_items_set_state(
                cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget, 0
            )
            # set check all plot
            self.select_all = True
            for signature in self.plot_catalog.catalog:
                self.plot_catalog.catalog[signature].selected = 0

    # show signature plot
    def show_signature_plot_t(self):
        self.signature_list_plot_table()
        cfg.spectral_plot_dlg.close()
        cfg.spectral_plot_dlg.show()

    # set plot legend max length
    def set_plot_legend_length(self):
        self.legend_max_chars = (
            cfg.spectral_plot_dlg.ui.plot_text_spinBox.value()
        )

    # sigma checkbox
    def sigma_checkbox(self):
        if cfg.spectral_plot_dlg.ui.sigma_checkBox.isChecked():
            self.sigma_check = True
        else:
            self.sigma_check = False
        # Create plot
        self.signature_plot()

    # grid checkbox
    def grid_checkbox(self):
        if cfg.spectral_plot_dlg.ui.grid_checkBox.isChecked():
            self.ax.grid(True)
        else:
            self.ax.grid(False)
        # Create plot
        self.signature_plot()

    # refresh plot
    def refresh_plot(self):
        self.signature_plot()
