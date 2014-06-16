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
import sys
# for moving files
import shutil
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qgis.utils as qgisUtils
try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s
# for debugging
import inspect
# Initialize Qt resources from file resources.py
import ui.resources_rc
from ui.ui_semiautomaticclassificationplugin import Ui_SemiAutomaticClassificationPlugin
# Import the code for the dialog
from ui.semiautomaticclassificationplugindialog import SemiAutomaticClassificationPluginDialog
# spectral signature plot
from ui.spectralsignaturedialog import SpectralSignatureDialog
# scatter plot
from ui.scatterplotdialog import ScatterPlotDialog
from ui.welcomedialog import WelcomeDialog
from ui.dockdialog import DockDialog
from ui.dockclassdialog import DockClassDialog
# Import plugin version
from __init__ import version as semiautomaticclassVersion
import core.messages as msgs
import core.config as cfg
from core.utils import Utils
from core.signature_importer import Signature_Importer
from roidock.manualroi import ManualROI
from roidock.roidock import RoiDock
from spectralsignature.spectralsignatureplot import SpectralSignaturePlot
from spectralsignature.scatter_plot import Scatter_Plot
from classificationdock.classificationdock import ClassificationDock
from maininterface.multipleroiTab import MultipleROITab
from spectralsignature.usgs_spectral_lib import USGS_Spectral_Lib
from maininterface.landsatTab import LandsatTab
from maininterface.accuracy import Accuracy
from maininterface.bandsetTab import BandsetTab
from maininterface.clipmultiplerasters import ClipMultipleRasters
from maininterface.landcoverchange import LandCoverChange
from maininterface.classreportTab import ClassReportTab
from maininterface.settings import Settings
from core.input import Input
from ui.ui_utils import Ui_Utils

