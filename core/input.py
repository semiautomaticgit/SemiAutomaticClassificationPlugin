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

import os
# for debugging
import inspect
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class Input:

	# check refresh raster and image list	
	def checkRefreshRasterLayer(self):
		# check if other processes are active
		if cfg.actionCheck == "No":
			self.refreshRasterLayer()
			
	def raster_layer_combo(self, layer):
		cfg.raster_name_combo.addItem(layer)
			
	# refresh raster and image list	
	def refreshRasterLayer(self):
		cfg.raster_name_combo.blockSignals(True)
		cfg.rasterComboEdited = "No"
		lL = cfg.lgnd.layers()
		cfg.raster_name_combo.clear()
		# image name
		cfg.imgNm = None
		# raster name
		cfg.rstrNm = None
		# empty item for new band set
		self.raster_layer_combo("")
		for l in lL:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() > 1:
					self.raster_layer_combo(l.name())
		if cfg.bndSetPresent == "Yes":
			self.raster_layer_combo(cfg.bndSetNm)
			id = cfg.raster_name_combo.findText(cfg.bndSetNm)
			cfg.raster_name_combo.setCurrentIndex(id)
			cfg.rstrNm = cfg.bndSetNm
			cfg.imgNm = cfg.rstrNm
		elif cfg.bndSetPresent == "No":
			id = cfg.raster_name_combo.findText(cfg.bndSetNm)
			cfg.raster_name_combo.removeItem(id)
			cfg.bst.clearBandSet("No", "No")
		cfg.rasterComboEdited = "Yes"
		cfg.raster_name_combo.blockSignals(False)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster layers refreshed")

	# set raster name as ROI target
	def rasterLayerName(self):
		if cfg.rasterComboEdited == "Yes":
			cfg.bst.clearBandSet("No", "No")
			cfg.rstrNm = str(cfg.raster_name_combo.currentText())
			cfg.imgNm = cfg.rstrNm	
			# set classification input
			cfg.classD.algorithmThreshold()
			cfg.classD.previewSize()
			# set input
			cfg.rLay = cfg.utls.selectLayerbyName(str(cfg.rstrNm))
			if cfg.rLay is not None:
				id = cfg.raster_name_combo.findText(cfg.bndSetNm)
				cfg.raster_name_combo.removeItem(id)
				cfg.imgSrc = cfg.rLay.source()
				cfg.bndSetPresent = "No"
				cfg.bst.clearBandSet("No", "No")
				cfg.bst.rasterToBandName(cfg.rstrNm)
			elif cfg.rstrNm == "" :
				cfg.bndSet = []
				cfg.bndSetWvLn = {}
				cfg.bndSetPresent = "No"
				cfg.bst.clearBandSet("No", "Yes")
			cfg.utls.writeProjectVariable("rasterName", cfg.rstrNm)
			# reset rapid ROI spinbox
			cfg.uid.rapidROI_band_spinBox.setValue(1)
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "input raster: " + str(cfg.rstrNm))
