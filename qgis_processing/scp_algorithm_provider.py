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

from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
# noinspection PyUnresolvedReferences
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from qgis.core import QgsProcessingProvider, QgsRuntimeProfiler

from .accuracy import Accuracy
from .band_calc import BandCalc
from .band_clip import BandClip
from .band_combination import BandCombination
from .band_dilation import BandDilation
from .band_erosion import BandErosion
from .band_pca import BandPCA
from .band_neighbor import BandNeighbor
from .band_sieve import BandSieve
from .classification import Classification
from .cross_classification import CrossClassification
from .image_conversion import ImageConversion
from .masking_bands import MaskingBands
from .raster_report import RasterReport
from .raster_reclassification import RasterReclassification
from .raster_to_vector import RasterToVector
from .reproject_raster_bands import ReprojectRasterBands
from .split_bands import SplitBands
from .stack_bands import StackBands


""" Class to manage QGIS Processing algorithms """


# noinspection PyPep8Naming
class SCPAlgorithmProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()
        self.algorithm_list = [
            Accuracy, BandCalc, BandClip, BandCombination, BandErosion,
            BandPCA, BandDilation, BandNeighbor, BandSieve, Classification,
            CrossClassification, ImageConversion, MaskingBands, RasterReport,
            RasterReclassification, RasterToVector, ReprojectRasterBands,
            SplitBands, StackBands
        ]

    def load(self):
        try:
            with QgsRuntimeProfiler.profile('SCP Provider'):
                group = self.name()
                ProcessingConfig.settingIcons[group] = self.icon()
                ProcessingConfig.setGroupIcon(self.name(), self.icon())
                ProcessingConfig.addSetting(
                    Setting(
                        group, 'SCP_N_PROCESSES',
                        self.translate('Number of parallel processes'), 2,
                        valuetype=Setting.INT
                    )
                )
                ProcessingConfig.addSetting(
                    Setting(
                        group, 'SCP_MEMORY',
                        self.translate('Available RAM in MB'),
                        2048, valuetype=Setting.INT
                    )
                )
                ProcessingConfig.addSetting(
                    Setting(group, 'SCP_ACTIVATE', 'Activate', True)
                )
                ProcessingConfig.readSettings()
                self.refreshAlgorithms()
            return True
        except Exception as err:
            str(err)
            group = self.name()
            ProcessingConfig.settingIcons[group] = self.icon()
            ProcessingConfig.setGroupIcon(self.name(), self.icon())
            ProcessingConfig.addSetting(
                Setting(
                    group, 'SCP_N_PROCESSES',
                    self.translate('Number of parallel processes'), 2,
                    valuetype=Setting.INT
                )
            )
            ProcessingConfig.addSetting(
                Setting(
                    group, 'SCP_MEMORY',
                    self.translate('Available RAM in MB'),
                    2048, valuetype=Setting.INT
                )
            )
            ProcessingConfig.addSetting(
                Setting(group, 'SCP_ACTIVATE', 'Activate', True)
            )
            ProcessingConfig.readSettings()
            self.refreshAlgorithms()
            return True

    @staticmethod
    def unload():
        ProcessingConfig.removeSetting('SCP_N_PROCESSES')
        ProcessingConfig.removeSetting('SCP_MEMORY')
        ProcessingConfig.removeSetting('SCP_ACTIVATE')

    @staticmethod
    def icon():
        return QIcon(
            '%s/ui/icons/semiautomaticclassificationplugin.svg' %
            Path(__file__).parent.parent
        )

    # noinspection PyTypeChecker
    @staticmethod
    def translate(text):
        return QApplication.translate(
            'semiautomaticclassificationplugin',
            text
        )

    def loadAlgorithms(self):
        for algorithm in self.algorithm_list:
            self.addAlgorithm(algorithm())

    @staticmethod
    def name():
        return 'Semi-Automatic Classification Plugin'

    @staticmethod
    def longName():
        return 'Semi-Automatic Classification Plugin'

    @staticmethod
    def id():
        return 'scp_8'

    @staticmethod
    def versionInfo():
        return '8.0.0'

    @staticmethod
    def isActive():
        return ProcessingConfig.getSetting('SCP_ACTIVATE')
