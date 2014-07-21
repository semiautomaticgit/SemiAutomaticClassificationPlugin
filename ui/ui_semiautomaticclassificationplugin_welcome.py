# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_semiautomaticclassificationplugin_welcome.ui'
#
# Created: Mon Jul 21 22:15:35 2014
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

class Ui_Welcome(object):
    def setupUi(self, Welcome):
        Welcome.setObjectName(_fromUtf8("Welcome"))
        Welcome.resize(600, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Welcome.sizePolicy().hasHeightForWidth())
        Welcome.setSizePolicy(sizePolicy)
        Welcome.setMinimumSize(QtCore.QSize(600, 300))
        Welcome.setMaximumSize(QtCore.QSize(600, 300))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/semiautomaticclassificationplugin/semiautomaticclassificationplugin.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Welcome.setWindowIcon(icon)
        self.gridLayout_2 = QtGui.QGridLayout(Welcome)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.OK_welcome_buttonBox = QtGui.QDialogButtonBox(Welcome)
        self.OK_welcome_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.OK_welcome_buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.OK_welcome_buttonBox.setObjectName(_fromUtf8("OK_welcome_buttonBox"))
        self.gridLayout.addWidget(self.OK_welcome_buttonBox, 1, 0, 1, 1)
        self.textBrowser = QtGui.QTextBrowser(Welcome)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Welcome)
        QtCore.QObject.connect(self.OK_welcome_buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Welcome.accept)
        QtCore.QObject.connect(self.OK_welcome_buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Welcome.reject)
        QtCore.QMetaObject.connectSlotsByName(Welcome)

    def retranslateUi(self, Welcome):
        Welcome.setWindowTitle(_translate("Welcome", "Welcome", None))
        self.textBrowser.setHtml(_translate("Welcome", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">Welcome to the Semi-Automatic Classification Plugin for QGIS</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Semi-Automatic Classification Plugin allows for the semi-automatic supervised classification of remote sensing images, providing tools to expedite the creation of ROIs, the classification process, the pre processing and the post processing phases (accuracy assessment, land cover change).</p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Please, visit the <a href=\"http://fromgistors.blogspot.com/p/theinterface-2.html\"><span style=\" text-decoration: underline; color:#0057ae;\">user manual page</span></a> for information about the plugin interface.</p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Also, several <a href=\"http://fromgistors.blogspot.com/search/label/Tutorial\"><span style=\" text-decoration: underline; color:#0057ae;\">tutorials</span></a> are available about the use of this plugin.</p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://fromgistors.blogspot.com/\"><span style=\" font-weight:600; text-decoration: underline; color:#0057ae;\">From GIS to Remote Sensing</span></a></p></body></html>", None))

import resources_rc
