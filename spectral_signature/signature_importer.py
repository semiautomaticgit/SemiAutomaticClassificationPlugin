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


import shutil
import zipfile

from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QApplication
# noinspection PyUnresolvedReferences
from qgis.core import QgsApplication

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


class USGSSpectralLib:

    # noinspection PyTypeChecker
    def __init__(self):
        self.library = None
        self.usgs_lib_name = []
        self.usgs_lib = []
        self.usgs_c1 = QApplication.translate(
            'semiautomaticclassificationplugin', 'Chapter 1: Minerals'
        )
        self.usgs_c2 = QApplication.translate(
            'semiautomaticclassificationplugin',
            'Chapter 2: Soils and Mixtures'
        )
        self.usgs_c3 = QApplication.translate(
            'semiautomaticclassificationplugin', 'Chapter 3: Coatings'
        )
        self.usgs_c4 = QApplication.translate(
            'semiautomaticclassificationplugin', 'Chapter 4: Liquids'
        )
        self.usgs_c5 = QApplication.translate(
            'semiautomaticclassificationplugin', 'Chapter 5: Organics'
        )
        self.usgs_c6 = QApplication.translate(
            'semiautomaticclassificationplugin', 'Chapter 6: Artificial'
        )
        self.usgs_c7 = QApplication.translate(
            'semiautomaticclassificationplugin',
            'Chapter 7: Vegetation and Mixtures'
        )
        self.usgs_lib_list = [
            '', self.usgs_c1, self.usgs_c2, self.usgs_c3, self.usgs_c4,
            self.usgs_c5, self.usgs_c6, self.usgs_c7
        ]
        base_dir = (
                QFileInfo(QgsApplication.qgisUserDatabaseFilePath()).path()
                + '/python/plugins/SemiAutomaticClassificationPlugin/'
                  'spectral_signature/usgs_spectral_library/'
        )
        self.usgs_c1p = base_dir + 'minerals.csv'
        self.usgs_c2p = base_dir + 'soils.csv'
        self.usgs_c3p = base_dir + 'coatings.csv'
        self.usgs_c4p = base_dir + 'liquids.csv'
        self.usgs_c5p = base_dir + 'organics.csv'
        self.usgs_c6p = base_dir + 'artificial.csv'
        self.usgs_c7p = base_dir + 'vegetation.csv'

    # add library list to combo
    def add_libraries_to_combo(self):
        cfg.dialog.ui.usgs_library_comboBox.blockSignals(True)
        cfg.dialog.ui.usgs_library_comboBox.clear()
        cfg.dialog.ui.usgs_library_comboBox.addItem('')
        for i in self.usgs_lib_name:
            cfg.dialog.ui.usgs_library_comboBox.addItem(i)
        cfg.dialog.ui.usgs_library_comboBox.blockSignals(False)

    # selection of chapter
    def chapter_changed(self):
        self.usgs_lib_name = []
        self.usgs_lib = []
        chapter = cfg.dialog.ui.usgs_chapter_comboBox.currentText()
        if chapter == self.usgs_c1:
            usgs_list = self.usgs_c1p
        elif chapter == self.usgs_c2:
            usgs_list = self.usgs_c2p
        elif chapter == self.usgs_c3:
            usgs_list = self.usgs_c3p
        elif chapter == self.usgs_c4:
            usgs_list = self.usgs_c4p
        elif chapter == self.usgs_c5:
            usgs_list = self.usgs_c5p
        elif chapter == self.usgs_c6:
            usgs_list = self.usgs_c6p
        elif chapter == self.usgs_c7:
            usgs_list = self.usgs_c7p
        else:
            cfg.dialog.ui.usgs_library_comboBox.clear()
            return 1
        library = open(usgs_list, 'r')
        for i in library.readlines():
            row = eval(i)
            self.usgs_lib_name.append(row[0])
            self.usgs_lib.append([row[1], row[2]])
        self.add_libraries_to_combo()
        cfg.dialog.ui.USGS_library_textBrowser.setHtml('')

    # selection of library
    def library_changed(self):
        self.library = None
        library_name = cfg.dialog.ui.usgs_library_comboBox.currentText()
        if len(library_name) > 0:
            try:
                library_index = self.usgs_lib_name.index(library_name)
                link, library = self.usgs_lib[library_index]
                temp_path = (
                    cfg.rs.configurations.temp.temporary_file_path(
                        name_suffix='.html'
                    )
                )
                cfg.ui_utils.add_progress_bar()
                check, output = cfg.rs.download_tools.download_file(
                    link, temp_path, timeout=2
                )
                cfg.ui_utils.remove_progress_bar(sound=False)
                if check is True:
                    description = open(temp_path, 'r', errors='ignore')
                    description_html = description.read()
                    cfg.dialog.ui.USGS_library_textBrowser.setHtml(
                        description_html
                    )
                self.library = library
            except Exception as err:
                cfg.logger.log.error(str(err))
                cfg.mx.msg_err_5()
        else:
            cfg.dialog.ui.USGS_library_textBrowser.setHtml('')

    # download signature file
    @staticmethod
    def download_library(link):
        temp_path = (
            cfg.rs.configurations.temp.temporary_file_path(
                name_suffix='.zip'
            )
        )
        cfg.ui_utils.add_progress_bar()
        try:
            check, output = cfg.rs.download_tools.download_file(
                link, temp_path, timeout=2
            )
        except Exception as err:
            str(err)
            check = False
        cfg.ui_utils.remove_progress_bar(sound=False)
        if check is False:
            cfg.mx.msg_err_5()
            return None, None, None
        else:
            (reflectance, wavelength_list,
             standard_deviation_list) = unzip_library(temp_path)
            return reflectance, wavelength_list, standard_deviation_list

    # add signature to catalog
    def add_signature_to_catalog(self):
        library_name = cfg.dialog.ui.usgs_library_comboBox.currentText()
        if self.library is not None:
            cfg.logger.log.debug('self.library: %s' % self.library)
            if len(str(self.library)) > 0:
                cfg.ui_utils.add_progress_bar()
                reflectance, wavelength, std = self.download_library(
                    self.library
                )
                # add to training
                if reflectance is not None:
                    cfg.scp_training.save_temporary_signature_catalog()
                    signature_catalog = (
                        cfg.scp_training.signature_catalog_copy()
                    )
                    cfg.scp_training.set_signature_catalog(
                        signature_catalog=signature_catalog
                    )
                    cfg.scp_training.add_spectral_signature_to_catalog(
                        values=reflectance, wavelengths=wavelength,
                        standard_deviations=std, class_name=library_name
                    )
                    cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(True)
                    cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
                cfg.ui_utils.remove_progress_bar()
                cfg.logger.log.debug(
                    'add_signature_to_catalog: %s' % library_name
                )

    # add chapter list to combo
    def add_spectral_library_to_combo(self):
        for i in self.usgs_lib_list:
            cfg.dialog.ui.usgs_chapter_comboBox.addItem(i)


