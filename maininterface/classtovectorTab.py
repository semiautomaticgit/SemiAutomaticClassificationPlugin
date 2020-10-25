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

class ClassToVectorTab:

	def __init__(self):
		pass
					
	# convert classification to vector
	def convertClassificationToVectorAction(self):
		self.convertClassificationToVector()
		
	# convert classification to vector
	def convertClassificationToVector(self, batch = 'No', inputRaster = None, outputVector = None, dissolve = None, useCode = None):
		if batch == 'No':
			self.clssfctnNm = str(cfg.ui.classification_vector_name_combo.currentText())
			i = cfg.utls.selectLayerbyName(self.clssfctnNm, 'Yes')
			try:
				classificationPath = cfg.utls.layerSource(i)
			except Exception as err:
				cfg.mx.msg4()
				cfg.utls.refreshClassificationLayer()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
			out = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save vector output'), '', '*.gpkg', 'gpkg')
		else:
			if cfg.osSCP.path.isfile(inputRaster):
				classificationPath = inputRaster
			else:
				return 'No'
			out = outputVector
		if out is not False:
			if out.lower().endswith('.gpkg'):
				pass
			else:
				out = out + '.gpkg'
			if batch == 'No':
				cfg.uiUtls.addProgressBar()
				# disable map canvas render
				cfg.cnvs.setRenderFlag(False)
			cfg.uiUtls.updateBar(10)
			n = cfg.utls.fileName(out)
			cfg.uiUtls.updateBar(20)
			if str(cfg.ui.class_macroclass_comboBox.currentText()) == cfg.fldMacroID_class_def:
				mc = 'Yes'
				sL = cfg.SCPD.createMCIDList()
			else:
				mc = 'No'
				sL = cfg.classTab.getSignatureList()
			if dissolve is None:
				if cfg.ui.dissolve_output_checkBox.isChecked() is True:
					dissolve = 'Yes'
				else:
					dissolve = 'No'
			res = cfg.utls.multiProcessRasterToVector(rasterPath = classificationPath, outputVectorPath = out, dissolveOutput = dissolve)
			cfg.uiUtls.updateBar(80)
			if res != 'No':
				vl = cfg.utls.addVectorLayer(out, cfg.utls.fileName(out), 'ogr')
				if useCode is None or useCode == 'Yes':
					if cfg.ui.use_class_code_checkBox.isChecked() is True or useCode == 'Yes':
						cfg.utls.vectorSymbol(vl, sL, mc)
						# save qml file
						nm = cfg.osSCP.path.splitext(n)[0]
						cfg.utls.saveQmlStyle(vl, cfg.osSCP.path.dirname(out) + '/' + nm + '.qml')
				cfg.uiUtls.updateBar(100)
				cfg.utls.addLayerToMap(vl)
			if batch == 'No':
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.utls.finishSound()
				cfg.utls.sendSMTPMessage(None, str(__name__))
				cfg.uiUtls.removeProgressBar()
