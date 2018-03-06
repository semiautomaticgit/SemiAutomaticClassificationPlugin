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

class Sentinel3Tab:

	def __init__(self):
		pass
		
	# Sentinel-3 input
	def inputSentinel(self):
		i = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		cfg.ui.S3_label_87.setText(str(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(i))
		
	# populate table
	def populateTable(self, input, batch = "No"):
		check = "Yes"
		sat = "Sentinel-3A"
		prod = "OLCI"
		cfg.ui.S3_satellite_lineEdit.setText(sat)
		cfg.ui.S3_product_lineEdit.setText(prod)
		l = cfg.ui.sentinel_3_tableWidget
		cfg.utls.setColumnWidthList(l, [[0, 450]])
		cfg.utls.clearTable(l)
		inp = input
		if len(inp) == 0:
			cfg.mx.msg14()
		else:
			if batch == "No":
				cfg.uiUtls.addProgressBar()
			cfg.ui.S3_satellite_lineEdit.setText(sat)
			# bands
			dBs = {}
			bandNames = []	
			for f in cfg.osSCP.listdir(inp):
				if f.lower().endswith(".nc"):
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
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
			
	# edited satellite
	def editedSatellite(self):
		sat = cfg.ui.S3_satellite_lineEdit.text()
		if str(sat).lower() in ['sentinel_3a', 'sentinel-3a', 'sentinel_3b', 'sentinel-3b']:
			cfg.ui.S3_satellite_lineEdit.setStyleSheet("color : black")
		else:
			cfg.ui.S3_satellite_lineEdit.setStyleSheet("color : red")
	
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
				l.item(row, column).setText("")

	# sentinel-3 output
	def performSentinelConversion(self):
		if len(cfg.ui.S3_label_87.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.sentinel3(cfg.ui.S3_label_87.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Perform sentinel-3 conversion: " + str(cfg.ui.S3_label_87.text()))
		
	# sentinel-3 conversion
	def sentinel3(self, inputDirectory, outputDirectory, batch = "No", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		cfg.uiUtls.addProgressBar()
		# disable map canvas render for speed
		if batch == "No":
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
		if str(sat) == "":
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No satellite error")
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
			cfg.mx.msgErr37()
			return "No"
		cfg.uiUtls.updateBar(5)	
		l = cfg.ui.sentinel_3_tableWidget
		inp = inputDirectory
		out = outputDirectory
		# input
		for f in cfg.osSCP.listdir(inp):
			cfg.uiUtls.updateBar(10)
			cfg.QtWidgetsSCP.qApp.processEvents()
			if f.lower().endswith(".nc") and "qualityflags" in f.lower():
				pass
			elif f.lower().endswith(".nc") and "geo_coordinates" in f.lower():
				# get pixel coordinates
				geo_coordinates = inp + "/" + f
				# open input with GDAL
				rDGC = cfg.gdalSCP.Open(geo_coordinates, cfg.gdalSCP.GA_ReadOnly)
				rDGCSub = rDGC.GetSubDatasets()
				for sb in rDGCSub:
					nm = sb[0]
					if "latitude" in str(nm):
						# open input with GDAL
						rDLat = cfg.gdalSCP.Open(nm)
						rDLatB = rDLat.GetRasterBand(1)
					elif "longitude" in str(nm):
						# open input with GDAL
						rDLon = cfg.gdalSCP.Open(nm)
						rDLonB = rDLon.GetRasterBand(1)
				# set GCPs
				gcpList = []
				z = 0
				rX = list(range(0, rDLon.RasterXSize, int(rDLon.RasterXSize/100)))
				rY = list(range(0, rDLon.RasterYSize, int(rDLon.RasterYSize/100)))
				for pX in rX:
					for pY in rY:
						x = cfg.utls.readArrayBlock(rDLonB, pX, pY, 1, 1) / 1000000
						y = cfg.utls.readArrayBlock(rDLatB, pX, pY, 1, 1) / 1000000
						gcp = cfg.gdalSCP.GCP(float(x), float(y), z, pX, pY)
						gcpList.append(gcp)
				pX = rDLon.RasterXSize-1
				pY = rDLat.RasterYSize-1
				x = cfg.utls.readArrayBlock(rDLonB, pX, pY, 1, 1) / 1000000
				y = cfg.utls.readArrayBlock(rDLatB, pX, pY, 1, 1) / 1000000
				gcp = cfg.gdalSCP.GCP(float(x), float(y), z, pX, pY)
				gcpList.append(gcp)
				sr = cfg.osrSCP.SpatialReference()
				sr.ImportFromEPSG(4326)
				gcpProj = sr.ExportToWkt()
				rDLatB = None
				rDLat = None
				bLLonB = None
				rDLon = None
				rDSub = None
				rD = None
			elif f.lower().endswith(".nc") and "tie_geometries" in f.lower():
				tie_geometries = inp + "/" + f
				# open input with GDAL
				rDTG = cfg.gdalSCP.Open(tie_geometries, cfg.gdalSCP.GA_ReadOnly)
				rDTGSub = rDTG.GetSubDatasets()
				for sb in rDTGSub:
					nm = sb[0]
					if "SZA" in str(nm):
						# open input with GDAL
						rDSZA = cfg.gdalSCP.Open(nm)
						rDSZAB = rDSZA.GetRasterBand(1)
						# get the mean value of sun zenith angle
						bSt = rDSZAB.GetStatistics(True, True)
						SZA = bSt[2] / 1000000	
				rDTGSub = None
				rDTG = None
			elif f.lower().endswith(".nc") and "instrument_data" in f.lower():
				instrument_data = inp + "/" + f
				# open input with GDAL
				rDID = cfg.gdalSCP.Open(instrument_data, cfg.gdalSCP.GA_ReadOnly)
				rDIDSub = rDID.GetSubDatasets()
				# Esun
				dEsunB = {}
				for sb in rDIDSub:
					nm = sb[0]
					if "solar_flux" in str(nm):
						# open input with GDAL
						rDSolF = cfg.gdalSCP.Open(nm)
						rDSolFB = rDSolF.GetRasterBand(1)
						# get the mean value of solar flux for each band
						for y in range(0, rDSolF.RasterYSize):
							esun = cfg.utls.readArrayBlock(rDSolFB, int(rDSolF.RasterXSize / 2), y, 1, 1)
							dEsunB["ESUN_BAND" + str(y + 1)] = float(esun)
				rDIDSub = None
				rDID = None
		cfg.uiUtls.updateBar(15)
		if SZA is None or bool(dEsunB) is False or gcpList is None:
			if batch == "No":
				cfg.cnvs.setRenderFlag(True)
				cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr37()
			else:
				cfg.mx.msgErr37()
				return
		# name prefix
		pre = "RT_"
		oDir = cfg.utls.makeDirectory(out)
		l = cfg.ui.sentinel_3_tableWidget
		# input bands
		c = l.rowCount()
		# date time for temp name
		dT = cfg.utls.getTime()
		# temp raster
		tempRasterList = []
		# output raster list
		outputRasterList = []
		nodataValue = 0		
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				cfg.uiUtls.updateBar(20)
				cfg.QtWidgetsSCP.qApp.processEvents()
				iBand = l.item(i,0).text()
				iBandN = int(iBand[-2:])
				sBand = inp + "/" + iBand + ".nc"
				# open input with GDAL
				rDB = cfg.gdalSCP.Open(sBand, cfg.gdalSCP.GA_ReadOnly)
				rDMeta = rDB.GetMetadata_List()
				for metadata in rDMeta:
					if "scale_factor" in metadata:
						scale_factor = metadata.split("=")[1]
					elif "add_offset" in metadata:
						add_offset = metadata.split("=")[1]
					elif "_FillValue" in metadata:
						fillValue = metadata.split("=")[1]
					elif "start_time" in metadata:
						date = metadata.split("=")[1].split("T")[0]
				eSun = float(dEsunB["ESUN_BAND" + str(iBandN)])
				# temp files
				dT = cfg.utls.getTime()
				tPMN = cfg.reflectanceRasterNm + "B" + str(iBandN) + ".tif"
				tPMD = cfg.tmpDir + "/" + dT + tPMN
				self.sentinel3reflectance(iBandN, sBand, scale_factor, add_offset, fillValue, eSun, SZA, date, tPMD)
				cfg.uiUtls.updateBar(30)
				cfg.QtWidgetsSCP.qApp.processEvents()
				outputRaster = oDir + "/" + pre + iBand + ".tif"
				ck = self.georeferenceImage(iBandN, tPMD, outputRaster, rDB.RasterXSize, rDB.RasterYSize, gcpList, gcpProj, 0)
				if ck != "No":
					# band list
					bandSetList.append(iBandN)
					bandSetNameList.append(pre + iBand + ".tif")
					outputRasterList.append(outputRaster)
		if cfg.actionCheck == "Yes":
			# load raster bands
			for outR in outputRasterList:
				if cfg.osSCP.path.isfile(outR):
					cfg.utls.addRasterLayer(outR)
				else:
					cfg.mx.msgErr38(outR)
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "WARNING: unable to load raster" + str(outR))
			# create band set
			if cfg.ui.S3_create_bandset_checkBox.isChecked() is True:
				if cfg.ui.add_new_bandset_checkBox_3.isChecked() is True:
					bandSetNumber = cfg.bst.addBandSetTab()
				cfg.bst.rasterBandName()
				cfg.bst.setBandSet(bandSetNameList, bandSetNumber)
				cfg.bandSetsList[bandSetNumber][0] = "Yes"
				cfg.bst.setSatelliteWavelength(cfg.satSentinel3, bandSetList, bandSetNumber)				
				if bandSetNumber == None:
					bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
				tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
				tW.clearSelection()
			cfg.bst.bandSetTools(oDir)
			cfg.uiUtls.updateBar(100)
		if batch == "No":
			cfg.utls.finishSound()
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()

	# conversion to Reflectance
	def sentinel3reflectance(self, bandNumber, inputRaster, scale_factor, add_offset, fillValue, eSun, SZA, date, outputRaster):
		DOScheck = "Yes"
		if cfg.ui.DOS1_checkBox_S3.isChecked() is True and cfg.ui.DOS1_bands_checkBox_S2_2.isChecked() is True:
			if str(bandNumber) in ["1", "2", "3", "4", "5", "6"]:
				DOScheck = "Yes"
			else:
				DOScheck = "No"
		eSD = None
		# date format
		dFmt = "%Y-%m-%d"
		try:
			eSD = float(cfg.utls.calculateEarthSunDistance(date, dFmt))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# cosine solar zenith angle
		sA = cfg.np.cos(SZA * cfg.np.pi / 180)
		x = bandNumber
		# temp files
		dT = cfg.utls.getTime()
		tPMN = cfg.reflectanceRasterNm + ".tif"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		tPMN2 = cfg.reflectanceRasterNm + "2.tif"
		tPMD2 = cfg.tmpDir + "/" + dT + tPMN2
		# No data value
		if cfg.ui.S3_nodata_checkBox.isChecked() is True:
			nD = cfg.ui.S2_nodata_spinBox_2.value()
		else:
			nD = cfg.NoDataVal
		# TOA reflectance with correction for sun angle
		if cfg.ui.DOS1_checkBox_S3.isChecked() is False or DOScheck == "No":
			try:
				m = float(scale_factor)
				a = float(add_offset)
				# open input with GDAL
				rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)	
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
				cfg.uiUtls.updateBar(40)
				cfg.QtWidgetsSCP.qApp.processEvents()
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) * " + str("%.16f" % cfg.np.pi) + " * " + str("%.16f" % eSD) + " * " + str("%.16f" % eSD) + "/ (" + str("%.16f" % eSun)+ " * " + str(sA) + " ) )", "raster", "TOA b" + str(x))
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
		# DOS atmospheric correction
		elif cfg.ui.DOS1_checkBox_S3.isChecked() is True:
			DNm = cfg.utls.findDNmin(inputRaster, nD)
			# calculate DOS1 corrected reflectance
			try:
				# radiance calculation
				m = float(scale_factor)
				a = float(add_offset)
				# open input with GDAL
				rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
				cfg.uiUtls.updateBar(40)
				cfg.QtWidgetsSCP.qApp.processEvents()
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", (raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")))", "raster", "radiance b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				# path radiance Lp = ML* DNm + AL  – 0.01* ESUNλ * cosθs / (π * d^2)	
				Lp = m * DNm + a - 0.01 * eSun * sA / (cfg.np.pi * eSD * eSD)
				# land surface reflectance ρ = [π * (Lλ - Lp) * d^2]/ (ESUNλ * cosθs)	
				# open input with GDAL
				rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD2)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster - (" + str("%.16f" % Lp) + " ) )* " + str("%.16f" % cfg.np.pi) + " * " + str("%.16f" % eSD) + " * " + str("%.16f" % eSD) + " / ( " + str("%.16f" % eSun)+ " * " + str(sA) + " )", "raster", "DOS1 b" + str(x))
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
			
	# georeference image
	def georeferenceImage(self, bandNumber, inputImage, output, RasterXSize, RasterYSize, gcpList, gcpProj, nodataValue):
		cK = "Yes"
		# temp files
		dT = cfg.utls.getTime()
		tPMN = cfg.reflectanceRasterNm + "g" + ".tif"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		band = cfg.np.zeros([RasterYSize, RasterXSize])
		tD = cfg.gdalSCP.GetDriverByName('GTiff')		
		oD = tD.Create(tPMD, RasterXSize, RasterYSize, 1, cfg.gdalSCP.GDT_Float32)
		oD.SetProjection(gcpProj)
		oD.SetGCPs(gcpList, gcpProj)
		# output rasters
		oMR = []
		oMR.append(oD)
		oBnd = oD.GetRasterBand(1)
		oBnd.SetNoDataValue(nodataValue)
		oBnd.Fill(nodataValue)
		# open input with GDAL
		rD = cfg.gdalSCP.Open(inputImage)
		# band list
		bL = cfg.utls.readAllBandsFromRaster(rD)
		cfg.uiUtls.updateBar(50)
		cfg.QtWidgetsSCP.qApp.processEvents()
		try:
			o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", " raster * 1", "raster", "Georeferencing b" + str(bandNumber))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cK = "No"
		# close GDAL rasters
		for b in range(0, len(oMR)):
			oMR[b] = None
		for b in range(0, len(bL)):
			bL[b] = None
		rD = None
		oBnd = None
		oD = None
		cfg.utls.GDALReprojectRaster(tPMD, output, "GTiff", None, "EPSG:4326", "-ot Float32 -dstnodata " + str(nodataValue))
		try:
			cfg.osSCP.remove(tPMD)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files deleted")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		return cK
	
	# raster reclassification <0 and >1
	def reclassRaster0min1max(self, inputRaster, outputRaster):
		# register drivers
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
						