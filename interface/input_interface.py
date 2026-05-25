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


from inspect import stack
from re import findall

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (QIcon, QFont, QDesktopServices, QPixmap, QAction,
                         QKeySequence)
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QRadioButton, QLabel, QMenu, QTabBar,
    QDoubleSpinBox, QTreeWidgetItem, QSpinBox, QWidget, QHBoxLayout,
    QWidgetAction, QLineEdit
)
from requests import get

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

try:
    # noinspection PyUnresolvedReferences
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    # noinspection PyPep8Naming
    def _fromUtf8(s):
        return s


# function dictionaries
# noinspection PyTypeChecker
def function_dictionaries(simplified=False):
    if simplified:
        cfg.first_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Download products'
            ): download_products_tab
        }
        # Basic tools
        cfg.basic_tools_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Import signatures'
            ): import_signatures_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Export signatures'
            ): export_signatures_tab,
        }
        # Preprocessing
        cfg.preprocessing_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Clip raster bands'
            ): clip_raster_bands_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Image conversion'
            ): image_conversion_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Masking bands'
            ): masking_bands_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Split raster bands'
            ): split_bands_tab,
        }
        # Band processing
        cfg.band_processing_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Classification'
            ): classification_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Clustering'
            ): band_clustering_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Combination'
            ): combination_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Dilation'
            ): dilation_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Erosion'
            ): erosion_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Sieve'
            ): sieve_tab,
        }
        cfg.postprocessing_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Accuracy'
            ): accuracy_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Classification report'
            ): classification_report_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Classification to vector'
            ): classification_to_vector_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Reclassification'
            ): reclassification_tab
        }
        cfg.calc_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Band calc'
            ): band_calc_tab
        }
        cfg.top_tree_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Basic tools'
            ): top_tree,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Preprocessing'
            ): top_tree,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Band processing'
            ): top_tree,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Postprocessing'
            ): top_tree,
        }
        cfg.setting_functions = {}
    else:
        cfg.first_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Band set'
            ): bandset_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Download products'
            ): download_products_tab
        }
        cfg.basic_tools_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin',
                'RGB composite'
            ): rgb_composite_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin',
                'Multiple ROI creation'
            ): multiple_roi_creation_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Import signatures'
            ): import_signatures_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Export signatures'
            ): export_signatures_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Signature threshold'
            ): signature_threshold_tab
        }
        cfg.preprocessing_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Clip raster bands'
            ): clip_raster_bands_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Image conversion'
            ): image_conversion_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Masking bands'
            ): masking_bands_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Mosaic band sets'
            ): mosaic_bandsets_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Reproject raster bands'
            ): reproject_bands_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Split raster bands'
            ): split_bands_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Stack raster bands'
            ): stack_bands_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Vector to raster'
            ): vector_to_raster_tab
        }
        cfg.band_processing_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Classification'
            ): classification_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Clustering'
            ): band_clustering_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'PCA'
            ): pca_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Combination'
            ): combination_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Dilation'
            ): dilation_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Erosion'
            ): erosion_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Neighbor'
            ): band_neighbor_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Sieve'
            ): sieve_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Spectral distance'
            ): spectral_distance_tab
        }
        cfg.postprocessing_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Accuracy'
            ): accuracy_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Classification report'
            ): classification_report_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Cross classification'
            ): cross_classification_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Classification to vector'
            ): classification_to_vector_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Edit raster'
            ): edit_raster_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Raster zonal stats'
            ): raster_zonal_stats_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Reclassification'
            ): reclassification_tab
        }
        cfg.top_tree_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Basic tools'
            ): top_tree,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Preprocessing'
            ): top_tree,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Band processing'
            ): top_tree,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Postprocessing'
            ): top_tree,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Settings'
            ): top_tree
        }
        cfg.calc_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Band calc'
            ): band_calc_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Script'
            ): script_tab
        }
        cfg.setting_functions = {
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Debug'
            ): debug_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Interface'
            ): interface_tab,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Processing setting'
            ): processing_settings_tab
        }
    cfg.other_functions = {
        QApplication.translate(
            'semiautomaticclassificationplugin', 'User manual'
        ): quick_guide,
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Help'
        ): ask_help,
        QApplication.translate(
            'semiautomaticclassificationplugin', 'About'
        ): about_tab
    }
    cfg.first_icons = {
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Band set'
        ): 'semiautomaticclassificationplugin_bandset_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Download products'
        ): 'semiautomaticclassificationplugin_download_arrow.svg'
    }
    cfg.basic_tools_icons = {
        QApplication.translate(
            'semiautomaticclassificationplugin', 'RGB composite'
        ): 'semiautomaticclassificationplugin_rgb_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Multiple ROI creation'
        ): 'semiautomaticclassificationplugin_roi_multiple.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Import signatures'
        ): 'semiautomaticclassificationplugin_import_spectral_library.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Export signatures'
        ): 'semiautomaticclassificationplugin_export_spectral_library.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Signature threshold'
        ): 'semiautomaticclassificationplugin_threshold_tool.svg'
    }
    cfg.preprocessing_icons = {
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Clip raster bands'
        ): 'semiautomaticclassificationplugin_clip_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Image conversion'
        ): 'semiautomaticclassificationplugin_landsat8_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Masking bands'
        ): 'semiautomaticclassificationplugin_cloud_masking_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Mosaic band sets'
        ): 'semiautomaticclassificationplugin_mosaic_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Reproject raster bands'
        ): 'semiautomaticclassificationplugin_reproject_raster_bands.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Split raster bands'
        ): 'semiautomaticclassificationplugin_split_raster.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Stack raster bands'
        ): 'semiautomaticclassificationplugin_stack_raster.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Vector to raster'
        ): 'semiautomaticclassificationplugin_vector_to_raster_tool.svg'
    }
    cfg.band_processing_icons = {
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Classification'
        ):
            'semiautomaticclassificationplugin_classification.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Clustering'
        ):
            'semiautomaticclassificationplugin_clustering.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'PCA'
        ):
            'semiautomaticclassificationplugin_pca_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Combination'
        ):
            'semiautomaticclassificationplugin_band_combination_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Dilation'
        ):
            'semiautomaticclassificationplugin_classification_dilation.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Neighbor'
        ):
            'semiautomaticclassificationplugin_neighbor_pixels.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Sieve'
        ):
            'semiautomaticclassificationplugin_classification_sieve.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Erosion'
        ):
            'semiautomaticclassificationplugin_classification_erosion.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Spectral distance'
        ):
            'semiautomaticclassificationplugin_spectral_distance.svg'
    }
    cfg.postprocessing_icons = {
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Accuracy'
        ): 'semiautomaticclassificationplugin_accuracy_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Classification report'
        ):
            'semiautomaticclassificationplugin_report_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Cross classification'
        ):
            'semiautomaticclassificationplugin_cross_classification.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Classification to vector'
        ):
            'semiautomaticclassificationplugin_class_to_vector_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Edit raster'
        ):
            'semiautomaticclassificationplugin_edit_raster.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Raster zonal stats'
        ):
            'semiautomaticclassificationplugin_zonal_stat_raster_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Reclassification'
        ):
            'semiautomaticclassificationplugin_reclassification_tool.svg'
    }
    cfg.calc_icons = {
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Band calc'
        ): 'semiautomaticclassificationplugin_bandcalc_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Script'
        ): 'semiautomaticclassificationplugin_batch.svg'
    }
    cfg.other_icons = {
        QApplication.translate(
            'semiautomaticclassificationplugin', 'User manual'
        ): 'guide.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Help'
        ): 'help.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'About'
        ): 'fromGIStoRS.png'
    }
    cfg.setting_icons = {
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Debug'
        ): None,
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Interface'
        ): None,
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Processing setting'
        ): None
    }
    dictionaries = [
        cfg.first_functions, cfg.basic_tools_functions,
        cfg.preprocessing_functions, cfg.band_processing_functions,
        cfg.postprocessing_functions, cfg.top_tree_functions,
        cfg.calc_functions, cfg.other_functions, cfg.setting_functions
    ]
    return dictionaries


