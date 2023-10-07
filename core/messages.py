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


from PyQt5.QtWidgets import QMessageBox, QToolButton
from qgis.core import Qgis

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# message box information
def msg_box(title, message):
    QMessageBox.information(cfg.iface.mainWindow(), str(title), str(message))


# message box error
def msg_box_error(title, message):
    QMessageBox.critical(cfg.iface.mainWindow(), title, message)


# message box warning
def msg_box_warning(title, message):
    QMessageBox.warning(cfg.iface.mainWindow(), title, message)


# message bar information
def msg_bar(title, message):
    cfg.iface.messageBar().pushMessage(
        title, message, level=Qgis.Info, duration=7
    )
    cfg.iface.messageBar().findChildren(QToolButton)[0].setHidden(False)


# message bar information
def msg_bar_info(message):
    msg_bar(cfg.translate('SCP information'), message)


# Message bar error
def msg_bar_critical(title, message):
    cfg.iface.messageBar().pushMessage(
        title, message, level=Qgis.Critical
    )
    cfg.iface.messageBar().findChildren(
        QToolButton
    )[0].setHidden(False)


# Message bar error
def msg_bar_error(message):
    msg_bar_critical(cfg.translate('Error'), message=message)


# message bar warning
def _msg_bar_warning(title, message):
    cfg.iface.messageBar().pushMessage(
        title, message, level=Qgis.Warning, duration=7
    )
    cfg.iface.messageBar().findChildren(
        QToolButton
    )[0].setHidden(False)


# message bar warning
def msg_bar_warning(message):
    _msg_bar_warning(title=cfg.translate('Warning'), message=message)


''' Messages for callback '''


def info(message):
    msg_bar('SCP', message)


def warning(message):
    if 'dependency error' in message:
        if cfg.first_install == 1:
            _msg_bar_warning('SCP', message)
    else:
        _msg_bar_warning('SCP', message)


def error(message):
    msg_bar_critical('SCP', message)


''' Information '''


def msg_test(message):
    msg_box(cfg.translate('Test results'), message)


def msg_inf_1():
    msg_bar_info(cfg.translate('Training input cannot be edited'))


def msg_inf_2():
    msg_bar_info(cfg.translate('At least 3 points are required'))


def msg_inf_3():
    msg_bar_info(cfg.translate('Detailed log is active'))


def msg_inf_4():
    msg_bar_info(cfg.translate('Training vector exported'))


def msg_inf_5():
    msg_bar_info(cfg.translate('Enter class values'))


def msg_inf_6():
    msg_bar_info(cfg.translate('Process completed'))


""" Errors """


def msg_err_1():
    msg_bar_error(cfg.translate('Process failed'))


def msg_err_2():
    msg_bar_error(cfg.translate('Bandset not found'))


def msg_err_3():
    msg_bar_error(cfg.translate('Area coordinates error'))


def msg_err_4():
    msg_bar_error(cfg.translate('Unable to create RGB color composite'))


def msg_err_5():
    msg_bar_error(cfg.translate('Unable to open file'))


def msg_err_6():
    msg_bar_error(cfg.translate('Unable to calculate'))


def msg_err_7():
    msg_bar_error(cfg.translate('Expression error'))


""" Warnings """


def msg_war_1():
    msg_bar_warning(cfg.translate('Pixel resolution undefined'))


def msg_war_2():
    msg_bar_warning(
        cfg.translate(
            'Unable to define hidden layer size, setting default 100'
        )
    )


def msg_war_3():
    msg_bar_warning(
        cfg.translate(
            'Point outside band set or band set not defined'
        )
    )


def msg_war_4():
    msg_bar_warning(cfg.translate('ROI not found'))


def msg_war_5():
    msg_bar_warning(
        cfg.translate(
            'Select a training input; input is not loaded'
        )
    )


def msg_war_6(bandset_number=None):
    msg_bar_warning(
        cfg.translate('Band set') + ' ' + str(bandset_number) + ' '
        + cfg.translate('is empty')
    )


def msg_war_7():
    msg_bar_warning(cfg.translate(
        'No band found. Check metadata inside the directory')
    )


def msg_war_8():
    msg_bar_warning(cfg.translate('No tool selected'))
