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
import sys
import subprocess
import inspect
import time
import datetime
import numpy as np
import urllib
import urllib2
import base64
try:
	import winsound
except:
	pass
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import ogr
from osgeo import osr
import SemiAutomaticClassificationPlugin.core.config as cfg
try:
	from scipy import spatial
	import scipy.stats.distributions as dist
	from scipy.spatial.distance import cdist
	cfg.scipyCheck = "Yes"
except:
	cfg.scipyCheck = "No"
	
class Utils:
	def __init__(self):
		# initialize plugin directory
		cfg.lgndir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/SemiAutomaticClassificationPlugin"
		# log file path
		cfg.logFile = cfg.lgndir.replace('//', '/') + "/__0semiautomaticclass.log"
		# file system encoding
		cfg.fSEnc = sys.getfilesystemencoding()

	# Add required fields if missing
	def addFieldsToLayer(self, layerName):
		l = cfg.utls.selectLayerbyName(layerName)
		# band set
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			b = len(cfg.bndSet)
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
			b = i.bandCount()
		fds = []
		# add field for each image band
		for x in range(1, b + 1):
			fds.append(QgsField(cfg.ROIFieldMean + str(x), QVariant.Double))
			fds.append(QgsField(cfg.ROISigma + str(x), QVariant.Double))
		fds.append(QgsField(cfg.ROINBands, QVariant.Int))	
		l.startEditing()
		aF = l.dataProvider().addAttributes(fds)
		# commit changes
		l.commitChanges()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " fields added")
		
### Add layer to map
	def addLayerToMap(self, layer):
		QgsMapLayerRegistry.instance().addMapLayers([layer])
		
### Add layer
	def addVectorLayer(self, path, name, format):
		l = QgsVectorLayer(path, name, format)
		return l
		
### Add raster layer
	def addRasterLayer(self, path, name):
		r = cfg.iface.addRasterLayer(path, name)
		return r
		
	# set all items to state 0 or 2
	def allItemsSetState(self, tableWidget, value):
		tW = tableWidget
		r = tW.rowCount()
		for b in range(0, r):
			if cfg.actionCheck == "Yes":
				tW.item(b, 0).setCheckState(value)
				cfg.uiUtls.updateBar((b+1) * 100 / r)
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " cancelled")
		
	# calculation of earth sun distance
	def calculateEarthSunDistance(self, date, dateFormat):
		dStr = datetime.datetime.strptime(date, dateFormat)
		dStrT = dStr.timetuple()
		# calculate julian day
		day = dStrT.tm_yday
		# Earth Sun distance from http://landsathandbook.gsfc.nasa.gov/excel_docs/d.xls
		dL = [0.98331, 0.98330, 0.98330, 0.98330, 0.98330, 0.98332, 0.98333, 0.98335, 0.98338, 0.98341, 0.98345, 0.98349, 0.98354, 0.98359, 0.98365, 0.98371, 0.98378, 0.98385,
						0.98393, 0.98401, 0.98410, 0.98419, 0.98428, 0.98439, 0.98449, 0.98460, 0.98472, 0.98484, 0.98496, 0.98509, 0.98523, 0.98536, 0.98551, 0.98565, 0.98580, 0.98596, 0.98612,
						0.98628, 0.98645, 0.98662, 0.98680, 0.98698, 0.98717, 0.98735, 0.98755, 0.98774, 0.98794, 0.98814, 0.98835, 0.98856, 0.98877, 0.98899, 0.98921, 0.98944, 0.98966, 0.98989,
						0.99012, 0.99036, 0.99060, 0.99084, 0.99108, 0.99133, 0.99158, 0.99183, 0.99208, 0.99234, 0.99260, 0.99286, 0.99312, 0.99339, 0.99365, 0.99392, 0.99419, 0.99446, 0.99474,
						0.99501, 0.99529, 0.99556, 0.99584, 0.99612, 0.99640, 0.99669, 0.99697, 0.99725, 0.99754, 0.99782, 0.99811, 0.99840, 0.99868, 0.99897, 0.99926, 0.99954, 0.99983, 1.00012,
						1.00041, 1.00069, 1.00098, 1.00127, 1.00155, 1.00184, 1.00212, 1.00240, 1.00269, 1.00297, 1.00325, 1.00353, 1.00381, 1.00409, 1.00437, 1.00464, 1.00492, 1.00519, 1.00546,
						1.00573, 1.00600, 1.00626, 1.00653, 1.00679, 1.00705, 1.00731, 1.00756, 1.00781, 1.00806, 1.00831, 1.00856, 1.00880, 1.00904, 1.00928, 1.00952, 1.00975, 1.00998, 1.01020,
						1.01043, 1.01065, 1.01087, 1.01108, 1.01129, 1.01150, 1.01170, 1.01191, 1.01210, 1.01230, 1.01249, 1.01267, 1.01286, 1.01304, 1.01321, 1.01338, 1.01355, 1.01371, 1.01387,
						1.01403, 1.01418, 1.01433, 1.01447, 1.01461, 1.01475, 1.01488, 1.01500, 1.01513, 1.01524, 1.01536, 1.01547, 1.01557, 1.01567, 1.01577, 1.01586, 1.01595, 1.01603, 1.01610,
						1.01618, 1.01625, 1.01631, 1.01637, 1.01642, 1.01647, 1.01652, 1.01656, 1.01659, 1.01662, 1.01665, 1.01667, 1.01668, 1.01670, 1.01670, 1.01670, 1.01670, 1.01669, 1.01668,
						1.01666, 1.01664, 1.01661, 1.01658, 1.01655, 1.01650, 1.01646, 1.01641, 1.01635, 1.01629, 1.01623, 1.01616, 1.01609, 1.01601, 1.01592, 1.01584, 1.01575, 1.01565, 1.01555,
						1.01544, 1.01533, 1.01522, 1.01510, 1.01497, 1.01485, 1.01471, 1.01458, 1.01444, 1.01429, 1.01414, 1.01399, 1.01383, 1.01367, 1.01351, 1.01334, 1.01317, 1.01299, 1.01281,
						1.01263, 1.01244, 1.01225, 1.01205, 1.01186, 1.01165, 1.01145, 1.01124, 1.01103, 1.01081, 1.01060, 1.01037, 1.01015, 1.00992, 1.00969, 1.00946, 1.00922, 1.00898, 1.00874,
						1.00850, 1.00825, 1.00800, 1.00775, 1.00750, 1.00724, 1.00698, 1.00672, 1.00646, 1.00620, 1.00593, 1.00566, 1.00539, 1.00512, 1.00485, 1.00457, 1.00430, 1.00402, 1.00374,
						1.00346, 1.00318, 1.00290, 1.00262, 1.00234, 1.00205, 1.00177, 1.00148, 1.00119, 1.00091, 1.00062, 1.00033, 1.00005, 0.99976, 0.99947, 0.99918, 0.99890, 0.99861, 0.99832,
						0.99804, 0.99775, 0.99747, 0.99718, 0.99690, 0.99662, 0.99634, 0.99605, 0.99577, 0.99550, 0.99522, 0.99494, 0.99467, 0.99440, 0.99412, 0.99385, 0.99359, 0.99332, 0.99306,
						0.99279, 0.99253, 0.99228, 0.99202, 0.99177, 0.99152, 0.99127, 0.99102, 0.99078, 0.99054, 0.99030, 0.99007, 0.98983, 0.98961, 0.98938, 0.98916, 0.98894, 0.98872, 0.98851,
						0.98830, 0.98809, 0.98789, 0.98769, 0.98750, 0.98731, 0.98712, 0.98694, 0.98676, 0.98658, 0.98641, 0.98624, 0.98608, 0.98592, 0.98577, 0.98562, 0.98547, 0.98533, 0.98519,
						0.98506, 0.98493, 0.98481, 0.98469, 0.98457, 0.98446, 0.98436, 0.98426, 0.98416, 0.98407, 0.98399, 0.98391, 0.98383, 0.98376, 0.98370, 0.98363, 0.98358, 0.98353, 0.98348,
						0.98344, 0.98340, 0.98337, 0.98335, 0.98333, 0.98331]
		eSD = dL[day - 1]	
		return eSD
	
### calculate NDVI
	def calculateNDVI(self, NIR, RED):
		NDVI = (NIR - RED) / (NIR + RED)
		if NDVI > 1:
			NDVI = 1
		elif NDVI < -1:
			NDVI = -1
		return NDVI
		
### calculate EVI
	def calculateEVI(self, NIR, RED, BLUE):
		EVI = 2.5 * (NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1)
		if EVI > 1:
			EVI = 1
		elif EVI < -1:
			EVI = -1
		return EVI
		
### NDVI calculator from image
	def NDVIcalculator(self, imageName, point):
		NDVI = None
		#gdal.AllRegister()
		# band set
		if cfg.bndSetPresent == "Yes" and imageName == cfg.bndSetNm:
			if cfg.NIRBand is None or cfg.REDBand is None:
				return "No"
			else:
				NIRRaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.NIRBand) - 1], "Yes")	
				REDRaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.REDBand) - 1], "Yes")
				# open input with GDAL
				try:
					NIRr = gdal.Open(NIRRaster.source(), GA_ReadOnly)
					REDr = gdal.Open(REDRaster.source(), GA_ReadOnly)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				NIRB = NIRr.GetRasterBand(1)
				REDB = REDr.GetRasterBand(1)
				geoT = NIRr.GetGeoTransform()
		else:
			inputRaster = cfg.utls.selectLayerbyName(imageName, "Yes")	
			# open input with GDAL
			try:
				rD = gdal.Open(inputRaster.source(), GA_ReadOnly)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			if rD is None or cfg.NIRBand is None or cfg.REDBand is None:
				return "No"
			else:
				NIRB = rD.GetRasterBand(int(cfg.NIRBand))
				REDB = rD.GetRasterBand(int(cfg.REDBand))
			geoT = rD.GetGeoTransform()
		tLX = geoT[0]
		tLY = geoT[3]
		pSX = geoT[1]
		pSY = geoT[5]
		# start and end pixels
		pixelStartColumn = (int((point.x() - tLX) / pSX))
		pixelStartRow = -(int((tLY - point.y()) / pSY))
		NIR = self.readArrayBlock(NIRB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.NIRBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.NIRBand) - 1]
		RED = self.readArrayBlock(REDB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.REDBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.REDBand) - 1]
		if NIR is not None and RED is not None:
			try:
				NDVI = self.calculateNDVI(float(NIR), float(RED))
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# close bands
				NIRB = None
				REDB = None
				# close raster
				rD = None
				return "No"
		# close bands
		NIRB = None
		REDB = None
		# close raster
		rD = None
		NIRr = None
		REDr = None
		try:
			return round(NDVI, 2)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No" 
		
### EVI calculator from image
	def EVIcalculator(self, imageName, point):
		EVI = None
		#gdal.AllRegister()
		# band set
		if cfg.bndSetPresent == "Yes" and imageName == cfg.bndSetNm:
			if cfg.NIRBand is None or cfg.REDBand is None or cfg.BLUEBand is None:
				return "No"
			else:
				NIRRaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.NIRBand) - 1], "Yes")	
				REDRaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.REDBand) - 1], "Yes")
				BLUERaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.BLUEBand) - 1], "Yes")
				# open input with GDAL
				try:
					NIRr = gdal.Open(NIRRaster.source(), GA_ReadOnly)
					REDr = gdal.Open(REDRaster.source(), GA_ReadOnly)
					BLUEr = gdal.Open(BLUERaster.source(), GA_ReadOnly)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				NIRB = NIRr.GetRasterBand(1)
				REDB = REDr.GetRasterBand(1)
				BLUEB = REDr.GetRasterBand(1)
				geoT = NIRr.GetGeoTransform()
		else:
			inputRaster = cfg.utls.selectLayerbyName(imageName, "Yes")	
			# open input with GDAL
			try:
				rD = gdal.Open(inputRaster.source(), GA_ReadOnly)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			if rD is None or cfg.NIRBand is None or cfg.REDBand is None or cfg.BLUEBand is None:
				return "No"
			else:
				NIRB = rD.GetRasterBand(int(cfg.NIRBand))
				REDB = rD.GetRasterBand(int(cfg.REDBand))
				BLUEB = rD.GetRasterBand(int(cfg.BLUEBand))
			geoT = rD.GetGeoTransform()
		tLX = geoT[0]
		tLY = geoT[3]
		pSX = geoT[1]
		pSY = geoT[5]
		# start and end pixels
		pixelStartColumn = (int((point.x() - tLX) / pSX))
		pixelStartRow = -(int((tLY - point.y()) / pSY))
		NIR = self.readArrayBlock(NIRB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.NIRBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.NIRBand) - 1]
		RED = self.readArrayBlock(REDB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.REDBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.REDBand) - 1]
		BLUE = self.readArrayBlock(BLUEB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.BLUEBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.BLUEBand) - 1]
		if NIR is not None and RED is not None and BLUE is not None:
			if NIR <= 1 and RED <= 1 and BLUE <= 1:
				try:
					EVI = self.calculateEVI(float(NIR), float(RED), float(BLUE))
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					# close bands
					NIRB = None
					REDB = None
					BLUEB = None
					# close raster
					rD = None
					return "No"
		# close bands
		NIRB = None
		REDB = None
		BLUEB = None
		# close raster
		rD = None
		NIRr = None
		REDr = None
		BLUEr = None
		try:
			return round(EVI, 2)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No" 
		
		
### find band set number used for vegetation index calculation
	def findBandNumber(self):
		cfg.REDBand = None
		cfg.NIRBand = None
		cfg.BLUEBand = None
		if cfg.bndSetUnit["UNIT"] != cfg.noUnit:
			if cfg.bndSetUnit["UNIT"] == cfg.unitNano:
				RED = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.REDCenterBand*1000, cfg.REDThreshold*1000)
				NIR = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.NIRCenterBand*1000, cfg.NIRThreshold*1000)
				BLUE = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.BLUECenterBand*1000, cfg.BLUEThreshold*1000)
			elif cfg.bndSetUnit["UNIT"] == cfg.unitMicro:
				RED = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.REDCenterBand, cfg.REDThreshold)
				NIR = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.NIRCenterBand, cfg.NIRThreshold)
				BLUE = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.BLUECenterBand, cfg.BLUEThreshold)
			if RED is not None and NIR is not None:
				for band, value in cfg.bndSetWvLn.items():
					if value == RED:
						bN = band.replace("WAVELENGTH_", "")
						cfg.REDBand = int(bN)
					elif value == NIR:
						bN = band.replace("WAVELENGTH_", "")
						cfg.NIRBand = int(bN)
			if BLUE is not None:
				for band, value in cfg.bndSetWvLn.items():
					if value == BLUE:
						bN = band.replace("WAVELENGTH_", "")
						cfg.BLUEBand = int(bN)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "RED =" + unicode(cfg.REDBand) + ", NIR =" + unicode(cfg.NIRBand))
		
### find nearest value in list
	def findNearestValueinList(self, list, value, threshold):
		if len(list) > 0:
			arr = np.asarray(list)
			v = (np.abs(arr - value)).argmin()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "find nearest" + unicode(value))
			if np.abs(arr[v] - value) < threshold:
				return arr[v]
			else:
				return None
		else:
			return None

