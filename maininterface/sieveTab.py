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

class SieveRaster:

	def __init__(self):
		pass
		
	# sieve classification
	def sieveClassificationAction(self):
		self.sieveClassification()
		
	# sieve classification
	def sieveClassification(self, batch = "No", rasterInput = None, rasterOutput = None):
		if batch == "No":
			outputRaster = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save output"), "", "*.tif", "tif")
		else:
			outputRaster = rasterOutput
		if outputRaster is not False:
			if outputRaster.lower().endswith(".tif"):
				pass
			else:
				outputRaster = outputRaster + ".tif"
			if batch == "No":
				cfg.uiUtls.addProgressBar()
				raster = cfg.ui.sieve_raster_name_combo.currentText()
				b = cfg.utls.selectLayerbyName(raster, "Yes")
			else:
				b = "No"
			if b is not None:
				if batch == "No":
					rSource = cfg.utls.layerSource(b)
				else:
					if cfg.osSCP.path.isfile(rasterInput):
						rSource = rasterInput
					else:
						return "No"
				cfg.uiUtls.updateBar(40)
				pixelThreshold =  cfg.ui.sieve_threshold_spinBox.value()
				connect = cfg.ui.sieve_connection_combo.currentText()
				cfg.utls.rasterSieve(rSource, outputRaster, pixelThreshold, connect)
				if cfg.osSCP.path.isfile(outputRaster):
					r =cfg.utls.addRasterLayer(outputRaster, cfg.osSCP.path.basename(outputRaster))
				else:
					return "No"
				if b != "No":
					cfg.utls.copyRenderer(b, r)
				if batch == "No":
					cfg.utls.finishSound()
					cfg.uiUtls.updateBar(100)
					cfg.uiUtls.removeProgressBar()
			else:
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
				cfg.utls.refreshClassificationLayer()
				cfg.mx.msgErr9()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error raster not found")
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			