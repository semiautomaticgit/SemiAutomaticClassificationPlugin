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

class ClassificationDock:

	def __init__(self):
		# rubber band
		cfg.rbbrBnd = QgsRubberBand(cfg.cnvs)
		cfg.rbbrBnd.setColor(cfg.QtGuiSCP.QColor(0,255,255))
		cfg.rbbrBnd.setWidth(2)
		# emit a QgsPoint on each click
		#self.clickPreview = QgsMapToolEmitPoint(cfg.cnvs)
		# connect to pointerClick when map is clicked
		#self.clickPreview.canvasClicked.connect(self.pointerClickPreview)
		
	# set algorithm
	def algorithmName(self):
		cfg.algName = cfg.uidc.algorithm_combo.currentText()
		if unicode(cfg.algName) == cfg.algML:
			if cfg.algThrshld > 100:
				cfg.mx.msg10()
				cfg.uidc.alg_threshold_SpinBox.setValue(100)
		elif unicode(cfg.algName) == cfg.algSAM:
			if cfg.algThrshld > 90:
				cfg.mx.msg11()
				cfg.uidc.alg_threshold_SpinBox.setValue(90)
		cfg.utls.writeProjectVariable("ClassAlgorithm", unicode(cfg.algName))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "training name: " + unicode(cfg.algName))
				
	# set algorithm threshold
	def algorithmThreshold(self):
		cfg.algThrshld = cfg.uidc.alg_threshold_SpinBox.value()
		if unicode(cfg.algName) == cfg.algML:
			if cfg.algThrshld > 100:
				cfg.uidc.alg_threshold_SpinBox.setValue(100)
		elif unicode(cfg.algName) == cfg.algSAM:
			if cfg.algThrshld > 90:
				cfg.uidc.alg_threshold_SpinBox.setValue(90)
		cfg.algThrshld = cfg.uidc.alg_threshold_SpinBox.value()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithm threshold: " + str(cfg.algThrshld))
		
	# Apply qml style to classifications and previews
	def applyQmlStyle(self, classLayer, stylePath):
		# read path from project istance
		p = cfg.qgisCoreSCP.QgsProject.instance()
		cfg.qmlFl = p.readEntry("SemiAutomaticClassificationPlugin", "qmlfile", "")[0]
		classLayer.loadNamedStyle(cfg.qmlFl) 
		# refresh legend
		if hasattr(classLayer, "setCacheImage"):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(classLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification symbology applied with qml: " + unicode(stylePath))
			
	# set preview transparency
	def changePreviewTransparency(self, value):
		try:
			l = cfg.utls.selectLayerbyName(cfg.lastPrev)
			if l is not None:
				cfg.cnvs.setRenderFlag(False)
				l.renderer().setOpacity(float(1) - float(value) / 100)
				if hasattr(l, "setCacheImage"):
					l.setCacheImage(None)
				l.triggerRepaint()
				cfg.cnvs.setRenderFlag(True)
				cfg.cnvs.refresh()
		except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
	# show hide preview radio button 2
	def showHidePreview2(self):
		try:
			l = cfg.utls.selectLayerbyName(cfg.lastPrev)
			if l is not None:
				if cfg.show_preview_radioButton2.isChecked():				
					cfg.lgnd.setLayerVisible(l, True)
					cfg.utls.moveLayerTop(l)
				else:
					cfg.lgnd.setLayerVisible(l, False)
		except:
			pass
			
	# create classification preview
	def createPreview(self, point, algorithmRaster = "No"):
		if cfg.imgNm is None:
			cfg.mx.msg4()
			cfg.pntPrvw = None
		# check if image is None
		elif cfg.utls.selectLayerbyName(cfg.imgNm, "Yes") is None:
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
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> PREVIEW click")
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			cfg.uiUtls.updateBar(10)
			lastPrevX = cfg.lastPrev
			# date time for temp name
			dT = cfg.utls.getTime()
			# temp files
			tPMN = dT + cfg.algRasterNm + ".tif"
			tPMD = cfg.tmpDir + "/" + tPMN
			# preview name and path
			pN =  dT + cfg.prvwTempNm
			pP = cfg.tmpDir + "/" + pN
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "point (X,Y) = (%s,%s)" % (cfg.pntPrvw.x() , cfg.pntPrvw.y()))
			# signature list
			sL = self.getSignatureList()
			# input image
			if cfg.actionCheck == "Yes" and  self.trainSigCheck == "Yes":
				# check band set
				ckB = "Yes"
				if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
					ckB = cfg.utls.checkBandSet()
				if ckB == "Yes":
					cfg.uiUtls.updateBar(20)
					# compression
					if int(cfg.prvwSz) <= 2000:
						compress = "No"
					else:
						compress = cfg.rasterCompression
					ok, opOut, mOut = self.runAlgorithm(cfg.algName, cfg.imgNm, sL, pP, cfg.macroclassCheck, None, int(cfg.prvwSz), point, compress)
					if ok == "Yes":
						if algorithmRaster == "No":
							r = cfg.iface.addRasterLayer(pP, cfg.osSCP.path.basename(str(pP)))
							cfg.lastPrev = r.name()
							cfg.uiUtls.updateBar(80)
							# apply symbology
							self.applyClassSymbology(r, cfg.macroclassCheck, cfg.qmlFl, sL)
						else:
							r = cfg.iface.addRasterLayer(mOut, cfg.osSCP.path.basename(str(mOut)))
							cfg.lastPrev = r.name()
							cfg.utls.rasterPreviewSymbol(r, cfg.algName)
							cfg.uiUtls.updateBar(80)
						# move to top
						cfg.prevList.append(r)
						cfg.utls.moveLayerTop(r)
						cfg.iface.setActiveLayer(r)
						# move previous preview to group
						g = cfg.utls.groupIndex(cfg.grpNm)
						if g is None:
							g = cfg.utls.createGroup(cfg.grpNm)
						preP = cfg.utls.selectLayerbyName(lastPrevX)
						if preP is not None:
							cfg.lgnd.moveLayer(preP, g)
						cfg.lgnd.setGroupVisible(g, False)
						cfg.lgnd.setGroupExpanded(g, False)
						cfg.show_preview_radioButton2.setChecked(True)
					cfg.uiUtls.updateBar(100)
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< PREVIEW created: " + unicode(pN))
					# enable Redo button
					cfg.redoPreviewButton.setEnabled(True)
				else:
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
					cfg.mx.msgErr6()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "preview no")	
			else:
				cfg.uiUtls.removeProgressBar()
				if self.trainSigCheck == "No":
					cfg.mx.msg18()
				cfg.cnvs.setRenderFlag(True)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "preview no")	
	
	# calculate signatures for checked ROIs
	def getSignatureList(self):
		refreshTable = None
		for i in cfg.ROI_SCP_UID.values():
			if str(i) not in cfg.signIDs.values() and cfg.signList["CHECKBOX_" + str(i)] == 2:
				rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(i))
				cfg.utls.calculateSignature(cfg.shpLay, cfg.rstrNm, rId, cfg.ROI_MC_ID[i], cfg.ROI_MC_Info[i], cfg.ROI_C_ID[i], cfg.ROI_C_Info[i], None, None, "No", "No", i)
				refreshTable = "Yes"
		if refreshTable == "Yes":
			cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
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
				s.append(cfg.signList["LCS_MIN_" + str(i)])
				s.append(cfg.signList["LCS_MAX_" + str(i)])
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
				if cfg.algName == cfg.algMinDist:
					s.append(cfg.signList["MD_THRESHOLD_" + str(i)])
				elif cfg.algName == cfg.algML:
					s.append(cfg.signList["ML_THRESHOLD_" + str(i)])
				elif cfg.algName == cfg.algSAM:
					s.append(cfg.signList["SAM_THRESHOLD_" + str(i)])
		if len(signatureList) > 0:
			self.trainSigCheck = "Yes"
		else:
			self.trainSigCheck = "No"
		return signatureList
			
	# set variable for macroclass classification
	def macroclassCheckbox(self):
		if cfg.uidc.macroclass_checkBox.isChecked() is True:
			cfg.sets.setQGISRegSetting(cfg.regConsiderMacroclass, "Yes")
			cfg.uidc.class_checkBox.blockSignals(True)
			cfg.uidc.class_checkBox.setCheckState(0)
			cfg.uidc.class_checkBox.blockSignals(False)
		else:
			cfg.sets.setQGISRegSetting(cfg.regConsiderMacroclass, "No")
			cfg.uidc.class_checkBox.blockSignals(True)
			cfg.uidc.class_checkBox.setCheckState(2)
			cfg.uidc.class_checkBox.blockSignals(False)
		cfg.macroclassCheck = cfg.sets.getQGISRegSetting(cfg.regConsiderMacroclass, "No")
		# check signature intersection
		intersect1 = cfg.LCSignT.checkIntersections()
		cfg.LCSignT.higlightRowsByID(intersect1)
		intersect2 = cfg.spSigPlot.checkIntersections()
		cfg.spSigPlot.higlightRowsByID(intersect2)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.macroclassCheck))
							
	# set variable for class classification
	def classCheckbox(self):
		if cfg.uidc.class_checkBox.isChecked() is True:
			cfg.uidc.macroclass_checkBox.setCheckState(0)
		else:
			cfg.uidc.macroclass_checkBox.setCheckState(2)
				
	# set variable for LC signature
	def LCSignature_Checkbox(self):
		if cfg.uidc.LC_signature_checkBox.isChecked() is True:
			cfg.sets.setQGISRegSetting(cfg.regLCSignature, "Yes")
		else:
			cfg.sets.setQGISRegSetting(cfg.regLCSignature, "No")
		cfg.LCsignatureCheckBox = cfg.sets.getQGISRegSetting(cfg.regLCSignature, "No")
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.LCsignatureCheckBox))
			
	# set variable for mask
	def maskCheckbox(self):
		if cfg.uidc.mask_checkBox.isChecked() is True:
			m = cfg.utls.getOpenFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a mask shapefile"), "", "Shapefile (*.shp)")
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
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.mskFlState))
		
	# Reset mask path
	def resetMask(self):
		cfg.mskFlPath = ""
		cfg.mskFlState = 0
		cfg.utls.writeProjectVariable("maskFilePath", unicode(cfg.mskFlPath))	
		cfg.utls.writeProjectVariable("maskFileState", unicode(cfg.mskFlState))	
		cfg.uidc.mask_lineEdit.setText(str(cfg.mskFlPath))
		self.setMaskCheckbox()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reset mask")
		
	def setMaskCheckbox(self):	
		cfg.uidc.mask_checkBox.blockSignals(True)
		cfg.uidc.mask_checkBox.setCheckState(int(cfg.mskFlState))
		cfg.uidc.mask_checkBox.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "mask checkbox")
		
	# left click pointer for classification preview
	def pointerClickPreview(self, point):
		# check if other processes are active
		if cfg.actionCheck == "No":
			cfg.utls.checkPointImage(cfg.imgNm, point)
			if cfg.pntCheck == "Yes":
				cfg.pntPrvw = cfg.lstPnt
				self.algRasterPrevw = "No"
				self.createPreview(cfg.pntPrvw)
				
	# right click pointer for preview algorithm raster
	def pointerRightClickPreview(self, point):
		# check if other processes are active
		if cfg.actionCheck == "No":
			point = cfg.utls.checkPointImage(cfg.rstrNm, point)
			if cfg.pntCheck == "Yes":
				cfg.pntPrvw = cfg.lstPnt
				self.algRasterPrevw = "Yes"
				self.createPreview(cfg.pntPrvw, self.algRasterPrevw)
		
	# Activate pointer for classification preview
	def pointerPreviewActive(self):
		# connect to click
		t = cfg.classPrev
		cfg.cnvs.setMapTool(t)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: preview")
		
	# set preview size
	def previewSize(self):
		cfg.prvwSz = int(float(cfg.preview_size_spinBox.value()))
		cfg.utls.writeProjectVariable("previewSize", str(cfg.prvwSz))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "preview size: " + str(cfg.prvwSz))
		
	# redo preview
	def redoPreview(self):
		# check if other processes are active
		if cfg.actionCheck == "No":
			if cfg.pntPrvw is None:
				pass
			else:
				self.createPreview(cfg.pntPrvw, self.algRasterPrevw)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "REDO Preview")
		
	# set variable for report
	def reportCheckbox(self):
		if cfg.uidc.report_checkBox.isChecked() is True:
			cfg.reportCheck = "Yes"
		else:
			cfg.reportCheck = "No"
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.reportCheck))
		
	# Reset qml style path
	def resetQmlStyle(self):
		p = cfg.qgisCoreSCP.QgsProject.instance()
		p.writeEntry("SemiAutomaticClassificationPlugin", "qmlfile", "")
		cfg.uidc.qml_lineEdit.setText("")
		cfg.qmlFl = ""
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reset qml")
		
	# run classification algorithm
	def runAlgorithm(self, algorithmName, imageName, signatureList, outputRasterPath, macroclassCheck = "No", algRasterPath = None, previewSize = 0, previewPoint = None, compress = "No"):
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
				rD = cfg.gdalSCP.Open(unicode(bS[i]), cfg.gdalSCP.GA_ReadOnly)
				bL.append(rD)
		else:
			# if masked raster
			if imageName == cfg.maskRasterNm:
				iR = cfg.maskRstSrc
			else:
				r = cfg.utls.selectLayerbyName(imageName, "Yes")
				iR = r.source()
			# open input with GDAL
			rD = cfg.gdalSCP.Open(iR, cfg.gdalSCP.GA_ReadOnly)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
		if rD is not None:
			# signature rasters
			oRL, opOut = cfg.utls.createSignatureClassRaster(signatureList, rD, cfg.tmpDir, cfg.NoDataVal, None, previewSize, previewPoint, "No")
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
				tPMN2 = dT + cfg.classRasterNm + ".tif"
				tPMD2 = cfg.tmpDir + "/" + tPMN2
				oM.append(tPMD)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, previewSize, previewPoint,  "No")
			oC.append(tPMD2)
			oCR = cfg.utls.createRasterFromReference(rD, 1, oC, cfg.NoDataVal, "GTiff", cfg.gdalSCP.GDT_Int32, previewSize, previewPoint, compress, "DEFLATE")
			o = cfg.utls.processRaster(rD, bL, signatureList, None, cfg.utls.classification, algorithmName, oRL, oMR[0], oCR[0], previewSize, previewPoint, cfg.NoDataVal, macroclassCheck, cfg.multiAddFactorsVar, cfg.bndSetMultAddFactorsList)
			if o == "No":
				return "No", opOut, tPMD
			# close GDAL rasters
			for x in range(0, len(oRL)):
				fList = oRL[x].GetFileList()
				oRL[x] = None
				if previewSize > 0:
					try:
						for fL in fList:
							cfg.osSCP.remove(fL)
					except:
						pass
			for x in range(0, len(oMR)):
				oMR[x] = None
			for x in range(0, len(oCR)):
				oCR[x] = None
			for x in range(0, len(bL)):
				bL[x] = None
			rD = None
			if cfg.rasterCompression != "No":
				try:
					cfg.utls.GDALCopyRaster(tPMD2, outputRasterPath, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
					cfg.osSCP.remove(tPMD2)
				except Exception, err:
					cfg.shutilSCP.copy(tPMD2, outputRasterPath)
					cfg.osSCP.remove(tPMD2)
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			else:
				cfg.shutilSCP.copy(tPMD2, outputRasterPath)
				cfg.osSCP.remove(tPMD2)
			# create raster table (removed because of some issues)
			#cfg.utls.createRasterTable(outputRasterPath, 1, signatureList)
			return "Yes", opOut, tPMD
		else:
			cfg.mx.msgErr25()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " error raster")
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
			tW = cfg.uidc.signature_list_tableWidget
			c = tW.rowCount()
			for row in range(0, c):
				id = tW.item(row, 6).text()
				cfg.signList["CHECKBOX_" + str(id)] = tW.item(row, 0).checkState()
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all signatures")
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.removeProgressBar()

	# perform classification
	def runClassificationAction(self):
		self.runClassification()
		
	# perform classification
	def runClassification(self, batch = "No", outputClassification = None):
		sL = self.getSignatureList()
		if self.trainSigCheck == "Yes":
			if batch == "No":
				clssOut = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save classification output"), "", "Image (*.tif)")
			else:
				clssOut = outputClassification
			if len(clssOut) > 0:
				clssOut = clssOut.replace('\\', '/')
				clssOut = clssOut.replace('//', '/')
				cfg.clssPth = clssOut
				sN = cfg.osSCP.path.basename(unicode(clssOut))
				if unicode(sN).endswith(".tif"):
					cfg.clssPth = clssOut
				else:
					nm = cfg.osSCP.path.splitext(sN)[0]
					cfg.clssPth = cfg.osSCP.path.dirname(clssOut) + '/' + nm + ".tif"
			cfg.QtGuiSCP.qApp.processEvents()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification output: " + unicode(cfg.clssPth))	
			# check if can run classification
			ckC = "Yes"
			if cfg.imgNm is None:
				cfg.mx.msg4()
				ckC = "No"
			elif cfg.clssPth is None:
				cfg.mx.msg12()
				ckC = "No"
			# check if image is None
			elif cfg.utls.selectLayerbyName(cfg.imgNm, "Yes") is None:
				# if band set then pass
				if cfg.imgNm != cfg.bndSetNm:
					cfg.mx.msg4()
					cfg.ipt.refreshRasterLayer()
					ckC = "No"
			if ckC != "No":
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> CLASSIFICATION STARTED")
				# base name
				n = cfg.osSCP.path.basename(cfg.clssPth)
				nm = cfg.osSCP.path.splitext(n)[0]
				if batch == "No":
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
				# check band set
				ckB = "Yes"
				if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
					ckB = cfg.utls.checkBandSet()
				# date time for temp name
				dT = cfg.utls.getTime()
				cfg.uiUtls.updateBar(10)
				if ckB == "Yes":
					cfg.bndSetMaskList = []
					img = cfg.imgNm
				### if mask
					if cfg.uidc.mask_checkBox.isChecked() is True:
						# mask shapefile path
						m = cfg.uidc.mask_lineEdit.text()
						dT = cfg.utls.getTime()
						tCN = dT + cfg.maskRasterNm
						# apply mask
						if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
							for x in range(0, len(cfg.bndSetLst)):
								tCD = cfg.tmpDir + "/" + str(x) + tCN 
								cfg.bndSetMaskList.append(tCD)
								cfg.utls.clipRasterByShapefile(m, cfg.bndSetLst[x], str(tCD), cfg.outTempRastFormat)
						else:
							# temp masked raster
							cfg.maskRstSrc = cfg.tmpDir + "/" + tCN 
							cfg.utls.clipRasterByShapefile(m, cfg.imgSrc, str(cfg.maskRstSrc), cfg.outTempRastFormat)
						img = cfg.maskRasterNm
				### if not mask
					cfg.uiUtls.updateBar(20)
					# compression
					compress = cfg.rasterCompression
					ok, opOut, mOut = self.runAlgorithm(cfg.algName, img, sL, cfg.clssPth, cfg.macroclassCheck, None, None, None, compress)
					if ok == "Yes":
						c = cfg.iface.addRasterLayer(cfg.clssPth, cfg.osSCP.path.basename(unicode(cfg.clssPth)))
						cfg.utls.moveLayerTop(c)
						cfg.uiUtls.updateBar(80)
						# apply symbology
						self.applyClassSymbology(c, cfg.macroclassCheck, cfg.qmlFl, sL)
						# save qml file
						cfg.utls.saveQmlStyle(c, cfg.osSCP.path.dirname(clssOut) + '/' + nm + ".qml")
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< CLASSIFICATION PERFORMED: " + unicode(cfg.clssPth))
				### calculate report
					if cfg.reportCheck == "Yes":
						reportOut = cfg.osSCP.path.dirname(cfg.clssPth) + "/" + nm + cfg.reportNm
						cfg.classRep.calculateClassificationReport(cfg.clssPth, 0, "Yes", reportOut)
				### convert classification to vector
					cfg.uiUtls.updateBar(85)
					if cfg.vectorOutputCheck == "Yes":
						cfg.uiUtls.updateBar(85, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", " conversion to vector. Please wait ..."))
						vO = cfg.osSCP.path.dirname(cfg.clssPth) + "/" + nm + ".shp"
						cfg.utls.rasterToVector(cfg.clssPth, vO)
						vl = cfg.utls.addVectorLayer(str(vO), cfg.osSCP.path.basename(vO), "ogr")
						cfg.utls.vectorSymbol(vl, sL, cfg.macroclassCheck)
						cfg.utls.addLayerToMap(vl)
					cfg.uiUtls.updateBar(95)
				### copy signature raster
					if cfg.algFilesCheck == "Yes":
						rOBaseNm = cfg.osSCP.path.dirname(cfg.clssPth)
						try:
							for r in opOut:
								rNm = cfg.osSCP.path.basename(r)[:7]
								bNm = nm + "_" + rNm + ".tif"
								if cfg.rasterCompression != "No":
									try:
										cfg.utls.GDALCopyRaster(r, rOBaseNm + "/" + bNm, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
									except Exception, err:
										cfg.shutilSCP.copy(r, rOBaseNm + "/" + bNm)
										# logger
										if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								else:
									cfg.shutilSCP.copy(r, rOBaseNm + "/" + bNm)
								c = cfg.iface.addRasterLayer(rOBaseNm + "/" + bNm, bNm)
								if cfg.uidc.LC_signature_checkBox.isChecked():
									cfg.utls.rasterSymbolLCSAlgorithmRaster(c)
							mOutNm = nm + "_" + cfg.algRasterNm + ".tif"
							if cfg.rasterCompression != "No":
								try:
									cfg.utls.GDALCopyRaster(mOut, rOBaseNm + "/" + mOutNm, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
								except Exception, err:
									cfg.shutilSCP.copy(mOut, rOBaseNm + "/" + mOutNm)
									# logger
									if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							else:
								cfg.shutilSCP.copy(mOut, rOBaseNm + "/" + mOutNm)
							c = cfg.iface.addRasterLayer(rOBaseNm + "/" + mOutNm, mOutNm)
							if cfg.uidc.LC_signature_checkBox.isChecked():
								cfg.utls.rasterSymbolLCSAlgorithmRaster(c)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files copied")
						except Exception, err:
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							cfg.mx.msgErr23()
					try:
						for r in opOut:
							cfg.osSCP.remove(r)
						cfg.osSCP.remove(mOut)
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "files deleted")
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				### ending
					cfg.uiUtls.updateBar(100)
					if batch == "No":
						cfg.utls.finishSound()
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
					cfg.clssPth = None
			### band set check failed
				else:
					cfg.mx.msgErr6()
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
					cfg.clssPth = None
					cfg.bst.rasterBandName()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "band set check failed")
		else:
			cfg.mx.msg18()
			if batch == "No":
				cfg.cnvs.setRenderFlag(True)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification no")	
			
	# apply symbology to classification			
	def applyClassSymbology(self, classificationRaster, macroclassCheck, qmlFile, signatureList = None):
		# qml symbology
		if qmlFile == "":
			if macroclassCheck == "Yes":
				signatureList = cfg.classD.createMCIDList()
				if len(signatureList) == 0:
					cfg.mx.msgWar19()
			cfg.utls.rasterSymbol(classificationRaster, signatureList, macroclassCheck)
		else:
			try:
				self.applyQmlStyle(classificationRaster, qmlFile)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							
	# Select qml style for classifications and previews
	def selectQmlStyle(self):
		cfg.qmlFl = cfg.utls.getOpenFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a qml style"), "", "Style (*.qml)")
		# write path to project istance
		p = cfg.qgisCoreSCP.QgsProject.instance()
		p.writeEntry("SemiAutomaticClassificationPlugin", "qmlfile", cfg.qmlFl)
		cfg.uidc.qml_lineEdit.setText(cfg.qmlFl)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "qml file: " + unicode(cfg.qmlFl))

	# export signature list to file
	def saveSignatureList(self, signatureFile):
		try:
			root = cfg.ETSCP.Element("signaturelist")
			MCID_LIST = cfg.classD.exportMCIDList()
			root.set("MCID_LIST", str(MCID_LIST))
			for k in cfg.signIDs.values():
				sigItem = cfg.ETSCP.SubElement(root, "signature")
				sigItem.set("ID", str(cfg.signIDs["ID_" + str(k)]))
				mcIDField = cfg.ETSCP.SubElement(sigItem, "MACROCLASSID")
				mcIDField.text = str(cfg.signList["MACROCLASSID_" + str(k)])
				mcInfoField = cfg.ETSCP.SubElement(sigItem, "MACROCLASSINFO")
				mcInfoField.text = str(cfg.signList["MACROCLASSINFO_" + str(k)])
				cIDField = cfg.ETSCP.SubElement(sigItem, "CLASSID")
				cIDField.text = str(cfg.signList["CLASSID_" + str(k)])
				cInfoField = cfg.ETSCP.SubElement(sigItem, "CLASSINFO")
				cInfoField.text = str(cfg.signList["CLASSINFO_" + str(k)])
				wvLngField = cfg.ETSCP.SubElement(sigItem, "VALUES")
				wvLngField.text = str(cfg.signList["VALUES_" + str(k)])
				lcsMinField = cfg.ETSCP.SubElement(sigItem, "LCS_MIN")
				lcsMinField.text = str(cfg.signList["LCS_MIN_" + str(k)])
				lcsMaxField = cfg.ETSCP.SubElement(sigItem, "LCS_MAX")
				lcsMaxField.text = str(cfg.signList["LCS_MAX_" + str(k)])
				wvLngField = cfg.ETSCP.SubElement(sigItem, "WAVELENGTH")
				wvLngField.text = str(cfg.signList["WAVELENGTH_" + str(k)])
				meanValField = cfg.ETSCP.SubElement(sigItem, "MEAN_VALUE")
				meanValField.text = str(cfg.signList["MEAN_VALUE_" + str(k)])
				checkboxField = cfg.ETSCP.SubElement(sigItem, "CHECKBOX")
				checkboxField.text = str(cfg.signList["CHECKBOX_" + str(k)])
				SDField = cfg.ETSCP.SubElement(sigItem, "SD")
				SDField.text = str(cfg.signList["SD_" + str(k)])
				unitField = cfg.ETSCP.SubElement(sigItem, "WAVELENGTH_UNIT")
				unitField.text = str(cfg.signList["UNIT_" + str(k)])
				colorField = cfg.ETSCP.SubElement(sigItem, "COLOR")
				colorField.text = str(cfg.signList["COLOR_" + str(k)].toRgb().name())
				covMatrField = cfg.ETSCP.SubElement(sigItem, "COVARIANCE_MATRIX")
				covMatrField.text = str(cfg.utls.covarianceMatrixToList(cfg.signList["COVMATRIX_" + str(k)]))
				roiSizeField = cfg.ETSCP.SubElement(sigItem, "ROI_SIZE")
				roiSizeField.text = str(cfg.signList["ROI_SIZE_" + str(k)])
				maxValField = cfg.ETSCP.SubElement(sigItem, "MAX_VALUE")
				maxValField.text = str(cfg.signList["MAX_VALUE_" + str(k)])
				minValField = cfg.ETSCP.SubElement(sigItem, "MIN_VALUE")
				minValField.text = str(cfg.signList["MIN_VALUE_" + str(k)])
				sigThrField = cfg.ETSCP.SubElement(sigItem, "SIGNATURE_THRESHOLD_MD")
				sigThrField.text = str(cfg.signList["MD_THRESHOLD_" + str(k)])
				sigThrField = cfg.ETSCP.SubElement(sigItem, "SIGNATURE_THRESHOLD_ML")
				sigThrField.text = str(cfg.signList["ML_THRESHOLD_" + str(k)])
				sigThrField = cfg.ETSCP.SubElement(sigItem, "SIGNATURE_THRESHOLD_SAM")
				sigThrField.text = str(cfg.signList["SAM_THRESHOLD_" + str(k)])
			o = open(signatureFile, 'w')
			f = cfg.minidomSCP.parseString(cfg.ETSCP.tostring(root)).toprettyxml()
			o.write(f)
			o.close()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures saved in: " + unicode(signatureFile))
		except Exception, err:
			cfg.mx.msgErr15()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	def openSignatureList(self, path = None):
		if path is None:
			signFilePath = cfg.utls.getOpenFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a signature list file"), "", "Signature list file .slf (*.slf)")
		else:
			signFilePath = path
		if len(signFilePath) > 0:
			if cfg.absolutePath == "false":
				signFile = cfg.utls.qgisAbsolutePathToRelativePath(signFilePath, cfg.projPath)
			else:
				signFile = signFilePath
			self.openSignatureListFile(signFilePath)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures opened: " + unicode(signFilePath))
					
	# open training file
	def openTrainingFile(self):
		scpPath = cfg.utls.getOpenFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a SCP training input"), "", "SCP file (*.scp)")
		if len(scpPath) > 0:
			cfg.classD.openInput(scpPath)
			
	# open input
	def openInput(self, scpPath = None):
		# shape layer
		cfg.shpLay = None
		# training layer name
		cfg.trnLay = None
		# signature file path
		cfg.sigFile = None
		cfg.inptDir = None
		if scpPath is None:
			scpPath = cfg.utls.readProjectVariable("trainingLayer", "")
		check = cfg.classD.openShapeFile(scpPath)
		if check == "Yes":
			cfg.utls.writeProjectVariable("trainingLayer", unicode(scpPath))
			cfg.scpFlPath = scpPath
			cfg.uidc.trainingFile_lineEdit.setText(unicode(scpPath))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures opened: " + unicode(scpPath))
		else:
			# shape layer
			cfg.shpLay = None
			# training layer name
			cfg.trnLay = None
			# signature file path
			cfg.sigFile = None
			cfg.inptDir = None
			cfg.uidc.trainingFile_lineEdit.setText("")

	# open input file
	def openShapeFile(self, shapeFilePath):
		# shapefile
		zipName = cfg.osSCP.path.basename(unicode(shapeFilePath))
		name = zipName[:-4]
		dT = cfg.utls.getTime()
		cfg.inptDir = cfg.tmpDir + "/" + name + dT
		oDir = cfg.utls.makeDirectory(cfg.inptDir)
		# unzip to temp dir
		try:
			with cfg.zipfileSCP.ZipFile(shapeFilePath) as zOpen:
				for flName in zOpen.namelist():
					zipF = zOpen.open(flName)
					fileName = cfg.osSCP.path.basename(flName)
					if fileName.endswith(".shp"):
						nm = fileName
					try:
						zipO = file(cfg.inptDir + "/" + fileName, "wb")
						with zipF, zipO:
							cfg.shutilSCP.copyfileobj(zipF, zipO)
					except:
						pass
		except:
			return "No"
		# try remove SCP input
		try:
			cfg.utls.removeLayer(name)
		except:
			pass
		try:
			tSS = cfg.utls.addVectorLayer(cfg.inptDir + "/" + nm, nm, "ogr")
		except:
			cfg.mx.msgErr59()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error training input")
			return "No"
		check = cfg.classD.checkFields(tSS)
		vEPSG = cfg.utls.getEPSGVectorQGIS(tSS)
		try:
			if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
				rEPSG = cfg.utls.getEPSGRaster(cfg.bndSetLst[0])
			else:
				rEPSG = cfg.utls.getEPSGRaster(cfg.imgSrc)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
				xR = cfg.utls.selectLayerbyName(cfg.bndSet[0], "Yes")
			else:
				xR = cfg.utls.selectLayerbyName(cfg.imgNm, "Yes")
			rEPSG = cfg.utls.getEPSGVectorQGIS(xR)
			#return "No"
		if str(vEPSG) != str(rEPSG):
			cfg.mx.msgWar22()
		if check == "Yes":
			# create memory layer
			provider = tSS.dataProvider()
			fields = provider.fields()
			pCrs = cfg.utls.getCrs(tSS)
			mL = QgsVectorLayer("MultiPolygon?crs=" + str(pCrs.toWkt()), name, "memory")
			#mL = QgsVectorLayer("Polygon?crs=" + str(pCrs.toWkt()), name, "memory")
			mL.setCrs(pCrs)
			pr = mL.dataProvider()
			for fld in fields:
				pr.addAttributes([fld])
			mL.updateFields()
			f = QgsFeature()
			mL.startEditing()
			for f in tSS.getFeatures():
				mL.addFeature(f)	
			mL.commitChanges()
			mL.dataProvider().createSpatialIndex()
			mL.updateExtents()
			cfg.utls.ROISymbol(mL)
			cfg.shpLay = mL
			cfg.trnLay = name
			cfg.utls.addLayerToMap(cfg.shpLay)
			sigFileNm = cfg.trnLay + ".slf"
			cfg.sigFile = cfg.inptDir + "/" + sigFileNm
			sigFile = cfg.sigFile
			for root, dirs, files in cfg.osSCP.walk(cfg.inptDir):
				for x in files:
					if x.lower().endswith(".slf"):
						sigFile = root + "/" + x
			if cfg.osSCP.path.isfile(sigFile):
				cfg.classD.openSignatureList(sigFile)
			else:
				cfg.classD.saveSignatureList(cfg.sigFile)
				cfg.mx.msg20()
				cfg.classD.openSignatureList(cfg.sigFile)
		return check
		
	# save memory layer to shapefile
	def saveMemToSHP(self, memoryLayer):
		dT = cfg.utls.getTime()
		inptDir2 = cfg.inptDir
		try:
			cfg.inptDir = cfg.tmpDir + "/" + cfg.trnLay + dT
		except Exception, err:
			cfg.mx.msgErr59()
			cfg.inptDir = cfg.tmpDir + "/" + dT
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error training input")
			return "No"
		oDir = cfg.utls.makeDirectory(cfg.inptDir)
		shpF = cfg.inptDir + "/" + cfg.trnLay + ".shp"
		l = cfg.utls.saveMemoryLayerToShapefile(memoryLayer, shpF, cfg.trnLay)
		if l == "No":
			cfg.classD.openInput()
			return "No"
		sigFileNm = cfg.trnLay + ".slf"
		cfg.sigFile = cfg.inptDir + "/" + sigFileNm 
		cfg.classD.saveSignatureList(cfg.sigFile)
				
	# check shapefile and fields
	def checkFields(self, trainingLayer):
		try:
			if (trainingLayer.geometryType() == QGis.Polygon):
				# filter if shapefile has ID_class and ROI_info fields
				f = trainingLayer.dataProvider().fields()
				if f.indexFromName(cfg.fldID_class) > -1 and f.indexFromName(cfg.fldROI_info) > -1 and f.indexFromName(cfg.fldMacroID_class) > -1 and f.indexFromName(cfg.fldROIMC_info) > -1 and f.indexFromName(cfg.fldSCP_UID) > -1:
					return "Yes"
				else:
					# ask for confirm
					a = cfg.utls.questionBox("Missing fields in shapefile", "Add missing fields to shapefile?")
					if a == "Yes":
						cfg.classD.addFieldsToLayer(trainingLayer)
						f = trainingLayer.dataProvider().fields()
						if f.indexFromName(cfg.fldID_class) > -1 and f.indexFromName(cfg.fldROI_info) > -1 and f.indexFromName(cfg.fldMacroID_class) > -1 and f.indexFromName(cfg.fldROIMC_info) > -1 and f.indexFromName(cfg.fldSCP_UID) > -1:
							return "Yes"
						else:
							return "No"
					else:
						return "No"
		except Exception, err:
			return "No"
			
	# Add required fields if missing
	def addFieldsToLayer(self, layer):
		f = []
		fi = layer.dataProvider().fields()
		# add fields
		if fi.indexFromName(cfg.fldID_class) == -1:
			f.append(QgsField(cfg.fldID_class, cfg.QVariantSCP.Int))
		if fi.indexFromName(cfg.fldROI_info) == -1:
			f.append(QgsField(cfg.fldROI_info, cfg.QVariantSCP.String))
		if fi.indexFromName(cfg.fldMacroID_class) == -1:
			f.append(QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))
		if fi.indexFromName(cfg.fldROIMC_info) == -1:
			f.append(QgsField(cfg.fldROIMC_info, cfg.QVariantSCP.String))
		if fi.indexFromName(cfg.fldSCP_UID) == -1:		
			f.append(QgsField(cfg.fldSCP_UID, cfg.QVariantSCP.String))
		layer.startEditing()
		aF = layer.dataProvider().addAttributes(f)
		# commit changes
		layer.commitChanges()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " fields added")

	# import SLC signature list
	def importSLCSignatureList(self, signatureFile, addToSignature = "No"):
		# shapefile
		zipName = cfg.osSCP.path.basename(signatureFile)
		name = zipName[:-4]
		dT = cfg.utls.getTime()
		unzipDir = cfg.tmpDir + "/" + name + dT
		oDir = cfg.utls.makeDirectory(unzipDir)
		shpF = unzipDir + "/" + name + ".shp"
		sigFile = unzipDir + "/" + name + ".slf"
		# unzip to temp dir
		try:
			with cfg.zipfileSCP.ZipFile(signatureFile) as zOpen:
				for flName in zOpen.namelist():
					zipF = zOpen.open(flName)
					fileName = cfg.osSCP.path.basename(flName)
					zipO = file(unzipDir + "/" + fileName, "wb")
					with zipF, zipO:
						cfg.shutilSCP.copyfileobj(zipF, zipO)
		except:
			return "No"
		tSS = cfg.utls.addVectorLayer(shpF, name , "ogr")
		pCrs = cfg.utls.getCrs(tSS)
		tCrs = cfg.utls.getCrs(cfg.shpLay)
		f = QgsFeature()
		cfg.shpLay.startEditing()
		for f in tSS.getFeatures():
			SCP_UID  = str(f[cfg.fldSCP_UID])
			if SCP_UID not in cfg.ROI_SCP_UID:
				# if same coordinates
				if pCrs == tCrs:
					cfg.shpLay.addFeature(f)
				else:
					# transform coordinates
					aF = f.geometry()
					trs = QgsCoordinateTransform(pCrs, tCrs)
					aF.transform(trs)
					oF = QgsFeature()
					oF.setGeometry(aF)
					at = f.attributes()
					oF.setAttributes(at)
					cfg.shpLay.addFeature(oF)
		cfg.shpLay.commitChanges()
		cfg.shpLay.dataProvider().createSpatialIndex()
		cfg.shpLay.updateExtents()
		cfg.classD.openSignatureListFile(sigFile, addToSignature)
		
	# open signature file
	def openSignatureListFile(self, signatureFile, addToSignature = "No"):
		try:
			tree = cfg.ETSCP.parse(signatureFile)
			root = tree.getroot()
			if addToSignature == "No":
				cfg.signList = {}
				cfg.signIDs = {}
			try:
				MCID_LIST = root.get("MCID_LIST")
				MCIDLIST = eval(MCID_LIST)
				cfg.classD.importMCIDList(MCIDLIST)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			for child in root:
				try:
					b = child.get("ID")
					if len(b) == 0:
						b = cfg.utls.signatureID()
				except:
					b = cfg.utls.signatureID()
				cfg.signList["MACROCLASSID_" + str(b)] = str(child.find("MACROCLASSID").text).strip()
				cfg.signList["MACROCLASSINFO_" + str(b)] = str(child.find("MACROCLASSINFO").text).strip()
				cfg.signList["CLASSID_" + str(b)] = str(child.find("CLASSID").text).strip()
				cfg.signList["CLASSINFO_" + str(b)] = str(child.find("CLASSINFO").text).strip()
				cfg.signList["UNIT_" + str(b)] = str(child.find("WAVELENGTH_UNIT").text).strip()
				cfg.signList["ROI_SIZE_" + str(b)] = str(child.find("ROI_SIZE").text).strip()
				cfg.signIDs["ID_" + str(b)] = b
				# get values
				vls = str(child.find("VALUES").text).strip()
				x = eval(vls)
				cfg.signList["VALUES_" + str(b)] = x	
				try:
					lcsMin = str(child.find("LCS_MIN").text).strip()
					min = eval(lcsMin)
					cfg.signList["LCS_MIN_" + str(b)] = min			
					lcsMax = str(child.find("LCS_MAX").text).strip()
					max = eval(lcsMax)
					cfg.signList["LCS_MAX_" + str(b)] = max
				except:
					cfg.signList["LCS_MIN_" + str(b)] = x
					cfg.signList["LCS_MAX_" + str(b)] = x
				try:
					minV = str(child.find("MIN_VALUE").text).strip()
					minVal = eval(minV)
					cfg.signList["MIN_VALUE_" + str(b)] = minVal
					maxV = str(child.find("MAX_VALUE").text).strip()	
					maxVal = eval(maxV)
					cfg.signList["MAX_VALUE_" + str(b)] = maxVal
				except:
					cfg.signList["MIN_VALUE_" + str(b)] = x
					cfg.signList["MAX_VALUE_" + str(b)] = x			
				cfg.signList["WAVELENGTH_" + str(b)] = eval(str(child.find("WAVELENGTH").text).strip())
				cfg.signList["SD_" + str(b)] = eval(str(child.find("SD").text).strip())
				cfg.signList["MEAN_VALUE_" + str(b)] = eval(str(child.find("MEAN_VALUE").text).strip())
				try:
					cfg.signList["CHECKBOX_" + str(b)] = eval(str(child.find("CHECKBOX").text).strip())
				except:
					cfg.signList["CHECKBOX_" + str(b)] = 2
				c = cfg.QtGuiSCP.QColor()
				c.setNamedColor(str(child.find("COLOR").text).strip())
				cfg.signList["COLOR_" + str(b)] = c
				# get covariance matrix
				mt = str(child.find("COVARIANCE_MATRIX").text).strip()
				try:
					cm = eval(mt)
				except:
					cm = "No"
				cfg.signList["COVMATRIX_" + str(b)] = cfg.utls.listToCovarianceMatrix(cm)
				try:
					cfg.signList["MD_THRESHOLD_" + str(b)] = float((child.find("SIGNATURE_THRESHOLD_MD").text).strip())
				except:
					cfg.signList["MD_THRESHOLD_" + str(b)] = 0
				try:
					cfg.signList["ML_THRESHOLD_" + str(b)] = float((child.find("SIGNATURE_THRESHOLD_ML").text).strip())
				except:
					cfg.signList["ML_THRESHOLD_" + str(b)] = 0
				try:
					cfg.signList["SAM_THRESHOLD_" + str(b)] = float((child.find("SIGNATURE_THRESHOLD_SAM").text).strip())
				except:
					cfg.signList["SAM_THRESHOLD_" + str(b)] = 0
			cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " opened signature " + str(len(cfg.signIDs)))
		except Exception, err:
			cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
			cfg.mx.msgErr16()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
	# export signature to file
	def exportSignatureFile(self):
		signFile = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Export SCP training input"), "", "SCP file (*.scp)")
		if len(signFile) > 0:
			# create shapefile
			crs = cfg.utls.getCrs(cfg.shpLay)
			f = QgsFields()
			# add Class ID, macroclass ID and Info fields
			f.append(QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))
			f.append(QgsField(cfg.fldROIMC_info, cfg.QVariantSCP.String))
			f.append(QgsField(cfg.fldID_class, cfg.QVariantSCP.Int))
			f.append(QgsField(cfg.fldROI_info, cfg.QVariantSCP.String))
			f.append(QgsField(cfg.fldSCP_UID, cfg.QVariantSCP.String))
			# open shapefile
			if signFile.lower().endswith(".scp"):
				sL = unicode(signFile)
			else:
				sL = unicode(signFile) + ".scp"
			# shapefile
			zipName = cfg.osSCP.path.basename(unicode(sL))
			name = zipName[:-4]
			dT = cfg.utls.getTime()
			unzipDir = cfg.tmpDir + "/" + name + dT
			shpF = unzipDir + "/" + name + ".shp"
			sigFile = unzipDir + "/" + name + ".slf"
			oDir = cfg.utls.makeDirectory(unzipDir)
			QgsVectorFileWriter(unicode(shpF), "CP1250", f, QGis.WKBMultiPolygon , crs, "ESRI Shapefile")
			tSS = cfg.utls.addVectorLayer(shpF, name + dT, "ogr")
			tW = cfg.uidc.signature_list_tableWidget
			r = []
			signIDorig = cfg.signIDs.copy()
			cfg.signIDs = {}
			for i in tW.selectedIndexes():
				id = tW.item(i.row(), 6).text()
				cfg.signIDs["ID_" + str(id)] = id
				r.append(id)
			if len(tW.selectedIndexes()) == 0:
				c = tW.rowCount()
				for i in range(0, c):
					id = tW.item(i, 6).text()
					cfg.signIDs["ID_" + str(id)] = id
					r.append(id)
			self.saveSignatureList(sigFile)
			cfg.signIDs = signIDorig.copy()
			f = QgsFeature()
			tSS.startEditing()
			for f in cfg.shpLay.getFeatures():
				SCP_UID  = str(f[cfg.fldSCP_UID])
				if SCP_UID in r:
					tSS.addFeature(f)
			tSS.commitChanges()
			tSS.dataProvider().createSpatialIndex()
			tSS.updateExtents()
			# create zip file
			cfg.utls.zipDirectoryInFile(signFile, unzipDir)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures exported in: " + unicode(signFile))
			
	# export signature to shapefile
	def exportSignatureShapefile(self):
		signFile = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Export SCP training input"), "", "Shapefile (*.shp)")
		if len(signFile) > 0:
			# create shapefile
			crs = cfg.utls.getCrs(cfg.shpLay)
			f = QgsFields()
			# add Class ID, macroclass ID and Info fields
			f.append(QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))
			f.append(QgsField(cfg.fldROIMC_info, cfg.QVariantSCP.String))
			f.append(QgsField(cfg.fldID_class, cfg.QVariantSCP.Int))
			f.append(QgsField(cfg.fldROI_info, cfg.QVariantSCP.String))
			f.append(QgsField(cfg.fldSCP_UID, cfg.QVariantSCP.String))
			# open shapefile
			if signFile.lower().endswith(".shp"):
				sL = unicode(signFile)
			else:
				sL = unicode(signFile) + ".shp"
			# shapefile
			zipName = cfg.osSCP.path.basename(unicode(sL))
			name = zipName[:-4]
			dT = cfg.utls.getTime()
			shpF = sL
			QgsVectorFileWriter(unicode(shpF), "CP1250", f, QGis.WKBMultiPolygon , crs, "ESRI Shapefile")
			tSS = cfg.utls.addVectorLayer(shpF, name + dT, "ogr")
			tW = cfg.uidc.signature_list_tableWidget
			r = []
			for i in tW.selectedIndexes():
				id = tW.item(i.row(), 6).text()
				r.append(id)
			if len(tW.selectedIndexes()) == 0:
				c = tW.rowCount()
				for i in range(0, c):
					id = tW.item(i, 6).text()
					r.append(id)
	
			f = QgsFeature()
			tSS.startEditing()
			for f in cfg.shpLay.getFeatures():
				SCP_UID  = str(f[cfg.fldSCP_UID])
				if SCP_UID in r:
					tSS.addFeature(f)
			tSS.commitChanges()
			tSS.dataProvider().createSpatialIndex()
			tSS.updateExtents()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures exported in: " + unicode(signFile))
			
	# save signature to file
	def saveSignatureListToFile(self):
		try:
			cfg.classD.saveSignatureList(cfg.sigFile)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures saved in: " + unicode(cfg.sigFile))
		except Exception, err:
			cfg.mx.msgErr15()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								
	# open signature file
	def openLibraryFile(self, libraryFile):
		try:
			if cfg.bndSetUnit["UNIT"] != cfg.noUnit:
				libFile = cfg.utls.getOpenFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a library file"), "", "SCP file (*.scp);;USGS library (*.asc);;ASTER library (*.txt);;CSV (*.csv)")
				if len(libFile) > 0:
					cfg.uiUtls.addProgressBar()
					if libFile.lower().endswith(".asc"):
						cfg.sigImport.USGSLibrary(libFile)
					elif libFile.lower().endswith(".txt"):
						cfg.sigImport.ASTERLibrary(libFile)
					elif libFile.lower().endswith(".csv"):
						cfg.sigImport.CSVLibrary(libFile)
					elif libFile.lower().endswith(".scp"):
						self.importSLCSignatureList(libFile, "Yes")
					cfg.uiUtls.removeProgressBar()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " spectral library " + unicode(libFile))
			else:
				cfg.mx.msgWar8()
		except Exception, err:
			cfg.mx.msgWar8()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# export signatures to CSV library
	def exportToCSVLibrary(self):
		tW = cfg.uidc.signature_list_tableWidget
		r = []
		for i in tW.selectedIndexes():
			r.append(i.row())
		if len(r) > 0:
			v = list(set(r))
			d = cfg.utls.getExistingDirectory(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Export the highlighted signatures to CSV library"))
			if len(d) > 0:
				for b in v:
					mID = tW.item(b, 1).text()
					mC = tW.item(b, 2).text()
					cID = tW.item(b, 3).text()
					c = tW.item(b, 4).text()
					signFile = d + "/" + str(mC) + "_" + str(mID) + "_" + str(c) + "_" + str(cID) + str(".csv")
					# open file
					l = open(signFile, 'w')
					try:
						l.write("wavelength;reflectance;standardDeviation;waveLengthUnit \n")
						l.close()
					except Exception, err:
						cfg.mx.msgErr18()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
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
							cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					l.close()

	# set variable for vector classification
	def vectorCheckbox(self):
		if cfg.uidc.vector_output_checkBox.isChecked() is True:
			cfg.vectorOutputCheck = "Yes"
		else:
			cfg.vectorOutputCheck = "No"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.vectorOutputCheck))
		
	# zoom to preview
	def zoomToPreview(self):
		preP = cfg.utls.selectLayerbyName(cfg.lastPrev)
		if preP is not None:
			cfg.utls.setMapExtentFromLayer(preP)
			preP.triggerRepaint()
			cfg.cnvs.refresh()
			
			
		
