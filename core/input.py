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

cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])
try:
	_fromUtf8 = cfg.QtCoreSCP.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s
		
class Input:
				
##################################
	""" Input functions """
##################################

	# check refresh raster and image list	
	def checkRefreshRasterLayer(self):
		# check if other processes are active
		if cfg.actionCheck == "No":
			self.refreshRasterLayer()
			
	def raster_layer_combo(self, layer):
		cfg.uidc.raster_name_combo.addItem(layer)
			
	# refresh raster and image list	
	def refreshRasterLayer(self):
		cfg.uidc.raster_name_combo.blockSignals(True)
		cfg.rasterComboEdited = "No"
		lL = cfg.lgnd.layers()
		cfg.uidc.raster_name_combo.clear()
		# image name
		cfg.imgNm = None
		# raster name
		cfg.rstrNm = None
		# empty item for new band set
		self.raster_layer_combo("")
		for l in lL:
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() > 1:
					self.raster_layer_combo(l.name())
		if cfg.bndSetPresent == "Yes":
			self.raster_layer_combo(cfg.bndSetNm)
			id = cfg.uidc.raster_name_combo.findText(cfg.bndSetNm)
			cfg.uidc.raster_name_combo.setCurrentIndex(id)
			cfg.rstrNm = cfg.bndSetNm
			cfg.imgNm = cfg.rstrNm
		elif cfg.bndSetPresent == "No":
			id = cfg.uidc.raster_name_combo.findText(cfg.bndSetNm)
			cfg.uidc.raster_name_combo.removeItem(id)
			cfg.bst.clearBandSet("No", "No")
		cfg.rasterComboEdited = "Yes"
		cfg.uidc.raster_name_combo.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster layers refreshed")

	# set raster name as ROI target
	def rasterLayerName(self):
		if cfg.rasterComboEdited == "Yes":
			cfg.bst.clearBandSet("No", "No")
			cfg.rstrNm = cfg.uidc.raster_name_combo.currentText()
			cfg.imgNm = cfg.rstrNm	
			# set classification input
			cfg.classD.algorithmThreshold()
			cfg.classD.previewSize()
			# set input
			cfg.rLay = cfg.utls.selectLayerbyName(cfg.rstrNm)
			if cfg.rLay is not None:
				id = cfg.uidc.raster_name_combo.findText(cfg.bndSetNm)
				cfg.uidc.raster_name_combo.removeItem(id)
				cfg.imgSrc = cfg.rLay.source()
				cfg.bndSetPresent = "No"
				cfg.bst.clearBandSet("No", "No")
				cfg.bst.rasterToBandName(cfg.rstrNm)
			elif cfg.rstrNm == "" :
				cfg.bndSet = []
				cfg.bndSetWvLn = {}
				cfg.bndSetPresent = "No"
				cfg.bst.clearBandSet("No", "Yes")
			cfg.utls.writeProjectVariable("rasterName", cfg.rstrNm)
			# reset rapid ROI spinbox
			cfg.uidc.rapidROI_band_spinBox.setValue(1)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "input raster: " + unicode(cfg.rstrNm))
						
##################################
	""" Interface functions """
