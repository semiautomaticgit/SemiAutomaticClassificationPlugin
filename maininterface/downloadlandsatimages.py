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
		cfg.ui.dateEdit_to.setDate(QDate.currentDate())
		
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
				jpg = str(tW.item(i, 10).text())
				if os.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
					pass
				else:
					self.downloadThumbnail(imgID, path, row, min_lat, min_lon, max_lat, max_lon, jpg, progress)
				if os.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
					r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID + ".vrt", imgID + ".vrt")
					cfg.utls.setRasterColorComposite(r, 1, 2, 3)
				progress = progress + progressStep
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.cnvs.refresh()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnails displayed")
		
	def downloadThumbnail(self, imgID, path, row, min_lat, min_lon, max_lat, max_lon, imageJPG, progress = None):
		check = cfg.utls.downloadFile(imageJPG, cfg.tmpDir + "//" + imgID + "_thumb.jpg", imgID + "_thumb.jpg", progress)
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
		tW = cfg.ui.landsat_images_tableWidget
		cfg.utls.removeRowsFromTable(tW)
		
	def updateImageDatabase(self):
		# ask for confirm
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Update image database"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to download the Landsat image database (requires internet connection)?"))
		if a == "Yes":
			cfg.uiUtls.addProgressBar()
			self.downloadImageDatabase("Yes")
			cfg.uiUtls.removeProgressBar()
			
	def downloadImageDatabase(self, force = "No", databaseForce = None):
		cfg.cnvs.setRenderFlag(False)
		# Landsat 8 Amazon
		database = cfg.LandsatImageDatabase
		check = cfg.utls.downloadFile("http://landsat-pds.s3.amazonaws.com/scene_list.gz", cfg.tmpDir + "//" + "scene_list.gz", "scene_list.gz", 50)
		if check == "Yes":
			if not QDir(cfg.LandsatDatabaseDirectory).exists():
				os.makedirs(cfg.LandsatDatabaseDirectory)
			if os.path.isfile(cfg.tmpDir + "//" + "scene_list.gz"):
				shutil.copy(cfg.tmpDir + "//" + "scene_list.gz", database)		
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " L8 Amazon database downloaded")
		else:
			cfg.mx.msgErr40()
		if cfg.ui.update_L8_checkBox.isChecked():
			cfg.cnvs.setRenderFlag(True)
			return "Yes"
		else:
			if cfg.ui.L7_checkBox.isChecked() and cfg.actionCheck != "No":
				# Landsat 7 SLC On
				database7On = cfg.Landsat7OnImageDatabase
				checkL7On = cfg.utls.downloadFile("http://landsat.usgs.gov/metadata_service/bulk_metadata_files/LANDSAT_ETM.csv.gz", cfg.tmpDir + "//" + "LANDSAT_ETM.csv.gz", "LANDSAT_ETM.csv.gz", 55)
				if checkL7On == "Yes":
					if os.path.isfile(cfg.tmpDir + "//" + "LANDSAT_ETM.csv.gz"):
						shutil.copy(cfg.tmpDir + "//" + "LANDSAT_ETM.csv.gz", database7On)		
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " L7 SLC On database downloaded")
				else:
					cfg.mx.msgErr40()
			if cfg.ui.L45_checkbox.isChecked() and cfg.actionCheck != "No":
				# Landsat 4-5 TM '80
				databaseLTM80 = cfg.LandsatTM80ImageDatabase
				checkLTM80 = cfg.utls.downloadFile("http://landsat.usgs.gov/metadata_service/bulk_metadata_files/LANDSAT_TM-1980-1989.csv.gz", cfg.tmpDir + "//" + "LANDSAT_TM-1980-1989.csv.gz", "LANDSAT_TM-1980-1989.csv.gz", 60)
				if checkLTM80 == "Yes":
					if os.path.isfile(cfg.tmpDir + "//" + "LANDSAT_TM-1980-1989.csv.gz"):
						shutil.copy(cfg.tmpDir + "//" + "LANDSAT_TM-1980-1989.csv.gz", databaseLTM80)		
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " LTM 80 database downloaded")
				else:
					cfg.mx.msgErr40()
				# Landsat 4-5 TM '90
				databaseLTM90 = cfg.LandsatTM90ImageDatabase
				checkLTM90 = cfg.utls.downloadFile("http://landsat.usgs.gov/metadata_service/bulk_metadata_files/LANDSAT_TM-1990-1999.csv.gz", cfg.tmpDir + "//" + "LANDSAT_TM-1990-1999.csv.gz", "LANDSAT_TM-1990-1999.csv.gz", 65)
				if checkLTM90 == "Yes":
					if os.path.isfile(cfg.tmpDir + "//" + "LANDSAT_TM-1990-1999.csv.gz"):
						shutil.copy(cfg.tmpDir + "//" + "LANDSAT_TM-1990-1999.csv.gz", databaseLTM90)		
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " LTM 90 database downloaded")
				else:
					cfg.mx.msgErr40()
				# Landsat 4-5 TM '00
				databaseLTM00 = cfg.LandsatTM00ImageDatabase
				checkLTM00 = cfg.utls.downloadFile("http://landsat.usgs.gov/metadata_service/bulk_metadata_files/LANDSAT_TM-2000-2009.csv.gz", cfg.tmpDir + "//" + "LANDSAT_TM-2000-2009.csv.gz", "LANDSAT_TM-2000-2009.csv.gz", 70)
				if checkLTM00 == "Yes":
					if os.path.isfile(cfg.tmpDir + "//" + "LANDSAT_TM-2000-2009.csv.gz"):
						shutil.copy(cfg.tmpDir + "//" + "LANDSAT_TM-2000-2009.csv.gz", databaseLTM00)		
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " LTM 00 database downloaded")
				else:
					cfg.mx.msgErr40()	
				# Landsat 4-5 TM '10
				databaseLTM10 = cfg.LandsatTM10ImageDatabase
				checkLTM10 = cfg.utls.downloadFile("http://landsat.usgs.gov/metadata_service/bulk_metadata_files/LANDSAT_TM-2010-2012.csv.gz", cfg.tmpDir + "//" + "LANDSAT_TM-2010-2012.csv.gz", "LANDSAT_TM-2010-2012.csv.gz", 75)
				if checkLTM10 == "Yes":
					if os.path.isfile(cfg.tmpDir + "//" + "LANDSAT_TM-2010-2012.csv.gz"):
						shutil.copy(cfg.tmpDir + "//" + "LANDSAT_TM-2010-2012.csv.gz", databaseLTM10)		
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " LTM 10 database downloaded")
				else:
					cfg.mx.msgErr40()
			if cfg.ui.L7_checkBox.isChecked() and cfg.actionCheck != "No":
				# Landsat 7 SLC Off
				database7Off = cfg.Landsat7OffImageDatabase
				checkL7Off = cfg.utls.downloadFile("http://landsat.usgs.gov/metadata_service/bulk_metadata_files/LANDSAT_ETM_SLC_OFF.csv.gz", cfg.tmpDir + "//" + "LANDSAT_ETM_SLC_OFF.csv.gz", "LANDSAT_ETM_SLC_OFF.csv.gz", 80)
				if checkL7Off == "Yes":
					if os.path.isfile(cfg.tmpDir + "//" + "LANDSAT_ETM_SLC_OFF.csv.gz"):
						shutil.copy(cfg.tmpDir + "//" + "LANDSAT_ETM_SLC_OFF.csv.gz", database7Off)		
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " L7 SLC Off database downloaded")
				else:
					cfg.mx.msgErr40()
			if cfg.ui.L8_checkBox.isChecked() and cfg.actionCheck != "No":
				# Landsat 8
				database8 = cfg.Landsat8ImageDatabase
				checkL8 = cfg.utls.downloadFile("http://landsat.usgs.gov/metadata_service/bulk_metadata_files/LANDSAT_8.csv.gz", cfg.tmpDir + "//" + "LANDSAT_8.csv.gz", "LANDSAT_8.csv.gz", 90)
				if checkL8 == "Yes":
					if os.path.isfile(cfg.tmpDir + "//" + "LANDSAT_8.csv.gz"):
						shutil.copy(cfg.tmpDir + "//" + "LANDSAT_8.csv.gz", database8)		
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " L8 database downloaded")
				else:
					cfg.mx.msgErr40()
			cfg.cnvs.setRenderFlag(True)
					
	# download images in table
	def downloadImages(self):
		d = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Download the images in the table (requires internet connection)"))
		if len(d) > 0:
			self.downloadLandsatImages(d)
		
	# download Landsat 8 data using the service http://aws.amazon.com/public-data-sets/landsat/
	def downloadLandsatImages(self, outputDirectory, exporter = "No"):
		cfg.uiUtls.addProgressBar()
		tW = cfg.ui.landsat_images_tableWidget
		c = tW.rowCount()
		progressStep = 100 / c
		progressStep2 = progressStep/12
		progress = 0
		outDirList = []
		imgList = []
		links = []
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				imgID = str(tW.item(i, 0).text())
				if cfg.ui.download_if_preview_in_legend_checkBox.isChecked() and cfg.utls.selectLayerbyName(imgID + ".vrt", "Yes") is None:
					pass
				else:
					path = str(tW.item(i, 3).text())
					row = str(tW.item(i, 4).text())
					service = str(tW.item(i, 9).text())
					outDir = outputDirectory + "/" + imgID
					if not QDir(outDir).exists():
						os.makedirs(outDir)
					outDirList.append(outDir)
					if service == "Amazon":
						urlL = "http://landsat-pds.s3.amazonaws.com/L8/" + path.zfill(3) + "/" + row.zfill(3) +"/" + imgID + "/" + imgID + "_"
						if exporter == "No":
							check = cfg.utls.downloadFile( urlL + "MTL.txt", outDir + "//" + imgID + "_MTL.txt", imgID + "_MTL.txt", progress)
						else:
							check = "Yes"
						if check == "Yes":
							for i in range(1, 12):
								progress = progress + progressStep2
								if cfg.actionCheck == "Yes":
									if exporter == "Yes":
										links.append(urlL + "B" + str(i) + ".TIF")
									else:
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
									if exporter == "Yes":
										links.append(urlL + "BQA.TIF")
									else:
										cfg.utls.downloadFile( urlL + "BQA.TIF", outDir + "//" + imgID + "_BQA.TIF", imgID + "_BQA.TIF", progress)
										if os.path.isfile(outDir + "//" + imgID + "_BQA.TIF"):
											imgList.append(outDir + "//" + imgID + "_BQA.TIF")
												# logger
											cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image downloaded " + imgID + "_BQA.TIF")
						else:
							cfg.mx.msgErr40()
							cfg.uiUtls.removeProgressBar()
							return "No"
					elif service == "Google":
						outUrl = self.downloadLandsatImagesFromGoogle(imgID, path, row, outDir, progress, exporter)
						links.append(outUrl)
						progress = progress + progressStep
			else:
				cfg.uiUtls.removeProgressBar()
				return "No"
		if exporter == "Yes":
			return links
		else:
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
				for d in outDirList:
					for f in os.listdir(d):
						if f.lower().endswith(".tif"):
							r = cfg.utls.addRasterLayer(d + "/" + f, f)
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.utls.finishSound()
			
	# download Landsat data using the service http://storage.googleapis.com/earthengine-public/landsat/
	def downloadLandsatImagesFromGoogle(self, imageID, path, row, outputDirectory, progress, exporter = "No"):
		baseUrl = "http://storage.googleapis.com/earthengine-public/landsat/"
		if imageID[2] == "8":
			sat = "L8"
		elif imageID[2] == "7":
			sat = "L7"
		elif imageID[2] == "5":
			sat = "L5"
		elif imageID[2] == "4":
			sat = "LT4"
		else:
			return "No"
		url = baseUrl + sat + "/" + path.zfill(3) + "/" + row.zfill(3) + "/" + imageID + ".tar.bz"
		if exporter == "Yes":
			return url
		else:
			try:
				check = cfg.utls.downloadFile( url, cfg.tmpDir + "//" + imageID + ".tar.bz", imageID + ".tar.bz", progress)
				if os.path.getsize(cfg.tmpDir + "//" + imageID + ".tar.bz") > 10000:
					tarFile = tarfile.open(cfg.tmpDir + "//" + imageID + ".tar.bz", 'r:bz2')
					for f in tarFile:
						if f.name.lower().endswith(".txt"):
							tarFile.extract(f, outputDirectory)
						elif f.name.lower().endswith(".tif"):
							tarFile.extract(f, outputDirectory)
					return url
				else:
					cfg.mx.msgErr42(imageID)
					return "No"
			except:
				return "No"
					
	def exportLinks(self):
		d = QFileDialog.getSaveFileName(None , QApplication.translate("semiautomaticclassificationplugin", "Export download links"), "", "*.txt")
		if len(d) > 0:
			links = self.downloadLandsatImages("No", "Yes")
			if links == "No":
				pass
			else:
				l = open(d, 'w')
				for t in links:
					l.write(t + "\n")
				l.close()
				cfg.uiUtls.removeProgressBar()
					
	# read database
	def readDatabase(self, database = None):
		if database == None:
			database = cfg.LandsatImageDatabase
		if not os.path.isfile(database):
			self.selectDatabaseDir()
			self.updateImageDatabase()
		if os.path.isfile(database):
			QdateFrom = cfg.ui.dateEdit_from.date()
			QdateTo = cfg.ui.dateEdit_to.date()
			dateFrom = QdateFrom.toPyDate()
			dateTo = QdateTo.toPyDate()
			maxCloudCover = float(cfg.ui.cloud_cover_spinBox.value())
			imageFindList = []
			if len(cfg.ui.imageID_lineEdit.text()) > 0:
				imgIDLine = cfg.ui.imageID_lineEdit.text()
				imgIDLineSplit = str(imgIDLine).replace(" ", "").split(";")
				if len(imgIDLineSplit) == 1:
					imgIDLineSplit = str(imgIDLine).replace(" ", "").split(",")
				for m in imgIDLineSplit:
					imageFindList.append(m.lower())
			else:
				try:
					rubbRect = QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
			try:
				cfg.uiUtls.addProgressBar()
				cfg.cnvs.setRenderFlag(False)
				f = gzip.open(database, 'rb')
				sep = ","
				tW = cfg.ui.landsat_images_tableWidget
				cfg.utls.clearTable(tW)
				cfg.uiUtls.updateBar(30, QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
				qApp.processEvents()
				imageTableList = []
				pathRowList = []
				tW.setSortingEnabled(False)
				# Amazon service
				b = 0
				for file in f:
					b = b +1
					if b > 1:
						p = file.strip().split(sep)
						imgDateTime = datetime.datetime.strptime(p[1].split(" ")[0], "%Y-%m-%d")
						imgDate = imgDateTime.date()
						imgCloudCover = p[2]
						min_lat,min_lon,max_lat,max_lon = p[6], p[7], p[8], p[9]	
						if (len(cfg.ui.imageID_lineEdit.text()) > 0 ):
							inter = 0	
						else:
							imgRect = QgsRectangle(float(min_lon), float(max_lat), float(max_lon), float(min_lat))
							inter = rubbRect.intersects(imgRect)
							if inter == 1 and p[0].lower() not in imageFindList:
								pathRowList.append(p[4].zfill(3) + "-" + p[5].zfill(3))
						if inter == 1 or p[0].lower() in imageFindList:
							if cfg.ui.L8_checkBox.isChecked():
								if (imgDate >= dateFrom and imgDate <= dateTo and float(imgCloudCover) <= maxCloudCover) or (len(cfg.ui.imageID_lineEdit.text()) > 0 ):
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
									service = QTableWidgetItem("Amazon")
									imgPreview = QTableWidgetItem("http://landsat-pds.s3.amazonaws.com/L8/" + p[4].zfill(3) + "/" + p[5].zfill(3) +"/" + p[0] + "/" + p[0] + "_thumb_large.jpg")
									tW.setItem(c, 0, imgID)
									tW.setItem(c, 1, acqDate)
									tW.setItem(c, 2, cloudCover)
									tW.setItem(c, 3, path)
									tW.setItem(c, 4, row)
									tW.setItem(c, 5, MinLat)
									tW.setItem(c, 6, MinLon)
									tW.setItem(c, 7, MaxLat)
									tW.setItem(c, 8, MaxLon)
									tW.setItem(c, 9, service)
									tW.setItem(c, 10, imgPreview)
									imageTableList.append(p[0])
				f.close()
				pathRowListUnique = list(set(pathRowList))
				# Landsat 8
				if cfg.ui.L8_checkBox.isChecked():
					L8Dtmin = datetime.datetime.strptime("2013-04-11", "%Y-%m-%d").date()
					if L8Dtmin <= dateTo :
						imageTableListL8 = self.readLandsatDatabase(imageFindList, imageTableList, pathRowListUnique, dateFrom, dateTo, maxCloudCover, "Landsat 8", cfg.Landsat8ImageDatabase)
				# Landsat 4-5
				if cfg.ui.L45_checkbox.isChecked():
					LTMDtmin = datetime.datetime.strptime("1980-01-01", "%Y-%m-%d").date()
					LTMDt80 = datetime.datetime.strptime("1989-12-31", "%Y-%m-%d").date()
					LTMDt90 = datetime.datetime.strptime("1999-12-31", "%Y-%m-%d").date()
					LTMDt00 = datetime.datetime.strptime("2009-12-31", "%Y-%m-%d").date()
					LTMDt10 = datetime.datetime.strptime("2012-12-31", "%Y-%m-%d").date()
					if dateFrom <= LTMDt80 and LTMDtmin <= dateTo:
						imageTableListLTM80 = self.readLandsatDatabase(imageFindList, imageTableList, pathRowListUnique, dateFrom, dateTo, maxCloudCover, "Landsat TM", cfg.LandsatTM80ImageDatabase)
					if dateFrom <= LTMDt90 and LTMDt80 <= dateTo:
						imageTableListLTM90 = self.readLandsatDatabase(imageFindList, imageTableList, pathRowListUnique, dateFrom, dateTo, maxCloudCover, "Landsat TM", cfg.LandsatTM90ImageDatabase)
					if dateFrom <= LTMDt00 and LTMDt90 <= dateTo:
						imageTableListLTM00 = self.readLandsatDatabase(imageFindList, imageTableList, pathRowListUnique, dateFrom, dateTo, maxCloudCover, "Landsat TM", cfg.LandsatTM00ImageDatabase)
					if dateFrom <= LTMDt10 and LTMDt00 <= dateTo:
						imageTableListLTM10 = self.readLandsatDatabase(imageFindList, imageTableList, pathRowListUnique, dateFrom, dateTo, maxCloudCover, "Landsat TM", cfg.LandsatTM10ImageDatabase)
				# Landsat 7
				if cfg.ui.L7_checkBox.isChecked():
					L7Dtmin = datetime.datetime.strptime("1999-07-01", "%Y-%m-%d").date()
					L7Dt03 = datetime.datetime.strptime("2003-05-30", "%Y-%m-%d").date()
					if dateFrom <= L7Dt03 and L7Dtmin <= dateTo :
						imageTableListLETMOn = self.readLandsatDatabase(imageFindList, imageTableList, pathRowListUnique, dateFrom, dateTo, maxCloudCover, "Landsat 7 ETM+", cfg.Landsat7OnImageDatabase)
					if L7Dt03 <= dateTo:
						imageTableListLETMOff = self.readLandsatDatabase(imageFindList, imageTableList, pathRowListUnique, dateFrom, dateTo, maxCloudCover, "Landsat 7 ETM+", cfg.Landsat7OffImageDatabase)
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
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Landsat images")
			except Exception, err:
				cfg.mx.msgErr39()
				cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					
	def readLandsatDatabase(self, imageFindList = None, imageTableList = None, pathRowList = None, dateFrom = None, dateTo = None, maxCloudCover = None, satellites = None, database = None):
		if os.path.isfile(database):
			try:
				f = gzip.open(database, 'rb')
				sep = ","
				tW = cfg.ui.landsat_images_tableWidget
				cfg.uiUtls.updateBar(50, QApplication.translate("semiautomaticclassificationplugin", "Searching " + str(satellites) + " ..."))
				qApp.processEvents()
				imageTableList8 = []
				b = 0
				for file in f:
					b = b +1
					if b > 1:
						check = "No"
						p = file.strip().split(sep)
						pathRow = str(p[6].zfill(3) + "-" + p[7].zfill(3))
						if pathRow in pathRowList:
							imgDateTime = datetime.datetime.strptime(p[2], "%Y-%m-%d")
							imgDate = imgDateTime.date()
							if (imgDate >= dateFrom and imgDate <= dateTo and float(p[19]) <= maxCloudCover):
								check = "Yes"
						if (p[0].lower() in imageFindList):
							check = "Yes"
						if check == "Yes" and p[0] not in imageTableList:
							# upperLeftCornerLatitude, upperRightCornerLatitude, lowerLeftCornerLatitude, lowerRightCornerLatitude 
							lat = [float(p[8]), float(p[10]), float(p[12]), float(p[14])]
							#upperLeftCornerLongitude, upperRightCornerLongitude, lowerLeftCornerLongitude, lowerRightCornerLongitude
							lon = [float(p[9]), float(p[11]), float(p[13]), float(p[15])]
							min_lon = min(lon)
							max_lon = max(lon)
							min_lat = min(lat)
							max_lat = max(lat)
							# add item to table
							c = tW.rowCount()
							# add list items to table
							tW.setRowCount(c + 1)
							imgID = QTableWidgetItem(p[0])
							acqDate = QTableWidgetItem(p[2])
							cloudCover = QTableWidgetItem()
							cloudCover.setData(Qt.DisplayRole, float(p[19]))
							path = QTableWidgetItem()
							path.setData(Qt.DisplayRole, int(p[6]))
							row = QTableWidgetItem()
							row.setData(Qt.DisplayRole, int(p[7]))
							MinLat = QTableWidgetItem()
							MinLat.setData(Qt.DisplayRole, min_lat)
							MinLon = QTableWidgetItem()
							MinLon.setData(Qt.DisplayRole, min_lon)
							MaxLat = QTableWidgetItem()
							MaxLat.setData(Qt.DisplayRole, max_lat)
							MaxLon = QTableWidgetItem()
							MaxLon.setData(Qt.DisplayRole, max_lon)
							service = QTableWidgetItem("Google")
							imgPreview = QTableWidgetItem(p[5])
							tW.setItem(c, 0, imgID)
							tW.setItem(c, 1, acqDate)
							tW.setItem(c, 2, cloudCover)
							tW.setItem(c, 3, path)
							tW.setItem(c, 4, row)
							tW.setItem(c, 5, MinLat)
							tW.setItem(c, 6, MinLon)
							tW.setItem(c, 7, MaxLat)
							tW.setItem(c, 8, MaxLon)
							tW.setItem(c, 9, service)
							tW.setItem(c, 10, imgPreview)
							imageTableList8.append(p[0])
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), str(imageTableList8))
				return imageTableList8	
			except Exception, err:
				cfg.mx.msgErr39()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(inspect.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
				
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
			
	# reset DatabaseDir
	def resetDatabaseDir(self):
		# ask for confirm
		a = cfg.utls.questionBox(QApplication.translate("semiautomaticclassificationplugin", "Landsat database directory"), QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to reset Landsat database directory?"))
		if a == "Yes":
			self.setDatabaseDir()
		
	def selectDatabaseDir(self):
		d = QFileDialog.getExistingDirectory(None , QApplication.translate("semiautomaticclassificationplugin", "Select Landsat database directory"))
		if len(d) > 0:
			self.setDatabaseDir(d)
		
	# set database directory
	def setDatabaseDir(self, directory = None):
		if directory is None:
			cfg.LandsatImageDatabase = cfg.plgnDir + "/maininterface/" + "scene_list.gz"	
			cfg.Landsat7OnImageDatabase = cfg.plgnDir + "/maininterface/" + "LANDSAT_ETM.csv.gz"	
			cfg.Landsat7OffImageDatabase = cfg.plgnDir + "/maininterface/" + "LANDSAT_ETM_SLC_OFF.csv.gz"	
			cfg.LandsatTM80ImageDatabase = cfg.plgnDir + "/maininterface/" + "LANDSAT_TM-1980-1989.csv.gz"	
			cfg.LandsatTM90ImageDatabase = cfg.plgnDir + "/maininterface/" + "LANDSAT_TM-1990-1999.csv.gz"	
			cfg.LandsatTM00ImageDatabase = cfg.plgnDir + "/maininterface/" + "LANDSAT_TM-2000-2009.csv.gz"	
			cfg.LandsatTM10ImageDatabase = cfg.plgnDir + "/maininterface/" + "LANDSAT_TM-2010-2012.csv.gz"	
			cfg.Landsat8ImageDatabase = cfg.plgnDir + "/maininterface/" + "LANDSAT_8.csv.gz"	
			cfg.LandsatTMImageDatabase2010 = cfg.plgnDir + "/maininterface/" + "LANDSAT_TM-2010-2012.csv.gz"
			cfg.ui.database_lineEdit.setText(cfg.plgnDir + "/maininterface/")
		else:
			cfg.LandsatImageDatabase = directory + "/" + "scene_list.gz"	
			cfg.Landsat7OnImageDatabase = directory + "/" + "LANDSAT_ETM.csv.gz"	
			cfg.Landsat7OffImageDatabase = directory + "/" + "LANDSAT_ETM_SLC_OFF.csv.gz"	
			cfg.LandsatTM80ImageDatabase = directory + "/" + "LANDSAT_TM-1980-1989.csv.gz"	
			cfg.LandsatTM90ImageDatabase = directory + "/" + "LANDSAT_TM-1990-1999.csv.gz"	
			cfg.LandsatTM00ImageDatabase = directory + "/" + "LANDSAT_TM-2000-2009.csv.gz"	
			cfg.LandsatTM10ImageDatabase = directory + "/" + "LANDSAT_TM-2010-2012.csv.gz"	
			cfg.Landsat8ImageDatabase = directory + "/" + "LANDSAT_8.csv.gz"	
			cfg.LandsatTMImageDatabase2010 = directory + "/" + "LANDSAT_TM-2010-2012.csv.gz"
			cfg.ui.database_lineEdit.setText(directory)
		cfg.LandsatDatabaseDirectory = cfg.ui.database_lineEdit.text()
		cfg.sets.setQGISRegSetting(cfg.regLandsatDBDir, cfg.LandsatDatabaseDirectory)
			
""" deprecated	
	# read database from http://storage.googleapis.com/earthengine-public/landsat/ 
	def readGoogleDatabase(self, imageFindList = None, imageTableList = None, pathRowList = None, dateFrom = None, dateTo = None, maxCloudCover = None, satellites = None, database = None):		
		if database == None:
			database = cfg.LandsatImageDatabaseGoogle
		if os.path.isfile(database):
			pass
		else:
			self.downloadImageDatabase()
		sep = "/"
		imageOutList = []
		imageMetadataList = []
		with zipfile.ZipFile(database) as f:
			with f.open('scene_list') as fL:
				for b in fL:
					p = b.strip().split(sep)
					sat = p[4]
					path = str(p[5].zfill(3))
					row = str(p[6].zfill(3))
					pathRow = path + "-" + row
					imageNm = p[7].split(".")[0]
					if (pathRow in pathRowList and not imageNm in imageTableList) or (imageNm in imageFindList and not imageNm in imageTableList):
						imageMetadataList.append([imageNm, path, row])
		for i in imageMetadataList:
			metadata = self.downloadUSGSMetadata(i[0])
			if metadata != "No":
				dateX, cloudCover, preview, ULX, ULY, LRX, LRY = self.openMetadataXML(metadata)
				imgDateTime = datetime.datetime.strptime(dateX, "%Y/%m/%d")
				imgDate = imgDateTime.date()
				if (imgDate >= dateFrom and imgDate <= dateTo and float(cloudCover) <= maxCloudCover):
						imageOutList.append([i[0], dateX, cloudCover, i[1], i[2], LRY, ULX, ULY, LRX])		
		return imageOutList
		
	# open USGS metadata xml
	def openMetadataXML(self, metadataFile):
		import xml.etree.cElementTree as ET
		from xml.dom import minidom
		date = None
		cloudCover = None
		preview = None
		ULX = None
		NWX = None
		ULY = None
		NWY = None
		LRX = None
		SEX = None
		LRY = None
		SEY = None
		tree = ET.parse(metadataFile)
		root = tree.getroot()
		for child in root[0]:
			a = child.get("name")
			if a == "Date Acquired":
				date = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip()
			if a == "Cloud Cover" or a == "Scene Cloud Cover":
				cloudCover = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip()
			# for preview
			if a == "Corner UL Longitude Product":
				ULX = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip().split(" ")[0]
			if a == "NW Corner Long dec":
				NWX = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip()	
			if a == "Corner UL Latitude Product":
				ULY = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip().split(" ")[0]
			if a == "NW Corner Lat dec":
				NWY = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip()
			if a == "Corner LR Longitude Product":
				LRX = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip().split(" ")[0]
			if a == "SE Corner Long dec":
				SEX = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip()
			if a == "Corner LR Latitude Product":
				LRY = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip().split(" ")[0]
			if a == "SE Corner Lat dec":
				SEY = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}metadataValue').text).strip()	
		if ULX is None:
			ULX = NWX
		if ULY is None:
			ULY = NWY
		if LRX is None:
			LRX = SEX
		if LRY is None:
			LRY = SEY
		for child in root[1]:		
			a = child.get("id")
			if a == "BROWSE_REFL_WMS_PATH" or a == "BROWSE_REFL_PATH":
				preview = str(child.find('{http://earthexplorer.usgs.gov/eemetadata.xsd}browseLink').text).strip()
		return date, cloudCover, preview, ULX, ULY, LRX, LRY
		
	# download image metadata from http://earthexplorer.usgs.gov
	def downloadUSGSMetadata(self, imageID):
		sat = imageID[0:3]
		url = None
		if sat == "LC8":
			# L8
			url = "http://earthexplorer.usgs.gov/metadata/xml/4923/" + imageID
		elif sat == "LE7":
			# L7 (1 June 2003 -present)
			url1 = "http://earthexplorer.usgs.gov/metadata/xml/3373/" + imageID
			# L7 (1999-  May 31, 2003 )
			url2 = "http://earthexplorer.usgs.gov/metadata/xml/3372/" + imageID
		elif sat == "LT5" or sat == "LT4":
			# L4-5
			url = "http://earthexplorer.usgs.gov/metadata/xml/3119/" + imageID
		if url is not None:
			check = cfg.utls.downloadFile(url, cfg.tmpDir  + "//" + imageID + "_MTL.xml", imageID + "_MTL.xml", 50)
			if check == "Yes":
				metadata = cfg.tmpDir  + "//" + imageID + "_MTL.xml"
		else:
			try:
				check2 = cfg.utls.downloadFile(url2, cfg.tmpDir  + "//" + imageID + "_MTL.xml", imageID + "_MTL.xml", 50)
				if check == "Yes":
					metadata = cfg.tmpDir  + "//" + imageID + "_MTL.xml"
				else:
					metadata = "No"
			except:
				metadata = "No"
		return metadata
"""


			