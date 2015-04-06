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

class BandCalcTab:

	def __init__(self):
		pass
		
	# Set raster band table
	def rasterBandName(self):
		ls = cfg.lgnd.layers()
		l = cfg.ui.tableWidget_band_calc
		l.setSortingEnabled(False)
		cfg.utls.clearTable(l)
		b = 0
		for x in ls:
			if x.type() == QgsMapLayer.RasterLayer and x.bandCount() == 1:
				# band name
				bN = x.name()
				# Add band to table
				l.insertRow(b)
				itV = QTableWidgetItem(cfg.variableName + str(b + 1))
				itV.setFlags(Qt.ItemIsEnabled)
				l.setItem(b, 0, itV)
				itN = QTableWidgetItem(bN)
				itN.setFlags(Qt.ItemIsEnabled)
				l.setItem(b, 1, itN)
				b = b + 1
		if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
			c = 1
			for x in cfg.bndSetLst:
				# band name
				bN = cfg.variableBandsetName + "#b" + str(c)
				# Add band to table
				l.insertRow(b)
				itV = QTableWidgetItem(cfg.variableName + str(b + 1))
				itV.setFlags(Qt.ItemIsEnabled)
				l.setItem(b, 0, itV)
				itN = QTableWidgetItem(bN)
				itN.setFlags(Qt.ItemIsEnabled)
				l.setItem(b, 1, itN)
				b = b + 1
				c = c + 1
		elif cfg.imgNm is not None:
			r = cfg.utls.selectLayerbyName(cfg.imgNm, "Yes")
			iR = r.source()
			x = cfg.utls.getNumberBandRaster(cfg.imgSrc)
			for c in range(1, x + 1):
				# band name
				bN = cfg.variableBandsetName + "#b" + str(c)
				# Add band to table
				l.insertRow(b)
				itV = QTableWidgetItem(cfg.variableName + str(b + 1))
				itV.setFlags(Qt.ItemIsEnabled)
				l.setItem(b, 0, itV)
				itN = QTableWidgetItem(bN)
				itN.setFlags(Qt.ItemIsEnabled)
				l.setItem(b, 1, itN)
				b = b + 1
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster band name checklist created")
		
	# calculate
	def calculate(self):
		tW = cfg.ui.tableWidget_band_calc
		c = tW.rowCount()
		if c > 0:
			outF = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save raster output"), "", "*.tif")
			if len(outF) > 0:
				cfg.uiUtls.addProgressBar()
				cfg.uiUtls.updateBar(10)
				expression = " " + cfg.ui.plainTextEdit_calc.toPlainText() + " "
				check = self.checkExpression(expression)
				if check == "No":
					cfg.mx.msgErr36()
					cfg.uiUtls.removeProgressBar()
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " check No")
					return "No"
				cfg.cnvs.setRenderFlag(False)
				it = 1
				for e in check:
					n = os.path.basename(outF)
					if n.lower().endswith(".tif"):
						if len(check) > 1:
							out = os.path.dirname(outF) + "/" + n.rstrip(n[len(n) - 4: len(n)]) + "_" + str(it) + ".tif"
						else:
							out = outF
					else:
						if len(check) > 1:
							out = os.path.dirname(outF) + "/" + n + "_" + str(it) + ".tif"
						else:
							out = outF + ".tif"
					tPMN = cfg.tmpVrtNm + ".vrt"
					# date time for temp name
					dT = cfg.utls.getTime()
					tPMD = cfg.tmpDir + "/" + dT + tPMN
					# band list
					bList = []
					bandNumberList = []
					# variable list
					variableList = []
					for b in range(0, c):
						bV = tW.item(b, 0).text()
						bN = tW.item(b, 1).text()
						if bV in e or bN in e:
							variableList.append(['"' + bV + '"', '"' + bN + '"'])
							if cfg.variableBandsetName in bN:
								bandNumber = bN.split("#b")
								if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
									bPath = cfg.bndSetLst[int(bandNumber[1]) - 1]
									bandNumberList.append(1)
									bList.append(bPath)
								elif cfg.imgNm is not None:
									i = cfg.utls.selectLayerbyName(cfg.imgNm, "Yes")
									try:
										bPath = i.source()
									except Exception, err:
										cfg.mx.msg4()
										self.rasterBandName()
										# logger
										cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
										cfg.uiUtls.removeProgressBar()
										cfg.cnvs.setRenderFlag(True)
										return "No"
									bandNumberList.append(int(bandNumber[1]))
									bList.append(bPath)
							else:
								i = cfg.utls.selectLayerbyName(bN, "Yes")
								try:
									bPath = i.source()
								except Exception, err:
									cfg.mx.msg4()
									self.rasterBandName()
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
									cfg.uiUtls.removeProgressBar()
									cfg.cnvs.setRenderFlag(True)
									return "No"
								bandNumberList.append(1)
								bList.append(bPath)
					vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes")
					# open input with GDAL
					rD = gdal.Open(tPMD, GA_ReadOnly)
					if rD is None:
						cfg.mx.msg4()
						self.rasterBandName()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " None raster")
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
						return "No"
					# band list
					bL = cfg.utls.readAllBandsFromRaster(rD)
					# output rasters
					oM = []
					oM.append(out)
					oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType)
					o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.bandCalculation, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "calculation " + str(it))
					# close GDAL rasters
					for b in range(0, len(oMR)):
						oMR[b] = None
					for b in range(0, len(bL)):
						bL[b] = None
					rD = None
					if o != "No":
						r = cfg.utls.addRasterLayer(out, os.path.basename(out))
						cfg.utls.rasterSymbolSingleBandGray(r)
					it = it + 1
				cfg.uiUtls.updateBar(100)	
				cfg.utls.finishSound()
				cfg.cnvs.setRenderFlag(True)
				cfg.uiUtls.removeProgressBar()
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band calculation ended")
				
	def textChanged(self):
		expression = " " + cfg.ui.plainTextEdit_calc.toPlainText() + " "
		self.checkExpression(expression)
		
	# check the expression and return it
	def checkExpression(self, expression):
		tW = cfg.ui.tableWidget_band_calc
		v = tW.rowCount()
		name = []		
		cfg.ui.plainTextEdit_calc.setStyleSheet("color : red")
		for x in range(0, v):
			name.append('"' + tW.item(x, 0).text() + '"')
			name.append('"' + tW.item(x, 1).text() + '"')

		e = expression.rstrip().split("\n")
		ex = []
		for f in e:
			oldF = f
			ex.append(f)
			# create function
			for i in name:
				f = f.replace(i, " rasterSCPArrayfunctionBand ")
			if f == oldF:
				cfg.ui.plainTextEdit_calc.setStyleSheet("color : red")
				cfg.ui.toolButton_calculate.setEnabled(False)
				return "No"
			else:
				# replace numpy operators
				f = cfg.utls.replaceNumpyOperators(f)
				rasterSCPArrayfunctionBand = np.arange(9).reshape(3, 3)
				try:
					o = eval(f)
					cfg.ui.plainTextEdit_calc.setStyleSheet("color : green")
					cfg.ui.toolButton_calculate.setEnabled(True)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.ui.plainTextEdit_calc.setStyleSheet("color : red")
					cfg.ui.toolButton_calculate.setEnabled(False)
					return "No"
		return ex
			
	def doubleClick(self, index):
		tW = cfg.ui.tableWidget_band_calc
		k = tW.item(index.row(), index.column()).text()
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText('"' + k + '"')
		cfg.ui.plainTextEdit_calc.setFocus()
		#cursor.insertHtml("<FONT color=blue  style=\"BACKGROUND-COLOR: red\">"+ k +"</FONT>")

	def buttonPlus(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" + ")

	def buttonMinus(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" - ")	
		
	def buttonProduct(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" * ")

	def buttonRatio(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" / ")
		
	def buttonPower(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText("^")
						
	def buttonSQRT(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText("sqrt(")		
		
	def buttonLbracket(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText("(")
				
	def buttonRbracket(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(")")		
		
	def buttonSin(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" sin(")
			
	def buttonASin(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" asin(")
					
	def buttonCos(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" cos(")
							
	def buttonACos(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" acos(")
		
	def buttonTan(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" tan(")		
		
	def buttonATan(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" atan(")
			
	def buttonExp(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" exp(")

	def buttonLog(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" ln(")

	def buttonPi(self):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(" pi ")