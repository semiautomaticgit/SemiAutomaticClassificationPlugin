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

class AlgWeightTab:

	def __init__(self):
		pass
				
	# reset algorithm table
	def resetAlgorithmTable(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " reset Algorithm Table")
		for index in range(0, len(cfg.bandSetsList)):
			self.tableEdited = "No"
			tW = eval("cfg.ui.alg_weight_tableWidget_" + str(index))
			cfg.utls.clearTable(tW)
			bandNameList = cfg.bandSetsList[index][3]
			for bd in bandNameList:
				c = tW.rowCount()
				# add list items to table
				tW.setRowCount(c + 1)
				cfg.utls.addTableItem(tW, str(c + 1), c, 0, "No")
				cfg.utls.addTableItem(tW, bd, c, 1, "No")
				cfg.utls.addTableItem(tW, "1", c, 2)
			self.tableEdited = "Yes"
			self.readAlgorithmTable()
			
	# load algorithm table
	def loadAlgorithmTable(self, index):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " load Algorithm Table")
		if cfg.bndSetNumber >= 0:
			self.tableEdited = "No"
			tW = eval("cfg.ui.alg_weight_tableWidget_" + str(index))
			cfg.utls.clearTable(tW)
			bandNameList = cfg.bandSetsList[index][3]
			for bd in bandNameList:
				c = tW.rowCount()
				# add list items to table
				tW.setRowCount(c + 1)
				cfg.utls.addTableItem(tW, str(c + 1), c, 0, "No")
				cfg.utls.addTableItem(tW, bd, c, 1, "No")
				cfg.utls.addTableItem(tW, "1", c, 2)
			self.tableEdited = "Yes"
			self.readAlgorithmTable()

	# read algorithm table
	def readAlgorithmTable(self):
		if cfg.bndSetNumber >= 0:
			tW = eval("cfg.ui.alg_weight_tableWidget_" + str(cfg.bndSetNumber))
			w = []
			c = tW.rowCount()
			for b in range(0, c):
				wI = tW.item(b, 2).text()
				w.append(float(wI))
			cfg.algBandWeigths = w
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
	
	# add tab
	def addBandSetWeigthTab(self, refresh = "Yes"):
		t = cfg.ui.alg_band_weight_tabWidget.count()
		band_set_tab = cfg.QtWidgetsSCP.QWidget()
		band_set_tab.setObjectName(cfg.bandSetName + str(t + 1))	
		gridLayout = cfg.QtWidgetsSCP.QGridLayout(band_set_tab)
		gridLayout.setObjectName("gridLayout" + str(t + 1)) 
		exec("cfg.ui.alg_weight_tableWidget_" + str(t) + " = cfg.QtWidgetsSCP.QTableWidget(band_set_tab)")
		tW = eval("cfg.ui.alg_weight_tableWidget_" + str(t))
		tW.setFrameShape(cfg.QtWidgetsSCP.QFrame.WinPanel)
		tW.setFrameShadow(cfg.QtWidgetsSCP.QFrame.Sunken)
		tW.setAlternatingRowColors(True)
		tW.setSelectionMode(cfg.QtWidgetsSCP.QAbstractItemView.MultiSelection)
		tW.setSelectionBehavior(cfg.QtWidgetsSCP.QAbstractItemView.SelectRows)
		tW.setColumnCount(3)
		tW.setObjectName(cfg.bandSetName + str(t + 1))
		tW.setRowCount(0)
		item = cfg.QtWidgetsSCP.QTableWidgetItem()
		tW.setHorizontalHeaderItem(0, item)
		item = cfg.QtWidgetsSCP.QTableWidgetItem()
		tW.setHorizontalHeaderItem(1, item)
		item = cfg.QtWidgetsSCP.QTableWidgetItem()
		tW.setHorizontalHeaderItem(2, item)
		item = tW.horizontalHeaderItem(0)
		item.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band number"))
		item = tW.horizontalHeaderItem(1)
		item.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band name"))
		item = tW.horizontalHeaderItem(2)
		item.setText(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Weight"))
		tW.verticalHeader().setDefaultSectionSize(16)
		tW.horizontalHeader().setDefaultSectionSize(200)
		tW.horizontalHeader().setStretchLastSection(True)
		gridLayout.addWidget(tW, 0, 0, 1, 1)
		# connect to edited cell
		try:
			tW.cellChanged.disconnect()
		except:
			pass
		tW.cellChanged.connect(cfg.algWT.editedWeightTable)
		cfg.ui.alg_band_weight_tabWidget.addTab(band_set_tab, cfg.bandSetName + str(t + 1))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " added band set weight tab " + str(t + 1))
		
	# delete Band set Weigth tab	
	def deleteBandSetWeigthTab(self, index):
		cfg.ui.alg_band_weight_tabWidget.removeTab(index)
		for i in range(0, index):
			cfg.ui.alg_band_weight_tabWidget.setTabText(i, cfg.bandSetName + str(i + 1))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " closed band set weigth " + str(index + 1))
		
	# table edited
	def editedWeightTable(self, row, column):
		bandSetNumber = cfg.ui.alg_band_weight_tabWidget.currentIndex()
		if self.tableEdited == "Yes":
			tW = eval("cfg.ui.alg_weight_tableWidget_" + str(bandSetNumber))
			t = tW.item(row, column).text()
			try:
				float(t)
			except:
				cfg.utls.setTableItem(tW, row, 2, "1")
			cfg.algWT.readAlgorithmTable()
			
	def resetWeights(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset weights"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset weights?"))
		if a == "Yes":
			bandSetNumber = cfg.ui.alg_band_weight_tabWidget.currentIndex()
			self.loadAlgorithmTable(bandSetNumber)
		
	# set weights
	def setWeights(self):
		self.tableEdited = "No"
		bandSetNumber = cfg.ui.alg_band_weight_tabWidget.currentIndex()
		tW = eval("cfg.ui.alg_weight_tableWidget_" + str(bandSetNumber))
		iR = []
		for i in tW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		wv = cfg.ui.weight_doubleSpinBox.value()
		if len(v) > 0:
			for c in v:
				cfg.utls.setTableItem(tW, c, 2, str(wv))
		else:
			v = tW.rowCount()
			for c in range(0, v):
				cfg.utls.setTableItem(tW, c, 2, str(wv))
		self.tableEdited = "Yes"
		self.readAlgorithmTable()
