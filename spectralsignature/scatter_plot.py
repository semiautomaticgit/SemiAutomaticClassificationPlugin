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
	
class Scatter_Plot:

	def __init__(self):
		self.mouseScroll = cfg.uiscp.Scatter_Widget_2.sigCanvas.mpl_connect('scroll_event', self.scroll_event)
		self.mousePress = cfg.uiscp.Scatter_Widget_2.sigCanvas.mpl_connect('button_press_event', self.press_event)
		self.mouseRelease = cfg.uiscp.Scatter_Widget_2.sigCanvas.mpl_connect('button_release_event', self.release_event)
		self.mouseLeaveFigure = cfg.uiscp.Scatter_Widget_2.sigCanvas.mpl_connect('figure_leave_event', self.leave_event)
		self.mouseMove = cfg.uiscp.Scatter_Widget_2.sigCanvas.mpl_connect('motion_notify_event', self.motion_event)
		self.editing = 0
		self.xMin = None
		self.xMax = None
		self.yMin = None
		self.yMax = None
		self.lastxMin = None
		self.lastxMax = None
		self.lastyMin = None
		self.lastyMax = None
		self.polX = []
		self.polY = []
		self.polygon = []
		self.polygons = []
		self.polP = []
		self.patches = []
		self.color = "#FFAA00"
				
	# add colormap list to combo
	def addColormapToCombo(self, list):
		for i in list:
			cfg.uiscp.colormap_comboBox.addItem(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " list added")
	
	def motion_event(self, event):
		if event.inaxes is not None:
			cfg.uiscp.value_label_2.setText("x=" + str(event.xdata)[:8].ljust(8) + " y=" + str(event.ydata)[:8].ljust(8) )
	
	def press_event(self, event):
		if event.inaxes is None:
			self.press = None
			return 0
		self.press = [event.xdata, event.ydata]
		
	def selectRange(self):
		self.editing = 1
	
	def release_event(self, event):
		if event.inaxes is None:
			self.release = None
			return 0
		self.release = [event.xdata, event.ydata]
		if self.editing == 1:
			if event.button == 3:
				self.drawPolygon(self.color, float(cfg.ROITrnspVal)/100)
				self.polygons.append([self.polygon, self.color])
				self.polygon = []
				self.polX = []
				self.polY = []
			else:
				self.drawLine(self.color)
		else:
			if event.button == 3:
				self.resize()
			else:
				self.move()
				
	def leave_event(self, event):
		self.stop_edit()

	def stop_edit(self):
		self.editing = 0
		self.skipQuestion = 0
		
	def scroll_event(self, event):	
		xMin, xMax = cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.get_xlim()
		yMin, yMax = cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.get_ylim()
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
		cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_xlim(xLimMin, xLimMax)
		cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_ylim(yLimMin, yLimMax)
		cfg.uiscp.Scatter_Widget_2.sigCanvas.draw()
		self.lastxMin = xLimMin
		self.lastxMax = xLimMax
		self.lastyMin = yLimMin
		self.lastyMax = yLimMax
	
	# edited cell
	def editedCell(self, row, column):
		if cfg.ScatterTabEdited == "Yes":
			tW = cfg.uiscp.scatter_list_plot_tableWidget
			id = tW.item(row, 6).text()
			if column == 0:
				cfg.scatterPlotList["CHECKBOX_" + str(id)] = tW.item(row, 0).checkState()
			cfg.scaPlT.scatterPlot()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "edited cell" + str(row) + ";" + str(column))
			
	def scatterPlotDoubleClick(self, index):
		if index.column() == 5:
			c = cfg.utls.selectColor()
			if c is not None:
				tW = cfg.uiscp.scatter_list_plot_tableWidget
				r = []
				for i in tW.selectedIndexes():
					r.append(i.row())
				v = list(set(r))
				for x in v:
					i = tW.item(x, 6).text()
					tW.item(x, 5).setBackground(c)
					# color
					c = str(tW.item(x, 5).background().color().toRgb().name())
					hue = tW.item(x, 5).background().color().hue()
					saturation = tW.item(x, 5).background().color().saturation()
					value = tW.item(x, 5).background().color().value()
					# lighter color
					cL = cfg.QtGuiSCP.QColor()
					newVal = value + 60
					if newVal > 255:
						newVal = 255
					cL.setHsv(hue, saturation, newVal)
					# darker color
					cD = cfg.QtGuiSCP.QColor()
					newVal = value - 60
					if newVal < 0:
						newVal = 0
					cD.setHsv(hue, saturation, newVal)
					pal = cfg.mplcolorsSCP.LinearSegmentedColormap.from_list('color',[cD.toRgb().name(), c, cL.toRgb().name()])
					pal.set_under('w', 0.0)
					cfg.scatterPlotList["COLORMAP_" + str(i)] = pal
				cfg.scaPlT.scatterPlot()
		elif index.column() == 0:
			self.selectAllROIs()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " signatures index: " + str(index))
		
	# select all signatures
	def selectAllROIs(self):
		try:
			cfg.uiUtls.addProgressBar()
			# select all
			if cfg.allSignCheck3 == "Yes":
				cfg.utls.allItemsSetState(cfg.uiscp.scatter_list_plot_tableWidget, 2)
				# set check all plot
				cfg.allSignCheck3 = "No"
			# unselect all if previously selected all
			elif cfg.allSignCheck3 == "No":
				cfg.utls.allItemsSetState(cfg.uiscp.scatter_list_plot_tableWidget, 0)
				# set check all plot
				cfg.allSignCheck3 = "Yes"
			tW = cfg.uiscp.scatter_list_plot_tableWidget
			r = tW.rowCount()
			for b in range(0, r):
				id = tW.item(b, 6).text()
				cfg.scatterPlotList["CHECKBOX_" + str(id)] = tW.item(b, 0).checkState()
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " all signatures")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.removeProgressBar()
			
	# signature list to plot list
	def sigListToScatterPlot(self, id, histogram, bandList):
		cfg.scatterPlotIDs["ID_" + str(id)] = id
		cfg.scatterPlotList["HISTOGRAM_" + str(id) + "_" + str(bandList)] = histogram
		cfg.scatterPlotList["MACROCLASSID_" + str(id)] = cfg.signList["MACROCLASSID_" + str(id)]
		cfg.scatterPlotList["MACROCLASSINFO_" + str(id)] = cfg.signList["MACROCLASSINFO_" + str(id)]
		cfg.scatterPlotList["CLASSID_" + str(id)] = cfg.signList["CLASSID_" + str(id)]
		cfg.scatterPlotList["CLASSINFO_" + str(id)] = cfg.signList["CLASSINFO_" + str(id)]
		cfg.scatterPlotList["COLOR_" + str(id)] = cfg.signList["COLOR_" + str(id)]
		cfg.scatterPlotList["CHECKBOX_" + str(id)] = 2
		try:
			a = cfg.scatterPlotList["COLORMAP_" + str(id)]
		except:
			cfg.scatterPlotList["COLORMAP_" + str(id)] = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		
	# temp ROI to plot list
	def tempROIToScatterPlot(self, id, histogram, bandList):
		cfg.scatterPlotIDs["ID_" + str(id)] = id
		cfg.scatterPlotList["HISTOGRAM_" + str(id) + "_" + str(bandList)] = histogram
		cfg.scatterPlotList["MACROCLASSID_" + str(id)] = 0
		cfg.scatterPlotList["MACROCLASSINFO_" + str(id)] = cfg. tempScatterNm
		cfg.scatterPlotList["CLASSID_" + str(id)] = 0
		cfg.scatterPlotList["CLASSINFO_" + str(id)] = str(bandList)
		cfg.scatterPlotList["COLOR_" + str(id)] = cfg.QtGuiSCP.QColor(cfg.ROIClrVal)
		cfg.scatterPlotList["CHECKBOX_" + str(id)] = 2
		try:
			a = cfg.scatterPlotList["COLORMAP_" + str(id)]
		except:
			cfg.scatterPlotList["COLORMAP_" + str(id)] = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		
	# add temp ROI to scatter plot
	def addTempROIToScatterPlot(self):
		if cfg.lstROI is not None:
			cfg.uiUtls.addProgressBar()
			bX = cfg.scatterBandX
			bY = cfg.scatterBandY
			cfg.sctrROIID_h["HISTOGRAM_" + str(cfg.sctrROIID) + "_" + str([bX, bY])] = self.calculateTempROIToScatterPlot()
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			
	# add image extent to scatter plot
	def addImageToScatterPlot(self):	
		cfg.uiUtls.addProgressBar()
		rectangle = cfg.cnvs.extent()
		imageName = cfg.bandSetsList[cfg.bndSetNumber][8]
		# band set
		if cfg.bandSetsList[cfg.bndSetNumber][0] == "Yes":
			imageName = cfg.bandSetsList[cfg.bndSetNumber][3][0]
		tLX, tLY, lRX, lRY, pSX, pSY = cfg.utls.imageInformationSize(imageName)
		pol = []
		pol.append(cfg.qgisCoreSCP.QgsPointXY(tLX , tLY))
		pol.append(cfg.qgisCoreSCP.QgsPointXY(lRX , tLY))
		pol.append(cfg.qgisCoreSCP.QgsPointXY(lRX , lRY))
		pol.append(cfg.qgisCoreSCP.QgsPointXY(tLX , lRY))
		self.calculatePolygonScatterPlot(pol)
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		
	# add display extent to scatter plot
	def addDisplayToScatterPlot(self):
		cfg.uiUtls.addProgressBar()
		rectangle = cfg.cnvs.extent()
		imageName = cfg.bandSetsList[cfg.bndSetNumber][8]
		# band set
		if cfg.bandSetsList[cfg.bndSetNumber][0] == "Yes":
			imageName = cfg.bandSetsList[cfg.bndSetNumber][3][0]
		tLX, tLY, lRX, lRY, pSX, pSY = cfg.utls.imageInformationSize(imageName)
		pol = []
		pol.append(cfg.qgisCoreSCP.QgsPointXY(min([rectangle.xMaximum(), tLX]) , min([rectangle.yMaximum(), tLY])))
		pol.append(cfg.qgisCoreSCP.QgsPointXY(max([rectangle.xMinimum(), lRX]) , min([rectangle.yMaximum(), tLY])))
		pol.append(cfg.qgisCoreSCP.QgsPointXY(max([rectangle.xMinimum(), lRX]) , max([rectangle.yMinimum(), lRY])))
		pol.append(cfg.qgisCoreSCP.QgsPointXY(min([rectangle.xMaximum(), tLX]) , max([rectangle.yMinimum(), lRY])))
		self.calculatePolygonScatterPlot(pol)
		cfg.uiUtls.removeProgressBar()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		
	# calculate polygon scatter plot
	def calculatePolygonScatterPlot(self, polygon):
		bX = cfg.scatterBandX
		bY = cfg.scatterBandY
		imageName = cfg.bandSetsList[cfg.bndSetNumber][8]
		# band set
		if cfg.bandSetsList[cfg.bndSetNumber][0] == "Yes":
			imageName = cfg.bandSetsList[cfg.bndSetNumber][3][0]
			# image CRS
			bN0 = cfg.utls.selectLayerbyName(imageName, "Yes")
			pCrs = cfg.utls.getCrs(bN0)
		else:
			# image CRS
			bN0 = cfg.utls.selectLayerbyName(imageName, "Yes")
			pCrs = cfg.utls.getCrs(bN0)
		if pCrs is None:
			pCrs = cfg.utls.getQGISCrs()
		# date time for temp name
		dT = cfg.utls.getTime()
		mL = cfg.qgisCoreSCP.QgsVectorLayer("MultiPolygon?crs=" + str(pCrs.toWkt()), "m"+ str(dT), "memory")
		pointF = cfg.QtCoreSCP.QPointF()
		polF = cfg.QtGuiSCP.QPolygonF()
		for v in polygon:
			pointF.setX(v.x())
			pointF.setY(v.y())
			polF.append(pointF)
		pointF.setX(polygon[0].x())
		pointF.setY(polygon[0].y())
		polF.append(pointF)
		g = cfg.qgisCoreSCP.QgsGeometry().fromQPolygonF(polF)
		f = cfg.qgisCoreSCP.QgsFeature()
		f.setGeometry(g)
		mL.startEditing()
		mL.addFeatures([f])
		mL.commitChanges()
		mL.dataProvider().createSpatialIndex()
		mL.updateExtents()
		cfg.sctrROIID_h["HISTOGRAM_" + str(cfg.sctrROIID) + "_" + str([bX, bY])] = self.calculateTempROIToScatterPlot(mL)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			
	# add temp ROI to scatter plot
	def calculateTempROIToScatterPlot(self, vector = None):
		if vector is None:
			vector = cfg.lstROI
		cfg.sctrROIID = cfg. tempScatterNm
		h = cfg.utls.calculateScatterPlot(vector, "ID", str(cfg.sctrROIID), "Yes")
		# add ROI to scatter plot table
		cfg.scaPlT.tempROIToScatterPlot(cfg.sctrROIID, h, [cfg.scatterBandX, cfg.scatterBandY])
		cfg.scaPlT.scatterPlotListTable(cfg.uiscp.scatter_list_plot_tableWidget)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return h
	
	# calculate scatter plot
	def scatterPlotCalc(self):	
		cfg.uiUtls.addProgressBar()
		tW = cfg.uiscp.scatter_list_plot_tableWidget
		bX = cfg.scatterBandX
		bY = cfg.scatterBandY
		r = tW.rowCount()
		for b in range(0, r):
			if tW.item(b, 0).checkState() == 2:
				i = tW.item(b, 6).text()
				if str(i) in list(cfg.ROI_SCP_UID.values()):
					h = cfg.utls.calculateScatterPlot(cfg.shpLay, cfg.fldSCP_UID, str(i))
					# add ROI to scatter plot table
					cfg.scaPlT.sigListToScatterPlot(i, h, [cfg.scatterBandX, cfg.scatterBandY])
				elif str(i) == cfg.sctrROIID:
					cfg.sctrROIID_h["HISTOGRAM_" + str(i) + "_" + str([bX, bY])] = cfg.scaPlT.calculateTempROIToScatterPlot()
		cfg.uiUtls.removeProgressBar()
		cfg.scaPlT.scatterPlot()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			
	# plot colormap
	def colorPlot(self):
		tW = cfg.uiscp.scatter_list_plot_tableWidget
		iR = []
		for i in tW.selectedIndexes():
			iR.append(i.row())
		v = list(set(iR))
		if len(v) == 0:
			count = tW.rowCount()
			v = list(range(0, count))
		ids = []
		for x in v:
			ids.append(tW.item(x, 6).text())
		cfg.scaPlT.scatterPlot(ids)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		
	# Create scatter plot
	def scatterPlot(self, colorMap = "No"):
		cfg.uiUtls.addProgressBar()
		tW = cfg.uiscp.scatter_list_plot_tableWidget
		# Clear plot
		cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.clear()
		cfg.uiscp.Scatter_Widget_2.sigCanvas.draw()
		bX = cfg.scatterBandX
		bY = cfg.scatterBandY
		# Set labels
		cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_xlabel(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band" + " " +  str(bX)))
		cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_ylabel(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Band" + " " + str(bY)))
		r = tW.rowCount()
		xMins = []
		xMaxs = []
		yMins = []
		yMaxs = []
		for b in range(0, r):
			if tW.item(b, 0).checkState() == 2:
				i = tW.item(b, 6).text()
				if i in colorMap:
					pal = cfg.mplpltSCP.get_cmap(cfg.uiscp.colormap_comboBox.currentText())
					pal.set_under('w', 0.0)
					cfg.scatterPlotList["COLORMAP_" + str(i)] = pal
				else:
					if cfg.scatterPlotList["COLORMAP_" + str(i)] is None:
						# color
						c = str(tW.item(b, 5).background().color().toRgb().name())
						hue = tW.item(b, 5).background().color().hue()
						saturation = tW.item(b, 5).background().color().saturation()
						value = tW.item(b, 5).background().color().value()
						# lighter color
						cL = cfg.QtGuiSCP.QColor()
						newVal = value + 60
						if newVal > 255:
							newVal = 255
						cL.setHsv(hue, saturation, newVal)
						# darker color
						cD = cfg.QtGuiSCP.QColor()
						newVal = value - 60
						if newVal < 0:
							newVal = 0
						cD.setHsv(hue, saturation, newVal)
						pal = cfg.mplcolorsSCP.LinearSegmentedColormap.from_list('color',[cD.toRgb().name(), c, cL.toRgb().name()])
						pal.set_under('w', 0.0)
						cfg.scatterPlotList["COLORMAP_" + str(i)] = pal
					else:
						pal = cfg.scatterPlotList["COLORMAP_" + str(i)]
				try:
					h = cfg.scatterPlotList["HISTOGRAM_" + str(i) + "_" + str([bX, bY])]
					if h != "No":
						p = cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.imshow(h[0].T, origin='low', interpolation='none', extent=[h[1][0], h[1][-1], h[2][0], h[2][-1]], cmap=pal, vmin = 0.001)
					else:
						cfg.uiUtls.removeProgressBar()
						return "No"
				except:
					if str(i) == cfg.sctrROIID:
						try:
							h = cfg.sctrROIID_h["HISTOGRAM_" + str(i) + "_" + str([bX, bY])]
						except:
							cfg.uiUtls.removeProgressBar()
							return "No"
						if h != "No":
							p = cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.imshow(h[0].T, origin='low', interpolation='none', extent=[h[1][0], h[1][-1], h[2][0], h[2][-1]], cmap=pal, vmin = 0.001)
						else:
							cfg.uiUtls.removeProgressBar()
							return "No"
					else:
						cfg.uiUtls.removeProgressBar()
						return "No"
				xMins.append(h[1][0])
				xMaxs.append(h[1][-1])
				yMins.append(h[2][0])
				yMaxs.append(h[2][-1])
		# Grid for X and Y axes
		try:
			cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.xaxis.set_major_locator(cfg.MaxNLocatorSCP(5))
			cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.yaxis.set_major_locator(cfg.MaxNLocatorSCP(5))	
		except:
			pass
		try:
			self.xMin = min(xMins)
			self.xMax = max(xMaxs)
			self.yMin = min(yMins)
			self.yMax = max(yMaxs)
			if self.lastxMin is None or self.lastxMax is None or self.lastyMin is None or self.lastyMax is None:
				self.lastxMin = self.xMin
				self.lastxMax = self.xMax 
				self.lastyMin = self.yMin
				self.lastyMax = self.yMax
		except:
			pass		
		for pol in self.patches:
			self.polP.append(cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.add_patch(pol))
		# Draw the plot
		cfg.scaPlT.fitPlotToAxes("Yes")
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " scatter plot created")
		cfg.uiUtls.removeProgressBar()
		
	# remove scatter plot from list
	def removeScatter(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Delete scatter plot"), cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to delete highlighted scatter plots?"))
		if a == "Yes":
			tW =cfg.uiscp.scatter_list_plot_tableWidget
			r = []
			for i in tW.selectedIndexes():
				r.append(i.row())
			v = list(set(r))
			for x in v:
				id = tW.item(x, 6).text()
				self.removeScatterByID(id)
			cfg.scaPlT.scatterPlotListTable(cfg.uiscp.scatter_list_plot_tableWidget, "Yes")
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " removed plots: " + str(v))
		
	# remove scatter plot by ID
	def removeScatterByID(self, id):
		cfg.scatterPlotIDs.pop("ID_" + str(id))
		cfg.scatterPlotList.pop("MACROCLASSID_" + str(id))
		cfg.scatterPlotList.pop("MACROCLASSINFO_" + str(id))
		cfg.scatterPlotList.pop("CLASSID_" + str(id))
		cfg.scatterPlotList.pop("CLASSINFO_" + str(id))
		cfg.scatterPlotList.pop("CHECKBOX_" + str(id))
		cfg.scatterPlotList.pop("COLOR_" + str(id))
		cfg.scatterPlotList.pop("COLORMAP_" + str(id))
		cfg.scatterPlotList.pop("ROW_" + str(id))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			
	# Create signature list for plot
	def scatterPlotListTable(self, table, skipPlot = "No"):
		# checklist
		l = table
		cfg.ScatterTabEdited = "No"
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
		cfg.utls.clearTable(l)
		l.setColumnCount(0)
		cfg.utls.insertTableColumn(l, 0, "S", wid0)
		cfg.utls.insertTableColumn(l, 1, cfg.tableMCID, wid1)
		cfg.utls.insertTableColumn(l, 2, cfg.tableMCInfo, wid2)
		cfg.utls.insertTableColumn(l, 3, cfg.tableCID, wid3)
		cfg.utls.insertTableColumn(l, 4, cfg.tableCInfo, wid4)
		cfg.utls.insertTableColumn(l, 5, cfg.tableColor2, wid5)
		# signature ID column
		cfg.utls.insertTableColumn(l, 6, cfg.tableColString, 60, "Yes")
		# add signature items
		x = 0
		for k in list(cfg.scatterPlotIDs.values()):
			cfg.utls.insertTableRow(l, x, 20)
			cfg.utls.addTableItem(l, "checkbox", x, 0, "Yes", None, cfg.scatterPlotList["CHECKBOX_" + str(k)])
			cfg.utls.addTableItem(l, int(cfg.scatterPlotList["MACROCLASSID_" + str(k)]), x, 1)
			cfg.utls.addTableItem(l, str(cfg.scatterPlotList["MACROCLASSINFO_" + str(k)]), x, 2)
			cfg.utls.addTableItem(l, int(cfg.scatterPlotList["CLASSID_" + str(k)]), x, 3)
			cfg.utls.addTableItem(l, str(cfg.scatterPlotList["CLASSINFO_" + str(k)]), x, 4)
			c = cfg.scatterPlotList["COLOR_" + str(k)]
			cfg.utls.addTableItem(l, "", x, 5, "Yes", c)
			cfg.utls.addTableItem(l, str(cfg.scatterPlotIDs["ID_" + str(k)]), x, 6, "No")
			x = x + 1
		l.show()
		l.setColumnWidth(0, wid0)
		try:
			vOrd = self.orderColumn
		except:
			vOrd = 6
		cfg.utls.sortTableColumn(l, vOrd,l.horizontalHeader().sortIndicatorOrder())
		l.setSortingEnabled(True)
		l.blockSignals(False)
		cfg.ScatterTabEdited = "Yes"
		self.orderedTable(vOrd)
		# Create plot
		if skipPlot == "No":
			self.scatterPlot()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " list created")
		
	# ordered table
	def orderedTable(self, column):
		self.orderColumn = column
		tW = cfg.uiscp.scatter_list_plot_tableWidget
		count = tW.rowCount()
		v = list(range(0, count))
		for x in v:
			id = tW.item(x, 6).text()
			cfg.scatterPlotList["ROW_" + str(id)] = x
		
	# set band X
	def bandXPlot(self):
		self.removePolygons()
		# band set
		if cfg.bandSetsList[cfg.bndSetNumber][0] == "Yes":
			b = len(cfg.bandSetsList[cfg.bndSetNumber][3])
		else:
			i = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8], "Yes")
			try:
				b = i.bandCount()
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				b = 1
		if cfg.uiscp.bandX_spinBox.value() > b:
			cfg.uiscp.bandX_spinBox.setValue(b)
		cfg.scatterBandX = cfg.uiscp.bandX_spinBox.value()
		cfg.scaPlT.scatterPlot()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "scatter band X: " + str(cfg.scatterBandX))
		
	# set band Y
	def bandYPlot(self):
		self.removePolygons()
		# band set
		if cfg.bandSetsList[cfg.bndSetNumber][0] == "Yes":
			b = len(cfg.bandSetsList[cfg.bndSetNumber][3])
		else:
			i = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8], "Yes")
			try:
				b = i.bandCount()
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				b = 1
		if cfg.uiscp.bandY_spinBox.value() > b:
			cfg.uiscp.bandY_spinBox.setValue(b)
		cfg.scatterBandY = cfg.uiscp.bandY_spinBox.value()
		cfg.scaPlT.scatterPlot()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "scatter band X: " + str(cfg.scatterBandY))
		
	# resize plot
	def resize(self):
		try:
			xLimMin = min([float(self.press[0]), float(self.release[0])])
			xLimMax = max([float(self.press[0]), float(self.release[0])])
			yLimMin = min([float(self.press[1]), float(self.release[1])])
			yLimMax = max([float(self.press[1]), float(self.release[1])])
			if ((xLimMax - xLimMin) * (xLimMax - xLimMin)) < 0.000001 or ((yLimMax - yLimMin) * (yLimMax - yLimMin)) < 0.000001:
				return
			cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_xlim(xLimMin, xLimMax)
			cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_ylim(yLimMin, yLimMax)
			cfg.uiscp.Scatter_Widget_2.sigCanvas.draw()
			self.lastxMin = xLimMin
			self.lastxMax = xLimMax
			self.lastyMin = yLimMin
			self.lastyMax = yLimMax
		except:
			pass
			
	# move plot
	def move(self):
		try:
			dX = (float(self.press[0]) - float(self.release[0]))
			dY = (float(self.press[1]) - float(self.release[1]))
			xMin, xMax = cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.get_xlim()
			yMin, yMax = cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.get_ylim()
			cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_xlim(xMin + dX, xMax + dX)
			cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_ylim(yMin + dY, yMax + dY)
			cfg.uiscp.Scatter_Widget_2.sigCanvas.draw()
			self.lastxMin = xMin + dX
			self.lastxMax = xMax + dX
			self.lastyMin = yMin + dY
			self.lastyMax = yMax + dY
		except:
			pass
			
	# draw line
	def drawLine(self, colorLine):
		if self.press is not None:
			self.polX.append(float(self.press[0]))
			self.polY.append(float(self.press[1]))
			try:
				self.line.remove()
			except:
				pass
			self.line, = cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.plot(self.polX , self.polY, colorLine)
			point = [float(self.press[0]),float(self.press[1])]
			self.polygon.append(point)
			try:
				# Draw the plot
				cfg.uiscp.Scatter_Widget_2.sigCanvas.draw()
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			
	# draw polygon
	def drawPolygon(self, fillColor, transparency, fillOption = True):
		if self.press is not None:
			try:
				self.line.remove()
			except:
				pass
			point = [float(self.press[0]),float(self.press[1])]
			self.polygon.append(point)
			pol = cfg.mplpltSCP.Polygon(self.polygon, True, facecolor=fillColor, alpha=transparency, fill=fillOption)
			self.patches.append(pol)
			self.polP.append(cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.add_patch(pol))
			try:
				# Draw the plot
				cfg.uiscp.Scatter_Widget_2.sigCanvas.draw()
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		
	# calculate scatter raster and add to signature list
	def addToSignatureList(self):
		cfg.uiUtls.addProgressBar()
		r = self.calculatePolygonIntersection("Yes")
		# date time for temp name
		dT = cfg.utls.getTime()
		# temporary layer
		tLN = cfg.tempROINm + dT + ".shp"
		tLP = cfg.tmpDir + "/" + tLN
		cfg.utls.rasterToVector(r, tLP)
		vl = cfg.utls.addVectorLayer(tLP, tLN, "ogr")
		f = cfg.qgisCoreSCP.QgsFeature()
		ids = []
		for f in vl.getFeatures():
			id = f.id()
			ids.append(id)
		if len(ids) > 0:
			vl2 = cfg.utls.mergePolygonsToNewLayer(vl, ids, [0])
			roi = cfg.lstROI
			cfg.lstROI = vl2
			cfg.SCPD.saveROItoShapefile("No")
			cfg.lstROI = roi
			vl = None
			vl2 = None
		cfg.uiUtls.removeProgressBar()
			
	# show area of scatter polygons
	def showScatterPolygonArea(self):
		cfg.uiUtls.addProgressBar()
		self.calculatePolygonIntersection()
		cfg.uiUtls.removeProgressBar()
			
	# conver polygon to raster
	def polygonToRaster(self, polygon, xMin, xMax, yMin, yMax, dX, dY):
		# date time for temp name
		dT = cfg.utls.getTime()
		# temporary layer
		tLN = cfg.polyRasterNm + dT + ".shp"
		tLP = cfg.tmpDir + "/" + tLN
		# get layer crs
		crs = cfg.qgisCoreSCP.QgsCoordinateReferenceSystem("EPSG:4326")
		# create a temp shapefile with a field
		cfg.utls.createEmptyShapefileQGIS(crs, tLP)
		tSS = cfg.utls.addVectorLayer(tLP , tLN, "ogr")
		pointF = cfg.QtCoreSCP.QPointF()
		polF = cfg.QtGuiSCP.QPolygonF()
		for v in polygon:
			pointF.setX(v[0])
			pointF.setY(v[1])
			polF.append(pointF)
		pointF.setX(polygon[0][0])
		pointF.setY(polygon[0][1])
		polF.append(pointF)
		g = cfg.qgisCoreSCP.QgsGeometry().fromQPolygonF(polF)
		oF = cfg.qgisCoreSCP.QgsFeature()
		if g is not None:
			oF.setGeometry(g)
			tSS.startEditing()
			attributeList = [1]
			oF.setAttributes(attributeList)
			tSS.addFeature(oF)
			tSS.commitChanges()
			tSS.dataProvider().createSpatialIndex()
			tSS.updateExtents()
		a = self.rasterizePolygon(tLP, xMin, xMax, yMin, yMax, dX, dY)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return a
			
	# rasterize polygon
	def rasterizePolygon(self, shapefile, xMin, xMax, yMin, yMax, dX, dY):
		shp = cfg.ogrSCP.Open(shapefile)
		gL = shp.GetLayer()
		# date time for temp name
		dT = cfg.utls.getTime()
		# temporary layer
		tLN = cfg.polyRasterNm + dT + ".tif"
		tLP = cfg.tmpDir + "/" + tLN
		rC = abs(int(round((xMax - xMin) / dX)))
		rR = abs(int(round((yMax - yMin) / dY)))
		tD = cfg.gdalSCP.GetDriverByName("GTiff")
		oR = tD.Create(tLP, rC, rR, 1, cfg.gdalSCP.GDT_Int32)
		try:
			oRB = oR.GetRasterBand(1)
		# in case of errors
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		oR.SetGeoTransform( [ xMin , dX, 0 , yMin , 0 , dY ] )
		oRB.SetNoDataValue(cfg.NoDataVal)
		m = cfg.np.zeros((rR, rC), dtype='int32')
		oRB.WriteArray(m, 0, 0)
		oRB.FlushCache()
		# convert reference layer to raster
		oC = cfg.gdalSCP.RasterizeLayer(oR, [1], gL, options = ["ATTRIBUTE=" + str("DN"), "ALL_TOUCHED=TRUE"])
		a =  oRB.ReadAsArray()
		# close bands
		oRB = None
		# close rasters
		oR = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return a

	# create grid
	def createGrid(self, h, xMin, xMax, yMin, yMax, dX, dY, polygon):
		a = self.polygonToRaster(polygon, xMin, xMax, yMin, yMax, dX, dY)
		d = a.T * cfg.np.where(h>0,1,0)
		return d.T
		
	# aggregate grid
	def aggregateGrid(self, grid, h, xMin, xMax, yMin, yMax, dX, dY):
		# structure
		s = cfg.np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])
		ranges = []
		l, ft = cfg.labelSCP(grid, structure=s)
		for v in range(1, ft + 1):
			r = cfg.np.where( l == v )
			rY = r[0][0]
			rXmin = r[1][0]
			rXmax = r[1][-1]
			rangeY = [yMin + rY * dY, yMin + (1 + rY) * dY]
			rangeX = [xMin + rXmin * dX, xMin + (1 + rXmax) * dX]
			ranges.append([rangeX, rangeY])
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
		return ranges

	# calculate polygon intersection
	def calculatePolygonIntersection(self, saveSignature = None):
		if len(self.polygons)>0:
			tW = cfg.uiscp.scatter_list_plot_tableWidget
			bX = cfg.scatterBandX
			bY = cfg.scatterBandY
			r = tW.rowCount()
			rangeList = []
			# grid polygon
			n = 0
			colorList = []
			for p in self.polygons:
				n = n + 1
				colorList.append([n, p[1]])
				for b in range(0, r):
					if tW.item(b, 0).checkState() == 2:
						i = tW.item(b, 6).text()
						if str(i) in list(cfg.ROI_SCP_UID.values()):
							h = cfg.scatterPlotList["HISTOGRAM_" + str(i) + "_" + str([bX, bY])]
						elif str(i) == cfg.sctrROIID:
							h = cfg.sctrROIID_h["HISTOGRAM_" + str(i) + "_" + str([bX, bY])]
						else:
							h = None
						if h is not None:
							grid = self.createGrid(h[0], h[1][0], h[1][-1], h[2][0], h[2][-1], h[1][1]-h[1][0], h[2][1]-h[2][0], p[0])
							ranges = self.aggregateGrid(grid, h[0], h[1][0], h[1][-1], h[2][0], h[2][-1], h[1][1]-h[1][0], h[2][1]-h[2][0])
							rangeList.append([ranges, n])
			rasterSymbol = cfg.utls.rasterScatterSymbol(colorList)
			condition = cfg.utls.createScatterPlotRasterCondition(rangeList)
			aX = cfg.scatterBandX - 1
			aY = cfg.scatterBandY - 1
			# virtual raster
			tPMN = cfg.tmpVrtNm + ".vrt"
			# date time for temp name
			dT = cfg.utls.getTime()
			tPMD = cfg.tmpDir + "/" + dT + tPMN
			# calculation extent
			if cfg.uiscp.extent_comboBox.currentText() == "same as display":
				rectangle = cfg.cnvs.extent()
			else:
				imageName = cfg.bandSetsList[cfg.bndSetNumber][8]
				# band set
				if cfg.bandSetsList[cfg.bndSetNumber][0] == "Yes":
					imageName = cfg.bandSetsList[cfg.bndSetNumber][3][0]
				i = cfg.utls.selectLayerbyName(imageName, "Yes")
				rectangle = i.extent()
			# output raster
			tPMN2 = dT + cfg.scatterRasterNm + ".tif"
			tPMD2 = cfg.tmpDir + "/" + tPMN2
			oM = []
			oM.append(tPMD2)
			# clip by ROI
			bList = cfg.utls.subsetImageByRectangle([rectangle.xMinimum(), rectangle.xMaximum(), rectangle.yMinimum(), rectangle.yMaximum()], cfg.bandSetsList[cfg.bndSetNumber][8], [aX, aY], cfg.bndSetNumber)
			bandNumberList = [1, 1]
			vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "No")
			# open input with GDAL
			rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression)
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			variableList = [["bandX", "a"], ["bandY", "b"]]
			if condition == 0:
				conditions = cfg.utls.singleScatterPlotRasterCondition(rangeList)
				o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.scatterRasterMultipleWhere, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", conditions, variableList, "No")	
			else:
				# calculation
				o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.scatterRasterBandCalculation, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", condition, variableList, "No")
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
			if saveSignature is None:
				# move previous preview to group
				g = cfg.utls.groupIndex(cfg.grpNm)
				if g is None:
					g = cfg.utls.createGroup(cfg.grpNm)
				preP = cfg.utls.selectLayerbyName(cfg.lastScattRaster)
				if preP is not None:
					cfg.utls.moveLayer(preP, cfg.grpNm)
				cfg.lastScattRaster = cfg.osSCP.path.basename(tPMD2)
				r = cfg.utls.addRasterLayer(str(tPMD2), str(cfg.osSCP.path.basename(tPMD2)))
				cfg.utls.setRasterScatterSymbol(r, rasterSymbol)
				cfg.utls.moveLayerTop(r)
				cfg.utls.setGroupVisible(g, False)
				cfg.utls.setGroupExpanded(g, False)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			return tPMD2
		
	# remove polygons
	def removePolygons(self):
		try:
			self.patches = []
			self.polygons = []
			for i in self.polP:
				i.remove()
			self.polP = []
			self.line.remove()
		except:
			pass
		# Draw the plot
		cfg.uiscp.Scatter_Widget_2.sigCanvas.draw()
			
	# save plot to file
	def savePlot(self):
		imgOut = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save plot to file"), "", "JPG file (*.jpg);;PNG file (*.png);;PDF file (*.pdf)", None)
		if len(imgOut) > 0:
			if str(imgOut).endswith(".png"):
				cfg.uiscp.Scatter_Widget_2.sigCanvas.figure.savefig(imgOut, format="png", dpi=300)
			elif str(imgOut).endswith(".pdf"):
				cfg.uiscp.Scatter_Widget_2.sigCanvas.figure.savefig(imgOut, format="pdf", dpi=300)
			elif str(imgOut).endswith(".jpg"):
				cfg.uiscp.Scatter_Widget_2.sigCanvas.figure.savefig(imgOut, format="jpg", dpi=300, quality=90)
			else:
				imgOut = imgOut + ".jpg"
				cfg.uiscp.Scatter_Widget_2.sigCanvas.figure.savefig(imgOut, format="jpg", dpi=300, quality=90)
			
	# fit plot to axes
	def fitPlotToAxes(self, preserveLast = "No"):
		if preserveLast == "Yes":
			xMin = self.lastxMin
			xMax = self.lastxMax
			yMin = self.lastyMin
			yMax = self.lastyMax
		else:
			xMin = self.xMin
			xMax = self.xMax
			yMin = self.yMin
			yMax = self.yMax
		cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_xlim(xMin, xMax)
		cfg.uiscp.Scatter_Widget_2.sigCanvas.ax.set_ylim(yMin, yMax)
		self.lastxMin = xMin
		self.lastxMax = xMax
		self.lastyMin = yMin
		self.lastyMax = yMax
		try:
			# Draw the plot
			cfg.uiscp.Scatter_Widget_2.sigCanvas.draw()
		except Exception as err:
			cfg.mx.msgErr53()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
			
	# Change ROI color
	def changePolygonColor(self):
		c = cfg.QtWidgetsSCP.QColorDialog.getColor()
		if c.isValid():	
			self.color = c.name()
			cfg.uiscp.polygon_color_Button.setStyleSheet("background-color :" + self.color)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "")
			