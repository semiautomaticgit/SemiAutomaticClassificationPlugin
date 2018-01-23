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

class RGBListTab:

	def __init__(self):
		self.tableEdited = "Yes"
	
	# Create RGB list table
	def RGBListTable(self, list):
		l = cfg.ui.RGB_tableWidget
		self.tableEdited = "No"
		l.blockSignals(True)
		cfg.utls.clearTable(l)
		x = 0
		for i in list:
			if i != "-":
				cfg.utls.insertTableRow(l, x)
				cfg.utls.addTableItem(l, i, x, 0)
				x = x + 1
		l.blockSignals(False)
		self.tableEdited = "Yes"

	# edited table
	def editedTable(self, row, column):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		if self.tableEdited == "Yes":
			tW = cfg.ui.RGB_tableWidget
			t = tW.item(row, column).text()
			try:
				check = cfg.utls.createRGBColorComposite(t)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				check = "No"
			if check == "Yes":
				listA = self.readRGBListTable()
				cfg.RGBList = listA
				cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
				cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
				id = cfg.rgb_combo.findText(t)
				cfg.rgb_combo.setCurrentIndex(id)
			else:
				cfg.RGBLT.RGBListTable(cfg.RGBList)
					
	# read RGB List table
	def readRGBListTable(self):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		tW = cfg.ui.RGB_tableWidget
		c = tW.rowCount()
		list = []
		list.append("-")
		for b in range(0, c):
			t = tW.item(b, 0).text()
			list.append(t)
		return list
		
	# add RGB
	def addRGBToTable(self):
		tW = cfg.ui.RGB_tableWidget
		# add item to table
		c = tW.rowCount()
		# add list items to table
		tW.setRowCount(c + 1)
		cfg.utls.addTableItem(tW, "0-0-0", c, 0)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "added RGB " + str(c + 1))

	# remove RGB
	def removeRGBFromTable(self):
		cfg.utls.removeRowsFromTable(cfg.ui.RGB_tableWidget)
		listA = self.readRGBListTable()
		cfg.RGBList = listA
		cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
		cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
		
	# sort RGB
	def sortRGBName(self):
		listA = cfg.RGBList
		sortRGB = sorted(listA)
		cfg.RGBList = sortRGB
		cfg.RGBLT.RGBListTable(cfg.RGBList)
		cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
		cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
			
	# clear the band set
	def clearTableAction(self):
		self.clearTable()
		
	# clear Table
	def clearTable(self, question = "Yes"):
		if question == "Yes":
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset RGB list"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the RGB list?"))
		else:
			a = "Yes"
		if a == "Yes":
			tW = cfg.ui.RGB_tableWidget
			cfg.utls.clearTable(tW)
			listA = self.readRGBListTable()
			cfg.RGBList = listA
			cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
			cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
		
	# move up selected RGB
	def moveUpRGB(self):
		tW = cfg.ui.RGB_tableWidget
		self.tableEdited = "No"
		tW.blockSignals(True)
		c = tW.rowCount()
		s = tW.selectedItems()
		# create list for new selection after move
		ns  = []
		for i in range (0, len(s)):
			ns.append(s[i].row() - 1)
		try:
			for b in range(0, c):
				if tW.item(b, 0).isSelected():
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
		self.tableEdited = "Yes"
		tW.blockSignals(False)
		listA = self.readRGBListTable()
		cfg.RGBList = listA
		cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
		cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " RGB moved")
				
	# move down selected RGB
	def moveDownRGB(self):
		tW = cfg.ui.RGB_tableWidget
		self.tableEdited = "No"
		tW.blockSignals(True)
		c = tW.rowCount()
		s = tW.selectedItems()
		# create list for new selection after move
		ns  = []
		for i in range (0, len(s)):
			ns.append(s[i].row() + 1)
		try:
			for b in reversed(list(range(0, c))):
				if tW.item(b, 0).isSelected():
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
		self.tableEdited = "Yes"
		tW.blockSignals(False)
		listA = self.readRGBListTable()
		cfg.RGBList = listA
		cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
		cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " RGB moved")
				
	# all RGB List 
	def allRGBListAction(self):
		self.allRGBList()

	# all RGB List 
	def allRGBList(self, question = "Yes", bandSetNumber = None):
		if question == "Yes":
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "RGB list"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Calculate all the RGB combinations?"))
		else:
			a = "Yes"
		if a == "Yes":
			if bandSetNumber is None:
				bandSetNumber = cfg.bndSetNumber
			if bandSetNumber >= len(cfg.bandSetsList):
				cfg.mx.msgWar25(bandSetNumber + 1)
				return "No"
			perm = list(cfg.itertoolsSCP.permutations(list(range(1, len(cfg.bandSetsList[bandSetNumber][3])+1)), 3))
			tW = cfg.ui.RGB_tableWidget
			self.tableEdited = "No"
			tW.blockSignals(True)
			cfg.utls.clearTable(tW)
			for x in perm:
				c = tW.rowCount()
				# add list items to table
				tW.setRowCount(c + 1)
				cfg.utls.addTableItem(tW, str(x[0]) + "-" + str(x[1]) + "-" + str(x[2]), c, 0)
			self.tableEdited = "Yes"
			tW.blockSignals(False)
			listA = self.readRGBListTable()
			cfg.RGBList = listA
			cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
			cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		
# export RGB list to file
	def exportRGBList(self):
		file = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save the RGB list to file"), "", "*.csv", "csv")
		if file is not False:
			if file.lower().endswith(".csv"):
				pass
			else:
				file = file + ".csv"
			try:
				f = open(file, 'w')
				f.write("")
				f.close()
				f = open(file, 'a')
				for i in cfg.RGBList:
					if i != "-":
						txt = i + "\n"
						f.write(txt)
				f.close()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " list exported")
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# import RGB from file
	def importRGB(self):
		file = cfg.utls.getOpenFileName(None , "Select a RGB list file", "", "CSV (*.csv)")
		try:
			f = open(file)
			if cfg.osSCP.path.isfile(file):
				file = f.readlines()
				tW = cfg.ui.RGB_tableWidget
				# RGB list
				for b in range(1, len(file)):
					# add item to table
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, file[b].strip(), c, 0)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " list imported")
		except Exception as err:
			cfg.mx.msgErr19()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		