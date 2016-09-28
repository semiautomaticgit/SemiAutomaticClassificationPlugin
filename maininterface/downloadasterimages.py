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
cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

class DownloadASTERImages:

	def __init__(self):
		# check all bands
		self.checkAll = "No"
		self.rbbrBndPol = QgsRubberBand(cfg.cnvs, 2)
		cfg.ui.dateEdit_to_2.setDate(cfg.QDateSCP.currentDate())
		
	# add satellite list to combo
	def addSatelliteToCombo(self, satelliteList):
		for i in satelliteList:
			cfg.ui.astert_satellite_combo.addItem(i)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " satellites added")
			
	# user
	def rememberUser(self):
		if cfg.ui.remember_user_checkBox_3.isChecked():
			user = cfg.ui.user_usgs_lineEdit_2.text()
			pswd = cfg.utls.encryptPassword(cfg.ui.password_usgs_lineEdit_2.text())
			cfg.sets.setQGISRegSetting(cfg.regUSGSUserASTER, user)
			cfg.sets.setQGISRegSetting(cfg.regUSGSPassASTER, pswd)
			
	def rememberUserCheckbox(self):
		if cfg.ui.remember_user_checkBox_3.isChecked():
			self.rememberUser()
		else:
			cfg.sets.setQGISRegSetting(cfg.regUSGSUserASTER, "")
			cfg.sets.setQGISRegSetting(cfg.regUSGSPassASTER, "")
		
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
		t = cfg.dwnlASTERP
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(":/pointer/icons/pointer/ROI_pointer.png")
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: ASTER")
		
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
			UL = QgsPoint(float(cfg.ui.UX_lineEdit_4.text()), float(cfg.ui.UY_lineEdit_4.text()))
			UL1 = cfg.utls.projectPointCoordinates(UL, iCrs, pCrs)
			LR = QgsPoint(float(cfg.ui.LX_lineEdit_4.text()), float(cfg.ui.LY_lineEdit_4.text()))
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
		cfg.ui.LX_lineEdit_4.setText(str(point1.x()))
		cfg.ui.LY_lineEdit_4.setText(str(point1.y()))
		self.showArea()
		
	# set coordinates
	def pointerClickUL(self, point):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = QgsCoordinateReferenceSystem()
		iCrs.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
		point1 = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
		cfg.ui.UX_lineEdit_4.setText(str(point1.x()))
		cfg.ui.UY_lineEdit_4.setText(str(point1.y()))
		self.showArea()
		
	# find images
	def findImages(self):
		self.downloadMetadata()
				
	# download image metadata from NASA CMR Search https://cmr.earthdata.nasa.gov/search/site/search_api_docs.html
	def downloadMetadata(self):
		listImgID = []
		QdateFrom = cfg.ui.dateEdit_from_2.date()
		QdateTo = cfg.ui.dateEdit_to_2.date()
		dateFrom = QdateFrom.toPyDate().strftime("%Y-%m-%d") 
		dateTo = QdateTo.toPyDate().strftime("%Y-%m-%d") 
		maxCloudCover = int(cfg.ui.cloud_cover_spinBox_3.value())
		sat = cfg.ui.astert_satellite_combo.currentText()
		if sat == cfg.usgsASTER:
			NASAcollection = cfg.NASAASTERCollection
		imageFindList = []
		if len(cfg.ui.imageID_lineEdit_2.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit_2.text()
			imgIDLineSplit = str(imgIDLine).replace(" ", "").split(";")
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(" ", "").split(",")
			for m in imgIDLineSplit:
				imageFindList.append(m.lower())
		try:
			rubbRect = QgsRectangle(float(cfg.ui.UX_lineEdit_4.text()), float(cfg.ui.UY_lineEdit_4.text()), float(cfg.ui.LX_lineEdit_4.text()), float(cfg.ui.LY_lineEdit_4.text()))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg23()
			return "No"
		try:
			cfg.uiUtls.addProgressBar()
			cfg.QtGuiSCP.qApp.processEvents()
			cfg.cnvs.setRenderFlag(False)
			tW = cfg.ui.aster_images_tableWidget
			tW.setSortingEnabled(False)
			cfg.uiUtls.updateBar(30, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
			searchUrl = 'https://cmr.earthdata.nasa.gov/search/granules.echo10?bounding_box=' + cfg.ui.UX_lineEdit_4.text() + '%2C' + cfg.ui.LY_lineEdit_4.text() + '%2C' + cfg.ui.LX_lineEdit_4.text() + '%2C' + cfg.ui.UY_lineEdit_4.text() + '&echo_collection_id=' + NASAcollection + '&temporal=' + dateFrom + '%2C' + dateTo + 'T23%3A59%3A59.000Z&cloud_cover=0,' + str(maxCloudCover) + '&sort_key%5B%5D=-start_date&page_size=100&pretty=true'
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
				gId = entry.getElementsByTagName("ProducerGranuleId")[0]
				imgID = gId.firstChild.data
				if imgID not in imgIDList:
					imgIDList.append(imgID)
					imgDispID = imgID
					cc = entry.getElementsByTagName("QAPercentCloudCover")[0]
					cloudCover = cc.firstChild.data
					on = entry.getElementsByTagName("OnlineResources")
					url = on[0].getElementsByTagName("URL")[0]
					imgPreview = url.firstChild.data
					dt = entry.getElementsByTagName("SingleDateTime")[0]
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
					DayNightFlag = entry.getElementsByTagName("DayNightFlag")[0]
					dayNight = DayNightFlag.firstChild.data
					listImgID.append([imgID, imgDate, cloudCover, imgDispID, dayNight, lon, lat, imgPreview])
			cfg.uiUtls.updateBar(100, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
			c = tW.rowCount()
			for imID in listImgID:
				if len(imageFindList) > 0:
					for iF in imageFindList:
						if iF in imID[0].lower():
							imgCheck = "Yes"
							break
						else:
							imgCheck = "No"
				else:
					imgCheck = "Yes"
				if imgCheck == "Yes":
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, imID[0], c, 0)
					cfg.utls.addTableItem(tW, str(imID[1]), c, 1)
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
					cfg.utls.addTableItem(tW,"EOSDIS Earthdata", c, 9)
					cfg.utls.addTableItem(tW, imID[7], c, 10)
					cfg.utls.addTableItem(tW, NASAcollection, c, 11)
			tW.setSortingEnabled(True)
			cfg.cnvs.setRenderFlag(True)				
			cfg.uiUtls.removeProgressBar()
			self.clearCanvasPoly()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ASTER images")
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
		tW = cfg.ui.aster_images_tableWidget
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
				imgDispID = str(tW.item(i, 3).text())
				row = str(tW.item(i, 4).text())
				min_lat = str(tW.item(i, 5).text())
				min_lon = str(tW.item(i, 6).text())
				max_lat = str(tW.item(i, 7).text())
				max_lon = str(tW.item(i, 8).text())
				jpg = str(tW.item(i, 10).text())
				if cfg.osSCP.path.isfile(cfg.tmpDir + "//" + imgDispID + ".vrt"):
					l = cfg.utls.selectLayerbyName(imgDispID + ".vrt")
					if l is not None:		
						cfg.lgnd.setLayerVisible(l, True)
						cfg.utls.moveLayerTop(l)
					else:
						r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgDispID + ".vrt", imgDispID + ".vrt")
						cfg.utls.setRasterColorComposite(r, 1, 2, 3)
				else:
					self.downloadThumbnail(imgID, imgDispID, row, min_lat, min_lon, max_lat, max_lon, jpg, progress)
					if cfg.osSCP.path.isfile(cfg.tmpDir + "//" + imgDispID + ".vrt"):
						r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgDispID + ".vrt", imgDispID + ".vrt")
						cfg.utls.setRasterColorComposite(r, 1, 2, 3)
				progress = progress + progressStep
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.cnvs.refresh()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnails displayed")
		
	# download thumbnail
	def downloadThumbnail(self, imgID, imgDispID, row, min_lat, min_lon, max_lat, max_lon, imageJPG, progress = None):
		check = cfg.utls.downloadFile(imageJPG, cfg.tmpDir + "//" + imgDispID + "_thumb.jpg", imgDispID + "_thumb.jpg", progress)
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
				a = cfg.gdalPath + "gdal_translate -of VRT -a_ullr " + str(UL1.x()) + " " + str(UL1.y()) + " " + str(LR1.x()) + " " + str(LR1.y()) + ' -a_srs "+proj=utm +zone=' + str(zone) + ' +datum=WGS84 +units=m +no_defs" ' + cfg.tmpDir + "//" + imgDispID + "_thumb.jpg " + cfg.tmpDir + "//" + imgDispID + ".vrt"
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
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnail downloaded" + str(imgDispID))
			else:
				cfg.mx.msgErr41()
		else:
			cfg.mx.msgErr40()
	
	# remove highlighted images from table
	def removeImageFromTable(self):
		tW = cfg.ui.aster_images_tableWidget
		cfg.utls.removeRowsFromTable(tW)
					
	# download images in table
	def downloadImages(self):
		tW = cfg.ui.aster_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = cfg.utls.getExistingDirectory(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Download the images in the table (requires internet connection)"))
			if len(d) > 0:
				self.downloadASTERImages(d)
		
	# download ASTER data
	def downloadASTERImages(self, outputDirectory, exporter = "No"):
		cfg.uiUtls.addProgressBar()
		tW = cfg.ui.aster_images_tableWidget
		c = tW.rowCount()
		progressStep = 100 / c
		progressStep2 = progressStep/12
		progress = 0
		outDirList = []
		outFileList = []
		imgList = []
		links = []		
		for i in range(0, c):
			if cfg.actionCheck == "Yes":
				imgID = str(tW.item(i, 0).text())
				imgDispID = str(tW.item(i, 3).text())
				date = str(tW.item(i, 1).text())[0:10]
				if cfg.ui.download_if_preview_in_legend_checkBox_2.isChecked() and cfg.utls.selectLayerbyName(imgDispID + ".vrt", "Yes") is None:
					pass
				else:
					row = str(tW.item(i, 4).text())
					NASAcollection = str(tW.item(i, 11).text())
					outDir = outputDirectory + "/" + imgDispID
					if exporter == "No":
						oDir = cfg.utls.makeDirectory(outDir)
						if oDir is None:
							cfg.mx.msgErr58()
							cfg.uiUtls.removeProgressBar()
							return "No"
					outDirList.append(outDir)
					outFileList.append(outDir + "//" + imgDispID + ".hdf")
					progress = progress + progressStep
					outUrl = self.downloadASTERImagesFromNASA(imgID, NASAcollection, imgDispID, outDir, progress, exporter, date)
					links.append(outUrl)
			else:
				cfg.uiUtls.removeProgressBar()
				return "No"
		if exporter == "Yes":
			return links
		else:
			cfg.cnvs.setRenderFlag(False)
			if cfg.ui.preprocess_ASTER_checkBox.isChecked():
				for d in outFileList:
					if cfg.actionCheck == "Yes":
						cfg.ASTERT.populateTable(d, "Yes")
						o = d + "_converted"
						oDir = cfg.utls.makeDirectory(o)
						cfg.ASTERT.ASTER(d, o, "Yes")
			elif cfg.ui.load_in_QGIS_checkBox_2.isChecked():
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
			
	# download image
	def downloadASTERImagesFromNASA(self, imageID, collection, imageDisplayID, outputDirectory, progress, exporter = "No", date = None):
		# The ASTER L1T data products are retrieved from the online Data Pool, courtesy of the NASA Land Processes Distributed Active Archive Center (LP DAAC), USGS/Earth Resources Observation and Science (EROS) Center, Sioux Falls, South Dakota, https://lpdaac.usgs.gov/data_access/data_pool"
		url = "http://e4ftl01.cr.usgs.gov/ASTT/AST_L1T.003/" + date.replace("-", ".")+ "/" + imageDisplayID + ".hdf"
		if exporter == "Yes":
			return url
		else:
			user = cfg.ui.user_usgs_lineEdit_2.text()
			password =cfg.ui.password_usgs_lineEdit_2.text()
			try:
				imgID = imageDisplayID + ".hdf"
				check = cfg.utls.passwordConnectPython(user, password, url, 'urs.earthdata.nasa.gov', cfg.tmpDir + "//" + imgID, progress)
				if str(check) == 'Cancel action':
					return check
				if cfg.osSCP.path.getsize(cfg.tmpDir + "//" + imgID) > 10000:
					if collection == cfg.NASAASTERCollection:
						cfg.shutilSCP.copy(cfg.tmpDir + "//" + imgID, outputDirectory + "//" + imgID)
						cfg.osSCP.remove(cfg.tmpDir + "//" + imgID)
					else:
						tarFiles = cfg.tarfileSCP.open(cfg.tmpDir + "//" + imgID, 'r:gz')
						tarFiles.extractall(outputDirectory)
						tarFiles.close()
						cfg.osSCP.remove(cfg.tmpDir + "//" + imgID)
						return url
				else:
					cfg.mx.msgErr55(imgID)
					return "No"
			except Exception, err:
				cfg.mx.msgErr55(imgID)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			
	# export links
	def exportLinks(self):
		tW = cfg.ui.aster_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Export download links"), "", "*.txt")
			if len(d) > 0:
				links = self.downloadASTERImages("No", "Yes")
				if links == "No":
					pass
				else:
					l = open(d, 'w')
					for t in links:
						l.write(t + "\n")
					l.close()
					cfg.uiUtls.removeProgressBar()
			
	# clear table
	def clearTable(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset signature list"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the table?"))
		if a == "Yes":
			tW = cfg.ui.aster_images_tableWidget
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