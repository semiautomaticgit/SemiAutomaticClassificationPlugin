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

class SCPDock:

	def __init__(self):
		# rubber band
		cfg.rbbrBnd = cfg.qgisGuiSCP.QgsRubberBand(cfg.cnvs, False)
		cfg.rbbrBnd.setColor(cfg.QtGuiSCP.QColor(0,255,255))
		cfg.rbbrBnd.setWidth(2)
		cfg.mrctrVrtc = []
		self.clearCanvas()
		
	# set preview transparency
	def changePreviewTransparency(self, value):
		try:
			l = cfg.utls.selectLayerbyName(cfg.lastPrev)
			if l is not None:
				cfg.cnvs.setRenderFlag(False)
				l.renderer().setOpacity(float(1) - float(value) / 100)
				if hasattr(l, 'setCacheImage'):
					l.setCacheImage(None)
				l.triggerRepaint()
				cfg.cnvs.setRenderFlag(True)
				cfg.cnvs.refresh()
		except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			
	# show hide preview radio button 2
	def showHidePreview2(self):
		try:
			l = cfg.utls.selectLayerbyName(cfg.lastPrev)
			if l is not None:
				if cfg.show_preview_radioButton2.isChecked():				
					cfg.utls.setLayerVisible(l, True)
					cfg.utls.moveLayerTop(l)
				else:
					cfg.utls.setLayerVisible(l, False)
		except:
			pass
			
	# left click pointer for classification preview
	def pointerClickPreview(self, point):
		# check if other processes are active
		if cfg.actionCheck == 'No':
			cfg.utls.checkPointImage(cfg.bandSetsList[cfg.bndSetNumber][8], point)
			if cfg.pntCheck == 'Yes':
				cfg.pntPrvw = cfg.lstPnt
				self.algRasterPrevw = 'No'
				cfg.classTab.createPreview(cfg.pntPrvw, self.algRasterPrevw )
				
	# right click pointer for preview algorithm raster
	def pointerRightClickPreview(self, point):
		# check if other processes are active
		if cfg.actionCheck == 'No':
			point = cfg.utls.checkPointImage(cfg.bandSetsList[cfg.bndSetNumber][8], point)
			if cfg.pntCheck == 'Yes':
				cfg.pntPrvw = cfg.lstPnt
				self.algRasterPrevw = 'Yes'
				cfg.classTab.createPreview(cfg.pntPrvw, self.algRasterPrevw)
		
	# Activate pointer for classification preview
	def pointerPreviewActive(self):
		# connect to click
		t = cfg.classPrev
		cfg.cnvs.setMapTool(t)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "pointer active: preview")
		
	# set preview size
	def previewSize(self):
		cfg.prvwSz = int(float(cfg.preview_size_spinBox.value()))
		cfg.utls.writeProjectVariable("previewSize", str(cfg.prvwSz))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "preview size: " + str(cfg.prvwSz))
		
	# redo preview
	def redoPreview(self):
		# check if other processes are active
		if cfg.actionCheck == 'No':
			if cfg.pntPrvw is None:
				pass
			else:
				cfg.classTab.createPreview(cfg.pntPrvw, self.algRasterPrevw)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "REDO Preview")
		
	# set all items to state 0 or 2
	def allItemsSetState(self, value, selected = None):
		tW = cfg.uidc.signature_list_treeWidget
		tW.setSortingEnabled(False)
		tW.blockSignals(True)
		if selected is None:
			for id, val in cfg.treeDockItm.items():
				if cfg.actionCheck == 'Yes':
					cfg.treeDockItm[str(id)].setCheckState(0, value)
					cfg.signList['CHECKBOX_' + str(id)] = cfg.treeDockItm[str(id)].checkState(0)
				else:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' cancelled')
					break
		else:
			for i in tW.selectedItems():
				if cfg.actionCheck == 'Yes':
					# classes
					if len(i.text(1)) > 0:
						try:
							i.setCheckState(0, value)
							cfg.signList['CHECKBOX_' + str(i.text(5))] = cfg.treeDockItm[str(i.text(5))].checkState(0)
						except:
							pass
					# macroclasses
					else:
						count = i.childCount()
						for roi in range(0, count):
							try:
								i.child(roi).setCheckState(0, value)
								cfg.signList['CHECKBOX_' + str(i.child(roi).text(5))] = cfg.treeDockItm[str(i.child(roi).text(5))].checkState(0)
							except:
								pass
				else:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' cancelled')
					break
		tW.setSortingEnabled(True)
		tW.blockSignals(False)
				
	# select all signatures
	def selectAllSignatures(self, check = None, selected = None):
		cfg.uiUtls.addProgressBar()
		try:
			# select all
			if check is True:
				cfg.SCPD.allItemsSetState(2, selected)
			# unselect all
			else:
				cfg.SCPD.allItemsSetState(0, selected)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' all signatures')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		cfg.uiUtls.removeProgressBar()
				
	# export signature list to file
	def saveSignatureList(self, signatureFile):
		try:
			root = cfg.ETSCP.Element('signaturelist')
			MCID_LIST = cfg.SCPD.exportMCIDList()
			root.set('MCID_LIST', str(MCID_LIST))
			for k in list(cfg.signIDs.values()):
				sigItem = cfg.ETSCP.SubElement(root, 'signature')
				sigItem.set('ID', str(cfg.signIDs['ID_' + str(k)]))
				mcIDField = cfg.ETSCP.SubElement(sigItem, 'MACROCLASSID')
				mcIDField.text = str(cfg.signList['MACROCLASSID_' + str(k)])
				mcInfoField = cfg.ETSCP.SubElement(sigItem, 'MACROCLASSINFO')
				mcInfoField.text = str(cfg.signList['MACROCLASSINFO_' + str(k)])
				cIDField = cfg.ETSCP.SubElement(sigItem, 'CLASSID')
				cIDField.text = str(cfg.signList['CLASSID_' + str(k)])
				cInfoField = cfg.ETSCP.SubElement(sigItem, 'CLASSINFO')
				cInfoField.text = str(cfg.signList['CLASSINFO_' + str(k)])
				wvLngField = cfg.ETSCP.SubElement(sigItem, 'VALUES')
				wvLngField.text = str(cfg.signList['VALUES_' + str(k)])
				lcsMinField = cfg.ETSCP.SubElement(sigItem, 'LCS_MIN')
				lcsMinField.text = str(cfg.signList['LCS_MIN_' + str(k)])
				lcsMaxField = cfg.ETSCP.SubElement(sigItem, 'LCS_MAX')
				lcsMaxField.text = str(cfg.signList['LCS_MAX_' + str(k)])
				wvLngField = cfg.ETSCP.SubElement(sigItem, 'WAVELENGTH')
				wvLngField.text = str(cfg.signList['WAVELENGTH_' + str(k)])
				meanValField = cfg.ETSCP.SubElement(sigItem, 'MEAN_VALUE')
				meanValField.text = str(cfg.signList['MEAN_VALUE_' + str(k)])
				checkboxField = cfg.ETSCP.SubElement(sigItem, 'CHECKBOX')
				checkboxField.text = str(cfg.signList['CHECKBOX_' + str(k)])
				SDField = cfg.ETSCP.SubElement(sigItem, 'SD')
				SDField.text = str(cfg.signList['SD_' + str(k)])
				unitField = cfg.ETSCP.SubElement(sigItem, 'WAVELENGTH_UNIT')
				unitField.text = str(cfg.signList['UNIT_' + str(k)])
				colorField = cfg.ETSCP.SubElement(sigItem, 'COLOR')
				colorField.text = str(cfg.signList['COLOR_' + str(k)].toRgb().name())
				covMatrField = cfg.ETSCP.SubElement(sigItem, 'COVARIANCE_MATRIX')
				covMatrField.text = str(cfg.utls.covarianceMatrixToList(cfg.signList['COVMATRIX_' + str(k)]))
				roiSizeField = cfg.ETSCP.SubElement(sigItem, 'ROI_SIZE')
				roiSizeField.text = str(cfg.signList['ROI_SIZE_' + str(k)])
				maxValField = cfg.ETSCP.SubElement(sigItem, 'MAX_VALUE')
				maxValField.text = str(cfg.signList['MAX_VALUE_' + str(k)])
				minValField = cfg.ETSCP.SubElement(sigItem, 'MIN_VALUE')
				minValField.text = str(cfg.signList['MIN_VALUE_' + str(k)])
				sigThrField = cfg.ETSCP.SubElement(sigItem, 'SIGNATURE_THRESHOLD_MD')
				sigThrField.text = str(cfg.signList['MD_THRESHOLD_' + str(k)])
				sigThrField = cfg.ETSCP.SubElement(sigItem, 'SIGNATURE_THRESHOLD_ML')
				sigThrField.text = str(cfg.signList['ML_THRESHOLD_' + str(k)])
				sigThrField = cfg.ETSCP.SubElement(sigItem, 'SIGNATURE_THRESHOLD_SAM')
				sigThrField.text = str(cfg.signList['SAM_THRESHOLD_' + str(k)])
			o = open(signatureFile, 'w')
			f = cfg.minidomSCP.parseString(cfg.ETSCP.tostring(root)).toprettyxml()
			o.write(f)
			o.close()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' signatures saved in: ' + str(signatureFile))
		except Exception as err:
			cfg.mx.msgErr15()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		
	def openSignatureList(self, path = None):
		if path is None:
			signFilePath = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a signature list file'), '', 'Signature list file .slf (*.slf)')
		else:
			signFilePath = path
		if len(signFilePath) > 0:
			if cfg.absolutePath == 'false':
				signFile = cfg.utls.qgisAbsolutePathToRelativePath(signFilePath, cfg.projPath)
			else:
				signFile = signFilePath
			self.openSignatureListFile(signFilePath)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' signatures opened: ' + str(signFilePath))
					
	# open training file
	def openTrainingFile(self):
		scpPath = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a SCP training input'), '', 'SCP file (*.scp)')
		if len(scpPath) > 0:
			cfg.signList = {}
			cfg.signIDs = {}
			cfg.SCPD.openInput(scpPath)
			
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
			scpPath = cfg.utls.readProjectVariable('trainingLayer', '')
		check = cfg.SCPD.openShapeFile(scpPath)
		if check == 'Yes':
			cfg.utls.writeProjectVariable('trainingLayer', str(scpPath))
			cfg.scpFlPath = scpPath
			cfg.uidc.trainingFile_lineEdit.setText(str(scpPath))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures opened: " + str(scpPath))
		else:
			# shape layer
			cfg.shpLay = None
			# training layer name
			cfg.trnLay = None
			# signature file path
			cfg.sigFile = None
			cfg.inptDir = None
			cfg.uidc.trainingFile_lineEdit.setText('')

	# open input file
	def openShapeFile(self, shapeFilePath):
		# shapefile
		name = cfg.utls.fileNameNoExt(shapeFilePath)
		dT = cfg.utls.getTime()
		cfg.inptDir = cfg.tmpDir + '/' + name + dT
		oDir = cfg.utls.makeDirectory(cfg.inptDir)
		# unzip to temp dir
		try:
			with cfg.zipfileSCP.ZipFile(shapeFilePath) as zOpen:
				for flName in zOpen.namelist():
					zipF = zOpen.open(flName)
					fileName = cfg.utls.fileName(flName)
					if fileName.endswith('.gpkg') or fileName.endswith('.shp') :
						nm = fileName
					try:
						zipO = open(cfg.inptDir + '/' + fileName, 'wb')
						with zipF, zipO:
							cfg.shutilSCP.copyfileobj(zipF, zipO)
						zipO.close()
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		except Exception as err:
			return 'No'
		# try to remove SCP input
		try:
			cfg.utls.removeLayer(name)
		except:
			pass
		# convert to geopackage
		if nm.endswith('.shp'):
			try:
				nm2 = nm[:-3] + 'gpkg'
				v = cfg.utls.mergeAllLayers([cfg.inptDir + '/' + nm], cfg.inptDir + '/' + nm2)
				nm = nm2
			except:
				pass
		try:
			tSS = cfg.utls.addVectorLayer(cfg.inptDir + '/' + nm)
		except:
			cfg.mx.msgErr59()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error training input')
			return 'No'
		check = cfg.SCPD.checkFields(tSS)
		vCrs = cfg.utls.getCrsGDAL(cfg.inptDir + '/' + nm)
		vEPSG = cfg.osrSCP.SpatialReference()
		vEPSG.ImportFromWkt(vCrs)
		try:
			if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
				b = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][0])
				ql = cfg.utls.layerSource(b)
				rCrs = cfg.utls.getCrsGDAL(ql)
				rEPSG = cfg.osrSCP.SpatialReference()
				rEPSG.ImportFromWkt(rCrs)
			else:
				b = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8])
				ql = cfg.utls.layerSource(b)
				rCrs = cfg.utls.getCrsGDAL(ql)
				rEPSG = cfg.osrSCP.SpatialReference()
				rEPSG.ImportFromWkt(rCrs)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			rEPSG = None
			#return 'No'
		try:
			if vEPSG.IsSame(rEPSG) != 1:
				cfg.mx.msgWar22()
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		if check == 'Yes':
			# create memory layer
			provider = tSS.dataProvider()
			fields = provider.fields()
			pCrs = cfg.utls.getCrs(tSS)
			mL = cfg.qgisCoreSCP.QgsVectorLayer('MultiPolygon?crs=' + str(pCrs.toWkt()), name, 'memory')
			mL.setCrs(pCrs)
			pr = mL.dataProvider()
			for fld in fields:
				pr.addAttributes([fld])
			mL.updateFields()
			f = cfg.qgisCoreSCP.QgsFeature()
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
			sigFileNm = cfg.trnLay + '.slf'
			cfg.sigFile = cfg.inptDir + '/' + sigFileNm
			sigFile = cfg.sigFile
			for root, dirs, files in cfg.osSCP.walk(cfg.inptDir):
				for x in files:
					if x.lower().endswith('.slf'):
						sigFile = root + '/' + x
						break
						break
			if cfg.osSCP.path.isfile(sigFile):
				cfg.SCPD.openSignatureList(sigFile)
			else:
				cfg.SCPD.saveSignatureList(cfg.sigFile)
				cfg.mx.msg20()
				cfg.SCPD.openSignatureList(cfg.sigFile)
		return check
		
	# save memory layer to shapefile
	def saveMemToSHP(self, memoryLayer):
		dT = cfg.utls.getTime()
		try:
			cfg.inptDir = cfg.tmpDir + '/' + cfg.trnLay + dT
		except Exception as err:
			cfg.mx.msgErr59()
			cfg.inptDir = cfg.tmpDir + '/' + dT
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error training input')
			return 'No'
		oDir = cfg.utls.makeDirectory(cfg.inptDir)
		shpF = cfg.inptDir + '/' + cfg.trnLay + '.gpkg'
		l = cfg.utls.saveMemoryLayerToShapefile(memoryLayer, shpF, cfg.trnLay, format = 'GPKG')
		if l == 'No':
			cfg.SCPD.openInput()
			return 'No'
		tSS = cfg.shpLay
		# create memory layer
		provider = tSS.dataProvider()
		fields = provider.fields()
		pCrs = cfg.utls.getCrs(tSS)
		mL = cfg.qgisCoreSCP.QgsVectorLayer('MultiPolygon?crs=' + str(pCrs.toWkt()), cfg.trnLay, 'memory')
		mL.setCrs(pCrs)
		pr = mL.dataProvider()
		for fld in fields:
			pr.addAttributes([fld])
		mL.updateFields()
		f = cfg.qgisCoreSCP.QgsFeature()
		mL.startEditing()
		for f in tSS.getFeatures():
			mL.addFeature(f)	
		mL.commitChanges()
		mL.dataProvider().createSpatialIndex()
		mL.updateExtents()
		cfg.utls.ROISymbol(mL)
		try:
			cfg.utls.removeLayerByLayer(cfg.shpLay)
		except:
			pass
		cfg.shpLay = mL
		cfg.utls.addLayerToMap(cfg.shpLay)
		sigFileNm = cfg.trnLay + '.slf'
		cfg.sigFile = cfg.inptDir + '/' + sigFileNm 
		cfg.SCPD.saveSignatureList(cfg.sigFile)
				
	# check shapefile and fields
	def checkFields(self, trainingLayer):
		try:
			if (trainingLayer.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.MultiPolygon):
				# filter if shapefile has ID_class and ROI_info fields
				f = trainingLayer.dataProvider().fields()
				if f.indexFromName(cfg.fldID_class) > -1 and f.indexFromName(cfg.fldROI_info) > -1 and f.indexFromName(cfg.fldMacroID_class) > -1 and f.indexFromName(cfg.fldROIMC_info) > -1 and f.indexFromName(cfg.fldSCP_UID) > -1:
					return 'Yes'
				else:
					# ask for confirm
					a = cfg.utls.questionBox('Missing fields in shapefile', 'Add missing fields to shapefile?')
					if a == 'Yes':
						cfg.SCPD.addFieldsToLayer(trainingLayer)
						f = trainingLayer.dataProvider().fields()
						if f.indexFromName(cfg.fldID_class) > -1 and f.indexFromName(cfg.fldROI_info) > -1 and f.indexFromName(cfg.fldMacroID_class) > -1 and f.indexFromName(cfg.fldROIMC_info) > -1 and f.indexFromName(cfg.fldSCP_UID) > -1:
							return 'Yes'
						else:
							return 'No'
					else:
						return 'No'
		except Exception as err:
			return 'No'
			
	# Add required fields if missing
	def addFieldsToLayer(self, layer):
		f = []
		fi = layer.dataProvider().fields()
		# add fields
		if fi.indexFromName(cfg.fldID_class) == -1:
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldID_class, cfg.QVariantSCP.Int))
		if fi.indexFromName(cfg.fldROI_info) == -1:
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldROI_info, cfg.QVariantSCP.String))
		if fi.indexFromName(cfg.fldMacroID_class) == -1:
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))
		if fi.indexFromName(cfg.fldROIMC_info) == -1:
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldROIMC_info, cfg.QVariantSCP.String))
		if fi.indexFromName(cfg.fldSCP_UID) == -1:		
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldSCP_UID, cfg.QVariantSCP.String))
		layer.startEditing()
		aF = layer.dataProvider().addAttributes(f)
		# commit changes
		layer.commitChanges()
		layer.dataProvider().createSpatialIndex()
		layer.updateExtents()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' fields added')

	# import SLC signature list
	def importSLCSignatureList(self, signatureFile, addToSignature = 'No'):
		# shapefile
		name = cfg.utls.fileNameNoExt(signatureFile)
		dT = cfg.utls.getTime()
		unzipDir = cfg.tmpDir + '/' + name + dT
		oDir = cfg.utls.makeDirectory(unzipDir)
		# unzip to temp dir
		try:
			with cfg.zipfileSCP.ZipFile(signatureFile) as zOpen:
				for flName in zOpen.namelist():
					if flName.endswith('.gpkg') or flName.endswith('.shp') :
						nm = cfg.utls.fileNameNoExt(flName)
					zipF = zOpen.open(flName)
					fileName = cfg.utls.fileName(flName)
					zipO = open(unzipDir + '/' + fileName, 'wb')
					with zipF, zipO:
						cfg.shutilSCP.copyfileobj(zipF, zipO)
		except:
			return 'No'
		shpF = unzipDir + '/' + nm + '.gpkg'
		if not cfg.osSCP.path.isfile(shpF):
			shpF = unzipDir + '/' + nm + '.shp'
		sigFile = unzipDir + '/' + nm + '.slf'
		sL = cfg.utls.createTempRasterPath('gpkg')
		s = cfg.utls.saveMemoryLayerToShapefile(cfg.shpLay, sL, format = 'GPKG')
		tVect = cfg.utls.createTempRasterPath('gpkg')
		inputLayersList = [sL, shpF]
		v = cfg.utls.mergeAllLayers(inputLayersList, tVect)
		l = cfg.shpLay
		try:
			tSS = cfg.utls.addVectorLayer(tVect)
		except:
			cfg.mx.msgErr59()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error training input')
			return 'No'
		# try to remove SCP input
		try:
			cfg.utls.removeLayer(cfg.trnLay)
		except:
			pass
		provider = tSS.dataProvider()
		fields = provider.fields()
		pCrs = cfg.utls.getCrs(tSS)
		mL = cfg.qgisCoreSCP.QgsVectorLayer('MultiPolygon?crs=' + str(pCrs.toWkt()), cfg.trnLay , 'memory')
		mL.setCrs(pCrs)
		pr = mL.dataProvider()
		for fld in fields:
			pr.addAttributes([fld])
		mL.updateFields()
		fldSCP_UID = cfg.utls.fieldID(tSS, cfg.fldSCP_UID)
		f = cfg.qgisCoreSCP.QgsFeature()
		mL.startEditing()
		UIDList = []
		for f in tSS.getFeatures():
			UID = f.attributes()[fldSCP_UID]
			if UID not in UIDList:
				mL.addFeature(f)
				UIDList.append(UID)
		mL.commitChanges()
		mL.dataProvider().createSpatialIndex()
		mL.updateExtents()
		cfg.utls.ROISymbol(mL)
		cfg.shpLay = mL
		cfg.utls.addLayerToMap(cfg.shpLay)
		cfg.SCPD.openSignatureListFile(sigFile, addToSignature)
		cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
		
	# open signature file
	def openSignatureListFile(self, signatureFile, addToSignature = 'No'):
		try:
			tree = cfg.ETSCP.parse(signatureFile)
			root = tree.getroot()
			if addToSignature == 'No':
				cfg.signList = {}
				cfg.signIDs = {}
			try:
				MCID_LIST = root.get('MCID_LIST')
				MC_List = eval(MCID_LIST)
				newList = []
				idList = []
				for k in cfg.MCID_List:
					idList.append(k[0])
					newList.append(k)
				for k in MC_List:
					if k[0] not in idList:
						idList.append(k[0])
						newList.append(k)
				cfg.MCID_List = newList
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			for child in root:
				try:
					b = child.get('ID')
					if len(b) == 0:
						b = cfg.utls.signatureID()
				except:
					b = cfg.utls.signatureID()
				cfg.signList['MACROCLASSID_' + str(b)] = str(child.find('MACROCLASSID').text).strip()
				cfg.signList['MACROCLASSINFO_' + str(b)] = str(child.find('MACROCLASSINFO').text).strip()
				cfg.signList['CLASSID_' + str(b)] = str(child.find('CLASSID').text).strip()
				cfg.signList['CLASSINFO_' + str(b)] = str(child.find('CLASSINFO').text).strip()
				cfg.signList['UNIT_' + str(b)] = str(child.find('WAVELENGTH_UNIT').text).strip()
				cfg.signList['ROI_SIZE_' + str(b)] = str(child.find('ROI_SIZE').text).strip()
				cfg.signIDs['ID_' + str(b)] = b
				# get values
				vls = str(child.find('VALUES').text).strip().replace('nan', '0')
				x = eval(vls)
				cfg.signList['VALUES_' + str(b)] = x	
				try:
					lcsMin = str(child.find('LCS_MIN').text).strip()
					min = eval(lcsMin)
					cfg.signList['LCS_MIN_' + str(b)] = min			
					lcsMax = str(child.find('LCS_MAX').text).strip()
					max = eval(lcsMax)
					cfg.signList['LCS_MAX_' + str(b)] = max
				except:
					cfg.signList['LCS_MIN_' + str(b)] = x
					cfg.signList['LCS_MAX_' + str(b)] = x
				try:
					minV = str(child.find('MIN_VALUE').text).strip()
					minVal = eval(minV)
					cfg.signList['MIN_VALUE_' + str(b)] = minVal
					maxV = str(child.find('MAX_VALUE').text).strip()	
					maxVal = eval(maxV)
					cfg.signList['MAX_VALUE_' + str(b)] = maxVal
				except:
					cfg.signList['MIN_VALUE_' + str(b)] = x
					cfg.signList['MAX_VALUE_' + str(b)] = x			
				cfg.signList['WAVELENGTH_' + str(b)] = eval(str(child.find('WAVELENGTH').text).strip())
				cfg.signList['SD_' + str(b)] = eval(str(child.find('SD').text).strip().replace('nan', '0'))
				cfg.signList['MEAN_VALUE_' + str(b)] = eval(str(child.find('MEAN_VALUE').text).strip().replace('nan', '0'))
				try:
					cfg.signList['CHECKBOX_' + str(b)] = eval(str(child.find('CHECKBOX').text).strip())
				except:
					cfg.signList['CHECKBOX_' + str(b)] = 2
				c = cfg.QtGuiSCP.QColor()
				c.setNamedColor(str(child.find('COLOR').text).strip())
				cfg.signList['COLOR_' + str(b)] = c
				# get covariance matrix
				mt = str(child.find('COVARIANCE_MATRIX').text).strip()
				try:
					cm = eval(mt)
				except:
					cm = 'No'
				cfg.signList['COVMATRIX_' + str(b)] = cfg.utls.listToCovarianceMatrix(cm)
				try:
					cfg.signList['MD_THRESHOLD_' + str(b)] = float((child.find('SIGNATURE_THRESHOLD_MD').text).strip())
				except:
					cfg.signList['MD_THRESHOLD_' + str(b)] = 0
				try:
					cfg.signList['ML_THRESHOLD_' + str(b)] = float((child.find('SIGNATURE_THRESHOLD_ML').text).strip())
				except:
					cfg.signList['ML_THRESHOLD_' + str(b)] = 0
				try:
					cfg.signList['SAM_THRESHOLD_' + str(b)] = float((child.find('SIGNATURE_THRESHOLD_SAM').text).strip())
				except:
					cfg.signList['SAM_THRESHOLD_' + str(b)] = 0
			cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
			# logger
			if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' opened signature ' + str(len(cfg.signIDs)))
		except Exception as err:
			cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
			cfg.mx.msgErr16()
			# logger
			if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			
	# export signature to file
	def exportSignatureFile(self):
		sL = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Export SCP training input'), '', '*.scp', 'scp')
		if sL is not False:
			# create vector
			crs = cfg.shpLay.crs()
			f = cfg.qgisCoreSCP.QgsFields()
			# add Class ID, macroclass ID and Info fields
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldROIMC_info, cfg.QVariantSCP.String))
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldID_class, cfg.QVariantSCP.Int))
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldROI_info, cfg.QVariantSCP.String))
			f.append(cfg.qgisCoreSCP.QgsField(cfg.fldSCP_UID, cfg.QVariantSCP.String))
			# vector
			name = cfg.utls.fileNameNoExt(sL)
			dT = cfg.utls.getTime()
			unzipDir = cfg.tmpDir + '/' + name + dT
			shpF = unzipDir + '/' + name + '.gpkg'
			sigFile = unzipDir + '/' + name + '.slf'
			oDir = cfg.utls.makeDirectory(unzipDir)
			cfg.qgisCoreSCP.QgsVectorFileWriter(str(shpF), 'CP1250', f, cfg.qgisCoreSCP.QgsWkbTypes.MultiPolygon , crs, 'GPKG')
			tSS = cfg.utls.addVectorLayer(shpF, name + dT, 'ogr')
			signIDorig = cfg.signIDs.copy()
			cfg.signIDs = {}
			tW = cfg.uidc.signature_list_treeWidget
			v = []
			for i in tW.selectedItems():
				# classes
				if len(i.text(1)) > 0:
					try:
						id = i.text(5)
						cfg.ROI_C_ID[id]
						cfg.signIDs['ID_' + str(id)] = id
						v.append(id)
					except:
						pass
				# macroclasses
				else:
					count = i.childCount()
					for roi in range(0, count):
						try:
							id = i.child(roi).text(5)
							cfg.ROI_C_ID[id]
							cfg.signIDs['ID_' + str(id)] = id
							v.append(id)
						except:
							pass
			if len(v) == 0:
				for id, val in cfg.treeDockItm.items():
					cfg.signIDs['ID_' + str(id)] = id
					v.append(id)
			self.saveSignatureList(sigFile)
			cfg.signIDs = signIDorig.copy()
			f = cfg.qgisCoreSCP.QgsFeature()
			tSS.startEditing()
			for f in cfg.shpLay.getFeatures():
				SCP_UID  = str(f[cfg.fldSCP_UID])
				if SCP_UID in v:
					tSS.addFeature(f)
			tSS.commitChanges()
			tSS.dataProvider().createSpatialIndex()
			tSS.updateExtents()
			# create zip file
			cfg.utls.zipDirectoryInFile(sL, unzipDir)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' signatures exported in: ' + str(sL))
			cfg.mx.msg27()
			
	# export signature to shapefile
	def exportSignatureShapefile(self):
		sL = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Export SCP training input'), '', 'SHP file (*.shp);;GPKG file (*.gpkg)', None)
		if sL is not False:
			crs = cfg.utls.getCrs(cfg.shpLay)
			if str(sL).endswith('.shp'):	
				format = 'ESRI Shapefile'
			elif str(sL).endswith('.gpkg'):
				format = 'GPKG'
			else:
				sL = sL + '.gpkg'
				format = 'GPKG'
			# filter IDs
			tW = cfg.uidc.signature_list_treeWidget
			v = cfg.SCPD.getHighlightedIDs('Yes')
			s = cfg.utls.saveMemoryLayerToShapefile(cfg.shpLay, sL, format = format, IDList = v, listFieldName = cfg.fldSCP_UID)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' signatures exported in: ' + str(sL))
			cfg.mx.msg27()
			
	# get highlighted IDs
	def getHighlightedIDs(self, selectAll = None, signatures = None):
		# filter IDs
		tW = cfg.uidc.signature_list_treeWidget
		v = []
		for i in tW.selectedItems():
			# classes
			if len(i.text(1)) > 0:
				try:
					cfg.ROI_C_ID[i.text(5)]
					v.append(i.text(5))
				except:
					if signatures == 'Yes':
						try:
							cfg.signIDs['ID_' + i.text(5)]
							v.append(i.text(5))
						except:
							pass
			# macroclasses
			else:
				count = i.childCount()
				for roi in range(0, count):
					try:
						cfg.ROI_C_ID[i.child(roi).text(5)]
						v.append(i.child(roi).text(5))
					except:
						if signatures == 'Yes':
							try:
								cfg.signIDs['ID_' + i.child(roi).text(5)]
								v.append(i.child(roi).text(5))
							except:
								pass
		if len(v) == 0 and selectAll == 'Yes':
			for id, val in cfg.treeDockItm.items():
				v.append(id)
		return v
							
	# save signature to file
	def saveSignatureListToFile(self):
		try:
			cfg.SCPD.saveSignatureList(cfg.sigFile)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' signatures saved in: ' + str(cfg.sigFile))
		except Exception as err:
			cfg.mx.msgErr15()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
								
	# open signature file
	def openLibraryFile(self, libraryFile):
		try:
			if cfg.bandSetsList[cfg.bndSetNumber][5] == cfg.noUnit:
				cfg.mx.msgWar8()
			libFileList = cfg.utls.getOpenFileNames(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a library file'), '', 'SCP file (*.scp);;USGS library (*.zip);;ASTER library (*.txt);;CSV (*.csv)')
			if len(libFileList) > 0:
				for libFile in libFileList:
					cfg.uiUtls.addProgressBar()
					if libFile.lower().endswith('.zip'):
						libraryR, libraryW, libraryS = cfg.usgsLib.unzipLibrary(libFile)
						cfg.sigImport.USGSLibrary(libraryR, libraryW, libraryS)
					elif libFile.lower().endswith('.txt'):
						cfg.sigImport.ASTERLibrary(libFile)
					elif libFile.lower().endswith('.csv'):
						cfg.sigImport.CSVLibrary(libFile)
					elif libFile.lower().endswith('.scp'):
						self.importSLCSignatureList(libFile, 'Yes')
					cfg.uiUtls.removeProgressBar()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' spectral library ' + str(libFile))
				cfg.mx.msg28()
		except Exception as err:
			cfg.uiUtls.removeProgressBar()
			cfg.mx.msgWar8()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		
	# export signatures to CSV library
	def exportToCSVLibrary(self):
		tW = cfg.uidc.signature_list_treeWidget
		v = cfg.SCPD.getHighlightedIDs('Yes', 'Yes')
		if len(v) > 0:
			d = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Export the highlighted signatures to CSV library'))
			if len(d) > 0:
				for id in v:
					mID = cfg.signList['MACROCLASSID_' + str(id)]
					mC = cfg.signList['MACROCLASSINFO_' + str(id)]
					cID = cfg.signList['CLASSID_' + str(id)]
					c = cfg.signList['CLASSINFO_' + str(id)]
					signFile = d + '/' + str(mID) + '_' + str(mC) + '_' + str(cID) + '_' + str(c) + str('.csv')
					# open file
					l = open(signFile, 'w')
					try:
						l.write('wavelength;reflectance;standardDeviation;waveLengthUnit \n')
						l.close()
					except Exception as err:
						cfg.mx.msgErr18()
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					u = str(cfg.signList['UNIT_' + str(id)])
					# wavelength
					a = str(cfg.signList['WAVELENGTH_' + str(id)])
					wlg = eval(a)
					# signature values
					n = str(cfg.signList['VALUES_' + str(id)])
					val = eval(n)
					# open file
					l = open(signFile, 'a')
					for k in range(0, len(wlg)):
						wl = wlg[k]
						vl = val[k*2]
						sD = val[k*2 + 1]
						line = str(wl) + ';' + str(vl) + ';' + str(sD) + ';' + str(u) + '\n'
						try:
							l.write(line)
						except Exception as err:
							cfg.mx.msgErr18()
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					l.close()
				cfg.mx.msg27()

	# zoom to preview
	def zoomToPreview(self):
		preP = cfg.utls.selectLayerbyName(cfg.lastPrev)
		if preP is not None:
			cfg.utls.setMapExtentFromLayer(preP)
			preP.triggerRepaint()
			cfg.cnvs.refresh()
					