### check if the clicked point is inside the image
	def checkPointImage(self, imageName, point, quiet = "No"):
		# band set
		if cfg.bndSetPresent == "Yes" and imageName == cfg.bndSetNm:
			imageName = cfg.bndSet[0]
			# image CRS
			bN0 = self.selectLayerbyName(imageName, "Yes")
			iCrs = self.getCrs(bN0)
			if iCrs is None:
				iCrs = cfg.utls.getQGISCrs()
				pCrs = iCrs
			else:
				# projection of input point from project's crs to raster's crs
				pCrs = cfg.utls.getQGISCrs()
				if pCrs != iCrs:
					try:
						point = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
						if point is False:
							cfg.pntCheck = "No"
							cfg.utls.setQGISCrs(iCrs)
							return "No"
					# Error latitude or longitude exceeded limits
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						crs = None
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), QApplication.translate("semiautomaticclassificationplugin", "Error") + ": latitude or longitude exceeded limits")
						cfg.pntCheck = "No"
						return "No"
			# workaround coordinates issue
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "project crs: " + unicode(pCrs.toProj4()) + " - raster " + unicode(imageName) + " crs: " + unicode(iCrs.toProj4()))
			cfg.lstPnt = QgsPoint(point.x() / float(1), point.y() / float(1))
			pX = point.x()
			pY = point.y()
			i = self.selectLayerbyName(imageName, "Yes")
			if i is not None:
				# Point Check	
				cfg.pntCheck = None
				if pX > i.extent().xMaximum() or pX < i.extent().xMinimum() or pY > i.extent().yMaximum() or pY < i.extent().yMinimum() :
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "point outside the image area")
					if quiet == "No":
						cfg.mx.msg6()
					cfg.pntCheck = "No"
				else :
					cfg.pntCheck = "Yes"
					return cfg.lstPnt
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image missing")
				if quiet == "No":
					cfg.mx.msg4()
					cfg.pntCheck = "No"
		else:
			if self.selectLayerbyName(imageName, "Yes") is None:
				if quiet == "No":
					cfg.mx.msg4()
				#cfg.ipt.refreshRasterLayer()
				self.pntROI = None
				cfg.pntCheck = "No"
			else:
				# image CRS
				bN0 = self.selectLayerbyName(imageName, "Yes")
				iCrs = self.getCrs(bN0)
				if iCrs is None:
					iCrs = None
				else:
					# projection of input point from project's crs to raster's crs
					pCrs = cfg.utls.getQGISCrs()
					if pCrs != iCrs:
						try:
							point = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
							if point is False:
								cfg.pntCheck = "No"
								cfg.utls.setQGISCrs(iCrs)
								return "No"
						# Error latitude or longitude exceeded limits
						except Exception, err:
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							crs = None
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), QApplication.translate("semiautomaticclassificationplugin", "Error") + ": latitude or longitude exceeded limits")
							cfg.pntCheck = "No"
							return "No"
				# workaround coordinates issue
				if quiet == "No":
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "project crs: " + unicode(pCrs.toProj4()) + " - raster " + unicode(imageName) + " crs: " + unicode(iCrs.toProj4()))
				cfg.lstPnt = QgsPoint(point.x() / float(1), point.y() / float(1))
				pX = point.x()
				pY = point.y()
				i = self.selectLayerbyName(imageName, "Yes")
				# Point Check	
				cfg.pntCheck = None
				if pX > i.extent().xMaximum() or pX < i.extent().xMinimum() or pY > i.extent().yMaximum() or pY < i.extent().yMinimum() :
					if quiet == "No":
						cfg.mx.msg6()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "point outside the image area")
					cfg.pntCheck = "No"
				else :
					cfg.pntCheck = "Yes"
					return cfg.lstPnt
		
### Project point coordinates
	def projectPointCoordinates(self, point, inputCoordinates, outputCoordinates):
		try:
			t = QgsCoordinateTransform(inputCoordinates, outputCoordinates)
			point = t.transform(point)
			return point
		# if empty shapefile
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return False
		
### Clear log file
	def clearLogFile(self):
		if os.path.isfile(cfg.logFile):
			try:
				l = open(cfg.logFile, 'w')
			except:
				pass
			try:
				l.write("Date	Function	Message \n")
				l.write(str(cfg.sysInfo)+"\n")
				l.close()
			except:
				cfg.mx.msg2()

### Copy feature by ID to layer
	def copyFeatureToLayer(self, sourceLayer, ID, targetLayer):
		f = self.getFeaturebyID(sourceLayer, ID)
		# get geometry
		fG = f.geometry()
		f.setGeometry(fG)
		sF = targetLayer.pendingFields()
		f.initAttributes(sF.count())
		if f.geometry() is None:
			cfg.mx.msg6()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feature geometry is none")			
		else:	
			# copy polygon to shapefile
			targetLayer.startEditing()
			targetLayer.addFeature(f)	
			targetLayer.commitChanges()
			targetLayer.dataProvider().createSpatialIndex()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feature copied")
				
### Delete a field from a shapefile by its name
	def deleteFieldShapefile(self, layerPath, fieldName):
		fds = self.fieldsShapefile(layerPath)
		s = ogr.Open(layerPath, 1)
		l = s.GetLayer()
		i = fds.index(fieldName)
		l.DeleteField(i)
		s = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "deleted field: " + unicode(fieldName) + " for layer: " + unicode(l.name()))
				
### Find field ID by name
	def fieldID(self, layer, fieldName):
		fID = layer.fieldNameIndex(fieldName)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "ID: " + str(fID) + " for layer: " + unicode(layer.name()))
		return fID
				
### Get field names of a shapefile
	def fieldsShapefile(self, layerPath):
		s = ogr.Open(layerPath)
		l = s.GetLayer()
		lD = l.GetLayerDefn()
		fN = [lD.GetFieldDefn(i).GetName() for i in range(lD.GetFieldCount())]
		s = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "shapefile field " + unicode(l.name()))
		return fN
				
	def getFieldAttributeList(self, layer, field):
		fID = self.fieldID(layer, field)
		f = QgsFeature()
		l = []
		for f in layer.getFeatures():
			a = f.attributes()[fID]
			l.append(a)
		x = list(set(l))
		return x
			
### Get CRS of a layer by name thereof
	def getCrs(self, lddRstr):
		if lddRstr is None:
			crs = None
		else:
			rP = lddRstr.dataProvider()
			crs = rP.crs()
		return crs
		
### Get raster data type name
	def getRasterDataTypeName(self, inputRaster):
		rD = gdal.Open(inputRaster, GA_ReadOnly)
		b = rD.GetRasterBand(1)
		dType = gdal.GetDataTypeName(b.DataType)
		rD = None
		return dType

### Get QGIS project CRS
	def getQGISCrs(self):
		# QGIS < 2.4
		try:
			pCrs = cfg.cnvs.mapRenderer().destinationCrs()
		# QGIS >= 2.4
		except:
			pCrs = cfg.cnvs.mapSettings().destinationCrs()
		return pCrs
		
		
### Set QGIS project CRS
	def setQGISCrs(self, crs):
		# QGIS < 2.4
		try:
			cfg.cnvs.mapRenderer().setDestinationCrs(crs)
		# QGIS >= 2.4
		except:
			cfg.cnvs.setDestinationCrs(crs)
				
### Get a feature from a shapefile by feature ID
	def getFeaturebyID(self, layer, ID):
		f = QgsFeature()
		# feature request
		fR = QgsFeatureRequest().setFilterFid(ID)
		try:
			f = layer.getFeatures(fR)
			f = f.next()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "get feature " + str(ID) + " from shapefile: " + unicode(layer.name()))
			return f
		# if empty shapefile
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return False
				
### Get a feature box by feature ID
	def getFeatureRectangleBoxbyID(self, layer, ID):
		d = ogr.GetDriverByName("ESRI Shapefile")
		dr = d.Open(layer.source(), 1)
		l = dr.GetLayer()
		f = l.GetFeature(ID)
		# bounding box rectangle
		e = f.GetGeometryRef().GetEnvelope()
		minX = e[0]
		minY = e[2]
		maxX = e[1]
		maxY = e[3]
		centerX = (maxX + minX) / 2
		centerY = (maxY + minY) / 2
		width = maxX - minX
		heigth = maxY - minY
		l = None
		dr = None
		return centerX, centerY, width, heigth
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi bounding box: center " + str(r.center()) + " width: " + str(r.width())+ " height: " + str(r.height()))
		try:
			pass
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			pass
			
### Try to get GDAL for Mac
	def getGDALForMac(self):
		if cfg.sysNm == "Darwin":
			v = cfg.utls.getGDALVersion()
			cfg.gdalPath = '/Library/Frameworks/GDAL.framework/Versions/' + v[0] + '.' + v[1] + '/Programs/'
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " getGDALForMac: " + unicode(v))
			
### Get GDAL version
	def getGDALVersion(self):
		v = gdal.VersionInfo("RELEASE_NAME").split('.')
		return v
			
### Get extent of a shapefile
	def getShapefileRectangleBox(self, layer):
		d = ogr.GetDriverByName("ESRI Shapefile")
		dr = d.Open(layer.source(), 1)
		l = dr.GetLayer()
		e = l.GetExtent()
		minX = e[0]
		minY = e[2]
		maxX = e[1]
		maxY = e[3]
		centerX = (maxX + minX) / 2
		centerY = (maxY + minY) / 2
		width = maxX - minX
		heigth = maxY - minY
		l = None
		dr = None
		return centerX, centerY, width, heigth
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi bounding box: center " + str(r.center()) + " width: " + str(r.width())+ " height: " + str(r.height()))
		try:
			pass
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			pass				
### get ID by attributes
	def getIDByAttributes(self, layer, field, attribute):
		IDs = []
		for f in layer.getFeatures(QgsFeatureRequest( str(field) + " = " + str(attribute))):
			IDs.append(f.id())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID: " + str(IDs))
		return IDs
		
### Get last feauture id
	def getLastFeatureID(self, layer):
		f = QgsFeature()
		for f in layer.getFeatures():
			ID = f.id()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID: " + str(ID))
		return ID
		
### copy a raster band from a multi band raster
	def getRasterBandByBandNumber(self, inputRaster, band, outputRaster, virtualRaster = "No", GDALFormat = None, multiAddList = None):
		if virtualRaster == "No":
			#gdal.AllRegister()
			# open input with GDAL
			rD = gdal.Open(inputRaster, GA_ReadOnly)
			# number of x pixels
			rC = rD.RasterXSize
			# number of y pixels
			rR = rD.RasterYSize
			# check projections
			rP = rD.GetProjection()
			# pixel size and origin
			rGT = rD.GetGeoTransform()
			tD = gdal.GetDriverByName( "GTiff" )
			iRB = rD.GetRasterBand(int(band))
			if GDALFormat is None:
				bDT = iRB.DataType
			else:
				if GDALFormat == "Float64":
					bDT = GDT_Float64
				elif GDALFormat == "Float32":
					bDT = GDT_Float32
			a =  iRB.ReadAsArray()
			if multiAddList is not None:
				a = cfg.utls.arrayMultiplicativeAdditiveFactors(a, multiAddList[0], multiAddList[1])
			oR = tD.Create(outputRaster, rC, rR, 1, bDT)
			oR.SetGeoTransform( [ rGT[0] , rGT[1] , 0 , rGT[3] , 0 , rGT[5] ] )
			oR.SetProjection(rP)
			oRB = oR.GetRasterBand(1)
			oRB.WriteArray(a)
			# close bands
			oRB = None
			iRB = None
			# close rasters
			oR = None
			rD = None
		else:
			vrtCheck = cfg.utls.createVirtualRaster([inputRaster], outputRaster, band)
			time.sleep(1)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "get band: " + unicode(band))
		
### get a raster band statistic
	def getRasterBandStatistics(self, inputRaster, band, multiAddList = None):
		#gdal.AllRegister()
		# open input with GDAL
		rD = gdal.Open(inputRaster, GA_ReadOnly)
		if rD is None:
			bSt = None
			a = None
		else:
			iRB = rD.GetRasterBand(band)
			bSt = iRB.GetStatistics(True, True)
			a =  iRB.ReadAsArray()
			if multiAddList is not None:
				a = cfg.utls.arrayMultiplicativeAdditiveFactors(a, multiAddList[0], multiAddList[1])
				bSt = [bSt[0] * multiAddList[0] + multiAddList[1], bSt[1] * multiAddList[0] + multiAddList[1], bSt[2] * multiAddList[0] + multiAddList[1], bSt[3] * multiAddList[0]]
			# close band
			iRB = None
			# close raster
			rD = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "get band: " + unicode(band))
		return bSt, a
		
