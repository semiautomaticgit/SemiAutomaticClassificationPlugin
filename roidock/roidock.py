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

class RoiDock:

	def __init__(self):
		cfg.rbbrBnd = QgsRubberBand(cfg.cnvs, False)
		cfg.rbbrBnd.setColor(cfg.QtGuiSCP.QColor(0,255,255))
		cfg.rbbrBnd.setWidth(2)
		cfg.mrctrVrtc = []
		
##################################
	""" Map functions """
##################################
				
	# add Highlight Polygon
	def addHighlightPolygon(self, sourceLayer, ID):
		try:
			self.clearCanvasPoly()
		except:
			pass
		clr = cfg.QtGuiSCP.QColor(cfg.ROIClrVal)
		rT = 255 - cfg.ROITrnspVal * 255 / 100
		clr.setAlpha(rT)
		f = cfg.utls.getFeaturebyID(sourceLayer, ID)
		cfg.rbbrBndPol = QgsHighlight(cfg.cnvs, f.geometry(), sourceLayer)
		cfg.rbbrBndPol.setWidth(2)
		cfg.rbbrBndPol.setColor(cfg.QtGuiSCP.QColor(cfg.ROIClrOutlineValDefault))
		try:
			cfg.rbbrBndPol.setFillColor(clr)
		except:
			pass
		cfg.rbbrBndPol.show()
		cfg.show_ROI_radioButton.setChecked(True)
		cfg.ctrlClick = None

	# clear canvas
	def clearCanvas(self):
		cfg.lastVrt = []
		cfg.rbbrBnd.reset(True)
		for m in cfg.mrctrVrtc:
		    cfg.cnvs.scene().removeItem(m)
		    del m
		cfg.cnvs.refresh()
		try:
			self.clearROICanvas()
		except:
			pass
		
	# clear ROI point canvas
	def clearROICanvas(self):
		cfg.rbbrBnd.reset(True)
		for m in self.ROIVrtc:
		    cfg.cnvs.scene().removeItem(m)
		    del m
		cfg.cnvs.refresh()	

	# clear canvas
	def clearCanvasPoly(self):
		cfg.rbbrBndPol.hide()
		try:
			cfg.rbbrBndPolOut.reset(True)
		except:
			pass
		cfg.cnvs.refresh()	
			
##################################
	""" ROI functions """