##################################
	''' Table functions '''
##################################
	
	# calculate signatures
	def calculateSignatures(self):
		tW = cfg.uidc.signature_list_treeWidget
		v = cfg.SCPD.getHighlightedIDs('No')
		if len(v) == 0:
			return 0
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Calculate signatures'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Calculate signatures for highlighted items?'))
		if a == 'Yes':
			cfg.uiUtls.addProgressBar()
			progresStep = 100 / len(v)
			progress = 0
			for id in v:
				progress = progress * progresStep
				# if ROI
				if str(id) in list(cfg.ROI_SCP_UID.values()):
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
					cfg.utls.calculateSignature(cfg.shpLay, cfg.bandSetsList[cfg.bndSetNumber][8], rId, cfg.ROI_MC_ID[id], cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.ROI_C_Info[id], progress, progresStep, 'No', 'No', id)
				if id in list(cfg.signPlotIDs.values()):
					cfg.SCPD.sigListToPlot(id)
					cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
			if cfg.saveInputCheck == '2':
				cfg.SCPD.saveMemToSHP(cfg.shpLay)
				cfg.utls.zipDirectoryInFile(cfg.scpFlPath, cfg.inptDir)
			cfg.uiUtls.removeProgressBar()
			
	# merge highlighted signatures
	def mergeSelectedSignatures(self):
		tW = cfg.uidc.signature_list_treeWidget
		v = cfg.SCPD.getHighlightedIDs('No')
		if len(set(v)) > 1:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Merge signatures'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Merge highlighted signatures?'))
			if a == 'Yes':
				cfg.uiUtls.addProgressBar()
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
				for id in v:
					# if ROI
					if str(id) in list(cfg.ROI_SCP_UID.values()):
						ifd = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
						ids.append(ifd[0])
						ROIcheck.append(1)
					else:
						ROIcheck.append(0)
					# if not signatue
					if str(id) not in list(cfg.signIDs.values()):
						rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
						cfg.utls.calculateSignature(cfg.shpLay, cfg.bandSetsList[cfg.bndSetNumber][8], rId, cfg.ROI_MC_ID[id], cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.ROI_C_Info[id], None, None, 'No', 'No', id)
					if len(wl) == 0:
						wl = cfg.signList['WAVELENGTH_' + str(id)]
						unit = cfg.signList['UNIT_' + str(id)]
						MC_ID  = cfg.signList['MACROCLASSID_' + str(id)]
						MC_Info  = cfg.merged_name + cfg.signList['MACROCLASSINFO_' + str(id)]
						C_ID = cfg.signList['CLASSID_' + str(id)]
						C_Info = cfg.merged_name + cfg.signList['CLASSINFO_' + str(id)]
						color = cfg.signList['COLOR_' + str(id)]
						checkbox  = cfg.signList['CHECKBOX_' + str(id)]
						sigThr  = cfg.signList['MD_THRESHOLD_' + str(id)]
						sigThrML  = cfg.signList['ML_THRESHOLD_' + str(id)]
						sigThrSAM  = cfg.signList['SAM_THRESHOLD_' + str(id)]
					elif wl != cfg.signList['WAVELENGTH_' + str(id)] or unit != cfg.signList['UNIT_' + str(id)]:
						cfg.mx.msgErr35()
						return 'No'
					val.append(cfg.signList['VALUES_' + str(id)])
					min.append(cfg.signList['LCS_MIN_' + str(id)])
					max.append(cfg.signList['LCS_MAX_' + str(id)])
					vmin.append(cfg.signList['MIN_VALUE_' + str(id)])
					vmax.append(cfg.signList['MAX_VALUE_' + str(id)])
					covMat.append(cfg.signList['COVMATRIX_' + str(id)])
				i = cfg.utls.signatureID()
				# if ROIs
				if 0 not in ROIcheck:
					attributeList = [cfg.ROI_MC_ID[id], cfg.merged_name + cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.merged_name + cfg.ROI_C_Info[id], i]
					tl = cfg.utls.mergePolygons(cfg.shpLay, ids, attributeList)
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(i))
					cfg.utls.calculateSignature(cfg.shpLay, cfg.bandSetsList[cfg.bndSetNumber][8], rId, cfg.ROI_MC_ID[id], cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.ROI_C_Info[id], None, None, 'No', 'No', i)
				else:
					covMatrixSum = 0
					try:
						for cvm in covMat:
							covMatrixSum = covMatrixSum + cvm
						covMatrix = covMatrixSum / len(covMat)
						cfg.np.linalg.inv(covMatrix)
					except:
						covMatrix = 'No'
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
					cfg.signList['CHECKBOX_' + str(i)] = cfg.QtSCP.Checked
					cfg.signList['MACROCLASSID_' + str(i)] = MC_ID
					cfg.signList['MACROCLASSINFO_' + str(i)] = MC_Info
					cfg.signList['CLASSID_' + str(i)] = C_ID
					cfg.signList['CLASSINFO_' + str(i)] = C_Info
					cfg.signList['WAVELENGTH_' + str(i)] = wl
					cfg.signList['VALUES_' + str(i)] = val_mean
					cfg.signList['LCS_MIN_' + str(i)] = min_mean
					cfg.signList['LCS_MAX_' + str(i)] = max_mean
					cfg.signList['MIN_VALUE_' + str(i)] = vmin_mean
					cfg.signList['MAX_VALUE_' + str(i)] = vmaxs_mean			
					cfg.signList['ROI_SIZE_' + str(i)] = 0
					cfg.signList['COVMATRIX_' + str(i)] = covMatrix
					cfg.signList['MD_THRESHOLD_' + str(i)] = sigThr
					cfg.signList['ML_THRESHOLD_' + str(i)] = sigThrML
					cfg.signList['SAM_THRESHOLD_' + str(i)] = sigThrSAM
					# counter
					n = 0
					m = []
					sdL = []
					for wi in wl:
						m.append(val_mean[n * 2])
						sdL.append(val_mean[n * 2 +1])
						n = n + 1
					cfg.signList['MEAN_VALUE_' + str(i)] = m
					cfg.signList['SD_' + str(i)] = sdL
					if unit is None:
						unit = cfg.bandSetsList[cfg.bndSetNumber][5]
					cfg.signList['UNIT_' + str(i)] = unit
					cfg.signList['COLOR_' + str(i)] = color
					cfg.signIDs['ID_' + str(i)] = i
				cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
				if cfg.saveInputCheck == '2':
					cfg.SCPD.saveMemToSHP(cfg.shpLay)
					cfg.utls.zipDirectoryInFile(cfg.scpFlPath, cfg.inptDir)
				cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' merged signatures: ' + str(v))

	# remove selected signatures
	def removeSelectedSignatures(self):
		tW = cfg.uidc.signature_list_treeWidget
		selected = tW.selectedItems()
		if len(selected) > 0:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Delete signatures'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Are you sure you want to delete highlighted ROIs and signatures?'))
			if a == 'Yes':
				ids = []
				for i in tW.selectedItems():
					# classes
					if i.text(5) in list(cfg.signIDs.values()):
						cfg.SCPD.deleteSignatureByID(i.text(5))
					if i.text(5) in list(cfg.ROI_SCP_UID.values()):
						rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(i.text(5)))
						for rI in rId:
							ids.append(rI)
					# macroclasses
					if i.text(5) in cfg.treeDockMCItm:
						c = cfg.treeDockMCItm[i.text(5)]
						for x in range(0, c.childCount()):
							if c.child(x).text(5) in list(cfg.signIDs.values()):
								cfg.SCPD.deleteSignatureByID(c.child(x).text(5))
							if c.child(x).text(5) in list(cfg.ROI_SCP_UID.values()):
								rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(c.child(x).text(5)))
								for rI in rId:
									ids.append(rI)
				if cfg.shpLay is not None:
					cfg.utls.deleteFeatureShapefile(cfg.shpLay, ids)
				cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
				if cfg.saveInputCheck == '2':
					cfg.SCPD.saveMemToSHP(cfg.shpLay)
					cfg.utls.zipDirectoryInFile(cfg.scpFlPath, cfg.inptDir)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' removed signatures: ' + str(ids))
		
	# delete signature by ID
	def deleteSignatureByID(self, id):
		cfg.signIDs.pop('ID_' + str(id))
		cfg.signList.pop('MACROCLASSID_' + str(id))
		cfg.signList.pop('MACROCLASSINFO_' + str(id))
		cfg.signList.pop('CLASSID_' + str(id))
		cfg.signList.pop('CLASSINFO_' + str(id))
		cfg.signList.pop('WAVELENGTH_' + str(id))
		try:
			cfg.signList.pop('MEAN_VALUE_' + str(id))
			cfg.signList.pop('SD_' + str(id))
		except:
			pass
		cfg.signList.pop('VALUES_' + str(id))
		cfg.signList.pop('LCS_MIN_' + str(id))
		cfg.signList.pop('LCS_MAX_' + str(id))
		cfg.signList.pop('MIN_VALUE_' + str(id))
		cfg.signList.pop('MAX_VALUE_' + str(id))
		cfg.signList.pop('ROI_SIZE_' + str(id))
		cfg.signList.pop('COLOR_' + str(id))
		cfg.signList.pop('UNIT_' + str(id))
		cfg.signList.pop('COVMATRIX_' + str(id))
		cfg.signList.pop('MD_THRESHOLD_' + str(id))
		cfg.signList.pop('ML_THRESHOLD_' + str(id))
		cfg.signList.pop('SAM_THRESHOLD_' + str(id))
		try:
			cfg.signList.pop('CHECKBOX' + str(id))
		except:
			pass
		try:
			cfg.signList.pop('LCS_ROW' + str(id))
		except:
			pass
		try:
			cfg.scaPlT.removeScatterByID(id)
			cfg.scaPlT.scatterPlotListTable(cfg.uiscp.scatter_list_plot_tableWidget)
		except:
			pass
		
	# add signatures to spectral plot
	def addSignatureToSpectralPlot(self, tabIndex = 0):
		tW = cfg.uidc.signature_list_treeWidget
		v = cfg.SCPD.getHighlightedIDs('No', 'Yes')
		check = 'Yes'
		if len(v) > 0:
			progresStep = 100 / len(v)
			progress = 0
			cfg.uiUtls.addProgressBar()
			for id in v:
				progress = progress * progresStep
				if id in list(cfg.signIDs.values()):
					if id not in list(cfg.signPlotIDs.values()):
						cfg.SCPD.sigListToPlot(id)
				else:
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
					cfg.utls.calculateSignature(cfg.shpLay, cfg.bandSetsList[cfg.bndSetNumber][8], rId, cfg.ROI_MC_ID[id], cfg.ROI_MC_Info[id], cfg.ROI_C_ID[id], cfg.ROI_C_Info[id], progress, progresStep, 'No', 'No', id)
					cfg.SCPD.sigListToPlot(id)
					check = 'No'
			cfg.uiUtls.removeProgressBar()
			if check == 'No':
				cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
			cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			cfg.utls.spectralPlotTab()
			cfg.utls.selectSpectralPlotTabSettings(tabIndex)
		else:
			cfg.utls.spectralPlotTab()
			cfg.utls.selectSpectralPlotTabSettings(tabIndex)
			
	# add ROI to scatter plot
	def addROIToScatterPlot(self):
		tW = cfg.uidc.signature_list_treeWidget
		v = cfg.SCPD.getHighlightedIDs('No')
		if len(v) > 0:
			progresStep = 100 / len(v)
			progress = 0
			cfg.uiUtls.addProgressBar()
			for id in v:
				progress = progress * progresStep
				if str(id) in list(cfg.ROI_SCP_UID.values()):
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
		try:
			cfg.signPlotIDs['ID_' + str(id)] = id
			cfg.spectrPlotList['MACROCLASSID_' + str(id)] = cfg.signList['MACROCLASSID_' + str(id)]
			cfg.spectrPlotList['MACROCLASSINFO_' + str(id)] = cfg.signList['MACROCLASSINFO_' + str(id)]
			cfg.spectrPlotList['CLASSID_' + str(id)] = cfg.signList['CLASSID_' + str(id)]
			cfg.spectrPlotList['CLASSINFO_' + str(id)] = cfg.signList['CLASSINFO_' + str(id)]
			cfg.spectrPlotList['VALUES_' + str(id)] = cfg.signList['VALUES_' + str(id)]
			cfg.spectrPlotList['ROI_SIZE_' + str(id)] = cfg.signList['ROI_SIZE_' + str(id)]
			cfg.spectrPlotList['MIN_VALUE_' + str(id)] = cfg.signList['MIN_VALUE_' + str(id)]
			cfg.spectrPlotList['MAX_VALUE_' + str(id)] = cfg.signList['MAX_VALUE_' + str(id)]
			cfg.spectrPlotList['LCS_MIN_' + str(id)] = cfg.signList['LCS_MIN_' + str(id)]
			cfg.spectrPlotList['LCS_MAX_' + str(id)] = cfg.signList['LCS_MAX_' + str(id)]
			cfg.spectrPlotList['WAVELENGTH_' + str(id)] = cfg.signList['WAVELENGTH_' + str(id)]
			cfg.spectrPlotList['MEAN_VALUE_' + str(id)] = cfg.signList['MEAN_VALUE_' + str(id)]
			cfg.spectrPlotList['SD_' + str(id)] = cfg.signList['SD_' + str(id)]
			cfg.spectrPlotList['COLOR_' + str(id)] = cfg.signList['COLOR_' + str(id)]
			cfg.spectrPlotList['CHECKBOX_' + str(id)] = 2
			cfg.spectrPlotList['UNIT_' + str(id)] = cfg.signList['UNIT_' + str(id)] 
			cfg.spectrPlotList['COVMATRIX_' + str(id)] = cfg.signList['COVMATRIX_' + str(id)]
			cfg.spectrPlotList['MD_THRESHOLD_' + str(id)] = cfg.signList['MD_THRESHOLD_' + str(id)]
			cfg.spectrPlotList['ML_THRESHOLD_' + str(id)] = cfg.signList['ML_THRESHOLD_' + str(id)]
			cfg.spectrPlotList['SAM_THRESHOLD_' + str(id)] = cfg.signList['SAM_THRESHOLD_' + str(id)]
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msg3()
			
	# get all ROI attributes
	def getROIAttributes(self, layer):
		l = layer
		cfg.ROI_MC_ID = {}
		cfg.ROI_MC_Info = {}
		cfg.ROI_C_ID = {}
		cfg.ROI_C_Info = {}
		cfg.ROI_Count = {}
		cfg.ROI_ShapeID = {}
		cfg.ROI_SCP_UID = {}
		cfg.treeDockItm = {}
		cfg.treeDockMCItm = {}
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
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msg3()
				i = i + 1
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ROI attributes')
			
	# add item to tree
	def addTreeItem(self, tree, textList, color = None, checkboxState = None, tooltip = None, foreground = None, bold = None):
		mc = textList[0]
		mcInfo = textList[1]
		row = tree.topLevelItemCount()
		cfg.treeDockMCItm[str(mc)] = cfg.QTreeWidgetItemSCP(row)
		tree.addTopLevelItem(cfg.treeDockMCItm[str(mc)])
		cfg.treeDockMCItm[str(mc)].setFlags(cfg.QtSCP.ItemIsEditable | cfg.QtSCP.ItemIsEnabled | cfg.QtSCP.ItemIsSelectable | cfg.QtSCP.ItemIsDropEnabled)
		cfg.treeDockMCItm[str(mc)].setExpanded(True)
		cfg.treeDockMCItm[str(mc)].setData(0, 0, int(mc))
		cfg.treeDockMCItm[str(mc)].setData(2, 0, str(mcInfo))
		cfg.treeDockMCItm[str(mc)].setData(5, 0, int(mc))
		font = cfg.QtGuiSCP.QFont()
		font.setBold(True)
		cfg.treeDockMCItm[str(mc)].setFont(0, font)
		cfg.treeDockMCItm[str(mc)].setFont(2, font)
		if checkboxState is not None:
			cfg.treeDockMCItm[str(mc)].setCheckState(column, checkboxState)
		if color is not None:
			cfg.treeDockMCItm[str(mc)].setBackground(4, color)
			
