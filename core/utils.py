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
# sound for Windows
try:
	import winsound
except:
	pass
	
class Utils:
	def __init__(self):
		pass

##################################
	""" Download functions """
##################################

	# download html file
	def downloadHtmlFileQGIS(self, url,  url2 = None, timeOutSec = 1):
		cfg.htmlW = url2
		r = cfg.QNetworkRequestSCP(cfg.QtCoreSCP.QUrl(url))
		cfg.reply = cfg.qgisCoreSCP.QgsNetworkAccessManager.instance().get(r)
		cfg.reply.finished.connect(self.replyInTextBrowser)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return "No"
	
	# load reply in text browser
	def replyInTextBrowser(self):
		cfg.reply.deleteLater()
		html = str(cfg.reply.readAll())
		if "404: Not Found" in html:
			r = cfg.QNetworkRequestSCP(cfg.QtCoreSCP.QUrl(cfg.htmlW))
			cfg.reply2 = cfg.qgisCoreSCP.QgsNetworkAccessManager.instance().get(r)
			cfg.reply2.finished.connect(self.replyInTextBrowser2)
		cfg.uidc.main_textBrowser.clear()
		cfg.uidc.main_textBrowser.setHtml(html)
		cfg.reply.finished.disconnect()
		cfg.reply.abort()
		cfg.reply.close()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		
	# load reply in text browser
	def replyInTextBrowser2(self):
		cfg.reply2.deleteLater()
		html = str(cfg.reply2.readAll())
		cfg.uidc.main_textBrowser.clear()
		cfg.uidc.main_textBrowser.setHtml(html)
		cfg.reply2.finished.disconnect()
		cfg.reply2.abort()
		cfg.reply2.close()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		
	# get proxy opener
	def getProxyHandler(self):
		cfg.utls.getQGISProxySettings()
		if str(cfg.proxyEnabled) == "true" and len(cfg.proxyHost) > 0:
			if len(cfg.proxyUser) > 0:
				proxyHandler = cfg.urllib2SCP.ProxyHandler({'http': 'http://'+ cfg.proxyUser + ":" + cfg.proxyPassword  + "@" + cfg.proxyHost + ':' + cfg.proxyPort})
			else:
				proxyHandler = cfg.urllib2SCP.ProxyHandler({'http': 'http://' + cfg.proxyHost + ':' + cfg.proxyPort})
		else:
			proxyHandler = None
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return proxyHandler

	# get password opener
	def getPasswordHandler(self, user, password, topLevelUrl):
		pswMng = cfg.urllib2SCP.HTTPPasswordMgrWithDefaultRealm()
		pswMng.add_password(None, topLevelUrl, user.encode(cfg.sysSCP.getfilesystemencoding()), password.encode(cfg.sysSCP.getfilesystemencoding()))
		passwordHandler = cfg.urllib2SCP.HTTPBasicAuthHandler(pswMng)
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return passwordHandler
			
	# reply Finish
	def replyFinish(self):
		cfg.replyP.deleteLater()
		cfg.fileP = cfg.replyP.readAll()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
				
	# replyText
	def replyText(self):
		cfg.replyP.deleteLater()
		cfg.htmlP = cfg.replyP.readAll()
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			
	# progress
	def downloadProgress(self, value, total):
		cfg.uiUtls.updateBar(self.progressP, "(" + str(value/1048576) + "/" + str(total/1048576) + " MB) " + self.urlP, "Downloading")
		if cfg.actionCheck == "No":
			cfg.replyP.finished.disconnect()
			cfg.replyP.abort()
			cfg.replyP.close()
							
	# connect with password
	def passwordConnect(self, user, password, url, topLevelUrl, outputPath = None, progress = None, quiet = "No"):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		# auth
		base64UP = cfg.base64SCP.encodestring(user + ":" + password)[:-1]
		h = "Basic " + base64UP
		hKey = cfg.QtCoreSCP.QByteArray("Authorization")
		hValue = cfg.QtCoreSCP.QByteArray(h)
		r = cfg.QNetworkRequestSCP(cfg.QtCoreSCP.QUrl(url))
		r.setRawHeader(hKey, hValue)
		try:
			if outputPath is None:
				cfg.replyP = cfg.qgisCoreSCP.QgsNetworkAccessManager.instance().get(r)
				cfg.replyP.finished.connect(self.replyText)
				# loop
				eL = cfg.QtCoreSCP.QEventLoop()
				cfg.replyP.finished.connect(eL.quit)
				eL.exec_()
				cfg.replyP.finished.disconnect(eL.quit)
				cfg.replyP.finished.disconnect()
				cfg.replyP.abort()
				cfg.replyP.close()
				return cfg.htmlP
			else:
				self.urlP = url
				self.progressP = progress
				cfg.replyP = cfg.qgisCoreSCP.QgsNetworkAccessManager.instance().get(r)
				cfg.replyP.finished.connect(self.replyFinish)
				cfg.replyP.downloadProgress.connect(self.downloadProgress)
				# loop
				eL = cfg.QtCoreSCP.QEventLoop()
				cfg.replyP.finished.connect(eL.quit)
				eL.exec_()
				cfg.replyP.finished.disconnect(eL.quit)
				cfg.replyP.finished.disconnect()
				cfg.replyP.abort()
				cfg.replyP.close()
				with open(outputPath, "wb") as file:
					file.write(cfg.fileP)
				
				if cfg.actionCheck == "No":
					raise ValueError('Cancel action')
				if cfg.osSCP.path.getsize(outputPath) > 500:
					cfg.fileP = None
					return "Yes"
				else:
					if "problem" in cfg.fileP:
						cfg.fileP = None
						return "No"
					else:
						cfg.fileP = None
						return "Yes"
					
		except Exception, err:
			if unicode(err) != 'Cancel action':
				if quiet == "No":
					if "ssl" in unicode(err):
						cfg.mx.msgErr56()
					else:
						cfg.mx.msgErr50(unicode(err))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
			
	# connect with password Python
	def passwordConnectPython(self, user, password, url, topLevelUrl, outputPath = None, progress = None, quiet = "No"):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		proxyHandler = cfg.utls.getProxyHandler()
		passwordHandler = cfg.utls.getPasswordHandler(user, password, topLevelUrl)
		cookieHandler = cfg.urllib2SCP.HTTPCookieProcessor()
		if proxyHandler is None:
			opener = cfg.urllib2SCP.build_opener(cookieHandler, passwordHandler)
		else:
			opener = cfg.urllib2SCP.build_opener(proxyHandler, cookieHandler, passwordHandler)
		cfg.urllib2SCP.install_opener(opener)
		try:
			if outputPath is None:
				response = opener.open(url)
				return response
			else:
				f = cfg.urllib2SCP.urlopen(url)
				total_size = int(f.headers["Content-Length"])
				MB_size = total_size/1048576
				block_size = 1024 * 1024
				with open(outputPath, "wb") as file:
					while True:
						block = f.read(block_size)
						dSize =  int(cfg.osSCP.stat(outputPath).st_size)/1048576
						cfg.uiUtls.updateBar(progress, "(" + str(dSize) + "/" + str(MB_size) + " MB) " +  url, "Downloading")
						cfg.QtGuiSCP.qApp.processEvents()
						if not block:
							break
						file.write(block)
						if cfg.actionCheck == "No":
							raise ValueError('Cancel action')
				return "Yes"
		except Exception, err:
			if unicode(err) != 'Cancel action':
				if quiet == "No":
					if "ssl" in unicode(err):
						cfg.mx.msgErr56()
					else:
						cfg.mx.msgErr50(unicode(err))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
	
	# connect to USGS
	def generalOpener(self):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		proxyHandler = cfg.utls.getProxyHandler()
		cfg.cookieJ = cfg.CookieJarSCP()
		if proxyHandler is None:
			cfg.openerGeneral = cfg.urllib2SCP.build_opener(cfg.urllib2SCP.HTTPCookieProcessor(cfg.cookieJ))
		else:
			cfg.openerGeneral = cfg.urllib2SCP.build_opener(proxyHandler, cfg.urllib2SCP.HTTPCookieProcessor(cfg.cookieJ))
		
	# NASA search
	def NASASearch(self, url):
		cfg.utls.generalOpener()
		request1 = cfg.urllib2SCP.Request(url)
		try:
			response1 = cfg.openerGeneral.open(request1)
		except Exception, err:
			cfg.urllib2SCP.install_opener(cfg.openerGeneral)
			# certificate error
			newContext = cfg.sslSCP.SSLContext(cfg.sslSCP.PROTOCOL_TLSv1) 
			response1 = cfg.urllib2SCP.urlopen(request1, context=newContext)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return response1
		
	# connect with password
	def USGSLogin(self, user, password, topLevelUrl):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		if len(user) > 0:
			cfg.utls.generalOpener()
			request1 = cfg.urllib2SCP.Request(topLevelUrl)
			response1 = cfg.openerGeneral.open(request1)
			html1 = response1.read()
			# required token
			tok = cfg.reSCP.findall('value=(.*?)id="csrf_token"', str(html1))
			tid = tok[0].replace('"', '').replace(' ', '')
			# login
			params = 'username=' + user + '&password=' + password + '&csrf_token=' + tid
			request2 = cfg.urllib2SCP.Request('https://ers.cr.usgs.gov/login', params)
			response2 = cfg.openerGeneral.open(request2)
			for cookie in cfg.cookieJ:
				if cookie.name == "EROS_SSO_production":
					cookievalue = cookie.value
			try:
				cfg.openerGeneral.addheaders = [('Cookie', 'EROS_SSO_production=' + cookievalue)]
				return cookievalue
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				raise ValueError('Login error')
			
	# download file
	def downloadFileUSGS(self, user, password, topLevelUrl, url, outputPath, fileName = None, progress = None, quiet = "No"):
		cookievalue = cfg.utls.USGSLogin(user, password, topLevelUrl)
		cfg.urllib2SCP.install_opener(cfg.openerGeneral)
		cfg.timeSCP.sleep(0.5)
		try:
			request1 = cfg.urllib2SCP.Request(url)
			response1 = cfg.openerGeneral.open(request1)
			cfg.timeSCP.sleep(0.5)
			f = cfg.urllib2SCP.urlopen(response1.url)
			total_size = int(f.headers["Content-Length"])
			MB_size = total_size/1048576
			block_size = 1024 * 1024
			with open(outputPath, "wb") as file:
				while True:
					block = f.read(block_size)
					dSize =  int(cfg.osSCP.stat(outputPath).st_size)/1048576
					cfg.uiUtls.updateBar(progress, "(" + str(dSize) + "/" + str(MB_size) + " MB) " +  url, "Downloading")
					cfg.QtGuiSCP.qApp.processEvents()
					if not block:
						break
					file.write(block)
					if cfg.actionCheck == "No":
						raise ValueError('Cancel action')
						
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return "Yes"
		except Exception, err:
			if unicode(err) != 'Cancel action':
				if quiet == "No":
					cfg.mx.msgErr50(unicode(err))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			raise ValueError(str(err))
	
	# encrypt password
	def encryptPassword(self, password):
		e = cfg.base64SCP.b64encode(password.encode(cfg.sysSCP.getfilesystemencoding()))
		return e
		
	# decrypt password
	def decryptPassword(self, password):
		d = cfg.base64SCP.b64decode(password)
		return d
		
	# download file
	def downloadFile(self, url, outputPath, fileName = None, progress = None):
		try:
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			proxyHandler = cfg.utls.getProxyHandler()
			if proxyHandler is not None:
				opener = cfg.urllib2SCP.build_opener(proxyHandler)
				cfg.urllib2SCP.install_opener(opener)
			else:
				opener = cfg.urllib2SCP.build_opener()
			f = cfg.urllib2SCP.urlopen(url)
			try:
				total_size = int(f.headers["Content-Length"])
				MB_size = total_size/1048576
			except:
				total_size = 1
			block_size = 1024 * 1024
			if block_size >= total_size:
				response = f.read()
				l = open(outputPath, 'wb')
				l.write(str(response))
				l.close()
			else:
				with open(outputPath, "wb") as file:
					while True:
						block = f.read(block_size)
						dSize =  int(cfg.osSCP.stat(outputPath).st_size)/1048576
						cfg.uiUtls.updateBar(progress, "(" + str(dSize) + "/" + str(MB_size) + " MB) " +  url, "Downloading")
						cfg.QtGuiSCP.qApp.processEvents()
						if not block:
							break
						file.write(block)
						if cfg.actionCheck == "No":
							raise ValueError('Cancel action')
			return "Yes"
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return err

##################################
	""" LOG functions """
##################################

	# Clear log file
	def clearLogFile(self):
		if cfg.osSCP.path.isfile(cfg.logFile):
			try:
				l = open(cfg.logFile, 'w')
			except:
				pass
			try:
				l.write("Date	Function	Message \n")
				l.write(str(cfg.sysSCPInfo)+"\n")
				l.close()
			except:
				cfg.mx.msg2()

	# Get the code line number for log file
	def lineOfCode(self):
		return str(cfg.inspectSCP.currentframe().f_back.f_lineno)
		
	# logger condition
	def logCondition(self, function, message = ""):
		if cfg.logSetVal == "Yes":
			cfg.utls.logToFile(function, message)
		
	# Logger of function
	def logToFile(self, function, message):
		# message string
		m = cfg.datetimeSCP.datetime.now().strftime("%Y-%m-%d %H.%M.%S.%f") + "	" + function + "	" + message + "\n"
		if cfg.osSCP.path.isfile(cfg.logFile):
			try:
				l = open(cfg.logFile, 'a')
			except:
				pass
		else:
			l = open(cfg.logFile, 'w')
			try:
				l.write("Date	Function	Message \n")
				l.write(m)
				l.close()
			except:
				pass
		try:
			l.write(m)
			l.close()
		except:
			pass

##################################
	""" Time functions """
##################################

	# get  time
	def getTime(self):
		t = cfg.datetimeSCP.datetime.now().strftime("%Y%m%d_%H%M%S%f")
		return t
		
	# convert seconds to H M S
	def timeToHMS(self, time):
		min, sec = divmod(time, 60)
		hour, min = divmod(min, 60)
		if hour > 0:
			m = str("%.f" % round(hour)) + " H " + str("%.f" % round(min)) + " min"
		else:
			m = str("%.f" % round(min)) + " min " + str("%.f" % round(sec)) + " sec"
		return m

##################################
	""" Symbology functions """
##################################
		
	# set layer color for ROIs
	def ROISymbol(self, layer):
		st = { 'color': '0,0,0,230',  'color_border': '0,0,0,230', 'style': 'solid', 'style_border': 'solid' }
		r = QgsFillSymbolV2.createSimple(st)
		renderer = layer.rendererV2()
		renderer.setSymbol(r)
		
	# Define vector symbology
	def vectorSymbol(self, layer, signatureList, macroclassCheck):
		c = []
		n = []
		# class count
		mc = []
		v = signatureList
		s = QgsSymbolV2.defaultSymbol(layer.geometryType())
		s.setColor(cfg.QtGuiSCP.QColor("#000000"))
		c.append(QgsRendererCategoryV2(0, s, "0 - " + cfg.uncls))
		for i in range(0, len(v)):
				if macroclassCheck == "Yes":
					if int(v[i][0]) not in mc:
						mc.append(int(v[i][0]))
						n.append([int(v[i][0]), v[i][6], str(v[i][1])])
				else:
					n.append([int(v[i][2]), v[i][6], str(v[i][3])])
		for b in sorted(n, key=lambda c: c[0]):
			s = QgsSymbolV2.defaultSymbol(layer.geometryType())
			s.setColor(b[1])
			ca = QgsRendererCategoryV2(b[0], s, str(b[0]) + " - " + b[2])
			c.append(ca)
		f = str(cfg.fldID_class)
		r = QgsCategorizedSymbolRendererV2(f, c)
		layer.setRendererV2(r)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		
	# Define class symbology
	def rasterSymbol(self, classLayer, signatureList, macroclassCheck):
		classLayer.setDrawingStyle("SingleBandPseudoColor")
		# The band of classLayer
		cLB = 1
		# Color list for ramp
		cL = []
		n = []
		# class count
		mc = []
		v = signatureList
		if cfg.unclassValue is not None:
			cL.append(QgsColorRampShader.ColorRampItem(cfg.unclassValue, cfg.QtGuiSCP.QColor("#4d4d4d"), cfg.overlap))
		cL.append(QgsColorRampShader.ColorRampItem(0, cfg.QtGuiSCP.QColor("#000000"), "0 - " + cfg.uncls))
		for i in range(0, len(v)):
			if macroclassCheck == "Yes":
				if int(v[i][0]) not in mc and int(v[i][0]) != 0:
					mc.append(int(v[i][0]))
					n.append([int(v[i][0]), v[i][6], str(v[i][1])])
			else:
				if int(v[i][2]) != 0:
					n.append([int(v[i][2]), v[i][6], str(v[i][3])])
		for b in sorted(n, key=lambda c: c[0]):
			cL.append(QgsColorRampShader.ColorRampItem(b[0], b[1], str(b[0]) + " - " + b[2]))
		# Create the shader
		lS = QgsRasterShader()
		# Create the color ramp function
		cR = QgsColorRampShader()
		cR.setColorRampType(QgsColorRampShader.EXACT)
		cR.setColorRampItemList(cL)
		# Set the raster shader function
		lS.setRasterShaderFunction(cR)
		# Create the renderer
		lR = QgsSingleBandPseudoColorRenderer(classLayer.dataProvider(), cLB, lS)
		# Apply the renderer to classLayer
		classLayer.setRenderer(lR)
		# refresh legend
		if hasattr(classLayer, "setCacheImage"):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(classLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(classLayer.source()))
		
	# Define class symbology
	def rasterSymbolLCSAlgorithmRaster(self, classLayer):
		classLayer.setDrawingStyle("SingleBandPseudoColor")
		# The band of classLayer
		cLB = 1
		# Color list for ramp
		cL = []
		if cfg.unclassValue is not None:
			cL.append(QgsColorRampShader.ColorRampItem(cfg.unclassValue, cfg.QtGuiSCP.QColor("#4d4d4d"), cfg.overlap))
		cL.append(QgsColorRampShader.ColorRampItem(0, cfg.QtGuiSCP.QColor("#000000"), "0 " + cfg.uncls))
		cL.append(QgsColorRampShader.ColorRampItem(1, cfg.QtGuiSCP.QColor("#ffffff"), "1 " + cfg.clasfd))
		# Create the shader
		lS = QgsRasterShader()
		# Create the color ramp function
		cR = QgsColorRampShader()
		cR.setColorRampType(QgsColorRampShader.EXACT)
		cR.setColorRampItemList(cL)
		# Set the raster shader function
		lS.setRasterShaderFunction(cR)
		# Create the renderer
		lR = QgsSingleBandPseudoColorRenderer(classLayer.dataProvider(), cLB, lS)
		# Apply the renderer to classLayer
		classLayer.setRenderer(lR)
		# refresh legend
		if hasattr(classLayer, "setCacheImage"):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(classLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(classLayer.source()))
		
	# Define class symbology
	def rasterPreviewSymbol(self, previewLayer, algorithmName):
		if cfg.uidc.LC_signature_checkBox.isChecked():
			cfg.utls.rasterSymbolLCSAlgorithmRaster(previewLayer)
		elif algorithmName == cfg.algMinDist or algorithmName == cfg.algSAM:
			cfg.utls.rasterSymbolPseudoColor(previewLayer)
		elif algorithmName == cfg.algML:
			cfg.utls.rasterSymbolSingleBandGray(previewLayer)
			
	# Define class symbology pseudo color
	def rasterSymbolPseudoColor(self, layer):
		layer.setDrawingStyle("SingleBandPseudoColor")
		# Band statistics
		bndStat = layer.dataProvider().bandStatistics(1)
		max = bndStat.maximumValue
		min = bndStat.minimumValue
		# The band of layer
		cLB = 1
		# Color list for ramp
		cL = []
		colorMin = cfg.QtGuiSCP.QColor("#ffffff")
		colorMax = cfg.QtGuiSCP.QColor("#000000")
		cL.append(QgsColorRampShader.ColorRampItem(min, colorMin, str(min)))
		cL.append(QgsColorRampShader.ColorRampItem(max, colorMax, str(max)))
		# Create the shader
		lS = QgsRasterShader()
		# Create the color ramp function
		cR = QgsColorRampShader()
		cR.setColorRampType(QgsColorRampShader.INTERPOLATED)
		cR.setColorRampItemList(cL)
		# Set the raster shader function
		lS.setRasterShaderFunction(cR)
		# Create the renderer
		lR = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), cLB, lS)
		# Apply the renderer to layer
		layer.setRenderer(lR)
		# refresh legend
		if hasattr(layer, "setCacheImage"):
			layer.setCacheImage(None)
		layer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(layer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(layer.source()))
		
	# Define class symbology single band grey
	def rasterSymbolSingleBandGray(self, layer):
		layer.setDrawingStyle("SingleBandGray")
		layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, QgsRaster.ContrastEnhancementCumulativeCut)
		# refresh legend
		if hasattr(layer, "setCacheImage"):
			layer.setCacheImage(None)
		layer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(layer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(layer.source()))
		
	# Define raster symbology
	def rasterSymbolGeneric(self, rasterLayer, zeroValue = "Unchanged"):
		rasterLayer.setDrawingStyle("SingleBandPseudoColor")
		# The band of classLayer
		classLyrBnd = 1
		# Band statistics
		bndStat = rasterLayer.dataProvider().bandStatistics(1)
		classMax = bndStat.maximumValue
		# Color list for ramp
		clrLst = [ QgsColorRampShader.ColorRampItem(0, cfg.QtGuiSCP.QColor(0,0,0), zeroValue), QgsColorRampShader.ColorRampItem(1, cfg.QtGuiSCP.QColor(0,0,255), "1"), QgsColorRampShader.ColorRampItem(round(classMax/2), cfg.QtGuiSCP.QColor(255,0,0), str(round(classMax/2))), QgsColorRampShader.ColorRampItem(classMax, cfg.QtGuiSCP.QColor(0,255,0), str(classMax)) ]
		# Create the shader
		lyrShdr = QgsRasterShader()
		# Create the color ramp function
		clrFnctn = QgsColorRampShader()
		clrFnctn.setColorRampType(QgsColorRampShader.INTERPOLATED)
		clrFnctn.setColorRampItemList(clrLst)
		# Set the raster shader function
		lyrShdr.setRasterShaderFunction(clrFnctn)
		# Create the renderer
		lyrRndr = QgsSingleBandPseudoColorRenderer(rasterLayer.dataProvider(), classLyrBnd, lyrShdr)
		# Apply the renderer to rasterLayer
		rasterLayer.setRenderer(lyrRndr)
		# refresh legend
		if hasattr(rasterLayer, "setCacheImage"):
			rasterLayer.setCacheImage(None)
		rasterLayer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(rasterLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "symbology")

	# Define scatter raster symbology
	def rasterScatterSymbol(self, valueColorList):
		# Color list for ramp
		cL = []
		for i in valueColorList:
			cL.append(QgsColorRampShader.ColorRampItem(i[0], cfg.QtGuiSCP.QColor(i[1]), str(i[0])))
		# Create the shader
		lS = QgsRasterShader()
		# Create the color ramp function
		cR = QgsColorRampShader()
		cR.setColorRampType(QgsColorRampShader.EXACT)
		cR.setColorRampItemList(cL)
		# Set the raster shader function
		lS.setRasterShaderFunction(cR)
		return lS
		
	# set scatter raster symbology
	def setRasterScatterSymbol(self, classLayer, shader):
		classLayer.setDrawingStyle("SingleBandPseudoColor")
		# The band of classLayer
		cLB = 1
		# Create the renderer
		lR = QgsSingleBandPseudoColorRenderer(classLayer.dataProvider(), cLB, shader)
		# Apply the renderer to classLayer
		classLayer.setRenderer(lR)
		# refresh legend
		if hasattr(classLayer, "setCacheImage"):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.lgnd.refreshLayerSymbology(classLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(classLayer.source()))
		
	# copy renderer
	def copyRenderer(self, inputRaster, outputRaster):
		try:
			outputRaster.setDrawingStyle("SingleBandPseudoColor")
			r = inputRaster.renderer()
			cR = r.shader()
			# The band of classLayer
			classLyrBnd = 1
			# Create the renderer
			lyrRndr = QgsSingleBandPseudoColorRenderer(outputRaster.dataProvider(), classLyrBnd, cR)
			# Apply the renderer to rasterLayer
			outputRaster.setRenderer(lyrRndr)
			outputRaster.triggerRepaint()
			cfg.lgnd.refreshLayerSymbology(outputRaster)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		except Exception, err:
			list = "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
##################################
	""" Classification functions """
