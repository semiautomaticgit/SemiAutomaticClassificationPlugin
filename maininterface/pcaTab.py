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

class PcaTab:

	def __init__(self):
		pass
	
	# calculate PCA action
	def calculatePCAAction(self):
		self.calculatePCA()
		
	# calculate PCA
	def calculatePCA(self, batch = 'No', outputDirectory = None, bandSetNumber = None):
		if bandSetNumber is None:
			bandSet = cfg.ui.band_set_comb_spinBox_4.value()
			bandSetNumber = bandSet - 1
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		if batch == 'No':
			outF = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		else:
			outF = outputDirectory
		if len(outF) > 0:
			oDir = cfg.utls.makeDirectory(outF)
			imageName = cfg.bandSetsList[bandSetNumber][8]
			# if band set
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				ckB = cfg.utls.checkBandSet(bandSetNumber)
				if ckB == 'Yes':
					lenBL = len(cfg.bndSetLst)
					iR = cfg.utls.createTempVirtualRaster(cfg.bndSetLst, 'No', 'Yes', 'Yes', 0, 'No', 'Yes')
				else:
					cfg.mx.msgErr6()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "Error no band set")	
					return None
			else:
				r = cfg.utls.selectLayerbyName(imageName, 'Yes')
				try:
					iR = cfg.utls.layerSource(r)
					# open input with GDAL
					rD = cfg.gdalSCP.Open(iR, cfg.gdalSCP.GA_ReadOnly)
				except Exception as err:
					# logger
					if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return 'No'
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				lenBL = len(bL)
				rD = None
			if cfg.ui.num_comp_checkBox.isChecked() is True:
				numbComp = cfg.ui.pca_components_spinBox.value()
				if numbComp > lenBL:
					numbComp = lenBL
			else:
				numbComp = lenBL
			if cfg.osSCP.path.isfile(iR):
				self.PCACalculation(iR, lenBL, outF, numbComp, None, batch)
				
	# PCA calculation
	def PCACalculation(self, inputRaster, numberOfBands, outputDirectory, numberComponents = 1, NoDataValue = None, batch = 'No', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		if batch == 'No':
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
		cfg.uiUtls.updateBar(10)
		# No data value
		if NoDataValue is not None:
			nD = NoDataValue
		elif cfg.ui.nodata_checkBox_4.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_5.value()
		else:
			nD = None
		cfg.rasterClassSignature = {}
		varList = []
		argumentList = []
		for bN in range(0, numberOfBands):
			argumentList.append(bN)
			varList.append(bN)
		cfg.parallelArrayDict = {}
		# calculate pixel sum
		o = cfg.utls.multiProcessRaster(rasterPath = inputRaster, functionBand = 'No', functionRaster = cfg.utls.rasterPixelCount, nodataValue = nD,  functionBandArgument = argumentList, functionVariable = varList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Statistics'), outputNoDataValue = nD, compress = cfg.rasterCompression, compressFormat = 'LZW', parallel = cfg.parallelArray)
		for x in sorted(cfg.parallelArrayDict):
			try:
				for ar in cfg.parallelArrayDict[x]:
					for arX in ar[0]:
						cfg.rasterClassSignature[arX] = ar[0][arX]
			except:
				if batch == 'No':
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.uiUtls.removeProgressBar()
				return 'No'
		# calculate band mean
		try:
			for i in range(0, numberOfBands):
				cfg.rasterClassSignature['MEAN_BAND_' + str(i)] = cfg.rasterClassSignature['SUM_BAND_' + str(i)] / cfg.rasterClassSignature['COUNT_BAND_' + str(i)]
		except Exception as err:
			if batch == 'No':
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.utls.finishSound()
				cfg.utls.sendSMTPMessage(None, str(__name__))
				cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
		comb = cfg.itertoolsSCP.combinations(list(range(0, numberOfBands)), 2)
		argumentList = []
		varList = []
		for i in comb:	
			argumentList.append([i[0], i[1]])
			varList.append(cfg.rasterClassSignature)
		cfg.parallelArrayDict = {}
		# process
		o = cfg.utls.multiProcessRaster(rasterPath = inputRaster, functionBand = 'No', functionRaster = cfg.utls.rasterCovariance, nodataValue = nD,  functionBandArgument = argumentList, functionVariable = cfg.rasterClassSignature, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Statistics'), outputNoDataValue = nD, compress = cfg.rasterCompression, compressFormat = 'LZW')
		cfg.uiUtls.updateBar(40)
		for x in sorted(cfg.parallelArrayDict):
			try:
				for ar in cfg.parallelArrayDict[x]:
					for arX in ar[0]:
						for i in argumentList:
							if 'COV_BAND_' + str(i[0]) + '-' + str(i[1]) == arX:
								try:
									cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1])] = cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1])] + ar[0][arX]
								except:
									cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1])] = ar[0][arX]
						for i in range(0, numberOfBands):
							if 'COV_BAND_' + str(i) + '-' + str(i) == arX:
								try:
									cfg.rasterClassSignature['COV_BAND_' + str(i) + '-' + str(i)] = cfg.rasterClassSignature['COV_BAND_' + str(i) + '-' + str(i)] + ar[0][arX]
								except:
									cfg.rasterClassSignature['COV_BAND_' + str(i) + '-' + str(i)] = ar[0][arX]
			except:
				if batch == 'No':
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.uiUtls.removeProgressBar()
				return 'No'
		covM = self.createCovarianceMatrix(numberOfBands)
		corrM = self.createCorrelationMatrix(covM)
		comp, totalVariance, totalVarianceCumulative, eigenValues = self.calculateEigenVectors(covM)
		comp = comp[:numberComponents]
		totalVariance = totalVariance[:numberComponents]
		totalVarianceCumulative = totalVarianceCumulative[:numberComponents]
		eigenValues =eigenValues[:numberComponents]
		# output rasters
		oM = cfg.utls.createTempRasterList(numberOfBands)
		outputList = []
		for n in range(0, numberComponents):
			out = outputDirectory + '/bandset' + str(bandSetNumber + 1) + '_pc' + str(n+1) + '.tif'
			outputList.append(out)
		# open input with GDAL
		rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
		# output rasters
		cfg.utls.createRasterFromReference(rD, 1, outputList, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0,  None, compress = 'Yes', compressFormat = 'LZW')
		# temporary bands
		cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0,  None, compress = 'No')
		rD = None
		# normalize bands
		functionList = []
		variableList = []
		for b in range(0, numberOfBands):
			e = 'raster - ' + str(cfg.rasterClassSignature['MEAN_BAND_' + str(b)])
			functionList.append(e)
			variableList.append(['raster'])
		# process
		o = cfg.utls.multiProcessRaster(rasterPath = inputRaster, functionBand = 'No', functionRaster = cfg.utls.calculateRaster, outputRasterList = oM, nodataValue =  nD, functionBandArgument = functionList, functionVariable = variableList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion'), parallel = cfg.parallelRaster)
		cfg.uiUtls.updateBar(60)
		# virtual raster
		tPMD = cfg.utls.createTempVirtualRaster(oM, 'No', 'Yes', 'Yes', 0, 'No', 'No')
		# calculate PCA bands
		o = cfg.utls.multiProcessRaster(rasterPath = tPMD, functionBand = 'No', functionRaster = cfg.utls.calculatePCABands, outputRasterList = ['No'], nodataValue = nD, functionBandArgument = [comp], functionVariable = [outputList], progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'PCA'), outputNoDataValue = nD, compress = cfg.rasterCompression, compressFormat = 'LZW', threadNumber = 1, parallel = cfg.parallelRaster, skipSingleBand = 'Yes')
		# remove temporary raster
		for tR in oM:
			try:
				cfg.osSCP.remove(tR)
			except:
				pass
		# load raster
		if o != 'No':
			for r in outputList:
				# add raster to layers
				cfg.utls.addRasterLayer(r)
			# display parameters
			self.displayParameters(covM, corrM, comp, totalVariance, totalVarianceCumulative, eigenValues, outputDirectory, 'bandset' + str(bandSetNumber + 1) + '_')
			cfg.ui.toolBox_PCA.setCurrentIndex(1)
			cfg.uiUtls.updateBar(100)
		if batch == 'No':
			# enable map canvas render
			cfg.cnvs.setRenderFlag(True)
			cfg.utls.finishSound()
			cfg.utls.sendSMTPMessage(None, str(__name__))
			cfg.uiUtls.removeProgressBar()
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' PCA calculated')
	
	# display PCA parameters
	def displayParameters(self, covarianceMatrix, correlationMatrix, components, totalVariance, totalVarianceCumulative, eigenValues, outputDirectory, outputFileName = None):
		tblOut = outputDirectory + '/' + str(outputFileName) + cfg.PCAReportNm
		try:
			l = open(tblOut, 'w')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
		t = str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Principal Components Analysis')) + '	' + str('\n') + str('\n')
		l.write(t)
		t = str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Covariance matrix')) + '	'
		l.write(str(t) + str('\n'))
		tB = str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Bands')) + '	'
		for y in range(0, covarianceMatrix.shape[0]):
			tB = tB + str(y + 1) + '	'
		l.write(str(tB) + str('\n'))
		for y in range(0, covarianceMatrix.shape[0]):
			t = str(y + 1) + '	'
			for x in range(0, covarianceMatrix.shape[1]):
				t = t + str(covarianceMatrix[y,x]) + '	'
			l.write(str(t) + str('\n'))
		l.write(str('\n'))
		t = str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Correlation matrix')) + '	'
		l.write(str(t) + str('\n'))
		l.write(str(tB) + str('\n'))
		for y in range(0, correlationMatrix.shape[0]):
			t = str(y + 1) + '	'
			for x in range(0, correlationMatrix.shape[1]):
				t = t + str(correlationMatrix[y,x]) + '	'
			l.write(str(t) + str('\n'))
		l.write(str('\n'))
		t = str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Eigen vectors')) + '	'
		l.write(str(t) + str('\n'))
		tB = str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Bands')) + '	'
		for y in range(0, len(components)):
			tB = tB + str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Vector_')) + str(y + 1) + '	'
		l.write(str(tB) + str('\n'))
		for i in range(0, len(components)):
			t = str(i + 1) + '	'
			for v in components:
				t = t + str(v[i]) + '	'
			l.write(str(t) + str('\n'))
		l.write(str('\n'))
		t = str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Eigen values')) + '	' + str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Accounted variance')) + '	' + str(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Cumulative variance')) + '	'
		l.write(str(t) + str('\n'))
		for i in range(0, len(eigenValues)):
			t = str(eigenValues[i]) + '	' + str(totalVariance[i]) + '	' + str(totalVarianceCumulative[i])
			l.write(str(t) + str('\n'))
		l.close()
		try:
			f = open(tblOut)
			if cfg.osSCP.path.isfile(tblOut):
				eM = f.read()
				cfg.ui.report_textBrowser_2.setText(str(eM))
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' PCA calculated')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
	
	# create covariance matrix
	def createCovarianceMatrix(self, numberOfBands):
		m = cfg.np.zeros((numberOfBands, numberOfBands))
		comb = cfg.itertoolsSCP.combinations(list(range(0, numberOfBands)), 2)
		for i in comb:
			v = cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1])]
			m.itemset((int(i[0]), int(i[1])), v)
			m.itemset((int(i[1]), int(i[0])), v)
		for i in range(0, numberOfBands):
			v = cfg.rasterClassSignature['COV_BAND_' + str(i) + '-' + str(i)]
			m.itemset((int(i), int(i)), v)	
		return m
		
	# create correlation matrix
	def createCorrelationMatrix(self, covarianceMatrix):
		m = cfg.np.zeros(covarianceMatrix.shape)
		for y in range(0, covarianceMatrix.shape[0]):
			for x in range(0, covarianceMatrix.shape[1]):
				v = covarianceMatrix[y, x] / cfg.np.sqrt(covarianceMatrix[y, y] * covarianceMatrix[x, x])
				m.itemset((y, x), v)
		return m
		
	# calculate eigen vectors
	def calculateEigenVectors(self, matrix):
		val, vect = cfg.np.linalg.eigh(matrix)
		sort = cfg.np.argsort(val)
		comp = []
		totalVariance = []
		totalVarianceCumulative = []
		eVal = []
		for i in reversed(sort):
			eVal.append(val[i])
			comp.append(vect[:, i])
			totalVariance.append(val[i]/val.sum() * 100)
			totalVarianceCumulative.append(cfg.np.sum(totalVariance))
		return comp, totalVariance, totalVarianceCumulative, eVal
		