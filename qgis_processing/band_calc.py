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
    QgsProcessingParameterFileDestination, QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber, QgsProcessingParameterString, QgsRasterLayer,
    QgsProcessingParameterMultipleLayers, QgsProcessing, QgsProject,
    QgsProcessingParameterBoolean, QgsProcessingParameterEnum
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class BandCalc(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'band_calc'

    @staticmethod
    def displayName():
        return 'Band calc'

    @staticmethod
    def shortDescription():
        return (
            'Perform calculations between raster bands. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.band_calc.html">Tool description</a>')  # noqa: E501

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
                    'Raster names used in expression, separated by comma, '
                    'in the same order as input list'
                ),
                defaultValue='b1, b2', multiLine=False
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT,
                description=self.translate('Expression'),
                defaultValue='"b1" + "b2"', multiLine=False
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL,
                description=self.translate('Input NoData as value'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE,
                description=self.translate('Use value as NoData'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ENUMERATOR, self.translate('Calculation data type'),
                ['Float32', 'Int32', 'UInt32', 'Int16', 'UInt16', 'Byte'],
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
                name=self.VALUE_2,
                description=self.translate('Output NoData value'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ENUMERATOR_3, self.translate('NoData mask'),
                ['False', 'True', 'None'],
                defaultValue=[0], allowMultiple=False
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_3,
                description=self.translate('Set scale'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_4,
                description=self.translate('Set offset'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_RASTER,
                description=self.translate('Align raster'),
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_RASTER_2,
                description=self.translate('Extent raster'),
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.INPUT_LIST_2,
                description=self.translate(
                    'Coordinates left, top, right, bottom, separated by comma'
                ),
                defaultValue=None, multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_2,
                description=self.translate('Extent intersection'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_5,
                description=self.translate('Pixel resolution'),
                defaultValue=None, optional=True,
                type=QgsProcessingParameterNumber.Double
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
            '%s/ui/icons/semiautomaticclassificationplugin_bandcalc_tool.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return BandCalc()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        input_raster_list = self.parameterAsFileList(
            parameters, self.MULTIPLE_LAYERS, context
        )
        input_names = self.parameterAsStrings(
            parameters, self.INPUT_LIST, context
        )
        input_name_list = []
        for name in input_names[0].split(','):
            input_name_list.append(name.strip())
        if parameters[self.BOOL] is None:
            input_nodata_as_value = None
        else:
            input_nodata_as_value = self.parameterAsBool(
                parameters, self.BOOL, context
            )
        if parameters[self.VALUE] is None:
            use_value_as_nodata = None
        else:
            use_value_as_nodata = self.parameterAsInt(
                parameters, self.VALUE, context
            )
        if parameters[self.ENUMERATOR] is None:
            calc_datatype = None
        else:
            types = ['Float32', 'Int32', 'UInt32', 'Int16', 'UInt16', 'Byte']
            data_type = self.parameterAsInt(
                parameters, self.ENUMERATOR, context
            )
            calc_datatype = types[data_type]
        if parameters[self.ENUMERATOR_2] is None:
            output_datatype = None
        else:
            types = ['Float32', 'Int32', 'UInt32', 'Int16', 'UInt16', 'Byte']
            data_type = self.parameterAsInt(
                parameters, self.ENUMERATOR_2, context
            )
            output_datatype = types[data_type]
        if parameters[self.VALUE_2] is None:
            output_nodata = None
        else:
            output_nodata = self.parameterAsInt(
                parameters, self.VALUE_2, context
            )
        if parameters[self.VALUE_3] is None:
            use_scale = None
        else:
            use_scale = self.parameterAsInt(
                parameters, self.VALUE_3, context
            )
        if parameters[self.VALUE_4] is None:
            use_offset = None
        else:
            use_offset = self.parameterAsInt(
                parameters, self.VALUE_4, context
            )
        if parameters[self.ENUMERATOR_3] is None:
            any_nodata_mask = None
        else:
            types = ['False', 'True', 'None']
            enum = self.parameterAsInt(
                parameters, self.ENUMERATOR_3, context
            )
            if types[enum] == 'False':
                any_nodata_mask = False
            elif types[enum] == 'True':
                any_nodata_mask = True
            else:
                any_nodata_mask = None
        expression = self.parameterAsString(
            parameters, self.TEXT, context
        )
        if parameters[self.INPUT_RASTER_2] is None:
            extent_raster = None
        else:
            extent_raster = self.parameterAsFile(
                parameters, self.INPUT_RASTER_2, context
            )
        if parameters[self.INPUT_LIST_2] is None:
            extent_list = None
        else:
            extent_text = self.parameterAsStrings(
                parameters, self.INPUT_LIST_2, context
            )
            if len(extent_text) > 0:
                extent_list = []
                for extent in extent_text[0].split(','):
                    extent_list.append(float(extent.strip()))
            else:
                extent_list = None
        if parameters[self.BOOL_2] is None:
            extent_intersection = None
        else:
            extent_intersection = self.parameterAsBool(
                parameters, self.BOOL_2, context
            )
        if parameters[self.INPUT_RASTER] is None:
            align_raster = None
        else:
            align_raster = self.parameterAsFile(
                parameters, self.INPUT_RASTER, context
            )
        if parameters[self.VALUE_5] is None:
            xy_resolution_list = None
        else:
            xy_resolution = self.parameterAsDouble(
                parameters, self.VALUE_5, context
            )
            xy_resolution_list = [xy_resolution, xy_resolution]
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
        output = rs.band_calc(
            expression_string=expression, output_path=output_path,
            input_raster_list=input_bands,
            input_name_list=input_name_list, align_raster=align_raster,
            use_value_as_nodata=use_value_as_nodata,
            input_nodata_as_value=input_nodata_as_value,
            extent_raster=extent_raster, extent_list=extent_list,
            extent_intersection=extent_intersection,
            calc_datatype=calc_datatype, output_datatype=output_datatype,
            output_nodata=output_nodata, any_nodata_mask=any_nodata_mask,
            use_scale=use_scale, use_offset=use_offset,
            xy_resolution_list=xy_resolution_list
        )
        if output.check:
            paths = output.paths
            for raster in paths:
                layer = QgsRasterLayer(raster, Path(raster).name)
                QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
