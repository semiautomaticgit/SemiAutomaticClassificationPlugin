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


cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

class Ui_Utils:

	def __init__(self):
		pass
		
### Add a progress bar and a cancel button
	def addProgressBar(self, message = "", action = "Executing"):
		# remove if bar already there
		try:
			self.removeProgressBar()
			self.createProgressBar(message, action)
		except:
			self.createProgressBar()
		
	# Create a progress bar and a cancel button
	def createProgressBar(self, message = "", action = "Executing"):
		self.widgetBar = cfg.iface.messageBar().createMessage(action, message)
		cfg.progressBar = cfg.QtWidgetsSCP.QProgressBar()
		cfg.progressBar.setMinimum(0)
		cfg.progressBar.setMaximum(100)
		cfg.progressBar.setProperty("value", 0)
		cfg.progressBar.setTextVisible(True)
		cfg.progressBar.setObjectName("progressBar")
		self.cancelButton = cfg.QtWidgetsSCP.QPushButton()
		self.cancelButton.setEnabled(True)
		self.cancelButton.setObjectName("cancelButton")
		self.cancelButton.setText("Cancel")       
		self.widgetBar.layout().addWidget(cfg.progressBar)
		self.widgetBar.layout().addWidget(self.cancelButton)
		self.cancelButton.clicked.connect(self.cancelAction)
		# set action to yes
		cfg.actionCheck = "Yes"
		self.setInterface(False)
		cfg.iface.messageBar().pushWidget(self.widgetBar, cfg.qgisCoreSCP.Qgis.Info)
		
	# cancel action
	def cancelAction(self):
		cfg.actionCheck = "No"
		self.removeProgressBar()
		self.setInterface(True)
			
	# update bar value
	def updateBar(self, value, message = "", action = "Executing"):
		if cfg.actionCheck == "Yes":
			self.addProgressBar(message, action)
			cfg.progressBar.setValue(value)
			
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
		# classification dock
		cfg.dockclassdlg.setEnabled(state)
		# main interface
		cfg.dlg.setEnabled(state)
		# toolbar
		cfg.toolBar2.setEnabled(state)
		cfg.toolBar3.setEnabled(state)
		