##################################
			
	# calculate covariance matrix from array list
	def calculateCovMatrix(self, arrayList):
		# create empty array
		d = arrayList[0].shape
		arrCube = cfg.np.zeros((d[0], d[1], len(arrayList)), dtype=cfg.np.float64)
		i = 0
		try:
			for a in arrayList:
				arrCube[:, :, i] = a
				i = i + 1
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		matrix = arrCube.reshape(d[0] * d[1], len(arrayList))
		# find No data
		NoDt = cfg.np.where(cfg.np.isnan(matrix[:, 0]))
		# delete No data
		GMatrix = cfg.np.delete(matrix, NoDt, axis=0)
		TMatrix = GMatrix.T
		# covariance matrix (degree of freedom = 1 for unbiased estimate)
		CovMatrix = cfg.np.cov(TMatrix, ddof=1)
		try:
			if cfg.np.isnan(CovMatrix[0,0]):
				CovMatrix = "No"
			try:
				inv = cfg.np.linalg.inv(CovMatrix)
				if cfg.np.isnan(inv[0,0]):
					CovMatrix = "No"
			except:
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "TEST matrix: " + str(CovMatrix))
				CovMatrix = "No"
		except Exception, err:
			CovMatrix = "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "cov matrix: " + str(CovMatrix))
		return CovMatrix
			
	# convert list to covariance array
	def listToCovarianceMatrix(self, list):
		try:
			covMat = cfg.np.zeros((len(list), len(list)), dtype=cfg.np.float64)
			i = 0
			for x in list:
				covMat[i, :] = x
				i = i + 1
			return covMat
		except Exception, err:
			list = "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		return "No"
		
	# convert covariance array to list
	def covarianceMatrixToList(self, covarianceArray):
		try:
			d = covarianceArray.shape
			list = []
			for i in range(0, d[0]):
				list.append(covarianceArray[i, :].tolist())
		except Exception, err:
			list = "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		return list
		
	# create one raster for each signature class
	def createSignatureClassRaster(self, signatureList, gdalRasterRef, outputDirectory, nodataValue = None, outputName = None, previewSize = 0, previewPoint = None, compress = "No", compressFormat = "DEFLATE21"):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "start createSignatureClassRaster")	
		dT = self.getTime()
		outputRasterList = []
		for s in range(0, len(signatureList)):
			if outputName == None:
				o = outputDirectory + "/" + cfg.sigRasterNm + "_" + str(signatureList[s][0]) + "_" + str(signatureList[s][2]) + "_" + dT + ".tif"
			else:
				o = outputDirectory + "/" + outputName + "_" + str(signatureList[s][0]) + "_" + str(signatureList[s][2]) + ".tif"
			outputRasterList.append(o)
		oRL = self.createRasterFromReference(gdalRasterRef, 1, outputRasterList, nodataValue, "GTiff", cfg.rasterDataType, previewSize, previewPoint, compress, compressFormat)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "end createSignatureClassRaster")
		return oRL, outputRasterList
		
	# perform classification
	def classification(self, gdalBandList, signatureList, algorithmName, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, outputAlgorithmRaster, outputClassificationRaster, nodataValue, macroclassCheck, previewSize, pixelStartColumnPreview, pixelStartRowPreview, progressStart, progresStep, remainingBlocks, progressMessage):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "start classification block")
		sigArrayList = self.createArrayFromSignature(gdalBandList, signatureList)
		LCSminMaxL = cfg.utls.LCSminMaxList(signatureList)
		bN = 0
		minArray = None
		maxArray = None
		classArray = None
		classArrayAlg = None
		classArrayLCS = None
		equalArray = None
		cfg.unclassValue = None
		n = 0
		StartT = 0
		itCount = 0
		itTot = len(sigArrayList)
		progresStep = progresStep / len(sigArrayList)
		if cfg.uidc.LC_signature_checkBox.isChecked():
			# max and min values
			tr = self.thresholdList(signatureList)
			covMatrList = self.covarianceMatrixList(signatureList)
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = cfg.timeSCP.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						#cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
						pass
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = cfg.timeSCP.clock()
					# algorithm
					rasterArrayx = cfg.np.copy(rasterArray)
					# threshold
					multFactor = float(1)
					# second classification
					if cfg.uidc.LCS_class_algorithm_checkBox.isChecked():
						secondClassification = algorithmName
					else:
						secondClassification = "No"
					if secondClassification == "No":
						dataValue = -100
						cfg.unclassValue = -1000
					elif secondClassification == cfg.algMinDist:
						dataValue = -100
						cfg.unclassValue = -1000
					elif secondClassification == cfg.algSAM:
						dataValue = -100
						cfg.unclassValue = -1000
					elif secondClassification == cfg.algML:
						dataValue = cfg.maxValDt
						cfg.unclassValue = -1000
					# calculate LCS array
					LCSarray = self.algorithmLCS(rasterArrayx, s, LCSminMaxL[n][0], LCSminMaxL[n][1] , multFactor, cfg.algBandWeigths, dataValue, nodataValue)
					if type(LCSarray) is not int:
						oR = outputGdalRasterList[bN]
						if previewSize > 0:
							pixelStartColumn = int(pixelStartColumnPreview)
							pixelStartRow = int(pixelStartRowPreview)
						# binary classification
						LCSarrayWrite = cfg.np.where(LCSarray==dataValue,1,0)
						# algorithm raster
						self.writeArrayBlock(oR, 1, LCSarrayWrite, pixelStartColumn, pixelStartRow, nodataValue)
						LCSarrayWrite = None
						# find equal array for overlapping classes
						if equalArray is None:
							equalArray = LCSarray
						else:
							equalArray = self.findEqualArray(LCSarray, equalArray, dataValue, nodataValue, cfg.unclassValue)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMinimumArray signature" + str(itCount))
						if classArray == None:
							classArray = nodataValue
						if macroclassCheck == "Yes":
							classArray = self.classifyClassesLCSSimple(LCSarray, equalArray, classArray, dataValue, cfg.unclassValue, nodataValue, signatureList[n][0])
						else:
							classArray = self.classifyClassesLCSSimple(LCSarray, equalArray, classArray, dataValue, cfg.unclassValue, nodataValue, signatureList[n][2])
						# in case of same class overlapping
						equalArray = cfg.np.where( (equalArray ==cfg.unclassValue) & (classArray !=cfg.unclassValue), dataValue, equalArray)
						# refine class output
						classArrayLCS = cfg.np.where(classArray == nodataValue, 0, classArray)
						algArrayWrite = cfg.np.where(classArrayLCS == 0, 0, cfg.np.where(classArrayLCS == cfg.unclassValue, cfg.unclassValue, 1))
						# algorithm raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, algArrayWrite, pixelStartColumn, pixelStartRow, nodataValue)
						algArrayWrite = None
						if secondClassification == "No":
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
						elif secondClassification == cfg.algMinDist:
							# algorithm
							rasterArrayx = cfg.np.copy(rasterArray)
							c = self.algorithmMinimumDistance(rasterArrayx, s, cfg.algBandWeigths)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithmMinimumDistance signature" + str(itCount))
							# threshold
							algThrshld = float(tr[n])
							if algThrshld > 0:
								c = self.minimumDistanceThreshold(c, algThrshld, nodataValue)
							if type(c) is not int:
								oR = outputGdalRasterList[bN]
								# algorithm raster
								#self.writeArrayBlock(oR, 1, c, pixelStartColumn, pixelStartRow, nodataValue)
								if minArray is None:
									minArray = c
								else:
									minArray = self.findMinimumArray(c, minArray, nodataValue)
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMinimumArray signature" + str(itCount))
								# minimum raster
								#self.writeArrayBlock(outputAlgorithmRaster, 1, minArray, pixelStartColumn, pixelStartRow, nodataValue)
								# signature classification raster
								if macroclassCheck == "Yes":
									clA = self.classifyClasses(c, minArray, signatureList[n][0])
								else:
									clA = self.classifyClasses(c, minArray, signatureList[n][2])
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
								# classification raster
								if classArrayAlg == None:
									classArrayAlg = clA
								else:
									e = cfg.np.ma.masked_equal(clA, 0)
									classArrayAlg =  e.mask * classArrayAlg + clA
									e = None
								clA = None
								classArrayAlg[classArrayAlg == cfg.unclassifiedVal] = 0
								classArrayLCS = cfg.np.where(classArray == cfg.unclassValue, classArrayAlg, classArray)
								if cfg.uidc.LCS_leave_unclassified_checkBox.isChecked():
									pass
								else:
									classArrayLCS = cfg.np.where(classArray == nodataValue, classArrayAlg, classArrayLCS)
							else:
								return "No"
						elif secondClassification == cfg.algSAM:
							# algorithm
							rasterArrayx = cfg.np.copy(rasterArray)
							c = self.algorithmSAM(rasterArrayx, s, cfg.algBandWeigths)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithmSAM signature" + str(itCount))
							# threshold
							algThrshld = float(tr[n])
							if algThrshld > 0:
								if algThrshld > 90:
									algThrshld = 90
								c = self.minimumDistanceThreshold(c, algThrshld, nodataValue)
							if type(c) is not int:
								oR = outputGdalRasterList[bN]
								if previewSize > 0:
									pixelStartColumn = int(pixelStartColumnPreview)
									pixelStartRow = int(pixelStartRowPreview)
								# algorithm raster
								#self.writeArrayBlock(oR, 1, c, pixelStartColumn, pixelStartRow, nodataValue)
								if minArray is None:
									minArray = c
								else:
									minArray = self.findMinimumArray(c, minArray, nodataValue)
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMinimumArray signature" + str(itCount))
								# minimum raster
								#self.writeArrayBlock(outputAlgorithmRaster, 1, minArray, pixelStartColumn, pixelStartRow, nodataValue)
								# signature classification raster
								if macroclassCheck == "Yes":
									clA = self.classifyClasses(c, minArray, signatureList[n][0])
								else:
									clA = self.classifyClasses(c, minArray, signatureList[n][2])
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
								# classification raster
								if classArrayAlg == None:
									classArrayAlg = clA
								else:
									e = cfg.np.ma.masked_equal(clA, 0)
									classArrayAlg =  e.mask * classArrayAlg + clA
									e = None
								clA = None
								classArrayAlg[classArrayAlg == cfg.unclassifiedVal] = 0
								classArrayLCS = cfg.np.where(classArray == cfg.unclassValue, classArrayAlg, classArray)
								if cfg.uidc.LCS_leave_unclassified_checkBox.isChecked():
									pass
								else:
									classArrayLCS = cfg.np.where(classArray == nodataValue, classArrayAlg, classArrayLCS)
							else:
								return "No"									
						elif secondClassification == cfg.algML:
							# algorithm
							rasterArrayx = cfg.np.copy(rasterArray)
							# threshold
							algThrshld = float(tr[n])
							if algThrshld > 100:
								algThrshld = 100
							c = self.algorithmMaximumLikelihood(rasterArrayx, s, covMatrList[n], cfg.algBandWeigths, algThrshld)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithmMaximumLikelihood signature" + str(itCount))
							if algThrshld > 0:
								c = self.maximumLikelihoodThreshold(c, nodataValue)
							if type(c) is not int:					
								oR = outputGdalRasterList[bN]
								if previewSize > 0:
									pixelStartColumn = int(pixelStartColumnPreview)
									pixelStartRow = int(pixelStartRowPreview)
								# algorithm raster
								#self.writeArrayBlock(oR, 1, c, pixelStartColumn, pixelStartRow, nodataValue)
								if maxArray is None:
									maxArray = c
								else:
									maxArray = self.findMaximumArray(c, maxArray, nodataValue)
									# logger
									cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMaximumArray signature" + str(itCount))
								# maximum raster
								#self.writeArrayBlock(outputAlgorithmRaster, 1, maxArray, pixelStartColumn, pixelStartRow, nodataValue)
								# signature classification raster
								if macroclassCheck == "Yes":
									clA = self.classifyClasses(c, maxArray, signatureList[n][0])
								else:
									clA = self.classifyClasses(c, maxArray, signatureList[n][2])
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
								# classification raster
								if classArrayAlg == None:
									classArrayAlg = clA
								else:
									e = cfg.np.ma.masked_equal(clA, 0)
									classArrayAlg =  e.mask * classArrayAlg + clA
									e = None
								clA = None
								classArrayAlg[classArrayAlg == cfg.unclassifiedVal] = 0
								classArrayLCS = cfg.np.where(classArray == cfg.unclassValue, classArrayAlg, classArray)
								if cfg.uidc.LCS_leave_unclassified_checkBox.isChecked():
									pass
								else:
									classArrayLCS = cfg.np.where(classArray == nodataValue, classArrayAlg, classArrayLCS)
							else:
								return "No"
						classArrayWrite = cfg.np.where(classArrayLCS == nodataValue, 0, classArrayLCS)
						# classification raster
						self.writeArrayBlock(outputClassificationRaster, 1, classArrayWrite, pixelStartColumn, pixelStartRow, nodataValue)
						bN = bN + 1
						n = n + 1
					else:
						return "No"
				else:
					return "No"
		elif algorithmName == cfg.algMinDist:
			tr = self.thresholdList(signatureList)
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = cfg.timeSCP.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = cfg.timeSCP.clock()
					# algorithm
					rasterArrayx = cfg.np.copy(rasterArray)
					c = self.algorithmMinimumDistance(rasterArrayx, s, cfg.algBandWeigths)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithmMinimumDistance signature" + str(itCount))
					# threshold
					algThrshld = float(tr[n])
					if algThrshld > 0:
						c = self.minimumDistanceThreshold(c, algThrshld, nodataValue)
					if type(c) is not int:
						oR = outputGdalRasterList[bN]
						if previewSize > 0:
							pixelStartColumn = int(pixelStartColumnPreview)
							pixelStartRow = int(pixelStartRowPreview)
						# algorithm raster
						self.writeArrayBlock(oR, 1, c, pixelStartColumn, pixelStartRow, nodataValue)
						if minArray is None:
							minArray = c
						else:
							minArray = self.findMinimumArray(c, minArray, nodataValue)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMinimumArray signature" + str(itCount))
						# minimum raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, minArray, pixelStartColumn, pixelStartRow, nodataValue)
						# signature classification raster
						if macroclassCheck == "Yes":
							clA = self.classifyClasses(c, minArray, signatureList[n][0])
						else:
							clA = self.classifyClasses(c, minArray, signatureList[n][2])
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
						# classification raster
						if classArray == None:
							classArray = clA
						else:
							e = cfg.np.ma.masked_equal(clA, 0)
							classArray =  e.mask * classArray + clA
							e = None
						clA = None
						classArray[classArray == cfg.unclassifiedVal] = 0
						# classification raster
						self.writeArrayBlock(outputClassificationRaster, 1, classArray, pixelStartColumn, pixelStartRow, nodataValue)
						bN = bN + 1
						n = n + 1
					else:
						return "No"
				else:
					return "No"
		elif algorithmName == cfg.algSAM:
			tr = self.thresholdList(signatureList)
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = cfg.timeSCP.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						#cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
						pass
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = cfg.timeSCP.clock()
					# algorithm
					rasterArrayx = cfg.np.copy(rasterArray)
					c = self.algorithmSAM(rasterArrayx, s, cfg.algBandWeigths)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithmSAM signature" + str(itCount))
					# threshold
					algThrshld = float(tr[n])
					if algThrshld > 0:
						if algThrshld > 90:
							algThrshld = 90
						c = self.minimumDistanceThreshold(c, algThrshld, nodataValue)
					if type(c) is not int:
						oR = outputGdalRasterList[bN]
						if previewSize > 0:
							pixelStartColumn = int(pixelStartColumnPreview)
							pixelStartRow = int(pixelStartRowPreview)
						# algorithm raster
						self.writeArrayBlock(oR, 1, c, pixelStartColumn, pixelStartRow, nodataValue)
						if minArray is None:
							minArray = c
						else:
							minArray = self.findMinimumArray(c, minArray, nodataValue)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMinimumArray signature" + str(itCount))
						# minimum raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, minArray, pixelStartColumn, pixelStartRow, nodataValue)
						# signature classification raster
						if macroclassCheck == "Yes":
							clA = self.classifyClasses(c, minArray, signatureList[n][0])
						else:
							clA = self.classifyClasses(c, minArray, signatureList[n][2])
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
						# classification raster
						if classArray == None:
							classArray = clA
						else:
							e = cfg.np.ma.masked_equal(clA, 0)
							classArray =  e.mask * classArray + clA
							e = None
						clA = None
						classArray[classArray == cfg.unclassifiedVal] = 0
						# classification raster
						self.writeArrayBlock(outputClassificationRaster, 1, classArray, pixelStartColumn, pixelStartRow, nodataValue)
						bN = bN + 1
						n = n + 1
					else:
						return "No"
				else:
					return "No"
		elif algorithmName == cfg.algML:
			covMatrList = self.covarianceMatrixList(signatureList)
			tr = self.thresholdList(signatureList)
			for s in sigArrayList:
				if cfg.actionCheck == "Yes":
					# progress bar
					progress = progressStart + n * progresStep
					EndT = cfg.timeSCP.clock()
					itCount = itCount + 1
					if StartT != 0:
						processT = EndT - StartT
						cfg.remainingTime = (remainingBlocks * itTot  - itCount) * processT
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					elif cfg.remainingTime != 0:
						cfg.uiUtls.updateBar(progress, progressMessage + self.timeToHMS(cfg.remainingTime) + " remaining")
					else:
						cfg.uiUtls.updateBar(progress)
					StartT = cfg.timeSCP.clock()
					# algorithm
					rasterArrayx = cfg.np.copy(rasterArray)
					# threshold
					algThrshld = float(tr[n])
					if algThrshld > 100:
						algThrshld = 100
					c = self.algorithmMaximumLikelihood(rasterArrayx, s, covMatrList[n], cfg.algBandWeigths, algThrshld)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "algorithmMaximumLikelihood signature" + str(itCount))
					if algThrshld > 0:
						c = self.maximumLikelihoodThreshold(c, nodataValue)
					if type(c) is not int:					
						oR = outputGdalRasterList[bN]
						if previewSize > 0:
							pixelStartColumn = int(pixelStartColumnPreview)
							pixelStartRow = int(pixelStartRowPreview)
						# algorithm raster
						self.writeArrayBlock(oR, 1, c, pixelStartColumn, pixelStartRow, nodataValue)
						if maxArray is None:
							maxArray = c
						else:
							maxArray = self.findMaximumArray(c, maxArray, nodataValue)
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "findMaximumArray signature" + str(itCount))
						# maximum raster
						self.writeArrayBlock(outputAlgorithmRaster, 1, maxArray, pixelStartColumn, pixelStartRow, nodataValue)
						# signature classification raster
						if macroclassCheck == "Yes":
							clA = self.classifyClasses(c, maxArray, signatureList[n][0])
						else:
							clA = self.classifyClasses(c, maxArray, signatureList[n][2])
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classifyClasses signature" + str(itCount))
						# classification raster
						if classArray == None:
							classArray = clA
						else:
							e = cfg.np.ma.masked_equal(clA, 0)
							classArray =  e.mask * classArray + clA
							e = None
						clA = None
						classArray[classArray == cfg.unclassifiedVal] = 0
						# classification raster
						self.writeArrayBlock(outputClassificationRaster, 1, classArray, pixelStartColumn, pixelStartRow, nodataValue)
						bN = bN + 1
						n = n + 1
					else:
						return "No"
				else:
					return "No"
		classArray = None
		rasterArrayx = None
		c = None
		try:
			minArray = None
		except:
			pass
		try:
			maxArray = None
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "end classification block")
		return "Yes"
		
	# classify classes
	def classifyClasses(self, algorithmArray, minimumArray, classID, nodataValue = -999):
		if int(classID) == 0:
			classID = cfg.unclassifiedVal
		cB = cfg.np.equal(algorithmArray, minimumArray) * int(classID)
		cA = cfg.np.where(minimumArray != nodataValue, cB, cfg.unclassifiedVal)
		return cA
										
	# classify classes
	def classifyClassesLCSSimple(self, LCSarray, equalArray, classArrayLCS, dataValue, unclassValue, nodataValue, classID):
		cA = cfg.np.where( (LCSarray == dataValue) & (equalArray == dataValue), int(classID), cfg.np.where( (equalArray == unclassValue) & (classArrayLCS <> int(classID) ), unclassValue,classArrayLCS ) )
		return cA
		
	# find minimum array
	def findMinimumArray(self, firstArray, secondArray, nodataValue = -999):
		f = cfg.np.where(firstArray == nodataValue, cfg.maxValDt, firstArray)
		s = cfg.np.where(secondArray == nodataValue, cfg.maxValDt, secondArray)
		n = cfg.np.minimum(f, s)
		m = cfg.np.where(n == cfg.maxValDt, nodataValue, n)
		return m	
		
	# find equal array
	def findEqualArray(self, firstArray, secondArray, dataValue = -1, nodataValue = -999, unclassifiedValue = -1000):
		f = cfg.np.where( (firstArray == dataValue) & (secondArray == dataValue), unclassifiedValue, cfg.np.where(firstArray == unclassifiedValue, unclassifiedValue, cfg.np.where(secondArray == unclassifiedValue, unclassifiedValue, cfg.np.where(firstArray == nodataValue, secondArray, firstArray) ) ) )
		return f
		
	# find maximum array
	def findMaximumArray(self, firstArray, secondArray, nodataValue = -999):
		f = cfg.np.where(firstArray == nodataValue, cfg.maxLikeNoDataVal, firstArray)
		s = cfg.np.where(secondArray == nodataValue, cfg.maxLikeNoDataVal, secondArray)
		m = cfg.np.maximum(f, s)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return m
		
	# set threshold
	def maximumLikelihoodThreshold(self, array, nodataValue = 0):	
		outArray = cfg.np.where(array > cfg.maxLikeNoDataVal, array, nodataValue)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return outArray
		
	# set threshold
	def minimumDistanceThreshold(self, array, threshold, nodataValue = 0):	
		outArray = cfg.np.where(array < threshold, array, nodataValue)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return outArray
		
	# create array from signature list
	def createArrayFromSignature(self, gdalBandList, signatureList):
		arrayList = []
		for s in signatureList:
			val = s[4]
			array = cfg.np.zeros((len(gdalBandList)), dtype=cfg.np.float64)
			max = len(gdalBandList) * 2
			i = 0
			for b in range(0, max, 2):
				array[i] = val[b]
				i = i + 1
			arrayList.append(array)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return arrayList
	
	# minimum Euclidean distance algorithm [ sqrt( sum( (r_i - s_i)^2 ) ) ]
	def algorithmMinimumDistance(self, rasterArray, signatureArray, weightList = None):
		try:
			if weightList is not None:
				c = 0
				for w in weightList:
					rasterArray[:,:,c] *= w
					signatureArray[c] *= w
					c = c + 1
			algArray = cfg.np.sqrt(((rasterArray - signatureArray)**2).sum(axis = 2))
			return algArray
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
		
	# create covariance matrix list from signature list
	def covarianceMatrixList(self, signatureList):
		c = []
		for s in signatureList:
			cov = s[7]
			c.append(cov)
		return c
		
	# create LCSmin LCSmax list from signature list
	def LCSminMaxList(self, signatureList):
		arrayList = []
		for s in signatureList:
			LCSmin = s[8]
			LCSmax = s[9]
			arrayList.append([LCSmin, LCSmax])
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return arrayList

	# create threshold list from signature list
	def thresholdList(self, signatureList):
		c = []
		for s in signatureList:
			t = s[10]
			c.append(t)
		return c
		
	# calculate critical chi square and threshold
	def chisquare(self, algThrshld):
		p = 1 - (algThrshld / 100)
		chi = cfg.statdistrSCP.chi2.isf(p, 4)
		return chi
		
	# Maximum Likelihood algorithm
	def algorithmMaximumLikelihood(self, rasterArray, signatureArray, covarianceMatrixZ, weightList = None, algThrshld = 0):
		try:
			covarianceMatrix = cfg.np.copy(covarianceMatrixZ)
			if weightList is not None:
				c = 0
				for w in weightList:
					rasterArray[:,:,c] *= w
					signatureArray[c] *= w
					c = c + 1
			(sign, logdet) = cfg.np.linalg.slogdet(covarianceMatrix)
			invC = cfg.np.linalg.inv(covarianceMatrix)
			d = rasterArray - signatureArray
			algArray = - logdet - (cfg.np.dot(d, invC) * d).sum(axis = 2)
			if algThrshld > 0:
				chi = self.chisquare(algThrshld)
				threshold = - chi - logdet
				algArray = cfg.np.where(algArray < threshold, cfg.maxLikeNoDataVal, algArray)
			return algArray
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
		
	# spectral angle mapping algorithm [ arccos( sum(r_i * s_i) / ( sum(r_i**2) * sum(s_i**2) ) ) ]
	def algorithmSAM(self, rasterArray, signatureArray, weightList = None):
		try:
			if weightList is not None:
				c = 0
				for w in weightList:
					rasterArray[:,:,c] *= w
					signatureArray[c] *= w
					c = c + 1
			algArray = cfg.np.arccos((rasterArray * signatureArray).sum(axis = 2) / cfg.np.sqrt((rasterArray**2).sum(axis = 2) * (signatureArray**2).sum())) * 180 / cfg.np.pi
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return algArray
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
				
	# land cover signature
	def algorithmLCS(self, rasterArray, signatureArray, LCSmin, LCSmax, multFactor, weightList = None, dataValue = 0, nodataValue = -999):
		try:
			if weightList is not None:
				c = 0
				for w in weightList:
					rasterArray[:,:,c] *= w
					signatureArray[c] *= w
					LCSmin[c] *= w
					LCSmax[c] *= w
					c = c + 1
			condit1 = "cfg.np.where( "
			for i in range(len(signatureArray)):
				condit1 = condit1 + "(cfg.np.around(rasterArray[:,:," + str(i) + "], 11) >= cfg.np.around(" + repr(LCSmin[i] * multFactor) + ", 11)) & (cfg.np.around(rasterArray[:,:," + str(i) + "], 11) <= cfg.np.around(" + repr(LCSmax[i] * multFactor) + ", 11)) & "
			condit1 = condit1[:-4] + "), " +repr(dataValue) +", " + repr(nodataValue) + ")"
			algArray = eval(condit1)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return algArray
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr28()
			return 0
	
##################################
	""" Signature spectral distance functions """
##################################
		
	# calculate Jeffries-Matusita distance Jij = 2[1 − e^(−B)] from Richards, J. A. & Jia, X. 2006. Remote Sensing Digital Image Analysis: An Introduction, Springer.
	def jeffriesMatusitaDistance(self, signatureArrayI, signatureArrayJ, covarianceMatrixI, covarianceMatrixJ, weightList = None):
		try:
			I = cfg.np.array(signatureArrayI)
			J = cfg.np.array(signatureArrayJ)
			cI = cfg.np.copy(covarianceMatrixI)
			cJ = cfg.np.copy(covarianceMatrixJ)
			if weightList is not None:
				c = 0
				for w in weightList:
					I[c] *= w
					J[c] *= w
					c = c + 1
			d = (I - J)
			C = (cI + cJ)/2
			invC = cfg.np.linalg.inv(C)
			dInvC = cfg.np.dot(d.T, invC)
			f = cfg.np.dot(dInvC, d) / 8.0
			(signC, logdetC) = cfg.np.linalg.slogdet(C)
			(signcI, logdetcI) = cfg.np.linalg.slogdet(cI)
			(signcJ, logdetcJ) = cfg.np.linalg.slogdet(cJ)
			s = cfg.np.log(signC * cfg.np.exp(logdetC) / (cfg.np.sqrt(signcI * cfg.np.exp(logdetcI)) * cfg.np.sqrt(signcJ * cfg.np.exp(logdetcJ)))) / 2.0
			B = f + s
			JM = 2 * (1 - cfg.np.exp(-B))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			JM = cfg.notAvailable
		return JM
		
	# calculate transformed divergence dij = 2[1 − e^(−dij/8)] from Richards, J. A. & Jia, X. 2006. Remote Sensing Digital Image Analysis: An Introduction, Springer.
	def transformedDivergence(self, signatureArrayI, signatureArrayJ, covarianceMatrixI, covarianceMatrixJ):
		try:
			I = cfg.np.array(signatureArrayI)
			J = cfg.np.array(signatureArrayJ)
			d = (I - J)
			cI = covarianceMatrixI
			cJ = covarianceMatrixJ
			invCI = cfg.np.linalg.inv(cI)
			invCJ = cfg.np.linalg.inv(cJ)
			p1 = (cI - cJ) * (invCI - invCJ)
			t1 = 0.5 * cfg.np.trace(p1)
			p2 = (invCI + invCJ) * d
			p3 = p2 * d.T
			t2 = 0.5 * cfg.np.trace(p3)
			div = t1 + t2
			TD = 2 * (1 - cfg.np.exp(-div/8.0))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			TD = cfg.notAvailable
		return TD
		
	# Bray-Curtis similarity (100 - 100 * sum(abs(x[ki]-x[kj]) / (sum(x[ki] + x[kj])))
	def brayCurtisSimilarity(self, signatureArrayI, signatureArrayJ):
		try:
			I = cfg.np.array(signatureArrayI)
			J = cfg.np.array(signatureArrayJ)
			sumIJ = I.sum() + J.sum()
			d = cfg.np.sqrt((I - J)**2)
			sim = 100 - d.sum() / sumIJ * 100
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			sim = cfg.notAvailable
		return sim
			
	# Euclidean distance sqrt(sum((x[ki] - x[kj])^2))
	def euclideanDistance(self, signatureArrayI, signatureArrayJ, weightList = None):
		try:
			I = cfg.np.array(signatureArrayI)
			J = cfg.np.array(signatureArrayJ)
			if weightList is not None:
				c = 0
				for w in weightList:
					I[c] *= w
					J[c] *= w
					c = c + 1
			d = (I - J)**2
			dist = cfg.np.sqrt(d.sum())
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			dist = cfg.notAvailable
		return dist		

	# Spectral angle algorithm [ arccos( sum(r_i * s_i) / sqrt( sum(r_i**2) * sum(s_i**2) ) ) ]
	def spectralAngle(self, signatureArrayI, signatureArrayJ, weightList = None):
		try:
			I = cfg.np.array(signatureArrayI)
			J = cfg.np.array(signatureArrayJ)
			if weightList is not None:
				c = 0
				for w in weightList:
					I[c] *= w
					J[c] *= w
					c = c + 1
			angle = cfg.np.arccos((I * J).sum() / cfg.np.sqrt((I**2).sum() * (J**2).sum())) * 180 / cfg.np.pi
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			angle = cfg.notAvailable
		return angle

##################################
	""" Signature functions """
