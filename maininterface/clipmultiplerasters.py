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
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all rasters cancelled")
		
	# clip multiple rasters
	def clipRasters(self):
		oD = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Select a directory where to save clipped rasters"))
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
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters to be clipped" + str(rT))
		if cfg.ui.shapefile_checkBox.isChecked() is True:
			# use shape
			uS = 1
			sN = str(cfg.ui.shapefile_comboBox.currentText())
			sL = cfg.utls.selectLayerbyName(sN)
			try:
				s = str(sL.source())
			except Exception, err:
				st = "Yes"
				cfg.mx.msgErr11()
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		else:
			uS = 0
		# No data value
		noDt = cfg.ui.nodata_spinBox.value()
		if len(oD) > 0:
			UX = cfg.ui.UX_lineEdit.text()
			UY = cfg.ui.UY_lineEdit.text()
			LX = cfg.ui.LX_lineEdit.text()
			LY = cfg.ui.LY_lineEdit.text()
			for l in rT:
				lC = cfg.utls.selectLayerbyName(l)
				if str(l).endswith(".tif"):
					pass
				else:
					l = l + ".tif"
				try:
					cL = "\"" + str(lC.source()) + "\""
				except Exception, err:
					st = "Yes"
					cfg.mx.msgErr11()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				if  st != "Yes":
					# no shapefile
					if uS == 0 and len(UX) > 0 and len(UY) > 0 and len(LX) > 0 and len(LY) > 0:
						sP = subprocess.Popen("gdal_translate -a_nodata " + str(noDt) + " -projwin " + str(UX) + " " + str(UY) + " " + str(LX) + " " + str(LY) + " -of GTiff " + cL + " \"" + str(oD) + "/" + cfg.clipNm + "_" + os.path.basename(str(l)) + "\"", shell=True)
						sP.wait()
					# using shapefile
					elif uS == 1:
						sP = subprocess.Popen("gdalwarp -dstnodata " + str(noDt) + " -cutline \"" + s + "\" -crop_to_cutline -of GTiff " + cL + " \"" + str(oD) + "/" + cfg.clipNm + "_" + os.path.basename(str(l)) + "\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
						sP.wait()
						# get error
						out, err = sP.communicate()
						if len(err) > 0:
							cfg.mx.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error"), err)
							st = "Yes"
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error:: " + str(err) )
					else:
						return "No"
					try:
						if  st != "Yes":
							cfg.iface.addRasterLayer(str(str(oD.encode(cfg.fSEnc)) + "/clip_" + str(os.path.basename(str(l)).encode(cfg.fSEnc))), str("clip_" + str(os.path.basename(str(l)).encode(cfg.fSEnc))))
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters clipped" )
					except Exception, err:
						st = "Yes"
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.mx.msgErr10()
		
	def clipSetTab(self):
		# select clip tab
		cfg.ui.tabWidget_preprocessing.setCurrentIndex(0)
		# show the dialog
		cfg.dlg.show()
		
	# set coordinates
	def pointerClickLR(self, point):
		cfg.utls.pan()
		cfg.ui.LX_lineEdit.setText(str(point.x()))
		cfg.ui.LY_lineEdit .setText(str(point.y()))
		
	# set coordinates
	def pointerClickUL(self, point):
		cfg.utls.pan()
		cfg.ui.UX_lineEdit.setText(str(point.x()))
		cfg.ui.UY_lineEdit .setText(str(point.y()))
		self.clipSetTab()
		
	# connect to pointer
	def pointerLRActive(self):
		cfg.cnvs.setMapTool(self.clickLR)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: LR")
		
	# connect to pointer
	def pointerULActive(self):
		cfg.cnvs.setMapTool(self.clickUL)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: UL")
		
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
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster name checklist created")
		
	# refresh shape and training list	
	def refreshShapeClip(self):
		ls = cfg.lgnd.layers()
		cfg.ui.shapefile_comboBox.clear()
		for l in ls:
			if (l.type()==QgsMapLayer.VectorLayer):
				if (l.geometryType() == QGis.Polygon):
					cfg.dlg.shape_clip_combo(l.name())
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "shape layers refreshed")
		
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
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				pass
		cfg.uiUtls.removeProgressBar()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all rasters clicked")
	