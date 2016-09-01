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
		for nf in e:
			f = nf.split(";")
			nm = f[0].replace(" ", "")
			fNm, fRun, fList = cfg.batchT.replaceFunctionNames(nm)
			oldF = f
			# create function
			if fNm == "No":
				checkO = "No"
			else:
				try:
					check, parameters = eval(fNm + "(" + str(f[1:]) + ")")
					cfg.ui.plainTextEdit_batch.setStyleSheet("color : green")
					cfg.ui.toolButton_run_batch.setEnabled(True)
					if check == "No":
						checkO = "No"
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					checkO = "No"
			if checkO == "Yes":
				function = fRun + "("
				for p in parameters:
					function = function + p + ","
				function = function[:-1] + ")"
				ex.append(function)
			else:
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
		file = cfg.utls.getOpenFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a batch file"), "", "txt (*.txt)")
		if len(file) > 0:
			text = open(file, 'r').read()
			cfg.ui.plainTextEdit_batch.setPlainText(text)
			
	# export batch to text file
	def exportBatch(self):
		file = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save the batch to file"), "", "txt (*.txt)")
		if len(file) > 0:
			if file.lower().endswith(".txt"):
				pass
			else:
				file = file + ".txt"
			f = cfg.ui.plainTextEdit_batch.toPlainText()
			o = open(file, 'w')
			o.write(f)
			o.close()
				
	# add function list to combo
	def addFunctionsToCombo(self, functionList):
		cfg.ui.batch_function_combo.addItem("")
		for i in functionList:
			cfg.ui.batch_function_combo.addItem(i[0][0])
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
				
	# set function
	def setFunction(self):
		pT = cfg.ui.plainTextEdit_batch
		text = pT.toPlainText()
		if len(text) > 0:
			space = "\n"
		else:
			space = ""
		nm = cfg.ui.batch_function_combo.currentText()
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
			workingDir = g[0]
			if len(workingDir) > 0 and cfg.QDirSCP(workingDir).exists():
				cfg.workingDir =workingDir
			else:
				return "No", "No"
		# append parameters
		try:
			parameters.append(cfg.workingDirNm)
		except:
			return "No", "No"
		return "Yes", parameters
		
	# batch add raster
	def performAddRaster(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					file = "'" + g[0] + "'"
				else:
					return "No", "No"
			elif pName == "input_raster_name":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					name = "'" + g.strip() + "'"
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			parameters.append(file)
			parameters.append(name)
		except:
			return "No", "No"
		return "Yes", parameters
									
	# batch Landsat conversion
	def performLandsatConversion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input directory inside " "
			if pName == "input_dir":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				cfg.ui.label_26.setText(g[0])
				inputDir = "'" + g[0] + "'"
				if len(g[0]) > 0 and cfg.QDirSCP(unicode(g[0])).exists():
					pass
				else:
					l = cfg.ui.landsat_tableWidget
					cfg.utls.clearTable(l)
					return "No", "No"
			# output directory inside " "
			elif pName == "output_dir":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", "No"
			# MTL file path inside " "
			elif pName == "mtl_file_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				cfg.ui.label_27.setText(g[0])
			# temperature in Celsius checkbox (1 checked or 0 unchecked)
			elif pName == "celsius_temperature":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.celsius_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.celsius_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == "apply_dos1":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_2.setCheckState(0)
				else:
					return "No", "No"
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_3.setValue(val)
				except:
					return "No", "No"
			# pansharpening checkbox (1 checked or 0 unchecked)
			elif pName == "pansharpening":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.pansharpening_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.pansharpening_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == "create_bandset":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.create_bandset_checkBox.setCheckState(0)
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			parameters.append(inputDir)
			parameters.append(outputDir)
			# batch
			parameters.append('"Yes"')
		except:
			return "No", "No"
		# populate table
		cfg.landsatT.populateTable(cfg.ui.label_26.text(), "Yes")
		return "Yes", parameters
															
	# batch ASTER conversion
	def performASTERConversion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file inside " "
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				cfg.ui.label_143.setText(g[0])
				inputFile = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					l = cfg.ui.ASTER_tableWidget
					cfg.utls.clearTable(l)
					return "No", "No"
			# output directory inside " "
			elif pName == "output_dir":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", "No"
			# temperature in Celsius checkbox (1 checked or 0 unchecked)
			elif pName == "celsius_temperature":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.celsius_checkBox_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.celsius_checkBox_2.setCheckState(0)
				else:
					return "No", "No"
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == "apply_dos1":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_checkBox_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_checkBox_2.setCheckState(0)
				else:
					return "No", "No"
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_5.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_5.setCheckState(0)
				else:
					return "No", "No"
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_6.setValue(val)
				except:
					return "No", "No"
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == "create_bandset":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.create_bandset_checkBox_2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.create_bandset_checkBox_2.setCheckState(0)
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			parameters.append(inputFile)
			parameters.append(outputDir)
			# batch
			parameters.append('"Yes"')
		except:
			return "No", "No"
		# populate table
		cfg.ASTERT.populateTable(cfg.ui.label_143.text(), "Yes")
		return "Yes", parameters
						
	# batch Sentinel conversion
	def performSentinelConversion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input directory inside " "
			if pName == "input_dir":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				cfg.ui.S2_label_86.setText(g[0])
				inputDir = "'" + g[0] + "'"
				if len(g[0]) > 0 and cfg.QDirSCP(unicode(g[0])).exists():
					pass
				else:
					l = cfg.ui.sentinel_2_tableWidget
					cfg.utls.clearTable(l)
					return "No", "No"
			# output directory inside " "
			elif pName == "output_dir":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", "No"
			# MTD_SAFL1C file path inside " "
			elif pName == "mtd_safl1c_file_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				cfg.ui.S2_label_94.setText(g[0])
			# DOS1 checkbox (1 checked or 0 unchecked)
			elif pName == "apply_dos1":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.DOS1_checkBox_S2.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.DOS1_checkBox_S2.setCheckState(0)
				else:
					return "No", "No"
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.S2_nodata_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.S2_nodata_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.S2_nodata_spinBox.setValue(val)
				except:
					return "No", "No"
			# bandset checkbox (1 checked or 0 unchecked)
			elif pName == "create_bandset":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.S2_create_bandset_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.S2_create_bandset_checkBox.setCheckState(0)
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			parameters.append(inputDir)
			parameters.append(outputDir)
			# batch
			parameters.append('"Yes"')
		except:
			return "No", "No"
		# populate table
		cfg.sentinel2T.populateTable(cfg.ui.S2_label_86.text(), "Yes")
		return "Yes", parameters
																
	# batch classification
	def performClassification(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# output classification inside " "
			if pName == "output_classification_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputClassification = "'" + g[0] + "'"
				else:
					return "No", "No"
			# use macroclass checkbox (1 checked or 0 unchecked)
			elif pName == "use_macroclass":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.macroclass_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.macroclass_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# use LCS checkbox (1 checked or 0 unchecked)
			elif pName == "use_lcs":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.LC_signature_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.LC_signature_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# use LCS with algorithm checkbox (1 checked or 0 unchecked)
			elif pName == "use_lcs_algorithm":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.LCS_class_algorithm_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.LCS_class_algorithm_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# use LCS only overlap checkbox (1 checked or 0 unchecked)
			elif pName == "use_lcs_only_overlap":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.LCS_leave_unclassified_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.LCS_leave_unclassified_checkBox.setCheckState(0)
				else:
					return "No", "No"
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
					return "No", "No"
			# mask file path inside " "
			elif pName == "mask_file_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					cfg.uidc.mask_lineEdit.setText(g[0])
				else:
					cfg.uidc.mask_lineEdit.setText("")
					return "No", "No"
			# vector output checkbox (1 checked or 0 unchecked)
			elif pName == "vector_output":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.vector_output_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.vector_output_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# classification report checkbox (1 checked or 0 unchecked)
			elif pName == "classification_report":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.report_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.report_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# save algorithm files checkbox (1 checked or 0 unchecked)
			elif pName == "save_algorithm_files":
				if pSplit[1].replace(" ", "") == "1":
					cfg.uidc.alg_files_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.uidc.alg_files_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# algorithm name "Minimum Distance" "Maximum Likelihood" "Spectral Angle Mapping"
			elif pName == "algorithm_name":
				id = cfg.uidc.algorithm_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.uidc.algorithm_combo.setCurrentIndex(id)
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputClassification)
		except:
			return "No", "No"
		return "Yes", parameters
										
	# batch create band set
	def performBandSetCreation(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " " separated by ,
			if pName == "raster_path_list":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				files = g[0]
				if len(files) > 0:
					files = "'" + files + "'"
				else:
					return "No", "No"
			# center wavelength inside " " separated by ,
			elif pName == "center_wavelength":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				center_wavelength = g[0]
				if len(center_wavelength) > 0:
					center_wavelength = "'" + center_wavelength + "'"
				else:
					return "No", "No"
			# multiplicative factor inside " " separated by ,
			elif pName == "multiplicative_factor":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				multiplicative_factor = g[0]
				if len(multiplicative_factor) > 0:
					multiplicative_factor = "'" + multiplicative_factor + "'"
				else:
					return "No", "No"
			# additive factor inside " " separated by ,
			elif pName == "additive_factor":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				additive_factor = g[0]
				if len(additive_factor) > 0:
					additive_factor = "'" + additive_factor + "'"
				else:
					return "No", "No"
			else:
				return "No", "No"
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
			return "No", "No"
		return "Yes", parameters
																								
	# batch split raster
	def performSplitRaster(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				file = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# output directory inside " "
			elif pName == "output_dir":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", "No"
			# output name prefix inside " "
			elif pName == "output_name_prefix":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					cfg.ui.output_name_lineEdit.setText(g)
				else:
					cfg.ui.output_name_lineEdit.setText("")
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"No"')
			parameters.append('"Yes"')
			parameters.append(file)
			parameters.append(outputDir)
		except:
			return "No", "No"
		return "Yes", parameters
																																				
	# batch band calc
	def performBandCalc(self, paramList):
		extentRaster = "None"
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# expression inside " "
			if pName == "expression":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					expr = "'" + g + "'"
				else:
					return "No", "No"
			# output file path inside " "
			elif pName == "output_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				outputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# extent same as raster name inside " "
			elif pName == "extent_same_as_raster_name":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				extentRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					cfg.ui.extent_checkBox.setCheckState(2)
				else:
					return "No", "No"
			# extent checkbox (1 checked or 0 unchecked)
			elif pName == "extent_intersection":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.intersection_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.intersection_checkBox.setCheckState(0)
					cfg.ui.extent_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "set_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_3.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_3.setCheckState(0)
				else:
					return "No", "No"
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_4.setValue(val)
				except:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append(outputRaster)
			parameters.append('"Yes"')
			parameters.append(expr)
			parameters.append(extentRaster)
		except:
			return "No", "No"
		return "Yes", parameters
																									
	# batch clip rasters
	def performClipRasters(self, paramList):
		shapefilePath = "None"
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " " separated by ,
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				files = g[0]
				if len(files) > 0:
					files = "'" + files + "'"
				else:
					return "No", "No"
			# output directory inside " "
			elif pName == "output_dir":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", "No"
			# output name prefix inside " "
			elif pName == "output_name_prefix":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					cfg.ui.output_name_lineEdit.setText(g)
				else:
					cfg.ui.output_name_lineEdit.setText("")
					return "No", "No"
			# use shapefile of components checkbox (1 checked or 0 unchecked)
			elif pName == "use_shapefile":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.shapefile_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.shapefile_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# shapefile path inside " "
			elif pName == "shapefile_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					shapefilePath = "'" + g[0] + "'"
				else:
					return "No", "No"
			# ul_x inside " "
			elif pName == "ul_x":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					cfg.ui.UX_lineEdit.setText(g[0])
				else:
					cfg.ui.UX_lineEdit.setText("")
					return "No", "No"
			# ul_y inside " "
			elif pName == "ul_y":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					cfg.ui.UY_lineEdit.setText(g[0])
				else:
					cfg.ui.UY_lineEdit.setText("")
					return "No", "No"
			# lr_x inside " "
			elif pName == "lr_x":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					cfg.ui.LX_lineEdit.setText(g[0])
				else:
					cfg.ui.LX_lineEdit.setText("")
					return "No", "No"
			# lr_y inside " "
			elif pName == "lr_y":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					cfg.ui.LY_lineEdit.setText(g[0])
				else:
					cfg.ui.LY_lineEdit.setText("")
					return "No", "No"
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox.setValue(val)
				except:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(files)
			parameters.append(outputDir)
			parameters.append(shapefilePath)
		except:
			return "No", "No"
		return "Yes", parameters
	
	# batch reclassification
	def performReclassification(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				inputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# output file path inside " "
			elif pName == "output_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				outputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# reclassification values inside " " (list of oldValue-newValue separated by ,)
			elif pName == "value_list":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				values = g[0]
				if len(values) > 0:
					values = "'" + values + "'"
				else:
					return "No", "No"
			# use signature list code checkbox (1 checked or 0 unchecked)
			elif pName == "use_signature_list_code":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.apply_symbology_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.apply_symbology_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# code field
			elif pName == "code_field":
				id = cfg.ui.class_macroclass_comboBox_2.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.class_macroclass_comboBox_2.setCurrentIndex(id)
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
			parameters.append(values)
		except:
			return "No", "No"
		return "Yes", parameters
		
	# batch classification sieve
	def performClassificationSieve(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				inputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# output file path inside " "
			elif pName == "output_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				outputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# size threshold value (int value)
			elif pName == "size_threshold":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.sieve_threshold_spinBox.setValue(val)
				except:
					return "No", "No"
			# code field
			elif pName == "pixel_connection":
				id = cfg.ui.sieve_connection_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.sieve_connection_combo.setCurrentIndex(id)
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
		except:
			return "No", "No"
		return "Yes", parameters
				
	# batch classification erosion
	def performClassificationErosion(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				inputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# output file path inside " "
			elif pName == "output_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				outputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# class values inside " "
			elif pName == "class_values":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					cfg.ui.erosion_classes_lineEdit.setText(g[0])
				else:
					cfg.ui.erosion_classes_lineEdit.setText("")
					return "No", "No"
			# size threshold value (int value)
			elif pName == "size_in_pixels":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.erosion_threshold_spinBox.setValue(val)
				except:
					return "No", "No"
			# code field
			elif pName == "pixel_connection":
				id = cfg.ui.erosion_connection_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.erosion_connection_combo.setCurrentIndex(id)
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
		except:
			return "No", "No"
		return "Yes", parameters
					
	# batch classification dilation
	def performClassificationDilation(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				inputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# output file path inside " "
			elif pName == "output_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				outputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# class values inside " "
			elif pName == "class_values":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					cfg.ui.dilation_classes_lineEdit.setText(g[0])
				else:
					cfg.ui.dilation_classes_lineEdit.setText("")
					return "No", "No"
			# size threshold value (int value)
			elif pName == "size_in_pixels":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.dilation_threshold_spinBox.setValue(val)
				except:
					return "No", "No"
			# code field
			elif pName == "pixel_connection":
				id = cfg.ui.dilation_connection_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.dilation_connection_combo.setCurrentIndex(id)
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputRaster)
		except:
			return "No", "No"
		return "Yes", parameters
				
	# batch edit raster using shapefile
	def performEditRasterUsingShapefile(self, paramList):
		vectorFieldName = "None"
		cfg.ui.edit_val_use_vector_radioButton.setChecked(True)
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				inputRaster = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# input vector inside " "
			elif pName == "input_vector_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				inputVector = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			# vector field name inside " "
			elif pName == "vector_field_name":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					vectorFieldName = "'" + g[0] + "'"
					cfg.ui.use_field_vector_checkBox.setCheckState(2)
				else:
					return "No", "No"
			# expression inside " "
			elif pName == "expression":
				g = pSplit[1].replace("'", '')
				if len(g) > 0:
					cfg.ui.expression_lineEdit.setText(g)
					cfg.ui.use_expression_checkBox.setCheckState(2)
				else:
					cfg.ui.expression_lineEdit.setText("")
					return "No", "No"
			# constant value (int value)
			elif pName == "constant_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.value_spinBox.setValue(val)
					cfg.ui.use_constant_val_checkBox.setCheckState(2)
				except:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(inputVector)
			parameters.append(vectorFieldName)
		except:
			return "No", "No"
		return "Yes", parameters
		
	# batch PCA
	def performPCA(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# output directory inside " "
			if pName == "output_dir":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputDir = "'" + g[0] + "'"
				else:
					return "No", "No"
			# use number of components checkbox (1 checked or 0 unchecked)
			elif pName == "use_number_of_components":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.num_comp_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.num_comp_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# number of components (int value)
			elif pName == "number_of_components":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.pca_components_spinBox.setValue(val)
				except:
					return "No", "No"
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox_4.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox_4.setCheckState(0)
				else:
					return "No", "No"
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_5.setValue(val)
				except:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputDir)
		except:
			return "No", "No"
		return "Yes", parameters
		
	# batch accuracy
	def performAccuracy(self, paramList):
		shapefileField = "None"
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# classification path inside " "
			if pName == "classification_file_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					classification = "'" + g[0] + "'"
				else:
					return "No", "No"
			# output path inside " "
			elif pName == "output_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputRaster = "'" + g[0] + "'"
				else:
					return "No", "No"
			# shapefile field name inside " "
			elif pName == "shapefile_field_name":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					shapefileField = "'" + g[0] + "'"
				else:
					return "No", "No"
			# reference path inside " "
			elif pName == "reference_file_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					reference = "'" + g[0] + "'"
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append(classification)
			parameters.append(reference)
			parameters.append('"Yes"')
			parameters.append(shapefileField)
			parameters.append(outputRaster)
		except:
			return "No", "No"
		return "Yes", parameters
									
	# batch vector to raster
	def performVectorToRaster(self, paramList):
		vectorFieldName = "None"
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# output path inside " "
			if pName == "output_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputRaster = "'" + g[0] + "'"
				else:
					return "No", "No"
			# input vector path inside " "
			elif pName == "vector_file_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					inputVector= "'" + g[0] + "'"
				else:
					return "No", "No"
			# input vector field name " "
			elif pName == "vector_field_name":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					vectorFieldName = "'" + g[0] + "'"
				else:
					return "No", "No"
			# use value field checkbox (1 checked or 0 unchecked)
			elif pName == "use_value_field":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.field_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.field_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# constant value (int value)
			elif pName == "constant_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.constant_value_spinBox.setValue(val)
				except:
					return "No", "No"
			# type of conversion inside " " ("Center of pixels" , "All pixels touched")
			elif pName == "type_of_conversion":
				id = cfg.ui.conversion_type_combo.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.conversion_type_combo.setCurrentIndex(id)
				else:
					return "No", "No"
			# input raster path inside " "
			elif pName == "reference_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					inputRaster = "'" + g[0] + "'"
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(outputRaster)
			parameters.append(inputVector)
			parameters.append(vectorFieldName)
			parameters.append(inputRaster)
		except:
			return "No", "No"
		return "Yes", parameters
																
	# batch Land Cover Change
	def performLandCoverChange(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# output path inside " "
			if pName == "output_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputRaster = "'" + g[0] + "'"
				else:
					return "No", "No"
			# input raster path inside " "
			elif pName == "reference_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					refRaster = "'" + g[0] + "'"
				else:
					return "No", "No"
			# input raster path inside " "
			elif pName == "new_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					newRaster = "'" + g[0] + "'"
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(refRaster)
			parameters.append(newRaster)
			parameters.append(outputRaster)
		except:
			return "No", "No"
		return "Yes", parameters
		
	# batch classification report
	def performClassificationReport(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# output path inside " "
			if pName == "output_report_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputReport = "'" + g[0] + "'"
				else:
					return "No", "No"
			# input raster path inside " "
			elif pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					inputRaster = "'" + g[0] + "'"
				else:
					return "No", "No"
			# nodata checkbox (1 checked or 0 unchecked)
			elif pName == "use_nodata":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.nodata_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.nodata_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# nodata value (int value)
			elif pName == "nodata_value":
				try:
					val = int(pSplit[1].replace(" ", ""))
					cfg.ui.nodata_spinBox_2.setValue(val)
				except:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			parameters.append(inputRaster)
			parameters.append("None")
			# batch
			parameters.append('"Yes"')
			parameters.append(outputReport)
		except:
			return "No", "No"
		return "Yes", parameters
		
	# batch classification to vector
	def performClassificationToVector(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input raster path inside " "
			if pName == "input_raster_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					inputRaster = "'" + g[0] + "'"
				else:
					return "No", "No"
			# output vector path inside " "
			elif pName == "output_vector_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				if len(g[0]) > 0:
					outputVector = "'" + g[0] + "'"
				else:
					return "No", "No"
			# use signature list code checkbox (1 checked or 0 unchecked)
			elif pName == "use_signature_list_code":
				if pSplit[1].replace(" ", "") == "1":
					cfg.ui.use_class_code_checkBox.setCheckState(2)
				elif pSplit[1].replace(" ", "") == "0":
					cfg.ui.use_class_code_checkBox.setCheckState(0)
				else:
					return "No", "No"
			# code field
			elif pName == "code_field":
				id = cfg.ui.class_macroclass_comboBox.findText(pSplit[1].strip().replace("'", ""))
				if id >= 0:
					cfg.ui.class_macroclass_comboBox.setCurrentIndex(id)
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			# batch
			parameters.append('"Yes"')
			parameters.append(inputRaster)
			parameters.append(outputVector)
		except:
			return "No", "No"
		return "Yes", parameters
														
	# batch open training input
	def performOpenTrainingInput(self, paramList):
		parameters = []
		for p in paramList:
			pSplit = p.split(":")
			pName = pSplit[0].lower().replace(" ", "")
			# input file path inside " "
			if pName == "training_file_path":
				g = cfg.reSCP.findall('[\'](.*?)[\']',pSplit[1])
				file = "'" + g[0] + "'"
				if len(g[0]) > 0:
					pass
				else:
					return "No", "No"
			else:
				return "No", "No"
		# append parameters
		try:
			parameters.append(file)
		except:
			return "No", "No"
		return "Yes", parameters
				