##################################
		
	# calculate ROI signature (one signature for ROIs that have the same macroclass ID and class ID)
	def calculateSignature(self, lyr, rasterName, featureIDList, macroclassID, macroclassInfo, classID, classInfo, progress = None, progresStep = None, plot = "No", tempROI = "No", SCP_UID = None):
		if rasterName is not None and len(rasterName) > 0:
			if progress is not None:
				cfg.uiUtls.updateBar(progress + int((1 / 4) * progresStep))
			else:
				#cfg.uiUtls.updateBar(0)
				pass
			# disable map canvas render for speed
			cfg.cnvs.setRenderFlag(False)
			# date time for temp name
			dT = cfg.utls.getTime()
			# temp subset
			tSN = cfg.subsROINm
			tSD = cfg.tmpDir + "/" + dT + tSN
			# temporary layer
			tLN = cfg.subsTmpROI + dT + ".shp"
			tLP = cfg.tmpDir + "/" + dT + tLN
			# get layer crs
			crs = cfg.utls.getCrs(lyr)
			# create a temp shapefile with a field
			cfg.utls.createEmptyShapefileQGIS(crs, tLP)
			mL = cfg.utls.addVectorLayer(tLP , tLN, "ogr")
			rD = None
			for x in featureIDList:
				# copy ROI to temp shapefile
				cfg.utls.copyFeatureToLayer(lyr, x, mL)
			# calculate ROI center, height and width
			rCX, rCY, rW, rH = cfg.utls.getShapefileRectangleBox(mL)
			if progress is not None:
				cfg.uiUtls.updateBar(progress + int((2 / 4) * progresStep))
			cfg.tblOut = {}
			ROIArray = []
			ROIsize = None
			# band set
			if cfg.bndSetPresent == "Yes" and rasterName == cfg.bndSetNm:
				tLX, tLY, pS = cfg.utls.imageInformation(cfg.bndSet[0])
				cfg.bndSetLst = ""
				# subset 
				for b in range(0, len(cfg.bndSet)):
					tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + str(b) + "_" + dT + ".tif")
					pr = cfg.utls.subsetImage(cfg.bndSet[b], rCX, rCY, int(round(rW/pS + 3)), int(round(rH/pS + 3)), tS)
					if pr == "Yes":
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error edge")
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						return pr
					bX = cfg.utls.clipRasterByShapefile(tLP, tS, None)
					rStat, ar = cfg.utls.getRasterBandStatistics(bX, 1, cfg.bndSetMultAddFactorsList[b])
					if rStat is None:
						cfg.mx.msgErr31()
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						return "No"
					else:
						if ROIsize is None:
							ROIsize = cfg.utls.getROISize(bX, 1, rStat[0], rStat[1])
						rStatStr = str(rStat)
						rStatStr = rStatStr.replace("nan", "0")
						rStat = eval(rStatStr)
						ROIArray.append(ar)
						cfg.bndSetLst = cfg.bndSetLst + str(tS) + ";"
						cfg.tblOut["BAND_" + str(b+1)] = rStat
						cfg.tblOut["WAVELENGTH_" + str(b + 1)] = cfg.bndSetWvLn["WAVELENGTH_" + str(b + 1)]
				cfg.bndSetLst = cfg.bndSetLst.rstrip(';')
			else:
				# subset 
				tLX, tLY, pS = cfg.utls.imageInformation(rasterName)
				tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + dT + ".tif")
				pr = cfg.utls.subsetImage(rasterName, rCX, rCY, int(round(rW/pS + 3)),  int(round(rH/pS + 3)), str(tS))
				if pr == "Yes":
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error edge")
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					return pr
				oList = cfg.utls.rasterToBands(tS, cfg.tmpDir, None, "No", cfg.bndSetMultAddFactorsList)
				rL = cfg.utls.selectLayerbyName(rasterName, "Yes")
				bCount = rL.bandCount()
				for b in range(0, bCount):
					tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + str(b) + "_" + dT + ".tif")
					bX = cfg.utls.clipRasterByShapefile(tLP, oList[b], None)
					rStat, ar = cfg.utls.getRasterBandStatistics(bX, 1)
					if rStat is None:
						cfg.mx.msgErr31()
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						return "No"
					else:
						if ROIsize is None:
							ROIsize = cfg.utls.getROISize(bX, 1, rStat[0], rStat[1])
						rStatStr = str(rStat)
						rStatStr = rStatStr.replace("nan", "0")
						rStat = eval(rStatStr)
						ROIArray.append(ar)
						cfg.tblOut["BAND_" + str(b+1)] = rStat
						cfg.tblOut["WAVELENGTH_" + str(b + 1)] = cfg.bndSetWvLn["WAVELENGTH_" + str(b + 1)]
			if progress is not None:
				cfg.uiUtls.updateBar(progress + int((3 / 4) * progresStep))
			# if not temporary ROI min max
			if tempROI != "MinMax":
				covMat = cfg.utls.calculateCovMatrix(ROIArray)
				if covMat == "No":
					cfg.mx.msgWar12(macroclassID, classID)
			# remove temp layers
			cfg.utls.removeLayer(tLN)
			cfg.tblOut["ROI_SIZE"] = ROIsize
			# if not temporary ROI min max
			if tempROI != "MinMax":
				cfg.utls.ROIStatisticsToSignature(covMat, macroclassID, macroclassInfo, classID, classInfo, cfg.bndSetUnit["UNIT"], plot, tempROI, SCP_UID)
			# enable map canvas render
			cfg.cnvs.setRenderFlag(True)
			if progress is not None:
				cfg.uiUtls.updateBar(progress + int((4 / 4) * progresStep))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi signature calculated")
		else:
			cfg.mx.msg3()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi signature not calculated")
		
	# calculate pixel signature
	def calculatePixelSignature(self, point, rasterName, plot = "No", showPlot = "Yes"):
		if rasterName is not None and len(rasterName) > 0:
			cfg.tblOut = {}
			cfg.tblOut["ROI_SIZE"] = 1
			rStat = []
			# band set
			if cfg.bndSetPresent == "Yes" and rasterName == cfg.bndSetNm:
				for b in range(0, len(cfg.bndSet)):
					rast = cfg.utls.selectLayerbyName(cfg.bndSet[b], "Yes")	
					# open input with GDAL
					try:
						Or = cfg.gdalSCP.Open(rast.source(), cfg.gdalSCP.GA_ReadOnly)
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						cfg.mx.msgErr4()
						return "No"
					OrB = Or.GetRasterBand(1)
					geoT = Or.GetGeoTransform()
					tLX = geoT[0]
					tLY = geoT[3]
					pSX = geoT[1]
					pSY = geoT[5]
					# start and end pixels
					pixelStartColumn = (int((point.x() - tLX) / pSX))
					pixelStartRow = -(int((tLY - point.y()) / pSY))
					bVal = float(cfg.utls.readArrayBlock(OrB, pixelStartColumn, pixelStartRow, 1, 1)) * cfg.bndSetMultiFactorsList[b] + cfg.bndSetAddFactorsList[b]
					rStat = [bVal, bVal, bVal, 0]
					cfg.tblOut["BAND_" + str(b + 1)] = rStat
					cfg.tblOut["WAVELENGTH_" + str(b + 1)] = cfg.bndSetWvLn["WAVELENGTH_" + str(b + 1)] 
			else:
				rL = cfg.utls.selectLayerbyName(rasterName, "Yes")
				# open input with GDAL
				try:
					Or = cfg.gdalSCP.Open(rL.source(), cfg.gdalSCP.GA_ReadOnly)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					cfg.mx.msgErr4()
					return "No"
				bCount = rL.bandCount()
				for b in range(1, bCount + 1):
					OrB = Or.GetRasterBand(b)
					geoT = Or.GetGeoTransform()
					tLX = geoT[0]
					tLY = geoT[3]
					pSX = geoT[1]
					pSY = geoT[5]
					# start and end pixels
					pixelStartColumn = (int((point.x() - tLX) / pSX))
					pixelStartRow = -(int((tLY - point.y()) / pSY))
					bVal = float(cfg.utls.readArrayBlock(OrB, pixelStartColumn, pixelStartRow, 1, 1))  * cfg.bndSetMultiFactorsList[b-1] + cfg.bndSetAddFactorsList[b-1]
					rStat = [bVal, bVal, bVal, 0]
					cfg.tblOut["BAND_" + str(b)] = rStat
					cfg.tblOut["WAVELENGTH_" + str(b)] = cfg.bndSetWvLn["WAVELENGTH_" + str(b)] 
			macroclassID = 0
			classID = 0
			macroclassInfo = cfg.pixelNm
			classInfo = cfg.pixelCoords + " " + str(point)
			covMat = "No"
			val = cfg.utls.ROIStatisticsToSignature(covMat, macroclassID, macroclassInfo, classID, classInfo, cfg.bndSetUnit["UNIT"], plot, "No")
			if showPlot == "Yes":
				cfg.spSigPlot.showSignaturePlotT()
			return val
		
	# Get values for ROI signature
	def ROIStatisticsToSignature(self, covarianceMatrix, macroclassID, macroclassInfo, classID, classInfo, unit = None, plot = "No", tempROI = "No", SCP_UID = None):
		if cfg.rstrNm is not None:
			# band set
			if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
				iB = len(cfg.bndSet)
			else:
				iR = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
				iB = iR.bandCount()
			wvl = []
			val = []
			valM = []
			min = []
			max = []
			vMin = []
			vMax = []
			ROISize = cfg.tblOut["ROI_SIZE"]
			for b in range(1, iB + 1):
				stats = cfg.tblOut["BAND_" + str(b)]
				w = cfg.tblOut["WAVELENGTH_" + str(b)]
				wvl.append(w)
				vMin.append(stats[0])
				vMax.append(stats[1])
				# values for mean and standard deviation
				vM = stats[2]
				vS = stats[3]
				val.append(vM)
				valM.append(vM)
				val.append(vS)
				#min.append(vM - vS)
				#max.append(vM + vS)
				min = vMin
				max = vMax
				c, cc = cfg.utls.randomColor()
			if plot == "No":
				if SCP_UID is None:
					i = cfg.utls.signatureID()
				else:
					i = SCP_UID
				cfg.signList["CHECKBOX_" + str(i)] = cfg.QtSCP.Checked
				cfg.signList["MACROCLASSID_" + str(i)] = macroclassID
				cfg.signList["MACROCLASSINFO_" + str(i)] = macroclassInfo
				cfg.signList["CLASSID_" + str(i)] = classID
				cfg.signList["CLASSINFO_" + str(i)] = classInfo
				cfg.signList["WAVELENGTH_" + str(i)] = wvl
				cfg.signList["VALUES_" + str(i)] = val
				cfg.signList["MIN_VALUE_" + str(i)] = vMin
				cfg.signList["MAX_VALUE_" + str(i)] = vMax
				cfg.signList["ROI_SIZE_" + str(i)] = ROISize
				cfg.signList["LCS_MIN_" + str(i)] = min
				cfg.signList["LCS_MAX_" + str(i)] = max
				cfg.signList["COVMATRIX_" + str(i)] = covarianceMatrix
				cfg.signList["MD_THRESHOLD_" + str(i)] = cfg.algThrshld
				cfg.signList["ML_THRESHOLD_" + str(i)] = cfg.algThrshld
				cfg.signList["SAM_THRESHOLD_" + str(i)] = cfg.algThrshld
				# counter
				n = 0
				m = []
				sdL = []
				for wi in wvl:
					m.append(val[n * 2])
					sdL.append(val[n * 2 +1])
					n = n + 1
				cfg.signList["MEAN_VALUE_" + str(i)] = m
				cfg.signList["SD_" + str(i)] = sdL
				if unit is None:
					unit = cfg.bndSetUnit["UNIT"]
				cfg.signList["UNIT_" + str(i)] = unit
				cfg.signList["COLOR_" + str(i)] = c
				#cfg.signList["COMPL_COLOR_" + str(i)] = cc
				cfg.signIDs["ID_" + str(i)] = i
			# calculation for plot
			elif plot == "Yes":
				if SCP_UID is None:
					i = cfg.utls.signatureID()
				else:
					i = SCP_UID
				cfg.spectrPlotList["CHECKBOX_" + str(i)] = cfg.QtSCP.Checked
				cfg.spectrPlotList["MACROCLASSID_" + str(i)] = macroclassID
				cfg.spectrPlotList["MACROCLASSINFO_" + str(i)] = macroclassInfo
				cfg.spectrPlotList["CLASSID_" + str(i)] = classID
				cfg.spectrPlotList["CLASSINFO_" + str(i)] = classInfo
				cfg.spectrPlotList["WAVELENGTH_" + str(i)] = wvl
				cfg.spectrPlotList["VALUES_" + str(i)] = val
				cfg.spectrPlotList["LCS_MIN_" + str(i)] = vMin
				cfg.spectrPlotList["LCS_MAX_" + str(i)] = vMax
				cfg.spectrPlotList["MIN_VALUE_" + str(i)] = vMin
				cfg.spectrPlotList["MAX_VALUE_" + str(i)] = vMax
				cfg.spectrPlotList["ROI_SIZE_" + str(i)] = ROISize
				cfg.spectrPlotList["COVMATRIX_" + str(i)] = covarianceMatrix
				cfg.spectrPlotList["MD_THRESHOLD_" + str(i)] = cfg.algThrshld
				cfg.spectrPlotList["ML_THRESHOLD_" + str(i)] = cfg.algThrshld
				cfg.spectrPlotList["SAM_THRESHOLD_" + str(i)] = cfg.algThrshld
				# counter
				n = 0
				m = []
				sdL = []
				for wi in wvl:
					m.append(val[n * 2])
					sdL.append(val[n * 2 +1])
					n = n + 1
				cfg.spectrPlotList["MEAN_VALUE_" + str(i)] = m
				cfg.spectrPlotList["SD_" + str(i)] = sdL
				if unit is None:
					unit = cfg.bndSetUnit["UNIT"]
				cfg.spectrPlotList["UNIT_" + str(i)] = unit
				cfg.spectrPlotList["COLOR_" + str(i)] = c
				#cfg.spectrPlotList["COMPL_COLOR_" + str(i)] = cc
				cfg.signPlotIDs["ID_" + str(i)] = i
				if tempROI == "Yes":
					try:
						cfg.tmpROIColor = cfg.spectrPlotList["COLOR_" + str(cfg.tmpROIID)]
						if cfg.spectrPlotList["MACROCLASSINFO_" + str(cfg.tmpROIID)] == cfg.tmpROINm:
							cfg.spSigPlot.removeSignatureByID(cfg.tmpROIID)
							cfg.tmpROIID = i 
							cfg.spectrPlotList["COLOR_" + str(i)] = cfg.tmpROIColor
						else:
							cfg.tmpROIID = i
							cfg.spectrPlotList["COLOR_" + str(i)] = cfg.QtGuiSCP.QColor(cfg.ROIClrVal)
					except:
						cfg.tmpROIID = i
						cfg.spectrPlotList["COLOR_" + str(i)] = cfg.QtGuiSCP.QColor(cfg.ROIClrVal)
					#cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " values to shape concluded, plot: " + str(plot))
			elif plot == "Pixel":
				return valM
			
	# import a shapefile
	def importShapefile(self):
		shpFile = cfg.ui.select_shapefile_label.text()
		if cfg.shpLay is None:
			cfg.mx.msg3()
			return "No"
		if len(shpFile) > 0:
			cfg.uiUtls.addProgressBar()
			cfg.uiUtls.updateBar(10)
			shpName = cfg.osSCP.path.basename(unicode(shpFile))
			tSS = cfg.utls.addVectorLayer(shpFile, shpName, "ogr")
			# create memory layer
			provider = tSS.dataProvider()
			fields = provider.fields()
			tCrs = cfg.utls.getCrs(cfg.shpLay)
			pCrs = cfg.utls.getCrs(tSS)
			f = QgsFeature()
			mcIdF = self.fieldID(tSS, cfg.ui.MC_ID_combo.currentText())
			mcInfoF = self.fieldID(tSS, cfg.ui.MC_Info_combo.currentText())
			cIdF = self.fieldID(tSS, cfg.ui.C_ID_combo.currentText())
			cInfoF = self.fieldID(tSS, cfg.ui.C_Info_combo.currentText())
			for f in tSS.getFeatures():
				cfg.shpLay.startEditing()
				aF = f.geometry()
				if pCrs != tCrs:
					# transform coordinates
					trs = QgsCoordinateTransform(pCrs, tCrs)
					aF.transform(trs)
				oF = QgsFeature()
				oF.setGeometry(aF)
				mcIdV = f.attributes()[mcIdF]
				try:
					mcId = int(mcIdV)
				except:
					mcId = cfg.ROIMacroID
				mcInfo = f.attributes()[mcInfoF]
				cIdV = f.attributes()[cIdF]
				try:
					cId = int(cIdV)
				except:
					cId = cfg.ROIID
				cInfo = f.attributes()[cInfoF]
				i = cfg.utls.signatureID()
				attributeList = [mcId, mcInfo, cId, cInfo, i]
				oF.setAttributes(attributeList)
				cfg.shpLay.addFeature(oF)
				cfg.shpLay.commitChanges()
				cfg.shpLay.dataProvider().createSpatialIndex()
				cfg.shpLay.updateExtents()
				cfg.uiUtls.updateBar(40)
				# calculate signature if checkbox is yes
				if cfg.ui.signature_checkBox_2.isChecked() is True:
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(i))
					cfg.utls.calculateSignature(cfg.shpLay, cfg.rstrNm, rId, mcId, mcInfo, cId, cInfo, None, None, "No", "No", i)	
					cfg.uiUtls.updateBar(90)
					try:
						c = cfg.signList["COLOR_" + str(i)]
						cfg.classD.checkMCIDList(mcId, mcInfo, c)
					except:
						c, cc = cfg.utls.randomColor()
						cfg.classD.checkMCIDList(mcId, mcInfo, c)
			cfg.classD.ROIListTable(cfg.trnLay, cfg.uidc.signature_list_tableWidget)
			cfg.uiUtls.updateBar(100)
			cfg.uiUtls.removeProgressBar()
			
##################################
	""" Process functions """
