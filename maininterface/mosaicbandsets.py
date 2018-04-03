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

class MosaicBandSets:

	def __init__(self):
		pass
		
	# list band sets
	def textChanged(self):
		self.checkValueList()
				
	# check value list
	def checkValueList(self):
		try:
			# class value list
			text = cfg.ui.mosaic_band_sets_lineEdit.text()
			list = text.split(",")
			valueList = []
			for v in list:
				valueList.append(int(v))
			cfg.ui.mosaic_band_sets_lineEdit.setStyleSheet("color : green")
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		except Exception as err:
			cfg.ui.mosaic_band_sets_lineEdit.setStyleSheet("color : red")
			valueList = []
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		return valueList
		
	# mosaic band sets
	def mosaicAction(self):
		self.mosaicBandSets()
		
	# mosaic multiple band sets
	def mosaicBandSets(self, batch = "No", outputDirectory = None, bandSetList = None):
		if bandSetList is None:
			bandSetList = cfg.mosaicBS.checkValueList()
		else:
			bandSetList = eval(bandSetList)
		if len(bandSetList) > 0:
			bSL = []
			for v in bandSetList:
				bSL.append(v-1)
			if batch == "No":
				o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
			else:
				o = outputDirectory
			if len(o) > 0:
				outputName = cfg.ui.mosaic_output_name_lineEdit.text()
				if len(outputName) > 0:
					outputName = str(outputName.encode('ascii','replace'))[2:-1] + "_" 
				bndSetSources = []
				bndSetIf = []
				if batch == "No":
					cfg.uiUtls.addProgressBar()
				# create list of rasters
				for bandSetNumber in bSL:
					try:
						cfg.bandSetsList[bandSetNumber][0]
					except:
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
						cfg.mx.msgWar28()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
						return "No"
					if cfg.bandSetsList[bandSetNumber][0] == "Yes":
						ckB = cfg.utls.checkBandSet(bandSetNumber)
						bndSetIf.append("Yes")
					else:
						ckB = cfg.utls.checkImageBandSet(bandSetNumber)
						bndSetIf.append("No")
					if ckB == "Yes":
						bndSetSources.append(cfg.bndSetLst)
					if len(cfg.bndSetLst) == 0:
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
						cfg.mx.msgWar28()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
						return "No"
				cfg.uiUtls.updateBar(10)
				rEPSG = cfg.utls.getEPSGRaster(bndSetSources[0][0])				
				if rEPSG is None:
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar28()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
					return "No"	
				cfg.uiUtls.updateBar(20)
				# No data value
				if cfg.ui.nodata_checkBox_9.isChecked() is True:
					NoDataVal = cfg.ui.nodata_spinBox_10.value()
				else:
					NoDataVal = cfg.NoDataVal
				for bst in bndSetSources:
					if len(bst) != len(bndSetSources[0]):
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
						cfg.mx.msgWar28()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
						return "No"
					bstIndex = bndSetSources.index(bst)
					for b in range(0, len(bst)):						
						EPSG = cfg.utls.getEPSGRaster(bst[b])
						if str(EPSG) != str(rEPSG):
							if cfg.bandSetsList[bstIndex][0] == "Yes":
								nD = cfg.utls.imageNoDataValue(bst[b])
								if nD is None:
									nD = NoDataVal
								# date time for temp name
								dT = cfg.utls.getTime()
								tPMN = dT + cfg.calcRasterNm + ".tif"
								tPMD = cfg.tmpDir + "/" + tPMN
								cfg.utls.GDALReprojectRaster(bst[b], tPMD, "GTiff", None, "EPSG:" + str(rEPSG), "-ot Float32 -dstnodata " + str(nD))
								if cfg.osSCP.path.isfile(tPMD):
									bndSetSources[bstIndex][b] = tPMD
								else:
									if batch == "No":
										cfg.uiUtls.removeProgressBar()
									cfg.mx.msgErr60()
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
									return "No"
							else:
								nD = cfg.utls.imageNoDataValue(bst[b])
								if nD is None:
									nD = NoDataVal
								# date time for temp name
								dT = cfg.utls.getTime()
								tPMN = dT + cfg.calcRasterNm + ".tif"
								tPMD = cfg.tmpDir + "/" + tPMN
								cfg.utls.GDALReprojectRaster(bst[b], tPMD, "GTiff", None, "EPSG:" + str(rEPSG), "-ot Float32 -dstnodata " + str(nD))
								if cfg.osSCP.path.isfile(tPMD):
									for bb in range(0, len(bst)):
										bndSetSources[bstIndex][bb] = tPMD
									break
								else:
									if batch == "No":
										cfg.uiUtls.removeProgressBar()
									cfg.mx.msgErr60()
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
									return "No"
				cfg.uiUtls.updateBar(40)
				for y in range(0, len(bndSetSources[0])):
					bList = []
					bandNumberList = []
					for x in range(0, len(bndSetSources)):
						bstIndex = bndSetSources.index(bndSetSources[x])
						if bndSetIf[bstIndex] == "Yes":
							bList.append(bndSetSources[x][y])
							bandNumberList.append(1)
						else:
							bList.append(bndSetSources[x][y])
							bandNumberList.append(y + 1)
					nD = cfg.utls.imageNoDataValue(bndSetSources[0][y])
					if nD is None:
						nD = NoDataVal
					# date time for temp name
					dT = cfg.utls.getTime()
					tPMN1 = cfg.tmpVrtNm + str(y + 1) + ".vrt"
					tPMD1 = cfg.tmpDir + "/" + dT + tPMN1
					tPMN2 = dT + cfg.calcRasterNm + str(y + 1) + ".tif"
					tPMD2 = cfg.tmpDir + "/" + tPMN2
					# create virtual raster					
					vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD1, bandNumberList, "Yes", NoDataVal, 0, "No", "No")
					# open input with GDAL
					rD = cfg.gdalSCP.Open(tPMD1, cfg.gdalSCP.GA_ReadOnly)
					# band list
					bL = cfg.utls.readAllBandsFromRaster(rD)
					# output rasters
					oM = []
					oM.append(tPMD2)
					oMR = cfg.utls.createRasterFromReference(rD, 1, oM, nD, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
					# mosaic
					check = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.mosaicProcess, None, oMR, None, None, 0, None, nD, "No", NoDataVal, None, "Mosaic band " + str(y + 1), "Yes")
					# close GDAL rasters
					for b in range(0, len(oMR)):
						oMR[b] = None
					for b in range(0, len(bL)):
						bL[b] = None
					rD = None
					rstrOut = o + "/" + outputName + str(cfg.osSCP.path.splitext(cfg.osSCP.path.basename(bndSetSources[0][y]))[0]) + ".tif"
					if cfg.osSCP.path.isfile(tPMD2):
						cfg.cnvs.setRenderFlag(False)
						if cfg.rasterCompression != "No":
							try:
								cfg.utls.GDALCopyRaster(tPMD2, rstrOut, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
								cfg.osSCP.remove(tPMD2)
							except Exception as err:
								cfg.shutilSCP.copy(tPMD2, rstrOut)
								cfg.osSCP.remove(tPMD2)
								# logger
								if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						else:
							cfg.shutilSCP.copy(tPMD2, rstrOut)
							cfg.osSCP.remove(tPMD2)
						# add raster to layers
						cfg.utls.addRasterLayer(str(rstrOut))
				cfg.cnvs.setRenderFlag(True)
				cfg.uiUtls.updateBar(100)
				if batch == "No":
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
							
				