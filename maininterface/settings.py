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

import os
import shutil
# for debugging
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class Settings:

	def __init__(self):
		pass
		
	# set variable for algorithm files
	def algFilesCheckbox(self):
		if cfg.ui.alg_files_checkBox.isChecked() is True:
			cfg.algFilesCheck = "Yes"
		else:
			cfg.algFilesCheck = "No"
		q = QSettings()		
		q.setValue(cfg.regAlgFiles, cfg.algFilesCheck)
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.algFilesCheck))
		
	# Change ROI color
	def changeROIColor(self):
		c = QColorDialog.getColor()
		if c.isValid():
			clrSttngChng = QSettings()		
			clrSttngChng.setValue(cfg.regROIClr, c.name())
			cfg.ROIClrVal = clrSttngChng.value(cfg.regROIClr, "#ffaa00")
			cfg.ui.color_mdiArea.setBackground(QColor(cfg.ROIClrVal))
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi colour changed to: " + str(cfg.ROIClrVal))

	# ROI transparency
	def changeROITransparency(self):
		cfg.ROITrnspVal = cfg.ui.transparency_Slider.value()
		cfg.ui.transparency_Label.setText(QApplication.translate("semiautomaticclassificationplugin", "Transparency ") + str(cfg.ROITrnspVal) + "%")
		q = QSettings()		
		q.setValue(cfg.regROITransp, cfg.ROITrnspVal)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi transparency changed to: " + str(cfg.ROITrnspVal) + "%")
		
	def copyLogFile(self):
		out = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save Log file"), "", "*.txt")
		if len(out) > 0:
			if os.path.isfile(cfg.logFile):
				try:
					shutil.copy(cfg.logFile, out)
				except Exception, err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.mx.msgErr20()
		
	# field ID name
	def IDFieldNameChange(self):
		cfg.fldID_class = cfg.ui.ID_field_name_lineEdit.text()
		q = QSettings()
		q.setValue(cfg.regIDFieldName, cfg.fldID_class)
		cfg.ROId.refreshShapeLayer()
		cfg.acc.refreshReferenceLayer()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "IDFieldName changed to: " + str(cfg.fldID_class))
		
	# field Macro ID name
	def MacroIDFieldNameChange(self):
		cfg.fldMacroID_class = cfg.ui.MID_field_name_lineEdit.text()
		q = QSettings()
		q.setValue(cfg.regMacroIDFieldName, cfg.fldMacroID_class)
		cfg.ROId.refreshShapeLayer()
		cfg.acc.refreshReferenceLayer()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "macroclassIDFieldName changed to: " + str(cfg.fldMacroID_class))
		
	# macroclass field Info name
	def MacroInfoFieldNameChange(self):
		cfg.fldROIMC_info = cfg.ui.MCInfo_field_name_lineEdit.text()
		q = QSettings()
		q.setValue(cfg.regMCInfoFieldName, cfg.fldROIMC_info)
		cfg.ROId.refreshShapeLayer()
		cfg.acc.refreshReferenceLayer()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Macroclass IDFieldName changed to: " + str(cfg.fldROIMC_info))
		
	# field class Info name
	def InfoFieldNameChange(self):
		cfg.fldROI_info = cfg.ui.Info_field_name_lineEdit.text()
		q = QSettings()
		q.setValue(cfg.regInfoFieldName, cfg.fldROI_info)
		cfg.ROId.refreshShapeLayer()
		cfg.acc.refreshReferenceLayer()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "IDFieldName changed to: " + str(cfg.fldROI_info))
		
	# checkbox switch log
	def logCheckbox(self):
		# log setting
		q = QSettings()
		if cfg.ui.log_checkBox.isChecked() is True:
			q.setValue(cfg.regLogKey, "Yes")
			# logger
			cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "LOG ACTIVE" + cfg.sysInfo)
		elif cfg.ui.log_checkBox.isChecked() is False:
			# logger
			cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "LOG DISABLED")
			q.setValue(cfg.regLogKey, "No")
		cfg.logSetVal = q.value(cfg.regLogKey, "Yes")
		
	# checkbox switch sound
	def soundCheckbox(self):
		# sound setting
		q = QSettings()
		if cfg.ui.sound_checkBox.isChecked() is True:
			q.setValue(cfg.regSound, "Yes")
		elif cfg.ui.sound_checkBox.isChecked() is False:
			q.setValue(cfg.regSound, "No")
		cfg.soundVal = q.value(cfg.regSound, "Yes")
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "sound: " + str(cfg.soundVal))
		
	# RAM setting
	def RAMSettingChange(self):
		cfg.RAMValue = cfg.ui.RAM_spinBox.value()
		q = QSettings()
		q.setValue(cfg.regRAMValue, cfg.RAMValue)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "ram value changed to: " + str(cfg.RAMValue))
		
	# field Info name
	def resetFieldNames(self):
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Reset field names"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset field names?"))
		if a == "Yes":
			cfg.ui.ID_field_name_lineEdit.setText("C_ID")
			cfg.ui.Info_field_name_lineEdit.setText("C_info")
			cfg.ui.MID_field_name_lineEdit.setText("MC_ID")
			cfg.ui.MCInfo_field_name_lineEdit.setText("MC_info")
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "field Info name reset")
		
	# Reset qml style path
	def resetROIStyle(self):
		q = QSettings()
		q.setValue(cfg.regROIClr, "#ffaa00")
		qT = QSettings()
		qT.setValue(cfg.regROITransp, "20")
		cfg.ROITrnspVal = 20
		cfg.ROIClrVal = "#ffaa00"
		cfg.ui.color_mdiArea.setBackground(QColor(cfg.ROIClrVal))
		cfg.ui.transparency_Label.setText(QApplication.translate("semiautomaticclassificationplugin", "Transparency ") + str(cfg.ROITrnspVal) + "%")
		cfg.ui.transparency_Slider.setValue(20)
		cfg.mx.msg1()
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi color reset")
		
	# set plot legend max lenght
	def setPlotLegendLenght(self):
		cfg.roundCharList = cfg.ui.plot_text_spinBox.value()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "plot legend max lenght value changed to: " + str(cfg.roundCharList))
