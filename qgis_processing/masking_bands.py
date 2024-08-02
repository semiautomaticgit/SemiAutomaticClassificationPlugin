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
    QgsProcessingParameterFolderDestination, QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber, QgsProcessingParameterString, QgsRasterLayer,
    QgsProcessingParameterMultipleLayers, QgsProcessing, QgsProject,
    QgsProcessingParameterBoolean
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class MaskingBands(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'masking_bands'

    @staticmethod
    def displayName():
        return 'Masking bands'

    @staticmethod
    def shortDescription():
        return (
            'Perform the masking of bands based on a raster mask. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.band_mask.html">Tool description</a>')  # noqa: E501

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
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_RASTER,
                description=self.translate('Input raster')
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.INPUT_LIST,
                description=self.translate(
                    'Mask class values, separated by comma'
                ),
                defaultValue='', multiLine=False
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE,
                description=self.translate('Size in pixels'),
                defaultValue=1, minValue=1
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_2,
                description=self.translate('Output NoData value'),
                defaultValue=-32768, optional=True
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
            QgsProcessingParameterString(
                name=self.TEXT,
                description=self.translate('Output name'),
                defaultValue='mask_', multiLine=False
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
            'semiautomaticclassificationplugin_cloud_masking_tool.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return MaskingBands()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        input_raster_list = self.parameterAsFileList(
            parameters, self.MULTIPLE_LAYERS, context
        )
        classification = self.parameterAsFile(
            parameters, self.INPUT_RASTER, context
        )
        input_classes = self.parameterAsStrings(
            parameters, self.INPUT_LIST, context
        )
        values = []
        for name in input_classes[0].split(','):
            values.append(int(name.strip()))
        if parameters[self.VALUE] is None:
            size = None
        else:
            size = self.parameterAsInt(
                parameters, self.VALUE, context
            )
        if parameters[self.VALUE_2] is None:
            nodata = None
        else:
            nodata = self.parameterAsInt(
                parameters, self.VALUE_2, context
            )
        output_name = self.parameterAsString(
            parameters, self.TEXT, context
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
        output = rs.band_mask(
            input_bands=input_bands, input_mask=classification,
            mask_values=values,
            output_path=output_path, prefix=output_name, buffer=size,
            nodata_value=nodata, virtual_output=virtual_output
        )
        if output.check:
            paths = output.paths
            for raster in paths:
                layer = QgsRasterLayer(raster, Path(raster).name)
                QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
