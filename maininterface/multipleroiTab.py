# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

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

class MultipleROITab:

	def __init__(self):
		pass
		
	# add point
	def addPointToTable(self):
		tW = cfg.ui.point_tableWidget
		# add item to table
		c = tW.rowCount()
		# add list items to table
		tW.setRowCount(c + 1)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "added point " + str(c + 1))
		
	# add random point
	def addRandomPointToTable(self, point):
		tW = cfg.ui.point_tableWidget
		# add item to table
		c = tW.rowCount()
		# add list items to table
		tW.setRowCount(c + 1)
		#tW.setRowCount(c + 1)
		if cfg.uidc.rapid_ROI_checkBox.isChecked() is True:
			RBand = str(cfg.ROIband)
		else:
			RBand = ""
		cfg.utls.addTableItem(tW, str(point[0]), c, 0)
		cfg.utls.addTableItem(tW, str(point[1]), c, 1)
		cfg.utls.addTableItem(tW, str(cfg.ROIMacroID), c, 2)
		cfg.utls.addTableItem(tW, str(cfg.ROIMacroClassInfo), c, 3)
		cfg.utls.addTableItem(tW, str(cfg.ROIID), c, 4)
		cfg.utls.addTableItem(tW, str(cfg.ROIInfo), c, 5)
		cfg.utls.addTableItem(tW, str(cfg.minROISz), c, 6)
		cfg.utls.addTableItem(tW, str(cfg.maxROIWdth), c, 7)
		cfg.utls.addTableItem(tW, str(cfg.rngRad), c, 8)
		cfg.utls.addTableItem(tW, RBand, c, 9)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "added point " + str(c + 1))
			
	# text changed
	def textChanged(self):
		stratifiedExpression = cfg.ui.stratified_lineEdit.text()
		tSplit = stratifiedExpression.split(";")
		for b in tSplit:
			try:
				cfg.ui.stratified_lineEdit.setStyleSheet("color : green")
				check = "Yes"
				eval(b.replace(cfg.variableName, "1"))
				if b.strip() == cfg.variableName:
					cfg.ui.stratified_lineEdit.setStyleSheet("color : red")
					check = "No"
			except:
				cfg.ui.stratified_lineEdit.setStyleSheet("color : red")
				check = "No"
		return check
		
	# create random point
	def createRandomPoint(self):
		if cfg.bandSetsList[cfg.bndSetNumber][0] == "Yes":
			imageName = cfg.bandSetsList[cfg.bndSetNumber][3][0]
		else:
			try:
				imageName = cfg.bandSetsList[cfg.bndSetNumber][8]
			except:
				cfg.mx.msg4()
				return "No"
		img = cfg.utls.selectLayerbyName(imageName, "Yes")
		crs = cfg.utls.getCrs(img)
		geographicFlag = crs.isGeographic()
		if geographicFlag is False:
			minDistance = None
			points = None
			stratified = None
			stratifiedExpression = None
			bandSetNumber = None
			if cfg.ui.stratified_point_checkBox.isChecked() is True:
				check = cfg.multiROI.textChanged()
				if check == "Yes":
					stratified = "Yes"
					stratifiedExpression = cfg.ui.stratified_lineEdit.text()
					bandSet = cfg.ui.band_set_comb_spinBox_10.value()
					bandSetNumber = bandSet - 1
				else:
					cfg.mx.msgErr64()
					return "No"
			cfg.uiUtls.addProgressBar()
			tLX, tLY, lRX, lRY, pSX, pSY = cfg.utls.imageInformationSize(imageName)
			Xmin = int(round(min(tLX, lRX)))
			Xmax = int(round(max(tLX, lRX)))
			Ymin = int(round(min(tLY, lRY)))
			Ymax = int(round(max(tLY, lRY)))
			pointNumber = int(cfg.ui.point_number_spinBox.value())
			cfg.uiUtls.updateBar(10)

			if cfg.ui.point_distance_checkBox.isChecked() is True:
				minDistance = int(cfg.ui.point_distance_spinBox.value())
			if cfg.ui.point_grid_checkBox.isChecked() is True:
				gridSize = int(cfg.ui.point_grid_spinBox.value())
				XRange = list(range(Xmin, Xmax, gridSize))
				YRange = list(range(Ymin, Ymax, gridSize))
				if len(XRange) == 1:
					XRange = [Xmin, Xmax]	
				if len(YRange) == 1:
					YRange = [Ymin, Ymax]
				for x in XRange:
					if XRange.index(x) < (len(XRange) - 1):
						for y in YRange:
							if YRange.index(y) < (len(YRange) - 1):
								newpoints = cfg.utls.randomPoints(1, x, XRange[XRange.index(x)+1], y, YRange[YRange.index(y)+1], minDistance, imageName, None, None, None, bandSetNumber)
								if points is None:
									points = newpoints
								else:
									points.append(newpoints[0])
			elif stratified is not None:
				tSplit = stratifiedExpression.split(";")
				for b in tSplit:
					newpoints = cfg.utls.randomPoints(pointNumber, Xmin, Xmax, Ymin, Ymax, minDistance, imageName, None, stratified, b, bandSetNumber)				
					if points is None:
						points = newpoints
					else:
						points = points + newpoints
			else:
				points = cfg.utls.randomPoints(pointNumber, Xmin, Xmax, Ymin, Ymax, minDistance, imageName, None, None, None, bandSetNumber)
			cfg.uiUtls.updateBar(50)
			# check distance
			if minDistance is not None:
				npPoints = cfg.np.array(points)
				for i in range(0, len(points)):
					distance = cfg.cdistSCP(npPoints, npPoints)
					if i < distance.shape[0]:
						index = cfg.np.where((distance[i,:] <= minDistance)  & (distance[i,:] > 0))
						npPoints = cfg.np.delete(npPoints, index, 0)
				points = npPoints.tolist()
			for i in range(0, len(points)):
				self.addRandomPointToTable(points[i])
			cfg.uiUtls.updateBar(100)
			cfg.uiUtls.removeProgressBar()
		else:
			cfg.mx.msgWar14()
		
	# create ROI
	def createROIfromPoint(self):
		tW = cfg.ui.point_tableWidget
		c = tW.rowCount()
		if c > 0:
			# save previous point for single ROI
			try:
				pP = cfg.lstPnt
			except:
				pass
			cfg.uiUtls.addProgressBar()
			for i in range(0, c):
				cfg.QtWidgetsSCP.qApp.processEvents()
				if cfg.actionCheck != "No":
					cfg.uiUtls.updateBar((i+1) * 100 / (c + 1))
					try:
						X = tW.item(i,0).text()
						Y = tW.item(i,1).text()
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.mx.msg6()
					try:
						p = cfg.qgisCoreSCP.QgsPointXY(float(X), float(Y))
						cfg.utls.checkPointImage(cfg.bandSetsList[cfg.bndSetNumber][8], p)
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
							cfg.origPoint = cfg.pntROI
							cfg.SCPD.createROI(cfg.pntROI, "No")
							# save ROI
							v = int(tW.item(i, 2).text())
							cfg.ROIMacroID = v
							cfg.ROIMacroClassInfo = tW.item(i, 3).text()
							v = int(tW.item(i, 4).text())
							cfg.ROIID = v
							cfg.ROIInfo = tW.item(i, 5).text()
							cfg.SCPD.saveROItoShapefile("No")
							# disable undo save ROI
							cfg.uidc.undo_save_Button.setEnabled(False)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.mx.msgErr20()
				# restore settings for single ROI 
				cfg.SCPD.setROIMacroID()
				cfg.SCPD.roiMacroclassInfo()
				cfg.SCPD.setROIID()
				cfg.SCPD.roiClassInfo()
				cfg.SCPD.minROISize()
				cfg.SCPD.maxROIWidth()
				cfg.SCPD.rangeRadius()
				cfg.SCPD.rapidROIband()
				cfg.SCPD.rapidROICheckbox()
			cfg.utls.finishSound()
			cfg.uiUtls.removeProgressBar()
			# restore previous point for single ROI
			try:
				cfg.lstPnt = pP
			except:
				pass
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ROI created")

	# export point list to file
	def exportPointList(self):
		pointListFile = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save the point list to file"), "", "*.csv", "csv")
		try:
			if pointListFile.lower().endswith(".csv"):
				pass
			else:
				pointListFile = pointListFile + ".csv"
			f = open(pointListFile, 'w')
			sep = "\t"
			f.write("X\tY\tMC_ID\tMC_Info\tC_ID\tC_Info\tMin\tMax\tDist\tRapid_ROI_band\n")
			f.close()
			tW = cfg.ui.point_tableWidget
			c = tW.rowCount()
			for i in range(0, c):
				f = open(pointListFile, 'a')
				sep = "\t"
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
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " point list exported")
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# import points from file
	def importPoints(self):
		pointFile = cfg.utls.getOpenFileName(None , "Select a point list file", "", "CSV (*.csv);; Point shapefile .shp (*.shp)")
		if pointFile.lower().endswith(".csv"):
			try:
				f = open(pointFile)
				if cfg.osSCP.path.isfile(pointFile):
					file = f.readlines()
					if "\t" in file[0]:
						sep = "\t"
					else:
						sep = ";"
					tW = cfg.ui.point_tableWidget
					for b in range(1, len(file)):
						# point list
						p = file[b].strip().split(sep)
						MinSize = cfg.minROISz
						MaxWidth = cfg.maxROIWdth
						RangRad = cfg.rngRad
						RBand = ""
						try:
							MinSize = p[6]
							MaxWidth = p[7]
							RangRad = p[8]
							RBand = p[9]
						except:
							pass
						# add item to table
						c = tW.rowCount()
						# add list items to table
						tW.setRowCount(c + 1)
						cfg.utls.addTableItem(tW, p[0], c, 0)
						cfg.utls.addTableItem(tW, p[1], c, 1)
						cfg.utls.addTableItem(tW, p[2], c, 2)
						cfg.utls.addTableItem(tW, p[3], c, 3)
						cfg.utls.addTableItem(tW, p[4], c, 4)
						cfg.utls.addTableItem(tW, p[5], c, 5)
						cfg.utls.addTableItem(tW, MinSize, c, 6)
						cfg.utls.addTableItem(tW, MaxWidth, c, 7)
						cfg.utls.addTableItem(tW, RangRad, c, 8)
						cfg.utls.addTableItem(tW, RBand, c, 9)
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " points imported")
			except Exception as err:
				cfg.mx.msgErr19()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		elif pointFile.lower().endswith(".shp"):
			try:
				lPRS = cfg.utls.getEPSGVector(pointFile)
				# band set
				if cfg.bandSetsList[cfg.bndSetNumber][0] == "Yes":
					try:
						imageName = cfg.bandSetsList[cfg.bndSetNumber][3][0]
					except:
						cfg.mx.msgWar25(str(cfg.bndSetNumber + 1))
						return "No"
					# image CRS
					bN0 = cfg.utls.selectLayerbyName(imageName, "Yes")
					iCrs = cfg.utls.getCrs(bN0)
				else:
					# image CRS
					bN0 = cfg.utls.selectLayerbyName(imageName, "Yes")
					iCrs = cfg.utls.getCrs(bN0)
				rPSys = cfg.osrSCP.SpatialReference(wkt=iCrs.toWkt())
				rPSys.AutoIdentifyEPSG()
				rPRS = rPSys.GetAuthorityCode(None)
				if str(lPRS) != str(rPRS):
					# date time for temp name
					dT = cfg.utls.getTime()
					reprjShapefile = cfg.tmpDir + "/" + dT + cfg.osSCP.path.basename(pointFile)
					cfg.utls.repojectShapefile(pointFile, int(lPRS), reprjShapefile, int(rPRS), "wkbPoint")
					pointFile = reprjShapefile
				d = cfg.ogrSCP.GetDriverByName("ESRI Shapefile")
				dr = d.Open(pointFile, 0)
				iL = dr.GetLayer()
				iF = iL.GetNextFeature()
				while iF:
					g = iF.GetGeometryRef()
					p = [g.GetX(), g.GetY()]
					iF.Destroy()
					iF = iL.GetNextFeature()
					self.addRandomPointToTable(p)
				iL = None
				dr = None
			except Exception as err:
				cfg.mx.msgErr19()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				
	def removePointFromTable(self):
		cfg.utls.removeRowsFromTable(cfg.ui.point_tableWidget)
			
	# Activate signature calculation checkbox2
	def signatureCheckbox2(self):
		p = cfg.qgisCoreSCP.QgsProject.instance()
		if cfg.ui.signature_checkBox2.isChecked() is True:
			p.writeEntry("SemiAutomaticClassificationPlugin", "calculateSignature", "Yes")
			cfg.sigClcCheck = "Yes"
			cfg.uidc.signature_checkBox.setCheckState(2)
		else:
			p.writeEntry("SemiAutomaticClassificationPlugin", "calculateSignature", "No")
			cfg.sigClcCheck = "No"
			cfg.uidc.signature_checkBox.setCheckState(0)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.sigClcCheck))
	