##################################

	# create value list from text
	def textToValueList(self, text):
		vList = []
		if "," in text:
			c = text.split(",")
		elif "-" in text:
			v = text.split("-")
			for z in range(int(v[0]), int(v[-1]) + 1):
				vList.append(int(z))
			c = []
		else:
			vList.append(int(text))
			c = []
		for b in c:
			if "-" in b:
				v = b.split("-")
				for z in range(int(v[0]), int(v[-1]) + 1):
					vList.append(int(z))
			else:
				vList.append(int(b))
		uList = cfg.np.unique(vList).tolist()
		return uList
			
	# create 3x3 window
	def create3x3Window(self, connection = "8"):
		size = 3
		B = cfg.np.ones((size,size))
		if connection != "8":
			# 4 cells
			B[0,0] = 0
			B[0,2] = 0
			B[2,0] = 0
			B[2,2] = 0
		return B
		
	# scatter plot raster
	def createScatterPlotRasterCondition(self, rangeList, weightList = None, nodataValue = -999):
		if weightList is not None:
			c = 0
			for w in weightList:
				#bandX *= w
				#bandY *= w
				c = c + 1
		condit1 = ""
		condit2 = ""
		bandX = cfg.np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
		bandY = cfg.np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
		for list in rangeList:
			for range in list[0]:
				Xmin = range[0][0]
				Xmax = range[0][1]
				Ymin = range[1][0]
				Ymax = range[1][1]
				condit1 = condit1 + "cfg.np.where( (bandX >= " + str(Xmin) + ") & (bandX <= " + str(Xmax) + ") & (bandY >= " + str(Ymin) + ") & (bandY <= " + str(Ymax) + "), " + str(list[1]) + ", "
				condit2 = condit2 + ")"
		condit1 = condit1[:-2] + ", " + str(nodataValue) + condit2
		try:	
			algArray = eval(condit1)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return 0
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return condit1
		
	# scatter plot raster
	def singleScatterPlotRasterCondition(self, rangeList, weightList = None, nodataValue = -999):
		if weightList is not None:
			c = 0
			for w in weightList:
				#bandX *= w
				#bandY *= w
				c = c + 1
		conditions = []
		for list in rangeList:
			for range in list[0]:
				Xmin = range[0][0]
				Xmax = range[0][1]
				Ymin = range[1][0]
				Ymax = range[1][1]
				condit1 = "cfg.np.where( (bandX >= " + str(Xmin) + ") & (bandX <= " + str(Xmax) + ") & (bandY >= " + str(Ymin) + ") & (bandY <= " + str(Ymax) + "), " + str(list[1]) + ", " + str(nodataValue) + ")"
				conditions.append(condit1)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return conditions
	
	# get UID
	def signatureID(self):
		dT = cfg.utls.getTime()
		r = cfg.randomSCP.randint(100,999)
		i = dT + "_" + str(r)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID" + str(i))
		return i
		
	# calculate unique CID and MCID list
	def calculateUnique_CID_MCID(self):
		unique = []
		if len(cfg.signIDs.values()) > 0:
			for i in cfg.signIDs.values():
				unique.append(str(cfg.signList["CLASSID_" + str(i)]) + "-" + str(cfg.signList["MACROCLASSID_" + str(i)]))
			l = set(unique)
			list = cfg.utls.uniqueToOrderedList(l)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " unique" + str(list))
			return list
		else:
			return "No"
			
	# find DNmin in raster for DOS1
	def findDNmin(self, inputRaster, noDataVal = None):
		DNm = 0
		cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
		cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
		# open input with GDAL
		rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
		# band list
		bL = cfg.utls.readAllBandsFromRaster(rD)
		# No data value
		nD = noDataVal
		o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, None, "UniqueVal")
		cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
		cfg.rasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)
		try:
			cfg.rasterBandUniqueVal.remove(nD)
		except:
			pass
		cfg.rasterBandPixelCount = 0
		o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterValueCount, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, cfg.rasterBandUniqueVal[-1], "Sum")
		sum = cfg.rasterBandPixelCount
		pT1pc = sum * 0.0001
		min = 0
		max = len(cfg.rasterBandUniqueVal)
		for i in range(0, len(cfg.rasterBandUniqueVal)):
			if i == 0:
				pos = int(round((max+min)/4))
			else:
				pos = int(round((max+min)/2))
			DNm = cfg.rasterBandUniqueVal[pos]
			cfg.rasterBandPixelCount = 0
			o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.rasterValueCount, None, None, None, None, 0, None, cfg.NoDataVal, "No", nD, DNm, "DNmin " + str(DNm))
			newSum = cfg.rasterBandPixelCount
			if newSum <= pT1pc:
				min = pos
			else:
				max = pos
			if int(round(max-min)) <= 1:
				break
		for b in range(0, len(bL)):
			bL[b] = None
		rD = None
		cfg.rasterBandUniqueVal = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " DNm " + unicode(DNm))
		return DNm
			
	# unique CID and MCID list to ordered list
	def uniqueToOrderedList(self, uniqueList):
		list = []
		for i in uniqueList:
			v = i.split("-")
			list.append([int(v[0]), int(v[1])])
		sortedList = sorted(list, key=lambda list: (list[0], list[1]))
		return sortedList
			
	# calculate block size
	def calculateBlockSize(self, bandNumber):
		if cfg.sysSCP64bit == "No" and cfg.sysSCPNm == "Windows":
			mem = 512
		else:
			mem = cfg.RAMValue
		b = int((mem / (cfg.arrayUnitMemory * (bandNumber +  5) ))**.5)
		# set system memory max
		if cfg.sysSCP64bit == "No" and b > 2500:
			b = 2500
		# check memory
		try:
			a = cfg.np.zeros((b,b), dtype = cfg.np.float64)
			cfg.uiUtls.updateBar(20,  cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Please wait ..."))
		except:
			for i in reversed(range(128, mem, int(mem/10))):
				try:
					b = int((i / (cfg.arrayUnitMemory * (bandNumber +  5) ))**.5)
					# set system memory max
					if cfg.sysSCP64bit == "No" and b > 2500:
						b = 2500
					a = cfg.np.zeros((int(b),int(b)), dtype = cfg.np.float64)
					size = a.nbytes / 1048576
					cfg.ui.RAM_spinBox.setValue(size * bandNumber)
					cfg.mx.msgWar11()
					cfg.uiUtls.updateBar(20,  cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Please wait ..."))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "block = " + str(b))
					return b
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "block = " + str(b))
		return b
	
	# check band set and create band set list
	def checkBandSet(self):
		ck = "Yes"
		# list of bands for algorithm
		cfg.bndSetLst = []
		for x in range(0, len(cfg.bndSet)):
			b = cfg.utls.selectLayerbyName(cfg.bndSet[x], "Yes")
			if b is not None:
				cfg.bndSetLst.append(b.source())
			else:
				ck = "No"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " raster is not loaded: " + unicode(cfg.bndSet[x]))
				return ck
		return ck

	# check if the clicked point is inside the image
	def checkPointImage(self, imageName, point, quiet = "No"):
		# band set
		if cfg.bndSetPresent == "Yes" and imageName == cfg.bndSetNm:
			imageName = cfg.bndSet[0]
			# image CRS
			bN0 = self.selectLayerbyName(imageName, "Yes")
			iCrs = self.getCrs(bN0)
			if iCrs is None:
				iCrs = cfg.utls.getQGISCrs()
				pCrs = iCrs
			else:
				# projection of input point from project's crs to raster's crs
				pCrs = cfg.utls.getQGISCrs()
				if pCrs != iCrs:
					try:
						point = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
						if point is False:
							cfg.pntCheck = "No"
							cfg.utls.setQGISCrs(iCrs)
							return "No"
					# Error latitude or longitude exceeded limits
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						crs = None
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + ": latitude or longitude exceeded limits")
						cfg.pntCheck = "No"
						return "No"
			# workaround coordinates issue
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "project crs: " + unicode(pCrs.toProj4()) + " - raster " + unicode(imageName) + " crs: " + unicode(iCrs.toProj4()))
			cfg.lstPnt = QgsPoint(point.x() / float(1), point.y() / float(1))
			pX = point.x()
			pY = point.y()
			i = self.selectLayerbyName(imageName, "Yes")
			if i is not None:
				# Point Check	
				cfg.pntCheck = None
				if pX > i.extent().xMaximum() or pX < i.extent().xMinimum() or pY > i.extent().yMaximum() or pY < i.extent().yMinimum() :
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "point outside the image area")
					if quiet == "No":
						cfg.mx.msg6()
					cfg.pntCheck = "No"
				else :
					cfg.pntCheck = "Yes"
					return cfg.lstPnt
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image missing")
				if quiet == "No":
					cfg.mx.msg4()
					cfg.pntCheck = "No"
		else:
			if self.selectLayerbyName(imageName, "Yes") is None:
				if quiet == "No":
					cfg.mx.msg4()
				#cfg.ipt.refreshRasterLayer()
				self.pntROI = None
				cfg.pntCheck = "No"
			else:
				# image CRS
				bN0 = self.selectLayerbyName(imageName, "Yes")
				iCrs = self.getCrs(bN0)
				if iCrs is None:
					iCrs = None
				else:
					# projection of input point from project's crs to raster's crs
					pCrs = cfg.utls.getQGISCrs()
					if pCrs != iCrs:
						try:
							point = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
							if point is False:
								cfg.pntCheck = "No"
								cfg.utls.setQGISCrs(iCrs)
								return "No"
						# Error latitude or longitude exceeded limits
						except Exception, err:
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
							crs = None
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Error") + ": latitude or longitude exceeded limits")
							cfg.pntCheck = "No"
							return "No"
				# workaround coordinates issue
				if quiet == "No":
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "project crs: " + unicode(pCrs.toProj4()) + " - raster " + unicode(imageName) + " crs: " + unicode(iCrs.toProj4()))
				cfg.lstPnt = QgsPoint(point.x() / float(1), point.y() / float(1))
				pX = point.x()
				pY = point.y()
				i = self.selectLayerbyName(imageName, "Yes")
				# Point Check	
				cfg.pntCheck = None
				if pX > i.extent().xMaximum() or pX < i.extent().xMinimum() or pY > i.extent().yMaximum() or pY < i.extent().yMinimum() :
					if quiet == "No":
						cfg.mx.msg6()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "point outside the image area")
					cfg.pntCheck = "No"
				else :
					cfg.pntCheck = "Yes"
					return cfg.lstPnt
		
	# create virtual raster with Python
	def createVirtualRaster2(self, inputRasterList, output, bandNumberList = "No", quiet = "No", NoDataVal = "No", relativeToVRT = 0, pansharp = "No", intersection = "Yes", boxCoordList = None):
		# create virtual raster
		drv = cfg.gdalSCP.GetDriverByName("VRT")
		rXList = []
		rYList = []
		topList = []
		leftList = []
		rightList = []
		bottomList = []
		pXSizeList = []
		pYSizeList = []
		for b in inputRasterList:
			gdalRaster = cfg.gdalSCP.Open(b, cfg.gdalSCP.GA_ReadOnly)	
			gt = gdalRaster.GetGeoTransform()
			rP = gdalRaster.GetProjection()
			if rP == "":
				cfg.mx.msgErr47()
				return "Yes"
			pXSizeList.append(abs(gt[1]))
			pYSizeList.append(abs(gt[5]))
			leftList.append(gt[0])
			topList.append(gt[3])
			rightList.append(gt[0] + gt[1] * gdalRaster.RasterXSize)
			bottomList.append(gt[3] + gt[5] * gdalRaster.RasterYSize)
			# number of x pixels
			rXList.append(float(gdalRaster.RasterXSize))
			# number of y pixels
			rYList.append(float(gdalRaster.RasterYSize))
			gdalRaster = None
		# find raster box
		iLeft = min(leftList)
		iTop= max(topList)
		iRight= max(rightList)
		iBottom= min(bottomList)
		# find intersection box
		xLeft = max(leftList)
		xTop= min(topList)
		xRight= min(rightList)
		xBottom= max(bottomList)
		# highest resolution
		pXSize = min(pXSizeList)
		pYSize = min(pYSizeList)
		if boxCoordList is not None:
			try:
				override = boxCoordList[4]
				if override == "Yes":
					# find raster box
					if iLeft < boxCoordList[0]:
						iLeft = iLeft +abs(int(round((iLeft - boxCoordList[0]) / pXSize))) * pXSize
					else:
						iLeft = iLeft - abs(int(round((iLeft - boxCoordList[0]) / pXSize))) * pXSize
					if iTop > boxCoordList[1]:
						iTop= iTop - abs(int(round((iTop -boxCoordList[1]) / pYSize))) * pYSize
					else:
						iTop= iTop + abs(int(round((iTop -boxCoordList[1]) / pYSize))) * pYSize
					if iRight > boxCoordList[2]:
						iRight = iRight - abs(int(round((iRight - boxCoordList[2])  / pXSize))) * pXSize
					else:
						iRight = iRight + abs(int(round((iRight - boxCoordList[2])  / pXSize))) * pXSize
					if iBottom < boxCoordList[3]:
						iBottom = iBottom + abs(int(round((iBottom - boxCoordList[3]) / pYSize))) * pYSize
					else:
						iBottom = iBottom - abs(int(round((iBottom - boxCoordList[3]) / pYSize))) * pYSize
			except:
				# find raster box
				if iLeft < boxCoordList[0]:
					iLeft = iLeft +abs(int(round((iLeft - boxCoordList[0]) / pXSize))) * pXSize
				if iTop > boxCoordList[1]:
					iTop= iTop - abs(int(round((iTop -boxCoordList[1]) / pYSize))) * pYSize
				if iRight > boxCoordList[2]:
					iRight = iRight - abs(int(round((iRight - boxCoordList[2])  / pXSize))) * pXSize
				if iBottom < boxCoordList[3]:
					iBottom = iBottom + abs(int(round((iBottom - boxCoordList[3]) / pYSize))) * pYSize
				# find intersection box
				if xLeft < boxCoordList[0]:
					xLeft =  xLeft +abs(int(round((xLeft - boxCoordList[0]) / pXSize))) * pXSize				
				if xTop > boxCoordList[1]:
					xTop= xTop - abs(int(round((xTop -boxCoordList[1]) / pYSize))) * pYSize
				if xRight > boxCoordList[2]:
					xRight= xRight - abs(int(round((xRight - boxCoordList[2])  / pXSize))) * pXSize
				if xBottom < boxCoordList[3]:
					xBottom = xBottom + abs(int(round((xBottom - boxCoordList[3]) / pYSize))) * pYSize
		# number of x pixels
		if intersection == "Yes":
			rX = abs(int(round((xRight - xLeft) / pXSize)))
			rY = abs(int(round((xTop - xBottom) / pYSize)))
		else:
			rX = abs(int(round((iRight - iLeft) / pXSize)))
			rY = abs(int(round((iTop - iBottom) / pYSize)))
		# create virtual raster
		vRast = drv.Create(output, rX, rY, 0)
		# set raster projection from reference intersection
		if intersection == "Yes":
			vRast.SetGeoTransform((xLeft, pXSize, 0, xTop, 0, -pYSize))
		else:
			vRast.SetGeoTransform((iLeft, pXSize, 0, iTop, 0, -pYSize))
		vRast.SetProjection(rP)
		if len(inputRasterList) == 1 and bandNumberList != "No":
			x = 0
			gdalRaster2 = cfg.gdalSCP.Open(b, cfg.gdalSCP.GA_ReadOnly)			
			try:
				for b in bandNumberList:
					gBand2 = gdalRaster2.GetRasterBand(int(b)) 
					noData = gBand2.GetNoDataValue()
					if noData is None or str(noData) == "nan":
						noData = cfg.NoDataVal
					gt = gdalRaster2.GetGeoTransform()
					pX =  abs(gt[1])
					pY = abs(gt[5])
					left = gt[0]
					top = gt[3]
					bsize2 = gBand2.GetBlockSize()
					x_block = bsize2[0]
					y_block = bsize2[1]
					# number of x pixels
					rX2 = gdalRaster2.RasterXSize * int(round(pX / pXSize))
					# number of y pixels
					rY2 = gdalRaster2.RasterYSize * int(round(pY / pYSize))
					# offset
					if intersection == "Yes":
						xoffX = abs(int(round((left - xLeft) / pX)))
						xoffY = abs(int(round((xTop - top) / pY)))
						offX = 0
						offY = 0
					else:
						offX = abs(int(round((left - iLeft) / pXSize)))
						offY = int(round((iTop - top) / pYSize))
						xoffX = 0
						xoffY = 0
					try:
						override = boxCoordList[4]
						if override == "Yes":
							if iLeft < left:
								xoffX = 0
								offX = abs(int(round((left - iLeft) / pXSize)))
							else:
								xoffX = abs(int(round((left - iLeft) / pX)))
								offX = 0
							if iTop > top:
								xoffY = 0
								offY = abs(int(round((iTop - top) / pYSize)))
							else:
								xoffY = abs(int(round((iTop - top) / pY)))
								offY = 0
					except:
						pass
					vRast.AddBand(cfg.gdalSCP.GDT_Float32)
					bandNumber = bandNumberList[x]
					band = vRast.GetRasterBand(x + 1)
					bsize = band.GetBlockSize()
					x_block = bsize[0]
					y_block = bsize[1]
					source_path = inputRasterList[0]
					# set metadata xml
					xml = """
					<ComplexSource>
					  <SourceFilename relativeToVRT="%i">%s</SourceFilename>
					  <SourceBand>%i</SourceBand>
					  <SourceProperties RasterXSize="%i" RasterYSize="%i" DataType=%s BlockXSize="%i" BlockYSize="%i" />
					  <SrcRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
					  <DstRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
					  <NODATA>%i</NODATA>
					</ComplexSource>
					"""
					source = xml % (relativeToVRT, source_path.encode(cfg.sysSCP.getfilesystemencoding()), bandNumber, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, "Float64", x_block, y_block, xoffX, xoffY, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, offX, offY, rX2, rY2, noData)
					band.SetMetadataItem("ComplexSource", source, "new_vrt_sources")
					if NoDataVal == "Yes":
						band.SetNoDataValue(noData)	
					elif NoDataVal != "No":
						band.SetNoDataValue(NoDataVal)
					band = None
					gBand2 = None
					x = x + 1
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			gdalRaster2 = None
		else:
			x = 0
			for b in inputRasterList:
				gdalRaster2 = cfg.gdalSCP.Open(b, cfg.gdalSCP.GA_ReadOnly)
				gdalBandNumber = gdalRaster2.RasterCount
				for bb in range(1, gdalBandNumber + 1):
					gBand2 = gdalRaster2.GetRasterBand(bb) 
					noData = gBand2.GetNoDataValue()
					if noData is None:
						noData = cfg.NoDataVal
					gt = gdalRaster2.GetGeoTransform()
					pX =  abs(gt[1])
					pY = abs(gt[5])
					left = gt[0]
					top = gt[3]
					bsize2 = gBand2.GetBlockSize()
					x_block = bsize2[0]
					y_block = bsize2[1]
					# number of x pixels
					rX2 = gdalRaster2.RasterXSize * int(round(pX / pXSize))
					# number of y pixels
					rY2 = gdalRaster2.RasterYSize * int(round(pY / pYSize))
					# offset
					if intersection == "Yes":
						xoffX = abs(int(round((left - xLeft) / pX)))
						xoffY = abs(int(round((xTop - top) / pY)))
						offX = 0
						offY = 0
					else:
						offX = abs(int(round((left - iLeft) / pXSize)))
						offY = int(round((iTop - top) / pYSize))
						xoffX = 0
						xoffY = 0
					try:
						override = boxCoordList[4]
						if override == "Yes":
							if iLeft < left:
								xoffX = 0
								offX = abs(int(round((left - iLeft) / pXSize)))
							else:
								xoffX = abs(int(round((left - iLeft) / pX)))
								offX = 0
							if iTop > top:
								xoffY = 0
								offY = abs(int(round((iTop - top) / pYSize)))
							else:
								xoffY = abs(int(round((iTop - top) / pY)))
								offY = 0
					except:
						pass
					gBand2 = None
					vRast.AddBand(cfg.gdalSCP.GDT_Float32)
					try:
						errorCheck = "Yes"
						if bandNumberList == "No":
							bandNumber = 1
						else:
							bandNumber = bandNumberList[x]
						errorCheck = "No"	
						band = vRast.GetRasterBand(x + 1)
						bsize = band.GetBlockSize()
						x_block = bsize[0]
						y_block = bsize[1]
						source_path = b.replace("//", "/")
						# set metadata xml
						xml = """
						<ComplexSource>
						  <SourceFilename relativeToVRT="%i">%s</SourceFilename>
						  <SourceBand>%i</SourceBand>
						  <SourceProperties RasterXSize="%i" RasterYSize="%i" DataType=%s BlockXSize="%i" BlockYSize="%i" />
						  <SrcRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
						  <DstRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
						  <NODATA>%i</NODATA>
						</ComplexSource>
						"""
						source = xml % (relativeToVRT, source_path.encode(cfg.sysSCP.getfilesystemencoding()), bandNumber, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, "Float64", x_block, y_block, xoffX, xoffY, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, offX, offY, rX2, rY2, noData)
						band.SetMetadataItem("ComplexSource", source, "new_vrt_sources")
						if NoDataVal == "Yes":
							band.SetNoDataValue(noData)	
						elif NoDataVal != "No":
							band.SetNoDataValue(NoDataVal)
						band = None
						x = x + 1
					except Exception, err:
						if errorCheck == "No":
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				gdalRaster2 = None
		vRast = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "virtual raster: " + unicode(output))
		return unicode(output)

	# calculate raster block ranges
	def rasterBlocks(self, gdalRaster, blockSizeX = 1, blockSizeY = 1, previewSize = 0, previewPoint = None):
		# number of x pixels
		rX = gdalRaster.RasterXSize
		# number of y pixels
		rY = gdalRaster.RasterYSize
		# list of range pixels
		lX = None
		lY = None
		if blockSizeX != 1 or blockSizeY !=1:
			lX = range(0, rX, blockSizeX)
			lY = range(0, rY, blockSizeY)
		# classification preview
		if previewPoint != None:
			geoT = gdalRaster.GetGeoTransform()
			tLX = geoT[0]
			tLY = geoT[3]
			pSX = geoT[1]
			pSY = geoT[5]
			# start and end pixels
			sX = (int((previewPoint.x() - tLX) / pSX)) - int(previewSize / 2)
			eX = (int((previewPoint.x() - tLX) / pSX)) + int(previewSize / 2)
			sY = -(int((tLY - previewPoint.y()) / pSY)) - int(previewSize / 2)
			eY = -(int((tLY - previewPoint.y()) / pSY)) + int(previewSize / 2)
			# if start outside image
			if sX < 0:
				sX = 0
			if sY < 0:
				sY = 0
			if eX > rX:
				eX = rX
			if eY > rY:
				eY = rY
			if blockSizeX > previewSize:
					blockSizeX = previewSize
			if blockSizeY > previewSize:
					blockSizeY = previewSize
			# raster range blocks
			if previewSize > 1:
				lX = range(sX, eX, blockSizeX)
				lY = range(sY, eY, blockSizeY)
			else:
				lX = [sX]
				lY = [sY]
			# preview range blocks
			pX = range(0, previewSize, blockSizeX)
			pY = range(0, previewSize, blockSizeY)
		# if not preview
		else:
			# set pX and pY if not preview
			pX = lX
			pY = lY
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return rX, rY, lX, lY, pX, pY
		
	# read a block of band as array
	def readArrayBlock(self, gdalBand, pixelStartColumn, pixelStartRow, blockColumns, blockRow):
		#gdalBand.SetNoDataValue(-999)
		a = gdalBand.ReadAsArray(pixelStartColumn, pixelStartRow, blockColumns, blockRow)
		return a
		
	# apply multiplicative and additivie factors to array
	def arrayMultiplicativeAdditiveFactors(self, array, multiplicativeFactor, additiveFactor):
		a = array * float(multiplicativeFactor) + float(additiveFactor)
		return a
		
	# write an array to band
	def writeArrayBlock(self, gdalRaster, bandNumber, dataArray, pixelStartColumn, pixelStartRow, nodataValue=None):
		b = gdalRaster.GetRasterBand(bandNumber)
		x = gdalRaster.RasterXSize - pixelStartColumn 
		y = gdalRaster.RasterYSize - pixelStartRow
		dataArray = dataArray[:y, :x]
		b.WriteArray(dataArray, pixelStartColumn, pixelStartRow)
		if nodataValue is not None:
			b.SetNoDataValue(nodataValue)
		b.FlushCache()
		b = None
	
	# create raster from another raster
	def createRasterFromReference(self, gdalRasterRef, bandNumber, outputRasterList, nodataValue = None, driver = "GTiff", format = "Float32", previewSize = 0, previewPoint = None, compress = "No", compressFormat = "DEFLATE21", projection = None, geotransform = None):
		oRL = []
		if format == "Float64":
			format = cfg.gdalSCP.GDT_Float64
		elif format == "Float32":
			format = cfg.gdalSCP.GDT_Float32
		for o in outputRasterList:
			# pixel size and origin from reference
			if projection is None:
				rP = gdalRasterRef.GetProjection()
			else:
				rP = projection
			if geotransform is None:
				rGT = gdalRasterRef.GetGeoTransform()
			else:
				rGT = geotransform
			tD = cfg.gdalSCP.GetDriverByName(driver)
			c = gdalRasterRef.RasterXSize
			r = gdalRasterRef.RasterYSize
			if previewSize > 0:
				tLX = rGT[0]
				tLY = rGT[3]
				pSX = rGT[1]
				pSY = rGT[5]
				sX = int((previewPoint.x() - tLX) / pSX) - int(previewSize / 2)
				sY = int((tLY - previewPoint.y()) / cfg.np.sqrt(pSY ** 2)) - int(previewSize / 2)
				lX = tLX + sX * pSX
				tY = tLY + sY * pSY
				if tY > tLY:
					tY = tLY
				if lX < tLX:
					lX = tLX
				if previewSize < c:
					c = previewSize
				if previewSize < r:
					r = previewSize
				rGT = (lX, rGT[1], rGT[2], tY,  rGT[4],  rGT[5])
			if compress == "No":
				oR = tD.Create(o, c, r, bandNumber, format)
			elif compress == "DEFLATE21":
				oR = tD.Create(o, c, r, bandNumber, format, options = ['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=1'])
			else:
				oR = tD.Create(o, c, r, bandNumber, format, ['COMPRESS=' + compressFormat])
			# set raster projection from reference
			oR.SetGeoTransform(rGT)
			oR.SetProjection(rP)
			oRL.append(oR)
			if nodataValue is not None:
				for x in range(1, bandNumber+1):
					b = oR.GetRasterBand(x)
					b.SetNoDataValue(nodataValue)
					b.Fill(nodataValue)
					b = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(outputRasterList))
		return oRL
		
	# clip a raster using a shapefile
	def clipRasterByShapefile(self,  shapefile, raster, outputRaster = None, outFormat = "GTiff"):
		# date time for temp name
		dT = cfg.utls.getTime()
		if outputRaster is None:
			# temp files
			tRN = cfg.copyTmpROI + dT + ".tif"
			tR = str(cfg.tmpDir + "//" + tRN)
		else:
			tR = str(outputRaster)
		# convert polygon to raster 
		tRNxs = cfg.copyTmpROI + dT + "xs.tif"
		tRxs = str(cfg.tmpDir + "//" + tRNxs)
		burnValues = 1
		conversionType = None
		if cfg.osSCP.path.isfile(shapefile):
			check = cfg.utls.vectorToRaster(cfg.emptyFN, shapefile, cfg.emptyFN, tRxs, raster, conversionType, "GTiff", burnValues)
		else:
			return "No"
		if check != "No":
			cfg.utls.clipRasterByRaster(raster, tRxs, tR, outFormat, cfg.NoDataVal)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "shapefile " + unicode(shapefile) + "raster " + unicode(raster) + "tR " + unicode(tR))
			return tR
		else:
			return "No"
		
	# clip raster with another raster
	def clipRasterByRaster(self, rasterClipped, rasterClipping, outputRaster = None, outFormat = "GTiff", nodataValue=None):
		dT = self.getTime()
		tPMN = cfg.tmpVrtNm + ".vrt"
		tPMD = cfg.tmpDir + "/" + dT + tPMN
		bList = [rasterClipped, rasterClipping]
		iBC = cfg.utls.getNumberBandRaster(rasterClipped)
		# create band list of clipped bands and clipping band
		bandNumberList = []
		for cc in range(1, iBC + 1):
			bandNumberList.append(cc)
		bandNumberList.append(1)
		vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", cfg.NoDataVal, 0)
		# open input with GDAL
		rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
		if rD is None:
			cfg.mx.msg4()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " None raster")
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			return "No"
		try:
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			bC = len(bL)
			# output rasters
			oM = []
			oM.append(outputRaster)
			oMR = cfg.utls.createRasterFromReference(rD, bC - 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, "No")
			for bb in range(0, bC - 1):
				e = str("a * b")
				variableList = [["im1", "a"], ["im2", "b"]]
				o = cfg.utls.processRaster(rD, [bL[bb], bL[bC - 1]], None, "No", cfg.utls.bandCalculation, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "No")
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster " + unicode(outputRaster))
		return outputRaster
		
	# copy a raster
	def copyRaster(self, raster, outputRaster = None, outFormat = "GTiff", nodataValue=None):
		# open input with GDAL
		rD = cfg.gdalSCP.Open(raster, cfg.gdalSCP.GA_ReadOnly)
		if rD is None:
			cfg.mx.msg4()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " None raster")
			return "No"
		# band list
		bL = cfg.utls.readAllBandsFromRaster(rD)
		bC = len(bL)
		# output rasters
		oM = []
		oM.append(outputRaster)
		oMR = cfg.utls.createRasterFromReference(rD, bC, oM, nodataValue, outFormat, cfg.rasterDataType, 0,  None, "No")
		for bb in range(0, bC):
			e = str("a * 1")
			variableList = [["im1", "a"]]
			o = cfg.utls.processRaster(rD, [bL[bb]], None, "No", cfg.utls.bandCalculation, None, oMR , None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "No")
		# close GDAL rasters
		for b in range(0, len(oMR)):
			oMR[b] = None
		for b in range(0, len(bL)):
			bL[b] = None
		rD = None
		return outputRaster
		
	# find nearest value in list
	def findNearestValueinList(self, list, value, threshold):
		if len(list) > 0:
			arr = cfg.np.asarray(list)
			v = (cfg.np.abs(arr - value)).argmin()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "find nearest" + unicode(value))
			if cfg.np.abs(arr[v] - value) < threshold:
				return arr[v]
			else:
				return None
		else:
			return None
	
	# find band set number used for vegetation index calculation
	def findBandNumber(self):
		cfg.REDBand = None
		cfg.NIRBand = None
		cfg.BLUEBand = None
		try:
			cfg.bndSetUnit["UNIT"]
		except:
			return "No"
		if cfg.bndSetUnit["UNIT"] != cfg.noUnit:
			if cfg.bndSetUnit["UNIT"] == cfg.unitNano:
				RED = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.REDCenterBand*1000, cfg.REDThreshold*1000)
				NIR = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.NIRCenterBand*1000, cfg.NIRThreshold*1000)
				BLUE = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.BLUECenterBand*1000, cfg.BLUEThreshold*1000)
			elif cfg.bndSetUnit["UNIT"] == cfg.unitMicro:
				RED = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.REDCenterBand, cfg.REDThreshold)
				NIR = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.NIRCenterBand, cfg.NIRThreshold)
				BLUE = self.findNearestValueinList(cfg.bndSetWvLn.values(), cfg.BLUECenterBand, cfg.BLUEThreshold)
			if RED is not None and NIR is not None:
				for band, value in cfg.bndSetWvLn.items():
					if value == RED:
						bN = band.replace("WAVELENGTH_", "")
						cfg.REDBand = int(bN)
					elif value == NIR:
						bN = band.replace("WAVELENGTH_", "")
						cfg.NIRBand = int(bN)
			if BLUE is not None:
				for band, value in cfg.bndSetWvLn.items():
					if value == BLUE:
						bN = band.replace("WAVELENGTH_", "")
						cfg.BLUEBand = int(bN)
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "RED =" + str(cfg.REDBand) + ", NIR =" + str(cfg.NIRBand) + ", BLUE =" + str(cfg.BLUEBand))
		
	# calculation of earth sun distance
	def calculateEarthSunDistance(self, date, dateFormat):
		dStr = cfg.datetimeSCP.datetime.strptime(date, dateFormat)
		dStrT = dStr.timetuple()
		# calculate julian day
		day = dStrT.tm_yday
		# Earth Sun distance from http://landsathandbook.gsfc.nasa.gov/excel_docs/d.xls
		dL = [0.98331, 0.98330, 0.98330, 0.98330, 0.98330, 0.98332, 0.98333, 0.98335, 0.98338, 0.98341, 0.98345, 0.98349, 0.98354, 0.98359, 0.98365, 0.98371, 0.98378, 0.98385,
						0.98393, 0.98401, 0.98410, 0.98419, 0.98428, 0.98439, 0.98449, 0.98460, 0.98472, 0.98484, 0.98496, 0.98509, 0.98523, 0.98536, 0.98551, 0.98565, 0.98580, 0.98596, 0.98612,
						0.98628, 0.98645, 0.98662, 0.98680, 0.98698, 0.98717, 0.98735, 0.98755, 0.98774, 0.98794, 0.98814, 0.98835, 0.98856, 0.98877, 0.98899, 0.98921, 0.98944, 0.98966, 0.98989,
						0.99012, 0.99036, 0.99060, 0.99084, 0.99108, 0.99133, 0.99158, 0.99183, 0.99208, 0.99234, 0.99260, 0.99286, 0.99312, 0.99339, 0.99365, 0.99392, 0.99419, 0.99446, 0.99474,
						0.99501, 0.99529, 0.99556, 0.99584, 0.99612, 0.99640, 0.99669, 0.99697, 0.99725, 0.99754, 0.99782, 0.99811, 0.99840, 0.99868, 0.99897, 0.99926, 0.99954, 0.99983, 1.00012,
						1.00041, 1.00069, 1.00098, 1.00127, 1.00155, 1.00184, 1.00212, 1.00240, 1.00269, 1.00297, 1.00325, 1.00353, 1.00381, 1.00409, 1.00437, 1.00464, 1.00492, 1.00519, 1.00546,
						1.00573, 1.00600, 1.00626, 1.00653, 1.00679, 1.00705, 1.00731, 1.00756, 1.00781, 1.00806, 1.00831, 1.00856, 1.00880, 1.00904, 1.00928, 1.00952, 1.00975, 1.00998, 1.01020,
						1.01043, 1.01065, 1.01087, 1.01108, 1.01129, 1.01150, 1.01170, 1.01191, 1.01210, 1.01230, 1.01249, 1.01267, 1.01286, 1.01304, 1.01321, 1.01338, 1.01355, 1.01371, 1.01387,
						1.01403, 1.01418, 1.01433, 1.01447, 1.01461, 1.01475, 1.01488, 1.01500, 1.01513, 1.01524, 1.01536, 1.01547, 1.01557, 1.01567, 1.01577, 1.01586, 1.01595, 1.01603, 1.01610,
						1.01618, 1.01625, 1.01631, 1.01637, 1.01642, 1.01647, 1.01652, 1.01656, 1.01659, 1.01662, 1.01665, 1.01667, 1.01668, 1.01670, 1.01670, 1.01670, 1.01670, 1.01669, 1.01668,
						1.01666, 1.01664, 1.01661, 1.01658, 1.01655, 1.01650, 1.01646, 1.01641, 1.01635, 1.01629, 1.01623, 1.01616, 1.01609, 1.01601, 1.01592, 1.01584, 1.01575, 1.01565, 1.01555,
						1.01544, 1.01533, 1.01522, 1.01510, 1.01497, 1.01485, 1.01471, 1.01458, 1.01444, 1.01429, 1.01414, 1.01399, 1.01383, 1.01367, 1.01351, 1.01334, 1.01317, 1.01299, 1.01281,
						1.01263, 1.01244, 1.01225, 1.01205, 1.01186, 1.01165, 1.01145, 1.01124, 1.01103, 1.01081, 1.01060, 1.01037, 1.01015, 1.00992, 1.00969, 1.00946, 1.00922, 1.00898, 1.00874,
						1.00850, 1.00825, 1.00800, 1.00775, 1.00750, 1.00724, 1.00698, 1.00672, 1.00646, 1.00620, 1.00593, 1.00566, 1.00539, 1.00512, 1.00485, 1.00457, 1.00430, 1.00402, 1.00374,
						1.00346, 1.00318, 1.00290, 1.00262, 1.00234, 1.00205, 1.00177, 1.00148, 1.00119, 1.00091, 1.00062, 1.00033, 1.00005, 0.99976, 0.99947, 0.99918, 0.99890, 0.99861, 0.99832,
						0.99804, 0.99775, 0.99747, 0.99718, 0.99690, 0.99662, 0.99634, 0.99605, 0.99577, 0.99550, 0.99522, 0.99494, 0.99467, 0.99440, 0.99412, 0.99385, 0.99359, 0.99332, 0.99306,
						0.99279, 0.99253, 0.99228, 0.99202, 0.99177, 0.99152, 0.99127, 0.99102, 0.99078, 0.99054, 0.99030, 0.99007, 0.98983, 0.98961, 0.98938, 0.98916, 0.98894, 0.98872, 0.98851,
						0.98830, 0.98809, 0.98789, 0.98769, 0.98750, 0.98731, 0.98712, 0.98694, 0.98676, 0.98658, 0.98641, 0.98624, 0.98608, 0.98592, 0.98577, 0.98562, 0.98547, 0.98533, 0.98519,
						0.98506, 0.98493, 0.98481, 0.98469, 0.98457, 0.98446, 0.98436, 0.98426, 0.98416, 0.98407, 0.98399, 0.98391, 0.98383, 0.98376, 0.98370, 0.98363, 0.98358, 0.98353, 0.98348,
						0.98344, 0.98340, 0.98337, 0.98335, 0.98333, 0.98331]
		eSD = dL[day - 1]	
		return eSD
	
	# calculate NDVI
	def calculateNDVI(self, NIR, RED):
		NDVI = (NIR - RED) / (NIR + RED)
		if NDVI > 1:
			NDVI = 1
		elif NDVI < -1:
			NDVI = -1
		return NDVI
		
	# calculate EVI
	def calculateEVI(self, NIR, RED, BLUE):
		EVI = 2.5 * (NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1)
		if EVI > 1:
			EVI = 1
		elif EVI < -1:
			EVI = -1
		return EVI
		
	# NDVI calculator from image
	def NDVIcalculator(self, imageName, point):
		NDVI = None
		# band set
		if cfg.bndSetPresent == "Yes" and imageName == cfg.bndSetNm:
			if cfg.NIRBand is None or cfg.REDBand is None:
				return "No"
			else:
				NIRRaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.NIRBand) - 1], "Yes")	
				REDRaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.REDBand) - 1], "Yes")
				# open input with GDAL
				try:
					NIRr = cfg.gdalSCP.Open(NIRRaster.source(), cfg.gdalSCP.GA_ReadOnly)
					REDr = cfg.gdalSCP.Open(REDRaster.source(), cfg.gdalSCP.GA_ReadOnly)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				NIRB = NIRr.GetRasterBand(1)
				REDB = REDr.GetRasterBand(1)
				geoT = NIRr.GetGeoTransform()
		else:
			inputRaster = cfg.utls.selectLayerbyName(imageName, "Yes")	
			# open input with GDAL
			try:
				rD = cfg.gdalSCP.Open(inputRaster.source(), cfg.gdalSCP.GA_ReadOnly)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			if rD is None or cfg.NIRBand is None or cfg.REDBand is None:
				return "No"
			else:
				NIRB = rD.GetRasterBand(int(cfg.NIRBand))
				REDB = rD.GetRasterBand(int(cfg.REDBand))
			geoT = rD.GetGeoTransform()
		tLX = geoT[0]
		tLY = geoT[3]
		pSX = geoT[1]
		pSY = geoT[5]
		# start and end pixels
		pixelStartColumn = (int((point.x() - tLX) / pSX))
		pixelStartRow = -(int((tLY - point.y()) / pSY))
		try:
			NIR = self.readArrayBlock(NIRB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.NIRBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.NIRBand) - 1]
			RED = self.readArrayBlock(REDB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.REDBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.REDBand) - 1]
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			# close bands
			NIRB = None
			REDB = None
			# close raster
			rD = None
			return "No"
		if NIR is not None and RED is not None:
			try:
				NDVI = self.calculateNDVI(float(NIR), float(RED))
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# close bands
				NIRB = None
				REDB = None
				# close raster
				rD = None
				return "No"
		# close bands
		NIRB = None
		REDB = None
		# close raster
		rD = None
		NIRr = None
		REDr = None
		try:
			return round(NDVI, 3)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No" 
		
	# EVI calculator from image
	def EVIcalculator(self, imageName, point):
		EVI = None
		# band set
		if cfg.bndSetPresent == "Yes" and imageName == cfg.bndSetNm:
			if cfg.NIRBand is None or cfg.REDBand is None or cfg.BLUEBand is None:
				return "No"
			else:
				NIRRaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.NIRBand) - 1], "Yes")	
				REDRaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.REDBand) - 1], "Yes")
				BLUERaster = cfg.utls.selectLayerbyName(cfg.bndSet[int(cfg.BLUEBand) - 1], "Yes")
				# open input with GDAL
				try:
					NIRr = cfg.gdalSCP.Open(NIRRaster.source(), cfg.gdalSCP.GA_ReadOnly)
					REDr = cfg.gdalSCP.Open(REDRaster.source(), cfg.gdalSCP.GA_ReadOnly)
					BLUEr = cfg.gdalSCP.Open(BLUERaster.source(), cfg.gdalSCP.GA_ReadOnly)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				NIRB = NIRr.GetRasterBand(1)
				REDB = REDr.GetRasterBand(1)
				BLUEB = REDr.GetRasterBand(1)
				geoT = NIRr.GetGeoTransform()
		else:
			inputRaster = cfg.utls.selectLayerbyName(imageName, "Yes")	
			# open input with GDAL
			try:
				rD = cfg.gdalSCP.Open(inputRaster.source(), cfg.gdalSCP.GA_ReadOnly)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			if rD is None or cfg.NIRBand is None or cfg.REDBand is None or cfg.BLUEBand is None:
				return "No"
			else:
				NIRB = rD.GetRasterBand(int(cfg.NIRBand))
				REDB = rD.GetRasterBand(int(cfg.REDBand))
				BLUEB = rD.GetRasterBand(int(cfg.BLUEBand))
			geoT = rD.GetGeoTransform()
		tLX = geoT[0]
		tLY = geoT[3]
		pSX = geoT[1]
		pSY = geoT[5]
		# start and end pixels
		pixelStartColumn = (int((point.x() - tLX) / pSX))
		pixelStartRow = -(int((tLY - point.y()) / pSY))
		NIR = self.readArrayBlock(NIRB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.NIRBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.NIRBand) - 1]
		RED = self.readArrayBlock(REDB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.REDBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.REDBand) - 1]
		BLUE = self.readArrayBlock(BLUEB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(cfg.BLUEBand) - 1] + cfg.bndSetAddFactorsList[int(cfg.BLUEBand) - 1]
		if NIR is not None and RED is not None and BLUE is not None:
			if NIR <= 1 and RED <= 1 and BLUE <= 1:
				try:
					EVI = self.calculateEVI(float(NIR), float(RED), float(BLUE))
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					# close bands
					NIRB = None
					REDB = None
					BLUEB = None
					# close raster
					rD = None
					return "No"
		# close bands
		NIRB = None
		REDB = None
		BLUEB = None
		# close raster
		rD = None
		NIRr = None
		REDr = None
		BLUEr = None
		try:
			return round(EVI, 3)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No" 
			
	# custom index calculator from image
	def customIndexCalculator(self, imageName, point):
		customIndex = None
		geoT = None
		e = " " + cfg.uidc.custom_index_lineEdit.text() + " "
		dExpr = e
		for b in range(1, len(cfg.bndSet)+1):
			if "bandset#b" + str(b) in e:
				# band set
				if cfg.bndSetPresent == "Yes" and imageName == cfg.bndSetNm:
					raster = cfg.utls.selectLayerbyName(cfg.bndSet[int(b) - 1], "Yes")
					rRaster = cfg.gdalSCP.Open(raster.source(), cfg.gdalSCP.GA_ReadOnly)
					rasterB = rRaster.GetRasterBand(1)
					if geoT is None:
						geoT = rRaster.GetGeoTransform()
					tLX = geoT[0]
					tLY = geoT[3]
					pSX = geoT[1]
					pSY = geoT[5]
					# start and end pixels
					pixelStartColumn = (int((point.x() - tLX) / pSX))
					pixelStartRow = -(int((tLY - point.y()) / pSY))
					val = self.readArrayBlock(rasterB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(b) - 1] + cfg.bndSetAddFactorsList[int(b) - 1]
					dExpr = dExpr.replace("bandset#b" + str(b), str(val[0,0]))
					# close bands
					rasterB = None
					# close raster
					rD = None
				else:
					inputRaster = cfg.utls.selectLayerbyName(imageName, "Yes")	
					# open input with GDAL
					try:
						rD = cfg.gdalSCP.Open(inputRaster.source(), cfg.gdalSCP.GA_ReadOnly)
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						return "No"
					if rD is None or cfg.NIRBand is None or cfg.REDBand is None or cfg.BLUEBand is None:
						return "No"
					else:
						rasterB = rD.GetRasterBand(int(b))
					if geoT is None:
						geoT = rD.GetGeoTransform()
					tLX = geoT[0]
					tLY = geoT[3]
					pSX = geoT[1]
					pSY = geoT[5]
					# start and end pixels
					pixelStartColumn = (int((point.x() - tLX) / pSX))
					pixelStartRow = -(int((tLY - point.y()) / pSY))
					val = self.readArrayBlock(rasterB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bndSetMultiFactorsList[int(b) - 1] + cfg.bndSetAddFactorsList[int(b) - 1]
					dExpr = dExpr.replace("bandset#b" + str(b), str(val[0,0]))
					# close bands
					rasterB = None
					# close raster
					rD = None
		try:
			f = cfg.utls.replaceNumpyOperators(dExpr)
			customIndex = eval(f)
			return round(customIndex, 3)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No" 
		
	# copy a raster band from a multi band raster
	def getRasterBandByBandNumber(self, inputRaster, band, outputRaster, virtualRaster = "No", GDALFormat = None, multiAddList = None):
		if virtualRaster == "No":
			# open input with GDAL
			rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
			# number of x pixels
			rC = rD.RasterXSize
			# number of y pixels
			rR = rD.RasterYSize
			# check projections
			rP = rD.GetProjection()
			# pixel size and origin
			rGT = rD.GetGeoTransform()
			tD = cfg.gdalSCP.GetDriverByName( "GTiff" )
			iRB = rD.GetRasterBand(int(band))
			if GDALFormat is None:
				bDT = iRB.DataType
			else:
				if GDALFormat == "Float64":
					bDT = cfg.gdalSCP.GDT_Float64
				elif GDALFormat == "Float32":
					bDT = cfg.gdalSCP.GDT_Float32
			a =  iRB.ReadAsArray()
			if multiAddList is not None:
				a = cfg.utls.arrayMultiplicativeAdditiveFactors(a, multiAddList[0], multiAddList[1])
			oR = tD.Create(outputRaster, rC, rR, 1, bDT)
			oR.SetGeoTransform( [ rGT[0] , rGT[1] , 0 , rGT[3] , 0 , rGT[5] ] )
			oR.SetProjection(rP)
			oRB = oR.GetRasterBand(1)
			oRB.WriteArray(a)
			# close bands
			oRB = None
			iRB = None
			# close rasters
			oR = None
			rD = None
		else:
			vrtCheck = cfg.utls.createVirtualRaster([inputRaster], outputRaster, band)
			cfg.timeSCP.sleep(1)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "get band: " + unicode(band))
		
	# Split raster into single bands, and return a list of images
	def rasterToBands(self, rasterPath, outputFolder, outputName = None, progressBar = "No", multiAddList = None):
		dT = self.getTime()
		iBC = cfg.utls.getNumberBandRaster(rasterPath)
		iL = []
		if outputName is None:
			name = cfg.splitBndNm + dT
		else:
			name = outputName
		progresStep = int(100 / iBC)
		i = 1
		for x in range(1, iBC+1):
			if cfg.actionCheck == "Yes":
				xB = outputFolder + "/" + name + "_B" + str(x) + ".tif"
				if multiAddList is not None:
					self.getRasterBandByBandNumber(rasterPath, x, xB, "No", None, multiAddList[x - 1])
				else:
					self.getRasterBandByBandNumber(rasterPath, x, xB, "No", None)
				iL.append(xB)
				if progressBar == "Yes":
					cfg.uiUtls.updateBar(progresStep * i)
					i = i + 1
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "raster: " + unicode(rasterPath) + " split to bands")
		return iL
		
	# band calculation
	def bandCalculation(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):
		if cfg.actionCheck == "Yes":
			f = functionBandArgument
			# create function
			b = 0
			for i in functionVariableList:
				f = f.replace(i[0], " rasterSCPArrayfunctionBand[::, ::," + str(b) + "] ")
				f = f.replace(i[1], " rasterSCPArrayfunctionBand[::, ::," + str(b) + "] ")
				b = b + 1
			# replace numpy operators
			f = cfg.utls.replaceNumpyOperators(f)
			# perform operation
			try:
				o = eval(f)
			except Exception, err:
				cfg.mx.msgErr36()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			# create array if not
			if not isinstance(o, cfg.np.ndarray):
				a = cfg.np.zeros((rasterSCPArrayfunctionBand.shape[0], rasterSCPArrayfunctionBand.shape[1]), dtype=cfg.np.float64)
				try:
					a.fill(o)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				o = a
			oR = outputGdalRasterList[0]
			# output raster
			band = gdalBandList[0].GetBand()
			try:
				self.writeArrayBlock(oR, band, o, pixelStartColumn, pixelStartRow)
			except Exception, err:
				cfg.mx.msgErr36()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			
	# multiple where band calculation 
	def bandCalculationMultipleWhere(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):
		if cfg.actionCheck == "Yes":
			for f in functionBandArgument:
				# create function
				b = 0
				for i in functionVariableList:
					f = f.replace(i[0], " rasterSCPArrayfunctionBand[::, ::," + str(b) + "] ")
					f = f.replace(i[1], " rasterSCPArrayfunctionBand[::, ::," + str(b) + "] ")
					b = b + 1
				# replace numpy operators
				f = cfg.utls.replaceNumpyOperators(f)
				# perform operation
				try:
					o = o + eval(f)
				# first iteration
				except:
					try:
						o = eval(f)
					except Exception, err:
						cfg.mx.msgErr36()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						return "No"
			# create array if not
			try:
				if not isinstance(o, cfg.np.ndarray):
					o = cfg.np.where(o == 0, cfg.NoDataVal, o)
					a = cfg.np.zeros((rasterSCPArrayfunctionBand.shape[0], rasterSCPArrayfunctionBand.shape[1]), dtype=cfg.np.float64)
					a.fill(o)
					o = a
			except Exception, err:
				cfg.mx.msgErr36()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			oR = outputGdalRasterList[0]
			# output raster
			band = gdalBandList[0].GetBand()
			try:
				self.writeArrayBlock(oR, band, o, pixelStartColumn, pixelStartRow)
			except Exception, err:
				cfg.mx.msgErr36()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
								
	# multiple where scatter raster calculation 
	def scatterRasterMultipleWhere(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):
		if cfg.actionCheck == "Yes":
			for f in functionBandArgument:
				# create function
				f = f.replace("bandX", " rasterSCPArrayfunctionBand[::, ::, 0] ")
				f = f.replace("bandY", " rasterSCPArrayfunctionBand[::, ::, 1] ")
				# perform operation
				try:
					u = eval(f)
					o = cfg.np.where(u == cfg.NoDataVal, o, u)
				# first iteration
				except:
					try:
						o = eval(f)
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
						return "No"
			oR = outputGdalRasterList[0]
			# output raster
			try:
				self.writeArrayBlock(oR, 1, o, pixelStartColumn, pixelStartRow)
				oR = None
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
										
	#  band calculation scatter raster
	def scatterRasterBandCalculation(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):
		if cfg.actionCheck == "Yes":
			f = functionBandArgument
			# create function
			f = f.replace("bandX", " rasterSCPArrayfunctionBand[::, ::, 0] ")
			f = f.replace("bandY", " rasterSCPArrayfunctionBand[::, ::, 1] ")
			# perform operation
			out = eval(f)
			oR = outputGdalRasterList[0]
			# output raster
			try:
				self.writeArrayBlock(oR, 1, out, pixelStartColumn, pixelStartRow)
				oR = None
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
				
	# raster erosion boundaries
	def rasterErosionBoundaries(self, gdalBandList, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):	
		cfg.utls.rasterErosion(gdalBandList, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList, "Yes")
		
	# raster erosion
	def rasterErosion(self, gdalBandList, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList, boundaries = None):		
		A = rasterArray[::, ::, 0]
		B = functionBandArgument
		# value sum dictionary
		C={}
		# unique value list
		uniqueVal = cfg.np.unique(A)
		aUniqueVal = list(uniqueVal.astype(int))
		# calculate sum
		for i in aUniqueVal:
			C['arr_'+ str(i)] = cfg.signalSCP.convolve2d(cfg.np.where(A==i, 1,0), B, 'same')
		# erosion
		D = cfg.np.ones(A.shape)
		R = cfg.np.zeros(A.shape)
		for v in functionVariableList:
			if v in aUniqueVal:
				# core
				D[C['arr_'+ str(v)] == B.sum()] = 0
				# erosion values
				R[A == v] = 1
				aUniqueVal.remove(v)
		# empty array
		Z = cfg.np.zeros((C['arr_'+ str(i)].shape[0], C['arr_'+ str(i)].shape[1], len(aUniqueVal)))
		# copy sum
		for s in range(0, (len(aUniqueVal))):
			Z[::,::,s] = C['arr_'+ str(aUniqueVal[s])]
		try:
			# maximum sum
			maxA = cfg.np.argmax(Z, axis = 2)
			maxACopy = cfg.np.copy(maxA)
			# replace maximum with class value
			for s in range(0, (len(aUniqueVal))):
				maxA[maxACopy == s] = aUniqueVal[s]
			# output erosion
			out = cfg.np.where((R * D * cfg.np.where(cfg.np.max(Z, axis = 2) > 0, 1, 0) == 1), maxA, A)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			out = A
		oR = outputGdalRasterList[0]
		if boundaries is None:
			# output raster
			try:
				self.writeArrayBlock(oR, 1, out, pixelStartColumn, pixelStartRow)
				oR = None
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		else:
			# output raster
			try:
				self.writeArrayBlock(oR, 1, out[1:-1,1:-1], pixelStartColumn+1, pixelStartRow+1)
				oR = None
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			
	# raster dilation boundaries
	def rasterDilationBoundaries(self, gdalBandList, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):	
		cfg.utls.rasterDilation(gdalBandList, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList, "Yes")
			
	# raster dilation
	def rasterDilation(self, gdalBandList, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList, boundaries = None):		
		A = rasterArray[::, ::, 0]
		B = functionBandArgument
		# value sum dictionary
		C={}
		# unique value list
		uniqueVal = cfg.np.unique(A)
		aUniqueVal = list(uniqueVal.astype(int))
		# calculate sum
		for i in aUniqueVal:
			C['arr_'+ str(i)] = cfg.signalSCP.convolve2d(cfg.np.where(A==i, 1,0), B, 'same')
		# core
		D = cfg.np.ones(A.shape)
		for v in functionVariableList:
			D[cfg.np.where(A == v)] = 0

		# dilation
		out = cfg.np.copy(A)
		try:
			for v in functionVariableList:
				out[(D * C['arr_'+ str(v)]) > 0] = v
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		oR = outputGdalRasterList[0]
		if boundaries is None:
			# output raster
			try:
				self.writeArrayBlock(oR, 1, out, pixelStartColumn, pixelStartRow)
				oR = None
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		else:
			# output raster
			try:
				self.writeArrayBlock(oR, 1, out[1:-1,1:-1], pixelStartColumn+1, pixelStartRow+1)
				oR = None
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				return "No"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			
	# replace numpy operators for expressions in Band calc
	def replaceNoDataValues(self, expression, nameList):
		if "nodata" in expression:
			# find all non-greedy expression
			g = cfg.reSCP.findall('nodata\(\"#?(.*?)#?\"\)',expression)
		else:
			return expression
		for l in g:
			name = l
			for i in nameList:
				if l == i[0].replace('"', ''):
					l = i[1].replace('"', '')
			if l in cfg.variableBlueName or l in cfg.variableRedName or l in cfg.variableNIRName :
				if cfg.bndSetPresent == "Yes" and cfg.imgNm == cfg.bndSetNm:
					name = "#" + name
					if "#" + l == cfg.variableRedName :
						bandNumber = ["", cfg.REDBand]
					elif "#" + l == cfg.variableNIRName :
						bandNumber = ["", cfg.NIRBand]
					elif "#" + l == cfg.variableBlueName :
						bandNumber = ["", cfg.BLUEBand]
					l = cfg.bndSet[int(bandNumber[1]) - 1]
				elif cfg.imgNm is not None:
					l = cfg.imgNm
			name = '"' + name + '"'
			r = cfg.utls.selectLayerbyName(l, "Yes")
			if r is not None:
				nd = cfg.utls.imageNoDataValue(r.source())
				expression = expression.replace('nodata(' + name + ')', str(nd))
		# find Nodata values
		return expression
		
	# replace numpy operators for expressions in Band calc
	def replaceNumpyOperators(self, expression):
		f = expression
		f = f.replace(" ln(", " " + cfg.logn + "(")
		f = f.replace(" ln (", " " + cfg.logn + "(")
		f = f.replace(" sqrt(", " " + cfg.numpySqrt + "(")
		f = f.replace(" sqrt (", " " + cfg.numpySqrt + "(")
		f = f.replace(" cos(", " " + cfg.numpyCos+ "(")
		f = f.replace(" cos (", " " + cfg.numpyCos + "(")
		f = f.replace(" acos(", " " + cfg.numpyArcCos + "(")
		f = f.replace(" acos (", " " + cfg.numpyArcCos + "(")
		f = f.replace(" sin(", " " + cfg.numpySin + "(")
		f = f.replace(" sin (", " " + cfg.numpySin + "(")
		f = f.replace(" asin(", " " + cfg.numpyArcSin + "(")
		f = f.replace(" asin (", " " + cfg.numpyArcSin + "(")
		f = f.replace(" tan(", " " + cfg.numpyTan + "(")
		f = f.replace(" tan (", " " + cfg.numpyTan + "(")
		f = f.replace(" atan(", " " + cfg.numpyArcTan + "(")
		f = f.replace(" atan (", " " + cfg.numpyArcTan + "(")
		f = f.replace(" exp(", " " + cfg.numpyExp + "(")
		f = f.replace(" exp (", " " + cfg.numpyExp + "(")
		f = f.replace("^", "**")
		f = f.replace(" pi ", " " + cfg.numpyPi + " ")
		f = f.replace(" where(", " " + cfg.numpyWhere + "(")
		f = f.replace(" where (", " " + cfg.numpyWhere + "(")
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return f
			
	# process a raster with block size
	def processRasterBoundaries(self, gdalRaster, gdalBandList, signatureList = None, functionBand = None, functionRaster = None, algorithmName = None, outputRasterList = None, outputAlgorithmRaster = None, outputClassificationRaster = None, previewSize = 0, previewPoint = None, nodataValue = None, macroclassCheck = "No", functionBandArgument = None, functionVariable = None, progressMessage = "", boundarySize = None):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "start processRaster boundaries")
		blockSizeX = self.calculateBlockSize(len(gdalBandList))
		blockSizeY = blockSizeX
		# raster blocks
		rX, rY, lX, lY, pX, pY  = self.rasterBlocks(gdalRaster, blockSizeX, blockSizeY, previewSize, previewPoint)
		# set initial value for progress bar
		progresStep = 60 / (len(lX) + len(lY))
		progressStart = 20 - progresStep
		if blockSizeX > rX:
			blockSizeX = rX
		if blockSizeY > rY:
			blockSizeY = rY
		cfg.remainingTime = 0
		remainingBlocks = (len(lX) + len(lY) - 2)
		totBlocks = remainingBlocks
		if len(lX) > 1 or len(lY) > 1:
			for y in lY:
				if y != 0 and (y - boundarySize) <= rY:
					if cfg.actionCheck == "Yes":
						# set initial value for progress bar
						progressStart = progressStart + progresStep
						bSX = rX
						bSY = boundarySize * 2  
						array = cfg.np.zeros((bSX, bSY, len(gdalBandList)), dtype=cfg.np.float64)
						for b in range(0, len(gdalBandList)):
							ndv = cfg.NoDataVal
							a = self.readArrayBlock(gdalBandList[b], 0, y - boundarySize, bSX, bSY)
							try:
								b0 = gdalBandList[b].GetRasterBand(1)
								ndv2 = b0.GetNoDataValue()
							except:
								try:
									ndv2 = gdalBandList[b].GetNoDataValue()
								except:
									ndv2 = None				
							if a is not None:
								array[::, ::, b] = a.reshape(bSX, bSY)
							else:
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "error reading array")
								cfg.mx.msgErr46()
								return "No"
							a = None
							array[::, ::, b][array[::, ::, b] == ndv] = cfg.np.nan
							if ndv2 is not None:
								array[::, ::, b][array[::, ::, b] == ndv2] = cfg.np.nan
						c = array.reshape(bSY, bSX, len(gdalBandList))
						array = None
						if functionRaster is not None:
							if functionBand == "No":
								cfg.QtGuiSCP.qApp.processEvents()
								o = functionRaster(gdalBandList, c, bSX, bSY, 0, y - boundarySize, outputRasterList, functionBandArgument, functionVariable)
								if progressMessage != "No":
									cfg.uiUtls.updateBar(progressStart, " (" + str(totBlocks - remainingBlocks) + "/" + str(totBlocks) + ") " + progressMessage)
									remainingBlocks = (remainingBlocks - 1)
								if o == "No":
									return "No"	
					else:
						return "No"
			for x in lX:
				if x != 0 and (x - boundarySize) <= rX:
					if cfg.actionCheck == "Yes":
						# set initial value for progress bar
						progressStart = progressStart + progresStep
						bSX = boundarySize * 2 
						bSY = rY 
						array = cfg.np.zeros((bSX, bSY, len(gdalBandList)), dtype=cfg.np.float64)
						for b in range(0, len(gdalBandList)):
							ndv = cfg.NoDataVal
							a = self.readArrayBlock(gdalBandList[b], x - boundarySize, 0, bSX, bSY)
							try:
								b0 = gdalBandList[b].GetRasterBand(1)
								ndv2 = b0.GetNoDataValue()
							except:
								try:
									ndv2 = gdalBandList[b].GetNoDataValue()
								except:
									ndv2 = None				
							if a is not None:
								array[::, ::, b] = a.reshape(bSX, bSY)
							else:
								# logger
								cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "error reading array")
								cfg.mx.msgErr46()
								return "No"
							a = None
							array[::, ::, b][array[::, ::, b] == ndv] = cfg.np.nan
							if ndv2 is not None:
								array[::, ::, b][array[::, ::, b] == ndv2] = cfg.np.nan
						c = array.reshape(bSY, bSX, len(gdalBandList))
						array = None
						if functionRaster is not None:
							if functionBand == "No":
								cfg.QtGuiSCP.qApp.processEvents()
								o = functionRaster(gdalBandList, c, bSX, bSY, x - boundarySize, 0, outputRasterList, functionBandArgument, functionVariable)
								if progressMessage != "No":
									cfg.uiUtls.updateBar(progressStart, " (" + str(totBlocks - remainingBlocks) + "/" + str(totBlocks) + ") " + progressMessage)
									remainingBlocks = (remainingBlocks - 1)
								if o == "No":
									return "No"	
					else:
						return "No"
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "end processRaster boundaries")
		return "Yes"
		
	# process a raster with block size
	def processRaster(self, gdalRaster, gdalBandList, signatureList = None, functionBand = None, functionRaster = None, algorithmName = None, outputRasterList = None, outputAlgorithmRaster = None, outputClassificationRaster = None, previewSize = 0, previewPoint = None, nodataValue = None, macroclassCheck = "No", functionBandArgument = None, functionVariable = None, progressMessage = "", skipReplaceNoData = None):
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "start processRaster")
		blockSizeX = self.calculateBlockSize(len(gdalBandList))
		blockSizeY = blockSizeX
		# raster blocks
		rX, rY, lX, lY, pX, pY  = self.rasterBlocks(gdalRaster, blockSizeX, blockSizeY, previewSize, previewPoint)
		# set initial value for progress bar
		try:
			progresStep = 60 / (len(lX) * len(lY))
		except:
			progresStep = 60 
		progressStart = 20 - progresStep
		if blockSizeX > rX:
			blockSizeX = rX
		if blockSizeY > rY:
			blockSizeY = rY
		cfg.remainingTime = 0
		remainingBlocks = len(lX) * len(lY)
		totBlocks = remainingBlocks
		for y in lY:
			bSY = blockSizeY
			if previewSize > 0 and bSY > previewSize:
				bSY = previewSize
			if y + bSY > rY:
				bSY = rY - y
			for x in lX:
				if cfg.actionCheck == "Yes":
					# set initial value for progress bar
					progressStart = progressStart + progresStep
					bSX = blockSizeX 
					if previewSize > 0 and bSX > previewSize:
						bSX = previewSize
					if x + bSX > rX:
						bSX = rX - x
					array = cfg.np.zeros((bSX, bSY, len(gdalBandList)), dtype=cfg.np.float64)
					for b in range(0, len(gdalBandList)):
						ndv = cfg.NoDataVal
						a = self.readArrayBlock(gdalBandList[b], x, y, bSX, bSY)
						try:
							b0 = gdalBandList[b].GetRasterBand(1)
							ndv2 = b0.GetNoDataValue()
						except:
							try:
								ndv2 = gdalBandList[b].GetNoDataValue()
							except:
								ndv2 = None
						if a is not None:
							if functionBandArgument == cfg.multiAddFactorsVar:
								multiAdd = functionVariable[b]
								a = cfg.utls.arrayMultiplicativeAdditiveFactors(a, multiAdd[0], multiAdd[1])
							array[::, ::, b] = a.reshape(bSX, bSY)
						else:
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "error reading array")
							cfg.mx.msgErr46()
							return "No"
						a = None
						# set nodata value
						#noData = gBand2.GetNoDataValue()
						if skipReplaceNoData is None:
							array[::, ::, b][array[::, ::, b] == ndv] = cfg.np.nan
							if ndv2 is not None:
								array[::, ::, b][array[::, ::, b] == ndv2] = cfg.np.nan
						if functionBand is not None and functionBand != "No":
							cfg.QtGuiSCP.qApp.processEvents()
							functionBand(b+1, array[::, ::, b].reshape(bSY, bSX), bSX, bSY, x, y, outputRasterList, functionBandArgument, functionVariable)
							if progressMessage != "No":
								cfg.uiUtls.updateBar(progressStart, " (" + str(totBlocks - remainingBlocks) + "/" + str(totBlocks) + ") " + progressMessage)
					c = array.reshape(bSY, bSX, len(gdalBandList))
					array = None
					if functionRaster is not None:
						if functionBand == "No":
							cfg.QtGuiSCP.qApp.processEvents()
							o = functionRaster(gdalBandList, c, bSX, bSY, x, y, outputRasterList, functionBandArgument, functionVariable)
							if progressMessage != "No":
								cfg.uiUtls.updateBar(progressStart, " (" + str(totBlocks - remainingBlocks) + "/" + str(totBlocks) + ") " + progressMessage)
							if o == "No":
								return "No"
						else:
							cfg.QtGuiSCP.qApp.processEvents()
							progressMessage = " (" + str(totBlocks - remainingBlocks) + "/" + str(totBlocks) + ") "
							o = functionRaster(gdalBandList, signatureList, algorithmName, c, bSX, bSY, x, y, outputRasterList, outputAlgorithmRaster, outputClassificationRaster, nodataValue, macroclassCheck, previewSize, pX[lX.index(x)], pY[lY.index(y)], progressStart, progresStep, remainingBlocks, progressMessage)
							if o == "No":
								return "No"
					remainingBlocks = (remainingBlocks - 1)
				else:
					return "No"
		outputClassificationRaster = None
		c = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "end processRaster")
		return "Yes"

	# calculate raster
	def calculateRaster(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariable):
		if cfg.actionCheck == "Yes":
			# create function
			f = functionBandArgument.replace(functionVariable, "rasterArray")
			f = f.replace("ln", cfg.logn)
			# perform operation
			o = eval(f)
			oR = outputGdalRasterList[0]
			# output raster
			self.writeArrayBlock(oR, 1, o, pixelStartColumn, pixelStartRow)
			o = None
			oR = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
					
	# reclassify raster
	def reclassifyRaster(self, gdalBand, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariable):
		if cfg.actionCheck == "Yes":
			# raster array
			o = rasterSCPArrayfunctionBand
			for i in functionBandArgument:
				# create condition
				c = i[0].replace(functionVariable, "rasterSCPArrayfunctionBand")
				f = "cfg.np.where(" + c + ", " + str(i[1]) + ", o)"
				# perform operation
				try:
					o = eval(f)
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			oR = outputGdalRasterList[0]
			# output raster
			self.writeArrayBlock(oR, 1, o, pixelStartColumn, pixelStartRow)
			o = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())

	# pan-sharpening
	def pansharpening(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):
		if cfg.actionCheck == "Yes":
			# functionBandArgument = [satellite, panType]
			if functionBandArgument[0] in ['landsat8', 'landsat_8']:
				try:
					# functionVariableList = [bandNumber]
					B = functionVariableList.index(2)
					G = functionVariableList.index(3)
					R = functionVariableList.index(4)
				except Exception, err:
					cfg.mx.msgErr44()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				# Intensity (SCP weights)
				I = (0.42* rasterSCPArrayfunctionBand[:,:,B] + 0.98 * rasterSCPArrayfunctionBand[:,:,G] + 0.6 * rasterSCPArrayfunctionBand[:,:,R] ) / 2
			elif functionBandArgument[0] in ['landsat7', 'landsat_7']:
				try:
					# functionVariableList = [bandNumber]
					B = functionVariableList.index(1)
					G = functionVariableList.index(2)
					R = functionVariableList.index(3)
					NIR = functionVariableList.index(4)
				except Exception, err:
					cfg.mx.msgErr44()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				# Intensity (SCP weights)
				I = (0.42* rasterSCPArrayfunctionBand[:,:,B] + 0.98 * rasterSCPArrayfunctionBand[:,:,G] + 0.6* rasterSCPArrayfunctionBand[:,:,R] + 1* rasterSCPArrayfunctionBand[:,:,NIR]  ) / 3
			if functionBandArgument[1] == cfg.IHS_panType:
				# delta
				d = rasterSCPArrayfunctionBand[:,:,0] - I
			i = 0
			for oR in outputGdalRasterList:
				# process multiband rasters
				i = i + 1
				if functionBandArgument[1] == cfg.IHS_panType:
					o = rasterSCPArrayfunctionBand[:,:,i] + d
				elif functionBandArgument[1] == cfg.BT_panType:
					o = rasterSCPArrayfunctionBand[:,:,i] * rasterSCPArrayfunctionBand[:,:,0] / I	
				# output raster
				try:
					self.writeArrayBlock(oR, 1, o, pixelStartColumn, pixelStartRow)
				except Exception, err:
					cfg.mx.msgErr45()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			I = None
			o = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Pansharpening")
			
	# calculate random points
	def randomPoints(self, pointNumber, Xmin, Xmax, Ymin, Ymax, minDistance = None):
		XCoords = cfg.np.random.uniform(Xmin,Xmax,pointNumber).reshape(pointNumber, 1)
		YCoords = cfg.np.random.uniform(Ymin,Ymax,pointNumber).reshape(pointNumber, 1)
		points = cfg.np.hstack((XCoords,YCoords))
		if minDistance is not None:
			for i in range(0, pointNumber):
				distance = cfg.cdistSCP(points, points)
				if i < distance.shape[0]:
					index = cfg.np.where((distance[i,:] <= minDistance)  & (distance[i,:] > 0))
					points = cfg.np.delete(points, index, 0)
		return points
			
	# calculate raster unique values
	def rasterUniqueValues(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			val = cfg.np.unique(rasterArray)
			# remove multiple nan
			val = cfg.np.unique(val[~cfg.np.isnan(val)])
			cfg.rasterBandUniqueVal = cfg.np.append(cfg.rasterBandUniqueVal, [val], axis =1)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.rasterBandUniqueVal
			
	# count pixels in a raster lower than value
	def rasterValueCount(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			sum = ((rasterArray <= functionVariable) & (rasterArray != functionBandArgumentNoData)).sum()
			cfg.rasterBandPixelCount = cfg.rasterBandPixelCount + sum
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.rasterBandPixelCount
						
	# count pixels in a raster equal to value
	def rasterEqualValueCount(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			sum = (rasterArray == functionVariable).sum()
			cfg.rasterBandPixelCount = cfg.rasterBandPixelCount + sum
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.rasterBandPixelCount
			
	# calculate raster unique values (slow)
	def rasterUniqueValuesWithSum(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			val = cfg.np.unique(rasterArray).tolist()
			for i in val:
				if i != functionBandArgumentNoData:
					sum = (rasterArray == i).sum()
					index = cfg.np.where(cfg.rasterBandUniqueVal[1,:] == i)
					if index[0].size > 0:
						oldVal = cfg.rasterBandUniqueVal[0,index[0]]
						newValue = oldVal + sum
						cfg.rasterBandUniqueVal[0, index[0]] = newValue
					else:
						cfg.rasterBandUniqueVal = cfg.np.append(cfg.rasterBandUniqueVal, [[sum], [ i]], axis =1)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.rasterBandUniqueVal
						
	# calculate sum raster unique values
	def rasterSumUniqueValues(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			val = cfg.np.unique(rasterArray).tolist()
			for i in val:
				try:
					oldV = cfg.uVal[str(i)]
				except:
					oldV = 0
				sum = oldV  + (rasterArray == i).sum()
				cfg.uVal[str(i)] = sum
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.uVal			
		
	# count pixels in a raster
	def rasterPixelCount(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			for i in range(0, rasterArray.shape[2]):
				a = rasterArray[::, ::, i].flatten() * cfg.bndSetMultiFactorsList[i] + cfg.bndSetAddFactorsList[i]
				if functionBandArgumentNoData is not None:
					a = a[a != functionBandArgumentNoData]
				count = a.shape[0]
				try:
					cfg.rasterPixelCountPCA["COUNT_BAND_" + str(i)] = cfg.rasterPixelCountPCA["COUNT_BAND_" + str(i)] + count
				except:
					cfg.rasterPixelCountPCA["COUNT_BAND_" + str(i)] = count
				sum = a.sum()
				try:
					cfg.rasterPixelCountPCA["SUM_BAND_" + str(i)] = cfg.rasterPixelCountPCA["SUM_BAND_" + str(i)] + sum
				except:
					cfg.rasterPixelCountPCA["SUM_BAND_" + str(i)] = sum
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.rasterPixelCountPCA
					
	# covariance in a raster
	def rasterCovariance(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			comb = cfg.itertoolsSCP.combinations(range(0, rasterArray.shape[2]), 2)
			# covariance
			for i in comb:
				x = rasterArray[::, ::, int(i[0])] * cfg.bndSetMultiFactorsList[i[0]] + cfg.bndSetAddFactorsList[i[0]]
				y = rasterArray[::, ::, int(i[1])] * cfg.bndSetMultiFactorsList[i[1]] + cfg.bndSetAddFactorsList[i[1]]
				a = x - cfg.rasterPixelCountPCA["MEAN_BAND_" + str(i[0])]
				b = y - cfg.rasterPixelCountPCA["MEAN_BAND_" + str(i[1])]
				c = a * b
				cov = c.sum() / (cfg.rasterPixelCountPCA["COUNT_BAND_" + str(i[0])] - 1)
				try:
					cfg.rasterPixelCountPCA["COV_BAND_" + str(i[0]) + "-" + str(i[1])] = cfg.rasterPixelCountPCA["COV_BAND_" + str(i[0]) + "-" + str(i[1])] + cov
				except:
					cfg.rasterPixelCountPCA["COV_BAND_" + str(i[0]) + "-" + str(i[1])] = cov	
			# variance
			for i in range(0, rasterArray.shape[2]):
				x = rasterArray[::, ::, int(i)] * cfg.bndSetMultiFactorsList[i] + cfg.bndSetAddFactorsList[i]
				a = x - cfg.rasterPixelCountPCA["MEAN_BAND_" + str(i)]
				c = a * a
				cov = c.sum() / (cfg.rasterPixelCountPCA["COUNT_BAND_" + str(i)] - 1)
				try:
					cfg.rasterPixelCountPCA["COV_BAND_" + str(i) + "-" + str(i)] = cfg.rasterPixelCountPCA["COV_BAND_" + str(i) + "-" + str(i)] + cov
				except:
					cfg.rasterPixelCountPCA["COV_BAND_" + str(i) + "-" + str(i)] = cov
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.rasterPixelCountPCA
			
	# calculate PCA bands
	def calculatePCABands(self, gdalBandList, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList):
		n = 0
		for b in range(0, rasterArray.shape[2]):
			rArray = rasterArray * cfg.bndSetMultiFactorsList[b] + cfg.bndSetAddFactorsList[b] - cfg.rasterPixelCountPCA["MEAN_BAND_" + str(b)]
		for i in functionBandArgument:
			a = cfg.np.array(i) * rArray
			o = a.sum(axis=2)
			# output raster
			try:
				self.writeArrayBlock(outputGdalRasterList[n], 1, o, pixelStartColumn, pixelStartRow)
			except Exception, err:
				cfg.mx.msgErr45()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			n = n + 1
	
	# raster values to list
	def rasterValuesToList(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == "Yes":
			cfg.uVal = cfg.np.append(cfg.uVal, rasterArray)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.uVal
			
	def calculateHistogram2d(self, xVal, yVal, binVal, normedVal = False):
		try:
			h, xE, yE = cfg.np.histogram2d(xVal, yVal, bins=binVal, normed=normedVal)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return [h, xE, yE ]
		except Exception, err:
			cfg.mx.msgErr53()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
			
	# calculate scatter plot
	def calculateScatterPlot(self, vector, field, id, tempROI = "No"):
		# band set
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			# crs of loaded raster
			b = cfg.utls.selectLayerbyName(cfg.bndSet[0], "Yes")
			crs = cfg.utls.getCrs(b)
		else:
			# crs of loaded raster
			crs = cfg.utls.getCrs(cfg.rLay)
		# date time for temp name
		dT = cfg.utls.getTime()
		# temporary layer
		tLN = cfg.subsTmpROI + dT + ".shp"
		tLP = cfg.tmpDir + "/" + dT + tLN
		# create a temp shapefile with a field
		cfg.utls.createEmptyShapefileQGIS(crs, tLP)
		mL = cfg.utls.addVectorLayer(tLP , tLN, "ogr")
		if tempROI == "No":
			rId = cfg.utls.getIDByAttributes(vector, field, str(id))
		else:
			rId = []
			f = QgsFeature()
			for f in vector.getFeatures():
				rId.append(f.id())		
		# copy ROI to temp shapefile
		for pI in rId:
			cfg.utls.copyFeatureToLayer(vector, pI, mL)
		bandList = [cfg.scatterBandX - 1, cfg.scatterBandY - 1]
		# clip by ROI
		bX = cfg.utls.subsetImageByShapefile(mL, cfg.rstrNm, bandList)
		# get raster values
		rDC = cfg.gdalSCP.Open(bX[0], cfg.gdalSCP.GA_ReadOnly)
		bLC = cfg.utls.readAllBandsFromRaster(rDC)
		cfg.uVal = cfg.np.array([])
		o = cfg.utls.processRaster(rDC, bLC, None, "No", cfg.utls.rasterValuesToList, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "value " + str(id))
		xVal = cfg.uVal
		for bR in range(0, len(bLC)):
			bLC[bR] = None
		# close raster
		rDC = None
		rDC = cfg.gdalSCP.Open(bX[1], cfg.gdalSCP.GA_ReadOnly)
		bLC = cfg.utls.readAllBandsFromRaster(rDC)
		cfg.uVal = cfg.np.array([])
		o = cfg.utls.processRaster(rDC, bLC, None, "No", cfg.utls.rasterValuesToList, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "value " + str(id))
		yVal = cfg.uVal
		for bR in range(0, len(bLC)):
			bLC[bR] = None
		# close raster
		rDC = None
		# calculate histogram
		try:
			xVal2 = xVal[~cfg.np.isnan(xVal)]
			yVal2 = yVal[~cfg.np.isnan(xVal)]
			xVal = xVal2[~cfg.np.isnan(yVal2)]
			yVal = yVal2[~cfg.np.isnan(yVal2)]
			xMax = cfg.np.amax(xVal)
			yMax = cfg.np.amax(yVal)
		except Exception, err:
			cfg.mx.msgErr54()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		if cfg.uiscp.precision_checkBox.isChecked():
			rou = int(cfg.uiscp.precision_comboBox.currentText())
			prc = cfg.np.power(10, -float(rou))
			xMin = cfg.np.amin(xVal)
			xMin = cfg.np.around(xMin, rou) - prc
			xMax = cfg.np.around(xMax, rou) + prc
			xSteps = self.calculateSteps(xMin, xMax, prc)
			yMin = cfg.np.amin(yVal)
			yMin = cfg.np.around(yMin, rou) - prc
			yMax = cfg.np.around(yMax, rou) + prc
			ySteps = self.calculateSteps(yMin, yMax, prc)
		elif xMax <= 1.1:
			xMin = cfg.np.amin(xVal)
			xMin = cfg.np.around(xMin, 3) - 0.001
			xMax = cfg.np.around(xMax, 3) + 0.001
			xSteps = self.calculateSteps(xMin, xMax, 0.001)
			yMin = cfg.np.amin(yVal)
			yMin = cfg.np.around(yMin, 3) - 0.001
			yMax = cfg.np.around(yMax, 3) + 0.001
			ySteps = self.calculateSteps(yMin, yMax, 0.001)
		else:
			xMin = cfg.np.amin(xVal)
			xMin = cfg.np.around(xMin, 3) - 10
			xMax = cfg.np.around(xMax, 3) + 10
			xSteps = self.calculateSteps(xMin, xMax, 10)
			yMin = cfg.np.amin(yVal)
			yMin = cfg.np.around(yMin, 3) - 10
			yMax = cfg.np.around(yMax, 3) + 10
			ySteps = self.calculateSteps(yMin, yMax, 10)
		binVal = (xSteps, ySteps)
		h = cfg.utls.calculateHistogram2d(xVal, yVal, binVal)
		return h
	
	# calculate step list
	def calculateSteps(self, minValue, maxValue, step):
		steps = []
		val = minValue
		steps.append(val)
		while val < maxValue:
			val = val + step
			steps.append(val)
		return steps
		
	# subset image by vector
	def subsetImageByShapefile(self, vector, rasterName, bandList):
		tLP = vector.source()
		# date time for temp name
		dT = cfg.utls.getTime()
		# calculate ROI center, height and width
		rCX, rCY, rW, rH = cfg.utls.getShapefileRectangleBox(vector)
		bands = []
		# band set
		if cfg.bndSetPresent == "Yes" and rasterName == cfg.bndSetNm:
			tLX, tLY, pS = cfg.utls.imageInformation(cfg.bndSet[0])
			# subset 
			for b in bandList:
				tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + str(b) + "_" + dT + ".tif")
				pr = cfg.utls.subsetImage(cfg.bndSet[b], rCX, rCY, int(round(rW/pS + 3)),  int(round(rH/pS + 3)), tS)
				if pr == "Yes":
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error edge")
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					return pr
				bX = cfg.utls.clipRasterByShapefile(tLP, tS, None)
				bands.append(bX)
		else:
			# subset 
			tLX, tLY, pS = cfg.utls.imageInformation(rasterName)
			tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + dT + ".tif")
			pr = cfg.utls.subsetImage(rasterName, rCX, rCY, int(round(rW/pS + 3)),  int(round(rH/pS + 3)), str(tS))
			if pr == "Yes":
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error edge")
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				return pr
			oList = cfg.utls.rasterToBands(tS, cfg.tmpDir, None, "No", cfg.bndSetMultAddFactorsList)
			rL = cfg.utls.selectLayerbyName(rasterName, "Yes")
			bCount = rL.bandCount()
			for b in range(0, bCount):
				tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + str(b) + "_" + dT + ".tif")
				bX = cfg.utls.clipRasterByShapefile(tLP, oList[b], None)
				bands.append(bX)		
		return bands
		
	# subset image by rectangle
	def subsetImageByRectangle(self, rectangle, rasterName, bandList):
		# date time for temp name
		dT = cfg.utls.getTime()
		# calculate ROI center, height and width
		xMin = rectangle[0]
		xMax = rectangle[1]
		yMin = rectangle[2]
		yMax = rectangle[3]
		rCX = (xMax + xMin) / 2
		rW = (xMax - xMin)
		rCY = (yMax + yMin) / 2
		rH = (yMax - yMin)
		bands = []
		# band set
		if cfg.bndSetPresent == "Yes" and rasterName == cfg.bndSetNm:
			tLX, tLY, pS = cfg.utls.imageInformation(cfg.bndSet[0])
			# subset 
			for b in bandList:
				tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + str(b) + "_" + dT + ".tif")
				pr = cfg.utls.subsetImage(cfg.bndSet[b], rCX, rCY, int(round(rW/pS + 3)),  int(round(rH/pS + 3)), tS)
				if pr == "Yes":
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error edge")
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					return pr
				bands.append(tS)
		else:
			# subset 
			tLX, tLY, pS = cfg.utls.imageInformation(rasterName)
			tS = str(cfg.tmpDir + "//" + cfg.subsTmpRaster + "_" + dT + ".tif")
			pr = cfg.utls.subsetImage(rasterName, rCX, rCY, int(round(rW/pS + 3)),  int(round(rH/pS + 3)), str(tS))
			if pr == "Yes":
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " Error edge")
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				return pr
			oList = cfg.utls.rasterToBands(tS, cfg.tmpDir, None, "No", cfg.bndSetMultAddFactorsList)
			n = 0
			for b in oList:
				if n in bandList:
					bands.append(b)
				n = n + 1
		return bands
			
##################################
	""" Interface functions """
##################################
	
	# Question box
	def questionBox(self, caption, message):
		i = cfg.QtGuiSCP.QWidget()
		q = cfg.QtGuiSCP.QMessageBox.question(i, caption, message, cfg.QtGuiSCP.QMessageBox.Yes, cfg.QtGuiSCP.QMessageBox.No)
		if q == cfg.QtGuiSCP.QMessageBox.Yes:
			return "Yes"
		if q == cfg.QtGuiSCP.QMessageBox.No:
			return "No"

	# show hide input image
	def showHideInputImage(self):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			i = cfg.tmpVrt
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
		try:
			if i is not None:
				if cfg.inputImageRadio.isChecked():
					cfg.lgnd.setLayerVisible(i, True)
					cfg.utls.moveLayerTop(i)
				else:
					cfg.lgnd.setLayerVisible(i, False)
		except:
			pass
			
	# refresh classification combo
	def refreshRasterExtent(self):
		ls = cfg.lgnd.layers()
		cfg.ui.raster_extent_combo.clear()
		cfg.dlg.raster_extent_combo(cfg.mapExtent)
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				cfg.dlg.raster_extent_combo(l.name())
				
	# refresh classification combo
	def refreshClassificationLayer(self):
		ls = cfg.lgnd.layers()
		cfg.ui.classification_name_combo.clear()
		cfg.ui.classification_report_name_combo.clear()
		cfg.ui.classification_vector_name_combo.clear()
		cfg.ui.reclassification_name_combo.clear()
		cfg.ui.edit_raster_name_combo.clear()
		cfg.ui.sieve_raster_name_combo.clear()
		cfg.ui.erosion_raster_name_combo.clear()
		cfg.ui.dilation_raster_name_combo.clear()
		cfg.ui.reference_raster_name_combo.clear()
		# classification name
		self.clssfctnNm = None
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.classification_layer_combo(l.name())
					cfg.dlg.classification_report_combo(l.name())
					cfg.dlg.classification_to_vector_combo(l.name())
					cfg.dlg.reclassification_combo(l.name())
					cfg.dlg.edit_raster_combo(l.name())
					cfg.dlg.sieve_raster_combo(l.name())
					cfg.dlg.erosion_raster_combo(l.name())
					cfg.dlg.dilation_raster_combo(l.name())
					cfg.dlg.reference_raster_combo(l.name())
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification layers refreshed")
			
	# refresh vector combo
	def refreshVectorLayer(self):
		cfg.ui.vector_name_combo.blockSignals(True)
		cfg.ui.vector_name_combo_2.blockSignals(True)
		ls = cfg.lgnd.layers()
		cfg.ui.shapefile_comboBox.clear()
		cfg.ui.vector_name_combo.clear()
		cfg.ui.vector_name_combo_2.clear()
		for l in ls:
			if (l.type()==QgsMapLayer.VectorLayer):
				if (l.geometryType() == QGis.Polygon):
					cfg.dlg.shape_clip_combo(l.name())
					cfg.dlg.vector_to_raster_combo(l.name())
					cfg.dlg.vector_edit_raster_combo(l.name())
		cfg.ui.vector_name_combo.blockSignals(False)
		cfg.ui.vector_name_combo_2.blockSignals(False)
		cfg.utls.refreshVectorFields()
		cfg.utls.refreshVectorFields2()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "vector layers refreshed")
			
	# reference layer name
	def refreshVectorFields(self):
		referenceLayer = cfg.ui.vector_name_combo.currentText()
		cfg.ui.field_comboBox.clear()
		l = cfg.utls.selectLayerbyName(referenceLayer)
		try:
			if l.type()== 0:
				f = l.dataProvider().fields()
				for i in f:
					if i.typeName() != "String":
						cfg.dlg.reference_field_combo(unicode(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
						
	# reference layer name
	def refreshVectorFields2(self):
		referenceLayer = cfg.ui.vector_name_combo_2.currentText()
		cfg.ui.field_comboBox_2.clear()
		l = cfg.utls.selectLayerbyName(referenceLayer)
		try:
			if l.type()== 0:
				f = l.dataProvider().fields()
				for i in f:
					if i.typeName() != "String":
						cfg.dlg.reference_field_combo2(unicode(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			
	# get random color and complementary color
	def randomColor(self):
		r = cfg.randomSCP.randint(0,255)
		g = cfg.randomSCP.randint(0,255)
		b = cfg.randomSCP.randint(0,255)
		c = cfg.QtGuiSCP.QColor(r, g, b)
		cc = cfg.QtGuiSCP.QColor(255 - r, 255 - r, 225 - r)
		return c, cc
		
	# select color
	def selectColor(self):
		c = cfg.QtGuiSCP.QColorDialog.getColor()
		if c.isValid():
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "color")
			return c
			
	# get save file name
	def getSaveFileName(self, parent, text, directory, filterText):
		directory = cfg.lastSaveDir
		out = cfg.QtGuiSCP.QFileDialog.getSaveFileName(None, text, directory, filterText)
		cfg.lastSaveDir = cfg.osSCP.path.dirname(out)
		return out
					
	# get open file name
	def getOpenFileName(self, parent, text, directory, filterText):
		directory = cfg.lastSaveDir
		out = cfg.QtGuiSCP.QFileDialog.getOpenFileName(None, text, directory, filterText)
		cfg.lastSaveDir = cfg.osSCP.path.dirname(out)
		return out
							
	# get open file names
	def getOpenFileNames(self, parent, text, directory, filterText):
		directory = cfg.lastSaveDir
		out = cfg.QtGuiSCP.QFileDialog.getOpenFileNames(None, text, directory, filterText)
		if len(out) > 0:
			cfg.lastSaveDir = cfg.osSCP.path.dirname(out[0])
		return out
		
	# get existing directory
	def getExistingDirectory(self, parent, text):
		directory = cfg.lastSaveDir
		out = cfg.QtGuiSCP.QFileDialog.getExistingDirectory(None, text, directory)
		cfg.lastSaveDir = out
		return out
			
##################################
	""" QGIS functions """
##################################

	# get QGIS Proxy settings
	def getQGISProxySettings(self):
		cfg.proxyEnabled = cfg.utls.readRegistryKeys("proxy/proxyEnabled", "")
		cfg.proxyType = cfg.utls.readRegistryKeys("proxy/proxyType", "")
		cfg.proxyHost = cfg.utls.readRegistryKeys("proxy/proxyHost", "")
		cfg.proxyPort = cfg.utls.readRegistryKeys("proxy/proxyPort", "")
		cfg.proxyUser = cfg.utls.readRegistryKeys("proxy/proxyUser", "")
		cfg.proxyPassword = cfg.utls.readRegistryKeys("proxy/proxyPassword", "")
		
	# save memory layer to shapefile
	def saveMemoryLayerToShapefile(self, memoryLayer, output, name = None):
		shpF = output
		# create shapefile
		f = QgsFields()
		# add Class ID, macroclass ID and Info fields
		f.append(QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))
		f.append(QgsField(cfg.fldROIMC_info, cfg.QVariantSCP.String))
		f.append(QgsField(cfg.fldID_class, cfg.QVariantSCP.Int))
		f.append(QgsField(cfg.fldROI_info, cfg.QVariantSCP.String))
		f.append(QgsField(cfg.fldSCP_UID, cfg.QVariantSCP.String))
		pCrs = cfg.utls.getCrs(memoryLayer)
		QgsVectorFileWriter(unicode(shpF), "CP1250", f, QGis.WKBMultiPolygon , pCrs, "ESRI Shapefile")
		if name is None:
			name = cfg.osSCP.path.basename(shpF)
		tSS = cfg.utls.addVectorLayer(shpF, name, "ogr")
		tSS.updateFields()
		f = QgsFeature()
		tSS.startEditing()
		for f in memoryLayer.getFeatures():
			tSS.addFeature(f)	
		tSS.commitChanges()
		tSS.dataProvider().createSpatialIndex()
		tSS.updateExtents()
		return tSS

	# read registry keys
	def readRegistryKeys(self, key, value):
		rK = cfg.QSettingsSCP()
		val = rK.value(key, value)
		return val
		
	# create a polygon shapefile with QGIS
	def createEmptyShapefileQGIS(self, crs, outputVector):
		fields = QgsFields()
		# add field
		fN = cfg.emptyFN
		fields.append(QgsField(fN, cfg.QVariantSCP.Int))	
		QgsVectorFileWriter(unicode(outputVector), "CP1250", fields, QGis.WKBMultiPolygon, crs, "ESRI Shapefile")

	# Raster no data value
	def imageNoDataValue(self, rasterPath):
		rD = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_ReadOnly)
		gBand = rD.GetRasterBand(1) 
		nd = gBand.GetNoDataValue()
		gBand = None
		rD = None
		return nd
		
	# Raster no data value
	def imageNoDataValueQGIS(self, qgisRaster):
		nd = qgisRaster.dataProvider().srcNoDataValue(1)
		return nd
		
	# Raster top left origin and pixel size
	def imageInformation(self, imageName):
		try:
			i = self.selectLayerbyName(imageName, "Yes")
			# TopLeft X coord
			tLX = i.extent().xMinimum()
			# TopLeft Y coord
			tLY = i.extent().yMaximum()
			# pixel size
			pS = i.rasterUnitsPerPixelX()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "image: " + unicode(imageName) + " topleft: (" + str(tLX) + ","+ str(tLY) + ")")
			# return a tuple TopLeft X, TopLeft Y, and Pixel size
			return tLX, tLY, pS
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return None, None, None
			
	# Raster size
	def imageInformationSize(self, imageName):
		try:
			i = self.selectLayerbyName(imageName, "Yes")
			# TopLeft X coord
			tLX = i.extent().xMinimum()
			# TopLeft Y coord
			tLY = i.extent().yMaximum()
			# LowRight X coord
			lRY = i.extent().yMinimum()
			# LowRight Y coord
			lRX = i.extent().xMaximum()
			# pixel size
			pS = i.rasterUnitsPerPixelX()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "image: " + unicode(imageName) + " topleft: (" + str(tLX) + ","+ str(tLY) + ")")
			# return a tuple TopLeft X, TopLeft Y, and Pixel size
			return tLX, tLY, lRX, lRY, pS
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return None, None, None, None, None

	# Get CRS of a layer by name thereof
	def getCrs(self, lddRstr):
		if lddRstr is None:
			crs = None
		else:
			rP = lddRstr.dataProvider()
			crs = rP.crs()
		return crs
		
	# Pan action
	def pan(self):
		cfg.toolPan = QgsMapToolPan(cfg.cnvs)
		cfg.cnvs.setMapTool(cfg.toolPan)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "pan action")

	# Project point coordinates
	def projectPointCoordinates(self, point, inputCoordinates, outputCoordinates):
		try:
			t = QgsCoordinateTransform(inputCoordinates, outputCoordinates)
			point = t.transform(point)
			return point
		# if empty shapefile
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return False

	# Group index by its name
	def groupIndex(self, groupName):
		g = cfg.lgnd.groups()
		if len(g) > 0:
			# all positions
			aP = len(g)
			for p in range(0, aP):
				if g[p] == groupName:
						# group position
						return p
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group " + unicode(groupName) + " Position: " + unicode(p))

	# Layer ID by its name
	def layerID(self, layerName):
	 	ls = cfg.lgnd.layers()
		for l in ls:
			lN = l.name()
			if lN == layerName:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer: " + unicode(layerName) + " ID: " + unicode(l.id()))
				return l.id()
						
	# read project variable
	def readProjectVariable(self, variableName, value):
		p = cfg.qgisCoreSCP.QgsProject.instance()
		v = p.readEntry("SemiAutomaticClassificationPlugin", variableName, value)[0]
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "variable: " + unicode(variableName) + " - value: " + unicode(value))
		return v
		
	# read QGIS path project variable
	def readQGISVariablePath(self):
		cfg.projPath = cfg.qgisCoreSCP.QgsProject.instance().fileName()
		p = cfg.qgisCoreSCP.QgsProject.instance()
		v = p.readEntry("Paths", "Absolute", "")[0]
		cfg.absolutePath = v
		
	# write project variable
	def writeProjectVariable(self, variableName, value):
		p = cfg.qgisCoreSCP.QgsProject.instance()
		p.writeEntry("SemiAutomaticClassificationPlugin", variableName, value)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "variable: " + unicode(variableName) + " - value: " + unicode(value))
		
	# absolute to relative path
	def qgisAbsolutePathToRelativePath(self, absolutePath, relativePath):
		p = cfg.qgisCoreSCP.QgsApplication.absolutePathToRelativePath(absolutePath, relativePath)
		return p
		
	# relative to absolute path
	def qgisRelativePathToAbsolutePath(self, relativePath, absolutePath):
		p = cfg.qgisCoreSCP.QgsApplication.relativePathToAbsolutePath(relativePath, absolutePath)
		return p
		
	# Remove layer from map
	def removeLayer(self, layerName):
		try:
			QgsMapLayerRegistry.instance().removeMapLayer(self.layerID(layerName))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer: " + unicode(layerName))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))	
			
	# Remove layer from map
	def removeLayerByLayer(self, layer):
		try:
			QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
	# Remove layer from map
	def removeGroup(self, groupName):
		g = cfg.utls.groupIndex(cfg.grpNm)
		try:
			if g is not None:
				cfg.lgnd.removeGroup(g)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group: " + unicode(groupName))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))

	# remove temporary files from project
	def removeTempFiles(self):
		# disable map canvas render
		cfg.cnvs.setRenderFlag(False)
		try:
			for p in cfg.prevList:
				pp = cfg.utls.selectLayerbyName(p.name())
				if pp is not None:
					cfg.utls.removeLayerByLayer(p)
			vrt = cfg.utls.selectLayerbyName(cfg.tmpVrtNm + ".vrt")
			if vrt is not None:
				cfg.utls.removeLayerByLayer(cfg.tmpVrt)
			cfg.utls.removeGroup(cfg.grpNm)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		cfg.prevList = []
		cfg.tmpVrt = None
		# enable map canvas render
		cfg.cnvs.setRenderFlag(True)
			
	# Create group
	def createGroup(self, groupName):
		g = cfg.lgnd.addGroup(groupName, False)
		cfg.utls.moveGroup(groupName)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group: " + unicode(groupName))
		return g		
	
	# Move group to top layers
	def moveGroup(self, groupName):
		# QGIS >= 2.4
		try:
			p = cfg.qgisCoreSCP.QgsProject.instance()
			root = p.layerTreeRoot()
			g = root.findGroup(groupName)
			cG = g.clone()
			root.insertChildNode(0, cG)
			root.removeChildNode(g)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group: " + unicode(groupName))
		# QGIS < 2.4
		except Exception, err:
			if "layerTreeRoot" not in str(err):
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# Move layer to top layers
	def moveLayerTop(self, layer):
		# QGIS >= 2.4
		try:
			p = cfg.qgisCoreSCP.QgsProject.instance()
			root = p.layerTreeRoot()
			g = root.findLayer(layer.id())
			cG = g.clone()
			root.insertChildNode(0, cG)
			root.removeChildNode(g)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer: " + unicode(layer.name()))
		# QGIS < 2.4
		except Exception, err:
			if "layerTreeRoot" not in str(err):
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# Select layer by name thereof
	def selectLayerbyName(self, layerName, filterRaster=None):
	 	ls = cfg.lgnd.layers()
		for l in ls:
			lN = l.name()
			if lN == layerName:
				if filterRaster is None:
					return l
				else:
					if l.type() == 1:
						return l
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer selected: " + unicode(layerName))
	
	# file path
	def getFilePath(self, layerName):
		try:
			l = cfg.utls.selectLayerbyName(layerName)
			filePath = l.source()
			return filePath
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
	
	# set map extent from layer
	def setMapExtentFromLayer(self, layer):
		ext = layer.extent()
		tLPoint = QgsPoint(ext.xMinimum(), ext.yMaximum())
		lRPoint = QgsPoint(ext.xMaximum(), ext.yMinimum())
		point1 = tLPoint
		point2 = lRPoint
		# project extent
		iCrs = cfg.utls.getCrs(layer)
		pCrs = cfg.utls.getQGISCrs()
		if iCrs is None:
			iCrs = pCrs
		# projection of input point from raster's crs to project's crs
		if pCrs != iCrs:
			try:
				point1 = cfg.utls.projectPointCoordinates(tLPoint, iCrs, pCrs)
				point2 = cfg.utls.projectPointCoordinates(lRPoint, iCrs, pCrs)
				if point1 is False:
					point1 = tLPoint
					point2 = lRPoint
			# Error latitude or longitude exceeded limits
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				point1 = tLPoint
				point2 = lRPoint
		cfg.cnvs.setExtent(QgsRectangle(point1, point2))
		
	# save a qml style
	def saveQmlStyle(self, layer, stylePath):
		layer.saveNamedStyle(stylePath)
		
	# Zoom to selected feature of layer
	def zoomToSelected(self, layer, featureID):
		layer.removeSelection()
		layer.select(featureID)
		cfg.cnvs.zoomToSelected(layer)
		layer.deselect(featureID)
		
	# Zoom to band set
	def zoomToBandset(self):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			b = cfg.utls.selectLayerbyName(cfg.bndSet[0], "Yes")
		else:
			b = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
		if b is not None:
			cfg.utls.setMapExtentFromLayer(b)
			cfg.cnvs.refresh()
			
	# Add layer to map
	def addLayerToMap(self, layer):
		QgsMapLayerRegistry.instance().addMapLayers([layer])
		
	# Add layer
	def addVectorLayer(self, path, name, format):
		l = QgsVectorLayer(path, name, format)
		return l
		
	# Add raster layer
	def addRasterLayer(self, path, name):
		if cfg.osSCP.path.isfile(path):
			r = cfg.iface.addRasterLayer(path, name)
			return r
		else:
			return "No"

	# Get QGIS project CRS
	def getQGISCrs(self):
		# QGIS < 2.4
		try:
			pCrs = cfg.cnvs.mapRenderer().destinationCrs()
		# QGIS >= 2.4
		except:
			pCrs = cfg.cnvs.mapSettings().destinationCrs()
		return pCrs
		
	# Set QGIS project CRS
	def setQGISCrs(self, crs):
		# QGIS < 2.4
		try:
			cfg.cnvs.mapRenderer().setDestinationCrs(crs)
		# QGIS >= 2.4
		except:
			cfg.cnvs.setDestinationCrs(crs)
		
