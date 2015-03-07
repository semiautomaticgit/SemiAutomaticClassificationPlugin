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

class AlgWeightTab:

	def __init__(self):
		pass
		
	# load algorithm table
	def loadAlgorithmTable(self, bandNameList):
		self.tableEdited = "No"
		tAW = cfg.ui.tableWidget_weight
		cfg.utls.clearTable(tAW)
		for bd in bandNameList:
			c = tAW.rowCount()
			# add list items to table
			tAW.setRowCount(c + 1)
			i = QTableWidgetItem(str(c + 1))
			i.setFlags(Qt.ItemIsEnabled)
			i.setText(str(c + 1))
			tAW.setItem(c, 0, i)
			b = QTableWidgetItem(str(c + 1))
			b.setFlags(Qt.ItemIsEnabled)
			b.setText(bd)
			tAW.setItem(c, 1, b)	
			w = QTableWidgetItem(str(c + 1))
			w.setText("1")
			tAW.setItem(c, 2, w)
		self.tableEdited = "Yes"
		self.readAlgorithmTable()

	# read algorithm table
	def readAlgorithmTable(self):
		tAW = cfg.ui.tableWidget_weight
		w = []
		c = tAW.rowCount()
		for b in range(0, c):
			wI = tAW.item(b, 2).text()
			w.append(float(wI))
		cfg.algBandWeigths = w
		
	# table edited
	def editedWeightTable(self, row, column):
		if self.tableEdited == "Yes":
			tW = cfg.ui.tableWidget_weight
			t = tW.item(row, column).text()
			try:
				float(t)
			except:
				w = QTableWidgetItem(str(row))
				w.setText("1")
				tW.setItem(row, 2, w)
			cfg.algWT.readAlgorithmTable()
			
	def resetWeights(self):
		# ask for confirm
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Reset weights"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset weights?"))
		if a == "Yes":
			self.loadAlgorithmTable(cfg.bndSet)
		
	# set weights
	def setWeights(self):
		self.tableEdited = "No"
		tAW = cfg.ui.tableWidget_weight
		iR = []
		for i in tAW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		wv = cfg.ui.weight_doubleSpinBox.value()
		if len(v) > 0:
			for c in v:
				w = QTableWidgetItem(str(c))
				w.setText(str(wv))
				tAW.setItem(c, 2, w)
		else:
			v = tAW.rowCount()
			for c in range(0, v):
				w = QTableWidgetItem(str(c))
				w.setText(str(wv))
				tAW.setItem(c, 2, w)
		self.tableEdited = "Yes"
		self.readAlgorithmTable()
