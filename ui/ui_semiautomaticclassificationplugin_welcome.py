# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_semiautomaticclassificationplugin_welcome.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SCP_Welcome(object):
    def setupUi(self, SCP_Welcome):
        SCP_Welcome.setObjectName("SCP_Welcome")
        SCP_Welcome.resize(609, 355)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/semiautomaticclassificationplugin/semiautomaticclassificationplugin.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SCP_Welcome.setWindowIcon(icon)
        self.gridLayout_2 = QtWidgets.QGridLayout(SCP_Welcome)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.textBrowser = QtWidgets.QTextBrowser(SCP_Welcome)
        self.textBrowser.setFrameShape(QtWidgets.QFrame.Panel)
        self.textBrowser.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(SCP_Welcome)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(SCP_Welcome)
        self.buttonBox.accepted.connect(SCP_Welcome.accept)
        self.buttonBox.rejected.connect(SCP_Welcome.reject)
        QtCore.QMetaObject.connectSlotsByName(SCP_Welcome)

    def retranslateUi(self, SCP_Welcome):
        _translate = QtCore.QCoreApplication.translate
        SCP_Welcome.setWindowTitle(_translate("SCP_Welcome", "Welcome to Semi-Automatic Classification Plugin"))
        self.textBrowser.setHtml(_translate("SCP_Welcome", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Droid Sans\'; font-size:11pt;\">First time using the </span><span style=\" font-family:\'Droid Sans\'; font-size:11pt; font-weight:600;\">Semi-Automatic Classification Plugin</span><span style=\" font-family:\'Droid Sans\'; font-size:11pt;\"> (SCP)?</span></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Droid Sans\'; font-size:11pt;\">Please check the </span><a href=\"https://fromgistors.blogspot.com/p/user-manual.html.\"><span style=\" font-size:11pt; text-decoration: underline; color:#0000ff;\">user manual</span></a><span style=\" font-family:\'Droid Sans\'; font-size:11pt;\"> with tutorials available in several languages.</span></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Droid Sans\'; font-size:11pt;\">You can also contribute to SCP.</span></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Droid Sans\'; font-size:11pt;\">Don\'t forget to join the </span><a href=\"https://www.facebook.com/groups/SemiAutomaticClassificationPlugin\"><span style=\" font-size:11pt; text-decoration: underline; color:#0000ff;\">SCP group in Facebook</span></a><span style=\" font-size:11pt;\"> or </span><a href=\"https://plus.google.com/communities/107833394986612468374\"><span style=\" font-size:11pt; text-decoration: underline; color:#0000ff;\">SCP community in Google+</span></a><span style=\" font-size:11pt;\"> .</span></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Droid Sans\'; font-size:11pt;\">Thank you!</span></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/plugins/semiautomaticclassificationplugin/icons/fromGIStoRS.png\" /><a href=\"https://fromgistors.blogspot.com/p/semi-automatic-classification-plugin.html?spref=scp\"><span style=\" font-family:\'Droid Sans\'; font-size:14pt; text-decoration: underline; color:#0000ff;\">From GIS to Remote Sensing</span></a></p></body></html>"))

from . import resources_rc
