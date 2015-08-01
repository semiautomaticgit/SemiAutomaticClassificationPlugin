# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
 providing a tool for the region growing of image pixels, creating polygon shapefiles intended for
 the collection of training areas (ROIs), and rapidly performing the classification process (or a preview).
							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2015 by Luca Congedo
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

import os
import numpy as np
import itertools
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from osgeo import gdal
from osgeo.gdalconst import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class Accuracy:

	def __init__(self):
		self.clssfctnNm = None
		
	# calculate error matrix if click on button
	def calculateErrorMatrix(self):
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " calculate Error Matrix")
		self.errorMatrix(self.clssfctnNm, cfg.referenceLayer)
	
	# classification name
	def classificationLayerName(self):
		self.clssfctnNm = cfg.ui.classification_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification name: " + unicode(self.clssfctnNm))
	
	# error matrix calculation
	def errorMatrix(self, classification, reference):
		# check if numpy is updated
		try:
			np.count_nonzero([1,1,0])
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			rstrCheck = "No"
			cfg.mx.msgErr26()
			a = cfg.utls.questionBox("Semi-Automatic Classification Plugin", "NumPy version is outdated. Do you want to open the following site for help? http://fromgistors.blogspot.com/p/frequently-asked-questions.html#numpy_version ")
			if a == "Yes":
				QDesktopServices().openUrl(QUrl("http://fromgistors.blogspot.com/p/frequently-asked-questions.html#numpy_version"))
			return "No"
		rstrOut = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save error matrix raster output"), "", "*.tif")
		if len(rstrOut) > 0:
			iClass = cfg.utls.selectLayerbyName(classification, "Yes")
			l = cfg.utls.selectLayerbyName(reference)
			if iClass is not None and l is not None:
				# check projections
				newRstrProj = cfg.utls.getCrs(iClass)
				refRstrProj = cfg.utls.getCrs(l)
				if refRstrProj != newRstrProj:
					cfg.mx.msg9()
					return "No"
				else:
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
					qApp.processEvents()
					# date time for temp name
					dT = cfg.utls.getTime()
					# temp raster layer
					tRC= cfg.tmpDir + "/" + cfg.rclssTempNm + dT + ".tif"
					# error matrix
					eMN = dT + cfg.errMatrixNm
					cfg.reportPth = str(cfg.tmpDir + "/" + eMN)
					errorRstPath = rstrOut
					errorRstPath = errorRstPath.replace('\\', '/')
					errorRstPath = errorRstPath.replace('//', '/')
					tblOut = os.path.dirname(errorRstPath) + "/" + os.path.basename(errorRstPath)
					tblOut = os.path.splitext(tblOut)[0] + ".csv"
					if unicode(errorRstPath).lower().endswith(".tif"):
						pass
					else:
						errorRstPath = errorRstPath + ".tif"
				cfg.uiUtls.updateBar(10)
				# if reference shapefile
				if l.type()== 0:
					fd = cfg.ui.class_field_comboBox.currentText()
					# convert reference layer to raster
					cfg.utls.vectorToRaster(fd, unicode(l.source()), classification, unicode(tRC))
					referenceRaster = tRC
				# if reference raster
				elif l.type()== 1:
					referenceRaster = l.source()
				# open input with GDAL
				refRstrDt = gdal.Open(unicode(referenceRaster), GA_ReadOnly)
				newRstrDt = gdal.Open(iClass.source(), GA_ReadOnly)
				# combination finder
				# band list
				bLR = cfg.utls.readAllBandsFromRaster(refRstrDt)
				cfg.rasterBandUniqueVal = np.zeros((1, 1))
				cfg.rasterBandUniqueVal = np.delete(cfg.rasterBandUniqueVal, 0, 1)
				o = cfg.utls.processRaster(refRstrDt, bLR, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
				cfg.rasterBandUniqueVal = np.unique(cfg.rasterBandUniqueVal).tolist()
				refRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)
				# band list
				bLN = cfg.utls.readAllBandsFromRaster(newRstrDt)
				cfg.rasterBandUniqueVal = np.zeros((1, 1))
				cfg.rasterBandUniqueVal = np.delete(cfg.rasterBandUniqueVal, 0, 1)
				o = cfg.utls.processRaster(newRstrDt, bLN, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
				for b in range(0, len(bLR)):
					bLR[b] = None
				refRstrDt = None
				for b in range(0, len(bLN)):
					bLN[b] = None
				newRstrDt = None		
				cfg.rasterBandUniqueVal = np.unique(cfg.rasterBandUniqueVal).tolist()
				newRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)	
				cmb = list(itertools.product(refRasterBandUniqueVal, newRasterBandUniqueVal))
				# error matrix
				col = []
				row = []
				cmbntns = {}
				# expression builder
				n = 1
				cPar = " "
				e = "np.where( "
				for i in cmb:
					if str(i[0]) == "nan" or str(i[1]) == "nan" :
						pass
					else:
						e = e + "(a == " + str(i[0]) + ") & (b == " + str(i[1]) + "), " + str(n) + ", (np.where( "
						cPar = cPar + "))"
						cmbntns["combination_" + str(i[0]) + "_"+ str(i[1])] = n
						col.append(i[0])
						row.append(i[1])
						n = n + 1
				e = e[:-11] + str(cfg.NoDataVal) + cPar[:-1]
				# virtual raster
				tPMN = cfg.tmpVrtNm + ".vrt"
				# date time for temp name
				dT = cfg.utls.getTime()
				tPMD = cfg.tmpDir + "/" + dT + tPMN
				bList = [unicode(referenceRaster), iClass.source()]
				bandNumberList = [1, 1]
				vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", cfg.NoDataVal, 0, "No", "No")
				# open input with GDAL
				rD = gdal.Open(tPMD, GA_ReadOnly)
				# output rasters
				oM = []
				oM.append(errorRstPath)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, "Yes")
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# calculation
				variableList = [["im1", "a"], ["im2", "b"]]
				o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.bandCalculation, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "No")
				# logger
				cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "accuracy raster output: " + unicode(rstrOut))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				cfg.uiUtls.updateBar(80)
				cols = sorted(np.unique(col).tolist())
				rows = sorted(np.unique(row).tolist())
				totX = cols
				totX.extend(rows)
				total = sorted(np.unique(totX).tolist())
				errMatrix = np.zeros((len(total), len(total)))
				cList = "V " + str(QApplication.translate("semiautomaticclassificationplugin", 'Classification')) + "\t"
				l = open(tblOut, 'w')
				t = str(QApplication.translate("semiautomaticclassificationplugin", 'ErrMatrixCode')) + "	" + str(QApplication.translate("semiautomaticclassificationplugin", 'Reference')) + "	" + str(QApplication.translate("semiautomaticclassificationplugin", 'Classification')) + "	" + str(QApplication.translate("semiautomaticclassificationplugin", 'PixelSum') + str("\n"))
				l.write(t)
				# open error raster
				rDC = gdal.Open(errorRstPath, GA_ReadOnly)
				bLC = cfg.utls.readAllBandsFromRaster(rDC)
				for c in total:
					cList = cList + str(c) + "\t"
					for r in total:
						cfg.rasterBandPixelCount = 0
						try:
							v = cmbntns["combination_" + str(c) + "_"+ str(r)]
							o = cfg.utls.processRaster(rDC, bLC, None, "No", cfg.utls.rasterEqualValueCount, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, v, "value " + str(v))
							t = str(v) + "\t" + str(c) + "\t" + str(r) + "\t" + str(cfg.rasterBandPixelCount) + str("\n")
							l.write(t)
							errMatrix[total.index(r), total.index(c)] = cfg.rasterBandPixelCount
						except:
							errMatrix[total.index(r), total.index(c)] = cfg.rasterBandPixelCount
				# save combination to table
				l.write(str("\n"))
				l.write(str(QApplication.translate("semiautomaticclassificationplugin", 'ERROR MATRIX')) + str("\n"))
				l.write("\t" + "> " + str(QApplication.translate("semiautomaticclassificationplugin", 'Reference')) + str("\n"))
				l.write(cList + str(QApplication.translate("semiautomaticclassificationplugin", 'Total') + str("\n")))
				# temp matrix
				tmpMtrx= cfg.tmpDir + "/" + cfg.tempMtrxNm + dT + ".txt"
				np.savetxt(tmpMtrx, errMatrix, delimiter="\t", fmt="%i")
				tM = open(tmpMtrx, 'r')
				# write matrix
				ix = 0
				for j in tM:
					tMR = str(total[ix]) + "\t" + j.rstrip('\n') + "\t" + str(int(errMatrix[ix, :].sum())) + str("\n")
					l.write(tMR)
					ix = ix + 1
				# last line
				lL = str(QApplication.translate("semiautomaticclassificationplugin", 'Total'))
				for c in range(0, len(total)):
					lL = lL + "\t" + str(int(errMatrix[:, c].sum()))
				totMat = int(errMatrix.sum())
				lL = lL + "\t" + str(totMat) + str("\n")
				l.write(lL)
				l.write(str("\n"))
				# overall accuracy
				oA = 100 * errMatrix.trace() / totMat
				t = str(QApplication.translate("semiautomaticclassificationplugin", 'Overall accuracy [%] = ')) + str(oA) + str("\n")
				l.write(t)
				# producer's accuracy
				for g in range(0, len(total)):
					p = 100 * errMatrix[g,g] / errMatrix[:, g].sum()
					u = 100 * errMatrix[g,g] / errMatrix[g, :].sum()
					t = QApplication.translate("semiautomaticclassificationplugin", 'Class ') + str(total[g]) + QApplication.translate("semiautomaticclassificationplugin", ' producer accuracy [%] = ') + str(p) + "\t" + QApplication.translate("semiautomaticclassificationplugin", ' user accuracy [%] = ') + str(u) + str("\n")
					l.write(t)
				l.close()
				# close bands
				for b in range(0, len(bLC)):
					bLC[b] = None
				rDC = None
				# add raster to layers
				cfg.iface.addRasterLayer(unicode(errorRstPath), unicode(os.path.basename(errorRstPath)))
				rstr = cfg.utls.selectLayerbyName(unicode(os.path.basename(errorRstPath)), "Yes")
				cfg.utls.rasterSymbolGeneric(rstr, "NoData")	
				try:
					f = open(tblOut)
					if os.path.isfile(tblOut):
						eM = f.read()
						cfg.ui.error_matrix_textBrowser.setText(str(eM))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " error matrix calculated")
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.uiUtls.updateBar(100)
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.utls.finishSound()
				cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "finished")
			else:
				self.refreshReferenceLayer()
				cfg.utls.refreshClassificationLayer()
				
	# reference layer name
	def referenceLayerName(self):
		cfg.referenceLayer = cfg.ui.reference_name_combo.currentText()
		cfg.ui.class_field_comboBox.clear()
		l = cfg.utls.selectLayerbyName(cfg.referenceLayer)
		try:
			if l.type()== 0:
				f = l.dataProvider().fields()
				for i in f:
					if i.typeName() != "String":
						cfg.dlg.class_field_combo(unicode(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layer name: " + unicode(cfg.referenceLayer))
	
	# refresh reference layer name
	def refreshReferenceLayer(self):
		ls = cfg.lgnd.layers()
		cfg.ui.reference_name_combo.clear()
		# reference layer name
		cfg.referenceLayer = None
		for l in ls:
			if (l.type()==QgsMapLayer.VectorLayer):
				if (l.geometryType() == QGis.Polygon):
					cfg.dlg.reference_layer_combo(l.name())
			elif (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.reference_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layers refreshed")
