# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
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

class SpectralSignaturePlot:

	def __init__(self):
		self.mouseScroll = cfg.uisp.Sig_Widget.sigCanvas.mpl_connect('scroll_event', self.scroll_event)
		self.mousePress = cfg.uisp.Sig_Widget.sigCanvas.mpl_connect('button_press_event', self.press_event)
		self.mouseRelease = cfg.uisp.Sig_Widget.sigCanvas.mpl_connect('button_release_event', self.release_event)
		self.mouseLeaveFigure = cfg.uisp.Sig_Widget.sigCanvas.mpl_connect('figure_leave_event', self.leave_event)
		self.mouseMove = cfg.uisp.Sig_Widget.sigCanvas.mpl_connect('motion_notify_event', self.motion_event)
		self.editing = 0
		self.checkLimits = "No"

	def editValueRange(self):
		self.editing = 1
	
	def press_event(self, event):
		if event.inaxes is None:
			self.press = None
			return 0
		self.press = [event.xdata, event.ydata]
				
	def release_event(self, event):
		if event.inaxes is None:
			self.release = None
			return 0
		self.release = [event.xdata, event.ydata]
		if self.editing == 1:
			if event.button == 3:
				self.resize()
			else:
				self.move()
			try:
				dX = (float(self.press[0]) - float(self.release[0]))
				dY = (float(self.press[1]) - float(self.release[1]))
			except:
				return 0
			if dX == 0 and dY == 0:
				tW = cfg.uisp.signature_list_plot_tableWidget
				iR = []
				for i in tW.selectedIndexes():
					iR.append(i.row())
				v = list(set(iR))
				if len(v) == 0:
					count = tW.rowCount()
					v = list(range(0, count))
				# ask for confirm
				if len(v) > 1:
					if self.skipQuestion == 0:
						a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Edit value range"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to edit the value range for several signatures?"))
						if a == "Yes":
							self.editing = 1
							self.skipQuestion = 1
							self.editLCSThresholds(v)
						else:
							self.editing = 0
							return 0
					else:
						self.editLCSThresholds(v)
				else:
					self.editLCSThresholds(v)
		else:
			if event.button == 3:
				self.resize()
			else:
				self.move()
				
	def motion_event(self, event):
		if event.inaxes is not None:
			cfg.uisp.value_label.setText("x=" + str(event.xdata)[:8].ljust(8) + " y=" + str(event.ydata)[:8].ljust(8) )
				
	def leave_event(self, event):
		self.stop_edit()

	def stop_edit(self):
		self.editing = 0
		self.skipQuestion = 0
		
	# edoted LCS thresholds
	def editLCSThresholds(self, rows):
		if self.press is None or self.release is None:
			return 0
		tW = cfg.uisp.signature_list_plot_tableWidget
		vx = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
		for row in rows:
			wlgPressList = []
			id = tW.item(row, vx).text()
			# find wavelength
			w = cfg.spectrPlotList["WAVELENGTH_" + str(id)]
			wlg = eval(str(w))
			wlgA = cfg.np.array(wlg)
			wlgB = wlgA - float(self.press[0])
			wlgIndex = cfg.np.argmin(cfg.np.absolute(wlgB))
			# values
			v = cfg.spectrPlotList["VALUES_" + str(id)]
			val = eval(str(v))
			if float(self.press[1]) >= val[wlgIndex * 2]:
				max = cfg.spectrPlotList["LCS_MAX_" + str(id)]
				lcs_max = eval(str(max))
				if float(self.release[1]) < val[wlgIndex * 2]:
					lcs_max[wlgIndex] = val[wlgIndex * 2]
				else:
					lcs_max[wlgIndex] = float(self.release[1])
				cfg.spectrPlotList["LCS_MAX_" + str(id)] = lcs_max
				cfg.signList["LCS_MAX_" + str(id)] = lcs_max
			else:
				min = cfg.spectrPlotList["LCS_MIN_" + str(id)]
				lcs_min = eval(str(min))
				if float(self.release[1]) > val[wlgIndex * 2]:
					lcs_min[wlgIndex] = val[wlgIndex * 2]
				else:
					lcs_min[wlgIndex] = float(self.release[1])
				cfg.spectrPlotList["LCS_MIN_" + str(id)] = lcs_min
				cfg.signList["LCS_MIN_" + str(id)] = lcs_min
			self.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			cfg.LCSignT.LCSignatureThresholdListTable()
			cfg.utls.selectRowsInTable(tW, rows)

	# scroll
	def scroll_event(self, event):	
		xMin, xMax = cfg.uisp.Sig_Widget.sigCanvas.ax.get_xlim()
		yMin, yMax = cfg.uisp.Sig_Widget.sigCanvas.ax.get_ylim()
		zoomX = (xMax - xMin) * 0.2
		zoomY = (yMax - yMin) * 0.2
		if event.button == 'down':
			xLimMin = xMin - zoomX
			xLimMax = xMax + zoomX
			yLimMin = yMin - zoomY
			yLimMax = yMax + zoomY
		else:
			xLimMin = xMin + zoomX
			xLimMax = xMax  - zoomX
			yLimMin = yMin + zoomY
			yLimMax = yMax - zoomY
		cfg.uisp.Sig_Widget.sigCanvas.ax.set_xlim(xLimMin, xLimMax)
		cfg.uisp.Sig_Widget.sigCanvas.ax.set_ylim(yLimMin, yLimMax)
		cfg.uisp.Sig_Widget.sigCanvas.draw()
			
	# resize plot
	def resize(self):
		try:
			xLimMin = min([float(self.press[0]), float(self.release[0])])
			xLimMax = max([float(self.press[0]), float(self.release[0])])
			yLimMin = min([float(self.press[1]), float(self.release[1])])
			yLimMax = max([float(self.press[1]), float(self.release[1])])
			if ((xLimMax - xLimMin) * (xLimMax - xLimMin)) < 0.0001 or ((yLimMax - yLimMin) * (yLimMax - yLimMin)) < 0.0001:
				return
			cfg.uisp.Sig_Widget.sigCanvas.ax.set_xlim(xLimMin, xLimMax)
			cfg.uisp.Sig_Widget.sigCanvas.ax.set_ylim(yLimMin, yLimMax)
			cfg.uisp.Sig_Widget.sigCanvas.draw()
		except:
			pass
			
	# move plot
	def move(self):
		try:
			dX = (float(self.press[0]) - float(self.release[0]))
			dY = (float(self.press[1]) - float(self.release[1]))
			xMin, xMax = cfg.uisp.Sig_Widget.sigCanvas.ax.get_xlim()
			yMin, yMax = cfg.uisp.Sig_Widget.sigCanvas.ax.get_ylim()
			cfg.uisp.Sig_Widget.sigCanvas.ax.set_xlim(xMin + dX, xMax + dX)
			cfg.uisp.Sig_Widget.sigCanvas.ax.set_ylim(yMin + dY, yMax + dY)
			cfg.uisp.Sig_Widget.sigCanvas.draw()
		except:
			pass
			
	# save plot to file
	def savePlot(self):
		imgOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save plot to file"), "", "JPG file (*.jpg);;PNG file (*.png);;PDF file (*.pdf)", None)
		if len(imgOut) > 0:
			if str(imgOut).endswith(".png"):
				cfg.uisp.Sig_Widget.sigCanvas.figure.savefig(imgOut, format="png", dpi=300)
			elif str(imgOut).endswith(".pdf"):
				cfg.uisp.Sig_Widget.sigCanvas.figure.savefig(imgOut, format="pdf", dpi=300)
			elif str(imgOut).endswith(".jpg"):
				cfg.uisp.Sig_Widget.sigCanvas.figure.savefig(imgOut, format="jpg", dpi=300, quality=90)
			else:
				imgOut = imgOut + ".jpg"
				cfg.uisp.Sig_Widget.sigCanvas.figure.savefig(imgOut, format="jpg", dpi=300, quality=90)
			
	# fit plot to axes
	def fitPlotToAxes(self):
		cfg.uisp.Sig_Widget.sigCanvas.ax.relim()
		cfg.uisp.Sig_Widget.sigCanvas.ax.autoscale(True)
		cfg.uisp.Sig_Widget.sigCanvas.ax.autoscale_view(True)
		try:
			cfg.uisp.Sig_Widget.sigCanvas.ax.set_ylim(self.minVal, self.maxVal)
		except:
			pass
		# Draw the plot
		cfg.uisp.Sig_Widget.sigCanvas.draw()
			
	# Add to signature list
	def addToSignatureList(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Add to Signature list"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to add highlighted signatures to the list?"))
		if a == "Yes":
			tW = cfg.uisp.signature_list_plot_tableWidget
			vx = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
			iR = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			v = list(set(iR))
			if len(v) == 0:
				count = tW.rowCount()
				v = list(range(0, count))
			for x in v:
				id = tW.item(x, vx).text()
				cfg.signIDs["ID_" + str(id)] = id
				cfg.signList["MACROCLASSID_" + str(id)] = cfg.spectrPlotList["MACROCLASSID_" + str(id)]
				cfg.signList["MACROCLASSINFO_" + str(id)] = cfg.spectrPlotList["MACROCLASSINFO_" + str(id)]
				cfg.signList["CLASSID_" + str(id)] = cfg.spectrPlotList["CLASSID_" + str(id)]
				cfg.signList["CLASSINFO_" + str(id)] = cfg.spectrPlotList["CLASSINFO_" + str(id)]
				cfg.signList["VALUES_" + str(id)] = cfg.spectrPlotList["VALUES_" + str(id)]
				cfg.signList["LCS_MIN_" + str(id)] = cfg.spectrPlotList["LCS_MIN_" + str(id)]
				cfg.signList["LCS_MAX_" + str(id)] = cfg.spectrPlotList["LCS_MAX_" + str(id)]
				cfg.signList["MIN_VALUE_" + str(id)] = cfg.spectrPlotList["MIN_VALUE_" + str(id)]
				cfg.signList["MAX_VALUE_" + str(id)] = cfg.spectrPlotList["MAX_VALUE_" + str(id)]
				cfg.signList["WAVELENGTH_" + str(id)] = cfg.spectrPlotList["WAVELENGTH_" + str(id)]
				cfg.signList["MEAN_VALUE_" + str(id)] = cfg.spectrPlotList["MEAN_VALUE_" + str(id)]
				cfg.signList["SD_" + str(id)] = cfg.spectrPlotList["SD_" + str(id)]
				cfg.signList["COLOR_" + str(id)] = cfg.spectrPlotList["COLOR_" + str(id)]
				cfg.signList["CHECKBOX_" + str(id)] = 2
				cfg.signList["UNIT_" + str(id)] = cfg.spectrPlotList["UNIT_" + str(id)] 
				cfg.signList["COVMATRIX_" + str(id)] = cfg.spectrPlotList["COVMATRIX_" + str(id)]
				cfg.signList["ROI_SIZE_" + str(id)] = cfg.spectrPlotList["ROI_SIZE_" + str(id)]
				cfg.signList["MD_THRESHOLD_" + str(id)] = cfg.spectrPlotList["MD_THRESHOLD_" + str(id)]
				cfg.signList["ML_THRESHOLD_" + str(id)] = cfg.spectrPlotList["ML_THRESHOLD_" + str(id)]
				cfg.signList["SAM_THRESHOLD_" + str(id)] = cfg.spectrPlotList["SAM_THRESHOLD_" + str(id)]
			cfg.SCPD.ROIListTable(cfg.shpLay, cfg.uidc.signature_list_tableWidget)
			
	# Create signature list for plot
	def signatureListPlotTable(self, table, skipPlot = "No"):
		# checklist
		l = table
		cfg.SigTabEdited = "No"
		l.setSortingEnabled(False)
		l.blockSignals(True)
		# column width
		try:
			wid0 = l.columnWidth(0)
			wid1 = l.columnWidth(1)
			wid2 = l.columnWidth(2)
			wid3 = l.columnWidth(3)
			wid4 = l.columnWidth(4)
			wid5 = l.columnWidth(5)
		except:
			wid0 = 40
			wid1 = 40
			wid2 = 70
			wid3 = 40
			wid4 = 70
			wid5 = 70
		v = 6
		wid = []
		for i in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
			try:
				if l.columnWidth(v) == 0:
					wid.append(70)
				else:
					wid.append(l.columnWidth(v))
			except:
				wid.append(70)
			v = v +1
			try:
				if l.columnWidth(v) == 0:
					wid.append(70)
				else:
					wid.append(l.columnWidth(v))
			except:
				wid.append(70)
			v = v +1
		cfg.utls.clearTable(l)
		l.setColumnCount(0)
		cfg.utls.insertTableColumn(l, 0, "S", wid0)
		cfg.utls.insertTableColumn(l, 1, cfg.tableMCID, wid1)
		cfg.utls.insertTableColumn(l, 2, cfg.tableMCInfo, wid2)
		cfg.utls.insertTableColumn(l, 3, cfg.tableCID, wid3)
		cfg.utls.insertTableColumn(l, 4, cfg.tableCInfo, wid4)
		cfg.utls.insertTableColumn(l, 5, cfg.tableColor, wid5)
		v = 6
		for i in range(1, cfg.bandSetsList[cfg.bndSetNumber][2] + 1):
			cfg.utls.insertTableColumn(l, v, cfg.tableMin + str(i), wid[v-6])
			v = v +1
			cfg.utls.insertTableColumn(l, v, cfg.tableMax + str(i), wid[v-6])
			v = v +1
		# signature ID column
		cfg.utls.insertTableColumn(l, v, cfg.tableColString, 60, "Yes")
		# add signature items
		x = 0
		try:
			for k in list(cfg.signPlotIDs.values()):
				cfg.utls.insertTableRow(l, x, 20)
				cfg.utls.addTableItem(l, "checkbox", x, 0, "Yes", None, cfg.spectrPlotList["CHECKBOX_" + str(k)])
				cfg.utls.addTableItem(l, int(cfg.spectrPlotList["MACROCLASSID_" + str(k)]), x, 1)
				cfg.utls.addTableItem(l, str(cfg.spectrPlotList["MACROCLASSINFO_" + str(k)]), x, 2)
				cfg.utls.addTableItem(l, int(cfg.spectrPlotList["CLASSID_" + str(k)]), x, 3)
				cfg.utls.addTableItem(l, str(cfg.spectrPlotList["CLASSINFO_" + str(k)]), x, 4)
				c = cfg.spectrPlotList["COLOR_" + str(k)]
				cfg.utls.addTableItem(l, "", x, 5, "Yes", c)
				vb = 6
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					cfg.utls.addTableItem(l, str(cfg.spectrPlotList["LCS_MIN_" + str(k)][b]), x, vb)
					vb = vb + 1
					cfg.utls.addTableItem(l, str(cfg.spectrPlotList["LCS_MAX_" + str(k)][b]), x, vb)
					vb = vb + 1
				cfg.utls.addTableItem(l, str(cfg.signPlotIDs["ID_" + str(k)]), x, v, "No")
				x = x + 1
		except Exception as err:
			cfg.utls.clearTable(l)
			cfg.mx.msgErr57("MC" +str(cfg.signList["MACROCLASSID_" + str(k)]) + ";C" + str(cfg.signList["CLASSID_" + str(k)]) + ";" + str(cfg.signList["CLASSINFO_" + str(k)]) )
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		l.show()
		l.setColumnWidth(0, wid0)
		try:
			vOrd = self.orderColumn
		except:
			vOrd = v
		cfg.utls.sortTableColumn(l, vOrd,l.horizontalHeader().sortIndicatorOrder())
		l.setSortingEnabled(True)
		l.blockSignals(False)
		cfg.SigTabEdited = "Yes"
		self.orderedTable(vOrd)
		intersect = self.checkIntersections()
		self.higlightRowsByID(intersect)
		# Create plot
		if skipPlot == "No":
			self.signaturePlot()
			self.checkLimits = "Yes"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " list created")
		
	# highlight rows by ID
	def higlightRowsByID(self, IDComb):
		tW = cfg.uisp.signature_list_plot_tableWidget
		c = tW.rowCount()
		v = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
		cfg.SigTabEdited = "No"
		tW.blockSignals(True)
		tW.setSortingEnabled(False)
		for b in range(0, c):
			tW.item(b, 5).setText("")
			for x in range(0, 5):
				tW.item(b, x).setBackground(cfg.QtGuiSCP.QColor(255,255,255))
		for ids in IDComb:
			row0 = cfg.spectrPlotList["ROW_" + str(ids[0])]
			row1 = cfg.spectrPlotList["ROW_" + str(ids[1])]
			for x in range(0, 5):
				tW.item(row0, x).setBackground(cfg.QtGuiSCP.QColor(255,203,69))
				tW.item(row1, x).setBackground(cfg.QtGuiSCP.QColor(255,203,69))
			text0 = tW.item(row1, 5).text()
			text1 = tW.item(row0, 5).text()
			mcId0 = str(cfg.spectrPlotList["MACROCLASSID_" + str(ids[0])])
			cId0 = str(cfg.spectrPlotList["CLASSID_" + str(ids[0])])
			mcId1 = str(cfg.spectrPlotList["MACROCLASSID_" + str(ids[1])])
			cId1 = str(cfg.spectrPlotList["CLASSID_" + str(ids[1])])
			text0 = text0 + mcId0 + "-" + cId0 + ";"
			text1 = text1 + mcId1 + "-" + cId1 + ";"
			tW.item(row0, 5).setText(text1)
			tW.item(row1, 5).setText(text0)
		tW.blockSignals(False)
		tW.setSortingEnabled(True)
		cfg.SigTabEdited = "Yes"
		
	# check in thresholds are intersecting
	def checkIntersections(self):
		intersect = []
		cmb = list(cfg.itertoolsSCP.combinations(list(cfg.signPlotIDs.values()), 2))
		for a in cmb:
			id0 = a[0]
			minA = cfg.np.array(cfg.spectrPlotList["LCS_MIN_" + str(id0)])
			maxA = cfg.np.array(cfg.spectrPlotList["LCS_MAX_" + str(id0)])
			id1 = a[1]
			minB = cfg.np.array(cfg.spectrPlotList["LCS_MIN_" + str(id1)])
			maxB= cfg.np.array(cfg.spectrPlotList["LCS_MAX_" + str(id1)])
			if cfg.macroclassCheck == "Yes":
				class0 = cfg.spectrPlotList["MACROCLASSID_" + str(id0)]
				class1 = cfg.spectrPlotList["MACROCLASSID_" + str(id1)]
			else:
				class0 = cfg.spectrPlotList["CLASSID_" + str(id0)]
				class1 = cfg.spectrPlotList["CLASSID_" + str(id1)]
			if class0 != class1:
				test = []
				try:
					for i in range(0, len(cfg.spectrPlotList["LCS_MIN_" + str(id0)])):
						if max(cfg.spectrPlotList["LCS_MIN_" + str(id0)][i], cfg.spectrPlotList["LCS_MIN_" + str(id1)][i]) <= min(cfg.spectrPlotList["LCS_MAX_" + str(id1)][i], cfg.spectrPlotList["LCS_MAX_" + str(id0)][i]):
							test.append(1)
				# in case of deleted signature
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					try:
						self.removeSignatureByID(id0)
						self.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
						cfg.LCSignT.LCSignatureThresholdListTable()
					except:
						pass
					try:
						self.removeSignatureByID(id1)
						self.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
						cfg.LCSignT.LCSignatureThresholdListTable()
					except:
						pass
					cfg.mx.msgWar20()
					return intersect
				sum = cfg.np.array(test).sum()
				if sum == len(cfg.spectrPlotList["LCS_MIN_" + str(id0)]):
					intersect.append(a)
		return intersect
		
	# range checkbox
	def sigmaCheckbox(self):
		if cfg.uisp.sigma_checkBox.isChecked() is True:
			cfg.sigmaCheck = "Yes"
		else:
			cfg.sigmaCheck = "No"
		# Create plot		
		self.signaturePlot()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.sigmaCheck))
		
	# refresh plot
	def refreshPlot(self):
		# Create plot		
		self.signaturePlot()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			
	# remove signature from list
	def removeSignature(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Delete signatures"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to delete highlighted signatures?"))
		if a == "Yes":
			tW = cfg.uisp.signature_list_plot_tableWidget
			vx = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
			r = []
			for i in tW.selectedIndexes():
				r.append(i.row())
			v = list(set(r))
			for x in v:	
				try:
					id = tW.item(x, vx).text()
				except:
					cfg.mx.msgWar26(str(cfg.bndSetNumber))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error bands")
					return "No"				
				self.removeSignatureByID(id)
			self.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " removed signatures: " + str(v))
		
	# remove signature by ID
	def removeSignatureByID(self, id):
		cfg.signPlotIDs.pop("ID_" + str(id))
		cfg.spectrPlotList.pop("MACROCLASSID_" + str(id))
		cfg.spectrPlotList.pop("MACROCLASSINFO_" + str(id))
		cfg.spectrPlotList.pop("CLASSID_" + str(id))
		cfg.spectrPlotList.pop("CLASSINFO_" + str(id))
		cfg.spectrPlotList.pop("WAVELENGTH_" + str(id))
		cfg.spectrPlotList.pop("VALUES_" + str(id))
		cfg.spectrPlotList.pop("MEAN_VALUE_" + str(id))
		cfg.spectrPlotList.pop("SD_" + str(id))
		cfg.spectrPlotList.pop("LCS_MIN_" + str(id))
		cfg.spectrPlotList.pop("LCS_MAX_" + str(id))
		cfg.spectrPlotList.pop("MIN_VALUE_" + str(id))
		cfg.spectrPlotList.pop("MAX_VALUE_" + str(id))
		cfg.spectrPlotList.pop("ROI_SIZE_" + str(id))
		cfg.spectrPlotList.pop("COLOR_" + str(id))
		cfg.spectrPlotList.pop("UNIT_" + str(id))
		cfg.spectrPlotList.pop("CHECKBOX_" + str(id))
		cfg.spectrPlotList.pop("ROW_" + str(id))
		
	# edited cell
	def editedCell(self, row, column):
		if cfg.SigTabEdited == "Yes":
			tW = cfg.uisp.signature_list_plot_tableWidget
			v = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
			try:
				id = tW.item(row, v).text()
			except:
				cfg.mx.msgWar26(str(cfg.bndSetNumber))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error bands")
				return "No"
			try:
				if int(tW.columnCount() - 7)/2 != len(cfg.spectrPlotList["LCS_MIN_" + str(id)]):
					cfg.mx.msgWar26(str(cfg.bndSetNumber))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error bands")
					return "No"
			except:
				cfg.mx.msgWar26(str(cfg.bndSetNumber))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error bands")
				return "No"
			if column == 0:
				cfg.spectrPlotList["CHECKBOX_" + str(id)] = tW.item(row, 0).checkState()
			elif column == 5:
				cfg.utls.setTableItem(tW, row, column, "")
			elif column in [1, 2, 3, 4]:
				cfg.spectrPlotList["MACROCLASSID_" + str(id)] = tW.item(row, 1).text()
				cfg.spectrPlotList["MACROCLASSINFO_" + str(id)] = tW.item(row, 2).text()
				cfg.spectrPlotList["CLASSID_" + str(id)] = tW.item(row, 3).text()
				cfg.spectrPlotList["CLASSINFO_" + str(id)] = tW.item(row, 4).text()
			else:
				t = tW.item(row, column).text()
				try:
					tr = float(t)
					values = cfg.spectrPlotList["VALUES_" + str(id)]
					vb = 6
					for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
						if column == vb:
							if tr >= values[b * 2]:
								val = str(values[b * 2])
								cfg.SigTabEdited = "No"
								tW.blockSignals(True)
								cfg.utls.setTableItem(tW, row, column, val)
								tW.blockSignals(False)
								cfg.SigTabEdited = "Yes"
							break
						vb = vb + 1
						if column == vb:
							if tr <= values[b * 2]:
								val = str(values[b * 2])
								cfg.SigTabEdited = "No"
								tW.blockSignals(True)
								cfg.utls.setTableItem(tW, row, column, val)
								tW.blockSignals(False)
								cfg.SigTabEdited = "Yes"
							break
						vb = vb + 1
				except:
					vb = 6
					for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
						if column == vb:
							val = str(cfg.spectrPlotList["LCS_MIN_" + str(id)][b])
							break
						vb = vb + 1
						if column == vb:
							val = str(cfg.spectrPlotList["LCS_MAX_" + str(id)][b])
							break
						vb = vb + 1
					cfg.SigTabEdited = "No"
					tW.blockSignals(True)
					cfg.utls.setTableItem(tW, row, column, val)
					tW.blockSignals(False)
					cfg.SigTabEdited = "Yes"
					self.readThresholdTable()
					cfg.LCSignT.LCSignatureThresholdListTable()
					cfg.spSigPlot.refreshPlot()
					return 0
				self.readThresholdTable()
				cfg.LCSignT.LCSignatureThresholdListTable()
				#cfg.spSigPlot.refreshPlot()
			# Create plot		
			self.signaturePlot()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "edited cell" + str(row) + ";" + str(column))
			
	# read threshold table
	def readThresholdTable(self):
		tW = cfg.uisp.signature_list_plot_tableWidget
		c = tW.rowCount()
		for b in range(0, c):
			try:
				v = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
				id = tW.item(b, v).text()
				vb = 6
				min = []
				max = []
				for n in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					min.append(float(tW.item(b, vb).text()))
					vb = vb + 1
					max.append(float(tW.item(b, vb).text()))
					vb = vb + 1
				cfg.signList["LCS_MIN_" + str(id)] = min
				cfg.signList["LCS_MAX_" + str(id)] = max	
				cfg.spectrPlotList["LCS_MIN_" + str(id)] = min
				cfg.spectrPlotList["LCS_MAX_" + str(id)] = max
			except:
				pass
		intersect = self.checkIntersections()
		self.higlightRowsByID(intersect)
		
	# Create signature plot
	def signaturePlot(self):
		check = "Yes"
		self.minVal = 10000000000
		self.maxVal = -10000000000
		try:
			if self.firstPlot == "No":
				xMin, xMax = cfg.uisp.Sig_Widget.sigCanvas.ax.get_xlim()
				yMin, yMax = cfg.uisp.Sig_Widget.sigCanvas.ax.get_ylim()
		except:
			self.firstPlot = "No"
		# Clear plot
		try:
			for i in cfg.pF:
				i.remove()
			cfg.pF = []
		except:
			pass
		lines = len(cfg.uisp.Sig_Widget.sigCanvas.ax.lines)
		if lines > 0:
			for i in reversed(list(range(0, lines))):
				cfg.uisp.Sig_Widget.sigCanvas.ax.lines.pop(i)
		cfg.uisp.Sig_Widget.sigCanvas.ax.grid('on')
		cfg.uisp.Sig_Widget.sigCanvas.draw()
		# Set labels
		cfg.uisp.Sig_Widget.sigCanvas.ax.set_xlabel(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Wavelength [" + str(cfg.ui.unit_combo.currentText()) + "]"))
		cfg.uisp.Sig_Widget.sigCanvas.ax.set_ylabel(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Values"))
		# Add plots and legend
		pL = []
		pLN = []
		mVal = []
		wlg = []
		# clear signature values
		cfg.uisp.value_textBrowser.clear()
		for b in sorted(cfg.signPlotIDs.values()):
			if cfg.spectrPlotList["CHECKBOX_" + str(b)] == 2:
				#IDList.append(b)
				c = cfg.spectrPlotList["COLOR_" + str(b)].toRgb().name()
				# name
				nm = str(cfg.spectrPlotList["MACROCLASSID_" + str(b)]) + "#" + str(cfg.spectrPlotList["MACROCLASSINFO_" + str(b)]) + " " + str(cfg.spectrPlotList["CLASSID_" + str(b)]) + "#" + str(cfg.spectrPlotList["CLASSINFO_" + str(b)])
				# wavelength
				w = cfg.spectrPlotList["WAVELENGTH_" + str(b)]
				wlg = eval(str(w))
				# values
				v = cfg.spectrPlotList["VALUES_" + str(b)]
				try:
					val = eval(str(v))
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					try:
						self.removeSignatureByID(b)
						self.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
						cfg.LCSignT.LCSignatureThresholdListTable()
					except:
						pass
					check = "No"
				if check == "Yes":
					mVal.extend(val)
					minA = cfg.spectrPlotList["LCS_MIN_" + str(b)]
					mMS = eval(str(minA))
					maxA = cfg.spectrPlotList["LCS_MAX_" + str(b)]
					mPS = eval(str(maxA))
					vMin = min(mMS)
					vMax = max(mPS)
					if vMin < self.minVal:
						self.minVal = vMin
					if vMax > self.maxVal:
						self.maxVal = vMax
					# unit
					unit = cfg.spectrPlotList["UNIT_" + str(b)]
					m = cfg.spectrPlotList["MEAN_VALUE_" + str(b)]
					sdL = cfg.spectrPlotList["SD_" + str(b)]
					# plot
					p, = cfg.uisp.Sig_Widget.sigCanvas.ax.plot(wlg , m, c)
					if cfg.sigmaCheck == "Yes":
						# fill plot
						cfg.pF.append(cfg.uisp.Sig_Widget.sigCanvas.ax.fill_between(wlg, mPS, mMS, color=c, alpha=0.2))
					# add plot to legend
					pL.append(p)
					pLN.append(nm[:cfg.sigPLRoundCharList])
					# signature values
					self.signatureDetails(str(cfg.spectrPlotList["MACROCLASSID_" + str(b)]), str(cfg.spectrPlotList["MACROCLASSINFO_" + str(b)]), str(cfg.spectrPlotList["CLASSID_" + str(b)]), str(cfg.spectrPlotList["CLASSINFO_" + str(b)]), wlg, unit, m, sdL, c, str(cfg.spectrPlotList["ROI_SIZE_" + str(b)]))
		if cfg.uisp.band_lines_checkBox.isChecked():
			for wl in wlg:
				wlD = cfg.uisp.Sig_Widget.sigCanvas.ax.axvline(wl, color='black', linestyle='dashed')
		# place legend		
		# matplotlib API Changes for 3.1.1
		try:
			cfg.uisp.Sig_Widget.sigCanvas.ax.legend(pL, pLN, bbox_to_anchor=(0.1, 0.0, 1.1, 1.0), loc=1, borderaxespad=0.).set_draggable(True)
		except:
			cfg.uisp.Sig_Widget.sigCanvas.ax.legend(pL, pLN, bbox_to_anchor=(0.1, 0.0, 1.1, 1.0), loc=1, borderaxespad=0.).draggable()
		# Grid for X and Y axes
		if cfg.uisp.grid_checkBox.isChecked():
			cfg.uisp.Sig_Widget.sigCanvas.ax.grid('on')
		else:
			cfg.uisp.Sig_Widget.sigCanvas.ax.grid('off')
		cfg.uisp.Sig_Widget.sigCanvas.ax.set_xticks(wlg)
		cfg.uisp.Sig_Widget.sigCanvas.ax.xaxis.set_major_locator(cfg.MaxNLocatorSCP(7))
		cfg.uisp.Sig_Widget.sigCanvas.ax.yaxis.set_major_locator(cfg.MaxNLocatorSCP(5))
		try:
			cfg.uisp.Sig_Widget.sigCanvas.ax.set_xlim(xMin, xMax)
			cfg.uisp.Sig_Widget.sigCanvas.ax.set_ylim(yMin, yMax)
			if (self.maxVal/max(wlg)) > 100:
				cfg.uisp.Sig_Widget.sigCanvas.ax.set_aspect('auto')
		except:
			pass
		# Draw the plot
		cfg.uisp.Sig_Widget.sigCanvas.draw()
		if self.checkLimits == "No":
			self.fitPlotToAxes()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " plot created")
		
	# calculate spectral distances
	def calculateSpectralDistances(self):
		try:
			IDList = []
			meanDict = {}
			covDict = {}
			for b in sorted(cfg.signPlotIDs.values()):
				if cfg.spectrPlotList["CHECKBOX_" + str(b)] == 2:
					IDList.append(b)
			#clear distance values
			cfg.uisp.distance_textBrowser.clear()
			for b in sorted(cfg.signPlotIDs.values()):
				# wavelength
				w = cfg.spectrPlotList["WAVELENGTH_" + str(b)]
				wlg = eval(str(w))
				# values
				v = cfg.spectrPlotList["VALUES_" + str(b)]
				val = eval(str(v))
				# counter
				n = 0
				m = []
				for i in wlg:
					m.append(val[n * 2])
					n = n + 1
				meanDict["ID_" + str(b)] = m
				covDict["ID_" + str(b)] = cfg.spectrPlotList["COVMATRIX_" + str(b)]
			# calculate distances
			cmb = list(cfg.itertoolsSCP.combinations(sorted(IDList), 2))
			for cB in cmb:
				sim = cfg.utls.brayCurtisSimilarity(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])])
				JM = cfg.utls.jeffriesMatusitaDistance(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])], covDict["ID_" + str(cB[0])], covDict["ID_" + str(cB[1])], cfg.algBandWeigths)
				#TD = cfg.utls.transformedDivergence(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])], covDict["ID_" + str(cB[0])], covDict["ID_" + str(cB[1])])
				dist = cfg.utls.euclideanDistance(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])], cfg.algBandWeigths)
				angle = cfg.utls.spectralAngle(meanDict["ID_" + str(cB[0])], meanDict["ID_" + str(cB[1])], cfg.algBandWeigths)
				self.signatureDistances(str(cfg.spectrPlotList["MACROCLASSID_" + str(cB[0])]), str(cfg.spectrPlotList["MACROCLASSINFO_" + str(cB[0])]), str(cfg.spectrPlotList["CLASSID_" + str(cB[0])]), str(cfg.spectrPlotList["CLASSINFO_" + str(cB[0])]), cfg.spectrPlotList["COLOR_" + str(cB[0])].toRgb().name(), cfg.spectrPlotList["MACROCLASSID_" + str(cB[1])], str(cfg.spectrPlotList["MACROCLASSINFO_" + str(cB[1])]), str(cfg.spectrPlotList["CLASSID_" + str(cB[1])]), str(cfg.spectrPlotList["CLASSINFO_" + str(cB[1])]), cfg.spectrPlotList["COLOR_" + str(cB[1])].toRgb().name(), JM, angle, dist, sim)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " distances calculated")
			cfg.utls.selectSpectralPlotTabSettings(2)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# signature details
	def signatureDetails(self, macroclassID, macroclassInfo, classID, classInfo, wavelengths, wavelength_unit, values, standardDeviation, color, ROISize = 0):
		tbl = "<table border=\"1\" style=\"width:100%\"><tr><th bgcolor=" + color + "></th><th colspan=" + str(len(wavelengths)) + ">" + str(cfg.fldMacroID_class) + " = " + str(macroclassID) + " " + str(cfg.fldROIMC_info) + " = " + str(macroclassInfo) + " " + str(cfg.fldID_class) + " = " + str(classID) + " " + str(cfg.fldROI_info) + " = " + str(classInfo) + " " + str(cfg.ROI_Size_info) + " = " + str(ROISize) + " pixels</th></tr><tr><th>" + cfg.wavelenNm + " [" + str(wavelength_unit) + "]</th>"
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
		try:
			if float(jeffriesMatusitaDistance) < 1.5:
				jMColor = highlightColor
		except:
			pass
		tDColor = "black"
		if transformedDivergence != "No":
			if float(transformedDivergence) < 1.5:
				tDColor = highlightColor
		sAColor = "black"
		if float(spectralAngle) < 10:
			sAColor = highlightColor
		bCColor = "black"
		if float(brayCurtisSimilarity) > 90:
			bCColor = highlightColor
		mDColor = "black"
		if float(euclideanDistance) < 0.1:
			mDColor = highlightColor
		tbl = "<table border=\"1\" style=\"width:100%\"><tr><th bgcolor=" + color1 + "></th><th>" + str(cfg.fldMacroID_class) + " = " + str(macroclassID1) + " " + str(cfg.fldROIMC_info) + " = " + str(macroclassInfo1) + " " + str(cfg.fldID_class) + " = " + str(classID1) + " " + str(cfg.fldROI_info) + " = " + str(classInfo1) + "</th></tr><tr><th bgcolor=" + color2 + "></th><th>" + str(cfg.fldMacroID_class) + " = " + str(macroclassID2) + " " + str(cfg.fldROIMC_info) + " = " + str(macroclassInfo2) + " " + str(cfg.fldID_class) + " = " + str(classID2) + " " + str(cfg.fldROI_info) + " = " + str(classInfo2)
		tbl = tbl + "</th></tr><tr><th>" + cfg.jeffriesMatusitaDistNm + "</th><td><font color=" + jMColor + ">" + str(jeffriesMatusitaDistance) + "</font></td></tr>" 
		tbl = tbl + "<tr><th>" + cfg.spectralAngleNm + "</th><td><font color=" + sAColor + ">" + str(spectralAngle) + "</font></td></tr>" 
		tbl = tbl + "<tr><th>" + cfg.euclideanDistNm + "</th><td><font color=" + mDColor + ">" + str(euclideanDistance) + "</font></td></tr>"
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
				vx = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
				r = []
				for i in tW.selectedIndexes():
					r.append(i.row())
				v = list(set(r))
				for x in v:
					k = cfg.uisp.signature_list_plot_tableWidget.item(x, vx).text()
					cfg.spectrPlotList["COLOR_" + str(k)] = c
					cfg.uisp.signature_list_plot_tableWidget.item(x, 5).setBackground(c)
		elif index.column() == 0:
			for k in list(cfg.signPlotIDs.values()):
				if cfg.allSignCheck2 == "Yes":
					v = 2
				else:
					v = 0
				cfg.spectrPlotList["CHECKBOX_" + str(k)] = v
			self.selectAllSignatures()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures index: " + str(index))
		
	# select all signatures
	def selectAllSignatures(self):
		try:
			cfg.uiUtls.addProgressBar()
			# select all
			if cfg.allSignCheck2 == "Yes":
				cfg.utls.allItemsSetState(cfg.uisp.signature_list_plot_tableWidget, 2)
				# set check all plot
				cfg.allSignCheck2 = "No"
			# unselect all if previously selected all
			elif cfg.allSignCheck2 == "No":
				cfg.utls.allItemsSetState(cfg.uisp.signature_list_plot_tableWidget, 0)
				# set check all plot
				cfg.allSignCheck2 = "Yes"
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all signatures")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.removeProgressBar()
			
	# show signature plot
	def showSignaturePlotT(self):
		cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
		cfg.spectralplotdlg.close()
		cfg.spectralplotdlg.show()
		
	# include Checkbox
	def includeCheckbox(self):
		cfg.uisp.LCS_cut_checkBox_2.blockSignals(True)
		cfg.ui.LCS_include_checkBox.blockSignals(True)
		cfg.ui.LCS_cut_checkBox.blockSignals(True)
		if cfg.uisp.LCS_include_checkBox_2.isChecked():
			cfg.ui.LCS_cut_checkBox.setCheckState(0)
			cfg.ui.LCS_include_checkBox.setCheckState(2)
			cfg.uisp.LCS_cut_checkBox_2.setCheckState(0)
		else:
			cfg.ui.LCS_cut_checkBox.setCheckState(2)
			cfg.ui.LCS_include_checkBox.setCheckState(0)
			cfg.uisp.LCS_cut_checkBox_2.setCheckState(2)
		cfg.ui.LCS_cut_checkBox.blockSignals(False)
		cfg.ui.LCS_include_checkBox.blockSignals(False)
		cfg.uisp.LCS_cut_checkBox_2.blockSignals(False)
			
	# cut Checkbox
	def cutCheckbox(self):
		cfg.uisp.LCS_include_checkBox_2.blockSignals(True)
		cfg.ui.LCS_include_checkBox.blockSignals(True)
		cfg.ui.LCS_cut_checkBox.blockSignals(True)
		if cfg.uisp.LCS_cut_checkBox_2.isChecked():
			cfg.ui.LCS_include_checkBox.setCheckState(0)
			cfg.uisp.LCS_include_checkBox_2.setCheckState(0)
			cfg.ui.LCS_cut_checkBox.setCheckState(2)
		else:
			cfg.ui.LCS_include_checkBox.setCheckState(2)
			cfg.uisp.LCS_include_checkBox_2.setCheckState(2)
			cfg.ui.LCS_cut_checkBox.setCheckState(0)
		cfg.ui.LCS_include_checkBox.blockSignals(False)
		cfg.uisp.LCS_include_checkBox_2.blockSignals(False)
		cfg.ui.LCS_cut_checkBox.blockSignals(False)
	
	# Activate pointer for pixel threshold
	def pointerActive(self):
		# connect to click
		t = cfg.LCSPixel2
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(":/pointer/icons/pointer/LCS_pointer.png")
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: LCS pixel")
		
	# left click ROI pointer for pixel signature
	def pointerLeftClick(self, point):
		tW = cfg.uisp.signature_list_plot_tableWidget
		iR = []
		for i in tW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		point = cfg.utls.checkPointImage(cfg.bandSetsList[cfg.bndSetNumber][8], point)
		if cfg.pntCheck == "Yes":
			sig = cfg.utls.calculatePixelSignature(point, cfg.bandSetsList[cfg.bndSetNumber][8], cfg.bndSetNumber, "Pixel")
			if len(v) == 0:
				count = tW.rowCount()
				v = list(range(0, count))
			if len(v) > 1:
				# ask for confirm
				a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to set thresholds for several signatures?"))
				if a == "Yes":
					pass
				else:
					return "No"
			cfg.uiUtls.addProgressBar()
			self.tableEdited = "No"
			tW.blockSignals(True)
			tW.setSortingEnabled(False)
			progrStep = 0
			cfg.undoIDList = {}
			cfg.undoSpectrPlotList = {}
			for x in reversed(v):
				progrStep = progrStep + 100/(len(v))
				cfg.uiUtls.updateBar(int(progrStep))
				idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
				id = tW.item(x, idCol).text()
				# undo list
				cfg.undoIDList["ID_" + str(id)] = str(id)
				cfg.undoSpectrPlotList["LCS_MIN_" + str(id)] = cfg.spectrPlotList["LCS_MIN_" + str(id)] 
				cfg.undoSpectrPlotList["LCS_MAX_" + str(id)] = cfg.spectrPlotList["LCS_MAX_" + str(id)]
				cfg.uisp.undo_threshold_Button.setEnabled(True)
				# values
				val = cfg.spectrPlotList["VALUES_" + str(id)]
				vb = 6
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					sigVal = sig[b]
					valMax = float(cfg.spectrPlotList["LCS_MAX_" + str(id)][b])
					valMin = float(cfg.spectrPlotList["LCS_MIN_" + str(id)][b])
					if sigVal >= val[b * 2]:
						if cfg.uisp.LCS_include_checkBox_2.isChecked():
							if sigVal >= valMax:
								max = sigVal + 1e-12
							else:
								max = valMax
						else:
							if sigVal >= valMax:
								max = valMax
							else:
								max = sigVal - 1e-12
						min = valMin
					else:
						if cfg.uisp.LCS_include_checkBox_2.isChecked():
							if sigVal <= valMin:
								min = sigVal - 1e-12
							else:
								min = valMin
						else:
							if sigVal <= valMin:
								min = valMin
							else:
								min = sigVal + 1e-12
						max = valMax
					cfg.utls.setTableItem(tW, x, vb, str(min))
					vb = vb + 1
					cfg.utls.setTableItem(tW, x, vb, str(max))
					vb = vb + 1
			tW.blockSignals(False)
			tW.setSortingEnabled(True)
			self.tableEdited = "Yes"
			self.readThresholdTable()
			cfg.LCSignT.LCSignatureThresholdListTable()
			cfg.spSigPlot.refreshPlot()
			cfg.utls.selectRowsInTable(tW, v)
			cfg.uiUtls.removeProgressBar()
			
	# ordered table
	def orderedTable(self, column):
		self.orderColumn = column
		tW = cfg.uisp.signature_list_plot_tableWidget
		count = tW.rowCount()
		v = list(range(0, count))
		vx = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
		for x in v:
			id = tW.item(x, vx).text()
			cfg.spectrPlotList["ROW_" + str(id)] = x
			
	# set minimum and maximum
	def setMinimumMaximum(self):
		tW = cfg.uisp.signature_list_plot_tableWidget
		iR = []
		for i in tW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		if len(v) == 0:
			count = tW.rowCount()
			v = list(range(0, count))
		if len(v) > 1:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to set thresholds for several signatures?"))
			if a == "Yes":
				pass
			else:
				return "No"
		cfg.uiUtls.addProgressBar()
		self.tableEdited = "No"
		tW.setSortingEnabled(False)
		tW.blockSignals(True)
		progrStep = 0
		cfg.undoIDList = {}
		cfg.undoSpectrPlotList = {}
		for x in reversed(v):
			progrStep = progrStep + 100/(len(v))
			cfg.uiUtls.updateBar(int(progrStep))
			idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
			id = tW.item(x, idCol).text()
			# undo list
			cfg.undoIDList["ID_" + str(id)] = str(id)
			cfg.undoSpectrPlotList["LCS_MIN_" + str(id)] = cfg.spectrPlotList["LCS_MIN_" + str(id)] 
			cfg.undoSpectrPlotList["LCS_MAX_" + str(id)] = cfg.spectrPlotList["LCS_MAX_" + str(id)]
			cfg.uisp.undo_threshold_Button.setEnabled(True)
			vb = 6
			for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
				min = float(cfg.spectrPlotList["MIN_VALUE_" + str(id)][b])
				max = float(cfg.spectrPlotList["MAX_VALUE_" + str(id)][b])
				cfg.utls.addTableItem(tW, str(min), x, vb)
				vb = vb + 1
				cfg.utls.addTableItem(tW, str(max), x, vb)
				vb = vb + 1
		tW.blockSignals(False)
		tW.setSortingEnabled(True)
		self.tableEdited = "Yes"
		self.readThresholdTable()
		cfg.LCSignT.LCSignatureThresholdListTable()
		cfg.spSigPlot.refreshPlot()
		cfg.utls.selectRowsInTable(tW, v)
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "set")

	# undo threshold
	def undoThreshold(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Undo thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to undo thresholds?"))
		if a == "Yes":
			pass
		else:
			return "No"
		tW = cfg.uisp.signature_list_plot_tableWidget
		cfg.uiUtls.addProgressBar()
		self.tableEdited = "No"
		tW.blockSignals(True)
		tW.setSortingEnabled(False)
		progrStep = 20
		idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
		c = tW.rowCount()
		for x in range(0, c):
			idT = tW.item(x, idCol).text()
			if idT in list(cfg.undoIDList.values()):
				progrStep = progrStep +80/(len(list(cfg.undoIDList.values())))
				cfg.uiUtls.updateBar(int(progrStep))
				vb = 6
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					cfg.utls.addTableItem(tW, str(cfg.undoSpectrPlotList["LCS_MIN_" + str(idT)][b]), x, vb)
					vb = vb + 1
					cfg.utls.addTableItem(tW, str(cfg.undoSpectrPlotList["LCS_MAX_" + str(idT)][b]), x, vb)
					vb = vb + 1
		tW.blockSignals(False)
		tW.setSortingEnabled(True)
		self.tableEdited = "Yes"
		cfg.uisp.undo_threshold_Button.setEnabled(False)
		cfg.undoIDList = {}
		cfg.undoSpectrPlotList = {}
		self.readThresholdTable()
		cfg.LCSignT.LCSignatureThresholdListTable()
		cfg.spSigPlot.refreshPlot()
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "undo")
		
	# set threshold from ROI
	def ROIThreshold(self):
		if cfg.lstROI is not None:
			tW = cfg.uisp.signature_list_plot_tableWidget
			iR = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			v = list(set(iR))
			if len(v) == 0:
				count = tW.rowCount()
				v = list(range(0, count))
			if len(v) > 1:
				# ask for confirm
				a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to set thresholds for several signatures?"))
				if a == "Yes":
					pass
				else:
					return "No"
			cfg.uiUtls.addProgressBar()
			self.tableEdited = "No"
			tW.blockSignals(True)
			tW.setSortingEnabled(False)
			progrStep = 0
			# calculate ROI
			fID = cfg.utls.getLastFeatureID(cfg.lstROI)
			cfg.utls.calculateSignature(cfg.lstROI, cfg.bandSetsList[cfg.bndSetNumber][8], [fID],  0, cfg.tmpROINm, 0, 0, 0, 20, "MinMax", "MinMax", None)
			progrStep = 20
			cfg.undoIDList = {}
			cfg.undoSpectrPlotList = {}
			for x in reversed(v):
				progrStep = progrStep +80/(len(v))
				cfg.uiUtls.updateBar(int(progrStep))
				idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
				id = tW.item(x, idCol).text()
				# undo list
				cfg.undoIDList["ID_" + str(id)] = str(id)
				cfg.undoSpectrPlotList["LCS_MIN_" + str(id)] = cfg.spectrPlotList["LCS_MIN_" + str(id)] 
				cfg.undoSpectrPlotList["LCS_MAX_" + str(id)] = cfg.spectrPlotList["LCS_MAX_" + str(id)]
				cfg.uisp.undo_threshold_Button.setEnabled(True)
				# values
				val = cfg.spectrPlotList["VALUES_" + str(id)]
				vb = 6
				for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
					stats = cfg.tblOut["BAND_" + str(b + 1)]
					min = stats[0]
					max = stats[1]
					if cfg.uisp.LCS_include_checkBox_2.isChecked():
						if cfg.np.around(float(tW.item(x, vb).text()), 11) > cfg.np.around(min, 11):
							cfg.utls.addTableItem(tW, str(min  - 1e-12), x, vb)
					else:
						if cfg.np.around(float(tW.item(x, vb).text()), 11) < cfg.np.around(min, 11):
							if min >= val[b * 2]:
								if min < cfg.np.around(float(tW.item(x, vb + 1).text()), 11):
									cfg.utls.addTableItem(tW, str(min + 1e-12), x, vb + 1)
							else:
								cfg.utls.addTableItem(tW, str(min + 1e-12), x, vb)
					vb = vb + 1
					if cfg.uisp.LCS_include_checkBox_2.isChecked():
						if cfg.np.around(float(tW.item(x, vb).text()), 11) < cfg.np.around(max, 11):
							cfg.utls.addTableItem(tW, str(max + 1e-12), x, vb)
					else:
						if cfg.np.around(float(tW.item(x, vb).text()), 11) > cfg.np.around(max, 11):
							if max <= val[b * 2]:
								if max > cfg.np.around(float(tW.item(x, vb - 1).text()), 11):
									cfg.utls.addTableItem(tW, str(max - 1e-12), x, vb - 1)
							else:
								cfg.utls.addTableItem(tW, str(max - 1e-12), x, vb)
					vb = vb + 1
			tW.blockSignals(False)
			tW.setSortingEnabled(True)
			self.tableEdited = "Yes"
			self.readThresholdTable()
			cfg.LCSignT.LCSignatureThresholdListTable()
			cfg.spSigPlot.refreshPlot()
			cfg.utls.selectRowsInTable(tW, v)
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "set")

	# set weights based on variance
	def setAllWeightsVariance(self):
		tW = cfg.uisp.signature_list_plot_tableWidget
		iR = []
		for i in tW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		if len(v) == 0:
			count = tW.rowCount()
			v = list(range(0, count))
		if len(v) > 1:
			# ask for confirm
			a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Set thresholds"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to set thresholds for several signatures?"))
			if a == "Yes":
				pass
			else:
				return "No"
		cfg.uiUtls.addProgressBar()
		self.tableEdited = "No"
		tW.blockSignals(True)
		tW.setSortingEnabled(False)
		progrStep = 0
		cfg.undoIDList = {}
		cfg.undoSpectrPlotList = {}
		for x in reversed(v):
			progrStep = progrStep + 100/(len(v))
			cfg.uiUtls.updateBar(int(progrStep))
			cfg.QtWidgetsSCP.qApp.processEvents()
			idCol = cfg.bandSetsList[cfg.bndSetNumber][2] * 2 + 6
			id = tW.item(x, idCol).text()
			# undo list
			cfg.undoIDList["ID_" + str(id)] = str(id)
			cfg.undoSpectrPlotList["LCS_MIN_" + str(id)] = cfg.spectrPlotList["LCS_MIN_" + str(id)] 
			cfg.undoSpectrPlotList["LCS_MAX_" + str(id)] = cfg.spectrPlotList["LCS_MAX_" + str(id)]
			cfg.uisp.undo_threshold_Button.setEnabled(True)
			# values
			val = cfg.spectrPlotList["VALUES_" + str(id)]
			vb = 6
			for b in range(0, cfg.bandSetsList[cfg.bndSetNumber][2]):
				sd = val[b * 2 +1]
				cfg.utls.addTableItem(tW, str(val[b * 2] - (sd * cfg.uisp.multiplicative_threshold_doubleSpinBox_2.value())), x, vb)
				vb = vb + 1
				cfg.utls.addTableItem(tW, str(val[b * 2] + (sd * cfg.uisp.multiplicative_threshold_doubleSpinBox_2.value())), x, vb)
				vb = vb + 1
		tW.blockSignals(False)
		tW.setSortingEnabled(True)
		self.tableEdited = "Yes"
		self.readThresholdTable()
		cfg.LCSignT.LCSignatureThresholdListTable()
		cfg.spSigPlot.refreshPlot()
		cfg.utls.selectRowsInTable(tW, v)
		cfg.uiUtls.removeProgressBar()		
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "set")
			
	# set plot legend max lenght
	def setPlotLegendLenght(self):
		cfg.sigPLRoundCharList = cfg.uisp.plot_text_spinBox.value()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "plot legend max length value changed to: " + str(cfg.sigPLRoundCharList))
			