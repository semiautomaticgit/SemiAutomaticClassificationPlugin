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

class BandCombination:

	def __init__(self):
		self.clssfctnNm = None
		
	# calculate band set combination if click on button
	def calculateBandSetCombination(self):
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' calculate band combination ')
		self.bandSetCombination()
	
	# cross classification calculation
	def bandSetCombination(self, batch = 'No', bandSetNumber = None, rasterOutput = None):
		if batch == 'No':
			combRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save band combination raster output'), '', 'TIF file (*.tif);;VRT file (*.vrt)')
		else:
			combRstPath = rasterOutput
		# virtual raster
		vrtR = 'No'
		if combRstPath is not False:
			if combRstPath.lower().endswith('.vrt'):
				vrtR = 'Yes'
			elif combRstPath.lower().endswith('.tif'):
				pass
			else:
				combRstPath = combRstPath + '.tif'
			if bandSetNumber is None:
				bandSet = cfg.ui.band_set_comb_spinBox.value()
				bandSetNumber = bandSet - 1
			if batch == 'No':
				cfg.uiUtls.addProgressBar()
			# create list of rasters
			try:
				cfg.bandSetsList[bandSetNumber][0]
			except:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar28()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
				return 'No'
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				ckB = cfg.utls.checkBandSet(bandSetNumber)
			else:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar29()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
				return 'No'
			if ckB != 'Yes':
				pass
			if len(cfg.bndSetLst) <= 1:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar28()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
				return 'No'
			# name of combination field in output table
			combName = ''
			for rbName in cfg.bandSetsList[bandSetNumber][3]:
				combName = combName + rbName[0:16] + ','
			combName = combName.rstrip(',')
			cfg.uiUtls.updateBar(10)
			cfg.utls.makeDirectory(cfg.osSCP.path.dirname(combRstPath))
			NoDataVal = cfg.NoDataVal
			rCrs = cfg.utls.getCrsGDAL(cfg.bndSetLst[0])
			rEPSG = cfg.osrSCP.SpatialReference()
			rEPSG.ImportFromWkt(rCrs)
			if rEPSG is None:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar28()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
				return 'No'
			cfg.uiUtls.updateBar(20)
			bListNum = []
			nData = []
			for b in range(0, len(cfg.bndSetLst)):
				nD = cfg.utls.imageNoDataValue(cfg.bndSetLst[b])
				nData.append(nD)
				bListNum.append(1)
				eCrs = cfg.utls.getCrsGDAL(cfg.bndSetLst[b])
				EPSG = cfg.osrSCP.SpatialReference()
				EPSG.ImportFromWkt(eCrs)
				if EPSG.IsSame(rEPSG) != 1:
					if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
						tPMD = cfg.utls.createTempRasterPath('vrt')
						cfg.utls.createWarpedVrt(cfg.bndSetLst[b], tPMD, str(rCrs))
						cfg.mx.msg9()
						if cfg.osSCP.path.isfile(tPMD):
							cfg.bndSetLst[b] = tPMD
						else:
							if batch == 'No':
								cfg.uiUtls.removeProgressBar()
							cfg.mx.msgErr60()
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
							return 'No'
			cfg.uiUtls.updateBar(40)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' nData: ' + str(nData))
			# No data value
			nD = NoDataVal
			vrtCheck = cfg.utls.createTempVirtualRaster(cfg.bndSetLst, bListNum, 'Yes', 'Yes', 0, 'No', 'Yes')
			calcDataType = cfg.np.int32
			calcNodata = cfg.NoDataValInt32
			cfg.parallelArrayDict = {}
			o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValues, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values '), calcDataType = calcDataType)
			# calculate unique values
			values = cfg.np.array([])
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						try:
							values = cfg.np.vstack((values, ar[0]))
						except:
							values = ar[0]
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
			# adapted from Jaime answer at https://stackoverflow.com/questions/16970982/find-unique-rows-in-numpy-array
			bVV = values.view(cfg.np.dtype((cfg.np.void, values.dtype.itemsize * values.shape[1])))
			ff, indexA = cfg.np.unique(bVV, return_index=True, return_counts=False)
			cmb = []
			for cmV in values[indexA].tolist():
				useV = 'Yes'
				for rnData in nData:
					if int(rnData) in cmV:
						useV = 'No'
						break
				if useV == 'Yes':
					cmb.append(cmV)
			cmbArr = cfg.np.array(cmb)
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' len(cmb): ' + str(len(cmb)))
			maxV = cfg.np.nanmax(cmbArr, axis=0)
			if cfg.np.sum(cmbArr<=0) < 1:
				calcDataType = cfg.np.uint32
				calcNodata = cfg.NoDataValUInt32
				addC = 0
			else:
				addC = - cfg.np.nanmin(cmbArr)
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' addC: ' + str(addC))
			# expression builder
			check = 'No'
			maxDig = 10-len(str(cfg.np.sum(maxV)))
			if maxDig < 0:
				maxDig = 2
			t = 0
			while t < 5000:
				t = t + 1
				rndVarList = []
				sumA = cfg.np.zeros(cmbArr.shape, dtype=calcDataType)
				for cmbI in range(0, len(cmb[0])):
					if t < 1000:
						expR = int(cfg.np.random.random()*10)+1
						if expR > maxDig:
							expR = maxDig
						constV = int(10**(expR))
					elif t < 2000:
						constV = int(10**(maxDig-cmbI))
					elif t < 3000:
						constV = int(10**(maxDig-(len(cmb[0])-cmbI)))
					elif t < 4000:
						constV = int(10**(maxDig))
					else:
						expR = int(cfg.np.random.random()*10)+1
						if expR > 8:
							expR = 8
						constV = int(10**(expR))
					if constV < 1:
						constV = 3
					rndVar = int(constV * cfg.np.random.random())
					if rndVar == 0:
						rndVar = 1
					rndVarList.append(rndVar)
					sumA[:, cmbI] = (cmbArr[:, cmbI] + addC) * rndVar
				sumT = cfg.np.sum(sumA, axis=1)
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' (sumT) ' + str(sumT))
				uniqueS = cfg.np.unique(sumT, return_index=False, return_counts=False)
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rndVarList: ' + str(rndVarList) + ' uniqueS.shape[0] ' + str(uniqueS.shape[0]))
				if uniqueS.shape[0] == len(cmb) and cfg.np.sum(uniqueS<0) < 1:
					check = 'Yes'
					break
			if check == 'No':
				if batch == 'No':
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr63()
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR combinations')
				return 'No'
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rndVarList: ' + str(rndVarList))
			reclassDict = {}
			for i in cmb:
				newVl = 0
				for rE in range(0, len(rndVarList)):
					if nData[rE] in i:
						newVl = 0
						break
					else:
						newVl = newVl + (i[rE] + 1) * (rndVarList[rE])
				if newVl > 0:
					reclassDict[newVl] = i
			n = 1
			reclassList = []
			cmbntns = {}	
			for newVl in sorted(reclassDict.keys()):
				reclassList.append(newVl)
				cmbntns[n] = reclassDict[newVl]
				n = n + 1
			e = ''
			for rE in range(0, len(rndVarList)):
				e = e + '(rasterSCPArrayfunctionBand[::, ::, ' + str(rE) + '] + 1) * ' + str(rndVarList[rE]) + ' + '
			e = e.rstrip(' + ')
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' e: ' + str(e))
			# check projections
			left, right, top, bottom, cRPX, cRPY, rP, un = cfg.utls.imageGeoTransform(vrtCheck)
			# calculation
			cfg.parallelArrayDict = {}
			o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.crossRasters, outputRasterList = [combRstPath], functionBandArgument = reclassList, functionVariable = e, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Cross classification '),  nodataValue = cfg.NoDataValInt32, outputNoDataValue = cfg.NoDataValInt32, virtualRaster = vrtR, compress = cfg.rasterCompression, dataType = 'UInt32', calcDataType = calcDataType)
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
			values = values.astype(int)
			rasterBandUniqueVal = {}
			for v in range(0, len(values)):
				try:
					cmbX = cmbntns[values[v]]
					try:
						rasterBandUniqueVal[tuple(cmbX)] = rasterBandUniqueVal[tuple(cmbX)] + sumVal[v]
					except:
						rasterBandUniqueVal[tuple(cmbX)] = sumVal[v]
				except:
					pass
			refRasterBandUniqueVal = list(set(values))
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'cross raster output: ' + str(combRstPath))
			cfg.uiUtls.updateBar(80)
			# table output
			tblOut = cfg.osSCP.path.dirname(combRstPath) + '/' + cfg.utls.fileNameNoExt(combRstPath) + '.csv'
			try:
				l = open(tblOut, 'w')
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
			t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'RasterValue') + '\t' + combName + '\t' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'PixelSum') + '\t' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Area [' + un + '^2]') + str('\n')
			l.write(t)
			for c in refRasterBandUniqueVal:
				try:
					v = tuple(cmbntns[c])
					if rasterBandUniqueVal[v] > 0:
						area = str(rasterBandUniqueVal[v] * cRPX * cRPY)
						cList = str(c) + '\t' + ','.join([str(l) for l in cmbntns[c]]) + '\t' + str(rasterBandUniqueVal[v]).replace('.0', '') + '\t' + area + str('\n')
						l.write(cList)
				except Exception as err:
					pass
			l.close()	
			# add raster to layers
			rastUniqueVal = cfg.np.unique(values).tolist()
			rstr =cfg.utls.addRasterLayer(combRstPath)
			cfg.utls.rasterSymbolGeneric(rstr, 'NoData', rasterUniqueValueList = rastUniqueVal)	
			try:
				f = open(tblOut)
				if cfg.osSCP.path.isfile(tblOut):
					eM = f.read()
					cfg.ui.band_set_comb_textBrowser.setText(eM)
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
				cfg.ui.toolBox_band_set_combination.setCurrentIndex(1)
				cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'finished')
	