""" Interface functions """


def load_input_toolbar():
    cfg.working_toolbar = cfg.iface.addToolBar('SCP Working Toolbar')
    cfg.working_toolbar.setObjectName('SCP Working Toolbar')
    load_working_toolbar()
    set_dock_tabs()


# SCP Working Toolbar
# noinspection PyUnresolvedReferences,PyTypeChecker
def load_working_toolbar():
    add_toolbar_action(
        show_plugin, 'semiautomaticclassificationplugin.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Semi-Automatic Classification Plugin'
            )
    )
    # button zoom to image
    add_toolbar_action(
        cfg.util_qgis.zoom_to_bandset,
        'semiautomaticclassificationplugin_zoom_to_Image.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Zoom to input image extent'
            )
    )
    # radio button show hide input image
    cfg.inputImageRadio = add_toolbar_radio(
        show_hide_input_mage,
        QApplication.translate('semiautomaticclassificationplugin', 'RGB = '),
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Show/hide the input image'
            )
    )
    # combo RGB composite
    cfg.rgb_combo = QComboBox(cfg.iface.mainWindow())
    cfg.rgb_combo.setFixedWidth(80)
    cfg.rgb_combo.setEditable(True)
    cfg.working_toolbar.addWidget(cfg.rgb_combo)
    cfg.rgb_combo.setToolTip(
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Select a RGB color composite'
            )
        )
    cfg.rgb_combo.currentIndexChanged.connect(rgb_combo_changed)
    # local cumulative cut stretch button
    cfg.local_cumulative_stretch_toolButton = add_toolbar_action(
        cfg.util_qgis.set_raster_cumulative_stretch,
        'semiautomaticclassificationplugin_bandset_cumulative_stretch_tool'
        '.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Local cumulative cut stretch of band set'
            )
    )
    # local standard deviation stretch button
    cfg.local_std_dev_stretch_toolButton = add_toolbar_action(
        cfg.util_qgis.set_raster_std_dev_stretch,
        'semiautomaticclassificationplugin_bandset_std_dev_stretch_tool.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Local standard deviation stretch of band set'
            )
    )
    # button zoom to ROI
    cfg.zoom_to_temp_roi = add_toolbar_action(
        zoom_to_temp_roi, 'semiautomaticclassificationplugin_zoom_to_ROI.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Zoom to temporary ROI'
            )
    )
    # radio button show hide ROI
    cfg.show_ROI_radioButton = add_toolbar_radio(
        cfg.scp_dock.show_hide_roi, QApplication.translate(
            'semiautomaticclassificationplugin', 'ROI     '
            ),
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Show/hide the temporary ROI'
            )
    )
    # manual ROI pointer
    cfg.polygonROI_Button = add_toolbar_action(
        cfg.scp_dock.pointer_manual_roi_active,
        'semiautomaticclassificationplugin_manual_ROI.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Create a ROI polygon'
            )
    )
    # pointer button
    cfg.pointerButton = add_toolbar_action(
        cfg.scp_dock.pointer_region_growing_roi_active,
        'semiautomaticclassificationplugin_roi_single.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Activate ROI pointer'
            )
    )
    # redo button
    cfg.redo_ROI_Button = add_toolbar_action(
        cfg.scp_dock.redo_roi,
        'semiautomaticclassificationplugin_roi_redo.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Redo the ROI at the same point'
            )
    )
    cfg.redo_ROI_Button.setEnabled(False)
    style = (
        'background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1,'
        ' y2:0, stop:0 #535353, stop:1 #535353); color : white'
    )
    # spinbox spectral distance
    lbl_spectral_distance = add_toolbar_label(
        QApplication.translate('semiautomaticclassificationplugin', ' Dist'),
        'Yes'
    )
    lbl_spectral_distance.setStyleSheet(_fromUtf8(style))
    cfg.Range_radius_spin = add_toolbar_spin(
        cfg.scp_dock.range_radius,
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Similarity of pixels (distance in radiometry unit)'
            ),
        6, 1e-06, 10000.0, 0.001, 0.01
    )
    # spinbox min size
    label_min = add_toolbar_label(
        QApplication.translate('semiautomaticclassificationplugin', ' Min'),
        'Yes'
        )
    label_min.setStyleSheet(_fromUtf8(style))
    cfg.roi_min_size_spin = add_toolbar_spin(
        cfg.scp_dock.roi_min_size,
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Minimum area of ROI (in pixel unit)'
            ), 0, 1, 10000,
        1, 60, 60
    )
    # spinbox max size
    label_max = add_toolbar_label(
        QApplication.translate('semiautomaticclassificationplugin', ' Max'),
        'Yes'
        )
    label_max.setStyleSheet(_fromUtf8(style))
    cfg.max_roi_width_spin = add_toolbar_spin(
        cfg.scp_dock.max_roi_width,
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Side of a square which inscribes the ROI, '
            'defining the maximum width thereof (in pixel unit)'
            ),
        0, 1, 10000, 1, int(cfg.project_registry[cfg.reg_roi_max_width]), 60
    )
    # button zoom to preview
    add_toolbar_action(
        zoom_to_preview,
        'semiautomaticclassificationplugin_zoom_to_preview.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Zoom to the classification preview'
            )
    )
    # radio button show hide preview
    cfg.show_preview_radioButton2 = add_toolbar_radio(
        show_hide_preview, QApplication.translate(
            'semiautomaticclassificationplugin', 'Preview '
            ),
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Show/hide the classification preview'
            )
    )
    # preview pointer button
    add_toolbar_action(
        cfg.classification.pointer_classification_preview_active,
        'semiautomaticclassificationplugin_preview.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Activate classification preview pointer'
            )
    )
    cfg.redoPreviewButton = add_toolbar_action(
        redo_preview, 'semiautomaticclassificationplugin_preview_redo.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin',
            'Redo the classification preview at the same point'
            )
    )
    cfg.redoPreviewButton.setEnabled(False)
    # spinbox transparency
    lbl_t = add_toolbar_label(
        QApplication.translate('semiautomaticclassificationplugin', ' T'),
        'Yes'
        )
    lbl_t.setStyleSheet(_fromUtf8(style))
    add_toolbar_spin(
        change_transparency, QApplication.translate(
            'semiautomaticclassificationplugin', 'Set preview transparency'
            ), 0, 0,
        100, 10, 0, 50
    )
    # spinbox size
    lbl_s = add_toolbar_label(
        QApplication.translate('semiautomaticclassificationplugin', ' S'),
        'Yes'
        )
    lbl_s.setStyleSheet(_fromUtf8(style))
    cfg.preview_size_spinBox = add_toolbar_spin(
        preview_size, QApplication.translate(
            'semiautomaticclassificationplugin',
            'Set the preview size (in pixel unit)'
            ),
        0, 1, 1000000, 100, int(cfg.project_registry[cfg.reg_preview_size]),
        60
    )
    add_toolbar_action(
        cfg.utils.create_kml_from_map,
        'semiautomaticclassificationplugin_kml_add.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Create KML'
            )
    )
    add_toolbar_action(
        cfg.utils.create_copernicus_browser_link_from_map,
        'semiautomaticclassificationplugin_copernicus_browser_link.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Open Copernicus Browser'
            )
    )
    cfg.on_off_button_1 = add_toolbar_action(
        activate_layer_1, 'On/Off 1',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'On/Off 1'
            )
    )
    cfg.on_off_button_1.setToolTip(
        QApplication.translate('semiautomaticclassificationplugin',
                               'Press Z to show/hide the layer 1')
    )
    cfg.layer_on_off_1 = QLineEdit(cfg.iface.mainWindow())
    cfg.layer_on_off_1.setFixedWidth(80)
    cfg.layer_on_off_1.setToolTip(
        QApplication.translate('semiautomaticclassificationplugin',
                               'Enter the name of layer 1')
    )
    cfg.layer_on_off_1.editingFinished.connect(key_sequence_z)
    cfg.working_toolbar.addWidget(cfg.layer_on_off_1)
    cfg.on_off_button_2 = add_toolbar_action(
        activate_layer_2, 'On/Off 2',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'On/Off 2'
            )
    )
    cfg.on_off_button_2.setToolTip(
        QApplication.translate('semiautomaticclassificationplugin',
                               'Press X to show/hide the layer 2')
    )
    cfg.layer_on_off_2 = QLineEdit(cfg.iface.mainWindow())
    cfg.layer_on_off_2.setFixedWidth(80)
    cfg.layer_on_off_2.setToolTip(
        QApplication.translate('semiautomaticclassificationplugin',
                               'Enter the name of layer 2')
    )
    cfg.layer_on_off_2.editingFinished.connect(key_sequence_x)
    cfg.working_toolbar.addWidget(cfg.layer_on_off_2)
    cfg.on_off_button_3 = add_toolbar_action(
        activate_layer_3, 'On/Off 3',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'On/Off 3'
            )
    )
    cfg.on_off_button_3.setToolTip(
        QApplication.translate('semiautomaticclassificationplugin',
                               'Press C to show/hide the layer 3')
    )
    cfg.layer_on_off_3 = QLineEdit(cfg.iface.mainWindow())
    cfg.layer_on_off_3.setFixedWidth(80)
    cfg.layer_on_off_3.setToolTip(
        QApplication.translate('semiautomaticclassificationplugin',
                               'Enter the name of layer 3')
    )
    cfg.layer_on_off_3.editingFinished.connect(key_sequence_c)
    cfg.working_toolbar.addWidget(cfg.layer_on_off_3)


