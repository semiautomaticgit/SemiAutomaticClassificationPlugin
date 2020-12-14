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

class Sentinel3Tab:

	def __init__(self):
		pass
		
	# Sentinel-3 input
	def inputSentinel(self):
		i = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
		cfg.ui.S3_label_87.setText(str(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), str(i))
		
	# populate table
	def populateTable(self, input, batch = 'No'):
		check = 'Yes'
		sat = 'Sentinel-3A'
		prod = 'OLCI'
		cfg.ui.S3_satellite_lineEdit.setText(sat)
		cfg.ui.S3_product_lineEdit.setText(prod)
		l = cfg.ui.sentinel_3_tableWidget
		cfg.utls.setColumnWidthList(l, [[0, 450]])
		cfg.utls.clearTable(l)
		inp = input
		if len(inp) == 0:
			cfg.mx.msg14()
		else:
			if batch == 'No':
				cfg.uiUtls.addProgressBar()
			cfg.ui.S3_satellite_lineEdit.setText(sat)
			# bands
			dBs = {}
			bandNames = []	
			for f in cfg.osSCP.listdir(inp):
				if f.lower().endswith('.nc'):
					f = f[0:-3]
					# check band number
					bNmb = str(f[2:4])
					try:
						if int(bNmb) in range(0,22):
							bandNames.append(f)
					except:
						bNmb = str(f[-2:])
						try:
							if int(bNmb) in range(0,22):
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
			
	# edited satellite
	def editedSatellite(self):
		sat = cfg.ui.S3_satellite_lineEdit.text()
		if str(sat).lower() in ['sentinel_3a', 'sentinel-3a', 'sentinel_3b', 'sentinel-3b']:
			cfg.ui.S3_satellite_lineEdit.setStyleSheet('color : black')
		else:
			cfg.ui.S3_satellite_lineEdit.setStyleSheet('color : red')
	
	# remove band
	def removeHighlightedBand(self):
		l = cfg.ui.sentinel_3_tableWidget
		cfg.utls.removeRowsFromTable(l)

	# edited cell
	def editedCell(self, row, column):
		if column != 0:
			l = cfg.ui.sentinel_3_tableWidget
			val = l.item(row, column).text()
			try:
				float(val)
			except:
				l.item(row, column).setText('')

	# sentinel-3 output
	def performSentinelConversion(self):
		if len(cfg.ui.S3_label_87.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.sentinel3(cfg.ui.S3_label_87.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Perform sentinel-3 conversion: ' + str(cfg.ui.S3_label_87.text()))
		
	# sentinel-3 conversion
	def sentinel3(self, inputDirectory, outputDirectory, batch = 'No', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		cfg.uiUtls.addProgressBar()
		# disable map canvas render for speed
		if batch == 'No':
			cfg.cnvs.setRenderFlag(False)
		SZA = None
		dEsunB = None
		gcpList = None
		# output raster list
		outputRasterList = []
		# band list
		bandSetList = []
		bandSetNameList = []
		bandNumberList = []
		sat = cfg.ui.S3_satellite_lineEdit.text()
		productType = cfg.ui.S3_product_lineEdit.text()
		if str(sat) == '':
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' No satellite error')
			if batch == 'No':
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
			cfg.mx.msgErr37()
			return 'No'
		cfg.uiUtls.updateBar(5, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion'))
		l = cfg.ui.sentinel_3_tableWidget
		inp = inputDirectory
		out = outputDirectory
		# input
		for f in cfg.osSCP.listdir(inp):
			cfg.QtWidgetsSCP.qApp.processEvents()
			if f.lower().endswith('.nc') and 'qualityflags' in f.lower():
				pass
			elif f.lower().endswith('.nc') and 'geo_coordinates' in f.lower():
				# get pixel coordinates
				geo_coordinates = inp + '/' + f
				# open input with GDAL
				rDGC = cfg.gdalSCP.Open(geo_coordinates, cfg.gdalSCP.GA_ReadOnly)
				rDGCSub = rDGC.GetSubDatasets()
				for sb in rDGCSub:
					nm = sb[0]
					if 'latitude' in str(nm):
						# open input with GDAL
						rDLat = cfg.gdalSCP.Open(nm)
						rDLatB = rDLat.GetRasterBand(1)
					elif 'longitude' in str(nm):
						# open input with GDAL
						rDLon = cfg.gdalSCP.Open(nm)
						rDLonB = rDLon.GetRasterBand(1)
				# set GCPs
				gcpList = []
				z = 0
				x10 = int(rDLon.RasterXSize/10)
				y10 = int(rDLon.RasterYSize/10)
				rX = list(range(0, rDLon.RasterXSize, x10))
				rY = list(range(0, rDLon.RasterYSize, y10))
				rX.append(rDLon.RasterXSize-1)
				rY.append(rDLon.RasterYSize-1)
				# read points
				for pX in rX:
					for pY in rY:
						x = cfg.utls.readArrayBlock(rDLonB, pX, pY, 1, 1)
						y = cfg.utls.readArrayBlock(rDLatB, pX, pY, 1, 1)
						try:
							gcp = cfg.gdalSCP.GCP(float(x), float(y), z, pX, pY)
							gcpList.append(gcp)
						except:
							pass
				sr = cfg.osrSCP.SpatialReference()
				sr.ImportFromEPSG(4326)
				gcpProj = sr.ExportToWkt()
				rDLatB = None
				rDLat = None
				bLLonB = None
				rDLon = None
				rDSub = None
				rD = None
			elif f.lower().endswith('.nc') and 'tie_geometries' in f.lower():
				tie_geometries = inp + '/' + f
				# open input with GDAL
				rDTG = cfg.gdalSCP.Open(tie_geometries, cfg.gdalSCP.GA_ReadOnly)
				rDTGSub = rDTG.GetSubDatasets()
				for sb in rDTGSub:
					nm = sb[0]
					if 'SZA' in str(nm):
						# open input with GDAL
						rDSZA = cfg.gdalSCP.Open(nm)
						rDSZAB = rDSZA.GetRasterBand(1)
						# get the mean value of sun zenith angle
						bSt = rDSZAB.GetStatistics(True, True)
						SZA = bSt[2] / 1000000
				rDTGSub = None
				rDTG = None
			elif f.lower().endswith('.nc') and 'instrument_data' in f.lower():
				instrument_data = inp + '/' + f
				# open input with GDAL
				rDID = cfg.gdalSCP.Open(instrument_data, cfg.gdalSCP.GA_ReadOnly)
				rDIDSub = rDID.GetSubDatasets()
				# Esun
				dEsunB = {}
				for sb in rDIDSub:
					nm = sb[0]
					if 'solar_flux' in str(nm):
						# open input with GDAL
						rDSolF = cfg.gdalSCP.Open(nm)
						rDSolFB = rDSolF.GetRasterBand(1)
						# get the mean value of solar flux for each band
						for y in range(0, rDSolF.RasterYSize):
							esun = cfg.utls.readArrayBlock(rDSolFB, int(rDSolF.RasterXSize / 2), y, 1, 1)
							dEsunB['ESUN_BAND' + str(y + 1)] = float(esun)
				rDIDSub = None
				rDID = None
		cfg.uiUtls.updateBar(20)
		if SZA is None or bool(dEsunB) is False or gcpList is None:
			if batch == 'No':
				cfg.cnvs.setRenderFlag(True)
				cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr37()
			else:
				cfg.mx.msgErr37()
				return
		# name prefix
		pre = 'RT_'
		oDir = cfg.utls.makeDirectory(out)
		l = cfg.ui.sentinel_3_tableWidget
		# input bands
		c = l.rowCount()
		# output raster list
		outputRasterList = []
		convInputList = []
		nodataValue = 0		
		for i in range(0, c):
			iBand = l.item(i,0).text()
			iBandN = int(iBand[-2:])
			sBand = inp + '/' + iBand + '.nc'
			# open input with GDAL
			rDB = cfg.gdalSCP.Open(sBand, cfg.gdalSCP.GA_ReadOnly)
			rDMeta = rDB.GetMetadata_List()
			for metadata in rDMeta:
				if 'scale_factor' in metadata:
					scale_factor = metadata.split('=')[1]
				elif 'add_offset' in metadata:
					add_offset = metadata.split('=')[1]
				elif '_FillValue' in metadata:
					fillValue = metadata.split('=')[1]
				elif 'start_time' in metadata:
					date = metadata.split('=')[1].split('T')[0]
			eSun = float(dEsunB['ESUN_BAND' + str(iBandN)])
			# temp files
			tPMD = cfg.utls.createTempRasterPath('tif')
			e = self.sentinel3reflectance(scale_factor, add_offset, fillValue, eSun, SZA, date, tPMD)
			outputRaster = oDir + '/' + pre + iBand + '.tif'
			convInputList.append([sBand, e, outputRaster])
			# band list
			bandSetList.append(iBandN)
			bandSetNameList.append(pre + iBand)
			outputRasterList.append(outputRaster)
			xSize = rDB.RasterXSize
			ySize = rDB.RasterYSize
			rDB = None
		if len(convInputList) > 0:
			# conversion
			inputList = []
			functionList = []
			variableList = []
			bandList = []
			# reference system
			rSrc = cfg.osrSCP.SpatialReference()
			rSrc.SetProjCS('proj')
			rSrc.SetWellKnownGeogCS('WGS84')
			self.rSr = rSrc.ExportToWkt()
			for inP in convInputList:
				inputList.append(inP[0])
				functionList.append(inP[1])	
				variableList.append(['"raster"', '"raster"'])
				bandList.append(1)
			tPMDN = cfg.utls.createTempVirtualRaster(inputList, bandList, 'Yes', 'Yes', 0, self.rSr, 'No')
			# No data value
			if cfg.ui.S3_nodata_checkBox.isChecked() is True:
				NoData = cfg.ui.S2_nodata_spinBox_2.value()
			else:
				NoData = cfg.NoDataVal	
			# DOS 1
			if cfg.ui.DOS1_checkBox_S3.isChecked() is True:
				LDNmList = cfg.utls.findDNmin(tPMDN, NoData)
				argumentList = []
				for dnM in range(0, len(LDNmList)):
					e = functionList[dnM].replace('LDNm', str(LDNmList[dnM]))
					argumentList.append(e)
			else:
				argumentList = functionList
			# create temporary rasters
			tempRasterList = cfg.utls.createTempRasterList(len(inputList))
			self.createGeoreferencedRaster(tempRasterList, xSize, ySize, gcpList, gcpProj, 0)
			o = cfg.utls.multiProcessRaster(rasterPath = tPMDN, functionBand = 'No', functionRaster = cfg.utls.calculateRaster, outputRasterList = tempRasterList, nodataValue = NoData, functionBandArgument = argumentList, functionVariable = variableList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion'), parallel = cfg.parallelRaster)
			if cfg.actionCheck == 'Yes':
				for t in range(0, len(outputRasterList)):
					cfg.utls.GDALReprojectRaster(tempRasterList[t], outputRasterList[t], 'GTiff', None, 'EPSG:4326', '-ot Float32 -dstnodata ' + str(NoData))
					#cfg.shutilSCP.move(tempRasterList[t], outputRasterList[t])
				# load raster bands
				for outR in outputRasterList:
					if cfg.osSCP.path.isfile(outR):
						cfg.utls.addRasterLayer(outR)
					else:
						cfg.mx.msgErr38(outR)
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'WARNING: unable to load raster' + str(outR))
				# create band set
				if cfg.ui.S3_create_bandset_checkBox.isChecked() is True:
					if cfg.ui.add_new_bandset_checkBox_3.isChecked() is True:
						bandSetNumber = cfg.bst.addBandSetTab()
					cfg.bst.rasterBandName()
					cfg.bst.setBandSet(bandSetNameList, bandSetNumber, date)
					cfg.bandSetsList[bandSetNumber][0] = 'Yes'
					cfg.bst.setSatelliteWavelength(cfg.satSentinel3, bandSetList, bandSetNumber)				
					if bandSetNumber is None:
						bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
					tW = eval('cfg.ui.tableWidget__' + cfg.bndSetTabList[bandSetNumber])
					tW.clearSelection()
				cfg.bst.bandSetTools(oDir)
		if batch == 'No':
			cfg.utls.finishSound()
			cfg.utls.sendSMTPMessage(None, str(__name__))
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()

	# conversion to Reflectance
	def sentinel3reflectance(self, scale_factor, add_offset, fillValue, eSun, SZA, date, outputRaster):
		eSD = None
		# date format
		dFmt = '%Y-%m-%d'
		try:
			eSD = float(cfg.utls.calculateEarthSunDistance(date, dFmt))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		# cosine solar zenith angle
		sA = cfg.np.cos(SZA * cfg.np.pi / 180)
		# No data value
		if cfg.ui.S3_nodata_checkBox.isChecked() is True:
			nD = cfg.ui.S2_nodata_spinBox_2.value()
		else:
			nD = cfg.NoDataVal
		m = float(scale_factor)
		a = float(add_offset)
		# TOA reflectance with correction for sun angle
		if cfg.ui.DOS1_checkBox_S3.isChecked() is False:
			e = 'cfg.np.clip(cfg.np.where("raster" == ' + str(nD) + ', ' + str(cfg.NoDataVal) + ', ( "raster" *' + str('%.16f' % m) + '+ (' + str('%.16f' % a) + ')) * ' + str('%.16f' % cfg.np.pi) + ' * ' + str('%.16f' % eSD) + ' * ' + str('%.16f' % eSD) + '/ (' + str('%.16f' % eSun)+ ' * ' + str(sA) + ' ) ), 0, 1)'
		# DOS atmospheric correction
		else:
			# radiance calculation
			e = 'cfg.np.where("raster" == ' + str(nD) + ', ' + str(cfg.NoDataVal) + ', ("raster" *' + str('%.16f' % m) + '+ (' + str('%.16f' % a) + ')))'
			# path radiance Lp = ML* DNm + AL  – 0.01* ESUNλ * cosθs / (π * d^2)	
			Lp =  str(m) + ' * LDNm + ' + str(a - 0.01 * eSun * sA / (cfg.np.pi * eSD * eSD))
			# land surface reflectance ρ = [π * (Lλ - Lp) * d^2]/ (ESUNλ * cosθs)
			e = 'cfg.np.clip((' + e + ' - (' + Lp + ' ) )* ' + str('%.16f' % cfg.np.pi) + ' * ' + str('%.16f' % eSD) + ' * ' + str('%.16f' % eSD) + ' / ( ' + str('%.16f' % eSun)+ ' * ' + str(sA) + ' ), 0, 1)'
		return e

	# georeferenced raster
	def createGeoreferencedRaster(self, outputList, RasterXSize, RasterYSize, gcpList, gcpProj, nodataValue):
		for output in outputList:
			tD = cfg.gdalSCP.GetDriverByName('GTiff')		
			oD = tD.Create(output, RasterXSize, RasterYSize, 1, cfg.gdalSCP.GDT_Float32, ['COMPRESS=LZW'])
			oD.SetGCPs(gcpList, gcpProj)
			oBnd = oD.GetRasterBand(1)
			oBnd.SetNoDataValue(nodataValue)
			oBnd.Fill(nodataValue)
			oBnd = None
			oD = None
		