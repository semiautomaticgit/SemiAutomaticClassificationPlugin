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
import subprocess
import sys
# for debugging
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from osgeo import gdal
from osgeo.gdalconst import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class ClipMultipleRasters:

	def __init__(self):
		# emit a QgsPoint on each click
		self.clickUL = QgsMapToolEmitPoint(cfg.cnvs)
		# connect to pointerClick when map is clicked
		self.clickUL.canvasClicked.connect(self.pointerClickUL)
		# emit a QgsPoint on each click
		self.clickLR = QgsMapToolEmitPoint(cfg.cnvs)
		# connect to pointerClick when map is clicked
		self.clickLR.canvasClicked.connect(self.pointerClickLR)
		
	# add rubber band
	def addRubberBandPolygon(self, pointUL, pointLR):
		try:
			self.clearCanvasPoly()
		except:
			pass
		self.rbbrBndPol = QgsRubberBand(cfg.cnvs, 2)
		rectangle = [[pointUL, QgsPoint(pointLR.x(), pointUL.y()), pointLR, QgsPoint(pointUL.x(), pointLR.y())]]
		self.rbbrBndPol.setToGeometry(QgsGeometry.fromPolygon(rectangle), None)
		clr = QColor(cfg.ROIClrVal)
		clr.setAlpha(50)
		try:
			# QGIS 2.6
			self.rbbrBndPol.setFillColor(clr)
			#self.rbbrBndPol.setBorderColor(QColor(cfg.ROIClrOutlineValDefault))
			#self.rbbrBndPol.setLineStyle(Qt.DotLine)
			self.rbbrBndPol.setWidth(3)
		except:
			# QGIS < 2.6
			self.rbbrBndPol.setColor(clr)
			#self.rbbrBndPol.setLineStyle(Qt.DotLine)
			self.rbbrBndPol.setWidth(3)
		
	# clear canvas
	def clearCanvasPoly(self):
		self.rbbrBndPol.reset(True)
		cfg.cnvs.refresh()	
		
	# set all bands to state 0 or 2
	def allRasterSetState(self, value):
		# checklist
		l = cfg.ui.raster_listView_2
		# count rows in checklist
		c = l.model().rowCount()
		for b in range(0, c):
			if cfg.actionCheck == "Yes":
				cfg.bndMdls.item(b).setCheckState(value)
				cfg.uiUtls.updateBar((b+1) * 100 / (c))
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all rasters cancelled")
		
	# clip multiple rasters
	def clipRasters(self):
		UX = ""
		UY = ""
		LX = ""
		LY = ""
		# creation of the required table of reclassification
		rT = []
		# st variable
		st = "No"
		# checklist
		lst = cfg.ui.raster_listView_2
		# count rows in checklist
		c = lst.model().rowCount()
		for x in range(0, c):
			# If checkbox is activated
			if cfg.bndMdls.item(x).checkState() == 2:
				# name of item of list
				itN = cfg.bndMdls.item(x).text()
				rT.append(itN)
		if len(rT) == 0:
			cfg.mx.msgWar15()
			return "No"
		oD = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Select a directory where to save clipped rasters"))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters to be clipped" + unicode(rT))
		if cfg.ui.shapefile_checkBox.isChecked() is True:
			# use shape
			uS = 1
			sN = cfg.ui.shapefile_comboBox.currentText()
			sL = cfg.utls.selectLayerbyName(sN)
			try:
				s = sL.source()
			except Exception, err:
				cfg.mx.msgErr11()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		else:
			uS = 0
		# No data value
		noDt = cfg.ui.nodata_spinBox.value()
		if len(oD) > 0:
			outputName = cfg.ui.output_clip_name_lineEdit.text()
			if len(outputName) > 0:
				outputName = str(outputName.encode('ascii','replace'))
			else:
				outputName = cfg.clipNm
			# no shapefile
			if uS == 0:
				try:
					self.clearCanvasPoly()
					UX = cfg.ui.UX_lineEdit.text()
					UY = cfg.ui.UY_lineEdit.text()
					LX = cfg.ui.LX_lineEdit.text()
					LY = cfg.ui.LY_lineEdit.text()
					UL = QgsPoint(float(UX), float(UY))
					LR = QgsPoint(float(LX), float(LY))
					ULP = cfg.utls.checkPointImage(rT[0], UL, "Yes")
					if str(cfg.pntCheck) == "No":
						cfg.mx.msgErr34()
						return "No"
					LRP = cfg.utls.checkPointImage(rT[0], LR, "Yes")
					if str(cfg.pntCheck) == "No":
						cfg.mx.msgErr34()
						return "No"
					UX = str(ULP.x())
					UY = str(ULP.y())
					LX = str(LRP.x())
					LY = str(LRP.y())
					if float(UX) > float(LX):
						UX = str(LRP.x())
						LX = str(ULP.x())
					if float(UY) < float(LY):
						UY = str(LRP.y())
						LY = str(ULP.y())
				except:
					pass
			cfg.uiUtls.addProgressBar()
			# no shapefile
			if uS == 0 and len(UX) > 0 and len(UY) > 0 and len(LX) > 0 and len(LY) > 0:
				for l in rT:
					lC = cfg.utls.selectLayerbyName(l, "Yes")
					if str(l).lower().endswith(".tif"):
						pass
					else:
						l = l + ".tif"
					cL = lC.source().encode(sys.getfilesystemencoding())
					dT = cfg.utls.getTime()
					c = oD.encode(sys.getfilesystemencoding()) + "/"
					d = outputName + "_" 
					e = os.path.basename(l.encode(sys.getfilesystemencoding()))
					f = c + d + e
					tPMN = cfg.tmpVrtNm + ".vrt"
					tPMD = cfg.tmpDir + "/" + dT + tPMN
					bList = [cL]
					bandNumberList = [1]		
					vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", noDt, 0, "No", "Yes", [float(UX), float(UY), float(LX), float(LY)])
					clipOutput = cfg.utls.copyRaster(tPMD, f, "GTiff", noDt)
					cfg.iface.addRasterLayer(unicode(oD) + "/" + outputName + "_" + unicode(os.path.basename(unicode(l))), unicode(outputName + "_" + unicode(os.path.basename(unicode(l)))))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters clipped" )
			# using shapefile
			elif uS == 1:
				for l in rT:
					lC = cfg.utls.selectLayerbyName(l, "Yes")
					if str(l).lower().endswith(".tif"):
						pass
					else:
						l = l + ".tif"
					cL = lC.source().encode(sys.getfilesystemencoding())
					dT = cfg.utls.getTime()
					# convert polygon to raster 
					tRNxs = cfg.copyTmpROI + dT + "xs.tif"
					tRxs = str(cfg.tmpDir + "//" + tRNxs)
					check = cfg.utls.vectorToRaster(cfg.emptyFN, unicode(s), cfg.emptyFN, tRxs, unicode(cL), None, "GTiff", 1)
					if check != "No":
						b = oD.encode(sys.getfilesystemencoding()) + "/" 
						c = outputName + "_" 
						d = os.path.basename(l.encode(sys.getfilesystemencoding()))
						e = b + c + d
						s.encode(sys.getfilesystemencoding()) 
						cfg.utls.clipRasterByRaster(cL, tRxs, e, "GTiff", noDt)
						cfg.iface.addRasterLayer(unicode(oD) + "/" + outputName + "_" + unicode(os.path.basename(unicode(l))), unicode(outputName + "_" + unicode(os.path.basename(unicode(l)))))
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters clipped" )
					else:
						st = "Yes"
						cfg.uiUtls.removeProgressBar()
			else:
				cfg.uiUtls.removeProgressBar()
				return "No"
			if  st != "Yes":
				cfg.uiUtls.removeProgressBar()
				cfg.utls.finishSound()
		
	# set coordinates
	def pointerClickLR(self, point):
		cfg.ui.LX_lineEdit.setText(str(point.x()))
		cfg.ui.LY_lineEdit.setText(str(point.y()))
		try:
			self.addRubberBandPolygon(QgsPoint(float(cfg.ui.UX_lineEdit.text()), float(cfg.ui.UY_lineEdit.text())), QgsPoint(float(cfg.ui.LX_lineEdit.text()), float(cfg.ui.LY_lineEdit.text())))
		except:
			pass
		
	# set coordinates
	def pointerClickUL(self, point):
		cfg.ui.UX_lineEdit.setText(str(point.x()))
		cfg.ui.UY_lineEdit.setText(str(point.y()))
		try:
			self.addRubberBandPolygon(QgsPoint(float(cfg.ui.UX_lineEdit.text()), float(cfg.ui.UY_lineEdit.text())), QgsPoint(float(cfg.ui.LX_lineEdit.text()), float(cfg.ui.LY_lineEdit.text())))
		except:
			pass
		
	# connect to pointer
	def pointerLRActive(self):
		cfg.cnvs.setMapTool(self.clickLR)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: LR")
		
	# connect to pointer
	def pointerULActive(self):
		cfg.cnvs.setMapTool(self.clickUL)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: UL")
		
	# Set rasters checklist
	def rasterNameList(self):
		ls = cfg.lgnd.layers()
		# checklist
		lst = cfg.ui.raster_listView_2
		# create band item model
		cfg.bndMdls = QStandardItemModel(lst)
		cfg.bndMdls.clear()
		lst.setModel(cfg.bndMdls)
		lst.show()
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					# band name
					it = QStandardItem(l.name())
					# Create checkbox
					it.setCheckable(True)
					# Add band to model
					cfg.bndMdls.appendRow(it)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster name checklist created")
		
	# refresh shape and training list	
	def refreshShapeClip(self):
		ls = cfg.lgnd.layers()
		cfg.ui.shapefile_comboBox.clear()
		for l in ls:
			if (l.type()==QgsMapLayer.VectorLayer):
				if (l.geometryType() == QGis.Polygon):
					cfg.dlg.shape_clip_combo(l.name())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "shape layers refreshed")
		
	# select all rasters
	def selectAllRasters(self):
		cfg.uiUtls.addProgressBar()
		try:
			# select all
			if self.allRastersCheck == "Yes":
				self.allRasterSetState(2)
				# set check all bands
				self.allRastersCheck = "No"
			# unselect all if previously selected all
			elif self.allRastersCheck == "No":
				self.allRasterSetState(0)
				# set check all bands
				self.allRastersCheck = "Yes"
		except:
			# first time except
			try:
				self.allRasterSetState(2)
				# set check all bands
				self.allRastersCheck = "No"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				pass
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all rasters clicked")
	