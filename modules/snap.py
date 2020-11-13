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

class snap:

	def __init__(self):
		pass
		
	# load service
	def loading(self):
		# registry
		cfg.regSNAPGPT= "SemiAutomaticClassificationPlugin/SNAPGPT"
		cfg.SNAPGPT = ""
		cfg.SNAPGPT = cfg.utls.readRegistryKeys(cfg.regSNAPGPT, cfg.SNAPGPT)
		# set gpt
		cfg.ui.SNAP_GPT_lineEdit.setText(cfg.SNAPGPT)
		cfg.ui.SNAP_GPT_lineEdit.editingFinished.connect(self.rememberSNAPGPT)

	# root
	def rememberSNAPGPT(self):
		cfg.SNAPGPT = cfg.ui.SNAP_GPT_lineEdit.text()
		if cfg.osSCP.path.isfile(cfg.SNAPGPT):
			cfg.ui.SNAP_GPT_lineEdit.setStyleSheet("color : black")
		else:
			cfg.ui.SNAP_GPT_lineEdit.setStyleSheet("color : red")
		cfg.utls.setQGISRegSetting(cfg.regSNAPGPT, cfg.SNAPGPT)
		
	# root
	def findSNAPGPT(self):
		if cfg.sysSCPNm == "Windows":
			gpt = "C:/snap/bin/gpt.exe"
			if not cfg.osSCP.path.isfile(gpt):
				gpt = "C:/Program Files/snap/bin/gpt.exe"
		else:
			gpt = "/usr/local/snap/bin/gpt"
		if cfg.osSCP.path.isfile(gpt):
			cfg.SNAPGPT = gpt
			cfg.ui.SNAP_GPT_lineEdit.setText(cfg.SNAPGPT)
			cfg.utls.setQGISRegSetting(cfg.regSNAPGPT, cfg.SNAPGPT)
			return 'Yes'
		else:
			cfg.mx.msgWar31()
			return 'No'