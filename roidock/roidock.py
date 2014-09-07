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
# for debugging
import inspect
import numpy as np
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
try:
	from scipy.ndimage import label
	cfg.scipyCheck = "Yes"
except:
	cfg.scipyCheck = "No"

class RoiDock:

	def __init__(self):
		# rubber band
		cfg.rbbrBnd = QgsRubberBand(cfg.cnvs)
		cfg.rbbrBnd.setColor(QColor(0,255,255))
		cfg.rbbrBnd.setWidth(2)
		# emit a QgsPoint on each click
		cfg.clickROI = QgsMapToolEmitPoint(cfg.cnvs)
		
	# check refresh shape and training list	
	def checkRefreshShapeLayer(self):
		# check if other processes are active
		if cfg.actionCheck == "No":
			cfg.uid.ROI_tableWidget.blockSignals(True)
			self.refreshShapeLayer()
			cfg.uid.ROI_tableWidget.blockSignals(False)

	# left click
	def clckL(self, pnt):
		cfg.utls.checkPointImage(cfg.rstrNm, pnt)
		if cfg.pntCheck == "Yes":
			cfg.lastVrt.append(pnt)
			cfg.rbbrBnd.addPoint(pnt)
			v = QgsVertexMarker(cfg.cnvs)
			v.setCenter(pnt)
			self.mrctrVrtc.append(v)
		
	# right click
	def clckR(self, pnt):
		cfg.utls.checkPointImage(cfg.rstrNm, pnt)
		if cfg.pntCheck == "Yes":
			self.clckL(pnt)
			f = QgsFeature()
			dT = cfg.utls.getTime()
			# temp name
			tN = cfg.subsTmpROI + dT
			# band set
			if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
				# crs of loaded raster
				bN = cfg.utls.selectLayerbyName(cfg.bndSet[0])
				crs = cfg.utls.getCrs(bN)
				ck = "Yes"
			else:
				try:
					# crs of loaded raster
					crs = cfg.utls.getCrs(cfg.rLay)
					ck = "Yes"
				except:
					ck = "No"
			if crs is None:
				ck = "No"
			if ck == "Yes":
				mL = QgsVectorLayer("Polygon?crs=" + str(crs.toWkt()), tN, "memory")
				mL.setCrs(crs) 
				if not len(cfg.lastVrt) >= 3:
					cfg.mx.msg16()
					self.clearCanvas()
					return
				g = QgsGeometry().fromPolygon([cfg.lastVrt])
				# no intersection
				mL.removePolygonIntersections(g)
				mL.addTopologicalPoints(g)
				pr = mL.dataProvider()
				# create temp ROI
				mL.startEditing()		
				# add fields
				pr.addAttributes( [QgsField("ID",  QVariant.Int)] )
				# add a feature
				f.setGeometry(g)
				f.setAttributes([1])
				pr.addFeatures([f])
				mL.commitChanges()
				mL.updateExtents()
				self.clearCanvas()
				# semitransparent symbol and line for ROI
				rT = cfg.ROITrnspVal * 255 / 100
				rC = str(QColor(cfg.ROIClrVal).red()) + "," + str(QColor(cfg.ROIClrVal).green()) + "," + str(QColor(cfg.ROIClrVal).blue()) + "," + str(rT) 
				sP = { 'color' : rC , 'color_border' : '0,255,255,50', 'offset' : '0,0', 'style' : 'solid', 'style_border' : 'dot', 'width_border' : '0.4' }
				sL = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SimpleFill").createSymbolLayer(sP)
				# apply symbology
				mL.setRendererV2(QgsSingleSymbolRendererV2(QgsFillSymbolV2([sL])))
				# workaround for setRendererV2 crash
				lS = mL.rendererV2().symbols()
				fS = lS[0]
				fS.appendSymbolLayer(sL)
				# add ROI layer
				cfg.uiUtls.updateBar(90)
				cfg.utls.addLayerToMap(mL)
				# create temp group
				cfg.lstROI = mL
				g = cfg.utls.groupIndex(cfg.grpNm)
				if g is None:
					g = cfg.lgnd.addGroup(cfg.grpNm, False) 
					cfg.lgnd.moveLayer (cfg.lstROI, g)
				else:
					cfg.lgnd.moveLayer (cfg.lstROI, g)
				cfg.uid.button_Save_ROI.setEnabled(True)
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< ROI created: " + str(tN))
			else:
				cfg.mx.msg4()
				self.clearCanvas()
		
	# clear canvas
	def clearCanvas(self):
		cfg.lastVrt = []
		cfg.rbbrBnd.reset(True)
		for m in self.mrctrVrtc:
		    cfg.cnvs.scene().removeItem(m)
		    del m
		cfg.cnvs.refresh()	
		
	# set Min ROI size
	def minROISize(self):
		cfg.minROISz = int(cfg.uid.Min_region_size_spin.value())
		cfg.utls.writeProjectVariable("minROISize", str(cfg.minROISz))
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "min roi size: " + str(cfg.minROISz))

	# set Max ROI size
	def maxROIWidth(self):
		cfg.maxROIWdth = int(cfg.uid.Max_ROI_width_spin.value())
		cfg.utls.writeProjectVariable("maxROIWidth", str(cfg.maxROIWdth))
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "max roi width: " + str(cfg.maxROIWdth))

	def pointerClickROI(self, point):
		# check if other processes are active
		if cfg.actionCheck == "No":
			cfg.utls.checkPointImage(cfg.rstrNm, point)
			if cfg.pntCheck == "Yes":
				cfg.pntROI = cfg.lstPnt
				self.createROI(cfg.pntROI)
		
	# Activate pointer for ROI creation
	def pointerManualROIActive(self):
		cfg.lastVrt = []
		self.mrctrVrtc = []
		t = cfg.mnlROI
		cfg.cnvs.setMapTool(t)
		c = QCursor()
		c.setShape(Qt.CrossCursor)
		cfg.cnvs.setCursor(c)

		
	# Activate pointer for ROI creation
	def pointerROIActive(self):
		# connect to click
		cfg.cnvs.setMapTool(cfg.clickROI)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: ROI")
		
	# set Range radius
	def rangeRadius(self):
		cfg.rngRad = float(cfg.uid.Range_radius_spin.value())
		cfg.utls.writeProjectVariable("rangeRadius", str(cfg.rngRad))
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "range radius: " + str(cfg.rngRad))

	# set ROI class info
	def roiClassInfo(self):
		cfg.ROIInfo = str(cfg.uid.ROI_Class_line.text())
		cfg.utls.writeProjectVariable("ROIInfoField", str(cfg.ROIInfo))
		self.roiInfoCompleter()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi info: " + str(cfg.ROIInfo))
		
	# ROI info completer
	def roiInfoCompleter(self):
		if cfg.shpLay is not None:
			l = cfg.utls.getFieldAttributeList(cfg.shpLay, cfg.fldROI_info)
			# class names
			cfg.cmplClsNm = QCompleter(l)
			cfg.uid.ROI_Class_line.setCompleter(cfg.cmplClsNm)
			
	# set ROI class info
	def roiMacroclassInfo(self):
		cfg.ROIMacroClassInfo = str(cfg.uid.ROI_Macroclass_line.text())
		cfg.utls.writeProjectVariable("ROIMacroclassInfoField", str(cfg.ROIMacroClassInfo))
		self.roiMacroclassInfoCompleter()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi info: " + str(cfg.ROIInfo))
			
	# ROI info completer
	def roiMacroclassInfoCompleter(self):
		if cfg.shpLay is not None:
			l = cfg.utls.getFieldAttributeList(cfg.shpLay, cfg.fldROIMC_info)
			# class names
			cfg.cmplMClsNm = QCompleter(l)
			cfg.uid.ROI_Macroclass_line.setCompleter(cfg.cmplMClsNm)
		
	# set ROI class ID
	def setROIID(self):
		cfg.ROIID = cfg.uid.ROI_ID_spin.value()
		cfg.utls.writeProjectVariable("ROIIDField", str(cfg.ROIID))
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi id: " + str(cfg.ROIID))
		
	# set ROI macroclass ID
	def setROIMacroID(self):
		cfg.ROIMacroID = cfg.uid.ROI_Macroclass_ID_spin.value()
		cfg.utls.writeProjectVariable("ROIMacroIDField", str(cfg.ROIMacroID))
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi macroclass id: " + str(cfg.ROIMacroID))
	
	# set shape name for saving ROIs
	def shapeLayerName(self):
		s = str(cfg.uid.shape_name_combo.currentText())
		cfg.shpLay = cfg.utls.selectLayerbyName(s)
		cfg.trnLay = s 
		# set the training layer for classification
		if cfg.shpLay is not "":
			self.ROIListTable(cfg.trnLay, cfg.uid.ROI_tableWidget)
			self.ROIScatterPlotListTable(cfg.trnLay, cfg.uiscp.scatter_list_plot_tableWidget)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi shapefile: " + str(s))
		
	# Create new shapefile 
	def createShapefile(self):
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> create shapefile click")
		try:
			if cfg.rstrNm is not None:
				sF = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save shapefile"), "", "Shapefile (*.shp)")
				try:
					# band set
					if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
						iB = len(cfg.bndSet)
						# crs of loaded raster
						b = cfg.utls.selectLayerbyName(cfg.bndSet[0])
						crs = cfg.utls.getCrs(b)
					else:
						# crs of loaded raster
						crs = cfg.utls.getCrs(cfg.rLay)
						iB = cfg.rLay.bandCount()
					f = QgsFields()
					# add Class ID, macroclass ID and Info fields
					f.append(QgsField(cfg.fldMacroID_class, QVariant.Int))
					f.append(QgsField(cfg.fldROIMC_info, QVariant.String))
					f.append(QgsField(cfg.fldID_class, QVariant.Int))
					f.append(QgsField(cfg.fldROI_info, QVariant.String))
					QgsVectorFileWriter(unicode(sF), "CP1250", f, QGis.WKBPolygon, crs, "ESRI Shapefile")
					# refresh shape list
					sN = os.path.basename(unicode(sF))
					if unicode(sF).endswith(".shp"):
						sL = cfg.utls.addVectorLayer(unicode(sF), sN, "ogr")
						cfg.utls.addLayerToMap(sL)
					else:
						sL = cfg.utls.addVectorLayer(unicode(sF) + ".shp", sN, "ogr")
						cfg.utls.addLayerToMap(sL)
					self.refreshShapeLayer()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< shapefile created: " + "\"" + unicode(sF) + "\"")
				except Exception, err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					self.refreshRasterLayer()
					cfg.mx.msg4()
			else:
				cfg.mx.msg4()
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< create shapefile fail: no raster")
				self.refreshRasterLayer()
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg4()

	def createROI(self, point, progressbar = "Yes"):
		if cfg.rstrNm is None:
			cfg.mx.msg4()
			cfg.pntROI = None
		elif cfg.scipyCheck == "No":
			if str(os.name) == "nt":
				cfg.mx.msgWar2Windows()
			else:
				cfg.mx.msgWar2Linux()
			cfg.pntROI = None
		elif cfg.utls.selectLayerbyName(cfg.rstrNm) is None:
			# if band set then pass
			if cfg.rstrNm == cfg.bndSetNm:
				pass
			else:
				cfg.mx.msg4()
				self.refreshRasterLayer()
				cfg.pntROI = None
		if cfg.pntROI != None:
			if progressbar == "Yes":
				cfg.uiUtls.addProgressBar()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> ROI click")
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(10)
			# ROI date time for temp name
			dT = cfg.utls.getTime()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "point (X,Y) = (%s,%s)" % (cfg.pntROI.x() , cfg.pntROI.y()))
			# disable map canvas render for speed (not in QGIS 1.8)
			cfg.cnvs.setRenderFlag(False)
			# temp files
			tRN = cfg.subsTmpROI + dT + ".tif"
			tSN = cfg.subsTmpROI + dT + ".shp"
			tR = str(cfg.tmpDir + "//" + tRN)
			tS = str(cfg.tmpDir + "//" + tSN)
			# subprocess bands
			dBs = {}
			dBSP = {}
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(20)
			# band set
			if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
				if cfg.rpdROICheck == "No":
					# subset and stack layers to tR
					for b in range(0, len(cfg.bndSet)):
						tmpSubset = str(cfg.tmpDir + "//" + "subset_temp_b_" + str(b) + "_" + dT + ".tif")
						dBs["BANDS_{0}".format(b)] = str(cfg.tmpDir + "//" + "subset_temp_b_" + str(b) + "_" + dT + ".tif")
						dBSP["BAND_SUBPROCESS_{0}".format(b)] = cfg.utls.subsetImage(cfg.bndSet[b], point.x(), point.y(), float(cfg.maxROIWdth), float(cfg.maxROIWdth), tmpSubset)
						if dBSP["BAND_SUBPROCESS_{0}".format(b)] == "Yes":
							cfg.mx.msgErr29()
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation, edge point")
							cfg.pntROI = None
							if progressbar == "Yes":
								cfg.uiUtls.removeProgressBar()
							return dBSP["BAND_SUBPROCESS_{0}".format(b)]
				else:
					try:
						b = int(cfg.ROIband) - 1
						pr = cfg.utls.subsetImage(cfg.bndSet[b], point.x(), point.y(), int(cfg.maxROIWdth), int(cfg.maxROIWdth), tR)
						if pr == "Yes":
							cfg.mx.msgErr29()
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation, edge point")
							cfg.pntROI = None
							if progressbar == "Yes":
								cfg.uiUtls.removeProgressBar()
							return pr
						dBs["BANDS_{0}".format(b)] = tR
					except Exception, err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.mx.msgErr7
			else:
				if cfg.rpdROICheck == "No":
					# subset image
					pr = cfg.utls.subsetImage(cfg.rstrNm, point.x(), point.y(), int(cfg.maxROIWdth), int(cfg.maxROIWdth), tR)
					if pr == "Yes":
						cfg.mx.msgErr29()
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation, edge point")
						cfg.pntROI = None
						if progressbar == "Yes":
							cfg.uiUtls.removeProgressBar()
						return pr
					dBs["BANDS_{0}".format(1)] = tR
				else:
					try:
						# temp files
						tRN2 = cfg.copyTmpROI + dT + ".tif"
						tR2 = str(cfg.tmpDir + "//" + tRN2)
						# subset image
						pr = cfg.utls.subsetImage(cfg.rstrNm, point.x(), point.y(), int(cfg.maxROIWdth), int(cfg.maxROIWdth), tR2)
						if pr == "Yes":
							cfg.mx.msgErr29()
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation, edge point")
							cfg.pntROI = None
							if progressbar == "Yes":
								cfg.uiUtls.removeProgressBar()
							return pr
						cfg.utls.getRasterBandByBandNumber(tR2, int(cfg.ROIband), tR)
						dBs["BANDS_{0}".format(1)] = tR
					except Exception, err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.mx.msgErr7
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(40)
			# run segmentation
			self.regionGrowing(dBs, point.x(), point.y(), cfg.rngRad, int(cfg.minROISz), tS)
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "output segmentation: " + str(tSN))
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(60)
			tSS = cfg.utls.addVectorLayer(tS, tSN, "ogr")
			# check if segmentation went wrong
			if tSS is None:
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation")
				cfg.pntROI = None
				if progressbar == "Yes":
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr2()
			else:
				cfg.lgnd.setLayerVisible(tSS, False)
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(70)
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "temp roi saved in " + str(tS))
				# semitransparent symbol and line for ROI
				rT = cfg.ROITrnspVal * 255 / 100
				rC = str(QColor(cfg.ROIClrVal).red()) + "," + str(QColor(cfg.ROIClrVal).green()) + "," + str(QColor(cfg.ROIClrVal).blue()) + "," + str(rT) 
				sP = { 'color' : rC , 'color_border' : '0,255,255,50', 'offset' : '0,0', 'style' : 'solid', 'style_border' : 'dot', 'width_border' : '0.4' }
				sL = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SimpleFill").createSymbolLayer(sP)
				# apply symbology
				tSS.setRendererV2(QgsSingleSymbolRendererV2(QgsFillSymbolV2([sL])))
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(70)
				# workaround for setRendererV2 crash
				lS = tSS.rendererV2().symbols()
				fS = lS[0]
				fS.appendSymbolLayer(sL)
				# add ROI layer
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(90)
				cfg.utls.addLayerToMap(tSS)
				# create temp group
				cfg.lstROI = tSS
				g = cfg.utls.groupIndex(cfg.grpNm)
				if g is None:
					g = cfg.lgnd.addGroup(cfg.grpNm, False) 
					cfg.lgnd.moveLayer (cfg.lstROI, g)
				else:
					cfg.lgnd.moveLayer (cfg.lstROI, g)
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(100)
				cfg.uid.button_Save_ROI.setEnabled(True)
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< ROI created: " + str(tSS.name()))
				# enable Redo button
				cfg.uid.redo_ROI_Button.setEnabled(True)
				if progressbar == "Yes":
					cfg.uiUtls.removeProgressBar()
			
	# region growing
	def regionGrowing(self, rasterDictionary, seedX, seedY, spectralRange, minimumSize, outputVector):
		gdal.AllRegister()
		tD = gdal.GetDriverByName( "GTiff" )
		itRs = iter(rasterDictionary)
		iR = str(rasterDictionary[next(itRs)])
		# open input with GDAL
		rD = gdal.Open(iR, GA_ReadOnly)
		# number of x pixels
		rX = rD.RasterXSize
		# number of y pixels
		rY = rD.RasterYSize
		# check projections
		rP = rD.GetProjection()
		# pixel size and origin
		rGT = rD.GetGeoTransform()
		UX = abs(rGT[0])
		UY = abs(rGT[3])
		xSz = rD.RasterXSize
		ySz = rD.RasterYSize
		# seed pixel number
		sPX = xSz / 2
		sPY = ySz / 2
		# create a shapefile
		d = ogr.GetDriverByName('ESRI Shapefile')
		# use ogr
		if d is not None:
			dS = d.CreateDataSource(outputVector)
			if dS is None:
				# close rasters
				rD = None
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "region growing failed: " + str(outputVector))
			else:
				# shapefile
				sR = osr.SpatialReference()
				sR.ImportFromWkt(rD.GetProjectionRef())
				rL = dS.CreateLayer('ROILayer', sR, ogr.wkbPolygon)
				fN = "DN"
				fd = ogr.FieldDefn(fN, ogr.OFTInteger)
				rL.CreateField(fd)
				fld = rL.GetLayerDefn().GetFieldIndex(fN)
				# prepare output raster
				dT = cfg.utls.getTime()
				tRN = cfg.tmpRegionNm + dT + ".tif"
				tR = str(cfg.tmpDir + "//" + tRN)
				iRB = rD.GetRasterBand(1)
				dtTp = iRB.DataType
				rR = tD.Create(tR, rX, rY, 1, dtTp)
				rR.SetGeoTransform( [ rGT[0] , rGT[1] , 0 , rGT[3] , 0 , rGT[5] ] )
				rR.SetProjection(rP)
				rRB = rR.GetRasterBand(1)
				rRB.SetNoDataValue(0)
				# input array
				aB =  iRB.ReadAsArray()
				# region growing alg
				r = self.regionGrowingAlg(aB, sPX, sPY, spectralRange, minimumSize)
				if len(rasterDictionary) > 1:
					for raster in itRs:
						iR = str(rasterDictionary[raster])
						# open input with GDAL
						rD = gdal.Open(iR, GA_ReadOnly)
						iRB = rD.GetRasterBand(1)
						# input array
						aB =  iRB.ReadAsArray()
						# region growing alg
						nR = self.regionGrowingAlg(aB, sPX, sPY, spectralRange, minimumSize)
						r = r * nR
					lR2, nF2 = label(r)
					# value of ROI seed
					rSV = lR2[sPX,sPX]
					r = rSV == lR2
				if cfg.bndSetPresent != "Yes" and cfg.rpdROICheck == "No":
					bN = rD.RasterCount
					for i in range(2, bN + 1):
						iRB = rD.GetRasterBand(i)
						# input array
						aB =  iRB.ReadAsArray()
						# region growing alg
						nR = self.regionGrowingAlg(aB, sPX, sPY, spectralRange, minimumSize)
						r = r * nR
					lR2, nF2 = label(r)
					# value of ROI seed
					rSV = lR2[sPX,sPX]
					r = rSV == lR2
				# write array
				rRB.WriteArray(r)
				# raster to polygon
				gdal.Polygonize(rRB, rRB.GetMaskBand(), rL, fld)
				# close bands
				rRB = None
				# close rasters
				rR = None
				rD = None
				dS = None
				rL = None
				d = None
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "region growing completed: " + str(iR) + " " + str(spectralRange))
		else:
			# possibly ogr driver is missinig
			cfg.mx.msgErr27()
			
	# region growing algorithm of an array and a seed
	def regionGrowingAlg(self, array, seedX, seedY, spectralRange, minimumSize):
		sA = np.zeros(array.shape)
		sA.fill(array[seedX, seedY])
		# no data mask
		m = -9999 == array
		m = m * (-1)
		# difference array
		dA = abs(array - sA)
		# calculate minimum difference
		uDA = np.unique(dA)
		# if ROI on no data
		if uDA.all() == 0:
			mD = 0
		else:
			mD = int(uDA[1] - uDA[0])
		if spectralRange < mD:
			spectralRange = mD
		# distance array
		dstA = (dA / float(spectralRange)).astype(int)
		uDstA = np.unique(dstA)
		for i in uDstA:
			iA = (dstA < i)
			rL, num_features = label(iA)
			# value of ROI seed
			rV = rL[seedX,seedY]
			if rV != 0:
				rS = (rL == rV).sum()
				if rS >= minimumSize:
					break
		r = rV == rL
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " region growing seed: " + str(seedX) + ";" + str(seedY))
		return r
			
	# Save last ROI to shapefile 
	def saveROItoShapefile(self, progressbar = "Yes"):
		if progressbar is False:
			progressbar = "Yes"
		# check if layer was removed ## there is an issue if the removed layer was already saved in the project ##
		try:
			sN = str(cfg.shpLay.name())
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg3()
			self.refreshShapeLayer()
		# check if no layer is selected
		if cfg.shpLay is None:
			cfg.mx.msg3()
		# check if no ROI created
		elif cfg.lstROI is None:
			cfg.mx.msg6()
		else:
			if progressbar == "Yes":
				cfg.uiUtls.addProgressBar()
				cfg.uiUtls.updateBar(10)
			# get polygon from ROI
			try:
				# region growing ROI
				cfg.utls.copyFeatureToLayer(cfg.lstROI, 0, cfg.shpLay)
			except:
				# manual ROI
				cfg.utls.copyFeatureToLayer(cfg.lstROI, 1, cfg.shpLay)
			self.ROILastID = cfg.utls.getLastFeatureID(cfg.shpLay)
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(30)
			tW = cfg.uid.ROI_tableWidget
			tW.blockSignals(True)
			try:
				# start editing
				cfg.shpLay.startEditing()
				# set ID class attribute
				fdID = cfg.utls.fieldID(cfg.shpLay, str(cfg.fldID_class))
				cfg.shpLay.changeAttributeValue(self.ROILastID, fdID, cfg.ROIID)
				# set macroclass ID attribute
				fdMID = cfg.utls.fieldID(cfg.shpLay, str(cfg.fldMacroID_class))
				cfg.shpLay.changeAttributeValue(self.ROILastID, fdMID, cfg.ROIMacroID)
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.shpLay.startEditing()	
				cfg.shpLay.dataProvider().deleteFeatures([self.ROILastID])
				cfg.shpLay.commitChanges()
				cfg.shpLay.dataProvider().createSpatialIndex()
				cfg.uid.undo_save_Button.setEnabled(False)
				a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Add required fds"), QApplication.translate("semiautomaticclassificationplugin", "It appears that the shapefile ") + cfg.shpLay.name() + QApplication.translate("semiautomaticclassificationplugin", " is missing some fields that are required for the signature calculation. \nDo you want to add the required fields to this shapefile?"))
				if a == "Yes":
					fds = []
					fds.append(QgsField(cfg.fldMacroID_class, QVariant.Int))	
					cfg.shpLay.startEditing()
					aF = cfg.shpLay.dataProvider().addAttributes(fds)
					# commit changes
					cfg.shpLay.commitChanges()
					if progressbar == "Yes":
						cfg.uiUtls.removeProgressBar()
					return 1
				else:
					if progressbar == "Yes":
						cfg.uiUtls.removeProgressBar()
					return 0
			# set ROI Class info attribute
			fdInfo = cfg.utls.fieldID(cfg.shpLay, str(cfg.fldROI_info))
			cfg.shpLay.changeAttributeValue(self.ROILastID, fdInfo, cfg.ROIInfo)
			# set ROI Macroclass info attribute
			fdMCInfo = cfg.utls.fieldID(cfg.shpLay, str(cfg.fldROIMC_info))
			cfg.shpLay.changeAttributeValue(self.ROILastID, fdMCInfo, cfg.ROIMacroClassInfo)
			# commit changes
			cfg.shpLay.commitChanges()
			cfg.uid.undo_save_Button.setEnabled(True)
			cfg.ROITabEdited == "No"
			self.ROIListTable(cfg.trnLay, cfg.uid.ROI_tableWidget)
			self.ROIScatterPlotListTable(cfg.trnLay, cfg.uiscp.scatter_list_plot_tableWidget)
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(40)
			tW.blockSignals(False)
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi: " + str(cfg.ROIID) + ", " + str(cfg.ROIInfo) + " saved to shapefile: " + str(cfg.shpLay.name()))
			# calculate signature if checkbox is yes
			if cfg.uid.signature_checkBox.isChecked() is True:
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(50)
					self.calculateSignature(cfg.shpLay, cfg.rstrNm, [self.ROILastID], cfg.ROIMacroID, cfg.ROIMacroClassInfo, cfg.ROIID, cfg.ROIInfo, 50, 40)
				else:
					self.calculateSignature(cfg.shpLay, cfg.rstrNm, [self.ROILastID], cfg.ROIMacroID, cfg.ROIMacroClassInfo, cfg.ROIID, cfg.ROIInfo)
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(90)
				cfg.classD.signatureListTable(cfg.uidc.signature_list_tableWidget)
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(100)
				cfg.uiUtls.removeProgressBar()
		
	# Create ROI list
	def ROIListTable(self, layerName, table, checkstate=0):
		# get ROIs
		self.getROIAttributes(layerName)
		# checklist
		l = table
		l.setSortingEnabled(False)
		cfg.utls.clearTable(l)
		# add ROI items
		for b in range(0, len(cfg.ROI_C_ID)):
			l.insertRow(b)
			l.setRowHeight(b, 20)
			for key, id in cfg.ROI_Count.iteritems():
				if str(id) == str(b):
					k = key
			cfg.ROITabEdited = "No"
			itMID = QTableWidgetItem()
			itMID.setData(Qt.DisplayRole, int(cfg.ROI_MC_ID[k]))
			l.setItem(b, 0, itMID)
			l.setItem(b, 1, QTableWidgetItem(str(cfg.ROI_MC_Info[k])))
			itID = QTableWidgetItem()
			itID.setData(Qt.DisplayRole, int(cfg.ROI_C_ID[k]))
			l.setItem(b, 2, itID)
			l.setItem(b, 3, QTableWidgetItem(str(cfg.ROI_C_Info[k])))
			l.setItem(b, 4, QTableWidgetItem(str(cfg.ROI_ShapeID[k])))
		l.show()
		l.setColumnWidth(0, 40)
		l.setColumnWidth(2, 40)
		l.setSortingEnabled(True)
		cfg.ROITabEdited = "Yes"
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " roi list table created")

	# Create ROI list for scatter plot
	def ROIScatterPlotListTable(self, layerName, table, checkstate=0):
		# get ROIs
		self.getROIAttributes(layerName)
		# checklist
		l = table
		l.setSortingEnabled(False)
		cfg.utls.clearTable(l)
		# add ROI items
		for b in range(0, len(cfg.ROI_C_ID)):
			l.insertRow(b)
			l.setRowHeight(b, 20)
			for key, id in cfg.ROI_Count.iteritems():
				if str(id) == str(b):
					k = key
			cfg.ROITabEdited = "No"
			cb = QTableWidgetItem("checkbox")
			cb.setCheckState(checkstate)
			l.setItem(b, 0, cb)
			itMID = QTableWidgetItem()
			itMID.setData(Qt.DisplayRole, int(cfg.ROI_MC_ID[k]))
			l.setItem(b, 1, itMID)
			l.setItem(b, 2, QTableWidgetItem(str(cfg.ROI_MC_Info[k])))
			itID = QTableWidgetItem()
			itID.setData(Qt.DisplayRole, int(cfg.ROI_C_ID[k]))
			l.setItem(b, 3, itID)
			l.setItem(b, 4, QTableWidgetItem(str(cfg.ROI_C_Info[k])))
			l.setItem(b, 5, QTableWidgetItem(""))
			c, cc = cfg.utls.randomColor()
			l.item(b, 5).setBackground(c)
			l.setItem(b, 6, QTableWidgetItem(str(cfg.ROI_ShapeID[k])))
		l.show()
		l.setColumnWidth(0, 40)
		l.setColumnWidth(2, 40)
		l.setSortingEnabled(True)
		cfg.ROITabEdited = "Yes"
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " roi list table created")
		
	def deleteSelectedROIs(self):
		tW = cfg.uid.ROI_tableWidget
		# ask for confirm
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Delete ROIs"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to delete highlighted ROIs?"))
		if a == "Yes":
			tW.blockSignals(True)
			ids = []
			for i in tW.selectedIndexes():
				id = int(cfg.uid.ROI_tableWidget.item(i.row(), 4).text())
				ids.append(id)
			cfg.utls.deleteFeatureShapefile(cfg.shpLay, ids)
			self.ROIListTable(cfg.trnLay, cfg.uid.ROI_tableWidget)
			self.ROIScatterPlotListTable(cfg.trnLay, cfg.uiscp.scatter_list_plot_tableWidget)
			cfg.uid.undo_save_Button.setEnabled(False)
			tW.blockSignals(False)
		cfg.cnvs.refresh()	
		
	# add signature to list
	def addSelectedROIsToSignature(self, plot = "No"):
		tW = cfg.uid.ROI_tableWidget
		r = []
		for i in tW.selectedIndexes():
			r.append(i.row())
		if len(r) > 0:
			v = list(set(r))
			progresStep = 100 / len(v)
			cfg.uiUtls.addProgressBar()
			lst = []
			# find ROI values
			for x in v:
				id = int(cfg.uid.ROI_tableWidget.item(x, 4).text())
				mcID = int(cfg.uid.ROI_tableWidget.item(x, 0).text())
				mcI = cfg.uid.ROI_tableWidget.item(x, 1).text()
				cID = int(cfg.uid.ROI_tableWidget.item(x, 2).text())
				cI = cfg.uid.ROI_tableWidget.item(x, 3).text()
				lst.append([str(mcID) + "-" + str(cID), id, mcID, mcI, cID, cI])
			# find ROI with same class ID and macroclass ID
			m = []
			e = []
			for c in lst:
				r = [it for it,n in enumerate(lst) if n[0] == c[0]]
				if r not in m:
					m.append(r)
					IDs = []
					for n in r:
						IDs.append(lst[n][1])
					e.append([IDs, c[2], c[3], c[4], c[5]])
			# calculate signature for ROI with the same class ID and macroclass ID
			n = 1
			for s in e:
				progress = n * progresStep
				self.calculateSignature(cfg.shpLay, cfg.rstrNm, s[0], s[1], s[2], s[3], s[4], progress, progresStep, plot)
				n = n + 1
			cfg.uiUtls.removeProgressBar()
			if plot == "No":
				cfg.classD.signatureListTable(cfg.uidc.signature_list_tableWidget)
			elif plot == "Yes":
				cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			
	# add ROI signature to plot
	def addSelectedROIsToSignaturePlot(self):
		self.addSelectedROIsToSignature("Yes")
		cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
		cfg.spectralplotdlg.close()
		cfg.spectralplotdlg.show()
		
	# add ROI signature to list
	def addSelectedROIsToSignatureList(self):
		self.addSelectedROIsToSignature("No")
		
	# get all ROI attributes
	def getROIAttributes(self, layerName):
		l = cfg.utls.selectLayerbyName(layerName)
		cfg.ROI_MC_ID = {}
		cfg.ROI_MC_Info = {}
		cfg.ROI_C_ID = {}
		cfg.ROI_C_Info = {}
		cfg.ROI_Count = {}
		cfg.ROI_ShapeID = {}
		if l is not None:
			i = 0
			for f in l.getFeatures():
				id = f.id()
				try:
					cfg.ROI_MC_ID[id]= str(f[cfg.fldMacroID_class])
					cfg.ROI_MC_Info[id] = str(f[cfg.fldROIMC_info])
					cfg.ROI_C_ID[id] = str(f[cfg.fldID_class])
					cfg.ROI_C_Info[id] = str(f[cfg.fldROI_info])
					cfg.ROI_Count[id]= str(i)
					cfg.ROI_ShapeID[id]= str(id)
				except Exception, err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.mx.msg3()
				i = i + 1
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ROI attributes")
		
	# zoom to clicked ROI 
	def zoomToROI(self, index):
		l = cfg.utls.selectLayerbyName(cfg.trnLay)
		l.removeSelection()
		id = int(cfg.uid.ROI_tableWidget.item(index.row(), 4).text())
		l.select(id)
		cfg.cnvs.zoomToSelected(l)
		l.deselect(id)
		
	def editedCell(self, row, column):
		tW = cfg.uid.ROI_tableWidget
		if cfg.ROITabEdited == "Yes":
			tW.blockSignals(True)
			l = cfg.utls.selectLayerbyName(cfg.trnLay)
			v = tW.item(row, column).text()
			id = int(tW.item(row, 4).text())
			f = None
			if column == 0:
				try:
					cfg.ROI_MC_ID[id] = int(v)
					v = int(v)
					f = cfg.fldMacroID_class
				except:
					tW.setItem(row, column, QTableWidgetItem(str(cfg.ROI_MC_ID[id])))
			elif column == 1:
				cfg.ROI_MC_Info[id] = str(v)
				v = str(v)
				f = cfg.fldROIMC_info
			elif column == 2:
				try:
					cfg.ROI_C_ID[id] = int(v)
					v = int(v)
					f = cfg.fldID_class
				except:
					tW.setItem(row, column, QTableWidgetItem(str(cfg.ROI_C_ID[id])))
			elif column == 3:
				cfg.ROI_C_Info[id] = str(v)
				v = str(v)
				f = cfg.fldROI_info
			if f is not None:
				cfg.utls.editFeatureShapefile(l, id, str(f), v)
			tW.blockSignals(False)
		cfg.ROITabEdited = "No"
		# refresh and set the same layer
		layer = cfg.trnLay
		tW.blockSignals(True)
		self.refreshShapeLayer()
		id = cfg.uid.shape_name_combo.findText(layer)
		cfg.uid.shape_name_combo.setCurrentIndex(id)
		tW.blockSignals(False)
		
	# calculate ROI signature (one signature for ROIs that have the same macroclass ID and class ID)
	def calculateSignature(self, lyr, rasterName, featureIDList, macroclassID, macroclassInfo, classID, classInfo, progress = None, progresStep = None, plot = "No"):
		if rasterName is not None and len(rasterName) > 0:
			if progress is not None:
				cfg.uiUtls.updateBar(progress + int((1 / 4) * progresStep))
			else:
				#cfg.uiUtls.updateBar(0)
				pass
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			# date time for temp name
			dT = cfg.utls.getTime()
			# temp subset
			tSN = cfg.subsROINm
			tSD = cfg.tmpDir + "/" + dT + tSN
			# temporary layer
			tLN = cfg.subsTmpROI + dT + ".shp"
			tLP = cfg.tmpDir + "/" + dT + tLN
			# get layer crs
			crs = cfg.utls.getCrs(lyr)
			# create a temp shapefile with a field
			cfg.utls.createEmptyShapefileQGIS(crs, tLP)
			mL = cfg.utls.addVectorLayer(tLP , tLN, "ogr")
			rD = None
			for x in featureIDList:
				# copy ROI to temp shapefile
				cfg.utls.copyFeatureToLayer(lyr, x, mL)
			# calculate ROI center, height and width
			rCX, rCY, rW, rH = cfg.utls.getShapefileRectangleBox(lyr)
			if progress is not None:
				cfg.uiUtls.updateBar(progress + int((2 / 4) * progresStep))
			cfg.tblOut = {}
			ROIArray = []
			# band set
			if cfg.bndSetPresent == "Yes" and rasterName == cfg.bndSetNm:
				tLX, tLY, pS = cfg.utls.imageInformation(cfg.bndSet[0])
				cfg.bndSetLst = ""
				# subset 
				for b in range(0, len(cfg.bndSet)):
					tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + str(b) + "_" + dT + ".tif")
					pr = cfg.utls.subsetImage(cfg.bndSet[b], rCX, rCY, rW/pS + 3,  rH/pS + 3, tS)
					if pr == "Yes":
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error edge")
						return pr
					bX = cfg.utls.clipRasterByShapefile(tLP, tS)
					rStat, ar = cfg.utls.getRasterBandStatistics(bX, 1)
					rStatStr = str(rStat)
					rStatStr = rStatStr.replace("nan", "0")
					rStat = eval(rStatStr)
					ROIArray.append(ar)
					cfg.bndSetLst = cfg.bndSetLst + str(tS) + ";"
					cfg.tblOut["BAND_{0}".format(b+1)] = rStat
					cfg.tblOut["WAVELENGTH_{0}".format(b + 1)] = cfg.bndSetWvLn["WAVELENGTH_{0}".format(b + 1)]
				cfg.bndSetLst = cfg.bndSetLst.rstrip(';')
			else:
				# subset 
				tLX, tLY, pS = cfg.utls.imageInformation(rasterName)
				tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + dT + ".tif")
				pr = cfg.utls.subsetImage(rasterName, rCX, rCY, rW/pS + 3 , rH/pS + 3, str(tS))
				if pr == "Yes":
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error edge")
					return pr
				bX = cfg.utls.clipRasterByShapefile(tLP, tS)
				rL = cfg.utls.selectLayerbyName(rasterName)
				bCount = rL.bandCount()	
				for b in range(1, bCount + 1):
					rStat, ar = cfg.utls.getRasterBandStatistics(bX, b)
					rStatStr = str(rStat)
					rStatStr = rStatStr.replace("nan", "0")
					rStat = eval(rStatStr)
					ROIArray.append(ar)
					cfg.tblOut["BAND_{0}".format(b)] = rStat
					cfg.tblOut["WAVELENGTH_{0}".format(b)] = cfg.bndSetWvLn["WAVELENGTH_{0}".format(b)] 
			if progress is not None:
				cfg.uiUtls.updateBar(progress + int((3 / 4) * progresStep))
			covMat = cfg.utls.calculateCovMatrix(ROIArray)
			if covMat == "No":
				cfg.mx.msgWar12(macroclassID, classID)
			# remove temp layers
			cfg.utls.removeLayer(tLN)
			self.ROIStatisticsToSignature(covMat, macroclassID, macroclassInfo, classID, classInfo, cfg.bndSetUnit["UNIT"], plot)
			# enable map canvas render
			cfg.cnvs.setRenderFlag(True)
			if progress is not None:
				cfg.uiUtls.updateBar(progress + int((4 / 4) * progresStep))
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi signature calculated")
		else:
			cfg.mx.msg3()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi signature not calculated")
			
	# delete last saved ROI
	def undoSaveROI(self):
		# check if layer was removed ## there is an issue if the removed layer was already saved in the project ##
		try:
			s = str(cfg.shpLay.name())
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg3()
			self.refreshShapeLayer()
		# check if no layer is selected
		if cfg.shpLay is None:
			cfg.mx.msg3()
		# check if no ROI created
		elif cfg.lstROI is None:
			cfg.mx.msg6()
		else:
			# ask for confirm
			a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Undo save ROI"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to delete the last saved ROI?"))
			if a == "Yes":
				cfg.utls.deleteFeatureShapefile(cfg.shpLay, [self.ROILastID])
				cfg.uid.undo_save_Button.setEnabled(False)
				self.ROIListTable(cfg.trnLay, cfg.uid.ROI_tableWidget)
				self.ROIScatterPlotListTable(cfg.trnLay, cfg.uiscp.scatter_list_plot_tableWidget)
				cfg.cnvs.refresh()
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi deleted: " + str(self.ROILastID))
			
	# create a ROI in the same point
	def redoROI(self):
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> REDO ROI creation")
		# check if other processes are active
		if cfg.actionCheck == "No":
			if cfg.pntROI is None:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "REDO ROI fail: no point")
				pass
			else:
				self.createROI(cfg.pntROI)
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile("redoROI " + cfg.utls.lineOfCode(), "<<< REDO ROI creation")
				
	# Activate rapid ROI creation
	def rapidROICheckbox(self):
		if cfg.uid.rapid_ROI_checkBox.isChecked() is True:
			cfg.rpdROICheck = "Yes"
		else:
			cfg.rpdROICheck = "No"
		cfg.utls.writeProjectVariable("rapidROI", cfg.rpdROICheck)
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.rpdROICheck))
	
	# set rapid ROI band
	def rapidROIband(self):
		# band set
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			iB = len(cfg.bndSet)
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm)
			try:
				iB = i.bandCount()
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				iB = 1
		if cfg.uid.rapidROI_band_spinBox.value() > iB:
			cfg.uid.rapidROI_band_spinBox.setValue(iB)
		cfg.ROIband = cfg.uid.rapidROI_band_spinBox.value()
		cfg.utls.writeProjectVariable("rapidROIBand", str(cfg.ROIband))
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "ROI band: " + str(cfg.ROIband))
		
	# refresh shape and training list	
	def refreshShapeLayer(self):
		lL = cfg.lgnd.layers()
		cfg.uid.shape_name_combo.clear()
		# shape layer
		cfg.shpLay = None
		# training layer
		cfg.trnLay = None
		for sL in lL:
			if (sL.type()==QgsMapLayer.VectorLayer):
				if (sL.geometryType() == QGis.Polygon):
					# filter if shapefile has ID_class and ROI_info fields
					f = sL.dataProvider().fields()
					if f.indexFromName(str(cfg.fldID_class)) > -1:
						if f.indexFromName(str(cfg.fldROI_info)) > -1:
							if f.indexFromName(str(cfg.fldMacroID_class)) > -1:
								if f.indexFromName(str(cfg.fldROIMC_info)) > -1:
									cfg.dockdlg.shape_layer_combo(sL.name())
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "shape layers refreshed")
		
	# Get values for ROI signature
	def ROIStatisticsToSignature(self, covarianceMatrix, macroclassID, macroclassInfo, classID, classInfo, unit = None, plot = "No"):
		if cfg.rstrNm is not None:
			# band set
			if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
				iB = len(cfg.bndSet)
			else:
				i = cfg.utls.selectLayerbyName(cfg.rstrNm)
				iB = i.bandCount()
			wvl = []
			val = []
			for b in range(1, iB + 1):
				stats = cfg.tblOut["BAND_" + str(b)]
				w = cfg.tblOut["WAVELENGTH_" + str(b)] 
				wvl.append(w)
				# values for mean and standard deviation
				vM = stats[2]
				vS = stats[3]
				val.append(vM)
				val.append(vS)
				c, cc = cfg.utls.randomColor()
			if plot == "No":
				i = self.signatureID()
				cfg.signList["CHECKBOX_{0}".format(i)] = Qt.Checked
				cfg.signList["MACROCLASSID_{0}".format(i)] = macroclassID
				cfg.signList["MACROCLASSINFO_{0}".format(i)] = macroclassInfo
				cfg.signList["CLASSID_{0}".format(i)] = classID
				cfg.signList["CLASSINFO_{0}".format(i)] = classInfo
				cfg.signList["WAVELENGTH_{0}".format(i)] = wvl
				cfg.signList["VALUES_{0}".format(i)] = val
				cfg.signList["COVMATRIX_{0}".format(i)] = covarianceMatrix
				if unit is None:
					unit = cfg.bndSetUnit["UNIT"]
				cfg.signList["UNIT_{0}".format(i)] = unit
				cfg.signList["COLOR_{0}".format(i)] = c
				#cfg.signList["COMPL_COLOR_{0}".format(i)] = cc
				cfg.signIDs["ID_{0}".format(i)] = i
			# calculation for plot
			elif plot == "Yes":
				i = cfg.spSigPlot.signaturePlotID()
				cfg.spectrPlotList["CHECKBOX_{0}".format(i)] = Qt.Checked
				cfg.spectrPlotList["MACROCLASSID_{0}".format(i)] = macroclassID
				cfg.spectrPlotList["MACROCLASSINFO_{0}".format(i)] = macroclassInfo
				cfg.spectrPlotList["CLASSID_{0}".format(i)] = classID
				cfg.spectrPlotList["CLASSINFO_{0}".format(i)] = classInfo
				cfg.spectrPlotList["WAVELENGTH_{0}".format(i)] = wvl
				cfg.spectrPlotList["VALUES_{0}".format(i)] = val
				if unit is None:
					unit = cfg.bndSetUnit["UNIT"]
				cfg.spectrPlotList["UNIT_{0}".format(i)] = unit
				cfg.spectrPlotList["COLOR_{0}".format(i)] = c
				#cfg.spectrPlotList["COMPL_COLOR_{0}".format(i)] = cc
				cfg.signPlotIDs["ID_{0}".format(i)] = i
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " values to shape concluded, plot: " + str(plot))
	
	def signatureID(self):
		i = 1
		if len(cfg.signIDs.values()) > 0:
			while i in cfg.signIDs.values():
				i = i + 1
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID" + str(i))
		return i
		
	# Activate signature calculation
	def signatureCheckbox(self):
		if cfg.uid.signature_checkBox.isChecked() is True:
			cfg.sigClcCheck = "Yes"
			cfg.ui.signature_checkBox2.setCheckState(2)
		else:
			cfg.sigClcCheck = "No"
			cfg.ui.signature_checkBox2.setCheckState(0)
		cfg.utls.writeProjectVariable("calculateSignature", cfg.sigClcCheck)
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.sigClcCheck))