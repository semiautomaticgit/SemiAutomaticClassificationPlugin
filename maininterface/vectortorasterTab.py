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

class VectorToRasterTab:

	def __init__(self):
		pass
	
	# convert to raster
	def convertToRasterAction(self):
		self.convertToRaster()
		
	# convert to raster
	def convertToRaster(self, batch = "No", rasterOutput = None, vectorPath = None, fieldName = None, rasterPath = None):
		if batch == "No":
			vector = cfg.ui.vector_name_combo.currentText()
			l = cfg.utls.selectLayerbyName(vector)
			referenceRasterName = cfg.ui.reference_raster_name_combo.currentText()
			r = cfg.utls.selectLayerbyName(referenceRasterName)
			if l is None or r is None:
				cfg.utls.refreshVectorLayer()
				cfg.utls.refreshClassificationLayer()
				return
			vectorSource = cfg.utls.layerSource(l)
			referenceRasterPath = cfg.utls.layerSource(r)
			fd = cfg.ui.field_comboBox.currentText()
			if len(fd) == 0 and cfg.ui.field_checkBox.isChecked():
				cfg.utls.refreshVectorLayer()
				return
			rstrOut = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster output"), "", "*.tif", "tif")
		else:
			vectorSource = vectorPath
			referenceRasterPath = rasterPath
			referenceRasterName = "No"
			rstrOut = rasterOutput
			fd = fieldName
		if rstrOut is not False:
			if rstrOut.lower().endswith(".tif"):
				pass
			else:
				rstrOut = rstrOut + ".tif"
			if batch == "No":
				cfg.uiUtls.addProgressBar()
				# disable map canvas render for speed
				cfg.cnvs.setRenderFlag(False)
			# date time for temp name
			dT = cfg.utls.getTime()
			# vector EPSG
			if "MultiPolygon?crs=PROJCS" in str(vectorSource):
				# temp shapefile
				tSHP = cfg.tmpDir + "/" + cfg.rclssTempNm + dT + ".shp"
				l = cfg.utls.saveMemoryLayerToShapefile(l, tSHP)
				vectorSource = tSHP
			if cfg.ui.field_checkBox.isChecked():
				burnValues = None
			else:
				burnValues = cfg.ui.constant_value_spinBox.value()
			cfg.uiUtls.updateBar(10)
			if cfg.ui.conversion_type_combo.currentText() == cfg.centerOfPixels:
				conversionType = None
			else:
				conversionType = "ALL_TOUCHED"
			# convert vector layer to raster		
			check = cfg.utls.vectorToRaster(fd, vectorSource, referenceRasterName, rstrOut, referenceRasterPath, conversionType, "GTiff", burnValues)
			cfg.uiUtls.updateBar(100)
			# add raster to layers
			if cfg.osSCP.path.isfile(rstrOut):
				rstr = cfg.utls.addRasterLayer(rstrOut, cfg.osSCP.path.basename(rstrOut))
			else:
				return "No"
			cfg.utls.rasterSymbolSingleBandGray(rstr)
			if batch == "No":
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.utls.finishSound()
				cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "finished")
		
	# reload vector list
	def reloadVectorList(self):
		cfg.utls.refreshVectorLayer()
				
	# checkbox changed
	def checkboxConstantValueChanged(self):
		cfg.ui.field_checkBox.blockSignals(True)
		cfg.ui.constant_value_checkBox.blockSignals(True)
		if cfg.ui.constant_value_checkBox.isChecked():
			cfg.ui.field_checkBox.setCheckState(0)
		else:
			cfg.ui.field_checkBox.setCheckState(2)
		cfg.ui.field_checkBox.blockSignals(False)
		cfg.ui.constant_value_checkBox.blockSignals(False)	
		
	# checkbox changed
	def checkboxFieldChanged(self):
		cfg.ui.field_checkBox.blockSignals(True)
		cfg.ui.constant_value_checkBox.blockSignals(True)
		if cfg.ui.field_checkBox.isChecked():
			cfg.ui.constant_value_checkBox.setCheckState(0)
		else:
			cfg.ui.constant_value_checkBox.setCheckState(2)
		cfg.ui.field_checkBox.blockSignals(False)
		cfg.ui.constant_value_checkBox.blockSignals(False)