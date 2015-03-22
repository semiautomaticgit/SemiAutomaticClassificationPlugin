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
import shutil
import subprocess
# for debugging
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg
try:
	from osgeo import gdal
	from osgeo.gdalconst import *
	from osgeo import ogr
	from osgeo import osr
except Exception, err:
	cfg.testGDALV = err
try:
	import numpy as np
except Exception, err:
	cfg.testNumpyV = err
try:
	from scipy.ndimage import label
	from scipy import spatial
	import scipy.stats.distributions as dist
	from scipy.spatial.distance import cdist
except Exception, err:
	cfg.testScipyV = err
try:
	from matplotlib.ticker import MaxNLocator
except Exception, err:
	cfg.testMatplotlibV = err

class Settings:

	def __init__(self):
		pass
		
	# set variable for algorithm files
	def algFilesCheckbox(self):
		if cfg.ui.alg_files_checkBox.isChecked() is True:
			cfg.algFilesCheck = "Yes"
		else:
			cfg.algFilesCheck = "No"
		self.setQGISRegSetting(cfg.regAlgFiles, cfg.algFilesCheck)
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.algFilesCheck))
		
	# Change ROI color
	def changeROIColor(self):
		c = QColorDialog.getColor()
		if c.isValid():	
			self.setQGISRegSetting(cfg.regROIClr, c.name())
			cfg.ROIClrVal = self.getQGISRegSetting(cfg.regROIClr, cfg.ROIClrValDefault)
			cfg.ui.color_mdiArea.setBackground(QColor(cfg.ROIClrVal))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi colour changed to: " + str(cfg.ROIClrVal))

	# ROI transparency
	def changeROITransparency(self):
		cfg.ROITrnspVal = cfg.ui.transparency_Slider.value()
		cfg.ui.transparency_Label.setText(QApplication.translate("semiautomaticclassificationplugin", "Transparency ") + str(cfg.ROITrnspVal) + "%")
		self.setQGISRegSetting(cfg.regROITransp, cfg.ROITrnspVal)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi transparency changed to: " + str(cfg.ROITrnspVal) + "%")
		
	def copyLogFile(self):
		out = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save Log file"), "", "*.txt")
		if len(out) > 0:
			if os.path.isfile(cfg.logFile):
				try:
					shutil.copy(cfg.logFile, out)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.mx.msgErr20()
		
	# get QGIS registry value
	def getQGISRegSetting(self, key, defaultValue):
		q = QSettings()
		v = q.value(key, defaultValue)
		return v
		
	# field ID name
	def IDFieldNameChange(self):
		cfg.fldID_class = cfg.ui.ID_field_name_lineEdit.text()
		self.setQGISRegSetting(cfg.regIDFieldName, cfg.fldID_class)
		cfg.ROId.refreshShapeLayer()
		cfg.acc.refreshReferenceLayer()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "IDFieldName changed to: " + unicode(cfg.fldID_class))
		
	# field Macro ID name
	def MacroIDFieldNameChange(self):
		cfg.fldMacroID_class = cfg.ui.MID_field_name_lineEdit.text()
		self.setQGISRegSetting(cfg.regMacroIDFieldName, cfg.fldMacroID_class)
		cfg.ROId.refreshShapeLayer()
		cfg.acc.refreshReferenceLayer()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "macroclassIDFieldName changed to: " + unicode(cfg.fldMacroID_class))
		
	# macroclass field Info name
	def MacroInfoFieldNameChange(self):
		cfg.fldROIMC_info = cfg.ui.MCInfo_field_name_lineEdit.text()
		self.setQGISRegSetting(cfg.regMCInfoFieldName, cfg.fldROIMC_info)
		cfg.ROId.refreshShapeLayer()
		cfg.acc.refreshReferenceLayer()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Macroclass IDFieldName changed to: " + unicode(cfg.fldROIMC_info))
		
	# variable name
	def VariableNameChange(self):
		cfg.variableName = cfg.ui.variable_name_lineEdit.text()
		self.setQGISRegSetting(cfg.regVariableName, cfg.variableName)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Variable name changed to: " + unicode(cfg.variableName))
				
	# group name
	def GroupNameChange(self):
		cfg.grpNm = cfg.ui.group_name_lineEdit.text()
		self.setQGISRegSetting(cfg.regGroupName, cfg.grpNm)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group name changed to: " + unicode(cfg.grpNm))
		
	# field class Info name
	def InfoFieldNameChange(self):
		cfg.fldROI_info = cfg.ui.Info_field_name_lineEdit.text()
		self.setQGISRegSetting(cfg.regInfoFieldName, cfg.fldROI_info)
		cfg.ROId.refreshShapeLayer()
		cfg.acc.refreshReferenceLayer()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "IDFieldName changed to: " + unicode(cfg.fldROI_info))
		
	# checkbox switch log
	def logCheckbox(self):
		# log setting
		if cfg.ui.log_checkBox.isChecked() is True:
			self.setQGISRegSetting(cfg.regLogKey, "Yes")
			# logger
			cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "LOG ACTIVE" + cfg.sysInfo)
		elif cfg.ui.log_checkBox.isChecked() is False:
			# logger
			cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "LOG DISABLED")
			self.setQGISRegSetting(cfg.regLogKey, "No")
		cfg.logSetVal = self.getQGISRegSetting(cfg.regLogKey, "Yes")
		
	# checkbox switch sound
	def soundCheckbox(self):
		# sound setting
		if cfg.ui.sound_checkBox.isChecked() is True:
			self.setQGISRegSetting(cfg.regSound, "Yes")
		elif cfg.ui.sound_checkBox.isChecked() is False:
			self.setQGISRegSetting(cfg.regSound, "No")
		cfg.soundVal = self.getQGISRegSetting(cfg.regSound, "Yes")
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "sound: " + str(cfg.soundVal))
		
	# RAM setting
	def RAMSettingChange(self):
		cfg.RAMValue = cfg.ui.RAM_spinBox.value()
		self.setQGISRegSetting(cfg.regRAMValue, cfg.RAMValue)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "ram value changed to: " + str(cfg.RAMValue))
		
	# reset field names
	def resetFieldNames(self):
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Reset field names"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset field names?"))
		if a == "Yes":
			cfg.ui.ID_field_name_lineEdit.setText(cfg.fldID_class_def)
			cfg.ui.Info_field_name_lineEdit.setText(cfg.fldROI_info_def)
			cfg.ui.MID_field_name_lineEdit.setText(cfg.fldMacroID_class_def)
			cfg.ui.MCInfo_field_name_lineEdit.setText(cfg.fldROIMC_info_def)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "field Info name reset")
	
	# reset variable names
	def resetVariableName(self):
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Reset variable name"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset variable name?"))
		if a == "Yes":
			cfg.ui.variable_name_lineEdit.setText(cfg.variableName_def)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "variable name reset")
			
	# reset group name
	def resetGroupName(self):
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Reset group name"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset group name?"))
		if a == "Yes":
			cfg.ui.group_name_lineEdit.setText(cfg.grpNm_def)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group name reset")
		
	# Reset qml style path
	def resetROIStyle(self):
		self.setQGISRegSetting(cfg.regROIClr, cfg.ROIClrValDefault)
		self.setQGISRegSetting(cfg.regROITransp, str(cfg.ROITrnspValDefault))
		cfg.ROITrnspVal = cfg.ROITrnspValDefault
		cfg.ROIClrVal = cfg.ROIClrValDefault
		cfg.ui.color_mdiArea.setBackground(QColor(cfg.ROIClrVal))
		cfg.ui.transparency_Label.setText(QApplication.translate("semiautomaticclassificationplugin", "Transparency ") + str(cfg.ROITrnspVal) + "%")
		cfg.ui.transparency_Slider.setValue(cfg.ROITrnspValDefault)
		cfg.mx.msg1()
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi color reset")
		
	# set plot legend max lenght
	def setPlotLegendLenght(self):
		cfg.roundCharList = cfg.ui.plot_text_spinBox.value()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "plot legend max length value changed to: " + str(cfg.roundCharList))

	# set QGIS registry value
	def setQGISRegSetting(self, key, value):
		q = QSettings()
		q.setValue(key, value)
	
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
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(cfg.testGDALV))
			test = "Fail"
		else:
			v = cfg.utls.getGDALVersion()
			if int(v[0]) == 1 and int(v[1]) < 10:
				test = "Success (GDAL version outdated " + str(v[0]) + "." + str(v[1]) + ")"
			# check OGR drivers
			d = ogr.GetDriverByName('ESRI Shapefile')
			if d is None:
				test = "Fail (missing drivers)"
		# logger		
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
		
	# test GDAL subprocess
	def testGDALSubprocess(self):
		test = "Success"
		tPMN = cfg.tmpVrtNm + ".vrt"
		dT = cfg.utls.getTime()
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		r = cfg.plgnDir + cfg.debugRasterPath
		if os.path.isfile(r) is False:
			test = "Unable to test"
			return test
		try:
			cfg.utls.getGDALForMac()
			sP = subprocess.Popen(cfg.gdalPath + 'gdalbuildvrt -separate "' + unicode(tPMD) + '" ' + unicode(r), shell=True)
			sP.wait()
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			try:
				cfg.utls.getGDALForMac()
				sP = subprocess.Popen(cfg.gdalPath + 'gdalbuildvrt -separate "' + unicode(tPMD) + '" ' + unicode(r), shell=True)
				sP.wait()
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				test = "Fail"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
		
	def testInternetConnection(self):
		dT = cfg.utls.getTime()
		check = cfg.utls.downloadFile("http://landsat-pds.s3.amazonaws.com/L8/139/045/LC81390452014295LGN00/LC81390452014295LGN00_thumb_small.jpg", cfg.tmpDir + "//" + dT + "_thumb_small.jpg", dT + "_thumb_small.jpg", 50)
		if check == "Yes":
			test = "Success"
		else:
			test = "Fail"
		return test
		
	# test Numpy
	def testNumpy(self):
		test = "Success"
		if cfg.testNumpyV is not None:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(cfg.testNumpyV))
			test = "Fail"
		# check if NumPy is updated
		else:
			try:
				np.count_nonzero([1,1,0])
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				test = "Success (NumPy is outdated)"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
		
	# test Scipy
	def testScipy(self):
		test = "Success"
		if cfg.testScipyV is not None:
			# logger
			cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(cfg.testScipyV))
			test = "Fail"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
		
	# test Matplotlib
	def testMatplotlib(self):
		test = "Success"
		if cfg.testMatplotlibV is not None:
			# logger
			cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(cfg.testMatplotlibV))
			test = "Fail"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " test: " + str(test))
		return test
			
	# set variable for virtual raster format
	def virtualRasterFormatCheckbox(self):
		if cfg.ui.virtual_raster_checkBox.isChecked() is True:
			cfg.outTempRastFormat = "VRT"
		else:
			cfg.outTempRastFormat = "GTiff"
		self.setQGISRegSetting(cfg.regTempRasterFormat, cfg.outTempRastFormat)
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.outTempRastFormat))
		