# add item to tree
	def addChildTreeItem(self, tree, textList, color = None, checkboxState = None):
		mc = textList[0]
		mcInfo = textList[1]
		cId = textList[2]
		cInfo = textList[3]
		type = textList[4]
		k = textList[5]
		cfg.treeDockItm[str(k)] = cfg.QTreeWidgetItemSCP()
		try:
			cfg.treeDockMCItm[str(mc)].addChild(cfg.treeDockItm[str(k)])
		except:
			cfg.SCPD.addTreeItem(tree, [mc, mcInfo], color = color)
			cfg.treeDockMCItm[str(mc)].addChild(cfg.treeDockItm[str(k)])
		cfg.treeDockItm[str(k)].setFlags(cfg.QtSCP.ItemIsEditable | cfg.QtSCP.ItemIsEnabled | cfg.QtSCP.ItemIsUserCheckable | cfg.QtSCP.ItemIsSelectable | cfg.QtSCP.ItemIsDragEnabled)
		if checkboxState is not None:
			cfg.treeDockItm[str(k)].setCheckState(0, checkboxState)
		cfg.treeDockItm[str(k)].setData(0, 0, int(mc))
		cfg.treeDockItm[str(k)].setData(1, 0, int(cId))
		cfg.treeDockItm[str(k)].setData(2, 0, str(cInfo))
		cfg.treeDockItm[str(k)].setData(3, 0, str(type))
		cfg.treeDockItm[str(k)].setData(5, 0, str(k))
		if color is not None:
			cfg.treeDockItm[str(k)].setBackground(4, color)
			
	# clear tree
	def clearTree(self, tree = None):
		if tree is None:	
			order = 0
			sorter = cfg.QtSCP.AscendingOrder
		else:
			order = tree.header().sortIndicatorOrder()
			sorter = tree.header().sortIndicatorSection()
			tree.deleteLater()
		cfg.uidc.signature_list_treeWidget = cfg.QtWidgetsSCP.QTreeWidget(cfg.uidc.tab_2)
		cfg.uidc.signature_list_treeWidget.setEditTriggers(cfg.QtWidgetsSCP.QAbstractItemView.AnyKeyPressed|cfg.QtWidgetsSCP.QAbstractItemView.SelectedClicked)
		cfg.uidc.signature_list_treeWidget.setAlternatingRowColors(True)
		cfg.uidc.signature_list_treeWidget.setSelectionMode(cfg.QtWidgetsSCP.QAbstractItemView.MultiSelection)
		cfg.uidc.signature_list_treeWidget.setIndentation(5)
		cfg.uidc.signature_list_treeWidget.setExpandsOnDoubleClick(False)
		cfg.uidc.signature_list_treeWidget.setObjectName('signature_list_treeWidget')
		cfg.uidc.gridLayout.addWidget(cfg.uidc.signature_list_treeWidget, 1, 1, 1, 1)
		cfg.uidc.signature_list_treeWidget.setSortingEnabled(True)
		cfg.uidc.signature_list_treeWidget.headerItem().setText(0, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'MC ID'))
		cfg.uidc.signature_list_treeWidget.headerItem().setText(1, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'C ID'))
		cfg.uidc.signature_list_treeWidget.headerItem().setText(2, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Name'))
		cfg.uidc.signature_list_treeWidget.headerItem().setText(3, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Type'))
		cfg.uidc.signature_list_treeWidget.headerItem().setText(4, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Color'))
		cfg.uidc.signature_list_treeWidget.headerItem().setText(5, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'SCPID'))
		# tree list
		cfg.uidc.signature_list_treeWidget.header().hideSection(5)
		cfg.uidc.signature_list_treeWidget.header().setSortIndicator(sorter, order)
		cfg.utls.setTreeColumnWidthList(cfg.uidc.signature_list_treeWidget, [[0, 60], [1, 30], [2, 100], [3, 40], [4, 30]])
		# connect to edited cell
		cfg.uidc.signature_list_treeWidget.itemChanged.connect(cfg.SCPD.editedCellTree)
		# connect to signature list double click
		cfg.uidc.signature_list_treeWidget.itemDoubleClicked.connect(cfg.SCPD.signatureListDoubleClickTree)
		#  context menu
		cfg.uidc.signature_list_treeWidget.setContextMenuPolicy(cfg.QtCoreSCP.Qt.CustomContextMenu)
		cfg.uidc.signature_list_treeWidget.customContextMenuRequested.connect(cfg.SCPD.contextMenu)
		return cfg.uidc.signature_list_treeWidget
		
	# add item to menu
	def addMenuItem(self, menu, function, iconName, name, tooltip = ''):
		try:
			action = cfg.QtWidgetsSCP.QAction(cfg.QtGuiSCP.QIcon(':/plugins/semiautomaticclassificationplugin/icons/' + iconName), name, cfg.iface.mainWindow())
		except:
			action = cfg.QtWidgetsSCP.QAction(name, cfg.iface.mainWindow())
		action.setObjectName('action')
		action.setToolTip(tooltip)
		action.triggered.connect(function)
		menu.addAction(action)
		return action
		
	# menu
	def contextMenu(self, event):
		#index = cfg.uidc.signature_list_treeWidget.indexAt(event)
		#cfg.itemMenu = cfg.uidc.signature_list_treeWidget.itemAt(event)
		#cfg.uidc.signature_list_treeWidget.setCurrentItem(cfg.itemMenu)
		m = cfg.QtWidgetsSCP.QMenu()
		m.setToolTipsVisible(True)
		zoomToMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.zoomToMenu, 'semiautomaticclassificationplugin_zoom_to_ROI.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Zoom to'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Zoom to highlighted items'))
		selectAllMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.selectAllMenu, 'semiautomaticclassificationplugin_batch_check.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Check/uncheck'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Check/uncheck highlighted items'))
		clearSelectionMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.clearSelectionMenu, 'semiautomaticclassificationplugin_select_all.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Clear selection'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Clear selection of highlighted items'))
		collapseMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.collapseMenu, 'semiautomaticclassificationplugin_docks.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Collapse/expand all'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Collapse/expand all macroclasses'))
		m.addSeparator()
		changeMacroclassMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.changeMacroclassMenu, 'semiautomaticclassificationplugin_enter.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Change MC ID'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Change MC ID for highlighted items'))
		changeColorMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.changeColorMenu, 'semiautomaticclassificationplugin_enter.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Change color'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Change color for highlighted items'))
		m.addSeparator()
		mergeSignaturesMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.mergeSelectedSignatures, 'semiautomaticclassificationplugin_merge_sign_tool.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Merge items'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Merge highlighted items'))
		calculateSignaturesMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.calculateSignatures, 'semiautomaticclassificationplugin_add_sign_tool.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Calculate signatures'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Calculate signatures for highlighted items'))
		deleteSignaturesMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.removeSelectedSignatures, 'semiautomaticclassificationplugin_delete_signature.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Delete items'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Delete highlighted items'))
		m.addSeparator()
		addSignaturesPlotMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.addSignatureToSpectralPlot, 'semiautomaticclassificationplugin_sign_tool.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Add to spectral plot'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Add highlighted items to spectral plot'))
		addScatterPlotMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.addROIToScatterPlot, 'semiautomaticclassificationplugin_scatter_tool.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Add to scatter plot'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Add highlighted items to scatter plot'))
		propertiesMenu = cfg.SCPD.addMenuItem(m, cfg.SCPD.propertiesMenu, 'semiautomaticclassificationplugin_accuracy_tool.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Properties'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Properties for highlighted items'))
		m.addSeparator()
		importMenu = cfg.SCPD.addMenuItem(m, cfg.utls.importSignaturesTab, 'semiautomaticclassificationplugin_import_spectral_library.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Import'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Import spectral signatures'))
		exportMenu = cfg.SCPD.addMenuItem(m, cfg.utls.exportSignaturesTab, 'semiautomaticclassificationplugin_export_spectral_library.svg', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Export'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Export highlighted items'))
		m.exec_(cfg.uidc.signature_list_treeWidget.mapToGlobal(event))
		
	# properties menu
	def propertiesMenu(self):
		cfg.SCPD.addSignatureToSpectralPlot(1)
		
	# collaps menu
	def collapseMenu(self):
		try:
			if cfg.collapseDock == True:
				cfg.uidc.signature_list_treeWidget.collapseAll()
				cfg.collapseDock = False
			else:
				cfg.uidc.signature_list_treeWidget.expandAll()
				cfg.collapseDock = True
		except:
			cfg.uidc.signature_list_treeWidget.collapseAll()
			cfg.collapseDock = False
			
	# change macroclass menu
	def changeMacroclassMenu(self):
		if len(cfg.uidc.signature_list_treeWidget.selectedItems()) > 0:
			mc = cfg.ROIMacroID
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Change Macroclass ID'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Change the Macroclass ID for highlighted items to ') + str(mc) + ' ?')
			if a == 'Yes':
				for i in cfg.uidc.signature_list_treeWidget.selectedItems():
					# classes
					if len(i.text(1)) > 0:
						id = i.text(5)
						cfg.signList['MACROCLASSID_' + str(id)] = mc
						if id in list(cfg.ROI_SCP_UID.values()):
							cfg.ROI_MC_ID[id] = mc
							rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
							for rI in rId:
								cfg.utls.editFeatureShapefile(cfg.shpLay, rI, cfg.fldMacroID_class, mc)
					# macroclasses
					else:
						count = i.childCount()
						for roi in reversed(range(0, count)):
							idC = i.child(roi).text(5)
							cfg.signList['MACROCLASSID_' + str(idC)] = mc
							if idC in list(cfg.ROI_SCP_UID.values()):
								cfg.ROI_MC_ID[idC] = mc
								rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(idC))
								for rI in rId:
									cfg.utls.editFeatureShapefile(cfg.shpLay, rI, cfg.fldMacroID_class, mc)
				cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)

	# change color menu
	def changeColorMenu(self):
		if len(cfg.uidc.signature_list_treeWidget.selectedItems()) > 0:
			c = cfg.utls.selectColor()
			if c is not None:
				r = []
				for i in cfg.uidc.signature_list_treeWidget.selectedItems():
					id = i.text(5)
					try:
						cfg.treeDockItm[str(id)].setBackground(4, c)
						cfg.signList['COLOR_' + str(id)] = c
					except:
						pass
					try:
						cfg.treeDockMCItm[str(id)].setBackground(4, c)
						cfg.SCPD.roiMacroclassInfoCompleter()
					except:
						pass

	# clear selection menu
	def clearSelectionMenu(self):
		cfg.uidc.signature_list_treeWidget.clearSelection()
		
	# zoom to menu
	def zoomToMenu(self):
		id = cfg.SCPD.getHighlightedIDs('No', 'No')
		cfg.SCPD.zoomToROI(id)
		
	# select all menu
	def selectAllMenu(self):
		for i in cfg.uidc.signature_list_treeWidget.selectedItems():
			# classes
			if len(i.text(1)) > 0:
				try:
					v = cfg.signList['CHECKBOX_' + str(i.text(5))]
					break
				except:
					pass
			# macroclasses
			else:
				count = i.childCount()
				for roi in range(0, count):
					try:
						v = cfg.signList['CHECKBOX_' + str(i.child(roi).text(5))]
						break
					except:
						pass
		try:
			cfg.SCPD.selectAllSignatures(check = not v, selected = True)
		except:
			pass
		
	# Create ROI list
	def ROIListTableTree(self, layer, tree, checkstate=0):
		l = self.clearTree(tree)
		# get ROIs
		cfg.SCPD.getROIAttributes(layer)
		l.blockSignals(True)
		l.setSortingEnabled(False)
		try:
			# macroclasses
			for k in cfg.MCID_List:
				try:
					if k[2] is None:
						c, cc = cfg.utls.randomColor()
						k[2] = c
				except:
					c, cc = cfg.utls.randomColor()
					k[2] = c
				cfg.SCPD.addTreeItem(l, [k[0], k[1]], color = cfg.QtGuiSCP.QColor(k[2]))
			# ROIs
			for k in sorted(cfg.ROI_SCP_UID.values()):
				if str(k) in list(cfg.signIDs.values()):
					cfg.SCPD.addChildTreeItem(l, [int(float(cfg.ROI_MC_ID[k])), str(cfg.ROI_MC_Info[k]), int(float(cfg.ROI_C_ID[k])), str(cfg.ROI_C_Info[k]), cfg.ROISigTypeNm, k], checkboxState = cfg.signList['CHECKBOX_' + str(k)], color = cfg.signList['COLOR_' + str(k)])
					# for signature list coherence
					try:
						cfg.signList['MACROCLASSID_' + str(k)] = int(float(cfg.ROI_MC_ID[k]))
					except:
						cfg.signList['MACROCLASSID_' + str(k)] = int(0)
					cfg.signList['MACROCLASSINFO_' + str(k)] = str(cfg.ROI_MC_Info[k])
					try:
						cfg.signList['CLASSID_' + str(k)] = int(float(cfg.ROI_C_ID[k]))
					except:
						cfg.signList['CLASSID_' + str(k)] = int(0)
					cfg.signList['CLASSINFO_' + str(k)] = str(cfg.ROI_C_Info[k])
				else:
					try:
						cfg.SCPD.addChildTreeItem(l, [int(float(cfg.ROI_MC_ID[k])), str(cfg.ROI_MC_Info[k]), int(float(cfg.ROI_C_ID[k])), str(cfg.ROI_C_Info[k]), cfg.ROITypeNm, k], checkboxState = cfg.signList['CHECKBOX_' + str(k)])
					except:
						cfg.SCPD.addChildTreeItem(l, [int(float(cfg.ROI_MC_ID[k])), str(cfg.ROI_MC_Info[k]), int(float(cfg.ROI_C_ID[k])), str(cfg.ROI_C_Info[k]), cfg.ROITypeNm, k], checkboxState = cfg.QtSCP.Checked)
					# for signature list coherence
					try:
						cfg.signList['MACROCLASSID_' + str(k)] = int(float(cfg.ROI_MC_ID[k]))
					except:
						cfg.signList['MACROCLASSID_' + str(k)] = int(0)
					cfg.signList['MACROCLASSINFO_' + str(k)] = str(cfg.ROI_MC_Info[k])
					try:
						cfg.signList['CLASSID_' + str(k)] = int(float(cfg.ROI_C_ID[k]))
					except:
						cfg.signList['CLASSID_' + str(k)] = int(0)
					cfg.signList['CLASSINFO_' + str(k)] = str(cfg.ROI_C_Info[k])
					cfg.signList['CHECKBOX_' + str(k)] = 2
					cfg.signList['COLOR_' + str(k)] = cfg.QtGuiSCP.QColor(255, 255, 225)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msgErr43()
		# signature
		for k in sorted(cfg.signIDs.values()):
			if str(k) not in list(cfg.ROI_SCP_UID.values()):
				cfg.SCPD.addChildTreeItem(l, [int(cfg.signList['MACROCLASSID_' + str(k)]), str(cfg.signList['MACROCLASSINFO_' + str(k)]), int(cfg.signList['CLASSID_' + str(k)]), str(cfg.signList['CLASSINFO_' + str(k)]), cfg.SIGTypeNm, k], checkboxState = cfg.signList['CHECKBOX_' + str(k)], color = cfg.signList['COLOR_' + str(k)])
		l.show()
		l.setSortingEnabled(True)
		l.blockSignals(False)
		cfg.SCPD.exportMCIDList()
		cfg.LCSignT.LCSignatureThresholdListTable()
		cfg.signT.signatureThresholdListTable()
		# info completer
		cfg.SCPD.roiInfoCompleter()
		cfg.SCPD.roiMacroclassInfoCompleter()
		
	# filter tree	
	def filterTree(self):
		try:
			text = cfg.uidc.ROI_filter_lineEdit.text()
			t = cfg.uidc.signature_list_treeWidget
			r = t.invisibleRootItem()
			t.blockSignals(True)
			if len(text)>0:
				t.expandAll()
				items = t.findItems(text, cfg.QtSCP.MatchContains)
				for i in range(0, r.childCount()):
					c = r.child(i)
					c.setHidden(False)
					for x in range(0, c.childCount()):
						if text.lower() in c.child(x).text(2).lower():
							c.child(x).setHidden(False)
						else:
							c.child(x).setHidden(True)
			else:
				t.expandAll()
				for i in range(0, r.childCount()):
					c = r.child(i)
					c.setHidden(False)
					for x in range(0, c.childCount()):
						if text in c.child(x).text(0):
							c.child(x).setHidden(False)
			t.blockSignals(False)
		except Exception as err:
			# logger
			if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		
