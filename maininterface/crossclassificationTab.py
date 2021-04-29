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

class CrossClassification:

	def __init__(self):
		self.clssfctnNm = None
		
	# calculate cross classification if click on button
	def calculateCrossClassification(self):
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' calculate Cross Classification ')
		self.crossClassification(self.clssfctnNm, cfg.referenceLayer2)
	
	# classification name
	def classificationLayerName(self):
		self.clssfctnNm = cfg.ui.classification_name_combo_2.currentText()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'classification name: ' + str(self.clssfctnNm))
	
	# cross classification calculation
	def crossClassification(self, classification, reference, batch = 'No', shapefileField = None, rasterOutput = None,  NoDataValue = None):
		# check if numpy is updated
		try:
			cfg.np.count_nonzero([1,1,0])
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			rstrCheck = 'No'
			cfg.mx.msgErr26()
		if batch == 'No':
			crossRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save cross classification raster output'), '', 'TIF file (*.tif);;VRT file (*.vrt)')
		else:
			crossRstPath = rasterOutput
		# virtual raster
		vrtR = 'No'
		if crossRstPath is not False:
			if crossRstPath.lower().endswith('.vrt'):
				vrtR = 'Yes'
			elif crossRstPath.lower().endswith('.tif'):
				pass
			else:
				crossRstPath = crossRstPath + '.tif'
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
			if iClass is not None and l is not None:
				cfg.utls.makeDirectory(cfg.osSCP.path.dirname(crossRstPath))
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
					if 'Polygon?crs=' in str(cfg.utls.layerSource(l)) or 'memory?geometry=' in str(cfg.utls.layerSource(l)):
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
				tRC = cfg.utls.createTempRasterPath('tif')
				# cross classification
				eMN = dT + cfg.crossClassNm
				cfg.reportPth = str(cfg.tmpDir + '/' + eMN)
				tblOut = cfg.osSCP.path.dirname(crossRstPath) + '/' + cfg.utls.fileNameNoExt(crossRstPath) + '.csv'
				cfg.uiUtls.updateBar(10)
				# if reference shapefile
				if l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
					if batch == 'No':
						fd = cfg.ui.class_field_comboBox_2.currentText()
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
				# No data value
				if NoDataValue is not None:
					nD = NoDataValue
				elif cfg.ui.nodata_checkBox_6.isChecked() is True:
					nD = cfg.ui.nodata_spinBox_7.value()
				else:
					nD = None
				# create virtual raster
				qlllllllI = cfg.utls.layerSource(iClass)
				bList = [referenceRaster, qlllllllI]
				bListNum = [1, 1]
				vrtCheck = cfg.utls.createTempVirtualRaster(bList, bListNum, 'Yes', 'Yes', 0, 'No', 'Yes')
				bandsUniqueVal = []
				for b in bList:
					cfg.parallelArrayDict = {}
					o = cfg.utls.multiProcessRaster(rasterPath = b, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = nD, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'))
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
								# enable map canvas render
								cfg.cnvs.setRenderFlag(True)
								cfg.uiUtls.removeProgressBar()			
							# logger
							cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR values')
							cfg.mx.msgErr9()		
							return 'No'
					rasterBandUniqueVal = cfg.np.unique(values).tolist()
					refRasterBandUniqueVal = sorted(rasterBandUniqueVal)
					try:
						refRasterBandUniqueVal.remove(nD)
					except:
						pass
					bandsUniqueVal.append(refRasterBandUniqueVal)
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
						if nD not in i:
							newVl = cfg.np.multiply(rndVarList, i).sum()
							newValueList.append(newVl)
							reclassList.append([newVl, n])
							cmbntns[n] = [i[1], i[0]]
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
				# check projections
				left, right, top, bottom, cRPX, cRPY, rP, un = cfg.utls.imageGeoTransform(vrtCheck)					
				# calculation
				o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.crossRasters, outputRasterList = [crossRstPath], nodataValue = nD,  functionBandArgument = reclassList, functionVariable = e, progressMessage = 'cross classification ', outputNoDataValue = 0,  virtualRaster = vrtR, compress = cfg.rasterCompression, dataType = 'UInt16')
				cfg.uiUtls.updateBar(60)
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = crossRstPath, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = 0, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'))
				if o == 'No':
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr45()
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error')
					return 'No'
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'cross raster output: ' + str(crossRstPath))
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
				reclRasterBandUniqueVal = {}
				values = values.astype(int)
				for v in range(0, len(values)):
					try:
						reclRasterBandUniqueVal[values[v]] = reclRasterBandUniqueVal[values[v]] + sumVal[v]
					except:
						reclRasterBandUniqueVal[values[v]] = sumVal[v]
				rasterBandUniqueVal = {}
				for v in range(0, len(values)):
					cmbX = cmbntns[values[v]]
					rasterBandUniqueVal[(cmbX[0], cmbX[1])] = [reclRasterBandUniqueVal[values[v]], values[v]]
				cfg.uiUtls.updateBar(80)
				col2 = list(set(col))
				row2 = list(set(row))
				cols = sorted(cfg.np.unique(col2).tolist())
				rows = sorted(cfg.np.unique(row2).tolist())
				crossClass = cfg.np.zeros((len(rows), len(cols)))
				cList = 'V_' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reference') + '\t'
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
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'CrossClassCode') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Classification') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reference') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'PixelSum') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Area [' + un + '^2]') + str('\n')
				l.write(t)
				for c in cols:
					cList = cList + str(c) + '\t'
					for r in rows:
						try:
							v = (c, r)
							area = str(rasterBandUniqueVal[v][0] * cRPX * cRPY)
							t = str(rasterBandUniqueVal[v][1]) + '\t' + str(c) + '\t' + str(r) + '\t' + str(rasterBandUniqueVal[v][0]) + '\t' + area + str('\n')
							l.write(t)
							crossClass[rows.index(r), cols.index(c)] = rasterBandUniqueVal[v][0] * cRPX * cRPY
						except:
							crossClass[rows.index(r), cols.index(c)] = 0
				# save combination to table
				l.write(str('\n'))
				tStr = '\t' + '> ' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'CROSS MATRIX [') + str(un) + '^2]' + '\n'
				l.write(tStr)
				tStr = '\t' + '> ' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Classification') + '\n'
				l.write(tStr)
				tStr = cList + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Total') + '\n'
				l.write(tStr)
				# temp matrix
				tmpMtrx= cfg.tmpDir + '/' + cfg.tempMtrxNm + dT + '.txt'
				cfg.np.savetxt(tmpMtrx, crossClass, delimiter='\t', fmt='%i')
				tM = open(tmpMtrx, 'r')
				# write matrix
				ix = 0
				for j in tM:
					tMR = str(rows[ix]) + '\t' + j.rstrip('\n') + '\t' + str(int(crossClass[ix, :].sum())) + str('\n')
					l.write(tMR)
					ix = ix + 1
				# last line
				lL = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Total')
				for c in range(0, len(cols)):
					lL = lL + '\t' + str(int(crossClass[:, c].sum()))
				totMat = int(crossClass.sum())
				lL = lL + '\t' + str(totMat) + str('\n')
				l.write(lL)
				l.close()
				# add raster to layers
				rastUniqueVal = cfg.np.unique(values).tolist()
				rstr = cfg.utls.addRasterLayer(crossRstPath)
				cfg.utls.rasterSymbolGeneric(rstr, 'NoData', rasterUniqueValueList = rastUniqueVal)	
				try:
					f = open(tblOut)
					if cfg.osSCP.path.isfile(tblOut):
						eM = f.read()
						cfg.ui.cross_matrix_textBrowser.setText(eM)
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' cross matrix calculated')
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				cfg.uiUtls.updateBar(100)
				if batch == 'No':
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.ui.toolBox_cross_classification.setCurrentIndex(1)
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
		cfg.referenceLayer2 = cfg.ui.reference_name_combo_2.currentText()
		cfg.ui.class_field_comboBox_2.clear()
		l = cfg.utls.selectLayerbyName(cfg.referenceLayer2)
		try:
			if l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
				f = l.dataProvider().fields()
				for i in f:
					if str(i.typeName()).lower() != 'string':
						cfg.dlg.class_field_combo_2(str(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'reference layer name: ' + str(cfg.referenceLayer2))
	
	# refresh reference layer name
	def refreshReferenceLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.reference_name_combo_2.clear()
		# reference layer name
		cfg.referenceLayer2 = None
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer):
				if (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.Polygon) or (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.MultiPolygon):
					cfg.dlg.reference_layer_combo_2(l.name())
			elif (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.reference_layer_combo_2(l.name())
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'reference layers refreshed')
