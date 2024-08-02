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


from PyQt5.QtCore import (
    Qt, QFileInfo, QSettings, qVersion, QCoreApplication, QTranslator
)
from PyQt5.QtWidgets import QDialog, QDockWidget
# noinspection PyUnresolvedReferences
from qgis.core import QgsApplication

from .ui_semiautomaticclassificationplugin import (
    Ui_SemiAutomaticClassificationPlugin
)
from .ui_semiautomaticclassificationplugin_dock_class import Ui_DockClass
from .ui_semiautomaticclassificationplugin_scatter_plot import Ui_ScatterPlot
from .ui_semiautomaticclassificationplugin_signature_plot import (
    Ui_SpectralSignaturePlot
)
from .ui_semiautomaticclassificationplugin_widget import Ui_SCP_Widget

try:
    cfg = __import__(
        str(__name__).split('.')[0] + '.core.config', fromlist=['']
    )
except Exception as error:
    str(error)


# create the dialog
class SemiAutomaticClassificationPluginDialog(QDialog):
    # noinspection PyArgumentList
    def __init__(self):
        QDialog.__init__(self)
        try:
            self.setWindowFlags(Qt.Window)
        except Exception as err:
            str(err)
            return
        # initialize plugin directory
        self.plugin_dir = QFileInfo(
            QgsApplication.qgisUserDatabaseFilePath()
        ).path() + '/python/plugins/SemiAutomaticClassificationPlugin'
        # locale name
        self.locale_name = QSettings().value('locale/userLocale')[0:2]
        # path to locale
        locale_path = ''
        if QFileInfo(self.plugin_dir).exists():
            locale_path = ('%s/i18n/semiautomaticclassificationplugin_%s.qm'
                           % (self.plugin_dir, self.locale_name))
        if QFileInfo(locale_path).exists():
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        # Set up the user interface from Designer.
        self.ui = Ui_SemiAutomaticClassificationPlugin()
        self.ui.setupUi(self)

    def shape_clip_combo(self, shape):
        self.ui.shapefile_comboBox.addItem(shape)

    def vector_to_raster_combo(self, vector):
        self.ui.vector_name_combo.addItem(vector)

    def classification_layer_combo(self, layer):
        self.ui.classification_name_combo.addItem(layer)

    def classification_layer_combo_2(self, layer):
        self.ui.classification_name_combo_2.addItem(layer)

    def classification_report_combo(self, layer):
        self.ui.classification_report_name_combo.addItem(layer)

    def classification_to_vector_combo(self, layer):
        self.ui.classification_vector_name_combo.addItem(layer)

    def reclassification_combo(self, layer):
        self.ui.reclassification_name_combo.addItem(layer)

    def reference_layer_combo(self, shape):
        self.ui.reference_name_combo.addItem(shape)

    def reference_layer_combo_2(self, shape):
        self.ui.reference_name_combo_2.addItem(shape)

    def raster_layer_combo(self, layer):
        self.ui.raster_name_combo.addItem(layer)

    def raster_extent_combo(self, layer):
        self.ui.raster_extent_combo.addItem(layer)

    def raster_extent_combo_2(self, layer):
        self.ui.raster_extent_combo_2.addItem(layer)

    def cloud_mask_raster_combo(self, layer):
        self.ui.classification_name_combo_4.addItem(layer)

    def reference_raster_combo(self, layer):
        self.ui.reference_raster_name_combo.addItem(layer)

    def project_raster_combo(self, layer):
        self.ui.raster_align_comboBox.addItem(layer)

    def class_field_combo(self, field):
        self.ui.class_field_comboBox.addItem(field)

    def class_field_combo_2(self, field):
        self.ui.class_field_comboBox_2.addItem(field)

    def class_field_combo_3(self, field):
        self.ui.class_field_comboBox_3.addItem(field)

    def reference_field_combo(self, field):
        self.ui.field_comboBox.addItem(field)

    def statistic_name_combo2(self, field):
        self.ui.statistic_name_combobox_2.addItem(field)

    def vector_edit_raster_combo(self, vector):
        self.ui.vector_name_combo_2.addItem(vector)

    def edit_raster_combo(self, layer):
        self.ui.edit_raster_name_combo.addItem(layer)

    def zonal_stat_raster_combo(self, layer):
        self.ui.classification_name_combo_5.addItem(layer)

    def vector_zonal_raster_combo(self, vector):
        self.ui.reference_name_combo_3.addItem(vector)

    def zonal_reference_field_combo(self, field):
        self.ui.class_field_comboBox_4.addItem(field)

    def reference_field_combo2(self, field):
        self.ui.field_comboBox_2.addItem(field)


