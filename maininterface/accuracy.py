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
			i = cfg.utls.selectLayerbyName(classification, "Yes")
			l = cfg.utls.selectLayerbyName(reference)
			if i is not None and l is not None:
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
				# field of reclassification
				if cfg.macroclassCheck == "No":
					fd = cfg.fldID_class
				elif cfg.macroclassCheck == "Yes":
					fd = cfg.fldMacroID_class
				# convert reference layer to raster
				cfg.utls.vectorToRaster(str(fd), unicode(l.source()), classification, unicode(tRC))		
				cfg.uiUtls.updateBar(10)
				# open input with GDAL
				refRstrDt = gdal.Open(unicode(tRC), GA_ReadOnly)
				newRstrDt = gdal.Open(i.source(), GA_ReadOnly)
				# number of x pixels
				refRstrCols = refRstrDt.RasterXSize
				newRstrCols = newRstrDt.RasterXSize
				# number of y pixels
				refRstrRows = refRstrDt.RasterYSize
				newRstrRows = newRstrDt.RasterYSize
				# check projections
				refRstrProj = refRstrDt.GetProjection()
				newRstrProj = newRstrDt.GetProjection()
				# pixel size and origin
				refRstGeoTrnsf = refRstrDt.GetGeoTransform()
				newRstGeoTrnsf = newRstrDt.GetGeoTransform()
				refRstPxlXSz = abs(refRstGeoTrnsf[1])
				newRstPxlXSz = abs(newRstGeoTrnsf[1])
				refRstPxlYSz = abs(refRstGeoTrnsf[5])
				newRstPxlYSz = abs(newRstGeoTrnsf[5])
				if refRstrProj != newRstrProj:
					cfg.mx.msg9()
				else:
					errorRstPath = rstrOut
					errorRstPath = errorRstPath.replace('\\', '/')
					errorRstPath = errorRstPath.replace('//', '/')
					tblOut = os.path.dirname(errorRstPath) + "/" + os.path.basename(errorRstPath)
					tblOut = os.path.splitext(tblOut)[0] + ".csv"
					if unicode(errorRstPath).endswith(".tif"):
						pass
					else:
						errorRstPath = errorRstPath + ".tif"
					if refRstPxlXSz != newRstPxlXSz or refRstPxlYSz != newRstPxlYSz:
						cfg.mx.msgWar5()
					# get band
					refRstrBnd = refRstrDt.GetRasterBand(1)
					newRstrBnd = newRstrDt.GetRasterBand(1)
					# calculate raster offset
					xOffst = int((refRstGeoTrnsf[0] - newRstGeoTrnsf[0]) / refRstPxlXSz) 
					yOffst = int((refRstGeoTrnsf[3] - newRstGeoTrnsf[3]) / refRstPxlYSz)
					# calculate overlapping origins, rows and columns
					if xOffst <= 0:
						refRstrXOrig = abs(xOffst)
						newRstrXOrig = 0
						if refRstrCols + xOffst < newRstrCols:
							ovlpCols = refRstrCols +  xOffst
						elif refRstrCols + xOffst >= newRstrCols:
							ovlpCols = newRstrCols
					if xOffst > 0:
						refRstrXOrig = 0
						newRstrXOrig = xOffst
						if refRstrCols < newRstrCols - xOffst:
							ovlpCols = refRstrCols
						elif refRstrCols >= newRstrCols - xOffst:
							ovlpCols = newRstrCols - xOffst
					if yOffst >= 0:
						refRstrYOrig = yOffst
						newRstrYOrig = 0
						if refRstrRows - yOffst <= newRstrRows:
							ovlpRows = refRstrRows - yOffst
						elif refRstrRows - yOffst > newRstrRows:
							ovlpRows = newRstrRows
					if yOffst < 0:
						refRstrYOrig = 0
						newRstrYOrig = abs(yOffst)
						if refRstrRows < newRstrRows + yOffst:
							ovlpRows = refRstrRows
						elif refRstrRows >= newRstrRows + yOffst:
							ovlpRows = newRstrRows + yOffst
					blockSizeX = cfg.utls.calculateBlockSize(6)
					blockSizeY = blockSizeX
					# reference raster range blocks
					lX = range(refRstrXOrig, refRstrXOrig + ovlpCols, blockSizeX)
					lY = range(refRstrYOrig, refRstrYOrig + ovlpRows, blockSizeY)
					# new raster range blocks
					nlX = range(newRstrXOrig, newRstrXOrig + ovlpCols, blockSizeX)
					nlY = range(newRstrYOrig, newRstrYOrig + ovlpRows, blockSizeY)
					cfg.uiUtls.updateBar(20)
					# set initial value for progress bar
					progresStep = 60 / (len(lX) * len(lY))
					progressStart = 20 - progresStep
					# block size
					if blockSizeX > ovlpCols:
						blockSizeX = ovlpCols
					if blockSizeY > ovlpRows:
						blockSizeY = ovlpRows
					# create output raster
					oC = []
					oC.append(rstrOut)
					oCR = cfg.utls.createRasterFromReference(refRstrDt, 1, oC, cfg.NoDataVal, "GTiff", GDT_Int32)
					cmbntns = []
					valSum = []
					n = 1
					# process
					for y in lY:
						bSY = blockSizeY
						for x in lX:
							if cfg.actionCheck == "Yes":
								progress = progressStart + n * progresStep
								cfg.uiUtls.updateBar(progress)
								bSX = blockSizeX
								if bSY + y > refRstrYOrig + ovlpRows:
									bSY = ovlpRows - y
								if x + bSX > refRstrXOrig + ovlpCols:
									bSX = ovlpCols - x
								# combinations of classes
								refRstrArr = refRstrBnd.ReadAsArray(x, y, bSX, bSY)
								newRstrArr = newRstrBnd.ReadAsArray(nlX[lX.index(x)], nlY[lY.index(y)], bSX, bSY)
								refRstrVal = np.unique(refRstrArr).tolist()
								newRstrVal = np.unique(newRstrArr).tolist()
								cmb = list(itertools.product(refRstrVal, newRstrVal))
								for i in cmb:
									if i not in cmbntns:
										if str(i[0]) != str(cfg.NoDataVal):
											cmbntns.extend([i])
											valSum.append(0)
								val = 1
								changeArray = None
								for i in cmbntns:
									# change conditions
									cmbsArr = val * np.logical_and(refRstrArr == i[0], newRstrArr == i[1])
									sum = np.count_nonzero(cmbsArr)
									# change raster
									if changeArray == None:
										changeArray = cmbsArr
									else:
										e = np.ma.masked_equal(cmbsArr, 0)
										changeArray =  e.mask * changeArray + cmbsArr
										e = None
									valSum[val - 1] = valSum[val - 1] + sum
									cfg.utls.writeArrayBlock(oCR[0], 1, changeArray, x, y, cfg.NoDataVal)
									val = val + 1
							n = n + 1
					cfg.uiUtls.updateBar(80)
					# error matrix
					col = []
					row = []
					for k in cmbntns:
						col.append(k[0])
						row.append(k[1])
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
					v = 1
					# append total
					total.append(str(QApplication.translate("semiautomaticclassificationplugin", 'Total')))
					for c in total:
						cList = cList + str(c) + "\t"
						for r in total:
							try:
								t = str(v) + "\t" + str(c) + "\t" + str(r) + "\t" + str(valSum[cmbntns.index((c, r))]) + str("\n")
								l.write(t)
								errMatrix[total.index(r), total.index(c)] = valSum[cmbntns.index((c, r))]
								v = v + 1
							except:
								pass
					# save combination to table
					l.write(str("\n"))
					l.write(str(QApplication.translate("semiautomaticclassificationplugin", 'ERROR MATRIX')) + str("\n"))
					l.write("\t" + "> " + str(QApplication.translate("semiautomaticclassificationplugin", 'Reference')) + str("\n"))
					l.write(cList + str("\n"))
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
					for c in range(0, len(total) - 1):
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
					for g in range(0, len(total) - 1):
						p = 100 * errMatrix[g,g] / errMatrix[:, g].sum()
						u = 100 * errMatrix[g,g] / errMatrix[g, :].sum()
						t = QApplication.translate("semiautomaticclassificationplugin", 'Class ') + str(total[g]) + QApplication.translate("semiautomaticclassificationplugin", ' producer accuracy [%] = ') + str(p) + "\t" + QApplication.translate("semiautomaticclassificationplugin", ' user accuracy [%] = ') + str(u) + str("\n")
						l.write(t)
					l.close()
					# close bands
					refRstrBnd = None
					newRstrBnd = None
					oCR[0] = None
					refRstrDt = None
					newRstrDt = None
					# add raster to layers
					cfg.iface.addRasterLayer(unicode(rstrOut), unicode(os.path.basename(rstrOut)))
					rstr = cfg.utls.selectLayerbyName(unicode(os.path.basename(rstrOut)), "Yes")
					cfg.utls.rasterSymbolGeneric(rstr)	
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
	
	# reference layer name
	def referenceLayerName(self):
		cfg.referenceLayer = cfg.ui.reference_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layer name: " + unicode(cfg.referenceLayer))
	
	def refreshReferenceLayer(self):
		ls = cfg.lgnd.layers()
		cfg.ui.reference_name_combo.clear()
		# reference layer name
		cfg.referenceLayer = None
		for l in ls:
			if (l.type()==QgsMapLayer.VectorLayer):
				if (l.geometryType() == QGis.Polygon):
					# filter if shapefile has ID_class field
					fds = l.dataProvider().fields()
					if fds.indexFromName(cfg.fldID_class) > -1:
						cfg.dlg.reference_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layers refreshed")
