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
import sys
import subprocess
import inspect
import time
import datetime
import numpy as np
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
			i = cfg.utls.selectLayerbyName(cfg.rstrNm)
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), " fields added")
		
### Add layer to map
	def addLayerToMap(self, layer):
		QgsMapLayerRegistry.instance().addMapLayers([layer])
		
### Add layer
	def addVectorLayer(self, path, name, format):
		l = QgsVectorLayer(path, name, format)
		return l
		
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
				if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), " cancelled")
		
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
	
### check if the clicked point is inside the image
	def checkPointImage(self, imageName, point):
		# band set
		if cfg.bndSetPresent == "Yes" and imageName == cfg.bndSetNm:
			imageName = cfg.bndSet[0]
			# image CRS
			bN0 = self.selectLayerbyName(imageName)
			iCrs = self.getCrs(bN0)
			if iCrs is None:
				iCrs = cfg.cnvs.mapRenderer().destinationCrs()
				pCrs = cfg.cnvs.mapRenderer().destinationCrs()
			else:
				# projection of input point from project's crs to raster's crs
				pCrs = cfg.cnvs.mapRenderer().destinationCrs()
				if pCrs != iCrs:
					try:
						t = QgsCoordinateTransform(pCrs, iCrs)
						point = t.transform(point)
					# Error latitude or longitude exceeded limits
					except Exception, err:
						# logger
						if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
						crs = None
						# logger
						if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), QApplication.translate("semiautomaticclassificationplugin", "Error") + ": latitude or longitude exceeded limits")
						pass
			# workaround coordinates issue
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "project crs: " + str(pCrs.toProj4()) + " - raster " + str(imageName) + " crs: " + str(iCrs.toProj4()))
			cfg.lstPnt = QgsPoint(point.x() / float(1), point.y() / float(1))
			pX = point.x()
			pY = point.y()
			i = self.selectLayerbyName(imageName)
			if i is not None:
				# Point Check	
				cfg.pntCheck = None
				if pX > i.extent().xMaximum() or pX < i.extent().xMinimum() or pY > i.extent().yMaximum() or pY < i.extent().yMinimum() :
					# logger
					if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "point outside the image area")
					cfg.mx.msg6()
					cfg.pntCheck = "No"
				else :
					cfg.pntCheck = "Yes"
			else:
				# logger
				if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), " image missing")
				cfg.mx.msg4()
				cfg.pntCheck = "No"
		else:
			if self.selectLayerbyName(imageName) is None:
				cfg.mx.msg4()
				#cfg.ipt.refreshRasterLayer()
				self.pntROI = None
				cfg.pntCheck = "No"
			else:
				# image CRS
				bN0 = self.selectLayerbyName(imageName)
				iCrs = self.getCrs(bN0)
				if iCrs is None:
					iCrs = None
				else:
					# projection of input point from project's crs to raster's crs
					pCrs = cfg.cnvs.mapRenderer().destinationCrs()
					if pCrs != iCrs:
						try:
							t = QgsCoordinateTransform(pCrs, iCrs)
							point = t.transform(point)
						# Error latitude or longitude exceeded limits
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
							crs = None
							# logger
							if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), QApplication.translate("semiautomaticclassificationplugin", "Error") + ": latitude or longitude exceeded limits")
							pass
				# workaround coordinates issue
				# logger
				if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "project crs: " + str(pCrs.toProj4()) + " - raster " + str(imageName) + " crs: " + str(iCrs.toProj4()))
				cfg.lstPnt = QgsPoint(point.x() / float(1), point.y() / float(1))
				pX = point.x()
				pY = point.y()
				i = self.selectLayerbyName(imageName)
				# Point Check	
				cfg.pntCheck = None
				if pX > i.extent().xMaximum() or pX < i.extent().xMinimum() or pY > i.extent().yMaximum() or pY < i.extent().yMinimum() :
					# logger
					if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "point outside the image area")
					cfg.mx.msg6()
					cfg.pntCheck = "No"
				else :
					cfg.pntCheck = "Yes"
		
### Clear log file
	def clearLogFile(self):
		if os.path.isfile(cfg.logFile):
			try:
				l = open(cfg.logFile, 'w')
			except:
				pass
			try:
				l.write("Date	Function	Message \n")
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
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "feature geometry is none")			
		else:	
			# copy polygon to shapefile
			targetLayer.startEditing()
			targetLayer.addFeature(f)	
			targetLayer.commitChanges()
			targetLayer.dataProvider().createSpatialIndex()
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "feature copied")
				
### Delete a field from a shapefile by its name
	def deleteFieldShapefile(self, layerPath, fieldName):
		fds = self.fieldsShapefile(layerPath)
		s = ogr.Open(layerPath, 1)
		l = s.GetLayer()
		i = fds.index(fieldName)
		l.DeleteField(i)
		s = None
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "deleted field: " + str(fieldName) + " for layer: " + str(l.name()))
				
