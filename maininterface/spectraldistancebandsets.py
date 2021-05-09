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

class SpectralDistanceBandsets:

	def __init__(self):
		pass
		
	# calculate distance band sets
	def calculateDistanceAction(self):
		self.spectralDistBandSets()
		
	# miniumum distance radioButton button changed
	def radioMinDistChanged(self):
		cfg.ui.min_distance_radioButton_2.blockSignals(True)
		cfg.ui.spectral_angle_map_radioButton_2.blockSignals(True)
		cfg.ui.min_distance_radioButton_2.setChecked(True)
		cfg.ui.spectral_angle_map_radioButton_2.setChecked(False)
		cfg.ui.min_distance_radioButton_2.blockSignals(False)
		cfg.ui.spectral_angle_map_radioButton_2.blockSignals(False)
		
	# SAM radioButton button changed
	def radioSAMChanged(self):
		cfg.ui.min_distance_radioButton_2.blockSignals(True)
		cfg.ui.spectral_angle_map_radioButton_2.blockSignals(True)
		cfg.ui.spectral_angle_map_radioButton_2.setChecked(True)
		cfg.ui.min_distance_radioButton_2.setChecked(False)
		cfg.ui.min_distance_radioButton_2.blockSignals(False)
		cfg.ui.spectral_angle_map_radioButton_2.blockSignals(False)
		thresh = cfg.ui.thresh_doubleSpinBox_2.value()
		if thresh > 90:
			cfg.mx.msg11()
			cfg.ui.thresh_doubleSpinBox_2.setValue(90)	
		
	# calculate distance band sets
	def spectralDistBandSets(self, firstBandSet = None, secondBandSet = None, outputRaster = None, batch = 'No'):
		if firstBandSet is None:
			bandSet = cfg.ui.band_set_comb_spinBox_6.value()
			firstBandSet = bandSet - 1
		if secondBandSet is None:
			bandSet = cfg.ui.band_set_comb_spinBox_7.value()
			secondBandSet = bandSet - 1
		bSL = []
		bSL.append(firstBandSet)
		bSL.append(secondBandSet)
		if batch == 'No':
			specRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save distance raster output'), '', 'TIF file (*.tif);;VRT file (*.vrt)')
		else:
			specRstPath = outputRaster
		# virtual raster
		vrtR = 'No'
		if specRstPath.lower().endswith('.vrt'):
			vrtR = 'Yes'
		if specRstPath is not False:
			o = cfg.osSCP.path.dirname(specRstPath)
			outputName = cfg.utls.fileNameNoExt(specRstPath)  + str(firstBandSet + 1)+ "_" + str(secondBandSet + 1)
			if batch == 'No':
				cfg.uiUtls.addProgressBar()
			bndSetSources = []
			bndSetIf = []
			# create list of rasters
			for bandSetNumber in bSL:
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
					bndSetIf.append('Yes')
				else:
					ckB = cfg.utls.checkImageBandSet(bandSetNumber)
					bndSetIf.append('No')
				if ckB == 'Yes':
					bndSetSources.append(cfg.bndSetLst)
				if len(bndSetSources) == 0:
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar28()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
					return 'No'
			cfg.uiUtls.updateBar(10)
			rCrs = cfg.utls.getCrsGDAL(bndSetSources[0][0])
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
			cfg.utls.makeDirectory(cfg.osSCP.path.dirname(specRstPath))
			# No data value
			NoDataVal = cfg.NoDataVal
			for bst in bndSetSources:
				if len(bst) != len(bndSetSources[0]):
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar28()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
					return 'No'
				bstIndex = bndSetSources.index(bst)
				for b in range(0, len(bst)):
					eCrs = cfg.utls.getCrsGDAL(bst[b])
					EPSG = cfg.osrSCP.SpatialReference()
					EPSG.ImportFromWkt(eCrs)
					if EPSG.IsSame(rEPSG) != 1:
						if cfg.bandSetsList[bstIndex][0] == 'Yes':
							nD = cfg.utls.imageNoDataValue(bst[b])
							if nD is None:
								nD = NoDataVal
							tPMD = cfg.utls.createTempRasterPath('vrt')
							cfg.utls.createWarpedVrt(bst[b], tPMD, str(rCrs))
							cfg.mx.msg9()
							#tPMD = cfg.utls.createTempRasterPath('tif')
							#cfg.utls.GDALReprojectRaster(bst[b], tPMD, "GTiff", None, "EPSG:" + str(rEPSG), "-ot Float32 -dstnodata " + str(nD))
							if cfg.osSCP.path.isfile(tPMD):
								bndSetSources[bstIndex][b] = tPMD
							else:
								if batch == 'No':
									cfg.uiUtls.removeProgressBar()
								cfg.mx.msgErr60()
								# logger
								cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
								return 'No'
						else:
							nD = cfg.utls.imageNoDataValue(bst[b])
							if nD is None:
								nD = NoDataVal
							tPMD = cfg.utls.createTempRasterPath('tif')
							cfg.utls.GDALReprojectRaster(bst[b], tPMD, "GTiff", None, rCrs, '-ot Float32 -dstnodata ' + str(nD))
							if cfg.osSCP.path.isfile(tPMD):
								for bb in range(0, len(bst)):
									bndSetSources[bstIndex][bb] = tPMD
								break
							else:
								if batch == 'No':
									cfg.uiUtls.removeProgressBar()
								cfg.mx.msgErr60()
								# logger
								cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
								return 'No'
			cfg.uiUtls.updateBar(40)
			bList = []
			bandNumberList = []
			for x in range(0, len(bndSetSources)):
				for y in range(0, len(bndSetSources[0])):						
					if bndSetIf[x] == 'Yes':
						bList.append(bndSetSources[x][y])
						bandNumberList.append(1)
					else:
						bList.append(bndSetSources[x][y])
						bandNumberList.append(y + 1)
			if cfg.ui.min_distance_radioButton_2.isChecked() is True:
				alg = cfg.algMinDist
			else:
				alg = cfg.algSAM
			if cfg.ui.distance_threshold_checkBox.isChecked() is True:
				thresh = cfg.ui.thresh_doubleSpinBox_2.value()
			else:
				thresh = 0
			if vrtR == 'Yes':
				rstrOut = o + '/' + outputName + '.vrt'
			else:
				rstrOut = o + '/' + outputName + '.tif'
			# create virtual raster
			vrtCheck = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'Yes')
			oo = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.spectralDistanceProcess, outputRasterList = [rstrOut], nodataValue = None,  functionBandArgument = NoDataVal, functionVariable = [alg], progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Spectral distance'), virtualRaster = vrtR, compress = cfg.rasterCompression, compressFormat = 'LZW')
			if cfg.osSCP.path.isfile(rstrOut):
				# add raster to layers
				cfg.utls.addRasterLayer(rstrOut)
				if cfg.ui.distance_threshold_checkBox.isChecked() is True:
					e = 'cfg.np.where("raster" > ' + str(thresh) + ', 1, 0 )'
					variableList = []
					variableList.append(['"raster"', '"raster"'])
					if vrtR == 'Yes':
						rstrOut2 = o + '/' + outputName + '_change' + '.vrt'
					else:
						rstrOut2 = o + '/' + outputName + '_change' + '.tif'
					oo2 = cfg.utls.multiProcessRaster(rasterPath = rstrOut, functionBand = 'No', functionRaster = cfg.utls.bandCalculation, outputRasterList = [rstrOut2], functionBandArgument = e, functionVariable = variableList, progressMessage = 'Threshold ', virtualRaster = vrtR, compress = cfg.rasterCompression, compressFormat = 'LZW')
					if cfg.osSCP.path.isfile(rstrOut2):
						# add raster to layers
						c = cfg.utls.addRasterLayer(rstrOut2)
						rasterSymbol = cfg.utls.rasterScatterSymbol([[1,"#FF0000"]])
						cfg.utls.setRasterScatterSymbol(c, rasterSymbol)
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.updateBar(100)
			if batch == 'No':
				cfg.utls.finishSound()
				cfg.utls.sendSMTPMessage(None, str(__name__))
				cfg.uiUtls.removeProgressBar()