##################################
	""" raster GDAL functions """
##################################
			
	# Get the number of bands of a raster
	def getNumberBandRaster(self, raster):
		rD = cfg.gdalSCP.Open(raster, cfg.gdalSCP.GA_ReadOnly)
		number = rD.RasterCount
		rD = None
		return number
			
	# # set GDAL cache max (deprecated)
	# def setGDALCacheMax(self, value):
		# c = cfg.gdalSCP.GetCacheMax()
		# cfg.gdalSCP.SetCacheMax(value)
		
	# raster sieve with GDAL
	def rasterSieve(self, inputRaster, outputRaster, pixelThreshold, connect = 4, outFormat = "GTiff", quiet = "No"):
		if cfg.sysSCPNm == "Windows":
			gD = "gdal_sieve.bat"
		else:
			gD = "gdal_sieve.py"
		st = "No"
		try:
			cfg.utls.getGDALForMac()
			a = cfg.gdalPath + gD + " -st " + str(pixelThreshold) + " -" + str(connect) + " " + inputRaster + " -of "+ outFormat + " " + outputRaster 
			sP = cfg.subprocessSCP.Popen(a, shell=True, stdout=cfg.subprocessSCP.PIPE, stderr=cfg.subprocessSCP.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				st = "Yes"
				if quiet == "No": 
					cfg.mx.msgErr45()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error: " + str(err) )
		# in case of errors
		except Exception, err:
			cfg.utls.getGDALForMac()
			a = cfg.gdalPath + gD + " -st " + str(pixelThreshold) + " -" + str(connect) + " " + inputRaster + " -of "+ outFormat + " " + outputRaster 
			sP = cfg.subprocessSCP.Popen(a, shell=True)
			sP.wait()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "sieve: " + unicode(outputRaster))
		return st
							
	# create virtual raster with GDAL
	def createVirtualRaster(self, inputRasterList, output, bandNumber = "No", quiet = "No"):
		r = ""
		st = "No"
		for i in inputRasterList:
			r = r + ' "' + i + '"'
		if bandNumber == "No":
			bndOption = " -separate"
		else:
			bndOption = "-b " + str(bandNumber)
		try:
			cfg.utls.getGDALForMac()
			sP = cfg.subprocessSCP.Popen(cfg.gdalPath + 'gdalbuildvrt -resolution highest ' + bndOption + ' "' + output.encode(cfg.sysSCP.getfilesystemencoding()) + '" ' + r.encode(cfg.sysSCP.getfilesystemencoding()), shell=True, stdout=cfg.subprocessSCP.PIPE, stderr=cfg.subprocessSCP.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				st = "Yes"
				if quiet == "No": 
					cfg.mx.msgWar13()
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error: " + str(err) )
		# in case of errors
		except Exception, err:
			cfg.utls.getGDALForMac()
			sP = cfg.subprocessSCP.Popen(cfg.gdalPath + 'gdalbuildvrt -resolution highest ' + bndOption + ' "' + output.encode(cfg.sysSCP.getfilesystemencoding()) + '" ' + r.encode(cfg.sysSCP.getfilesystemencoding()), shell=True)
			sP.wait()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "virtual raster: " + unicode(output))
		return st
					
	# build GDAL overviews
	def buildOverviewsGDAL(self, inputRaster):
		try:
			cfg.utls.getGDALForMac()
			sP = cfg.subprocessSCP.Popen(cfg.gdalPath + 'gdaladdo -r NEAREST -ro "' + inputRaster + '" 8 16 32 64 ', shell=True, stdout=cfg.subprocessSCP.PIPE, stderr=cfg.subprocessSCP.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error: " + str(err) )
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "build overviews" + unicode(i))
		# in case of errors
		except Exception, err:
			cfg.utls.getGDALForMac()
			sP = cfg.subprocessSCP.Popen(cfg.gdalPath + 'gdaladdo -r NEAREST -ro "' + inputRaster + '" 8 16 32 64 ', shell=True)
			sP.wait()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "build overviews" + unicode(inputRaster))

	# Try to get GDAL for Mac
	def getGDALForMac(self):
		if cfg.sysSCPNm == "Darwin":
			v = cfg.utls.getGDALVersion()
			cfg.gdalPath = '/Library/Frameworks/GDAL.framework/Versions/' + v[0] + '.' + v[1] + '/Programs/'
			if cfg.osSCP.path.isfile(cfg.gdalPath + "gdal_translate"):
				pass
			else:
				cfg.gdalPath = ''
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " getGDALForMac: " + unicode(cfg.gdalPath))
			
	# Get GDAL version
	def getGDALVersion(self):
		v = cfg.gdalSCP.VersionInfo("RELEASE_NAME").split('.')
		return v
			
	# get a raster band statistic
	def getRasterBandStatistics(self, inputRaster, band, multiAddList = None):
		# open input with GDAL
		rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
		if rD is None:
			bSt = None
			a = None
		else:
			iRB = rD.GetRasterBand(band)
			bSt = iRB.GetStatistics(True, True)
			a =  iRB.ReadAsArray()
			if multiAddList is not None:
				a = cfg.utls.arrayMultiplicativeAdditiveFactors(a, multiAddList[0], multiAddList[1])
				bSt = [bSt[0] * multiAddList[0] + multiAddList[1], bSt[1] * multiAddList[0] + multiAddList[1], bSt[2] * multiAddList[0] + multiAddList[1], bSt[3] * multiAddList[0]]
			# close band
			iRB = None
			# close raster
			rD = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "get band: " + unicode(band))
		return bSt, a

	# get ROI size
	def getROISize(self, inputRaster, band, min, max):
		# open input with GDAL
		rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
		if rD is None:
			s = None
		else:
			iRB = rD.GetRasterBand(band)
			a =  iRB.ReadAsArray()
			s = ( (a >= min) & (a <= max)).sum()
			# close band
			iRB = None
			# close raster
			rD = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "get band: " + unicode(band))
		return s
		
	# Get raster data type name
	def getRasterDataTypeName(self, inputRaster):
		rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
		b = rD.GetRasterBand(1)
		dType = cfg.gdalSCP.GetDataTypeName(b.DataType)
		rD = None
		return dType
	
	# create GDAL raster table
	def createRasterTable(self, rasterPath, bandNumber, signatureList):
		r = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_Update)
		b = r.GetRasterBand(bandNumber)
		at = cfg.gdalSCP.RasterAttributeTable()
		at.CreateColumn(str(cfg.fldID_class), cfg.gdalSCP.GFT_Integer, cfg.gdalSCP.GFU_Generic )
		at.CreateColumn(str(cfg.fldROI_info), cfg.gdalSCP.GFT_String, cfg.gdalSCP.GFU_Generic )
		v = signatureList
		if cfg.macroclassCheck == "Yes":
			mc = []
			for c in range(len(v)):
				mc.append(int(v[c][0]))
			mcList = list(set(mc))
			for i in range(len(mcList)):
				at.SetValueAsInt(i, 0, mcList[i])
				ind = mc.index(mcList[i])
				at.SetValueAsString(i, 1, v[ind][1])
		else:
			for i in range(len(v)):
				at.SetValueAsInt(i, 0, int(v[i][2]))
				at.SetValueAsString(i, 1, v[i][3])
		b.SetDefaultRAT(at)
		b = None
		r = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "" + unicode(rasterPath))
				
	# read all raster from band
	def readAllBandsFromRaster(self, gdalRaster):
		bandNumber = gdalRaster.RasterCount
		bandList = []
		for b in range(1, bandNumber + 1):
			rB = gdalRaster.GetRasterBand(b)
			bandList.append(rB)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		return bandList
		
	# copy raster with GDAL
	def GDALCopyRaster(self, input, output, outFormat = "GTiff", compress = "No", compressFormat = "DEFLATE", additionalParams = ""):
		if compress == "No":
			op = " -of " + outFormat
		else:
			op = " -co COMPRESS=" + compressFormat + " -of " + outFormat
		try:
			cfg.utls.getGDALForMac()
			gD = "gdal_translate"
			a = cfg.gdalPath + gD + " " + additionalParams + " " + op 
			b = '"' + input + '" '
			c = '"' + output + '" '
			d = a + " " + b + " " + c
			sP = cfg.subprocessSCP.Popen(d, shell=True, stdout=cfg.subprocessSCP.PIPE, stderr=cfg.subprocessSCP.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error:: " + str(err) )
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.utls.getGDALForMac()
			gD = "gdal_translate"
			a = cfg.gdalPath + gD + " " + additionalParams + " " + op 
			b = '"' + input + '" '
			c = '"' + output + '" '
			d = a + " " + b + " " + c
			sP = cfg.subprocessSCP.Popen(d, shell=True)
			sP.wait()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image: " + unicode(output))
			
	# Merge raster bands
	def mergeRasterBands(self, bandList, output, outFormat = "GTiff", compress = "No"):
		if compress == "No":
			op = "-of " + outFormat
		else:
			op = "-co COMPRESS=LZW -of " + outFormat
		input = ""
		for b in bandList:
			input = input + '"' + b.encode(cfg.sysSCP.getfilesystemencoding()) + '" '
		input = input
		try:
			cfg.utls.getGDALForMac()
			if cfg.sysSCPNm == "Windows":
				gD = "gdal_merge.bat"
			else:
				gD = "gdal_merge.py"
			a = cfg.gdalPath + gD + ' -separate ' + op + ' -o '
			b = '"' + output.encode(cfg.sysSCP.getfilesystemencoding()) + '" '
			c = input
			d = a + b + c
			sP = cfg.subprocessSCP.Popen(d, shell=True, stdout=cfg.subprocessSCP.PIPE, stderr=cfg.subprocessSCP.PIPE)
			sP.wait()
			# get error
			out, err = sP.communicate()
			sP.stdout.close()
			if len(err) > 0:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " GDAL error:: " + str(err) )
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.utls.getGDALForMac()
			if cfg.sysSCPNm == "Windows":
				gD = "gdal_merge.bat"
			else:
				gD = "gdal_merge.py"
			a = cfg.gdalPath + gD + ' -separate ' + op + ' -o '
			b = '"' + output.encode(cfg.sysSCP.getfilesystemencoding()) + '" '
			c = input
			d = a + b + c
			sP = cfg.subprocessSCP.Popen(d, shell=True)
			sP.wait()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image: " + unicode(output))
			
	# Subset an image, given an origin point and a subset width
	def subsetImage(self, imageName, XCoord, YCoord, Width, Height, output, outFormat = "GTiff", virtual = "No"):
		i = self.selectLayerbyName(imageName, "Yes")
		# output variable
		st = "Yes"
		if i is not None:
			bandNumberList = []
			for bb in range(1, i.bandCount()+1):
				bandNumberList.append(bb)
			i = i.source().encode(cfg.sysSCP.getfilesystemencoding())
			st = "No"
			# raster top left origin and pixel size
			tLX, tLY, lRX, lRY, pS = self.imageInformationSize(imageName)
			if pS is None:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image none or missing")
			else:		
				try:
					dType = self.getRasterDataTypeName(i)
					# subset origin
					UX = tLX + abs(int((tLX - XCoord) / pS )) * pS - (Width -1 )/ 2 * pS
					UY = tLY - abs(int((tLY - YCoord) / pS )) * pS + (Height -1 )/ 2 * pS
					LX = UX + Width * pS
					LY = UY - Height * pS
					dT = cfg.utls.getTime()
					tPMN = cfg.tmpVrtNm + ".vrt"
					tPMD = cfg.tmpDir + "/" + dT + tPMN
					bList = [i]
					if virtual == "No":
						st = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", cfg.NoDataVal, 0, "No", "Yes", [float(UX), float(UY), float(LX), float(LY)])
						clipOutput = cfg.utls.copyRaster(tPMD, output, str(outFormat), cfg.NoDataVal)
						st = clipOutput
					else:
						st = cfg.utls.createVirtualRaster2(bList, output, bandNumberList, "Yes", cfg.NoDataVal, 0, "No", "Yes", [float(UX), float(UY), float(LX), float(LY)])
				# in case of errors
				except Exception, err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					st = "Yes"
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "image: " + unicode(imageName) + " subset origin: (" + str(XCoord) + ","+ str(YCoord) + ") width: " + str(Width))
		return st
			
	# get EPSG for vector
	def getEPSGVector(self, layerPath):
		l = cfg.ogrSCP.Open(layerPath)
		if l is None:
			return "No"
		gL = l.GetLayer()
		# check projection
		lP = cfg.osrSCP.SpatialReference()
		lP = gL.GetSpatialRef()
		lP.AutoIdentifyEPSG()
		lPRS = lP.GetAuthorityCode(None)
		epsg = int(lPRS)
		l.Destroy()
		return epsg
			
	# get EPSG for vector QGIS
	def getEPSGVectorQGIS(self, layer):
		pCrs = cfg.utls.getCrs(layer)
		id = pCrs.authid()
		id = int(id.replace("EPSG:", ""))
		return id
		
	# get EPSG for raster
	def getEPSGRaster(self, layerPath):
		rD = cfg.gdalSCP.Open(layerPath, cfg.gdalSCP.GA_ReadOnly)
		# check projections
		rP = rD.GetProjection()
		rPSys =cfg.osrSCP.SpatialReference(wkt=rP)
		rPSys.AutoIdentifyEPSG()
		rPRS = rPSys.GetAuthorityCode(None)
		epsg = int(rPRS)
		return epsg
		
	# convert reference layer to raster based on the resolution of a raster
	def vectorToRaster(self, fieldName, layerPath, referenceRasterName, outputRaster, referenceRasterPath=None, ALL_TOUCHED=None, outFormat = "GTiff", burnValues = None):
		if referenceRasterPath is None:
			# band set
			if cfg.bndSetPresent == "Yes" and referenceRasterName == cfg.bndSetNm:
				referenceRasterName = cfg.bndSet[0]
				# input
				r = self.selectLayerbyName(referenceRasterName, "Yes")
			else:
				if self.selectLayerbyName(referenceRasterName, "Yes") is None:
					cfg.mx.msg4()
					cfg.ipt.refreshRasterLayer()
				else:
					# input
					r = self.selectLayerbyName(referenceRasterName, "Yes")
			try:
				rS = r.source()
				ck = "Yes"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				ck = "No"
				cfg.mx.msg4()
				return ck
		else:
			rS = referenceRasterPath
		try:
			# open input with GDAL
			rD = cfg.gdalSCP.Open(rS, cfg.gdalSCP.GA_ReadOnly)
			# number of x pixels
			rC = rD.RasterXSize
			# number of y pixels
			rR = rD.RasterYSize
			# check projections
			rP = rD.GetProjection()
			# pixel size and origin
			rGT = rD.GetGeoTransform()
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msg4()
			return "No"
		l = cfg.ogrSCP.Open(layerPath)
		try:
			gL = l.GetLayer()
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr34()
			return "No"
		# check projection
		lP = cfg.osrSCP.SpatialReference()
		lP = gL.GetSpatialRef()
		lP.AutoIdentifyEPSG()
		lPRS = lP.GetAuthorityCode(None)
		rPSys =cfg.osrSCP.SpatialReference(wkt=rP)
		rPSys.AutoIdentifyEPSG()
		rPRS = rPSys.GetAuthorityCode(None)
		if lP != "":
			if lPRS == None:
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error None lP: " + unicode(lP) + "rPRS: " + unicode(rPRS))
			if lPRS != rPRS:
				# date time for temp name
				dT = cfg.utls.getTime()
				reprjShapefile = cfg.tmpDir + "/" + dT + cfg.osSCP.path.basename(layerPath)
				cfg.utls.repojectShapefile(layerPath, int(lPRS), reprjShapefile, int(rPRS))
				l.Destroy()
				l = cfg.ogrSCP.Open(reprjShapefile)
				gL = l.GetLayer()
			minX, maxX, minY, maxY = gL.GetExtent()
			origX = rGT[0] +  rGT[1] * int(round((minX - rGT[0]) / rGT[1]))
			origY = rGT[3] + rGT[5] * int(round((maxY - rGT[3]) / rGT[5]))
			rC = abs(int(round((maxX - minX) / rGT[1])))
			rR = abs(int(round((maxY - minY) / rGT[5])))
			tD = cfg.gdalSCP.GetDriverByName(outFormat)
			oR = tD.Create(outputRaster, rC, rR, 1, cfg.gdalSCP.GDT_Float32)
			try:
				oRB = oR.GetRasterBand(1)
			# in case of errors
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.mx.msgErr34()
				return "No"
			# set raster projection from reference
			oR.SetGeoTransform( [ origX , rGT[1] , 0 , origY , 0 , rGT[5] ] )
			oR.SetProjection(rP)
			oRB.SetNoDataValue(cfg.NoDataVal)
			m = cfg.np.zeros((rR, rC), dtype=cfg.np.float64)
			m.fill(cfg.NoDataVal)
			oRB.WriteArray(m, 0, 0)
			oRB.FlushCache()
			# close bands
			oRB = None
			# convert reference layer to raster
			if ALL_TOUCHED is None:
				if burnValues is None:
					oC = cfg.gdalSCP.RasterizeLayer(oR, [1], gL, options = ["ATTRIBUTE=" + str(fieldName)])
				else:
					oC = cfg.gdalSCP.RasterizeLayer(oR, [1], gL, burn_values=[burnValues])
			else:
				if burnValues is None:
					oC = cfg.gdalSCP.RasterizeLayer(oR, [1], gL, options = ["ATTRIBUTE=" + str(fieldName), "ALL_TOUCHED=TRUE"])
				else:
					oC = cfg.gdalSCP.RasterizeLayer(oR, [1], gL, burn_values=[burnValues], options = ["ALL_TOUCHED=TRUE"])
			# close rasters
			oR = None
			rD = None
			l.Destroy()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "vector to raster check: " + unicode(oC))
		else:
			cfg.mx.msg9()
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "lP: " + unicode(lP) + "rPRS: " + unicode(rPRS))
			return "No"
			
	# convert raster to shapefile
	def rasterToVector(self, rasterPath, outputShapefilePath, fieldName = "No"):
		tD = cfg.gdalSCP.GetDriverByName( "GTiff" )
		# open input with GDAL
		try:
			rD = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_ReadOnly)
			# number of x pixels
			rC = rD.RasterXSize
		# in case of errors
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return "No"
		# create a shapefile
		d = cfg.ogrSCP.GetDriverByName('ESRI Shapefile')
		dS = d.CreateDataSource(outputShapefilePath)
		if dS is None:
			# close rasters
			rD = None
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " error: " + unicode(outputShapefilePath))
		else:
			# shapefile
			sR = cfg.osrSCP.SpatialReference()
			sR.ImportFromWkt(rD.GetProjectionRef())
			rL = dS.CreateLayer(cfg.osSCP.path.basename(rasterPath).encode(cfg.sysSCP.getfilesystemencoding()), sR, cfg.ogrSCP.wkbMultiPolygon)
			if fieldName == "No":
				fN = str(cfg.fldID_class)
			else:
				fN = fieldName
			fd = cfg.ogrSCP.FieldDefn(fN, cfg.ogrSCP.OFTInteger)
			try:
				rL.CreateField(fd)
			# in case of errors
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				# close rasters
				rD = None
				return "No"
			fld = rL.GetLayerDefn().GetFieldIndex(fN)
			rRB = rD.GetRasterBand(1)
			# raster to polygon
			cfg.gdalSCP.Polygonize(rRB, rRB.GetMaskBand(), rL, fld)		
			# close rasters and shapefile
			rRB = None
			rD = None			
			dS = None							
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " vector output performed")

