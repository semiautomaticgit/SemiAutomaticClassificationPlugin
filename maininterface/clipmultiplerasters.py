# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2017 by Luca Congedo
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
cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

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
		clr = cfg.QtGuiSCP.QColor(cfg.ROIClrVal)
		clr.setAlpha(50)
		try:
			# QGIS 2.6
			self.rbbrBndPol.setFillColor(clr)
			#self.rbbrBndPol.setBorderColor(cfg.QtGuiSCP.QColor(cfg.ROIClrOutlineValDefault))
			#self.rbbrBndPol.setLineStyle(cfg.QtSCP.DotLine)
			self.rbbrBndPol.setWidth(3)
		except:
			# QGIS < 2.6
			self.rbbrBndPol.setColor(clr)
			#self.rbbrBndPol.setLineStyle(cfg.QtSCP.DotLine)
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
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all rasters cancelled")
		
	# clip multiple rasters action
	def clipRastersAction(self):
		self.clipRasters()
		
	# clip multiple rasters
	def clipRasters(self, batch = "No", fileListString = None, outputDirectory = None, shapefilePath = None):
		UX = ""
		UY = ""
		LX = ""
		LY = ""
		# creation of the required table of reclassification
		rT = []
		# st variable
		st = "No"
		if batch == "No":
			cfg.uiUtls.addProgressBar()
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
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
				return "No"
			oD = cfg.utls.getExistingDirectory(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory where to save clipped rasters"))
			if len(oD) == 0:
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
				return "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters to be clipped" + unicode(rT))
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
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					return "No"
			elif cfg.ui.temporary_ROI_checkBox.isChecked() is True:
				# use shape
				uS = 1
				if cfg.lstROI is not None:
					s = cfg.lstROI
				else:
					cfg.mx.msgErr11()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR: no vector" )
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					return "No"
			else:
				uS = 0
		else:
			fileList = fileListString.split(",")
			for f in fileList:
				rT.append(f.strip())
			oD = outputDirectory
			oDir = cfg.utls.makeDirectory(oD)
			if oDir is None:
				cfg.mx.msgErr58()
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
				return "No"
			s = shapefilePath
			if cfg.ui.shapefile_checkBox.isChecked() is True:
				# use shape
				uS = 1
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
				UX = cfg.ui.UX_lineEdit.text()
				UY = cfg.ui.UY_lineEdit.text()
				LX = cfg.ui.LX_lineEdit.text()
				LY = cfg.ui.LY_lineEdit.text()
				if batch == "No":
					try:
						self.clearCanvasPoly()
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
			else:
				try:
					if float(UX) > float(LX):
						tUX = UX
						UX = str(LX)
						LX = str(tUX)
					if float(UY) < float(LY):
						tUY = UY
						UY = str(LY)
						LY = str(tUY)
				except:
					pass
			# no shapefile
			if uS == 0 and len(UX) > 0 and len(UY) > 0 and len(LX) > 0 and len(LY) > 0:
				for l in rT:
					if batch == "No":
						lC = cfg.utls.selectLayerbyName(l, "Yes")
						if str(l).lower().endswith(".tif"):
							pass
						else:
							l = l + ".tif"
						cL = lC.source().encode(cfg.sysSCP.getfilesystemencoding())
					else:
						if str(l).lower().endswith(".tif"):
							pass
						else:
							l = l + ".tif"
						cL = l
					dT = cfg.utls.getTime()
					c = oD.encode(cfg.sysSCP.getfilesystemencoding()) + "/"
					d = outputName + "_" 
					e = cfg.osSCP.path.basename(l.encode(cfg.sysSCP.getfilesystemencoding()))
					f = c + d + e
					tPMN = cfg.tmpVrtNm + ".vrt"
					tPMD = cfg.tmpDir + "/" + dT + tPMN
					tPMN2 = dT + cfg.calcRasterNm + ".tif"
					tPMD2 = cfg.tmpDir + "/" + tPMN2
					bList = [cL]
					bandNumberList = [1]		
					vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", noDt, 0, "No", "Yes", [float(UX), float(UY), float(LX), float(LY)])
					clipOutput = cfg.utls.copyRaster(tPMD, tPMD2, "GTiff", noDt)
					if cfg.rasterCompression != "No":
						try:
							cfg.utls.GDALCopyRaster(tPMD2, f, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
							cfg.osSCP.remove(tPMD2)
						except Exception, err:
							cfg.shutilSCP.copy(tPMD2, f)
							cfg.osSCP.remove(tPMD2)
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					else:
						cfg.shutilSCP.copy(tPMD2, f)
						cfg.osSCP.remove(tPMD2)
					cfg.iface.addRasterLayer(unicode(oD) + "/" + outputName + "_" + unicode(cfg.osSCP.path.basename(unicode(l))), unicode(outputName + "_" + unicode(cfg.osSCP.path.basename(unicode(l)))))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters clipped" )
			# using shapefile
			elif uS == 1:
				dT = cfg.utls.getTime()
				# vector EPSG
				if "MultiPolygon?crs=PROJCS" in unicode(s):
					# temp shapefile
					tSHP = cfg.tmpDir + "/" + sN + dT + ".shp"
					s = cfg.utls.saveMemoryLayerToShapefile(sL, tSHP)
					s = s.source()
					vEPSG = cfg.utls.getEPSGVector(tSHP)
				elif "QgsVectorLayer" in unicode(s):
					# temporary layer
					tLN = cfg.subsTmpROI + dT + ".shp"
					tLP = cfg.tmpDir + "/" + dT + tLN
					# get layer crs
					crs = cfg.utls.getCrs(s)
					# create a temp shapefile with a field
					cfg.utls.createEmptyShapefileQGIS(crs, tLP)
					mL = cfg.utls.addVectorLayer(tLP , tLN, "ogr")
					f = QgsFeature()
					for f in s.getFeatures():
						ID = f.id()
						# copy ROI to temp shapefile
						cfg.utls.copyFeatureToLayer(s, ID, mL)
					s = tLP
					vEPSG = cfg.utls.getEPSGVector(s)
				else:
					vEPSG = cfg.utls.getEPSGVector(s)
				# in case of reprojection
				reprjShapefile = cfg.tmpDir + "/" + dT + cfg.osSCP.path.basename(s)
				for l in rT:
					if batch == "No":
						lC = cfg.utls.selectLayerbyName(l, "Yes")
						if str(l).lower().endswith(".tif"):
							pass
						else:
							l = l + ".tif"
						cL = lC.source().encode(cfg.sysSCP.getfilesystemencoding())
					else:
						if str(l).lower().endswith(".tif"):
							pass
						else:
							l = l + ".tif"
						cL = l
					dT = cfg.utls.getTime()
					# convert polygon to raster 
					tRNxs = cfg.copyTmpROI + dT + "xs.tif"
					tRxs = str(cfg.tmpDir + "//" + tRNxs)
					tPMN2 = dT + cfg.calcRasterNm + ".tif"
					tPMD2 = cfg.tmpDir + "/" + tPMN2
					rEPSG = cfg.utls.getEPSGRaster(cL)
					vect = s
					if vEPSG != rEPSG:
						if cfg.osSCP.path.isfile(reprjShapefile):
							vect = reprjShapefile
						else:
							try:
								cfg.utls.repojectShapefile(s, int(vEPSG), reprjShapefile, int(rEPSG))
							except Exception, err:
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								return "No"
							vect = reprjShapefile
					check = cfg.utls.vectorToRaster(cfg.emptyFN, vect, cfg.emptyFN, tRxs, cL, None, "GTiff", 1)
					if check != "No":
						b = oD.encode(cfg.sysSCP.getfilesystemencoding()) + "/" 
						c = outputName + "_" 
						d = cfg.osSCP.path.basename(l.encode(cfg.sysSCP.getfilesystemencoding()))
						e = b + c + d
						cfg.utls.clipRasterByRaster(cL, tRxs, tPMD2, "GTiff", noDt)
						if cfg.rasterCompression != "No":
							try:
								cfg.utls.GDALCopyRaster(tPMD2, e, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
								cfg.osSCP.remove(tPMD2)
							except Exception, err:
								cfg.shutilSCP.copy(tPMD2, e)
								cfg.osSCP.remove(tPMD2)
								# logger
								if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						else:
							cfg.shutilSCP.copy(tPMD2, e)
							cfg.osSCP.remove(tPMD2)
						try:
							cfg.osSCP.remove(tRxs)
						except:
							pass
						cfg.iface.addRasterLayer(unicode(oD) + "/" + outputName + "_" + unicode(cfg.osSCP.path.basename(unicode(l))), unicode(outputName + "_" + unicode(cfg.osSCP.path.basename(unicode(l)))))
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters clipped" )
					else:
						st = "Yes"
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
			else:
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
				return "No"
			if  st != "Yes":
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
					cfg.utls.finishSound()
		
	# Activate pointer
	def pointerActive(self):
		# connect to click
		t = cfg.clipMultiP
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(":/pointer/icons/pointer/ROI_pointer.png")
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active")
		
	# left click pointer
	def pointerLeftClick(self, point):
		self.pointerClickUL(point)
			
	# right click pointer
	def pointerRightClick(self, point):
		self.pointerClickLR(point)
		
	# set coordinates
	def pointerClickLR(self, point):
		cfg.ui.LX_lineEdit.setText(str(point.x()))
		cfg.ui.LY_lineEdit.setText(str(point.y()))
		self.showArea()
		
	# set coordinates
	def pointerClickUL(self, point):
		cfg.ui.UX_lineEdit.setText(str(point.x()))
		cfg.ui.UY_lineEdit.setText(str(point.y()))
		self.showArea()

	# show area
	def showArea(self):
		try:
			self.addRubberBandPolygon(QgsPoint(float(cfg.ui.UX_lineEdit.text()), float(cfg.ui.UY_lineEdit.text())), QgsPoint(float(cfg.ui.LX_lineEdit.text()), float(cfg.ui.LY_lineEdit.text())))
		except:
			pass
			
	# Set rasters checklist
	def rasterNameList(self):
		ls = cfg.lgnd.layers()
		# checklist
		lst = cfg.ui.raster_listView_2
		# create band item model
		cfg.bndMdls = cfg.QtGuiSCP.QStandardItemModel(lst)
		cfg.bndMdls.clear()
		lst.setModel(cfg.bndMdls)
		lst.show()
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					# band name
					it = cfg.QtGuiSCP.QStandardItem(l.name())
					# Create checkbox
					it.setCheckable(True)
					# Add band to model
					cfg.bndMdls.appendRow(it)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster name checklist created")
		
	# refresh shape and training list	
	def refreshShapeClip(self):
		cfg.utls.refreshVectorLayer()
		
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
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				pass
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all rasters clicked")
			
	# show hide area radio button
	def showHideArea(self):
		try:
			if cfg.ui.show_area_radioButton_3.isChecked():				
				self.showArea()
			else:
				self.clearCanvasPoly()
		except:
			pass
			
	# checkbox changed
	def checkboxShapeChanged(self):
		cfg.ui.shapefile_checkBox.blockSignals(True)
		cfg.ui.temporary_ROI_checkBox.blockSignals(True)
		if cfg.ui.shapefile_checkBox.isChecked():
			if cfg.ui.temporary_ROI_checkBox.isChecked():
				cfg.ui.temporary_ROI_checkBox.setCheckState(0)
		cfg.ui.shapefile_checkBox.blockSignals(False)
		cfg.ui.temporary_ROI_checkBox.blockSignals(False)
		
	# checkbox changed
	def checkboxTempROIChanged(self):
		cfg.ui.shapefile_checkBox.blockSignals(True)
		cfg.ui.temporary_ROI_checkBox.blockSignals(True)
		if cfg.ui.temporary_ROI_checkBox.isChecked():
			if cfg.ui.shapefile_checkBox.isChecked():
				cfg.ui.shapefile_checkBox.setCheckState(0)
		cfg.ui.shapefile_checkBox.blockSignals(False)
		cfg.ui.temporary_ROI_checkBox.blockSignals(False)
		