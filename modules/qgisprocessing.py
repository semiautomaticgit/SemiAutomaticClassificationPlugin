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

class qgisprocessing:

	def __init__(self):
		pass
				
	# load service
	def loading(self):
		cfg.pluginPathProcessing = cfg.qgisCoreSCP.QgsApplication.pkgDataPath() + '/python/plugins'
		cfg.prefixPathProcessing = cfg.qgisCoreSCP.QgsApplication.prefixPath()
		# replace funtions
		cfg.functionNames.append([['QGIS Processing']])
		cfg.functionNames.append([['qgis_processing', 'cfg.qgisprocessing.performProcessingAlg',  'cfg.qgisprocessing.runProcessingAlg',['command : \'\'', 'parameters : \'\'', 'load_results : 1']]])
		

	# run algorithm
	def runProcessingAlg(self, command, parameters, loadResults = 'Yes'):
		if ' {' not in parameters:
			parameters = ' {' + parameters + '}'
		parameters = eval(parameters)
		cfg.uiUtls.updateBar(10, command)
		# pool
		cfg.pool = cfg.poolSCP(processes=1)
		p = 0
		results = []
		c = cfg.pool.apply_async(self.processingThread, args=(cfg.pluginPathProcessing, cfg.prefixPathProcessing, command, parameters))
		results.append([c, p])
		cfg.QtWidgetsSCP.qApp.processEvents()
		while cfg.actionCheck == 'Yes':
			pR = []
			for r in results:
				pR.append(r[0].ready())
			if all(pR):
				break
			cfg.timeSCP.sleep(1)
			try:
				dots = dots + '.'
				if len(dots) > 3:
					dots = ''
			except:
				dots = ''
			cfg.uiUtls.updateBar('', command + dots)
			cfg.QtWidgetsSCP.qApp.processEvents()
		if cfg.actionCheck != 'Yes':
			cfg.mx.msgWar33()	
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'error: cancel ')
			return 'No'
		for r in results:
			if cfg.actionCheck == 'Yes':
				res = r[0].get()
				if len(str(res[1])) > 0:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error proc '+ str(p) + '-' + str(res[1]))
					cfg.mx.msgBarError(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Error'), 'Processing: ' + str(res[1]))
					return 'No'
			else:
				cfg.pool.close()
				cfg.pool.terminate()
				return 'No'
		cfg.pool.close()
		cfg.pool.terminate()
		result = res[0]
		if loadResults == 'Yes':
			outR = result['OUTPUT']
			try:
				r = cfg.utls.addRasterLayer(outR)
			except:
				try:
					vl = cfg.utls.addVectorLayer(outR)
					cfg.utls.addLayerToMap(vl)
				# in case of errors
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		cfg.uiUtls.updateBar(100, command)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' result ' + str(result))
		return result
		
	# processing thread
	def processingThread(self, pluginPath, prefixPath, command, parameters):
		import sys
		from qgis.core import QgsProcessingRegistry
		from qgis.analysis import QgsNativeAlgorithms
		from qgis.core import QgsApplication
		QgsApplication.setPrefixPath(prefixPath, True)
		qgs = QgsApplication([], False)
		qgs.initQgis()
		sys.path.append(pluginPath)
		from processing.core.Processing import Processing
		Processing.initialize()
		QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
		import processing
		try:
			from processing.algs.grass7.Grass7Utils import Grass7Utils
			Grass7Utils.checkGrassIsInstalled()
		except:
			pass
		try:
			result = processing.run(command, parameters)
			return result, ''
		except Exception as err:
			return '', str(err)
		
	# perform algorithm
	def performProcessingAlg(self, paramList):
		parameters = []
		loadResults = '\'Yes\''
		for p in paramList:
			pSplit = p.split(':', 1)
			pName = pSplit[0].lower().replace(' ', '')
			if pName == 'command':
				pSplitX = pSplit[1]
				if len(pSplitX) > 0:
					command = pSplit[1]
				else:
					return 'No', 'command'
			# load results (1 'Yes' or 0 'No')
			elif pName == 'load_results':
				if pSplit[1].replace(' ', '') == '1':
					loadResults = '\'Yes\''
				elif pSplit[1].replace(' ', '') == '0':
					loadResults = '\'No\''
				else:
					return 'No', pName
			elif pName == 'parameters':
				pSplitX = pSplit[1]
				if len(pSplitX) > 0:
					param = pSplitX
					try:
						eval(param)	
					except:
						param = '"' + pSplitX + '"'	
						try:
							eval(param)	
						except:
							param =  '\'' + pSplitX + '\''	
							try:
								eval(param)
							except:
								return 'No', 'parameters'
				else:
					return 'No', 'parameters'
			else:
				if len(pName.strip()) > 0:
					return 'No', pName
		# append parameters
		try:
			parameters.append(command)
			parameters.append(param)
			parameters.append(loadResults)
		except:
			return 'No', 'qgis_processing'
		return 'Yes', parameters
	