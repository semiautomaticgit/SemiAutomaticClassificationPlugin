# -*- coding: utf-8 -*-
'''
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright		: (C) 2012-2021 by Luca Congedo
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

'''



cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

class BandSetListTab:

	def __init__(self):
		self.tableEdited = 'Yes'
	
	# Create list table
	def BandSetListTable(self):
		tW = cfg.ui.band_set_list_tableWidget
		self.tableEdited = 'No'
		tW.blockSignals(True)
		cfg.utls.clearTable(tW)
		for i in range(0, len(cfg.bandSetsList)):
			cfg.utls.insertTableRow(tW, i)
			if i == cfg.bndSetNumber:
				co = cfg.QtGuiSCP.QColor(0, 128, 0)
				bo = 'Yes'
			else:
				co = None
				bo = None
			cfg.utls.addTableItem(tW, i + 1, i, 0, foreground = co, bold = bo)
			bands = str(cfg.bandSetsList[i][3]).replace("[", "").replace("]", "").replace("'", "")
			cfg.utls.addTableItem(tW, bands, i, 1, foreground = co, tooltip = bands, bold = bo)
		tW.blockSignals(False)
		self.tableEdited = 'Yes'
		
	# add band set
	def addBandSetToTable(self):
		b = cfg.bst.addBandSetTab()

	# display RGB band set
	def displayRGB(self):
		cfg.uiUtls.addProgressBar()
		cfg.QtWidgetsSCP.qApp.processEvents()
		rgb = cfg.rgb_combo.currentText()
		tW = cfg.ui.band_set_list_tableWidget
		# list of items
		iR  = []
		for i in tW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		tmpVrt = cfg.tmpVrtDict[cfg.bndSetNumber]
		# remove items
		c = 0
		for i in v:
			cfg.uiUtls.updateBar(int(c * 100 / (len(v))), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " RGB band set " + str(i+1)))
			c= c + 1
			try:
				b = cfg.utls.createRGBColorComposite(rgb, i)
			except:
				try:
					b = cfg.utls.createRGBColorComposite("3,2,1", i)
				except:
					pass
		cfg.tmpVrtDict[cfg.bndSetNumber] = tmpVrt
		cfg.uiUtls.removeProgressBar()				
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " row removed")

	# remove band set
	def removeBandSetFromTable(self):
		# ask for confirm
		a = cfg.utls.questionBox("Remove rows", "Are you sure you want to remove highlighted rows from the table?")
		if a == 'Yes':
			cfg.uiUtls.addProgressBar()
			tW = cfg.ui.band_set_list_tableWidget
			cfg.ui.Band_set_tabWidget.blockSignals(True)
			c = tW.rowCount()
			# list of item to remove
			iR  = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			v = list(sorted(set(iR)))
			a = 0
			# if remove all band sets
			if c == len(v):
				a = 1
				cfg.bst.clearBandSet('No', 'No', 0)
			# remove items
			for i in reversed(list(range(a, len(v)))):
				cfg.bst.removeBandSetTab(v[i])
				cfg.uiUtls.updateBar( 100 - (i) * 100 / (len(v)), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', ' removing'))
			cfg.bndSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
			cfg.ui.Band_set_tabWidget.blockSignals(False)
			cfg.bst.tabChanged()
			cfg.uiUtls.removeProgressBar()				
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " row removed")
		
	# move up selected
	def moveUpBandset(self):
		tW = cfg.ui.band_set_list_tableWidget
		t = cfg.ui.Band_set_tabWidget
		self.tableEdited = 'No'
		tW.blockSignals(True)
		s = tW.selectedItems()
		# create list for new selection after move
		ns  = []
		for x in range(0, len(s)):
			ns.append(s[x].row())
		v = list(set(ns))
		if 0 not in v:
			for i in range(0, len(v)):
				t.tabBar().moveTab(v[i], v[i] - 1)
			cfg.bst.tabChanged()
			try:
				for i in range(0, len(v)):
					tW.selectRow(v[i] - 1)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
		self.tableEdited = 'Yes'
		tW.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Bands moved")
				
	# move down selected
	def moveDownBandset(self):
		tW = cfg.ui.band_set_list_tableWidget
		t = cfg.ui.Band_set_tabWidget
		self.tableEdited = 'No'
		tW.blockSignals(True)
		c = tW.rowCount()
		s = tW.selectedItems()
		# create list for new selection after move
		ns  = []
		for x in range(0, len(s)):
			ns.append(s[x].row())
		v = list(set(ns))
		if c - 1 not in v:
			for i in reversed(list(range(0, len(v)))):
				t.tabBar().moveTab(v[i], v[i] + 1)
			cfg.bst.tabChanged()
			try:
				for i in range(0, len(v)):
					tW.selectRow(v[i] + 1)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				tW.clearSelection()
		self.tableEdited = 'Yes'
		tW.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Bands moved")
					
	# double click define active band set
	def doubleClick(self, index):
		cfg.ui.Band_set_tabWidget.setCurrentIndex(index.row())
					