### calculate covariance matrix from array list
	def calculateCovMatrix(self, arrayList):
		# create empty array
		d = arrayList[0].shape
		arrCube = np.zeros((d[0], d[1], len(arrayList)), dtype=np.float64)
		i = 0
		try:
			for a in arrayList:
				arrCube[:, :, i] = a
				i = i + 1
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		matrix = arrCube.reshape(d[0] * d[1], len(arrayList))
		# find No data
		NoDt = np.where(np.isnan(matrix[:, 0]))
		# delete No data
		GMatrix = np.delete(matrix, NoDt, axis=0)
		TMatrix = GMatrix.T
		# covariance matrix (degree of freedom = 1 for unbiased estimate)
		CovMatrix = np.cov(TMatrix, ddof=1)
		try:
			if np.isnan(CovMatrix[0,0]):
				CovMatrix = "No"
			try:
				inv = np.linalg.inv(CovMatrix)
				if np.isnan(inv[0,0]):
					CovMatrix = "No"
			except:
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "TEST matrix: " + str(CovMatrix))
				CovMatrix = "No"
		except Exception, err:
			CovMatrix = "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "cov matrix: " + str(CovMatrix))
		return CovMatrix
		
	def createVirtualRaster(self, inputRasterList, output, bandNumber = "No", quiet = "No"):
		r = ""
		st = "No"
		for i in inputRasterList:
			r = r + ' "' + i + '"'
		if bandNumber == "No":
			bndOption = " -separate"
		else:
			bndOption = "-b " + str(bandNumber)
		try:
			cfg.utls.getGDALForMac()
			sP = subprocess.Popen(cfg.gdalPath + 'gdalbuildvrt -resolution highest ' + bndOption + ' "' + output.encode(sys.getfilesystemencoding()) + '" ' + r.encode(sys.getfilesystemencoding()), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				st = "Yes"
				if quiet == "No": 
					cfg.mx.msgWar13()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error: " + str(err) )
		# in case of errors
		except Exception, err:
			cfg.utls.getGDALForMac()
			sP = subprocess.Popen(cfg.gdalPath + 'gdalbuildvrt -resolution highest ' + bndOption + ' "' + output.encode(sys.getfilesystemencoding()) + '" ' + r.encode(sys.getfilesystemencoding()), shell=True)
			sP.wait()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "virtual raster: " + unicode(output))
		return st
					
	# build GDAL overviews
	def buildOverviewsGDAL(self, inputRaster):
		try:
			cfg.utls.getGDALForMac()
			sP = subprocess.Popen(cfg.gdalPath + 'gdaladdo -r NEAREST -ro "' + inputRaster + '" 8 16 32 64 ', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error: " + str(err) )
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "build overviews" + unicode(i))
		# in case of errors
		except Exception, err:
			cfg.utls.getGDALForMac()
			sP = subprocess.Popen(cfg.gdalPath + 'gdaladdo -r NEAREST -ro "' + inputRaster + '" 8 16 32 64 ', shell=True)
			sP.wait()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "build overviews" + unicode(inputRaster))

			
	# create virtual raster with Python
	def createVirtualRaster2(self, inputRasterList, output, bandNumberList = "No", quiet = "No", NoDataVal = "No", relativeToVRT = 0, pansharp = "No", intersection = "Yes", boxCoordList = None):
		# create virtual raster
		#gdal.AllRegister()
		drv = gdal.GetDriverByName("VRT")
		rXList = []
		rYList = []
		topList = []
		leftList = []
		rightList = []
		bottomList = []
		pXSizeList = []
		pYSizeList = []
		for b in inputRasterList:
			gdalRaster = gdal.Open(b, GA_ReadOnly)	
			gt = gdalRaster.GetGeoTransform()
			rP = gdalRaster.GetProjection()
			if rP == "":
				cfg.mx.msgErr47()
				return "Yes"
			pXSizeList.append(abs(gt[1]))
			pYSizeList.append(abs(gt[5]))
			leftList.append(gt[0])
			topList.append(gt[3])
			rightList.append(gt[0] + gt[1] * gdalRaster.RasterXSize)
			bottomList.append(gt[3] + gt[5] * gdalRaster.RasterYSize)
			# number of x pixels
			rXList.append(float(gdalRaster.RasterXSize))
			# number of y pixels
			rYList.append(float(gdalRaster.RasterYSize))
			gdalRaster = None
		# find raster box
		iLeft = min(leftList)
		iTop= max(topList)
		iRight= max(rightList)
		iBottom= min(bottomList)
		# find intersection box
		xLeft = max(leftList)
		xTop= min(topList)
		xRight= min(rightList)
		xBottom= max(bottomList)
		# highest resolution
		pXSize = min(pXSizeList)
		pYSize = min(pYSizeList)
		if boxCoordList is not None:
			try:
				override = boxCoordList[4]
				if override == "Yes":
					# find raster box
					if iLeft < boxCoordList[0]:
						iLeft = iLeft +abs(int(round((iLeft - boxCoordList[0]) / pXSize))) * pXSize
					else:
						iLeft = iLeft - abs(int(round((iLeft - boxCoordList[0]) / pXSize))) * pXSize
					if iTop > boxCoordList[1]:
						iTop= iTop - abs(int(round((iTop -boxCoordList[1]) / pYSize))) * pYSize
					else:
						iTop= iTop + abs(int(round((iTop -boxCoordList[1]) / pYSize))) * pYSize
					if iRight > boxCoordList[2]:
						iRight = iRight - abs(int(round((iRight - boxCoordList[2])  / pXSize))) * pXSize
					else:
						iRight = iRight + abs(int(round((iRight - boxCoordList[2])  / pXSize))) * pXSize
					if iBottom < boxCoordList[3]:
						iBottom = iBottom + abs(int(round((iBottom - boxCoordList[3]) / pYSize))) * pYSize
					else:
						iBottom = iBottom - abs(int(round((iBottom - boxCoordList[3]) / pYSize))) * pYSize
			except:
				# find raster box
				if iLeft < boxCoordList[0]:
					iLeft = iLeft +abs(int(round((iLeft - boxCoordList[0]) / pXSize))) * pXSize
				if iTop > boxCoordList[1]:
					iTop= iTop - abs(int(round((iTop -boxCoordList[1]) / pYSize))) * pYSize
				if iRight > boxCoordList[2]:
					iRight = iRight - abs(int(round((iRight - boxCoordList[2])  / pXSize))) * pXSize
				if iBottom < boxCoordList[3]:
					iBottom = iBottom + abs(int(round((iBottom - boxCoordList[3]) / pYSize))) * pYSize
				# find intersection box
				if xLeft < boxCoordList[0]:
					xLeft =  xLeft +abs(int(round((xLeft - boxCoordList[0]) / pXSize))) * pXSize				
				if xTop > boxCoordList[1]:
					xTop= xTop - abs(int(round((xTop -boxCoordList[1]) / pYSize))) * pYSize
				if xRight > boxCoordList[2]:
					xRight= xRight - abs(int(round((xRight - boxCoordList[2])  / pXSize))) * pXSize
				if xBottom < boxCoordList[3]:
					xBottom = xBottom + abs(int(round((xBottom - boxCoordList[3]) / pYSize))) * pYSize

		# number of x pixels
		if intersection == "Yes":
			rX = abs(int(round((xRight - xLeft) / pXSize)))
			rY = abs(int(round((xTop - xBottom) / pYSize)))
		else:
			rX = abs(int(round((iRight - iLeft) / pXSize)))
			rY = abs(int(round((iTop - iBottom) / pYSize)))
		# create virtual raster
		vRast = drv.Create(output, rX, rY, 0)
		# set raster projection from reference intersection
		if intersection == "Yes":
			vRast.SetGeoTransform((xLeft, pXSize, 0, xTop, 0, -pYSize))
		else:
			vRast.SetGeoTransform((iLeft, pXSize, 0, iTop, 0, -pYSize))
		vRast.SetProjection(rP)
		if len(inputRasterList) == 1 and bandNumberList != "No":
			x = 0
			gdalRaster2 = gdal.Open(b, GA_ReadOnly)
			try:
				for b in bandNumberList:
					gBand2 = gdalRaster2.GetRasterBand(int(b)) 
					noData = gBand2.GetNoDataValue()
					if noData is None or str(noData) == "nan":
						noData = cfg.NoDataVal
					gt = gdalRaster2.GetGeoTransform()
					pX =  abs(gt[1])
					pY = abs(gt[5])
					left = gt[0]
					top = gt[3]
					bsize2 = gBand2.GetBlockSize()
					x_block = bsize2[0]
					y_block = bsize2[1]
					# number of x pixels
					rX2 = gdalRaster2.RasterXSize * int(round(pX / pXSize))
					# number of y pixels
					rY2 = gdalRaster2.RasterYSize * int(round(pY / pYSize))
					# offset
					if intersection == "Yes":
						xoffX = abs(int(round((left - xLeft) / pX)))
						xoffY = abs(int(round((xTop - top) / pY)))
						offX = 0
						offY = 0
					else:
						offX = abs(int(round((left - iLeft) / pXSize)))
						offY = int(round((iTop - top) / pYSize))
						xoffX = 0
						xoffY = 0
					try:
						override = boxCoordList[4]
						if override == "Yes":
							if iLeft < left:
								xoffX = 0
								offX = abs(int(round((left - iLeft) / pXSize)))
							else:
								xoffX = abs(int(round((left - iLeft) / pX)))
								offX = 0
							if iTop > top:
								xoffY = 0
								offY = abs(int(round((iTop - top) / pYSize)))
							else:
								xoffY = abs(int(round((iTop - top) / pY)))
								offY = 0
					except:
						pass
					vRast.AddBand(gdal.GDT_Float64)
					bandNumber = bandNumberList[x]
					band = vRast.GetRasterBand(x + 1)
					bsize = band.GetBlockSize()
					x_block = bsize[0]
					y_block = bsize[1]
					source_path = inputRasterList[0]
					# set metadata xml
					xml = """
					<ComplexSource>
					  <SourceFilename relativeToVRT="%i">%s</SourceFilename>
					  <SourceBand>%i</SourceBand>
					  <SourceProperties RasterXSize="%i" RasterYSize="%i" DataType=%s BlockXSize="%i" BlockYSize="%i" />
					  <SrcRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
					  <DstRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
					  <NODATA>%i</NODATA>
					</ComplexSource>
					"""
					source = xml % (relativeToVRT, source_path.encode(sys.getfilesystemencoding()), bandNumber, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, "Float64", x_block, y_block, xoffX, xoffY, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, offX, offY, rX2, rY2, noData)
					band.SetMetadataItem("ComplexSource", source, "new_vrt_sources")
					if NoDataVal != "No":
						band.SetNoDataValue(NoDataVal)
					band = None
					gBand2 = None
					x = x + 1
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			gdalRaster2 = None
		else:
			x = 0
			for b in inputRasterList:
				gdalRaster2 = gdal.Open(b, GA_ReadOnly)
				gdalBandNumber = gdalRaster2.RasterCount
				for bb in range(1, gdalBandNumber + 1):
					gBand2 = gdalRaster2.GetRasterBand(bb) 
					noData = gBand2.GetNoDataValue()
					if noData is None:
						noData = cfg.NoDataVal
					gt = gdalRaster2.GetGeoTransform()
					pX =  abs(gt[1])
					pY = abs(gt[5])
					left = gt[0]
					top = gt[3]
					bsize2 = gBand2.GetBlockSize()
					x_block = bsize2[0]
					y_block = bsize2[1]
					# number of x pixels
					rX2 = gdalRaster2.RasterXSize * int(round(pX / pXSize))
					# number of y pixels
					rY2 = gdalRaster2.RasterYSize * int(round(pY / pYSize))
					# offset
					if intersection == "Yes":
						xoffX = abs(int(round((left - xLeft) / pX)))
						xoffY = abs(int(round((xTop - top) / pY)))
						offX = 0
						offY = 0
					else:
						offX = abs(int(round((left - iLeft) / pXSize)))
						offY = int(round((iTop - top) / pYSize))
						xoffX = 0
						xoffY = 0
					try:
						override = boxCoordList[4]
						if override == "Yes":
							if iLeft < left:
								xoffX = 0
								offX = abs(int(round((left - iLeft) / pXSize)))
							else:
								xoffX = abs(int(round((left - iLeft) / pX)))
								offX = 0
							if iTop > top:
								xoffY = 0
								offY = abs(int(round((iTop - top) / pYSize)))
							else:
								xoffY = abs(int(round((iTop - top) / pY)))
								offY = 0
					except:
						pass
					gBand2 = None
					vRast.AddBand(gdal.GDT_Float64)
					try:
						errorCheck = "Yes"
						if bandNumberList == "No":
							bandNumber = 1
						else:
							bandNumber = bandNumberList[x]
						errorCheck = "No"	
						band = vRast.GetRasterBand(x + 1)
						bsize = band.GetBlockSize()
						x_block = bsize[0]
						y_block = bsize[1]
						source_path = b.replace("//", "/")
						# set metadata xml
						xml = """
						<ComplexSource>
						  <SourceFilename relativeToVRT="%i">%s</SourceFilename>
						  <SourceBand>%i</SourceBand>
						  <SourceProperties RasterXSize="%i" RasterYSize="%i" DataType=%s BlockXSize="%i" BlockYSize="%i" />
						  <SrcRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
						  <DstRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
						  <NODATA>%i</NODATA>
						</ComplexSource>
						"""
						source = xml % (relativeToVRT, source_path.encode(sys.getfilesystemencoding()), bandNumber, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, "Float64", x_block, y_block, xoffX, xoffY, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, offX, offY, rX2, rY2, noData)
						band.SetMetadataItem("ComplexSource", source, "new_vrt_sources")
						if NoDataVal != "No":
							band.SetNoDataValue(NoDataVal)
						band = None
						x = x + 1
					except Exception, err:
						if errorCheck == "No":
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				gdalRaster2 = None
		vRast = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "virtual raster: " + unicode(output))
		return unicode(output)
			
	# convert list to covariance array
	def listToCovarianceMatrix(self, list):
		try:
			covMat = np.zeros((len(list), len(list)), dtype=np.float64)
			i = 0
			for x in list:
				covMat[i, :] = x
				i = i + 1
			return covMat
		except Exception, err:
			list = "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		return "No"
		
	# convert covariance array to list
	def covarianceMatrixToList(self, covarianceArray):
		try:
			d = covarianceArray.shape
			list = []
			for i in range(0, d[0]):
				list.append(covarianceArray[i, :].tolist())
		except Exception, err:
			list = "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		return list
		
	# clip a raster using a shapefile
	def clipRasterByShapefile(self,  shapefile, raster, outputRaster = None, outFormat = "GTiff"):
		dT = self.getTime()
		if outputRaster is None:
			# temp files
			tRN = cfg.copyTmpROI + dT + ".tif"
			tR = str(cfg.tmpDir + "//" + tRN)
		else:
			tR = str(outputRaster)
		tPMN = cfg.tmpVrtNm + ".vrt"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
	# convert polygon to raster 
		tRNxs = cfg.copyTmpROI + dT + "xs.tif"
		tRxs = str(cfg.tmpDir + "//" + tRNxs)
		check = self.vectorToRaster(cfg.emptyFN, unicode(shapefile), cfg.emptyFN, tRxs, unicode(raster), None, str(outFormat), 1)
		if check != "No":
			cfg.utls.clipRasterByRaster(raster, tRxs, tR, outFormat, cfg.NoDataVal)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "shapefile " + unicode(shapefile) + "raster " + unicode(raster) + "tR " + unicode(tR))
			return tR
		else:
			return "No"
		
	# clip raster with another raster
	def clipRasterByRaster(self, rasterClipped, rasterClipping, outputRaster = None, outFormat = "GTiff", nodataValue=None):
		dT = self.getTime()
		tPMN = cfg.tmpVrtNm + ".vrt"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		bList = [rasterClipped, rasterClipping]
		iBC = cfg.utls.getNumberBandRaster(rasterClipped)
		# create band list of clipped bands and clipping band
		bandNumberList = []
		for cc in range(1, iBC + 1):
			bandNumberList.append(cc)
		bandNumberList.append(1)
		vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", cfg.NoDataVal, 0)
		# open input with GDAL
		rD = gdal.Open(tPMD, GA_ReadOnly)
		if rD is None:
			cfg.mx.msg4()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " None raster")
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			return "No"
		try:
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			bC = len(bL)
			# output rasters
			oM = []
			oM.append(outputRaster)
			oMR = cfg.utls.createRasterFromReference(rD, bC - 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, "No")
			for bb in range(0, bC - 1):
				e = str("a * b")
				variableList = [["im1", "a"], ["im2", "b"]]
				o = cfg.utls.processRaster(rD, [bL[bb], bL[bC - 1]], None, "No", cfg.utls.bandCalculation, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "No")
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster " + unicode(outputRaster))
		return outputRaster
		
	# copy a raster
	def copyRaster(self, raster, outputRaster = None, outFormat = "GTiff", nodataValue=None):
		# open input with GDAL
		rD = gdal.Open(raster, GA_ReadOnly)
		if rD is None:
			cfg.mx.msg4()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " None raster")
			return "No"
		# band list
		bL = cfg.utls.readAllBandsFromRaster(rD)
		bC = len(bL)
		# output rasters
		oM = []
		oM.append(outputRaster)
		oMR = cfg.utls.createRasterFromReference(rD, bC, oM, nodataValue, outFormat, cfg.rasterDataType, 0,  None, "No")
		for bb in range(0, bC):
			e = str("a * 1")
			variableList = [["im1", "a"]]
			o = cfg.utls.processRaster(rD, [bL[bb]], None, "No", cfg.utls.bandCalculation, None, oMR , None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "No")
		# close GDAL rasters
		for b in range(0, len(oMR)):
			oMR[b] = None
		for b in range(0, len(bL)):
			bL[b] = None
		rD = None
		return outputRaster
		
	# connect with password
	def passwordConnect(self, user, password, url, topLevelUrl, outputPath = None, progress = None):
		try:
			pswMng = urllib2.HTTPPasswordMgrWithDefaultRealm()
			pswMng.add_password(None, topLevelUrl, user, password)
			handler = urllib2.HTTPBasicAuthHandler(pswMng)
			opener = urllib2.build_opener(handler)
			if outputPath is None:
				response = opener.open(url)
				return response
			else:
				urllib2.install_opener(opener)
				f = urllib2.urlopen(url)
				total_size = int(f.headers["Content-Length"])
				MB_size = total_size/1048576
				block_size = 64 * 1024
				with open(outputPath, "wb") as file:
					while True:
						block = f.read(block_size)
						dSize =  int(os.stat(outputPath).st_size)/1048576
						cfg.uiUtls.updateBar(progress, "(" + str(dSize) + "/" + str(MB_size) + " MB) " +  url, "Downloading")
						qApp.processEvents()
						if not block:
							break
						file.write(block)
						if cfg.actionCheck == "No":
							raise ValueError('Cancel action')
				return "Yes"
		except Exception, err:
			cfg.mx.msgErr49()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
	
	# encrypt password
	def encryptPassword(self, password):
		e = base64.b64encode(password)
		return e
		
	# decrypt password
	def decryptPassword(self, password):
		d = base64.b64decode(password)
		return d
		
	# download file
	def downloadFile(self, urlIn, outputPath, fileName = None, progress = None):
		try:
			urllib.urlretrieve(urlIn, outputPath, lambda blocks_transferred, block_size, total_size, fileName=fileName: self.downloadReporthook(blocks_transferred, block_size, total_size, fileName, progress))
			return "Yes"
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"

			
	# download reportHook
	def downloadReporthook(self, blocks_transferred, block_size, total_size, fileName = None, progress = None):
		totalBlocks = total_size / block_size
		blockList = range(1, totalBlocks, 100)
		if blocks_transferred in blockList:
			MB_transferred = int(blocks_transferred * block_size) / 1048576
			MB_size = total_size/1048576
			cfg.uiUtls.updateBar(progress, "(" + str(MB_transferred) + "/" + str(MB_size) + " MB) " +  fileName, "Downloading")
			qApp.processEvents()
			if cfg.actionCheck == "No":
				raise ValueError('Cancel action')
			
	# set GDAL cache max
	def setGDALCacheMax(self, value):
		c = gdal.GetCacheMax()
		gdal.SetCacheMax(value)
		
	# get  time
	def getTime(self):
		t = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
		return t
		
	# create a polygon shapefile with OGR
	def createEmptyShapefile(self, crsWkt, outputVector):
		d = ogr.GetDriverByName('ESRI Shapefile')
		dS = d.CreateDataSource(outputVector)
		# shapefile
		sR = osr.SpatialReference()
		sR.ImportFromWkt(crsWkt)
		rL = dS.CreateLayer('NewLayer', sR, ogr.wkbPolygon)
		fN = cfg.emptyFN
		fd = ogr.FieldDefn(fN, ogr.OFTInteger)
		rL.CreateField(fd)
		rL = None
		dS = None
		
	# create a polygon shapefile with QGIS
	def createEmptyShapefileQGIS(self, crs, outputVector):
		fields = QgsFields()
		# add field
		fN = cfg.emptyFN
		fields.append(QgsField(fN, QVariant.Int))	
		QgsVectorFileWriter(unicode(outputVector), "CP1250", fields, QGis.WKBPolygon, crs, "ESRI Shapefile")
		
