# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2016 by Luca Congedo
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

from qgis.core import *
from qgis.gui import *
import SemiAutomaticClassificationPlugin.core.config as cfg

class DownloadLandsatImages:

	def __init__(self):
		# check all bands
		self.checkAll = "No"
		self.rbbrBndPol = QgsRubberBand(cfg.cnvs, 2)
		cfg.ui.dateEdit_to.setDate(cfg.QDateSCP.currentDate())
		
	# add satellite list to combo
	def addSatelliteToCombo(self, satelliteList):
		for i in satelliteList:
			cfg.ui.landsat_satellite_combo.addItem(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " satellites added")
			
	# user
	def rememberUser(self):
		if cfg.ui.remember_user_checkBox_2.isChecked():
			user = cfg.ui.user_usgs_lineEdit.text()
			pswd = cfg.utls.encryptPassword(cfg.ui.password_usgs_lineEdit.text())
			cfg.sets.setQGISRegSetting(cfg.regUSGSUser, user)
			cfg.sets.setQGISRegSetting(cfg.regUSGSPass, pswd)
			
	def rememberUserCheckbox(self):
		if cfg.ui.remember_user_checkBox_2.isChecked():
			self.rememberUser()
		else:
			cfg.sets.setQGISRegSetting(cfg.regUSGSUser, "")
			cfg.sets.setQGISRegSetting(cfg.regUSGSPass, "")
		
	# add rubber band
	def addRubberBandPolygon(self, pointUL, pointLR):
		try:
			self.clearCanvasPoly()
		except:
			pass
		rectangle = [[pointUL, QgsPoint(pointLR.x(), pointUL.y()), pointLR, QgsPoint(pointUL.x(), pointLR.y())]]
		self.rbbrBndPol.setToGeometry(QgsGeometry.fromPolygon(rectangle), None)
		clr = cfg.QtGuiSCP.QColor(cfg.ROIClrVal)
		clr.setAlpha(50)
		try:
			# QGIS 2.6
			self.rbbrBndPol.setFillColor(clr)
			#self.rbbrBndPol.setBorderColor(cfg.QtGuiSCP.QColor(cfg.ROIClrOutlineValDefault))
			#self.rbbrBndPol.setLineStyle(cfg.QtSCP.DotLine)
			self.rbbrBndPol.setWidth(3)
		except:
			# QGIS < 2.6
			self.rbbrBndPol.setColor(clr)
			#self.rbbrBndPol.setLineStyle(cfg.QtSCP.DotLine)
			self.rbbrBndPol.setWidth(3)
		
	# clear canvas
	def clearCanvasPoly(self):
		self.rbbrBndPol.reset(True)
		cfg.cnvs.refresh()

	# Activate pointer
	def pointerActive(self):
		# connect to click
		t = cfg.dwnlLandsatP
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(":/pointer/icons/pointer/ROI_pointer.png")
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: Landsat")
		

	# left click pointer
	def pointerLeftClick(self, point):
		self.pointerClickUL(point)
			
	# right click pointer
	def pointerRightClick(self, point):
		self.pointerClickLR(point)
			
	# show area
	def showArea(self):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = QgsCoordinateReferenceSystem()
		iCrs.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
		try:
			UL = QgsPoint(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()))
			UL1 = cfg.utls.projectPointCoordinates(UL, iCrs, pCrs)
			LR = QgsPoint(float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
			LR1 = cfg.utls.projectPointCoordinates(LR, iCrs, pCrs)
			self.addRubberBandPolygon(UL1, LR1)
		except:
			pass
			
	# set coordinates
	def pointerClickLR(self, point):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = QgsCoordinateReferenceSystem()
		iCrs.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
		point1 = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
		cfg.ui.LX_lineEdit_3.setText(str(point1.x()))
		cfg.ui.LY_lineEdit_3.setText(str(point1.y()))
		self.showArea()
		
	# set coordinates
	def pointerClickUL(self, point):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = QgsCoordinateReferenceSystem()
		iCrs.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
		point1 = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
		cfg.ui.UX_lineEdit_3.setText(str(point1.x()))
		cfg.ui.UY_lineEdit_3.setText(str(point1.y()))
		self.showArea()
		
	# find images
	def findImages(self):
		self.downloadMetadata()
				
	# download image metadata from NASA CMR Search https://cmr.earthdata.nasa.gov/search/site/search_api_docs.html
	def downloadMetadata(self):
		listImgID = []
		QdateFrom = cfg.ui.dateEdit_from.date()
		QdateTo = cfg.ui.dateEdit_to.date()
		dateFrom = QdateFrom.toPyDate().strftime("%Y-%m-%d") 
		dateTo = QdateTo.toPyDate().strftime("%Y-%m-%d") 
		maxCloudCover = int(cfg.ui.cloud_cover_spinBox.value())
		sat = cfg.ui.landsat_satellite_combo.currentText()
		if sat == cfg.usgsLandsat8:
			NASAcollection = cfg.NASALandsat8Collection
			USGScollection = cfg.usgsLandsat8Collection
		elif sat == cfg.usgsLandsat7:
			NASAcollection = cfg.NASALandsat7Collection
		elif sat == cfg.usgsLandsat45:
			NASAcollection = cfg.NASALandsat45Collection
			USGScollection = cfg.usgsLandsat45Collection
		elif sat == cfg.usgsLandsat15:
			NASAcollection = cfg.NASALandsat15Collection
			USGScollection = cfg.usgsLandsat15Collection
		imageFindList = []
		if len(cfg.ui.imageID_lineEdit.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit.text()
			imgIDLineSplit = str(imgIDLine).replace(" ", "").split(";")
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(" ", "").split(",")
			for m in imgIDLineSplit:
				imageFindList.append(m.lower())
		try:
			rubbRect = QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg23()
			return "No"
		try:
			cfg.uiUtls.addProgressBar()
			cfg.QtGuiSCP.qApp.processEvents()
			cfg.cnvs.setRenderFlag(False)
			tW = cfg.ui.landsat_images_tableWidget
			tW.setSortingEnabled(False)
			cfg.uiUtls.updateBar(30, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
			# cloud cover returns 0 results
			# without cloud cover
			searchUrl = 'https://cmr.earthdata.nasa.gov/search/granules.echo10?bounding_box=' + cfg.ui.UX_lineEdit_3.text() + '%2C' + cfg.ui.LY_lineEdit_3.text() + '%2C' + cfg.ui.LX_lineEdit_3.text() + '%2C' + cfg.ui.UY_lineEdit_3.text() + '&echo_collection_id=' + NASAcollection + '&temporal=' + dateFrom + '%2C' + dateTo + 'T23%3A59%3A59.000Z&sort_key%5B%5D=-start_date&page_size=100&pretty=true'
			# connect and search
			searchResult = cfg.utls.NASASearch(searchUrl)
			xmlFile = searchResult.read()
			imgIDList = []
			doc = cfg.minidomSCP.parseString(xmlFile)
			entries = doc.getElementsByTagName("Granule")
			pages = len(entries)
			page = 0
			for entry in entries:
				page = page + 1
				cfg.uiUtls.updateBar(30 + int(page * 70 / pages), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
				gId = entry.getElementsByTagName("GranuleUR")[0]
				imgID = gId.firstChild.data
				if imgID not in imgIDList:
					imgIDList.append(imgID)
					imgDispID = imgID
					cc = entry.getElementsByTagName("QAPercentCloudCover")[0]
					cloudCover = cc.firstChild.data
					StartCoordinate1 = entry.getElementsByTagName("StartCoordinate1")[0]
					path = StartCoordinate1.firstChild.data
					StartCoordinate2 = entry.getElementsByTagName("StartCoordinate2")[0]
					row = StartCoordinate2.firstChild.data
					on = entry.getElementsByTagName("ProviderBrowseUrl")
					url = on[0].getElementsByTagName("URL")[0]
					imgPreview = url.firstChild.data
					dt = entry.getElementsByTagName("BeginningDateTime")[0]
					imgDate = dt.firstChild.data
					imgDate = cfg.datetimeSCP.datetime.strptime(imgDate[0:19], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
					PointLatitude = entry.getElementsByTagName("PointLatitude")
					lat = []
					for latit in PointLatitude:
						lat.append(float(latit.firstChild.data))
					PointLongitude = entry.getElementsByTagName("PointLongitude")
					lon = []
					for longi in PointLongitude:
						lon.append(float(longi.firstChild.data))
					listImgID.append([imgID, imgDate, cloudCover, path, row, lon, lat, imgPreview])
			c = tW.rowCount()
			for imID in listImgID:
				if len(imageFindList) > 0:
					for iF in imageFindList:
						if iF in imID[0].lower():
							imgCheck = "Yes"
							break
						else:
							imgCheck = "No"
				# workaround for cloud cover filter
				elif maxCloudCover < float(imID[2]):
					imgCheck = "No"
				else:
					imgCheck = "Yes"
				if imgCheck == "Yes":
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, imID[0], c, 0)
					cfg.utls.addTableItem(tW, str(imID[1]), c, 1)
					if sat == cfg.usgsLandsat7:
						if cfg.datetimeSCP.datetime.strptime(imID[1][0:19], '%Y-%m-%d %H:%M:%S') < cfg.datetimeSCP.datetime.strptime('2003-05-30 00:00:00', '%Y-%m-%d %H:%M:%S'):
							USGScollection = cfg.usgsLandsat7slconCollection
						else:
							USGScollection = cfg.usgsLandsat7slcoffCollection
					cfg.utls.addTableItem(tW, int(round(float(imID[2]))), c, 2)
					cfg.utls.addTableItem(tW, imID[3], c, 3)
					cfg.utls.addTableItem(tW, imID[4], c, 4)
					min_lon = min(imID[5])
					max_lon = max(imID[5])
					min_lat = min(imID[6])
					max_lat = max(imID[6])
					cfg.utls.addTableItem(tW, float(min_lat), c, 5)
					cfg.utls.addTableItem(tW, float(min_lon), c, 6)
					cfg.utls.addTableItem(tW, float(max_lat), c, 7)
					cfg.utls.addTableItem(tW,float(max_lon), c, 8)
					cfg.utls.addTableItem(tW, USGScollection, c, 9)
					cfg.utls.addTableItem(tW, imID[7], c, 10)
					cfg.utls.addTableItem(tW, NASAcollection, c, 11)
			tW.setSortingEnabled(True)
			cfg.cnvs.setRenderFlag(True)				
			cfg.uiUtls.removeProgressBar()
			self.clearCanvasPoly()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Landsat images")
			c = tW.rowCount()
			if c == 0:
				cfg.mx.msg21()
		except Exception, err:
			cfg.mx.msgErr39()
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
	
	# display images
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
				if cfg.osSCP.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
					l = cfg.utls.selectLayerbyName(imgID + ".vrt")
					if l is not None:		
						cfg.lgnd.setLayerVisible(l, True)
						cfg.utls.moveLayerTop(l)
					else:
						r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID + ".vrt", imgID + ".vrt")
						cfg.utls.setRasterColorComposite(r, 1, 2, 3)
				else:
					self.downloadThumbnail(imgID, path, row, min_lat, min_lon, max_lat, max_lon, jpg, progress)
					if cfg.osSCP.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
						r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID + ".vrt", imgID + ".vrt")
						cfg.utls.setRasterColorComposite(r, 1, 2, 3)
				progress = progress + progressStep
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.cnvs.refresh()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnails displayed")
		
	# download thumbnail
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
					sP = cfg.subprocessSCP.Popen(a, shell=True, stdout=cfg.subprocessSCP.PIPE, stderr=cfg.subprocessSCP.PIPE)
					sP.wait()
					# get error
					out, err = sP.communicate()
					sP.stdout.close()
					if len(err) > 0:
						cfg.mx.msgBarError(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Error"), err)
						st = "Yes"
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error:: " + str(err) )
				# in case of errors
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					sP = cfg.subprocessSCP.Popen(a, shell=True)
					sP.wait()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnail downloaded" + str(imgID))
			else:
				cfg.mx.msgErr41()
		else:
			cfg.mx.msgErr40()
	
	# remove highlighted images from table
	def removeImageFromTable(self):
		tW = cfg.ui.landsat_images_tableWidget
		cfg.utls.removeRowsFromTable(tW)
					
	# download images in table
	def downloadImages(self):
		tW = cfg.ui.landsat_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = cfg.utls.getExistingDirectory(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Download the images in the table (requires internet connection)"))
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
					USGScollection = str(tW.item(i, 9).text())
					NASAcollection = str(tW.item(i, 11).text())
					outDir = outputDirectory + "/" + imgID
					if exporter == "No":
						if not cfg.QDirSCP(outDir).exists():
							try:
								cfg.osSCP.makedirs(outDir)
							# in case of errors
							except Exception, err:
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					outDirList.append(outDir)
					if NASAcollection == cfg.NASALandsat8Collection:
						urlL = "http://landsat-pds.s3.amazonaws.com/L8/" + path.zfill(3) + "/" + row.zfill(3) +"/" + imgID + "/" + imgID + "_"
						check = cfg.utls.downloadFile( urlL + "MTL.txt", outDir + "//" + imgID + "_MTL.txt", imgID + "_MTL.txt", progress)
						if check == "Yes":
							meta = open(outDir + "//" + imgID + "_MTL.txt", 'r').read()
							if "NoSuchKey" in meta:
								check = "No"
						if check == "Yes":
							links.append(urlL + "MTL.txt")
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
											if cfg.osSCP.path.isfile(outDir + "//" + imgID + "_B" + str(i) + ".TIF"):
												imgList.append(outDir + "//" + imgID + "_B" + str(i) + ".TIF")
												# logger
												cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image downloaded " + imgID + "_B" + str(i))
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
										if cfg.osSCP.path.isfile(outDir + "//" + imgID + "_BQA.TIF"):
											imgList.append(outDir + "//" + imgID + "_BQA.TIF")
												# logger
											cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image downloaded " + imgID + "_BQA.TIF")
						else:
							outUrl = self.downloadLandsatImagesFromGoogle(imgID, path, row, outDir, progress, exporter)
							if outUrl == 'Cancel action':
								pass
							elif outUrl == "No":
								outUrl = self.downloadLandsatImagesFromUSGS(imgID, USGScollection, row, outDir, progress, exporter)
							links.append(outUrl)
							progress = progress + progressStep
					else:
						progress = progress + progressStep
						outUrl = self.downloadLandsatImagesFromGoogle(imgID, path, row, outDir, progress, exporter)
						if outUrl == 'Cancel action':
							pass
						elif outUrl == "No":
							outUrl = self.downloadLandsatImagesFromUSGS(imgID, USGScollection, row, outDir, progress, exporter)
						links.append(outUrl)
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
						cfg.landsatT.populateTable(d, "Yes")
						o = d + "_converted"
						if not cfg.QDirSCP(o).exists():
							cfg.osSCP.makedirs(o)
						cfg.landsatT.landsat(d, o, "Yes")
			elif cfg.ui.load_in_QGIS_checkBox.isChecked():
				for d in outDirList:
					try:
						for f in cfg.osSCP.listdir(d):
							if f.lower().endswith(".tif"):
								r = cfg.utls.addRasterLayer(d + "/" + f, f)
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.utls.finishSound()
			
	# download image preview
	def downloadLandsatImagesFromUSGS(self, imageID, collection, row, outputDirectory, progress, exporter = "No"):
		url = "http://earthexplorer.usgs.gov/download/" + collection + "/" + imageID + "/STANDARD/EE"
		if exporter == "Yes":
			return url
		else:
			user = cfg.ui.user_usgs_lineEdit.text()
			password =cfg.ui.password_usgs_lineEdit.text()
			try:
				imgID = imageID + ".tar.gz"
				check = cfg.utls.downloadFileUSGS(user, password, 'https://ers.cr.usgs.gov/login', url, cfg.tmpDir + "//" + imgID, imgID, progress, "Yes")
				if str(check) == 'Cancel action':
					return check
				if cfg.osSCP.path.getsize(cfg.tmpDir + "//" + imgID) > 10000:
					tarFiles = cfg.tarfileSCP.open(cfg.tmpDir + "//" + imgID, 'r:gz')
					tarFiles.extractall(outputDirectory)
					tarFiles.close()
					cfg.osSCP.remove(cfg.tmpDir + "//" + imgID)
					return url
				else:
					cfg.mx.msgErr55(imgID)
					return "No"
			except Exception, err:
				cfg.mx.msgErr50(str(err))
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			
	# download Landsat data using the service http://storage.googleapis.com/earthengine-public/landsat/
	def downloadLandsatImagesFromGoogle(self, imageID, path, row, outputDirectory, progress, exporter = "No"):
		baseUrl = "http://storage.googleapis.com/earthengine-public/landsat/"
		if imageID[0:3] == "LC8":
			sat = "L8"
		elif imageID[0:3] == "LE7":
			sat = "L7"
		elif imageID[0:3] == "LT5":
			sat = "L5"
		elif imageID[0:3] == "LT4":
			sat = "LT4"
		else:
			return "No"
		url = baseUrl + sat + "/" + path.zfill(3) + "/" + row.zfill(3) + "/" + imageID + ".tar.bz"
		if exporter == "Yes":
			return url
		else:
			try:
				check = cfg.utls.downloadFile( url, cfg.tmpDir + "//" + imageID + ".tar.bz", imageID + ".tar.bz", progress)
				if str(check) == 'Cancel action':
					return check
				if cfg.osSCP.path.getsize(cfg.tmpDir + "//" + imageID + ".tar.bz") > 10000:
					tarFiles = cfg.tarfileSCP.open(cfg.tmpDir + "//" + imageID + ".tar.bz", 'r:bz2')
					tarFiles.extractall(outputDirectory)
					tarFiles.close()
					cfg.osSCP.remove(cfg.tmpDir + "//" + imageID + ".tar.bz")
					return url
				else:
					cfg.mx.msgErr42(imageID)
					return "No"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
					
	# export links
	def exportLinks(self):
		tW = cfg.ui.landsat_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Export download links"), "", "*.txt")
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
				
	# check all bands
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
			
	# clear table
	def clearTable(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset signature list"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the table?"))
		if a == "Yes":
			tW = cfg.ui.landsat_images_tableWidget
			cfg.utls.clearTable(tW)
			
	# show hide area radio button
	def showHideArea(self):
		try:
			if cfg.ui.show_area_radioButton_2.isChecked():				
				self.showArea()
			else:
				self.clearCanvasPoly()
		except:
			pass