class SemiAutomaticClassificationPlugin:

	def __init__(self, iface):
		# reference to QGIS interface
		cfg.iface = iface
		# reference to map canvas
		cfg.cnvs = iface.mapCanvas()
		# reference to legend
		cfg.lgnd = iface.legendInterface()		
		# create the dialog
		cfg.dlg = SemiAutomaticClassificationPluginDialog()
		# reference to ui
		cfg.ui =cfg.dlg.ui
		# dock dialog
		cfg.dockdlg = DockDialog(cfg.iface.mainWindow(), cfg.iface)
		# reference dock ui
		cfg.uid = cfg.dockdlg.ui
		# class dock dialog
		cfg.dockclassdlg = DockClassDialog(cfg.iface.mainWindow(), cfg.iface)
		# reference dock class ui
		cfg.uidc = cfg.dockclassdlg.ui
		# welcome dialog
		cfg.wlcmdlg = WelcomeDialog()
		# spectral signature plot dialog
		cfg.spectralplotdlg = SpectralSignatureDialog()
		cfg.uisp = cfg.spectralplotdlg.ui
		# scatter plot dialog
		cfg.scatterplotdlg = ScatterPlotDialog()
		cfg.uiscp = cfg.scatterplotdlg.ui
		cfg.mx = msgs.Messages(cfg.iface)
		cfg.utls = Utils()
		cfg.ROId = RoiDock()
		cfg.classD = ClassificationDock()
		cfg.spSigPlot = SpectralSignaturePlot()
		cfg.scaPlT = Scatter_Plot()
		cfg.multiROI = MultipleROITab()
		cfg.usgsLib = USGS_Spectral_Lib()
		cfg.acc = Accuracy()
		cfg.bst = BandsetTab()
		cfg.clipMulti = ClipMultipleRasters()
		cfg.landsatT = LandsatTab()
		cfg.landCC = LandCoverChange()
		cfg.classRep = ClassReportTab()
		cfg.sigImport = Signature_Importer()
		cfg.mnlROI = ManualROI(cfg.cnvs)
		# connect when map is clicked
		cfg.iface.connect(cfg.mnlROI , SIGNAL("leftClicked") , cfg.ROId.clckL)
		cfg.iface.connect(cfg.mnlROI , SIGNAL("rightClicked") , cfg.ROId.clckR)
		cfg.sets = Settings()
		cfg.uiUtls = Ui_Utils()
		cfg.ipt = Input()
		# 32bit or 64bit
		if sys.maxsize > 2**32:
			cfg.sys64bit = "Yes"
		else:
			cfg.sys64bit = "No"
		# file system encoding
		cfg.fSEnc = sys.getfilesystemencoding()
		self.readVariables()
		# initialize plugin directory
		cfg.plgnDir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/SemiAutomaticClassificationPlugin"
		# locale name
		lclNm = QSettings().value("locale/userLocale")[0:2] 
		""" temp names """
		# date for names
		dtTm = cfg.utls.getTime()
		# temp directory
		cfg.tmpDir = unicode(QDir.tempPath() + "/" + cfg.tempDirName)
		if not QDir(cfg.tmpDir).exists():
			os.makedirs(cfg.tmpDir)
		""" registry keys """
		# log setting
		rK = QSettings()
		cfg.logSetVal = rK.value(cfg.regLogKey, cfg.logSetVal)
		cfg.ROIClrVal = rK.value(cfg.regROIClr, cfg.ROIClrVal)
		cfg.ROITrnspVal = int(rK.value(cfg.regROITransp, cfg.ROITrnspVal))
		cfg.algFilesCheck = rK.value(cfg.regAlgFiles, str(cfg.algFilesCheck))
		cfg.RAMValue = int(rK.value(cfg.regRAMValue, str(cfg.RAMValue)))
		cfg.fldID_class = rK.value(cfg.regIDFieldName, cfg.fldID_class)
		cfg.fldMacroID_class = rK.value(cfg.regMacroIDFieldName, cfg.fldMacroID_class)
		cfg.macroclassCheck = rK.value(cfg.regConsiderMacroclass, cfg.macroclassCheck)
		cfg.fldROI_info = rK.value(cfg.regInfoFieldName, cfg.fldROI_info)
		cfg.fldROIMC_info = rK.value(cfg.regMCInfoFieldName, cfg.fldROIMC_info)
		cfg.bndSetNm = rK.value(cfg.regBandSetName, cfg.bndSetNm)
		cfg.roundCharList = rK.value(cfg.regRoundCharList, cfg.roundCharList)
		cfg.grpNm = rK.value(cfg.regGroupName, cfg.grpNm)
		cfg.soundVal = rK.value(cfg.regSound, cfg.soundVal)
		# path to locale
		lclPth = "" 
		if QFileInfo(cfg.plgnDir).exists(): 
			lclPth = cfg.plgnDir + "/i18n/semiautomaticclassificationplugin_" + lclNm + ".qm" 
		if QFileInfo(lclPth).exists(): 
			trnsltr = QTranslator() 
			trnsltr.load(lclPth) 
			if qVersion() > '4.3.3': 
				QCoreApplication.installTranslator(trnsltr)
		""" info """
		# QGIS version
		cfg.QGISVer = QGis.QGIS_VERSION_INT
		# system information
		cfg.sysInfo = str(" SemiAutomaticClass " + semiautomaticclassVersion() + " - QGIS v. " + str(cfg.QGISVer) + " - OS " + str(os.name))
		
	def initGui(self):
		""" toolbar """
		self.toolBar = cfg.iface.addToolBar("SCP Toolbar")
		self.toolBar.setObjectName("SCP Toolbar")
		# main tool
		cfg.main_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/semiautomaticclassificationplugin.png"), u"")
		cfg.main_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.main_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Semi-Automatic Classification Plugin"))
		self.toolBar.addWidget(cfg.main_toolButton)
		cfg.main_toolButton.clicked.connect(self.showPlugin)
		cfg.iface.addDockWidget(Qt.RightDockWidgetArea, cfg.dockdlg)
		cfg.iface.addDockWidget(Qt.LeftDockWidgetArea, cfg.dockclassdlg)
		# add toolbar button and menu item
		cfg.mainAction = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/semiautomaticclassificationplugin.png"), u"Semi-Automatic Classification Plugin", cfg.iface.mainWindow())
		cfg.mainAction.triggered.connect(self.showPlugin)
		cfg.iface.addPluginToRasterMenu(u"&Semi-Automatic Classification Plugin", cfg.mainAction)
		self.lblInput = QLabel(cfg.iface.mainWindow())
		font = QFont()
		font.setFamily(_fromUtf8("FreeSans"))
		font.setBold(True)
		font.setWeight(75)
		# label Input
		self.lblInput.setFont(font)
		self.lblInput.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
		self.lblInput.setObjectName(_fromUtf8("lblInput"))
		self.lblInput.setFixedWidth(90)
		self.lblInput.setMaximumHeight(18)
		self.lblInput.setText(QApplication.translate("SemiAutomaticClassificationPlugin", " Input image", None))
		self.toolBar.addWidget(self.lblInput)
		# combo layer
		cfg.raster_name_combo = QComboBox(cfg.iface.mainWindow())
		cfg.raster_name_combo.setFixedWidth(200)
		raster_name_comboAction = self.toolBar.addWidget(cfg.raster_name_combo)
		cfg.raster_name_combo.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Select an image"))
		cfg.raster_name_combo.currentIndexChanged.connect(cfg.ipt.rasterLayerName)
		# button reload raster
		cfg.toolButton_reload = QPushButton(u"↺")
		cfg.toolButton_reload.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Refresh list"))
		self.toolBar.addWidget(cfg.toolButton_reload)
		cfg.toolButton_reload.clicked.connect(cfg.ipt.checkRefreshRasterLayer)
		# band set button
		cfg.bandset_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_bandset_tool.png"), u"")
		cfg.bandset_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.bandset_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Band set"))
		self.toolBar.addWidget(cfg.bandset_toolButton)
		cfg.bandset_toolButton.clicked.connect(cfg.utls.bandSetTab)
		# spectral signature plot button
		cfg.spectral_plot_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_sign_tool.png"), u"")
		cfg.spectral_plot_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.spectral_plot_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Spectral plot"))
		self.toolBar.addWidget(cfg.spectral_plot_toolButton)
		cfg.spectral_plot_toolButton.clicked.connect(cfg.utls.spectralPlotTab)
		# ROI tools button
		cfg.ROItools_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_roi_tool.png"), u"")
		cfg.ROItools_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.ROItools_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "ROI tools"))
		self.toolBar.addWidget(cfg.ROItools_toolButton)
		cfg.ROItools_toolButton.clicked.connect(cfg.utls.roiToolsTab)
		# Pre processing button
		cfg.preprocessing_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_class_tool.png"), u"")
		cfg.preprocessing_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.preprocessing_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Pre processing"))
		self.toolBar.addWidget(cfg.preprocessing_toolButton)
		cfg.preprocessing_toolButton.clicked.connect(cfg.utls.preProcessingTab)
		# Post processing button
		cfg.postprocessing_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_post_process.png"), u"")
		cfg.postprocessing_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.postprocessing_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Post processing"))
		self.toolBar.addWidget(cfg.postprocessing_toolButton)
		cfg.postprocessing_toolButton.clicked.connect(cfg.utls.postProcessingTab)
		# Settings button
		cfg.settings_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_settings_tool.png"), u"")
		cfg.settings_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.settings_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Settings"))
		self.toolBar.addWidget(cfg.settings_toolButton)
		cfg.settings_toolButton.clicked.connect(cfg.utls.settingsTab)
		# User guide button
		cfg.userguide_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/guide.png"), u"")
		cfg.userguide_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.userguide_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "User guide"))
		self.toolBar.addWidget(cfg.userguide_toolButton)
		cfg.userguide_toolButton.clicked.connect(self.quickGuide)
		# Help button
		cfg.help_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/help.png"), u"")
		cfg.help_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.help_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Online help"))
		self.toolBar.addWidget(cfg.help_toolButton)
		cfg.help_toolButton.clicked.connect(self.askHelp)
		# set plugin version
		cfg.ui.plugin_version_label.setText(semiautomaticclassVersion())
		# ROI list ID column
		cfg.uid.ROI_tableWidget.insertColumn(4)
		cfg.uid.ROI_tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem(cfg.tableColString))
		cfg.uid.ROI_tableWidget.hideColumn(4)
		cfg.utls.sortTableColumn(cfg.uid.ROI_tableWidget, 4)
		cfg.uid.ROI_tableWidget.setColumnWidth(0, 40)
		cfg.uid.ROI_tableWidget.setColumnWidth(2, 40)
		# signature list
		cfg.uidc.signature_list_tableWidget.insertColumn(6)
		cfg.uidc.signature_list_tableWidget.setHorizontalHeaderItem(6, QTableWidgetItem(cfg.tableColString))
		cfg.uidc.signature_list_tableWidget.hideColumn(6)
		cfg.utls.sortTableColumn(cfg.uidc.signature_list_tableWidget, 6)
		cfg.uidc.signature_list_tableWidget.setColumnWidth(0, 30)
		cfg.uidc.signature_list_tableWidget.setColumnWidth(1, 40)
		cfg.uidc.signature_list_tableWidget.setColumnWidth(3, 40)
		cfg.uidc.signature_list_tableWidget.setColumnWidth(5, 30)
		# spectral signature plot list
		cfg.uisp.signature_list_plot_tableWidget.insertColumn(6)
		cfg.uisp.signature_list_plot_tableWidget.setHorizontalHeaderItem(6, QTableWidgetItem(cfg.tableColString))
		cfg.uisp.signature_list_plot_tableWidget.hideColumn(6)
		cfg.utls.sortTableColumn(cfg.uisp.signature_list_plot_tableWidget, 6)
		cfg.uisp.signature_list_plot_tableWidget.setColumnWidth(0, 30)
		cfg.uisp.signature_list_plot_tableWidget.setColumnWidth(1, 40)
		cfg.uisp.signature_list_plot_tableWidget.setColumnWidth(2, 100)
		cfg.uisp.signature_list_plot_tableWidget.setColumnWidth(3, 40)
		cfg.uisp.signature_list_plot_tableWidget.setColumnWidth(4, 100)
		cfg.uisp.signature_list_plot_tableWidget.setColumnWidth(5, 30)
		# scatter plot list
		cfg.uiscp.scatter_list_plot_tableWidget.insertColumn(6)
		cfg.uiscp.scatter_list_plot_tableWidget.setHorizontalHeaderItem(6, QTableWidgetItem(cfg.tableColString))
		cfg.uiscp.scatter_list_plot_tableWidget.hideColumn(6)
		cfg.utls.sortTableColumn(cfg.uiscp.scatter_list_plot_tableWidget, 6)
		cfg.uiscp.scatter_list_plot_tableWidget.setColumnWidth(0, 30)
		cfg.uiscp.scatter_list_plot_tableWidget.setColumnWidth(1, 40)
		cfg.uiscp.scatter_list_plot_tableWidget.setColumnWidth(2, 100)
		cfg.uiscp.scatter_list_plot_tableWidget.setColumnWidth(3, 40)
		cfg.uiscp.scatter_list_plot_tableWidget.setColumnWidth(4, 100)
		cfg.uiscp.scatter_list_plot_tableWidget.setColumnWidth(5, 30)
		# band set list
		cfg.ui.tableWidget.setColumnWidth(0, 220)
		cfg.ui.tableWidget.setColumnWidth(1, 80)
		# USGS spectral lbrary
		cfg.usgsLib.addSpectralLibraryToCombo(cfg.usgs_lib_list)
		cfg.usgs_C1p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/minerals.csv"
		cfg.usgs_C2p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/mixtures.csv"
		cfg.usgs_C3p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/coatings.csv"
		cfg.usgs_C4p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/volatiles.csv"
		cfg.usgs_C5p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/man-made.csv"
		cfg.usgs_C6p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/plants_veg_microorg.csv"
		cfg.bst.addSatelliteToCombo(cfg.satWlList)
		cfg.bst.addUnitToCombo(cfg.unitList)
		cfg.classD.previewSize()
		# set log state
		if cfg.logSetVal == "Yes":
			cfg.ui.log_checkBox.setCheckState(2)
		elif cfg.logSetVal == "No":
			cfg.ui.log_checkBox.setCheckState(0)
		# set alg files state
		if cfg.algFilesCheck == "Yes":
			cfg.ui.alg_files_checkBox.setCheckState(2)
		elif cfg.algFilesCheck == "No":
			cfg.ui.alg_files_checkBox.setCheckState(0)
		# set sound state
		if cfg.soundVal == "Yes":
			cfg.ui.sound_checkBox.setCheckState(2)
		elif cfg.soundVal == "No":
			cfg.ui.sound_checkBox.setCheckState(0)
		# connect to project loaded
		QObject.connect(QgsProject.instance(), SIGNAL("readProject(const QDomDocument &)"), self.projectLoaded)
		QObject.connect(QgsProject.instance(), SIGNAL("projectSaved()"), self.projectSaved)
		cfg.ui.quick_guide_pushButton.clicked.connect(self.quickGuide)
		cfg.ui.help_pushButton.clicked.connect(self.askHelp)
		""" Docks """
		# connect to activate docks button 
		cfg.ui.activate_docks_pushButton.clicked.connect(self.activateDocks)
		# reload layers in combos
		cfg.ipt.refreshRasterLayer()
		cfg.ROId.refreshShapeLayer()
		cfg.clipMulti.refreshShapeClip()
		# set ROI color
		cfg.ui.color_mdiArea.setBackground(QColor(cfg.ROIClrVal))
		# set ROI transparency
		cfg.ui.transparency_Slider.setValue(cfg.ROITrnspVal)
		# set RAM value
		cfg.ui.RAM_spinBox.setValue(cfg.RAMValue)
		# set ID field name line
		cfg.ui.ID_field_name_lineEdit.setText(cfg.fldID_class)
		cfg.ui.MID_field_name_lineEdit.setText(cfg.fldMacroID_class)
		# macroclass checkbox
		if cfg.macroclassCheck == "No":
			cfg.uidc.macroclass_checkBox.setCheckState(0)
		elif cfg.macroclassCheck == "Yes":
			cfg.uidc.macroclass_checkBox.setCheckState(2)
		# set Info field name line
		cfg.ui.Info_field_name_lineEdit.setText(cfg.fldROI_info)
		cfg.ui.MCInfo_field_name_lineEdit.setText(cfg.fldROIMC_info)
		# reload layers in combos
		cfg.acc.refreshClassificationLayer()
		cfg.acc.refreshReferenceLayer()
		cfg.landCC.refreshClassificationReferenceLayer()
		cfg.landCC.refreshNewClassificationLayer()
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# reload rasters in checklist
		cfg.clipMulti.rasterNameList()
		""" ROI tool tab """
		# shape combo
		cfg.uid.shape_name_combo.currentIndexChanged.connect(cfg.ROId.shapeLayerName)
		# button reload shapefile
		cfg.uid.buttonReload_shape.clicked.connect(cfg.ROId.checkRefreshShapeLayer)
		# button new shapefile
		cfg.uid.button_new_shapefile.clicked.connect(cfg.ROId.createShapefile)
		# connect double click ROI list to zoom
		cfg.uid.ROI_tableWidget.doubleClicked.connect(cfg.ROId.zoomToROI)
		cfg.uid.ROI_tableWidget.cellChanged.connect(cfg.ROId.editedCell)
		# connect to activate ROI pointer 
		cfg.uid.pointerButton.clicked.connect(cfg.ROId.pointerROIActive)
		cfg.uid.addToSignature_toolButton.clicked.connect(cfg.ROId.addSelectedROIsToSignatureList)
		cfg.uid.spectralSignature_toolButton.clicked.connect(cfg.ROId.addSelectedROIsToSignaturePlot)
		cfg.uid.scatterPlot_toolButton.clicked.connect(cfg.utls.scatterPlotTab)
		cfg.uid.deleteROI_toolButton.clicked.connect(cfg.ROId.deleteSelectedROIs)
		# connect to activate ROI pointer 
		cfg.uid.polygonROI_Button.clicked.connect(cfg.ROId.pointerManualROIActive)
		# connect to pointerClick when map is clicked
		cfg.clickROI.canvasClicked.connect(cfg.ROId.pointerClickROI)
		# connect to redo ROI 
		cfg.uid.redo_ROI_Button.clicked.connect(cfg.ROId.redoROI)
		# connect to multiple ROI creation
		cfg.uid.mutlipleROI_Button.clicked.connect(cfg.utls.mutlipleROITab)
		# connect to undo save ROI 
		cfg.uid.undo_save_Button.clicked.connect(cfg.ROId.undoSaveROI)
		# connect the Min ROI size spin	
		cfg.uid.Min_region_size_spin.valueChanged.connect(cfg.ROId.minROISize)
		# connect the Max ROI width spin	
		cfg.uid.Max_ROI_width_spin.valueChanged.connect(cfg.ROId.maxROIWidth)
		# connect the Range Radius	
		cfg.uid.Range_radius_spin.valueChanged.connect(cfg.ROId.rangeRadius)
		# connect to save to shapefile 
		cfg.uid.button_Save_ROI.clicked.connect(cfg.ROId.saveROItoShapefile)
		# connect the ROI Class 
		cfg.uid.ROI_Class_line.editingFinished.connect(cfg.ROId.roiClassInfo)
		# connect the ROI Macroclass 
		cfg.uid.ROI_Macroclass_line.editingFinished.connect(cfg.ROId.roiMacroclassInfo)
		# connect the ROI Class ID	
		cfg.uid.ROI_ID_spin.valueChanged.connect(cfg.ROId.setROIID)
		# connect the ROI macroclass ID	
		cfg.uid.ROI_Macroclass_ID_spin.valueChanged.connect(cfg.ROId.setROIMacroID)
		# connect the signature calculation checkBox
		cfg.uid.signature_checkBox.stateChanged.connect(cfg.ROId.signatureCheckbox)
		# connect the rapid ROI checkBox
		cfg.uid.rapid_ROI_checkBox.stateChanged.connect(cfg.ROId.rapidROICheckbox)
		# connect the rapid ROI band
		cfg.uid.rapidROI_band_spinBox.valueChanged.connect(cfg.ROId.rapidROIband)
		""" Multiple ROI tab """
		# connect to add point
		cfg.ui.add_point_pushButton.clicked.connect(cfg.multiROI.addPointToTable)
		# connect to remove point
		cfg.ui.remove_point_pushButton.clicked.connect(cfg.multiROI.removePointFromTable)
		# connect to save point ROIs
		cfg.ui.save_point_rois_pushButton.clicked.connect(cfg.multiROI.createROIfromPoint)
		# connect to import points
		cfg.ui.import_point_list_pushButton.clicked.connect(cfg.multiROI.importPoints)
		# connect to export point list
		cfg.ui.export_point_list_pushButton.clicked.connect(cfg.multiROI.exportPointList)
		# connect the signature calculation checkBox 2
		cfg.ui.signature_checkBox2.stateChanged.connect(cfg.multiROI.signatureCheckbox2)
		""" USGS spectral tab """
		# connect the chapter changed
		cfg.ui.usgs_chapter_comboBox.currentIndexChanged.connect(cfg.usgsLib.chapterChanged)
		# connect the library changed
		cfg.ui.usgs_library_comboBox.currentIndexChanged.connect(cfg.usgsLib.libraryChanged)
		# connect the close library
		cfg.ui.add_usgs_library_pushButton.clicked.connect(cfg.usgsLib.addSignatureToList)
		""" Classification tab """
		# connect to save signature list to file
		cfg.uidc.save_signature_list_toolButton.clicked.connect(cfg.classD.saveSignatureListToFile)
		# connect to open signature list
		cfg.uidc.open_signature_list_toolButton.clicked.connect(cfg.classD.openSignatureList)
		# connect to export signature list file
		cfg.uidc.export_signature_list_toolButton.clicked.connect(cfg.classD.exportSignatureFile)
		# connect to export signature to CSV
		cfg.uidc.export_CSV_library_toolButton.clicked.connect(cfg.classD.exportToCSVLibrary)
		# connect to import signature list file
		cfg.uidc.import_toolButton.clicked.connect(cfg.classD.importSignatureList)
		# connect to import library file
		cfg.uidc.import_library_toolButton.clicked.connect(cfg.classD.openLibraryFile)
		# connect to import USGS library file
		cfg.uidc.import_usgs_library_toolButton.clicked.connect(cfg.utls.importUSGSLibraryTab)
		# add to spectral signature plot
		cfg.uidc.signature_spectral_plot_toolButton.clicked.connect(cfg.classD.addSignatureToSpectralPlot)
		# connect to edited cell
		cfg.uidc.signature_list_tableWidget.cellChanged.connect(cfg.classD.editedCell)
		# connect to signature list double click
		cfg.uidc.signature_list_tableWidget.doubleClicked.connect(cfg.classD.signatureListDoubleClick)
		# connect to delete signature
		cfg.uidc.delete_Signature_Button.clicked.connect(cfg.classD.removeSelectedSignatures)
		# connect to activate preview pointer 
		cfg.uidc.pointerButton_preview.clicked.connect(cfg.classD.pointerPreviewActive)
		# connect to redo preview 
		cfg.uidc.redo_Preview_Button.clicked.connect(cfg.classD.redoPreview)
		# connect the algorithm combo	
		cfg.uidc.algorithm_combo.currentIndexChanged.connect(cfg.classD.algorithmName)
		# connect the algorithm threshold
		cfg.uidc.alg_threshold_SpinBox.valueChanged.connect(cfg.classD.algorithmThreshold)
		# connect the preview size
		cfg.uidc.preview_size_spinBox.valueChanged.connect(cfg.classD.previewSize)
		# connect to run classification
		cfg.uidc.button_classification.clicked.connect(cfg.classD.runClassification)
		# connect the vector output checkBox
		cfg.uidc.vector_output_checkBox.stateChanged.connect(cfg.classD.vectorCheckbox)
		# connect the vector output checkBox
		cfg.uidc.macroclass_checkBox.stateChanged.connect(cfg.classD.macroclassCheckbox)
		# connect the report checkBox
		cfg.uidc.report_checkBox.stateChanged.connect(cfg.classD.reportCheckbox)
		# connect the mask checkBox
		cfg.uidc.mask_checkBox.stateChanged.connect(cfg.classD.maskCheckbox)
		# connect to reset qml button
		cfg.uidc.resetQmlButton.clicked.connect(cfg.classD.resetQmlStyle)
		# connect to reset mask button
		cfg.uidc.resetMaskButton.clicked.connect(cfg.classD.resetMask)
		""" Spectral signature plot """	
		# connect the sigma checkBox
		cfg.uisp.sigma_checkBox.stateChanged.connect(cfg.spSigPlot.sigmaCheckbox)
		# connect to remove signature button
		cfg.uisp.remove_Signature_Button.clicked.connect(cfg.spSigPlot.removeSignature)
		# connect to fit to axes
		cfg.uisp.fitToAxes_pushButton.clicked.connect(cfg.spSigPlot.fitPlotToAxes)
		# connect to edited cell
		cfg.uisp.signature_list_plot_tableWidget.cellChanged.connect(cfg.spSigPlot.editedCell)
		# connect to signature plot list double click
		cfg.uisp.signature_list_plot_tableWidget.doubleClicked.connect(cfg.spSigPlot.signatureListDoubleClick)
		""" Scatter plot tab """
		# connect to scatter plot button 
		cfg.uiscp.scatter_ROI_Button.clicked.connect(cfg.scaPlT.scatterPlot)
		# connect to Band X spinbox
		cfg.uiscp.bandX_spinBox.valueChanged.connect(cfg.scaPlT.bandXPlot)
		# connect to Band Y spinbox
		cfg.uiscp.bandY_spinBox.valueChanged.connect(cfg.scaPlT.bandYPlot)
		# connect double click ROI list to zoom
		cfg.uiscp.scatter_list_plot_tableWidget.doubleClicked.connect(cfg.scaPlT.scatterPlotDoubleClick)
		""" Band set tab """
		# edited cell
		cfg.ui.tableWidget.cellChanged.connect(cfg.bst.editedBandSet)
		# connect to refresh button
		cfg.ui.toolButton_reload_3.clicked.connect(cfg.bst.rasterBandName)
		# connect to add raster band button
		cfg.ui.add_raster_bands_Button.clicked.connect(cfg.bst.addBandToSet)
		# connect to select all bands button
		cfg.ui.select_all_bands_Button.clicked.connect(cfg.bst.selectAllBands)
		# connect to clear band set button
		cfg.ui.clear_bandset_toolButton.clicked.connect(cfg.bst.clearBandSet)
		# connect to move up band button
		cfg.ui.move_up_toolButton.clicked.connect(cfg.bst.moveUpBand)
		# connect to move down band button
		cfg.ui.move_down_toolButton.clicked.connect(cfg.bst.moveDownBand)
		# connect to remove band button
		cfg.ui.remove_toolButton.clicked.connect(cfg.bst.removeBand)
		# connect to import band set button
		cfg.ui.import_bandset_toolButton.clicked.connect(cfg.bst.importBandSet)
		# connect to export band set button
		cfg.ui.export_bandset_toolButton.clicked.connect(cfg.bst.exportBandSet)
		# connect to satellite wavelength combo
		cfg.ui.wavelength_sat_combo.currentIndexChanged.connect(cfg.bst.setSatelliteWavelength)
		# connect to unit combo
		cfg.ui.unit_combo.currentIndexChanged.connect(cfg.bst.setBandUnit)
		""" Pre processing tab """
		""" Clip multiple rasters """
		# connect to clip button
		cfg.ui.clip_Button.clicked.connect(cfg.clipMulti.clipRasters)
		# connect to refresh rasters button
		cfg.ui.toolButton_reload_7.clicked.connect(cfg.clipMulti.rasterNameList)
		# connect to select all rasters button
		cfg.ui.select_all_rasters_Button_2.clicked.connect(cfg.clipMulti.selectAllRasters)
		# connect to activate UL pointer 
		cfg.ui.selectUL_toolButton.clicked.connect(cfg.clipMulti.pointerULActive)
		# connect to activate LR pointer 
		cfg.ui.selectLR_toolButton.clicked.connect(cfg.clipMulti.pointerLRActive)
		# connect to refresh shape button
		cfg.ui.toolButton_reload_8.clicked.connect(cfg.clipMulti.refreshShapeClip)		
		""" Landsat tab """
		# connect to refresh button
		cfg.ui.toolButton_directoryInput.clicked.connect(cfg.landsatT.inputLandsat)
		cfg.ui.toolButton_directoryOutput.clicked.connect(cfg.landsatT.outputLandsat)
		cfg.ui.pushButton_Conversion.clicked.connect(cfg.landsatT.performLandsatCorrection)
		""" Post processing tab """
		""" accuracy tab """
		# connect the classification combo
		cfg.ui.classification_name_combo.currentIndexChanged.connect(cfg.acc.classificationLayerName)
		# connect to refresh button
		cfg.ui.toolButton_reload_4.clicked.connect(cfg.acc.refreshClassificationLayer)
		# connect the reference combo
		cfg.ui.reference_name_combo.currentIndexChanged.connect(cfg.acc.referenceLayerName)
		# connect to refresh button
		cfg.ui.buttonReload_shape_4.clicked.connect(cfg.acc.refreshReferenceLayer)
		# connect to calculate error matrix button
		cfg.ui.calculateMatrix_toolButton.clicked.connect(cfg.acc.calculateErrorMatrix)
		""" Land cover change """
		# connect to refresh button reference classification
		cfg.ui.toolButton_reload_5.clicked.connect(cfg.landCC.refreshClassificationReferenceLayer)
		# connect to refresh button new classification
		cfg.ui.toolButton_reload_6.clicked.connect(cfg.landCC.refreshNewClassificationLayer)
		# connect the classification reference combo
		cfg.ui.classification_reference_name_combo.currentIndexChanged.connect(cfg.landCC.classificationReferenceLayerName)
		# connect the new classification combo
		cfg.ui.new_classification_name_combo.currentIndexChanged.connect(cfg.landCC.newClassificationLayerName)
		# connect the mask unchanged checkBox
		cfg.ui.mask_unchanged_checkBox.stateChanged.connect(cfg.landCC.maskUnchangedCheckbox)
		# connect to calculate land cover change button
		cfg.ui.calculateLandCoverChange_toolButton.clicked.connect(cfg.landCC.landCoverChange)
		""" Classification report """
		# connect to refresh button
		cfg.ui.toolButton_reload_10.clicked.connect(cfg.acc.refreshClassificationLayer)
		# connect to calculate button
		cfg.ui.calculateReport_toolButton.clicked.connect(cfg.classRep.calculateClassReport)
		# connect to calculate button
		cfg.ui.saveReport_toolButton.clicked.connect(cfg.classRep.saveReport)
		""" Settings tab """
		# connect the ID field name line
		cfg.ui.ID_field_name_lineEdit.textChanged.connect(cfg.sets.IDFieldNameChange)
		# connect the macroclass ID field name line
		cfg.ui.MID_field_name_lineEdit.textChanged.connect(cfg.sets.MacroIDFieldNameChange)
		# connect the macroclass Info field name line
		cfg.ui.MCInfo_field_name_lineEdit.textChanged.connect(cfg.sets.MacroInfoFieldNameChange)
		# connect the Info field name line
		cfg.ui.Info_field_name_lineEdit.textChanged.connect(cfg.sets.InfoFieldNameChange)
		# connect to reset field names button
		cfg.ui.reset_field_names_Button.clicked.connect(cfg.sets.resetFieldNames)
		# connect the log file checkBox
		cfg.ui.log_checkBox.stateChanged.connect(cfg.sets.logCheckbox)
		# connect the sound checkBox
		cfg.ui.sound_checkBox.stateChanged.connect(cfg.sets.soundCheckbox)
		# connect the alg files checkBox
		cfg.ui.alg_files_checkBox.stateChanged.connect(cfg.sets.algFilesCheckbox)
		# connect to clear log button
		cfg.ui.clearLog_Button.clicked.connect(cfg.utls.clearLogFile)
		# connect to export log button
		cfg.ui.exportLog_Button.clicked.connect(cfg.sets.copyLogFile)
		# connect to RAM spinbox
		cfg.ui.RAM_spinBox.valueChanged.connect(cfg.sets.RAMSettingChange)
		# connect to plot spinbox
		cfg.ui.plot_text_spinBox.valueChanged.connect(cfg.sets.setPlotLegendLenght)
		# connect to qml button
		cfg.uidc.qml_Button.clicked.connect(cfg.classD.selectQmlStyle)
		# connect to change color button
		cfg.ui.change_color_Button.clicked.connect(cfg.sets.changeROIColor)
		# connect to change color button
		cfg.ui.reset_color_Button.clicked.connect(cfg.sets.resetROIStyle)
		# connect to transparency slider
		cfg.ui.transparency_Slider.valueChanged.connect(cfg.sets.changeROITransparency)
		# welcome message
		if os.path.isfile(cfg.plgnDir + "/firstrun"):
			cfg.wlcmdlg.show()
			os.remove(cfg.plgnDir + "/firstrun")
		
	# save signature list when saving project
	def projectSaved(self):
		if len(cfg.signIDs) > 0:
			cfg.classD.saveSignatureListToFile()
		
	# read project variables
	def projectLoaded(self):
		# clear band set
		tW = cfg.ui.tableWidget
		cfg.utls.clearTable(tW)
		cfg.raster_name_combo.blockSignals(True)
		cfg.rasterComboEdited = "No"
		# read variables
		self.readVariables()
		# reload layers in combos
		cfg.ipt.refreshRasterLayer()
		cfg.uid.ROI_tableWidget
		cfg.uid.ROI_tableWidget.blockSignals(True)
		cfg.ROId.refreshShapeLayer()
		cfg.uid.ROI_tableWidget.blockSignals(False)
		cfg.clipMulti.refreshShapeClip()
		# set ROI color
		cfg.ui.color_mdiArea.setBackground(QColor(cfg.ROIClrVal))
		# set ROI transparency
		cfg.ui.transparency_Slider.setValue(cfg.ROITrnspVal)
		# set RAM value
		cfg.ui.RAM_spinBox.setValue(cfg.RAMValue)
		# rapid ROI band
		cfg.uid.rapidROI_band_spinBox.setValue(int(cfg.ROIband))
		# max ROI size
		cfg.uid.Min_region_size_spin.setValue(int(cfg.minROISz))
		# max ROI width
		cfg.uid.Max_ROI_width_spin.setValue(int(cfg.maxROIWdth))
		# range radius
		cfg.uid.Range_radius_spin.setValue(float(cfg.rngRad))
		# ROI ID field
		cfg.uid.ROI_ID_spin.setValue(float(cfg.ROIID))
		# ROI macro ID field
		cfg.uid.ROI_Macroclass_ID_spin.setValue(float(cfg.ROIMacroID))
		# ROI info
		cfg.uid.ROI_Class_line.setText(cfg.ROIInfo)
		cfg.uid.ROI_Macroclass_line.setText(cfg.ROIMacroClassInfo)
		# ROI completer
		cfg.ROId.roiInfoCompleter()
		cfg.ROId.roiMacroclassInfoCompleter()
		# set signature calculation checkbox state
		if cfg.rpdROICheck == "Yes":
			cfg.uid.rapid_ROI_checkBox.setCheckState(2)
		elif cfg.rpdROICheck == "No":
			cfg.uid.rapid_ROI_checkBox.setCheckState(0)
		# set signature calculation checkbox state
		if cfg.sigClcCheck == "Yes":
			cfg.uid.signature_checkBox.setCheckState(2)
			cfg.ui.signature_checkBox2.setCheckState(2)
		elif cfg.sigClcCheck == "No":
			cfg.uid.signature_checkBox.setCheckState(0)
			cfg.ui.signature_checkBox2.setCheckState(0)
		# set ID field name line
		cfg.ui.ID_field_name_lineEdit.setText(cfg.fldID_class)
		cfg.ui.MID_field_name_lineEdit.setText(cfg.fldMacroID_class)
		# set Info field name line
		cfg.ui.Info_field_name_lineEdit.setText(cfg.fldROI_info)
		cfg.ui.MCInfo_field_name_lineEdit.setText(cfg.fldROIMC_info)
		# reload layers in combos
		cfg.acc.refreshClassificationLayer()
		cfg.acc.refreshReferenceLayer()
		cfg.landCC.refreshClassificationReferenceLayer()
		cfg.landCC.refreshNewClassificationLayer()
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# reload rasters in checklist
		cfg.clipMulti.rasterNameList()
		if cfg.bndSetPresent == "No":
			# get wavelength
			bSW = cfg.utls.readProjectVariable("bndSetWvLn", "")
			# get unit
			un = cfg.utls.readProjectVariable("bndSetUnit", cfg.noUnit)
			bSU = cfg.bst.unitNameConversion(un, "Yes")
			# raster name
			cfg.rasterName = cfg.utls.readProjectVariable("rasterName", "")
			# load project image name in combo
			id = cfg.raster_name_combo.findText(cfg.rasterName)
			cfg.raster_name_combo.setCurrentIndex(id)
			try:
				# set wavelength
				wlg = eval(bSW)
				t = cfg.ui.tableWidget
				cfg.BandTabEdited = "No"
				t.blockSignals(True)
				it = 0
				for x in sorted(wlg):
					b = wlg.index(x)
					# add item to table
					t.item(it, 1).setText(str(wlg[b]))
					it = it + 1
				# load project unit in combo
				idU = cfg.ui.unit_combo.findText(bSU)
				cfg.ui.unit_combo.setCurrentIndex(idU)
				t.blockSignals(False)
			except Exception, err:
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.bst.readBandSet("No")
			cfg.BandTabEdited = "Yes"
		cfg.rasterComboEdited = "Yes"
		cfg.raster_name_combo.blockSignals(False)
		# signature table
		cfg.utls.clearTable(cfg.uidc.signature_list_tableWidget)
		cfg.signList = {}
		cfg.signIDs = {}
		signPath = cfg.utls.readProjectVariable("signatureFilePath", "")
		cfg.uidc.signatureFile_lineEdit.setText(unicode(signPath))
		if len(signPath) > 0:
			cfg.classD.openSignatureListFile(signPath)
		
	# read variables from project instance
	def readVariables(self):
		# read qml path from project instance	
		cfg.qmlFl = cfg.utls.readProjectVariable("qmlfile", "")
		# set qml line content
		cfg.uidc.qml_lineEdit.setText(cfg.qmlFl)
		# read signature checkbox from project instance
		cfg.sigClcCheck = cfg.utls.readProjectVariable("calculateSignature", "Yes")
		# read rapid ROI checkbox from project instance
		cfg.rpdROICheck = cfg.utls.readProjectVariable("rapidROI", "No")
		cfg.ROIband = cfg.utls.readProjectVariable("rapidROIBand", str(cfg.ROIband))
		cfg.minROISz = cfg.utls.readProjectVariable("minROISize", str(cfg.minROISz))
		cfg.maxROIWdth = cfg.utls.readProjectVariable("maxROIWidth", str(cfg.maxROIWdth))
		cfg.rngRad = cfg.utls.readProjectVariable("rangeRadius", str(cfg.rngRad))
		cfg.ROIID = cfg.utls.readProjectVariable("ROIIDField", str(cfg.ROIID))
		cfg.ROIInfo = cfg.utls.readProjectVariable("ROIInfoField", str(cfg.ROIInfo))
		cfg.ROIMacroClassInfo = cfg.utls.readProjectVariable("ROIMacroclassInfoField", str(cfg.ROIMacroClassInfo))
		cfg.ROIMacroID = cfg.utls.readProjectVariable("ROIMacroIDField", str(cfg.ROIMacroID))
		# mask option
		cfg.mskFlPath = cfg.utls.readProjectVariable("maskFilePath", unicode(cfg.mskFlPath))
		cfg.mskFlState = cfg.utls.readProjectVariable("maskFileState", str(cfg.mskFlState))
		cfg.uidc.mask_lineEdit.setText(unicode(cfg.mskFlPath))
		cfg.classD.setMaskCheckbox()
		# band set
		bSP = cfg.utls.readProjectVariable("bandSet", "")
		bSW = cfg.utls.readProjectVariable("bndSetWvLn", "")
		un = cfg.utls.readProjectVariable("bndSetUnit", cfg.noUnit)
		bSU = cfg.bst.unitNameConversion(un, "Yes")
		cfg.bndSetPresent = cfg.utls.readProjectVariable("bandSetPresent", "No")
		if cfg.bndSetPresent == "Yes":
			# add band set to table
			bs = eval(bSP)
			wlg = eval(bSW)
			t = cfg.ui.tableWidget
			it = 0
			cfg.BandTabEdited = "No"
			t.blockSignals(True)
			for x in sorted(wlg):
				b = wlg.index(x)
				# add item to table
				c = t.rowCount()
				# name of item of list
				iN = bs[it]
				# add list items to table
				t.setRowCount(c + 1)
				i = QTableWidgetItem(str(c + 1))
				i.setFlags(Qt.ItemIsEnabled)
				i.setText(iN)
				t.setItem(c, 0, i)
				w = QTableWidgetItem(str(c + 1))
				w.setText(str(wlg[b]))
				t.setItem(c, 1, w)
				it = it + 1
			# load project unit in combo
			idU = cfg.ui.unit_combo.findText(bSU)
			cfg.ui.unit_combo.setCurrentIndex(idU)
			t.blockSignals(False)
			cfg.bst.readBandSet("Yes")
			cfg.BandTabEdited = "Yes"
				
	# run
	def run(self):
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "OPEN SESSION" + cfg.sysInfo)
		# show the dialog
		cfg.dlg.show()
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# reload rasters in checklist
		cfg.clipMulti.rasterNameList()
		# Run the dialog event loop
		pointer_result = cfg.dlg.exec_()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "CLOSE SESSION")
		
	def showPlugin(self):
		# show the dialog
		cfg.dlg.show()
		self.activateDocks()
		
	def activateDocks(self):
		cfg.dockdlg.show()
		cfg.dockclassdlg.show()
		
	def askHelp(self):
		QDesktopServices().openUrl(QUrl("http://fromgistors.blogspot.com/p/ask-for-help.html?spref=scp"))
		
	def quickGuide(self):
		qgisUtils.showPluginHelp(None, "quickGuide/index")
		
	# remove plugin menu and icon	
	def unload(self):
		cfg.iface.removePluginMenu(u"&Semi-Automatic Classification Plugin", cfg.mainAction)
		cfg.iface.removeToolBarIcon(cfg.mainAction)
        # remove temp files
		if cfg.tmpDir is not None and QDir(cfg.tmpDir).exists():
			shutil.rmtree(cfg.tmpDir, True)
		if not QDir(cfg.tmpDir).exists():
			os.makedirs(cfg.tmpDir)
			