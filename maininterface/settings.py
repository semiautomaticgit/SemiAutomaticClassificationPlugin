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

class Settings:

	def __init__(self):	
		pass
		
	# set variable for algorithm files
	def algFilesCheckbox(self):
		if cfg.uidc.alg_files_checkBox.isChecked() is True:
			cfg.algFilesCheck = "Yes"
		else:
			cfg.algFilesCheck = "No"
		cfg.utls.setQGISRegSetting(cfg.regAlgFiles, cfg.algFilesCheck)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.algFilesCheck))
		
	# Change ROI color
	def changeROIColor(self):
		c = cfg.QtWidgetsSCP.QColorDialog.getColor()
		if c.isValid():	
			cfg.utls.setQGISRegSetting(cfg.regROIClr, c.name())
			cfg.ROIClrVal = self.getQGISRegSetting(cfg.regROIClr, cfg.ROIClrValDefault)
			cfg.ui.change_color_Button.setStyleSheet("background-color :" + cfg.ROIClrVal)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi colour changed to: " + str(cfg.ROIClrVal))

	# ROI transparency
	def changeROITransparency(self):
		cfg.ROITrnspVal = cfg.ui.transparency_Slider.value()
		cfg.ui.transparency_Label.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Transparency ") + str(cfg.ROITrnspVal) + "%")
		cfg.utls.setQGISRegSetting(cfg.regROITransp, cfg.ROITrnspVal)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi transparency changed to: " + str(cfg.ROITrnspVal) + "%")
		
	# copy the Log file
	def copyLogFile(self):
		out = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save Log file"), "", "*.txt", "txt")
		if out is not False:
			if out.lower().endswith(".txt"):
				pass
			else:
				out = out + ".txt"
			if cfg.osSCP.path.isfile(cfg.logFile):
				try:
					cfg.shutilSCP.copy(cfg.logFile, out)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.mx.msgErr20()
		
	# get QGIS registry value
	def getQGISRegSetting(self, key, defaultValue):
		q = cfg.QSettingsSCP()
		v = q.value(key, defaultValue)
		return v
		
	# field ID name
	def IDFieldNameChange(self):
		cfg.fldID_class = cfg.ui.ID_field_name_lineEdit.text()
		cfg.utls.setQGISRegSetting(cfg.regIDFieldName, cfg.fldID_class)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "IDFieldName changed to: " + str(cfg.fldID_class))
		
	# field Macro ID name
	def MacroIDFieldNameChange(self):
		cfg.fldMacroID_class = cfg.ui.MID_field_name_lineEdit.text()
		cfg.utls.setQGISRegSetting(cfg.regMacroIDFieldName, cfg.fldMacroID_class)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "macroclassIDFieldName changed to: " + str(cfg.fldMacroID_class))
		
	# macroclass field Info name
	def MacroInfoFieldNameChange(self):
		cfg.fldROIMC_info = cfg.ui.MCInfo_field_name_lineEdit.text()
		cfg.utls.setQGISRegSetting(cfg.regMCInfoFieldName, cfg.fldROIMC_info)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Macroclass IDFieldName changed to: " + str(cfg.fldROIMC_info))
		
	# variable name
	def VariableNameChange(self):
		cfg.variableName = cfg.ui.variable_name_lineEdit.text()
		cfg.utls.setQGISRegSetting(cfg.regVariableName, cfg.variableName)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Variable name changed to: " + str(cfg.variableName))
				
	# group name
	def GroupNameChange(self):
		cfg.grpNm = cfg.ui.group_name_lineEdit.text()
		cfg.utls.setQGISRegSetting(cfg.regGroupName, cfg.grpNm)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group name changed to: " + str(cfg.grpNm))
		
	# field class Info name
	def InfoFieldNameChange(self):
		cfg.fldROI_info = cfg.ui.Info_field_name_lineEdit.text()
		cfg.utls.setQGISRegSetting(cfg.regInfoFieldName, cfg.fldROI_info)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "IDFieldName changed to: " + str(cfg.fldROI_info))
		
	# raster data type change
	def rasterDataTypeChange(self):
		cfg.rasterDataType = cfg.ui.raster_precision_combo.currentText()
		cfg.utls.setQGISRegSetting(cfg.regRasterDataType, cfg.rasterDataType)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster data type changed to: " + str(cfg.rasterDataType))
		
	# checkbox switch log
	def logCheckbox(self):
		# log setting
		if cfg.ui.log_checkBox.isChecked() is True:
			cfg.utls.setQGISRegSetting(cfg.regLogKey, "Yes")
			# logger
			cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "LOG ACTIVE" + cfg.sysSCPInfo)
		elif cfg.ui.log_checkBox.isChecked() is False:
			# logger
			cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "LOG DISABLED")
			cfg.utls.setQGISRegSetting(cfg.regLogKey, "No")
		cfg.logSetVal = self.getQGISRegSetting(cfg.regLogKey, "Yes")
				
	# download news
	def downloadNewsCheckbox(self):
		# log setting
		if cfg.ui.download_news_checkBox.isChecked() is True:
			cfg.utls.setQGISRegSetting(cfg.downNewsKey, "Yes")
		elif cfg.ui.download_news_checkBox.isChecked() is False:
			cfg.utls.setQGISRegSetting(cfg.downNewsKey, "No")
		cfg.downNewsVal = self.getQGISRegSetting(cfg.downNewsKey, "Yes")
		
	# checkbox switch sound
	def soundCheckbox(self):
		# sound setting
		if cfg.ui.sound_checkBox.isChecked() is True:
			cfg.utls.setQGISRegSetting(cfg.regSound, "Yes")
		elif cfg.ui.sound_checkBox.isChecked() is False:
			cfg.utls.setQGISRegSetting(cfg.regSound, "No")
		cfg.soundVal = self.getQGISRegSetting(cfg.regSound, "Yes")
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "sound: " + str(cfg.soundVal))
		
	# RAM setting
	def RAMSettingChange(self):
		cfg.RAMValue = cfg.ui.RAM_spinBox.value()
		cfg.utls.setQGISRegSetting(cfg.regRAMValue, cfg.RAMValue)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "ram value changed to: " + str(cfg.RAMValue))
		
	# reset field names
	def resetFieldNames(self):
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset field names"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset field names?"))
		if a == "Yes":
			cfg.ui.ID_field_name_lineEdit.setText(cfg.fldID_class_def)
			cfg.ui.Info_field_name_lineEdit.setText(cfg.fldROI_info_def)
			cfg.ui.MID_field_name_lineEdit.setText(cfg.fldMacroID_class_def)
			cfg.ui.MCInfo_field_name_lineEdit.setText(cfg.fldROIMC_info_def)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "field Info name reset")
	
	# reset variable names
	def resetVariableName(self):
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset variable name"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset variable name?"))
		if a == "Yes":
			cfg.ui.variable_name_lineEdit.setText(cfg.variableName_def)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "variable name reset")
			
	# reset group name
	def resetGroupName(self):
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset group name"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset group name?"))
		if a == "Yes":
			cfg.ui.group_name_lineEdit.setText(cfg.grpNm_def)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group name reset")
					
	# change temporary directory
	def changeTempDir(self):
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Change temporary directory"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to change the temporary directory?"))
		if a == "Yes":
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
			if len(o) != 0:
				if cfg.QDirSCP(o).exists():
					dT = cfg.utls.getTime()
					oDir = cfg.utls.makeDirectory(o + "/" + dT)
					if oDir is None:
						cfg.mx.msgWar17()
						return "No"
					cfg.tmpDir = o + "/" + dT
					cfg.ui.temp_directory_label.setText(o)
					cfg.utls.setQGISRegSetting(cfg.regTmpDir, o)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "change temporary directory")
							
	# reset temporary directory
	def resetTempDir(self):
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset temporary directory"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset the temporary directory?"))
		if a == "Yes":
			cfg.tmpDir = str(cfg.QDirSCP.tempPath() + "/" + cfg.tempDirName)
			cfg.utls.setQGISRegSetting(cfg.regTmpDir, cfg.tmpDir)
			cfg.ui.temp_directory_label.setText(cfg.tmpDir)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reset temporary directory")

	# Reset qml style path
	def resetROIStyle(self):
		cfg.utls.setQGISRegSetting(cfg.regROIClr, cfg.ROIClrValDefault)
		cfg.utls.setQGISRegSetting(cfg.regROITransp, str(cfg.ROITrnspValDefault))
		cfg.ROITrnspVal = cfg.ROITrnspValDefault
		cfg.ROIClrVal = cfg.ROIClrValDefault
		cfg.ui.change_color_Button.setStyleSheet("background-color :" + cfg.ROIClrVal)
		cfg.ui.transparency_Label.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Transparency ") + str(cfg.ROITrnspVal) + "%")
		cfg.ui.transparency_Slider.setValue(cfg.ROITrnspValDefault)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi color reset")

	
	# test required dependencies
	def testDependencies(self):
		testGDAL = self.testGDAL()
		testGDALSubprocess = self.testGDALSubprocess()
		testNumpy = self.testNumpy()
		testScipy = self.testScipy()
		testMatplotlib = self.testMatplotlib()
		testInternet = self.testInternetConnection()
		message = "-GDAL: " + testGDAL + "\n" + "-GDAL subprocess: " + testGDALSubprocess + "\n" + "-NumPy: " + testNumpy + "\n" + "-SciPy: " + testScipy + "\n" + "-Matplotlib: " + testMatplotlib + "\n" + "-Internet connection: " + testInternet + "\n"
		cfg.mx.msgTest(message)
	
	# test GDAL
	def testGDAL(self):
		test = "Success"
		if cfg.testGDALV is not None:		
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(cfg.testGDALV))
			test = "Fail"
		else:
			v = cfg.utls.getGDALVersion()
			# logger		
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " gdal version:" + str(v[0]) + "." + str(v[1])  )
			if int(v[0]) == 1 and int(v[1]) < 10:
				test = "Success (GDAL version outdated " + str(v[0]) + "." + str(v[1]) + ")"
			# check OGR drivers
			d = cfg.ogrSCP.GetDriverByName('ESRI Shapefile')
			if d is None:
				test = "Fail (missing drivers)"
		# logger		
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
		
	# test GDAL subprocess
	def testGDALSubprocess(self):
		test = "Success"
		tPMN = cfg.tmpVrtNm + ".vrt"
		dT = cfg.utls.getTime()
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		r = cfg.plgnDir + cfg.debugRasterPath
		if cfg.osSCP.path.isfile(r) is False:
			test = "Unable to test"
			return test
		try:
			cfg.utls.getGDALForMac()
			sP = cfg.subprocessSCP.Popen(cfg.gdalPath + 'gdalbuildvrt -separate "' + str(tPMD) + '" ' + str(r), shell=True)
			sP.wait()
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			try:
				cfg.utls.getGDALForMac()
				sP = cfg.subprocessSCP.Popen(cfg.gdalPath + 'gdalbuildvrt -separate "' + str(tPMD) + '" ' + str(r), shell=True)
				sP.wait()
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				test = "Fail"
		try:
			cfg.utls.GDALCopyRaster(str(r), cfg.tmpDir + "/" + dT + "test.tif", "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			test = "Fail"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
		
	# test internet connection
	def testInternetConnection(self):
		dT = cfg.utls.getTime()
		check = cfg.utls.downloadFile("https://semiautomaticgit.github.io/SemiAutomaticClassificationPluginWelcome/changelog.html", cfg.tmpDir + "//" + dT + "_changelog.html", dT + "_changelog.html", 50)
		if check == "Yes":
			test = "Success"
		else:
			test = "Fail"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
		
	# test Numpy
	def testNumpy(self):
		test = "Success"
		if cfg.testNumpyV is not None:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(cfg.testNumpyV))
			test = "Fail"
		# check if NumPy is updated
		else:
			try:
				cfg.np.count_nonzero([1,1,0])
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				test = "Success (NumPy is outdated)"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
		
	# test Scipy
	def testScipy(self):
		test = "Success"
		if cfg.testScipyV is not None:
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(cfg.testScipyV))
			test = "Fail"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
		
	# test Matplotlib
	def testMatplotlib(self):
		test = "Success"
		if cfg.testMatplotlibV is not None:
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(cfg.testMatplotlibV))
			test = "Fail"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
			
	# set variable for virtual raster format
	def virtualRasterFormatCheckbox(self):
		if cfg.ui.virtual_raster_checkBox.isChecked() is True:
			cfg.outTempRastFormat = "VRT"
		else:
			cfg.outTempRastFormat = "GTiff"
		cfg.utls.setQGISRegSetting(cfg.regTempRasterFormat, cfg.outTempRastFormat)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.outTempRastFormat))
					
	# set variable for raster compression
	def rasterCompressionCheckbox(self):
		if cfg.ui.raster_compression_checkBox.isChecked() is True:
			cfg.rasterCompression = "Yes"
		else:
			cfg.rasterCompression = "No"
		cfg.utls.setQGISRegSetting(cfg.regRasterCompression, cfg.rasterCompression)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.rasterCompression))
		
	# smtp server
	def SMTPServerChange(self):
		cfg.SMTPServer = cfg.ui.smtp_server_lineEdit.text()
		cfg.utls.setQGISRegSetting(cfg.regSMTPServer, cfg.SMTPServer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "SMTP server changed to: " + str(cfg.SMTPServer))
		
	# smtp to emails
	def SMTPtoEmailsChange(self):
		cfg.SMTPtoEmails = cfg.ui.to_email_lineEdit.text()
		cfg.utls.setQGISRegSetting(cfg.regSMTPtoEmails, cfg.SMTPtoEmails)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "SMTP server changed to: " + str(cfg.SMTPtoEmails))
		
	# user
	def rememberUser(self):
		if cfg.ui.remeber_settings_checkBox.isChecked():
			cfg.SMTPUser = cfg.ui.smtp_user_lineEdit.text()
			cfg.SMTPPassword = cfg.utls.encryptPassword(cfg.ui.smtp_password_lineEdit.text())
			cfg.utls.setQGISRegSetting(cfg.regSMTPUser, cfg.SMTPUser)
			cfg.utls.setQGISRegSetting(cfg.regSMTPPassword, cfg.SMTPPassword)
			
	# checkbox remember user
	def rememberUserCheckbox(self):
		if cfg.ui.remeber_settings_checkBox.isChecked():
			self.rememberUser()
		else:
			cfg.utls.setQGISRegSetting(cfg.regSMTPUser, "")
			cfg.utls.setQGISRegSetting(cfg.regSMTPPassword, "")
			
	# checkbox SMTP
	def SMTPCheckbox(self):
		# sound setting
		if cfg.ui.smtp_checkBox.isChecked() is True:
			cfg.utls.setQGISRegSetting(cfg.regSMTPCheck, "Yes")
		elif cfg.ui.smtp_checkBox.isChecked() is False:
			cfg.utls.setQGISRegSetting(cfg.regSMTPCheck, "No")
		cfg.SMTPCheck = self.getQGISRegSetting(cfg.regSMTPCheck, "Yes")
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "sound: " + str(cfg.SMTPCheck))