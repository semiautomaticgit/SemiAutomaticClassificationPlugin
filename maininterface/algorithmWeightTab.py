# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2017 by Luca Congedo
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
			cfg.utls.addTableItem(tAW, str(c + 1), c, 0, "No")
			cfg.utls.addTableItem(tAW, bd, c, 1, "No")
			cfg.utls.addTableItem(tAW, "1", c, 2)
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
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		
	# table edited
	def editedWeightTable(self, row, column):
		if self.tableEdited == "Yes":
			tW = cfg.ui.tableWidget_weight
			t = tW.item(row, column).text()
			try:
				float(t)
			except:
				cfg.utls.setTableItem(tW, row, 2, "1")
			cfg.algWT.readAlgorithmTable()
			
	def resetWeights(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset weights"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset weights?"))
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
				cfg.utls.setTableItem(tAW, c, 2, str(wv))
		else:
			v = tAW.rowCount()
			for c in range(0, v):
				cfg.utls.setTableItem(tAW, c, 2, str(wv))
		self.tableEdited = "Yes"
		self.readAlgorithmTable()