##################################
	""" vector functions """
##################################
		
	# zip a directory
	def zipDirectoryInFile(self, zipPath, fileDirectory):
		zip = cfg.zipfileSCP.ZipFile(zipPath, 'w')
		for f in cfg.osSCP.listdir(fileDirectory):
			zip.write(fileDirectory + "/" + f)
		zip.close()
	
	# create backup file
	def createBackupFile(self, filePath):
		try:
			cfg.shutilSCP.copy(filePath, filePath + "." + cfg.backupNm)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# create a polygon shapefile with OGR
	def createEmptyShapefile(self, crsWkt, outputVector):
		d = cfg.ogrSCP.GetDriverByName('ESRI Shapefile')
		dS = d.CreateDataSource(outputVector)
		# shapefile
		sR = cfg.osrSCP.SpatialReference()
		sR.ImportFromWkt(crsWkt)
		rL = dS.CreateLayer('NewLayer', sR, cfg.ogrSCP.wkbMultiPolygon)
		fN = cfg.emptyFN
		fd = cfg.ogrSCP.FieldDefn(fN, cfg.ogrSCP.OFTInteger)
		rL.CreateField(fd)
		rL = None
		dS = None

	# Get extent of a shapefile
	def getShapefileRectangleBox(self, layer):
		try:
			d = cfg.ogrSCP.GetDriverByName("ESRI Shapefile")
			dr = d.Open(layer.source(), 1)
			l = dr.GetLayer()
			e = l.GetExtent()
			minX = e[0]
			minY = e[2]
			maxX = e[1]
			maxY = e[3]
			centerX = (maxX + minX) / 2
			centerY = (maxY + minY) / 2
			width = maxX - minX
			heigth = maxY - minY
			l = None
			dr = None
			return centerX, centerY, width, heigth
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi bounding box: center " + str(r.center()) + " width: " + str(r.width())+ " height: " + str(r.height()))
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
	# get ID by attributes
	def getIDByAttributes(self, layer, field, attribute):
		IDs = []
		fR = layer.getFeatures(QgsFeatureRequest().setFilterExpression('"' + str(field) + '" = \'' + str(attribute) + '\''))
		for f in fR:
			IDs.append(f.id())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID: " + str(IDs))
		return IDs
		
	# Get last feauture id
	def getLastFeatureID(self, layer):
		f = QgsFeature()
		for f in layer.getFeatures():
			ID = f.id()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID: " + str(ID))
		return ID
		
	# Get a feature from a shapefile by feature ID
	def getFeaturebyID(self, layer, ID):
		f = QgsFeature()
		# feature request
		fR = QgsFeatureRequest().setFilterFid(ID)
		try:
			f = layer.getFeatures(fR)
			f = f.next()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "get feature " + str(ID) + " from shapefile: " + unicode(layer.name()))
			return f
		# if empty shapefile
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return False
				
	# Get a feature box by feature ID
	def getFeatureRectangleBoxbyID(self, layer, ID):
		d = cfg.ogrSCP.GetDriverByName("ESRI Shapefile")
		dr = d.Open(layer.source(), 1)
		l = dr.GetLayer()
		f = l.GetFeature(ID)
		# bounding box rectangle
		e = f.GetGeometryRef().GetEnvelope()
		minX = e[0]
		minY = e[2]
		maxX = e[1]
		maxY = e[3]
		centerX = (maxX + minX) / 2
		centerY = (maxY + minY) / 2
		width = maxX - minX
		heigth = maxY - minY
		l = None
		dr = None
		return centerX, centerY, width, heigth
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi bounding box: center " + str(r.center()) + " width: " + str(r.width())+ " height: " + str(r.height()))
		try:
			pass
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			pass
		
	# Delete a feauture from a shapefile by its Id
	def deleteFeatureShapefile(self, layer, feautureIds):
		layer.startEditing()				
		res = layer.dataProvider().deleteFeatures(feautureIds)
		layer.commitChanges()
		res2 = layer.dataProvider().createSpatialIndex()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feauture deleted: " + unicode(layer) + " " + str(feautureIds) )

	# Edit a feauture in a shapefile by its Id
	def editFeatureShapefile(self, layer, feautureId, fieldName, value):
		id = self.fieldID(layer, fieldName)
		layer.startEditing()				
		res = layer.changeAttributeValue(feautureId, id, value)
		layer.commitChanges()
		res2 = layer.dataProvider().createSpatialIndex()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feauture edited: " + unicode(layer) + " " + str(feautureId) )
		
