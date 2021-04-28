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

class MosaicBandSets:

	def __init__(self):
		pass
		
	# list band sets
	def textChanged(self):
		self.checkValueList()
				
	# check value list
	def checkValueList(self):
		try:
			# class value list
			text = cfg.ui.mosaic_band_sets_lineEdit.text()
			if text == '*':
				l = list(range(1, len(cfg.bandSetsList)+1))
			else:
				l = text.split(',')
			valueList = []
			for v in l:
				valueList.append(int(v))
			cfg.ui.mosaic_band_sets_lineEdit.setStyleSheet('color : green')
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		except Exception as err:
			cfg.ui.mosaic_band_sets_lineEdit.setStyleSheet('color : red')
			valueList = []
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		return valueList
		
	# mosaic band sets
	def mosaicAction(self):
		self.mosaicBandSets()
		
	# mosaic multiple band sets
	def mosaicBandSets(self, batch = 'No', outputDirectory = None, bandSetList = None, virtual = None):
		if bandSetList is None:
			bandSetList = cfg.mosaicBS.checkValueList()
		else:
			if bandSetList == '*':
				bandSetList = list(range(1, len(cfg.bandSetsList)+1))
			else:
				try:
					bandSetList = eval(bandSetList)
				except:
					cfg.mx.msgWar28()
					return 'No'
		if virtual is None:
			if cfg.ui.mosaic_virtual_checkBox.isChecked() is True:
				virtual = 'Yes'
		if len(bandSetList) > 0:
			bSL = []
			for v in bandSetList:
				bSL.append(v-1)
			if batch == 'No':
				o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
			else:
				o = outputDirectory
			if len(o) > 0:
				outputName = cfg.ui.mosaic_output_name_lineEdit.text()
				if len(outputName) > 0:
					outputName = str(outputName.encode('ascii','replace'))[2:-1] + '_' 
				bndSetSources = []
				if batch == 'No':
					cfg.uiUtls.addProgressBar()
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
						if ckB == 'Yes':
							bndSetSources.append(cfg.bndSetLst)
					else:
						bi = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
						try:
							bPath = cfg.utls.layerSource(bi)
						except Exception as err:
							cfg.mx.msg4()
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
						rT = cfg.utls.rasterToBands(bPath, cfg.tmpDir, outputName = cfg.utls.fileName(cfg.bandSetsList[bandSetNumber][8]), virtual = 'No')
						bndSetSources.append(rT)
					if len(cfg.bndSetLst) == 0:
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
				# No data value
				if cfg.ui.nodata_checkBox_9.isChecked() is True:
					NoDataVal = cfg.ui.nodata_spinBox_10.value()
				else:
					NoDataVal = 'Yes'
				for bst in bndSetSources:
					if len(bst) != len(bndSetSources[0]):
						if batch == 'No':
							cfg.uiUtls.removeProgressBar()
						cfg.mx.msgWar28()
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
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
									nD = cfg.NoDataVal
								if virtual == 'Yes':
									tPMD = o + '/' + cfg.utls.fileNameNoExt(bndSetSources[bstIndex][b]) + 'p.vrt'
								else:
									tPMD = cfg.utls.createTempRasterPath('vrt')
								cfg.utls.createWarpedVrt(bst[b], tPMD, str(rCrs))
								cfg.mx.msg9()
								#tPMD = cfg.utls.createTempRasterPath('tif')
								#cfg.utls.GDALReprojectRaster(bst[b], tPMD, 'GTiff', None, 'EPSG:' + str(rEPSG), '-ot Float32 -dstnodata ' + str(nD))
								if cfg.osSCP.path.isfile(tPMD):
									bndSetSources[bstIndex][b] = tPMD
								else:
									if batch == 'No':
										cfg.uiUtls.removeProgressBar()
									cfg.mx.msgErr60()
									# logger
									cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
									return 'No'
							else:
								nD = cfg.utls.imageNoDataValue(bst[b])
								if nD is None:
									nD = cfg.NoDataVal
								if virtual == 'Yes':
									tPMD = o + '/' + cfg.utls.fileNameNoExt(bndSetSources[bstIndex][b]) + 'p.tif'
								else:
									tPMD = cfg.utls.createTempRasterPath('tif')
								cfg.utls.GDALReprojectRaster(bst[b], tPMD, 'GTiff', None, 'EPSG:' + str(rEPSG), '-ot Float32 -dstnodata ' + str(nD))
								if cfg.osSCP.path.isfile(tPMD):
									for bb in range(0, len(bst)):
										bndSetSources[bstIndex][bb] = tPMD
									break
								else:
									if batch == 'No':
										cfg.uiUtls.removeProgressBar()
									cfg.mx.msgErr60()
									# logger
									cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
									return 'No'
				cfg.uiUtls.updateBar(20)	
				for y in range(0, len(bndSetSources[0])):
					bList = []
					for x in range(0, len(bndSetSources)):
						bstIndex = bndSetSources.index(bndSetSources[x])
						bList.append(bndSetSources[x][y])
					dType = cfg.utls.getRasterDataTypeName(bndSetSources[0][y])
					if virtual == 'Yes':
						tVRT = o + '/' + outputName + cfg.utls.fileNameNoExt(bndSetSources[0][y]) + '.vrt'
						rstrOut = tVRT
					else:
						rstrOut = o + '/' + outputName + cfg.utls.fileNameNoExt(bndSetSources[0][y]) + '.tif'
						tVRT = cfg.utls.createTempRasterPath('vrt')
					cfg.utls.createVirtualRaster2(inputRasterList = bList, output = tVRT, NoDataValue = NoDataVal, dataType = dType)
					if virtual != 'Yes':
						cfg.utls.GDALCopyRaster(tVRT, rstrOut, 'GTiff', cfg.rasterCompression)
					if cfg.osSCP.path.isfile(rstrOut):
						cfg.utls.addRasterLayer(rstrOut)
				cfg.uiUtls.updateBar(100)
				if batch == 'No':
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.uiUtls.removeProgressBar()
				