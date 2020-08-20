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

class BandCombination:

	def __init__(self):
		self.clssfctnNm = None
		
	# calculate band set combination if click on button
	def calculateBandSetCombination(self):
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " calculate Cross Classification ")
		self.bandSetCombination()
	
	# cross classification calculation
	def bandSetCombination(self, batch = "No", bandSet = None, rasterOutput = None):
		if batch == "No":
			combRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save cross classification raster output"), "", "*.tif", "tif")
		else:
			combRstPath = rasterOutput
		if combRstPath is not False:
			if combRstPath.lower().endswith(".tif"):
				pass
			else:
				combRstPath = combRstPath + ".tif"
			if bandSet is None:
				bandSet = cfg.ui.band_set_comb_spinBox.value()
			bandSetNumber = bandSet - 1
			if batch == "No":
				cfg.uiUtls.addProgressBar()
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
			if ckB != "Yes":
				pass
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
			NoDataVal = cfg.NoDataVal				
			for b in range(0, len(cfg.bndSetLst)):						
				EPSG = cfg.utls.getEPSGRaster(cfg.bndSetLst[b])
				if str(EPSG) != str(rEPSG):
					if cfg.bandSetsList[bandSetNumber][0] == "Yes":
						nD = cfg.utls.imageNoDataValue(cfg.bndSetLst[b])
						if nD is None:
							nD = NoDataVal
						# date time for temp name
						dT = cfg.utls.getTime()
						tPMN = dT + cfg.calcRasterNm + ".tif"
						tPMD = cfg.tmpDir + "/" + tPMN
						cfg.utls.GDALReprojectRaster(cfg.bndSetLst[b], tPMD, "GTiff", None, "EPSG:" + str(rEPSG), "-ot Float32 -dstnodata " + str(nD))
						if cfg.osSCP.path.isfile(tPMD):
							cfg.bndSetLst[b] = tPMD
						else:
							if batch == "No":
								cfg.uiUtls.removeProgressBar()
							cfg.mx.msgErr60()
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Warning")
							return "No"
			cfg.uiUtls.updateBar(40)
			bandsUniqueVal = []
			bList = []
			bandNumberList = []
			for b in range(0, len(cfg.bndSetLst)):
				# open input with GDAL
				refRstrDt = cfg.gdalSCP.Open(cfg.bndSetLst[b], cfg.gdalSCP.GA_ReadOnly)
				# No data value
				nD = cfg.utls.imageNoDataValue(cfg.bndSetLst[b])
				if nD is None:
					nD = NoDataVal
				# combination finder
				# band list
				bLR = cfg.utls.readAllBandsFromRaster(refRstrDt)
				cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
				cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
				o = cfg.utls.processRaster(refRstrDt, bLR, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, nD, "No", None, None, "UniqueVal")
				cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
				refRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)
				for d in range(0, len(bLR)):
					bLR[d] = None
				refRstrDt = None
				try:
					refRasterBandUniqueVal.remove(nD)
				except:
					pass
				bandsUniqueVal.append(refRasterBandUniqueVal)
				bList.append(cfg.bndSetLst[b])
				bandNumberList.append(1)
			try:
				cmb = list(cfg.itertoolsSCP.product(*bandsUniqueVal))
			except Exception as err:
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr63()
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			# No data value
			nD = cfg.utls.imageNoDataValue(cfg.bndSetLst[0])
			if nD is None:
				nD = NoDataVal
			# date time for temp name
			dT = cfg.utls.getTime()			
			# temp raster layer
			tPMN = cfg.tmpVrtNm + ".vrt"
			tPMD = cfg.tmpDir + "/" + dT + tPMN
			tPMN2 = cfg.bsCombTempNm + dT + ".tif"
			tPMD2 = cfg.tmpDir + "/" + tPMN2
			tblOut = cfg.osSCP.path.dirname(combRstPath) + "/" + cfg.osSCP.path.basename(combRstPath)
			tblOut = cfg.osSCP.path.splitext(tblOut)[0] + ".csv"
			# create virtual raster					
			vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "Yes")
			# combinations
			cmbntns = []
			# expression builder
			n = 1
			e = []
			for c in cmb:
				combi = ""
				expr = "cfg.np.where( "
				for i in range(0, len(c)):
					if str(c[i]) == "nan":
						skip = "Yes"
						break
					else:
						skip = "No"
						if str(c[i]).endswith('.0'):
							combi = combi + str(c[i]).split('.')[0]
						else:
							combi = combi + str(c[i])
						expr = expr + "(im" + str(i) + " == " + str(c[i]) + ")"
						if i < (len(c) - 1):
							combi = combi + " "
							expr = expr + " & "
				if skip == "No":
					expr = expr + ", " + str(n) + ", 0)"
					e.append(expr)
					cmbntns.append([n, combi])
					n = n + 1
			# open input with GDAL
			rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
			# output rasters
			oM = []
			oM.append(tPMD2)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# calculation
			variableList = []
			for c in range(0, len(cmb[0])):
				variableList.append(["im" + str(c), "im" + str(c)])
			cfg.rasterBandUniqueVal = {}
			o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.bandCalculationMultipleWhere, None, oMR, None, None, 0, None, nD, "No", e, variableList, "Calculating raster")
			cfg.rasterBandUniqueVal.pop(nD, None)
			if o == "No":
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr45()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error")
				return "No"
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "cross raster output: " + str(combRstPath))
			# pixel size
			cRG = oMR[0].GetGeoTransform()
			cRPX = abs(cRG[1])
			cRPY = abs(cRG[5])
			# check projections
			cRP = oMR[0].GetProjection()
			cRSR = cfg.osrSCP.SpatialReference(wkt=cRP)
			un = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unknown")
			if cRSR.IsProjected:
				un = cRSR.GetAttrValue('unit')
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
			if cfg.rasterCompression != "No":
				try:
					cfg.utls.GDALCopyRaster(tPMD2, combRstPath, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
					cfg.osSCP.remove(tPMD2)
				except Exception as err:
					cfg.shutilSCP.copy(tPMD2, combRstPath)
					cfg.osSCP.remove(tPMD2)
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			else:
				cfg.shutilSCP.copy(tPMD2, combRstPath)
				cfg.osSCP.remove(tPMD2)
			cfg.uiUtls.updateBar(80)
			try:
				l = open(tblOut, 'w')
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'RasterValue') + "\t" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Combination') + "\t" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'PixelSum') + "\t" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Area [' + un + "^2]") + str("\n")
			l.write(t)
			for c in cmbntns:
				try:
					v = c[0]
					if cfg.rasterBandUniqueVal[v] > 0:
						area = str(cfg.rasterBandUniqueVal[v] * cRPX * cRPY)
						if area.endswith('.0'):
							area = area.split('.')[0]
						cList = str(c[0]) + "\t" + str(c[1]) + "\t" + str(cfg.rasterBandUniqueVal[v]) + "\t" + area + str("\n")
						l.write(cList)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			l.close()
			# add raster to layers
			rstr =cfg.utls.addRasterLayer(str(combRstPath), str(cfg.osSCP.path.basename(combRstPath)))
			cfg.utls.rasterSymbolGeneric(rstr, "NoData")	
			try:
				f = open(tblOut)
				if cfg.osSCP.path.isfile(tblOut):
					eM = f.read()
					cfg.ui.band_set_comb_textBrowser.setText(eM)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " cross matrix calculated")
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.updateBar(100)
			if batch == "No":
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.utls.finishSound()
				cfg.ui.toolBox_band_set_combination.setCurrentIndex(1)
				cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "finished")
	