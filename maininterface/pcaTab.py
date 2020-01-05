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

class PcaTab:

	def __init__(self):
		pass
	
	# calculate PCA action
	def calculatePCAAction(self):
		self.calculatePCA()
		
	# calculate PCA
	def calculatePCA(self, batch = "No", outputDirectory = None, bandSetNumber = None):
		if bandSetNumber is None:
			bandSet = cfg.ui.band_set_comb_spinBox_4.value()
			bandSetNumber = bandSet - 1
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		if batch == "No":
			outF = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		else:
			outF = outputDirectory
		if len(outF) > 0:
			oDir = cfg.utls.makeDirectory(outF)
			imageName = cfg.bandSetsList[bandSetNumber][8]
			# if band set
			if cfg.bandSetsList[bandSetNumber][0] == "Yes":
				ckB = cfg.utls.checkBandSet(bandSetNumber)
				if ckB == "Yes":
					bS = cfg.bndSetLst
					# open input with GDAL
					bL = []
					for i in range(0, len(bS)):
						rD = cfg.gdalSCP.Open(str(bS[i]), cfg.gdalSCP.GA_ReadOnly)
						bL.append(rD)
				else:
					cfg.mx.msgErr6()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error no band set")	
					return None
			else:
				r = cfg.utls.selectLayerbyName(imageName, "Yes")
				try:
					iR = cfg.utls.layerSource(r)
					# open input with GDAL
					rD = cfg.gdalSCP.Open(iR, cfg.gdalSCP.GA_ReadOnly)
				except Exception as err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
			if cfg.ui.num_comp_checkBox.isChecked() is True:
				numbComp = cfg.ui.pca_components_spinBox.value()
				if numbComp > len(bL):
					numbComp = len(bL)
			else:
				numbComp = len(bL)
			if rD is not None:
				self.PCACalculation(rD, bL, outF, numbComp, None, batch)
				for b in range(0, len(bL)):
					bL[b] = None
				rDC= None
				
	# PCA calculation
	def PCACalculation(self, inputGDALRaster, bandList, outputDirectory, numberComponents = 1, NoDataValue = None, batch = "No", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		if batch == "No":
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
		cfg.uiUtls.updateBar(10)
		# input raster
		rD = inputGDALRaster
		# band list
		bL =bandList
		# date time for temp name
		dT = cfg.utls.getTime()
		tempRasterList = []
		for i in range(1, numberComponents + 1):
			tempRasterList.append(cfg.tmpDir + "/" + dT + cfg.PCANm + str(i) + ".tif")
		# create rasters
		oMR = cfg.utls.createRasterFromReference(rD, 1, tempRasterList, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, cfg.rasterCompression, "DEFLATE21")
		# No data value
		if NoDataValue is not None:
			nD = NoDataValue
		elif cfg.ui.nodata_checkBox_4.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_5.value()
		else:
			nD = None
		cfg.rasterPixelCountPCA = {}
		o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterPixelCount, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, cfg.bandSetsList[bandSetNumber][6], "Sum")
		# calculate band mean
		for i in range(0, len(bL)):
			cfg.rasterPixelCountPCA["MEAN_BAND_" + str(i)] = cfg.rasterPixelCountPCA["SUM_BAND_" + str(i)] / cfg.rasterPixelCountPCA["COUNT_BAND_" + str(i)]
		o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterCovariance, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, cfg.bandSetsList[bandSetNumber][6], "Covariance")
		covM = self.createCovarianceMatrix(bL)
		corrM = self.createCorrelationMatrix(covM)
		comp, totalVariance, totalVarianceCumulative, eigenValues = self.calculateEigenVectors(covM)
		comp = comp[:numberComponents]
		totalVariance = totalVariance[:numberComponents]
		totalVarianceCumulative = totalVarianceCumulative[:numberComponents]
		eigenValues =eigenValues[:numberComponents]
		# calculation
		o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.calculatePCABands, "PCA", oMR, None, None, 0, None, cfg.NoDataVal, "No", comp, cfg.bandSetsList[bandSetNumber][6], "No")
		for b in range(0, len(oMR)):
			oMR[b] = None
		# copy raster
		if o != "No":
			for r in tempRasterList:
				out = outputDirectory + "/" + str(cfg.osSCP.path.basename(r)[21:])
				if cfg.rasterCompression != "No":
					try:
						cfg.utls.GDALCopyRaster(r, out, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						cfg.osSCP.remove(r)
					except Exception as err:
						cfg.shutilSCP.copy(r, out)
						cfg.osSCP.remove(r)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					cfg.shutilSCP.copy(r, out)
					cfg.osSCP.remove(r)
				# add raster to layers
				cfg.utls.addRasterLayer(str(out), str(cfg.osSCP.path.basename(out)))
			cfg.uiUtls.updateBar(90)		
			# display parameters
			self.displayParameters(covM, corrM, comp, totalVariance, totalVarianceCumulative, eigenValues, outputDirectory, str(cfg.osSCP.path.basename(out)))
			cfg.ui.toolBox_PCA.setCurrentIndex(1)
			cfg.uiUtls.updateBar(100)
		if batch == "No":
			# enable map canvas render
			cfg.cnvs.setRenderFlag(True)
			cfg.utls.finishSound()
			cfg.uiUtls.removeProgressBar()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " PCA calculated")
	
	# display PCA parameters
	def displayParameters(self, covarianceMatrix, correlationMatrix, components, totalVariance, totalVarianceCumulative, eigenValues, outputDirectory, outputFileName = None):
		tblOut = outputDirectory + "/" + str(outputFileName) + cfg.PCAReportNm
		try:
			l = open(tblOut, 'w')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		t = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Principal Components Analysis')) + "	" + str("\n") + str("\n")
		l.write(t)
		t = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Covariance matrix')) + "	"
		l.write(str(t) + str("\n"))
		tB = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Bands')) + "	"
		for y in range(0, covarianceMatrix.shape[0]):
			tB = tB + str(y + 1) + "	"
		l.write(str(tB) + str("\n"))
		for y in range(0, covarianceMatrix.shape[0]):
			t = str(y + 1) + "	"
			for x in range(0, covarianceMatrix.shape[1]):
				t = t + str(covarianceMatrix[y,x]) + "	"
			l.write(str(t) + str("\n"))
		l.write(str("\n"))
		t = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Correlation matrix')) + "	"
		l.write(str(t) + str("\n"))
		l.write(str(tB) + str("\n"))
		for y in range(0, correlationMatrix.shape[0]):
			t = str(y + 1) + "	"
			for x in range(0, correlationMatrix.shape[1]):
				t = t + str(correlationMatrix[y,x]) + "	"
			l.write(str(t) + str("\n"))
		l.write(str("\n"))
		t = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Eigen vectors')) + "	"
		l.write(str(t) + str("\n"))
		tB = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Bands')) + "	"
		for y in range(0, len(components)):
			tB = tB + str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Vector_')) + str(y + 1) + "	"
		l.write(str(tB) + str("\n"))
		for i in range(0, len(components)):
			t = str(i + 1) + "	"
			for v in components:
				t = t + str(v[i]) + "	"
			l.write(str(t) + str("\n"))
		l.write(str("\n"))
		t = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Eigen values')) + "	" + str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Accounted variance')) + "	" + str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Cumulative variance')) + "	"
		l.write(str(t) + str("\n"))
		for i in range(0, len(eigenValues)):
			t = str(eigenValues[i]) + "	" + str(totalVariance[i]) + "	" + str(totalVarianceCumulative[i])
			l.write(str(t) + str("\n"))
		l.close()
		try:
			f = open(tblOut)
			if cfg.osSCP.path.isfile(tblOut):
				eM = f.read()
				cfg.ui.report_textBrowser_2.setText(str(eM))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " PCA calculated")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
	
	# create covariance matrix
	def createCovarianceMatrix(self, bandList):
		m = cfg.np.zeros((len(bandList), len(bandList)))
		comb = cfg.itertoolsSCP.combinations(list(range(0, len(bandList))), 2)
		for i in comb:
			v = cfg.rasterPixelCountPCA["COV_BAND_" + str(i[0]) + "-" + str(i[1])]
			m.itemset((int(i[0]), int(i[1])), v)
			m.itemset((int(i[1]), int(i[0])), v)
		for i in range(0, len(bandList)):
			v = cfg.rasterPixelCountPCA["COV_BAND_" + str(i) + "-" + str(i)]
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
		