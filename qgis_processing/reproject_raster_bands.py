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
    QgsProcessingParameterBoolean, QgsProcessingParameterEnum,
    QgsProcessingParameterRasterLayer, QgsProcessingParameterNumber

)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class ReprojectRasterBands(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'reproject_raster_bands'

    @staticmethod
    def displayName():
        return 'Reproject raster bands'

    @staticmethod
    def shortDescription():
        return (
            'Perform the resampling and reprojection of bands. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.band_resample.html">Tool description</a>')  # noqa: E501

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
                description=self.translate('Align raster'), optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL,
                description=self.translate('Same extent as reference'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT,
                description=self.translate('EPSG code'),
                defaultValue='', multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE,
                description=self.translate('X resolution'),
                defaultValue=None, optional=True,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_2,
                description=self.translate('Y resolution'),
                defaultValue=None, optional=True,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_3,
                description=self.translate('Resample pixel factor'),
                defaultValue=None, optional=True,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ENUMERATOR, self.translate('Resampling method'),
                ['nearest_neighbour', 'average', 'sum', 'maximum', 'minimum',
                 'mode', 'median', 'first_quartile', 'third_quartile'],
                defaultValue=[0], allowMultiple=False
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ENUMERATOR_2, self.translate('Output data type'),
                ['Float32', 'Int32', 'UInt32', 'Int16', 'UInt16', 'Byte'],
                defaultValue=[0], allowMultiple=False
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_4,
                description=self.translate('Output NoData value'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT_2,
                description=self.translate('Output name'),
                defaultValue='reproj_', multiLine=False
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_2,
                description=self.translate('Virtual output'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT_3,
                description=self.translate('Compression'),
                defaultValue='LZW', multiLine=False, optional=True
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
            'semiautomaticclassificationplugin_reproject_raster_bands.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return ReprojectRasterBands()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        input_raster_list = self.parameterAsFileList(
            parameters, self.MULTIPLE_LAYERS, context
        )
        if parameters[self.INPUT_RASTER] is None:
            align_raster = None
        else:
            align_raster = self.parameterAsFile(
                parameters, self.INPUT_RASTER, context
            )
        if parameters[self.BOOL_2] is None:
            same_extent = None
        else:
            same_extent = self.parameterAsBool(
                parameters, self.BOOL_2, context
            )
        epsg = self.parameterAsString(parameters, self.TEXT, context)
        if len(epsg) == 0:
            epsg = None
        if parameters[self.VALUE] is None:
            x_y_resolution = None
        else:
            x_res = self.parameterAsDouble(
                parameters, self.VALUE, context
            )
            if parameters[self.VALUE_2] is None:
                x_y_resolution = None
            else:
                y_res = self.parameterAsDouble(
                    parameters, self.VALUE, context
                )
                x_y_resolution = [x_res, y_res]
        if parameters[self.VALUE] is None:
            resample_pixel_factor = None
        else:
            resample_pixel_factor = self.parameterAsDouble(
                parameters, self.VALUE, context
            )
        if parameters[self.ENUMERATOR] is None:
            resampling = None
        else:
            types = [
                'nearest_neighbour', 'average', 'sum', 'maximum', 'minimum',
                'mode', 'median', 'first_quartile', 'third_quartile'
            ]
            enum = self.parameterAsInt(
                parameters, self.ENUMERATOR, context
            )
            resampling = types[enum]
        if parameters[self.ENUMERATOR_2] is None:
            raster_type = None
        else:
            types = ['Float32', 'Int32', 'UInt32', 'Int16', 'UInt16', 'Byte']
            enum = self.parameterAsInt(
                parameters, self.ENUMERATOR_2, context
            )
            raster_type = types[enum]
        if parameters[self.VALUE_4] is None:
            nodata_value = None
        else:
            nodata_value = self.parameterAsInt(
                parameters, self.VALUE, context
            )
        output_name = self.parameterAsString(
            parameters, self.TEXT_2, context
        )
        if parameters[self.BOOL_2] is None:
            virtual_output = None
        else:
            virtual_output = self.parameterAsBool(
                parameters, self.BOOL_2, context
            )
        compress_format = self.parameterAsString(
            parameters, self.TEXT_3, context
        )
        compress = True
        if len(compress_format) == 0:
            compress_format = None
            compress = False
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
        output = rs.band_resample(
            input_bands=input_bands, output_path=output_path,
            prefix=output_name, epsg_code=epsg, align_raster=align_raster,
            resampling=resampling, nodata_value=nodata_value,
            x_y_resolution=x_y_resolution,
            resample_pixel_factor=resample_pixel_factor,
            output_data_type=raster_type, same_extent=same_extent,
            virtual_output=virtual_output, compress=compress,
            compress_format=compress_format
        )
        if output.check:
            paths = output.paths
            for raster in paths:
                layer = QgsRasterLayer(raster, Path(raster).name)
                QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
