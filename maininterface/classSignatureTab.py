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

class ClassSignatureTab:

	def __init__(self):
		pass
	
	# calculate class signature action
	def calculateClassSignatureAction(self):
		self.calculateClassSignature()
		
	# calculate class signature
	def calculateClassSignature(self, batch = "No", inputClassification = None, bandSetNumber = None, outputFile = None):
		if inputClassification is None:
			clssfctnNm = cfg.ui.classification_name_combo_3.currentText()
			clss = cfg.utls.selectLayerbyName(clssfctnNm, "Yes")
			inputClassification = cfg.utls.layerSource(clss)
		if bandSetNumber is None:
			bandSet = cfg.ui.band_set_comb_spinBox_8.value()
			bandSetNumber = bandSet - 1
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		if batch == "No":
			clssOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save signature output"), "", "*.txt", "txt")
		else:
			clssOut = outputFile
		if clssOut is not False:
			if batch == "No":
				cfg.uiUtls.addProgressBar()
			if clssOut.lower().endswith(".txt"):
				pass
			else:
				clssOut = clssOut + ".txt"
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "class signature")
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
				bndSetIf = "Yes"
			else:
				ckB = cfg.utls.checkImageBandSet(bandSetNumber)
				bndSetIf = "No"
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
			# No data value
			NoDataVal = cfg.NoDataVal
			EPSG = cfg.utls.getEPSGRaster(inputClassification)
			if str(EPSG) != str(rEPSG):
				nD = cfg.utls.imageNoDataValue(inputClassification)
				if nD is None:
					nD = NoDataVal
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
			bList = []
			bandNumberList = []
			bList.append(inputClassification)
			bandNumberList.append(1)
			for x in range(0, len(cfg.bndSetLst)):						
				if bndSetIf == "Yes":
					bList.append(cfg.bndSetLst[x])
					bandNumberList.append(1)
				else:
					bList.append(cfg.bndSetLst[x])
					bandNumberList.append(x + 1)
			nD = cfg.utls.imageNoDataValue(cfg.bndSetLst[0])
			if nD is None:
				nD = NoDataVal
			# date time for temp name
			dT = cfg.utls.getTime()
			tPMN1 = cfg.tmpVrtNm + ".vrt"
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
			# band list
			bLR = [bL[0]]
			cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
			cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
			o = cfg.utls.processRaster(rD, bLR, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, nD, "No", None, None, "UniqueVal")
			cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
			classes = sorted(cfg.rasterBandUniqueVal)
			cfg.uiUtls.updateBar(30)
			# calculation
			previewSize = 0
			previewPoint = None
			compress = cfg.rasterCompression
			o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterPixelCountClassSignature, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, [classes, cfg.bandSetsList[bandSetNumber][6]], "Sum")
			cfg.uiUtls.updateBar(40)
			# calculate band mean
			for c in classes:
				for b in range(0, len(bL) - 1):	
					cfg.rasterClassSignature["MEAN_BAND_" + str(b) + "_c_" + str(c)] = cfg.rasterClassSignature["SUM_BAND_" + str(b) + "_c_" + str(c)] / cfg.rasterClassSignature["COUNT_BAND_" + str(b) + "_c_" + str(c)]
			o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterStandardDeviationClassSignature, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, [classes, cfg.bandSetsList[bandSetNumber][6]], "Standard deviation")
			cfg.uiUtls.updateBar(70)
			comb = cfg.itertoolsSCP.combinations(list(range(0, len(bL) - 1)), 2)
			# calculate signature
			signatures = []
			for c in classes:
				covMat = cfg.np.zeros((len(bL) - 1, len(bL) - 1), dtype=cfg.np.float32)
				cfg.tblOut = {}
				s2 = []
				try:
					cfg.tblOut["ROI_SIZE"] = cfg.rasterClassSignature["COUNT_BAND_" + str(0) + "_c_" + str(c)]
					for b in range(0, len(bL) - 1):
						min = cfg.rasterClassSignature["MINIMUM_BAND_" + str(b) + "_c_" + str(c)]
						max = cfg.rasterClassSignature["MAXIMUM_BAND_" + str(b) + "_c_" + str(c)]
						mean = cfg.rasterClassSignature["MEAN_BAND_" + str(b) + "_c_" + str(c)]
						sd = cfg.np.sqrt(cfg.rasterClassSignature["VAR_BAND_" + str(b) + "_c_" + str(c)])
						signature = [min, max, mean, sd]
						s2.append(mean)
						cfg.tblOut["WAVELENGTH_" + str(b + 1)] = cfg.bandSetsList[cfg.bndSetNumber][4][b]
						covMat[b, b] = cfg.rasterClassSignature["VAR_BAND_" + str(b) + "_c_" + str(c)]
						cfg.tblOut["BAND_" + str(b + 1)] = signature
					# covariance
					for i in comb:
						covMat[i[0], i[1]] = cfg.rasterClassSignature["COV_BAND_" + str(i[0]) + "-" + str(i[1]) + "_c_" + str(c)]
						covMat[i[1], i[0]] = cfg.rasterClassSignature["COV_BAND_" + str(i[0]) + "-" + str(i[1]) + "_c_" + str(c)]
					signatures.append([c, s2, cfg.rasterClassSignature["COUNT_BAND_" + str(0) + "_c_" + str(c)]])
					if cfg.ui.class_signature_save_siglist_checkBox.isChecked() is True:
						val = cfg.utls.ROIStatisticsToSignature(covMat, int(c), cfg.classSignatureNm, int(c), cfg.classSignatureNm, bandSetNumber, cfg.bandSetsList[bandSetNumber][5], "No", "No")
						cfg.SCPD.ROIListTable(cfg.shpLay, cfg.uidc.signature_list_tableWidget)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No", None, None
			# close GDAL rasters
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
			# display parameters
			self.displayParameters(signatures, clssOut)
			cfg.uiUtls.updateBar(100)
			if batch == "No":
				cfg.utls.finishSound()
				cfg.uiUtls.removeProgressBar()
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " class signature calculated")	
					
	# display parameters
	def displayParameters(self, signatureList, outputFile = None):
		tblOut = outputFile
		try:
			l = open(tblOut, 'w')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		tB = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Class')) + "\t" + str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Signature')) + "\t" + str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'PixelSum')) + str("\n")
		l.write(str(tB))
		for s in signatureList:
			tB = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'C_ID_')) + str(s[0]) + "\t" 
			vB = None
			for k in s[1]:
				if vB is None:					
					vB = str(k)
				else:
					vB = vB + "," + str(k)
			l.write(str(tB) + str(vB) + "\t" + str(s[2]) + str("\n"))
		l.close()
		try:
			f = open(tblOut)
			if cfg.osSCP.path.isfile(tblOut):
				eM = f.read()
				cfg.ui.report_textBrowser_4.setText(str(eM))
				cfg.ui.toolBox_class_signature.setCurrentIndex(1)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "calculated")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))