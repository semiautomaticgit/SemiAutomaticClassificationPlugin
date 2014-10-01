# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_semiautomaticclassificationplugin_signature_plot.ui'
#
# Created: Wed Oct  1 11:42:02 2014
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

class Ui_SpectralSignaturePlot(object):
    def setupUi(self, SpectralSignaturePlot):
        SpectralSignaturePlot.setObjectName(_fromUtf8("SpectralSignaturePlot"))
        SpectralSignaturePlot.resize(575, 444)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SpectralSignaturePlot.sizePolicy().hasHeightForWidth())
        SpectralSignaturePlot.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/semiautomaticclassificationplugin.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SpectralSignaturePlot.setWindowIcon(icon)
        self.gridLayout_6 = QtGui.QGridLayout(SpectralSignaturePlot)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_25 = QtGui.QLabel(SpectralSignaturePlot)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        font.setBold(True)
        font.setWeight(75)
        self.label_25.setFont(font)
        self.label_25.setStyleSheet(_fromUtf8("background-color : qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #243a4e, stop:1 rgba(0, 0, 0, 0)); color : white"))
        self.label_25.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_25.setFrameShadow(QtGui.QFrame.Sunken)
        self.label_25.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.gridLayout_4.addWidget(self.label_25, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_4, 0, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.signature_list_plot_tableWidget = QtGui.QTableWidget(SpectralSignaturePlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.signature_list_plot_tableWidget.sizePolicy().hasHeightForWidth())
        self.signature_list_plot_tableWidget.setSizePolicy(sizePolicy)
        self.signature_list_plot_tableWidget.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.signature_list_plot_tableWidget.setObjectName(_fromUtf8("signature_list_plot_tableWidget"))
        self.signature_list_plot_tableWidget.setColumnCount(6)
        self.signature_list_plot_tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.signature_list_plot_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_plot_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_plot_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_plot_tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_plot_tableWidget.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.signature_list_plot_tableWidget.setHorizontalHeaderItem(5, item)
        self.signature_list_plot_tableWidget.horizontalHeader().setDefaultSectionSize(50)
        self.signature_list_plot_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.signature_list_plot_tableWidget.verticalHeader().setDefaultSectionSize(20)
        self.gridLayout_2.addWidget(self.signature_list_plot_tableWidget, 0, 0, 1, 1)
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.sigma_checkBox = QtGui.QCheckBox(SpectralSignaturePlot)
        self.sigma_checkBox.setObjectName(_fromUtf8("sigma_checkBox"))
        self.gridLayout_5.addWidget(self.sigma_checkBox, 0, 0, 1, 1)
        self.remove_Signature_Button = QtGui.QPushButton(SpectralSignaturePlot)
        self.remove_Signature_Button.setObjectName(_fromUtf8("remove_Signature_Button"))
        self.gridLayout_5.addWidget(self.remove_Signature_Button, 1, 0, 1, 1)
        self.fitToAxes_pushButton = QtGui.QPushButton(SpectralSignaturePlot)
        self.fitToAxes_pushButton.setObjectName(_fromUtf8("fitToAxes_pushButton"))
        self.gridLayout_5.addWidget(self.fitToAxes_pushButton, 2, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_5, 0, 1, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.Sig_Widget = SigWidget2(SpectralSignaturePlot)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Sig_Widget.sizePolicy().hasHeightForWidth())
        self.Sig_Widget.setSizePolicy(sizePolicy)
        self.Sig_Widget.setObjectName(_fromUtf8("Sig_Widget"))
        self.gridLayout_3.addWidget(self.Sig_Widget, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_3, 2, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.OK_welcome_buttonBox = QtGui.QDialogButtonBox(SpectralSignaturePlot)
        self.OK_welcome_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.OK_welcome_buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.OK_welcome_buttonBox.setObjectName(_fromUtf8("OK_welcome_buttonBox"))
        self.gridLayout.addWidget(self.OK_welcome_buttonBox, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout, 3, 0, 1, 1)

        self.retranslateUi(SpectralSignaturePlot)
        QtCore.QObject.connect(self.OK_welcome_buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SpectralSignaturePlot.accept)
        QtCore.QObject.connect(self.OK_welcome_buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SpectralSignaturePlot.reject)
        QtCore.QMetaObject.connectSlotsByName(SpectralSignaturePlot)

    def retranslateUi(self, SpectralSignaturePlot):
        SpectralSignaturePlot.setWindowTitle(_translate("SpectralSignaturePlot", "SCP: Spectral Signature Plot", None))
        self.label_25.setText(_translate("SpectralSignaturePlot", " Signature list", None))
        self.signature_list_plot_tableWidget.setSortingEnabled(True)
        item = self.signature_list_plot_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("SpectralSignaturePlot", "S", None))
        item = self.signature_list_plot_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("SpectralSignaturePlot", "MC ID", None))
        item = self.signature_list_plot_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("SpectralSignaturePlot", "MC Info", None))
        item = self.signature_list_plot_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("SpectralSignaturePlot", "C ID", None))
        item = self.signature_list_plot_tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("SpectralSignaturePlot", "C Info", None))
        item = self.signature_list_plot_tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("SpectralSignaturePlot", "Color", None))
        self.sigma_checkBox.setToolTip(_translate("SpectralSignaturePlot", "<html><head/><body><p>Plot standard deviation for each signature</p></body></html>", None))
        self.sigma_checkBox.setText(_translate("SpectralSignaturePlot", "Plot σ", None))
        self.remove_Signature_Button.setToolTip(_translate("SpectralSignaturePlot", "<html><head/><body><p>Remove highlighted signatures from list</p></body></html>", None))
        self.remove_Signature_Button.setText(_translate("SpectralSignaturePlot", "Remove signatures", None))
        self.fitToAxes_pushButton.setToolTip(_translate("SpectralSignaturePlot", "<html><head/><body><p>Automatically fit the plot to data</p></body></html>", None))
        self.fitToAxes_pushButton.setText(_translate("SpectralSignaturePlot", "Fit to data", None))

from sigwidget2 import SigWidget2
import resources_rc
