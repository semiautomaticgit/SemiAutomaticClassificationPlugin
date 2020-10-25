# -*- coding: utf-8 -*-
'''
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright		: (C) 2012-2021 by Luca Congedo
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

'''

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

class ClassSignatureTab:

	def __init__(self):
		pass
	
	# calculate class signature action
	def calculateClassSignatureAction(self):
		self.calculateClassSignature()
		
	# calculate class signature
	def calculateClassSignature(self, batch = 'No', inputClassification = None, bandSetNumber = None, outputFile = None):
		if inputClassification is None:
			clssfctnNm = cfg.ui.classification_name_combo_3.currentText()
			clss = cfg.utls.selectLayerbyName(clssfctnNm, 'Yes')
			if clss is None:
				return 'No'
			inputClassification = cfg.utls.layerSource(clss)
		if bandSetNumber is None:
			bandSet = cfg.ui.band_set_comb_spinBox_8.value()
			bandSetNumber = bandSet - 1
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		if batch == 'No':
			clssOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save signature output"), "", "*.txt", "txt")
		else:
			clssOut = outputFile
		if clssOut is not False:
			if batch == 'No':
				cfg.uiUtls.addProgressBar()
			if clssOut.lower().endswith(".txt"):
				pass
			else:
				clssOut = clssOut + ".txt"
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "class signature")
			try:
				cfg.bandSetsList[bandSetNumber][0]
			except:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar28()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
				return 'No'
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				ckB = cfg.utls.checkBandSet(bandSetNumber)
				bndSetIf = 'Yes'
			else:
				ckB = cfg.utls.checkImageBandSet(bandSetNumber)
				bndSetIf = 'No'
			if len(cfg.bndSetLst) == 0:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar28()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
				return 'No'
			cfg.uiUtls.updateBar(10)
			rEPSG = cfg.utls.getEPSGRaster(cfg.bndSetLst[0])				
			if rEPSG is None:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar28()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
				return 'No'	
			cfg.uiUtls.updateBar(20)
			# No data value
			NoDataVal = cfg.NoDataVal
			EPSG = cfg.utls.getEPSGRaster(inputClassification)
			if str(EPSG) != str(rEPSG):
				nD = cfg.utls.imageNoDataValue(inputClassification)
				if nD is None:
					nD = NoDataVal
				tPMD = cfg.utls.createTempRasterPath('tif')
				cfg.utls.GDALReprojectRaster(inputClassification, tPMD, "GTiff", None, "EPSG:" + str(rEPSG), "-ot Float32 -dstnodata " + str(nD))
				if cfg.osSCP.path.isfile(tPMD):
					inputClassification = tPMD
				else:
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr60()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
					return 'No'
			bList = []
			bandNumberList = []
			bList.append(inputClassification)
			bandNumberList.append(1)
			for x in range(0, len(cfg.bndSetLst)):						
				if bndSetIf == 'Yes':
					bList.append(cfg.bndSetLst[x])
					bandNumberList.append(1)
				else:
					bList.append(cfg.bndSetLst[x])
					bandNumberList.append(x + 1)
			nD = cfg.utls.imageNoDataValue(cfg.bndSetLst[0])
			if nD is None:
				nD = NoDataVal
			cfg.parallelArrayDict = {}
			o = cfg.utls.multiProcessRaster(rasterPath = inputClassification, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = nD, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'), deleteArray = 'No')
			cfg.parallelArrayDict = {}
			# calculate unique values
			values = cfg.np.array([])
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						values = cfg.np.append(values, ar[0, ::])
				except:
					return 'No'
			rasterBandUniqueVal = cfg.np.unique(values).tolist()
			classes = sorted(rasterBandUniqueVal)
			cfg.uiUtls.updateBar(30)
			# create functions
			functionList = []
			variableList = []
			for c in classes:
				if c != nD:
					for b in range(1, len(bList)):
						e = 'np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(b) + '], np.nan)'
						functionList.append(e)
						variableList.append("'rasterSCPArrayfunctionBand'")
			# create virtual raster
			vrtCheck = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'Yes')
			# open input with GDAL
			rDD = cfg.gdalSCP.Open(vrtCheck, cfg.gdalSCP.GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rDD)
			# calculation count, sum, mean, min, max, std
			o = cfg.utls.processRasterBoundaries(rDD, bL, None, 'No', "rasterStatistics", None, None, None, None, 0, None, nD, 'No', functionList, variableList, "raster statistics ", None, None, cfg.parallelArray)
			cfg.uiUtls.updateBar(60)
			# calculate covariance
			comb = list(cfg.itertoolsSCP.combinations(list(range(0, len(bL) - 1)), 2))
			# create functions
			functionList = []
			variableList = []
			for c in classes:
				if c != nD:
					for i in comb:
						e1 = 'np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(i[0]+1) + '], np.nan)'
						mean1 = o[e1][2]
						count = o[e1][0]
						e2 = 'np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(i[1]+1) + '], np.nan)'
						mean2 = o[e2][2]
						cE = 'np.nansum( (np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(i[0]+1) + '], np.nan).ravel() - ' + str(mean1) + ') * (np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(i[1]+1) + '], np.nan).ravel() - ' + str(mean2) + ') ) / (' + str(count) + ' - 1)'
						functionList.append(cE)
						variableList.append("'rasterSCPArrayfunctionBand'")
			# calculation count, sum, mean, min, max, std
			oo = cfg.utls.processRasterBoundaries(rDD, bL, None, 'No', "rasterCalculation", None, None, None, None, 0, None, nD, 'No', functionList, variableList, "raster statistics ", None, None, cfg.parallelArray)
			rDD = None
			for b in range(0, len(bL)):
				bL[b] = None
			cfg.uiUtls.updateBar(70)
			# calculate signature
			signatures = []
			for c in classes:
				if c != nD:
					covMat = cfg.np.zeros((len(bL) - 1, len(bL) - 1), dtype=cfg.np.float32)
					cfg.tblOut = {}
					s2 = []
					#try:
					for b in range(1, len(bList)):
						e = 'np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(b) + '], np.nan)'
						cfg.tblOut["ROI_SIZE"] = o[e][0]
						min = o[e][3]
						max = o[e][4]
						mean = o[e][2]
						sd = o[e][5]
						signature = [min, max, mean, sd]
						s2.append(mean)
						cfg.tblOut["WAVELENGTH_" + str(b)] = cfg.bandSetsList[cfg.bndSetNumber][4][b-1]
						covMat[b-1, b-1] = o[e][5] * o[e][5]
						cfg.tblOut["BAND_" + str(b)] = signature
					# covariance
					for i in comb:
						e1 = 'np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(i[0]+1) + '], np.nan)'
						mean1 = o[e1][2]
						count = o[e1][0]
						e2 = 'np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(i[1]+1) + '], np.nan)'
						mean2 = o[e2][2]
						cE = 'np.nansum( (np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(i[0]+1) + '], np.nan).ravel() - ' + str(mean1) + ') * (np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(i[1]+1) + '], np.nan).ravel() - ' + str(mean2) + ') ) / (' + str(count) + ' - 1)'
						covMat[i[0], i[1]] = oo[cE][0]
						covMat[i[1], i[0]] = oo[cE][0]
					signatures.append([c, s2, o[e][0]])
					if cfg.ui.class_signature_save_siglist_checkBox.isChecked() is True:
						val = cfg.utls.ROIStatisticsToSignature(covMat, int(c), cfg.classSignatureNm, int(c), cfg.classSignatureNm, bandSetNumber, cfg.bandSetsList[bandSetNumber][5], 'No', 'No')
						cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
					try:
						pass
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
						return 'No', None, None
			# display parameters
			self.displayParameters(signatures, clssOut)
			cfg.uiUtls.updateBar(100)
			if batch == 'No':
				cfg.utls.finishSound()
				cfg.utls.sendSMTPMessage(None, str(__name__))
				cfg.uiUtls.removeProgressBar()
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " class signature calculated")	
					
	

	# display parameters
	def displayParameters(self, signatureList, outputFile = None):
		tblOut = outputFile
		try:
			l = open(tblOut, 'w')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return 'No'
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
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "calculated")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))