### Group index by its name
	def groupIndex(self, groupName):
		g = cfg.lgnd.groups()
		if len(g) > 0:
			# all positions
			aP = len(g)
			for p in range(0, aP):
				if g[p] == groupName:
						# group position
						return p
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group " + unicode(groupName) + " Position: " + unicode(p))

### Raster top left origin and pixel size
	def imageInformation(self, imageName):
		try:
			i = self.selectLayerbyName(imageName, "Yes")
			# TopLeft X coord
			tLX = i.extent().xMinimum()
			# TopLeft Y coord
			tLY = i.extent().yMaximum()
			# pixel size
			pS = i.rasterUnitsPerPixelX()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "image: " + unicode(imageName) + " topleft: (" + str(tLX) + ","+ str(tLY) + ")")
			# return a tuple TopLeft X, TopLeft Y, and Pixel size
			return tLX, tLY, pS
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return None, None, None
			
### Raster size
	def imageInformationSize(self, imageName):
		try:
			i = self.selectLayerbyName(imageName, "Yes")
			# TopLeft X coord
			tLX = i.extent().xMinimum()
			# TopLeft Y coord
			tLY = i.extent().yMaximum()
			# LowRight X coord
			lRY = i.extent().yMinimum()
			# LowRight Y coord
			lRX = i.extent().xMaximum()
			# pixel size
			pS = i.rasterUnitsPerPixelX()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "image: " + unicode(imageName) + " topleft: (" + str(tLX) + ","+ str(tLY) + ")")
			# return a tuple TopLeft X, TopLeft Y, and Pixel size
			return tLX, tLY, lRX, lRY, pS
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return None, None, None, None, None
						
### Layer ID by its name
	def layerID(self, layerName):
	 	ls = cfg.lgnd.layers()
		for l in ls:
			lN = l.name()
			if lN == layerName:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer: " + unicode(layerName) + " ID: " + unicode(l.id()))
				return l.id()
						
### Get the code line number for log file
	def lineOfCode(self):
		return str(inspect.currentframe().f_back.f_lineno)
		
### logger condition
	def logCondition(self, function, message):
		if cfg.logSetVal == "Yes":
			cfg.utls.logToFile(function, message)
		
### Logger of functions
	def logToFile(self, function, message):
		# message string
		m = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S.%f") + "	" + function + "	" + message + "\n"
		if os.path.isfile(cfg.logFile):
			try:
				l = open(cfg.logFile, 'a')
			except:
				pass
		else:
			l = open(cfg.logFile, 'w')
			try:
				l.write("Date	Function	Message \n")
				l.write(m)
				l.close()
			except:
				pass
		try:
			l.write(m)
			l.close()
		except:
			pass
		
### Pan action
	def pan(self):
		cfg.toolPan = QgsMapToolPan(cfg.cnvs)
		cfg.cnvs.setMapTool(cfg.toolPan)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pan action")
		
### Question box
	def questionBox(self, caption, message):
		i = QWidget()
		q = QMessageBox.question(i, caption, message, QMessageBox.Yes, QMessageBox.No)
		if q == QMessageBox.Yes:
			return "Yes"
		if q == QMessageBox.No:
			return "No"
		
	# Define vector symbology
	def vectorSymbol(self, layer, signatureList, macroclassCheck):
		c = []
		n = []
		# class count
		mc = []
		v = signatureList
		s = QgsSymbolV2.defaultSymbol(layer.geometryType())
		s.setColor(QColor("#000000"))
		c.append(QgsRendererCategoryV2(0, s, "0 - " + cfg.uncls))
		for i in range(0, len(v)):
				if macroclassCheck == "Yes":
					if int(v[i][0]) not in mc:
						mc.append(int(v[i][0]))
						n.append([int(v[i][0]), v[i][6], str(v[i][1])])
				else:
					n.append([int(v[i][2]), v[i][6], str(v[i][3])])
		for b in sorted(n, key=lambda c: c[0]):
			s = QgsSymbolV2.defaultSymbol(layer.geometryType())
			s.setColor(b[1])
			ca = QgsRendererCategoryV2(b[0], s, str(b[0]) + " - " + b[2])
			c.append(ca)
		f = str(cfg.fldID_class)
		r = QgsCategorizedSymbolRendererV2(f, c)
		layer.setRendererV2(r)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		
	# Define class symbology
	def rasterSymbol(self, classLayer, signatureList, macroclassCheck):
		classLayer.setDrawingStyle("SingleBandPseudoColor")
		# The band of classLayer
		cLB = 1
		# Color list for ramp
		cL = []
		n = []
		# class count
		mc = []
		v = signatureList
		cL.append(QgsColorRampShader.ColorRampItem(0, QColor("#000000"), "0 - " + cfg.uncls))
		for i in range(0, len(v)):
			if macroclassCheck == "Yes":
				if int(v[i][0]) not in mc and int(v[i][0]) != 0:
					mc.append(int(v[i][0]))
					n.append([int(v[i][0]), v[i][6], str(v[i][1])])
			else:
				if int(v[i][2]) != 0:
					n.append([int(v[i][2]), v[i][6], str(v[i][3])])
		for b in sorted(n, key=lambda c: c[0]):
			cL.append(QgsColorRampShader.ColorRampItem(b[0], b[1], str(b[0]) + " - " + b[2]))
		# Create the shader
		lS = QgsRasterShader()
		# Create the color ramp function
		cR = QgsColorRampShader()
		cR.setColorRampType(QgsColorRampShader.EXACT)
		cR.setColorRampItemList(cL)
		# Set the raster shader function
		lS.setRasterShaderFunction(cR)
		# Create the renderer
		lR = QgsSingleBandPseudoColorRenderer(classLayer.dataProvider(), cLB, lS)
		# Apply the renderer to classLayer
		classLayer.setRenderer(lR)
		# refresh legend
		if hasattr(classLayer, "setCacheImage"):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(classLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(classLayer.source()))
		
	# Define class symbology
	def rasterPreviewSymbol(self, previewLayer, algorithmName):
		if algorithmName == cfg.algMinDist or algorithmName == cfg.algSAM:
			cfg.utls.rasterSymbolPseudoColor(previewLayer)
		elif algorithmName == cfg.algML:
			cfg.utls.rasterSymbolSingleBandGray(previewLayer)
			
	# Define class symbology pseudo color
	def rasterSymbolPseudoColor(self, layer):
		layer.setDrawingStyle("SingleBandPseudoColor")
		# Band statistics
		bndStat = layer.dataProvider().bandStatistics(1)
		max = bndStat.maximumValue
		min = bndStat.minimumValue
		# The band of layer
		cLB = 1
		# Color list for ramp
		cL = []
		colorMin = QColor("#ffffff")
		colorMax = QColor("#000000")
		cL.append(QgsColorRampShader.ColorRampItem(min, colorMin, str(min)))
		cL.append(QgsColorRampShader.ColorRampItem(max, colorMax, str(max)))
		# Create the shader
		lS = QgsRasterShader()
		# Create the color ramp function
		cR = QgsColorRampShader()
		cR.setColorRampType(QgsColorRampShader.INTERPOLATED)
		cR.setColorRampItemList(cL)
		# Set the raster shader function
		lS.setRasterShaderFunction(cR)
		# Create the renderer
		lR = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), cLB, lS)
		# Apply the renderer to layer
		layer.setRenderer(lR)
		# refresh legend
		if hasattr(layer, "setCacheImage"):
			layer.setCacheImage(None)
		layer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(layer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(layer.source()))
		
	# Define class symbology single band grey
	def rasterSymbolSingleBandGray(self, layer):
		layer.setDrawingStyle("SingleBandGray")
		layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, QgsRaster.ContrastEnhancementCumulativeCut)
		# refresh legend
		if hasattr(layer, "setCacheImage"):
			layer.setCacheImage(None)
		layer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(layer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(layer.source()))
		
### Split raster into single bands, and return a list of images
	def rasterToBands(self, rasterPath, outputFolder, outputName = None, progressBar = "No", multiAddList = None):
		dT = self.getTime()
		iBC = cfg.utls.getNumberBandRaster(rasterPath)
		iL = []
		if outputName is None:
			name = cfg.splitBndNm + dT
		else:
			name = outputName
		progresStep = int(100 / iBC)
		i = 1
		for x in range(1, iBC+1):
			if cfg.actionCheck == "Yes":
				xB = outputFolder + "/" + name + "_B" + str(x) + ".tif"
				if multiAddList is not None:
					self.getRasterBandByBandNumber(rasterPath, x, xB, "No", None, multiAddList[x - 1])
				else:
					self.getRasterBandByBandNumber(rasterPath, x, xB, "No", None)
				iL.append(xB)
				if progressBar == "Yes":
					cfg.uiUtls.updateBar(progresStep * i)
					i = i + 1
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster: " + unicode(rasterPath) + " split to bands")
		return iL
		
