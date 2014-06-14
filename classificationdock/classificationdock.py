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
		copyright			: (C) 2012 by Luca Congedo
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
# for debugging
import inspect
# for moving files
import shutil
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qgis.utils as qgisUtils
from osgeo import gdal
from osgeo import ogr 
from osgeo import osr
from osgeo.gdalconst import *
import xml.etree.cElementTree as ET
from xml.dom import minidom
import SemiAutomaticClassificationPlugin.core.config as cfg
try:
	from scipy.ndimage import label
	cfg.scipyCheck = "Yes"
except:
	cfg.scipyCheck = "No"

class ClassificationDock:

	def __init__(self):
		# rubber band
		cfg.rbbrBnd = QgsRubberBand(cfg.cnvs)
		cfg.rbbrBnd.setColor(QColor(0,255,255))
		cfg.rbbrBnd.setWidth(2)
		# emit a QgsPoint on each click
		self.clickPreview = QgsMapToolEmitPoint(cfg.cnvs)
		# connect to pointerClick when map is clicked
		self.clickPreview.canvasClicked.connect(self.pointerClickPreview)
		
	# set algorithm
	def algorithmName(self):
		cfg.algName = str(cfg.uidc.algorithm_combo.currentText())
		if str(cfg.algName) == cfg.algML:
			if cfg.algThrshld > 100:
				cfg.mx.msg10()
				cfg.uidc.alg_threshold_SpinBox.setValue(100)
		elif str(cfg.algName) == cfg.algSAM:
			if cfg.algThrshld > 90:
				cfg.mx.msg11()
				cfg.uidc.alg_threshold_SpinBox.setValue(90)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "training name: " + str(cfg.algName))
				
	# set algorithm threshold
	def algorithmThreshold(self):
		cfg.algThrshld = cfg.uidc.alg_threshold_SpinBox.value()
		if str(cfg.algName) == cfg.algML:
			if cfg.algThrshld > 100:
				cfg.uidc.alg_threshold_SpinBox.setValue(100)
		elif str(cfg.algName) == cfg.algSAM:
			if cfg.algThrshld > 90:
				cfg.uidc.alg_threshold_SpinBox.setValue(90)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithm threshold: " + str(cfg.algThrshld))
		
	# Apply qml style to classifications and previews
	def applyQmlStyle(self, classLayer, stylePath):
		# read path from project istance
		p = QgsProject.instance()
		cfg.qmlFl = p.readEntry("SemiAutomaticClassificationPlugin", "qmlfile", "")[0]
		classLayer.loadNamedStyle(cfg.qmlFl) 
		# refresh legend
		if hasattr(classLayer, "setCacheImage"):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(classLayer)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification symbology applied with qml: " + str(stylePath))
			
	# create classification preview
	def createPreview(self, point):
		if cfg.imgNm is None:
			cfg.mx.msg4()
			cfg.pntPrvw = None
		# check if image is None
		elif cfg.utls.selectLayerbyName(cfg.imgNm) is None:
			# if band set then pass
			if cfg.imgNm == cfg.bndSetNm:
				pass
			else:
				cfg.mx.msg4()
				cfg.ipt.refreshRasterLayer()
				cfg.pntPrvw = None
		if cfg.pntPrvw != None:
			cfg.uiUtls.addProgressBar()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> PREVIEW click")
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			cfg.uiUtls.updateBar(10)
			# date time for temp name
			dT = cfg.utls.getTime()
			# temp files
			tPMN = dT + cfg.algRasterNm + ".tif"
			tPMD = cfg.tmpDir + "/" + tPMN
			# preview name and path
			pN =  dT + cfg.prvwTempNm
			pP = cfg.tmpDir + "/" + pN
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "point (X,Y) = (%s,%s)" % (cfg.pntPrvw.x() , cfg.pntPrvw.y()))
			# signature list
			sL = self.getSignatureList()
			# input image
			if cfg.actionCheck == "Yes" and  self.trainSigCheck == "Yes":
				# check band set
				ckB = "Yes"
				if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
					ckB = self.checkBandSet()
				if ckB == "Yes":
					cfg.uiUtls.updateBar(20)
					ok, opOut, mOut = self.runAlgorithm(cfg.algName, cfg.imgNm, sL, pP, cfg.macroclassCheck, None, int(cfg.prvwSz), point)
					if ok == "Yes":
						r = cfg.iface.addRasterLayer(pP, os.path.basename(str(pP)))
						cfg.uiUtls.updateBar(80)
						# apply symbology
						self.applyClassSymbology(r, cfg.macroclassCheck, cfg.qmlFl, sL)
						# move to group
						g = cfg.utls.groupIndex(cfg.grpNm)
						if g is None:
							g = cfg.lgnd.addGroup(cfg.grpNm, False) 
							cfg.lgnd.moveLayer (r, g)
						else:
							cfg.lgnd.moveLayer (r, g)
					cfg.uiUtls.updateBar(100)
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< PREVIEW created: " + str(dT + pN))
					# enable Redo button
					cfg.uidc.redo_Preview_Button.setEnabled(True)
			else:
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "preview no")	
			
			
	def getSignatureList(self):
		id = cfg.signIDs.values()
		signatureList = []
		for i in id:
			if cfg.signList["CHECKBOX_" + str(i)] == 2:
				s = []
				s.append(cfg.signList["MACROCLASSID_" + str(i)])
				s.append(cfg.signList["MACROCLASSINFO_" + str(i)])
				s.append(cfg.signList["CLASSID_" + str(i)])
				s.append(cfg.signList["CLASSINFO_" + str(i)])
				s.append(cfg.signList["VALUES_" + str(i)])
				s.append(cfg.signList["WAVELENGTH_" + str(i)])
				s.append(cfg.signList["COLOR_" + str(i)])
				s.append(cfg.signList["COVMATRIX_" + str(i)])
				if len(cfg.signList["WAVELENGTH_" + str(i)]) == len(cfg.bndSetWvLn.values()):
					if str(sorted(cfg.signList["WAVELENGTH_" + str(i)])) != str(sorted(cfg.bndSetWvLn.values())):
						cfg.mx.msgWar9(cfg.signList["MACROCLASSID_" + str(i)], cfg.signList["CLASSID_" + str(i)])
					# check if signature has covariance matrix if maximum likelihood
					if cfg.algName == cfg.algML:
						if cfg.signList["COVMATRIX_" + str(i)] == "No":
							cfg.mx.msgWar10(cfg.signList["MACROCLASSID_" + str(i)], cfg.signList["CLASSID_" + str(i)])
						else:
							signatureList.append(s)
					else:
						signatureList.append(s)
				else:
					cfg.mx.msgErr24(cfg.signList["MACROCLASSID_" + str(i)], cfg.signList["CLASSID_" + str(i)])
					self.trainSigCheck = "No"
					return None
		if len(signatureList) > 0:
			self.trainSigCheck = "Yes"
		else:
			self.trainSigCheck = "No"
		return signatureList
			
	# check band set and create band set list
	def checkBandSet(self):
		ck = "Yes"
		# list of bands for algorithm
		cfg.bndSetLst = []
		for x in range(0, len(cfg.bndSet)):
			b = cfg.utls.selectLayerbyName(cfg.bndSet[x])
			if b is not None:
				cfg.bndSetLst.append(b.source())
			else:
				ck = "No"
		return ck
			
	# set variable for macroclass classification
	def macroclassCheckbox(self):
		q = QSettings()
		if cfg.uidc.macroclass_checkBox.isChecked() is True:
			q.setValue(cfg.regConsiderMacroclass, "Yes")
		else:
			q.setValue(cfg.regConsiderMacroclass, "No")
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.macroclassCheck))
		cfg.macroclassCheck = q.value(cfg.regConsiderMacroclass, "No")
			
	# set variable for mask
	def maskCheckbox(self):
		if cfg.uidc.mask_checkBox.isChecked() is True:
			m = QFileDialog.getOpenFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Select a mask shapefile"), "", "Shapefile (*.shp)")
			if len(m) > 0:
				cfg.mskFlPath = m
				cfg.uidc.mask_lineEdit.setText(unicode(cfg.mskFlPath))
				cfg.mskFlState = 2
			else:
				cfg.mskFlState = 2
				if len(cfg.uidc.mask_lineEdit.text()) == 0:
					cfg.uidc.mask_checkBox.setCheckState(0)
		else:
			cfg.mskFlState = 0
		cfg.utls.writeProjectVariable("maskFilePath", unicode(cfg.mskFlPath))	
		cfg.utls.writeProjectVariable("maskFileState", unicode(cfg.mskFlState))	
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.mskFlState))
		
	# Reset mask path
	def resetMask(self):
		p = QgsProject.instance()
		cfg.mskFlPath = ""
		cfg.mskFlState = 0
		cfg.utls.writeProjectVariable("maskFilePath", unicode(cfg.mskFlPath))	
		cfg.utls.writeProjectVariable("maskFileState", unicode(cfg.mskFlState))	
		cfg.uidc.mask_lineEdit.setText(str(cfg.mskFlPath))
		self.setMaskCheckbox()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reset mask")
		
	def setMaskCheckbox(self):	
		cfg.uidc.mask_checkBox.blockSignals(True)
		cfg.uidc.mask_checkBox.setCheckState(int(cfg.mskFlState))
		cfg.uidc.mask_checkBox.blockSignals(False)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "mask checkbox")
		
	def pointerClickPreview(self, point):
		# check if other processes are active
		if cfg.actionCheck == "No":
			cfg.utls.checkPointImage(cfg.imgNm, point)
			if cfg.pntCheck == "Yes":
				cfg.pntPrvw = cfg.lstPnt
				self.createPreview(cfg.pntPrvw)
		
	# Activate pointer for classification preview
	def pointerPreviewActive(self):
		cfg.cnvs.setMapTool(self.clickPreview)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: preview")
		
	# set preview size
	def previewSize(self):
		cfg.prvwSz = cfg.uidc.preview_size_spinBox.value()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "preview size: " + str(cfg.prvwSz))
		
	# redo preview
	def redoPreview(self):
		# check if other processes are active
		if cfg.actionCheck == "No":
			if cfg.pntPrvw is None:
				pass
			else:
				self.createPreview(cfg.pntPrvw)
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "REDO Preview")
		
	# set variable for report
	def reportCheckbox(self):
		if cfg.uidc.report_checkBox.isChecked() is True:
			cfg.reportCheck = "Yes"
		else:
			cfg.reportCheck = "No"
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.reportCheck))
		
	# Reset qml style path
	def resetQmlStyle(self):
		p = QgsProject.instance()
		p.writeEntry("SemiAutomaticClassificationPlugin", "qmlfile", "")
		cfg.uidc.qml_lineEdit.setText("")
		cfg.qmlFl = ""
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reset qml")
		
	# run classification algorithm
	def runAlgorithm(self, algorithmName, imageName, signatureList, outputRasterPath, macroclassCheck = "No", algRasterPath = None, previewSize = 0, previewPoint = None):
		# if band set
		if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
			# if masked bandset
			if imageName == cfg.maskRasterNm:
				bS = cfg.bndSetMaskList
			else:
				bS = cfg.bndSetLst
			# open input with GDAL
			bL = []
			for i in range(0, len(bS)):
				rD = gdal.Open(unicode(bS[i]), GA_ReadOnly)
				bL.append(rD)
		else:
			# if masked raster
			if imageName == cfg.maskRasterNm:
				iR = cfg.maskRstSrc
			else:
				r = cfg.utls.selectLayerbyName(imageName)
				iR = r.source()
			# open input with GDAL
			rD = gdal.Open(iR, GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
		if rD is not None:
			# signature rasters
			oRL, opOut = cfg.utls.createSignatureClassRaster(signatureList, rD, cfg.tmpDir, cfg.NoDataVal, None, previewSize, previewPoint)
			# output rasters
			oM = []
			oC = []
			if algRasterPath is not None:
				oM.append(algRasterPath)
			else:
				# date time for temp name
				dT = cfg.utls.getTime()
				# temp files
				tPMN = dT + cfg.algRasterNm + ".tif"
				tPMD = cfg.tmpDir + "/" + tPMN
				oM.append(tPMD)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", GDT_Float64, previewSize, previewPoint)
			oC.append(outputRasterPath)
			oCR = cfg.utls.createRasterFromReference(rD, 1, oC, cfg.NoDataVal, "GTiff", GDT_Int32, previewSize, previewPoint)
			o = cfg.utls.processRaster(rD, bL, signatureList, None, cfg.utls.classification, algorithmName, oRL, oMR[0], oCR[0], previewSize, previewPoint, cfg.NoDataVal, macroclassCheck)
			# close GDAL rasters
			for x in range(0, len(oRL)):
				oRL[x] = None
			for x in range(0, len(oCR)):
				oCR[x] = None
			for x in range(0, len(bL)):
				bL[x] = None
			cfg.utls.createRasterTable(outputRasterPath, 1, signatureList)
			return "Yes", opOut, tPMD
		else:
			cfg.mx.msgErr25()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " error raster")
			return "No", None, None
			
	# select all signatures
	def selectAllSignatures(self):
		try:
			cfg.uiUtls.addProgressBar()
			# select all
			if cfg.allSignCheck == "Yes":
				cfg.utls.allItemsSetState(cfg.uidc.signature_list_tableWidget, 2)
				# set check all plot
				cfg.allSignCheck = "No"
			# unselect all if previously selected all
			elif cfg.allSignCheck == "No":
				cfg.utls.allItemsSetState(cfg.uidc.signature_list_tableWidget, 0)
				# set check all plot
				cfg.allSignCheck = "Yes"
			cfg.uiUtls.removeProgressBar()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all signatures")
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.removeProgressBar()

	# perform classification
	def runClassification(self):
		clssOut = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save classification output"), "", "Image (*.tif)")
		if len(clssOut) > 0:
			clssOut = clssOut.replace('\\', '/')
			clssOut = clssOut.replace('//', '/')
			cfg.clssPth = clssOut
		qApp.processEvents()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification output: " + str(cfg.clssPth))	
		# check if can run classification
		ckC = "Yes"
		if cfg.imgNm is None:
			cfg.mx.msg4()
			ckC = "No"
		elif cfg.clssPth is None:
			cfg.mx.msg12()
			ckC = "No"
		# check if image is None
		elif cfg.utls.selectLayerbyName(cfg.imgNm) is None:
			# if band set then pass
			if cfg.imgNm != cfg.bndSetNm:
				cfg.mx.msg4()
				cfg.ipt.refreshRasterLayer()
				ckC = "No"
		if ckC != "No":
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> CLASSIFICATION STARTED")
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			# base name
			n = os.path.basename(cfg.clssPth)
			nm = os.path.splitext(n)[0]
			sL = self.getSignatureList()
			if self.trainSigCheck == "Yes":
				cfg.uiUtls.addProgressBar()
				# check band set
				ckB = "Yes"
				if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
					ckB = self.checkBandSet()
				# date time for temp name
				dT = cfg.utls.getTime()
				cfg.uiUtls.updateBar(10)
				if ckB == "Yes":
					cfg.bndSetMaskList = []
					img = cfg.imgNm
				### if mask
					if cfg.mskFlState == 2:
						# mask shapefile path
						m = cfg.uidc.mask_lineEdit.text()
						dT = cfg.utls.getTime()
						tCN = dT + cfg.maskRasterNm
						# apply mask
						if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
							for x in range(0, len(cfg.bndSetLst)):
								tCD = cfg.tmpDir + "/" + str(x) + tCN 
								cfg.bndSetMaskList.append(tCD)
								cfg.utls.clipRasterByShapefile(m, cfg.bndSetLst[x], str(tCD))
						else:
							# temp masked raster
							cfg.maskRstSrc = cfg.tmpDir + "/" + tCN 
							cfg.utls.clipRasterByShapefile(m, cfg.imgSrc, str(cfg.maskRstSrc))
						img = cfg.maskRasterNm
				### if not mask
					cfg.uiUtls.updateBar(20)
					ok, opOut, mOut = self.runAlgorithm(cfg.algName, img, sL, cfg.clssPth, cfg.macroclassCheck)
					if ok == "Yes":
						c = cfg.iface.addRasterLayer(cfg.clssPth, os.path.basename(unicode(cfg.clssPth)))
						cfg.uiUtls.updateBar(80)
						# apply symbology
						self.applyClassSymbology(c, cfg.macroclassCheck, cfg.qmlFl, sL)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< CLASSIFICATION PERFORMED: " + str(cfg.clssPth))
				### calculate report
					if cfg.reportCheck == "Yes":
						cfg.classRep.calculateClassificationReport(cfg.clssPth, 0)
						reportOut = os.path.dirname(cfg.clssPth) + "/" + nm + cfg.reportNm
						try:
							shutil.copy(cfg.reportPth, reportOut)
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							cfg.mx.msg7()
				### convert classification to vector
					cfg.uiUtls.updateBar(85)
					if cfg.vectorOutputCheck == "Yes":
						vO = os.path.dirname(cfg.clssPth) + "/" + nm + ".shp"
						cfg.utls.rasterToVector(cfg.clssPth, vO)
						vl = cfg.utls.addVectorLayer(str(vO), os.path.basename(vO), "ogr")
						cfg.utls.vectorSymbol(vl, sL, cfg.macroclassCheck)
						cfg.utls.addLayerToMap(vl)
					cfg.uiUtls.updateBar(95)
				### copy signature raster
					if cfg.algFilesCheck == "Yes":
						rOBaseNm = os.path.dirname(cfg.clssPth)
						try:
							for r in opOut:
								rNm = os.path.basename(r)[:7]
								bNm = nm + "_" + rNm + ".tif"
								shutil.copy(r, rOBaseNm + "/" + bNm)
								c = cfg.iface.addRasterLayer(rOBaseNm + "/" + bNm, bNm)
							mOutNm = nm + "_" + cfg.algRasterNm + ".tif"
							shutil.copy(mOut, rOBaseNm + "/" + mOutNm)
							c = cfg.iface.addRasterLayer(rOBaseNm + "/" + mOutNm, mOutNm)
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files copied")
						except Exception, err:
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							cfg.mx.msgErr23()
				### ending
					cfg.uiUtls.updateBar(100)
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.clssPth = None
			### band set check failed
				else:
					cfg.mx.msgErr6()
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
					cfg.clssPth = None
					cfg.bst.rasterBandName()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "band set check failed")
			else:
				cfg.cnvs.setRenderFlag(True)
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification no")	
			
	# apply symbology to classification			
	def applyClassSymbology(self, classificationRaster, macroclassCheck, qmlFile, signatureList = None):
		# qml symbology
		if qmlFile == "":
			cfg.utls.rasterSymbol(classificationRaster, signatureList, macroclassCheck)
		else:
			try:
				self.applyQmlStyle(classificationRaster, qmlFile)
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							
	# Select qml style for classifications and previews
	def selectQmlStyle(self):
		cfg.qmlFl = QFileDialog.getOpenFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Select a qml style"), "", "Style (*.qml)")
		# write path to project istance
		p = QgsProject.instance()
		p.writeEntry("SemiAutomaticClassificationPlugin", "qmlfile", cfg.qmlFl)
		cfg.uidc.qml_lineEdit.setText(cfg.qmlFl)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "qml file: " + str(cfg.qmlFl))

	def editedCell(self, row, column):
		if cfg.SigTabEdited == "Yes":
			tW = cfg.uidc.signature_list_tableWidget
			id = tW.item(row, 6).text()
			if column == 0:
				cfg.signList["CHECKBOX_" + str(id)] = tW.item(row, 0).checkState()
			else:
				try:
					cfg.signList["MACROCLASSID_" + str(id)] = int(tW.item(row, 1).text())
				except:
					tW.setItem(row, column, QTableWidgetItem(str(cfg.signList["MACROCLASSID_" + str(id)])))
				cfg.signList["MACROCLASSINFO_" + str(id)] = tW.item(row, 2).text()
				try:
					cfg.signList["CLASSID_" + str(id)] = int(tW.item(row, 3).text())
				except:
					tW.setItem(row, column, QTableWidgetItem(str(cfg.signList["CLASSID_" + str(id)])))
				cfg.signList["CLASSINFO_" + str(id)] = tW.item(row, 4).text()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "edited cell" + str(row) + ";" + str(column))

	# export band set to file
	def saveSignatureList(self, signatureFile):
		try:
			root = ET.Element("signaturelist")
			for k in cfg.signIDs.values():
				sigItem = ET.SubElement(root, "signature")
				sigItem.set("ID", str(cfg.signIDs["ID_" + str(k)]))
				mcIDField = ET.SubElement(sigItem, "MACROCLASSID")
				mcIDField.text = str(cfg.signList["MACROCLASSID_" + str(k)])
				mcInfoField = ET.SubElement(sigItem, "MACROCLASSINFO")
				mcInfoField.text = str(cfg.signList["MACROCLASSINFO_" + str(k)])
				cIDField = ET.SubElement(sigItem, "CLASSID")
				cIDField.text = str(cfg.signList["CLASSID_" + str(k)])
				cInfoField = ET.SubElement(sigItem, "CLASSINFO")
				cInfoField.text = str(cfg.signList["CLASSINFO_" + str(k)])
				wvLngField = ET.SubElement(sigItem, "VALUES")
				wvLngField.text = str(cfg.signList["VALUES_" + str(k)])
				wvLngField = ET.SubElement(sigItem, "WAVELENGTH")
				wvLngField.text = str(cfg.signList["WAVELENGTH_" + str(k)])
				unitField = ET.SubElement(sigItem, "WAVELENGTH_UNIT")
				unitField.text = str(cfg.signList["UNIT_" + str(k)])
				colorField = ET.SubElement(sigItem, "COLOR")
				colorField.text = str(cfg.signList["COLOR_" + str(k)].toRgb().name())
				covMatrField = ET.SubElement(sigItem, "COVARIANCE_MATRIX")
				covMatrField.text = str(cfg.utls.covarianceMatrixToList(cfg.signList["COVMATRIX_" + str(k)]))
			o = open(signatureFile, 'w')
			f = minidom.parseString(ET.tostring(root)).toprettyxml()
			o.write(f)
			o.close()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures saved in: " + str(signatureFile))
		except Exception, err:
			cfg.mx.msgErr15()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	def openSignatureList(self):
		signFile = QFileDialog.getOpenFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Select a signature list file"), "", "XML (*.xml)")
		if len(signFile) > 0:
			cfg.uidc.signatureFile_lineEdit.setText(unicode(signFile))
			self.openSignatureListFile(signFile)
			cfg.utls.writeProjectVariable("signatureFilePath", unicode(signFile))
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures opened: " + str(signFile))
			
	def importSignatureList(self):
		try:
			if cfg.bndSetUnit["UNIT"] != cfg.noUnit:
				signFile = QFileDialog.getOpenFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Select a signature list file"), "", "XML (*.xml)")
				if len(signFile) > 0:
					self.openSignatureListFile(signFile, "Yes")
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures imported: " + str(signFile))
			else:
				cfg.mx.msgWar8()
		except Exception, err:
			cfg.mx.msgWar8()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
	# open signature file
	def openSignatureListFile(self, signatureFile, addToSignature = "No"):
		try:
			tree = ET.parse(signatureFile)
			root = tree.getroot()
			if addToSignature == "No":
				cfg.signList = {}
				cfg.signIDs = {}
			for child in root:
				if len(cfg.signIDs) > 0:
					b = cfg.ROId.signatureID()
				else:
					b = int(child.get("ID"))
				cfg.signList["MACROCLASSID_" + str(b)] = str(child.find("MACROCLASSID").text)
				cfg.signList["MACROCLASSINFO_" + str(b)] = str(child.find("MACROCLASSINFO").text)
				cfg.signList["CLASSID_" + str(b)] = str(child.find("CLASSID").text)
				cfg.signList["CLASSINFO_" + str(b)] = str(child.find("CLASSINFO").text)
				cfg.signList["UNIT_" + str(b)] = str(child.find("WAVELENGTH_UNIT").text)
				cfg.signIDs["ID_" + str(b)] = b
				# get values
				vls = str(child.find("VALUES").text)
				x = eval(vls)
				cfg.signList["VALUES_" + str(b)] = x
				cfg.signList["WAVELENGTH_" + str(b)] = eval(str(child.find("WAVELENGTH").text))
				cfg.signList["CHECKBOX_" + str(b)] = 2
				c = QColor()
				c.setNamedColor(str(child.find("COLOR").text))
				cfg.signList["COLOR_" + str(b)] = c
				# get covariance matrix
				mt = str(child.find("COVARIANCE_MATRIX").text)
				try:
					cm = eval(mt)
				except:
					cm = "No"
				cfg.signList["COVMATRIX_" + str(b)] = cfg.utls.listToCovarianceMatrix(cm)
			self.signatureListTable(cfg.uidc.signature_list_tableWidget)
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " opened signature " + str(len(cfg.signIDs)))
		except Exception, err:
			self.signatureListTable(cfg.uidc.signature_list_tableWidget)
			cfg.mx.msgErr16()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
	# export band set to file
	def exportSignatureFile(self):
		signFile = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Export the signature list to file"), "", "XML (*.xml)")
		if len(signFile) > 0:
			self.saveSignatureList(signFile)
		return signFile
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures exported in: " + str(signFile))
			
	# export band set to file
	def saveSignatureListToFile(self):
		try:
			signFile = cfg.uidc.signatureFile_lineEdit.text()
			if len(signFile) > 0:
				self.saveSignatureList(signFile)
			elif len(signFile) == 0:
				signFile = self.exportSignatureFile()
				cfg.uidc.signatureFile_lineEdit.setText(unicode(signFile))
				cfg.utls.writeProjectVariable("signatureFilePath", unicode(signFile))
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures saved in: " + str(signFile))
		except Exception, err:
			cfg.uidc.signatureFile_lineEdit.setText("")
			cfg.mx.msgErr15()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# open signature file
	def openLibraryFile(self, libraryFile):
		try:
			if cfg.bndSetUnit["UNIT"] != cfg.noUnit:
				libFile = QFileDialog.getOpenFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Select a library file"), "", "USGS library (*.asc);;ASTER library (*.txt);;CSV (*.csv)")
				if len(libFile) > 0:
					cfg.uiUtls.addProgressBar()
					if libFile.endswith(".asc"):
						cfg.sigImport.USGSLibrary(libFile)
					elif libFile.endswith(".txt"):
						cfg.sigImport.ASTERLibrary(libFile)
					elif libFile.endswith(".csv"):
						cfg.sigImport.CSVLibrary(libFile)
					cfg.uiUtls.removeProgressBar()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library " + str(libFile))
			else:
				cfg.mx.msgWar8()
		except Exception, err:
			cfg.mx.msgWar8()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# export signatures to CSV library
	def exportToCSVLibrary(self):
		d = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Export the highlighted signatures to CSV library"))
		if len(d) > 0:
			tW = cfg.uidc.signature_list_tableWidget
			r = []
			for i in tW.selectedIndexes():
				r.append(i.row())
			v = list(set(r))
			for b in v:
				mID = tW.item(b, 1).text()
				mC = tW.item(b, 2).text()
				cID = tW.item(b, 3).text()
				c = tW.item(b, 4).text()
				signFile = d + "/" + str(mC) + str(mID) + "_" + str(c) + str(cID) + str(".csv")
				# open file
				l = open(signFile, 'w')
				try:
					l.write("wavelength;reflectance;standardDeviation;waveLengthUnit \n")
					l.close()
				except Exception, err:
					cfg.mx.msgErr18()
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				id = tW.item(b, 6).text()
				u = str(cfg.signList["UNIT_" + str(id)])
				# wavelength
				a = str(cfg.signList["WAVELENGTH_" + str(id)])
				wlg = eval(a)
				# signature values
				n = str(cfg.signList["VALUES_" + str(id)])
				val = eval(n)
				# open file
				l = open(signFile, 'a')
				for k in range(0, len(wlg)):
					wl = wlg[k]
					vl = val[k*2]
					sD = val[k*2 + 1]
					line = str(wl) + ";" + str(vl) + ";" + str(sD) + ";" + str(u) + "\n"
					try:
						l.write(line)
					except Exception, err:
						cfg.mx.msgErr18()
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				l.close()
		
	def signatureListDoubleClick(self, index):
		if index.column() == 5:
			c = cfg.utls.selectColor()
			if c is not None:
				k = cfg.uidc.signature_list_tableWidget.item(index.row(), 6).text()
				cfg.signList["COLOR_" + str(k)] = c
				cfg.uidc.signature_list_tableWidget.item(index.row(), 5).setBackground(c)
		else:
			self.selectAllSignatures()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures index: " + str(index))
		
	# Create signature list for classification
	def signatureListTable(self, table):
		# checklist
		l = table
		l.setSortingEnabled(False)
		cfg.utls.clearTable(l)
		# add signature items
		x = 0
		for k in cfg.signIDs.values():
			cfg.SigTabEdited = "No"
			l.insertRow(x)
			l.setRowHeight(x, 20)
			cb = QTableWidgetItem("checkbox")
			cb.setCheckState(cfg.signList["CHECKBOX_" + str(k)])
			l.setItem(x, 0, cb)
			itMID = QTableWidgetItem()
			itMID.setData(Qt.DisplayRole, int(cfg.signList["MACROCLASSID_" + str(k)]))
			l.setItem(x, 1, itMID)
			l.setItem(x, 2, QTableWidgetItem(str(cfg.signList["MACROCLASSINFO_" + str(k)])))
			itID = QTableWidgetItem()
			itID.setData(Qt.DisplayRole, int(cfg.signList["CLASSID_" + str(k)]))
			l.setItem(x, 3, itID)
			l.setItem(x, 4, QTableWidgetItem(str(cfg.signList["CLASSINFO_" + str(k)])))
			l.setItem(x, 5, QTableWidgetItem(""))
			c = cfg.signList["COLOR_" + str(k)]
			l.item(x, 5).setBackground(c)
			l.setItem(x, 6, QTableWidgetItem(str(cfg.signIDs["ID_" + str(k)])))
			x = x + 1
		l.show()
		l.setColumnWidth(0, 30)
		l.setColumnWidth(1, 40)
		l.setColumnWidth(3, 40)
		l.setColumnWidth(5, 30)
		l.setSortingEnabled(True)
		cfg.SigTabEdited = "Yes"
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " roi list table created")
		
	def removeSelectedSignatures(self):
		# ask for confirm
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Delete signatures"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to delete highlighted signatures?"))
		if a == "Yes":
			tW = cfg.uidc.signature_list_tableWidget
			r = []
			for i in tW.selectedIndexes():
				r.append(i.row())
			v = list(set(r))
			for x in v:
				id = tW.item(x, 6).text()
				cfg.signIDs.pop("ID_" + str(id))
				cfg.signList.pop("MACROCLASSID_" + str(id))
				cfg.signList.pop("MACROCLASSINFO_" + str(id))
				cfg.signList.pop("CLASSID_" + str(id))
				cfg.signList.pop("CLASSINFO_" + str(id))
				cfg.signList.pop("WAVELENGTH_" + str(id))
				cfg.signList.pop("VALUES_" + str(id))
				cfg.signList.pop("COLOR_" + str(id))
				cfg.signList.pop("UNIT_" + str(id))
				cfg.signList.pop("COVMATRIX_" + str(id))
			self.signatureListTable(cfg.uidc.signature_list_tableWidget)
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " removed signatures: " + str(v))
		
	# set variable for vector classification
	def vectorCheckbox(self):
		if cfg.uidc.vector_output_checkBox.isChecked() is True:
			cfg.vectorOutputCheck = "Yes"
		else:
			cfg.vectorOutputCheck = "No"
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.vectorOutputCheck))

	# add signatures to spectral plot
	def addSignatureToSpectralPlot(self):
		tW = cfg.uidc.signature_list_tableWidget
		r = []
		for i in tW.selectedIndexes():
			r.append(i.row())
		v = list(set(r))
		for x in v:
			b = cfg.spSigPlot.signaturePlotID()
			id = tW.item(x, 6).text()
			cfg.signPlotIDs["ID_" + str(b)] = b
			cfg.spectrPlotList["MACROCLASSID_" + str(b)] = cfg.signList["MACROCLASSID_" + str(id)]
			cfg.spectrPlotList["MACROCLASSINFO_" + str(b)] = cfg.signList["MACROCLASSINFO_" + str(id)]
			cfg.spectrPlotList["CLASSID_" + str(b)] = cfg.signList["CLASSID_" + str(id)]
			cfg.spectrPlotList["CLASSINFO_" + str(b)] = cfg.signList["CLASSINFO_" + str(id)]
			cfg.spectrPlotList["VALUES_" + str(b)] = cfg.signList["VALUES_" + str(id)]
			cfg.spectrPlotList["WAVELENGTH_" + str(b)] = cfg.signList["WAVELENGTH_" + str(id)]
			cfg.spectrPlotList["COLOR_" + str(b)] = cfg.signList["COLOR_" + str(id)]
			cfg.spectrPlotList["CHECKBOX_" + str(b)] = 2
			cfg.spectrPlotList["UNIT_" + str(b)] = cfg.signList["UNIT_" + str(id)] 
		cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
		cfg.spectralplotdlg.close()
		cfg.spectralplotdlg.show()
		