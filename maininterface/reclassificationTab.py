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
# for debugging
import inspect
import time
# for moving files
import shutil
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from osgeo import gdal
from osgeo import ogr 
from osgeo import osr
from osgeo.gdalconst import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class ReclassificationTab:

	def __init__(self):
		pass
					
	# reclassify
	def reclassify(self):
		self.clssfctnNm = cfg.ui.reclassification_name_combo.currentText()
		i = cfg.utls.selectLayerbyName(self.clssfctnNm, "Yes")
		try:
			classificationPath = i.source()
		except Exception, err:
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		list = self.getValuesTable()
		tW = cfg.ui.reclass_values_tableWidget
		c = tW.rowCount()
		if c > 0:
			out = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save raster output"), "", "*.tif")
			if len(out) > 0:
				cfg.uiUtls.addProgressBar()
				cfg.uiUtls.updateBar(10)
				n = os.path.basename(out)
				if n.endswith(".tif"):
					out = out
				else:
					out = out + ".tif"
				# date time for temp name
				dT = cfg.utls.getTime()
				tPMN2 = dT + cfg.calcRasterNm + ".tif"
				tPMD2 = cfg.tmpDir + "/" + tPMN2
				# open input with GDAL
				rD = gdal.Open(classificationPath, GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD2)
				reclassList = self.createReclassificationStringFromList(list)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.reclassifyRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", reclassList, cfg.variableName)
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				if cfg.rasterCompression != "No":
					try:
						cfg.utls.GDALCopyRaster(tPMD2, out, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						os.remove(tPMD2)
					except Exception, err:
						shutil.copy(tPMD2, out)
						os.remove(tPMD2)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					shutil.copy(tPMD2, out)
					os.remove(tPMD2)
				r = cfg.utls.addRasterLayer(out, os.path.basename(out))
				# create symbol
				if cfg.ui.apply_symbology_checkBox.isChecked() is True:	
					sL = cfg.classD.getSignatureList()
					if str(cfg.ui.class_macroclass_comboBox_2.currentText()) == "MC ID":
						mc = "Yes"
					else:
						mc = "No"
					cfg.utls.rasterSymbol(r, sL, mc)
				cfg.utls.finishSound()
				cfg.uiUtls.removeProgressBar()
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " reclassification ended")

	def calculateUniqueValues(self):
		self.clssfctnNm = cfg.ui.reclassification_name_combo.currentText()
		i = cfg.utls.selectLayerbyName(self.clssfctnNm, "Yes")
		try:
			classificationPath = i.source()
		except Exception, err:
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		try:
			clssRstrSrc = unicode(classificationPath)
			ck = "Yes"
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			ck = "No"
		if ck == "No":
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
		else:
			cfg.uiUtls.addProgressBar()
			cfg.uiUtls.updateBar(10)
			refRstrDt = gdal.Open(clssRstrSrc, GA_ReadOnly)
			# combination finder
			# band list
			bLR = cfg.utls.readAllBandsFromRaster(refRstrDt)
			cfg.rasterBandUniqueVal = np.zeros((1, 1))
			cfg.rasterBandUniqueVal = np.delete(cfg.rasterBandUniqueVal, 0, 1)
			o = cfg.utls.processRaster(refRstrDt, bLR, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
			cfg.rasterBandUniqueVal = np.unique(cfg.rasterBandUniqueVal).tolist()
			refRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)	
			cfg.uiUtls.updateBar(80)
			if cfg.ui.CID_MCID_code_checkBox.isChecked() is True:
				uniq = cfg.utls.calculateUnique_CID_MCID()
				if uniq == "No":
					uniq = self.createValueList(cfg.rasterBandUniqueVal)
			else:
				uniq = self.createValueList(cfg.rasterBandUniqueVal)
			self.addValuesToTable(uniq)
			for b in range(0, len(bLR)):
				bLR[b] = None
			refRstrDt = None
			cfg.uiUtls.updateBar(100)
			cfg.uiUtls.removeProgressBar()
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " values calculated")
			
	def createValueList(self, list):
		unique = []
		for i in list:
			unique.append([float(i),float(i)])
		l = sorted(unique, key=lambda unique: (unique[0]))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " unique" + str(l))
		return l
		
	def addValuesToTable(self, valuesList):
		cfg.ReclassTabEdited = "No"
		tW = cfg.ui.reclass_values_tableWidget
		cfg.utls.clearTable(tW)
		c = tW.rowCount()
		for i in valuesList:
			tW.setRowCount(c + 1)
			it = QTableWidgetItem(str(c + 1))
			oldV = QTableWidgetItem(str(i[0]))
			newV = QTableWidgetItem(str(i[1]))
			tW.setItem(c, 0, oldV)
			tW.setItem(c, 1, newV)
			# add list items to table
			tW.setRowCount(c + 1)
			c = c + 1
		cfg.ReclassTabEdited = "Yes"
		
	def getValuesTable(self):
		tW = cfg.ui.reclass_values_tableWidget
		c = tW.rowCount()
		list = []
		for row in range(0, c):
			old = tW.item(row, 0).text()
			new = tW.item(row, 1).text()
			list.append([old, new])
		return list
			
	def createReclassificationStringFromList(self, list):
		reclassList = []
		for i in list:
			try:
				old = float(i[0])
				cond = cfg.variableName + " == " + str(old)
			except:
				cond = str(i[0])
			reclassList.append([cond, float(i[1])])
		return reclassList
			
	def addRowToTable(self):
		cfg.ReclassTabEdited = "No"
		tW = cfg.ui.reclass_values_tableWidget
		# add item to table
		c = tW.rowCount()
		it = QTableWidgetItem(str(c + 1))
		old = QTableWidgetItem(str(0))
		new = QTableWidgetItem(str(0))
		# add list items to table
		tW.setRowCount(c + 1)
		tW.setItem(c, 0, old)
		tW.setItem(c, 1, new)
		cfg.ReclassTabEdited = "Yes"

	def removePointFromTable(self):
		cfg.utls.removeRowsFromTable(cfg.ui.reclass_values_tableWidget)
		
	def editedCell(self, row, column):
		if cfg.ReclassTabEdited == "Yes":
			tW = cfg.ui.reclass_values_tableWidget
			val = tW.item(row, column).text()
			if column == 1:
				try:	
					val = float(val)
				except:
					cfg.ReclassTabEdited = "No"
					tW.setItem(row, column, QTableWidgetItem(str(0)))
					cfg.ReclassTabEdited = "Yes"
			elif column == 0:	
				c = val.replace(cfg.variableName, "rasterSCPArrayfunctionBand")
				rasterSCPArrayfunctionBand = np.arange(9).reshape(3, 3)
				try:
					eval("np.where(" + c + ", 1, rasterSCPArrayfunctionBand)")
				except:
					cfg.ReclassTabEdited = "No"
					tW.setItem(row, column, QTableWidgetItem(str(0)))
					cfg.ReclassTabEdited = "Yes"
					cfg.mx.msgWar16()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "edited cell" + str(row) + ";" + str(column))