# menu index
# noinspection PyTypeChecker
def menu_index():
    dictionaries = function_dictionaries(False)
    try:
        # translate
        n_dict = {}
        for menu_dict in dictionaries:
            for val in menu_dict:
                n_dict[QApplication.translate(
                    'semiautomaticclassificationplugin', val
                    )] = menu_dict[val]
        s = cfg.dialog.ui.menu_treeWidget.selectedItems()
        n = s[0].text(0)
        t = cfg.dialog.ui.menu_treeWidget
        t.blockSignals(True)
        cfg.dialog.ui.SCP_tabs.blockSignals(True)
        n_dict[n]()
        s[0].setExpanded(True)
        cfg.dialog.ui.SCP_tabs.blockSignals(False)
        t.blockSignals(False)
    except Exception as err:
        str(err)
        cfg.dialog.ui.SCP_tabs.blockSignals(False)
        t = cfg.dialog.ui.menu_treeWidget
        t.blockSignals(False)


# menu index
# noinspection PyTypeChecker
def menu_index_simplified():
    dictionaries = function_dictionaries(True)
    try:
        # translate
        n_dict = {}
        for menu_dict in dictionaries:
            for val in menu_dict:
                n_dict[QApplication.translate(
                    'semiautomaticclassificationplugin', val
                    )] = menu_dict[val]
        s = cfg.dialog.ui.menu_treeWidget.selectedItems()
        n = s[0].text(0)
        t = cfg.dialog.ui.menu_treeWidget
        t.blockSignals(True)
        cfg.dialog.ui.SCP_tabs.blockSignals(True)
        n_dict[n]()
        s[0].setExpanded(True)
        cfg.dialog.ui.SCP_tabs.blockSignals(False)
        t.blockSignals(False)
    except Exception as err:
        str(err)
        cfg.dialog.ui.SCP_tabs.blockSignals(False)
        t = cfg.dialog.ui.menu_treeWidget
        t.blockSignals(False)


