# SemiAutomaticClassificationPlugin
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised 
# classification of remote sensing images, providing tools for the download, 
# the preprocessing and postprocessing of images.
# begin: 2012-12-29
# Copyright (C) 2012-2026 by Luca Congedo.
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
"""Classification.

This tool allows for classification of band set.
"""

from copy import deepcopy
import ast

# import the PyQt libraries
from PyQt6.QtGui import QIcon, QPixmap, QCursor
from PyQt6.QtWidgets import QApplication

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# set variable for macroclass classification
def macroclass_radio():
    if cfg.dialog.ui.macroclass_radioButton.isChecked() is True:
        cfg.dialog.ui.class_radioButton.blockSignals(True)
        cfg.dialog.ui.class_radioButton.setChecked(0)
        cfg.dialog.ui.class_radioButton.blockSignals(False)
    else:
        cfg.dialog.ui.macroclass_radioButton.blockSignals(True)
        cfg.dialog.ui.macroclass_radioButton.setChecked(1)
        cfg.dialog.ui.macroclass_radioButton.blockSignals(False)
    reset_preview()


# set variable for class classification
def class_radio():
    if cfg.dialog.ui.class_radioButton.isChecked() is True:
        cfg.dialog.ui.macroclass_radioButton.blockSignals(True)
        cfg.dialog.ui.macroclass_radioButton.setChecked(0)
        cfg.dialog.ui.macroclass_radioButton.blockSignals(False)
    else:
        cfg.dialog.ui.class_radioButton.blockSignals(True)
        cfg.dialog.ui.class_radioButton.setChecked(1)
        cfg.dialog.ui.class_radioButton.blockSignals(False)
    reset_preview()


# set variable for scaling
def z_scaling_radio():
    if cfg.dialog.ui.z_score_radioButton.isChecked() is True:
        cfg.dialog.ui.linear_scaling_radioButton.blockSignals(True)
        cfg.dialog.ui.linear_scaling_radioButton.setChecked(0)
        cfg.dialog.ui.linear_scaling_radioButton.blockSignals(False)
    else:
        cfg.dialog.ui.z_score_radioButton.blockSignals(True)
        cfg.dialog.ui.z_score_radioButton.setChecked(1)
        cfg.dialog.ui.z_score_radioButton.blockSignals(False)
    reset_preview()


# set variable for scaling
def linear_scaling_radio():
    if cfg.dialog.ui.linear_scaling_radioButton.isChecked() is True:
        cfg.dialog.ui.z_score_radioButton.blockSignals(True)
        cfg.dialog.ui.z_score_radioButton.setChecked(0)
        cfg.dialog.ui.z_score_radioButton.blockSignals(False)

    else:
        cfg.dialog.ui.linear_scaling_radioButton.blockSignals(True)
        cfg.dialog.ui.linear_scaling_radioButton.setChecked(1)
        cfg.dialog.ui.linear_scaling_radioButton.blockSignals(False)
    reset_preview()


# changed tab
def changed_tab(index):
    icon = QIcon()
    icon.addPixmap(
        QPixmap(
            ':/plugins/semiautomaticclassificationplugin/icons/'
            'semiautomaticclassificationplugin_options.svg'
        ), QIcon.Mode.Normal, QIcon.State.Off
    )
    count = cfg.dialog.ui.toolBox_classification.count()
    for position in range(0, count):
        cfg.dialog.ui.toolBox_classification.setItemIcon(position, QIcon())
    cfg.dialog.ui.toolBox_classification.setItemIcon(index, icon)
    reset_preview()


def reset_preview():
    # reset classifier
    cfg.classifier_preview = None


# load classifier
# noinspection PyTypeChecker
def open_classifier():
    file = cfg.util_qt.get_open_file(
        None, QApplication.translate('semiautomaticclassificationplugin',
                                     'Select a classifier file'), '',
        'Classifier (*%s)' % cfg.rs.configurations.rsmo_suffix
    )
    if len(file) > 0:
        cfg.dialog.ui.label_classifier.setText(file)
        temp_dir = cfg.rs.configurations.temp.create_temporary_directory()
        file_list = cfg.rs.files_directories.unzip_file(file, temp_dir)
        # open classification framework
        for f in file_list:
            f_name = cfg.rs.files_directories.file_name(f)
            if f_name == cfg.rs.configurations.classification_framework:
                with open(f, 'r') as f_file:
                    classification_framework = f_file.read()
                lines = classification_framework.split(
                    cfg.rs.configurations.new_line
                )
                for line in lines:
                    variable = line.split('=')
                    if (variable[0] ==
                            cfg.rs.configurations.algorithm_name_framework):
                        algorithm_name = variable[1]
                        cfg.dialog.ui.name_classifier.setText(algorithm_name)
                        break
            break
    else:
        cfg.dialog.ui.label_classifier.setText('')
        cfg.dialog.ui.name_classifier.setText('')


# apply symbology to classification
def apply_class_symbology(classification_raster, macroclass):
    value_name, value_color = cfg.scp_dock.export_symbology(macroclass)
    cfg.utils.classification_raster_symbol(
        classification_layer=classification_raster,
        value_name_dictionary=value_name, value_color_dictionary=value_color
    )


# perform classification
def run_classification_action():
    run_classifier()


# perform classification
def run_classification_action_simplified():
    run_classifier(simplified=True)


# save classifier
def save_classifier_action():
    output = run_classifier(save_classifier=True)
    return output


