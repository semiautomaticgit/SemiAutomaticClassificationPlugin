# -*- coding: utf-8 -*-
'''
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright		: (C) 2012-2021 by Luca Congedo
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

'''



cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

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
	def clipRasters(self, batch = 'No', outputDirectory = None, shapefilePath = None, bandSetNumber = None, vectorField = None):
		if bandSetNumber is None:
			bandSet = cfg.ui.band_set_comb_spinBox_2.value()
			bandSetNumber = bandSet - 1
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		UX = ''
		UY = ''
		LX = ''
		LY = ''
		# creation of the required table of reclassification
		rT = []
		# st variable
		st = 'No'
		if batch == 'No':
			oD = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory where to save clipped rasters'))
		else:
			oD = outputDirectory
		if len(oD) == 0:
			return 'No'
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
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
		elif cfg.ui.temporary_ROI_checkBox.isChecked() is True:
			# use shape
			uS = 1
			uSF = 0
			if cfg.lstROI is not None:
				# temp shapefile
				tSHP = cfg.utls.createTempRasterPath('gpkg')
				cfg.utls.createSCPVector(cfg.lstROI.crs(), tSHP, format = 'GPKG')
				tSS = cfg.utls.addVectorLayer(tSHP)
				cfg.utls.copyFeatureToLayer(cfg.lstROI, 1, tSS)
				s = tSHP
			else:
				cfg.mx.msgErr11()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR: no vector' )
				return 'No'
		else:
			uS = 0
		if batch == 'No':
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
		# No data value
		noDt = cfg.ui.nodata_spinBox.value()
		if len(oD) > 0:
			cfg.uiUtls.updateBar(20)
			cfg.utls.makeDirectory(oD)
			outputName = cfg.ui.output_clip_name_lineEdit.text()
			if len(outputName) > 0:
				outputName = str(outputName.encode('ascii','replace'))[2:-1]
			else:
				outputName = ''
			# no shapefile
			if uS == 0:
				UX = cfg.ui.UX_lineEdit.text()
				UY = cfg.ui.UY_lineEdit.text()
				LX = cfg.ui.LX_lineEdit.text()
				LY = cfg.ui.LY_lineEdit.text()
				if batch == 'No':
					try:
						self.clearCanvasPoly()
						UL = cfg.qgisCoreSCP.QgsPointXY(float(UX), float(UY))
						LR = cfg.qgisCoreSCP.QgsPointXY(float(LX), float(LY))
						LRP = UL
						ULP = LR
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
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			ckB = cfg.utls.checkBandSet(bandSetNumber)
			if ckB == 'Yes':
				rT = cfg.bndSetLst
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rasters to be clipped' + str(rT))
				if len(rT) == 0:
					cfg.mx.msgWar15()
					return 'No'
			else:
				cfg.mx.msgWar15()
				return 'No'
		else:
			bi = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
			try:
				bPath = cfg.utls.layerSource(bi)
			except Exception as err:
				cfg.mx.msg4()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			if uS == 1:
				rT = cfg.utls.rasterToBands(bPath, cfg.tmpDir, outputName = cfg.utls.fileName(cfg.bandSetsList[bandSetNumber][8]), virtual = 'No')
			else:
				rT = cfg.utls.rasterToBands(bPath, cfg.tmpDir, outputName = cfg.utls.fileName(cfg.bandSetsList[bandSetNumber][8]), virtual = 'Yes')
		cfg.uiUtls.updateBar(50)
		# using coordinates
		if uS == 0 and len(UX) > 0 and len(UY) > 0 and len(LX) > 0 and len(LY) > 0:
			for l in rT:
				f = oD + '/' + outputName + '_'  + cfg.utls.fileName(l)
				bbList = [l]
				bandNumberList = [1]
				vrtCheck = cfg.utls.createTempVirtualRaster(bbList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'Yes', [float(UX), float(UY), float(LX), float(LY)])
				cfg.utls.GDALCopyRaster(vrtCheck, f, 'GTiff', cfg.rasterCompression, 'LZW')
				cfg.utls.addRasterLayer(f)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rasters clipped' )
		# using vector
		elif uS == 1:
			dT = cfg.utls.getTime()
			# vector EPSG
			if 'Polygon?crs=' in str(s) or 'memory?geometry=' in str(s) or '(memory)' in str(s):
				# temp shapefile
				tSHP = cfg.utls.createTempRasterPath('gpkg')
				try:
					s = cfg.utls.saveMemoryLayerToShapefile(sL, tSHP, format = 'GPKG')
				except:
					s = cfg.utls.saveMemoryLayerToShapefile(s, tSHP, format = 'GPKG')
				s = cfg.utls.layerSource(s)
				vCrs = cfg.utls.getCrsGDAL(tSHP)
			elif 'QgsVectorLayer' in str(s):
				# temporary layer
				tLN = cfg.subsTmpROI + dT + '.shp'
				tLP = cfg.tmpDir + '/' + dT + tLN
				# get layer crs
				crs = cfg.utls.getCrsGDAL(s)
				# create a temp shapefile with a field
				cfg.utls.createEmptyShapefile(crs, tLP)
				mL = cfg.utls.addVectorLayer(tLP , tLN, 'ogr')
				f = cfg.qgisCoreSCP.QgsFeature()
				for f in s.getFeatures():
					ID = f.id()
					# copy ROI to temp shapefile
					cfg.utls.copyFeatureToLayer(s, ID, mL)
				s = tLP
				vCrs = cfg.utls.getCrsGDAL(s)
			else:
				vCrs = cfg.utls.getCrsGDAL(s)
			# in case of reprojection
			reprjShapefile = cfg.tmpDir + '/' + dT + cfg.utls.fileNameNoExt(s) + '.shp'
			# band list
			bbList = []
			for l in rT:
				bbList.append(l)
			tRxs = cfg.utls.createTempRasterPath('tif')
			# check projection
			vEPSG = cfg.osrSCP.SpatialReference()
			vEPSG.ImportFromWkt(vCrs)
			rP = cfg.utls.getCrsGDAL(l)
			rEPSG = cfg.osrSCP.SpatialReference()
			rEPSG.ImportFromWkt(rP)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rP: ' + str(rP))
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' vCrs: ' + str(vCrs))
			vect = s
			if vEPSG.IsSame(rEPSG) != 1:
				if cfg.osSCP.path.isfile(reprjShapefile):
					vect = reprjShapefile
				else:
					try:
						cfg.utls.repojectShapefile(s, vEPSG, reprjShapefile, rEPSG)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))	
						cfg.mx.msgErr43()
						if batch == 'No':
							cfg.uiUtls.removeProgressBar()
						return 'No'
					vect = reprjShapefile
			# if iterate through field	
			if uSF == 1:
				values = cfg.utls.getVectorFieldfValues(vect, vectorField)
				if values == 'No':
					cfg.mx.msgErr43()
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
				for v in values:
					check = cfg.utls.vectorToRaster(cfg.emptyFN, vect, cfg.emptyFN, tRxs, l, None, 'GTiff', 1, vectorField + '=' + str(v))
					if check != 'No':
						outList = cfg.utls.clipRasterByRaster(bbList, tRxs, oD, 'GTiff', noDt, outputNameRoot = outputName + vectorField + '_' + str(v) + '_')
						try:
							cfg.osSCP.remove(tRxs)
						except:
							pass
						try:
							for oU in outList:
								cfg.utls.addRasterLayer(oU)
						except Exception as err:
							# logger
							if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rasters clipped' )
					else:
						st = 'Yes'
						if batch == 'No':
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()
			# without field iteration
			else:
				check = cfg.utls.vectorToRaster(cfg.emptyFN, vect, cfg.emptyFN, tRxs, l, None, 'GTiff', 1)
				if check != 'No':
					outList = cfg.utls.clipRasterByRaster(bbList, tRxs, oD, 'GTiff', noDt, outputNameRoot = outputName + '_' )
					try:
						cfg.osSCP.remove(tRxs)
					except:
						pass
					try:
						for oU in outList:
							cfg.utls.addRasterLayer(oU)
					except Exception as err:
						# logger
						if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rasters clipped' )
				else:
					st = 'Yes'
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
		else:
			if batch == 'No':
				cfg.uiUtls.removeProgressBar()
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
			return 'No'
		if  st != 'Yes':
			if batch == 'No':
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.uiUtls.removeProgressBar()
				cfg.utls.finishSound()
				cfg.utls.sendSMTPMessage(None, str(__name__))
		
	# Activate pointer
	def pointerActive(self):
		# connect to click
		t = cfg.clipMultiP
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(":/pointer/icons/pointer/ROI_pointer.svg")
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "pointer active")
		
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
			if l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
				f = l.dataProvider().fields()
				for i in f:
					if str(i.typeName()).lower() != "string":
						cfg.dlg.class_field_combo_3(str(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layer name: " + str(referenceLayer3))
		