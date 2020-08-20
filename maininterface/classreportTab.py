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

class ClassReportTab:

	def __init__(self):
		pass
	
	# calculate classification report
	def calculateClassificationReport(self, classificationPath, NoDataValue = None,  batch = "No", rasterOutput = None):
		if batch == "No":
			r = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save classification report"), "", "*.csv", "csv")
		else:
			r = rasterOutput
		if r is not False:
			if r.lower().endswith(".csv"):
				pass
			else:
				r = r + ".csv"
			# date time for temp name
			dT = cfg.utls.getTime()
			# temp report
			rN = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "report") + dT + ".csv"
			cfg.reportPth = str(cfg.tmpDir + "/" + rN)
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
				if batch == "No":
					cfg.uiUtls.addProgressBar()
				cfg.uiUtls.updateBar(10)	
				cfg.rasterBandUniqueVal = {}
				# open input with GDAL
				if cfg.osSCP.path.isfile(clssRstrSrc):
					rD = cfg.gdalSCP.Open(clssRstrSrc, cfg.gdalSCP.GA_ReadOnly)
				else:
					return "No"
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
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# No data value
				if NoDataValue is not None:
					nD = NoDataValue
				elif cfg.ui.nodata_checkBox.isChecked() is True:
					nD = cfg.ui.nodata_spinBox_2.value()
				else:
					nD = None
				o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterUniqueValuesWithSum, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, None, "UniqueVal")
				sumTot = sum(cfg.rasterBandUniqueVal.values())
				# save combination to table
				l = open(cfg.reportPth, 'w')
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Class') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'PixelSum') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Percentage %') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Area [' + un + "^2]") + str("\n")
				l.write(t)
				for i in sorted(cfg.rasterBandUniqueVal):
					if str(i) == "nan":
						pass
					else:
						p = (float(cfg.rasterBandUniqueVal[i]) /float(sumTot)) * 100
						t = str(i) + "	" + str(cfg.rasterBandUniqueVal[i]) + "	" + str(p) + "	" + str(cfg.rasterBandUniqueVal[i] * cRPX * cRPY) + str("\n")
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
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " report calculated")
				try:
					cfg.shutilSCP.copy(cfg.reportPth, r)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " report saved")
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
					cfg.utls.finishSound()
					cfg.ui.toolBox_class_report.setCurrentIndex(1)
						
	# calculate classification report if click on button
	def calculateClassReport(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " calculate classification report")
		c = str(cfg.ui.classification_report_name_combo.currentText())
		r = cfg.utls.selectLayerbyName(c, "Yes")
		if r is not None:
			ql = cfg.utls.layerSource(r)
			self.calculateClassificationReport(ql)
		else:
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
					