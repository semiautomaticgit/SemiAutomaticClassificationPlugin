# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
 providing a tool for the region growing of image pixels, creating polygon shapefiles intended for
 the collection of training areas (ROIs), and rapidly performing the classification process (or a preview).
							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012 by Luca Congedo
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

import inspect
from matplotlib.ticker import MaxNLocator
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class SpectralSignaturePlot:

	def __init__(self):
		pass
	
	def fitPlotToAxes(self):
		cfg.uisp.Sig_Widget.sigCanvas.ax.relim()
		cfg.uisp.Sig_Widget.sigCanvas.ax.autoscale(True)
		cfg.uisp.Sig_Widget.sigCanvas.ax.autoscale_view(True)
		# Draw the plot
		cfg.uisp.Sig_Widget.sigCanvas.draw()
			
# Create signature list for plot
	def signatureListPlotTable(self, table):
		# checklist
		l = table
		l.setSortingEnabled(False)
		cfg.utls.clearTable(l)
		# add signature items
		x = 0
		for k in cfg.signPlotIDs.values():
			cfg.SigTabEdited = "No"
			l.insertRow(x)
			l.setRowHeight(x, 20)
			cb = QTableWidgetItem("checkbox")
			cb.setCheckState(cfg.spectrPlotList["CHECKBOX_" + str(k)])
			l.setItem(x, 0, cb)
			itMID = QTableWidgetItem()
			itMID.setData(Qt.DisplayRole, int(cfg.spectrPlotList["MACROCLASSID_" + str(k)]))
			l.setItem(x, 1, itMID)
			l.setItem(x, 2, QTableWidgetItem(str(cfg.spectrPlotList["MACROCLASSINFO_" + str(k)])))
			itID = QTableWidgetItem()
			itID.setData(Qt.DisplayRole, int(cfg.spectrPlotList["CLASSID_" + str(k)]))
			l.setItem(x, 3, itID)
			l.setItem(x, 4, QTableWidgetItem(str(cfg.spectrPlotList["CLASSINFO_" + str(k)])))
			l.setItem(x, 5, QTableWidgetItem(""))
			c = cfg.spectrPlotList["COLOR_" + str(k)]
			l.item(x, 5).setBackground(c)
			l.setItem(x, 6, QTableWidgetItem(str(cfg.signPlotIDs["ID_" + str(k)])))
			x = x + 1
		l.show()
		l.setColumnWidth(0, 30)
		l.setColumnWidth(1, 40)
		l.setColumnWidth(3, 40)
		l.setColumnWidth(5, 30)
		l.setSortingEnabled(True)
		cfg.SigTabEdited = "Yes"
		# Create plot		
		self.signaturePlot()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " list created")
		
	def signaturePlotID(self):
		i = 1
		if len(cfg.signPlotIDs.values()) > 0:
			while i in cfg.signPlotIDs.values():
				i = i + 1
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID" + str(i))
		return i
		
	def sigmaCheckbox(self):
		if cfg.uisp.sigma_checkBox.isChecked() is True:
			cfg.sigmaCheck = "Yes"
		else:
			cfg.sigmaCheck = "No"
		# Create plot		
		self.signaturePlot()
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.sigmaCheck))
		
	# remove signature from list
	def removeSignature(self):
		# ask for confirm
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Delete signatures"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to delete highlighted signatures?"))
		if a == "Yes":
			tW = cfg.uisp.signature_list_plot_tableWidget
			r = []
			for i in tW.selectedIndexes():
				r.append(i.row())
			v = list(set(r))
			for x in v:
				id = tW.item(x, 6).text()
				cfg.signPlotIDs.pop("ID_" + str(id))
				cfg.spectrPlotList.pop("MACROCLASSID_" + str(id))
				cfg.spectrPlotList.pop("MACROCLASSINFO_" + str(id))
				cfg.spectrPlotList.pop("CLASSID_" + str(id))
				cfg.spectrPlotList.pop("CLASSINFO_" + str(id))
				cfg.spectrPlotList.pop("WAVELENGTH_" + str(id))
				cfg.spectrPlotList.pop("VALUES_" + str(id))
				cfg.spectrPlotList.pop("COLOR_" + str(id))
				cfg.spectrPlotList.pop("UNIT_" + str(id))
			self.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " removed signatures: " + str(v))
		
	# edited cell
	def editedCell(self, row, column):
		if cfg.SigTabEdited == "Yes":
			tW = cfg.uisp.signature_list_plot_tableWidget
			id = tW.item(row, 6).text()
			if column == 0:
				cfg.spectrPlotList["CHECKBOX_" + str(id)] = tW.item(row, 0).checkState()
			else:
				cfg.spectrPlotList["MACROCLASSID_" + str(id)] = tW.item(row, 1).text()
				cfg.spectrPlotList["MACROCLASSINFO_" + str(id)] = tW.item(row, 2).text()
				cfg.spectrPlotList["CLASSID_" + str(id)] = tW.item(row, 3).text()
				cfg.spectrPlotList["CLASSINFO_" + str(id)] = tW.item(row, 4).text()
			# Create plot		
			self.signaturePlot()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "edited cell" + str(row) + ";" + str(column))
			
	# Create signature plot
	def signaturePlot(self):
		# Clear plot
		try:
			for i in cfg.pF:
				i.remove()
			cfg.pF = []
		except:
			pass
		lines = len(cfg.uisp.Sig_Widget.sigCanvas.ax.lines)
		if lines > 0:
			for i in reversed(range(0, lines)):
				cfg.uisp.Sig_Widget.sigCanvas.ax.lines.pop(i)
		cfg.uisp.Sig_Widget.sigCanvas.ax.grid('on')
		cfg.uisp.Sig_Widget.sigCanvas.draw()
		# Set labels
		cfg.uisp.Sig_Widget.sigCanvas.ax.set_xlabel(QApplication.translate("semiautomaticclassificationplugin", "Wavelength [" + unicode(cfg.ui.unit_combo.currentText()) + "]"))
		cfg.uisp.Sig_Widget.sigCanvas.ax.set_ylabel(QApplication.translate("semiautomaticclassificationplugin", "Values"))
		# Add plots and legend
		pL = []
		pLN = []
		mVal = []
		try:
			for b in cfg.signPlotIDs.values():
				if cfg.spectrPlotList["CHECKBOX_" + str(b)] == 2:
					c = cfg.spectrPlotList["COLOR_" + str(b)].toRgb().name()
					# name
					nm = str(cfg.spectrPlotList["MACROCLASSID_" + str(b)]) + "#" + str(cfg.spectrPlotList["MACROCLASSINFO_" + str(b)]) + " " + str(cfg.spectrPlotList["CLASSID_" + str(b)]) + "#" + str(cfg.spectrPlotList["CLASSINFO_" + str(b)])
					# wavelength
					w = cfg.spectrPlotList["WAVELENGTH_" + str(b)]
					wlg = eval(str(w))
					# values
					v = cfg.spectrPlotList["VALUES_" + str(b)]
					val = eval(str(v))
					mVal.extend(val)
					# counter
					n = 0
					m = []
					# mean plus standard deviation
					mPS = []
					# mean minus standard deviation
					mMS = []
					for i in wlg:
						m.append(val[n * 2])
						mPS.append(val[n * 2] + val[n * 2 +1])
						mMS.append(val[n * 2] - val[n * 2 +1])
						n = n + 1
					# plot
					p, = cfg.uisp.Sig_Widget.sigCanvas.ax.plot(wlg , m, c)
					if cfg.sigmaCheck == "Yes":
						# fill plot
						cfg.pF.append(cfg.uisp.Sig_Widget.sigCanvas.ax.fill_between(wlg, mPS, mMS, color=c, alpha=0.2))
					# add plot to legend
					pL.append(p)
					pLN.append(nm[:cfg.roundCharList])
			# place legend		
			cfg.uisp.Sig_Widget.sigCanvas.ax.legend(pL, pLN, bbox_to_anchor=(0.1, 0.0, 1.1, 1.1), loc=1, borderaxespad=0.).draggable()
			# Grid for X and Y axes
			cfg.uisp.Sig_Widget.sigCanvas.ax.grid('on')
			cfg.uisp.Sig_Widget.sigCanvas.ax.autoscale(False, "both", None)
			cfg.uisp.Sig_Widget.sigCanvas.ax.autoscale_view(False, False,False)
			cfg.uisp.Sig_Widget.sigCanvas.ax.xaxis.set_major_locator(MaxNLocator(11))
			cfg.uisp.Sig_Widget.sigCanvas.ax.yaxis.set_major_locator(MaxNLocator(5))
			# Draw the plot
			cfg.uisp.Sig_Widget.sigCanvas.draw()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " plot created")
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
	def signatureListDoubleClick(self, index):
		if index.column() == 5:
			c = cfg.utls.selectColor()
			if c is not None:
				k = cfg.uisp.signature_list_plot_tableWidget.item(index.row(), 6).text()
				cfg.spectrPlotList["COLOR_" + str(k)] = c
				cfg.uisp.signature_list_plot_tableWidget.item(index.row(), 5).setBackground(c)
		else:
			self.selectAllSignatures()
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures index: " + str(index))
		
	# select all signatures
	def selectAllSignatures(self):
		try:
			cfg.uiUtls.addProgressBar()
			# select all
			if cfg.allSignCheck == "Yes":
				cfg.utls.allItemsSetState(cfg.uisp.signature_list_plot_tableWidget, 2)
				# set check all plot
				cfg.allSignCheck = "No"
			# unselect all if previously selected all
			elif cfg.allSignCheck == "No":
				cfg.utls.allItemsSetState(cfg.uisp.signature_list_plot_tableWidget, 0)
				# set check all plot
				cfg.allSignCheck = "Yes"
			cfg.uiUtls.removeProgressBar()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all signatures")
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.removeProgressBar()
			