##################################

	def loadInputToolbar(self):
		cfg.toolBar = cfg.iface.addToolBar("SCP Tools")
		cfg.toolBar.setObjectName("SCP Tools")
		cfg.toolBar2 = cfg.iface.addToolBar("SCP Working Toolbar")
		cfg.toolBar2.setObjectName("SCP Working Toolbar")
		cfg.toolBar3 = cfg.iface.addToolBar("SCP Edit Toolbar")
		cfg.toolBar3.setObjectName("SCP Edit Toolbar")
		self.loadToolbar1()
		self.loadToolbar2()
		self.loadToolbarEditRaster()
		
	# SCP Working Toolbar
	def loadToolbar2(self):
		# main tool
		cfg.main_toolButton = cfg.QtGuiSCP.QPushButton(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/semiautomaticclassificationplugin.png"), u"")
		cfg.main_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.main_toolButton.setToolTip(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Semi-Automatic Classification Plugin"))
		cfg.toolBar2.addWidget(cfg.main_toolButton)
		cfg.main_toolButton.clicked.connect(self.showPlugin)
		# button zoom to image
		cfg.zoomToImage = cfg.ipt.addToolbar2Button(cfg.utls.zoomToBandset, "semiautomaticclassificationplugin_zoom_to_Image.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Zoom to input image extent"))
		# radio button show hide input image
		cfg.inputImageRadio = cfg.ipt.addToolbarRadio(cfg.utls.showHideInputImage, cfg.QtGuiSCP.QApplication.translate("SemiAutomaticClassificationPlugin", "RGB = ", None), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Show/hide the input image"))
		# combo RGB composite
		cfg.rgb_combo = cfg.QtGuiSCP.QComboBox(cfg.iface.mainWindow())
		cfg.rgb_combo.setFixedWidth(80)
		cfg.rgb_combo.setEditable(True)
		rgb_comboAction = cfg.toolBar2.addWidget(cfg.rgb_combo)
		cfg.rgb_combo.setToolTip(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a RGB color composite"))
		cfg.rgb_combo.currentIndexChanged.connect(cfg.utls.setRGBColorComposite)	
		# local cumulative cut stretch button
		cfg.local_cumulative_stretch_toolButton = cfg.ipt.addToolbar2Button(cfg.utls.setRasterCumulativeStretch, "semiautomaticclassificationplugin_bandset_cumulative_stretch_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Local cumulative cut stretch of band set"))
		# local standard deviation stretch button
		cfg.local_std_dev_stretch_toolButton = cfg.ipt.addToolbar2Button(cfg.utls.setRasterStdDevStretch, "semiautomaticclassificationplugin_bandset_std_dev_stretch_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Local standard deviation stretch of band set"))
		# button zoom to ROI
		cfg.zoomToTempROI = cfg.ipt.addToolbar2Button(cfg.ROId.zoomToTempROI, "semiautomaticclassificationplugin_zoom_to_ROI.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Zoom to temporary ROI"))
		# radio button show hide ROI
		cfg.show_ROI_radioButton = cfg.ipt.addToolbarRadio(cfg.ROId.showHideROI, cfg.QtGuiSCP.QApplication.translate("SemiAutomaticClassificationPlugin", "ROI     ", None), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Show/hide the temporary ROI"))
		# manual ROI pointer 
		cfg.polygonROI_Button = cfg.ipt.addToolbar2Button(cfg.ROId.pointerManualROIActive, "semiautomaticclassificationplugin_manual_ROI.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Create a ROI polygon"))
		# pointer button
		cfg.pointerButton = cfg.ipt.addToolbar2Button(cfg.ROId.pointerROIActive, "semiautomaticclassificationplugin_roi_single.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Activate ROI pointer"))
		# redo button
		cfg.redo_ROI_Button = cfg.ipt.addToolbar2Button(cfg.ROId.redoROI, "semiautomaticclassificationplugin_roi_redo.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Redo the ROI at the same point"))
		cfg.redo_ROI_Button.setEnabled(False)
		# spinbox spectral distance
		lblSpectralDistance = cfg.ipt.addToolbarLabel(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", " Dist"), "Yes")
		cfg.Range_radius_spin = cfg.ipt.addToolbarSpin(cfg.ROId.rangeRadius, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Similarity of pixels (distance in radiometry unit)"), 6, 1e-06, 10000.0, 0.001, 0.01)
		# spinbox min size
		lblmin= cfg.ipt.addToolbarLabel(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", " Min"), "Yes")
		cfg.Min_region_size_spin = cfg.ipt.addToolbarSpin(cfg.ROId.minROISize, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Minimum area of ROI (in pixel unit)"), 0, 1, 10000, 1, 60, 60)
		# spinbox max size
		lblmax = cfg.ipt.addToolbarLabel(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", " Max"), "Yes")
		cfg.Max_ROI_width_spin = cfg.ipt.addToolbarSpin(cfg.ROId.maxROIWidth, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Side of a square which inscribes the ROI, defining the maximum width thereof (in pixel unit)"), 0, 1, 10000, 1, int(cfg.maxROIWdth), 60)
		# button zoom to preview
		cfg.zoomToTempPreview = cfg.ipt.addToolbar2Button(cfg.classD.zoomToPreview, "semiautomaticclassificationplugin_zoom_to_preview.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Zoom to the classification preview"))
		# radio button show hide preview
		cfg.show_preview_radioButton2 = cfg.ipt.addToolbarRadio(cfg.classD.showHidePreview2, cfg.QtGuiSCP.QApplication.translate("SemiAutomaticClassificationPlugin", "Preview ", None), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Show/hide the classification preview"))
		# preview pointer button
		cfg.pointerPreviewButton = cfg.ipt.addToolbar2Button(cfg.classD.pointerPreviewActive, "semiautomaticclassificationplugin_preview.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Activate classification preview pointer"))
		cfg.redoPreviewButton = cfg.ipt.addToolbar2Button(cfg.classD.redoPreview, "semiautomaticclassificationplugin_preview_redo.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Redo the classification preview at the same point"))
		cfg.redoPreviewButton.setEnabled(False)
		# spinbox transparency
		lblmax = cfg.ipt.addToolbarLabel(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", " T"), "Yes")
		cfg.preview_transp_spin = cfg.ipt.addToolbarSpin(cfg.classD.changePreviewTransparency, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Set preview transparency"), 0, 0, 100, 10, 0, 50)
		# spinbox size
		lblmax = cfg.ipt.addToolbarLabel(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", " S"), "Yes")
		cfg.preview_size_spinBox = cfg.ipt.addToolbarSpin(cfg.classD.previewSize, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Set the preview size (in pixel unit)"), 0, 1, 1000000, 100, float(cfg.prvwSz), 60)
		cfg.removeTempFilesButton = cfg.ipt.addToolbar2Button(cfg.utls.removeTempFiles, "semiautomaticclassificationplugin_remove_temp.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Remove temporary files"))
		
	# add spinbox
	def addToolbarSpin(self, function, tooltip, decimals, min, max, step, value, width = 100):
		spin = cfg.QtGuiSCP.QDoubleSpinBox(cfg.iface.mainWindow())
		spin.setFixedWidth(width)
		spin.setDecimals(decimals)
		spin.setMinimum(min)
		spin.setMaximum(max)
		spin.setSingleStep(step)
		spin.setProperty("value", value)
		spin.setToolTip(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", tooltip))
		Range_radiusAction = cfg.toolBar2.addWidget(spin)
		spin.valueChanged.connect(function)
		return spin
		
	# add spinbox
	def addEditToolbarSpin(self, function, tooltip, decimals, min, max, step, value, width = 100):
		spin = cfg.QtGuiSCP.QDoubleSpinBox(cfg.iface.mainWindow())
		spin.setFixedWidth(width)
		spin.setDecimals(decimals)
		spin.setMinimum(min)
		spin.setMaximum(max)
		spin.setSingleStep(step)
		spin.setProperty("value", value)
		spin.setToolTip(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", tooltip))
		Range_radiusAction = cfg.toolBar3.addWidget(spin)
		#spin.valueChanged.connect(function)
		return spin
		
	# add radio button
	def addToolbarRadio(self, function, text, tooltip):
		radio = cfg.QtGuiSCP.QRadioButton(cfg.iface.mainWindow())
		inputImageRadio_comboAction = cfg.toolBar2.addWidget(radio)
		radio.setToolTip(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", tooltip))
		radio.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #535353, stop:1 #a6a6a6); color : white"))
		radio.setText(cfg.QtGuiSCP.QApplication.translate("SemiAutomaticClassificationPlugin", text, None))
		radio.setChecked(True)
		radio.setAutoExclusive(False)
		radio.clicked.connect(function)
		return radio
		
	# add label to toolbar
	def addToolbarLabel(self, text, black = None, width = None):
		font = cfg.QtGuiSCP.QFont()
		font.setFamily(_fromUtf8("FreeSans"))
		font.setBold(True)
		font.setWeight(75)
		lbl = cfg.QtGuiSCP.QLabel(cfg.iface.mainWindow())
		lbl.setFont(font)
		if black is None:
			lbl.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #535353, stop:1 #a6a6a6); color : white"))
		else:
			lbl.setStyleSheet(_fromUtf8("color : black"))
		lbl.setObjectName(_fromUtf8("lbl"))
		if width is not None:
			lbl.setFixedWidth(width)
		lbl.setMaximumHeight(18)
		lbl.setText(cfg.QtGuiSCP.QApplication.translate("SemiAutomaticClassificationPlugin", text, None))
		cfg.toolBar2.addWidget(lbl)
		return lbl
		
	# SCP Edit raster
	def loadToolbarEditRaster(self):
		cfg.editRasterToolbar_toolButton = cfg.ipt.addToolbarEditButton(cfg.utls.editRasterTab, "semiautomaticclassificationplugin_edit_raster.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Edit raster"))
		# spinbox value 0
		cfg.val0_spin = cfg.ipt.addEditToolbarSpin(None, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Value 0"), 0, -10000, 10000, 1, 0, 60)
		cfg.setVal0_toolButton = cfg.ipt.addToolbarEditButton(cfg.editRstr.toolbarValue0, "semiautomaticclassificationplugin_enter.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Set value 0"))
		# spinbox value 1
		cfg.val1_spin = cfg.ipt.addEditToolbarSpin(None, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Value 1"), 0, -10000, 10000, 1, 1, 60)
		cfg.setVal1_toolButton = cfg.ipt.addToolbarEditButton(cfg.editRstr.toolbarValue1, "semiautomaticclassificationplugin_enter.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Set value 1"))
		# spinbox value 2
		cfg.val2_spin = cfg.ipt.addEditToolbarSpin(None, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Value 2"), 0, -10000, 10000, 1, 2, 60)
		cfg.setVal2_toolButton = cfg.ipt.addToolbarEditButton(cfg.editRstr.toolbarValue2, "semiautomaticclassificationplugin_enter.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Set value 2"))
		cfg.undoEditRasterToolbar_toolButton = cfg.ipt.addToolbarEditButton(cfg.editRstr.undoEdit, "semiautomaticclassificationplugin_undo_edit_raster.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Undo edit (only for ROI polygons)"))
		cfg.undoEditRasterToolbar_toolButton.setEnabled(False)
		
	# SCP Tools
	def loadToolbar1(self):
		cfg.bandset_toolButton = cfg.ipt.addToolbarButton(cfg.utls.bandSetTab, "semiautomaticclassificationplugin_bandset_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Band set"))
		# Download images button
		cfg.download_images_toolButton = cfg.ipt.addToolbarButton(cfg.utls.downloadImagesTab, "semiautomaticclassificationplugin_download_arrow.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Download images"))
		# Tools button
		cfg.ROItools_toolButton = cfg.ipt.addToolbarButton(cfg.utls.roiToolsTab, "semiautomaticclassificationplugin_roi_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Tools"))
		# Preprocessing button
		cfg.preprocessing_toolButton = cfg.ipt.addToolbarButton(cfg.utls.preProcessingTab, "semiautomaticclassificationplugin_class_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Preprocessing"))
		# Postprocessing button
		cfg.postprocessing_toolButton = cfg.ipt.addToolbarButton(cfg.utls.postProcessingTab, "semiautomaticclassificationplugin_post_process.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Postprocessing"))
		# Band calc button
		cfg.bandcalc_toolButton = cfg.ipt.addToolbarButton(cfg.utls.bandCalcTab, "semiautomaticclassificationplugin_bandcalc_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Band calc"))
		# spectral signature plot button
		cfg.spectral_plot_toolButton = cfg.ipt.addToolbarButton(cfg.utls.spectralPlotTab, "semiautomaticclassificationplugin_sign_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Spectral plot"))
		# scatter signature plot button
		cfg.scatter_plot_toolButton = cfg.ipt.addToolbarButton(cfg.utls.scatterPlotTab, "semiautomaticclassificationplugin_scatter_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Scatter plot"))
		# batch
		cfg.batch_toolButton = cfg.ipt.addToolbarButton(cfg.utls.batchTab, "semiautomaticclassificationplugin_batch.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Batch"))
		# Settings button
		cfg.settings_toolButton = cfg.ipt.addToolbarButton(cfg.utls.settingsTab, "semiautomaticclassificationplugin_settings_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Settings"))
		# User manual button
		cfg.userguide_toolButton = cfg.ipt.addToolbarButton(self.quickGuide, "guide.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "User manual"))
		# Help button
		cfg.help_toolButton = cfg.ipt.addToolbarButton(self.askHelp, "help.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Online help"))
		
	# Add toolbar button
	def addToolbarButton(self, function, iconName, tooltip):
		toolButton = cfg.QtGuiSCP.QPushButton(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/" + iconName), u"")
		toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		toolButton.setToolTip(tooltip)
		cfg.toolBar.addWidget(toolButton)
		toolButton.clicked.connect(function)
		return toolButton
				
	# Add toolbar button
	def addToolbar2Button(self, function, iconName, tooltip):
		toolButton = cfg.QtGuiSCP.QPushButton(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/" + iconName), u"")
		toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		toolButton.setToolTip(tooltip)
		cfg.toolBar2.addWidget(toolButton)
		toolButton.clicked.connect(function)
		return toolButton
		
	# Add toolbar button
	def addToolbarEditButton(self, function, iconName, tooltip):
		toolButton = cfg.QtGuiSCP.QPushButton(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/" + iconName), u"")
		toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		toolButton.setToolTip(tooltip)
		cfg.toolBar3.addWidget(toolButton)
		toolButton.clicked.connect(function)
		return toolButton
			
	# show plugin
	def showPlugin(self):
		# show the dialog
		cfg.dlg.show()
		self.activateDocks()
		
	# activate docks
	def activateDocks(self):
		cfg.dockclassdlg.show()
		cfg.toolBar.show()
		cfg.toolBar2.show()
		cfg.toolBar3.show()
		
	# user manual
	def quickGuide(self):
		cfg.QtGuiSCP.QDesktopServices().openUrl(cfg.QtCoreSCP.QUrl("https://fromgistors.blogspot.com/p/user-manual.html?spref=scp"))
		
	# help
	def askHelp(self):
		cfg.QtGuiSCP.QDesktopServices().openUrl(cfg.QtCoreSCP.QUrl("https://fromgistors.blogspot.com/p/online-help.html?spref=scp"))
		
	# add item to menu
	def addMenuItem(self, menu, function, iconName, name):
		action = cfg.QtGuiSCP.QAction(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/" + iconName), name, cfg.iface.mainWindow())
		action.setObjectName("action")
		cfg.QObjectSCP.connect(action, cfg.SIGNALSCP("triggered()"), function)
		menu.addAction(action)
		return action
		
	# load SCP menu
	def loadMenu(self):
		cfg.menu = cfg.QtGuiSCP.QMenu(cfg.iface.mainWindow())
		cfg.menu.setObjectName('semiautomaticclassificationplugin')
		cfg.menu.setTitle(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "SCP"))
		menuBar = cfg.iface.mainWindow().menuBar()
		menuBar.insertMenu(cfg.iface.firstRightStandardMenu().menuAction(), cfg.menu)
		# Band set
		bandset_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.bandSetTab, "semiautomaticclassificationplugin_bandset_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Band set"))
		# Download
		cfg.download_images_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_download_arrow.png"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Download images"))
		# Download Landsat
		download_landsat8_action = cfg.ipt.addMenuItem(cfg.download_images_menu, cfg.utls.downloadLandast8Tab, "semiautomaticclassificationplugin_landsat8_download_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Landsat download"))
		# Download Sentinel
		download_sentinel_action = cfg.ipt.addMenuItem(cfg.download_images_menu, cfg.utls.downloadSentinelTab, "semiautomaticclassificationplugin_sentinel_download_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Sentinel-2 download "))
		# Download ASTER
		download_ASTER_action = cfg.ipt.addMenuItem(cfg.download_images_menu, cfg.utls.downloadASTERTab, "semiautomaticclassificationplugin_aster_download_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "ASTER download"))
		# Tools
		cfg.tools_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_roi_tool.png"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Tools"))
		# Multiple ROI creation
		multiple_ROI_creation_action = cfg.ipt.addMenuItem(cfg.tools_menu, cfg.utls.mutlipleROITab, "semiautomaticclassificationplugin_roi_multiple.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Multiple ROI creation"))
		# Import Spectral Library
		import_spectral_library_action = cfg.ipt.addMenuItem(cfg.tools_menu, cfg.utls.importLibraryTab, "semiautomaticclassificationplugin_import_spectral_library.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Import signatures"))
		# Export Spectral Library
		export_spectral_library_action = cfg.ipt.addMenuItem(cfg.tools_menu, cfg.utls.exportLibraryTab, "semiautomaticclassificationplugin_export_spectral_library.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Export signatures"))
		# Algorithm band weight
		algorithm_weight_action = cfg.ipt.addMenuItem(cfg.tools_menu, cfg.utls.algorithmWeighTab, "semiautomaticclassificationplugin_weight_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Algorithm band weight"))
		# Signature threshold
		signature_threshold_action = cfg.ipt.addMenuItem(cfg.tools_menu, cfg.utls.algorithmThresholdTab, "semiautomaticclassificationplugin_threshold_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Signature threshold"))
		# LCS threshold
		LCS_threshold_action = cfg.ipt.addMenuItem(cfg.tools_menu, cfg.utls.LCSThresholdTab, "semiautomaticclassificationplugin_LCS_threshold_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "LCS threshold"))
		# RGB list
		RGB_list_action = cfg.ipt.addMenuItem(cfg.tools_menu, cfg.utls.RGBListTab, "semiautomaticclassificationplugin_rgb_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "RGB list"))
		# Preprocessing
		cfg.preprocessing_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_class_tool.png"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Preprocessing"))
		# Landsat
		landsat_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.landsatTab, "semiautomaticclassificationplugin_landsat8_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Landsat"))
		# Sentinel-2
		sentinel2_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.sentinel2Tab, "semiautomaticclassificationplugin_sentinel_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Sentinel-2"))
		# ASTER
		aster_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.asterTab, "semiautomaticclassificationplugin_aster_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "ASTER"))
		# Clip multiple rasters
		clip_multiple_rasters_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.clipMultipleRastersTab, "semiautomaticclassificationplugin_clip_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Clip multiple rasters"))
		# Split raster bands
		split_raster_bands_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.splitrasterbandsTab, "semiautomaticclassificationplugin_split_raster.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Split raster bands"))
		# PCA
		PCA_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.PCATab, "semiautomaticclassificationplugin_pca_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "PCA"))
		# Vector to raster
		vector_to_raster_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.vectorToRasterTab, "semiautomaticclassificationplugin_vector_to_raster_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Vector to raster"))
		# Postprocessing
		cfg.postprocessing_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_post_process.png"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Postprocessing"))
		# Accuracy
		accuracy_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.accuracyTab, "semiautomaticclassificationplugin_accuracy_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Accuracy"))
		# Land cover change
		land_cover_change_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.landCoverChangeTab, "semiautomaticclassificationplugin_land_cover_change.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Land cover change"))
		# Classification report
		classification_report_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classificationReportTab, "semiautomaticclassificationplugin_report_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification report"))
		# Cross classification
		cross_classification_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.crossClassificationTab, "semiautomaticclassificationplugin_cross_classification.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Cross classification"))
		# Classification to vector
		class_to_vector_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classToVectorTab, "semiautomaticclassificationplugin_class_to_vector_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification to vector"))
		# Reclassification
		reclassification_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.reclassificationTab, "semiautomaticclassificationplugin_reclassification_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Reclassification"))
		# Edit raster
		edit_raster_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.editRasterTab, "semiautomaticclassificationplugin_edit_raster.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Edit raster"))
		# Classification sieve
		classification_sieve_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classificationSieveTab, "semiautomaticclassificationplugin_classification_sieve.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification sieve"))
		# Classification erosion
		classification_erosion_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classificationErosionTab, "semiautomaticclassificationplugin_classification_erosion.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification erosion"))
		# Classification dilation
		classification_erosion_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classificationDilationTab, "semiautomaticclassificationplugin_classification_dilation.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification dilation"))
		# Band calc
		bandcalc_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.bandCalcTab, "semiautomaticclassificationplugin_bandcalc_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Band calc"))
		# Spectral plot
		spectral_plot_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.spectralPlotTab, "semiautomaticclassificationplugin_sign_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Spectral plot"))	
		# scatter plot
		scatter_plot_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.scatterPlotTab, "semiautomaticclassificationplugin_scatter_tool.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Scatter plot"))
		# batch
		batch_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.batchTab, "semiautomaticclassificationplugin_batch.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Batch"))
		# Settings
		cfg.settings_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_settings_tool.png"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Settings"))
		# Settings interface
		self.settings_interface_action = cfg.QtGuiSCP.QAction(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Interface"), cfg.iface.mainWindow())
		self.settings_interface_action.setObjectName("settings_interface_action")
		cfg.QObjectSCP.connect(self.settings_interface_action, cfg.SIGNALSCP("triggered()"), cfg.utls.settingsInterfaceTab)
		cfg.settings_menu.addAction(self.settings_interface_action)
		# Settings processing
		self.settings_processing_action = cfg.QtGuiSCP.QAction(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Processing"), cfg.iface.mainWindow())
		self.settings_processing_action.setObjectName("settings_processing_action")
		cfg.QObjectSCP.connect(self.settings_processing_action, cfg.SIGNALSCP("triggered()"), cfg.utls.settingsProcessingTab)
		cfg.settings_menu.addAction(self.settings_processing_action)
		# Settings debug
		self.settings_debug_action = cfg.QtGuiSCP.QAction(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Debug"), cfg.iface.mainWindow())
		self.settings_debug_action.setObjectName("settings_debug_action")
		cfg.QObjectSCP.connect(self.settings_debug_action, cfg.SIGNALSCP("triggered()"), cfg.utls.settingsDebugTab)
		cfg.settings_menu.addAction(self.settings_debug_action)
		# User manual
		userguide_action = cfg.ipt.addMenuItem(cfg.menu, cfg.ipt.quickGuide, "guide.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "User manual"))
		# help
		help_action = cfg.ipt.addMenuItem(cfg.menu, cfg.ipt.askHelp, "help.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Online help"))
		# About
		about_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.aboutTab, "fromGIStoRS.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "About"))
		# show plugin
		show_action = cfg.ipt.addMenuItem(cfg.menu, self.showPlugin, "semiautomaticclassificationplugin_docks.png", cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Show plugin"))
		
	# welcome text
	def welcomeText(self, inputUrl = None, inputUrl2 = None):
		l = cfg.plgnDir + "/ui/welcome.html"
		if inputUrl is None:
			htmlText = open(l, 'r').read()
		else:
			if cfg.downNewsVal == "Yes":
				htmlText = cfg.utls.downloadHtmlFileQGIS(inputUrl, inputUrl2)
			else:
				htmlText = "No"
			if htmlText == "No":
				htmlText = open(l, 'r').read()
		cfg.uidc.main_textBrowser.clear()
		cfg.uidc.main_textBrowser.setHtml(htmlText)
		