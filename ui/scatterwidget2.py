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

# Import PyQt libraries
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
# Import FigureCanvas
import matplotlib
try:
	matplotlib.use("Qt5Agg")
except:
	pass
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanvas
# Import Figure
from matplotlib.figure import Figure

class SigCanvas(FigCanvas):
	def __init__(self):
		# Figure
		self.figure = Figure()
		# Add subplot for plot and legend
		self.ax = self.figure.add_axes([0.1, 0.15, 0.9, 0.9])
		# Canvas initialization
		FigCanvas.__init__(self, self.figure)
		# Set empty ticks
		self.ax.set_xticks([])
		self.ax.set_yticks([])
		self.ax.set_aspect('equal', 'datalim')

class ScatterWidget2(QWidget):
	def __init__(self, parent = None):
		# Widget initialization
		QWidget.__init__(self, parent)
		# Widget canvas
		self.sigCanvas = SigCanvas()
		# Create grid layout
		self.gridLayout = QtWidgets.QGridLayout()
		# Add widget to grid
		self.gridLayout.addWidget(self.sigCanvas)
		# Set layout
		self.setLayout(self.gridLayout)