### Find field ID by name
	def fieldID(self, layer, fieldName):
		fID = layer.fieldNameIndex(str(fieldName))
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "ID: " + str(fID) + " for layer: " + str(layer.name()))
		return fID
				
### Get field names of a shapefile
	def fieldsShapefile(self, layerPath):
		s = ogr.Open(layerPath)
		l = s.GetLayer()
		lD = l.GetLayerDefn()
		fN = [lD.GetFieldDefn(i).GetName() for i in range(lD.GetFieldCount())]
		s = None
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "shapefile field " + str(l.name()))
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
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "crs for " + str(lddRstr.name()) + ": " + str(crs.toProj4 ()))
		return crs
				
### Get a feature from a shapefile by feature ID
	def getFeaturebyID(self, layer, ID):
		f = QgsFeature()
		# feature request
		fR = QgsFeatureRequest().setFilterFid(ID)
		try:
			f = layer.getFeatures(fR)
			f = f.next()
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "get feature " + str(ID) + " from shapefile: " + str(layer.name()))
			return f
		# if empty shapefile
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "roi bounding box: center " + str(r.center()) + " width: " + str(r.width())+ " height: " + str(r.height()))
		try:
			pass
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
			pass
			
### Get extentof a shapefile
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "roi bounding box: center " + str(r.center()) + " width: " + str(r.width())+ " height: " + str(r.height()))
		try:
			pass
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
			pass				
### get ID by attributes
	def getIDByAttributes(self, layer, field, attribute):
		IDs = []
		for f in layer.getFeatures(QgsFeatureRequest( str(field) + " = " + str(attribute))):
			IDs.append(f.id())
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ID: " + str(IDs))
		return IDs
		
### Get last feauture id
	def getLastFeatureID(self, layer):
		f = QgsFeature()
		for f in layer.getFeatures():
			ID = f.id()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ID: " + str(ID))
		return ID
		
### get a raster band from a multi band raster
	def getRasterBandByBandNumber(self, inputRaster, band, outputRaster):
		gdal.AllRegister()
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
		bDT = iRB.DataType
		a =  iRB.ReadAsArray()
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
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "get band: " + str(band))
		
### get a raster band statistic
	def getRasterBandStatistics(self, inputRaster, band):
		gdal.AllRegister()
		# open input with GDAL
		rD = gdal.Open(inputRaster, GA_ReadOnly)
		iRB = rD.GetRasterBand(band)
		bSt = iRB.GetStatistics(True, True)
		a =  iRB.ReadAsArray()
		# close band
		iRB = None
		# close raster
		rD = None
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "get band: " + str(band))
		return bSt, a
		
### calculate covariance matrix from array list
	def calculateCovMatrix(self, arrayList):
		# create empty array
		d = arrayList[0].shape
		arrCube = np.zeros((d[0], d[1], len(arrayList)), dtype=np.float64)
		i = 0
		for a in arrayList:
			arrCube[:, :, i] = a
			i = i + 1
		matrix = arrCube.reshape(d[0] * d[1], len(arrayList))
		# find No data
		NoDt = np.where(matrix[:, 0] == cfg.NoDataVal)
		# delete No data
		GMatrix = np.delete(matrix, NoDt, axis=0)
		TMatrix = GMatrix.T
		# covariance matrix (degree of freedom = 1 for unbiased estimate)
		CovMatrix = np.cov(TMatrix, ddof=1)
		if np.isnan(CovMatrix[0,0]):
			CovMatrix = "No"
		try:
			np.linalg.inv(CovMatrix)
		except:
			CovMatrix = "No"
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "cov matrix: " + str(CovMatrix))
		return CovMatrix
		
	def createVirtualRaster(self, inputRasterList, output):
		r = ""
		for i in inputRasterList:
			r = r + " " + i
		sP = subprocess.Popen("gdalbuildvrt -separate " + unicode(output) + " " + unicode(r), shell=True)
		sP.wait()
		return sP
		
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
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
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
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
		return list
		
	# clip a raster using a shapefile
	def clipRasterByShapefile(self,  shapefile, raster, outputRaster = None):
		if outputRaster is None:
			# temp files
			dT = self.getTime()
			tRN = cfg.copyTmpROI + dT + ".tif"
			tR = str(cfg.tmpDir + "//" + tRN)
		else:
			tR = str(outputRaster)
		sP = subprocess.Popen("gdalwarp -ot Float64 -dstnodata " + str(cfg.NoDataVal) + " -cutline \"" + unicode(shapefile) + "\" -crop_to_cutline -of GTiff " + unicode(raster) + " " + str(tR) , shell=True)
		sP.wait()
		return tR
		
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
		fN = "DN"
		fd = ogr.FieldDefn(fN, ogr.OFTInteger)
		rL.CreateField(fd)
		rL = None
		dS = None
		
	# create a polygon shapefile with QGIS
	def createEmptyShapefileQGIS(self, crs, outputVector):
		fields = QgsFields()
		# add field
		fN = "DN"
		fields.append(QgsField(fN, QVariant.Int))	
		QgsVectorFileWriter(outputVector.encode(cfg.fSEnc), "CP1250", fields, QGis.WKBPolygon, crs, "ESRI Shapefile")
		
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
						if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "group " + str(groupName) + " Position: " + str(p))

