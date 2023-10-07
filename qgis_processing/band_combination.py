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
    QgsProcessingParameterNumber, QgsProcessingParameterString, QgsRasterLayer,
    QgsProcessingParameterMultipleLayers, QgsProcessing, QgsProject
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class BandCombination(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'band_combination'

    @staticmethod
    def displayName():
        return 'Combination'

    @staticmethod
    def shortDescription():
        return (
            'Combines classifications in order to get a raster where each '
            'value corresponds to a combination of class values. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.band_combination.html">Tool description</a>')  # noqa: E501

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
                    'Strings, separated by comma, corresponding to input '
                    'bands used as column names in output table'
                ),
                defaultValue='', multiLine=False, optional=True
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
            QgsProcessingParameterFolderDestination(
                name=self.OUTPUT,
                description=self.translate('Calculation output')
            )
        )

    @staticmethod
    def icon():
        return QIcon(
            '%s/ui/icons/'
            'semiautomaticclassificationplugin_band_combination_tool.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return BandCombination()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        input_raster_list = self.parameterAsFileList(
            parameters, self.MULTIPLE_LAYERS, context
        )
        column_names = self.parameterAsStrings(
            parameters, self.INPUT_LIST, context
        )
        if column_names is None:
            column_name_list = None
        else:
            column_name_list = column_names[0].split(',')
        if parameters[self.VALUE] is None:
            nodata = None
        else:
            nodata = self.parameterAsInt(
                parameters, self.VALUE, context
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
        output = rs.band_combination(
            input_bands=input_bands, output_path=output_path,
            nodata_value=nodata, column_name_list=column_name_list
        )
        if output.check:
            paths = output.paths
            layer = QgsRasterLayer(paths[0], Path(paths[0]).name)
            QgsProject.instance().addMapLayer(layer)
            self.feedback.pushInfo('Output table: ' + str(paths[1]))
        return {self.OUTPUT: output_path}
