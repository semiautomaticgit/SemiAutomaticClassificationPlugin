# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2018 by Luca Congedo
		email				: ing.congedoluca@gmail.com
**************************************************************************************************************************/
 
/**************************************************************************************************************************
 *
 * This file is part of Semi-Automatic Classification Plugin
 * 
 * Semi-Automatic Classification Plugin is free software: you can redistribute it and/or modify it under 
 * the terms of the GNU General Public License as published by the Free Software Foundation, 
 * version 3 of the License.
 * 
 * Semi-Automatic Classification Plugin is distributed in the hope that it will be useful, 
 * but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
 * FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with 
 * Semi-Automatic Classification Plugin. If not, see <http://www.gnu.org/licenses/>. 
 * 
**************************************************************************************************************************/

"""

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from .ui_semiautomaticclassificationplugin import Ui_SemiAutomaticClassificationPlugin
from .ui_semiautomaticclassificationplugin_dock_class import Ui_DockClass
from .ui_semiautomaticclassificationplugin_scatter_plot import Ui_ScatterPlot
from .ui_semiautomaticclassificationplugin_welcome import Ui_SCP_Welcome
from .ui_semiautomaticclassificationplugin_signature_plot import Ui_SpectralSignaturePlot
try:
	cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])
except:
	pass

# create the dialog
class SemiAutomaticClassificationPluginDialog(QtWidgets.QDialog):
	def __init__(self):
		QtWidgets.QDialog.__init__(self)
		try:
			self.setWindowFlags(cfg.QtSCP.Window)
		except:
			return
		# initialize plugin directory
		self.plgnDir = cfg.QFileInfoSCP(cfg.qgisCoreSCP.QgsApplication.qgisUserDatabaseFilePath()).path() + "/python/plugins/SemiAutomaticClassificationPlugin"
		# locale name
		self.lclNm = cfg.QSettingsSCP().value("locale/userLocale")[0:2] 
		# path to locale
		lclPth = "" 
		if cfg.QFileInfoSCP(self.plgnDir).exists(): 
			lclPth = self.plgnDir + "/i18n/semiautomaticclassificationplugin_" + self.lclNm + ".qm" 
		if cfg.QFileInfoSCP(lclPth).exists(): 
			self.trnsltr = cfg.QtCoreSCP.QTranslator() 
			self.trnsltr.load(lclPth) 
			if cfg.QtCoreSCP.qVersion() > '4.3.3': 
				cfg.QtCoreSCP.QCoreApplication.installTranslator(self.trnsltr)
		# Set up the user interface from Designer.
		self.ui = Ui_SemiAutomaticClassificationPlugin()
		self.ui.setupUi(self)
		
	def shape_clip_combo(self, shape):
		self.ui.shapefile_comboBox.addItem(shape)
		
	def vector_to_raster_combo(self, vector):
		self.ui.vector_name_combo.addItem(vector)
				
	def vector_edit_raster_combo(self, vector):
		self.ui.vector_name_combo_2.addItem(vector)
		
	def classification_layer_combo(self, layer):
		self.ui.classification_name_combo.addItem(layer)
		
	def classification_layer_combo_2(self, layer):
		self.ui.classification_name_combo_2.addItem(layer)
		
	def classification_layer_combo_3(self, layer):
		self.ui.classification_name_combo_3.addItem(layer)
		
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
		
	def classification_reference_layer_combo(self, layer):
		self.ui.classification_reference_name_combo.addItem(layer)
		
	def new_classification_layer_combo(self, layer):
		self.ui.new_classification_name_combo.addItem(layer)
		
	def raster_layer_combo(self, layer):
		self.ui.raster_name_combo.addItem(layer)		
		
	def raster_extent_combo(self, layer):
		self.ui.raster_extent_combo.addItem(layer)
				
	def edit_raster_combo(self, layer):
		self.ui.edit_raster_name_combo.addItem(layer)
						
	def sieve_raster_combo(self, layer):
		self.ui.sieve_raster_name_combo.addItem(layer)
								
	def erosion_raster_combo(self, layer):
		self.ui.erosion_raster_name_combo.addItem(layer)
		
	def dilation_raster_combo(self, layer):
		self.ui.dilation_raster_name_combo.addItem(layer)
			
	def cloud_mask_raster_combo(self, layer):
		self.ui.classification_name_combo_4.addItem(layer)
			
	def reference_raster_combo(self, layer):
		self.ui.reference_raster_name_combo.addItem(layer)
		
	def raster_data_type_combo(self, dataType):
		self.ui.raster_precision_combo.addItem(dataType)
		
	def class_field_combo(self, field):
		self.ui.class_field_comboBox.addItem(field)
				
	def class_field_combo_2(self, field):
		self.ui.class_field_comboBox_2.addItem(field)
				
	def class_field_combo_3(self, field):
		self.ui.class_field_comboBox_3.addItem(field)
				
	def reference_field_combo(self, field):
		self.ui.field_comboBox.addItem(field)
		
	def reference_field_combo2(self, field):
		self.ui.field_comboBox_2.addItem(field)
		
# create the dialog
class DockClassDialog(QtWidgets.QDockWidget):
	def __init__(self, parent, iface):
		QtWidgets.QDockWidget.__init__(self)
		# initialize plugin directory
		try:
			self.plgnDir = cfg.QFileInfoSCP(cfg.qgisCoreSCP.QgsApplication.qgisUserDatabaseFilePath()).path() + "/python/plugins/SemiAutomaticClassificationPlugin"
		except:
			return
		# locale name
		self.lclNm = cfg.QSettingsSCP().value("locale/userLocale")[0:2] 
		# path to locale
		lclPth = "" 
		if cfg.QFileInfoSCP(self.plgnDir).exists(): 
			lclPth = self.plgnDir + "/i18n/semiautomaticclassificationplugin_" + self.lclNm + ".qm" 
		if cfg.QFileInfoSCP(lclPth).exists(): 
			self.trnsltr = cfg.QtCoreSCP.QTranslator() 
			self.trnsltr.load(lclPth) 
			if cfg.QtCoreSCP.qVersion() > '4.3.3': 
				cfg.QtCoreSCP.QCoreApplication.installTranslator(self.trnsltr)
		self.ui = Ui_DockClass()
		self.ui.setupUi(self)

# create the dialog
class ScatterPlotDialog(QtWidgets.QDialog):
	def __init__(self):
		QtWidgets.QDockWidget.__init__(self)
		try:
			self.setWindowFlags(cfg.QtSCP.Window)
		except:
			return
		# initialize plugin directory
		self.plgnDir = cfg.QFileInfoSCP(cfg.qgisCoreSCP.QgsApplication.qgisUserDatabaseFilePath()).path() + "/python/plugins/SemiAutomaticClassificationPlugin"
		# locale name
		self.lclNm = cfg.QSettingsSCP().value("locale/userLocale")[0:2] 
		# path to locale
		lclPth = "" 
		if cfg.QFileInfoSCP(self.plgnDir).exists(): 
			lclPth = self.plgnDir + "/i18n/semiautomaticclassificationplugin_" + self.lclNm + ".qm" 
		if cfg.QFileInfoSCP(lclPth).exists(): 
			self.trnsltr = cfg.QtCoreSCP.QTranslator() 
			self.trnsltr.load(lclPth) 
			if cfg.QtCoreSCP.qVersion() > '4.3.3': 
				cfg.QtCoreSCP.QCoreApplication.installTranslator(self.trnsltr)
		self.ui = Ui_ScatterPlot()
		self.ui.setupUi(self)
		
class SpectralSignatureDialog(QtWidgets.QDialog):
	def __init__(self):
		QtWidgets.QDockWidget.__init__(self)
		self.setWindowFlags(cfg.QtSCP.Window)
		# initialize plugin directory
		self.plgnDir = cfg.QFileInfoSCP(cfg.qgisCoreSCP.QgsApplication.qgisUserDatabaseFilePath()).path() + "/python/plugins/SemiAutomaticClassificationPlugin"
		# locale name
		self.lclNm = cfg.QSettingsSCP().value("locale/userLocale")[0:2] 
		# path to locale
		lclPth = "" 
		if cfg.QFileInfoSCP(self.plgnDir).exists(): 
			lclPth = self.plgnDir + "/i18n/semiautomaticclassificationplugin_" + self.lclNm + ".qm" 
		if cfg.QFileInfoSCP(lclPth).exists(): 
			self.trnsltr = cfg.QtCoreSCP.QTranslator() 
			self.trnsltr.load(lclPth) 
			if cfg.QtCoreSCP.qVersion() > '4.3.3': 
				cfg.QtCoreSCP.QCoreApplication.installTranslator(self.trnsltr)
		self.ui = Ui_SpectralSignaturePlot()
		self.ui.setupUi(self)
		
class WelcomeDialog(QtWidgets.QDialog):
	def __init__(self):
		QtWidgets.QDockWidget.__init__(self)
		try:
			self.setWindowFlags(cfg.QtSCP.Window)
		except:
			return
		# initialize plugin directory
		self.plgnDir = cfg.QFileInfoSCP(cfg.qgisCoreSCP.QgsApplication.qgisUserDatabaseFilePath()).path() + "/python/plugins/SemiAutomaticClassificationPlugin"
		# locale name
		self.lclNm = cfg.QSettingsSCP().value("locale/userLocale")[0:2] 
		# path to locale
		lclPth = "" 
		if cfg.QFileInfoSCP(self.plgnDir).exists(): 
			lclPth = self.plgnDir + "/i18n/semiautomaticclassificationplugin_" + self.lclNm + ".qm" 
		if cfg.QFileInfoSCP(lclPth).exists(): 
			self.trnsltr = cfg.QtCoreSCP.QTranslator() 
			self.trnsltr.load(lclPth) 
			if cfg.QtCoreSCP.qVersion() > '4.3.3': 
				cfg.QtCoreSCP.QCoreApplication.installTranslator(self.trnsltr)
		self.ui = Ui_SCP_Welcome()
		self.ui.setupUi(self)