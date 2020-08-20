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

class CloudMasking:

	def __init__(self):
		pass
		
		
	# value text changed
	def textChanged(self):		
		self.checkValueList()
		
	# check value list
	def checkValueList(self):
		try:
			# class value list
			valueList = cfg.utls.textToValueList(cfg.ui.cloud_mask_classes_lineEdit.text())
			cfg.ui.cloud_mask_classes_lineEdit.setStyleSheet("color : green")
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		except Exception as err:
			cfg.ui.cloud_mask_classes_lineEdit.setStyleSheet("color : red")
			valueList = []
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		return valueList
		
		
	# mask band sets
	def maskAction(self):
		self.cloudMaskingBandSet()
		
	# cloud masking
	def cloudMaskingBandSet(self, batch = "No", bandSetNumber = None, inputClassification = None, outputDirectory = None):
		# class value list
		valueList = self.checkValueList()
		if len(valueList) > 0:
			if bandSetNumber is None:
				bandSet = cfg.ui.band_set_comb_spinBox_9.value()
				bandSetNumber = bandSet - 1
			if bandSetNumber >= len(cfg.bandSetsList):
				cfg.mx.msgWar25(bandSetNumber + 1)
				return "No"
			if inputClassification is None:
				clssfctnNm = cfg.ui.classification_name_combo_4.currentText()
				clss = cfg.utls.selectLayerbyName(clssfctnNm, "Yes")
				inputClassification = cfg.utls.layerSource(clss)
			if batch == "No":
				o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
			else:
				o = outputDirectory
			if len(o) > 0:
				if batch == "No":
					cfg.uiUtls.addProgressBar()
				bndSetSources = []
				# create list of rasters
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
				else:
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar29()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
					return "No"
				if cfg.bandSetsList[bandSetNumber][0] == "Yes":
					ckB = cfg.utls.checkBandSet(bandSetNumber)
					bndSetIf = "Yes"
				else:
					ckB = cfg.utls.checkImageBandSet(bandSetNumber)
					bndSetIf = "No"
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
				rEPSG = cfg.utls.getEPSGRaster(cfg.bndSetLst[0])				
				if rEPSG is None:
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar28()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
					return "No"	
				cfg.uiUtls.updateBar(20)
				EPSG = cfg.utls.getEPSGRaster(inputClassification)
				if str(EPSG) != str(rEPSG):
					nD = cfg.utls.imageNoDataValue(inputClassification)
					if nD is None:
						nD = cfg.NoDataVal
					# date time for temp name
					dT = cfg.utls.getTime()
					tPMN = dT + cfg.calcRasterNm + ".tif"
					tPMD = cfg.tmpDir + "/" + tPMN
					cfg.utls.GDALReprojectRaster(inputClassification, tPMD, "GTiff", None, "EPSG:" + str(rEPSG), "-ot Float32 -dstnodata " + str(nD))
					if cfg.osSCP.path.isfile(tPMD):
						inputClassification = tPMD
					else:
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
						cfg.mx.msgErr60()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
						return "No"
				if cfg.ui.cloud_buffer_checkBox.isChecked() is True:
					size =  cfg.ui.cloud_buffer_spinBox.value()
					struct = cfg.utls.create3x3Window()
					# open input with GDAL
					rD = cfg.gdalSCP.Open(inputClassification, cfg.gdalSCP.GA_ReadOnly)
					# band list
					bL = cfg.utls.readAllBandsFromRaster(rD)
					input = rD
					for s in range(0, size):
						# date time for temp name
						dT = cfg.utls.getTime()
						tPMD = cfg.tmpDir + "/" + dT + "buffer" + str(s) + ".tif"
						tempRasterList = []
						tempRasterList.append(tPMD)
						# create rasters
						oMR = cfg.utls.createRasterFromReference(rD, 1, tempRasterList, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21")
						cfg.uiUtls.updateBar(21)
						o = cfg.utls.processRaster(input, bL, None, "No", cfg.utls.rasterDilation, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", struct, valueList, "buffer ")
						cfg.uiUtls.updateBar(22)
						# boundaries
						o = cfg.utls.processRasterBoundaries(input, bL, None, "No", cfg.utls.rasterDilationBoundaries, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", struct, valueList, "buffer ", 2)
						cfg.uiUtls.updateBar(23)
						# close GDAL rasters
						for b in range(0, len(oMR)):
							oMR[b] = None
						for b in range(0, len(bL)):
							bL[b] = None
						rD = None
						# open input with GDAL
						rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
						# band list
						bL = cfg.utls.readAllBandsFromRaster(rD)
						input = rD
					for b in range(0, len(bL)):
						bL[b] = None
					rD = None
					if cfg.osSCP.path.isfile(tPMD):
						inputClassification = tPMD
					else:
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
						cfg.mx.msgErr60()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error")
						return "No"
				# No data value
				NoDataVal = cfg.ui.nodata_spinBox_11.value()
				nD = NoDataVal
				outputName = cfg.ui.mask_output_name_lineEdit.text()
				if len(outputName) > 0:
					outputName = str(outputName.encode('ascii','replace'))[2:-1] + "_" 
				cfg.uiUtls.updateBar(40)
				# create virtual raster
				for x in range(0, len(cfg.bndSetLst)):	
					bList = []
					bandNumberList = []
					bList.append(inputClassification)
					bandNumberList.append(1)			
					if bndSetIf == "Yes":
						bList.append(cfg.bndSetLst[x])
						bandNumberList.append(1)
					else:
						bList.append(cfg.bndSetLst[x])
						bandNumberList.append(x + 1)
					# date time for temp name
					dT = cfg.utls.getTime()
					tPMN1 = cfg.tmpVrtNm + str(x + 1) + ".vrt"
					tPMD1 = cfg.tmpDir + "/" + dT + tPMN1
					tPMN2 = dT + cfg.calcRasterNm + str(x + 1) + ".tif"
					tPMD2 = cfg.tmpDir + "/" + tPMN2
					# create virtual raster					
					vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD1, bandNumberList, "Yes", "Yes", 0, "No", "Yes")
					# open input with GDAL
					rD = cfg.gdalSCP.Open(tPMD1, cfg.gdalSCP.GA_ReadOnly)
					# band list
					bL = cfg.utls.readAllBandsFromRaster(rD)
					# output rasters
					oM = []
					oM.append(tPMD2)
					oMR = cfg.utls.createRasterFromReference(rD, 1, oM, nD, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
					# mask
					check = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.maskProcess, None, oMR, None, None, 0, None, nD, "No", NoDataVal, valueList, "Mosaic band " + str(x + 1), "Yes")
					# close GDAL rasters
					for b in range(0, len(oMR)):
						oMR[b] = None
					for b in range(0, len(bL)):
						bL[b] = None
					rD = None
					rstrOut = o + "/" + outputName + str(cfg.osSCP.path.splitext(cfg.osSCP.path.basename(cfg.bndSetLst[x]))[0]) + ".tif"
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
							
				