##################################
			
	# left click
	def clckL(self, pnt):
		pntO = pnt
		pnt = cfg.utls.checkPointImage(cfg.rstrNm, pnt)
		if cfg.pntCheck == "Yes":
			dT = cfg.utls.getTime()
			# temp name
			tN = cfg.subsTmpROI + dT
			# crs
			pCrs = cfg.utls.getQGISCrs()
			mL = QgsVectorLayer("Polygon?crs=" + str(pCrs.toWkt()), tN, "memory")
			mL.setCrs(pCrs) 
			cfg.lastVrt.append(pnt)
			cfg.rbbrBnd.addPoint(QgsPoint(pntO))
			geom = cfg.rbbrBnd.asGeometry()
			v = QgsVertexMarker(cfg.cnvs)
			v.setCenter(pntO)
			cfg.mrctrVrtc.append(v)
			cfg.rbbrBnd.setToGeometry(geom, mL)
			cfg.rbbrBnd.show()
		
	# right click
	def clckR(self, pnt):
		cfg.utls.checkPointImage(cfg.rstrNm, pnt)
		if cfg.pntCheck == "Yes":
			self.clckL(pnt)
			f = QgsFeature()
			dT = cfg.utls.getTime()
			# temp name
			tN = cfg.subsTmpROI + dT
			# band set
			if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
				# crs of loaded raster
				bN = cfg.utls.selectLayerbyName(cfg.bndSet[0], "Yes")
				crs = cfg.utls.getCrs(bN)
				ck = "Yes"
			else:
				try:
					# crs of loaded raster
					crs = cfg.utls.getCrs(cfg.rLay)
					ck = "Yes"
				except:
					ck = "No"
			if crs is None:
				ck = "No"
			if ck == "Yes":
				mL = QgsVectorLayer("Polygon?crs=" + str(crs.toWkt()), tN, "memory")
				mL.setCrs(crs) 
				if not len(cfg.lastVrt) >= 3:
					cfg.mx.msg16()
					self.clearCanvas()
					return
				g = QgsGeometry().fromPolygon([cfg.lastVrt])
				# no intersection
				mL.removePolygonIntersections(g)
				mL.addTopologicalPoints(g)
				pr = mL.dataProvider()
				# create temp ROI
				mL.startEditing()		
				# add fields
				pr.addAttributes( [QgsField("ID",  cfg.QVariantSCP.Int)] )
				# add a feature
				if cfg.ctrlClick is not None:
					g = self.addPartToROI(g)
				else:
					cfg.lstROI2 = cfg.lstROI2 
				f.setGeometry(g)
				f.setAttributes([1])
				pr.addFeatures([f])
				mL.commitChanges()
				mL.updateExtents()
				self.clearCanvas()
				# add ROI layer
				cfg.lstROI = mL
				self.addHighlightPolygon(cfg.lstROI, 1)
				if cfg.uidc.auto_calculate_ROI_signature_radioButton.isChecked():
					cfg.uiUtls.addProgressBar()
					cfg.uiUtls.updateBar(10)
					# ROI date time for temp name
					cfg.ROITime = cfg.datetimeSCP.datetime.now()
					self.tempROISpectralSignature()
					cfg.uiUtls.removeProgressBar()
				cfg.uidc.button_Save_ROI.setEnabled(True)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< ROI created: " + str(tN))
			else:
				cfg.mx.msg4()
				self.clearCanvas()
			
	# add multipart ROI
	def addPartToROI(self, part):
		if cfg.lstROI is not None and cfg.ctrlClick == 1:
			ft = cfg.lstROI.getFeatures()
			f = QgsFeature()
			ft.nextFeature(f)
			g = QgsGeometry(f.geometry())
			g.convertToMultiType()
			part.convertToMultiType()
			g.addPartGeometry(part)
			cfg.lstROI2 = cfg.lstROI
			return g
		else:
			return part
			
	def deleteLastROI(self):
		cfg.lstROI = cfg.lstROI2
		try:
			self.addHighlightPolygon(cfg.lstROI, 1)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						
	# create a ROI
	def createROI(self, point, progressbar = "Yes"):
		if cfg.rstrNm is None:
			cfg.mx.msg4()
			cfg.pntROI = None
		elif cfg.scipyCheck == "No":
			if str(cfg.osSCP.name) == "nt":
				cfg.mx.msgWar2Windows()
			else:
				cfg.mx.msgWar2Linux()
			cfg.pntROI = None
		elif cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes") is None:
			# if band set then pass
			if cfg.rstrNm == cfg.bndSetNm:
				pass
			else:
				cfg.mx.msg4()
				self.refreshRasterLayer()
				cfg.pntROI = None
		if cfg.pntROI != None:
			if progressbar == "Yes":
				cfg.uiUtls.addProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> ROI click")
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(10)
			# ROI date time for temp name
			cfg.ROITime = cfg.datetimeSCP.datetime.now()
			dT = cfg.utls.getTime()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "point (X,Y) = (%s,%s)" % (cfg.pntROI.x() , cfg.pntROI.y()))
			# disable map canvas render for speed (not in QGIS 1.8)
			cfg.cnvs.setRenderFlag(False)
			# temp files
			tRN = cfg.subsTmpROI + dT + ".tif"
			tSN = cfg.subsTmpROI + dT + ".shp"
			tR = unicode(cfg.tmpDir + "//" + tRN)
			tS = unicode(cfg.tmpDir + "//" + tSN)
			# temp name
			tN = cfg.subsTmpROI + dT
			# crs
			pCrs = cfg.utls.getQGISCrs()
			# subprocess bands
			dBs = {}
			dBSP = {}
			dBMA = {}
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(20)
			# band set
			if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
				imageName = cfg.bndSet[0]
				# image CRS
				bN0 = cfg.utls.selectLayerbyName(imageName, "Yes")
				iCrs = cfg.utls.getCrs(bN0)
				if cfg.rpdROICheck == "No":
					# subset and stack layers to tR
					for b in range(0, len(cfg.bndSet)):
						tmpSubset = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + str(b) + "_" + dT + ".vrt")
						dBs["BANDS_" + str(b)] = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + str(b) + "_" + dT + ".vrt")
						dBMA["BANDS_" + str(b)] = [cfg.bndSetMultiFactorsList[b], cfg.bndSetAddFactorsList[b]]
						dBSP["BAND_SUBPROCESS_" + str(b)] = cfg.utls.subsetImage(cfg.bndSet[b], point.x(), point.y(), float(cfg.maxROIWdth), float(cfg.maxROIWdth), tmpSubset, cfg.outTempRastFormat, "Yes")
						if dBSP["BAND_SUBPROCESS_" + str(b)] == "Yes":
							cfg.mx.msgErr29()
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation, edge point")
							cfg.pntROI = None
							if progressbar == "Yes":
								cfg.uiUtls.removeProgressBar()
							return dBSP["BAND_SUBPROCESS_" + str(b)]
				else:
					try:
						b = int(cfg.ROIband) - 1
						pr = cfg.utls.subsetImage(cfg.bndSet[b], point.x(), point.y(), int(cfg.maxROIWdth), int(cfg.maxROIWdth), tR, cfg.outTempRastFormat, "Yes")
						if pr == "Yes":
							cfg.mx.msgErr29()
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation, edge point")
							cfg.pntROI = None
							if progressbar == "Yes":
								cfg.uiUtls.removeProgressBar()
							return pr
						dBs["BANDS_" + str(b)] = tR
						dBMA["BANDS_" + str(b)] = [cfg.bndSetMultiFactorsList[b], cfg.bndSetAddFactorsList[b]]
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.mx.msgErr7()
			else:
				# image CRS
				bN0 = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
				iCrs = cfg.utls.getCrs(bN0)
				if cfg.rpdROICheck == "No":
					# subset image
					pr = cfg.utls.subsetImage(cfg.rstrNm, point.x(), point.y(), int(cfg.maxROIWdth), int(cfg.maxROIWdth), tR, cfg.outTempRastFormat, "Yes")
					if pr == "Yes":
						cfg.mx.msgErr29()
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation, edge point")
						cfg.pntROI = None
						if progressbar == "Yes":
							cfg.uiUtls.removeProgressBar()
						return pr
					oList = cfg.utls.rasterToBands(tR, cfg.tmpDir)
					bLC = 1
					for b in oList:
						dBs["BANDS_" + str(bLC)] = str(b)
						dBMA["BANDS_" + str(bLC)] = [cfg.bndSetMultiFactorsList[bLC - 1], cfg.bndSetAddFactorsList[bLC - 1]]
						bLC = bLC + 1
				else:
					try:
						# temp files
						tRN2 = cfg.copyTmpROI + dT + ".tif"
						tR2 = str(cfg.tmpDir + "//" + tRN2)
						# subset image
						pr = cfg.utls.subsetImage(cfg.rstrNm, point.x(), point.y(), int(cfg.maxROIWdth), int(cfg.maxROIWdth), tR2)
						if pr == "Yes":
							cfg.mx.msgErr29()
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation, edge point")
							cfg.pntROI = None
							if progressbar == "Yes":
								cfg.uiUtls.removeProgressBar()
							return pr
						cfg.utls.getRasterBandByBandNumber(tR2, str(cfg.ROIband), tR,  "No", cfg.rasterDataType, [cfg.bndSetMultiFactorsList[int(cfg.ROIband) - 1], cfg.bndSetAddFactorsList[int(cfg.ROIband) - 1]]) # issue if using virtual raster option
						dBs["BANDS_" + str(1)] = tR
						dBMA["BANDS_" + str(1)] = [cfg.bndSetMultiFactorsList[0], cfg.bndSetAddFactorsList[0]]
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.pntROI = None
						cfg.cnvs.setRenderFlag(True)
						if progressbar == "Yes":
							cfg.uiUtls.removeProgressBar()
						cfg.mx.msgErr7()
						return "No"
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(40)
			# run segmentation
			rGC = self.regionGrowing(dBs, point.x(), point.y(), cfg.rngRad, int(cfg.minROISz), tS, dBMA)
			# check if region growing failed
			if rGC == "Out":
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: Point outside image")
				cfg.pntROI = None
				if progressbar == "Yes":
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msg6()
				return "No"
			elif rGC == "No":
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation")
				cfg.pntROI = None
				if progressbar == "Yes":
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr2()
				return "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "output segmentation: " + str(tSN))
			if progressbar == "Yes":
				cfg.uiUtls.updateBar(60)
			tSS = cfg.utls.addVectorLayer(tS, tSN, "ogr")
			# check if segmentation failed
			if tSS is None:
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error: failed ROI creation")
				cfg.pntROI = None
				if progressbar == "Yes":
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgErr2()
			else:
				# add ROI layer
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(90)
				# add a feature
				f = QgsFeature()
				idf = cfg.utls.getLastFeatureID(tSS)
				q = cfg.utls.getFeaturebyID(tSS, idf)
				# get geometry
				g = q.geometry()
				mL = QgsVectorLayer("Polygon?crs=" + str(iCrs.toWkt()), tN, "memory")
				mL.setCrs(iCrs) 
				pr = mL.dataProvider()
				# create temp ROI
				mL.startEditing()		
				# add fields
				pr.addAttributes( [QgsField("ID",  cfg.QVariantSCP.Int)] )
				# add a feature
				if cfg.ctrlClick is not None:
					g = self.addPartToROI(g)
				else:
					cfg.lstROI2 = cfg.lstROI
				f.setGeometry(g)
				f.setAttributes([1])
				pr.addFeatures([f])
				mL.commitChanges()
				mL.updateExtents()	
				# add ROI layer
				cfg.lstROI = mL
				self.addHighlightPolygon(cfg.lstROI, 1)
				# add point marker
				try:
					self.clearROICanvas()
				except:
					self.ROIVrtc = []
				self.vx = QgsVertexMarker(cfg.cnvs)
				self.vx.setCenter(cfg.origPoint)
				self.vx.setIconType(1)
				self.vx.setColor(cfg.QtGuiSCP.QColor(0,255,255))
				self.vx.setIconSize(12)
				self.ROIVrtc.append(self.vx)
				if cfg.uidc.auto_calculate_ROI_signature_radioButton.isChecked():
					self.tempROISpectralSignature()
				if progressbar == "Yes":
					cfg.uiUtls.updateBar(100)
				cfg.uidc.button_Save_ROI.setEnabled(True)
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "<<< ROI created: " + str(tSS.name()))
				# enable Redo button
				cfg.redo_ROI_Button.setEnabled(True)
				if progressbar == "Yes":
					cfg.uiUtls.removeProgressBar()
			
	# calculate temporary ROI spectral signature
	def tempROISpectralSignature(self):
		idList = []
		for f in cfg.lstROI .getFeatures():
			idList.append(f.id())
		cfg.utls.calculateSignature(cfg.lstROI, cfg.rstrNm, idList, 0, cfg.tmpROINm, 0, cfg.ROITime.strftime("%H-%M-%S"), 0, 50, "Yes", "Yes")
		cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
			
	# region growing
	def regionGrowing(self, rasterDictionary, seedX, seedY, spectralRange, minimumSize, outputVector, multiAddDictionary = None):
		tD = cfg.gdalSCP.GetDriverByName( "GTiff" )
		itRs = iter(rasterDictionary)
		itRs1 = next(itRs)
		dBand = str(itRs1)
		iR = str(rasterDictionary[itRs1])
		# open input with GDAL
		try:
			rD = cfg.gdalSCP.Open(iR, cfg.gdalSCP.GA_ReadOnly)
			# number of x pixels
			rX = rD.RasterXSize
			# number of y pixels
			rY = rD.RasterYSize
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		# check projections
		rP = rD.GetProjection()
		# pixel size and origin
		rGT = rD.GetGeoTransform()
		UX = abs(rGT[0])
		UY = abs(rGT[3])
		pX =  abs(rGT[1])
		pY = abs(rGT[5])
		xSz = rD.RasterXSize
		ySz = rD.RasterYSize
		# seed pixel number
		sPX = abs(int((abs(seedX) - UX)/ pX))
		sPY = abs(int((UY - abs(seedY))/ pY))
		# create a shapefile
		d = cfg.ogrSCP.GetDriverByName('ESRI Shapefile')
		# use ogr
		if d is not None:
			dS = d.CreateDataSource(outputVector)
			if dS is None:
				# close rasters
				rD = None
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "region growing failed: " + str(outputVector))
				return "No"
			else:
				# shapefile
				sR = cfg.osrSCP.SpatialReference()
				sR.ImportFromWkt(rD.GetProjectionRef())
				rL = dS.CreateLayer('ROILayer', sR, cfg.ogrSCP.wkbMultiPolygon)
				fN = "DN"
				fd = cfg.ogrSCP.FieldDefn(fN, cfg.ogrSCP.OFTInteger)
				rL.CreateField(fd)
				fld = rL.GetLayerDefn().GetFieldIndex(fN)
				# prepare output raster
				dT = cfg.utls.getTime()
				tRN = cfg.tmpRegionNm + dT + ".tif"
				tR = str(cfg.tmpDir + "//" + tRN)
				iRB = rD.GetRasterBand(1)
				dtTp = iRB.DataType
				rR = tD.Create(tR, rX, rY, 1, dtTp)
				rR.SetGeoTransform( [ rGT[0] , rGT[1] , 0 , rGT[3] , 0 , rGT[5] ] )
				rR.SetProjection(rP)
				rRB = rR.GetRasterBand(1)
				rRB.SetNoDataValue(0)
				# input array
				aB =  iRB.ReadAsArray()
				try:
					if str(aB[sPY, sPX]) != "nan":
						if multiAddDictionary is not None:
							multiAdd = multiAddDictionary[dBand]
							aB = cfg.utls.arrayMultiplicativeAdditiveFactors(aB, multiAdd[0], multiAdd[1])
						area = int(cfg.maxROIWdth) * int(cfg.maxROIWdth)
						if area < minimumSize:
							minimumSize = area
						# array area
						aBArea = (aB.shape[0] * aB.shape[1]) 
						if aBArea < minimumSize:
							minimumSize = aBArea
						# region growing alg
						try:
							r = self.regionGrowingAlg(aB, sPX, sPY, spectralRange, minimumSize)
							if r is None:
								return "No"
						except Exception, err:
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							return "No"					
						if len(rasterDictionary) > 1:
							for raster in itRs:
								iR = str(rasterDictionary[raster])
								# open input with GDAL
								try:
									rD = cfg.gdalSCP.Open(iR, cfg.gdalSCP.GA_ReadOnly)
									iRB = rD.GetRasterBand(1)
								except Exception, err:
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
									return "No"
								# input array
								aB =  iRB.ReadAsArray()
								if multiAddDictionary is not None:
									multiAdd = multiAddDictionary[raster]
									aB = cfg.utls.arrayMultiplicativeAdditiveFactors(aB, multiAdd[0], multiAdd[1])
								# region growing alg
								try:
									nR = self.regionGrowingAlg(aB, sPX, sPY, spectralRange, minimumSize)
									if nR is not None:
										r = r * nR
									else:
										return "No"
								except Exception, err:
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
									return "No"
								lR, num_features = cfg.labelSCP(r)
								# value of ROI seed
								rV = lR[sPY, sPX]
								r[lR == rV] = 1
								r[lR != rV] = 0
						# write array
						rRB.WriteArray(r)
						# raster to polygon
						cfg.gdalSCP.Polygonize(rRB, rRB.GetMaskBand(), rL, fld)
						# close bands
						rRB = None
						# close rasters
						rR = None
						rD = None
						dS = None
						rL = None
						d = None
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "region growing completed: " + str(iR) + " " + str(spectralRange))
						return "Yes"
					else:
						return "Out"
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"	
		else:
			# possibly ogr driver is missing
			cfg.mx.msgErr27()
			return "No"
			
	# region growing algorithm of an array and a seed
	def regionGrowingAlg(self, array, seedX, seedY, spectralRange, minimumSize):
		sA = cfg.np.zeros(array.shape)
		sA.fill(array[seedY, seedX])
		# difference array
		dA = abs(array - sA)
		# calculate minimum difference
		uDA = cfg.np.unique(dA)
		uDB = uDA[uDA > float(spectralRange)]
		uDA = cfg.np.insert(uDB, 0, float(spectralRange))
		r = None
		for i in uDA:
			iA = cfg.np.where(dA <= i, 1, 0)
			rL, num_features = cfg.labelSCP(iA)
			# value of ROI seed
			rV = rL[seedY,seedX]
			rV_mask = cfg.np.where(rL == rV, 1, 0)
			if rV != 0 and rV_mask.sum() >= minimumSize:
				r = cfg.np.copy(rV_mask)
				break
		if r is None and rV != 0 :
			r = cfg.np.copy(rV_mask)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " region growing seed: " + str(seedX) + ";" + str(seedY))
		return r

