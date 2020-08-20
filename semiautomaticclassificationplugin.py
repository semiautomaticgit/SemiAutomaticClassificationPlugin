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

import os
import sys
import platform
import inspect
import shutil
import time
import datetime
import subprocess
import numpy as np
import urllib
import ssl
import smtplib
from http.cookiejar import CookieJar
import itertools
import zipfile
import tarfile
import base64
import random
import re
import xml.etree.cElementTree as ET
from xml.dom import minidom
import hashlib
import ctypes
from collections import Counter
# Import the PyQt libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, QFileInfo, QSettings, QDir, QDate, QVariant, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QNetworkRequest
# Import the QGIS libraries
import qgis.core as qgisCore
import qgis.gui as qgisGui
import qgis.utils as qgisUtils
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
# Initialize Qt ui
from .ui.resources_rc import *
from .ui.ui_semiautomaticclassificationplugin import Ui_SemiAutomaticClassificationPlugin
from .ui.ui_semiautomaticclassificationplugin_welcome import Ui_SCP_Welcome
from .ui.semiautomaticclassificationplugindialog import SemiAutomaticClassificationPluginDialog
from .ui.semiautomaticclassificationplugindialog import SpectralSignatureDialog
from .ui.semiautomaticclassificationplugindialog import WelcomeDialog
from .ui.semiautomaticclassificationplugindialog import ScatterPlotDialog
from .ui.semiautomaticclassificationplugindialog import DockClassDialog
# Import plugin version
from .__init__ import version as semiautomaticclassVersion

global PluginCheck
PluginCheck = "Yes"
try:
	from .core import config as cfg
except:
	PluginCheck = "No"
	
# required by other modules
cfg.QObjectSCP = QObject
cfg.pyqtSignalSCP = pyqtSignal


if PluginCheck == "Yes":
	try:
		from .core.messages import Messages as msgs
		from .core.utils import Utils
		from .core.signature_importer import Signature_Importer
		from .maininterface.downloadproductpointer import DownloadProductPointer
		from .maininterface.downloadproducts import DownloadProducts
		from .spectralsignature.spectralsignatureplot import SpectralSignaturePlot
		from .spectralsignature.scatter_plot import Scatter_Plot	
		from .dock.manualroi import ManualROI
		from .dock.regionroi import RegionROI
		from .dock.scpdock import SCPDock
		from .dock.classificationpreview import ClassificationPreview
		from .maininterface.multipleroiTab import MultipleROITab
		from .spectralsignature.usgs_spectral_lib import USGS_Spectral_Lib
		from .maininterface.landsatTab import LandsatTab
		from .maininterface.asterTab import ASTERTab
		from .maininterface.modisTab import MODISTab
		from .maininterface.sentinel2Tab import Sentinel2Tab
		from .maininterface.sentinel3Tab import Sentinel3Tab
		from .maininterface.accuracy import Accuracy
		from .maininterface.crossclassificationTab import CrossClassification
		from .maininterface.bandcombination import BandCombination
		from .maininterface.splitTab import SplitTab
		from .maininterface.pcaTab import PcaTab
		from .maininterface.clusteringTab import ClusteringTab
		from .maininterface.classSignatureTab import ClassSignatureTab
		from .maininterface.vectortorasterTab import VectorToRasterTab
		from .maininterface.bandsetTab import BandsetTab
		from .maininterface.algorithmWeightTab import AlgWeightTab
		from .maininterface.signatureThresholdTab import SigThresholdTab
		from .maininterface.LCSignatureThresholdTab import LCSigThresholdTab
		from .maininterface.rgblistTab import RGBListTab
		from .maininterface.LCSignaturePixel import LCSigPixel
		from .maininterface.LCSignaturePixel2 import LCSigPixel2
		from .maininterface.bandcalcTab import BandCalcTab
		from .maininterface.batchTab import BatchTab
		from .maininterface.clipmultiplerasters import ClipMultipleRasters
		from .maininterface.stackrasterbands import StackRasterBands
		from .maininterface.mosaicbandsets import MosaicBandSets
		from .maininterface.cloudmasking import CloudMasking
		from .maininterface.spectraldistancebandsets import SpectralDistanceBandsets
		from .maininterface.editraster import EditRaster
		from .maininterface.sieveTab import SieveRaster
		from .maininterface.erosionTab import ErosionRaster
		from .maininterface.dilationTab import DilationRaster
		from .maininterface.clipmultiplerasterspointer import ClipMultiplerastersPointer
		from .maininterface.landcoverchange import LandCoverChange
		from .maininterface.classreportTab import ClassReportTab
		from .maininterface.classtovectorTab import ClassToVectorTab
		from .maininterface.reclassificationTab import ReclassificationTab
		from .maininterface.settings import Settings
		from .core.input import Input
		from .ui.ui_utils import Ui_Utils
	except:
		PluginCheck = "No"
		qgisUtils.iface.messageBar().pushMessage("Semi-Automatic Classification Plugin", QApplication.translate("semiautomaticclassificationplugin", "Please, restart QGIS for executing the Semi-Automatic Classification Plugin"), level=qgisCore.Qgis.Info)

	try:
		import scipy.stats.distributions as statdistr
		from scipy.spatial.distance import cdist
		from scipy import signal
		from scipy.ndimage import label
		from scipy.cluster.vq import vq, kmeans, whiten
		cfg.scipyCheck = 'Yes'
	except:
		cfg.scipyCheck = 'No'
	try:
		from matplotlib.ticker import MaxNLocator
		import matplotlib.pyplot as mplplt
		import matplotlib.colors as mplcolors
		cfg.matplotlibCheck = 'Yes'
	except Exception as err:
		cfg.testMatplotlibV = err
		cfg.matplotlibCheck = 'No'

	
