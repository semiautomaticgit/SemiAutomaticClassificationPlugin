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

class StackRasterBands:

	def __init__(self):
		pass
		
	# stack raster
	def stackAction(self):
		self.stackRasters()
		
	# stack multiple rasters
	def stackRasters(self, batch = "No", outputFile = None, bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		cfg.uiUtls.addProgressBar()
		if cfg.bandSetsList[bandSetNumber][0] == "Yes":
			ckB = cfg.utls.checkBandSet(bandSetNumber)
			if ckB == "Yes":
				if len(cfg.bndSetLst) == 0:
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar28()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
					return "No"
				if outputFile is None:
					rstrOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster"), "", "*.tif", "tif")
					if rstrOut is False:
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
						return "No"
				else:
					rstrOut = outputFile
		else:
			cfg.mx.msgWar15()
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
			return "No"
		if rstrOut is not False:
			if rstrOut.lower().endswith(".tif"):
				pass
			else:
				rstrOut = rstrOut + ".tif"
			if outputFile is None:
				cfg.uiUtls.addProgressBar()
			
			cfg.uiUtls.updateBar(10)
			st = cfg.utls.mergeRasterBands(cfg.bndSetLst, rstrOut)
			if cfg.osSCP.path.isfile(rstrOut):
				cfg.cnvs.setRenderFlag(False)
				cfg.utls.addRasterLayer(str(rstrOut), str(cfg.osSCP.path.basename(rstrOut)))
				cfg.cnvs.setRenderFlag(True)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster: " + str(st))
				cfg.uiUtls.updateBar(100)
			if outputFile is None:
				if batch == "No":
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
				