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

class LandCoverChange:

	def __init__(self):
		pass
	
	# reference classification name
	def classificationReferenceLayerName(self):
		cfg.refClssfctnNm = cfg.ui.classification_reference_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "reference classification name: " + str(cfg.refClssfctnNm))
					
	# start land cover change calculation
	def landCoverChangeAction(self):			
		self.landCoverChange()
		
	# start land cover change calculation
	def landCoverChange(self, batch = 'No', referenceRaster = None, newRaster = None, rasterOutput = None):
		if batch == 'No':
			# input
			refRstr = cfg.utls.selectLayerbyName(cfg.refClssfctnNm, 'Yes')
			try:
				refRstrSrc = cfg.utls.layerSource(refRstr)
				rstrCheck = 'Yes'
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				rstrCheck = 'No'
			newRstr = cfg.utls.selectLayerbyName(cfg.newClssfctnNm, 'Yes')
			try:
				newRstrSrc = cfg.utls.layerSource(newRstr)
				rstrCheck = 'Yes'
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				rstrCheck = 'No'
		else:
			refRstrSrc = referenceRaster
			newRstrSrc = newRaster
			if cfg.osSCP.path.isfile(refRstrSrc) and cfg.osSCP.path.isfile(newRstrSrc):
				rstrCheck = 'Yes'
			else:
				rstrCheck = 'No'
		# check if numpy is updated
		try:
			cfg.np.count_nonzero([1,1,0])
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr26()
			return 'No'
		if rstrCheck == 'No':
			cfg.mx.msg4()
		else:
			if batch == 'No':
				chngRstPath = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save land cover change raster output'), '', 'TIF file (*.tif);;VRT file (*.vrt)')
			else:
				chngRstPath = rasterOutput
			# virtual raster
			vrtR = 'No'
			if chngRstPath is not False:
				# check projections
				rCrs = cfg.utls.getCrsGDAL(refRstrSrc)
				rEPSG = cfg.osrSCP.SpatialReference()
				rEPSG.ImportFromWkt(rCrs)
				eCrs = cfg.utls.getCrsGDAL(newRstrSrc)
				EPSG = cfg.osrSCP.SpatialReference()
				EPSG.ImportFromWkt(eCrs)
				if EPSG.IsSame(rEPSG) != 1:
					tPMD = cfg.utls.createTempRasterPath('vrt')
					cfg.utls.createWarpedVrt(newRstrSrc, tPMD, str(rCrs))
					cfg.mx.msg9()
					newRstrSrc = tPMD
				cfg.utls.makeDirectory(cfg.osSCP.path.dirname(chngRstPath))
				if chngRstPath.lower().endswith('.vrt'):
					vrtR = 'Yes'
				elif chngRstPath.lower().endswith('.tif'):
					pass
				else:
					chngRstPath = chngRstPath + '.tif'
				if batch == 'No':
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
				tblOut = cfg.osSCP.path.dirname(chngRstPath) + '/' + cfg.utls.fileNameNoExt(chngRstPath) + '.csv'
				# combination finder
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = refRstrSrc, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'))
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
				o = cfg.utls.multiProcessRaster(rasterPath = newRstrSrc, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'))
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
				for x in sorted(cfg.parallelArrayDict):
					try:
						for ar in cfg.parallelArrayDict[x]:
							valuesB = cfg.np.append(valuesB, ar[0, ::])
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
				try:
					cmbB = cfg.np.unique(valuesB, axis = 0).tolist()
					newRasterBandUniqueVal = sorted(cmbB)	
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
				bandsUniqueVal = [refRasterBandUniqueVal, newRasterBandUniqueVal]
				if 0 in refRasterBandUniqueVal:
					k0 = 1
				else:
					k0 = 0
				if 0 in newRasterBandUniqueVal:
					k1 = 1
				else:
					k1 = 0
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
					calcDataType = cfg.np.uint32
					# first try fixed list
					if t == 1:
						coT = 333
						for cmbI in range(0, len(cmb[0])):
							rndVarList.append(coT)
							coT = coT + 1
					# random list
					else:
						for cmbI in range(0, len(cmb[0])):
							rndVarList.append(int(999 * cfg.np.random.random()))
					newValueList = []
					reclassDict = {}
					for i in cmb:
						newVl = (i[0] + k0) * (rndVarList[0]) + (i[1] + k1) * (rndVarList[1])
						reclassDict[newVl] = i
						newValueList.append(newVl)
						if i[0] < 0 or i[1] < 0 :
							calcDataType = cfg.np.int32
					uniqueValList = cfg.np.unique(newValueList)
					if int(uniqueValList.shape[0]) == len(newValueList):
						n = 1
						col = []
						row = []
						reclassList = []
						cmbntns = {}	
						for newVl in sorted(reclassDict.keys()):
							i = reclassDict[newVl]
							reclassList.append(newVl)
							cmbntns[n] = [i[1], i[0]]
							col.append(i[1])
							row.append(i[0])
							n = n + 1
						check = 'Yes'
						break
				if check == 'No':
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					return 'No'
				e = '(rasterSCPArrayfunctionBand[::, ::, 0] + ' + str(k0) +' ) * ' + str(rndVarList[0]) + ' + (rasterSCPArrayfunctionBand[::, ::, 1] + ' + str(k1) +' ) * ' + str(rndVarList[1])	
				# calculation
				bList = [refRstrSrc, newRstrSrc]
				bandNumberList = [1, 1]
				vrtCheck = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'No')
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.crossRasters, outputRasterList = [chngRstPath],  functionBandArgument = reclassList, functionVariable = e, progressMessage =cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Land cover change'), virtualRaster = vrtR, compress = cfg.rasterCompression, outputNoDataValue = cfg.NoDataValUInt32, dataType = 'UInt32', calcDataType = calcDataType)
				# check projections
				left, right, top, bottom, cRPX, cRPY, rP, un = cfg.utls.imageGeoTransform(chngRstPath)			
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
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'land cover change raster output: ' + str(chngRstPath))
				# calculate unique values
				values = cfg.np.array([])
				sumVal = cfg.np.array([])
				for x in sorted(cfg.parallelArrayDict):
					try:
						for ar in cfg.parallelArrayDict[x]:
							values = cfg.np.append(values, ar[1][0, ::])
							sumVal = cfg.np.append(sumVal, ar[1][1, ::])
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
					try:
						cmbX = cmbntns[values[v]]
						rasterBandUniqueVal[(cmbX[0], cmbX[1])] = [reclRasterBandUniqueVal[values[v]], values[v]]
					except:
						pass
				cfg.uiUtls.updateBar(80)
				col2 = list(set(col))
				row2 = list(set(row))
				cols = sorted(cfg.np.unique(col2).tolist())
				rows = sorted(cfg.np.unique(row2).tolist())
				crossClass = cfg.np.zeros((len(rows), len(cols)))
				cList = 'V_' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'ReferenceClass') + '\t'
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
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'CrossClassCode') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'NewClass') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'ReferenceClass') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'PixelSum') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Area [' + un + '^2]') + str('\n')
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
				tStr = '\t' + '> ' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'LAND COVER CHANGE MATRIX [') + str(un) + '^2]' + '\n'
				l.write(tStr)
				tStr = '\t' + '> ' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'NewClass') + '\n'
				l.write(tStr)
				tStr = cList + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Total') + '\n'
				l.write(tStr)		
				# date time for temp name
				dT = cfg.utls.getTime()
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
				# open csv
				try:
					f = open(tblOut)
					if cfg.osSCP.path.isfile(tblOut):
						changeTxt = f.read()
						cfg.ui.change_textBrowser.setText(str(changeTxt))
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				# add raster to layers
				rstr = cfg.utls.addRasterLayer(chngRstPath)
				cfg.utls.rasterSymbolGeneric(rstr, rasterUniqueValueList = sorted(reclRasterBandUniqueVal.keys()))
				cfg.uiUtls.updateBar(100)
				if batch == 'No':
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.ui.toolBox_landCoverChange.setCurrentIndex(1)
					cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'finished')
						
	# state of checkbox for mask unchanged
	def maskUnchangedCheckbox(self):
		if cfg.ui.mask_unchanged_checkBox.isChecked() is True:
			cfg.unchngMaskCheck = True
		else:
			cfg.unchngMaskCheck = False
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.unchngMaskCheck))
	
	# new classification name
	def newClassificationLayerName(self):
		cfg.newClssfctnNm = cfg.ui.new_classification_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "reference classification name: " + str(cfg.newClssfctnNm))
	
	# refresh reference classification name
	def refreshClassificationReferenceLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.classification_reference_name_combo.clear()
		# reference classification name
		cfg.refClssfctnNm = None
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.classification_reference_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "reference classification layers refreshed")
	
	# refresh new classification name
	def refreshNewClassificationLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.new_classification_name_combo.clear()
		# new classification name
		cfg.newClssfctnNm = None
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.new_classification_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "new classification layers refreshed")