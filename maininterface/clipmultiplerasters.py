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

class ClipMultipleRasters:

	def __init__(self):
		pass
		
	# add rubber band
	def addRubberBandPolygon(self, pointUL, pointLR):
		try:
			self.clearCanvasPoly()
		except:
			pass
		self.rbbrBndPol = cfg.qgisGuiSCP.QgsRubberBand(cfg.cnvs, 2)
		pointF = cfg.QtCoreSCP.QPointF()
		polF = cfg.QtGuiSCP.QPolygonF()
		pointF.setX(pointUL.x())
		pointF.setY(pointUL.y())
		polF.append(pointF)
		pointF.setX(pointLR.x())
		pointF.setY(pointUL.y())
		polF.append(pointF)
		pointF.setX(pointLR.x())
		pointF.setY(pointLR.y())
		polF.append(pointF)
		pointF.setX(pointUL.x())
		pointF.setY(pointLR.y())
		polF.append(pointF)
		pointF.setX(pointUL.x())
		pointF.setY(pointUL.y())
		polF.append(pointF)
		g = cfg.qgisCoreSCP.QgsGeometry().fromQPolygonF(polF)
		self.rbbrBndPol.setToGeometry(g, None)
		clr = cfg.QtGuiSCP.QColor("#ff0000")
		clr.setAlpha(50)
		self.rbbrBndPol.setFillColor(clr)
		self.rbbrBndPol.setWidth(3)
		
	# clear canvas
	def clearCanvasPoly(self):
		self.rbbrBndPol.reset(True)
		cfg.cnvs.refresh()	
		
	# clip multiple rasters action
	def clipRastersAction(self):
		self.clipRasters()
		
	# clip multiple rasters
	def clipRasters(self, batch = "No", outputDirectory = None, shapefilePath = None, bandSetNumber = None, vectorField = None):
		if bandSetNumber is None:
			bandSet = cfg.ui.band_set_comb_spinBox_2.value()
			bandSetNumber = bandSet - 1
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		UX = ""
		UY = ""
		LX = ""
		LY = ""
		# creation of the required table of reclassification
		rT = []
		# st variable
		st = "No"
		cfg.uiUtls.addProgressBar()
		if cfg.bandSetsList[bandSetNumber][0] == "Yes":
			ckB = cfg.utls.checkBandSet(bandSetNumber)
			if ckB == "Yes":
				rT = cfg.bandSetsList[bandSetNumber][3]
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters to be clipped" + str(rT))
				if len(rT) == 0:
					cfg.mx.msgWar15()
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					return "No"
				if batch == "No":
					oD = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory where to save clipped rasters"))
				else:
					oD = outputDirectory
				if len(oD) == 0:
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					return "No"
				if cfg.ui.shapefile_checkBox.isChecked() is True:
					# use shape
					uS = 1
					sN = cfg.ui.shapefile_comboBox.currentText()
					sL = cfg.utls.selectLayerbyName(sN)
					try:
						s = cfg.utls.layerSource(sL)
						if cfg.ui.vector_field_checkBox.isChecked() is True:
							uSF = 1
							if vectorField is None:
								vectorField = cfg.ui.class_field_comboBox_3.currentText()
						else:
							uSF = 0
					except Exception as err:
						cfg.mx.msgErr11()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
						return "No"
				elif cfg.ui.temporary_ROI_checkBox.isChecked() is True:
					# use shape
					uS = 1
					uSF = 0
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
			cfg.mx.msgWar15()
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
			return "No"
		# No data value
		noDt = cfg.ui.nodata_spinBox.value()
		if len(oD) > 0:
			outputName = cfg.ui.output_clip_name_lineEdit.text()
			if len(outputName) > 0:
				outputName = str(outputName.encode('ascii','replace'))[2:-1]
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
						UL = cfg.qgisCoreSCP.QgsPointXY(float(UX), float(UY))
						LR = cfg.qgisCoreSCP.QgsPointXY(float(LX), float(LY))
						ULP = cfg.utls.checkPointImage(rT[0], UL, "Yes")
						if str(cfg.pntCheck) == "No":
							cfg.mx.msgErr34()
							if batch == "No":
								cfg.uiUtls.removeProgressBar()
							return "No"
						LRP = cfg.utls.checkPointImage(rT[0], LR, "Yes")
						if str(cfg.pntCheck) == "No":
							cfg.mx.msgErr34()
							if batch == "No":
								cfg.uiUtls.removeProgressBar()
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
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			# no shapefile
			if uS == 0 and len(UX) > 0 and len(UY) > 0 and len(LX) > 0 and len(LY) > 0:
				for l in rT:
					lC = cfg.utls.selectLayerbyName(l, "Yes")
					if str(l).lower().endswith(".tif"):
						pass
					else:
						l = l + ".tif"
					cL = cfg.utls.layerSource(lC)
					dT = cfg.utls.getTime()
					c = oD + "/"
					d = outputName + "_" 
					e = cfg.osSCP.path.basename(l)
					f = c + d + e
					tPMN = cfg.tmpVrtNm + ".vrt"
					tPMD = cfg.tmpDir + "/" + dT + tPMN
					tPMN2 = dT + cfg.calcRasterNm + ".tif"
					tPMD2 = cfg.tmpDir + "/" + tPMN2
					bList = [cL]
					bandNumberList = [1]		
					vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "Yes", [float(UX), float(UY), float(LX), float(LY)])
					clipOutput = cfg.utls.copyRaster(tPMD, tPMD2, "GTiff", noDt)
					if cfg.rasterCompression != "No":
						try:
							cfg.utls.GDALCopyRaster(tPMD2, f, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
							cfg.osSCP.remove(tPMD2)
						except Exception as err:
							cfg.shutilSCP.copy(tPMD2, f)
							cfg.osSCP.remove(tPMD2)
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					else:
						cfg.shutilSCP.copy(tPMD2, f)
						cfg.osSCP.remove(tPMD2)
					cfg.utls.addRasterLayer(str(oD) + "/" + outputName + "_" + str(cfg.osSCP.path.basename(str(l))))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters clipped" )
			# using shapefile
			elif uS == 1:
				dT = cfg.utls.getTime()
				# vector EPSG
				if "MultiPolygon?crs=PROJCS" in str(s):
					# temp shapefile
					tSHP = cfg.tmpDir + "/" + sN + dT + ".shp"
					s = cfg.utls.saveMemoryLayerToShapefile(sL, tSHP)
					s = cfg.utls.layerSource(s)
					vEPSG = cfg.utls.getEPSGVector(tSHP)
				elif "QgsVectorLayer" in str(s):
					# temporary layer
					tLN = cfg.subsTmpROI + dT + ".shp"
					tLP = cfg.tmpDir + "/" + dT + tLN
					# get layer crs
					crs = cfg.utls.getCrs(s)
					# create a temp shapefile with a field
					cfg.utls.createEmptyShapefileQGIS(crs, tLP)
					mL = cfg.utls.addVectorLayer(tLP , tLN, "ogr")
					f = cfg.qgisCoreSCP.QgsFeature()
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
					lC = cfg.utls.selectLayerbyName(l, "Yes")
					if str(l).lower().endswith(".tif"):
						pass
					else:
						l = l + ".tif"
					cL = cfg.utls.layerSource(lC)
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
							except Exception as err:
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								return "No"
							vect = reprjShapefile
					# if iterate through field	
					if uSF == 1:
						values = cfg.utls.getVectorFieldfValues(vect, vectorField)
						for v in values:
							check = cfg.utls.vectorToRaster(cfg.emptyFN, vect, cfg.emptyFN, tRxs, cL, None, "GTiff", 1, vectorField + "=" + str(v))
							if check != "No":
								b = oD + "/" 
								c = outputName + "_" 
								d = cfg.osSCP.path.basename(l).split(".")[0] + "_" + vectorField + "_" + str(v) + ".tif"
								e = b + c + d
								cfg.utls.clipRasterByRaster(cL, tRxs, tPMD2, "GTiff", noDt)
								if cfg.rasterCompression != "No":
									try:
										cfg.utls.GDALCopyRaster(tPMD2, e, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
										cfg.osSCP.remove(tPMD2)
									except Exception as err:
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
								cfg.utls.addRasterLayer(e)
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters clipped" )
							else:
								st = "Yes"
								if batch == "No":
									# enable map canvas render
									cfg.cnvs.setRenderFlag(True)
									cfg.uiUtls.removeProgressBar()
								
								
								
					else:
						check = cfg.utls.vectorToRaster(cfg.emptyFN, vect, cfg.emptyFN, tRxs, cL, None, "GTiff", 1)
						if check != "No":
							b = oD + "/" 
							c = outputName + "_" 
							d = cfg.osSCP.path.basename(l)
							e = b + c + d
							cfg.utls.clipRasterByRaster(cL, tRxs, tPMD2, "GTiff", noDt)
							if cfg.rasterCompression != "No":
								try:
									cfg.utls.GDALCopyRaster(tPMD2, e, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
									cfg.osSCP.remove(tPMD2)
								except Exception as err:
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
							cfg.utls.addRasterLayer(str(oD) + "/" + outputName + "_" + str(cfg.osSCP.path.basename(str(l))))
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " rasters clipped" )
						else:
							st = "Yes"
							if batch == "No":
								# enable map canvas render
								cfg.cnvs.setRenderFlag(True)
								cfg.uiUtls.removeProgressBar()
			else:
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
				return "No"
			if  st != "Yes":
				if batch == "No":
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
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
			self.addRubberBandPolygon(cfg.qgisCoreSCP.QgsPointXY(float(cfg.ui.UX_lineEdit.text()), float(cfg.ui.UY_lineEdit.text())), cfg.qgisCoreSCP.QgsPointXY(float(cfg.ui.LX_lineEdit.text()), float(cfg.ui.LY_lineEdit.text())))
		except:
			pass
		
	# refresh shape and training list	
	def refreshShapeClip(self):
		cfg.utls.refreshVectorLayer()
		
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
		
				
	# reference layer name
	def referenceLayerName(self):
		referenceLayer3 = cfg.ui.shapefile_comboBox.currentText()
		cfg.ui.class_field_comboBox_3.clear()
		l = cfg.utls.selectLayerbyName(referenceLayer3)
		try:
			if l.type()== 0:
				f = l.dataProvider().fields()
				for i in f:
					if i.typeName() != "String":
						cfg.dlg.class_field_combo_3(str(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layer name: " + str(referenceLayer3))
		