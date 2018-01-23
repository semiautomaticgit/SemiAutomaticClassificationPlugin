# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2018 by Luca Congedo
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


from qgis.gui import *
cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

class RegionROI(QgsMapTool):

	ROIrightClicked = cfg.pyqtSignalSCP( ['QgsPointXY'] )
	ROIleftClicked = cfg.pyqtSignalSCP( ['QgsPointXY'] )
	moved = cfg.pyqtSignalSCP( ['QgsPointXY'] )

	def __init__(self, canvas):
		QgsMapTool.__init__(self, canvas)
		self.cnvs = canvas	
		
	def canvasMoveEvent(self, event):
		point = self.cnvs.getCoordinateTransform().toMapCoordinates(event.pos())
		self.moved.emit(point)
		
	def canvasReleaseEvent(self, event):
		pnt = self.cnvs.getCoordinateTransform().toMapCoordinates(event.pos())
		# click
		if(event.button() == cfg.QtSCP.RightButton):
			self.ROIrightClicked.emit(pnt)
		else:
			self.ROIleftClicked.emit(pnt)
			
	def keyPressEvent(self, event):
		if event.key()==(cfg.QtSCP.Key_Control):
			cfg.ctrlClick = 1
		elif event.key()==(cfg.QtSCP.Key_Control and cfg.QtSCP.Key_Z):
			#cfg.ctrlClick = 0
			cfg.SCPD.deleteLastROI()
