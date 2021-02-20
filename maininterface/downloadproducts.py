# -*- coding: utf-8 -*-
'''
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright		: (C) 2012-2021 by Luca Congedo
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

'''



cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

class DownloadProducts:

	def __init__(self):
		# check all bands
		self.checkAll = 'No'
		self.rbbrBndPol = cfg.qgisGuiSCP.QgsRubberBand(cfg.cnvs, 2)
		cfg.ui.dateEdit_to.setDate(cfg.QDateSCP.currentDate())
		cfg.ui.dateEdit_from.setDate(cfg.QDateSCP.currentDate().addDays(-365))
		
	# add satellite list to combo
	def addSatelliteToCombo(self, satelliteList):
		for i in satelliteList:
			cfg.ui.landsat_satellite_combo.addItem(i)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " satellites added")
			
	# user
	def rememberUser(self):
		if cfg.ui.remember_user_checkBox_2.isChecked():
			user = cfg.ui.user_usgs_lineEdit.text()
			pswd = cfg.utls.encryptPassword(cfg.ui.password_usgs_lineEdit.text())
			cfg.utls.setQGISRegSetting(cfg.regUSGSUser, user)
			cfg.utls.setQGISRegSetting(cfg.regUSGSPass, pswd)
			
	def rememberUserCheckbox(self):
		if cfg.ui.remember_user_checkBox_2.isChecked():
			self.rememberUser()
		else:
			cfg.utls.setQGISRegSetting(cfg.regUSGSUser, "")
			cfg.utls.setQGISRegSetting(cfg.regUSGSPass, "")
		
	# add rubber band
	def addRubberBandPolygon(self, pointUL, pointLR):
		try:
			self.clearCanvasPoly()
		except:
			pass
		pointF = cfg.QtCoreSCP.QPointF()
		polF = cfg.QtGuiSCP.QPolygonF()
		pointF.setX(pointUL.x())
		pointF.setY(pointUL.y())
		polF.append(pointF)
		pointF.setX(pointLR.x())
		pointF.setY(pointUL.y())
		polF.append(pointF)
		pointF.setX(pointLR.x())
		pointF.setY(pointLR.y())
		polF.append(pointF)
		pointF.setX(pointUL.x())
		pointF.setY(pointLR.y())
		polF.append(pointF)
		pointF.setX(pointUL.x())
		pointF.setY(pointUL.y())
		polF.append(pointF)
		g = cfg.qgisCoreSCP.QgsGeometry().fromQPolygonF(polF)
		self.rbbrBndPol.setToGeometry(g, None)
		clr = cfg.QtGuiSCP.QColor('#ff0000')
		clr.setAlpha(50)
		self.rbbrBndPol.setFillColor(clr)
		self.rbbrBndPol.setWidth(3)
		
	# clear canvas
	def clearCanvasPoly(self):
		self.rbbrBndPol.reset(True)
		cfg.cnvs.refresh()

	# Activate pointer
	def pointerActive(self):
		# connect to click
		t = cfg.dwnlPrdPnt
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(':/pointer/icons/pointer/ROI_pointer.svg')
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'pointer active: Landsat')
		
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
		iCrs = cfg.qgisCoreSCP.QgsCoordinateReferenceSystem()
		iCrs.createFromProj4('+proj=longlat +datum=WGS84 +no_defs')
		try:
			UL = cfg.qgisCoreSCP.QgsPointXY(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()))
			UL1 = cfg.utls.projectPointCoordinates(UL, iCrs, pCrs)
			LR = cfg.qgisCoreSCP.QgsPointXY(float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
			LR1 = cfg.utls.projectPointCoordinates(LR, iCrs, pCrs)
			self.addRubberBandPolygon(UL1, LR1)
		except:
			pass
			
	# set coordinates
	def pointerClickLR(self, point):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = cfg.qgisCoreSCP.QgsCoordinateReferenceSystem('EPSG:4326')
		point1 = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
		if point1 is not False:
			try:
				if float(cfg.ui.UX_lineEdit_3.text()) < point1.x():
					cfg.ui.LX_lineEdit_3.setText(str(point1.x()))
				else:
					cfg.ui.LX_lineEdit_3.setText(str(cfg.ui.UX_lineEdit_3.text()))
					cfg.ui.UX_lineEdit_3.setText(str(point1.x()))
				if float(cfg.ui.UY_lineEdit_3.text()) > point1.y():
					cfg.ui.LY_lineEdit_3.setText(str(point1.y()))
				else:
					cfg.ui.LY_lineEdit_3.setText(str(cfg.ui.UY_lineEdit_3.text()))
					cfg.ui.UY_lineEdit_3.setText(str(point1.y()))
			except:
				cfg.ui.LX_lineEdit_3.setText(str(point1.x()))
				cfg.ui.LY_lineEdit_3.setText(str(point1.y()))
			self.showArea()
		
	# set coordinates
	def pointerClickUL(self, point):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = cfg.qgisCoreSCP.QgsCoordinateReferenceSystem('EPSG:4326')
		point1 = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
		if point1 is not False:
			try:
				if float(cfg.ui.LX_lineEdit_3.text()) > point1.x():
					cfg.ui.UX_lineEdit_3.setText(str(point1.x()))
				else:
					cfg.ui.UX_lineEdit_3.setText(str(cfg.ui.LX_lineEdit_3.text()))
					cfg.ui.LX_lineEdit_3.setText(str(point1.x()))
				if float(cfg.ui.LY_lineEdit_3.text()) < point1.y():
					cfg.ui.UY_lineEdit_3.setText(str(point1.y()))
				else:
					cfg.ui.UY_lineEdit_3.setText(str(cfg.ui.LY_lineEdit_3.text()))
					cfg.ui.LY_lineEdit_3.setText(str(point1.y()))
			except:
				cfg.ui.UX_lineEdit_3.setText(str(point1.x()))
				cfg.ui.UY_lineEdit_3.setText(str(point1.y()))
			self.showArea()
		
	# save download table
	def saveDownloadTable(self, file = None):
		downloadTable = cfg.utls.tableToText(cfg.ui.download_images_tableWidget)
		if file is None:
			cfg.utls.writeProjectVariable('SCP_DownloadTable', str(downloadTable))
		else:
			try:
				l = open(file, 'w')
			except:
				pass
			try:
				l.write(downloadTable)
				l.close()
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))	
		
	# open download table
	def openDownloadTable(self, file = None):
		if file is None:
			text = cfg.utls.readProjectVariable('SCP_DownloadTable', '')
		else:
			f = open(file, 'r')
			text = f.read()
		if len(text) > 0:
			downloadTable = cfg.utls.textToTable(cfg.ui.download_images_tableWidget, text)
			if downloadTable == 'No':
				cfg.utls.clearTable(cfg.ui.download_images_tableWidget)
				cfg.mx.msgErr19()
	
	# import table file
	def importTableText(self):
		file = cfg.utls.getOpenFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a text file of product table'), '', 'txt (*.txt)')
		if len(file) > 0:
			self.openDownloadTable(file)
		
	# find images
	def exportTableText(self):
		tW = cfg.ui.download_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Export table to file'), '', '*.txt', 'txt')
			if d is not False:
				if d.lower().endswith('.txt'):
					pass
				else:
					d = d + '.txt'
				self.saveDownloadTable(d)
		
	# find images
	def findImages(self):
		self.downloadMetadata()
				
	# download image metadata
	def downloadMetadata(self):
		sat = cfg.ui.landsat_satellite_combo.currentText()
		if sat in cfg.satSentinelList:
			self.queryDatabaseSentinel2()
		elif sat in cfg.satSentinel3List:
			self.queryDatabaseSentinel3()
		elif sat in cfg.satSentinel1List:
			self.queryDatabaseSentinel1()
		elif sat in cfg.satLandsatList:
			self.downloadMetadataLandsat()
		elif sat in cfg.satASTERtList:
			self.downloadMetadataASTER()
		elif sat in cfg.satMODIStList:
			self.downloadMetadataMODIS()
		elif sat in cfg.satGOEStList:
			self.downloadMetadataGOES()
			
	# download image metadata from NASA CMR Search https://cmr.earthdata.nasa.gov/search/site/search_api_docs.html
	def downloadMetadataLandsat(self):
		listImgID = []
		QdateFrom = cfg.ui.dateEdit_from.date()
		QdateTo = cfg.ui.dateEdit_to.date()
		dateFrom = QdateFrom.toPyDate().strftime('%Y-%m-%d') 
		dateTo = QdateTo.toPyDate().strftime('%Y-%m-%d') 
		maxCloudCover = int(cfg.ui.cloud_cover_spinBox.value())
		resultNum = int(cfg.ui.result_number_spinBox_2.value())
		sat = cfg.ui.landsat_satellite_combo.currentText()
		if sat == cfg.usgsLandsat8:
			NASAcollection = cfg.NASALandsat8Collection
			USGScollection = cfg.usgsLandsat8Collection
		elif sat == cfg.usgsLandsat7:
			NASAcollection = cfg.NASALandsat7Collection
			USGScollection = cfg.usgsLandsat7Collection
		elif sat == cfg.usgsLandsat45:
			NASAcollection = cfg.NASALandsat45Collection
			USGScollection = cfg.usgsLandsat45Collection
		elif sat == cfg.usgsLandsat15:
			NASAcollection = cfg.NASALandsat15Collection
			USGScollection = cfg.usgsLandsat15Collection
		imageFindList = []
		if len(cfg.ui.imageID_lineEdit.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit.text()
			imgIDLineSplit = str(imgIDLine).replace(' ', '').split(';')
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(' ', '').split(',')
			for m in imgIDLineSplit:
				imageFindList.append(m.lower())
		try:
			rubbRect = cfg.qgisCoreSCP.QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msg23()
			return 'No'
		try:
			cfg.uiUtls.addProgressBar()
			cfg.QtWidgetsSCP.qApp.processEvents()
			tW = cfg.ui.download_images_tableWidget
			tW.setSortingEnabled(False)
			cfg.uiUtls.updateBar(30, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
			# cloud cover returns 0 results
			# without cloud cover
			searchUrl = 'https://cmr.earthdata.nasa.gov/search/granules.echo10?bounding_box=' + cfg.ui.UX_lineEdit_3.text() + '%2C' + cfg.ui.LY_lineEdit_3.text() + '%2C' + cfg.ui.LX_lineEdit_3.text() + '%2C' + cfg.ui.UY_lineEdit_3.text() + '&echo_collection_id=' + NASAcollection + '&temporal=' + dateFrom + '%2C' + dateTo + 'T23%3A59%3A59.000Z&sort_key%5B%5D=-start_date&page_size=' + str(resultNum) + '&pretty=true'
			# connect and search
			searchResult = cfg.utls.NASASearch(searchUrl)
			xmlFile = searchResult.read()
			imgIDList = []
			doc = cfg.minidomSCP.parseString(xmlFile)
			entries = doc.getElementsByTagName('Granule')
			pages = len(entries)
			page = 0
			cloudCover = 0
			for entry in entries:
				page = page + 1
				cfg.uiUtls.updateBar(30 + int(page * 70 / pages), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
				gId = entry.getElementsByTagName('GranuleUR')[0]
				imgID = gId.firstChild.data
				lId = entry.getElementsByTagName('LocalVersionId')[0]
				lImgId = lId.firstChild.data
				if imgID not in imgIDList:
					imgIDList.append(imgID)
					imgDispID = imgID
					on = entry.getElementsByTagName('ProviderBrowseUrl')
					url = on[0].getElementsByTagName('URL')[0]
					imgPreview = url.firstChild.data
					if 'https://ims.cr.usgs.gov/browse/' not in imgPreview and 'https://earthexplorer.usgs.gov' not in imgPreview:
						imgPreview = 'https://ims.cr.usgs.gov/browse/' + imgPreview
					StartCoordinate1 = entry.getElementsByTagName('StartCoordinate1')[0]
					path = StartCoordinate1.firstChild.data
					StartCoordinate2 = entry.getElementsByTagName('StartCoordinate2')[0]
					row = StartCoordinate2.firstChild.data
					dt = entry.getElementsByTagName('BeginningDateTime')[0]
					imgDate = dt.firstChild.data
					imgDate = cfg.datetimeSCP.datetime.strptime(imgDate[0:19], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
					try:
						cc = entry.getElementsByTagName('QAPercentCloudCover')[0]
						cloudCover = cc.firstChild.data
					except:
						addAttrs = entry.getElementsByTagName('AdditionalAttribute')
						for addAttr in addAttrs:
							addAttrNames = addAttr.getElementsByTagName('Name')
							for addAttrName in addAttrNames:
								addAttrNameC = addAttrName.firstChild.data
								if addAttrNameC == 'LandCloudCover':
									addAttrValues = addAttr.getElementsByTagName('Values')[0]
									addAttrVal = addAttrValues.getElementsByTagName('Value')[0]
									cloudCover = addAttrVal.firstChild.data
					PointLatitude = entry.getElementsByTagName('PointLatitude')
					PointLongitude = entry.getElementsByTagName('PointLongitude')
					lat = []
					for latit in PointLatitude:
						lat.append(float(latit.firstChild.data))
					lon = []
					for longi in PointLongitude:
						lon.append(float(longi.firstChild.data))
					listImgID.append([imgID, imgDate, cloudCover, path, row, lon, lat, imgPreview, lImgId])
			c = tW.rowCount()
			for imID in listImgID:
				if len(imageFindList) > 0:
					for iF in imageFindList:
						if iF in imID[0].lower():
							imgCheck = 'Yes'
							break
						else:
							imgCheck = 'No'
				# workaround for cloud cover filter
				elif maxCloudCover < float(imID[2]):
					imgCheck = 'No'
				else:
					imgCheck = 'Yes'
				if imgCheck == 'Yes':
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, sat, c, 0)
					cfg.utls.addTableItem(tW, imID[0], c, 1)
					cfg.utls.addTableItem(tW, str(imID[1]), c, 2)
					cfg.utls.addTableItem(tW, int(round(float(imID[2]))), c, 3)
					cfg.utls.addTableItem(tW, imID[3], c, 4)
					cfg.utls.addTableItem(tW, imID[4], c, 5)
					min_lon = min(imID[5])
					max_lon = max(imID[5])
					min_lat = min(imID[6])
					max_lat = max(imID[6])
					cfg.utls.addTableItem(tW, float(min_lat), c, 6)
					cfg.utls.addTableItem(tW, float(min_lon), c, 7)
					cfg.utls.addTableItem(tW, float(max_lat), c, 8)
					cfg.utls.addTableItem(tW,float(max_lon), c, 9)
					cfg.utls.addTableItem(tW, USGScollection, c, 10)
					cfg.utls.addTableItem(tW, imID[7], c, 11)
					cfg.utls.addTableItem(tW, NASAcollection, c, 12)
					cfg.utls.addTableItem(tW, imID[8], c, 13)
			tW.setSortingEnabled(True)		
			cfg.uiUtls.removeProgressBar()
			self.clearCanvasPoly()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Landsat images')
			c = tW.rowCount()
			if c == 0:
				cfg.mx.msg21()
		except Exception as err:
			cfg.mx.msgErr39()
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
	
	# Add OpenStreetMap to the map as described in https://wiki.openstreetmap.org/wiki/QGIS (© OpenStreetMap contributors. The cartography is licensed as CC BY-SA)
	def displayOSM(self):
		cfg.utls.addRasterLayer(cfg.plgnDir + '/docs/openstreetmap_wms.xml', 'OpenStreetMap')
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' OSM added')
	
	# display images
	def displayImages(self):
		tW = cfg.ui.download_images_tableWidget
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
				sat = str(tW.item(i, 0).text())
				if sat in cfg.satSentinelList:
					self.displayGranulesSentinel2(i, progress)
				elif sat in cfg.satSentinel3List:
					self.displayGranulesSentinel3(i, progress)
				elif sat in cfg.satSentinel1List:
					self.displayGranulesSentinel1(i, progress)
				elif sat in cfg.satLandsatList or sat in cfg.satASTERtList or sat in cfg.satMODIStList:
					self.displayImagesNASA(i, progress)
				progress = progress + progressStep
				cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading ...'))
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.cnvs.refresh()
			
	# display images
	def displayImagesNASA(self, row, progress, preview = 'No'):
		i = row
		tW = cfg.ui.download_images_tableWidget
		sat = str(tW.item(i, 0).text())
		imgID = str(tW.item(i, 1).text())
		path = str(tW.item(i, 4).text())
		row = str(tW.item(i, 5).text())
		min_lat = str(tW.item(i, 6).text())
		min_lon = str(tW.item(i, 7).text())
		max_lat = str(tW.item(i, 8).text())
		max_lon = str(tW.item(i, 9).text())
		jpg = str(tW.item(i, 11).text())
		# image preview
		imOut = cfg.tmpDir + '//' + imgID + '_thumb.jpg'
		if preview == 'Yes' and cfg.osSCP.path.isfile(imOut):
			self.previewInLabel(imOut)
			return imOut
		if cfg.osSCP.path.isfile(cfg.tmpDir + '//' + imgID + '.vrt'):
			l = cfg.utls.selectLayerbyName(imgID)
			if l is not None:		
				cfg.utls.setLayerVisible(l, True)
				cfg.utls.moveLayerTop(l)
			else:
				r =cfg.utls.addRasterLayer(cfg.tmpDir + '//' + imgID + '.vrt')
				cfg.utls.setRasterColorComposite(r, 1, 2, 3)
		else:
			self.downloadThumbnail(imgID, path, row, min_lat, min_lon, max_lat, max_lon, jpg, sat, progress, preview)
			if cfg.osSCP.path.isfile(cfg.tmpDir + '//' + imgID + '.vrt'):
				r =cfg.utls.addRasterLayer(cfg.tmpDir + '//' + imgID + '.vrt')
				cfg.utls.setRasterColorComposite(r, 1, 2, 3)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' thumbnails displayed')
						
	# display image in label
	def previewInLabel(self, imagePath):
		tmpImage = imagePath.replace('.jp2', '.png')
		if imagePath.endswith('.jp2') and not cfg.osSCP.path.isfile(tmpImage):
			cfg.utls.getGDALForMac()
			# georeference thumbnail
			a = cfg.gdalPath + 'gdal_translate ' + imagePath + ' ' + tmpImage + ' -of PNG'
			if cfg.sysSCPNm != 'Windows':
				a = cfg.shlexSCP.split(a)
			try:
				if cfg.sysSCPNm == 'Windows':
					startupinfo = cfg.subprocessSCP.STARTUPINFO()
					startupinfo.dwFlags = cfg.subprocessSCP.STARTF_USESHOWWINDOW
					startupinfo.wShowWindow = cfg.subprocessSCP.SW_HIDE
					sP = cfg.subprocessSCP.Popen(a, shell=False, startupinfo = startupinfo, stdin = cfg.subprocessSCP.DEVNULL)
				else:
					sP = cfg.subprocessSCP.Popen(a, shell=False)
				sP.wait()
			# in case of errors
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		imagePath = tmpImage
		label = cfg.ui.image_preview_label
		pixmap = cfg.QtGuiSCP.QPixmap(imagePath).scaled(300, 300)
		label.setPixmap(pixmap)
		return imagePath
				
	# table click
	def tableClick(self):
		tW = cfg.ui.download_images_tableWidget
		i = tW.currentRow()
		if i >= 0:
			cfg.uiUtls.addProgressBar()
			progress = 10
			sat = str(tW.item(i, 0).text())
			if sat in cfg.satSentinelList:
				self.displayGranulesSentinel2(i, progress, 'Yes')
			elif sat in cfg.satSentinel3List:
				self.displayGranulesSentinel3(i, progress, 'Yes')
			elif sat in cfg.satSentinel1List:
				self.displayGranulesSentinel1(i, progress, 'Yes')
			elif sat in cfg.satLandsatList or sat in cfg.satASTERtList or sat in cfg.satMODIStList:
				self.displayImagesNASA(i, progress, 'Yes')
			cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading ...'))
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image index: ' + str(i))
						
	# download thumbnail
	def downloadThumbnail(self, imgID, path, row, min_lat, min_lon, max_lat, max_lon, imageJPG, sat, progress = None, preview = 'No'):
		imOut = cfg.tmpDir + '//' + imgID + '_thumb.jpg'
		if sat in cfg.satLandsatList:
			check = cfg.utls.downloadFile(imageJPG, imOut, imgID + '_thumb.jpg', progress)			
		elif sat == cfg.usgsASTER:
			user = cfg.ui.user_usgs_lineEdit_2.text()
			password = cfg.ui.password_usgs_lineEdit_2.text()
			check = cfg.utls.passwordConnectPython(user, password, imageJPG, 'urs.earthdata.nasa.gov', imOut, progress, 'No')
		elif sat in cfg.satMODIStList:
			user = cfg.ui.user_usgs_lineEdit_2.text()
			password =cfg.ui.password_usgs_lineEdit_2.text()
			check = cfg.utls.passwordConnectPython(user, password, imageJPG, 'urs.earthdata.nasa.gov', imOut, progress, 'No')
		if check == 'Yes':
			if preview == 'Yes':
				self.previewInLabel(imOut)
				return imOut
			self.onflyGeorefImage(cfg.tmpDir + '//' + imgID + '_thumb.jpg ', cfg.tmpDir + '//' + imgID + '.vrt', min_lon, max_lon, min_lat, max_lat)
		else:
			cfg.mx.msgErr40()
	
	# remove highlighted images from table
	def removeImageFromTable(self):
		tW = cfg.ui.download_images_tableWidget
		cfg.utls.removeRowsFromTable(tW)
					
	# download images in table
	def downloadImages(self):
		tW = cfg.ui.download_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Download the images in the table (requires internet connection)'))
			if len(d) > 0:
				self.downloadSentinelImages(d)
				self.downloadSentinel3Images(d)
				self.downloadSentinel1Images(d)
				self.downloadLandsatImages(d)
				self.downloadASTERImages(d)
				self.downloadMODISImages(d)
				self.downloadGOESImages(d)
				cfg.utls.sendSMTPMessage(None, str(__name__))
				cfg.utls.finishSound()
		
	# download Landsat data
	def downloadLandsatImages(self, outputDirectory, exporter = 'No'):
		cfg.uiUtls.addProgressBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'), message = '')
		tW = cfg.ui.download_images_tableWidget
		c = tW.rowCount()
		progressStep = 100 / c
		progressStep2 = progressStep/12
		progress = 0
		outDirList = []
		imgList = []
		links = []
		for i in range(0, c):
			sat = str(tW.item(i, 0).text())
			if cfg.actionCheck == 'Yes':
				if sat in cfg.satLandsatList:
					imgID = str(tW.item(i, 1).text())
					if cfg.ui.download_if_preview_in_legend_checkBox.isChecked() and cfg.utls.selectLayerbyName(imgID, 'Yes') is None:
						pass
					else:
						acquisitionDate = str(tW.item(i, 2).text())
						path = str(tW.item(i, 4).text())
						row = str(tW.item(i, 5).text())
						USGScollection = str(tW.item(i, 10).text())
						NASAcollection = str(tW.item(i, 12).text())
						lImgID = str(tW.item(i, 13).text())
						outDir = outputDirectory + '/' + imgID + '_' + acquisitionDate[0:10]
						oDir = cfg.utls.makeDirectory(outDir)
						if oDir is None:
							cfg.uiUtls.removeProgressBar()
							cfg.mx.msgErr58()
							return 'No'
						outDirList.append(outDir)
						# download Landsat data using the service https://storage.googleapis.com/gcp-public-data-landsat
						sat = imgID[0:4]
						collID = '01'
						urlL = 'https://storage.googleapis.com/gcp-public-data-landsat/'+ sat + '/' + collID +'/' + path.zfill(3) + '/' + row.zfill(3) +'/' + imgID + '/' + imgID + '_'
						check = cfg.utls.downloadFile( urlL + 'MTL.txt', outDir + '//' + imgID + '_MTL.txt', imgID + '_MTL.txt', progress)
						if check == 'Yes':
							meta = open(outDir + '//' + imgID + '_MTL.txt', 'r').read()
							if 'NoSuchKey' in meta:
								check = 'No'
						if check == 'Yes':
							links.append(urlL + 'MTL.txt')
							if NASAcollection == cfg.NASALandsat8Collection:
								bRange = [1,2,3,4,5,6,7,8,9,10,11,12]
							elif NASAcollection == cfg.NASALandsat7Collection:
								bRange = [1,2,3,4,5,6,7,8,12]
							elif NASAcollection == cfg.NASALandsat45Collection:
								bRange = [1,2,3,4,5,6,7,12]
							elif NASAcollection == cfg.NASALandsat15Collection:
								if sat[-1] == '4' or sat[-1]== '5':
									bRange = [1,2,3,4]
								else:
									bRange = [4,5,6,7]
							for i in bRange:
								progress = progress + progressStep2
								if cfg.actionCheck == 'Yes':
									if exporter == 'Yes':
										links.append(urlL + 'B' + str(i) + '.TIF')
									else:
										t = 'cfg.ui.checkBox_band_' + str(i) + '.isChecked()'
										checkBand = eval(t)
										if checkBand is True:
											# Landsat 7 bands 6
											if NASAcollection == cfg.NASALandsat7Collection and i == 6:
												cfg.utls.downloadFile( urlL + 'B6_VCID_1.TIF', outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_B6_VCID_1.TIF', imgID + '_B6_VCID_1.TIF', progress)
												if cfg.osSCP.path.isfile(outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_B6_VCID_1.TIF'):
													imgList.append(outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_B6_VCID_1.TIF')
													# logger
													cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image downloaded ' + imgID + '_B6_VCID_1.TIF')
												cfg.utls.downloadFile( urlL + 'B6_VCID_2.TIF', outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_B6_VCID_1.TIF', imgID + '_B6_VCID_2.TIF', progress)
												if cfg.osSCP.path.isfile(outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_B6_VCID_2.TIF'):
													imgList.append(outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_B6_VCID_2.TIF')
													# logger
													cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image downloaded ' + imgID + '_B6_VCID_2.TIF')
											else:
												cfg.utls.downloadFile( urlL + 'B' + str(i) + '.TIF', outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_B' + str(i) + '.TIF', imgID + '_B' + str(i) + '.TIF', progress)
												if cfg.osSCP.path.isfile(outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_B' + str(i) + '.TIF'):
													imgList.append(outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_B' + str(i) + '.TIF')
													# logger
													cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image downloaded ' + imgID + '_B' + str(i))
								else:
									cfg.uiUtls.removeProgressBar()
									return 'No'
							if cfg.actionCheck == 'Yes':
								progress = progress + progressStep2
								if cfg.ui.checkBox_band_12.isChecked():
									if exporter == 'Yes':
										links.append(urlL + 'BQA.TIF')
									else:
										cfg.utls.downloadFile( urlL + 'BQA.TIF', outDir + '//' + imgID  + '_' + acquisitionDate[0:10] + '_BQA.TIF', imgID + '_BQA.TIF', progress)
										if cfg.osSCP.path.isfile(outDir + '//' + imgID + '_' + acquisitionDate[0:10] + '_BQA.TIF'):
											imgList.append(outDir + '//' + imgID + '_' + acquisitionDate[0:10] + '_BQA.TIF')
											# logger
											cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image downloaded ' + imgID + '_BQA.TIF')
						else:
							outUrl = self.downloadLandsatImagesFromUSGS(lImgID, USGScollection, row, outDir, progress, exporter)
							links.append(outUrl)
							progress = progress + progressStep
			else:
				cfg.uiUtls.removeProgressBar()
				return 'No'
		if exporter == 'Yes':
			return links
		else:
			cfg.cnvs.setRenderFlag(False)
			if cfg.ui.preprocess_checkBox.isChecked():
				n = len(outDirList)
				i = 0
				for d in outDirList:
					i = i + 1
					cfg.uiUtls.updateBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Processing') + ' [' + str(i) + '/' + str(n) + '] ' + cfg.osSCP.path.basename(d), message = '')
					if cfg.actionCheck == 'Yes':
						cfg.landsatT.populateTable(d, 'Yes')
						o = d + '_converted'
						cfg.utls.makeDirectory(o)
						cfg.landsatT.landsat(d, o, 'Yes')
			elif cfg.ui.load_in_QGIS_checkBox.isChecked():
				for d in outDirList:
					try:
						for f in cfg.osSCP.listdir(d):
							if f.lower().endswith('.tif'):
								r =cfg.utls.addRasterLayer(d + '/' + f)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			
	# download image preview
	def downloadLandsatImagesFromUSGS(self, imageID, collection, row, outputDirectory, progress, exporter = 'No'):
		url = 'http://earthexplorer.usgs.gov/download/' + collection + '/' + imageID + '/STANDARD/EE'
		if exporter == 'Yes':
			return url
		else:
			user = cfg.ui.user_usgs_lineEdit.text()
			password =cfg.ui.password_usgs_lineEdit.text()
			try:
				imgID = imageID + '.tar.gz'
				check = cfg.utls.downloadFileUSGS(user, password, 'https://ers.cr.usgs.gov', url, cfg.tmpDir + '//' + imgID, imgID, progress, 'Yes')
				if str(check) == 'Cancel action':
					return check
				if cfg.osSCP.path.getsize(cfg.tmpDir + '//' + imgID) > 10000:
					tarFiles = cfg.tarfileSCP.open(cfg.tmpDir + '//' + imgID, 'r:gz')
					tarFiles.extractall(outputDirectory)
					tarFiles.close()
					cfg.osSCP.remove(cfg.tmpDir + '//' + imgID)
					return url
				else:
					cfg.mx.msgErr55(imgID)
					return 'No'
			except Exception as err:
				cfg.mx.msgErr50(str(err))
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
					
	# export links
	def exportLinks(self):
		tW = cfg.ui.download_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = cfg.utls.getSaveFileName(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Export download links'), '', '*.txt', 'txt')
			if d is not False:
				if d.lower().endswith('.txt'):
					pass
				else:
					d = d + '.txt'
				linksS = self.downloadSentinelImages(cfg.tmpDir, 'Yes')
				linksS3 = self.downloadSentinel3Images(cfg.tmpDir, 'Yes')
				linksS1 = self.downloadSentinel1Images(cfg.tmpDir, 'Yes')
				linksL = self.downloadLandsatImages(cfg.tmpDir, 'Yes')
				linksA = self.downloadASTERImages(cfg.tmpDir, 'Yes')
				linksM = self.downloadMODISImages(cfg.tmpDir, 'Yes')
				linksG = self.downloadGOESImages(cfg.tmpDir, 'Yes')
				links =  linksS + linksS3 + linksS1 + linksL + linksA + linksM + linksG
				if links == 'No':
					pass
				else:
					l = open(d, 'w')
					for t in links:
						l.write(t + '\n')
					l.close()
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
				
	# check all bands
	def checkAllBands(self):
		if self.checkAll == 'Yes':
			for i in range(1, 13):
				t = 'cfg.ui.checkBox_band_' + str(i) + '.setCheckState(2)'
				eval(t)
			self.checkAll = 'No'
		else:
			for i in range(1, 13):
				t = 'cfg.ui.checkBox_band_' + str(i) + '.setCheckState(0)'
				eval(t)
			self.checkAll = 'Yes'
			
	# clear table
	def clearTable(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reset signature list'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Are you sure you want to clear the table?'))
		if a == 'Yes':
			tW = cfg.ui.download_images_tableWidget
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
			
### Sentinel-3
					
	# read database
	def queryDatabaseSentinel3(self):
		QdateFrom = cfg.ui.dateEdit_from.date()
		QdateTo = cfg.ui.dateEdit_to.date()
		dateFrom = QdateFrom.toPyDate().strftime('%Y-%m-%d') 
		dateTo = QdateTo.toPyDate().strftime('%Y-%m-%d') 
		maxCloudCover = int(cfg.ui.cloud_cover_spinBox.value())
		resultNum = int(cfg.ui.result_number_spinBox_2.value())
		sat = cfg.ui.landsat_satellite_combo.currentText()
		imageFindList = []
		if len(cfg.ui.imageID_lineEdit.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit.text()
			imgIDLineSplit = str(imgIDLine).replace(' ', '').split(';')
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(' ', '').split(',')
			for m in imgIDLineSplit:
				imageFindList.append(m.lower())
			imgQuery = 'OL_1_EFR*'
		else:
			imageFindList.append('s3')
			imgQuery = 'OL_1_EFR*'
		try:
			rubbRect = cfg.qgisCoreSCP.QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
			if abs(float(cfg.ui.UX_lineEdit_3.text()) - float(cfg.ui.LX_lineEdit_3.text())) > 10 or abs(float(cfg.ui.UY_lineEdit_3.text()) - float(cfg.ui.LY_lineEdit_3.text())) > 10:
				cfg.mx.msgWar18()
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msg23()
			return 'No'
		cfg.uiUtls.addProgressBar()
		tW = cfg.ui.download_images_tableWidget
		cfg.uiUtls.updateBar(30, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
		cfg.QtWidgetsSCP.qApp.processEvents()
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		imageTableList = []
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl
		# loop for results
		maxResultNum = resultNum
		if maxResultNum > 100:
			maxResultNum = 100
		for startR in range(0, resultNum, maxResultNum):
			url = topUrl + '/search?q=' + imgQuery + '%20AND%20beginPosition:[' + str(dateFrom) + 'T00:00:00.000Z%20TO%20' + str(dateTo) + 'T23:59:59.999Z]%20AND%20footprint:%22Intersects(POLYGON((' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ',' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.LY_lineEdit_3.text() + ',' + cfg.ui.LX_lineEdit_3.text() + '%20' + cfg.ui.LY_lineEdit_3.text() + ',' + cfg.ui.LX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ',' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ')))%22' + '&rows=' + str(maxResultNum) + '&start=' + str(startR)
			#url = topUrl + '/search?q=' + imgQuery + '%20AND%20cloudcoverpercentage:[0%20TO%20' + str(maxCloudCover) + ']%20AND%20beginPosition:[' + str(dateFrom) + 'T00:00:00.000Z%20TO%20' + str(dateTo) + 'T23:59:59.999Z]%20AND%20footprint:%22Intersects(POLYGON((' + cfg.ui.UX_lineEdit_3.text() + "%20" + cfg.ui.UY_lineEdit_3.text() + "," + cfg.ui.UX_lineEdit_3.text() + "%20" + cfg.ui.LY_lineEdit_3.text() + "," + cfg.ui.LX_lineEdit_3.text() + "%20" + cfg.ui.LY_lineEdit_3.text() + "," + cfg.ui.LX_lineEdit_3.text() + "%20" + cfg.ui.UY_lineEdit_3.text() + "," + cfg.ui.UX_lineEdit_3.text() + "%20" + cfg.ui.UY_lineEdit_3.text() + ')))%22' + '&rows=' + str(maxResultNum) + '&start=' + str(startR)
			cloudcoverpercentage = 0
			response = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl, quiet = 'Yes')
			if response == 'No':
				# second try
				topLevelUrl = 'https://scihub.copernicus.eu/dhus'
				url = url.replace(topUrl, topLevelUrl)
				topUrl =topLevelUrl
				response = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl)
				if response == 'No':
					cfg.uiUtls.removeProgressBar()
					return 'No'
			#info = response.info()
			xml = response.read()
			tW.setSortingEnabled(False)
			try:
				doc = cfg.minidomSCP.parseString(xml)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				if 'HTTP Status 500' in xml:
					cfg.mx.msgWar24()
				else:
					cfg.mx.msgErr40()
				cfg.uiUtls.removeProgressBar()
				return 'No'
			entries = doc.getElementsByTagName('entry')
			e = 0
			for entry in entries:
				if cfg.actionCheck == 'Yes':
					productType = 'OL_1_EFR___'
					e = e + 1
					cfg.uiUtls.updateBar(30 + e * int(70/len(entries)), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
					imgNameTag = entry.getElementsByTagName('title')[0]
					imgName = imgNameTag.firstChild.data
					imgIDTag = entry.getElementsByTagName('id')[0]
					imgID = imgIDTag.firstChild.data
					summary = entry.getElementsByTagName('summary')[0]
					infos = summary.firstChild.data.split(',')
					for info in infos:
						infoIt = info.strip().split(' ')
						if infoIt[0] == 'Date:':
							acqDateI = infoIt[1]
						if infoIt[0] == 'Size:':
							size = infoIt[1] + ' ' + infoIt[2]
					strings = entry.getElementsByTagName('str')
					for x in strings:
						attr = x.getAttribute('name')
						if attr == 'producttype':
							productType = x.firstChild.data
						if attr == 'footprint':
							footprintCoord = x.firstChild.data.replace('MULTIPOLYGON (((', '').replace('POLYGON ((', '').replace(')))', '').replace('))', '').split(',')
							xList = []
							yList = []
							for coords in footprintCoord:
								cc = coords.lstrip()
								xList.append(float(cc.split(' ')[0]))
								yList.append(float(cc.split(' ')[1]))
							min_lon = min(xList)
							max_lon = max(xList)
							min_lat = min(yList)
							max_lat = max(yList)
					doubles = entry.getElementsByTagName('double')
					for xd in doubles:
						attr = xd.getAttribute('name')
						if attr == 'cloudcoverpercentage':
							cloudcoverpercentage = xd.firstChild.data
					try:
						if cfg.actionCheck == 'Yes':								
							for filter in imageFindList:
								if filter in imgName.lower():
									acZoneI = imgName[64:81]
									# add item to table
									c = tW.rowCount()
									# add list items to table
									tW.setRowCount(c + 1)
									imgPreview = topUrl + "/odata/v1/Products('" +  imgID + "')/Products('Quicklook')/$value"
									cfg.utls.addTableItem(tW, sat, c, 0)
									cfg.utls.addTableItem(tW, imgName, c, 1)
									cfg.utls.addTableItem(tW, acqDateI, c, 2)
									cfg.utls.addTableItem(tW, float(cloudcoverpercentage), c, 3)						
									cfg.utls.addTableItem(tW, acZoneI, c, 4)
									cfg.utls.addTableItem(tW, "", c, 5)
									cfg.utls.addTableItem(tW, float(min_lat), c, 6)
									cfg.utls.addTableItem(tW, float(min_lon), c, 7)
									cfg.utls.addTableItem(tW, float(max_lat), c, 8)
									cfg.utls.addTableItem(tW, float(max_lon), c, 9)
									cfg.utls.addTableItem(tW, size, c, 10)
									cfg.utls.addTableItem(tW, imgPreview, c, 11)
									cfg.utls.addTableItem(tW, imgID, c, 12)
									cfg.utls.addTableItem(tW, imgName, c, 13)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		tW.setSortingEnabled(True)		
		cfg.uiUtls.removeProgressBar()
		self.clearCanvasPoly()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Sentinel images")
			
	# display granule preview	
	def displayGranulesSentinel3(self, row, progress, preview = 'No'):
		i = row
		tW = cfg.ui.download_images_tableWidget
		imgNm = str(tW.item(i, 1).text())
		acquisitionDate = str(tW.item(i, 2).text())
		imgID = imgNm + '.vrt'
		url = str(tW.item(i, 11).text())
		# image preview
		imOut = cfg.tmpDir + '//' + imgID
		if preview == 'Yes' and cfg.osSCP.path.isfile(imOut):
			self.previewInLabel(imOut)
			return imOut
		if cfg.osSCP.path.isfile(imOut + '.vrt'):
			l = cfg.utls.selectLayerbyName(imgID)
			if l is not None:		
				cfg.utls.setLayerVisible(l, True)
				cfg.utls.moveLayerTop(l)
			else:
				r =cfg.utls.addRasterLayer(imOut, imgID)
		else:		
			min_lat = str(tW.item(i, 6).text())
			min_lon = str(tW.item(i, 7).text())
			max_lat = str(tW.item(i, 8).text())
			max_lon = str(tW.item(i, 9).text())
			self.downloadThumbnailSentinel3(imgID, min_lat, min_lon, max_lat, max_lon, url, progress, preview)
			if cfg.osSCP.path.isfile(imOut + '.vrt'):
				r =cfg.utls.addRasterLayer(imOut + '.vrt', imgID)
				cfg.utls.setRasterColorComposite(r, 1, 2, 3)		
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " granules displayed")
		
	# download image preview
	def downloadThumbnailSentinel3(self, imgID, min_lat, min_lon, max_lat, max_lon, imageJPG, progress = None, preview = 'No'):
		imOut = cfg.tmpDir + '//' + imgID
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl
		check = cfg.utls.passwordConnectPython(user, password, imageJPG, topLevelUrl, imOut, progress, quiet = 'Yes')
		if check == 'Yes':
			if preview == 'Yes':
				self.previewInLabel(imOut)
				return imOut
			self.onflyGeorefImage(cfg.tmpDir + '//' + imgID, cfg.tmpDir + '//' + imgID + '.vrt', min_lon, max_lon, min_lat, max_lat)
		else:
			# second try
			topLevelUrl = 'https://scihub.copernicus.eu/dhus'
			imageJPG = imageJPG.replace(topUrl, topLevelUrl)
			check = cfg.utls.passwordConnectPython(user, password, imageJPG, topLevelUrl, imOut, progress)
			if check == 'Yes':
				if preview == 'Yes':
					self.previewInLabel(imOut)
					return imOut
				self.onflyGeorefImage(cfg.tmpDir + '//' + imgID, cfg.tmpDir + '//' + imgID + '.vrt', min_lon, max_lon, min_lat, max_lat)
			else:
				cfg.mx.msgErr40()

	# download images
	def downloadSentinel3Images(self, outputDirectory, exporter = 'No'):
		cfg.uiUtls.addProgressBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'), message = '')
		tW = cfg.ui.download_images_tableWidget
		outDirList = []
		imgList = []
		links = []
		c = tW.rowCount()
		progressStep = 100 / c
		progress = 0
		# disable map canvas render for speed
		cfg.cnvs.setRenderFlag(False)
		for i in range(0, c):
			sat = str(tW.item(i, 0).text())
			if cfg.actionCheck == 'Yes':
				if sat == cfg.esaSentinel3:
					imgName = str(tW.item(i, 13).text())
					acquisitionDate = str(tW.item(i, 2).text())
					imgID = str(tW.item(i, 12).text())
					imgName2 = str(tW.item(i, 1).text())
					imgJp2 = imgName2 + '.vrt'
					if cfg.ui.download_if_preview_in_legend_checkBox.isChecked() and cfg.utls.selectLayerbyName(imgJp2, 'Yes') is None:
						pass
					else:
						outFiles = []
						outDirList.append(outputDirectory + '//' + imgName2)
						progress = progress + progressStep
						if exporter == 'No':
							oDir = cfg.utls.makeDirectory(outputDirectory + '//' + imgName2)
							if oDir is None:
								cfg.mx.msgErr58()
								cfg.uiUtls.removeProgressBar()
								cfg.cnvs.setRenderFlag(True)
								return 'No'
						# download bands
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_1, '01', imgID, imgName, imgName2, acquisitionDate,outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_2, '02', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_3, '03', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_4, '04', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_5, '05', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_6, '06', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_7, '07', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_8, '08', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_9, '09', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_10, '10', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_11, '11', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_12, '12', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_13, '13', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_14, '14', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_15, '15', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_16, '16', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_17, '17', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_18, '18', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_19, '19', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_20, '20', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.checkBoxs3_band_21, '21', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.s3_ancillary_data_checkBox, 'ancillary1', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.s3_ancillary_data_checkBox, 'ancillary2', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.s3_ancillary_data_checkBox, 'ancillary3', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						self.checkSentinel3ImageBands(cfg.ui.s3_ancillary_data_checkBox, 'ancillary4', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
						for oFile in outFiles:
							cfg.shutilSCP.copy(oFile[0], oFile[1])
							cfg.osSCP.remove(oFile[0])
			else:
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
				return 'No'
		if cfg.ui.preprocess_checkBox.isChecked() and exporter == 'No':
			n = len(outDirList)
			i = 0
			for d in outDirList:
				i = i + 1
				cfg.uiUtls.updateBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Processing') + ' [' + str(i) + '/' + str(n) + '] ' + cfg.osSCP.path.basename(d), message = '')
				if cfg.actionCheck == 'Yes':
					cfg.sentinel3T.populateTable(d, 'Yes')
					o = d + '_con'
					oDir = cfg.utls.makeDirectory(o)
					if oDir is None:
						cfg.mx.msgErr58()
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
						return 'No'
					cfg.sentinel3T.sentinel3(d, o, 'Yes')
		cfg.uiUtls.removeProgressBar()
		cfg.cnvs.setRenderFlag(True)
		return links
					
	# check band download
	def checkSentinel3ImageBands(self, checkbox, bandNumber, imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFilesList, linksList):
		if cfg.actionCheck == 'Yes':
			if checkbox.isChecked():
				user = cfg.ui.user_scihub_lineEdit.text()
				password =cfg.ui.password_scihub_lineEdit.text()
				# check url
				topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
				topUrl =topLevelUrl + '/odata/v1/Products'
				topUrl2 =topLevelUrl
				if bandNumber == 'ancillary1':				
					urlL = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SEN3')/Nodes('tie_geometries.nc')/$value"
					outFile = cfg.tmpDir + "//" + imgName[0:15] + "_" + acquisitionDate[0:10] + '_B' + bandNumber + '.nc'
					outCopyFile = outputDirectory + '//' + imgName2 + '//tie_geometries.nc'
				elif bandNumber == 'ancillary2':				
					urlL = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SEN3')/Nodes('qualityFlags.nc')/$value"
					outFile = cfg.tmpDir + "//" + imgName[0:15] + "_" + acquisitionDate[0:10] + '_B' + bandNumber + '.nc'
					outCopyFile = outputDirectory + '//' + imgName2 + '//qualityFlags.nc'
				elif bandNumber == 'ancillary3':				
					urlL = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SEN3')/Nodes('geo_coordinates.nc')/$value"
					outFile = cfg.tmpDir + '//' + imgName[0:15] + '_' + acquisitionDate[0:10] + '_B' + bandNumber + '.nc'
					outCopyFile = outputDirectory + '//' + imgName2 + '//geo_coordinates.nc'
				elif bandNumber == 'ancillary4':				
					urlL = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SEN3')/Nodes('instrument_data.nc')/$value"
					outFile = cfg.tmpDir + '//' + imgName[0:15] + '_' + acquisitionDate[0:10] + '_B' + bandNumber + '.nc'
					outCopyFile = outputDirectory + '//' + imgName2 + '//instrument_data.nc'
				else:
					urlL = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SEN3')/Nodes('Oa" + bandNumber + "_radiance.nc')/$value"
					outFile = cfg.tmpDir + '//' + imgName[0:15] + '_' + acquisitionDate[0:10] + '_B' + bandNumber + '.nc'
					outCopyFile = outputDirectory + '//' + imgName2 + '//' + imgName[0:15] + '_' + acquisitionDate[0:10] + '_B' + bandNumber + '.nc'
				if exporter == 'No':
					self.downloadFileSentinel3(urlL, outFile, progress)
					try:
						if cfg.osSCP.path.getsize(outFile) < 100000:
							self.downloadFileSentinel3(urlL, outFile, progress)
							if cfg.osSCP.path.getsize(outFile) < 100000:
								cfg.mx.msgWar23(imgName2 + '_B' + bandNumber)
						outFilesList.append([outFile, outCopyFile])
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					linksList.append(urlL)
		else:
			cfg.uiUtls.removeProgressBar()
			return 'No'
			
	# download file
	def downloadFileSentinel3(self, url, output, progress = None):
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), url)
		check = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl, output, progress, quiet = 'Yes')
		if check == 'Yes':
			return output
		else:
			# second try
			topLevelUrl = 'https://scihub.copernicus.eu/dhus'
			url = url.replace(topUrl, topLevelUrl)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), url)
			check = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl, output, progress)
			if check == 'Yes':
				return output
			else:
				cfg.mx.msgErr40()
				return 'No'
			
### Sentinel-2

	# user
	def rememberUserSentinel2(self):	
		if cfg.ui.remember_user_checkBox.isChecked():
			user = cfg.ui.user_scihub_lineEdit.text()
			pswd = cfg.utls.encryptPassword(cfg.ui.password_scihub_lineEdit.text())
			cfg.utls.setQGISRegSetting(cfg.regSciHubUser, user)
			cfg.utls.setQGISRegSetting(cfg.regSciHubPass, pswd)
			
	def rememberUserCheckboxSentinel2(self):
		if cfg.ui.remember_user_checkBox.isChecked():
			self.rememberUserSentinel2()
		else:
			cfg.utls.setQGISRegSetting(cfg.regSciHubUser, '')
			cfg.utls.setQGISRegSetting(cfg.regSciHubPass, '')
			
	def alternativeCheckboxSentinel2(self):
		if cfg.ui.sentinel2_alternative_search_checkBox.isChecked():
			cfg.utls.setQGISRegSetting(cfg.regSentinelAlternativeSearch, '2')
		else:
			cfg.utls.setQGISRegSetting(cfg.regSentinelAlternativeSearch, '0')
			
	# reset service
	def resetService(self):
		cfg.ui.sentinel_service_lineEdit.setText(cfg.SciHubServiceNm)
		cfg.utls.setQGISRegSetting(cfg.regSciHubService, cfg.SciHubServiceNm)

	# service
	def rememberService(self):
		service = cfg.ui.sentinel_service_lineEdit.text()
		cfg.utls.setQGISRegSetting(cfg.regSciHubService, service)
			
	# download file
	def downloadFileSentinel2(self, url, output, progress = None):
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), url)
		check = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl, output, progress, quiet = 'Yes')
		if check == 'Yes':
			return 'Yes'
		else:
			# second try
			topLevelUrl = 'https://scihub.copernicus.eu/dhus'
			url = url.replace(topUrl, topLevelUrl)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ' + url)
			check = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl, output, progress)
			if check == 'Yes':
				return output
			else:
				cfg.mx.msgErr40()
				return 'No'

	# display granule preview	
	def displayGranulesSentinel2(self, row, progress, preview = 'No'):
		i = row
		tW = cfg.ui.download_images_tableWidget
		imgNm = str(tW.item(i, 1).text())
		acquisitionDate = str(tW.item(i, 2).text())
		if imgNm[0:4] == 'L1C_':
			imgID = imgNm + '_p.jp2'
		elif imgNm[0:4] == 'L2A_':
			imgID = imgNm + '_p.jp2'
		else:
			imgID = imgNm[0:-7] + '_p.jp2'
		url = str(tW.item(i, 11).text())
		# image preview
		imOut = cfg.tmpDir + '//' + imgID
		if preview == 'Yes' and cfg.osSCP.path.isfile(imOut):
			self.previewInLabel(imOut)
			return imOut
		if cfg.osSCP.path.isfile(imOut  + '.vrt') or cfg.osSCP.path.isfile(imOut.replace('.jp2', '.png')  + '.vrt'):
			l = cfg.utls.selectLayerbyName(imgID)
			if l is not None:		
				cfg.utls.setLayerVisible(l, True)
				cfg.utls.moveLayerTop(l)
			else:
				r =cfg.utls.addRasterLayer(imOut + '.vrt', imgID)
		else:
			if 'storage.googleapis.com' in url:
				check = cfg.utls.downloadFile(url, imOut, None, progress)
			else:
				check = self.downloadFileSentinel2(url, imOut, progress)
			if check == 'Yes':
				if preview == 'Yes':
					self.previewInLabel(imOut)
					return imOut
				min_lat = str(tW.item(i, 6).text())
				min_lon = str(tW.item(i, 7).text())
				max_lat = str(tW.item(i, 8).text())
				max_lon = str(tW.item(i, 9).text())
				self.onflyGeorefImage(imOut, imOut + '.vrt', min_lon, max_lon, min_lat, max_lat)
				if cfg.osSCP.path.isfile(imOut + '.vrt'):
					r =cfg.utls.addRasterLayer(imOut + '.vrt', imgID.replace('.vrt',''))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' granules displayed')
					
	# use CREODIAS Finder API https://creodias.eu/ (from https://creodias.eu/eo-data-finder-api-manual the database is accessible free and anonymously, and open for anonymous access to everyone, no authorization is used). For other DIAS platforms see https://www.copernicus.eu/en/access-data/dias
	def queryDatabaseSentinel2Alternative(self):
		QdateFrom = cfg.ui.dateEdit_from.date()
		QdateTo = cfg.ui.dateEdit_to.date()
		dateFrom = QdateFrom.toPyDate().strftime('%Y-%m-%d') 
		dateTo = QdateTo.toPyDate().strftime('%Y-%m-%d') 
		maxCloudCover = int(cfg.ui.cloud_cover_spinBox.value())
		resultNum = int(cfg.ui.result_number_spinBox_2.value())
		sat = cfg.ui.landsat_satellite_combo.currentText()
		imageFindList = []
		m = 'S2*'
		if len(cfg.ui.imageID_lineEdit.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit.text()
			imgIDLineSplit = str(imgIDLine).replace(' ', '').split(';')
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(' ', '').split(',')
			for m in imgIDLineSplit:
				imageFindList.append(m.lower().replace('*', ''))
			imgQuery = ''
			if len(imageFindList) == 1:
				imgQuery = m + '%20AND%20'
		else:
			imageFindList.append('s2')
			imgQuery = ''
		try:
			NoRect = 'No'
			rubbRect = cfg.qgisCoreSCP.QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
			if abs(float(cfg.ui.UX_lineEdit_3.text()) - float(cfg.ui.LX_lineEdit_3.text())) > 10 or abs(float(cfg.ui.UY_lineEdit_3.text()) - float(cfg.ui.LY_lineEdit_3.text())) > 10:
				cfg.mx.msgWar18()
		except Exception as err:
			if len(imageFindList) == 1:
				imgQuery = m + '*' + '%20AND%20'
				NoRect = 'Yes'
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				cfg.mx.msg23()
				return 'No'
		cfg.uiUtls.addProgressBar()
		imgQuery = cfg.ui.imageID_lineEdit.text()
		if len(imgQuery) == 0:
			imgQuery = 'S2'
		tW = cfg.ui.download_images_tableWidget
		cfg.uiUtls.updateBar(30, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
		cfg.QtWidgetsSCP.qApp.processEvents()
		imageTableList = []
		# loop for results
		maxResultNum = resultNum
		if maxResultNum > 100:
			maxResultNum = 100
		for startR in range(0, resultNum, maxResultNum):
			if NoRect == 'Yes':
				url = 'https://finder.creodias.eu/resto/api/collections/Sentinel2/search.json?cloudCover=[0%2C' + str(maxCloudCover) + ']&maxRecords=' + str(maxResultNum) + '&page=' + str(startR+1) + '&sortParam=startDate&sortOrder=descending&status=all&dataset=ESA-DATASET' + '&productIdentifier=%25' + imgQuery + '%25&startDate=' + str(dateFrom) + 'T00%3A00%3A00Z&completionDate=' + str(dateTo) + 'T23%3A59%3A59Z'
			else:
				url = 'https://finder.creodias.eu/resto/api/collections/Sentinel2/search.json?cloudCover=[0%2C' + str(maxCloudCover) + ']&maxRecords=' + str(maxResultNum) + '&page=' + str(startR+1) + '&sortParam=startDate&sortOrder=descending&status=all&dataset=ESA-DATASET' + '&productIdentifier=%25' + imgQuery + '%25&startDate=' + str(dateFrom) + 'T00%3A00%3A00Z&completionDate=' + str(dateTo) + 'T23%3A59%3A59Z&geometry=POLYGON((' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ',' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.LY_lineEdit_3.text() + ',' + cfg.ui.LX_lineEdit_3.text() + '%20' + cfg.ui.LY_lineEdit_3.text() + ',' + cfg.ui.LX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ',' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + '))'
			jsonT = cfg.utls.createTempRasterPath('json')
			check = cfg.utls.downloadFile(url, jsonT)
			if check != 'Yes':
				cfg.uiUtls.removeProgressBar()
				return 'No'
			try:
				with open(jsonT) as jsonTF:
					doc = cfg.jsonSCP.load(jsonTF)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				cfg.mx.msgErr40()
				cfg.uiUtls.removeProgressBar()
				return 'No'
			tW.setSortingEnabled(False)
			entries = doc['features']
			e = 0
			for entry in entries:
				if cfg.actionCheck == 'Yes':
					productType = 'S2MSI1C'
					e = e + 1
					cfg.uiUtls.updateBar(30 + e * int(70/len(entries)), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
					imgName = entry['properties']['title'].replace('.SAFE', '')
					acqDateI =  entry['properties']['startDate']
					productType =  entry['properties']['productType']
					cloudcoverpercentage =  entry['properties']['cloudCover']
					footprintCoord =  entry['geometry']['coordinates'][0]
					xList = []
					yList = []
					for coords in footprintCoord:
						xList.append(float(coords[0]))
						yList.append(float(coords[1]))
					min_lon = min(xList)
					max_lon = max(xList)
					min_lat = min(yList)
					max_lat = max(yList)
					if cfg.actionCheck == 'Yes':
						# download Sentinel data using the service https://storage.googleapis.com/gcp-public-data-sentinel-2
						if productType == 'L1C':
							url2 = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/MTD_MSIL1C.xml'
						else:
							url2 = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/MTD_MSIL2A.xml'
						xml2T = cfg.utls.createTempRasterPath('xml')
						check = cfg.utls.downloadFile(url2, xml2T)
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' xml downloaded' )
						try:
							newV = None
							if xml2T is not None:
								doc2 = cfg.minidomSCP.parse(xml2T)
							else:
								doc2 = cfg.minidomSCP.parseString(xml2)
							try:
								imgName2Tag = doc2.getElementsByTagName('IMAGE_FILE')[0]
							except:
								imgName2Tag = doc2.getElementsByTagName('IMAGE_FILE_2A')[0]
							imgName2 = imgName2Tag.firstChild.data.split('/')[1]
							if cfg.actionCheck == 'Yes':								
								for filter in imageFindList:
									if filter in imgName.lower() or filter in imgName2.lower():
										acZoneI = imgName2.split("_")[1][1:]
										# add item to table
										c = tW.rowCount()
										# add list items to table
										tW.setRowCount(c + 1)
										if productType == 'L1C':
											imgName3 = imgName2Tag.firstChild.data.split('/')[3]
											imgName3 = imgName3.split('_')
											pviName = imgName3[0] + '_' + imgName3[1] + '_PVI.jp2'
											imgPreview = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/GRANULE/' + imgName2 + '/QI_DATA/' + pviName 
										else:
											imgName3 = imgName2Tag.firstChild.data.split('/')[4]
											imgName3 = imgName3.split('_')
											pviName = imgName3[0] + '_' + imgName3[1] + '_PVI.jp2'
											imgPreview = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/GRANULE/' + imgName2 + '/QI_DATA/' + pviName
										cfg.utls.addTableItem(tW, sat, c, 0)
										cfg.utls.addTableItem(tW, imgName2, c, 1)
										cfg.utls.addTableItem(tW, acqDateI, c, 2)
										cfg.utls.addTableItem(tW, float(cloudcoverpercentage), c, 3)
										cfg.utls.addTableItem(tW, acZoneI, c, 4)
										cfg.utls.addTableItem(tW, '', c, 5)
										cfg.utls.addTableItem(tW, float(min_lat), c, 6)
										cfg.utls.addTableItem(tW, float(min_lon), c, 7)
										cfg.utls.addTableItem(tW, float(max_lat), c, 8)
										cfg.utls.addTableItem(tW, float(max_lon), c, 9)
										cfg.utls.addTableItem(tW, '', c, 10)
										cfg.utls.addTableItem(tW, imgPreview, c, 11)
										cfg.utls.addTableItem(tW, imgName, c, 12)
										cfg.utls.addTableItem(tW, imgName, c, 13)
										newV = 'Yes'
										break
						except Exception as err:
							if cfg.actionCheck == 'Yes':								
								for filter in imageFindList:
									if filter in imgName.lower():
										# add item to table
										c = tW.rowCount()
										co = cfg.QtGuiSCP.QColor(160, 160, 160)
										# add list items to table
										tW.setRowCount(c + 1)
										cfg.utls.addTableItem(tW, sat, c, 0, 'Yes', co)
										cfg.utls.addTableItem(tW, imgName, c, 1, 'Yes', co)
										cfg.utls.addTableItem(tW, acqDateI, c, 2, 'Yes', co)
										cfg.utls.addTableItem(tW, float(cloudcoverpercentage), c, 3, 'Yes', co)
										cfg.utls.addTableItem(tW, '', c, 4, 'Yes', co)
										cfg.utls.addTableItem(tW, '', c, 5, 'Yes', co)
										cfg.utls.addTableItem(tW, float(min_lat), c, 6, 'Yes', co)
										cfg.utls.addTableItem(tW, float(min_lon), c, 7, 'Yes', co)
										cfg.utls.addTableItem(tW, float(max_lat), c, 8, 'Yes', co)
										cfg.utls.addTableItem(tW, float(max_lon), c, 9, 'Yes', co)
										cfg.utls.addTableItem(tW, '', c, 10, 'Yes', co)
										cfg.utls.addTableItem(tW, '', c, 11, 'Yes', co)
										cfg.utls.addTableItem(tW, imgName, c, 12, 'Yes', co)
										cfg.utls.addTableItem(tW, imgName, c, 13, 'Yes', co)
										newV = 'Yes'
										# logger
										cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
										break
		tW.setSortingEnabled(True)		
		cfg.uiUtls.removeProgressBar()
		self.clearCanvasPoly()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Sentinel images')
		
	# read database
	def queryDatabaseSentinel2(self):
		if len(cfg.ui.user_scihub_lineEdit.text()) == 0 or cfg.ui.sentinel2_alternative_search_checkBox.isChecked():
			cfg.downProd.queryDatabaseSentinel2Alternative()
		else:
			QdateFrom = cfg.ui.dateEdit_from.date()
			QdateTo = cfg.ui.dateEdit_to.date()
			dateFrom = QdateFrom.toPyDate().strftime('%Y-%m-%d') 
			dateTo = QdateTo.toPyDate().strftime('%Y-%m-%d') 
			maxCloudCover = int(cfg.ui.cloud_cover_spinBox.value())
			resultNum = int(cfg.ui.result_number_spinBox_2.value())
			sat = cfg.ui.landsat_satellite_combo.currentText()
			imageFindList = []
			m = 'S2*'
			if len(cfg.ui.imageID_lineEdit.text()) > 0:
				imgIDLine = cfg.ui.imageID_lineEdit.text()
				imgIDLineSplit = str(imgIDLine).replace(' ', '').split(';')
				if len(imgIDLineSplit) == 1:
					imgIDLineSplit = str(imgIDLine).replace(' ', '').split(',')
				for m in imgIDLineSplit:
					imageFindList.append(m.lower().replace('*', ''))
				imgQuery = ''
				if len(imageFindList) == 1:
					imgQuery = m + '%20AND%20'
			else:
				imageFindList.append('s2')
				imgQuery = ''
			try:
				NoRect = 'No'
				rubbRect = cfg.qgisCoreSCP.QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
				if abs(float(cfg.ui.UX_lineEdit_3.text()) - float(cfg.ui.LX_lineEdit_3.text())) > 10 or abs(float(cfg.ui.UY_lineEdit_3.text()) - float(cfg.ui.LY_lineEdit_3.text())) > 10:
					cfg.mx.msgWar18()
			except Exception as err:
				if len(imageFindList) == 1:
					imgQuery = m + '*' + '%20AND%20'
					NoRect = 'Yes'
				else:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msg23()
					return 'No'
			cfg.uiUtls.addProgressBar()
			tW = cfg.ui.download_images_tableWidget
			cfg.uiUtls.updateBar(30, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
			cfg.QtWidgetsSCP.qApp.processEvents()
			user = cfg.ui.user_scihub_lineEdit.text()
			password =cfg.ui.password_scihub_lineEdit.text()
			imageTableList = []
			# check url
			topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
			topUrl =topLevelUrl
			# loop for results
			maxResultNum = resultNum
			if maxResultNum > 100:
				maxResultNum = 100
			for startR in range(0, resultNum, maxResultNum):
				if NoRect == 'Yes':
					url = topUrl + '/search?q=(' + imgQuery + 'platformname:Sentinel-2)%20AND%20cloudcoverpercentage:[0%20TO%20' + str(maxCloudCover) + ']%20AND%20beginPosition:[' + str(dateFrom) + 'T00:00:00.000Z%20TO%20' + str(dateTo) + 'T23:59:59.999Z]' + '&rows=' + str(maxResultNum) + '&start=' + str(startR)
				else:
					url = topUrl + '/search?q=(' + imgQuery + 'platformname:Sentinel-2)%20AND%20cloudcoverpercentage:[0%20TO%20' + str(maxCloudCover) + ']%20AND%20beginPosition:[' + str(dateFrom) + 'T00:00:00.000Z%20TO%20' + str(dateTo) + 'T23:59:59.999Z]%20AND%20footprint:%22Intersects(POLYGON((' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ',' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.LY_lineEdit_3.text() + ',' + cfg.ui.LX_lineEdit_3.text() + '%20' + cfg.ui.LY_lineEdit_3.text() + ',' + cfg.ui.LX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ',' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ')))%22' + '&rows=' + str(maxResultNum) + '&start=' + str(startR)
				response = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl, quiet = 'Yes')
				if response == 'No':
					# second try
					topLevelUrl = 'https://scihub.copernicus.eu/dhus'
					url = url.replace(topUrl, topLevelUrl)
					topUrl =topLevelUrl
					response = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl)
					if response == 'No':
						cfg.uiUtls.removeProgressBar()
						return 'No'
				#info = response.info()
				try:
					xml = response.read()
					doc = cfg.minidomSCP.parseString(xml)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					try:
						if 'HTTP Status 500' in xml:
							cfg.mx.msgWar24()
						else:
							cfg.mx.msgErr40()
					except:
						cfg.mx.msgErr40()
					cfg.uiUtls.removeProgressBar()
					return 'No'
				tW.setSortingEnabled(False)
				entries = doc.getElementsByTagName('entry')
				e = 0
				for entry in entries:
					if cfg.actionCheck == 'Yes':
						productType = 'S2MSI1C'
						e = e + 1
						cfg.uiUtls.updateBar(30 + e * int(70/len(entries)), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
						imgNameTag = entry.getElementsByTagName('title')[0]
						imgName = imgNameTag.firstChild.data
						imgIDTag = entry.getElementsByTagName('id')[0]
						imgID = imgIDTag.firstChild.data
						summary = entry.getElementsByTagName('summary')[0]
						infos = summary.firstChild.data.split(',')
						for info in infos:
							infoIt = info.strip().split(' ')
							if infoIt[0] == 'Date:':
								acqDateI = infoIt[1]
							# if infoIt[0] == 'Satellite:':
								# print "Satellite " + infoIt[1]
							if infoIt[0] == 'Size:':
								size = infoIt[1] + ' ' + infoIt[2]
						strings = entry.getElementsByTagName('str')
						for x in strings:
							attr = x.getAttribute('name')
							if attr == 'producttype':
								productType = x.firstChild.data
							if attr == 'footprint':
								footprintCoord = x.firstChild.data.replace('MULTIPOLYGON (((', '').replace('POLYGON ((', '').replace(')))', '').replace('))', '').split(',')
								xList = []
								yList = []
								for coords in footprintCoord:
									cc = coords.lstrip()
									xList.append(float(cc.split(' ')[0]))
									yList.append(float(cc.split(' ')[1]))
								min_lon = min(xList)
								max_lon = max(xList)
								min_lat = min(yList)
								max_lat = max(yList)
						doubles = entry.getElementsByTagName('double')
						for xd in doubles:
							attr = xd.getAttribute('name')
							if attr == 'cloudcoverpercentage':
								cloudcoverpercentage = xd.firstChild.data
						if cfg.actionCheck == 'Yes':
							# download Sentinel data using the service https://storage.googleapis.com/gcp-public-data-sentinel-2
							if productType == 'S2MSI2Ap' or productType == 'S2MSI2A':
								url2 = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/MTD_MSIL2A.xml'
							else:
								url2 = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/MTD_MSIL1C.xml'
							xml2T = cfg.utls.createTempRasterPath('xml')
							check = cfg.utls.downloadFile(url2, xml2T)
							if check == 'Yes':
								pass
							else:
								xml2T = None
								if productType == 'S2MSI2Ap' or productType == 'S2MSI2A':
									url2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('MTD_MSIL2A.xml')/$value"
								else:
									url2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('MTD_MSIL1C.xml')/$value"
								response2 = cfg.utls.passwordConnectPython(user, password, url2, topLevelUrl, None, None, quiet = 'No')
								try:
									xml2 = response2.read()
								except:
									xml2 = response2
								if len(xml2) == 0 or 'Navigation failed' in str(xml2) or 'Internal Server Error' in str(xml2):
									# old xml version
									#url2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('" + imgName.replace('_PRD_MSIL1C_', '_MTD_SAFL1C_') + ".xml')/$value"
									#response2 = cfg.utls.passwordConnectPython(user, password, url2, topLevelUrl)
									pass
								if response2 == 'No':
									cfg.uiUtls.removeProgressBar()
									return 'No'
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' xml downloaded' )
							try:
								newV = None
								if xml2T is not None:
									doc2 = cfg.minidomSCP.parse(xml2T)
								else:
									doc2 = cfg.minidomSCP.parseString(xml2)
								try:
									imgName2Tag = doc2.getElementsByTagName('IMAGE_FILE')[0]
								except:
									imgName2Tag = doc2.getElementsByTagName('IMAGE_FILE_2A')[0]
								imgName2 = imgName2Tag.firstChild.data.split('/')[1]
								if cfg.actionCheck == 'Yes':								
									for filter in imageFindList:
										if filter in imgName.lower() or filter in imgName2.lower():
											acZoneI = imgName2.split("_")[1][1:]
											# add item to table
											c = tW.rowCount()
											# add list items to table
											tW.setRowCount(c + 1)
											if xml2T is None:
												imgPreview = topUrl + "/odata/v1/Products('" +  imgID + "')/Products('Quicklook')/$value"
												imgPreview2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('" + imgName2[0:-7] + "_B01.jp2')/$value"
											else:
												imgPreview = topUrl + "/odata/v1/Products('" +  imgID + "')/Products('Quicklook')/$value"
												imgPreview2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('" + imgName2[0:-7] + "_B01.jp2')/$value"
											cfg.utls.addTableItem(tW, sat, c, 0)
											cfg.utls.addTableItem(tW, imgName2, c, 1)
											cfg.utls.addTableItem(tW, acqDateI, c, 2)
											cfg.utls.addTableItem(tW, float(cloudcoverpercentage), c, 3)
											cfg.utls.addTableItem(tW, acZoneI, c, 4)
											cfg.utls.addTableItem(tW, "", c, 5)
											cfg.utls.addTableItem(tW, float(min_lat), c, 6)
											cfg.utls.addTableItem(tW, float(min_lon), c, 7)
											cfg.utls.addTableItem(tW, float(max_lat), c, 8)
											cfg.utls.addTableItem(tW, float(max_lon), c, 9)
											cfg.utls.addTableItem(tW, size, c, 10)
											cfg.utls.addTableItem(tW, imgPreview, c, 11)
											cfg.utls.addTableItem(tW, imgID, c, 12)
											cfg.utls.addTableItem(tW, imgName, c, 13)
											newV = 'Yes'
											break
							except Exception as err:
								if cfg.actionCheck == 'Yes':								
									for filter in imageFindList:
										if filter in imgName.lower():
											# add item to table
											c = tW.rowCount()
											co = cfg.QtGuiSCP.QColor(160, 160, 160)
											# add list items to table
											tW.setRowCount(c + 1)
											cfg.utls.addTableItem(tW, sat, c, 0, 'Yes', co)
											cfg.utls.addTableItem(tW, imgName, c, 1, 'Yes', co)
											cfg.utls.addTableItem(tW, acqDateI, c, 2, 'Yes', co)
											cfg.utls.addTableItem(tW, float(cloudcoverpercentage), c, 3, 'Yes', co)
											cfg.utls.addTableItem(tW, "", c, 4, 'Yes', co)
											cfg.utls.addTableItem(tW, "", c, 5, 'Yes', co)
											cfg.utls.addTableItem(tW, float(min_lat), c, 6, 'Yes', co)
											cfg.utls.addTableItem(tW, float(min_lon), c, 7, 'Yes', co)
											cfg.utls.addTableItem(tW, float(max_lat), c, 8, 'Yes', co)
											cfg.utls.addTableItem(tW, float(max_lon), c, 9, 'Yes', co)
											cfg.utls.addTableItem(tW, size, c, 10, 'Yes', co)
											cfg.utls.addTableItem(tW, "", c, 11, 'Yes', co)
											cfg.utls.addTableItem(tW, imgID, c, 12, 'Yes', co)
											cfg.utls.addTableItem(tW, imgName, c, 13, 'Yes', co)
											newV = 'Yes'
											# logger
											cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
											break
							if newV is None:
								# old xml version
								try:
									doc2 = cfg.minidomSCP.parseString(xml2)
									entries2 = doc2.getElementsByTagName("Granules")
									if len(entries2) == 0:
										entries2 = doc2.getElementsByTagName("Granule")
									for entry2 in entries2:
										if cfg.actionCheck == 'Yes':
											imgName2 = entry2.attributes["granuleIdentifier"].value
											for filter in imageFindList:
												if filter in imgName.lower() or filter in imgName2.lower():
													acZoneI = imgName2[-12:-7]
													# add item to table
													c = tW.rowCount()
													# add list items to table
													tW.setRowCount(c + 1)
													imgPreview = topUrl + "/odata/v1/Products('" +  imgID + "')/Products('Quicklook')/$value"
													imgPreview2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('" + imgName2[0:-7] + "_B01.jp2')/$value"
													cfg.utls.addTableItem(tW, sat, c, 0)
													cfg.utls.addTableItem(tW, imgName2, c, 1)
													cfg.utls.addTableItem(tW, acqDateI, c, 2)
													cfg.utls.addTableItem(tW, float(cloudcoverpercentage), c, 3)
													cfg.utls.addTableItem(tW, acZoneI, c, 4)
													cfg.utls.addTableItem(tW, "", c, 5)
													cfg.utls.addTableItem(tW, float(min_lat), c, 6)
													cfg.utls.addTableItem(tW, float(min_lon), c, 7)
													cfg.utls.addTableItem(tW, float(max_lat), c, 8)
													cfg.utls.addTableItem(tW, float(max_lon), c, 9)
													cfg.utls.addTableItem(tW, size, c, 10)
													cfg.utls.addTableItem(tW, imgPreview2, c, 11)
													cfg.utls.addTableItem(tW, imgID, c, 12)
													cfg.utls.addTableItem(tW, imgName, c, 13)
								except Exception as err:
									# logger
									cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			tW.setSortingEnabled(True)		
			cfg.uiUtls.removeProgressBar()
			self.clearCanvasPoly()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Sentinel images')

	# download images
	def downloadSentinelImages(self, outputDirectory, exporter = 'No'):
		cfg.uiUtls.addProgressBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'), message = '')
		tW = cfg.ui.download_images_tableWidget
		outDirList = []
		imgList = []
		links = []
		check = 'Yes'
		c = tW.rowCount()
		progressStep = 100 / c
		progress = 0
		# disable map canvas render for speed
		cfg.cnvs.setRenderFlag(False)
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl + '/odata/v1/Products'
		topUrl2 =topLevelUrl
		for i in range(0, c):
			sat = str(tW.item(i, 0).text())
			if cfg.actionCheck == 'Yes':
				if sat == cfg.esaSentinel2:
					imgName = str(tW.item(i, 13).text())
					acquisitionDate = str(tW.item(i, 2).text())
					imgID = str(tW.item(i, 12).text())
					imgName2 = str(tW.item(i, 1).text())
					if imgName2[0:4] == 'L1C_':
						imgJp2 = imgName2 + '_p.jp2'
					elif imgName2[0:4] == 'L2A_':
						imgJp2 = imgName2 + '_p.jp2'
					else:
						imgJp2 = imgName2[0:-7] + '_p.jp2'
					if cfg.ui.download_if_preview_in_legend_checkBox.isChecked() and cfg.utls.selectLayerbyName(imgJp2, 'Yes') is None:
						pass
					else:
						outFiles = []
						if imgName2[0:4] == 'L1C_':
							outDirList.append(outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10])
						elif imgName2[0:4] == 'L2A_':
							outDirList.append(outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10])
						else:
							outDirList.append(outputDirectory + '//' + imgName2[0:-7] + '_' + acquisitionDate[0:10])
						progress = progress + progressStep
						if exporter == 'No':
							if imgName2[0:4] == 'L1C_':
								oDir = cfg.utls.makeDirectory(outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10])
							elif imgName2[0:4] == 'L2A_':
								oDir = cfg.utls.makeDirectory(outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10])
							else:
								oDir = cfg.utls.makeDirectory(outputDirectory + '//' + imgName2[0:-7] + '_' + acquisitionDate[0:10])
							if oDir is None:
								cfg.mx.msgErr58()
								cfg.uiUtls.removeProgressBar()
								cfg.cnvs.setRenderFlag(True)
								return 'No'
						# download ancillary data
						urlL1 = []
						urlL2 = []
						urlL3 = []
						#download metadata
						if imgName2[0:4] == 'L1C_':
							# new version
							urlL1.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('MTD_MSIL1C.xml')/$value")
							outFile1 = outputDirectory + "//" + imgName2 + "_" + acquisitionDate[0:10] + "//" + 'MTD_MSIL1C.xml'
							urlL2.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('MTD_TL.xml')/$value")
							outFile2 = outputDirectory + "//" + imgName2 + "_" + acquisitionDate[0:10] + "//" + 'MTD_TL.xml'
							# download QI
							urlL3.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('QI_DATA')/Nodes('MSK_CLOUDS_B00.gml')/$value")
							outFile3 = outputDirectory + "//" + imgName2 + "_" + acquisitionDate[0:10] + "//" + 'MSK_CLOUDS_B00.gml'
							# download Sentinel data using the service https://storage.googleapis.com/gcp-public-data-sentinel-2
							urlL1.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/MTD_MSIL1C.xml')
							urlL2.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/GRANULE/' + imgName2 + '/MTD_TL.xml')
							urlL3.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/GRANULE/' + imgName2 + '/QI_DATA/MSK_CLOUDS_B00.gml')
						elif imgName2[0:4] == 'L2A_':
							# new version
							urlL1.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('MTD_MSIL2A.xml')/$value")
							outFile1 = outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10] + '//' + 'MTD_MSIL2A.xml'
							urlL2.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('MTD_TL.xml')/$value")
							outFile2 = outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10] + '//' + 'MTD_TL.xml'
							# download QI
							urlL3.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('QI_DATA')/Nodes('MSK_CLOUDS_B00.gml')/$value")
							outFile3 = outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10] + '//' + 'MSK_CLOUDS_B00.gml'
							# download Sentinel data using the service https://storage.googleapis.com/gcp-public-data-sentinel-2
							urlL1.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/MTD_MSIL2A.xml')
							urlL2.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/GRANULE/' + imgName2 + '/MTD_TL.xml')
							urlL3.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/GRANULE/' + imgName2 + '/QI_DATA/MSK_CLOUDS_B00.gml')
						else:
							# old version
							urlL1.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('" + imgName.replace('_PRD_MSIL1C_', '_MTD_SAFL1C_') + ".xml')/$value")
							outFile1 = outputDirectory + '//' + imgName2[0:-7] + '_' + acquisitionDate[0:10] + '//' + imgName.replace('_PRD_MSIL1C_', '_MTD_SAFL1C_') + '.xml'
							urlL2.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('" + imgName2[0:-7].replace('_MSI_L1C_', '_MTD_L1C_') + ".xml')/$value")
							outFile2 = outputDirectory + '//' + imgName2[0:-7] + '_' + acquisitionDate[0:10] + '//' + imgName2[0:-7].replace('_MSI_L1C_', '_MTD_L1C_')  + '.xml'		
							# download QI
							urlL3.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('QI_DATA')/Nodes('" + imgName2[0:-7].replace('_MSI_L1C_TL_', '_MSK_CLOUDS_')  + "_B00_MSIL1C.gml')/$value")
							outFile3 = outputDirectory + '//' + imgName2[0:-7] + '_' + acquisitionDate[0:10] + '//' + imgName2[0:-7].replace('_MSI_L1C_TL_', '_MSK_CLOUDS_') + '_B00_MSIL1C.gml'
							# download Sentinel data using the service https://storage.googleapis.com/gcp-public-data-sentinel-2
							urlL1.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/' + imgName.replace('_PRD_MSIL1C_', '_MTD_SAFL1C_') + '.xml')
							urlL2.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/' + imgName2 + '/GRANULE/' + imgName2[0:-7].replace('_MSI_L1C_', '_MTD_L1C_') + '.xml')
							urlL3.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE/' + imgName2 + '/GRANULE/QI_DATA/' + imgName2[0:-7].replace('_MSI_L1C_TL_', '_MSK_CLOUDS_')  + '_B00_MSIL1C.gml')
						tempFile1 = cfg.utls.createTempRasterPath('xml')
						check = cfg.utls.downloadFile(urlL1[1], tempFile1, None, progress)
						if cfg.ui.ancillary_data_checkBox.isChecked():
							if exporter == 'No':
								if check == 'Yes':
									cfg.utls.downloadFile(urlL1[1], outFile1, None, progress)
									cfg.utls.downloadFile(urlL2[1], outFile2, None, progress)
									cfg.utls.downloadFile(urlL3[1], outFile3, None, progress)
								else:
									self.downloadFileSentinel2(urlL1[0], outFile1, progress)
									self.downloadFileSentinel2(urlL2[0], outFile2, progress)
									self.downloadFileSentinel2(urlL3[0], outFile3, progress)
							else:
								if check == 'Yes':
									links.append(urlL1[1])
									links.append(urlL2[1])
									links.append(urlL3[1])
								else:
									links.append(urlL1[0])
									links.append(urlL2[0])
									links.append(urlL3[0])
						# download bands
						self.checkImageBands(cfg.ui.checkBoxs_band_1, '01', imgID, imgName, imgName2, acquisitionDate,outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_2, '02', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_3, '03', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_4, '04', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_5, '05', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_6, '06', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_7, '07', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_8, '08', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_9, '8A', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_10, '09', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_11, '10', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_12, '11', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						self.checkImageBands(cfg.ui.checkBoxs_band_13, '12', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links, check)
						for oFile in outFiles:
							cfg.shutilSCP.copy(oFile[0], oFile[1] + '.jp2')
							cfg.osSCP.remove(oFile[0])
							if cfg.ui.load_in_QGIS_checkBox.isChecked() and cfg.ui.preprocess_checkBox.isChecked() is False:
								c = cfg.utls.addRasterLayer(oFile[1] + '.jp2')
			else:
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
				return 'No'
		if cfg.ui.preprocess_checkBox.isChecked() and exporter == 'No':
			n = len(outDirList)
			i = 0
			for d in outDirList:
				i = i + 1
				cfg.uiUtls.updateBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Processing') + ' [' + str(i) + '/' + str(n) + '] ' + cfg.osSCP.path.basename(d), message = '')
				if cfg.actionCheck == 'Yes':
					cfg.sentinel2T.populateTable(d, 'Yes')
					o = d + "_con"
					oDir = cfg.utls.makeDirectory(o)
					if oDir is None:
						cfg.mx.msgErr58()
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
						return 'No'
					cfg.sentinel2T.sentinel2(d, o, 'Yes')
		cfg.uiUtls.removeProgressBar()
		cfg.cnvs.setRenderFlag(True)
		return links

	# check all bands
	def checkAllBandsSentinel2(self):
		if self.checkAll == 'Yes':
			for i in range(1, 14):
				t = 'cfg.ui.checkBoxs_band_' + str(i) + '.setCheckState(2)'
				eval(t)
			cfg.ui.ancillary_data_checkBox.setCheckState(2)
			self.checkAll = 'No'
		else:
			for i in range(1, 14):
				t = 'cfg.ui.checkBoxs_band_' + str(i) + '.setCheckState(0)'
				eval(t)
			cfg.ui.ancillary_data_checkBox.setCheckState(0)
			self.checkAll = 'Yes'
			
	# check all bands
	def checkAllBandsSentinel3(self):
		if self.checkAll == 'Yes':
			for i in range(1, 22):
				t = 'cfg.ui.checkBoxs3_band_' + str(i) + '.setCheckState(2)'
				eval(t)
			cfg.ui.s3_ancillary_data_checkBox.setCheckState(2)
			self.checkAll = 'No'
		else:
			for i in range(1, 22):
				t = 'cfg.ui.checkBoxs3_band_' + str(i) + '.setCheckState(0)'
				eval(t)
			cfg.ui.s3_ancillary_data_checkBox.setCheckState(0)
			self.checkAll = 'Yes'
			
	# check all bands
	def checkAllBandsGOES(self):
		if self.checkAll == 'Yes':
			for i in range(1, 7):
				t = 'cfg.ui.checkBoxs_goes_band_' + str(i) + '.setCheckState(2)'
				eval(t)
			self.checkAll = 'No'
		else:
			for i in range(1, 7):
				t = 'cfg.ui.checkBoxs_goes_band_' + str(i) + '.setCheckState(0)'
				eval(t)
			self.checkAll = 'Yes'
			
	# check band download
	def checkImageBands(self, checkbox, bandNumber, imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFilesList, linksList, checkDownload = None):
		if cfg.actionCheck == 'Yes':
			check = 'No'
			if checkbox.isChecked():
				# download from hub
				user = cfg.ui.user_scihub_lineEdit.text()
				password =cfg.ui.password_scihub_lineEdit.text()
				# check url
				topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
				topUrl =topLevelUrl + '/odata/v1/Products'
				topUrl2 =topLevelUrl
				urlL = []
				if imgName2[0:4] == 'L1C_':
					urlL.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('" + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + ".jp2')/$value")
					# download Sentinel data using the service https://storage.googleapis.com/gcp-public-data-sentinel-2
					urlL.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE' + '/GRANULE/' + imgName2 + '/IMG_DATA/' + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + '.jp2')
					outFile = cfg.tmpDir + '//' + imgName2.split('_')[1] + '_' + imgName.split('_')[2] + '_B' + bandNumber + '.jp2'
					outCopyFile = outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10] + '//L1C_' + imgName2[4:] + '_B' + bandNumber
				elif imgName2[0:4] == 'L2A_':
					if bandNumber in ['02', '03', '04', '08']:
						urlL.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('R10m')/Nodes('" + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + "_10m.jp2')/$value")
						urlL.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE' + '/GRANULE/' + imgName2 + '/IMG_DATA/R10m/' + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + '_10m.jp2')
						outFile = cfg.tmpDir + '//' + imgName2.split('_')[1] + '_' + imgName.split('_')[2] + '_B' + bandNumber + '.jp2'
						outCopyFile = outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10] + '//' + imgName2[4:] + '_B' + bandNumber
					elif bandNumber in ['05', '06', '07', '11', '12', '8A']:
						urlL.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('R20m')/Nodes('" + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + "_20m.jp2')/$value")
						urlL.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE' + '/GRANULE/' + imgName2 + '/IMG_DATA/R20m/' + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + '_20m.jp2')
						outFile = cfg.tmpDir + '//' + imgName2.split('_')[1] + '_' + imgName.split('_')[2] + '_B' + bandNumber + '.jp2'
						outCopyFile = outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10] + '//' + imgName2[4:] + '_B' + bandNumber
					elif bandNumber in ['01', '09']:
						urlL.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('R60m')/Nodes('" + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + "_60m.jp2')/$value")
						urlL.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE' + '/GRANULE/' + imgName2 + '/IMG_DATA/R60m/' + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + '_60m.jp2')
						outFile = cfg.tmpDir + '//' + imgName2.split('_')[1] + '_' + imgName.split('_')[2] + '_B' + bandNumber + '.jp2'
						outCopyFile = outputDirectory + '//' + imgName2 + '_' + acquisitionDate[0:10] + '//' + imgName2[4:] + '_B' + bandNumber
					else:
						return
				else:
					urlL.append(topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('" + imgName2[0:-7] + '_B' + bandNumber + ".jp2')/$value")
					urlL.append('https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + imgName[39:41] + '/'+  imgName[41]  + '/'+ imgName[42:44] + '/' +imgName + '.SAFE' + '/GRANULE/' + imgName2 + '/IMG_DATA/' + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + '.jp2')
					outFile = cfg.tmpDir + '//' + imgName2[0:-7] + '_B' + bandNumber + '.jp2'
					outCopyFile = outputDirectory + '//' + imgName2[0:-7]  + '_' + acquisitionDate[0:10] + '//' + imgName2[0:-7] + '_B' + bandNumber
				if exporter == 'No':
					if checkDownload == 'Yes':
						check = cfg.utls.downloadFile(urlL[1], outFile, None, progress)
					else:
						check = self.downloadFileSentinel2(urlL[0], outFile, progress)
					if cfg.osSCP.path.isfile(outFile):
						outFilesList.append([outFile, outCopyFile])
					else:
						cfg.mx.msgWar23(imgName2[0:-7] + '_B' + bandNumber + '.jp2')
				else:
					if checkDownload == 'Yes':
						linksList.append(urlL[1])
					else:
						linksList.append(urlL[0])
		else:
			cfg.uiUtls.removeProgressBar()
			return 'No'
	
	# download image preview
	def downloadThumbnailSentinel2(self, imgID, min_lat, min_lon, max_lat, max_lon, imageJPG, progress = None, preview = 'No'):
		imOut = cfg.tmpDir + '//' + imgID
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl = topLevelUrl
		check = cfg.utls.passwordConnectPython(user, password, imageJPG, topLevelUrl, imOut, progress, quiet = 'Yes')
		if check == 'Yes':
			if preview == 'Yes':
				self.previewInLabel(imOut)
				return imOut
			self.onflyGeorefImage(cfg.tmpDir + '//' + imgID, cfg.tmpDir + '//' + imgID + '.vrt', min_lon, max_lon, min_lat, max_lat)
		else:
			# second try
			topLevelUrl = 'https://scihub.copernicus.eu/dhus'
			imageJPG = imageJPG.replace(topUrl, topLevelUrl)
			check = cfg.utls.passwordConnectPython(user, password, imageJPG, topLevelUrl, imOut, progress)
			if check == 'Yes':
				if preview == 'Yes':
					self.previewInLabel(imOut)
					return imOut
				self.onflyGeorefImage(cfg.tmpDir + '//' + imgID, cfg.tmpDir + '//' + imgID + '.vrt', min_lon, max_lon, min_lat, max_lat)
			else:
				cfg.mx.msgErr40()
			
	# georef image on the fly based on UL and LR
	def onflyGeorefImage(self, inputImage, outputVRT, min_lon, max_lon, min_lat, max_lat):
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
		UL = cfg.qgisCoreSCP.QgsPointXY(float(min_lon), float(max_lat))
		LR = cfg.qgisCoreSCP.QgsPointXY(float(max_lon), float(min_lat))
		# WGS84 EPSG 4326
		wgsCrs = cfg.qgisCoreSCP.QgsCoordinateReferenceSystem()
		wgsCrs.createFromProj4('+proj=longlat +datum=WGS84 +no_defs')
		iCrs = cfg.qgisCoreSCP.QgsCoordinateReferenceSystem()
		iCrs.createFromProj4('+proj=utm +zone=' + str(zone) + ' +datum=WGS84 +units=m +no_defs')
		UL1 = cfg.utls.projectPointCoordinates(UL, wgsCrs, iCrs)
		LR1 = cfg.utls.projectPointCoordinates(LR, wgsCrs, iCrs)
		if UL1 != False and LR1 != False:
			cfg.utls.getGDALForMac()
			# georeference thumbnail
			a = cfg.gdalPath + 'gdal_translate -of VRT -a_ullr ' + str(UL1.x()) + ' ' + str(UL1.y()) + ' ' + str(LR1.x()) + ' ' + str(LR1.y()) + ' -a_srs "+proj=utm +zone=' + str(zone) + ' +datum=WGS84 +units=m +no_defs" ' + inputImage + ' ' + outputVRT
			if cfg.sysSCPNm != 'Windows':
				a = cfg.shlexSCP.split(a)
			try:
				if cfg.sysSCPNm == 'Windows':
					startupinfo = cfg.subprocessSCP.STARTUPINFO()
					startupinfo.dwFlags = cfg.subprocessSCP.STARTF_USESHOWWINDOW
					startupinfo.wShowWindow = cfg.subprocessSCP.SW_HIDE
					sP = cfg.subprocessSCP.Popen(a, shell=False, startupinfo = startupinfo, stdin = cfg.subprocessSCP.DEVNULL)
				else:
					sP = cfg.subprocessSCP.Popen(a, shell=False)
				sP.wait()
			# in case of errors
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' onfly georef' + str(inputImage))
		else:
			cfg.mx.msgErr41()
	
### Sentinel-1

	# read database S1
	def queryDatabaseSentinel1(self):
		QdateFrom = cfg.ui.dateEdit_from.date()
		QdateTo = cfg.ui.dateEdit_to.date()
		dateFrom = QdateFrom.toPyDate().strftime('%Y-%m-%d') 
		dateTo = QdateTo.toPyDate().strftime('%Y-%m-%d') 
		maxCloudCover = int(cfg.ui.cloud_cover_spinBox.value())
		resultNum = int(cfg.ui.result_number_spinBox_2.value())
		sat = cfg.ui.landsat_satellite_combo.currentText()
		imageFindList = []
		m = 'GRD'
		if len(cfg.ui.imageID_lineEdit.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit.text()
			imgIDLineSplit = str(imgIDLine).replace(' ', '').split(';')
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(' ', '').split(',')
			for m in imgIDLineSplit:
				imageFindList.append(m.lower())
			imgQuery = 'GRD'
			if len(imageFindList) == 1:
				imgQuery = '*' + m + '*'
		else:
			imageFindList.append('s1')
			imgQuery = 'GRD'
		try:
			NoRect = 'No'
			rubbRect = cfg.qgisCoreSCP.QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
			if abs(float(cfg.ui.UX_lineEdit_3.text()) - float(cfg.ui.LX_lineEdit_3.text())) > 10 or abs(float(cfg.ui.UY_lineEdit_3.text()) - float(cfg.ui.LY_lineEdit_3.text())) > 10:
				cfg.mx.msgWar18()
		except Exception as err:
			if len(imageFindList) == 1:
				imgQuery = m + '*'
				NoRect = 'Yes'
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				cfg.mx.msg23()
				return 'No'
		cfg.uiUtls.addProgressBar()
		tW = cfg.ui.download_images_tableWidget
		cfg.uiUtls.updateBar(30, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
		cfg.QtWidgetsSCP.qApp.processEvents()
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		imageTableList = []
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl
		# loop for results
		maxResultNum = resultNum
		if maxResultNum > 100:
			maxResultNum = 100
		imgQuery = '(%20(platformname:Sentinel-1%20AND%20producttype:GRD))'
		for startR in range(0, resultNum, maxResultNum):
			if NoRect == 'Yes':
				url = topUrl + '/search?q=' + imgQuery + '%20AND%20beginPosition:[' + str(dateFrom) + 'T00:00:00.000Z%20TO%20' + str(dateTo) + 'T23:59:59.999Z]' + '&rows=' + str(maxResultNum) + '&start=' + str(startR)
			else:
				url = topUrl + '/search?q=' + imgQuery + '%20AND%20beginPosition:[' + str(dateFrom) + 'T00:00:00.000Z%20TO%20' + str(dateTo) + 'T23:59:59.999Z]%20AND%20footprint:%22Intersects(POLYGON((' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ',' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.LY_lineEdit_3.text() + ',' + cfg.ui.LX_lineEdit_3.text() + '%20' + cfg.ui.LY_lineEdit_3.text() + ',' + cfg.ui.LX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ',' + cfg.ui.UX_lineEdit_3.text() + '%20' + cfg.ui.UY_lineEdit_3.text() + ')))%22' + '&rows=' + str(maxResultNum) + '&start=' + str(startR)
			response = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl, quiet = 'Yes')
			if response == 'No':
				# second try
				topLevelUrl = 'https://scihub.copernicus.eu/dhus'
				url = url.replace(topUrl, topLevelUrl)
				topUrl =topLevelUrl
				response = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl)
				if response == 'No':
					cfg.uiUtls.removeProgressBar()
					return 'No'
			#info = response.info()
			xml = response.read()
			tW.setSortingEnabled(False)
			try:
				doc = cfg.minidomSCP.parseString(xml)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				if 'HTTP Status 500' in xml:
					cfg.mx.msgWar24()
				else:
					cfg.mx.msgErr40()
				cfg.uiUtls.removeProgressBar()
				return 'No'
			entries = doc.getElementsByTagName('entry')
			e = 0
			for entry in entries:
				if cfg.actionCheck == 'Yes':
					productType = 'S1GRD'
					e = e + 1
					cfg.uiUtls.updateBar(30 + e * int(70/len(entries)), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
					imgNameTag = entry.getElementsByTagName('title')[0]
					imgName = imgNameTag.firstChild.data
					imgIDTag = entry.getElementsByTagName('id')[0]
					imgID = imgIDTag.firstChild.data
					summary = entry.getElementsByTagName('summary')[0]
					infos = summary.firstChild.data.split(',')
					for info in infos:
						infoIt = info.strip().split(' ')
						if infoIt[0] == 'Date:':
							acqDateI = infoIt[1]
						# if infoIt[0] == 'Satellite:':
							# print 'Satellite ' + infoIt[1]
						if infoIt[0] == 'Size:':
							size = infoIt[1] + ' ' + infoIt[2]
					strings = entry.getElementsByTagName('str')
					for x in strings:
						attr = x.getAttribute('name')
						if attr == 'producttype':
							productType = x.firstChild.data
						if attr == 'footprint':
							footprintCoord = x.firstChild.data.replace('MULTIPOLYGON (((', '').replace('POLYGON ((', '').replace(')))', '').replace('))', '').split(',')
							xList = []
							yList = []
							for coords in footprintCoord:
								cc = coords.lstrip()
								xList.append(float(cc.split(' ')[0]))
								yList.append(float(cc.split(' ')[1]))
							min_lon = min(xList)
							max_lon = max(xList)
							min_lat = min(yList)
							max_lat = max(yList)
					url2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('manifest.safe')/$value"
					if cfg.actionCheck == 'Yes':
						response2 = cfg.utls.passwordConnectPython(user, password, url2, topLevelUrl, None, None, quiet = 'No')
						try:
							xml2 = response2.read()
						except:
							xml2 = response2
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' xml downloaded' )
					if cfg.actionCheck == 'Yes':
						try:						
							for filter in imageFindList:
								if filter in imgName.lower():
									doc2 = cfg.minidomSCP.parseString(xml2)
									entries2 = doc2.getElementsByTagName('s1:pass')
									for entry2 in entries2:
										orbit = entry2.firstChild.data
									entries2 = doc2.getElementsByTagName('safe:relativeOrbitNumber')
									for entry2 in entries2:
										relativeOrbit = entry2.firstChild.data
									try:
										entries3 = doc2.getElementsByTagName('s1sarl1:sliceNumber')
										for entry3 in entries3:
											sliceNumber = entry3.firstChild.data
									except:
										sliceNumber = ''
									try:
										entries4 = doc2.getElementsByTagName('safe:number')
										for entry4 in entries4:
											satelliteN = entry4.firstChild.data
									except:
										satelliteN = ""
									# add item to table
									c = tW.rowCount()
									# add list items to table
									tW.setRowCount(c + 1)
									imgPreview = topUrl + "/odata/v1/Products('" +  imgID + "')/Products('Quicklook')/$value"
									cfg.utls.addTableItem(tW, sat, c, 0)
									cfg.utls.addTableItem(tW, imgName, c, 1)
									cfg.utls.addTableItem(tW, acqDateI, c, 2)
									cfg.utls.addTableItem(tW, orbit, c, 3)
									cfg.utls.addTableItem(tW, satelliteN + 'o' + relativeOrbit, c, 4)
									cfg.utls.addTableItem(tW, satelliteN + 's' + sliceNumber, c, 5)
									cfg.utls.addTableItem(tW, float(min_lat), c, 6)
									cfg.utls.addTableItem(tW, float(min_lon), c, 7)
									cfg.utls.addTableItem(tW, float(max_lat), c, 8)
									cfg.utls.addTableItem(tW, float(max_lon), c, 9)
									cfg.utls.addTableItem(tW, size, c, 10)
									cfg.utls.addTableItem(tW, imgPreview, c, 11)
									cfg.utls.addTableItem(tW, imgID, c, 12)
									cfg.utls.addTableItem(tW, imgName, c, 13)
									break
						except Exception as err:
							for filter in imageFindList:
								if filter in imgName.lower():
									# add item to table
									c = tW.rowCount()
									co = cfg.QtGuiSCP.QColor(160, 160, 160)
									# add list items to table
									tW.setRowCount(c + 1)
									cfg.utls.addTableItem(tW, sat, c, 0, 'Yes', co)
									cfg.utls.addTableItem(tW, imgName, c, 1, 'Yes', co)
									cfg.utls.addTableItem(tW, acqDateI, c, 2, 'Yes', co)
									cfg.utls.addTableItem(tW, '', c, 3, 'Yes', co)
									cfg.utls.addTableItem(tW, '', c, 4, 'Yes', co)
									cfg.utls.addTableItem(tW, '', c, 5, 'Yes', co)
									cfg.utls.addTableItem(tW, float(min_lat), c, 6, 'Yes', co)
									cfg.utls.addTableItem(tW, float(min_lon), c, 7, 'Yes', co)
									cfg.utls.addTableItem(tW, float(max_lat), c, 8, 'Yes', co)
									cfg.utls.addTableItem(tW, float(max_lon), c, 9, 'Yes', co)
									cfg.utls.addTableItem(tW, size, c, 10, 'Yes', co)
									cfg.utls.addTableItem(tW, '', c, 11, 'Yes', co)
									cfg.utls.addTableItem(tW, imgID, c, 12, 'Yes', co)
									cfg.utls.addTableItem(tW, imgName, c, 13, 'Yes', co)
									# logger
									cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
									break
		tW.setSortingEnabled(True)		
		cfg.uiUtls.removeProgressBar()
		self.clearCanvasPoly()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Sentinel images")
		
	# display granule preview	
	def displayGranulesSentinel1(self, row, progress, preview = 'No'):
		i = row
		tW = cfg.ui.download_images_tableWidget
		imgNm = str(tW.item(i, 1).text())
		acquisitionDate = str(tW.item(i, 2).text())
		imgID = imgNm + '_p.jpg'
		url = str(tW.item(i, 11).text())
		# image preview
		imOut = cfg.tmpDir + '//' + imgID
		if preview == 'Yes' and cfg.osSCP.path.isfile(imOut):
			self.previewInLabel(imOut)
			return imOut
		if cfg.osSCP.path.isfile(imOut  + '.vrt'):
			l = cfg.utls.selectLayerbyName(imgID)
			if l is not None:		
				cfg.utls.setLayerVisible(l, True)
				cfg.utls.moveLayerTop(l)
			else:
				r =cfg.utls.addRasterLayer(imOut, imgID)
		else:
			min_lat = str(tW.item(i, 6).text())
			min_lon = str(tW.item(i, 7).text())
			max_lat = str(tW.item(i, 8).text())
			max_lon = str(tW.item(i, 9).text())
			self.downloadThumbnailSentinel1(imgID, min_lat, min_lon, max_lat, max_lon, url, progress, preview)
			if cfg.osSCP.path.isfile(imOut + '.vrt'):
				r =cfg.utls.addRasterLayer(imOut + '.vrt', imgID)
				cfg.utls.setRasterColorComposite(r, 1, 2, 3)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' granules displayed')
	
	# download image preview
	def downloadThumbnailSentinel1(self, imgID, min_lat, min_lon, max_lat, max_lon, imageJPG, progress = None, preview = 'No'):
		imOut = cfg.tmpDir + '//' + imgID
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl
		check = cfg.utls.passwordConnectPython(user, password, imageJPG, topLevelUrl, imOut, progress, quiet = 'Yes')
		if check == 'Yes':
			if preview == 'Yes':
				self.previewInLabel(imOut)
				return imOut
			self.onflyGeorefImage(cfg.tmpDir + '//' + imgID, cfg.tmpDir + '//' + imgID + '.vrt', min_lon, max_lon, min_lat, max_lat)
		else:
			# second try
			topLevelUrl = 'https://scihub.copernicus.eu/dhus'
			imageJPG = imageJPG.replace(topUrl, topLevelUrl)
			check = cfg.utls.passwordConnectPython(user, password, imageJPG, topLevelUrl, imOut, progress)
			if check == 'Yes':
				if preview == 'Yes':
					self.previewInLabel(imOut)
					return imOut
				self.onflyGeorefImage(cfg.tmpDir + '//' + imgID, cfg.tmpDir + '//' + imgID + '.vrt', min_lon, max_lon, min_lat, max_lat)
			else:
				cfg.mx.msgErr40()
	
	# download images
	def downloadSentinel1Images(self, outputDirectory, exporter = 'No'):
		cfg.uiUtls.addProgressBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'), message = '')
		tW = cfg.ui.download_images_tableWidget
		outDirList = []
		imgList = []
		links = []
		c = tW.rowCount()
		progressStep = 100 / c
		progress = 0
		# disable map canvas render for speed
		cfg.cnvs.setRenderFlag(False)
		outFiles = []
		for i in range(0, c):
			sat = str(tW.item(i, 0).text())
			if cfg.actionCheck == 'Yes':
				if sat == cfg.esaSentinel1:
					imgName = str(tW.item(i, 13).text())
					acquisitionDate = str(tW.item(i, 2).text())
					orbit = str(tW.item(i, 3).text())
					relativeOrbit = str(tW.item(i, 4).text())
					sliceNumber = str(tW.item(i, 5).text())
					imgID = str(tW.item(i, 12).text())
					imgJp2 = imgName + '_p.jpg'
					if cfg.ui.download_if_preview_in_legend_checkBox.isChecked() and cfg.utls.selectLayerbyName(imgJp2, 'Yes') is None:
						pass
					else:
						# add info to name
						imgName = imgName.replace('.zip', '') + '_s' + orbit[0] + '_' + relativeOrbit + '_' + sliceNumber + '_' + acquisitionDate[0:10] 
						outDirList.append(outputDirectory + '//' + imgName)
						progress = progress + progressStep
						if exporter == 'No':
							oDir = cfg.utls.makeDirectory(outputDirectory + '//' + imgName)
							if oDir is None:
								cfg.mx.msgErr58()
								cfg.uiUtls.removeProgressBar()
								cfg.cnvs.setRenderFlag(True)
								return 'No'
						# download ancillary data
						if cfg.ui.ancillary_data_checkBox.isChecked():
							pass
						# download bands
						self.checkImageS1Bands(None, None, imgID, imgName, None, acquisitionDate,outputDirectory + '//' + imgName, exporter, progress, outFiles, links)
						for oFile in outFiles:
							cfg.shutilSCP.copy(oFile[0], oFile[1])
							cfg.osSCP.remove(oFile[0])
			else:
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
				return 'No'
		if cfg.ui.preprocess_checkBox.isChecked() and exporter == 'No':
			n = len(outFiles)
			i = 0
			for oFile in outFiles:
				if cfg.actionCheck == 'Yes':
					d = oFile[1]
					o = oFile[2] + '_con'
					i = i + 1
					cfg.uiUtls.updateBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Processing') + ' [' + str(i) + '/' + str(n) + '] ' + cfg.osSCP.path.basename(d), message = '')
					oDir = cfg.utls.makeDirectory(o)
					if oDir is None:
						cfg.mx.msgErr58()
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
						return 'No'
					cfg.sentinel1T.sentinel1(d, o, 'Yes')
		cfg.uiUtls.removeProgressBar()
		cfg.cnvs.setRenderFlag(True)
		return links
		
	# check band download
	def checkImageS1Bands(self, checkbox, bandNumber, imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFilesList, linksList):
		if cfg.actionCheck == 'Yes':
			# download from hub
			user = cfg.ui.user_scihub_lineEdit.text()
			password =cfg.ui.password_scihub_lineEdit.text()
			# check url
			topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
			topUrl =topLevelUrl + '/odata/v1/Products'
			topUrl2 =topLevelUrl
			urlL = topUrl + "('" +imgID  + "')/$value"
			outFile = cfg.tmpDir + '//' + imgName + '.zip'
			outCopyFile = outputDirectory + '//' + imgName + '.zip'
			if exporter == 'No':
				self.downloadFileSentinel1(urlL, outFile, progress)
				try:
					if cfg.osSCP.path.getsize(outFile) < 100000:
						self.downloadFileSentinel1(urlL, outFile, progress)
						if cfg.osSCP.path.getsize(outFile) < 100000:
							cfg.mx.msgWar23(imgName)
					outFilesList.append([outFile, outCopyFile, outputDirectory])
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			else:
				linksList.append(urlL)
		else:
			cfg.uiUtls.removeProgressBar()
			return 'No'
			
	# download file
	def downloadFileSentinel1(self, url, output, progress = None):
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ' + url)
		check = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl, output, progress, quiet = 'Yes')
		if check == 'Yes':
			return output
		else:
			# second try
			topLevelUrl = 'https://scihub.copernicus.eu/dhus'
			url = url.replace(topUrl, topLevelUrl)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ' + url)
			check = cfg.utls.passwordConnectPython(user, password, url, topLevelUrl, output, progress)
			if check == 'Yes':
				return output
			else:
				cfg.mx.msgErr40()
				return 'No'
			