##################################
	""" Interface functions """
##################################

	# left click ROI pointer for pixel signature
	def pointerRightClickROI(self, point):
		point = cfg.utls.checkPointImage(cfg.rstrNm, point)
		if cfg.pntCheck == "Yes":
			cfg.utls.calculatePixelSignature(point, cfg.rstrNm, "Yes")
		
	# zoom to ROI
	def zoomToTempROI(self):
		if cfg.lstROI is not None:
			cfg.utls.setMapExtentFromLayer(cfg.lstROI)

	# create a ROI in the same point
	def redoROI(self):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), ">>> REDO ROI creation")
		# check if other processes are active
		if cfg.actionCheck == "No":
			if cfg.pntROI is None:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "REDO ROI fail: no point")
				pass
			else:
				self.createROI(cfg.pntROI)
				# logger
				cfg.utls.logCondition("redoROI " + cfg.utls.lineOfCode(), "<<< REDO ROI creation")

	# show hide ROI radio button
	def showHideROI(self):
		try:
			if cfg.show_ROI_radioButton.isChecked():
				l = cfg.utls.selectLayerbyName(cfg.trnLay)
				if l is not None:
					cfg.lgnd.setLayerVisible(l, True)
				cfg.utls.moveLayerTop(l)
				cfg.rbbrBndPol.show()
				# QGIS < 2.6
				cfg.rbbrBndPolOut.show()
				# ROI point
				self.vx.show()
			else:
				l = cfg.utls.selectLayerbyName(cfg.trnLay)
				if l is not None:
					cfg.lgnd.setLayerVisible(l, False)
				cfg.rbbrBndPol.hide()
				# QGIS < 2.6
				cfg.rbbrBndPolOut.hide()
				# ROI point
				self.vx.hide()
			cfg.cnvs.setRenderFlag(False)
			cfg.cnvs.refresh()
			cfg.cnvs.setRenderFlag(True)
		except:
			pass
		
	# set Min ROI size
	def minROISize(self):
		cfg.minROISz = int(cfg.Min_region_size_spin.value())
		cfg.utls.writeProjectVariable("minROISize", str(cfg.minROISz))
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "min roi size: " + str(cfg.minROISz))

	# set Max ROI size
	def maxROIWidth(self):
		cfg.maxROIWdth = int(cfg.Max_ROI_width_spin.value())
		if (cfg.maxROIWdth % 2 == 0):
			cfg.maxROIWdth = cfg.maxROIWdth + 1
		cfg.utls.writeProjectVariable("maxROIWidth", str(cfg.maxROIWdth))
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "max roi width: " + str(cfg.maxROIWdth))

	def pointerClickROI(self, point):
		# check if other processes are active
		if cfg.actionCheck == "No":
			cfg.origPoint = point
			cfg.utls.checkPointImage(cfg.rstrNm, point)
			if cfg.pntCheck == "Yes":
				cfg.pntROI = cfg.lstPnt
				self.createROI(cfg.pntROI)
		
	# Activate pointer for ROI creation
	def pointerManualROIActive(self):
		cfg.lastVrt = []
		cfg.mrctrVrtc = []
		t = cfg.mnlROI
		cfg.cnvs.setMapTool(t)
		c = cfg.QtGuiSCP.QCursor()
		c.setShape(cfg.QtSCP.CrossCursor)
		cfg.cnvs.setCursor(c)

	# pointer moved
	def movedPointer(self, point):
		px = cfg.QtGuiSCP.QPixmap(":/pointer/icons/pointer/ROI_pointer.png")
		c = cfg.QtGuiSCP.QCursor(px)
		if cfg.uidc.display_cursor_checkBox.isChecked() is True:
			nm = "No"
			point = cfg.utls.checkPointImage(cfg.rstrNm, point, "Yes")
			if point is not None and point != "No":
				if str(cfg.indName) == cfg.indNDVI and cfg.rstrNm is not None:
					nm = cfg.utls.NDVIcalculator(cfg.rstrNm, point)
				elif str(cfg.indName) == cfg.indEVI and cfg.rstrNm is not None:
					nm = cfg.utls.EVIcalculator(cfg.rstrNm, point)
				elif str(cfg.indName) == cfg.indCustom and cfg.rstrNm is not None:
					nm = cfg.utls.customIndexCalculator(cfg.rstrNm, point)
			if nm != "No":
				c = cfg.ROId.cursorCreation(nm)
		cfg.cnvs.setCursor(c)
		
	# Activate pointer for ROI creation
	def pointerROIActive(self):
		self.clearCanvas()
		# connect to click
		t = cfg.regionROI
		cfg.cnvs.setMapTool(t)
		px = cfg.QtGuiSCP.QPixmap(":/pointer/icons/pointer/ROI_pointer.png")
		c = cfg.QtGuiSCP.QCursor(px)
		cfg.cnvs.setCursor(c)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pointer active: ROI")

	def cursorCreation(self, number):
		num = str(number)[0:6]
		pmap = cfg.QtGuiSCP.QPixmap(["48 48 3 1",
					"      c None",
					".     c #ffffff",
					"+     c #000000",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"................................................",
					"                                                ",
					"                      ++++                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                +++++++..+++++++                ",
					"                +..............+                ",
					"                +..............+                ",
					"                +++++++..+++++++                ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      +..+                      ",
					"                      ++++                      ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",
					"                                                ",])
		painter = cfg.QtGuiSCP.QPainter()
		painter.begin(pmap)
		painter.setPen(cfg.QtGuiSCP.QColor(0, 0, 0))
		painter.setFont(cfg.QtGuiSCP.QFont("Monospace", 9))
		painter.drawText(cfg.QtCoreSCP.QPoint(2, 12), num)
		painter.end()
		crsr = cfg.QtGuiSCP.QCursor(pmap)
		return crsr
		
	# set Range radius
	def rangeRadius(self):
		cfg.rngRad = float(cfg.Range_radius_spin.value())
		cfg.utls.writeProjectVariable("rangeRadius", str(cfg.rngRad))
		# auto refresh ROI
		if cfg.uidc.auto_refresh_ROI_radioButton.isChecked() and cfg.ROITime is not None:
			StartT = cfg.datetimeSCP.datetime.now()
			diffT = StartT - cfg.ROITime
			if StartT > (cfg.ROITime + cfg.datetimeSCP.timedelta(seconds=1)):
				self.redoROI()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "range radius: " + str(cfg.rngRad))
		