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
		copyright			: (C) 2012-2015 by Luca Congedo
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
import itertools
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
		self.signaturePlotOrder()
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
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " list created")
		
	def signaturePlotID(self):
		i = 1
		if len(cfg.signPlotIDs.values()) > 0:
			while i in cfg.signPlotIDs.values():
				i = i + 1
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID" + str(i))
		return i
		
	# copy for plot order
	def signaturePlotOrder(self):
		signPlotIDs_copy = {}
		spectrPlotList_copy = {}
		tmpROIID = cfg.tmpROIID
		i = 1
		for k in sorted(cfg.signPlotIDs.values()):
			if cfg.signPlotIDs["ID_{0}".format(k)] == tmpROIID:
				cfg.tmpROIID = i
			signPlotIDs_copy["ID_" + str(i)] = i
			spectrPlotList_copy["MACROCLASSID_" + str(i)]  = cfg.spectrPlotList["MACROCLASSID_" + str(k)]
			spectrPlotList_copy["MACROCLASSINFO_" + str(i)]  = cfg.spectrPlotList["MACROCLASSINFO_" + str(k)]
			spectrPlotList_copy["CLASSID_" + str(i)]  = cfg.spectrPlotList["CLASSID_" + str(k)]
			spectrPlotList_copy["CLASSINFO_" + str(i)]  = cfg.spectrPlotList["CLASSINFO_" + str(k)]
			spectrPlotList_copy["WAVELENGTH_" + str(i)]  = cfg.spectrPlotList["WAVELENGTH_" + str(k)]
			spectrPlotList_copy["VALUES_" + str(i)]  = cfg.spectrPlotList["VALUES_" + str(k)]
			spectrPlotList_copy["COLOR_" + str(i)]  = cfg.spectrPlotList["COLOR_" + str(k)]
			spectrPlotList_copy["UNIT_" + str(i)]  = cfg.spectrPlotList["UNIT_" + str(k)]
			spectrPlotList_copy["CHECKBOX_" + str(i)]  = cfg.spectrPlotList["CHECKBOX_" + str(k)]			
			spectrPlotList_copy["COVMATRIX_" + str(i)]  = cfg.spectrPlotList["COVMATRIX_" + str(k)]			
			i = i + 1
		cfg.signPlotIDs = {}
		cfg.spectrPlotList = {}
		cfg.signPlotIDs = signPlotIDs_copy
		cfg.spectrPlotList = spectrPlotList_copy
		
	def sigmaCheckbox(self):
		if cfg.uisp.sigma_checkBox.isChecked() is True:
			cfg.sigmaCheck = "Yes"
		else:
			cfg.sigmaCheck = "No"
		# Create plot		
		self.signaturePlot()
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.sigmaCheck))
		
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
				self.removeSignatureByID(id)
			try:
				cfg.tmpROIID = cfg.tmpROIID - len(tW.selectedIndexes())
			except:
				pass
			self.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			# logger
			cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " removed signatures: " + str(v))
		
	def removeSignatureByID(self, id):
		cfg.signPlotIDs.pop("ID_" + str(id))
		cfg.spectrPlotList.pop("MACROCLASSID_" + str(id))
		cfg.spectrPlotList.pop("MACROCLASSINFO_" + str(id))
		cfg.spectrPlotList.pop("CLASSID_" + str(id))
		cfg.spectrPlotList.pop("CLASSINFO_" + str(id))
		cfg.spectrPlotList.pop("WAVELENGTH_" + str(id))
		cfg.spectrPlotList.pop("VALUES_" + str(id))
		cfg.spectrPlotList.pop("COLOR_" + str(id))
		cfg.spectrPlotList.pop("UNIT_" + str(id))
		cfg.spectrPlotList.pop("CHECKBOX_" + str(id))
		
	# edited cell
	def editedCell(self, row, column):
		if cfg.SigTabEdited == "Yes":
			tW = cfg.uisp.signature_list_plot_tableWidget
			id = tW.item(row, 6).text()
			if column == 0:
				cfg.spectrPlotList["CHECKBOX_" + str(id)] = tW.item(row, 0).checkState()
			elif column == 5:
				tW.item(row, 5).setText("")
			else:
				cfg.spectrPlotList["MACROCLASSID_" + str(id)] = tW.item(row, 1).text()
				cfg.spectrPlotList["MACROCLASSINFO_" + str(id)] = tW.item(row, 2).text()
				cfg.spectrPlotList["CLASSID_" + str(id)] = tW.item(row, 3).text()
				cfg.spectrPlotList["CLASSINFO_" + str(id)] = tW.item(row, 4).text()
			# Create plot		
			self.signaturePlot()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "edited cell" + str(row) + ";" + str(column))
			
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
		# for distances
		IDList = []
		meanDict = {}
		covDict = {}
		# Add plots and legend
		pL = []
		pLN = []
		mVal = []
		# clear signature values
		cfg.uisp.value_textBrowser.clear()
		#clear distance values
		cfg.uisp.distance_textBrowser.clear()
		try:
			pass
		except:
			pass
		for b in sorted(cfg.signPlotIDs.values()):
			if cfg.spectrPlotList["CHECKBOX_" + str(b)] == 2:
				IDList.append(b)
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
				# unit
				unit = cfg.spectrPlotList["UNIT_" + str(b)]
				# counter
				n = 0
				m = []
				# mean plus standard deviation
				mPS = []
				# mean minus standard deviation
				mMS = []
				sdL = []
				for i in wlg:
					m.append(val[n * 2])
					sd = val[n * 2 +1]
					sdL.append(sd)
					mPS.append(val[n * 2] + sd)
					mMS.append(val[n * 2] - sd)
					n = n + 1
				# plot
				p, = cfg.uisp.Sig_Widget.sigCanvas.ax.plot(wlg , m, c)
				if cfg.sigmaCheck == "Yes":
					# fill plot
					cfg.pF.append(cfg.uisp.Sig_Widget.sigCanvas.ax.fill_between(wlg, mPS, mMS, color=c, alpha=0.2))
				# add plot to legend
				pL.append(p)
				pLN.append(nm[:cfg.roundCharList])
				meanDict["ID_" + str(b)] = m
				covDict["ID_" + str(b)] = cfg.spectrPlotList["COVMATRIX_" + str(b)]
				# signature values
				self.signatureDetails(str(cfg.spectrPlotList["MACROCLASSID_" + str(b)]), str(cfg.spectrPlotList["MACROCLASSINFO_" + str(b)]), str(cfg.spectrPlotList["CLASSID_" + str(b)]), str(cfg.spectrPlotList["CLASSINFO_" + str(b)]), wlg, unit, m, sdL, c)
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
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " plot created")
		if cfg.uisp.distances_checkBox.isChecked() is True:
			# calculate distances
			cmb = list(itertools.combinations(sorted(IDList), 2))
			for cB in cmb:
				sim = cfg.utls.brayCurtisSimilarity(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])])
				JM = cfg.utls.jeffriesMatusitaDistance(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])], covDict["ID_" + str(cB[0])], covDict["ID_" + str(cB[1])], cfg.algBandWeigths)
				#TD = cfg.utls.transformedDivergence(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])], covDict["ID_" + str(cB[0])], covDict["ID_" + str(cB[1])])
				dist = cfg.utls.euclideanDistance(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])], cfg.algBandWeigths)
				angle = cfg.utls.spectralAngle(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])], cfg.algBandWeigths)
				self.signatureDistances(str(cfg.spectrPlotList["MACROCLASSID_" + str(cB[0])]), str(cfg.spectrPlotList["MACROCLASSINFO_" + str(cB[0])]), str(cfg.spectrPlotList["CLASSID_" + str(cB[0])]), str(cfg.spectrPlotList["CLASSINFO_" + str(cB[0])]), cfg.spectrPlotList["COLOR_" + str(cB[0])].toRgb().name(), cfg.spectrPlotList["MACROCLASSID_" + str(cB[1])], str(cfg.spectrPlotList["MACROCLASSINFO_" + str(cB[1])]), str(cfg.spectrPlotList["CLASSID_" + str(cB[1])]), str(cfg.spectrPlotList["CLASSINFO_" + str(cB[1])]), cfg.spectrPlotList["COLOR_" + str(cB[1])].toRgb().name(), JM, angle, dist, sim)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " distances calculated")
		try:
			pass
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
	# signature details
	def signatureDetails(self, macroclassID, macroclassInfo, classID, classInfo, wavelengths, wavelength_unit, values, standardDeviation, color):
		tbl = "<table border=\"1\" style=\"width:100%\"><tr><th bgcolor=" + color + "></th><th colspan=" + str(len(wavelengths)) + ">" + str(cfg.fldMacroID_class) + " = " + str(macroclassID) + " " + str(cfg.fldROIMC_info) + " = " + str(macroclassInfo) + " " + str(cfg.fldID_class) + " = " + str(classID) + " " + str(cfg.fldROI_info) + " = " + str(classInfo) + "</th></tr><tr><th>" + cfg.wavelenNm + " [" + str(wavelength_unit) + "]</th>"
		for w in wavelengths:
			tbl = tbl + "<td>" + str(w) + "</td>"
		tbl = tbl + "</tr><tr><th>" + cfg.valNm + "</th>"
		for v in values:
			tbl = tbl + "<td>" + str(round(v, 5)) + "</td>"
		tbl = tbl + "</tr><tr><th>" + cfg.standDevNm + "</th>"
		for s in standardDeviation:
			tbl = tbl + "<td>" + str(round(s, 5)) + "</td>"
		tbl = tbl + "</tr></table>"
		cfg.uisp.value_textBrowser.append(tbl)
		cfg.uisp.value_textBrowser.append("<br/>")
		
	# signature distances
	def signatureDistances(self, macroclassID1, macroclassInfo1, classID1, classInfo1, color1, macroclassID2, macroclassInfo2, classID2, classInfo2, color2, jeffriesMatusitaDistance, spectralAngle, euclideanDistance, brayCurtisSimilarity, transformedDivergence = "No"):
		highlightColor = "red"
		jMColor = "black"
		if jeffriesMatusitaDistance < 1.5:
			jMColor = highlightColor
		tDColor = "black"
		if transformedDivergence < 1.5:
			tDColor = highlightColor
		sAColor = "black"
		if spectralAngle < 10:
			sAColor = highlightColor
		bCColor = "black"
		if brayCurtisSimilarity > 90:
			bCColor = highlightColor
		tbl = "<table border=\"1\" style=\"width:100%\"><tr><th bgcolor=" + color1 + "></th><th>" + str(cfg.fldMacroID_class) + " = " + str(macroclassID1) + " " + str(cfg.fldROIMC_info) + " = " + str(macroclassInfo1) + " " + str(cfg.fldID_class) + " = " + str(classID1) + " " + str(cfg.fldROI_info) + " = " + str(classInfo1) + "</th></tr><tr><th bgcolor=" + color2 + "></th><th>" + str(cfg.fldMacroID_class) + " = " + str(macroclassID2) + " " + str(cfg.fldROIMC_info) + " = " + str(macroclassInfo2) + " " + str(cfg.fldID_class) + " = " + str(classID2) + " " + str(cfg.fldROI_info) + " = " + str(classInfo2)
		tbl = tbl + "</th></tr><tr><th>" + cfg.jeffriesMatusitaDistNm + "</th><td><font color=" + jMColor + ">" + str(jeffriesMatusitaDistance) + "</font></td></tr>" 
		tbl = tbl + "<tr><th>" + cfg.spectralAngleNm + "</th><td><font color=" + sAColor + ">" + str(spectralAngle) + "</font></td></tr>" 
		tbl = tbl + "<tr><th>" + cfg.euclideanDistNm + "</th><td><font color=" + sAColor + ">" + str(euclideanDistance) + "</font></td></tr>"
		tbl = tbl + "<tr><th>" + cfg.brayCurtisSimNm + "</th><td><font color=" + bCColor + ">" + str(brayCurtisSimilarity) + "</font></td></tr>"
		if transformedDivergence != "No":
			tbl = tbl + "<tr><th>" + cfg.transformedDivergenceNm + "</th><td><font color=" + tDColor + ">" + str(transformedDivergence) + "</font></td></tr>"
		tbl = tbl + "</table>"
		cfg.uisp.distance_textBrowser.append(tbl)
		cfg.uisp.distance_textBrowser.append("<br/>")
	# signature list double click
	def signatureListDoubleClick(self, index):
		if index.column() == 5:
			c = cfg.utls.selectColor()
			if c is not None:
				tW = cfg.uisp.signature_list_plot_tableWidget
				r = []
				for i in tW.selectedIndexes():
					r.append(i.row())
				v = list(set(r))
				for x in v:
					k = cfg.uisp.signature_list_plot_tableWidget.item(x, 6).text()
					cfg.spectrPlotList["COLOR_" + str(k)] = c
					cfg.uisp.signature_list_plot_tableWidget.item(x, 5).setBackground(c)
		elif index.column() == 0:
			self.selectAllSignatures()
		# logger
		cfg.utls.logCondition(str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures index: " + str(index))
		
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
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all signatures")
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.removeProgressBar()
			
	def showSignaturePlotT(self):
		cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
		cfg.spectralplotdlg.close()
		cfg.spectralplotdlg.show()