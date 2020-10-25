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

class GOESTab:

	def __init__(self):
		pass
		
	# GOES input
	def inputGOES(self):
		i = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
		cfg.ui.GOES_label.setText(str(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), str(i))
		
	# populate table
	def populateTable(self, input, batch = 'No'):
		check = 'Yes'
		sat = 'GOES'
		cfg.ui.GOES_satellite_lineEdit.setText(sat)
		l = cfg.ui.GOES_tableWidget
		cfg.utls.setColumnWidthList(l, [[0, 450]])
		cfg.utls.clearTable(l)
		inp = input
		if len(inp) == 0:
			cfg.mx.msg14()
		else:
			if batch == 'No':
				cfg.uiUtls.addProgressBar()
			cfg.ui.GOES_satellite_lineEdit.setText(sat)
			# bands
			dBs = {}
			bandNames = []	
			for f in cfg.osSCP.listdir(inp):
				if f.lower().endswith('.nc'):
					f = f[0:-3]
					# check band number
					bNmb = str(f[-2:])
					try:
						if int(bNmb) in range(1,7):
							bandNames.append(f)
					except:
						pass
			cfg.uiUtls.updateBar(50)
			# add band items to table
			b = 0
			for band in sorted(bandNames):
				l.insertRow(b)
				l.setRowHeight(b, 20)
				cfg.utls.addTableItem(l, band, b, 0)
				b = b + 1
			if batch == 'No':
				cfg.uiUtls.removeProgressBar()
			
	# remove band
	def removeHighlightedBand(self):
		l = cfg.ui.GOES_tableWidget
		cfg.utls.removeRowsFromTable(l)

	# edited cell
	def editedCell(self, row, column):
		if column != 0:
			l = cfg.ui.GOES_tableWidget
			val = l.item(row, column).text()
			try:
				float(val)
			except:
				l.item(row, column).setText('')

	# GOES output
	def performGOESConversion(self):
		if len(cfg.ui.GOES_label.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.GOES(cfg.ui.GOES_label.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Perform GOES conversion: ' + str(cfg.ui.GOES_label.text()))
		
	# GOES conversion
	def GOES(self, inputDirectory, outputDirectory, batch = 'No', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		cfg.uiUtls.addProgressBar()
		# disable map canvas render for speed
		if batch == 'No':
			cfg.cnvs.setRenderFlag(False)
		# Esun
		dEsunB = {}
		# Esun from GOES-R, 2017. PRODUCT DEFINITION AND USER’S GUIDE (PUG) VOLUME 3: LEVEL 1B PRODUCTS
		dEsunB = {'ESUN_BAND01': 2041.6865234375, 'ESUN_BAND02': 1628.080078125, 'ESUN_BAND03': 955.5531005859375, 'ESUN_BAND04': 361.5187683105469, 'ESUN_BAND05': 242.64404296875, 'ESUN_BAND06': 77.00672149658203}
		# output raster list
		outputRasterList = []
		# band list
		bandSetList = []
		bandSetNameList = []
		bandNumberList = []
		sat = cfg.ui.GOES_satellite_lineEdit.text()
		if str(sat) == '':
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' No satellite error')
			if batch == 'No':
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
			cfg.mx.msgErr37()
			return 'No'
		cfg.uiUtls.updateBar(5, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion'))
		l = cfg.ui.GOES_tableWidget
		inp = inputDirectory
		out = outputDirectory
		# input
		for f in cfg.osSCP.listdir(inp):
			cfg.QtWidgetsSCP.qApp.processEvents()
		cfg.uiUtls.updateBar(20)
		# name prefix
		pre = 'RT_'
		oDir = cfg.utls.makeDirectory(out)
		l = cfg.ui.GOES_tableWidget
		# input bands
		c = l.rowCount()
		# output raster list
		outputRasterList = []
		convInputList = []
		tempRasterList1 = []
		# No data value
		if cfg.ui.GOES_nodata_checkBox.isChecked() is True:
			nD = cfg.ui.GOES_nodata_spinBox.value()
		else:
			nD = cfg.NoDataVal
		threadNumber = cfg.threads
		sez = list(range(0, c, threadNumber))
		sez.append(c)
		cfg.subprocDictProc = {}
		for s in range(0, len(sez)-1):
			for p in range(sez[s], sez[s+1]):
				iBand = l.item(p,0).text()
				iBandN = iBand[-2:]
				sBand = inp + '/' + iBand + '.nc'
				# temp files
				tPMD = cfg.utls.createTempRasterPath('tif')
				tempRasterList1.append(tPMD)
				gD = 'gdalwarp --config GDAL_DISABLE_READDIR_ON_OPEN TRUE -co BIGTIFF=YES -r near -co COMPRESS=LZW -t_srs ' + 'EPSG:4326 -ot Float32 -dstnodata ' + str(nD) + ' -of GTiff'
				cfg.utls.getGDALForMac()
				a = cfg.gdalPath + gD
				b = 'NETCDF:"' +sBand + '":Rad'
				g = '"' + tPMD + '" '
				d = a + ' ' + b + ' ' + g
				if cfg.sysSCPNm != 'Windows':
					d = cfg.shlexSCP.split(d)
				cfg.subprocDictProc['proc_'+ str(p)] = cfg.subprocessSCP.Popen(d, shell=False)
			while True:
				polls = []
				for p in range(sez[s], sez[s+1]):
					polls.append(cfg.subprocDictProc['proc_'+ str(p)].poll())
				if polls.count(None) == 0:
					break
				else:
					try:
						try:
							dots = dots + '.'
							if len(dots) > 3:
								dots = ''
						except:
							dots = ''
						cfg.uiUtls.updateBar(message = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reprojecting') + dots)
					except:
						pass
				cfg.QtWidgetsSCP.qApp.processEvents()
				if cfg.actionCheck != 'Yes':
					break
				cfg.timeSCP.sleep(1)
		for i in range(0, c):
			iBand = l.item(i,0).text()
			iBandN = iBand[-2:]
			sBand = inp + '/' + iBand + '.nc'
			# open input with GDAL
			rDB = cfg.gdalSCP.Open('NETCDF:"' +sBand + '":Rad', cfg.gdalSCP.GA_ReadOnly)
			gBand = rDB.GetRasterBand(1)
			offs = gBand.GetOffset()
			scl = gBand.GetScale()
			rDMeta = rDB.GetMetadata_List()
			# get metadata
			for metadata in rDMeta:
				if 'time_coverage_start' in metadata:
					dt = metadata.split('=')[1].split('T')[0]
			gBand = None
			rDB = None
			eSun = float(dEsunB['ESUN_BAND' + str(iBandN)])
			# date format
			dFmt = '%Y-%m-%d'
			eSD = float(cfg.utls.calculateEarthSunDistance(dt, dFmt))
			m = float(scl)
			a = float(offs)
			e = 'cfg.np.clip(cfg.np.where("raster" == ' + str(nD) + ', ' + str(cfg.NoDataVal) + ', ( "raster" *' + str('%.16f' % m) + '+ (' + str('%.16f' % a) + ')) * ' + str('%.16f' % cfg.np.pi) + ' * ' + str('%.16f' % eSD) + ' * ' + str('%.16f' % eSD) + '/ (' + str('%.16f' % eSun)+ ' ) ), 0, 1)'
			outputRaster = oDir + '/' + pre + iBand + '.tif'
			convInputList.append([tempRasterList1[i], e, outputRaster])
			# band list
			bandSetList.append(iBandN)
			bandSetNameList.append(pre + iBand)
			outputRasterList.append(outputRaster)
		if len(convInputList) > 0:
			# conversion
			inputList = []
			functionList = []
			variableList = []
			bandList = []
			for inP in convInputList:
				inputList.append(inP[0])
				functionList.append(inP[1])	
				variableList.append(['"raster"', '"raster"'])
				bandList.append(1)
			tPMDN = cfg.utls.createTempVirtualRaster(inputList, 'No', 'Yes', 'Yes', 0, 'No', 'No')
			tempRasterList = cfg.utls.createTempRasterList(len(outputRasterList))
			try:
				# open input with GDAL
				rD = cfg.gdalSCP.Open(tPMDN, cfg.gdalSCP.GA_ReadOnly)
				# output rasters
				cfg.utls.createRasterFromReference(rD, 1, tempRasterList, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0,  None, compress = 'Yes', compressFormat = 'LZW')
				rD = None
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return 'No'
			# No data value
			if cfg.ui.GOES_nodata_checkBox.isChecked() is True:
				NoData = cfg.ui.GOES_nodata_spinBox.value()
			else:
				NoData = cfg.NoDataVal	
			argumentList = functionList
			o = cfg.utls.multiProcessRaster(rasterPath = tPMDN, functionBand = 'No', functionRaster = cfg.utls.calculateRaster, outputRasterList = tempRasterList, nodataValue = NoData, functionBandArgument = argumentList, functionVariable = variableList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion'), parallel = cfg.parallelRaster)
			if cfg.actionCheck == 'Yes':
				for t in range(0, len(outputRasterList)):
					cfg.shutilSCP.move(tempRasterList[t], outputRasterList[t])
				# load raster bands
				for outR in outputRasterList:
					if cfg.osSCP.path.isfile(outR):
						cfg.utls.addRasterLayer(outR)
					else:
						cfg.mx.msgErr38(outR)
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'WARNING: unable to load raster' + str(outR))
				# create band set
				if cfg.ui.GOES_create_bandset_checkBox.isChecked() is True:
					if cfg.ui.add_new_bandset_checkBox_7.isChecked() is True:
						bandSetNumber = cfg.bst.addBandSetTab()
					cfg.bst.rasterBandName()
					cfg.bst.setBandSet(bandSetNameList, bandSetNumber, dt)
					cfg.bandSetsList[bandSetNumber][0] = 'Yes'
					cfg.bst.setSatelliteWavelength(cfg.satGOES, bandSetList, bandSetNumber)				
					if bandSetNumber == None:
						bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
					tW = eval('cfg.ui.tableWidget__' + cfg.bndSetTabList[bandSetNumber])
					tW.clearSelection()
				cfg.bst.bandSetTools(oDir)
				# remove temporary files
				try:
					for t in tempRasterList1:
						cfg.osSCP.remove(t)
				except:
					pass
		if batch == 'No':
			cfg.utls.finishSound()
			cfg.utls.sendSMTPMessage(None, str(__name__))
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()

