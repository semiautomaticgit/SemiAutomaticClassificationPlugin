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
    QgsProcessingParameterNumber, QgsProject
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class RasterReport(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'raster_report'

    @staticmethod
    def displayName():
        return 'Classification report'

    @staticmethod
    def shortDescription():
        return ('Calculate report of classes. '
                '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.raster_report.html">Tool description</a>')  # noqa: E501

    # noinspection PyUnusedLocal
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_RASTER,
                description=self.translate('Input raster')
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE,
                description=self.translate('NoData value'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                name=self.OUTPUT,
                description=self.translate('Classification report'),
                fileFilter=self.translate('csv file (*.csv)')
            )
        )

    @staticmethod
    def icon():
        return QIcon(
            '%s/ui/icons/semiautomaticclassificationplugin_report_tool.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return RasterReport()

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
        if parameters[self.VALUE] is None:
            nodata = None
        else:
            nodata = self.parameterAsInt(
                parameters, self.VALUE, context
            )
        output_path = self.parameterAsFileOutput(
            parameters, self.OUTPUT, context
        )
        rs.raster_report(
            raster_path=classification, output_path=output_path,
            nodata_value=nodata
        )
        return {self.OUTPUT: output_path}
