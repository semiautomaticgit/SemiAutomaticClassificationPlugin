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

class EditRaster:

	def __init__(self):
		pass
		
	# set raster value
	def setRasterValueAction(self):
		self.setRasterValue()
		
	# set raster value
	def setRasterValue(self, batch = "No", rasterInput = None, vectorInput = None, vectorFieldName = None):
		if cfg.ui.edit_val_use_ROI_radioButton.isChecked() and cfg.lstROI is None:
			cfg.mx.msg22()
			return
		else:
			if batch == "No":
				self.rstrNm = cfg.ui.edit_raster_name_combo.currentText()
				b = cfg.utls.selectLayerbyName(self.rstrNm, "Yes")
			else:
				b = "No"
			if b is not None:
				if batch == "No":
					rSource = cfg.utls.layerSource(b)
				else:
					rSource = rasterInput
				cfg.ui.undo_edit_Button.setEnabled(False)
				cfg.undoEditRasterToolbar_toolButton.setEnabled(False)
				# create feature list
				rId = []
				f = cfg.qgisCoreSCP.QgsFeature()
				# using vector
				if cfg.ui.edit_val_use_vector_radioButton.isChecked():
					if batch == "No":
						shapeNm = cfg.ui.vector_name_combo_2.currentText()
						shape = cfg.utls.selectLayerbyName(shapeNm)
					else:
						shape = cfg.utls.addVectorLayer(vectorInput , cfg.osSCP.path.basename(vectorInput), "ogr")
					if shape is None:
						return
					for f in shape.getFeatures():
						rId.append(f.id())
					vector = shape
				# using ROI polygon
				elif cfg.ui.edit_val_use_ROI_radioButton.isChecked():
					for f in cfg.lstROI.getFeatures():
						rId.append(f.id())		
					vector = cfg.lstROI
					# hide ROI
					cfg.show_ROI_radioButton.setChecked(False)
					cfg.SCPD.showHideROI()
				self.setValueRaster(rSource, vector, rId, batch, vectorFieldName)
				if b != "No":
					b.reload()
					b.triggerRepaint()
					cfg.cnvs.refresh()
				if batch == "No":
					pass
				else:
					cfg.utls.removeLayerByLayer(shape)
			else:
				cfg.utls.refreshClassificationLayer()
				cfg.mx.msgErr9()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error raster not found")
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())

	# set value raster
	def setValueRaster(self, inputRaster, inputVectorQGIS, qgisVectorFeatureList, batch = "No", vectorFieldName = None, toolbarValue = None):
		crs = cfg.utls.getCrs(inputVectorQGIS)
		# using ROI polygon
		if cfg.ui.edit_val_use_ROI_radioButton.isChecked() or toolbarValue is not None:
			# date time for temp name
			dT = cfg.utls.getTime()
			# temporary layer
			tLN = cfg.subsTmpROI + dT + ".shp"
			tLP = cfg.tmpDir + "/" + dT + tLN
			# create a temp shapefile with a field
			cfg.utls.createEmptyShapefileQGIS(crs, tLP)
			vector = cfg.utls.addVectorLayer(tLP, cfg.osSCP.path.basename(tLP), "ogr")
			for pI in qgisVectorFeatureList:
				cfg.utls.copyFeatureToLayer(inputVectorQGIS, pI, vector)
			if toolbarValue is None:
				toolbarValue = cfg.ui.value_spinBox.value()
			self.performEdit(inputRaster, tLP, toolbarValue)
			cfg.ui.undo_edit_Button.setEnabled(True)
			cfg.undoEditRasterToolbar_toolButton.setEnabled(True)
		# using vector
		else:
			if batch == "No":
				cfg.uiUtls.addProgressBar()
			progress = 0
			progressStep = 100 / (len(qgisVectorFeatureList) + 1)
			n = 0
			for pI in qgisVectorFeatureList:
				n = n + 1
				progress = progress + progressStep
				cfg.uiUtls.updateBar(progress)
				# date time for temp name
				dT = cfg.utls.getTime()
				# temporary layer
				tLN = cfg.subsTmpROI + dT + ".shp"
				tLP = cfg.tmpDir + "/" + dT + tLN
				# create a temp shapefile with a field
				cfg.utls.createEmptyShapefileQGIS(crs, tLP)
				vector = cfg.utls.addVectorLayer(tLP, cfg.osSCP.path.basename(tLP), "ogr")
				cfg.utls.copyFeatureToLayer(inputVectorQGIS, pI, vector)
				if cfg.ui.use_constant_val_checkBox.isChecked() is True:
					value = cfg.ui.value_spinBox.value()
				else:
					if vectorFieldName is None:
						fd = cfg.ui.field_comboBox_2.currentText()
					else:
						fd = vectorFieldName
					if len(fd) == 0:
						cfg.utls.refreshVectorLayer()
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
						return "No"
					fId = cfg.utls.fieldID(inputVectorQGIS, fd)
					f = cfg.utls.getFeaturebyID(inputVectorQGIS, pI)
					value = f.attributes()[fId]
				self.performEdit(inputRaster, tLP, value)
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
		
	# perform raster edit
	def performEdit(self, inputRasterPath, inputVectorPath, editValue = None):
		# date time for temp name
		dT = cfg.utls.getTime()
		# convert polygon to raster 
		tRNxs = cfg.copyTmpROI + dT + "xs.tif"
		tRxs = str(cfg.tmpDir + "//" + tRNxs)
		check = cfg.utls.vectorToRaster(cfg.emptyFN, str(inputVectorPath), cfg.emptyFN, tRxs, str(inputRasterPath), None, "GTiff", 1)
		# open input with GDAL
		rD = cfg.gdalSCP.Open(inputRasterPath, cfg.gdalSCP.GA_Update)
		if rD is None:
			return "No"
		rD2 = cfg.gdalSCP.Open(tRxs, cfg.gdalSCP.GA_ReadOnly)
		if rD2 is None:
			return "No"
		# pixel size and origin
		rGT = rD.GetGeoTransform()
		tLX = rGT[0]
		tLY = rGT[3]
		pSX = rGT[1]
		pSY = rGT[5]
		rGT2 = rD2.GetGeoTransform()
		tLX2 = rGT2[0]
		tLY2 = rGT2[3]
		# number of x pixels
		rC = rD.RasterXSize
		rC2 = rD2.RasterXSize
		# number of y pixels
		rR = rD.RasterYSize
		rR2 = rD2.RasterYSize
		if tLX2 < tLX:
			startX = tLX
		else:
			startX = tLX2
		if tLY2 > tLY:
			startY = tLY
		else:
			startY = tLY2
		self.pixelStartColumn = abs(int((tLX - startX) / pSX ))
		self.pixelStartRow = abs(int((tLY - startY) / pSY ))
		startColumn2 = abs(int((tLX2 - startX) / pSX ))
		startRow2 = abs(int((tLY2 - startY) / pSY ))
		columnNum = rC2 - startColumn2 
		rowNum = rR2 - startRow2 
		if columnNum < 1 or rowNum < 1:
			return
		if self.pixelStartColumn + columnNum > rC:
			columnNum1 = rC - self.pixelStartColumn
		else:
			columnNum1 = columnNum
		if columnNum1 < 0:
			return
		if self.pixelStartRow + rowNum > rR:
			rowNum1 = rR - self.pixelStartRow
		else:
			rowNum1 = rowNum
		if rowNum1 < 0:
			return
		# read raster
		iRB = rD.GetRasterBand(1)
		self.a1 =  iRB.ReadAsArray(self.pixelStartColumn, self.pixelStartRow, columnNum1, rowNum1)
		iRB2 = rD2.GetRasterBand(1)
		a2 =  iRB2.ReadAsArray(startColumn2, startRow2, columnNum1, rowNum1)
		# expression
		if cfg.ui.use_expression_checkBox.isChecked() is True:
			expression = " " + cfg.ui.expression_lineEdit.text() + " "
			e = self.checkExpression(expression, editValue)
			if e == "No":
				return "No"
			else:
				dataArray = eval(e)
		else:
			value = editValue
			dataArray = cfg.np.where(a2 >0 , value, self.a1)
		iRB = None
		iRB2 = None
		self.writeArrayBlock(rD, 1, dataArray, self.pixelStartColumn, self.pixelStartRow)
		rD = None
		rD2 = None

	# reload vector list
	def reloadVectorList(self):
		cfg.utls.refreshVectorLayer()
		
	# text changed
	def textChanged(self):
		expression = " " + cfg.ui.expression_lineEdit.text() + " "
		self.checkExpression(expression, 0)
		
	# check the expression and return it
	def checkExpression(self, expression, editValue):
		expr = expression
		expr = expr.replace(cfg.variableName, "self.a1")
		# replace numpy operators
		expr = cfg.utls.replaceNumpyOperators(expr)
		# value from vector
		expr = expr.replace(cfg.vectorVariableName, str(editValue))
		e = "cfg.np.where(a2 >0 ," + expr + ", self.a1)"
		# test
		ar1 = cfg.np.arange(9).reshape(3, 3)
		eCopy = e
		eCopy = eCopy.replace("self.a1", "ar1")
		eCopy = eCopy.replace("a2", "ar1")
		try:
			o = eval(eCopy)
			cfg.ui.expression_lineEdit.setStyleSheet("color : green")
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return e
		except Exception as err:
			cfg.ui.expression_lineEdit.setStyleSheet("color : red")
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
					
	# undo edit
	def undoEdit(self):
		try:
			b = cfg.utls.selectLayerbyName(self.rstrNm, "Yes")
			rSource = cfg.utls.layerSource(b)
			# open input with GDAL
			rD = cfg.gdalSCP.Open(rSource, cfg.gdalSCP.GA_Update)
			if rD is None:
				return "No"
			self.writeArrayBlock(rD, 1, self.a1, self.pixelStartColumn, self.pixelStartRow)
			rD = None
			b.reload()
			b.triggerRepaint()
			cfg.cnvs.refresh()
			cfg.ui.undo_edit_Button.setEnabled(False)
			cfg.undoEditRasterToolbar_toolButton.setEnabled(False)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		except:
			pass
		
	# write an array to band
	def writeArrayBlock(self, gdalRaster, bandNumber, dataArray, pixelStartColumn, pixelStartRow):
		b = gdalRaster.GetRasterBand(bandNumber)
		b.WriteArray(dataArray, pixelStartColumn, pixelStartRow)
		b.FlushCache()
		b = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		
	# checkbox changed
	def checkboxVectorFieldChanged(self):
		cfg.ui.use_constant_val_checkBox.blockSignals(True)
		cfg.ui.use_expression_checkBox.blockSignals(True)
		cfg.ui.use_field_vector_checkBox.blockSignals(True)
		if cfg.ui.use_field_vector_checkBox.isChecked():
			cfg.ui.use_expression_checkBox.setCheckState(0)
			cfg.ui.use_constant_val_checkBox.setCheckState(0)
		else:
			cfg.ui.use_field_vector_checkBox.setCheckState(2)
		cfg.ui.use_expression_checkBox.blockSignals(False)
		cfg.ui.use_constant_val_checkBox.blockSignals(False)	
		cfg.ui.use_field_vector_checkBox.blockSignals(False)
		cfg.ui.edit_val_use_vector_radioButton.setChecked(True)
		
	# checkbox changed
	def checkboxConstantValChanged(self):
		cfg.ui.use_constant_val_checkBox.blockSignals(True)
		cfg.ui.use_expression_checkBox.blockSignals(True)
		cfg.ui.use_field_vector_checkBox.blockSignals(True)
		if cfg.ui.use_constant_val_checkBox.isChecked():
			cfg.ui.use_expression_checkBox.setCheckState(0)
			cfg.ui.use_field_vector_checkBox.setCheckState(0)
		else:
			cfg.ui.use_constant_val_checkBox.setCheckState(2)
		cfg.ui.use_expression_checkBox.blockSignals(False)
		cfg.ui.use_constant_val_checkBox.blockSignals(False)	
		cfg.ui.use_field_vector_checkBox.blockSignals(False)	
		
	# checkbox changed
	def checkboxUseExpressionChanged(self):
		cfg.ui.use_expression_checkBox.blockSignals(True)
		cfg.ui.use_constant_val_checkBox.blockSignals(True)
		cfg.ui.use_field_vector_checkBox.blockSignals(True)
		if cfg.ui.use_expression_checkBox.isChecked():
			cfg.ui.use_constant_val_checkBox.setCheckState(0)
			cfg.ui.use_field_vector_checkBox.setCheckState(0)
		else:
			cfg.ui.use_expression_checkBox.setCheckState(2)
		cfg.ui.use_expression_checkBox.blockSignals(False)
		cfg.ui.use_constant_val_checkBox.blockSignals(False)
		cfg.ui.use_field_vector_checkBox.blockSignals(False)
		
	# radio button changed
	def radioUseROIPolygonChanged(self):
		cfg.ui.edit_val_use_ROI_radioButton.blockSignals(True)
		cfg.ui.edit_val_use_vector_radioButton.blockSignals(True)
		if cfg.ui.edit_val_use_ROI_radioButton.isChecked():
			cfg.ui.edit_val_use_vector_radioButton.setChecked(False)
		else:
			cfg.ui.edit_val_use_vector_radioButton.setChecked(True)
		cfg.ui.edit_val_use_ROI_radioButton.blockSignals(False)
		cfg.ui.edit_val_use_vector_radioButton.blockSignals(False)
		if cfg.ui.use_field_vector_checkBox.isChecked():
			cfg.ui.use_constant_val_checkBox.setCheckState(2)
			
	# radio button changed
	def radioUseVectorChanged(self):
		cfg.ui.edit_val_use_ROI_radioButton.blockSignals(True)
		cfg.ui.edit_val_use_vector_radioButton.blockSignals(True)
		if cfg.ui.edit_val_use_vector_radioButton.isChecked():
			cfg.ui.edit_val_use_ROI_radioButton.setChecked(False)
		else:
			cfg.ui.edit_val_use_ROI_radioButton.setChecked(True)
		cfg.ui.edit_val_use_ROI_radioButton.blockSignals(False)
		cfg.ui.edit_val_use_vector_radioButton.blockSignals(False)
		
	# edit using toolbar values
	def toolbarEditValue(self, toolbarValue):
		if cfg.lstROI is None:
			cfg.mx.msg22()
			return
		self.rstrNm = cfg.ui.edit_raster_name_combo.currentText()
		b = cfg.utls.selectLayerbyName(self.rstrNm, "Yes")
		if b is not None:
			rSource = cfg.utls.layerSource(b)
			cfg.ui.undo_edit_Button.setEnabled(False)
			cfg.undoEditRasterToolbar_toolButton.setEnabled(False)
			# create feature list
			rId = []
			f = cfg.qgisCoreSCP.QgsFeature()
			for f in cfg.lstROI.getFeatures():
				rId.append(f.id())		
			vector = cfg.lstROI
			# hide ROI
			cfg.show_ROI_radioButton.setChecked(False)
			cfg.SCPD.showHideROI()
			self.setValueRaster(rSource, vector, rId, "No", None, toolbarValue)
			if b != "No":
				b.reload()
				b.triggerRepaint()
				cfg.cnvs.refresh()
				
	# toolbar value 0
	def toolbarValue0(self):
		self.toolbarEditValue(int(cfg.val0_spin.value()))
				
	# toolbar value 1
	def toolbarValue1(self):
		self.toolbarEditValue(int(cfg.val1_spin.value()))
		
	# toolbar value 2
	def toolbarValue2(self):
		self.toolbarEditValue(int(cfg.val2_spin.value()))
		