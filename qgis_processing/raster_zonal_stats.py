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
    QgsProject, QgsProcessingParameterBoolean,
    QgsProcessingParameterVectorLayer, QgsProcessingParameterString,
    QgsVectorLayer
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class RasterZonalStats(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'raster_zonal_stats'

    @staticmethod
    def displayName():
        return 'Raster zonal stats'

    @staticmethod
    def shortDescription():
        return ('Calculation of statistics of a raster intersecting a vector. '
                '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.raster_zonal_stats.html">Tool description</a>')  # noqa: E501

    # noinspection PyUnusedLocal
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.INPUT_RASTER,
                description=self.translate('Input raster')
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INPUT_VECTOR,
                description=self.translate('Reference vector')
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT,
                description=self.translate('Vector field'),
                defaultValue='', multiLine=False
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL,
                description=self.translate('Count'),
                defaultValue=True, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_2,
                description=self.translate('Maximum'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_3,
                description=self.translate('Minimum'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_4,
                description=self.translate('Mean'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_5,
                description=self.translate('Median'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_6,
                description=self.translate('Percentile'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT_2,
                description=self.translate('Percentile values'),
                defaultValue='', multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_7,
                description=self.translate('Standard deviation'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_8,
                description=self.translate('Sum'),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                name=self.OUTPUT,
                description=self.translate('Calculation output'),
                fileFilter=self.translate('csv file (*.csv)')
            )
        )

    @staticmethod
    def icon():
        return QIcon(
            '%s/ui/icons'
            '/semiautomaticclassificationplugin_zonal_stat_raster_tool.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return RasterZonalStats()

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
            parameters, self.INPUT_VECTOR, context
        )
        if rs.files_directories.is_file(reference) is False:
            layer_x = root.findLayer(reference)
            reference = layer_x.layer().source().split("|layername=")[0]
        field = self.parameterAsString(parameters, self.TEXT, context)
        if len(field) == 0:
            field = None
        stat_names = []
        stat_percentile = None
        if parameters[self.BOOL] is not None:
            if self.parameterAsBool(parameters, self.BOOL, context) is True:
                stat_names.append('Count')
        if parameters[self.BOOL_2] is not None:
            if self.parameterAsBool(parameters, self.BOOL_2, context) is True:
                stat_names.append('Max')
        if parameters[self.BOOL_3] is not None:
            if self.parameterAsBool(parameters, self.BOOL_3, context) is True:
                stat_names.append('Min')
        if parameters[self.BOOL_4] is not None:
            if self.parameterAsBool(parameters, self.BOOL_4, context) is True:
                stat_names.append('Mean')
        if parameters[self.BOOL_5] is not None:
            if self.parameterAsBool(parameters, self.BOOL_5, context) is True:
                stat_names.append('Median')
        if parameters[self.BOOL_6] is not None:
            if self.parameterAsBool(parameters, self.BOOL_6, context) is True:
                stat_names.append('Percentile')
            percentile = self.parameterAsString(
                parameters, self.TEXT_2, context
            )
            if len(field) > 0:
                percentile_split = percentile.split(',')
                stat_percentile = []
                for i in percentile_split:
                    try:
                        stat_percentile.append(int(i))
                    except Exception as err:
                        str(err)
            if len(stat_percentile) == 0:
                stat_percentile = None
        if parameters[self.BOOL_7] is not None:
            if self.parameterAsBool(parameters, self.BOOL_7, context) is True:
                stat_names.append('StandardDeviation')
        if parameters[self.BOOL_8] is not None:
            if self.parameterAsBool(parameters, self.BOOL_8, context) is True:
                stat_names.append('Sum')
        output_path = self.parameterAsFileOutput(
            parameters, self.OUTPUT, context
        )
        output = rs.raster_zonal_stats(
            raster_path=classification, vector_path=reference,
            vector_field=field, stat_names=stat_names,
            stat_percentile=stat_percentile, output_path=output_path
        )
        return {self.OUTPUT: output.path}
