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

class SpectralDistanceBandsets:

	def __init__(self):
		pass
		
	# calculate distance band sets
	def calculateDistanceAction(self):
		self.spectralDistBandSets()
		
	# miniumum distance radioButton button changed
	def radioMinDistChanged(self):
		cfg.ui.min_distance_radioButton_2.blockSignals(True)
		cfg.ui.spectral_angle_map_radioButton_2.blockSignals(True)
		cfg.ui.min_distance_radioButton_2.setChecked(True)
		cfg.ui.spectral_angle_map_radioButton_2.setChecked(False)
		cfg.ui.min_distance_radioButton_2.blockSignals(False)
		cfg.ui.spectral_angle_map_radioButton_2.blockSignals(False)
		
	# SAM radioButton button changed
	def radioSAMChanged(self):
		cfg.ui.min_distance_radioButton_2.blockSignals(True)
		cfg.ui.spectral_angle_map_radioButton_2.blockSignals(True)
		cfg.ui.spectral_angle_map_radioButton_2.setChecked(True)
		cfg.ui.min_distance_radioButton_2.setChecked(False)
		cfg.ui.min_distance_radioButton_2.blockSignals(False)
		cfg.ui.spectral_angle_map_radioButton_2.blockSignals(False)
		thresh = cfg.ui.thresh_doubleSpinBox_2.value()
		if thresh > 90:
			cfg.mx.msg11()
			cfg.ui.thresh_doubleSpinBox_2.setValue(90)	
		
	# calculate distance band sets
	def spectralDistBandSets(self, firstBandSet = None, secondBandSet = None, outputDirectory = None, batch = "No"):
		if firstBandSet is None:
			bandSet = cfg.ui.band_set_comb_spinBox_6.value()
			firstBandSet = bandSet - 1
		if secondBandSet is None:
			bandSet = cfg.ui.band_set_comb_spinBox_7.value()
			secondBandSet = bandSet - 1
		bSL = []
		bSL.append(firstBandSet)
		bSL.append(secondBandSet)
		if batch == "No":
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		else:
			o = outputDirectory
		if len(o) > 0:
			outputName = cfg.spectralDistNm + str(firstBandSet + 1)+ "_" + str(secondBandSet + 1)
			if batch == "No":
				cfg.uiUtls.addProgressBar()
			bndSetSources = []
			bndSetIf = []
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
			bList = []
			bandNumberList = []
			for x in range(0, len(bndSetSources)):
				for y in range(0, len(bndSetSources[0])):						
					if bndSetIf[x] == "Yes":
						bList.append(bndSetSources[x][y])
						bandNumberList.append(1)
					else:
						bList.append(bndSetSources[x][y])
						bandNumberList.append(y + 1)
			if cfg.ui.min_distance_radioButton_2.isChecked() is True:
				alg = cfg.algMinDist
			else:
				alg = cfg.algSAM
			if cfg.ui.distance_threshold_checkBox.isChecked() is True:
				thresh = cfg.ui.thresh_doubleSpinBox_2.value()
			else:
				thresh = 0
			nD = cfg.utls.imageNoDataValue(bndSetSources[0][y])
			if nD is None:
				nD = NoDataVal
			# date time for temp name
			dT = cfg.utls.getTime()
			tPMN1 = cfg.tmpVrtNm + str(y + 1) + ".vrt"
			tPMD1 = cfg.tmpDir + "/" + dT + tPMN1
			tPMN2 = dT + cfg.calcRasterNm + ".tif"
			tPMD2 = cfg.tmpDir + "/" + tPMN2
			tPMN3 = dT + cfg.calcRasterNm + "_thresh" + ".tif"
			tPMD3 = cfg.tmpDir + "/" + tPMN3
			# create virtual raster
			vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD1, bandNumberList, "Yes", "Yes", 0, "No", "Yes")
			# open input with GDAL
			rD = cfg.gdalSCP.Open(tPMD1, cfg.gdalSCP.GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# output rasters
			oM = []
			oM.append(tPMD2)
			oM.append(tPMD3)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
			# distance
			check = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.spectralDistanceProcess, None, oMR, None, None, 0, None, nD, "No", NoDataVal, [alg, thresh], "Spectral distance ", "Yes")
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
			rstrOut = o + "/" + outputName + ".tif"
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
				cfg.utls.addRasterLayer(str(rstrOut), str(cfg.osSCP.path.basename(rstrOut)))
			if cfg.ui.distance_threshold_checkBox.isChecked() is True:
				rstrOut2 = o + "/" + outputName + "_change" + ".tif"
				if cfg.osSCP.path.isfile(tPMD3):
					cfg.cnvs.setRenderFlag(False)
					if cfg.rasterCompression != "No":
						try:
							cfg.utls.GDALCopyRaster(tPMD3, rstrOut2, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
							cfg.osSCP.remove(tPMD3)
						except Exception as err:
							cfg.shutilSCP.copy(tPMD3, rstrOut2)
							cfg.osSCP.remove(tPMD3)
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					else:
						cfg.shutilSCP.copy(tPMD3, rstrOut2)
						cfg.osSCP.remove(tPMD3)
					# add raster to layers
					c = cfg.utls.addRasterLayer(str(rstrOut2), str(cfg.osSCP.path.basename(rstrOut2)))
					rasterSymbol = cfg.utls.rasterScatterSymbol([[1,"#FF0000"]])
					cfg.utls.setRasterScatterSymbol(c, rasterSymbol)
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.updateBar(100)
			if batch == "No":
				cfg.utls.finishSound()
				cfg.uiUtls.removeProgressBar()
