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

import os
import numpy as np
# for debugging
import inspect
# for moving files
import shutil
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from osgeo import gdal
from osgeo import ogr 
from osgeo import osr
from osgeo.gdalconst import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class ClassToVectorTab:

	def __init__(self):
		pass
					
	# convert classification to vector
	def convertClassificationToVector(self):
		self.clssfctnNm = str(cfg.ui.classification_vector_name_combo.currentText())
		i = cfg.utls.selectLayerbyName(self.clssfctnNm, "Yes")
		try:
			classificationPath = i.source()
		except Exception, err:
			cfg.mx.msg4()
			cfg.utls.refreshClassificationLayer()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		out = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save shapefile output"), "", "*.shp")
		if len(out) > 0:
			cfg.uiUtls.addProgressBar()
			cfg.uiUtls.updateBar(10)
			n = os.path.basename(out)
			if n.endswith(".shp"):
				out = out
			else:
				out = out + ".shp"
			cfg.uiUtls.updateBar(20)
			if str(cfg.ui.class_macroclass_comboBox.currentText()) == "MC ID":
				mc = "Yes"
			else:
				mc = "No"
			cfg.utls.rasterToVector(classificationPath, out)
			cfg.uiUtls.updateBar(80)
			vl = cfg.utls.addVectorLayer(out, os.path.basename(out), "ogr")
			sL = cfg.classD.getSignatureList()
			if cfg.ui.use_class_code_checkBox.isChecked() is True:
				cfg.utls.vectorSymbol(vl, sL, mc)
				# save qml file
				nm = os.path.splitext(n)[0]
				cfg.utls.saveQmlStyle(vl, os.path.dirname(out) + '/' + nm + ".qml")
			cfg.uiUtls.updateBar(100)
			# disable map canvas render
			cfg.cnvs.setRenderFlag(False)
			cfg.utls.addLayerToMap(vl)
			# enable map canvas render
			cfg.cnvs.setRenderFlag(True)
			cfg.utls.finishSound()
			cfg.uiUtls.removeProgressBar()
		else:
			pass