def import_usgs_library(file_path):
    cfg.logger.log.debug('import_usgs_library: %s' % file_path)
    cfg.ui_utils.add_progress_bar()
    reflectance, wavelength, std = unzip_library(file_path)
    # add to training
    if reflectance is not None:
        cfg.scp_training.add_spectral_signature_to_catalog(
            values=reflectance, wavelengths=wavelength,
            standard_deviations=std, class_name='imported'
        )
    cfg.ui_utils.remove_progress_bar()


def unzip_library(file_path):
    reflectance = []
    wavelength_list = []
    standard_deviation_list = []
    zero_standard_deviation = []
    with zipfile.ZipFile(file_path) as open_file:
        for file_name in open_file.namelist():
            if file_name.endswith('.txt'):
                # noinspection SpellCheckingInspection
                if 'REF' in file_name and 'errorbars' not in file_name:
                    unzip_file = open_file.open(file_name)
                    temp_text = (
                        cfg.rs.configurations.temp.temporary_file_path(
                            name_suffix='.txt'
                        )
                    )
                    try:
                        unzip_temp_text = open(temp_text, 'wb')
                        with unzip_file, unzip_temp_text:
                            shutil.copyfileobj(
                                unzip_file, unzip_temp_text
                            )
                        unzip_temp_text.close()
                        open_text = open(temp_text)
                        file = open_text.readlines()
                        for b in range(1, len(file)):
                            value = float(file[b])
                            if value < 0:
                                value = 0
                            reflectance.append(value)
                            zero_standard_deviation.append(0)
                    except Exception as err:
                        str(err)
                elif 'Wavelengths' in file_name:
                    unzip_file = open_file.open(file_name)
                    temp_text = (
                        cfg.rs.configurations.temp.temporary_file_path(
                            name_suffix='.txt'
                        )
                    )
                    try:
                        unzip_temp_text = open(temp_text, 'wb')
                        with unzip_file, unzip_temp_text:
                            shutil.copyfileobj(
                                unzip_file, unzip_temp_text
                            )
                        unzip_temp_text.close()
                        open_text = open(temp_text)
                        file = open_text.readlines()
                        for b in range(1, len(file)):
                            wavelength_list.append(float(file[b]))
                    except Exception as err:
                        str(err)
                elif 'errorbars' in file_name:
                    unzip_file = open_file.open(file_name)
                    temp_text = (
                        cfg.rs.configurations.temp.temporary_file_path(
                            name_suffix='.txt'
                        )
                    )
                    try:
                        unzip_temp_text = open(temp_text, 'wb')
                        with unzip_file, unzip_temp_text:
                            shutil.copyfileobj(
                                unzip_file, unzip_temp_text
                            )
                        unzip_temp_text.close()
                        open_text = open(temp_text)
                        file = open_text.readlines()
                        for b in range(1, len(file)):
                            value = float(file[b])
                            standard_deviation_list.append(value)
                    except Exception as err:
                        str(err)
    if len(standard_deviation_list) == 0:
        standard_deviation_list = zero_standard_deviation
    return reflectance, wavelength_list, standard_deviation_list


# import ASTER spectral library (http://speclib.jpl.nasa.gov/search-1)
def aster_library(file_path):
    if cfg.utils.check_file(file_path):
        cfg.logger.log.debug('aster_library: %s' % file_path)
        library = open(file_path)
        lines = library.readlines()
        if 'Name' in lines[0]:
            wavelength = []
            reflectance = []
            standard_deviation = []
            for line in range(26, len(lines)):
                value = lines[line].split()
                wavelength.append(float(value[0]))
                reflectance.append(float(value[1]) / 100)
                standard_deviation.append(float(0))
            # add to training
            if len(reflectance) > 0:
                cfg.scp_training.add_spectral_signature_to_catalog(
                    values=reflectance, wavelengths=wavelength,
                    standard_deviations=standard_deviation,
                    class_name='imported'
                )
            cfg.logger.log.debug('values: %s' % len(reflectance))
        else:
            # try to open as csv
            cfg.scp_training.import_csv_file(file_path)
