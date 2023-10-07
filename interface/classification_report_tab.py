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
"""Classification report.

This tool allows for the classification report.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# calculate classification report if click on button
def calculate_classification_report():
    output_path = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Save classification report'), '', '*.csv', 'csv'
    )
    if output_path is not False:
        if not output_path.lower().endswith('.csv'):
            output_path += '.csv'
        cfg.logger.log.info(
            'calculate_classification_report: %s'
            % output_path
        )
        classification_layer = (
            cfg.dialog.ui.classification_report_name_combo.currentText())
        classification = cfg.util_qgis.get_file_path(classification_layer)
        cfg.logger.log.debug('classification: %s' % classification)
        # No data value
        if cfg.dialog.ui.nodata_checkBox.isChecked() is True:
            nodata = cfg.dialog.ui.nodata_spinBox_2.value()
        else:
            nodata = None
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.raster_report(
            raster_path=classification, output_path=output_path,
            nodata_value=nodata
        )
        if output.check:
            output_table = output.path
            if cfg.utils.check_file(output_table):
                with open(output_table, 'r') as f:
                    text = f.read()
                cfg.dialog.ui.report_textBrowser.setText(
                    text.replace(',', '\t')
                )
                cfg.dialog.ui.toolBox_class_report.setCurrentIndex(1)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


# set script button
def set_script():
    output_path = 'output_path'
    classification_layer = (
        cfg.dialog.ui.classification_report_name_combo.currentText())
    classification = cfg.util_qgis.get_file_path(classification_layer)
    # No data value
    if cfg.dialog.ui.nodata_checkBox.isChecked() is True:
        nodata = cfg.dialog.ui.nodata_spinBox_2.value()
    else:
        nodata = None
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# classification report \n'
               'rs.raster_report(raster_path="%s", output_path="%s", '
               'nodata_value=%s)'
               % (str(classification), str(output_path), str(nodata)))
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
