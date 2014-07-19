# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_semiautomaticclassificationplugin_dock.ui'
#
# Created: Sat Jul 19 14:53:19 2014
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dock(object):
    def setupUi(self, Dock):
        Dock.setObjectName(_fromUtf8("Dock"))
        Dock.resize(396, 784)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dock.sizePolicy().hasHeightForWidth())
        Dock.setSizePolicy(sizePolicy)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout_3 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout_14 = QtGui.QGridLayout()
        self.gridLayout_14.setObjectName(_fromUtf8("gridLayout_14"))
        self.label_32 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_32.setFont(font)
        self.label_32.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_32.setObjectName(_fromUtf8("label_32"))
        self.gridLayout_14.addWidget(self.label_32, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_14, 0, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonReload_shape = QtGui.QToolButton(self.dockWidgetContents)
        self.buttonReload_shape.setObjectName(_fromUtf8("buttonReload_shape"))
        self.gridLayout.addWidget(self.buttonReload_shape, 0, 1, 1, 1)
        self.button_new_shapefile = QtGui.QToolButton(self.dockWidgetContents)
        self.button_new_shapefile.setObjectName(_fromUtf8("button_new_shapefile"))
        self.gridLayout.addWidget(self.button_new_shapefile, 0, 2, 1, 1)
        self.shape_name_combo = QtGui.QComboBox(self.dockWidgetContents)
        self.shape_name_combo.setObjectName(_fromUtf8("shape_name_combo"))
        self.gridLayout.addWidget(self.shape_name_combo, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 1, 0, 1, 1)
        self.gridLayout_11 = QtGui.QGridLayout()
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.label_31 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_31.setFont(font)
        self.label_31.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_31.setObjectName(_fromUtf8("label_31"))
        self.gridLayout_11.addWidget(self.label_31, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_11, 2, 0, 1, 1)
        self.ROI_tableWidget = QtGui.QTableWidget(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ROI_tableWidget.sizePolicy().hasHeightForWidth())
        self.ROI_tableWidget.setSizePolicy(sizePolicy)
        self.ROI_tableWidget.setMinimumSize(QtCore.QSize(0, 100))
        self.ROI_tableWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.ROI_tableWidget.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.ROI_tableWidget.setDragDropOverwriteMode(False)
        self.ROI_tableWidget.setObjectName(_fromUtf8("ROI_tableWidget"))
        self.ROI_tableWidget.setColumnCount(4)
        self.ROI_tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.ROI_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.ROI_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.ROI_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.ROI_tableWidget.setHorizontalHeaderItem(3, item)
        self.ROI_tableWidget.horizontalHeader().setDefaultSectionSize(80)
        self.ROI_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.ROI_tableWidget.verticalHeader().setDefaultSectionSize(20)
        self.gridLayout_3.addWidget(self.ROI_tableWidget, 3, 0, 1, 1)
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.spectralSignature_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_sign_tool.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.spectralSignature_toolButton.setIcon(icon)
        self.spectralSignature_toolButton.setObjectName(_fromUtf8("spectralSignature_toolButton"))
        self.gridLayout_5.addWidget(self.spectralSignature_toolButton, 0, 2, 1, 1)
        self.addToSignature_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.addToSignature_toolButton.setObjectName(_fromUtf8("addToSignature_toolButton"))
        self.gridLayout_5.addWidget(self.addToSignature_toolButton, 0, 0, 1, 1)
        self.scatterPlot_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_scatter_tool.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.scatterPlot_toolButton.setIcon(icon1)
        self.scatterPlot_toolButton.setObjectName(_fromUtf8("scatterPlot_toolButton"))
        self.gridLayout_5.addWidget(self.scatterPlot_toolButton, 0, 3, 1, 1)
        self.deleteROI_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_delete_ROI.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.deleteROI_toolButton.setIcon(icon2)
        self.deleteROI_toolButton.setObjectName(_fromUtf8("deleteROI_toolButton"))
        self.gridLayout_5.addWidget(self.deleteROI_toolButton, 0, 4, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_5, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 5, 0, 1, 1)
        self.gridLayout_9 = QtGui.QGridLayout()
        self.gridLayout_9.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.label_30 = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_30.sizePolicy().hasHeightForWidth())
        self.label_30.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_30.setFont(font)
        self.label_30.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.gridLayout_9.addWidget(self.label_30, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_9, 6, 0, 1, 1)
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setVerticalSpacing(4)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_46 = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_46.sizePolicy().hasHeightForWidth())
        self.label_46.setSizePolicy(sizePolicy)
        self.label_46.setFrameShape(QtGui.QFrame.Panel)
        self.label_46.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_46.setObjectName(_fromUtf8("label_46"))
        self.gridLayout_4.addWidget(self.label_46, 1, 0, 1, 1)
        self.Max_ROI_width_spin = QtGui.QSpinBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Max_ROI_width_spin.sizePolicy().hasHeightForWidth())
        self.Max_ROI_width_spin.setSizePolicy(sizePolicy)
        self.Max_ROI_width_spin.setMinimumSize(QtCore.QSize(105, 0))
        self.Max_ROI_width_spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.Max_ROI_width_spin.setMinimum(1)
        self.Max_ROI_width_spin.setMaximum(10000)
        self.Max_ROI_width_spin.setProperty("value", 100)
        self.Max_ROI_width_spin.setObjectName(_fromUtf8("Max_ROI_width_spin"))
        self.gridLayout_4.addWidget(self.Max_ROI_width_spin, 2, 1, 1, 1)
        self.rapid_ROI_checkBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.rapid_ROI_checkBox.setObjectName(_fromUtf8("rapid_ROI_checkBox"))
        self.gridLayout_4.addWidget(self.rapid_ROI_checkBox, 3, 1, 1, 1)
        self.rapidROI_band_spinBox = QtGui.QSpinBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rapidROI_band_spinBox.sizePolicy().hasHeightForWidth())
        self.rapidROI_band_spinBox.setSizePolicy(sizePolicy)
        self.rapidROI_band_spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.rapidROI_band_spinBox.setMinimum(1)
        self.rapidROI_band_spinBox.setMaximum(10000)
        self.rapidROI_band_spinBox.setProperty("value", 1)
        self.rapidROI_band_spinBox.setObjectName(_fromUtf8("rapidROI_band_spinBox"))
        self.gridLayout_4.addWidget(self.rapidROI_band_spinBox, 4, 1, 1, 1)
        self.Range_radius_spin = QtGui.QDoubleSpinBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Range_radius_spin.sizePolicy().hasHeightForWidth())
        self.Range_radius_spin.setSizePolicy(sizePolicy)
        self.Range_radius_spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.Range_radius_spin.setDecimals(6)
        self.Range_radius_spin.setMinimum(1e-06)
        self.Range_radius_spin.setMaximum(10000.0)
        self.Range_radius_spin.setSingleStep(0.01)
        self.Range_radius_spin.setProperty("value", 0.01)
        self.Range_radius_spin.setObjectName(_fromUtf8("Range_radius_spin"))
        self.gridLayout_4.addWidget(self.Range_radius_spin, 4, 0, 1, 1)
        self.label_47 = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_47.sizePolicy().hasHeightForWidth())
        self.label_47.setSizePolicy(sizePolicy)
        self.label_47.setFrameShape(QtGui.QFrame.Panel)
        self.label_47.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_47.setObjectName(_fromUtf8("label_47"))
        self.gridLayout_4.addWidget(self.label_47, 1, 1, 1, 1)
        self.Min_region_size_spin = QtGui.QSpinBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Min_region_size_spin.sizePolicy().hasHeightForWidth())
        self.Min_region_size_spin.setSizePolicy(sizePolicy)
        self.Min_region_size_spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.Min_region_size_spin.setMinimum(1)
        self.Min_region_size_spin.setMaximum(10000)
        self.Min_region_size_spin.setProperty("value", 60)
        self.Min_region_size_spin.setObjectName(_fromUtf8("Min_region_size_spin"))
        self.gridLayout_4.addWidget(self.Min_region_size_spin, 2, 0, 1, 1)
        self.label_49 = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_49.sizePolicy().hasHeightForWidth())
        self.label_49.setSizePolicy(sizePolicy)
        self.label_49.setFrameShape(QtGui.QFrame.Panel)
        self.label_49.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_49.setObjectName(_fromUtf8("label_49"))
        self.gridLayout_4.addWidget(self.label_49, 3, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_4, 7, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 8, 0, 1, 1)
        self.gridLayout_15 = QtGui.QGridLayout()
        self.gridLayout_15.setObjectName(_fromUtf8("gridLayout_15"))
        self.label_51 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_51.setFont(font)
        self.label_51.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_51.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_51.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_51.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_51.setObjectName(_fromUtf8("label_51"))
        self.gridLayout_15.addWidget(self.label_51, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_15, 9, 0, 1, 1)
        self.gridLayout_6 = QtGui.QGridLayout()
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.polygonROI_Button = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.polygonROI_Button.sizePolicy().hasHeightForWidth())
        self.polygonROI_Button.setSizePolicy(sizePolicy)
        self.polygonROI_Button.setMinimumSize(QtCore.QSize(40, 27))
        self.polygonROI_Button.setMaximumSize(QtCore.QSize(30, 27))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.polygonROI_Button.setFont(font)
        self.polygonROI_Button.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.polygonROI_Button.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_manual_ROI.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.polygonROI_Button.setIcon(icon3)
        self.polygonROI_Button.setIconSize(QtCore.QSize(18, 18))
        self.polygonROI_Button.setCheckable(False)
        self.polygonROI_Button.setFlat(False)
        self.polygonROI_Button.setObjectName(_fromUtf8("polygonROI_Button"))
        self.gridLayout_6.addWidget(self.polygonROI_Button, 0, 4, 1, 1)
        self.pointerButton = QtGui.QPushButton(self.dockWidgetContents)
        self.pointerButton.setMinimumSize(QtCore.QSize(85, 27))
        self.pointerButton.setMaximumSize(QtCore.QSize(31, 27))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.pointerButton.setFont(font)
        self.pointerButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pointerButton.setCheckable(False)
        self.pointerButton.setFlat(False)
        self.pointerButton.setObjectName(_fromUtf8("pointerButton"))
        self.gridLayout_6.addWidget(self.pointerButton, 0, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem2, 0, 3, 1, 1)
        self.mutlipleROI_Button = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mutlipleROI_Button.sizePolicy().hasHeightForWidth())
        self.mutlipleROI_Button.setSizePolicy(sizePolicy)
        self.mutlipleROI_Button.setMinimumSize(QtCore.QSize(40, 27))
        self.mutlipleROI_Button.setMaximumSize(QtCore.QSize(30, 27))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.mutlipleROI_Button.setFont(font)
        self.mutlipleROI_Button.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.mutlipleROI_Button.setText(_fromUtf8(""))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_roi_multiple.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mutlipleROI_Button.setIcon(icon4)
        self.mutlipleROI_Button.setIconSize(QtCore.QSize(18, 18))
        self.mutlipleROI_Button.setCheckable(False)
        self.mutlipleROI_Button.setFlat(False)
        self.mutlipleROI_Button.setObjectName(_fromUtf8("mutlipleROI_Button"))
        self.gridLayout_6.addWidget(self.mutlipleROI_Button, 0, 6, 1, 1)
        self.redo_ROI_Button = QtGui.QPushButton(self.dockWidgetContents)
        self.redo_ROI_Button.setEnabled(False)
        self.redo_ROI_Button.setMaximumSize(QtCore.QSize(75, 16777215))
        self.redo_ROI_Button.setObjectName(_fromUtf8("redo_ROI_Button"))
        self.gridLayout_6.addWidget(self.redo_ROI_Button, 0, 2, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem3, 0, 1, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem4, 0, 5, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_6, 10, 0, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem5, 11, 0, 1, 1)
        self.gridLayout_10 = QtGui.QGridLayout()
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.label_43 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_43.setFont(font)
        self.label_43.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_43.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_43.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_43.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_43.setObjectName(_fromUtf8("label_43"))
        self.gridLayout_10.addWidget(self.label_43, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_10, 12, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setVerticalSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_44 = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_44.sizePolicy().hasHeightForWidth())
        self.label_44.setSizePolicy(sizePolicy)
        self.label_44.setMaximumSize(QtCore.QSize(90, 16777215))
        self.label_44.setFrameShape(QtGui.QFrame.Panel)
        self.label_44.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_44.setObjectName(_fromUtf8("label_44"))
        self.gridLayout_2.addWidget(self.label_44, 2, 0, 1, 1)
        self.gridLayout_13 = QtGui.QGridLayout()
        self.gridLayout_13.setObjectName(_fromUtf8("gridLayout_13"))
        self.button_Save_ROI = QtGui.QPushButton(self.dockWidgetContents)
        self.button_Save_ROI.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_Save_ROI.sizePolicy().hasHeightForWidth())
        self.button_Save_ROI.setSizePolicy(sizePolicy)
        self.button_Save_ROI.setObjectName(_fromUtf8("button_Save_ROI"))
        self.gridLayout_13.addWidget(self.button_Save_ROI, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_13, 9, 0, 1, 2)
        self.ROI_Macroclass_ID_spin = QtGui.QSpinBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ROI_Macroclass_ID_spin.sizePolicy().hasHeightForWidth())
        self.ROI_Macroclass_ID_spin.setSizePolicy(sizePolicy)
        self.ROI_Macroclass_ID_spin.setMaximumSize(QtCore.QSize(100, 16777215))
        self.ROI_Macroclass_ID_spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.ROI_Macroclass_ID_spin.setMinimum(1)
        self.ROI_Macroclass_ID_spin.setMaximum(9999)
        self.ROI_Macroclass_ID_spin.setProperty("value", 1)
        self.ROI_Macroclass_ID_spin.setObjectName(_fromUtf8("ROI_Macroclass_ID_spin"))
        self.gridLayout_2.addWidget(self.ROI_Macroclass_ID_spin, 3, 0, 1, 2)
        self.ROI_ID_spin = QtGui.QSpinBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ROI_ID_spin.sizePolicy().hasHeightForWidth())
        self.ROI_ID_spin.setSizePolicy(sizePolicy)
        self.ROI_ID_spin.setMaximumSize(QtCore.QSize(100, 16777215))
        self.ROI_ID_spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.ROI_ID_spin.setMinimum(1)
        self.ROI_ID_spin.setMaximum(9999)
        self.ROI_ID_spin.setProperty("value", 1)
        self.ROI_ID_spin.setObjectName(_fromUtf8("ROI_ID_spin"))
        self.gridLayout_2.addWidget(self.ROI_ID_spin, 5, 0, 1, 1)
        self.ROI_Class_line = QtGui.QLineEdit(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ROI_Class_line.sizePolicy().hasHeightForWidth())
        self.ROI_Class_line.setSizePolicy(sizePolicy)
        self.ROI_Class_line.setMaxLength(80)
        self.ROI_Class_line.setObjectName(_fromUtf8("ROI_Class_line"))
        self.gridLayout_2.addWidget(self.ROI_Class_line, 5, 3, 1, 1)
        self.label_41 = QtGui.QLabel(self.dockWidgetContents)
        self.label_41.setFrameShape(QtGui.QFrame.Panel)
        self.label_41.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_41.setObjectName(_fromUtf8("label_41"))
        self.gridLayout_2.addWidget(self.label_41, 4, 3, 1, 1)
        self.label_45 = QtGui.QLabel(self.dockWidgetContents)
        self.label_45.setFrameShape(QtGui.QFrame.Panel)
        self.label_45.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_45.setObjectName(_fromUtf8("label_45"))
        self.gridLayout_2.addWidget(self.label_45, 2, 3, 1, 1)
        self.ROI_Macroclass_line = QtGui.QLineEdit(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ROI_Macroclass_line.sizePolicy().hasHeightForWidth())
        self.ROI_Macroclass_line.setSizePolicy(sizePolicy)
        self.ROI_Macroclass_line.setMaxLength(80)
        self.ROI_Macroclass_line.setObjectName(_fromUtf8("ROI_Macroclass_line"))
        self.gridLayout_2.addWidget(self.ROI_Macroclass_line, 3, 3, 1, 1)
        self.gridLayout_12 = QtGui.QGridLayout()
        self.gridLayout_12.setObjectName(_fromUtf8("gridLayout_12"))
        self.undo_save_Button = QtGui.QPushButton(self.dockWidgetContents)
        self.undo_save_Button.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.undo_save_Button.sizePolicy().hasHeightForWidth())
        self.undo_save_Button.setSizePolicy(sizePolicy)
        self.undo_save_Button.setMaximumSize(QtCore.QSize(140, 16777215))
        self.undo_save_Button.setObjectName(_fromUtf8("undo_save_Button"))
        self.gridLayout_12.addWidget(self.undo_save_Button, 0, 2, 1, 1)
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_12.addItem(spacerItem6, 0, 1, 1, 1)
        self.signature_checkBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.signature_checkBox.setChecked(True)
        self.signature_checkBox.setObjectName(_fromUtf8("signature_checkBox"))
        self.gridLayout_12.addWidget(self.signature_checkBox, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_12, 9, 3, 1, 1)
        self.label_42 = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_42.sizePolicy().hasHeightForWidth())
        self.label_42.setSizePolicy(sizePolicy)
        self.label_42.setMaximumSize(QtCore.QSize(89, 16777215))
        self.label_42.setFrameShape(QtGui.QFrame.Panel)
        self.label_42.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_42.setObjectName(_fromUtf8("label_42"))
        self.gridLayout_2.addWidget(self.label_42, 4, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 13, 0, 1, 1)
        Dock.setWidget(self.dockWidgetContents)
        self.label_47.setBuddy(self.pointerButton)

        self.retranslateUi(Dock)
        QtCore.QMetaObject.connectSlotsByName(Dock)

    def retranslateUi(self, Dock):
        Dock.setWindowTitle(_translate("Dock", "SCP: ROI creation", None))
        self.label_32.setText(_translate("Dock", " Training shapefile", None))
        self.buttonReload_shape.setToolTip(_translate("Dock", "<html><head/><body><p>Refresh list</p></body></html>", None))
        self.buttonReload_shape.setText(_translate("Dock", "↺", None))
        self.button_new_shapefile.setToolTip(_translate("Dock", "<html><head/><body><p>Create a new training shapefile</p></body></html>", None))
        self.button_new_shapefile.setText(_translate("Dock", "New shp", None))
        self.shape_name_combo.setToolTip(_translate("Dock", "<html><head/><body><p>Select a layer</p></body></html>", None))
        self.label_31.setText(_translate("Dock", " ROI list", None))
        self.ROI_tableWidget.setSortingEnabled(True)
        item = self.ROI_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Dock", "MC ID", None))
        item = self.ROI_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Dock", "MC Info", None))
        item = self.ROI_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Dock", "C ID", None))
        item = self.ROI_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Dock", "C Info", None))
        self.spectralSignature_toolButton.setToolTip(_translate("Dock", "<html><head/><body><p>Add highlihted ROIs to spectral signature plot</p></body></html>", None))
        self.spectralSignature_toolButton.setText(_translate("Dock", "...", None))
        self.addToSignature_toolButton.setToolTip(_translate("Dock", "<html><head/><body><p>Add highlighted ROIs to signature list</p></body></html>", None))
        self.addToSignature_toolButton.setText(_translate("Dock", "Add to signature", None))
        self.scatterPlot_toolButton.setToolTip(_translate("Dock", "<html><head/><body><p>Show scatter plot</p></body></html>", None))
        self.scatterPlot_toolButton.setText(_translate("Dock", "...", None))
        self.deleteROI_toolButton.setToolTip(_translate("Dock", "<html><head/><body><p>Delete highlighted ROIs</p></body></html>", None))
        self.deleteROI_toolButton.setText(_translate("Dock", "Delete", None))
        self.label_30.setText(_translate("Dock", " ROI parameters", None))
        self.label_46.setText(_translate("Dock", "Min ROI size      ", None))
        self.Max_ROI_width_spin.setToolTip(_translate("Dock", "<html><head/><body><p align=\"justify\">Side of a square which inscribes the ROI, defining the maximum width thereof (in pixel unit)</p></body></html>", None))
        self.rapid_ROI_checkBox.setToolTip(_translate("Dock", "<html><head/><body><p>Calculate ROI only on one band</p></body></html>", None))
        self.rapid_ROI_checkBox.setText(_translate("Dock", "Rapid ROI on band", None))
        self.rapidROI_band_spinBox.setToolTip(_translate("Dock", "<html><head/><body><p>Band number</p></body></html>", None))
        self.Range_radius_spin.setToolTip(_translate("Dock", "<html><head/><body><p align=\"justify\">Radius in the multispectral space (in radiometry unit)</p></body></html>", None))
        self.label_47.setText(_translate("Dock", "Max ROI width   ", None))
        self.Min_region_size_spin.setToolTip(_translate("Dock", "<html><head/><body><p>Minimum area of ROI (in pixel unit)</p></body></html>", None))
        self.label_49.setText(_translate("Dock", "Range radius", None))
        self.label_51.setText(_translate("Dock", " ROI creation", None))
        self.polygonROI_Button.setToolTip(_translate("Dock", "<html><head/><body><p><span style=\" font-size:10pt;\">Create a ROI polygon</span></p></body></html>", None))
        self.pointerButton.setToolTip(_translate("Dock", "<html><head/><body><p><span style=\" font-size:10pt;\">Activate ROI pointer</span></p></body></html>", None))
        self.pointerButton.setText(_translate("Dock", "+", None))
        self.mutlipleROI_Button.setToolTip(_translate("Dock", "<html><head/><body><p><span style=\" font-size:10pt;\">Multiple ROI creation</span></p></body></html>", None))
        self.redo_ROI_Button.setToolTip(_translate("Dock", "<html><head/><body><p>Redo the ROI at the same point</p></body></html>", None))
        self.redo_ROI_Button.setText(_translate("Dock", "Redo ↺", None))
        self.label_43.setText(_translate("Dock", " ROI Signature definition", None))
        self.label_44.setText(_translate("Dock", "Macroclass ID", None))
        self.button_Save_ROI.setToolTip(_translate("Dock", "<html><head/><body><p>Save the last ROI to training shapefile</p></body></html>", None))
        self.button_Save_ROI.setText(_translate("Dock", "Save ROI", None))
        self.ROI_Macroclass_ID_spin.setToolTip(_translate("Dock", "<html><head/><body><p>The ID of the signature macroclass</p></body></html>", None))
        self.ROI_ID_spin.setToolTip(_translate("Dock", "<html><head/><body><p>The ID of the signature class</p></body></html>", None))
        self.ROI_Class_line.setToolTip(_translate("Dock", "<html><head/><body><p>The class name of the ROI signature</p></body></html>", None))
        self.ROI_Class_line.setText(_translate("Dock", "Class_1", None))
        self.label_41.setText(_translate("Dock", "Class Information", None))
        self.label_45.setText(_translate("Dock", "Macroclass Information", None))
        self.ROI_Macroclass_line.setToolTip(_translate("Dock", "<html><head/><body><p>The macroclass name of the ROI signature</p></body></html>", None))
        self.ROI_Macroclass_line.setText(_translate("Dock", "Macroclass_1", None))
        self.undo_save_Button.setToolTip(_translate("Dock", "<html><head/><body><p>Delete the last saved ROI</p></body></html>", None))
        self.undo_save_Button.setText(_translate("Dock", "↶ Undo", None))
        self.signature_checkBox.setToolTip(_translate("Dock", "<html><head/><body><p>Add ROI spectral signature to signature list</p></body></html>", None))
        self.signature_checkBox.setText(_translate("Dock", "Add sig. list", None))
        self.label_42.setText(_translate("Dock", "Class ID", None))

import resources_rc