### Copy feature by ID to layer
	def copyFeatureToLayer(self, sourceLayer, ID, targetLayer):
		f = self.getFeaturebyID(sourceLayer, ID)
		# get geometry
		fG = f.geometry()
		f.setGeometry(fG)
		sF = targetLayer.pendingFields()
		f.initAttributes(sF.count())
		if f.geometry() is None:
			cfg.mx.msg6()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feature geometry is none")			
		else:	
			# copy polygon to shapefile
			targetLayer.startEditing()
			targetLayer.addFeature(f)	
			targetLayer.commitChanges()
			targetLayer.dataProvider().createSpatialIndex()
			targetLayer.updateExtents()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "feature copied")
				
	# merge polygons
	def mergePolygons(self, targetLayer, idList, attributeList):
		f = cfg.utls.getFeaturebyID(targetLayer, idList[0])
		sg = QgsGeometry(f.geometry())
		for i in idList:
			if i != idList[0]:
				f = cfg.utls.getFeaturebyID(targetLayer, i)
				g = QgsGeometry(f.geometry())
				g.convertToMultiType()
				sg.addPartGeometry(g)
		pr = targetLayer.dataProvider()
		targetLayer.startEditing()		
		f.setGeometry(sg)
		f.setAttributes(attributeList)
		pr.addFeatures([f])
		targetLayer.commitChanges()
		targetLayer.updateExtents()
		return targetLayer
		
	# merge polygons to new layer
	def mergePolygonsToNewLayer(self, targetLayer, idList, attributeList):
		# create memory layer
		provider = targetLayer.dataProvider()
		fields = provider.fields()
		pCrs = cfg.utls.getCrs(targetLayer)
		mL = QgsVectorLayer("MultiPolygon?crs=" + str(pCrs.toWkt()), "memoryLayer", "memory")
		mL.setCrs(pCrs)
		pr = mL.dataProvider()
		for fld in fields:
			pr.addAttributes([fld])
		mL.updateFields()
		f = cfg.utls.getFeaturebyID(targetLayer, idList[0])
		sg = QgsGeometry(f.geometry())
		for i in idList:
			if i != idList[0]:
				f = cfg.utls.getFeaturebyID(targetLayer, i)
				g = QgsGeometry(f.geometry())
				g.convertToMultiType()
				sg.addPartGeometry(g)
		mL.startEditing()		
		f.setGeometry(sg)
		f.setAttributes(attributeList)
		pr.addFeatures([f])
		mL.commitChanges()
		mL.updateExtents()
		return mL

