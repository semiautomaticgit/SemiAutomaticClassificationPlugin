# -*- coding: utf-8 -*-
'''
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright		: (C) 2012-2021 by Luca Congedo
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

'''

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

class Ui_Utils:

	def __init__(self):
		pass
		
### Add a progress bar and a cancel button
	def addProgressBar(self, message = '', action = ' Executing', mainMessage = None):
		# remove if present
		try:
			cfg.progressBar.setValue(0)
		except:
			self.createProgressBar(mainMessage, message, action)
				
	# Create a progress bar and a cancel button
	def createProgressBar(self, mainMessage = None, message = '', action = ' Executing'):
		sizePolicy = cfg.QtWidgetsSCP.QSizePolicy(cfg.QtWidgetsSCP.QSizePolicy.Expanding, cfg.QtWidgetsSCP.QSizePolicy.Preferred)
		cfg.iconLabel = cfg.QtWidgetsSCP.QLabel()
		cfg.iconLabel.setMinimumSize(cfg.QtCoreSCP.QSize(20, 20))
		cfg.iconLabel.setMaximumSize(cfg.QtCoreSCP.QSize(50, 50))
		cfg.iconLabel.setSizePolicy(sizePolicy)
		cfg.iconLabel.setPixmap(cfg.QtGuiSCP.QPixmap(':/plugins/semiautomaticclassificationplugin/icons/semiautomaticclassificationplugin.svg'))
		cfg.msgLabelMain = cfg.QtWidgetsSCP.QLabel()
		sizePolicy = cfg.QtWidgetsSCP.QSizePolicy(cfg.QtWidgetsSCP.QSizePolicy.Expanding, cfg.QtWidgetsSCP.QSizePolicy.Preferred)
		cfg.msgLabelMain.setMinimumSize(cfg.QtCoreSCP.QSize(50, 0))
		cfg.msgLabelMain.setMaximumSize(cfg.QtCoreSCP.QSize(800, 30))
		cfg.msgLabelMain.setSizePolicy(sizePolicy)
		font = cfg.QtGuiSCP.QFont()
		font.setBold(True)
		cfg.msgLabelMain.setFont(font)
		cfg.msgLabelMain.setText(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Semi-Automatic Classification Plugin'))
		spacerItem = cfg.QtWidgetsSCP.QSpacerItem(40, 20, cfg.QtWidgetsSCP.QSizePolicy.Expanding, cfg.QtWidgetsSCP.QSizePolicy.Minimum)
		cfg.msgLabel = cfg.QtWidgetsSCP.QLabel()
		cfg.msgLabel.setMinimumSize(cfg.QtCoreSCP.QSize(50, 0)) 
		cfg.msgLabel.setMaximumSize(cfg.QtCoreSCP.QSize(600, 80)) 
		cfg.msgLabel.setSizePolicy(sizePolicy)
		cfg.msgLabel.setWordWrap(True)
		cfg.progressBar = cfg.QtWidgetsSCP.QProgressBar()
		cfg.progressBar.setMinimum(0)
		cfg.progressBar.setMaximum(100)
		cfg.progressBar.setProperty('value', 0)
		cfg.progressBar.setTextVisible(True)
		cfg.cancelButton = cfg.QtWidgetsSCP.QPushButton()
		cfg.cancelButton.setEnabled(True)
		cfg.cancelButton.setText(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Cancel'))
		cfg.qWidget = cfg.QtWidgetsSCP.QWidget()
		horizontalLayout = cfg.QtWidgetsSCP.QHBoxLayout()
		horizontalLayout2 = cfg.QtWidgetsSCP.QHBoxLayout()
		verticalLayout = cfg.QtWidgetsSCP.QVBoxLayout(cfg.qWidget)
		verticalLayout.addLayout(horizontalLayout)
		verticalLayout.addLayout(horizontalLayout2)
		horizontalLayout.addWidget(cfg.iconLabel)
		horizontalLayout.addWidget(cfg.msgLabelMain)
		horizontalLayout.addItem(spacerItem)
		horizontalLayout2.addWidget(cfg.msgLabel)
		horizontalLayout2.addWidget(cfg.progressBar)
		horizontalLayout2.addWidget(cfg.cancelButton)
		cfg.cancelButton.clicked.connect(self.cancelAction)
		self.widgetBar = cfg.iface.messageBar().createMessage('', '')
		cfg.iface.messageBar().findChildren(cfg.QtWidgetsSCP.QToolButton)[0].setHidden(True)
		self.widgetBar.layout().addWidget(cfg.qWidget)
		self.updateBar(0, message, mainMessage)
		# set action to yes
		cfg.actionCheck = 'Yes'
		self.setInterface(False)
		cfg.iface.messageBar().pushWidget(self.widgetBar, cfg.qgisCoreSCP.Qgis.Info)
		
	# cancel action
	def cancelAction(self):
		cfg.actionCheck = 'No'
		cfg.uiUtls.updateBar(100, ' Canceling ...')
		cfg.QtWidgetsSCP.qApp.processEvents()
		# kill subprocesses
		for p in range(0, len(cfg.subprocDictProc)):
			try:
				cfg.subprocDictProc['proc_'+ str(p)].kill()
			except:
				pass
		# terminate multiprocessing
		try:
			cfg.pool.close()
			cfg.pool.terminate()
		except:
			pass
		self.removeProgressBar()
		self.setInterface(True)
		cfg.cnvs.setRenderFlag(True)
			
	# update bar value
	def updateBar(self, value = None, message = '', mainMessage = None):
		try:
			if len(message) > 0:
				cfg.msgLabel.setText(str(message))
			cfg.progressBar.setValue(value)
		except:
			pass
		try:
			if mainMessage is not None:
				cfg.msgLabelMain.setText(str(mainMessage))
		except:
			pass
			
	# remove progress bar and cancel button
	def removeProgressBar(self):
		try:
			cfg.iface.messageBar().popWidget(self.widgetBar)
		except:
			pass
		cfg.progressBar = None
		cfg.actionCheck = 'No'
		self.setInterface(True)
		cfg.iface.messageBar().findChildren(cfg.QtWidgetsSCP.QToolButton)[0].setHidden(False)
		
	# enable disable the interface to avoid errors
	def setInterface(self, state):
		# classification dock
		cfg.dockclassdlg.setEnabled(state)
		# main interface
		cfg.dlg.setEnabled(state)
		# toolbar
		cfg.toolBar2.setEnabled(state)
		cfg.toolBar3.setEnabled(state)
		