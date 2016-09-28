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

class BandsetTab:

	def __init__(self):
		pass
		
	# add satellite list to combo
	def addSatelliteToCombo(self, satelliteList):
		for i in satelliteList:
			cfg.ui.wavelength_sat_combo.addItem(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " satellites added")
			
	# add unit list to combo
	def addUnitToCombo(self, unitList):
		for i in unitList:
			cfg.ui.unit_combo.addItem(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " units added")
			
	def setBandUnit(self):
		self.readBandSet(cfg.bndSetPresent)
			
	def satelliteWavelength(self):
		self.setSatelliteWavelength()
			
	# set satellite wavelengths
	def setSatelliteWavelength(self, satelliteName = None, bandList = None):
		if satelliteName is None:
			satelliteName = cfg.ui.wavelength_sat_combo.currentText()
		tW = cfg.ui.tableWidget
		c = tW.rowCount()
		wl = []
		tW.blockSignals(True)
		id = cfg.ui.unit_combo.findText(cfg.noUnit)
		if satelliteName == cfg.NoSatellite:
			for x in range(0, c):
				wl.append(x + 1)
			id = cfg.ui.unit_combo.findText(cfg.noUnit)
		# ASTER center wavelength calculated from USGS, 2015. Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) Level 1 Precision Terrain Corrected Registered At-Sensor Radiance Product (AST_L1T)
		elif satelliteName == cfg.satASTER:
			wl = [0.560, 0.660, 0.810, 1.650, 2.165, 2.205, 2.260, 2.330, 2.395, 8.300, 8.650, 9.100, 10.600, 11.300]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		# Landsat center wavelength calculated from http://landsat.usgs.gov/band_designations_landsat_satellites.php
		elif satelliteName == cfg.satLandsat8:
			wl = [0.48, 0.56, 0.655, 0.865, 1.61, 2.2]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		elif satelliteName == cfg.satLandsat7:
			wl = [0.485, 0.56, 0.66, 0.835, 1.65, 2.22]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		elif satelliteName == cfg.satLandsat45:
			wl = [0.485, 0.56, 0.66, 0.83, 1.65, 2.215]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)	
		elif satelliteName == cfg.satLandsat13:
			wl = [0.55, 0.65, 0.75, 0.95]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		# RapidEye center wavelength calculated from http://www.blackbridge.com/rapideye/products/ortho.htm
		elif satelliteName == cfg.satRapidEye:
			wl = [0.475, 0.555, 0.6575, 0.71, 0.805]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		# SPOT center wavelength calculated from http://www.astrium-geo.com/en/194-resolution-and-spectral-bands
		elif satelliteName == cfg.satSPOT4 or satelliteName == cfg.satSPOT5:
			wl = [0.545, 0.645, 0.835, 1.665]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		elif satelliteName == cfg.satSPOT6:
			wl = [0.485, 0.56, 0.66, 0.825]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		# Pléiades center wavelength calculated from http://www.astrium-geo.com/en/3027-pleiades-50-cm-resolution-products
		elif satelliteName == cfg.satPleiades:
			wl = [0.49, 0.56, 0.65, 0.84]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		# QuickBird center wavelength calculated from http://www.digitalglobe.com/resources/satellite-information
		elif satelliteName == cfg.satQuickBird:
			wl = [0.4875, 0.543, 0.65, 0.8165]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		# WorldView-2 center wavelength calculated from http://www.digitalglobe.com/resources/satellite-information
		elif satelliteName == cfg.satWorldView23:
			wl = [0.425, 0.48, 0.545, 0.605, 0.66, 0.725, 0.8325, 0.95]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		# GeoEye-1 center wavelength calculated from http://www.digitalglobe.com/resources/satellite-information
		elif satelliteName == cfg.satGeoEye1:
			wl = [0.48, 0.545, 0.6725, 0.85]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		# Sentinel-2 center wavelength from https://sentinel.esa.int/documents/247904/685211/Sentinel-2A+MSI+Spectral+Responses
		elif satelliteName == cfg.satSentinel2:
			wl = [0.490, 0.560, 0.665, 0.705, 0.740, 0.783, 0.842, 0.865, 1.610, 2.190]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		cfg.BandTabEdited = "No"
		b = 0
		if bandList is None:
			for i in wl:
				if b < c:
					tW.item(b, 1).setText(str(float(i)))
					b = b + 1
		else:
			for n in bandList:
				i = wl[n - 1]
				tW.item(b, 1).setText(str(float(i)))
				b = b + 1
		tW.blockSignals(False)
		cfg.BandTabEdited = "Yes"
		cfg.ui.unit_combo.setCurrentIndex(id)
		self.readBandSet(cfg.bndSetPresent)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " satellite" + str(satelliteName))
			
	# add file to band set action
	def addFileToBandSetAction(self):
		self.addFileToBandSet()
		
	# add file to band set
	def addFileToBandSet(self, batch = "No", fileListString = None, wavelengthString = None, multiplicativeFactorString = None, additiveFactorString = None):
		tW = cfg.ui.tableWidget
		if batch == "No":
			files = cfg.utls.getOpenFileNames(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a raster"), "", "Raster (*.*)")
		else:
			cfg.utls.clearTable(tW)
			fileList = fileListString.split(",")
			files = []
			for f in fileList:
				files.append(f.strip())
			try:
				wavelength = wavelengthString.split(",")
			except:
				wavelength = None
			try:
				multiplicativeFactor = multiplicativeFactorString.split(",")
			except:
				multiplicativeFactor = None
			try:
				additiveFactor = additiveFactorString.split(",")
			except:
				additiveFactor = None
		cfg.BandTabEdited = "No"
		tW.blockSignals(True)
		# count table rows
		c = tW.rowCount()
		if len(files) == 1:
			try:
				iBC = cfg.utls.getNumberBandRaster(files[0])
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msgErr25()
				return "No"
			if iBC > 1:
				r = cfg.utls.addRasterLayer(files[0], cfg.osSCP.path.basename(files[0]))
				cfg.utls.clearTable(tW)
				cfg.ipt.checkRefreshRasterLayer()
				# load project image name in combo
				id = cfg.uidc.raster_name_combo.findText(cfg.osSCP.path.basename(files[0]))
				cfg.uidc.raster_name_combo.setCurrentIndex(id)
				return "Yes"
		# check if single raster
		if c > 0 and cfg.bndSetPresent == "No":
			cfg.utls.clearTable(tW)
		for i in files:
			check = "Yes"
			try:
				iBC = cfg.utls.getNumberBandRaster(i)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msgErr25()
				iBC = None
				check = "No"
			if iBC == 1 and check == "Yes":
				r = cfg.utls.addRasterLayer(i, cfg.osSCP.path.basename(i))
				itN = cfg.osSCP.path.basename(i)
				# count table rows
				c = tW.rowCount()
				# add list items to table
				tW.setRowCount(c + 1)
				cfg.utls.addTableItem(tW, itN, c, 0)
				if wavelengthString is not None:
					try:
						v = float(wavelength[c])
					except:
						v = c + 1
				else:
					v = c + 1
				cfg.utls.addTableItem(tW, str(float(v)), c, 1)
				if multiplicativeFactorString is not None:
					try:
						v = float(multiplicativeFactor[c])
					except:
						v = "1"
				else:
					v = "1"
				cfg.utls.addTableItem(tW, v, c, 2)
				if additiveFactorString is not None:
					try:
						v = float(additiveFactor[c])
					except:
						v = "0"
				else:
					v = "0"
				cfg.utls.addTableItem(tW, v, c, 3)
		tW.blockSignals(False)
		cfg.bst.rasterBandName()
		self.readBandSet("Yes")
		cfg.rstrNm = cfg.bndSetNm
		cfg.imgNm = cfg.rstrNm
		cfg.BandTabEdited = "Yes"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set changed n. of bands" + str(c))
			
	# add band to band set
	def addBandToSet(self):
		tW = cfg.ui.tableWidget
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bndSetPresent == "No":
			pass
		else:
			# checklist
			l = cfg.ui.raster_listView
			# count rows in checklist
			lc = l.model().rowCount()
			cfg.BandTabEdited = "No"
			tW.blockSignals(True)
			for b in range(0, lc):
				# count table rows
				c = tW.rowCount()
				# If checkbox is activated
				if cfg.bndMdl.item(b).checkState() == 2:
					# name of item of list
					itN = cfg.bndMdl.item(b).text()
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, itN, c, 0)
					if len(cfg.bndSetWvLn.values()) > 0:
						v = max(cfg.bndSetWvLn.values()) + 1
					else:
						v = c + 1
					cfg.utls.addTableItem(tW, str(float(v)), c, 1)
					cfg.utls.addTableItem(tW, "1", c, 2)
					cfg.utls.addTableItem(tW, "0", c, 3)
			tW.blockSignals(False)
			self.readBandSet("Yes")
			cfg.rstrNm = cfg.bndSetNm
			cfg.imgNm = cfg.rstrNm
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set changed n. of bands" + str(lc))
		
	# set all bands to state 0 or 2
	def allBandSetState(self, value):
		# checklist
		l = cfg.ui.raster_listView
		# count rows in checklist
		c = l.model().rowCount()
		for b in range(0, c):
			if cfg.actionCheck == "Yes":
				cfg.bndMdl.item(b).setCheckState(value)
				cfg.uiUtls.updateBar((b+1) * 100 / (c))
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all bands cancelled")
				
	# clear the band set
	def clearBandSetAction(self):
		self.clearBandSet()
		
	# clear the band set
	def clearBandSet(self, question = "Yes", refresh = "Yes"):
		if question == "Yes":
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Clear band set"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the band set?"))
		else:
			a = "Yes"
		if a == "Yes":
			tW = cfg.ui.tableWidget
			cfg.BandTabEdited = "No"
			cfg.utls.clearTable(tW)
			cfg.BandTabEdited = "Yes"
			# band set unit
			cfg.bndSetUnit = {}
			# band set name list
			cfg.bndSet = []
			# band set wavelength
			cfg.bndSetWvLn = {}
			cfg.bndSetMultiFactors = {}
			cfg.bndSetAddFactors = {}
			if refresh == "Yes":
				# read band set
				self.readBandSet("No", refresh)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set cleared")
		
	# band set edited
	def editedBandSet(self, row, column):
		tW = cfg.ui.tableWidget
		if cfg.BandTabEdited == "Yes" and column == 1:
			# check if bandset is empty
			c = tW.rowCount()
			cfg.BandTabEdited = "No"
			try:
				w = str(float(tW.item(row, column).text()))
			except:
				w = str(float(cfg.bndSetWvLn["WAVELENGTH_" + str(row + 1)]))
			cfg.utls.setTableItem(tW, row, column, w)
			tW.show()
			if c == 0:
				self.readBandSet()
			elif float(tW.item(row, column).text()) in cfg.bndSetWvLn.values():
				cfg.mx.msgWar7()
				w = str(float(cfg.bndSetWvLn["WAVELENGTH_" + str(row + 1)]))
				cfg.utls.setTableItem(tW, row, column, w)
				tW.show()
			else:
				# order by wavelength
				nm = []
				wvl = []
				id = []
				for b in range(0, c):
					nm.append(tW.item(b, 0).text())
					wvl.append(float(tW.item(b, 1).text()))
				if wvl is not None:
					tW.clearContents()
					# sort items
					b = 0
					for i in sorted(wvl):
						x = wvl.index(i)
						cfg.utls.addTableItem(tW, nm[x], b, 0, "No")
						cfg.utls.addTableItem(tW, str(float(i)), b, 1)
						b = b + 1
					tW.show()
					self.readBandSet(cfg.bndSetPresent)
					cfg.BandTabEdited = "Yes"
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band edited; bands n. " + str(c))
			cfg.BandTabEdited = "Yes"
		elif cfg.BandTabEdited == "Yes" and column == 2:
			# check if bandset is empty
			c = tW.rowCount()
			if c == 0:
				self.readBandSet()
			else:
				cfg.BandTabEdited = "No"
				try:
					test = float(tW.item(row, column).text())
					cfg.utls.addTableItem(tW, str(tW.item(row, column).text()), row, column)
				except:
					cfg.utls.addTableItem(tW, str(cfg.bndSetMultiFactors["MULTIPLICATIVE_FACTOR_" + str(row + 1)]), row, column)
				tW.show()
				self.readBandSet(cfg.bndSetPresent)
				cfg.BandTabEdited = "Yes"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band edited; bands n. " + str(c))
		elif cfg.BandTabEdited == "Yes" and column == 3:
			# check if bandset is empty
			c = tW.rowCount()
			if c == 0:
				self.readBandSet()
			else:
				cfg.BandTabEdited = "No"
				try:
					test = float(tW.item(row, column).text())
					cfg.utls.addTableItem(tW, str(tW.item(row, column).text()), row, column)
				except:
					cfg.utls.addTableItem(tW, str(cfg.bndSetAddFactors["ADDITIVE_FACTOR_" + str(row + 1)]), row, column)
				tW.show()
				self.readBandSet(cfg.bndSetPresent)
				cfg.BandTabEdited = "Yes"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band edited; bands n. " + str(c))
		
	def readBandSet(self, bandset = "Yes", refresh = "Yes"):
		tW = cfg.ui.tableWidget
		# check if bandset is empty
		c = tW.rowCount()
		cfg.bandsetCount = c
		cfg.bndSetPresent = bandset
		# band set name list
		cfg.bndSet = []
		# band set wavelength
		cfg.bndSetWvLn = {}
		# band set multiplicative and additive factors
		cfg.bndSetMultiFactors = {}
		cfg.bndSetAddFactors = {}
		cfg.bndSetMultiFactorsList = []
		cfg.bndSetAddFactorsList = []
		cfg.bndSetMultAddFactorsList = []
		if c == 0:
			cfg.bndSetPresent = "No"
			if refresh == "Yes":
				cfg.ipt.refreshRasterLayer()
		else:
			for b in range(0, c):
				cfg.bndSet.append(tW.item(b, 0).text())
				cfg.bndSetWvLn["WAVELENGTH_{0}".format(b + 1)] = float(tW.item(b, 1).text())
				try:
					cfg.bndSetMultiFactors["MULTIPLICATIVE_FACTOR_{0}".format(b + 1)] = float(tW.item(b, 2).text())
				except:
					cfg.bndSetMultiFactors["MULTIPLICATIVE_FACTOR_{0}".format(b + 1)] = 1
				try:
					cfg.bndSetAddFactors["ADDITIVE_FACTOR_{0}".format(b + 1)] = float(tW.item(b, 3).text())
				except:
					cfg.bndSetAddFactors["ADDITIVE_FACTOR_{0}".format(b + 1)] = 0
				cfg.bndSetMultiFactorsList.append(cfg.bndSetMultiFactors["MULTIPLICATIVE_FACTOR_{0}".format(b + 1)])
				cfg.bndSetAddFactorsList.append(cfg.bndSetAddFactors["ADDITIVE_FACTOR_{0}".format(b + 1)])
				cfg.bndSetMultAddFactorsList.append([cfg.bndSetMultiFactors["MULTIPLICATIVE_FACTOR_{0}".format(b + 1)], cfg.bndSetAddFactors["ADDITIVE_FACTOR_{0}".format(b + 1)]])
			if bandset == "Yes":
				cfg.ipt.refreshRasterLayer()
		# read unit
		cfg.bndSetUnit["UNIT"] = self.unitNameConversion(cfg.ui.unit_combo.currentText())
		# find band number
		cfg.utls.findBandNumber()
		cfg.utls.checkBandSet()
		cfg.tmpVrt = None
		tPMN = cfg.tmpVrtNm + ".vrt"
		try:
			cfg.utls.removeLayer(tPMN)
		except:
			pass
		# write project variables
		cfg.utls.writeProjectVariable("bandSetPresent", str(cfg.bndSetPresent))
		cfg.utls.writeProjectVariable("bandSet", str(cfg.bndSet))
		cfg.utls.writeProjectVariable("bndSetWvLn", str(cfg.bndSetWvLn.values()))
		cfg.utls.writeProjectVariable("bndSetMultF", str(cfg.bndSetMultiFactorsList))
		cfg.utls.writeProjectVariable("bndSetAddF", str(cfg.bndSetAddFactorsList))
		cfg.utls.writeProjectVariable("bndSetUnit", str(cfg.bndSetUnit["UNIT"]))
		# load algorithm weight table
		cfg.algWT.loadAlgorithmTable(cfg.bndSet)
		
	# 	convert unit name string in combo
	def unitNameConversion(self, unitName, reverse = "No"):
		if reverse == "No":
			if unitName == cfg.wlNano:
				u = cfg.unitNano
			elif unitName == cfg.wlMicro:
				u = cfg.unitMicro
			elif unitName == cfg.noUnit:
				u= cfg.noUnit
		elif reverse == "Yes":
			if unitName == cfg.unitNano:
				u = cfg.wlNano
			elif unitName == cfg.unitMicro:
				u = cfg.wlMicro
			elif unitName == cfg.noUnit:
				u= cfg.noUnit
		return u

	# export band set to file
	def exportBandSet(self):
		bndSetFile = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save the band set to file"), "", "XML (*.xml)")
		if len(bndSetFile) > 0:
			try:
				tW = cfg.ui.tableWidget
				# check if bandset is empty
				c = tW.rowCount()
				if c != 0:
					root = cfg.ETSCP.Element("bandset")
					root.set("unit",str(cfg.bndSetUnit["UNIT"]))
					root.set("bandsetpresent",str(cfg.bndSetPresent))
					for b in range(0, c):
						bandItem = cfg.ETSCP.SubElement(root, "band")
						bandItem.set("number", str(b + 1))
						nameField = cfg.ETSCP.SubElement(bandItem, "name")
						nameField.text = tW.item(b, 0).text()
						rangeField = cfg.ETSCP.SubElement(bandItem, "wavelength")
						rangeField.text = tW.item(b, 1).text()
						mutliplicativeField = cfg.ETSCP.SubElement(bandItem, "multiplicative_factor")
						mutliplicativeField.text = tW.item(b, 2).text()	
						additiveField = cfg.ETSCP.SubElement(bandItem, "additive_factor")
						additiveField.text = tW.item(b, 3).text()
					o = open(bndSetFile, 'w')
					f = cfg.minidomSCP.parseString(cfg.ETSCP.tostring(root)).toprettyxml()
					o.write(f)
					o.close()
					# logger
					cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set exported")
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# import band set from file
	def importBandSet(self):
		bndSetFile = cfg.utls.getOpenFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a band set file"), "", "XML (*.xml)")
		if len(bndSetFile) > 0:
			try:
				tree = cfg.ETSCP.parse(bndSetFile)
				root = tree.getroot()
				# band set
				bs = {}
				# wavelength
				wl = {}
				# multiplicative and additive factors
				multF = {}
				addF = {}
				# band number
				bN = []
				unit = root.get("unit")
				bandset = root.get("bandsetpresent")
				if unit == cfg.unitMicro:
					id = cfg.ui.unit_combo.findText(cfg.wlMicro)
					cfg.ui.unit_combo.setCurrentIndex(id)
				elif unit == cfg.unitNano:
					id = cfg.ui.unit_combo.findText(cfg.wlNano)
					cfg.ui.unit_combo.setCurrentIndex(id)
				for child in root:
					n = int(child.get("number"))
					bN.append(n)
					bs[n] = str(child.find("name").text).strip()
					wl[n] = float(child.find("wavelength").text.strip())
					multF[n] = float(child.find("multiplicative_factor").text.strip())
					addF[n] = float(child.find("additive_factor").text.strip())					
				tW = cfg.ui.tableWidget
				cfg.BandTabEdited = "No"
				while tW.rowCount() > 0:
					tW.removeRow(0)
				for x in sorted(bN):
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, bs[x], c, 0, "No")
					cfg.utls.addTableItem(tW, str(wl[x]), c, 1)
					cfg.utls.addTableItem(tW, str(multF[x]), c, 2)
					cfg.utls.addTableItem(tW, str(addF[x]), c, 3)
				self.readBandSet(bandset)
				cfg.BandTabEdited = "Yes"
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set imported")		
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msgErr5()
				
	# set band set
	def setBandSet(self, bandNameList):
		tW = cfg.ui.tableWidget
		cfg.BandTabEdited = "No"
		try:
			while tW.rowCount() > 0:
				tW.removeRow(0)
			for x in bandNameList:
				c = tW.rowCount()
				# add list items to table
				tW.setRowCount(c + 1)
				cfg.utls.addTableItem(tW, x, c, 0, "No")
				cfg.utls.addTableItem(tW, "", c, 1)
				cfg.utls.addTableItem(tW, "1", c, 2)
				cfg.utls.addTableItem(tW, "0", c, 3)
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set set")
		except Exception, err:
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr5()
			
	# move down selected band
	def moveDownBand(self):
		tW = cfg.ui.tableWidget
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bndSetPresent == "No":
			pass
		else:
			s = tW.selectedItems()
			cfg.BandTabEdited = "No"
			# create list for new selection after move
			ns  = []
			for i in range (0, len(s)):
				ns.append(s[i].row() + 1)
			try:
				for b in reversed(range(0, c)):
					if tW.item(b, 0).isSelected() or tW.item(b, 1).isSelected():
						bNU = tW.item(b, 0).text()
						bND = tW.item(b + 1, 0).text()
						tW.item(b, 0).setText(str(bND))
						tW.item(b + 1, 0).setText(str(bNU))
				tW.clearSelection()
				v = list(set(ns))
				for i in range (0, len(v)):
					tW.selectRow(v[i])
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
			# update band set
			self.readBandSet()
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band moved")

	# sort band name
	def sortBandName(self):
		tW = cfg.ui.tableWidget
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bndSetPresent == "No":
			pass
		else:
			cfg.BandTabEdited = "No"
			try:
				bN = []
				bNL = []
				for b in range(0, c):
					bN.append(tW.item(b, 0).text())
					split = cfg.reSCP.split('([0-9]+)', tW.item(b, 0).text())
					try:
						bNL.append(int(split[-1]))
					except:
						try:
							bNL.append(int(split[-2]))
						except:
							try:
								bNL.append(int(split[-3]))
							except:
								bNL.append(tW.item(b, 0).text())
				if len(list(set(bNL))) == len(bN):
					sortBands = sorted(bNL)
					bNsort = []
					for k in sortBands:
						q = bNL.index(k)
						bNsort.append(bN[q])
				else:
					bNsort = sorted(bN)
				for b in range(0, c):
					tW.item(b, 0).setText(str(bNsort[b]))
				tW.clearSelection()
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
			# update band set
			self.readBandSet()
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band moved")
	
	# move up selected band
	def moveUpBand(self):
		tW = cfg.ui.tableWidget
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bndSetPresent == "No":
			pass
		else:
			s = tW.selectedItems()
			cfg.BandTabEdited = "No"
			# create list for new selection after move
			ns  = []
			for i in range (0, len(s)):
				ns.append(s[i].row() - 1)
			try:
				for b in range(0, c):
					if tW.item(b, 0).isSelected() or tW.item(b, 1).isSelected():
						bNU = tW.item(b, 0).text()
						bND = tW.item(b - 1, 0).text()
						tW.item(b, 0).setText(str(bND))
						tW.item(b - 1, 0).setText(str(bNU))					
				tW.clearSelection()
				v = list(set(ns))
				for i in range (0, len(v)):
					tW.selectRow(v[i])
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
			# update band set
			self.readBandSet()
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band moved")
				
	# Set raster band checklist
	def rasterBandName(self):
		ls = cfg.lgnd.layers()
		# checklist
		l = cfg.ui.raster_listView
		# create band item model
		cfg.bndMdl = cfg.QtGuiSCP.QStandardItemModel(l)
		cfg.bndMdl.clear()
		l.setModel(cfg.bndMdl)
		l.show()
		for x in ls:
			if x.type() == QgsMapLayer.RasterLayer and x.bandCount() == 1:
				# band name
				it = cfg.QtGuiSCP.QStandardItem(x.name())
				# Create checkbox
				it.setCheckable(True)
				# Add band to model
				cfg.bndMdl.appendRow(it)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster band name checklist created")
		
	# Set raster to single band names for wavelength definition
	def rasterToBandName(self, rasterName, bandset = "No"):
		tW = cfg.ui.tableWidget
		r = cfg.utls.selectLayerbyName(rasterName, "Yes")
		b = r.bandCount()
		cfg.BandTabEdited = "No"
		tW.blockSignals(True)
		for i in range(0, b):
			# count table rows
			c = tW.rowCount()
			# name of item of list
			itN = rasterName + "#b" + str(i)
			# add list items to table
			tW.setRowCount(c + 1)
			cfg.utls.addTableItem(tW, itN, c, 0, "No")
			if len(cfg.bndSetWvLn.values()) > 0:
				v = max(cfg.bndSetWvLn.values()) + 1
			else:
				v = i + 1
			wl = str(float(v))
			cfg.utls.addTableItem(tW, wl, c, 1)
			cfg.utls.addTableItem(tW, "1", c, 2)
			cfg.utls.addTableItem(tW, "0", c, 3)
		self.readBandSet(bandset)
		tW.blockSignals(False)
		cfg.BandTabEdited = "Yes"
	
	# remove selected band
	def removeBand(self):
		tW = cfg.ui.tableWidget
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bndSetPresent == "No":
			pass
		else:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Remove band"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to remove the selected bands from band set?"))
			if a == "Yes":
				r = []
				for i in tW.selectedItems():
					r.append(i.row())
				v = list(set(r))
				cfg.BandTabEdited = "No"
				for x in reversed(v):
				# remove items
					tW.removeRow(x)
				self.readBandSet()
				cfg.BandTabEdited = "Yes"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band removed; bands n. " + str(c))
		
	# select all bands for set
	def selectAllBands(self):
		cfg.uiUtls.addProgressBar()
		try:
			# select all
			if self.allBandsCheck == "Yes":
				self.allBandSetState(2)
				# set check all bands
				self.allBandsCheck = "No"
			# unselect all if previously selected all
			elif self.allBandsCheck == "No":
				self.allBandSetState(0)
				# set check all bands
				self.allBandsCheck = "Yes"
		except:
			# first time except
			try:
				self.allBandSetState(2)
				# set check all bands
				self.allBandsCheck = "No"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				pass
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all bands clicked")
		
	# create virtual raster
	def virtualRasterBandSet(self, outFile = None):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			ck = cfg.utls.checkBandSet()
			if outFile is None:
				rstrOut = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save virtual raster"), "", "*.vrt")
			else:
				rstrOut = outFile
			if len(rstrOut) > 0 and ck == "Yes":
				if unicode(rstrOut).endswith(".vrt"):
					rstrOut = rstrOut
				else:
					rstrOut = rstrOut + ".vrt"
				st = cfg.utls.createVirtualRaster(cfg.bndSetLst, rstrOut)
				# add virtual raster to layers
				cfg.iface.addRasterLayer(unicode(rstrOut), unicode(cfg.osSCP.path.basename(rstrOut)))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " virtual raster: " + str(st))
			elif ck == "No":
				cfg.mx.msgErr33()
			
	def stackBandSet(self, outFile = None):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			ck = cfg.utls.checkBandSet()
			if outFile is None:
				rstrOut = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster"), "", "*.tif")
			else:
				rstrOut = outFile
			if len(rstrOut) > 0 and ck == "Yes":
				if outFile is None:
					cfg.uiUtls.addProgressBar()
				cfg.cnvs.setRenderFlag(False)
				if unicode(rstrOut).endswith(".tif"):
					rstrOut = rstrOut
				else:
					rstrOut = rstrOut + ".tif"
				cfg.uiUtls.updateBar(10)
				# date time for temp name
				dT = cfg.utls.getTime()
				tPMN2 = dT + cfg.calcRasterNm + ".tif"
				tPMD2 = cfg.tmpDir + "/" + tPMN2
				st = cfg.utls.mergeRasterBands(cfg.bndSetLst, tPMD2)
				if cfg.rasterCompression != "No":
					try:
						cfg.utls.GDALCopyRaster(tPMD2, rstrOut, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						cfg.osSCP.remove(tPMD2)
					except Exception, err:
						cfg.shutilSCP.copy(tPMD2, rstrOut)
						cfg.osSCP.remove(tPMD2)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					cfg.shutilSCP.copy(tPMD2, rstrOut)
					cfg.osSCP.remove(tPMD2)
				# add raster to layers
				cfg.iface.addRasterLayer(unicode(rstrOut), unicode(cfg.osSCP.path.basename(rstrOut)))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster: " + str(st))
				cfg.uiUtls.updateBar(100)
				if outFile is None:
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
			elif ck == "No":
				cfg.mx.msgErr33()

	# build band overviews
	def buildOverviewsBandSet(self, quiet = "No"):
		tW = cfg.ui.tableWidget
		c = tW.rowCount()
		# check if single raster
		if c > 0:
			if quiet == "Yes":
				a = "Yes"
			else:
				# ask for confirm
				a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Build overviews"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Do you want to build the external overviews of bands?"))
			if a == "Yes":	
				if quiet == "No":
					cfg.uiUtls.addProgressBar()
				if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
					b = 1
					for i in cfg.bndSetLst:
						cfg.utls.buildOverviewsGDAL(i)
						cfg.uiUtls.updateBar((b) * 100 / (len(cfg.bndSetLst)), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", " building overviews"))
						b = b + 1
				else:
					image = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
					i = image.source()
					cfg.uiUtls.updateBar(50, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", " building overviews"))
					cfg.utls.buildOverviewsGDAL(i)
				cfg.uiUtls.updateBar(100)
				if quiet == "No":
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all bands clicked")
				
	# button perform Band set tools
	def performBandSetTools(self):
		i = cfg.utls.getExistingDirectory(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
		if len(i) > 0:
			cfg.uiUtls.addProgressBar()
			cfg.bst.bandSetTools(i)
			cfg.uiUtls.removeProgressBar()
			cfg.utls.finishSound()
			cfg.cnvs.setRenderFlag(True)
			
	# perform band set tools
	def bandSetTools(self, outputDirectory):
		if cfg.actionCheck == "Yes":
			if cfg.ui.band_calc_checkBox.isChecked() is True:
				cfg.bCalc.rasterBandName()
				cfg.bCalc.calculate(outputDirectory + "/" + cfg.calcRasterNm + ".tif")
		if cfg.actionCheck == "Yes":
			if cfg.ui.virtual_raster_bandset_checkBox.isChecked() is True:
				try:
					cfg.bst.virtualRasterBandSet(outputDirectory + "/" + cfg.osSCP.path.basename(cfg.bndSetLst[0]).split(".")[0][:-1] + cfg.virtualRasterNm + ".vrt")
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		if cfg.actionCheck == "Yes":
			if cfg.ui.stack_raster_bandset_checkBox.isChecked() is True:
				try:
					cfg.bst.stackBandSet(outputDirectory + "/" + cfg.osSCP.path.basename(cfg.bndSetLst[0]).split(".")[0][:-1] + cfg.stackRasterNm + ".tif")
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		if cfg.actionCheck == "Yes":
			if cfg.ui.overview_raster_bandset_checkBox.isChecked() is True:
				cfg.bst.buildOverviewsBandSet("Yes")
				