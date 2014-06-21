# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
 providing a tool for the region growing of image pixels, creating polygon shapefiles intended for
 the collection of training areas (ROIs), and rapidly performing the classification process (or a preview).
							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012 by Luca Congedo
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

import os
import inspect
import shutil
import numpy as np
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from osgeo import gdal
from osgeo.gdalconst import *
from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class LandsatTab:

	def __init__(self):
		pass
		
	# Landsat input
	def inputLandsat(self):
		i = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		cfg.ui.label_26.setText(str(i.encode(cfg.fSEnc)))
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(i.encode(cfg.fSEnc)))

	# Landsat conversion to reflectance and temperature
	def Landsat(self, inputDirectory, outputDirectory):
		inp = inputDirectory
		out = outputDirectory
		if len(inp) == 0 or len(out) == 0:
			cfg.mx.msg14()
		else:
			cfg.uiUtls.addProgressBar()
			# date time for temp name
			dT = cfg.utls.getTime()
			# temp raster layer
			tB1 = cfg.tmpDir + "/" + "temporary_band" + dT
			tB2 = cfg.tmpDir + "/" + "tempor2_band" + dT
			tB3 = cfg.tmpDir + "/" + "tempor3_band" + dT
			# bands
			dBs = {}
			# temporary bands
			dTBs1 = {}
			dTBs2 = {}
			dTBs3 = {}
			# new bands
			dNBs = {}
			# new bands
			dNBsN = {}
			# Esun
			dEsunB = {}
			# name prefix
			pre = "RT_"
			MTL = ""
			# input dictionaries
			for f in os.listdir(inp):
				if f.lower().endswith(".tif"):
					# name
					nm = os.path.splitext(f)[0]
					# landsat 7 thermal bands
					if str(nm[len(nm) - 8: len(nm) - 1]) == "6_VCID_" and nm[len(nm) - 1].isdigit():
						dBs["BAND6_VCID_{0}".format(nm[len(nm) - 1])] = inp + "/" + str(f)
						dTBs1["TEMPBAND6_VCID_{0}".format(nm[len(nm) - 1])] = str(tB1) + pre + str(nm)
						dTBs2["TEMPBAND6_VCID_{0}".format(nm[len(nm) - 1])] = str(tB2) + pre + str(nm)
						dTBs3["TEMPBAND6_VCID_{0}".format(nm[len(nm) - 1])] = str(tB3) + pre + str(nm)
						dNBs["NEWBAND6_VCID_{0}".format(nm[len(nm) - 1])] =  out + "/" + pre + str(f)
						dNBsN["BANDNAME6_VCID_{0}".format(nm[len(nm) - 1])] =  pre + str(f)
					# for bands > 9
					elif nm[len(nm) - 2].isdigit() and nm[len(nm) - 1].isdigit():
						dBs["BAND{0}".format(nm[len(nm) - 2] + nm[len(nm) - 1])] = inp + "/" + str(f)
						dTBs1["TEMPBAND{0}".format(nm[len(nm) - 2] + nm[len(nm) - 1])] = str(tB1) + pre + str(nm)
						dTBs2["TEMPBAND{0}".format(nm[len(nm) - 2] + nm[len(nm) - 1])] = str(tB2) + pre + str(nm)
						dTBs3["TEMPBAND{0}".format(nm[len(nm) - 2] + nm[len(nm) - 1])] = str(tB3) + pre + str(nm)
						dNBs["NEWBAND{0}".format(nm[len(nm) - 2] + nm[len(nm) - 1])] =  out + "/" + pre + str(f)
						dNBsN["BANDNAME{0}".format(nm[len(nm) - 2] + nm[len(nm) - 1])] =  pre + str(f)
					# for bands < 10
					elif str(nm[len(nm) - 8: len(nm) - 1]) != "6_VCID_" and nm[len(nm) - 1].isdigit():
						dBs["BAND{0}".format(nm[len(nm) - 1])] = inp + "/" + str(f)
						dTBs1["TEMPBAND{0}".format(nm[len(nm) - 1])] = str(tB1) + pre + str(nm)
						dTBs2["TEMPBAND{0}".format(nm[len(nm) - 1])] = str(tB2) + pre + str(nm)
						dTBs3["TEMPBAND{0}".format(nm[len(nm) - 1])] = str(tB3) + pre + str(nm)
						dNBs["NEWBAND{0}".format(nm[len(nm) - 1])] =  out + "/" + pre + str(f)
						dNBsN["BANDNAME{0}".format(nm[len(nm) - 1])] =  pre + str(f)
				if f.lower().endswith(".txt") and "mtl" in f.lower():
						MTLFile = inp + "/" + str(f)
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Bands found: " + str(dBs))
			if len(dNBsN) == 0:
				cfg.mx.msgErr9()
			cfg.uiUtls.updateBar(5)
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
			sat = "No"
			# open MTL file
			try:
				MTL = open(MTLFile, "r")
				check = "Yes"
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msgErr8()
				check = "No"
			# get information from MTL
			for r in MTL:
				# satellite
				if "SPACECRAFT_ID" in r.split():
					rV = r.split()[2]
					sat = str(rV)
				# landsat 8
				for x in range(1, 12):
					# for conversion to TOA Radiance from https://landsat.usgs.gov/Landsat8_Using_Product.php
					if "RADIANCE_MULT_BAND_" + str(x) in r.split():
						rV = r.split()[2]
						dRadMB["RADIANCE_MULT_BAND{0}".format(x)] = float(rV)
					if "RADIANCE_ADD_BAND_" + str(x) in r.split():
						rV = r.split()[2]
						dRadAB["RADIANCE_ADD_BAND{0}".format(x)] = float(rV)
					if "RADIANCE_MULT_BAND_6_VCID_" + str(x) in r.split():
						rV = r.split()[2]
						dRadMB["RADIANCE_MULT_BAND_6_VCID{0}".format(x)] = float(rV)
					if "RADIANCE_ADD_BAND_6_VCID_" + str(x) in r.split():
						rV = r.split()[2]
						dRadAB["RADIANCE_ADD_BAND_6_VCID{0}".format(x)] = float(rV)
					# for conversion to TOA Reflectance
					if "REFLECTANCE_MULT_BAND_" + str(x) in r.split():
						rV = r.split()[2]
						dRefMB["REFLECTANCE_MULT_BAND{0}".format(x)] = float(rV)
					if "REFLECTANCE_ADD_BAND_" + str(x) in r.split():
						rV = r.split()[2]
						dRefAB["REFLECTANCE_ADD_BAND{0}".format(x)] = float(rV)
					# for At-Satellite Brightness Temperature
					if "K1_CONSTANT_BAND_" + str(x) in r.split():
						rV = r.split()[2]
						dK1B["K1_CONSTANT_BAND{0}".format(x)] = float(rV)
					if "K2_CONSTANT_BAND_" + str(x) in r.split():
						rV = r.split()[2]
						dK2B["K2_CONSTANT_BAND{0}".format(x)] = float(rV)
					# for Esun calculation
					if "RADIANCE_MAXIMUM_BAND_" + str(x) in r.split():
						rV = r.split()[2]
						dRadMxB["RADIANCE_MAXIMUM_BAND{0}".format(x)] = float(rV)
					if "REFLECTANCE_MAXIMUM_BAND_" + str(x) in r.split():
						rV = r.split()[2]
						dRefMxB["REFLECTANCE_MAXIMUM_BAND{0}".format(x)] = float(rV)
				if "SUN_ELEVATION" in r.split():
					rV = r.split()[2]
					sE = float(rV)
					sA = np.sin(sE * np.pi / 180)
				if "EARTH_SUN_DISTANCE" in r.split():
					rV = r.split()[2]
					# earthSun distance
					eSD = float(rV)
				if "DATE_ACQUIRED" in r.split() or "ACQUISITION_DATE" in r.split():
					rV = r.split()[2]
					dt = str(rV)
			try:
				MTL.close()
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			# DOS atmospheric correction
			DOS = "No"
			if cfg.ui.DOS1_checkBox.isChecked() is True:
				DOS = "DOS1"
				DNm = 0
			# Kelvin or cs
			cs = 0
			if cfg.ui.celsius_checkBox.isChecked() is True:
				cs = 273.15
			qApp.processEvents()
			# Landsat 5 or Landsat 7
			if str(sat) == '"LANDSAT_4"' or str(sat) == '"Landsat4"' or str(sat) == '"LANDSAT_5"' or str(sat) == '"Landsat5"' or str(sat) == '"LANDSAT_7"' or str(sat) == '"Landsat7"':
				# date format
				dFmt = "%Y-%m-%d"
				eSD = cfg.utls.calculateEarthSunDistance(dt, dFmt)
				if str(sat) == '"LANDSAT_4"' or str(sat) == '"Landsat4"' :
					# Esun from Chander, G. & Markham, B. Revised Landsat-5 TM radiometric calibration procedures and postcalibration dynamic ranges Geoscience and Remote Sensing, IEEE Transactions on, 2003, 41, 2674 - 2677
					dEsunB = {"ESUN_BAND1": 1957, "ESUN_BAND2": 1825, "ESUN_BAND3": 1557, "ESUN_BAND4": 1033, "ESUN_BAND5": 214.9, "ESUN_BAND7": 80.72}
					# k1 and k2 from Chander, G. & Markham, B. Revised Landsat-5 TM radiometric calibration procedures and postcalibration dynamic ranges Geoscience and Remote Sensing, IEEE Transactions on, 2003, 41, 2674 - 2677
					k1 = float(671.62)
					k2 = float(1284.30)
					# At-Satellite Brightness Temperature
					try:
						m = float(dRadMB["RADIANCE_MULT_BAND6"])
						a = float(dRadAB["RADIANCE_ADD_BAND6"])
						# open input with GDAL
						rD = gdal.Open(dBs["BAND6"], GA_ReadOnly)
						# band list
						bL = cfg.utls.readAllBandsFromRaster(rD)
						# output rasters
						oM = []
						# temp files
						tPMD = dTBs1["TEMPBAND6"] + ".tif"
						oM.append(tPMD)
						oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
						o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "((" + str("%.16f" % k2) + ") / ( ln( (" + str("%.16f" % k1) + " / ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) ) + 1)) - " + str(cs) + ")", "raster")
						# close GDAL rasters
						for b in range(0, len(oMR)):
							oMR[b] = None
						for b in range(0, len(bL)):
							bL[b] = None
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(dBs["BAND6"]))
					except Exception, err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				if str(sat) == '"LANDSAT_5"' or str(sat) == '"Landsat5"':
					# Esun from Finn, M.P., Reed, M.D, and Yamamoto, K.H. A Straight Forward Guide for Processing Radiance and Reflectance for EO-1 ALI, Landsat 5 TM, Landsat 7 ETM+, and ASTER. Unpublished Report from USGS/Center of Excellence for Geospatial Information Science, 8 p. 2012
					dEsunB = {"ESUN_BAND1": 1983, "ESUN_BAND2": 1796, "ESUN_BAND3": 1536, "ESUN_BAND4": 1031, "ESUN_BAND5": 220, "ESUN_BAND7": 83.44}
					# k1 and k2 from Chander, G. & Markham, B. Revised Landsat-5 TM radiometric calibration procedures and postcalibration dynamic ranges Geoscience and Remote Sensing, IEEE Transactions on, 2003, 41, 2674 - 2677
					k1 = float(607.76)
					k2 = float(1260.56)
					# At-Satellite Brightness Temperature
					try:
						m = float(dRadMB["RADIANCE_MULT_BAND6"])
						a = float(dRadAB["RADIANCE_ADD_BAND6"])
						# open input with GDAL
						rD = gdal.Open(dBs["BAND6"], GA_ReadOnly)
						# band list
						bL = cfg.utls.readAllBandsFromRaster(rD)
						# output rasters
						oM = []
						# temp files
						tPMD = dTBs1["TEMPBAND6"] + ".tif"
						oM.append(tPMD)
						oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
						o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "((" + str("%.16f" % k2) + ") / ( ln( (" + str("%.16f" % k1) + " / ( raster * " + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) ) + 1)) - " + str(cs) + ")", "raster")
						# close GDAL rasters
						for b in range(0, len(oMR)):
							oMR[b] = None
						for b in range(0, len(bL)):
							bL[b] = None
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(),  str(dBs["BAND6"]))
					except Exception, err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				if str(sat) == '"LANDSAT_7"' or str(sat) == '"Landsat7"':
					# Esun from Finn, M.P., Reed, M.D, and Yamamoto, K.H. A Straight Forward Guide for Processing Radiance and Reflectance for EO-1 ALI, Landsat 5 TM, Landsat 7 ETM+, and ASTER. Unpublished Report from USGS/Center of Excellence for Geospatial Information Science, 8 p. 2012
					dEsunB = {"ESUN_BAND1": 1997, "ESUN_BAND2": 1812, "ESUN_BAND3": 1533, "ESUN_BAND4": 1039, "ESUN_BAND5": 230.08, "ESUN_BAND7": 84.9}
					# k1 and k2 from NASA (Ed.) Landsat 7 Science Data Users Handbook Landsat Project Science Office at NASA's Goddard Space Flight Center in Greenbelt, pp.186
					k1 = float(666.09)
					k2 = float(1282.71)
					# At-Satellite Brightness Temperature
					for x in (1, 2):
						try:
							m = float(dRadMB["RADIANCE_MULT_BAND_6_VCID"+ str(x)])
							a = float(dRadAB["RADIANCE_ADD_BAND_6_VCID"+ str(x)])
							# open input with GDAL
							rD = gdal.Open(dBs["BAND6_VCID_" + str(x)], GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs1["TEMPBAND6_VCID_" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "((" + str("%.16f" % k2) + ") / ( ln( (" + str("%.16f" % k1) + " / ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) ) + 1)) - " + str(cs) + ")", "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(dBs["BAND6_VCID_" + str(x)]))
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.uiUtls.updateBar(20)
				if DOS == "DOS1":
					# find DNm for each band
					for x in (1, 2, 3, 4, 5, 7):
						cfg.uiUtls.updateBar(20 + 5 * x)
						DNm = 0
						# register drivers
						gdal.AllRegister()
						try:
							# band source
							bS = dBs["BAND" + str(x)]
							ck = "Yes"
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							ck = "No"
						if ck == "Yes":
							# open input with GDAL
							rD = gdal.Open(bS, GA_ReadOnly)
							# number of x pixels
							rC = rD.RasterXSize
							# number of y pixels
							rR = rD.RasterYSize
							# get band
							rB = rD.GetRasterBand(1)
							# combinations of classes 
							rBA = rB.ReadAsArray(0, 0, rC, rR)
							rBUV = np.unique(rBA).tolist()
							# pixel sum
							pS = 0
							# No data value
							nD = cfg.ui.nodata_spinBox_3.value()
							if cfg.ui.nodata_checkBox_2.isChecked() is True:
								# pixel total
								pT = rC * rR - (rBA == nD).sum()
								pT1pc = pT * 0.0001
							else:
								pT = rC * rR
								pT1pc = pT * 0.0001
							for i in rBUV:
								if cfg.ui.nodata_checkBox_2.isChecked() is True:
									if str(i) != str(nD):
										# calculate sum of pixels
										pS = pS + (rBA == i).sum()
										if pS > pT1pc:
											DNm = i
											break
								else:
									# calculate sum of pixels
									pS = pS + (rBA == i).sum()
									if pS > pT1pc:
										DNm = i
										break
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Band: " + str(x) + " DNm " + str(DNm))
						# calculate DOS1 corrected reflectance
						try:
							m = float(dRadMB["RADIANCE_MULT_BAND" + str(x)])
							a = float(dRadAB["RADIANCE_ADD_BAND" + str(x)])
							eS = float(dEsunB["ESUN_BAND" + str(x)])
							# radiance calculation
							# open input with GDAL
							rD = gdal.Open(dBs["BAND" + str(x)], GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs2["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "(raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + "))", "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(dBs["BAND" + str(x)]))
							# path radiance Lp = ML* DNm + AL  – 0.01* ESUNλ * cosθs / (π * d^2)	
							Lp = m * DNm + a - 0.01 * eS * sA / (np.pi * eSD * eSD)
							# land surface reflectance ρ = [π * (Lλ - Lp) * d^2]/ (ESUNλ * cosθs)	
							# open input with GDAL
							rD = gdal.Open(dTBs2["TEMPBAND" + str(x)] + ".tif", GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs3["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster - (" + str("%.16f" % Lp) + ") ) * " + str("%.16f" % np.pi) + " * " + str("%.16f" % eSD) + " * " + str("%.16f" % eSD) + " / ( " + str("%.16f" % eS)+ " * (" + str(sA) + ") )", "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(dTBs2["TEMPBAND" + str(x)]) + ".tif")
							# reclassification <0 and >1
							# open input with GDAL
							rD = gdal.Open(dTBs3["TEMPBAND" + str(x)] + ".tif", GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs1["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.reclassifyRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", [["(raster < 0)", 0], ["(raster > 1)", 1]], "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					# conversion to TOA Reflectance
					for x in (1, 2, 3, 4, 5, 7):
						try:
							cfg.uiUtls.updateBar(20 + 5 * x)
							m = float(dRadMB["RADIANCE_MULT_BAND" + str(x)])
							a = float(dRadAB["RADIANCE_ADD_BAND" + str(x)])
							eS = float(dEsunB["ESUN_BAND" + str(x)])
							# radiance calculation
							# open input with GDAL
							rD = gdal.Open(dBs["BAND" + str(x)], GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs2["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + "))", "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(dBs["BAND" + str(x)]))
							# TOA Reflectance
							# open input with GDAL
							rD = gdal.Open(dTBs2["TEMPBAND" + str(x)] + ".tif", GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs3["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster * " + str("%.16f" % np.pi) + " * " + str("%.16f" % eSD) + " * " + str("%.16f" % eSD) + ") / ( " + str("%.16f" % eS)+ " * (" + str(sA) + ") )", "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(dTBs3["TEMPBAND" + str(x)]))
							# reclassification <0 and >1
							rD = gdal.Open(dTBs3["TEMPBAND" + str(x)] + ".tif", GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs1["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.reclassifyRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", [["(raster < 0)", 0], ["(raster > 1)", 1]], "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(dTBs1["TEMPBAND" + str(x)]))
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			# Landsat 8	
			elif str(sat) == '"LANDSAT_8"':
				if DOS == "DOS1":
					# find DNm for each band (skipping band 8)
					for x in (1, 2, 3, 4, 5, 6, 7, 9):
						cfg.uiUtls.updateBar(5 + 5 * x)
						DNm = 0
						# Esun calculation (see http://grass.osgeo.org/grass65/manuals/i.landsat.toar.html)
						radM = float(dRadMxB["RADIANCE_MAXIMUM_BAND" + str(x)])
						refM = float(dRefMxB["REFLECTANCE_MAXIMUM_BAND" + str(x)])
						dEsunB["ESUN_BAND{0}".format(x)] = (np.pi * eSD * eSD) * radM / refM
						# register drivers
						gdal.AllRegister()
						try:
							bS = dBs["BAND" + str(x)]
							ck = "Yes"
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							ck = "No"
						if ck == "Yes":
							# open input with GDAL
							rD = gdal.Open(bS, GA_ReadOnly)
							# number of x pixels
							rC = rD.RasterXSize
							# number of y pixels
							rR = rD.RasterYSize
							# get band
							rB = rD.GetRasterBand(1)
							# combinations of classes 
							rBA = rB.ReadAsArray(0, 0, rC, rR)
							rBUV = np.unique(rBA).tolist()
							pS = 0
							# No data value
							nD = cfg.ui.nodata_spinBox_3.value()
							if cfg.ui.nodata_checkBox_2.isChecked() is True:
								pT = rC * rR - (rBA == nD).sum()
								pT1pc = pT * 0.0001
							else:
								pT = rC * rR
								pT1pc = pT * 0.0001
							for i in rBUV:
								if cfg.ui.nodata_checkBox_2.isChecked() is True:
									if str(i) != str(nD):
										# calculate sum of pixels
										pS = pS + (rBA == i).sum()
										if pS > pT1pc:
											DNm = i
											break
								else:
									# calculate sum of pixels
									pS = pS + (rBA == i).sum()
									if pS > pT1pc:
										DNm = i
										break
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Band: " + str(x) + " DNm " + str(DNm))
						# calculate DOS1 corrected reflectance
						try:
							m = float(dRadMB["RADIANCE_MULT_BAND" + str(x)])
							a = float(dRadAB["RADIANCE_ADD_BAND" + str(x)])
							eS = float(dEsunB["ESUN_BAND" + str(x)])
							# radiance calculation
							# open input with GDAL
							rD = gdal.Open(dBs["BAND" + str(x)], GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs2["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "(raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + "))", "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(tPMD))
							# path radiance Lp = ML* DNm + AL  – 0.01* ESUNλ * cosθs / (π * d^2)	
							Lp = m * DNm + a - 0.01 * eS * sA / (np.pi * eSD * eSD)
							# land surface reflectance ρ = [π * (Lλ - Lp) * d^2]/ (ESUNλ * cosθs)	
							# open input with GDAL
							rD = gdal.Open(dTBs2["TEMPBAND" + str(x)] + ".tif", GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs3["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster - (" + str("%.16f" % Lp) + " ) )* " + str("%.16f" % np.pi) + " * " + str("%.16f" % eSD) + " * " + str("%.16f" % eSD) + " / ( " + str("%.16f" % eS)+ " * " + str(sA) + " )", "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(tPMD))
							# reclassification <0 and >1
							# open input with GDAL
							rD = gdal.Open(dTBs3["TEMPBAND" + str(x)] + ".tif", GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs1["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.reclassifyRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", [["(raster < 0)", 0], ["(raster > 1)", 1]], "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(tPMD))
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					# conversion to TOA Reflectance (skipping band 8)
					for x in (1, 2, 3, 4, 5, 6, 7, 9):
						try:
							cfg.uiUtls.updateBar(5 + 5 * x)
							m = float(dRefMB["REFLECTANCE_MULT_BAND" + str(x)])
							a = float(dRefAB["REFLECTANCE_ADD_BAND" + str(x)])
							# open input with GDAL
							rD = gdal.Open(dBs["BAND" + str(x)], GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs3["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) / (" + str(sA) + ")", "raster")
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(dBs["BAND" + str(x)]))
							# reclassification <0 and >1
							# open input with GDAL
							rD = gdal.Open(dTBs3["TEMPBAND" + str(x)] + ".tif", GA_ReadOnly)
							# band list
							bL = cfg.utls.readAllBandsFromRaster(rD)
							# output rasters
							oM = []
							# temp files
							tPMD = dTBs1["TEMPBAND" + str(x)] + ".tif"
							oM.append(tPMD)
							oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
							o = cfg.utls.processRaster(rD, bL, None, cfg.utls.reclassifyRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", [["(raster < 0)", 0], ["(raster > 1)", 1]], "raster")
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(tPMD))
							# close GDAL rasters
							for b in range(0, len(oMR)):
								oMR[b] = None
							for b in range(0, len(bL)):
								bL[b] = None
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# At-Satellite Brightness Temperature
				for x in range(10, 12):
					try:
						cfg.uiUtls.updateBar(5 + 5 * x)
						m = float(dRadMB["RADIANCE_MULT_BAND" + str(x)])
						a = float(dRadAB["RADIANCE_ADD_BAND" + str(x)])
						k1 = float(dK1B["K1_CONSTANT_BAND" + str(x)])
						k2 = float(dK2B["K2_CONSTANT_BAND" + str(x)])
						# open input with GDAL
						rD = gdal.Open(dBs["BAND" + str(x)], GA_ReadOnly)
						# band list
						bL = cfg.utls.readAllBandsFromRaster(rD)
						# output rasters
						oM = []
						# temp files
						tPMD = dTBs1["TEMPBAND" + str(x)] + ".tif"
						oM.append(tPMD)
						oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
						o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No",  "((" + str("%.16f" % k2) + ") / ( ln( (" + str("%.16f" % k1) + " / ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) ) + 1)) - " + str(cs) + ")", "raster")
						# close GDAL rasters
						for b in range(0, len(oMR)):
							oMR[b] = None
						for b in range(0, len(bL)):
							bL[b] = None
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(tPMD))
					except Exception, err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			# copy bands to output
			cfg.uiUtls.updateBar(80)
			rasterList = []
			for x in range(1, 12):
				try:
					shutil.copy(unicode(dTBs1["TEMPBAND" + str(x)]) + ".tif", unicode(dNBs["NEWBAND" + str(x)]))
					cfg.iface.addRasterLayer(unicode(dNBs["NEWBAND" + str(x)]), unicode(dNBsN["BANDNAME" + str(x)]))
					rasterList.append(unicode(dNBs["NEWBAND" + str(x)]))
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Converted: " + str(sat) + str(dNBs["NEWBAND" + str(x)]))
				except Exception, err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			for x in (1, 2):
				try:
					shutil.copy(str(dTBs1["TEMPBAND6_VCID_" + str(x)]) + ".tif", str(dNBs["NEWBAND6_VCID_" + str(x)]))
					cfg.iface.addRasterLayer(str(dNBs["NEWBAND6_VCID_" + str(x)]), str(dNBsN["BANDNAME6_VCID_" + str(x)]))
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Converted: " + str(sat) + str(dNBs["NEWBAND6_VCID_" + str(x)]))
				except Exception, err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			# create virtual raster
			if cfg.ui.create_VRT_checkBox.isChecked() is True and check == "Yes":
				outVrt = out + "//" + cfg.landsatVrtNm + ".vrt"
				cfg.utls.createVirtualRaster(rasterList, outVrt)
				vrtRaster = cfg.iface.addRasterLayer(outVrt)
				vrtRaster.setDrawingStyle('MultiBandColor')
				vrtRaster.renderer().setRedBand(3)
				vrtRaster.renderer().setGreenBand(2)
				vrtRaster.renderer().setBlueBand(1)
			cfg.uiUtls.updateBar(100)
			cfg.ui.label_26.setText("")
			cfg.ui.label_27.setText("")
			cfg.uiUtls.removeProgressBar()
			
	# Landsat output
	def outputLandsat(self):
		o = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		cfg.ui.label_27.setText(str(o.encode(cfg.fSEnc)))
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(o.encode(cfg.fSEnc)))
		
	# Landsat correction button
	def performLandsatCorrection(self):
		self.Landsat(cfg.ui.label_26.text(), cfg.ui.label_27.text())
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Perform clicked: " + str(cfg.ui.label_26.text()) + " " + str(cfg.ui.label_27.text()))
			