# perform classification
# noinspection PyTypeChecker
def run_classifier(
        save_classifier=None, preview_point=None,
        classification_confidence=None, simplified=None
):
    threshold = False
    signature_raster = False
    cross_validation = True
    find_best_estimator = False
    if classification_confidence is None:
        classification_confidence = False
    input_normalization = load_classifier = class_weight = None
    rf_max_features = rf_number_trees = rf_min_samples_split = svm_c = None
    svm_gamma = svm_kernel = mlp_hidden_layer_sizes = None
    mlp_training_portion = mlp_alpha = mlp_learning_rate_init = None
    mlp_max_iter = mlp_batch_size = mlp_activation = None
    additional_algorithm_name = pretrained_model_path = pretrained_model = None
    pretrained_segmentation = None
    value_name_dictionary = value_color_dictionary = None
    cfg.rs.configurations.action = True
    # if not preview ask for output file
    if preview_point is None:
        if save_classifier is True:
            output_path = cfg.util_qt.get_save_file_name(
                None,
                QApplication.translate('semiautomaticclassificationplugin',
                                       'Save classifier'),
                '', 'Classifier file (*%s)' % cfg.rs.configurations.rsmo_suffix
            )
        else:
            output_path = cfg.util_qt.get_save_file_name(
                None,
                QApplication.translate('semiautomaticclassificationplugin',
                                       'Save classification'),
                '', 'TIF file (*.tif);;VRT file (*.vrt)'
            )
    else:
        # path for preview
        output_path = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix='.vrt'
        )
    if output_path is False:
        return None
    else:
        if (output_path.lower().endswith('.vrt')
                or output_path.lower().endswith(
                    cfg.rs.configurations.rsmo_suffix)):
            pass
        elif not output_path.lower().endswith('.tif'):
            output_path += '.tif'
    cfg.logger.log.info('run_classifier: %s' % output_path)
    # load classifier
    if len(cfg.dialog.ui.label_classifier.text()) > 0:
        load_classifier = cfg.dialog.ui.label_classifier.text()
    if simplified:
        bandset_number = 1
        classifier_name = cfg.dock_class_simpl_dlg.ui.alg_combo.currentText()
    else:
        # get bandset
        if cfg.simplified:
            bandset_number = 1
        else:
            bandset_number = cfg.dialog.ui.band_set_comb_spinBox_12.value()
        cfg.logger.log.debug('bandset_number: %s' % bandset_number)
        classifier_index = cfg.dialog.ui.toolBox_classification.currentIndex()
        classifier_list = [
            cfg.rs.configurations.maximum_likelihood,
            cfg.rs.configurations.minimum_distance,
            cfg.rs.configurations.multi_layer_perceptron,
            cfg.rs.configurations.random_forest,
            cfg.rs.configurations.spectral_angle_mapping,
            cfg.rs.configurations.support_vector_machine,
            'pretrained'
        ]
        classifier_name = classifier_list[classifier_index]
    if cfg.dialog.ui.macroclass_radioButton.isChecked() is True:
        macroclass = True
    else:
        macroclass = False
    if cfg.dialog.ui.input_normalization_checkBox.isChecked() is True:
        if cfg.dialog.ui.z_score_radioButton.isChecked() is True:
            input_normalization = cfg.rs.configurations.z_score
        else:
            input_normalization = cfg.rs.configurations.linear_scaling
    if cfg.scp_training is None:
        if classifier_name != 'pretrained':
            cfg.mx.msg_war_5()
            return False
    if classifier_name == 'pretrained':
        signature_catalog = None
        save_classifier = False
    else:
        if (cfg.scp_training.signature_catalog is None
                or cfg.scp_training.signature_catalog is False):
            cfg.mx.msg_war_5()
            return False
        else:
            signature_catalog = cfg.scp_training.signature_catalog
    if save_classifier is True:
        only_fit = True
    else:
        only_fit = False
    # maximum likelihood
    if classifier_name == cfg.rs.configurations.maximum_likelihood:
        if cfg.dialog.ui.single_threshold_checkBox.isChecked() is True:
            threshold = cfg.dialog.ui.alg_threshold_SpinBox_2.value()
        if cfg.dialog.ui.single_threshold_checkBox_2.isChecked() is True:
            threshold = True
        if cfg.dialog.ui.signature_raster_checkBox_3.isChecked() is True:
            signature_raster = True
        if cfg.dialog.ui.confidence_raster_checkBox.isChecked() is True:
            classification_confidence = True
    # minimum distance
    elif classifier_name == cfg.rs.configurations.minimum_distance:
        if cfg.dialog.ui.single_threshold_checkBox_4.isChecked() is True:
            threshold = cfg.dialog.ui.alg_threshold_SpinBox_4.value()
        if cfg.dialog.ui.single_threshold_checkBox_3.isChecked() is True:
            threshold = True
        if cfg.dialog.ui.signature_raster_checkBox_2.isChecked() is True:
            signature_raster = True
        if cfg.dialog.ui.confidence_raster_checkBox_2.isChecked() is True:
            classification_confidence = True
    # multi layer perceptron
    elif classifier_name == cfg.rs.configurations.multi_layer_perceptron:
        if cfg.dialog.ui.pretrained_model_checkBox.isChecked() is True:
            pretrained_model = (
                cfg.dialog.ui.pretrained_model_combo.currentText())
            # exclude first element of combo that is empty
            if len(pretrained_model) == 1:
                pretrained_model = None
        if cfg.dialog.ui.pytorch_radioButton.isChecked() is True:
            classifier_name = (
                cfg.rs.configurations.pytorch_multi_layer_perceptron
            )
        if cfg.dialog.ui.best_estimator_checkBox_2.isChecked() is True:
            find_best_estimator = int(cfg.dialog.ui.steps_SpinBox_2.value())
        if cfg.dialog.ui.cross_validation_checkBox_3.isChecked() is True:
            cross_validation = True
        else:
            cross_validation = False
        mlp_training_portion = (
            cfg.dialog.ui.training_proportion_SpinBox.value())
        mlp_learning_rate_init = cfg.dialog.ui.learning_rate_SpinBox.value()
        mlp_alpha = cfg.dialog.ui.alpha_SpinBox.value()
        mlp_max_iter = int(cfg.dialog.ui.max_iterations_SpinBox.value())
        try:
            mlp_batch_size = int(cfg.dialog.ui.batch_size_lineEdit.text())
        except Exception as err:
            str(err)
            mlp_batch_size = 'auto'
        mlp_activation = cfg.dialog.ui.activation_lineEdit.text()
        hidden_layers = cfg.dialog.ui.hidden_layers_lineEdit.text()
        try:
            mlp_hidden_layer_sizes = ast.literal_eval(f'[{hidden_layers}]')
        except Exception as err:
            mlp_hidden_layer_sizes = [100]
            cfg.mx.msg_war_2()
            str(err)
        if cfg.dialog.ui.confidence_raster_checkBox_3.isChecked() is True:
            classification_confidence = True
    # random forest
    elif classifier_name == cfg.rs.configurations.random_forest:
        if cfg.dialog.ui.pretrained_model_checkBox_2.isChecked() is True:
            pretrained_model = (
                cfg.dialog.ui.pretrained_model_combo_2.currentText())
            # exclude first element of combo that is empty
            if len(pretrained_model) == 1:
                pretrained_model = None
        if cfg.dialog.ui.best_estimator_checkBox.isChecked() is True:
            find_best_estimator = int(cfg.dialog.ui.steps_SpinBox.value())
        if cfg.dialog.ui.ovr_checkBox.isChecked() is True:
            classifier_name = cfg.rs.configurations.random_forest_ovr
        if cfg.dialog.ui.class_weight_checkBox.isChecked() is True:
            class_weight = 'balanced'
        if cfg.dialog.ui.cross_validation_checkBox_2.isChecked() is True:
            cross_validation = True
        else:
            cross_validation = False
        rf_number_trees = int(cfg.dialog.ui.number_trees_SpinBox.value())
        rf_min_samples_split = int(cfg.dialog.ui.min_split_SpinBox.value())
        if len(cfg.dialog.ui.max_features_lineEdit.text()) > 0:
            if cfg.dialog.ui.max_features_lineEdit.text() == 'sqrt':
                rf_max_features = 'sqrt'
            else:
                try:
                    if int(cfg.dialog.ui.max_features_lineEdit.text()) > 1:
                        rf_max_features = int(
                            cfg.dialog.ui.max_features_lineEdit.text())
                    else:
                        rf_max_features = float(
                            cfg.dialog.ui.max_features_lineEdit.text()
                        )
                except Exception as err:
                    str(err)
        if cfg.dialog.ui.confidence_raster_checkBox_4.isChecked() is True:
            classification_confidence = True
    # spectral angle mapping
    elif classifier_name == cfg.rs.configurations.spectral_angle_mapping:
        if cfg.dialog.ui.single_threshold_checkBox_6.isChecked() is True:
            threshold = cfg.dialog.ui.alg_threshold_SpinBox_3.value()
        if cfg.dialog.ui.single_threshold_checkBox_5.isChecked() is True:
            threshold = True
        if cfg.dialog.ui.signature_raster_checkBox.isChecked() is True:
            signature_raster = True
        if cfg.dialog.ui.confidence_raster_checkBox_5.isChecked() is True:
            classification_confidence = True
    # SVM
    elif classifier_name == cfg.rs.configurations.support_vector_machine:
        svm_c = cfg.dialog.ui.param_c_SpinBox.value()
        if len(cfg.dialog.ui.gamma_lineEdit.text()) > 0:
            if cfg.dialog.ui.gamma_lineEdit.text() == 'scale':
                svm_gamma = 'scale'
            elif cfg.dialog.ui.gamma_lineEdit.text() == 'auto':
                svm_gamma = 'auto'
            else:
                try:
                    svm_gamma = float(cfg.dialog.ui.gamma_lineEdit.text())
                except Exception as err:
                    str(err)
        if len(cfg.dialog.ui.kernel_lineEdit.text()) > 0:
            svm_kernel = cfg.dialog.ui.kernel_lineEdit.text()
        if cfg.dialog.ui.best_estimator_checkBox_3.isChecked() is True:
            find_best_estimator = int(cfg.dialog.ui.steps_SpinBox_3.value())
        if cfg.dialog.ui.cross_validation_checkBox.isChecked() is True:
            cross_validation = True
        else:
            cross_validation = False
        if cfg.dialog.ui.class_weight_checkBox_2.isChecked() is True:
            class_weight = 'balanced'
        if cfg.dialog.ui.confidence_raster_checkBox_6.isChecked() is True:
            classification_confidence = True
    # pretrained models
    elif classifier_name == 'pretrained':
        pretrained_segmentation = (
            cfg.dialog.ui.pretrained_model_combo_3.currentText())
        # exclude first element of combo that is empty
        if len(pretrained_segmentation) == 1:
            pretrained_segmentation = None

        model_class_names = (
            cfg.rs.configurations.segmentation_model_class_dict[
                pretrained_segmentation]
        )
        model_class_colors = (
            cfg.rs.configurations.segmentation_model_color_dict[
                pretrained_segmentation]
        )
        value_name_dictionary = {}
        value_color_dictionary = {}
        for m, name in enumerate(model_class_names):
            value_name_dictionary[m] = name
        for m, color in enumerate(model_class_colors):
            value_color_dictionary[m] = color
    # pretrained model
    if pretrained_model:
        additional_algorithm_name = classifier_name
        classifier_name = pretrained_model
        pretrained_model_path = f'{cfg.plugin_dir}/{classifier_name}.pth'
    # pretrained models
    if pretrained_segmentation:
        classifier_name = pretrained_segmentation
        pretrained_model_path = f'{cfg.plugin_dir}/{classifier_name}.pth'
    cfg.logger.log.debug(
        'input_bands: %s; output_path: %s; spectral_signatures: %s;'
        'macroclass: %s; algorithm_name: %s; threshold: %s; '
        'cross_validation: %s; signature_raster: %s; input_normalization: %s; '
        'load_classifier: %s; class_weight_ %s; find_best_estimator: %s; '
        'rf_max_features: %s; rf_number_trees: %s; rf_min_samples_split: %s; '
        'svm_c: %s; svm_gamma: %s; svm_kernel: %s; mlp_training_portion: %s;'
        'mlp_alpha: %s; mlp_learning_rate_init: %s; mlp_max_iter: %s;'
        ' mlp_batch_size: %s; mlp_activation: %s; mlp_hidden_layer_sizes: %s; '
        'additional_algorithm_name %s: classification_confidence: %s; '
        'only_fit: %s; save_classifier: %s' %
        (bandset_number, output_path, signature_catalog, macroclass,
         classifier_name, threshold, cross_validation, signature_raster,
         input_normalization, load_classifier, class_weight,
         find_best_estimator, rf_max_features, rf_number_trees,
         rf_min_samples_split, svm_c, svm_gamma, svm_kernel,
         mlp_training_portion, mlp_alpha, mlp_learning_rate_init, mlp_max_iter,
         mlp_batch_size, mlp_activation, mlp_hidden_layer_sizes,
         additional_algorithm_name, classification_confidence,
         only_fit, save_classifier)
    )
    # get bandset
    bandset_x = cfg.bandset_catalog.get(bandset_number)
    if bandset_x is None:
        cfg.mx.msg_war_6(bandset_number)
        return None
    band_count = bandset_x.get_band_count()
    cfg.logger.log.debug('bandset band count: %s' % (str(band_count)))
    if band_count == 0:
        cfg.mx.msg_war_6(bandset_number)
        return None
    cfg.ui_utils.add_progress_bar()
    if pretrained_model is not None:
        if (classifier_name ==
                cfg.rs.configurations.pytorch_pretrained_s2_swin_v2_base
                or classifier_name ==
                cfg.rs.configurations.pytorch_pretrained_s2_swin_v2_tiny):
            bandset_x = order_bandset_pretrained_sentinel_2(bandset_x)
        elif (classifier_name ==
              cfg.rs.configurations.pytorch_pretrained_l89_swin_v2_base):
            bandset_x = order_bandset_pretrained_landsat89(bandset_x)
    if pretrained_segmentation is not None:
        if (classifier_name ==
                cfg.rs.configurations.pytorch_pretrained_s2_swin_v2_base_seg):
            bandset_x = order_bandset_pretrained_sentinel_2_rgb8(bandset_x)
        elif (classifier_name ==
              cfg.rs.configurations.pytorch_pretrained_s2_swin_v2_base_rgb_seg
        ):
            bandset_x = order_bandset_pretrained_sentinel_2_rgb(bandset_x)
    # classification
    if preview_point is None:
        bandset = bandset_x
        finish_sound = True
        smtp = str(__name__)
    # classification preview
    else:
        finish_sound = False
        smtp = None
        cfg.logger.log.debug(
            'preview_point x: %s; y: %s'
            % (str(preview_point.x()), str(preview_point.y()))
        )
        # subset bandset
        preview_size = cfg.project_registry[cfg.reg_preview_size]
        # prepare virtual raster of input
        dummy_path = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix='.vrt'
        )
        prepared = cfg.rs.shared_tools.prepare_process_files(
            input_bands=bandset_number, output_path=dummy_path,
            bandset_catalog=cfg.bandset_catalog, overwrite=True
        )
        temporary_virtual_raster = prepared['temporary_virtual_raster']
        if type(temporary_virtual_raster) is list:
            temporary_virtual_raster = temporary_virtual_raster[0]
        # get pixel size
        x_size, y_size = cfg.util_gdal.get_pixel_size(temporary_virtual_raster)
        # calculate preview window
        left = preview_point.x() - (x_size * preview_size) / 2
        top = preview_point.y() + (y_size * preview_size) / 2
        right = preview_point.x() + (x_size * preview_size) / 2
        bottom = preview_point.y() - (y_size * preview_size) / 2
        # copy bandset and subset
        bandset = deepcopy(bandset_x)
        bandset.box_coordinate_list = [left, top, right, bottom]
        cfg.logger.log.debug(
            'bandset.box_coordinate_list: %s'
            % str([left, top, right, bottom])
        )
        # load classifier
        if load_classifier is None:
            # classifier path
            classifier_path = cfg.rs.configurations.temp.temporary_file_path(
                name_suffix=cfg.rs.configurations.rsmo_suffix
            )
            # calculate from training on the whole bandset
            if cfg.classifier_preview is None:
                # run classification
                try:
                    fit_classifier = cfg.rs.band_classification(
                        only_fit=True, save_classifier=True,
                        input_bands=bandset_x,
                        output_path=classifier_path,
                        spectral_signatures=signature_catalog,
                        macroclass=macroclass, algorithm_name=classifier_name,
                        #bandset_catalog=cfg.bandset_catalog,
                        threshold=threshold, signature_raster=signature_raster,
                        cross_validation=cross_validation,
                        input_normalization=input_normalization,
                        load_classifier=load_classifier,
                        class_weight=class_weight,
                        find_best_estimator=find_best_estimator,
                        rf_max_features=rf_max_features,
                        rf_number_trees=rf_number_trees,
                        rf_min_samples_split=rf_min_samples_split,
                        svm_c=svm_c, svm_gamma=svm_gamma,
                        svm_kernel=svm_kernel,
                        mlp_training_portion=mlp_training_portion,
                        mlp_alpha=mlp_alpha,
                        mlp_learning_rate_init=mlp_learning_rate_init,
                        mlp_max_iter=mlp_max_iter,
                        mlp_batch_size=mlp_batch_size,
                        mlp_activation=mlp_activation,
                        mlp_hidden_layer_sizes=mlp_hidden_layer_sizes,
                        classification_confidence=classification_confidence,
                        additional_algorithm_name=additional_algorithm_name,
                        pretrained_model_path=pretrained_model_path
                    )
                except Exception as err:
                    cfg.logger.log.error(str(err))
                    cfg.mx.msg_err_1()
                    cfg.ui_utils.remove_progress_bar(
                        smtp=smtp, sound=finish_sound, failed=True
                        )
                    return None
                if fit_classifier.check:
                    only_fit = False
                    save_classifier = False
                    cfg.classifier_preview = fit_classifier.extra['model_path']
                    cfg.logger.log.debug(
                        'cfg.classifier_preview: %s' % cfg.classifier_preview
                    )
                else:
                    cfg.mx.msg_err_1()
                    cfg.ui_utils.remove_progress_bar(
                        smtp=smtp, sound=finish_sound, failed=True
                        )
                    return None
            # load classifier
            load_classifier = cfg.classifier_preview
    # run classification
    try:
        output = cfg.rs.band_classification(
            input_bands=bandset, output_path=output_path,
            spectral_signatures=signature_catalog,
            macroclass=macroclass, algorithm_name=classifier_name,
            #bandset_catalog=cfg.bandset_catalog,
            threshold=threshold,
            signature_raster=signature_raster,
            cross_validation=cross_validation,
            input_normalization=input_normalization,
            load_classifier=load_classifier, class_weight=class_weight,
            find_best_estimator=find_best_estimator,
            rf_max_features=rf_max_features, rf_number_trees=rf_number_trees,
            rf_min_samples_split=rf_min_samples_split,
            svm_c=svm_c, svm_gamma=svm_gamma, svm_kernel=svm_kernel,
            mlp_training_portion=mlp_training_portion,
            mlp_alpha=mlp_alpha, mlp_learning_rate_init=mlp_learning_rate_init,
            mlp_max_iter=mlp_max_iter, mlp_batch_size=mlp_batch_size,
            mlp_activation=mlp_activation,
            mlp_hidden_layer_sizes=mlp_hidden_layer_sizes,
            classification_confidence=classification_confidence,
            additional_algorithm_name=additional_algorithm_name,
            pretrained_model_path=pretrained_model_path,
            only_fit=only_fit, save_classifier=save_classifier
        )
    except Exception as err:
        cfg.logger.log.error(str(err))
        output = None
    if output is None:
        cfg.mx.msg_err_1()
        failed = True
    elif output.check:
        failed = False
        if save_classifier is not True and preview_point is None:
            output_raster = output.path
            # add raster to layers
            raster = cfg.util_qgis.add_raster_layer(output_raster)
            if raster is False:
                cfg.logger.log.error('raster output not found')
                cfg.mx.msg_err_1()
                failed = True
            else:
                cfg.util_qgis.move_layer_to_top(raster)
                # apply symbology
                if pretrained_segmentation:
                    cfg.utils.classification_raster_symbol(
                        classification_layer=raster,
                        value_name_dictionary=value_name_dictionary,
                        value_color_dictionary=value_color_dictionary
                    )
                else:
                    apply_class_symbology(raster, macroclass)
                name = cfg.rs.files_directories.file_name(output_raster)
                directory = cfg.rs.files_directories.parent_directory(
                    output_raster
                )
                cfg.util_qgis.save_qml_style(
                    raster, '%s/%s.qml' % (directory, name)
                )
            if 'algorithm_raster' in output.extra:
                if output.extra['algorithm_raster'] is not None:
                    # add raster to layers
                    cfg.util_qgis.add_raster_layer(
                        output.extra['algorithm_raster']
                    )
            if 'signature_rasters' in output.extra:
                # add raster to layers
                try:
                    for s in output.extra['signature_rasters']:
                        if s is not None:
                            cfg.util_qgis.add_raster_layer(s)
                except Exception as err:
                    str(err)
    else:
        cfg.mx.msg_err_1()
        failed = True
    cfg.ui_utils.remove_progress_bar(smtp=smtp, sound=finish_sound,
                                     failed=failed)
    return output


