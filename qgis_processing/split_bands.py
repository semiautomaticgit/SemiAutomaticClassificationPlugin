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
from qgis.core import (
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterString, QgsRasterLayer, QgsProject,
    QgsProcessingParameterRasterLayer
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class SplitBands(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'split_bands'

    @staticmethod
    def displayName():
        return 'Split raster bands'

    @staticmethod
    def shortDescription():
        return (
            'Perform the split of a raster to single bands. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.raster_split.html">Tool description</a>')  # noqa: E501

    # noinspection PyUnusedLocal
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_RASTER,
                description=self.translate('Input raster')
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT,
                description=self.translate('Output prefix'),
                defaultValue='split_', multiLine=False
            )
        )
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                name=self.OUTPUT,
                description=self.translate('Calculation output')
            )
        )

    @staticmethod
    def icon():
        return QIcon(
            '%s/ui/icons/'
            'semiautomaticclassificationplugin_split_raster.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return SplitBands()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        reference = self.parameterAsFile(
            parameters, self.INPUT_RASTER, context
        )
        prefix = self.parameterAsString(
            parameters, self.TEXT, context
        )
        output_path = self.parameterAsString(
            parameters, self.OUTPUT, context
        )
        try:
            if rs.files_directories.is_directory(output_path) is False:
                rs.files_directories.create_directory(output_path)
        except Exception as err:
            str(err)
        output = rs.raster_split(
            raster_path=reference, prefix=prefix, output_path=output_path
        )
        if output.check:
            paths = output.paths
            for raster in paths:
                layer = QgsRasterLayer(raster, Path(raster).name)
                QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