### Raster top left origin and pixel size
	def imageInformation(self, imageName):
		try:
			i = self.selectLayerbyName(imageName)
			# TopLeft X coord
			tLX = i.extent().xMinimum()
			# TopLeft Y coord
			tLY = i.extent().yMaximum()
			# pixel size
			pS = i.rasterUnitsPerPixelX()
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "image: " + str(imageName) + " topleft: (" + str(tLX) + ","+ str(tLY) + ")")
			# return a tuple TopLeft X, TopLeft Y, and Pixel size
			return tLX, tLY, pS
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
			return None, None, None
			
### Raster size
	def imageInformationSize(self, imageName):
		try:
			i = self.selectLayerbyName(imageName)
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
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "image: " + str(imageName) + " topleft: (" + str(tLX) + ","+ str(tLY) + ")")
			# return a tuple TopLeft X, TopLeft Y, and Pixel size
			return tLX, tLY, lRX, lRY, pS
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
			return None, None, None, None, None
						
### Layer ID by its name
	def layerID(self, layerName):
	 	ls = cfg.lgnd.layers()
		for l in ls:
			lN = l.name()
			if lN == layerName:
				# logger
				if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "layer: " + str(layerName) + " ID: " + str(l.id()))
				return l.id()
						
### Get the code line number for log file
	def lineOfCode(self):
		return str(inspect.currentframe().f_back.f_lineno)
		
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "pan action")
		
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		
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
				if int(v[i][0]) not in mc:
					mc.append(int(v[i][0]))
					n.append([int(v[i][0]), v[i][6], str(v[i][1])])
			else:
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		
### Split raster into single bands, and return a list of images
	def rasterToBands(self, raster, outputFolder):
		dT = self.getTime()
		i = self.selectLayerbyName(raster)
		iBC = i.bandCount()
		iL = ""
		for x in range(1, iBC+1):
			xB = outputFolder + "/" + "xBand_" + dT + "_" + str(x) + ".tif"
			self.getRasterBandByBandNumber(i.source().encode(cfg.fSEnc), x, xB)
			iL = iL + xB + ";"
		iL = iL.rstrip(';')
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "raster: " + str(raster) + " split to bands")
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return iL
		
	# delete all items in a table
	def clearTable(self, table):
		table.clearContents()
		for i in range(0, table.rowCount()):
			table.removeRow(0)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
			
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return rX, rY, lX, lY, pX, pY
		
	# read a block of band as array
	def readArrayBlock(self, gdalBand, pixelStartColumn, pixelStartRow, blockColumns, blockRow):
		a = gdalBand.ReadAsArray(pixelStartColumn, pixelStartRow, blockColumns, blockRow)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return a
		
	# write an array to band
	def writeArrayBlock(self, gdalRaster, bandNumber, dataArray, pixelStartColumn, pixelStartRow, nodataValue=None):
		b = gdalRaster.GetRasterBand(bandNumber)
		b.WriteArray(dataArray, pixelStartColumn, pixelStartRow)
		if nodataValue is not None:
			b.SetNoDataValue(nodataValue)
		b.FlushCache()
		b = None
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		
	def createRasterFromReference(self, gdalRasterRef, bandNumber, outputRasterList, nodataValue = None, driver = "GTiff", format = GDT_Float64, previewSize = 0, previewPoint = None, compress = "No"):
		oRL = []
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
			else:
				oR = tD.Create(o, c, r, bandNumber, format, ['COMPRESS=LZW'])
			# set raster projection from reference
			oR.SetGeoTransform(rGT)
			oR.SetProjection(rP)
			oRL.append(oR)
			if nodataValue is not None:
				for x in range(1, bandNumber+1):
					b = oR.GetRasterBand(x)
					b.Fill(nodataValue)
					b = None
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return oRL
		
	# create one raster for each signature class
	def createSignatureClassRaster(self, signatureList, gdalRasterRef, outputDirectory, nodataValue = None, outputName = None, previewSize = 0, previewPoint = None):
		dT = self.getTime()
		outputRasterList = []
		for s in range(0, len(signatureList)):
			if outputName == None:
				o = outputDirectory + "/" + cfg.sigRasterNm + "_" + str(signatureList[s][0]) + "_" + str(signatureList[s][2]) + "_" + dT + ".tif"
			else:
				o = outputDirectory + "/" + outputName + "_" + str(signatureList[s][0]) + "_" + str(signatureList[s][2]) + ".tif"
			outputRasterList.append(o)
		oRL = self.createRasterFromReference(gdalRasterRef, 1, outputRasterList, nodataValue, "GTiff", GDT_Float64, previewSize, previewPoint)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return oRL, outputRasterList
		
	# convert seconds to H M S
	def timeToHMS(self, time):
		min, sec = divmod(time, 60)
		hour, min = divmod(min, 60)
		if hour > 0:
			m = str("%.f" % round(hour)) + " H " + str("%.f" % round(min)) + " min"
		else:
			m = str("%.f" % round(min)) + " min " + str("%.f" % round(sec)) + " sec"
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return m
		
	# perform classification
	def classification(self, gdalBandList, signatureList, algorithmName, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, outputAlgorithmRaster, outputClassificationRaster, nodataValue, macroclassCheck, previewSize, pixelStartColumnPreview, pixelStartRowPreview, progressStart, progresStep, remainingBlocks):
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
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = time.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						cfg.uiUtls.updateBar(progress, self.timeToHMS(cfg.remainingTime) + " remaining")
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = time.clock()
					# algorithm
					c = self.algorithmMinimumDistance(rasterArray, s)
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
							minArray = self.findMinimumArray(c, minArray)
						# minimum raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, minArray, pixelStartColumn, pixelStartRow, nodataValue)
						# signature classification raster
						if macroclassCheck == "Yes":
							clA = self.classifyClasses(c, minArray, signatureList[n][0])
						else:
							clA = self.classifyClasses(c, minArray, signatureList[n][2])
						# classification raster
						if classArray == None:
							classArray = clA
						else:
							e = np.ma.masked_equal(clA, 0)
							classArray =  e.mask * classArray + clA
							e = None
						clA = None
						# threshold
						if cfg.algThrshld > 0:
							thr = self.minimumDistanceThreshold(minArray, cfg.algThrshld)
							classArray = classArray * thr
							thr = None		
						# classification raster
						self.writeArrayBlock(outputClassificationRaster, 1, classArray, pixelStartColumn, pixelStartRow, nodataValue)
						bN = bN + 1
						n = n + 1
					else:
						return "No"
				else:
					return "No"
		elif algorithmName == cfg.algSAM:
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = time.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						#cfg.uiUtls.updateBar(progress, self.timeToHMS(cfg.remainingTime) + " remaining")
						pass
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = time.clock()
					# algorithm
					c = self.algorithmSAM(rasterArray, s)
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
							minArray = self.findMinimumArray(c, minArray)
						# minimum raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, minArray, pixelStartColumn, pixelStartRow, nodataValue)
						# signature classification raster
						if macroclassCheck == "Yes":
							clA = self.classifyClasses(c, minArray, signatureList[n][0])
						else:
							clA = self.classifyClasses(c, minArray, signatureList[n][2])
						# classification raster
						if classArray == None:
							classArray = clA
						else:
							e = np.ma.masked_equal(clA, 0)
							classArray =  e.mask * classArray + clA
							e = None
						clA = None
						# threshold
						if cfg.algThrshld > 0:
							thr = self.minimumDistanceThreshold(minArray, cfg.algThrshld)
							classArray = classArray * thr
							thr = None
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
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = time.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						cfg.uiUtls.updateBar(progress, self.timeToHMS(cfg.remainingTime) + " remaining")
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = time.clock()
					# algorithm
					c = self.algorithmMaximumLikelihood(rasterArray, s, covMatrList[n])		
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
							maxArray = self.findMaximumArray(c, maxArray)
						# minimum raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, maxArray, pixelStartColumn, pixelStartRow, nodataValue)
						# signature classification raster
						if macroclassCheck == "Yes":
							clA = self.classifyClasses(c, maxArray, signatureList[n][0])
						else:
							clA = self.classifyClasses(c, maxArray, signatureList[n][2])
						# classification raster
						if classArray == None:
							classArray = clA
						else:
							e = np.ma.masked_equal(clA, 0)
							classArray =  e.mask * classArray + clA
							e = None
						clA = None
						# threshold
						if cfg.algThrshld > 0:
							thr = self.maximumLikelihoodThreshold(maxArray)
							classArray = classArray * thr
							thr = None
						# classification raster
						self.writeArrayBlock(outputClassificationRaster, 1, classArray, pixelStartColumn, pixelStartRow, nodataValue)
						bN = bN + 1
						n = n + 1
					else:
						return "No"
				else:
					return "No"
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
				
	# classify classes
	def classifyClasses(self, algorithmArray, minimumArray, classID):
		cA = np.equal(algorithmArray, minimumArray) * int(classID)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return cA
		
	# find minimum array
	def findMinimumArray(self, firstArray, secondArray):
		m = np.minimum(firstArray, secondArray)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return m
		
	# find maximum array
	def findMaximumArray(self, firstArray, secondArray):
		f = np.ma.masked_equal(firstArray, cfg.NoDataVal)
		s = np.ma.masked_equal(secondArray, - cfg.NoDataVal)
		m = np.maximum(firstArray, secondArray)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return m
		
	# set threshold
	def maximumLikelihoodThreshold(self, array):	
		outArray = np.where(array > cfg.maxLikeNoDataVal, 1, 0)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return outArray
		
	# set threshold
	def minimumDistanceThreshold(self, array, threshold):	
		outArray = np.where(array < threshold, 1, 0)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return arrayList
	
	# minimum Euclidean distance algorithm [ sqrt( sum( (r_i - s_i)^2 ) ) ]
	def algorithmMinimumDistance(self, rasterArray, signatureArray):
		try:
			algArray = np.sqrt(((rasterArray - signatureArray)**2).sum(axis = 2))
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
			return algArray
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
		
	# create covariance matrix list from signature list
	def covarianceMatrixList(self, signatureList):
		c = []
		for s in signatureList:
			cov = s[7]
			c.append(cov)
		return c
		
	# calculate critical chi square and threshold
	def chisquare(self):
		p = 1 - (cfg.algThrshld / 100)
		chi = dist.chi2.isf(p, 4)
		return chi
		
	# Maximum Likelihood algorithm
	def algorithmMaximumLikelihood(self, rasterArray, signatureArray, covarianceMatrix):
		try:
			(sign, logdet) = np.linalg.slogdet(covarianceMatrix)
			invC = np.linalg.inv(covarianceMatrix)
			d = rasterArray - signatureArray
			v = rasterArray.shape
			algArray = np.zeros((v[0], v[1]), dtype=np.float64)
			for i in range(0, v[0]):
				for j in range(0, v[1]):
					algArray[i, j] = - logdet - np.dot(np.dot(d[i, j, :].T, invC), d[i, j, :])
			if cfg.algThrshld > 0:
				chi = self.chisquare()
				threshold = - chi - logdet
				e = np.ma.masked_less(algArray, threshold)
				algArray = np.ma.filled(e, cfg.maxLikeNoDataVal)
			return algArray
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
		
	# spectral angle mapping algorithm [ arccos( sum(r_i * s_i) / ( sum(r_i**2) * sum(s_i**2) ) ) ]
	def algorithmSAM(self, rasterArray, signatureArray):
		try:
			algArray = np.arccos((rasterArray * signatureArray).sum(axis = 2) / np.sqrt((rasterArray**2).sum(axis = 2) * (signatureArray**2).sum())) * 180 / np.pi
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
			return algArray
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
			
	# read all raster from band
	def readAllBandsFromRaster(self, gdalRaster):
		bandNumber = gdalRaster.RasterCount
		bandList = []
		for b in range(1, bandNumber + 1):
			rB = gdalRaster.GetRasterBand(b)
			bandList.append(rB)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return bandList
	
	# process a raster with block size
	def processRaster(self, gdalRaster, gdalBandList, signatureList = None, functionBand = None, functionRaster = None, algorithmName = None, outputRasterList = None, outputAlgorithmRaster = None, outputClassificationRaster = None, previewSize = 0, previewPoint = None, nodataValue = None, macroclassCheck = "No", functionBandArgument = None, functionVariable = None):
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
							array[::, ::, b] = a.reshape(bSX, bSY)
							a = None
							# set nodata value
							array[::, ::, b][array[::, ::, b] == ndv] = np.nan
							if functionBand is not None:
								functionBand(b+1, array[::, ::, b].reshape(bSY, bSX), bSX, bSY, x, y, outputRasterList, functionBandArgument, functionVariable)
						c = array.reshape(bSY, bSX, len(gdalBandList))
						array = None
						if functionRaster is not None:
							qApp.processEvents()
							o = functionRaster(gdalBandList, signatureList, algorithmName, c, bSX, bSY, x, y, outputRasterList, outputAlgorithmRaster, outputClassificationRaster, nodataValue, macroclassCheck, previewSize, pX[lX.index(x)], pY[lY.index(y)], progressStart, progresStep, remainingBlocks)
							if o == "No":
								return "No"
						remainingBlocks = (remainingBlocks - 1)
					else:
						return "No"
			outputClassificationRaster = None
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
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
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
					
	# reclassify raster
	def reclassifyRaster(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariable):
		if cfg.actionCheck == "Yes":
			o = rasterArray
			for i in functionBandArgument:
				# create condition
				c = i[0].replace(functionVariable, "rasterArray")
				f = "np.where(" + c + ", " + str(i[1]) + ", o)"
				# perform operation
				o = eval(f)
			oR = outputGdalRasterList[0]
			# output raster
			self.writeArrayBlock(oR, 1, o, pixelStartColumn, pixelStartRow)
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
			
	# calculate raster unique values
	def rasterUniqueValues(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariable):
		if cfg.actionCheck == "Yes":
			val = np.unique(rasterArray).tolist()
			cfg.rasterBandUniqueVal.extend(val)
			cfg.rasterBandUniqueVal = list(set(cfg.rasterBandUniqueVal))
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
			return cfg.rasterBandUniqueVal 
			
	# calculate raster unique values
	def rasterPixelSum(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariable):
		if cfg.actionCheck == "Yes":
			val = (rasterArray == functionBandArgument).sum()
			cfg.rasterPixelSum = cfg.rasterPixelSum + val
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
			
	# calculate block size
	def calculateBlockSize(self, bandNumber):
		b = int((cfg.RAMValue / (cfg.arrayUnitMemory * (bandNumber +  5) ))**.5)
		# set system memory max
		if cfg.sys64bit == "No" and b > 2500:
			b = 2500
		# check memory
		try:
			a = np.zeros((b,b), dtype = np.float64)
			cfg.uiUtls.updateBar(20,  QApplication.translate("semiautomaticclassificationplugin", "Calculating remaining time"))
		except:
			for i in reversed(range(128, cfg.RAMValue, int(cfg.RAMValue/10))):
				try:
					b = int((i / (cfg.arrayUnitMemory * (bandNumber +  5) ))**.5)
					# set system memory max
					if cfg.sys64bit == "No" and b > 2500:
						b = 2500
					a = np.zeros((int(b),int(b)), dtype = np.float64)
					size = a.nbytes / 1048576
					cfg.ui.RAM_spinBox.setValue(size * bandNumber)
					cfg.mx.msgWar11()
					cfg.uiUtls.updateBar(20,  QApplication.translate("semiautomaticclassificationplugin", "Calculating remaining time"))
					# logger
					if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "block = " + str(b))
					return b
				except Exception, err:
					# logger
					if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "block = " + str(b))
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
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "color")
			return c
			
	# Define raster symbology
	def rasterSymbolGeneric(self, rasterLayer):
		rasterLayer.setDrawingStyle("SingleBandPseudoColor")
		# The band of classLayer
		classLyrBnd = 1
		# Band statistics
		bndStat = rasterLayer.dataProvider().bandStatistics(1)
		classMax = bndStat.maximumValue
		# Color list for ramp
		clrLst = [ QgsColorRampShader.ColorRampItem(0, QColor(0,0,0), "Unchanged"), QgsColorRampShader.ColorRampItem(1, QColor(0,0,255), "1"), QgsColorRampShader.ColorRampItem(round(classMax/2), QColor(255,0,0), str(round(classMax/2))), QgsColorRampShader.ColorRampItem(classMax, QColor(0,255,0), str(classMax)) ]
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "symbology")
			
	# read project variable
	def readProjectVariable(self, variableName, value):
		p = QgsProject.instance()
		v = p.readEntry("SemiAutomaticClassificationPlugin", variableName, value)[0]
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		return v
		