# create classification preview
def create_preview(preview_point, classification_confidence=None):
    point = cfg.utils.check_point_in_image(point=preview_point)
    if point is False:
        cfg.mx.msg_war_3()
        return False
    cfg.preview_point = point
    output = run_classifier(
        preview_point=point,
        classification_confidence=classification_confidence
    )
    if output is None:
        return False
    elif output.check:
        if classification_confidence is None:
            output_raster = output.path
        else:
            if 'algorithm_raster' in output.extra:
                output_raster = output.extra['algorithm_raster']
            else:
                output_raster = None
        # move previous preview to group
        group = cfg.util_qgis.group_index(
            cfg.qgis_registry[cfg.reg_group_name]
        )
        if group is None:
            group = cfg.util_qgis.create_group(
                cfg.qgis_registry[cfg.reg_group_name]
            )
        if cfg.classification_preview is not None:
            cfg.util_qgis.move_layer(
                cfg.classification_preview,
                cfg.qgis_registry[cfg.reg_group_name]
            )
        # add preview
        cfg.classification_preview = cfg.util_qgis.add_raster_layer(
            output_raster
        )
        if cfg.dialog.ui.macroclass_radioButton.isChecked() is True:
            macroclass = True
        else:
            macroclass = False
        # apply symbology
        if (classification_confidence is None
                and cfg.classification_preview is not False):
            apply_class_symbology(cfg.classification_preview, macroclass)
        # move to top
        cfg.util_qgis.move_layer_to_top(cfg.classification_preview)
        cfg.util_qgis.set_group_visible(group, False)
        cfg.util_qgis.set_group_expanded(group, False)
        # enable map canvas render
        cfg.map_canvas.setRenderFlag(True)
        # enable Redo button
        if not cfg.simplified:
            cfg.show_preview_radioButton2.setChecked(True)
            cfg.redoPreviewButton.setEnabled(True)
        return True
    else:
        cfg.mx.msg_err_1()
        return False


