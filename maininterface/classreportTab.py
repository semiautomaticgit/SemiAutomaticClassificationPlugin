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

class ClassReportTab:

	def __init__(self):
		pass
	
	# calculate classification report
	def calculateClassificationReport(self, classificationPath, NoDataValue = None,  batch = 'No', rasterOutput = None):
		if batch == 'No':
			r = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save classification report"), "", "*.csv", "csv")
		else:
			r = rasterOutput
		if r is not False:
			if r.lower().endswith(".csv"):
				pass
			else:
				r = r + ".csv"
			cfg.reportPth = cfg.utls.createTempRasterPath('csv')
			try:
				clssRstrSrc = str(classificationPath)
				ck = 'Yes'
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				ck = 'No'
			if ck == 'No':
				cfg.mx.msg4()
				cfg.utls.refreshClassificationLayer()
			else:
				if batch == 'No':
					cfg.uiUtls.addProgressBar()
				cfg.uiUtls.updateBar(10)
				# open input with GDAL
				if cfg.osSCP.path.isfile(clssRstrSrc):
					rD = cfg.gdalSCP.Open(clssRstrSrc, cfg.gdalSCP.GA_ReadOnly)
				else:
					return 'No'
				# pixel size
				cRG = rD.GetGeoTransform()
				cRPX = abs(cRG[1])
				cRPY = abs(cRG[5])
				# check projections
				cRP = rD.GetProjection()
				cRSR = cfg.osrSCP.SpatialReference(wkt=cRP)
				un = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unknown")
				if cRSR.IsProjected:
					un = cRSR.GetAttrValue('unit')
				else:
					pass
				# No data value
				if NoDataValue is not None:
					nD = NoDataValue
				elif cfg.ui.nodata_checkBox.isChecked() is True:
					nD = cfg.ui.nodata_spinBox_2.value()
				else:
					nD = None
				rD = None
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = clssRstrSrc, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = nD, progressMessage = 'UniqueVal ', deleteArray = 'No')
				# calculate unique values
				values = cfg.np.array([])
				sumVal = cfg.np.array([])
				for x in sorted(cfg.parallelArrayDict):
					try:
						for ar in cfg.parallelArrayDict[x]:
							values = cfg.np.append(values, ar[0, ::])
							sumVal = cfg.np.append(sumVal, ar[1, ::])
					except:
						if batch == 'No':
							cfg.utls.finishSound()
							cfg.utls.sendSMTPMessage(None, str(__name__))
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()			
						# logger
						cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR values')
						cfg.mx.msgErr9()		
						return 'No'
				rasterBandUniqueVal = {}
				for v in range(0, len(values)):
					if values[v] != nD:
						try:
							rasterBandUniqueVal[values[v]] = rasterBandUniqueVal[values[v]] + sumVal[v]
						except:
							rasterBandUniqueVal[values[v]] = sumVal[v]
				sumTot = sum(rasterBandUniqueVal.values())
				# save combination to table
				l = open(cfg.reportPth, 'w')
				t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Class') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'PixelSum') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Percentage %') + '	' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Area [' + un + '^2]') + str('\n')
				l.write(t)
				for i in sorted(rasterBandUniqueVal):
					if str(i) == 'nan':
						pass
					else:
						p = (float(rasterBandUniqueVal[i]) /float(sumTot)) * 100
						t = str(i) + '	' + str(rasterBandUniqueVal[i]) + '	' + str(p) + '	' + str(rasterBandUniqueVal[i] * cRPX * cRPY) + str('\n')
						l.write(t)
				l.close()
				cfg.uiUtls.updateBar(80)
				# open csv
				try:
					f = open(cfg.reportPth)
					if cfg.osSCP.path.isfile(cfg.reportPth):
						reportTxt = f.read()
						cfg.ui.report_textBrowser.setText(str(reportTxt))
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " report calculated")
				try:
					cfg.shutilSCP.copy(cfg.reportPth, r)
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " report saved")
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.ui.toolBox_class_report.setCurrentIndex(1)
						
	# calculate classification report if click on button
	def calculateClassReport(self):
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " calculate classification report")
		c = str(cfg.ui.classification_report_name_combo.currentText())
		r = cfg.utls.selectLayerbyName(c, 'Yes')
		if r is not None:
			ql = cfg.utls.layerSource(r)
			self.calculateClassificationReport(ql)
		else:
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
					