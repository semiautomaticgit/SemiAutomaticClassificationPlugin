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

class MODISTab:

	def __init__(self):
		pass
		
	# MODIS input
	def inputMODIS(self):
		i = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a HDF file'), '', 'file .hdf (*.hdf)')
		cfg.ui.label_217.setText(str(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), str(i))
	
	# MODIS conversion
	def MODIS(self, inputFile, outputDirectory, batch = 'No', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		if batch == 'No':
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)		
		cfg.uiUtls.updateBar(5)	
		l = cfg.ui.MODIS_tableWidget
		# input
		if inputFile.lower().endswith('.hdf') and cfg.osSCP.path.isfile(inputFile):
			fileNm = cfg.utls.fileNameNoExt(inputFile)
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputFile, cfg.gdalSCP.GA_ReadOnly)
			rDSub = rD.GetSubDatasets()
		out = outputDirectory
		oDir = cfg.utls.makeDirectory(out)
		date = cfg.ui.MODIS_date_lineEdit.text()
		# name prefix
		pre = 'RT_'
		# input bands
		c = l.rowCount()
		# temp raster
		tempRasterList = []
		convInputList = []
		# output raster list
		outputRasterList = []
		# band list
		bandSetList = []
		bandSetNameList = []
		bandNumberList = []
		for i in range(0, c):
			if cfg.actionCheck == 'Yes':
				iBand = l.item(i,0).text()
				iBandN = iBand[-2:]
				#  MODIS bands
				for sb in rDSub:
					inputRaster = None
					nm = sb[0]
					bandName = fileNm + '_' + iBandN
					inputRaster = nm
					try:
						bnI = inputRaster.split('b')[1][0:2]
						if inputRaster is not None and 'sur_refl' in str(inputRaster) and  iBandN == bnI:
							oNm = pre + iBand + '.tif'
							outputRaster = out + '/' + oNm
							outputRasterList.append(outputRaster)
							try:
								coeff = float(l.item(i,1).text())
							except:
								coeff = ''
							if cfg.ui.reproject_modis_checkBox.isChecked() is True:
								# temp files
								tPMD = cfg.utls.createTempRasterPath('tif')
								cfg.utls.GDALReprojectRaster(inputRaster, tPMD, 'GTiff', None, 'EPSG:4326', '-ot Float32 -dstnodata -999')
								inputRaster = tPMD
								tempRasterList.append(tPMD)
							# conversion
							m = float(coeff)
							e =  '( "raster" *' + str('%.16f' % m) + ' )'
							# band list
							bandSetList.append(int(bandName[-2:]))
							bandSetNameList.append(pre + bandName)
							convInputList.append([inputRaster, e, outputRaster])
					except:
						pass
		# conversion
		inputList = []
		argumentList = []
		variableList = []
		for inP in convInputList:
			inputList.append(inP[0])
			argumentList.append(inP[1])	
			variableList.append(['"raster"', '"raster"'])
		tPMDN = cfg.utls.createTempVirtualRaster(inputList, 'No', 'Yes', 'Yes', 0, 'No', 'No')
		# No data value
		if cfg.ui.nodata_checkBox_7.isChecked() is True:
			NoData = cfg.ui.nodata_spinBox_8.value()
		else:
			NoData = cfg.NoDataVal
		oM = cfg.utls.createTempRasterList(len(inputList))
		# open input with GDAL
		rD = cfg.gdalSCP.Open(tPMDN, cfg.gdalSCP.GA_ReadOnly)
		# output rasters
		cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0,  None, compress = cfg.rasterCompression, compressFormat = 'LZW')
		rD = None
		o = cfg.utls.multiProcessRaster(rasterPath = tPMDN, functionBand = 'No', functionRaster = cfg.utls.calculateRaster, outputRasterList = oM, nodataValue = NoData, functionBandArgument = argumentList, functionVariable = variableList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion'), parallel = cfg.parallelRaster)
		if cfg.actionCheck == 'Yes':
			for t in range(0, len(outputRasterList)):
				cfg.shutilSCP.move(oM[t], outputRasterList[t])
			# load raster bands
			for outR in outputRasterList:
				if cfg.osSCP.path.isfile(outR):
					cfg.utls.addRasterLayer(outR)
				else:
					cfg.mx.msgErr38(outR)
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'WARNING: unable to load raster' + str(outR))
			for tmpR in tempRasterList:
				try:
					cfg.osSCP.remove(tmpR)
				except:
					pass
			# create band set
			if cfg.ui.create_bandset_checkBox.isChecked() is True:
				if cfg.ui.add_new_bandset_checkBox_5.isChecked() is True:
					bandSetNumber = cfg.bst.addBandSetTab()
				cfg.bst.rasterBandName()
				cfg.bst.setBandSet(bandSetNameList, bandSetNumber, date)
				cfg.bandSetsList[bandSetNumber][0] = 'Yes'
				if len(bandSetNameList) > 2:
					cfg.bst.setSatelliteWavelength(cfg.satMODIS, None, bandSetNumber)
				else:
					cfg.bst.setSatelliteWavelength(cfg.satMODIS2, None, bandSetNumber)	
				if bandSetNumber is None:
					bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
				tW = eval('cfg.ui.tableWidget__' + cfg.bndSetTabList[bandSetNumber])
				tW.clearSelection()
				tW.selectRow(0)
				tW.selectRow(1)
				cfg.bst.moveDownBand()
				cfg.bst.moveDownBand()
				tW.clearSelection()
			cfg.bst.bandSetTools(out)
			cfg.uiUtls.updateBar(100)
		# close GDAL rasters
		rDSub = None
		rD = None
		if batch == 'No':
			cfg.utls.finishSound()
			cfg.utls.sendSMTPMessage(None, str(__name__))
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()
	
	# MODIS conversion button
	def performMODISConversion(self):
		if len(cfg.ui.label_217.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.MODIS(cfg.ui.label_217.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Perform MODIS conversion: ' + str(cfg.ui.label_217.text()))
		
	# populate table
	def populateTable(self, input, batch = 'No'):
		check = 'Yes'
		l = cfg.ui.MODIS_tableWidget
		cfg.utls.setColumnWidthList(l, [[0, 250]])
		cfg.utls.clearTable(l)
		if len(input) == 0:
			cfg.mx.msg14()
		else:
			if batch == 'No':
				cfg.uiUtls.addProgressBar()
			# bands
			bandNames = []
			# input
			if input.lower().endswith('.hdf'):
				fileNm = cfg.utls.fileNameNoExt(input)
				# open input with GDAL
				rD = cfg.gdalSCP.Open(input, cfg.gdalSCP.GA_ReadOnly)
				if rD is None:
					pass
				else:
					# get metadata
					rDMeta = rD.GetMetadata_List()
					for metadata in rDMeta:
						if 'LOCALGRANULEID' in metadata:
							mod_ID = metadata.split('=')[1]
						if 'RANGEBEGINNINGDATE' in metadata:
							date = metadata.split('=')[1]
					cfg.ui.MODIS_ID_lineEdit.setText(mod_ID)
					cfg.ui.MODIS_date_lineEdit.setText(date)
					rDSub = rD.GetSubDatasets()
					#  MODIS bands
					for sb in rDSub:
						nm = sb[0]
						if 'sur_refl' in str(nm):
							try:
								bandNames.append(fileNm + '_' + nm.split('b')[1][0:2])
							except:
								pass
			# add band items to table
			b = 0
			for band in sorted(bandNames):				
				l.insertRow(b)
				l.setRowHeight(b, 20)
				cfg.utls.addTableItem(l, band, b, 0, 'No')
				cfg.utls.addTableItem(l, str(0.0001), b, 1)
				b = b + 1
			if batch == 'No':
				cfg.uiUtls.removeProgressBar()			

	# edited cell
	def editedCell(self, row, column):
		if column != 0:
			l = cfg.ui.MODIS_tableWidget
			val = l.item(row, column).text()
			try:
				float(val)
			except:
				l.item(row, column).setText("")
			
	def removeHighlightedBand(self):
		l = cfg.ui.MODIS_tableWidget
		cfg.utls.removeRowsFromTable(l)
		