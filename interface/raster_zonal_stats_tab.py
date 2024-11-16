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
"""Raster zonal stats.

This tool allows for the calculation of raster zonal statistics.
"""
from PyQt5.QtWidgets import QApplication

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# raster zonal stats
def raster_zonal_stats_action():
    raster_zonal_stats()


# raster zonal stats
# noinspection PyTypeChecker
def raster_zonal_stats():
    raster_layer = cfg.dialog.ui.classification_name_combo_5.currentText()
    raster = cfg.util_qgis.get_file_path(raster_layer)
    reference_layer = cfg.dialog.ui.reference_name_combo_3.currentText()
    reference = cfg.util_qgis.get_file_path(reference_layer)
    field = cfg.dialog.ui.class_field_comboBox_4.currentText()
    if len(field) == 0:
        field = None
    if raster is not None and reference is not None:
        stat_percentile = None
        # get statistics
        stat_names = []
        if cfg.dialog.ui.count_checkBox.isChecked() is True:
            stat_names.append('Count')
        if cfg.dialog.ui.max_checkBox.isChecked() is True:
            stat_names.append('Max')
        if cfg.dialog.ui.min_checkBox.isChecked() is True:
            stat_names.append('Min')
        if cfg.dialog.ui.mean_checkBox.isChecked() is True:
            stat_names.append('Mean')
        if cfg.dialog.ui.median_checkBox.isChecked() is True:
            stat_names.append('Median')
        if cfg.dialog.ui.percentile_checkBox.isChecked() is True:
            stat_names.append('Percentile')
            percentile = cfg.dialog.ui.percentile_lineEdit.text()
            percentile_split = percentile.split(',')
            stat_percentile = []
            for i in percentile_split:
                try:
                    stat_percentile.append(int(i))
                except Exception as err:
                    str(err)
            if len(stat_percentile) == 0:
                return
        if cfg.dialog.ui.std_checkBox.isChecked() is True:
            stat_names.append('StandardDeviation')
        if cfg.dialog.ui.sum_checkBox.isChecked() is True:
            stat_names.append('Sum')
        if len(stat_names) == 0:
            return
        output_path = cfg.util_qt.get_save_file_name(
            None, QApplication.translate('semiautomaticclassificationplugin',
                                         'Save output'),
            '', 'CSV file (*.csv)'
        )
        if output_path is not False:
            failed = True
            if not output_path.lower().endswith('.csv'):
                output_path += '.csv'
            cfg.logger.log.info('raster zonal stats: %s' % output_path)
            cfg.ui_utils.add_progress_bar()
            output = cfg.rs.raster_zonal_stats(
                raster_path=raster, reference_path=reference,
                vector_field=field, stat_names=stat_names,
                stat_percentile=stat_percentile, output_path=output_path
            )
            if output.check:
                if cfg.utils.check_file(output.path):
                    with open(output.path, 'r') as f:
                        text = f.read()
                    cfg.dialog.ui.raster_zonal_stats_textBrowser.setText(
                        text.replace(',', '\t')
                    )
                    cfg.dialog.ui.toolBox_raster_zonal_stats.setCurrentIndex(1)
                failed = False
            cfg.ui_utils.remove_progress_bar(
                smtp=str(__name__), failed=failed
            )


# refresh reference layer name
def refresh_reference_layer():
    # noinspection PyArgumentList
    layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
    cfg.dialog.ui.reference_name_combo_3.clear()
    for layer in sorted(layers, key=lambda c: c.name()):
        if layer.type() == cfg.util_qgis.get_qgis_map_vector():
            if (layer.wkbType() == cfg.util_qgis.get_qgis_wkb_types().Polygon
                    or layer.wkbType() ==
                    cfg.util_qgis.get_qgis_wkb_types().MultiPolygon):
                cfg.dialog.vector_zonal_raster_combo(layer.name())
        elif layer.type() == cfg.util_qgis.get_qgis_map_raster():
            if layer.bandCount() == 1:
                cfg.dialog.vector_zonal_raster_combo(layer.name())


# reference layer name
def reference_layer_name():
    reference_layer = cfg.dialog.ui.reference_name_combo_3.currentText()
    cfg.dialog.ui.class_field_comboBox_4.clear()
    layer = cfg.util_qgis.select_layer_by_name(reference_layer)
    try:
        if layer.type() == cfg.util_qgis.get_qgis_map_vector():
            fields = layer.dataProvider().fields()
            for field in fields:
                cfg.dialog.zonal_reference_field_combo(str(field.name()))
    except Exception as err:
        str(err)


# set script button
def set_script():
    output_path = 'output_path'
    raster_layer = cfg.dialog.ui.classification_name_combo_5.currentText()
    raster = cfg.util_qgis.get_file_path(raster_layer)
    reference_layer = cfg.dialog.ui.reference_name_combo_3.currentText()
    reference = cfg.util_qgis.get_file_path(reference_layer)
    field = cfg.dialog.ui.class_field_comboBox_4.currentText()
    if len(field) == 0:
        field = None
    stat_percentile = None
    # get statistics
    stat_names = []
    if cfg.dialog.ui.count_checkBox.isChecked() is True:
        stat_names.append('Count')
    if cfg.dialog.ui.max_checkBox.isChecked() is True:
        stat_names.append('Max')
    if cfg.dialog.ui.min_checkBox.isChecked() is True:
        stat_names.append('Min')
    if cfg.dialog.ui.mean_checkBox.isChecked() is True:
        stat_names.append('Mean')
    if cfg.dialog.ui.median_checkBox.isChecked() is True:
        stat_names.append('Median')
    if cfg.dialog.ui.percentile_checkBox.isChecked() is True:
        stat_names.append('Percentile')
        percentile = cfg.dialog.ui.percentile_lineEdit.text()
        percentile_split = percentile.split(',')
        stat_percentile = []
        for i in percentile_split:
            try:
                stat_percentile.append(int(i))
            except Exception as err:
                str(err)
    if cfg.dialog.ui.std_checkBox.isChecked() is True:
        stat_names.append('StandardDeviation')
    if cfg.dialog.ui.sum_checkBox.isChecked() is True:
        stat_names.append('Sum')
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# raster zonal stats \n'
               'rs.raster_zonal_stats(raster_path="%s", reference_path="%s", '
               'vector_field="%s", output_path="%s", stat_names=%s, '
               'stat_percentile=%s)'
               % (str(raster), str(reference), str(field), str(output_path),
                  str(stat_names), str(stat_percentile))
               )
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
