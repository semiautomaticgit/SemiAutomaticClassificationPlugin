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

class ClassificationTab:

	def __init__(self):
		pass
	

	# set algorithm
	def algorithmName(self):
		algName = cfg.ui.algorithm_combo.currentText()
		#idAlg = cfg.ui.algorithm_combo.findText(cfg.algName)
		idAlg = cfg.ui.algorithm_combo.currentIndex()
		if idAlg == 0:
			cfg.algName = cfg.algMinDist
		elif idAlg == 1:
			cfg.algName = cfg.algML
		elif idAlg == 2:
			cfg.algName = cfg.algSAM
		else:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'algorithm name: error ')
		if str(cfg.algName) == cfg.algML:
			if cfg.algThrshld > 100:
				cfg.mx.msg10()
				cfg.ui.alg_threshold_SpinBox.setValue(100)
		elif str(cfg.algName) == cfg.algSAM:
			if cfg.algThrshld > 90:
				cfg.mx.msg11()
				cfg.ui.alg_threshold_SpinBox.setValue(90)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'algorithm name: ' + str(cfg.algName))
				
	# set algorithm threshold
	def algorithmThreshold(self):
		cfg.algThrshld = cfg.ui.alg_threshold_SpinBox.value()
		if str(cfg.algName) == cfg.algML:
			if cfg.algThrshld > 100:
				cfg.ui.alg_threshold_SpinBox.setValue(100)
		elif str(cfg.algName) == cfg.algSAM:
			if cfg.algThrshld > 90:
				cfg.ui.alg_threshold_SpinBox.setValue(90)
		cfg.algThrshld = cfg.ui.alg_threshold_SpinBox.value()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'algorithm threshold: ' + str(cfg.algThrshld))
		
	# perform classification
	def runClassificationAction(self):
		if cfg.ui.alg_files_checkBox.isChecked() is True:
			algFilesCheck = 'Yes'
		else:
			algFilesCheck = None
		if cfg.ui.report_checkBox.isChecked() is True:
			report = 'Yes'
		else:
			report = None
		if cfg.ui.vector_output_checkBox.isChecked() is True:
			vector = 'Yes'
		else:
			vector = None
		if cfg.ui.macroclass_checkBox.isChecked() is True:
			macroclass = 'Yes'
		else:
			macroclass = None
		if cfg.ui.LC_signature_checkBox.isChecked():
			useLcs = 'Yes'
		else:
			useLcs = None
		if cfg.ui.LCS_class_algorithm_checkBox.isChecked():
			useLcsAlgorithm = 'Yes'
		else:
			useLcsAlgorithm = None
		if cfg.ui.LCS_leave_unclassified_checkBox.isChecked():
			leaveUnclassified = 'Yes'
		else:
			leaveUnclassified = None
		if cfg.ui.mask_checkBox.isChecked() is True:
			maskC = 'Yes'
		else:
			maskC = None
		maskPath = cfg.ui.mask_lineEdit.text()
		if len(maskPath) == 0:
			maskC = None
		bndStN = cfg.ui.band_set_comb_spinBox_12.value() - 1
		self.runClassification(bandSetNumber = bndStN, algorithmFilesCheck = algFilesCheck, reportCheck = report, vectorConversion = vector, useMacroclass = macroclass, useLcs = useLcs, useLcsAlgorithm = useLcsAlgorithm, LCSLeaveUnclassified = leaveUnclassified, maskCheckBox = maskC, maskPath = maskPath)
		
	# perform classification
	def runClassification(self, batch = 'No', outputClassification = None, bandSetNumber = None, algorithmFilesCheck = None, reportCheck = None, vectorConversion = None, algorithmName = None, useMacroclass = None, useLcs = None, useLcsAlgorithm = None, LCSLeaveUnclassified = None, maskCheckBox = None, maskPath = None):
		sL = cfg.classTab.getSignatureList(bandSetNumber, algorithmName)
		if self.trainSigCheck == 'Yes':
			if bandSetNumber is None:
				bandSetNumber = cfg.bndSetNumber
			if bandSetNumber >= len(cfg.bandSetsList):
				cfg.mx.msgWar25(bandSetNumber + 1)
				return 'No'	
			if batch == 'No':
				clssOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save classification output'), '', '*.tif', 'tif')
			else:
				clssOut = outputClassification
			if clssOut is not False:
				cfg.clssPth = clssOut
			cfg.QtWidgetsSCP.qApp.processEvents()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'classification output: ' + str(cfg.clssPth))	
			# check if can run classification
			ckC = 'Yes'
			if cfg.clssPth is None:
				ckC = 'No'
			# check if image is None
			elif cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes') is None and cfg.bandSetsList[bandSetNumber][0] != 'Yes':
				cfg.mx.msg4()
				cfg.ipt.refreshRasterLayer()
				ckC = 'No'
			if ckC != 'No':
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '>>> CLASSIFICATION STARTED')
				# base name
				nm = cfg.utls.fileNameNoExt(cfg.clssPth)
				if batch == 'No':
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
				# check band set
				ckB = 'Yes'
				if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
					ckB = cfg.utls.checkBandSet(bandSetNumber)
				cfg.uiUtls.updateBar(10)
				if ckB == 'Yes':
					cfg.bndSetMaskList = []
					img = cfg.bandSetsList[bandSetNumber][8]
				### if mask
					if maskCheckBox is None:
						if cfg.ui.mask_checkBox.isChecked() is True:
							maskCheckBox = 'Yes'
					if maskCheckBox == 'Yes':
						# mask shapefile path
						if maskPath is None:
							maskPath = cfg.ui.mask_lineEdit.text()
						# apply mask
						if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
							for x in range(0, len(cfg.bandSetsList[bandSetNumber][3])):
								tCD = cfg.utls.createTempRasterPath('tif')
								bCSS = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][3][x], 'Yes')
								bCPath = cfg.utls.layerSource(bCSS)
								oc = cfg.utls.clipRasterByShapefile(maskPath, bCPath, str(tCD), cfg.outTempRastFormat)
								cfg.bndSetMaskList.append(oc)
						else:
							# temp masked raster
							cfg.maskRstSrc = cfg.utls.createTempRasterPath('tif')
							b = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8])
							ql = cfg.utls.layerSource(b)
							cfg.maskRstSrc = cfg.utls.clipRasterByShapefile(maskPath, ql, str(cfg.maskRstSrc), cfg.outTempRastFormat)
						img = cfg.maskRasterNm
				### if not mask
					cfg.uiUtls.updateBar(20)
					if algorithmFilesCheck == 'Yes':
						rOBaseNm = cfg.osSCP.path.dirname(cfg.clssPth)
						algRasterPath = rOBaseNm + '/' + nm + '_' + cfg.algRasterNm + '.tif'
					else:
						algRasterPath = None
					if algorithmName is None:
						algorithmName = cfg.algName
					if useMacroclass is None:
						useMacroclass = cfg.macroclassCheck
					classificationOptions = [useLcs, useLcsAlgorithm, LCSLeaveUnclassified, cfg.algBandWeigths, cfg.algThrshld]
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' classification set: ' + str([algorithmName, img, sL, cfg.clssPth, useMacroclass, algRasterPath, 0, None, cfg.rasterCompression, bandSetNumber, classificationOptions]))
					ok, cOut, mOut, opOut = self.runAlgorithm(algorithmName, img, sL, cfg.clssPth, useMacroclass, algRasterPath, 0, None, cfg.rasterCompression, bandSetNumber, classificationOptions)
					if ok == 'Yes':
						c = cfg.utls.addRasterLayer(cfg.clssPth)
						cfg.utls.moveLayerTop(c)
						cfg.uiUtls.updateBar(80)
						# apply symbology
						self.applyClassSymbology(c, cfg.macroclassCheck, cfg.qmlFl, sL)
						# save qml file
						cfg.utls.saveQmlStyle(c, cfg.osSCP.path.dirname(clssOut) + '/' + nm + '.qml')
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '<<< CLASSIFICATION PERFORMED: ' + str(cfg.clssPth))
				### calculate report
					if reportCheck == 'Yes':
						reportOut = cfg.osSCP.path.dirname(cfg.clssPth) + '/' + nm + cfg.reportNm
						cfg.classRep.calculateClassificationReport(cfg.clssPth, 0, 'Yes', reportOut)
				### convert classification to vector
					cfg.uiUtls.updateBar(85)
					if vectorConversion == 'Yes':
						cfg.uiUtls.updateBar(85, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion to vector. Please wait ...'))
						vO = cfg.osSCP.path.dirname(cfg.clssPth) + '/' + nm + '.gpkg'
						cfg.utls.multiProcessRasterToVector(rasterPath = cfg.clssPth, outputVectorPath = vO, dissolveOutput = 'Yes')
						vl = cfg.utls.addVectorLayer(str(vO), cfg.utls.fileName(vO), 'ogr')
						# apply symbology
						self.applyClassSymbologyVector(vl, cfg.macroclassCheck, cfg.qmlFl, sL)
						cfg.utls.addLayerToMap(vl)
					cfg.uiUtls.updateBar(95)
				### copy signature raster
					if algorithmFilesCheck == 'Yes':
						if useLcs is None:
							if cfg.ui.LC_signature_checkBox.isChecked() is True:
								useLcs = 'Yes'
						try:
							c = cfg.utls.addRasterLayer(algRasterPath)
							if useLcs == 'Yes':
								cfg.utls.rasterSymbolLCSAlgorithmRaster(c)
							for r in opOut:
								c = cfg.utls.addRasterLayer(r)
								if useLcs == 'Yes':
									cfg.utls.rasterSymbolLCSAlgorithmRaster(c)
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'files copied')
						except Exception as err:
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
							cfg.mx.msgErr23()
				### ending
					cfg.uiUtls.updateBar(100)
					if batch == 'No':
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
					cfg.clssPth = None
			### band set check failed
				else:
					cfg.mx.msgErr6()
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
					cfg.clssPth = None
					cfg.bst.rasterBandName()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'band set check failed')
		else:
			cfg.mx.msg18()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'classification no')	

	# apply symbology to classification			
	def applyClassSymbology(self, classificationRaster, macroclassCheck, qmlFile, signatureList = None):
		# qml symbology
		if qmlFile == "":
			if macroclassCheck == 'Yes':
				signatureList = cfg.SCPD.createMCIDList()
				if len(signatureList) == 0:
					cfg.mx.msgWar19()
			cfg.utls.rasterSymbol(classificationRaster, signatureList, macroclassCheck)
		else:
			try:
				self.applyQmlStyle(classificationRaster, qmlFile)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							
	# apply symbology to classification vector	
	def applyClassSymbologyVector(self, classificationVector, macroclassCheck, qmlFile, signatureList = None):
		# qml symbology
		if qmlFile == '':
			if macroclassCheck == 'Yes':
				signatureList = cfg.SCPD.createMCIDList()
				if len(signatureList) == 0:
					cfg.mx.msgWar19()
			cfg.utls.vectorSymbol(classificationVector, signatureList, macroclassCheck)
		else:
			try:
				self.applyQmlStyle(classificationRaster, qmlFile)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				
	# Apply qml style to classifications and previews
	def applyQmlStyle(self, classLayer, stylePath):
		# read path from project istance
		p = cfg.qgisCoreSCP.QgsProject.instance()
		cfg.qmlFl = p.readEntry('SemiAutomaticClassificationPlugin', 'qmlfile', '')[0]
		classLayer.loadNamedStyle(cfg.qmlFl) 
		# refresh legend
		if hasattr(classLayer, 'setCacheImage'):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.utls.refreshLayerSymbology(classLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'classification symbology applied with qml: ' + str(stylePath))
			
	# calculate signatures for checked ROIs
	def getSignatureList(self, bandSetNumber = None, algorithmName = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		refreshTable = None
		for i in list(cfg.ROI_SCP_UID.values()):
			if str(i) not in list(cfg.signIDs.values()) and cfg.signList['CHECKBOX_' + str(i)] == 2:
				rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(i))
				cfg.utls.calculateSignature(cfg.shpLay, cfg.bandSetsList[bandSetNumber][8], rId, cfg.ROI_MC_ID[i], cfg.ROI_MC_Info[i], cfg.ROI_C_ID[i], cfg.ROI_C_Info[i], None, None, 'No', 'No', i)
				refreshTable = 'Yes'
		if refreshTable == 'Yes':
			cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
		id = list(cfg.signIDs.values())
		if algorithmName is None:
			algorithmName = cfg.algName
		signatureList = []
		for i in id:
			if cfg.signList['CHECKBOX_' + str(i)] == 2:
				s = []
				s.append(cfg.signList['MACROCLASSID_' + str(i)])
				s.append(cfg.signList['MACROCLASSINFO_' + str(i)])
				s.append(cfg.signList['CLASSID_' + str(i)])
				s.append(cfg.signList['CLASSINFO_' + str(i)])
				s.append(cfg.signList['VALUES_' + str(i)])
				s.append(cfg.signList['WAVELENGTH_' + str(i)])
				s.append(cfg.signList['COLOR_' + str(i)])
				s.append(cfg.signList['COVMATRIX_' + str(i)])
				s.append(cfg.signList['LCS_MIN_' + str(i)])
				s.append(cfg.signList['LCS_MAX_' + str(i)])
				if len(cfg.signList['WAVELENGTH_' + str(i)]) == len(list(cfg.bandSetsList[bandSetNumber][4])):
					if str(sorted(cfg.signList['WAVELENGTH_' + str(i)])) != str(sorted(cfg.bandSetsList[bandSetNumber][4])):
						cfg.mx.msgWar9(cfg.signList['MACROCLASSID_' + str(i)], cfg.signList['CLASSID_' + str(i)])
					# check if signature has covariance matrix if maximum likelihood
					if algorithmName == cfg.algML:
						if cfg.signList['COVMATRIX_' + str(i)] == 'No':
							cfg.mx.msgWar10(cfg.signList['MACROCLASSID_' + str(i)], cfg.signList['CLASSID_' + str(i)])
						else:
							signatureList.append(s)
					else:
						signatureList.append(s)
				else:
					cfg.mx.msgErr24(cfg.signList['MACROCLASSID_' + str(i)], cfg.signList['CLASSID_' + str(i)], 'No')
					self.trainSigCheck = 'No'
					return None
				if algorithmName == cfg.algMinDist:
					s.append(cfg.signList['MD_THRESHOLD_' + str(i)])
				elif algorithmName == cfg.algML:
					s.append(cfg.signList['ML_THRESHOLD_' + str(i)])
				elif algorithmName == cfg.algSAM:
					s.append(cfg.signList['SAM_THRESHOLD_' + str(i)])
		if len(signatureList) > 0:
			self.trainSigCheck = 'Yes'
		else:
			self.trainSigCheck = 'No'
		return signatureList
		
	# create classification preview
	def createPreview(self, point, algorithmRaster = 'No', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No'
		try:
			cfg.bandSetsList[bandSetNumber][8]
		except:
			cfg.mx.msg4()
			cfg.ipt.refreshRasterLayer()
			cfg.pntPrvw = None
		if cfg.pntPrvw != None:
			cfg.uiUtls.addProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '>>> PREVIEW click')
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			cfg.uiUtls.updateBar(10)
			lastPrevX = cfg.lastPrev
			# temp files
			tPMD = cfg.utls.createTempRasterPath('tif')
			pP = cfg.utls.createTempRasterPath('tif')
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'point (X,Y) = (%s,%s)' % (cfg.pntPrvw.x() , cfg.pntPrvw.y()))
			# signature list
			sL = cfg.classTab.getSignatureList()
			# input image
			if cfg.actionCheck == 'Yes' and  self.trainSigCheck == 'Yes':
				# check band set
				ckB = 'Yes'
				if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
					ckB = cfg.utls.checkBandSet(bandSetNumber)
				if ckB == 'Yes':
					cfg.uiUtls.updateBar(20)
					if cfg.ui.LC_signature_checkBox.isChecked():
						useLcs = 'Yes'
					else:
						useLcs = None
					if cfg.ui.LCS_class_algorithm_checkBox.isChecked():
						useLcsAlgorithm = 'Yes'
					else:
						useLcsAlgorithm = None
					if cfg.ui.LCS_leave_unclassified_checkBox.isChecked():
						leaveUnclassified = 'Yes'
					else:
						leaveUnclassified = None
					classificationOptions = [useLcs, useLcsAlgorithm, leaveUnclassified, cfg.algBandWeigths, cfg.algThrshld]
					# compression
					if int(cfg.prvwSz) <= 2000:
						compress = 'No'
					else:
						compress = cfg.rasterCompression
					if algorithmRaster == 'Yes':
						tPMA = cfg.utls.createTempRasterPath('vrt')
					else:
						tPMA = None		
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' classification set: ' + str([cfg.algName, cfg.bandSetsList[bandSetNumber][8], sL, pP, cfg.macroclassCheck, tPMA, int(cfg.prvwSz), point, compress, bandSetNumber, classificationOptions]))
					ok, cOut, mOut, opOut = self.runAlgorithm(cfg.algName, cfg.bandSetsList[bandSetNumber][8], sL, pP, cfg.macroclassCheck, tPMA, int(cfg.prvwSz), point, compress, bandSetNumber, classificationOptions)
					if ok == 'Yes':
						if algorithmRaster == 'No':
							r = cfg.utls.addRasterLayer(cOut)
							cfg.lastPrev = r.name()
							cfg.uiUtls.updateBar(80)
							# apply symbology
							self.applyClassSymbology(r, cfg.macroclassCheck, cfg.qmlFl, sL)
						else:
							r = cfg.utls.addRasterLayer(mOut)
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
							cfg.utls.moveLayer(preP, cfg.grpNm)
						cfg.utls.setGroupVisible(g, False)
						cfg.utls.setGroupExpanded(g, False)
						cfg.show_preview_radioButton2.setChecked(True)
					cfg.uiUtls.updateBar(100)
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '<<< PREVIEW created: ' + str(pP))
					# enable Redo button
					cfg.redoPreviewButton.setEnabled(True)
				else:
					cfg.uiUtls.removeProgressBar()
					cfg.cnvs.setRenderFlag(True)
					cfg.mx.msgErr6()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'preview no')	
			else:
				cfg.uiUtls.removeProgressBar()
				if self.trainSigCheck == 'No':
					cfg.mx.msg18()
				cfg.cnvs.setRenderFlag(True)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'preview no')
				
	# run classification algorithm
	def runAlgorithm(self, algorithmName, imageName, signatureList, outputRasterPath, macroclassCheck = 'No', algRasterPath = None, previewSize = 0, previewPoint = None, compress = 'No', bandSetNumber = None, classificationOptions = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if bandSetNumber >= len(cfg.bandSetsList):
			cfg.mx.msgWar25(bandSetNumber + 1)
			return 'No', None, None, None
		# if band set
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			# if masked bandset
			if imageName == cfg.maskRasterNm:
				bL = cfg.bndSetMaskList
				bandNumberList = []
				for i in range(0, len(bL)):
					bandNumberList.append(1)
			else:
				bS = cfg.bandSetsList[bandSetNumber][3]
				bL = []
				bandNumberList = []
				for i in range(0, len(bS)):
					bandNumberList.append(1)
					bSS = cfg.utls.selectLayerbyName(bS[i], 'Yes')
					try:
						bPath = cfg.utls.layerSource(bSS)
						bL.append(bPath)
					except Exception as err:
						cfg.mx.msg4()
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		else:
			# if masked raster
			if imageName == cfg.maskRasterNm:
				iR = cfg.maskRstSrc
			else:
				r = cfg.utls.selectLayerbyName(imageName, 'Yes')
				iR = cfg.utls.layerSource(r)
			bL = [iR]
			bandNumberList = []
			iBC = cfg.utls.getNumberBandRaster(iR)
			for i in range(1, iBC+1):
				bandNumberList.append(i)
		# subset raster if preview
		if 	previewSize > 0:
			# open input with GDAL
			rD = cfg.gdalSCP.Open(bL[0], cfg.gdalSCP.GA_ReadOnly)
			if rD is None:
				cfg.mx.msg4()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' None raster')
				return 'No', None, None, None
			# pixel size and origin from reference
			rGT = rD.GetGeoTransform()
			c = rD.RasterXSize
			r = rD.RasterYSize
			geoT = rD.GetGeoTransform()
			tLX = geoT[0]
			tLY = geoT[3]
			pSX = geoT[1]
			pSY = geoT[5]
			# start and end pixels
			sX = int((previewPoint.x() - tLX) / pSX) - int(previewSize / 2)
			sY = int((tLY - previewPoint.y()) / cfg.np.sqrt(pSY ** 2)) - int(previewSize / 2)
			lX = tLX + sX * pSX
			tY = tLY + sY * pSY
			if tY > tLY:
				tY = tLY
			if lX < tLX:
				lX = tLX
			eX = lX + previewSize * pSX
			eY = tY + previewSize * pSY
			lRX = tLX + c * pSX
			lRY = tLY + r * pSY
			if eX > lRX:
				eX = lRX
			if eY < lRY:
				eY = lRY
			xyRes = [pSX, cfg.np.sqrt(pSY ** 2), lX, tY, eX, eY]
			tPMD = cfg.utls.createTempVirtualRaster(bL, bandNumberList, 'Yes', 'Yes', 0, 'No', 'No', [float(lX), float(tY), float(eX), float(eY), 'Yes'], xyRes)
			rD = None
		else:
			tPMD = cfg.utls.createTempVirtualRaster(bL, bandNumberList, 'Yes', 'Yes', 0, 'No', 'No')
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' multiprocess set: ' + str([tPMD, signatureList, algorithmName, macroclassCheck, classificationOptions, cfg.bandSetsList[bandSetNumber][6]]))
		# process calculation
		o = cfg.utls.multiProcessRaster(rasterPath = tPMD, signatureList = signatureList, functionBand = 'Yes', functionRaster = cfg.utls.classificationMultiprocess, algorithmName = algorithmName, nodataValue = -999, macroclassCheck = macroclassCheck,classificationOptions = classificationOptions, functionBandArgument = cfg.multiAddFactorsVar, functionVariable = cfg.bandSetsList[bandSetNumber][6], progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Classification'), virtualRaster = 'Yes', compress = compress, compressFormat = 'LZW')
		if o == 'No':
			return 'No', None, None, None
		# output rasters
		outputClasses, outputAlgs, outSigDict = o
		tPMDC = cfg.utls.createTempRasterPath('vrt')
		cfg.utls.createVirtualRaster2(inputRasterList = outputClasses, output = tPMDC, NoDataValue = 'Yes')
		# mosaic rasters
		if 	previewSize > 0:
			cOut = tPMDC
		else:
			gcopy = cfg.utls.GDALCopyRaster(tPMDC, outputRasterPath, 'GTiff', compress, 'DEFLATE -co PREDICTOR=2 -co ZLEVEL=1', additionalParams = '-ot  Int16')
			cOut = outputRasterPath
			for oC in outputClasses:
				try:
					cfg.osSCP.remove(oC)
				except:
					pass
		opOut = []
		if algRasterPath is not None:
			tPMDA = cfg.utls.createTempRasterPath('vrt')
			cfg.utls.createVirtualRaster2(inputRasterList = outputAlgs, output = tPMDA, NoDataValue = 'Yes')
			gcopy = cfg.utls.GDALCopyRaster(tPMDA, algRasterPath, 'GTiff', compress, 'LZW')
			for oA in outputAlgs:
				try:
					cfg.osSCP.remove(oA)
				except:
					pass
			rOBaseNm = cfg.osSCP.path.dirname(outputRasterPath)
			for s in range(0, len(signatureList)):
				sLR = str(signatureList[s][0]) + '_' + str(signatureList[s][2])
				try:
					tPMDS = cfg.utls.createTempRasterPath('vrt')
					cfg.utls.createVirtualRaster2(inputRasterList = outSigDict[sLR], output = tPMDS, NoDataValue = 'Yes')
					# base name
					nm = cfg.utls.fileNameNoExt(outputRasterPath)
					opO = rOBaseNm + '/' + nm + '_' + cfg.sigRasterNm + '_' + sLR + '.tif'
					gcopy = cfg.utls.GDALCopyRaster(tPMDS, opO, 'GTiff', compress, 'LZW')
					opOut.append(opO)
				except:
					pass
		else:
			for oA in outputAlgs:
				try:
					cfg.osSCP.remove(oA)
				except:
					pass
			for s in range(0, len(signatureList)):
				sLR = str(signatureList[s][0]) + '_' + str(signatureList[s][2])
				try:
					for oS in outSigDict[sLR]	:
						cfg.osSCP.remove(oS)
				except:
					pass
		# create raster table (removed because of some issues)
		#cfg.utls.createRasterTable(outputRasterPath, 1, signatureList)
		return 'Yes', cOut, algRasterPath, opOut
			
	# set variable for macroclass classification
	def macroclassCheckbox(self):
		if cfg.ui.macroclass_checkBox.isChecked() is True:
			cfg.utls.setQGISRegSetting(cfg.regConsiderMacroclass, 'Yes')
			cfg.ui.class_checkBox.blockSignals(True)
			cfg.ui.class_checkBox.setCheckState(0)
			cfg.ui.class_checkBox.blockSignals(False)
		else:
			cfg.utls.setQGISRegSetting(cfg.regConsiderMacroclass, 'No')
			cfg.ui.class_checkBox.blockSignals(True)
			cfg.ui.class_checkBox.setCheckState(2)
			cfg.ui.class_checkBox.blockSignals(False)
		cfg.macroclassCheck = cfg.sets.getQGISRegSetting(cfg.regConsiderMacroclass, 'No')
		# check signature intersection
		intersect1 = cfg.LCSignT.checkIntersections()
		cfg.LCSignT.higlightRowsByID(intersect1)
		intersect2 = cfg.spSigPlot.checkIntersections()
		cfg.spSigPlot.higlightRowsByID(intersect2)
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.macroclassCheck))
		
	# set variable for class classification
	def classCheckbox(self):
		if cfg.ui.class_checkBox.isChecked() is True:
			cfg.ui.macroclass_checkBox.setCheckState(0)
		else:
			cfg.ui.macroclass_checkBox.setCheckState(2)
				
	# set variable for LC signature
	def LCSignature_Checkbox(self):
		if cfg.ui.LC_signature_checkBox.isChecked() is True:
			cfg.utls.setQGISRegSetting(cfg.regLCSignature, 'Yes')
		else:
			cfg.utls.setQGISRegSetting(cfg.regLCSignature, 'No')
		cfg.LCsignatureCheckBox = cfg.sets.getQGISRegSetting(cfg.regLCSignature, 'No')
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' checkbox set: ' + str(cfg.LCsignatureCheckBox))
		
	# set variable for mask
	def maskCheckbox(self):
		if cfg.ui.mask_checkBox.isChecked() is True:
			m = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a mask shapefile'), '', 'Shapefile (*.shp)')
			if len(m) > 0:
				cfg.mskFlPath = m
				cfg.ui.mask_lineEdit.setText(str(cfg.mskFlPath))
				cfg.mskFlState = 2
			else:
				cfg.mskFlState = 2
				if len(cfg.ui.mask_lineEdit.text()) == 0:
					cfg.ui.mask_checkBox.setCheckState(0)
		else:
			cfg.mskFlState = 0
		cfg.utls.writeProjectVariable('maskFilePath', str(cfg.mskFlPath))	
		cfg.utls.writeProjectVariable('maskFileState', str(cfg.mskFlState))	
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' checkbox set: ' + str(cfg.mskFlState))
		
	# Reset qml style path
	def resetQmlStyle(self):
		p = cfg.qgisCoreSCP.QgsProject.instance()
		p.writeEntry('SemiAutomaticClassificationPlugin', 'qmlfile', '')
		cfg.ui.qml_lineEdit.setText('')
		cfg.qmlFl = ''
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'reset qml')
		
	# Reset mask path
	def resetMask(self):
		cfg.mskFlPath = ''
		cfg.mskFlState = 0
		cfg.utls.writeProjectVariable('maskFilePath', str(cfg.mskFlPath))	
		cfg.utls.writeProjectVariable('maskFileState', str(cfg.mskFlState))	
		cfg.ui.mask_lineEdit.setText(str(cfg.mskFlPath))
		self.setMaskCheckbox()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'reset mask')
		
	def setMaskCheckbox(self):	
		cfg.ui.mask_checkBox.blockSignals(True)
		cfg.ui.mask_checkBox.setCheckState(int(cfg.mskFlState))
		cfg.ui.mask_checkBox.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "mask checkbox")
		
	# Select qml style for classifications and previews
	def selectQmlStyle(self):
		cfg.qmlFl = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a qml style'), '', 'Style (*.qml)')
		# write path to project istance
		p = cfg.qgisCoreSCP.QgsProject.instance()
		p.writeEntry('SemiAutomaticClassificationPlugin', 'qmlfile', cfg.qmlFl)
		cfg.ui.qml_lineEdit.setText(cfg.qmlFl)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'qml file: ' + str(cfg.qmlFl))