# activate pointer for classification preview
def pointer_classification_preview_active():
    cfg.map_canvas.setMapTool(cfg.classification_preview_pointer)
    cursor = QCursor(QPixmap(':/pointer/icons/pointer/ROI_pointer.svg'))
    cfg.map_canvas.setCursor(cursor)


# left click pointer
def pointer_left_click(point):
    create_preview(point)


# right click pointer
def pointer_right_click(point):
    create_preview(point, classification_confidence=True)


# pretrained model info
def pretrained_model_info():
    pretrained_model = cfg.dialog.ui.pretrained_model_combo.currentText()
    text = cfg.rs.configurations.pretrained_model_dict[pretrained_model]
    cfg.dialog.ui.pretrained_textBrowser.clear()
    cfg.dialog.ui.pretrained_textBrowser.setText(text)


# pretrained model info
def pretrained_model_info_2():
    pretrained_model = cfg.dialog.ui.pretrained_model_combo_2.currentText()
    text = cfg.rs.configurations.pretrained_model_dict[pretrained_model]
    cfg.dialog.ui.pretrained_textBrowser_2.clear()
    cfg.dialog.ui.pretrained_textBrowser_2.setText(text)

# pretrained segmentation model info
def pretrained_model_info_3():
    pretrained_model = cfg.dialog.ui.pretrained_model_combo_3.currentText()
    text = cfg.rs.configurations.segmentation_model_dict[pretrained_model]
    cfg.dialog.ui.pretrained_textBrowser_3.clear()
    cfg.dialog.ui.pretrained_textBrowser_3.setText(text)


