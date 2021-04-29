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

class ClassRandomForestTab:

	def __init__(self):
		pass
					
	# Select classifier
	def selectRFClassifier(self):
		cfg.classRF = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a classifier'), '', 'class file (*.class);;xml file (*.xml)')
		cfg.ui.classifier_lineEdit_.setText(cfg.classRF)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'classifier file: ' + str(cfg.classRF))
			
	# Reset qml style path
	def resetRFClassifier(self):
		cfg.classRF = ''
		cfg.ui.qml_lineEdit.setText(cfg.classRF)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'reset classifier')
		
	# set variable for macroclass classification
	def macroclassCheckbox(self):
		if cfg.ui.macroclass_checkBox_rf.isChecked() is True:
			cfg.ui.class_checkBox_rf.blockSignals(True)
			cfg.ui.class_checkBox_rf.setCheckState(0)
			cfg.ui.class_checkBox_rf.blockSignals(False)
			cfg.macroclassCheckRF = 'Yes'
		else:
			cfg.ui.class_checkBox_rf.blockSignals(True)
			cfg.ui.class_checkBox_rf.setCheckState(2)
			cfg.ui.class_checkBox_rf.blockSignals(False)
			cfg.macroclassCheckRF = 'No'
							
	# set variable for class classification
	def classCheckbox(self):
		if cfg.ui.class_checkBox_rf.isChecked() is True:
			cfg.ui.macroclass_checkBox_rf.setCheckState(0)
			cfg.macroclassCheckRF = 'No'
		else:
			cfg.ui.macroclass_checkBox_rf.setCheckState(2)
			cfg.macroclassCheckRF = 'Yes'
			
	# create XML graph
	def createXMLRandomForest(self, vectorList):
		importVector =	'''<graph id="Graph">
		<version>1.0</version>
		<node id="Read">
			<operator>Read</operator>
			<sources/>
			<parameters class="com.bc.ceres.binding.dom.XppDomElement">
			  <file>$input</file>
			  <formatName>GeoTIFF</formatName>
			</parameters>
		</node>
		'''
		refID = 'Read'
		b = 0
		if len(vectorList) > 0:
			for b in range(0, len(vectorList)):
				nodeID = 'Import-Vector' + str(b)
				xml = '''
				<node id="%s">
				 <operator>Import-Vector</operator>
				 <sources>
				   <sourceProduct refid="%s"/>
				 </sources>
				 <parameters class="com.bc.ceres.binding.dom.XppDomElement">
				   <vectorFile>%s</vectorFile>
				   <separateShapes>false</separateShapes>
				 </parameters>
				</node>
				'''
				importVector = importVector + xml % (nodeID, refID, vectorList[b])
				refID = 'Import-Vector' + str(b)
			# add random forest
			xml = '''
			<node id="Random-Forest-Classifier">
				<operator>Random-Forest-Classifier</operator>
				<sources>
				  <sourceProduct refid="%s"/>
				</sources>
				<parameters class="com.bc.ceres.binding.dom.XppDomElement">
				  <treeCount>$treeCount</treeCount>
				  <numTrainSamples>$numTrainSamples</numTrainSamples>
				  <savedClassifierName>$classifierName</savedClassifierName>
				  <doLoadClassifier>$loadClassifier</doLoadClassifier>
				  <doClassValQuantization>false</doClassValQuantization>
				  <minClassValue>0.0</minClassValue>
				  <classValStepSize>5.0</classValStepSize>
				  <classLevels>101</classLevels>
				  <trainOnRaster>false</trainOnRaster>
				  <trainingBands/>
				  <trainingVectors>${trainingVectors}</trainingVectors>
				  <featureBands>${featureBands}</featureBands>
				  <labelSource>VectorNodeName</labelSource>
				  <evaluateClassifier>$evaluateClassifier</evaluateClassifier>
				  <evaluateFeaturePowerSet>$evaluateFeaturePowerSet</evaluateFeaturePowerSet>
				  <minPowerSetSize>$minPowerSetSize</minPowerSetSize>
				  <maxPowerSetSize>$maxPowerSetSize</maxPowerSetSize>
				</parameters>
			  </node>
			  <node id="Write">
				<operator>Write</operator>
				<sources>
				  <sourceProduct refid="Random-Forest-Classifier"/>
				</sources>
				<parameters class="com.bc.ceres.binding.dom.XppDomElement">
				  <file>$output</file>
				  <formatName>GeoTIFF-BigTIFF</formatName>
				</parameters>
			  </node>
			  <applicationData id="Presentation">
				<Description/>
				<node id="Read">
						<displayPosition x="10.0" y="160.0"/>
				</node>
				<node id="Random-Forest-Classifier">
				  <displayPosition x="100.0" y="160.0"/>
				</node>
				<node id="Write">
						<displayPosition x="300.0" y="160.0"/>
				</node>
			  </applicationData>
			</graph>
			'''
			importVector = importVector + xml % ('Import-Vector' + str(b))
		else:
			xml = '''
			<node id="Random-Forest-Classifier">
				<operator>Random-Forest-Classifier</operator>
				<sources>
				  <sourceProduct refid="Read"/>
				</sources>
				<parameters class="com.bc.ceres.binding.dom.XppDomElement">
				  <treeCount>$treeCount</treeCount>
				  <numTrainSamples>$numTrainSamples</numTrainSamples>
				  <savedClassifierName>$classifierName</savedClassifierName>
				  <doLoadClassifier>$loadClassifier</doLoadClassifier>
				  <doClassValQuantization>false</doClassValQuantization>
				  <minClassValue>0.0</minClassValue>
				  <classValStepSize>5.0</classValStepSize>
				  <classLevels>101</classLevels>
				  <trainOnRaster>false</trainOnRaster>
				  <trainingBands/>
				  <trainingVectors>false</trainingVectors>
				  <featureBands>${featureBands}</featureBands>
				  <labelSource>VectorNodeName</labelSource>
				  <evaluateClassifier>$evaluateClassifier</evaluateClassifier>
				  <evaluateFeaturePowerSet>$evaluateFeaturePowerSet</evaluateFeaturePowerSet>
				  <minPowerSetSize>$minPowerSetSize</minPowerSetSize>
				  <maxPowerSetSize>$maxPowerSetSize</maxPowerSetSize>
				</parameters>
			  </node>
			  <node id="Write">
				<operator>Write</operator>
				<sources>
				  <sourceProduct refid="Random-Forest-Classifier"/>
				</sources>
				<parameters class="com.bc.ceres.binding.dom.XppDomElement">
				  <file>$output</file>
				  <formatName>GeoTIFF-BigTIFF</formatName>
				</parameters>
			  </node>
			  <applicationData id="Presentation">
				<Description/>
				<node id="Read">
						<displayPosition x="10.0" y="160.0"/>
				</node>
				<node id="Random-Forest-Classifier">
				  <displayPosition x="100.0" y="160.0"/>
				</node>
				<node id="Write">
						<displayPosition x="300.0" y="160.0"/>
				</node>
			  </applicationData>
			</graph>
			'''
			importVector = importVector + xml
		tXml = cfg.utls.createTempRasterPath('xml')
		with open(tXml, 'w') as f:
			f.write(importVector)
		return tXml
					
	# classification output
	def performRandomForest(self):
		bs = cfg.ui.band_set_comb_spinBox_13.value() - 1
		self.randomForestClassification(bandSetNumber = bs, classPath = cfg.classRF)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Perform random forest classification ')
		
	# create  to shapefile from memory layer
	def createShapefileFromTraining(self, mcID = 'Yes'):
		if mcID == 'Yes':
			outList = []
			reclassList = []
			nameSeq = ''
			b = 0
			cfg.SCPD.createMCIDList()
			for mc in cfg.MCID_List:
				v = []
				for id, val in cfg.treeDockItm.items():
					if int(mc[0]) == int(cfg.ROI_MC_ID[id]):
						v.append(id)
				path = cfg.utls.featuresToShapefile(v)
				if path is not None:
					shpName = cfg.utls.fileNameNoExt(path)
					nameSeq = nameSeq + shpName + ','
					outList.append(path)
					reclassList.append([b, int(mc[0])])
					b = b + 1
		else:
			outList = []
			reclassList = []
			nameSeq = ''
			b = 0
			for id, val in cfg.treeDockItm.items():
				v = [id]
				path = cfg.utls.featuresToShapefile(v)
				if path is not None:
					shpName = cfg.utls.fileNameNoExt(path)
					outList.append(path)
					reclassList.append([b, int(val.text(1))])
					nameSeq = nameSeq + shpName + ','
					b = b + 1
		return [outList, nameSeq.rstrip(','), reclassList]
		
	# random forest
	def randomForestClassification(self, batch = 'No', outputFile = None, bandSetNumber = None, numberTrainingSamples = None, treeCount = None, evalClassifier = None, evalFeaturePowerSet = None, minPowerSize = None, maxPowerSize = None, macroclass = None, classPath = '', saveClassifier = None):
		# gpt executable
		if not cfg.osSCP.path.isfile(cfg.SNAPGPT):
			gpt = cfg.snap.findSNAPGPT()
			if gpt == 'No':
				return 'No'
		if saveClassifier is None:
			if cfg.ui.save_classifier_checkBox.isChecked():
				saveClassifier = 'Yes'
			else:
				saveClassifier = 'No'
		if len(classPath) == 0:
			classPath = cfg.classRF
			if len(classPath) == 0:
				if cfg.shpLay is None:
					cfg.mx.msgErr59()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error training')
					return 'No'
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			ckB = cfg.utls.checkBandSet(bandSetNumber)
			if ckB != 'Yes':
				return 'No'
		if outputFile is None:
			rstrOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save classification'), '', '*.tif', 'tif')
			if rstrOut is False:
				return 'No'
		else:
			rstrOut = outputFile
		cfg.utls.makeDirectory(cfg.osSCP.path.dirname(rstrOut))
		# disable map canvas render for speed
		if batch == 'No':
			cfg.cnvs.setRenderFlag(False)
		cfg.uiUtls.addProgressBar()
		# SNAP conversion
		if cfg.actionCheck == 'Yes':
			if macroclass is None:
				macroclass = cfg.macroclassCheckRF
			bandList = []
			featBandList = ''
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				for b in range(0, len(cfg.bandSetsList[bandSetNumber][3])):
					referenceRasterName = cfg.bandSetsList[bandSetNumber][3][b]
					r = cfg.utls.selectLayerbyName(referenceRasterName, 'Yes')
					referenceRasterPath = cfg.utls.layerSource(r)
					bandList.append(referenceRasterPath)
					featBandList = featBandList + 'band_' + str(b+1) + ','
				tR = cfg.utls.createTempRasterPath('tif')
				st = cfg.utls.mergeRasterBands(bandList, tR, compress = 'No')
			else:
				for b in range(0, len(cfg.bandSetsList[bandSetNumber][3])):
					featBandList = featBandList + 'band_' + str(b+1) + ','
				imageName = cfg.bandSetsList[bandSetNumber][8]
				img = cfg.utls.selectLayerbyName(imageName, 'Yes')
				tR = cfg.utls.layerSource(img)
			featBandList = featBandList.rstrip(',')
			# export training to vector
			vectorList, trainingVect, reclassList = self.createShapefileFromTraining(macroclass)
			xmlFile = self.createXMLRandomForest(vectorList)
			if numberTrainingSamples is None:
				numberTrainingSamples = str(int(cfg.ui.number_training_samples_SpinBox.value()))
			if treeCount is None:
				treeCount = str(int(cfg.ui.number_trees_SpinBox.value()))
			if evalClassifier is None:
				if cfg.ui.evaluate_classifier_checkBox.isChecked():
					evalClassifier = 'true'
					if evalFeaturePowerSet is None:
						if cfg.ui.evaluate_feature_power_set_checkBox.isChecked():
							evalFeaturePowerSet = 'true'
						else:
							evalFeaturePowerSet = 'false'
				else:
					evalClassifier = 'false'
					evalFeaturePowerSet = 'false'
			if minPowerSize is None:
				minPowerSize = str(int(cfg.ui.rf_power_min_SpinBox.value()))
			if maxPowerSize is None:
				maxPowerSize = str(int(cfg.ui.rf_power_max_SpinBox.value()))
			# process raster
			cfg.uiUtls.updateBar(0, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Random forest classification'))
			tempOut = cfg.utls.createTempRasterPath('tif')
			outTxt = self.processGPTRandomForest(xmlFile, tR, tempOut, treeCount, numberTrainingSamples, trainingVect, featBandList, evalClassifier, evalFeaturePowerSet, minPowerSize, maxPowerSize, classPath)
			if outTxt == 'No':	
				# logger
				if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' error: cancel')
				if batch == 'No':
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
				return 'No'
			cfg.uiUtls.updateBar(90)
			# split bands
			if cfg.osSCP.path.isfile(tempOut):
				try:
					iL = cfg.utls.rasterToBands(tempOut, cfg.tmpDir)
				except Exception as err:
					cfg.mx.msgErr38(rstrOut)
					# logger
					if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					if batch == 'No':
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					return 'No'
			else:
				cfg.mx.msgErr38(rstrOut)
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error: unable to load raster' + str(rstrOut))
				if batch == 'No':
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.cnvs.setRenderFlag(True)
					cfg.uiUtls.removeProgressBar()
				return 'No'
			# reclassification
			o = cfg.utls.multiProcessRaster(rasterPath = iL[0], functionBand = 'No', functionRaster = cfg.utls.reclassifyRaster, outputRasterList = [rstrOut], nodataValue = cfg.NoDataVal,  functionBandArgument = reclassList, functionVariable = cfg.variableName, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reclassify'), compress = cfg.rasterCompression, dataType = 'UInt16')
			# copy confidence raster
			if cfg.rasterCompression != 'No':
				try:
					cfg.utls.GDALCopyRaster(iL[1], rstrOut.rstrip('.tif') + '_conf.tif', 'GTiff', cfg.rasterCompression, 'LZW')
				except Exception as err:
					# logger
					if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			else:
				cfg.shutilSCP.copy(iL[1], rstrOut.rstrip('.tif') + '_conf.tif')
			if evalClassifier == 'true':
				try:
					cfg.shutilSCP.copy(outTxt, rstrOut.rstrip('.tif') + '_val.txt')
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				try:
					f = open(outTxt)
					eM = f.read()
					cfg.ui.report_textBrowser_5.setText(str(eM))
					cfg.ui.toolBox_random_forest.setCurrentIndex(1)
				except:
					pass
			# remove temp
			try:
				int(0)
				cfg.osSCP.remove(tRxs)
				cfg.osSCP.remove(tR)
				cfg.osSCP.remove(tempOut)
				cfg.osSCP.remove(iL[0])
				cfg.osSCP.remove(iL[1])
			except:
				pass
			if cfg.actionCheck == 'Yes':
				# load raster bands
				v = cfg.utls.addRasterLayer(rstrOut.rstrip('.tif') + '_conf.tif')
				r = cfg.utls.addRasterLayer(rstrOut)
				# apply symbology
				#cfg.utls.rasterSymbolSingleBandGray(v)
				sL = cfg.classTab.getSignatureList(bandSetNumber)
				cfg.classTab.applyClassSymbology(r, macroclass, cfg.qmlFl, sL)
				# save qml file
				cfg.utls.saveQmlStyle(r, rstrOut.rstrip('.tif') + '.qml')
			if saveClassifier == 'Yes':
				try:
					cfg.shutilSCP.copy(outTxt.rstrip('.txt') + '.class', rstrOut.rstrip('.tif') + '.class')
					cfg.shutilSCP.copy(outTxt.rstrip('.txt') + '.xml', rstrOut.rstrip('.tif') + '.xml')
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.uiUtls.updateBar(100)
		if batch == 'No':
			cfg.utls.finishSound()
			cfg.utls.sendSMTPMessage(None, str(__name__))
			cfg.cnvs.setRenderFlag(True)
			cfg.uiUtls.removeProgressBar()

	# process GPT
	def processGPTRandomForest(self, xmlFile, inputRaster, outputRaster, treeCount, numTrainSamples, trainingVectors, featureBands, evaluateClassifier, evaluateFeaturePowerSet, minPowerSetSize, maxPowerSetSize, classifierPath = ''):
		dT = cfg.utls.getTime()
		classifierName = 'scp' + dT
		loadClassifier = 'false'
		if len(classifierPath) > 0:
			loadClassifier = 'true'
			classifierName = cfg.utls.fileNameNoExt(classifierPath)
			cfg.utls.makeDirectory(cfg.tmpDir + '/auxdata/classifiers/RandomForest/')
			xml = cfg.tmpDir + '/auxdata/classifiers/RandomForest/' + classifierName + '.xml'
			cl = cfg.tmpDir + '/auxdata/classifiers/RandomForest/' + classifierName + '.class'
			# copy files
			try:
				cfg.shutilSCP.copy(cfg.osSCP.path.dirname(classifierPath) + '/' + classifierName + '.xml', xml)
				cfg.shutilSCP.copy(cfg.osSCP.path.dirname(classifierPath) + '/' + classifierName + '.class', cl)
			except:
				return 'No'
		d = '"' + cfg.SNAPGPT + '" -q ' + str(cfg.threads) + ' -c ' + str(cfg.RAMValue) + 'M ' + ' -Dsnap.userdir="' + cfg.tmpDir + '" "' + xmlFile + '" -Pinput="' + inputRaster + '" -PtreeCount=' + str(treeCount) + ' -PnumTrainSamples=' + str(numTrainSamples) + ' -PclassifierName="' + str(classifierName) + '" -PloadClassifier=' + str(loadClassifier) + ' -PtrainingVectors="' + str(trainingVectors) + '" -PfeatureBands=' + str(featureBands) + ' -PevaluateClassifier=' + str(evaluateClassifier) + ' -PevaluateFeaturePowerSet=' + str(evaluateFeaturePowerSet) + ' -PminPowerSetSize=' + str(minPowerSetSize) + ' -PmaxPowerSetSize=' + str(maxPowerSetSize) + ' -Poutput="' + outputRaster + '"'
		outTxt = cfg.tmpDir + '/auxdata/classifiers/RandomForest/' + classifierName + '.txt'
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' d: ' + str(d))
		if cfg.sysSCPNm != 'Windows':
			d = cfg.shlexSCP.split(d)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' RF d: ' + str(d))
		tPMD = cfg.utls.createTempRasterPath('txt')
		stF = open(tPMD, 'a')
		sPL = len(cfg.subprocDictProc)
		# issue on Windows
		if cfg.sysSCPNm == 'Windows':
			startupinfo = cfg.subprocessSCP.STARTUPINFO()
			startupinfo.dwFlags = cfg.subprocessSCP.STARTF_USESHOWWINDOW
			startupinfo.wShowWindow = cfg.subprocessSCP.SW_HIDE
			cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(d, shell=False, startupinfo = startupinfo, stdout=stF, stdin = cfg.subprocessSCP.DEVNULL)
		else:
			cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(d, shell=False, stdout=stF)
		progress = 0
		while True:
			line = ''
			with open(tPMD, 'r') as rStF:
				for line in rStF:
					pass
			poll = cfg.subprocDictProc['proc_'+ str(sPL)].poll()
			if poll != None:
				break
			else:
				try:
					progress = int(line.replace('.','').split('%')[-2])
					try:
						dots = dots + '.'
						if len(dots) > 3:
							dots = ''
					except:
						dots = ''
					cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Random forest classification') + dots)
				except:
					try:
						dots = dots + '.'
						if len(dots) > 3:
							dots = ''
					except:
						dots = ''
					cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Random forest classification') + dots)
			cfg.QtWidgetsSCP.qApp.processEvents()
			if cfg.actionCheck != 'Yes':	
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' error: cancel')
				return 'No'
			cfg.timeSCP.sleep(1)
		stF.close()
		# get error
		out, err = cfg.subprocDictProc['proc_'+ str(sPL)].communicate()
		if err is not None:
			if len(err) > 0:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' error: ' + str(err))
				outTxt = 'No'
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' classification: ' + str(outputRaster))
		return outTxt
	