# create the dialog
class DockClassDialog(QDockWidget):
    # noinspection PyArgumentList,PyUnusedLocal
    def __init__(self, parent, iface):
        QDockWidget.__init__(self)
        # initialize plugin directory
        try:
            self.plugin_dir = QFileInfo(
                QgsApplication.qgisUserDatabaseFilePath()
            ).path() + '/python/plugins/SemiAutomaticClassificationPlugin'
        except Exception as err:
            str(err)
            return
        # locale name
        self.locale_name = QSettings().value('locale/userLocale')[0:2]
        # path to locale
        locale_path = ''
        if QFileInfo(self.plugin_dir).exists():
            locale_path = ('%s/i18n/semiautomaticclassificationplugin_%s.qm'
                           % (self.plugin_dir, self.locale_name))
        if QFileInfo(locale_path).exists():
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.ui = Ui_DockClass()
        self.ui.setupUi(self)


# create the dialog
# noinspection PyMissingConstructor
class ScatterPlotDialog(QDialog):
    # noinspection PyArgumentList
    def __init__(self):
        QDockWidget.__init__(self)
        try:
            self.setWindowFlags(Qt.Window)
        except Exception as err:
            str(err)
            return
        # initialize plugin directory
        self.plugin_dir = QFileInfo(
            QgsApplication.qgisUserDatabaseFilePath()
        ).path() + '/python/plugins/SemiAutomaticClassificationPlugin'
        # locale name
        self.locale_name = QSettings().value('locale/userLocale')[0:2]
        # path to locale
        locale_path = ''
        if QFileInfo(self.plugin_dir).exists():
            locale_path = ('%s/i18n/semiautomaticclassificationplugin_%s.qm'
                           % (self.plugin_dir, self.locale_name))
        if QFileInfo(locale_path).exists():
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.ui = Ui_ScatterPlot()
        self.ui.setupUi(self)


# noinspection PyMissingConstructor
class SpectralSignatureDialog(QDialog):
    # noinspection PyArgumentList
    def __init__(self):
        QDockWidget.__init__(self)
        self.setWindowFlags(Qt.Window)
        # initialize plugin directory
        self.plugin_dir = QFileInfo(
            QgsApplication.qgisUserDatabaseFilePath()
        ).path() + '/python/plugins/SemiAutomaticClassificationPlugin'
        # locale name
        self.locale_name = QSettings().value('locale/userLocale')[0:2]
        # path to locale
        locale_path = ''
        if QFileInfo(self.plugin_dir).exists():
            locale_path = ('%s/i18n/semiautomaticclassificationplugin_%s.qm'
                           % (self.plugin_dir, self.locale_name))
        if QFileInfo(locale_path).exists():
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.ui = Ui_SpectralSignaturePlot()
        self.ui.setupUi(self)


# noinspection PyMissingConstructor
class WidgetDialog(QDialog):
    def __init__(self):
        QDockWidget.__init__(self)
        try:
            self.setWindowFlags(Qt.Window)
        except Exception as err:
            str(err)
        self.ui = Ui_SCP_Widget()
        self.ui.setupUi(self)