##################################
	""" Table functions """
##################################
	
	# calculate signatures
	def calculateSignatures(self):
		tW = cfg.uidc.signature_list_tableWidget
		r = []
		for i in tW.selectedIndexes():
			r.append(i.row())
		v = list(set(r))
		if len(v) == 0:
			return 0
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Calculate signatures"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Calculate signatures for highlighted items?"))
		if a == "Yes":
			cfg.uiUtls.addProgressBar()
			progresStep = 100 / len(v)
			progress = 0
			for x in v:
				progress = progress * progresStep
				id = tW.item(x, 6).text()
				# if ROI
				if str(id) in cfg.ROI_SCP_UID.values():
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
					cfg.utls.calculateSignature(cfg.shpLay, cfg.rstrNm, rId, cfg.ROI_MC_ID[id], cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.ROI_C_Info[id], progress, progresStep, "No", "No", id)
				if id in cfg.signPlotIDs.values():
					cfg.classD.sigListToPlot(id)
					cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
			cfg.uiUtls.removeProgressBar()
			
	# merge highlighted signatures
	def mergeSelectedSignatures(self):
		tW = cfg.uidc.signature_list_tableWidget
		r = []
		for i in tW.selectedIndexes():
			r.append(i.row())
		if len(set(r)) > 1:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Merge signatures"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Merge highlighted signatures?"))
			if a == "Yes":
				cfg.uiUtls.addProgressBar()
				v = list(set(r))
				wl = []
				val = []
				min = []
				max = []
				vmin = []
				vmax = []
				unit = []
				covMat = []
				ids = []
				ROIcheck = []
				for x in v:
					id = tW.item(x, 6).text()
					# if ROI
					if str(id) in cfg.ROI_SCP_UID.values():
						ifd = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
						ids.append(ifd[0])
						ROIcheck.append(1)
					else:
						ROIcheck.append(0)
					# if not signatue
					if str(id) not in cfg.signIDs.values():
						rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
						cfg.utls.calculateSignature(cfg.shpLay, cfg.rstrNm, rId, cfg.ROI_MC_ID[id], cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.ROI_C_Info[id], None, None, "No", "No", id)
					if len(wl) == 0:
						wl = cfg.signList["WAVELENGTH_" + str(id)]
						unit = cfg.signList["UNIT_" + str(id)]
						MC_ID  = cfg.signList["MACROCLASSID_" + str(id)]
						MC_Info  = cfg.merged_name + cfg.signList["MACROCLASSINFO_" + str(id)]
						C_ID = cfg.signList["CLASSID_" + str(id)]
						C_Info = cfg.merged_name + cfg.signList["CLASSINFO_" + str(id)]
						color = cfg.signList["COLOR_" + str(id)]
						checkbox  = cfg.signList["CHECKBOX_" + str(id)]
						sigThr  = cfg.signList["MD_THRESHOLD_" + str(id)]
						sigThrML  = cfg.signList["ML_THRESHOLD_" + str(id)]
						sigThrSAM  = cfg.signList["SAM_THRESHOLD_" + str(id)]
					elif wl != cfg.signList["WAVELENGTH_" + str(id)] or unit != cfg.signList["UNIT_" + str(id)]:
						cfg.mx.msgErr35()
						return "No"
					val.append(cfg.signList["VALUES_" + str(id)])
					min.append(cfg.signList["LCS_MIN_" + str(id)])
					max.append(cfg.signList["LCS_MAX_" + str(id)])
					vmin.append(cfg.signList["MIN_VALUE_" + str(id)])
					vmax.append(cfg.signList["MAX_VALUE_" + str(id)])
					covMat.append(cfg.signList["COVMATRIX_" + str(id)])
				i = cfg.utls.signatureID()
				# if ROIs
				if 0 not in ROIcheck:
					attributeList = [cfg.ROI_MC_ID[id], cfg.merged_name + cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.merged_name + cfg.ROI_C_Info[id], i]
					cfg.utls.mergePolygons(cfg.shpLay, ids, attributeList)
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(i))
					cfg.utls.calculateSignature(cfg.shpLay, cfg.rstrNm, rId, cfg.ROI_MC_ID[id], cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.ROI_C_Info[id], None, None, "No", "No", i)
				else:
					covMatrixSum = 0
					try:
						for cvm in covMat:
							covMatrixSum = covMatrixSum + cvm
						covMatrix = covMatrixSum / len(covMat)
						cfg.np.linalg.inv(covMatrix)
					except:
						covMatrix = "No"
					cfg.uiUtls.updateBar(10)
					# calculate mean
					vals = cfg.np.array(val)
					val_mean = cfg.np.mean(vals, axis=0).tolist()
					mins = cfg.np.array(min)
					min_mean = cfg.np.mean(mins, axis=0).tolist()
					maxs = cfg.np.array(max)
					max_mean = cfg.np.mean(maxs, axis=0).tolist()
					vmins = cfg.np.array(vmin)
					vmin_mean = cfg.np.mean(vmins, axis=0).tolist()
					vmaxs = cfg.np.array(vmax)
					vmaxs_mean = cfg.np.mean(vmaxs, axis=0).tolist()
					# add spectral signature
					cfg.signList["CHECKBOX_" + str(i)] = cfg.QtSCP.Checked
					cfg.signList["MACROCLASSID_" + str(i)] = MC_ID
					cfg.signList["MACROCLASSINFO_" + str(i)] = MC_Info
					cfg.signList["CLASSID_" + str(i)] = C_ID
					cfg.signList["CLASSINFO_" + str(i)] = C_Info
					cfg.signList["WAVELENGTH_" + str(i)] = wl
					cfg.signList["VALUES_" + str(i)] = val_mean
					cfg.signList["LCS_MIN_" + str(i)] = min_mean
					cfg.signList["LCS_MAX_" + str(i)] = max_mean
					cfg.signList["MIN_VALUE_" + str(i)] = vmin_mean
					cfg.signList["MAX_VALUE_" + str(i)] = vmaxs_mean			
					cfg.signList["ROI_SIZE_" + str(i)] = 0
					cfg.signList["COVMATRIX_" + str(i)] = covMatrix
					cfg.signList["MD_THRESHOLD_" + str(i)] = sigThr
					cfg.signList["ML_THRESHOLD_" + str(i)] = sigThrML
					cfg.signList["SAM_THRESHOLD_" + str(i)] = sigThrSAM
					# counter
					n = 0
					m = []
					sdL = []
					for wi in wl:
						m.append(val_mean[n * 2])
						sdL.append(val_mean[n * 2 +1])
						n = n + 1
					cfg.signList["MEAN_VALUE_" + str(i)] = m
					cfg.signList["SD_" + str(i)] = sdL
					if unit is None:
						unit = cfg.bndSetUnit["UNIT"]
					cfg.signList["UNIT_" + str(i)] = unit
					cfg.signList["COLOR_" + str(i)] = color
					cfg.signIDs["ID_" + str(i)] = i
				cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
				# select row
				row = cfg.utls.highlightRowInTable(tW, i, 6)
				tW.selectRow(row)
				cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " merged signatures: " + str(v))

	# remove selected signatures
	def removeSelectedSignatures(self):
		tW = cfg.uidc.signature_list_tableWidget
		if len(tW.selectedIndexes()) > 0:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Delete signatures"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to delete highlighted ROIs and signatures?"))
			if a == "Yes":
				r = []
				for i in tW.selectedIndexes():
					r.append(i.row())
				v = list(set(r))
				ids = []
				for x in v:
					id = tW.item(x, 6).text()
					if id in cfg.signIDs.values():
						cfg.classD.deleteSignatureByID(id)
					if id in cfg.ROI_SCP_UID.values():
						rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
						for rI in rId:
							ids.append(rI)
				if cfg.shpLay is not None:
					cfg.utls.deleteFeatureShapefile(cfg.shpLay, ids)
				cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " removed signatures: " + str(v))
		
	# delete signature by ID
	def deleteSignatureByID(self, id):
		cfg.signIDs.pop("ID_" + str(id))
		cfg.signList.pop("MACROCLASSID_" + str(id))
		cfg.signList.pop("MACROCLASSINFO_" + str(id))
		cfg.signList.pop("CLASSID_" + str(id))
		cfg.signList.pop("CLASSINFO_" + str(id))
		cfg.signList.pop("WAVELENGTH_" + str(id))
		try:
			cfg.signList.pop("MEAN_VALUE_" + str(id))
			cfg.signList.pop("SD_" + str(id))
		except:
			pass
		cfg.signList.pop("VALUES_" + str(id))
		cfg.signList.pop("LCS_MIN_" + str(id))
		cfg.signList.pop("LCS_MAX_" + str(id))
		cfg.signList.pop("MIN_VALUE_" + str(id))
		cfg.signList.pop("MAX_VALUE_" + str(id))
		cfg.signList.pop("ROI_SIZE_" + str(id))
		cfg.signList.pop("COLOR_" + str(id))
		cfg.signList.pop("UNIT_" + str(id))
		cfg.signList.pop("COVMATRIX_" + str(id))
		cfg.signList.pop("MD_THRESHOLD_" + str(id))
		cfg.signList.pop("ML_THRESHOLD_" + str(id))
		cfg.signList.pop("SAM_THRESHOLD_" + str(id))
		try:
			cfg.scaPlT.removeScatterByID(id)
			cfg.scaPlT.scatterPlotListTable(cfg.uiscp.scatter_list_plot_tableWidget)
		except:
			pass
		
	# add signatures to spectral plot
	def addSignatureToSpectralPlot(self):
		tW = cfg.uidc.signature_list_tableWidget
		r = []
		check = "Yes"
		for i in tW.selectedIndexes():
			r.append(i.row())
		v = list(set(r))
		if len(v) > 0:
			progresStep = 100 / len(v)
			progress = 0
			cfg.uiUtls.addProgressBar()
			for x in v:
				progress = progress * progresStep
				id = tW.item(x, 6).text()
				if id in cfg.signIDs.values():
					if id not in cfg.signPlotIDs.values():
						cfg.classD.sigListToPlot(id)
				else:
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
					cfg.utls.calculateSignature(cfg.shpLay, cfg.rstrNm, rId, cfg.ROI_MC_ID[id], cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.ROI_C_Info[id], progress, progresStep, "No", "No", id)
					cfg.classD.sigListToPlot(id)
					check = "No"
			cfg.uiUtls.removeProgressBar()
			if check == "No":
				cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
			cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			cfg.utls.spectralPlotTab()
		else:
			cfg.utls.spectralPlotTab()
			
	# add ROI to scatter plot
	def addROIToScatterPlot(self):
		tW = cfg.uidc.signature_list_tableWidget
		r = []
		for i in tW.selectedIndexes():
			r.append(i.row())
		v = list(set(r))
		if len(v) > 0:
			progresStep = 100 / len(v)
			progress = 0
			cfg.uiUtls.addProgressBar()
			for x in v:
				progress = progress * progresStep
				id = tW.item(x, 6).text()
				if str(id) in cfg.ROI_SCP_UID.values():
					h = cfg.utls.calculateScatterPlot(cfg.shpLay, cfg.fldSCP_UID, str(id))
					# add ROI to scatter plot table
					cfg.scaPlT.sigListToScatterPlot(id, h, [cfg.scatterBandX, cfg.scatterBandY])
			cfg.scaPlT.scatterPlotListTable(cfg.uiscp.scatter_list_plot_tableWidget)
			cfg.utls.scatterPlotTab()
			cfg.uiUtls.removeProgressBar()
		else:
			cfg.utls.scatterPlotTab()

	# signature list to plot list
	def sigListToPlot(self, id):
		cfg.signPlotIDs["ID_" + str(id)] = id
		cfg.spectrPlotList["MACROCLASSID_" + str(id)] = cfg.signList["MACROCLASSID_" + str(id)]
		cfg.spectrPlotList["MACROCLASSINFO_" + str(id)] = cfg.signList["MACROCLASSINFO_" + str(id)]
		cfg.spectrPlotList["CLASSID_" + str(id)] = cfg.signList["CLASSID_" + str(id)]
		cfg.spectrPlotList["CLASSINFO_" + str(id)] = cfg.signList["CLASSINFO_" + str(id)]
		cfg.spectrPlotList["VALUES_" + str(id)] = cfg.signList["VALUES_" + str(id)]
		cfg.spectrPlotList["ROI_SIZE_" + str(id)] = cfg.signList["ROI_SIZE_" + str(id)]
		cfg.spectrPlotList["MIN_VALUE_" + str(id)] = cfg.signList["MIN_VALUE_" + str(id)]
		cfg.spectrPlotList["MAX_VALUE_" + str(id)] = cfg.signList["MAX_VALUE_" + str(id)]
		cfg.spectrPlotList["LCS_MIN_" + str(id)] = cfg.signList["LCS_MIN_" + str(id)]
		cfg.spectrPlotList["LCS_MAX_" + str(id)] = cfg.signList["LCS_MAX_" + str(id)]
		cfg.spectrPlotList["WAVELENGTH_" + str(id)] = cfg.signList["WAVELENGTH_" + str(id)]
		cfg.spectrPlotList["MEAN_VALUE_" + str(id)] = cfg.signList["MEAN_VALUE_" + str(id)]
		cfg.spectrPlotList["SD_" + str(id)] = cfg.signList["SD_" + str(id)]
		cfg.spectrPlotList["COLOR_" + str(id)] = cfg.signList["COLOR_" + str(id)]
		cfg.spectrPlotList["CHECKBOX_" + str(id)] = 2
		cfg.spectrPlotList["UNIT_" + str(id)] = cfg.signList["UNIT_" + str(id)] 
		cfg.spectrPlotList["COVMATRIX_" + str(id)] = cfg.signList["COVMATRIX_" + str(id)]
		cfg.spectrPlotList["MD_THRESHOLD_" + str(id)] = cfg.signList["MD_THRESHOLD_" + str(id)]
		cfg.spectrPlotList["ML_THRESHOLD_" + str(id)] = cfg.signList["ML_THRESHOLD_" + str(id)]
		cfg.spectrPlotList["SAM_THRESHOLD_" + str(id)] = cfg.signList["SAM_THRESHOLD_" + str(id)]

	# get all ROI attributes
	def getROIAttributes(self, layerName):
		l = cfg.utls.selectLayerbyName(layerName)
		cfg.ROI_MC_ID = {}
		cfg.ROI_MC_Info = {}
		cfg.ROI_C_ID = {}
		cfg.ROI_C_Info = {}
		cfg.ROI_Count = {}
		cfg.ROI_ShapeID = {}
		cfg.ROI_SCP_UID = {}
		if l is not None:
			i = 0
			for f in l.getFeatures():
				id = f.id()
				SCP_UID  = str(f[cfg.fldSCP_UID])
				try:
					cfg.ROI_SCP_UID[SCP_UID]= SCP_UID
					cfg.ROI_MC_ID[SCP_UID]= str(f[cfg.fldMacroID_class])
					cfg.ROI_MC_Info[SCP_UID] = str(f[cfg.fldROIMC_info])
					cfg.ROI_C_ID[SCP_UID] = str(f[cfg.fldID_class])
					cfg.ROI_C_Info[SCP_UID] = str(f[cfg.fldROI_info])
					cfg.ROI_Count[SCP_UID]= str(i)
					cfg.ROI_ShapeID[SCP_UID]= str(id)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.mx.msg3()
				i = i + 1
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ROI attributes")
			
	# Create ROI list
	def ROIListTable(self, layerName, table, checkstate=0):
		# get ROIs
		cfg.classD.getROIAttributes(layerName)
		# checklist
		l = table
		l.blockSignals(True)
		l.setSortingEnabled(False)
		cfg.utls.clearTable(l)
		# add ROI items
		b = 0
		try:
			for k in sorted(cfg.ROI_SCP_UID.values()):
				cfg.utls.insertTableRow(l, b, 20)	
				if str(k) in cfg.signIDs.values():
					cfg.utls.addTableItem(l, "checkbox", b, 0, "Yes", None, cfg.signList["CHECKBOX_" + str(k)])
					cfg.utls.addTableItem(l, cfg.ROISigTypeNm, b, 1, "No")
					cfg.utls.addTableItem(l, "", b, 5, "Yes", cfg.signList["COLOR_" + str(k)])
					# for signature list coherence
					try:
						cfg.signList["MACROCLASSID_" + str(k)] = int(cfg.ROI_MC_ID[k])
					except:
						cfg.signList["MACROCLASSID_" + str(k)] = int(0)
					cfg.signList["MACROCLASSINFO_" + str(k)] = str(cfg.ROI_MC_Info[k])
					try:
						cfg.signList["CLASSID_" + str(k)] = int(cfg.ROI_C_ID[k])
					except:
						cfg.signList["CLASSID_" + str(k)] = int(0)
					cfg.signList["CLASSINFO_" + str(k)] = str(cfg.ROI_C_Info[k])
				else:
					try:
						cfg.utls.addTableItem(l, "checkbox", b, 0, "Yes", None, cfg.signList["CHECKBOX_" + str(k)])
					except:
						cfg.utls.addTableItem(l, "checkbox", b, 0, "Yes", None, cfg.QtSCP.Checked)
						cfg.signList["CHECKBOX_" + str(k)] = 2
					cfg.utls.addTableItem(l, cfg.ROITypeNm, b, 1, "No", cfg.QtGuiSCP.QColor(200, 200, 200))
					cfg.utls.addTableItem(l, "", b, 5, "Yes")
					# for signature list coherence
				try:
					cfg.utls.addTableItem(l, int(cfg.ROI_MC_ID[k]), b, 2)
				except:
					cfg.utls.addTableItem(l, int(0), b, 2)
				try:
					cfg.utls.addTableItem(l, int(cfg.ROI_C_ID[k]), b, 3)
				except:
					cfg.utls.addTableItem(l, int(0), b, 3)
				cfg.utls.addTableItem(l, str(cfg.ROI_C_Info[k]), b, 4, "Yes", None, None, str(cfg.ROI_C_Info[k]))
				cfg.utls.addTableItem(l, str(k), b, 6)
				b = b +1
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr43()
		for k in sorted(cfg.signIDs.values()):
			if str(k) not in cfg.ROI_SCP_UID.values():
				cfg.utls.insertTableRow(l, b, 20)	
				cfg.utls.addTableItem(l, "checkbox", b, 0, "Yes", None, cfg.signList["CHECKBOX_" + str(k)])
				cfg.utls.addTableItem(l, cfg.SIGTypeNm, b, 1, "No")
				cfg.utls.addTableItem(l, "", b, 5, "Yes", cfg.signList["COLOR_" + str(k)])
				cfg.utls.addTableItem(l, int(cfg.signList["MACROCLASSID_" + str(k)]), b, 2)
				cfg.utls.addTableItem(l, int(cfg.signList["CLASSID_" + str(k)]), b, 3)
				cfg.utls.addTableItem(l, str(cfg.signList["CLASSINFO_" + str(k)]), b, 4, "Yes", None, None, str(cfg.signList["CLASSINFO_" + str(k)]))
				cfg.utls.addTableItem(l, str(k), b, 6)
				b = b +1
		l.show()
		l.setSortingEnabled(True)
		l.blockSignals(False)
		cfg.signT.signatureThresholdListTable()
		cfg.LCSignT.LCSignatureThresholdListTable()
		# info completer
		cfg.classD.roiInfoCompleter()
		cfg.classD.roiMacroclassInfoCompleter()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " roi list table created")
						
