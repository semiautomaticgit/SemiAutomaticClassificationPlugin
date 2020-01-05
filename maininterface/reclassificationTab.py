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

class ReclassificationTab:

	def __init__(self):
		pass
					
	# reclassify
	def reclassifyAction(self):
		self.reclassify()
		
	# reclassify
	def reclassify(self, batch = "No", rasterInput = None, rasterOutput = None, valueString = None):
		if batch == "No":
			self.clssfctnNm = cfg.ui.reclassification_name_combo.currentText()
			i = cfg.utls.selectLayerbyName(self.clssfctnNm, "Yes")
			try:
				classificationPath = cfg.utls.layerSource(i)
			except Exception as err:
				cfg.mx.msg4()
				cfg.utls.refreshClassificationLayer()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			list = self.getValuesTable()
			tW = cfg.ui.reclass_values_tableWidget
			c = tW.rowCount()
		else:
			if cfg.osSCP.path.isfile(rasterInput):
				classificationPath = rasterInput
			else:
				return "No"
			list = []
			values = valueString.split(",")
			for v in values:
				val = v.split("_")
				list.append([val[0], val[1]])
			c = 1
		if c > 0:
			if batch == "No":
				out = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save raster output"), "", "*.tif", "tif")
			else:
				out = rasterOutput
			if out is not False:
				if out.lower().endswith(".tif"):
					pass
				else:
					out = out + ".tif"
				if batch == "No":
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
				cfg.uiUtls.updateBar(10)
				# date time for temp name
				dT = cfg.utls.getTime()
				tPMN2 = dT + cfg.calcRasterNm + ".tif"
				tPMD2 = cfg.tmpDir + "/" + tPMN2
				# open input with GDAL
				rD = cfg.gdalSCP.Open(classificationPath, cfg.gdalSCP.GA_ReadOnly)
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# output rasters
				oM = []
				oM.append(tPMD2)
				reclassList = self.createReclassificationStringFromList(list)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
				o = cfg.utls.processRaster(rD, bL, None, cfg.utls.reclassifyRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", reclassList, cfg.variableName)
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				if cfg.rasterCompression != "No":
					try:
						cfg.utls.GDALCopyRaster(tPMD2, out, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						cfg.osSCP.remove(tPMD2)
					except Exception as err:
						cfg.shutilSCP.copy(tPMD2, out)
						cfg.osSCP.remove(tPMD2)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					cfg.shutilSCP.copy(tPMD2, out)
					cfg.osSCP.remove(tPMD2)
				if cfg.osSCP.path.isfile(out):
					r =cfg.utls.addRasterLayer(out, cfg.osSCP.path.basename(out))
				else:
					if batch == "No":
						cfg.utls.finishSound()
						cfg.uiUtls.removeProgressBar()
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
					return "No"
				# create symbol
				if cfg.ui.apply_symbology_checkBox.isChecked() is True:	
					if str(cfg.ui.class_macroclass_comboBox_2.currentText()) == cfg.fldMacroID_class_def:
						mc = "Yes"
						sL = cfg.SCPD.createMCIDList()
					else:
						mc = "No"
						sL = cfg.SCPD.getSignatureList()
					cfg.utls.rasterSymbol(r, sL, mc)
				if batch == "No":
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " reclassification ended")

	def calculateUniqueValues(self):
		self.clssfctnNm = cfg.ui.reclassification_name_combo.currentText()
		i = cfg.utls.selectLayerbyName(self.clssfctnNm, "Yes")
		try:
			classificationPath = cfg.utls.layerSource(i)
		except Exception as err:
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		try:
			clssRstrSrc = str(classificationPath)
			ck = "Yes"
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			ck = "No"
		if ck == "No":
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
		else:
			cfg.uiUtls.addProgressBar()
			cfg.uiUtls.updateBar(10)
			refRstrDt = cfg.gdalSCP.Open(clssRstrSrc, cfg.gdalSCP.GA_ReadOnly)
			# combination finder
			# band list
			bLR = cfg.utls.readAllBandsFromRaster(refRstrDt)
			cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
			cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
			o = cfg.utls.processRaster(refRstrDt, bLR, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
			cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
			refRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)	
			cfg.uiUtls.updateBar(80)
			if cfg.ui.CID_MCID_code_checkBox.isChecked() is True:
				uniq = cfg.utls.calculateUnique_CID_MCID()
				if uniq == "No":
					uniq = self.createValueList(cfg.rasterBandUniqueVal)
			else:
				uniq = self.createValueList(cfg.rasterBandUniqueVal)
			self.addValuesToTable(uniq)
			for b in range(0, len(bLR)):
				bLR[b] = None
			refRstrDt = None
			cfg.uiUtls.updateBar(100)
			cfg.uiUtls.removeProgressBar()
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " values calculated")
			
	def createValueList(self, list):
		unique = []
		for i in list:
			unique.append([float(i),float(i)])
		l = sorted(unique, key=lambda unique: (unique[0]))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " unique" + str(l))
		return l
		
	def addValuesToTable(self, valuesList):
		cfg.ReclassTabEdited = "No"
		tW = cfg.ui.reclass_values_tableWidget
		cfg.utls.clearTable(tW)
		c = tW.rowCount()
		for i in valuesList:
			tW.setRowCount(c + 1)
			cfg.utls.addTableItem(tW, str(i[0]), c, 0)
			cfg.utls.addTableItem(tW, str(i[1]), c, 1)
			c = c + 1
		cfg.ReclassTabEdited = "Yes"
		
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
				old = float(i[0])
				cond = cfg.variableName + " == " + str(old)
			except:
				cond = str(i[0])
			reclassList.append([cond, float(i[1])])
		return reclassList
			
	def addRowToTable(self):
		cfg.ReclassTabEdited = "No"
		tW = cfg.ui.reclass_values_tableWidget
		# add item to table
		c = tW.rowCount()
		tW.setRowCount(c + 1)
		cfg.utls.addTableItem(tW, "0", c, 0)
		cfg.utls.addTableItem(tW, "0", c, 1)
		cfg.ReclassTabEdited = "Yes"

	def removePointFromTable(self):
		cfg.utls.removeRowsFromTable(cfg.ui.reclass_values_tableWidget)
		
	def editedCell(self, row, column):
		if cfg.ReclassTabEdited == "Yes":
			tW = cfg.ui.reclass_values_tableWidget
			val = tW.item(row, column).text()
			if column == 1:
				try:	
					val = float(val)
				except:
					cfg.ReclassTabEdited = "No"
					cfg.utls.setTableItem(tW, row, column, "0")
					cfg.ReclassTabEdited = "Yes"
			elif column == 0:	
				c = val.replace(cfg.variableName, "rasterSCPArrayfunctionBand")
				rasterSCPArrayfunctionBand = cfg.np.arange(9).reshape(3, 3)
				try:
					eval("cfg.np.where(" + c + ", 1, rasterSCPArrayfunctionBand)")
				except:
					cfg.ReclassTabEdited = "No"
					cfg.utls.setTableItem(tW, row, column, "0")
					cfg.ReclassTabEdited = "Yes"
					cfg.mx.msgWar16()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "edited cell" + str(row) + ";" + str(column))