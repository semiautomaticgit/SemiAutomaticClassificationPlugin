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
# for debugging
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class SigThresholdTab:

	def __init__(self):
		pass

	# Create signature list table
	def signatureThresholdListTable(self):
		self.tableEdited = "No"
		l = cfg.ui.signature_threshold_tableWidget
		cfg.utls.clearTable(l)
		x = 0
		for k in cfg.signIDs.values():
			l.insertRow(x)
			l.setRowHeight(x, 20)
			itMID = QTableWidgetItem(str(x + 1))
			itMID.setFlags(Qt.ItemIsEnabled)
			itMID.setText(str(cfg.signList["MACROCLASSID_" + str(k)]))
			l.setItem(x, 0, itMID)
			itMInfo = QTableWidgetItem(str(x + 1))
			itMInfo.setFlags(Qt.ItemIsEnabled)
			itMInfo.setText(str(cfg.signList["MACROCLASSINFO_" + str(k)]))
			l.setItem(x, 1, itMInfo)
			itID = QTableWidgetItem(str(x + 1))
			itID.setFlags(Qt.ItemIsEnabled)
			itID.setText(str(cfg.signList["CLASSID_" + str(k)]))
			l.setItem(x, 2, itID)			
			itInfo = QTableWidgetItem(str(x + 1))
			itInfo.setFlags(Qt.ItemIsEnabled)
			itInfo.setText(str(cfg.signList["CLASSINFO_" + str(k)]))
			l.setItem(x, 3, itInfo)	
			itT = QTableWidgetItem(str(x + 1))
			itT.setText("0")
			l.setItem(x, 4, itT)
			itI = QTableWidgetItem(str(x + 1))
			itI.setFlags(Qt.ItemIsEnabled)
			itI.setText(str(cfg.signIDs["ID_" + str(k)]))
			l.setItem(x, 5, itI)			
			x = x + 1
		self.tableEdited = "Yes"
		self.readThresholdTable()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signature list threshold created")
		
	def readThresholdTable(self):
		tAW = cfg.ui.signature_threshold_tableWidget
		c = tAW.rowCount()
		for b in range(0, c):
			try:
				wI = tAW.item(b, 4).text()
				id = tAW.item(b, 5).text()
				cfg.signList["SIG_THRESHOLD_" + str(id)] = wI
			except:
				pass

	def editedThresholdTable(self, row, column):
		if self.tableEdited == "Yes":
			tW = cfg.ui.signature_threshold_tableWidget
			t = tW.item(row, column).text()
			try:
				tr = float(t)
			except:
				w = QTableWidgetItem(str(row))
				w.setText("0")
				tW.setItem(row, 4, w)
				cfg.signT.readThresholdTable()
				return 0
			if str(cfg.algName) == cfg.algML:
				if tr > 100:
					cfg.mx.msg10()
					w = QTableWidgetItem(str(row))
					w.setText("100")
					tW.setItem(row, 4, w)
			elif str(cfg.algName) == cfg.algSAM:
				if tr > 90:
					cfg.mx.msg11()
					w = QTableWidgetItem(str(row))
					w.setText("90")
					tW.setItem(row, 4, w)
			cfg.signT.readThresholdTable()
			
	def resetThresholds(self):
		# ask for confirm
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Reset thresholds"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset thresholds?"))
		if a == "Yes":
			self.signatureThresholdListTable()
			
	def setThresholds(self):
		self.tableEdited = "No"
		tAW = cfg.ui.signature_threshold_tableWidget
		iR = []
		for i in tAW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		wv = cfg.ui.threshold_doubleSpinBox.value()
		if str(cfg.algName) == cfg.algML:
			if wv > 100:
				cfg.mx.msg10()
				wv = 100
				cfg.ui.threshold_doubleSpinBox.setValue(wv)
		elif str(cfg.algName) == cfg.algSAM:
			if wv > 90:
				cfg.mx.msg11()
				wv = 90
				cfg.ui.threshold_doubleSpinBox.setValue(wv)
		if len(v) > 0:
			for c in v:
				w = QTableWidgetItem(str(c))
				w.setText(str(wv))
				tAW.setItem(c, 4, w)
		else:
			v = tAW.rowCount()
			for c in range(0, v):
				w = QTableWidgetItem(str(c))
				w.setText(str(wv))
				tAW.setItem(c, 4, w)
		self.tableEdited = "Yes"
		self.readThresholdTable()
		
		
	# set all weights
	def setAllWeights(self, value):
		self.tableEdited = "No"
		tAW = cfg.ui.signature_threshold_tableWidget
		v = tAW.rowCount()
		for c in range(0, v):
			w = QTableWidgetItem(str(c))
			w.setText(str(value))
			tAW.setItem(c, 4, w)
		self.tableEdited = "Yes"
		self.readThresholdTable()