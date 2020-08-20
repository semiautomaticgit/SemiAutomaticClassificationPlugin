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

class MODISTab:

	def __init__(self):
		pass
		
	# MODIS input
	def inputMODIS(self):
		i = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a HDF file"), "", "file .hdf (*.hdf)")
		cfg.ui.label_217.setText(str(i))
		self.populateTable(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(i))
	
	# MODIS conversion
	def MODIS(self, inputFile, outputDirectory, batch = "No", bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return "No"
		if batch == "No":
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)		
		cfg.uiUtls.updateBar(5)	
		l = cfg.ui.MODIS_tableWidget
		# input
		if inputFile.lower().endswith(".hdf") and cfg.osSCP.path.isfile(inputFile):
			fileNm = cfg.osSCP.path.basename(inputFile)[:-4]
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputFile, cfg.gdalSCP.GA_ReadOnly)
			rDSub = rD.GetSubDatasets()
		out = outputDirectory
		oDir = cfg.utls.makeDirectory(out)
		# name prefix
		pre = "RT_"
		# input bands
		c = l.rowCount()
		# date time for temp name
		dT = cfg.utls.getTime()
		# temp raster
		tempRasterList = []
		# output raster list
		outputRasterList = []
		# band list
		bandSetList = []
		bandSetNameList = []
		bandNumberList = []
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				iBand = l.item(i,0).text()
				iBandN = iBand[-2:]
				#  MODIS bands
				for sb in rDSub:
					inputRaster = None
					nm = sb[0]
					bandName = fileNm + "_" + iBandN
					inputRaster = nm
					try:
						bnI = inputRaster.split("b")[1][0:2]
						if inputRaster is not None and "sur_refl" in str(inputRaster) and  iBandN == bnI:
							oNm = pre + iBand + ".tif"
							outputRaster = out + "/" + oNm
							outputRasterList.append(outputRaster)
							tempRaster = cfg.tmpDir + "/" + dT + iBand + ".tif"
							tempRasterList.append(tempRaster)
							try:
								coeff = float(l.item(i,1).text())
							except:
								coeff = ""
							# conversion
							ck = self.MODIS_reflectance(bandName[-2:], coeff, inputRaster, tempRaster)
							if ck != "No":
								# band list
								bandSetList.append(int(bandName[-2:]))
								bandSetNameList.append(pre + bandName)
					except:
						pass
		cfg.uiUtls.updateBar(90)
		if cfg.actionCheck == "Yes":
			# copy raster bands
			bN = 0
			for temp in tempRasterList:
				resample = ""
				try:
					cfg.utls.GDALCopyRaster(temp, outputRasterList[bN], "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1", resample)
					cfg.osSCP.remove(temp)
				except Exception as err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					try:
						cfg.shutilSCP.copy(temp, outputRasterList[bN])
						cfg.osSCP.remove(temp)
					except Exception as err:
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				bN = bN + 1
		if cfg.actionCheck == "Yes":
			# load raster bands
			for outR in outputRasterList:
				if cfg.osSCP.path.isfile(outR):
					cfg.utls.addRasterLayer(outR)
				else:
					cfg.mx.msgErr38(outR)
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "WARNING: unable to load raster" + str(outR))
			# create band set
			if cfg.ui.create_bandset_checkBox.isChecked() is True:
				if cfg.ui.add_new_bandset_checkBox_5.isChecked() is True:
					bandSetNumber = cfg.bst.addBandSetTab()
				cfg.bst.rasterBandName()
				cfg.bst.setBandSet(bandSetNameList, bandSetNumber)
				cfg.bandSetsList[bandSetNumber][0] = "Yes"
				if len(bandSetNameList) > 2:
					cfg.bst.setSatelliteWavelength(cfg.satMODIS, None, bandSetNumber)
				else:
					cfg.bst.setSatelliteWavelength(cfg.satMODIS2, None, bandSetNumber)	
				if bandSetNumber == None:
					bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
				tW = eval("cfg.ui.tableWidget__" + cfg.bndSetTabList[bandSetNumber])
				tW.clearSelection()
				tW.selectRow(0)
				tW.selectRow(1)
				cfg.bst.moveDownBand()
				cfg.bst.moveDownBand()
				tW.clearSelection()
			cfg.bst.bandSetTools(out)
			cfg.uiUtls.updateBar(100)
		# close GDAL rasters
		rDSub = None
		rD = None
		if batch == "No":
			cfg.utls.finishSound()
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()
			
	# conversion to Reflectance
	def MODIS_reflectance(self, bandNumber, conversionCoefficient, inputRaster, outputRaster):
		m = float(conversionCoefficient)
		# No data value
		if cfg.ui.nodata_checkBox_7.isChecked() is True:
			nD = cfg.ui.nodata_spinBox_8.value()
		else:
			nD = cfg.NoDataVal
		if cfg.ui.reproject_modis_checkBox.isChecked() is True:
			# temp files
			dT = cfg.utls.getTime()
			tPMN = cfg.reflectanceRasterNm + ".tif"
			tPMD = cfg.tmpDir + "/" + dT + tPMN
			cfg.utls.GDALReprojectRaster(inputRaster, tPMD, "GTiff", None, "EPSG:4326", "-ot Float32 -dstnodata -999")
			inputRaster = tPMD
		# reflectance
		try:
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputRaster)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			# output rasters
			oM = []
			oM.append(outputRaster)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21")
			o = cfg.utls.processRaster(rD, bL, None, cfg.utls.calculateRaster, None, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", "( raster *" + str("%.16f" % m) + " )", "raster", "TOA b" + str(bandNumber))
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(inputRaster))
			return "Yes"
			try:
				cfg.osSCP.remove(tPMD)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files deleted")
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"

	# MODIS conversion button
	def performMODISConversion(self):
		if len(cfg.ui.label_217.text()) == 0:
			cfg.mx.msg14()
		else:
			o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a directory"))
			if len(o) == 0:
				cfg.mx.msg14()
			else:
				self.MODIS(cfg.ui.label_217.text(), o)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Perform MODIS conversion: " + str(cfg.ui.label_217.text()))
		
	# populate table
	def populateTable(self, input, batch = "No"):
		check = "Yes"
		l = cfg.ui.MODIS_tableWidget
		cfg.utls.setColumnWidthList(l, [[0, 250]])
		cfg.utls.clearTable(l)
		if len(input) == 0:
			cfg.mx.msg14()
		else:
			if batch == "No":
				cfg.uiUtls.addProgressBar()
			# bands
			bandNames = []
			# input
			if input.lower().endswith(".hdf"):
				fileNm = cfg.osSCP.path.basename(input)[:-4]
				# open input with GDAL
				rD = cfg.gdalSCP.Open(input, cfg.gdalSCP.GA_ReadOnly)
				if rD is None:
					pass
				else:
					# get metadata
					rDMeta = rD.GetMetadata_List()
					for metadata in rDMeta:
						if "LOCALGRANULEID" in metadata:
							mod_ID = metadata.split("=")[1]
					cfg.ui.MODIS_ID_lineEdit.setText(mod_ID)
					rDSub = rD.GetSubDatasets()
					#  MODIS bands
					for sb in rDSub:
						nm = sb[0]
						if "sur_refl" in str(nm):
							try:
								bandNames.append(fileNm + "_" + nm.split("b")[1][0:2])
							except:
								pass
			# add band items to table
			b = 0
			for band in sorted(bandNames):				
				l.insertRow(b)
				l.setRowHeight(b, 20)
				cfg.utls.addTableItem(l, band, b, 0, "No")
				cfg.utls.addTableItem(l, str(0.0001), b, 1)
				b = b + 1
			if batch == "No":
				cfg.uiUtls.removeProgressBar()			

	# edited cell
	def editedCell(self, row, column):
		if column != 0:
			l = cfg.ui.MODIS_tableWidget
			val = l.item(row, column).text()
			try:
				float(val)
			except:
				l.item(row, column).setText("")
			
	def removeHighlightedBand(self):
		l = cfg.ui.MODIS_tableWidget
		cfg.utls.removeRowsFromTable(l)
		