### Get the number of bands of a raster
	def getNumberBandRaster(self, raster):
		#gdal.AllRegister()
		rD = gdal.Open(raster, GA_ReadOnly)
		number = rD.RasterCount
		rD = None
		return number
		
	# delete all items in a table
	def clearTable(self, table):
		table.clearContents()
		for i in range(0, table.rowCount()):
			table.removeRow(0)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			
	# calculate raster block ranges
	def rasterBlocks(self, gdalRaster, blockSizeX = 1, blockSizeY = 1, previewSize = 0, previewPoint = None):
		# number of x pixels
		rX = gdalRaster.RasterXSize
		# number of y pixels
		rY = gdalRaster.RasterYSize
		# list of range pixels
		lX = None
		lY = None
		if blockSizeX != 1 or blockSizeY !=1:
			lX = range(0, rX, blockSizeX)
			lY = range(0, rY, blockSizeY)
		# classification preview
		if previewPoint != None:
			geoT = gdalRaster.GetGeoTransform()
			tLX = geoT[0]
			tLY = geoT[3]
			pSX = geoT[1]
			pSY = geoT[5]
			# start and end pixels
			sX = (int((previewPoint.x() - tLX) / pSX)) - int(previewSize / 2)
			eX = (int((previewPoint.x() - tLX) / pSX)) + int(previewSize / 2)
			sY = -(int((tLY - previewPoint.y()) / pSY)) - int(previewSize / 2)
			eY = -(int((tLY - previewPoint.y()) / pSY)) + int(previewSize / 2)
			# if start outside image
			if sX < 0:
				sX = 0
			if sY < 0:
				sY = 0
			if eX > rX:
				eX = rX
			if eY > rY:
				eY = rY
			if blockSizeX > previewSize:
					blockSizeX = previewSize
			if blockSizeY > previewSize:
					blockSizeY = previewSize
			# raster range blocks
			lX = range(sX, eX, blockSizeX)
			lY = range(sY, eY, blockSizeY)
			# preview range blocks
			pX = range(0, previewSize, blockSizeX)
			pY = range(0, previewSize, blockSizeY)
		# if not preview
		else:
			# set pX and pY if not preview
			pX = lX
			pY = lY
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return rX, rY, lX, lY, pX, pY
		
	# read a block of band as array
	def readArrayBlock(self, gdalBand, pixelStartColumn, pixelStartRow, blockColumns, blockRow):
		a = gdalBand.ReadAsArray(pixelStartColumn, pixelStartRow, blockColumns, blockRow)
		return a
		
	# apply multiplicative and additivie factors to array
	def arrayMultiplicativeAdditiveFactors(self, array, multiplicativeFactor, additiveFactor):
		a = array * float(multiplicativeFactor) + float(additiveFactor)
		return a
		
	# write an array to band
	def writeArrayBlock(self, gdalRaster, bandNumber, dataArray, pixelStartColumn, pixelStartRow, nodataValue=None):
		b = gdalRaster.GetRasterBand(bandNumber)
		x = gdalRaster.RasterXSize - pixelStartColumn 
		y = gdalRaster.RasterYSize - pixelStartRow
		dataArray = dataArray[:y, :x]
		b.WriteArray(dataArray, pixelStartColumn, pixelStartRow)
		if nodataValue is not None:
			b.SetNoDataValue(nodataValue)
		b.FlushCache()
		b = None
	
	# create raster from another raster
	def createRasterFromReference(self, gdalRasterRef, bandNumber, outputRasterList, nodataValue = None, driver = "GTiff", format = GDT_Float64, previewSize = 0, previewPoint = None, compress = "No", compressFormat = "DEFLATE21"):
		oRL = []
		if format == "Float64":
			format = GDT_Float64
		elif format == "Float32":
			format = GDT_Float32
		for o in outputRasterList:
			# pixel size and origin from reference
			rP = gdalRasterRef.GetProjection()
			rGT = gdalRasterRef.GetGeoTransform()
			tD = gdal.GetDriverByName(driver)
			c = gdalRasterRef.RasterXSize
			r = gdalRasterRef.RasterYSize
			if previewSize > 0:
				tLX = rGT[0]
				tLY = rGT[3]
				pSX = rGT[1]
				pSY = rGT[5]
				sX = int((previewPoint.x() - tLX) / pSX) - int(previewSize / 2)
				sY = int((tLY - previewPoint.y()) / np.sqrt(pSY ** 2)) - int(previewSize / 2)
				lX = tLX + sX * pSX
				tY = tLY + sY * pSY
				if tY > tLY:
					tY = tLY
				if lX < tLX:
					lX = tLX
				if previewSize < c:
					c = previewSize
				if previewSize < r:
					r = previewSize
				rGT = (lX, rGT[1], rGT[2], tY,  rGT[4],  rGT[5])
			if compress == "No":
				oR = tD.Create(o, c, r, bandNumber, format)
			elif compress == "DEFLATE21":
				oR = tD.Create(o, c, r, bandNumber, format, options = ['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=1'])
			else:
				oR = tD.Create(o, c, r, bandNumber, format, ['COMPRESS=' + compressFormat])
			# set raster projection from reference
			oR.SetGeoTransform(rGT)
			oR.SetProjection(rP)
			oRL.append(oR)
			if nodataValue is not None:
				for x in range(1, bandNumber+1):
					b = oR.GetRasterBand(x)
					b.SetNoDataValue(nodataValue)
					b.Fill(nodataValue)
					b = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(outputRasterList))
		return oRL
		
	# create one raster for each signature class
	def createSignatureClassRaster(self, signatureList, gdalRasterRef, outputDirectory, nodataValue = None, outputName = None, previewSize = 0, previewPoint = None, compress = "No", compressFormat = "DEFLATE21"):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "start createSignatureClassRaster")	
		dT = self.getTime()
		outputRasterList = []
		for s in range(0, len(signatureList)):
			if outputName == None:
				o = outputDirectory + "/" + cfg.sigRasterNm + "_" + str(signatureList[s][0]) + "_" + str(signatureList[s][2]) + "_" + dT + ".tif"
			else:
				o = outputDirectory + "/" + outputName + "_" + str(signatureList[s][0]) + "_" + str(signatureList[s][2]) + ".tif"
			outputRasterList.append(o)
		oRL = self.createRasterFromReference(gdalRasterRef, 1, outputRasterList, nodataValue, "GTiff", cfg.rasterDataType, previewSize, previewPoint, compress, compressFormat)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "end createSignatureClassRaster")
		return oRL, outputRasterList
		
	# convert seconds to H M S
	def timeToHMS(self, time):
		min, sec = divmod(time, 60)
		hour, min = divmod(min, 60)
		if hour > 0:
			m = str("%.f" % round(hour)) + " H " + str("%.f" % round(min)) + " min"
		else:
			m = str("%.f" % round(min)) + " min " + str("%.f" % round(sec)) + " sec"
		return m
		
	# perform classification
	def classification(self, gdalBandList, signatureList, algorithmName, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, outputAlgorithmRaster, outputClassificationRaster, nodataValue, macroclassCheck, previewSize, pixelStartColumnPreview, pixelStartRowPreview, progressStart, progresStep, remainingBlocks, progressMessage):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "start classification block")
		sigArrayList = self.createArrayFromSignature(gdalBandList, signatureList)
		bN = 0
		minArray = None
		maxArray = None
		classArray = None
		n = 0
		StartT = 0
		itCount = 0
		itTot = len(sigArrayList)
		progresStep = progresStep / len(sigArrayList)
		if algorithmName == cfg.algMinDist:
			tr = self.thresholdList(signatureList)
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = time.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = time.clock()
					# algorithm
					rasterArrayx = np.copy(rasterArray)
					c = self.algorithmMinimumDistance(rasterArrayx, s, cfg.algBandWeigths)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithmMinimumDistance signature" + str(itCount))
					# threshold
					algThrshld = float(tr[n])
					if algThrshld > 0:
						c = self.minimumDistanceThreshold(c, algThrshld, nodataValue)
					if type(c) is not int:
						oR = outputGdalRasterList[bN]
						if previewSize > 0:
							pixelStartColumn = int(pixelStartColumnPreview)
							pixelStartRow = int(pixelStartRowPreview)
						# algorithm raster
						self.writeArrayBlock(oR, 1, c, pixelStartColumn, pixelStartRow, nodataValue)
						if minArray is None:
							minArray = c
						else:
							minArray = self.findMinimumArray(c, minArray, nodataValue)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMinimumArray signature" + str(itCount))
						# minimum raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, minArray, pixelStartColumn, pixelStartRow, nodataValue)
						# signature classification raster
						if macroclassCheck == "Yes":
							clA = self.classifyClasses(c, minArray, signatureList[n][0])
						else:
							clA = self.classifyClasses(c, minArray, signatureList[n][2])
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
						# classification raster
						if classArray == None:
							classArray = clA
						else:
							e = np.ma.masked_equal(clA, 0)
							classArray =  e.mask * classArray + clA
							e = None
						clA = None
						classArray[classArray == cfg.unclassifiedVal] = 0
						# classification raster
						self.writeArrayBlock(outputClassificationRaster, 1, classArray, pixelStartColumn, pixelStartRow, nodataValue)
						bN = bN + 1
						n = n + 1
					else:
						return "No"
				else:
					return "No"
		elif algorithmName == cfg.algSAM:
			tr = self.thresholdList(signatureList)
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = time.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						#cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
						pass
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = time.clock()
					# algorithm
					rasterArrayx = np.copy(rasterArray)
					c = self.algorithmSAM(rasterArrayx, s, cfg.algBandWeigths)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithmSAM signature" + str(itCount))
					# threshold
					algThrshld = float(tr[n])
					if algThrshld > 0:
						if algThrshld > 90:
							algThrshld = 90
						c = self.minimumDistanceThreshold(c, algThrshld, nodataValue)
					if type(c) is not int:
						oR = outputGdalRasterList[bN]
						if previewSize > 0:
							pixelStartColumn = int(pixelStartColumnPreview)
							pixelStartRow = int(pixelStartRowPreview)
						# algorithm raster
						self.writeArrayBlock(oR, 1, c, pixelStartColumn, pixelStartRow, nodataValue)
						if minArray is None:
							minArray = c
						else:
							minArray = self.findMinimumArray(c, minArray, nodataValue)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMinimumArray signature" + str(itCount))
						# minimum raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, minArray, pixelStartColumn, pixelStartRow, nodataValue)
						# signature classification raster
						if macroclassCheck == "Yes":
							clA = self.classifyClasses(c, minArray, signatureList[n][0])
						else:
							clA = self.classifyClasses(c, minArray, signatureList[n][2])
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
						# classification raster
						if classArray == None:
							classArray = clA
						else:
							e = np.ma.masked_equal(clA, 0)
							classArray =  e.mask * classArray + clA
							e = None
						clA = None
						classArray[classArray == cfg.unclassifiedVal] = 0
						# classification raster
						self.writeArrayBlock(outputClassificationRaster, 1, classArray, pixelStartColumn, pixelStartRow, nodataValue)
						bN = bN + 1
						n = n + 1
					else:
						return "No"
				else:
					return "No"
		elif algorithmName == cfg.algML:
			covMatrList = self.covarianceMatrixList(signatureList)
			tr = self.thresholdList(signatureList)
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = time.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = time.clock()
					# algorithm
					rasterArrayx = np.copy(rasterArray)
					# threshold
					algThrshld = float(tr[n])
					if algThrshld > 100:
						algThrshld = 100
					c = self.algorithmMaximumLikelihood(rasterArrayx, s, covMatrList[n], cfg.algBandWeigths, algThrshld)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithmMaximumLikelihood signature" + str(itCount))
					if algThrshld > 0:
						c = self.maximumLikelihoodThreshold(c, nodataValue)
					if type(c) is not int:					
						oR = outputGdalRasterList[bN]
						if previewSize > 0:
							pixelStartColumn = int(pixelStartColumnPreview)
							pixelStartRow = int(pixelStartRowPreview)
						# algorithm raster
						self.writeArrayBlock(oR, 1, c, pixelStartColumn, pixelStartRow, nodataValue)
						if maxArray is None:
							maxArray = c
						else:
							maxArray = self.findMaximumArray(c, maxArray, nodataValue)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMaximumArray signature" + str(itCount))
						# maximum raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, maxArray, pixelStartColumn, pixelStartRow, nodataValue)
						# signature classification raster
						if macroclassCheck == "Yes":
							clA = self.classifyClasses(c, maxArray, signatureList[n][0])
						else:
							clA = self.classifyClasses(c, maxArray, signatureList[n][2])
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
						# classification raster
						if classArray == None:
							classArray = clA
						else:
							e = np.ma.masked_equal(clA, 0)
							classArray =  e.mask * classArray + clA
							e = None
						clA = None
						classArray[classArray == cfg.unclassifiedVal] = 0
						# classification raster
						self.writeArrayBlock(outputClassificationRaster, 1, classArray, pixelStartColumn, pixelStartRow, nodataValue)
						bN = bN + 1
						n = n + 1
					else:
						return "No"
				else:
					return "No"
		classArray = None
		rasterArrayx = None
		c = None
		try:
			minArray = None
		except:
			pass
		try:
			maxArray = None
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "end classification block")
		return "Yes"
				
	def createRasterTable(self, rasterPath, bandNumber, signatureList):
		r = gdal.Open(rasterPath, GA_Update)
		b = r.GetRasterBand(bandNumber)
		at = gdal.RasterAttributeTable()
		at.CreateColumn(str(cfg.fldID_class), gdal.GFT_Integer, gdal.GFU_Generic )
		at.CreateColumn(str(cfg.fldROI_info), gdal.GFT_String, gdal.GFU_Generic )
		v = signatureList
		if cfg.macroclassCheck == "Yes":
			mc = []
			for c in range(len(v)):
				mc.append(int(v[c][0]))
			mcList = list(set(mc))
			for i in range(len(mcList)):
				at.SetValueAsInt(i, 0, mcList[i])
				ind = mc.index(mcList[i])
				at.SetValueAsString(i, 1, v[ind][1])
		else:
			for i in range(len(v)):
				at.SetValueAsInt(i, 0, int(v[i][2]))
				at.SetValueAsString(i, 1, v[i][3])
		b.SetDefaultRAT(at)
		b = None
		r = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(rasterPath))
				
	# classify classes
	def classifyClasses(self, algorithmArray, minimumArray, classID, nodataValue = -999):
		if int(classID) == 0:
			classID = cfg.unclassifiedVal
		cB = np.equal(algorithmArray, minimumArray) * int(classID)
		cA = np.where(minimumArray != nodataValue, cB, cfg.unclassifiedVal)
		return cA
		
	# find minimum array
	def findMinimumArray(self, firstArray, secondArray, nodataValue = -999):
		f = np.where(firstArray == nodataValue, cfg.maxValDt, firstArray)
		s = np.where(secondArray == nodataValue, cfg.maxValDt, secondArray)
		n = np.minimum(f, s)
		m = np.where(n == cfg.maxValDt, nodataValue, n)
		return m
		
	# find maximum array
	def findMaximumArray(self, firstArray, secondArray, nodataValue = -999):
		f = np.where(firstArray == nodataValue, cfg.maxLikeNoDataVal, firstArray)
		s = np.where(secondArray == nodataValue, cfg.maxLikeNoDataVal, secondArray)
		m = np.maximum(f, s)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return m
		
	# set threshold
	def maximumLikelihoodThreshold(self, array, nodataValue = 0):	
		outArray = np.where(array > cfg.maxLikeNoDataVal, array, nodataValue)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return outArray
		
	# set threshold
	def minimumDistanceThreshold(self, array, threshold, nodataValue = 0):	
		outArray = np.where(array < threshold, array, nodataValue)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return outArray
		
	def createArrayFromSignature(self, gdalBandList, signatureList):
		arrayList = []
		for s in signatureList:
			val = s[4]
			array = np.zeros((len(gdalBandList)), dtype=np.float64)
			max = len(gdalBandList) * 2
			i = 0
			for b in range(0, max, 2):
				array[i] = val[b]
				i = i + 1
			arrayList.append(array)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return arrayList
	
	# minimum Euclidean distance algorithm [ sqrt( sum( (r_i - s_i)^2 ) ) ]
	def algorithmMinimumDistance(self, rasterArray, signatureArray, weightList = None):
		try:
			if weightList is not None:
				c = 0
				for w in weightList:
					rasterArray[:,:,c] *= w
					signatureArray[c] *= w
					c = c + 1
			algArray = np.sqrt(((rasterArray - signatureArray)**2).sum(axis = 2))
			return algArray
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
		
	# create covariance matrix list from signature list
	def covarianceMatrixList(self, signatureList):
		c = []
		for s in signatureList:
			cov = s[7]
			c.append(cov)
		return c

	# create threshold list from signature list
	def thresholdList(self, signatureList):
		c = []
		for s in signatureList:
			t = s[8]
			c.append(t)
		return c
		
	# calculate critical chi square and threshold
	def chisquare(self, algThrshld):
		p = 1 - (algThrshld / 100)
		chi = dist.chi2.isf(p, 4)
		return chi
		
	# Maximum Likelihood algorithm
	def algorithmMaximumLikelihood(self, rasterArray, signatureArray, covarianceMatrixZ, weightList = None, algThrshld = 0):
		try:
			covarianceMatrix = np.copy(covarianceMatrixZ)
			if weightList is not None:
				c = 0
				for w in weightList:
					rasterArray[:,:,c] *= w
					signatureArray[c] *= w
					c = c + 1
			(sign, logdet) = np.linalg.slogdet(covarianceMatrix)
			invC = np.linalg.inv(covarianceMatrix)
			d = rasterArray - signatureArray
			algArray = - logdet - (np.dot(d, invC) * d).sum(axis = 2)
			if algThrshld > 0:
				chi = self.chisquare(algThrshld)
				threshold = - chi - logdet
				algArray = np.where(algArray < threshold, cfg.maxLikeNoDataVal, algArray)
			return algArray
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
		
	# spectral angle mapping algorithm [ arccos( sum(r_i * s_i) / ( sum(r_i**2) * sum(s_i**2) ) ) ]
	def algorithmSAM(self, rasterArray, signatureArray, weightList = None):
		try:
			if weightList is not None:
				c = 0
				for w in weightList:
					rasterArray[:,:,c] *= w
					signatureArray[c] *= w
					c = c + 1
			algArray = np.arccos((rasterArray * signatureArray).sum(axis = 2) / np.sqrt((rasterArray**2).sum(axis = 2) * (signatureArray**2).sum())) * 180 / np.pi
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			return algArray
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
			
	# calculate Jeffries-Matusita distance Jij = 2[1 − e^(−B)] from Richards, J. A. & Jia, X. 2006. Remote Sensing Digital Image Analysis: An Introduction, Springer.
	def jeffriesMatusitaDistance(self, signatureArrayI, signatureArrayJ, covarianceMatrixI, covarianceMatrixJ, weightList = None):
		try:
			I = np.array(signatureArrayI)
			J = np.array(signatureArrayJ)
			cI = np.copy(covarianceMatrixI)
			cJ = np.copy(covarianceMatrixJ)
			if weightList is not None:
				c = 0
				for w in weightList:
					I[c] *= w
					J[c] *= w
					c = c + 1
			d = (I - J)
			C = (cI + cJ)/2
			invC = np.linalg.inv(C)
			dInvC = np.dot(d.T, invC)
			f = np.dot(dInvC, d) / 8.0
			(signC, logdetC) = np.linalg.slogdet(C)
			(signcI, logdetcI) = np.linalg.slogdet(cI)
			(signcJ, logdetcJ) = np.linalg.slogdet(cJ)
			s = np.log(signC * np.exp(logdetC) / (np.sqrt(signcI * np.exp(logdetcI)) * np.sqrt(signcJ * np.exp(logdetcJ)))) / 2.0
			B = f + s
			JM = 2 * (1 - np.exp(-B))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			JM = cfg.notAvailable
		return JM
		
	# calculate transformed divergence dij = 2[1 − e^(−dij/8)] from Richards, J. A. & Jia, X. 2006. Remote Sensing Digital Image Analysis: An Introduction, Springer.
	def transformedDivergence(self, signatureArrayI, signatureArrayJ, covarianceMatrixI, covarianceMatrixJ):
		try:
			I = np.array(signatureArrayI)
			J = np.array(signatureArrayJ)
			d = (I - J)
			cI = covarianceMatrixI
			cJ = covarianceMatrixJ
			invCI = np.linalg.inv(cI)
			invCJ = np.linalg.inv(cJ)
			p1 = (cI - cJ) * (invCI - invCJ)
			t1 = 0.5 * np.trace(p1)
			p2 = (invCI + invCJ) * d
			p3 = p2 * d.T
			t2 = 0.5 * np.trace(p3)
			div = t1 + t2
			TD = 2 * (1 - np.exp(-div/8.0))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			TD = cfg.notAvailable
		return TD
		
	# Bray-Curtis similarity (100 - 100 * sum(abs(x[ki]-x[kj]) / (sum(x[ki] + x[kj])))
	def brayCurtisSimilarity(self, signatureArrayI, signatureArrayJ):
		try:
			I = np.array(signatureArrayI)
			J = np.array(signatureArrayJ)
			sumIJ = I.sum() + J.sum()
			d = np.sqrt((I - J)**2)
			sim = 100 - d.sum() / sumIJ * 100
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			sim = cfg.notAvailable
		return sim
			
	# Euclidean distance sqrt(sum((x[ki] - x[kj])^2))
	def euclideanDistance(self, signatureArrayI, signatureArrayJ, weightList = None):
		try:
			I = np.array(signatureArrayI)
			J = np.array(signatureArrayJ)
			if weightList is not None:
				c = 0
				for w in weightList:
					I[c] *= w
					J[c] *= w
					c = c + 1
			d = (I - J)**2
			dist = np.sqrt(d.sum())
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			dist = cfg.notAvailable
		return dist		

	# Spectral angle algorithm [ arccos( sum(r_i * s_i) / sqrt( sum(r_i**2) * sum(s_i**2) ) ) ]
	def spectralAngle(self, signatureArrayI, signatureArrayJ, weightList = None):
		try:
			I = np.array(signatureArrayI)
			J = np.array(signatureArrayJ)
			if weightList is not None:
				c = 0
				for w in weightList:
					I[c] *= w
					J[c] *= w
					c = c + 1
			angle = np.arccos((I * J).sum() / np.sqrt((I**2).sum() * (J**2).sum())) * 180 / np.pi
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			angle = cfg.notAvailable
		return angle
			
	# read all raster from band
	def readAllBandsFromRaster(self, gdalRaster):
		bandNumber = gdalRaster.RasterCount
		bandList = []
		for b in range(1, bandNumber + 1):
			rB = gdalRaster.GetRasterBand(b)
			bandList.append(rB)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return bandList
	
	# process a raster with block size
	def processRaster(self, gdalRaster, gdalBandList, signatureList = None, functionBand = None, functionRaster = None, algorithmName = None, outputRasterList = None, outputAlgorithmRaster = None, outputClassificationRaster = None, previewSize = 0, previewPoint = None, nodataValue = None, macroclassCheck = "No", functionBandArgument = None, functionVariable = None, progressMessage = ""):
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "start processRaster")
			blockSizeX = self.calculateBlockSize(len(gdalBandList))
			blockSizeY = blockSizeX
			# raster blocks
			rX, rY, lX, lY, pX, pY  = self.rasterBlocks(gdalRaster, blockSizeX, blockSizeY, previewSize, previewPoint)
			# set initial value for progress bar
			progresStep = 60 / (len(lX) * len(lY))
			progressStart = 20 - progresStep
			if blockSizeX > rX:
				blockSizeX = rX
			if blockSizeY > rY:
				blockSizeY = rY
			cfg.remainingTime = 0
			remainingBlocks = len(lX) * len(lY)
			totBlocks = remainingBlocks
			for y in lY:
				bSY = blockSizeY
				if previewSize > 0 and bSY > previewSize:
					bSY = previewSize
				if y + bSY > rY:
					bSY = rY - y
				for x in lX:
					if cfg.actionCheck == "Yes":
						# set initial value for progress bar
						progressStart = progressStart + progresStep
						bSX = blockSizeX 
						if previewSize > 0 and bSX > previewSize:
							bSX = previewSize
						if x + bSX > rX:
							bSX = rX - x
						array = np.zeros((bSX, bSY, len(gdalBandList)), dtype=np.float64)
						for b in range(0, len(gdalBandList)):
							ndv = cfg.NoDataVal
							a = self.readArrayBlock(gdalBandList[b], x, y, bSX, bSY)
							try:
								b0 = gdalBandList[b].GetRasterBand(1)
								ndv2 = b0.GetNoDataValue()
							except:
								try:
									ndv2 = gdalBandList[b].GetNoDataValue()
								except:
									ndv2 = None
							if a is not None:
								if functionBandArgument == cfg.multiAddFactorsVar:
									multiAdd = functionVariable[b]
									a = cfg.utls.arrayMultiplicativeAdditiveFactors(a, multiAdd[0], multiAdd[1])
								array[::, ::, b] = a.reshape(bSX, bSY)
							else:
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "error reading array")
								cfg.mx.msgErr46()
								return "No"
							a = None
							# set nodata value
							#noData = gBand2.GetNoDataValue()
							array[::, ::, b][array[::, ::, b] == ndv] = np.nan
							if ndv2 is not None:
								array[::, ::, b][array[::, ::, b] == ndv2] = np.nan
							if functionBand is not None and functionBand != "No":
								qApp.processEvents()
								functionBand(b+1, array[::, ::, b].reshape(bSY, bSX), bSX, bSY, x, y, outputRasterList, functionBandArgument, functionVariable)
								if progressMessage != "No":
									cfg.uiUtls.updateBar(progressStart, " (" + str(totBlocks - remainingBlocks) + "/" + str(totBlocks) + ") " + progressMessage)
						c = array.reshape(bSY, bSX, len(gdalBandList))
						array = None
						if functionRaster is not None:
							if functionBand == "No":
								qApp.processEvents()
								o = functionRaster(gdalBandList, c, bSX, bSY, x, y, outputRasterList, functionBandArgument, functionVariable)
								if progressMessage != "No":
									cfg.uiUtls.updateBar(progressStart, " (" + str(totBlocks - remainingBlocks) + "/" + str(totBlocks) + ") " + progressMessage)
								if o == "No":
									return "No"
							else:
								qApp.processEvents()
								progressMessage = " (" + str(totBlocks - remainingBlocks) + "/" + str(totBlocks) + ") "
								o = functionRaster(gdalBandList, signatureList, algorithmName, c, bSX, bSY, x, y, outputRasterList, outputAlgorithmRaster, outputClassificationRaster, nodataValue, macroclassCheck, previewSize, pX[lX.index(x)], pY[lY.index(y)], progressStart, progresStep, remainingBlocks, progressMessage)
								if o == "No":
									return "No"
						remainingBlocks = (remainingBlocks - 1)
					else:
						return "No"
			outputClassificationRaster = None
			c = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "end processRaster")
			return "Yes"

	# calculate raster
	def calculateRaster(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariable):
		if cfg.actionCheck == "Yes":
			# create function
			f = functionBandArgument.replace(functionVariable, "rasterArray")
			f = f.replace("ln", cfg.logn)
			# perform operation
			o = eval(f)
			oR = outputGdalRasterList[0]
			# output raster
			self.writeArrayBlock(oR, 1, o, pixelStartColumn, pixelStartRow)
			o = None
			oR = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
					
	# reclassify raster
	def reclassifyRaster(self, gdalBand, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariable):
		if cfg.actionCheck == "Yes":
			# raster array
			o = rasterSCPArrayfunctionBand
			for i in functionBandArgument:
				# create condition
				c = i[0].replace(functionVariable, "rasterSCPArrayfunctionBand")
				f = "np.where(" + c + ", " + str(i[1]) + ", o)"
				# perform operation
				try:
					o = eval(f)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			oR = outputGdalRasterList[0]
			# output raster
			self.writeArrayBlock(oR, 1, o, pixelStartColumn, pixelStartRow)
			o = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			
	# band calculation
	def bandCalculation(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):
		if cfg.actionCheck == "Yes":
			f = functionBandArgument
			# create function
			b = 0
			for i in functionVariableList:
				f = f.replace(i[0], " rasterSCPArrayfunctionBand[::, ::," + str(b) + "] ")
				f = f.replace(i[1], " rasterSCPArrayfunctionBand[::, ::," + str(b) + "] ")
				b = b + 1
			# replace numpy operators
			f = cfg.utls.replaceNumpyOperators(f)
			# perform operation
			try:
				o = eval(f)
			except Exception, err:
				cfg.mx.msgErr36()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			# create array if not
			if not isinstance(o, np.ndarray):
				a = np.zeros((rasterSCPArrayfunctionBand.shape[0], rasterSCPArrayfunctionBand.shape[1]), dtype=np.float64)
				a.fill(o)
				o = a
			oR = outputGdalRasterList[0]
			# output raster
			band = gdalBandList[0].GetBand()
			try:
				self.writeArrayBlock(oR, band, o, pixelStartColumn, pixelStartRow)
			except Exception, err:
				cfg.mx.msgErr36()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			
	# multiple where band calculation 
	def bandCalculationMultipleWhere(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):
		if cfg.actionCheck == "Yes":
			for f in functionBandArgument:
				# create function
				b = 0
				for i in functionVariableList:
					f = f.replace(i[0], " rasterSCPArrayfunctionBand[::, ::," + str(b) + "] ")
					f = f.replace(i[1], " rasterSCPArrayfunctionBand[::, ::," + str(b) + "] ")
					b = b + 1
				# replace numpy operators
				f = cfg.utls.replaceNumpyOperators(f)
				# perform operation
				try:
					o = o + eval(f)
				# first iteration
				except:
					try:
						o = eval(f)
					except Exception, err:
						cfg.mx.msgErr36()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						return "No"
			# create array if not
			try:
				if not isinstance(o, np.ndarray):
					o = np.where(o == 0, cfg.NoDataVal, o)
					a = np.zeros((rasterSCPArrayfunctionBand.shape[0], rasterSCPArrayfunctionBand.shape[1]), dtype=np.float64)
					a.fill(o)
					o = a
			except Exception, err:
				cfg.mx.msgErr36()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			oR = outputGdalRasterList[0]
			# output raster
			band = gdalBandList[0].GetBand()
			try:
				self.writeArrayBlock(oR, band, o, pixelStartColumn, pixelStartRow)
			except Exception, err:
				cfg.mx.msgErr36()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
				
	# pan-sharpening
	def pansharpening(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):
		if cfg.actionCheck == "Yes":
			# functionBandArgument = [satellite, panType]
			if functionBandArgument[0] in ['landsat8', 'landsat_8']:
				try:
					# functionVariableList = [bandNumber]
					B = functionVariableList.index(2)
					G = functionVariableList.index(3)
					R = functionVariableList.index(4)
				except Exception, err:
					cfg.mx.msgErr44()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				# Intensity (SCP weights)
				I = (0.42* rasterSCPArrayfunctionBand[:,:,B] + 0.98 * rasterSCPArrayfunctionBand[:,:,G] + 0.6 * rasterSCPArrayfunctionBand[:,:,R] ) / 2
			elif functionBandArgument[0] in ['landsat7', 'landsat_7']:
				try:
					# functionVariableList = [bandNumber]
					B = functionVariableList.index(1)
					G = functionVariableList.index(2)
					R = functionVariableList.index(3)
					NIR = functionVariableList.index(4)
				except Exception, err:
					cfg.mx.msgErr44()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				# Intensity (SCP weights)
				I = (0.42* rasterSCPArrayfunctionBand[:,:,B] + 0.98 * rasterSCPArrayfunctionBand[:,:,G] + 0.6* rasterSCPArrayfunctionBand[:,:,R] + 1* rasterSCPArrayfunctionBand[:,:,NIR]  ) / 3
			if functionBandArgument[1] == cfg.IHS_panType:
				# delta
				d = rasterSCPArrayfunctionBand[:,:,0] - I
			i = 0
			for oR in outputGdalRasterList:
				# process multiband rasters
				i = i + 1
				if functionBandArgument[1] == cfg.IHS_panType:
					o = rasterSCPArrayfunctionBand[:,:,i] + d
				elif functionBandArgument[1] == cfg.BT_panType:
					o = rasterSCPArrayfunctionBand[:,:,i] * rasterSCPArrayfunctionBand[:,:,0] / I	
				# output raster
				try:
					self.writeArrayBlock(oR, 1, o, pixelStartColumn, pixelStartRow)
				except Exception, err:
					cfg.mx.msgErr45()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			I = None
			o = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Pansharpening")
			
	# replace numpy operators for expressions
	def replaceNumpyOperators(self, expression):
		f = expression
		f = f.replace(" ln(", " " + cfg.logn + "(")
		f = f.replace(" ln (", " " + cfg.logn + "(")
		f = f.replace(" sqrt(", " " + cfg.numpySqrt + "(")
		f = f.replace(" sqrt (", " " + cfg.numpySqrt + "(")
		f = f.replace(" cos(", " " + cfg.numpyCos+ "(")
		f = f.replace(" cos (", " " + cfg.numpyCos + "(")
		f = f.replace(" acos(", " " + cfg.numpyArcCos + "(")
		f = f.replace(" acos (", " " + cfg.numpyArcCos + "(")
		f = f.replace(" sin(", " " + cfg.numpySin + "(")
		f = f.replace(" sin (", " " + cfg.numpySin + "(")
		f = f.replace(" asin(", " " + cfg.numpyArcSin + "(")
		f = f.replace(" asin (", " " + cfg.numpyArcSin + "(")
		f = f.replace(" tan(", " " + cfg.numpyTan + "(")
		f = f.replace(" tan (", " " + cfg.numpyTan + "(")
		f = f.replace(" atan(", " " + cfg.numpyArcTan + "(")
		f = f.replace(" atan (", " " + cfg.numpyArcTan + "(")
		f = f.replace(" exp(", " " + cfg.numpyExp + "(")
		f = f.replace(" exp (", " " + cfg.numpyExp + "(")
		f = f.replace("^", "**")
		f = f.replace(" pi ", " " + cfg.numpyPi + " ")
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return f
			
	# calculate raster unique values
	def rasterUniqueValues(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			val = np.unique(rasterArray)
			# remove multiple nan
			val = np.unique(val[~np.isnan(val)])
			cfg.rasterBandUniqueVal = np.append(cfg.rasterBandUniqueVal, [val], axis =1)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			return cfg.rasterBandUniqueVal
			
	# count pixels in a raster lower than value
	def rasterValueCount(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			sum = ((rasterArray <= functionVariable) & (rasterArray != functionBandArgumentNoData)).sum()
			cfg.rasterBandPixelCount = cfg.rasterBandPixelCount + sum
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			return cfg.rasterBandPixelCount
						
	# count pixels in a raster equal to value
	def rasterEqualValueCount(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			sum = (rasterArray == functionVariable).sum()
			cfg.rasterBandPixelCount = cfg.rasterBandPixelCount + sum
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			return cfg.rasterBandPixelCount
			
	# calculate raster unique values (slow)
	def rasterUniqueValuesWithSum(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			val = np.unique(rasterArray).tolist()
			for i in val:
				if i != functionBandArgumentNoData:
					sum = (rasterArray == i).sum()
					index = np.where(cfg.rasterBandUniqueVal[1,:] == i)
					if index[0].size > 0:
						oldVal = cfg.rasterBandUniqueVal[0,index[0]]
						newValue = oldVal + sum
						cfg.rasterBandUniqueVal[0, index[0]] = newValue
					else:
						cfg.rasterBandUniqueVal = np.append(cfg.rasterBandUniqueVal, [[sum], [ i]], axis =1)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			return cfg.rasterBandUniqueVal
			
	# get IDs of signature list dictionari
	def signatureID(self):
		i = 1
		if len(cfg.signIDs.values()) > 0:
			while i in cfg.signIDs.values():
				i = i + 1
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID" + str(i))
		return i
		
	def calculateUnique_CID_MCID(self):
		unique = []
		if len(cfg.signIDs.values()) > 0:
			for i in cfg.signIDs.values():
				unique.append(str(cfg.signList["CLASSID_" + str(i)]) + "-" + str(cfg.signList["MACROCLASSID_" + str(i)]))
			l = set(unique)
			list = cfg.utls.uniqueToOrderedList(l)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " unique" + str(list))
			return list
		else:
			return "No"
			
	def uniqueToOrderedList(self, uniqueList):
		list = []
		for i in uniqueList:
			v = i.split("-")
			list.append([int(v[0]), int(v[1])])
		sortedList = sorted(list, key=lambda list: (list[0], list[1]))
		return sortedList
		
		
	# highlight row in table
	def highlightRowInTable(self, table, value, columnIndex):
		tW = table
		v = tW.rowCount()
		for x in range(0, v):
			id = tW.item(x, columnIndex).text()
			if str(id) == str(value):
				return x
			
	# remove rows from table
	def removeRowsFromTable(self, table):
		# ask for confirm
		a = cfg.utls.questionBox("Remove rows", "Are you sure you want to remove highlighted rows from the table?")
		if a == "Yes":
			tW = table
			c = tW.rowCount()
			# list of item to remove
			iR  = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			v = list(set(iR))
			# remove items
			for i in reversed(range(0, len(v))):
				tW.removeRow(v[i])
			c = tW.rowCount()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " row removed")
			
	# calculate block size
	def calculateBlockSize(self, bandNumber):
		if cfg.sys64bit == "No" and cfg.sysNm == "Windows":
			mem = 512
		else:
			mem = cfg.RAMValue
		b = int((mem / (cfg.arrayUnitMemory * (bandNumber +  5) ))**.5)
		# set system memory max
		if cfg.sys64bit == "No" and b > 2500:
			b = 2500
		# check memory
		try:
			a = np.zeros((b,b), dtype = np.float64)
			cfg.uiUtls.updateBar(20,  QApplication.translate("semiautomaticclassificationplugin", "Please wait ..."))
		except:
			for i in reversed(range(128, mem, int(mem/10))):
				try:
					b = int((i / (cfg.arrayUnitMemory * (bandNumber +  5) ))**.5)
					# set system memory max
					if cfg.sys64bit == "No" and b > 2500:
						b = 2500
					a = np.zeros((int(b),int(b)), dtype = np.float64)
					size = a.nbytes / 1048576
					cfg.ui.RAM_spinBox.setValue(size * bandNumber)
					cfg.mx.msgWar11()
					cfg.uiUtls.updateBar(20,  QApplication.translate("semiautomaticclassificationplugin", "Please wait ..."))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "block = " + str(b))
					return b
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "block = " + str(b))
		return b
		
	# get random color and complementary color
	def randomColor(self):
		import random
		r = random.randint(0,255)
		g = random.randint(0,255)
		b = random.randint(0,255)
		c = QColor(r, g, b)
		cc = QColor(255 - r, 255 - r, 225 - r)
		return c, cc
		
	# select color
	def selectColor(self):
		c = QColorDialog.getColor()
		if c.isValid():
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "color")
			return c
	
	# Define raster symbology
	def rasterSymbolGeneric(self, rasterLayer, zeroValue = "Unchanged"):
		rasterLayer.setDrawingStyle("SingleBandPseudoColor")
		# The band of classLayer
		classLyrBnd = 1
		# Band statistics
		bndStat = rasterLayer.dataProvider().bandStatistics(1)
		classMax = bndStat.maximumValue
		# Color list for ramp
		clrLst = [ QgsColorRampShader.ColorRampItem(0, QColor(0,0,0), zeroValue), QgsColorRampShader.ColorRampItem(1, QColor(0,0,255), "1"), QgsColorRampShader.ColorRampItem(round(classMax/2), QColor(255,0,0), str(round(classMax/2))), QgsColorRampShader.ColorRampItem(classMax, QColor(0,255,0), str(classMax)) ]
		# Create the shader
		lyrShdr = QgsRasterShader()
		# Create the color ramp function
		clrFnctn = QgsColorRampShader()
		clrFnctn.setColorRampType(QgsColorRampShader.INTERPOLATED)
		clrFnctn.setColorRampItemList(clrLst)
		# Set the raster shader function
		lyrShdr.setRasterShaderFunction(clrFnctn)
		# Create the renderer
		lyrRndr = QgsSingleBandPseudoColorRenderer(rasterLayer.dataProvider(), classLyrBnd, lyrShdr)
		# Apply the renderer to rasterLayer
		rasterLayer.setRenderer(lyrRndr)
		# refresh legend
		if hasattr(rasterLayer, "setCacheImage"):
			rasterLayer.setCacheImage(None)
		rasterLayer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(rasterLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "symbology")
			
	# read project variable
	def readProjectVariable(self, variableName, value):
		p = QgsProject.instance()
		v = p.readEntry("SemiAutomaticClassificationPlugin", variableName, value)[0]
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "variable: " + unicode(variableName) + " - value: " + unicode(value))
		return v
		
	# read QGIS path project variable
	def readQGISVariablePath(self):
		cfg.projPath = QgsProject.instance().fileName()
		p = QgsProject.instance()
		v = p.readEntry("Paths", "Absolute", "")[0]
		cfg.absolutePath = v
		
	def qgisAbsolutePathToRelativePath(self, absolutePath, relativePath):
		p = QgsApplication.absolutePathToRelativePath(absolutePath, relativePath)
		return p
		
	def qgisRelativePathToAbsolutePath(self, relativePath, absolutePath):
		p = QgsApplication.relativePathToAbsolutePath(relativePath, absolutePath)
		return p
		
