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

import sys
from shutil import copy

from PyQt5.QtCore import QDir

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# Change ROI color
def change_roi_color():
    c = cfg.QtWidgetsSCP.QColorDialog.getColor()
    if c.isValid():
        cfg.qgis_registry[cfg.reg_roi_color] = c.name()
        cfg.dialog.ui.change_color_Button.setStyleSheet(
            'background-color :' + cfg.qgis_registry[cfg.reg_roi_color]
        )


# ROI transparency
def change_roi_transparency():
    cfg.qgis_registry[cfg.reg_roi_transparency] = (
        cfg.dialog.ui.transparency_Slider.value()
    )
    cfg.dialog.ui.transparency_Label.setText(
        cfg.translate('Transparency ')
        + str(cfg.qgis_registry[cfg.reg_roi_transparency]) + '%'
    )


# variable name
def raster_variable_name_change():
    cfg.qgis_registry[cfg.reg_raster_variable_name] = (
        cfg.dialog.ui.variable_name_lineEdit.text()
    )


# group name
def group_name_change():
    cfg.qgis_registry[cfg.reg_group_name] = (
        cfg.dialog.ui.group_name_lineEdit.text()
    )


# download news
def download_news_change():
    if cfg.dialog.ui.download_news_checkBox.isChecked() is True:
        cfg.qgis_registry[cfg.reg_download_news] = 2
    elif cfg.dialog.ui.download_news_checkBox.isChecked() is False:
        cfg.qgis_registry[cfg.reg_download_news] = 0


# checkbox switch sound
def sound_checkbox_change():
    # sound setting
    if cfg.dialog.ui.sound_checkBox.isChecked() is True:
        cfg.qgis_registry[cfg.reg_sound] = 2
    elif cfg.dialog.ui.sound_checkBox.isChecked() is False:
        cfg.qgis_registry[cfg.reg_sound] = 0


# RAM setting
def ram_setting_change():
    cfg.qgis_registry[cfg.reg_ram_value] = cfg.dialog.ui.RAM_spinBox.value()
    cfg.rs.set(available_ram=int(cfg.qgis_registry[cfg.reg_ram_value]))


# thread setting
def threads_setting_change():
    cfg.qgis_registry[
        cfg.reg_threads_value] = cfg.dialog.ui.CPU_spinBox.value()
    cfg.rs.set(n_processes=int(cfg.qgis_registry[cfg.reg_threads_value]))


# reset raster variable names
def reset_raster_variable_name():
    answer = cfg.util_qt.question_box(
        cfg.translate('Reset variable name'),
        cfg.translate('Are you sure you want to reset variable name?')
    )
    if answer is True:
        cfg.qgis_registry[
            cfg.reg_raster_variable_name] = cfg.raster_variable_name_def
        cfg.dialog.ui.variable_name_lineEdit.setText(
            cfg.qgis_registry[cfg.reg_raster_variable_name]
        )


# reset group name
def reset_group_name():
    answer = cfg.util_qt.question_box(
        cfg.translate('Reset group name'),
        cfg.translate('Are you sure you want to reset group name?')
    )
    if answer is True:
        cfg.qgis_registry[cfg.reg_group_name] = cfg.group_name_def
        cfg.dialog.ui.group_name_lineEdit.setText(
            cfg.qgis_registry[cfg.reg_group_name]
        )


# change temporary directory
def change_temp_dir():
    answer = cfg.util_qt.question_box(
        cfg.translate('Change temporary directory'),
        cfg.translate(
            'Are you sure you want to change the temporary directory?'
        )
    )
    if answer is True:
        output = cfg.util_qt.get_existing_directory(
            None, cfg.translate('Select a directory')
        )
        if output is not False:
            if QDir(output).exists():
                date_time = cfg.utils.get_time()
                output_dir = cfg.rs.files_directories.create_directory(
                    '%s/%s' % (output, date_time)
                )
                if output_dir is False:
                    return False
                cfg.temp_dir = '%s/%s' % (output, date_time)
                cfg.dialog.ui.temp_directory_label.setText(output)
                cfg.util_qt.write_registry_keys(cfg.reg_temp_dir, output)
                cfg.rs.set(temporary_directory=cfg.temp_dir)


# reset temporary directory
def reset_temp_dir():
    answer = cfg.util_qt.question_box(
        cfg.translate('Reset temporary directory'),
        cfg.translate(
            'Are you sure you want to reset the temporary directory?'
        )
    )
    if answer is True:
        # noinspection PyArgumentList
        cfg.temp_dir = '%s/%s' % (QDir.tempPath(), cfg.temp_dir_name)
        cfg.util_qt.write_registry_keys(cfg.reg_temp_dir, cfg.temp_dir)
        cfg.dialog.ui.temp_directory_label.setText(cfg.temp_dir)
        cfg.rs.set(temporary_directory=cfg.temp_dir)


