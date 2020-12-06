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
			# calculate unique values
			values = cfg.np.array([])
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						values = cfg.np.append(values, ar[0, ::])
				except:
					if batch == 'No':
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						cfg.uiUtls.removeProgressBar()
					return 'No'
			rasterBandUniqueVal = cfg.np.unique(values).tolist()
			classes = []
			for c in sorted(rasterBandUniqueVal):
				classes.append(int(c))
			cfg.uiUtls.updateBar(30)
			argumentList = [list(range(0, len(bList) - 1)), classes]
			# create virtual raster
			vrtCheck = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'Yes')
			cfg.parallelArrayDict = {}
			cfg.rasterClassSignature = {}
			# process
			o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.rasterPixelCountClassSignature, nodataValue = nD, functionBandArgument = argumentList, functionVariable = cfg.rasterClassSignature, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Statistics'), outputNoDataValue = nD, compress = cfg.rasterCompression, compressFormat = 'LZW')
			# find values
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						for arX in ar:
							for i in range(0, len(bList) - 1):
								for c in classes:
									if 'COUNT_BAND_' + str(i) + '_c_' + str(c) == arX:
										try:
											cfg.rasterClassSignature['COUNT_BAND_' + str(i) + '_c_' + str(c)] = cfg.rasterClassSignature['COUNT_BAND_' + str(i) + '_c_' + str(c)] + ar[arX]
										except:
											cfg.rasterClassSignature['COUNT_BAND_' + str(i) + '_c_' + str(c)] = ar[arX]
									elif 'SUM_BAND_' + str(i) + '_c_' + str(c) == arX:
										try:
											cfg.rasterClassSignature['SUM_BAND_' + str(i) + '_c_' + str(c)] = cfg.rasterClassSignature['SUM_BAND_' + str(i) + '_c_' + str(c)] + ar[arX]
										except:
											cfg.rasterClassSignature['SUM_BAND_' + str(i) + '_c_' + str(c)] = ar[arX]
									elif 'MINIMUM_BAND_' + str(i) + '_c_' + str(c) == arX:
										try:
											cfg.rasterClassSignature['MINIMUM_BAND_' + str(i) + '_c_' + str(c)] = min(ar[arX], cfg.rasterClassSignature['MINIMUM_BAND_' + str(i) + '_c_' + str(c)])
										except:
											cfg.rasterClassSignature['MINIMUM_BAND_' + str(i) + '_c_' + str(c)] = ar[arX]
									elif 'MAXIMUM_BAND_' + str(i) + '_c_' + str(c) == arX:
										try:
											cfg.rasterClassSignature['MAXIMUM_BAND_' + str(i) + '_c_' + str(c)] = max(ar[arX], cfg.rasterClassSignature['MAXIMUM_BAND_' + str(i) + '_c_' + str(c)])
										except:
											cfg.rasterClassSignature['MAXIMUM_BAND_' + str(i) + '_c_' + str(c)] = ar[arX]
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					if batch == 'No':
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						cfg.uiUtls.removeProgressBar()
					return 'No'
			# calculate band mean
			for c in classes:
				for b in range(0, len(bList) - 1):	
					cfg.rasterClassSignature['MEAN_BAND_' + str(b) + '_c_' + str(c)] = cfg.rasterClassSignature['SUM_BAND_' + str(b) + '_c_' + str(c)] / cfg.rasterClassSignature['COUNT_BAND_' + str(b) + '_c_' + str(c)]
			comb = cfg.itertoolsSCP.combinations(list(range(0, len(bList) - 1)), 2)
			varList = []
			for i in comb:	
				varList.append([i[0], i[1]])
			argumentList = [varList, classes, list(range(0, len(bList) - 1))]
			cfg.parallelArrayDict = {}
			# process
			o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.rasterStandardDeviationClassSignature, nodataValue = nD, functionBandArgument = argumentList, functionVariable = cfg.rasterClassSignature, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Statistics'), outputNoDataValue = nD, compress = cfg.rasterCompression, compressFormat = 'LZW')
			# find values
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						for arX in ar:
							for i in varList:
								for c in classes:
									if 'COV_BAND_' + str(i[0]) + '-' + str(i[1]) + '_c_' + str(c) == arX:
										try:
											cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1]) + '_c_' + str(c)] = cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1]) + '_c_' + str(c)] + ar[arX]
										except:
											cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1]) + '_c_' + str(c)] = ar[arX]
							for f in range(0, len(bList) - 1):
								for c in classes:
									if 'VAR_BAND_' + str(f) + '_c_' + str(c) == arX:
										try:
											cfg.rasterClassSignature['VAR_BAND_' + str(f) + '_c_' + str(c)] = cfg.rasterClassSignature['VAR_BAND_' + str(f) + '_c_' + str(c)] + ar[arX]
										except:
											cfg.rasterClassSignature['VAR_BAND_' + str(f) + '_c_' + str(c)] = ar[arX]
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					if batch == 'No':
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						cfg.uiUtls.removeProgressBar()
					return 'No'
			cfg.uiUtls.updateBar(70)
			comb = cfg.itertoolsSCP.combinations(list(range(0, len(bList) - 1)), 2)
			# calculate signature
			signatures = []
			for c in classes:
				covMat = cfg.np.zeros((len(bList) - 1, len(bList) - 1), dtype=cfg.np.float32)
				cfg.tblOut = {}
				s2 = []
				if c != nD:
					try:
						cfg.tblOut['ROI_SIZE'] = cfg.rasterClassSignature['COUNT_BAND_' + str(0) + '_c_' + str(c)]
						for b in range(0, len(bList) - 1):
							smin = cfg.rasterClassSignature['MINIMUM_BAND_' + str(b) + '_c_' + str(c)]
							smax = cfg.rasterClassSignature['MAXIMUM_BAND_' + str(b) + '_c_' + str(c)]
							smean = cfg.rasterClassSignature['MEAN_BAND_' + str(b) + '_c_' + str(c)]
							sd = cfg.np.sqrt(cfg.rasterClassSignature['VAR_BAND_' + str(b) + '_c_' + str(c)])
							signature = [smin, smax, smean, sd]
							s2.append(smean)
							cfg.tblOut['WAVELENGTH_' + str(b + 1)] = cfg.bandSetsList[cfg.bndSetNumber][4][b]
							covMat[b, b] = cfg.rasterClassSignature['VAR_BAND_' + str(b) + '_c_' + str(c)]
							cfg.tblOut['BAND_' + str(b + 1)] = signature
						# covariance
						for i in comb:
							covMat[i[0], i[1]] = cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1]) + '_c_' + str(c)]
							covMat[i[1], i[0]] = cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1]) + '_c_' + str(c)]
						signatures.append([c, s2, cfg.rasterClassSignature['COUNT_BAND_' + str(0) + '_c_' + str(c)]])
						if cfg.ui.class_signature_save_siglist_checkBox.isChecked() is True:
							val = cfg.utls.ROIStatisticsToSignature(covMat, int(c), cfg.classSignatureNm, int(c), cfg.classSignatureNm, bandSetNumber, cfg.bandSetsList[bandSetNumber][5], 'No', 'No')
							cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
					except Exception as err:
						if batch == 'No':
							cfg.utls.finishSound()
							cfg.utls.sendSMTPMessage(None, str(__name__))
							cfg.uiUtls.removeProgressBar()
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
			