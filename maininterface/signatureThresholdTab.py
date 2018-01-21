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

class SigThresholdTab:

	def __init__(self):
		pass

	# Create signature list table
	def signatureThresholdListTable(self):
		l = cfg.ui.signature_threshold_tableWidget
		self.tableEdited = "No"
		l.blockSignals(True)
		cfg.utls.clearTable(l)
		x = 0
		for k in list(cfg.signIDs.values()):
			cfg.utls.insertTableRow(l, x)
			cfg.utls.addTableItem(l, int(cfg.signList["MACROCLASSID_" + str(k)]), x, 0, "No")
			cfg.utls.addTableItem(l, str(cfg.signList["MACROCLASSINFO_" + str(k)]), x, 1, "No")
			cfg.utls.addTableItem(l, int(cfg.signList["CLASSID_" + str(k)]), x, 2, "No")
			cfg.utls.addTableItem(l, str(cfg.signList["CLASSINFO_" + str(k)]), x, 3, "No")
			cfg.utls.addTableItem(l, str(cfg.signList["MD_THRESHOLD_" + str(k)]), x, 4)
			cfg.utls.addTableItem(l, str(cfg.signList["ML_THRESHOLD_" + str(k)]), x, 5)
			cfg.utls.addTableItem(l, str(cfg.signList["SAM_THRESHOLD_" + str(k)]), x, 6)
			cfg.utls.addTableItem(l, str(cfg.signIDs["ID_" + str(k)]), x, 7, "No")
			x = x + 1
		l.blockSignals(False)
		self.tableEdited = "Yes"
		cfg.utls.sortTableColumn(l, 7)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signature list threshold created")
		
	# read threshold table
	def readThresholdTable(self):
		tAW = cfg.ui.signature_threshold_tableWidget
		c = tAW.rowCount()
		for b in range(0, c):
			try:
				wI = tAW.item(b, 4).text()
				wIML = tAW.item(b, 5).text()
				wISAM = tAW.item(b, 6).text()
				id = tAW.item(b, 7).text()
				cfg.signList["MD_THRESHOLD_" + str(id)] = wI
				cfg.signList["ML_THRESHOLD_" + str(id)] = wIML
				cfg.signList["SAM_THRESHOLD_" + str(id)] = wISAM
			except:
				pass

	# edited threshold table
	def editedThresholdTable(self, row, column):
		if self.tableEdited == "Yes":
			tW = cfg.ui.signature_threshold_tableWidget
			t = tW.item(row, column).text()
			try:
				tr = float(t)
			except:
				self.tableEdited = "No"
				tW.blockSignals(True)
				cfg.utls.setTableItem(tW, row, column, "0")
				tW.blockSignals(False)
				self.tableEdited = "Yes"
				cfg.signT.readThresholdTable()
				return 0
			if column == 5:
				if tr > 100:
					cfg.mx.msg10()
					self.tableEdited = "No"
					tW.blockSignals(True)
					cfg.utls.setTableItem(tW, row, column, "100")
					tW.blockSignals(False)
					self.tableEdited = "Yes"
			elif column == 6:
				if tr > 90:
					cfg.mx.msg11()
					self.tableEdited = "No"
					tW.blockSignals(True)
					cfg.utls.setTableItem(tW, row, column, "90")
					tW.blockSignals(False)
					self.tableEdited = "Yes"
			cfg.signT.readThresholdTable()
			
	# reset thresholds
	def resetThresholds(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset thresholds?"))
		if a == "Yes":
			tW = cfg.ui.signature_threshold_tableWidget
			v = tW.rowCount()
			self.tableEdited = "No"
			tW.blockSignals(True)
			for c in range(0, v):
				cfg.utls.setTableItem(tW, c, 4, "0")
				cfg.utls.setTableItem(tW, c, 5, "0")
				cfg.utls.setTableItem(tW, c, 6, "0")
			tW.blockSignals(False)
			self.tableEdited = "Yes"
			cfg.signT.readThresholdTable()
				
	# set thresholds
	def setThresholds(self):
		self.tableEdited = "No"
		i = None
		tW = cfg.ui.signature_threshold_tableWidget
		tW.setSortingEnabled(False)
		iR = []
		for i in tW.selectedIndexes():
			iR.append([i.row(), i.column()])
		self.tableEdited = "No"
		tW.blockSignals(True)
		if len(iR) > 0:
			for c in reversed(iR):
				if c[1] == 6:
					wvSAM = cfg.ui.threshold_doubleSpinBox.value()
					if wvSAM > 90:
						cfg.mx.msg11()
						wvSAM = 90
					try:
						cfg.utls.setTableItem(tW, c[0], 6, str(wvSAM))
					except:
						pass
				elif c[1] == 5:
					wvML = cfg.ui.threshold_doubleSpinBox.value()
					if wvML > 100:
						cfg.mx.msg10()
						wvML = 100
					try:
						cfg.utls.setTableItem(tW, c[0], 5, str(wvML))
					except:
						pass
				else:
					wv = cfg.ui.threshold_doubleSpinBox.value()
					try:
						cfg.utls.setTableItem(tW, c[0], 4, str(wv))
					except:
						pass
		else:
			pass
		tW.setSortingEnabled(True)
		tW.blockSignals(False)
		self.tableEdited = "Yes"
		self.readThresholdTable()
		
	# set weights based on variance
	def setAllWeightsVariance(self):
		tW = cfg.ui.signature_threshold_tableWidget
		iR = []
		for i in tW.selectedIndexes():
			iR.append([i.row(), i.column()])
		if len(iR) > 0:
			self.tableEdited = "No"
			tW.blockSignals(True)
			tW.setSortingEnabled(False)
			for c in reversed(iR):
				id = tW.item(c[0], 7).text()
				# wavelength
				wlg = cfg.signList["WAVELENGTH_" + str(id)]
				val = cfg.signList["VALUES_" + str(id)]
				# counter
				n = 0
				m = []
				# mean plus standard deviation
				mPS = []
				mMS = []
				for s in wlg:
					m.append(val[n * 2])
					sd = val[n * 2 +1]
					mPS.append(val[n * 2] + sd)
					mMS.append(val[n * 2] - sd)
					n = n + 1
				if c[1] == 6:
					angleP = cfg.utls.spectralAngle(m, mPS)
					angleM = cfg.utls.spectralAngle(m, mMS)
					valueTSAM = cfg.ui.multiplicative_threshold_doubleSpinBox.value() * max([angleP, angleM])
					if valueTSAM > 90:
						valueTSAM = 90
					cfg.utls.setTableItem(tW, c[0], 6, str(valueTSAM))
				elif c[1] == 4:
					distP = cfg.utls.euclideanDistance(m, mPS)
					distM = cfg.utls.euclideanDistance(m, mMS)
					valueT = cfg.ui.multiplicative_threshold_doubleSpinBox.value() * max([distP, distM])
					cfg.utls.setTableItem(tW, c[0], 4, str(valueT))
			tW.setSortingEnabled(True)
			tW.blockSignals(False)
			self.tableEdited = "Yes"
			try:
				vOrd = self.orderColumn
			except:
				vOrd = 7
			cfg.utls.sortTableColumn(tW, vOrd, tW.horizontalHeader().sortIndicatorOrder())
			cfg.signT.readThresholdTable()
			
	# ordered table
	def orderedTable(self, column):
		self.orderColumn = column
			