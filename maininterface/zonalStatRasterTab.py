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

class ZonalStatRasterTab:

	def __init__(self):
		pass
	
	# calculate zonal stat action
	def zonalStatRasterAction(self):
		self.zonalStatRaster()

	# calculate zonal stat raster
	def zonalStatRaster(self, batch = 'No', inputRaster = None, reference = None, shapefileField = None, rasterOutput = None,  statName = None, statPerc = None,  NoDataValue = None):
		if inputRaster is None:
			inputRasterNm = cfg.ui.classification_name_combo_5.currentText()
			iClass = cfg.utls.selectLayerbyName(inputRasterNm, 'Yes')
			if iClass is None:
				cfg.mx.msgErr38(inputRasterNm)
				return 'No'
			inputRaster = cfg.utls.layerSource(iClass)
		else:
			iClass = cfg.utls.addRasterLayer(inputRaster)
		if reference is None:
			referenceNm = cfg.ui.reference_name_combo_3.currentText()
			l = cfg.utls.selectLayerbyName(referenceNm)
			reference = cfg.utls.selectLayerbyName(referenceNm, 'Yes')
		else:
			try:
				# open input with GDAL
				rD = cfg.gdalSCP.Open(reference, cfg.gdalSCP.GA_ReadOnly)
				if rD is None:
					l = cfg.utls.addVectorLayer(reference, cfg.utls.fileName(reference), "ogr")
				else:
					l = cfg.utls.addRasterLayer(reference)
				reml = l
				rD = None
			except:
				cfg.mx.msgErr38(reference)
				return 'No'
		# statistic name
		if statName is None:
			statName =  cfg.ui.statistic_name_combobox.currentText()
		for i in cfg.statisticList:
			if i[0].lower() == statName.lower():
				statNp = i[1]
				if i[0].lower() == 'percentile':
					if statPerc is None:
						statPerc = cfg.ui.statistic_lineEdit.text()
					try:
						statPerc = int(statPerc)
						break
					except:
						cfg.mx.msgErr66()
						return 'No'
				else:
					break
		if batch == 'No':
			zonalRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save zonal stat raster output'), '', '*.tif', 'tif')
		else:
			zonalRstPath = rasterOutput
		if zonalRstPath is not False:
			if zonalRstPath.lower().endswith('.tif'):
				pass
			else:
				zonalRstPath = zonalRstPath + '.tif'
			if iClass is not None and l is not None:
				if batch == 'No':
					cfg.uiUtls.addProgressBar()
				# if not reference shapefile
				if l.type() != cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
					# check projections
					newRstrProj = cfg.utls.getCrs(iClass)
					refRstrProj = cfg.utls.getCrs(l)
					if refRstrProj != newRstrProj:
						cfg.mx.msg9()
						return 'No'
				else:
					# vector EPSG
					if 'Polygon?crs=' in str(cfg.utls.layerSource(l))  or 'memory?geometry=' in str(cfg.utls.layerSource(l)):
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
					dT = cfg.utls.getTime()
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
								except:
									pass
								# logger
								cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
								cfg.mx.msgErr9()
								return 'No'
						l = cfg.utls.addVectorLayer(reprjShapefile, cfg.utls.fileName(reprjShapefile) , 'ogr')
				if batch == 'No':
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
					cfg.QtWidgetsSCP.qApp.processEvents()
				# temp raster layer
				tRC = cfg.utls.createTempRasterPath('tif')
				cfg.uiUtls.updateBar(10)
				# if reference shapefile
				if l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
					if batch == 'No':
						fd = cfg.ui.class_field_comboBox_4.currentText()
					else:
						fd = shapefileField
					if batch == 'No':
						# convert reference layer to raster
						qlllll = cfg.utls.layerSource(l)
						qllllll = cfg.utls.layerSource(iClass)
						vect = cfg.utls.vectorToRaster(fd, str(qlllll), inputRaster, str(tRC), str(qllllll), extent = 'Yes')
					else:
						qlllllll = cfg.utls.layerSource(l)
						vect = cfg.utls.vectorToRaster(fd, str(qlllllll), inputRaster, str(tRC), inputRaster, extent = 'Yes')
					if vect == 'No':
						if batch == 'No':
							cfg.utls.finishSound()
							cfg.utls.sendSMTPMessage(None, str(__name__))
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()						
						# logger
						cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR vector')
						cfg.mx.msgErr9()		
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
				elif cfg.ui.nodata_checkBox_10.isChecked() is True:
					nD = cfg.ui.nodata_spinBox_12.value()
				else:
					nD = cfg.utls.imageNoDataValue(referenceRaster)
				if nD is None:
					nD = cfg.NoDataVal
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = referenceRaster, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = nD, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'), deleteArray = 'No')
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
				classes = sorted(rasterBandUniqueVal)
				# get integer values
				intClass = []
				for c in classes:
					try:
						if int(c) == c:
							intClass.append(int(c))
						else:
							intClass.append(c)
					except:
						intClass.append(c)
				classes = intClass
				cfg.uiUtls.updateBar(30)
				# create functions
				bList = [referenceRaster, inputRaster]
				bListNum = [1, 1]
				functionList = []
				variableList = []
				bandNumberList = []
				for c in classes:
					if c != nD:
						for b in range(1, len(bList)):
							e = 'cfg.np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(b) + '], cfg.np.nan)'
							ee = statNp.replace('array', e)
							try:
								statPerc = int(statPerc)
								ee = ee.replace(cfg.statPerc, str(statPerc))
							except:
								pass
							functionList.append(ee)
							variableList.append('rasterSCPArrayfunctionBand')
							bandNumberList.append([0, b])
				# create virtual raster
				vrtCheck = cfg.utls.createTempVirtualRaster(bList, bListNum, 'Yes', 'Yes', 0, 'No', 'Yes')
				# calculation statistic
				o = cfg.utls.multiProcessNoBlocks(rasterPath = vrtCheck, bandNumberList = bandNumberList, functionRaster = cfg.utls.noBlocksCalculation, nodataValue = nD, functionBandArgument = functionList, functionVariable = variableList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Raster statistics'))
				cfg.uiUtls.updateBar(60)
				# write report
				colStat = statName
				if statPerc is not None:
					colStat = statName + statPerc
				l = open(zonalRstPath[:-4] + '_report.csv', 'w')
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Class') + '	' + colStat + str('\n')
				l.write(t)
				# get values
				for c in classes:
					if c != nD:
						for b in range(1, len(bList)):
							e = 'cfg.np.where(rasterSCPArrayfunctionBand[::, ::, ' + str(0) + '] == ' + str(c) + ', rasterSCPArrayfunctionBand[::, ::, ' + str(b) + '], cfg.np.nan)'
							ee = statNp.replace('array', e)
							try:
								statPerc = int(statPerc)
								ee = ee.replace(cfg.statPerc, str(statPerc))
							except:
								pass
							try:
								if o[ee] is None:
									value = cfg.NoDataVal
								else:
									value = float(o[ee])
							except Exception as err:
								# logger
								cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
								if batch == 'No':
									cfg.utls.finishSound()
									cfg.utls.sendSMTPMessage(None, str(__name__))
									# enable map canvas render
									cfg.cnvs.setRenderFlag(True)
									cfg.uiUtls.removeProgressBar()			
								return 'No'
							# output rasters
							outRaster = zonalRstPath[:-4] + str(c) + '.tif'
							oM = []
							oM.append(outRaster)
							try:
								rDD = cfg.gdalSCP.Open(vrtCheck, cfg.gdalSCP.GA_ReadOnly)
								oMR = cfg.utls.createRasterFromReference(rDD, 1, oM, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0, None, cfg.rasterCompression, 'LZW', constantValue = value)
							except Exception as err:
								# logger
								cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								if batch == 'No':
									cfg.utls.finishSound()
									cfg.utls.sendSMTPMessage(None, str(__name__))
									# enable map canvas render
									cfg.cnvs.setRenderFlag(True)
									cfg.uiUtls.removeProgressBar()			
								return 'No'
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							# add raster to layers
							rstr = cfg.utls.addRasterLayer(outRaster)
							t = str(c) + '	' + str(value) + str('\n')
							l.write(t)
				l.close()
				rDD = None
				# remove temp
				try:
					cfg.osSCP.remove(tRC)
				except:
					pass
				cfg.uiUtls.updateBar(100)
				if batch == 'No':
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.uiUtls.removeProgressBar()
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " zonal stat calculated")	
				
	# classification name
	def classificationLayerName(self):
		self.clssfctnNm = cfg.ui.classification_name_combo_5.currentText()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification name: " + str(self.clssfctnNm))
	
	# reference layer name
	def referenceLayerName(self):
		cfg.referenceLayer3 = cfg.ui.reference_name_combo_3.currentText()
		cfg.ui.class_field_comboBox_4.clear()
		l = cfg.utls.selectLayerbyName(cfg.referenceLayer3)
		try:
			if l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
				f = l.dataProvider().fields()
				for i in f:
					if str(i.typeName()).lower() != 'string':
						cfg.dlg.class_field_combo_4(str(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layer name: " + str(cfg.referenceLayer3))
				
	# refresh reference layer name
	def refreshReferenceLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.reference_name_combo_3.clear()
		# reference layer name
		cfg.referenceLayer3 = None
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer):
				if (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.Polygon) or (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.MultiPolygon):
					cfg.dlg.reference_layer_combo_3(l.name())
			elif (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.reference_layer_combo_3(l.name())
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layers refreshed")
		
	# stat combo
	def loadStatisticCombo(self):
		cfg.ui.statistic_name_combobox.blockSignals(True)
		cfg.ui.statistic_name_combobox.clear()
		for i in cfg.statisticList:
			cfg.dlg.statistic_name_combo(i[0])
		cfg.ui.statistic_name_combobox.blockSignals(False)
			