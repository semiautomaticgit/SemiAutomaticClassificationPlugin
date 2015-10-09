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

import os
import sys
import subprocess
import datetime
import gzip
import tarfile
import zipfile
import time
# for moving files
import shutil
# for debugging
import inspect
from xml.dom import minidom
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class DownloadSentinelImages:

	def __init__(self):
		# emit a QgsPoint on each click
		self.clickUL = QgsMapToolEmitPoint(cfg.cnvs)
		# connect to pointerClick when map is clicked
		self.clickUL.canvasClicked.connect(self.pointerClickUL)
		# emit a QgsPoint on each click
		self.clickLR = QgsMapToolEmitPoint(cfg.cnvs)
		# connect to pointerClick when map is clicked
		self.clickLR.canvasClicked.connect(self.pointerClickLR)
		self.rbbrBndPol = QgsRubberBand(cfg.cnvs, 2)
		cfg.ui.dateEdit_to_3.setDate(QDate.currentDate())
		
	# add rubber band
	def addRubberBandPolygon(self, pointUL, pointLR):
		try:
			self.clearCanvasPoly()
		except:
			pass
		rectangle = [[pointUL, QgsPoint(pointLR.x(), pointUL.y()), pointLR, QgsPoint(pointUL.x(), pointLR.y())]]
		self.rbbrBndPol.setToGeometry(QgsGeometry.fromPolygon(rectangle), None)
		clr = QColor(cfg.ROIClrVal)
		clr.setAlpha(50)
		try:
			# QGIS 2.6
			self.rbbrBndPol.setFillColor(clr)
			#self.rbbrBndPol.setBorderColor(QColor(cfg.ROIClrOutlineValDefault))
			#self.rbbrBndPol.setLineStyle(Qt.DotLine)
			self.rbbrBndPol.setWidth(3)
		except:
			# QGIS < 2.6
			self.rbbrBndPol.setColor(clr)
			#self.rbbrBndPol.setLineStyle(Qt.DotLine)
			self.rbbrBndPol.setWidth(3)
		
	# clear canvas
	def clearCanvasPoly(self):
		self.rbbrBndPol.reset(True)
		cfg.cnvs.refresh()

	# set coordinates
	def pointerClickLR(self, point):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = QgsCoordinateReferenceSystem()
		iCrs.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
		point1 = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
		cfg.ui.LX_lineEdit_5.setText(str(point1.x()))
		cfg.ui.LY_lineEdit_5.setText(str(point1.y()))
		try:
			UL = QgsPoint(float(cfg.ui.UX_lineEdit_5.text()), float(cfg.ui.UY_lineEdit_5.text()))
			UL1 = cfg.utls.projectPointCoordinates(UL, iCrs, pCrs)
			LR = QgsPoint(float(cfg.ui.LX_lineEdit_5.text()), float(cfg.ui.LY_lineEdit_5.text()))
			LR1 = cfg.utls.projectPointCoordinates(LR, iCrs, pCrs)
			self.addRubberBandPolygon(UL1, LR1)
		except:
			pass
		
	# set coordinates
	def pointerClickUL(self, point):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = QgsCoordinateReferenceSystem()
		iCrs.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
		point1 = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
		cfg.ui.UX_lineEdit_5.setText(str(point1.x()))
		cfg.ui.UY_lineEdit_5.setText(str(point1.y()))
		try:
			UL = QgsPoint(float(cfg.ui.UX_lineEdit_5.text()), float(cfg.ui.UY_lineEdit_5.text()))
			UL1 = cfg.utls.projectPointCoordinates(UL, iCrs, pCrs)
			LR = QgsPoint(float(cfg.ui.LX_lineEdit_5.text()), float(cfg.ui.LY_lineEdit_5.text()))
			LR1 = cfg.utls.projectPointCoordinates(LR, iCrs, pCrs)
			self.addRubberBandPolygon(UL1, LR1)
		except:
			pass
		
	# connect to pointer
	def pointerLRActive(self):
		cfg.cnvs.setMapTool(self.clickLR)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: LR")
		
	# connect to pointer
	def pointerULActive(self):
		cfg.cnvs.setMapTool(self.clickUL)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: UL")
		
	# find images
	def findImages(self):
		self.queryDatabase()
		
	def rememberUser(self):
		if cfg.ui.remember_user_checkBox.isChecked():
			user = cfg.ui.user_scihub_lineEdit.text()
			pswd = cfg.utls.encryptPassword(cfg.ui.password_scihub_lineEdit.text())
			cfg.sets.setQGISRegSetting(cfg.regSciHubUser, user)
			cfg.sets.setQGISRegSetting(cfg.regSciHubPass, pswd)
			
	def rememberUserCheckbox(self):
		if cfg.ui.remember_user_checkBox.isChecked():
			self.rememberUser()
		else:
			cfg.sets.setQGISRegSetting(cfg.regSciHubUser, "")
			cfg.sets.setQGISRegSetting(cfg.regSciHubPass, "")
		
	def displayImages(self):
		tW = cfg.ui.	sentinel_images_tableWidget
		ids = []
		for i in tW.selectedIndexes():
			ids.append(i.row())
		id = set(ids)
		if len(id) > 0:
			progressStep = 100 / len(id)
			cfg.uiUtls.addProgressBar()
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			progress = 0
			for i in id:
				imgID = str(tW.item(i, 0).text())
				min_lat = str(tW.item(i, 5).text())
				min_lon = str(tW.item(i, 6).text())
				max_lat = str(tW.item(i, 7).text())
				max_lon = str(tW.item(i, 8).text())
				jpg = str(tW.item(i, 10).text())
				if os.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
					pass
				else:
					self.downloadThumbnail(imgID, min_lat, min_lon, max_lat, max_lon, jpg, progress)
				if os.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
					r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID + ".vrt", imgID + ".vrt")
					cfg.utls.setRasterColorComposite(r, 1, 2, 3)
				progress = progress + progressStep
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.cnvs.refresh()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnails displayed")
		
	def downloadThumbnail(self, imgID, min_lat, min_lon, max_lat, max_lon, imageJPG, progress = None):
		topLevelUrl = 'https://scihub.esa.int'
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		check = cfg.utls.passwordConnect(user, password, imageJPG, topLevelUrl, cfg.tmpDir + "//" + imgID + "_thumb.jpg", progress)
		if check == "Yes":
			cLon = (float(min_lon) + float(max_lon)) / 2
			cLat = (float(min_lat) + float(max_lat)) / 2
			# calculate UTM zone (adapted from http://stackoverflow.com/questions/9186496/determining-utm-zone-to-convert-from-longitude-latitude)
			zone = 1 + int((cLon + 180) / 6)
			# exceptions
			if cLon >= 3.0 and cLon < 12.0 and cLat >= 56.0 and cLat < 64.0:
				zone = 32
			elif cLon >= 0.0 and cLon < 9.0 and cLat >= 72.0 and cLat < 84.0:
				zone = 31
			elif cLon >= 9.0 and cLon < 21.0 and cLat >= 72.0 and cLat < 84.0:
				zone = 33
			elif cLon >= 21.0 and cLon < 33.0 and cLat >= 72.0 and cLat < 84.0:
				zone = 35		
			elif cLon >= 33.0 and cLon < 42.0 and cLat >= 72.0 and cLat < 84.0:
				zone = 37
			UL = QgsPoint(float(min_lon), float(max_lat))
			LR = QgsPoint(float(max_lon), float(min_lat))
			# WGS84 EPSG 4326
			wgsCrs = QgsCoordinateReferenceSystem()
			wgsCrs.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
			iCrs = QgsCoordinateReferenceSystem()
			iCrs.createFromProj4("+proj=utm +zone="+ str(zone) + " +datum=WGS84 +units=m +no_defs")
			UL1 = cfg.utls.projectPointCoordinates(UL, wgsCrs, iCrs)
			LR1 = cfg.utls.projectPointCoordinates(LR, wgsCrs, iCrs)
			if UL1 != False and LR1 != False:
				cfg.utls.getGDALForMac()
				# georeference thumbnail
				a = cfg.gdalPath + "gdal_translate -of VRT -a_ullr " + str(UL1.x()) + " " + str(UL1.y()) + " " + str(LR1.x()) + " " + str(LR1.y()) + ' -a_srs "+proj=utm +zone=' + str(zone) + ' +datum=WGS84 +units=m +no_defs" ' + cfg.tmpDir + "//" + imgID + "_thumb.jpg " + cfg.tmpDir + "//" + imgID + ".vrt"
				try:
					sP = subprocess.Popen(a, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					sP.wait()
					# get error
					out, err = sP.communicate()
					sP.stdout.close()
					if len(err) > 0:
						cfg.mx.msgBarError(QApplication.translate("semiautomaticclassificationplugin", "Error"), err)
						st = "Yes"
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error:: " + str(err) )
				# in case of errors
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					sP = subprocess.Popen(a, shell=True)
					sP.wait()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnail downloaded" + str(imgID))
			else:
				cfg.mx.msgErr41()
		else:
			cfg.mx.msgErr40()
	
	# remove highlighted images from table
	def removeImageFromTable(self):
		tW = cfg.ui.	sentinel_images_tableWidget
		cfg.utls.removeRowsFromTable(tW)
			
	# download images in table
	def downloadImages(self):
		tW = cfg.ui.	sentinel_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Download the images in the table (requires internet connection)"))
			if len(d) > 0:
				self.downloadSentinelImages(d)
		
	# download images
	def downloadSentinelImages(self, outputDirectory, exporter = "No"):
		cfg.uiUtls.addProgressBar()
		tW = cfg.ui.	sentinel_images_tableWidget
		c = tW.rowCount()
		progressStep = 100 / c
		progress = 0
		outDirList = []
		imgList = []
		links = []
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				imgName = str(tW.item(i, 0).text())
				imgID = str(tW.item(i, 11).text())
				if cfg.ui.download_if_preview_in_legend_checkBox_3.isChecked() and cfg.utls.selectLayerbyName(imgName + ".vrt", "Yes") is None:
					pass
				else:
					progress = progress + progressStep
					urlL = "https://scihub.esa.int/dhus/odata/v1/Products('" + imgID + "')/$value"
					outFile = cfg.tmpDir + "/" + imgName + ".zip"
					if exporter == "No":
						topLevelUrl = 'https://scihub.esa.int'
						user = cfg.ui.user_scihub_lineEdit.text()
						password =cfg.ui.password_scihub_lineEdit.text()
						check = cfg.utls.passwordConnect(user, password, urlL, topLevelUrl, outFile, progress)
						if check == "Yes":
							try:
								if os.path.getsize(outFile) > 10000:
									with zipfile.ZipFile(outFile, "r") as zFile:
										zFile.extractall(outputDirectory)										
									os.remove(outFile)
									outDirList.append(outputDirectory + "/" + imgName + ".SAFE/GRANULE")
								else:
									cfg.mx.msgErr50(imgName)
							except Exception, err:
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								cfg.mx.msgErr50(imgName)
					else:
						links.append(urlL)
			else:
				cfg.uiUtls.removeProgressBar()
				return "No"
		if exporter == "Yes":
			return links
		else:
			cfg.cnvs.setRenderFlag(False)
			if cfg.ui.load_in_QGIS_checkBox_3.isChecked():
				for d in outDirList:
					for g in os.listdir(d):
						for f in os.listdir(d + "/" + g + '/IMG_DATA'):
							if f.lower().endswith(".jp2"):
								# convert jp2 to tif file
								cfg.utls.GDALCopyRaster(d + "/" + g + '/IMG_DATA' + "/" + f, d + "/" + g + '/IMG_DATA' + "/" + os.path.splitext(f)[0] + ".tif", "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
								r = cfg.utls.addRasterLayer(d + "/" + g + '/IMG_DATA' + "/" + os.path.splitext(f)[0] + ".tif", os.path.splitext(f)[0] + ".tif")
								
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.utls.finishSound()
					
	def exportLinks(self):
		d = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Export download links"), "", "*.txt")
		if len(d) > 0:
			links = self.downloadSentinelImages("No", "Yes")
			if links == "No":
				pass
			else:
				l = open(d, 'w')
				for t in links:
					l.write(t + "\n")
				l.close()
				cfg.uiUtls.removeProgressBar()
					
	# read database
	def queryDatabase(self):
		QdateFrom = cfg.ui.dateEdit_from_3.date()
		QdateTo = cfg.ui.dateEdit_to_3.date()
		dateFrom = QdateFrom.toPyDate()
		dateTo = QdateTo.toPyDate()
		if len(cfg.ui.imageID_lineEdit_3.text()) > 0:
			imgQuery = cfg.ui.imageID_lineEdit_3.text()
		else:
			imgQuery = "S2A*"
			try:
				rubbRect = QgsRectangle(float(cfg.ui.UX_lineEdit_5.text()), float(cfg.ui.UY_lineEdit_5.text()), float(cfg.ui.LX_lineEdit_5.text()), float(cfg.ui.LY_lineEdit_5.text()))
				if abs(float(cfg.ui.UX_lineEdit_5.text()) - float(cfg.ui.LX_lineEdit_5.text())) > 10 or abs(float(cfg.ui.UY_lineEdit_5.text()) - float(cfg.ui.LY_lineEdit_5.text())) > 10:
					cfg.mx.msgWar18()
					#return "No"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		cfg.uiUtls.addProgressBar()
		cfg.cnvs.setRenderFlag(False)
		tW = cfg.ui.	sentinel_images_tableWidget
		cfg.utls.clearTable(tW)
		cfg.uiUtls.updateBar(30, QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
		qApp.processEvents()
		imageTableList = []
		url = 'https://scihub.esa.int/dhus/search?q=' + imgQuery + '%20AND%20beginPosition:[' + str(dateFrom) + 'T00:00:00.000Z%20TO%20' + str(dateTo) + 'T23:59:59.999Z]%20AND%20footprint:"Intersects%28POLYGON%28%28' + cfg.ui.UX_lineEdit_5.text() + "%20" + cfg.ui.UY_lineEdit_5.text() + "," + cfg.ui.UX_lineEdit_5.text() + "%20" + cfg.ui.LY_lineEdit_5.text() + "," + cfg.ui.LX_lineEdit_5.text() + "%20" + cfg.ui.LY_lineEdit_5.text() + "," + cfg.ui.LX_lineEdit_5.text() + "%20" + cfg.ui.UY_lineEdit_5.text() + "," + cfg.ui.UX_lineEdit_5.text() + "%20" + cfg.ui.UY_lineEdit_5.text() + '%29%29%29%22'
		topLevelUrl = 'https://scihub.esa.int'
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		response = cfg.utls.passwordConnect(user, password, url, topLevelUrl)
		if response == "No":
			cfg.uiUtls.removeProgressBar()
			return "No"
		#info = response.info()
		xml = response.read()
		tW.setSortingEnabled(False)
		doc = minidom.parseString(xml)
		entries = doc.getElementsByTagName("entry")
		for entry in entries:
			# add item to table
			c = tW.rowCount()
			# add list items to table
			tW.setRowCount(c + 1)
			imgNameTag = entry.getElementsByTagName("title")[0]
			imgName = imgNameTag.firstChild.data
			imgNm = QTableWidgetItem(imgName)
			imgIDTag = entry.getElementsByTagName("id")[0]
			imgID = imgIDTag.firstChild.data
			imgIDtable = QTableWidgetItem(imgID)
			summary = entry.getElementsByTagName("summary")[0]
			infos = summary.firstChild.data.split(',')
			for info in infos:
				infoIt = info.strip().split(' ')
				if infoIt[0] == "Date:":
					acqDate = QTableWidgetItem(infoIt[1])
				if infoIt[0] == "Satellite:":
					print "Satellite " + infoIt[1]
				if infoIt[0] == "Size:":
					size = infoIt[1] + " " + infoIt[2]
			strings = entry.getElementsByTagName("str")
			for x in strings:
				attr = x.getAttribute("name")
				if attr == "footprint":
					footprintCoord = x.firstChild.data.replace('POLYGON ((', "").replace('))', "").split(',')
					xList = []
					yList = []
					for coords in footprintCoord:
						xList.append(float(coords.split(' ')[0]))
						yList.append(float(coords.split(' ')[1]))
					min_lon = min(xList)
					max_lon = max(xList)
					min_lat = min(yList)
					max_lat = max(yList)
			#path = QTableWidgetItem()
			#path.setData(Qt.DisplayRole, int(p[4]))
			#row = QTableWidgetItem()
			#row.setData(Qt.DisplayRole, int(p[5]))
			MinLat = QTableWidgetItem()
			MinLat.setData(Qt.DisplayRole, float(min_lat))
			MinLon = QTableWidgetItem()
			MinLon.setData(Qt.DisplayRole, float(min_lon))
			MaxLat = QTableWidgetItem()
			MaxLat.setData(Qt.DisplayRole, float(max_lat))
			MaxLon = QTableWidgetItem()
			MaxLon.setData(Qt.DisplayRole, float(max_lon))
			imgSize = QTableWidgetItem(size)
			imgPreview = QTableWidgetItem("https://scihub.esa.int/dhus/odata/v1/Products%28'" +  imgID + "'%29/Products%28'Quicklook'%29/$value")
			tW.setItem(c, 0, imgNm)
			tW.setItem(c, 1, acqDate)
			#tW.setItem(c, 3, path)
			#tW.setItem(c, 4, row)
			tW.setItem(c, 5, MinLat)
			tW.setItem(c, 6, MinLon)
			tW.setItem(c, 7, MaxLat)
			tW.setItem(c, 8, MaxLon)
			tW.setItem(c, 9, imgSize)
			tW.setItem(c, 10, imgPreview)
			tW.setItem(c, 11, imgIDtable)
			tW.setColumnWidth(0, 200)
			tW.setColumnWidth(1, 100)
			tW.setColumnWidth(2, 100)
			tW.setColumnWidth(3, 60)
			tW.setColumnWidth(4, 60)
			tW.setColumnWidth(5, 80)
			tW.setColumnWidth(6, 80)
			tW.setColumnWidth(7, 80)
			tW.setColumnWidth(8, 80)
		tW.setSortingEnabled(True)
		cfg.cnvs.setRenderFlag(True)				
		cfg.uiUtls.removeProgressBar()
		self.clearCanvasPoly()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Sentinel images")

	def clearTable(self):
		# ask for confirm
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Reset signature list"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the table?"))
		if a == "Yes":
			tW = cfg.ui.	sentinel_images_tableWidget
			cfg.utls.clearTable(tW)
			