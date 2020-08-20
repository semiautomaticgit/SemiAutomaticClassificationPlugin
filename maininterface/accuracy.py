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

class Accuracy:

	def __init__(self):
		self.clssfctnNm = None
		
	# calculate error matrix if click on button
	def calculateErrorMatrix(self):
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " calculate Error Matrix")
		self.errorMatrix(self.clssfctnNm, cfg.referenceLayer)
	
	# classification name
	def classificationLayerName(self):
		self.clssfctnNm = cfg.ui.classification_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification name: " + str(self.clssfctnNm))
	
	# error matrix calculation
	def errorMatrix(self, classification, reference, batch = "No", shapefileField = None, rasterOutput = None):
		# check if numpy is updated
		try:
			cfg.np.count_nonzero([1,1,0])
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			rstrCheck = "No"
			cfg.mx.msgErr26()
		if batch == "No":
			errorRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save error matrix raster output"), "", "*.tif", "tif")
		else:
			errorRstPath = rasterOutput
		if errorRstPath is not False:
			if errorRstPath.lower().endswith(".tif"):
				pass
			else:
				errorRstPath = errorRstPath + ".tif"
			if batch == "No":
				iClass = cfg.utls.selectLayerbyName(classification, "Yes")
				l = cfg.utls.selectLayerbyName(reference)
			else:
				try:
					# open input with GDAL
					rD = cfg.gdalSCP.Open(reference, cfg.gdalSCP.GA_ReadOnly)
					if rD is None:
						l = cfg.utls.addVectorLayer(str(reference) , str(cfg.osSCP.path.basename(reference)), "ogr")
					else:
						l = cfg.utls.addRasterLayer(str(reference), str(cfg.osSCP.path.basename(reference)))
					reml = l
					rD = None
					if cfg.osSCP.path.isfile(classification):
						iClass = cfg.utls.addRasterLayer(str(classification), str(cfg.osSCP.path.basename(classification)))
						remiClass = iClass
					else:
						return "No"
				except:
					return "No"
			# date time for temp name
			dT = cfg.utls.getTime()
			if iClass is not None and l is not None:
				# if not reference shapefile
				if l.type() != 0:
					# check projections
					newRstrProj = cfg.utls.getCrs(iClass)
					refRstrProj = cfg.utls.getCrs(l)
					if refRstrProj != newRstrProj:
						cfg.mx.msg9()
						return "No"
				else:
					# vector EPSG
					ql = cfg.utls.layerSource(l)
					if "MultiPolygon?crs=PROJCS" in str(ql):
						# temp shapefile
						tSHP = cfg.tmpDir + "/" + cfg.rclssTempNm + dT + ".shp"
						l = cfg.utls.saveMemoryLayerToShapefile(l, tSHP)
						vEPSG = cfg.utls.getEPSGVector(tSHP)
					else:
						ql = cfg.utls.layerSource(l)
						vEPSG = cfg.utls.getEPSGVector(ql)
					dT = cfg.utls.getTime()
					# in case of reprojection
					qll = cfg.utls.layerSource(l)
					reprjShapefile = cfg.tmpDir + "/" + dT + cfg.osSCP.path.basename(qll)
					qlll = cfg.utls.layerSource(iClass)
					rEPSG = cfg.utls.getEPSGRaster(qlll)
					if vEPSG != rEPSG:
						if cfg.osSCP.path.isfile(reprjShapefile):
							pass
						else:
							try:
								qllll = cfg.utls.layerSource(l)
								cfg.utls.repojectShapefile(qllll, int(vEPSG), reprjShapefile, int(rEPSG))
							except Exception as err:
								# remove temp layers
								try:
									cfg.utls.removeLayerByLayer(reml)
									cfg.utls.removeLayerByLayer(remiClass)
								except:
									pass
								# logger
								cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								return "No"
						l = cfg.utls.addVectorLayer(reprjShapefile, cfg.osSCP.path.basename(reprjShapefile) , "ogr")
				if batch == "No":
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
					cfg.QtWidgetsSCP.qApp.processEvents()
				# temp raster layer
				tRC= cfg.tmpDir + "/" + cfg.rclssTempNm + dT + ".tif"
				# error matrix
				eMN = dT + cfg.errMatrixNm
				cfg.reportPth = str(cfg.tmpDir + "/" + eMN)
				tblOut = cfg.osSCP.path.dirname(errorRstPath) + "/" + cfg.osSCP.path.basename(errorRstPath)
				tblOut = cfg.osSCP.path.splitext(tblOut)[0] + ".csv"
				cfg.uiUtls.updateBar(10)
				# if reference shapefile
				if l.type()== 0:
					if batch == "No":
						fd = cfg.ui.class_field_comboBox.currentText()
					else:
						fd = shapefileField
					if batch == "No":
						# convert reference layer to raster
						qlllll = cfg.utls.layerSource(l)
						qllllll = cfg.utls.layerSource(iClass)
						vect = cfg.utls.vectorToRaster(fd, str(qlllll), classification, str(tRC), str(qllllll), extent = "Yes")
					else:
						qlllllll = cfg.utls.layerSource(l)
						vect = cfg.utls.vectorToRaster(fd, str(qlllllll), classification, str(tRC), classification, extent = "Yes")
					if vect == "No":
						if batch == "No":
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()
						return "No"	
					referenceRaster = tRC
				# if reference raster
				elif l.type()== 1:
					if batch == "No":
						referenceRaster = cfg.utls.layerSource(l)
					else:
						referenceRaster = reference
				# open input with GDAL
				refRstrDt = cfg.gdalSCP.Open(str(referenceRaster), cfg.gdalSCP.GA_ReadOnly)
				qllllllll = cfg.utls.layerSource(iClass)
				newRstrDt = cfg.gdalSCP.Open(qllllllll, cfg.gdalSCP.GA_ReadOnly)
				# combination finder
				# band list
				bLR = cfg.utls.readAllBandsFromRaster(refRstrDt)
				cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
				cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
				o = cfg.utls.processRaster(refRstrDt, bLR, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
				cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
				refRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)
				# band list
				bLN = cfg.utls.readAllBandsFromRaster(newRstrDt)
				cfg.rasterBandUniqueVal = {}
				o = cfg.utls.processRaster(newRstrDt, bLN, None, "No", cfg.utls.rasterUniqueValuesWithSum, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
				newRasterBandUniqueVal = []
				pixelTotal = {} 
				totPixelClass = 0
				for i in sorted(cfg.rasterBandUniqueVal):
					newRasterBandUniqueVal.append(i)
					pixelTotal[i] = cfg.rasterBandUniqueVal[i]
					totPixelClass = totPixelClass + cfg.rasterBandUniqueVal[i]
				for b in range(0, len(bLR)):
					bLR[b] = None
				refRstrDt = None
				for b in range(0, len(bLN)):
					bLN[b] = None
				newRstrDt = None		
				cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
				cmb = list(cfg.itertoolsSCP.product(refRasterBandUniqueVal, newRasterBandUniqueVal))
				# error matrix
				col = []
				row = []
				cmbntns = {}
				# expression builder
				n = 1
				e = []
				for i in cmb:
					if str(i[0]) == "nan" or str(i[1]) == "nan" :
						pass
					else:
						e.append("cfg.np.where( (a == " + str(i[0]) + ") & (b == " + str(i[1]) + "), " + str(n) + ", 0)")
						cmbntns["combination_" + str(i[0]) + "_"+ str(i[1])] = n
						col.append(i[0])
						row.append(i[1])
						n = n + 1
				# virtual raster
				tPMN = cfg.tmpVrtNm + ".vrt"
				# date time for temp name
				dT = cfg.utls.getTime()
				tPMD = cfg.tmpDir + "/" + dT + tPMN
				tPMN2 = dT + cfg.calcRasterNm + ".tif"
				tPMD2 = cfg.tmpDir + "/" + tPMN2
				bList = [str(referenceRaster), cfg.utls.layerSource(iClass)]
				bandNumberList = [1, 1]
				vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "No")
				# open input with GDAL
				rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
				# output rasters
				oM = []
				oM.append(tPMD2)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
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
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# calculation
				variableList = [["im1", "a"], ["im2", "b"]]
				cfg.rasterBandUniqueVal = {}
				o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.bandCalculationMultipleWhere, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "Calculating raster")
				cfg.rasterBandUniqueVal.pop(cfg.NoDataVal, None)
				if o == "No":
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr48()
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error")
					return "No"
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "accuracy raster output: " + str(errorRstPath))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				if cfg.rasterCompression != "No":
					try:
						cfg.utls.GDALCopyRaster(tPMD2, errorRstPath, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						cfg.osSCP.remove(tPMD2)
					except Exception as err:
						cfg.shutilSCP.copy(tPMD2, errorRstPath)
						cfg.osSCP.remove(tPMD2)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					cfg.shutilSCP.copy(tPMD2, errorRstPath)
					cfg.osSCP.remove(tPMD2)
				cfg.uiUtls.updateBar(80)
				cols = sorted(cfg.np.unique(col).tolist())
				rows = sorted(cfg.np.unique(row).tolist())
				totX = cols
				totX.extend(rows)
				total = sorted(cfg.np.unique(totX).tolist())
				errMatrix = cfg.np.zeros((len(total), len(total) + 1))
				errMatrixUnbias = cfg.np.zeros((len(total), len(total) + 2))
				cList = "V_" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Classified') + "\t"
				try:
					l = open(tblOut, 'w')
				except Exception as err:
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				# error raster table
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'ErrMatrixCode') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Reference') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Classified') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'PixelSum') + "\n"
				l.write(t)
				for c in total:
					cList = cList + str(int(c)) + "\t"
					for r in total:
						try:
							v = cmbntns["combination_" + str(c) + "_"+ str(r)]
							t = str(v) + "\t" + str(int(c)) + "\t" + str(int(r)) + "\t" + str(cfg.rasterBandUniqueVal[v]) + str("\n")
							l.write(t)
							errMatrix[total.index(r), total.index(c)] = cfg.rasterBandUniqueVal[v]
							errMatrixUnbias[total.index(r), total.index(c)] = cfg.rasterBandUniqueVal[v]
						except:
							errMatrix[total.index(r), total.index(c)] = 0
							errMatrixUnbias[total.index(r), total.index(c)] = 0
				# sum without totals
				totMat = int(errMatrix.sum())
				# add totals to matrices
				for r in total:
					errMatrix[total.index(r), len(total)] = int(errMatrix[total.index(r), :].sum())
					try:
						errMatrixUnbias[total.index(r), len(total)] = pixelTotal[r] * cRPX * cRPY
					except:
						errMatrixUnbias[total.index(r), len(total)] = 0
					try:
						errMatrixUnbias[total.index(r), len(total) + 1] = pixelTotal[r] / totPixelClass
					except:
						errMatrixUnbias[total.index(r), len(total) + 1] = 0
				for c in total:
					for r in total:
						try:
							errMatrixUnbias[total.index(r), total.index(c)] = errMatrixUnbias[total.index(r), len(total) + 1] * (errMatrix[total.index(r), total.index(c)] ) / errMatrix[total.index(r), len(total) ]
						except:
							errMatrixUnbias[total.index(r), total.index(c)] = 0
				errMatrix[cfg.np.isnan(errMatrix)] = 0
				errMatrixUnbias[cfg.np.isnan(errMatrixUnbias)] = 0
				# save combination to table
				l.write(str("\n"))
				tStr = "\t" + "> " + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'ERROR MATRIX (pixel count)') + "\n"
				l.write(tStr)
				tStr = "\t" + "> " + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Reference') + "\n"
				l.write(tStr)
				tStr = cList + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Total') + "\n"
				l.write(tStr)
				# temp matrix
				tmpMtrx= cfg.tmpDir + "/" + cfg.tempMtrxNm + dT + ".txt"
				cfg.np.savetxt(tmpMtrx, errMatrix, delimiter="\t", fmt="%i")
				tM = open(tmpMtrx, 'r')
				# write matrix
				ix = 0
				for j in tM:
					tMR = str(int(total[ix])) + "\t" + j
					l.write(tMR)
					ix = ix + 1
				lL = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Total')
				for c in range(0, len(total)):
					lL = lL + "\t" + str(int(errMatrix[:, c].sum()))
				lL = lL + "\t" + str(totMat) + str("\n")
				l.write(lL)
				
				# area based error matrix (see Olofsson, et al., 2014, Good practices for estimating area and assessing accuracy of land change, Remote Sensing of Environment, 148, 42-57)
				l.write(str("\n"))
				tStr = "\t" + "> " + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'AREA BASED ERROR MATRIX') + "\n"
				l.write(tStr)
				tStr = "\t" + "> " + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Reference') + "\n"
				l.write(tStr)
				tStr = cList + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Area') + "\t" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Wi') + "\n"
				l.write(tStr)
				# temp matrix
				# date time for temp name
				dT = cfg.utls.getTime()
				tmpMtrxU= cfg.tmpDir + "/" + cfg.tempMtrxNm + dT + ".txt"
				cfg.np.savetxt(tmpMtrxU, errMatrixUnbias, delimiter="\t", fmt="%1.4f")
				tM = open(tmpMtrxU, 'r')
				ix = 0
				for j in tM:
					tMR = str(int(total[ix])) + "\t" + j
					l.write(tMR)
					ix = ix + 1
				# last lines
				lL = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Total')
				for c in range(0, len(total)):
					lL = lL + "\t" + str("%1.4f " % errMatrixUnbias[:, c].sum())
				lL = lL + "\t" + str("%1.4f " % (totPixelClass * cRPX * cRPY)) + str("\n")
				l.write(lL)
				lL0 = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Area')
				for c in range(0, len(total)):
					lL0 = lL0 + "\t" + str( int(round(totPixelClass * cRPX * cRPY * errMatrixUnbias[:, c].sum())))
				lL0 = lL0 + "\t" + str(int(totPixelClass * cRPX * cRPY)) + str("\n")
				l.write(lL0)
				lL1 = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'SE')
				lL2 = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'SE area')
				lL3 = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", '95% CI area')
				for c in range(0, len(total)):
					se = 0
					for r in range(0, len(total)):
						se = se + (errMatrixUnbias[r, len(total) + 1]  * errMatrixUnbias[r, c] - errMatrixUnbias[r, c] * errMatrixUnbias[r, c] ) / (errMatrix[r, len(total) ] - 1)
						try:
							int(se)
						except:
							se = 0
					lL1 = lL1 + "\t" + str("%1.4f" % cfg.np.sqrt(se))
					lL2 = lL2 + "\t" + str(int(round(cfg.np.sqrt(se) * totPixelClass * cRPX * cRPY)))
					lL3 = lL3 + "\t" + str(int(round(cfg.np.sqrt(se) * totPixelClass * cRPX * cRPY * 1.96)))
				l.write(lL1)
				l.write(str("\n"))
				l.write(lL2)
				l.write(str("\n"))
				l.write(lL3)
				l.write(str("\n"))
				# user and producer's accuracy and kappa hat, equations from Congalton, R. & Green, K. (2009) Assessing the Accuracy of Remotely Sensed Data: Principles and Practices. CRC Press
				lL4 = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'PA  [%]')
				lL5 = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'UA  [%]')
				lL6 = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Kappa hat')
				nipXnpi = 0
				niiTot = 0
				for g in range(0, len(total)):
					nii = errMatrixUnbias[g,g]
					niiTot = niiTot + nii
					nip = errMatrixUnbias[g, 0:len(total)].sum()
					npi = errMatrixUnbias[0:len(total), g].sum()
					nipXnpi = nipXnpi + (nip * npi)
					p = 100 * nii / npi
					u = 100 * nii / nip
					khatI = ((1 * nii) - (nip * npi)) / ((1 * nip) - (nip * npi))
					lL4 = lL4 + "\t" + str("%1.4f" % p)
					lL5 = lL5 + "\t" + str("%1.4f" % u)
					lL6 = lL6 + "\t" + str("%1.4f" % khatI)
				l.write(lL4)
				l.write(str("\n"))
				l.write(lL5)
				l.write(str("\n"))
				l.write(lL6)
				l.write(str("\n"))
				# overall accuracy
				l.write(str("\n"))
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Overall accuracy [%] = ') + str("%1.4f" % (niiTot * 100)) + "\n"
				l.write(t)
				khat = ((1 * niiTot) - nipXnpi) / ((1 * 1) - nipXnpi)
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Kappa hat classification = ') + str("%1.4f" % khat) + str("\n")
				l.write(t)
				l.write(str("\n"))
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Area unit = ' + un + "^2") + str("\n")
				l.write(t)
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'SE = standard error') + str("\n")
				l.write(t)
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'CI = confidence interval') + str("\n")
				l.write(t)
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "PA = producer's accuracy") + str("\n")
				l.write(t)
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "UA = user's accuracy") + str("\n")
				l.write(t)
				l.close()
				# add raster to layers
				rstr = cfg.utls.addRasterLayer(str(errorRstPath), str(cfg.osSCP.path.basename(errorRstPath)))
				cfg.utls.rasterSymbolGeneric(rstr, "NoData")	
				try:
					f = open(tblOut)
					if cfg.osSCP.path.isfile(tblOut):
						eM = f.read()
						cfg.ui.error_matrix_textBrowser.setText(eM)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " error matrix calculated")
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.uiUtls.updateBar(100)
				if batch == "No":
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.ui.toolBox_accuracy.setCurrentIndex(1)
					cfg.uiUtls.removeProgressBar()
				else:
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except:
						pass
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "finished")
			else:
				self.refreshReferenceLayer()
				cfg.utls.refreshClassificationLayer()
				
	# reference layer name
	def referenceLayerName(self):
		cfg.referenceLayer = cfg.ui.reference_name_combo.currentText()
		cfg.ui.class_field_comboBox.clear()
		l = cfg.utls.selectLayerbyName(cfg.referenceLayer)
		try:
			if l.type()== 0:
				f = l.dataProvider().fields()
				for i in f:
					if i.typeName() != "String":
						cfg.dlg.class_field_combo(str(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layer name: " + str(cfg.referenceLayer))
	
	# refresh reference layer name
	def refreshReferenceLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.reference_name_combo.clear()
		# reference layer name
		cfg.referenceLayer = None
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type()== cfg.qgisCoreSCP.QgsMapLayer.VectorLayer):
				if (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.Polygon) or (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.MultiPolygon):
					cfg.dlg.reference_layer_combo(l.name())
			elif (l.type()== cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.reference_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layers refreshed")
