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

class BatchTab:

	def __init__(self):
		pass

	# run
	def runButton(self):
		cfg.uiUtls.addProgressBar()
		cfg.cnvs.setRenderFlag(False)
		expression = " " + cfg.ui.plainTextEdit_batch.toPlainText() + " "
		e = expression.rstrip().split("\n")
		cfg.workingDir = None
		for nf in e:
			if len(nf.strip()) == 0:
				pass
			elif nf.strip()[0] == "#":
				pass
			else:
				function = self.checkExpression(nf)
				runFunction = function[0]
				if runFunction == "(" + cfg.workingDirNm + ")":
					pass
				else:
					if cfg.workingDir is not None:
						runFunction = runFunction.replace(cfg.workingDirNm, cfg.workingDir)
					eval(runFunction)
		cfg.utls.finishSound()
		cfg.cnvs.setRenderFlag(True)
		cfg.uiUtls.removeProgressBar()
		
	# text changed
	def textChanged(self):
		expression = " " + cfg.ui.plainTextEdit_batch.toPlainText() + " "
		self.checkExpression(expression)
		cfg.ui.plainTextEdit_batch.setFocus()
		
	# check the expression and return it
	def checkExpression(self, expression):
		cfg.ui.plainTextEdit_batch.setStyleSheet("color : red")
		e = expression.rstrip().split("\n")
		ex = []
		checkO = "Yes"
		errNf = ""
		for nf in e:
			if len(nf.strip()) == 0:
				pass
			elif nf.strip()[0] == "#":
				pass
			else:
				f = nf.split(";")
				nm = f[0].replace(" ", "")
				fNm, fRun, fList = cfg.batchT.replaceFunctionNames(nm)
				oldF = f
				errPar = ""
				# create function
				if fNm == "No":
					checkO = "No"
					errNf = nm
				else:
					try:
						check, parameters = eval(fNm + "(" + str(f[1:]) + ")")
						cfg.ui.plainTextEdit_batch.setStyleSheet("color : green")
						cfg.ui.toolButton_run_batch.setEnabled(True)
						cfg.ui.batch_label.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Check OK"))
						if check == "No":
							checkO = "No"
							errNf = nm
							if errPar is not None:
								errPar = parameters
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						checkO = "No"
						errNf = nm
				if checkO == "Yes":
					function = fRun + "("
					for p in parameters:
						function = function + p + ","
					function = function[:-1] + ")"
					ex.append(function)
				else:
					cfg.ui.batch_label.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Error in: ") + str(errNf) + " --> " + str(errPar))
					cfg.ui.plainTextEdit_batch.setStyleSheet("color : red")
					cfg.ui.toolButton_run_batch.setEnabled(False)
		return ex
			
	# replace function names
	def replaceFunctionNames(self, name):
		for i in cfg.functionNames:
			if name.lower() == i[0][0]:
				return i[0][1], i[0][2], i[0][3]
		return "No", "No", "No"
	
	# clear batch
	def clearBatch(self):
		cfg.ui.plainTextEdit_batch.setPlainText("")
						
	# import batch from text file
	def importBatch(self):
		file = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a batch file"), "", "txt (*.txt)")
		if len(file) > 0:
			text = open(file, 'r').read()
			cfg.ui.plainTextEdit_batch.setPlainText(text)
			
	# export batch to text file
	def exportBatch(self):
		file = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save the batch to file"), "", "*.txt", "txt")
		if file is not False:
			if file.lower().endswith(".txt"):
				pass
			else:
				file = file + ".txt"
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
			# name of item of list
			itN = i[0][0]
			# add list items to table
			tW.setRowCount(c + 1)
			cfg.utls.addTableItem(tW, itN, c, 0)
			tW.blockSignals(False)
			cfg.BandTabEdited = "Yes"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
				
	# set function
	def setFunction(self, index):
		pT = cfg.ui.plainTextEdit_batch
		tW = cfg.ui.batch_tableWidget
		text = pT.toPlainText()
		if len(text) > 0:
			space = "\n"
		else:
			space = ""
		nm = tW.item(index.row(), 0).text()
		fNm, fRun, fList = cfg.batchT.replaceFunctionNames(nm)
		if fNm != "No":
			text = text + space + nm + ";"
			for f in fList:
				text = text + f + ";"
			pT.setPlainText(text[:-1])
			pT.setFocus()
			
	# batch working directory
	def workingDirectory(self, paramList):
		parameters = []
		for p in paramList:
			# working directory inside " "
			g = cfg.reSCP.findall('[\'](.*?)[\']',p)
			workingDir = g[0].replace('\\', '/')
			if len(workingDir) > 0 and cfg.QDirSCP(workingDir).exists():
				cfg.workingDir =workingDir
			else:
				return "No", "workingDirectory"
		# append parameters
		try:
			parameters.append(cfg.workingDirNm)
		except:
			return "No", "workingDirectory"
		return "Yes", parameters
		
	# batch add raster
	def performAddRaster(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					file = "'" + g[0] + "'"
				else:
					return "No", pName
			elif pName == "input_raster_name":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0].strip()) > 0:
					name = "'" + g[0].strip() + "'"
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(file)
			parameters.append(name)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
									
	# batch Landsat conversion
	def performLandsatConversion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input directory inside " "
			if pName == "input_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.label_26.setText(g[0])
				inputDir = "'" + g[0] + "'"
				if len(g[0]) > 0 and cfg.QDirSCP(str(g[0])).exists():
					pass
				else:
					l = cfg.ui.landsat_tableWidget
					cfg.utls.clearTable(l)
					return "No", pName
			# output directory inside " "
			elif pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# MTL file path inside " "
			elif pName == "mtl_file_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.label_27.setText(g[0])
			# temperature in Celsius checkbox (1 checked or 0 unchecked)
			elif pName == "celsius_temperature":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.celsius_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.celsius_checkBox.setCheckState(0)
				else:
					return "No", pName
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == "apply_dos1":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_checkBox.setCheckState(0)
				else:
					return "No", pName
			# DOS1 only blue and green bands checkbox (1 checked or 0 unchecked)
			elif pName == "dos1_only_blue_green":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_bands_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_bands_checkBox.setCheckState(0)
				else:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_2.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_3.setValue(val)
				except:
					return "No", pName
			# pansharpening checkbox (1 checked or 0 unchecked)
			elif pName == "pansharpening":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.pansharpening_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.pansharpening_checkBox.setCheckState(0)
				else:
					return "No", pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == "create_bandset":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.create_bandset_checkBox.setCheckState(0)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(inputDir)
			parameters.append(outputDir)
			# batch
			parameters.append('"Yes"')
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		# populate table
		cfg.landsatT.populateTable(cfg.ui.label_26.text(), "Yes")
		return "Yes", parameters
															
	# batch ASTER conversion
	def performASTERConversion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.label_143.setText(g[0])
				inputFile = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					l = cfg.ui.ASTER_tableWidget
					cfg.utls.clearTable(l)
					return "No", pName
			# output directory inside " "
			elif pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# temperature in Celsius checkbox (1 checked or 0 unchecked)
			elif pName == "celsius_temperature":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.celsius_checkBox_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.celsius_checkBox_2.setCheckState(0)
				else:
					return "No", pName
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == "apply_dos1":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_checkBox_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_checkBox_2.setCheckState(0)
				else:
					return "No", pName
			# DOS1 only blue and green bands checkbox (1 checked or 0 unchecked)
			elif pName == "dos1_only_green":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_bands_checkBox_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_bands_checkBox_2.setCheckState(0)
				else:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_5.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_5.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_6.setValue(val)
				except:
					return "No", pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == "create_bandset":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.create_bandset_checkBox_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.create_bandset_checkBox_2.setCheckState(0)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(inputFile)
			parameters.append(outputDir)
			# batch
			parameters.append('"Yes"')
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		# populate table
		cfg.ASTERT.populateTable(cfg.ui.label_143.text(), "Yes")
		return "Yes", parameters
																			
	# batch MODIS conversion
	def performMODISConversion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.label_217.setText(g[0])
				inputFile = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					l = cfg.ui.MODIS_tableWidget
					cfg.utls.clearTable(l)
					return "No", pName
			# output directory inside " "
			elif pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# reproject to WGS 84 checkbox (1 checked or 0 unchecked)
			elif pName == "reproject_wgs84":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.reproject_modis_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.reproject_modis_checkBox.setCheckState(0)
				else:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_7.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_7.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_8.setValue(val)
				except:
					return "No", pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == "create_bandset":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.create_bandset_checkBox_3.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.create_bandset_checkBox_3.setCheckState(0)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(inputFile)
			parameters.append(outputDir)
			# batch
			parameters.append('"Yes"')
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		# populate table
		cfg.MODIST.populateTable(cfg.ui.label_217.text(), "Yes")
		return "Yes", parameters
						
	# batch Sentinel conversion
	def performSentinel2Conversion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input directory inside " "
			if pName == "input_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.S2_label_86.setText(g[0])
				inputDir = "'" + g[0] + "'"
				if len(g[0]) > 0 and cfg.QDirSCP(str(g[0])).exists():
					pass
				else:
					l = cfg.ui.sentinel_2_tableWidget
					cfg.utls.clearTable(l)
					return "No", pName
			# output directory inside " "
			elif pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# MTD_SAFL1C file path inside " "
			elif pName == "mtd_safl1c_file_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.S2_label_94.setText(g[0])
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == "apply_dos1":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_checkBox_S2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_checkBox_S2.setCheckState(0)
				else:
					return "No", pName
			# DOS1 only blue and green bands checkbox (1 checked or 0 unchecked)
			elif pName == "dos1_only_blue_green":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_bands_checkBox_S2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_bands_checkBox_S2.setCheckState(0)
				else:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.S2_nodata_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.S2_nodata_checkBox.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.S2_nodata_spinBox.setValue(val)
				except:
					return "No", pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == "create_bandset":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.S2_create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.S2_create_bandset_checkBox.setCheckState(0)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(inputDir)
			parameters.append(outputDir)
			# batch
			parameters.append('"Yes"')
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		# populate table
		cfg.sentinel2T.populateTable(cfg.ui.S2_label_86.text(), "Yes")
		return "Yes", parameters
										
	# batch Sentinel 3 conversion
	def performSentinel3Conversion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input directory inside " "
			if pName == "input_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				cfg.ui.S3_label_87.setText(g[0])
				inputDir = "'" + g[0] + "'"
				if len(g[0]) > 0 and cfg.QDirSCP(str(g[0])).exists():
					pass
				else:
					l = cfg.ui.sentinel_3_tableWidget
					cfg.utls.clearTable(l)
					return "No", pName
			# output directory inside " "
			elif pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == "apply_dos1":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_checkBox_S3.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_checkBox_S3.setCheckState(0)
				else:
					return "No", pName
			# DOS1 only blue and green bands checkbox (1 checked or 0 unchecked)
			elif pName == "dos1_only_blue_green":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_bands_checkBox_S2_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_bands_checkBox_S2_2.setCheckState(0)
				else:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.S3_nodata_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.S3_nodata_checkBox.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.S2_nodata_spinBox_2.setValue(val)
				except:
					return "No", pName
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == "create_bandset":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.S3_create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.S3_create_bandset_checkBox.setCheckState(0)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(inputDir)
			parameters.append(outputDir)
			# batch
			parameters.append('"Yes"')
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		# populate table
		cfg.sentinel3T.populateTable(cfg.ui.S3_label_87.text(), "Yes")
		return "Yes", parameters
																
	# batch classification
	def performClassification(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output classification inside " "
			if pName == "output_classification_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					outputClassification = "'" + g[0] + "'"
				else:
					return "No", pName
			# use macroclass checkbox (1 checked or 0 unchecked)
			elif pName == "use_macroclass":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.macroclass_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.macroclass_checkBox.setCheckState(0)
				else:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# use LCS checkbox (1 checked or 0 unchecked)
			elif pName == "use_lcs":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.LC_signature_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.LC_signature_checkBox.setCheckState(0)
				else:
					return "No", pName
			# use LCS with algorithm checkbox (1 checked or 0 unchecked)
			elif pName == "use_lcs_algorithm":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.LCS_class_algorithm_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.LCS_class_algorithm_checkBox.setCheckState(0)
				else:
					return "No", pName
			# use LCS only overlap checkbox (1 checked or 0 unchecked)
			elif pName == "use_lcs_only_overlap":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.LCS_leave_unclassified_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.LCS_leave_unclassified_checkBox.setCheckState(0)
				else:
					return "No", pName
			# apply mask checkbox (1 checked or 0 unchecked)
			elif pName == "apply_mask":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.mask_checkBox.blockSignals(True)
					cfg.uidc.mask_checkBox.setCheckState(2)
					cfg.uidc.mask_checkBox.blockSignals(False)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.mask_checkBox.blockSignals(True)
					cfg.uidc.mask_checkBox.setCheckState(0)
					cfg.uidc.mask_checkBox.blockSignals(False)
				else:
					return "No", pName
			# mask file path inside " "
			elif pName == "mask_file_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					cfg.uidc.mask_lineEdit.setText(g[0])
				else:
					cfg.uidc.mask_lineEdit.setText("")
					return "No", pName
			# vector output checkbox (1 checked or 0 unchecked)
			elif pName == "vector_output":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.vector_output_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.vector_output_checkBox.setCheckState(0)
				else:
					return "No", pName
			# classification report checkbox (1 checked or 0 unchecked)
			elif pName == "classification_report":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.report_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.report_checkBox.setCheckState(0)
				else:
					return "No", pName
			# save algorithm files checkbox (1 checked or 0 unchecked)
			elif pName == "save_algorithm_files":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.alg_files_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.alg_files_checkBox.setCheckState(0)
				else:
					return "No", pName
			# algorithm name "Minimum Distance" "Maximum Likelihood" "Spectral Angle Mapping"
			elif pName == "algorithm_name":
				id = cfg.uidc.algorithm_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.uidc.algorithm_combo.setCurrentIndex(id)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputClassification)
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
										
	# batch create band set
	def performBandSetCreation(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " " separated by ,
			if pName == "raster_path_list":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				files = g[0]
				if len(files) > 0:
					files = "'" + files + "'"
				else:
					return "No", pName
			#  wavelength unit 0=number 1=u"µm (1 E-6m)" 2="nm (1 E-9m)"
			elif pName == "wavelength_unit":
				if pSplit[1].replace(" ", "") == "0":
					noUnitId = cfg.ui.unit_combo.findText(cfg.wlMicro)
					cfg.ui.unit_combo.setCurrentIndex(noUnitId)
					id = cfg.ui.unit_combo.findText(cfg.noUnit)
					cfg.ui.unit_combo.setCurrentIndex(id)
				elif pSplit[1].replace(" ", "") == "1":
					noUnitId = cfg.ui.unit_combo.findText(cfg.noUnit)
					cfg.ui.unit_combo.setCurrentIndex(noUnitId)
					id = cfg.ui.unit_combo.findText(cfg.wlMicro)
					cfg.ui.unit_combo.setCurrentIndex(id)
				elif pSplit[1].replace(" ", "") == "2":
					noUnitId = cfg.ui.unit_combo.findText(cfg.noUnit)
					cfg.ui.unit_combo.setCurrentIndex(noUnitId)
					id = cfg.ui.unit_combo.findText(cfg.wlNano)
					cfg.ui.unit_combo.setCurrentIndex(id)
				else:
					return "No", pName
			# center wavelength inside " " separated by ,
			elif pName == "center_wavelength":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				center_wavelength = g[0]
				if len(center_wavelength) > 0:
					center_wavelength = "'" + center_wavelength + "'"
				else:
					return "No", pName
			# multiplicative factor inside " " separated by ,
			elif pName == "multiplicative_factor":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				multiplicative_factor = g[0]
				if len(multiplicative_factor) > 0:
					multiplicative_factor = "'" + multiplicative_factor + "'"
				else:
					return "No", pName
			# additive factor inside " " separated by ,
			elif pName == "additive_factor":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				additive_factor = g[0]
				if len(additive_factor) > 0:
					additive_factor = "'" + additive_factor + "'"
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(files)
			try:
				parameters.append(center_wavelength)
			except:
				parameters.append('""')
			try:
				parameters.append(multiplicative_factor)
			except:
				parameters.append('""')
			try:
				parameters.append(additive_factor)
			except:
				parameters.append('""')
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters	
		
	# batch select band set
	def performBandSetSelection(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			if pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch remove band set
	def performRemoveBandSet(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			if pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch add new band set
	def performAddNewBandSet(self, paramList):
		parameters = []
		parameters.append('"Yes"')
		return "Yes", parameters
									
	# batch band combination
	def performBandCombination(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			if pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# output file path inside " "
			elif pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			else:
				return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(bandset)
			parameters.append(outputRaster)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
																								
	# batch split raster
	def performSplitRaster(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				file = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# output directory inside " "
			elif pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# output name prefix inside " "
			elif pName == "output_name_prefix":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					cfg.ui.output_name_lineEdit.setText(g)
				else:
					cfg.ui.output_name_lineEdit.setText("")
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"No"')
			parameters.append('"Yes"')
			parameters.append(file)
			parameters.append(outputDir)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# mosaic band sets
	def performMosaicBandSets(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output directory inside " "
			if pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# output name prefix inside " "
			elif pName == "output_name_prefix":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					cfg.ui.mosaic_output_name_lineEdit.setText(g)
				else:
					cfg.ui.mosaic_output_name_lineEdit.setText("")
					return "No", pName
			# band set list " " separated by ,
			elif pName == "band_set_list":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				band_set_list = g[0]
				if len(band_set_list) > 0:
					band_set_list = '"[' + band_set_list + ']"'
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputDir)
			parameters.append(band_set_list)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters

	# batch band calc
	def performBandCalc(self, paramList):
		extentRaster = "None"
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# expression inside " "
			if pName == "expression":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					expr = "'" + g + "'"
				else:
					return "No", pName
			# output file path inside " "
			elif pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# extent same as raster name inside " "
			elif pName == "extent_same_as_raster_name":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				extentRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					cfg.ui.extent_checkBox.setCheckState(2)
				else:
					return "No", pName
			# extent checkbox (1 checked or 0 unchecked)
			elif pName == "extent_intersection":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.intersection_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.intersection_checkBox.setCheckState(0)
					cfg.ui.extent_checkBox.setCheckState(0)
				else:
					return "No", pName
			# align checkbox (1 checked or 0 unchecked)
			elif pName == "align":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.align_radioButton.setChecked(True)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.align_radioButton.setChecked(False)
				else:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "set_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_3.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_3.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_4.setValue(val)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append(outputRaster)
			parameters.append('"Yes"')
			parameters.append(expr)
			parameters.append(extentRaster)
			parameters.append("None")
			parameters.append('"No"')
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
																									
	# batch clip rasters
	def performClipRasters(self, paramList):
		shapefilePath = "None"
		vector_field = "None"
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output directory inside " "
			if pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# output name prefix inside " "
			elif pName == "output_name_prefix":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					cfg.ui.output_clip_name_lineEdit.setText(g)
				else:
					cfg.ui.output_clip_name_lineEdit.setText("")
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# use vector checkbox (1 checked or 0 unchecked)
			elif pName == "use_vector":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.shapefile_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.shapefile_checkBox.setCheckState(0)
				else:
					return "No", pName
			# use vector field checkbox (1 checked or 0 unchecked)
			elif pName == "use_vector_field":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.vector_field_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.vector_field_checkBox.setCheckState(0)
				else:
					return "No", pName
			# vector path inside " "
			elif pName == "vector_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					shapefilePath = "'" + g[0] + "'"
				else:
					return "No", pName
			# vector field inside " "
			elif pName == "vector_field":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					vector_field = "'" + g[0] + "'"
				else:
					return "No", pName
			# ul_x inside " "
			elif pName == "ul_x":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.UX_lineEdit.setText(g[0])
				else:
					cfg.ui.UX_lineEdit.setText("")
					return "No", pName
			# ul_y inside " "
			elif pName == "ul_y":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.UY_lineEdit.setText(g[0])
				else:
					cfg.ui.UY_lineEdit.setText("")
					return "No", pName
			# lr_x inside " "
			elif pName == "lr_x":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.LX_lineEdit.setText(g[0])
				else:
					cfg.ui.LX_lineEdit.setText("")
					return "No", pName
			# lr_y inside " "
			elif pName == "lr_y":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.LY_lineEdit.setText(g[0])
				else:
					cfg.ui.LY_lineEdit.setText("")
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox.setValue(val)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputDir)
			parameters.append(shapefilePath)
			parameters.append(bandset)
			parameters.append(vector_field)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters																								
	# batch cloud masking
	def performCloudMasking(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output directory inside " "
			if pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# output name prefix inside " "
			elif pName == "output_name_prefix":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					cfg.ui.mask_output_name_lineEdit.setText(g)
				else:
					cfg.ui.mask_output_name_lineEdit.setText("")
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# use buffer checkbox (1 checked or 0 unchecked)
			elif pName == "use_buffer":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.cloud_buffer_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.cloud_buffer_checkBox.setCheckState(0)
				else:
					return "No", pName
			# size buffer value (int value)
			elif pName == "size_in_pixels":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.cloud_buffer_spinBox.setValue(val)
				except:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_11.setValue(val)
				except:
					return "No", pName
			# input file path inside " "
			elif pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# class values inside " "
			elif pName == "class_values":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.cloud_mask_classes_lineEdit.setText(g[0])
				else:
					cfg.ui.cloud_mask_classes_lineEdit.setText("")
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(bandset)
			parameters.append(inputRaster)
			parameters.append(outputDir)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch spectral distance band sets
	def performSpectralDistance(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output directory inside " "
			if pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# band set number
			elif pName == "first_band_set":
				try:
					bandset1 = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# band set number
			elif pName == "second_band_set":
				try:
					bandset2 = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# method (1 minimum distance, 2 SAM)
			elif pName == "distance_algorithm":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.min_distance_radioButton_2.setChecked(True)
					cfg.ui.spectral_angle_map_radioButton_2.setChecked(False)
				elif pSplit[1].replace(" ", "") == "2":
					cfg.ui.min_distance_radioButton_2.setChecked(False)
					cfg.ui.spectral_angle_map_radioButton_2.setChecked(True)
				else:
					return "No", pName
			# threshold checkbox (1 checked or 0 unchecked)
			elif pName == "use_distance_threshold":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.distance_threshold_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.distance_threshold_checkBox.setCheckState(0)
				else:
					return "No", pName
			# threshold value (float value)
			elif pName == "threshold_value":
				try:
					val = float(pSplit[1].replace(" ", ""))
					cfg.ui.thresh_doubleSpinBox_2.setValue(val)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(bandset1)
			parameters.append(bandset2)
			parameters.append(outputDir)
			# batch
			parameters.append('"Yes"')
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch stack rasters
	def performStackRaster(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# band set number
			if pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# output file path inside " "
			elif pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputRaster)
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
	
	# batch reclassification
	def performReclassification(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# output file path inside " "
			elif pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# reclassification values inside " " (list of oldValue_newValue separated by ,)
			elif pName == "value_list":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				values = g[0]
				if len(values) > 0:
					valuesStr = values.split(",")
					valList = []
					for v in valuesStr:
						val = v.split("_")
						valList.append([float(val[0]), float(val[1])])
					values = "'" + values + "'"
				else:
					return "No", pName
			# use signature list code checkbox (1 checked or 0 unchecked)
			elif pName == "use_signature_list_code":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.apply_symbology_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.apply_symbology_checkBox.setCheckState(0)
				else:
					return "No", pName
			# code field
			elif pName == "code_field":
				id = cfg.ui.class_macroclass_comboBox_2.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.class_macroclass_comboBox_2.setCurrentIndex(id)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
			parameters.append(values)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch classification sieve
	def performClassificationSieve(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# output file path inside " "
			elif pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# size threshold value (int value)
			elif pName == "size_threshold":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.sieve_threshold_spinBox.setValue(val)
				except:
					return "No", pName
			# code field
			elif pName == "pixel_connection":
				id = cfg.ui.sieve_connection_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.sieve_connection_combo.setCurrentIndex(id)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
				
	# batch classification erosion
	def performClassificationErosion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# output file path inside " "
			elif pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# class values inside " "
			elif pName == "class_values":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.erosion_classes_lineEdit.setText(g[0])
				else:
					cfg.ui.erosion_classes_lineEdit.setText("")
					return "No", pName
			# size threshold value (int value)
			elif pName == "size_in_pixels":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.erosion_threshold_spinBox.setValue(val)
				except:
					return "No", pName
			# code field
			elif pName == "pixel_connection":
				id = cfg.ui.erosion_connection_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.erosion_connection_combo.setCurrentIndex(id)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
					
	# batch classification dilation
	def performClassificationDilation(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# output file path inside " "
			elif pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				outputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# class values inside " "
			elif pName == "class_values":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					cfg.ui.dilation_classes_lineEdit.setText(g[0])
				else:
					cfg.ui.dilation_classes_lineEdit.setText("")
					return "No", pName
			# size threshold value (int value)
			elif pName == "size_in_pixels":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.dilation_threshold_spinBox.setValue(val)
				except:
					return "No", pName
			# code field
			elif pName == "pixel_connection":
				id = cfg.ui.dilation_connection_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.dilation_connection_combo.setCurrentIndex(id)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
				
	# batch edit raster using vector
	def performEditRasterUsingVector(self, paramList):
		vectorFieldName = "None"
		cfg.ui.edit_val_use_vector_radioButton.setChecked(True)
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputRaster = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# input vector inside " "
			elif pName == "input_vector_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				inputVector = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			# vector field name inside " "
			elif pName == "vector_field_name":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					vectorFieldName = "'" + g[0] + "'"
					cfg.ui.use_field_vector_checkBox.setCheckState(2)
				else:
					return "No", pName
			# expression inside " "
			elif pName == "expression":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					cfg.ui.expression_lineEdit.setText(g)
					cfg.ui.use_expression_checkBox.setCheckState(2)
				else:
					cfg.ui.expression_lineEdit.setText("")
					return "No", pName
			# constant value (int value)
			elif pName == "constant_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.value_spinBox.setValue(val)
					cfg.ui.use_constant_val_checkBox.setCheckState(2)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(inputVector)
			parameters.append(vectorFieldName)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch PCA
	def performPCA(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output directory inside " "
			if pName == "output_dir":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", pName
			# use number of components checkbox (1 checked or 0 unchecked)
			elif pName == "use_number_of_components":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.num_comp_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.num_comp_checkBox.setCheckState(0)
				else:
					return "No", pName
			# number of components (int value)
			elif pName == "number_of_components":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.pca_components_spinBox.setValue(val)
				except:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_4.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_4.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_5.setValue(val)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputDir)
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch Clustering
	def performClustering(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output path inside " "
			if pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					outputRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			# number of classes (int value)
			elif pName == "number_of_classes":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.kmeans_classes_spinBox.setValue(val)
				except:
					return "No", pName
			# max number of iterations (int value)
			elif pName == "max_iterations":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.kmeans_iter_spinBox.setValue(val)
				except:
					return "No", pName
			# ISODATA maximum standard deviation (float value)
			elif pName == "isodata_max_std_dev":
				try:
					val = float(pSplit[1].replace(" ", ""))
					cfg.ui.std_dev_doubleSpinBox.setValue(val)
				except:
					return "No", pName
			# ISODATA minimum class size (int value)
			elif pName == "isodata_min_class_size":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.min_size_class_spinBox.setValue(val)
				except:
					return "No", pName
			# threshold checkbox (1 checked or 0 unchecked)
			elif pName == "use_distance_threshold":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.kmean_threshold_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.kmean_threshold_checkBox.setCheckState(0)
				else:
					return "No", pName
			# method (1 K-means, 2 ISODATA)
			elif pName == "clustering_method":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.kmeans_radioButton.setChecked(True)
					cfg.ui.isodata_radioButton.setChecked(False)
				elif pSplit[1].replace(" ", "") == "2":
					cfg.ui.kmeans_radioButton.setChecked(False)
					cfg.ui.isodata_radioButton.setChecked(True)
				else:
					return "No", pName
			# seed signatures (1 from band values, 2 from signature list, or 3 random)
			elif pName == "seed_signatures":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.kmean_minmax_radioButton.setChecked(True)
				elif pSplit[1].replace(" ", "") == "2":
					cfg.ui.kmean_siglist_radioButton.setChecked(True)
				elif pSplit[1].replace(" ", "") == "3":
					cfg.ui.kmean_randomsiglist_radioButton.setChecked(True)
				else:
					return "No", pName
			# algorithm (1 Minimum Distance, 2 Spectral Angle Mapping)
			elif pName == "distance_algorithm":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.min_distance_radioButton.setChecked(True)
				elif pSplit[1].replace(" ", "") == "2":
					cfg.ui.spectral_angle_map_radioButton.setChecked(True)
				else:
					return "No", pName
			# save signatures checkbox (1 checked or 0 unchecked)
			elif pName == "save_signatures":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.kmean_save_siglist_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.kmean_save_siglist_checkBox.setCheckState(0)
				else:
					return "No", pName
			# threshold value (float value)
			elif pName == "threshold_value":
				try:
					val = float(pSplit[1].replace(" ", ""))
					cfg.ui.thresh_doubleSpinBox.setValue(val)
				except:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_8.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_8.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_9.setValue(val)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputRaster)
			parameters.append(bandset)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch accuracy
	def performAccuracy(self, paramList):
		shapefileField = "None"
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# classification path inside " "
			if pName == "classification_file_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					classification = "'" + g[0] + "'"
				else:
					return "No", pName
			# output path inside " "
			elif pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					outputRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			# shapefile field name inside " "
			elif pName == "vector_field_name":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					shapefileField = "'" + g[0] + "'"
				else:
					return "No", pName
			# reference path inside " "
			elif pName == "reference_file_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					reference = "'" + g[0] + "'"
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append(classification)
			parameters.append(reference)
			parameters.append('"Yes"')
			parameters.append(shapefileField)
			parameters.append(outputRaster)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
											
	# batch cross classification
	def performCrossClassification(self, paramList):
		shapefileField = "None"
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# classification path inside " "
			if pName == "classification_file_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					classification = "'" + g[0] + "'"
				else:
					return "No", pName
			# output path inside " "
			elif pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					outputRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			# shapefile field name inside " "
			elif pName == "vector_field_name":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					shapefileField = "'" + g[0] + "'"
				else:
					return "No", pName
			# reference path inside " "
			elif pName == "reference_file_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					reference = "'" + g[0] + "'"
				else:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_6.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_6.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_7.setValue(val)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append(classification)
			parameters.append(reference)
			parameters.append('"Yes"')
			parameters.append(shapefileField)
			parameters.append(outputRaster)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
									
	# batch vector to raster
	def performVectorToRaster(self, paramList):
		vectorFieldName = "None"
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output path inside " "
			if pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					outputRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			# input vector path inside " "
			elif pName == "vector_file_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					inputVector= "'" + g[0] + "'"
				else:
					return "No", pName
			# input vector field name " "
			elif pName == "vector_field_name":
				pSplitX = pSplit[1]
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(g[0]) > 0:
					vectorFieldName = "'" + g[0] + "'"
				else:
					return "No", pName
			# use value field checkbox (1 checked or 0 unchecked)
			elif pName == "use_value_field":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.field_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.field_checkBox.setCheckState(0)
				else:
					return "No", pName
			# constant value (int value)
			elif pName == "constant_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.constant_value_spinBox.setValue(val)
				except:
					return "No", pName
			# type of conversion inside " " ("Center of pixels" , "All pixels touched")
			elif pName == "type_of_conversion":
				id = cfg.ui.conversion_type_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.conversion_type_combo.setCurrentIndex(id)
				else:
					return "No", pName
			# input raster path inside " "
			elif pName == "reference_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					inputRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputRaster)
			parameters.append(inputVector)
			parameters.append(vectorFieldName)
			parameters.append(inputRaster)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
																
	# batch Land Cover Change
	def performLandCoverChange(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output path inside " "
			if pName == "output_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					outputRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			# input raster path inside " "
			elif pName == "reference_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					refRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			# input raster path inside " "
			elif pName == "new_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					newRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(refRaster)
			parameters.append(newRaster)
			parameters.append(outputRaster)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch classification report
	def performClassificationReport(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# output path inside " "
			if pName == "output_report_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					outputReport = "'" + g[0] + "'"
				else:
					return "No", pName
			# input raster path inside " "
			elif pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					inputRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox.setCheckState(0)
				else:
					return "No", pName
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_2.setValue(val)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(inputRaster)
			parameters.append("None")
			# batch
			parameters.append('"Yes"')
			parameters.append(outputReport)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch classification to vector
	def performClassificationToVector(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input raster path inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					inputRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			# output vector path inside " "
			elif pName == "output_vector_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					outputVector = "'" + g[0] + "'"
				else:
					return "No", pName
			# use signature list code checkbox (1 checked or 0 unchecked)
			elif pName == "use_signature_list_code":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.use_class_code_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.use_class_code_checkBox.setCheckState(0)
				else:
					return "No", pName
			# code field
			elif pName == "code_field":
				id = cfg.ui.class_macroclass_comboBox.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.class_macroclass_comboBox.setCurrentIndex(id)
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputVector)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
		
	# batch class signature
	def performClassSignature(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input raster path inside " "
			if pName == "input_raster_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					inputRaster = "'" + g[0] + "'"
				else:
					return "No", pName
			# output vector path inside " "
			elif pName == "output_text_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					outputText = "'" + g[0] + "'"
				else:
					return "No", pName
			# use signature list code checkbox (1 checked or 0 unchecked)
			elif pName == "save_signatures":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.class_signature_save_siglist_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.class_signature_save_siglist_checkBox.setCheckState(0)
				else:
					return "No", pName
			# band set number
			elif pName == "band_set":
				try:
					bandset = str(int(pSplit[1].replace(" ", "")) - 1)
				except:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(bandset)
			parameters.append(outputText)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
														
	# batch open training input
	def performOpenTrainingInput(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":", 1)
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "training_file_path":
				pSplitX = pSplit[1]
				if cfg.workingDir is not None:
					pSplitX = pSplitX.replace(cfg.workingDirNm, cfg.workingDir)
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplitX.replace('\\', '/'))
				file = "'" + g[0] + "'"
				if len(cfg.osSCP.path.basename(g[0])) > 0:
					pass
				else:
					return "No", pName
			else:
				return "No", pName
		# append parameters
		try:
			parameters.append(file)
		except:
			return "No", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "missing parameter")
		return "Yes", parameters
				