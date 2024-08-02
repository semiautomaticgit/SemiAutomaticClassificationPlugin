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


from PyQt5.QtWidgets import qApp, QApplication
cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# clear text
# noinspection PyTypeChecker
def clear_text():
    answer = cfg.util_qt.question_box(
        QApplication.translate('semiautomaticclassificationplugin',
                               'Clear script'),
        QApplication.translate('semiautomaticclassificationplugin',
                               'Are you sure you want to clear the script?')
    )
    if answer is True:
        cfg.dialog.ui.plainTextEdit_batch.setPlainText('')


# copy text
def copy_text():
    text = cfg.dialog.ui.plainTextEdit_batch.toPlainText()
    clipboard = qApp.clipboard()
    clipboard.setText(text)


# save script to file
# noinspection PyTypeChecker
def save_script():
    output_path = cfg.util_qt.get_save_file_name(
        None, QApplication.translate('semiautomaticclassificationplugin',
                                     'Save script'), '',
        'Python file (*.py)'
    )
    if output_path is not False:
        if output_path.lower().endswith('.py'):
            pass
        else:
            output_path = output_path + '.py'
        text = cfg.dialog.ui.plainTextEdit_batch.toPlainText()
        with open(output_path, 'w') as output_file:
            output_file.write(text)
