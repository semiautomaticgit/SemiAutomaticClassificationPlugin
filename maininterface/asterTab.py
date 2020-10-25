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

class ASTERTab:

	def __init__(self):
		pass
		
	# ASTER input
	def inputASTER(self):
		i = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a HDF file'), '', 'file .hdf (*.hdf)')
		cfg.ui.label_143.setText(str(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), str(i))
	
	# ASTER conversion to reflectance and temperature
	def ASTER(self, inputFile, outputDirectory, batch = 'No', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		if batch == 'No':
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
		self.sA = ''
		self.eSD = ''
		ulm = cfg.ui.ulm_lineEdit.text()
		lrm = cfg.ui.lrm_lineEdit.text()
		try:
			uLY = float(ulm.split(',')[0])
			uLX = float(ulm.split(',')[1])
			lRY = float(lrm.split(',')[0])
			lRX = float(lrm.split(',')[1])
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' No earth sun distance error')
			if batch == 'No':
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
			cfg.mx.msgErr37()
			return 'No'
		utmZone = int(cfg.ui.utm_zone_lineEdit.text())
		# reference system
		rSrc = cfg.osrSCP.SpatialReference()
		rSrc.SetProjCS('proj')
		rSrc.SetWellKnownGeogCS('WGS84')
		if utmZone > 0:
			rSrc.SetUTM(utmZone, True)
		else:
			rSrc.SetUTM(utmZone, False)
		self.rSr = rSrc.ExportToWkt()
		if len(cfg.ui.sun_elev_lineEdit_2.text()) > 0:
			sE = float(cfg.ui.sun_elev_lineEdit_2.text())
			# sine sun elevation
			self.sA = cfg.np.sin(sE * cfg.np.pi / 180)
		else:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' No sun elevation error')
			if batch == 'No':
				cfg.uiUtls.removeProgressBar()
			cfg.mx.msgErr37()
			return 'No'
		# earth sun distance
		if len(cfg.ui.earth_sun_dist_lineEdit_2.text()) > 0:
			try:
				self.eSD = float(cfg.ui.earth_sun_dist_lineEdit_2.text())
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' No earth sun distance error')
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
				cfg.mx.msgErr37()
				return 'No'
		dt = cfg.ui.date_lineEdit_2.text()
		if len(str(self.eSD)) == 0:
			dFmt = '%Y%m%d'
			try:
				self.eSD = cfg.utls.calculateEarthSunDistance(dt, dFmt)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
				cfg.mx.msgErr37()
				return 'No'
		cfg.uiUtls.updateBar(5)	
		l = cfg.ui.ASTER_tableWidget
		# input
		if inputFile.lower().endswith('.hdf'):
			fileNm = cfg.utls.fileNameNoExt(inputFile)
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputFile, cfg.gdalSCP.GA_ReadOnly)
			rDSub = rD.GetSubDatasets()
		out = outputDirectory
		oDir = cfg.utls.makeDirectory(out)
		# name prefix
		pre = 'RT_'
		# input bands
		c = l.rowCount()
		# output raster list
		outputRasterList = []
		outputRasterList2 = []
		outputRasterListT = []
		bandSetNameList = []
		convInputList = []
		convInputList2 = []
		# temperature
		tempInputList = []
		for i in range(0, c):
			if cfg.actionCheck == 'Yes':
				iBand = l.item(i,0).text()
				iBandN = iBand[-2:]
				#  aster bands
				for sb in rDSub:
					inputRaster = None
					nm = sb[0]
					if 'VNIR' in str(nm):
						if '0' + nm[-1:] == iBandN:
							bandName = fileNm + '_' + iBandN
							inputRaster = nm
						elif nm[-2:] == '3N' and iBandN in ['03']:
							bandName = fileNm + '_03'
							inputRaster = nm
					elif 'SWIR' in str(nm):
						if '0' + nm[-1:] == iBandN:
							bandName = fileNm + '_' + iBandN
							inputRaster = nm
					elif 'TIR' in str(nm):
						if nm[-2:] == iBandN:
							bandName = fileNm + '_' + iBandN
							inputRaster = nm
					if inputRaster is not None:
						oNm = pre + iBand + '.tif'
						outputRaster = out + '/' + oNm
						tempRaster = cfg.utls.createTempRasterPath('tif')
						try:
							coeff = float(l.item(i,1).text())
						except:
							coeff = ''
						if bandName[-2:] not in ['10', '11', '12', '13', '14']:
							# conversion
							e = self.ASTER_reflectance(bandName[-2:], coeff)
							if e != 'No':
								bandSetNameList.append(pre + bandName)
								if bandName[-2:] in ['04', '05', '06', '07', '08', '09']:
									try:
										pSize2 = int(l.item(i,2).text())
									except:
										pSize2 = ''
									convInputList2.append([inputRaster, e, outputRaster])
									outputRasterList2.append(outputRaster)
									geotransform2 = (uLX, pSize2, 0, uLY, 0, -pSize2)
								else:
									try:
										pSize = int(l.item(i,2).text())
									except:
										pSize = ''
									convInputList.append([inputRaster, e, outputRaster])
									outputRasterList.append(outputRaster)
									geotransform = (uLX, pSize, 0, uLY, 0, -pSize)
						# thermal bands
						else:
							e = self.ASTERTemperature(bandName[-2:], coeff)
							try:
								pSizeT = int(l.item(i,2).text())
							except:
								pSizeT = ''
							geotransformT = (uLX, pSizeT, 0, uLY, 0, -pSizeT)
							if e != 'No':
								tempInputList.append([inputRaster, e, outputRaster])
								outputRasterListT.append(outputRaster)
		# close GDAL rasters
		rDSub = None
		rD = None
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
		tPMDN = cfg.utls.createTempVirtualRaster(inputList, bandList, 'Yes', 'Yes', 0, self.rSr, 'No', xyResList = [pSize, pSize, float(uLX), float(uLY), float(lRX), float(lRY)], aster = 'Yes')
		# No data value
		if cfg.ui.nodata_checkBox_5.isChecked() is True:
			NoData = cfg.ui.nodata_spinBox_6.value()
		else:
			NoData = cfg.NoDataVal
		# DOS 1
		if cfg.ui.DOS1_checkBox_2.isChecked() is True:
			LDNmList = cfg.utls.findDNmin(tPMDN, NoData)
			argumentList = []
			for dnM in range(0, len(LDNmList)):
				e = functionList[dnM].replace('LDNm', str(LDNmList[dnM]))
				argumentList.append(e)
		else:
			argumentList = functionList
		oM = cfg.utls.createTempRasterList(len(inputList))
		# open input with GDAL
		rD = cfg.gdalSCP.Open(tPMDN, cfg.gdalSCP.GA_ReadOnly)
		# output rasters
		cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0,  None, compress = cfg.rasterCompression, compressFormat = 'LZW', projection = self.rSr, geotransform = geotransform)
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
		if len(convInputList2) > 0:
			# conversion
			inputList = []
			functionList = []
			variableList = []
			bandList = []
			for inP in convInputList2:
				inputList.append(inP[0])
				functionList.append(inP[1])	
				variableList.append(['"raster"', '"raster"'])
				bandList.append(1)
			tPMDN = cfg.utls.createTempVirtualRaster(inputList, bandList, 'Yes', 'Yes', 0, self.rSr, 'No', xyResList = [pSize2, pSize2, float(uLX), float(uLY), float(lRX), float(lRY)], aster = 'Yes')
			# No data value
			if cfg.ui.nodata_checkBox_5.isChecked() is True:
				NoData = cfg.ui.nodata_spinBox_6.value()
			else:
				NoData = cfg.NoDataVal
			# DOS 1
			if cfg.ui.DOS1_checkBox_2.isChecked() is True:
				LDNmList = cfg.utls.findDNmin(tPMDN, NoData)
				argumentList = []
				for dnM in range(0, len(LDNmList)):
					e = functionList[dnM].replace('LDNm', str(LDNmList[dnM]))
					argumentList.append(e)
			else:
				argumentList = functionList
			oM = cfg.utls.createTempRasterList(len(inputList))
			# open input with GDAL
			rD = cfg.gdalSCP.Open(tPMDN, cfg.gdalSCP.GA_ReadOnly)
			# output rasters
			cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0,  None, compress = cfg.rasterCompression, compressFormat = 'LZW', projection = self.rSr, geotransform = geotransform2)
			rD = None
			o = cfg.utls.multiProcessRaster(rasterPath = tPMDN, functionBand = 'No', functionRaster = cfg.utls.calculateRaster, outputRasterList = oM, nodataValue = NoData, functionBandArgument = argumentList, functionVariable = variableList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion'), parallel = cfg.parallelRaster)
			if cfg.actionCheck == 'Yes':
				for t in range(0, len(outputRasterList2)):
					cfg.shutilSCP.move(oM[t], outputRasterList2[t])
				# load raster bands
				for outR in outputRasterList2:
					if cfg.osSCP.path.isfile(outR):
						cfg.utls.addRasterLayer(outR)
					else:
						cfg.mx.msgErr38(outR)
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'WARNING: unable to load raster' + str(outR))
		if len(tempInputList) > 0:
			# conversion
			inputList = []
			functionList = []
			variableList = []
			bandList = []
			for inP in tempInputList:
				inputList.append(inP[0])
				functionList.append(inP[1])
				variableList.append(['"raster"', '"raster"'])
				bandList.append(1)
			tPMDN = cfg.utls.createTempVirtualRaster(inputList, bandList, 'Yes', 'Yes', 0, self.rSr, 'No', xyResList = [pSizeT, pSizeT, float(uLX), float(uLY), float(lRX), float(lRY)], aster = 'Yes')
			# No data value
			if cfg.ui.nodata_checkBox_5.isChecked() is True:
				NoData = cfg.ui.nodata_spinBox_6.value()
			else:
				NoData = cfg.NoDataVal
			argumentList = functionList
			oM = cfg.utls.createTempRasterList(len(inputList))
			# open input with GDAL
			rD = cfg.gdalSCP.Open(tPMDN, cfg.gdalSCP.GA_ReadOnly)
			# output rasters
			cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0,  None, compress = cfg.rasterCompression, compressFormat = 'LZW', projection = self.rSr, geotransform = geotransformT)
			rD = None
			o = cfg.utls.multiProcessRaster(rasterPath = tPMDN, functionBand = 'No', functionRaster = cfg.utls.calculateRaster, outputRasterList = oM, nodataValue = NoData, functionBandArgument = argumentList, functionVariable = variableList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion'), parallel = cfg.parallelRaster)
			if cfg.actionCheck == 'Yes':
				for t in range(0, len(outputRasterListT)):
					cfg.shutilSCP.move(oM[t], outputRasterListT[t])
				# load raster bands
				for outR in outputRasterListT:
					if cfg.osSCP.path.isfile(outR):
						cfg.utls.addRasterLayer(outR)
					else:
						cfg.mx.msgErr38(outR)
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'WARNING: unable to load raster' + str(outR))
			# create band set
			if cfg.ui.create_bandset_checkBox.isChecked() is True:
				if cfg.ui.add_new_bandset_checkBox_4.isChecked() is True:
					bandSetNumber = cfg.bst.addBandSetTab()
				cfg.bst.rasterBandName()
				cfg.bst.setBandSet(bandSetNameList, bandSetNumber, dt[:4]+'-'+dt[4:6]+'-'+dt[6:8])
				cfg.bandSetsList[bandSetNumber][0] = 'Yes'
				cfg.bst.setSatelliteWavelength(cfg.satASTER, None, bandSetNumber)
			cfg.bst.bandSetTools(out)
			cfg.uiUtls.updateBar(100)
		if batch == 'No':
			cfg.utls.finishSound()
			cfg.utls.sendSMTPMessage(None, str(__name__))
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()
				
	# conversion to Reflectance
	def ASTER_reflectance(self, bandNumber, conversionCoefficient):
		m = float(conversionCoefficient)
		# Esun
		dEsunB = {}
		# Esun from Michael P. Finn, Matthew D. Reed, and Kristina H. Yamamoto (2012). A Straight Forward Guide for Processing Radiance and Reflectance for EO-1 ALI, Landsat 5 TM, Landsat 7 ETM+, and ASTER    
		dEsunB = {'ESUN_BAND01': 1848, 'ESUN_BAND02': 1549, 'ESUN_BAND03': 1114, 'ESUN_BAND04': 225.4, 'ESUN_BAND05': 86.63, 'ESUN_BAND06': 81.85, 'ESUN_BAND07': 74.85, 'ESUN_BAND08': 66.49, 'ESUN_BAND09': 59.85}
		eS = float(dEsunB['ESUN_BAND' + str(bandNumber)])
		# No data value
		if cfg.ui.nodata_checkBox_5.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_6.value()
		else:
			nD = cfg.NoDataVal
		# TOA reflectance
		if cfg.ui.DOS1_checkBox_2.isChecked() is False:
			e = 'cfg.np.clip(cfg.np.where("raster" == ' + str(nD) + ', ' + str(cfg.NoDataVal) + ', (  ("raster" - 1 ) *' + str('%.16f' % m) + ' * ' + str('%.16f' % cfg.np.pi) + ' * ' + str('%.16f' % self.eSD) + ' * ' + str('%.16f' % self.eSD) + ') / ( ' + str('%.16f' % eS)+ ' * (' + str(self.sA) + ') ) ), 0, 1)'
		# DOS atmospheric correction
		else:
			e = 'cfg.np.where("raster" == ' + str(nD) + ', ' + str(cfg.NoDataVal) + ', ( ("raster" - 1) * ' + str('%.16f' % m) + ') )'
			# path radiance Lp = ML* DNm + AL  – 0.01* ESUN * coss / (π * d^2)	
			Lp = str(m) + ' * (LDNm - 1) - ' + str(0.01 * eS * self.sA / (cfg.np.pi * self.eSD * self.eSD))
			# land surface reflectance r = [π * (L - Lp) * d^2]/ (ESUN * coss)
			e = 'cfg.np.clip(( ' + e +' - (' + str(Lp) + ') ) * ' + str('%.16f' % cfg.np.pi) + ' * ' + str('%.16f' % self.eSD) + ' * ' + str('%.16f' % self.eSD) + ' / ( ' + str('%.16f' % eS)+ ' * (' + str(self.sA) + ') ), 0, 1)'
		return e
					
	# ASTER temperature
	def ASTERTemperature(self, bandNumber, conversionCoefficient):
		# No data value
		if cfg.ui.nodata_checkBox_5.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_6.value()
		else:
			nD = cfg.NoDataVal
		# K1 = c1 /(lambda^5) and K2 = c2/lambda
		# where c1 and c2 are first and second radiation constants from CODATA Recommended Values of the Fundamental Physical Constants: 2014
		if int(bandNumber) == 10:
			# k1 and k2
			k1 = 3.0236879000387607831e3
			k2 = 1.73346669879518072289e3
		elif int(bandNumber) == 11:
			# k1 and k2
			k1 = 2.45950033786752380082e3
			k2 = 1.66332642774566473988e3
		elif int(bandNumber) == 12:
			# k1 and k2
			k1 = 1.9086243591011446439e3
			k2 = 1.58107402197802197802e3
		elif int(bandNumber) == 13:
			# k1 and k2
			k1 = 8.90016580863773201879e2
			k2 = 1.35733713207547169811e3
		elif int(bandNumber) == 14:
			# k1 and k2
			k1 = 6.4645039694287387514e2
			k2 = 1.27325430088495575221e3
		# Kelvin or cs
		cs = 0
		if cfg.ui.celsius_checkBox_2.isChecked() is True:
			cs = 273.15
		# At-Satellite Brightness Temperature
		m = float(conversionCoefficient)
		e = 'cfg.np.where("raster" == ' + str(nD) + ', ' + str(cfg.NoDataVal) + ', ((' + str('%.16f' % k2) + ') / ( ln( (' + str('%.16f' % k1) + ' / ( ("raster" - 1 ) * ' + str('%.16f' % m) + ') ) + 1)) - ' + str(cs) + ') )'
		return e

	# ASTER correction button
	def performASTERCorrection(self):
		if len(cfg.ui.label_143.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.ASTER(cfg.ui.label_143.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Perform ASTER correction: ' + str(cfg.ui.label_143.text()))
		
	# populate table
	def populateTable(self, input, batch = 'No'):
		check = 'Yes'
		dt = ''
		sE = ''
		esd = ''
		cfg.ui.date_lineEdit_2.setText(dt)
		cfg.ui.sun_elev_lineEdit_2.setText(sE)
		cfg.ui.earth_sun_dist_lineEdit_2.setText(esd)
		l = cfg.ui.ASTER_tableWidget
		cfg.utls.setColumnWidthList(l, [[0, 250]])
		cfg.utls.clearTable(l)
		if len(input) == 0:
			cfg.mx.msg14()
		else:
			if batch == 'No':
				cfg.uiUtls.addProgressBar()
			# bands
			dBs = {}
			dGains = {}
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
						if 'CALENDARDATE' in metadata:
							dt = metadata.split('=')[1]
						elif 'SOLARDIRECTION' in metadata:
							sD = metadata.split('=')[1]
							sE = sD.split(',')[1]
						elif 'UTMZONECODE' in metadata:
							utm = metadata.split('=')[1]
						elif 'UPPERLEFTM' in metadata:
							uLM = metadata.split('=')[1]
						elif 'LOWERRIGHTM' in metadata:
							lRM = metadata.split('=')[1]
						elif 'GAIN' in metadata:
							g = metadata.split('=')[1]
							if g.split(',')[0] == '01':
								if g.split(',')[1].strip() == 'HGH':
									v  = 0.676
								elif g.split(',')[1].strip() == 'NOR':
									v  = 1.688 
								elif g.split(',')[1].strip() == 'LOW':
									v  = 2.25
								else:
									v = 'No'
								dGains['BAND_' + g.split(',')[0]] = v
							elif g.split(',')[0] == '02':
								if g.split(',')[1].strip() == 'HGH':
									v  = 0.708
								elif g.split(',')[1].strip() == 'NOR':
									v  = 1.415
								elif g.split(',')[1].strip() == 'LOW':
									v  = 1.89
								else:
									v = 'No'
								dGains['BAND_' + g.split(',')[0]] = v
							elif g.split(',')[0] == '3N':
								if g.split(',')[1].strip() == 'HGH':
									v  = 0.423 
								elif g.split(',')[1].strip() == 'NOR':
									v  = 0.862
								elif g.split(',')[1].strip() == 'LOW':
									v  = 1.15
								else:
									v = 'No'	
								dGains['BAND_03']  = v
							elif g.split(',')[0] == '04':
								if g.split(',')[1].strip() == 'HGH':
									v  = 0.1087
								elif g.split(',')[1].strip() == 'NOR':
									v  = 0.2174
								elif g.split(',')[1].strip() == 'LO1':
									v  = 0.290
								elif g.split(',')[1].strip() == 'LO2':
									v  = 0.290
								else:
									v = 'No'
								dGains['BAND_' + g.split(',')[0]] = v
							elif g.split(',')[0] == '05':
								if g.split(',')[1].strip() == 'HGH':
									v  = 0.0348
								elif g.split(',')[1].strip() == 'NOR':
									v  = 0.0696
								elif g.split(',')[1].strip() == 'LO1':
									v  = 0.0925
								elif g.split(',')[1].strip() == 'LO2':
									v  = 0.409
								else:
									v = 'No'
								dGains['BAND_' + g.split(',')[0]] = v
							elif g.split(',')[0] == '06':
								if g.split(',')[1].strip() == 'HGH':
									v  = 0.0313
								elif g.split(',')[1].strip() == 'NOR':
									v  = 0.0625
								elif g.split(',')[1].strip() == 'LO1':
									v  = 0.0830
								elif g.split(',')[1].strip() == 'LO2':
									v  = 0.390
								else:
									v = 'No'
								dGains['BAND_' + g.split(',')[0]] = v
							elif g.split(',')[0] == '07':
								if g.split(',')[1].strip() == 'HGH':
									v  = 0.0299
								elif g.split(',')[1].strip() == 'NOR':
									v  = 0.0597
								elif g.split(',')[1].strip() == 'LO1':
									v  = 0.0795
								elif g.split(',')[1].strip() == 'LO2':
									v  = 0.332
								else:
									v = 'No'
								dGains['BAND_' + g.split(',')[0]] = v
							elif g.split(',')[0] == '08':
								if g.split(',')[1].strip() == 'HGH':
									v  = 0.0209
								elif g.split(',')[1].strip() == 'NOR':
									v  = 0.0417
								elif g.split(',')[1].strip() == 'LO1':
									v  = 0.0556
								elif g.split(',')[1].strip() == 'LO2':
									v  = 0.245
								else:
									v = 'No'
								dGains['BAND_' + g.split(',')[0]] = v
							elif g.split(',')[0] == '09':
								if g.split(',')[1].strip() == 'HGH':
									v  = 0.0159
								elif g.split(',')[1].strip() == 'NOR':
									v  = 0.0318
								elif g.split(',')[1].strip() == 'LO1':
									v  = 0.0424
								elif g.split(',')[1].strip() == 'LO2':
									v  = 0.265
								else:
									v = 'No'
								dGains['BAND_' + g.split(',')[0]] = v
							dGains['BAND_' + '10'] = 0.006822
							dGains['BAND_' + '11'] = 0.006780
							dGains['BAND_' + '12'] = 0.006590
							dGains['BAND_' + '13'] = 0.005693
							dGains['BAND_' + '14'] = 0.005225
					# date format
					dFmt = '%Y%m%d'
					try:
						esd = str(cfg.utls.calculateEarthSunDistance(dt, dFmt))
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					try:
						cfg.ui.date_lineEdit_2.setText(dt)
						cfg.ui.sun_elev_lineEdit_2.setText(sE)
						cfg.ui.earth_sun_dist_lineEdit_2.setText(esd)
						cfg.ui.utm_zone_lineEdit.setText(utm)
						cfg.ui.ulm_lineEdit.setText(uLM)
						cfg.ui.lrm_lineEdit.setText(lRM)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
						if batch == 'No':
							cfg.uiUtls.removeProgressBar()
						return
					rDSub = rD.GetSubDatasets()
					#  aster bands
					for sb in rDSub:
						nm = sb[0]
						if 'VNIR' in str(nm):
							sbD = cfg.gdalSCP.Open(str(nm))
							if nm[-1:].isdigit() :
								dBs['BAND_0{0}'.format(nm[-1:])] = 15
								bandNames.append(fileNm + '_0' + nm[-1:])
							elif nm[-2:] == '3N':
								dBs['BAND_03'] = 15
								bandNames.append(fileNm + '_03')
						elif 'SWIR' in str(nm):
							sbD = cfg.gdalSCP.Open(str(nm))
							if nm[-1:].isdigit() :
								dBs['BAND_0{0}'.format(nm[-1:])] = 30
								bandNames.append(fileNm + '_0' + nm[-1:])
						elif 'TIR' in str(nm):
							sbD = cfg.gdalSCP.Open(str(nm))
							if nm[-2:].isdigit() :
								dBs['BAND_{0}'.format(nm[-2:])] = 90
								bandNames.append(fileNm + '_' + nm[-2:])
			# add band items to table
			b = 0
			for band in sorted(bandNames):				
				l.insertRow(b)
				l.setRowHeight(b, 20)
				cfg.utls.addTableItem(l, band, b, 0, 'No')
				try:
					cfg.utls.addTableItem(l, str(dGains['BAND_' + band[-2:]]), b, 1)
					cfg.utls.addTableItem(l, dBs['BAND_' + band[-2:]], b, 2)
				except:
					pass
				b = b + 1
			if batch == 'No':
				cfg.uiUtls.removeProgressBar()			

	def editedCell(self, row, column):
		if column != 0:
			l = cfg.ui.ASTER_tableWidget
			val = l.item(row, column).text()
			try:
				float(val)
			except:
				l.item(row, column).setText('')
	
	# earth sun distance
	def editedEarthSunDist(self):
		try:
			float(cfg.ui.earth_sun_dist_lineEdit_2.text())
		except:
			cfg.ui.earth_sun_dist_lineEdit_2.setText('')
			
	# sun elevation
	def editedSunElevation(self):
		try:
			float(cfg.ui.sun_elev_lineEdit_2.text())
		except:
			cfg.ui.sun_elev_lineEdit_2.setText('')
			
	def editedDate(self):
		dFmt = '%Y%m%d'
		dt = cfg.ui.date_lineEdit_2.text()
		try:
			cfg.utls.calculateEarthSunDistance(dt, dFmt)
			cfg.ui.date_lineEdit_2.setStyleSheet('color : black')
		except:
			cfg.ui.date_lineEdit_2.setStyleSheet('color : red')
		
	def removeHighlightedBand(self):
		l = cfg.ui.ASTER_tableWidget
		cfg.utls.removeRowsFromTable(l)
		