# pretrained model info
def add_pretrained_model_info_to_combo(info_dict):
    for i in info_dict:
        cfg.dialog.ui.pretrained_model_combo.addItem(i)
        cfg.dialog.ui.pretrained_model_combo_2.addItem(i)

# pretrained segmentation model info
def add_pretrained_segmentation_info_to_combo(info_dict):
    for i in info_dict:
        cfg.dialog.ui.pretrained_model_combo_3.addItem(i)


# order Sentinel-2 bands in bandset
def order_bandset_pretrained_sentinel_2(bandset):
    # order bands in band set
    # B04, B03, B02, B05, B06, B07, B08, B11, B12
    wl_list = [
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][3],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][2],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][1],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][4],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][5],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][6],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][7],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][11],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][12],
    ]
    s2_bands = bandset.get_absolute_paths()
    s2_band_list = []
    for wl in wl_list:
        band = bandset.get_band_by_wavelength(wavelength=wl,
                                                output_as_number=True)
        s2_band_list.append(s2_bands[band - 1])
    bandset_catalog_s2 = cfg.rs.bandset_catalog()
    bandset_catalog_s2.create_bandset(paths=s2_band_list, bandset_number=2)
    return bandset_catalog_s2.get(2)

# order Sentinel-2 bands in bandset
def order_bandset_pretrained_sentinel_2_rgb8(bandset):
    # order bands in band set
    # B04, B03, B02, B08
    wl_list = [
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][3],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][2],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][1],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][7],
    ]
    s2_bands = bandset.get_absolute_paths()
    s2_band_list = []
    for wl in wl_list:
        band = bandset.get_band_by_wavelength(wavelength=wl,
                                                output_as_number=True)
        s2_band_list.append(s2_bands[band - 1])
    bandset_catalog_s2 = cfg.rs.bandset_catalog()
    bandset_catalog_s2.create_bandset(paths=s2_band_list, bandset_number=2)
    return bandset_catalog_s2.get(2)

