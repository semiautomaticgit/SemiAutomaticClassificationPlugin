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
import sys
import platform
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
global PluginCheck
PluginCheck = "Yes"
try:
	import core.messages as msgs
	import core.config as cfg
	from core.utils import Utils
	from core.signature_importer import Signature_Importer
	from roidock.manualroi import ManualROI
	from roidock.regionroi import RegionROI
	from roidock.roidock import RoiDock
	from spectralsignature.spectralsignatureplot import SpectralSignaturePlot
	from spectralsignature.scatter_plot import Scatter_Plot
	from classificationdock.classificationdock import ClassificationDock
	from classificationdock.classificationpreview import ClassificationPreview
	from maininterface.multipleroiTab import MultipleROITab
	from spectralsignature.usgs_spectral_lib import USGS_Spectral_Lib
	from maininterface.landsatTab import LandsatTab
	from maininterface.accuracy import Accuracy
	from maininterface.splitTab import SplitTab
	from maininterface.bandsetTab import BandsetTab
	from maininterface.algorithmWeightTab import AlgWeightTab
	from maininterface.signatureThresholdTab import SigThresholdTab
	from maininterface.bandcalcTab import BandCalcTab
	from maininterface.clipmultiplerasters import ClipMultipleRasters
	from maininterface.downloadlandsatimages import DownloadLandsatImages
	from maininterface.landcoverchange import LandCoverChange
	from maininterface.classreportTab import ClassReportTab
	from maininterface.classtovectorTab import ClassToVectorTab
	from maininterface.reclassificationTab import ReclassificationTab
	from maininterface.settings import Settings
	from core.input import Input
	from ui.ui_utils import Ui_Utils
except:
	PluginCheck = "No"
	qgisUtils.iface.messageBar().pushMessage("Semi-Automatic Classification Plugin", QApplication.translate("semiautomaticclassificationplugin", "Please, restart QGIS for executing the Semi-Automatic Classification Plugin"), level=QgsMessageBar.INFO)

