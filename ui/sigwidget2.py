# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
 providing a tool for the region growing of image pixels, creating polygon shapefiles intended for
 the collection of training areas (ROIs), and rapidly performing the classification process (or a preview).
							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2015 by Luca Congedo
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
from PyQt4 import QtGui
# Import FigureCanvas
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
# Import Figure
from matplotlib.figure import Figure

class SigCanvas(FigCanvas):
	def __init__(self):
		# Figure
		self.figure = Figure()
		# Add subplot for plot and legend
		self.ax = self.figure.add_axes([0.05, 0.1, 0.75, 0.8])
		# Canvas initialization
		FigCanvas.__init__(self, self.figure)
		# Set empty ticks
		self.ax.set_xticks([])
		self.ax.set_yticks([])

class SigWidget2(QtGui.QWidget):
	def __init__(self, parent = None):
		# Widget initialization
		QtGui.QWidget.__init__(self, parent)
		# Widget canvas
		self.sigCanvas = SigCanvas()
		# Create grid layout
		self.gridLayout = QtGui.QGridLayout()
		# Add widget to grid
		self.gridLayout.addWidget(self.sigCanvas)
		# Add toolbar
		tbar= NavigationToolbar(self.sigCanvas, self.sigCanvas)
		self.gridLayout.addWidget(tbar)
		# Set layout
		self.setLayout(self.gridLayout)