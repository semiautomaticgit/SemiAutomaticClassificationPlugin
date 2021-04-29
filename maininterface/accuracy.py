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

class Accuracy:

	def __init__(self):
		self.clssfctnNm = None
		
	# calculate error matrix if click on button
	def calculateErrorMatrix(self):
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' calculate Error Matrix')
		# No data value
		if cfg.ui.nodata_checkBox_11.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_15.value()
		else:
			nD = None
		self.errorMatrix(self.clssfctnNm, cfg.referenceLayer, NoDataValue = nD)
	
	# classification name
	def classificationLayerName(self):
		self.clssfctnNm = cfg.ui.classification_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'classification name: ' + str(self.clssfctnNm))
	
	# error matrix calculation
	def errorMatrix(self, classification, reference, batch = 'No', shapefileField = None, rasterOutput = None, NoDataValue = None):
		# check if numpy is updated
		try:
			cfg.np.count_nonzero([1,1,0])
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			rstrCheck = 'No'
			cfg.mx.msgErr26()
		if batch == 'No':
			errorRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save error matrix raster output'), '', 'TIF file (*.tif);;VRT file (*.vrt)')
		else:
			errorRstPath = rasterOutput
		# virtual raster
		vrtR = 'No'
		if errorRstPath is not False:
			if errorRstPath.lower().endswith('.vrt'):
				vrtR = 'Yes'
			elif errorRstPath.lower().endswith('.tif'):
				pass
			else:
				errorRstPath = errorRstPath + '.tif'
			if batch == 'No':
				iClass = cfg.utls.selectLayerbyName(classification, 'Yes')
				l = cfg.utls.selectLayerbyName(reference)
			else:
				try:
					# open input with GDAL
					rD = cfg.gdalSCP.Open(reference, cfg.gdalSCP.GA_ReadOnly)
					if rD is None:
						l = cfg.utls.addVectorLayer(reference, cfg.utls.fileName(reference), 'ogr')
					else:
						l = cfg.utls.addRasterLayer(reference)
					reml = l
					rD = None
					if cfg.osSCP.path.isfile(classification):
						iClass = cfg.utls.addRasterLayer(classification)
						remiClass = iClass
					else:
						return 'No'
				except:
					return 'No'
			# date time for temp name
			dT = cfg.utls.getTime()
			cfg.utls.makeDirectory(cfg.osSCP.path.dirname(errorRstPath))
			if iClass is not None and l is not None:
				# if not reference shapefile
				if l.type() != 0:
					# check projections
					newRstrProj = cfg.utls.getCrs(iClass)
					refRstrProj = cfg.utls.getCrs(l)
					if refRstrProj != newRstrProj:
						cfg.mx.msg9()
						return 'No'
				else:
					# vector EPSG
					ql = cfg.utls.layerSource(l)
					if 'Polygon?crs=' in str(ql) or 'memory?geometry=' in str(ql):
						# temp shapefile
						tSHP = cfg.utls.createTempRasterPath('gpkg')
						l = cfg.utls.saveMemoryLayerToShapefile(l, tSHP, format = 'GPKG')
						vCrs = cfg.utls.getCrsGDAL(tSHP)
						vEPSG = cfg.osrSCP.SpatialReference()
						vEPSG.ImportFromWkt(vCrs)
					else:
						ql = cfg.utls.layerSource(l)
						vCrs = cfg.utls.getCrsGDAL(ql)
						vEPSG = cfg.osrSCP.SpatialReference()
						vEPSG.ImportFromWkt(vCrs)
					# in case of reprojection
					qll = cfg.utls.layerSource(l)
					reprjShapefile = cfg.tmpDir + '/' + dT + cfg.utls.fileName(qll)
					qlll = cfg.utls.layerSource(iClass)
					rCrs = cfg.utls.getCrsGDAL(qlll)
					rEPSG = cfg.osrSCP.SpatialReference()
					rEPSG.ImportFromWkt(rCrs)
					if vEPSG.IsSame(rEPSG) != 1:
						if cfg.osSCP.path.isfile(reprjShapefile):
							pass
						else:
							try:
								qllll = cfg.utls.layerSource(l)
								cfg.utls.repojectShapefile(qllll, vEPSG, reprjShapefile, rEPSG)
							except Exception as err:
								# remove temp layers
								try:
									cfg.utls.removeLayerByLayer(reml)
									cfg.utls.removeLayerByLayer(remiClass)
								except:
									pass
								# logger
								cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
								return 'No'
						l = cfg.utls.addVectorLayer(reprjShapefile, cfg.utls.fileName(reprjShapefile) , 'ogr')
				if batch == 'No':
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
					cfg.QtWidgetsSCP.qApp.processEvents()
				# temp raster layer
				tRC= cfg.utls.createTempRasterPath('tif')
				# error matrix
				eMN = dT + cfg.errMatrixNm
				cfg.reportPth = str(cfg.tmpDir + '/' + eMN)
				tblOut = cfg.osSCP.path.dirname(errorRstPath) + '/' + cfg.utls.fileNameNoExt(errorRstPath) + '.csv'
				cfg.uiUtls.updateBar(10)
				# if reference shapefile
				if l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
					if batch == 'No':
						fd = cfg.ui.class_field_comboBox.currentText()
					else:
						fd = shapefileField
					if batch == 'No':
						# convert reference layer to raster
						qlllll = cfg.utls.layerSource(l)
						qllllll = cfg.utls.layerSource(iClass)
						vect = cfg.utls.vectorToRaster(fd, str(qlllll), classification, str(tRC), str(qllllll), extent = 'Yes')
					else:
						qlllllll = cfg.utls.layerSource(l)
						vect = cfg.utls.vectorToRaster(fd, str(qlllllll), classification, str(tRC), classification, extent = 'Yes')
					if vect == 'No':
						if batch == 'No':
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()
						return 'No'	
					referenceRaster = tRC
				# if reference raster
				elif l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer:
					if batch == 'No':
						referenceRaster = cfg.utls.layerSource(l)
					else:
						referenceRaster = reference
						
				qllllllll = cfg.utls.layerSource(iClass)
				# combination finder
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = referenceRaster, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'), nodataValue = NoDataValue)
				if o == 'No':
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr45()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error')
					return 'No'
				# calculate unique values
				valuesA = cfg.np.array([])
				for x in sorted(cfg.parallelArrayDict):
					try:
						for ar in cfg.parallelArrayDict[x]:
							valuesA = cfg.np.append(valuesA, ar[0, ::])
					except:
						if batch == 'No':
							cfg.utls.finishSound()
							cfg.utls.sendSMTPMessage(None, str(__name__))
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()			
						# logger
						cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR values')
						cfg.mx.msgErr9()		
						return 'No'
				valuesA = valuesA.astype(int)
				try:
					cmbA = cfg.np.unique(valuesA, axis = 0).tolist()
					refRasterBandUniqueVal = sorted(cmbA)	
				except:
					if batch == 'No':
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					# logger
					cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR values')
					cfg.mx.msgErr9()		
					return 'No'
				# new raster
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = qllllllll, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'), nodataValue = NoDataValue)
				if o == 'No':
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr45()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error')
					return 'No'
				# calculate unique values
				valuesB = cfg.np.array([])
				sumVal = cfg.np.array([])
				for x in sorted(cfg.parallelArrayDict):
					try:
						for ar in cfg.parallelArrayDict[x]:
							valuesB = cfg.np.append(valuesB, ar[0, ::])
							sumVal = cfg.np.append(sumVal, ar[1, ::])
					except:
						if batch == 'No':
							cfg.utls.finishSound()
							cfg.utls.sendSMTPMessage(None, str(__name__))
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()			
						# logger
						cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR values')
						cfg.mx.msgErr9()		
						return 'No'
				reclRasterBandUniqueVal = {}
				valuesB = valuesB.astype(int)
				for v in range(0, len(valuesB)):
					try:
						reclRasterBandUniqueVal[valuesB[v]] = reclRasterBandUniqueVal[valuesB[v]] + sumVal[v]
					except:
						reclRasterBandUniqueVal[valuesB[v]] = sumVal[v]
				newRasterBandUniqueVal = []
				pixelTotal = {} 
				totPixelClass = 0
				for i in sorted(reclRasterBandUniqueVal):
					newRasterBandUniqueVal.append(i)
					pixelTotal[i] = reclRasterBandUniqueVal[i]
					totPixelClass = totPixelClass + reclRasterBandUniqueVal[i]
				bandsUniqueVal = [refRasterBandUniqueVal, newRasterBandUniqueVal]
				try:
					cmb = list(cfg.itertoolsSCP.product(*bandsUniqueVal))
					testCmb = cmb[0]
				except Exception as err:
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr63()
					# logger
					if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return 'No'
				# expression builder
				check = 'No'
				t = 0
				while t < 100:
					t = t + 1
					rndVarList = []
					for cmbI in range(0, len(cmb[0])):
						rndVarList.append(int(999 * cfg.np.random.random()))
					n = 1
					col = []
					row = []
					cmbntns = {}
					newValueList = []
					reclassList = []
					for i in cmb:
						newVl = cfg.np.multiply(rndVarList, i).sum()
						newValueList.append(newVl)
						reclassList.append([newVl, n])
						cmbntns['combination_' + str(i[0]) + '_'+ str(i[1])] = n
						col.append(i[1])
						row.append(i[0])
						n = n + 1
					uniqueValList = cfg.np.unique(newValueList)
					if int(uniqueValList.shape[0]) == len(newValueList):
						check = 'Yes'
						break
				if check == 'No':
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					return 'No'
				e = ''
				for rE in range(0, len(rndVarList)):
					e = e + 'rasterSCPArrayfunctionBand[::, ::, ' + str(rE) + '] * ' + str(rndVarList[rE]) + ' + '
				e = e.rstrip(' + ')			
				# calculation
				bList = [referenceRaster, qllllllll]
				bandNumberList = [1, 1]
				vrtCheck = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'No')
				o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.crossRasters, outputRasterList = [errorRstPath],  functionBandArgument = reclassList, functionVariable = e, progressMessage = 'accuracy ', compress = cfg.rasterCompression,  nodataValue = NoDataValue, outputNoDataValue = -10, virtualRaster = vrtR, dataType = 'Int32')
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = errorRstPath, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'))
				# check projections
				left, right, top, bottom, cRPX, cRPY, rP, un = cfg.utls.imageGeoTransform(errorRstPath)			
				if o == 'No':
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr45()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error')
					return 'No'
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'land cover change raster output: ' + str(errorRstPath))
				# calculate unique values
				values = cfg.np.array([])
				sumVal = cfg.np.array([])
				for x in sorted(cfg.parallelArrayDict):
					try:
						for ar in cfg.parallelArrayDict[x]:
							values = cfg.np.append(values, ar[0, ::])
							sumVal = cfg.np.append(sumVal, ar[1, ::])
					except:
						if batch == 'No':
							cfg.utls.finishSound()
							cfg.utls.sendSMTPMessage(None, str(__name__))
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()			
						# logger
						cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR values')
						cfg.mx.msgErr9()		
						return 'No'
				rasterBandUniqueVal = {}
				values = values.astype(int)
				for v in range(0, len(values)):
					try:
						rasterBandUniqueVal[values[v]] = rasterBandUniqueVal[values[v]] + sumVal[v]
					except:
						rasterBandUniqueVal[values[v]] = sumVal[v]
				cfg.uiUtls.updateBar(80)
				cols = sorted(cfg.np.unique(col).tolist())
				rows = sorted(cfg.np.unique(row).tolist())
				totX = cols
				totX.extend(rows)
				total = sorted(cfg.np.unique(totX).tolist())
				errMatrix = cfg.np.zeros((len(total), len(total) + 1))
				errMatrixUnbias = cfg.np.zeros((len(total), len(total) + 2))
				cList = 'V_' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Classified') + '\t'
				try:
					l = open(tblOut, 'w')
				except Exception as err:
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					return 'No'
				# error raster table
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'ErrMatrixCode') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reference') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Classified') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'PixelSum') + '\n'
				l.write(t)
				for c in total:
					cList = cList + str(int(c)) + '\t'
					for r in total:
						try:
							v = cmbntns['combination_' + str(c) + '_'+ str(r)]
							t = str(v) + '\t' + str(int(c)) + '\t' + str(int(r)) + '\t' + str(rasterBandUniqueVal[v]) + str('\n')
							l.write(t)
							errMatrix[total.index(r), total.index(c)] = rasterBandUniqueVal[v]
							errMatrixUnbias[total.index(r), total.index(c)] = rasterBandUniqueVal[v]
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
				l.write(str('\n'))
				tStr = '\t' + '> ' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'ERROR MATRIX (pixel count)') + '\n'
				l.write(tStr)
				tStr = '\t' + '> ' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reference') + '\n'
				l.write(tStr)
				tStr = cList + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Total') + '\n'
				l.write(tStr)
				# temp matrix
				tmpMtrx= cfg.utls.createTempRasterPath('txt')
				cfg.np.savetxt(tmpMtrx, errMatrix, delimiter='\t', fmt='%i')
				tM = open(tmpMtrx, 'r')
				# write matrix
				ix = 0
				for j in tM:
					tMR = str(int(total[ix])) + '\t' + j
					l.write(tMR)
					ix = ix + 1
				lL = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Total')
				for c in range(0, len(total)):
					lL = lL + '\t' + str(int(errMatrix[:, c].sum()))
				lL = lL + '\t' + str(totMat) + str('\n')
				l.write(lL)
				# area based error matrix (see Olofsson, et al., 2014, Good practices for estimating area and assessing accuracy of land change, Remote Sensing of Environment, 148, 42-57)
				l.write(str("\n"))
				tStr = '\t' + '> ' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'AREA BASED ERROR MATRIX') + '\n'
				l.write(tStr)
				tStr = '\t' + '> ' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reference') + '\n'
				l.write(tStr)
				tStr = cList + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Area') + '\t' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Wi') + '\n'
				l.write(tStr)
				# temp matrix
				tmpMtrxU= cfg.utls.createTempRasterPath('txt')
				cfg.np.savetxt(tmpMtrxU, errMatrixUnbias, delimiter='\t', fmt='%1.4f')
				tM = open(tmpMtrxU, 'r')
				ix = 0
				for j in tM:
					tMR = str(int(total[ix])) + '\t' + j
					l.write(tMR)
					ix = ix + 1
				# last lines
				lL = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Total')
				for c in range(0, len(total)):
					lL = lL + '\t' + str('%1.4f ' % errMatrixUnbias[:, c].sum())
				lL = lL + '\t' + str('%1.4f ' % (totPixelClass * cRPX * cRPY)) + str('\n')
				l.write(lL)
				lL0 = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Area')
				for c in range(0, len(total)):
					lL0 = lL0 + '\t' + str( int(round(totPixelClass * cRPX * cRPY * errMatrixUnbias[:, c].sum())))
				lL0 = lL0 + '\t' + str(int(totPixelClass * cRPX * cRPY)) + str('\n')
				l.write(lL0)
				lL1 = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'SE')
				lL2 = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'SE area')
				lL3 = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', '95% CI area')
				for c in range(0, len(total)):
					se = 0
					for r in range(0, len(total)):
						se = se + (errMatrixUnbias[r, len(total) + 1]  * errMatrixUnbias[r, c] - errMatrixUnbias[r, c] * errMatrixUnbias[r, c] ) / (errMatrix[r, len(total) ] - 1)
						try:
							int(se)
						except:
							se = 0
					lL1 = lL1 + '\t' + str('%1.4f' % cfg.np.sqrt(se))
					try:
						lL2 = lL2 + '\t' + str(int(round(cfg.np.sqrt(se) * totPixelClass * cRPX * cRPY)))
					except:
						lL2 = lL2 + '\t' + '0'
					try:
						lL3 = lL3 + '\t' + str(int(round(cfg.np.sqrt(se) * totPixelClass * cRPX * cRPY * 1.96)))
					except:
						lL3 = lL3 + '\t' + '0'
				l.write(lL1)
				l.write(str('\n'))
				l.write(lL2)
				l.write(str('\n'))
				l.write(lL3)
				l.write(str("\n"))
				# user and producer's accuracy and kappa hat, equations from Congalton, R. & Green, K. (2009) Assessing the Accuracy of Remotely Sensed Data: Principles and Practices. CRC Press
				lL4 = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'PA  [%]')
				lL5 = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'UA  [%]')
				lL6 = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Kappa hat')
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
					lL4 = lL4 + '\t' + str('%1.4f' % p)
					lL5 = lL5 + '\t' + str('%1.4f' % u)
					lL6 = lL6 + '\t' + str('%1.4f' % khatI)
				l.write(lL4)
				l.write(str('\n'))
				l.write(lL5)
				l.write(str('\n'))
				l.write(lL6)
				l.write(str('\n'))
				# overall accuracy
				l.write(str('\n'))
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Overall accuracy [%] = ') + str('%1.4f' % (niiTot * 100)) + '\n'
				l.write(t)
				khat = ((1 * niiTot) - nipXnpi) / ((1 * 1) - nipXnpi)
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Kappa hat classification = ') + str('%1.4f' % khat) + str('\n')
				l.write(t)
				l.write(str('\n'))
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Area unit = ' + un + '^2') + str('\n')
				l.write(t)
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'SE = standard error') + str('\n')
				l.write(t)
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'CI = confidence interval') + str('\n')
				l.write(t)
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', "PA = producer's accuracy") + str('\n')
				l.write(t)
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', "UA = user's accuracy") + str('\n')
				l.write(t)
				l.close()
				# add raster to layers
				rstr = cfg.utls.addRasterLayer(errorRstPath)
				cfg.utls.rasterSymbolGeneric(rstr, 'NoData')	
				try:
					f = open(tblOut)
					if cfg.osSCP.path.isfile(tblOut):
						eM = f.read()
						cfg.ui.error_matrix_textBrowser.setText(eM)
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' error matrix calculated')
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				cfg.uiUtls.updateBar(100)
				if batch == 'No':
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
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
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'finished')
			else:
				self.refreshReferenceLayer()
				cfg.utls.refreshClassificationLayer()
				
	# reference layer name
	def referenceLayerName(self):
		cfg.referenceLayer = cfg.ui.reference_name_combo.currentText()
		cfg.ui.class_field_comboBox.clear()
		l = cfg.utls.selectLayerbyName(cfg.referenceLayer)
		try:
			if l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
				f = l.dataProvider().fields()
				for i in f:
					if str(i.typeName()).lower() != 'string':
						cfg.dlg.class_field_combo(str(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'reference layer name: ' + str(cfg.referenceLayer))
	
	# refresh reference layer name
	def refreshReferenceLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.reference_name_combo.clear()
		# reference layer name
		cfg.referenceLayer = None
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer):
				if (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.Polygon) or (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.MultiPolygon):
					cfg.dlg.reference_layer_combo(l.name())
			elif (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.reference_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layers refreshed")
