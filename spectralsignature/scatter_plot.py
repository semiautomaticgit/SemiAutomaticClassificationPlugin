# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
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
import datetime
import subprocess
# for debugging
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qgis.utils as qgisUtils
from osgeo import gdal
from osgeo import ogr 
from osgeo import osr
from osgeo.gdalconst import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class Scatter_Plot:

	def __init__(self):
		pass
		
	def scatterPlotDoubleClick(self, index):
		if index.column() == 5:
			c = cfg.utls.selectColor()
			if c is not None:
				cfg.uiscp.scatter_list_plot_tableWidget.item(index.row(), 5).setBackground(c)
		else:
			self.selectAllROIs()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures index: " + str(index))
		
	# select all signatures
	def selectAllROIs(self):
		try:
			cfg.uiUtls.addProgressBar()
			# select all
			if cfg.allSignCheck == "Yes":
				cfg.utls.allItemsSetState(cfg.uiscp.scatter_list_plot_tableWidget, 2)
				# set check all plot
				cfg.allSignCheck = "No"
			# unselect all if previously selected all
			elif cfg.allSignCheck == "No":
				cfg.utls.allItemsSetState(cfg.uiscp.scatter_list_plot_tableWidget, 0)
				# set check all plot
				cfg.allSignCheck = "Yes"
			cfg.uiUtls.removeProgressBar()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all signatures")
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.removeProgressBar()
			
	# Create scatter plot
	def scatterPlot(self):
		if cfg.rstrNm is not None:
			cfg.uiUtls.addProgressBar()
			tW = cfg.uiscp.scatter_list_plot_tableWidget
			# Clear plot
			cfg.uiscp.Sig_Widget_2.sigCanvas.ax.clear()
			cfg.uiscp.Sig_Widget_2.sigCanvas.draw()
			bX = cfg.scatterBandX
			bY = cfg.scatterBandY
			# Set labels
			cfg.uiscp.Sig_Widget_2.sigCanvas.ax.set_xlabel(QApplication.translate("semiautomaticclassificationplugin", "Band" + " " +  str(bX)))
			cfg.uiscp.Sig_Widget_2.sigCanvas.ax.set_ylabel(QApplication.translate("semiautomaticclassificationplugin", "Band" + " " + str(bY)))
			# Add plots and legend
			pL = []
			pLN = []
			xP = []
			yP = []
			r = tW.rowCount()
			for b in range(0, r):
				if tW.item(b, 0).checkState() == 2:
					i = int(tW.item(b, 6).text())
					nm = tW.item(b, 1).text() + "#" + tW.item(b, 2).text() + " " + tW.item(b, 3).text() + "#" + tW.item(b, 4).text()
					# color
					c = str(tW.item(b, 5).background().color().toRgb().name())
					xP = self.calculateScatter(cfg.shpLay, bX, i)
					yP = self.calculateScatter(cfg.shpLay, bY, i)
					p = cfg.uiscp.Sig_Widget_2.sigCanvas.ax.scatter(xP, yP, color=c, s=3)
					# add plot to legend
					pL.append(p)
					pLN.append(nm[:cfg.roundCharList])
			# place legend		
			cfg.uiscp.Sig_Widget_2.sigCanvas.ax.legend(pL, pLN, bbox_to_anchor=(0.1, 0.0, 1.1, 1.1), loc=1, borderaxespad=0.).draggable()
			# Grid for X and Y axes
			cfg.uiscp.Sig_Widget_2.sigCanvas.ax.grid('on')
			# Draw the plot
			cfg.uiscp.Sig_Widget_2.sigCanvas.draw()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " scatter plot created")
			cfg.uiUtls.removeProgressBar()
		
	# calculate scatter statistics for selected ROIs
	def calculateScatter(self, lyr, rasterBand, featureID):
		cfg.uiUtls.updateBar(0)
		# disable map canvas render for speed
		cfg.cnvs.setRenderFlag(False)
		# date time for temp name
		dT = cfg.utls.getTime()
		# temp subset
		tSN = cfg.subsROINm
		tSD = cfg.tmpDir + "/" + dT + tSN
		# ROI class name
		cN = cfg.subsTmpRaster + str(rasterBand) + str(featureID) + ".tif"
		# ROI class path
		cD = cfg.tmpDir + "/" + dT + cN
		# temporary layer
		tLN = cfg.subsTmpROI + dT + ".shp"
		tLD = cfg.tmpDir + "/" + tLN
		# get layer crs
		crs = cfg.utls.getCrs(lyr)
		# create a temp shapefile with a field
		cfg.utls.createEmptyShapefile(crs.toWkt(), tLD)
		tL = cfg.utls.addVectorLayer(tLD , tLN, "ogr")
		# copy ROI to temp shapefile
		cfg.utls.copyFeatureToLayer(lyr, featureID, tL)		
		f = cfg.utls.getFeaturebyID(tL, 0)
		g = f.geometry()
		# bounding box rectangle
		r = g.boundingBox().toString()
		xM = g.boundingBox().xMaximum()
		xMn = g.boundingBox().xMinimum()
		yM = g.boundingBox().yMaximum()
		yMn = g.boundingBox().yMinimum()		
		cfg.uiUtls.updateBar(10)
		# band set
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			rB = rasterBand - 1
			rL = cfg.utls.selectLayerbyName(str(cfg.bndSet[rB]))
			sP = subprocess.Popen("gdal_translate -a_nodata -999 -projwin " + str(xMn) + " " + str(yM) + " " + str(xM) + " " + str(yMn) + " -of GTiff \"" + rL.source().encode(cfg.fSEnc) + "\" " + str(tSD), shell=True)
			sP.wait()
			sP = subprocess.Popen("gdalwarp -dstnodata  -999 -cutline " + str(tLD) + " -of GTiff " + str(tSD) + " " + cD, shell=True)
			sP.wait()
		else:
			# temp files
			tRN = cfg.subsTmpROI + dT + ".tif"
			tRD = str(cfg.tmpDir + "//" + tRN)
			i = cfg.utls.selectLayerbyName(str(cfg.rstrNm))		
			cfg.utls.getRasterBandByBandNumber(i.source().encode(cfg.fSEnc), rasterBand, tRD)
			sP = subprocess.Popen("gdal_translate -a_nodata -999 -projwin " + str(xMn) + " " + str(yM) + " " + str(xM) + " " + str(yMn) + " -of GTiff " + str(tRD) + " " + str(tSD), shell=True)
			sP.wait()
			sP = subprocess.Popen("gdalwarp -dstnodata  -999 -cutline " + str(tLD) + " -of GTiff " + str(tSD) + " " + cD, shell=True)
			sP.wait()
		# register drivers
		gdal.AllRegister()
		# open input with GDAL
		rD = gdal.Open(cD, GA_ReadOnly)
		# number of x pixels
		rC = rD.RasterXSize
		# number of y pixels
		rR = rD.RasterYSize
		# get band
		b = rD.GetRasterBand(1)
		lst = []
		for y in range(0, rR):
			for x in range(0, rC):
				a = b.ReadAsArray(x, y, 1, 1)
				# filter 0 and -999
				if a[0,0] != 0:
					if a[0,0] != -999:
						lst.append(a[0,0])
		# remove temp layers
		#cfg.utls.removeLayer(tLN)
		b = None
		rD = None
		# enable map canvas render
		cfg.cnvs.setRenderFlag(True)
		cfg.uiUtls.updateBar(100)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " scatter plot calculated " + str(lyr) + " band " + str(rasterBand) + " ID " + str(featureID))
		return lst
		
	# set band X
	def bandXPlot(self):
		# band set
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			b = len(cfg.bndSet)
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm)
			try:
				b = i.bandCount()
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				b = 1
		if cfg.uiscp.bandX_spinBox.value() > b:
			cfg.uiscp.bandX_spinBox.setValue(b)
		cfg.scatterBandX = cfg.uiscp.bandX_spinBox.value()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "scatter band X: " + str(cfg.scatterBandX))
		
	# set band Y
	def bandYPlot(self):
		# band set
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			b = len(cfg.bndSet)
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm)
			try:
				b = i.bandCount()
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				b = 1
		if cfg.uiscp.bandY_spinBox.value() > b:
			cfg.uiscp.bandY_spinBox.setValue(b)
		cfg.scatterBandY = cfg.uiscp.bandY_spinBox.value()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "scatter band X: " + str(cfg.scatterBandY))
		