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

class StackRasterBands:

	def __init__(self):
		pass
	
			
	# Set rasters checklist
	def rasterNameList(self):
		ls = cfg.lgnd.layers()
		# checklist
		lst = cfg.ui.raster_listView_3
		# create band item model
		cfg.bndMdls2 = cfg.QtGuiSCP.QStandardItemModel(lst)
		cfg.bndMdls2.clear()
		lst.setModel(cfg.bndMdls2)
		lst.show()
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					# band name
					it = cfg.QtGuiSCP.QStandardItem(l.name())
					# Create checkbox
					it.setCheckable(True)
					# Add band to model
					cfg.bndMdls2.appendRow(it)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster name checklist created")
		
	# set all bands to state 0 or 2
	def allRasterSetState(self, value):
		# checklist
		l = cfg.ui.raster_listView_3
		# count rows in checklist
		c = l.model().rowCount()
		for b in range(0, c):
			if cfg.actionCheck == "Yes":
				cfg.bndMdls2.item(b).setCheckState(value)
				cfg.uiUtls.updateBar((b+1) * 100 / (c))
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all rasters cancelled")
		
	# stack raster
	def stackAction(self):
		self.stackRasters()
	
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
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all rasters clicked")
				
	# set all bands to state 0 or 2
	def allRasterSetState(self, value):
		# checklist
		l = cfg.ui.raster_listView_3
		# count rows in checklist
		c = l.model().rowCount()
		for b in range(0, c):
			if cfg.actionCheck == "Yes":
				cfg.bndMdls2.item(b).setCheckState(value)
				cfg.uiUtls.updateBar((b+1) * 100 / (c))
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all rasters cancelled")
				
		
	# stack multiple rasters
	def stackRasters(self, batch = "No", fileListString = None, outputFile = None):
		rT = []	
		if batch == "No":
			cfg.uiUtls.addProgressBar()
			# checklist
			lst = cfg.ui.raster_listView_3
			# count rows in checklist
			c = lst.model().rowCount()
			for x in range(0, c):
				# If checkbox is activated
				if cfg.bndMdls2.item(x).checkState() == 2:
					# name of item of list
					itN = cfg.bndMdls2.item(x).text()
					itS = cfg.utls.selectLayerbyName(itN, "Yes")
					try:
						rT.append(itS.source())
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.mx.msgErr9()
			if len(rT) == 0:
				cfg.mx.msgWar15()
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
				return "No"
			if outputFile is None:
				rstrOut = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster"), "", "*.tif")
			else:
				rstrOut = outputFile
		else:
			fileList = fileListString.split(",")
			for f in fileList:
				rT.append(f.strip())
			rstrOut = outputFile
		if len(rstrOut) > 0:
			if outputFile is None:
				cfg.uiUtls.addProgressBar()
			cfg.cnvs.setRenderFlag(False)
			if unicode(rstrOut).endswith(".tif"):
				rstrOut = rstrOut
			else:
				rstrOut = rstrOut + ".tif"
			cfg.uiUtls.updateBar(10)
			# date time for temp name
			dT = cfg.utls.getTime()
			tPMN2 = dT + cfg.calcRasterNm + ".tif"
			tPMD2 = cfg.tmpDir + "/" + tPMN2
			st = cfg.utls.mergeRasterBands(rT, tPMD2)
			if cfg.osSCP.path.isfile(tPMD2):
				if cfg.rasterCompression != "No":
					try:
						cfg.utls.GDALCopyRaster(tPMD2, rstrOut, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						cfg.osSCP.remove(tPMD2)
					except Exception, err:
						cfg.shutilSCP.copy(tPMD2, rstrOut)
						cfg.osSCP.remove(tPMD2)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					cfg.shutilSCP.copy(tPMD2, rstrOut)
					cfg.osSCP.remove(tPMD2)
				# add raster to layers
				cfg.iface.addRasterLayer(unicode(rstrOut), unicode(cfg.osSCP.path.basename(rstrOut)))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster: " + str(st))
				cfg.uiUtls.updateBar(100)
			if outputFile is None:
				cfg.utls.finishSound()
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
				