##################################
	''' Interface functions '''
##################################

	# right click ROI pointer for pixel signature
	def pointerRightClickROI(self, point):
		if cfg.ctrlClick == 1:
			bandSetNumList = list(range(0, len(cfg.bandSetsList)))
		else:
			bandSetNumList = [cfg.bndSetNumber]
		for i in bandSetNumList:
			point = cfg.utls.checkPointImage(cfg.bandSetsList[i][8], point)
			if cfg.pntCheck == 'Yes':
				cfg.utls.calculatePixelSignature(point, cfg.bandSetsList[i][8], i, 'Yes')
		cfg.ctrlClick = None
		
	# zoom to ROI
	def zoomToTempROI(self):
		if cfg.lstROI is not None:
			cfg.utls.setMapExtentFromLayer(cfg.lstROI)

	# create a ROI in the same point
	def redoROI(self):
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '>>> REDO ROI creation')
		# check if other processes are active
		if cfg.actionCheck == 'No':
			if cfg.pntROI is None:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'REDO ROI fail: no point')
				pass
			else:
				self.createROI(cfg.pntROI)
				# logger
				cfg.utls.logCondition('redoROI ' + cfg.utls.lineOfCode(), '<<< REDO ROI creation')

	# show hide ROI radio button
	def showHideROI(self):
		try:
			if cfg.show_ROI_radioButton.isChecked():
				l = cfg.utls.selectLayerbyName(cfg.trnLay)
				if l is not None:
					cfg.utls.setLayerVisible(l, True)
				cfg.utls.moveLayerTop(l)
				cfg.rbbrBndPol.show()
				# ROI point
				self.vx.show()
			else:
				l = cfg.utls.selectLayerbyName(cfg.trnLay)
				if l is not None:
					cfg.utls.setLayerVisible(l, False)
				cfg.rbbrBndPol.hide()
				# ROI point
				self.vx.hide()
			cfg.cnvs.setRenderFlag(False)
			cfg.cnvs.refresh()
			cfg.cnvs.setRenderFlag(True)
		except:
			pass
		
	# set Min ROI size
	def minROISize(self):
		cfg.minROISz = int(cfg.Min_region_size_spin.value())
		cfg.utls.writeProjectVariable('minROISize', str(cfg.minROISz))
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'min roi size: ' + str(cfg.minROISz))

	# set Max ROI size
	def maxROIWidth(self):
		cfg.maxROIWdth = int(cfg.Max_ROI_width_spin.value())
		if (cfg.maxROIWdth % 2 == 0):
			cfg.maxROIWdth = cfg.maxROIWdth + 1
		cfg.utls.writeProjectVariable('maxROIWidth', str(cfg.maxROIWdth))
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'max roi width: ' + str(cfg.maxROIWdth))

	def pointerClickROI(self, point):
		# check if other processes are active
		if cfg.actionCheck == 'No':
			cfg.origPoint = point
			cfg.utls.checkPointImage(cfg.bandSetsList[cfg.bndSetNumber][8], point)
			if cfg.pntCheck == 'Yes':
				cfg.pntROI = cfg.lstPnt
				self.createROI(cfg.pntROI)
		
	# Activate pointer for ROI creation
	def pointerManualROIActive(self):
		cfg.lastVrt = []
		cfg.mrctrVrtc = []
		t = cfg.mnlROI
		cfg.cnvs.setMapTool(t)
		c = cfg.QtGuiSCP.QCursor()
		c.setShape(cfg.QtSCP.CrossCursor)
		cfg.cnvs.setCursor(c)

	# pointer moved
	def movedPointer(self, point):
		px = cfg.QtGuiSCP.QPixmap(':/pointer/icons/pointer/ROI_pointer.svg')
		c = cfg.QtGuiSCP.QCursor(px)
		if cfg.uidc.display_cursor_checkBox.isChecked() is True:
			nm = 'No'
			try:
				if len(cfg.bandSetsList[cfg.bndSetNumber][3]) > 0:
					point = cfg.utls.checkPointImage(cfg.bandSetsList[cfg.bndSetNumber][8], point, 'Yes')
					if point is not None and point != 'No':
						if str(cfg.indName) == cfg.indNDVI:
							nm = cfg.utls.NDVIcalculator(cfg.bandSetsList[cfg.bndSetNumber][8], point)
						elif str(cfg.indName) == cfg.indEVI:
							nm = cfg.utls.EVIcalculator(cfg.bandSetsList[cfg.bndSetNumber][8], point)
						elif str(cfg.indName) == cfg.indCustom:
							nm = cfg.utls.customIndexCalculator(cfg.bandSetsList[cfg.bndSetNumber][8], point)
					if nm != 'No':
						c = cfg.SCPD.cursorCreation(nm)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		cfg.cnvs.setCursor(c)
		
	# Activate pointer for ROI creation
	def pointerROIActive(self):
		self.clearCanvas()
		# connect to click
		t = cfg.regionROI
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(':/pointer/icons/pointer/ROI_pointer.svg')
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'pointer active: ROI')

	def cursorCreation(self, number):
		num = str(number)[0:6]
		pmap = cfg.QtGuiSCP.QPixmap(["48 48 3 1",
					"      c None",
					".     c #ffffff",
					"+     c #000000",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"                                                ",
					"                      ++++                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                +++++++..+++++++                ",
					"                +..............+                ",
					"                +..............+                ",
					"                +++++++..+++++++                ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      ++++                      ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",])
		painter = cfg.QtGuiSCP.QPainter()
		painter.begin(pmap)
		painter.setPen(cfg.QtGuiSCP.QColor(0, 0, 0))
		painter.setFont(cfg.QtGuiSCP.QFont('Monospace', 9))
		painter.drawText(cfg.QtCoreSCP.QPoint(2, 12), num)
		painter.end()
		crsr = cfg.QtGuiSCP.QCursor(pmap)
		return crsr
		
	# set Range radius
	def rangeRadius(self):
		cfg.rngRad = float(cfg.Range_radius_spin.value())
		cfg.utls.writeProjectVariable('rangeRadius', str(cfg.rngRad))
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'range radius: ' + str(cfg.rngRad))
		
	# set rapid ROI band
	def rapidROIband(self):
		# band set
		if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
			iB = len(cfg.bandSetsList[cfg.bndSetNumber][3])
		else:
			i = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8], 'Yes')
			try:
				iB = i.bandCount()
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				iB = 1
		if cfg.uidc.rapidROI_band_spinBox.value() > iB:
			cfg.uidc.rapidROI_band_spinBox.setValue(iB)
		cfg.ROIband = cfg.uidc.rapidROI_band_spinBox.value()
		cfg.utls.writeProjectVariable('rapidROIBand', str(cfg.ROIband))
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'ROI band: ' + str(cfg.ROIband))
		
	# Activate rapid ROI creation
	def rapidROICheckbox(self):
		if cfg.uidc.rapid_ROI_checkBox.isChecked() is True:
			cfg.rpdROICheck = '2'
		else:
			cfg.rpdROICheck = '0'
		cfg.utls.writeProjectVariable('rapidROI', cfg.rpdROICheck)
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' checkbox set: ' + str(cfg.rpdROICheck))
		
	# set vegetation index name
	def vegetationIndexName(self):
		cfg.indName = str(cfg.uidc.vegetation_index_comboBox.currentText())
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'index name: ' + str(cfg.indName))
		
	# Activate vegetation index checkbox
	def vegetationIndexCheckbox(self):
		if cfg.uidc.display_cursor_checkBox.isChecked() is True:
			cfg.vegIndexCheck = '2'
			cfg.msgWar8check = '0'
		else:
			cfg.vegIndexCheck = '0'
		cfg.utls.writeProjectVariable('vegetationIndex', cfg.vegIndexCheck)
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' checkbox set: ' + str(cfg.vegIndexCheck))
	
	# set ROI macroclass ID
	def setROIMacroID(self):
		cfg.ROIMacroID = cfg.uidc.ROI_Macroclass_ID_spin.value()
		cfg.utls.writeProjectVariable('ROIMacroIDField', str(cfg.ROIMacroID))
		for i in cfg.MCID_List:
			if str(cfg.ROIMacroID) == i[0]:
				cfg.uidc.ROI_Macroclass_line.setText(i[1])
				cfg.ROIMacroClassInfo = str(i[1])
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'roi macroclass id: ' + str(cfg.ROIMacroID))
		
	# set ROI class ID
	def setROIID(self):
		cfg.ROIID = cfg.uidc.ROI_ID_spin.value()
		cfg.utls.writeProjectVariable('ROIIDField', str(cfg.ROIID))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'roi id: ' + str(cfg.ROIID))

	# set ROI class info
	def roiClassInfo(self):
		cfg.uidc.ROI_Class_line.blockSignals(True)
		iTxt = str(cfg.uidc.ROI_Class_line.text())
		cfg.ROIInfo = str(iTxt)
		cfg.utls.writeProjectVariable('ROIInfoField', str(cfg.ROIInfo))
		cfg.uidc.ROI_Class_line.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'roi info: ' + str(cfg.ROIInfo))
		
	# ROI info completer
	def roiInfoCompleter(self):
		if cfg.shpLay is not None:
			try:
				l = cfg.utls.getFieldAttributeList(cfg.shpLay, cfg.fldROI_info)
				# class names
				cfg.cmplClsNm = cfg.QtWidgetsSCP.QCompleter(l)
				cfg.uidc.ROI_Class_line.setCompleter(cfg.cmplClsNm)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))

	# set custom expression
	def customExpressionEdited(self):
		cfg.customExpression = str(cfg.uidc.custom_index_lineEdit.text())
		cfg.utls.writeProjectVariable('customExpression', str(cfg.customExpression))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' expression: ' + str(cfg.customExpression))
			
	# set ROI class info
	def roiMacroclassInfo(self):
		cfg.uidc.ROI_Macroclass_line.blockSignals(True)
		iTxt = str(cfg.uidc.ROI_Macroclass_line.text())
		cfg.ROIMacroClassInfo = str(iTxt)
		cfg.utls.writeProjectVariable('ROIMacroclassInfoField', str(cfg.ROIMacroClassInfo))
		cfg.uidc.ROI_Macroclass_line.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'roi info: ' + str(cfg.ROIInfo))
			
	# ROI info completer
	def roiMacroclassInfoCompleter(self):
		if cfg.shpLay is not None:
			try:
				MCID_LIST = cfg.SCPD.exportMCIDList()
				l = [MC[1] for MC in MCID_LIST]
				# class names
				cfg.cmplMClsNm = cfg.QtWidgetsSCP.QCompleter(l)
				cfg.uidc.ROI_Macroclass_line.setCompleter(cfg.cmplMClsNm)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		
	# signature table double click
	def signatureListDoubleClickTree(self, item, column):
		tW = cfg.uidc.signature_list_treeWidget
		for id, val in cfg.treeDockItm.items():
			if val == item:
				#if column == 0:
				#	self.selectAllSignatures(not item.checkState(0))
				if column == 4:
					c = cfg.utls.selectColor()
					if c is not None:
						r = []
						for i in tW.selectedItems():
							id = i.text(5)
							try:
								cfg.treeDockItm[str(id)].setBackground(4, c)
								cfg.signList['COLOR_' + str(id)] = c
							except:
								pass
				else:
					cfg.SCPD.zoomToROI([id])
				break
		for id, val in cfg.treeDockMCItm.items():
			if val == item:
				if column == 0 or column == 1 or column == 2 or column == 3:
					item.setExpanded(not item.isExpanded())
				elif column == 4:
					c = cfg.utls.selectColor()
					if c is not None:
						cfg.treeDockMCItm[str(id)].setBackground(4, c)
						cfg.SCPD.roiMacroclassInfoCompleter()
						break
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' signatures index: ' + str(column))
		
	# edited cell
	def editedCellTree(self, item, column):
		tW = cfg.uidc.signature_list_treeWidget
		tW.setSortingEnabled(False)
		tW.blockSignals(True)
		move = 'No'
		# items
		for id, val in cfg.treeDockItm.items():
			if val == item:
				if column == 0:
					cfg.signList['CHECKBOX_' + str(id)] = item.checkState(0)
					oldV = int(cfg.signList['MACROCLASSID_' + str(id)])
					v = int(item.text(column))
					if oldV != v:
						try:
							if v < 0:
								v = 0
								item.setData(column, v)
								cfg.mx.msg17()
							cfg.signList['MACROCLASSID_' + str(id)] = v
							if id in list(cfg.ROI_SCP_UID.values()):
								cfg.ROI_MC_ID[id] = v
								rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
								for rI in rId:
									cfg.utls.editFeatureShapefile(cfg.shpLay, rI, cfg.fldMacroID_class, v)
							move = 'Yes'
						except:
							item.setData(column, 0, oldV)
				elif column == 1:
					try:
						v = int(item.text(column))
						if v < 0:
							v = 0
							item.setData(column, v)
							cfg.mx.msg17()
						cfg.signList['CLASSID_' + str(id)] = v
						if id in list(cfg.ROI_SCP_UID.values()):
							cfg.ROI_C_ID[id] = v
							rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
							for rI in rId:
								cfg.utls.editFeatureShapefile(cfg.shpLay, rI, cfg.fldID_class, v)
					except:
						item.setData(column, 0, int(cfg.signList['CLASSID_' + str(id)]))
				elif column == 2:
					iTxt2 = item.text(column)
					cfg.signList['CLASSINFO_' + str(id)] = iTxt2
					if id in list(cfg.ROI_SCP_UID.values()):
						cfg.ROI_C_Info[id] = iTxt2
						rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(id))
						for rI in rId:
							cfg.utls.editFeatureShapefile(cfg.shpLay, rI, cfg.fldROI_info, iTxt2)
				elif column == 3:
					item.setData(column, 0, '')
				elif column == 4:
					item.setData(column, 0, '')
					tW.clearSelection()
				break
		# macroclasses
		for id, val in cfg.treeDockMCItm.items():
			if val == item:
				if column == 0:
					v = item.text(column)
					oldV = str(id)
					if str(v) != str(oldV):
						count = item.childCount()
						try:
							v = int(v)
							if v < 0:
								v = 0
								item.setData(column, v)
								cfg.mx.msg17()
							move = 'Yes'
							for roi in reversed(range(0, count)):
								cld = item.child(roi)
								idC = cld.text(5)
								cfg.signList['MACROCLASSID_' + str(idC)] = v
								if idC in list(cfg.ROI_SCP_UID.values()):
									cfg.ROI_MC_ID[idC] = v
									rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(idC))
									for rI in rId:
										cfg.utls.editFeatureShapefile(cfg.shpLay, rI, cfg.fldMacroID_class, v)
						except:
							item.setData(column, 0, int(oldV))
				elif column == 2:
					v = item.text(column)
					count = item.childCount()
					for roi in reversed(range(0, count)):
						cld = item.child(roi)
						idC = cld.text(5)
						cfg.signList['MACROCLASSINFO_' + str(idC)] = v
				elif column == 3:
					item.setData(column, 0, '')
				elif column == 4:
					item.setData(column, 0, '')
					tW.clearSelection()
				break
		tW.setSortingEnabled(True)
		tW.blockSignals(False)
		if move == 'Yes':
			cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
		else:
			cfg.LCSignT.LCSignatureThresholdListTable()
			cfg.signT.signatureThresholdListTable()
			cfg.SCPD.exportMCIDList()
			# info completer
			cfg.SCPD.roiInfoCompleter()
			cfg.SCPD.roiMacroclassInfoCompleter()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'edited cell' + str(column))
			
	# create MCID list for symbology
	def createMCIDList(self):
		sL = []
		for k in cfg.MCID_List:
			sL.append([k[0], k[1], None, None, None, None, k[2]])
		return sL
		
	# export MCID list for symbology
	def exportMCIDList(self):
		sL = []
		s = []
		delete = []
		tW = cfg.uidc.signature_list_treeWidget
		for id, val in cfg.treeDockMCItm.items():
			try:
				count = val.childCount()
				if count > 0:
					mID = val.text(0)
					mC = val.text(2)
					c = val.background(4).color() 
					s = []
					s.append(mID)
					s.append(mC)
					s.append(c.toRgb().name())
					sL.append(s)
				else:
					delete.append([id, val])
			except:
				delete.append([id, val])
		for id, val in delete:
			try:
				tW.takeTopLevelItem(tW.indexOfTopLevelItem(val))
			except:
				pass
			try:
				del cfg.treeDockMCItm[id]
			except:
				pass
		cfg.MCID_List = sL
		return sL

	# zoom to clicked ROI 
	def zoomToROI(self, idList):
		l = cfg.shpLay
		rId = []
		if l is not None:
			for id in idList:
				if id in list(cfg.ROI_SCP_UID.values()):
					rId.append(cfg.utls.getIDByAttributes(l, cfg.fldSCP_UID, str(id)))
			cfg.utls.zoomToSelected(l, rId)
			cfg.utls.setLayerVisible(l, True)
			cfg.utls.moveLayerTop(l)

	# Activate signature calculation
	def signatureCheckbox(self):
		if cfg.uidc.signature_checkBox.isChecked() is True:
			cfg.sigClcCheck = '2'
			cfg.ui.signature_checkBox2.setCheckState(2)
		else:
			cfg.sigClcCheck = '0'
			cfg.ui.signature_checkBox2.setCheckState(0)
		cfg.utls.writeProjectVariable('calculateSignature', cfg.sigClcCheck)
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' checkbox set: ' + str(cfg.sigClcCheck))
		
	# Activate save input file
	def saveInputCheckbox(self):
		if cfg.uidc.save_input_checkBox.isChecked() is True:
			cfg.saveInputCheck = '2'
			cfg.uidc.save_input_checkBox.setCheckState(2)
		else:
			cfg.saveInputCheck = '0'
			cfg.uidc.save_input_checkBox.setCheckState(0)
		cfg.utls.writeProjectVariable('saveInput', cfg.saveInputCheck)
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' checkbox set: ' + str(cfg.saveInputCheck))
		