# add spinbox
# noinspection PyUnresolvedReferences,PyTypeChecker
def add_toolbar_spin(
        function, tooltip, decimals, minimum, maximum, step, value, width=100
):
    spin = QDoubleSpinBox(cfg.iface.mainWindow())
    spin.setFixedWidth(width)
    spin.setDecimals(decimals)
    spin.setMinimum(minimum)
    spin.setMaximum(maximum)
    spin.setSingleStep(step)
    spin.setProperty('value', value)
    spin.setToolTip(
        QApplication.translate('semiautomaticclassificationplugin', tooltip)
        )
    cfg.working_toolbar.addWidget(spin)
    spin.valueChanged.connect(function)
    return spin


# add radio button
# noinspection PyTypeChecker
def add_toolbar_radio(function, text, tooltip):
    radio = QRadioButton(cfg.iface.mainWindow())
    radio.setToolTip(
        QApplication.translate('semiautomaticclassificationplugin', tooltip)
        )
    radio.setStyleSheet(_fromUtf8('background-color : #656565; color : white'))
    radio.setText(
        QApplication.translate('semiautomaticclassificationplugin', text)
        )
    radio.setChecked(True)
    radio.setAutoExclusive(False)
    cfg.working_toolbar.addWidget(radio)
    # noinspection PyUnresolvedReferences
    radio.clicked.connect(function)
    return radio


# add label to toolbar
# noinspection PyTypeChecker
def add_toolbar_label(text, black=None, width=None):
    font = QFont()
    font.setFamily(_fromUtf8('FreeSans'))
    font.setBold(True)
    font.setWeight(75)
    lbl = QLabel(cfg.iface.mainWindow())
    lbl.setFont(font)
    if black is None:
        lbl.setStyleSheet(
            _fromUtf8('background-color : #656565; color : white')
        )
    else:
        lbl.setStyleSheet(_fromUtf8('color : black'))
    lbl.setObjectName(_fromUtf8('lbl'))
    if width is not None:
        lbl.setFixedWidth(width)
    lbl.setMaximumHeight(18)
    lbl.setText(
        QApplication.translate('semiautomaticclassificationplugin', text)
        )
    cfg.working_toolbar.addWidget(lbl)
    return lbl


# Add toolbar action
def add_toolbar_action(function, icon_name, tooltip):
    action = QAction(
        QIcon(f'{cfg.plugin_dir}/ui/icons/{icon_name}'), tooltip,
        cfg.iface.mainWindow()
    )
    action.setToolTip(tooltip)
    # noinspection PyUnresolvedReferences
    action.triggered.connect(function)
    cfg.working_toolbar.addAction(action)
    return action


# show plugin
def show_plugin():
    # close the dialog
    cfg.dialog.close()
    activate_docks()
    if cfg.simplified:
        download_products_tab()
    # show the dialog
    cfg.dialog.show()
    cfg.ui_utils.set_interface(True)
    cfg.rs.configurations.action = True


# simplified interface
def simplified_interface(state):
    # change registry key if registry simplified
    if state:
        cfg.qgis_registry[cfg.reg_simplified] = 2
    else:
        cfg.qgis_registry[cfg.reg_simplified] = 0
    cfg.mx.msg_inf_8()


# activate docks
def activate_docks():
    if cfg.simplified:
        cfg.dock_class_simpl_dlg.show()
    else:
        cfg.dock_class_dlg.show()
        cfg.working_toolbar.show()


# connect resize event
def resize_event(event):
    size = event.size()
    cfg.qgis_registry[cfg.reg_window_size_w] = str(size.width())
    cfg.qgis_registry[cfg.reg_window_size_h] = str(size.height())


# user manual
def quick_guide():
    QDesktopServices().openUrl(
        QtCore.QUrl(
            'https://fromgistors.blogspot.com/p/user-manual.html?spref=scp'
        )
    )


# help
def ask_help():
    QDesktopServices().openUrl(
        QtCore.QUrl(
            'https://fromgistors.blogspot.com/p/online-help.html?spref=scp'
        )
    )


# add item to menu
def add_menu_item(menu, function, icon_name, name):
    try:
        action = QAction(
            QIcon(f'{cfg.plugin_dir}/ui/icons/{icon_name}'), name,
            cfg.iface.mainWindow()
        )
    except Exception as err:
        str(err)
        action = QAction(name, cfg.iface.mainWindow())
    action.setObjectName('action')
    # noinspection PyUnresolvedReferences
    action.triggered.connect(function)
    menu.addAction(action)
    return action


# add item to tree
def add_tree_item(tree, icon_name, name):
    action = QTreeWidgetItem(tree)
    action.setText(0, name)
    try:
        action.setIcon(0, QIcon(f'{cfg.plugin_dir}/ui/icons/{icon_name}'))
    except Exception as err:
        str(err)
    return action


# add checkbox to tree
def add_tree_checkbox(tree, icon_name, name, checked=True):
    action = QTreeWidgetItem(tree)
    action.setText(0, name)
    try:
        action.setIcon(0, QIcon(f'{cfg.plugin_dir}/ui/icons/{icon_name}'))
    except Exception as err:
        str(err)
    if checked:
        action.setCheckState(0, Qt.CheckState.Checked)
    else:
        action.setCheckState(0, Qt.CheckState.Unchecked)
    return action


# add spinbox to tree
def add_tree_spinbox(tree, subtree, function, name, minimum, maximum, value):
    if subtree is None:
        subtree = tree
    action = QTreeWidgetItem(subtree)
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    label = QLabel(name)
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setValue(value)
    spin.valueChanged.connect(function)
    layout.addWidget(label)
    layout.addWidget(spin)
    tree.setItemWidget(action, 0, widget)
    return spin


def tree_item_changed(item, column):
    state = item.checkState(column)
    text = item.text(column)
    if text == 'Simplified interface':
        if state == Qt.CheckState.Checked:
            simplified_interface(True)
        else:
            simplified_interface(False)


# add checkbox to menu
def add_menu_checkbox(menu, function, icon_name, name, checked=True):
    try:
        action = QAction(
            QIcon(f'{cfg.plugin_dir}/ui/icons/{icon_name}'), name,
            cfg.iface.mainWindow()
        )
    except Exception as err:
        str(err)
        action = QAction(name, cfg.iface.mainWindow())
    action.setObjectName('action')
    # noinspection PyUnresolvedReferences
    action.triggered.connect(function)
    action.setCheckable(True)
    action.setChecked(checked)
    menu.addAction(action)
    return action


# add spin to menu
def add_menu_spinbox(menu, function, icon_name, name, minimum, maximum, value):
    _icon_name = icon_name
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(8, 0, 8, 0)
    label = QLabel(name)
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setValue(value)
    spin.valueChanged.connect(function)
    layout.addWidget(label)
    layout.addWidget(spin)
    action = QWidgetAction(menu)
    action.setDefaultWidget(widget)
    menu.addAction(action)
    return spin


