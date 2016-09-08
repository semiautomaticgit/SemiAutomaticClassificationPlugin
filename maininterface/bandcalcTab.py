# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2016 by Luca Congedo
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

from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class BandCalcTab:

	def __init__(self):
		self.expressionButton = False
		self.decisionRulesButton = False
		
	# toolbox changed
	def toolboxChanged(self, index):
		cfg.bandCalcIndex = index
		if cfg.bandCalcIndex == 0:
			cfg.ui.toolButton_calculate.setEnabled(self.expressionButton)
		elif cfg.bandCalcIndex == 1:
			cfg.ui.toolButton_calculate.setEnabled(self.decisionRulesButton)
		
	# add row to table
	def addRowToTable(self):
		tW = cfg.ui.decision_rules_tableWidget
		# add item to table
		c = tW.rowCount()
		# add list items to table
		tW.setRowCount(c + 1)
		tW.blockSignals(True)
		cfg.utls.addTableItem(tW, str(c + 1), c, 0)
		cfg.utls.addTableItem(tW, "", c, 1)
		tW.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "added row " + str(c + 1))
		e = cfg.bCalc.decisionRulesExpression()
		check = self.checkExpression(e)
		if len(check) > 0:
			tW.setStyleSheet("color : green")
		else:
			tW.setStyleSheet("color : red")	
		
	# remove row
	def removeHighlightedRule(self):
		tW = cfg.ui.decision_rules_tableWidget
		cfg.utls.removeRowsFromTable(tW)
		e = cfg.bCalc.decisionRulesExpression()
		check = self.checkExpression(e)
		if len(check) > 0:
			tW.setStyleSheet("color : green")
		else:
			tW.setStyleSheet("color : red")
			
	# clear the rules
	def clearRulesAction(self):
		self.clearRules()
		expression = cfg.bCalc.decisionRulesExpression()
		check = self.checkExpression(expression)
		tW = cfg.ui.decision_rules_tableWidget
		if len(check) > 0:
			tW.setStyleSheet("color : green")
		else:
			tW.setStyleSheet("color : red")
		
	# clear the rules
	def clearRules(self, question = "Yes"):
		if question == "Yes":
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Clear rules"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the rules?"))
		else:
			a = "Yes"
		if a == "Yes":
			tW = cfg.ui.decision_rules_tableWidget
			tW.blockSignals(True)
			cfg.utls.clearTable(tW)
			tW.blockSignals(False)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		
	# edited table
	def editedDecisionRulesTable(self, row, column):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		tW = cfg.ui.decision_rules_tableWidget
		if column == 0:
			try:
				tr = int(tW.item(row, 0).text())
			except:
				tr = 1
				tW.blockSignals(True)
				cfg.utls.setTableItem(tW, row, 0, str(tr))
				tW.blockSignals(False)
		try:
			value = tW.item(row, 0).text()
		except:
			value = "No"
		NoDataValue = cfg.ui.nodata_spinBox_4.value()
		try:
			t = tW.item(row, 1).text()
		except:
			tW.setStyleSheet("color : red")
			self.decisionRulesButton = False
			cfg.ui.toolButton_calculate.setEnabled(self.decisionRulesButton)
			return "No"
		e = cfg.bCalc.decisionRulesExpression()
		check = self.checkExpression(e)
		if len(check) > 0:
			tW.setStyleSheet("color : green")
		else:
			tW.setStyleSheet("color : red")
				
	# create decision rule expression
	def decisionRulesExpression(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		tW = cfg.ui.decision_rules_tableWidget
		NoDataValue = cfg.ui.nodata_spinBox_4.value()
		c = tW.rowCount()
		if c > 0:
			for row in range(0, c):
				try:
					w = e
				except:
					pass
				try:
					value = tW.item(row, 0).text()
					t = tW.item(row, 1).text()
				except:
					return "No"
				tSplit = t.split(";")
				e = "cfg.np.where( "
				for b in tSplit:
					if len(b) > 0:
						e = e + "(" + b + ") & "
				e = e[:-4] + "), " + str(value) + "," + "str(NoDataValue)" + ")"
				try:
					e = w.replace("str(NoDataValue)", str(e))
				except:
					pass
			e = e.replace("str(NoDataValue)", str(NoDataValue))
			return e
		
	# import rules from text file
	def importRules(self):
		file = cfg.utls.getOpenFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a text file of rules"), "", "txt (*.txt)")
		if len(file) > 0:
			self.clearRules("No")
			tW = cfg.ui.decision_rules_tableWidget
			text = open(file, 'r')
			lines = text.readlines()
			tW.blockSignals(True)
			for b in lines:
				v = b.split(";", 1)
				# add item to table
				c = tW.rowCount()
				# add list items to table
				tW.setRowCount(c + 1)
				try:
					cfg.utls.addTableItem(tW, v[0].strip(), c, 0)
					cfg.utls.addTableItem(tW, v[1].strip(), c, 1)
				except:
					tW.blockSignals(False)
					self.clearRules("No")
					cfg.mx.msgErr19()
					return "No"
			tW.blockSignals(False)
			expression = cfg.bCalc.decisionRulesExpression()
			check = self.checkExpression(expression)
			if len(check) > 0:
				tW.setStyleSheet("color : green")
			else:
				tW.setStyleSheet("color : red")
				
	# export rules to text file
	def exportRules(self):
		tW = cfg.ui.decision_rules_tableWidget
		c = tW.rowCount()
		if c > 0:
			file = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save the rules to file"), "", "txt (*.txt)")
			if len(file) > 0:
				if file.lower().endswith(".txt"):
					pass
				else:
					file = file + ".txt"
				f = self.rulesToCSV()
				o = open(file, 'w')
				o.write(f)
				o.close()
				
	# convert rules to CSV
	def rulesToCSV(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		tW = cfg.ui.decision_rules_tableWidget
		c = tW.rowCount()
		if c > 0:
			e = ""
			for row in range(0, c):
				try:
					value = tW.item(row, 0).text()
					t = tW.item(row, 1).text()
				except:
					return "No"
				e = e + value + ";" + t + "\n"
			return e
					
	# Set raster band table
	def rasterBandName(self):
		cfg.utls.refreshRasterExtent()
		ls = cfg.lgnd.layers()
		l = cfg.ui.tableWidget_band_calc
		l.setSortingEnabled(False)
		cfg.utls.clearTable(l)
		check = "Yes"
		b = 0
		for x in ls:
			if x.type() == QgsMapLayer.RasterLayer and x.bandCount() == 1:
				# band name
				bN = x.name()
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1
		if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
			c = 1
			for x in cfg.bndSetLst:
				# band name
				bN = cfg.variableBandsetName + "#b" + str(c)
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1
				c = c + 1
		elif cfg.imgNm is not None:
			try:
				r = cfg.utls.selectLayerbyName(cfg.imgNm, "Yes")
				iR = r.source()
			except:
				check = "No"
			if check == "Yes":
				x = cfg.utls.getNumberBandRaster(cfg.imgSrc)
				for c in range(1, x + 1):
					# band name
					bN = cfg.variableBandsetName + "#b" + str(c)
					# Add band to table
					l.insertRow(b)
					cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
					cfg.utls.addTableItem(l, bN, b, 1, "No")
					b = b + 1
		if check == "Yes":
			cfg.utls.findBandNumber()
			if cfg.BLUEBand is not None:
				# band name
				bN = cfg.variableBlueName
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1
			if cfg.REDBand is not None:
				# band name
				bN = cfg.variableRedName
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1
			if cfg.NIRBand is not None:
				# band name
				bN = cfg.variableNIRName
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1		
		cfg.bCalc.textChanged()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster band name checklist created")
		
	# add satellite list to combo
	def addIndicesToCombo(self, indicesList):
		for i in indicesList:
			cfg.ui.band_set_calculation_combo.addItem(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " indices added")
	
	# set indices combo
	def setIndices(self):
		pT = cfg.ui.plainTextEdit_calc
		text = pT.toPlainText()
		if len(text) > 0:
			space = "\n"
		else:
			space = ""
		if cfg.ui.band_set_calculation_combo.currentText() == cfg.indNDVI:
			pT.setPlainText(text + space + '( "' + str(cfg.variableNIRName) + '" - "' + str(cfg.variableRedName) +'") / ( "' + str(cfg.variableNIRName) + '" + "' + str(cfg.variableRedName) +'") @ NDVI')
		elif cfg.ui.band_set_calculation_combo.currentText() == cfg.indEVI:
			pT.setPlainText(text + space + '2.5 * ( "' + str(cfg.variableNIRName) + '" - "' + str(cfg.variableRedName) + '" ) / ( "' + str(cfg.variableNIRName) + '" + 6 * "' + str(cfg.variableRedName) + '" - 7.5 * "' + str(cfg.variableBlueName) + '" + 1) @ EVI')
				
	# calculate button
	def calculateButton(self):
		# band calc
		if cfg.bandCalcIndex == 0:
			cfg.bCalc.calculate()
		# decision rules
		elif cfg.bandCalcIndex == 1:
			e = cfg.bCalc.decisionRulesExpression()
			cfg.bCalc.calculate(None, "No", e)
		
	# calculate
	def calculate(self, outFile = None, batch = "No", expressionString = None, extentRaster = None, extentList = None, quiet = "No"):
		if batch == "No":
			pass
		else:
			self.rasterBandName()
		tW = cfg.ui.tableWidget_band_calc
		c = tW.rowCount()
		if c > 0:
			if outFile is None:
				# band calc
				if cfg.bandCalcIndex == 0:
					textCount = cfg.ui.plainTextEdit_calc.blockCount()
					if textCount > 1:
						outF = cfg.utls.getExistingDirectory(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
						outF = outF + "/" + cfg.calcRasterNm + ".tif"
					else:
						outF = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster output"), "", "*.tif")
				# decision rules
				elif cfg.bandCalcIndex == 1:
					outF = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster output"), "", "*.tif")
			else:
				outF = outFile
			if len(outF) > 0:
				if outFile is None:
					cfg.uiUtls.addProgressBar()
				cfg.uiUtls.updateBar(10)
				if expressionString is None:
					expression = " " + cfg.ui.plainTextEdit_calc.toPlainText() + " "
				else:
					expression = expressionString
				check = self.checkExpression(expression)
				if check == "No":
					cfg.mx.msgErr36()
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " check No")
					if outFile is None:
						cfg.uiUtls.removeProgressBar()
						return "No"
				cfg.cnvs.setRenderFlag(False)
				it = 1
				for eM in check:
					e = eM[0]
					dCheck = "Yes"
					try:
						eN = eM[1]
					except Exception, err:
						dCheck = "No"
						cfg.mx.msg4()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						if outFile is None:
							cfg.uiUtls.removeProgressBar()
							cfg.cnvs.setRenderFlag(True)
							return "No"
					if dCheck == "Yes":
						if eN is None:
							n = cfg.osSCP.path.basename(outF)
						else:
							n = eN
						if n.lower().endswith(".tif"):
							if eN is None and len(check) == 1:
								out = cfg.osSCP.path.dirname(outF) + "/" + n.rstrip(n[len(n) - 4: len(n)]) + ".tif"
							elif eN is None and len(check) > 1:
								out = cfg.osSCP.path.dirname(outF) + "/" + n.rstrip(n[len(n) - 4: len(n)]) + "_" + unicode(it) + ".tif"
							else:
								out = cfg.osSCP.path.dirname(outF) + "/" + n.rstrip(n[len(n) - 4: len(n)]) + ".tif"
						else:
							if eN is None and len(check) == 1:
								out = cfg.osSCP.path.dirname(outF) + "/" + n + ".tif"
							elif eN is None and len(check) > 1:
								out = cfg.osSCP.path.dirname(outF) + "/" + n + "_" + unicode(it) + ".tif"
							else:
								out = cfg.osSCP.path.dirname(outF) + "/" + n + ".tif"
						tPMN = cfg.tmpVrtNm + ".vrt"
						# date time for temp name
						dT = cfg.utls.getTime()
						tPMD = cfg.tmpDir + "/" + dT + tPMN
						tPMN2 = dT + cfg.calcRasterNm + ".tif"
						tPMD2 = cfg.tmpDir + "/" + tPMN2
						# band list
						bList = []
						bandNumberList = []
						# variable list
						variableList = []
						for b in range(0, c):
							bV = tW.item(b, 0).text()
							bN = tW.item(b, 1).text()
							if unicode('"' +  bV +'"') in e or unicode('"' + bN +'"') in e:
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
											cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
											if outFile is None:
												cfg.uiUtls.removeProgressBar()
												cfg.cnvs.setRenderFlag(True)
												return "No"
										bandNumberList.append(int(bandNumber[1]))
										bList.append(bPath)
								elif cfg.variableBlueName in bN or cfg.variableRedName in bN or cfg.variableNIRName in bN :
									if bN == cfg.variableRedName :
										bandNumber = ["", cfg.REDBand]
									elif bN == cfg.variableNIRName :
										bandNumber = ["", cfg.NIRBand]
									elif bN == cfg.variableBlueName :
										bandNumber = ["", cfg.BLUEBand]
									else:
										cfg.mx.msg4()
										if outFile is None:
											cfg.uiUtls.removeProgressBar()
											cfg.cnvs.setRenderFlag(True)
											return "No"
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
											cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
											if outFile is None:
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
										cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
										if outFile is None:
											cfg.uiUtls.removeProgressBar()
											cfg.cnvs.setRenderFlag(True)
											return "No"
									bandNumberList.append(1)
									bList.append(bPath)				
						try:
							gdalRaster2 = cfg.gdalSCP.Open(bPath, cfg.gdalSCP.GA_ReadOnly)
							gBand2 = gdalRaster2.GetRasterBand(int(1)) 
						except Exception, err:
							cfg.mx.msg4()
							self.rasterBandName()
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							if outFile is None:
								cfg.uiUtls.removeProgressBar()
								cfg.cnvs.setRenderFlag(True)
								return "No"
						noData = gBand2.GetNoDataValue()
						if cfg.ui.nodata_checkBox_3.isChecked() is True:
							NoDataValue = cfg.ui.nodata_spinBox_4.value()
						else:
							NoDataValue = cfg.NoDataVal
						if extentList is None:
							if cfg.ui.intersection_checkBox.isChecked() is True:
								vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "Yes")
							elif cfg.ui.extent_checkBox.isChecked() is True:
								if extentRaster is None:
									extRaster = cfg.ui.raster_extent_combo.currentText()
								else:
									extRaster = extentRaster
								if extRaster == cfg.mapExtent:
									rectangle = cfg.cnvs.extent()
									tLX, tLY, lRX, lRY = rectangle.xMinimum(), rectangle.yMaximum(), rectangle.xMaximum(), rectangle.yMinimum()
								elif extRaster == cfg.pixelExtent:
									tLX, tLY, lRX, lRY = extentList[0], extentList[1], extentList[2], extentList[3]
								else:
									tLX, tLY, lRX, lRY, pS = cfg.utls.imageInformationSize(extRaster)
								if tLX is None:
									if outFile is None:
										cfg.uiUtls.removeProgressBar()
										cfg.cnvs.setRenderFlag(True)
									return "No"
								vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "No", [float(tLX), float(tLY), float(lRX), float(lRY), "Yes"])
							else:
								vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "No")
						else:
							tLX, tLY, lRX, lRY = extentList[0], extentList[1], extentList[2], extentList[3]
							vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "No", [float(tLX), float(tLY), float(lRX), float(lRY), "Yes"])
						# open input with GDAL
						rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
						if rD is None:
							cfg.mx.msg4()
							self.rasterBandName()
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " None raster")
							if outFile is None:
								cfg.uiUtls.removeProgressBar()
								cfg.cnvs.setRenderFlag(True)
							return "No"
						# band list
						bL = cfg.utls.readAllBandsFromRaster(rD)
						# output rasters
						oM = []
						oM.append(tPMD2)
						oMR = cfg.utls.createRasterFromReference(rD, 1, oM, NoDataValue, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
						o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.bandCalculation, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "calculation " + str(it), "Yes")
						# close GDAL rasters
						for b in range(0, len(oMR)):
							oMR[b] = None
						for b in range(0, len(bL)):
							bL[b] = None
						rD = None
						if o != "No":
							if cfg.rasterCompression != "No":
								try:
									cfg.utls.GDALCopyRaster(tPMD2, out, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
									cfg.osSCP.remove(tPMD2)
								except Exception, err:
									cfg.shutilSCP.copy(tPMD2, out)
									cfg.osSCP.remove(tPMD2)
									# logger
									if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							else:
								cfg.shutilSCP.copy(tPMD2, out)
								cfg.osSCP.remove(tPMD2)
							if quiet == "No":
								r = cfg.utls.addRasterLayer(out, cfg.osSCP.path.basename(out))
								try:
									cfg.utls.rasterSymbolSingleBandGray(r)
								except Exception, err:
									# logger
									if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						it = it + 1
				cfg.uiUtls.updateBar(100)
				if outFile is None:
					cfg.utls.finishSound()
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band calculation ended")
				
	# text changed
	def textChanged(self):
		if cfg.bandCalcIndex == 0:
			expression = " " + cfg.ui.plainTextEdit_calc.toPlainText() + " "
			self.checkExpression(expression)
		elif cfg.bandCalcIndex == 1:
			expression = cfg.bCalc.decisionRulesExpression()
			check = self.checkExpression(expression)
			tW = cfg.ui.decision_rules_tableWidget
			if len(check) > 0:
				tW.setStyleSheet("color : green")
			else:
				tW.setStyleSheet("color : red")
			
	# check the expression and return it
	def checkExpression(self, expression):
		tW = cfg.ui.tableWidget_band_calc
		v = tW.rowCount()
		name = []		
		nameList = []		
		cfg.ui.plainTextEdit_calc.setStyleSheet("color : red")
		for x in range(0, v):
			name.append('"' + tW.item(x, 0).text() + '"')
			name.append('"' + tW.item(x, 1).text() + '"')
			nameList.append(['"' + tW.item(x, 0).text() + '"', '"' + tW.item(x, 1).text() + '"'])
		ex = []
		if expression is None:
			checkO = "No"
		else:
			e = expression.rstrip().split("\n")
			checkO = "Yes"
			for nf in e:
				f = nf.split("@")[0]
				try:
					nm = nf.split("@")[1]
				except:
					nm = None
				# replace NoData values
				f = cfg.utls.replaceNoDataValues(f, nameList)
				oldF = f
				check = "Yes"
				# create function
				for i in name:
					f = f.replace(i, " rasterSCPArrayfunctionBand ")
				if f == oldF:
					check = "No"
					checkO = "No"
				else:
					# replace numpy operators
					f = cfg.utls.replaceNumpyOperators(f)
					rasterSCPArrayfunctionBand = cfg.np.arange(9).reshape(3, 3)
					try:
						o = eval(f)
						cfg.ui.plainTextEdit_calc.setStyleSheet("color : green")
						if cfg.bandCalcIndex == 0:
							self.expressionButton = True
						elif cfg.bandCalcIndex == 1:
							self.decisionRulesButton = True
						cfg.ui.toolButton_calculate.setEnabled(True)
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						check = "No"
						checkO = "No"
				if check == "Yes":
					ex.append([oldF, nm])
		if checkO == "No":
			cfg.ui.plainTextEdit_calc.setStyleSheet("color : red")
			if cfg.bandCalcIndex == 0:
				self.expressionButton = False
			elif cfg.bandCalcIndex == 1:
				self.decisionRulesButton = False
			cfg.ui.toolButton_calculate.setEnabled(False)
		return ex
			
	# extent checkbox
	def extentCheckbox(self):
		if cfg.ui.extent_checkBox.isChecked() is True:
			if cfg.ui.intersection_checkBox.isChecked() is True:
				cfg.ui.intersection_checkBox.blockSignals(True)
				cfg.ui.intersection_checkBox.setCheckState(0)
				cfg.ui.intersection_checkBox.blockSignals(False)
			
	# intersection checkbox
	def intersectionCheckbox(self):
		if cfg.ui.intersection_checkBox.isChecked() is True:
			if cfg.ui.extent_checkBox.isChecked() is True:
				cfg.ui.extent_checkBox.blockSignals(True)
				cfg.ui.extent_checkBox.setCheckState(0)
				cfg.ui.extent_checkBox.blockSignals(False)
		
	# double click
	def doubleClick(self, index):
		l = cfg.ui.tableWidget_band_calc
		k = l.item(index.row(), index.column()).text()
		if cfg.bandCalcIndex == 0:
			cursor = cfg.ui.plainTextEdit_calc.textCursor()
			cursor.insertText('"' + k + '"')
			cfg.ui.plainTextEdit_calc.setFocus()
		elif cfg.bandCalcIndex == 1:
			tW = cfg.ui.decision_rules_tableWidget
			# list of items
			iR  = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			v = list(set(iR))
			if len(v) > 0:
				tW.blockSignals(True)
				for i in v:
					try:
						tr = tW.item(i, 1).text()
						cfg.utls.setTableItem(tW, i, 1, str(tr + ' "' + k + '" '))
					except:
						tW.blockSignals(False)
						return "No"
				tW.blockSignals(False)
				e = cfg.bCalc.decisionRulesExpression()
				check = self.checkExpression(e)
				if len(check) > 0:
					tW.setStyleSheet("color : green")
				else:
					tW.setStyleSheet("color : red")
				
	# move up selected rules
	def moveUpRule(self):
		tW = cfg.ui.decision_rules_tableWidget
		c = tW.rowCount()
		s = tW.selectedItems()
		# create list for new selection after move
		ns  = []
		for i in range (0, len(s)):
			ns.append(s[i].row() - 1)
		try:
			for b in range(0, c):
				if tW.item(b, 0).isSelected() or tW.item(b, 1).isSelected():
					bNU = tW.item(b, 0).text()
					bND = tW.item(b - 1, 0).text()
					tW.item(b, 0).setText(str(bND))
					tW.item(b - 1, 0).setText(str(bNU))	
					brNU = tW.item(b, 1).text()
					brND = tW.item(b - 1, 1).text()
					tW.item(b, 1).setText(str(brND))
					tW.item(b - 1, 1).setText(str(brNU))					
			tW.clearSelection()
			v = list(set(ns))
			cfg.utls.selectRowsInTable(tW, v)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			tW.clearSelection()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
								
	# move down selected rules
	def moveDownRule(self):
		tW = cfg.ui.decision_rules_tableWidget
		c = tW.rowCount()
		s = tW.selectedItems()
		# create list for new selection after move
		ns  = []
		for i in range (0, len(s)):
			ns.append(s[i].row() + 1)
		try:
			for b in reversed(range(0, c)):
				if tW.item(b, 0).isSelected() or tW.item(b, 1).isSelected():
					bNU = tW.item(b, 0).text()
					bND = tW.item(b + 1, 0).text()
					tW.item(b, 0).setText(str(bND))
					tW.item(b + 1, 0).setText(str(bNU))	
					brNU = tW.item(b, 1).text()
					brND = tW.item(b + 1, 1).text()
					tW.item(b, 1).setText(str(brND))
					tW.item(b + 1, 1).setText(str(brNU))
			tW.clearSelection()
			v = list(set(ns))
			cfg.utls.selectRowsInTable(tW, v)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			tW.clearSelection()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
				
				
	# buttons
	def insertButton(self, text):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(text)

	def buttonPlus(self):
		cfg.bCalc.insertButton(" + ")

	def buttonMinus(self):
		cfg.bCalc.insertButton(" - ")	
		
	def buttonProduct(self):
		cfg.bCalc.insertButton(" * ")

	def buttonRatio(self):
		cfg.bCalc.insertButton(" / ")
		
	def buttonPower(self):
		cfg.bCalc.insertButton("^")
						
	def buttonSQRT(self):
		cfg.bCalc.insertButton("sqrt(")		
		
	def buttonLbracket(self):
		cfg.bCalc.insertButton("(")
				
	def buttonRbracket(self):
		cfg.bCalc.insertButton(")")		
						
	def buttonGreater(self):
		cfg.bCalc.insertButton(" > ")		
								
	def buttonLower(self):
		cfg.bCalc.insertButton(" < ")		
								
	def buttonUnequal(self):
		cfg.bCalc.insertButton(" != ")		
								
	def buttonEqual(self):
		cfg.bCalc.insertButton(" == ")		
		
	def buttonSin(self):
		cfg.bCalc.insertButton(" sin(")
			
	def buttonASin(self):
		cfg.bCalc.insertButton(" asin(")
					
	def buttonCos(self):
		cfg.bCalc.insertButton(" cos(")
							
	def buttonACos(self):
		cfg.bCalc.insertButton(" acos(")
		
	def buttonTan(self):
		cfg.bCalc.insertButton(" tan(")		
		
	def buttonATan(self):
		cfg.bCalc.insertButton(" atan(")
			
	def buttonExp(self):
		cfg.bCalc.insertButton(" exp(")
					
	def buttonNoDataVal(self):
		cfg.bCalc.insertButton(" nodata(")
		
	def buttonNpWhere(self):
		cfg.bCalc.insertButton(" where(")

	def buttonLog(self):
		cfg.bCalc.insertButton(" ln(")

	def buttonPi(self):
		cfg.bCalc.insertButton(" pi ")
		