# Reset ROI style
def reset_roi_style():
    cfg.qgis_registry[cfg.reg_roi_color] = cfg.roi_color_default
    cfg.qgis_registry[cfg.reg_roi_transparency] = cfg.roi_transparency_default
    cfg.dialog.ui.change_color_Button.setStyleSheet(
        'background-color :' + cfg.qgis_registry[cfg.reg_roi_color]
    )
    cfg.dialog.ui.transparency_Label.setText(
        cfg.translate('Transparency ')
        + str(cfg.qgis_registry[cfg.reg_roi_transparency]) + '%'
    )
    cfg.dialog.ui.transparency_Slider.setValue(
        cfg.qgis_registry[cfg.reg_roi_transparency]
    )


# set variable for raster compression
def raster_compression_checkbox():
    if cfg.dialog.ui.raster_compression_checkBox.isChecked() is True:
        cfg.qgis_registry[cfg.reg_raster_compression] = 2
    else:
        cfg.qgis_registry[cfg.reg_raster_compression] = 0


# smtp server
def smtp_server_change():
    cfg.qgis_registry[
        cfg.reg_smtp_server] = cfg.dialog.ui.smtp_server_lineEdit.text()
    cfg.smtp_server = cfg.qgis_registry[cfg.reg_smtp_server]


# smtp to emails
def smtp_to_emails_change():
    cfg.qgis_registry[
        cfg.reg_smtp_emails] = cfg.dialog.ui.to_email_lineEdit.text()
    cfg.smtp_recipients = cfg.qgis_registry[
        cfg.reg_smtp_emails]


# user
def remember_user():
    if cfg.dialog.ui.remeber_settings_checkBox.isChecked():
        cfg.qgis_registry[
            cfg.reg_smtp_user] = cfg.dialog.ui.smtp_user_lineEdit.text()
        cfg.qgis_registry[cfg.reg_smtp_password] = cfg.utils.encrypt_password(
            cfg.dialog.ui.smtp_password_lineEdit.text()
        )
    cfg.smtp_user = cfg.dialog.ui.smtp_user_lineEdit.text()
    cfg.smtp_password = (
        cfg.dialog.ui.smtp_password_lineEdit.text()
    )


# checkbox remember user
def remember_user_checkbox():
    if cfg.dialog.ui.remeber_settings_checkBox.isChecked():
        remember_user()
    else:
        cfg.qgis_registry[cfg.reg_smtp_user] = ''
    cfg.qgis_registry[cfg.reg_smtp_password] = ''


# checkbox SMTP
def smtp_checkbox():
    # sound setting
    if cfg.dialog.ui.smtp_checkBox.isChecked() is True:
        cfg.qgis_registry[cfg.reg_smtp_check] = 2
        cfg.smtp_notification = True
    elif cfg.dialog.ui.smtp_checkBox.isChecked() is False:
        cfg.qgis_registry[cfg.reg_smtp_check] = 0
        cfg.smtp_notification = False


# GDAL setting
def gdal_path_change():
    if len(cfg.dialog.ui.gdal_path_lineEdit.text()) == 0:
        cfg.qgis_registry[cfg.reg_gdal_path] = ''
    else:
        cfg.qgis_registry[cfg.reg_gdal_path] = (
                cfg.dialog.ui.gdal_path_lineEdit.text().rstrip('/') + '/')


# checkbox switch log
def log_checkbox_change():
    if cfg.dialog.ui.log_checkBox.isChecked() is True:
        cfg.qgis_registry[cfg.reg_log_key] = 2
        if cfg.rs is not None:
            cfg.rs.set(log_level=10)
    elif cfg.dialog.ui.log_checkBox.isChecked() is False:
        cfg.qgis_registry[cfg.reg_log_key] = 0
        if cfg.rs is not None:
            cfg.rs.set(log_level=20)


# copy the Log file
def copy_log_file():
    out = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Save Log file'), '', '*.txt', 'txt'
    )
    if out is not False:
        if not out.lower().endswith('.txt'):
            out += '.txt'
        if cfg.utils.check_file(cfg.rs.configurations.logger.file_path):
            try:
                copy(cfg.rs.configurations.logger.file_path, out)
            except Exception as err:
                str(err)


""" Tests """