# load SCP menu
# noinspection PyTypeChecker
def load_menu():
    menu_bar = cfg.iface.mainWindow().menuBar()
    cfg.main_menu = QMenu(cfg.iface.mainWindow())
    cfg.main_menu.setObjectName('semiautomaticclassificationplugin')
    cfg.main_menu.setTitle(
        QApplication.translate('semiautomaticclassificationplugin', 'SCP')
        )
    menu_bar.insertMenu(
        cfg.iface.firstRightStandardMenu().menuAction(), cfg.main_menu
    )
    function_dictionaries(cfg.simplified)
    for b in cfg.first_functions:
        add_menu_item(
            cfg.main_menu, cfg.first_functions[b], cfg.first_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    # Basic tools
    basic_tools_menu = cfg.main_menu.addMenu(
        QIcon(
            f'{cfg.plugin_dir}/ui/icons/'
            f'semiautomaticclassificationplugin_roi_tool.svg'
        ), QApplication.translate(
            'semiautomaticclassificationplugin', 'Basic tools'
            )
    )
    # Preprocessing
    preprocessing_menu = cfg.main_menu.addMenu(
        QIcon(
            f'{cfg.plugin_dir}/ui/icons/'
            f'semiautomaticclassificationplugin_class_tool.svg'
        ), QApplication.translate(
            'semiautomaticclassificationplugin', 'Preprocessing'
            )
    )
    # Band processing
    band_processing_menu = cfg.main_menu.addMenu(
        QIcon(
            f'{cfg.plugin_dir}/ui/icons/'
            f'semiautomaticclassificationplugin_band_processing.svg'
        ), QApplication.translate(
            'semiautomaticclassificationplugin', 'Band processing'
            )
    )
    # Postprocessing
    postprocessing_menu = cfg.main_menu.addMenu(
        QIcon(
            f'{cfg.plugin_dir}/ui/icons/'
            f'semiautomaticclassificationplugin_post_process.svg'
        ), QApplication.translate(
            'semiautomaticclassificationplugin', 'Postprocessing'
            )
    )
    for b in cfg.calc_functions:
        add_menu_item(
            cfg.main_menu, cfg.calc_functions[b], cfg.calc_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    if not cfg.simplified:
        # Spectral plot
        add_menu_item(
            cfg.main_menu, spectral_plot_tab,
            'semiautomaticclassificationplugin_sign_tool.svg',
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Spectral plot'
                )
        )
        # Scatter plot
        add_menu_item(
            cfg.main_menu, scatter_plot_tab,
            'semiautomaticclassificationplugin_scatter_tool.svg',
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Scatter plot'
                )
        )
    # Settings
    settings_menu = cfg.main_menu.addMenu(
        QIcon(
            f'{cfg.plugin_dir}/ui/icons/'
            f'semiautomaticclassificationplugin_settings_tool.svg'
        ),
        QApplication.translate('semiautomaticclassificationplugin', 'Settings')
    )
    for b in cfg.other_functions:
        add_menu_item(
            cfg.main_menu, cfg.other_functions[b], cfg.other_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.basic_tools_functions:
        add_menu_item(
            basic_tools_menu, cfg.basic_tools_functions[b],
            cfg.basic_tools_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.preprocessing_functions:
        add_menu_item(
            preprocessing_menu, cfg.preprocessing_functions[b],
            cfg.preprocessing_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.band_processing_functions:
        add_menu_item(
            band_processing_menu, cfg.band_processing_functions[b],
            cfg.band_processing_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.postprocessing_functions:
        add_menu_item(
            postprocessing_menu, cfg.postprocessing_functions[b],
            cfg.postprocessing_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.setting_functions:
        add_menu_item(
            settings_menu, cfg.setting_functions[b], cfg.setting_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    # simplified interface
    if cfg.simplified:
        cfg.ram_menu_spin = add_menu_spinbox(
            settings_menu, ram_setting_change, None,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Available RAM (MB)'
                ), 128, 196608, cfg.qgis_registry[cfg.reg_ram_value]
        )
        cfg.cpu_menu_spin = add_menu_spinbox(
            settings_menu, threads_setting_change, None,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'CPU threads'
            ), 1, 1000, cfg.qgis_registry[cfg.reg_threads_value]
        )
    add_menu_checkbox(
        settings_menu, simplified_interface, None,
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Simplified interface'
            ), cfg.simplified
    )
    # Show plugin
    add_menu_item(
        cfg.main_menu, show_plugin,
        'semiautomaticclassificationplugin_docks.svg',
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Show plugin'
            )
    )


# load SCP main interface menu
# noinspection PyTypeChecker
def load_main_menu():
    tree = cfg.dialog.ui.menu_treeWidget
    function_dictionaries(cfg.simplified)
    for b in cfg.first_functions:
        add_tree_item(
            tree, cfg.first_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    # Basic tools
    basic_tools_menu = add_tree_item(
        tree,
        QIcon(f'{cfg.plugin_dir}/ui/icons/'
              f'semiautomaticclassificationplugin_roi_tool.svg'
              ), QApplication.translate('semiautomaticclassificationplugin',
                                        'Basic tools')
    )
    # Preprocessing
    preprocessing_menu = add_tree_item(
        tree, QIcon(
            f'{cfg.plugin_dir}/ui/icons/'
            f'semiautomaticclassificationplugin_class_tool.svg'
        ), QApplication.translate(
            'semiautomaticclassificationplugin', 'Preprocessing')
    )
    # Band processing
    band_processing_menu = add_tree_item(
        tree, QIcon(
            f'{cfg.plugin_dir}/ui/icons/'
            f'semiautomaticclassificationplugin_band_processing.svg'
        ), QApplication.translate(
            'semiautomaticclassificationplugin', 'Band processing')
    )
    # Postprocessing
    postprocessing_menu = add_tree_item(
        tree, QIcon(
            f'{cfg.plugin_dir}/ui/icons/'
            f'semiautomaticclassificationplugin_post_process.svg'
        ), QApplication.translate(
            'semiautomaticclassificationplugin', 'Postprocessing')
    )
    for b in cfg.calc_functions:
        add_tree_item(
            tree, cfg.calc_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    # Settings
    settings_menu = add_tree_item(
        tree, QIcon(
            f'{cfg.plugin_dir}/ui/icons/'
            f'semiautomaticclassificationplugin_settings_tool.svg'
        ),
        QApplication.translate('semiautomaticclassificationplugin', 'Settings')
    )
    for b in cfg.other_functions:
        add_tree_item(
            tree, cfg.other_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.basic_tools_functions:
        add_tree_item(
            basic_tools_menu, cfg.basic_tools_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.preprocessing_functions:
        add_tree_item(
            preprocessing_menu, cfg.preprocessing_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.band_processing_functions:
        add_tree_item(
            band_processing_menu, cfg.band_processing_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.postprocessing_functions:
        add_tree_item(
            postprocessing_menu, cfg.postprocessing_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    for b in cfg.setting_functions:
        add_tree_item(
            settings_menu, cfg.setting_icons[b],
            QApplication.translate('semiautomaticclassificationplugin', b)
        )
    # simplified interface
    if cfg.simplified:
        cfg.ram_tree_spin = add_tree_spinbox(
            tree, settings_menu, ram_setting_change,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'Available RAM (MB)'
                ), 128, 196608, cfg.qgis_registry[cfg.reg_ram_value]
        )
        cfg.cpu_tree_spin = add_tree_spinbox(
            tree, settings_menu, threads_setting_change,
            QApplication.translate(
                'semiautomaticclassificationplugin', 'CPU threads'
                ), 1, 1000, cfg.qgis_registry[cfg.reg_threads_value]
        )
    add_tree_checkbox(
        settings_menu, None,
        QApplication.translate(
            'semiautomaticclassificationplugin', 'Simplified interface'
            ), cfg.simplified
    )
    tree.collapseAll()
    tree.itemChanged.connect(tree_item_changed)


# RAM setting
def ram_setting_change(value):
    cfg.qgis_registry[cfg.reg_ram_value] = value
    cfg.rs.set(available_ram=int(cfg.qgis_registry[cfg.reg_ram_value]))
    cfg.ram_tree_spin.blockSignals(True)
    cfg.ram_tree_spin.setValue(value)
    cfg.ram_tree_spin.blockSignals(False)
    cfg.ram_menu_spin.blockSignals(True)
    cfg.ram_menu_spin.setValue(value)
    cfg.ram_menu_spin.blockSignals(False)


# thread setting
def threads_setting_change(value):
    cfg.qgis_registry[cfg.reg_threads_value] = value
    cfg.rs.set(n_processes=int(cfg.qgis_registry[cfg.reg_threads_value]))
    cfg.cpu_tree_spin.blockSignals(True)
    cfg.cpu_tree_spin.setValue(value)
    cfg.cpu_tree_spin.blockSignals(False)
    cfg.cpu_menu_spin.blockSignals(True)
    cfg.cpu_menu_spin.setValue(value)
    cfg.cpu_menu_spin.blockSignals(False)


# set SCP dock tabs buttons
def set_dock_tabs():
    source = f'{cfg.plugin_dir}/ui/icons/'
    icons = [
        '%s/semiautomaticclassificationplugin_bandset_tool' % source,
        '%s/semiautomaticclassificationplugin_download_arrow' % source,
        '%s/semiautomaticclassificationplugin_roi_tool' % source,
        '%s/semiautomaticclassificationplugin_class_tool' % source,
        '%s/semiautomaticclassificationplugin_band_processing' % source,
        '%s/semiautomaticclassificationplugin_post_process' % source,
        '%s/semiautomaticclassificationplugin_bandcalc_tool' % source]
    for i in range(3, 10):
        label = QLabel()
        label.setStyleSheet(_fromUtf8('color : black'))
        label.setObjectName(_fromUtf8('label'))
        label.setPixmap(
            QPixmap(icons[i - 3]).scaled(24, 24,
                                         Qt.AspectRatioMode.KeepAspectRatio)
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cfg.dock_class_dlg.ui.tabWidget_dock.tabBar().setTabButton(
            i, QTabBar.ButtonPosition.LeftSide, label
        )


# dock tab index
def dock_tab_changed(name):
    if cfg.simplified:
        tree = cfg.dialog.ui.menu_treeWidget
        root = tree.invisibleRootItem()
        tree.blockSignals(True)
        index = 0
        # unselect all
        for i in range(0, root.childCount()):
            child = root.child(i)
            child.setHidden(False)
            if child.text(0) == name:
                child.setSelected(True)
                child.setExpanded(True)
                index = i
            else:
                child.setSelected(False)
            for x in range(0, child.childCount()):
                child.child(x).setHidden(False)
                if child.child(x).text(0) == name:
                    child.child(x).setSelected(True)
                    child.setExpanded(True)
                else:
                    child.child(x).setSelected(False)
        cfg.dialog.close()
        cfg.dialog.show()
        cfg.dialog.ui.SCP_tabs.setCurrentIndex(index + 1)
        tree.blockSignals(False)
        cfg.dock_class_dlg.ui.tabWidget_dock.blockSignals(True)
        cfg.dock_class_dlg.ui.tabWidget_dock.setCurrentIndex(
            cfg.settings_tab_index
        )
        cfg.dock_class_dlg.ui.tabWidget_dock.blockSignals(False)
    else:
        if name > 2:
            cfg.dialog.ui.SCP_tabs.setCurrentIndex(name - 3)
            tree = cfg.dialog.ui.menu_treeWidget
            root = tree.invisibleRootItem()
            tree.blockSignals(True)
            # unselect all
            for i in range(0, root.childCount()):
                child = root.child(i)
                child.setHidden(False)
                child.setSelected(False)
                for x in range(0, child.childCount()):
                    child.child(x).setHidden(False)
                    child.child(x).setSelected(False)
            child = root.child(name - 3)
            child.setSelected(True)
            child.setExpanded(True)
            tree.blockSignals(False)
            cfg.dock_class_dlg.ui.tabWidget_dock.blockSignals(True)
            cfg.dock_class_dlg.ui.tabWidget_dock.setCurrentIndex(
                cfg.settings_tab_index
            )
            cfg.dock_class_dlg.ui.tabWidget_dock.blockSignals(False)
            cfg.dialog.close()
            cfg.dialog.show()
        else:
            cfg.settings_tab_index = (
                cfg.dock_class_dlg.ui.tabWidget_dock.currentIndex()
            )


# menu tab
def tree_menu_tab():
    current_tab = cfg.current_tab[0:-3].lower().replace('_', '')
    tree = cfg.dialog.ui.menu_treeWidget
    root = tree.invisibleRootItem()
    tree.blockSignals(True)
    # unselect all
    for i in range(0, root.childCount()):
        child = root.child(i)
        child.setHidden(False)

        if child.text(0).lower().replace(' ', '').replace(
                '-', ''
        ) == current_tab:
            child.setSelected(True)
            child.setExpanded(True)
        else:
            child.setSelected(False)
        for x in range(0, child.childCount()):
            child.child(x).setHidden(False)
            if child.child(x).text(0).lower().replace(' ', '').replace(
                    '-', ''
            ) == current_tab:
                child.child(x).setSelected(True)
                child.setExpanded(True)
            else:
                child.child(x).setSelected(False)
    tree.blockSignals(False)
    cfg.dialog.ui.main_tabWidget.setCurrentIndex(0)
    cfg.dialog.show()


# SCP tab index
def scp_tab_changed(_index):
    cfg.dialog.close()
    cfg.dialog.show()


# main tab index
def main_tab_changed(index):
    if index == 1 and cfg.current_tab != 'about_tab':
        cfg.dialog.ui.help_textBrowser.clear()
        cfg.dialog.ui.help_textBrowser.setPlainText('Loading ...')
        # for user manual
        cfg.rs.files_directories.create_directory(
            '%s/_images/' % cfg.rs.configurations.temp.dir)
        base_url = (
                'https://semiautomaticclassificationmanual.readthedocs.io/en/'
                'latest/%s.html' % cfg.current_tab
        )
        cfg.logger.log.debug('help tab: %s' % base_url)
        QApplication.instance().processEvents()
        if not cfg.utils.check_file(
                '%s/%s.html' %
                (cfg.rs.configurations.temp.dir, cfg.current_tab)
        ):
            response = get(base_url, timeout=60)
            with open(
                    '%s/%s.html'
                    % (cfg.rs.configurations.temp.dir, cfg.current_tab), 'wb'
            ) as file:
                file.write(response.content)
        with open('%s/%s.html'
                  % (cfg.rs.configurations.temp.dir, cfg.current_tab),
                  'r') as h:
            html = h.read()
        images = findall('src="_images/(.+?)"', str(html))
        for image in images:
            if not cfg.utils.check_file(
                    cfg.rs.configurations.temp.dir + '/_images/' + image):
                try:
                    response = get(
                        'https://semiautomaticclassificationmanual.'
                        'readthedocs.io/en/latest/_images/%s' % image,
                        timeout=60
                    )
                    with open(
                            '%s/_images/%s'
                            % (cfg.rs.configurations.temp.dir, image), 'wb'
                    ) as file:
                        file.write(response.content)
                except Exception as err:
                    str(err)
        if len(html) > 0:
            cfg.dialog.ui.help_textBrowser.clear()
            cfg.dialog.ui.help_textBrowser.setHtml(html)


# top tree
def top_tree():
    pass


def moved_splitter(_index, _pos):
    cfg.qgis_registry[cfg.reg_splitter_sizes] = str(
        cfg.dialog.ui.splitter.sizes()
    )


# filter tree
def filter_tree():
    try:
        text = cfg.dialog.ui.f_filter_lineEdit.text()
        tree = cfg.dialog.ui.menu_treeWidget
        root = tree.invisibleRootItem()
        tree.blockSignals(True)
        if len(text) > 0:
            tree.expandAll()
            tree.findItems(text, cfg.util_qt.get_match_contains())
            for i in range(0, root.childCount()):
                child = root.child(i)
                child.setHidden(False)
                for x in range(0, child.childCount()):
                    if text.lower() in child.child(x).text(0).lower():
                        child.child(x).setHidden(False)
                    else:
                        child.child(x).setHidden(True)
        else:
            tree.collapseAll()
            for i in range(0, root.childCount()):
                child = root.child(i)
                child.setHidden(False)
                for x in range(0, child.childCount()):
                    if text in child.child(x).text(0):
                        child.child(x).setHidden(False)
        tree.blockSignals(False)
    except Exception as err:
        str(err)


# welcome text
def welcome_text(input_url, input_url2=None):
    html_text_f = open('%s/ui/welcome.html' % cfg.plugin_dir, 'r')
    html_text = html_text_f.read()
    cfg.dock_class_dlg.ui.main_textBrowser.clear()
    cfg.dock_class_dlg.ui.main_textBrowser.setHtml(html_text)
    html_text_f.close()
    if cfg.qgis_registry[cfg.reg_download_news] == 2:
        cfg.utils.download_html(input_url, input_url2)


""" Classification preview """


# set preview transparency
def change_transparency(value):
    try:
        if cfg.classification_preview is not None:
            cfg.map_canvas.setRenderFlag(False)
            cfg.classification_preview.renderer().setOpacity(
                float(1) - float(value) / 100
            )
            if hasattr(cfg.classification_preview, 'setCacheImage'):
                cfg.classification_preview.setCacheImage(None)
            cfg.classification_preview.triggerRepaint()
            cfg.map_canvas.setRenderFlag(True)
            cfg.map_canvas.refresh()
    except Exception as err:
        str(err)


# show hide preview radio button
def show_hide_preview():
    try:
        if cfg.classification_preview is not None:
            if cfg.show_preview_radioButton2.isChecked():
                cfg.util_qgis.set_layer_visible(
                    cfg.classification_preview,
                    True
                )
                cfg.util_qgis.move_layer_to_top(cfg.classification_preview)
            else:
                cfg.util_qgis.set_layer_visible(
                    cfg.classification_preview,
                    False
                )
    except Exception as err:
        str(err)


# set preview size
def preview_size():
    cfg.project_registry[cfg.reg_preview_size] = int(
        cfg.preview_size_spinBox.value()
    )


# redo preview
def redo_preview():
    if cfg.preview_point is not None:
        cfg.classification.create_preview(cfg.preview_point)


# zoom to ROI
def zoom_to_temp_roi():
    if cfg.temporary_roi is not None:
        cfg.util_qgis.set_map_extent_from_layer(cfg.temporary_roi)


# zoom to preview
def zoom_to_preview():
    if cfg.classification_preview is not None:
        cfg.util_qgis.set_map_extent_from_layer(cfg.classification_preview)

        cfg.classification_preview.triggerRepaint()
        cfg.map_canvas.refresh()


# show hide input image
def show_hide_input_mage():
    i = None
    try:
        i = cfg.virtual_bandset_dict[cfg.project_registry[
            cfg.reg_active_bandset_number]]
    except Exception as err:
        str(err)
    try:
        if i is not None:
            if cfg.inputImageRadio.isChecked():
                cfg.util_qgis.set_layer_visible(i, True)
                cfg.util_qgis.move_layer_to_top(i)
            else:
                cfg.util_qgis.set_layer_visible(i, False)
    except Exception as err:
        str(err)


""" tab selection functions """


# select band set tab
def bandset_tab():
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(0)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select tab 1
def select_download_products_tab():
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(1)
    dock_tab_changed('Download products')


# select preprocessing tab
def download_products_tab():
    select_download_products_tab()
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select tab 2 from Main Interface
def select_tab_2_main_interface(second_tab=None):
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(2)
    if second_tab is not None:
        cfg.dialog.ui.tabWidget_5.setCurrentIndex(second_tab)


# select basic tools tab
def basic_tools_tab():
    select_tab_2_main_interface()
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# RGB composite tab
def rgb_composite_tab():
    select_tab_2_main_interface(0)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select multiple roi tab
def multiple_roi_creation_tab():
    select_tab_2_main_interface(1)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# import library signatures tab
def import_signatures_tab():
    select_tab_2_main_interface(2)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# export library signatures tab
def export_signatures_tab():
    select_tab_2_main_interface(3)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# signature threshold tab
def signature_threshold_tab():
    select_tab_2_main_interface(4)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select tab 3 from Main Interface
def select_tab_3_main_interface(second_tab=None):
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(3)
    if second_tab is not None:
        cfg.dialog.ui.tabWidget_preprocessing.setCurrentIndex(second_tab)


# select preprocessing tab
def pre_processing_tab():
    select_tab_3_main_interface()
    dock_tab_changed('Preprocessing')


# select Landsat tab
def image_conversion_tab():
    select_tab_3_main_interface(0)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# Vector to raster tab
def vector_to_raster_tab():
    select_tab_3_main_interface(1)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Clip raster bands tab
def clip_raster_bands_tab():
    select_tab_3_main_interface(2)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Reproject raster bands tab
def reproject_bands_tab():
    select_tab_3_main_interface(3)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Split raster bands tab
def split_bands_tab():
    select_tab_3_main_interface(4)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Stack raster bands tab
def stack_bands_tab():
    select_tab_3_main_interface(5)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# Mosaic tab
def mosaic_bandsets_tab():
    select_tab_3_main_interface(6)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# cloud masking tab
def masking_bands_tab():
    select_tab_3_main_interface(7)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select tab 4 from Main Interface
def select_tab_4_main_interface(second_tab=None):
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(4)
    if second_tab is not None:
        cfg.dialog.ui.tabWidget_4.setCurrentIndex(second_tab)


# select band processing tab
def band_processing_tab():
    select_tab_4_main_interface()
    dock_tab_changed('Band processing')


# select Band combination tab
def combination_tab():
    select_tab_4_main_interface(0)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select band dilation tab
def dilation_tab():
    select_tab_4_main_interface(1)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# band erosion tab
def erosion_tab():
    select_tab_4_main_interface(2)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# band sieve tab
def sieve_tab():
    select_tab_4_main_interface(3)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# PCA tab
def pca_tab():
    select_tab_4_main_interface(4)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select classification tab
def classification_tab():
    select_tab_4_main_interface(5)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select neighbor pixels tab
def band_neighbor_tab():
    select_tab_4_main_interface(6)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select clustering tab
def band_clustering_tab():
    select_tab_4_main_interface(7)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# spectral distance tab
def spectral_distance_tab():
    select_tab_4_main_interface(8)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select tab 5 from Main Interface
def select_tab_5_main_interface(second_tab=None):
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(5)
    if second_tab is not None:
        cfg.dialog.ui.tabWidget_2.setCurrentIndex(second_tab)


# select postprocessing tab
def post_processing_tab():
    select_tab_5_main_interface()
    dock_tab_changed('Postprocessing')


# select Accuracy tab
def accuracy_tab():
    select_tab_5_main_interface(0)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Classification report tab
def classification_report_tab():
    select_tab_5_main_interface(1)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Cross classification tab
def cross_classification_tab():
    select_tab_5_main_interface(2)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Classification to vector tab
def classification_to_vector_tab():
    select_tab_5_main_interface(3)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Reclassification tab
def reclassification_tab():
    select_tab_5_main_interface(4)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Edit raster tab
def edit_raster_tab():
    select_tab_5_main_interface(5)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select raster zonal stats tab
def raster_zonal_stats_tab():
    select_tab_5_main_interface(6)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select Band calc tab
def band_calc_tab():
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(6)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select tab 7 from Main Interface
def select_tab_7_main_interface(second_tab=None):
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(7)
    if second_tab is not None:
        cfg.dialog.ui.toolBox.setCurrentIndex(second_tab)


# select batch tab
def script_tab():
    select_tab_7_main_interface()
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select tab 8 from Main Interface
def select_tab_8_main_interface(second_tab=None):
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(8)
    if second_tab is not None:
        cfg.dialog.ui.settings_tabWidget.setCurrentIndex(second_tab)


# select settings tab
def settings_tab():
    select_tab_8_main_interface()


# select settings Processing tab
def processing_settings_tab():
    select_tab_8_main_interface(0)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select settings interface tab
def interface_tab():
    select_tab_8_main_interface(1)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select settings debug tab
def debug_tab():
    select_tab_8_main_interface(2)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# select about tab
def about_tab():
    cfg.dialog.ui.SCP_tabs.setCurrentIndex(9)
    cfg.current_tab = str(stack()[0][3])
    tree_menu_tab()


# spectral signature plot tab
def spectral_plot_tab():
    cfg.spectral_plot_dlg.close()
    cfg.spectral_plot_dlg.show()


# select tab in signature plot tab
def select_spectral_plot_settings_tab(second_tab=None):
    if second_tab is not None:
        cfg.spectral_plot_dlg.ui.tabWidget.setCurrentIndex(second_tab)


# scatter plot tab
def scatter_plot_tab():
    cfg.scatter_plot_dlg.close()
    cfg.scatter_plot_dlg.show()


# rgb changed
def rgb_combo_changed():
    cfg.utils.set_rgb_color_composite(cfg.rgb_combo.currentText())


# add classification algorithm list to combo
def add_algorithm_to_combo(algorithm_list):
    for i in algorithm_list:
        cfg.dock_class_simpl_dlg.ui.alg_combo.addItem(i)


def activate_layer_1():
    layer_name = cfg.layer_on_off_1.text()
    try:
        cfg.util_qgis.activate_layer(layer_name)
    except Exception as err:
        str(err)
        cfg.mx.msg_err_9(layer_name)


def key_sequence_z():
    cfg.on_off_button_1.setShortcut(QKeySequence('Z'))


def activate_layer_2():
    layer_name = cfg.layer_on_off_2.text()
    try:
        cfg.util_qgis.activate_layer(layer_name)
    except Exception as err:
        str(err)
        cfg.mx.msg_err_9(layer_name)


def key_sequence_x():
    cfg.on_off_button_2.setShortcut(QKeySequence('X'))


def activate_layer_3():
    layer_name = cfg.layer_on_off_3.text()
    try:
        cfg.util_qgis.activate_layer(layer_name)
    except Exception as err:
        str(err)
        cfg.mx.msg_err_9(layer_name)


def key_sequence_c():
    cfg.on_off_button_3.setShortcut(QKeySequence('C'))
