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

class NeighborPixels:

	def __init__(self):
		pass
		
	# neighbor
	def classNeighborAction(self):
		self.classNeighbor()
		
	# matrix file
	def inputMatrixFile(self):
		m = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a XML file'), '', 'CSV file (*.csv);;Text file (*.txt)')
		cfg.ui.label_287.setText(str(m))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), str(m))
		
	# classification neighbor
	def classNeighbor(self, batch = 'No', bandSetNumber = None, outputDirectory = None, size = None, structure = None, statName = None, statPerc = None, outputName = None):
			if bandSetNumber is None:
				bandSet = cfg.ui.band_set_comb_spinBox_15.value()
				bandSetNumber = bandSet - 1
			if bandSetNumber >= len(cfg.bandSetsList):
				cfg.mx.msgWar25(bandSetNumber + 1)
				return 'No'
			if batch == 'No':
				o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
			else:
				o = outputDirectory
			if len(o) > 0:
				if outputName is None:
					outputName = cfg.ui.neighbor_output_name_lineEdit.text()
					if len(outputName) > 0:
						outputName = str(outputName.encode('ascii','replace'))[2:-1] + '_' 
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
				bndSetSources = []
				if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
					ckB = cfg.utls.checkBandSet(bandSetNumber)
					bndSetSources = cfg.bndSetLst
				else:
					r = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
					iR = cfg.utls.layerSource(r)
					iBC = cfg.utls.getNumberBandRaster(iR)
					for i in range(1, iBC+1):
						bndNumberList.append(i)
						tVRT = cfg.utls.createTempRasterPath('vrt')
						bndSetSources.append(tVRT)
						cfg.utls.createVirtualRaster(inputRasterList = [iR], output = tVRT, bandNumberList = [i], quiet = 'Yes')
				if len(bndSetSources) == 0:
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar28()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error')
					return 'No'
				cfg.uiUtls.updateBar(10)
				if size is None:
					size =  cfg.ui.class_neighbor_threshold_spinBox.value()
				if statName is None:
					statName =  cfg.ui.statistic_name_combobox_2.currentText()
				for i in cfg.statisticList:
					if i[0].lower() == statName.lower():
						statNp = i[1]
						if i[0].lower() == 'percentile':
							if statPerc is None:
								statPerc = cfg.ui.statistic_lineEdit_2.text()
							try:
								statPerc = int(statPerc)
								break
							except:
								cfg.mx.msgErr66()
								return 'No'
						else:
							break
				if cfg.statPerc in statNp:
					ee = statNp.replace('array', 'A')
					try:
						statPerc = int(statPerc)
						ee = ee.replace(cfg.statPerc, str(statPerc) + ', axis=2')
					except:
						pass
				else:
					ee = statNp.replace('array', 'A, axis=2')
				functionList = [ee.replace('np.', 'cfg.np.')]
				if structure is None:
					if len(cfg.ui.label_287.text()) > 0:
						try:
							structure = self.openStructure(cfg.ui.label_287.text())
						except Exception as err:
							# logger
							if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
							return 'No'
					else:
						structure = cfg.np.ones((size*2+1,size*2+1))
				else:
					try:
						structure = self.openStructure(structure)
					except Exception as err:
						# logger
						if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
						return 'No'
				if 'nansum' in ee:
					additionalLayer = 2
				else:
					additionalLayer = structure.shape[0]*structure.shape[1]*0.8
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'structure ' + str(structure))
				for y in range(0, len(bndSetSources)):
					if cfg.actionCheck == 'Yes':
						input = bndSetSources[y]
						nd = cfg.utls.imageNoDataValue(input)
						dType = cfg.utls.getRasterDataTypeName(input)
						tPMD = cfg.utls.createTempRasterPath('vrt')
						# process calculation
						u = cfg.utls.multiProcessRaster(rasterPath = input, functionBand = 'No', functionRaster = cfg.utls.rasterNeighbor, outputRasterList = [tPMD], functionBandArgument = structure, functionVariable = functionList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Neighbor pixels'), virtualRaster = 'Yes', compress = 'No', outputNoDataValue = nd, dataType = dType, boundarySize = structure.shape[0]+1, additionalLayer = additionalLayer)
						outputRaster = o + '/' + outputName + cfg.utls.fileNameNoExt(bndSetSources[y]) + '.tif'
						# copy raster
						try:
							cfg.utls.GDALCopyRaster(tPMD, outputRaster, 'GTiff', cfg.rasterCompression, 'LZW')
						except Exception as err:
							# logger
							if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
						if cfg.osSCP.path.isfile(outputRaster):
							oR =cfg.utls.addRasterLayer(outputRaster)
				if batch == 'No':
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
			else:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
				cfg.mx.msgErr9()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error raster not found')
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		
	# open structure file
	def openStructure(self, structure):
		text = open(structure, 'r')
		lines = text.readlines()
		for b in lines:
			b = b.replace('nan', 'cfg.np.nan').replace('\n', '')
			a = eval(b)
			i = cfg.np.array(a,  dtype=cfg.np.float32)
			try:
				c = cfg.np.append(c, [i], axis=0)
			except:
				try:
					c = cfg.np.append([c], [i], axis=0)
				except:
					c = i
		return c
			
	# stat combo
	def loadStatisticCombo(self):
		cfg.ui.statistic_name_combobox_2.blockSignals(True)
		cfg.ui.statistic_name_combobox_2.clear()
		for i in cfg.statisticList:
			cfg.dlg.statistic_name_combo2(i[0])
		cfg.ui.statistic_name_combobox_2.blockSignals(False)