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

class BandCalcTab:

	def __init__(self):
		self.expressionButton = False
		self.decisionRulesButton = False
		
	# toolbox changed
	def tabChanged(self, index):
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
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Clear rules"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the rules?"))
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
		file = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a text file of rules"), "", "txt (*.txt)")
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
			file = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save the rules to file"), "", "*.txt", "txt")
			if file is not False:
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
	def rasterBandName(self, bandSetNumber = None):
		if bandSetNumber is None or bandSetNumber is False:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		cfg.utls.refreshRasterExtent()
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		l = cfg.ui.tableWidget_band_calc
		l.setSortingEnabled(False)
		cfg.utls.clearTable(l)
		check = "Yes"
		b = 0
		for x in sorted(ls, key=lambda c: c.name()):
			if x.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer and x.bandCount() == 1:
				# band name
				bN = x.name()
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1
		# test empty band set
		try:
			cfg.bandSetsList[bandSetNumber][0]
		except:
			return
		if cfg.bandSetsList[bandSetNumber][0] == "Yes":
			c = 1
			for x in range(0, len(cfg.bandSetsList[bandSetNumber][3])):
				# band name
				bN = cfg.variableBandsetName + "#b" + str(c)
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1
				c = c + 1
		else:
			try:
				r = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], "Yes")
				iR = cfg.utls.layerSource(r)
			except:
				check = "No"
			if check == "Yes":
				x = cfg.utls.getNumberBandRaster(iR)
				for c in range(1, x + 1):
					# band name
					bN = cfg.variableBandsetName + "#b" + str(c)
					# Add band to table
					l.insertRow(b)
					cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
					cfg.utls.addTableItem(l, bN, b, 1, "No")
					b = b + 1
		if check == "Yes":
			if len(cfg.bandSetsList[bandSetNumber][3]) > 0:
				cfg.utls.findBandNumber()
			if cfg.BLUEBand is not None:
				# band name
				bN = cfg.variableBlueName
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1
			if cfg.GREENBand is not None:
				# band name
				bN = cfg.variableGreenName
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
			if cfg.SWIR1Band is not None:
				# band name
				bN = cfg.variableSWIR1Name
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1	
			if cfg.SWIR2Band is not None:
				# band name
				bN = cfg.variableSWIR2Name
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, "No")
				cfg.utls.addTableItem(l, bN, b, 1, "No")
				b = b + 1		
		cfg.bCalc.textChanged()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster band name checklist created")
		
	
	# set indices combo
	def setIndices(self):
		pT = cfg.ui.plainTextEdit_calc
		text = pT.toPlainText()
		if len(text) > 0:
			space = "\n"
		else:
			space = ""
		for key in cfg.expressionDict:
			if cfg.ui.band_set_calculation_combo.currentText() == key:
				pT.setPlainText(text + space + cfg.expressionDict[key])
		
	# import expressions from file
	def importExpressionList(self):
		funcFile = cfg.utls.getOpenFileName(None , "Select an expression file", "", "TXT (*.txt)")
		if len(funcFile) > 0:
			try:
				f = open(funcFile)
				sep = ";"
				if cfg.osSCP.path.isfile(funcFile):
					cfg.expressionListBC = []
					lines = f.readlines()
					tW = cfg.ui.point_tableWidget
					if len(lines) > 0:
						for b in lines:
							try:
								v = b.split(sep)
								# name and expression
								n = v[0]
								e = v[1].strip()
								cfg.expressionListBC.append([n, e])
							except:
								pass
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " expressions imported")
						# save in registry
						cfg.utls.setQGISRegSetting(cfg.regExpressionListBC, cfg.expressionListBC)
						cfg.bCalc.createExpressionList(cfg.expressionListBC)
					else:
						# save in registry
						cfg.utls.setQGISRegSetting(cfg.regExpressionListBC, cfg.expressionListBCbase)
						cfg.bCalc.createExpressionList(cfg.expressionListBCbase)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				
	# create expression list
	def createExpressionList(self, expressionList):
		cfg.ui.band_set_calculation_combo.clear()
		cfg.ui.band_set_calculation_combo.addItem(" ")
		cfg.expressionDict = {}
		try:
			for i in expressionList:
				try:
					n = i[0]
					e = i[1]
					cfg.ui.band_set_calculation_combo.addItem(n)
					cfg.expressionDict[n] = e
				except:
					pass
		except:
			for i in cfg.expressionListBCbase:
				try:
					n = i[0]
					e = i[1]
					cfg.ui.band_set_calculation_combo.addItem(n)
					cfg.expressionDict[n] = e
				except:
					pass
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " expressions created")
			
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
	def calculate(self, outFile = None, batch = "No", expressionString = None, extentRaster = None, extentList = None, quiet = "No", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"	
		if batch == "No":
			pass
		else:
			self.rasterBandName(bandSetNumber)
		tW = cfg.ui.tableWidget_band_calc
		c = tW.rowCount()
		if c > 0:
			if outFile is None:
				# band calc
				if cfg.bandCalcIndex == 0:
					textCount = cfg.ui.plainTextEdit_calc.blockCount()
					if textCount > 1:
						outF = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
						if len(outF) > 0:
							outF = outF + "/" + cfg.calcRasterNm + ".tif"
						else:
							return
					else:
						try:
							nm = cfg.ui.plainTextEdit_calc.toPlainText().split("@")[1]
							outF = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
							if len(outF) > 0:
								outF = outF + "/" + cfg.calcRasterNm + ".tif"
							else:
								return
						except:
							outF = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster output"), "", "*.tif", "tif")
				# decision rules
				elif cfg.bandCalcIndex == 1:
					outF = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster output"), "", "*.tif", "tif")
			else:
				outF = outFile
			if outF is not False:
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
						eN = self.checkOutputName(eM[1])
					except Exception as err:
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
								out = cfg.osSCP.path.dirname(outF) + "/" + n
							elif eN is None and len(check) > 1:
								out = cfg.osSCP.path.dirname(outF) + "/" + n.replace('.tif', '') + "_" + str(it) + ".tif"
							else:
								out = cfg.osSCP.path.dirname(outF) + "/" + n
						else:
							if eN is None and len(check) == 1:
								out = cfg.osSCP.path.dirname(outF) + "/" + n + ".tif"
							elif eN is None and len(check) > 1:
								out = cfg.osSCP.path.dirname(outF) + "/" + n + "_" + str(it) + ".tif"
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
							if str('"' +  bV +'"') in e or str('"' + bN +'"') in e:
								variableList.append(['"' + bV + '"', '"' + bN + '"'])
								if cfg.variableBandsetName in bN:
									bandNumber = bN.split("#b")
									if cfg.bandSetsList[bandSetNumber][0] == "Yes":
										bPath = cfg.bndSetLst[int(bandNumber[1]) - 1]
										bandNumberList.append(1)
										bList.append(bPath)
									else:
										i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], "Yes")
										try:
											bPath = cfg.utls.layerSource(i)
										except Exception as err:
											cfg.mx.msg4()
											self.rasterBandName(bandSetNumber)
											# logger
											cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
											if outFile is None:
												cfg.uiUtls.removeProgressBar()
												cfg.cnvs.setRenderFlag(True)
												return "No"
										bandNumberList.append(int(bandNumber[1]))
										bList.append(bPath)
								elif cfg.variableBlueName in bN or cfg.variableRedName in bN or cfg.variableNIRName in bN or cfg.variableGreenName in bN or cfg.variableSWIR1Name in bN or cfg.variableSWIR2Name in bN :
									if bN == cfg.variableRedName :
										bandNumber = ["", cfg.REDBand]
									elif bN == cfg.variableNIRName :
										bandNumber = ["", cfg.NIRBand]
									elif bN == cfg.variableBlueName :
										bandNumber = ["", cfg.BLUEBand]
									elif bN == cfg.variableGreenName :
										bandNumber = ["", cfg.GREENBand]
									elif bN == cfg.variableSWIR1Name :
										bandNumber = ["", cfg.SWIR1Band]
									elif bN == cfg.variableSWIR2Name :
										bandNumber = ["", cfg.SWIR2Band]
									else:
										cfg.mx.msg4()
										if outFile is None:
											cfg.uiUtls.removeProgressBar()
											cfg.cnvs.setRenderFlag(True)
											return "No"
									if cfg.bandSetsList[bandSetNumber][0] == "Yes":
										bPath = cfg.bndSetLst[int(bandNumber[1]) - 1]
										bandNumberList.append(1)
										bList.append(bPath)
									else:
										i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], "Yes")
										try:
											bPath = cfg.utls.layerSource(i)
										except Exception as err:
											cfg.mx.msg4()
											self.rasterBandName(bandSetNumber)
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
										bPath = cfg.utls.layerSource(i)
									except Exception as err:
										cfg.mx.msg4()
										self.rasterBandName(bandSetNumber)
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
						except Exception as err:
							cfg.mx.msg4()
							self.rasterBandName(bandSetNumber)
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
								vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "Yes")
							elif cfg.ui.extent_checkBox.isChecked() is True:
								# raster resolution
								xyRes = None
								if extentRaster is None:
									extRaster = cfg.ui.raster_extent_combo.currentText()
								else:
									extRaster = extentRaster
								if extRaster == cfg.mapExtent:
									rectangle = cfg.cnvs.extent()
									tLX, tLY, lRX, lRY = rectangle.xMinimum(), rectangle.yMaximum(), rectangle.xMaximum(), rectangle.yMinimum()
									pCrs = cfg.utls.getQGISCrs()
									# check projection 
									if cfg.bandSetsList[bandSetNumber][0] == "Yes":
										try:
											imageName = cfg.bandSetsList[bandSetNumber][3][0]
										except:
											imageName = variableList[0][1][1:-1]
									else:
										try:
											imageName = cfg.bandSetsList[bandSetNumber][8]
										except:
											imageName = variableList[0][1][1:-1]
									# image CRS
									bN0 = cfg.utls.selectLayerbyName(imageName, "Yes")
									iCrs = cfg.utls.getCrs(bN0)
									if iCrs is None:
										iCrs = pCrs
									# projection of input point from project's crs to raster's crs
									if pCrs != iCrs:
										tLPoint = cfg.qgisCoreSCP.QgsPointXY(tLX, tLY)
										lRPoint = cfg.qgisCoreSCP.QgsPointXY(lRX, lRY)
										try:
											tLPoint = cfg.utls.projectPointCoordinates(tLPoint, pCrs, iCrs)
											lRPoint = cfg.utls.projectPointCoordinates(lRPoint, pCrs, iCrs)
											if tLPoint is False or lRPoint is False:
												cfg.utls.setQGISCrs(iCrs)
												cfg.uiUtls.removeProgressBar()
												cfg.cnvs.setRenderFlag(True)
												return "No"
											else:
												tLX = tLPoint.x()
												tLY = tLPoint.y()
												lRX = lRPoint.x()
												lRY = lRPoint.y()
										except Exception as err:
											# logger
											cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
											cfg.uiUtls.removeProgressBar()
											cfg.cnvs.setRenderFlag(True)
											return "No"
								elif extRaster == cfg.pixelExtent:
									tLX, tLY, lRX, lRY = extentList[0], extentList[1], extentList[2], extentList[3]
								else:
									tLX, tLY, lRX, lRY, pSX, pSY = cfg.utls.imageInformationSize(extRaster)
									if cfg.ui.align_radioButton.isChecked():
										xyRes = [pSX, pSY, tLX, tLY, lRX, lRY]
										# add extent raster to virtual raster list
										i = cfg.utls.selectLayerbyName(extRaster, "Yes")
										try:
											bPath = cfg.utls.layerSource(i)
										except Exception as err:
											cfg.mx.msg4()
											self.rasterBandName(bandSetNumber)
											# logger
											cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
											if outFile is None:
												cfg.uiUtls.removeProgressBar()
												cfg.cnvs.setRenderFlag(True)
												return "No"
										bandNumberList.append(1)
										bList.append(bPath)
										
								if tLX is None:
									if outFile is None:
										cfg.uiUtls.removeProgressBar()
										cfg.cnvs.setRenderFlag(True)
									return "No"
								vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "No", [float(tLX), float(tLY), float(lRX), float(lRY), "Yes"], xyRes)
							else:
								vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "No")
						else:
							tLX, tLY, lRX, lRY = extentList[0], extentList[1], extentList[2], extentList[3]
							vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "No", [float(tLX), float(tLY), float(lRX), float(lRY), "Yes"])
						# open input with GDAL
						rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
						if rD is None:
							cfg.mx.msg4()
							self.rasterBandName(bandSetNumber)
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
									if cfg.osSCP.path.isfile(out):
										pass
									else:
										try:
											cfg.shutilSCP.copy(tPMD2, out)
										except Exception as err:
											# logger
											if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
									cfg.osSCP.remove(tPMD2)
								except Exception as err:
									try:
										cfg.shutilSCP.copy(tPMD2, out)
									except Exception as err:
										# logger
										if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
									cfg.osSCP.remove(tPMD2)
									# logger
									if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							else:
								try:
									cfg.shutilSCP.copy(tPMD2, out)
								except Exception as err:
									# logger
									if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								cfg.osSCP.remove(tPMD2)
							if quiet == "No":
								r =cfg.utls.addRasterLayer(out, cfg.osSCP.path.basename(out))
								try:
									cfg.utls.rasterSymbolSingleBandGray(r)
								except Exception as err:
									# logger
									if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						it = it + 1
				cfg.uiUtls.updateBar(100)
				if batch == "No":
					pass
				else:
					self.rasterBandName(bandSetNumber)
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
			
	# check the output Name and return it
	def checkOutputName(self, outputName):
		try:
			outputName = outputName.replace(cfg.variableOutputNameBandset, cfg.osSCP.path.basename(cfg.bndSetLst[0]).rpartition(".")[0][:-1])
		except:
			pass
		try:
			dT = cfg.utls.getTime()
			outputName = outputName.replace(cfg.variableOutputNameDate, dT)
		except:
			pass
		return outputName
		
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
					except Exception as err:
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
		except Exception as err:
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
			for b in reversed(list(range(0, c))):
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
		except Exception as err:
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
		