### Remove layer from map
	def removeLayer(self, layerName):
		QgsMapLayerRegistry.instance().removeMapLayer(self.layerID(layerName))
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		
### Select layer by name thereof
	def selectLayerbyName(self, layerName):
	 	ls = cfg.lgnd.layers()
		for l in ls:
			lN = l.name()
			if lN == layerName:
				return l
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "layer selected: " + str(layerName))
			
### Subset an image, given an origin point and a subset width
	def subsetImage(self, imageName, XCoord, YCoord, Width, Height, output):
		i = self.selectLayerbyName(imageName)
		# output variable
		st = "No"
		# raster top left origin and pixel size
		tLX, tLY, lRX, lRY, pS = self.imageInformationSize(imageName)
		if pS is None:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " image none or missing")
		else:			
			# subset origin
			sX = (int((XCoord - tLX) / pS)) - int(Width / 2) 
			sY = (int((tLY - YCoord) / pS)) - int(Height / 2)
			sP = subprocess.Popen("gdal_translate -ot Float64 -a_nodata " + str(cfg.NoDataVal) + " -srcwin " + str(sX) + " " + str(sY) + " " + str(Width) + " " + str(Height) + " -of GTiff \"" + i.source().encode(cfg.fSEnc) + "\" " + output, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			if len(err) > 0:
				st = "Yes"
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error:: " + str(err) )
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "image: " + str(imageName) + " subset origin: (" + str(XCoord) + ","+ str(YCoord) + ") width: " + str(Width))
			return st
			
