# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
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

from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class Messages:

	def __init__(self, iface):
		# reference to QGIS interface
		cfg.iface = iface
		
	# Message box information
	def msgBox(self, title, message):
		QMessageBox.information(cfg.iface.mainWindow(), title, message)
		
	# Message box error
	def msgBoxError(self, title, message):
		QMessageBox.critical(cfg.iface.mainWindow(), title, message)
		
	# Message box warning
	def msgBoxWarning(self, title, message):
		QMessageBox.warning(cfg.iface.mainWindow(), title, message)
		
	# Message bar information
	def msgBar(self, title, message):
		cfg.iface.messageBar().pushMessage(title, message, level=QgsMessageBar.INFO, duration=7)
		
	# Message bar error
	def msgBarError(self, title, message):
		cfg.iface.messageBar().pushMessage(title, message, level=QgsMessageBar.CRITICAL)
		
	# Message bar warning
	def msgBarWarning(self, title, message):
		cfg.iface.messageBar().pushMessage(title, message, level=QgsMessageBar.WARNING, duration=7)
		
	""" Messages """
	""" Information """
	def msg1(self):
		self.msgBox(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [1]", QApplication.translate("semiautomaticclassificationplugin", "Default ROI style"))

	def msg2(self):		
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [2]", QApplication.translate("semiautomaticclassificationplugin", "No log file found"))
		
	def msg3(self):
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [3]", QApplication.translate("semiautomaticclassificationplugin", "Select a shapefile; shapefile is not loaded"))
		
	def msg4(self):	
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [4]", QApplication.translate("semiautomaticclassificationplugin", "Select a raster; raster is not loaded"))

	def msg6(self):	
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [6]", QApplication.translate("semiautomaticclassificationplugin", "Select a point inside the image area"))
		
	def msg7(self):	
		self.msgBox(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [7]", QApplication.translate("semiautomaticclassificationplugin", "No file found"))
	
	def msg9(self):	
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [9]", QApplication.translate("semiautomaticclassificationplugin", "Raster projections does not match. Reproject raster to the same projection"))
		
	def msg10(self):	
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [10]", QApplication.translate("semiautomaticclassificationplugin", "Maximum Likelihood threshold must be less than 100"))
		
	def msg11(self):	
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [11]", QApplication.translate("semiautomaticclassificationplugin", "Spectral Angle Mapping threshold must be less than 90"))
		
	def msg12(self):
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [12]", QApplication.translate("semiautomaticclassificationplugin", "Select a classification output"))

	def msg14(self):
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [14]", QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))

	def msg15(self):
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [15]", QApplication.translate("semiautomaticclassificationplugin", "Restart QGIS for the new settings"))

	def msg16(self):
		self.msgBar(QApplication.translate("semiautomaticclassificationplugin", "Information") + " [16]", QApplication.translate("semiautomaticclassificationplugin", "At least 3 points are required"))
		
	""" Errors """
	def msgErr1(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [1]", QApplication.translate("semiautomaticclassificationplugin", "Classification failed."))
		
	def msgErr2(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [2]", QApplication.translate("semiautomaticclassificationplugin", "ROI creation failed. \r\nor \r\nPossible reason: one or more band of the band set are missing"))
		
	#def msgErr3(self):
		#self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [3]", QApplication.translate("semiautomaticclassificationplugin", "Signature calculation failed."))
		
	def msgErr4(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [4]", QApplication.translate("semiautomaticclassificationplugin", "Signature calculation failed. \r\nPossible reason: the raster is not loaded"))
		
	def msgErr5(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [5]", QApplication.translate("semiautomaticclassificationplugin", "Import failed. \r\nPossible reason: selected file is not a band set"))
		
	def msgErr6(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [6]", QApplication.translate("semiautomaticclassificationplugin", "Classification failed. \r\nIt appears the one or more bands of the band set are missing"))
		
	def msgErr7(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [7]", QApplication.translate("semiautomaticclassificationplugin", "ROI creation failed. \r\nPossible reason: selected rapid ROI band is not loaded"))
	
	def msgErr8(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [8]", QApplication.translate("semiautomaticclassificationplugin", "No metadata found inside the input directory (a .txt file whose name contains MTL)"))

	def msgErr9(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [9]", QApplication.translate("semiautomaticclassificationplugin", "Raster not found"))
	
	def msgErr10(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [10]", QApplication.translate("semiautomaticclassificationplugin", "Raster not found or clip failed"))
		
	def msgErr11(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [11]", QApplication.translate("semiautomaticclassificationplugin", "Shapefile or raster not found"))
		
	def msgErr12(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [12]", QApplication.translate("semiautomaticclassificationplugin", "Error deleting ROI"))
		
	def msgErr13(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [13]", QApplication.translate("semiautomaticclassificationplugin", "The Macroclass field is missing"))
		
	def msgErr15(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [15]", QApplication.translate("semiautomaticclassificationplugin", "Error saving signatures"))
			
	def msgErr16(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [16]", QApplication.translate("semiautomaticclassificationplugin", "Error opening signatures"))
		
	def msgErr17(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [17]", QApplication.translate("semiautomaticclassificationplugin", "Error opening spectral library"))
					
	def msgErr18(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [18]", QApplication.translate("semiautomaticclassificationplugin", "Error saving spectral library"))
					
	def msgErr19(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [19]", QApplication.translate("semiautomaticclassificationplugin", "Import failed"))

	def msgErr20(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [20]", QApplication.translate("semiautomaticclassificationplugin", "ROI creation failed"))
					
	def msgErr21(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [21]", QApplication.translate("semiautomaticclassificationplugin", "Internet connection failed"))
		
	def msgErr22(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [22]", QApplication.translate("semiautomaticclassificationplugin", "Exporting Log file failed"))

	def msgErr23(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [23]", QApplication.translate("semiautomaticclassificationplugin", "Saving algorithm files failed"))

	def msgErr23(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [23]", QApplication.translate("semiautomaticclassificationplugin", "Unable to get ROI attributes; check training shapefiles field names"))

	def msgErr24(self, Macro_ID, Class_ID):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [24]", QApplication.translate("semiautomaticclassificationplugin", "The following signature does not match the band set. Macro: " + str(Macro_ID) + " ID: " + str(Class_ID)))
			
	def msgErr25(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [25]", QApplication.translate("semiautomaticclassificationplugin", "Error reading raster. Possibly the raster path contains unicode characters"))
			
	def msgErr26(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [26]", QApplication.translate("semiautomaticclassificationplugin", "The version of Numpy is outdated. Please install QGIS using OSGEO4W for an updated version of Numpy"))

	def msgErr27(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [27]", QApplication.translate("semiautomaticclassificationplugin", "Unable to perform operation. Possibly OGR is missinig drivers. Please repeat QGIS installation."))
					
	def msgErr28(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [28]", QApplication.translate("semiautomaticclassificationplugin", "Memory error. Please, set a lower value of RAM in the tab Settings."))
					
	def msgErr29(self):
		self.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error") + " [29]", QApplication.translate("semiautomaticclassificationplugin", "Edge error. Reduce the ROI width or draw a ROI manually (recommended installation of GDAL >= 1.10)"))
					
	""" Warnings """
	def msgWar2Windows(self):
		self.msgBoxWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [2]", QApplication.translate("semiautomaticclassificationplugin", "It appears that SciPy is not correctly installed. Please, see this page for information about SciPy installation ") + " http://semiautomaticclassificationmanual.readthedocs.org/en/latest/installation_win64.html#scipy-installation")
		
	def msgWar2Linux(self):
		self.msgBoxWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [2]", QApplication.translate("semiautomaticclassificationplugin", "It appears that SciPy is not correctly installed. Please, see this page for information about SciPy installation ") + " http://semiautomaticclassificationmanual.readthedocs.org/en/latest/installation_ubuntu.html#qgis-download-and-installation")
		
	def msgWar5(self):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [5]", QApplication.translate("semiautomaticclassificationplugin", "rasters have different pixel sizes that can lead to incorrect results. Please, consider to resample rasters to the same pixel size"))

	def msgWar6(self):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [6]", QApplication.translate("semiautomaticclassificationplugin", "The same ID class has been already assigned to a different macrolass"))

	def msgWar7(self):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [7]", QApplication.translate("semiautomaticclassificationplugin", "Wavelength already present"))
		
	def msgWar8(self):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [8]", QApplication.translate("semiautomaticclassificationplugin", "Wavelength unit not provided"))
		
	def msgWar9(self, Macro_ID, Class_ID):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [9]", QApplication.translate("semiautomaticclassificationplugin", "The following signature has wavelength different from band set. Macro: " + str(Macro_ID) + " ID: " + str(Class_ID)))
		
	def msgWar10(self, Macro_ID, Class_ID):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [10]", QApplication.translate("semiautomaticclassificationplugin", "The following signature has not a covariance matrix and is excluded. Macro: " + str(Macro_ID) + " ID: " + str(Class_ID)))
				
	def msgWar11(self):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [11]", QApplication.translate("semiautomaticclassificationplugin", "RAM value was too high. Value has been decreased automatically"))
		
	def msgWar12(self, Macro_ID, Class_ID):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [12]", QApplication.translate("semiautomaticclassificationplugin", "The following signature will be excluded if using Maximum Likelihood (singular covariance matrix). Macro: " + str(Macro_ID) + " ID: " + str(Class_ID)))
		
	def msgWar13(self):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [13]", QApplication.translate("semiautomaticclassificationplugin", "Unable to load the virtual raster. Please create it manually"))
		
	def msgWar14(self):
		self.msgBarWarning(QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [14]", QApplication.translate("semiautomaticclassificationplugin", "Unable to proceed. The raster must be in projected coordinates"))