##################################
	''' Shapefile functions '''
##################################
			
	# reset input 
	def resetInput(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Remove training input'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Are you sure you want to remove training input?'))
		if a == 'Yes':
			cfg.SCPD.resetInputDock()
		
	# reset input 
	def resetInputDock(self):
		cfg.treeDockItm = {}
		cfg.treeDockMCItm = {}
		cfg.uidc.signature_list_treeWidget.clear()
		try:
			cfg.utls.removeLayerByLayer(cfg.shpLay)
			cfg.cnvs.refresh()
		except:
			pass
		# shape layer
		cfg.shpLay = None
		# training layer name
		cfg.trnLay = None
		# signature file path
		cfg.sigFile = None
		cfg.inptDir = None
		cfg.scpFlPath = None
		cfg.signList = {}
		cfg.signIDs = {}
		cfg.uidc.trainingFile_lineEdit.setText('')
		cfg.utls.writeProjectVariable('trainingLayer', '')
		
	# Create new input 
	def createInput(self):
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '>>> create input click')
		try:
			sL = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Create SCP training input'), '', '*.scp', 'scp')
			if sL is not False:
				cfg.SCPD.resetInputDock()
				try:
					# band set
					if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
						iB = len(cfg.bandSetsList[cfg.bndSetNumber][3])
						# crs of loaded raster
						b = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][0], 'Yes')
						filePath = cfg.utls.layerSource(b)
						crs = cfg.utls.getCrsGDAL(filePath)
						if len(crs) == 0:
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR crs')
							cfg.mx.msgErr61(cfg.bandSetsList[cfg.bndSetNumber][3][0])
							return
					else:
						# crs of loaded raster
						b = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8])
						filePath = cfg.utls.layerSource(b)
						crs = cfg.utls.getCrsGDAL(filePath)
						iB = b.bandCount()
						if len(crs) == 0:
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR crs')
							cfg.mx.msgErr61(cfg.bandSetsList[cfg.bndSetNumber][8])
							return
					# shapefile
					name = cfg.utls.fileNameNoExt(sL)
					dT = cfg.utls.getTime()
					unzipDir = cfg.tmpDir + '/' + name + dT
					#shpF = unzipDir + '/' + name + '.shp'
					shpF = unzipDir + '/' + name + '.gpkg'
					oDir = cfg.utls.makeDirectory(unzipDir)
					#cfg.utls.createSCPShapefile(crs, shpF)
					cfg.utls.createSCPVector(crs, shpF)
					sigFile = unzipDir + '/' + name + '.slf'
					cfg.SCPD.saveSignatureList(sigFile)
					# create zip file
					cfg.utls.zipDirectoryInFile(sL, unzipDir)
					# open input
					cfg.SCPD.openInput(sL)
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '<<< SCP created: ' + '\'' + str(sL) + '\'')
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.ipt.refreshRasterLayer()
					cfg.mx.msg4()
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msg4()

	# Save last ROI to shapefile 
	def saveROItoShapefile(self, progressbar = 'Yes', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		l = cfg.shpLay
		if l is None:
			cfg.mx.msg3()
			return 0
		if progressbar is False:
			progressbar = 'Yes'
		# check if layer was removed ## there is an issue if the removed layer was already saved in the project ##
		try:
			sN = str(cfg.shpLay.name())
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msg3()
		# check if no layer is selected
		if cfg.shpLay is None:
			cfg.mx.msg3()
		# check if no ROI created
		elif cfg.lstROI is None:
			cfg.mx.msg6()
		elif len(cfg.bandSetsList[bandSetNumber][3])==0:
			cfg.mx.msgErr2(SMTP = 'No')
		else:
			if progressbar == 'Yes':
				cfg.uiUtls.addProgressBar()
				cfg.uiUtls.updateBar(10, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Creating ROI'))
			# get polygon from ROI
			try:
				# region growing ROI
				cfg.utls.copyFeatureToLayer(cfg.lstROI, 0, cfg.shpLay)
			except:
				# manual ROI
				cfg.utls.copyFeatureToLayer(cfg.lstROI, 1, cfg.shpLay)
			self.ROILastID = cfg.utls.getLastFeatureID(cfg.shpLay)
			if progressbar == 'Yes':
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
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				cfg.shpLay.startEditing()	
				cfg.shpLay.dataProvider().deleteFeatures([self.ROILastID])
				cfg.shpLay.commitChanges()
				cfg.shpLay.dataProvider().createSpatialIndex()
				cfg.shpLay.updateExtents()
				cfg.uidc.undo_save_Button.setEnabled(False)
				a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Add required fields'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'It appears that the shapefile ') + cfg.shpLay.name() + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', ' is missing some fields that are required for the signature calculation. \nDo you want to add the required fields to this shapefile?'))
				if a == 'Yes':
					fds = []
					fds.append(cfg.qgisCoreSCP.QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))	
					cfg.shpLay.startEditing()
					aF = cfg.shpLay.dataProvider().addAttributes(fds)
					# commit changes
					cfg.shpLay.commitChanges()
					cfg.shpLay.dataProvider().createSpatialIndex()
					cfg.shpLay.updateExtents()
					if progressbar == 'Yes':
						cfg.uiUtls.removeProgressBar()
					return 1
				else:
					if progressbar == 'Yes':
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
			cfg.shpLay.dataProvider().createSpatialIndex()
			cfg.shpLay.updateExtents()
			cfg.uidc.undo_save_Button.setEnabled(True)
			try:
				self.clearCanvasPoly()
			except:
				pass
			try:
				self.clearROICanvas()
			except:
				pass
			if progressbar == 'Yes':
				cfg.uiUtls.updateBar(40)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'roi: ' + str(cfg.ROIID) + ', ' + str(cfg.ROIInfo) + ' saved to shapefile: ' + str(cfg.shpLay.name()))
			# calculate signature if checkbox is yes
			if cfg.uidc.signature_checkBox.isChecked() is True:
				if progressbar == 'Yes':
					cfg.uiUtls.updateBar(50)
					cfg.utls.calculateSignature(cfg.shpLay, cfg.bandSetsList[bandSetNumber][8], [self.ROILastID], cfg.ROIMacroID, cfg.ROIMacroClassInfo, cfg.ROIID, cfg.ROIInfo, 50, 40, 'No', 'No', UID, bandSetNumber = bandSetNumber)
				else:
					cfg.utls.calculateSignature(cfg.shpLay, cfg.bandSetsList[bandSetNumber][8], [self.ROILastID], cfg.ROIMacroID, cfg.ROIMacroClassInfo, cfg.ROIID, cfg.ROIInfo, None, None, 'No', 'No', UID, bandSetNumber = bandSetNumber)
				if progressbar == 'Yes':
					cfg.uiUtls.updateBar(90)
			else:
				cfg.signList['MACROCLASSID_' + str(UID)] = cfg.ROIMacroID
				cfg.signList['MACROCLASSINFO_' + str(UID)] = cfg.ROIMacroClassInfo
				cfg.signList['CLASSID_' + str(UID)] = cfg.ROIID
				cfg.signList['CLASSINFO_' + str(UID)] = cfg.ROIInfo
				cfg.signList['CHECKBOX_' + str(UID)] = 2
				cfg.signList['COLOR_' + str(UID)] = cfg.QtGuiSCP.QColor(255, 255, 225)
			cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
			# increase C_ID
			v = cfg.uidc.ROI_ID_spin.value()
			cfg.uidc.ROI_ID_spin.setValue(v+1)
			if cfg.saveInputCheck == '2':
				cfg.SCPD.saveMemToSHP(cfg.shpLay)
				cfg.utls.zipDirectoryInFile(cfg.scpFlPath, cfg.inptDir)
			if progressbar == 'Yes':
				cfg.uiUtls.updateBar(100)
				cfg.uiUtls.removeProgressBar()
				
	# delete last saved ROI
	def undoSaveROI(self):
		l = cfg.shpLay
		if l is None:
			cfg.mx.msg3()
			return 0
		# check if layer was removed ## there is an issue if the removed layer was already saved in the project ##
		try:
			s = str(cfg.shpLay.name())
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msg3()
		# check if no layer is selected
		if cfg.shpLay is None:
			cfg.mx.msg3()
		# check if no ROI created
		elif cfg.lstROI is None:
			cfg.mx.msg6()
		else:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Undo save ROI'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Are you sure you want to delete the last saved ROI?'))
			if a == 'Yes':
				f = cfg.utls.getFeaturebyID(cfg.shpLay, self.ROILastID)
				SCP_UID  = str(f[cfg.fldSCP_UID])
				cfg.utls.deleteFeatureShapefile(cfg.shpLay, [self.ROILastID])
				try:
					cfg.SCPD.deleteSignatureByID(SCP_UID)
					del cfg.treeDockItm[SCP_UID]
				except:
					pass
				cfg.uidc.undo_save_Button.setEnabled(False)
				cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
				cfg.cnvs.refresh()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'roi deleted: ' + str(self.ROILastID))
				
		