# order Sentinel-2 bands in bandset
def order_bandset_pretrained_sentinel_2_rgb(bandset):
    # order bands in band set
    # B04, B03, B02
    wl_list = [
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][3],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][2],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satSentinel2][0][1],
    ]
    s2_bands = bandset.get_absolute_paths()
    s2_band_list = []
    for wl in wl_list:
        band = bandset.get_band_by_wavelength(wavelength=wl,
                                                output_as_number=True)
        s2_band_list.append(s2_bands[band - 1])
    bandset_catalog_s2 = cfg.rs.bandset_catalog()
    bandset_catalog_s2.create_bandset(paths=s2_band_list, bandset_number=2)
    return bandset_catalog_s2.get(2)


# order Landsat 8/9 bands in bandset
def order_bandset_pretrained_landsat89(bandset):
    # order bands in band set
    # B01, B02, B03, B04, B05, B06, B07, B08, B09, B10, B11
    wl_list = [
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][0],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][1],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][2],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][4],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][5],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][7],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][8],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][3],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][6],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][9],
        cfg.rs.configurations.satellites[
            cfg.rs.configurations.satLandsat89][0][10],
    ]
    s2_bands = bandset.get_absolute_paths()
    s2_band_list = []
    for wl in wl_list:
        band = bandset.get_band_by_wavelength(wavelength=wl,
                                                output_as_number=True)
        s2_band_list.append(s2_bands[band - 1])
    bandset_catalog_s2 = cfg.rs.bandset_catalog()
    bandset_catalog_s2.create_bandset(paths=s2_band_list, bandset_number=2)
    return bandset_catalog_s2.get(2)


