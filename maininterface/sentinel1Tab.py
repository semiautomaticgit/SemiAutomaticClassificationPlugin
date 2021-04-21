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

class Sentinel1Tab:

	def __init__(self):
		pass
		
	# Sentinel-1 input
	def inputSentinel(self):
		i = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a Sentinel-1 file'), '', 'Sentinel-1 file .zip (*.zip)')
		cfg.ui.S1_label_87.setText(str(i))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), str(i))
		
	# XML input 
	def inputXML(self):
		m = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a XML file'), '', 'XML file .xml (*.xml)')
		cfg.ui.S1_label_96.setText(str(m))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), str(m))
			
	# sentinel-1 output
	def performSentinelConversion(self):
		if len(cfg.ui.S1_label_87.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.sentinel1(cfg.ui.S1_label_87.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Perform sentinel-1 conversion: ' + str(cfg.ui.S1_label_87.text()))
		
	# sentinel-1 conversion
	def sentinel1(self, inputFile, outputDirectory, batch = 'No', bandSetNumber = None, xmlGPT = None):
		# gpt executable
		if not cfg.osSCP.path.isfile(cfg.SNAPGPT):
			gpt = cfg.snap.findSNAPGPT()
			if gpt == 'No':
				return 'No'
		cfg.uiUtls.addProgressBar()
		# disable map canvas render for speed
		if batch == 'No':
			cfg.cnvs.setRenderFlag(False)
		if xmlGPT is None:
			xml = cfg.ui.S1_label_96.text()
			xmlVVVH = xml
			if str(xml) == '':
				xml = cfg.plgnDir + '/modules/snap/S1_process.xml' 
				xmlVVVH = cfg.plgnDir + '/modules/snap/S1_process_VVVH.xml' 
		else:
			xml = xmlGPT
			xmlVVVH = xmlGPT
		cfg.uiUtls.updateBar(5)	
		inp = inputFile
		out = outputDirectory
		cfg.utls.makeDirectory(out)		
		# output raster list
		outputRasterList = []
		# band list
		bandSetList = []
		bandSetNameList = []
		bandNumberList = []
		# SNAP conversion
		if cfg.actionCheck == 'Yes':
			if cfg.ui.VH_checkBox_S1.isChecked() is True and cfg.ui.VV_checkBox_S1.isChecked() is True:
				cfg.uiUtls.updateBar(30, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion') + ' ' + inputFile)
				tVH, tVV, date = self.processGPT(inp, out, xmlVVVH, 'VVVH')
				outputRasterList.append(tVH)
				bandSetList.append(1)
				outputRasterList.append(tVV)
				bandSetList.append(2)
				bandSetNameList.append(cfg.utls.fileNameNoExt(tVH))
				bandSetNameList.append(cfg.utls.fileNameNoExt(tVV))
			elif cfg.ui.VH_checkBox_S1.isChecked() is True:
				cfg.uiUtls.updateBar(0, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion') + ' ' + inputFile)
				tVH, date = self.processGPT(inp, out, xml, 'VH')
				outputRasterList.append(tVH)
				bandSetList.append(1)
				bandSetNameList.append(cfg.utls.fileNameNoExt(tVH))
			elif cfg.ui.VV_checkBox_S1.isChecked() is True:
				cfg.uiUtls.updateBar(50, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion') + ' ' + inputFile)
				tVV, date = self.processGPT(inp, out, xml, 'VV')
				outputRasterList.append(tVV)
				bandSetList.append(2)
				bandSetNameList.append(cfg.utls.fileNameNoExt(tVV))
			cfg.uiUtls.updateBar(90)
			if cfg.actionCheck == 'Yes':
				# load raster bands
				check = 'Yes'
				for outR in outputRasterList:
					if cfg.osSCP.path.isfile(outR):
						cfg.utls.addRasterLayer(outR)
					else:
						cfg.mx.msgErr38(outR)
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'WARNING: unable to load raster' + str(outR))
						check = 'No'
				# create band set
				if cfg.ui.S1_create_bandset_checkBox.isChecked() is True and check == 'Yes':
					satName = cfg.satSentinel1
					if cfg.ui.add_new_bandset_checkBox_6.isChecked() is True:
						if bandSetNumber is None:
							bandSetNumber = cfg.bst.addBandSetTab()
						elif bandSetNumber >= len(cfg.bandSetsList):
								bandSetNumber = cfg.bst.addBandSetTab()
					cfg.bst.rasterBandName()
					bandSetNameList = sorted(bandSetNameList)
					bandSetNameList = [list for (number, list) in sorted(zip(bandSetList, bandSetNameList))]
					cfg.bst.setBandSet(bandSetNameList, bandSetNumber, date)
					cfg.bandSetsList[bandSetNumber][0] = 'Yes'
					bandSetList = sorted(bandSetList)
					cfg.bst.setSatelliteWavelength(satName, bandSetList, bandSetNumber)
				cfg.bst.bandSetTools(out)
			cfg.uiUtls.updateBar(100)
		if batch == 'No':
			cfg.utls.finishSound()
			cfg.utls.sendSMTPMessage(None, str(__name__))
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()

	# process GPT
	def processGPT(self, inputRaster, outputDirectory, xmlFile, polarization):
		# date time for temp name
		dT = cfg.utls.getTime()
		tVsnap = cfg.utls.createTempRasterPath('tif')
		tVsnap2 = cfg.utls.createTempRasterPath('tif')
		# get orbit
		try:
			with cfg.zipfileSCP.ZipFile(inputRaster) as zOpen:
				for flName in zOpen.namelist():
					zipF = zOpen.open(flName)
					fileName = cfg.utls.fileName(flName)
					if fileName.lower() == 'manifest.safe':
						zipO = open(cfg.tmpDir + '/' + dT + fileName, 'wb')
						with zipF, zipO:
							cfg.shutilSCP.copyfileobj(zipF, zipO)
						zipO.close()
						break
			doc = cfg.minidomSCP.parse(cfg.tmpDir + '/' + dT + fileName)
			entries = doc.getElementsByTagName('s1:pass')
			for entry in entries:
				orbit = entry.firstChild.data
			entries2 = doc.getElementsByTagName('safe:relativeOrbitNumber')
			for entry2 in entries2:
				relativeOrbit = entry2.firstChild.data
			try:
				entries3 = doc.getElementsByTagName('s1sarl1:sliceNumber')
				for entry3 in entries3:
					sliceNumber = entry3.firstChild.data
			except:
				sliceNumber = ''
			try:
				entries4 = doc.getElementsByTagName('safe:number')
				for entry4 in entries4:
					satelliteN = str(entry4.firstChild.data)
			except:
				satelliteN = ''
			try:
				entries5 = doc.getElementsByTagName('safe:startTime')
				for entry5 in entries5:
					date = entry5.firstChild.data
			except:
				date = ''
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No', ''
		if polarization == 'VVVH':
			outputRasterVV = outputDirectory + '/grd' + date.split('T')[0] + '_s' + orbit[0] + '_' + satelliteN + 'o' + relativeOrbit + '_' + satelliteN + 's' + sliceNumber + '_' + 'VV' + '.tif'
			outputRasterVH = outputDirectory + '/grd' + date.split('T')[0] + '_s' + orbit[0] + '_' + satelliteN + 'o' + relativeOrbit + '_' + satelliteN + 's' + sliceNumber + '_' + 'VH' + '.tif'
			d = '"' + cfg.SNAPGPT + '" -q ' + str(cfg.threads) + ' -c ' + str(cfg.RAMValue) + 'M "' + xmlFile + '" -Pinput="' + inputRaster + '" -PoutputVH="' + tVsnap + '" -PoutputVV="' + tVsnap2 + '"'
            # logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' S1 d: ' + d)
			if cfg.sysSCPNm != 'Windows':
				d = cfg.shlexSCP.split(d)
			tPMD = cfg.utls.createTempRasterPath('txt')
			stF = open(tPMD, 'a')
			sPL = len(cfg.subprocDictProc)
			# issue on Windows
			if cfg.sysSCPNm == 'Windows':
				startupinfo = cfg.subprocessSCP.STARTUPINFO()
				startupinfo.dwFlags = cfg.subprocessSCP.STARTF_USESHOWWINDOW
				startupinfo.wShowWindow = cfg.subprocessSCP.SW_HIDE
				cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(d, shell=False, startupinfo = startupinfo, stdout=stF, stdin = cfg.subprocessSCP.DEVNULL)
			else:
				cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(d, shell=False, stdout=stF)
			progress = 0
			while True:
				line = ''
				with open(tPMD, 'r') as rStF:
					for line in rStF:
						pass
				poll = cfg.subprocDictProc['proc_'+ str(sPL)].poll()
				if poll != None:
					break
				else:
					try:
						progress = int(line.replace('.','').split('%')[-2])
						try:
							dots = dots + '.'
							if len(dots) > 3:
								dots = ''
						except:
							dots = ''
						cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion') + inputRaster + dots)
					except:
						try:
							dots = dots + '.'
							if len(dots) > 3:
								dots = ''
						except:
							dots = ''
						cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion') + dots)
				cfg.QtWidgetsSCP.qApp.processEvents()
				if cfg.actionCheck != 'Yes':	
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' error: cancel')
					return 'No', '', ''
				cfg.timeSCP.sleep(1)
			stF.close()
			# get error
			out, err = cfg.subprocDictProc['proc_'+ str(sPL)].communicate()
			if err is not None:
				if len(err) > 0:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' error: ' + str(err))
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image: ' + str(tVsnap))
			self.processS1toDB(tVsnap, outputRasterVH)
			self.processS1toDB(tVsnap2, outputRasterVV)
			# remove temp
			try:
				cfg.osSCP.remove(tVsnap)
			except:
				pass
			try:
				cfg.osSCP.remove(tVsnap2)
			except:
				pass
			return outputRasterVH, outputRasterVV, date.split('T')[0]
		else:
			outputRaster = outputDirectory + '/grd' + date.split('T')[0] + '_s' + orbit[0] + '_' + satelliteN + 'o' + relativeOrbit + '_' + satelliteN + 's' + sliceNumber + '_' + polarization + '.tif'
			d = '"' + cfg.SNAPGPT + '" -q ' + str(cfg.threads) + ' -c ' + str(cfg.RAMValue) + 'M "' + xmlFile + '" -Pinput="' + inputRaster + '" -Poutput="' + tVsnap + '" -Ppolarization=' + polarization
            # logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' S1 d: ' + d)
			if cfg.sysSCPNm != 'Windows':
				d = cfg.shlexSCP.split(d)
			tPMD = cfg.utls.createTempRasterPath('txt')
			stF = open(tPMD, 'a')
			sPL = len(cfg.subprocDictProc)
			# issue on Windows
			if cfg.sysSCPNm == 'Windows':
				startupinfo = cfg.subprocessSCP.STARTUPINFO()
				startupinfo.dwFlags = cfg.subprocessSCP.STARTF_USESHOWWINDOW
				startupinfo.wShowWindow = cfg.subprocessSCP.SW_HIDE
				cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(d, shell=False, startupinfo = startupinfo, stdout=stF, stdin = cfg.subprocessSCP.DEVNULL)
			else:
				cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(d, shell=False, stdout=stF)
			progress = 0
			while True:
				line = ''
				with open(tPMD, 'r') as rStF:
					for line in rStF:
						pass
				poll = cfg.subprocDictProc['proc_'+ str(sPL)].poll()
				if poll != None:
					break
				else:
					try:
						progress = int(line.replace('.','').split('%')[-2])
						try:
							dots = dots + '.'
							if len(dots) > 3:
								dots = ''
						except:
							dots = ''
						cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion') + inputRaster + dots)
					except:
						try:
							dots = dots + '.'
							if len(dots) > 3:
								dots = ''
						except:
							dots = ''
						cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion') + dots)
				cfg.QtWidgetsSCP.qApp.processEvents()
				if cfg.actionCheck != 'Yes':	
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' error: cancel')
					return 'No', ''
				cfg.timeSCP.sleep(1)
			stF.close()
			# get error
			out, err = cfg.subprocDictProc['proc_'+ str(sPL)].communicate()
			if err is not None:
				if len(err) > 0:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' error: ' + str(err))
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image: ' + str(tVsnap))
			self.processS1toDB(tVsnap, outputRaster)
			# remove temp
			try:
				cfg.osSCP.remove(tVsnap)
			except:
				pass
			return outputRaster, date.split('T')[0]
			
	# process db
	def processS1toDB(self, inputRaster, outputRaster):
		bandSetNumber = cfg.ui.band_set_comb_spinBox_11.value() - 1
		# No data value
		if cfg.ui.S1_nodata_checkBox.isChecked() is True:
			nD = cfg.ui.S1_nodata_spinBox.value()
			e = 'cfg.np.where("raster" == ' + str(nD) + ", " + str(cfg.NoDataVal) + ', ("raster") )'
		else:
			nD = None
			e = '("raster")'
		if cfg.ui.convert_to_db_checkBox.isChecked() is True:
			e = e.replace('("raster")', '10 * cfg.np.log10("raster")' )
		# reproject
		reproject = 'No'
		if cfg.ui.projection_checkBox_S1.isChecked() is True:
			rEPSG = None
			# band set
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				try:
					b = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][3][0], 'Yes')
					rast = cfg.utls.layerSource(b)
					# image EPSG
					rCrs = cfg.utls.getCrsGDAL(rast)
					rEPSG = cfg.osrSCP.SpatialReference()
					rEPSG.ImportFromWkt(rCrs)
				except:
					cfg.mx.msgWar25(str(bandSetNumber + 1))
			else:
				b = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8])
				rast = cfg.utls.layerSource(b)
				rCrs = cfg.utls.getCrsGDAL(rast)
				rEPSG = cfg.osrSCP.SpatialReference()
				rEPSG.ImportFromWkt(rCrs)
			eCrs = cfg.utls.getCrsGDAL(inputRaster)
			EPSG = cfg.osrSCP.SpatialReference()
			EPSG.ImportFromWkt(eCrs)
			if EPSG.IsSame(rEPSG) != 1:
				if nD is None:
					nD = cfg.NoDataVal
				reproject = 'Yes'
		variableList = []
		# conversion
		if e != '("raster")':
			if cfg.outTempRastFormat == 'VRT' and reproject == 'Yes':
				tPMD1 = cfg.utls.createTempRasterPath('vrt')
				vrtR = 'Yes'
			else:
				tPMD1 = cfg.utls.createTempRasterPath('tif')
				vrtR = 'No'
			oM = tPMD1
			variableList.append(['"raster"', '"raster"'])
			try:
				o = cfg.utls.multiProcessRaster(rasterPath = inputRaster, functionBand = 'No', functionRaster = cfg.utls.bandCalculation, outputRasterList = [tPMD1], nodataValue = nD, functionBandArgument = e, functionVariable = variableList, progressMessage = 'Conversion ', virtualRaster = vrtR, compress = cfg.rasterCompression, compressFormat = 'LZW')
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
		else:
			oM = inputRaster
		# reprojection
		if reproject == 'Yes':
			tPMD2 = cfg.utls.createTempRasterPath('tif')
			cfg.utls.GDALReprojectRaster(input = oM, output = tPMD2, outFormat = 'GTiff', s_srs = None, t_srs = 'EPSG:' + str(rEPSG), rasterDataType = 'Float32', noDataVal = nD)
			# remove temp
			try:
				cfg.osSCP.remove(oM)
			except:
				pass
			oM = tPMD2
		try:
			cfg.shutilSCP.move(oM, outputRaster)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# remove temp
		try:
			cfg.osSCP.remove(tPMD1)
		except:
			pass
		for tRL in cfg.tmpList:
			try:
				cfg.osSCP.remove(tRL)
			except:
				pass
		return outputRaster
				