##################################
	''' Map functions '''
##################################
				
	# add Highlight Polygon
	def addHighlightPolygon(self, sourceLayer, ID):
		try:
			self.clearCanvasPoly()
		except:
			pass
		clr = cfg.QtGuiSCP.QColor(cfg.ROIClrVal)
		rT = 255 - cfg.ROITrnspVal * 255 / 100
		clr.setAlpha(rT)
		f = cfg.utls.getFeaturebyID(sourceLayer, ID)
		cfg.rbbrBndPol = cfg.qgisGuiSCP.QgsHighlight(cfg.cnvs, f.geometry(), sourceLayer)
		cfg.rbbrBndPol.setWidth(2)
		cfg.rbbrBndPol.setColor(cfg.QtGuiSCP.QColor(cfg.ROIClrOutlineValDefault))
		try:
			cfg.rbbrBndPol.setFillColor(clr)
		except:
			pass
		cfg.rbbrBndPol.show()
		cfg.show_ROI_radioButton.setChecked(True)
		cfg.ctrlClick = None

	# clear canvas
	def clearCanvas(self):
		cfg.lastVrt = []
		cfg.rbbrBnd.reset(True)
		for m in cfg.mrctrVrtc:
		    cfg.cnvs.scene().removeItem(m)
		    del m
		cfg.cnvs.refresh()
		try:
			self.clearROICanvas()
		except:
			pass
		
	# clear ROI point canvas
	def clearROICanvas(self):
		cfg.rbbrBnd.reset(True)
		for m in self.ROIVrtc:
		    cfg.cnvs.scene().removeItem(m)
		    del m
		cfg.cnvs.refresh()	

	# clear canvas
	def clearCanvasPoly(self):
		cfg.rbbrBndPol.hide()
		cfg.cnvs.refresh()	
			