### Delete a field from a shapefile by its name
	def deleteFieldShapefile(self, layerPath, fieldName):
		fds = self.fieldsShapefile(layerPath)
		s = cfg.ogrSCP.Open(layerPath, 1)
		l = s.GetLayer()
		i = fds.index(fieldName)
		l.DeleteField(i)
		s = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "deleted field: " + unicode(fieldName) + " for layer: " + unicode(l.name()))
				
### Find field ID by name
	def fieldID(self, layer, fieldName):
		try:
			fID = layer.fieldNameIndex(fieldName)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "ID: " + str(fID) + " for layer: " + unicode(layer.name()))
			return fID
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				
### Get field names of a shapefile
	def fieldsShapefile(self, layerPath):
		s = cfg.ogrSCP.Open(layerPath)
		l = s.GetLayer()
		lD = l.GetLayerDefn()
		fN = [lD.GetFieldDefn(i).GetName() for i in range(lD.GetFieldCount())]
		s = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "shapefile field " + unicode(layerPath))
		return fN
				
	# get field attribute list
	def getFieldAttributeList(self, layer, field):
		fID = self.fieldID(layer, field)
		f = QgsFeature()
		l = []
		for f in layer.getFeatures():
			a = f.attributes()[fID]
			l.append(a)
		x = list(set(l))
		return x
		
	# reproject shapefile
	def repojectShapefile(self, inputShapefilePath, inputEPSG, outputShapefilePath, outputEPSG):
		iD = cfg.ogrSCP.GetDriverByName('ESRI Shapefile')
		# spatial reference
		iSR = cfg.osrSCP.SpatialReference()
		iSR.ImportFromEPSG(inputEPSG)
		oSR = cfg.osrSCP.SpatialReference()
		oSR.ImportFromEPSG(outputEPSG)
		# Coordinate Transformation
		cT = cfg.osrSCP.CoordinateTransformation(iSR, oSR)
		# input shapefile
		iS = iD.Open(inputShapefilePath)
		iL = iS.GetLayer()
		# output shapefile
		oS = iD.CreateDataSource(outputShapefilePath)
		nm = cfg.osSCP.path.basename(outputShapefilePath)
		oL = oS.CreateLayer(str(nm), oSR, cfg.ogrSCP.wkbMultiPolygon)
		iLDefn = iL.GetLayerDefn()
		# fields
		for i in range(0, iLDefn.GetFieldCount()):
			fDefn = iLDefn.GetFieldDefn(i)
			oL.CreateField(fDefn)
		oLDefn = oL.GetLayerDefn()
		oLFcount = oLDefn.GetFieldCount()
		iF = iL.GetNextFeature()
		while iF:
			g = iF.GetGeometryRef()
			g.Transform(cT)
			oF = cfg.ogrSCP.Feature(oLDefn)
			oF.SetGeometry(g)
			for i in range(0, oLFcount):
				nmRef = oLDefn.GetFieldDefn(i).GetNameRef()
				field = iF.GetField(i)
				oF.SetField(nmRef, field)
			oL.CreateFeature(oF)
			oF.Destroy()
			iF.Destroy()
			iF = iL.GetNextFeature()
		iS.Destroy()
		oS.Destroy()
		
##################################
	""" raster color composite functions """
##################################

	# get items in combobox
	def getAllItemsInCombobox(self, combobox):
		it = [combobox.itemText(i) for i in range(combobox.count())]
		return it
		
	# set RGB Combobox
	def setComboboxItems(self, combobox, itemList):
		combobox.clear()
		for i in itemList:
			if len(i) > 0:
				combobox.addItem(i)
				
	# set RGB color composite
	def setRGBColorComposite(self):
		if cfg.rgb_combo.currentText() != "-":
			try:
				rgb = cfg.rgb_combo.currentText()
				check = self.createRGBColorComposite(rgb)
				if check == "Yes":
					listA = cfg.utls.getAllItemsInCombobox(cfg.rgb_combo)
					cfg.RGBList = listA
					cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
					cfg.RGBLT.RGBListTable(cfg.RGBList)
					return "Yes"
				else:
					int(check)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
	
	# create RGB color composite
	def createRGBColorComposite(self, colorComposite):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			# if bandset create temporary virtual raster
			tPMN = cfg.tmpVrtNm + ".vrt"
			if cfg.tmpVrt is None:
				try:
					self.removeLayer(tPMN)
				except:
					pass
				# date time for temp name
				dT = cfg.utls.getTime()
				tPMD = cfg.tmpDir + "/" + dT + tPMN
				vrtCheck = cfg.utls.createVirtualRaster(cfg.bndSetLst, tPMD)
				cfg.timeSCP.sleep(1)
				i = self.addRasterLayer(tPMD, tPMN)
				cfg.utls.setRasterColorComposite(i, 3, 2, 1)
				cfg.tmpVrt = i
			else:
				i = cfg.utls.selectLayerbyName(tPMN, "Yes")
			c = str(colorComposite).split(",")
			if len(c) == 1:
				c = str(colorComposite).split("-")
			if len(c) == 1:
				c = str(colorComposite).split(";")
			if len(c) == 1:
				c = str(colorComposite)
			if i is not None:
				b = len(cfg.bndSet)
				if int(c[0]) <= b and int(c[1]) <= b and int(c[2]) <= b:
					cfg.utls.setRasterColorComposite(i, int(c[0]), int(c[1]), int(c[2]))
					return "Yes"
				else:
					return "No"
			else:
				cfg.tmpVrt = None
		else:
			c = str(colorComposite).split(",")
			if len(c) == 1:
				c = str(colorComposite).split("-")
			if len(c) == 1:
				c = str(colorComposite).split(";")
			if len(c) == 1:
				c = str(colorComposite)
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
			if i is not None:
				b = len(cfg.bndSet)
				if int(c[0]) <= b and int(c[1]) <= b and int(c[2]) <= b:
					self.setRasterColorComposite(i, int(c[0]), int(c[1]), int(c[2]))
					return "Yes"
				else:
					return "No"
					
	# set raster color composite
	def setRasterColorComposite(self, raster, RedBandNumber, GreenBandNumber, BlueBandNumber):
		raster.setDrawingStyle('MultiBandColor')
		raster.renderer().setRedBand(RedBandNumber)
		raster.renderer().setGreenBand(GreenBandNumber)
		raster.renderer().setBlueBand(BlueBandNumber)
		cfg.utls.setRasterContrastEnhancement(raster, cfg.defaultContrast )
		
	# set local cumulative cut stretch
	def setRasterCumulativeStretch(self):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			i = cfg.tmpVrt
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
		cfg.utls.setRasterContrastEnhancement(i, cfg.cumulativeCutContrast)
		cfg.defaultContrast = cfg.cumulativeCutContrast
				
	# set local standard deviation stretch
	def setRasterStdDevStretch(self):
		if cfg.bndSetPresent == "Yes" and cfg.rstrNm == cfg.bndSetNm:
			i = cfg.tmpVrt
		else:
			i = cfg.utls.selectLayerbyName(cfg.rstrNm, "Yes")
		cfg.utls.setRasterContrastEnhancement(i, cfg.stdDevContrast)
		cfg.defaultContrast = cfg.stdDevContrast
		
	# set raster enhancement
	def setRasterContrastEnhancement(self, QGISraster, contrastType = cfg.cumulativeCutContrast):
		ext = cfg.cnvs.extent( )
		tLPoint = QgsPoint(ext.xMinimum(), ext.yMaximum())
		lRPoint = QgsPoint(ext.xMaximum(), ext.yMinimum())
		point1 = tLPoint
		point2 = lRPoint
		# project extent
		iCrs = cfg.utls.getCrs(QGISraster)
		pCrs = cfg.utls.getQGISCrs()
		if iCrs is None:
			iCrs = pCrs
		# projection of input point from project's crs to raster's crs
		if pCrs != iCrs:
			try:
				point1 = cfg.utls.projectPointCoordinates(tLPoint, pCrs, iCrs)
				point2 = cfg.utls.projectPointCoordinates(lRPoint, pCrs, iCrs)
				if point1 is False:
					point1 = tLPoint
					point2 = lRPoint
			# Error latitude or longitude exceeded limits
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				point1 = tLPoint
				point2 = lRPoint
		if contrastType == cfg.stdDevContrast:
			contrast = QgsRaster.ContrastEnhancementStdDev
		elif contrastType == cfg.cumulativeCutContrast:
			contrast = QgsRaster.ContrastEnhancementCumulativeCut
		try:
			QGISraster.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, contrast, QgsRectangle(point1, point2))
			QGISraster.triggerRepaint()
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))

##################################
	""" table functions """
##################################
		
	# delete all items in a table
	def clearTable(self, table):
		table.clearContents()
		for i in range(0, table.rowCount()):
			table.removeRow(0)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		
	# set all items to state 0 or 2
	def allItemsSetState(self, tableWidget, value):
		tW = tableWidget
		tW.blockSignals(True)
		r = tW.rowCount()
		for b in range(0, r):
			if cfg.actionCheck == "Yes":
				tW.item(b, 0).setCheckState(value)
				#cfg.uiUtls.updateBar((b+1) * 100 / r)
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " cancelled")
				tW.blockSignals(False)
		tW.blockSignals(False)
				
	# highlight row in table
	def highlightRowInTable(self, table, value, columnIndex):
		tW = table
		v = tW.rowCount()
		for x in range(0, v):
			id = tW.item(x, columnIndex).text()
			if str(id) == str(value):
				return x
			
	# remove rows from table
	def removeRowsFromTable(self, table):
		# ask for confirm
		a = cfg.utls.questionBox("Remove rows", "Are you sure you want to remove highlighted rows from the table?")
		if a == "Yes":
			tW = table
			c = tW.rowCount()
			# list of item to remove
			iR  = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			v = list(set(iR))
			# remove items
			for i in reversed(range(0, len(v))):
				tW.removeRow(v[i])
			c = tW.rowCount()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " row removed")
			
	# select rows in table
	def selectRowsInTable(self, table, rowList):
		c = table.columnCount()
		for row in rowList:
			table.setRangeSelected(cfg.QtGuiSCP.QTableWidgetSelectionRange(row, 0, row, c-1), True)
		
	# add item to table
	def addTableItem(self, table, item, row, column, enabled = "Yes", color = None, checkboxState = None, tooltip = None):
		itMID = cfg.QtGuiSCP.QTableWidgetItem()
		if checkboxState != None:
			itMID.setCheckState(checkboxState)
		if enabled == "No":
			itMID.setFlags(cfg.QtSCP.ItemIsEnabled)
		itMID.setData(cfg.QtSCP.DisplayRole, item)
		table.setItem(row, column, itMID)
		if color is not None:
			table.item(row, column).setBackground(color)
		if tooltip is not None:
			itMID.setToolTip(tooltip)
		
	# set table item
	def setTableItem(self, table, row, column, value):
		table.item(row, column).setText(value)
							
	# insert table row
	def insertTableRow(self, table, row, height = None):
		table.insertRow(row)
		if height is not None:
			table.setRowHeight(row, height)
		
	# insert table column
	def insertTableColumn(self, table, column, name, width = None, hide = "No"):
		table.insertColumn(column)
		table.setHorizontalHeaderItem(column, cfg.QtGuiSCP.QTableWidgetItem(name))
		if width is not None:
			table.setColumnWidth(column, width)
		if hide == "Yes":
			table.hideColumn(column)
	
	# sort table column
	def sortTableColumn(self, table, column, ascending = False):
		table.sortItems(column, ascending)
		
	# set table column width
	def setColumnWidthList(self, table, list):
		for c in list:
			table.setColumnWidth(c[0], c[1])
	
##################################
	""" tab selection functions """
##################################

### tab 0
	# select band set tab
	def selectTabDownloadImages(self, secondTab = None):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(0)
		if secondTab is not None:
			cfg.ui.tab_download.setCurrentIndex(secondTab)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select pre processing tab
	def downloadImagesTab(self):
		cfg.utls.selectTabDownloadImages()
		
	# download Landsat tab
	def downloadLandast8Tab(self):
		cfg.utls.selectTabDownloadImages(0)
		
	# download Sentinel tab
	def downloadSentinelTab(self):
		cfg.utls.selectTabDownloadImages(1)

	# download ASTER tab
	def downloadASTERTab(self):
		cfg.utls.selectTabDownloadImages(2)

### tab 1
	# select tab 0 from Main Interface
	def selectTab0MainInterface(self, secondTab = None):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(1)
		if secondTab is not None:
			cfg.ui.tabWidget.setCurrentIndex(secondTab)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select roi tools tab
	def roiToolsTab(self):
		cfg.utls.selectTab0MainInterface()

	# select multiple roi tab
	def mutlipleROITab(self):
		cfg.utls.selectTab0MainInterface(0)
		
	# import library signatures tab
	def importLibraryTab(self):
		cfg.utls.selectTab0MainInterface(1)
				
	# export library signatures tab
	def exportLibraryTab(self):
		cfg.utls.selectTab0MainInterface(2)
		
	# algorithm weight tab
	def algorithmWeighTab(self):
		cfg.utls.selectTab0MainInterface(3)
		
	# signature threshold tab
	def algorithmThresholdTab(self):
		cfg.utls.selectTab0MainInterface(4)

	# LCS threshold tab
	def LCSThresholdTab(self):
		cfg.utls.selectTab0MainInterface(5)
		
	# RGB List tab
	def RGBListTab(self):
		cfg.utls.selectTab0MainInterface(6)
		
### tab 2
	# select tab 2 from Main Interface
	def selectTab1MainInterface(self, secondTab = None):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(2)
		if secondTab is not None:
			cfg.ui.tabWidget_preprocessing.setCurrentIndex(secondTab)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select pre processing tab
	def preProcessingTab(self):
		cfg.utls.selectTab1MainInterface()

	# select Landsat tab
	def landsatTab(self):
		cfg.utls.selectTab1MainInterface(0)
		
	# select Sentinel-2 tab
	def sentinel2Tab(self):
		cfg.utls.selectTab1MainInterface(1)
		
	# select ASTER tab
	def asterTab(self):
		cfg.utls.selectTab1MainInterface(2)
		
	# select Clip multiple rasters tab
	def clipMultipleRastersTab(self):
		cfg.utls.selectTab1MainInterface(3)
	
	# select Split raster bands tab
	def splitrasterbandsTab(self):
		cfg.utls.selectTab1MainInterface(4)
		
	# PCA tab
	def PCATab(self):
		cfg.utls.selectTab1MainInterface(5)
			
	# Vector to raster tab
	def vectorToRasterTab(self):
		cfg.utls.selectTab1MainInterface(6)
		
### tab 3
	# select tab 3 from Main Interface
	def selectTab2MainInterface(self, secondTab = None):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(3)
		if secondTab is not None:
			cfg.ui.tabWidget_2.setCurrentIndex(secondTab)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select post processing tab
	def postProcessingTab(self):
		cfg.utls.selectTab2MainInterface()
		
	# select Accuracy tab
	def accuracyTab(self):
		cfg.utls.selectTab2MainInterface(0)
		
	# select Land cover change tab
	def landCoverChangeTab(self):
		cfg.utls.selectTab2MainInterface(1)
		
	# select Classification report tab
	def classificationReportTab(self):
		cfg.utls.selectTab2MainInterface(2)
		
	# select Classification report tab
	def classToVectorTab(self):
		cfg.utls.selectTab2MainInterface(3)
	
	# select Reclassification tab
	def reclassificationTab(self):
		cfg.utls.selectTab2MainInterface(4)
			
	# select Edit raster tab
	def editRasterTab(self):
		cfg.utls.selectTab2MainInterface(5)
		
	# select Classification sieve tab
	def classificationSieveTab(self):
		cfg.utls.selectTab2MainInterface(6)		
		
	# select Classification erosion tab
	def classificationErosionTab(self):
		cfg.utls.selectTab2MainInterface(7)
		
	# select Classification dilation tab
	def classificationDilationTab(self):
		cfg.utls.selectTab2MainInterface(8)
		
### tab 4
	# select Band calc tab
	def bandCalcTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(4)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
	
### tab 5
	# select band set tab
	def bandSetTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(5)
		# reload raster bands in checklist
		cfg.bst.rasterBandName()
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
	
### tab 6
	# select tab 6 from Main Interface
	def selectTabBatch(self, secondTab = None):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(6)
		if secondTab is not None:
			cfg.ui.toolBox.setCurrentIndex(secondTab)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select batch tab
	def batchTab(self):
		cfg.utls.selectTabBatch()
		
### tab 7
	# select tab 7 from Main Interface
	def selectTabSettings(self, secondTab = None):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(7)
		if secondTab is not None:
			cfg.ui.toolBox.setCurrentIndex(secondTab)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# select settings tab
	def settingsTab(self):
		cfg.utls.selectTabSettings()
		
	# select settings interface tab
	def settingsInterfaceTab(self):
		cfg.utls.selectTabSettings(0)
		
	# select settings Processing tab
	def settingsProcessingTab(self):
		cfg.utls.selectTabSettings(1)
		
	# select settings debug tab
	def settingsDebugTab(self):
		cfg.utls.selectTabSettings(2)

### tab 8
	# select bout tab
	def aboutTab(self):
		cfg.dlg.close()
		cfg.ui.toolButton_plugin.setCurrentIndex(8)
		# show the dialog
		cfg.dlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# spectral singature plot tab
	def spectralPlotTab(self):
		cfg.spectralplotdlg.close()
		cfg.spectralplotdlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")

	# select tab in singature plot tab
	def selectSpectralPlotTabSettings(self, secondTab = None):
		if secondTab is not None:
			cfg.uisp.toolBox.setCurrentIndex(secondTab)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
	# scatter plot tab
	def scatterPlotTab(self):
		cfg.scatterplotdlg.close()
		cfg.scatterplotdlg.show()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "tab selected")
		
##################################
	""" sound functions """
##################################

	# beep sound
	def beepSound(self, frequency, duration):
		if cfg.sysSCP.platform.startswith('win'):
			winsound.Beep(frequency, int(duration * 1000))
		elif cfg.sysSCP.platform.startswith('linux'):
			cfg.osSCP.system("play --no-show-progress --null --channels 1 synth " + str(duration) + " sine " + str(frequency))
		else:
			cfg.sysSCP.stdout.write('\a')
			cfg.sysSCP.stdout.flush()
	
	# finish sound
	def finishSound(self):
		try:
			self.beepSound(800, 0.2)
			self.beepSound(600, 0.3)
			self.beepSound(700, 0.5)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		
##################################
	""" clean functions """
##################################

	# clean old temporary directory
	def cleanOldTempDirectory(self):
		t = cfg.datetimeSCP.datetime.now()
		inputDir = unicode(cfg.QDirSCP.tempPath() + "/" + cfg.tempDirName)
		try:
			for name in cfg.osSCP.listdir(inputDir):
				dStr = cfg.datetimeSCP.datetime.strptime(name, "%Y%m%d_%H%M%S%f")
				diff = (t - dStr)
				if diff.days > 3:
					cfg.shutilSCP.rmtree(inputDir + "/" + name, True)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			
##################################
	""" general functions """
##################################
		
	# 32bit or 64bit
	def findSystemSpecs(self):
		if cfg.sysSCP.maxsize > 2**32:
			cfg.sysSCP64bit = "Yes"
		else:
			cfg.sysSCP64bit = "No"
		# file system encoding
		cfg.fSEnc = cfg.sysSCP.getfilesystemencoding()
		# system information
		cfg.sysSCPNm = cfg.platformSCP.system()
		# QGIS version
		cfg.QGISVer = cfg.qgisCoreSCP.QGis.QGIS_VERSION_INT
			
	# read variables from project instance
	def readVariables(self):
		# read qml path from project instance	
		cfg.qmlFl = cfg.utls.readProjectVariable("qmlfile", "")
		# set qml line content
		cfg.uidc.qml_lineEdit.setText(cfg.qmlFl)
		# read signature checkbox from project instance
		cfg.sigClcCheck = cfg.utls.readProjectVariable("calculateSignature", "Yes")
		# read rapid ROI checkbox from project instance
		cfg.rpdROICheck = cfg.utls.readProjectVariable("rapidROI", "No")
		cfg.vegIndexCheck = cfg.utls.readProjectVariable("vegetationIndex", "Yes")
		cfg.ROIband = cfg.utls.readProjectVariable("rapidROIBand", str(cfg.ROIband))
		cfg.algName = cfg.utls.readProjectVariable("ClassAlgorithm", unicode(cfg.algName))
		cfg.prvwSz = cfg.utls.readProjectVariable("previewSize", str(cfg.prvwSz))
		cfg.minROISz = cfg.utls.readProjectVariable("minROISize", str(cfg.minROISz))
		cfg.maxROIWdth = cfg.utls.readProjectVariable("maxROIWidth", str(cfg.maxROIWdth))
		cfg.rngRad = cfg.utls.readProjectVariable("rangeRadius", str(cfg.rngRad))
		cfg.ROIID = cfg.utls.readProjectVariable("ROIIDField", str(cfg.ROIID))
		cfg.ROIInfo = cfg.utls.readProjectVariable("ROIInfoField", str(cfg.ROIInfo))
		cfg.ROIMacroClassInfo = cfg.utls.readProjectVariable("ROIMacroclassInfoField", str(cfg.ROIMacroClassInfo))
		cfg.customExpression = cfg.utls.readProjectVariable("customExpression", str(cfg.customExpression))
		cfg.ROIMacroID = cfg.utls.readProjectVariable("ROIMacroIDField", str(cfg.ROIMacroID))
		# mask option
		cfg.mskFlPath = cfg.utls.readProjectVariable("maskFilePath", unicode(cfg.mskFlPath))
		cfg.mskFlState = cfg.utls.readProjectVariable("maskFileState", str(cfg.mskFlState))
		cfg.uidc.mask_lineEdit.setText(unicode(cfg.mskFlPath))
		cfg.classD.setMaskCheckbox()
		# band set
		bSP = cfg.utls.readProjectVariable("bandSet", "")
		bSW = cfg.utls.readProjectVariable("bndSetWvLn", "")
		bSM = cfg.utls.readProjectVariable("bndSetMultF", "")
		bSA = cfg.utls.readProjectVariable("bndSetAddF", "")
		un = cfg.utls.readProjectVariable("bndSetUnit", cfg.noUnit)
		bSU = cfg.bst.unitNameConversion(un, "Yes")
		cfg.bndSetPresent = cfg.utls.readProjectVariable("bandSetPresent", "No")
		if cfg.bndSetPresent == "Yes":
			# add band set to table
			bs = eval(bSP)
			wlg = eval(bSW)
			try:
				multF = eval(bSM)
				addF = eval(bSA)
			except:
				pass
			t = cfg.ui.tableWidget
			it = 0
			cfg.BandTabEdited = "No"
			t.blockSignals(True)
			for x in sorted(wlg):
				b = wlg.index(x)
				# add item to table
				c = t.rowCount()
				# name of item of list
				iN = bs[it]
				# add list items to table
				t.setRowCount(c + 1)
				cfg.utls.addTableItem(t, iN, c, 0)
				cfg.utls.addTableItem(t, str(wlg[b]), c, 1)
				try:
					cfg.utls.addTableItem(t, str(multF[it]), c, 2)
				except:
					cfg.utls.addTableItem(t, "1", c, 2)
				try:
					cfg.utls.addTableItem(t, str(addF[it]), c, 3)
				except:
					cfg.utls.addTableItem(t, "0", c, 3)
				it = it + 1
			# load project unit in combo
			idU = cfg.ui.unit_combo.findText(bSU)
			cfg.ui.unit_combo.setCurrentIndex(idU)
			t.blockSignals(False)
			cfg.bst.readBandSet("Yes")
			cfg.BandTabEdited = "Yes"
		# read RGB list
		rgbList = cfg.utls.readProjectVariable("SCP_RGBList", str(cfg.RGBList))
		cfg.RGBList = eval(rgbList)
		try:
			cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
		except:
			pass
			
	# get temporary directory
	def getTempDirectory(self):
		# temp directory
		if cfg.tmpDir is None:
			tmpDir0 = unicode(cfg.QDirSCP.tempPath() + "/" + cfg.tempDirName)
		else:
			tmpDir0 = cfg.tmpDir
		if not cfg.QDirSCP(tmpDir0).exists():
			try:
				cfg.osSCP.makedirs(tmpDir0)
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.sets.setQGISRegSetting(cfg.regTmpDir, tmpDir0)
				cfg.mx.msgWar17()
				if not cfg.QDirSCP(tmpDir0).exists():
					cfg.osSCP.makedirs(tmpDir0)
		try:
			dT = cfg.utls.getTime()
			cfg.osSCP.makedirs(tmpDir0 + "/" + dT)
			cfg.tmpDir = unicode(tmpDir0 + "/" + dT)
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgWar17()
			if not cfg.QDirSCP(cfg.tmpDir).exists():
				cfg.osSCP.makedirs(cfg.tmpDir)
		return tmpDir0