### ASTER

	# download image metadata from NASA CMR Search https://cmr.earthdata.nasa.gov/search/site/search_api_docs.html
	def downloadMetadataASTER(self):
		listImgID = []
		QdateFrom = cfg.ui.dateEdit_from.date()
		QdateTo = cfg.ui.dateEdit_to.date()
		dateFrom = QdateFrom.toPyDate().strftime('%Y-%m-%d') 
		dateTo = QdateTo.toPyDate().strftime('%Y-%m-%d') 
		maxCloudCover = int(cfg.ui.cloud_cover_spinBox.value())
		resultNum = int(cfg.ui.result_number_spinBox_2.value())
		sat = cfg.ui.landsat_satellite_combo.currentText()
		if sat == cfg.usgsASTER:
			NASAcollection = cfg.NASAASTERCollection
		imageFindList = []
		if len(cfg.ui.imageID_lineEdit.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit.text()
			imgIDLineSplit = str(imgIDLine).replace(' ', '').split(';')
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(' ', '').split(',')
			for m in imgIDLineSplit:
				imageFindList.append(m.lower())
		try:
			rubbRect = cfg.qgisCoreSCP.QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg23()
			return 'No'
		try:
			cfg.uiUtls.addProgressBar()
			cfg.QtWidgetsSCP.qApp.processEvents()
			tW = cfg.ui.download_images_tableWidget
			tW.setSortingEnabled(False)
			cfg.uiUtls.updateBar(30, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
			searchUrl = 'https://cmr.earthdata.nasa.gov/search/granules.echo10?bounding_box=' + cfg.ui.UX_lineEdit_3.text() + '%2C' + cfg.ui.LY_lineEdit_3.text() + '%2C' + cfg.ui.LX_lineEdit_3.text() + '%2C' + cfg.ui.UY_lineEdit_3.text() + '&echo_collection_id=' + NASAcollection + '&temporal=' + dateFrom + '%2C' + dateTo + 'T23%3A59%3A59.000Z&cloud_cover=0,' + str(maxCloudCover) + '&sort_key%5B%5D=-start_date&page_size=' + str(resultNum) + '&pretty=true'
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
				cfg.uiUtls.updateBar(30 + int(page * 70 / pages), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
				gId = entry.getElementsByTagName('ProducerGranuleId')[0]
				imgID = gId.firstChild.data
				if imgID not in imgIDList:
					imgIDList.append(imgID)
					imgDispID = imgID
					cc = entry.getElementsByTagName('QAPercentCloudCover')[0]
					cloudCover = cc.firstChild.data
					on = entry.getElementsByTagName('OnlineResources')
					urls = on[0].getElementsByTagName('URL')
					imgPreview = ''
					for ur in urls:
						url = ur.firstChild.data
						if '.jpg' in url:
							imgPreview = url
							break
					dt = entry.getElementsByTagName('SingleDateTime')[0]
					imgDate = dt.firstChild.data
					imgDate = cfg.datetimeSCP.datetime.strptime(imgDate[0:19], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
					PointLatitude = entry.getElementsByTagName('PointLatitude')
					lat = []
					for latit in PointLatitude:
						lat.append(float(latit.firstChild.data))
					PointLongitude = entry.getElementsByTagName('PointLongitude')
					lon = []
					for longi in PointLongitude:
						lon.append(float(longi.firstChild.data))
					DayNightFlag = entry.getElementsByTagName('DayNightFlag')[0]
					dayNight = DayNightFlag.firstChild.data
					listImgID.append([imgID, imgDate, cloudCover, imgDispID, dayNight, lon, lat, imgPreview.replace('http:', 'https:')])
			cfg.uiUtls.updateBar(100, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
			c = tW.rowCount()
			for imID in listImgID:
				if len(imageFindList) > 0:
					for iF in imageFindList:
						if iF in imID[0].lower():
							imgCheck = 'Yes'
							break
						else:
							imgCheck = 'No'
				else:
					imgCheck = 'Yes'
				if imgCheck == 'Yes':
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, sat, c, 0)					
					cfg.utls.addTableItem(tW, imID[3], c, 1)
					cfg.utls.addTableItem(tW, str(imID[1]), c, 2)
					cfg.utls.addTableItem(tW, int(round(float(imID[2]))), c, 3)
					cfg.utls.addTableItem(tW, "", c, 4)
					cfg.utls.addTableItem(tW, imID[4], c, 5)
					min_lon = min(imID[5])
					max_lon = max(imID[5])
					min_lat = min(imID[6])
					max_lat = max(imID[6])
					cfg.utls.addTableItem(tW, float(min_lat), c, 6)
					cfg.utls.addTableItem(tW, float(min_lon), c, 7)
					cfg.utls.addTableItem(tW, float(max_lat), c, 8)
					cfg.utls.addTableItem(tW,float(max_lon), c, 9)
					cfg.utls.addTableItem(tW,'EOSDIS Earthdata', c, 10)
					cfg.utls.addTableItem(tW, imID[7], c, 11)
					cfg.utls.addTableItem(tW, NASAcollection, c, 12)
					cfg.utls.addTableItem(tW, imID[0], c, 13)
			tW.setSortingEnabled(True)	
			cfg.uiUtls.removeProgressBar()
			self.clearCanvasPoly()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ASTER images')
			c = tW.rowCount()
			if c == 0:
				cfg.mx.msg21()
		except Exception as err:
			cfg.mx.msgErr39()
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
	
	# user
	def rememberUserEarthdata(self):
		if cfg.ui.remember_user_checkBox_3.isChecked():
			user = cfg.ui.user_usgs_lineEdit_2.text()
			pswd = cfg.utls.encryptPassword(cfg.ui.password_usgs_lineEdit_2.text())
			cfg.utls.setQGISRegSetting(cfg.regUSGSUserASTER, user)
			cfg.utls.setQGISRegSetting(cfg.regUSGSPassASTER, pswd)
			
	def rememberUserCheckboxEarthdata(self):
		if cfg.ui.remember_user_checkBox_3.isChecked():
			self.rememberUserEarthdata()
		else:
			cfg.utls.setQGISRegSetting(cfg.regUSGSUserASTER, "")
			cfg.utls.setQGISRegSetting(cfg.regUSGSPassASTER, "")
			
		
	# download ASTER data
	def downloadASTERImages(self, outputDirectory, exporter = 'No'):
		cfg.uiUtls.addProgressBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'), message = '')
		tW = cfg.ui.download_images_tableWidget
		c = tW.rowCount()
		progressStep = 100 / c
		progressStep2 = progressStep/12
		progress = 0
		outDirList = []
		outFileList = []
		imgList = []
		links = []		
		for i in range(0, c):
			sat = str(tW.item(i, 0).text())
			if cfg.actionCheck == 'Yes':
				if sat in cfg.satASTERtList:
					imgID = str(tW.item(i, 13).text())
					imgDispID = str(tW.item(i, 1).text())
					date = str(tW.item(i, 2).text())[0:10]
					if cfg.ui.download_if_preview_in_legend_checkBox.isChecked() and cfg.utls.selectLayerbyName(imgDispID, 'Yes') is None:
						pass
					else:
						NASAcollection = str(tW.item(i, 12).text())
						outDir = outputDirectory + '/' + imgDispID
						if exporter == 'No':
							oDir = cfg.utls.makeDirectory(outDir)
							if oDir is None:
								cfg.mx.msgErr58()
								cfg.uiUtls.removeProgressBar()
								return 'No'
						outDirList.append(outDir)
						outFileList.append(outDir + '//' + imgDispID + '.hdf')
						progress = progress + progressStep
						outUrl = self.downloadASTERImagesFromNASA(imgID, NASAcollection, imgDispID, outDir, progress, exporter, date)
						links.append(outUrl)
			else:
				cfg.uiUtls.removeProgressBar()
				return 'No'
		if exporter == 'Yes':
			return links
		else:
			cfg.cnvs.setRenderFlag(False)
			if cfg.ui.preprocess_checkBox.isChecked():
				n = len(outFileList)
				i = 0
				for d in outFileList:
					i = i + 1
					cfg.uiUtls.updateBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Processing') + ' [' + str(i) + '/' + str(n) + '] ' + cfg.osSCP.path.basename(d), message = '')
					if cfg.actionCheck == 'Yes':
						cfg.ASTERT.populateTable(d, 'Yes')
						o = d + '_converted'
						oDir = cfg.utls.makeDirectory(o)
						cfg.ASTERT.ASTER(d, o, 'Yes')
			elif cfg.ui.load_in_QGIS_checkBox.isChecked():
				for d in outDirList:
					try:
						for f in cfg.osSCP.listdir(d):
							if f.lower().endswith('.tif'):
								r =cfg.utls.addRasterLayer(d + '/' + f)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			
	# download image
	def downloadASTERImagesFromNASA(self, imageID, collection, imageDisplayID, outputDirectory, progress, exporter = 'No', date = None):
		# The ASTER L1T data products are retrieved from the online Data Pool, courtesy of the NASA Land Processes Distributed Active Archive Center (LP DAAC), USGS/Earth Resources Observation and Science (EROS) Center, Sioux Falls, South Dakota, https://lpdaac.usgs.gov/data_access/data_pool'
		url = 'https://e4ftl01.cr.usgs.gov/ASTT/AST_L1T.003/' + date.replace('-', '.')+ '/' + imageDisplayID + '.hdf'
		if exporter == 'Yes':
			return url
		else:
			user = cfg.ui.user_usgs_lineEdit_2.text()
			password =cfg.ui.password_usgs_lineEdit_2.text()
			try:
				imgID = imageDisplayID + '.hdf'
				check = cfg.utls.passwordConnectPython(user, password, url, 'urs.earthdata.nasa.gov', cfg.tmpDir + '//' + imgID, progress)
				if str(check) == 'Cancel action':
					return check
				if cfg.osSCP.path.getsize(cfg.tmpDir + '//' + imgID) > 10000:
					if collection == cfg.NASAASTERCollection:
						cfg.shutilSCP.copy(cfg.tmpDir + '//' + imgID, outputDirectory + '//' + imgID)
						cfg.osSCP.remove(cfg.tmpDir + '//' + imgID)
					else:
						tarFiles = cfg.tarfileSCP.open(cfg.tmpDir + '//' + imgID, 'r:gz')
						tarFiles.extractall(outputDirectory)
						tarFiles.close()
						cfg.osSCP.remove(cfg.tmpDir + '//' + imgID)
						return url
				else:
					cfg.mx.msgErr55(imgID)
					return 'No'
			except Exception as err:
				cfg.mx.msgErr55(imgID)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
	
### GOES

	# download image metadata from Amazon Web Services https://registry.opendata.aws/noaa-goes/
	def downloadMetadataGOES(self):
		QdateFrom = cfg.ui.dateEdit_from.date()
		dStrT = QdateFrom.toPyDate().timetuple()
		# calculate julian day
		fromDay = dStrT.tm_yday
		fromYear = dStrT.tm_year
		QdateTo = cfg.ui.dateEdit_to.date()
		dStrTo = QdateTo.toPyDate().timetuple()
		# calculate julian day
		toDay = dStrTo.tm_yday
		toYear = dStrTo.tm_year
		if fromYear != toYear:
			cfg.mx.msgWar34()
		resultNum = int(cfg.ui.result_number_spinBox_2.value())
		sat = cfg.ui.landsat_satellite_combo.currentText()
		if sat == cfg.goes16:
			goesCol = 'https://noaa-goes16.s3.amazonaws.com'
		elif sat == cfg.goes17:
			goesCol = 'https://noaa-goes17.s3.amazonaws.com'
		imageFindList = []
		if len(cfg.ui.imageID_lineEdit.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit.text()
			imgIDLineSplit = str(imgIDLine).replace(' ', '').split(';')
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(' ', '').split(',')
			for m in imgIDLineSplit:
				imageFindList.append(m.lower())
		else:
			imageFindList.append('l1b')
		cfg.uiUtls.addProgressBar()
		cfg.QtWidgetsSCP.qApp.processEvents()
		tW = cfg.ui.download_images_tableWidget
		tW.setSortingEnabled(False)
		cfg.uiUtls.updateBar(30, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
		# iterat days
		dCount = 0
		for day in range(fromDay, toDay + 1):
			if cfg.actionCheck == 'Yes':
				dCount = dCount + 1
				if dCount < resultNum:
					# iterate hours
					for hour in range(0, 24):
						if cfg.actionCheck == 'Yes':
							cfg.uiUtls.updateBar(30 + int(hour * 70 / 24), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ... [day ' + str(day) + ']'))
							searchUrl = goesCol + '/?list-type=2&delimiter=/&prefix=ABI-L1b-RadF/' + str(fromYear) + '/' + str(day).zfill(3) + '/' + str(hour).zfill(2) + '/'
							# connect and search
							xml2T = cfg.utls.createTempRasterPath('xml')
							searchResult = cfg.utls.downloadFile(searchUrl, xml2T)
							xmlFile = open(xml2T, 'r').read()
							imgIDList = []
							doc = cfg.minidomSCP.parseString(xmlFile)
							entries = doc.getElementsByTagName('Key')
							for entry in entries:
								if cfg.actionCheck == 'Yes':
									imgID = entry.firstChild.data
									if 'C01' in imgID:
										for imF in imageFindList:
											if imF in imgID.lower():
												c = tW.rowCount()
												inDate = cfg.datetimeSCP.datetime.strptime(imgID.split('_s')[1][0:13],  '%Y%j%H%M%S').strftime('%Y.%m.%dT%H_%M_%S')
												# add list items to table
												tW.setRowCount(c + 1)
												cfg.utls.addTableItem(tW, sat, c, 0)
												cfg.utls.addTableItem(tW, imgID.split('/')[-1], c, 1)
												cfg.utls.addTableItem(tW, str(inDate), c, 2)
												cfg.utls.addTableItem(tW, '', c, 3)
												cfg.utls.addTableItem(tW, '', c, 4)
												cfg.utls.addTableItem(tW, '', c, 5)
												cfg.utls.addTableItem(tW, '', c, 6)
												cfg.utls.addTableItem(tW, '', c, 7)
												cfg.utls.addTableItem(tW, '', c, 8)
												cfg.utls.addTableItem(tW, '', c, 9)
												cfg.utls.addTableItem(tW,'AWS', c, 10)
												cfg.utls.addTableItem(tW, '', c, 11)
												cfg.utls.addTableItem(tW, imgID.split('_s')[1][0:14], c, 12)
												cfg.utls.addTableItem(tW, searchUrl, c, 13)
		tW.setSortingEnabled(True)
		cfg.uiUtls.removeProgressBar()
		self.clearCanvasPoly()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' GOES images')
		c = tW.rowCount()
		if c == 0:
			cfg.mx.msg21()
			
	# download images
	def downloadGOESImages(self, outputDirectory, exporter = 'No'):
		cfg.uiUtls.addProgressBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'), message = '')
		tW = cfg.ui.download_images_tableWidget
		outDirList = []
		imgList = []
		links = []
		c = tW.rowCount()
		progressStep = 100 / c
		progress = 0
		# disable map canvas render for speed
		cfg.cnvs.setRenderFlag(False)
		for i in range(0, c):
			sat = str(tW.item(i, 0).text())
			if cfg.actionCheck == 'Yes':
				if sat == cfg.goes16 or sat == cfg.goes17:
					imgID = str(tW.item(i, 1).text())
					acquisitionDate = str(tW.item(i, 2).text())
					imgName2 = str(tW.item(i, 12).text())
					searchUrl = str(tW.item(i, 13).text())
					if cfg.ui.download_if_preview_in_legend_checkBox.isChecked():
						pass
					else:
						outFiles = []
						outDirList.append(outputDirectory + '//' + imgID[0:25]  + '_' + acquisitionDate)
						progress = progress + progressStep
						if exporter == 'No':
							oDir = cfg.utls.makeDirectory(outputDirectory + '//' + imgID[0:25]  + '_' + acquisitionDate)
							if oDir is None:
								cfg.mx.msgErr58()
								cfg.uiUtls.removeProgressBar()
								cfg.cnvs.setRenderFlag(True)
								return 'No'
						# download bands
						self.checkGOESImageBands(cfg.ui.checkBoxs_goes_band_1, '01', imgID, searchUrl, imgName2, acquisitionDate, outputDirectory + '//' + imgID[0:25]  + '_' + acquisitionDate, exporter, progress, outFiles, links)
						self.checkGOESImageBands(cfg.ui.checkBoxs_goes_band_2, '02', imgID, searchUrl, imgName2, acquisitionDate, outputDirectory + '//' + imgID[0:25]  + '_' + acquisitionDate, exporter, progress, outFiles, links)
						self.checkGOESImageBands(cfg.ui.checkBoxs_goes_band_3, '03', imgID, searchUrl, imgName2, acquisitionDate, outputDirectory + '//' + imgID[0:25]  + '_' + acquisitionDate, exporter, progress, outFiles, links)
						self.checkGOESImageBands(cfg.ui.checkBoxs_goes_band_4, '04', imgID, searchUrl, imgName2, acquisitionDate, outputDirectory + '//' + imgID[0:25]  + '_' + acquisitionDate, exporter, progress, outFiles, links)
						self.checkGOESImageBands(cfg.ui.checkBoxs_goes_band_5, '05', imgID, searchUrl, imgName2, acquisitionDate, outputDirectory + '//' + imgID[0:25]  + '_' + acquisitionDate, exporter, progress, outFiles, links)
						self.checkGOESImageBands(cfg.ui.checkBoxs_goes_band_6, '06', imgID, searchUrl, imgName2, acquisitionDate, outputDirectory + '//' + imgID[0:25]  + '_' + acquisitionDate, exporter, progress, outFiles, links)
						for oFile in outFiles:
							cfg.shutilSCP.copy(oFile[0], oFile[1])
							cfg.osSCP.remove(oFile[0])
			else:
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
				return 'No'
		if cfg.ui.preprocess_checkBox.isChecked() and exporter == 'No':
			n = len(outDirList)
			i = 0
			for d in outDirList:
				i = i + 1
				cfg.uiUtls.updateBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Processing') + ' [' + str(i) + '/' + str(n) + '] ' + cfg.osSCP.path.basename(d), message = '')
				if cfg.actionCheck == 'Yes':
					cfg.goesT.populateTable(d, 'Yes')
					o = d + "_con"
					oDir = cfg.utls.makeDirectory(o)
					if oDir is None:
						cfg.mx.msgErr58()
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
						return 'No'
					cfg.goesT.GOES(d, o, 'Yes')
		cfg.uiUtls.removeProgressBar()
		cfg.cnvs.setRenderFlag(True)
		return links
					
	# check band download
	def checkGOESImageBands(self, checkbox, bandNumber, imgName, searchUrl, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFilesList, linksList):
		if cfg.actionCheck == 'Yes':
			if checkbox.isChecked():
				# connect and search
				xml2T = cfg.utls.createTempRasterPath('xml')
				searchResult = cfg.utls.downloadFile(searchUrl, xml2T)
				xmlFile = open(xml2T, 'r').read()
				imgIDList = []
				doc = cfg.minidomSCP.parseString(xmlFile)
				entries = doc.getElementsByTagName('Key')
				for entry in entries:
					imgID = entry.firstChild.data
					if 'C' + str(bandNumber) in imgID and imgName2 in imgID:
						outFile = cfg.tmpDir + '//' + imgName[0:25] + '_' + acquisitionDate+ '_B' + bandNumber + '.nc'
						outCopyFile = outputDirectory + '//' + imgName[0:25]  + '_' + acquisitionDate + '_B' + bandNumber + '.nc'
						urlL = searchUrl.split('?')[0] + imgID
						if exporter == 'No':
							cfg.utls.downloadFile(urlL, outFile)
							outFilesList.append([outFile, outCopyFile])
						else:
							linksList.append(urlL)
		else:
			cfg.uiUtls.removeProgressBar()
			return 'No'
			
			
### MODIS

	# download image metadata from NASA CMR Search https://cmr.earthdata.nasa.gov/search/site/search_api_docs.html
	def downloadMetadataMODIS(self):
		listImgID = []
		QdateFrom = cfg.ui.dateEdit_from.date()
		QdateTo = cfg.ui.dateEdit_to.date()
		dateFrom = QdateFrom.toPyDate().strftime("%Y-%m-%d") 
		dateTo = QdateTo.toPyDate().strftime("%Y-%m-%d") 
		maxCloudCover = int(cfg.ui.cloud_cover_spinBox.value())
		resultNum = int(cfg.ui.result_number_spinBox_2.value())
		sat = cfg.ui.landsat_satellite_combo.currentText()
		if sat == cfg.usgsMODIS_MOD09GQ:
			NASAcollection = cfg.NASAMOD09GQCollection
		elif sat == cfg.usgsMODIS_MYD09GQ:
			NASAcollection = cfg.NASAMYD09GQCollection
		elif sat == cfg.usgsMODIS_MOD09GA:
			NASAcollection = cfg.NASAMOD09GACollection
		elif sat == cfg.usgsMODIS_MYD09GA:
			NASAcollection = cfg.NASAMYD09GACollection
		elif sat == cfg.usgsMODIS_MOD09Q1:
			NASAcollection = cfg.NASAMOD09Q1Collection
		elif sat == cfg.usgsMODIS_MYD09Q1:
			NASAcollection = cfg.NASAMYD09Q1Collection
		elif sat == cfg.usgsMODIS_MOD09A1:
			NASAcollection = cfg.NASAMOD09A1Collection
		elif sat == cfg.usgsMODIS_MYD09A1:
			NASAcollection = cfg.NASAMYD09A1Collection
		imageFindList = []
		if len(cfg.ui.imageID_lineEdit.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit.text()
			imgIDLineSplit = str(imgIDLine).replace(' ', '').split(';')
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(' ', '').split(',')
			for m in imgIDLineSplit:
				imageFindList.append(m.lower())
		try:
			rubbRect = cfg.qgisCoreSCP.QgsRectangle(float(cfg.ui.UX_lineEdit_3.text()), float(cfg.ui.UY_lineEdit_3.text()), float(cfg.ui.LX_lineEdit_3.text()), float(cfg.ui.LY_lineEdit_3.text()))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msg23()
			return 'No'
		try:
			cfg.uiUtls.addProgressBar()
			cfg.QtWidgetsSCP.qApp.processEvents()
			tW = cfg.ui.download_images_tableWidget
			tW.setSortingEnabled(False)
			cfg.uiUtls.updateBar(30, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
			# issue with cloud cover search
			#searchUrl = 'https://cmr.earthdata.nasa.gov/search/granules.echo10?bounding_box=' + cfg.ui.UX_lineEdit_3.text() + '%2C' + cfg.ui.LY_lineEdit_3.text() + '%2C' + cfg.ui.LX_lineEdit_3.text() + '%2C' + cfg.ui.UY_lineEdit_3.text() + '&echo_collection_id=' + NASAcollection + '&temporal=' + dateFrom + '%2C' + dateTo + 'T23%3A59%3A59.000Z&cloud_cover=0,' + str(maxCloudCover) + '&sort_key%5B%5D=-start_date&page_size=' + str(resultNum) + '&pretty=true'
			searchUrl = 'https://cmr.earthdata.nasa.gov/search/granules.echo10?bounding_box=' + cfg.ui.UX_lineEdit_3.text() + '%2C' + cfg.ui.LY_lineEdit_3.text() + '%2C' + cfg.ui.LX_lineEdit_3.text() + '%2C' + cfg.ui.UY_lineEdit_3.text() + '&echo_collection_id=' + NASAcollection + '&temporal=' + dateFrom + '%2C' + dateTo + 'T23%3A59%3A59.000Z&sort_key%5B%5D=-start_date&page_size=' + str(resultNum) + '&pretty=true'
			# connect and search
			searchResult = cfg.utls.NASASearch(searchUrl)
			xmlFile = searchResult.read()
			imgIDList = []
			doc = cfg.minidomSCP.parseString(xmlFile)
			entries = doc.getElementsByTagName('Granule')
			pages = len(entries)
			page = 0
			for entry in entries:
				page = page + 1
				cfg.uiUtls.updateBar(30 + int(page * 70 / pages), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
				gId = entry.getElementsByTagName('ProducerGranuleId')[0]
				imgID = gId.firstChild.data
				if imgID not in imgIDList:
					imgIDList.append(imgID)
					imgDispID = imgID.replace('.hdf', '')
					#cc = entry.getElementsByTagName("QAPercentCloudCover")[0]
					#cloudCover = cc.firstChild.data
					cloudCover = 0
					on = entry.getElementsByTagName('OnlineResources')
					url = on[0].getElementsByTagName('URL')[1]
					imgPreview = url.firstChild.data
					# in case of missing preview
					if not imgPreview.lower().endswith('.jpg'):
						inTime = entry.getElementsByTagName('InsertTime')[0]
						inDate = inTime.firstChild.data
						inDate = cfg.datetimeSCP.datetime.strptime(inDate[0:19], '%Y-%m-%dT%H:%M:%S').strftime('%Y.%m.%d')
						imgPreview = 'https://e4ftl01.cr.usgs.gov/WORKING/BRWS/Browse.001/' + inDate + '/BROWSE.' + imgDispID.replace('GQ', 'GA') + '.1.jpg'
					dt = entry.getElementsByTagName('BeginningDateTime')[0]
					imgDate = dt.firstChild.data
					imgDate = cfg.datetimeSCP.datetime.strptime(imgDate[0:19], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
					PointLatitude = entry.getElementsByTagName('PointLatitude')
					lat = []
					for latit in PointLatitude:
						lat.append(float(latit.firstChild.data))
					PointLongitude = entry.getElementsByTagName('PointLongitude')
					lon = []
					for longi in PointLongitude:
						pppLon = float(longi.firstChild.data)
						if pppLon < -170:
							pppLon = 180 + (180 + pppLon)
						lon.append(pppLon)
					DayNightFlag = entry.getElementsByTagName('DayNightFlag')[0]
					dayNight = DayNightFlag.firstChild.data
					listImgID.append([imgID, imgDate, cloudCover, imgDispID, dayNight, lon, lat, imgPreview.replace('http:', 'https:')])
			cfg.uiUtls.updateBar(100, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Searching ...'))
			c = tW.rowCount()
			for imID in listImgID:
				if len(imageFindList) > 0:
					for iF in imageFindList:
						if iF in imID[0].lower():
							imgCheck = 'Yes'
							break
						else:
							imgCheck = 'No'
				else:
					imgCheck = 'Yes'
				if imgCheck == 'Yes':
					c = tW.rowCount()
					# add list items to table
					tW.setRowCount(c + 1)
					cfg.utls.addTableItem(tW, sat, c, 0)
					cfg.utls.addTableItem(tW, imID[3], c, 1)
					cfg.utls.addTableItem(tW, str(imID[1]), c, 2)
					cfg.utls.addTableItem(tW, int(round(float(imID[2]))), c, 3)
					cfg.utls.addTableItem(tW, '', c, 4)
					cfg.utls.addTableItem(tW, imID[4], c, 5)
					min_lon = min(imID[5])
					max_lon = max(imID[5])
					min_lat = min(imID[6])
					max_lat = max(imID[6])
					cfg.utls.addTableItem(tW, float(min_lat), c, 6)
					cfg.utls.addTableItem(tW, float(min_lon), c, 7)
					cfg.utls.addTableItem(tW, float(max_lat), c, 8)
					cfg.utls.addTableItem(tW,float(max_lon), c, 9)
					cfg.utls.addTableItem(tW,'EOSDIS Earthdata', c, 10)
					cfg.utls.addTableItem(tW, imID[7], c, 11)
					cfg.utls.addTableItem(tW, NASAcollection, c, 12)
					cfg.utls.addTableItem(tW, imID[0], c, 13)
			tW.setSortingEnabled(True)	
			cfg.uiUtls.removeProgressBar()
			self.clearCanvasPoly()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' MODIS images')
			c = tW.rowCount()
			if c == 0:
				cfg.mx.msg21()
		except Exception as err:
			cfg.mx.msgErr39()
			cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
	# download MODIS data
	def downloadMODISImages(self, outputDirectory, exporter = 'No'):
		cfg.uiUtls.addProgressBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'), message = '')
		tW = cfg.ui.download_images_tableWidget
		c = tW.rowCount()
		progressStep = 100 / c
		progressStep2 = progressStep/12
		progress = 0
		outDirList = []
		outFileList = []
		imgList = []
		links = []		
		for i in range(0, c):
			sat = str(tW.item(i, 0).text())
			if cfg.actionCheck == 'Yes':
				if sat in cfg.satMODIStList:
					imgID = str(tW.item(i, 13).text())
					imgDispID = str(tW.item(i, 1).text())
					date = str(tW.item(i, 2).text())[0:10]
					if cfg.ui.download_if_preview_in_legend_checkBox.isChecked() and cfg.utls.selectLayerbyName(imgDispID, 'Yes') is None:
						pass
					else:
						NASAcollection = str(tW.item(i, 12).text())
						outDir = outputDirectory + "/" + imgDispID
						if exporter == 'No':
							oDir = cfg.utls.makeDirectory(outDir)
							if oDir is None:
								cfg.mx.msgErr58()
								cfg.uiUtls.removeProgressBar()
								return 'No'
						outDirList.append(outDir)
						outFileList.append(outDir + "//" + imgDispID + ".hdf")
						progress = progress + progressStep
						outUrl = self.downloadMODISImagesFromNASA(imgID, NASAcollection, imgDispID, outDir, progress, exporter, date)
						links.append(outUrl)
			else:
				cfg.uiUtls.removeProgressBar()
				return 'No'
		if exporter == 'Yes':
			return links
		else:
			cfg.cnvs.setRenderFlag(False)
			if cfg.ui.preprocess_checkBox.isChecked():
				n = len(outFileList)
				i = 0
				for d in outFileList:
					i = i + 1
					cfg.uiUtls.updateBar(mainMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Processing') + ' [' + str(i) + '/' + str(n) + '] ' + cfg.osSCP.path.basename(d), message = '')
					if cfg.actionCheck == 'Yes':
						cfg.MODIST.populateTable(d, 'Yes')
						o = d + '_converted'
						oDir = cfg.utls.makeDirectory(o)
						cfg.MODIST.MODIS(d, o, 'Yes')
			elif cfg.ui.load_in_QGIS_checkBox.isChecked():
				for d in outDirList:
					try:
						for f in cfg.osSCP.listdir(d):
							if f.lower().endswith('.tif'):
								r =cfg.utls.addRasterLayer(d + '/' + f)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			
	# download image
	def downloadMODISImagesFromNASA(self, imageID, collection, imageDisplayID, outputDirectory, progress, exporter = 'No', date = None):
		# The MODIS data products are retrieved from the online Data Pool, courtesy of the NASA Land Processes Distributed Active Archive Center (LP DAAC), USGS/Earth Resources Observation and Science (EROS) Center, Sioux Falls, South Dakota, https://lpdaac.usgs.gov/data_access/data_pool'
		if collection == cfg.NASAMOD09GQCollection:
			url = 'https://e4ftl01.cr.usgs.gov/MOLT/MOD09GQ.006/' + date.replace('-', '.')+ '/' + imageDisplayID + '.hdf'
		elif collection == cfg.NASAMYD09GQCollection:
			url = 'https://e4ftl01.cr.usgs.gov/MOLA/MYD09GQ.006/' + date.replace('-', '.')+ '/' + imageDisplayID + '.hdf'
		elif collection == cfg.NASAMOD09GACollection:
			url = 'https://e4ftl01.cr.usgs.gov/MOLT/MOD09GA.006/' + date.replace('-', '.')+ '/' + imageDisplayID + '.hdf'
		elif collection == cfg.NASAMYD09GACollection:
			url = 'https://e4ftl01.cr.usgs.gov/MOLA/MYD09GA.006/' + date.replace('-', '.')+ '/' + imageDisplayID + '.hdf'
		elif collection == cfg.NASAMOD09Q1Collection:
			url = 'https://e4ftl01.cr.usgs.gov/MOLT/MOD09Q1.006/' + date.replace('-', '.')+ '/' + imageDisplayID + '.hdf'
		elif collection == cfg.NASAMYD09Q1Collection:
			url = 'https://e4ftl01.cr.usgs.gov/MOLA/MYD09Q1.006/' + date.replace('-', '.')+ '/' + imageDisplayID + '.hdf'
		elif collection == cfg.NASAMOD09A1Collection:
			url = 'https://e4ftl01.cr.usgs.gov/MOLT/MOD09A1.006/' + date.replace('-', '.')+ '/' + imageDisplayID + '.hdf'
		elif collection == cfg.NASAMYD09A1Collection:
			url = 'https://e4ftl01.cr.usgs.gov/MOLA/MYD09A1.006/' + date.replace('-', '.')+ '/' + imageDisplayID + '.hdf'
		if exporter == 'Yes':
			return url
		else:
			user = cfg.ui.user_usgs_lineEdit_2.text()
			password =cfg.ui.password_usgs_lineEdit_2.text()
			try:
				imgID = imageDisplayID + '.hdf'
				check = cfg.utls.passwordConnectPython(user, password, url, 'urs.earthdata.nasa.gov', cfg.tmpDir + '//' + imgID, progress)
				if str(check) == 'Cancel action':
					return check
				if cfg.osSCP.path.getsize(cfg.tmpDir + '//' + imgID) > 10000:
					cfg.shutilSCP.copy(cfg.tmpDir + '//' + imgID, outputDirectory + '//' + imgID)
					cfg.osSCP.remove(cfg.tmpDir + '//' + imgID)
				else:
					cfg.mx.msgErr55(imgID)
					return 'No'
			except Exception as err:
				cfg.mx.msgErr55(imgID)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return 'No'
			
	# perform bands filter
	def filterTable(self):
		l = cfg.ui.download_images_tableWidget
		text = cfg.ui.products_filter_lineEdit.text()
		items = l.findItems(text, cfg.QtSCP.MatchContains)
		c = l.rowCount()
		list = []
		for item in items:
			list.append( item.row())
		l.blockSignals(True)
		for i in range (0, c):
			l.setRowHidden(i, False)
			if i not in list:
				l.setRowHidden(i, True)
		l.blockSignals(False)