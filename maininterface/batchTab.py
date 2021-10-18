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
f
'''

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

class BatchTab:

	def __init__(self):
		pass

	# run
	def runButton(self):
		cfg.uiUtls.addProgressBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Batch'), message = '')
		cfg.cnvs.setRenderFlag(False)
		expression = ' ' + cfg.ui.plainTextEdit_batch.toPlainText() + ' '
		e = self.checkExpression(expression)
		cfg.workingDir = None
		n = len(e)
		i = 0
		for nf in e:
			if len(nf.strip()) > 0:
				if nf.strip()[0] != '#':
					i = i + 1
					cfg.uiUtls.updateBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Batch') + ' [' + str(i) + '/' + str(n) + '] ' + nf, message = '')
					if cfg.actionCheck == 'Yes':
						check, runFunction = self.checkExpressionLine(nf)
						if check == 'Yes':
							if runFunction == '(' + cfg.workingDirNm + ')':
								pass
							else:
								if cfg.workingDir is not None:
									runFunction = runFunction.replace(cfg.workingDirNm, cfg.workingDir)
								try:
									eval(runFunction)
								except Exception as err:
									# logger
									cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
									cfg.mx.msgBarError(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Error'), str(err))
		cfg.utls.finishSound()
		cfg.utls.sendSMTPMessage(None, str(__name__))
		cfg.cnvs.setRenderFlag(True)
		cfg.uiUtls.removeProgressBar()
		
	# text changed
	def textChanged(self):
		expression = ' ' + cfg.ui.plainTextEdit_batch.toPlainText() + ' '
		self.checkExpression(expression)
		#cfg.ui.plainTextEdit_batch.setFocus()
		
	# check the expression and return it
	def checkExpression(self, expression):
		cfg.ui.plainTextEdit_batch.setStyleSheet('color : red')
		#cfg.ui.toolButton_run_batch.setEnabled(False)
		cfg.ui.batch_label.setText('')
		vexpression = expression
		# check working dir
		try:
			cfg.workingDir = None
			fTrail = 0
			for traiL in expression.split('\n'):
				fTrail = fTrail + 1
				if len(traiL.strip()) > 0:
					if traiL.strip()[0] != '#':
						firstLine = traiL
						break
			if cfg.workingDirNm in firstLine:
				check, function = self.checkExpressionLine(firstLine)
				try:
					nextLines = '\n'.join(expression.split('\n')[fTrail:])
					vexpression = firstLine + '\n' + nextLines.replace(cfg.workingDirNm, cfg.workingDir)
				except:
					pass
		except:
			pass
		# variables between ! !
		variables = {}
		rexpression = ''
		varList = [cfg.workingDirNm,cfg.tempDirNm, cfg.startForDirNm, cfg.DirNm, cfg.directoryName, cfg.endForDirNm, cfg.startForFileNm, cfg.FileNm, cfg.FileDirNm, cfg.endForFileNm, cfg.startForBandSetNm, cfg.bandSetNm, cfg.endForBandSetNm]
		cfg.ui.batch_label.setText(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Checking ...'))
		cfg.QtWidgetsSCP.qApp.processEvents()
		for traiL in vexpression.split('\n'):
			if len(traiL.strip()) > 0 and traiL.strip()[0] == '!' and traiL.replace(' ', '').split('=')[0].replace('!', '') not in varList:
				try:
					variables[traiL.replace(' ', '').split('=')[0].strip()] = traiL.split('=')[1].strip()
				except:
					rexpression = rexpression + traiL + '\n'
					for variableVal in variables:
						rexpression = rexpression.replace(variableVal, variables[variableVal])
			else:
				# replace variables in variables
				variablesCopy = variables.copy()
				for variableValC in variables:
					for variableVal in variables:
						if variableVal != variableValC:
							variablesCopy[variableValC] = str(variablesCopy[variableValC]).replace(str(variableVal), str(variables[variableVal]))
				variables = variablesCopy.copy()
				rexpression = rexpression + traiL + '\n'
				for variableVal in variables:
					rexpression = rexpression.replace(variableVal, variables[variableVal])
		# temporary rasters
		if cfg.tempRasterNm in rexpression:
			rasterNumber = cfg.reSCP.findall(cfg.tempRasterNm + '(.*?)!', rexpression)
			self.tempRasters = []
			for rN in rasterNumber:
				if cfg.outTempRastFormat == 'VRT':
					rP = cfg.utls.createTempRasterPathBatch(cfg.tempRasterNm.replace('!', '') + str(rN), 'vrt')
				else:
					rP = cfg.utls.createTempRasterPathBatch(cfg.tempRasterNm.replace('!', '') + str(rN), 'tif')
				self.tempRasters.append(rP)
				rexpression = rexpression.replace(cfg.tempRasterNm + str(rN) + '!', rP)
		# temporary directory
		if cfg.tempDirNm in rexpression:
			try:
				rexpression = rexpression.replace(cfg.tempDirNm, cfg.tmpDir)
			except:
				pass
		fexpression = rexpression
		# for directory
		if cfg.startForDirNm in fexpression:
			rexpressionX = fexpression.split(cfg.startForDirNm)
			fReplaceX = ''
			for fs in rexpressionX:
				if len(fs.strip()) > 0:
					fsSplit = fs.lstrip().split('\n')
					firstL = fsSplit[0]
					forDirX = None
					if firstL[0] == ';':
						forDir = firstL.split(';')
						forDirX = forDir[1].replace('\'', '').strip().rstrip('/')
						if len(forDirX) > 0 and cfg.QDirSCP(forDirX).exists():
							try:
								forDirFilter = forDir[3].split('|')
							except:
								forDirFilter = None
							try:
								forDirLevel = int(forDir[2])
							except:
								forDirLevel = 10000
								try:
									forDirFilter = forDir[2].split('|')
								except:
									pass
						else:
							forDirX = None
						fsSplit.pop(0)
						fs = '\n'.join(fsSplit)
					if forDirX is not None:
						fstart = fs.split(cfg.endForDirNm)
						for root, dirs, files in cfg.osSCP.walk(forDirX):
							if root[len(forDirX):].count(cfg.osSCP.sep) + 1 <= forDirLevel:
								for d in dirs:
									if forDirFilter is None:
										dirPath = cfg.osSCP.path.join(root, d)
										fReplaceX1 = fstart[0].replace(cfg.DirNm, dirPath).replace(cfg.directoryName, d)
										fLineX = fReplaceX1.rstrip().split('\n')
										for line in fLineX:
											if len(line) > 0:
												if cfg.startForFileNm in line or cfg.FileNm in line or cfg.endForFileNm in line:
													fReplaceX = fReplaceX + line + '\n'
												else:
													check, function = self.checkExpressionLine(line)
													if check == 'Yes':
														fReplaceX = fReplaceX + line + '\n'
									else:
										for fFil in forDirFilter:
											trueList = []
											for fFilAndX in fFil.strip().replace('\'', '').split('&'):
												# check date
												try:
													dateS = fFilAndX.split(':')
													dStr0 = cfg.datetimeSCP.datetime.strptime(dateS[0].strip(), '%Y-%m-%d')
													dStr1 = cfg.datetimeSCP.datetime.strptime(dateS[1].strip(), '%Y-%m-%d')
													# date from directory name
													try:
														dStr = cfg.datetimeSCP.datetime.strptime(d[-10:], '%Y-%m-%d')
													except:
														dStr = cfg.datetimeSCP.datetime.strptime(d.split('_')[-2][-10:], '%Y-%m-%d')
													trueList.append((dStr >= dStr0) & (dStr <= dStr1))
												except:
													trueList.append(fFilAndX in d)
											# add lines
											if all(trueList):
												dirPath = cfg.osSCP.path.join(root, d)
												fReplaceX1 = fstart[0].replace(cfg.DirNm, dirPath).replace(cfg.directoryName, d)
												fLineX = fReplaceX1.rstrip().split('\n')
												for line in fLineX:
													if len(line) > 0:
														if cfg.startForFileNm in line or cfg.FileNm in line or cfg.endForFileNm in line:
															fReplaceX = fReplaceX + line + '\n'
														else:
															check, function = self.checkExpressionLine(line)
															if check == 'Yes':
																fReplaceX = fReplaceX + line + '\n'
												break
						fstart.pop(0)
						fss = '\n'.join(fstart)
						try:
							fReplaceX = fReplaceX + fss + '\n'
						except:
							pass
					else:
						fReplaceX = fReplaceX + fs + '\n'
			fexpression = fReplaceX.rstrip('\\n').rstrip('\n')
		# for file in directory
		if cfg.startForFileNm in fexpression:
			fexpressionD = fexpression.split(cfg.startForFileNm)
			fReplace2 = ''
			for fs in fexpressionD:
				if len(fs.strip()) > 0:
					fsSplit = fs.lstrip().split('\n')
					firstL = fsSplit[0]
					forDirX = None
					if firstL[0] == ';':
						forDir = firstL.split(';')
						forDirX = forDir[1].replace('\'', '').strip()
						if len(forDirX) > 0 and cfg.QDirSCP(forDirX).exists():
							try:
								forDirFileFilter = forDir[3].split('|')
							except:
								forDirFileFilter = None
							try:
								forDirLevel = int(forDir[2])
							except:
								forDirLevel = 10000
								try:
									forDirFileFilter = forDir[2].split('|')
								except:
									pass
						else:
							forDirX = None
						fsSplit.pop(0)
						fs = '\n'.join(fsSplit)
					if forDirX is not None:
						fstart = fs.split(cfg.endForFileNm)
						for root, dirs, files in cfg.osSCP.walk(forDirX):
							if root[len(forDirX):].count(cfg.osSCP.sep) + 1 <= forDirLevel:
								for x in files:
									if forDirFileFilter is None:
										filePath = cfg.osSCP.path.join(root, x)
										fReplace = fstart[0].replace(cfg.FileNm, filePath).replace(cfg.FileDirNm, root)
										fReplace2 = fReplace2 + fReplace + '\n'
									else:
										for fFil in forDirFileFilter:
											trueList = []
											for fFilAndX in fFil.replace('\'', '').split('&'):
												# check date
												try:
													dateS = fFilAndX.split(':')
													dStr0 = cfg.datetimeSCP.datetime.strptime(dateS[0], '%Y-%m-%d')
													dStr1 = cfg.datetimeSCP.datetime.strptime(dateS[1], '%Y-%m-%d')
													try:
														ffNm = cfg.utls.fileNameNoExt(x)
														dStr = cfg.datetimeSCP.datetime.strptime(ffNm[-10:], '%Y-%m-%d')
													except:
														dStr = cfg.datetimeSCP.datetime.strptime(ffNm.split('_')[-2][-10:], '%Y-%m-%d')
													trueList.append((dStr >= dStr0) & (dStr <= dStr1))
												except:
													trueList.append(fFilAndX in x)	
											if all(trueList):
												filePath = cfg.osSCP.path.join(root, x)
												fReplace = fstart[0].replace(cfg.FileNm, filePath).replace(cfg.FileDirNm, root)
												fReplace2 = fReplace2 + fReplace + '\n'
												break
						try:
							fReplace2 = fReplace2 + fstart[1] + '\n'
						except:
							pass
					else:
						fReplace2 = fReplace2 + fs + '\n'
			fexpression = fReplace2.rstrip('\\n').rstrip('\n')
		# for band set
		if cfg.startForBandSetNm in fexpression:
			ffexpression = fexpression.split(cfg.startForBandSetNm)
			fReplace3 = ''
			for fs in ffexpression:
				if len(fs.strip()) > 0:
					fsSplit = fs.lstrip().split('\n')
					firstL = fsSplit[0]
					forBS = None
					if firstL[0] == ';':
						forBss = firstL.split(';')
						forBS = forBss[1].replace('\'', '').strip()
						fsSplit.pop(0)
						fs = '\n'.join(fsSplit)
					if forBS is not None:
						bsetList = []
						if forBS == '*':
							bsetList = list(range(1, len(cfg.bandSetsList)+1))
						else:
							try:
								# range of band sets
								rgX = forBS.split(',')
								for rgB in rgX:
									try:
										# range of band sets
										rg = rgB.split(':')
										bsetList1 = list(range(int(rg[0]), int(rg[1]) + 1))
										bsetList.extend(bsetList1)
									except:
										try:
											bsetList.extend([int(rgB)])
										except:
											pass
							except:
								pass
						fstart = fs.split(cfg.endForBandSetNm)
						fReplaceB = ''
						for bsset in bsetList:
							fReplaceB = fReplaceB + fstart[0].replace(cfg.bandSetNm, str(bsset)) + '\n'
						try:
							fReplaceB = fReplaceB + fstart[1]
						except:
							pass
						fReplace3 = fReplace3 + fReplaceB + '\n'
					else:
						fReplace3 = fReplace3 + fs + '\n'
			fexpression = fReplace3.rstrip('\\n').rstrip('\n')	
		fLine = fexpression.rstrip().split('\n')
		ef = []
		for line in fLine:
			if len(line) > 0 and line[0] != '#':
				ef.append(line)
		lnmb = 0
		for nf in ef:
			if len(nf.strip()) > 0:
				if nf.strip()[0] != '#':
					lnmb = lnmb + 1
					try:
						check, function = self.checkExpressionLine(nf)
					except:
						check = 'No'
						function = [str(nf), str(nf)]
					if check == 'Yes':
						pass
					else:
						errNf = function[0]
						errPar = function[1]
						cfg.ui.batch_label.setText(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Error line ') + str(lnmb) + ': ' + str(errNf) + ' --> ' + str(errPar))
						cfg.ui.plainTextEdit_batch.setStyleSheet('color : red')
						#cfg.ui.toolButton_run_batch.setEnabled(False)
						return ef
		cfg.ui.plainTextEdit_batch.setStyleSheet('color : green')
		#cfg.ui.toolButton_run_batch.setEnabled(True)
		cfg.ui.batch_label.setText(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Check OK'))
		return ef
			
	# check the expression line and return it
	def checkExpressionLine(self, expression):
		checkO = 'Yes'
		errNf = ''
		if len(expression.strip()) == 0:
			pass
		elif expression.strip()[0] == '#':
			return checkO, ['', '']
		else:
			f = expression.split(';')
			nm = f[0].replace(' ', '')
			fNm, fRun, fList = cfg.batchT.replaceFunctionNames(nm)
			oldF = f
			errPar = ''
			# create function
			if fNm == 'No':
				checkO = 'No'
				errNf = nm
			else:
				try:
					check, parameters = eval(fNm + '(' + str(f[1:]) + ')')
					if check == 'No':
						checkO = 'No'
						errNf = nm
						if errPar is not None:
							errPar = parameters
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					checkO = 'No'
					errNf = nm
			if checkO == 'Yes':
				function = fRun + '('
				for p in parameters:
					function = function + str(p) + ','
				function = function[:-1] + ')'
				return checkO, function
			else:
				return checkO, [errNf, errPar]
			
	# replace function names
	def replaceFunctionNames(self, name):
		for i in cfg.functionNames:
			if name.lower().strip() == i[0][0].strip():
				return i[0][1], i[0][2], i[0][3]
		return 'No', 'No', 'No'
	
	# clear batch
	def clearBatch(self):
		cfg.ui.plainTextEdit_batch.setPlainText('')
						
	# import batch from text file
	def importBatch(self):
		file = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a batch file'), '', 'txt (*.txt)')
		if len(file) > 0:
			text = open(file, 'r').read()
			cfg.ui.plainTextEdit_batch.setPlainText(text)
			
	# export batch to text file
	def exportBatch(self):
		file = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save the batch to file'), '', '*.txt', 'txt')
		if file is not False:
			if file.lower().endswith('.txt'):
				pass
			else:
				file = file + '.txt'
			f = cfg.ui.plainTextEdit_batch.toPlainText()
			o = open(file, 'w')
			o.write(f)
			o.close()
				
	# add function list to table
	def addFunctionsToTable(self, functionList):
		tW = cfg.ui.batch_tableWidget
		for i in functionList:
			tW.blockSignals(True)
			# count table rows
			c = tW.rowCount()
			try:
				itF = i[0][1]
				# name of item of list
				itN = i[0][0]
				# add list items to table
				tW.setRowCount(c + 1)
				cfg.utls.addTableItem(tW, itN, c, 0)
			except:
				itN = i[0][0]
				# add list items to table
				tW.setRowCount(c + 1)
				co = cfg.QtGuiSCP.QColor(200, 200, 200)
				cfg.utls.addTableItem(tW, itN, c, 0, 'No', co, bold = 'Yes')
			tW.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
				
	# set function
	def setFunction(self, index):
		pT = cfg.ui.plainTextEdit_batch
		tW = cfg.ui.batch_tableWidget
		text = pT.toPlainText()
		if len(text) > 0:
			space = '\n'
		else:
			space = ''
		nm = tW.item(index.row(), 0).text()
		fNm, fRun, fList = cfg.batchT.replaceFunctionNames(nm)
		if fNm != 'No':
			text = text + space + nm.strip() + ';'
			for f in fList:
				text = text + f + ';'
			pT.setPlainText(text[:-1])
			pT.setFocus()
			
	# set function button
	def setFunctionButton(self):
		pT = cfg.ui.plainTextEdit_batch
		text = pT.toPlainText()
		if len(text) > 0:
			space = '\n'
		else:
			space = ''
		nm = cfg.dlg.sender().objectName()
		fNm, fRun, fList = cfg.batchT.replaceFunctionNames(nm)
		if fNm != 'No':
			text = text + space + nm.strip() + ';'
			for f in fList:
				text = text + f + ';'
			pT.setPlainText(text[:-1])
			pT.setFocus()
			cfg.utls.batchTab()
			
	# batch working directory
	def workingDirectory(self, paramList):
		parameters = []
		for p in paramList:
			# working directory inside ' '
			g = cfg.reSCP.findall('[\'](.*?)[\']',p)
			workingDir = g[0].replace('\\', '/')
			if len(workingDir) > 0 and cfg.QDirSCP(workingDir).exists():
				cfg.workingDir = workingDir
			else:
				return 'No', 'workingDirectory'
		# append parameters
		try:
			parameters.append(cfg.workingDirNm)
		except:
			return 'No', 'workingDirectory'
		return 'Yes', parameters
		
	# batch process settings
	def processSettings(self, paramList):
		threads = 'None'
		ram = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			if pName == 'threads':
				try:
					threads = str(int(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			elif pName == 'ram':
				try:
					ram = str(int(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(threads)
			parameters.append(ram)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch add raster
	def performAddRaster(self, paramList):
		file = 'None'
		name = 'None'
		bandset = 'None'
		wavelength = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					file = '\'' + g[0] + '\''
				else:
					return 'No', pName
			elif pName == 'input_raster_name':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0].strip()) > 0:
					name = '\'' + g[0].strip() + '\''
				else:
					return 'No', pName
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			elif pName == 'center_wavelength':
				try:
					wavelength = str(float(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(file)
			parameters.append(name)
			parameters.append(bandset)
			parameters.append(wavelength)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
									
	# batch Landsat conversion
	def performLandsatConversion(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input directory inside ' '
			if pName == 'input_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.label_26.setText(g[0])
				inputDir = '\'' + g[0] + '\''
				if len(g[0]) > 0 and cfg.QDirSCP(str(g[0])).exists():
					pass
				else:
					l = cfg.ui.landsat_tableWidget
					cfg.utls.clearTable(l)
					return 'No', pName
			# output directory inside ' '
			elif pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# MTL file path inside ' '
			elif pName == 'mtl_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.label_27.setText(g[0])
			# temperature in Celsius checkbox (1 checked or 0 unchecked)
			elif pName == 'celsius_temperature':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.celsius_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.celsius_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == 'apply_dos1':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.DOS1_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.DOS1_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.nodata_checkBox_2.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.nodata_checkBox_2.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.nodata_spinBox_3.setValue(val)
				except:
					return 'No', pName
			# pansharpening checkbox (1 checked or 0 unchecked)
			elif pName == 'pansharpening':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.pansharpening_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.pansharpening_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == 'create_bandset':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.create_bandset_checkBox.setCheckState(0)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(inputDir)
			parameters.append(outputDir)
			# batch
			parameters.append('\'Yes\'')
			try:
				parameters.append(bandset)
			except:
				parameters.append('None')
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		# populate table
		cfg.landsatT.populateTable(cfg.ui.label_26.text(), 'Yes')
		return 'Yes', parameters
															
	# batch ASTER conversion
	def performASTERConversion(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.label_143.setText(g[0])
				inputFile = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					l = cfg.ui.ASTER_tableWidget
					cfg.utls.clearTable(l)
					return 'No', pName
			# output directory inside ' '
			elif pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# temperature in Celsius checkbox (1 checked or 0 unchecked)
			elif pName == 'celsius_temperature':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.celsius_checkBox_2.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.celsius_checkBox_2.setCheckState(0)
				else:
					return 'No', pName
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == 'apply_dos1':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.DOS1_checkBox_2.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.DOS1_checkBox_2.setCheckState(0)
				else:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.nodata_checkBox_5.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.nodata_checkBox_5.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.nodata_spinBox_6.setValue(val)
				except:
					return 'No', pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == 'create_bandset':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.create_bandset_checkBox_2.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.create_bandset_checkBox_2.setCheckState(0)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(inputFile)
			parameters.append(outputDir)
			# batch
			parameters.append('\'Yes\'')
			try:
				parameters.append(bandset)
			except:
				parameters.append('None')
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		# populate table
		cfg.ASTERT.populateTable(cfg.ui.label_143.text(), 'Yes')
		return 'Yes', parameters
																			
	# batch MODIS conversion
	def performMODISConversion(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.label_217.setText(g[0])
				inputFile = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					l = cfg.ui.MODIS_tableWidget
					cfg.utls.clearTable(l)
					return 'No', pName
			# output directory inside ' '
			elif pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# reproject to WGS 84 checkbox (1 checked or 0 unchecked)
			elif pName == 'reproject_wgs84':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.reproject_modis_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.reproject_modis_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.nodata_checkBox_7.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.nodata_checkBox_7.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.nodata_spinBox_8.setValue(val)
				except:
					return 'No', pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == 'create_bandset':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.create_bandset_checkBox_3.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.create_bandset_checkBox_3.setCheckState(0)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(inputFile)
			parameters.append(outputDir)
			# batch
			parameters.append('\'Yes\'')
			try:
				parameters.append(bandset)
			except:
				parameters.append('None')
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		# populate table
		cfg.MODIST.populateTable(cfg.ui.label_217.text(), 'Yes')
		return 'Yes', parameters
						
	# batch Sentinel-1 conversion
	def performSentinel1Conversion(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input directory inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputFile = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# output directory inside ' '
			elif pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# xml graph file path inside ' '
			elif pName == 'xml_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.S2_label_94.setText(g[0])
			# VH polarization checkbox (1 checked or 0 unchecked)
			elif pName == 'vh':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.VH_checkBox_S1.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.VH_checkBox_S1.setCheckState(0)
				else:
					return 'No', pName
			# VV polarization checkbox (1 checked or 0 unchecked)
			elif pName == 'vv':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.VV_checkBox_S1.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.VV_checkBox_S1.setCheckState(0)
				else:
					return 'No', pName
			# raster conversion to dB
			elif pName == 'convert_to_db':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.convert_to_db_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.convert_to_db_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# raster projection as band set
			elif pName == 'raster_project':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.projection_checkBox_S1.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.projection_checkBox_S1.setCheckState(0)
				else:
					return 'No', pName
			# band set number
			elif pName == 'raster_projections_band_set':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.band_set_comb_spinBox_11.setValue(val)
				except:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.S1_nodata_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.S1_nodata_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.S1_nodata_spinBox.setValue(val)
				except:
					return 'No', pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == 'create_bandset':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.S1_create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.S1_create_bandset_checkBox.setCheckState(0)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(inputFile)
			parameters.append(outputDir)
			# batch
			parameters.append('\'Yes\'')
			try:
				parameters.append(bandset)
			except:
				parameters.append('None')
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
											
	# batch Sentinel conversion
	def performSentinel2Conversion(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input directory inside ' '
			if pName == 'input_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.S2_label_86.setText(g[0])
				inputDir = '\'' + g[0] + '\''
				if len(g[0]) > 0 and cfg.QDirSCP(str(g[0])).exists():
					pass
				else:
					l = cfg.ui.sentinel_2_tableWidget
					cfg.utls.clearTable(l)
					return 'No', pName
			# output directory inside ' '
			elif pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', '')) - 1))
				except:
					return 'No', pName
			# MTD_SAFL1C file path inside ' '
			elif pName == 'mtd_safl1c_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.S2_label_94.setText(g[0])
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == 'apply_dos1':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.DOS1_checkBox_S2.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.DOS1_checkBox_S2.setCheckState(0)
				else:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.S2_nodata_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.S2_nodata_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# preprocess bands 1 9 10
			elif pName == 'preprocess_bands_1_9_10':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.preprocess_b_1_9_10_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.preprocess_b_1_9_10_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.S2_nodata_spinBox.setValue(val)
				except:
					return 'No', pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == 'create_bandset':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.S2_create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.S2_create_bandset_checkBox.setCheckState(0)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(inputDir)
			parameters.append(outputDir)
			# batch
			parameters.append('\'Yes\'')
			try:
				parameters.append(bandset)
			except:
				parameters.append('None')
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		# populate table
		cfg.sentinel2T.populateTable(cfg.ui.S2_label_86.text(), 'Yes')
		return 'Yes', parameters
										
	# batch Sentinel 3 conversion
	def performSentinel3Conversion(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input directory inside ' '
			if pName == 'input_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.S3_label_87.setText(g[0])
				inputDir = '\'' + g[0] + '\''
				if len(g[0]) > 0 and cfg.QDirSCP(str(g[0])).exists():
					pass
				else:
					l = cfg.ui.sentinel_3_tableWidget
					cfg.utls.clearTable(l)
					return 'No', pName
			# output directory inside ' '
			elif pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == 'apply_dos1':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.DOS1_checkBox_S3.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.DOS1_checkBox_S3.setCheckState(0)
				else:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.S3_nodata_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.S3_nodata_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.S2_nodata_spinBox_2.setValue(val)
				except:
					return 'No', pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == 'create_bandset':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.S3_create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.S3_create_bandset_checkBox.setCheckState(0)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(inputDir)
			parameters.append(outputDir)
			# batch
			parameters.append('\'Yes\'')
			try:
				parameters.append(bandset)
			except:
				parameters.append('None')
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		# populate table
		cfg.sentinel3T.populateTable(cfg.ui.S3_label_87.text(), 'Yes')
		return 'Yes', parameters
															
	# batch GOES conversion
	def performGOESConversion(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input directory inside ' '
			if pName == 'input_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.GOES_label.setText(g[0])
				inputDir = '\'' + g[0] + '\''
				if len(g[0]) > 0 and cfg.QDirSCP(str(g[0])).exists():
					pass
				else:
					l = cfg.ui.GOES_tableWidget
					cfg.utls.clearTable(l)
					return 'No', pName
			# output directory inside ' '
			elif pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.GOES_nodata_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.GOES_nodata_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.GOES_nodata_spinBox.setValue(val)
				except:
					return 'No', pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == 'create_bandset':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.GOES_create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.GOES_create_bandset_checkBox.setCheckState(0)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(inputDir)
			parameters.append(outputDir)
			# batch
			parameters.append('\'Yes\'')
			try:
				parameters.append(bandset)
			except:
				parameters.append('None')
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		# populate table
		cfg.goesT.populateTable(cfg.ui.GOES_label.text(), 'Yes')
		return 'Yes', parameters
																
	# batch classification
	def performClassification(self, paramList):
		bandset = 'None'
		algFiles = '\'No\''
		reportCheckBox = '\'No\''
		vectorOutput = '\'No\''
		useLcs = '\'No\''
		useLcsAlgorithm = '\'No\''
		useLcsOnlyOverlap = '\'No\''
		maskCheckBox = '\'No\''
		mask = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output classification inside ' '
			if pName == 'output_classification_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputClassification = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# use macroclass checkbox (1 checked or 0 unchecked)
			elif pName == 'use_macroclass':
				if pSplit[1].strip().replace(' ', '') == '1':
					useMacroclass = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					useMacroclass = '\'No\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# use LCS checkbox (1 checked or 0 unchecked)
			elif pName == 'use_lcs':
				if pSplit[1].strip().replace(' ', '') == '1':
					useLcs = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					useLcs = '\'No\''
				else:
					return 'No', pName
			# use LCS with algorithm checkbox (1 checked or 0 unchecked)
			elif pName == 'use_lcs_algorithm':
				if pSplit[1].strip().replace(' ', '') == '1':
					useLcsAlgorithm = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					useLcsAlgorithm = '\'No\''
				else:
					return 'No', pName
			# use LCS only overlap checkbox (1 checked or 0 unchecked)
			elif pName == 'use_lcs_only_overlap':
				if pSplit[1].strip().replace(' ', '') == '1':
					useLcsOnlyOverlap = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					useLcsOnlyOverlap = '\'No\''
				else:
					return 'No', pName
			# apply mask checkbox (1 checked or 0 unchecked)
			elif pName == 'apply_mask':
				if pSplit[1].strip().replace(' ', '') == '1':
					maskCheckBox = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					maskCheckBox = '\'No\''
				else:
					return 'No', pName
			# mask file path inside ' '
			elif pName == 'mask_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					mask = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# vector output checkbox (1 checked or 0 unchecked)
			elif pName == 'vector_output':
				if pSplit[1].strip().replace(' ', '') == '1':
					vectorOutput = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					vectorOutput = '\'No\''
				else:
					return 'No', pName
			# classification report checkbox (1 checked or 0 unchecked)
			elif pName == 'classification_report':
				if pSplit[1].strip().replace(' ', '') == '1':
					reportCheckBox = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					reportCheckBox = '\'No\''
				else:
					return 'No', pName
			# save algorithm files checkbox (1 checked or 0 unchecked)
			elif pName == 'save_algorithm_files':
				if pSplit[1].strip().replace(' ', '') == '1':
					algFiles = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					algFiles = '\'No\''
				else:
					return 'No', pName
			# algorithm name 'Minimum Distance' 'Maximum Likelihood' 'Spectral Angle Mapping'
			elif pName == 'algorithm_name':
				aL = [cfg.algMinDist, cfg.algML, cfg.algSAM]
				a = pSplit[1].strip().strip().replace('\'', '')
				if a in aL:
					algorithm =  '\'' + a + '\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputClassification)
			parameters.append(bandset)
			parameters.append(algFiles)
			parameters.append(reportCheckBox)
			parameters.append(vectorOutput)
			parameters.append(algorithm)
			parameters.append(useMacroclass)
			parameters.append(useLcs)
			parameters.append(useLcsAlgorithm)
			parameters.append(useLcsOnlyOverlap)
			parameters.append(maskCheckBox)
			parameters.append(mask)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch classification
	def performRandomForest(self, paramList):
		evalClassifier = '\'false\''
		evalFeaturePowerSet = '\'false\''
		minPowerSize = '2'
		maxPowerSize = '7'
		saveClassifier = '\'No\''
		classPath = '\'\''
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output classification inside ' '
			if pName == 'output_classification_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputClassification = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# use macroclass checkbox (1 checked or 0 unchecked)
			elif pName == 'use_macroclass':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.macroclass_checkBox_rf.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.macroclass_checkBox_rf.setCheckState(0)
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# number of training samples
			elif pName == 'number_training_samples':
				try:
					numberTrainingSamples = str(int(eval(pSplit[1].strip().replace(' ', ''))))
				except:
					return 'No', pName
			# number of training samples
			elif pName == 'number_trees':
				try:
					treeCount = str(int(eval(pSplit[1].strip().replace(' ', ''))))
				except:
					return 'No', pName
			# evaluate classifier (1 checked or 0 unchecked)
			elif pName == 'evaluate_classifier':
				if pSplit[1].strip().replace(' ', '') == '1':
					evalClassifier = '\'true\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					evalClassifier = '\'false\''
				else:
					return 'No', pName
			# evaluate feature power set (1 checked or 0 unchecked)
			elif pName == 'evaluate_feature_power_set':
				if pSplit[1].strip().replace(' ', '') == '1':
					evalFeaturePowerSet = '\'true\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					evalFeaturePowerSet = '\'false\''
				else:
					return 'No', pName
			# min power
			elif pName == 'min_power':
				try:
					minPowerSize = str(int(eval(pSplit[1].strip().replace(' ', ''))))
				except:
					return 'No', pName
			# max power
			elif pName == 'max_power':
				try:
					maxPowerSize = str(int(eval(pSplit[1].strip().replace(' ', ''))))
				except:
					return 'No', pName
					
			# classifier file path inside ' '
			elif pName == 'classifier_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					classPath = g[0]
				else:
					classPath = '\'\''
					return 'No', pName
			# save classifier checkbox (1 checked or 0 unchecked)
			elif pName == 'save_classifier':
				if pSplit[1].strip().replace(' ', '') == '1':
					saveClassifier = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					saveClassifier = '\'No\''
				else:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputClassification)
			parameters.append(bandset)
			parameters.append(numberTrainingSamples)
			parameters.append(treeCount)
			parameters.append(evalClassifier)
			parameters.append(evalFeaturePowerSet)
			parameters.append(minPowerSize)
			parameters.append(maxPowerSize)
			parameters.append(classPath)
			parameters.append(saveClassifier)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
										
	# batch create band set
	def performBandSetCreation(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file path inside ' ' separated by ,
			if pName == 'raster_path_list':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				files = g[0]
				if len(files) > 0:
					files = '\'' + files + '\''
				else:
					return 'No', pName
			#  wavelength unit 0=number 1=u'µm (1 E-6m)' 2='nm (1 E-9m)'
			elif pName == 'wavelength_unit':
				if pSplit[1].strip().replace(' ', '') == '0':
					noUnitId = cfg.ui.unit_combo.findText(cfg.wlMicro)
					cfg.ui.unit_combo.setCurrentIndex(noUnitId)
					id = cfg.ui.unit_combo.findText(cfg.noUnit)
					cfg.ui.unit_combo.setCurrentIndex(id)
				elif pSplit[1].strip().replace(' ', '') == '1':
					noUnitId = cfg.ui.unit_combo.findText(cfg.noUnit)
					cfg.ui.unit_combo.setCurrentIndex(noUnitId)
					id = cfg.ui.unit_combo.findText(cfg.wlMicro)
					cfg.ui.unit_combo.setCurrentIndex(id)
				elif pSplit[1].strip().replace(' ', '') == '2':
					noUnitId = cfg.ui.unit_combo.findText(cfg.noUnit)
					cfg.ui.unit_combo.setCurrentIndex(noUnitId)
					id = cfg.ui.unit_combo.findText(cfg.wlNano)
					cfg.ui.unit_combo.setCurrentIndex(id)
				else:
					return 'No', pName
			# center wavelength inside ' ' separated by ,
			elif pName == 'center_wavelength':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				center_wavelength = g[0]
				if len(center_wavelength) > 0:
					center_wavelength = '\'' + center_wavelength + '\''
				else:
					return 'No', pName
			# multiplicative factor inside ' ' separated by ,
			elif pName == 'multiplicative_factor':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				multiplicative_factor = g[0]
				if len(multiplicative_factor) > 0:
					multiplicative_factor = '\'' + multiplicative_factor + '\''
				else:
					return 'No', pName
			# additive factor inside ' ' separated by ,
			elif pName == 'additive_factor':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				additive_factor = g[0]
				if len(additive_factor) > 0:
					additive_factor = '\'' + additive_factor + '\''
				else:
					return 'No', pName
			# date in format %Y-%m-%d
			elif pName == 'date':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				date = g[0]
				if len(date) > 0:
					date = '\'' + date + '\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(files)
			try:
				parameters.append(center_wavelength)
			except:
				parameters.append('\'\'')
			try:
				parameters.append(multiplicative_factor)
			except:
				parameters.append('\'\'')
			try:
				parameters.append(additive_factor)
			except:
				parameters.append('\'\'')
			try:
				parameters.append(date)
			except:
				pass
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters	
		
	# batch select band set
	def performBandSetSelection(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			if pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(bandset)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch remove band set
	def performRemoveBandSet(self, paramList):
		unload = '\'No\''
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			if pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# unload bands (1 checked or 0 unchecked)
			elif pName == 'unload_bands':
				if pSplit[1].strip().replace(' ', '') == '1':
					unload = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					unload = '\'No\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(bandset)
			parameters.append(unload)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch remove band from band set
	def performRemoveBandFromBandSet(self, paramList):
		unload = '\'No\''
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			if pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# band set list ' ' separated by ,
			elif pName == 'band_list':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				band_list = g[0]
				if len(band_list) > 0:
					band_list = '\'[' + band_list + ']\''
				else:
					return 'No', pName
			# unload bands (1 checked or 0 unchecked)
			elif pName == 'unload_bands':
				if pSplit[1].strip().replace(' ', '') == '1':
					unload = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					unload = '\'No\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(bandset)
			parameters.append(band_list)
			parameters.append(unload)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch add new band set
	def performAddNewBandSet(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			if pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))))
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		parameters.append('\'Yes\'')
		parameters.append(bandset)
		return 'Yes', parameters
		
	# batch send notification
	def performSendNotification(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			if pName == 'subject':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				subject = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			elif pName == 'message':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				message = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		parameters.append(subject)
		parameters.append(message)
		return 'Yes', parameters
									
	# batch band combination
	def performBandCombination(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			if pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# output file path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			else:
				return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(bandset)
			parameters.append(outputRaster)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
																								
	# batch split raster
	def performSplitRaster(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				file = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# output directory inside ' '
			elif pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output name prefix inside ' '
			elif pName == 'output_name_prefix':
				g = pSplit[1].strip().replace('\'', '')
				if len(g) > 0:
					cfg.ui.output_name_lineEdit.setText(g)
				else:
					cfg.ui.output_name_lineEdit.setText('')
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'No\'')
			parameters.append('\'Yes\'')
			parameters.append(file)
			parameters.append(outputDir)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# mosaic band sets
	def performMosaicBandSets(self, paramList):
		virtual = '\'No\''
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output directory inside ' '
			if pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output name prefix inside ' '
			elif pName == 'output_name_prefix':
				g = pSplit[1].strip().replace('\'', '')
				if len(g) > 0:
					cfg.ui.mosaic_output_name_lineEdit.setText(g)
				else:
					cfg.ui.mosaic_output_name_lineEdit.setText('')
					return 'No', pName
			# band set list ' ' separated by ,
			elif pName == 'band_set_list':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				band_set_list = g[0]
				if len(band_set_list) > 0:
					if band_set_list == '*':
						band_set_list = '\'*\''
					else:
						band_set_list = '\'[' + band_set_list + ']\''
				else:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.nodata_checkBox_9.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.nodata_checkBox_9.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.nodata_spinBox_10.setValue(val)
				except:
					return 'No', pName
			# virtual output checkbox (1 checked or 0 unchecked)
			elif pName == 'virtual_output':
				if pSplit[1].strip().replace(' ', '') == '1':
					virtual = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					virtual = '\'No\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputDir)
			parameters.append(band_set_list)
			parameters.append(virtual)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters

	# neighbor pixels band sets
	def performNeighborPixels(self, paramList):
		matrixSize = 'None'
		file = 'None'
		namePrefix = 'None'
		statPerc = 'None'
		circular = 'None'
		virtual = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output directory inside ' '
			if pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output name prefix inside ' '
			elif pName == 'output_name_prefix':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				namePrefix = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# input file path inside ' '
			elif pName == 'matrix_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				file = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# virtual output checkbox (1 checked or 0 unchecked)
			elif pName == 'virtual_output':
				if pSplit[1].strip().replace(' ', '') == '1':
					virtual = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					virtual = '\'No\''
				else:
					return 'No', pName
			# matrix size (int value)
			elif pName == 'matrix_size':
				try:
					matrixSize = str(int(eval(pSplit[1].strip().replace(' ', ''))))
				except:
					return 'No', pName
			# circular checkbox (1 checked or 0 unchecked)
			elif pName == 'circular':
				if pSplit[1].strip().replace(' ', '') == '1':
					circular = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					circular = '\'No\''
				else:
					return 'No', pName
			# statistic name inside ' '
			elif pName == 'statistic':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					statName = None
					for i in cfg.statisticList:
						if i[0].lower() == g[0].lower():
							statName = '\'' + g[0] + '\''
							break
					if statName is None:
						return 'No', pName
				else:
					return 'No', pName
			# stat value (int value)
			elif pName == 'stat_value':
				try:
					statPerc = int(eval(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(bandset)
			parameters.append(outputDir)
			parameters.append(matrixSize)
			parameters.append(file)
			parameters.append(statName)
			parameters.append(statPerc)
			parameters.append(namePrefix)
			parameters.append(circular)
			parameters.append(virtual)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
	
	# batch band calc
	def performBandCalc(self, paramList):
		extentRaster = 'None'
		bandset = 'None'
		outputRaster = 'None'
		useValueNoData = '\'No\''
		inputNodataAsValue = '\'No\''
		extentIntersection = '\'Yes\''
		extentSameAs = '\'No\''
		align = '\'Yes\''
		outputNoData = '\'' + str(cfg.NoDataVal) + '\''
		scaleValue = '\'1\''
		offsetValue = '\'0\''
		dataType = '\'Float32\''
		calcDataType = 'None'
		useNodataMask = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# expression inside ' '
			if pName == 'expression':
				g = pSplit[1].strip().replace('!!', ';')
				if len(g) > 2:
					expr = g
				else:
					return 'No', pName
			# output file path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = '\'' + g[0] + '\''
				if len(g[0]) > 0:
					pass
				else:
					return 'No', pName
			# extent same as raster name inside ' '
			elif pName == 'extent_same_as_raster_name':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				extentRaster = '\'' + g[0] + '\''
				if len(g[0]) > 0:
					extentSameAs = '\'Yes\'' 
				else:
					return 'No', pName
			# extent checkbox (1 checked or 0 unchecked)
			elif pName == 'extent_intersection':
				if pSplit[1].strip().replace(' ', '') == '1':
					extentIntersection = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					extentIntersection = '\'No\''
				else:
					return 'No', pName
			# align checkbox (1 checked or 0 unchecked)
			elif pName == 'align':
				if pSplit[1].strip().replace(' ', '') == '1':
					align = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					align = '\'No\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# nodata as value checkbox (1 checked or 0 unchecked)
			elif pName == 'input_nodata_as_value':
				if pSplit[1].strip().replace(' ', '') == '1':
					inputNodataAsValue = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					inputNodataAsValue = '\'No\''
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'use_value_nodata':
				try:
					useValueNoData = str(int(eval(pSplit[1].strip().replace(' ', ''))))
				except:
					return 'No', pName
			# nodata mask value (int value)
			elif pName == 'nodata_mask':
				try:
					useNodataMask = str(int(eval(pSplit[1].strip().replace(' ', ''))))
				except:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'output_nodata_value':
				try:
					outputNoData = int(eval(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			# scale value (float value)
			elif pName == 'scale_value':
				try:
					scaleValue = str(float(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			# offset value (float value)
			elif pName == 'offset_value':
				try:
					offsetValue = str(float(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			# data type prefix inside ' '
			elif pName == 'data_type':
				g = pSplit[1].strip().replace('\'', '')
				if len(g) > 0:
					dataType = '\'' + g + '\''
				else:
					return 'No', pName
			# calculation data type prefix inside ' '
			elif pName == 'calculation_data_type':
				g = pSplit[1].strip().replace('\'', '')
				if len(g) > 0:
					calcDataType = '\'' + g + '\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append(outputRaster)
			parameters.append('\'Yes\'')
			parameters.append(expr)
			parameters.append(extentRaster)
			parameters.append('None')
			parameters.append(inputNodataAsValue)
			parameters.append(useValueNoData)
			parameters.append(outputNoData)
			parameters.append(dataType)
			parameters.append(scaleValue)
			parameters.append(offsetValue)
			parameters.append(align)
			if extentSameAs == '\'Yes\'':
				extentIntersection = '\'No\''
			parameters.append(extentIntersection)
			parameters.append(extentSameAs)
			parameters.append('\'No\'')
			parameters.append(bandset)
			parameters.append(calcDataType)
			parameters.append(useNodataMask)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch clip rasters
	def performClipRasters(self, paramList):
		shapefilePath = 'None'
		vector_field = 'None'
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output directory inside ' '
			if pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output name prefix inside ' '
			elif pName == 'output_name_prefix':
				g = pSplit[1].strip().replace('\'', '')
				if len(g) > 0:
					cfg.ui.output_clip_name_lineEdit.setText(g)
				else:
					cfg.ui.output_clip_name_lineEdit.setText('')
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# use vector checkbox (1 checked or 0 unchecked)
			elif pName == 'use_vector':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.shapefile_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.shapefile_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# use vector field checkbox (1 checked or 0 unchecked)
			elif pName == 'use_vector_field':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.vector_field_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.vector_field_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# vector path inside ' '
			elif pName == 'vector_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					shapefilePath = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# vector field inside ' '
			elif pName == 'vector_field':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					vector_field = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# ul_x inside ' '
			elif pName == 'ul_x':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.UX_lineEdit.setText(g[0])
				else:
					cfg.ui.UX_lineEdit.setText('')
					return 'No', pName
			# ul_y inside ' '
			elif pName == 'ul_y':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.UY_lineEdit.setText(g[0])
				else:
					cfg.ui.UY_lineEdit.setText('')
					return 'No', pName
			# lr_x inside ' '
			elif pName == 'lr_x':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.LX_lineEdit.setText(g[0])
				else:
					cfg.ui.LX_lineEdit.setText('')
					return 'No', pName
			# lr_y inside ' '
			elif pName == 'lr_y':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.LY_lineEdit.setText(g[0])
				else:
					cfg.ui.LY_lineEdit.setText('')
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.nodata_spinBox.setValue(val)
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputDir)
			parameters.append(shapefilePath)
			parameters.append(bandset)
			parameters.append(vector_field)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
															
	# batch reproject rasters
	def performReprojectRasters(self, paramList):
		alignRasterPath = 'None'
		epsgVal = 'None'
		bandset = 'None'
		xresolution = 'None'
		yresolution = 'None'
		resamplePixelSize = 'None'
		outName = 'None'
		outputNoData = 'None'
		dataType = 'None'
		sameExtent = '\'No\''
		resampling_methods = ['nearest_neighbour', 'near', 'average', 'average', 'sum', 'sum', 'maximum', 'max', 'minimum', 'min', 'mode', 'mode', 'median', 'med', 'first_quartile', 'q1', 'third_quartile', 'q3']
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output directory inside ' '
			if pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output name prefix inside ' '
			elif pName == 'output_name_prefix':
				g = pSplit[1].strip().replace('\'', '')
				if len(g) > 0:
					outName = '\'' + g + '\''
				else:
					return 'No', pName
			# resampling method inside ' '
			elif pName == 'resampling_method':
				g = pSplit[1].strip().replace('\'', '')
				if g in resampling_methods:
					if g == 'nearest_neighbour':
						g = 'near'
					elif g == 'average':
						g = 'average'
					elif g == 'sum':
						g = 'sum'
					elif g == 'maximum':
						g = 'max'
					elif g == 'minimum':
						g = 'min'
					elif g == 'mode':
						g = 'mode'
					elif g == 'median':
						g = 'med'
					elif g == 'first_quartile':
						g = 'q1'
					elif g == 'third_quartile':
						g = 'q3'
					resamplingMethod = '\'' + g + '\''
				else:
					return 'No', pName
			# data type prefix inside ' '
			elif pName == 'data_type':
				g = pSplit[1].strip().replace('\'', '')
				if len(g) > 0:
					if g.lower() == 'auto':
						dataType = 'None'
					else:
						dataType = '\'' + g + '\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# use extent checkbox (1 checked or 0 unchecked)
			elif pName == 'same_extent_reference':
				if pSplit[1].strip().replace(' ', '') == '1':
					sameExtent = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					sameExtent = '\'No\''
				else:
					return 'No', pName
			# raster path inside ' '
			elif pName == 'align_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					alignRasterPath = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# epsg  inside ' '
			elif pName == 'epsg':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					epsgVal = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# epsg  inside ' '
			elif pName == 'resample_pixel_size':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					resamplePixelSize = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# x resolution  inside ' '
			elif pName == 'x_resolution':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					xresolution = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'output_nodata_value':
				try:
					outputNoData = int(eval(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			# y resolution  inside ' '
			elif pName == 'y_resolution':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					yresolution = '\'' + g[0] + '\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputDir)
			parameters.append(alignRasterPath)
			parameters.append(sameExtent)
			parameters.append(epsgVal)
			parameters.append(xresolution)
			parameters.append(yresolution)
			parameters.append(resamplePixelSize)
			parameters.append(resamplingMethod)
			parameters.append(dataType)
			parameters.append(outputNoData)
			parameters.append(outName)
			parameters.append(bandset)
			if alignRasterPath == 'None' and epsgVal == 'None':
				return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch cloud masking
	def performCloudMasking(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output directory inside ' '
			if pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output name prefix inside ' '
			elif pName == 'output_name_prefix':
				g = pSplit[1].strip().replace('\'', '')
				if len(g) > 0:
					cfg.ui.mask_output_name_lineEdit.setText(g)
				else:
					cfg.ui.mask_output_name_lineEdit.setText('')
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# use buffer checkbox (1 checked or 0 unchecked)
			elif pName == 'use_buffer':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.cloud_buffer_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.cloud_buffer_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# size buffer value (int value)
			elif pName == 'size_in_pixels':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.cloud_buffer_spinBox.setValue(val)
				except:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.nodata_spinBox_11.setValue(val)
				except:
					return 'No', pName
			# input file path inside ' '
			elif pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# class values inside ' '
			elif pName == 'class_values':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.cloud_mask_classes_lineEdit.setText(g[0])
				else:
					cfg.ui.cloud_mask_classes_lineEdit.setText('')
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(bandset)
			parameters.append(inputRaster)
			parameters.append(outputDir)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch spectral distance band sets
	def performSpectralDistance(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output raster inside ' '
			if pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# band set number
			elif pName == 'first_band_set':
				try:
					bandset1 = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# band set number
			elif pName == 'second_band_set':
				try:
					bandset2 = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# method (1 minimum distance, 2 SAM)
			elif pName == 'distance_algorithm':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.min_distance_radioButton_2.setChecked(True)
					cfg.ui.spectral_angle_map_radioButton_2.setChecked(False)
				elif pSplit[1].strip().replace(' ', '') == '2':
					cfg.ui.min_distance_radioButton_2.setChecked(False)
					cfg.ui.spectral_angle_map_radioButton_2.setChecked(True)
				else:
					return 'No', pName
			# threshold checkbox (1 checked or 0 unchecked)
			elif pName == 'use_distance_threshold':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.distance_threshold_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.distance_threshold_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# threshold value (float value)
			elif pName == 'threshold_value':
				try:
					val = float(pSplit[1].strip().replace(' ', ''))
					cfg.ui.thresh_doubleSpinBox_2.setValue(val)
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(bandset1)
			parameters.append(bandset2)
			parameters.append(outputRaster)
			# batch
			parameters.append('\'Yes\'')
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch stack rasters
	def performStackRaster(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# band set number
			if pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# output file path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputRaster)
			parameters.append(bandset)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
	
	# batch reclassification
	def performReclassification(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# output file path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# reclassification values inside ' ' (list of oldValue_newValue separated by ,)
			elif pName == 'value_list':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				values = g[0]
				if len(values) > 0:
					valuesStr = values.split(',')
					valList = []
					for v in valuesStr:
						val = v.split('_')
						valList.append([float(val[0]), float(val[1])])
					values = '\'' + values + '\''
				else:
					return 'No', pName
			# use signature list code checkbox (1 checked or 0 unchecked)
			elif pName == 'use_signature_list_code':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.apply_symbology_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.apply_symbology_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# code field
			elif pName == 'code_field':
				id = cfg.ui.class_macroclass_comboBox_2.findText(pSplit[1].strip().strip().replace('\'', ''))
				if id >= 0:
					cfg.ui.class_macroclass_comboBox_2.setCurrentIndex(id)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
			parameters.append(values)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch classification sieve
	def performClassificationSieve(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# output file path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# size threshold value (int value)
			elif pName == 'size_threshold':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.sieve_threshold_spinBox.setValue(val)
				except:
					return 'No', pName
			# code field
			elif pName == 'pixel_connection':
				id = cfg.ui.sieve_connection_combo.findText(pSplit[1].strip().strip().replace('\'', ''))
				if id >= 0:
					cfg.ui.sieve_connection_combo.setCurrentIndex(id)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
				
	# batch classification erosion
	def performClassificationErosion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# output file path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# class values inside ' '
			elif pName == 'class_values':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.erosion_classes_lineEdit.setText(g[0])
				else:
					cfg.ui.erosion_classes_lineEdit.setText('')
					return 'No', pName
			# size threshold value (int value)
			elif pName == 'size_in_pixels':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.erosion_threshold_spinBox.setValue(val)
				except:
					return 'No', pName
			# circular checkbox (1 checked or 0 unchecked)
			elif pName == 'circular':
				if pSplit[1].strip().replace(' ', '') == '1':
					circular = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					circular = '\'No\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
					
	# batch classification dilation
	def performClassificationDilation(self, paramList):	
		circular = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# output file path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# class values inside ' '
			elif pName == 'class_values':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.dilation_classes_lineEdit.setText(g[0])
				else:
					cfg.ui.dilation_classes_lineEdit.setText('')
					return 'No', pName
			# size threshold value (int value)
			elif pName == 'size_in_pixels':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.dilation_threshold_spinBox.setValue(val)
				except:
					return 'No', pName
			# circular checkbox (1 checked or 0 unchecked)
			elif pName == 'circular':
				if pSplit[1].strip().replace(' ', '') == '1':
					circular = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					circular = '\'No\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
			parameters.append(circular)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
				
	# batch edit raster using vector
	def performEditRasterUsingVector(self, paramList):
		vectorFieldName = 'None'
		cfg.ui.edit_val_use_vector_radioButton.setChecked(True)
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# input vector inside ' '
			elif pName == 'input_vector_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputVector = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			# vector field name inside ' '
			elif pName == 'vector_field_name':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					vectorFieldName = '\'' + g[0] + '\''
					cfg.ui.use_field_vector_checkBox.setCheckState(2)
				else:
					return 'No', pName
			# expression inside ' '
			elif pName == 'expression':
				g = pSplit[1].strip().replace('\'', '')
				if len(g) > 0:
					cfg.ui.expression_lineEdit.setText(g)
					cfg.ui.use_expression_checkBox.setCheckState(2)
				else:
					cfg.ui.expression_lineEdit.setText('')
					return 'No', pName
			# constant value (int value)
			elif pName == 'constant_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.value_spinBox.setValue(val)
					cfg.ui.use_constant_val_checkBox.setCheckState(2)
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(inputRaster)
			parameters.append(inputVector)
			parameters.append(vectorFieldName)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch PCA
	def performPCA(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output directory inside ' '
			if pName == 'output_dir':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# use number of components checkbox (1 checked or 0 unchecked)
			elif pName == 'use_number_of_components':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.num_comp_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.num_comp_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# number of components (int value)
			elif pName == 'number_of_components':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.pca_components_spinBox.setValue(val)
				except:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.nodata_checkBox_4.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.nodata_checkBox_4.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.nodata_spinBox_5.setValue(val)
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputDir)
			parameters.append(bandset)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch Clustering
	def performClustering(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output path inside ' '
			if pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', ''))) - 1)
				except:
					return 'No', pName
			# number of classes (int value)
			elif pName == 'number_of_classes':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.kmeans_classes_spinBox.setValue(val)
				except:
					return 'No', pName
			# max number of iterations (int value)
			elif pName == 'max_iterations':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.kmeans_iter_spinBox.setValue(val)
				except:
					return 'No', pName
			# ISODATA maximum standard deviation (float value)
			elif pName == 'isodata_max_std_dev':
				try:
					val = float(pSplit[1].strip().replace(' ', ''))
					cfg.ui.std_dev_doubleSpinBox.setValue(val)
				except:
					return 'No', pName
			# ISODATA minimum class size (int value)
			elif pName == 'isodata_min_class_size':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.min_size_class_spinBox.setValue(val)
				except:
					return 'No', pName
			# threshold checkbox (1 checked or 0 unchecked)
			elif pName == 'use_distance_threshold':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.kmean_threshold_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.kmean_threshold_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# method (1 K-means, 2 ISODATA)
			elif pName == 'clustering_method':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.kmeans_radioButton.setChecked(True)
					cfg.ui.isodata_radioButton.setChecked(False)
				elif pSplit[1].strip().replace(' ', '') == '2':
					cfg.ui.kmeans_radioButton.setChecked(False)
					cfg.ui.isodata_radioButton.setChecked(True)
				else:
					return 'No', pName
			# seed signatures (1 from band values, 2 from signature list, or 3 random)
			elif pName == 'seed_signatures':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.kmean_minmax_radioButton.setChecked(True)
				elif pSplit[1].strip().replace(' ', '') == '2':
					cfg.ui.kmean_siglist_radioButton.setChecked(True)
				elif pSplit[1].strip().replace(' ', '') == '3':
					cfg.ui.kmean_randomsiglist_radioButton.setChecked(True)
				else:
					return 'No', pName
			# algorithm (1 Minimum Distance, 2 Spectral Angle Mapping)
			elif pName == 'distance_algorithm':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.min_distance_radioButton.setChecked(True)
				elif pSplit[1].strip().replace(' ', '') == '2':
					cfg.ui.spectral_angle_map_radioButton.setChecked(True)
				else:
					return 'No', pName
			# save signatures checkbox (1 checked or 0 unchecked)
			elif pName == 'save_signatures':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.kmean_save_siglist_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.kmean_save_siglist_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# threshold value (float value)
			elif pName == 'threshold_value':
				try:
					val = float(pSplit[1].strip().replace(' ', ''))
					cfg.ui.thresh_doubleSpinBox.setValue(val)
				except:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.nodata_checkBox_8.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.nodata_checkBox_8.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.nodata_spinBox_9.setValue(val)
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputRaster)
			parameters.append(bandset)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch accuracy
	def performAccuracy(self, paramList):
		shapefileField = 'None'
		useNoData = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# classification path inside ' '
			if pName == 'classification_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					classification = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# shapefile field name inside ' '
			elif pName == 'vector_field_name':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					shapefileField = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# reference path inside ' '
			elif pName == 'reference_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					reference = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'use_value_nodata':
				try:
					useNoData = int(eval(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append(classification)
			parameters.append(reference)
			parameters.append('\'Yes\'')
			parameters.append(shapefileField)
			parameters.append(outputRaster)
			parameters.append(useNoData)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
											
	# batch cross classification
	def performCrossClassification(self, paramList):
		shapefileField = 'None'
		NoDataValue = 'None'
		useNodata = 'No'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# classification path inside ' '
			if pName == 'classification_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					classification = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# shapefile field name inside ' '
			elif pName == 'vector_field_name':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					shapefileField = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# reference path inside ' '
			elif pName == 'reference_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					reference = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.nodata_checkBox_6.setCheckState(2)
					useNodata = 'Yes'
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.nodata_checkBox_6.setCheckState(0)
					useNodata = 'No'
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					NoDataValue = int(eval(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			# raster from regression checkbox (1 checked or 0 unchecked)
			elif pName == 'regression':
				if pSplit[1].strip().replace(' ', '') == '1':
					regression = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					regression = '\'No\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		if useNodata == 'No':
			NoDataValue = 'None'
		# append parameters
		try:
			# batch
			parameters.append(classification)
			parameters.append(reference)
			parameters.append('\'Yes\'')
			parameters.append(shapefileField)
			parameters.append(outputRaster)
			parameters.append(NoDataValue)
			parameters.append(regression)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
																	
	# batch zonal stat raster
	def performZonalStatRaster(self, paramList):
		shapefileField = 'None'
		statPerc = 'None'
		NoDataValue = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# inputRaster path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					inputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output path inside ' '
			elif pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# shapefile field name inside ' '
			elif pName == 'vector_field_name':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					shapefileField = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# statistic name inside ' '
			elif pName == 'statistic':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					statName = None
					for i in cfg.statisticList:
						if i[0].lower() == g[0].lower():
							statName = '\'' + g[0] + '\''
							break
					if statName is None:
						return 'No', pName
				else:
					return 'No', pName
			# reference path inside ' '
			elif pName == 'reference_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					reference = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.nodata_checkBox_10.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.nodata_checkBox_10.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					NoDataValue = int(eval(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			# stat value (int value)
			elif pName == 'stat_value':
				try:
					statPerc = int(eval(pSplit[1].strip().replace(' ', '')))
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(inputRaster)
			parameters.append(reference)
			parameters.append(shapefileField)
			parameters.append(outputRaster)
			parameters.append(statName)
			parameters.append(statPerc)
			parameters.append(NoDataValue)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
									
	# batch vector to raster
	def performVectorToRaster(self, paramList):
		vectorFieldName = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output path inside ' '
			if pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# input vector path inside ' '
			elif pName == 'vector_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					inputVector= '\'' + g[0] + '\''
				else:
					return 'No', pName
			# input vector field name ' '
			elif pName == 'vector_field_name':
				pSplitX = pSplit[1].strip()
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					vectorFieldName = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# use value field checkbox (1 checked or 0 unchecked)
			elif pName == 'use_value_field':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.field_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.field_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# extent same as reference (1 checked or 0 unchecked)
			elif pName == 'extent_same_as_reference':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.extent_checkBox_2.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.extent_checkBox_2.setCheckState(0)
				else:
					return 'No', pName
			# constant value (int value)
			elif pName == 'constant_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.constant_value_spinBox.setValue(val)
				except:
					return 'No', pName
			# type of conversion inside ' ' ('Center of pixels' , 'All pixels touched')
			elif pName == 'type_of_conversion':
				id = cfg.ui.conversion_type_combo.findText(pSplit[1].strip().strip().replace('\'', ''))
				if id >= 0:
					cfg.ui.conversion_type_combo.setCurrentIndex(id)
				else:
					return 'No', pName
			# input raster path inside ' '
			elif pName == 'reference_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					inputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputRaster)
			parameters.append(inputVector)
			parameters.append(vectorFieldName)
			parameters.append(inputRaster)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
																
	# batch Land Cover Change
	def performLandCoverChange(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output path inside ' '
			if pName == 'output_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# input raster path inside ' '
			elif pName == 'reference_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					refRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# input raster path inside ' '
			elif pName == 'new_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					newRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(refRaster)
			parameters.append(newRaster)
			parameters.append(outputRaster)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch classification report
	def performClassificationReport(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# output path inside ' '
			if pName == 'output_report_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputReport = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# input raster path inside ' '
			elif pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					inputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == 'use_nodata':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.nodata_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.nodata_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# nodata value (int value)
			elif pName == 'nodata_value':
				try:
					val = int(eval(pSplit[1].strip().replace(' ', '')))
					cfg.ui.nodata_spinBox_2.setValue(val)
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(inputRaster)
			parameters.append('None')
			# batch
			parameters.append('\'Yes\'')
			parameters.append(outputReport)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch classification to vector
	def performClassificationToVector(self, paramList):
		parameters = []
		dissolve = '\'No\''
		useCode = '\'No\''
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input raster path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					inputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output vector path inside ' '
			elif pName == 'output_vector_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputVector = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# use signature list code checkbox (1 checked or 0 unchecked)
			elif pName == 'use_signature_list_code':
				if pSplit[1].strip().replace(' ', '') == '1':
					useCode = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					useCode = '\'No\''
				else:
					return 'No', pName
			# use signature list code checkbox (1 checked or 0 unchecked)
			elif pName == 'dissolve_output':
				if pSplit[1].strip().replace(' ', '') == '1':
					dissolve = '\'Yes\''
				elif pSplit[1].strip().replace(' ', '') == '0':
					dissolve = '\'No\''
				else:
					return 'No', pName
			# code field
			elif pName == 'code_field':
				id = cfg.ui.class_macroclass_comboBox.findText(pSplit[1].strip().strip().replace('\'', ''))
				if id >= 0:
					cfg.ui.class_macroclass_comboBox.setCurrentIndex(id)
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(inputRaster)
			parameters.append(outputVector)
			parameters.append(dissolve)
			parameters.append(useCode)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
		
	# batch class signature
	def performClassSignature(self, paramList):
		bandset = 'None'
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input raster path inside ' '
			if pName == 'input_raster_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					inputRaster = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# output vector path inside ' '
			elif pName == 'output_text_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.utls.fileName(g[0])) > 0:
					outputText = '\'' + g[0] + '\''
				else:
					return 'No', pName
			# use signature list code checkbox (1 checked or 0 unchecked)
			elif pName == 'save_signatures':
				if pSplit[1].strip().replace(' ', '') == '1':
					cfg.ui.class_signature_save_siglist_checkBox.setCheckState(2)
				elif pSplit[1].strip().replace(' ', '') == '0':
					cfg.ui.class_signature_save_siglist_checkBox.setCheckState(0)
				else:
					return 'No', pName
			# band set number
			elif pName == 'band_set':
				try:
					bandset = str(int(eval(pSplit[1].strip().replace(' ', '')) - 1))
				except:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			# batch
			parameters.append('\'Yes\'')
			parameters.append(inputRaster)
			parameters.append(bandset)
			parameters.append(outputText)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
														
	# batch open training input
	def performOpenTrainingInput(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			# input file path inside ' '
			if pName == 'training_file_path':
				pSplitX = pSplit[1].strip()
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				file = '\'' + g[0] + '\''
				if len(cfg.utls.fileName(g[0])) > 0:
					pass
				else:
					return 'No', pName
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(file)
		except:
			return 'No', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'missing parameter')
		return 'Yes', parameters
				