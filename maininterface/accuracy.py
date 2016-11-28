# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2016 by Luca Congedo
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

class Accuracy:

	def __init__(self):
		self.clssfctnNm = None
		
	# calculate error matrix if click on button
	def calculateErrorMatrix(self):
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " calculate Error Matrix")
		self.errorMatrix(self.clssfctnNm, cfg.referenceLayer)
	
	# classification name
	def classificationLayerName(self):
		self.clssfctnNm = cfg.ui.classification_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification name: " + unicode(self.clssfctnNm))
	
	# error matrix calculation
	def errorMatrix(self, classification, reference, batch = "No", shapefileField = None, rasterOutput = None):
		# check if numpy is updated
		try:
			cfg.np.count_nonzero([1,1,0])
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			rstrCheck = "No"
			cfg.mx.msgErr26()
		if batch == "No":
			rstrOut = cfg.utls.getSaveFileName(None, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save error matrix raster output"), "", "*.tif")
		else:
			rstrOut = rasterOutput
		if len(rstrOut) > 0:
			if batch == "No":
				iClass = cfg.utls.selectLayerbyName(classification, "Yes")
				l = cfg.utls.selectLayerbyName(reference)
			else:
				try:
					# open input with GDAL
					rD = cfg.gdalSCP.Open(reference, cfg.gdalSCP.GA_ReadOnly)
					if rD is None:
						l = cfg.utls.addVectorLayer(unicode(reference) , unicode(cfg.osSCP.path.basename(reference)), "ogr")
					else:
						l = cfg.iface.addRasterLayer(unicode(reference), unicode(cfg.osSCP.path.basename(reference)))
					reml = l
					rD = None
					if cfg.osSCP.path.isfile(classification):
						iClass = cfg.iface.addRasterLayer(unicode(classification), unicode(cfg.osSCP.path.basename(classification)))
						remiClass = iClass
					else:
						return "No"
				except:
					return "No"
			# date time for temp name
			dT = cfg.utls.getTime()
			if iClass is not None and l is not None:
				# if not reference shapefile
				if l.type() != 0:
					# check projections
					newRstrProj = cfg.utls.getCrs(iClass)
					refRstrProj = cfg.utls.getCrs(l)
					if refRstrProj != newRstrProj:
						cfg.mx.msg9()
						return "No"
				else:
					# vector EPSG
					if "MultiPolygon?crs=PROJCS" in str(l.source()):
						# temp shapefile
						tSHP = cfg.tmpDir + "/" + cfg.rclssTempNm + dT + ".shp"
						l = cfg.utls.saveMemoryLayerToShapefile(l, tSHP)
						vEPSG = cfg.utls.getEPSGVector(tSHP)
					else:
						vEPSG = cfg.utls.getEPSGVector(l.source())
					dT = cfg.utls.getTime()
					# in case of reprojection
					reprjShapefile = cfg.tmpDir + "/" + dT + cfg.osSCP.path.basename(l.source())
					rEPSG = cfg.utls.getEPSGRaster(iClass.source())
					if vEPSG != rEPSG:
						if cfg.osSCP.path.isfile(reprjShapefile):
							pass
						else:
							try:
								cfg.utls.repojectShapefile(l.source(), int(vEPSG), reprjShapefile, int(rEPSG))
							except Exception, err:
								# remove temp layers
								cfg.utls.removeLayerByLayer(reml)
								cfg.utls.removeLayerByLayer(remiClass)
								# logger
								cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								return "No"
						l = cfg.utls.addVectorLayer(reprjShapefile, cfg.osSCP.path.basename(reprjShapefile) , "ogr")
						
					if batch == "No":
						cfg.uiUtls.addProgressBar()
						# disable map canvas render for speed
						cfg.cnvs.setRenderFlag(False)
						cfg.QtGuiSCP.qApp.processEvents()
					# temp raster layer
					tRC= cfg.tmpDir + "/" + cfg.rclssTempNm + dT + ".tif"
				# error matrix
				eMN = dT + cfg.errMatrixNm
				cfg.reportPth = str(cfg.tmpDir + "/" + eMN)
				errorRstPath = rstrOut
				errorRstPath = errorRstPath.replace('\\', '/')
				errorRstPath = errorRstPath.replace('//', '/')
				tblOut = cfg.osSCP.path.dirname(errorRstPath) + "/" + cfg.osSCP.path.basename(errorRstPath)
				tblOut = cfg.osSCP.path.splitext(tblOut)[0] + ".csv"
				if unicode(errorRstPath).lower().endswith(".tif"):
					pass
				else:
					errorRstPath = errorRstPath + ".tif"
				cfg.uiUtls.updateBar(10)
				# if reference shapefile
				if l.type()== 0:
					if batch == "No":
						fd = cfg.ui.class_field_comboBox.currentText()
					else:
						fd = shapefileField
					if batch == "No":
						# convert reference layer to raster
						cfg.utls.vectorToRaster(fd, unicode(l.source()), classification, unicode(tRC))
					else:
						cfg.utls.vectorToRaster(fd, unicode(l.source()), classification, unicode(tRC), classification)
					referenceRaster = tRC
				# if reference raster
				elif l.type()== 1:
					if batch == "No":
						referenceRaster = l.source()
					else:
						referenceRaster = reference
				# open input with GDAL
				refRstrDt = cfg.gdalSCP.Open(unicode(referenceRaster), cfg.gdalSCP.GA_ReadOnly)
				newRstrDt = cfg.gdalSCP.Open(iClass.source(), cfg.gdalSCP.GA_ReadOnly)
				# combination finder
				# band list
				bLR = cfg.utls.readAllBandsFromRaster(refRstrDt)
				cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
				cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
				o = cfg.utls.processRaster(refRstrDt, bLR, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
				cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
				refRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)
				# band list
				bLN = cfg.utls.readAllBandsFromRaster(newRstrDt)
				cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
				cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
				o = cfg.utls.processRaster(newRstrDt, bLN, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
				for b in range(0, len(bLR)):
					bLR[b] = None
				refRstrDt = None
				for b in range(0, len(bLN)):
					bLN[b] = None
				newRstrDt = None		
				cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
				newRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)	
				cmb = list(cfg.itertoolsSCP.product(refRasterBandUniqueVal, newRasterBandUniqueVal))
				# error matrix
				col = []
				row = []
				cmbntns = {}
				# expression builder
				n = 1
				e = []
				for i in cmb:
					if str(i[0]) == "nan" or str(i[1]) == "nan" :
						pass
					else:
						e.append("cfg.np.where( (a == " + str(i[0]) + ") & (b == " + str(i[1]) + "), " + str(n) + ", 0)")
						cmbntns["combination_" + str(i[0]) + "_"+ str(i[1])] = n
						col.append(i[0])
						row.append(i[1])
						n = n + 1
				# virtual raster
				tPMN = cfg.tmpVrtNm + ".vrt"
				# date time for temp name
				dT = cfg.utls.getTime()
				tPMD = cfg.tmpDir + "/" + dT + tPMN
				tPMN2 = dT + cfg.calcRasterNm + ".tif"
				tPMD2 = cfg.tmpDir + "/" + tPMN2
				bList = [unicode(referenceRaster), iClass.source()]
				bandNumberList = [1, 1]
				vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", cfg.NoDataVal, 0, "No", "No")
				# open input with GDAL
				rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
				# output rasters
				oM = []
				oM.append(tPMD2)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# calculation
				variableList = [["im1", "a"], ["im2", "b"]]
				o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.bandCalculationMultipleWhere, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "No")
				if o == "No":
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr48()
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error")
					return "No"
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "accuracy raster output: " + unicode(rstrOut))
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				if cfg.rasterCompression != "No":
					try:
						cfg.utls.GDALCopyRaster(tPMD2, errorRstPath, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						cfg.osSCP.remove(tPMD2)
					except Exception, err:
						cfg.shutilSCP.copy(tPMD2, errorRstPath)
						cfg.osSCP.remove(tPMD2)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					cfg.shutilSCP.copy(tPMD2, errorRstPath)
					cfg.osSCP.remove(tPMD2)
				cfg.uiUtls.updateBar(80)
				cols = sorted(cfg.np.unique(col).tolist())
				rows = sorted(cfg.np.unique(row).tolist())
				totX = cols
				totX.extend(rows)
				total = sorted(cfg.np.unique(totX).tolist())
				errMatrix = cfg.np.zeros((len(total), len(total)))
				cList = "V_" + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Classification') + "\t"
				try:
					l = open(tblOut, 'w')
				except Exception, err:
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				t = cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'ErrMatrixCode') + "	" + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Reference') + "	" + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Classification') + "	" + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'PixelSum') + "\n"
				try:
					t = t.encode(cfg.sysSCP.getfilesystemencoding())
				except:
					pass
				l.write(t)
				# open error raster
				rDC = cfg.gdalSCP.Open(errorRstPath, cfg.gdalSCP.GA_ReadOnly)
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
				tStr = "\t" + "> " + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'ERROR MATRIX') + "\n"
				try:
					tStr = tStr.encode(cfg.sysSCP.getfilesystemencoding())
				except:
					pass
				l.write(tStr)
				tStr = "\t" + "> " + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Reference') + "\n"
				try:
					tStr = tStr.encode(cfg.sysSCP.getfilesystemencoding())
				except:
					pass
				l.write(tStr)
				tStr = cList + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Total') + "\n"
				try:
					tStr = tStr.encode(cfg.sysSCP.getfilesystemencoding())
				except:
					pass
				l.write(tStr)
				# temp matrix
				tmpMtrx= cfg.tmpDir + "/" + cfg.tempMtrxNm + dT + ".txt"
				cfg.np.savetxt(tmpMtrx, errMatrix, delimiter="\t", fmt="%i")
				tM = open(tmpMtrx, 'r')
				# write matrix
				ix = 0
				for j in tM:
					tMR = str(total[ix]) + "\t" + j.rstrip('\n') + "\t" + str(int(errMatrix[ix, :].sum())) + str("\n")
					l.write(tMR)
					ix = ix + 1
				# last line
				lL = cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Total')
				for c in range(0, len(total)):
					lL = lL + "\t" + str(int(errMatrix[:, c].sum()))
				totMat = int(errMatrix.sum())
				lL = lL + "\t" + str(totMat) + str("\n")
				try:
					lL = lL.encode(cfg.sysSCP.getfilesystemencoding())
				except:
					pass
				l.write(lL)
				l.write(str("\n"))
				# overall accuracy
				oA = 100 * errMatrix.trace() / totMat
				t = cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Overall accuracy [%] = ') + str(oA) + "\n"
				try:
					t = t.encode(cfg.sysSCP.getfilesystemencoding())
				except:
					pass
				l.write(t)
				# user and producer's accuracy and kappa hat, equations from Congalton, R. & Green, K. (2009) Assessing the Accuracy of Remotely Sensed Data: Principles and Practices. CRC Press
				nipXnpi = 0
				niiTot = 0
				for g in range(0, len(total)):
					nii = errMatrix[g,g]
					niiTot = niiTot + nii
					nip = errMatrix[g, :].sum()
					npi = errMatrix[:, g].sum()
					nipXnpi = nipXnpi + (nip * npi)
					p = 100 * nii / npi
					u = 100 * nii / nip
					khatI = ((totMat * nii) - (nip * npi)) / ((totMat * nip) - (nip * npi))
					t = cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Class ') + str(total[g]) + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", ' producer accuracy [%] = ') + str(p) + "\t" + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", ' user accuracy [%] = ') + str(u) + "\t" + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Kappa hat = ') + str(khatI) + str("\n")
					try:
						t = t.encode(cfg.sysSCP.getfilesystemencoding())
					except:
						pass
					l.write(t)
				khat = ((totMat * niiTot) - nipXnpi) / ((totMat * totMat) - nipXnpi)
				t = cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'Kappa hat classification = ') + str(khat) + str("\n")
				try:
					t = t.encode(cfg.sysSCP.getfilesystemencoding())
				except:
					pass
				l.write(t)
				l.close()
				# close bands
				for b in range(0, len(bLC)):
					bLC[b] = None
				rDC = None
				# add raster to layers
				cfg.iface.addRasterLayer(unicode(errorRstPath), unicode(cfg.osSCP.path.basename(errorRstPath)))
				rstr = cfg.utls.selectLayerbyName(unicode(cfg.osSCP.path.basename(errorRstPath)), "Yes")
				cfg.utls.rasterSymbolGeneric(rstr, "NoData")	
				try:
					f = open(tblOut)
					if cfg.osSCP.path.isfile(tblOut):
						eM = f.read()
						cfg.ui.error_matrix_textBrowser.setText(eM)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " error matrix calculated")
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.uiUtls.updateBar(100)
				if batch == "No":
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
				else:
					# remove temp layers
					cfg.utls.removeLayerByLayer(reml)
					cfg.utls.removeLayerByLayer(remiClass)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "finished")
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
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layer name: " + unicode(cfg.referenceLayer))
	
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
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layers refreshed")