### convert reference layer to raster based on the resolution of a raster
	def vectorToRaster(self, fieldName, layerPath, referenceRasterName, outputRaster):
		# band set
		if cfg.bndSetPresent == "Yes" and referenceRasterName == cfg.bndSetNm:
			referenceRasterName = cfg.bndSet[0]
			# input
			r = self.selectLayerbyName(referenceRasterName)
		else:
			if self.selectLayerbyName(referenceRasterName) is None:
				cfg.mx.msg4()
				cfg.ipt.refreshRasterLayer()
			else:
				# input
				r = self.selectLayerbyName(referenceRasterName)
		# register drivers
		gdal.AllRegister()
		try:
			rS = r.source().encode(cfg.fSEnc)
			ck = "Yes"
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
			ck = "No"
		if ck == "No":
			cfg.mx.msg4()
		else:
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
			tD = gdal.GetDriverByName( "GTiff" )
			oR = tD.Create(outputRaster, rC, rR, 1, GDT_Int32)
			oRB = oR.GetRasterBand(1)
			# set raster projection from reference
			oR.SetGeoTransform( [ rGT[0] , rGT[1] , 0 , rGT[3] , 0 , rGT[5] ] )
			oR.SetProjection(rP)
			oRB.SetNoDataValue(cfg.NoDataVal)
			m = np.zeros((rR, rC), dtype='int32')
			m.fill(cfg.NoDataVal)
			oRB.WriteArray(m, 0, 0)
			oRB.FlushCache()
			l = ogr.Open(layerPath)
			gL = l.GetLayer()
			# convert reference layer to raster
			oC = gdal.RasterizeLayer(oR, [1], gL, options = ["ATTRIBUTE=" + str(fieldName)])
			# close bands
			oRB = None
			# close rasters
			oR = None
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "vector to raster check: " + str(oC))
			
	# convert raster to shapefile
	def rasterToVector(self, rasterPath, outputShapefilePath):
		gdal.AllRegister()
		tD = gdal.GetDriverByName( "GTiff" )
		# open input with GDAL
		rD = gdal.Open(rasterPath, GA_ReadOnly)
		# create a shapefile
		d = ogr.GetDriverByName('ESRI Shapefile')
		dS = d.CreateDataSource(outputShapefilePath)
		if dS is None:
			# close rasters
			rD = None
			# logger
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), " failed: " + str(outputVector))
		else:
			# shapefile
			sR = osr.SpatialReference()
			sR.ImportFromWkt(rD.GetProjectionRef())
			rL = dS.CreateLayer(str(os.path.basename(rasterPath)), sR, ogr.wkbPolygon)
			fN = str(cfg.fldID_class)
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
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), " vector output performed")

	# write project variable
	def writeProjectVariable(self, variableName, value):
		p = QgsProject.instance()
		p.writeEntry("SemiAutomaticClassificationPlugin", variableName, value)
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + self.lineOfCode(), "")
		
