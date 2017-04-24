# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2017 by Luca Congedo
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

class DownloadSentinelImages:

	def __init__(self):
		# check all bands
		self.checkAll = "No"
		self.rbbrBndPol = QgsRubberBand(cfg.cnvs, 2)
		cfg.ui.dateEdit_to_3.setDate(cfg.QDateSCP.currentDate())
		
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
	
	# show area
	def showArea(self):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = QgsCoordinateReferenceSystem()
		iCrs.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
		try:
			UL = QgsPoint(float(cfg.ui.UX_lineEdit_5.text()), float(cfg.ui.UY_lineEdit_5.text()))
			UL1 = cfg.utls.projectPointCoordinates(UL, iCrs, pCrs)
			LR = QgsPoint(float(cfg.ui.LX_lineEdit_5.text()), float(cfg.ui.LY_lineEdit_5.text()))
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
		cfg.ui.LX_lineEdit_5.setText(str(point1.x()))
		cfg.ui.LY_lineEdit_5.setText(str(point1.y()))
		self.showArea()
		
	# set coordinates
	def pointerClickUL(self, point):
		pCrs = cfg.utls.getQGISCrs()
		# WGS84 EPSG 4326
		iCrs = QgsCoordinateReferenceSystem()
		iCrs.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
		point1 = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
		cfg.ui.UX_lineEdit_5.setText(str(point1.x()))
		cfg.ui.UY_lineEdit_5.setText(str(point1.y()))
		self.showArea()
		
	# Activate pointer
	def pointerActive(self):
		# connect to click
		t = cfg.dwnlSentinelP
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(":/pointer/icons/pointer/ROI_pointer.png")
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: Sentinel")
		
	# left click pointer
	def pointerLeftClick(self, point):
		self.pointerClickUL(point)
			
	# right click pointer
	def pointerRightClick(self, point):
		self.pointerClickLR(point)
		
	# find images
	def findImages(self):
		self.queryDatabase()
		
	# service
	def rememberService(self):
		service = cfg.ui.sentinel_service_lineEdit.text()
		cfg.sets.setQGISRegSetting(cfg.regSciHubService, service)
		
	# reset service
	def resetService(self):
		cfg.ui.sentinel_service_lineEdit.setText(cfg.SciHubServiceNm)
		cfg.sets.setQGISRegSetting(cfg.regSciHubService, cfg.SciHubServiceNm)

	# user
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
		
	# download image preview from Amazon
	def downloadPreviewAmazon(self, imgID, imgIDN, imgIDT, imgIDTT, acquisitionDate, progress = None):
		url = "http://sentinel-s2-l1c.s3.amazonaws.com/tiles/" + imgIDN + "/" + imgIDT + "/" + imgIDTT + "/" + acquisitionDate[0:4] + "/" + acquisitionDate[5:7].lstrip('0') + "/" + acquisitionDate[8:10].lstrip('0') + "/0/preview.jp2"
		check = cfg.utls.downloadFile(url, cfg.tmpDir + "//" + imgID + '_p.jp2', imgID, progress)
		return check
		
	# display granule preview	
	def displayGranules(self):
		tW = cfg.ui.sentinel_images_tableWidget
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
				imgNm = str(tW.item(i, 1).text())
				acquisitionDate = str(tW.item(i, 2).text())
				if imgNm[0:4] == "L1C_":
					imgID = imgNm + '_p.jp2'
				else:
					imgID = imgNm[0:-7] + '_p.jp2'
				url = str(tW.item(i, 11).text())
				if cfg.osSCP.path.isfile(cfg.tmpDir + "//" + imgID):
					l = cfg.utls.selectLayerbyName(imgID)
					if l is not None:		
						cfg.lgnd.setLayerVisible(l, True)
						cfg.utls.moveLayerTop(l)
					else:
						r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID, imgID)
				else:
					if imgNm[0:4] == "L1C_":
						checkA = self.downloadPreviewAmazon(imgNm, imgNm.split("_")[1][1:3], imgNm.split("_")[1][3], imgNm.split("_")[1][4:],acquisitionDate, progress)
					else:
						checkA = self.downloadPreviewAmazon(imgNm[0:-7] , imgNm[0:-7][-5:-3], imgNm[0:-7][-3], imgNm[0:-7][-2:], acquisitionDate, progress)
					if checkA != "Yes":
						# single granule
						if "MB" in str(tW.item(i, 9).text()):
							min_lat = str(tW.item(i, 5).text())
							min_lon = str(tW.item(i, 6).text())
							max_lat = str(tW.item(i, 7).text())
							max_lon = str(tW.item(i, 8).text())
							jpg = str(tW.item(i, 10).text())
							self.downloadThumbnail(imgID, min_lat, min_lon, max_lat, max_lon, jpg, progress)
							if cfg.osSCP.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
								r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID + ".vrt", imgID.replace(".vrt",""))
								cfg.utls.setRasterColorComposite(r, 1, 2, 3)
						else:
							self.downloadFile(url, cfg.tmpDir + "//" + imgID, progress)
					if cfg.osSCP.path.isfile(cfg.tmpDir + "//" + imgID):
						r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID, imgID)
				progress = progress + progressStep
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.cnvs.refresh()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " granules displayed")
			
	# display image preview	
	def displayImages(self):
		tW = cfg.ui.sentinel_images_tableWidget
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
				if cfg.osSCP.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
					l = cfg.utls.selectLayerbyName(imgID + ".vrt")
					if l is not None:		
						cfg.lgnd.setLayerVisible(l, True)
						cfg.utls.moveLayerTop(l)
					else:
						r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID + ".vrt", imgID + ".vrt")
						cfg.utls.setRasterColorComposite(r, 1, 2, 3)
				else:
					self.downloadThumbnail(imgID, min_lat, min_lon, max_lat, max_lon, jpg, progress)
					if cfg.osSCP.path.isfile(cfg.tmpDir + "//" + imgID + ".vrt"):
						r = cfg.utls.addRasterLayer(cfg.tmpDir + "//" + imgID + ".vrt", imgID + ".vrt")
						cfg.utls.setRasterColorComposite(r, 1, 2, 3)
				progress = progress + progressStep
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			cfg.cnvs.refresh()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnails displayed")
		
	# download file
	def downloadFile(self, url, output, progress = None):
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " " + topLevelUrl)
		# response = cfg.utls.passwordConnect(user, password, topUrl + '/search?q=', topLevelUrl, None, None, "Yes")
		# if response == "No":
			# cfg.mx.msgErr40()
			# # logger
			# cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " error connection " + topUrl)
		check = cfg.utls.passwordConnect(user, password, url, topLevelUrl, output, progress)
		if check == "Yes":
			return output
		else:
			cfg.mx.msgErr40()
			return "No"
	
	# download image preview
	def downloadThumbnail(self, imgID, min_lat, min_lon, max_lat, max_lon, imageJPG, progress = None):
		user = cfg.ui.user_scihub_lineEdit.text()
		password =cfg.ui.password_scihub_lineEdit.text()
		# check url
		topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
		topUrl =topLevelUrl
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
		tW = cfg.ui.sentinel_images_tableWidget
		cfg.utls.removeRowsFromTable(tW)
			
	# download images in table
	def downloadImages(self):
		tW = cfg.ui.sentinel_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = cfg.utls.getExistingDirectory(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Download the images in the table (requires internet connection)"))
			if len(d) > 0:
				self.downloadSentinelImages(d)
		
	# check all bands
	def checkAllBands(self):
		if self.checkAll == "Yes":
			for i in range(1, 14):
				t = "cfg.ui.checkBoxs_band_" + str(i) + ".setCheckState(2)"
				eval(t)
			cfg.ui.ancillary_data_checkBox.setCheckState(2)
			self.checkAll = "No"
		else:
			for i in range(1, 14):
				t = "cfg.ui.checkBoxs_band_" + str(i) + ".setCheckState(0)"
				eval(t)
			cfg.ui.ancillary_data_checkBox.setCheckState(0)
			self.checkAll = "Yes"
		
	# check band download
	def checkImageBands(self, checkbox, bandNumber, imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFilesList, linksList):
		if cfg.actionCheck == "Yes":
			check = "No"
			if checkbox.isChecked():
				# download using the service http://sentinel-s2-l1c.s3-website.eu-central-1.amazonaws.com
				urlL = "http://sentinel-s2-l1c.s3.amazonaws.com/tiles/" + imgID[-5:-3] + "/" + imgID[-3] + "/" + imgID[-2:] + "/" + acquisitionDate[0:4] + "/" + acquisitionDate[5:7].replace("0", "") + "/" + acquisitionDate[8:10].replace("0", "") + "/0/"
				check = cfg.utls.downloadFile( urlL + "metadata.xml", cfg.tmpDir  + "//" + imgID + "_metadata.xml", imgID + "_metadata.xml", progress)
				if check == "Yes":
					meta = open(cfg.tmpDir  + "//" + imgID + "_metadata.xml", 'r').read()
					if "NoSuchKey" in meta:
						check = "No"
				if check == "Yes":
					if cfg.actionCheck == "Yes":
						if exporter == "Yes":
							linksList.append(urlL + 'B' + bandNumber + '.jp2')
						else:
							if imgName2[0:4] == "L1C_":
								outFile = cfg.tmpDir + "//" + imgName2[4:]  + '_B' + bandNumber + '.jp2'
								outCopyFile = outputDirectory + "//" + imgName2 + "//" + imgName2[4:]  + '_B' + bandNumber
								check = cfg.utls.downloadFile( urlL + 'B' + bandNumber + ".jp2", outFile, imgName2[4:] + '_B' + bandNumber + '.jp2', progress)
							else:
								outFile = cfg.tmpDir + "//" + imgName2[0:-7] + '_B' + bandNumber + '.jp2'
								outCopyFile = outputDirectory + "//" + imgName2[0:-7] + "//" + imgName2[0:-7] + '_B' + bandNumber
								check = cfg.utls.downloadFile( urlL + 'B' + bandNumber + ".jp2", outFile, imgName2[0:-7] + '_B' + bandNumber + '.jp2', progress)
							outFilesList.append([outFile, outCopyFile])
				# download from hub
				else:
					user = cfg.ui.user_scihub_lineEdit.text()
					password =cfg.ui.password_scihub_lineEdit.text()
					# check url
					topLevelUrl = cfg.ui.sentinel_service_lineEdit.text()
					topUrl =topLevelUrl + '/odata/v1/Products'
					topUrl2 =topLevelUrl
					if imgName2[0:4] == "L1C_":
						urlL = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('" + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + ".jp2')/$value"
						outFile = cfg.tmpDir + "//" + imgName2.split("_")[1] + "_" + imgName.split("_")[2] + '_B' + bandNumber + '.jp2'
						outCopyFile = outputDirectory + "//" + imgName2  + "//" + imgName2[4:] + '_B' + bandNumber
					else:
						urlL = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('" + imgName2[0:-7] + '_B' + bandNumber + ".jp2')/$value"
						outFile = cfg.tmpDir + "//" + imgName2[0:-7] + '_B' + bandNumber + '.jp2'
						outCopyFile = outputDirectory + "//" + imgName2[0:-7] + "//" + imgName2[0:-7] + '_B' + bandNumber
					if exporter == "No":
						self.downloadFile(urlL, outFile, progress)
						if cfg.osSCP.path.getsize(outFile) < 100000:
							self.downloadFile(urlL, outFile, progress)
							if cfg.osSCP.path.getsize(outFile) < 100000:
								cfg.mx.msgWar23(imgName2[0:-7] + '_B' + bandNumber + '.jp2')
						outFilesList.append([outFile, outCopyFile])
					else:
						linksList.append(urlL)
		else:
			cfg.uiUtls.removeProgressBar()
			return "No"
		
	# download images
	def downloadSentinelImages(self, outputDirectory, exporter = "No"):
		cfg.uiUtls.addProgressBar()
		tW = cfg.ui.sentinel_images_tableWidget
		outDirList = []
		imgList = []
		links = []
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
			if cfg.actionCheck == "Yes":
				imgName = str(tW.item(i, 0).text())
				acquisitionDate = str(tW.item(i, 2).text())
				imgID = str(tW.item(i, 12).text())
				imgName2 = str(tW.item(i, 1).text())
				if imgName2[0:4] == "L1C_":
					imgJp2 = imgName2 + '_p.jp2'
				else:
					imgJp2 = imgName2[0:-7] + '_p.jp2'
				if cfg.ui.download_if_preview_in_legend_checkBox_3.isChecked() and cfg.utls.selectLayerbyName(imgJp2, "Yes") is None:
					pass
				else:
					outFiles = []
					if imgName2[0:4] == "L1C_":
						outDirList.append(outputDirectory + "//" + imgName2)
					else:
						outDirList.append(outputDirectory + "//" + imgName2[0:-7])
					progress = progress + progressStep
					if exporter == "No":
						if imgName2[0:4] == "L1C_":
							oDir = cfg.utls.makeDirectory(outputDirectory + "//" + imgName2)
						else:
							oDir = cfg.utls.makeDirectory(outputDirectory + "//" + imgName2[0:-7])
						if oDir is None:
							cfg.mx.msgErr58()
							cfg.uiUtls.removeProgressBar()
							cfg.cnvs.setRenderFlag(True)
							return "No"
					# download ancillary data
					if cfg.ui.ancillary_data_checkBox.isChecked():
						#download metadata
						if imgName2[0:4] == "L1C_":
							# new version
							urlL1 = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('MTD_MSIL1C.xml')/$value"
							outFile1 = outputDirectory + "//" + imgName2 + "//" + 'MTD_MSIL1C.xml'
							urlL2 = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('MTD_TL.xml')/$value"
							outFile2 = outputDirectory + "//" + imgName2 + "//" + 'MTD_TL.xml'
							# download QI
							urlL3 = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('QI_DATA')/Nodes('MSK_CLOUDS_B00.gml')/$value"
							outFile3 = outputDirectory + "//" + imgName2 + "//" + 'MSK_CLOUDS_B00.gml'
						else:
							# old version
							urlL1 = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('" + imgName.replace('_PRD_MSIL1C_', '_MTD_SAFL1C_') + ".xml')/$value"
							outFile1 = outputDirectory + "//" + imgName2[0:-7] + "//" + imgName.replace('_PRD_MSIL1C_', '_MTD_SAFL1C_') + '.xml'
							urlL2 = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('" + imgName2[0:-7].replace('_MSI_L1C_', '_MTD_L1C_') + ".xml')/$value"
							outFile2 = outputDirectory + "//" + imgName2[0:-7] + "//" + imgName2[0:-7].replace('_MSI_L1C_', '_MTD_L1C_')  + '.xml'		
							# download QI
							urlL3 = topUrl + "('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('QI_DATA')/Nodes('" + imgName2[0:-7].replace('_MSI_L1C_TL_', '_MSK_CLOUDS_')  + "_B00_MSIL1C.gml')/$value"
							outFile3 = outputDirectory + "//" + imgName2[0:-7] + "//" + imgName2[0:-7].replace('_MSI_L1C_TL_', '_MSK_CLOUDS_') + '_B00_MSIL1C.gml'
						if exporter == "No":
							self.downloadFile(urlL1, outFile1, progress)
							self.downloadFile(urlL2, outFile2, progress)
							self.downloadFile(urlL3, outFile3, progress)
						else:
							links.append(urlL1)
							links.append(urlL2)
							links.append(urlL3)
					# download bands
					self.checkImageBands(cfg.ui.checkBoxs_band_1, '01', imgID, imgName, imgName2, acquisitionDate,outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_2, '02', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_3, '03', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_4, '04', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_5, '05', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_6, '06', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_7, '07', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_8, '08', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_9, '8A', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_10, '09', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_11, '10', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_12, '11', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					self.checkImageBands(cfg.ui.checkBoxs_band_13, '12', imgID, imgName, imgName2, acquisitionDate, outputDirectory, exporter, progress, outFiles, links)
					for oFile in outFiles:
						cfg.shutilSCP.copy(oFile[0], oFile[1] + '.jp2')
						cfg.osSCP.remove(oFile[0])
						if cfg.ui.S2_load_in_QGIS_checkBox.isChecked() and cfg.ui.preprocess_Sentinel_checkBox.isChecked() is False:
							c = cfg.iface.addRasterLayer(oFile[1] + '.jp2', cfg.osSCP.path.basename(oFile[1] + '.jp2'))
			else:
				cfg.uiUtls.removeProgressBar()
				cfg.cnvs.setRenderFlag(True)
				return "No"
		if cfg.ui.preprocess_Sentinel_checkBox.isChecked() and exporter == "No":
			for d in outDirList:
				if cfg.actionCheck == "Yes":
					cfg.sentinel2T.populateTable(d)
					o = d + "_con"
					oDir = cfg.utls.makeDirectory(o)
					if oDir is None:
						cfg.mx.msgErr58()
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
						return "No"
					cfg.sentinel2T.sentinel2(d, o, "Yes")
		cfg.uiUtls.removeProgressBar()
		cfg.cnvs.setRenderFlag(True)
		if exporter == "No":
			cfg.utls.finishSound()
		return links
					
	# export links
	def exportLinks(self):
		tW = cfg.ui.sentinel_images_tableWidget
		c = tW.rowCount()
		if c > 0:
			d = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Export download links"), "", "*.txt")
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
		maxCloudCover = float(cfg.ui.cloud_cover_spinBox_2.value())
		resultNum = int(cfg.ui.result_number_spinBox.value())
		imageFindList = []
		if len(cfg.ui.imageID_lineEdit_3.text()) > 0:
			imgIDLine = cfg.ui.imageID_lineEdit_3.text()
			imgIDLineSplit = str(imgIDLine).replace(" ", "").split(";")
			if len(imgIDLineSplit) == 1:
				imgIDLineSplit = str(imgIDLine).replace(" ", "").split(",")
			for m in imgIDLineSplit:
				imageFindList.append(m.lower())
			imgQuery = "S2A*"
		else:
			imageFindList.append("s2a")
			imgQuery = "S2A*"
		try:
			rubbRect = QgsRectangle(float(cfg.ui.UX_lineEdit_5.text()), float(cfg.ui.UY_lineEdit_5.text()), float(cfg.ui.LX_lineEdit_5.text()), float(cfg.ui.LY_lineEdit_5.text()))
			if abs(float(cfg.ui.UX_lineEdit_5.text()) - float(cfg.ui.LX_lineEdit_5.text())) > 10 or abs(float(cfg.ui.UY_lineEdit_5.text()) - float(cfg.ui.LY_lineEdit_5.text())) > 10:
				cfg.mx.msgWar18()
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg23()
			return "No"
		cfg.uiUtls.addProgressBar()
		tW = cfg.ui.sentinel_images_tableWidget
		cfg.uiUtls.updateBar(30, cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
		cfg.QtGuiSCP.qApp.processEvents()
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
			url = topUrl + '/search?q=' + imgQuery + '%20AND%20cloudcoverpercentage:[0%20TO%20' + str(maxCloudCover) + ']%20AND%20beginPosition:[' + str(dateFrom) + 'T00:00:00.000Z%20TO%20' + str(dateTo) + 'T23:59:59.999Z]%20AND%20footprint:"Intersects(POLYGON((' + cfg.ui.UX_lineEdit_5.text() + "%20" + cfg.ui.UY_lineEdit_5.text() + "," + cfg.ui.UX_lineEdit_5.text() + "%20" + cfg.ui.LY_lineEdit_5.text() + "," + cfg.ui.LX_lineEdit_5.text() + "%20" + cfg.ui.LY_lineEdit_5.text() + "," + cfg.ui.LX_lineEdit_5.text() + "%20" + cfg.ui.UY_lineEdit_5.text() + "," + cfg.ui.UX_lineEdit_5.text() + "%20" + cfg.ui.UY_lineEdit_5.text() + ')))%22' + '&rows=' + str(maxResultNum) + '&start=' + str(startR)
			response = cfg.utls.passwordConnect(user, password, url, topLevelUrl)
			if response == "No":
				cfg.uiUtls.removeProgressBar()
				return "No"
			#info = response.info()
			xml = response	
			tW.setSortingEnabled(False)
			try:
				doc = cfg.minidomSCP.parseString(xml)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				if "HTTP Status 500" in xml:
					cfg.mx.msgWar24()
				else:
					cfg.mx.msgErr40()
				cfg.uiUtls.removeProgressBar()
				return "No"
			entries = doc.getElementsByTagName("entry")
			e = 0
			for entry in entries:
				if cfg.actionCheck == "Yes":
					e = e + 1
					cfg.uiUtls.updateBar(30 + e * int(70/len(entries)), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Searching ..."))
					imgNameTag = entry.getElementsByTagName("title")[0]
					imgName = imgNameTag.firstChild.data
					imgIDTag = entry.getElementsByTagName("id")[0]
					imgID = imgIDTag.firstChild.data
					summary = entry.getElementsByTagName("summary")[0]
					infos = summary.firstChild.data.split(',')
					for info in infos:
						infoIt = info.strip().split(' ')
						if infoIt[0] == "Date:":
							acqDateI = infoIt[1]
						# if infoIt[0] == "Satellite:":
							# print "Satellite " + infoIt[1]
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
					doubles = entry.getElementsByTagName("double")
					for xd in doubles:
						attr = xd.getAttribute("name")
						if attr == "cloudcoverpercentage":
							cloudcoverpercentage = xd.firstChild.data
					url2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('MTD_MSIL1C.xml')/$value"
					if cfg.actionCheck == "Yes":
						response2 = cfg.utls.passwordConnect(user, password, url2, topLevelUrl)
						if len(response2) == 0:
							# old xml version
							url2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('" + imgName.replace('_PRD_MSIL1C_', '_MTD_SAFL1C_') + ".xml')/$value"
							response2 = cfg.utls.passwordConnect(user, password, url2, topLevelUrl)
						if response2 == "No":
							cfg.uiUtls.removeProgressBar()
							return "No"
						xml2 = response2
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " thumbnail downloaded" + xml2)
						try:
							newV = None
							doc2 = cfg.minidomSCP.parseString(xml2)
							imgName2Tag = doc2.getElementsByTagName("IMAGE_FILE")[0]
							imgName2 = imgName2Tag.firstChild.data.split("/")[1]
							if cfg.actionCheck == "Yes":								
								for filter in imageFindList:
									if filter in imgName.lower() or filter in imgName2.lower():
										acZoneI = imgName2.split("_")[1][1:]
										# add item to table
										c = tW.rowCount()
										# add list items to table
										tW.setRowCount(c + 1)
										imgPreview = topUrl + "/odata/v1/Products('" +  imgID + "')/Products('Quicklook')/$value"
										imgPreview2 = topUrl + "/odata/v1/Products('" +imgID  + "')/Nodes('" +imgName + ".SAFE')/Nodes('GRANULE')/Nodes('" + imgName2 + "')/Nodes('IMG_DATA')/Nodes('" + imgName2[0:-7] + "_B01.jp2')/$value"
										cfg.utls.addTableItem(tW, imgName, c, 0)
										cfg.utls.addTableItem(tW, imgName2, c, 1)
										cfg.utls.addTableItem(tW, acqDateI, c, 2)
										cfg.utls.addTableItem(tW, acZoneI, c, 3)
										cfg.utls.addTableItem(tW, float(cloudcoverpercentage), c, 4)
										cfg.utls.addTableItem(tW, float(min_lat), c, 5)
										cfg.utls.addTableItem(tW, float(min_lon), c, 6)
										cfg.utls.addTableItem(tW, float(max_lat), c, 7)
										cfg.utls.addTableItem(tW, float(max_lon), c, 8)
										cfg.utls.addTableItem(tW, size, c, 9)
										cfg.utls.addTableItem(tW, imgPreview, c, 10)
										cfg.utls.addTableItem(tW, imgPreview2, c, 11)
										cfg.utls.addTableItem(tW, imgID, c, 12)
										newV = "Yes"
						except Exception, err:
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						if newV is None:
							# old xml version
							try:
								doc2 = cfg.minidomSCP.parseString(xml2)
								entries2 = doc2.getElementsByTagName("Granules")
								if len(entries2) == 0:
									entries2 = doc2.getElementsByTagName("Granule")
								for entry2 in entries2:
									if cfg.actionCheck == "Yes":
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
												cfg.utls.addTableItem(tW, imgName, c, 0)
												cfg.utls.addTableItem(tW, imgName2, c, 1)
												cfg.utls.addTableItem(tW, acqDateI, c, 2)
												cfg.utls.addTableItem(tW, acZoneI, c, 3)
												cfg.utls.addTableItem(tW, float(cloudcoverpercentage), c, 4)
												cfg.utls.addTableItem(tW, float(min_lat), c, 5)
												cfg.utls.addTableItem(tW, float(min_lon), c, 6)
												cfg.utls.addTableItem(tW, float(max_lat), c, 7)
												cfg.utls.addTableItem(tW, float(max_lon), c, 8)
												cfg.utls.addTableItem(tW, size, c, 9)
												cfg.utls.addTableItem(tW, imgPreview, c, 10)
												cfg.utls.addTableItem(tW, imgPreview2, c, 11)
												cfg.utls.addTableItem(tW, imgID, c, 12)
							except Exception, err:
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		tW.setSortingEnabled(True)		
		cfg.uiUtls.removeProgressBar()
		self.clearCanvasPoly()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Sentinel images")

	# clear table
	def clearTable(self):
		# ask for confirm
		a = cfg.utls.questionBox(cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Reset signature list"), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Are you sure you want to clear the table?"))
		if a == "Yes":
			tW = cfg.ui.sentinel_images_tableWidget
			cfg.utls.clearTable(tW)
			
	# show hide area radio button
	def showHideArea(self):
		try:
			if cfg.ui.show_area_radioButton.isChecked():				
				self.showArea()
			else:
				self.clearCanvasPoly()
		except:
			pass
			