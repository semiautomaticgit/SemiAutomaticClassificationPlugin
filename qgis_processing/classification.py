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
    QgsProcessingParameterNumber, QgsProcessingParameterString, QgsRasterLayer,
    QgsProcessingParameterMultipleLayers, QgsProcessing, QgsProject,
    QgsProcessingParameterBoolean, QgsProcessingParameterEnum,
    QgsProcessingParameterFile
)

from .algorithm_template import AlgorithmTemplate


# noinspection PyPep8Naming
class Classification(AlgorithmTemplate):

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'classification'

    @staticmethod
    def displayName():
        return 'Classification'

    @staticmethod
    def shortDescription():
        return (
            'Perform calculations between raster bands. '
            '<a href="https://remotior-sensus.readthedocs.io/en/latest/remotior_sensus.tools.band_classification.html">Tool description</a>')  # noqa: E501

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
            QgsProcessingParameterFile(
                name=self.INPUT_FILE,
                description=self.translate('Training input file'),
                fileFilter=self.translate('scpx file (*.scpx)'), optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ENUMERATOR, self.translate('Input normalization'),
                ['z-score', 'linear scaling'],
                defaultValue=None, allowMultiple=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL,
                description=self.translate(
                    'Use Macroclass value (if False is Class value)'
                ), defaultValue=True, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ENUMERATOR_2, self.translate('Algorithm'),
                ['minimum distance', 'maximum likelihood',
                 'spectral angle mapping', 'random forest',
                 'support vector machine',
                 'multi-layer perceptron', 'pytorch multi-layer perceptron'],
                defaultValue=[0], allowMultiple=False
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE,
                description=self.translate(
                    'Use single threshold (Minimum Distance, '
                    'Maximum Likelihood, Spectral Angle Mapping'
                ),
                defaultValue=None, optional=True,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_2,
                description=self.translate(
                    'Signature threshold (Minimum Distance, '
                    'Maximum Likelihood, Spectral Angle Mapping'
                ),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_3,
                description=self.translate(
                    'Save signature raster (Minimum Distance, '
                    'Maximum Likelihood, Spectral Angle Mapping'
                ),
                defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_4,
                description=self.translate(
                    'Calculate classification confidence raster'
                ), defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.INPUT_LIST,
                description=self.translate(
                    'Multi-Layer Perceptron: Hidden layer sizes (values '
                    'separated by comma)'
                ), defaultValue=100, multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_2,
                description=self.translate(
                    'Multi-Layer Perceptron: max iter size'
                ), defaultValue=200, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT,
                description=self.translate(
                    'Multi-Layer Perceptron: activation'
                ), defaultValue='relu', multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_3,
                description=self.translate('Multi-Layer Perceptron: alpha'),
                defaultValue=0.01, optional=True,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_4,
                description=self.translate(
                    'Multi-Layer Perceptron: training portion'
                ),
                defaultValue=0.9, optional=True,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT_2,
                description=self.translate(
                    'Multi-Layer Perceptron: batch size'
                ), defaultValue='auto', multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_5,
                description=self.translate(
                    'Multi-Layer Perceptron: learning rate init'
                ),
                defaultValue=0.001, optional=True,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_5,
                description=self.translate(
                    'Cross validation (Multi-Layer Perceptron, Random Forest, '
                    'Support Vector Machine)'
                ), defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_7,
                description=self.translate('Random Forest: number of trees'),
                defaultValue=10, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_8,
                description=self.translate(
                    'Random Forest: minimum number to split'
                ), defaultValue=2, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT_3,
                description=self.translate(
                    'Random Forest: max features'
                ), defaultValue=None, multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_6,
                description=self.translate(
                    'Random Forest: One-Vs-Rest'
                ), defaultValue=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_9,
                description=self.translate(
                    'Support Vector Machine: regularization parameter C'
                ),
                defaultValue=1, optional=True,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT_4,
                description=self.translate(
                    'Support Vector Machine: kernel'
                ), defaultValue='rbf', multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.TEXT_5,
                description=self.translate(
                    'Support Vector Machine: gamma'
                ), defaultValue='scale', multiLine=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.VALUE_6,
                description=self.translate(
                    'Find best estimator with steps (Multi-Layer Perceptron, '
                    'Random Forest, Support Vector Machine)'
                ), defaultValue=None, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.BOOL_7,
                description=self.translate(
                    'Balanced class weight (Random Forest, '
                    'Support Vector Machine)'
                ), defaultValue=False, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT_FILE_2,
                description=self.translate('Classifier file'),
                fileFilter=self.translate('rsmo file (*.rsmo)'), optional=True
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
            '%s/ui/icons/semiautomaticclassificationplugin_classification.svg'
            % Path(__file__).parent.parent
        )

    @staticmethod
    def createInstance():
        return Classification()

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        rs = self.start_remotior_sensus_session()
        input_raster_list = self.parameterAsFileList(
            parameters, self.MULTIPLE_LAYERS, context
        )
        if self.INPUT_FILE is None:
            training_path = None
        else:
            training_path = self.parameterAsFile(
                parameters, self.INPUT_FILE, context
            )
            if len(training_path) == 0:
                training_path = None
        if parameters[self.ENUMERATOR] is None:
            input_normalization = None
        else:
            types = [rs.configurations.z_score,
                     rs.configurations.linear_scaling]
            norm_type = self.parameterAsInt(
                parameters, self.ENUMERATOR, context
            )
            input_normalization = types[norm_type]
        if parameters[self.BOOL] is None:
            macroclass = None
        else:
            macroclass = self.parameterAsBool(
                parameters, self.BOOL, context
            )
        if parameters[self.ENUMERATOR_2] is None:
            classifier_name = 'minimum distance'
        else:
            alg_types = [
                'minimum distance', 'maximum likelihood',
                'spectral angle mapping', 'random forest',
                'support vector machine', 'multi-layer perceptron',
                'pytorch multi-layer perceptron'
            ]
            alg_type = self.parameterAsInt(
                parameters, self.ENUMERATOR_2, context
            )
            classifier_name = alg_types[alg_type]
        if parameters[self.VALUE] is None:
            threshold = None
        else:
            threshold = self.parameterAsDouble(
                parameters, self.VALUE, context
            )
        if parameters[self.BOOL_2] is not None:
            thresholds = self.parameterAsBool(
                parameters, self.BOOL_2, context
            )
            if thresholds is True:
                threshold = True
        if parameters[self.BOOL_3] is None:
            signature_raster = None
        else:
            signature_raster = self.parameterAsBool(
                parameters, self.BOOL_3, context
            )
        if parameters[self.BOOL_4] is None:
            classification_confidence = None
        else:
            classification_confidence = self.parameterAsBool(
                parameters, self.BOOL_4, context
            )
        hidden_layers = self.parameterAsString(
            parameters, self.INPUT_LIST, context
        )
        mlp_hidden_layer_sizes = None
        if hidden_layers is not None:
            try:
                mlp_hidden_layer_sizes = eval('[%s]' % hidden_layers)
            except Exception as err:
                str(err)
                raise 'mlp hidden layer sizes'
        if parameters[self.VALUE_2] is None:
            mlp_max_iter = None
        else:
            mlp_max_iter = self.parameterAsInt(
                parameters, self.VALUE_2, context
            )
        mlp_activation = self.parameterAsString(
            parameters, self.TEXT, context
        )
        if parameters[self.VALUE_3] is None:
            mlp_alpha = None
        else:
            mlp_alpha = self.parameterAsDouble(
                parameters, self.VALUE_3, context
            )
        if parameters[self.VALUE_4] is None:
            mlp_training_portion = None
        else:
            mlp_training_portion = self.parameterAsDouble(
                parameters, self.VALUE_4, context
            )
        mlp_batch_size = self.parameterAsString(
            parameters, self.TEXT_2, context
        )
        if parameters[self.VALUE_5] is None:
            mlp_learning_rate_init = None
        else:
            mlp_learning_rate_init = self.parameterAsDouble(
                parameters, self.VALUE_5, context
            )
        if parameters[self.BOOL_5] is None:
            cross_validation = None
        else:
            cross_validation = self.parameterAsBool(
                parameters, self.BOOL_5, context
            )
        if parameters[self.VALUE_6] is None:
            find_best_estimator = None
        else:
            find_best_estimator = self.parameterAsInt(
                parameters, self.VALUE_6, context
            )
        if parameters[self.VALUE_7] is None:
            rf_number_trees = None
        else:
            rf_number_trees = self.parameterAsInt(
                parameters, self.VALUE_7, context
            )
        if parameters[self.VALUE_8] is None:
            rf_min_samples_split = None
        else:
            rf_min_samples_split = self.parameterAsInt(
                parameters, self.VALUE_8, context
            )
        rf_max_features = self.parameterAsString(
            parameters, self.TEXT_3, context
        )
        if parameters[self.BOOL_6] is not None:
            rf_ovr = self.parameterAsBool(
                parameters, self.BOOL_6, context
            )
            if rf_ovr is True:
                classifier_name = 'random forest ovr'
        class_weight = None
        if parameters[self.BOOL_7] is None:
            class_weight = None
        else:
            class_weight_bool = self.parameterAsBool(
                parameters, self.BOOL_7, context
            )
            if class_weight_bool is True:
                class_weight = 'balanced'
        if parameters[self.VALUE_9] is None:
            svm_c = None
        else:
            svm_c = self.parameterAsDouble(
                parameters, self.VALUE_9, context
            )
        svm_kernel = self.parameterAsString(
            parameters, self.TEXT_4, context
        )
        svm_gamma = self.parameterAsString(
            parameters, self.TEXT_5, context
        )
        load_classifier = None
        if self.INPUT_FILE_2 is None:
            load_classifier = None
        else:
            classifier = self.parameterAsFile(
                parameters, self.INPUT_FILE_2, context
            )
            if len(classifier) == 0:
                load_classifier = None
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
        output = rs.band_classification(
            input_bands=input_bands, output_path=output_path,
            spectral_signatures=training_path, macroclass=macroclass,
            algorithm_name=classifier_name, threshold=threshold,
            signature_raster=signature_raster,
            cross_validation=cross_validation,
            input_normalization=input_normalization,
            load_classifier=load_classifier,
            class_weight=class_weight, find_best_estimator=find_best_estimator,
            rf_max_features=rf_max_features, rf_number_trees=rf_number_trees,
            rf_min_samples_split=rf_min_samples_split, svm_c=svm_c,
            svm_gamma=svm_gamma, svm_kernel=svm_kernel,
            mlp_training_portion=mlp_training_portion,
            mlp_alpha=mlp_alpha, mlp_learning_rate_init=mlp_learning_rate_init,
            mlp_max_iter=mlp_max_iter, mlp_batch_size=mlp_batch_size,
            mlp_activation=mlp_activation,
            mlp_hidden_layer_sizes=mlp_hidden_layer_sizes,
            classification_confidence=classification_confidence
        )
        if output.check:
            raster = output.path
            layer = QgsRasterLayer(raster, Path(raster).name)
            QgsProject.instance().addMapLayer(layer)
        return {self.OUTPUT: output_path}