##################################
	""" Interface functions """
##################################
	
	# set rapid ROI band
	def rapidROIband(self):
		# band set
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			iB = len(cfg.bndSet)
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
			try:
				iB = i.bandCount()
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				iB = 1
		if cfg.uidc.rapidROI_band_spinBox.value() > iB:
			cfg.uidc.rapidROI_band_spinBox.setValue(iB)
		cfg.ROIband = cfg.uidc.rapidROI_band_spinBox.value()
		cfg.utls.writeProjectVariable("rapidROIBand", str(cfg.ROIband))
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "ROI band: " + str(cfg.ROIband))
		
	# Activate rapid ROI creation
	def rapidROICheckbox(self):
		if cfg.uidc.rapid_ROI_checkBox.isChecked() is True:
			cfg.rpdROICheck = "Yes"
		else:
			cfg.rpdROICheck = "No"
		cfg.utls.writeProjectVariable("rapidROI", cfg.rpdROICheck)
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.rpdROICheck))
		
	# set vegetation index name
	def vegetationIndexName(self):
		cfg.indName = str(cfg.uidc.vegetation_index_comboBox.currentText())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "index name: " + str(cfg.indName))
		
	# Activate vegetation index checkbox
	def vegetationIndexCheckbox(self):
		if cfg.uidc.display_cursor_checkBox.isChecked() is True:
			cfg.vegIndexCheck = "Yes"
			cfg.msgWar8check = "No"
		else:
			cfg.vegIndexCheck = "No"
		cfg.utls.writeProjectVariable("vegetationIndex", cfg.vegIndexCheck)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.vegIndexCheck))
	
	# set ROI macroclass ID
	def setROIMacroID(self):
		cfg.ROIMacroID = cfg.uidc.ROI_Macroclass_ID_spin.value()
		cfg.utls.writeProjectVariable("ROIMacroIDField", str(cfg.ROIMacroID))
		for i in cfg.MCID_List:
			if str(cfg.ROIMacroID) == i[0]:
				cfg.uidc.ROI_Macroclass_line.setText(i[1])
				cfg.ROIMacroClassInfo = str(i[1])
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi macroclass id: " + str(cfg.ROIMacroID))
		
	# set ROI class ID
	def setROIID(self):
		cfg.ROIID = cfg.uidc.ROI_ID_spin.value()
		cfg.utls.writeProjectVariable("ROIIDField", str(cfg.ROIID))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi id: " + str(cfg.ROIID))

	# set ROI class info
	def roiClassInfo(self):
		cfg.uidc.ROI_Class_line.blockSignals(True)
		iTxt = str(cfg.uidc.ROI_Class_line.text().encode('ascii','replace'))
		cfg.ROIInfo = str(iTxt)
		cfg.utls.writeProjectVariable("ROIInfoField", str(cfg.ROIInfo))
		cfg.uidc.ROI_Class_line.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi info: " + str(cfg.ROIInfo))
		
	# ROI info completer
	def roiInfoCompleter(self):
		if cfg.shpLay is not None:
			try:
				l = cfg.utls.getFieldAttributeList(cfg.shpLay, cfg.fldROI_info)
				# class names
				cfg.cmplClsNm = cfg.QtGuiSCP.QCompleter(l)
				cfg.uidc.ROI_Class_line.setCompleter(cfg.cmplClsNm)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))

	# set custom expression
	def customExpressionEdited(self):
		cfg.customExpression = str(cfg.uidc.custom_index_lineEdit.text())
		cfg.utls.writeProjectVariable("customExpression", str(cfg.customExpression))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " expression: " + str(cfg.customExpression))
			
	# set ROI class info
	def roiMacroclassInfo(self):
		cfg.uidc.ROI_Macroclass_line.blockSignals(True)
		iTxt = str(cfg.uidc.ROI_Macroclass_line.text().encode('ascii','replace'))
		cfg.ROIMacroClassInfo = str(iTxt)
		cfg.utls.writeProjectVariable("ROIMacroclassInfoField", str(cfg.ROIMacroClassInfo))
		cfg.uidc.ROI_Macroclass_line.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi info: " + str(cfg.ROIInfo))
			
	# ROI info completer
	def roiMacroclassInfoCompleter(self):
		if cfg.shpLay is not None:
			try:
				MCID_LIST = cfg.classD.exportMCIDList()
				l = [MC[1] for MC in MCID_LIST]
				# class names
				cfg.cmplMClsNm = cfg.QtGuiSCP.QCompleter(l)
				cfg.uidc.ROI_Macroclass_line.setCompleter(cfg.cmplMClsNm)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	def editedCell(self, row, column):
		tW = cfg.uidc.signature_list_tableWidget
		tW.blockSignals(True)
		id = tW.item(row, 6).text()
		if column == 0:
			cfg.signList["CHECKBOX_" + str(id)] = tW.item(row, column).checkState()
		elif column == 5:
			cfg.utls.setTableItem(tW, row, column, "")
			tW.clearSelection()
		elif column == 2:
			try:
				v = int(tW.item(row, column).text())
				if v < 0:
					v = 0
					cfg.utls.setTableItem(tW, row, column, str(v))
					cfg.mx.msg17()
				cfg.signList["MACROCLASSID_" + str(id)] = v
				if id in cfg.ROI_SCP_UID.values():
					cfg.ROI_MC_ID[id] = v
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
					for rI in rId:
						cfg.utls.editFeatureShapefile(cfg.shpLay, rI, cfg.fldMacroID_class, v)
			except:
				tW.setItem(row, column, QTableWidgetItem(str(cfg.signList["MACROCLASSID_" + str(id)])))
		elif column == 3:
			try:
				v = int(tW.item(row, column).text())
				if v < 0:
					v = 0
					cfg.utls.setTableItem(tW, row, column, str(v))
					cfg.mx.msg17()
				cfg.signList["CLASSID_" + str(id)] = v
				if id in cfg.ROI_SCP_UID.values():
					cfg.ROI_C_ID[id] = v
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
					for rI in rId:
						cfg.utls.editFeatureShapefile(cfg.shpLay, rI, cfg.fldID_class, v)
			except:
				tW.setItem(row, column, QTableWidgetItem(str(cfg.signList["CLASSID_" + str(id)])))
		elif column == 4:
			iTxt2 = tW.item(row, column).text().encode('ascii','replace')
			cfg.signList["CLASSINFO_" + str(id)] = iTxt2
			cfg.utls.setTableItem(tW, row, column, iTxt2)
			if id in cfg.ROI_SCP_UID.values():
				cfg.ROI_C_Info[id] = iTxt2
				rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
				for rI in rId:
					cfg.utls.editFeatureShapefile(cfg.shpLay, rI, cfg.fldROI_info, iTxt2)
		tW.blockSignals(False)			
		cfg.LCSignT.LCSignatureThresholdListTable()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "edited cell" + str(row) + ";" + str(column))
		
	def McIdEditedCell(self, row, column):
		tW = cfg.uidc.macroclass_color_tableWidget
		tW.blockSignals(True)
		if column == 0:
			pass
		elif column == 1:
			pass
		elif column == 2:
			cfg.utls.setTableItem(tW, row, column, "")
			tW.clearSelection()
		tW.blockSignals(False)
		cfg.classD.roiMacroclassInfoCompleter()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "edited cell" + str(row) + ";" + str(column))

	# check if MCID in table
	def checkMCIDList(self, MCID, MCInfo, color):
		tW = cfg.uidc.macroclass_color_tableWidget
		c = tW.rowCount()
		mC = []
		for b in range(0, c):
			mID = tW.item(b, 0).text()
			mC.append(str(mID))
		if str(MCID) not in mC:
			cfg.classD.addMCIDrow(MCID, MCInfo, color)
		MCID_LIST = cfg.classD.exportMCIDList()
			
	# add MCID to table
	def addMCIDrow(self, MCID, MCInfo, color):
		tW = cfg.uidc.macroclass_color_tableWidget
		tW.blockSignals(True)
		c = tW.rowCount()
		cfg.utls.insertTableRow(tW, c)	
		cfg.utls.addTableItem(tW, int(MCID), c, 0)
		cfg.utls.addTableItem(tW, MCInfo, c, 1)
		cfg.utls.addTableItem(tW, "", c, 2, "Yes", color)
		tW.blockSignals(False)
			
	# create MCID list for symbology
	def createMCIDList(self):
		tW = cfg.uidc.macroclass_color_tableWidget
		sL = []
		s = []
		c = tW.rowCount()
		for b in range(0, c):
			mID = tW.item(b, 0).text()
			mC = tW.item(b, 1).text()
			c = tW.item(b, 2).backgroundColor()
			s = []
			s.append(mID)
			s.append(mC)
			s.append(None)
			s.append(None)
			s.append(None)
			s.append(None)
			s.append(c)
			sL.append(s)
		return sL
			
	# import MCID list for symbology
	def importMCIDList(self, MCIDList):
		tW = cfg.uidc.macroclass_color_tableWidget
		cfg.utls.clearTable(tW)
		for i in MCIDList:
			cfg.classD.addMCIDrow(i[0], i[1], cfg.QtGuiSCP.QColor(i[2]))
		
	# export MCID list for symbology
	def exportMCIDList(self):
		tW = cfg.uidc.macroclass_color_tableWidget
		sL = []
		s = []
		c = tW.rowCount()
		for b in range(0, c):
			mID = tW.item(b, 0).text()
			mC = tW.item(b, 1).text()
			c = tW.item(b, 2).backgroundColor()
			s = []
			s.append(mID)
			s.append(mC)
			s.append(c.toRgb().name())
			sL.append(s)
		cfg.MCID_List = sL
		return sL

	# MCID table double click
	def McIdDoubleClick(self, index):
		if index.column() == 2:
			c = cfg.utls.selectColor()
			if c is not None:
				tW = cfg.uidc.macroclass_color_tableWidget
				r = []
				for i in tW.selectedIndexes():
					r.append(i.row())
				v = list(set(r))
				for x in v:
					tW.item(x, 2).setBackground(c)
					tW.clearSelection()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " index: " + str(index))
		
	# add row to table
	def addMCIDToTable(self):
		tW = cfg.uidc.macroclass_color_tableWidget
		c = tW.rowCount()
		mC = []
		mC.append(0)
		for b in range(0, c):
			mID = tW.item(b, 0).text()
			mC.append(int(mID))
		MCID = max(mC) + 1
		cfg.classD.addMCIDrow(MCID, "", cfg.QtGuiSCP.QColor("#000000"))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "added row " + str(c))

	def removeMCIDFromTable(self):
		cfg.utls.removeRowsFromTable(cfg.uidc.macroclass_color_tableWidget)
		
	# signature table double click
	def signatureListDoubleClick(self, index):
		if index.column() == 5:
			c = cfg.utls.selectColor()
			if c is not None:
				tW = cfg.uidc.signature_list_tableWidget
				r = []
				for i in tW.selectedIndexes():
					r.append(i.row())
				v = list(set(r))
				for x in v:
					k = tW.item(x, 6).text()
					cfg.signList["COLOR_" + str(k)] = c
					tW.item(x, 5).setBackground(c)
					tW.clearSelection()
		elif index.column() == 0:
			self.selectAllSignatures()
		else:
			cfg.classD.zoomToROI(index)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures index: " + str(index))

	# zoom to clicked ROI 
	def zoomToROI(self, index):
		l = cfg.utls.selectLayerbyName(cfg.trnLay)
		if l is not None:
			id = cfg.uidc.signature_list_tableWidget.item(index.row(), 6).text()
			if id in cfg.ROI_SCP_UID.values():
				rId = cfg.utls.getIDByAttributes(l, cfg.fldSCP_UID, str(id))
				cfg.utls.zoomToSelected(l, rId)
				cfg.lgnd.setLayerVisible(l, True)
				cfg.utls.moveLayerTop(l)

	# Activate signature calculation
	def signatureCheckbox(self):
		if cfg.uidc.signature_checkBox.isChecked() is True:
			cfg.sigClcCheck = "Yes"
			cfg.ui.signature_checkBox2.setCheckState(2)
		else:
			cfg.sigClcCheck = "No"
			cfg.ui.signature_checkBox2.setCheckState(0)
		cfg.utls.writeProjectVariable("calculateSignature", cfg.sigClcCheck)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.sigClcCheck))
		
