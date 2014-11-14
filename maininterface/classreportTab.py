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
		copyright			: (C) 2012 by Luca Congedo
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

class ClassReportTab:

	def __init__(self):
		pass
					
	# calculate classification report
	def calculateClassificationReport(self, classificationPath, NoDataValue = None):
		# register drivers
		gdal.AllRegister()
		# date time for temp name
		dT = cfg.utls.getTime()
		# temp report
		rN = QApplication.translate("semiautomaticclassificationplugin", "report") + dT + ".csv"
		cfg.reportPth = str(cfg.tmpDir + "/" + rN)
		try:
			clssRstrSrc = classificationPath.encode(cfg.fSEnc)
			ck = "Yes"
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			ck = "No"
		if ck == "No":
			cfg.mx.msg4()
			cfg.acc.refreshClassificationLayer()
		else:
			# open input with GDAL
			cR = gdal.Open(clssRstrSrc, GA_ReadOnly)
			# number of x pixels
			cRC = cR.RasterXSize
			# number of y pixels
			cRR = cR.RasterYSize
			# pixel size
			cRG = cR.GetGeoTransform()
			cRPX = abs(cRG[1])
			cRPY = abs(cRG[5])
			# check projections
			cRP = cR.GetProjection()
			cRSR = osr.SpatialReference(wkt=cRP)
			un = QApplication.translate("semiautomaticclassificationplugin", "Unknown")
			if cRSR.IsProjected:
				un = cRSR.GetAttrValue('unit')
			else:
				pass
			cfg.uiUtls.addProgressBar()
			cfg.uiUtls.updateBar(10)
			# get band
			cRB = cR.GetRasterBand(1)
			blockSizeX = cfg.utls.calculateBlockSize(5)
			blockSizeY = blockSizeX
			# raster range blocks
			lX = range(0, cRC, blockSizeX)
			lY = range(0, cRR, blockSizeY)
			cfg.uiUtls.updateBar(20)
			# set initial value for progress bar
			progresStep = 60 / (len(lX) * len(lY))
			progressStart = 20 - progresStep
			# block size
			if blockSizeX > cRC:
				blockSizeX = cRC
			if blockSizeY > cRR:
				blockSizeY = cRR
			if NoDataValue is None:
				# No data value
				nD = cfg.ui.nodata_spinBox_2.value()
			else:
				nD = NoDataValue
			cmbntns = []
			valSum = []
			n = 1
			# process
			for y in lY:
				bSY = blockSizeY
				if y + bSY > cRR:
					bSY = cRR - y
				for x in lX:
					if cfg.actionCheck == "Yes":
						progress = progressStart + n * progresStep
						cfg.uiUtls.updateBar(progress)
						bSX = blockSizeX
						if x + bSX > cRC:
							bSX = cRC - x
						# combinations of classes
						refRstrArr = cRB.ReadAsArray(x, y, bSX, bSY)
						refRstrVal = np.unique(refRstrArr).tolist()
						for i in refRstrVal:
							if i not in cmbntns:
								if cfg.ui.nodata_checkBox.isChecked() is True or NoDataValue is not None:
									if str(i) != str(nD):
										cmbntns.append(i)
										valSum.append(0)
								else:
									cmbntns.append(i)
									valSum.append(0)
						val = 1
						changeArray = None
						for i in cmbntns:
							# sum
							sum = (refRstrArr == i).sum()
							valSum[val - 1] = valSum[val - 1] + sum
							val = val + 1
					n = n + 1
			pixelTotal = np.sum(valSum)
			cfg.uiUtls.updateBar(80)
			# save combination to table
			l = open(cfg.reportPth, 'w')
			t = str(QApplication.translate("semiautomaticclassificationplugin", 'Class')) + "	" + str(QApplication.translate("semiautomaticclassificationplugin", 'PixelSum')) + "	" + str(QApplication.translate("semiautomaticclassificationplugin", 'Percentage %')) + "	" + str(QApplication.translate("semiautomaticclassificationplugin", 'Area [' + str(un) + "^2]") + str("\n"))
			l.write(t)
			val = 1
			for i in cmbntns:
				p = (float(valSum[val - 1]) /pixelTotal) * 100
				t = str(i) + "	" + str(valSum[val - 1]) + "	" + str(p) + "	" + str(valSum[val - 1] * cRPX * cRPY) + str("\n")
				l.write(t)
				val = val + 1
			l.close()	
			# close bands
			cRB = None
			# close rasters
			cR = None
			cfg.uiUtls.updateBar(80)
			# open csv
			try:
				f = open(cfg.reportPth)
				if os.path.isfile(cfg.reportPth):
					reportTxt = f.read()
					cfg.ui.report_textBrowser.setText(str(reportTxt))
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.uiUtls.removeProgressBar()
			cfg.uiUtls.removeProgressBar()
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " report calculated")
					
	# calculate classification report if click on button
	def calculateClassReport(self):
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " calculate classification report")
		c = str(cfg.ui.classification_report_name_combo.currentText())
		r = cfg.utls.selectLayerbyName(c, "Yes")
		if r is not None:
			self.calculateClassificationReport(r.source())
		else:
			cfg.mx.msg4()
			cfg.acc.refreshClassificationLayer()
					
	def saveReport(self):
		r = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save classification report"), "", "Text (*.csv)")
		try:
			if len(r) > 0:
				shutil.copy(cfg.reportPth, r)
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " report saved")
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					