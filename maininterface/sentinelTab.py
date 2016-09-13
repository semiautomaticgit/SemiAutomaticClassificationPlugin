# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2016 by Luca Congedo
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

from qgis.core import *
from qgis.gui import *
cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

class Sentinel2Tab:

	def __init__(self):
		pass
		
	# Sentinel-2 input
	def inputSentinel(self):
		i = cfg.utls.getExistingDirectory(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		cfg.ui.S2_label_86.setText(unicode(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(i))
		
	# XML input MTD_SAFL1C
	def inputXML2(self):
		m = cfg.utls.getOpenFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a XML file"), "", "XML file .xml (*.xml)")
		cfg.ui.S2_label_94.setText(unicode(m))
		if len(cfg.ui.S2_label_86.text()) > 0:
			self.populateTable(cfg.ui.S2_label_86.text())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(m))
			
	# populate table
	def populateTable(self, input, batch = "No"):
		check = "Yes"
		sat = "Sentinel-2A"
		# dt = ""
		# sE = ""
		# esd = ""
		dEsunB = {}
		dEsunB = {"ESUN_BAND01": 1913.57, "ESUN_BAND02": 1941.63, "ESUN_BAND03": 1822.61, "ESUN_BAND04": 1512.79, "ESUN_BAND05": 1425.56, "ESUN_BAND06": 1288.32, "ESUN_BAND07": 1163.19, "ESUN_BAND08": 1036.39, "ESUN_BAND8A": 955.19, "ESUN_BAND09": 813.04, "ESUN_BAND10": 367.15, "ESUN_BAND11": 245.59, "ESUN_BAND12": 85.25}
		quantVal = 10000
		dU = 1
		cfg.ui.S2_satellite_lineEdit.setText(sat)
		# cfg.ui.S2_date_lineEdit.setText(dt)
		# cfg.ui.S2_sun_zenith_lineEdit.setText(sE)
		# cfg.ui.S2_earth_sun_dist_lineEdit.setText(esd)
		l = cfg.ui.sentinel_2_tableWidget
		cfg.utls.setColumnWidthList(l, [[0, 450]])
		cfg.utls.clearTable(l)
		inp = input
		if len(inp) == 0:
			cfg.mx.msg14()
		else:
			if batch == "No":
				cfg.uiUtls.addProgressBar()
			# if len(cfg.ui.S2_label_92.text()) == 0:
				# for f in cfg.osSCP.listdir(inp):
					# if f.lower().endswith(".xml") and "_mtd_l1c_" in f.lower():
							# MTD_L1C = inp + "/" + str(f)
			# else:
				# MTD_L1C = cfg.ui.S2_label_92.text()
			# # open metadata file
			# try:
				# doc = cfg.minidomSCP.parse(MTD_L1C)
				# SENSING_TIME = doc.getElementsByTagName("SENSING_TIME")[0]
				# dt = SENSING_TIME.firstChild.data
				# cfg.ui.S2_date_lineEdit.setText(dt[0:10])
				# if esd == "":
					# # date format
					# dFmt = "%Y-%m-%d"
					# esd = str(cfg.utls.calculateEarthSunDistance(dt[0:10], dFmt))
				# cfg.ui.S2_earth_sun_dist_lineEdit.setText(esd)
				# ZENITH_ANGLE = doc.getElementsByTagName("ZENITH_ANGLE")[0]
				# zA = ZENITH_ANGLE.firstChild.data
				# # Zenith
				# cfg.ui.S2_sun_zenith_lineEdit.setText(zA)
			# except Exception, err:
				# # logger
				# cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + unicode(err))
				# if batch == "No":
					# cfg.uiUtls.removeProgressBar()
				# cfg.mx.msgErr51()
				# check = "No"
			if len(cfg.ui.S2_label_94.text()) == 0:
				for f in cfg.osSCP.listdir(inp):
					if f.lower().endswith(".xml") and "_mtd_safl1c_" in f.lower():
							MTD_SAFL1C = inp + "/" + str(f)
			else:
				MTD_SAFL1C = cfg.ui.S2_label_94.text()
			# open metadata file
			try:
				doc2 = cfg.minidomSCP.parse(MTD_SAFL1C)
				SPACECRAFT_NAME = doc2.getElementsByTagName("SPACECRAFT_NAME")[0]
				sat = SPACECRAFT_NAME.firstChild.data
				cfg.ui.S2_satellite_lineEdit.setText(sat)
				paramU = doc2.getElementsByTagName("U")[0]
				dU = paramU.firstChild.data
				QUANTIFICATION_VALUE = doc2.getElementsByTagName("QUANTIFICATION_VALUE")[0]
				quantVal = QUANTIFICATION_VALUE.firstChild.data
				SOLAR_IRRADIANCE = doc2.getElementsByTagName("SOLAR_IRRADIANCE")
				dEsunB = {"ESUN_BAND01": SOLAR_IRRADIANCE[0].firstChild.data, "ESUN_BAND02": SOLAR_IRRADIANCE[1].firstChild.data, "ESUN_BAND03": SOLAR_IRRADIANCE[2].firstChild.data, "ESUN_BAND04": SOLAR_IRRADIANCE[3].firstChild.data, "ESUN_BAND05": SOLAR_IRRADIANCE[4].firstChild.data, "ESUN_BAND06": SOLAR_IRRADIANCE[5].firstChild.data, "ESUN_BAND07": SOLAR_IRRADIANCE[6].firstChild.data, "ESUN_BAND08": SOLAR_IRRADIANCE[7].firstChild.data, "ESUN_BAND8A": SOLAR_IRRADIANCE[8].firstChild.data, "ESUN_BAND09": SOLAR_IRRADIANCE[9].firstChild.data, "ESUN_BAND10": SOLAR_IRRADIANCE[10].firstChild.data, "ESUN_BAND11": SOLAR_IRRADIANCE[11].firstChild.data, "ESUN_BAND12": SOLAR_IRRADIANCE[12].firstChild.data}
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + unicode(err))
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar21()
				check = "No"
			# bands
			dBs = {}
			bandNames = []
			for f in cfg.osSCP.listdir(inp):
				if f.lower().endswith(".jp2"):
					# name
					nm = cfg.osSCP.path.splitext(f)[0]
					bandNames.append(f)
			# add band items to table
			b = 0
			for band in sorted(bandNames):
				l.insertRow(b)
				l.setRowHeight(b, 20)
				cfg.utls.addTableItem(l, band, b, 0, "No")
				cfg.utls.addTableItem(l, quantVal, b, 1)
				eS = str(dEsunB["ESUN_BAND" + str(band[-6:-4])])				
				cfg.utls.addTableItem(l, eS, b, 2)
				b = b + 1
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
			
	# edited satellite
	def editedSatellite(self):
		sat = cfg.ui.S2_satellite_lineEdit.text()
		if str(sat).lower() in ['sentinel_2a', 'sentinel-2a', 'sentinel_2b', 'sentinel-2b']:
			cfg.ui.S2_satellite_lineEdit.setStyleSheet("color : black")
		else:
			cfg.ui.S2_satellite_lineEdit.setStyleSheet("color : red")
	
	# remove band
	def removeHighlightedBand(self):
		l = cfg.ui.sentinel_2_tableWidget
		cfg.utls.removeRowsFromTable(l)

	# edited cell
	def editedCell(self, row, column):
		if column != 0:
			l = cfg.ui.sentinel_2_tableWidget
			val = l.item(row, column).text()
			try:
				float(val)
			except:
				l.item(row, column).setText("")

	# sentinel-2 output
	def performSentinelConversion(self):
		if len(cfg.ui.S2_label_86.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.sentinel2(cfg.ui.S2_label_86.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Perform sentinel-2 conversion: " + unicode(cfg.ui.S2_label_86.text()))
		
	# sentinel-2 conversion
	def sentinel2(self, inputDirectory, outputDirectory, batch = "No"):
		cfg.uiUtls.addProgressBar()
		# disable map canvas render for speed
		if batch == "No":
			cfg.cnvs.setRenderFlag(False)
		self.sA = ""
		self.eSD = ""
		sat = cfg.ui.S2_satellite_lineEdit.text()
		if str(sat) == "":
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No satellite error")
			if batch == "No":
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
			cfg.mx.msgErr37()
			return "No"
		cfg.uiUtls.updateBar(5)	
		l = cfg.ui.sentinel_2_tableWidget
		inp = inputDirectory
		out = outputDirectory
		if cfg.QDirSCP(out).exists():
			pass
		else:
			cfg.osSCP.makedirs(out)
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
		# multispectral raster list
		rasterList = []
		# band list
		bandSetList = []
		bandSetNameList = []
		bandNumberList = []
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				bNm = str(l.item(i,0).text()[0:-4])
				bNmb = str(l.item(i,0).text()[-6:-4])
				inputRaster = inp + "/" + l.item(i,0).text()				
				oNm = pre + bNm
				outputRaster = out + "/" + oNm + ".tif"
				outputRasterList.append(outputRaster)
				quantificationValue = float(l.item(i,1).text())
				ESUN = float(l.item(i,2).text())
				if str(bNmb).lower() in ['02','03','04','05','06','07','08','8a','11','12']:
					if str(bNmb).lower() == '02':
						bandSetList.append(1)
					elif str(bNmb).lower() == '03':
						bandSetList.append(2)
					elif str(bNmb).lower() == '04':
						bandSetList.append(3)
					elif str(bNmb).lower() == '05':
						bandSetList.append(4)
					elif str(bNmb).lower() == '06':
						bandSetList.append(5)
					elif str(bNmb).lower() == '07':
						bandSetList.append(6)
					elif str(bNmb).lower() == '08':
						bandSetList.append(7)
					elif str(bNmb).lower() == '8a':
						bandSetList.append(8)
					elif str(bNmb).lower() == '11':
						bandSetList.append(9)
					elif str(bNmb).lower() == '12':
						bandSetList.append(10)
					bandSetNameList.append(oNm)
				# conversion
				ck = self.sentinelReflectance(inputRaster, outputRaster, bNmb, quantificationValue)
				if ck != "No":
					rasterList.append(outputRaster)
		cfg.uiUtls.updateBar(90)
		if cfg.actionCheck == "Yes":
			# load raster bands
			for outR in outputRasterList:
				if cfg.osSCP.path.isfile(outR):
					cfg.iface.addRasterLayer(outR)
				else:
					cfg.mx.msgErr38(outR)
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "WARNING: unable to load raster" + unicode(outR))
			# create band set
			if cfg.ui.S2_create_bandset_checkBox.isChecked() is True:
				if str(sat).lower() in ['sentinel_2a', 'sentinel-2a', 'sentinel_2b', 'sentinel-2b']:
					satName = cfg.satSentinel2
				else:
					satName = "No"
				if satName != "No":
					cfg.bst.rasterBandName()
					bandSetNameList = sorted(bandSetNameList)
					bandSetNameList = [list for (number, list) in sorted(zip(bandSetList, bandSetNameList))]
					cfg.bst.setBandSet(bandSetNameList)
					cfg.bndSetPresent = "Yes"
					bandSetList = sorted(bandSetList)
					cfg.bst.setSatelliteWavelength(satName, bandSetList)
				cfg.bst.bandSetTools(out)
		cfg.uiUtls.updateBar(100)
		if batch == "No":
			cfg.utls.finishSound()
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()

	# calculate DOS1 reflectance
	def sentinelReflectance(self, inputRaster, outputRaster, bandNumber, quantificationValue):
		# date time for temp name
		dT = cfg.utls.getTime()
		tempRaster = cfg.tmpDir + "/" + dT + "sent2_temp" + bandNumber + ".tif"
		tPMN = cfg.reflectanceRasterNm + ".tif"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		if bandNumber.lower() in ["01", "09", "10"]:
			resample = "-outsize 600% 600%"
		elif bandNumber.lower() in ["05", "06", "07", "8a", "11", "12"]:
			resample = "-outsize 200% 200%"
		else:
			resample = ""
		radC = 1 / float(quantificationValue)
		try:
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# output rasters
			oM = []
			oM.append(tPMD)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No")
			# No data value
			if cfg.ui.S2_nodata_checkBox.isChecked() is True:
				nD = cfg.ui.S2_nodata_spinBox.value()
			else:
				nD = cfg.NoDataVal
			if cfg.ui.DOS1_checkBox_S2.isChecked() is True:
				# No data value
				if cfg.ui.S2_nodata_checkBox.isChecked() is True:
					nD = cfg.ui.S2_nodata_spinBox.value()
				# find DNmin
				LDNm = cfg.utls.findDNmin(inputRaster, nD)
				# calculate DOS1 corrected reflectance
				# reflectance = DN / quantificationValue = DN * radC
				# radiance = reflectance * ESUNλ * cosθs / (π * d^2) = DN * radC  * ESUNλ * cosθs / (π * d^2)
				# path radiance Lp = (LDNm * radC - 0.01) * ESUNλ * cosθs / (π * d^2)
				# land surface reflectance ρ = [π * (Lλ - Lp) * d^2]/ (ESUNλ * cosθs) = DN * radC - (LDNm * radC - 0.01)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", ( raster * " + str("%.16f" % radC) + " - (- 0.01 + " + str("%.16f" % (LDNm * radC)) + " )) )", "raster", "DOS1 b" + str(bandNumber))
			else:
				# calculate reflectance = DN / quantVal
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "cfg.np.where(raster == " + str(nD) + ", " + str(cfg.NoDataVal) + ", ( raster /" + str(quantificationValue) + ") )", "raster", "TOA b" + str(bandNumber))
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None		
			# reclassification <0 and >1
			self.reclassRaster0min1max(tPMD, tempRaster)
			cfg.utls.GDALCopyRaster(tempRaster, outputRaster, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1", resample)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + unicode(err))
			return "No"
		try:
			cfg.osSCP.remove(tPMD)
			cfg.osSCP.remove(tempRaster)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files deleted")
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(inputRaster))
		return "Yes"
			
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
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(inputRaster))
						