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
    QgsProcessingParameterFileDestination, QgsProcessingParameterRasterLayer,
    QgsProject, QgsProcessingParameterString,
    QgsProcessingParameterFile, QgsRasterLayer
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class RasterReclassification(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'raster_reclassification'

    @staticmethod
    def displayName():
        return 'Reclassification'

    @staticmethod
    def shortDescription():
        return (
            'Reclassification of a raster based on a reclassification table. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.raster_reclassification.html">Tool description</a>')  # noqa: E501

    # noinspection PyUnusedLocal
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_RASTER,
                description=self.translate('Input raster')
            )
        )
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT_FILE,
                description=self.translate('Input reclassification table'),
                fileFilter=self.translate(
                    'csv file (*.csv);; txt file (*.txt)'
                )
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT,
                description=self.translate('Separator'),
                defaultValue=',', multiLine=False
            )
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                name=self.OUTPUT,
                description=self.translate('Calculation output'),
                fileFilter=self.translate(
                    'tif file (*.tif);; vrt file (*.vrt)'
                )
            )
        )

    @staticmethod
    def icon():
        return QIcon(
            '%s/ui/icons'
            '/semiautomaticclassificationplugin_reclassification_tool.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return RasterReclassification()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        classification = self.parameterAsFile(
            parameters, self.INPUT_RASTER, context
        )
        root = QgsProject.instance().layerTreeRoot()
        if rs.files_directories.is_file(classification) is False:
            layer_x = root.findLayer(classification)
            classification = layer_x.layer().source()
        csv_path = self.parameterAsFile(
            parameters, self.INPUT_FILE, context
        )
        output_path = self.parameterAsFileOutput(
            parameters, self.OUTPUT, context
        )
        separator = self.parameterAsString(
            parameters, self.TEXT, context
        )
        output = rs.raster_reclassification(
            raster_path=classification, output_path=output_path,
            csv_path=csv_path, separator=separator
        )
        if output.check:
            raster = output.path
            layer = QgsRasterLayer(raster, Path(raster).name)
            QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
