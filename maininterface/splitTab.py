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
		copyright			: (C) 2012-2015 by Luca Congedo
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
import numpy as np
import itertools
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from osgeo import gdal
from osgeo.gdalconst import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class SplitTab:

	def __init__(self):
		pass
		
	# raster name
	def rasterLayerName(self):
		self.rstrLyNm = cfg.ui.raster_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster name: " + self.rstrLyNm)
		
	def refreshClassificationLayer(self):
		ls = cfg.lgnd.layers()
		cfg.ui.raster_name_combo.clear()
		# raster name
		self.rstrLyNm = None
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() > 1:
					cfg.dlg.raster_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster layers refreshed")
		
	# split raster button
	def splitRaster(self):
		try:
			i = len(cfg.ui.raster_name_combo.currentText())
		except:
			self.refreshClassificationLayer()
			return "No"
		if i > 0:
			self.splitRasterToBands(self.rstrLyNm)
			# logger
			cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " split raster layer to band")
		else:
			self.refreshClassificationLayer()
		
	# split raster to bands
	def splitRasterToBands(self, rasterName):
		o = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		outputName = cfg.ui.output_name_lineEdit.text()
		if len(outputName) > 0:
			outputName = str(outputName.encode('ascii','replace')) + "_" 
		if len(o) > 0:
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			cfg.uiUtls.addProgressBar()
			i = cfg.utls.selectLayerbyName(rasterName, "Yes")
			try:
				iL = cfg.utls.rasterToBands(i.source(), o, outputName + rasterName, "Yes")
				for r in iL:
					cfg.utls.addRasterLayer(r, os.path.basename(r))
				cfg.utls.finishSound()
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " end split raster layer to band")
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr32()
				return "No"