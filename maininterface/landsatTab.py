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
		copyright			: (C) 2012-2015 by Luca Congedo
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
		
	# landsat input
	def inputLandsat(self):
		i = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		cfg.ui.label_26.setText(unicode(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(i))
		
	# MTL input
	def inputMTL(self):
		m = QFileDialog.getOpenFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Select a MTL file"), "", "MTL file .txt (*.txt);;MTL file .met (*.met)")
		cfg.ui.label_27.setText(unicode(m))
		if len(cfg.ui.label_26.text()) > 0:
			self.populateTable(cfg.ui.label_26.text())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(m))

	# landsat conversion to reflectance and temperature
	def landsat(self, inputDirectory, outputDirectory):
		cfg.uiUtls.addProgressBar()
		# disable map canvas render for speed
		cfg.cnvs.setRenderFlag(False)
		self.sA = ""
		self.eSD = ""
		sat = cfg.ui.satellite_lineEdit.text()
		if str(sat) == "":
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No satellite error")
			cfg.uiUtls.removeProgressBar()
			cfg.mx.msgErr37()
			cfg.cnvs.setRenderFlag(True)
			return "No"
		if len(cfg.ui.sun_elev_lineEdit.text()) > 0:
			sE = float(cfg.ui.sun_elev_lineEdit.text())
			# sine sun elevation
			self.sA = np.sin(sE * np.pi / 180)
		else:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No sun elevation error")
			cfg.uiUtls.removeProgressBar()
			cfg.mx.msgErr37()
			return "No"
		# earth sun distance
		if len(cfg.ui.earth_sun_dist_lineEdit.text()) > 0:
			try:
				self.eSD = float(cfg.ui.earth_sun_dist_lineEdit.text())
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " No earth sun distance error")
				cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr37()
				cfg.cnvs.setRenderFlag(True)
				return "No"
		if len(str(self.eSD)) == 0:
			dFmt = "%Y-%m-%d"
			dt = cfg.ui.date_lineEdit.text()
			try:
				self.eSD = cfg.utls.calculateEarthSunDistance(dt, dFmt)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr37()
				cfg.cnvs.setRenderFlag(True)
				return "No"
		cfg.uiUtls.updateBar(5)	
		l = cfg.ui.landsat_tableWidget
		inp = inputDirectory
		out = outputDirectory
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
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				inputRaster = inp + "/" + l.item(i,0).text()
				oNm = pre + l.item(i,0).text()
				outputRaster = out + "/" + oNm
				outputRasterList.append(outputRaster)
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
				nm = os.path.splitext(bandName)[0]
				if str(sat).lower() in ['landsat_4', 'landsat4', 'landsat_5', 'landsat5', 'landsat_7', 'landsat7']:
					# landsat bands (e.g. b10, b20, b61)
					if nm[len(nm) - 2].isdigit() and nm[len(nm) - 1].isdigit():
						if str(nm[len(nm) - 1]) == "0":
							ck = self.landsat457reflectance(sat, str(nm[len(nm) - 2]), RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
							if ck != "No":
								rasterList.append(outputRaster)
								# band list
								if int(nm[len(nm) - 1]) in [1, 2, 3, 4, 5]:
									bandSetList.append(int(nm[len(nm) - 1]))
									bandSetNameList.append(os.path.splitext(oNm)[0])
								elif int(nm[len(nm) - 1]) == 7:
									bandSetList.append(6)
									bandSetNameList.append(os.path.splitext(oNm)[0])
						# landsat thermal bands
						elif str(nm[len(nm) - 2]) == "6":
							self.landsat457Temperature(sat, RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
					# landsat bands (e.g. b1, b2, b6_VCID_1)
					elif str(nm[len(nm) - 8: len(nm) - 1]) != "6_VCID_" and nm[len(nm) - 1].isdigit():
						# landsat thermal bands
						if str(nm[len(nm) -1]) == "6":
							self.landsat457Temperature(sat, RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
						else:
							ck = self.landsat457reflectance(sat, str(nm[len(nm) - 1]), RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
							if ck != "No":
								rasterList.append(outputRaster)
								# band list
								if int(nm[len(nm) - 1]) in [1, 2, 3, 4, 5]:
									bandSetList.append(int(nm[len(nm) - 1]))
									bandSetNameList.append(os.path.splitext(oNm)[0])
								elif int(nm[len(nm) - 1]) == 7:
									bandSetList.append(6)
									bandSetNameList.append(os.path.splitext(oNm)[0])
					# landsat thermal bands
					elif str(nm[len(nm) - 8: len(nm) - 1]) == "6_VCID_" and nm[len(nm) - 1].isdigit():
						self.landsat457Temperature(sat, RADIANCE_MULT, RADIANCE_ADD, inputRaster, tempRaster)
				elif str(sat).lower() in ['landsat8', 'landsat_8']:
					# for bands < 10
					if str(nm[len(nm) - 8: len(nm) - 1]) != "6_VCID_" and nm[len(nm) - 1].isdigit():
						ck = self.landsat8reflectance(sat, str(nm[len(nm) - 1]), REFLECTANCE_MULT, REFLECTANCE_ADD, RADIANCE_MULT, RADIANCE_ADD, RADIANCE_MAXIMUM, REFLECTANCE_MAXIMUM, inputRaster, tempRaster)
						if ck != "No":
							rasterList.append(outputRaster)
							# band list
							if int(nm[len(nm) - 1]) in [2, 3, 4, 5, 6, 7]:
								bandSetList.append(int(nm[len(nm) - 1]) - 1)
								bandSetNameList.append(os.path.splitext(oNm)[0])
					# landsat thermal bands
					elif nm[len(nm) - 2].isdigit() and nm[len(nm) - 1].isdigit():
						self.landsat8Temperature(RADIANCE_MULT, RADIANCE_ADD, K1_CONSTANT, K2_CONSTANT, inputRaster, tempRaster)
		cfg.uiUtls.updateBar(90)
		if cfg.actionCheck == "Yes":
			# copy raster bands
			bN = 0
			for temp in tempRasterList:
				try:
					shutil.copy(temp, outputRasterList[bN])
				except Exception, err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				bN = bN + 1
		if cfg.actionCheck == "Yes":
			# load raster bands
			for outR in outputRasterList:
				if os.path.isfile(outR):
					cfg.iface.addRasterLayer(outR)
				else:
					cfg.mx.msgErr38(outR)
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "WARNING: unable to load raster" + str(outR))
			# create band set
			if cfg.ui.create_bandset_checkBox.isChecked() is True:
				if str(sat).lower() in ['landsat8', 'landsat_8']:
					satName = cfg.satLandsat8
				elif str(sat).lower() in ['landsat_7', 'landsat7']:
					satName = cfg.satLandsat7
				elif str(sat).lower() in ['landsat_4', 'landsat4', 'landsat_5', 'landsat5']:
					satName = cfg.satLandsat45
				else:
					satName = "No"
				if satName != "No":
					cfg.bst.rasterBandName()
					cfg.bst.setBandSet(bandSetNameList)
					cfg.bndSetPresent = "Yes"
					cfg.bst.setSatelliteWavelength(satName, bandSetList)
					
					
			# create virtual raster
			if cfg.ui.create_VRT_checkBox.isChecked() is True:
				outVrt = out + "//" + cfg.landsatVrtNm + ".vrt"
				vrtCheck = cfg.utls.createVirtualRaster(rasterList, outVrt)
				if vrtCheck == "No":
					vrtRaster = cfg.iface.addRasterLayer(outVrt)
					if vrtRaster is not None:
						vrtRaster.setDrawingStyle('MultiBandColor')
						vrtRaster.renderer().setRedBand(3)
						vrtRaster.renderer().setGreenBand(2)
						vrtRaster.renderer().setBlueBand(1)
						vrtRaster.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, QgsRaster.ContrastEnhancementCumulativeCut)
						vrtRaster.triggerRepaint()
					else:
						cfg.mx.msgWar13()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "WARNING: unable to load virtual raster")
			cfg.utls.finishSound()
			cfg.uiUtls.updateBar(100)
		cfg.cnvs.setRenderFlag(True)
		cfg.uiUtls.removeProgressBar()

	# landsat 8 conversion to Reflectance
	def landsat8reflectance(self, satellite, bandNumber, REFLECTANCE_MULT_BAND, REFLECTANCE_ADD_BAND, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, RADIANCE_MAXIMUM_BAND, REFLECTANCE_MAXIMUM_BAND, inputRaster, outputRaster):
		sat = satellite
		x = bandNumber
		# temp files
		dT = cfg.utls.getTime()
		tPMN = cfg.reflectanceRasterNm + ".tif"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		tPMN2 = cfg.reflectanceRasterNm + "2.tif"
		tPMD2 = cfg.tmpDir + "/" + dT + tPMN2
		# register drivers
		gdal.AllRegister()
		# TOA reflectance
		if cfg.ui.DOS1_checkBox.isChecked() is False:
			try:
				m = float(REFLECTANCE_MULT_BAND)
				a = float(REFLECTANCE_ADD_BAND)
				# open input with GDAL
				rD = gdal.Open(inputRaster, GA_ReadOnly)	
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) / (" + str(self.sA) + ")", "raster", "TOA b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				# reclassification <0 and >1
				self.reclassRaster0min1max(tPMD, outputRaster)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(inputRaster))
				return "Yes"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + unicode(err))
				return "No"
		# DOS atmospheric correction
		elif cfg.ui.DOS1_checkBox.isChecked() is True:
			DNm = self.findDNmin(inputRaster)
			# Esun calculation (see http://grass.osgeo.org/grass65/manuals/i.landsat.toar.html)
			radM = float(RADIANCE_MAXIMUM_BAND)
			refM = float(REFLECTANCE_MAXIMUM_BAND)
			eS = (np.pi * self.eSD * self.eSD) * radM / refM
			# calculate DOS1 corrected reflectance
			try:
				# radiance calculation
				m = float(RADIANCE_MULT_BAND)
				a = float(RADIANCE_ADD_BAND)
				# open input with GDAL
				rD = gdal.Open(inputRaster, GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "(raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + "))", "raster", "radiance b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				# path radiance Lp = ML* DNm + AL  – 0.01* ESUNλ * cosθs / (π * d^2)	
				Lp = m * DNm + a - 0.01 * eS * self.sA / (np.pi * self.eSD * self.eSD)
				# land surface reflectance ρ = [π * (Lλ - Lp) * d^2]/ (ESUNλ * cosθs)	
				# open input with GDAL
				rD = gdal.Open(tPMD, GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD2)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster - (" + str("%.16f" % Lp) + " ) )* " + str("%.16f" % np.pi) + " * " + str("%.16f" % self.eSD) + " * " + str("%.16f" % self.eSD) + " / ( " + str("%.16f" % eS)+ " * " + str(self.sA) + " )", "raster", "DOS1 b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				# reclassification <0 and >1
				self.reclassRaster0min1max(tPMD2, outputRaster)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(inputRaster))
				return "Yes"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
				
	# raster reclassification <0 and >1
	def reclassRaster0min1max(self, inputRaster, outputRaster):
		# register drivers
		gdal.AllRegister()
		rD = gdal.Open(inputRaster, GA_ReadOnly)
		# band list
		bL = cfg.utls.readAllBandsFromRaster(rD)
		# output rasters
		oM = []
		oM.append(outputRaster)
		oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
		o = cfg.utls.processRaster(rD, bL, None, cfg.utls.reclassifyRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", [["(raster < 0)", 0], ["(raster > 1)", 1]], "raster", "reflectance")
		# close GDAL rasters
		for b in range(0, len(oMR)):
			oMR[b] = None
		for b in range(0, len(bL)):
			bL[b] = None
		rD = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(inputRaster))
						
	# landsat 4, 5, 7 conversion to Reflectance
	def landsat457reflectance(self, satellite, bandNumber, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, inputRaster, outputRaster):
		sat = satellite
		x = bandNumber
		# Esun
		dEsunB = {}
		# landsat 4
		if str(sat).lower() in ['landsat_4', 'landsat4']:
			# Esun from Chander, G. & Markham, B. Revised landsat-5 TM radiometric calibration procedures and postcalibration dynamic ranges Geoscience and Remote Sensing, IEEE Transactions on, 2003, 41, 2674 - 2677
			dEsunB = {"ESUN_BAND1": 1957, "ESUN_BAND2": 1825, "ESUN_BAND3": 1557, "ESUN_BAND4": 1033, "ESUN_BAND5": 214.9, "ESUN_BAND7": 80.72}
		# landsat 5
		elif str(sat).lower() in ['landsat_5', 'landsat5']:
			# Esun from Finn, M.P., Reed, M.D, and Yamamoto, K.H. A Straight Forward Guide for Processing Radiance and Reflectance for EO-1 ALI, landsat 5 TM, landsat 7 ETM+, and ASTER. Unpublished Report from USGS/Center of Excellence for Geospatial Information Science, 8 p. 2012
			dEsunB = {"ESUN_BAND1": 1983, "ESUN_BAND2": 1796, "ESUN_BAND3": 1536, "ESUN_BAND4": 1031, "ESUN_BAND5": 220, "ESUN_BAND7": 83.44}
		# landsat 7
		elif str(sat).lower() in ['landsat_7', 'landsat7']:
			# Esun from Finn, M.P., Reed, M.D, and Yamamoto, K.H. A Straight Forward Guide for Processing Radiance and Reflectance for EO-1 ALI, landsat 5 TM, landsat 7 ETM+, and ASTER. Unpublished Report from USGS/Center of Excellence for Geospatial Information Science, 8 p. 2012
			dEsunB = {"ESUN_BAND1": 1997, "ESUN_BAND2": 1812, "ESUN_BAND3": 1533, "ESUN_BAND4": 1039, "ESUN_BAND5": 230.08, "ESUN_BAND7": 84.9, "ESUN_BAND8": 1369}
		eS = float(dEsunB["ESUN_BAND" + str(x)])
		m = float(RADIANCE_MULT_BAND)
		a = float(RADIANCE_ADD_BAND)
		# temp files
		dT = cfg.utls.getTime()
		tPMN = cfg.reflectanceRasterNm + ".tif"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		tPMN2 = cfg.reflectanceRasterNm + "2.tif"
		tPMD2 = cfg.tmpDir + "/" + dT + tPMN2
		# register drivers
		gdal.AllRegister()
		# TOA reflectance
		if cfg.ui.DOS1_checkBox.isChecked() is False:
			try:
				# TOA Reflectance
				# open input with GDAL
				rD = gdal.Open(inputRaster, GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) * " + str("%.16f" % np.pi) + " * " + str("%.16f" % self.eSD) + " * " + str("%.16f" % self.eSD) + ") / ( " + str("%.16f" % eS)+ " * (" + str(self.sA) + ") )", "raster", "TOA b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				# reclassification <0 and >1
				self.reclassRaster0min1max(tPMD, outputRaster)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(inputRaster))
				return "Yes"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		# DOS atmospheric correction
		elif cfg.ui.DOS1_checkBox.isChecked() is True:
			DNm = self.findDNmin(inputRaster)
			# calculate DOS1 corrected reflectance
			try:
				# radiance calculation
				# open input with GDAL
				rD = gdal.Open(inputRaster, GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "(raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + "))", "raster", "radiance b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				# path radiance Lp = ML* DNm + AL  – 0.01* ESUNλ * cosθs / (π * d^2)	
				Lp = m * DNm + a - 0.01 * eS * self.sA / (np.pi * self.eSD * self.eSD)
				# land surface reflectance ρ = [π * (Lλ - Lp) * d^2]/ (ESUNλ * cosθs)	
				# open input with GDAL
				rD = gdal.Open(tPMD, GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD2)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster - (" + str("%.16f" % Lp) + ") ) * " + str("%.16f" % np.pi) + " * " + str("%.16f" % self.eSD) + " * " + str("%.16f" % self.eSD) + " / ( " + str("%.16f" % eS)+ " * (" + str(self.sA) + ") )", "raster", "DOS1 b" + str(x))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				# reclassification <0 and >1
				self.reclassRaster0min1max(tPMD2, outputRaster)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(inputRaster))
				return "Yes"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			
	# find DNmin in raster
	def findDNmin(self, inputRaster):
		DNm = 0
		# register drivers
		gdal.AllRegister()
		# open input with GDAL
		rD = gdal.Open(inputRaster, GA_ReadOnly)
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
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " DNm " + str(DNm))
		return DNm
			
	# landsat 4,5, or 7 temperature
	def landsat457Temperature(self, satellite, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, inputRaster, outputRaster):
		sat = satellite
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
			# register drivers
			gdal.AllRegister()
			# open input with GDAL
			rD = gdal.Open(inputRaster, GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# output rasters
			oM = []
			oM.append(outputRaster)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
			o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "((" + str("%.16f" % k2) + ") / ( ln( (" + str("%.16f" % k1) + " / ( raster * " + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) ) + 1)) - " + str(cs) + ")", "raster", "temperature")
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(outputRaster))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))		
			
	# landsat 8 temperature
	def landsat8Temperature(self, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, K1_CONSTANT_BAND, K2_CONSTANT_BAND, inputRaster, outputRaster):
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
			gdal.AllRegister()
			rD = gdal.Open(inputRaster, GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# output rasters
			oM = []
			oM.append(outputRaster)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64)
			o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No",  "((" + str("%.16f" % k2) + ") / ( ln( (" + str("%.16f" % k1) + " / ( raster *" + str("%.16f" % m) + "+ (" + str("%.16f" % a) + ")) ) + 1)) - " + str(cs) + ")", "raster", "temperature")
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(outputRaster))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
	# landsat output
	def outputLandsat(self):
		o = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		cfg.ui.label_27.setText(unicode(o))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), unicode(o))
		
	# landsat correction button
	def performLandsatCorrection(self):
		if len(cfg.ui.label_26.text()) == 0:
			cfg.mx.msg14()
		else:
			o = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.landsat(cfg.ui.label_26.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Perform landsat correction: " + str(cfg.ui.label_26.text()))
		
	def populateTable(self, input):
		check = "Yes"
		sat = ""
		dt = ""
		sE = ""
		esd = ""
		cfg.ui.satellite_lineEdit.setText(sat)
		cfg.ui.date_lineEdit.setText(dt)
		cfg.ui.sun_elev_lineEdit.setText(sE)
		cfg.ui.earth_sun_dist_lineEdit.setText(esd)
		l = cfg.ui.landsat_tableWidget
		l.setColumnWidth(0, 250)
		cfg.utls.clearTable(l)
		inp = input
		if len(inp) == 0:
			cfg.mx.msg14()
		else:
			cfg.uiUtls.addProgressBar()
			if len(cfg.ui.label_27.text()) == 0:
				for f in os.listdir(inp):
					if f.lower().endswith(".txt") and "mtl" in f.lower():
							MTLFile = inp + "/" + str(f)
					# for compatibility with glcf images
					if f.lower().endswith(".met"):
							MTLFile = inp + "/" + str(f)
			else:
				MTLFile = cfg.ui.label_27.text()
		#### open MTL file
			try:
				# get information from MTL
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
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr8()
				check = "No"						
			if esd == "":
				# date format
				dFmt = "%Y-%m-%d"
				try:
					esd = str(cfg.utls.calculateEarthSunDistance(dt, dFmt))
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.ui.satellite_lineEdit.setText(sat)
			cfg.ui.date_lineEdit.setText(dt)
			cfg.ui.sun_elev_lineEdit.setText(sE)
			cfg.ui.earth_sun_dist_lineEdit.setText(esd)
		#### list bands
			# bands
			dBs = {}
			bandNames = []
			# input dictionaries
			for f in os.listdir(inp):
				if f.lower().endswith(".tif") or f.lower().endswith(".TIF") or f.lower().endswith(".Tif"):
					# name
					nm = os.path.splitext(f)[0]
					if str(sat).lower() in ['landsat_4', 'landsat4', 'landsat_5', 'landsat5', 'landsat_7', 'landsat7']:
						# landsat bands
						if nm[len(nm) - 2].isdigit() and nm[len(nm) - 1].isdigit():
							if str(nm[len(nm) - 1]) == "0" and nm[len(nm) - 2] != "8":
								dBs["BAND_{0}".format(nm[len(nm) - 2])] = str(f)
								bandNames.append(f)
							# landsat 7 thermal bands
							elif str(nm[len(nm) - 2]) == "6":
								dBs["BAND_6_VCID_{0}".format(nm[len(nm) - 1])] = str(f)
								bandNames.append(f)
						elif str(nm[len(nm) - 8: len(nm) - 1]) != "6_VCID_" and nm[len(nm) - 1].isdigit() and nm[len(nm) - 1] != "8":
							dBs["BAND_{0}".format(nm[len(nm) - 1])] = str(f)
							bandNames.append(f)
						# landsat 7 thermal bands
						elif str(nm[len(nm) - 8: len(nm) - 1]) == "6_VCID_" and nm[len(nm) - 1].isdigit():
							dBs["BAND_6_VCID_{0}".format(nm[len(nm) - 1])] = str(f)
							bandNames.append(f)
					elif str(sat).lower() in ['landsat_8', 'landsat8']:
						# for bands < 10
						if str(nm[len(nm) - 8: len(nm) - 1]) != "6_VCID_" and nm[len(nm) - 1].isdigit() and nm[len(nm) - 1] != "8":
							dBs["BAND_{0}".format(nm[len(nm) - 1])] = str(f)
							bandNames.append(f)
						# for bands > 9
						elif nm[len(nm) - 2].isdigit() and nm[len(nm) - 1].isdigit():
							dBs["BAND_{0}".format(nm[len(nm) - 1])] = str(f)
							bandNames.append(f)
					else:
						bandNames.append(f)
			# add band items to table
			b = 0
			for band in sorted(bandNames):				
				l.insertRow(b)
				l.setRowHeight(b, 20)
				itBand = QTableWidgetItem()
				itBand.setData(Qt.DisplayRole, band)
				itBand.setFlags(Qt.ItemIsEnabled)
				l.setItem(b, 0, itBand)
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
				# get information from MTL
				with open(MTLFile, "r") as MTL:
					for r in MTL:
						for key, band in dBs.iteritems():
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
				# add items to table
				b = 0
				for bandName in sorted(bandNames):	
					for key, band in dBs.iteritems():
						if bandName == band:
							if dRadMB:
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRadMB["RADIANCE_MULT_" + str(key)])
								l.setItem(b, 1, itBand)
							if dRadAB:
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRadAB["RADIANCE_ADD_" + str(key)])
								l.setItem(b, 2, itBand)
							if dRefMB:
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRefMB["REFLECTANCE_MULT_" + str(key)])
								l.setItem(b, 3, itBand)
							if dRefAB:
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRefAB["REFLECTANCE_ADD_" + str(key)])
								l.setItem(b, 4, itBand)
							if dRadMxB:
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRadMxB["RADIANCE_MAXIMUM_" + str(key)])
								l.setItem(b, 5, itBand)
							if dRefMxB:
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRefMxB["REFLECTANCE_MAXIMUM_" + str(key)])
								l.setItem(b, 6, itBand)
							if dK1B:
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dK1B["K1_CONSTANT_" + str(key)])
								l.setItem(b, 7, itBand)
							if dK2B:
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dK2B["K2_CONSTANT_" + str(key)])
								l.setItem(b, 8, itBand)
							if dRad:
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRad["LMAX_" + str(key)])
								l.setItem(b, 9, itBand)
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRad["LMIN_" + str(key)])
								l.setItem(b, 10, itBand)
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRad["QCALMAX_" + str(key)])
								l.setItem(b, 11, itBand)
								itBand = QTableWidgetItem()
								itBand.setData(Qt.DisplayRole, dRad["QCALMIN_" + str(key)])
								l.setItem(b, 12, itBand)
					b = b + 1
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
		if str(sat).lower() in ['landsat_4', 'landsat4', 'landsat_5', 'landsat5', 'landsat_7', 'landsat7', 'landsat_8', 'landsat8']:
			cfg.ui.satellite_lineEdit.setStyleSheet("color : black")
		else:
			cfg.ui.satellite_lineEdit.setStyleSheet("color : red")