##################################
	""" Shapefile functions """
##################################
			
	# Create new input 
	def createInput(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> create input click")
		try:
			if cfg.rstrNm is not None:
				sF = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Create SCP training input"), "", "SCP file (*.scp)")
				if len(sF) > 0:
					try:
						# band set
						if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
							iB = len(cfg.bndSet)
							# crs of loaded raster
							b = cfg.utls.selectLayerbyName(cfg.bndSet[0], "Yes")
							crs = cfg.utls.getCrs(b)
						else:
							# crs of loaded raster
							crs = cfg.utls.getCrs(cfg.rLay)
							iB = cfg.rLay.bandCount()
						f = QgsFields()
						# add Class ID, macroclass ID and Info fields
						f.append(QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))
						f.append(QgsField(cfg.fldROIMC_info, cfg.QVariantSCP.String))
						f.append(QgsField(cfg.fldID_class, cfg.QVariantSCP.Int))
						f.append(QgsField(cfg.fldROI_info, cfg.QVariantSCP.String))
						f.append(QgsField(cfg.fldSCP_UID, cfg.QVariantSCP.String))
						# open shapefile
						if sF.lower().endswith(".scp"):
							sL = unicode(sF)
						else:
							sL = unicode(sF) + ".scp"
						# shapefile
						zipName = cfg.osSCP.path.basename(unicode(sL))
						name = zipName[:-4]
						dT = cfg.utls.getTime()
						unzipDir = cfg.tmpDir + "/" + name + dT
						shpF = unzipDir + "/" + name + ".shp"
						oDir = cfg.utls.makeDirectory(unzipDir)
						QgsVectorFileWriter(unicode(shpF), "CP1250", f, QGis.WKBMultiPolygon , crs, "ESRI Shapefile")
						sigFile = unzipDir + "/" + name + ".slf"
						cfg.classD.saveSignatureList(sigFile)
						# create zip file
						cfg.utls.zipDirectoryInFile(sL, unzipDir)
						# open input
						cfg.classD.openInput(sL)
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< SCP created: " + "\"" + unicode(sL) + "\"")
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.ipt.refreshRasterLayer()
						cfg.mx.msg4()
			else:
				cfg.mx.msg4()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< create SCP fail: no raster")
				cfg.ipt.refreshRasterLayer()
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg4()

	# Save last ROI to shapefile 
	def saveROItoShapefile(self, progressbar = "Yes"):
		l = cfg.utls.selectLayerbyName(cfg.trnLay)
		if l is None:
			cfg.mx.msg3()
			return 0
		if progressbar is False:
			progressbar = "Yes"
		# check if layer was removed ## there is an issue if the removed layer was already saved in the project ##
		try:
			sN = unicode(cfg.shpLay.name())
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg3()
		# check if no layer is selected
		if cfg.shpLay is None:
			cfg.mx.msg3()
		# check if no ROI created
		elif cfg.lstROI is None:
			cfg.mx.msg6()
		else:
			if progressbar == "Yes":
				cfg.uiUtls.addProgressBar()
				cfg.uiUtls.updateBar(10)
			# get polygon from ROI
			try:
				# region growing ROI
				cfg.utls.copyFeatureToLayer(cfg.lstROI, 0, cfg.shpLay)
			except:
				# manual ROI
				cfg.utls.copyFeatureToLayer(cfg.lstROI, 1, cfg.shpLay)
			self.ROILastID = cfg.utls.getLastFeatureID(cfg.shpLay)
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(30)
			try:
				# start editing
				cfg.shpLay.startEditing()
				# set ID class attribute
				fdID = cfg.utls.fieldID(cfg.shpLay, str(cfg.fldID_class))
				cfg.shpLay.changeAttributeValue(self.ROILastID, fdID, cfg.ROIID)
				# set macroclass ID attribute
				fdMID = cfg.utls.fieldID(cfg.shpLay, str(cfg.fldMacroID_class))
				cfg.shpLay.changeAttributeValue(self.ROILastID, fdMID, cfg.ROIMacroID)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.shpLay.startEditing()	
				cfg.shpLay.dataProvider().deleteFeatures([self.ROILastID])
				cfg.shpLay.commitChanges()
				cfg.shpLay.dataProvider().createSpatialIndex()
				cfg.uidc.undo_save_Button.setEnabled(False)
				a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Add required fds"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "It appears that the shapefile ") + cfg.shpLay.name() + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", " is missing some fields that are required for the signature calculation. \nDo you want to add the required fields to this shapefile?"))
				if a == "Yes":
					fds = []
					fds.append(QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))	
					cfg.shpLay.startEditing()
					aF = cfg.shpLay.dataProvider().addAttributes(fds)
					# commit changes
					cfg.shpLay.commitChanges()
					if progressbar == "Yes":
						cfg.uiUtls.removeProgressBar()
					return 1
				else:
					if progressbar == "Yes":
						cfg.uiUtls.removeProgressBar()
					return 0
			# set ROI Class info attribute
			fdInfo = cfg.utls.fieldID(cfg.shpLay, str(cfg.fldROI_info))
			cfg.shpLay.changeAttributeValue(self.ROILastID, fdInfo, cfg.ROIInfo)
			# set ROI Macroclass info attribute
			fdMCInfo = cfg.utls.fieldID(cfg.shpLay, str(cfg.fldROIMC_info))
			cfg.shpLay.changeAttributeValue(self.ROILastID, fdMCInfo, cfg.ROIMacroClassInfo)
			# set SCP UID attribute
			UID = cfg.utls.signatureID()
			SCP_UID = cfg.utls.fieldID(cfg.shpLay, str(cfg.fldSCP_UID))
			cfg.shpLay.changeAttributeValue(self.ROILastID, SCP_UID, UID)
			# commit changes
			cfg.shpLay.commitChanges()
			cfg.uidc.undo_save_Button.setEnabled(True)
			try:
				self.clearCanvasPoly()
			except:
				pass
			try:
				self.clearROICanvas()
			except:
				pass
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(40)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi: " + str(cfg.ROIID) + ", " + str(cfg.ROIInfo) + " saved to shapefile: " + unicode(cfg.shpLay.name()))
			# calculate signature if checkbox is yes
			if cfg.uidc.signature_checkBox.isChecked() is True:
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(50)
					cfg.utls.calculateSignature(cfg.shpLay, cfg.rstrNm, [self.ROILastID], cfg.ROIMacroID, cfg.ROIMacroClassInfo, cfg.ROIID, cfg.ROIInfo, 50, 40, "No", "No", UID)
				else:
					cfg.utls.calculateSignature(cfg.shpLay, cfg.rstrNm, [self.ROILastID], cfg.ROIMacroID, cfg.ROIMacroClassInfo, cfg.ROIID, cfg.ROIInfo, None, None, "No", "No", UID)
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(90)
			cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
			try:
				c = cfg.signList["COLOR_" + str(UID)]
				cfg.classD.checkMCIDList(cfg.ROIMacroID, cfg.ROIMacroClassInfo, c)
			except:
				c, cc = cfg.utls.randomColor()
				cfg.classD.checkMCIDList(cfg.ROIMacroID, cfg.ROIMacroClassInfo, c)
			# increase C_ID
			v = cfg.uidc.ROI_ID_spin.value()
			cfg.uidc.ROI_ID_spin.setValue(v+1)
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(100)
				cfg.uiUtls.removeProgressBar()
				
	# delete last saved ROI
	def undoSaveROI(self):
		l = cfg.utls.selectLayerbyName(cfg.trnLay)
		if l is None:
			cfg.mx.msg3()
			return 0
		# check if layer was removed ## there is an issue if the removed layer was already saved in the project ##
		try:
			s = str(cfg.shpLay.name())
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg3()
		# check if no layer is selected
		if cfg.shpLay is None:
			cfg.mx.msg3()
		# check if no ROI created
		elif cfg.lstROI is None:
			cfg.mx.msg6()
		else:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Undo save ROI"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to delete the last saved ROI?"))
			if a == "Yes":
				f = cfg.utls.getFeaturebyID(cfg.shpLay, self.ROILastID)
				SCP_UID  = str(f[cfg.fldSCP_UID])
				cfg.utls.deleteFeatureShapefile(cfg.shpLay, [self.ROILastID])
				try:
					cfg.classD.deleteSignatureByID(SCP_UID)
				except:
					pass
				cfg.uidc.undo_save_Button.setEnabled(False)
				cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
				cfg.cnvs.refresh()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi deleted: " + str(self.ROILastID))