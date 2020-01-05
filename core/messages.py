# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
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

class Messages:

	def __init__(self, iface):
		# reference to QGIS interface
		cfg.iface = iface
		
	# Message box information
	def msgBox(self, title, message):
		cfg.QtWidgetsSCP.QMessageBox.information(cfg.iface.mainWindow(), str(title), str(message))
		
	# Message box error
	def msgBoxError(self, title, message):
		cfg.QtWidgetsSCP.QMessageBox.critical(cfg.iface.mainWindow(), title, message)
		
	# Message box warning
	def msgBoxWarning(self, title, message):
		cfg.QtWidgetsSCP.QMessageBox.warning(cfg.iface.mainWindow(), title, message)
		
	# Message bar information
	def msgBar(self, title, message):
		cfg.iface.messageBar().pushMessage(title, message, level= cfg.qgisCoreSCP.Qgis.Info, duration=7)
		
	# Message bar error
	def msgBarError(self, title, message):
		cfg.iface.messageBar().pushMessage(title, message, level= cfg.qgisCoreSCP.Qgis.Critical)
		cfg.utls.sendSMTPMessage('SCP: ' + title, message)
		
	# Message bar warning
	def msgBarWarning(self, title, message):
		cfg.iface.messageBar().pushMessage(title, message, level= cfg.qgisCoreSCP.Qgis.Warning, duration=7)
		
	""" Messages """
	""" Information """
	def msgTest(self, message):
		self.msgBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Test results"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", message))
		
	def msg2(self):		
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [2]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "No log file found"))
		
	def msg3(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [3]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a SCP training input; input is not loaded"))
		
	def msg4(self):	
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [4]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a raster; raster is not loaded"))

	def msg6(self):	
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [6]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a point inside the image area"))
		
	def msg9(self):	
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [9]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Data projections do not match. Reproject data to the same projection"))
		
	def msg10(self):	
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [10]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Maximum Likelihood threshold must be less than 100"))
		
	def msg11(self):	
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [11]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Spectral Angle Mapping threshold must be less than 90"))
		
	def msg14(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [14]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))

	def msg16(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [16]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "At least 3 points are required"))
		
	def msg17(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [17]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Negative IDs are not allowed"))
		
	def msg18(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [18]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select at least one signature"))
		
	def msg19(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [19]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "SCP is recording the Log file"))
				
	def msg20(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [20]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Signature list file (.slf) created"))
		
	def msg21(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [21]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "No image found. Try with a larger area"))
				
	def msg22(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [22]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Create a ROI polygon or use a vector"))
		
	def msg23(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [23]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Define a search area"))
		
	def msg24(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [24]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "At least one band set is required"))
		
	def msg25(self):
		self.msgBar(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Information") + " [25]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to remove bands from a multiband image"))
		
	""" Errors """
		
	def msgErr2(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [2]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "ROI creation failed. \r\nor \r\nPossible reason: one or more band of the band set are missing"))
		
	def msgErr4(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [4]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Signature calculation failed. \r\nPossible reason: the raster is not loaded"))
		
	def msgErr5(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [5]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Import failed. \r\nPossible reason: selected file is not a band set"))
		
	def msgErr6(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [6]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification failed. \r\nIt appears the one or more bands of the band set are missing"))
		
	def msgErr7(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [7]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "ROI creation failed. \r\nPossible reason: input is a virtual raster or band is not loaded"))
	
	def msgErr8(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [8]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "No metadata found inside the input directory (a .txt file whose name contains MTL)"))

	def msgErr9(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [9]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Raster not found"))
		
	def msgErr11(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [11]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Vector or raster not found"))
		
	def msgErr15(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [15]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error saving signatures"))
			
	def msgErr16(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [16]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error opening signatures"))
		
	def msgErr17(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [17]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error opening spectral library"))
					
	def msgErr18(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [18]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error saving spectral library"))
					
	def msgErr19(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [19]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Import failed"))

	def msgErr20(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [20]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "ROI creation failed"))
					
	def msgErr21(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [21]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Internet connection failed"))

	def msgErr23(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [23]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error saving raster"))

	def msgErr24(self, Macro_ID, Class_ID):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [24]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "The following signature does not match the band set. MC_ID: " + str(Macro_ID) + " C_ID: " + str(Class_ID)))
			
	def msgErr25(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [25]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error reading raster. Possibly the raster path contains unicode characters"))
			
	def msgErr26(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [26]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "The version of Numpy is outdated"))

	def msgErr27(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [27]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to perform operation. Possibly OGR is missing drivers. Please repeat QGIS installation"))
					
	def msgErr28(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [28]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Memory error. Please, set a lower value of RAM in the tab Settings"))
					
	def msgErr29(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [29]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Edge error. Reduce the ROI width or draw a ROI manually"))
				
	def msgErr31(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [31]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error calculating signature. Possibly ROI is too small"))
		
	def msgErr32(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [32]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to split bands"))
		
	def msgErr33(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [33]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error reading band set. Possibly raster files are not loaded"))
		
	def msgErr34(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [34]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Clip area outside image. Check the raster projection"))
		
	def msgErr35(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [35]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to merge. Signatures have different unit or wavelength"))
		
	def msgErr36(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [36]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to calculate. Expression error"))

	def msgErr37(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [37]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to calculate. Metadata error"))
		
	def msgErr38(self, path):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [38]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to load raster " + path))

	def msgErr39(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [39]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to find images"))
		
	def msgErr40(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [40]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to connect"))
		
	def msgErr41(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [41]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to load image"))
		
	def msgErr42(self, imageID):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [42]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to download image " + imageID + " . Please check the availability at http://earthexplorer.usgs.gov/"))

	def msgErr43(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [43]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Attribute table error"))
			
	def msgErr44(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [44]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to pansharpen: missing bands "))
				
	def msgErr45(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [45]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to calculate"))	
		
	def msgErr46(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [46]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error reading raster. Possibly bands are not aligned"))
		
	def msgErr47(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [47]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to get raster projection. Try to reproject the raster"))
			
	def msgErr48(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [48]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error calculating accuracy. Possibly shapefile polygons are outside classification"))
			
	def msgErr50(self, error):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [50]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Internet error:" + error))
				
	def msgErr53(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [53]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Memory error. Please, decrease decimal precision"))
			
	def msgErr54(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [54]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error calculating plot"))
	
	def msgErr55(self, imageID):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [55]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to download image " + imageID + " . Check user name and password"))

	def msgErr56(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [56]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "SSL connection error. Please see the FAQ of the plugin user manual for solving this"))
		
	def msgErr57(self, signature):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [57]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Spectral signature " + signature +" doesn't match Band set. Calculate the spectral signatures again"))
		
	def msgErr58(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [58]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Directory error. Check write permission"))
		
	def msgErr59(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [59]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error accessing training input"))
		
	def msgErr60(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [60]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Rasters appear to be in different projections. Reproject rasters to the same CRS"))
		
	def msgErr61(self, raster):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [61]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Projection error. Try to assign projection to raster " + raster))
		
	def msgErr62(self, index):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [62]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band set " + index + " not available"))

	def msgErr63(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [63]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Memory error, too many combinations. Try to reclassify the values"))
		
	def msgErr64(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [64]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error, please change stratification parameters"))
		
	def msgErr65(self):
		self.msgBarError(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + " [65]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error, extent of vector too large"))
		
	""" Warnings """
	def msgWar2Windows(self):
		self.msgBoxWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [2]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "It appears that SciPy is not correctly installed. Please, update QGIS "))
		
	def msgWar2Linux(self):
		self.msgBoxWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [2]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "It appears that SciPy is not correctly installed. Please, check the user manual"))

	def msgWar7(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [7]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Wavelength already present"))
		
	def msgWar8(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [8]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Wavelength unit not provided in band set"))
		cfg.msgWar8check = "Yes"
		
	def msgWar9(self, Macro_ID, Class_ID):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [9]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "The following signature has wavelength different from band set. Macro: " + str(Macro_ID) + " ID: " + str(Class_ID)))
		
	def msgWar10(self, Macro_ID, Class_ID):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [10]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "The following signature has not a covariance matrix and is excluded. Macro: " + str(Macro_ID) + " ID: " + str(Class_ID)))
				
	def msgWar11(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [11]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "RAM value was too high. Value has been decreased automatically"))
		
	def msgWar12(self, Macro_ID, Class_ID):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [12]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "The following signature will be excluded if using Maximum Likelihood (singular covariance matrix). Macro: " + str(Macro_ID) + " ID: " + str(Class_ID)))
		
	def msgWar13(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [13]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to load the virtual raster. Please create it manually"))
		
	def msgWar14(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [14]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to proceed. The raster must be in projected coordinates"))
		
	def msgWar15(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [15]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select at least one raster band"))
	
	def msgWar16(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [16]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Incorrect expression"))
			
	def msgWar17(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [17]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unable to access the temporary directory"))
			
	def msgWar18(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [18]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Reduce the search area extent within 10 degrees of latitude and 10 degrees of longitude"))
		
	def msgWar19(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [19]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Macroclass symbology is missing"))
		
	def msgWar20(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [20]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Missing bands"))

	def msgWar21(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [21]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "No metadata found inside the input directory. Default values will be used"))

	def msgWar22(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [22]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "The coordinate system of training input is different from the input image. Please create a new training input"))
		
	def msgWar23(self, image):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [23]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Check integrity of image " + image))
		
	def msgWar24(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [24]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Search error HTTP Status 500, reduce the result number"))
		
	def msgWar25(self, band_set):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [25]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band set " + str(band_set) + " isn't correctly defined"))
		
	def msgWar26(self, band_set):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [26]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band set " + str(band_set) + " doesn't match training input. Create a new training input or change band set."))
		
	def msgWar27(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [27]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Signature bands don't match band set. Calculate the spectral signature again"))
		
	def msgWar28(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [28]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Please define band sets with matching number of bands"))
		
	def msgWar29(self):
		self.msgBarWarning(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Warning") + " [29]", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Please add single band rasters to the band set"))
		