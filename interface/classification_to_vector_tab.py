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
"""Classification to vector.

This tool allows for the conversion from raster to vector.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# convert classification to vector
def convert_classification_to_vector_action():
    convert_classification_to_vector()


# convert classification to vector
def convert_classification_to_vector():
    output_path = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Save vector output'), '', '*.gpkg', 'gpkg'
    )
    if output_path is not False:
        if not output_path.lower().endswith('.gpkg'):
            output_path += '.gpkg'
        cfg.logger.log.info(
            'convert_classification_to_vector: %s'
            % output_path
        )
        classification_layer = (
            cfg.dialog.ui.classification_vector_name_combo.currentText())
        classification = cfg.util_qgis.get_file_path(classification_layer)
        try:
            if (cfg.dialog.ui.class_macroclass_comboBox.currentText()
                    == 'MC_ID'):
                macroclass = True
            else:
                macroclass = False
            value_name_dictionary, value_color_dictionary = (
                cfg.scp_dock.export_symbology(macroclass)
            )
        except Exception as err:
            str(err)
            value_name_dictionary = value_color_dictionary = None
        if cfg.dialog.ui.dissolve_output_checkBox.isChecked() is True:
            dissolve = True
        else:
            dissolve = False
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.raster_to_vector(
            raster_path=classification, output_path=output_path,
            dissolve=dissolve
        )
        if output.check:
            output_vector = output.path
            layer = cfg.util_qgis.add_vector_layer(path=output_vector)
            if (cfg.dialog.ui.use_class_code_checkBox.isChecked() is True
                    and value_name_dictionary is not None):
                cfg.utils.vector_symbol(
                    layer, value_name_dictionary, value_color_dictionary
                )
                # save qml file
                name = cfg.rs.files_directories.file_name(output_vector)
                cfg.util_qgis.save_qml_style(
                    layer, ''.join(
                        [cfg.utils.directory_name(output_vector), '/', name,
                         '.qml']
                    )
                )
            cfg.util_qgis.add_layer_to_map(layer)
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


# set script button
def set_script():
    output_path = 'output_path'
    classification_layer = (
        cfg.dialog.ui.classification_vector_name_combo.currentText())
    classification = cfg.util_qgis.get_file_path(classification_layer)
    if cfg.dialog.ui.dissolve_output_checkBox.isChecked() is True:
        dissolve = True
    else:
        dissolve = False
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# classification to vector \n'
               'rs.raster_to_vector(raster_path="%s", output_path="%s", '
               'dissolve=%s)'
               % (str(classification), str(output_path), str(dissolve)))
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
