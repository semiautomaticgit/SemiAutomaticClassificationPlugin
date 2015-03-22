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
# for moving files
import shutil
# for debugging
import inspect
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class DownloadLandsatImages:

	def __init__(self):
		# check all bands
		self.checkAll = "No"
		# emit a QgsPoint on each click
		self.clickUL = QgsMapToolEmitPoint(cfg.cnvs)
		# connect to pointerClick when map is clicked
		self.clickUL.canvasClicked.connect(self.pointerClickUL)
		# emit a QgsPoint on each click
		self.clickLR = QgsMapToolEmitPoint(cfg.cnvs)
		# connect to pointerClick when map is clicked
		self.clickLR.canvasClicked.connect(self.pointerClickLR)
		self.rbbrBndPol = QgsRubberBand(cfg.cnvs, 2)
		
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
		cfg.ui.LX_lineEdit_3.setText(str(point1.x()))
		cfg.ui.LY_lineEdit_3.setText(str(point1.y()))
		try:
			UL = QgsPoint(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()))
			UL1 = cfg.utls.projectPointCoordinates(UL, iCrs, pCrs)
			LR = QgsPoint(float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
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
		cfg.ui.UX_lineEdit_3.setText(str(point1.x()))
		cfg.ui.UY_lineEdit_3.setText(str(point1.y()))
		try:
			UL = QgsPoint(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()))
			UL1 = cfg.utls.projectPointCoordinates(UL, iCrs, pCrs)
			LR = QgsPoint(float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
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
		self.readDatabase()
		
	def displayImages(self):
		tW = cfg.ui.landsat_images_tableWidget
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
				path = str(tW.item(i, 3).text())
				row = str(tW.item(i, 4).text())
				min_lat = str(tW.item(i, 5).text())
				min_lon = str(tW.item(i, 6).text())
				max_lat = str(tW.item(i, 7).text())
				max_lon = str(tW.item(i, 8).text())
				if os.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
					pass
				else:
					self.downloadThumbnail(imgID, path, row, min_lat, min_lon, max_lat, max_lon, progress)
				if os.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
					r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID + ".vrt", imgID + ".vrt")
					cfg.utls.setRasterColorComposite(r, 1, 2, 3)
				progress = progress + progressStep
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.cnvs.refresh()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnails displayed")
		
	def downloadThumbnail(self, imgID, path, row, min_lat, min_lon, max_lat, max_lon, progress = None):
		check = cfg.utls.downloadFile("http://landsat-pds.s3.amazonaws.com/L8/" + path.zfill(3) + "/" + row.zfill(3) +"/" + imgID + "/" + imgID + "_thumb_large.jpg", cfg.tmpDir + "//" + imgID + "_thumb_large.jpg", imgID + "_thumb_large.jpg", progress)
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
				a = cfg.gdalPath + "gdal_translate -of VRT -a_ullr " + str(UL1.x()) + " " + str(UL1.y()) + " " + str(LR1.x()) + " " + str(LR1.y()) + ' -a_srs "+proj=utm +zone=' + str(zone) + ' +datum=WGS84 +units=m +no_defs" ' + cfg.tmpDir + "//" + imgID + "_thumb_large.jpg " + cfg.tmpDir + "//" + imgID + ".vrt"
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
		tW = cfg.ui.landsat_images_tableWidget
		cfg.utls.removeRowsFromTable(tW)
		
	def updateImageDatabase(self):
		# ask for confirm
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Update image database"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want update image database (requires internet connection)?"))
		if a == "Yes":
			self.downloadImageDatabase()
			
	def downloadImageDatabase(self):
		cfg.uiUtls.addProgressBar()
		database = cfg.LandsatImageDatabase
		check = cfg.utls.downloadFile("http://landsat-pds.s3.amazonaws.com/scene_list.gz", cfg.tmpDir + "//" + "scene_list.gz", "scene_list.gz", 50)
		if check == "Yes":
			if os.path.isfile(cfg.tmpDir + "//" + "scene_list.gz"):
				shutil.copy(cfg.tmpDir + "//" + "scene_list.gz", database)		
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " database downloaded")
		else:
			cfg.mx.msgErr40()
					
	# download images in table
	def downloadImages(self):
		d = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Download the images in the table (requires internet connection)"))
		if len(d) > 0:
			self.downloadLandsatImages(d)
		
	# download Landsat 8 data using the service http://aws.amazon.com/public-data-sets/landsat/
	def downloadLandsatImages(self, outputDirectory):
		cfg.uiUtls.addProgressBar()
		tW = cfg.ui.landsat_images_tableWidget
		c = tW.rowCount()
		progressStep = 100 / c
		progressStep2 = progressStep/12
		progress = 0
		outDirList = []
		imgList = []
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				imgID = str(tW.item(i, 0).text())
				path = str(tW.item(i, 3).text())
				row = str(tW.item(i, 4).text())
				outDir = outputDirectory + "/" + imgID
				if not QDir(outDir).exists():
					os.makedirs(outDir)
				outDirList.append(outDir)
				urlL = "http://landsat-pds.s3.amazonaws.com/L8/" + path.zfill(3) + "/" + row.zfill(3) +"/" + imgID + "/" + imgID + "_"
				check = cfg.utls.downloadFile( urlL + "MTL.txt", outDir + "//" + imgID + "_MTL.txt", imgID + "_MTL.txt", progress)
				if check == "Yes":
					for i in range(1, 12):
						progress = progress + progressStep2
						if cfg.actionCheck == "Yes":
							t = "cfg.ui.checkBox_band_" + str(i) + ".isChecked()"
							checkBand = eval(t)
							if checkBand is True:
								cfg.utls.downloadFile( urlL + "B" + str(i) + ".TIF", outDir + "//" + imgID + "_B" + str(i) + ".TIF", imgID + "_B" + str(i) + ".TIF", progress)
								if os.path.isfile(outDir + "//" + imgID + "_B" + str(i) + ".TIF"):
									imgList.append(outDir + "//" + imgID + "_B" + str(i) + ".TIF")
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image downloaded " + imgID + "_B" + str(i))
						else:
							cfg.uiUtls.removeProgressBar()
							return "No"
					if cfg.actionCheck == "Yes":
						progress = progress + progressStep2
						if cfg.ui.checkBox_band_12.isChecked():
							cfg.utls.downloadFile( urlL + "BQA.TIF", outDir + "//" + imgID + "_BQA.TIF", imgID + "_BQA.TIF", progress)
							if os.path.isfile(outDir + "//" + imgID + "_BQA.TIF"):
									imgList.append(outDir + "//" + imgID + "_BQA.TIF")
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image downloaded " + imgID + "_BQA.TIF")
				else:
					cfg.mx.msgErr40()
					cfg.uiUtls.removeProgressBar()
					return "No"
			else:
				cfg.uiUtls.removeProgressBar()
				return "No"
		cfg.cnvs.setRenderFlag(False)
		if cfg.ui.preprocess_Landsat_checkBox.isChecked():
			for d in outDirList:
				if cfg.actionCheck == "Yes":
					cfg.landsatT.populateTable(d)
					o = d + "_converted"
					if not QDir(o).exists():
						os.makedirs(o)
					cfg.landsatT.landsat(d, o, "Yes")
		elif cfg.ui.load_in_QGIS_checkBox.isChecked():
			for d in imgList:
				r = cfg.utls.addRasterLayer(d, os.path.basename(d))
		cfg.uiUtls.removeProgressBar()
		cfg.cnvs.setRenderFlag(True)
		cfg.utls.finishSound()
			
	# read database
	def readDatabase(self, database = None):		
		if database == None:
			database = cfg.LandsatImageDatabase
		if os.path.isfile(database):
			pass
		else:
			self.downloadImageDatabase()
		if os.path.isfile(database):
			QdateFrom = cfg.ui.dateEdit_from.date()
			QdateTo = cfg.ui.dateEdit_to.date()
			dateFrom = QdateFrom.toPyDate()
			dateTo = QdateTo.toPyDate()
			maxCloudCover = float(cfg.ui.cloud_cover_spinBox.value())
			imgList = []
			if len(cfg.ui.imageID_lineEdit.text()) > 0:
				imgIDLine = cfg.ui.imageID_lineEdit.text()
				imgIDLineSplit = str(imgIDLine).replace(" ", "").split(";")
				if len(imgIDLineSplit) == 1:
					imgIDLineSplit = str(imgIDLine).replace(" ", "").split(",")
				for m in imgIDLineSplit:
					imgList.append(m.lower())
			else:
				try:
					rubbRect = QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
			try:
				cfg.uiUtls.addProgressBar()
				f = gzip.open(database, 'rb')
				file = f.readlines()
				sep = ","
				tW = cfg.ui.landsat_images_tableWidget
				cfg.utls.clearTable(tW)
				cfg.uiUtls.updateBar(30, QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
				qApp.processEvents()
				for b in range(1, len(file)):
					p = file[b].strip().split(sep)
					imgDateTime = datetime.datetime.strptime(p[1].split(" ")[0], "%Y-%m-%d")
					imgDate = imgDateTime.date()
					imgCloudCover = p[2]
					if (imgDate >= dateFrom and imgDate <= dateTo and float(imgCloudCover) <= maxCloudCover) or (len(cfg.ui.imageID_lineEdit.text()) > 0 ):
						min_lat,min_lon,max_lat,max_lon = p[6], p[7], p[8], p[9]	
						if (len(cfg.ui.imageID_lineEdit.text()) > 0 ):
							inter = 0	
						else:
							imgRect = QgsRectangle(float(min_lon), float(max_lat), float(max_lon), float(min_lat))
							inter = rubbRect.intersects(imgRect)
						if inter == 1 or p[0].lower() in imgList:
							tW.setSortingEnabled(False)
							# add item to table
							c = tW.rowCount()
							# add list items to table
							tW.setRowCount(c + 1)
							imgID = QTableWidgetItem(p[0])
							acqDate = QTableWidgetItem(p[1])
							cloudCover = QTableWidgetItem()
							cloudCover.setData(Qt.DisplayRole, float(imgCloudCover))
							path = QTableWidgetItem()
							path.setData(Qt.DisplayRole, int(p[4]))
							row = QTableWidgetItem()
							row.setData(Qt.DisplayRole, int(p[5]))
							MinLat = QTableWidgetItem()
							MinLat.setData(Qt.DisplayRole, float(min_lat))
							MinLon = QTableWidgetItem()
							MinLon.setData(Qt.DisplayRole, float(min_lon))
							MaxLat = QTableWidgetItem()
							MaxLat.setData(Qt.DisplayRole, float(max_lat))
							MaxLon = QTableWidgetItem()
							MaxLon.setData(Qt.DisplayRole, float(max_lon))
							tW.setItem(c, 0, imgID)
							tW.setItem(c, 1, acqDate)
							tW.setItem(c, 2, cloudCover)
							tW.setItem(c, 3, path)
							tW.setItem(c, 4, row)
							tW.setItem(c, 5, MinLat)
							tW.setItem(c, 6, MinLon)
							tW.setItem(c, 7, MaxLat)
							tW.setItem(c, 8, MaxLon)
							tW.setSortingEnabled(True)
				f.close()
				tW.setColumnWidth(0, 200)
				tW.setColumnWidth(1, 100)
				tW.setColumnWidth(2, 100)
				tW.setColumnWidth(3, 60)
				tW.setColumnWidth(4, 60)
				tW.setColumnWidth(5, 80)
				tW.setColumnWidth(6, 80)
				tW.setColumnWidth(7, 80)
				tW.setColumnWidth(8, 80)
				cfg.uiUtls.removeProgressBar()
				self.clearCanvasPoly()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Landsat images")
			except Exception, err:
				cfg.mx.msgErr39()
				cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				
	def checkAllBands(self):
		if self.checkAll == "Yes":
			for i in range(1, 13):
				t = "cfg.ui.checkBox_band_" + str(i) + ".setCheckState(2)"
				eval(t)
			self.checkAll = "No"
		else:
			for i in range(1, 13):
				t = "cfg.ui.checkBox_band_" + str(i) + ".setCheckState(0)"
				eval(t)
			self.checkAll = "Yes"
			