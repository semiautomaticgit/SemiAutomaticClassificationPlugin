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

class LCSigThresholdTab:

	def __init__(self):
		pass

	# Create signature list table
	def LCSignatureThresholdListTable(self):
		l = cfg.ui.LCS_tableWidget
		self.tableEdited = "No"
		l.blockSignals(True)
		l.setSortingEnabled(False)
		# column width
		try:
			wid0 = l.columnWidth(0)
			wid1 = l.columnWidth(1)
			wid2 = l.columnWidth(2)
			wid3 = l.columnWidth(3)
			wid4 = l.columnWidth(4)
		except:
			wid0 = 40
			wid1 = 70
			wid2 = 40
			wid3 = 70
			wid4 = 70
		v = 5
		wid = []
		try:
			for i in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
				try:
					if l.columnWidth(v) == 0:
						wid.append(70)
					else:
						wid.append(l.columnWidth(v))
				except:
					wid.append(70)
				v = v +1
				try:
					if l.columnWidth(v) == 0:
						wid.append(70)
					else:
						wid.append(l.columnWidth(v))
				except:
					wid.append(70)
				v = v +1
		except:
			pass
		cfg.utls.clearTable(l)
		l.setColumnCount(0)
		cfg.utls.insertTableColumn(l, 0, cfg.tableMCID, 40)
		cfg.utls.insertTableColumn(l, 1, cfg.tableMCInfo, 70)
		cfg.utls.insertTableColumn(l, 2, cfg.tableCID, 30)
		cfg.utls.insertTableColumn(l, 3, cfg.tableCInfo, 70)
		cfg.utls.insertTableColumn(l, 4, cfg.tableColor, 70)
		v = 5
		try:
			for i in range(1, cfg.bandSetsList[cfg.bndSetNumber][2] + 1):
				cfg.utls.insertTableColumn(l, v, cfg.tableMin + str(i), wid[v-5])
				v = v +1
				cfg.utls.insertTableColumn(l, v, cfg.tableMax + str(i), wid[v-5])
				v = v +1
		except:
			pass
		# signature ID column
		cfg.utls.insertTableColumn(l, v, cfg.tableColString, 60, "Yes")
		x = 0
		try:
			for k in list(cfg.signIDs.values()):
				cfg.utls.insertTableRow(l, x)
				cfg.utls.addTableItem(l, int(cfg.signList["MACROCLASSID_" + str(k)]), x, 0, "No")
				cfg.utls.addTableItem(l, str(cfg.signList["MACROCLASSINFO_" + str(k)]), x, 1, "No")
				cfg.utls.addTableItem(l, int(cfg.signList["CLASSID_" + str(k)]), x, 2, "No")
				cfg.utls.addTableItem(l, str(cfg.signList["CLASSINFO_" + str(k)]), x, 3, "No")
				c = cfg.signList["COLOR_" + str(k)]
				cfg.utls.addTableItem(l,  str(""), x, 4, "No", c)
				vb = 5
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					cfg.utls.addTableItem(l, str(cfg.signList["LCS_MIN_" + str(k)][b]), x, vb)
					vb = vb + 1
					cfg.utls.addTableItem(l, str(cfg.signList["LCS_MAX_" + str(k)][b]), x, vb)
					vb = vb + 1
				cfg.utls.addTableItem(l, str(cfg.signIDs["ID_" + str(k)]), x, v, "No")
				x = x + 1
		except Exception as err:
			cfg.utls.clearTable(l)
			cfg.mx.msgErr57("MC" +str(cfg.signList["MACROCLASSID_" + str(k)]) + ";C" + str(cfg.signList["CLASSID_" + str(k)]) + ";" + str(cfg.signList["CLASSINFO_" + str(k)]) )
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		cfg.utls.setColumnWidthList(l, [[0, 40]])
		try:
			vOrd = self.orderColumn
			order = l.horizontalHeader().sortIndicatorOrder()
		except:
			vOrd = 2
			order = 0
		cfg.utls.sortTableColumn(l, vOrd, order)
		l.setSortingEnabled(True)
		l.blockSignals(False)
		self.tableEdited = "Yes"
		self.orderedTable(vOrd)
		intersect = cfg.LCSignT.checkIntersections()
		cfg.LCSignT.higlightRowsByID(intersect)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signature list threshold created")
		
	# read threshold table
	def readThresholdTable(self):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		tW = cfg.ui.LCS_tableWidget
		c = tW.rowCount()
		for b in range(0, c):
			try:
				v = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 +5
				id = tW.item(b, v).text()
				vb = 5
				min = []
				max = []
				for n in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					min.append(float(tW.item(b, vb).text()))
					vb = vb + 1
					max.append(float(tW.item(b, vb).text()))
					vb = vb + 1
				cfg.signList["LCS_MIN_" + str(id)] = min
				cfg.signList["LCS_MAX_" + str(id)] = max	
				cfg.spectrPlotList["LCS_MIN_" + str(id)] = min
				cfg.spectrPlotList["LCS_MAX_" + str(id)] = max
			except:
				pass
		intersect = cfg.LCSignT.checkIntersections()
		cfg.LCSignT.higlightRowsByID(intersect)
		
	# check in thresholds are intersecting
	def checkIntersections(self):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		intersect = []
		cmb = list(cfg.itertoolsSCP.combinations(list(cfg.signIDs.values()), 2))
		for a in cmb:
			id0 = a[0]
			minA = cfg.np.array(cfg.signList["LCS_MIN_" + str(id0)])
			maxA = cfg.np.array(cfg.signList["LCS_MAX_" + str(id0)])
			id1 = a[1]
			minB = cfg.np.array(cfg.signList["LCS_MIN_" + str(id1)])
			maxB= cfg.np.array(cfg.signList["LCS_MAX_" + str(id1)])
			if cfg.macroclassCheck == "Yes":
				class0 = cfg.signList["MACROCLASSID_" + str(id0)]
				class1 = cfg.signList["MACROCLASSID_" + str(id1)]
			else:
				class0 = cfg.signList["CLASSID_" + str(id0)]
				class1 = cfg.signList["CLASSID_" + str(id1)]
			if class0 != class1:
				test = []
				tW = cfg.ui.LCS_tableWidget				
				if int((tW.columnCount() - 6)/2) != len(cfg.signList["LCS_MIN_" + str(id0)]):
					cfg.mx.msgWar26(str(cfg.bndSetNumber))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error bands")
					return "No"
				for i in range(0, len(cfg.signList["LCS_MIN_" + str(id0)])):
					if max(cfg.signList["LCS_MIN_" + str(id0)][i], cfg.signList["LCS_MIN_" + str(id1)][i]) <= min(cfg.signList["LCS_MAX_" + str(id1)][i], cfg.signList["LCS_MAX_" + str(id0)][i]):
						test.append(1)
				sum = cfg.np.array(test).sum()
				if sum == len(cfg.signList["LCS_MIN_" + str(id0)]):
					intersect.append(a)
		return intersect
		
	# ordered table
	def orderedTable(self, column):
		self.orderColumn = column
		tW = cfg.ui.LCS_tableWidget
		count = tW.rowCount()
		v = list(range(0, count))
		try:
			vx = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 5
			for x in v:
				id = tW.item(x, vx).text()
				cfg.signList["LCS_ROW_" + str(id)] = x
		except:
			pass
		
	# highlight rows by ID
	def higlightRowsByID(self, IDComb):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		tW = cfg.ui.LCS_tableWidget
		c = tW.rowCount()
		self.tableEdited = "No"
		tW.setSortingEnabled(False)
		tW.blockSignals(True)
		for b in range(0, c):
			tW.item(b, 4).setText("")
			for x in range(0, 4):
				tW.item(b, x).setBackground(cfg.QtGuiSCP.QColor(255,255,255))
		for ids in IDComb:
			try:
				row0 = cfg.signList["LCS_ROW_" + str(ids[0])]
				row1 = cfg.signList["LCS_ROW_" + str(ids[1])]
			except:
				cfg.mx.msgWar27()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error bands")
				return "No"
			for x in range(0, 4):
				tW.item(row0, x).setBackground(cfg.QtGuiSCP.QColor(255,203,69))
				tW.item(row1, x).setBackground(cfg.QtGuiSCP.QColor(255,203,69))
			text0 = tW.item(row1, 4).text()
			text1 = tW.item(row0, 4).text()
			mcId0 = str(cfg.signList["MACROCLASSID_" + str(ids[0])])
			cId0 = str(cfg.signList["CLASSID_" + str(ids[0])])
			mcId1 = str(cfg.signList["MACROCLASSID_" + str(ids[1])])
			cId1 = str(cfg.signList["CLASSID_" + str(ids[1])])
			text0 = text0 + mcId0 + "-" + cId0 + ";"
			text1 = text1 + mcId1 + "-" + cId1 + ";"
			tW.item(row0, 4).setText(text1)
			tW.item(row1, 4).setText(text0)
		tW.blockSignals(False)
		tW.setSortingEnabled(True)
		self.tableEdited = "Yes"
		
	# edited threshold table
	def editedThresholdTable(self, row, column):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		if self.tableEdited == "Yes":
			tW = cfg.ui.LCS_tableWidget
			t = tW.item(row, column).text()
			if tW.columnCount() != cfg.bandSetsList[cfg.bndSetNumber][2]:
				cfg.mx.msgWar26(str(cfg.bndSetNumber))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error bands")
				return "No"
			try:
				tr = float(t)
				v = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 +5
				id = tW.item(row, v).text()
				values = cfg.signList["VALUES_" + str(id)]
				vb = 5
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					if column == vb:
						if tr >= values[b * 2]:
							val = str(values[b * 2])
							self.tableEdited = "No"
							tW.blockSignals(True)
							cfg.utls.setTableItem(tW, row, column, val)
							tW.blockSignals(False)
							self.tableEdited = "Yes"
						break
					vb = vb + 1
					if column == vb:
						if tr <= values[b * 2]:
							val = str(values[b * 2])
							self.tableEdited = "No"
							tW.blockSignals(True)
							cfg.utls.setTableItem(tW, row, column, val)
							tW.blockSignals(False)
							self.tableEdited = "Yes"
						break
					vb = vb + 1
			except:
				v = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 +5
				id = tW.item(row, v).text()
				vb = 5
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					if column == vb:
						val = str(cfg.signList["LCS_MIN_" + str(id)][b])
						break
					vb = vb + 1
					if column == vb:
						val = str(cfg.signList["LCS_MAX_" + str(id)][b])
						break
					vb = vb + 1
				self.tableEdited = "No"
				tW.blockSignals(True)
				cfg.utls.setTableItem(tW, row, column, val)
				tW.blockSignals(False)
				self.tableEdited = "Yes"
				cfg.LCSignT.readThresholdTable()
				cfg.spSigPlot.refreshPlot()
				return 0
			cfg.LCSignT.readThresholdTable()
			#cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget, "Yes")
			cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			cfg.spSigPlot.refreshPlot()

	# set weights based on variance
	def setAllWeightsVariance(self):
		tW = cfg.ui.LCS_tableWidget
		iR = []
		for i in tW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		if len(v) == 0:
			count = tW.rowCount()
			v = list(range(0, count))
		if len(v) > 1:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to set thresholds for several signatures?"))
			if a == "Yes":
				pass
			else:
				return "No"
		cfg.uiUtls.addProgressBar()
		self.tableEdited = "No"
		tW.setSortingEnabled(False)
		tW.blockSignals(True)
		progrStep = 0
		for x in reversed(v):
			progrStep = progrStep + 100/(len(v))
			cfg.uiUtls.updateBar(int(progrStep))
			cfg.QtWidgetsSCP.qApp.processEvents()
			idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 +5
			id = tW.item(x, idCol).text()
			# values
			val = cfg.signList["VALUES_" + str(id)]
			vb = 5
			try:
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					sd = val[b * 2 +1]
					cfg.utls.addTableItem(tW, str(val[b * 2] - (sd * cfg.ui.multiplicative_threshold_doubleSpinBox_2.value())), x, vb)
					vb = vb + 1
					cfg.utls.addTableItem(tW, str(val[b * 2] + (sd * cfg.ui.multiplicative_threshold_doubleSpinBox_2.value())), x, vb)
					vb = vb + 1
			except:
				pass
		tW.blockSignals(False)
		tW.setSortingEnabled(True)
		self.tableEdited = "Yes"
		cfg.LCSignT.readThresholdTable()
		cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget, "Yes")
		#cfg.spSigPlot.refreshPlot()
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "set")
		
	# Activate pointer for pixel threshold
	def pointerActive(self):
		# connect to click
		t = cfg.LCSPixel
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(":/pointer/icons/pointer/ROI_pointer.png")
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: LCS pixel")
		
	# left click ROI pointer for pixel signature
	def pointerLeftClick(self, point):
		point = cfg.utls.checkPointImage(cfg.bandSetsList[cfg.bndSetNumber][8], point)
		if cfg.pntCheck == "Yes":
			sig = cfg.utls.calculatePixelSignature(point, cfg.bandSetsList[cfg.bndSetNumber][8], cfg.bndSetNumber,  "Pixel", "No")
			tW = cfg.ui.LCS_tableWidget
			iR = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			v = list(set(iR))
			if len(v) == 0:
				count = tW.rowCount()
				v = list(range(0, count))
			if len(v) > 1:
				# ask for confirm
				a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to set thresholds for several signatures?"))
				if a == "Yes":
					pass
				else:
					return "No"
			cfg.uiUtls.addProgressBar()
			self.tableEdited = "No"
			tW.blockSignals(True)
			tW.setSortingEnabled(False)
			progrStep = 0
			for x in reversed(v):
				progrStep = progrStep + 100/(len(v))
				cfg.uiUtls.updateBar(int(progrStep))
				idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 +5
				id = tW.item(x, idCol).text()
				# values
				val = cfg.signList["VALUES_" + str(id)]
				vb = 5
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					sigVal = sig[b]
					valMax = float(cfg.signList["LCS_MAX_" + str(id)][b])
					valMin = float(cfg.signList["LCS_MIN_" + str(id)][b])
					if sigVal >= val[b * 2]:
						if cfg.ui.LCS_include_checkBox.isChecked():
							if sigVal >= valMax:
								#max = valMax + (sigVal - valMax) * cfg.ui.multiplicative_threshold_doubleSpinBox_2.value()
								max = sigVal
							else:
								max = valMax
						else:
							max = sigVal - 1e-10
						min = valMin
					else:
						if cfg.ui.LCS_include_checkBox.isChecked():
							if sigVal <= valMin:
								#min = valMin - (valMin - sigVal) * cfg.ui.multiplicative_threshold_doubleSpinBox_2.value()
								min = sigVal
							else:
								min = valMin
						else:
							min = sigVal + 1e-10
						max = valMax
					cfg.utls.addTableItem(tW, str(min), x, vb)
					vb = vb + 1
					cfg.utls.addTableItem(tW, str(max), x, vb)
					vb = vb + 1
			tW.blockSignals(False)
			tW.setSortingEnabled(True)
			self.tableEdited = "Yes"
			cfg.LCSignT.readThresholdTable()
			cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget, "Yes")
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer")
				
	# include checkbox
	def includeCheckbox(self):
		cfg.ui.LCS_cut_checkBox.blockSignals(True)
		cfg.uisp.LCS_include_checkBox_2.blockSignals(True)
		cfg.uisp.LCS_cut_checkBox_2.blockSignals(True)
		if cfg.ui.LCS_include_checkBox.isChecked():
			cfg.ui.LCS_cut_checkBox.setCheckState(0)
			cfg.uisp.LCS_include_checkBox_2.setCheckState(2)
			cfg.uisp.LCS_cut_checkBox_2.setCheckState(0)
		else:
			cfg.ui.LCS_cut_checkBox.setCheckState(2)
			cfg.uisp.LCS_include_checkBox_2.setCheckState(0)
			cfg.uisp.LCS_cut_checkBox_2.setCheckState(2)
		cfg.ui.LCS_cut_checkBox.blockSignals(False)
		cfg.uisp.LCS_include_checkBox_2.blockSignals(False)
		cfg.uisp.LCS_cut_checkBox_2.blockSignals(False)
				
	# cut checkbox
	def cutCheckbox(self):
		cfg.ui.LCS_include_checkBox.blockSignals(True)
		cfg.uisp.LCS_include_checkBox_2.blockSignals(True)
		cfg.uisp.LCS_cut_checkBox_2.blockSignals(True)
		if cfg.ui.LCS_cut_checkBox.isChecked():
			cfg.ui.LCS_include_checkBox.setCheckState(0)
			cfg.uisp.LCS_include_checkBox_2.setCheckState(0)
			cfg.uisp.LCS_cut_checkBox_2.setCheckState(2)
		else:
			cfg.ui.LCS_include_checkBox.setCheckState(2)
			cfg.uisp.LCS_include_checkBox_2.setCheckState(2)
			cfg.uisp.LCS_cut_checkBox_2.setCheckState(0)
		cfg.ui.LCS_include_checkBox.blockSignals(False)
		cfg.uisp.LCS_include_checkBox_2.blockSignals(False)
		cfg.uisp.LCS_cut_checkBox_2.blockSignals(False)
	
	# set minimum and maximum
	def setMinimumMaximum(self):
		tW = cfg.ui.LCS_tableWidget
		iR = []
		for i in tW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		if len(v) == 0:
			count = tW.rowCount()
			v = list(range(0, count))
		if len(v) > 1:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to set thresholds for several signatures?"))
			if a == "Yes":
				pass
			else:
				return "No"
		cfg.uiUtls.addProgressBar()
		self.tableEdited = "No"
		tW.setSortingEnabled(False)
		tW.blockSignals(True)
		progrStep = 0
		for x in reversed(v):
			progrStep = progrStep + 100/(len(v))
			cfg.uiUtls.updateBar(int(progrStep))
			idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 +5
			id = tW.item(x, idCol).text()
			vb = 5
			for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
				min = float(cfg.signList["MIN_VALUE_" + str(id)][b])
				max = float(cfg.signList["MAX_VALUE_" + str(id)][b])
				cfg.utls.addTableItem(tW, str(min), x, vb)
				vb = vb + 1
				cfg.utls.addTableItem(tW, str(max), x, vb)
				vb = vb + 1
		tW.blockSignals(False)
		tW.setSortingEnabled(True)
		self.tableEdited = "Yes"
		cfg.LCSignT.readThresholdTable()
		cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget, "Yes")
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "set")

	def ROIThreshold(self):
		if cfg.lstROI is not None:
			tW = cfg.ui.LCS_tableWidget
			iR = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			v = list(set(iR))
			if len(v) == 0:
				count = tW.rowCount()
				v = list(range(0, count))
			if len(v) > 1:
				# ask for confirm
				a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to set thresholds for several signatures?"))
				if a == "Yes":
					pass
				else:
					return "No"
			cfg.uiUtls.addProgressBar()
			self.tableEdited = "No"
			tW.setSortingEnabled(False)
			tW.blockSignals(True)
			progrStep = 0
			# calculate ROI
			fID = cfg.utls.getLastFeatureID(cfg.lstROI)
			cfg.utls.calculateSignature(cfg.lstROI, cfg.bandSetsList[cfg.bndSetNumber][8], [fID],  0, cfg.tmpROINm, 0, 0, 0, 20, "MinMax", "MinMax", None)
			progrStep = 20
			for x in reversed(v):
				progrStep = progrStep +80/(len(v))
				cfg.uiUtls.updateBar(int(progrStep))
				idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 +5
				id = tW.item(x, idCol).text()
				# values
				val = cfg.signList["VALUES_" + str(id)]
				vb = 5
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					stats = cfg.tblOut["BAND_" + str(b + 1)]
					min = stats[0]
					max = stats[1]						
					if cfg.ui.LCS_include_checkBox.isChecked():
						if cfg.np.around(float(tW.item(x, vb).text()), 11) > cfg.np.around(min, 11):
							cfg.utls.addTableItem(tW, str(min), x, vb)
					else:
						if cfg.np.around(float(tW.item(x, vb).text()), 11) < cfg.np.around(min, 11):
							if min >= val[b * 2]:
								cfg.utls.addTableItem(tW, str(min + 1e-10), x, vb + 1)
							else:
								cfg.utls.addTableItem(tW, str(min + 1e-10), x, vb)
					vb = vb + 1
					if cfg.ui.LCS_include_checkBox.isChecked():
						if cfg.np.around(float(tW.item(x, vb).text()), 11) < cfg.np.around(max, 11):
							cfg.utls.addTableItem(tW, str(max), x, vb)
					else:
						if cfg.np.around(float(tW.item(x, vb).text()), 11) > cfg.np.around(max, 11):
							if max <= val[b * 2]:
								cfg.utls.addTableItem(tW, str(max - 1e-10), x, vb - 1)
							else:
								cfg.utls.addTableItem(tW, str(max - 1e-10), x, vb)
					vb = vb + 1
			tW.blockSignals(False)
			tW.setSortingEnabled(True)
			self.tableEdited = "Yes"
			cfg.LCSignT.readThresholdTable()
			cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget, "Yes")
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "set")
	
	# add signatures to spectral plot
	def addSignatureToSpectralPlot(self):
		tW = cfg.ui.LCS_tableWidget
		r = []
		check = "Yes"
		for i in tW.selectedIndexes():
			r.append(i.row())
		v = list(set(r))
		if len(v) > 0:
			progresStep = 100 / len(v)
			progress = 0
			cfg.uiUtls.addProgressBar()
			for x in v:
				progress = progress * progresStep
				idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 +5
				id = tW.item(x, idCol).text()
				if id in list(cfg.signIDs.values()):
					if id not in list(cfg.signPlotIDs.values()):
						cfg.SCPD.sigListToPlot(id)
				else:
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
					cfg.utls.calculateSignature(cfg.shpLay, cfg.bandSetsList[cfg.bndSetNumber][8], rId, cfg.ROI_MC_ID[id], cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.ROI_C_Info[id], progress, progresStep, "No", "No", id)
					cfg.SCPD.sigListToPlot(id)
					check = "No"
			cfg.uiUtls.removeProgressBar()
			if check == "No":
				cfg.SCPD.ROIListTable(cfg.shpLay, cfg.uidc.signature_list_tableWidget)
			cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			cfg.utls.spectralPlotTab()
		else:
			cfg.utls.spectralPlotTab()
			