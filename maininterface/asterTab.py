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

class ASTERTab:

	def __init__(self):
		pass
		
	# ASTER input
	def inputASTER(self):
		i = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a HDF file"), "", "file .hdf (*.hdf)")
		cfg.ui.label_143.setText(str(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(i))
	
	# ASTER conversion to reflectance and temperature
	def ASTER(self, inputFile, outputDirectory, batch = "No", bandSetNumber = None):
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
		ulm = cfg.ui.ulm_lineEdit.text()
		try:
			uLY = float(ulm.split(",")[0])
			uLX = float(ulm.split(",")[1])
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No earth sun distance error")
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
			cfg.mx.msgErr37()
			return "No"
		utmZone = int(cfg.ui.utm_zone_lineEdit.text())
		# reference system
		rSrc = cfg.osrSCP.SpatialReference()
		rSrc.SetProjCS("proj")
		rSrc.SetWellKnownGeogCS("WGS84")
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
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No sun elevation error")
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
			cfg.mx.msgErr37()
			return "No"
		# earth sun distance
		if len(cfg.ui.earth_sun_dist_lineEdit_2.text()) > 0:
			try:
				self.eSD = float(cfg.ui.earth_sun_dist_lineEdit_2.text())
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No earth sun distance error")
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
				cfg.mx.msgErr37()
				return "No"
		if len(str(self.eSD)) == 0:
			dFmt = "%Y%m%d"
			dt = cfg.ui.date_lineEdit_2.text()
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
		l = cfg.ui.ASTER_tableWidget
		# input
		if inputFile.lower().endswith(".hdf"):
			fileNm = cfg.osSCP.path.basename(inputFile)[:-4]
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputFile, cfg.gdalSCP.GA_ReadOnly)
			rDSub = rD.GetSubDatasets()
		out = outputDirectory
		oDir = cfg.utls.makeDirectory(out)
		# name prefix
		pre = "RT_"
		# input bands
		c = l.rowCount()
		# date time for temp name
		dT = cfg.utls.getTime()
		# temp raster
		tempRasterList = []
		# output raster list
		outputRasterList = []
		# band list
		bandSetList = []
		bandSetNameList = []
		bandNumberList = []
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				iBand = l.item(i,0).text()
				iBandN = iBand[-2:]
				#  aster bands
				for sb in rDSub:
					inputRaster = None
					nm = sb[0]
					if "VNIR" in str(nm):
						if "0" + nm[-1:] == iBandN:
							bandName = fileNm + "_" + iBandN
							inputRaster = nm
						elif nm[-2:] == "3N" and iBandN in ["03"]:
							bandName = fileNm + "_03"
							inputRaster = nm
					elif "SWIR" in str(nm):
						if "0" + nm[-1:] == iBandN:
							bandName = fileNm + "_" + iBandN
							inputRaster = nm
					elif "TIR" in str(nm):
						if nm[-2:] == iBandN:
							bandName = fileNm + "_" + iBandN
							inputRaster = nm
					if inputRaster is not None:
						oNm = pre + iBand + ".tif"
						outputRaster = out + "/" + oNm
						outputRasterList.append(outputRaster)
						tempRaster = cfg.tmpDir + "/" + dT + iBand + ".tif"
						tempRasterList.append(tempRaster)
						try:
							coeff = float(l.item(i,1).text())
						except:
							coeff = ""
						try:
							pSize = int(l.item(i,2).text())
						except:
							pSize = ""
						self.geotransform = (uLX, pSize, 0, uLY, 0, -pSize)
						if bandName[-2:] not in ["10", "11", "12", "13", "14"]:
							# conversion
							ck = self.ASTER_reflectance(bandName[-2:], coeff, inputRaster, tempRaster)
							if ck != "No":
								# band list
								bandSetList.append(int(bandName[-2:]))
								bandSetNameList.append(pre + bandName)
						# thermal bands
						else:
							ck = self.ASTERTemperature(bandName[-2:], coeff, inputRaster, tempRaster)
							if ck != "No":
								# band list
								bandSetList.append(int(bandName[-2:]))
								bandSetNameList.append(pre + bandName)
		cfg.uiUtls.updateBar(90)
		if cfg.actionCheck == "Yes":
			# copy raster bands
			bN = 0
			for temp in tempRasterList:
				if temp[-2:].lower() in ["10", "11", "12", "13", "14"]:
					resample = "-outsize 600% 600%"
				elif temp[-2:].lower() in ["04", "05", "06", "07", "08", "09"]:
					resample = "-outsize 200% 200%"
				else:
					resample = ""
				try:
					cfg.utls.GDALCopyRaster(temp, outputRasterList[bN], "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1", resample)
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
		if cfg.actionCheck == "Yes":
			# load raster bands
			for outR in outputRasterList:
				if cfg.osSCP.path.isfile(outR):
					cfg.utls.addRasterLayer(outR)
				else:
					cfg.mx.msgErr38(outR)
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "WARNING: unable to load raster" + str(outR))
			# create band set
			if cfg.ui.create_bandset_checkBox.isChecked() is True:
				if cfg.ui.add_new_bandset_checkBox_4.isChecked() is True:
					bandSetNumber = cfg.bst.addBandSetTab()
				cfg.bst.rasterBandName()
				cfg.bst.setBandSet(bandSetNameList, bandSetNumber)
				cfg.bandSetsList[bandSetNumber][0] = "Yes"
				cfg.bst.setSatelliteWavelength(cfg.satASTER, None, bandSetNumber)
			cfg.bst.bandSetTools(out)
			cfg.uiUtls.updateBar(100)
		# close GDAL rasters
		rDSub = None
		rD = None
		if batch == "No":
			cfg.utls.finishSound()
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()
				
	# raster reclassification <0 and >1
	def reclassRaster0min1max(self, inputRaster, outputRaster):
		rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
		# band list
		bL = cfg.utls.readAllBandsFromRaster(rD)
		# output rasters
		oM = []
		oM.append(outputRaster)
		oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21", self.rSr, self.geotransform)
		o = cfg.utls.processRaster(rD, bL, None, cfg.utls.reclassifyRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", [["(raster < 0)", 0], ["(raster > 1)", 1]], "raster", "reflectance")
		# close GDAL rasters
		for b in range(0, len(oMR)):
			oMR[b] = None
		for b in range(0, len(bL)):
			bL[b] = None
		rD = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(inputRaster))
						
	# conversion to Reflectance
	def ASTER_reflectance(self, bandNumber, conversionCoefficient, inputRaster, outputRaster):
		DOScheck = "Yes"
		if cfg.ui.DOS1_checkBox_2.isChecked() is True and cfg.ui.DOS1_bands_checkBox_2.isChecked() is True:
			if str(bandNumber) in ["01"]:
				DOScheck = "Yes"
			else:
				DOScheck = "No"
		m = float(conversionCoefficient)
		# Esun
		dEsunB = {}
		# Esun from Michael P. Finn, Matthew D. Reed, and Kristina H. Yamamoto (2012). A Straight Forward Guide for Processing Radiance and Reflectance for EO-1 ALI, Landsat 5 TM, Landsat 7 ETM+, and ASTER    
		dEsunB = {"ESUN_BAND01": 1848, "ESUN_BAND02": 1549, "ESUN_BAND03": 1114, "ESUN_BAND04": 225.4, "ESUN_BAND05": 86.63, "ESUN_BAND06": 81.85, "ESUN_BAND07": 74.85, "ESUN_BAND08": 66.49, "ESUN_BAND09": 59.85}
		eS = float(dEsunB["ESUN_BAND" + str(bandNumber)])
		# temp files
		dT = cfg.utls.getTime()
		tPMN = cfg.reflectanceRasterNm + ".tif"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		tPMN2 = cfg.reflectanceRasterNm + "2.tif"
		tPMD2 = cfg.tmpDir + "/" + dT + tPMN2
		tempRasterNm = cfg.reflectanceRasterNm + "3.tif"
		tempRaster = cfg.tmpDir + "/" + dT + tempRasterNm
		# No data value
		if cfg.ui.nodata_checkBox_5.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_6.value()
		else:
			nD = cfg.NoDataVal
		# TOA reflectance
		if cfg.ui.DOS1_checkBox_2.isChecked() is False or DOScheck == "No":
			try:
				# open input with GDAL
				rD = cfg.gdalSCP.Open(inputRaster)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21", self.rSr, self.geotransform)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", (  (raster - 1 ) *" + str("%.16f" % m) + " * " + str("%.16f" % cfg.np.pi) + " * " + str("%.16f" % self.eSD) + " * " + str("%.16f" % self.eSD) + ") / ( " + str("%.16f" % eS)+ " * (" + str(self.sA) + ") ) )", "raster", "TOA b" + str(bandNumber))
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
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
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
		elif cfg.ui.DOS1_checkBox_2.isChecked() is True:
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
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21", self.rSr, self.geotransform)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", ( (raster - 1) * " + str("%.16f" % m) + ") )", "raster", "radiance b" + str(bandNumber))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				# path radiance Lp = ML* DNm + AL  – 0.01* ESUN * coss / (π * d^2)	
				Lp = m * (DNm - 1) - 0.01 * eS * self.sA / (cfg.np.pi * self.eSD * self.eSD)
				# land surface reflectance r = [π * (L - Lp) * d^2]/ (ESUN * coss)	
				# open input with GDAL
				rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD2)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21", self.rSr, self.geotransform)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster - (" + str("%.16f" % Lp) + ") ) * " + str("%.16f" % cfg.np.pi) + " * " + str("%.16f" % self.eSD) + " * " + str("%.16f" % self.eSD) + " / ( " + str("%.16f" % eS)+ " * (" + str(self.sA) + ") )", "raster", "DOS1 b" + str(bandNumber))
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
					
	# ASTER temperature
	def ASTERTemperature(self, bandNumber, conversionCoefficient, inputRaster, outputRaster):
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
		try:
			m = float(conversionCoefficient)
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# output rasters
			oM = []
			oM.append(outputRaster)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21", self.rSr, self.geotransform)
			o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", ((" + str("%.16f" % k2) + ") / ( ln( (" + str("%.16f" % k1) + " / ( (raster - 1 ) * " + str("%.16f" % m) + ") ) + 1)) - " + str(cs) + ") )", "raster", "temperature")
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

	# ASTER correction button
	def performASTERCorrection(self):
		if len(cfg.ui.label_143.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.ASTER(cfg.ui.label_143.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Perform ASTER correction: " + str(cfg.ui.label_143.text()))
		
	# populate table
	def populateTable(self, input, batch = "No"):
		check = "Yes"
		dt = ""
		sE = ""
		esd = ""
		cfg.ui.date_lineEdit_2.setText(dt)
		cfg.ui.sun_elev_lineEdit_2.setText(sE)
		cfg.ui.earth_sun_dist_lineEdit_2.setText(esd)
		l = cfg.ui.ASTER_tableWidget
		cfg.utls.setColumnWidthList(l, [[0, 250]])
		cfg.utls.clearTable(l)
		if len(input) == 0:
			cfg.mx.msg14()
		else:
			if batch == "No":
				cfg.uiUtls.addProgressBar()
			# bands
			dBs = {}
			dGains = {}
			bandNames = []
			# input
			if input.lower().endswith(".hdf"):
				fileNm = cfg.osSCP.path.basename(input)[:-4]
				# open input with GDAL
				rD = cfg.gdalSCP.Open(input, cfg.gdalSCP.GA_ReadOnly)
				if rD is None:
					pass
				else:
					# get metadata
					rDMeta = rD.GetMetadata_List()
					for metadata in rDMeta:
						if "CALENDARDATE" in metadata:
							dt = metadata.split("=")[1]
						elif "SOLARDIRECTION" in metadata:
							sD = metadata.split("=")[1]
							sE = sD.split(",")[1]
						elif "UTMZONECODE" in metadata:
							utm = metadata.split("=")[1]
						elif "UPPERLEFTM" in metadata:
							uLM = metadata.split("=")[1]
						elif "GAIN" in metadata:
							g = metadata.split("=")[1]
							if g.split(",")[0] == "01":
								if g.split(",")[1].strip() == "HGH":
									v  = 0.676
								elif g.split(",")[1].strip() == "NOR":
									v  = 1.688 
								elif g.split(",")[1].strip() == "LOW":
									v  = 2.25
								else:
									v = "No"
								dGains["BAND_" + g.split(",")[0]] = v
							elif g.split(",")[0] == "02":
								if g.split(",")[1].strip() == "HGH":
									v  = 0.708
								elif g.split(",")[1].strip() == "NOR":
									v  = 1.415
								elif g.split(",")[1].strip() == "LOW":
									v  = 1.89
								else:
									v = "No"
								dGains["BAND_" + g.split(",")[0]] = v
							elif g.split(",")[0] == "3N":
								if g.split(",")[1].strip() == "HGH":
									v  = 0.423 
								elif g.split(",")[1].strip() == "NOR":
									v  = 0.862
								elif g.split(",")[1].strip() == "LOW":
									v  = 1.15
								else:
									v = "No"	
								dGains["BAND_03"]  = v
							elif g.split(",")[0] == "04":
								if g.split(",")[1].strip() == "HGH":
									v  = 0.1087
								elif g.split(",")[1].strip() == "NOR":
									v  = 0.2174
								elif g.split(",")[1].strip() == "LO1":
									v  = 0.290
								elif g.split(",")[1].strip() == "LO2":
									v  = 0.290
								else:
									v = "No"
								dGains["BAND_" + g.split(",")[0]] = v
							elif g.split(",")[0] == "05":
								if g.split(",")[1].strip() == "HGH":
									v  = 0.0348
								elif g.split(",")[1].strip() == "NOR":
									v  = 0.0696
								elif g.split(",")[1].strip() == "LO1":
									v  = 0.0925
								elif g.split(",")[1].strip() == "LO2":
									v  = 0.409
								else:
									v = "No"
								dGains["BAND_" + g.split(",")[0]] = v
							elif g.split(",")[0] == "06":
								if g.split(",")[1].strip() == "HGH":
									v  = 0.0313
								elif g.split(",")[1].strip() == "NOR":
									v  = 0.0625
								elif g.split(",")[1].strip() == "LO1":
									v  = 0.0830
								elif g.split(",")[1].strip() == "LO2":
									v  = 0.390
								else:
									v = "No"
								dGains["BAND_" + g.split(",")[0]] = v
							elif g.split(",")[0] == "07":
								if g.split(",")[1].strip() == "HGH":
									v  = 0.0299
								elif g.split(",")[1].strip() == "NOR":
									v  = 0.0597
								elif g.split(",")[1].strip() == "LO1":
									v  = 0.0795
								elif g.split(",")[1].strip() == "LO2":
									v  = 0.332
								else:
									v = "No"
								dGains["BAND_" + g.split(",")[0]] = v
							elif g.split(",")[0] == "08":
								if g.split(",")[1].strip() == "HGH":
									v  = 0.0209
								elif g.split(",")[1].strip() == "NOR":
									v  = 0.0417
								elif g.split(",")[1].strip() == "LO1":
									v  = 0.0556
								elif g.split(",")[1].strip() == "LO2":
									v  = 0.245
								else:
									v = "No"
								dGains["BAND_" + g.split(",")[0]] = v
							elif g.split(",")[0] == "09":
								if g.split(",")[1].strip() == "HGH":
									v  = 0.0159
								elif g.split(",")[1].strip() == "NOR":
									v  = 0.0318
								elif g.split(",")[1].strip() == "LO1":
									v  = 0.0424
								elif g.split(",")[1].strip() == "LO2":
									v  = 0.265
								else:
									v = "No"
								dGains["BAND_" + g.split(",")[0]] = v
							dGains["BAND_" + "10"] = 0.006822
							dGains["BAND_" + "11"] = 0.006780
							dGains["BAND_" + "12"] = 0.006590
							dGains["BAND_" + "13"] = 0.005693
							dGains["BAND_" + "14"] = 0.005225
					# date format
					dFmt = "%Y%m%d"
					try:
						esd = str(cfg.utls.calculateEarthSunDistance(dt, dFmt))
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					try:
						cfg.ui.date_lineEdit_2.setText(dt)
						cfg.ui.sun_elev_lineEdit_2.setText(sE)
						cfg.ui.earth_sun_dist_lineEdit_2.setText(esd)
						cfg.ui.utm_zone_lineEdit.setText(utm)
						cfg.ui.ulm_lineEdit.setText(uLM)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
						return
					rDSub = rD.GetSubDatasets()
					#  aster bands
					for sb in rDSub:
						nm = sb[0]
						if "VNIR" in str(nm):
							sbD = cfg.gdalSCP.Open(str(nm))
							if nm[-1:].isdigit() :
								dBs["BAND_0{0}".format(nm[-1:])] = 15
								bandNames.append(fileNm + "_0" + nm[-1:])
							elif nm[-2:] == "3N":
								dBs["BAND_03"] = 15
								bandNames.append(fileNm + "_03")
						elif "SWIR" in str(nm):
							sbD = cfg.gdalSCP.Open(str(nm))
							if nm[-1:].isdigit() :
								dBs["BAND_0{0}".format(nm[-1:])] = 30
								bandNames.append(fileNm + "_0" + nm[-1:])
						elif "TIR" in str(nm):
							sbD = cfg.gdalSCP.Open(str(nm))
							if nm[-2:].isdigit() :
								dBs["BAND_{0}".format(nm[-2:])] = 90
								bandNames.append(fileNm + "_" + nm[-2:])
			# add band items to table
			b = 0
			for band in sorted(bandNames):				
				l.insertRow(b)
				l.setRowHeight(b, 20)
				cfg.utls.addTableItem(l, band, b, 0, "No")
				try:
					cfg.utls.addTableItem(l, str(dGains["BAND_" + band[-2:]]), b, 1)
					cfg.utls.addTableItem(l, dBs["BAND_" + band[-2:]], b, 2)
				except:
					pass
				b = b + 1
			if batch == "No":
				cfg.uiUtls.removeProgressBar()			

	def editedCell(self, row, column):
		if column != 0:
			l = cfg.ui.ASTER_tableWidget
			val = l.item(row, column).text()
			try:
				float(val)
			except:
				l.item(row, column).setText("")
	
	# earth sun distance
	def editedEarthSunDist(self):
		try:
			float(cfg.ui.earth_sun_dist_lineEdit_2.text())
		except:
			cfg.ui.earth_sun_dist_lineEdit_2.setText("")
			
	# sun elevation
	def editedSunElevation(self):
		try:
			float(cfg.ui.sun_elev_lineEdit_2.text())
		except:
			cfg.ui.sun_elev_lineEdit_2.setText("")
			
	def editedDate(self):
		dFmt = "%Y%m%d"
		dt = cfg.ui.date_lineEdit_2.text()
		try:
			cfg.utls.calculateEarthSunDistance(dt, dFmt)
			cfg.ui.date_lineEdit_2.setStyleSheet("color : black")
		except:
			cfg.ui.date_lineEdit_2.setStyleSheet("color : red")
		
	def removeHighlightedBand(self):
		l = cfg.ui.ASTER_tableWidget
		cfg.utls.removeRowsFromTable(l)
		