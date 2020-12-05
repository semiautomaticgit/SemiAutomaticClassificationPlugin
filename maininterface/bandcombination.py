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
	def bandSetCombination(self, batch = 'No', bandSet = None, rasterOutput = None):
		if batch == 'No':
			combRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save band combination raster output'), '', '*.tif', 'tif')
		else:
			combRstPath = rasterOutput
		if combRstPath is not False:
			if combRstPath.lower().endswith('.tif'):
				pass
			else:
				combRstPath = combRstPath + '.tif'
			if bandSet is None:
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
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
				return 'No'
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				ckB = cfg.utls.checkBandSet(bandSetNumber)
			else:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar29()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
				return 'No'
			if ckB != 'Yes':
				pass
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
			NoDataVal = cfg.NoDataVal				
			for b in range(0, len(cfg.bndSetLst)):						
				EPSG = cfg.utls.getEPSGRaster(cfg.bndSetLst[b])
				if str(EPSG) != str(rEPSG):
					if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
						nD = cfg.utls.imageNoDataValue(cfg.bndSetLst[b])
						if nD is None:
							nD = NoDataVal
						tPMD = cfg.utls.createTempRasterPath('tif')
						cfg.utls.GDALReprojectRaster(cfg.bndSetLst[b], tPMD, "GTiff", None, "EPSG:" + str(rEPSG), "-ot Float32 -dstnodata " + str(nD))
						if cfg.osSCP.path.isfile(tPMD):
							cfg.bndSetLst[b] = tPMD
						else:
							if batch == 'No':
								cfg.uiUtls.removeProgressBar()
							cfg.mx.msgErr60()
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
							return 'No'
			cfg.uiUtls.updateBar(40)
			bandsUniqueVal = []
			bList = []
			bandNumberList = []
			for b in range(0, len(cfg.bndSetLst)):
				bList.append(cfg.bndSetLst[b])
				bandNumberList.append(1)
			# create virtual raster					
			vrtCheck = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'Yes')
			# No data value
			nD = cfg.utls.imageNoDataValue(cfg.bndSetLst[0])
			if nD is None:
				nD = NoDataVal
			cfg.parallelArrayDict = {}
			o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValues, nodataValue = nD, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'), deleteArray = 'No')
			# calculate unique values
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						try:
							if ar is not None:
								values = cfg.np.append(values, ar, axis = 0)
						except:
							values = ar
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
				cmb = cfg.np.unique(values, axis = 0).tolist()
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
			# expression builder
			t = 0
			while t < 100:
				t = t + 1
				rndVarList = []
				for cmbI in range(0, len(cmb[0])):
					rndVarList.append(int(999 * cfg.np.random.random()))
				n = 1
				cmbntns = {}
				newValueList = []
				reclassList = []
				for i in cmb:
					if nD not in i:
						newVl = cfg.np.multiply(rndVarList, i).sum()
						newValueList.append(newVl)
						reclassList.append([newVl, n])
						cmbntns[n] = i
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
			o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.crossRasters, outputRasterList = [combRstPath], nodataValue = nD, functionBandArgument = reclassList, functionVariable = e, progressMessage = 'band combination ', dataType = 'UInt16', outputNoDataValue = 0, compress = cfg.rasterCompression, compressFormat = 'DEFLATE -co PREDICTOR=2 -co ZLEVEL=1')
			cfg.uiUtls.updateBar(60)
			cfg.parallelArrayDict = {}
			o = cfg.utls.multiProcessRaster(rasterPath = combRstPath, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = nD, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'), deleteArray = 'No')
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
				rasterBandUniqueVal[tuple(cmbX)] = [reclRasterBandUniqueVal[values[v]], values[v]]
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
			t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'RasterValue') + '\t' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Combination') + '\t' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'PixelSum') + '\t' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Area [' + un + '^2]') + str('\n')
			l.write(t)
			for c in cmbntns:
				try:
					v = tuple(cmbntns[c])
					if rasterBandUniqueVal[v][0] > 0:
						area = str(rasterBandUniqueVal[v][0] * cRPX * cRPY)
						cList = str(c) + '\t' + ','.join([str(l).replace('.0', '') for l in cmbntns[c]]) + '\t' + str(rasterBandUniqueVal[v][0]) + '\t' + area + str('\n')
						l.write(cList)
				except:
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
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " cross matrix calculated")
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.updateBar(100)
			if batch == 'No':
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.utls.finishSound()
				cfg.utls.sendSMTPMessage(None, str(__name__))
				cfg.ui.toolBox_band_set_combination.setCurrentIndex(1)
				cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "finished")
	