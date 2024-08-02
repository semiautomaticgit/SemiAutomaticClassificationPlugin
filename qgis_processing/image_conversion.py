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
    QgsProcessingParameterFolderDestination, QgsProcessingParameterFile,
    QgsRasterLayer, QgsProcessingParameterNumber,
    QgsProject, QgsProcessingParameterBoolean
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class ImageConversion(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'image_conversion'

    @staticmethod
    def displayName():
        return 'Image conversion'

    @staticmethod
    def shortDescription():
        return (
            'Perform the preprocessing of products. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.preprocess_products.html">Tool description</a>')  # noqa: E501

    # noinspection PyUnusedLocal
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT_DIRECTORY,
                description=self.translate('Directory containing bands'),
                behavior=QgsProcessingParameterFile.Folder
            )
        )
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT_FILE,
                description=self.translate('Metadata file'), optional=True
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
            QgsProcessingParameterBoolean(
                name=self.BOOL,
                description=self.translate(
                    'Apply DOS1 atmospheric correction'
                ),
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
            'semiautomaticclassificationplugin_landsat8_tool.svg' %
            Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return ImageConversion()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        input_path = self.parameterAsString(
            parameters, self.INPUT_DIRECTORY, context
        )
        if rs.files_directories.is_directory(input_path) is False:
            raise 'input directory'
        if self.INPUT_FILE is None:
            metadata = None
        else:
            metadata = self.parameterAsFile(
                parameters, self.INPUT_FILE, context
            )
            if len(metadata) == 0:
                metadata = None
        if parameters[self.VALUE] is None:
            nodata = None
        else:
            nodata = self.parameterAsInt(
                parameters, self.VALUE, context
            )
        if parameters[self.BOOL] is None:
            dos1_correction = None
        else:
            dos1_correction = self.parameterAsBool(
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
        output = rs.preprocess_products.preprocess(
            input_path=input_path, output_path=output_path,
            metadata_file_path=metadata, nodata_value=nodata,
            dos1_correction=dos1_correction, output_prefix='RT_'
        )
        if output.check:
            paths = output.paths
            for raster in paths:
                layer = QgsRasterLayer(raster, Path(raster).name)
                QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
