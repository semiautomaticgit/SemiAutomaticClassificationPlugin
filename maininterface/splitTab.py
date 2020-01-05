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

class SplitTab:

	def __init__(self):
		pass
		
	# raster name
	def rasterLayerName(self):
		self.rstrLyNm = cfg.ui.raster_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster name: " + self.rstrLyNm)
		
	def refreshClassificationLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.raster_name_combo.clear()
		# raster name
		self.rstrLyNm = None
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type()== cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() > 1:
					cfg.dlg.raster_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster layers refreshed")
		
	# split raster button
	def splitRaster(self):
		try:
			i = len(cfg.ui.raster_name_combo.currentText())
		except:
			self.refreshClassificationLayer()
			return "No"
		if i > 0:
			self.splitRasterToBands(self.rstrLyNm)
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " split raster layer to band")
		else:
			self.refreshClassificationLayer()
		
	# split raster to bands
	def splitRasterToBands(self, rasterName, batch = "No",  inputFile = None, outputDirectory = None):
		if batch == "No":
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		else:
			o = outputDirectory
		outputName = cfg.ui.output_name_lineEdit.text()
		if len(outputName) > 0:
			outputName = str(outputName.encode('ascii','replace'))[2:-1] + "_" 
		if len(o) > 0:
			oDir = cfg.utls.makeDirectory(o)
			if oDir is None:
				if batch == "No":
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr58()
				return "No"
			if batch == "No":
				# disable map canvas render for speed
				cfg.cnvs.setRenderFlag(False)
				cfg.uiUtls.addProgressBar()
				i = cfg.utls.selectLayerbyName(rasterName, "Yes")
				rPath = cfg.utls.layerSource(i)
			else:
				rPath = inputFile
			try:
				iL = cfg.utls.rasterToBands(rPath, cfg.tmpDir, outputName + rasterName, "Yes")
				for r in iL:
					if cfg.rasterCompression != "No":
						try:
							cfg.utls.GDALCopyRaster(r, o + "/" + cfg.osSCP.path.basename(r), "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						except Exception as err:
							cfg.shutilSCP.copy(r, o + "/" + cfg.osSCP.path.basename(r))
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					else:
						cfg.shutilSCP.copy(r, o + "/" + cfg.osSCP.path.basename(r))
					cfg.utls.addRasterLayer(o + "/" + cfg.osSCP.path.basename(r), cfg.osSCP.path.basename(r))
					cfg.osSCP.remove(r)
				if batch == "No":
					cfg.utls.finishSound()
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " end split raster layer to band")
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				if batch == "No":
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr32()
				return "No"
				