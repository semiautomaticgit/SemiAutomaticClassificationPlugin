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

class ReprojectRasterBands:

	def __init__(self):
		pass
		
	def reprojectRasterBands(self):
		bandSet = cfg.ui.band_set_comb_spinBox_14.value() - 1
		sameExtent = 'No'
		outName = cfg.ui.reproj_output_name_lineEdit.text()
		if len(outName) > 0:
			outName = str(outName.encode('ascii','replace'))[2:-1]
		else:
			outName = None
		alignRaster = None
		EPSG = None
		if cfg.ui.use_align_raster_checkBox.isChecked() is True:
			# use align
			referenceRasterName = cfg.ui.raster_align_comboBox.currentText()
			try:
				sL = cfg.utls.selectLayerbyName(referenceRasterName)
				alignRaster = cfg.utls.layerSource(sL)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))	
				return 'No'
			if cfg.ui.same_extent_raster_checkBox.isChecked() is True:
				sameExtent = 'Yes'
		# use EPSG
		elif cfg.ui.use_epsg_checkBox.isChecked() is True:
			# spatial reference
			referenceRasterName = None
			try:
				EPSG = int(cfg.ui.epsg_code_lineEdit.text())
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))	
				return 'No'
		if cfg.ui.change_nodata_checkBox.isChecked() is True:
			noData = cfg.ui.nodata_spinBox_14.value()
		else:
			noData = None
		if cfg.ui.resample_checkBox.isChecked() is True:
			try:
				resPixelSize = float(cfg.ui.resample_lineEdit.text())
			except:
				resPixelSize = None
		else:
			resPixelSize = None
		xResolution = cfg.ui.x_resolution_lineEdit.text()
		yResolution = cfg.ui.y_resolution_lineEdit.text()
		# resampling method
		resampling = cfg.ui.resampling_method_comboBox.currentText()
		if resampling == 'nearest_neighbour':
			resample = 'near'
		elif resampling == 'average':
			resample = 'average'
		elif resampling == 'sum':
			resample = 'sum'
			gdalV = cfg.utls.getGDALVersion()
			if float(gdalV[0] + '.' + gdalV[1]) < 3.1:
				cfg.mx.msgErr68()
				return 'No'
		elif resampling == 'maximum':
			resample = 'max'
		elif resampling == 'minimum':
			resample = 'min'
		elif resampling == 'mode':
			resample = 'mode'
		elif resampling == 'median':
			resample = 'med'
		elif resampling == 'first_quartile':
			resample = 'q1'
		elif resampling == 'third_quartile':
			resample = 'q3'
		# resampling type
		type = cfg.ui.raster_type_combo_2.currentText()
		if type.lower() == 'auto':
			type = None
		self.reprojectRasters('No', None, alignRaster, sameExtent, EPSG, xResolution, yResolution, resPixelSize, resample, type, noData, outName, bandSet)
		
	# reproject multiple rasters
	def reprojectRasters(self, batch = 'No', outputDirectory = None, alignRasterPath = None, sameExtent = 'No', EPSGCode = None, xResolution = None, yResolution = None, resamplePixelFactor = None, resamplingMethod = None, outputType = None, noDataValue = None, outputName = None, bandSetNumber = None, outFormat = 'GTiff'):
		EPSG = None
		if bandSetNumber is None:
			bandSet = cfg.ui.band_set_comb_spinBox_14.value()
			bandSetNumber = bandSet - 1
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		if resamplePixelFactor is None:
			resamplePixelFactor = 1
		try:
			resamplePixelFactor = float(resamplePixelFactor)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))	
			cfg.mx.msgErr67()
			return 'No'
		# list of images
		rT = []
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			ckB = cfg.utls.checkBandSet(bandSetNumber)
			if ckB == 'Yes':
				rT = cfg.bandSetsList[bandSetNumber][3]
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rasters to be projected' + str(rT))
				if len(rT) == 0:
					cfg.mx.msgWar15()
					return 'No'
				if batch == 'No':
					oD = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory where to save projected rasters'))
				else:
					oD = outputDirectory
				if len(oD) > 0:
					if outputName is None:
						outputName = cfg.reprojNm
				else:
					return 'No'
				cfg.utls.makeDirectory(oD)
				if alignRasterPath is not None:
					# raster extent and pixel size	
					try:
						left, right, top, bottom, pX, pY, rP, unit = cfg.utls.imageGeoTransform(alignRasterPath)
						# check projections
						rPSys =cfg.osrSCP.SpatialReference(wkt=rP)
						rPSys.AutoIdentifyEPSG()
						EPSG = 'No'
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))	
						cfg.mx.msgErr67()
						return 'No'
					pX = pX * resamplePixelFactor
					pY = pY * resamplePixelFactor
					extra = '-tr ' + str(pX) + ' ' + str(pY) + ' -te ' + str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
		else:
			cfg.mx.msgWar15()
			return 'No'
		if batch == 'No':
			cfg.uiUtls.addProgressBar()
		outList = []
		n = 0
		for l in rT:
			prog = int(n / len(rT))
			lC = cfg.utls.selectLayerbyName(l, 'Yes')
			bLS = cfg.utls.layerSource(lC)
			# calculate minimal extent
			if alignRasterPath is not None:
				# raster extent and pixel size
				try:
					leftS, rightS, topS, bottomS, pXS, pYS, rPS, unitS = cfg.utls.imageGeoTransform(bLS)
					rPSC =cfg.osrSCP.SpatialReference(wkt=rPS)
					leftSP, topSP  = cfg.utls.projectPointCoordinatesOGR(leftS, topS, rPSC, rPSys)
					rightSP, bottomSP = cfg.utls.projectPointCoordinatesOGR(rightS, bottomS, rPSC, rPSys)
				# Error latitude or longitude exceeded limits
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msgErr61(lC)
					return 'No'
				if sameExtent == 'No':
					# minimum extent
					if leftSP < left:
						leftR = left - int(2 + (left - leftSP) / pX) * pX
					else:
						leftR = left + int((leftSP- left) / pX - 2) * pX
					if rightSP > right:
						rightR = right + int(2 + (rightSP - right) / pX) * pX
					else:
						rightR = right - int((right - rightSP) / pX - 2) * pX
					if topSP > top:
						topR = top + int(2 + (topSP - top) / pY) * pY
					else:
						topR = top - int((top - topSP) / pY - 2) * pY
					if bottomSP > bottom:
						bottomR = bottom + int((bottomSP - bottom) / pY - 2) * pY
					else:
						bottomR = bottom - int(2 + (bottom - bottomSP) / pY) * pY
				else:
					leftR, rightR, topR, bottomR, pXR, pYR, rPR, unitR = cfg.utls.imageGeoTransform(alignRasterPath)
				extra = '-tr ' + str(pX) + ' ' + str(pY) + ' -te ' + str(leftR) + ' ' + str(bottomR) + ' ' + str(rightR) + ' ' + str(topR)
			# use EPSG
			elif EPSGCode is not None:
				# spatial reference
				extra = None
				try:
					EPSG = int(EPSGCode)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msgErr67()
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						return 'No'			
				if sameExtent == 'No':
					try:
						extra = '-tr ' + str(float(xResolution)) + ' ' + str(float(yResolution))
					except:
						pass
				else:
					leftR, rightR, topR, bottomR, pXR, pYR, rPR, unitR = cfg.utls.imageGeoTransform(alignRasterPath)	
					try:
						extra = '-tr ' + str(float(xResolution)) + ' ' + str(float(yResolution)) + ' -te ' + str(leftR) + ' ' + str(bottomR) + ' ' + str(rightR) + ' ' + str(topR)
					except:
						pass
			# resample
			else:
				if EPSG == 'No':
					pass
				else:
					EPSG = None
				# raster extent and pixel size
				try:
					leftS, rightS, topS, bottomS, pXS, pYS, rPS, unitS = cfg.utls.imageGeoTransform(bLS)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.mx.msgErr61(lC)
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						return 'No'
				pX = pXS * resamplePixelFactor
				pY = pYS * resamplePixelFactor
				if sameExtent == 'No':
					try:
						extra = '-tr ' + str(pX) + ' ' + str(pY)
					except:
						pass
				else:
					leftR, rightR, topR, bottomR, pXR, pYR, rPR, unitR = cfg.utls.imageGeoTransform(alignRasterPath)	
					try:
						extra = '-tr ' + str(pX) + ' ' + str(pY) + ' -te ' + str(leftR) + ' ' + str(bottomR) + ' ' + str(rightR) + ' ' + str(topR)
					except:
						pass
			if str(l).lower().endswith('.tif'):
				pass
			else:
				l = l + '.tif'
			f = oD + '/' + outputName + '_'  + cfg.utls.fileName(l)
			tRxs = cfg.utls.createTempRasterPath('tif')
			if EPSG is not None:
				if EPSG == 'No':
					outEPSG = rP
				else:
					outEPSG = 'EPSG:' + str(EPSG)
			else:
				outEPSG = None
			if resamplingMethod is None:
				resamplingMethod = 'near'
			cfg.utls.GDALReprojectRaster(input = bLS, output = tRxs, outFormat = outFormat, s_srs = None, t_srs = outEPSG, additionalParams = extra, resampleMethod = resamplingMethod, rasterDataType = outputType, noDataVal = noDataValue)
			try:
				cfg.shutilSCP.move(tRxs, f)
				outList.append(f)
			except Exception as err:
				# logger
				if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.uiUtls.updateBar(prog)
			n = n + 1
		try:
			for oU in outList:
				cfg.utls.addRasterLayer(oU)
		except Exception as err:
			# logger
			if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rasters reprojected' )
		if batch == 'No':
			# enable map canvas render
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()
			cfg.utls.finishSound()
			cfg.utls.sendSMTPMessage(None, str(__name__))
		
	# checkbox changed
	def checkboxAlignChanged(self):
		cfg.ui.use_align_raster_checkBox.blockSignals(True)
		cfg.ui.use_epsg_checkBox.blockSignals(True)
		if cfg.ui.use_align_raster_checkBox.isChecked():
			cfg.ui.use_epsg_checkBox.setCheckState(0)
		cfg.ui.use_align_raster_checkBox.blockSignals(False)
		cfg.ui.use_epsg_checkBox.blockSignals(False)
		
	# checkbox changed
	def checkboxEPSGChanged(self):
		cfg.ui.use_align_raster_checkBox.blockSignals(True)
		cfg.ui.use_epsg_checkBox.blockSignals(True)
		if cfg.ui.use_epsg_checkBox.isChecked():
			cfg.ui.use_align_raster_checkBox.setCheckState(0)
		cfg.ui.use_align_raster_checkBox.blockSignals(False)
		cfg.ui.use_epsg_checkBox.blockSignals(False)
		
	def refreshClassificationLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.raster_align_comboBox.clear()
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				cfg.dlg.project_raster_combo(l.name())
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'raster layers refreshed')
		