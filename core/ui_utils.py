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


import os
import sys
import ssl
import smtplib

import qgis.core as qgis_core
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    qApp, QWidget, QSizePolicy, QLabel, QSpacerItem, QProgressBar, QPushButton,
    QHBoxLayout, QVBoxLayout, QToolButton, QApplication
)

# sound for Windows
try:
    import winsound
except Exception as error:
    str(error)

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


class UiUtils:
    progress_bar = None
    widget_bar = None
    msg_label_main = None
    msg_label = None
    remaining = ''

    def __init__(self):
        pass

    # add a progress bar and a cancel button
    def add_progress_bar(self, message='', main_message=None):
        # remove if present
        try:
            UiUtils.progress_bar.setValue(0)
        except Exception as err:
            str(err)
            self.create_progress_bar(main_message, message)
        # disable map canvas render for speed
        cfg.map_canvas.setRenderFlag(False)
        qApp.processEvents()

    # Create a progress bar and a cancel button
    # noinspection PyArgumentList,PyUnresolvedReferences,PyTypeChecker
    def create_progress_bar(self, main_message=None, message=''):
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        icon_label = QLabel()
        icon_label.setMinimumSize(QSize(20, 20))
        icon_label.setMaximumSize(QSize(50, 50))
        icon_label.setSizePolicy(size_policy)
        icon_label.setPixmap(
            QPixmap(
                ':/plugins/semiautomaticclassificationplugin/icons/'
                'semiautomaticclassificationplugin.svg'
            )
        )
        UiUtils.msg_label_main = QLabel()
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        UiUtils.msg_label_main.setMinimumSize(QSize(50, 0))
        UiUtils.msg_label_main.setMaximumSize(QSize(800, 30))
        UiUtils.msg_label_main.setSizePolicy(size_policy)
        font = QFont()
        font.setBold(True)
        UiUtils.msg_label_main.setFont(font)
        UiUtils.msg_label_main.setText(
            QApplication.translate('semiautomaticclassificationplugin',
                                   'Semi-Automatic Classification Plugin')
        )
        spacer_item = QSpacerItem(
            40, 20, QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )
        UiUtils.msg_label = QLabel()
        UiUtils.msg_label.setMinimumSize(QSize(50, 0))
        UiUtils.msg_label.setMaximumSize(QSize(600, 80))
        UiUtils.msg_label.setSizePolicy(size_policy)
        UiUtils.msg_label.setWordWrap(True)
        UiUtils.progress_bar = QProgressBar()
        UiUtils.progress_bar.setMinimum(0)
        UiUtils.progress_bar.setMaximum(100)
        UiUtils.progress_bar.setProperty('value', 0)
        UiUtils.progress_bar.setTextVisible(True)
        cancel_button = QPushButton()
        cancel_button.setEnabled(True)
        cancel_button.setText(QApplication.translate(
            'semiautomaticclassificationplugin', 'Cancel'
        ))
        q_widget = QWidget()
        horizontal_layout = QHBoxLayout()
        horizontal_layout2 = QHBoxLayout()
        vertical_layout = QVBoxLayout(q_widget)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addLayout(horizontal_layout2)
        horizontal_layout.addWidget(icon_label)
        horizontal_layout.addWidget(UiUtils.msg_label_main)
        horizontal_layout.addItem(spacer_item)
        horizontal_layout2.addWidget(UiUtils.msg_label)
        horizontal_layout2.addWidget(UiUtils.progress_bar)
        horizontal_layout2.addWidget(cancel_button)
        cancel_button.clicked.connect(self.cancel_action)
        UiUtils.widget_bar = cfg.iface.messageBar().createMessage('', '')
        cfg.iface.messageBar().findChildren(QToolButton)[0].setHidden(True)
        UiUtils.widget_bar.layout().addWidget(q_widget)
        self.update_bar(0, message, main_message)
        cfg.rs.configurations.action = True
        self.set_interface(False)
        cfg.iface.messageBar().pushWidget(
            UiUtils.widget_bar,
            qgis_core.Qgis.Info
        )

    # cancel action
    def cancel_action(self):
        cfg.logger.log.debug('cancel_action')
        self.remove_progress_bar(failed=True)
        cfg.rs.configurations.action = False
        UiUtils.update_bar(100, ' Canceling ...')
        qApp.processEvents()
        self.set_interface(True)
        cfg.map_canvas.setRenderFlag(True)

    # update bar value
    @staticmethod
    def update_bar(
            step=None, message=None, process=None, percentage=None,
            elapsed_time=None, previous_step=None, start=None, end=None,
            failed=None, ping=0
    ):
        progress_symbols = ['○', '◔', '◑', '◕', '⬤', '⚙']
        colon = [' ◵ ', ' ◷ ']
        if start:
            text = '{} {} {}'.format(
                message, progress_symbols[-1], colon[ping]
            )
            try:
                UiUtils.msg_label.setText(text)
                UiUtils.progress_bar.setValue(step)
            except Exception as err:
                str(err)
            if process is not None:
                try:
                    UiUtils.msg_label_main.setText(str(process))
                except Exception as err:
                    str(err)
        elif failed:
            pass
        elif end:
            if elapsed_time is not None:
                e_time = (
                    '(elapsed: {}min{}sec)'.format(
                        int(elapsed_time / 60), str(
                            int(
                                60 * ((elapsed_time / 60) - int(
                                    elapsed_time / 60
                                ))
                            )
                        ).rjust(2, '0')
                    )
                )
            else:
                e_time = ''
            text = '{} - {}'.format(
                progress_symbols[-2], e_time
            )
            try:
                UiUtils.msg_label.setText(text)
                UiUtils.progress_bar.setValue(step)
            except Exception as err:
                str(err)
            try:
                if process is not None:
                    UiUtils.msg_label_main.setText(str(process))
            except Exception as err:
                str(err)
        else:
            if not percentage and percentage is not None:
                percentage = -25
            if elapsed_time is not None:
                e_time = (
                    'elapsed: {}min{}sec'.format(
                        int(elapsed_time / 60), str(
                            int(
                                60 * ((elapsed_time / 60) - int(
                                    elapsed_time / 60
                                ))
                            )
                        ).rjust(2, '0')
                    )
                )
                if previous_step < step:
                    try:
                        remaining_time = (
                                (100 - int(step)) * elapsed_time / int(step)
                        )
                        minutes = int(remaining_time / 60)
                        seconds = round(
                            60 * ((remaining_time / 60)
                                  - int(remaining_time / 60))
                        )
                        if seconds == 60:
                            seconds = 0
                            minutes += 1
                        remaining = '; remaining: {}min{}sec'.format(
                            minutes, str(seconds).rjust(2, '0')
                        )
                        UiUtils.remaining = remaining
                    except Exception as err:
                        str(err)
                        remaining = ''
                else:
                    remaining = UiUtils.remaining
            else:
                e_time = ''
                remaining = ''
            try:
                text = '{} {} - {}{} {}'.format(
                    message, progress_symbols[int(percentage / 25)], e_time,
                    remaining, colon[ping]
                )
                UiUtils.msg_label.setText(text)
                UiUtils.progress_bar.setValue(step)
                qApp.processEvents()
                if process is not None:
                    UiUtils.msg_label_main.setText(str(process))
            except Exception as err:
                str(err)
                if process is not None:
                    try:
                        UiUtils.msg_label_main.setText(str(process))
                    except Exception as err:
                        str(err)

    # remove progress bar and cancel button
    # noinspection PyTypeChecker
    def remove_progress_bar(self, smtp=None, sound=None, failed=None):
        UiUtils.remaining = ''
        try:
            cfg.iface.messageBar().popWidget(UiUtils.widget_bar)
        except Exception as err:
            str(err)
        UiUtils.progress_bar = None
        self.set_interface(True)
        cfg.iface.messageBar().findChildren(QToolButton)[0].setHidden(False)
        cfg.map_canvas.setRenderFlag(True)
        cfg.logger.log.debug('end progress: %s' % smtp)
        if smtp is not None:
            # send SMTP message
            self.send_smtp_message(
                subject=QApplication.translate(
                    'semiautomaticclassificationplugin',
                    'Semi-Automatic Classification Plugin'
                ),
                message=QApplication.translate(
                    'semiautomaticclassificationplugin',
                    '%s: process finished' % smtp
                )
            )
        if sound is not False:
            if failed is True:
                self.failed_sound()
            else:
                self.finish_sound()

    # enable disable the interface to avoid errors
    @staticmethod
    def set_interface(state):
        # classification dock
        cfg.dock_class_dlg.setEnabled(state)
        # main interface
        cfg.dialog.setEnabled(state)
        # toolbar
        cfg.working_toolbar.setEnabled(state)

    # send SMTP message
    @staticmethod
    def send_smtp_message(subject: str = None, message: str = None):
        if cfg.smtp_notification is True:
            try:
                if len(cfg.smtp_server) > 0:
                    server = smtplib.SMTP(cfg.smtp_server, 587)
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                    server.login(cfg.smtp_user, cfg.smtp_password)
                    tolist = cfg.smtp_recipients.split(',')
                    if subject is None:
                        subject = 'completed process'
                    if message is None:
                        message = 'completed process'
                    msg = 'From: %s\nTo: \nSubject: %s\n\n%s' % (
                        cfg.smtp_user, subject, message)
                    server.sendmail(cfg.smtp_user, tolist, msg)
                    server.quit()
            except Exception as err:
                str(err)

    # finish sound
    @staticmethod
    def finish_sound():
        if cfg.qgis_registry[cfg.reg_sound] == 2:
            try:
                beeps(800, 0.2)
                beeps(600, 0.3)
                beeps(700, 0.5)
            except Exception as err:
                str(err)

    # finish sound
    @staticmethod
    def failed_sound():
        if cfg.qgis_registry[cfg.reg_sound] == 2:
            try:
                beeps(700, 0.2)
                beeps(700, 0.1)
            except Exception as err:
                str(err)


# beep sound
def beeps(frequency: int, duration: float):
    if sys.platform.startswith('win'):
        winsound.Beep(frequency, int(duration * 1000))
    elif sys.platform.startswith('linux'):
        os.system(
            'play --no-show-progress --null --channels 1 synth %s sine %s'
            % (str(duration), str(frequency))
        )
