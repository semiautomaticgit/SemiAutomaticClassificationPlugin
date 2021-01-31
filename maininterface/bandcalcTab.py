# -*- coding: utf-8 -*-
'''
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright		: (C) 2012-2021 by Luca Congedo
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

'''



cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

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
		cfg.utls.addTableItem(tW, '', c, 1)
		tW.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "added row " + str(c + 1))
		e = cfg.bCalc.decisionRulesExpression()
		check = self.checkExpression(e)
		if len(check) > 0:
			tW.setStyleSheet('color : green')
		else:
			tW.setStyleSheet('color : red')	
		
	# remove row
	def removeHighlightedRule(self):
		tW = cfg.ui.decision_rules_tableWidget
		cfg.utls.removeRowsFromTable(tW)
		e = cfg.bCalc.decisionRulesExpression()
		check = self.checkExpression(e)
		if len(check) > 0:
			tW.setStyleSheet('color : green')
		else:
			tW.setStyleSheet('color : red')
			
	# clear the rules
	def clearRulesAction(self):
		self.clearRules()
		expression = cfg.bCalc.decisionRulesExpression()
		check = self.checkExpression(expression)
		tW = cfg.ui.decision_rules_tableWidget
		if len(check) > 0:
			tW.setStyleSheet('color : green')
		else:
			tW.setStyleSheet('color : red')
		
	# clear the rules
	def clearRules(self, question = 'Yes'):
		if question == 'Yes':
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Clear rules'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Are you sure you want to clear the rules?'))
		else:
			a = 'Yes'
		if a == 'Yes':
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
			value = 'No'
		try:
			t = tW.item(row, 1).text()
		except:
			tW.setStyleSheet('color : red')
			self.decisionRulesButton = False
			cfg.ui.toolButton_calculate.setEnabled(self.decisionRulesButton)
			return 'No'
		e = cfg.bCalc.decisionRulesExpression()
		check = self.checkExpression(e)
		if len(check) > 0:
			tW.setStyleSheet('color : green')
		else:
			tW.setStyleSheet('color : red')
				
	# create decision rule expression
	def decisionRulesExpression(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		tW = cfg.ui.decision_rules_tableWidget
		NoDataValue = cfg.ui.nodata_spinBox_13.value()
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
					return 'No'
				tSplit = t.split(';')
				e = 'cfg.np.where( '
				for b in tSplit:
					if len(b) > 0:
						e = e + '(' + b + ') & '
				e = e[:-4] + '), ' + str(value) + ',' + 'str(NoDataValue)' + ')'
				try:
					e = w.replace('str(NoDataValue)', str(e))
				except:
					pass
			e = e.replace('str(NoDataValue)', str(NoDataValue))
			return e
		
	# import rules from text file
	def importRules(self):
		file = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a text file of rules'), '', 'txt (*.txt)')
		if len(file) > 0:
			self.clearRules('No')
			tW = cfg.ui.decision_rules_tableWidget
			text = open(file, 'r')
			lines = text.readlines()
			tW.blockSignals(True)
			for b in lines:
				v = b.split(';', 1)
				# add item to table
				c = tW.rowCount()
				# add list items to table
				tW.setRowCount(c + 1)
				try:
					cfg.utls.addTableItem(tW, v[0].strip(), c, 0)
					cfg.utls.addTableItem(tW, v[1].strip(), c, 1)
				except:
					tW.blockSignals(False)
					self.clearRules('No')
					cfg.mx.msgErr19()
					return 'No'
			tW.blockSignals(False)
			expression = cfg.bCalc.decisionRulesExpression()
			check = self.checkExpression(expression)
			if len(check) > 0:
				tW.setStyleSheet('color : green')
			else:
				tW.setStyleSheet('color : red')
				
	# export rules to text file
	def exportRules(self):
		tW = cfg.ui.decision_rules_tableWidget
		c = tW.rowCount()
		if c > 0:
			file = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save the rules to file'), '', '*.txt', 'txt')
			if file is not False:
				if file.lower().endswith('.txt'):
					pass
				else:
					file = file + '.txt'
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
			e = ''
			for row in range(0, c):
				try:
					value = tW.item(row, 0).text()
					t = tW.item(row, 1).text()
				except:
					return 'No'
				e = e + value + ';' + t + '\n'
			return e
					
	# Set output name table
	def outputNameTable(self, nameList = None):
		if nameList is None:
			pass
		l = cfg.ui.tableWidget_band_calc
		l.blockSignals(True)
		l.setSortingEnabled(False)
		c = l.rowCount()
		# remove items
		for i in reversed(range(0, c)):
			if cfg.variableOutName in l.item(i, 0).text():
				l.removeRow(i)
			else:
				break
			
		b = l.rowCount()
		for bN in nameList:
			# Add band to table
			l.insertRow(b)
			cfg.utls.addTableItem(l, cfg.variableOutName + str(b + 1), b, 0, 'No')
			cfg.utls.addTableItem(l, bN[0].replace('"', ''), b, 1, 'No')
			b = b + 1
		l.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " output name table created")
		
	# Set raster band table
	def rasterBandName(self, bandSetNumber = None):
		if bandSetNumber is None or bandSetNumber is False:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		cfg.utls.refreshRasterExtent()
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		l = cfg.ui.tableWidget_band_calc
		l.setSortingEnabled(False)
		cfg.utls.clearTable(l)
		check = 'Yes'
		b = 0
		for x in sorted(ls, key=lambda c: c.name()):
			if x.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer and x.bandCount() == 1:
				# band name
				bN = x.name()
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1
		# test empty band set
		try:
			cfg.bandSetsList[bandSetNumber][0]
		except:
			return
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			if len(cfg.bandSetsList[bandSetNumber][3]) > 0 :
				# variable band set
				bN = cfg.variableBandsetName + '#b*'
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1
			for x in range(0, len(cfg.bandSetsList[bandSetNumber][3])):
				# band name
				bN = cfg.variableBandsetName + '#b' + str(x + 1)
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1
		else:
			try:
				r = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
				iR = cfg.utls.layerSource(r)
			except:
				check = 'No'
			if check == 'Yes':
				x = cfg.utls.getNumberBandRaster(iR)
				for c in range(1, x + 1):
					# band name
					bN = cfg.variableBandsetName + '#b' + str(c)
					# Add band to table
					l.insertRow(b)
					cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
					cfg.utls.addTableItem(l, bN, b, 1, 'No')
					b = b + 1
		if check == 'Yes':
			bNList = []
			for bNum in range(0, len(cfg.bandSetsList)):
				if len(cfg.bandSetsList[bNum][3]) > 0 :
					for x in range(0, len(cfg.bandSetsList[bNum][3])):
						# band name
						bN = cfg.variableBandsetName + str(bNum + 1) + 'b' + str(x + 1)
						# Add band to table
						l.insertRow(b)
						cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
						cfg.utls.addTableItem(l, bN, b, 1, 'No')
						b = b + 1
						# band name
						bN = cfg.variableBandsetName + '*b' + str(x + 1)
						if bN not in bNList:
							bNList.append(bN)
					# variable band set
					bN = cfg.variableBandsetName + str(bNum + 1) + 'b*'
					# Add band to table
					l.insertRow(b)
					cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
					cfg.utls.addTableItem(l, bN, b, 1, 'No')
					b = b + 1
			for bN in bNList:
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1
			if len(cfg.bandSetsList[bandSetNumber][3]) > 0:
				cfg.utls.findBandNumber()
			if cfg.BLUEBand is not None:
				# band name
				bN = cfg.variableBlueName
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1
			if cfg.GREENBand is not None:
				# band name
				bN = cfg.variableGreenName
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1	
			if cfg.REDBand is not None:
				# band name
				bN = cfg.variableRedName
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1
			if cfg.NIRBand is not None:
				# band name
				bN = cfg.variableNIRName
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1			
			if cfg.SWIR1Band is not None:
				# band name
				bN = cfg.variableSWIR1Name
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1	
			if cfg.SWIR2Band is not None:
				# band name
				bN = cfg.variableSWIR2Name
				# Add band to table
				l.insertRow(b)
				cfg.utls.addTableItem(l, cfg.variableName + str(b + 1), b, 0, 'No')
				cfg.utls.addTableItem(l, bN, b, 1, 'No')
				b = b + 1		
		cfg.bCalc.textChanged()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " raster band name checklist created")
		
	# set raster type
	def setRasterType(self):
		cfg.rasterBandCalcType = cfg.ui.raster_type_combo.currentText()
		
	# import expressions from file
	def importExpressionList(self):
		funcFile = cfg.utls.getOpenFileName(None , 'Select an expression file', '', 'TXT (*.txt)')
		if len(funcFile) > 0:
			try:
				f = open(funcFile)
				sep = ';'
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
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " expressions imported")
						# save in registry
						cfg.utls.setQGISRegSetting(cfg.regExpressionListBC, cfg.expressionListBC)
						cfg.bCalc.createExpressionList(cfg.expressionListBC)
					else:
						# save in registry
						lbase=[]
						cfg.utls.setQGISRegSetting(cfg.regExpressionListBC, str(lbase))
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				
	# create expression list
	def createExpressionList(self, expressionList):
		cfg.utls.clearTable(cfg.ui.band_calc_function_tableWidget)
		cfg.bCalc.addFunctionsToTable(cfg.bandCalcFunctionNames)
		cfg.bCalc.addFunctionsToTable(expressionList)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " expressions created")
			
	# add function list to table
	def addFunctionsToTable(self, functionList):
		if functionList is not None:
			tW = cfg.ui.band_calc_function_tableWidget
			for i in functionList:
				tW.blockSignals(True)
				# count table rows
				c = tW.rowCount()
				try:
					# name of item of list
					itN = i[0]
					itF = i[1]
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, itN, c, 0)
				except:
					itN = i[0]
					# add list items to table
					tW.setRowCount(c + 1)
					co = cfg.QtGuiSCP.QColor(200, 200, 200)
					cfg.utls.addTableItem(tW, itN, c, 0, 'No', co, bold = 'Yes')
				tW.blockSignals(False)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
				
	# set function
	def setFunction(self, index):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		tW = cfg.ui.band_calc_function_tableWidget
		nm = tW.item(index.row(), 0).text()
		text = self.replaceFunctionNames(nm)
		if text != 'No':
			cursor.insertHtml(' ' + text)
		
	# replace function names
	def replaceFunctionNames(self, name):
		if cfg.expressionListBC is not None:
			cF =  cfg.bandCalcFunctionNames + cfg.expressionListBC
		else:
			cF = cfg.bandCalcFunctionNames
		for i in cF:
			if name == i[0]:
				try:
					return i[1]
				except:
					return 'No'
		return 'No'
		
	# calculate button
	def calculateButton(self):
		# band calc
		if cfg.bandCalcIndex == 0:
			cfg.bCalc.calculate()
		# decision rules
		elif cfg.bandCalcIndex == 1:
			e = cfg.bCalc.decisionRulesExpression()
			cfg.bCalc.calculate(None, 'No', e)
		
	# calculate
	def calculate(self, outFile = None, batch = 'No', expressionString = None, extentRaster = None, extentList = None, inputNoDataAsValue = None, useNoDataValue = None,  outputNoData = None, rasterDataType = None, useScale = None, useOffset = None, align = None, extentIntersection = None, extentSameAs = None, quiet = 'No', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'	
		if batch == 'No':
			pass
		else:
			self.rasterBandName(bandSetNumber)
		tW = cfg.ui.tableWidget_band_calc
		c = tW.rowCount()
		if c > 0:
			if outFile is None and batch == 'No':
				# band calc
				if cfg.bandCalcIndex == 0:
					textCount = cfg.ui.plainTextEdit_calc.blockCount()
					# multiple lines
					if textCount > 1:
						outF = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
						if len(outF) > 0:
							outF = outF + '/' + cfg.calcRasterNm + '.tif'
						else:
							return
					# one line
					else:
						try:
							# output name defined
							nm = cfg.ui.plainTextEdit_calc.toPlainText().split('@')[1]
							outF = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
							if len(outF) > 0:
								outF = outF + '/' + cfg.calcRasterNm + '.tif'
							else:
								return
						except:
							outF = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save raster output'), '', 'TIF file (*.tif);;VRT file (*.vrt)', None)
				# decision rules
				elif cfg.bandCalcIndex == 1:
					outF = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save raster output'), '', 'TIF file (*.tif);;VRT file (*.vrt)', None)
			else:
				outF = outFile
			if outF is not False:
				if outFile is None:
					cfg.uiUtls.addProgressBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Band calc'), message = '')
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' band calculation started')
				if expressionString is None:
					expression = ' ' + cfg.ui.plainTextEdit_calc.toPlainText() + ' '
				else:
					expression = expressionString
				check = self.checkExpression(expression)
				if check == 'No':
					cfg.mx.msgErr36()
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' check No')
					if outFile is None:
						cfg.uiUtls.removeProgressBar()
						return 'No'
				cfg.cnvs.setRenderFlag(False)
				it = 1
				nCh = len(check)
				for eM in check:
					c = tW.rowCount()
					e = eM[0]
					eN = eM[1]
					ePath = eM[2]
					if batch == 'No':
						cfg.uiUtls.updateBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Band calc') + ' [' + str(it) + '/' + str(nCh) + '] ' + e, message = '')
					# do not replace expression
					expe = None
                    # add to band set
					try:
						eNBS = eN.split('%')[1]
						eN = eN.split('%')[0]
					except:
						eNBS = None
					# virtual raster
					vrtR = 'No'
					dCheck = 'Yes'
					if dCheck == 'Yes':
						if eN is None:
							n = cfg.utls.fileName(outF)
						else:
							n = eN
						if ePath is not None:
							outF = ePath + '/' + n
							if ePath == cfg.tmpDir and cfg.outTempRastFormat == 'VRT':
								vrtR = 'Yes'
						if n.lower().endswith('.tif'):
							if eN is None and len(check) == 1:
								out = cfg.osSCP.path.dirname(outF) + '/' + n
							elif eN is None and len(check) > 1:
								out = cfg.osSCP.path.dirname(outF) + '/' + n.replace('.tif', '') + '_' + str(it) + '.tif'
							else:
								out = cfg.osSCP.path.dirname(outF) + '/' + n
						elif n.lower().endswith('.vrt'):
							vrtR = 'Yes'
							if eN is None and len(check) == 1:
								out = cfg.osSCP.path.dirname(outF) + '/' + n
							elif eN is None and len(check) > 1:
								out = cfg.osSCP.path.dirname(outF) + '/' + n.replace('.vrt', '') + '_' + str(it) + '.vrt'
							else:
								out = cfg.osSCP.path.dirname(outF) + '/' + n
						else:
							if vrtR == 'Yes':
								if eN is None and len(check) == 1:
									out = cfg.osSCP.path.dirname(outF) + '/' + n + '.vrt'
								elif eN is None and len(check) > 1:
									out = cfg.osSCP.path.dirname(outF) + '/' + n + '_' + str(it) + '.vrt'
								else:
									out = cfg.osSCP.path.dirname(outF) + '/' + n + '.vrt'
							else:
								if eN is None and len(check) == 1:
									out = cfg.osSCP.path.dirname(outF) + '/' + n + '.tif'
								elif eN is None and len(check) > 1:
									out = cfg.osSCP.path.dirname(outF) + '/' + n + '_' + str(it) + '.tif'
								else:
									out = cfg.osSCP.path.dirname(outF) + '/' + n + '.tif'
						outDir = cfg.osSCP.path.dirname(outF)
						# if function
						if cfg.calcFunctionNm in e:
							nf = e.split(cfg.calcFunctionNm)
							ee = nf[1]
							ee = ee.replace(cfg.FileNm, out)
							ee = ee.replace(cfg.DirNm, outDir)
							for b in range(0, c):
								bV = tW.item(b, 0).text()
								bN = tW.item(b, 1).text()
								if str('"' +  bV +'"') in ee or str('"' + bN +'"') in ee or str('$' +  bV +'$') in ee or str('$' + bN +'$') in ee:
									# do not replace expressions
									eep = ee.split('expression :')
									if len(eep) == 1:
										eep = ee.split('expression:')
									if len(eep) > 1:
										eepd = eep[1].split(';')
										expe = eepd[0]
										ee = ee.replace(expe, cfg.calcVarReplace)
									# variable bandset#b1
									if cfg.variableBandsetName + '#b' in bN:
										bandNumber = int(bN.split('#b')[1])
										if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
											bPath = cfg.bndSetLst[bandNumber - 1]
											ee = ee.replace('"' +  bV + '"', bPath)
											ee = ee.replace('"' +  bN +' "', bPath)
											ee = ee.replace('$' +  bV + '$', "'" +  cfg.bandSetsList[bandSetNumber][3][bandNumber] + "'")
											ee = ee.replace('$' +  bN + '$', "'" +  cfg.bandSetsList[bandSetNumber][3][bandNumber] + "'")
										else:
											i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
											try:
												bPath = cfg.utls.layerSource(i)
												ee = ee.replace('"' +  bV + '"', bPath)
												ee = ee.replace('"' +  bN +' "', bPath)
												ee = ee.replace('$' +  bV + '$', "'" + cfg.bandSetsList[bandSetNumber][8] + "'")
												ee = ee.replace('$' +  bN + '$', "'" + cfg.bandSetsList[bandSetNumber][8] + "'")
											except Exception as err:
												cfg.mx.msg4()
												self.rasterBandName(bandSetNumber)
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'
									# variable bandset1b1
									elif cfg.variableBandsetName in bN:
										bandSetBandNumber = bN.replace(cfg.variableBandsetName, '').split('b')
										bandSetNumberX = int(bandSetBandNumber[0]) - 1
										bandNumX = int(bandSetBandNumber[1]) - 1
										if cfg.bandSetsList[bandSetNumberX][0] == 'Yes':
											i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumberX][3][bandNumX], 'Yes')
											try:
												bPath = cfg.utls.layerSource(i)
												ee = ee.replace('"' +  bV +'"', bPath)
												ee = ee.replace('"' +  bN +'"', bPath)
												ee = ee.replace('$' +  bV + '$', "'" +  cfg.bandSetsList[bandSetNumberX][3][bandNumX] + "'")
												ee = ee.replace('$' +  bN + '$', "'" +  cfg.bandSetsList[bandSetNumberX][3][bandNumX] + "'")
											except Exception as err:
												cfg.mx.msg4()
												self.rasterBandName(bandSetNumber)
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'
										# single band
										else:
											i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumberX][8], 'Yes')
											try:
												bPath = cfg.utls.layerSource(i)
												ee = ee.replace('"' +  bV +'"', bPath)
												ee = ee.replace('"' +  bN +'"', bPath)
												ee = ee.replace('$' +  bV + '$', "'" + cfg.bandSetsList[bandSetNumberX][8] + "'")
												ee = ee.replace('$' +  bN + '$', "'" + cfg.bandSetsList[bandSetNumberX][8] + "'")
											except Exception as err:
												cfg.mx.msg4()
												self.rasterBandName(bandSetNumberX)
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'
									# spectral range bands
									elif cfg.variableBlueName in bN or cfg.variableRedName in bN or cfg.variableNIRName in bN or cfg.variableGreenName in bN or cfg.variableSWIR1Name in bN or cfg.variableSWIR2Name in bN :
										if bN == cfg.variableRedName :
											bandNumber = ['', cfg.REDBand]
										elif bN == cfg.variableNIRName :
											bandNumber = ['', cfg.NIRBand]
										elif bN == cfg.variableBlueName :
											bandNumber = ['', cfg.BLUEBand]
										elif bN == cfg.variableGreenName :
											bandNumber = ['', cfg.GREENBand]
										elif bN == cfg.variableSWIR1Name :
											bandNumber = ['', cfg.SWIR1Band]
										elif bN == cfg.variableSWIR2Name :
											bandNumber = ['', cfg.SWIR2Band]
										else:
											cfg.mx.msg4()
											if outFile is None:
												cfg.uiUtls.removeProgressBar()
												cfg.cnvs.setRenderFlag(True)
												return 'No'
										if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
											try:
												bPath = cfg.bndSetLst[int(bandNumber[1]) - 1]
												ee = ee.replace('"' +  bV +'"', bPath)
												ee = ee.replace('"' +  bN +'"', bPath)
												ee = ee.replace('$' +  bV + '$', "'" +  cfg.bandSetsList[bandSetNumber][3][bandNumber] + "'")
												ee = ee.replace('$' +  bN + '$', "'" +  cfg.bandSetsList[bandSetNumber][3][bandNumber] + "'")
											except:
												return 'No'
										else:
											i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
											try:
												bPath = cfg.utls.layerSource(i)
												ee = ee.replace('"' +  bV +'"', bPath)
												ee = ee.replace('"' +  bN +'"', bPath)
												ee = ee.replace('$' +  bV + '$', "'" + cfg.bandSetsList[bandSetNumber][8] + "'")
												ee = ee.replace('$' +  bN + '$', "'" + cfg.bandSetsList[bandSetNumber][8] + "'")
											except Exception as err:
												cfg.mx.msg4()
												self.rasterBandName(bandSetNumber)
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'							
									else:
										i = cfg.utls.selectLayerbyName(bN, 'Yes')
										try:
											bPath = cfg.utls.layerSource(i)
											ee = ee.replace('"' +  bV +'"', bPath)
											ee = ee.replace('"' +  bN +'"', bPath)
											ee = ee.replace('$' +  bV + '$', '\'' +  bN + '\'')
											ee = ee.replace('$' +  bN + '$', '\'' +  bN + '\'')
										except Exception as err:
											cfg.mx.msg4()
											self.rasterBandName(bandSetNumber)
											# logger
											cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
											if outFile is None:
												cfg.uiUtls.removeProgressBar()
												cfg.cnvs.setRenderFlag(True)
												return 'No'
							# do not replace expression
							if expe is not None:
								ee = ee.replace(cfg.calcVarReplace, expe)
							ee = ee.replace('$', '\'').replace('!!', ';')
							dCheck, function = cfg.batchT.checkExpressionLine(ee)
							try:
								eval(function)
							except Exception as err:
								cfg.mx.msgErr36()
								# logger
								cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
								if batch == 'No':
									cfg.uiUtls.removeProgressBar()
									cfg.cnvs.setRenderFlag(True)
									return 'No'
						# not function
						else:
							# variable list
							variableList = []
							# band list
							bList = []
							bandNumberList = []
							for b in range(0, c):
								try:
									bV = tW.item(b, 0).text()
									bN = tW.item(b, 1).text()
								except Exception as err:
									cfg.mx.msg4()
									self.rasterBandName(bandSetNumber)
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err) + " bandset" + str(bandSetNumberX+1) + " band" + str(bandNumX+1) + " layer " + str(cfg.bandSetsList[bandSetNumberX][3][bandNumX]))
									if outFile is None:
										cfg.uiUtls.removeProgressBar()
										cfg.cnvs.setRenderFlag(True)
										return 'No'
								if str('"' +  bV +'"') in e or str('"' + bN +'"') in e:
									variableList.append(['"' + bV + '"', '"' + bN + '"'])
									# variable bandset#b1
									if cfg.variableBandsetName + '#b' in bN:
										bandNumber = bN.split('#b')
										if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
											try:
												bPath = cfg.bndSetLst[int(bandNumber[1]) - 1]
												bandNumberList.append(1)
												bList.append(bPath)
											except Exception as err:
												cfg.mx.msg4()
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'
										else:
											i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
											try:
												bPath = cfg.utls.layerSource(i)
											except Exception as err:
												cfg.mx.msg4()
												self.rasterBandName(bandSetNumber)
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'
											bandNumberList.append(int(bandNumber[1]))
											bList.append(bPath)
									# variable bandset1b1
									elif cfg.variableBandsetName in bN:
										bandSetBandNumber = bN.replace(cfg.variableBandsetName, '').split('b')
										bandSetNumberX = int(bandSetBandNumber[0]) - 1
										bandNumX = int(bandSetBandNumber[1]) - 1
										if cfg.bandSetsList[bandSetNumberX][0] == 'Yes':
											i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumberX][3][bandNumX], 'Yes')
											try:
												bPath = cfg.utls.layerSource(i)
											except Exception as err:
												cfg.mx.msg4()
												self.rasterBandName(bandSetNumber)
												# logger
												cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err) + " bandset" + str(bandSetNumberX+1) + " band" + str(bandNumX+1) + " layer " + str(cfg.bandSetsList[bandSetNumberX][3][bandNumX]))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'
											bandNumberList.append(1)
											bList.append(bPath)
										else:
											i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumberX][8], 'Yes')
											try:
												bPath = cfg.utls.layerSource(i)
											except Exception as err:
												cfg.mx.msg4()
												self.rasterBandName(bandSetNumberX)
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'
											bandNumberList.append(int(bandNumX))
											bList.append(bPath)
									# spectral range bands
									elif cfg.variableBlueName in bN or cfg.variableRedName in bN or cfg.variableNIRName in bN or cfg.variableGreenName in bN or cfg.variableSWIR1Name in bN or cfg.variableSWIR2Name in bN :
										if bN == cfg.variableRedName :
											bandNumber = ['', cfg.REDBand]
										elif bN == cfg.variableNIRName :
											bandNumber = ['', cfg.NIRBand]
										elif bN == cfg.variableBlueName :
											bandNumber = ['', cfg.BLUEBand]
										elif bN == cfg.variableGreenName :
											bandNumber = ['', cfg.GREENBand]
										elif bN == cfg.variableSWIR1Name :
											bandNumber = ['', cfg.SWIR1Band]
										elif bN == cfg.variableSWIR2Name :
											bandNumber = ['', cfg.SWIR2Band]
										else:
											cfg.mx.msg4()
											if outFile is None:
												cfg.uiUtls.removeProgressBar()
												cfg.cnvs.setRenderFlag(True)
												return 'No'
										if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
											try:
												bPath = cfg.bndSetLst[int(bandNumber[1]) - 1]
											except:
												return 'No'
											bandNumberList.append(1)
											bList.append(bPath)
										else:
											i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
											try:
												bPath = cfg.utls.layerSource(i)
											except Exception as err:
												cfg.mx.msg4()
												self.rasterBandName(bandSetNumber)
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'
											bandNumberList.append(int(bandNumber[1]))
											bList.append(bPath)										
									else:
										i = cfg.utls.selectLayerbyName(bN, 'Yes')
										try:
											bPath = cfg.utls.layerSource(i)
										except Exception as err:
											cfg.mx.msg4()
											self.rasterBandName(bandSetNumber)
											# logger
											cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
											if outFile is None:
												cfg.uiUtls.removeProgressBar()
												cfg.cnvs.setRenderFlag(True)
												return 'No'
										bandNumberList.append(1)
										bList.append(bPath)
							try:
								gdalRaster2 = cfg.gdalSCP.Open(bPath, cfg.gdalSCP.GA_ReadOnly)
								gBand2 = gdalRaster2.GetRasterBand(int(1)) 
							except Exception as err:
								cfg.mx.msg4()
								self.rasterBandName(bandSetNumber)
								# logger
								cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
								if outFile is None:
									cfg.uiUtls.removeProgressBar()
									cfg.cnvs.setRenderFlag(True)
									return 'No'
							noData = gBand2.GetNoDataValue()
							# close band
							gBand2 = None
							# close raster
							gdalRaster2 = None
							if inputNoDataAsValue is None:
								if cfg.ui.nodata_as_value_checkBox.isChecked() is True:
									skipReplaceNoDT = 1
								else:
									skipReplaceNoDT = None
							else:
								if inputNoDataAsValue == 'Yes':
									skipReplaceNoDT = 1
								else:
									skipReplaceNoDT = None
							if useScale is None:
								if cfg.ui.set_scale_checkBox.isChecked() is True:
									useScale = cfg.ui.scale_doubleSpinBox.value()
								else:
									useScale = None
							if useOffset is None:
								if cfg.ui.set_offset_checkBox.isChecked() is True:
									useOffset = cfg.ui.offset_doubleSpinBox.value()
								else:
									useOffset = None
							if useNoDataValue is None:
								if cfg.ui.nodata_checkBox_3.isChecked() is True:
									useNoDataValue = cfg.ui.nodata_spinBox_13.value()
								else:
									useNoDataValue = None
							elif useNoDataValue == 'No':
								useNoDataValue = None
							if outputNoData is None:
								outputNoData = cfg.ui.nodata_spinBox_4.value()
							if rasterDataType is None:
								rasterDataType = cfg.rasterBandCalcType
							if extentList is None:
								if (extentIntersection is None and cfg.ui.intersection_checkBox.isChecked() is True) or extentIntersection == 'Yes':
									tPMD = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'Yes')
								elif (extentSameAs is None and cfg.ui.extent_checkBox.isChecked() is True) or extentSameAs == 'Yes':
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
										try:
											bN0 =cfg.utls.addRasterLayer(bList[0])
											iCrs = cfg.utls.getCrs(bN0)
											cfg.utls.removeLayerByLayer(bN0)
										except:
											pass
										# image CRS
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
													return 'No'
												else:
													tLX = tLPoint.x()
													tLY = tLPoint.y()
													lRX = lRPoint.x()
													lRY = lRPoint.y()
											except Exception as err:
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
												cfg.uiUtls.removeProgressBar()
												cfg.cnvs.setRenderFlag(True)
												return 'No'
									elif extRaster == cfg.pixelExtent:
										tLX, tLY, lRX, lRY = extentList[0], extentList[1], extentList[2], extentList[3]
									else:
										tLX, tLY, lRX, lRY, pSX, pSY = cfg.utls.imageInformationSize(extRaster)
										if align is None:
											if cfg.ui.align_radioButton.isChecked():
												xyRes = [pSX, pSY, tLX, tLY, lRX, lRY]
												# add extent raster to virtual raster list
												i = cfg.utls.selectLayerbyName(extRaster, 'Yes')
												try:
													bPath = cfg.utls.layerSource(i)
												except Exception as err:
													cfg.mx.msg4()
													self.rasterBandName(bandSetNumber)
													# logger
													cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
													if outFile is None:
														cfg.uiUtls.removeProgressBar()
														cfg.cnvs.setRenderFlag(True)
														return 'No'
												bandNumberList.append(1)
												bList.append(bPath)
										elif align == 'Yes':
											xyRes = [pSX, pSY, tLX, tLY, lRX, lRY]
											# add extent raster to virtual raster list
											i = cfg.utls.selectLayerbyName(extRaster, 'Yes')
											try:
												bPath = cfg.utls.layerSource(i)
											except Exception as err:
												cfg.mx.msg4()
												self.rasterBandName(bandSetNumber)
												# logger
												cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
												if outFile is None:
													cfg.uiUtls.removeProgressBar()
													cfg.cnvs.setRenderFlag(True)
													return 'No'
											bandNumberList.append(1)
											bList.append(bPath)
									if tLX is None:
										if outFile is None:
											cfg.uiUtls.removeProgressBar()
											cfg.cnvs.setRenderFlag(True)
										return 'No'
									tPMD = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'No', [float(tLX), float(tLY), float(lRX), float(lRY), 'Yes'], xyRes)
								else:
									tPMD = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'No')
							else:
								tLX, tLY, lRX, lRY = extentList[0], extentList[1], extentList[2], extentList[3]
								tPMD = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'No', [float(tLX), float(tLY), float(lRX), float(lRY), 'Yes'])
							# process calculation
							o = cfg.utls.multiProcessRaster(rasterPath = tPMD, functionBand = 'No', functionRaster = cfg.utls.bandCalculation, outputRasterList = [out], nodataValue = useNoDataValue,  functionBandArgument = e, functionVariable = variableList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Calculation ') + str(e), skipReplaceNoData = skipReplaceNoDT, virtualRaster = vrtR, compress = cfg.rasterCompression, compressFormat = 'LZW', outputNoDataValue = outputNoData, dataType = rasterDataType, scale = useScale, offset = useOffset)
							if o != 'No':
								if quiet == 'No':
									r =cfg.utls.addRasterLayer(out)
									try:
										cfg.utls.rasterSymbolSingleBandGray(r)
									except Exception as err:
										# logger
										if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
									if eNBS is not None:
										try:
											if eNBS == '#':
												eNBS = None
											else:
												eNBS = int(eNBS) - 1
											cfg.bst.addBandToBandSet(eN, eNBS)
										except:
											pass
							it = it + 1
				cfg.uiUtls.updateBar(100)
				if batch == 'No':
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
				else:
					self.rasterBandName(bandSetNumber)
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " band calculation ended")
				
	# text changed
	def textChanged(self):
		if cfg.bandCalcIndex == 0:
			expression = ' ' + cfg.ui.plainTextEdit_calc.toPlainText() + ' '
			self.checkExpression(expression)
			if cfg.forbandsets in expression or cfg.forbsdates in expression  or cfg.forbandsinbandset in expression or cfg.calcFunctionNm in expression:
				self.expressionButton = True
				cfg.ui.toolButton_calculate.setEnabled(True)
				cfg.ui.plainTextEdit_calc.setStyleSheet('color : green')
		elif cfg.bandCalcIndex == 1:
			expression = cfg.bCalc.decisionRulesExpression()
			check = self.checkExpression(expression)
			tW = cfg.ui.decision_rules_tableWidget
			if len(check) > 0:
				tW.setStyleSheet('color : green')
			else:
				tW.setStyleSheet('color : red')
		
	# check the expression and return it
	def checkExpression(self, expression):
		tW = cfg.ui.tableWidget_band_calc
		v = tW.rowCount()
		checkO = 'Yes'
		cfg.ui.plainTextEdit_calc.setStyleSheet('color : red')
		name = []	
		nameList = []
		# list of raster names
		for x in range(0, v):
			name.append('"' + tW.item(x, 0).text() + '"')
			name.append('"' + tW.item(x, 1).text() + '"')
			nameList.append(['"' + tW.item(x, 0).text() + '"', '"' + tW.item(x, 1).text() + '"'])
		ex = []
		outNameList = []
		if expression is None:
			checkO = 'No'
		else:
			bsetList = [cfg.bndSetNumber + 1]
			e = expression.rstrip().split('\n')
			try:
				# band set iteration
				if cfg.forbandsets in e[0]:
					fE0 = e[0]
					bsetList = []
					filterBS = None
					try:
						fEf = e[0].split(']')
						filterBSA = fEf[1].strip()
						if len(filterBSA) == 0:
							filterBS = None
						else:
							fE0 = fEf[0]
							filterBS = filterBSA.split(',')
					except:
						filterBS = None
					foB = fE0.replace(cfg.forbandsets, '')
					try:
						# range of band sets
						rg = foB.split(':')
						bsetListA = list(range(int(rg[0].replace('[', '')), int(rg[1].replace(']', '')) + 1))
					except:
						# list of band sets
						try:
							bsetListA = eval(foB)
						except:
							checkO = 'No'
					if filterBS is None:
						bsetList = bsetListA
					else:
						for j in bsetListA:
							try:
								if cfg.bandSetsList[j-1][0] == 'Yes':
									rB0 = cfg.bandSetsList[j-1][3][0]
								else:
									rB0 = cfg.bandSetsList[j-1][8]
								for filterBSX in filterBS:
									if filterBSX.lower() in rB0.lower():
										bsetList.append(j)
										break
							except:
								pass
					e.pop(0)
				# bands in band set iteration
				if cfg.forbandsinbandset in e[0]:
					foB = e[0].replace(cfg.forbandsinbandset, '')
					try:
						# range of band sets
						rg = foB.split(':')
						bsetList = list(range(int(rg[0].replace('[', '')), int(rg[1].replace(']', '')) + 1))
					except:
						# list of band sets
						try:
							bsetList = eval(foB)
						except:
							checkO = 'No'
					e.pop(0)
				# ban set date iteration
				elif cfg.forbsdates in e[0]:
					fE0 = e[0]
					bsetList = []
					filterBS = None
					try:
						fEf = e[0].split(']')
						filterBSA = fEf[1].strip()
						if len(filterBSA) == 0:
							filterBS = None
						else:
							fE0 = fEf[0]
							filterBS = filterBSA.split(',')
					except:
						filterBS = None
					foB = fE0.replace(cfg.forbsdates, '').replace('[', '').replace(']', '')
					dtList = []
					dtRList = []
					if ':' in foB and ',' in foB:
						# list of ranges of dates
						try:
							lrg = foB.split(',')
							for lrgL in lrg:
								try:
									# range of dates
									rg = lrgL.split(':')
									dtRList.append([cfg.datetimeSCP.datetime.strptime(rg[0].strip(), '%Y-%m-%d'), cfg.datetimeSCP.datetime.strptime(rg[1].strip(), '%Y-%m-%d')])
								except:
									pass
						except:
							checkO = 'No'
					else:
						try:
							# range of dates
							rg = foB.split(':')
							dtRList.append([cfg.datetimeSCP.datetime.strptime(rg[0].strip(), '%Y-%m-%d'), cfg.datetimeSCP.datetime.strptime(rg[1].strip(), '%Y-%m-%d')])
						except:
							# list of dates
							try:
								rg = foB.split(',')
								for rgL in rg:
									dtList.append(rgL.strip())
							except:
								checkO = 'No'
					# list of band set number
					if checkO == 'Yes':
						# list of dates
						if len(dtList) > 0:
							for j in range(0, len(cfg.bandSetsList)):
								try:
									if cfg.bandSetsList[j][9] in dtList:
										if filterBS is None:
											bsetList.append(j+1)
										else:
											if cfg.bandSetsList[j][0] == 'Yes':
												rB0 = cfg.bandSetsList[j][3][0]
											else:
												rB0 = cfg.bandSetsList[j][8]
											for filterBSX in filterBS:
												if filterBSX.lower() in rB0.lower():
													bsetList.append(j+1)
													break
								except:
									pass
						else:
							# range of dates
							for j in range(0, len(cfg.bandSetsList)):
								try:
									bD =  cfg.datetimeSCP.datetime.strptime(cfg.bandSetsList[j][9], '%Y-%m-%d')
									# date range
									for dStr in dtRList:
										if (bD >= dStr[0]) & (bD <= dStr[1]) is True:
											if filterBS is None:
												bsetList.append(j+1)
												break
											else:
												if cfg.bandSetsList[j][0] == 'Yes':
													rB0 = cfg.bandSetsList[j][3][0]
												else:
													rB0 = cfg.bandSetsList[j][8]
												for filterBSX in filterBS:
													if filterBSX.lower() in rB0.lower():
														bsetList.append(j+1)
														break
								except:
									pass
					e.pop(0)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				checkO = 'No'
			if checkO == 'Yes':
				h = []
				# replace band set number for iteration
				for b in bsetList:
					#nmList = []
					for bs in range(0, len(e)):
						bsN = None
						f = str(e[bs].split('@')[0])
						dT = cfg.utls.getTime()
						if len(f)>0:
							# split output name
							try:
								nm = e[bs].split('@')[2].strip()
								nPath = e[bs].split('@')[1]
								# variable path band set
								if cfg.variableOutputNameBandset in nPath:
									if cfg.bandSetsList[b-1][0] == 'Yes':
										r = cfg.utls.selectLayerbyName(cfg.bandSetsList[b-1][3][0], 'Yes')
									else:
										r = cfg.utls.selectLayerbyName(cfg.bandSetsList[b-1][8], 'Yes')
									rS = cfg.utls.layerSource(r)
									nPath = cfg.osSCP.path.dirname(rS)
								# temporary directory
								elif 'temp' == nPath.lower():
									nPath = cfg.tmpDir
							except:
								try:
									nm = e[bs].split('@')[1].strip()
									nPath = None
								except:
									nm = None
									nPath = None
							# variable name band set
							try:
								nm = nm.replace(cfg.variableOutputNameBandset, cfg.bandSetsList[b-1][3][0][:-2])
							except:
								pass
							try:
								nm = nm.replace(cfg.variableOutputNameDate, dT)
							except:
								pass
							try:
								nm, bsN = nm.split('%')
								nm = nm.strip()
							except:
								pass
							# replace variables
							findB = cfg.utls.findBandNumber(b-1)
							try:
								f = f.replace(cfg.variableOutputNameBandset, cfg.bandSetsList[b-1][3][0][:-2])
							except:
								pass
							if findB == 'Yes':
								try:
									f = f.replace(cfg.variableRedName, cfg.bandSetsList[b-1][3][int(cfg.REDBand) - 1])
								except:
									pass
								try:
									f = f.replace(cfg.variableNIRName, cfg.bandSetsList[b-1][3][int(cfg.NIRBand) - 1])	
								except:
									pass
								try:
									f = f.replace(cfg.variableBlueName, cfg.bandSetsList[b-1][3][int(cfg.BLUEBand) - 1])
								except:
									pass
								try:
									f = f.replace(cfg.variableGreenName, cfg.bandSetsList[b-1][3][int(cfg.GREENBand) - 1])
								except:
									pass
								try:
									f = f.replace(cfg.variableSWIR1Name, cfg.bandSetsList[b-1][3][int(cfg.SWIR1Band) - 1])
								except:
									pass
								try:
									f = f.replace(cfg.variableSWIR2Name, cfg.bandSetsList[b-1][3][int(cfg.SWIR2Band) - 1])
								except:
									pass
								# replace previous output names
								#for r in nmList:
								#	f = f.replace(r[0], r[1])
								# replace original name
								#try:
								#	if nm is not None:
								#		nmO = str(e[bs].split('@')[0]).strip()
								#		nmList.append([nmO, nm])
								#except:
								#	pass
							if cfg.variableBandsetName + '#b' in f:
								f = f.replace(cfg.variableBandsetName + '#', cfg.variableBandsetName + str(b))
							try:
								# bands in band set iteration
								if cfg.variableBand in f:
									for bndX in range(0, len(cfg.bandSetsList[b-1][3])):
										try:
											fRev = f + ' @' + nPath + '@' + nm + '%' + bsN.replace('#', str(b))
											h.append(fRev.replace(cfg.variableBand, cfg.bandSetsList[b-1][3][bndX]))
										except:
											try:
												fRev = f + ' @' + nPath + '@' + nm
												h.append(fRev.replace(cfg.variableBand, cfg.bandSetsList[b-1][3][bndX]))
											except:
												try:
													fRev = f + ' @' + nm + '%' + bsN.replace('#', str(b))
													h.append(fRev.replace(cfg.variableBand, cfg.bandSetsList[b-1][3][bndX]))
												except:
													try:
														fRev = f + ' @' + nm
														h.append(fRev.replace(cfg.variableBand, cfg.bandSetsList[b-1][3][bndX]))
													except:
														h.append(f.replace(cfg.variableBand, cfg.bandSetsList[b-1][3][bndX]))
								else:
									try:
										h.append(f + ' @' + nPath + '@' + nm + '%' + bsN.replace('#', str(b)))
									except:
										try:
											h.append(f + ' @' + nPath + '@' + nm)
										except:
											try:
												h.append(f + ' @' + nm + '%' + bsN.replace('#', str(b)))
											except:
												try:
													h.append(f + ' @' + nm)
												except:
													h.append(f)
							except:
								pass
				e = h
			for nf in e:
				nm = None
				nPath = None
				bsN = None
				nameList.extend(outNameList)
				f = nf.split('@')[0]
				try:
					nm = nf.split('@')[2].strip()
					nPath = nf.split('@')[1].strip()
				except:
					try:
						nm = nf.split('@')[1].strip()
					except:
						pass
				try:
					nm = nm.replace(cfg.variableOutputNameBandset, cfg.utls.fileName(cfg.bndSetLst[0]).rpartition('.')[0][:-2])
				except:
					pass
				try:
					dT = cfg.utls.getTime()
					nm = nm.replace(cfg.variableOutputNameDate, dT)
				except:
					pass
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(nameList))
				# replace NoData values
				f = cfg.utls.replaceOperatorNames(f, nameList)	
				if nm is not None:
					try:
						nm, bsN = nm.split('%')
						nm = nm.strip()
					except:
						pass
					outNameList.append(['"' + str(nm) + '"', '"' + str(nm) + '"'])
				oldF = f
				check = 'Yes'
				# create function
				for i in name:
					f = f.replace(i, ' rasterSCPArrayfunctionBand ')	
				for i in outNameList:
					f = f.replace(i[0], ' rasterSCPArrayfunctionBand ')	
				if cfg.calcFunctionNm in f:
					#ex.append([f, nm])
					pass
				elif f == oldF:
					check = 'No'
					checkO = 'No'
				else:
					# replace numpy operators
					f = cfg.utls.replaceNumpyOperators(f)
					rasterSCPArrayfunctionBand = cfg.np.arange(9).reshape(3, 3)
					try:
						o = eval(f)
						cfg.ui.plainTextEdit_calc.setStyleSheet('color : green')
						if cfg.bandCalcIndex == 0:
							self.expressionButton = True
						elif cfg.bandCalcIndex == 1:
							self.decisionRulesButton = True
						cfg.ui.toolButton_calculate.setEnabled(True)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err) + " " + str(f))
						check = 'No'
						checkO = 'No'
				if check == 'Yes':
					if bsN is not None:
						n2 = nm + '%' + bsN
					else:
						n2 = nm
					ex.append([oldF, n2, nPath])
		if checkO == 'No':
			cfg.ui.plainTextEdit_calc.setStyleSheet('color : red')
			if cfg.bandCalcIndex == 0:
				self.expressionButton = False
			elif cfg.bandCalcIndex == 1:
				self.decisionRulesButton = False
			cfg.ui.toolButton_calculate.setEnabled(False)
		self.outputNameTable(outNameList)
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
						return 'No'
				tW.blockSignals(False)
				e = cfg.bCalc.decisionRulesExpression()
				check = self.checkExpression(e)
				if len(check) > 0:
					tW.setStyleSheet('color : green')
				else:
					tW.setStyleSheet('color : red')
				
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
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
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
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			tW.clearSelection()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
				
	# perform bands filter
	def filterTable(self):
		l = cfg.ui.tableWidget_band_calc
		text = cfg.ui.bandcalc_filter_lineEdit.text()
		items = l.findItems(text, cfg.QtSCP.MatchContains)
		c = l.rowCount()
		list = []
		for item in items:
			if item.column() == 1:
				list.append(item.row())
		l.blockSignals(True)
		for i in range (0, c):
			l.setRowHidden(i, False)
			if i not in list:
				l.setRowHidden(i, True)
		l.blockSignals(False)
		
	# buttons
	def insertButton(self, text):
		cursor = cfg.ui.plainTextEdit_calc.textCursor()
		cursor.insertText(text)

	def buttonPlus(self):
		cfg.bCalc.insertButton(' + ')

	def buttonMinus(self):
		cfg.bCalc.insertButton(' - ')	
		
	def buttonProduct(self):
		cfg.bCalc.insertButton(' * ')

	def buttonRatio(self):
		cfg.bCalc.insertButton(' / ')
		
	def buttonPower(self):
		cfg.bCalc.insertButton('^')
						
	def buttonSQRT(self):
		cfg.bCalc.insertButton('sqrt(')		
		
	def buttonLbracket(self):
		cfg.bCalc.insertButton('(')
				
	def buttonRbracket(self):
		cfg.bCalc.insertButton(')')		
						
	def buttonGreater(self):
		cfg.bCalc.insertButton(' > ')		
								
	def buttonLower(self):
		cfg.bCalc.insertButton(' < ')		
								
	def buttonUnequal(self):
		cfg.bCalc.insertButton(' != ')		
								
	def buttonEqual(self):
		cfg.bCalc.insertButton(' == ')		
		