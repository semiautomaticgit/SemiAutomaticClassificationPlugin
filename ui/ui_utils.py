# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
 providing a tool for the region growing of image pixels, creating polygon shapefiles intended for
 the collection of training areas (ROIs), and rapidly performing the classification process (or a preview).
							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012 by Luca Congedo
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

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class Ui_Utils:

	def __init__(self):
		pass
		
### Add a progress bar and a cancel button
	def addProgressBar(self, message = ""):
		# remove if bar already there
		try:
			self.removeProgressBar()
			self.createProgressBar(message)
		except:
			self.createProgressBar()
		
	# Create a progress bar and a cancel button
	def createProgressBar(self, message = ""):
		self.widgetBar = cfg.iface.messageBar().createMessage(QApplication.translate("semiautomaticclassificationplugin","Executing"), message)
		cfg.progressBar = QProgressBar()
		cfg.progressBar.setMinimum(0)
		cfg.progressBar.setMaximum(100)
		cfg.progressBar.setProperty("value", 0)
		cfg.progressBar.setTextVisible(True)
		cfg.progressBar.setObjectName("progressBar")
		self.cancelButton = QPushButton()
		self.cancelButton.setEnabled(True)
		self.cancelButton.setObjectName("cancelButton")
		self.cancelButton.setText("Cancel")       
		self.widgetBar.layout().addWidget(cfg.progressBar)
		self.widgetBar.layout().addWidget(self.cancelButton)
		self.cancelButton.clicked.connect(self.cancelAction)
		# set action to yes
		cfg.actionCheck = "Yes"
		self.setInterface(False)
		cfg.iface.messageBar().pushWidget(self.widgetBar, cfg.iface.messageBar().INFO)
		
	# cancel action
	def cancelAction(self):
		cfg.actionCheck = "No"
		self.removeProgressBar()
		self.setInterface(True)
			
	# update bar value
	def updateBar(self, value, message = ""):
		if cfg.actionCheck == "Yes":
			self.addProgressBar(message)
			cfg.progressBar.setValue(value)
			#qApp.processEvents()
			
	# remove progress bar and cancel button
	def removeProgressBar(self):
		try:
			cfg.progressBar.close()
			self.cancelButton.close()
			cfg.iface.messageBar().popWidget(self.widgetBar)
			cfg.actionCheck = "No"
			self.setInterface(True)
		except:
			cfg.actionCheck = "No"
			self.setInterface(True)
		
	# enable disable the interface to avoid errors
	def setInterface(self, state):
		# ROI dock
		cfg.dockdlg.setEnabled(state)
		# classification dock
		cfg.dockclassdlg.setEnabled(state)
		# main interface
		cfg.dlg.setEnabled(state)
		# toolbar
		cfg.main_toolButton.setEnabled(state)
		cfg.bandset_toolButton.setEnabled(state)
		cfg.spectral_plot_toolButton.setEnabled(state)
		cfg.ROItools_toolButton.setEnabled(state)
		cfg.preprocessing_toolButton.setEnabled(state)
		cfg.postprocessing_toolButton.setEnabled(state)
		cfg.settings_toolButton.setEnabled(state)
		cfg.raster_name_combo.setEnabled(state)
		cfg.toolButton_reload.setEnabled(state)