### Delete a feauture from a shapefile by its Id
	def deleteFeatureShapefile(self, layer, feautureIds):
		layer.startEditing()				
		res = layer.dataProvider().deleteFeatures(feautureIds)
		layer.commitChanges()
		res2 = layer.dataProvider().createSpatialIndex()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "feauture deleted: " + str(layer) + " " + str(feautureId) )

### Edit a feauture in a shapefile by its Id
	def editFeatureShapefile(self, layer, feautureId, fieldName, value):
		id = self.fieldID(layer, fieldName)
		layer.startEditing()				
		res = layer.changeAttributeValue(feautureId, id, value)
		layer.commitChanges()
		res2 = layer.dataProvider().createSpatialIndex()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "feauture edited: " + unicode(layerPath) + " " + str(feautureId) )
		
	# select band set tab
	def bandSetTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(3)
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# show the dialog
		cfg.dlg.show()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "tab selected")
		
	# select roi tools tab
	def roiToolsTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		# show the dialog
		cfg.dlg.show()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "tab selected")

	# select roi tools tab
	def mutlipleROITab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		cfg.ui.tabWidget.setCurrentIndex(0)
		# show the dialog
		cfg.dlg.show()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "tab selected")
		
	# select pre processing tab
	def preProcessingTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(1)
		# show the dialog
		cfg.dlg.show()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "tab selected")
		
	# select post processing tab
	def postProcessingTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(2)
		# show the dialog
		cfg.dlg.show()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "tab selected")
		
	# select settings tab
	def settingsTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(4)
		# show the dialog
		cfg.dlg.show()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "tab selected")
		
	def sortTableColumn(self, table, column, ascending = False):
		table.sortItems(column, ascending)
		
	# spectral singature plot tab
	def spectralPlotTab(self):
		cfg.spectralplotdlg.close()
		cfg.spectralplotdlg.show()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "tab selected")
				
	# scatter plot tab
	def scatterPlotTab(self):
		cfg.scatterplotdlg.close()
		cfg.scatterplotdlg.show()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "tab selected")
		
	# scatter plot tab
	def importUSGSLibraryTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		cfg.ui.tabWidget.setCurrentIndex(1)
		# show the dialog
		cfg.dlg.show()
		# logger
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "tab selected")
		
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
			if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), " ERROR exception: " + str(err))
		
