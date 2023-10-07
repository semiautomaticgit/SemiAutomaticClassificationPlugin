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
"""Split bands.

This tool allows for slitting bands of multiband raster.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# refresh reference layer name
def refresh_reference_layer():
    # noinspection PyArgumentList
    layers = cfg.util_qgis.get_qgis_project().mapLayers().values()
    cfg.dialog.ui.raster_name_combo.clear()
    for layer in sorted(layers, key=lambda c: c.name()):
        if layer.type() == cfg.util_qgis.get_qgis_map_raster():
            if layer.bandCount() > 1:
                cfg.dialog.raster_layer_combo(layer.name())


# split raster button
def split_raster():
    split_raster_to_bands()


# split raster to bands
def split_raster_to_bands():
    output_path = cfg.util_qt.get_existing_directory(
        None, cfg.translate('Select a directory')
    )
    if output_path is not False:
        cfg.logger.log.info('split_raster_to_bands: %s' % output_path)
        reference_layer = cfg.dialog.ui.raster_name_combo.currentText()
        reference = cfg.util_qgis.get_file_path(reference_layer)
        if reference is not None:
            prefix = cfg.dialog.ui.output_name_lineEdit.text()
            cfg.ui_utils.add_progress_bar()
            output = cfg.rs.raster_split(
                raster_path=reference, prefix=prefix, output_path=output_path
            )
            if output.check:
                output_paths = output.paths
                for raster in output_paths:
                    # add raster to layers
                    cfg.util_qgis.add_raster_layer(raster)
            else:
                cfg.mx.msg_err_1()
            cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


# set script button
def set_script():
    output_path = 'output_path'
    reference_layer = cfg.dialog.ui.raster_name_combo.currentText()
    reference = cfg.util_qgis.get_file_path(reference_layer)
    prefix = cfg.dialog.ui.output_name_lineEdit.text()
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# split bands \n'
               'rs.raster_split(raster_path="%s", prefix="%s", '
               'output_path="%s")'
               % (str(reference), str(prefix), str(output_path)))
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