##################################
	''' ROI functions '''
##################################
			
	# left click
	def clckL(self, pnt):
		pntO = pnt
		# band set
		if len(cfg.bandSetsList[cfg.bndSetNumber][3])>0:
			pnt = cfg.utls.checkPointImage(cfg.bandSetsList[cfg.bndSetNumber][8], pnt)
			if cfg.pntCheck == 'No':
				return 'No'
		dT = cfg.utls.getTime()
		# temp name
		tN = cfg.subsTmpROI + dT
		# crs
		pCrs = cfg.utls.getQGISCrs()
		mL = cfg.qgisCoreSCP.QgsVectorLayer('MultiPolygon?crs=' + str(pCrs.toWkt()), tN, 'memory')
		mL.setCrs(pCrs) 
		cfg.lastVrt.append(pnt)
		cfg.rbbrBnd.addPoint(cfg.qgisCoreSCP.QgsPointXY(pntO))
		geom = cfg.rbbrBnd.asGeometry()
		v = cfg.qgisGuiSCP.QgsVertexMarker(cfg.cnvs)
		v.setCenter(pntO)
		cfg.mrctrVrtc.append(v)
		cfg.rbbrBnd.setToGeometry(geom, mL)
		cfg.rbbrBnd.show()
		
	# right click
	def clckR(self, pnt):
		self.clckL(pnt)
		f = cfg.qgisCoreSCP.QgsFeature()
		dT = cfg.utls.getTime()
		# temp name
		tN = cfg.subsTmpROI + dT
		crs = cfg.utls.getQGISCrs()
		# band set
		if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
			try:
				# crs of loaded raster
				bN = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][0], 'Yes')
				crs = cfg.utls.getCrs(bN)
			except:
				crs = cfg.utls.getQGISCrs()
		else:
			try:
				# crs of loaded raster
				b = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8])
				crs = cfg.utls.getCrs(b)
			except:
				crs = cfg.utls.getQGISCrs()
		mL = cfg.qgisCoreSCP.QgsVectorLayer('MultiPolygon?crs=' + str(crs.toWkt()), tN, 'memory')
		mL.setCrs(crs) 
		if not len(cfg.lastVrt) >= 3:
			cfg.mx.msg16()
			self.clearCanvas()
			return
		pointF = cfg.QtCoreSCP.QPointF()
		polF = cfg.QtGuiSCP.QPolygonF()
		for v in cfg.lastVrt:
			pointF.setX(v.x())
			pointF.setY(v.y())
			polF.append(pointF)
		pointF.setX(cfg.lastVrt[0].x())
		pointF.setY(cfg.lastVrt[0].y())
		polF.append(pointF)
		g = cfg.qgisCoreSCP.QgsGeometry().fromQPolygonF(polF)
		mL.addTopologicalPoints(g)
		pr = mL.dataProvider()
		# create temp ROI
		mL.startEditing()		
		# add fields
		pr.addAttributes( [cfg.qgisCoreSCP.QgsField('ID',  cfg.QVariantSCP.Int)] )
		# add a feature
		if cfg.ctrlClick is not None:
			g = self.addPartToROI(g)
		else:
			cfg.lstROI2 = cfg.lstROI2 
		f.setGeometry(g)
		f.setAttributes([1])
		pr.addFeatures([f])
		mL.commitChanges()
		mL.updateExtents()
		self.clearCanvas()
		# add ROI layer
		cfg.lstROI = mL
		self.addHighlightPolygon(cfg.lstROI, 1)
		if cfg.uidc.auto_calculate_ROI_signature_radioButton.isChecked():
			cfg.uiUtls.addProgressBar()
			cfg.uiUtls.updateBar(10)
			# ROI date time for temp name
			cfg.ROITime = cfg.datetimeSCP.datetime.now()
			self.tempROISpectralSignature()
			cfg.uiUtls.removeProgressBar()
		cfg.uidc.button_Save_ROI.setEnabled(True)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '<<< ROI created: ' + str(tN))
			
	# add multipart ROI
	def addPartToROI(self, part):
		if cfg.lstROI is not None and cfg.ctrlClick == 1:
			ft = cfg.lstROI.getFeatures()
			f = cfg.qgisCoreSCP.QgsFeature()
			ft.nextFeature(f)
			g = cfg.qgisCoreSCP.QgsGeometry(f.geometry())
			g.convertToMultiType()
			part.convertToMultiType()
			g.addPartGeometry(part)
			cfg.lstROI2 = cfg.lstROI
			return g
		else:
			return part
			
	def deleteLastROI(self):
		cfg.lstROI = cfg.lstROI2
		try:
			self.addHighlightPolygon(cfg.lstROI, 1)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
						
	# create a ROI
	def createROI(self, point, progressbar = 'Yes', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if (float(cfg.maxROIWdth) % 2 == 0):
			cfg.maxROIWdth = float(cfg.maxROIWdth) + 1
		if cfg.scipyCheck == 'No':
			if str(cfg.osSCP.name) == 'nt':
				cfg.mx.msgWar2Windows()
			else:
				cfg.mx.msgWar2Linux()
			cfg.pntROI = None
		elif cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes') is None:
			# if band set then pass
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				pass
			else:
				cfg.mx.msg4()
				self.refreshRasterLayer()
				cfg.pntROI = None
		if cfg.pntROI != None:
			if progressbar == 'Yes':
				cfg.uiUtls.addProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '>>> ROI click')
			if progressbar == 'Yes':
				cfg.uiUtls.updateBar(10)
			# ROI date time for temp name
			cfg.ROITime = cfg.datetimeSCP.datetime.now()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'point (X,Y) = (%s,%s)' % (cfg.pntROI.x() , cfg.pntROI.y()))
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			# temp files
			tS = cfg.utls.createTempRasterPath('gpkg')
			# temp name
			dT = cfg.utls.getTime()
			tN = cfg.subsTmpROI + dT
			# crs
			pCrs = cfg.utls.getQGISCrs()
			cfg.parallelArrayDict = {}
			# band set
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				try:
					imageName = cfg.bandSetsList[bandSetNumber][3][0]
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msgWar25(bandSetNumber + 1)
					if progressbar == 'Yes':
						cfg.uiUtls.removeProgressBar()
					return 'No'
				# image CRS
				bN0 = cfg.utls.selectLayerbyName(imageName, 'Yes')
				filePath = cfg.utls.layerSource(bN0)
				iCrs = cfg.utls.getCrsGDAL(filePath)
				bList = []
				bandNumberList = []
				functionList = []
				if cfg.rpdROICheck == '0':
					# subset
					for b in range(0, len(cfg.bandSetsList[bandSetNumber][3])):
						oL = cfg.utls.subsetImage(cfg.bandSetsList[bandSetNumber][3][b], point.x(), point.y(), float(cfg.maxROIWdth), float(cfg.maxROIWdth), virtual ='Yes')
						bList.append(oL)
						bandNumberList.append(1)
						functionList.append(b)
				# rapid ROI
				else:
					b = int(cfg.ROIband) - 1
					oL = cfg.utls.subsetImage(cfg.bandSetsList[bandSetNumber][3][b], point.x(), point.y(), float(cfg.maxROIWdth), float(cfg.maxROIWdth), virtual ='Yes')
					bList.append(oL)
					bandNumberList.append(1)
					functionList.append(0)
			# multiband image
			else:
				# image CRS
				bN0 = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
				filePath = cfg.utls.layerSource(bN0)
				iCrs = cfg.utls.getCrsGDAL(filePath)
				tRR = cfg.utls.createTempRasterPath('tif')
				bList = []
				bandNumberList = []
				functionList = []
				if cfg.rpdROICheck == '0':
					# subset image
					oL = cfg.utls.subsetImage(cfg.bandSetsList[bandSetNumber][8], point.x(), point.y(), int(cfg.maxROIWdth), int(cfg.maxROIWdth), tRR, cfg.outTempRastFormat, 'Yes')
					bList = cfg.utls.rasterToBands(tRR, cfg.tmpDir, None, 'No', cfg.bandSetsList[bandSetNumber][6])
					for b in range(0, len(bList)):
						bandNumberList.append(1)
						functionList.append(b)
				# rapid ROI
				else:
					# subset image
					oL = cfg.utls.subsetImage(cfg.bandSetsList[bandSetNumber][8], point.x(), point.y(), int(cfg.maxROIWdth), int(cfg.maxROIWdth), tRR)
					bList = cfg.utls.rasterToBands(tRR, cfg.tmpDir, None, 'No', cfg.bandSetsList[bandSetNumber][6])
					b = int(cfg.ROIband) - 1
					bList = [bList[b]]
					bandNumberList.append(1)
					functionList.append(0)
			# open input with GDAL
			try:
				rD = cfg.gdalSCP.Open(oL, cfg.gdalSCP.GA_ReadOnly)
				# number of x pixels
				rX = rD.RasterXSize
				# number of y pixels
				rY = rD.RasterYSize
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				if progressbar == 'Yes':
					cfg.uiUtls.removeProgressBar()
				return 'No'
			# pixel size and origin
			rGT = rD.GetGeoTransform()
			UX = abs(rGT[0])
			UY = abs(rGT[3])
			pX =  abs(rGT[1])
			pY = abs(rGT[5])
			# seed pixel number
			sPX = abs(int((abs(point.x()) - UX)/ pX))
			sPY = abs(int((UY - abs(point.y()))/ pY))
			# area
			area = int(cfg.maxROIWdth) * int(cfg.maxROIWdth)
			minimumSize = int(cfg.minROISz)
			if area < minimumSize:
				minimumSize = area
			# array area
			aBArea = (rX * rY) 
			if aBArea < minimumSize:
				minimumSize = aBArea
			# variables for multiprocess
			fVarList = []
			oM = []
			for rb in range(0, len(bList)):
				fVarList.append([sPX, sPY, cfg.rngRad, int(minimumSize)])
				oM.append(None)
			# create virtual raster of subset bands
			tPMD = cfg.utls.createTempRasterPath('vrt')
			vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, 'Yes', 'Yes', 0)
			# region growing
			o = cfg.utls.multiProcessRaster(rasterPath = tPMD, functionBand = 'No', functionRaster = cfg.utls.regionGrowingAlgMultiprocess, outputRasterList = oM, functionBandArgument = functionList, functionVariable = fVarList, progressMessage = 'Region growing', parallel = cfg.parallelRaster, skipSingleBand = 'Yes')
			# run segmentation
			for x in sorted(cfg.parallelArrayDict):
				try:
					for dic in cfg.parallelArrayDict[x]:
						arr = dic[0]
						try:
							r = r * arr.astype(int)
						except:
							r = arr.astype(int)
				except:
					pass
			check = 'Yes'
			if cfg.np.count_nonzero(r) > 0:
				try:
					lR, num_features = cfg.labelSCP(r)
					# value of ROI seed
					rV = lR[sPY, sPX]
					r = (lR == rV).astype(int)
				except:
					r = 0
			else:
				check = 'No'
			if cfg.np.count_nonzero(r) > 0 and r[sPY, sPX] == 1 and check == 'Yes':
				# output ROI
				d = cfg.ogrSCP.GetDriverByName('GPKG')
				# use ogr
				dS = d.CreateDataSource(tS)
				# shapefile
				sR = cfg.osrSCP.SpatialReference()
				sR.ImportFromWkt(rD.GetProjectionRef())
				rL = dS.CreateLayer('ROILayer', sR, cfg.ogrSCP.wkbMultiPolygon)
				fN = 'DN'
				fd = cfg.ogrSCP.FieldDefn(fN, cfg.ogrSCP.OFTInteger)
				rL.CreateField(fd)
				fld = rL.GetLayerDefn().GetFieldIndex(fN)
				# prepare output raster
				tR = cfg.utls.createTempRasterPath('tif')
				iRB = rD.GetRasterBand(1)
				dtTp = iRB.DataType
				tD = cfg.gdalSCP.GetDriverByName('GTiff')
				rR = tD.Create(tR, rX, rY, 1, dtTp)
				rR.SetGeoTransform( [ rGT[0] , rGT[1] , 0 , rGT[3] , 0 , rGT[5] ] )
				rP = rD.GetProjection()
				rR.SetProjection(rP)
				rRB = rR.GetRasterBand(1)
				rRB.SetNoDataValue(0)		
				# write array
				rRB.WriteArray(r)
				# raster to polygon
				cfg.gdalSCP.Polygonize(rRB, rRB.GetMaskBand(), rL, fld)
				# close bands
				rRB = None
				# close rasters
				rR = None
				rD = None
				dS = None
				rL = None
				d = None
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'output segmentation: ' + str(tS))
				tSS = cfg.utls.addVectorLayer(tS)
				# check if segmentation failed
				if tSS is None:
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error: failed ROI creation')
					cfg.pntROI = None
					if progressbar == 'Yes':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr2(SMTP = 'No')
				else:
					# add ROI layer
					if progressbar == 'Yes':
						cfg.uiUtls.updateBar(90)
					# add a feature
					f = cfg.qgisCoreSCP.QgsFeature()
					idf = cfg.utls.getLastFeatureID(tSS)
					q = cfg.utls.getFeaturebyID(tSS, idf)
					# get geometry
					g = q.geometry()
					mL = cfg.qgisCoreSCP.QgsVectorLayer('MultiPolygon?crs=' + str(iCrs), tN, 'memory')
					iCrsQ = cfg.qgisCoreSCP.QgsCoordinateReferenceSystem.fromWkt(iCrs)
					mL.setCrs(iCrsQ) 
					pr = mL.dataProvider()
					# create temp ROI
					mL.startEditing()		
					# add fields
					pr.addAttributes( [cfg.qgisCoreSCP.QgsField('ID',  cfg.QVariantSCP.Int)] )
					# add a feature
					if cfg.ctrlClick is not None:
						g = self.addPartToROI(g)
					else:
						cfg.lstROI2 = cfg.lstROI
					f.setGeometry(g)
					f.setAttributes([1])
					pr.addFeatures([f])
					mL.commitChanges()
					mL.updateExtents()	
					# add ROI layer
					cfg.lstROI = mL
					self.addHighlightPolygon(cfg.lstROI, 1)
					# add point marker
					try:
						self.clearROICanvas()
					except:
						self.ROIVrtc = []
					self.vx = cfg.qgisGuiSCP.QgsVertexMarker(cfg.cnvs)
					self.vx.setCenter(cfg.origPoint)
					self.vx.setIconType(1)
					self.vx.setColor(cfg.QtGuiSCP.QColor(0,255,255))
					self.vx.setIconSize(12)
					self.ROIVrtc.append(self.vx)
					if cfg.uidc.auto_calculate_ROI_signature_radioButton.isChecked():
						self.tempROISpectralSignature(bandSetNumber)
					if progressbar == 'Yes':
						cfg.uiUtls.updateBar(100)
					cfg.uidc.button_Save_ROI.setEnabled(True)
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '<<< ROI created: ' + str(tSS.name()))
					# enable Redo button
					cfg.redo_ROI_Button.setEnabled(True)
					if progressbar == 'Yes':
						cfg.uiUtls.removeProgressBar()
			else:
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error: failed ROI creation')
				cfg.pntROI = None
				if progressbar == 'Yes':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr2(SMTP = 'No')
				return 'No'

	# calculate temporary ROI spectral signature
	def tempROISpectralSignature(self, bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		idList = []
		for f in cfg.lstROI .getFeatures():
			idList.append(f.id())
		cfg.utls.calculateSignature(cfg.lstROI, cfg.bandSetsList[bandSetNumber][8], idList, 0, cfg.tmpROINm, 0, cfg.ROITime.strftime('%H-%M-%S'), 0, 50, 'Yes', 'Yes', bandSetNumber = bandSetNumber)
		cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
		