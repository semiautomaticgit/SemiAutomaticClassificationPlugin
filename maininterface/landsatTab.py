# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2018 by Luca Congedo
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

"""


cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

class LandsatTab:

	def __init__(self):
		pass
		
	# landsat input
	def inputLandsat(self):
		i = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		cfg.ui.label_26.setText(str(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(i))
		
	# MTL input
	def inputMTL(self):
		m = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a MTL file"), "", "MTL file .txt (*.txt);;MTL file .met (*.met)")
		cfg.ui.label_27.setText(str(m))
		if len(cfg.ui.label_26.text()) > 0:
			self.populateTable(cfg.ui.label_26.text())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(m))

	# landsat conversion to reflectance and temperature
	def landsat(self, inputDirectory, outputDirectory, batch = "No", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		if batch == "No":
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
		self.sA = ""
		self.eSD = ""
		sat = cfg.ui.satellite_lineEdit.text()
		if str(sat) == "":
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No satellite error")
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
			cfg.mx.msgErr37()
			return "No"
		if len(cfg.ui.sun_elev_lineEdit.text()) > 0:
			sE = float(cfg.ui.sun_elev_lineEdit.text())
			# sine sun elevation
			self.sA = cfg.np.sin(sE * cfg.np.pi / 180)
		else:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No sun elevation error")
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
			cfg.mx.msgErr37()
			return "No"
		# earth sun distance
		if len(cfg.ui.earth_sun_dist_lineEdit.text()) > 0:
			try:
				self.eSD = float(cfg.ui.earth_sun_dist_lineEdit.text())
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No earth sun distance error")
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
				cfg.mx.msgErr37()
				return "No"
		if len(str(self.eSD)) == 0:
			dFmt = "%Y-%m-%d"
			dt = cfg.ui.date_lineEdit.text()
			try:
				self.eSD = cfg.utls.calculateEarthSunDistance(dt, dFmt)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
				cfg.mx.msgErr37()
				return "No"
		cfg.uiUtls.updateBar(5)	
		l = cfg.ui.landsat_tableWidget
		inp = inputDirectory
		out = outputDirectory
		cfg.utls.makeDirectory(out)
		# name prefix
		pre = "RT_"
		prePAN = "PAN_"
		# input bands
		c = l.rowCount()
		# date time for temp name
		dT = cfg.utls.getTime()
		# temp raster
		tempRasterList = []
		# output raster list
		outputRasterList = []
		# multispectral raster list
		rasterList = []
		# band list
		bandSetList = []
		bandSetNameList = []
		bandNumberList = []
		bandPansharpList = []
		pansharpRasterList = []
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				inputRaster = inp + "/" + l.item(i,0).text()				
				oNme = pre + l.item(i,0).text()
				oNm, ext = cfg.osSCP.path.splitext(oNme)
				outputRaster = out + "/" + oNme
				outputRasterList.append(outputRaster)
				panRaster = out + "/" + prePAN + l.item(i,0).text()
				tempRaster = cfg.tmpDir + "/" + dT + l.item(i,0).text()
				tempRasterList.append(tempRaster)
				bandName = l.item(i,0).text()
				try:
					REFLECTANCE_MULT = float(l.item(i,3).text())
				except:
					REFLECTANCE_MULT = ""
				try:
					REFLECTANCE_ADD = float(l.item(i,4).text())
				except:
					REFLECTANCE_ADD = ""
				try:
					RADIANCE_MAXIMUM = float(l.item(i,5).text())
				except:
					RADIANCE_MAXIMUM = ""
				try:
					REFLECTANCE_MAXIMUM = float(l.item(i,6).text())
				except:
					REFLECTANCE_MAXIMUM = ""
				try:
					K1_CONSTANT = float(l.item(i,7).text())
				except:
					K1_CONSTANT = ""
				try:
					K2_CONSTANT = float(l.item(i,8).text())
				except:
					K2_CONSTANT = ""
				try:
					LMAX = float(l.item(i,9).text())
				except:
					LMAX = ""
				try:
					LMIN = float(l.item(i,10).text())
				except:
					LMIN = ""
				try:
					QCALMAX = float(l.item(i,11).text())
				except:
					QCALMAX = ""
				try:
					QCALMIN = float(l.item(i,12).text())
				except:
					QCALMIN = ""
				try:
					RADIANCE_MULT = float(l.item(i,1).text())
				except:
					try:
						# for compatibility with glcf images
						RADIANCE_MULT = (LMAX - LMIN) / (QCALMAX - QCALMIN)
					except:
						RADIANCE_MULT = ""
				try:
					RADIANCE_ADD = float(l.item(i,2).text())
				except:
					try:
						# for compatibility with glcf images
						RADIANCE_ADD = LMIN - QCALMIN * (LMAX - LMIN) / (QCALMAX - QCALMIN)
					except:
						RADIANCE_ADD = ""
				nm = cfg.osSCP.path.splitext(bandName)[0]
				# conversion
				if str(sat).lower() in ['landsat_1', 'landsat1','landsat_2', 'landsat2','landsat_3', 'landsat3']:
					# landsat bands (e.g. b4, b4)
					if nm[len(nm) - 1].isdigit():
						ck = self.landsat1_7reflectance(sat, str(nm[len(nm) - 1]), RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
						if ck != "No":
							rasterList.append(outputRaster)
							# band list
							if int(nm[len(nm) - 1]) in [4, 5, 6, 7]:
								bandSetList.append(int(nm[len(nm) - 1]))
								bandSetNameList.append(oNm)
				elif str(sat).lower() in ['landsat_4', 'landsat4', 'landsat_5', 'landsat5', 'landsat_7', 'landsat7']:
					# landsat bands (e.g. b10, b20, b61)
					if nm[len(nm) - 2].isdigit() and nm[len(nm) - 1].isdigit():
						if str(nm[len(nm) - 1]) == "0":
							if str(nm[len(nm) - 2]) == "6":
								self.landsat457Temperature(sat, RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
							else:
								ck = self.landsat1_7reflectance(sat, str(nm[len(nm) - 2]), RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
								if ck != "No":
									rasterList.append(outputRaster)
									# band list
									if int(nm[len(nm) - 2]) in [1, 2, 3, 4, 5]:
										bandSetList.append(int(nm[len(nm) - 2]))
										bandSetNameList.append(oNm)
										bandNumberList.append(int(nm[len(nm) - 2]))
										bandPansharpList.append(outputRaster)
										pansharpRasterList.append(panRaster)
									elif int(nm[len(nm) - 2]) == 8:
										bandNumberList.insert(0, 8)
										bandPansharpList.insert(0, outputRaster)
									elif int(nm[len(nm) - 2]) == 7:
										bandSetList.append(6)
										bandSetNameList.append(cfg.osSCP.path.splitext(oNm)[0])
										bandNumberList.append(int(nm[len(nm) - 2]))
										bandPansharpList.append(outputRaster)
										pansharpRasterList.append(panRaster)
						# landsat thermal bands
						elif str(nm[len(nm) - 2]) == "6":
							self.landsat457Temperature(sat, RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
					# landsat bands (e.g. b1, b2, b6_VCID_1)
					elif str(nm[len(nm) - 8: len(nm) - 1]) != "6_VCID_" and nm[len(nm) - 1].isdigit():
						# landsat thermal bands
						if str(nm[len(nm) -1]) == "6":
							self.landsat457Temperature(sat, RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
						else:
							ck = self.landsat1_7reflectance(sat, str(nm[len(nm) - 1]), RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
							if ck != "No":
								rasterList.append(outputRaster)
								# band list
								if int(nm[len(nm) - 1]) in [1, 2, 3, 4, 5]:
									bandSetList.append(int(nm[len(nm) - 1]))
									bandSetNameList.append(oNm)
									bandNumberList.append(int(nm[len(nm) - 1]))
									bandPansharpList.append(outputRaster)
									pansharpRasterList.append(panRaster)
								elif int(nm[len(nm) - 1]) == 8:
									bandNumberList.insert(0, 8)
									bandPansharpList.insert(0, outputRaster)
								elif int(nm[len(nm) - 1]) == 7:
									bandSetList.append(6)
									bandSetNameList.append(cfg.osSCP.path.splitext(oNm)[0])
									bandNumberList.append(int(nm[len(nm) - 1]))
									bandPansharpList.append(outputRaster)
									pansharpRasterList.append(panRaster)
					# landsat thermal bands
					elif str(nm[len(nm) - 8: len(nm) - 1]) == "6_VCID_" and nm[len(nm) - 1].isdigit():
						self.landsat457Temperature(sat, RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
				elif str(sat).lower() in ['landsat8', 'landsat_8']:
					# landsat thermal bands
					if nm[len(nm) - 2: len(nm) - 0] in ["10", "11"]:
						self.landsat8Temperature(RADIANCE_MULT, RADIANCE_ADD, K1_CONSTANT, K2_CONSTANT, inputRaster, tempRaster)
					# for bands < 10
					elif str(nm[len(nm) - 8: len(nm) - 1]) != "6_VCID_" and nm[len(nm) - 1].isdigit():
						ck = self.landsat8reflectance(sat, str(nm[len(nm) - 1]), REFLECTANCE_MULT, REFLECTANCE_ADD, RADIANCE_MULT, RADIANCE_ADD, RADIANCE_MAXIMUM, REFLECTANCE_MAXIMUM, inputRaster, tempRaster)
						if ck != "No":
							rasterList.append(outputRaster)
							# band list
							if int(nm[len(nm) - 1]) in [2, 3, 4, 5, 6, 7]:
								bandSetList.append(int(nm[len(nm) - 1]) - 1)
								bandSetNameList.append(oNm)
								bandNumberList.append(int(nm[len(nm) - 1]))
								bandPansharpList.append(outputRaster)
								pansharpRasterList.append(panRaster)
							elif int(nm[len(nm) - 1]) == 8:
								bandNumberList.insert(0, 8)
								bandPansharpList.insert(0, outputRaster)
				elif str(sat).lower() in ['landsat_1_sr', 'landsat_2_sr', 'landsat_3_sr', 'landsat_4_sr', 'landsat_5_sr', 'landsat_7_sr', 'landsat_8_sr']:
						ck = self.landsatSurfaceReflectance(sat, str(nm[len(nm) - 1]), REFLECTANCE_MULT, REFLECTANCE_ADD, RADIANCE_MULT, RADIANCE_ADD, RADIANCE_MAXIMUM, REFLECTANCE_MAXIMUM, inputRaster, tempRaster)
						if ck != "No":
							rasterList.append(outputRaster)
							# band list
							if len(bandSetList) > 0:
								bandSetList.append(max(bandSetList) + 1)
							else:
								bandSetList.append(1)
							bandSetNameList.append(oNm)
							bandNumberList.append(int(nm[len(nm) - 1]))
		cfg.uiUtls.updateBar(90)
		if cfg.actionCheck == "Yes":
			# copy raster bands
			bN = 0
			for temp in tempRasterList:
				try:
					cfg.utls.GDALCopyRaster(temp, outputRasterList[bN], "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
					cfg.osSCP.remove(temp)
				except Exception as err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					try:
						cfg.shutilSCP.copy(temp, outputRasterList[bN])
						cfg.osSCP.remove(temp)
					except Exception as err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				bN = bN + 1
		if cfg.actionCheck == "Yes" and cfg.ui.pansharpening_checkBox.isChecked() is True:
			# type Brovey Transform
			panType = cfg.BT_panType
			if bandNumberList[0] == 8:
				panCheck = self.landsat_Pansharp(bandPansharpList, [str(sat).lower(), panType], bandNumberList, pansharpRasterList)
			else:
				cfg.mx.msgErr44()
				panCheck = "No"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Missing bands " + str(bandNumberList))
		if cfg.actionCheck == "Yes":
			# load raster bands
			for outR in outputRasterList:
				if cfg.osSCP.path.isfile(outR):
					cfg.utls.addRasterLayer(outR)
				else:
					cfg.mx.msgErr38(outR)
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "WARNING: unable to load raster" + str(outR))
			if cfg.ui.pansharpening_checkBox.isChecked() is True and panCheck != "No":
				bandSetNameList = []
				rasterList = []
				# load raster bands
				for outR in pansharpRasterList:
					if cfg.osSCP.path.isfile(outR):
						cfg.utls.addRasterLayer(outR)
						bandSetNameList.append(cfg.osSCP.path.splitext(cfg.osSCP.path.basename(outR))[0])
						rasterList.append(outR)
					else:
						cfg.mx.msgErr38(outR)
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "WARNING: unable to load raster" + str(outR))
			# create band set
			if cfg.ui.create_bandset_checkBox.isChecked() is True:
				if str(sat).lower() in ['landsat8', 'landsat_8', 'landsat_8_sr']:
					satName = cfg.satLandsat8
				elif str(sat).lower() in ['landsat_7','landsat_7_sr', 'landsat7']:
					satName = cfg.satLandsat7
				elif str(sat).lower() in ['landsat_4', 'landsat_4_sr', 'landsat4', 'landsat_5', 'landsat_5_sr', 'landsat5']:
					satName = cfg.satLandsat45
				elif str(sat).lower() in ['landsat_1', 'landsat_1_sr', 'landsat1','landsat_2','landsat_2_sr', 'landsat2','landsat_3','landsat_3_sr', 'landsat3']:
					satName = cfg.satLandsat13
				else:
					satName = "No"
				if satName != "No":
					if cfg.ui.add_new_bandset_checkBox_1.isChecked() is True:
						bandSetNumber = cfg.bst.addBandSetTab()
					cfg.bst.rasterBandName()
					cfg.bst.setBandSet(bandSetNameList, bandSetNumber)
					cfg.bandSetsList[bandSetNumber][0] = "Yes"
					if str(sat).lower() in ['landsat_1', 'landsat1','landsat_2', 'landsat2','landsat_3', 'landsat3']:
						cfg.bst.setSatelliteWavelength(satName, None, bandSetNumber)
					else:
						cfg.bst.setSatelliteWavelength(satName, bandSetList, bandSetNumber)
			cfg.bst.bandSetTools(out)
			cfg.uiUtls.updateBar(100)
		if batch == "No":
			cfg.utls.finishSound()
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()

	# landsat 8 conversion to Reflectance
	def landsat8reflectance(self, satellite, bandNumber, REFLECTANCE_MULT_BAND, REFLECTANCE_ADD_BAND, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, RADIANCE_MAXIMUM_BAND, REFLECTANCE_MAXIMUM_BAND, inputRaster, outputRaster):
		DOScheck = "Yes"
		if cfg.ui.DOS1_checkBox.isChecked() is True and cfg.ui.DOS1_bands_checkBox.isChecked() is True:
			if str(bandNumber) in ["1", "2", "3"]:
				DOScheck = "Yes"
			else:
				DOScheck = "No"
		sat = satellite
		x = bandNumber
		# temp files
		dT = cfg.utls.getTime()
		tPMN = cfg.reflectanceRasterNm + ".tif"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		tPMN2 = cfg.reflectanceRasterNm + "2.tif"
		tPMD2 = cfg.tmpDir + "/" + dT + tPMN2
		# No data value
		if cfg.ui.nodata_checkBox_2.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_3.value()
		else:
			nD = cfg.NoDataVal
		# TOA reflectance with correction for sun angle
		if cfg.ui.DOS1_checkBox.isChecked() is False or DOScheck == "No" or str(sat).lower() in ['surface reflectance', 'surface_reflectance', 'surfacereflectance']:
			try:
				m = float(REFLECTANCE_MULT_BAND)
				a = float(REFLECTANCE_ADD_BAND)
				# open input with GDAL
				rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)	
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) / (" + str(self.sA) + ") )", "raster", "TOA b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				# reclassification <0 and >1
				self.reclassRaster0min1max(tPMD, outputRaster)
				try:
					cfg.osSCP.remove(tPMD)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files deleted")
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(inputRaster))
				return "Yes"
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		# DOS atmospheric correction
		elif cfg.ui.DOS1_checkBox.isChecked() is True:
			DNm = cfg.utls.findDNmin(inputRaster, nD)
			# Esun calculation (see http://grass.osgeo.org/grass65/manuals/i.landsat.toar.html)
			radM = float(RADIANCE_MAXIMUM_BAND)
			refM = float(REFLECTANCE_MAXIMUM_BAND)
			eS = (cfg.np.pi * self.eSD * self.eSD) * radM / refM
			# calculate DOS1 corrected reflectance
			try:
				# radiance calculation
				m = float(RADIANCE_MULT_BAND)
				a = float(RADIANCE_ADD_BAND)
				# open input with GDAL
				rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", (raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")))", "raster", "radiance b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				# path radiance Lp = ML* DNm + AL  – 0.01* ESUNλ * cosθs / (π * d^2)	
				Lp = m * DNm + a - 0.01 * eS * self.sA / (cfg.np.pi * self.eSD * self.eSD)
				# land surface reflectance ρ = [π * (Lλ - Lp) * d^2]/ (ESUNλ * cosθs)	
				# open input with GDAL
				rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD2)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster - (" + str("%.16f" % Lp) + " ) )* " + str("%.16f" % cfg.np.pi) + " * " + str("%.16f" % self.eSD) + " * " + str("%.16f" % self.eSD) + " / ( " + str("%.16f" % eS)+ " * " + str(self.sA) + " )", "raster", "DOS1 b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				# reclassification <0 and >1
				self.reclassRaster0min1max(tPMD2, outputRaster)
				try:
					cfg.osSCP.remove(tPMD)
					cfg.osSCP.remove(tPMD2)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files deleted")
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(inputRaster))
				return "Yes"
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
				
	# landsat conversion of surface reflectance products
	def landsatSurfaceReflectance(self, satellite, bandNumber, REFLECTANCE_MULT_BAND, REFLECTANCE_ADD_BAND, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, RADIANCE_MAXIMUM_BAND, REFLECTANCE_MAXIMUM_BAND, inputRaster, outputRaster):
		sat = satellite
		x = bandNumber
		# temp files
		dT = cfg.utls.getTime()
		tPMN = cfg.reflectanceRasterNm + ".tif"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		# No data value
		if cfg.ui.nodata_checkBox_2.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_3.value()
		else:
			nD = cfg.NoDataVal
		# reflectance
		try:
			m = float(REFLECTANCE_MULT_BAND)
			a = float(REFLECTANCE_ADD_BAND)
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)	
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# output rasters
			oM = []
			oM.append(tPMD)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
			o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) )" , "raster", "surface reflectance b" + str(x))
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
			# reclassification <0 and >1
			self.reclassRaster0min1max(tPMD, outputRaster)
			try:
				cfg.osSCP.remove(tPMD)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files deleted")
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(inputRaster))
			return "Yes"
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
				
	# raster reclassification <0 and >1
	def reclassRaster0min1max(self, inputRaster, outputRaster):
		rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
		# band list
		bL = cfg.utls.readAllBandsFromRaster(rD)
		# output rasters
		oM = []
		oM.append(outputRaster)
		oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21")
		o = cfg.utls.processRaster(rD, bL, None, cfg.utls.reclassifyRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", [["(raster < 0)", 0], ["(raster > 1)", 1]], "raster", "reflectance")
		# close GDAL rasters
		for b in range(0, len(oMR)):
			oMR[b] = None
		for b in range(0, len(bL)):
			bL[b] = None
		rD = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(inputRaster))
						
	# landsat 1 to 7 conversion to Reflectance
	def landsat1_7reflectance(self, satellite, bandNumber, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, inputRaster, outputRaster):
		sat = satellite
		x = bandNumber
		# No data value
		if cfg.ui.nodata_checkBox_2.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_3.value()
		else:
			nD = cfg.NoDataVal
		# Esun
		dEsunB = {}
		# Esun from Chander, G.; Markham, B. L. & Helder, D. L. Summary of current radiometric calibration coefficients for Landsat MSS, TM, ETM+, and EO-1 ALI sensors Remote Sensing of Environment, 2009, 113, 893 - 903
		# landsat 1
		if str(sat).lower() in ['landsat_1', 'landsat1']:
			dEsunB = {"ESUN_BAND4": 1823, "ESUN_BAND5": 1559, "ESUN_BAND6": 1276, "ESUN_BAND7": 880.1}
		# landsat 2
		elif str(sat).lower() in ['landsat_2', 'landsat2']:
			dEsunB = {"ESUN_BAND4": 1829, "ESUN_BAND5": 1539, "ESUN_BAND6": 1268, "ESUN_BAND7": 886.6}	
		# landsat 3
		elif str(sat).lower() in ['landsat_3', 'landsat3']:
			dEsunB = {"ESUN_BAND4": 1839, "ESUN_BAND5": 1555, "ESUN_BAND6": 1291, "ESUN_BAND7": 887.9}
		# landsat 4
		elif str(sat).lower() in ['landsat_4', 'landsat4']:
			dEsunB = {"ESUN_BAND1": 1983, "ESUN_BAND2": 1795, "ESUN_BAND3": 1539, "ESUN_BAND4": 1028, "ESUN_BAND5": 219.8, "ESUN_BAND7": 83.49}
		# landsat 5
		elif str(sat).lower() in ['landsat_5', 'landsat5']:
			dEsunB = {"ESUN_BAND1": 1983, "ESUN_BAND2": 1796, "ESUN_BAND3": 1536, "ESUN_BAND4": 1031, "ESUN_BAND5": 220, "ESUN_BAND7": 83.44}
		# landsat 7 Esun from http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html
		elif str(sat).lower() in ['landsat_7', 'landsat7']:
			dEsunB = {"ESUN_BAND1": 1970, "ESUN_BAND2": 1842, "ESUN_BAND3": 1547, "ESUN_BAND4": 1044, "ESUN_BAND5": 225.7, "ESUN_BAND7": 82.06, "ESUN_BAND8": 1369}
		eS = float(dEsunB["ESUN_BAND" + str(x)])
		multipFactor = 1
		if str(cfg.RADIANCE_UNITS) == '"mW/cm^2/srad"':
			multipFactor = 10
		try:
			m = float(RADIANCE_MULT_BAND) * multipFactor
			a = float(RADIANCE_ADD_BAND) * multipFactor
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		# temp files
		dT = cfg.utls.getTime()
		tPMN = cfg.reflectanceRasterNm + ".tif"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		tPMN2 = cfg.reflectanceRasterNm + "2.tif"
		tPMD2 = cfg.tmpDir + "/" + dT + tPMN2
		# TOA reflectance
		if cfg.ui.DOS1_checkBox.isChecked() is False:
			try:
				# TOA Reflectance
				# open input with GDAL
				rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", ( ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) * " + str("%.16f" % cfg.np.pi) + " * " + str("%.16f" % self.eSD) + " * " + str("%.16f" % self.eSD) + ") / ( " + str("%.16f" % eS)+ " * (" + str(self.sA) + ") ) )", "raster", "TOA b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				# reclassification <0 and >1
				self.reclassRaster0min1max(tPMD, outputRaster)
				try:
					cfg.osSCP.remove(tPMD)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files deleted")
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(inputRaster))
				return "Yes"
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		# DOS atmospheric correction
		elif cfg.ui.DOS1_checkBox.isChecked() is True:
			# No data value
			if cfg.ui.nodata_checkBox_2.isChecked() is True:
				nD = cfg.ui.nodata_spinBox_3.value()
			DNm = cfg.utls.findDNmin(inputRaster, nD)
			# calculate DOS1 corrected reflectance
			try:
				# radiance calculation
				# open input with GDAL
				rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", (raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) )", "raster", "radiance b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				# path radiance Lp = ML* DNm + AL  – 0.01* ESUNλ * cosθs / (π * d^2)	
				Lp = m * DNm + a - 0.01 * eS * self.sA / (cfg.np.pi * self.eSD * self.eSD)
				# land surface reflectance ρ = [π * (Lλ - Lp) * d^2]/ (ESUNλ * cosθs)	
				# open input with GDAL
				rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD2)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster - (" + str("%.16f" % Lp) + ") ) * " + str("%.16f" % cfg.np.pi) + " * " + str("%.16f" % self.eSD) + " * " + str("%.16f" % self.eSD) + " / ( " + str("%.16f" % eS)+ " * (" + str(self.sA) + ") )", "raster", "DOS1 b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				# reclassification <0 and >1
				self.reclassRaster0min1max(tPMD2, outputRaster)
				try:
					cfg.osSCP.remove(tPMD)
					cfg.osSCP.remove(tPMD2)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files deleted")
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(inputRaster))
				return "Yes"
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			
	# landsat 4,5, or 7 temperature
	def landsat457Temperature(self, satellite, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, inputRaster, outputRaster):
		sat = satellite
		# No data value
		if cfg.ui.nodata_checkBox_2.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_3.value()
		else:
			nD = cfg.NoDataVal
		# landsat 4
		if str(sat).lower() in ['landsat_4', 'landsat4']:
			# k1 and k2 from Chander, G. & Markham, B. Revised landsat-5 TM radiometric calibration procedures and postcalibration dynamic ranges Geoscience and Remote Sensing, IEEE Transactions on, 2003, 41, 2674 - 2677
			k1 = float(671.62)
			k2 = float(1284.30)
		# landsat 5
		elif str(sat).lower() in ['landsat_5', 'landsat5']:
			# k1 and k2 from Chander, G. & Markham, B. Revised landsat-5 TM radiometric calibration procedures and postcalibration dynamic ranges Geoscience and Remote Sensing, IEEE Transactions on, 2003, 41, 2674 - 2677
			k1 = float(607.76)
			k2 = float(1260.56)
		# landsat 7
		elif str(sat).lower() in ['landsat_7', 'landsat7']:
			# k1 and k2 from NASA (Ed.) landsat 7 Science Data Users Handbook landsat Project Science Office at NASA's Goddard Space Flight Center in Greenbelt, pp.186
			k1 = float(666.09)
			k2 = float(1282.71)
		# Kelvin or cs
		cs = 0
		if cfg.ui.celsius_checkBox.isChecked() is True:
			cs = 273.15
		# At-Satellite Brightness Temperature
		try:
			m = float(RADIANCE_MULT_BAND)
			a = float(RADIANCE_ADD_BAND)
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# output rasters
			oM = []
			oM.append(outputRaster)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21")
			o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ",  ((" + str("%.16f" % k2) + ") / ( ln( (" + str("%.16f" % k1) + " / ( raster * " + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) ) + 1)) - " + str(cs) + ") )", "raster", "temperature")
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(outputRaster))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))		
			
	# landsat 8 temperature
	def landsat8Temperature(self, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, K1_CONSTANT_BAND, K2_CONSTANT_BAND, inputRaster, outputRaster):
		# No data value
		if cfg.ui.nodata_checkBox_2.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_3.value()
		else:
			nD = cfg.NoDataVal
		# Kelvin or cs
		cs = 0
		if cfg.ui.celsius_checkBox.isChecked() is True:
			cs = 273.15
		try:
			m = float(RADIANCE_MULT_BAND)
			a = float(RADIANCE_ADD_BAND)
			k1 = float(K1_CONSTANT_BAND)
			k2 = float(K2_CONSTANT_BAND)
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# output rasters
			oM = []
			oM.append(outputRaster)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21")
			o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No",  "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ",  ((" + str("%.16f" % k2) + ") / ( ln( (" + str("%.16f" % k1) + " / ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) ) + 1)) - " + str(cs) + ") )", "raster", "temperature")
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(outputRaster))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
	
	# landsat correction button
	def performLandsatCorrection(self):
		if len(cfg.ui.label_26.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.landsat(cfg.ui.label_26.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Perform landsat correction: " + str(cfg.ui.label_26.text()))
		
	# populate table
	def populateTable(self, input, batch = "No"):
		check = "Yes"
		sat = ""
		dt = ""
		sE = ""
		esd = ""
		surface_reflectance = "No"
		cfg.ui.satellite_lineEdit.setText(sat)
		cfg.ui.date_lineEdit.setText(dt)
		cfg.ui.sun_elev_lineEdit.setText(sE)
		cfg.ui.earth_sun_dist_lineEdit.setText(esd)
		l = cfg.ui.landsat_tableWidget
		cfg.utls.setColumnWidthList(l, [[0, 250]])
		cfg.utls.clearTable(l)
		inp = input
		if len(inp) == 0:
			cfg.mx.msg14()
		else:
			if batch == "No":
				cfg.uiUtls.addProgressBar()
			if len(cfg.ui.label_27.text()) == 0:
				for f in cfg.osSCP.listdir(inp):					
					#check metadata of surface reflectance level 2 products
					if f.lower().endswith("_t1.xml"):
						doc = cfg.minidomSCP.parse(inp + "/" + str(f))
						satellite = doc.getElementsByTagName("satellite")[0]
						sat = satellite.firstChild.data
						acquisition_date = doc.getElementsByTagName("acquisition_date")[0]
						dt = acquisition_date.firstChild.data
						surface_reflectance = "Yes"
						sat = sat + "_sr"
						cfg.ui.satellite_lineEdit.setText(sat)
						cfg.ui.date_lineEdit.setText(dt)
						cfg.ui.sun_elev_lineEdit.setText("1")
						cfg.ui.earth_sun_dist_lineEdit.setText("1")
					if f.lower().endswith(".txt") and "mtl" in f.lower():
							MTLFile = inp + "/" + str(f)
					# for compatibility with glcf images
					if f.lower().endswith(".met"):
							MTLFile = inp + "/" + str(f)
			else:
				MTLFile = cfg.ui.label_27.text()
		#### open MTL file
			if surface_reflectance == "No":
				try:
					# get information from MTL
					cfg.RADIANCE_UNITS = None
					with open(MTLFile, "r") as MTL:
						for r in MTL:
							# satellite
							if "SPACECRAFT_ID" in r.split():
								sat = str(r.split()[2]).replace('"', '')
							if "SUN_ELEVATION" in r.split():
								sE = str(r.split()[2])
							if "EARTH_SUN_DISTANCE" in r.split():
								esd = str(r.split()[2])
							if "DATE_ACQUIRED" in r.split() or "ACQUISITION_DATE" in r.split():
								dt = str(r.split()[2])
							if "RADIANCE_UNITS" in r.split():
								cfg.RADIANCE_UNITS = str(r.split()[2])
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr8()
					check = "No"						
				if esd == "":
					# date format
					dFmt = "%Y-%m-%d"
					try:
						esd = str(cfg.utls.calculateEarthSunDistance(dt, dFmt))
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.ui.satellite_lineEdit.setText(sat)
				cfg.ui.date_lineEdit.setText(dt)
				cfg.ui.sun_elev_lineEdit.setText(sE)
				cfg.ui.earth_sun_dist_lineEdit.setText(esd)
		#### list bands
			# bands
			dBs = {}
			bandNames = []
			# input dictionaries
			for f in cfg.osSCP.listdir(inp):
				if f.lower().endswith(".tif") or f.lower().endswith(".TIF") or f.lower().endswith(".Tif"):
					# name
					nm = cfg.osSCP.path.splitext(f)[0]
					if str(sat).lower() in ['landsat_4', 'landsat4', 'landsat_5', 'landsat5', 'landsat_7', 'landsat7']:
						# landsat bands
						if nm[len(nm) - 2].isdigit() and nm[len(nm) - 1].isdigit():
							if str(nm[len(nm) - 1]) == "0":
								dBs["BAND_{0}".format(nm[len(nm) - 2])] = str(f)
								bandNames.append(f)
							# landsat 7 thermal bands
							elif str(nm[len(nm) - 2]) == "6":
								dBs["BAND_6_VCID_{0}".format(nm[len(nm) - 1])] = str(f)
								bandNames.append(f)
						elif str(nm[len(nm) - 8: len(nm) - 1]) != "6_VCID_" and nm[len(nm) - 1].isdigit():
							dBs["BAND_{0}".format(nm[len(nm) - 1])] = str(f)
							bandNames.append(f)
						# landsat 7 thermal bands
						elif str(nm[len(nm) - 8: len(nm) - 1]) == "6_VCID_" and nm[len(nm) - 1].isdigit():
							dBs["BAND_6_VCID_{0}".format(nm[len(nm) - 1])] = str(f)
							bandNames.append(f)
					elif str(sat).lower() in ['landsat_8', 'landsat8']:
						# for bands > 9
						if nm[len(nm) - 2: len(nm) - 0] in ["10", "11"]:
							dBs["BAND_" + nm[len(nm) - 2: len(nm) - 0]] = str(f)
							bandNames.append(f)
						# for bands < 10
						elif str(nm[len(nm) - 8: len(nm) - 1]) != "6_VCID_" and nm[len(nm) - 1].isdigit() :
							dBs["BAND_{0}".format(nm[len(nm) - 1])] = str(f)
							bandNames.append(f)
					elif str(sat).lower() in ['landsat_1', 'landsat1','landsat_2', 'landsat2','landsat_3', 'landsat3']:
						#  landsat bands
						if nm[len(nm) - 1].isdigit() :
							dBs["BAND_{0}".format(nm[len(nm) - 1])] = str(f)
							bandNames.append(f)
					elif str(sat).lower() in ['landsat_1_sr', 'landsat_2_sr', 'landsat_3_sr', 'landsat_4_sr', 'landsat_5_sr', 'landsat_7_sr', 'landsat_8_sr']:
						#  landsat bands
						if nm[len(nm) - 1].isdigit() :
							dBs["BAND_{0}".format(nm[len(nm) - 1])] = str(f)
							bandNames.append(f)
					else:
						bandNames.append(f)
			# add band items to table
			b = 0
			for band in sorted(bandNames):				
				l.insertRow(b)
				l.setRowHeight(b, 20)
				cfg.utls.addTableItem(l, band, b, 0, "No")
				b = b + 1
			if check != "No":
				# radiance
				dRadMB = {}
				dRadAB = {}
				# reflectance
				dRefMB = {}
				dRefAB = {}
				# constants
				dK1B = {}
				dK2B = {}
				# radiance and reflectance maximum band
				dRadMxB = {}
				dRefMxB = {}
				dRad = {}
				if surface_reflectance == "No":
					# get information from MTL
					with open(MTLFile, "r") as MTL:
						for r in MTL:
							for key, band in dBs.items():
								try:
									# for conversion to TOA Radiance from https://landsat.usgs.gov/landsat8_Using_Product.php
									if "RADIANCE_MULT_" + str(key) in r.split():
										dRadMB["RADIANCE_MULT_" + str(key)] = str(r.split()[2])
									if "RADIANCE_ADD_" + str(key) in r.split():
										dRadAB["RADIANCE_ADD_" + str(key)] = str(r.split()[2])
									# for conversion to TOA Reflectance
									if "REFLECTANCE_MULT_" + str(key) in r.split():
										dRefMB["REFLECTANCE_MULT_" + str(key)] = str(r.split()[2])
									if "REFLECTANCE_ADD_" + str(key) in r.split():
										dRefAB["REFLECTANCE_ADD_" + str(key)] = str(r.split()[2])
									# for Esun calculation
									if "RADIANCE_MAXIMUM_" + str(key) in r.split():
										dRadMxB["RADIANCE_MAXIMUM_" + str(key)] = str(r.split()[2])
									if "REFLECTANCE_MAXIMUM_" + str(key) in r.split():
										dRefMxB["REFLECTANCE_MAXIMUM_" + str(key)] = str(r.split()[2])
									# for At-Satellite Brightness Temperature
									if "K1_CONSTANT_" + str(key) in r.split():
										dK1B["K1_CONSTANT_" + str(key)] = str(r.split()[2])
									if "K2_CONSTANT_" + str(key) in r.split():
										# rV = r.split()[2]
										dK2B["K2_CONSTANT_" + str(key)] = str(r.split()[2])
									# for compatibility with glcf images
									if "LMAX_" + str(key.replace('_', '').replace('VCID', '')) in r.split():
										dRad["LMAX_" + str(key)] = str(r.split()[2])
									if "LMIN_" + str(key.replace('_', '').replace('VCID', '')) in r.split():
										dRad["LMIN_" + str(key)] = str(r.split()[2])
									if "QCALMAX_" + str(key.replace('_', '').replace('VCID', '')) in r.split():
										dRad["QCALMAX_" + str(key)] = str(r.split()[2])
									if "QCALMIN_" + str(key.replace('_', '').replace('VCID', '')) in r.split():
										dRad["QCALMIN_" + str(key)] = str(r.split()[2])
									if "GAIN_" + str(key) in r.split() or "GAIN_" + str(key).replace("BAND_", "BAND") in r.split():
										dRadMB["RADIANCE_MULT_" + str(key)] = str(r.split()[2])
									if "BIAS_" + str(key) in r.split() or ("BIAS_" + str(key)).replace("BAND_", "BAND") in r.split():
										dRadAB["RADIANCE_ADD_" + str(key)] = str(r.split()[2])
								except Exception as err:
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))	
				# add items to table
				b = 0
				for bandName in sorted(bandNames):	
					for key, band in dBs.items():
						if bandName == band:
							if surface_reflectance == "Yes":
								try:
									cfg.utls.addTableItem(l, 0.0001, b, 3)
								except:
									pass
								try:
									cfg.utls.addTableItem(l, 0, b, 4)
								except:
									pass
							if dRadMB:
								try:
									cfg.utls.addTableItem(l, dRadMB["RADIANCE_MULT_" + str(key)], b, 1)
								except:
									pass
							if dRadAB:
								try:
									cfg.utls.addTableItem(l, dRadAB["RADIANCE_ADD_" + str(key)], b, 2)
								except:
									pass
							if dRefMB:
								try:
									cfg.utls.addTableItem(l, dRefMB["REFLECTANCE_MULT_" + str(key)], b, 3)
								except:
									pass
							if dRefAB:
								try:
									cfg.utls.addTableItem(l, dRefAB["REFLECTANCE_ADD_" + str(key)], b, 4)
								except:
									pass
							if dRadMxB:
								try:
									cfg.utls.addTableItem(l, dRadMxB["RADIANCE_MAXIMUM_" + str(key)], b, 5)
								except:
									pass
							if dRefMxB:
								try:
									cfg.utls.addTableItem(l, dRefMxB["REFLECTANCE_MAXIMUM_" + str(key)], b, 6)
								except:
									pass
							if dK1B:
								try:
									cfg.utls.addTableItem(l, dK1B["K1_CONSTANT_" + str(key)], b, 7)
								except:
									pass
							if dK2B:
								try:
									cfg.utls.addTableItem(l, dK2B["K2_CONSTANT_" + str(key)], b, 8)
								except:
									pass
							if dRad:
								try:
									cfg.utls.addTableItem(l, dRad["LMAX_" + str(key)], b, 9)
									cfg.utls.addTableItem(l, dRad["LMIN_" + str(key)], b, 10)
									cfg.utls.addTableItem(l, dRad["QCALMAX_" + str(key)], b, 11)
									cfg.utls.addTableItem(l, dRad["QCALMIN_" + str(key)], b, 12)
								except:
									pass
					b = b + 1
				if batch == "No":
					cfg.uiUtls.removeProgressBar()			

	def editedCell(self, row, column):
		if column != 0:
			l = cfg.ui.landsat_tableWidget
			val = l.item(row, column).text()
			try:
				float(val)
			except:
				l.item(row, column).setText("")
	
	# earth sun distance
	def editedEarthSunDist(self):
		try:
			float(cfg.ui.earth_sun_dist_lineEdit.text())
		except:
			cfg.ui.earth_sun_dist_lineEdit.setText("")
			
	# sun elevation
	def editedSunElevation(self):
		try:
			float(cfg.ui.sun_elev_lineEdit.text())
		except:
			cfg.ui.sun_elev_lineEdit.setText("")
			
	def editedDate(self):
		dFmt = "%Y-%m-%d"
		dt = cfg.ui.date_lineEdit.text()
		try:
			cfg.utls.calculateEarthSunDistance(dt, dFmt)
			cfg.ui.date_lineEdit.setStyleSheet("color : black")
		except:
			cfg.ui.date_lineEdit.setStyleSheet("color : red")
		
	def removeHighlightedBand(self):
		l = cfg.ui.landsat_tableWidget
		cfg.utls.removeRowsFromTable(l)
		
	def editedSatellite(self):
		sat = cfg.ui.satellite_lineEdit.text()
		if str(sat).lower() in ['landsat_1', 'landsat1','landsat_2', 'landsat2','landsat_3', 'landsat3','landsat_4', 'landsat4', 'landsat_5', 'landsat5', 'landsat_7', 'landsat7', 'landsat_8', 'landsat8', 'landsat_1_sr', 'landsat_2_sr', 'landsat_3_sr', 'landsat_4_sr', 'landsat_5_sr', 'landsat_7_sr', 'landsat_8_sr']:
			cfg.ui.satellite_lineEdit.setStyleSheet("color : black")
		else:
			cfg.ui.satellite_lineEdit.setStyleSheet("color : red")
			
	def landsat_Pansharp(self, inputList, satellite, bandNumberList, outputList):
		tPMN = cfg.tmpVrtNm + ".vrt"
		# date time for temp name
		dT = cfg.utls.getTime()
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		tempRasterList = []
		for i in range(0, len(outputList)):
			tempRasterList.append(cfg.tmpDir + "/" + dT + str(i) +"t.tif")
		vrtCheck = cfg.utls.createVirtualRaster(inputList, tPMD, "No", "Yes", "Yes", 0, "Yes")
		# open input with GDAL
		rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
		if rD is None:
			cfg.mx.msg4()
			self.rasterBandName()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " None raster")
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			return "No"
		# band list
		bL = cfg.utls.readAllBandsFromRaster(rD)
		# create rasters
		oMR = cfg.utls.createRasterFromReference(rD, 1, tempRasterList, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21")
		o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.pansharpening, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", satellite, bandNumberList, "pansharpening ")
		# close GDAL rasters
		for b in range(0, len(oMR)):
			oMR[b] = None
		for b in range(0, len(bL)):
			bL[b] = None
		rD = None
		bN = 0
		for temp in tempRasterList:
			try:
				cfg.utls.GDALCopyRaster(temp, outputList[bN], "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
				cfg.osSCP.remove(temp)
			except Exception as err:
				try:
					cfg.shutilSCP.copy(temp, outputRasterList[bN])
					cfg.osSCP.remove(temp)
				except Exception as err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			bN = bN + 1
		return o