### Remove layer from map
	def removeLayer(self, layerName):
		QgsMapLayerRegistry.instance().removeMapLayer(self.layerID(layerName))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer: " + unicode(layerName))
		
### Create group
	def createGroup(self, groupName):
		g = cfg.lgnd.addGroup(groupName, False)
		cfg.utls.moveGroup(groupName)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group: " + unicode(groupName))
		return g		
	
### Move group to top layers
	def moveGroup(self, groupName):
		# QGIS >= 2.4
		try:
			p = QgsProject.instance()
			root = p.layerTreeRoot()
			g = root.findGroup(groupName)
			cG = g.clone()
			root.insertChildNode(0, cG)
			root.removeChildNode(g)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group: " + unicode(groupName))
		# QGIS < 2.4
		except Exception, err:
			if "layerTreeRoot" not in str(err):
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
### Move layer to top layers
	def moveLayerTop(self, layer):
		# QGIS >= 2.4
		try:
			p = QgsProject.instance()
			root = p.layerTreeRoot()
			g = root.findLayer(layer.id())
			cG = g.clone()
			root.insertChildNode(0, cG)
			root.removeChildNode(g)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer: " + unicode(layer.name()))
		# QGIS < 2.4
		except Exception, err:
			if "layerTreeRoot" not in str(err):
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
### Select layer by name thereof
	def selectLayerbyName(self, layerName, filterRaster=None):
	 	ls = cfg.lgnd.layers()
		for l in ls:
			lN = l.name()
			if lN == layerName:
				if filterRaster is None:
					return l
				else:
					if l.type() == 1:
						return l
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer selected: " + unicode(layerName))

