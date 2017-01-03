# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2017 by Luca Congedo
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

from qgis.core import *
from qgis.gui import *
cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

class ClassReportTab:

	def __init__(self):
		pass
	
	# calculate classification report
	def calculateClassificationReport(self, classificationPath, NoDataValue = None,  batch = "No", rasterOutput = None):
		if batch == "No":
			r = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save classification report"), "", "Text (*.csv)")
		else:
			r = rasterOutput
		if len(r) > 0:
			# date time for temp name
			dT = cfg.utls.getTime()
			# temp report
			rN = cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "report") + dT + ".csv"
			cfg.reportPth = str(cfg.tmpDir + "/" + rN)
			try:
				clssRstrSrc = unicode(classificationPath)
				ck = "Yes"
			except Exception, err:
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
				DNm = 0
				cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
				cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
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
				un = cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Unknown")
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
				o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, None, "UniqueVal")
				cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
				cfg.rasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)
				try:
					cfg.rasterBandUniqueVal.remove(nD)
				except:
					pass
				cfg.rasterBandPixelCount = 0
				o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterValueCount, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, cfg.rasterBandUniqueVal[-1], "Sum")
				sum = cfg.rasterBandPixelCount
				# save combination to table
				l = open(cfg.reportPth, 'w')
				t = str(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Class')) + "	" + str(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'PixelSum')) + "	" + str(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Percentage %')) + "	" + str(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Area [' + str(un) + "^2]") + str("\n"))
				l.write(t)
				for i in cfg.rasterBandUniqueVal:
					cfg.rasterBandPixelCount = 0
					o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterEqualValueCount, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, i, "value " + str(i))
					p = (float(cfg.rasterBandPixelCount) /float(sum)) * 100
					t = str(i) + "	" + str(cfg.rasterBandPixelCount) + "	" + str(p) + "	" + str(cfg.rasterBandPixelCount * cRPX * cRPY) + str("\n")
					l.write(t)
				l.close()			
				# close bands
				cRB = None
				# close rasters
				cR = None
				cfg.uiUtls.updateBar(80)
				# open csv
				try:
					f = open(cfg.reportPth)
					if cfg.osSCP.path.isfile(cfg.reportPth):
						reportTxt = f.read()
						cfg.ui.report_textBrowser.setText(str(reportTxt))
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " report calculated")
				try:
					cfg.shutilSCP.copy(cfg.reportPth, r)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " report saved")
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				if batch == "No":
					cfg.uiUtls.removeProgressBar()
					cfg.utls.finishSound()
						
	# calculate classification report if click on button
	def calculateClassReport(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " calculate classification report")
		c = str(cfg.ui.classification_report_name_combo.currentText())
		r = cfg.utls.selectLayerbyName(c, "Yes")
		if r is not None:
			self.calculateClassificationReport(r.source())
		else:
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
					