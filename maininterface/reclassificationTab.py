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

class ReclassificationTab:

	def __init__(self):
		pass
					
	# reclassify
	def reclassifyAction(self):
		self.reclassify()
		
	# reclassify
	def reclassify(self, batch = 'No', rasterInput = None, rasterOutput = None, valueString = None):
		if batch == 'No':
			self.clssfctnNm = cfg.ui.reclassification_name_combo.currentText()
			i = cfg.utls.selectLayerbyName(self.clssfctnNm, 'Yes')
			try:
				classificationPath = cfg.utls.layerSource(i)
			except Exception as err:
				cfg.mx.msg4()
				cfg.utls.refreshClassificationLayer()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
			list = self.getValuesTable()
			tW = cfg.ui.reclass_values_tableWidget
			c = tW.rowCount()
		else:
			if cfg.osSCP.path.isfile(rasterInput):
				classificationPath = rasterInput
			else:
				return 'No'
			list = []
			values = valueString.split(',')
			for v in values:
				val = v.split('_')
				list.append([val[0], val[1]])
			c = 1
		if c > 0:
			if batch == 'No':
				out = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save raster output'), '', 'TIF file (*.tif);;VRT file (*.vrt)')
			else:
				out = rasterOutput
			# virtual raster
			vrtR = 'No'
			if out is not False:
				if out.lower().endswith('.vrt'):
					vrtR = 'Yes'
				elif out.lower().endswith('.tif'):
					pass
				else:
					out = out + '.tif'
				if batch == 'No':
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
				cfg.uiUtls.updateBar(10)
				cfg.utls.makeDirectory(cfg.osSCP.path.dirname(out))
				reclassList = self.createReclassificationStringFromList(list)
				o = cfg.utls.multiProcessRaster(rasterPath = classificationPath, functionBand = 'No', functionRaster = cfg.utls.reclassifyRaster, outputRasterList = [out], nodataValue = cfg.NoDataVal,  functionBandArgument = reclassList, functionVariable = cfg.variableName, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reclassify'), virtualRaster = vrtR, compress = cfg.rasterCompression)
				if cfg.osSCP.path.isfile(out):
					r =cfg.utls.addRasterLayer(out)
				else:
					if batch == 'No':
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						cfg.uiUtls.removeProgressBar()
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
					return 'No'
				# create symbol
				if cfg.ui.apply_symbology_checkBox.isChecked() is True:	
					if str(cfg.ui.class_macroclass_comboBox_2.currentText()) == cfg.fldMacroID_class_def:
						mc = 'Yes'
						sL = cfg.SCPD.createMCIDList()
					else:
						mc = 'No'
						sL = cfg.classTab.getSignatureList()
					cfg.utls.rasterSymbol(r, sL, mc)
				if batch == 'No':
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.uiUtls.removeProgressBar()
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' reclassification ended')

	def calculateUniqueValues(self):
		self.clssfctnNm = cfg.ui.reclassification_name_combo.currentText()
		i = cfg.utls.selectLayerbyName(self.clssfctnNm, 'Yes')
		try:
			classificationPath = cfg.utls.layerSource(i)
		except Exception as err:
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
		try:
			clssRstrSrc = str(classificationPath)
			ck = 'Yes'
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			ck = 'No'
		if ck == 'No':
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
		else:
			cfg.uiUtls.addProgressBar()
			cfg.uiUtls.updateBar(10)
			cfg.parallelArrayDict = {}
			o = cfg.utls.multiProcessRaster(rasterPath = clssRstrSrc, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = cfg.NoDataVal, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'), deleteArray = 'No')
			# calculate unique values
			values = cfg.np.array([])
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						values = cfg.np.append(values, ar[0, ::])
				except:
					pass
			values = cfg.np.unique(values).tolist()
			cfg.uiUtls.updateBar(80)
			if cfg.ui.CID_MCID_code_checkBox.isChecked() is True:
				uniq = cfg.utls.calculateUnique_CID_MCID()
				if uniq == 'No':
					uniq = self.createValueList(values)
			else:
				uniq = self.createValueList(values)
			self.addValuesToTable(uniq)
			cfg.uiUtls.updateBar(100)
			cfg.uiUtls.removeProgressBar()
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' values calculated')
			
	def incrementalNewValues(self):
		self.clssfctnNm = cfg.ui.reclassification_name_combo.currentText()
		i = cfg.utls.selectLayerbyName(self.clssfctnNm, 'Yes')
		try:
			classificationPath = cfg.utls.layerSource(i)
		except Exception as err:
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
		try:
			clssRstrSrc = str(classificationPath)
			ck = 'Yes'
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			ck = 'No'
		if ck == 'No':
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
		else:
			cfg.uiUtls.addProgressBar()
			cfg.uiUtls.updateBar(10)
			cfg.parallelArrayDict = {}
			o = cfg.utls.multiProcessRaster(rasterPath = clssRstrSrc, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = cfg.NoDataVal, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values'), deleteArray = 'No')
			# calculate unique values
			values = cfg.np.array([])
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						values = cfg.np.append(values, ar[0, ::])
				except:
					pass
			values = cfg.np.unique(values).tolist()
			cfg.uiUtls.updateBar(80)
			uniq = self.createValueList(values, 'Yes')
			self.addValuesToTable(uniq)
			cfg.uiUtls.updateBar(100)
			cfg.uiUtls.removeProgressBar()
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' values calculated')
			
	def createValueList(self, list, incremental = 'No'):
		unique = []
		if incremental == 'No':
			for i in sorted(list):
				g = str(i).split('.0')
				try:
					t = g[1]
					p = i
				except:
					p = g[0]
				unique.append([p, p])
		else:
			v = 1
			for i in sorted(list):
				g = str(i).split('.0')
				try:
					t = g[1]
					if len(t) > 0:
						p = i
					else:
						p = g[0]
				except:
					p = g[0]
				unique.append([p,str(v)])
				v = v + 1
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' unique' + str(unique))
		return unique
		
	def addValuesToTable(self, valuesList):
		cfg.ReclassTabEdited = 'No'
		tW = cfg.ui.reclass_values_tableWidget
		cfg.utls.clearTable(tW)
		c = tW.rowCount()
		for i in valuesList:
			tW.setRowCount(c + 1)
			cfg.utls.addTableItem(tW, str(i[0]), c, 0)
			cfg.utls.addTableItem(tW, str(i[1]), c, 1)
			c = c + 1
		cfg.ReclassTabEdited = 'Yes'
		
	def getValuesTable(self):
		tW = cfg.ui.reclass_values_tableWidget
		c = tW.rowCount()
		list = []
		for row in range(0, c):
			old = tW.item(row, 0).text()
			new = tW.item(row, 1).text()
			list.append([old, new])
		return list
			
	def createReclassificationStringFromList(self, list):
		reclassList = []
		for i in list:
			try:
				cond = float(i[0])
			except:
				cond = str(i[0])
			reclassList.append([cond, float(i[1])])
		return reclassList
			
	def addRowToTable(self):
		cfg.ReclassTabEdited = 'No'
		tW = cfg.ui.reclass_values_tableWidget
		# add item to table
		c = tW.rowCount()
		tW.setRowCount(c + 1)
		cfg.utls.addTableItem(tW, '0', c, 0)
		cfg.utls.addTableItem(tW, '0', c, 1)
		cfg.ReclassTabEdited = 'Yes'

	def removePointFromTable(self):
		cfg.utls.removeRowsFromTable(cfg.ui.reclass_values_tableWidget)
		
	def editedCell(self, row, column):
		if cfg.ReclassTabEdited == 'Yes':
			tW = cfg.ui.reclass_values_tableWidget
			val = tW.item(row, column).text()
			if column == 1:
				try:	
					val = float(val)
				except:
					cfg.ReclassTabEdited = 'No'
					cfg.utls.setTableItem(tW, row, column, '0')
					cfg.ReclassTabEdited = 'Yes'
			elif column == 0:	
				c = val.replace(cfg.variableName, 'rasterSCPArrayfunctionBand')
				rasterSCPArrayfunctionBand = cfg.np.arange(9).reshape(3, 3)
				try:
					eval('cfg.np.where(' + c + ', 1, rasterSCPArrayfunctionBand)')
				except:
					cfg.ReclassTabEdited = 'No'
					cfg.utls.setTableItem(tW, row, column, '0')
					cfg.ReclassTabEdited = 'Yes'
					cfg.mx.msgWar16()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'edited cell' + str(row) + ';' + str(column))
			
	# import reclass from file
	def importReclass(self):
		file = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a reclassification file'), '', 'CSV (*.csv)')
		if len(file) > 0:
			self.importReclassFile(file)
			
	# import reclass
	def importReclassFile(self, file):
		try:
			f = open(file)
			if cfg.osSCP.path.isfile(file):
				file = f.readlines()
				if '\t' in file[0]:
					sep = '\t'
				else:
					sep = ','
				tW = cfg.ui.reclass_values_tableWidget
				for b in range(0, len(file)):
					# rule list
					p = file[b].strip().split(sep)
					oldV = 0
					newV = 0
					try:
						oldV = p[0]
						newV = p[1]
					except:
						pass
					# add item to table
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, oldV, c, 0)
					cfg.utls.addTableItem(tW, newV, c, 1)
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rules imported')
		except Exception as err:
			cfg.mx.msgErr19()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			
	# export reclass list to file
	def exportReclass(self):
		listFile = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save the reclassification list to file'), '', '*.csv', 'csv')
		try:
			if listFile.lower().endswith('.csv'):
				pass
			else:
				listFile = listFile + '.csv'
			tW = cfg.ui.reclass_values_tableWidget
			c = tW.rowCount()
			f = open(listFile, 'w')
			txt = ''
			for i in range(0, c):
				sep = ','
				X = tW.item(i,0).text()
				Y = tW.item(i,1).text()
				try:
					oldV = tW.item(i,0).text()
					newV = tW.item(i,1).text()
				except:
					pass
				txt = txt + oldV + sep + newV + '\n'
			f.write(txt)
			f.close()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' point list exported')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			