# export list to file
	def exportList(self):
		sL = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save the Band set list to file"), "", "*.scpb", "scpb")
		if sL is not False:
			cfg.uiUtls.addProgressBar()
			try:
				dT = cfg.utls.getTime()
				unzipDir = cfg.tmpDir + "/" + dT
				oDir = cfg.utls.makeDirectory(unzipDir)
				# export band sets
				for i in range(0, len(cfg.bandSetsList)):
					dT = cfg.utls.getTime()
					outFile = unzipDir + "/" + cfg.bandSetName + dT + ".xml"
					cfg.bst.exportBandSetFile(outFile, i)
					cfg.uiUtls.updateBar((i) * 100 / (len(cfg.bandSetsList)), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " exporting"))
				# create zip file
				cfg.utls.zipDirectoryInFile(sL, unzipDir)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " list exported")
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msg14()
			cfg.uiUtls.removeProgressBar()
			cfg.utls.finishSound()
				
	# import list from file
	def importList(self):
		file = cfg.utls.getOpenFileName(None , "Select a Band set list file", "", "SCPB (*.scpb)")
		if len(file) > 0:
			dT = cfg.utls.getTime()
			unzipDir = cfg.tmpDir + "/" + dT
			oDir = cfg.utls.makeDirectory(unzipDir)
			# unzip to temp dir
			try:
				cfg.uiUtls.addProgressBar()
				with cfg.zipfileSCP.ZipFile(file) as zOpen:
					c = len(zOpen.namelist())
					i = 0
					for flName in sorted(zOpen.namelist()):
						if cfg.actionCheck == 'Yes':
							i = i + 1
							cfg.uiUtls.updateBar(i * 100 / c, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " importing"))
							zipF = zOpen.open(flName)
							fileName = cfg.utls.fileName(flName)
							if fileName.endswith(".xml"):
								try:
									zipO = open(unzipDir + "/" + fileName, "wb")
									with zipF, zipO:
										cfg.shutilSCP.copyfileobj(zipF, zipO)
									zipO.close()
									b = cfg.bst.addBandSetTab('No')
									cfg.bst.importBandSetFile(unzipDir + "/" + fileName, b)
								except Exception as err:
									# logger
									cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			except Exception as err:
				cfg.mx.msgErr19()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.bst.readBandSet('Yes')
			cfg.uiUtls.removeProgressBar()
			cfg.utls.finishSound()
	
	# perform bands filter
	def filterTable(self):
		l = cfg.ui.band_set_list_tableWidget
		text = cfg.ui.band_set_filter_lineEdit.text()
		items = l.findItems(text, cfg.QtSCP.MatchContains)
		c = l.rowCount()
		list = []
		for item in items:
			list.append( item.row())
		l.blockSignals(True)
		for i in range (0, c):
			l.setRowHidden(i, False)
			if i not in list:
				l.setRowHidden(i, True)
		l.blockSignals(False)		