### copy raster with GDAL
	def GDALCopyRaster(self, input, output, outFormat = "GTiff", compress = "No", compressFormat = "DEFLATE"):
		if compress == "No":
			op = " -of " + outFormat
		else:
			op = " -co COMPRESS=" + compressFormat + " -of " + outFormat
		try:
			cfg.utls.getGDALForMac()
			gD = "gdal_translate"
			a = cfg.gdalPath + gD + op 
			b = '"' + input + '" '
			c = '"' + output + '" '
			d = a + " " + b + " " + c
			sP = subprocess.Popen(d, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error:: " + str(err) )
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.utls.getGDALForMac()
			gD = "gdal_translate"
			a = cfg.gdalPath + gD + op 
			b = '"' + input + '" '
			c = '"' + output + '" '
			d = a + " " + b + " " + c
			sP = subprocess.Popen(d, shell=True)
			sP.wait()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image: " + unicode(output))
			
### Merge raster bands
	def mergeRasterBands(self, bandList, output, outFormat = "GTiff", compress = "No"):
		if compress == "No":
			op = "-of " + outFormat
		else:
			op = "-co COMPRESS=LZW -of " + outFormat
		input = ""
		for b in bandList:
			input = input + '"' + b.encode(sys.getfilesystemencoding()) + '" '
		input = input
		try:
			cfg.utls.getGDALForMac()
			if cfg.sysNm == "Windows":
				gD = "gdal_merge.bat"
			else:
				gD = "gdal_merge.py"
			a = cfg.gdalPath + gD + ' -separate ' + op + ' -o '
			b = '"' + output.encode(sys.getfilesystemencoding()) + '" '
			c = input
			d = a + b + c
			sP = subprocess.Popen(d, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error:: " + str(err) )
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.utls.getGDALForMac()
			if cfg.sysNm == "Windows":
				gD = "gdal_merge.bat"
			else:
				gD = "gdal_merge.py"
			a = cfg.gdalPath + gD + ' -separate ' + op + ' -o '
			b = '"' + output.encode(sys.getfilesystemencoding()) + '" '
			c = input
			d = a + b + c
			sP = subprocess.Popen(d, shell=True)
			sP.wait()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image: " + unicode(output))
			
### Subset an image, given an origin point and a subset width
	def subsetImage(self, imageName, XCoord, YCoord, Width, Height, output, outFormat = "GTiff", virtual = "No"):
		i = self.selectLayerbyName(imageName, "Yes")
		# output variable
		st = "Yes"
		if i is not None:
			bandNumberList = []
			for bb in range(1, i.bandCount()+1):
				bandNumberList.append(bb)
			i = i.source().encode(sys.getfilesystemencoding())
			st = "No"
			# raster top left origin and pixel size
			tLX, tLY, lRX, lRY, pS = self.imageInformationSize(imageName)
			if pS is None:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image none or missing")
			else:		
				try:
					dType = self.getRasterDataTypeName(i)
					# subset origin
					UX = tLX + abs(int((tLX - XCoord) / pS )) * pS - (Width -1 )/ 2 * pS
					UY = tLY - abs(int((tLY - YCoord) / pS )) * pS + (Height -1 )/ 2 * pS
					LX = UX + Width * pS
					LY = UY - Height * pS
					dT = cfg.utls.getTime()
					tPMN = cfg.tmpVrtNm + ".vrt"
					tPMD = cfg.tmpDir + "/" + dT + tPMN
					bList = [i]
					if virtual == "No":
						st = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", cfg.NoDataVal, 0, "No", "Yes", [float(UX), float(UY), float(LX), float(LY)])
						clipOutput = cfg.utls.copyRaster(tPMD, output, str(outFormat), cfg.NoDataVal)
						st = clipOutput
					else:
						st = cfg.utls.createVirtualRaster2(bList, output, bandNumberList, "Yes", cfg.NoDataVal, 0, "No", "Yes", [float(UX), float(UY), float(LX), float(LY)])
				# in case of errors
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					st = "Yes"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "image: " + unicode(imageName) + " subset origin: (" + str(XCoord) + ","+ str(YCoord) + ") width: " + str(Width))
		return st
			
### convert reference layer to raster based on the resolution of a raster
	def vectorToRaster(self, fieldName, layerPath, referenceRasterName, outputRaster, referenceRasterPath=None, ALL_TOUCHED=None, outFormat = "GTiff", burnValues = None):
		# register drivers
		#gdal.AllRegister()
		if referenceRasterPath is None:
			# band set
			if cfg.bndSetPresent == "Yes" and referenceRasterName == cfg.bndSetNm:
				referenceRasterName = cfg.bndSet[0]
				# input
				r = self.selectLayerbyName(referenceRasterName, "Yes")
			else:
				if self.selectLayerbyName(referenceRasterName, "Yes") is None:
					cfg.mx.msg4()
					cfg.ipt.refreshRasterLayer()
				else:
					# input
					r = self.selectLayerbyName(referenceRasterName, "Yes")
			try:
				rS = r.source()
				ck = "Yes"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				ck = "No"
				cfg.mx.msg4()
				return ck
		else:
			rS = referenceRasterPath
		try:
			# open input with GDAL
			rD = gdal.Open(rS, GA_ReadOnly)
			# number of x pixels
			rC = rD.RasterXSize
			# number of y pixels
			rR = rD.RasterYSize
			# check projections
			rP = rD.GetProjection()
			# pixel size and origin
			rGT = rD.GetGeoTransform()
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg4()
			return "No"
		l = ogr.Open(layerPath)
		gL = l.GetLayer()
		# check projection
		lP = osr.SpatialReference()
		lP = gL.GetSpatialRef()
		lP.AutoIdentifyEPSG()
		lPRS = lP.GetAuthorityCode(None)
		rPSys =osr.SpatialReference(wkt=rP)
		rPSys.AutoIdentifyEPSG()
		rPRS = rPSys.GetAuthorityCode(None)
		if lP != "":
			if lPRS == None:
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "lP: " + unicode(lP) + "rPRS: " + unicode(rPRS))
			minX, maxX, minY, maxY = gL.GetExtent()
			origX = rGT[0] +  rGT[1] * abs(int(round((minX - rGT[0]) / rGT[1])))
			origY = rGT[3] + rGT[5] * abs(int(round((maxY - rGT[3]) / rGT[5])))
			rC = abs(int(round((maxX - minX) / rGT[1])))
			rR = abs(int(round((maxY - minY) / rGT[5])))
			tD = gdal.GetDriverByName(outFormat)
			oR = tD.Create(outputRaster, rC, rR, 1, GDT_Int32)
			try:
				oRB = oR.GetRasterBand(1)
			# in case of errors
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msgErr34()
				return "No"
			# set raster projection from reference
			oR.SetGeoTransform( [ origX , rGT[1] , 0 , origY , 0 , rGT[5] ] )
			oR.SetProjection(rP)
			oRB.SetNoDataValue(cfg.NoDataVal)
			m = np.zeros((rR, rC), dtype='int32')
			m.fill(cfg.NoDataVal)
			oRB.WriteArray(m, 0, 0)
			oRB.FlushCache()
			# convert reference layer to raster
			if ALL_TOUCHED is None:
				if burnValues is None:
					oC = gdal.RasterizeLayer(oR, [1], gL, options = ["ATTRIBUTE=" + str(fieldName)])
				else:
					oC = gdal.RasterizeLayer(oR, [1], gL, burn_values=[burnValues])
			else:
				if burnValues is None:
					oC = gdal.RasterizeLayer(oR, [1], gL, options = ["ATTRIBUTE=" + str(fieldName), "ALL_TOUCHED=TRUE"])
				else:
					oC = gdal.RasterizeLayer(oR, [1], gL, burn_values=[burnValues], options = ["ALL_TOUCHED=TRUE"])
			# close bands
			oRB = None
			# close rasters
			oR = None
			rD = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "vector to raster check: " + unicode(oC))
		else:
			cfg.mx.msg9()
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "lP: " + unicode(lP) + "rPRS: " + unicode(rPRS))
			return "No"
			
	# convert raster to shapefile
	def rasterToVector(self, rasterPath, outputShapefilePath, fieldName = "No"):
		#gdal.AllRegister()
		tD = gdal.GetDriverByName( "GTiff" )
		# open input with GDAL
		try:
			rD = gdal.Open(rasterPath, GA_ReadOnly)
			# number of x pixels
			rC = rD.RasterXSize
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		# create a shapefile
		d = ogr.GetDriverByName('ESRI Shapefile')
		dS = d.CreateDataSource(outputShapefilePath)
		if dS is None:
			# close rasters
			rD = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " failed: " + unicode(outputShapefilePath))
		else:
			# shapefile
			sR = osr.SpatialReference()
			sR.ImportFromWkt(rD.GetProjectionRef())
			rL = dS.CreateLayer(os.path.basename(rasterPath).encode(sys.getfilesystemencoding()), sR, ogr.wkbPolygon)
			if fieldName == "No":
				fN = str(cfg.fldID_class)
			else:
				fN = fieldName
			fd = ogr.FieldDefn(fN, ogr.OFTInteger)
			rL.CreateField(fd)
			fld = rL.GetLayerDefn().GetFieldIndex(fN)
			rRB = rD.GetRasterBand(1)
			# raster to polygon
			gdal.Polygonize(rRB, rRB.GetMaskBand(), rL, fld)		
			# close rasters and shapefile
			rRB = None
			rD = None			
			dS = None							
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " vector output performed")

	# set RGB color composite
	def setRGBColorComposite(self):
		if cfg.rgb_combo.currentText() != "-":
			try:
				rgb = cfg.rgb_combo.currentText()
				check = self.createRGBColorComposite(rgb)
				if check == "Yes":
					listA = cfg.utls.getAllItemsInCombobox(cfg.rgb_combo)
					cfg.RGBList = sorted(list(set(listA)))
					cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
					return "Yes"
				else:
					int(check)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				id = cfg.rgb_combo.findText(cfg.rgb_combo.currentText())
				cfg.rgb_combo.removeItem(id)
	
	# create RGB color composite
	def createRGBColorComposite(self, colorComposite):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			# if bandset create temporary virtual raster
			tPMN = cfg.tmpVrtNm + ".vrt"
			if cfg.tmpVrt is None:
				try:
					self.removeLayer(tPMN)
				except:
					pass
				# date time for temp name
				dT = cfg.utls.getTime()
				tPMD = cfg.tmpDir + "/" + dT + tPMN
				vrtCheck = cfg.utls.createVirtualRaster(cfg.bndSetLst, tPMD)
				time.sleep(1)
				i = self.addRasterLayer(tPMD, tPMN)
				cfg.utls.setRasterColorComposite(i, 3, 2, 1)
				cfg.tmpVrt = i
			else:
				i = cfg.utls.selectLayerbyName(tPMN, "Yes")
			c = str(colorComposite).split(",")
			if len(c) == 1:
				c = str(colorComposite).split("-")
			if len(c) == 1:
				c = str(colorComposite).split(";")
			if len(c) == 1:
				c = str(colorComposite)
			if i is not None:
				b = len(cfg.bndSet)
				if int(c[0]) <= b and int(c[1]) <= b and int(c[2]) <= b:
					cfg.utls.setRasterColorComposite(i, int(c[0]), int(c[1]), int(c[2]))
					return "Yes"
				else:
					return "No"
			else:
				cfg.tmpVrt = None
		else:
			c = str(colorComposite).split(",")
			if len(c) == 1:
				c = str(colorComposite).split("-")
			if len(c) == 1:
				c = str(colorComposite).split(";")
			if len(c) == 1:
				c = str(colorComposite)
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
			if i is not None:
				b = len(cfg.bndSet)
				if int(c[0]) <= b and int(c[1]) <= b and int(c[2]) <= b:
					self.setRasterColorComposite(i, int(c[0]), int(c[1]), int(c[2]))
					return "Yes"
				else:
					return "No"
					
	def setMapExtentFromLayer(self, layer):
		ext = layer.extent()
		tLPoint = QgsPoint(ext.xMinimum(), ext.yMaximum())
		lRPoint = QgsPoint(ext.xMaximum(), ext.yMinimum())
		point1 = tLPoint
		point2 = lRPoint
		# project extent
		iCrs = cfg.utls.getCrs(layer)
		pCrs = cfg.utls.getQGISCrs()
		if iCrs is None:
			iCrs = pCrs
		# projection of input point from raster's crs to project's crs
		if pCrs != iCrs:
			try:
				point1 = cfg.utls.projectPointCoordinates(tLPoint, iCrs, pCrs)
				point2 = cfg.utls.projectPointCoordinates(lRPoint, iCrs, pCrs)
				if point1 is False:
					point1 = tLPoint
					point2 = lRPoint
			# Error latitude or longitude exceeded limits
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				point1 = tLPoint
				point2 = lRPoint
		cfg.cnvs.setExtent(QgsRectangle(point1, point2))
	
	# show hide input image
	def showHideInputImage(self):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			i = cfg.tmpVrt
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
		try:
			if i is not None:
				if cfg.inputImageRadio.isChecked():
					cfg.lgnd.setLayerVisible(i, True)
					cfg.utls.moveLayerTop(i)
				else:
					cfg.lgnd.setLayerVisible(i, False)
		except:
			pass

	# set raster color composite
	def setRasterColorComposite(self, raster, RedBandNumber, GreenBandNumber, BlueBandNumber):
		raster.setDrawingStyle('MultiBandColor')
		raster.renderer().setRedBand(RedBandNumber)
		raster.renderer().setGreenBand(GreenBandNumber)
		raster.renderer().setBlueBand(BlueBandNumber)
		cfg.utls.setRasterContrastEnhancement(raster, cfg.defaultContrast )
		
	# set local cumulative cut stretch
	def setRasterCumulativeStretch(self):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			i = cfg.tmpVrt
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
		cfg.utls.setRasterContrastEnhancement(i, cfg.cumulativeCutContrast)
		cfg.defaultContrast = cfg.cumulativeCutContrast
				
	# set local standard deviation stretch
	def setRasterStdDevStretch(self):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			i = cfg.tmpVrt
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
		cfg.utls.setRasterContrastEnhancement(i, cfg.stdDevContrast)
		cfg.defaultContrast = cfg.stdDevContrast
		
	# set raster enhancement
	def setRasterContrastEnhancement(self, QGISraster, contrastType = cfg.cumulativeCutContrast):
		ext = cfg.cnvs.extent( )
		tLPoint = QgsPoint(ext.xMinimum(), ext.yMaximum())
		lRPoint = QgsPoint(ext.xMaximum(), ext.yMinimum())
		point1 = tLPoint
		point2 = lRPoint
		# project extent
		iCrs = cfg.utls.getCrs(QGISraster)
		pCrs = cfg.utls.getQGISCrs()
		if iCrs is None:
			iCrs = pCrs
		# projection of input point from project's crs to raster's crs
		if pCrs != iCrs:
			try:
				point1 = cfg.utls.projectPointCoordinates(tLPoint, pCrs, iCrs)
				point2 = cfg.utls.projectPointCoordinates(lRPoint, pCrs, iCrs)
				if point1 is False:
					point1 = tLPoint
					point2 = lRPoint
			# Error latitude or longitude exceeded limits
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				point1 = tLPoint
				point2 = lRPoint
		if contrastType == cfg.stdDevContrast:
			contrast = QgsRaster.ContrastEnhancementStdDev
		elif contrastType == cfg.cumulativeCutContrast:
			contrast = QgsRaster.ContrastEnhancementCumulativeCut
		try:
			QGISraster.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, contrast, QgsRectangle(point1, point2))
			QGISraster.triggerRepaint()
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	def getAllItemsInCombobox(self, combobox):
		it = [combobox.itemText(i) for i in range(combobox.count())]
		return it
		
	def setComboboxItems(self, combobox, itemList):
		combobox.clear()
		for i in itemList:
			if len(i) > 0:
				combobox.addItem(i)

	# check band set and create band set list
	def checkBandSet(self):
		ck = "Yes"
		# list of bands for algorithm
		cfg.bndSetLst = []
		for x in range(0, len(cfg.bndSet)):
			b = cfg.utls.selectLayerbyName(cfg.bndSet[x], "Yes")
			if b is not None:
				cfg.bndSetLst.append(b.source())
			else:
				ck = "No"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster is not loaded: " + unicode(cfg.bndSet[x]))
				return ck
		return ck
			
	# write project variable
	def writeProjectVariable(self, variableName, value):
		p = QgsProject.instance()
		p.writeEntry("SemiAutomaticClassificationPlugin", variableName, value)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "variable: " + unicode(variableName) + " - value: " + unicode(value))
		