# set script button
def set_script():
    output_path = 'output_path'
    macroclass = classifier_name = threshold = signature_raster = None
    cross_validation = input_normalization = load_classifier = None
    class_weight = find_best_estimator = rf_max_features = None
    rf_number_trees = rf_min_samples_split = svm_c = svm_gamma = None
    svm_kernel = mlp_training_portion = mlp_alpha = None
    mlp_learning_rate_init = mlp_max_iter = mlp_batch_size = None
    mlp_activation = mlp_hidden_layer_sizes = classification_confidence = None
    bandset_number = cfg.dialog.ui.band_set_comb_spinBox_12.value()
    bandset_x = cfg.bandset_catalog.get_bandset_by_number(bandset_number)
    if bandset_x is not None:
        if cfg.dialog.ui.macroclass_radioButton.isChecked() is True:
            macroclass = True
        else:
            macroclass = False
        if cfg.dialog.ui.input_normalization_checkBox.isChecked() is True:
            if cfg.dialog.ui.z_score_radioButton.isChecked() is True:
                input_normalization = cfg.rs.configurations.z_score
            else:
                input_normalization = cfg.rs.configurations.linear_scaling
        if len(cfg.dialog.ui.label_classifier.text()) > 0:
            load_classifier = cfg.dialog.ui.label_classifier.text()
        classifier_index = cfg.dialog.ui.toolBox_classification.currentIndex()
        classifier_list = [
            cfg.rs.configurations.maximum_likelihood_a,
            cfg.rs.configurations.minimum_distance_a,
            cfg.rs.configurations.multi_layer_perceptron_a,
            cfg.rs.configurations.random_forest_a,
            cfg.rs.configurations.spectral_angle_mapping_a,
            cfg.rs.configurations.support_vector_machine_a,
            'pretrained'
        ]
        classifier_name = classifier_list[classifier_index]
        # maximum likelihood
        if classifier_name == cfg.rs.configurations.maximum_likelihood_a:
            if cfg.dialog.ui.single_threshold_checkBox.isChecked() is True:
                threshold = cfg.dialog.ui.alg_threshold_SpinBox_2.value()
            if cfg.dialog.ui.single_threshold_checkBox_2.isChecked() is True:
                threshold = True
            if cfg.dialog.ui.signature_raster_checkBox_3.isChecked() is True:
                signature_raster = True
            if cfg.dialog.ui.confidence_raster_checkBox.isChecked() is True:
                classification_confidence = True
        # minimum distance
        elif classifier_name == cfg.rs.configurations.minimum_distance_a:
            if cfg.dialog.ui.single_threshold_checkBox_4.isChecked() is True:
                threshold = cfg.dialog.ui.alg_threshold_SpinBox_4.value()
            if cfg.dialog.ui.single_threshold_checkBox_3.isChecked() is True:
                threshold = True
            if cfg.dialog.ui.signature_raster_checkBox_2.isChecked() is True:
                signature_raster = True
            if cfg.dialog.ui.confidence_raster_checkBox_2.isChecked() is True:
                classification_confidence = True
        # multi layer perceptron
        elif classifier_name == cfg.rs.configurations.multi_layer_perceptron_a:
            if cfg.dialog.ui.pytorch_radioButton.isChecked() is True:
                classifier_name = (
                    cfg.rs.configurations.pytorch_multi_layer_perceptron_a
                )
            if cfg.dialog.ui.best_estimator_checkBox_2.isChecked() is True:
                find_best_estimator = int(
                    cfg.dialog.ui.steps_SpinBox_2.value()
                )
            if cfg.dialog.ui.cross_validation_checkBox_3.isChecked() is True:
                cross_validation = True
            else:
                cross_validation = False
            mlp_training_portion = (
                cfg.dialog.ui.training_proportion_SpinBox.value())
            mlp_learning_rate_init = (
                cfg.dialog.ui.learning_rate_SpinBox.value()
            )
            mlp_alpha = cfg.dialog.ui.alpha_SpinBox.value()
            mlp_max_iter = int(cfg.dialog.ui.max_iterations_SpinBox.value())
            try:
                mlp_batch_size = int(cfg.dialog.ui.batch_size_lineEdit.text())
            except Exception as err:
                str(err)
                mlp_batch_size = 'auto'
            mlp_activation = cfg.dialog.ui.activation_lineEdit.text()
            hidden_layers = cfg.dialog.ui.hidden_layers_lineEdit.text()
            try:
                mlp_hidden_layer_sizes = ast.literal_eval(f'[{hidden_layers}]')
            except Exception as err:
                mlp_hidden_layer_sizes = [100]
                cfg.mx.msg_war_2()
                str(err)
            if cfg.dialog.ui.confidence_raster_checkBox_3.isChecked() is True:
                classification_confidence = True
        # random forest
        elif classifier_name == cfg.rs.configurations.random_forest_a:
            if cfg.dialog.ui.best_estimator_checkBox.isChecked() is True:
                find_best_estimator = int(cfg.dialog.ui.steps_SpinBox.value())
            if cfg.dialog.ui.ovr_checkBox.isChecked() is True:
                classifier_name = cfg.rs.configurations.random_forest_a_ovr
            if cfg.dialog.ui.class_weight_checkBox.isChecked() is True:
                class_weight = 'balanced'
            if cfg.dialog.ui.cross_validation_checkBox_2.isChecked() is True:
                cross_validation = True
            else:
                cross_validation = False
            rf_number_trees = int(cfg.dialog.ui.number_trees_SpinBox.value())
            rf_min_samples_split = int(cfg.dialog.ui.min_split_SpinBox.value())
            if len(cfg.dialog.ui.max_features_lineEdit.text()) > 0:
                if cfg.dialog.ui.max_features_lineEdit.text() == 'sqrt':
                    rf_max_features = 'sqrt'
                else:
                    try:
                        if int(cfg.dialog.ui.max_features_lineEdit.text()) > 1:
                            rf_max_features = int(
                                cfg.dialog.ui.max_features_lineEdit.text())
                        else:
                            rf_max_features = float(
                                cfg.dialog.ui.max_features_lineEdit.text()
                            )
                    except Exception as err:
                        str(err)
            if cfg.dialog.ui.confidence_raster_checkBox_4.isChecked() is True:
                classification_confidence = True
        # spectral angle mapping
        elif classifier_name == cfg.rs.configurations.spectral_angle_mapping_a:
            if cfg.dialog.ui.single_threshold_checkBox_6.isChecked() is True:
                threshold = cfg.dialog.ui.alg_threshold_SpinBox_3.value()
            if cfg.dialog.ui.single_threshold_checkBox_5.isChecked() is True:
                threshold = True
            if cfg.dialog.ui.signature_raster_checkBox.isChecked() is True:
                signature_raster = True
            if cfg.dialog.ui.confidence_raster_checkBox_5.isChecked() is True:
                classification_confidence = True
        # SVM
        elif classifier_name == cfg.rs.configurations.support_vector_machine_a:
            svm_c = cfg.dialog.ui.param_c_SpinBox.value()
            if len(cfg.dialog.ui.gamma_lineEdit.text()) > 0:
                if cfg.dialog.ui.gamma_lineEdit.text() == 'scale':
                    svm_gamma = 'scale'
                elif cfg.dialog.ui.gamma_lineEdit.text() == 'auto':
                    svm_gamma = 'auto'
                else:
                    try:
                        svm_gamma = float(cfg.dialog.ui.gamma_lineEdit.text())
                    except Exception as err:
                        str(err)
            if len(cfg.dialog.ui.kernel_lineEdit.text()) > 0:
                svm_kernel = cfg.dialog.ui.kernel_lineEdit.text()
            if cfg.dialog.ui.best_estimator_checkBox_3.isChecked() is True:
                find_best_estimator = int(
                    cfg.dialog.ui.steps_SpinBox_3.value()
                )
            if cfg.dialog.ui.cross_validation_checkBox.isChecked() is True:
                cross_validation = True
            else:
                cross_validation = False
            if cfg.dialog.ui.class_weight_checkBox_2.isChecked() is True:
                class_weight = 'balanced'
            if cfg.dialog.ui.confidence_raster_checkBox_6.isChecked() is True:
                classification_confidence = True
        # get input band paths
        files = bandset_x.get_absolute_paths()
        paths = '['
        for file in files:
            paths += '"%s", ' % file
        paths = paths[:-2] + ']'
        if paths == ']':
            paths = '[]'
    else:
        paths = '[]'
    if cfg.scp_training is None:
        training_path = 'training_path'
    else:
        training_path = cfg.scp_training.output_path
    # copy the command
    session = ('rs = remotior_sensus.Session(n_processes=%s, available_ram=%s)'
               % (cfg.qgis_registry[cfg.reg_threads_value],
                  cfg.qgis_registry[cfg.reg_ram_value]))
    command = ('# classification (input files from bandset)\n'
               'rs.band_classification(input_bands=%s, output_path="%s", '
               'spectral_signatures="%s", macroclass=%s, algorithm_name="%s", '
               'threshold="%s", signature_raster=%s, cross_validation=%s,'
               'input_normalization="%s", load_classifier="%s", '
               'class_weight="%s", find_best_estimator=%s, '
               'rf_max_features=%s, rf_number_trees=%s, '
               'rf_min_samples_split=%s, svm_c=%s, svm_gamma="%s", '
               'svm_kernel="%s", mlp_training_portion="%s", '
               'mlp_alpha=%s, mlp_learning_rate_init=%s, mlp_max_iter=%s, '
               'mlp_batch_size="%s", mlp_activation="%s", '
               'mlp_hidden_layer_sizes=%s, classification_confidence=%s)'
               % (str(paths), str(output_path),
                  str(training_path), macroclass,
                  str(classifier_name), str(threshold),
                  str(signature_raster), str(cross_validation),
                  str(input_normalization), str(load_classifier),
                  str(class_weight), str(find_best_estimator),
                  str(rf_max_features), str(rf_number_trees),
                  str(rf_min_samples_split), str(svm_c), str(svm_gamma),
                  str(svm_kernel), str(mlp_training_portion), str(mlp_alpha),
                  str(mlp_learning_rate_init), str(mlp_max_iter),
                  str(mlp_batch_size), str(mlp_activation),
                  str(mlp_hidden_layer_sizes), str(classification_confidence)
                  ))
    previous = cfg.dialog.ui.plainTextEdit_batch.toPlainText()
    if 'import remotior_sensus' in previous:
        text = '\n'.join([previous, command])
    else:
        text = '\n'.join(
            ['import remotior_sensus', session, previous, command]
        )
    cfg.dialog.ui.plainTextEdit_batch.setPlainText(
        text.replace('"None"', 'None').replace('"False"', 'False').replace(
            '"True"', 'True'
        )
    )
    cfg.input_interface.script_tab()
