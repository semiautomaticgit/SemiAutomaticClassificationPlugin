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
"""Stack band set.

This tool allows for stacking bands.
"""

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# stack bandset
def stack_action():
    stack_bands()


# stack multiple rasters
def stack_bands():
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_3.value()
    if bandset_number > cfg.bandset_catalog.get_bandset_count():
        cfg.mx.msg_err_2()
        return
    output_path = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Save error matrix raster output'), '',
        'TIF file (*.tif);;VRT file (*.vrt)'
    )
    if output_path is not False:
        if output_path.lower().endswith('.vrt'):
            pass
        elif not output_path.lower().endswith('.tif'):
            output_path += '.tif'
        cfg.logger.log.info('band_sieve: %s' % output_path)
        cfg.logger.log.debug('bandset_number: %s' % bandset_number)
        cfg.ui_utils.add_progress_bar()
        output = cfg.rs.band_stack(
            input_bands=bandset_number, output_path=output_path,
            bandset_catalog=cfg.bandset_catalog
        )
        if output.check:
            cfg.util_qgis.add_raster_layer(output.path)
        else:
            cfg.mx.msg_err_1()
        cfg.ui_utils.remove_progress_bar(smtp=str(__name__))


# set script button
def set_script():
    output_path = 'output_path'
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_3.value()
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    if bandset_x is not None:
        # get input band paths
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
    command = ('# stack bands (input files from bandset)\n'
               'rs.band_stack(input_bands=%s, output_path="%s")'
               % (str(paths), str(output_path)))
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
