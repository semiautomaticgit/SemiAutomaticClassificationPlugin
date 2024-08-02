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
    QgsRasterLayer, QgsProcessingParameterFileDestination,
    QgsProcessingParameterMultipleLayers, QgsProcessing, QgsProject
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class StackBands(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'stack_bands'

    @staticmethod
    def displayName():
        return 'Stack bands'

    @staticmethod
    def shortDescription():
        return (
            'Perform stack of raster bands. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.band_stack.html">Tool description</a>')  # noqa: E501

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
            '%s/ui/icons/'
            'semiautomaticclassificationplugin_stack_raster.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return StackBands()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        input_raster_list = self.parameterAsFileList(
            parameters, self.MULTIPLE_LAYERS, context
        )
        output_path = self.parameterAsFileOutput(
            parameters, self.OUTPUT, context
        )
        root = QgsProject.instance().layerTreeRoot()
        input_bands = []
        for raster in input_raster_list:
            if rs.files_directories.is_file(raster) is False:
                layer_x = root.findLayer(raster)
                input_bands.append(layer_x.layer().source())
            else:
                input_bands.append(raster)
        output = rs.band_stack(
            input_bands=input_bands, output_path=output_path
        )
        if output.check:
            raster = output.path
            layer = QgsRasterLayer(raster, Path(raster).name)
            QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