class SemiAutomaticClassificationPlugin:

	def __init__(self, iface):
		if PluginCheck == "Yes":
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
			cfg.classPrev = ClassificationPreview(cfg.cnvs)
			cfg.spSigPlot = SpectralSignaturePlot()
			cfg.scaPlT = Scatter_Plot()
			cfg.multiROI = MultipleROITab()
			cfg.usgsLib = USGS_Spectral_Lib()
			cfg.acc = Accuracy()
			cfg.splitT = SplitTab()
			cfg.bst = BandsetTab()
			cfg.algWT = AlgWeightTab()
			cfg.signT = SigThresholdTab()
			cfg.bCalc = BandCalcTab()
			cfg.clipMulti = ClipMultipleRasters()
			cfg.downLandsat = DownloadLandsatImages()
			cfg.landsatT = LandsatTab()
			cfg.landCC = LandCoverChange()
			cfg.classRep = ClassReportTab()
			cfg.classVect = ClassToVectorTab()
			cfg.reclassification = ReclassificationTab()
			cfg.sigImport = Signature_Importer()
			cfg.mnlROI = ManualROI(cfg.cnvs)
			cfg.regionROI = RegionROI(cfg.cnvs)
			# connect when map is clicked
			cfg.iface.connect(cfg.mnlROI , SIGNAL("leftClicked") , cfg.ROId.clckL)
			cfg.iface.connect(cfg.mnlROI , SIGNAL("rightClicked") , cfg.ROId.clckR)
			cfg.iface.connect(cfg.mnlROI , SIGNAL("moved") , cfg.ROId.movedPointer)
			cfg.iface.connect(cfg.regionROI , SIGNAL("ROIleftClicked") , cfg.ROId.pointerClickROI)
			cfg.iface.connect(cfg.regionROI , SIGNAL("ROIrightClicked") , cfg.ROId.pointerRightClickROI)
			cfg.iface.connect(cfg.regionROI , SIGNAL("moved") , cfg.ROId.movedPointer)
			cfg.iface.connect(cfg.classPrev , SIGNAL("leftClicked") , cfg.classD.pointerClickPreview)
			cfg.iface.connect(cfg.classPrev , SIGNAL("rightClicked") , cfg.classD.pointerRightClickPreview)
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
			cfg.outTempRastFormat = rK.value(cfg.regTempRasterFormat, str(cfg.outTempRastFormat))
			cfg.RAMValue = int(rK.value(cfg.regRAMValue, str(cfg.RAMValue)))
			cfg.fldID_class = rK.value(cfg.regIDFieldName, cfg.fldID_class)
			cfg.fldMacroID_class = rK.value(cfg.regMacroIDFieldName, cfg.fldMacroID_class)
			cfg.macroclassCheck = rK.value(cfg.regConsiderMacroclass, cfg.macroclassCheck)
			cfg.fldROI_info = rK.value(cfg.regInfoFieldName, cfg.fldROI_info)
			cfg.fldROIMC_info = rK.value(cfg.regMCInfoFieldName, cfg.fldROIMC_info)
			cfg.variableName = rK.value(cfg.regVariableName, cfg.variableName)
			cfg.bndSetNm = rK.value(cfg.regBandSetName, cfg.bndSetNm)
			cfg.roundCharList = rK.value(cfg.regRoundCharList, cfg.roundCharList)
			cfg.grpNm = rK.value(cfg.regGroupName, cfg.grpNm)
			cfg.rasterDataType = rK.value(cfg.regRasterDataType, cfg.rasterDataType)
			cfg.LandsatDatabaseDirectory = rK.value(cfg.regLandsatDBDir, cfg.LandsatDatabaseDirectory)
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
			cfg.sysNm = platform.system()
			cfg.sysInfo = str(" SemiAutomaticClass " + semiautomaticclassVersion() + " - QGIS v. " + str(cfg.QGISVer) + " - OS " + str(cfg.sysNm) + " - 64bit =" + cfg.sys64bit)
			
	# load SCP menu
	def loadMenu(self):
		cfg.menu = QMenu(cfg.iface.mainWindow())
		cfg.menu.setObjectName('semiautomaticclassificationplugin')
		cfg.menu.setTitle(QApplication.translate("semiautomaticclassificationplugin", "SCP"))
		menuBar = cfg.iface.mainWindow().menuBar()
		menuBar.insertMenu(cfg.iface.firstRightStandardMenu().menuAction(), cfg.menu)
		# main action
		cfg.menu.addAction(cfg.mainAction)
		# Band set
		self.bandset_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_bandset_tool.png"), "Band set", cfg.iface.mainWindow())
		self.bandset_action.setObjectName("bandset_action")
		QObject.connect(self.bandset_action, SIGNAL("triggered()"), cfg.utls.bandSetTab)
		cfg.menu.addAction(self.bandset_action)
		# Spectral plot
		self.spectral_plot_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_sign_tool.png"), "Spectral plot", cfg.iface.mainWindow())
		self.spectral_plot_action.setObjectName("spectral_plot_action")
		QObject.connect(self.spectral_plot_action, SIGNAL("triggered()"), cfg.utls.spectralPlotTab)
		cfg.menu.addAction(self.spectral_plot_action)
		# scatter plot
		self.scatter_plot_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_scatter_tool.png"), "Scatter plot", cfg.iface.mainWindow())
		self.scatter_plot_action.setObjectName("scatter_plot_action")
		QObject.connect(self.scatter_plot_action, SIGNAL("triggered()"), cfg.utls.scatterPlotTab)
		cfg.menu.addAction(self.scatter_plot_action)
		# Tools
		cfg.tools_menu = cfg.menu.addMenu(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_roi_tool.png"), QApplication.translate("semiautomaticclassificationplugin", "Tools"))
		# Multiple ROI creation
		self.multiple_ROI_creation_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_roi_multiple.png"), "Multiple ROI creation", cfg.iface.mainWindow())
		self.multiple_ROI_creation_action.setObjectName("multiple_ROI_creation_action")
		QObject.connect(self.multiple_ROI_creation_action, SIGNAL("triggered()"), cfg.utls.mutlipleROITab)
		cfg.tools_menu.addAction(self.multiple_ROI_creation_action)
		# USGS Spectral Library
		self.USGS_spectral_library_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_import_USGS_spectral_library.png"), "USGS Spectral Library", cfg.iface.mainWindow())
		self.USGS_spectral_library_action.setObjectName("USGS_spectral_library_action")
		QObject.connect(self.USGS_spectral_library_action, SIGNAL("triggered()"), cfg.utls.importUSGSLibraryTab)
		cfg.tools_menu.addAction(self.USGS_spectral_library_action)
		# Algorithm band weight
		self.algorithm_weight_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_weight_tool.png"), "Algorithm band weight", cfg.iface.mainWindow())
		self.algorithm_weight_action.setObjectName("algorithm_weight_action")
		QObject.connect(self.algorithm_weight_action, SIGNAL("triggered()"), cfg.utls.algorithmWeighTab)
		cfg.tools_menu.addAction(self.algorithm_weight_action)
		# Signature threshold
		self.signature_threshold_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_threshold_tool.png"), "Signature threshold", cfg.iface.mainWindow())
		self.signature_threshold_action.setObjectName("signature_threshold_action")
		QObject.connect(self.signature_threshold_action, SIGNAL("triggered()"), cfg.utls.algorithmThresholdTab)
		cfg.tools_menu.addAction(self.signature_threshold_action)
		# Download Landsat
		self.download_landsat8_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_landsat8_download_tool.png"), "Download Landsat", cfg.iface.mainWindow())
		self.download_landsat8_action.setObjectName("download_landsat8_action")
		QObject.connect(self.download_landsat8_action, SIGNAL("triggered()"), cfg.utls.downloadLandast8Tab)
		cfg.tools_menu.addAction(self.download_landsat8_action)
		# Pre processing
		cfg.preprocessing_menu = cfg.menu.addMenu(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_class_tool.png"), QApplication.translate("semiautomaticclassificationplugin", "Pre processing"))
		# Landsat
		self.landsat_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_landsat8_tool.png"), "Landsat", cfg.iface.mainWindow())
		self.landsat_action.setObjectName("landsat_action")
		QObject.connect(self.landsat_action, SIGNAL("triggered()"), cfg.utls.landsatTab)
		cfg.preprocessing_menu.addAction(self.landsat_action)
		# Clip multiple rasters
		self.clip_multiple_rasters_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_clip_tool.png"), "Clip multiple rasters", cfg.iface.mainWindow())
		self.clip_multiple_rasters_action.setObjectName("clip_multiple_rasters_action")
		QObject.connect(self.clip_multiple_rasters_action, SIGNAL("triggered()"), cfg.utls.clipMultipleRastersTab)
		cfg.preprocessing_menu.addAction(self.clip_multiple_rasters_action)
		# Split raster bands
		self.split_raster_bands_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_split_raster.png"), "Split raster bands", cfg.iface.mainWindow())
		self.split_raster_bands_action.setObjectName("split_raster_bands_action")
		QObject.connect(self.split_raster_bands_action, SIGNAL("triggered()"), cfg.utls.splitrasterbandsTab)
		cfg.preprocessing_menu.addAction(self.split_raster_bands_action)
		# Post processing
		cfg.postprocessing_menu = cfg.menu.addMenu(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_post_process.png"), QApplication.translate("semiautomaticclassificationplugin", "Post processing"))
		# Accuracy
		self.accuracy_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_accuracy_tool.png"), "Accuracy", cfg.iface.mainWindow())
		self.accuracy_action.setObjectName("accuracy_action")
		QObject.connect(self.accuracy_action, SIGNAL("triggered()"), cfg.utls.accuracyTab)
		cfg.postprocessing_menu.addAction(self.accuracy_action)
		# Land cover change
		self.land_cover_change_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_land_cover_change.png"), "Land cover change", cfg.iface.mainWindow())
		self.land_cover_change_action.setObjectName("land_cover_change_action")
		QObject.connect(self.land_cover_change_action, SIGNAL("triggered()"), cfg.utls.landCoverChangeTab)
		cfg.postprocessing_menu.addAction(self.land_cover_change_action)
		# Classification report
		self.classification_report_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_report_tool.png"), "Classification report", cfg.iface.mainWindow())
		self.classification_report_action.setObjectName("classification_report_action")
		QObject.connect(self.classification_report_action, SIGNAL("triggered()"), cfg.utls.classificationReportTab)
		cfg.postprocessing_menu.addAction(self.classification_report_action)
		# Classification to vector
		self.class_to_vector_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_class_to_vector_tool.png"), "Classification to vector", cfg.iface.mainWindow())
		self.class_to_vector_action.setObjectName("class_to_vector_action")
		QObject.connect(self.class_to_vector_action, SIGNAL("triggered()"), cfg.utls.classToVectorTab)
		cfg.postprocessing_menu.addAction(self.class_to_vector_action)
		# Reclassification
		self.reclassification_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_reclassification_tool.png"), "Reclassification", cfg.iface.mainWindow())
		self.reclassification_action.setObjectName("reclassification_action")
		QObject.connect(self.reclassification_action, SIGNAL("triggered()"), cfg.utls.reclassificationTab)
		cfg.postprocessing_menu.addAction(self.reclassification_action)
		# Band calc
		self.bandcalc_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_bandcalc_tool.png"), "Band calc", cfg.iface.mainWindow())
		self.bandcalc_action.setObjectName("bandcalc_action")
		QObject.connect(self.bandcalc_action, SIGNAL("triggered()"), cfg.utls.bandCalcTab)
		cfg.menu.addAction(self.bandcalc_action)
		# Settings
		cfg.settings_menu = cfg.menu.addMenu(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_settings_tool.png"), QApplication.translate("semiautomaticclassificationplugin", "Settings"))
		# Settings interface
		self.settings_interface_action = QAction("Interface", cfg.iface.mainWindow())
		self.settings_interface_action.setObjectName("settings_interface_action")
		QObject.connect(self.settings_interface_action, SIGNAL("triggered()"), cfg.utls.settingsInterfaceTab)
		cfg.settings_menu.addAction(self.settings_interface_action)
		# Settings processing
		self.settings_processing_action = QAction("Processing", cfg.iface.mainWindow())
		self.settings_processing_action.setObjectName("settings_processing_action")
		QObject.connect(self.settings_processing_action, SIGNAL("triggered()"), cfg.utls.settingsProcessingTab)
		cfg.settings_menu.addAction(self.settings_processing_action)
		# Settings debug
		self.settings_debug_action = QAction("Debug", cfg.iface.mainWindow())
		self.settings_debug_action.setObjectName("settings_debug_action")
		QObject.connect(self.settings_debug_action, SIGNAL("triggered()"), cfg.utls.settingsDebugTab)
		cfg.settings_menu.addAction(self.settings_debug_action)
		# user guide
		self.userguide_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/guide.png"), "User guide", cfg.iface.mainWindow())
		self.userguide_action.setObjectName("userguide_action")
		QObject.connect(self.userguide_action, SIGNAL("triggered()"), self.quickGuide)
		cfg.menu.addAction(self.userguide_action)
		# help
		self.help_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/help.png"), "Online help", cfg.iface.mainWindow())
		self.help_action.setObjectName("help_action")
		QObject.connect(self.help_action, SIGNAL("triggered()"), self.askHelp)
		cfg.menu.addAction(self.help_action)
		# About
		self.about_action = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/icons/fromGIStoRS.png"), "About", cfg.iface.mainWindow())
		self.about_action.setObjectName("about_action")
		QObject.connect(self.about_action, SIGNAL("triggered()"), cfg.utls.aboutTab)
		cfg.menu.addAction(self.about_action)
			
	def initGui(self):
		if PluginCheck == "Yes":
			""" toolbar """
			cfg.toolBar = cfg.iface.addToolBar("SCP Toolbar")
			cfg.toolBar.setObjectName("SCP Toolbar")
			# main tool
			cfg.main_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/semiautomaticclassificationplugin.png"), u"")
			cfg.main_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.main_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Semi-Automatic Classification Plugin"))
			cfg.toolBar.addWidget(cfg.main_toolButton)
			cfg.main_toolButton.clicked.connect(self.showPlugin)
			cfg.iface.addDockWidget(Qt.RightDockWidgetArea, cfg.dockdlg)
			cfg.iface.addDockWidget(Qt.LeftDockWidgetArea, cfg.dockclassdlg)
			# add toolbar button and menu item
			cfg.mainAction = QAction(QIcon(":/plugins/semiautomaticclassificationplugin/semiautomaticclassificationplugin.png"), u"Semi-Automatic Classification Plugin", cfg.iface.mainWindow())
			cfg.mainAction.triggered.connect(self.showPlugin)
			font = QFont()
			font.setFamily(_fromUtf8("FreeSans"))
			font.setBold(True)
			font.setWeight(75)
			# band set button
			cfg.bandset_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_bandset_tool.png"), u"")
			cfg.bandset_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.bandset_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Band set"))
			cfg.toolBar.addWidget(cfg.bandset_toolButton)
			cfg.bandset_toolButton.clicked.connect(cfg.utls.bandSetTab)
			# label Input
			self.lblInput = QLabel(cfg.iface.mainWindow())
			self.lblInput.setFont(font)
			self.lblInput.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
			self.lblInput.setObjectName(_fromUtf8("lblInput"))
			self.lblInput.setFixedWidth(90)
			self.lblInput.setMaximumHeight(18)
			self.lblInput.setText(QApplication.translate("SemiAutomaticClassificationPlugin", " Input image", None))
			cfg.toolBar.addWidget(self.lblInput)
			# combo layer
			cfg.raster_name_combo = QComboBox(cfg.iface.mainWindow())
			cfg.raster_name_combo.setFixedWidth(200)
			raster_name_comboAction = cfg.toolBar.addWidget(cfg.raster_name_combo)
			cfg.raster_name_combo.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Select an image"))
			cfg.raster_name_combo.currentIndexChanged.connect(cfg.ipt.rasterLayerName)
			# button reload raster
			cfg.toolButton_reload = QPushButton(u"↺")
			cfg.toolButton_reload.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Refresh list"))
			cfg.toolBar.addWidget(cfg.toolButton_reload)
			cfg.toolButton_reload.clicked.connect(cfg.ipt.checkRefreshRasterLayer)
			# label RGB
			self.lblRGB = QLabel(cfg.iface.mainWindow())
			self.lblRGB.setFont(font)
			self.lblRGB.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
			self.lblRGB.setObjectName(_fromUtf8("lblRGB"))
			self.lblRGB.setFixedWidth(50)
			self.lblRGB.setMaximumHeight(18)
			self.lblRGB.setText(QApplication.translate("SemiAutomaticClassificationPlugin", " RGB=", None))
			cfg.toolBar.addWidget(self.lblRGB)
			# combo RGB composite
			cfg.rgb_combo = QComboBox(cfg.iface.mainWindow())
			cfg.rgb_combo.setFixedWidth(70)
			cfg.rgb_combo.setEditable(True)
			#cfg.rgb_combo.lineEdit().setMaxLength(3)
			rgb_comboAction = cfg.toolBar.addWidget(cfg.rgb_combo)
			cfg.rgb_combo.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Select a RGB color composite"))
			cfg.rgb_combo.addItem("-")
			cfg.rgb_combo.addItem("3-2-1")
			cfg.rgb_combo.addItem("4-3-2")
			cfg.rgb_combo.currentIndexChanged.connect(cfg.utls.setRGBColorComposite)	
			# radio button show hide input image
			cfg.inputImageRadio = QtGui.QRadioButton(cfg.iface.mainWindow())
			inputImageRadio_comboAction = cfg.toolBar.addWidget(cfg.inputImageRadio)
			cfg.inputImageRadio.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Show/hide the input image"))
			cfg.inputImageRadio.setText(QApplication.translate("SemiAutomaticClassificationPlugin", " Show", None))
			cfg.inputImageRadio.setChecked(True)
			cfg.inputImageRadio.setAutoExclusive(False)
			cfg.inputImageRadio.clicked.connect(cfg.utls.showHideInputImage)
			# local cumulative cut stretch button
			cfg.local_cumulative_stretch_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_bandset_cumulative_stretch_tool.png"), u"")
			cfg.local_cumulative_stretch_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.local_cumulative_stretch_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Local cumulative cut stretch of band set"))
			cfg.toolBar.addWidget(cfg.local_cumulative_stretch_toolButton)
			cfg.local_cumulative_stretch_toolButton.clicked.connect(cfg.utls.setRasterCumulativeStretch)
			# local standard deviation stretch button
			cfg.local_std_dev_stretch_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_bandset_std_dev_stretch_tool.png"), u"")
			cfg.local_std_dev_stretch_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.local_std_dev_stretch_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Local standard deviation stretch of band set"))
			cfg.toolBar.addWidget(cfg.local_std_dev_stretch_toolButton)
			cfg.local_std_dev_stretch_toolButton.clicked.connect(cfg.utls.setRasterStdDevStretch)
			# spectral signature plot button
			cfg.spectral_plot_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_sign_tool.png"), u"")
			cfg.spectral_plot_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.spectral_plot_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Spectral plot"))
			cfg.toolBar.addWidget(cfg.spectral_plot_toolButton)
			cfg.spectral_plot_toolButton.clicked.connect(cfg.utls.spectralPlotTab)
			# Tools button
			cfg.ROItools_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_roi_tool.png"), u"")
			cfg.ROItools_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.ROItools_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Tools"))
			cfg.toolBar.addWidget(cfg.ROItools_toolButton)
			cfg.ROItools_toolButton.clicked.connect(cfg.utls.roiToolsTab)
			# Pre processing button
			cfg.preprocessing_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_class_tool.png"), u"")
			cfg.preprocessing_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.preprocessing_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Pre processing"))
			cfg.toolBar.addWidget(cfg.preprocessing_toolButton)
			cfg.preprocessing_toolButton.clicked.connect(cfg.utls.preProcessingTab)
			# Post processing button
			cfg.postprocessing_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_post_process.png"), u"")
			cfg.postprocessing_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.postprocessing_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Post processing"))
			cfg.toolBar.addWidget(cfg.postprocessing_toolButton)
			cfg.postprocessing_toolButton.clicked.connect(cfg.utls.postProcessingTab)
			# Band calc button
			cfg.bandcalc_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_bandcalc_tool.png"), u"")
			cfg.bandcalc_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.bandcalc_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Band calc"))
			cfg.toolBar.addWidget(cfg.bandcalc_toolButton)
			cfg.bandcalc_toolButton.clicked.connect(cfg.utls.bandCalcTab)			
			# Settings button
			cfg.settings_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_settings_tool.png"), u"")
			cfg.settings_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.settings_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Settings"))
			cfg.toolBar.addWidget(cfg.settings_toolButton)
			cfg.settings_toolButton.clicked.connect(cfg.utls.settingsTab)
			# User guide button
			cfg.userguide_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/guide.png"), u"")
			cfg.userguide_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.userguide_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "User guide"))
			cfg.toolBar.addWidget(cfg.userguide_toolButton)
			cfg.userguide_toolButton.clicked.connect(self.quickGuide)
			# Help button
			cfg.help_toolButton = QPushButton(QIcon(":/plugins/semiautomaticclassificationplugin/icons/help.png"), u"")
			cfg.help_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
			cfg.help_toolButton.setToolTip(QApplication.translate("semiautomaticclassificationplugin", "Online help"))
			cfg.toolBar.addWidget(cfg.help_toolButton)
			cfg.help_toolButton.clicked.connect(self.askHelp)
			""" menu """
			self.loadMenu()
			# set plugin version
			cfg.ui.plugin_version_label.setText(semiautomaticclassVersion())
			# ROI list ID column
			cfg.uid.ROI_tableWidget.insertColumn(4)
			cfg.uid.ROI_tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem(cfg.tableColString))
			cfg.uid.ROI_tableWidget.hideColumn(4)
			cfg.utls.sortTableColumn(cfg.uid.ROI_tableWidget, 4)
			cfg.uid.ROI_tableWidget.setColumnWidth(0, 40)
			cfg.uid.ROI_tableWidget.setColumnWidth(2, 40)
			try:
				cfg.uid.ROI_tableWidget.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
				cfg.uid.ROI_tableWidget.horizontalHeader().setResizeMode(3, QHeaderView.Stretch)
			except:
				pass
			# signature list
			cfg.uidc.signature_list_tableWidget.insertColumn(6)
			cfg.uidc.signature_list_tableWidget.setHorizontalHeaderItem(6, QTableWidgetItem(cfg.tableColString))
			cfg.uidc.signature_list_tableWidget.hideColumn(6)
			cfg.utls.sortTableColumn(cfg.uidc.signature_list_tableWidget, 6)
			cfg.uidc.signature_list_tableWidget.setColumnWidth(0, 30)
			cfg.uidc.signature_list_tableWidget.setColumnWidth(1, 40)
			cfg.uidc.signature_list_tableWidget.setColumnWidth(3, 40)
			cfg.uidc.signature_list_tableWidget.setColumnWidth(5, 30)
			try:
				cfg.uidc.signature_list_tableWidget.horizontalHeader().setResizeMode(2, QHeaderView.Stretch)
				cfg.uidc.signature_list_tableWidget.horizontalHeader().setResizeMode(4, QHeaderView.Stretch)
			except:
				pass
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
			try:
				cfg.uisp.signature_list_plot_tableWidget.horizontalHeader().setResizeMode(2, QHeaderView.Stretch)
				cfg.uisp.signature_list_plot_tableWidget.horizontalHeader().setResizeMode(4, QHeaderView.Stretch)
			except:
				pass
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
			try:
				cfg.uiscp.scatter_list_plot_tableWidget.horizontalHeader().setResizeMode(2, QHeaderView.Stretch)
				cfg.uiscp.scatter_list_plot_tableWidget.horizontalHeader().setResizeMode(4, QHeaderView.Stretch)
			except:
				pass
			# signature threshold
			cfg.ui.signature_threshold_tableWidget.insertColumn(5)
			cfg.ui.signature_threshold_tableWidget.setHorizontalHeaderItem(5, QTableWidgetItem(cfg.tableColString))
			cfg.ui.signature_threshold_tableWidget.hideColumn(5)
			try:
				cfg.ui.signature_threshold_tableWidget.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
				cfg.ui.signature_threshold_tableWidget.horizontalHeader().setResizeMode(3, QHeaderView.Stretch)
			except:
				pass
			# band set list
			cfg.ui.tableWidget.setColumnWidth(0, 350)
			cfg.ui.tableWidget.setColumnWidth(1, 150)
			cfg.ui.tableWidget.setColumnWidth(2, 150)
			cfg.ui.tableWidget.setColumnWidth(3, 150)
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
				cfg.mx.msg19()
			elif cfg.logSetVal == "No":
				cfg.ui.log_checkBox.setCheckState(0)
			# set alg files state
			if cfg.algFilesCheck == "Yes":
				cfg.ui.alg_files_checkBox.setCheckState(2)
			elif cfg.algFilesCheck == "No":
				cfg.ui.alg_files_checkBox.setCheckState(0)
			# set alg files state
			if cfg.outTempRastFormat == "VRT":
				cfg.ui.virtual_raster_checkBox.setCheckState(2)
			elif cfg.outTempRastFormat == "GTiff":
				cfg.ui.virtual_raster_checkBox.setCheckState(0)
			# set sound state
			if cfg.soundVal == "Yes":
				cfg.ui.sound_checkBox.setCheckState(2)
			elif cfg.soundVal == "No":
				cfg.ui.sound_checkBox.setCheckState(0)
			# connect to project loaded
			QObject.connect(QgsProject.instance(), SIGNAL("readProject(const QDomDocument &)"), self.projectLoaded)
			QObject.connect(QgsProject.instance(), SIGNAL("projectSaved()"), self.projectSaved)
			cfg.iface.newProjectCreated.connect(self.newProjectLoaded)
			cfg.ui.quick_guide_pushButton.clicked.connect(self.quickGuide)
			cfg.ui.help_pushButton.clicked.connect(self.askHelp)
			""" Docks """
			# connect to activate docks button 
			cfg.ui.activate_docks_pushButton.clicked.connect(self.activateDocks)
			# reload layers in combos
			cfg.ipt.refreshRasterLayer()
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
			cfg.ui.variable_name_lineEdit.setText(cfg.variableName)
			cfg.ui.group_name_lineEdit.setText(cfg.grpNm)
			# raster data type
			rDTid = cfg.ui.raster_precision_combo.findText(str(cfg.rasterDataType))
			cfg.ui.raster_precision_combo.setCurrentIndex(rDTid)
			if len(cfg.LandsatDatabaseDirectory) > 0:
				cfg.downLandsat.setDatabaseDir(cfg.LandsatDatabaseDirectory)
			else:
				cfg.downLandsat.setDatabaseDir()
			# reload layers in combos
			cfg.utls.refreshClassificationLayer()
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
			#cfg.clickROI.canvasClicked.connect(cfg.ROId.pointerClickROI)
			# connect to redo ROI 
			cfg.uid.redo_ROI_Button.clicked.connect(cfg.ROId.redoROI)
			# connect to multiple ROI creation
			cfg.uid.mutlipleROI_Button.clicked.connect(cfg.utls.mutlipleROITab)
			# connect to undo save ROI 
			cfg.uid.undo_save_Button.clicked.connect(cfg.ROId.undoSaveROI)
			# connect the vegetation index combo	
			cfg.uid.vegetation_index_comboBox.currentIndexChanged.connect(cfg.ROId.vegetationIndexName)
			# connect the Min ROI size spin	
			cfg.uid.Min_region_size_spin.valueChanged.connect(cfg.ROId.minROISize)
			# connect the Max ROI width spin	
			cfg.uid.Max_ROI_width_spin.valueChanged.connect(cfg.ROId.maxROIWidth)
			# connect the Range Radius	
			cfg.uid.Range_radius_spin.valueChanged.connect(cfg.ROId.rangeRadius)
			# connect to show ROI radio button
			cfg.uid.show_ROI_radioButton.clicked.connect(cfg.ROId.showHideROI)
			# connect to zoom to ROI button
			cfg.uid.zoom_ROI_button.clicked.connect(cfg.ROId.zoomToROI)
			# connect to automatic refresh ROI radio button
			cfg.uid.auto_refresh_ROI_radioButton.clicked.connect(cfg.ROId.automaticRefreshROI)
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
			# connect the rapid ROI checkBox
			cfg.uid.display_cursor_checkBox.stateChanged.connect(cfg.ROId.vegetationIndexCheckbox)
			# connect the vegetation index display checkbox
			cfg.uid.rapidROI_band_spinBox.valueChanged.connect(cfg.ROId.rapidROIband)
			""" Multiple ROI tab """
			# connect to add point
			cfg.ui.add_point_pushButton.clicked.connect(cfg.multiROI.addPointToTable)
			# connect to create random points
			cfg.ui.add_random_point_pushButton.clicked.connect(cfg.multiROI.createRandomPoint)
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
			""" Algorithm weight tab """
			# edited cell
			cfg.ui.tableWidget_weight.cellChanged.connect(cfg.algWT.editedWeightTable)
			cfg.ui.reset_weights_pushButton.clicked.connect(cfg.algWT.resetWeights)
			cfg.ui.set_weight_value_pushButton.clicked.connect(cfg.algWT.setWeights)
			""" Signature threshold tab """
			# edited cell
			cfg.ui.signature_threshold_tableWidget.cellChanged.connect(cfg.signT.editedThresholdTable)
			cfg.ui.reset_threshold_pushButton.clicked.connect(cfg.signT.resetThresholds)
			cfg.ui.automatic_threshold_pushButton.clicked.connect(cfg.signT.setAllWeightsVariance)
			cfg.ui.set_threshold_value_pushButton.clicked.connect(cfg.signT.setThresholds)
			""" Download Landsat tab """
			# connect to find images button
			cfg.ui.find_images_toolButton.clicked.connect(cfg.downLandsat.findImages)
			cfg.ui.selectUL_toolButton_3.clicked.connect(cfg.downLandsat.pointerULActive)
			# connect to activate LR pointer 
			cfg.ui.selectLR_toolButton_3.clicked.connect(cfg.downLandsat.pointerLRActive)
			# connect to display button
			cfg.ui.toolButton_display.clicked.connect(cfg.downLandsat.displayImages)
			cfg.ui.update_image_database_toolButton.clicked.connect(cfg.downLandsat.updateImageDatabase)
			cfg.ui.select_database_dir_toolButton.clicked.connect(cfg.downLandsat.selectDatabaseDir)
			cfg.ui.reset_database_dir_toolButton.clicked.connect(cfg.downLandsat.resetDatabaseDir)
			cfg.ui.remove_image_toolButton.clicked.connect(cfg.downLandsat.removeImageFromTable)
			cfg.ui.clear_table_toolButton.clicked.connect(cfg.downLandsat.clearTable)
			cfg.ui.download_images_Button.clicked.connect(cfg.downLandsat.downloadImages)
			cfg.ui.export_links_Button.clicked.connect(cfg.downLandsat.exportLinks)
			cfg.ui.check_toolButton.clicked.connect(cfg.downLandsat.checkAllBands)
			""" Classification dock """
			# connect to save signature list to file
			cfg.uidc.save_signature_list_toolButton.clicked.connect(cfg.classD.saveSignatureListToFile)
			# connect to save signature list to file
			cfg.uidc.reset_signature_toolButton.clicked.connect(cfg.classD.resetSignatureList)
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
			# connect to merge signatures
			cfg.uidc.merge_signature_toolButton.clicked.connect(cfg.classD.mergeSelectedSignatures)
			# connect to activate preview pointer 
			cfg.uidc.pointerButton_preview.clicked.connect(cfg.classD.pointerPreviewActive)
			# connect to algorithm weight button 
			cfg.uidc.algorithm_weight_button.clicked.connect(cfg.utls.algorithmWeighTab)
			# connect to threshold button 
			cfg.uidc.algorithm_threshold_button.clicked.connect(cfg.utls.algorithmThresholdTab)
			# connect to redo preview 
			cfg.uidc.redo_Preview_Button.clicked.connect(cfg.classD.redoPreview)
			# connect to show preview radio button
			cfg.uidc.show_preview_radioButton.clicked.connect(cfg.classD.showHidePreview)
			# connect to zoom to preview
			cfg.uidc.zoom_preview_button.clicked.connect(cfg.classD.zoomToPreview)
			cfg.uidc.preview_transparency_slider.valueChanged.connect(cfg.classD.changePreviewTransparency)
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
			# connect to sort by name button
			cfg.ui.sort_by_name_toolButton.clicked.connect(cfg.bst.sortBandName)
			# connect to remove band button
			cfg.ui.remove_toolButton.clicked.connect(cfg.bst.removeBand)
			# connect to import band set button
			cfg.ui.import_bandset_toolButton.clicked.connect(cfg.bst.importBandSet)
			# connect to export band set button
			cfg.ui.export_bandset_toolButton.clicked.connect(cfg.bst.exportBandSet)
			# connect to satellite wavelength combo
			cfg.ui.wavelength_sat_combo.currentIndexChanged.connect(cfg.bst.satelliteWavelength)
			# connect to unit combo
			cfg.ui.unit_combo.currentIndexChanged.connect(cfg.bst.setBandUnit)
			# connect to Create virtual raster button
			cfg.ui.virtual_raster_bandset_toolButton.clicked.connect(cfg.bst.virtualRasterBandSet)
			# connect to stack bands button
			cfg.ui.stack_bandset_toolButton.clicked.connect(cfg.bst.stackBandSet)
			# connect to build overviews button
			cfg.ui.band_overview_bandset_toolButton.clicked.connect(cfg.bst.buildOverviewsBandSet)
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
			# connect to input button
			cfg.ui.toolButton_directoryInput.clicked.connect(cfg.landsatT.inputLandsat)
			cfg.ui.toolButton_directoryInput_MTL.clicked.connect(cfg.landsatT.inputMTL)
			cfg.ui.pushButton_Conversion.clicked.connect(cfg.landsatT.performLandsatCorrection)
			cfg.ui.pushButton_remove_band.clicked.connect(cfg.landsatT.removeHighlightedBand)
			cfg.ui.landsat_tableWidget.cellChanged.connect(cfg.landsatT.editedCell)
			cfg.ui.earth_sun_dist_lineEdit.textChanged.connect(cfg.landsatT.editedEarthSunDist)
			cfg.ui.sun_elev_lineEdit.textChanged.connect(cfg.landsatT.editedSunElevation)
			cfg.ui.date_lineEdit.textChanged.connect(cfg.landsatT.editedDate)
			cfg.ui.satellite_lineEdit.textChanged.connect(cfg.landsatT.editedSatellite)
			""" Split tab """
			# connect the classification combo
			cfg.ui.raster_name_combo.currentIndexChanged.connect(cfg.splitT.rasterLayerName)
			# connect to refresh button
			cfg.ui.toolButton_reload_9.clicked.connect(cfg.splitT.refreshClassificationLayer)
			# connect to split raster button
			cfg.ui.split_Button.clicked.connect(cfg.splitT.splitRaster)
			""" Post processing tab """
			""" accuracy tab """
			# connect the classification combo
			cfg.ui.classification_name_combo.currentIndexChanged.connect(cfg.acc.classificationLayerName)
			# connect to refresh button
			cfg.ui.toolButton_reload_4.clicked.connect(cfg.utls.refreshClassificationLayer)
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
			cfg.ui.toolButton_reload_10.clicked.connect(cfg.utls.refreshClassificationLayer)
			# connect to calculate button
			cfg.ui.calculateReport_toolButton.clicked.connect(cfg.classRep.calculateClassReport)
			# connect to calculate button
			cfg.ui.saveReport_toolButton.clicked.connect(cfg.classRep.saveReport)
			""" Classification to vector """
			# connect to refresh button
			cfg.ui.toolButton_reload_12.clicked.connect(cfg.utls.refreshClassificationLayer)
			# connect to convert button
			cfg.ui.convert_toolButton.clicked.connect(cfg.classVect.convertClassificationToVector)
			""" Reclassification """
			# connect to refresh button
			cfg.ui.toolButton_reload_11.clicked.connect(cfg.utls.refreshClassificationLayer)
			# connect to reclassify button
			cfg.ui.reclassify_toolButton.clicked.connect(cfg.reclassification.reclassify)
			# connect to calculate unique values button
			cfg.ui.calculate_unique_values_toolButton.clicked.connect(cfg.reclassification.calculateUniqueValues)
			# connect to add value button
			cfg.ui.add_value_pushButton.clicked.connect(cfg.reclassification.addRowToTable)
			# connect to remove point
			cfg.ui.remove_row_pushButton.clicked.connect(cfg.reclassification.removePointFromTable)
			# connect to edited cell
			cfg.ui.reclass_values_tableWidget.cellChanged.connect(cfg.reclassification.editedCell)
			""" Band Calc tab """
			# connect to refresh button
			cfg.ui.toolButton_reload_13.clicked.connect(cfg.bCalc.rasterBandName)
			# connect to reclassify button
			cfg.ui.toolButton_calculate.clicked.connect(cfg.bCalc.calculate)
			# connect the expression text
			cfg.ui.plainTextEdit_calc.textChanged.connect(cfg.bCalc.textChanged)
			# connect double click table
			cfg.ui.tableWidget_band_calc.doubleClicked.connect(cfg.bCalc.doubleClick)
			# connect the intersection checkBox
			cfg.ui.intersection_checkBox.stateChanged.connect(cfg.bCalc.intersectionCheckbox)
			# connect the extent checkBox
			cfg.ui.extent_checkBox.stateChanged.connect(cfg.bCalc.extentCheckbox)
			# connect to expression buttons
			cfg.ui.toolButton_plus.clicked.connect(cfg.bCalc.buttonPlus)
			cfg.ui.toolButton_minus.clicked.connect(cfg.bCalc.buttonMinus)
			cfg.ui.toolButton_product.clicked.connect(cfg.bCalc.buttonProduct)
			cfg.ui.toolButton_ratio.clicked.connect(cfg.bCalc.buttonRatio)
			cfg.ui.toolButton_power.clicked.connect(cfg.bCalc.buttonPower)
			cfg.ui.toolButton_sqrt.clicked.connect(cfg.bCalc.buttonSQRT)
			cfg.ui.toolButton_lbracket.clicked.connect(cfg.bCalc.buttonLbracket)
			cfg.ui.toolButton_rbracket.clicked.connect(cfg.bCalc.buttonRbracket)
			cfg.ui.toolButton_sin.clicked.connect(cfg.bCalc.buttonSin)
			cfg.ui.toolButton_asin.clicked.connect(cfg.bCalc.buttonASin)
			cfg.ui.toolButton_cos.clicked.connect(cfg.bCalc.buttonCos)
			cfg.ui.toolButton_acos.clicked.connect(cfg.bCalc.buttonACos)
			cfg.ui.toolButton_tan.clicked.connect(cfg.bCalc.buttonTan)
			cfg.ui.toolButton_atan.clicked.connect(cfg.bCalc.buttonATan)
			cfg.ui.toolButton_exponential.clicked.connect(cfg.bCalc.buttonExp)
			cfg.ui.toolButton_npWhere.clicked.connect(cfg.bCalc.buttonNpWhere)
			cfg.ui.toolButton_log.clicked.connect(cfg.bCalc.buttonLog)
			cfg.ui.toolButton_pi.clicked.connect(cfg.bCalc.buttonPi)
			""" Settings tab """
			# connect the ID field name line
			cfg.ui.ID_field_name_lineEdit.textChanged.connect(cfg.sets.IDFieldNameChange)
			# connect the macroclass ID field name line
			cfg.ui.MID_field_name_lineEdit.textChanged.connect(cfg.sets.MacroIDFieldNameChange)
			# connect the macroclass Info field name line
			cfg.ui.MCInfo_field_name_lineEdit.textChanged.connect(cfg.sets.MacroInfoFieldNameChange)
			# connect the Info field name line
			cfg.ui.Info_field_name_lineEdit.textChanged.connect(cfg.sets.InfoFieldNameChange)
			# connect the variable name line
			cfg.ui.variable_name_lineEdit.textChanged.connect(cfg.sets.VariableNameChange)
			# connect the group name line
			cfg.ui.group_name_lineEdit.textChanged.connect(cfg.sets.GroupNameChange)
			# connect to reset field names button
			cfg.ui.reset_field_names_Button.clicked.connect(cfg.sets.resetFieldNames)
			# connect to reset variable name button
			cfg.ui.reset_variable_name_Button.clicked.connect(cfg.sets.resetVariableName)
			# connect to reset group name button
			cfg.ui.reset_group_name_Button.clicked.connect(cfg.sets.resetGroupName)
			# connect the log file checkBox
			cfg.ui.log_checkBox.stateChanged.connect(cfg.sets.logCheckbox)
			# connect the sound checkBox
			cfg.ui.sound_checkBox.stateChanged.connect(cfg.sets.soundCheckbox)
			# connect the alg files checkBox
			cfg.ui.alg_files_checkBox.stateChanged.connect(cfg.sets.algFilesCheckbox)
			# connect the virtual raster format checkBox
			cfg.ui.virtual_raster_checkBox.stateChanged.connect(cfg.sets.virtualRasterFormatCheckbox)
			# connect to raster data type
			cfg.ui.raster_precision_combo.currentIndexChanged.connect(cfg.sets.rasterDataTypeChange)
			# connect to clear log button
			cfg.ui.clearLog_Button.clicked.connect(cfg.utls.clearLogFile)
			# connect to export log button
			cfg.ui.exportLog_Button.clicked.connect(cfg.sets.copyLogFile)
			# connect to test dependencies button
			cfg.ui.test_dependencies_Button.clicked.connect(cfg.sets.testDependencies)
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
		else:
			dockdlg = DockDialog(qgisUtils.iface.mainWindow(), qgisUtils.iface)
			dockclassdlg = DockClassDialog(qgisUtils.iface.mainWindow(), qgisUtils.iface)
			qgisUtils.iface.removeDockWidget(dockdlg)
			qgisUtils.iface.removeDockWidget(dockclassdlg)			
			
	# save signature list when saving project
	def projectSaved(self):
		if len(cfg.signIDs) > 0:
			cfg.classD.saveSignatureListToFile()
		
	# new project
	def newProjectLoaded(self):
		cfg.projPath = QgsProject.instance().fileName()
		# clear band set
		tW = cfg.ui.tableWidget
		cfg.utls.clearTable(tW)
		# signature table
		cfg.utls.clearTable(cfg.uidc.signature_list_tableWidget)
		# reload layers in combos
		cfg.ipt.refreshRasterLayer()
		cfg.raster_name_combo.clear()
		# image name
		cfg.imgNm = None
		# raster name
		cfg.rstrNm = None
		# empty item for new band set
		cfg.ipt.raster_layer_combo("")
		cfg.uid.ROI_tableWidget.blockSignals(True)
		cfg.ROId.refreshShapeLayer()
		cfg.uid.ROI_tableWidget.blockSignals(False)
		cfg.clipMulti.refreshShapeClip()
		# reload layers in combos
		cfg.utls.refreshClassificationLayer()
		cfg.acc.refreshReferenceLayer()
		cfg.landCC.refreshClassificationReferenceLayer()
		cfg.landCC.refreshNewClassificationLayer()
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# reload rasters in checklist
		cfg.clipMulti.rasterNameList()
		cfg.bCalc.rasterBandName()
		cfg.uidc.signatureFile_lineEdit.setText("")
				
	# read project variables
	def projectLoaded(self):
		cfg.projPath = QgsProject.instance().fileName()
		# clear band set
		tW = cfg.ui.tableWidget
		cfg.utls.clearTable(tW)
		cfg.raster_name_combo.blockSignals(True)
		cfg.rasterComboEdited = "No"
		# read variables
		self.readVariables()
		# reload layers in combos
		cfg.ipt.refreshRasterLayer()
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
		# set vegetation index calculation checkbox state
		if cfg.vegIndexCheck == "Yes":
			cfg.uid.display_cursor_checkBox.setCheckState(2)
		elif cfg.vegIndexCheck == "No":
			cfg.uid.display_cursor_checkBox.setCheckState(0)
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
		cfg.ui.variable_name_lineEdit.setText(cfg.variableName)
		cfg.ui.group_name_lineEdit.setText(cfg.grpNm)
		# raster data type
		rDTid = cfg.ui.raster_precision_combo.findText(str(cfg.rasterDataType))
		cfg.ui.raster_precision_combo.setCurrentIndex(rDTid)
		if len(cfg.LandsatDatabaseDirectory) > 0:
			cfg.downLandsat.setDatabaseDir(cfg.LandsatDatabaseDirectory)
		else:
			cfg.downLandsat.setDatabaseDir()
		# reload layers in combos
		cfg.utls.refreshClassificationLayer()
		cfg.acc.refreshReferenceLayer()
		cfg.landCC.refreshClassificationReferenceLayer()
		cfg.landCC.refreshNewClassificationLayer()
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# reload rasters in checklist
		cfg.clipMulti.rasterNameList()
		cfg.bCalc.rasterBandName()
		if cfg.bndSetPresent == "No":
			# get wavelength
			bSW = cfg.utls.readProjectVariable("bndSetWvLn", "")
			bSM = cfg.utls.readProjectVariable("bndSetMultF", "")
			bSA = cfg.utls.readProjectVariable("bndSetAddF", "")
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
				try:
					multF = eval(bSM)
					addF = eval(bSA)
				except:
					pass
				t = cfg.ui.tableWidget
				cfg.BandTabEdited = "No"
				t.blockSignals(True)
				it = 0
				for x in sorted(wlg):
					b = wlg.index(x)
					# add item to table
					t.item(it, 1).setText(str(wlg[b]))
					try:
						mF = QTableWidgetItem()
						mF.setData(Qt.DisplayRole, str(str(multF[it])))
						t.setItem(it, 2, mF)
					except:
						mF = QTableWidgetItem()
						mF.setData(Qt.DisplayRole, str(1))
						t.setItem(it, 2, mF)		
					try:
						aF = QTableWidgetItem()
						aF.setData(Qt.DisplayRole, str(str(addF[it])))
						t.setItem(it, 3, aF)
					except:
						aF = QTableWidgetItem()
						aF.setData(Qt.DisplayRole, str(0))
						t.setItem(it, 3, aF)
					it = it + 1
				# load project unit in combo
				idU = cfg.ui.unit_combo.findText(bSU)
				cfg.ui.unit_combo.setCurrentIndex(idU)
				t.blockSignals(False)
			except Exception, err:
				t = cfg.ui.tableWidget
				t.blockSignals(False)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.bst.readBandSet("No")
			cfg.BandTabEdited = "Yes"
		cfg.rasterComboEdited = "Yes"
		cfg.raster_name_combo.blockSignals(False)
		# signature table
		cfg.utls.clearTable(cfg.uidc.signature_list_tableWidget)
		cfg.signList = {}
		cfg.signIDs = {}
		signPath = cfg.utls.readProjectVariable("signatureFilePath", "")
		if len(signPath) > 0:
			cfg.utls.readQGISVariablePath()
			absolutePath = cfg.utls.readProjectVariable("signatureFilePathAbsolute", str(cfg.absolutePath))
			if cfg.absolutePath == "false" and absolutePath != "false":
				cfg.classD.openSignatureListFile(signPath)
				signPath = cfg.utls.qgisAbsolutePathToRelativePath(signPath, cfg.projPath)
				cfg.uidc.signatureFile_lineEdit.setText(unicode(signPath))
			elif cfg.absolutePath != "false" and absolutePath == "false":
				signPath = cfg.utls.qgisRelativePathToAbsolutePath(signPath, cfg.projPath)
				cfg.classD.openSignatureListFile(signPath)
				cfg.uidc.signatureFile_lineEdit.setText(unicode(signPath))
			elif cfg.absolutePath == "false" and absolutePath == "false":
				cfg.uidc.signatureFile_lineEdit.setText(unicode(signPath))
				signPath = cfg.utls.qgisRelativePathToAbsolutePath(signPath, cfg.projPath)
				cfg.classD.openSignatureListFile(signPath)
			elif cfg.absolutePath != "false" and absolutePath != "false":
				cfg.classD.openSignatureListFile(signPath)
				cfg.uidc.signatureFile_lineEdit.setText(unicode(signPath))
			cfg.utls.writeProjectVariable("signatureFilePath", unicode(signPath))
			cfg.utls.writeProjectVariable("signatureFilePathAbsolute", str(cfg.absolutePath))

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
		cfg.vegIndexCheck = cfg.utls.readProjectVariable("vegetationIndex", "Yes")
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
		bSM = cfg.utls.readProjectVariable("bndSetMultF", "")
		bSA = cfg.utls.readProjectVariable("bndSetAddF", "")
		un = cfg.utls.readProjectVariable("bndSetUnit", cfg.noUnit)
		bSU = cfg.bst.unitNameConversion(un, "Yes")
		cfg.bndSetPresent = cfg.utls.readProjectVariable("bandSetPresent", "No")
		if cfg.bndSetPresent == "Yes":
			# add band set to table
			bs = eval(bSP)
			wlg = eval(bSW)
			try:
				multF = eval(bSM)
				addF = eval(bSA)
			except:
				pass
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
				try:
					mF = QTableWidgetItem()
					mF.setData(Qt.DisplayRole, str(str(multF[it])))
					t.setItem(c, 2, mF)
				except:
					mF = QTableWidgetItem()
					mF.setData(Qt.DisplayRole, str(1))
					t.setItem(c, 2, mF)		
				try:
					aF = QTableWidgetItem()
					aF.setData(Qt.DisplayRole, str(str(addF[it])))
					t.setItem(c, 3, aF)
				except:
					aF = QTableWidgetItem()
					aF.setData(Qt.DisplayRole, str(0))
					t.setItem(c, 3, aF)
				it = it + 1
			# load project unit in combo
			idU = cfg.ui.unit_combo.findText(bSU)
			cfg.ui.unit_combo.setCurrentIndex(idU)
			t.blockSignals(False)
			cfg.bst.readBandSet("Yes")
			cfg.BandTabEdited = "Yes"
		# read RGB list
		rgbList = cfg.utls.readProjectVariable("SCP_RGBList", str(cfg.RGBList))
		cfg.RGBList = eval(rgbList)
		try:
			cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
		except:
			pass
				
	# run
	def run(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "OPEN SESSION" + cfg.sysInfo)
		# show the dialog
		cfg.dlg.show()
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# reload rasters in checklist
		cfg.clipMulti.rasterNameList()
		# Run the dialog event loop
		pointer_result = cfg.dlg.exec_()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "CLOSE SESSION")
		
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
		try:
			cfg.iface.removePluginMenu(u"&Semi-Automatic Classification Plugin", cfg.mainAction)
			cfg.iface.removeToolBarIcon(cfg.mainAction)
			qgisUtils.iface.removeDockWidget(cfg.dockdlg)
			qgisUtils.iface.removeDockWidget(cfg.dockclassdlg)
			cfg.menu.deleteLater()
			# remove temp files
			if cfg.tmpDir is not None and QDir(cfg.tmpDir).exists():
				shutil.rmtree(cfg.tmpDir, True)
			if not QDir(cfg.tmpDir).exists():
				os.makedirs(cfg.tmpDir)
		except:
			if PluginCheck == "Yes":
				qgisUtils.iface.messageBar().pushMessage("Semi-Automatic Classification Plugin", QApplication.translate("semiautomaticclassificationplugin", "Please, restart QGIS for executing the Semi-Automatic Classification Plugin"), level=QgsMessageBar.INFO)