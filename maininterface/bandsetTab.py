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
# for debugging
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import xml.etree.cElementTree as ET
from xml.dom import minidom
import SemiAutomaticClassificationPlugin.core.config as cfg

class BandsetTab:

	def __init__(self):
		pass
		
	# add satellite list to combo
	def addSatelliteToCombo(self, satelliteList):
		for i in satelliteList:
			cfg.ui.wavelength_sat_combo.addItem(i)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " satellites added")
			
	# add unit list to combo
	def addUnitToCombo(self, unitList):
		for i in unitList:
			cfg.ui.unit_combo.addItem(i)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " units added")
			
	def setBandUnit(self):
		self.readBandSet(cfg.bndSetPresent)
			
	# set satellite wavelengths
	def setSatelliteWavelength(self):
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
		cfg.ui.unit_combo.setCurrentIndex(id)
		cfg.BandTabEdited = "No"
		b = 0
		for i in wl:
			if b < c:
				tW.item(b, 1).setText(str(float(i)))
				b = b + 1
		tW.blockSignals(False)
		cfg.BandTabEdited = "Yes"
		self.readBandSet(cfg.bndSetPresent)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " satellite" + str(satelliteName))
			
	def  addBandToSet(self):
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
					it = QTableWidgetItem(str(c + 1))
					it.setText(itN)
					tW.setItem(c, 0, it)
					wl = QTableWidgetItem(str(c + 1))
					if len(cfg.bndSetWvLn.values()) > 0:
						v = max(cfg.bndSetWvLn.values()) + 1
					else:
						v = c + 1
					wl.setText(str(float(v)))
					tW.setItem(c, 1, wl)
			tW.blockSignals(False)
			self.readBandSet("Yes")
			cfg.rstrNm = cfg.bndSetNm
			cfg.imgNm = cfg.rstrNm
			cfg.BandTabEdited = "Yes"
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set changed n. of bands" + str(lc))
		
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
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all bands cancelled")
				
	# clear the band set
	def clearBandSet(self, question = "Yes", refresh = "Yes"):
		if question == "Yes":
			# ask for confirm
			a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Clear band set"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the band set?"))
		else:
			a = "Yes"
		if a == "Yes":
			tW = cfg.ui.tableWidget
			cfg.BandTabEdited = "No"
			while tW.rowCount() > 0:
				tW.removeRow(0)
			cfg.BandTabEdited = "Yes"
			# band set unit
			cfg.bndSetUnit = {}
			# band set name list
			cfg.bndSet = []
			# band set wavelength
			cfg.bndSetWvLn = {}
			if refresh == "Yes":
				# read band set
				self.readBandSet("No", refresh)
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set cleared")
		
	# band set edited
	def editedBandSet(self, row, column):
		if cfg.BandTabEdited == "Yes" and column == 1:
			tW = cfg.ui.tableWidget
			# check if bandset is empty
			c = tW.rowCount()
			cfg.BandTabEdited = "No"
			w = QTableWidgetItem(str(row))
			w.setText(str(float(tW.item(row, column).text())))
			tW.setItem(row, column, w)
			tW.show()
			if c == 0:
				self.readBandSet()
			elif float(tW.item(row, column).text()) in cfg.bndSetWvLn.values():
				cfg.mx.msgWar7()
				w = QTableWidgetItem(str(row))
				w.setText(str(float(cfg.bndSetWvLn["WAVELENGTH_" + str(row + 1)])))
				tW.setItem(row, 1, w)
				tW.show()
				cfg.BandTabEdited = "Yes"
			else:
				cfg.BandTabEdited = "No"
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
						n = QTableWidgetItem(str(b))
						n.setFlags(Qt.ItemIsEnabled)
						n.setText(nm[x])
						tW.setItem(b, 0, n)
						w = QTableWidgetItem(str(b))
						w.setText(str(float(i)))
						tW.setItem(b, 1, w)
						b = b + 1
					tW.show()
					self.readBandSet()
					cfg.BandTabEdited = "Yes"
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band edited; bands n. " + str(c))
		
	def readBandSet(self, bandset = "Yes", refresh = "Yes"):
		tW = cfg.ui.tableWidget
		# check if bandset is empty
		c = tW.rowCount()
		cfg.bndSetPresent = bandset
		# band set name list
		cfg.bndSet = []
		# band set wavelength
		cfg.bndSetWvLn = {}
		if c == 0:
			cfg.bndSetPresent = "No"
			if refresh == "Yes":
				cfg.ipt.refreshRasterLayer()
		else:
			for b in range(0, c):
				cfg.bndSet.append(tW.item(b, 0).text())
				cfg.bndSetWvLn["WAVELENGTH_{0}".format(b + 1)] = float(tW.item(b, 1).text())
			if bandset == "Yes":
				cfg.ipt.refreshRasterLayer()
		# read unit
		cfg.bndSetUnit["UNIT"] = self.unitNameConversion(cfg.ui.unit_combo.currentText())
		# write project variables
		cfg.utls.writeProjectVariable("bandSetPresent", str(cfg.bndSetPresent))
		cfg.utls.writeProjectVariable("bandSet", str(cfg.bndSet))
		cfg.utls.writeProjectVariable("bndSetWvLn", str(cfg.bndSetWvLn.values()))
		cfg.utls.writeProjectVariable("bndSetUnit", str(cfg.bndSetUnit["UNIT"]))
	
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
		bndSetFile = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save the band set to file"), "", "XML (*.xml)")
		if len(bndSetFile) > 0:
			try:
				tW = cfg.ui.tableWidget
				# check if bandset is empty
				c = tW.rowCount()
				if c != 0:
					root = ET.Element("bandset")
					root.set("unit",str(cfg.bndSetUnit["UNIT"]))
					root.set("bandsetpresent",str(cfg.bndSetPresent))
					for b in range(0, c):
						bandItem = ET.SubElement(root, "band")
						bandItem.set("number", str(b + 1))
						nameField = ET.SubElement(bandItem, "name")
						nameField.text = tW.item(b, 0).text()
						rangeField = ET.SubElement(bandItem, "wavelength")
						rangeField.text = tW.item(b, 1).text()
					o = open(bndSetFile, 'w')
					f = minidom.parseString(ET.tostring(root)).toprettyxml()
					o.write(f)
					o.close()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set exported")
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# import band set from file
	def importBandSet(self):
		bndSetFile = QFileDialog.getOpenFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Select a band set file"), "", "XML (*.xml)")
		if len(bndSetFile) > 0:
			try:
				tree = ET.parse(bndSetFile)
				root = tree.getroot()
				# band set
				bs = {}
				# wavelength
				wl = {}
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
					bs[n] = str(child.find("name").text)
					wl[n] = float(child.find("wavelength").text)
				tW = cfg.ui.tableWidget
				cfg.BandTabEdited = "No"
				while tW.rowCount() > 0:
					tW.removeRow(0)
				for x in sorted(bN):
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					i = QTableWidgetItem(str(c + 1))
					i.setFlags(Qt.ItemIsEnabled)
					i.setText(bs[x])
					tW.setItem(c, 0, i)
					w = QTableWidgetItem(str(c + 1))
					w.setText(str(wl[x]))
					tW.setItem(c, 1, w)
				self.readBandSet(bandset)
				cfg.BandTabEdited = "Yes"
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band set imported")		
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
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
				for i in range (0, len(ns)):
					tW.selectRow(ns[i])
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
			# update band set
			self.readBandSet()
			cfg.BandTabEdited = "Yes"
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band moved")
	
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
				for i in range (0, len(ns)):
					tW.selectRow(ns[i])
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
			# update band set
			self.readBandSet()
			cfg.BandTabEdited = "Yes"
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band moved")
				
	# Set raster band checklist
	def rasterBandName(self):
		ls = cfg.lgnd.layers()
		# checklist
		l = cfg.ui.raster_listView
		# create band item model
		cfg.bndMdl = QStandardItemModel(l)
		cfg.bndMdl.clear()
		l.setModel(cfg.bndMdl)
		l.show()
		for x in ls:
			if x.type() == QgsMapLayer.RasterLayer and x.bandCount() == 1:
				# band name
				it = QStandardItem(x.name())
				# Create checkbox
				it.setCheckable(True)
				# Add band to model
				cfg.bndMdl.appendRow(it)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster band name checklist created")
		
	# Set raster to single band names for wavelength definition
	def rasterToBandName(self, rasterName, bandset = "No"):
		tW = cfg.ui.tableWidget
		r = cfg.utls.selectLayerbyName(rasterName, "Yes")
		b = r.bandCount()
		cfg.BandTabEdited == "No"
		tW.blockSignals(True)
		for i in range(0, b):
			# count table rows
			c = tW.rowCount()
			# name of item of list
			itN = rasterName + "#b" + str(i)
			# add list items to table
			tW.setRowCount(c + 1)
			it = QTableWidgetItem(str(c + 1))
			it.setText(itN)
			tW.setItem(c, 0, it)
			wl = QTableWidgetItem(str(c + 1))
			if len(cfg.bndSetWvLn.values()) > 0:
				v = max(cfg.bndSetWvLn.values()) + 1
			else:
				v = i + 1
			wl.setText(str(float(v)))
			tW.setItem(c, 1, wl)
		self.readBandSet(bandset)
		tW.blockSignals(False)
		cfg.BandTabEdited == "Yes"
	
	# remove selected band
	def removeBand(self):
		tW = cfg.ui.tableWidget
		c = tW.rowCount()
		# check if single raster
		if c > 0 and cfg.bndSetPresent == "No":
			pass
		else:
			# ask for confirm
			a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Remove band"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to remove the selected bands from band set?"))
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
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " band removed; bands n. " + str(c))
		
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
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				pass
		cfg.uiUtls.removeProgressBar()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all bands clicked")
		