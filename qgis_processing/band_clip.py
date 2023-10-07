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
    QgsProcessingParameterString, QgsRasterLayer,
    QgsProcessingParameterMultipleLayers, QgsProcessing, QgsProject,
    QgsProcessingParameterBoolean, QgsProcessingParameterVectorLayer
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class BandClip(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'band_clip'

    @staticmethod
    def displayName():
        return 'Clip raster bands'

    @staticmethod
    def shortDescription():
        return (
            'Perform the clipping of raster bands based on a vector or extent '
            'coordinate list. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.band_clip.html">Tool description</a>')  # noqa: E501

    # noinspection PyUnusedLocal
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                name=self.MULTIPLE_LAYERS,
                description=self.translate('Input raster list'),
                layerType=QgsProcessing.TypeRaster
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.INPUT_LIST,
                description=self.translate(
                    'Extent coordinates (in the order Minimum X, Maximum Y, '
                    'Maximum X, Minimum Y), separated by comma'
                ),
                defaultValue='', multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INPUT_VECTOR,
                description=self.translate('Reference vector'), optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT,
                description=self.translate('Vector field'),
                defaultValue='', multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT_2,
                description=self.translate('Output name'),
                defaultValue='clip_', multiLine=False
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL,
                description=self.translate('Virtual output'),
                defaultValue=None, optional=True
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
            'semiautomaticclassificationplugin_clip_tool.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return BandClip()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        input_raster_list = self.parameterAsFileList(
            parameters, self.MULTIPLE_LAYERS, context
        )
        input_coordinates = self.parameterAsStrings(
            parameters, self.INPUT_LIST, context
        )
        values = []
        for name in input_coordinates[0].split(','):
            values.append(int(name.strip()))
        if len(values) == 0:
            values = None
        if self.INPUT_VECTOR is None:
            reference = None
        else:
            reference = self.parameterAsFile(
                parameters, self.INPUT_VECTOR, context
            )
        field = self.parameterAsString(parameters, self.TEXT, context)
        if len(field) == 0:
            field = None
        output_name = self.parameterAsString(
            parameters, self.TEXT_2, context
        )
        if parameters[self.BOOL] is None:
            virtual_output = None
        else:
            virtual_output = self.parameterAsBool(
                parameters, self.BOOL, context
            )
        output_path = self.parameterAsString(
            parameters, self.OUTPUT, context
        )
        try:
            if rs.files_directories.is_directory(output_path) is False:
                rs.files_directories.create_directory(output_path)
        except Exception as err:
            str(err)
        root = QgsProject.instance().layerTreeRoot()
        input_bands = []
        for raster in input_raster_list:
            if rs.files_directories.is_file(raster) is False:
                layer_x = root.findLayer(raster)
                input_bands.append(layer_x.layer().source())
            else:
                input_bands.append(raster)
        output = rs.band_clip(
            input_bands=input_bands, output_path=output_path,
            vector_path=reference, vector_field=field,
            prefix=output_name, extent_list=values,
            virtual_output=virtual_output
        )
        if output.check:
            paths = output.paths
            for raster in paths:
                layer = QgsRasterLayer(raster, Path(raster).name)
                QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
