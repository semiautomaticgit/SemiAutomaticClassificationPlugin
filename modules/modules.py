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
import os
cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

class Modules:

	def __init__(self):
		pass
		
	# load
	def loading(self):
		dirF = os.path.dirname(str(__file__))
		for r, d, f in cfg.osSCP.walk(dirF):
			for x in f:
				if x.endswith('.py') and str(str(__name__).split('.')[1]) not in x:
					xL = 'from .' + x.split('.')[0] +' import ' + x.split('.')[0]
					exec(xL)
					exec('cfg.' + x.split('.')[0] +' = ' + x.split('.')[0] + '()')
					exec('cfg.' + x.split('.')[0] +' .loading()')