""" deprecated
		
### Select a layer feature by point coordinates and return a temporary ROI
	# def selectbyCoords(self, layer, XCoord, YCoord):
		# # feature
		# f = QgsFeature()
		# ROI = QgsFeature()
		# fID = None
		# allF = layer.getFeatures()
		# dT = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
		# # temp name
		# tmpShp2Nm = "ROI_temp" + dT
		# while allF.nextFeature(f):
			# if f.geometry().intersects(QgsRectangle(XCoord + 0.00000001, YCoord + 0.00000001, XCoord, YCoord)):
				# fID = QgsFeature(f).id()
				# f2Geometry = f.geometry().asPolygon()
				# break
		# if fID is None:
			# cfg.mx.msg6()
			# # logger
			# if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), QApplication.translate("semiautomaticclassificationplugin", "Error") + ": point outside layer")
		# else:
			# # band set
			# if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
				# bN0 = self.selectLayerbyName(cfg.bndSet[0])
				# # crs of loaded raster
				# crs = self.getCrs(bN0)
			# else:
				# # crs of loaded raster
				# crs = self.getCrs(cfg.rLay)
			# # create layer
			# memLyr = QgsVectorLayer("Polygon", tmpShp2Nm, "memory")
			# memLyr.setCrs(crs) 
			# prvdr = memLyr.dataProvider()
			# memLyr.startEditing()		
			# # add fields
			# prvdr.addAttributes( [QgsField("ID",  QVariant.Int)] )
			# # add a feature
			# ROI.setGeometry(QgsGeometry.fromPolygon(f2Geometry))
			# ROI.setAttributes([1])
			# prvdr.addFeatures([ROI])
			# memLyr.commitChanges()
			# memLyr.updateExtents()
			# return memLyr
			# # logger
			# if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "feauture selected at point: (" + str(XCoord) + "," + str(YCoord) + ") for layer: " + str(layer.name()))
		
### Check if training shapefile is empty
	# def checkEmptyShapefile(self, layer):
		# if self.getFeaturebyID(layer, 1) is False:
			# return "No"
			# cfg.mx.msg5()
			# # logger
			# if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "empty shapefile")
		# else:
			# return "Yes"

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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "feauture deleted: " + str(layerPath) + " " + str(feautureId) )
		
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
		if cfg.logSetVal == "Yes": self.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + self.lineOfCode(), "feauture edited: " + unicode(layerPath) + " " + str(feautureId) )
		
	# Maximum Likelihood algorithm
	def algorithmMaximumLikelihoodOLD(self, rasterArray, signatureArray, covarianceMatrix):
		(sign, logdet) = np.linalg.slogdet(covarianceMatrix)
		invC = np.linalg.inv(covarianceMatrix)
		d = rasterArray - signatureArray
		v = rasterArray.shape
		algArray = np.zeros((v[0], v[1]), dtype=np.float64)
		for i in range(0, v[0]):
			tr = d[i, :, :]
			o = np.tensordot(tr.transpose(),invC, axes=([0,0]))
			p = np.tensordot(o, tr, axes=([1,1]))
			dg = p.diagonal()
			algArray[i, :] = - logdet - dg
		if cfg.algThrshld > 0:
			chi = self.chisquare()
			threshold = - chi - logdet
			e = np.ma.masked_less(algArray, threshold)
			algArray = np.ma.filled(e, cfg.maxLikeNoDataVal)
		return algArray
			
	# convert project variable to list
	def projectVariableToList(self, variableString):
		bs = str(variableString)
		bs = bs.strip("[")
		bs = bs.replace("u'", "")
		bs = bs.replace("'", "")
		bs = bs.replace(" ", "")
		bs = bs.strip("']")
		bs = bs.split(",")
		return bs
		
	# convert string list to float list
	def stringListToFloat(self, list):
		x = []
		for s in range(0, len(list)):
			x.append(float(list[s]))
		return x
		
"""