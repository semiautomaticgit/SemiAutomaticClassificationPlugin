# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
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

import os
import inspect
import numpy as np
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class MultipleROITab:

	def __init__(self):
		pass
		
	def addPointToTable(self):
		tW = cfg.ui.point_tableWidget
		# add item to table
		c = tW.rowCount()
		# add list items to table
		tW.setRowCount(c + 1)
		it = QTableWidgetItem(str(c + 1))
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "added point " + str(c + 1))
		
	def addRandomPointToTable(self, point):
		tW = cfg.ui.point_tableWidget
		# add item to table
		c = tW.rowCount()
		# add list items to table
		tW.setRowCount(c + 1)
		it = QTableWidgetItem(str(c + 1))
		X = QTableWidgetItem(str(point[0]))
		Y = QTableWidgetItem(str(point[1]))
		MID = QTableWidgetItem(str(cfg.ROIMacroID))
		MInf = QTableWidgetItem(str(cfg.ROIMacroClassInfo))
		CID = QTableWidgetItem(str(cfg.ROIID))
		CInf = QTableWidgetItem(str(cfg.ROIInfo))
		MinSize = QTableWidgetItem(str(cfg.minROISz))
		MaxWidth = QTableWidgetItem(str(cfg.maxROIWdth))
		RangRad = QTableWidgetItem(str(cfg.rngRad))
		if cfg.uid.rapid_ROI_checkBox.isChecked() is True:
			RBand = QTableWidgetItem(str(cfg.ROIband))
		else:
			RBand = QTableWidgetItem(str(""))
		# add list items to table
		tW.setRowCount(c + 1)
		tW.setItem(c, 0, X)
		tW.setItem(c, 1, Y)
		tW.setItem(c, 2, MID)
		tW.setItem(c, 3, MInf)
		tW.setItem(c, 4, CID)
		tW.setItem(c, 5, CInf)
		tW.setItem(c, 6, MinSize)
		tW.setItem(c, 7, MaxWidth)
		tW.setItem(c, 8, RangRad)
		tW.setItem(c, 9, RBand)
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "added point " + str(c + 1))
				
	def createRandomPoint(self):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			imageName = cfg.bndSet[0]
		else:
			if cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes") is None:
				cfg.mx.msg4()
				return "No"
			else:
				imageName = cfg.rstrNm	
				# logger
				if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "No image selected")
		img = cfg.utls.selectLayerbyName(imageName, "Yes")
		crs = cfg.utls.getCrs(img)
		geographicFlag = crs.geographicFlag()
		if geographicFlag is False:
			cfg.uiUtls.addProgressBar()
			tLX, tLY, lRX, lRY, pS = cfg.utls.imageInformationSize(imageName)
			Xmin = int(round(min(tLX, lRX)))
			Xmax = int(round(max(tLX, lRX)))
			Ymin = int(round(min(tLY, lRY)))
			Ymax = int(round(max(tLY, lRY)))
			pointNumber = int(cfg.ui.point_number_spinBox.value())
			cfg.uiUtls.updateBar(10)
			minDistance = None
			points = None
			if cfg.ui.point_distance_checkBox.isChecked() is True:
				minDistance = int(cfg.ui.point_distance_spinBox.value())
			if cfg.ui.point_grid_checkBox.isChecked() is True:
				gridSize = int(cfg.ui.point_grid_spinBox.value())
				XRange = range(Xmin, Xmax, gridSize)
				YRange = range(Ymin, Ymax, gridSize)
				for x in XRange:
					if XRange.index(x) < (len(XRange) - 1):
						for y in YRange:
							if YRange.index(y) < (len(YRange) - 1):
								newpoints = cfg.utls.randomPoints(pointNumber, x, XRange[XRange.index(x)+1], y, YRange[YRange.index(y)+1], minDistance)
								if points is None:
									points = newpoints
								else:
									points = np.concatenate((points, newpoints), axis=0)
			else:
				points = cfg.utls.randomPoints(pointNumber, Xmin, Xmax, Ymin, Ymax, minDistance)
			cfg.uiUtls.updateBar(50)
			for i in range(0, points.shape[0]):
				self.addRandomPointToTable(points[i])
			cfg.uiUtls.updateBar(100)
			cfg.uiUtls.removeProgressBar()
		else:
			cfg.mx.msgWar14()
		
	def createROIfromPoint(self):
		tW = cfg.ui.point_tableWidget
		c = tW.rowCount()
		# save previous point for single ROI
		try:
			pP = cfg.lstPnt
		except:
			pass
		cfg.uiUtls.addProgressBar()
		for i in range(0, c):
			qApp.processEvents()
			if cfg.actionCheck != "No":
				cfg.uiUtls.updateBar((i+1) * 100 / (c + 1))
				try:
					X = tW.item(i,0).text()
					Y = tW.item(i,1).text()
				except Exception, err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.mx.msg6()
				try:
					p = QgsPoint(float(X), float(Y))
					cfg.utls.checkPointImage(cfg.rstrNm, p)
					if cfg.pntCheck == "Yes":
						cfg.pntROI = cfg.lstPnt
						# create ROI
						if len(tW.item(i,6).text()) > 0:
							v = int(tW.item(i,6).text())
							cfg.minROISz = v
						if len(tW.item(i,7).text()) > 0:
							v = int(tW.item(i,7).text())
							cfg.maxROIWdth = v
						if len(tW.item(i,8).text()) > 0:
							v = float(tW.item(i,8).text())
							cfg.rngRad = v
						if len(tW.item(i,9).text()) > 0:
							v = int(tW.item(i,9).text())
							cfg.ROIband = v
							cfg.rpdROICheck = "Yes"
						cfg.ROId.createROI(cfg.pntROI, "No")
						# save ROI
						v = int(tW.item(i, 2).text())
						cfg.ROIMacroID = v
						cfg.ROIMacroClassInfo = tW.item(i, 3).text()
						v = int(tW.item(i, 4).text())
						cfg.ROIID = v
						cfg.ROIInfo = tW.item(i, 5).text()
						cfg.ROId.saveROItoShapefile("No")
						# disable undo save ROI
						cfg.uid.undo_save_Button.setEnabled(False)
				except Exception, err:
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.mx.msgErr20()
			# restore settings for single ROI 
			cfg.ROId.setROIMacroID()
			cfg.ROId.roiMacroclassInfo()
			cfg.ROId.setROIID()
			cfg.ROId.roiClassInfo()
			cfg.ROId.minROISize()
			cfg.ROId.maxROIWidth()
			cfg.ROId.rangeRadius()
			cfg.ROId.rapidROIband()
			cfg.ROId.rapidROICheckbox()
		cfg.uiUtls.removeProgressBar()
			# restore previous point for single ROI
		try:
			cfg.lstPnt = pP
		except:
			pass
		# logger
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ROI created")

	# export point list to file
	def exportPointList(self):
		pointListFile = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Save the point list to file"), "", "CSV (*.csv)")
		try:
			f = open(pointListFile, 'w')
			f.write("X;Y;MC ID;MC Info;C ID;C Info;Min size;Max width;Range radius;Rapid ROI band\n")
			f.close()
			tW = cfg.ui.point_tableWidget
			c = tW.rowCount()
			for i in range(0, c):
				f = open(pointListFile, 'a')
				sep = ";"
				X = tW.item(i,0).text()
				Y = tW.item(i,1).text()
				MID = tW.item(i,2).text()
				MInf = tW.item(i,3).text()
				CID = tW.item(i,4).text()
				CInf = tW.item(i,5).text()
				MinSize = ""
				MaxWidth = ""
				RangRad = ""
				RBand = ""
				try:
					MinSize = tW.item(i,6).text()
					MaxWidth = tW.item(i,7).text()
					RangRad = tW.item(i,8).text()
					RBand = tW.item(i,9).text()
				except:
					pass
				else:
					Inf = ""
				txt = X + sep + Y + sep + MID + sep + MInf + sep + CID + sep + CInf + sep + MinSize + sep + MaxWidth + sep + RangRad + sep + RBand+ "\n"
				f.write(txt)
				f.close()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " point list exported")
		except Exception, err:
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# import points from file
	def importPoints(self):
		pointFile = QFileDialog.getOpenFileName(None , "Select a point list file", "", "CSV (*.csv)")
		try:
			f = open(pointFile)
			sep = ";"
			if os.path.isfile(pointFile):
				file = f.readlines()
				tW = cfg.ui.point_tableWidget
				for b in range(1, len(file)):
					# point list
					p = file[b].strip().split(sep)
					X = QTableWidgetItem(p[0])
					Y = QTableWidgetItem(p[1])
					MID = QTableWidgetItem(p[2])
					MInf = QTableWidgetItem(p[3])
					CID = QTableWidgetItem(p[4])
					CInf = QTableWidgetItem(p[5])
					MinSize = cfg.minROISz
					MaxWidth = cfg.maxROIWdth
					RangRad = cfg.rngRad
					RBand = ""
					try:
						MinSize = QTableWidgetItem(p[6])
						MaxWidth = QTableWidgetItem(p[7])
						RangRad = QTableWidgetItem(p[8])
						RBand = QTableWidgetItem(p[9])
					except:
						pass
					# add item to table
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					tW.setItem(c, 0, X)
					tW.setItem(c, 1, Y)
					tW.setItem(c, 2, MID)
					tW.setItem(c, 3, MInf)
					tW.setItem(c, 4, CID)
					tW.setItem(c, 5, CInf)
					tW.setItem(c, 6, MinSize)
					tW.setItem(c, 7, MaxWidth)
					tW.setItem(c, 8, RangRad)
					tW.setItem(c, 9, RBand)
					# logger
					if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " points imported")
		except Exception, err:
			cfg.mx.msgErr19()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))

	def removePointFromTable(self):
		# ask for confirm
		a = cfg.utls.questionBox("Remove points", "Are you sure you want to remove the selected points from the table?")
		if a == "Yes":
			tW = cfg.ui.point_tableWidget
			c = tW.rowCount()
			# list of item to remove
			iR  = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			# remove items
			for i in reversed(range(0, len(iR))):
				tW.removeRow(iR[i])
			c = tW.rowCount()
			# logger
			if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " points removed")
			
	# Activate signature calculation checkbox2
	def signatureCheckbox2(self):
		p = QgsProject.instance()
		if cfg.ui.signature_checkBox2.isChecked() is True:
			p.writeEntry("SemiAutomaticClassificationPlugin", "calculateSignature", "Yes")
			cfg.sigClcCheck = "Yes"
			cfg.uid.signature_checkBox.setCheckState(2)
		else:
			p.writeEntry("SemiAutomaticClassificationPlugin", "calculateSignature", "No")
			cfg.sigClcCheck = "No"
			cfg.uid.signature_checkBox.setCheckState(0)
		if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.sigClcCheck))
	