class SemiAutomaticClassificationPlugin:

	def __init__(self, iface):
		try:
			cfg.osSCP = os
			cfg.sysSCP = sys
			cfg.platformSCP = platform
			cfg.shutilSCP = shutil
			cfg.inspectSCP = inspect
			cfg.timeSCP = time
			cfg.datetimeSCP = datetime
			cfg.subprocessSCP = subprocess
			cfg.urllibSCP = urllib
			cfg.itertoolsSCP = itertools
			cfg.zipfileSCP = zipfile
			cfg.tarfileSCP = tarfile
			cfg.base64SCP = base64
			cfg.randomSCP = random
			cfg.QtCoreSCP = QtCore
			cfg.QtGuiSCP = QtGui
			cfg.QtWidgetsSCP = QtWidgets
			cfg.QNetworkRequestSCP = QNetworkRequest
			cfg.QtSCP = Qt
			cfg.QVariantSCP = QVariant
			cfg.QFileInfoSCP = QFileInfo
			cfg.QSettingsSCP = QSettings
			cfg.QDirSCP = QDir
			cfg.QDateSCP = QDate
			cfg.qgisCoreSCP = qgisCore
			cfg.qgisGuiSCP = qgisGui
			cfg.gdalSCP = gdal
			cfg.ogrSCP = ogr
			cfg.osrSCP = osr
			cfg.sslSCP = ssl
			cfg.smtplibSCP = smtplib
			cfg.CookieJarSCP = CookieJar
			cfg.reSCP = re
			cfg.ETSCP = ET
			cfg.minidomSCP = minidom
			cfg.hashlibSCP = hashlib
			cfg.ctypesSCP = ctypes
			cfg.counterSCP = Counter
		except:
			qgisUtils.iface.messageBar().pushMessage('Semi-Automatic Classification Plugin', QApplication.translate('semiautomaticclassificationplugin', 'Please, restart QGIS for executing the Semi-Automatic Classification Plugin'), level=qgisCore.Qgis.Critical)
			return
		try:
			cfg.np = np
		except:
			qgisUtils.iface.messageBar().pushMessage('Semi-Automatic Classification Plugin', QApplication.translate('semiautomaticclassificationplugin', 'Error. Check Python Numpy installation for the Semi-Automatic Classification Plugin'), level=qgisCore.Qgis.Critical)
		try:
			if cfg.scipyCheck == 'Yes':
				cfg.statdistrSCP = statdistr
				cfg.cdistSCP = cdist
				cfg.signalSCP = signal
				cfg.labelSCP = label
				cfg.vqSCP = vq
				cfg.kmeansSCP = kmeans
				cfg.whitenSCP = whiten
			if cfg.matplotlibCheck == 'Yes':
				cfg.MaxNLocatorSCP = MaxNLocator
				cfg.mplpltSCP = mplplt
				cfg.mplcolorsSCP = mplcolors
		except:
			pass
		if cfg.scipyCheck == 'No':
			qgisUtils.iface.messageBar().pushMessage('Semi-Automatic Classification Plugin', QApplication.translate('semiautomaticclassificationplugin', 'Error. Check Python Scipy installation for the Semi-Automatic Classification Plugin'), level=qgisCore.Qgis.Critical)
		if cfg.matplotlibCheck == 'No':
			qgisUtils.iface.messageBar().pushMessage('Semi-Automatic Classification Plugin', QApplication.translate('semiautomaticclassificationplugin', 'Error. Check Python Matplotlib installation for the Semi-Automatic Classification Plugin'), level=qgisCore.Qgis.Critical)
		if PluginCheck == 'Yes':
			# reference to QGIS interface
			cfg.iface = iface
			# reference to map canvas
			cfg.cnvs = iface.mapCanvas()
			# create the dialog
			cfg.dlg = SemiAutomaticClassificationPluginDialog()
			# reference to ui
			cfg.ui = cfg.dlg.ui
			# class dock dialog
			cfg.dockclassdlg = DockClassDialog(cfg.iface.mainWindow(), cfg.iface)
			# reference dock class ui
			cfg.uidc = cfg.dockclassdlg.ui
			# welcome dialog
			cfg.welcomedlg = WelcomeDialog()
			# spectral signature plot dialog
			cfg.spectralplotdlg = SpectralSignatureDialog()
			cfg.uisp = cfg.spectralplotdlg.ui
			# scatter plot dialog
			cfg.scatterplotdlg = ScatterPlotDialog()
			cfg.uiscp = cfg.scatterplotdlg.ui
			cfg.mx = msgs(cfg.iface)
			cfg.utls = Utils()
			cfg.SCPD = SCPDock()
			cfg.classPrev = ClassificationPreview(cfg.cnvs)
			cfg.spSigPlot = SpectralSignaturePlot()
			cfg.scaPlT = Scatter_Plot()
			cfg.multiROI = MultipleROITab()
			cfg.usgsLib = USGS_Spectral_Lib()
			cfg.acc = Accuracy()
			cfg.crossC = CrossClassification()
			cfg.bsComb = BandCombination()
			cfg.splitT = SplitTab()
			cfg.pcaT = PcaTab()
			cfg.clusteringT = ClusteringTab()
			cfg.classSigT = ClassSignatureTab()
			cfg.vctRstrT = VectorToRasterTab()
			cfg.bst = BandsetTab()
			cfg.algWT = AlgWeightTab()
			cfg.signT = SigThresholdTab()
			cfg.LCSignT = LCSigThresholdTab()
			cfg.RGBLT = RGBListTab()
			cfg.bCalc = BandCalcTab()
			cfg.batchT= BatchTab()
			cfg.clipMulti = ClipMultipleRasters()
			cfg.stackRstr = StackRasterBands()
			cfg.mosaicBS = MosaicBandSets()
			cfg.cloudMsk = CloudMasking()
			cfg.spclDstBS = SpectralDistanceBandsets()
			cfg.editRstr = EditRaster()
			cfg.sieveRstr = SieveRaster()
			cfg.ersnRstr = ErosionRaster()
			cfg.dltnRstr = DilationRaster()
			cfg.downProd = DownloadProducts()
			cfg.landsatT = LandsatTab()
			cfg.ASTERT = ASTERTab()
			cfg.MODIST = MODISTab()
			cfg.sentinel2T = Sentinel2Tab()
			cfg.sentinel3T = Sentinel3Tab()
			cfg.landCC = LandCoverChange()
			cfg.classRep = ClassReportTab()
			cfg.classVect = ClassToVectorTab()
			cfg.reclassification = ReclassificationTab()
			cfg.sigImport = Signature_Importer()
			cfg.mnlROI = ManualROI(cfg.cnvs)
			cfg.regionROI = RegionROI(cfg.cnvs)
			cfg.dwnlPrdPnt = DownloadProductPointer(cfg.cnvs)
			cfg.clipMultiP = ClipMultiplerastersPointer(cfg.cnvs)
			cfg.LCSPixel = LCSigPixel(cfg.cnvs)
			cfg.LCSPixel2 = LCSigPixel2(cfg.cnvs)
			cfg.sets = Settings()
			cfg.uiUtls = Ui_Utils()
			cfg.ipt = Input()
			# connect when map is clicked
			cfg.mnlROI.rightClicked.connect(cfg.SCPD.clckR)
			cfg.mnlROI.leftClicked.connect(cfg.SCPD.clckL)
			cfg.mnlROI.moved.connect(cfg.SCPD.movedPointer)
			cfg.regionROI.ROIleftClicked.connect(cfg.SCPD.pointerClickROI)
			cfg.regionROI.ROIrightClicked.connect(cfg.SCPD.pointerRightClickROI)
			cfg.regionROI.moved.connect(cfg.SCPD.movedPointer)
			cfg.clipMultiP.leftClicked.connect(cfg.clipMulti.pointerLeftClick)
			cfg.clipMultiP.rightClicked.connect(cfg.clipMulti.pointerRightClick)
			cfg.dwnlPrdPnt.leftClicked.connect(cfg.downProd.pointerLeftClick)
			cfg.dwnlPrdPnt.rightClicked.connect(cfg.downProd.pointerRightClick)
			cfg.classPrev.leftClicked.connect(cfg.SCPD.pointerClickPreview)
			cfg.classPrev.rightClicked.connect(cfg.SCPD.pointerRightClickPreview)
			cfg.LCSPixel.MaprightClicked.connect(cfg.LCSignT.pointerLeftClick)
			cfg.LCSPixel.MapleftClicked.connect(cfg.LCSignT.pointerLeftClick)
			cfg.LCSPixel2.MaprightClicked.connect(cfg.spSigPlot.pointerLeftClick)
			cfg.LCSPixel2.MapleftClicked.connect(cfg.spSigPlot.pointerLeftClick)			
			# system variables
			cfg.utls.findSystemSpecs()
			cfg.utls.readVariables()
			# initialize plugin directory
			cfg.plgnDir = cfg.QFileInfoSCP(cfg.qgisCoreSCP.QgsApplication.qgisUserDatabaseFilePath()).path() + "/python/plugins/" + str(__name__).split(".")[0]
			# initialize LOG directory
			cfg.lgndir = cfg.plgnDir
			# log file path
			cfg.logFile = cfg.lgndir.replace('//', '/') + "/__0semiautomaticclass.log"
			# locale name
			lclNm = cfg.QSettingsSCP().value("locale/userLocale")[0:2]
			self.registryKeys()
			""" temporary directory """
			tmpDir = cfg.utls.getTempDirectory()
			cfg.ui.temp_directory_label.setText(tmpDir)
			""" locale """
			lclPth = "" 
			if cfg.QFileInfoSCP(cfg.plgnDir).exists(): 
				lclPth = cfg.plgnDir + "/i18n/semiautomaticclassificationplugin_" + lclNm + ".qm" 
			if cfg.QFileInfoSCP(lclPth).exists(): 
				trnsltr = cfg.QtCoreSCP.QTranslator() 
				trnsltr.load(lclPth) 
				if cfg.QtCoreSCP.qVersion() > '4.3.3': 
					cfg.QtCoreSCP.QCoreApplication.installTranslator(trnsltr)
			""" info """
			cfg.sysSCPInfo = str(" SemiAutomaticClass " + semiautomaticclassVersion() + " - QGIS v. " + str(cfg.QGISVer) + " L:" + lclNm + " - OS " + str(cfg.sysSCPNm) + " - 64bit =" + cfg.sysSCP64bit)
			# GDAL NUMBER of THREADS
			try:
				cfg.gdalSCP.SetConfigOption('GDAL_NUM_THREADS', 'ALL_CPUS')
			except:
				pass

	# read registry keys 
	def registryKeys(self):
		""" registry keys """
		cfg.firstInstallVal = cfg.utls.readRegistryKeys(cfg.regFirstInstall, cfg.firstInstallVal)
		cfg.logSetVal = cfg.utls.readRegistryKeys(cfg.regLogKey, cfg.logSetVal)
		cfg.downNewsVal = cfg.utls.readRegistryKeys(cfg.downNewsKey, cfg.downNewsVal)
		cfg.ROIClrVal = cfg.utls.readRegistryKeys(cfg.regROIClr, cfg.ROIClrVal)
		cfg.ROITrnspVal = int(cfg.utls.readRegistryKeys(cfg.regROITransp, cfg.ROITrnspVal))
		cfg.algFilesCheck = cfg.utls.readRegistryKeys(cfg.regAlgFiles, str(cfg.algFilesCheck))
		cfg.outTempRastFormat = cfg.utls.readRegistryKeys(cfg.regTempRasterFormat, str(cfg.outTempRastFormat))
		cfg.rasterCompression = cfg.utls.readRegistryKeys(cfg.regRasterCompression, str(cfg.rasterCompression))
		cfg.RAMValue = int(cfg.utls.readRegistryKeys(cfg.regRAMValue, str(cfg.RAMValue)))
		cfg.tmpDir = cfg.utls.readRegistryKeys(cfg.regTmpDir, cfg.tmpDir)
		cfg.fldID_class = cfg.utls.readRegistryKeys(cfg.regIDFieldName, cfg.fldID_class)
		cfg.fldMacroID_class = cfg.utls.readRegistryKeys(cfg.regMacroIDFieldName, cfg.fldMacroID_class)
		cfg.macroclassCheck = cfg.utls.readRegistryKeys(cfg.regConsiderMacroclass, cfg.macroclassCheck)
		cfg.LCsignatureCheckBox = cfg.utls.readRegistryKeys(cfg.regLCSignature, cfg.LCsignatureCheckBox)
		cfg.fldROI_info = cfg.utls.readRegistryKeys(cfg.regInfoFieldName, cfg.fldROI_info)
		cfg.fldROIMC_info = cfg.utls.readRegistryKeys(cfg.regMCInfoFieldName, cfg.fldROIMC_info)
		cfg.variableName = cfg.utls.readRegistryKeys(cfg.regVariableName, cfg.variableName)		
		cfg.vectorVariableName = cfg.utls.readRegistryKeys(cfg.regVectorVariableName, cfg.vectorVariableName)		
		cfg.SMTPCheck = cfg.utls.readRegistryKeys(cfg.regSMTPCheck, cfg.SMTPCheck)
		cfg.SMTPServer = cfg.utls.readRegistryKeys(cfg.regSMTPServer, cfg.SMTPServer)
		cfg.SMTPtoEmails = cfg.utls.readRegistryKeys(cfg.regSMTPtoEmails, cfg.SMTPtoEmails)
		cfg.SMTPUser = cfg.utls.readRegistryKeys(cfg.regSMTPUser, cfg.SMTPUser)
		cfg.SMTPPassword = cfg.utls.readRegistryKeys(cfg.regSMTPPassword, cfg.SMTPPassword)
		cfg.USGSUser = cfg.utls.readRegistryKeys(cfg.regUSGSUser, cfg.USGSUser)
		cfg.USGSPass = cfg.utls.readRegistryKeys(cfg.regUSGSPass, cfg.USGSPass)
		cfg.USGSUserASTER = cfg.utls.readRegistryKeys(cfg.regUSGSUserASTER, cfg.USGSUserASTER)
		cfg.USGSPassASTER = cfg.utls.readRegistryKeys(cfg.regUSGSPassASTER, cfg.USGSPassASTER)
		cfg.SciHubUser = cfg.utls.readRegistryKeys(cfg.regSciHubUser, cfg.SciHubUser)
		cfg.SciHubService = cfg.utls.readRegistryKeys(cfg.regSciHubService, cfg.SciHubService)
		cfg.SciHubPass = cfg.utls.readRegistryKeys(cfg.regSciHubPass, cfg.SciHubPass)
		cfg.sigPLRoundCharList = cfg.roundCharList
		cfg.scatPlRoundCharList = cfg.roundCharList
		cfg.grpNm = cfg.utls.readRegistryKeys(cfg.regGroupName, cfg.grpNm)
		cfg.rasterDataType = cfg.utls.readRegistryKeys(cfg.regRasterDataType, cfg.rasterDataType)
		cfg.expressionListBC = cfg.utls.readRegistryKeys(cfg.regExpressionListBC, cfg.expressionListBC)
		cfg.soundVal = cfg.utls.readRegistryKeys(cfg.regSound, cfg.soundVal)
		
	def initGui(self):
		if PluginCheck == "Yes":
			try:
				cfg.iface.addDockWidget(cfg.QtSCP.LeftDockWidgetArea, cfg.dockclassdlg)
			except:
				msg = ""
				try:
					import scipy.stats.distributions as statdistr
				except:
					msg = "SciPy"
				try:
					from matplotlib.ticker import MaxNLocator
				except:
					msg = "Matplotlib"
				try:
					import numpy as np
				except:
					msg = "NumPy"
				try:
					from osgeo import gdal
				except:
					msg = "Gdal"
				if len(msg) > 0:
					qgisUtils.iface.messageBar().pushMessage("Semi-Automatic Classification Plugin", QApplication.translate("semiautomaticclassificationplugin", "Semi-Automatic Classification Plugin possible missing dependecies: " + msg), level=qgisCore.Qgis.Info)
				else:
					qgisUtils.iface.messageBar().pushMessage("Semi-Automatic Classification Plugin", QApplication.translate("semiautomaticclassificationplugin", "Please restart QGIS for installing the Semi-Automatic Classification Plugin"), level=qgisCore.Qgis.Info)
				return
			cfg.ipt.loadInputToolbar()
			cfg.algMinDist = cfg.uidc.algorithm_combo.itemText(0) 
			cfg.algML = cfg.uidc.algorithm_combo.itemText(1) 
			cfg.algSAM = cfg.uidc.algorithm_combo.itemText(2)
			cfg.algName = cfg.algMinDist
			cfg.uidc.algorithm_combo.setCurrentIndex(0)
			# vector to raster type of conversion
			cfg.ui.conversion_type_combo.addItem(cfg.convCenterPixels)
			cfg.ui.conversion_type_combo.addItem(cfg.convAllPixelsTouch)
			cfg.centerOfPixels = cfg.ui.conversion_type_combo.itemText(0)
			""" menu """
			cfg.ipt.loadMenu()
			# set plugin version
			cfg.ui.plugin_version_label.setText(semiautomaticclassVersion())
			cfg.uidc.plugin_version_label2.setText("SCP " + semiautomaticclassVersion())
			# signature list
			cfg.utls.insertTableColumn(cfg.uidc.signature_list_tableWidget, 6, cfg.tableColString, None, "Yes")
			cfg.utls.sortTableColumn(cfg.uidc.signature_list_tableWidget, 6)
			cfg.utls.setColumnWidthList(cfg.uidc.signature_list_tableWidget, [[0, 30], [1, 30], [2, 40], [3, 40], [4, 50], [5, 40]])
			# row height
			cfg.ui.download_images_tableWidget.verticalHeader().setDefaultSectionSize(16)
			cfg.ui.tableWidget_band_calc.verticalHeader().setDefaultSectionSize(16)
			cfg.ui.landsat_tableWidget.verticalHeader().setDefaultSectionSize(16)
			cfg.ui.sentinel_2_tableWidget.verticalHeader().setDefaultSectionSize(16)
			cfg.utls.setColumnWidthList(cfg.ui.sentinel_2_tableWidget, [[0, 400], [1, 200], [2, 60]])
			cfg.ui.ASTER_tableWidget.verticalHeader().setDefaultSectionSize(16)
			cfg.utls.setColumnWidthList(cfg.ui.ASTER_tableWidget, [[0, 400], [1, 200], [2, 60]])
			cfg.ui.MODIS_tableWidget.verticalHeader().setDefaultSectionSize(16)
			cfg.utls.setColumnWidthList(cfg.ui.MODIS_tableWidget, [[0, 400], [1, 200], [2, 60]])
			cfg.ui.LCS_tableWidget.verticalHeader().setDefaultSectionSize(16)
			cfg.ui.signature_threshold_tableWidget.verticalHeader().setDefaultSectionSize(16)
			cfg.ui.point_tableWidget.verticalHeader().setDefaultSectionSize(16)
			cfg.ui.log_tableWidget.verticalHeader().setDefaultSectionSize(16)
			cfg.utls.setColumnWidthList(cfg.ui.log_tableWidget, [[0, 100], [1, 200], [2, 800]])
			try:
				cfg.uidc.signature_list_tableWidget.horizontalHeader().setSectionResizeMode(4, cfg.QtWidgetsSCP.QHeaderView.Stretch)
			except:
				pass
			try:
				cfg.uidc.macroclass_color_tableWidget.horizontalHeader().setSectionResizeMode(1, cfg.QtWidgetsSCP.QHeaderView.Stretch)
			except:
				pass
			# spectral signature plot list
			cfg.utls.insertTableColumn(cfg.uisp.signature_list_plot_tableWidget, 6, cfg.tableColString, None, "Yes")
			cfg.utls.sortTableColumn(cfg.uisp.signature_list_plot_tableWidget, 3)
			cfg.utls.setColumnWidthList(cfg.uisp.signature_list_plot_tableWidget, [[0, 30], [1, 40], [2, 100], [3, 40], [4, 100], [5, 30]])
			try:
				cfg.uisp.signature_list_plot_tableWidget.horizontalHeader().setSectionResizeMode(2, cfg.QtWidgetsSCP.QHeaderView.Stretch)
				cfg.uisp.signature_list_plot_tableWidget.horizontalHeader().setSectionResizeMode(4, cfg.QtWidgetsSCP.QHeaderView.Stretch)
			except:
				pass
			# passwords
			cfg.ui.smtp_password_lineEdit.setEchoMode(cfg.QtWidgetsSCP.QLineEdit.Password)
			cfg.ui.password_usgs_lineEdit.setEchoMode(cfg.QtWidgetsSCP.QLineEdit.Password)
			cfg.ui.password_usgs_lineEdit_2.setEchoMode(cfg.QtWidgetsSCP.QLineEdit.Password)
			cfg.ui.password_scihub_lineEdit.setEchoMode(cfg.QtWidgetsSCP.QLineEdit.Password)
			# scatter plot list
			cfg.utls.insertTableColumn(cfg.uiscp.scatter_list_plot_tableWidget, 6, cfg.tableColString, None, "Yes")
			cfg.utls.sortTableColumn(cfg.uiscp.scatter_list_plot_tableWidget, 3)
			cfg.utls.setColumnWidthList(cfg.uiscp.scatter_list_plot_tableWidget, [[0, 30], [1, 40], [2, 100], [3, 40], [4, 100], [5, 30]])
			try:
				cfg.uiscp.scatter_list_plot_tableWidget.horizontalHeader().setSectionResizeMode(2, cfg.QtWidgetsSCP.QHeaderView.Stretch)
				cfg.uiscp.scatter_list_plot_tableWidget.horizontalHeader().setSectionResizeMode(4, cfg.QtWidgetsSCP.QHeaderView.Stretch)
			except:
				pass
			# signature threshold
			cfg.utls.insertTableColumn(cfg.ui.signature_threshold_tableWidget, 7, cfg.tableColString, None, "Yes")
			cfg.utls.setColumnWidthList(cfg.ui.signature_threshold_tableWidget,  [[4, 100], [5, 100], [6, 100]])
			try:
				cfg.ui.signature_threshold_tableWidget.horizontalHeader().setSectionResizeMode(1, cfg.QtWidgetsSCP.QHeaderView.Stretch)
				cfg.ui.signature_threshold_tableWidget.horizontalHeader().setSectionResizeMode(3, cfg.QtWidgetsSCP.QHeaderView.Stretch)
			except:
				pass
			# product download tab
			cfg.utls.setColumnWidthList(cfg.ui.download_images_tableWidget, [[0, 100], [1, 400]])
			# USGS spectral lbrary
			cfg.usgsLib.addSpectralLibraryToCombo(cfg.usgs_lib_list)
			cfg.usgs_C1p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/minerals.csv"
			cfg.usgs_C2p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/mixtures.csv"
			cfg.usgs_C3p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/coatings.csv"
			cfg.usgs_C4p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/volatiles.csv"
			cfg.usgs_C5p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/man-made.csv"
			cfg.usgs_C6p = cfg.plgnDir + "/spectralsignature/usgs_spectral_library/plants_veg_microorg.csv"
			# band calc expression
			cfg.bCalc.createExpressionList(cfg.expressionListBC)
			cfg.batchT.addFunctionsToTable(cfg.functionNames)
			cfg.bst.addSatelliteToCombo(cfg.satWlList)
			cfg.downProd.addSatelliteToCombo(cfg.downProductList)
			cfg.scaPlT.addColormapToCombo(cfg.scatterColorMap)
			cfg.bst.addUnitToCombo(cfg.unitList)
			cfg.SCPD.previewSize()
			# set log state
			if cfg.logSetVal == "Yes":
				cfg.ui.log_checkBox.setCheckState(2)
				cfg.mx.msg19()
			elif cfg.logSetVal == "No":
				cfg.ui.log_checkBox.setCheckState(0)
			# set download news state
			if cfg.downNewsVal == "Yes":
				cfg.ui.download_news_checkBox.setCheckState(2)
			elif cfg.downNewsVal == "No":
				cfg.ui.download_news_checkBox.setCheckState(0)
			# set alg files state
			if cfg.algFilesCheck == "Yes":
				cfg.uidc.alg_files_checkBox.setCheckState(2)
			elif cfg.algFilesCheck == "No":
				cfg.uidc.alg_files_checkBox.setCheckState(0)
			# set raster format
			if cfg.outTempRastFormat == "VRT":
				cfg.ui.virtual_raster_checkBox.setCheckState(2)
			elif cfg.outTempRastFormat == "GTiff":
				cfg.ui.virtual_raster_checkBox.setCheckState(0)
			# set raster compression
			if cfg.rasterCompression == "Yes":
				cfg.ui.raster_compression_checkBox.setCheckState(2)
			elif cfg.rasterCompression == "No":
				cfg.ui.raster_compression_checkBox.setCheckState(0)
			# set SMTP checkbox state
			if cfg.SMTPCheck == "Yes":
				cfg.ui.smtp_checkBox.setCheckState(2)
			elif cfg.SMTPCheck == "No":
				cfg.ui.smtp_checkBox.setCheckState(0)
			# set sound state
			if cfg.soundVal == "Yes":
				cfg.ui.sound_checkBox.setCheckState(2)
			elif cfg.soundVal == "No":
				cfg.ui.sound_checkBox.setCheckState(0)
			# connect to project loaded
			cfg.qgisCoreSCP.QgsProject.instance().readProject.connect(self.projectLoaded)
			cfg.qgisCoreSCP.QgsProject.instance().projectSaved.connect(self.projectSaved)
			cfg.iface.newProjectCreated.connect(self.newProjectLoaded)
			#cfg.qgisCoreSCP.QgsProject.instance().readMapLayer.connect(self.test)
			#cfg.qgisCoreSCP.QgsProject.instance().layerLoaded.connect(self.test)
			
			""" Docks """
			# reload layers in combos
			cfg.ipt.refreshRasterLayer()
			cfg.utls.refreshVectorLayer()
			# set ROI color
			cfg.ui.change_color_Button.setStyleSheet("background-color :" + cfg.ROIClrVal)
			# set ROI transparency
			cfg.ui.transparency_Slider.setValue(cfg.ROITrnspVal)
			# set RAM value
			cfg.ui.RAM_spinBox.setValue(cfg.RAMValue)
			# macroclass checkbox
			if cfg.macroclassCheck == "No":
				cfg.uidc.macroclass_checkBox.setCheckState(0)
				cfg.uidc.class_checkBox.blockSignals(True)
				cfg.uidc.class_checkBox.setCheckState(2)
				cfg.uidc.class_checkBox.blockSignals(False)
			elif cfg.macroclassCheck == "Yes":
				cfg.uidc.macroclass_checkBox.setCheckState(2)
				cfg.uidc.class_checkBox.blockSignals(True)
				cfg.uidc.class_checkBox.setCheckState(0)
				cfg.uidc.class_checkBox.blockSignals(False)
			# LC signature checkbox
			if cfg.LCsignatureCheckBox == "No":
				cfg.uidc.LC_signature_checkBox.setCheckState(0)
			elif cfg.LCsignatureCheckBox == "Yes":
				cfg.uidc.LC_signature_checkBox.setCheckState(2)
			try:
				# set ID field name line
				cfg.ui.ID_field_name_lineEdit.setText(cfg.fldID_class)
				cfg.ui.MID_field_name_lineEdit.setText(cfg.fldMacroID_class)
				# set Info field name line
				cfg.ui.Info_field_name_lineEdit.setText(cfg.fldROI_info)
				cfg.ui.MCInfo_field_name_lineEdit.setText(cfg.fldROIMC_info)
				cfg.ui.variable_name_lineEdit.setText(cfg.variableName)
				cfg.ui.group_name_lineEdit.setText(cfg.grpNm)
				# set SMTP server
				cfg.ui.smtp_server_lineEdit.setText(cfg.SMTPServer)
				# set SMTP to emails
				cfg.ui.to_email_lineEdit.setText(cfg.SMTPtoEmails)
				# set SMTP user and password
				cfg.ui.smtp_user_lineEdit.setText(cfg.SMTPUser)
				if cfg.SMTPPassword is not None:
					SMTPPsw = cfg.utls.decryptPassword(cfg.SMTPPassword[2:-1])
					cfg.ui.smtp_password_lineEdit.setText(str(SMTPPsw)[2:-1])
					cfg.SMTPPassword = str(SMTPPsw)[2:-1]
				# set USGS user and password
				cfg.ui.user_usgs_lineEdit.setText(cfg.USGSUser)
				if cfg.USGSPass is not None:
					USGSPsw = cfg.utls.decryptPassword(cfg.USGSPass[2:-1])
					cfg.ui.password_usgs_lineEdit.setText(str(USGSPsw)[2:-1])
				cfg.ui.user_usgs_lineEdit_2.setText(cfg.USGSUserASTER)
				if cfg.USGSPassASTER is not None:
					USGSPsw2 = cfg.utls.decryptPassword(cfg.USGSPassASTER[2:-1])
					cfg.ui.password_usgs_lineEdit_2.setText(str(USGSPsw2)[2:-1])
				# set SciHub user and password
				cfg.ui.sentinel_service_lineEdit.setText(cfg.SciHubService)
				cfg.ui.user_scihub_lineEdit.setText(cfg.SciHubUser)
				if cfg.SciHubPass is not None:
					sciHubPsw = cfg.utls.decryptPassword(cfg.SciHubPass[2:-1])
					cfg.ui.password_scihub_lineEdit.setText(str(sciHubPsw)[2:-1])
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			# reload layers in combos
			cfg.utls.refreshClassificationLayer()
			cfg.utls.refreshRasterExtent()
			cfg.acc.refreshReferenceLayer()
			cfg.crossC.refreshReferenceLayer()
			cfg.landCC.refreshClassificationReferenceLayer()
			cfg.landCC.refreshNewClassificationLayer()
			# reload raster bands in checklist
			cfg.bst.rasterBandName()
			# set default SCP tab
			cfg.ipt.SCPTabChanged(0)
			""" SCP tab """
			cfg.ui.SCP_tabs.currentChanged.connect(cfg.ipt.SCPTabChanged)
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
			# connect to text changed
			cfg.ui.stratified_lineEdit.textChanged.connect(cfg.multiROI.textChanged)
			""" Import spectral signature tab """
			# connect the import library
			cfg.ui.open_library_pushButton.clicked.connect(cfg.SCPD.openLibraryFile)
			# connect the open shapefile
			cfg.ui.open_shapefile_pushButton.clicked.connect(cfg.sigImport.openShapefileI)
			# connect the import shapefile
			cfg.ui.import_shapefile_pushButton.clicked.connect(cfg.utls.importShapefile)
			# connect the chapter changed
			cfg.ui.usgs_chapter_comboBox.currentIndexChanged.connect(cfg.usgsLib.chapterChanged)
			# connect the library changed
			cfg.ui.usgs_library_comboBox.currentIndexChanged.connect(cfg.usgsLib.libraryChanged)
			# connect the close library
			cfg.ui.add_usgs_library_pushButton.clicked.connect(cfg.usgsLib.addSignatureToList)
			""" Export spectral signature tab """
			# connect to export signature to SCP file
			cfg.ui.export_SCP_pushButton.clicked.connect(cfg.SCPD.exportSignatureFile)
			cfg.ui.export_SHP_pushButton.clicked.connect(cfg.SCPD.exportSignatureShapefile)
			# connect to export signature to CSV
			cfg.ui.export_CSV_library_toolButton.clicked.connect(cfg.SCPD.exportToCSVLibrary)
			""" Algorithm weight tab """
			cfg.ui.reset_weights_pushButton.clicked.connect(cfg.algWT.resetWeights)
			cfg.ui.set_weight_value_pushButton.clicked.connect(cfg.algWT.setWeights)
			""" Signature threshold tab """
			# edited cell
			cfg.ui.signature_threshold_tableWidget.cellChanged.connect(cfg.signT.editedThresholdTable)
			cfg.ui.reset_threshold_pushButton.clicked.connect(cfg.signT.resetThresholds)
			cfg.ui.automatic_threshold_pushButton.clicked.connect(cfg.signT.setAllWeightsVariance)
			cfg.ui.set_threshold_value_pushButton.clicked.connect(cfg.signT.setThresholds)
			cfg.ui.signature_threshold_tableWidget.horizontalHeader().sectionClicked.connect(cfg.signT.orderedTable)
			""" LC Signature threshold tab """
			cfg.ui.LCS_tableWidget.cellChanged.connect(cfg.LCSignT.editedThresholdTable)
			cfg.ui.LCS_tableWidget.horizontalHeader().sectionClicked.connect(cfg.LCSignT.orderedTable)
			cfg.ui.automatic_threshold_pushButton_2.clicked.connect(cfg.LCSignT.setAllWeightsVariance)
			# connect to activate pointer 
			cfg.ui.LCS_pointerButton.clicked.connect(cfg.LCSignT.pointerActive)
			cfg.ui.LCS_ROI_button.clicked.connect(cfg.LCSignT.ROIThreshold)
			cfg.ui.set_min_max_Button.clicked.connect(cfg.LCSignT.setMinimumMaximum)
			# connect the include signature checkBox
			cfg.ui.LCS_include_checkBox.stateChanged.connect(cfg.LCSignT.includeCheckbox)
			cfg.ui.LCS_cut_checkBox.stateChanged.connect(cfg.LCSignT.cutCheckbox)
			# add to spectral signature plot
			cfg.ui.signature_spectral_plot_toolButton_2.clicked.connect(cfg.LCSignT.addSignatureToSpectralPlot)
			""" RGB List tab """
			cfg.ui.RGB_tableWidget.cellChanged.connect(cfg.RGBLT.editedTable)
			cfg.ui.add_RGB_pushButton.clicked.connect(cfg.RGBLT.addRGBToTable)
			cfg.ui.remove_RGB_toolButton.clicked.connect(cfg.RGBLT.removeRGBFromTable)
			cfg.ui.sort_by_name_toolButton_2.clicked.connect(cfg.RGBLT.sortRGBName)
			cfg.ui.clear_RGB_list_toolButton.clicked.connect(cfg.RGBLT.clearTableAction)
			cfg.ui.move_up_toolButton_3.clicked.connect(cfg.RGBLT.moveUpRGB)
			cfg.ui.move_down_toolButton_3.clicked.connect(cfg.RGBLT.moveDownRGB)
			cfg.ui.all_RGB_list_toolButton.clicked.connect(cfg.RGBLT.allRGBListAction)
			cfg.ui.export_RGB_List_toolButton.clicked.connect(cfg.RGBLT.exportRGBList)
			cfg.ui.import_RGB_List_toolButton.clicked.connect(cfg.RGBLT.importRGB)
			""" Download product tab """
			# connect to find images button
			cfg.ui.find_images_toolButton.clicked.connect(cfg.downProd.findImages)
			cfg.ui.selectUL_toolButton_3.clicked.connect(cfg.downProd.pointerActive)
			# connect to display button
			cfg.ui.toolButton_display.clicked.connect(cfg.downProd.displayImages)
			cfg.ui.toolButton_OSM.clicked.connect(cfg.downProd.displayOSM)
			cfg.ui.remove_image_toolButton.clicked.connect(cfg.downProd.removeImageFromTable)
			cfg.ui.clear_table_toolButton.clicked.connect(cfg.downProd.clearTable)
			cfg.ui.download_images_Button.clicked.connect(cfg.downProd.downloadImages)
			cfg.ui.export_links_Button.clicked.connect(cfg.downProd.exportLinks)
			cfg.ui.import_table_pushButton.clicked.connect(cfg.downProd.importTableText)
			cfg.ui.export_table_pushButton.clicked.connect(cfg.downProd.exportTableText)
			cfg.ui.check_toolButton.clicked.connect(cfg.downProd.checkAllBands)
			cfg.ui.show_area_radioButton_2.clicked.connect(cfg.downProd.showHideArea)
			cfg.ui.remember_user_checkBox_2.stateChanged.connect(cfg.downProd.rememberUserCheckbox)
			cfg.ui.user_usgs_lineEdit.editingFinished.connect(cfg.downProd.rememberUser)
			cfg.ui.password_usgs_lineEdit.editingFinished.connect(cfg.downProd.rememberUser)
			cfg.ui.reset_sentinel_service_toolButton.clicked.connect(cfg.downProd.resetService)
			cfg.ui.remember_user_checkBox.stateChanged.connect(cfg.downProd.rememberUserCheckboxSentinel2)
			cfg.ui.user_scihub_lineEdit.editingFinished.connect(cfg.downProd.rememberUserSentinel2)
			cfg.ui.password_scihub_lineEdit.editingFinished.connect(cfg.downProd.rememberUserSentinel2)
			cfg.ui.sentinel_service_lineEdit.editingFinished.connect(cfg.downProd.rememberService)
			cfg.ui.check_toolButton_2.clicked.connect(cfg.downProd.checkAllBandsSentinel2)
			cfg.ui.check_toolButton_3.clicked.connect(cfg.downProd.checkAllBandsSentinel3)
			cfg.ui.remember_user_checkBox_3.stateChanged.connect(cfg.downProd.rememberUserCheckboxEarthdata)
			cfg.ui.user_usgs_lineEdit_2.editingFinished.connect(cfg.downProd.rememberUserEarthdata)
			cfg.ui.password_usgs_lineEdit_2.editingFinished.connect(cfg.downProd.rememberUserEarthdata)
			cfg.ui.download_images_tableWidget.itemSelectionChanged.connect(cfg.downProd.tableClick)
			""" Classification dock """
			# button band set
			cfg.uidc.bandset_toolButton.clicked.connect(cfg.utls.bandSetTab)
			cfg.uidc.band_processing_toolButton.clicked.connect(cfg.utls.bandProcessingTab)
			cfg.uidc.preprocessing_toolButton_2.clicked.connect(cfg.utls.preProcessingTab)
			cfg.uidc.postprocessing_toolButton_2.clicked.connect(cfg.utls.postProcessingTab)
			cfg.uidc.bandcalc_toolButton_2.clicked.connect(cfg.utls.bandCalcTab)
			cfg.uidc.download_images_toolButton_2.clicked.connect(cfg.utls.selectTabDownloadImages)
			cfg.uidc.basic_tools_toolButton.clicked.connect(cfg.utls.basicToolsTab)
			cfg.uidc.batch_toolButton.clicked.connect(cfg.utls.batchTab)
			cfg.uidc.userguide_toolButton_2.clicked.connect(cfg.ipt.quickGuide)
			cfg.uidc.help_toolButton_2.clicked.connect(cfg.ipt.askHelp)
			cfg.uidc.support_toolButton.clicked.connect(cfg.ipt.supportSCP)
			cfg.uidc.tabWidget_dock.currentChanged.connect(cfg.ipt.dockTabChanged)
			# button new shapefile
			cfg.uidc.button_new_input.clicked.connect(cfg.SCPD.createInput)
			# connect to save to shapefile 
			cfg.uidc.button_Save_ROI.clicked.connect(cfg.SCPD.saveROItoShapefile)
			# connect to undo save ROI 
			cfg.uidc.undo_save_Button.clicked.connect(cfg.SCPD.undoSaveROI)
			# connect the signature calculation checkBox
			cfg.uidc.signature_checkBox.stateChanged.connect(cfg.SCPD.signatureCheckbox)
			cfg.uidc.scatterPlot_toolButton.clicked.connect(cfg.SCPD.addROIToScatterPlot)
			# connect the save input checkBox
			cfg.uidc.save_input_checkBox.stateChanged.connect(cfg.SCPD.saveInputCheckbox)
			# connect to open training shapefile
			cfg.uidc.trainingFile_toolButton.clicked.connect(cfg.SCPD.openTrainingFile)
			# connect to export signature list file
			cfg.uidc.export_signature_list_toolButton.clicked.connect(cfg.utls.exportLibraryTab)
			# connect to import library file
			cfg.uidc.import_library_toolButton.clicked.connect(cfg.utls.importLibraryTab)
			# add to spectral signature plot
			cfg.uidc.signature_spectral_plot_toolButton.clicked.connect(cfg.SCPD.addSignatureToSpectralPlot)
			# connect to edited cell
			cfg.uidc.signature_list_tableWidget.cellChanged.connect(cfg.SCPD.editedCell)
			# connect to signature list double click
			cfg.uidc.signature_list_tableWidget.doubleClicked.connect(cfg.SCPD.signatureListDoubleClick)
			# connect to delete signature
			cfg.uidc.delete_Signature_Button.clicked.connect(cfg.SCPD.removeSelectedSignatures)
			# connect to merge signatures
			cfg.uidc.merge_signature_toolButton.clicked.connect(cfg.SCPD.mergeSelectedSignatures)
			cfg.uidc.calculate_signature_toolButton.clicked.connect(cfg.SCPD.calculateSignatures)
			# connect the ROI macroclass ID	
			cfg.uidc.ROI_Macroclass_ID_spin.valueChanged.connect(cfg.SCPD.setROIMacroID)
			# connect the ROI Macroclass 
			cfg.uidc.ROI_Macroclass_line.editingFinished.connect(cfg.SCPD.roiMacroclassInfo)
			# custom expression
			cfg.uidc.custom_index_lineEdit.editingFinished.connect(cfg.SCPD.customExpressionEdited)
			# connect the ROI Class ID
			cfg.uidc.ROI_ID_spin.valueChanged.connect(cfg.SCPD.setROIID)
			# connect the ROI Class 
			cfg.uidc.ROI_Class_line.editingFinished.connect(cfg.SCPD.roiClassInfo)
			# connect the rapid ROI checkBox
			cfg.uidc.display_cursor_checkBox.stateChanged.connect(cfg.SCPD.vegetationIndexCheckbox)
			# connect the vegetation index combo	
			cfg.uidc.vegetation_index_comboBox.currentIndexChanged.connect(cfg.SCPD.vegetationIndexName)
			# connect the rapid ROI checkBox
			cfg.uidc.rapid_ROI_checkBox.stateChanged.connect(cfg.SCPD.rapidROICheckbox)
			# connect the vegetation index display checkbox
			cfg.uidc.rapidROI_band_spinBox.valueChanged.connect(cfg.SCPD.rapidROIband)
			# connect to algorithm weight button 
			cfg.uidc.algorithm_weight_button.clicked.connect(cfg.utls.algorithmWeighTab)
			# connect to threshold button 
			cfg.uidc.algorithm_threshold_button.clicked.connect(cfg.utls.algorithmThresholdTab)
			# connect to LCS threshold button 
			cfg.uidc.LC_signature_button.clicked.connect(cfg.utls.LCSThresholdTab)
			# connect the algorithm combo	
			cfg.uidc.algorithm_combo.currentIndexChanged.connect(cfg.SCPD.algorithmName)
			# connect the algorithm threshold
			cfg.uidc.alg_threshold_SpinBox.valueChanged.connect(cfg.SCPD.algorithmThreshold)
			# connect to edited cell
			cfg.uidc.macroclass_color_tableWidget.cellChanged.connect(cfg.SCPD.McIdEditedCell)
			# connect to MC ID double click
			cfg.uidc.macroclass_color_tableWidget.doubleClicked.connect(cfg.SCPD.McIdDoubleClick)
			# connect to add row
			cfg.uidc.add_MC_row_Button.clicked.connect(cfg.SCPD.addMCIDToTable)
			cfg.uidc.delete_MC_row_Button.clicked.connect(cfg.SCPD.removeMCIDFromTable)
			# connect to run classification
			cfg.uidc.button_classification.clicked.connect(cfg.SCPD.runClassificationAction)
			# connect the alg files checkBox
			cfg.uidc.alg_files_checkBox.stateChanged.connect(cfg.sets.algFilesCheckbox)
			# connect the vector output checkBox
			cfg.uidc.vector_output_checkBox.stateChanged.connect(cfg.SCPD.vectorCheckbox)
			# connect the macroclass checkBox
			cfg.uidc.macroclass_checkBox.stateChanged.connect(cfg.SCPD.macroclassCheckbox)
			cfg.uidc.class_checkBox.stateChanged.connect(cfg.SCPD.classCheckbox)
			# connect the LC signature checkBox
			cfg.uidc.LC_signature_checkBox.stateChanged.connect(cfg.SCPD.LCSignature_Checkbox)
			# connect the report checkBox
			cfg.uidc.report_checkBox.stateChanged.connect(cfg.SCPD.reportCheckbox)
			# connect the mask checkBox
			cfg.uidc.mask_checkBox.stateChanged.connect(cfg.SCPD.maskCheckbox)
			# connect to reset qml button
			cfg.uidc.resetQmlButton.clicked.connect(cfg.SCPD.resetQmlStyle)
			# connect to reset mask button
			cfg.uidc.resetMaskButton.clicked.connect(cfg.SCPD.resetMask)
			# connect to qml button
			cfg.uidc.qml_Button.clicked.connect(cfg.SCPD.selectQmlStyle)
			""" Spectral signature plot """	
			# connect the sigma checkBox
			cfg.uisp.sigma_checkBox.stateChanged.connect(cfg.spSigPlot.sigmaCheckbox)
			cfg.uisp.band_lines_checkBox.stateChanged.connect(cfg.spSigPlot.refreshPlot)
			cfg.uisp.grid_checkBox.stateChanged.connect(cfg.spSigPlot.refreshPlot)
			# connect to remove signature button
			cfg.uisp.remove_Signature_Button.clicked.connect(cfg.spSigPlot.removeSignature)
			# connect to calculate spectral distances button
			cfg.uisp.calculate_spectral_distance_Button.clicked.connect(cfg.spSigPlot.calculateSpectralDistances)
			# connect to fit to axes
			cfg.uisp.fitToAxes_pushButton.clicked.connect(cfg.spSigPlot.fitPlotToAxes)
			# connect to plot spinbox
			cfg.uisp.plot_text_spinBox.valueChanged.connect(cfg.spSigPlot.setPlotLegendLenght)
			# connect to value range
			cfg.uisp.value_range_pushButton.clicked.connect(cfg.spSigPlot.editValueRange)
			cfg.uisp.set_min_max_Button.clicked.connect(cfg.spSigPlot.setMinimumMaximum)
			cfg.uisp.automatic_threshold_pushButton_2.clicked.connect(cfg.spSigPlot.setAllWeightsVariance)
			# connect to activate pointer 
			cfg.uisp.LCS_pointerButton_2.clicked.connect(cfg.spSigPlot.pointerActive)
			cfg.uisp.LCS_ROI_button_2.clicked.connect(cfg.spSigPlot.ROIThreshold)
			# undo threshold
			cfg.uisp.undo_threshold_Button.clicked.connect(cfg.spSigPlot.undoThreshold)
			# connect the include signature checkBox
			cfg.uisp.LCS_include_checkBox_2.stateChanged.connect(cfg.spSigPlot.includeCheckbox)
			cfg.uisp.LCS_cut_checkBox_2.stateChanged.connect(cfg.spSigPlot.cutCheckbox)
			# connect to add to signature list
			cfg.uisp.add_signature_list_pushButton.clicked.connect(cfg.spSigPlot.addToSignatureList)
			# connect to save plot
			cfg.uisp.save_plot_pushButton.clicked.connect(cfg.spSigPlot.savePlot)
			# connect to edited cell
			cfg.uisp.signature_list_plot_tableWidget.cellChanged.connect(cfg.spSigPlot.editedCell)
			cfg.uisp.signature_list_plot_tableWidget.horizontalHeader().sectionClicked.connect(cfg.spSigPlot.orderedTable)
			# connect to signature plot list double click
			cfg.uisp.signature_list_plot_tableWidget.doubleClicked.connect(cfg.spSigPlot.signatureListDoubleClick)
			""" Scatter plot tab """
			# connect to scatter plot button 
			cfg.uiscp.scatter_ROI_Button.clicked.connect(cfg.scaPlT.scatterPlotCalc)
			# connect to Band X spinbox
			cfg.uiscp.bandX_spinBox.valueChanged.connect(cfg.scaPlT.bandXPlot)
			# connect to Band Y spinbox
			cfg.uiscp.bandY_spinBox.valueChanged.connect(cfg.scaPlT.bandYPlot)
			# connect double click ROI list to zoom
			cfg.uiscp.scatter_list_plot_tableWidget.doubleClicked.connect(cfg.scaPlT.scatterPlotDoubleClick)
			# connect to edited cell
			cfg.uiscp.scatter_list_plot_tableWidget.cellChanged.connect(cfg.scaPlT.editedCell)
			# connect to remove signature button
			cfg.uiscp.remove_Signature_Button.clicked.connect(cfg.scaPlT.removeScatter)
			# connect to save plot
			cfg.uiscp.save_plot_pushButton_2.clicked.connect(cfg.scaPlT.savePlot)
			# connect to fit to axes
			cfg.uiscp.fitToAxes_pushButton_2.clicked.connect(cfg.scaPlT.fitPlotToAxes)
			cfg.uiscp.plot_temp_ROI_pushButton.clicked.connect(cfg.scaPlT.addTempROIToScatterPlot)
			cfg.uiscp.plot_display_pushButton.clicked.connect(cfg.scaPlT.addDisplayToScatterPlot)
			cfg.uiscp.plot_image_pushButton.clicked.connect(cfg.scaPlT.addImageToScatterPlot)
			# connect to change color button
			cfg.uiscp.polygon_color_Button.clicked.connect(cfg.scaPlT.changePolygonColor)
			cfg.uiscp.plot_color_ROI_pushButton.clicked.connect(cfg.scaPlT.colorPlot)
			# connect to select value range
			cfg.uiscp.draw_polygons_pushButton.clicked.connect(cfg.scaPlT.selectRange)
			cfg.uiscp.remove_polygons_pushButton.clicked.connect(cfg.scaPlT.removePolygons)
			cfg.uiscp.show_polygon_area_pushButton.clicked.connect(cfg.scaPlT.showScatterPolygonArea)
			cfg.uiscp.add_signature_list_pushButton.clicked.connect(cfg.scaPlT.addToSignatureList)
			""" Band set tab """
			# connect to refresh button
			cfg.ui.toolButton_reload_3.clicked.connect(cfg.bst.rasterBandName)
			# button reload
			cfg.ui.toolButton_reload.clicked.connect(cfg.ipt.checkRefreshRasterLayer)
			# connect to add file button
			cfg.ui.toolButton_input_raster.clicked.connect(cfg.bst.addFileToBandSetAction)
			# connect to add raster band button
			cfg.ui.add_raster_bands_Button.clicked.connect(cfg.bst.addBandToSet)
			# connect to select all bands button
			cfg.ui.select_all_bands_Button.clicked.connect(cfg.bst.selectAllBands)
			# connect to clear band set button
			cfg.ui.clear_bandset_toolButton.clicked.connect(cfg.bst.clearBandSetAction)
			# connect to move up band button
			cfg.ui.move_up_toolButton.clicked.connect(cfg.bst.moveUpBand)
			# connect to move down band button
			cfg.ui.move_down_toolButton.clicked.connect(cfg.bst.moveDownBand)
			# connect to sort by name button
			cfg.ui.sort_by_name_toolButton.clicked.connect(cfg.bst.sortBandName)
			# connect to remove band button
			cfg.ui.remove_toolButton.clicked.connect(cfg.bst.removeBand)
			# connect add band set
			cfg.ui.add_band_set_toolButton.clicked.connect(cfg.bst.addBandSetTabAction)
			# connect to changed tab
			cfg.ui.Band_set_tabWidget.currentChanged.connect(cfg.bst.tabBandSetChanged)
			# connect close tab
			cfg.ui.Band_set_tabWidget.tabCloseRequested.connect(cfg.bst.closeBandSetTab)
			# combo layer
			cfg.ui.image_raster_name_combo.currentIndexChanged.connect(cfg.bst.rasterLayerName)
			# connect to import band set button
			cfg.ui.import_bandset_toolButton.clicked.connect(cfg.bst.importBandSet)
			# connect to export band set button
			cfg.ui.export_bandset_toolButton.clicked.connect(cfg.bst.exportBandSet)
			# connect to satellite wavelength combo
			cfg.ui.wavelength_sat_combo.currentIndexChanged.connect(cfg.bst.satelliteWavelength)
			# connect to unit combo
			cfg.ui.unit_combo.currentIndexChanged.connect(cfg.bst.setBandUnit)
			# connect to band set processs button
			cfg.ui.band_set_process_toolButton.clicked.connect(cfg.bst.performBandSetTools)
			""" Pre processing tab """
			""" Clip multiple rasters """
			# connect to clip button
			cfg.ui.clip_Button.clicked.connect(cfg.clipMulti.clipRastersAction)
			# connect to activate UL pointer 
			cfg.ui.selectUL_toolButton.clicked.connect(cfg.clipMulti.pointerActive)
			# connect to refresh shape button
			cfg.ui.toolButton_reload_8.clicked.connect(cfg.clipMulti.refreshShapeClip)
			cfg.ui.show_area_radioButton_3.clicked.connect(cfg.clipMulti.showHideArea)
			cfg.ui.shapefile_checkBox.stateChanged.connect(cfg.clipMulti.checkboxShapeChanged)
			cfg.ui.temporary_ROI_checkBox.stateChanged.connect(cfg.clipMulti.checkboxTempROIChanged)
			# connect the shapefile combo
			cfg.ui.shapefile_comboBox.currentIndexChanged.connect(cfg.clipMulti.referenceLayerName)
			""" Stack raster bands """
			# connect to stack button
			cfg.ui.stack_Button.clicked.connect(cfg.stackRstr.stackAction)
			""" Spectral change band sets """
			# connect to calculate button
			cfg.ui.spectral_distance_bandsets_toolButton.clicked.connect(cfg.spclDstBS.calculateDistanceAction)			
			cfg.ui.min_distance_radioButton_2.clicked.connect(cfg.spclDstBS.radioMinDistChanged)			
			cfg.ui.spectral_angle_map_radioButton_2.clicked.connect(cfg.spclDstBS.radioSAMChanged)
			""" Mosaic band sets """
			# connect to mosaic button
			cfg.ui.mosaic_bandsets_toolButton.clicked.connect(cfg.mosaicBS.mosaicAction)
			cfg.ui.mosaic_band_sets_lineEdit.textChanged.connect(cfg.mosaicBS.textChanged)
			""" Cloud masking """
			# connect to mask button
			cfg.ui.cloud_mask_toolButton.clicked.connect(cfg.cloudMsk.maskAction)
			cfg.ui.cloud_mask_classes_lineEdit.textChanged.connect(cfg.cloudMsk.textChanged)
			# connect to refresh button
			cfg.ui.toolButton_reload_23.clicked.connect(cfg.utls.refreshClassificationLayer)			
			""" ASTER tab """
			# connect to input button
			cfg.ui.toolButton_directoryInput_ASTER.clicked.connect(cfg.ASTERT.inputASTER)
			cfg.ui.ASTER_tableWidget.cellChanged.connect(cfg.ASTERT.editedCell)
			cfg.ui.earth_sun_dist_lineEdit_2.textChanged.connect(cfg.ASTERT.editedEarthSunDist)
			cfg.ui.sun_elev_lineEdit_2.textChanged.connect(cfg.ASTERT.editedSunElevation)
			cfg.ui.date_lineEdit_2.textChanged.connect(cfg.ASTERT.editedDate)
			cfg.ui.pushButton_Conversion_3.clicked.connect(cfg.ASTERT.performASTERCorrection)
			cfg.ui.pushButton_remove_band_2.clicked.connect(cfg.ASTERT.removeHighlightedBand)
			""" MODIS tab """
			# connect to input button
			cfg.ui.toolButton_directoryInput_MODIS.clicked.connect(cfg.MODIST.inputMODIS)
			cfg.ui.MODIS_tableWidget.cellChanged.connect(cfg.MODIST.editedCell)
			cfg.ui.pushButton_Conversion_4.clicked.connect(cfg.MODIST.performMODISConversion)
			cfg.ui.pushButton_remove_band_3.clicked.connect(cfg.MODIST.removeHighlightedBand)
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
			""" Sentinel-2 tab """
			# connect to input button
			cfg.ui.S2_toolButton_directoryInput.clicked.connect(cfg.sentinel2T.inputSentinel)
			cfg.ui.pushButton_Conversion_2.clicked.connect(cfg.sentinel2T.performSentinelConversion)
			cfg.ui.S2_satellite_lineEdit.textChanged.connect(cfg.sentinel2T.editedSatellite)
			cfg.ui.S2_pushButton_remove_band.clicked.connect(cfg.sentinel2T.removeHighlightedBand)
			cfg.ui.sentinel_2_tableWidget.cellChanged.connect(cfg.sentinel2T.editedCell)
			cfg.ui.S2_toolButton_directoryInput_xml2.clicked.connect(cfg.sentinel2T.inputXML2)
			""" Sentinel-3 tab """
			# connect to input button
			cfg.ui.S3_toolButton_directoryInput.clicked.connect(cfg.sentinel3T.inputSentinel)
			cfg.ui.pushButton_Conversion_5.clicked.connect(cfg.sentinel3T.performSentinelConversion)
			cfg.ui.S3_pushButton_remove_band.clicked.connect(cfg.sentinel3T.removeHighlightedBand)
			""" Split tab """
			# connect the classification combo
			cfg.ui.raster_name_combo.currentIndexChanged.connect(cfg.splitT.rasterLayerName)
			# connect to refresh button
			cfg.ui.toolButton_reload_9.clicked.connect(cfg.splitT.refreshClassificationLayer)
			# connect to split raster button
			cfg.ui.split_Button.clicked.connect(cfg.splitT.splitRaster)
			""" PCA tab """
			# connect to PCA button
			cfg.ui.pca_Button.clicked.connect(cfg.pcaT.calculatePCAAction)
			""" K-means tab """
			# connect to kmeans button
			cfg.ui.kmeans_Button.clicked.connect(cfg.clusteringT.calculateClusteringAction)
			# connect the algorithm combo
			cfg.ui.kmean_minmax_radioButton.clicked.connect(cfg.clusteringT.radiokmean_minmaxChanged)
			cfg.ui.kmean_siglist_radioButton.clicked.connect(cfg.clusteringT.radiokmean_siglistChanged)
			cfg.ui.kmean_randomsiglist_radioButton.clicked.connect(cfg.clusteringT.radiokmean_randomsiglistChanged)			
			cfg.ui.kmeans_radioButton.clicked.connect(cfg.clusteringT.radioKmeansChanged)			
			cfg.ui.isodata_radioButton.clicked.connect(cfg.clusteringT.radioIsodataChanged)					
			cfg.ui.min_distance_radioButton.clicked.connect(cfg.clusteringT.radioMinDistChanged)			
			cfg.ui.spectral_angle_map_radioButton.clicked.connect(cfg.clusteringT.radioSAMChanged)			
			""" Vector to Raster tab """
			cfg.ui.toolButton_reload_16.clicked.connect(cfg.vctRstrT.reloadVectorList)
			cfg.ui.toolButton_reload_17.clicked.connect(cfg.utls.refreshClassificationLayer)
			cfg.ui.convert_vector_toolButton.clicked.connect(cfg.vctRstrT.convertToRasterAction)
			cfg.ui.vector_name_combo.currentIndexChanged.connect(cfg.utls.refreshVectorFields)
			cfg.ui.field_checkBox.stateChanged.connect(cfg.vctRstrT.checkboxFieldChanged)
			cfg.ui.constant_value_checkBox.stateChanged.connect(cfg.vctRstrT.checkboxConstantValueChanged)
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
			cfg.ui.calculateLandCoverChange_toolButton.clicked.connect(cfg.landCC.landCoverChangeAction)
			""" Classification report """
			# connect to refresh button
			cfg.ui.toolButton_reload_10.clicked.connect(cfg.utls.refreshClassificationLayer)
			# connect to calculate button
			cfg.ui.calculateReport_toolButton.clicked.connect(cfg.classRep.calculateClassReport)
			""" Band set combination tab """
			# connect to calculate button
			cfg.ui.calculateBandSetComb_toolButton.clicked.connect(cfg.bsComb.calculateBandSetCombination)
			""" Cross classification tab """
			# connect the classification combo
			cfg.ui.classification_name_combo_2.currentIndexChanged.connect(cfg.crossC.classificationLayerName)
			# connect to refresh button
			cfg.ui.toolButton_reload_21.clicked.connect(cfg.utls.refreshClassificationLayer)
			# connect the reference combo
			cfg.ui.reference_name_combo_2.currentIndexChanged.connect(cfg.crossC.referenceLayerName)
			# connect to refresh button
			cfg.ui.buttonReload_shape_5.clicked.connect(cfg.crossC.refreshReferenceLayer)
			# connect to calculate error matrix button
			cfg.ui.calculatecrossClass_toolButton.clicked.connect(cfg.crossC.calculateCrossClassification)
			""" Class signature """
			# connect to calculate signature
			cfg.ui.class_signature_Button.clicked.connect(cfg.classSigT.calculateClassSignatureAction)
			# connect to refresh button
			cfg.ui.toolButton_reload_22.clicked.connect(cfg.utls.refreshClassificationLayer)
			""" Classification to vector """
			# connect to refresh button
			cfg.ui.toolButton_reload_12.clicked.connect(cfg.utls.refreshClassificationLayer)
			# connect to convert button
			cfg.ui.convert_toolButton.clicked.connect(cfg.classVect.convertClassificationToVectorAction)
			""" Reclassification """
			# connect to refresh button
			cfg.ui.toolButton_reload_11.clicked.connect(cfg.utls.refreshClassificationLayer)
			# connect to reclassify button
			cfg.ui.reclassify_toolButton.clicked.connect(cfg.reclassification.reclassifyAction)
			# connect to calculate unique values button
			cfg.ui.calculate_unique_values_toolButton.clicked.connect(cfg.reclassification.calculateUniqueValues)
			# connect to add value button
			cfg.ui.add_value_pushButton.clicked.connect(cfg.reclassification.addRowToTable)
			# connect to remove point
			cfg.ui.remove_row_pushButton.clicked.connect(cfg.reclassification.removePointFromTable)
			# connect to edited cell
			cfg.ui.reclass_values_tableWidget.cellChanged.connect(cfg.reclassification.editedCell)
			""" Edit Raster tab"""
			# connect to set value
			cfg.ui.raster_set_value_toolButton.clicked.connect(cfg.editRstr.setRasterValueAction)
			# connect to refresh rasters button
			cfg.ui.toolButton_reload_14.clicked.connect(cfg.utls.refreshClassificationLayer)
			cfg.ui.undo_edit_Button.clicked.connect(cfg.editRstr.undoEdit)
			# connect the expression text
			cfg.ui.expression_lineEdit.textChanged.connect(cfg.editRstr.textChanged)
			cfg.ui.use_constant_val_checkBox.stateChanged.connect(cfg.editRstr.checkboxConstantValChanged)
			cfg.ui.use_field_vector_checkBox.stateChanged.connect(cfg.editRstr.checkboxVectorFieldChanged)
			cfg.ui.use_expression_checkBox.stateChanged.connect(cfg.editRstr.checkboxUseExpressionChanged)
			cfg.ui.edit_val_use_ROI_radioButton.clicked.connect(cfg.editRstr.radioUseROIPolygonChanged)
			cfg.ui.edit_val_use_vector_radioButton.clicked.connect(cfg.editRstr.radioUseVectorChanged)
			cfg.ui.toolButton_reload_20.clicked.connect(cfg.editRstr.reloadVectorList)
			cfg.ui.vector_name_combo_2.currentIndexChanged.connect(cfg.utls.refreshVectorFields2)
			""" Classification sieve tab"""
			# connect to refresh rasters button
			cfg.ui.toolButton_reload_15.clicked.connect(cfg.utls.refreshClassificationLayer)
			cfg.ui.sieve_toolButton.clicked.connect(cfg.sieveRstr.sieveClassificationAction)
			""" Classification erosion tab"""
			# connect to refresh rasters button
			cfg.ui.toolButton_reload_18.clicked.connect(cfg.utls.refreshClassificationLayer)
			cfg.ui.class_erosion_toolButton.clicked.connect(cfg.ersnRstr.erosionClassificationAction)
			# connect the value text
			cfg.ui.erosion_classes_lineEdit.textChanged.connect(cfg.ersnRstr.textChanged)
			""" Classification dilation tab"""
			# connect to refresh rasters button
			cfg.ui.toolButton_reload_19.clicked.connect(cfg.utls.refreshClassificationLayer)
			cfg.ui.class_dilation_toolButton.clicked.connect(cfg.dltnRstr.dilationClassificationAction)
			# connect the value text
			cfg.ui.dilation_classes_lineEdit.textChanged.connect(cfg.dltnRstr.textChanged)
			""" Band Calc tab """
			# connect to refresh button
			cfg.ui.toolButton_reload_13.clicked.connect(cfg.bCalc.rasterBandName)
			# connect to calc button
			cfg.ui.toolButton_calculate.clicked.connect(cfg.bCalc.calculateButton)
			# connect to import expression button
			cfg.ui.toolButton_import_expression.clicked.connect(cfg.bCalc.importExpressionList)
			# connect the expression text
			cfg.ui.plainTextEdit_calc.textChanged.connect(cfg.bCalc.textChanged)
			# connect double click table
			cfg.ui.tableWidget_band_calc.doubleClicked.connect(cfg.bCalc.doubleClick)
			# connect the intersection checkBox
			cfg.ui.intersection_checkBox.stateChanged.connect(cfg.bCalc.intersectionCheckbox)
			# connect the extent checkBox
			cfg.ui.extent_checkBox.stateChanged.connect(cfg.bCalc.extentCheckbox)
			# connect to indices combo
			cfg.ui.band_set_calculation_combo.currentIndexChanged.connect(cfg.bCalc.setIndices)
			# connect to expression buttons
			cfg.ui.toolButton_plus.clicked.connect(cfg.bCalc.buttonPlus)
			cfg.ui.toolButton_minus.clicked.connect(cfg.bCalc.buttonMinus)
			cfg.ui.toolButton_product.clicked.connect(cfg.bCalc.buttonProduct)
			cfg.ui.toolButton_ratio.clicked.connect(cfg.bCalc.buttonRatio)
			cfg.ui.toolButton_power.clicked.connect(cfg.bCalc.buttonPower)
			cfg.ui.toolButton_sqrt.clicked.connect(cfg.bCalc.buttonSQRT)
			cfg.ui.toolButton_lbracket.clicked.connect(cfg.bCalc.buttonLbracket)
			cfg.ui.toolButton_rbracket.clicked.connect(cfg.bCalc.buttonRbracket)
			cfg.ui.toolButton_greater.clicked.connect(cfg.bCalc.buttonGreater)
			cfg.ui.toolButton_less.clicked.connect(cfg.bCalc.buttonLower)
			cfg.ui.toolButton_equal.clicked.connect(cfg.bCalc.buttonEqual)
			cfg.ui.toolButton_unequal.clicked.connect(cfg.bCalc.buttonUnequal)
			cfg.ui.toolButton_sin.clicked.connect(cfg.bCalc.buttonSin)
			cfg.ui.toolButton_asin.clicked.connect(cfg.bCalc.buttonASin)
			cfg.ui.toolButton_cos.clicked.connect(cfg.bCalc.buttonCos)
			cfg.ui.toolButton_acos.clicked.connect(cfg.bCalc.buttonACos)
			cfg.ui.toolButton_tan.clicked.connect(cfg.bCalc.buttonTan)
			cfg.ui.toolButton_atan.clicked.connect(cfg.bCalc.buttonATan)
			cfg.ui.toolButton_exponential.clicked.connect(cfg.bCalc.buttonExp)
			cfg.ui.toolButton_noDataVal.clicked.connect(cfg.bCalc.buttonNoDataVal)
			cfg.ui.toolButton_npWhere.clicked.connect(cfg.bCalc.buttonNpWhere)
			cfg.ui.toolButton_log.clicked.connect(cfg.bCalc.buttonLog)
			cfg.ui.toolButton_pi.clicked.connect(cfg.bCalc.buttonPi)
			# decision rules
			cfg.ui.decision_rules_tableWidget.cellChanged.connect(cfg.bCalc.editedDecisionRulesTable)
			cfg.ui.band_calc_tabWidget.currentChanged.connect(cfg.bCalc.tabChanged)
			# connect to add rule
			cfg.ui.add_rule_toolButton.clicked.connect(cfg.bCalc.addRowToTable)
			cfg.ui.remove_rule_toolButton.clicked.connect(cfg.bCalc.removeHighlightedRule)
			# connect to clear button
			cfg.ui.clear_rules_toolButton.clicked.connect(cfg.bCalc.clearRulesAction)
			cfg.ui.export_rules_toolButton.clicked.connect(cfg.bCalc.exportRules)
			cfg.ui.import_rules_toolButton.clicked.connect(cfg.bCalc.importRules)
			cfg.ui.move_up_toolButton_2.clicked.connect(cfg.bCalc.moveUpRule)
			cfg.ui.move_down_toolButton_2.clicked.connect(cfg.bCalc.moveDownRule)
			""" Batch tab """
			# connect the batch text
			cfg.ui.plainTextEdit_batch.textChanged.connect(cfg.batchT.textChanged)
			# connect to calc button
			cfg.ui.toolButton_run_batch.clicked.connect(cfg.batchT.runButton)
			cfg.ui.clear_batch_toolButton.clicked.connect(cfg.batchT.clearBatch)
			cfg.ui.export_batch_toolButton.clicked.connect(cfg.batchT.exportBatch)
			cfg.ui.import_batch_toolButton.clicked.connect(cfg.batchT.importBatch)
			# connect to signature list double click
			cfg.ui.batch_tableWidget.doubleClicked.connect(cfg.batchT.setFunction)
			cfg.ui.menu_tableWidget.itemSelectionChanged.connect(cfg.ipt.menuIndex)
			cfg.ui.menu_tableWidget.clicked.connect(cfg.ipt.menuClicked)
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
			# connect the SMTP line
			cfg.ui.smtp_server_lineEdit.textChanged.connect(cfg.sets.SMTPServerChange)
			# connect the SMTP to emails line
			cfg.ui.to_email_lineEdit.textChanged.connect(cfg.sets.SMTPtoEmailsChange)
			# connect the SMTP user
			cfg.ui.smtp_user_lineEdit.editingFinished.connect(cfg.sets.rememberUser)
			# connect the SMTP password
			cfg.ui.smtp_password_lineEdit.editingFinished.connect(cfg.sets.rememberUser)
			# connect the SMTP checkbox
			cfg.ui.remeber_settings_checkBox.stateChanged.connect(cfg.sets.rememberUserCheckbox)	
			# connect the SMTP checkBox
			cfg.ui.smtp_checkBox.stateChanged.connect(cfg.sets.SMTPCheckbox)		
			# connect to reset field names button
			cfg.ui.reset_field_names_Button.clicked.connect(cfg.sets.resetFieldNames)
			# connect to reset variable name button
			cfg.ui.reset_variable_name_Button.clicked.connect(cfg.sets.resetVariableName)
			# connect to reset group name button
			cfg.ui.reset_group_name_Button.clicked.connect(cfg.sets.resetGroupName)
			# connect the log file checkBox
			cfg.ui.log_checkBox.stateChanged.connect(cfg.sets.logCheckbox)
			# connect the download news checkBox
			cfg.ui.download_news_checkBox.stateChanged.connect(cfg.sets.downloadNewsCheckbox)
			# connect the sound checkBox
			cfg.ui.sound_checkBox.stateChanged.connect(cfg.sets.soundCheckbox)
			# connect the virtual raster format checkBox
			cfg.ui.virtual_raster_checkBox.stateChanged.connect(cfg.sets.virtualRasterFormatCheckbox)
			# connect the raster compression checkBox
			cfg.ui.raster_compression_checkBox.stateChanged.connect(cfg.sets.rasterCompressionCheckbox)
			# connect to change temporary directory button
			cfg.ui.temp_directory_Button.clicked.connect(cfg.sets.changeTempDir)
			# connect to reset temporary directory button
			cfg.ui.reset_temp_directory_Button.clicked.connect(cfg.sets.resetTempDir)
			# connect to clear log button
			cfg.ui.clearLog_Button.clicked.connect(cfg.utls.clearLogFile)
			# connect to export log button
			cfg.ui.exportLog_Button.clicked.connect(cfg.sets.copyLogFile)
			# connect to test dependencies button
			cfg.ui.test_dependencies_Button.clicked.connect(cfg.sets.testDependencies)
			# connect to RAM spinbox
			cfg.ui.RAM_spinBox.valueChanged.connect(cfg.sets.RAMSettingChange)
			# connect to change color button
			cfg.ui.change_color_Button.clicked.connect(cfg.sets.changeROIColor)
			# connect to change color button
			cfg.ui.reset_color_Button.clicked.connect(cfg.sets.resetROIStyle)
			# connect to transparency slider
			cfg.ui.transparency_Slider.valueChanged.connect(cfg.sets.changeROITransparency)
			# first install
			if cfg.firstInstallVal == "Yes":
				cfg.utls.welcomeTab()
				cfg.utls.setQGISRegSetting(cfg.regFirstInstall, "No")
				cfg.utls.findAvailableRAM()
			# welcome message
			lWelcome = cfg.plgnDir + "/ui/welcome.html"
			htmlText = open(lWelcome, 'r').read()
			cfg.uidc.main_textBrowser.clear()
			cfg.uidc.main_textBrowser.setHtml(htmlText)
			if cfg.osSCP.path.isfile(cfg.plgnDir + "/firstrun"):
				cfg.ipt.welcomeText("https://semiautomaticgit.github.io/SemiAutomaticClassificationPluginWelcome/changelog.html")
				cfg.osSCP.remove(cfg.plgnDir + "/firstrun")
			else:
				dateV = cfg.datetimeSCP.datetime.now()
				dStr = dateV.strftime("%Y_%m_%d") 
				cfg.ipt.welcomeText("https://semiautomaticgit.github.io/SemiAutomaticClassificationPluginWelcome/welcome" + "_" + dStr + ".html", "https://semiautomaticgit.github.io/SemiAutomaticClassificationPluginWelcome/welcome.html")
			cfg.utls.cleanOldTempDirectory()
			cfg.skipRegistry = False
		else:
			dockclassdlg = DockClassDialog(qgisUtils.iface.mainWindow(), qgisUtils.iface)
			qgisUtils.iface.removeDockWidget(dockclassdlg)			
			
	# save signature list when saving project
	def projectSaved(self):
		if cfg.skipProjectSaved == "No":
			if len(cfg.signIDs) > 0:
				cfg.SCPD.saveSignatureListToFile()
			if cfg.scpFlPath is not None:
				cfg.SCPD.saveMemToSHP(cfg.shpLay)
				cfg.utls.createBackupFile(cfg.scpFlPath)
				cfg.utls.zipDirectoryInFile(cfg.scpFlPath, cfg.inptDir)
			cfg.downProd.saveDownloadTable()
		
	# new project
	def newProjectLoaded(self):
		cfg.projPath = cfg.qgisCoreSCP.QgsProject.instance().fileName()
		cfg.lastSaveDir = cfg.osSCP.path.dirname(cfg.projPath)
		cfg.signList = {}
		cfg.signIDs = {}
		cfg.spectrPlotList = {}
		cfg.signPlotIDs = {}
		cfg.scatterPlotIDs = {}
		cfg.scatterPlotList = {}
		cfg.undoIDList = {}
		cfg.undoSpectrPlotList = {}
		cfg.lstROI = None
		cfg.lstROI2 = None
		cfg.utls.clearTable(cfg.uisp.signature_list_plot_tableWidget)
		cfg.utls.clearTable(cfg.uiscp.scatter_list_plot_tableWidget)
		cfg.utls.clearTable(cfg.ui.signature_threshold_tableWidget)
		cfg.utls.clearTable(cfg.ui.download_images_tableWidget)
		cfg.utls.clearTable(cfg.ui.LCS_tableWidget)
		cfg.scaPlT.scatterPlotListTable(cfg.uiscp.scatter_list_plot_tableWidget)
		cfg.spSigPlot.refreshPlot()
		cfg.LCSignT.LCSignatureThresholdListTable()
		# reload layers in combos
		cfg.ipt.refreshRasterLayer()
		# clear band set
		t = cfg.ui.Band_set_tabWidget.count()
		for index in reversed(list(range(0, t))):
			cfg.bst.deleteBandSetTab(index)
		cfg.bst.addBandSetTab()	
		# signature table
		cfg.utls.clearTable(cfg.uidc.signature_list_tableWidget)
		cfg.utls.clearTable(cfg.uidc.macroclass_color_tableWidget)
		cfg.scpFlPath = None
		cfg.SCPD.openInput()
		cfg.utls.refreshVectorLayer()
		# reload layers in combos
		cfg.utls.refreshClassificationLayer()
		cfg.utls.refreshRasterExtent()
		cfg.acc.refreshReferenceLayer()
		cfg.crossC.refreshReferenceLayer()
		cfg.landCC.refreshClassificationReferenceLayer()
		cfg.landCC.refreshNewClassificationLayer()
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		cfg.bCalc.rasterBandName()
		# rapid ROI band
		cfg.uidc.rapidROI_band_spinBox.setValue(1)
		# min ROI size
		cfg.Min_region_size_spin.setValue(60)
		# max ROI width
		cfg.Max_ROI_width_spin.setValue(100)
		# range radius
		cfg.Range_radius_spin.setValue(0.01)
		# ROI ID field
		cfg.uidc.ROI_ID_spin.setValue(1)
		# ROI macro ID field
		cfg.uidc.ROI_Macroclass_ID_spin.setValue(1)
		# preview size
		cfg.preview_size_spinBox.setValue(float(cfg.prvwSz))
		# ROI info
		cfg.uidc.ROI_Class_line.setText("C 1")
		cfg.uidc.ROI_Macroclass_line.setText("MC 1")
		try:
			cfg.uidc.custom_index_lineEdit.setText("")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# RGB list
		cfg.rgb_combo.clear()
		cfg.rgb_combo.addItem("-")
		cfg.rgb_combo.addItem("3-2-1")
		cfg.rgb_combo.addItem("4-3-2")
		cfg.RGBList = eval(cfg.RGBListDef)
		cfg.RGBLT.RGBListTable(cfg.RGBList)
		
	# read project variables
	def projectLoaded(self):
		cfg.projPath = cfg.qgisCoreSCP.QgsProject.instance().fileName()
		cfg.lastSaveDir = cfg.osSCP.path.dirname(cfg.projPath)
		cfg.signList = {}
		cfg.signIDs = {}
		cfg.spectrPlotList = {}
		cfg.signPlotIDs = {}
		cfg.scatterPlotIDs = {}
		cfg.scatterPlotList = {}
		cfg.undoIDList = {}
		cfg.undoSpectrPlotList = {}
		cfg.lstROI = None
		cfg.lstROI2 = None
		cfg.utls.clearTable(cfg.uisp.signature_list_plot_tableWidget)
		cfg.utls.clearTable(cfg.uiscp.scatter_list_plot_tableWidget)
		cfg.utls.clearTable(cfg.ui.signature_threshold_tableWidget)
		cfg.utls.clearTable(cfg.ui.download_images_tableWidget)
		cfg.utls.clearTable(cfg.ui.LCS_tableWidget)
		cfg.scaPlT.scatterPlotListTable(cfg.uiscp.scatter_list_plot_tableWidget)
		cfg.spSigPlot.refreshPlot()
		cfg.LCSignT.LCSignatureThresholdListTable()
		cfg.ui.image_raster_name_combo.blockSignals(True)
		cfg.rasterComboEdited = "No"
		# read variables
		cfg.utls.readVariables()
		# load product download table
		cfg.downProd.openDownloadTable()
		# reload layers in combos
		#cfg.ipt.refreshRasterLayer()
		cfg.utls.refreshVectorLayer()
		# set ROI color
		cfg.ui.change_color_Button.setStyleSheet("background-color :" + cfg.ROIClrVal)
		# set ROI transparency
		cfg.ui.transparency_Slider.setValue(cfg.ROITrnspVal)
		# set RAM value
		cfg.ui.RAM_spinBox.setValue(cfg.RAMValue)
		# rapid ROI band
		cfg.uidc.rapidROI_band_spinBox.setValue(int(cfg.ROIband))
		# min ROI size
		cfg.Min_region_size_spin.setValue(int(cfg.minROISz))
		# max ROI width
		cfg.Max_ROI_width_spin.setValue(int(cfg.maxROIWdth))
		# range radius
		cfg.Range_radius_spin.setValue(float(cfg.rngRad))
		# ROI ID field
		cfg.uidc.ROI_ID_spin.setValue(float(cfg.ROIID))
		# ROI macro ID field
		cfg.uidc.ROI_Macroclass_ID_spin.setValue(float(cfg.ROIMacroID))
		# preview size
		cfg.preview_size_spinBox.setValue(float(cfg.prvwSz))
		# ROI info
		cfg.uidc.ROI_Class_line.setText(cfg.ROIInfo)
		cfg.uidc.ROI_Macroclass_line.setText(cfg.ROIMacroClassInfo)
		cfg.uidc.custom_index_lineEdit.setText(cfg.customExpression)
		# ROI completer
		cfg.SCPD.roiInfoCompleter()
		cfg.SCPD.roiMacroclassInfoCompleter()
		# set signature calculation checkbox state
		if cfg.rpdROICheck == "Yes":
			cfg.uidc.rapid_ROI_checkBox.setCheckState(2)
		elif cfg.rpdROICheck == "No":
			cfg.uidc.rapid_ROI_checkBox.setCheckState(0)
		# set vegetation index calculation checkbox state
		if cfg.vegIndexCheck == "Yes":
			cfg.uidc.display_cursor_checkBox.setCheckState(2)
		elif cfg.vegIndexCheck == "No":
			cfg.uidc.display_cursor_checkBox.setCheckState(0)
		# set signature calculation checkbox state
		if cfg.sigClcCheck == "Yes":
			cfg.uidc.signature_checkBox.setCheckState(2)
			cfg.ui.signature_checkBox2.setCheckState(2)
		elif cfg.sigClcCheck == "No":
			cfg.uidc.signature_checkBox.setCheckState(0)
			cfg.ui.signature_checkBox2.setCheckState(0)
		# set save input checkbox state
		if cfg.saveInputCheck == "Yes":
			cfg.uidc.save_input_checkBox.setCheckState(2)
		elif cfg.saveInputCheck == "No":
			cfg.uidc.save_input_checkBox.setCheckState(0)
		# set ID field name line
		cfg.ui.ID_field_name_lineEdit.setText(cfg.fldID_class)
		cfg.ui.MID_field_name_lineEdit.setText(cfg.fldMacroID_class)
		# set Info field name line
		cfg.ui.Info_field_name_lineEdit.setText(cfg.fldROI_info)
		cfg.ui.MCInfo_field_name_lineEdit.setText(cfg.fldROIMC_info)
		cfg.ui.variable_name_lineEdit.setText(cfg.variableName)
		cfg.ui.group_name_lineEdit.setText(cfg.grpNm)
		# reload layers in combos
		cfg.utls.refreshClassificationLayer()
		cfg.utls.refreshRasterExtent()
		cfg.acc.refreshReferenceLayer()
		cfg.crossC.refreshReferenceLayer()
		cfg.landCC.refreshClassificationReferenceLayer()
		cfg.landCC.refreshNewClassificationLayer()
		# load classification algorithm
		idAlg = cfg.uidc.algorithm_combo.findText(cfg.algName)
		if idAlg >= 0:
			cfg.uidc.algorithm_combo.setCurrentIndex(idAlg)
		else:
			cfg.uidc.algorithm_combo.setCurrentIndex(0)
			cfg.algName = cfg.algMinDist
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		cfg.rasterComboEdited = "Yes"
		cfg.ui.image_raster_name_combo.blockSignals(False)
		cfg.bCalc.rasterBandName()
		# signature table
		cfg.utls.clearTable(cfg.uidc.signature_list_tableWidget)
		cfg.utls.clearTable(cfg.uidc.macroclass_color_tableWidget)
		cfg.SCPD.openInput()
		# RGB list
		cfg.RGBLT.RGBListTable(cfg.RGBList)

		
	# run
	def run(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "OPEN SESSION" + cfg.sysSCPInfo)
		# show the dialog
		cfg.dlg.show()
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# Run the dialog event loop
		pointer_result = cfg.dlg.exec_()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "CLOSE SESSION")
		
	# remove plugin menu and icon	
	def unload(self):
		try:
			qgisUtils.iface.removeDockWidget(cfg.dockclassdlg)
			del cfg.toolBar2
			del cfg.toolBar3
			cfg.menu.deleteLater()
			# remove temp files
			if cfg.tmpDir is not None and cfg.QDirSCP(cfg.tmpDir).exists():
				cfg.shutilSCP.rmtree(cfg.tmpDir, True)
			oDir = cfg.utls.makeDirectory(str(cfg.QDirSCP.tempPath() + "/" + cfg.tempDirName))
		except:
			if PluginCheck == "Yes":
				qgisUtils.iface.messageBar().pushMessage("Semi-Automatic Classification Plugin", QApplication.translate("semiautomaticclassificationplugin", "Please, restart QGIS for executing the Semi-Automatic Classification Plugin"), level=qgisCore.Qgis.Info)

		