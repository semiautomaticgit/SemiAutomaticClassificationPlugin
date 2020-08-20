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

class ClusteringTab:

	def __init__(self):
		pass
	
	# kmeans radioButton button changed
	def radioKmeansChanged(self):
		cfg.ui.kmeans_radioButton.blockSignals(True)
		cfg.ui.isodata_radioButton.blockSignals(True)
		cfg.ui.kmeans_radioButton.setChecked(True)
		cfg.ui.isodata_radioButton.setChecked(False)
		cfg.ui.kmeans_radioButton.blockSignals(False)
		cfg.ui.isodata_radioButton.blockSignals(False)
		
	# ISODATA radioButton button changed
	def radioIsodataChanged(self):
		cfg.ui.kmeans_radioButton.blockSignals(True)
		cfg.ui.isodata_radioButton.blockSignals(True)
		cfg.ui.isodata_radioButton.setChecked(True)
		cfg.ui.kmeans_radioButton.setChecked(False)
		cfg.ui.kmeans_radioButton.blockSignals(False)
		cfg.ui.isodata_radioButton.blockSignals(False)
		
	# miniumum distance radioButton button changed
	def radioMinDistChanged(self):
		cfg.ui.min_distance_radioButton.blockSignals(True)
		cfg.ui.spectral_angle_map_radioButton.blockSignals(True)
		cfg.ui.min_distance_radioButton.setChecked(True)
		cfg.ui.spectral_angle_map_radioButton.setChecked(False)
		cfg.ui.min_distance_radioButton.blockSignals(False)
		cfg.ui.spectral_angle_map_radioButton.blockSignals(False)
		
	# SAM radioButton button changed
	def radioSAMChanged(self):
		cfg.ui.min_distance_radioButton.blockSignals(True)
		cfg.ui.spectral_angle_map_radioButton.blockSignals(True)
		cfg.ui.spectral_angle_map_radioButton.setChecked(True)
		cfg.ui.min_distance_radioButton.setChecked(False)
		cfg.ui.min_distance_radioButton.blockSignals(False)
		cfg.ui.spectral_angle_map_radioButton.blockSignals(False)
		thresh = cfg.ui.thresh_doubleSpinBox.value()
		if thresh > 90:
			cfg.mx.msg11()
			cfg.ui.thresh_doubleSpinBox.setValue(90)
	
	# kmean_minmax_radioButton button changed
	def radiokmean_minmaxChanged(self):
		cfg.ui.kmean_minmax_radioButton.blockSignals(True)
		cfg.ui.kmean_siglist_radioButton.blockSignals(True)
		cfg.ui.kmean_randomsiglist_radioButton.blockSignals(True)
		cfg.ui.kmean_minmax_radioButton.setChecked(True)
		cfg.ui.kmean_siglist_radioButton.setChecked(False)
		cfg.ui.kmean_randomsiglist_radioButton.setChecked(False)
		cfg.ui.kmean_minmax_radioButton.blockSignals(False)
		cfg.ui.kmean_siglist_radioButton.blockSignals(False)
		cfg.ui.kmean_randomsiglist_radioButton.blockSignals(False)
	
	# kmean_siglist_radioButton button changed
	def radiokmean_siglistChanged(self):
		cfg.ui.kmean_minmax_radioButton.blockSignals(True)
		cfg.ui.kmean_siglist_radioButton.blockSignals(True)
		cfg.ui.kmean_randomsiglist_radioButton.blockSignals(True)
		cfg.ui.kmean_minmax_radioButton.setChecked(False)
		cfg.ui.kmean_siglist_radioButton.setChecked(True)
		cfg.ui.kmean_randomsiglist_radioButton.setChecked(False)
		cfg.ui.kmean_minmax_radioButton.blockSignals(False)
		cfg.ui.kmean_siglist_radioButton.blockSignals(False)
		cfg.ui.kmean_randomsiglist_radioButton.blockSignals(False)
		
	# kmean_randomsiglist_radioButton button changed
	def radiokmean_randomsiglistChanged(self):
		cfg.ui.kmean_minmax_radioButton.blockSignals(True)
		cfg.ui.kmean_siglist_radioButton.blockSignals(True)
		cfg.ui.kmean_randomsiglist_radioButton.blockSignals(True)
		cfg.ui.kmean_minmax_radioButton.setChecked(False)
		cfg.ui.kmean_siglist_radioButton.setChecked(False)
		cfg.ui.kmean_randomsiglist_radioButton.setChecked(True)
		cfg.ui.kmean_minmax_radioButton.blockSignals(False)
		cfg.ui.kmean_siglist_radioButton.blockSignals(False)
		cfg.ui.kmean_randomsiglist_radioButton.blockSignals(False)
	
	# calculate clustering action
	def calculateClusteringAction(self):
		self.calculateClustering()
		
	# calculate clustering
	def calculateClustering(self, batch = "No", outputFile = None, bandSetNumber = None):
		if bandSetNumber is None:
			bandSet = cfg.ui.band_set_comb_spinBox_5.value()
			bandSetNumber = bandSet - 1
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		if batch == "No":
			clssOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save clustering output"), "", "*.tif", "tif")
		else:
			clssOut = outputFile
		if clssOut is not False:
			if clssOut.lower().endswith(".tif"):
				pass
			else:
				clssOut = clssOut + ".tif"
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "clustering")
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
				except:
					return None
				# open input with GDAL
				rD = cfg.gdalSCP.Open(iR, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
			try:
				rD
			except Exception as err:
				cfg.mx.msgErr6()
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return None				
			if rD is not None:
				k_or_sigs = cfg.ui.kmeans_classes_spinBox.value()				
				if cfg.ui.kmean_siglist_radioButton.isChecked() is True:					
					sL = cfg.SCPD.getSignatureList()					
					if len(sL) > 0:
						k_or_sigs = []
						for s in sL:
							vL = []
							for k in range(0, len(cfg.bandSetsList[bandSetNumber][4])):
								vL.append(s[4][k*2])
							k_or_sigs.append([vL, s[2], s[6]])	
				iterations = cfg.ui.kmeans_iter_spinBox.value()
				maxStandardDeviation = cfg.ui.std_dev_doubleSpinBox.value()
				if cfg.ui.kmean_threshold_checkBox.isChecked() is True:
					thresh = cfg.ui.thresh_doubleSpinBox.value()
				else:
					thresh = 0.000001
				minSize = cfg.ui.min_size_class_spinBox.value()
				NoDataValue = None
				if cfg.ui.kmeans_radioButton.isChecked():
					self.kmeansCalculation(rD, bL, clssOut, k_or_sigs, iterations, thresh, NoDataValue, batch, bandSetNumber)
				elif cfg.ui.isodata_radioButton.isChecked():
					self.isodataCalculation(rD, bL, clssOut, k_or_sigs, iterations, thresh, minSize, maxStandardDeviation, NoDataValue, batch, bandSetNumber)
				for b in range(0, len(bL)):
					bL[b] = None	
					
	# ISODATA calculation (adapted from Ball & Hall, 1965. ISODATA. A novel method of data analysis and pattern classification)
	def isodataCalculation(self, inputGDALRaster, bandList, outputFile, k_or_sigs, iterations = 10, thresh = 0.000001, minSize = 10, maxStandardDeviation = 0.000001, NoDataValue = None, batch = "No", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if batch == "No":
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
		cfg.uiUtls.updateBar(10)
		outputDirectory = cfg.osSCP.path.dirname(outputFile)
		# input raster
		rD = inputGDALRaster
		# band list
		bL = bandList		
		cfg.uiUtls.updateBar(20, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " Calculating. Please wait ..."))
		try:
			classNumber = int(k_or_sigs)
		except:
			classNumber = len(k_or_sigs)
		progressStep = int(60 / iterations)
		for iteration in range(0, iterations):
			if cfg.actionCheck == "Yes":
				# remove previous raster
				try:
					cfg.osSCP.remove(r)
				except:
					pass
				r, sigs, sL = self.isodataIteration(rD, bL, iteration, k_or_sigs, classNumber, iterations, thresh, minSize, maxStandardDeviation, NoDataValue, batch, bandSetNumber)
				cfg.uiUtls.updateBar(20 + progressStep, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " Calculating iteration: " + str(iteration) + ". Please wait ..."))
				k_or_sigs = sigs
				if r is None:
					break
			else:
				if batch == "No":
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
					return "No"
		r, sigs, sL = self.isodataIteration(rD, bL, -2, k_or_sigs, classNumber, iterations, thresh, minSize, maxStandardDeviation, NoDataValue, batch, bandSetNumber)
		k_or_sigs = sigs
		cfg.uiUtls.updateBar(80, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " Calculating classification. Please wait ..."))
		r, sigs0, sL0 = self.isodataIteration(rD, bL, -1, k_or_sigs, classNumber, iterations, thresh, minSize, maxStandardDeviation, NoDataValue, batch, bandSetNumber)
		for x in range(0, len(bL)):
			bL[x] = None
		rD = None
		cfg.uiUtls.updateBar(90)
		if r == "No":
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error")
			cfg.mx.msgErr45()
			if batch == "No":
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.utls.finishSound()
				cfg.uiUtls.removeProgressBar()
				return "No"
		else:
			# copy raster
			if cfg.rasterCompression != "No":
				try:
					cfg.utls.GDALCopyRaster(r, outputFile, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
					cfg.osSCP.remove(r)
				except Exception as err:
					cfg.shutilSCP.copy(r, outputFile)
					cfg.osSCP.remove(r)
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			else:
				cfg.shutilSCP.copy(r, outputFile)
				cfg.osSCP.remove(r)
			# add raster to layers
			l =cfg.utls.addRasterLayer(str(outputFile), str(cfg.osSCP.path.basename(outputFile)))
			cfg.utls.rasterSymbol(l, sL, "No")
		cfg.uiUtls.updateBar(90)		
		# display parameters
		self.displayParameters(sL, None, outputDirectory, str(cfg.osSCP.path.basename(outputFile)))
		if cfg.ui.kmean_save_siglist_checkBox.isChecked() is True:
			for x in sL:
				id = cfg.utls.signatureID()
				cfg.signIDs["ID_" + str(id)] = id
				vl = []
				wvl = cfg.bandSetsList[bandSetNumber][4]
				sd = []
				for k in range(0, int(len(x[4])/2)):
					vl.append(x[4][k*2])
					sd.append(0)
				cfg.signList["MACROCLASSID_" + str(id)] = x[0]
				cfg.signList["MACROCLASSINFO_" + str(id)] = cfg.kmeansNm + str(x[1])
				cfg.signList["CLASSID_" + str(id)] = x[2]
				cfg.signList["CLASSINFO_" + str(id)] = cfg.kmeansNm + str(x[3])
				cfg.signList["VALUES_" + str(id)] = x[4]
				cfg.signList["LCS_MIN_" + str(id)] = vl
				cfg.signList["LCS_MAX_" + str(id)] = vl
				cfg.signList["MIN_VALUE_" + str(id)] = vl
				cfg.signList["MAX_VALUE_" + str(id)] = vl
				cfg.signList["WAVELENGTH_" + str(id)] = wvl
				cfg.signList["MEAN_VALUE_" + str(id)] = vl
				cfg.signList["SD_" + str(id)] = sd
				cfg.signList["COLOR_" + str(id)] = x[6]
				cfg.signList["CHECKBOX_" + str(id)] = 2
				cfg.signList["UNIT_" + str(id)] = cfg.bandSetsList[bandSetNumber][5]
				cfg.signList["COVMATRIX_" + str(id)] = "No"
				cfg.signList["ROI_SIZE_" + str(id)] = 0
				cfg.signList["MD_THRESHOLD_" + str(id)] = 0
				cfg.signList["ML_THRESHOLD_" + str(id)] = 0
				cfg.signList["SAM_THRESHOLD_" + str(id)] = 0
			cfg.SCPD.ROIListTable(cfg.shpLay, cfg.uidc.signature_list_tableWidget)
			cfg.ui.toolBox_kmeans.setCurrentIndex(1)			
		cfg.uiUtls.updateBar(100)
		if batch == "No":
			# enable map canvas render
			cfg.cnvs.setRenderFlag(True)
			cfg.utls.finishSound()
			cfg.uiUtls.removeProgressBar()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ISODATA calculated")	
		
	# isodata iteration
	def isodataIteration(self, inputGDALRaster, bandList, iteration, k_or_sigs, classNumber, iterations = 20, thresh = 0.00001, minSize = 10, maxStandardDeviation = 0.000001, NoDataValue = None, batch = "No", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if cfg.actionCheck == "Yes":
			algorithmName = cfg.algMinDist
			# calculate band mean
			cfg.rasterClustering = {}
			# No data value
			nD = None
			if NoDataValue is not None:
				nD = NoDataValue
			elif cfg.ui.nodata_checkBox_8.isChecked() is True:
				nD = cfg.ui.nodata_spinBox_9.value()
			# input raster
			rD = inputGDALRaster
			# band list
			bL = bandList
			try:
				k = int(k_or_sigs)
				if cfg.ui.kmean_minmax_radioButton.isChecked() is True:
					try:
						# signatures from minimum maximum values
						o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterMinimumMaximum, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, cfg.bandSetsList[bandSetNumber][6], "Calculating minimum maximum values")
					except Exception as err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					signatures1 = []
					signatureList = []
					kN = 1
					classes = []
					for p in range(0, k):
						sig = []
						signature = []
						for b in range(0, len(bL)):				
							vMin = cfg.rasterClustering["MINIMUM_BAND_" + str(b)]
							vMax = cfg.rasterClustering["MAXIMUM_BAND_" + str(b)]
							d = (vMax - vMin) / k						
							sig.append(vMin - (d/2) + (d * kN))
							signature.append(vMin - (d/2) + (d * kN))
							signature.append(0)
						signatures1.append([sig])
						s = []
						s.append(kN)
						s.append(str(kN))
						s.append(kN)
						s.append(str(kN))
						s.append(signature)
						s.append(cfg.bandSetsList[bandSetNumber][4])
						c, cc = cfg.utls.randomColor()
						s.append(c)
						s.append("No")
						s.append(signature)
						s.append(signature)
						s.append(0)
						signatureList.append(s)
						classes.append([kN, c])
						kN = kN + 1
				else:
					# random seeds
					points = self.createRandomSeeds(k, nD, bandSetNumber)
					signatures1 = []
					signatureList = []
					kN = 1
					classes = []
					for p in range(0, len(points)):
						sig = cfg.utls.calculatePixelSignature(cfg.qgisCoreSCP.QgsPointXY(points[p][0], points[p][1]), cfg.bandSetsList[bandSetNumber][8], bandSetNumber, "Pixel", "No")
						signatures1.append(sig)
						signature = []
						for v in range(0, len(sig)):
							signature.append(sig[v])
							signature.append(0)
						s = []
						s.append(kN)
						s.append(str(kN))
						s.append(kN)
						s.append(str(kN))
						s.append(signature)
						s.append(cfg.bandSetsList[bandSetNumber][4])
						c, cc = cfg.utls.randomColor()
						s.append(c)
						s.append("No")
						s.append(signature)
						s.append(signature)
						s.append(0)
						signatureList.append(s)
						classes.append([kN, c])
						kN = kN + 1
			except:
				# seed signatures
				try:
					k = len(k_or_sigs)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No", None, None
				signatures1 = k_or_sigs
				signatureList = []
				classes = []
				for p in range(0, k):
					sig = signatures1[p][0]
					signature = []
					for v in range(0, len(sig)):
						signature.append(sig[v])
						signature.append(0)
					s = []
					s.append(signatures1[p][1])
					s.append(str(signatures1[p][1]))
					s.append(signatures1[p][1])
					s.append(str(signatures1[p][1]))
					s.append(signature)
					s.append(cfg.bandSetsList[bandSetNumber][4])
					s.append(signatures1[p][2])
					s.append("No")
					s.append(signature)
					s.append(signature)
					s.append(0)
					signatureList.append(s)
					classes.append([signatures1[p][1], signatures1[p][2]])
			# calculation
			previewSize = 0
			previewPoint = None
			compress = cfg.rasterCompression
			# signature rasters
			oRL, opOut = cfg.utls.createSignatureClassRaster(signatureList, rD, cfg.tmpDir, cfg.NoDataVal, None, previewSize, previewPoint, "No")
			# output rasters
			oM = []
			oC = []
			# date time for temp name
			dT = cfg.utls.getTime()
			# temp files
			tPMN = dT + cfg.algRasterNm + "_" + str(iteration) + ".tif"
			tPMD = cfg.tmpDir + "/" + tPMN	
			tPMN2 = dT + cfg.classRasterNm + "_" + str(iteration) + ".tif"
			tPMD2 = cfg.tmpDir + "/" + tPMN2
			oM.append(tPMD)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, previewSize, previewPoint, compress)
			oC.append(tPMD2)
			oCR = cfg.utls.createRasterFromReference(rD, 1, oC, cfg.NoDataVal, "GTiff", cfg.gdalSCP.GDT_Int32, previewSize, previewPoint, compress, "DEFLATE")
			o = cfg.utls.processRaster(rD, bL, signatureList, None, cfg.utls.classification, algorithmName, oRL, oMR[0], oCR[0], previewSize, previewPoint, cfg.NoDataVal, "No", cfg.multiAddFactorsVar, cfg.bandSetsList[bandSetNumber][6])
			if o == "No":
				return "No", None, None
			# last classification
			if iteration == -1:
				# close GDAL rasters
				for x in range(0, len(oRL)):
					fList = oRL[x].GetFileList()
					oRL[x] = None
				for x in range(0, len(oMR)):
					oMR[x] = None
				for x in range(0, len(oCR)):
					oCR[x] = None
				# remove temp rasters
				try:
					for oT in opOut:
						cfg.osSCP.remove(oT)
					cfg.osSCP.remove(tPMD)
				except:
					pass
				return tPMD2, None, None		
			bLC = bL.copy()
			bLC.append(oCR[0])
			bLC.append(oMR[0])
			o = cfg.utls.processRaster(rD, bLC, None, "No", cfg.utls.rasterPixelCountISODATA, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, [classes, cfg.bandSetsList[bandSetNumber][6]], "Sum")
			# calculate band mean
			for c in classes:
				for b in range(0, len(bL)):	
					try:
						cfg.rasterClustering["MEAN_BAND_" + str(b) + "_c_" + str(c[0])] = cfg.rasterClustering["SUM_BAND_" + str(b) + "_c_" + str(c[0])] / cfg.rasterClustering["COUNT_BAND_" + str(b) + "_c_" + str(c[0])]
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						return "No", None, None
			o = cfg.utls.processRaster(rD, bLC, None, "No", cfg.utls.rasterStandardDeviationISODATA, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, [classes, cfg.bandSetsList[bandSetNumber][6]], "Standard deviation")
			classes2 = []
			avDistance = 0
			sumNi = 0
			maxClasses = []
			# calculate standard deviation
			for c in classes:
				try:
					signature = []
					s2 = []
					stdDev = []
					avDist = cfg.rasterClustering["SUM_DIST_" + str(c[0])]
					avDistance = avDistance + avDist
					Ni = cfg.rasterClustering["COUNT_BAND_" + str(0) + "_c_" + str(c[0])]
					if Ni >= minSize:
						maxClasses.append(c[0])
						sumNi = sumNi + Ni
						for b in range(0, len(bL)):	
							stdDev.append(cfg.np.sqrt(cfg.rasterClustering["VAR_BAND_" + str(b) + "_c_" + str(c[0])]))
							v = cfg.rasterClustering["MEAN_BAND_" + str(b) + "_c_" + str(c[0])]
							s2.append(v)
						maxStdDev = max(stdDev)
						try:
							maxStdDevK = stdDev.index(maxStdDev)
						except:
							maxStdDevK = 0
						classes2.append([c[0], c[1], s2, Ni, avDist, maxStdDev, maxStdDevK])
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No", None, None
			# penultimate iteration
			if iteration == -2:
				signatures2 = []
				signatureList2 = []
				count = 1
				for c in classes2:
					signature = []
					s2 = []
					for v in c[2]:
						signature.append(v)
						s2.append(v)
						signature.append(0)
					signatures2.append([s2, count, c[1]])
					s = []
					s.append(count)
					s.append(str(count))
					s.append(count)
					s.append(str(count))
					s.append(signature)
					s.append(cfg.bandSetsList[bandSetNumber][4])
					s.append(c[1])
					s.append("No")
					s.append("")
					s.append("")
					s.append(0)
					signatureList2.append(s)
					count = count + 1
			else:
				# average distance
				AD = avDistance / sumNi
				try:
					maxClass = max(maxClasses)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No", None, None
				classes3 = []
				# check split
				if len(classes2) <= classNumber:
					for c in classes2:
						s2 = []
						s3 = []
						if c[5] > maxStandardDeviation:
							if ((c[4] > AD) and (c[3] > (2 * minSize + 2))) or (2 * len(classes2) < classNumber):
								s2 = c[2].copy()
								s3 = c[2].copy()						
								if s2[c[6]] - c[5] < 0:
									s2[c[6]] = 0
								else:
									s2[c[6]] = s2[c[6]] - c[5]
								s3[c[6]] = s3[c[6]] + c[5]
								classes3.append([c[0], c[1], s2])
								co, cco = cfg.utls.randomColor()
								classes3.append([maxClass + 1, co, s3])
								maxClass = maxClass + 1
						else:
							classes3.append(c)
				# check merge
				else:
					# calculate distance
					distances = []
					merge = []
					for c in classes2:
						for cc in classes2:
							# calculate pairwise distances
							if c[0] < cc[0]:
								dist = cfg.utls.euclideanDistance(c[2], cc[2])
								distances.append(dist)
								merge.append([c[0], cc[0], c[1], cc[1], c[2], cc[2], c[3], cc[3]])
					diff = len(classes2) - classNumber
					cMerge = []
					for n in range(0, diff):
						maxDist = max(distances)
						minDist = min(distances)
						if minDist > thresh:
							cl = distances.index(minDist)
							mergeClass = merge[cl]
							p1 = cfg.np.array(mergeClass[4]) * mergeClass[6]
							p2 = cfg.np.array(mergeClass[5]) * mergeClass[7]
							s2 = (p1 + p2)/(mergeClass[6] + mergeClass[7])
							classes3.append([mergeClass[0], mergeClass[2], s2.tolist()])
							cMerge.append(mergeClass[0])
							cMerge.append(mergeClass[1])
							distances[cl] = maxDist + 1
					for c in classes2:
						if c[0] not in cMerge:
							classes3.append(c)
				signatures2 = []
				signatureList2 = []
				for c in classes3:
					signature = []
					s2 = []
					for v in c[2]:
						signature.append(v)
						s2.append(v)
						signature.append(0)
					signatures2.append([s2, c[0], c[1]])
					s = []
					s.append( c[0])
					s.append(str( c[0]))
					s.append( c[0])
					s.append(str( c[0]))
					s.append(signature)
					s.append(cfg.bandSetsList[bandSetNumber][4])
					s.append(c[1])
					s.append("No")
					s.append("")
					s.append("")
					s.append(0)
					signatureList2.append(s)
			# close GDAL rasters
			for x in range(0, len(oRL)):
				fList = oRL[x].GetFileList()
				oRL[x] = None
			for x in range(0, len(oMR)):
				oMR[x] = None
			for x in range(0, len(oCR)):
				oCR[x] = None
			# remove temp rasters
			try:
				for oT in opOut:
					cfg.osSCP.remove(oT)
				cfg.osSCP.remove(tPMD)
			except:
				pass
			return tPMD2, signatures2, signatureList2
		else:
			return "No", None, None
			
	# K-means calculation
	def kmeansCalculation(self, inputGDALRaster, bandList, outputFile, k_or_sigs, iterations = 10, thresh = 0.000001, NoDataValue = None, batch = "No", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if batch == "No":
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
		cfg.uiUtls.updateBar(10)
		outputDirectory = cfg.osSCP.path.dirname(outputFile)
		# input raster
		rD = inputGDALRaster
		# band list
		bL = bandList		
		cfg.uiUtls.updateBar(20, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " Calculating. Please wait ..."))
		progressStep = int(60 / iterations)
		for iteration in range(0, iterations):
			if cfg.actionCheck == "Yes":
				# remove previous raster
				try:
					cfg.osSCP.remove(r)
				except:
					pass
				r, sigs, sL, distances = self.kmeansIteration(rD, bL, iteration, k_or_sigs, iterations, thresh, NoDataValue, batch, bandSetNumber)
				cfg.uiUtls.updateBar(20 + progressStep, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " Calculating iteration: " + str(iteration) + ". Please wait ..."))
				k_or_sigs = sigs
				if r is None:
					break
			else:
				if batch == "No":
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
					return "No"
		r, sigs0, sL0, distances0 = self.kmeansIteration(rD, bL, -1, k_or_sigs, iterations, thresh, NoDataValue, batch, bandSetNumber)
		cfg.uiUtls.updateBar(80, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " Calculating classification. Please wait ..."))
		for x in range(0, len(bL)):
			bL[x] = None
		rD = None
		cfg.uiUtls.updateBar(90)
		if r == "No":
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error")
			cfg.mx.msgErr45()
		else:
			# copy raster
			if cfg.rasterCompression != "No":
				try:
					cfg.utls.GDALCopyRaster(r, outputFile, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
					cfg.osSCP.remove(r)
				except Exception as err:
					cfg.shutilSCP.copy(r, outputFile)
					cfg.osSCP.remove(r)
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			else:
				cfg.shutilSCP.copy(r, outputFile)
				cfg.osSCP.remove(r)
			# add raster to layers
			l =cfg.utls.addRasterLayer(str(outputFile), str(cfg.osSCP.path.basename(outputFile)))
			cfg.utls.rasterSymbol(l, sL, "No")
		cfg.uiUtls.updateBar(90)		
		# display parameters
		self.displayParameters(sL, distances, outputDirectory, str(cfg.osSCP.path.basename(outputFile)))
		if cfg.ui.kmean_save_siglist_checkBox.isChecked() is True:
			for x in sL:
				id = cfg.utls.signatureID()
				cfg.signIDs["ID_" + str(id)] = id
				vl = []
				wvl = cfg.bandSetsList[bandSetNumber][4]
				sd = []
				for k in range(0, int(len(x[4])/2)):
					vl.append(x[4][k*2])
					sd.append(0)
				cfg.signList["MACROCLASSID_" + str(id)] = x[0]
				cfg.signList["MACROCLASSINFO_" + str(id)] = cfg.kmeansNm + str(x[1])
				cfg.signList["CLASSID_" + str(id)] = x[2]
				cfg.signList["CLASSINFO_" + str(id)] = cfg.kmeansNm + str(x[3])
				cfg.signList["VALUES_" + str(id)] = x[4]
				cfg.signList["LCS_MIN_" + str(id)] = vl
				cfg.signList["LCS_MAX_" + str(id)] = vl
				cfg.signList["MIN_VALUE_" + str(id)] = vl
				cfg.signList["MAX_VALUE_" + str(id)] = vl
				cfg.signList["WAVELENGTH_" + str(id)] = wvl
				cfg.signList["MEAN_VALUE_" + str(id)] = vl
				cfg.signList["SD_" + str(id)] = sd
				cfg.signList["COLOR_" + str(id)] = x[6]
				cfg.signList["CHECKBOX_" + str(id)] = 2
				cfg.signList["UNIT_" + str(id)] = cfg.bandSetsList[bandSetNumber][5]
				cfg.signList["COVMATRIX_" + str(id)] = "No"
				cfg.signList["ROI_SIZE_" + str(id)] = 0
				cfg.signList["MD_THRESHOLD_" + str(id)] = 0
				cfg.signList["ML_THRESHOLD_" + str(id)] = 0
				cfg.signList["SAM_THRESHOLD_" + str(id)] = 0
			cfg.SCPD.ROIListTable(cfg.shpLay, cfg.uidc.signature_list_tableWidget)
			cfg.ui.toolBox_kmeans.setCurrentIndex(1)			
		cfg.uiUtls.updateBar(100)
		if batch == "No":
			# enable map canvas render
			cfg.cnvs.setRenderFlag(True)
			cfg.utls.finishSound()
			cfg.uiUtls.removeProgressBar()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " K-means calculated")
				
	# K-means iteration
	def kmeansIteration(self, inputGDALRaster, bandList, iteration, k_or_sigs, iterations = 20, thresh = 0.00001, NoDataValue = None, batch = "No", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if cfg.actionCheck == "Yes":
			if cfg.ui.min_distance_radioButton.isChecked() is True: 
				algorithmName = cfg.algMinDist
			else:
				algorithmName = cfg.algSAM
			# calculate band mean
			cfg.rasterClustering = {}
			# No data value
			nD = None
			if NoDataValue is not None:
				nD = NoDataValue
			elif cfg.ui.nodata_checkBox_8.isChecked() is True:
				nD = cfg.ui.nodata_spinBox_9.value()
			# input raster
			rD = inputGDALRaster
			# band list
			bL = bandList
			try:
				k = int(k_or_sigs)
				if cfg.ui.kmean_minmax_radioButton.isChecked() is True:
					try:
						# signatures from minimum maximum values
						o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterMinimumMaximum, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, cfg.bandSetsList[bandSetNumber][6], "Calculating minimum maximum values")
					except Exception as err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					signatures1 = []
					signatureList = []
					kN = 1
					classes = []
					for p in range(0, k):
						sig = []
						signature = []
						for b in range(0, len(bL)):				
							vMin = cfg.rasterClustering["MINIMUM_BAND_" + str(b)]
							vMax = cfg.rasterClustering["MAXIMUM_BAND_" + str(b)]
							d = (vMax - vMin) / k						
							sig.append(vMin - (d/2) + (d * kN))
							signature.append(vMin - (d/2) + (d * kN))
							signature.append(0)
						signatures1.append([sig])
						s = []
						s.append(kN)
						s.append(str(kN))
						s.append(kN)
						s.append(str(kN))
						s.append(signature)
						s.append(cfg.bandSetsList[bandSetNumber][4])
						c, cc = cfg.utls.randomColor()
						s.append(c)
						s.append("No")
						s.append(signature)
						s.append(signature)
						s.append(0)
						signatureList.append(s)
						classes.append([kN, c])
						kN = kN + 1
				else:
					# random seeds
					points = self.createRandomSeeds(k, nD, bandSetNumber)
					signatures1 = []
					signatureList = []
					kN = 1
					classes = []
					for p in range(0, len(points)):
						sig = cfg.utls.calculatePixelSignature(cfg.qgisCoreSCP.QgsPointXY(points[p][0], points[p][1]), cfg.bandSetsList[bandSetNumber][8], bandSetNumber, "Pixel", "No")
						signatures1.append(sig)
						signature = []
						for v in range(0, len(sig)):
							signature.append(sig[v])
							signature.append(0)
						s = []
						s.append(kN)
						s.append(str(kN))
						s.append(kN)
						s.append(str(kN))
						s.append(signature)
						s.append(cfg.bandSetsList[bandSetNumber][4])
						c, cc = cfg.utls.randomColor()
						s.append(c)
						s.append("No")
						s.append(signature)
						s.append(signature)
						s.append(0)
						signatureList.append(s)
						classes.append([kN, c])
						kN = kN + 1
			except:
				# seed signatures
				k = len(k_or_sigs)
				signatures1 = k_or_sigs
				signatureList = []
				classes = []
				for p in range(0, k):
					sig = signatures1[p][0]
					signature = []
					for v in range(0, len(sig)):
						signature.append(sig[v])
						signature.append(0)
					s = []
					s.append(signatures1[p][1])
					s.append(str(signatures1[p][1]))
					s.append(signatures1[p][1])
					s.append(str(signatures1[p][1]))
					s.append(signature)
					s.append(cfg.bandSetsList[bandSetNumber][4])
					s.append(signatures1[p][2])
					s.append("No")
					s.append(signature)
					s.append(signature)
					s.append(0)
					signatureList.append(s)
					classes.append([signatures1[p][1], signatures1[p][2]])
			# calculation
			previewSize = 0
			previewPoint = None
			compress = cfg.rasterCompression
			# signature rasters
			oRL, opOut = cfg.utls.createSignatureClassRaster(signatureList, rD, cfg.tmpDir, cfg.NoDataVal, None, previewSize, previewPoint, "No")
			# output rasters
			oM = []
			oC = []
			# date time for temp name
			dT = cfg.utls.getTime()
			# temp files
			tPMN = dT + cfg.algRasterNm + "_" + str(iteration) + ".tif"
			tPMD = cfg.tmpDir + "/" + tPMN	
			tPMN2 = dT + cfg.classRasterNm + "_" + str(iteration) + ".tif"
			tPMD2 = cfg.tmpDir + "/" + tPMN2
			oM.append(tPMD)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, previewSize, previewPoint, compress)
			oC.append(tPMD2)
			oCR = cfg.utls.createRasterFromReference(rD, 1, oC, cfg.NoDataVal, "GTiff", cfg.gdalSCP.GDT_Int32, previewSize, previewPoint, compress, "DEFLATE")
			o = cfg.utls.processRaster(rD, bL, signatureList, None, cfg.utls.classification, algorithmName, oRL, oMR[0], oCR[0], previewSize, previewPoint, cfg.NoDataVal, "No", cfg.multiAddFactorsVar, cfg.bandSetsList[bandSetNumber][6])
			if o == "No":
				return "No", None, None, None
			# last classification
			if iteration == -1:
				# close GDAL rasters
				for x in range(0, len(oRL)):
					fList = oRL[x].GetFileList()
					oRL[x] = None
				for x in range(0, len(oMR)):
					oMR[x] = None
				for x in range(0, len(oCR)):
					oCR[x] = None
				# remove temp rasters
				try:
					for oT in opOut:
						cfg.osSCP.remove(oT)
					cfg.osSCP.remove(tPMD)
				except:
					pass
				return tPMD2, None, None, None
			signatureList2 = []
			bLC = bL.copy()
			bLC.append(oCR[0])
			signatures2 = []
			o = cfg.utls.processRaster(rD, bLC, None, "No", cfg.utls.rasterPixelCountKmeans, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, [classes, cfg.bandSetsList[bandSetNumber][6]], "Sum")
			for c in classes:
				signature = []
				s2 = []
				for b in range(0, len(bL)):
					try:
						v = cfg.rasterClustering["SUM_BAND_" + str(b) + "_c_" + str(c[0])] / cfg.rasterClustering["COUNT_BAND_" + str(b) + "_c_" + str(c[0])]
						signature.append(v)
						s2.append(v)
						signature.append(0)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						return "No", None, None, None
				signatures2.append([s2, c[0], c[1]])
				s = []
				s.append( c[0])
				s.append(str( c[0]))
				s.append( c[0])
				s.append(str( c[0]))
				s.append(signature)
				s.append(cfg.bandSetsList[bandSetNumber][4])
				s.append(c[1])
				s.append("No")
				s.append("")
				s.append("")
				s.append(0)
				signatureList2.append(s)
			# check distance
			distances = []
			for i in range(0, k):
				if algorithmName == cfg.algMinDist:
					dist = cfg.utls.euclideanDistance(signatures1[i][0], signatures2[i][0])
				elif algorithmName == cfg.algSAM:
					dist = cfg.utls.spectralAngle(signatures1[i][0], signatures2[i][0])
				distances.append(dist)
			# close GDAL rasters
			for x in range(0, len(oRL)):
				fList = oRL[x].GetFileList()
				oRL[x] = None
			for x in range(0, len(oMR)):
				oMR[x] = None
			for x in range(0, len(oCR)):
				oCR[x] = None
			# remove temp rasters
			try:
				for oT in opOut:
					cfg.osSCP.remove(oT)
				cfg.osSCP.remove(tPMD)
			except:
				pass
			if max(distances) <= thresh:
				return None, signatures2, signatureList2, distances
			else:
				return tPMD2, signatures2, signatureList2, distances
		else:
			return "No", None, None, None
			
	# create random point
	def createRandomSeeds(self, pointNumber, NoDataValue = None, bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		try:
			if cfg.bandSetsList[bandSetNumber][0] == "Yes":
				imageName = cfg.bandSetsList[bandSetNumber][3][0]
			else:
				if cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], "Yes") is None:
					cfg.mx.msg4()
					return "No"
				else:
					imageName = cfg.bandSetsList[bandSetNumber][8]	
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "No image selected")
			img = cfg.utls.selectLayerbyName(imageName, "Yes")
			crs = cfg.utls.getCrs(img)
			geographicFlag = crs.isGeographic()
			if geographicFlag is False:
				tLX, tLY, lRX, lRY, pSX, pSY = cfg.utls.imageInformationSize(imageName)
				Xmin = int(round(min(tLX, lRX)))
				Xmax = int(round(max(tLX, lRX)))
				Ymin = int(round(min(tLY, lRY)))
				Ymax = int(round(max(tLY, lRY)))
				points = cfg.utls.randomPoints(pointNumber, Xmin, Xmax, Ymin, Ymax, None, cfg.bandSetsList[bandSetNumber][8], NoDataValue)
				return points
			else:
				cfg.mx.msgWar14()
		except Exception as err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					
	# display parameters
	def displayParameters(self, signatureList, distances = None, outputDirectory = None, outputFileName = None):
		tblOut = outputDirectory + "/" + str(outputFileName) + cfg.kmeansReportNm
		try:
			l = open(tblOut, 'w')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		t = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Clustering')) + "	" + str("\n") + str("\n")
		l.write(t)
		tB = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Class')) + "	" + str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Signature')) + "	" + str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Distance')) + str("\n")
		l.write(str(tB))
		c = 0
		for s in signatureList:
			if distances is None:
				d = " "
			else:
				d = str(distances[c])
			tB = str(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'C_ID_')) + str(s[2]) + "	" 
			vB = None
			for k in range(0, int(len(s[4])/2)):
				vl = s[4][k*2]
				if vB is None:					
					vB = str(vl)
				else:
					vB = vB + "," + str(vl)
			l.write(str(tB) + str(vB) + "	" + d + str("\n"))
			c = c + 1
		l.close()
		try:
			f = open(tblOut)
			if cfg.osSCP.path.isfile(tblOut):
				eM = f.read()
				cfg.ui.report_textBrowser_3.setText(str(eM))
				cfg.ui.toolBox_kmeans.setCurrentIndex(1)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "calculated")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))