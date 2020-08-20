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
			
	# set Band unit
	def setBandUnit(self):
		bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		c = tW.rowCount()
		cfg.BandTabEdited = "No"
		tW.blockSignals(True)
		for i in range(0, c):
			cfg.utls.setTableItem(tW, i, 4, cfg.ui.unit_combo.currentText())
		tW.blockSignals(False)
		cfg.BandTabEdited = "Yes"
		self.readBandSet("Yes")
			
	def satelliteWavelength(self):
		self.setSatelliteWavelength()
			
	# set satellite wavelengths
	def setSatelliteWavelength(self, satelliteName = None, bandList = None, bandSetNumber = None):
		if satelliteName is None:
			satelliteName = cfg.ui.wavelength_sat_combo.currentText()
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
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
			bl = ['01', '02', '3N', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14']
		# Landsat center wavelength calculated from http://landsat.usgs.gov/band_designations_landsat_satellites.php
		elif satelliteName == cfg.satLandsat8:
			wl = [0.48, 0.56, 0.655, 0.865, 1.61, 2.2]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['02', '03', '04', '05', '06', '07']
		elif satelliteName == cfg.satLandsat7:
			wl = [0.485, 0.56, 0.66, 0.835, 1.65, 2.22]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['01', '02', '03', '04', '05', '07']
		elif satelliteName == cfg.satLandsat45:
			wl = [0.485, 0.56, 0.66, 0.83, 1.65, 2.215]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)	
			bl = ['01', '02', '03', '04', '05', '07']
		elif satelliteName == cfg.satLandsat13:
			wl = [0.55, 0.65, 0.75, 0.95]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['04', '05', '06', '07']
		# MODIS center wavelength calculated from https://lpdaac.usgs.gov/dataset_discovery/modis
		elif satelliteName == cfg.satMODIS:
			wl = [0.469, 0.555, 0.645, 0.858, 1.24, 1.64, 2.13]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['03', '04', '01', '02', '05', '06', '07']
		elif satelliteName == cfg.satMODIS2:
			wl = [0.645, 0.858]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['01', '02']
		# RapidEye center wavelength calculated from http://www.blackbridge.com/rapideye/products/ortho.htm
		elif satelliteName == cfg.satRapidEye:
			wl = [0.475, 0.555, 0.6575, 0.71, 0.805]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['01', '02', '03', '04', '05']
		# SPOT center wavelength calculated from http://www.astrium-geo.com/en/194-resolution-and-spectral-bands
		elif satelliteName == cfg.satSPOT4 or satelliteName == cfg.satSPOT5:
			wl = [0.545, 0.645, 0.835, 1.665]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['01', '02', '03', '04']
		elif satelliteName == cfg.satSPOT6:
			wl = [0.485, 0.56, 0.66, 0.825]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['01', '02', '03', '04']
		# Pléiades center wavelength calculated from http://www.astrium-geo.com/en/3027-pleiades-50-cm-resolution-products
		elif satelliteName == cfg.satPleiades:
			wl = [0.49, 0.56, 0.65, 0.84]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['01', '02', '03', '04']
		# QuickBird center wavelength calculated from http://www.digitalglobe.com/resources/satellite-information
		elif satelliteName == cfg.satQuickBird:
			wl = [0.4875, 0.543, 0.65, 0.8165]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['01', '02', '03', '04']
		# WorldView-2 center wavelength calculated from http://www.digitalglobe.com/resources/satellite-information
		elif satelliteName == cfg.satWorldView23:
			wl = [0.425, 0.48, 0.545, 0.605, 0.66, 0.725, 0.8325, 0.95]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['01', '02', '03', '04', '05', '06', '07', '08']
		# GeoEye-1 center wavelength calculated from http://www.digitalglobe.com/resources/satellite-information
		elif satelliteName == cfg.satGeoEye1:
			wl = [0.48, 0.545, 0.6725, 0.85]
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
			bl = ['01', '02', '03', '04']
		# Sentinel-2 center wavelength from https://sentinel.esa.int/documents/247904/685211/Sentinel-2A+MSI+Spectral+Responses
		elif satelliteName == cfg.satSentinel2:
			wl = [0.490, 0.560, 0.665, 0.705, 0.740, 0.783, 0.842, 0.865, 1.610, 2.190]
			bl = ['02','03','04','05','06','07','08','8a','11','12']
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		# Sentinel-3 center wavelength from Sentinel-3 xfdumanifest.xml
		elif satelliteName == cfg.satSentinel3:
			wl = [0.400, 0.4125, 0.4425, 0.490, 0.510, 0.560, 0.620, 0.665, 0.67375, 0.68125, 0.70875, 0.75375, 0.76125, 0.764375, 0.7675, 0.77875, 0.865, 0.885, 0.900, 0.940, 1.020]
			bl = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
			id = cfg.ui.unit_combo.findText(cfg.wlMicro)
		cfg.BandTabEdited = "No"
		if bandList is None:
			vals = []
			for i in range(0, c):
				try:
					b = bl.index(tW.item(i, 0).text().lower().split(".")[0][-2:])
					val = float(wl[b])
					if val not in vals:
						tW.item(i, 1).setText(str(val))					
						vals.append(val)
					else:
						tW.item(i, 1).setText(str(i))
				except:
					try:
						b = bl.index(tW.item(i, 0).text().lower().split(".")[0][-2:].lstrip('0'))				
						val = float(wl[b])
						if val not in vals:
							tW.item(i, 1).setText(str(val))					
							vals.append(val)
						else:
							tW.item(i, 1).setText(str(i))
					except:
						try:
							val = float(wl[i])
							if val not in vals:
								tW.item(i, 1).setText(str(val))					
								vals.append(val)
							else:
								tW.item(i, 1).setText(str(i))							
						except:
							pass
		else:
			b = 0
			for n in bandList:
				i = wl[n - 1]
				tW.item(b, 1).setText(str(float(i)))
				b = b + 1
		tW.blockSignals(False)
		cfg.BandTabEdited = "Yes"
		cfg.bst.orderByWavelength(bandSetNumber)
		noUnitId = cfg.ui.unit_combo.findText(cfg.noUnit)
		cfg.ui.unit_combo.setCurrentIndex(noUnitId)
		cfg.ui.unit_combo.setCurrentIndex(id)
		self.readBandSet("Yes")
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " satellite" + str(satelliteName))
			
	# add file to band set action
	def addFileToBandSetAction(self):
		self.addFileToBandSet()
		
	# add file to band set
	def addFileToBandSet(self, batch = "No", fileListString = None, wavelengthString = None, multiplicativeFactorString = None, additiveFactorString = None, bandSetNumber = None):		
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		if batch == "No":
			files = cfg.utls.getOpenFileNames(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a raster"), "", "Raster (*.*)")
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
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msgErr25()
				return "No"
			if iBC > 1:
				r =cfg.utls.addRasterLayer(files[0], cfg.osSCP.path.basename(files[0]))
				cfg.utls.clearTable(tW)
				cfg.QtWidgetsSCP.qApp.processEvents()
				cfg.ipt.checkRefreshRasterLayer()
				# load project image name in combo
				id = cfg.ui.image_raster_name_combo.findText(r.name())
				cfg.ui.image_raster_name_combo.setCurrentIndex(id)
				return "Yes"
		# check if single raster
		if c > 0 and cfg.bandSetsList[bandSetNumber][0] == "No":
			cfg.utls.clearTable(tW)
		for i in files:
			check = "Yes"
			try:
				iBC = cfg.utls.getNumberBandRaster(i)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msgErr25()
				iBC = None
				check = "No"
			if iBC == 1 and check == "Yes":
				r =cfg.utls.addRasterLayer(i)
				itN = r.name()
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
				cfg.utls.addTableItem(tW, cfg.ui.unit_combo.currentText(), c, 4)
				cfg.utls.addTableItem(tW, "", c, 5)
		tW.blockSignals(False)
		cfg.bst.rasterBandName()
		self.readBandSet("Yes")
		cfg.BandTabEdited = "Yes"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set changed n. of bands" + str(c))
			
	# add band to band set
	def addBandToSet(self):	
		bandSetNumber = None
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bandSetsList[bandSetNumber][0] == "No":
			pass
		else:
			l = cfg.ui.bands_tableWidget
			c = l.rowCount()
			s = l.selectedItems()
			ns  = []
			for i in range (0, len(s)):
				ns.append(s[i].row())
			lc = list(set(ns))
			cfg.BandTabEdited = "No"
			tW.blockSignals(True)
			if len(list(cfg.bandSetsList[bandSetNumber][4])) > 0:
				v = max(cfg.bandSetsList[bandSetNumber][4])
			else:
				v = 0
			for b in lc:
				# count table rows
				c = tW.rowCount()
				v = v + 1
				# name of item of list
				itN = l.item(b, 0).text()
				# add list items to table
				tW.setRowCount(c + 1)
				cfg.utls.addTableItem(tW, itN, c, 0)
				cfg.utls.addTableItem(tW, str(float(v)), c, 1)
				cfg.utls.addTableItem(tW, "1", c, 2)
				cfg.utls.addTableItem(tW, "0", c, 3)
				cfg.utls.addTableItem(tW, cfg.ui.unit_combo.currentText(), c, 4)
				cfg.utls.addTableItem(tW, "", c, 5)
			tW.blockSignals(False)
			self.readBandSet("Yes")
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set changed n. of bands" + str(lc))
		
	# set all bands to state 0 or 2
	def allBandSetState(self, value):
		tW = cfg.ui.bands_tableWidget
		c = tW.rowCount()
		if value == 0:
			tW.clearSelection() 
		else:
			v = list(range(0, c))
			cfg.utls.selectRowsInTable(tW, v)
		
	# set raster name as band set
	def rasterLayerName(self):
		if cfg.rasterComboEdited == "Yes":
			imgNm = cfg.ui.image_raster_name_combo.currentText()
			# set input
			rLay = cfg.utls.selectLayerbyName(imgNm)
			if rLay is not None:
				cfg.bst.clearBandSet("No", "No")
				cfg.bst.rasterToBandName(imgNm)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "input raster: " + str(imgNm))
			
	# clear the band set
	def clearBandSetAction(self):
		self.clearBandSet()
		
	# clear the band set
	def clearBandSet(self, question = "Yes", refresh = "Yes", bandSetNumber = None):
		if question == "Yes":
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Clear band set"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the band set?"))
		else:
			a = "Yes"
		if a == "Yes":	
			if bandSetNumber == None:
				bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
			tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
			cfg.BandTabEdited = "No"
			cfg.utls.clearTable(tW)
			cfg.BandTabEdited = "Yes"
			# band set list
			try:
				cfg.bandSetsList[bandSetNumber] = []
			except:
				pass
			if refresh == "Yes":
				# read band set
				self.readBandSet("Yes", refresh)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set cleared")
		
	# order by wavelength
	def orderByWavelength(self, bandSetNumber):
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		cfg.BandTabEdited = "No"
		tW.blockSignals(True)		
		nm = []
		wvl = []
		add = []
		mul = []
		id = []
		c = tW.rowCount()
		for b in range(0, c):
			nm.append(tW.item(b, 0).text())
			wvl.append(float(tW.item(b, 1).text()))
			mul.append(tW.item(b, 2).text())
			add.append(tW.item(b, 3).text())
		if wvl is not None:
			# sort items
			b = 0
			for i in sorted(wvl):
				x = wvl.index(i)
				cfg.utls.addTableItem(tW, nm[x], b, 0, "No")
				cfg.utls.addTableItem(tW, str(float(i)), b, 1)
				cfg.utls.addTableItem(tW, str(mul[x]), b, 2)
				cfg.utls.addTableItem(tW, str(add[x]), b, 3)
				b = b + 1
			tW.show()
			self.readBandSet("Yes")
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ordered bands")
		tW.blockSignals(False)
		cfg.BandTabEdited = "Yes"
		
	# band set edited
	def editedBandSet(self, row, column):
		bandSetNumber = None
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		if cfg.BandTabEdited == "Yes" and column == 1:
			# check if bandset is empty
			c = tW.rowCount()
			cfg.BandTabEdited = "No"
			try:
				w = str(float(tW.item(row, column).text()))
			except:
				w = str(float(cfg.bandSetsList[bandSetNumber][4][row]))
			cfg.utls.setTableItem(tW, row, column, w)
			tW.show()
			if c == 0:
				self.readBandSet("Yes")
			elif float(tW.item(row, column).text()) in cfg.bandSetsList[bandSetNumber][4]:
				cfg.mx.msgWar7()
				w = str(float(cfg.bandSetsList[bandSetNumber][4][row]))
				cfg.utls.setTableItem(tW, row, column, w)
				tW.show()
			else:
				cfg.bst.orderByWavelength(bandSetNumber)
			cfg.BandTabEdited = "Yes"
		elif cfg.BandTabEdited == "Yes" and column == 2:
			# check if bandset is empty
			c = tW.rowCount()
			if c == 0:
				self.readBandSet("No")
			else:
				cfg.BandTabEdited = "No"
				try:
					test = float(tW.item(row, column).text())
					cfg.utls.addTableItem(tW, str(tW.item(row, column).text()), row, column)
				except:
					cfg.utls.addTableItem(tW, str(cfg.bandSetsList[bandSetNumber][6][0][row]), row, column)
				tW.show()
				self.readBandSet("No")
				cfg.BandTabEdited = "Yes"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band edited; bands n. " + str(c))
		elif cfg.BandTabEdited == "Yes" and column == 3:
			# check if bandset is empty
			c = tW.rowCount()
			if c == 0:
				self.readBandSet("No")
			else:
				cfg.BandTabEdited = "No"
				try:
					test = float(tW.item(row, column).text())
					cfg.utls.addTableItem(tW, str(tW.item(row, column).text()), row, column)
				except:
					cfg.utls.addTableItem(tW, str(cfg.bandSetsList[bandSetNumber][6][1][row]), row, column)
				tW.show()
				self.readBandSet("No")
				cfg.BandTabEdited = "Yes"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band edited; bands n. " + str(c))
		elif cfg.BandTabEdited == "Yes" and column == 4:
			cfg.BandTabEdited = "No"
			cfg.utls.addTableItem(tW, str(cfg.bst.unitNameConversion(cfg.bandSetsList[bandSetNumber][5], "Yes")), row, column)
			cfg.BandTabEdited = "Yes"
		elif cfg.BandTabEdited == "Yes" and column == 5:
			cfg.BandTabEdited = "No"
			cfg.utls.addTableItem(tW, str(cfg.bandSetsList[bandSetNumber][8]), row, column)
			cfg.BandTabEdited = "Yes"
		elif cfg.BandTabEdited == "Yes" and column == 0:
			cfg.BandTabEdited = "No"
			cfg.utls.addTableItem(tW, str(cfg.bandSetsList[bandSetNumber][3][row]), row, column)
			cfg.BandTabEdited = "Yes"
		
	# tab band set changed
	def tabBandSetChanged(self, index):
		if cfg.BandTabEdited == "Yes":
			cfg.bndSetNumber = index
			t = cfg.ui.Band_set_tabWidget.count()
			cfg.bndSetTabList = []
			for i in range(0, t):
				cfg.bndSetTabList.append(str(cfg.ui.Band_set_tabWidget.widget(i).objectName()).split("__")[1])
				cfg.ui.Band_set_tabWidget.setTabText(i, cfg.bandSetName + str(i + 1))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " changed tab band set")
			cfg.bst.readBandSet("Yes")
		
	# select band set tab
	def selectBandSetTab(self, index):
		t = len(cfg.bndSetTabList)
		if index >= t:
			cfg.mx.msgErr62(str(index + 1))
		else:
			cfg.ui.Band_set_tabWidget.setCurrentIndex(index)
		
	# select band set tab
	def removeBandSetTab(self, index):
		t = len(cfg.bndSetTabList)
		if t > 1:
			cfg.bst.deleteBandSetTab(index)
		else:
			cfg.mx.msgErr62(str(index + 1))
		
	# add band set tab
	def addBandSetTabAction(self):
		cfg.bst.addBandSetTab()
		
	# add band set tab
	def addBandSetTab(self, refresh = "Yes"):
		cfg.algWT.addBandSetWeigthTab()
		dT = cfg.utls.getTime()
		w = "cfg.ui.tableWidget__" + str(dT)
		cfg.bndSetTabList.append(dT)
		band_set_tab = cfg.QtWidgetsSCP.QWidget()
		band_set_tab.setObjectName(w)	
		gridLayout = cfg.QtWidgetsSCP.QGridLayout(band_set_tab)
		gridLayout.setObjectName("gridLayout" + str(dT))		
		exec(w + " = cfg.QtWidgetsSCP.QTableWidget(band_set_tab)")
		tW = eval(w)
		tW.setFrameShape(cfg.QtWidgetsSCP.QFrame.WinPanel)
		tW.setFrameShadow(cfg.QtWidgetsSCP.QFrame.Sunken)
		tW.setAlternatingRowColors(True)
		tW.setSelectionMode(cfg.QtWidgetsSCP.QAbstractItemView.MultiSelection)
		tW.setSelectionBehavior(cfg.QtWidgetsSCP.QAbstractItemView.SelectRows)
		tW.setColumnCount(6)
		tW.setObjectName(w)
		tW.setRowCount(0)
		item = cfg.QtWidgetsSCP.QTableWidgetItem()
		tW.setHorizontalHeaderItem(0, item)
		item = cfg.QtWidgetsSCP.QTableWidgetItem()
		tW.setHorizontalHeaderItem(1, item)
		item = cfg.QtWidgetsSCP.QTableWidgetItem()
		tW.setHorizontalHeaderItem(2, item)
		item = cfg.QtWidgetsSCP.QTableWidgetItem()
		tW.setHorizontalHeaderItem(3, item)
		item = cfg.QtWidgetsSCP.QTableWidgetItem()
		tW.setHorizontalHeaderItem(4, item)
		item = cfg.QtWidgetsSCP.QTableWidgetItem()
		tW.setHorizontalHeaderItem(5, item)
		item = tW.horizontalHeaderItem(0)
		item.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band name"))
		item = tW.horizontalHeaderItem(1)
		item.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Center wavelength"))
		item = tW.horizontalHeaderItem(2)
		item.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Multiplicative Factor"))
		item = tW.horizontalHeaderItem(3)
		item.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Additive Factor"))
		item = tW.horizontalHeaderItem(4)
		item.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Wavelength unit"))
		item = tW.horizontalHeaderItem(5)
		item.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Image name"))
		tW.verticalHeader().setDefaultSectionSize(16)
		tW.horizontalHeader().setStretchLastSection(True)
		gridLayout.addWidget(tW, 0, 0, 1, 1)
		# connect to edited cell
		try:
			tW.cellChanged.disconnect()
		except:
			pass
		tW.cellChanged.connect(cfg.bst.editedBandSet)
		cfg.ui.Band_set_tabWidget.addTab(band_set_tab, cfg.bandSetName + str(len(cfg.bndSetTabList)))		
		cfg.utls.setColumnWidthList(tW, [[0, 350], [1, 150], [2, 150], [3, 150], [4, 150], [5, 150]])
		if refresh == "Yes":
			cfg.bst.readBandSet("Yes")
			cfg.ui.Band_set_tabWidget.setCurrentIndex(len(cfg.bndSetTabList) - 1)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " added band set")
		return len(cfg.bndSetTabList) - 1
			
	# close Band set tab
	def closeBandSetTab(self, index):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Remove band set"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to remove band set " + str(index + 1) + "?"))
		if a == "Yes":
			t = len(cfg.bndSetTabList)
			if t > 1:
				cfg.bst.deleteBandSetTab(index)
				for i in range(0, t-1):
					cfg.ui.Band_set_tabWidget.setTabText(i, cfg.bandSetName + str(i + 1))
				cfg.bst.readBandSet("Yes")
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " closed band set " + str(index + 1))
			else:
				cfg.mx.msg24()
				
	# delete Band set tab	
	def deleteBandSetTab(self, index):
		try:
			cfg.bndSetTabList.pop(index)
			cfg.ui.Band_set_tabWidget.removeTab(index)
			cfg.algWT.deleteBandSetWeigthTab(index)
		except Exception as err:
			cfg.mx.msgErr62(str(index + 1))
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# read band set
	def readBandSet(self, bandsetPresent = "Yes", refresh = "No"):
		cfg.bandSetsList = []
		imgName = ""		
		for i in range(0, len(cfg.bndSetTabList)):
			try:
				tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[i])	
			except Exception as err:
				self.tabBandSetChanged(0)
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return
			# check if bandset is empty
			c = tW.rowCount()
			bandSetList = [bandsetPresent, i, c, None, None, None, None, None, None]
			# band set name list
			bndSet = []
			# band set wavelength
			bndSetWvLn = []
			# band set multiplicative and additive factors
			bndSetMultiFactorsList = []
			bndSetAddFactorsList = []
			unit = cfg.noUnit
			if c == 0:
				bandSetList[0] = "No"
				if refresh == "Yes":
					cfg.ipt.refreshRasterLayer()
			else:
				for b in range(0, c):
					imgName = tW.item(0, 5).text()
					bndSet.append(tW.item(b, 0).text())
					bndSetWvLn.append(float(tW.item(b, 1).text()))
					try:
						bndSetMultiFactorsList.append(float(tW.item(b, 2).text()))
					except:
						bndSetMultiFactorsList.append(1)
					try:
						bndSetAddFactorsList.append(float(tW.item(b, 3).text()))
					except:
						bndSetAddFactorsList.append(0)
					try:
						unit = tW.item(0, 4).text()
					except:
						unit = cfg.noUnit						
			bandSetList[7] = cfg.bandSetName + str(i)	
			if imgName == "":
				bandSetList[0] = "Yes"
				bandSetList[8] = ""
			else:
				bandSetList[0] = "No"
				bandSetList[8] = imgName
			bandSetList[3] = bndSet
			bandSetList[4] = bndSetWvLn
			bandSetList[5] = self.unitNameConversion(unit)
			bandSetList[6] = [bndSetMultiFactorsList, bndSetAddFactorsList]					
			cfg.bandSetsList.append(bandSetList)
		cfg.bCalc.rasterBandName()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " read band set")
		cfg.bst.configureBandSet(bandsetPresent)

	# configure band set
	def configureBandSet(self, reset = "Yes", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
			# write project variables
			cfg.utls.writeProjectVariable("bandSetsList", str(cfg.bandSetsList))		
			cfg.utls.writeProjectVariable("bndSetNumber", str(cfg.bndSetNumber))
			cfg.tmpVrt = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " configure band set")
		try:
			cfg.bandSetsList[bandSetNumber][3]
		except:
			return "No"
		# find band number
		if len(cfg.bandSetsList[bandSetNumber][3]) > 0:
			cfg.utls.findBandNumber()
		cfg.utls.checkBandSet(bandSetNumber)		
		# reset rapid ROI spinbox
		cfg.uidc.rapidROI_band_spinBox.setValue(1)
		# read algorithm weight table
		if reset == "Yes":
			cfg.algWT.resetAlgorithmTable()
		else:
			cfg.algWT.readAlgorithmTable()
		
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
		bndSetFile = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save the band set to file"), "", "*.xml", "xml")
		if bndSetFile is not False:
			if bndSetFile.lower().endswith(".xml"):
				pass
			else:
				bndSetFile = bndSetFile + ".xml"
			try:
				bandSetNumber = None
				if bandSetNumber == None:
					bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
				tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
				# check if bandset is empty
				c = tW.rowCount()
				if c != 0:
					root = cfg.ETSCP.Element("bandset")
					root.set("unit",str(cfg.bandSetsList[bandSetNumber][5]))
					root.set("bandsetpresent",str(cfg.bandSetsList[bandSetNumber][0]))
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
						unitField = cfg.ETSCP.SubElement(bandItem, "wavelength_unit")
						unitField.text = tW.item(b, 4).text()
						imageNameField = cfg.ETSCP.SubElement(bandItem, "image_name")
						imageNameField.text = tW.item(b, 5).text()						
					o = open(bndSetFile, 'w')
					f = cfg.minidomSCP.parseString(cfg.ETSCP.tostring(root)).toprettyxml()
					o.write(f)
					o.close()
					# logger
					cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set exported")
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# import band set from file
	def importBandSet(self):
		bndSetFile = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a band set file"), "", "XML (*.xml)")
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
				wlU = {}
				imNm = {}
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
					wlU[n] = str(child.find("wavelength_unit").text.strip())
					try:		
						imNm[n] = str(child.find("image_name").text.strip())
					except:
						imNm[n] = ""					
				bandSetNumber = None
				if bandSetNumber == None:
					bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
				tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
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
					cfg.utls.addTableItem(tW, str(wlU[x]), c, 4)
					cfg.utls.addTableItem(tW, str(imNm[x]), c, 5)					
				self.readBandSet("Yes")
				cfg.BandTabEdited = "Yes"
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set imported")
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msgErr5()
				
	# set band set
	def setBandSet(self, bandNameList, bandSetNumber = None):
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		cfg.BandTabEdited = "No"
		try:
			while tW.rowCount() > 0:
				tW.removeRow(0)
			for x in bandNameList:
				c = tW.rowCount()
				# add list items to table
				tW.setRowCount(c + 1)
				cfg.utls.addTableItem(tW, x, c, 0, "No")
				cfg.utls.addTableItem(tW, c+1, c, 1)
				cfg.utls.addTableItem(tW, "1", c, 2)
				cfg.utls.addTableItem(tW, "0", c, 3)
				cfg.utls.addTableItem(tW, cfg.noUnit, c, 4)
				cfg.utls.addTableItem(tW, "", c, 5)
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set set")
		except Exception as err:
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr5()
			
	# move down selected band
	def moveDownBand(self):
		bandSetNumber = None
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bandSetsList[bandSetNumber][0] == "No":
			pass
		else:
			s = tW.selectedItems()
			cfg.BandTabEdited = "No"
			# create list for new selection after move
			ns  = []
			for i in range (0, len(s)):
				ns.append(s[i].row() + 1)
			try:
				for b in reversed(list(range(0, c))):
					if tW.item(b, 0).isSelected() or tW.item(b, 1).isSelected():
						bNU = tW.item(b, 0).text()
						bND = tW.item(b + 1, 0).text()
						tW.item(b, 0).setText(str(bND))
						tW.item(b + 1, 0).setText(str(bNU))
				tW.clearSelection()
				v = list(set(ns))
				for i in range (0, len(v)):
					tW.selectRow(v[i])
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
			# update band set
			self.readBandSet("Yes")
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band moved")

	# sort band name
	def sortBandName(self):
		bandSetNumber = None
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bandSetsList[bandSetNumber][0] == "No":
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
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
			# update band set
			self.readBandSet("Yes")
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band moved")
	
	# move up selected band
	def moveUpBand(self):
		bandSetNumber = None
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bandSetsList[bandSetNumber][0] == "No":
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
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
			# update band set
			self.readBandSet("Yes")
			cfg.BandTabEdited = "Yes"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band moved")
				
	# Set raster band checklist
	def rasterBandName(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		tW = cfg.ui.bands_tableWidget
		cfg.utls.clearTable(tW)
		for x in sorted(ls, key=lambda c: c.name()):
			if x.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer and x.bandCount() == 1 and cfg.bndSetVrtNm not in x.name():
				tW.blockSignals(True)
				# count table rows
				c = tW.rowCount()
				# add list items to table
				tW.setRowCount(c + 1)
				cfg.utls.addTableItem(tW, x.name(), c, 0)
				tW.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster band name checklist created")
		
	# Set raster to single band names for wavelength definition
	def rasterToBandName(self, rasterName, bandset = "No", bandSetNumber = None):		
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
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
			v = i + 1
			wl = str(float(v))
			cfg.utls.addTableItem(tW, wl, c, 1)
			cfg.utls.addTableItem(tW, "1", c, 2)
			cfg.utls.addTableItem(tW, "0", c, 3)
			cfg.utls.addTableItem(tW, "0", c, 4)
			cfg.utls.addTableItem(tW, cfg.ui.unit_combo.currentText(), c, 4)
			cfg.utls.addTableItem(tW, rasterName, c, 5)
		self.readBandSet("Yes")
		tW.blockSignals(False)
		cfg.BandTabEdited = "Yes"
	
	# remove selected band
	def removeBand(self):
		bandSetNumber = None
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bandSetsList[bandSetNumber][0] == "No":
			cfg.mx.msg25()
		else:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Remove band"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to remove the selected bands from band set?"))
			if a == "Yes":
				r = []
				for i in tW.selectedItems():
					r.append(i.row())
				v = sorted(list(set(r)))
				cfg.BandTabEdited = "No"
				for x in reversed(v):
				# remove items
					tW.removeRow(x)
				self.readBandSet("Yes")
				cfg.BandTabEdited = "Yes"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band removed; bands n. " + str(c))
		
	# select all bands for set
	def selectAllBands(self):
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
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				pass
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all bands clicked")
		
	# create virtual raster
	def virtualRasterBandSet(self, outFile = None, bandSetNumber = None):		
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		if cfg.bandSetsList[bandSetNumber][0] == "Yes":
			ck = cfg.utls.checkBandSet(bandSetNumber)
			if outFile is None:
				rstrOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save virtual raster"), "", "*.vrt", "vrt")
			else:
				rstrOut = outFile
			if rstrOut is not False and ck == "Yes":
				if rstrOut.lower().endswith(".vrt"):
					pass
				else:
					rstrOut = rstrOut + ".vrt"
				st = cfg.utls.createVirtualRaster(cfg.bndSetLst, rstrOut, "No", "Yes", "Yes", 0)
				# add virtual raster to layers
				cfg.utls.addRasterLayer(str(rstrOut), str(cfg.osSCP.path.basename(rstrOut)))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " virtual raster: " + str(st))
			elif ck == "No":
				cfg.mx.msgErr33()
			
	def stackBandSet(self, outFile = None, bandSetNumber = None):		
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		if cfg.bandSetsList[bandSetNumber][0] == "Yes":
			ck = cfg.utls.checkBandSet(bandSetNumber)
			if outFile is None:
				rstrOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster"), "", "*.tif", "tif")
			else:
				rstrOut = outFile
			if rstrOut is not False and ck == "Yes":
				if rstrOut.lower().endswith(".tif"):
					pass
				else:
					rstrOut = rstrOut + ".tif"
				if outFile is None:
					cfg.uiUtls.addProgressBar()
				cfg.uiUtls.updateBar(10)
				st = cfg.utls.mergeRasterBands(cfg.bndSetLst, rstrOut)
				if cfg.osSCP.path.isfile(rstrOut):
					cfg.cnvs.setRenderFlag(False)
					cfg.utls.addRasterLayer(str(rstrOut), str(cfg.osSCP.path.basename(rstrOut)))
					cfg.cnvs.setRenderFlag(True)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster: " + str(st))
					cfg.uiUtls.updateBar(100)
				if outFile is None:
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
			elif ck == "No":
				cfg.mx.msgErr33()

	# build band overviews
	def buildOverviewsBandSet(self, quiet = "No", bandSetNumber = None):
		if bandSetNumber == None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
		c = tW.rowCount()
		# check if single raster
		if c > 0:
			if quiet == "Yes":
				a = "Yes"
			else:
				# ask for confirm
				a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Build overviews"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Do you want to build the external overviews of bands?"))
			if a == "Yes":	
				if quiet == "No":
					cfg.uiUtls.addProgressBar()
				if cfg.bandSetsList[bandSetNumber][0] == "Yes":
					b = 1
					for i in cfg.bndSetLst:
						cfg.utls.buildOverviewsGDAL(i)
						cfg.uiUtls.updateBar((b) * 100 / (len(cfg.bndSetLst)), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " building overviews"))
						b = b + 1
				else:
					image = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], "Yes")
					i = cfg.utls.layerSource(image)
					cfg.uiUtls.updateBar(50, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " building overviews"))
					cfg.utls.buildOverviewsGDAL(i)
				cfg.uiUtls.updateBar(100)
				if quiet == "No":
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all bands clicked")
				
	# button perform Band set tools
	def performBandSetTools(self):
		if cfg.ui.overview_raster_bandset_checkBox.isChecked() is True and cfg.ui.band_calc_checkBox.isChecked() is False and cfg.ui.stack_raster_bandset_checkBox.isChecked() is False and cfg.ui.virtual_raster_bandset_checkBox.isChecked() is False:
			i = "Yes"
		else:
			i = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
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
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		if cfg.actionCheck == "Yes":
			if cfg.ui.stack_raster_bandset_checkBox.isChecked() is True:
				try:
					cfg.bst.stackBandSet(outputDirectory + "/" + cfg.osSCP.path.basename(cfg.bndSetLst[0]).split(".")[0][:-1] + cfg.stackRasterNm + ".tif")
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		if cfg.actionCheck == "Yes":
			if cfg.ui.overview_raster_bandset_checkBox.isChecked() is True:
				cfg.bst.buildOverviewsBandSet("Yes")
				