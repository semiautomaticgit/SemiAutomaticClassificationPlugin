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
		copyright			: (C) 2012 by Luca Congedo
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

from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from ui_semiautomaticclassificationplugin_signature_plot import Ui_SpectralSignaturePlot
# create the dialog

class SpectralSignatureDialog(QtGui.QDialog):
	def __init__(self):
		QDockWidget.__init__(self)
		self.setWindowFlags(Qt.Window)
		# initialize plugin directory
		self.plgnDir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/SemiAutomaticClassificationPlugin"
		# locale name
		self.lclNm = QSettings().value("locale/userLocale")[0:2] 
		# path to locale
		lclPth = "" 
		if QFileInfo(self.plgnDir).exists(): 
			lclPth = self.plgnDir + "/i18n/semiautomaticclassificationplugin_" + self.lclNm + ".qm" 
		if QFileInfo(lclPth).exists(): 
			self.trnsltr = QTranslator() 
			self.trnsltr.load(lclPth) 
			if qVersion() > '4.3.3': 
				QCoreApplication.installTranslator(self.trnsltr)
		self.ui = Ui_SpectralSignaturePlot()
		self.ui.setupUi(self)
		

