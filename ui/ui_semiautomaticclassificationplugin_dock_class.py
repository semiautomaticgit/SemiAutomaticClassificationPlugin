# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_semiautomaticclassificationplugin_dock_class.ui'
#
# Created: Sat Jul 19 14:53:20 2014
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

class Ui_DockClass(object):
    def setupUi(self, DockClass):
        DockClass.setObjectName(_fromUtf8("DockClass"))
        DockClass.resize(353, 813)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DockClass.sizePolicy().hasHeightForWidth())
        DockClass.setSizePolicy(sizePolicy)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout_3 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout_6 = QtGui.QGridLayout()
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_38 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_38.setFont(font)
        self.label_38.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_38.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_38.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_38.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_38.setObjectName(_fromUtf8("label_38"))
        self.gridLayout_6.addWidget(self.label_38, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_6, 0, 0, 1, 1)
        self.gridLayout_15 = QtGui.QGridLayout()
        self.gridLayout_15.setObjectName(_fromUtf8("gridLayout_15"))
        self.open_signature_list_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.open_signature_list_toolButton.setObjectName(_fromUtf8("open_signature_list_toolButton"))
        self.gridLayout_15.addWidget(self.open_signature_list_toolButton, 0, 0, 1, 1)
        self.signatureFile_lineEdit = QtGui.QLineEdit(self.dockWidgetContents)
        self.signatureFile_lineEdit.setEnabled(False)
        self.signatureFile_lineEdit.setObjectName(_fromUtf8("signatureFile_lineEdit"))
        self.gridLayout_15.addWidget(self.signatureFile_lineEdit, 0, 1, 1, 1)
        self.save_signature_list_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.save_signature_list_toolButton.setObjectName(_fromUtf8("save_signature_list_toolButton"))
        self.gridLayout_15.addWidget(self.save_signature_list_toolButton, 0, 2, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_15, 1, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_37 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_37.setFont(font)
        self.label_37.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_37.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_37.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_37.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_37.setObjectName(_fromUtf8("label_37"))
        self.gridLayout.addWidget(self.label_37, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 2, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.signature_list_tableWidget = QtGui.QTableWidget(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.signature_list_tableWidget.sizePolicy().hasHeightForWidth())
        self.signature_list_tableWidget.setSizePolicy(sizePolicy)
        self.signature_list_tableWidget.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.signature_list_tableWidget.setObjectName(_fromUtf8("signature_list_tableWidget"))
        self.signature_list_tableWidget.setColumnCount(6)
        self.signature_list_tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.signature_list_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_tableWidget.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_tableWidget.setHorizontalHeaderItem(5, item)
        self.signature_list_tableWidget.horizontalHeader().setDefaultSectionSize(50)
        self.signature_list_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.signature_list_tableWidget.verticalHeader().setDefaultSectionSize(20)
        self.gridLayout_2.addWidget(self.signature_list_tableWidget, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 3, 0, 1, 1)
        self.gridLayout_16 = QtGui.QGridLayout()
        self.gridLayout_16.setObjectName(_fromUtf8("gridLayout_16"))
        self.export_CSV_library_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_export_sign_to_csv.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.export_CSV_library_toolButton.setIcon(icon)
        self.export_CSV_library_toolButton.setObjectName(_fromUtf8("export_CSV_library_toolButton"))
        self.gridLayout_16.addWidget(self.export_CSV_library_toolButton, 0, 4, 1, 1)
        self.delete_Signature_Button = QtGui.QToolButton(self.dockWidgetContents)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_delete_signature.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_Signature_Button.setIcon(icon1)
        self.delete_Signature_Button.setObjectName(_fromUtf8("delete_Signature_Button"))
        self.gridLayout_16.addWidget(self.delete_Signature_Button, 0, 1, 1, 1)
        self.import_library_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_import_spectral_library.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.import_library_toolButton.setIcon(icon2)
        self.import_library_toolButton.setObjectName(_fromUtf8("import_library_toolButton"))
        self.gridLayout_16.addWidget(self.import_library_toolButton, 0, 2, 1, 1)
        self.import_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.import_toolButton.setObjectName(_fromUtf8("import_toolButton"))
        self.gridLayout_16.addWidget(self.import_toolButton, 0, 8, 1, 1)
        self.export_signature_list_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        self.export_signature_list_toolButton.setObjectName(_fromUtf8("export_signature_list_toolButton"))
        self.gridLayout_16.addWidget(self.export_signature_list_toolButton, 0, 7, 1, 1)
        self.signature_spectral_plot_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_sign_tool.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.signature_spectral_plot_toolButton.setIcon(icon3)
        self.signature_spectral_plot_toolButton.setObjectName(_fromUtf8("signature_spectral_plot_toolButton"))
        self.gridLayout_16.addWidget(self.signature_spectral_plot_toolButton, 0, 5, 1, 1)
        self.import_usgs_library_toolButton = QtGui.QToolButton(self.dockWidgetContents)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin_import_USGS_spectral_library.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.import_usgs_library_toolButton.setIcon(icon4)
        self.import_usgs_library_toolButton.setObjectName(_fromUtf8("import_usgs_library_toolButton"))
        self.gridLayout_16.addWidget(self.import_usgs_library_toolButton, 0, 3, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_16, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 5, 0, 1, 1)
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_26 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_26.setFont(font)
        self.label_26.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_26.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_26.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_26.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.gridLayout_4.addWidget(self.label_26, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_4, 6, 0, 1, 1)
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setSpacing(4)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.algorithm_combo = QtGui.QComboBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.algorithm_combo.sizePolicy().hasHeightForWidth())
        self.algorithm_combo.setSizePolicy(sizePolicy)
        self.algorithm_combo.setMinimumSize(QtCore.QSize(100, 0))
        self.algorithm_combo.setObjectName(_fromUtf8("algorithm_combo"))
        self.algorithm_combo.addItem(_fromUtf8(""))
        self.algorithm_combo.addItem(_fromUtf8(""))
        self.algorithm_combo.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.algorithm_combo, 1, 0, 1, 1)
        self.label_14 = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setFrameShape(QtGui.QFrame.Panel)
        self.label_14.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_5.addWidget(self.label_14, 0, 0, 1, 1)
        self.alg_threshold_SpinBox = QtGui.QDoubleSpinBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.alg_threshold_SpinBox.sizePolicy().hasHeightForWidth())
        self.alg_threshold_SpinBox.setSizePolicy(sizePolicy)
        self.alg_threshold_SpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.alg_threshold_SpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.alg_threshold_SpinBox.setDecimals(4)
        self.alg_threshold_SpinBox.setMaximum(10000.0)
        self.alg_threshold_SpinBox.setObjectName(_fromUtf8("alg_threshold_SpinBox"))
        self.gridLayout_5.addWidget(self.alg_threshold_SpinBox, 1, 1, 1, 1)
        self.label_16 = QtGui.QLabel(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)
        self.label_16.setMaximumSize(QtCore.QSize(500, 16777215))
        self.label_16.setFrameShape(QtGui.QFrame.Panel)
        self.label_16.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_5.addWidget(self.label_16, 0, 1, 1, 1)
        self.macroclass_checkBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.macroclass_checkBox.setObjectName(_fromUtf8("macroclass_checkBox"))
        self.gridLayout_5.addWidget(self.macroclass_checkBox, 2, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_5, 7, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 8, 0, 1, 1)
        self.gridLayout_8 = QtGui.QGridLayout()
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.label_28 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_28.setFont(font)
        self.label_28.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_28.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_28.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_28.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_28.setObjectName(_fromUtf8("label_28"))
        self.gridLayout_8.addWidget(self.label_28, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_8, 9, 0, 1, 1)
        self.gridLayout_9 = QtGui.QGridLayout()
        self.gridLayout_9.setSpacing(4)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.preview_size_spinBox = QtGui.QSpinBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.preview_size_spinBox.sizePolicy().hasHeightForWidth())
        self.preview_size_spinBox.setSizePolicy(sizePolicy)
        self.preview_size_spinBox.setMaximumSize(QtCore.QSize(80, 16777215))
        self.preview_size_spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.preview_size_spinBox.setMinimum(1)
        self.preview_size_spinBox.setMaximum(1000000)
        self.preview_size_spinBox.setSingleStep(50)
        self.preview_size_spinBox.setProperty("value", 100)
        self.preview_size_spinBox.setObjectName(_fromUtf8("preview_size_spinBox"))
        self.gridLayout_9.addWidget(self.preview_size_spinBox, 0, 2, 1, 1)
        self.redo_Preview_Button = QtGui.QPushButton(self.dockWidgetContents)
        self.redo_Preview_Button.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.redo_Preview_Button.sizePolicy().hasHeightForWidth())
        self.redo_Preview_Button.setSizePolicy(sizePolicy)
        self.redo_Preview_Button.setMaximumSize(QtCore.QSize(75, 16777215))
        self.redo_Preview_Button.setObjectName(_fromUtf8("redo_Preview_Button"))
        self.gridLayout_9.addWidget(self.redo_Preview_Button, 0, 4, 1, 1)
        self.label_17 = QtGui.QLabel(self.dockWidgetContents)
        self.label_17.setFrameShape(QtGui.QFrame.Panel)
        self.label_17.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout_9.addWidget(self.label_17, 0, 1, 1, 1)
        self.pointerButton_preview = QtGui.QPushButton(self.dockWidgetContents)
        self.pointerButton_preview.setMinimumSize(QtCore.QSize(85, 27))
        self.pointerButton_preview.setMaximumSize(QtCore.QSize(31, 27))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.pointerButton_preview.setFont(font)
        self.pointerButton_preview.setCheckable(False)
        self.pointerButton_preview.setFlat(False)
        self.pointerButton_preview.setObjectName(_fromUtf8("pointerButton_preview"))
        self.gridLayout_9.addWidget(self.pointerButton_preview, 0, 5, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem2, 0, 3, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_9, 10, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem3, 11, 0, 1, 1)
        self.gridLayout_14 = QtGui.QGridLayout()
        self.gridLayout_14.setObjectName(_fromUtf8("gridLayout_14"))
        self.label_15 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_15.setFont(font)
        self.label_15.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_15.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_15.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_15.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout_14.addWidget(self.label_15, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_14, 12, 0, 1, 1)
        self.gridLayout_7 = QtGui.QGridLayout()
        self.gridLayout_7.setSpacing(4)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.qml_lineEdit = QtGui.QLineEdit(self.dockWidgetContents)
        self.qml_lineEdit.setEnabled(False)
        self.qml_lineEdit.setObjectName(_fromUtf8("qml_lineEdit"))
        self.gridLayout_7.addWidget(self.qml_lineEdit, 0, 1, 1, 1)
        self.qml_Button = QtGui.QPushButton(self.dockWidgetContents)
        self.qml_Button.setObjectName(_fromUtf8("qml_Button"))
        self.gridLayout_7.addWidget(self.qml_Button, 0, 0, 1, 1)
        self.resetQmlButton = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resetQmlButton.sizePolicy().hasHeightForWidth())
        self.resetQmlButton.setSizePolicy(sizePolicy)
        self.resetQmlButton.setMaximumSize(QtCore.QSize(49, 16777215))
        self.resetQmlButton.setObjectName(_fromUtf8("resetQmlButton"))
        self.gridLayout_7.addWidget(self.resetQmlButton, 0, 2, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_7, 13, 0, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem4, 14, 0, 1, 1)
        self.gridLayout_10 = QtGui.QGridLayout()
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.label_32 = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_32.setFont(font)
        self.label_32.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_32.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_32.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_32.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_32.setObjectName(_fromUtf8("label_32"))
        self.gridLayout_10.addWidget(self.label_32, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_10, 15, 0, 1, 1)
        self.gridLayout_11 = QtGui.QGridLayout()
        self.gridLayout_11.setSpacing(4)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.report_checkBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.report_checkBox.setObjectName(_fromUtf8("report_checkBox"))
        self.gridLayout_11.addWidget(self.report_checkBox, 3, 1, 1, 1)
        self.vector_output_checkBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.vector_output_checkBox.setObjectName(_fromUtf8("vector_output_checkBox"))
        self.gridLayout_11.addWidget(self.vector_output_checkBox, 3, 0, 1, 1)
        self.gridLayout_13 = QtGui.QGridLayout()
        self.gridLayout_13.setObjectName(_fromUtf8("gridLayout_13"))
        self.mask_checkBox = QtGui.QCheckBox(self.dockWidgetContents)
        self.mask_checkBox.setObjectName(_fromUtf8("mask_checkBox"))
        self.gridLayout_13.addWidget(self.mask_checkBox, 0, 0, 1, 1)
        self.mask_lineEdit = QtGui.QLineEdit(self.dockWidgetContents)
        self.mask_lineEdit.setEnabled(False)
        self.mask_lineEdit.setInputMethodHints(QtCore.Qt.ImhUrlCharactersOnly)
        self.mask_lineEdit.setText(_fromUtf8(""))
        self.mask_lineEdit.setObjectName(_fromUtf8("mask_lineEdit"))
        self.gridLayout_13.addWidget(self.mask_lineEdit, 0, 1, 1, 1)
        self.resetMaskButton = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resetMaskButton.sizePolicy().hasHeightForWidth())
        self.resetMaskButton.setSizePolicy(sizePolicy)
        self.resetMaskButton.setMaximumSize(QtCore.QSize(49, 16777215))
        self.resetMaskButton.setObjectName(_fromUtf8("resetMaskButton"))
        self.gridLayout_13.addWidget(self.resetMaskButton, 0, 2, 1, 1)
        self.gridLayout_11.addLayout(self.gridLayout_13, 2, 0, 1, 2)
        self.gridLayout_3.addLayout(self.gridLayout_11, 16, 0, 1, 1)
        self.gridLayout_12 = QtGui.QGridLayout()
        self.gridLayout_12.setSpacing(4)
        self.gridLayout_12.setObjectName(_fromUtf8("gridLayout_12"))
        self.button_classification = QtGui.QPushButton(self.dockWidgetContents)
        self.button_classification.setMaximumSize(QtCore.QSize(200, 16777215))
        self.button_classification.setObjectName(_fromUtf8("button_classification"))
        self.gridLayout_12.addWidget(self.button_classification, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_12, 17, 0, 1, 1)
        DockClass.setWidget(self.dockWidgetContents)
        self.label_17.setBuddy(self.pointerButton_preview)

        self.retranslateUi(DockClass)
        QtCore.QMetaObject.connectSlotsByName(DockClass)

    def retranslateUi(self, DockClass):
        DockClass.setWindowTitle(_translate("DockClass", "SCP: Classification", None))
        self.label_38.setText(_translate("DockClass", " Signature list file", None))
        self.open_signature_list_toolButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Open a signature list file</p></body></html>", None))
        self.open_signature_list_toolButton.setText(_translate("DockClass", "Open", None))
        self.signatureFile_lineEdit.setToolTip(_translate("DockClass", "<html><head/><body><p>Qml file path</p></body></html>", None))
        self.save_signature_list_toolButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Save a signature list</p></body></html>", None))
        self.save_signature_list_toolButton.setText(_translate("DockClass", "Save", None))
        self.label_37.setText(_translate("DockClass", " Signature list", None))
        self.signature_list_tableWidget.setSortingEnabled(True)
        item = self.signature_list_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("DockClass", "S", None))
        item = self.signature_list_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("DockClass", "MC ID", None))
        item = self.signature_list_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("DockClass", "MC Info", None))
        item = self.signature_list_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("DockClass", "C ID", None))
        item = self.signature_list_tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("DockClass", "C Info", None))
        item = self.signature_list_tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("DockClass", "Color", None))
        self.export_CSV_library_toolButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Export selected signatures to CSV spectral library</p></body></html>", None))
        self.export_CSV_library_toolButton.setText(_translate("DockClass", "Export to CSV", None))
        self.delete_Signature_Button.setToolTip(_translate("DockClass", "<html><head/><body><p>Delete highlighted signatures</p></body></html>", None))
        self.delete_Signature_Button.setText(_translate("DockClass", "...", None))
        self.import_library_toolButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Import a spectral library</p></body></html>", None))
        self.import_library_toolButton.setText(_translate("DockClass", "Import library", None))
        self.import_toolButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Import and add a signature list file</p></body></html>", None))
        self.import_toolButton.setText(_translate("DockClass", "Import list", None))
        self.export_signature_list_toolButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Export the signature list to file</p></body></html>", None))
        self.export_signature_list_toolButton.setText(_translate("DockClass", "Export list", None))
        self.signature_spectral_plot_toolButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Add highlighted signatures to spectral signature plot</p></body></html>", None))
        self.signature_spectral_plot_toolButton.setText(_translate("DockClass", "Plot", None))
        self.import_usgs_library_toolButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Import a USGS Spectral Library (requires internet connection)</p></body></html>", None))
        self.import_usgs_library_toolButton.setText(_translate("DockClass", "Import library", None))
        self.label_26.setText(_translate("DockClass", " Classification algorithm", None))
        self.algorithm_combo.setToolTip(_translate("DockClass", "<html><head/><body><p>Select a classification algorithm</p></body></html>", None))
        self.algorithm_combo.setItemText(0, _translate("DockClass", "Minimum Distance", None))
        self.algorithm_combo.setItemText(1, _translate("DockClass", "Maximum Likelihood", None))
        self.algorithm_combo.setItemText(2, _translate("DockClass", "Spectral Angle Mapping", None))
        self.label_14.setText(_translate("DockClass", "Select classification algorithm", None))
        self.alg_threshold_SpinBox.setToolTip(_translate("DockClass", "<html><head/><body><p>Set a classification threshold</p></body></html>", None))
        self.label_16.setText(_translate("DockClass", "Threshold", None))
        self.macroclass_checkBox.setToolTip(_translate("DockClass", "<html><head/><body><p>Use the ID of macroclasses for the classification</p></body></html>", None))
        self.macroclass_checkBox.setText(_translate("DockClass", "Use Macroclass ID", None))
        self.label_28.setText(_translate("DockClass", " Classification preview", None))
        self.preview_size_spinBox.setToolTip(_translate("DockClass", "<html><head/><body><p>Set the preview size (in pixel unit)</p></body></html>", None))
        self.redo_Preview_Button.setToolTip(_translate("DockClass", "<html><head/><body><p>Redo the classification preview at the same point</p></body></html>", None))
        self.redo_Preview_Button.setText(_translate("DockClass", "Redo ↺", None))
        self.label_17.setText(_translate("DockClass", "Size", None))
        self.pointerButton_preview.setToolTip(_translate("DockClass", "<html><head/><body><p><span style=\" font-size:10pt;\">Activate Preview pointer</span></p></body></html>", None))
        self.pointerButton_preview.setText(_translate("DockClass", "+", None))
        self.label_15.setText(_translate("DockClass", " Classification style", None))
        self.qml_lineEdit.setToolTip(_translate("DockClass", "<html><head/><body><p>Qml file path</p></body></html>", None))
        self.qml_Button.setToolTip(_translate("DockClass", "<html><head/><body><p>Select a qml file</p></body></html>", None))
        self.qml_Button.setText(_translate("DockClass", "Select qml", None))
        self.resetQmlButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Reset qml style to default</p></body></html>", None))
        self.resetQmlButton.setText(_translate("DockClass", "Reset", None))
        self.label_32.setText(_translate("DockClass", " Classification output", None))
        self.report_checkBox.setText(_translate("DockClass", "Classification report", None))
        self.vector_output_checkBox.setToolTip(_translate("DockClass", "<html><head/><body><p>Create a classification shapefile</p></body></html>", None))
        self.vector_output_checkBox.setText(_translate("DockClass", "Create vector", None))
        self.mask_checkBox.setToolTip(_translate("DockClass", "<html><head/><body><p>Select an optional mask shapefile</p></body></html>", None))
        self.mask_checkBox.setText(_translate("DockClass", "Apply mask", None))
        self.mask_lineEdit.setToolTip(_translate("DockClass", "<html><head/><body><p>Path of the optional mask shapefile</p></body></html>", None))
        self.resetMaskButton.setToolTip(_translate("DockClass", "<html><head/><body><p>Reset mask path</p></body></html>", None))
        self.resetMaskButton.setText(_translate("DockClass", "Reset", None))
        self.button_classification.setToolTip(_translate("DockClass", "<html><head/><body><p>Perform the classification and save it as .tif file</p></body></html>", None))
        self.button_classification.setText(_translate("DockClass", "Perform classification", None))

import resources_rc
