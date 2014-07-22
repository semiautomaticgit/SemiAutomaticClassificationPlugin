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
import sys
import inspect
import numpy as np
import SemiAutomaticClassificationPlugin.core.config as cfg

class Signature_Importer:
	def __init__(self):
		pass
		
	# import USGS spectral library (http://speclab.cr.usgs.gov/spectral-lib.html)
	def USGSLibrary(self, libraryPath):
			if os.path.isfile(libraryPath):
				f = open(libraryPath)
				file = f.readlines()
				if "USGS" in file[0]:
					wl = []
					ref = []
					sD = []
					for b in range(16, len(file)):
						r = " ".join(file[b].split())
						v = r.split()
						wl.append(float(v[0]))
						ref.append(float(v[1]))
						sD.append(float(v[2]))
					wavelength = np.array(wl)
					a = cfg.bndSetWvLn.values()
					s = sorted(a, key=float)
					b = 0
					cfg.tblOut = {}
					for w in s:
						i = (np.abs(wavelength - w)).argmin()
						waveL = wl[i]
						# empty value for obtaining the same structure as the ROI stats
						zero = 0
						reflectance = ref[i]
						standardDeviation = sD[i]
						val = []
						val.append(waveL)
						val.append(zero)
						val.append(reflectance)
						val.append(standardDeviation)
						cfg.tblOut["BAND_{0}".format(b+1)] = val
						cfg.tblOut["WAVELENGTH_{0}".format(b + 1)] = w
						b = b + 1
					self.addLibraryToSignatureList()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library imported" + str(file[0]))
				else:
					cfg.mx.msgErr17()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library " + str(file[0]))
					
	# import ASTER spectral library (http://speclib.jpl.nasa.gov/search-1)
	def ASTERLibrary(self, libraryPath):
			if os.path.isfile(libraryPath):
				f = open(libraryPath)
				file = f.readlines()
				if "Name" in file[0]:
					wl = []
					ref = []
					sD = []
					for b in range(26, len(file)):
						v = file[b].split()
						wl.append(float(v[0]))
						ref.append(float(v[1]) / 100)
						sD.append(float(0))
					wavelength = np.array(wl)
					a = cfg.bndSetWvLn.values()
					s = sorted(a, key=float)
					b = 0
					cfg.tblOut = {}
					for w in s:
						i = (np.abs(wavelength - w)).argmin()
						waveL = wl[i]
						# empty value for obtaining the same structure as the ROI stats
						zero = 0
						reflectance = ref[i]
						standardDeviation = sD[i]
						val = []
						val.append(waveL)
						val.append(zero)
						val.append(reflectance)
						val.append(standardDeviation)
						cfg.tblOut["BAND_{0}".format(b+1)] = val
						cfg.tblOut["WAVELENGTH_{0}".format(b + 1)] = w
						b = b + 1
					self.addLibraryToSignatureList()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library imported" + str(file[0]))
				else:
					cfg.mx.msgErr17()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library " + str(file[0]))
		
	# import generic CSV spectral library (first line: wavelength, reflectance, standardDeviation, waveLengthUnit)
	def CSVLibrary(self, libraryPath):
		if os.path.isfile(libraryPath):
			f = open(libraryPath)
			file = f.readlines()
			wl = []
			ref = []
			sD = []
			for b in range(1, len(file)):
				v = file[b].split(";")
				if len(v) == 1:
					v = file[b].split(",")
				# check if wavelength is not in micrometers
				vL = float(v[0])
				if vL > 30 and str(cfg.bndSetUnit["UNIT"]) == cfg.unitMicro:
					vL = vL / 1000
				elif vL < 30 and str(cfg.bndSetUnit["UNIT"]) == cfg.wlNano:
					vL = vL * 1000
				wl.append(vL)
				ref.append(float(v[1]))
				try:
					sD.append(float(v[2]))
				except:
					sD.append(float(0))
			wavelength = np.array(wl)
			a = cfg.bndSetWvLn.values()
			s = sorted(a, key=float)
			b = 0
			cfg.tblOut = {}
			for w in s:
				i = (np.abs(wavelength - w)).argmin()
				waveL = wl[i]
				# empty value for obtaining the same structure as the ROI stats
				zero = 0
				reflectance = ref[i]
				standardDeviation = sD[i]
				val = []
				val.append(waveL)
				val.append(zero)
				val.append(reflectance)
				val.append(standardDeviation)
				cfg.tblOut["BAND_{0}".format(b+1)] = val
				cfg.tblOut["WAVELENGTH_{0}".format(b + 1)] = w
				b = b + 1
			try:
				self.addLibraryToSignatureList(v[3])
			except:
				self.addLibraryToSignatureList()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library imported" + str(file[0]))

	# add library values to signature list
	def addLibraryToSignatureList(self, unit = None):
		macroclassID = cfg.ROIMacroID
		macroclassInfo = cfg.ROIMacroClassInfo
		classID = 	cfg.ROIID
		classInfo = cfg.ROIInfo
		if unit is None:
			unit = cfg.unitMicro
		cfg.ROId.ROIStatisticsToSignature("No", macroclassID, macroclassInfo, classID, classInfo, unit)
		cfg.classD.signatureListTable(cfg.uidc.signature_list_tableWidget)