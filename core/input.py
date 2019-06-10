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
		cfg.ui.image_raster_name_combo.addItem(layer)
			
	# refresh raster and image list	
	def refreshRasterLayer(self):
		cfg.ui.image_raster_name_combo.blockSignals(True)
		cfg.rasterComboEdited = "No"
		lL = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.image_raster_name_combo.clear()
		# empty item for new band set
		self.raster_layer_combo("")
		for l in sorted(lL, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() > 1 and cfg.bndSetVrtNm not in l.name():
					self.raster_layer_combo(l.name())
		cfg.rasterComboEdited = "Yes"
		cfg.ui.image_raster_name_combo.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster layers refreshed")
						
##################################
	""" Interface functions """
##################################

	def loadInputToolbar(self):
		cfg.toolBar2 = cfg.iface.addToolBar("SCP Working Toolbar")
		cfg.toolBar2.setObjectName("SCP Working Toolbar")
		cfg.toolBar3 = cfg.iface.addToolBar("SCP Edit Toolbar")
		cfg.toolBar3.setObjectName("SCP Edit Toolbar")
		self.loadToolbar2()
		self.loadToolbarEditRaster()
		self.setSCPDockTabs()
		
	# SCP Working Toolbar
	def loadToolbar2(self):
		# main tool
		cfg.main_toolButton = cfg.QtWidgetsSCP.QPushButton(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/semiautomaticclassificationplugin.png"), "")
		cfg.main_toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		cfg.main_toolButton.setToolTip(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Semi-Automatic Classification Plugin"))
		cfg.toolBar2.addWidget(cfg.main_toolButton)
		cfg.main_toolButton.clicked.connect(self.showPlugin)
		# button zoom to image
		cfg.zoomToImage = cfg.ipt.addToolbar2Button(cfg.utls.zoomToBandset, "semiautomaticclassificationplugin_zoom_to_Image.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Zoom to input image extent"))
		# radio button show hide input image
		cfg.inputImageRadio = cfg.ipt.addToolbarRadio(cfg.utls.showHideInputImage, cfg.QtWidgetsSCP.QApplication.translate("SemiAutomaticClassificationPlugin", "RGB = ", None), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Show/hide the input image"))
		# combo RGB composite
		cfg.rgb_combo = cfg.QtWidgetsSCP.QComboBox(cfg.iface.mainWindow())
		cfg.rgb_combo.setFixedWidth(80)
		cfg.rgb_combo.setEditable(True)
		rgb_comboAction = cfg.toolBar2.addWidget(cfg.rgb_combo)
		cfg.rgb_combo.setToolTip(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Select a RGB color composite"))
		cfg.rgb_combo.currentIndexChanged.connect(cfg.utls.setRGBColorComposite)	
		# local cumulative cut stretch button
		cfg.local_cumulative_stretch_toolButton = cfg.ipt.addToolbar2Button(cfg.utls.setRasterCumulativeStretch, "semiautomaticclassificationplugin_bandset_cumulative_stretch_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Local cumulative cut stretch of band set"))
		# local standard deviation stretch button
		cfg.local_std_dev_stretch_toolButton = cfg.ipt.addToolbar2Button(cfg.utls.setRasterStdDevStretch, "semiautomaticclassificationplugin_bandset_std_dev_stretch_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Local standard deviation stretch of band set"))
		# button zoom to ROI
		cfg.zoomToTempROI = cfg.ipt.addToolbar2Button(cfg.SCPD.zoomToTempROI, "semiautomaticclassificationplugin_zoom_to_ROI.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Zoom to temporary ROI"))
		# radio button show hide ROI
		cfg.show_ROI_radioButton = cfg.ipt.addToolbarRadio(cfg.SCPD.showHideROI, cfg.QtWidgetsSCP.QApplication.translate("SemiAutomaticClassificationPlugin", "ROI     ", None), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Show/hide the temporary ROI"))
		# manual ROI pointer 
		cfg.polygonROI_Button = cfg.ipt.addToolbar2Button(cfg.SCPD.pointerManualROIActive, "semiautomaticclassificationplugin_manual_ROI.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Create a ROI polygon"))
		# pointer button
		cfg.pointerButton = cfg.ipt.addToolbar2Button(cfg.SCPD.pointerROIActive, "semiautomaticclassificationplugin_roi_single.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Activate ROI pointer"))
		# redo button
		cfg.redo_ROI_Button = cfg.ipt.addToolbar2Button(cfg.SCPD.redoROI, "semiautomaticclassificationplugin_roi_redo.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Redo the ROI at the same point"))
		cfg.redo_ROI_Button.setEnabled(False)
		# spinbox spectral distance
		lblSpectralDistance = cfg.ipt.addToolbarLabel(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " Dist"), "Yes")
		lblSpectralDistance.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #535353, stop:1 #535353); color : white"))
		cfg.Range_radius_spin = cfg.ipt.addToolbarSpin(cfg.SCPD.rangeRadius, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Similarity of pixels (distance in radiometry unit)"), 6, 1e-06, 10000.0, 0.001, 0.01)
		# spinbox min size
		lblmin= cfg.ipt.addToolbarLabel(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " Min"), "Yes")
		lblmin.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #535353, stop:1 #535353); color : white"))
		cfg.Min_region_size_spin = cfg.ipt.addToolbarSpin(cfg.SCPD.minROISize, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Minimum area of ROI (in pixel unit)"), 0, 1, 10000, 1, 60, 60)
		# spinbox max size
		lblmax = cfg.ipt.addToolbarLabel(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " Max"), "Yes")
		lblmax.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #535353, stop:1 #535353); color : white"))
		cfg.Max_ROI_width_spin = cfg.ipt.addToolbarSpin(cfg.SCPD.maxROIWidth, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Side of a square which inscribes the ROI, defining the maximum width thereof (in pixel unit)"), 0, 1, 10000, 1, int(cfg.maxROIWdth), 60)
		# button zoom to preview
		cfg.zoomToTempPreview = cfg.ipt.addToolbar2Button(cfg.SCPD.zoomToPreview, "semiautomaticclassificationplugin_zoom_to_preview.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Zoom to the classification preview"))
		# radio button show hide preview
		cfg.show_preview_radioButton2 = cfg.ipt.addToolbarRadio(cfg.SCPD.showHidePreview2, cfg.QtWidgetsSCP.QApplication.translate("SemiAutomaticClassificationPlugin", "Preview ", None), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Show/hide the classification preview"))
		# preview pointer button
		cfg.pointerPreviewButton = cfg.ipt.addToolbar2Button(cfg.SCPD.pointerPreviewActive, "semiautomaticclassificationplugin_preview.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Activate classification preview pointer"))
		cfg.redoPreviewButton = cfg.ipt.addToolbar2Button(cfg.SCPD.redoPreview, "semiautomaticclassificationplugin_preview_redo.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Redo the classification preview at the same point"))
		cfg.redoPreviewButton.setEnabled(False)
		# spinbox transparency
		lblT = cfg.ipt.addToolbarLabel(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " T"), "Yes")
		lblT.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #535353, stop:1 #535353); color : white"))
		cfg.preview_transp_spin = cfg.ipt.addToolbarSpin(cfg.SCPD.changePreviewTransparency, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set preview transparency"), 0, 0, 100, 10, 0, 50)
		# spinbox size
		lblS = cfg.ipt.addToolbarLabel(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", " S"), "Yes")
		lblS.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #535353, stop:1 #535353); color : white"))
		cfg.preview_size_spinBox = cfg.ipt.addToolbarSpin(cfg.SCPD.previewSize, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set the preview size (in pixel unit)"), 0, 1, 1000000, 100, float(cfg.prvwSz), 60)
		cfg.removeTempFilesButton = cfg.ipt.addToolbar2Button(cfg.utls.removeTempFiles, "semiautomaticclassificationplugin_remove_temp.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Remove temporary files"))
		cfg.createKMLButton = cfg.ipt.addToolbar2Button(cfg.utls.createKMLFromMap, "semiautomaticclassificationplugin_kml_add.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Create KML"))
		
	# add spinbox
	def addToolbarSpin(self, function, tooltip, decimals, min, max, step, value, width = 100):
		spin = cfg.QtWidgetsSCP.QDoubleSpinBox(cfg.iface.mainWindow())
		spin.setFixedWidth(width)
		spin.setDecimals(decimals)
		spin.setMinimum(min)
		spin.setMaximum(max)
		spin.setSingleStep(step)
		spin.setProperty("value", value)
		spin.setToolTip(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", tooltip))
		Range_radiusAction = cfg.toolBar2.addWidget(spin)
		spin.valueChanged.connect(function)
		return spin
		
	# add spinbox
	def addEditToolbarSpin(self, function, tooltip, decimals, min, max, step, value, width = 100):
		spin = cfg.QtWidgetsSCP.QDoubleSpinBox(cfg.iface.mainWindow())
		spin.setFixedWidth(width)
		spin.setDecimals(decimals)
		spin.setMinimum(min)
		spin.setMaximum(max)
		spin.setSingleStep(step)
		spin.setProperty("value", value)
		spin.setToolTip(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", tooltip))
		Range_radiusAction = cfg.toolBar3.addWidget(spin)
		#spin.valueChanged.connect(function)
		return spin
		
	# add radio button
	def addToolbarRadio(self, function, text, tooltip):
		radio = cfg.QtWidgetsSCP.QRadioButton(cfg.iface.mainWindow())
		inputImageRadio_comboAction = cfg.toolBar2.addWidget(radio)
		radio.setToolTip(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", tooltip))
		radio.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #535353, stop:1 #a6a6a6); color : white"))
		radio.setText(cfg.QtWidgetsSCP.QApplication.translate("SemiAutomaticClassificationPlugin", text, None))
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
		lbl = cfg.QtWidgetsSCP.QLabel(cfg.iface.mainWindow())
		lbl.setFont(font)
		if black is None:
			lbl.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #535353, stop:1 #a6a6a6); color : white"))
		else:
			lbl.setStyleSheet(_fromUtf8("color : black"))
		lbl.setObjectName(_fromUtf8("lbl"))
		if width is not None:
			lbl.setFixedWidth(width)
		lbl.setMaximumHeight(18)
		lbl.setText(cfg.QtWidgetsSCP.QApplication.translate("SemiAutomaticClassificationPlugin", text, None))
		cfg.toolBar2.addWidget(lbl)
		return lbl
		
	# SCP Edit raster
	def loadToolbarEditRaster(self):
		cfg.editRasterToolbar_toolButton = cfg.ipt.addToolbarEditButton(cfg.utls.editRasterTab, "semiautomaticclassificationplugin_edit_raster.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Edit raster"))
		# spinbox value 0
		cfg.val0_spin = cfg.ipt.addEditToolbarSpin(None, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Value 0"), 0, -10000, 10000, 1, 0, 60)
		cfg.setVal0_toolButton = cfg.ipt.addToolbarEditButton(cfg.editRstr.toolbarValue0, "semiautomaticclassificationplugin_enter.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set value 0"))
		# spinbox value 1
		cfg.val1_spin = cfg.ipt.addEditToolbarSpin(None, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Value 1"), 0, -10000, 10000, 1, 1, 60)
		cfg.setVal1_toolButton = cfg.ipt.addToolbarEditButton(cfg.editRstr.toolbarValue1, "semiautomaticclassificationplugin_enter.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set value 1"))
		# spinbox value 2
		cfg.val2_spin = cfg.ipt.addEditToolbarSpin(None, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Value 2"), 0, -10000, 10000, 1, 2, 60)
		cfg.setVal2_toolButton = cfg.ipt.addToolbarEditButton(cfg.editRstr.toolbarValue2, "semiautomaticclassificationplugin_enter.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set value 2"))
		cfg.undoEditRasterToolbar_toolButton = cfg.ipt.addToolbarEditButton(cfg.editRstr.undoEdit, "semiautomaticclassificationplugin_undo_edit_raster.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Undo edit (only for ROI polygons)"))
		cfg.undoEditRasterToolbar_toolButton.setEnabled(False)
				
	# Add toolbar button
	def addToolbar2Button(self, function, iconName, tooltip):
		toolButton = cfg.QtWidgetsSCP.QPushButton(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/" + iconName), "")
		toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		toolButton.setToolTip(tooltip)
		cfg.toolBar2.addWidget(toolButton)
		toolButton.clicked.connect(function)
		return toolButton
		
	# Add toolbar button
	def addToolbarEditButton(self, function, iconName, tooltip):
		toolButton = cfg.QtWidgetsSCP.QPushButton(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/" + iconName), "")
		toolButton.setStyleSheet(" border: none;margin: 2px;icon-size: 24px; color: black")
		toolButton.setToolTip(tooltip)
		cfg.toolBar3.addWidget(toolButton)
		toolButton.clicked.connect(function)
		return toolButton
			
	# show plugin
	def showPlugin(self):
		# close the dialog
		cfg.dlg.close()
		self.activateDocks()
		# show the dialog
		cfg.dlg.show()
		
	# activate docks
	def activateDocks(self):
		cfg.dockclassdlg.show()
		cfg.toolBar2.show()
		cfg.toolBar3.show()
		
	# user manual
	def quickGuide(self):
		cfg.QtGuiSCP.QDesktopServices().openUrl(cfg.QtCoreSCP.QUrl("https://fromgistors.blogspot.com/p/user-manual.html?spref=scp"))
		
	# help
	def askHelp(self):
		cfg.QtGuiSCP.QDesktopServices().openUrl(cfg.QtCoreSCP.QUrl("https://fromgistors.blogspot.com/p/online-help.html?spref=scp"))
		
	# support SCP
	def supportSCP(self):
		cfg.QtGuiSCP.QDesktopServices().openUrl(cfg.QtCoreSCP.QUrl("https://fromgistors.blogspot.com/p/support-scp.html?spref=scp"))
		
	# add item to menu
	def addMenuItem(self, menu, function, iconName, name):
		action = cfg.QtWidgetsSCP.QAction(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/" + iconName), name, cfg.iface.mainWindow())
		action.setObjectName("action")
		action.triggered.connect(function)
		menu.addAction(action)
		return action
		
	# load SCP menu
	def loadMenu(self):
		cfg.menu = cfg.QtWidgetsSCP.QMenu(cfg.iface.mainWindow())
		cfg.menu.setObjectName('semiautomaticclassificationplugin')
		cfg.menu.setTitle(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "SCP"))
		menuBar = cfg.iface.mainWindow().menuBar()
		menuBar.insertMenu(cfg.iface.firstRightStandardMenu().menuAction(), cfg.menu)
		# Band set
		bandset_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.bandSetTab, "semiautomaticclassificationplugin_bandset_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band set"))
		# Band tools
		cfg.basic_tools_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_roi_tool.png"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Basic tools"))
		# RGB list
		RGB_list_action = cfg.ipt.addMenuItem(cfg.basic_tools_menu, cfg.utls.RGBListTab, "semiautomaticclassificationplugin_rgb_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "RGB list"))
		# Algorithm band weight
		algorithm_weight_action = cfg.ipt.addMenuItem(cfg.basic_tools_menu, cfg.utls.algorithmWeighTab, "semiautomaticclassificationplugin_weight_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Algorithm band weight"))
		# Multiple ROI creation
		multiple_ROI_creation_action = cfg.ipt.addMenuItem(cfg.basic_tools_menu, cfg.utls.mutlipleROITab, "semiautomaticclassificationplugin_roi_multiple.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Multiple ROI creation"))
		# Import Spectral Library
		import_spectral_library_action = cfg.ipt.addMenuItem(cfg.basic_tools_menu, cfg.utls.importLibraryTab, "semiautomaticclassificationplugin_import_spectral_library.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Import signatures"))
		# Export Spectral Library
		export_spectral_library_action = cfg.ipt.addMenuItem(cfg.basic_tools_menu, cfg.utls.exportLibraryTab, "semiautomaticclassificationplugin_export_spectral_library.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Export signatures"))
		# Signature threshold
		signature_threshold_action = cfg.ipt.addMenuItem(cfg.basic_tools_menu, cfg.utls.algorithmThresholdTab, "semiautomaticclassificationplugin_threshold_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Signature threshold"))
		# LCS threshold
		LCS_threshold_action = cfg.ipt.addMenuItem(cfg.basic_tools_menu, cfg.utls.LCSThresholdTab, "semiautomaticclassificationplugin_LCS_threshold_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "LCS threshold"))
		# Download
		cfg.download_products_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.downloadImagesTab, "semiautomaticclassificationplugin_download_arrow.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Download products"))
		# Preprocessing
		cfg.preprocessing_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_class_tool.png"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Preprocessing"))
		# Landsat
		landsat_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.landsatTab, "semiautomaticclassificationplugin_landsat8_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Landsat"))
		# Sentinel-2
		sentinel2_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.sentinel2Tab, "semiautomaticclassificationplugin_sentinel_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Sentinel-2"))
		# Sentinel-3
		sentinel3_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.sentinel3Tab, "semiautomaticclassificationplugin_sentinel3_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Sentinel-3"))
		# ASTER
		aster_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.asterTab, "semiautomaticclassificationplugin_aster_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "ASTER"))
		# MODIS
		modis_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.modisTab, "semiautomaticclassificationplugin_modis_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "MODIS"))
		# Vector to raster
		vector_to_raster_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.vectorToRasterTab, "semiautomaticclassificationplugin_vector_to_raster_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Vector to raster"))
		# Clip multiple rasters
		clip_multiple_rasters_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.clipMultipleRastersTab, "semiautomaticclassificationplugin_clip_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Clip multiple rasters"))
		# Split raster bands
		split_raster_bands_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.splitrasterbandsTab, "semiautomaticclassificationplugin_split_raster.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Split raster bands"))
		# Stack raster bands
		stack_raster_bands_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.stackrasterbandsTab, "semiautomaticclassificationplugin_stack_raster.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Stack raster bands"))
		# Mosaic bands
		mosaic_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.mosaicTab, "semiautomaticclassificationplugin_mosaic_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Mosaic band sets"))
		# Cloud masking
		cloud_mask_action = cfg.ipt.addMenuItem(cfg.preprocessing_menu, cfg.utls.cloudMaskingTab, "semiautomaticclassificationplugin_cloud_masking_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Cloud masking"))
		# Band processing
		cfg.band_processing_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_band_processing.png"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band processing"))
		# Band combination
		band_combination_action = cfg.ipt.addMenuItem(cfg.band_processing_menu, cfg.utls.bandCombinationTab, "semiautomaticclassificationplugin_band_combination_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band combination"))
		# PCA
		PCA_action = cfg.ipt.addMenuItem(cfg.band_processing_menu, cfg.utls.PCATab, "semiautomaticclassificationplugin_pca_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "PCA"))
		# k-means
		Kmeans_action = cfg.ipt.addMenuItem(cfg.band_processing_menu, cfg.utls.clusteringTab, "semiautomaticclassificationplugin_kmeans_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Clustering"))
		# spectral distance
		spectral_distance_action = cfg.ipt.addMenuItem(cfg.band_processing_menu, cfg.utls.spectralDistanceTab, "semiautomaticclassificationplugin_spectral_distance.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Spectral distance"))
		# Postprocessing
		cfg.postprocessing_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_post_process.png"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Postprocessing"))
		# Accuracy
		accuracy_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.accuracyTab, "semiautomaticclassificationplugin_accuracy_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Accuracy"))
		# Land cover change
		land_cover_change_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.landCoverChangeTab, "semiautomaticclassificationplugin_land_cover_change.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Land cover change"))
		# Classification report
		classification_report_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classificationReportTab, "semiautomaticclassificationplugin_report_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification report"))
		# Cross classification
		cross_classification_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.crossClassificationTab, "semiautomaticclassificationplugin_cross_classification.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Cross classification"))
		# Class signature
		class_to_vector_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classSignatureTab, "semiautomaticclassificationplugin_class_signature_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Class signature"))
		# Classification to vector
		class_to_vector_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classToVectorTab, "semiautomaticclassificationplugin_class_to_vector_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification to vector"))
		# Reclassification
		reclassification_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.reclassificationTab, "semiautomaticclassificationplugin_reclassification_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Reclassification"))
		# Edit raster
		edit_raster_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.editRasterTab, "semiautomaticclassificationplugin_edit_raster.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Edit raster"))
		# Classification sieve
		classification_sieve_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classificationSieveTab, "semiautomaticclassificationplugin_classification_sieve.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification sieve"))
		# Classification erosion
		classification_erosion_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classificationErosionTab, "semiautomaticclassificationplugin_classification_erosion.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification erosion"))
		# Classification dilation
		classification_erosion_action = cfg.ipt.addMenuItem(cfg.postprocessing_menu, cfg.utls.classificationDilationTab, "semiautomaticclassificationplugin_classification_dilation.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Classification dilation"))
		# Band calc
		bandcalc_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.bandCalcTab, "semiautomaticclassificationplugin_bandcalc_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band calc"))
		# batch
		batch_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.batchTab, "semiautomaticclassificationplugin_batch.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Batch"))
		# Settings
		cfg.settings_menu = cfg.menu.addMenu(cfg.QtGuiSCP.QIcon(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_settings_tool.png"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Settings"))
		# Settings processing
		self.settings_processing_action = cfg.QtWidgetsSCP.QAction(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Processing"), cfg.iface.mainWindow())
		self.settings_processing_action.setObjectName("settings_processing_action")
		self.settings_processing_action.triggered.connect(cfg.utls.settingsProcessingTab)
		cfg.settings_menu.addAction(self.settings_processing_action)
		# Settings interface
		self.settings_interface_action = cfg.QtWidgetsSCP.QAction(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Interface"), cfg.iface.mainWindow())
		self.settings_interface_action.setObjectName("settings_interface_action")
		self.settings_interface_action.triggered.connect(cfg.utls.settingsInterfaceTab)
		cfg.settings_menu.addAction(self.settings_interface_action)
		# Settings debug
		self.settings_debug_action = cfg.QtWidgetsSCP.QAction(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Debug"), cfg.iface.mainWindow())
		self.settings_debug_action.setObjectName("settings_debug_action")
		self.settings_debug_action.triggered.connect(cfg.utls.settingsDebugTab)
		cfg.settings_menu.addAction(self.settings_debug_action)
		# Spectral plot
		spectral_plot_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.spectralPlotTab, "semiautomaticclassificationplugin_sign_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Spectral plot"))	
		# scatter plot
		scatter_plot_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.scatterPlotTab, "semiautomaticclassificationplugin_scatter_tool.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Scatter plot"))
		# User manual
		userguide_action = cfg.ipt.addMenuItem(cfg.menu, cfg.ipt.quickGuide, "guide.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "User manual"))
		# help
		help_action = cfg.ipt.addMenuItem(cfg.menu, cfg.ipt.askHelp, "help.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Online help"))
		# About
		about_action = cfg.ipt.addMenuItem(cfg.menu, cfg.utls.aboutTab, "fromGIStoRS.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "About"))
		# show plugin
		show_action = cfg.ipt.addMenuItem(cfg.menu, self.showPlugin, "semiautomaticclassificationplugin_docks.png", cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Show plugin"))
		
	# set SCP dock tabs buttons
	def setSCPDockTabs(self):
		icons = [":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_bandset_tool", ":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_roi_tool", ":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_download_arrow", ":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_class_tool", ":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_band_processing", ":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_post_process", ":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_bandcalc_tool"]
		for i in range(3, 10):
			lbl = cfg.QtWidgetsSCP.QLabel()
			lbl.setStyleSheet(_fromUtf8("color : black"))
			lbl.setObjectName(_fromUtf8("lbl"))
			lbl.setPixmap(cfg.QtGuiSCP.QPixmap(icons[i-3]).scaled(24,24,cfg.QtSCP.KeepAspectRatio))
			lbl.setAlignment(cfg.QtSCP.AlignCenter)
			cfg.uidc.tabWidget_dock.tabBar().setTabButton(i, cfg.QtWidgetsSCP.QTabBar.LeftSide, lbl)
		
	# dock tab index
	def dockTabChanged(self, index):
		if index > 2:
			item = cfg.ui.menu_tableWidget.item(index - 3, 0)
			cfg.ui.menu_tableWidget.setCurrentItem(item)
			cfg.uidc.tabWidget_dock.setCurrentIndex(cfg.dockIndex)
			cfg.dlg.close()
			cfg.dlg.show()
		else:
			cfg.dockIndex = cfg.uidc.tabWidget_dock.currentIndex()

	# SCP tab index
	def SCPTabChanged(self, index):
		cfg.ui.menu_tableWidget.blockSignals(True)
		item = cfg.ui.menu_tableWidget.item(index, 0)
		cfg.ui.menu_tableWidget.setCurrentItem(item)
		cfg.ui.menu_tableWidget.blockSignals(False)

	# menu index
	def menuIndex(self):
		tW = cfg.ui.menu_tableWidget
		c = tW.currentRow()
		cfg.ui.SCP_tabs.blockSignals(True)
		cfg.ui.SCP_tabs.setCurrentIndex(c)
		cfg.ui.SCP_tabs.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
	
	# menu Clicked
	def menuClicked(self, index):
		c = index.row()
		if c == 10:
			cfg.ipt.quickGuide()
		elif c == 11:
			cfg.ipt.askHelp()
		elif c == 12:
			cfg.ipt.supportSCP()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
	
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
		