# test required dependencies
def test_dependencies():
    message = '<ul>'
    test_numpy_a = test_numpy()
    if test_numpy_a:
        message += '<li>NumPy: %s</li>' % cfg.translate('Success')
    else:
        message += '<li style="color:red">NumPy: %s</li>' % (
            cfg.translate('Fail')
        )
    test_scipy_a = test_scipy()
    if test_scipy_a:
        message += '<li>SciPy: %s</li>' % cfg.translate('Success')
    else:
        message += '<li style="color:red">SciPy: %s</li>' % (
            cfg.translate('Fail'))
    test_matplotlib_a = test_matplotlib()
    if test_matplotlib_a:
        message += '<li>Matplotlib: %s</li>' % cfg.translate('Success')
    else:
        message += '<li style="color:red">Matplotlib: %s' % (
            cfg.translate('Fail'))
    test_gdal_a = test_gdal()
    if test_gdal_a:
        message += '<li>GDAL: %s</li>' % cfg.translate('Success')
    else:
        message += '<li style="color:red">GDAL: %s</li>' % (
            cfg.translate('Fail'))
    test_pytorch_a = test_pytorch()
    if test_pytorch_a:
        message += '<li>PyTorch: %s</li>' % cfg.translate('Success')
    else:
        message += '<li style="color:red">PyTorch: %s</li>' % (
            cfg.translate('Fail')
        )
    test_sklearn_a = test_sklearn()
    if test_sklearn_a:
        message += '<li>scikit-learn: %s</li>' % cfg.translate('Success')
    else:
        message += '<li style="color:red">scikit-learn: %s</li>' % (
            cfg.translate('Fail'))
    test_remotior_sensus_a = test_remotior_sensus()
    if test_remotior_sensus_a:
        message += '<li>Remotior Sensus: %s</li>' % cfg.translate('Success')
    else:
        message += (
                '<li style="color:red">Remotior Sensus: %s. '
                'Please read the %s</li>' % (
                    cfg.translate('Fail'),
                    '<a href="https://remotior-sensus.readthedocs.io/en/latest'
                    '/installation.html">installation manual</a>'
                )
        )
    test_multiprocess_a = test_multiprocess()
    if test_multiprocess_a:
        message += '<li>Multiprocess: %s</li>' % cfg.translate('Success')
    else:
        message += '<li style="color:red">Multiprocess: %s</li>' % (
            cfg.translate('Fail')
        )
        message += '<li>sys.exec_prefix: %s</li>' % str(sys.exec_prefix)
    test_internet_a = test_internet_connection()
    if test_internet_a:
        message += '<li>Internet connection: %s</li>' % cfg.translate(
            'Success'
        )
    else:
        message += '<li style="color:red">Internet connection: %s</li>' % (
            cfg.translate('Fail')
        )
    message += '</ul>'
    cfg.dialog.ui.test_textBrowser.clear()
    cfg.dialog.ui.test_textBrowser.setHtml(message)
    try:
        cfg.logger.log.debug('tests: %s' % message)
    except Exception as err:
        str(err)


# test Remotior Sensus
def test_remotior_sensus():
    test = True
    try:
        import remotior_sensus
        remotior_sensus.Session(n_processes=2, available_ram=10)
    except Exception as err:
        str(err)
        test = False
    return test


# test multiprocess
def test_multiprocess():
    test = True
    try:
        import remotior_sensus
        from remotior_sensus.core.processor_functions import (
            raster_unique_values_with_sum
        )
        rs = remotior_sensus.Session(n_processes=2, available_ram=10)
        raster_path = '%s/debug/raster.tif' % cfg.plugin_dir
        rs.configurations.multiprocess.run(
            raster_path=raster_path, function=raster_unique_values_with_sum,
            n_processes=2, available_ram=100, keep_output_argument=True
        )
    except Exception as err:
        str(err)
        test = False
    return test


# test GDAL
def test_gdal():
    test = True
    try:
        from osgeo import gdal, ogr, osr
        assert gdal.Translate
    except Exception as err:
        str(err)
        test = False
    return test


# test GDAL
def test_pytorch():
    test = True
    try:
        # noinspection PyUnresolvedReferences
        import torch
    except Exception as err:
        str(err)
        test = False
    return test


# test scikit-learn
def test_sklearn():
    test = True
    try:
        from sklearn import svm
    except Exception as err:
        str(err)
        test = False
    return test


# test internet connection
def test_internet_connection():
    test = True
    try:
        from remotior_sensus.util import download_tools
        url = 'https://www.python.org'
        temp = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix='.html'
        )
        download_tools.download_file(url=url, output_path=temp)
    except Exception as err:
        str(err)
        test = False
    return test


# test Numpy
def test_numpy():
    test = True
    try:
        import numpy
        numpy.count_nonzero([1, 1, 0])
    except Exception as err:
        str(err)
        test = False
    return test


# test Scipy
def test_scipy():
    test = True
    try:
        import scipy
    except Exception as err:
        str(err)
        test = False
    return test


# test Matplotlib
def test_matplotlib():
    test = True
    try:
        from matplotlib.ticker import MaxNLocator
    except Exception as err:
        str(err)
        test = False
    return test
