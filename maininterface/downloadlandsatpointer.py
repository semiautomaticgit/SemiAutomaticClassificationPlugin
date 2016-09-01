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
import SemiAutomaticClassificationPlugin.core.config as cfg

class DownloadLandsatPointer(QgsMapTool):
	def __init__(self, canvas):
		QgsMapTool.__init__(self, canvas)
		self.cnvs = canvas	
		
	def canvasMoveEvent(self, event):
		point = self.cnvs.getCoordinateTransform().toMapCoordinates(event.pos())
		self.emit(cfg.SIGNALSCP("moved"), point)
		
	def canvasReleaseEvent(self, event):
		pnt = self.cnvs.getCoordinateTransform().toMapCoordinates(event.pos())
		# click
		if(event.button() == cfg.QtSCP.RightButton):
			self.emit(cfg.SIGNALSCP("rightClicked"), pnt)
		else:
			self.emit(cfg.SIGNALSCP("leftClicked"), pnt)
