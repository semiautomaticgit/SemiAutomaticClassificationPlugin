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

class Signature_Importer:
	def __init__(self):
		pass
		
	# import USGS spectral library (http://speclab.cr.usgs.gov/spectral-lib.html)
	def USGSLibrary(self, libraryPath):
		if cfg.osSCP.path.isfile(libraryPath):
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
				wavelength = cfg.np.array(wl)
				a = list(cfg.bandSetsList[cfg.bndSetNumber][4])
				s = sorted(a, key=float)
				b = 0
				cfg.tblOut = {}
				for w in s:
					i = (cfg.np.abs(wavelength - w)).argmin()
					waveL = wl[i]
					reflectance = ref[i]
					standardDeviation = sD[i]
					val = []
					val.append(reflectance-standardDeviation)
					val.append(reflectance+standardDeviation)
					val.append(reflectance)
					val.append(standardDeviation)
					cfg.tblOut["BAND_{0}".format(b+1)] = val
					cfg.tblOut["WAVELENGTH_{0}".format(b + 1)] = w
					b = b + 1
				self.addLibraryToSignatureList()
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library imported" + str(file[0]))
			else:
				cfg.mx.msgErr17()
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library " + str(file[0]))
					
	# import ASTER spectral library (http://speclib.jpl.nasa.gov/search-1)
	def ASTERLibrary(self, libraryPath):
		if cfg.osSCP.path.isfile(libraryPath):
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
				wavelength = cfg.np.array(wl)
				a = list(cfg.bandSetsList[cfg.bndSetNumber][4])
				s = sorted(a, key=float)
				b = 0
				cfg.tblOut = {}
				for w in s:
					i = (cfg.np.abs(wavelength - w)).argmin()
					waveL = wl[i]
					reflectance = ref[i]
					standardDeviation = sD[i]
					val = []
					val.append(reflectance-standardDeviation)
					val.append(reflectance+standardDeviation)
					val.append(reflectance)
					val.append(standardDeviation)
					cfg.tblOut["BAND_{0}".format(b+1)] = val
					cfg.tblOut["WAVELENGTH_{0}".format(b + 1)] = w
					b = b + 1
				self.addLibraryToSignatureList()
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library imported" + str(file[0]))
			else:
				cfg.mx.msgErr17()
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library " + str(file[0]))
		
	# import generic CSV spectral library (first line: wavelength, reflectance, standardDeviation, waveLengthUnit)
	def CSVLibrary(self, libraryPath):
		if cfg.osSCP.path.isfile(libraryPath):
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
				if v[3] != cfg.noUnit:
					if vL > 30 and str(cfg.bandSetsList[cfg.bndSetNumber][5]) == cfg.unitMicro:
						vL = vL / 1000
					elif vL < 30 and str(cfg.bandSetsList[cfg.bndSetNumber][5]) == cfg.wlNano:
						vL = vL * 1000
				wl.append(vL)
				ref.append(float(v[1]))
				try:
					sD.append(float(v[2]))
				except:
					sD.append(float(0))
			wavelength = cfg.np.array(wl)
			a = list(cfg.bandSetsList[cfg.bndSetNumber][4])
			s = sorted(a, key=float)
			b = 0
			cfg.tblOut = {}
			for w in s:
				i = (cfg.np.abs(wavelength - w)).argmin()
				waveL = wl[i]
				reflectance = ref[i]
				standardDeviation = sD[i]
				val = []
				val.append(reflectance-standardDeviation)
				val.append(reflectance+standardDeviation)
				val.append(reflectance)
				val.append(standardDeviation)
				cfg.tblOut["BAND_{0}".format(b+1)] = val
				cfg.tblOut["WAVELENGTH_{0}".format(b + 1)] = w
				b = b + 1
			unit = v[3].strip()
			if str(unit) == cfg.noUnit or str(unit) == cfg.unitMicro or str(unit) == cfg.wlNano:
				self.addLibraryToSignatureList(unit)
			else:
				self.addLibraryToSignatureList()
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library imported " + str(libraryPath))

	# add library values to signature list
	def addLibraryToSignatureList(self, unit = None):
		macroclassID = cfg.ROIMacroID
		macroclassInfo = cfg.ROIMacroClassInfo
		classID = cfg.ROIID
		classInfo = cfg.ROIInfo
		cfg.tblOut["ROI_SIZE"] = 0
		cfg.utls.ROIStatisticsToSignature("No", macroclassID, macroclassInfo, classID, classInfo, cfg.bndSetNumber, unit)
		cfg.SCPD.ROIListTable(cfg.shpLay, cfg.uidc.signature_list_tableWidget)
		
	# open a shapefile
	def openShapefileI(self):
		shpFile = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a shapefile"), "", "Shapefile (*.shp)")
		if len(shpFile) > 0:
			fields = cfg.utls.fieldsShapefile(shpFile)
			cfg.ui.MC_ID_combo.clear()
			cfg.ui.MC_ID_combo.addItems(fields)
			cfg.ui.MC_Info_combo.clear()
			cfg.ui.MC_Info_combo.addItems(fields)
			cfg.ui.C_ID_combo.clear()
			cfg.ui.C_ID_combo.addItems(fields)
			cfg.ui.C_Info_combo.clear()
			cfg.ui.C_Info_combo.addItems(fields)
			cfg.ui.select_shapefile_label.setText(shpFile)
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " open Shapefile")
			