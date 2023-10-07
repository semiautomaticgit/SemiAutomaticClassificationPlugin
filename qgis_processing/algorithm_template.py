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

import multiprocessing
import platform
import sys
from os import path

from PyQt5.QtWidgets import QApplication
# noinspection PyUnresolvedReferences
from processing.core.ProcessingConfig import ProcessingConfig
from qgis.core import QgsProcessingAlgorithm, Qgis, QgsMessageLog

try:
    import remotior_sensus
except Exception as error:
    str(error)
    QgsMessageLog.logMessage(str(error), 'remotior_sensus', Qgis.Info)


class AlgorithmTemplate(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()
        self.rs = None
        self.remaining_time = None
        self.feedback = None
        self.INPUT_RASTER = 'INPUT_RASTER'
        self.INPUT_RASTER_2 = 'INPUT_RASTER_2'
        self.INPUT_FILE = 'INPUT_FILE'
        self.INPUT_FILE_2 = 'INPUT_FILE_2'
        self.INPUT_DIRECTORY = 'INPUT_DIRECTORY'
        self.INPUT_VECTOR = 'INPUT_VECTOR'
        self.MULTIPLE_LAYERS = 'MULTIPLE_LAYERS'
        self.INPUT_LIST = 'INPUT_LIST'
        self.INPUT_LIST_2 = 'INPUT_LIST_2'
        self.OUTPUT = 'OUTPUT'
        self.VALUE = 'VALUE'
        self.VALUE_2 = 'VALUE_2'
        self.VALUE_3 = 'VALUE_3'
        self.VALUE_4 = 'VALUE_4'
        self.VALUE_5 = 'VALUE_5'
        self.VALUE_6 = 'VALUE_6'
        self.VALUE_7 = 'VALUE_7'
        self.VALUE_8 = 'VALUE_8'
        self.VALUE_9 = 'VALUE_9'
        self.TEXT = 'TEXT'
        self.TEXT_2 = 'TEXT_2'
        self.TEXT_3 = 'TEXT_3'
        self.TEXT_4 = 'TEXT_4'
        self.TEXT_5 = 'TEXT_5'
        self.BOOL = 'BOOL'
        self.BOOL_2 = 'BOOL_2'
        self.BOOL_3 = 'BOOL_3'
        self.BOOL_4 = 'BOOL_4'
        self.BOOL_5 = 'BOOL_5'
        self.BOOL_6 = 'BOOL_6'
        self.BOOL_7 = 'BOOL_7'
        self.BOOL_8 = 'BOOL_8'
        self.BOOL_9 = 'BOOL_9'
        self.BOOL_10 = 'BOOL_10'
        self.ENUMERATOR = 'ENUMERATOR'
        self.ENUMERATOR_2 = 'ENUMERATOR_2'
        self.ENUMERATOR_3 = 'ENUMERATOR_3'

    @staticmethod
    def group():
        return 'Remotior Sensus'

    # noinspection PyPep8Naming
    @staticmethod
    def groupId():
        return 'remotior_sensus'

    # noinspection PyTypeChecker
    @staticmethod
    def translate(text):
        return QApplication.translate(
            'semiautomaticclassificationplugin',
            text
        )

    def start_remotior_sensus_session(self):
        try:
            multiprocessing.set_start_method('spawn')
        except Exception as err:
            str(err)
        if platform.system() == 'Windows':
            try:
                python_path = path.abspath(
                    path.join(sys.exec_prefix, 'pythonw.exe')
                )
                if path.isfile(python_path):
                    multiprocessing.set_executable(python_path)
                else:
                    # from https://trac.osgeo.org/osgeo4w/ticket/392
                    python_path = path.abspath(
                        path.join(sys.exec_prefix, '../../bin/pythonw.exe')
                    )
                    if path.isfile(python_path):
                        multiprocessing.set_executable(python_path)
                    else:
                        self.feedback.reportError(
                            'Error. Python library not found'
                        )
            except Exception as err:
                str(err)
        self.feedback.pushDebugInfo(
            'SCP_N_PROCESSES %s'
            % ProcessingConfig.getSetting('SCP_N_PROCESSES')
        )
        self.feedback.pushDebugInfo(
            'SCP_MEMORY' + str(ProcessingConfig.getSetting('SCP_MEMORY'))
        )
        rs = remotior_sensus.Session(
            n_processes=int(ProcessingConfig.getSetting('SCP_N_PROCESSES')),
            log_level=20,
            available_ram=int(ProcessingConfig.getSetting('SCP_MEMORY')),
            multiprocess_module=multiprocessing,
            progress_callback=self.print_progress,
            messages_callback=MessagesCallback(self.feedback)
        )
        rs.configurations.logger.log.info = self.feedback.pushConsoleInfo
        rs.configurations.logger.log.debug = self.feedback.pushDebugInfo
        rs.configurations.logger.log.error = self.feedback.reportError
        return rs

    # print progress always in a new line
    def print_progress(
            self, process=None, step=None, message=None, percentage=None,
            elapsed_time=None, previous_step=None, start=None, end=None,
            ping=0
    ):
        progress_symbols = ['○', '◔', '◑', '◕', '⬤', '⚙']
        colon = [' ', ':']
        if start:
            text = (
                '{} [{}%]{}{}:{} {}'.format(
                    process, str(100).rjust(3, ' '), '', '',
                    message, progress_symbols[-2]
                )
            )
            try:
                if self.feedback.isCanceled():
                    self.rs.configurations.action = False
                self.feedback.setProgressText(text)
            except Exception as err:
                str(err)
        elif end:
            self.feedback.setProgressText('')
            self.feedback.setProgress(100)
        else:
            if not percentage and percentage is not None:
                percentage = -25
            if elapsed_time is not None:
                e_time = (' [elapsed {}min{}sec]'.format(
                    int(elapsed_time / 60), str(
                        int(
                            60 * (
                                    (elapsed_time / 60)
                                    - int(elapsed_time / 60))
                        )
                    ).rjust(2, '0')
                ))
                if previous_step < step:
                    try:
                        remaining_time = (
                                (100 - int(step)) * elapsed_time / int(step))
                        minutes = int(remaining_time / 60)
                        seconds = round(
                            60 * ((remaining_time / 60)
                                  - int(remaining_time / 60))
                        )
                        if seconds == 60:
                            seconds = 0
                            minutes += 1
                        remaining = ' [remaining {}min{}sec]'.format(
                            minutes, str(seconds).rjust(2, '0')
                        )
                        self.remaining_time = remaining
                    except Exception as err:
                        str(err)
                        remaining = ''
                else:
                    remaining = self.remaining_time
            else:
                e_time = ''
                remaining = ''
            try:
                text = (
                    '{} [{}%]{}{}{}{} {}'.format(
                        process, str(step).rjust(3, ' '), e_time, remaining,
                        colon[ping],
                        message, progress_symbols[int(percentage / 25)]
                    )
                )
            except Exception as err:
                str(err)
                text = (str(process))
            try:
                if self.feedback.isCanceled():
                    self.rs.configurations.action = False
                self.feedback.setProgress(int(step))
                self.feedback.setProgressText(text)
            except Exception as err:
                str(err)


""" Class for messages """


class MessagesCallback:

    def __init__(self, feedback):
        self.feedback = feedback

    def warning(self, text):
        self.feedback.pushWarning(text)
        return text

    def info(self, text):
        self.feedback.pushDebugInfo(text)
        return text

    def error(self, text):
        self.feedback.reportError(text)
        return text