### Delete a feauture from a shapefile by its Id
	def deleteFeatureShapefile(self, layer, feautureIds):
		layer.startEditing()				
		res = layer.dataProvider().deleteFeatures(feautureIds)
		layer.commitChanges()
		res2 = layer.dataProvider().createSpatialIndex()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feauture deleted: " + unicode(layer) + " " + str(feautureIds) )

### Edit a feauture in a shapefile by its Id
	def editFeatureShapefile(self, layer, feautureId, fieldName, value):
		id = self.fieldID(layer, fieldName)
		layer.startEditing()				
		res = layer.changeAttributeValue(feautureId, id, value)
		layer.commitChanges()
		res2 = layer.dataProvider().createSpatialIndex()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feauture edited: " + unicode(layer) + " " + str(feautureId) )
		
	# calculate random points
	def randomPoints(self, pointNumber, Xmin, Xmax, Ymin, Ymax, minDistance = None):
		XCoords = np.random.uniform(Xmin,Xmax,pointNumber).reshape(pointNumber, 1)
		YCoords = np.random.uniform(Ymin,Ymax,pointNumber).reshape(pointNumber, 1)
		points = np.hstack((XCoords,YCoords))
		if minDistance is not None:
			for i in range(0, pointNumber):
				distance = cdist(points, points)
				if i < distance.shape[0]:
					index = np.where((distance[i,:] <= minDistance)  & (distance[i,:] > 0))
					points = np.delete(points, index, 0)
		return points
		
	# save a qml style
	def saveQmlStyle(self, layer, stylePath):
		layer.saveNamedStyle(stylePath)
		
	""" tab selection """
### tab 0
	# select roi tools tab
	def roiToolsTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")

	# select multiple roi tab
	def mutlipleROITab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		cfg.ui.tabWidget.setCurrentIndex(0)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# scatter plot tab
	def importUSGSLibraryTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		cfg.ui.tabWidget.setCurrentIndex(1)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# algorithm weight tab
	def algorithmWeighTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		cfg.ui.tabWidget.setCurrentIndex(2)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# signature threshold tab
	def algorithmThresholdTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		cfg.ui.tabWidget.setCurrentIndex(3)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# download Landsat tab
	def downloadLandast8Tab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		cfg.ui.tabWidget.setCurrentIndex(4)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# download Sentinel tab
	def downloadSentinelTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		cfg.ui.tabWidget.setCurrentIndex(5)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")

### tab 1
	# select pre processing tab
	def preProcessingTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(1)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select Clip multiple rasters tab
	def clipMultipleRastersTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(1)
		cfg.ui.tabWidget_preprocessing.setCurrentIndex(1)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select Landsat tab
	def landsatTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(1)
		cfg.ui.tabWidget_preprocessing.setCurrentIndex(0)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select Split raster bands tab
	def splitrasterbandsTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(1)
		cfg.ui.tabWidget_preprocessing.setCurrentIndex(2)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
### tab 2
	# select post processing tab
	def postProcessingTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(2)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select Accuracy tab
	def accuracyTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(2)
		cfg.ui.tabWidget_2.setCurrentIndex(0)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select Land cover change tab
	def landCoverChangeTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(2)
		cfg.ui.tabWidget_2.setCurrentIndex(1)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select Classification report tab
	def classificationReportTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(2)
		cfg.ui.tabWidget_2.setCurrentIndex(2)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select Classification report tab
	def classToVectorTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(2)
		cfg.ui.tabWidget_2.setCurrentIndex(3)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
	
	# select reclassification tab
	def reclassificationTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(2)
		cfg.ui.tabWidget_2.setCurrentIndex(4)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
### tab 3
	# select Band calc tab
	def bandCalcTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(3)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
	
### tab 4
	# select band set tab
	def bandSetTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(4)
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
	
### tab 5	
	# select settings tab
	def settingsTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(5)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select settings interface tab
	def settingsInterfaceTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(5)
		cfg.ui.toolBox.setCurrentIndex(0)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select settings Processing tab
	def settingsProcessingTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(5)
		cfg.ui.toolBox.setCurrentIndex(1)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select settings debug tab
	def settingsDebugTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(5)
		cfg.ui.toolBox.setCurrentIndex(2)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")

### tab 6
	# select bout tab
	def aboutTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(6)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# spectral singature plot tab
	def spectralPlotTab(self):
		cfg.spectralplotdlg.close()
		cfg.spectralplotdlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")

	# scatter plot tab
	def scatterPlotTab(self):
		cfg.scatterplotdlg.close()
		cfg.scatterplotdlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# beep sound
	def beepSound(self, frequency, duration):
		if sys.platform.startswith('win'):
			winsound.Beep(frequency, int(duration * 1000))
		elif sys.platform.startswith('linux'):
			os.system("play --no-show-progress --null --channels 1 synth " + str(duration) + " sine " + str(frequency))
		else:
			sys.stdout.write('\a')
			sys.stdout.flush()
	
	# finish sound
	def finishSound(self):
		try:
			self.beepSound(800, 0.2)
			self.beepSound(600, 0.3)
			self.beepSound(700, 0.5)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	def sortTableColumn(self, table, column, ascending = False):
		table.sortItems(column, ascending)
	
	# refresh classification combo
	def refreshClassificationLayer(self):
		ls = cfg.lgnd.layers()
		cfg.ui.classification_name_combo.clear()
		cfg.ui.classification_report_name_combo.clear()
		cfg.ui.classification_vector_name_combo.clear()
		cfg.ui.reclassification_name_combo.clear()
		cfg.ui.raster_extent_combo.clear()
		# classification name
		self.clssfctnNm = None
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				cfg.dlg.raster_extent_combo(l.name())
				if l.bandCount() == 1:
					cfg.dlg.classification_layer_combo(l.name())
					cfg.dlg.classification_report_combo(l.name())
					cfg.dlg.classification_to_vector_combo(l.name())
					cfg.dlg.reclassification_combo(l.name())
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification layers refreshed")
	
### Zoom to selected feature of layer
	def zoomToSelected(self, layer, featureID):
		layer.removeSelection()
		layer.select(featureID)
		cfg.cnvs.zoomToSelected(layer)
		layer.deselect(featureID)
		
""" deprecated

### Delete a feauture from a shapefile by its Id
	def deleteFeatureShapefileOGR(self, layerPath, feautureId):
		d = ogr.GetDriverByName("ESRI Shapefile")
		dr = d.Open(layerPath, 1)
		l = dr.GetLayer()
		l.DeleteFeature(feautureId)
		dr.ExecuteSQL("REPACK " + l.GetName())
		dr = None
		dr = d.Open(layerPath, 1)
		l = dr.GetLayer()
		dr.ExecuteSQL("REPACK " + l.GetName())
		dr = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feauture deleted: " + str(layerPath) + " " + str(feautureId) )
		
### Edit a feauture in a shapefile by its Id
	def editFeatureShapefileOGR(self, layerPath, feautureId, fieldName, value):
		d = ogr.GetDriverByName("ESRI Shapefile")
		dr = d.Open(layerPath, 1)
		l = dr.GetLayer()
		f = l.GetFeature(feautureId)
		i = f.GetFieldIndex(fieldName)
		f.SetField(i, value)
		l.SetFeature(f)
		dr = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feauture edited: " + unicode(layerPath) + " " + str(feautureId) )
		
	#clip a raster using a shapefile
	def clipRasterByShapefile(self,  shapefile, raster, outputRaster = None, outFormat = "GTiff"):
		dT = self.getTime()
		if outputRaster is None:
			###temp files
			tRN = cfg.copyTmpROI + dT + ".tif"
			tR = str(cfg.tmpDir + "//" + tRN)
		else:
			tR = str(outputRaster)
		try:
			dType = self.getRasterDataTypeName(raster)
			cfg.utls.getGDALForMac()
			sP = subprocess.Popen(cfg.gdalPath + "gdalwarp -ot " + dType + " -dstnodata " + str(cfg.NoDataVal) + " -cutline \"" + unicode(shapefile) + "\" -crop_to_cutline -of "  + outFormat + " " + unicode(raster) + " " + str(tR) , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			sP.wait()
			###get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				###logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error:: " + str(err) )
		###in case of errors
		except Exception, err:	
			###logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.utls.getGDALForMac()
			sP = subprocess.Popen(cfg.gdalPath + "gdalwarp -ot " + dType + " -dstnodata " + str(cfg.NoDataVal) + " -cutline \"" + unicode(shapefile) + "\" -crop_to_cutline -of "  + outFormat + " " + unicode(raster) + " " + str(tR) , shell=True)
			sP.wait()
		if os.path.isfile(tR) is False:
		###if shapefile is too small try to convert to raster then to polygon
			tRNxs = cfg.copyTmpROI + dT + "xs.tif"
			tRxs = str(cfg.tmpDir + "//" + tRNxs)
			tSHPxs = cfg.copyTmpROI + dT + "xs.shp"
			tSxs = str(cfg.tmpDir + "//" + tSHPxs)
			self.vectorToRaster(cfg.emptyFN, unicode(shapefile), cfg.emptyFN, tRxs, unicode(raster), "Yes", outFormat)
			self.rasterToVector(tRxs, tSxs)
			try:
				dType = self.getRasterDataTypeName(raster)
				cfg.utls.getGDALForMac()
				sP = subprocess.Popen(cfg.gdalPath + "gdalwarp -ot " + dType + " -dstnodata " + str(cfg.NoDataVal) + " -cutline \"" + tSxs + "\" -crop_to_cutline -of GTiff " + unicode(raster) + " " + str(tR) , shell=True)
				sP.wait()
			###in case of errors
			except Exception, err:
				###logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.utls.getGDALForMac()
				try:
					cfg.utls.getGDALForMac()
					sP = subprocess.Popen(cfg.gdalPath + "gdalwarp -ot " + dType + " -dstnodata " + str(cfg.NoDataVal) + " -cutline \"" + tSxs + "\" -crop_to_cutline -of GTiff " + unicode(raster) + " " + str(tR) , shell=True)
					sP.wait()
				###in case of errors
				except Exception, err:
					###logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		###logger
		cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "sP " + unicode(sP) + "shapefile " + unicode(shapefile) + "raster " + unicode(raster) + "tR " + unicode(tR))
		return tR
		
"""