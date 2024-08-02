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
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterNumber, QgsProcessingParameterString, QgsRasterLayer,
    QgsProcessingParameterMultipleLayers, QgsProcessing, QgsProject,
    QgsProcessingParameterEnum
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class BandClustering(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'band_clustering'

    @staticmethod
    def displayName():
        return 'Clustering'

    @staticmethod
    def shortDescription():
        return (
            'Perform the clustering (method K-means) of a set of rasters. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.band_clustering.html">Tool description</a>')  # noqa: E501

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
            QgsProcessingParameterNumber(
                name=self.VALUE,
                description=self.translate('Number of classes'),
                defaultValue=10, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_2,
                description=self.translate('Distance threshold'),
                defaultValue=None, optional=True,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_3,
                description=self.translate('Max iterations'),
                defaultValue=10, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_4,
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
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ENUMERATOR, self.translate('Seed signatures'),
                ['Seed signatures from band values', 'Random seed signatures'],
                defaultValue=[0], allowMultiple=False
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ENUMERATOR_2, self.translate('Distance algorithm'),
                ['Minimum Distance', 'Spectral Angle Mapping'],
                defaultValue=[0], allowMultiple=False
            )
        )

    @staticmethod
    def icon():
        return QIcon(
            '%s/ui/icons/'
            'semiautomaticclassificationplugin_clustering.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return BandClustering()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        input_raster_list = self.parameterAsFileList(
            parameters, self.MULTIPLE_LAYERS, context
        )
        if parameters[self.VALUE] is None:
            class_number = None
        else:
            class_number = self.parameterAsInt(
                parameters, self.VALUE, context
            )
        if parameters[self.VALUE_2] is None:
            threshold = None
        else:
            threshold = self.parameterAsDouble(
                parameters, self.VALUE_2, context
            )
        if parameters[self.VALUE_3] is None:
            max_iter = None
        else:
            max_iter = self.parameterAsInt(
                parameters, self.VALUE_3, context
            )
        if parameters[self.VALUE_4] is None:
            nodata = None
        else:
            nodata = self.parameterAsInt(
                parameters, self.VALUE_4, context
            )

        if parameters[self.ENUMERATOR] is None:
            seed_signatures = None
        else:
            seed_types = [rs.configurations.band_mean,
                          rs.configurations.random_pixel]
            data_type = self.parameterAsInt(
                parameters, self.ENUMERATOR, context
            )
            seed_signatures = seed_types[data_type]
        if parameters[self.ENUMERATOR_2] is None:
            algorithm_name = None
        else:
            types = [rs.configurations.minimum_distance_a,
                     rs.configurations.spectral_angle_mapping_a]
            data_type = self.parameterAsInt(
                parameters, self.ENUMERATOR_2, context
            )
            algorithm_name = types[data_type]
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
        output = rs.band_clustering(
            input_bands=input_bands, output_raster_path=output_path,
            nodata_value=nodata, class_number=class_number,
            algorithm_name=algorithm_name, max_iter=max_iter,
            threshold=threshold, seed_signatures=seed_signatures
        )
        if output.check:
            path = output.path
            layer = QgsRasterLayer(path, Path(path).name)
            QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
