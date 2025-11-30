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

from pathlib import Path

from PyQt5.QtGui import QIcon
# noinspection PyUnresolvedReferences
from qgis.core import (
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterNumber, QgsProcessingParameterField, QgsRasterLayer,
    QgsProject, QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorLayer
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class Accuracy(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'accuracy'

    @staticmethod
    def displayName():
        return 'Accuracy'

    @staticmethod
    def shortDescription():
        return (
            'Perform the accuracy assessment. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.cross_classification.html">Tool description</a>')  # noqa: E501

    # noinspection PyUnusedLocal
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_RASTER,
                description=self.translate('Input raster')
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_RASTER_2,
                description=self.translate('Reference raster'), optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INPUT_VECTOR,
                description=self.translate('Reference vector'), optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                name=self.TEXT,
                description=self.translate('Vector field'),
                defaultValue='class_id',
                parentLayerParameterName=self.INPUT_VECTOR, optional=True
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
                description=self.translate('Calculation output'),
                fileFilter='tif file (*.tif)'
            )
        )

    @staticmethod
    def icon():
        return QIcon(
            '%s/ui/icons/'
            'semiautomaticclassificationplugin_accuracy_tool.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return Accuracy()

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
        reference = self.parameterAsFile(
            parameters, self.INPUT_RASTER_2, context
        )
        if reference is '':
            reference = self.parameterAsFile(
                parameters, self.INPUT_VECTOR, context
            )
        if rs.files_directories.is_file(reference) is False:
            layer_x = root.findLayer(reference)
            reference = layer_x.layer().source().split("|layername=")[0]
        field = self.parameterAsString(parameters, self.TEXT, context)
        if len(field) == 0:
            field = None
        if parameters[self.VALUE] is None:
            nodata = None
        else:
            nodata = self.parameterAsInt(
                parameters, self.VALUE, context
            )
        output_path = self.parameterAsString(
            parameters, self.OUTPUT, context
        )
        output = rs.cross_classification(
            classification_path=classification, reference_path=reference,
            output_path=output_path, vector_field=field, nodata_value=nodata,
            error_matrix=True
        )
        if output.check:
            paths = output.paths
            layer = QgsRasterLayer(paths[0], Path(paths[0]).name)
            QgsProject.instance().addMapLayer(layer)
            self.feedback.pushInfo('Output table: ' + str(paths[1]))

        return {self.OUTPUT: output_path}
