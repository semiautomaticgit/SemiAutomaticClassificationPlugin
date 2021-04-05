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
# sound for Windows
try:
	import winsound
except:
	pass
	
class Utils:
	def __init__(self):
		pass

##################################
	''' Download functions '''
##################################

	# download html file
	def downloadHtmlFileQGIS(self, url,  url2 = None, timeOutSec = 1):
		cfg.htmlW = url2
		r = cfg.QNetworkRequestSCP(cfg.QtCoreSCP.QUrl(url))
		cfg.reply = cfg.qgisCoreSCP.QgsNetworkAccessManager.instance().get(r)
		cfg.reply.finished.connect(self.replyInTextBrowser)
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		return 'No'
	
	# load reply in text browser
	def replyInTextBrowser(self):
		cfg.reply.deleteLater()
		html2 = cfg.reply.readAll().data()		
		html = bytes.decode(html2)
		# Github file not found
		if '<h1>404</h1>' in html:
			r = cfg.QNetworkRequestSCP(cfg.QtCoreSCP.QUrl(cfg.htmlW))
			cfg.reply2 = cfg.qgisCoreSCP.QgsNetworkAccessManager.instance().get(r)
			cfg.reply2.finished.connect(self.replyInTextBrowser2)
		if len(html) > 0:
			cfg.uidc.main_textBrowser.clear()
			cfg.uidc.main_textBrowser.setHtml(html)
		cfg.reply.finished.disconnect()
		cfg.reply.abort()
		cfg.reply.close()
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		
	# load reply in text browser
	def replyInTextBrowser2(self):
		cfg.reply2.deleteLater()
		html2 = cfg.reply2.readAll().data()		
		html = bytes.decode(html2)
		if len(html) > 0:
			cfg.uidc.main_textBrowser.clear()
			cfg.uidc.main_textBrowser.setHtml(html)
		cfg.reply2.finished.disconnect()
		cfg.reply2.abort()
		cfg.reply2.close()
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
			
	# reply Finish
	def replyFinish(self):
		cfg.replyP.deleteLater()
		cfg.fileP = cfg.replyP.readAll()
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
				
	# replyText
	def replyText(self):
		cfg.replyP.deleteLater()
		cfg.htmlP = cfg.replyP.readAll()
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
			
	# progress
	def downloadProgress(self, value, total):
		cfg.uiUtls.updateBar(self.progressP, '(' + str(value/1048576) + '/' + str(total/1048576) + ' MB) ' + self.urlP, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'))
		if cfg.actionCheck == 'No':
			cfg.replyP.finished.disconnect()
			cfg.replyP.abort()
			cfg.replyP.close()
							
	# reply redirect
	def replyRedirect(self):
		cfg.replyR.deleteLater()
		rA = cfg.replyR.attribute(cfg.QNetworkRequestSCP.RedirectionTargetAttribute)
		if rA is not None:
			cfg.replyRURL = rA.toString()
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
						
	# reply redirect
	def replyRedirect2(self):
		cfg.replyR2.deleteLater()
		rA = cfg.replyR2.attribute(cfg.QNetworkRequestSCP.RedirectionTargetAttribute)
		if rA is not None:
			cfg.replyRURL2 = rA.toString()
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
			
	# reply redirect
	def replyRedirect3(self):
		cfg.replyR3.deleteLater()
		rA = cfg.replyR3.attribute(cfg.QNetworkRequestSCP.RedirectionTargetAttribute)
		if rA is not None:
			cfg.replyRURL3 = rA.toString()
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())

	# connect with password QT
	def passwordConnect(self, user, password, url, topLevelUrl, outputPath = None, progress = None, quiet = 'No', redirect = 'No'):
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ' + url)
		# auth
		base64UP = cfg.base64SCP.encodestring(bytes(user + ':' + password, 'utf-8')[:-1])
		h = bytes('Basic ', 'utf-8') + base64UP
		hKey = cfg.QtCoreSCP.QByteArray(bytes('Authorization', 'utf-8') )
		hValue = cfg.QtCoreSCP.QByteArray(h)
		r = cfg.QNetworkRequestSCP(cfg.QtCoreSCP.QUrl(url))
		r.setRawHeader(hKey, hValue)		
		qnamI = cfg.qgisCoreSCP.QgsNetworkAccessManager.instance()
		if redirect != 'No':
			cfg.replyR = qnamI.get(r)
			cfg.replyR.finished.connect(self.replyRedirect)
			# loop
			eL = cfg.QtCoreSCP.QEventLoop()
			cfg.replyR.finished.connect(eL.quit)
			eL.exec_()
			cfg.replyR.finished.disconnect(eL.quit)
			cfg.replyR.finished.disconnect()
			cfg.replyR.abort()
			cfg.replyR.close()
			r2 = cfg.QNetworkRequestSCP(cfg.QtCoreSCP.QUrl(cfg.replyRURL))
			r2.setRawHeader(hKey, hValue)
			cfg.replyR2 = qnamI.get(r2)
			cfg.replyR2.finished.connect(self.replyRedirect2)
			# loop
			eL = cfg.QtCoreSCP.QEventLoop()
			cfg.replyR2.finished.connect(eL.quit)
			eL.exec_()
			cfg.replyR2.finished.disconnect(eL.quit)
			cfg.replyR2.finished.disconnect()
			cfg.replyR2.abort()
			cfg.replyR2.close()
			r3 = cfg.QNetworkRequestSCP(cfg.QtCoreSCP.QUrl(cfg.replyRURL2))
			r3.setRawHeader(hKey, hValue)
			cfg.replyR3 = qnamI.get(r3)
			cfg.replyR3.finished.connect(self.replyRedirect3)
			# loop
			eL = cfg.QtCoreSCP.QEventLoop()
			cfg.replyR3.finished.connect(eL.quit)
			eL.exec_()
			cfg.replyR3.finished.disconnect(eL.quit)
			cfg.replyR3.finished.disconnect()
			cfg.replyR3.abort()
			cfg.replyR3.close()
		try:
			if outputPath is None:
				cfg.replyP = qnamI.get(r)
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
				cfg.replyP = qnamI.get(r)
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
				with open(outputPath, 'wb') as file:
					file.write(cfg.fileP)
				if cfg.actionCheck == 'No':
					raise ValueError('Cancel action')
				if cfg.osSCP.path.getsize(outputPath) > 500:
					cfg.fileP = None
					return 'Yes'
				else:
					if 'problem' in cfg.fileP:
						cfg.fileP = None
						return 'No'
					else:
						cfg.fileP = None
						return 'Yes'
		except Exception as err:
			if str(err) != 'Cancel action':
				if quiet == 'No':
					if 'ssl' in str(err):
						cfg.mx.msgErr56()
					else:
						cfg.mx.msgErr50(str(err))
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
			
	# get password opener
	def getPasswordHandler(self, user, password, topLevelUrl):
		pswMng = cfg.urllibSCP.request.HTTPPasswordMgrWithDefaultRealm()
		pswMng.add_password(None, topLevelUrl, user, password)
		passwordHandler = cfg.urllibSCP.request.HTTPBasicAuthHandler(pswMng)
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		return passwordHandler
		
	# connect with password Python
	def passwordConnectPython(self, user, password, url, topLevelUrl, outputPath = None, progress = None, quiet = 'No'):
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ' + url)
		proxyHandler = cfg.utls.getProxyHandler()
		passwordHandler = cfg.utls.getPasswordHandler(user, password, topLevelUrl)
		cookieHandler = cfg.urllibSCP.request.HTTPCookieProcessor()
		if proxyHandler is None:
			if len(user) > 0:
				opener = cfg.urllibSCP.request.build_opener(cookieHandler, passwordHandler)
			else:
				opener = cfg.urllibSCP.request.build_opener(cookieHandler)
		else:
			if len(user) > 0:
				opener = cfg.urllibSCP.request.build_opener(proxyHandler, cookieHandler, passwordHandler)
			else:
				opener = cfg.urllibSCP.request.build_opener(proxyHandler, cookieHandler)
		cfg.urllibSCP.request.install_opener(opener)
		try:
			if outputPath is None:
				response = opener.open(url)
				return response
			else:
				f = cfg.urllibSCP.request.urlopen(url)
				total_size = int(f.headers['Content-Length'])
				MB_size = round(total_size/1048576, 2)
				block_size = 1024 * 1024
				ratio = 0
				tune = 'Yes'
				with open(outputPath, 'wb') as file:
					while True:
						if tune == 'Yes':
							start = cfg.datetimeSCP.datetime.now()
						block = f.read(block_size)
						dSize =  round(int(cfg.osSCP.stat(outputPath).st_size)/1048576, 2)
						cfg.uiUtls.updateBar(progress, '(' + str(dSize) + '/' + str(MB_size) + ' MB) ' +  url, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'))
						cfg.QtWidgetsSCP.qApp.processEvents()
						if not block:
							break
						file.write(block)
						if tune == 'Yes':
							end = cfg.datetimeSCP.datetime.now()
							delta =  end - start
							newRatio = block_size / delta.microseconds
							if newRatio > ratio:
								block_size = block_size + 1024 * 1024
							elif newRatio < ratio:
								block_size = block_size - 1024 * 1024
								tune = 'No'
							ratio = newRatio
						if cfg.actionCheck == 'No':
							raise ValueError('Cancel action')
				return 'Yes'
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			if str(err) != 'Cancel action':
				if quiet == 'No':
					if 'ssl' in str(err):
						cfg.mx.msgErr56()
					elif 'Navigation failed' in str(err) or 'Internal Server Error' in str(err):
						return 'Internal Server Error'
					else:
						cfg.mx.msgErr50(str(err))
			return 'No'
		
	# get proxy opener
	def getProxyHandler(self):
		cfg.utls.getQGISProxySettings()
		if str(cfg.proxyEnabled) == 'true' and len(cfg.proxyHost) > 0:
			if len(cfg.proxyUser) > 0:
				proxyHandler = cfg.urllibSCP.ProxyHandler({'http': 'http://'+ cfg.proxyUser + ':' + cfg.proxyPassword  + '@' + cfg.proxyHost + ':' + cfg.proxyPort})
			else:
				proxyHandler = cfg.urllibSCP.ProxyHandler({'http': 'http://' + cfg.proxyHost + ':' + cfg.proxyPort})
		else:
			proxyHandler = None
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		return proxyHandler
	
	# connect to USGS
	def generalOpener(self):
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		proxyHandler = cfg.utls.getProxyHandler()
		cfg.cookieJ = cfg.CookieJarSCP()
		if proxyHandler is None:
			cfg.openerGeneral = cfg.urllibSCP.request.build_opener(cfg.urllibSCP.request.HTTPCookieProcessor(cfg.cookieJ))
		else:
			cfg.openerGeneral = cfg.urllibSCP.request.build_opener(proxyHandler, cfg.urllibSCP.request.HTTPCookieProcessor(cfg.cookieJ))
		
	# NASA search
	def NASASearch(self, url):
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' url:' + str(url))
		cfg.utls.generalOpener()
		request1 = cfg.urllibSCP.request.Request(url)
		try:
			response1 = cfg.openerGeneral.open(request1)
		except Exception as err:
			cfg.urllibSCP.request.install_opener(cfg.openerGeneral)
			# certificate error
			newContext = cfg.sslSCP.SSLContext(cfg.sslSCP.PROTOCOL_TLSv1_2) 
			response1 = cfg.urllibSCP.request.urlopen(request1, context=newContext)		
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		return response1
		
	# download file
	def downloadFile(self, url, outputPath, fileName = None, progress = None):
		try:
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' url:' + str(url))
			proxyHandler = cfg.utls.getProxyHandler()
			if proxyHandler is not None:
				opener = cfg.urllibSCP.request.build_opener(proxyHandler)
				cfg.urllibSCP.request.install_opener(opener)
			else:
				opener = cfg.urllibSCP.request.build_opener()
			f = cfg.urllibSCP.request.urlopen(url)
			try:
				total_size = int(f.headers['Content-Length'])
				MB_size = round(total_size/1048576, 2)
			except:
				total_size = 1
			block_size = 1024 * 1024
			ratio = 0
			tune = 'Yes'
			if block_size >= total_size:
				response = f.read()
				l = open(outputPath, 'wb')
				l.write(response)
				l.close()
			else:
				with open(outputPath, 'wb') as file:
					while True:
						if tune == 'Yes':
							start = cfg.datetimeSCP.datetime.now()
						block = f.read(block_size)
						dSize =  round(int(cfg.osSCP.stat(outputPath).st_size)/1048576, 2)
						cfg.uiUtls.updateBar(progress, '(' + str(dSize) + '/' + str(MB_size) + ' MB) ' +  url, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'))
						cfg.QtWidgetsSCP.qApp.processEvents()
						if not block:
							break
						file.write(block)
						if tune == 'Yes':
							end = cfg.datetimeSCP.datetime.now()
							delta =  end - start
							newRatio = block_size / delta.microseconds
							if newRatio > ratio:
								block_size = block_size + 1024 * 1024
							elif newRatio < ratio:
								block_size = block_size - 1024 * 1024
								tune = 'No'
							ratio = newRatio
						if cfg.actionCheck == 'No':
							raise ValueError('Cancel action')
			return 'Yes'
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err) + ' url:' + str(url))
			return err
		
	# connect with password
	def USGSLogin(self, user, password, topLevelUrl):
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		if len(user) > 0:
			cfg.utls.generalOpener()
			request1 = cfg.urllibSCP.request.Request(topLevelUrl)
			response1 = cfg.openerGeneral.open(request1)
			html1 = response1.read()
			# required token
			tok = cfg.reSCP.findall('<input type="hidden" name="csrf_token" value="(.+?)" id="csrf_token" />', str(html1))
			tid = tok[0].replace('"', '').replace(' ', '')
			# login
			params = cfg.urllibSCP.parse.urlencode({'username': user, 'password': password, 'csrf_token': tid})
			params2 = params.encode()
			request2 = cfg.urllibSCP.request.Request('https://ers.cr.usgs.gov/login', params2)
			response2 = cfg.openerGeneral.open(request2)
			for cookie in cfg.cookieJ:
				if cookie.name == "EROS_SSO_production":
					cookievalue = cookie.value
			try:
				cfg.openerGeneral.addheaders = [('Cookie', 'EROS_SSO_production=' + cookievalue)]
				return cookievalue
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				raise ValueError('Login error')
			
	# download file
	def downloadFileUSGS(self, user, password, topLevelUrl, url, outputPath, fileName = None, progress = None, quiet = 'No'):
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' url:' + str(url))
		cookievalue = cfg.utls.USGSLogin(user, password, topLevelUrl)
		cfg.urllibSCP.request.install_opener(cfg.openerGeneral)
		cfg.timeSCP.sleep(0.5)
		try:
			request1 = cfg.urllibSCP.request.Request(url)
			response1 = cfg.openerGeneral.open(request1)
			cfg.timeSCP.sleep(0.5)
			f = cfg.urllibSCP.request.urlopen(response1.url)
			total_size = int(f.headers['Content-Length'])
			MB_size = round(total_size/1048576, 2)
			block_size = 1024 * 1024
			ratio = 0
			tune = 'Yes'
			with open(outputPath, 'wb') as file:
				while True:
					if tune == 'Yes':
						start = cfg.datetimeSCP.datetime.now()
					block = f.read(block_size)
					dSize =  round(int(cfg.osSCP.stat(outputPath).st_size)/1048576, 2)
					cfg.uiUtls.updateBar(progress, '(' + str(dSize) + '/' + str(MB_size) + ' MB) ' +  url, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Downloading'))
					cfg.QtWidgetsSCP.qApp.processEvents()
					if not block:
						break
					file.write(block)
					if tune == 'Yes':
						end = cfg.datetimeSCP.datetime.now()
						delta =  end - start
						newRatio = block_size / delta.microseconds
						if newRatio > ratio:
							block_size = block_size + 1024 * 1024
						elif newRatio < ratio:
							block_size = block_size - 1024 * 1024
							tune = 'No'
						ratio = newRatio
					if cfg.actionCheck == 'No':
						raise ValueError('Cancel action')
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
			return 'Yes'
		except Exception as err:
			if str(err) != 'Cancel action':
				if quiet == 'No':
					cfg.mx.msgErr50(str(err))
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err) + " url:" + str(url))
			raise ValueError(str(err))
	
	# encrypt password
	def encryptPassword(self, password):
		e = cfg.base64SCP.b64encode(bytes(password, 'utf-8'))
		return str(e)
		
	# decrypt password
	def decryptPassword(self, password):
		if password is not None:
			d = cfg.base64SCP.b64decode(password)
			return d
		else:
			return ''
		
##################################
	''' LOG functions '''
##################################

	# Clear log file
	def clearLogFile(self):
		if cfg.osSCP.path.isfile(cfg.logFile):
			try:
				l = open(cfg.logFile, 'w')
			except:
				pass
			try:
				# logger
				cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "LOG ACTIVE" + cfg.sysSCPInfo)
				cfg.ui.log_tableWidget.clearContents()
				for i in range(0, cfg.ui.log_tableWidget.rowCount()):
					cfg.ui.log_tableWidget.removeRow(0)
			except:
				cfg.mx.msg2()

	# Get the code line number for log file
	def lineOfCode(self):
		return str(cfg.inspectSCP.currentframe().f_back.f_lineno)
		
	# logger condition
	def logCondition(self, function, message = ""):
		if cfg.logSetVal == 'Yes':
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
			# log table
			mT = m.split("\t")
			tW = cfg.ui.log_tableWidget
			c = tW.rowCount()
			# add list items to table
			tW.setRowCount(c + 1)		
			if "ERROR exception" in mT[2]:
				cfg.utls.addTableItem(tW, mT[0], c, 0, 'No', cfg.QtGuiSCP.QColor(254, 137, 137))
				cfg.utls.addTableItem(tW, mT[1], c, 1, 'No', cfg.QtGuiSCP.QColor(254, 137, 137))
				cfg.utls.addTableItem(tW, mT[2], c, 2, 'No', cfg.QtGuiSCP.QColor(254, 137, 137))
			elif "error" in mT[2].lower():
				cfg.utls.addTableItem(tW, mT[0], c, 0, 'No', cfg.QtGuiSCP.QColor(30, 200, 200))
				cfg.utls.addTableItem(tW, mT[1], c, 1, 'No', cfg.QtGuiSCP.QColor(30, 200, 200))
				cfg.utls.addTableItem(tW, mT[2], c, 2, 'No', cfg.QtGuiSCP.QColor(30, 200, 200))
			else:
				cfg.utls.addTableItem(tW, mT[0], c, 0, 'No')
				cfg.utls.addTableItem(tW, mT[1], c, 1, 'No')
				cfg.utls.addTableItem(tW, mT[2], c, 2, 'No')
			cfg.ui.log_tableWidget.scrollToBottom()
		except:
			pass

##################################
	''' Time functions '''
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
	''' Symbology functions '''
##################################
		
	# set layer color for ROIs
	def ROISymbol(self, layer):
		st = { 'color': '0,0,0,230',  'color_border': '255,255,255,230', 'style': 'solid', 'style_border': 'dash' }
		r = cfg.qgisCoreSCP.QgsFillSymbol.createSimple(st)
		renderer = layer.renderer()
		renderer.setSymbol(r)
		
	# Define vector symbology
	def vectorSymbol(self, layer, signatureList, macroclassCheck):
		c = []
		n = []
		# class count
		mc = []
		v = signatureList
		s = cfg.qgisCoreSCP.QgsSymbol.defaultSymbol(layer.geometryType())
		s.setColor(cfg.QtGuiSCP.QColor('#000000'))
		c.append(cfg.qgisCoreSCP.QgsRendererCategory(0, s, '0 - ' + cfg.uncls))
		for i in range(0, len(v)):
			if macroclassCheck == 'Yes':
				if int(v[i][0]) not in mc:
					mc.append(int(v[i][0]))
					n.append([int(v[i][0]), cfg.QtGuiSCP.QColor(v[i][6]), str(v[i][1])])
			else:
				n.append([int(v[i][2]), v[i][6], str(v[i][3])])
		for b in sorted(n, key=lambda c: c[0]):
			s = cfg.qgisCoreSCP.QgsSymbol.defaultSymbol(layer.geometryType())
			s.setColor(b[1])
			ca = cfg.qgisCoreSCP.QgsRendererCategory(b[0], s, str(b[0]) + ' - ' + b[2])
			c.append(ca)
		f = 'DN'
		r = cfg.qgisCoreSCP.QgsCategorizedSymbolRenderer(f, c)
		layer.setRenderer(r)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		
	# Define class symbology
	def rasterSymbol(self, classLayer, signatureList, macroclassCheck):
		# The band of classLayer
		cLB = 1
		# Color list for ramp
		cL = []
		n = []
		# class count
		mc = []
		v = signatureList
		if cfg.unclassValue is not None:
			cL.append(cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(cfg.unclassValue, cfg.QtGuiSCP.QColor("#4d4d4d"), cfg.overlap))
		cL.append(cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(0, cfg.QtGuiSCP.QColor("#000000"), "0 - " + cfg.uncls))
		for i in range(0, len(v)):
			if macroclassCheck == 'Yes':
				if int(v[i][0]) not in mc and int(v[i][0]) != 0:
					mc.append(int(v[i][0]))
					n.append([int(v[i][0]), cfg.QtGuiSCP.QColor(v[i][6]), str(v[i][1])])
			else:
				if int(v[i][2]) != 0:
					n.append([int(v[i][2]), v[i][6], str(v[i][3])])
		for b in sorted(n, key=lambda c: c[0]):
			cL.append(cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(b[0], b[1], str(b[0]) + " - " + b[2]))
		# Create the renderer
		lR = cfg.qgisCoreSCP.QgsPalettedRasterRenderer(classLayer.dataProvider(), cLB, cL)
		# Apply the renderer to classLayer
		classLayer.setRenderer(lR)
		# refresh legend
		if hasattr(classLayer, "setCacheImage"):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.utls.refreshLayerSymbology(classLayer)
		ql = cfg.utls.layerSource(classLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "" + str(ql))
		
	# Define class symbology
	def rasterSymbolLCSAlgorithmRaster(self, classLayer):
		# The band of classLayer
		cLB = 1
		# Color list for ramp
		cL = []
		if cfg.unclassValue is not None:
			cL.append(cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(cfg.unclassValue, cfg.QtGuiSCP.QColor("#4d4d4d"), cfg.overlap))
		cL.append(cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(0, cfg.QtGuiSCP.QColor("#000000"), "0 " + cfg.uncls))
		cL.append(cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(1, cfg.QtGuiSCP.QColor("#ffffff"), "1 " + cfg.clasfd))
		# Create the renderer
		lR = cfg.qgisCoreSCP.QgsPalettedRasterRenderer(classLayer.dataProvider(), cLB, cL)
		# Apply the renderer to classLayer
		classLayer.setRenderer(lR)
		# refresh legend
		if hasattr(classLayer, "setCacheImage"):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.utls.refreshLayerSymbology(classLayer)
		ql = cfg.utls.layerSource(classLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "" + str(ql))
		
	# Define class symbology
	def rasterPreviewSymbol(self, previewLayer, algorithmName):
		if cfg.ui.LC_signature_checkBox.isChecked():
			cfg.utls.rasterSymbolLCSAlgorithmRaster(previewLayer)
		elif algorithmName == cfg.algMinDist or algorithmName == cfg.algSAM:
			cfg.utls.rasterSymbolPseudoColor(previewLayer)
		elif algorithmName == cfg.algML:
			cfg.utls.rasterSymbolSingleBandGray(previewLayer)
			
	# Define class symbology pseudo color
	def rasterSymbolPseudoColor(self, layer):
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
		cL.append(cfg.qgisCoreSCP.QgsColorRampShader.ColorRampItem(min, colorMin, str(min)))
		cL.append(cfg.qgisCoreSCP.QgsColorRampShader.ColorRampItem(max, colorMax, str(max)))
		# Create the shader
		lS = cfg.qgisCoreSCP.QgsRasterShader()
		# Create the color ramp function
		cR = cfg.qgisCoreSCP.QgsColorRampShader()
		cR.setColorRampType(cfg.qgisCoreSCP.QgsColorRampShader.Interpolated)
		cR.setColorRampItemList(cL)
		# Set the raster shader function
		lS.setRasterShaderFunction(cR)
		# Create the renderer
		lR = cfg.qgisCoreSCP.QgsSingleBandPseudoColorRenderer(layer.dataProvider(), cLB, lS)
		# Apply the renderer to layer
		layer.setRenderer(lR)
		# refresh legend
		if hasattr(layer, "setCacheImage"):
			layer.setCacheImage(None)
		layer.triggerRepaint()
		cfg.utls.refreshLayerSymbology(layer)
		ql = cfg.utls.layerSource(layer)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "" + str(ql))
		
	# Define class symbology single band grey
	def rasterSymbolSingleBandGray(self, layer):
		# QGIS3
		#layer.setDrawingStyle("SingleBandGray")
		try:
			layer.setContrastEnhancement(cfg.qgisCoreSCP.QgsContrastEnhancement.StretchToMinimumMaximum, cfg.qgisCoreSCP.QgsRasterMinMaxOrigin.CumulativeCut)
			# refresh legend
			if hasattr(layer, "setCacheImage"):
				layer.setCacheImage(None)
			layer.triggerRepaint()
			cfg.utls.refreshLayerSymbology(layer)
			ql = cfg.utls.layerSource(layer)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "" + str(ql))
		except Exception as err:
			list = 'No'
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			
	# Define raster symbology
	def rasterSymbolGeneric(self, rasterLayer, zeroValue = 'Unchanged', rasterUniqueValueList = None):
		if rasterUniqueValueList is None:
			ql = cfg.utls.layerSource(rasterLayer)
			cfg.parallelArrayDict = {}
			o = cfg.utls.multiProcessRaster(rasterPath = ql, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, progressMessage = 'UniqueVal ', deleteArray = 'No')
			# calculate unique values
			values = cfg.np.array([])
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						values = cfg.np.append(values, ar[0, ::])
				except:
					pass
			rasterBandUniqueVal = cfg.np.unique(values).tolist()
			refRasterBandUniqueVal = sorted(rasterBandUniqueVal)
		else:
			refRasterBandUniqueVal = rasterUniqueValueList
		try:
			maxV = max(refRasterBandUniqueVal)
		except:
			maxV = 1
		# Color list for ramp
		cL = [ cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(0, cfg.QtGuiSCP.QColor(0,0,0), zeroValue)]
		for i in refRasterBandUniqueVal:
			if i > maxV/2:
				c = cfg.QtGuiSCP.QColor(int(255 * (i/maxV)),int(255 * (1- (i/maxV))),int(255 * (1 - (i/maxV))))
				cL.append(cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(i, c, str(i)))
			elif i > 0:
				c = cfg.QtGuiSCP.QColor(int(255 * (i/maxV)),int(255 * (i/maxV)),int(255 * (1 - (i/maxV))))
				cL.append(cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(i, c, str(i)))
		# The band of classLayer
		classLyrBnd = 1
		# Create the renderer
		lyrRndr = cfg.qgisCoreSCP.QgsPalettedRasterRenderer(rasterLayer.dataProvider(), classLyrBnd, cL)
		# Apply the renderer to rasterLayer
		rasterLayer.setRenderer(lyrRndr)
		# refresh legend
		if hasattr(rasterLayer, 'setCacheImage'):
			rasterLayer.setCacheImage(None)
		rasterLayer.triggerRepaint()
		cfg.utls.refreshLayerSymbology(rasterLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "symbology")

	# Define scatter raster symbology
	def rasterScatterSymbol(self, valueColorList):
		# Color list for ramp
		cL = []
		for i in valueColorList:
			cL.append(cfg.qgisCoreSCP.QgsPalettedRasterRenderer.Class(i[0], cfg.QtGuiSCP.QColor(i[1]), str(i[0])))
		return cL
		
	# set scatter raster symbology
	def setRasterScatterSymbol(self, classLayer, shader):
		# The band of classLayer
		cLB = 1
		# Create the renderer
		lR = cfg.qgisCoreSCP.QgsPalettedRasterRenderer(classLayer.dataProvider(), cLB, shader)
		# Apply the renderer to classLayer
		classLayer.setRenderer(lR)
		# refresh legend
		if hasattr(classLayer, "setCacheImage"):
			classLayer.setCacheImage(None)
		classLayer.triggerRepaint()
		cfg.utls.refreshLayerSymbology(classLayer)
		ql = cfg.utls.layerSource(classLayer)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "" + str(ql))
		
	# copy renderer
	def copyRenderer(self, inputRaster, outputRaster):
		try:
			r = inputRaster.renderer().clone()
			# Apply the renderer to rasterLayer
			outputRaster.setRenderer(r)
			outputRaster.triggerRepaint()
			cfg.utls.refreshLayerSymbology(outputRaster)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		except Exception as err:
			list = 'No'
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			
##################################
	''' Classification functions '''
##################################
			
	# calculate covariance matrix from array list
	def calculateCovMatrix(self, arrayList):
		matrix = cfg.np.stack(arrayList)
		# covariance matrix (degree of freedom = 1 for unbiased estimate)
		CovMatrix = cfg.np.ma.cov(cfg.np.ma.masked_invalid(matrix), ddof=1)
		try:
			try:
				inv = cfg.np.linalg.inv(CovMatrix)
				if cfg.np.isnan(inv[0,0]):
					CovMatrix = 'No'
			except:
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'TEST matrix: ' + str(CovMatrix))
				CovMatrix = 'No'
		except Exception as err:
			CovMatrix = 'No'
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'cov matrix: ' + str(CovMatrix))
		return CovMatrix
			
	# convert list to covariance array
	def listToCovarianceMatrix(self, list):
		try:
			covMat = cfg.np.zeros((len(list), len(list)), dtype=cfg.np.float32)
			i = 0
			for x in list:
				covMat[i, :] = x
				i = i + 1
			return covMat
		except Exception as err:
			list = 'No'
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		return 'No'
		
	# convert covariance array to list
	def covarianceMatrixToList(self, covarianceArray):
		try:
			d = covarianceArray.shape
			list = []
			for i in range(0, d[0]):
				list.append(covarianceArray[i, :].tolist())
		except Exception as err:
			list = 'No'
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		return list
		
	# create one raster for each signature class
	def createSignatureClassRaster(self, signatureList, gdalRasterRef, outputDirectory, nodataValue = None, outputName = None, previewSize = 0, previewPoint = None, compress = 'No', compressFormat = 'DEFLATE21'):
		dT = cfg.utls.getTime()
		outputRasterList = []
		for s in range(0, len(signatureList)):
			if outputName is None:
				o = outputDirectory + '/' + cfg.sigRasterNm + '_' + str(signatureList[s][0]) + '_' + str(signatureList[s][2]) + '_' + dT + '.tif'
			else:
				o = outputDirectory + '/' + outputName + '_' + str(signatureList[s][0]) + '_' + str(signatureList[s][2]) + '.tif'
			outputRasterList.append(o)
		oRL = cfg.utls.createRasterFromReference(gdalRasterRef, 1, outputRasterList, nodataValue, 'GTiff', cfg.rasterDataType, previewSize, previewPoint, compress, compressFormat)
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'end createSignatureClassRaster')
		return oRL, outputRasterList
		
	# perform classification
	def classificationMultiprocess(self, bandListNumber, signatureList, algorithmName, rasterArray, landCoverSignature, LCSClassAlgorithm,LCSLeaveUnclassified, algBandWeigths, outputGdalRasterList, outputAlgorithmRaster, outputClassificationRaster, nodataValue, macroclassCheck, algThrshld):
		sigArrayList = self.createArrayFromSignature(bandListNumber, signatureList)
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'sigArrayList ' + str(sigArrayList))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'outputGdalRasterList ' + str(outputGdalRasterList))
		LCSminMaxL = cfg.utls.LCSminMaxList(signatureList)
		minArray = None
		maxArray = None
		classArray = None
		classArrayAlg = None
		classArrayLCS = None
		equalArray = None
		cfg.unclassValue = None
		cfg.algThrshld = algThrshld
		n = 0
		# max and min values
		tr = self.thresholdList(signatureList)
		# if maximum likelihood
		covMatrList = self.covarianceMatrixList(signatureList)
		# open input with GDAL
		rDC = cfg.gdalSCP.Open(outputClassificationRaster, cfg.gdalSCP.GA_Update)
		rDA = cfg.gdalSCP.Open(outputAlgorithmRaster, cfg.gdalSCP.GA_Update)
		if landCoverSignature == 'Yes':
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'landCoverSignature ' + str(landCoverSignature))
			for s in sigArrayList:
				# algorithm
				rasterArrayx = cfg.np.copy(rasterArray)
				# threshold
				multFactor = float(1)
				# second classification
				if LCSClassAlgorithm == 'Yes':
					secondClassification = algorithmName
				else:
					secondClassification = 'No'
				if secondClassification == 'No':
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
				# logger
				cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'algBandWeigths' + str(algBandWeigths))
				# calculate LCS array
				LCSarray = cfg.utls.algorithmLCS(rasterArrayx, s, LCSminMaxL[n][0], LCSminMaxL[n][1] , multFactor, algBandWeigths, dataValue, nodataValue)
				if type(LCSarray) is not int:
					# open input with GDAL
					oR = cfg.gdalSCP.Open(outputGdalRasterList[n], cfg.gdalSCP.GA_Update)
					# binary classification
					LCSarrayWrite = cfg.np.where(LCSarray==dataValue,1,0)
					# algorithm raster
					cfg.utls.writeArrayBlock(oR, 1, LCSarrayWrite, 0, 0, nodataValue)
					oR = None
					LCSarrayWrite = None
					# find equal array for overlapping classes
					if equalArray is None:
						equalArray = LCSarray
					else:
						equalArray = cfg.utls.findEqualArray(LCSarray, equalArray, dataValue, nodataValue, cfg.unclassValue)
					if classArray is None:
						classArray = nodataValue
					if macroclassCheck == 'Yes':
						classArray = cfg.utls.classifyClassesLCSSimple(LCSarray, equalArray, classArray, dataValue, cfg.unclassValue, nodataValue, signatureList[n][0])
					else:
						classArray = cfg.utls.classifyClassesLCSSimple(LCSarray, equalArray, classArray, dataValue, cfg.unclassValue, nodataValue, signatureList[n][2])
					# in case of same class overlapping
					equalArray = cfg.np.where( (equalArray ==cfg.unclassValue) & (classArray !=cfg.unclassValue), dataValue, equalArray)
					# refine class output
					classArrayLCS = cfg.np.where(classArray == nodataValue, 0, classArray)
					algArrayWrite = cfg.np.where(classArrayLCS == 0, 0, cfg.np.where(classArrayLCS == cfg.unclassValue, cfg.unclassValue, 1))
					# algorithm raster
					cfg.utls.writeArrayBlock(rDA, 1, algArrayWrite, 0, 0, nodataValue)
					algArrayWrite = None
					if secondClassification == 'No':
						pass
					elif secondClassification == cfg.algMinDist:
						# algorithm
						rasterArrayx = cfg.np.copy(rasterArray)
						c = cfg.utls.algorithmMinimumDistance(rasterArrayx, s, cfg.algBandWeigths)
						# threshold
						algThrshld = float(tr[n])
						if algThrshld > 0:
							c = cfg.utls.minimumDistanceThreshold(c, algThrshld, nodataValue)
						if type(c) is not int:
							if minArray is None:
								minArray = c
							else:
								minArray = cfg.utls.findMinimumArray(c, minArray, nodataValue)
							# signature classification raster
							if macroclassCheck == 'Yes':
								clA = cfg.utls.classifyClasses(c, minArray, signatureList[n][0])
							else:
								clA = cfg.utls.classifyClasses(c, minArray, signatureList[n][2])
							# classification raster
							if classArrayAlg is None:
								classArrayAlg = clA
							else:
								e = cfg.np.ma.masked_equal(clA, 0)
								classArrayAlg =  e.mask * classArrayAlg + clA
								e = None
							clA = None
							classArrayAlg[classArrayAlg == cfg.unclassifiedVal] = 0
							classArrayLCS = cfg.np.where(classArray == cfg.unclassValue, classArrayAlg, classArray)
							if LCSLeaveUnclassified == 'Yes':
								pass
							else:
								classArrayLCS = cfg.np.where(classArray == nodataValue, classArrayAlg, classArrayLCS)
						else:
							return 'No'
					elif secondClassification == cfg.algSAM:
						# algorithm
						rasterArrayx = cfg.np.copy(rasterArray)
						c = cfg.utls.algorithmSAM(rasterArrayx, s, cfg.algBandWeigths)
						# threshold
						algThrshld = float(tr[n])
						if algThrshld > 0:
							if algThrshld > 90:
								algThrshld = 90
							c = cfg.utls.minimumDistanceThreshold(c, algThrshld, nodataValue)
						if type(c) is not int:
							if minArray is None:
								minArray = c
							else:
								minArray = cfg.utls.findMinimumArray(c, minArray, nodataValue)
							# signature classification raster
							if macroclassCheck == 'Yes':
								clA = cfg.utls.classifyClasses(c, minArray, signatureList[n][0])
							else:
								clA = cfg.utls.classifyClasses(c, minArray, signatureList[n][2])
							# classification raster
							if classArrayAlg is None:
								classArrayAlg = clA
							else:
								e = cfg.np.ma.masked_equal(clA, 0)
								classArrayAlg =  e.mask * classArrayAlg + clA
								e = None
							clA = None
							classArrayAlg[classArrayAlg == cfg.unclassifiedVal] = 0
							classArrayLCS = cfg.np.where(classArray == cfg.unclassValue, classArrayAlg, classArray)
							if LCSLeaveUnclassified == 'Yes':
								pass
							else:
								classArrayLCS = cfg.np.where(classArray == nodataValue, classArrayAlg, classArrayLCS)
						else:
							return 'No'									
					elif secondClassification == cfg.algML:
						# algorithm
						rasterArrayx = cfg.np.copy(rasterArray)
						# threshold
						algThrshld = float(tr[n])
						if algThrshld > 100:
							algThrshld = 100
						c = cfg.utls.algorithmMaximumLikelihood(rasterArrayx, s, covMatrList[n], cfg.algBandWeigths, algThrshld, nodataValue)
						if type(c) is not int:
							if maxArray is None:
								maxArray = c
							else:
								maxArray = cfg.utls.findMaximumArray(c, maxArray, nodataValue)
							# signature classification raster
							if macroclassCheck == 'Yes':
								clA = cfg.utls.classifyClasses(c, maxArray, signatureList[n][0])
							else:
								clA = cfg.utls.classifyClasses(c, maxArray, signatureList[n][2])
							# classification raster
							if classArrayAlg is None:
								classArrayAlg = clA
							else:
								e = cfg.np.ma.masked_equal(clA, 0)
								classArrayAlg =  e.mask * classArrayAlg + clA
								e = None
							clA = None
							classArrayAlg[classArrayAlg == cfg.unclassifiedVal] = 0
							classArrayLCS = cfg.np.where(classArray == cfg.unclassValue, classArrayAlg, classArray)
							if LCSLeaveUnclassified == 'Yes':
								pass
							else:
								classArrayLCS = cfg.np.where(classArray == nodataValue, classArrayAlg, classArrayLCS)
						else:
							return 'No'
					classArrayWrite = cfg.np.where(classArrayLCS == nodataValue, 0, classArrayLCS)
					# classification raster
					cfg.utls.writeArrayBlock(rDC, 1, classArrayWrite, 0, 0, nodataValue)
					n = n + 1
				else:
					return 'No'
		elif algorithmName == cfg.algMinDist:
			for s in sigArrayList:
				cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'n ' + str(n))
				# algorithm
				rasterArrayx = cfg.np.copy(rasterArray)
				c = self.algorithmMinimumDistance(rasterArrayx, s, cfg.algBandWeigths)
				# logger
				cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'algorithmMinimumDistance signature' + str(c))
				# threshold
				algThrshld = float(tr[n])
				if algThrshld > 0:
					c = self.minimumDistanceThreshold(c, algThrshld, nodataValue)
				if type(c) is not int:
					# open input with GDAL
					oR = cfg.gdalSCP.Open(outputGdalRasterList[n], cfg.gdalSCP.GA_Update)
					# logger
					cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'outputGdalRasterList[n] ' + str(outputGdalRasterList[n]))
					# logger
					cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oR ' + str(oR))
					# algorithm raster
					cfg.utls.writeArrayBlock(oR, 1, c, 0, 0, nodataValue)
					oR = None
					if minArray is None:
						minArray = c
					else:
						minArray = self.findMinimumArray(c, minArray, nodataValue)
					# logger
					cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'findMinimumArray signature' + str(minArray[0,0]))
					# minimum raster
					self.writeArrayBlock(rDA, 1, minArray, 0, 0, nodataValue)
					# signature classification raster
					if macroclassCheck == 'Yes':
						clA = self.classifyClasses(c, minArray, signatureList[n][0])
					else:
						clA = self.classifyClasses(c, minArray, signatureList[n][2])
					# classification raster
					if classArray is None:
						classArray = clA
					else:
						e = cfg.np.ma.masked_equal(clA, 0)
						classArray =  e.mask * classArray + clA
						e = None
					clA = None
					classArray[classArray == cfg.unclassifiedVal] = 0
					# classification raster
					self.writeArrayBlock(rDC, 1, classArray, 0, 0, nodataValue)
					n = n + 1
				else:
					return 'No'
		elif algorithmName == cfg.algSAM:
			for s in sigArrayList:
				# algorithm
				rasterArrayx = cfg.np.copy(rasterArray)
				c = self.algorithmSAM(rasterArrayx, s, cfg.algBandWeigths)
				# threshold
				algThrshld = float(tr[n])
				if algThrshld > 0:
					if algThrshld > 90:
						algThrshld = 90
					c = self.minimumDistanceThreshold(c, algThrshld, nodataValue)
				if type(c) is not int:
					# open input with GDAL
					oR = cfg.gdalSCP.Open(outputGdalRasterList[n], cfg.gdalSCP.GA_Update)
					# algorithm raster
					self.writeArrayBlock(oR, 1, c, 0, 0, nodataValue)
					oR = None
					if minArray is None:
						minArray = c
					else:
						minArray = self.findMinimumArray(c, minArray, nodataValue)
					# minimum raster
					self.writeArrayBlock(rDA, 1, minArray, 0, 0, nodataValue)
					# signature classification raster
					if macroclassCheck == 'Yes':
						clA = self.classifyClasses(c, minArray, signatureList[n][0])
					else:
						clA = self.classifyClasses(c, minArray, signatureList[n][2])
					# classification raster
					if classArray is None:
						classArray = clA
					else:
						e = cfg.np.ma.masked_equal(clA, 0)
						classArray =  e.mask * classArray + clA
						e = None
					clA = None
					classArray[classArray == cfg.unclassifiedVal] = 0
					# classification raster
					self.writeArrayBlock(rDC, 1, classArray, 0, 0, nodataValue)
					n = n + 1
				else:
					return 'No'
		elif algorithmName == cfg.algML:
			for s in sigArrayList:
				# algorithm
				rasterArrayx = cfg.np.copy(rasterArray)
				# threshold
				algThrshld = float(tr[n])
				if algThrshld > 100:
					algThrshld = 100
				c = self.algorithmMaximumLikelihood(rasterArrayx, s, covMatrList[n], cfg.algBandWeigths, algThrshld, nodataValue)
				if type(c) is not int:
					# open input with GDAL
					oR = cfg.gdalSCP.Open(outputGdalRasterList[n], cfg.gdalSCP.GA_Update)
					# algorithm raster
					self.writeArrayBlock(oR, 1, c, 0, 0, nodataValue)
					oR = None
					if maxArray is None:
						maxArray = c
					else:
						maxArray = self.findMaximumArray(c, maxArray, nodataValue)
					# maximum raster
					self.writeArrayBlock(rDA, 1, maxArray, 0, 0, nodataValue)
					# signature classification raster
					if macroclassCheck == 'Yes':
						clA = self.classifyClasses(c, maxArray, signatureList[n][0])
					else:
						clA = self.classifyClasses(c, maxArray, signatureList[n][2])
					# classification raster
					if classArray is None:
						classArray = clA
					else:
						e = cfg.np.ma.masked_equal(clA, 0)
						classArray =  e.mask * classArray + clA
						e = None
					clA = None
					classArray[classArray == cfg.unclassifiedVal] = 0
					# classification raster
					self.writeArrayBlock(rDC, 1, classArray, 0, 0, nodataValue)
					n = n + 1
				else:
					return 'No'
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
		rDC = None
		rDA = None
		
	# classify classes
	def classifyClasses(self, algorithmArray, minimumArray, classID, nodataValue = -999):
		if int(classID) == 0:
			classID = cfg.unclassifiedVal
		cB = cfg.np.equal(algorithmArray, minimumArray) * int(classID)
		cA = cfg.np.where(minimumArray != nodataValue, cB, cfg.unclassifiedVal)
		return cA
										
	# classify classes
	def classifyClassesLCSSimple(self, LCSarray, equalArray, classArrayLCS, dataValue, unclassValue, nodataValue, classID):
		cA = cfg.np.where( (LCSarray == dataValue) & (equalArray == dataValue), int(classID), cfg.np.where( (equalArray == unclassValue) & (classArrayLCS != int(classID) ), unclassValue,classArrayLCS ) )
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
		m = cfg.np.maximum(firstArray, secondArray)
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
	def createArrayFromSignature(self, bandListNumber, signatureList):
		arrayList = []
		for s in signatureList:
			val = s[4]
			array = cfg.np.zeros((bandListNumber), dtype=cfg.np.float32)
			max = bandListNumber * 2
			i = 0
			for b in range(0, max, 2):
				array[i] = val[b]
				i = i + 1
			arrayList.append(array)
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
		except Exception as err:
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
			arrayList.append([s[8], s[9]])
		return arrayList

	# create threshold list from signature list
	def thresholdList(self, signatureList):
		c = []
		if cfg.algThrshld > 0:
			for s in signatureList:
				c.append(cfg.algThrshld)
		else:
			for s in signatureList:
				t = s[10]
				c.append(t)
		return c
		
	# calculate critical chi square and threshold
	def chisquare(self, algThrshld, bands):
		p = (algThrshld / 100)
		chi = cfg.statdistrSCP.chi2.isf(p, bands)
		return chi
			
	# Maximum Likelihood algorithm
	def algorithmMaximumLikelihood(self, rasterArray, signatureArray, covarianceMatrix, weightList = None, algThrshld = 0, nodataValue = 0):
		try:
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
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' logdet: ' + str(logdet))
			if algThrshld > 0:
				chi = self.chisquare(algThrshld, covarianceMatrix.shape[0])
				threshold = - 2 * chi - logdet
				cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' threshold: ' + str(threshold) + ' algThrshld: ' + str(algThrshld))
				algArray[algArray < threshold] = nodataValue
			return algArray
		except Exception as err:
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
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
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
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
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msgErr28()
			return 0
	
##################################
	''' Signature spectral distance functions '''
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
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
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
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
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
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
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
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
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
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			angle = cfg.notAvailable
		return angle

##################################
	''' Signature functions '''
##################################
		
	# calculate ROI signature (one signature for ROIs that have the same macroclass ID and class ID)
	def calculateSignature(self, lyr, rasterName, featureIDList, macroclassID, macroclassInfo, classID, classInfo, progress = None, progresStep = None, plot = 'No', tempROI = 'No', SCP_UID = None, bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		if progress is not None:
			cfg.uiUtls.updateBar(progress + int((1 / 4) * progresStep))
		# disable map canvas render for speed
		cfg.cnvs.setRenderFlag(False)
		# temporary layer
		tSD = cfg.utls.createTempRasterPath('tif')
		tLP = cfg.utls.createTempRasterPath('gpkg')
		# get layer crs
		crs = cfg.utls.getCrs(lyr)
		# create a temp shapefile with a field
		cfg.utls.createEmptyShapefile(crs, tLP, format = 'GPKG')
		mL = cfg.utls.addVectorLayer(tLP)
		rD = None
		for x in featureIDList:
			# copy ROI to temp shapefile
			cfg.utls.copyFeatureToLayer(lyr, x, mL)
		tRxs = cfg.utls.createTempRasterPath('tif')
		if progress is not None:
			cfg.uiUtls.updateBar(progress + int((2 / 4) * progresStep))
		cfg.tblOut = {}
		cfg.parallelArrayDict = {}
		ROIArray = []
		ROIsize = None
		# band set
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			cfg.utls.checkBandSet(bandSetNumber)
			check = cfg.utls.vectorToRaster(None, tLP, None, tRxs, cfg.bndSetLst[0], None, 'GTiff', 1)
			if check == 'No':
				return 'No'
			outList = cfg.utls.clipRasterByRaster(cfg.bndSetLst, tRxs, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Calculating signature'), stats = 'Yes')
		else:
			rS = cfg.utls.selectLayerbyName(rasterName, 'Yes')
			check = cfg.utls.vectorToRaster(None, tLP, None, tRxs, rS.source(), None, 'GTiff', 1)
			if check == 'No':
				return 'No'
			# calculate ROI center, height and width
			rCX, rCY, rW, rH = cfg.utls.getShapefileRectangleBox(tLP)
			# subset 
			tLX, tLY, pS = cfg.utls.imageInformation(rasterName)
			tS = cfg.utls.createTempRasterPath('tif')
			# reduce band size
			pr = cfg.utls.subsetImage(rasterName, rCX, rCY, int(round(rW/pS + 3)),  int(round(rH/pS + 3)), str(tS), virtual = 'Yes')
			if pr == 'Yes':
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error edge')
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				return pr
			oList = cfg.utls.rasterToBands(tS, cfg.tmpDir, None, 'No', cfg.bandSetsList[bandSetNumber][6])
			outList = cfg.utls.clipRasterByRaster(oList, tRxs, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Calculating signature'), stats = 'Yes')
		# calculate signatures
		b = 0
		ROIsizes = []
		for x in sorted(cfg.parallelArrayDict):
			try:
				for dic in cfg.parallelArrayDict[x]:
					outFile, rStat, ar, ROIsize = dic
					ROIsizes.append(ROIsize)
			except:
				pass
			rStatStr = str(rStat)
			rStatStr = rStatStr.replace('nan', '0')
			rStat = eval(rStatStr)
			ROIArray.append(ar)
			cfg.tblOut['BAND_' + str(b+1)] = rStat
			cfg.tblOut['WAVELENGTH_' + str(b + 1)] = cfg.bandSetsList[bandSetNumber][4][b]
			b = b + 1
		if progress is not None:
			cfg.uiUtls.updateBar(progress + int((3 / 4) * progresStep))
		# if not temporary ROI min max
		if tempROI != 'MinMax':
			try:
				covMat = cfg.utls.calculateCovMatrix(ROIArray)
				if covMat == 'No':
					cfg.mx.msgWar12(macroclassID, classID)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				covMat = 'No'
				cfg.mx.msgWar12(macroclassID, classID)
		# remove temp layers
		cfg.utls.removeLayer(cfg.utls.fileName(tLP))
		try:
			cfg.osSCP.remove(tRxs)
		except:
			pass
		try:
			cfg.tblOut['ROI_SIZE'] = min(ROIsizes)
		except:
			pass
		# if not temporary ROI min max
		if tempROI != 'MinMax':
			cfg.utls.ROIStatisticsToSignature(covMat, macroclassID, macroclassInfo, classID, classInfo, bandSetNumber, cfg.bandSetsList[bandSetNumber][5], plot, tempROI, SCP_UID)
		# enable map canvas render
		cfg.cnvs.setRenderFlag(True)
		if progress is not None:
			cfg.uiUtls.updateBar(progress + int((4 / 4) * progresStep))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "roi signature calculated")
			
	# calculate pixel signature
	def calculatePixelSignature(self, point, rasterName, bandSetNumber = None, plot = 'No', showPlot = 'Yes'):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		cfg.tblOut = {}
		cfg.tblOut["ROI_SIZE"] = 1
		rStat = []
		# band set
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			for b in range(0, len(cfg.bandSetsList[bandSetNumber][3])):
				rast = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][3][b], 'Yes')	
				# open input with GDAL
				try:
					ql = cfg.utls.layerSource(rast)
					Or = cfg.gdalSCP.Open(ql, cfg.gdalSCP.GA_ReadOnly)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msgErr4()
					return 'No'
				OrB = Or.GetRasterBand(1)
				geoT = Or.GetGeoTransform()
				tLX = geoT[0]
				tLY = geoT[3]
				pSX = geoT[1]
				pSY = geoT[5]
				# start and end pixels
				pixelStartColumn = (int((point.x() - tLX) / pSX))
				pixelStartRow = -(int((tLY - point.y()) / pSY))
				try:
					bVal = float(cfg.utls.readArrayBlock(OrB, pixelStartColumn, pixelStartRow, 1, 1)) * cfg.bandSetsList[bandSetNumber][6][0][b] + cfg.bandSetsList[bandSetNumber][6][1][b]
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msgErr4()
					return 'No'
				rStat = [bVal, bVal, bVal, 0]
				cfg.tblOut["BAND_" + str(b + 1)] = rStat
				cfg.tblOut["WAVELENGTH_" + str(b + 1)] = cfg.bandSetsList[bandSetNumber][4][b]
		else:
			rL = cfg.utls.selectLayerbyName(rasterName, 'Yes')
			# open input with GDAL
			try:
				qll = cfg.utls.layerSource(rL)
				Or = cfg.gdalSCP.Open(qll, cfg.gdalSCP.GA_ReadOnly)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				cfg.mx.msgErr4()
				return 'No'
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
				try:
					bVal = float(cfg.utls.readArrayBlock(OrB, pixelStartColumn, pixelStartRow, 1, 1))  * cfg.bandSetsList[bandSetNumber][6][0][b-1] + cfg.bandSetsList[bandSetNumber][6][1][b-1]	
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msgErr4()
					return 'No'
				rStat = [bVal, bVal, bVal, 0]
				cfg.tblOut["BAND_" + str(b)] = rStat
				cfg.tblOut["WAVELENGTH_" + str(b)] = cfg.bandSetsList[bandSetNumber][4][b-1]
		macroclassID = 0
		classID = 0
		macroclassInfo = cfg.pixelNm + " " + cfg.bandSetName + str(bandSetNumber + 1)
		classInfo = cfg.pixelCoords + " " + str(point)
		covMat = 'No'
		val = cfg.utls.ROIStatisticsToSignature(covMat, macroclassID, macroclassInfo, classID, classInfo, bandSetNumber, cfg.bandSetsList[bandSetNumber][5], plot, 'No')
		if showPlot == 'Yes':
			cfg.spSigPlot.showSignaturePlotT()
		return val
		
	# Get values for ROI signature
	def ROIStatisticsToSignature(self, covarianceMatrix, macroclassID, macroclassInfo, classID, classInfo, bandSetNumber = None, unit = None, plot = 'No', tempROI = 'No', SCP_UID = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		# band set
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			iB = len(cfg.bandSetsList[bandSetNumber][3])
		else:
			iR = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
			iB = iR.bandCount()
		wvl = []
		val = []
		valM = []
		min = []
		max = []
		vMin = []
		vMax = []
		try:
			ROISize = cfg.tblOut['ROI_SIZE']
			for b in range(1, iB + 1):
				stats = cfg.tblOut['BAND_' + str(b)]
				w = cfg.tblOut['WAVELENGTH_' + str(b)]
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
			if plot == 'No':
				if SCP_UID is None:
					i = cfg.utls.signatureID()
				else:
					i = SCP_UID
				cfg.signList['CHECKBOX_' + str(i)] = cfg.QtSCP.Checked
				cfg.signList['MACROCLASSID_' + str(i)] = macroclassID
				cfg.signList['MACROCLASSINFO_' + str(i)] = macroclassInfo
				cfg.signList['CLASSID_' + str(i)] = classID
				cfg.signList['CLASSINFO_' + str(i)] = classInfo
				cfg.signList['WAVELENGTH_' + str(i)] = wvl
				cfg.signList['VALUES_' + str(i)] = val
				cfg.signList['MIN_VALUE_' + str(i)] = vMin
				cfg.signList['MAX_VALUE_' + str(i)] = vMax
				cfg.signList['ROI_SIZE_' + str(i)] = ROISize
				cfg.signList['LCS_MIN_' + str(i)] = min
				cfg.signList['LCS_MAX_' + str(i)] = max
				cfg.signList['COVMATRIX_' + str(i)] = covarianceMatrix
				cfg.signList['MD_THRESHOLD_' + str(i)] = cfg.algThrshld
				cfg.signList['ML_THRESHOLD_' + str(i)] = cfg.algThrshld
				cfg.signList['SAM_THRESHOLD_' + str(i)] = cfg.algThrshld
				# counter
				n = 0
				m = []
				sdL = []
				for wi in wvl:
					m.append(val[n * 2])
					sdL.append(val[n * 2 +1])
					n = n + 1
				cfg.signList['MEAN_VALUE_' + str(i)] = m
				cfg.signList['SD_' + str(i)] = sdL
				if unit is None:
					unit = cfg.bandSetsList[bandSetNumber][5]
				cfg.signList['UNIT_' + str(i)] = unit
				cfg.signList['COLOR_' + str(i)] = c
				#cfg.signList['COMPL_COLOR_' + str(i)] = cc
				cfg.signIDs['ID_' + str(i)] = i
			# calculation for plot
			elif plot == 'Yes':
				if SCP_UID is None:
					i = cfg.utls.signatureID()
				else:
					i = SCP_UID
				cfg.spectrPlotList['CHECKBOX_' + str(i)] = cfg.QtSCP.Checked
				cfg.spectrPlotList['MACROCLASSID_' + str(i)] = macroclassID
				cfg.spectrPlotList['MACROCLASSINFO_' + str(i)] = macroclassInfo
				cfg.spectrPlotList['CLASSID_' + str(i)] = classID
				cfg.spectrPlotList['CLASSINFO_' + str(i)] = classInfo
				cfg.spectrPlotList['WAVELENGTH_' + str(i)] = wvl
				cfg.spectrPlotList['VALUES_' + str(i)] = val
				cfg.spectrPlotList['LCS_MIN_' + str(i)] = vMin
				cfg.spectrPlotList['LCS_MAX_' + str(i)] = vMax
				cfg.spectrPlotList['MIN_VALUE_' + str(i)] = vMin
				cfg.spectrPlotList['MAX_VALUE_' + str(i)] = vMax
				cfg.spectrPlotList['ROI_SIZE_' + str(i)] = ROISize
				cfg.spectrPlotList['COVMATRIX_' + str(i)] = covarianceMatrix
				cfg.spectrPlotList['MD_THRESHOLD_' + str(i)] = cfg.algThrshld
				cfg.spectrPlotList['ML_THRESHOLD_' + str(i)] = cfg.algThrshld
				cfg.spectrPlotList['SAM_THRESHOLD_' + str(i)] = cfg.algThrshld
				# counter
				n = 0
				m = []
				sdL = []
				for wi in wvl:
					m.append(val[n * 2])
					sdL.append(val[n * 2 +1])
					n = n + 1
				cfg.spectrPlotList['MEAN_VALUE_' + str(i)] = m
				cfg.spectrPlotList['SD_' + str(i)] = sdL
				if unit is None:
					unit = cfg.bandSetsList[bandSetNumber][5]
				cfg.spectrPlotList['UNIT_' + str(i)] = unit
				cfg.spectrPlotList['COLOR_' + str(i)] = c
				#cfg.spectrPlotList['COMPL_COLOR_' + str(i)] = cc
				cfg.signPlotIDs['ID_' + str(i)] = i
				if tempROI == 'Yes':
					try:
						cfg.tmpROIColor = cfg.spectrPlotList['COLOR_' + str(cfg.tmpROIID)]
						if cfg.spectrPlotList['MACROCLASSINFO_' + str(cfg.tmpROIID)] == cfg.tmpROINm:
							cfg.spSigPlot.removeSignatureByID(cfg.tmpROIID)
							cfg.tmpROIID = i 
							cfg.spectrPlotList['COLOR_' + str(i)] = cfg.tmpROIColor
						else:
							cfg.tmpROIID = i
							cfg.spectrPlotList['COLOR_' + str(i)] = cfg.QtGuiSCP.QColor(cfg.ROIClrVal)
					except:
						cfg.tmpROIID = i
						cfg.spectrPlotList['COLOR_' + str(i)] = cfg.QtGuiSCP.QColor(cfg.ROIClrVal)
					#cfg.spSigPlot.signatureListPlotTable(cfg.uisp.signature_list_plot_tableWidget)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' values to shape concluded, plot: ' + str(plot))
			elif plot == 'Pixel':
				return valM
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return []
			
	# import a shapefile
	def importShapefile(self):
		shpFile = cfg.ui.select_shapefile_label.text()
		if cfg.shpLay is None:
			cfg.mx.msg3()
			return 'No'
		if len(shpFile) > 0:
			cfg.uiUtls.addProgressBar()
			cfg.uiUtls.updateBar(10)
			shpName = cfg.utls.fileName(shpFile)
			tSS = cfg.utls.addVectorLayer(shpFile, shpName, 'ogr')
			# create memory layer
			provider = tSS.dataProvider()
			fields = provider.fields()
			tCrs = cfg.utls.getCrs(cfg.shpLay)
			pCrs = cfg.utls.getCrs(tSS)
			f = cfg.qgisCoreSCP.QgsFeature()
			mcIdF = self.fieldID(tSS, cfg.ui.MC_ID_combo.currentText())
			mcInfoF = self.fieldID(tSS, cfg.ui.MC_Info_combo.currentText())
			cIdF = self.fieldID(tSS, cfg.ui.C_ID_combo.currentText())
			cInfoF = self.fieldID(tSS, cfg.ui.C_Info_combo.currentText())
			for f in tSS.getFeatures():
				oFid = cfg.shpLay.fields().indexFromName('fid')
				mFid = cfg.shpLay.maximumValue(oFid) + 1
				if mFid < 1:
					mFid = 1
				cfg.shpLay.startEditing()
				aF = f.geometry()
				if pCrs != tCrs:
					# transform coordinates
					trs = cfg.qgisCoreSCP.QgsCoordinateTransform(pCrs, tCrs)
					aF.transform(trs)
				oF = cfg.qgisCoreSCP.QgsFeature()
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
				attributeList = [mFid, mcId, mcInfo, cId, cInfo, i]
				oF.setAttributes(attributeList)
				cfg.shpLay.addFeature(oF)
				cfg.shpLay.commitChanges()
				cfg.shpLay.dataProvider().createSpatialIndex()
				cfg.shpLay.updateExtents()
				cfg.uiUtls.updateBar(40)
				# calculate signature if checkbox is yes
				if cfg.ui.signature_checkBox_2.isChecked() is True:
					rId = cfg.utls.getIDByAttributes(cfg.shpLay, cfg.fldSCP_UID, str(i))
					cfg.utls.calculateSignature(cfg.shpLay, cfg.bandSetsList[cfg.bndSetNumber][8], rId, mcId, mcInfo, cId, cInfo, None, None, 'No', 'No', i)	
					cfg.uiUtls.updateBar(90)
			cfg.SCPD.ROIListTableTree(cfg.shpLay, cfg.uidc.signature_list_treeWidget)
			cfg.uiUtls.updateBar(100)
			cfg.uiUtls.removeProgressBar()
			
##################################
	''' Process functions '''
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
	def create3x3Window(self, connection = '8'):
		size = 3
		B = cfg.np.ones((size,size))
		if connection != '8':
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
		condit1 = ''
		condit2 = ''
		bandX = cfg.np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
		bandY = cfg.np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
		for list in rangeList:
			for range in list[0]:
				Xmin = range[0][0]
				Xmax = range[0][1]
				Ymin = range[1][0]
				Ymax = range[1][1]
				condit1 = condit1 + 'cfg.np.where( (bandX >= ' + str(Xmin) + ') & (bandX <= ' + str(Xmax) + ') & (bandY >= ' + str(Ymin) + ') & (bandY <= ' + str(Ymax) + '), ' + str(list[1]) + ', '
				condit2 = condit2 + ')'
		condit1 = condit1[:-2] + ', ' + str(nodataValue) + condit2
		try:	
			algArray = eval(condit1)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 0
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
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
				condit1 = 'cfg.np.where( (bandX >= ' + str(Xmin) + ') & (bandX <= ' + str(Xmax) + ') & (bandY >= ' + str(Ymin) + ') & (bandY <= ' + str(Ymax) + '), ' + str(list[1]) + ', ' + str(nodataValue) + ')'
				conditions.append(condit1)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		return conditions
	
	# get UID
	def signatureID(self):
		dT = cfg.utls.getTime()
		r = cfg.randomSCP.randint(100,999)
		i = dT + "_" + str(r)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ID" + str(i))
		return i
		
	# calculate unique CID and MCID list
	def calculateUnique_CID_MCID(self):
		unique = []
		try:
			if len(list(cfg.signIDs.values())) > 0:
				for i in list(cfg.signIDs.values()):
					unique.append(str(cfg.signList["CLASSID_" + str(i)]) + "-" + str(cfg.signList["MACROCLASSID_" + str(i)]))
				l = set(unique)
				listA = cfg.utls.uniqueToOrderedList(l)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " unique" + str(list))
				return listA
			else:
				return 'No'
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
			
	# find DNmin in raster for DOS1
	def findDNmin(self, inputRaster, noDataVal = None):
		cfg.parallelArrayDict = {}
		o = cfg.utls.multiProcessRaster(rasterPath = inputRaster, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = noDataVal, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'DOS1 calculation'), deleteArray = 'No', parallel = cfg.parallelArray)
		DNlist = []
		for x in sorted(cfg.parallelArrayDict):
			rasterBandUniqueVal = {}
			DNm = 0
			try:
				for ar in cfg.parallelArrayDict[x]:
					values = ar[0, ::]
					count = ar[1, ::]
					val = zip(values, count)
					uniqueVal = cfg.counterSCP(dict(val))
					oldUniqueVal = cfg.counterSCP(rasterBandUniqueVal)
					rasterBandUniqueVal = uniqueVal + oldUniqueVal
					rasterBandUniqueVal.pop(noDataVal, None)
			except:
				return 'No'
			sumTot = sum(rasterBandUniqueVal.values())
			mina = min(rasterBandUniqueVal.keys())
			pT1pc = sumTot * 0.0001
			newSum = 0
			for i in sorted(rasterBandUniqueVal):
				DNm = i
				newSum = newSum + rasterBandUniqueVal[i]
				if newSum >= pT1pc:
					DNm = i
					break
			DNlist.append(DNm)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' DNlist ' + str(DNlist))
		return DNlist
			
	# unique CID and MCID list to ordered list
	def uniqueToOrderedList(self, uniqueList):
		list = []
		for i in uniqueList:
			v = i.split('-')
			list.append([int(v[0]), int(v[1])])
		sortedList = sorted(list, key=lambda list: (list[0], list[1]))
		return sortedList
			
	# calculate block size
	def calculateBlockSize(self, bandNumber):
		mem = cfg.RAMValue
		b = int((mem / (cfg.arrayUnitMemory * bandNumber ))**.5)
		# set system memory max
		if cfg.sysSCP64bit == 'No' and b > 2500:
			b = 2500
		# check memory
		try:
			a = cfg.np.zeros((b, b, bandNumber), dtype = cfg.np.float32)
		except:
			for i in reversed(list(range(128, mem, int(mem/10)))):
				try:
					b = int((i / (cfg.arrayUnitMemory * bandNumber ))**.5)
					# set system memory max
					if cfg.sysSCP64bit == 'No' and b > 2500:
						b = 2500
					a = cfg.np.zeros((b, b, bandNumber), dtype = cfg.np.float32)
					size = a.nbytes / 1048576
					cfg.ui.RAM_spinBox.setValue(size * bandNumber)
					cfg.mx.msgWar11()
					break
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "block = " + str(b))
		return b
	
	# check band set and create band set list
	def checkBandSet(self, bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		ck = 'Yes'
		# list of bands for algorithm
		cfg.bndSetLst = []
		for x in range(0, len(cfg.bandSetsList[bandSetNumber][3])):
			b = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][3][x], 'Yes')
			if b is not None:
				ql = cfg.utls.layerSource(b)
				cfg.bndSetLst.append(ql)
			else:
				ck = 'No'
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' raster is not loaded: ' + str(cfg.bandSetsList[bandSetNumber][3][x]))
				return ck
		return ck
		
	# check image Band set and create band set list
	def checkImageBandSet(self, bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		ck = 'Yes'
		# list of bands for algorithm
		cfg.bndSetLst = []
		b = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
		for x in range(0, len(cfg.bandSetsList[bandSetNumber][3])):			
			if b is not None:
				ql = cfg.utls.layerSource(b)
				cfg.bndSetLst.append(ql)
			else:
				ck = 'No'
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " raster is not loaded: " + str(cfg.bandSetsList[bandSetNumber][3][x]))
				return ck
		return ck

	# check if the clicked point is inside the image
	def checkPointImage(self, imageName, point, quiet = 'No', bandSetNumber = None, pointCoordinates = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		# band set
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			try:
				imageName = cfg.bandSetsList[bandSetNumber][3][0]
			except:
				cfg.mx.msgWar25(str(bandSetNumber + 1))
				return 'No'
			# image CRS
			bN0 = cfg.utls.selectLayerbyName(imageName, 'Yes')
			iCrs = self.getCrs(bN0)
			if iCrs is None:
				if pointCoordinates is not None:
					iCrs = pointCoordinates
					pCrs = iCrs
				else:
					iCrs = cfg.utls.getQGISCrs()
					pCrs = iCrs
			else:
				if pointCoordinates is not None:
					pCrs = pointCoordinates
				else:
					# projection of input point from project's crs to raster's crs
					pCrs = cfg.utls.getQGISCrs()
				if pCrs != iCrs:
					try:
						point = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
						if point is False:
							cfg.pntCheck = 'No'
							cfg.utls.setQGISCrs(iCrs)
							return 'No'
					# Error latitude or longitude exceeded limits
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
						crs = None
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Error') + ': latitude or longitude exceeded limits' + 'project crs: ' + str(pCrs.toProj4()) + ' - raster ' + str(imageName) + ' crs: ' + str(iCrs.toProj4()))
						cfg.pntCheck = 'No'
						return 'No'
			# workaround coordinates issue
			cfg.lstPnt = cfg.qgisCoreSCP.QgsPointXY(point.x() / float(1), point.y() / float(1))
			pX = point.x()
			pY = point.y()
			i = cfg.utls.selectLayerbyName(imageName, 'Yes')
			if i is not None:
				# Point Check	
				cfg.pntCheck = None
				if pX > i.extent().xMaximum() or pX < i.extent().xMinimum() or pY > i.extent().yMaximum() or pY < i.extent().yMinimum() :
					if quiet == 'No':
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'point outside the image area')
						cfg.mx.msg6()
					cfg.pntCheck = 'No'
				else :
					cfg.pntCheck = 'Yes'
					return cfg.lstPnt
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image missing')
				if quiet == 'No':
					cfg.mx.msg4()
					cfg.pntCheck = 'No'
		else:
			if cfg.utls.selectLayerbyName(imageName, 'Yes') is None:
				if quiet == 'No':
					cfg.mx.msg4()
				self.pntROI = None
				cfg.pntCheck = 'No'
			else:
				# image CRS
				bN0 = cfg.utls.selectLayerbyName(imageName, 'Yes')
				iCrs = self.getCrs(bN0)
				if iCrs is None:
					iCrs = None
				else:
					if pointCoordinates is not None:
						pCrs = pointCoordinates
					else:
						# projection of input point from project's crs to raster's crs
						pCrs = cfg.utls.getQGISCrs()
					if pCrs != iCrs:
						try:
							point = cfg.utls.projectPointCoordinates(point, pCrs, iCrs)
							if point is False:
								cfg.pntCheck = 'No'
								cfg.utls.setQGISCrs(iCrs)
								return 'No'
						# Error latitude or longitude exceeded limits
						except Exception as err:
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
							crs = None
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Error') + ': latitude or longitude exceeded limits')
							cfg.pntCheck = 'No'
							return 'No'
				# workaround coordinates issue
				if quiet == 'No':
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'project crs: ' + str(pCrs.toProj4()) + ' - raster ' + str(imageName) + ' crs: ' + str(iCrs.toProj4()))
				cfg.lstPnt = cfg.qgisCoreSCP.QgsPointXY(point.x() / float(1), point.y() / float(1))
				pX = point.x()
				pY = point.y()
				i = cfg.utls.selectLayerbyName(imageName, 'Yes')
				# Point Check	
				cfg.pntCheck = None
				if pX > i.extent().xMaximum() or pX < i.extent().xMinimum() or pY > i.extent().yMaximum() or pY < i.extent().yMinimum() :
					if quiet == 'No':
						cfg.mx.msg6()
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "point outside the image area")
					cfg.pntCheck = 'No'
				else :
					cfg.pntCheck = 'Yes'
					return cfg.lstPnt
	
	# create temporary raster list
	def createTempRasterList(self, rasterNumber):
		oM = []
		dT = cfg.utls.getTime()
		r = cfg.randomSCP.randint(0,1000)
		for t in range(0, rasterNumber):
			# date time for temp name
			tPMD = cfg.osSCP.path.join(cfg.tmpDir, dT + str(r) + str(t) + '_temp.tif')
			oM.append(tPMD)
		return oM
		
	# create temporary raster path
	def createTempRasterPath(self, extension, name = '_temp'):
		r = cfg.randomSCP.randint(0,1000)
		dT = cfg.utls.getTime()
		tPMD = cfg.tmpDir + '/' + dT + str(r) + name + '.' + extension
		return tPMD
		
	# create temporary raster path
	def createTempRasterPathBatch(self, name, extension):
		tPMD = cfg.tmpDir + '/' + name + '.' + extension
		return tPMD
		
	# create temporary virtual raster
	def createTempVirtualRaster(self, inputRasterList, bandNumberList = 'No', quiet = 'No', NoDataVal = 'No', relativeToVRT = 0, projection = 'No', intersection = 'Yes', boxCoordList = None, xyResList = None, aster = 'No'):
		r = cfg.randomSCP.randint(0,1000)
		# date time for temp name
		dT = cfg.utls.getTime()
		tPMN1 = cfg.tmpVrtNm + '.vrt'
		tPMD1 = cfg.tmpDir + '/' + dT + str(r) + tPMN1
		# create virtual raster
		output = cfg.utls.createVirtualRaster(inputRasterList, tPMD1, bandNumberList, quiet, NoDataVal, relativeToVRT, projection, intersection, boxCoordList, xyResList, aster)
		return output
				
	# create virtual raster with Python
	def createVirtualRaster(self, inputRasterList, output, bandNumberList = 'No', quiet = 'No', NoDataVal = 'No', relativeToVRT = 0, projection = 'No', intersection = 'Yes', boxCoordList = None, xyResList = None, aster = 'No'):
		# create virtual raster
		drv = cfg.gdalSCP.GetDriverByName('vrt')
		rXList = []
		rYList = []
		topList = []
		leftList = []
		rightList = []
		bottomList = []
		pXSizeList = []
		pYSizeList = []
		epsgList = []
		for b in inputRasterList:
			gdalRaster = cfg.gdalSCP.Open(b, cfg.gdalSCP.GA_ReadOnly)
			try:
				gt = gdalRaster.GetGeoTransform()
				if projection != 'No':
					rP = projection
				else:
					rP = gdalRaster.GetProjection()
				if rP == '':
					cfg.mx.msgErr47()
					return 'Yes'
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))	
				return 'Yes'
			# check projections
			try:
				if rP is not None:
					epsgList.append(rP)
				else:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rP is None ' + str(rP))
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))	
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
		# check projections
		epsgListI = list(set(epsgList))
		rEPSG = cfg.osrSCP.SpatialReference()
		rEPSG.ImportFromWkt(epsgListI[0])
		for epsg in epsgListI:
			vEPSG = cfg.osrSCP.SpatialReference()
			vEPSG.ImportFromWkt(epsg)
			if vEPSG.IsSame(rEPSG) != 1:
				cfg.mx.msgErr60()
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
		if xyResList is not None:
			pXSize = xyResList[0]
			pYSize = xyResList[1]
		if boxCoordList is not None:
			try:
				override = boxCoordList[4]
				if override == 'Yes':
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
		if xyResList is not None:
			iLeft = xyResList[2]
			iTop = xyResList[3]
			iRight = xyResList[4]
			iBottom = xyResList[5]
		# number of x pixels
		if intersection == 'Yes':
			rX = abs(int(round((xRight - xLeft) / pXSize)))
			rY = abs(int(round((xTop - xBottom) / pYSize)))
		else:
			rX = abs(int(round((iRight - iLeft) / pXSize)))
			rY = abs(int(round((iTop - iBottom) / pYSize)))
		# create virtual raster
		vRast = drv.Create(output, rX, rY, 0)
		# set raster projection from reference intersection
		if intersection == 'Yes':
			vRast.SetGeoTransform((xLeft, pXSize, 0, xTop, 0, -pYSize))
		else:
			vRast.SetGeoTransform((iLeft, pXSize, 0, iTop, 0, -pYSize))
		vRast.SetProjection(rP)
		if len(inputRasterList) == 1 and bandNumberList != 'No':
			x = 0
			gdalRaster2 = cfg.gdalSCP.Open(b, cfg.gdalSCP.GA_ReadOnly)
			try:
				for b in bandNumberList:
					gBand2 = gdalRaster2.GetRasterBand(int(b))
					offs = gBand2.GetOffset()
					scl = gBand2.GetScale()
					noData = gBand2.GetNoDataValue()
					if noData is None or str(noData) == 'nan':
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
					rX2 = int(round(gdalRaster2.RasterXSize * pX / pXSize))
					# number of y pixels
					rY2 = int(round(gdalRaster2.RasterYSize * pY / pYSize))
					# offset
					if intersection == 'Yes':
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
						if override == 'Yes':
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
					# check path
					source_path = inputRasterList[0]
					try:
						source_path = source_path
					except:
						pass
					# set metadata xml
					xml = '''
					<SimpleSource>
					  <SourceFilename relativeToVRT='%i'>%s</SourceFilename>
					  <SourceBand>%i</SourceBand>
					  <SourceProperties RasterXSize='%i' RasterYSize='%i' DataType=%s BlockXSize='%i' BlockYSize='%i' />
					  <SrcRect xOff='%i' yOff='%i' xSize='%i' ySize='%i' />
					  <DstRect xOff='%i' yOff='%i' xSize='%i' ySize='%i' />
					  <NODATA>%i</NODATA>
					</SimpleSource>
					'''
					source = xml % (relativeToVRT, source_path, bandNumber, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, 'Float32', x_block, y_block, xoffX, xoffY, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, offX, offY, rX2, rY2, noData)
					band.SetMetadataItem('SimpleSource', source, 'new_vrt_sources')
					if NoDataVal == 'Yes':
						band.SetNoDataValue(noData)	
					elif NoDataVal != 'No':
						band.SetNoDataValue(NoDataVal)
					if offs is not None:
						o = band.SetOffset(offs)
					if scl is not None:
						s = band.SetScale(scl)
					band = None
					gBand2 = None
					x = x + 1
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			gdalRaster2 = None
		else:
			x = 0
			for b in inputRasterList:
				gdalRaster2 = cfg.gdalSCP.Open(b, cfg.gdalSCP.GA_ReadOnly)
				gdalBandNumber = gdalRaster2.RasterCount
				for bb in range(1, gdalBandNumber + 1):
					gBand2 = gdalRaster2.GetRasterBand(bb)
					offs = gBand2.GetOffset()
					scl = gBand2.GetScale()
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
					rX2 = int(round(gdalRaster2.RasterXSize * pX / pXSize))
					# number of y pixels
					rY2 = int(round(gdalRaster2.RasterYSize * pY / pYSize))
					# offset
					if intersection == 'Yes':
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
						if override == 'Yes':
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
						errorCheck = 'Yes'
						if bandNumberList == 'No':
							bandNumber = 1
						else:
							bandNumber = bandNumberList[x]
						errorCheck = 'No'	
						band = vRast.GetRasterBand(x + 1)
						bsize = band.GetBlockSize()
						x_block = bsize[0]
						y_block = bsize[1]
						# check path
						source_path = b.replace('//', '/')
						try:
							source_path = source_path
						except:
							pass
						# set metadata xml
						xml = '''
						<SimpleSource>
						  <SourceFilename relativeToVRT='%i'>%s</SourceFilename>
						  <SourceBand>%i</SourceBand>
						  <SourceProperties RasterXSize='%i' RasterYSize='%i' DataType=%s BlockXSize='%i' BlockYSize='%i' />
						  <SrcRect xOff='%i' yOff='%i' xSize='%i' ySize='%i' />
						  <DstRect xOff='%i' yOff='%i' xSize='%i' ySize='%i' />
						  <NODATA>%i</NODATA>
						</SimpleSource>
						'''
						if aster == 'No':
							source = xml % (relativeToVRT, source_path, bandNumber, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, 'Float32', x_block, y_block, xoffX, xoffY, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, offX, offY, rX2, rY2, noData)
						else:
							source = xml % (relativeToVRT, source_path, bandNumber, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, 'Float32', x_block, y_block, xoffX, xoffY, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, xoffX, xoffY, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, noData)
						band.SetMetadataItem('SimpleSource', source, 'new_vrt_sources')
						if NoDataVal == 'Yes':
							band.SetNoDataValue(noData)	
						elif NoDataVal != 'No':
							band.SetNoDataValue(NoDataVal)
						if offs is not None:
							o = band.SetOffset(offs)
						if scl is not None:
							s = band.SetScale(scl)
						band = None
						x = x + 1
					except Exception as err:
						if errorCheck == 'No':
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				gdalRaster2 = None
		vRast = None
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'virtual raster: ' + str(output))
		return str(output)
		
	# simplified virtual raster creation for mosaic
	def createVirtualRaster2(self, inputRasterList, output, bandNumberList = None, NoDataValue = 'No', relativeToVRT = 0, intersection = 'No', extentList = None, dataType = None):
		lefts = []
		rights = []
		tops = []
		bottoms = []
		pXSizes = []
		pYSizes = []
		for i in inputRasterList:
			# raster extent and pixel size
			left, right, top, bottom, pX, pY, rP, unit = cfg.utls.imageGeoTransform(i)
			lefts.append(left)
			rights.append(right)
			tops.append(top)
			bottoms.append(bottom)
			pXSizes.append(pX)
			pYSizes.append(pY)
		if intersection == 'No':
			iLeft = min(lefts)
			iTop = max(tops)
			iRight = max(rights)
			iBottom = min(bottoms)
		else:
			iLeft = max(lefts)
			iTop = min(tops)
			iRight = min(rights)
			iBottom = max(bottoms)
		pXSize = min(pXSizes)
		pYSize = min(pYSizes)
		# create virtual raster
		drv = cfg.gdalSCP.GetDriverByName('vrt')
		# number of x pixels
		rX = abs(int(round((iRight - iLeft) / pXSize)))
		rY = abs(int(round((iTop - iBottom) / pYSize)))
		# create virtual raster
		vRast = drv.Create(output, rX, rY, 0)
		# set raster projection from reference intersection
		vRast.SetGeoTransform((iLeft, pXSize, 0, iTop, 0, -pYSize))
		vRast.SetProjection(rP)
		if dataType is not None:
			try:
				format = eval('cfg.gdalSCP.GDT_' + dataType)
			except:
				format = cfg.gdalSCP.GDT_Float32
		else:
			dataType = 'Float32'
			format = cfg.gdalSCP.GDT_Float32
		vRast.AddBand(format)
		band = vRast.GetRasterBand(1)
		bsize = band.GetBlockSize()
		x_block = bsize[0]
		y_block = bsize[1]
		x = 0
		for b in range(0, len(inputRasterList)):
			if bandNumberList is None:
				bandNumber = 1
			else:
				bandNumber = bandNumberList[b]
			gdalRaster2 = cfg.gdalSCP.Open(inputRasterList[b], cfg.gdalSCP.GA_ReadOnly)
			gBand2 = gdalRaster2.GetRasterBand(bandNumber) 
			offs = gBand2.GetOffset()
			scl = gBand2.GetScale()
			noData = gBand2.GetNoDataValue()
			if noData is None:
				noData = NoDataValue
			gt = gdalRaster2.GetGeoTransform()
			pX =  abs(gt[1])
			pY = abs(gt[5])
			left = gt[0]
			top = gt[3]
			bsize2 = gBand2.GetBlockSize()
			x_block = bsize2[0]
			y_block = bsize2[1]
			# number of x pixels
			rX2 = int(round(gdalRaster2.RasterXSize * pX / pXSize))
			# number of y pixels
			rY2 = int(round(gdalRaster2.RasterYSize * pY / pYSize))
			# offset
			offX = abs(int(round((left - iLeft) / pXSize)))
			offY = abs(int(round((iTop - top) / pYSize)))
			xoffX = 0
			xoffY = 0
			gBand2 = None
			rX1 = gdalRaster2.RasterXSize
			rY1 = gdalRaster2.RasterYSize
			if extentList is not None:
				offX, offY, rX2, rY2 = extentList
				xoffX = offX
				xoffY = offY
				rX1 = rX2
				rY1 = rY2
			try:
				# check path
				source_path = inputRasterList[b].replace('//', '/')
				# set metadata xml
				xml = '''
				<SimpleSource>
				  <SourceFilename relativeToVRT="%i">%s</SourceFilename>
				  <SourceBand>%i</SourceBand>
				  <SourceProperties RasterXSize="%i" RasterYSize="%i" DataType=%s BlockXSize="%i" BlockYSize="%i" />
				  <SrcRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
				  <DstRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
				  <NODATA>%i</NODATA>
				</SimpleSource>
				'''
				source = xml % (relativeToVRT, source_path, bandNumber, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, dataType, x_block, y_block, xoffX, xoffY, rX1, rY1, offX, offY, rX2, rY2, noData)
				band.SetMetadataItem('SimpleSource', source, 'new_vrt_sources')
				if NoDataValue == 'Yes':
					band.SetNoDataValue(noData)	
				elif NoDataValue != 'No':
					band.SetNoDataValue(NoDataValue)
				x = x + 1
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			gdalRaster2 = None
		if offs is not None:
			o = band.SetOffset(offs)
		if scl is not None:
			s = band.SetScale(scl)
		band = None
		vRast = None
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'virtual raster: ' + str(output))
		return str(output)
		
	# simplified virtual raster creation
	def createVirtualRaster3(self, inputRasterList, output, bandNumberList = None, NoDataValue = 'No', relativeToVRT = 0, intersection = 'No', extentList = None):
		lefts = []
		rights = []
		tops = []
		bottoms = []
		pXSizes = []
		pYSizes = []
		for i in inputRasterList:
			# raster extent and pixel size
			left, right, top, bottom, pX, pY, rP, unit = cfg.utls.imageGeoTransform(i)
			lefts.append(left)
			rights.append(right)
			tops.append(top)
			bottoms.append(bottom)
			pXSizes.append(pX)
			pYSizes.append(pY)
		if intersection == 'No':
			iLeft = min(lefts)
			iTop = max(tops)
			iRight = max(rights)
			iBottom = min(bottoms)
		else:
			iLeft = max(lefts)
			iTop = min(tops)
			iRight = min(rights)
			iBottom = max(bottoms)
		pXSize = min(pXSizes)
		pYSize = min(pYSizes)
		if extentList is not None:
			iLeft, iRight, iTop, iBottom = extentList
		# create virtual raster
		drv = cfg.gdalSCP.GetDriverByName('vrt')
		# number of x pixels
		rX = abs(int(round((iRight - iLeft) / pXSize)))
		rY = abs(int(round((iTop - iBottom) / pYSize)))
		# create virtual raster
		vRast = drv.Create(output, rX, rY, 0)
		# set raster projection from reference intersection
		vRast.SetGeoTransform((iLeft, pXSize, 0, iTop, 0, -pYSize))
		vRast.SetProjection(rP)
		x = 0
		for b in range(0, len(inputRasterList)):
			if bandNumberList is None:
				bandNumber = 1
			else:
				bandNumber = bandNumberList[b]
			gdalRaster2 = cfg.gdalSCP.Open(inputRasterList[b], cfg.gdalSCP.GA_ReadOnly)
			gBand2 = gdalRaster2.GetRasterBand(bandNumber) 
			noData = gBand2.GetNoDataValue()
			if noData is None:
				noData = NoDataValue
			gt = gdalRaster2.GetGeoTransform()
			pX =  abs(gt[1])
			pY = abs(gt[5])
			left = gt[0]
			top = gt[3]
			bsize2 = gBand2.GetBlockSize()
			x_block = bsize2[0]
			y_block = bsize2[1]
			# number of x pixels
			rX2 = int(round(gdalRaster2.RasterXSize * pX / pXSize))
			# number of y pixels
			rY2 = int(round(gdalRaster2.RasterYSize * pY / pYSize))
			# offset
			offX = abs(int(round((left - iLeft) / pXSize)))
			offY = abs(int(round((iTop - top) / pYSize)))
			xoffX = 0
			xoffY = 0
			gBand2 = None
			vRast.AddBand(cfg.gdalSCP.GDT_Float32)
			try:
				band = vRast.GetRasterBand(x + 1)
				bsize = band.GetBlockSize()
				x_block = bsize[0]
				y_block = bsize[1]
				# check path
				source_path = inputRasterList[b].replace("//", "/")
				# set metadata xml
				xml = '''
				<SimpleSource>
				  <SourceFilename relativeToVRT="%i">%s</SourceFilename>
				  <SourceBand>%i</SourceBand>
				  <SourceProperties RasterXSize="%i" RasterYSize="%i" DataType=%s BlockXSize="%i" BlockYSize="%i" />
				  <SrcRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
				  <DstRect xOff="%i" yOff="%i" xSize="%i" ySize="%i" />
				  <NODATA>%i</NODATA>
				</SimpleSource>
				'''
				source = xml % (relativeToVRT, source_path, bandNumber, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, "Float32", x_block, y_block, xoffX, xoffY, gdalRaster2.RasterXSize, gdalRaster2.RasterYSize, offX, offY, rX2, rY2, noData)
				band.SetMetadataItem("SimpleSource", source, "new_vrt_sources")
				if NoDataValue == 'Yes':
					band.SetNoDataValue(noData)	
				elif NoDataValue != 'No':
					band.SetNoDataValue(NoDataValue)
				band = None
				x = x + 1
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			gdalRaster2 = None
		vRast = None
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "virtual raster: " + str(output))
		return str(output)
		
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
			lX = list(range(0, rX, blockSizeX))
			lY = list(range(0, rY, blockSizeY))
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
				lX = list(range(sX, eX, blockSizeX))
				lY = list(range(sY, eY, blockSizeY))
			else:
				lX = [sX]
				lY = [sY]
			# preview range blocks
			pX = list(range(0, previewSize, blockSizeX))
			pY = list(range(0, previewSize, blockSizeY))
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
		try:
			o = gdalBand.GetOffset()
			s = gdalBand.GetScale()
			if o is None:
				o = 0.0
			if s is None:
				s = 1.0
		except:
			o = 0.0
			s = 1.0
		try:
			a = gdalBand.ReadAsArray(pixelStartColumn, pixelStartRow, blockColumns, blockRow)*s+o
		except:
			return None
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
		
	# write an array to band
	def writeRasterBlock(self, gdalRaster, bandNumber, dataArray, pixelStartColumn, pixelStartRow, nodataValue=None):
		b = gdalRaster.GetRasterBand(bandNumber)
		y, x = dataArray.shape
		b.WriteRaster(pixelStartColumn, pixelStartRow, x, y, dataArray.tostring())
		if nodataValue is not None:
			b.SetNoDataValue(nodataValue)
		b.FlushCache()
		b = None
	
	# create raster from another raster
	def createRasterFromReferenceMultiprocess(self, raster, bandNumber, outputRasterList, nodataValue = None, driver = 'GTiff', format = 'Float32', compress = 'No', compressFormat = 'DEFLATE21', projection = None, geotransform = None, constantValue = None, xSize = None, ySize = None):
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'format ' + str(format) )
		# open input with GDAL
		gdalRasterRef = cfg.gdalSCP.Open(raster, cfg.gdalSCP.GA_ReadOnly)
		if format == 'Float64':
			format = cfg.gdalSCP.GDT_Float64
		elif format == 'Float32':
			format = cfg.gdalSCP.GDT_Float32
		elif format == 'Int32':
			format = cfg.gdalSCP.GDT_Int32
		elif format == 'UInt32':
			format = cfg.gdalSCP.GDT_UInt32
		elif format == 'Int16':
			format = cfg.gdalSCP.GDT_Int16
		elif format == 'UInt16':
			format = cfg.gdalSCP.GDT_UInt16
		elif format == 'Byte':
			format = cfg.gdalSCP.GDT_Byte
		for o in outputRasterList:
			if driver == 'GTiff':
				if o.lower().endswith('.tif'):
					pass
				else:
					o = o + '.tif'
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
			if xSize is None:
				c = gdalRasterRef.RasterXSize
			else:
				c = xSize
			if ySize is None:
				r = gdalRasterRef.RasterYSize
			else:
				r = ySize
			if compress == 'No':
				oR = tD.Create(o, c, r, bandNumber, format)
			elif compress == 'DEFLATE21':
				oR = tD.Create(o, c, r, bandNumber, format, options = ['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=1'])
			else:
				oR = tD.Create(o, c, r, bandNumber, format, ['COMPRESS=' + compressFormat])
			if oR is None:
				# logger
				cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error GDAL raster')
			# set raster projection from reference
			oR.SetGeoTransform(rGT)
			oR.SetProjection(rP)
			if nodataValue is not None:
				for x in range(1, bandNumber+1):
					b = oR.GetRasterBand(x)
					b.SetNoDataValue(nodataValue)
					b.Fill(nodataValue)
					b = None
			if constantValue is not None:
				for x in range(1, bandNumber+1):
					b = oR.GetRasterBand(x)
					b.Fill(constantValue)
					b = None
			oR = None
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'raster ' + str(outputRasterList))
		return outputRasterList
		
	# create raster from another raster
	def createRasterFromReference(self, gdalRasterRef, bandNumber, outputRasterList, nodataValue = None, driver = 'GTiff', format = 'Float32', previewSize = 0, previewPoint = None, compress = 'No', compressFormat = 'DEFLATE21', projection = None, geotransform = None, constantValue = None):
		oRL = []
		if format == 'Float64':
			format = cfg.gdalSCP.GDT_Float64
		elif format == 'Float32':
			format = cfg.gdalSCP.GDT_Float32
		elif format == 'Int32':
			format = cfg.gdalSCP.GDT_Int32
		elif format == 'Int16':
			format = cfg.gdalSCP.GDT_Int16
		elif format == 'Byte':
			format = cfg.gdalSCP.GDT_Byte
		for o in outputRasterList:
			if driver == 'GTiff':
				if o.lower().endswith('.tif'):
					pass
				else:
					o = o + '.tif'
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
			if compress == 'No':
				oR = tD.Create(o, c, r, bandNumber, format)
			elif compress == 'DEFLATE21':
				oR = tD.Create(o, c, r, bandNumber, format, options = ['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=1'])
			else:
				oR = tD.Create(o, c, r, bandNumber, format, ['COMPRESS=' + compressFormat])
			if oR is None:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error GDAL raster')
				return 'No'
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
			if constantValue is not None:
				for x in range(1, bandNumber+1):
					b = oR.GetRasterBand(x)
					b.Fill(constantValue)
					b = None
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'raster ' + str(outputRasterList))
		return oRL
		
	# clip a raster using a shapefile
	def clipRasterByShapefile(self, shapefile, raster, outputRaster = None, outFormat = "GTiff"):
		# convert polygon to raster 
		tRxs = cfg.utls.createTempRasterPath('tif')
		burnValues = 1
		conversionType = None
		bbList = [raster]
		if cfg.osSCP.path.isfile(shapefile):
			check = cfg.utls.vectorToRaster(cfg.emptyFN, shapefile, cfg.emptyFN, tRxs, raster, conversionType, "GTiff", burnValues)
		else:
			return 'No'
		if check != 'No':
			dirPath = cfg.osSCP.path.dirname(outputRaster)
			outList = cfg.utls.clipRasterByRaster(bbList, tRxs, dirPath, outFormat, cfg.NoDataVal, progressMessage = None)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'shapefile ' + str(shapefile) + 'raster ' + str(raster) + 'outputRaster ' + str(outList[0]))
			return outList[0]
		else:
			return 'No'
		
	# clip raster with another raster
	def clipRasterByRaster(self, rasterClippedList, rasterClipping, outputRasterDir = None, outFormat = 'GTiff', nodataVal = None, progressMessage = 'Clip', stats = None, parallelWritingCheck = None, outputNameRoot = None):
		tPMD = cfg.utls.createTempRasterPath('vrt')
		bList = rasterClippedList.copy()
		bList.append(rasterClipping)
		iBC = len(bList)
		# create band list of clipped bands and clipping band
		bandNumberList = []
		for cc in range(1, iBC + 1):
			bandNumberList.append(1)
		vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, 'Yes', 'Yes', 0)
		# open input with GDAL
		rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
		if rD is None:
			cfg.mx.msg4()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' None raster')
			cfg.uiUtls.removeProgressBar()
			cfg.cnvs.setRenderFlag(True)
			return 'No'
		try:
			# band list
			bL = cfg.utls.readAllBandsFromRaster(rD)
			bC = len(bL)
			functionList = []
			variableList = []
			varList = []
			for t in range(0, bC):
				varList.append('"im' + str(t)+ '"')
			for t in range(0, bC - 1):
				# output rasters
				e = str('"im' + str(t) + '" *  "im' + str(bC-1) + '"')
				functionList.append(e)
				variableList.append(varList)
			oM = cfg.utls.createTempRasterList(bC-1)
			oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0, None, 'No')
			# close GDAL rasters
			for b in range(0, len(oMR)):
				oMR[b] = None
			for b in range(0, len(bL)):
				bL[b] = None
			rD = None
			if stats is None:
				ffR = cfg.utls.calculateRaster
			else:
				ffR = cfg.utls.calculateRasterWithStats
			o = cfg.utls.multiProcessRaster(rasterPath = tPMD, functionBand = 'No', functionRaster = ffR, outputRasterList = oM, nodataValue = nodataVal, functionBandArgument = functionList, functionVariable = variableList, progressMessage = progressMessage, parallel = cfg.parallelRaster, skipSingleBand = 'Yes', parallelWritingCheck = parallelWritingCheck)
		# in case of errors
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		if outputRasterDir is None:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'raster ' + str(oM))
			return oM
		else:
			outList = []
			for cc in range(0, len(oM)):
				d = cfg.utls.fileName(rasterClippedList[cc])
				if outputNameRoot is None:
					t = ''
				else:
					t = outputNameRoot
				e = outputRasterDir.rstrip('/') + '/' + t + d
				outList.append(e)
				if str(e).lower().endswith('.tif'):
					pass
				else:
					e = e + '.tif'
				if cfg.rasterCompression != 'No':
					try:
						cfg.utls.GDALCopyRaster(oM[cc], e, 'GTiff', cfg.rasterCompression, 'LZW')
						cfg.osSCP.remove(oM[cc])
					except Exception as err:
						cfg.shutilSCP.copy(oM[cc], e)
						cfg.osSCP.remove(oM[cc])
						# logger
						if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				else:
					cfg.shutilSCP.move(oM[cc], e)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'raster ' + str(outList))
			return outList
		
	# find nearest value in list
	def findNearestValueinList(self, list, value, threshold):
		if len(list) > 0:
			arr = cfg.np.asarray(list)
			v = (cfg.np.abs(arr - value)).argmin()
			if cfg.np.abs(arr[v] - value) < threshold:
				return arr[v]
			else:
				return None
		else:
			return None
	
	# find band set number used for vegetation index calculation
	def findBandNumber(self, bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		cfg.REDBand = None
		cfg.NIRBand = None
		cfg.BLUEBand = None
		cfg.GREENBand = None
		cfg.SWIR1Band = None
		cfg.SWIR2Band = None
		try:
			cfg.bandSetsList[bandSetNumber][5]
		except:
			return 'No'
		if cfg.bandSetsList[bandSetNumber][5] != cfg.noUnit:
			if cfg.bandSetsList[bandSetNumber][5] == cfg.unitNano:
				SWIR1 = self.findNearestValueinList(list(cfg.bandSetsList[bandSetNumber][4]), cfg.SWIR1CenterBand*1000, cfg.SWIR1Threshold*1000)
				SWIR2 = self.findNearestValueinList(list(cfg.bandSetsList[bandSetNumber][4]), cfg.SWIR2CenterBand*1000, cfg.SWIR2Threshold*1000)
				RED = self.findNearestValueinList(list(cfg.bandSetsList[bandSetNumber][4]), cfg.REDCenterBand*1000, cfg.REDThreshold*1000)
				NIR = self.findNearestValueinList(list(cfg.bandSetsList[bandSetNumber][4]), cfg.NIRCenterBand*1000, cfg.NIRThreshold*1000)
				BLUE = self.findNearestValueinList(list(cfg.bandSetsList[bandSetNumber][4]), cfg.BLUECenterBand*1000, cfg.BLUEThreshold*1000)
				GREEN = self.findNearestValueinList(list(cfg.bandSetsList[bandSetNumber][4]), cfg.GREENCenterBand*1000, cfg.GREENThreshold*1000)
			elif cfg.bandSetsList[bandSetNumber][5] == cfg.unitMicro:
				SWIR1 = self.findNearestValueinList(list(cfg.bandSetsList[bandSetNumber][4]), cfg.SWIR1CenterBand, cfg.SWIR1Threshold)
				SWIR2 = self.findNearestValueinList(list(cfg.bandSetsList[bandSetNumber][4]), cfg.SWIR2CenterBand, cfg.SWIR2Threshold)
				RED = self.findNearestValueinList(cfg.bandSetsList[bandSetNumber][4], cfg.REDCenterBand, cfg.REDThreshold)
				NIR = self.findNearestValueinList(cfg.bandSetsList[bandSetNumber][4], cfg.NIRCenterBand, cfg.NIRThreshold)
				BLUE = self.findNearestValueinList(cfg.bandSetsList[bandSetNumber][4], cfg.BLUECenterBand, cfg.BLUEThreshold)
				GREEN = self.findNearestValueinList(cfg.bandSetsList[bandSetNumber][4], cfg.GREENCenterBand, cfg.GREENThreshold)
			if RED is not None:
				cfg.REDBand = cfg.bandSetsList[bandSetNumber][4].index(RED) + 1
			if NIR is not None:
				cfg.NIRBand = cfg.bandSetsList[bandSetNumber][4].index(NIR) + 1
			if BLUE is not None:
				cfg.BLUEBand = cfg.bandSetsList[bandSetNumber][4].index(BLUE) + 1
			if GREEN is not None:
				cfg.GREENBand = cfg.bandSetsList[bandSetNumber][4].index(GREEN) + 1
			if SWIR1 is not None:
				cfg.SWIR1Band = cfg.bandSetsList[bandSetNumber][4].index(SWIR1) + 1
			if SWIR2 is not None:
				cfg.SWIR2Band = cfg.bandSetsList[bandSetNumber][4].index(SWIR2) + 1
			return 'Yes'
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "RED =" + str(cfg.REDBand) + ", NIR =" + str(cfg.NIRBand) + ", BLUE =" + str(cfg.BLUEBand) + ", GREEN =" + str(cfg.GREENBand) + ", SWIR1 =" + str(cfg.SWIR1Band) + ", SWIR2 =" + str(cfg.SWIR2Band))
		
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
		if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
			if cfg.NIRBand is None or cfg.REDBand is None:
				return 'No'
			else:
				NIRRaster = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][int(cfg.NIRBand) - 1], 'Yes')	
				REDRaster = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][int(cfg.REDBand) - 1], 'Yes')	
				# open input with GDAL
				try:
					NIRr = cfg.gdalSCP.Open(cfg.utls.layerSource(NIRRaster), cfg.gdalSCP.GA_ReadOnly)
					REDr = cfg.gdalSCP.Open(cfg.utls.layerSource(REDRaster), cfg.gdalSCP.GA_ReadOnly)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					return 'No'
				NIRB = NIRr.GetRasterBand(1)
				REDB = REDr.GetRasterBand(1)
				geoT = NIRr.GetGeoTransform()
		else:
			inputRaster = cfg.utls.selectLayerbyName(imageName, 'Yes')	
			# open input with GDAL
			try:
				ql = cfg.utls.layerSource(inputRaster)
				rD = cfg.gdalSCP.Open(ql, cfg.gdalSCP.GA_ReadOnly)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
			if rD is None or cfg.NIRBand is None or cfg.REDBand is None:
				return 'No'
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
			NIR = self.readArrayBlock(NIRB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bandSetsList[cfg.bndSetNumber][6][0][int(cfg.NIRBand) - 1] + cfg.bandSetsList[cfg.bndSetNumber][6][1][int(cfg.NIRBand) - 1]
			RED = self.readArrayBlock(REDB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bandSetsList[cfg.bndSetNumber][6][0][int(cfg.REDBand) - 1] + cfg.bandSetsList[cfg.bndSetNumber][6][1][int(cfg.REDBand) - 1]
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			# close bands
			NIRB = None
			REDB = None
			# close raster
			rD = None
			return 'No'
		if NIR is not None and RED is not None:
			try:
				NDVI = self.calculateNDVI(float(NIR), float(RED))
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				# close bands
				NIRB = None
				REDB = None
				# close raster
				rD = None
				return 'No'
		# close bands
		NIRB = None
		REDB = None
		# close raster
		rD = None
		NIRr = None
		REDr = None
		try:
			return round(NDVI, 3)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No' 
		
	# EVI calculator from image
	def EVIcalculator(self, imageName, point):
		EVI = None
		# band set
		if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
			if cfg.NIRBand is None or cfg.REDBand is None or cfg.BLUEBand is None:
				return 'No'
			else:
				NIRRaster = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][int(cfg.NIRBand) - 1], 'Yes')	
				REDRaster = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][int(cfg.REDBand) - 1], 'Yes')
				BLUERaster = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][int(cfg.BLUEBand) - 1], 'Yes')
				# open input with GDAL
				try:
					NIRr = cfg.gdalSCP.Open(cfg.utls.layerSource(NIRRaster), cfg.gdalSCP.GA_ReadOnly)
					REDr = cfg.gdalSCP.Open(cfg.utls.layerSource(REDRaster), cfg.gdalSCP.GA_ReadOnly)
					BLUEr = cfg.gdalSCP.Open(cfg.utls.layerSource(BLUERaster), cfg.gdalSCP.GA_ReadOnly)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					return 'No'
				NIRB = NIRr.GetRasterBand(1)
				REDB = REDr.GetRasterBand(1)
				BLUEB = REDr.GetRasterBand(1)
				geoT = NIRr.GetGeoTransform()
		else:
			inputRaster = cfg.utls.selectLayerbyName(imageName, 'Yes')	
			# open input with GDAL
			try:
				ql = cfg.utls.layerSource(inputRaster)
				rD = cfg.gdalSCP.Open(ql, cfg.gdalSCP.GA_ReadOnly)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
			if rD is None or cfg.NIRBand is None or cfg.REDBand is None or cfg.BLUEBand is None:
				return 'No'
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
		NIR = self.readArrayBlock(NIRB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bandSetsList[cfg.bndSetNumber][6][0][int(cfg.NIRBand) - 1] + cfg.bandSetsList[cfg.bndSetNumber][6][1][int(cfg.NIRBand) - 1]
		RED = self.readArrayBlock(REDB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bandSetsList[cfg.bndSetNumber][6][0][int(cfg.REDBand) - 1] + cfg.bandSetsList[cfg.bndSetNumber][6][1][int(cfg.REDBand) - 1]
		BLUE = self.readArrayBlock(BLUEB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bandSetsList[cfg.bndSetNumber][6][0][int(cfg.BLUEBand) - 1] + cfg.bandSetsList[cfg.bndSetNumber][6][1][int(cfg.BLUEBand) - 1]
		if NIR is not None and RED is not None and BLUE is not None:
			if NIR <= 1 and RED <= 1 and BLUE <= 1:
				try:
					EVI = self.calculateEVI(float(NIR), float(RED), float(BLUE))
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					# close bands
					NIRB = None
					REDB = None
					BLUEB = None
					# close raster
					rD = None
					return 'No'
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
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No' 
			
	# custom index calculator from image
	def customIndexCalculator(self, imageName, point):
		customIndex = None
		geoT = None
		e = " " + cfg.uidc.custom_index_lineEdit.text() + " "
		dExpr = e
		for b in range(1, len(cfg.bandSetsList[cfg.bndSetNumber][3])+1):
			if "bandset#b" + str(b) in e:
				# band set
				if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
					raster = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][int(b) - 1], 'Yes')
					ql = cfg.utls.layerSource(raster)
					rRaster = cfg.gdalSCP.Open(ql, cfg.gdalSCP.GA_ReadOnly)
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
					val = self.readArrayBlock(rasterB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bandSetsList[cfg.bndSetNumber][6][0][int(b) - 1] + cfg.bandSetsList[cfg.bndSetNumber][6][1][int(b) - 1]					
					dExpr = dExpr.replace("bandset#b" + str(b), str(val[0,0]))
					# close bands
					rasterB = None
					# close raster
					rD = None
				else:
					inputRaster = cfg.utls.selectLayerbyName(imageName, 'Yes')	
					# open input with GDAL
					try:
						qll = cfg.utls.layerSource(inputRaster)
						rD = cfg.gdalSCP.Open(qll, cfg.gdalSCP.GA_ReadOnly)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
						return 'No'
					if rD is None or cfg.NIRBand is None or cfg.REDBand is None or cfg.BLUEBand is None or cfg.GREENBand is None:
						return 'No'
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
					val = self.readArrayBlock(rasterB, pixelStartColumn, pixelStartRow, 1, 1) * cfg.bandSetsList[cfg.bndSetNumber][6][0][int(b) - 1] + cfg.bandSetsList[cfg.bndSetNumber][6][1][int(b) - 1]
					dExpr = dExpr.replace("bandset#b" + str(b), str(val[0,0]))
					# close bands
					rasterB = None
					# close raster
					rD = None
		try:
			f = cfg.utls.replaceNumpyOperators(dExpr)
			customIndex = eval(f)
			return round(customIndex, 3)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No' 
		
	# copy a raster band from a multi band raster
	def getRasterBandByBandNumber(self, inputRaster, band, outputRaster, virtualRaster = 'No', GDALFormat = None, multiAddList = None):
		if virtualRaster == 'No':
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
			tD = cfg.gdalSCP.GetDriverByName('GTiff')
			iRB = rD.GetRasterBand(int(band))
			if GDALFormat is None:
				bDT = iRB.DataType
			else:
				if GDALFormat == 'Float64':
					bDT = cfg.gdalSCP.GDT_Float64
				elif GDALFormat == 'Float32':
					bDT = cfg.gdalSCP.GDT_Float32
			try:
				o = iRB.GetOffset()
				s = iRB.GetScale()
				if o is None:
					o = 0
				if s is None:
					s = 1
			except:
				o = 0
				s = 1
			a =  iRB.ReadAsArray()*s+o
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
			vrtCheck = cfg.utls.createVirtualRaster([inputRaster], outputRaster, [band], 'Yes', 'Yes', 'Yes')
			cfg.timeSCP.sleep(0.1)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "get band: " + str(band))
		
	# Split raster into single bands, and return a list of images
	def rasterToBands(self, rasterPath, outputFolder, outputName = None, progressBar = 'No', multiAddList = None, virtual = 'No'):
		try:
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
				if cfg.actionCheck == 'Yes':
					xB = outputFolder + '/' + name + '_B' + str(x) + '.tif'
					if multiAddList is not None:
						self.getRasterBandByBandNumber(rasterPath, x, xB, 'No', None, [multiAddList[0][x - 1], multiAddList[1][x - 1]])
					else:
						self.getRasterBandByBandNumber(rasterPath, x, xB, virtual, None)
					iL.append(xB)
					if progressBar == 'Yes':
						cfg.uiUtls.updateBar(progresStep * i)
						i = i + 1
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'raster: ' + str(rasterPath) + ' split to bands')
			return iL
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No' 
		
##################################
	''' Multiprocess functions '''
##################################

	# calculate raster
	def calculateRaster(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputRaster, functionBandArgument, functionVariableList, outputBandNumber):
		# create function
		b = 0
		f = functionBandArgument
		for i in functionVariableList:
			f = f.replace(i , ' rasterSCPArrayfunctionBand[::, ::,' + str(b) + '] ')
			b = b + 1
		# replace numpy operators
		f = cfg.utls.replaceNumpyOperators(f)	
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'f ' + str(f))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterSCPArrayfunctionBand shape' + str(rasterSCPArrayfunctionBand.shape))
		try:
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterSCPArrayfunctionBand ' + str(rasterSCPArrayfunctionBand[0, 0, 0]))
		except:
			pass
		# perform operation
		o = eval(f)
		# output raster
		oR = cfg.gdalSCP.Open(outputRaster, cfg.gdalSCP.GA_Update)
		cfg.utls.writeRasterBlock(oR, int(outputBandNumber), o, pixelStartColumn, pixelStartRow)
		o = None
		oR = None
		return outputRaster
		
	# calculate raster with stats
	def calculateRasterWithStats(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputRaster, functionBandArgument, functionVariableList, outputBandNumber):
		# create function
		b = 0
		f = functionBandArgument
		for i in functionVariableList:
			f = f.replace(i , ' rasterSCPArrayfunctionBand[::, ::,' + str(b) + '] ')
			b = b + 1
		# replace numpy operators
		f = cfg.utls.replaceNumpyOperators(f)
		# perform operation
		o = eval(f)
		# output raster
		oR = cfg.gdalSCP.Open(outputRaster, cfg.gdalSCP.GA_Update)
		cfg.utls.writeArrayBlock(oR, int(outputBandNumber), o, pixelStartColumn, pixelStartRow)
		min = cfg.np.nanmin(o)
		max = cfg.np.nanmax(o)
		mean = cfg.np.nanmean(o)
		stdDev = cfg.np.nanstd(o)
		array = o.flatten()
		count = cfg.np.count_nonzero(~cfg.np.isnan(o))
		o = None
		oR = None
		return [outputRaster, [min, max, mean, stdDev], array, count]
			
	# calculate raster unique values with sum
	def rasterUniqueValuesWithSum(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgumentNoData, functionVariableList, outputBandNumber):
		o = cfg.np.array(cfg.np.unique(rasterSCPArrayfunctionBand.ravel()[~cfg.np.isnan(rasterSCPArrayfunctionBand.ravel())], return_counts=True))
		return o
			
	# calculate raster unique values
	def rasterUniqueValues(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgumentNoData, functionVariableList, outputBandNumber):
		c = cfg.np.unique(rasterSCPArrayfunctionBand, axis=0)
		o = c[~cfg.np.isnan(c).any(axis=2)]
		if o.shape[0] > 0:
			c = cfg.np.unique(o, axis = 0)
		else:
			c = None
		return c
		
	# reclassify raster
	def reclassifyRaster(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):
		# raster array
		o = rasterSCPArrayfunctionBand.flatten()
		a = rasterSCPArrayfunctionBand.ravel()
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'reclassifyRaster ' )
		for i in functionBandArgument:
			# create condition
			try:
				o[a==int(i[0])] = float(i[1])
			except Exception as err:
				try:
					exp = 'o[' + i[0].replace(functionVariableList, 'a') + '] = float(i[1])'
					exec(exp)
				except Exception as err:
					# logger
					cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'error ' + str(err) )
					return 'No'
		return o.reshape(rasterSCPArrayfunctionBand.shape[0], rasterSCPArrayfunctionBand.shape[1])
			
	# cross raster
	def crossRasters(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionVariableList ' + str(functionVariableList) )
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionBandArgument ' + str(functionBandArgument) )
		o = eval(functionVariableList)
		a = cfg.np.copy(o)
		for i in functionBandArgument:
			# create condition
			o[a==int(i[0])] = int(i[1])
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'o ' + str(o) )
		return o
		
	# band calculation
	def bandCalculation(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):
		f = functionBandArgument
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'f ' + str(f) )
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterSCPArrayfunctionBand type ' + str(rasterSCPArrayfunctionBand.dtype) )
		# create function
		b = 0
		for i in functionVariableList:
			f = f.replace(i[0], ' rasterSCPArrayfunctionBand[::, ::,' + str(b) + '] ')
			f = f.replace(i[1], ' rasterSCPArrayfunctionBand[::, ::,' + str(b) + '] ')
			b = b + 1
		# replace numpy operators
		f = cfg.utls.replaceNumpyOperators(f)
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'f ' + str(f) )
		# perform operation
		try:
			o = eval(f)
		except Exception as err:
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'error ' + str(err) )
			return err
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'o ' + str(o) )
		# create array if not
		if not isinstance(o, cfg.np.ndarray):
			return 'No'
		# check nan
		#oo = cfg.np.nan_to_num(o) * 1.0
		#oo[cfg.np.isnan(o)] = cfg.np.nan
		#o = oo
		return o
								
	# multiple where scatter raster calculation 
	def scatterRasterMultipleWhere(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):
		for f in functionBandArgument:
			# create function
			f = f.replace('bandX', ' rasterSCPArrayfunctionBand[::, ::, 0] ')
			f = f.replace('bandY', ' rasterSCPArrayfunctionBand[::, ::, 1] ')
			# perform operation
			try:
				u = eval(f)
				o = cfg.np.where(u == -999, o, u)
			# first iteration
			except:
				try:
					o = eval(f)
				except Exception as err:
					# logger
					cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'error ' + str(err) )
					return 'No'
		return o
										
	#  band calculation scatter raster
	def scatterRasterBandCalculation(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):
		f = functionBandArgument
		# create function
		f = f.replace('bandX', ' rasterSCPArrayfunctionBand[::, ::, 0] ')
		f = f.replace('bandY', ' rasterSCPArrayfunctionBand[::, ::, 1] ')
		# perform operation
		o = eval(f)
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), f)
		return o

	# raster neighbor
	def rasterNeighbor(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):	
		structure = functionBandArgument
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'structure ' + str(structure))

		sizeJ = int(structure.shape[0]/2)
		sizeI = int(structure.shape[1]/2)
		# faster
		if 'nansum' in functionVariableList[0]:
			o = cfg.signalSCP.convolve2d(rasterSCPArrayfunctionBand[:,:,0], structure, 'same', boundary='fill', fillvalue=cfg.np.nan)
		else:
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'sizeI ' + str(sizeI))
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'sizeJ ' + str(sizeJ))
			A = cfg.np.zeros([rasterSCPArrayfunctionBand.shape[0], rasterSCPArrayfunctionBand.shape[1], structure.shape[0]*structure.shape[1]])
			A[:] = cfg.np.nan
			z = 0
			for i in range(-sizeI, sizeI+1):
				for j in range(-sizeJ, sizeJ+1):
					try:
						# logger
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), '[i,j] ' + str([i,j]) )
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'structure[j+sizeJ,i+sizeI] ' + str(structure[j+sizeJ,i+sizeI]) )
						if not cfg.np.isnan(structure[j+sizeJ,i+sizeI]):
							if i < 0:
								if j < 0:
									A[-j:,-i:,z] = rasterSCPArrayfunctionBand[0:j,0:i,0] * structure[j+sizeJ,i+sizeI]
								elif j == 0:
									A[:,-i:,z] = rasterSCPArrayfunctionBand[:,0:i,0] * structure[j+sizeJ,i+sizeI]
								else:
									A[0:-j,-i:,z] = rasterSCPArrayfunctionBand[j:,0:i,0] * structure[j+sizeJ,i+sizeI]
							elif i == 0:
								if j < 0:
									A[-j:,:,z] = rasterSCPArrayfunctionBand[0:j,:,0] * structure[j+sizeJ,i+sizeI]
								elif j == 0:
									A[:,:,z] = rasterSCPArrayfunctionBand[:,:,0] * structure[j+sizeJ,i+sizeI]
								else:
									A[0:-j,:,z] = rasterSCPArrayfunctionBand[j:,:,0] * structure[j+sizeJ,i+sizeI]
							else:
								if j < 0:
									A[-j:,0:-i,z] = rasterSCPArrayfunctionBand[0:j,i:,0] * structure[j+sizeJ,i+sizeI]
								elif j == 0:
									A[:,0:-i,z] = rasterSCPArrayfunctionBand[:,i:,0] * structure[j+sizeJ,i+sizeI]
								else:
									A[0:-j,0:-i,z] = rasterSCPArrayfunctionBand[j:,i:,0] * structure[j+sizeJ,i+sizeI]
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'A[:,:,z] ' + str(A[0,0,z]) )	
							z = z+1
					except:
						pass
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'A[0,0,:] ' + str(A[0,0,:]) )	
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionVariableList ' + str(functionVariableList[0]) )
			o = eval(functionVariableList[0])
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'o ' + str(o) )
		return o
		
	# raster erosion
	def rasterErosion(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):	
		A = rasterSCPArrayfunctionBand[::, ::, 0]
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
			o = cfg.np.where((R * D * cfg.np.where(cfg.np.max(Z, axis = 2) > 0, 1, 0) == 1), maxA, A)
		except Exception as err:
			o = A
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'o ' + str(o) )
		return o
			
	# raster dilation
	def rasterDilation(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):
		A = rasterSCPArrayfunctionBand[::, ::, 0]
		B = functionBandArgument
		# value dictionary
		C={}
		for i in functionVariableList:
			C['arr_'+ str(i)] = cfg.signalSCP.convolve2d(cfg.np.where(A==i, 1,0), B, 'same')
		# core
		D = cfg.np.ones(A.shape)
		for v in functionVariableList:
			D[A == v] = 0
		# dilation
		o = cfg.np.copy(A)
		try:
			for v in functionVariableList:
				o[(D * C['arr_'+ str(v)]) > 0] = v
		except Exception as err:
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'o ' + str(o) )
		return o
		
	# calculate raster with stats
	def regionGrowingAlgMultiprocess(self, rasterSCPArrayfunctionBand, functionBandArgument, functionVariableList, outputArrayFile, outputBandNumber):
		# create function
		f = ' rasterSCPArrayfunctionBand[::, ::,' + str(functionBandArgument) + '] '
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'f  ' + str(f) )
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionVariableList  ' + str(functionVariableList) )
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterSCPArrayfunctionBand  ' + str(rasterSCPArrayfunctionBand.shape) )
		# perform operation
		array = eval(f)
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'array  ' + str(array) )
		seedX = functionVariableList[0]
		seedY = functionVariableList[1]
		spectralRange = functionVariableList[2]
		minimumSize = functionVariableList[3]
		sA = cfg.np.zeros(array.shape)
		seedV = array[seedY, seedX]
		# if nodata
		if cfg.np.sum(cfg.np.isnan(seedV)) > 0:
			return sA
		sA.fill(seedV)
		# difference array
		dA = abs(array - sA)
		# calculate minimum difference
		uDA = cfg.np.unique(dA)
		uDB = uDA[uDA > float(spectralRange)]
		uDA = cfg.np.insert(uDB, 0, float(spectralRange))
		rr = None
		for i in uDA:
			rL, num_features = cfg.labelSCP(dA <= i)
			# value of ROI seed
			rV = rL[seedY,seedX]
			rV_mask =(rL == rV)
			if rV != 0 and cfg.np.count_nonzero(rV_mask) >= minimumSize:
				rr = cfg.np.copy(rV_mask)
				break
		if rr is None and rV != 0 :
			rr = cfg.np.copy(rV_mask)
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rr.shape  ' + str(rr.shape) )
		return [rr]
		
	# replace numpy operators for expressions in Band calc
	def replaceOperatorNames(self, expression, nameList, bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		# variable bandset#b*
		if '"' + cfg.variableBandsetName + '#b*"' in expression:
			bandList = '['
			for b in range(1, len(cfg.bandSetsList[bandSetNumber][3])+1):
				bandList = bandList + '"' + cfg.variableBandsetName + '#b' + str(b) + '", '
			# if percentile
			perc = cfg.reSCP.findall(r'percentile\(#?(.*?)#?\)',expression.replace(' ', ''))
			for percX in perc:
				if '"' + cfg.variableBandsetName + '#b*"' in percX:
					percXS = percX.split(',')
					try:
						expression = expression.replace(percX, bandList[:-2] + '],' + percXS[1] + ', axis = 0')
					except:
						pass
			bandList = bandList[:-2] + '], axis = 0'
			expression = expression.replace('"' + cfg.variableBandsetName + '#b*"', bandList)
		# variable bandset*b1
		elif '"' + cfg.variableBandsetName + '*b' in expression:
			bandNums = cfg.reSCP.findall(cfg.variableBandsetName + r'\*b#?(.*?)#?"', expression)
			for parts in bandNums:
				try:
					numB = int(parts)
				except:
					return expression
				bandList = '['
				for c in range(1, len(cfg.bandSetsList) + 1):
					try:
						# check band
						cfg.bandSetsList[c-1][3][numB-1]
						bandList = bandList + '"' + cfg.variableBandsetName + str(c) + 'b' + str(numB) + '", '
					except:
						pass
				# if percentile
				perc = cfg.reSCP.findall(r'percentile\(#?(.*?)#?\)',expression)
				for percX in perc:
					if '"' + cfg.variableBandsetName + '*b' in percX:
						percXS = percX.split(',')
						try:
							expression = expression.replace(percX, bandList[:-2] + '],' + percXS[1] + ', axis = 0')
						except:
							pass
				bandList = bandList[:-2] + '], axis = 0'
				expression = expression.replace('"' + cfg.variableBandsetName + '*b' + str(numB) + '"', bandList)
		# variable bandset{1,2,3}b1
		elif '"' + cfg.variableBandsetName + '{' in expression:
			bandNums = cfg.reSCP.findall(cfg.variableBandsetName + '{(.*?)\"', expression)
			bsetList = []
			checkO = 'Yes'
			for parts in bandNums:
				partSplit = parts.split('}b')
				try:
					numB = int(partSplit[1])
				except:
					return expression
				foB = partSplit[0]
				dtList = []
				dtRList = []
				nBList = []
				if ':' in foB and ',' in foB:
					# list of ranges of dates
					try:
						lrg = foB.split(',')
						for lrgL in lrg:
							try:
								# range of numbers
								rg = lrgL.split(':')
								for nbRg in range(int(rg[0].strip()), int(rg[1].strip())+1):
									nBList.append(nbRg)
							except:
								try:
									# range of dates
									rg = lrgL.split(':')
									dtRList.append([cfg.datetimeSCP.datetime.strptime(rg[0].strip(), '%Y-%m-%d'), cfg.datetimeSCP.datetime.strptime(rg[1].strip(), '%Y-%m-%d')])
								except:
									pass
					except:
						checkO = 'No'
				else:
					try:		
						try:
							# range of numbers
							rg = foB.split(':')
							for nbRg in range(int(rg[0].strip()), int(rg[1].strip())+1):
								nBList.append(nbRg)
						except:
							# range of dates
							rg = foB.split(':')
							dtRList.append([cfg.datetimeSCP.datetime.strptime(rg[0].strip(), '%Y-%m-%d'), cfg.datetimeSCP.datetime.strptime(rg[1].strip(), '%Y-%m-%d')])
					except:
						# list of dates
						try:
							rg = foB.split(',')
							for rgL in rg:
								try:
									# number of band set
									nBList.append(int(rgL.strip()))
								except:
									# date of band sets
									dtList.append(rgL.strip())
						except:
							checkO = 'No'
				if checkO == 'Yes':
					# number of band set
					if len(nBList) > 0:
						for j in nBList:
							bsetList.append(j)
					# date of band set
					elif len(dtList) > 0:
						for j in range(0, len(cfg.bandSetsList)):
							if cfg.bandSetsList[j][9] in dtList:
								bsetList.append(j+1)
					# range of dates of band set
					else:
						for j in range(0, len(cfg.bandSetsList)):
							try:
								bD = cfg.datetimeSCP.datetime.strptime(cfg.bandSetsList[j][9], '%Y-%m-%d')
								for dStr in dtRList:
									if (bD >= dStr[0]) & (bD <= dStr[1]) is True:
										bsetList.append(j+1)
										break
							except:
								pass
				bandList = '['
				for c in bsetList:
					try:
						# check band
						cfg.bandSetsList[c-1][3][numB-1]
						bandList = bandList + '"' + cfg.variableBandsetName + str(c) + 'b' + str(numB) + '", '
					except:
						pass
				# if percentile
				perc = cfg.reSCP.findall(r'percentile\((.*?)\)',expression)
				for percX in perc:
					if '"' + cfg.variableBandsetName + '{' + parts in percX:
						percXS = percX.split('",')
						try:
							expression = expression.replace(percX, bandList[:-2] + '],' + percXS[1] + ', axis = 0')
						except:
							pass
				bandList = bandList[:-2] + '], axis = 0'
				expression = expression.replace('"' + cfg.variableBandsetName + '{' + parts + '"', bandList)
		# variable bandset1b*
		elif cfg.variableBandsetName in expression and 'b*"' in expression:
			for c in range(0, len(cfg.bandSetsList)): 
				bandList = '['
				if '"' + cfg.variableBandsetName + str(c + 1) + 'b*"' in expression:
					for b in range(1, len(cfg.bandSetsList[c][3])+1):
						bandList = bandList + '"' + cfg.variableBandsetName + str(c + 1) + 'b' + str(b) + '", '
					# if percentile
					perc = cfg.reSCP.findall(r'percentile\(#?(.*?)#?\)',expression)
					for percX in perc:
						if '"' + cfg.variableBandsetName in percX and 'b*"' in percX:
							percXS = percX.split(',')
							try:
								expression = expression.replace(percX, bandList[:-2] + "]," + percXS[1] + ", axis = 0")
							except:
								pass
					bandList = bandList[:-2] + '], axis = 0'
					expression = expression.replace('"' + cfg.variableBandsetName + str(c + 1) + 'b*"', bandList)
		if "nodata" in expression:
			# find all non-greedy expression
			g = cfg.reSCP.findall(r'nodata\(\"#?(.*?)#?\"\)',expression)
		else:
			return expression
		for l in g:
			name = l
			for i in nameList:
				if l == i[0].replace('"', ''):
					l = i[1].replace('"', '')
			if l in cfg.variableBlueName or l in cfg.variableRedName or l in cfg.variableNIRName or l in cfg.variableGreenName or l in cfg.variableSWIR1Name or l in cfg.variableSWIR2Name :
				if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
					name = '#' + name
					if '#' + l == cfg.variableRedName :
						bandNumber = ['', cfg.REDBand]
					elif '#' + l == cfg.variableGreenName :
						bandNumber = ['', cfg.GREENBand]
					elif '#' + l == cfg.variableNIRName :
						bandNumber = ['', cfg.NIRBand]
					elif '#' + l == cfg.variableBlueName :
						bandNumber = ['', cfg.BLUEBand]
					elif '#' + l == cfg.variableSWIR1Name :
						bandNumber = ['', cfg.SWIR1Band]
					elif '#' + l == cfg.variableSWIR2Name :
						bandNumber = ['', cfg.SWIR2Band]
					l = cfg.bandSetsList[bandSetNumber][3][int(bandNumber[1]) - 1]
				else:
					l = cfg.bandSetsList[bandSetNumber][8]
			# in case of bandset name
			for b in range(1, len(cfg.bandSetsList[bandSetNumber][3])+1):
				if cfg.variableBandsetName + '#b' + str(b) == l:
					# band set
					if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
						l = cfg.bandSetsList[bandSetNumber][3][int(b) - 1]
					else:
						l = cfg.bandSetsList[bandSetNumber][8]
					break
			for c in range(0, len(cfg.bandSetsList)):
				for b in range(0, len(cfg.bandSetsList[c][3])):
					if cfg.variableBandsetName + str(c + 1) + 'b' + str(b + 1) == l:
						# band set
						if cfg.bandSetsList[c][0] == 'Yes':
							l = cfg.bandSetsList[c][3][int(b)]
						else:
							l = cfg.bandSetsList[c][8]
						break
			name = '"' + name + '"'
			r = cfg.utls.selectLayerbyName(l, 'Yes')
			if r is not None:
				ql = cfg.utls.layerSource(r)
				nd = cfg.utls.imageNoDataValue(ql)
				expression = expression.replace('nodata(' + name + ')', str(nd))
		# find Nodata values
		return expression
		
	# replace numpy operators for expressions in Band calc
	def replaceNumpyOperators(self, expression):
		f = ' ' + expression + ' '
		f = f.replace(' np.', ' ' + cfg.numpyn)
		f = f.replace('~np.', ' ~' + cfg.numpyn)
		f = f.replace(' ln(', ' ' + cfg.logn + '(')
		f = f.replace(' ln (', ' ' + cfg.logn + '(')
		f = f.replace(' log10(', ' ' + cfg.log10 + '(')
		f = f.replace(' log10 (', ' ' + cfg.log10 + '(')
		f = f.replace(' sqrt(', ' ' + cfg.numpySqrt + '(')
		f = f.replace(' sqrt (', ' ' + cfg.numpySqrt + '(')
		f = f.replace(' cos(', ' ' + cfg.numpyCos+ '(')
		f = f.replace(' cos (', ' ' + cfg.numpyCos + '(')
		f = f.replace(' acos(', ' ' + cfg.numpyArcCos + '(')
		f = f.replace(' acos (', ' ' + cfg.numpyArcCos + '(')
		f = f.replace(' sin(', ' ' + cfg.numpySin + '(')
		f = f.replace(' sin (', ' ' + cfg.numpySin + '(')
		f = f.replace(' asin(', ' ' + cfg.numpyArcSin + '(')
		f = f.replace(' asin (', ' ' + cfg.numpyArcSin + '(')
		f = f.replace(' tan(', ' ' + cfg.numpyTan + '(')
		f = f.replace(' tan (', ' ' + cfg.numpyTan + '(')
		f = f.replace(' atan(', ' ' + cfg.numpyArcTan + '(')
		f = f.replace(' atan (', ' ' + cfg.numpyArcTan + '(')
		f = f.replace(' exp(', ' ' + cfg.numpyExp + '(')
		f = f.replace(' exp (', ' ' + cfg.numpyExp + '(')
		f = f.replace(' min(', ' ' + cfg.numpyAMin + '(')
		f = f.replace(' min (', ' ' + cfg.numpyAMin + '(')
		f = f.replace(' max(', ' ' + cfg.numpyAMax + '(')
		f = f.replace(' max (', ' ' + cfg.numpyAMax + '(')
		f = f.replace(' percentile(', ' ' + cfg.numpyPercentile + '(')
		f = f.replace(' percentile (', ' ' + cfg.numpyPercentile + '(')
		f = f.replace(' median(', ' ' + cfg.numpyMedian + '(')
		f = f.replace(' median (', ' ' + cfg.numpyMedian + '(')
		f = f.replace(' mean(', ' ' + cfg.numpyMean + '(')
		f = f.replace(' mean (', ' ' + cfg.numpyMean + '(')
		f = f.replace(' sum(', ' ' + cfg.numpySum + '(')
		f = f.replace(' sum (', ' ' + cfg.numpySum + '(')
		f = f.replace(' std(', ' ' + cfg.numpyStd + '(')
		f = f.replace(' std (', ' ' + cfg.numpyStd + '(')
		f = f.replace('^', '**')
		f = f.replace(' where(', ' ' + cfg.numpyWhere + '(')
		f = f.replace(' where (', ' ' + cfg.numpyWhere + '(')
		return f
			
	# raster calculation
	def noBlocksCalculation(self, rasterSCPArrayfunctionBand, functionBandArgument, functionVariableList, outputArrayFile, outputBandNumber):
		f = functionBandArgument
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'f  ' + str(f) )
		# replace numpy operators
		f = cfg.utls.replaceNumpyOperators(f)
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'f  ' + str(f) )
		# perform operation
		o = eval(f)
		if outputArrayFile is None:
			return o
		else:
			cfg.np.save(outputArrayFile, o)
			return outputArrayFile
	
	# interprocess
	def multiProcessNoBlocksDev(self, raster = None, signatureList = None, bandNumberList = None, functionRaster = None, algorithmName = None, outputArrayFile = None, outputAlgorithmRaster = None, outputClassificationRaster = None, previewSize = None, previewPoint = None, nodataValue = None, macroclassCheck = None, functionBandArgument = None, functionVariable = None, progressMessage = None, skipReplaceNoData = None, outputBandNumber = None, writerLog = None):
		from . import config as cfg
		import os
		import sys
		import inspect
		import time
		import datetime
		import random
		import numpy as np
		try:
			from scipy.ndimage import label
			cfg.labelSCP = label
		except:
			pass
		from osgeo import gdal
		from osgeo import ogr
		from osgeo import osr
		cfg.osSCP = os
		cfg.sysSCP = sys
		cfg.inspectSCP = inspect
		cfg.datetimeSCP = datetime
		cfg.np = np
		cfg.randomSCP = random
		cfg.gdalSCP = gdal
		cfg.ogrSCP = ogr
		cfg.osrSCP = osr
		from .utils import Utils
		cfg.utls = Utils()
		wrtProc = str(writerLog[0])
		cfg.tmpDir = writerLog[1]
		memory = writerLog[2]
		cfg.logFile = cfg.tmpDir + '/log_' + wrtProc
		# GDAL config
		try:
			cfg.gdalSCP.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'TRUE')
			cfg.gdalSCP.SetConfigOption('GDAL_CACHEMAX', memory)
			cfg.gdalSCP.SetConfigOption('VSI_CACHE', 'FALSE')
		except:
			pass
		# open input with GDAL
		rD = cfg.gdalSCP.Open(raster, cfg.gdalSCP.GA_ReadOnly)
		bandNumber = rD.RasterCount
		# number of x pixels
		rX = rD.RasterXSize
		# number of y pixels
		rY = rD.RasterYSize
		gdalBandList = []
		for b in range(1, bandNumber + 1):
			rB = rD.GetRasterBand(b)
			gdalBandList.append(rB)
		if outputBandNumber is None:
			outputBandNumber = 1
		# numpy data
		array = cfg.np.zeros((rY, rX, len(gdalBandList)), dtype=cfg.np.float32)
		for b in bandNumberList:
			if nodataValue is None:
				ndv = cfg.NoDataVal
			else:
				ndv = nodataValue
			# multiband
			try:
				b0 = gdalBandList[b].GetRasterBand(b+1)
			except:
				b0 = gdalBandList[b]
			try:
				of = b0.GetOffset()
				s = b0.GetScale()	
				if of is None:
					of = 0
				if s is None:
					s = 1
			except:
				of = 0
				s = 1
			a = b0.ReadAsArray()*s+of
			try:
				ndvBand = b0.GetNoDataValue() * s + of
			except:
				ndvBand = None
			if a is not None:
				if functionBandArgument == cfg.multiAddFactorsVar:
					multiAdd = functionVariable
					a = cfg.utls.arrayMultiplicativeAdditiveFactors(a, multiAdd[0][b], multiAdd[1][b])
				array[::, ::, b] = a
			else:
				return 'No'
			a = None
			# set nodata value
			if ndvBand is not None:
				try:
					array[::, ::, b][array[::, ::, b] == ndvBand] = cfg.np.nan
				except:
					pass
			if skipReplaceNoData is not None:
				try:
					array[::, ::, b][cfg.np.isnan(array[::, ::, b])] = ndvBand	
				except:
					pass
			if ndv is not None:
				try:
					array[::, ::, b][array[::, ::, b] == ndv] = cfg.np.nan
				except:
					pass
		for b in range(0, len(gdalBandList)):
			gdalBandList[b] = None
		rD = None
		o = functionRaster(array, functionBandArgument, functionVariable, outputArrayFile, outputBandNumber)
		# close GDAL rasters
		array = None
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'o ' + str(o) )
		return o

	# process a raster entirely 
	def multiProcessNoBlocks(self, rasterPath, signatureList = None, bandNumberList = None, functionRaster = None, algorithmName = None, outputRasterList = None, outputAlgorithmRaster = None, outputClassificationRaster = None, previewSize = 0, previewPoint = None, nodataValue = None, macroclassCheck = 'No', functionBandArgument = None, functionVariable = None, progressMessage = '', skipReplaceNoData = None, threadNumber = None, parallel = None, outputBandNumber = None, compress = 'No', compressFormat = 'LZW'):
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'start processRaster no boundaries')
		if threadNumber is None:
			threadNumber = cfg.threads
		memVal = str(int( cfg.RAMValue / threadNumber)*1000000)
		# multiple calculations
		sez = list(range(0, len(functionBandArgument), threadNumber))
		sez.append(len(functionBandArgument))
		totBlocks = len(functionBandArgument)
		# calculation multiprocess
		output = {}
		completedBlocks = 0
		for s in range(0, len(sez)-1):
			cfg.subprocRes = {}
			cfg.pool = cfg.poolSCP(processes=threadNumber)
			results = []
			for p in range(sez[s], sez[s+1]):
				if cfg.actionCheck == 'Yes':
					try:
						pOut = outputRasterList[p]
					except:
						pOut = None
					fArg = functionBandArgument[p]
					fVar = functionVariable[p]
					bList = bandNumberList[p]
					wrtP = [p, cfg.tmpDir, memVal, compress, compressFormat]
					c = cfg.pool.apply_async(cfg.utls.multiProcessNoBlocksDev, args=(rasterPath, signatureList, bList, functionRaster, algorithmName, pOut, outputAlgorithmRaster, outputClassificationRaster, previewSize, previewPoint, nodataValue, macroclassCheck, fArg, fVar, progressMessage, skipReplaceNoData, outputBandNumber, wrtP))
					results.append([c, p])
			# update progress
			while cfg.actionCheck == 'Yes':
				pR = []
				for r in results:
					pR.append(r[0].ready())
				if all(pR):
					break
				try:
					if progressMessage is not None:
						cfg.uiUtls.updateBar(int(100 * (completedBlocks + sum(pR)) / totBlocks), progressMessage)
				except:
					pass
				cfg.QtWidgetsSCP.qApp.processEvents()
			completedBlocks = completedBlocks + sum(pR)
			if cfg.actionCheck == 'Yes':
				for r in results:
					cfg.subprocRes[r[1]] = r[0].get()
			cfg.pool.close()
			cfg.pool.terminate()
			for p in range(sez[s], sez[s+1]):
				if cfg.actionCheck == 'Yes':
					try:
						output[functionBandArgument[p]] = cfg.subprocRes[p]
					except:
						output[functionBandArgument[p]] = None
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "end processRaster no boundaries")
		return output
		
	# interprocess
	def processRasterDev(self, raster = None, signatureList = None, functionBand = None, functionRaster = None, algorithmName = None, outputArrayFile = None, outputAlgorithmRaster = None, outputClassificationRaster = None, section = None, classificationOptions = None, nodataValue = None, macroclassCheck = None, functionBandArgument = None, functionVariable = None, progressMessage = None, skipReplaceNoData = None, singleBandNumber = None, outputBandNumber = None, outputNoData = None, scale = None, offset = None, writerLog = None):
		from . import config as cfg
		import os
		import sys
		import inspect
		import time
		import datetime
		import random
		import numpy as np
		try:
			import scipy.stats.distributions as statdistr
			cfg.statdistrSCP = statdistr
		except:
			pass
		try:
			from scipy import signal
			cfg.signalSCP = signal
		except:
			pass
		from osgeo import gdal
		from osgeo import ogr
		from osgeo import osr
		cfg.osSCP = os
		cfg.sysSCP = sys
		cfg.inspectSCP = inspect
		cfg.datetimeSCP = datetime
		cfg.np = np
		cfg.randomSCP = random
		cfg.gdalSCP = gdal
		cfg.ogrSCP = ogr
		cfg.osrSCP = osr
		from .utils import Utils
		cfg.utls = Utils()
		wrtProc = str(writerLog[0])
		wrtOut = writerLog[1]
		cfg.tmpDir = writerLog[2]
		parallelWritingCheck = writerLog[3]
		progressQueue = writerLog[4]
		memory = writerLog[5]
		compress = writerLog[6]
		compressFormat = writerLog[7]
		dataType = writerLog[8]
		boundarySize = writerLog[9]
		roX = writerLog[10]
		roY = writerLog[11]
		vBX = writerLog[12]
		vBY = writerLog[13]
		cfg.logFile = cfg.tmpDir + '/log_' + wrtProc
		# GDAL config
		try:
			cfg.gdalSCP.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'TRUE')
			cfg.gdalSCP.SetConfigOption('GDAL_CACHEMAX', memory)
			cfg.gdalSCP.SetConfigOption('VSI_CACHE', 'FALSE')
		except:
			pass
		if scale is not None:
			scl = float(scale)
		else:
			scl = 1.0
		if offset is not None:
			offs = float(offset)
		else:
			offs = 0.0
		# for raster creation
		format = cfg.gdalSCP.GDT_Float32
		# open input with GDAL
		rD = cfg.gdalSCP.Open(raster, cfg.gdalSCP.GA_ReadOnly)
		# pixel size and origin from reference
		rP = rD.GetProjection()
		rGT = rD.GetGeoTransform()
		tD = cfg.gdalSCP.GetDriverByName('GTiff')
		xSize = rD.RasterXSize
		ySize = rD.RasterYSize
		tLX = rGT[0]
		tLY = rGT[3]
		pSX = rGT[1]
		pSY = rGT[5]
		bandNumber = rD.RasterCount
		rD = None
		# if classification
		if functionRaster is not None and functionBand == 'Yes':
			# classification rasters
			outClasses = []
			# algorithm rasters
			outAlgs = []
			# signature dictionary rasters
			outSigDict = {}
		# create raster
		uLX = tLX + roX * pSX
		uLY = tLY + roY * pSY
		geotransform = (uLX, pSX, rGT[2], uLY, rGT[4], pSY)
		wrtFile = cfg.utls.createTempRasterPath('tif', wrtProc)
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'wrtFile, roX, roY, vBX, vBY ' + str([wrtFile, roX, roY, vBX, vBY]) )
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'dataType ' + str(dataType) )
		# output
		if wrtOut is not None:
			cfg.utls.createRasterFromReferenceMultiprocess(raster, 1, [wrtFile], nodataValue, 'GTiff', dataType, compress, compressFormat, geotransform = geotransform, xSize = vBX, ySize = vBY)
		process = 0
		while process < 2:
			procError = 'No'
			process = process + 1
			o = []
			countPerc = 0				
			for sec in section:
				# logger
				cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'sec ' + str(sec) )
				check = 0
				# open input with GDAL
				rD = cfg.gdalSCP.Open(raster, cfg.gdalSCP.GA_ReadOnly)
				gdalBandList = []
				if singleBandNumber is None:
					for b in range(1, bandNumber + 1):
						rB = rD.GetRasterBand(b)
						gdalBandList.append(rB)
				else:
						rB = rD.GetRasterBand(singleBandNumber+1)
						gdalBandList.append(rB)
				# perform the process twice in case of error
				while check < 2:
					if boundarySize is None:
						x, y, bSX, bSY = sec
						# logger
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'x, y, bSX, bSY ' + str([x, y, bSX, bSY]) )
					else:
						x, y, bSX, bSY, oX, oXX, oY, oYY = sec
						# logger
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'x, y, bSX, bSY, oX, oXX, oY, oYY ' + str([x, y, bSX, bSY, oX, oXX, oY, oYY]) )
					# if classification
					if functionRaster is not None and functionBand == 'Yes':
						dT = cfg.datetimeSCP.datetime.now().strftime('%Y%m%d_%H%M%S%f')
						# signature raster list
						outputSigRasterList = []
						# list of rasters to be created
						outputReferenceRasterList = []
						# create tif paths
						for s in range(0, len(signatureList)):
							sLR = str(signatureList[s][0]) + '_' + str(signatureList[s][2])
							sTR = cfg.tmpDir + '/' + cfg.sigRasterNm + '_' + sLR + '_' + dT + str(wrtProc) + '.tif'
							try:
								outSigDict[sLR].append(sTR)
							except Exception as err:
								outSigDict[sLR] = [sTR]
							outputSigRasterList.append(sTR)
							outputReferenceRasterList.append(sTR)
						# logger
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'outSigDict ' + str(outSigDict) )
						outClass = cfg.tmpDir + '/' + 'c_' + dT + str(wrtProc) + '.tif'
						outAlg = cfg.tmpDir + '/' + 'a_' + dT + str(wrtProc) + '.tif'
						outputReferenceRasterList.append(outClass)
						outputReferenceRasterList.append(outAlg)
						outClasses.append(outClass)
						outAlgs.append(outAlg)
						uLX = tLX + x * pSX
						uLY = tLY + y * pSY
						geotransform = (uLX, pSX, rGT[2], uLY, rGT[4], pSY)
						cfg.utls.createRasterFromReferenceMultiprocess(raster, 1, outputReferenceRasterList, nodataValue, 'GTiff', cfg.rasterDataType, compress, compressFormat, geotransform = geotransform, xSize = bSX, ySize = bSY)
					array = cfg.np.zeros((bSY, bSX, len(gdalBandList)), dtype=cfg.np.float32)
					for b in range(0, len(gdalBandList)):
						sclB = 1.0
						offsB = 0.0
						# logger
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' nodataValue ' + str(nodataValue) )
						if nodataValue is None:
							ndv = None
						else:
							ndv = nodataValue
						# logger
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'read band ' + str(b) )
						# read
						if parallelWritingCheck == 'Yes':
							pCount = 0
							while True:
								pCount = pCount + 1
								a = cfg.utls.readArrayBlock(gdalBandList[b], x, y, bSX, bSY)
								time.sleep(0.1)
								a2 = cfg.utls.readArrayBlock(gdalBandList[b], x, y, bSX, bSY)
								checkA = cfg.np.allclose(a, a2, equal_nan=True)
								# logger
								cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'checkA ' + str(checkA) )
								if checkA is True:
									break
								if pCount > 3:
									a = None
									break
							a2 = None
						else:
							a = cfg.utls.readArrayBlock(gdalBandList[b], x, y, bSX, bSY)
						try:
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'a ' + str(a[0,0]) )
						except:
							pass
						# logger
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'read band' + str(b) )
						try:
							b0 = gdalBandList[b].GetRasterBand(1)
							offsB = b0.GetOffset()
							sclB = b0.GetScale()
							if sclB is not None:
								sclB = float(sclB)
							if offsB is not None:
								offsB = float(offsB)
							ndvBand = b0.GetNoDataValue() 
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'ndvBand ' + str(ndvBand) )
							ndvBand = ndvBand * sclB + offsB
						except:
							try:
								offsB = gdalBandList[b].GetOffset()
								sclB = gdalBandList[b].GetScale()
								if sclB is not None:
									sclB = float(sclB)
								if offsB is not None:
									offsB = float(offsB)
								ndvBand = gdalBandList[b].GetNoDataValue()
								# logger
								cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'ndvBand ' + str(ndvBand) )
								ndvBand = ndvBand * sclB + offsB
							except:
								ndvBand = None
						# logger
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'ndvBand ' + str(ndvBand) + ' sclB ' + str(sclB)+ ' offsB ' + str(offsB))
						if a is not None:
							if functionBandArgument == cfg.multiAddFactorsVar:
								multiAdd = functionVariable
								a = cfg.utls.arrayMultiplicativeAdditiveFactors(a, multiAdd[0][b], multiAdd[1][b])
							array[::, ::, b] = a
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'array[0, 0, b] ' + str(array[0, 0, b] ) )
						else:
							procError = 'Error array none'
						a = None
						# set nodata value
						if ndvBand is not None:
							try:
								array[::, ::, b][array[::, ::, b] == ndvBand] = cfg.np.nan
							except:
								pass
						if skipReplaceNoData is not None:
							try:
								array[::, ::, b][cfg.np.isnan(array[::, ::, b])] = ndvBand
							except:
								pass
						if ndv is not None:
							try:
								array[::, ::, b][array[::, ::, b] == ndv] = cfg.np.nan
							except:
								pass
						# logger
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'skipReplaceNoData ' + str(skipReplaceNoData))
						#if functionBand is not None and functionBand != 'No':
						#	functionBand(b+1, array[::, ::, b].reshape(bSY, bSX), bSX, bSY, x, y, outputArrayFile, functionBandArgument, functionVariable)
							# logger
						#	cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionBand ' + str(functionBand))
					# logger
					try:
						cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'array ' + str(array[0,0,0]))
					except:
						pass
					# logger
					cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'wrtOut ' + str(wrtOut))
					# logger
					cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionBand ' + str(functionBand))
					if functionRaster is not None:
						if functionBand == 'No':
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'outputBandNumber ' + str(outputBandNumber))
							oo = functionRaster(gdalBandList, array, bSX, bSY, x, y, outputArrayFile, functionBandArgument, functionVariable, outputBandNumber)
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oo ' + str(oo))
							if wrtOut is None:
								o.append(oo)
							else:
								o.append([wrtFile, sec])
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionBand No functionRaster ' + str(functionRaster))
							if oo == 'No':
								procError = 'Error function raster'
						# classification
						else:
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'outputSigRasterList ' + str(outputSigRasterList))
							landCoverSignature, LCSClassAlgorithm, LCSLeaveUnclassified, algBandWeigths, algThrshld = classificationOptions
							oo = functionRaster(len(gdalBandList), signatureList, algorithmName, array, landCoverSignature, LCSClassAlgorithm,LCSLeaveUnclassified, algBandWeigths, outputSigRasterList, outAlg, outClass, nodataValue, macroclassCheck, algThrshld)
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oo ' + str(oo))
							o = [outClasses, outAlgs, outSigDict]
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionRaster ' + str(functionRaster))
							if oo == 'No':
								procError = 'Error function band'	
					# output
					if wrtOut is not None:
						try:
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'scale ' + str(scale))
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'offset ' + str(offset))
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oo dtype ' + str(oo.dtype))
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'outputNoData ' + str(outputNoData))
							# write array
							oo[cfg.np.isnan(oo)] = outputNoData
							if boundarySize is not None:
								oo = oo[oY:(bSY-oYY), oX:(bSX-oXX)]
								x = x + oX
								y = y + oY
								bSX = bSX - oX - oXX
								bSY = bSY - oY - oYY
								# logger
								cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'x ' + str(x))
								cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oXX ' + str(oXX))
								cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'bSX ' + str(bSX))
								cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oo1 ' + str(oo.shape))
								# logger
								cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oo2 ' + str(oo.shape))
							if parallelWritingCheck == 'Yes':
								pCount = 0
								while True:
									pCount = pCount + 1
									#writeOut = cfg.utls.writeRaster(wrtFile, [tLX + x*pSX, pSX, rGT[2], tLY + y*pSY, rGT[4], pSY], rP, bSX, bSY, format, oo, outputNoData, scl, offs, compress, compressFormat, dataType)
									writeOut = cfg.utls.writeRasterNew(wrtFile, x-roX, y-roY, bSX, bSY, oo, outputNoData, scl, offs, dataType)
									oR = cfg.gdalSCP.Open(wrtFile, cfg.gdalSCP.GA_ReadOnly)
									bO = oR.GetRasterBand(1)
									oo2 = cfg.utls.readArrayBlock(bO, x-roX, y-roY, bSX, bSY)
									#oo2 = bO.ReadAsArray()
									bO = None
									oR = None
									checkOO = cfg.np.allclose(oo, oo2, equal_nan=True)
									# logger
									cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'checkOO ' + str(checkOO))
									if checkOO is True:
										break
									if pCount > 3:
										break
							else:
								#writeOut = cfg.utls.writeRaster(wrtFile, [tLX + x*pSX, pSX, rGT[2], tLY + y*pSY, rGT[4], pSY], rP, bSX, bSY, format, oo, outputNoData, scl, offs, compress, compressFormat, dataType)
								writeOut = cfg.utls.writeRasterNew(wrtFile, x-roX, y-roY, bSX, bSY, oo, outputNoData, scl, offs, dataType)
							check = 2
							array = None
							oo = None
							oo2 = None
							# logger
							cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'wrtFile ' + str(wrtFile) + ' writeOut' + str(writeOut))
						except Exception as err:
							procError = err
							check = check + 1
					else:
						check = 2
					if wrtProc == '0':
						perc = str(int(100 * countPerc / len(section)))
						progressQueue.put([perc], False)
				# close GDAL rasters
				for b in range(0, len(gdalBandList)):
					gdalBandList[b].FlushCache()
					gdalBandList[b] = None
				gdalBandList = None
				rD = None	
				countPerc = countPerc + 1
			if procError == 'No':
				process = 2
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'end for')
		if procError != 'No':
			return o, procError
		return o, ''
		
	# process a raster with block size
	def multiProcessRaster(self, rasterPath, signatureList = None, functionBand = None, functionRaster = None, algorithmName = None, outputRasterList = None, outputAlgorithmRaster = None, outputClassificationRaster = None, classificationOptions = None, nodataValue = None, macroclassCheck = 'No', functionBandArgument = None, functionVariable = None, progressMessage = "", skipReplaceNoData = None, threadNumber = None, parallel = None, deleteArray = None, skipSingleBand = None, outputBandNumber = None, virtualRaster = 'No', compress = 'No', compressFormat = 'LZW', outputNoDataValue = None, dataType = None, scale = None, offset = None, parallelWritingCheck = None, boundarySize = None, additionalLayer = None):
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'start processRaster')
		if outputNoDataValue is None:
			outputNoDataValue = cfg.NoDataVal
		if dataType is None:
			dataType = cfg.rasterDataType
		gdalRaster = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_ReadOnly)
		if additionalLayer is None:
			additionalLayer = 1
		elif algorithmName == 'PCA':
			additionalLayer = 10
		if outputBandNumber is None:
			outputBandNumber = 1
		if parallelWritingCheck is None:
			parallelWritingCheck = cfg.parallelWritingCheck
		try:
			bandNumber = gdalRaster.RasterCount
		except:
			return 'No'
		if threadNumber is None:
			threadNumber = cfg.threads
		# number of x pixels
		rX = gdalRaster.RasterXSize
		# number of y pixels
		rY = gdalRaster.RasterYSize
		# list of range pixels
		blockSizeY = int(rY/threadNumber)+1
		lY = list(range(0, rY, blockSizeY))
		blockSizeX = int(cfg.RAMValue / (blockSizeY * cfg.arrayUnitMemory * (bandNumber + additionalLayer) * threadNumber))+1
		if blockSizeX > rX:
			blockSizeX = rX
		lX = list(range(0, rX, blockSizeX))
		gdalRaster = None
		# set initial value for progress bar
		try:
			progresStep = 60 / (len(lX) * len(lY))
		except:
			progresStep = 60 
		progressStart = 20 - progresStep
		singleBandNumber = None
		cfg.remainingTime = 0
		remainingBlocks = len(lX) * len(lY)
		totBlocks = remainingBlocks
		manager = cfg.MultiManagerSCP()
		# progress queue
		pMQ = manager.Queue()
		results = []
		pR = []
		# temporary raster output
		tmpRastList = []
		cfg.subprocRes = {}
		# calculate raster ranges
		ranges = []
		for y in lY:
			secs = []
			bSY = blockSizeY
			if y + bSY > rY:
				bSY = rY - y
			for x in lX:
				bSX = blockSizeX 
				if x + bSX > rX:
					bSX = rX - x
				# single parallel process
				if parallel is None:
					if boundarySize is None:
						secs.append([x, y, bSX, bSY])
					else:
						# left x position plus boundary
						boundX = x - boundarySize
						# right x position plus boundary
						boundSX = bSX + boundarySize *  2
						# left pixels
						oX = boundarySize
						# right pixels
						oXX = boundarySize
						if boundX <= 0:
							boundX = 0
							boundSX = bSX + boundarySize
							oX = 0
						if boundX + boundSX >= rX:
							boundSX = rX - boundX
							oXX = 0
						# upper position plus boundary
						boundY = y - boundarySize
						# lower y position plus boundary
						boundSY = bSY + boundarySize *  2
						# upper pixels
						oY = boundarySize
						# lower pixels
						oYY = boundarySize
						if boundY <= 0:
							boundY = 0
							boundSY = bSY + boundarySize
							oY = 0
						if boundY + boundSY >= rY:
							boundSY = rY - boundY
							oYY = 0
						secs.append([boundX, boundY, boundSX, boundSY, oX, oXX, oY, oYY])
				# multiple parallel processes
				else:
					ranges.append([x, y, bSX, bSY])
			# single parallel process
			if parallel is None:
				ranges.append(secs)
		if skipSingleBand is not None:
			ranges.append([0, 0, rX, rY])
		# single parallel process
		if parallel is None:
			# pool
			cfg.pool = cfg.poolSCP(processes=threadNumber)
			memVal = '100000000'
			if progressMessage is not None:
				cfg.uiUtls.updateBar(progressStart + int((100 - progressStart) * (totBlocks - remainingBlocks) / totBlocks), progressMessage)
			for p in range(0, len(ranges)):
				sections = ranges[p]
				vX = []
				vBX = 0
				for sec in sections:
					if boundarySize is not None:
						x, y, bSX, bSY, oX, oXX, oY, oYY = sec
						x = x + oX
						bSX = bSX - oX - oXX
						y = y + oY
						bSY = bSY - oY - oYY
					else:
						x, y, bSX, bSY = sec
					vX.append(x)
					vBX = vBX + bSX
				# minimum origin
				roX = min(vX)
				if cfg.actionCheck == 'Yes':
					pOut = ''
					wrtP = [p, outputRasterList, cfg.tmpDir, parallelWritingCheck, pMQ, memVal, compress, compressFormat, dataType, boundarySize, roX, y, vBX, bSY]
					c = cfg.pool.apply_async(self.processRasterDev, args=(rasterPath, signatureList, functionBand, functionRaster, algorithmName, pOut, outputAlgorithmRaster, outputClassificationRaster, sections, classificationOptions, nodataValue, macroclassCheck, functionBandArgument, functionVariable, progressMessage, skipReplaceNoData, singleBandNumber, outputBandNumber, outputNoDataValue, scale, offset, wrtP))
					results.append([c, p])
					cfg.QtWidgetsSCP.qApp.processEvents()
			# update progress
			while cfg.actionCheck == 'Yes':
				pR = []
				for r in results:
					pR.append(r[0].ready())
				if all(pR):
					break
				cfg.timeSCP.sleep(1)
				try:
					dots = dots + '.'
					if len(dots) > 3:
						dots = ''
				except:
					dots = ''
				try:
					pMQp = pMQ.get(False)
					pgQ = int(pMQp[0])
					try:
						# update progress and message
						cfg.uiUtls.updateBar(pgQ, pMQp[1] + dots)
					except:
						cfg.uiUtls.updateBar(pgQ)
				except:
					if progressMessage is not None:
						cfg.uiUtls.updateBar(message = progressMessage + dots)
				cfg.QtWidgetsSCP.qApp.processEvents()
			if cfg.actionCheck == 'Yes':
				for r in results:
					if cfg.actionCheck == 'Yes':
						res = r[0].get()
						cfg.subprocRes[r[1]] = res[0]
						if len(str(res[1])) > 0:
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error proc '+ str(p) + '-' + str(res[1]))
							return 'No'
					else:
						cfg.pool.close()
						cfg.pool.terminate()
						return 'No'
				cfg.pool.close()
				cfg.pool.terminate()
		# multiple parallel processes
		else:
			if progressMessage is not None:
				cfg.uiUtls.updateBar(progressStart + int((100 - progressStart) * (totBlocks - remainingBlocks) / totBlocks), progressMessage)
			# set initial value for progress bar
			progressStart = progressStart + progresStep
			# for band number
			if functionBandArgument is None:
				sez = list(range(0, bandNumber, threadNumber)) 
				sez.append(bandNumber)
				totBlocks = bandNumber
			# for function number
			else:
				sez = list(range(0, len(functionBandArgument), threadNumber))
				sez.append(len(functionBandArgument))
				totBlocks = len(functionBandArgument)
			completedBlocks = 0
			for s in range(0, len(sez)-1):
				# pool
				cfg.pool = cfg.poolSCP(processes=len(list(range(sez[s], sez[s+1]))))
				memVal = str(int( cfg.RAMValue / len(list(range(sez[s], sez[s+1]))))*1000000)
				results = []
				roX = 0
				for p in range(sez[s], sez[s+1]):
					if cfg.actionCheck == 'Yes':
						sections= ranges
						if parallel == cfg.parallelArray:
							pOut = ''
							try:
								fArg = functionBandArgument[p]
							except:
								fArg = None
							try:
								fVar = functionVariable[p]
							except:
								fVar = None
							otpLst = outputRasterList
						# cfg.parallelRaster
						else:
							pOut = outputRasterList[p]
							fArg = functionBandArgument[p]
							fVar = functionVariable[p]
							otpLst = None
						wrtP = [p, otpLst, cfg.tmpDir, parallelWritingCheck, pMQ, memVal, compress, compressFormat, dataType, boundarySize, 0, 0, rX, rY]
						if skipSingleBand is None:
							singleBand = p
						else:
							singleBand = None
						c = cfg.pool.apply_async(self.processRasterDev, args=(rasterPath, signatureList, functionBand, functionRaster, algorithmName, pOut, outputAlgorithmRaster, outputClassificationRaster, sections, classificationOptions, nodataValue, macroclassCheck, fArg, fVar, progressMessage, skipReplaceNoData, singleBand, outputBandNumber, outputNoDataValue, scale, offset, wrtP))
						results.append([c, p])
				# update progress
				while cfg.actionCheck == 'Yes':
					pR = []
					for r in results:
						pR.append(r[0].ready())
					if all(pR):
						break
					try:
						if progressMessage is not None:
							try:
								dots = dots + '.'
								if len(dots) > 3:
									dots = ''
							except:
								dots = ''
							cfg.uiUtls.updateBar(progressStart + int((100 - progressStart) * (completedBlocks + sum(pR)) / totBlocks), progressMessage + dots)
					except:
						pass
					cfg.timeSCP.sleep(1)
					cfg.QtWidgetsSCP.qApp.processEvents()
				completedBlocks = completedBlocks + sum(pR)
				if cfg.actionCheck == 'Yes':
					for r in results:
						res = r[0].get()
						cfg.subprocRes[r[1]] = res[0]
						if len(str(res[1])) > 0:
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error proc '+ str(p) + '-' + str(res[1]))
							cfg.pool.close()
							cfg.pool.terminate()
							return 'No'
						cfg.QtWidgetsSCP.qApp.processEvents()
					cfg.pool.close()
					cfg.pool.terminate()
		# get parallel dictionary result
		for p in sorted(cfg.subprocRes):
			try:
				cfg.parallelArrayDict[p].extend(cfg.subprocRes[p])
			except:
				cfg.parallelArrayDict[p] = cfg.subprocRes[p]
		# output
		if outputRasterList is not None and parallel is None:
			try:
				parts = len(cfg.subprocRes[p]) * len(cfg.subprocRes)
			except:
				return 'No'
			for p in cfg.subprocRes:
				for op in cfg.subprocRes[p]:
					try:
						dots = dots + '.'
						if len(dots) > 3:
							dots = ''
					except:
						dots = ''
					cfg.uiUtls.updateBar(0, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Writing file') + dots)
					tmpRastList.append(op[0])
			gdalV = cfg.utls.getGDALVersion()
			if float(gdalV[0] + '.' + gdalV[1]) >= 2.3:
				if scale is not None:
					scl = scale
				else:
					scl = 1
				if offset is not None:
					offs = offset
				else:
					offs = 0
				if scale is not None or offset is not None:
					parScaleOffset = ' -a_scale ' + str(scl) + ' -a_offset ' + str(offs)
				else:
					parScaleOffset = ''
			else:
				parScaleOffset = ''
			if virtualRaster == 'Yes':
				cfg.tmpList = []
				dirPath = cfg.osSCP.path.dirname(outputRasterList[0])
				for tR in tmpRastList:
					oTR = dirPath + '/' + cfg.utls.fileName(tR)
					cfg.tmpList.append(oTR)
					cfg.shutilSCP.move(tR, oTR)
				cfg.utls.createVirtualRaster2(inputRasterList = cfg.tmpList, output = outputRasterList[0], NoDataValue = 'Yes', dataType = dataType)
			else:
				vrtFile = cfg.utls.createTempRasterPath('vrt')	
				try:
					cfg.utls.createVirtualRaster2(inputRasterList = tmpRastList, output = vrtFile, NoDataValue = 'Yes', dataType = dataType)
					gcopy = cfg.utls.GDALCopyRaster(vrtFile, outputRasterList[0], 'GTiff', compress, compressFormat, additionalParams = '-ot ' + str(dataType) + parScaleOffset)
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'gcopy ' + gcopy)
				except:
					try:
						cfg.utls.createVirtualRaster2(inputRasterList = tmpRastList, output = vrtFile, NoDataValue = 'Yes', dataType = dataType)
						gcopy = cfg.utls.GDALCopyRaster(vrtFile, outputRasterList[0], 'GTiff', compress, compressFormat, additionalParams = '-ot ' + str(dataType) + parScaleOffset)
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'gcopy ' + gcopy)
					except:
						return 'No'
		if functionBand == 'Yes':
			outputClasses = []
			outputAlgs = []
			outSigDict = {}
			for p in cfg.subprocRes:
				for s in range(0, len(signatureList)):
					sLR = str(signatureList[s][0]) + '_' + str(signatureList[s][2])
					try:
						nSLR = list(cfg.subprocRes[p][2][sLR])
						nSLR.extend(outSigDict[sLR])
						outSigDict[sLR] = nSLR
					except:
						outSigDict[sLR] = cfg.subprocRes[p][2][sLR]
				for oC in cfg.subprocRes[p][0]:
					outputClasses.append(oC)
				for oA in cfg.subprocRes[p][1]:
					outputAlgs.append(oA)
			return [outputClasses, outputAlgs, outSigDict]
		# delete temp array
		if deleteArray is None and virtualRaster != 'Yes':
			for n in tmpRastList:
				try:
					cfg.osSCP.remove(n)
				except:
					pass
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'end processRaster')
		return 'Yes'
		
	# convert raster to shapefile
	def multiProcessRasterToVector(self, rasterPath, outputVectorPath, fieldName = 'No', threadNumber = None, dissolveOutput = 'Yes'):
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'start raster to vector')
		if threadNumber is None:
			threadNumber = cfg.threads
		gdalRaster = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_ReadOnly)
		xSize = gdalRaster.RasterXSize
		ySize = gdalRaster.RasterYSize
		blockSizeX = int(xSize/float(threadNumber))+1
		blockSizeY = ySize
		# raster blocks
		rX, rY, lX, lY, pX, pY  = self.rasterBlocks(gdalRaster, blockSizeX, blockSizeY)
		rGT = gdalRaster.GetGeoTransform()
		tLX = rGT[0]
		tLY = rGT[3]
		pSX = rGT[1]
		pSY = rGT[5]
		gdalRaster = None
		if blockSizeX > rX:
			blockSizeX = rX
		if blockSizeY > rY:
			blockSizeY = rY
		# pool
		cfg.pool = cfg.poolSCP(processes=threadNumber)
		# temporary raster output
		tmpRastList = []
		subprocRes = []
		# calculate raster ranges
		nn = 0
		for y in lY:
			bSY = blockSizeY
			if y + bSY > rY:
				bSY = rY - y
			for x in lX:
				bSX = blockSizeX 
				if x + bSX > rX:
					bSX = rX - x
				tPMD = cfg.utls.createTempRasterPath('vrt', name = str(nn))
				tmpRastList.append(tPMD)
				cfg.utls.createVirtualRaster2(inputRasterList = [rasterPath], output = tPMD, NoDataValue = 'Yes', extentList = [x, y, bSX, bSY])
				nn = nn + 1
		# multiple parallel processes
		results = []
		field = 'DN'
		for p in range(0, len(tmpRastList)):
			if cfg.actionCheck == 'Yes':
				vRasterPath = tmpRastList[p]
				tVect = cfg.utls.createTempRasterPath('gpkg', name = str(p))
				wrtP = [p, cfg.tmpDir]
				c = cfg.pool.apply_async(cfg.utls.rasterToVectorMulti, args=(vRasterPath, tVect, field, wrtP))
				results.append([c, p])
		while cfg.actionCheck == 'Yes':
			pR = []
			for r in results:
				pR.append(r[0].ready())
				try:
					dots = dots + '.'
					if len(dots) > 3:
						dots = ''
				except:
					dots = ''
				cfg.uiUtls.updateBar(int(100 * sum(pR) / len(pR)), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Conversion to vector') + dots)
			if all(pR):
				break
			cfg.timeSCP.sleep(1)
			cfg.QtWidgetsSCP.qApp.processEvents()	
		for r in results:
			if cfg.actionCheck == 'Yes':
				res = r[0].get()
				subprocRes.append(res[0])
				if len(str(res[1])) > 0:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error proc '+ str(p) + '-' + str(res[1]))
					return 'No'
				cfg.QtWidgetsSCP.qApp.processEvents()
			else:
				cfg.pool.close()
				cfg.pool.terminate()
				return 'No'
		cfg.pool.close()
		cfg.pool.terminate()
		cfg.uiUtls.updateBar(50)
		# merge vectors
		merged = cfg.utls.createTempRasterPath('gpkg')
		if len(subprocRes) > 1:
			merge = cfg.utls.mergeLayersToNewLayer(subprocRes, outputVectorPath, field, dissolveOutput)
		else:
			merge = subprocRes[0]
		cfg.uiUtls.updateBar(60)
		# copy merge
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' merged')
		return merge

	# convert raster to shapefile
	def rasterToVectorMulti(self, rasterPath, outputVectorPath, fieldName = 'No', writerLog = None):	
		from . import config as cfg
		import os
		import sys
		import inspect
		import time
		import datetime
		import random
		import numpy as np
		from osgeo import gdal
		from osgeo import ogr
		from osgeo import osr
		cfg.osSCP = os
		cfg.sysSCP = sys
		cfg.inspectSCP = inspect
		cfg.datetimeSCP = datetime
		cfg.randomSCP = random
		cfg.np = np
		cfg.gdalSCP = gdal
		cfg.ogrSCP = ogr
		cfg.osrSCP = osr
		from .utils import Utils
		cfg.utls = Utils()
		# GDAL config
		try:
			cfg.gdalSCP.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'TRUE')
			cfg.gdalSCP.SetConfigOption('GDAL_CACHEMAX', '4')
			cfg.gdalSCP.SetConfigOption('VSI_CACHE', 'FALSE')
		except:
			pass
		wrtProc = str(writerLog[0])
		cfg.tmpDir = writerLog[1]
		cfg.logFile = cfg.tmpDir + '/log_' + wrtProc
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " process: " + str(wrtProc))
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " rasterPath: " + str(rasterPath))
		# open input with GDAL
		try:
			rD = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_ReadOnly)
			# number of x pixels
			rC = rD.RasterXSize
		# in case of errors
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return '', 'No'
		# create a shapefile
		d = cfg.ogrSCP.GetDriverByName('GPKG')
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " outputVectorPath: " + str(outputVectorPath))
		dS = d.CreateDataSource(outputVectorPath)
		if dS is None:
			# close rasters
			rD = None
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " error: " + str(outputVectorPath))
		else:
			# shapefile
			sR = cfg.osrSCP.SpatialReference()
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " sR: " + str(sR))
			sR.ImportFromWkt(rD.GetProjectionRef())
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " sR: " + str(sR))
			rL = dS.CreateLayer(cfg.utls.fileName(rasterPath), sR, cfg.ogrSCP.wkbMultiPolygon)
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " rL: " + str(rL))
			if fieldName == 'No':
				fN = str(cfg.fldID_class)
			else:
				fN = fieldName
			fd = cfg.ogrSCP.FieldDefn(fN, cfg.ogrSCP.OFTInteger)
			try:
				rL.CreateField(fd)
			# in case of errors
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				# close rasters
				rD = None
				return '', 'No'
			fld = rL.GetLayerDefn().GetFieldIndex(fN)
			rRB = rD.GetRasterBand(1)
			# raster to polygon
			cfg.gdalSCP.Polygonize(rRB, rRB.GetMaskBand(), rL, fld)		
			# close rasters and shapefile
			rRB = None
			rD = None			
			dS = None							
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " vector output performed")
			# open layer
			input0 = cfg.ogrSCP.Open(outputVectorPath)
			iL0 = input0.GetLayer()
			iNm0 = iL0.GetName()
			sql = 'SELECT MIN(minx) FROM "rtree_' + iNm0 + '_geom"'
			uV = input0.ExecuteSQL(sql, dialect = "SQLITE")
			uVF = uV.GetNextFeature()
			minX = uVF.GetField(0)
			sql = 'SELECT MAX(maxx) FROM "rtree_' + iNm0 + '_geom"'
			uV = input0.ExecuteSQL(sql, dialect = "SQLITE")
			uVF = uV.GetNextFeature()
			maxX = uVF.GetField(0)
			return [outputVectorPath, minX, maxX], ''
		
	# write raster
	def writeArrayRaster(self, rasterPath, arrayFile, section):
		if cfg.actionCheck == 'Yes':
			r = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_Update)
			try:
				arrayFile = arrayFile[::, ::, 0]
			except:
				pass
			cfg.utls.writeArrayBlock(r, 1, arrayFile, section[0], section[1])
			r = None
			
	# write raster
	def writeRaster(self, rasterPath, geoTransform, projection, bSX, bSY, format, dataArray, nodataValue = None, scale = None, offset = None, compress = 'No', compressFormat = 'LZW', dataType = None):
		tD = cfg.gdalSCP.GetDriverByName('GTiff')
		if compress == 'Yes':
			option = ['COMPRESS=' + compressFormat]
		else:
			option = []
		if dataType is not None:
			try:
				format = eval('cfg.gdalSCP.GDT_' + dataType)
			except:
				format = cfg.gdalSCP.GDT_Float32
			if dataType == 'Float64':
				oType = cfg.np.float64
			elif dataType == 'Float32':
				oType = cfg.np.float32
			elif dataType == 'Int32':
				oType = cfg.np.int32
			elif dataType == 'UInt32':
				oType = cfg.np.uint32
			elif dataType == 'Int16':
				oType = cfg.np.int16
			elif dataType == 'UInt16':
				oType = cfg.np.uint16
			elif dataType == 'Byte':
				oType = cfg.np.byte
			else:
				oType = cfg.np.float32
		else:
			format = cfg.gdalSCP.GDT_Float32
			oType = cfg.np.float32
		oR = tD.Create(rasterPath, bSX, bSY, 1, format, options = option)
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oR write ' + str(rasterPath))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'format ' + str(format))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'option ' + str(option))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oType ' + str(oType))
		# set raster projection from reference
		oR.SetGeoTransform(geoTransform)
		oR.SetProjection(projection)
		bO = oR.GetRasterBand(1)
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'write bO ' + str(bO))
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'dataArray shape write ' + str(dataArray.shape) + ' type ' + str(dataArray.dtype) )
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' scale ' + str(scale) )
		try:
			# it seems a GDAL issue that if scale is float the datatype is converted to Float32
			if scale is not None or offset is not None:
				dataArray = cfg.np.subtract(dataArray/scale, offset/scale)
				bO.SetScale(scale)
				bO.SetOffset(offset)
		except Exception as err:
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		if nodataValue is not None:
			bO.SetNoDataValue(int(nodataValue))
		try:
			dataArray = dataArray[::, ::, 0]
		except:
			pass
		r = bO.WriteRaster(0, 0, bSX, bSY, dataArray[:bSY, :bSX].astype(oType).tostring())
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'output r ' + str(r))
		bO.FlushCache()
		bO = None
		oR = None
		return rasterPath
		
	# write raster
	def writeRasterNew(self, rasterPath, x, y, bSX, bSY, dataArray, nodataValue = None, scale = None, offset = None, dataType = None):
		if dataType is not None:
			if dataType == 'Float64':
				oType = cfg.np.float64
			elif dataType == 'Float32':
				oType = cfg.np.float32
			elif dataType == 'Int32':
				oType = cfg.np.int32
			elif dataType == 'UInt32':
				oType = cfg.np.uint32
			elif dataType == 'Int16':
				oType = cfg.np.int16
			elif dataType == 'UInt16':
				oType = cfg.np.uint16
			elif dataType == 'Byte':
				oType = cfg.np.byte
			else:
				oType = cfg.np.float32
		else:
			oType = cfg.np.float32
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'oType ' + str(oType))
		oR = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_Update)
		bO = oR.GetRasterBand(1)
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'write bO ' + str(bO))
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'dataArray shape write ' + str(dataArray.shape) + ' type ' + str(dataArray.dtype) )
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' scale ' + str(scale) )
		try:
			# it seems a GDAL issue that if scale is float the datatype is converted to Float32
			if scale is not None or offset is not None:
				dataArray = cfg.np.subtract(dataArray/scale, offset/scale)
				bO.SetScale(scale)
				bO.SetOffset(offset)
		except Exception as err:
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		if nodataValue is not None:
			bO.SetNoDataValue(int(nodataValue))
		try:
			dataArray = dataArray[::, ::, 0]
		except:
			pass
		r = bO.WriteRaster(x, y, bSX, bSY, dataArray[:bSY, :bSX].astype(oType).tostring())
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'output r ' + str(r))
		bO.FlushCache()
		bO = None
		oR = None
		return rasterPath
			
	# calculate random points
	def randomPoints(self, pointNumber, Xmin, Xmax, Ymin, Ymax, minDistance = None, rasterName = None, NoDataValue = None, stratified = None, stratifiedExpression = None, bandSetNumber = None):
		points = []
		counter = 0
		while len(points) < pointNumber:
			counter = counter + 1
			XCoords = cfg.np.random.uniform(Xmin,Xmax,1)
			YCoords = cfg.np.random.uniform(Ymin,Ymax,1)
			point = cfg.qgisCoreSCP.QgsPointXY(XCoords, YCoords)
			if bandSetNumber is None:
				bandSetNumber = cfg.bndSetNumber
			# band set
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				rast = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][3][0], 'Yes')	
				# open input with GDAL
				try:
					ql = cfg.utls.layerSource(rast)
					Or = cfg.gdalSCP.Open(ql, cfg.gdalSCP.GA_ReadOnly)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msgErr4()
					return points
			else:
				rL = cfg.utls.selectLayerbyName(rasterName, 'Yes')
				# open input with GDAL
				try:
					qll = cfg.utls.layerSource(rL)
					Or = cfg.gdalSCP.Open(qll, cfg.gdalSCP.GA_ReadOnly)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msgErr4()
					return points
			OrB = Or.GetRasterBand(1)
			geoT = Or.GetGeoTransform()
			tLX = geoT[0]
			tLY = geoT[3]
			pSX = geoT[1]
			pSY = geoT[5]
			# start and end pixels
			pixelStartColumn = (int((point.x() - tLX) / pSX))
			pixelStartRow = -(int((tLY - point.y()) / pSY))
			bVal = None
			try:
				bVal = float(cfg.utls.readArrayBlock(OrB, pixelStartColumn, pixelStartRow, 1, 1))
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			if bVal is not None:
				try:
					if str(bVal).lstrip('[').rstrip(']') == 'nan':
						pass
					elif NoDataValue is not None and float(bVal) == float(NoDataValue):
							pass
					elif stratified is not None:
						try:
							if eval(stratifiedExpression.replace(cfg.variableName, 'bVal')) is True:
								points.append([XCoords[0], YCoords[0]])
						except:
							pass
						if counter == pointNumber*100 and len(points) == 0:
							# logger
							cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR : maximum number of iterations" )
							cfg.mx.msgErr64()
							return points
					else:
						points.append([XCoords[0], YCoords[0]])
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		return points
			
	# count pixels in a raster lower than value
	def rasterValueCount(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == 'Yes':
			sum = ((rasterArray <= functionVariable) & (rasterArray != functionBandArgumentNoData)).sum()
			cfg.rasterBandPixelCount = cfg.rasterBandPixelCount + sum
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.rasterBandPixelCount
						
	# count pixels in a raster equal to value
	def rasterEqualValueCount(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == 'Yes':
			sum = (rasterArray == functionVariable).sum()
			cfg.rasterBandPixelCount = cfg.rasterBandPixelCount + sum
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return cfg.rasterBandPixelCount
			
	# calculate sum raster unique values
	def rasterSumUniqueValues(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		if cfg.actionCheck == 'Yes':
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
	def rasterPixelCount(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):
		try:
			bool(cfg.rasterClassSignature)
		except:
			cfg.rasterClassSignature = {}
		i = functionBandArgument
		a = rasterSCPArrayfunctionBand.ravel()
		rasterSCPArrayfunctionBand = None
		a = a[~cfg.np.isnan(a)]
		count = a.shape[0]
		try:
			cfg.rasterClassSignature['COUNT_BAND_' + str(i)] = cfg.rasterClassSignature['COUNT_BAND_' + str(i)] + count
		except:
			cfg.rasterClassSignature['COUNT_BAND_' + str(i)] = count
		sum = a.sum()
		try:
			cfg.rasterClassSignature['SUM_BAND_' + str(i)] = cfg.rasterClassSignature['SUM_BAND_' + str(i)] + sum
		except:
			cfg.rasterClassSignature['SUM_BAND_' + str(i)] = sum
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'cfg.rasterClassSignature ' + str(cfg.rasterClassSignature))
		return cfg.rasterClassSignature
			
	# covariance in a raster
	def rasterCovariance(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):
		try:
			bool(cfg.rasterClassSignature)
		except:
			cfg.rasterClassSignature = {}
		preClassSignature = functionVariableList
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionBandArgument ' + str(functionBandArgument))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'preClassSignature ' + str(preClassSignature))
		# covariance
		for i in functionBandArgument:
			xx = rasterSCPArrayfunctionBand[::, ::, int(i[0])].ravel()
			yy = rasterSCPArrayfunctionBand[::, ::, int(i[1])].ravel()
			x = xx[~cfg.np.isnan(xx)&~cfg.np.isnan(yy)]
			y = yy[~cfg.np.isnan(xx)&~cfg.np.isnan(yy)]
			xx = None
			yy = None
			cov = ( (x - preClassSignature['MEAN_BAND_' + str(i[0])]) * (y - preClassSignature['MEAN_BAND_' + str(i[1])]) ).sum() / (preClassSignature['COUNT_BAND_' + str(i[0])] - 1)
			try:
				cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1])] = cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1])] + cov
			except:
				cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1])] = cov	
		# variance
		for f in range(0, rasterSCPArrayfunctionBand.shape[2]):
			x = rasterSCPArrayfunctionBand[::, ::, int(f)].ravel()
			x = x[~cfg.np.isnan(x)]
			# (x - M) * (x - M)
			cov = ( (x - preClassSignature['MEAN_BAND_' + str(f)]) * (x - preClassSignature['MEAN_BAND_' + str(f)]) ).sum() / (preClassSignature['COUNT_BAND_' + str(f)] - 1)
			try:
				cfg.rasterClassSignature['COV_BAND_' + str(f) + '-' + str(f)] = cfg.rasterClassSignature['COV_BAND_' + str(f) + '-' + str(f)] + cov
			except:
				cfg.rasterClassSignature['COV_BAND_' + str(f) + '-' + str(f)] = cov
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'cfg.rasterClassSignature ' + str(cfg.rasterClassSignature))
		return cfg.rasterClassSignature
			
	# count pixels in a raster
	def rasterPixelCountClassSignature(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgument, functionVariableList, outputBandNumber):
		try:
			bool(cfg.rasterClassSignature)
		except:
			cfg.rasterClassSignature = {}
		preClassSignature = functionVariableList
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionBandArgument ' + str(functionBandArgument))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionVariableList ' + str(functionVariableList))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterSCPArrayfunctionBand shape ' + str(rasterSCPArrayfunctionBand.shape))
		b = rasterSCPArrayfunctionBand[::, ::, 0].ravel()
		for i in functionBandArgument[0]:
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'i ' + str(i))
			for c in functionBandArgument[1]:
				# logger
				cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'c ' + str(c))
				a = rasterSCPArrayfunctionBand[::, ::, i+1].ravel()
				a = a[b == c]
				a = a[~cfg.np.isnan(a)]
				count = a.shape[0]
				if count > 0:
					try:
						cfg.rasterClassSignature['COUNT_BAND_' + str(i) + '_c_' + str(c)] = cfg.rasterClassSignature['COUNT_BAND_' + str(i) + '_c_' + str(c)] + count
					except:
						cfg.rasterClassSignature['COUNT_BAND_' + str(i) + '_c_' + str(c)] = count
					amin = cfg.np.nanmin(a)
					amax = cfg.np.nanmax(a)
					try:
						cfg.rasterClassSignature['MINIMUM_BAND_' + str(i) + '_c_' + str(c)] = min(amin, cfg.rasterClassSignature['MINIMUM_BAND_' + str(i) + '_c_' + str(c)])
					except:
						cfg.rasterClassSignature['MINIMUM_BAND_' + str(i) + '_c_' + str(c)] = amin
					try:
						cfg.rasterClassSignature['MAXIMUM_BAND_' + str(i) + '_c_' + str(c)] = max(amax, cfg.rasterClassSignature['MAXIMUM_BAND_' + str(i) + '_c_' + str(c)])
					except:
						cfg.rasterClassSignature['MAXIMUM_BAND_' + str(i) + '_c_' + str(c)] = amax
					sum = a.sum()
					try:
						cfg.rasterClassSignature['SUM_BAND_' + str(i) + '_c_' + str(c)] = cfg.rasterClassSignature['SUM_BAND_' + str(i) + '_c_' + str(c)] + sum
					except:
						cfg.rasterClassSignature['SUM_BAND_' + str(i) + '_c_' + str(c)] = sum	
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'cfg.rasterClassSignature ' + str(cfg.rasterClassSignature))
		return cfg.rasterClassSignature
			
	# count for standard deviation in a raster
	def rasterStandardDeviationClassSignature(self, gdalBand, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgument, functionVariableList, outputBandNumber):
		try:
			bool(cfg.rasterClassSignature)
		except:
			cfg.rasterClassSignature = {}
		cl = rasterArray[::, ::, 0].ravel()
		i = functionBandArgument
		preClassSignature = functionVariableList
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionBandArgument ' + str(functionBandArgument))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'preClassSignature ' + str(preClassSignature))
		for i in functionBandArgument[0]:
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'i ' + str(i))
			for c in functionBandArgument[1]:
				xx = rasterArray[::, ::, int(i[0]+1)].ravel()
				xx = xx[cl == c]
				yy = rasterArray[::, ::, int(i[1]+1)].ravel()
				yy = yy[cl == c]
				x = xx[~cfg.np.isnan(xx)&~cfg.np.isnan(yy)]
				y = yy[~cfg.np.isnan(xx)&~cfg.np.isnan(yy)]
				xx = None
				yy = None
				a = x - preClassSignature['MEAN_BAND_' + str(i[0]) + '_c_' + str(c)]
				b = y - preClassSignature['MEAN_BAND_' + str(i[1]) + '_c_' + str(c)]
				d = a * b
				cov = d.sum() / (preClassSignature['COUNT_BAND_' + str(i[0]) + '_c_' + str(c)] - 1)
				try:
					cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1]) + '_c_' + str(c)] = cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1]) + '_c_' + str(c)] + cov
				except:
					cfg.rasterClassSignature['COV_BAND_' + str(i[0]) + '-' + str(i[1]) + '_c_' + str(c)] = cov	
		# variance
		for f in functionBandArgument[2]:
			for c in functionBandArgument[1]:		
				x = rasterArray[::, ::, int(f+1)].ravel()
				x = x[cl == c]
				x = x[~cfg.np.isnan(x)]					
				a = x - preClassSignature['MEAN_BAND_' + str(f) + '_c_' + str(c)]
				d = a * a
				var = d.sum() / (preClassSignature['COUNT_BAND_' + str(f) + '_c_' + str(c)] - 1)
				try:
					cfg.rasterClassSignature['VAR_BAND_' + str(f) + '_c_' + str(c)] = cfg.rasterClassSignature['VAR_BAND_' + str(f)  + '_c_' + str(c)] + var
				except:
					cfg.rasterClassSignature['VAR_BAND_' + str(f) + '_c_' + str(c)] = var
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'cfg.rasterClassSignature ' + str(cfg.rasterClassSignature))
		return cfg.rasterClassSignature	
			
	# calculate minimum and maximum values in a raster
	def rasterMinimumMaximum(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgumentNoData, functionVariableList, outputBandNumber):
		rasterDict = {}
		for i in range(0, rasterSCPArrayfunctionBand.shape[2]):
			try:
				a = rasterSCPArrayfunctionBand[::, ::, i].ravel()
				amin = cfg.np.nanmin(a)
				amax = cfg.np.nanmax(a)
				rasterDict['MINIMUM_BAND_' + str(i)] = amin
				rasterDict['MAXIMUM_BAND_' + str(i)] = amax
				# logger
				cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterDict ' + str(rasterDict) )
			except Exception as err:
				# logger
				cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		return rasterDict	
					
	# count pixels in a raster
	def rasterPixelCountKmeans(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgumentNoData, functionVariableList, outputBandNumber):
		rasterDict = {}
		b = rasterSCPArrayfunctionBand[::, ::, rasterSCPArrayfunctionBand.shape[2] - 1].ravel()
		for i in range(0, rasterSCPArrayfunctionBand.shape[2] - 1):
			for c in functionVariableList:					
				a = rasterSCPArrayfunctionBand[::, ::, i].ravel()
				a = a[b == c[0]]
				a = a[~cfg.np.isnan(a)]
				count = a.shape[0]
				rasterDict['COUNT_BAND_' + str(i) + '_c_' + str(c[0])] = count
				sum = a.sum()
				rasterDict['SUM_BAND_' + str(i) + '_c_' + str(c[0])] = sum	
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterDict ' + str(rasterDict) )
		return rasterDict
			
	# count for standard deviation in a raster
	def rasterStandardDeviationISODATA(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgumentNoData, functionVariableList, outputBandNumber):
		rasterDict = {}
		b = rasterSCPArrayfunctionBand[::, ::, rasterSCPArrayfunctionBand.shape[2] - 2].ravel()
		# variance
		for i in range(0, rasterSCPArrayfunctionBand.shape[2] - 2):
			for c in functionVariableList[0]:			
				x = rasterSCPArrayfunctionBand[::, ::, int(i)].ravel()
				x = x[b == c[0]]
				# find No data
				NoDtX = cfg.np.where(cfg.np.isnan(x))
				# delete No data
				x = cfg.np.delete(x, NoDtX)
				NoDtX = None
				x = x[~cfg.np.isnan(x)]					
				a = x - functionVariableList[1]['MEAN_BAND_' + str(i) + '_c_' + str(c[0])]
				d = a * a
				var = d.sum() / (functionVariableList[1]['COUNT_BAND_' + str(i) + '_c_' + str(c[0])] - 1)
				rasterDict['VAR_BAND_' + str(i) + '_c_' + str(c[0])] = var
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterDict ' + str(rasterDict) )
		return rasterDict
			
	# count pixels in a raster
	def rasterPixelCountISODATA(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgumentNoData, functionVariableList, outputBandNumber):
		rasterDict = {}
		b = rasterSCPArrayfunctionBand[::, ::, rasterSCPArrayfunctionBand.shape[2] - 2].ravel()
		for i in range(0, rasterSCPArrayfunctionBand.shape[2] - 2):
			for c in functionVariableList:					
				a = rasterSCPArrayfunctionBand[::, ::, i].ravel()
				a = a[b == c[0]]
				a = a[~cfg.np.isnan(a)]
				count = a.shape[0]
				rasterDict['COUNT_BAND_' + str(i) + '_c_' + str(c[0])] = count
				sum = a.sum()
				rasterDict['SUM_BAND_' + str(i) + '_c_' + str(c[0])] = sum
		g = rasterSCPArrayfunctionBand[::, ::, rasterSCPArrayfunctionBand.shape[2] - 1].ravel()
		for c in functionVariableList:		
			d = g[b == c[0]]
			d = d[~cfg.np.isnan(d)]
			sum = d.sum()
			rasterDict['SUM_DIST_' + str(c[0])] = sum
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterDict ' + str(rasterDict))
		return rasterDict
			
	# calculate PCA bands
	def calculatePCABands(self, gdalBandList, rasterSCPArrayfunctionBand, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputRaster, functionBandArgument, functionVariableList, outputBandNumber):
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionVariableList ' + str(functionVariableList))
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'functionBandArgument ' + str(functionBandArgument))
		n = 0
		for i in functionBandArgument:
			try:
				o = (cfg.np.array(i) * rasterSCPArrayfunctionBand).sum(axis=2, dtype=cfg.np.float32)
			except Exception as err:
				return 'No'
			# logger
			cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'o shape ' + str(o.shape))
			# output raster
			oR = cfg.gdalSCP.Open(functionVariableList[n], cfg.gdalSCP.GA_Update)
			cfg.utls.writeRasterBlock(oR, int(outputBandNumber), o, pixelStartColumn, pixelStartRow)
			o = None
			oR = None
			n = n + 1
		return functionVariableList
			
	# mask process
	def maskProcess(self, gdalBandList, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputGdalRasterList, functionBandArgumentNoData, functionVariable):
		# mask
		a = rasterArray[::, ::, 0]
		# raster
		b = rasterArray[::, ::, 1]
		b[b==functionBandArgumentNoData] = cfg.np.nan
		for v in functionVariable:
			o = cfg.np.where(a == v, cfg.np.nan,b)
			b = cfg.np.copy(o)
		a = None
		# create array if not
		if not isinstance(o, cfg.np.ndarray):
			a = cfg.np.zeros((rasterArray.shape[0], rasterArray.shape[1]), dtype=cfg.np.float32)
			try:
				a.fill(o)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
			o = a
		a = cfg.np.nan_to_num(o) * 1.0
		a[cfg.np.isnan(o)] = cfg.np.nan
		o = a
		return o
			
	# spectral distance process
	def spectralDistanceProcess(self, gdalBandList, rasterArray, columnNumber, rowNumber, pixelStartColumn, pixelStartRow, outputArrayFile, functionBandArgumentNoData, functionVariable, outputBandNumber):
		f = functionBandArgumentNoData
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'f ' + str(f) )
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'rasterArray type ' + str(rasterArray.dtype) )
		rasterArray[rasterArray==functionBandArgumentNoData] = cfg.np.nan
		firstArray = rasterArray[::, ::, :rasterArray.shape[2]//2]
		secondArray = rasterArray[::, ::, rasterArray.shape[2]//2:]
		rasterArray = None
		if functionVariable[0] == cfg.algMinDist:
			o = cfg.np.sqrt(((firstArray - secondArray)**2).sum(axis = 2))
		else:
			o = cfg.np.arccos((firstArray * secondArray).sum(axis = 2) / cfg.np.sqrt((firstArray**2).sum(axis = 2) * (secondArray**2).sum(axis = 2))) * 180 / cfg.np.pi
		secondArray = None
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'o type ' + str(o.dtype) )
		# create array if not
		if not isinstance(o, cfg.np.ndarray):
			return 'No'
		return o
			
	# calculate histogram 2d
	def calculateHistogram2d(self, xVal, yVal, binVal, normedVal = False):
		try:
			h, xE, yE = cfg.np.histogram2d(xVal, yVal, bins=binVal, normed=normedVal)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			return [h, xE, yE ]
		except Exception as err:
			cfg.mx.msgErr53()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
			
	# calculate scatter plot
	def calculateScatterPlot(self, vector, field, id, tempROI = 'No', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
		# band set
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			# crs of loaded raster
			b = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][3][0], 'Yes')
			filePath = cfg.utls.layerSource(b)
			crs = cfg.utls.getCrsGDAL(filePath)
		else:
			# crs of loaded raster
			b = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8])
			filePath = cfg.utls.layerSource(b)
			crs = cfg.utls.getCrsGDAL(filePath)
		tLP = cfg.utls.createTempRasterPath('gpkg')
		# create a temp shapefile with a field
		cfg.utls.createEmptyShapefile(crs, tLP, format = 'GPKG')
		mL = cfg.utls.addVectorLayer(tLP)
		try:
			if tempROI == 'No':
				rId = cfg.utls.getIDByAttributes(vector, field, str(id))
			else:
				rId = []
				f = cfg.qgisCoreSCP.QgsFeature()
				for f in vector.getFeatures():
					rId.append(f.id())
		except Exception as err:
			cfg.mx.msgErr54()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'				
		# copy ROI to temp shapefile
		for pI in rId:
			cfg.utls.copyFeatureToLayer(vector, pI, mL)
		# clip by ROI
		tRxs = cfg.utls.createTempRasterPath('tif')
		# band set
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			cfg.utls.checkBandSet(bandSetNumber)
			bandX = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][3][cfg.scatterBandX - 1], 'Yes')
			bandY = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][3][cfg.scatterBandY - 1], 'Yes')
			bandList = [bandX.source(), bandY.source()]
			check = cfg.utls.vectorToRaster(cfg.emptyFN, tLP, cfg.emptyFN, tRxs, bandList[0], None, 'GTiff', 1)
			if check == 'No':
				return 'No'
			bX = cfg.utls.clipRasterByRaster(bandList, tRxs, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Calculating signature'), stats = 'Yes')
		else:
			rS = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
			check = cfg.utls.vectorToRaster(cfg.emptyFN, tLP, cfg.emptyFN, tRxs, rS.source(), None, 'GTiff', 1)
			if check == 'No':
				return 'No'
			# calculate ROI center, height and width
			rCX, rCY, rW, rH = cfg.utls.getShapefileRectangleBox(tLP)
			# subset 
			tLX, tLY, pS = cfg.utls.imageInformation(cfg.bandSetsList[bandSetNumber][8])
			tS = cfg.utls.createTempRasterPath('tif')
			# reduce band size
			pr = cfg.utls.subsetImage(cfg.bandSetsList[bandSetNumber][8], rCX, rCY, int(round(rW/pS + 3)),  int(round(rH/pS + 3)), str(tS), virtual = 'Yes')
			if pr == 'Yes':
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error edge')
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				return pr
			oList = cfg.utls.rasterToBands(tS, cfg.tmpDir, None, 'No', cfg.bandSetsList[cfg.bndSetNumber][6])
			bandList = [oList[cfg.scatterBandX - 1], oList[cfg.scatterBandY - 1]]
			bX = cfg.utls.clipRasterByRaster(bandList, tRxs, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Calculating signature'), stats = 'Yes')
		# band X
		rD = cfg.gdalSCP.Open(bX[0], cfg.gdalSCP.GA_ReadOnly)
		iRB = rD.GetRasterBand(1)
		try:
			o = iRB.GetOffset()
			s = iRB.GetScale()
			if o is None:
				o = 0
			if s is None:
				s = 1
		except:
			o = 0
			s = 1
		xVal = iRB.ReadAsArray()*s+o
		# close bands
		iRB = None
		# close rasters
		rD = None
		# band Y
		rD = cfg.gdalSCP.Open(bX[1], cfg.gdalSCP.GA_ReadOnly)
		iRB = rD.GetRasterBand(1)
		try:
			o = iRB.GetOffset()
			s = iRB.GetScale()
			if o is None:
				o = 0
			if s is None:
				s = 1
		except:
			o = 0
			s = 1
		yVal = iRB.ReadAsArray()*s+o
		# close bands
		iRB = None
		# close rasters
		rD = None
		# calculate histogram
		try:
			xVal2 = xVal[~cfg.np.isnan(xVal)]
			yVal2 = yVal[~cfg.np.isnan(xVal)]
			xVal = xVal2[~cfg.np.isnan(yVal2)]
			yVal = yVal2[~cfg.np.isnan(yVal2)]
			del xVal2
			del yVal2
			xMax = cfg.np.amax(xVal)
			yMax = cfg.np.amax(yVal)
		except Exception as err:
			cfg.mx.msgErr54()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
		if cfg.uiscp.precision_checkBox.isChecked():
			rou = int(cfg.uiscp.precision_comboBox.currentText())			
		elif xMax <= 1.1:
			rou = 3
		else:
			rou = -1
		prc = cfg.np.power(10, -float(rou))
		xMin = cfg.np.amin(xVal)
		xMin = cfg.np.around(xMin, rou) - prc
		xMax = cfg.np.around(xMax, rou) + prc
		xSteps = self.calculateSteps(xMin, xMax, prc)
		yMin = cfg.np.amin(yVal)
		yMin = cfg.np.around(yMin, rou) - prc
		yMax = cfg.np.around(yMax, rou) + prc
		ySteps = self.calculateSteps(yMin, yMax, prc)
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
		
	# subset image by rectangle
	def subsetImageByRectangle(self, rectangle, rasterName, bandList, bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.bndSetNumber
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
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			tLX, tLY, pS = cfg.utls.imageInformation(cfg.bandSetsList[bandSetNumber][3][0])
			# subset 
			for b in bandList:
				tS = cfg.utls.createTempRasterPath('tif')
				pr = cfg.utls.subsetImage(cfg.bandSetsList[bandSetNumber][3][b], rCX, rCY, int(round(rW/pS + 3)),  int(round(rH/pS + 3)), tS)
				if pr == 'Yes':
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error edge')
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					return pr
				bands.append(tS)
		else:
			# subset 
			tLX, tLY, pS = cfg.utls.imageInformation(rasterName)
			tS = cfg.utls.createTempRasterPath('tif')
			pr = cfg.utls.subsetImage(rasterName, rCX, rCY, int(round(rW/pS + 3)),  int(round(rH/pS + 3)), str(tS))
			if pr == 'Yes':
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error edge')
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				return pr
			oList = cfg.utls.rasterToBands(tS, cfg.tmpDir, None, 'No', cfg.bandSetsList[bandSetNumber][6])
			n = 0
			for b in oList:
				if n in bandList:
					bands.append(b)
				n = n + 1
		return bands
			
##################################
	''' Interface functions '''
##################################
	
	# Question box
	def questionBox(self, caption, message):
		i = cfg.QtWidgetsSCP.QWidget()
		q = cfg.QtWidgetsSCP.QMessageBox.question(i, caption, message, cfg.QtWidgetsSCP.QMessageBox.Yes, cfg.QtWidgetsSCP.QMessageBox.No)
		if q == cfg.QtWidgetsSCP.QMessageBox.Yes:
			return 'Yes'
		if q == cfg.QtWidgetsSCP.QMessageBox.No:
			return 'No'

	# show hide input image
	def showHideInputImage(self):
		if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
			i = cfg.tmpVrtDict[cfg.bndSetNumber]
		else:
			i = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8], 'Yes')
		try:
			if i is not None:
				if cfg.inputImageRadio.isChecked():
					cfg.utls.setLayerVisible(i, True)
					cfg.utls.moveLayerTop(i)
				else:
					cfg.utls.setLayerVisible(i, False)
		except:
			pass
			
	# refresh classification combo
	def refreshRasterExtent(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.raster_extent_combo.clear()
		cfg.dlg.raster_extent_combo(cfg.mapExtent)
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				cfg.dlg.raster_extent_combo(l.name())
				
	# refresh classification combo
	def refreshClassificationLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.classification_name_combo.clear()
		cfg.ui.classification_name_combo_2.clear()
		cfg.ui.classification_name_combo_3.clear()
		cfg.ui.classification_name_combo_5.clear()
		cfg.ui.classification_report_name_combo.clear()
		cfg.ui.classification_vector_name_combo.clear()
		cfg.ui.reclassification_name_combo.clear()
		cfg.ui.edit_raster_name_combo.clear()
		cfg.ui.sieve_raster_name_combo.clear()
		cfg.ui.erosion_raster_name_combo.clear()
		cfg.ui.dilation_raster_name_combo.clear()
		cfg.ui.classification_name_combo_4.clear()
		cfg.ui.reference_raster_name_combo.clear()
		cfg.ui.raster_align_comboBox.clear()
		# classification name
		self.clssfctnNm = None
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.classification_layer_combo(l.name())
					cfg.dlg.classification_layer_combo_2(l.name())
					cfg.dlg.classification_layer_combo_3(l.name())
					cfg.dlg.classification_layer_combo_5(l.name())
					cfg.dlg.classification_report_combo(l.name())
					cfg.dlg.classification_to_vector_combo(l.name())
					cfg.dlg.reclassification_combo(l.name())
					cfg.dlg.edit_raster_combo(l.name())
					cfg.dlg.sieve_raster_combo(l.name())
					cfg.dlg.erosion_raster_combo(l.name())
					cfg.dlg.dilation_raster_combo(l.name())
					cfg.dlg.cloud_mask_raster_combo(l.name())
					cfg.dlg.reference_raster_combo(l.name())
					cfg.dlg.project_raster_combo(l.name())
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'classification layers refreshed')
			
	# refresh vector combo
	def refreshVectorLayer(self):
		cfg.ui.vector_name_combo.blockSignals(True)
		cfg.ui.vector_name_combo_2.blockSignals(True)
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.shapefile_comboBox.clear()
		cfg.ui.vector_name_combo.clear()
		cfg.ui.vector_name_combo_2.clear()
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer):
				if (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.Polygon) or (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.MultiPolygon):
					cfg.dlg.shape_clip_combo(l.name())
					cfg.dlg.vector_to_raster_combo(l.name())
					cfg.dlg.vector_edit_raster_combo(l.name())
		cfg.ui.vector_name_combo.blockSignals(False)
		cfg.ui.vector_name_combo_2.blockSignals(False)
		cfg.utls.refreshVectorFields()
		cfg.utls.refreshVectorFields2()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'vector layers refreshed')
			
	# reference layer name
	def refreshVectorFields(self):
		referenceLayer = cfg.ui.vector_name_combo.currentText()
		cfg.ui.field_comboBox.clear()
		l = cfg.utls.selectLayerbyName(referenceLayer)
		try:
			if l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
				f = l.dataProvider().fields()
				for i in f:
					if str(i.typeName()).lower() != 'string':
						cfg.dlg.reference_field_combo(str(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
						
	# reference layer name
	def refreshVectorFields2(self):
		referenceLayer = cfg.ui.vector_name_combo_2.currentText()
		cfg.ui.field_comboBox_2.clear()
		l = cfg.utls.selectLayerbyName(referenceLayer)
		try:
			if l.type() == cfg.qgisCoreSCP.QgsMapLayer.VectorLayer:
				f = l.dataProvider().fields()
				for i in f:
					if str(i.typeName()).lower() != 'string':
						cfg.dlg.reference_field_combo2(str(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		
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
		c = cfg.QtWidgetsSCP.QColorDialog.getColor()
		if c.isValid():
			# logger
			#cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'color')
			return c
			
	# get save file name
	def getSaveFileName(self, parent, text, directory, filterText, extension = None):
		directory = cfg.lastSaveDir
		out = cfg.QtWidgetsSCP.QFileDialog.getSaveFileName(None, text, directory, filterText)
		if len(out[0]) > 0:
			output = out[0].replace('\\', '/')
			output = output.replace('//', '/')
			cfg.lastSaveDir = cfg.osSCP.path.dirname(output)
			if extension is not None:
				if output.lower().endswith(extension):
					return output
				else:
					output = output + '.' + extension
					return output
			else:
				return output
		else:
			return False
						
	# get open file name
	def getOpenFileName(self, parent, text, directory, filterText):
		directory = cfg.lastSaveDir
		out = cfg.QtWidgetsSCP.QFileDialog.getOpenFileName(None, text, directory, filterText)
		cfg.lastSaveDir = cfg.osSCP.path.dirname(out[0])
		return out[0]
							
	# get open file names
	def getOpenFileNames(self, parent, text, directory, filterText):
		directory = cfg.lastSaveDir
		out = cfg.QtWidgetsSCP.QFileDialog.getOpenFileNames(None, text, directory, filterText)
		if len(out) > 0:
			if len(out[0]) > 0:
				cfg.lastSaveDir = cfg.osSCP.path.dirname(out[0][0])
		return out[0]
		
	# get existing directory
	def getExistingDirectory(self, parent, text):
		directory = cfg.lastSaveDir
		out = cfg.QtWidgetsSCP.QFileDialog.getExistingDirectory(None, text, directory)
		cfg.lastSaveDir = out
		return out
			
##################################
	''' QGIS functions '''
##################################

	# get QGIS Proxy settings
	def getQGISProxySettings(self):
		cfg.proxyEnabled = cfg.utls.readRegistryKeys('proxy/proxyEnabled', '')
		cfg.proxyType = cfg.utls.readRegistryKeys('proxy/proxyType', '')
		cfg.proxyHost = cfg.utls.readRegistryKeys('proxy/proxyHost', '')
		cfg.proxyPort = cfg.utls.readRegistryKeys('proxy/proxyPort', '')
		cfg.proxyUser = cfg.utls.readRegistryKeys('proxy/proxyUser', '')
		cfg.proxyPassword = cfg.utls.readRegistryKeys('proxy/proxyPassword', '')
		
	# read registry keys
	def readRegistryKeys(self, key, value):
		rK = cfg.QSettingsSCP()
		val = rK.value(key, value)
		return val
		
	# set QGIS registry value
	def setQGISRegSetting(self, key, value):
		q = cfg.QSettingsSCP()
		q.setValue(key, value)

	# Raster top left origin and pixel size
	def imageInformation(self, imageName):
		try:
			i = cfg.utls.selectLayerbyName(imageName, 'Yes')
			# TopLeft X coord
			tLX = i.extent().xMinimum()
			# TopLeft Y coord
			tLY = i.extent().yMaximum()
			# pixel size
			pS = i.rasterUnitsPerPixelX()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'image: ' + str(imageName) + ' topleft: (' + str(tLX) + ','+ str(tLY) + ')')
			# return a tuple TopLeft X, TopLeft Y, and Pixel size
			return tLX, tLY, pS
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return None, None, None
			
	# Raster size
	def imageInformationSize(self, imageName):
		try:
			i = cfg.utls.selectLayerbyName(imageName, 'Yes')
			# TopLeft X coord
			tLX = i.extent().xMinimum()
			# TopLeft Y coord
			tLY = i.extent().yMaximum()
			# LowRight X coord
			lRY = i.extent().yMinimum()
			# LowRight Y coord
			lRX = i.extent().xMaximum()
			# pixel size
			pSX = i.rasterUnitsPerPixelX()
			pSY = i.rasterUnitsPerPixelX()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'image: ' + str(imageName) + ' topleft: (' + str(tLX) + ','+ str(tLY) + ')')
			# return a tuple TopLeft X, TopLeft Y, and Pixel size
			return tLX, tLY, lRX, lRY, pSX, pSY
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return None, None, None, None, None, None

	# Get CRS of a layer by name thereof
	def getCrs(self, layer):
		if layer is None:
			crs = None
		else:
			rP = layer.dataProvider()
			crs = rP.crs()
		return crs
		
	# Pan action
	def pan(self):
		cfg.toolPan = cfg.qgisGuiSCP.QgsMapToolPan(cfg.cnvs)
		cfg.cnvs.setMapTool(cfg.toolPan)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'pan action')

	# Project point coordinates
	def projectPointCoordinates(self, point, inputCoordinates, outputCoordinates):
		try:
			# spatial reference
			iSR = cfg.osrSCP.SpatialReference()
			iSR.ImportFromWkt(inputCoordinates.toWkt())
			oSR = cfg.osrSCP.SpatialReference()
			oSR.ImportFromWkt(outputCoordinates.toWkt())
			# required by GDAL 3 coordinate order
			try:
				iSR.SetAxisMappingStrategy(cfg.osrSCP.OAMS_TRADITIONAL_GIS_ORDER)
				oSR.SetAxisMappingStrategy(cfg.osrSCP.OAMS_TRADITIONAL_GIS_ORDER)
			except:
				pass
			# Coordinate Transformation
			cT = cfg.osrSCP.CoordinateTransformation(iSR, oSR)
			pointT = cfg.ogrSCP.Geometry(cfg.ogrSCP.wkbPoint)
			pointT.AddPoint(point.x(), point.y())
			pointT.Transform(cT)
			pointTQ = cfg.qgisCoreSCP.QgsPointXY(pointT.GetX(), pointT.GetY())
			return pointTQ
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return False

	# Project point coordinates
	def projectPointCoordinatesOGR(self, pointX, pointY, inputCoordinates, outputCoordinates):
		try:
			# spatial reference
			iSR = inputCoordinates
			oSR = outputCoordinates
			# required by GDAL 3 coordinate order
			try:
				iSR.SetAxisMappingStrategy(cfg.osrSCP.OAMS_TRADITIONAL_GIS_ORDER)
				oSR.SetAxisMappingStrategy(cfg.osrSCP.OAMS_TRADITIONAL_GIS_ORDER)
			except:
				pass
			# Coordinate Transformation
			cT = cfg.osrSCP.CoordinateTransformation(iSR, oSR)
			pointT = cfg.ogrSCP.Geometry(cfg.ogrSCP.wkbPoint)
			pointT.AddPoint(pointX, pointY)
			pointT.Transform(cT)
			return [pointT.GetX(), pointT.GetY()]
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return False

	# Find group by its name
	def groupIndex(self, groupName):
		root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
		p = root.findGroup(groupName)
		return p
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'group ' + str(groupName) + ' Position: ' + str(p))

	# Layer ID by its name
	def layerID(self, layerName, trainingID):
		lsx = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		for lx in lsx:
			lN = lx.name()
			if lN == layerName:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'layer: ' + str(layerName) + ' ID: ' + str(lx.id()))
				if lx.id() != trainingID:
					return lx.id()

	# read project variable
	def readProjectVariable(self, variableName, value):
		p = cfg.qgisCoreSCP.QgsProject.instance()
		v = p.readEntry('SemiAutomaticClassificationPlugin', variableName, value)[0]
		cfg.QtWidgetsSCP.qApp.processEvents()
		return v
		
	# read QGIS path project variable
	def readQGISVariablePath(self):
		cfg.projPath = cfg.qgisCoreSCP.QgsProject.instance().fileName()
		p = cfg.qgisCoreSCP.QgsProject.instance()
		v = p.readEntry('Paths', 'Absolute', '')[0]
		cfg.absolutePath = v
		
	# read QGIS font project variable
	def readQGISVariableFont(self):
		s = cfg.qgisCoreSCP.QgsSettings()
		f = s.value('qgis/stylesheet/fontFamily')
		size = s.value('qgis/stylesheet/fontPointSize')
		i = s.value('qgis/stylesheet/iconSize')
		return [f, size, i]
		
	# write project variable
	def writeProjectVariable(self, variableName, value):
		if cfg.skipRegistry is False:
			p = cfg.qgisCoreSCP.QgsProject.instance()
			p.writeEntry('SemiAutomaticClassificationPlugin', variableName, value)
			cfg.QtWidgetsSCP.qApp.processEvents()
			# logger
			#cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'variable: ' + str(variableName) + ' - value: ' + str(value))
		
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
			cfg.qgisCoreSCP.QgsProject.instance().removeMapLayer(self.layerID(layerName))
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'layer: ' + str(layerName))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))	
			
	# Remove layer from map
	def removeLayerByLayer(self, layer):
		try:
			cfg.qgisCoreSCP.QgsProject.instance().removeMapLayer(layer.id())
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			
	# Remove layer from map
	def removeGroup(self, groupName):
		root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
		g = root.findGroup(groupName)
		try:
			if g is not None:
				root.removeChildNode(g)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'group: ' + str(groupName))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))

	# remove temporary files from project
	def removeTempFiles(self):
		# disable map canvas render
		cfg.cnvs.setRenderFlag(False)
		try:
			for p in cfg.prevList:
				pp = cfg.utls.selectLayerbyName(p.name())
				if pp is not None:
					cfg.utls.removeLayerByLayer(p)
			for i in range(0, len(cfg.bandSetsList)):			
				vrt = cfg.utls.selectLayerbyName(cfg.bndSetVrtNm + str(i + 1))
				if vrt is not None:
					cfg.utls.removeLayerByLayer(vrt)
			cfg.utls.removeGroup(cfg.grpNm)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		cfg.prevList = []
		cfg.tmpVrtDict[cfg.bndSetNumber] = None
		# remove layers with the same name as training input
		try:
			scpPath = cfg.utls.readProjectVariable('trainingLayer', '')
			name = cfg.utls.fileNameNoExt(scpPath)
			duplicateID = cfg.utls.layerID(name, cfg.shpLay.id())
			cfg.qgisCoreSCP.QgsProject.instance().removeMapLayer(duplicateID)
		except:
			pass
		# enable map canvas render
		cfg.cnvs.setRenderFlag(True)
		
	# create KML from map
	def createKMLFromMap(self):
		cfg.uiUtls.addProgressBar()
		cfg.uiUtls.updateBar(10)
		ext1 = cfg.cnvs.extent()
		pCrs = cfg.utls.getQGISCrs()
		crswgs84 = cfg.qgisCoreSCP.QgsCoordinateReferenceSystem(4326)
		cfg.utls.setQGISCrs(crswgs84)
		cfg.cnvs.refreshAllLayers()
		cfg.QtWidgetsSCP.qApp.processEvents()
		cfg.uiUtls.updateBar(30)
		cfg.timeSCP.sleep(1)
		cfg.QtWidgetsSCP.qApp.processEvents()
		ext = cfg.cnvs.extent()
		# date time for temp name
		dT = cfg.utls.getTime()
		tPMN = cfg.kmlNm
		tPMD = cfg.tmpDir + "/" + dT + tPMN + ".png"
		tPMD2 = cfg.tmpDir + "/" + tPMN + ".kml"
		cfg.cnvs.setCanvasColor(cfg.QtSCP.transparent)
		cfg.cnvs.saveAsImage(tPMD)
		xml = '''<?xml version="1.0" encoding="UTF-8"?>
			 <kml xmlns="http://www.opengis.net/kml/2.2">
			  <GroundOverlay>
			   <name>%s</name>
			   <Icon>
			    <href>%s</href>
			   </Icon>
			   <LatLonBox>
			   <north>%.10f</north>
			   <south>%.10f</south>
			   <east>%.10f</east>
			   <west>%.10f</west>
			   </LatLonBox>
			   <Camera>       
			    <longitude>%.10f</longitude>       
			    <latitude>%.10f</latitude>       
			   <altitude>5000</altitude>
			</Camera>
			  </GroundOverlay>
			 </kml>
			'''
		source = xml % (tPMN, dT + tPMN + ".png", ext.yMaximum(), ext.yMinimum(), ext.xMaximum(), ext.xMinimum(), (ext.xMaximum() + ext.xMinimum())/2, (ext.yMinimum() + ext.yMaximum())/2)
		l = open(tPMD2, 'w')
		try:
			l.write(source)
			l.close()
		except:
			pass
		if cfg.osSCP.path.isfile(tPMD2):
			if cfg.sysSCPNm == 'Darwin':
				sP = cfg.subprocessSCP.call(('open', tPMD2))
			elif cfg.sysSCPNm == 'Windows':
				cfg.osSCP.startfile(tPMD2)
			else:
				sP = cfg.subprocessSCP.call(('xdg-open', tPMD2))
		cfg.utls.setQGISCrs(pCrs)
		cfg.cnvs.setExtent(ext1)
		cfg.cnvs.refreshAllLayers()
		cfg.uiUtls.updateBar(100)
		cfg.uiUtls.removeProgressBar()
			
	# Create group
	def createGroup(self, groupName):
		root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
		g = root.insertGroup(0, groupName)
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group: " + str(groupName))
		return g		
	
	# Move group to top layers
	def moveGroup(self, groupName):
		try:
			root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
			g = root.findGroup(groupName)
			cG = g.clone()
			root.insertChildNode(0, cG)
			root.removeChildNode(g)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group: " + str(groupName))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			
	# Set group visibile
	def setGroupVisible(self, groupIndex, visible = False):
		try:
			root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
			cfg.qgisCoreSCP.QgsLayerTreeNode.setItemVisibilityChecked(groupIndex, visible)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group: " + str(groupIndex))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					
	# Set group expanded
	def setGroupExpanded(self, groupIndex, expanded = False):
		try:
			root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
			cfg.qgisCoreSCP.QgsLayerTreeNode.setExpanded(groupIndex, expanded)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "group: " + str(groupIndex))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		
	# Move layer to top layers
	def moveLayerTop(self, layer):
		try:
			root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
			g = root.findLayer(layer.id())
			cG = g.clone()
			root.insertChildNode(0, cG)
			root.removeChildNode(g)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer: " + str(layer.name()))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				
	# Move layer in group
	def moveLayer(self, layer, groupName):
		try:
			root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
			g = root.findLayer(layer.id())
			a = root.findGroup(groupName)
			a.insertLayer(0, layer)
			root.removeChildNode(g)
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer: " + str(layer.name()))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))

	# Set layer visible
	def setLayerVisible(self, layer, visible = True):
		root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
		g = root.findLayer(layer.id())
		cfg.qgisCoreSCP.QgsLayerTreeNode.setItemVisibilityChecked(g, visible)
		
	# Refresh layer Symbology
	def refreshLayerSymbology(self, layer):
		root = cfg.qgisCoreSCP.QgsProject.instance().layerTreeRoot()
		model = cfg.iface.layerTreeView().model()
		try:
			g = root.findLayer(layer.id())
			model.refreshLayerLegend(g)
		except:
			cfg.iface.layerTreeView().refreshLayerSymbology(layer.id())

	# Select layer by name thereof
	def selectLayerbyName(self, layerName, filterRaster=None):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		for l in ls:
			lN = l.name()
			if lN == layerName:
				if filterRaster is None:
					return l
				else:
					try:
						if l.type().value == 1:
							return l
					except:
						if l.type() == cfg.qgisCoreSCP.QgsMapLayer.RasterLayer:
							return l
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "layer selected: " + str(layerName))
	
	# file path
	def getFilePath(self, layerName):
		try:
			l = cfg.utls.selectLayerbyName(layerName)
			filePath = cfg.utls.layerSource(l)
			return filePath
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
	
	# set map extent from layer
	def setMapExtentFromLayer(self, layer):
		ext = layer.extent()
		tLPoint = cfg.qgisCoreSCP.QgsPointXY(ext.xMinimum(), ext.yMaximum())
		lRPoint = cfg.qgisCoreSCP.QgsPointXY(ext.xMaximum(), ext.yMinimum())
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
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				point1 = tLPoint
				point2 = lRPoint
		cfg.cnvs.setExtent(cfg.qgisCoreSCP.QgsRectangle(point1, point2))
		
	# save a qml style
	def saveQmlStyle(self, layer, stylePath):
		layer.saveNamedStyle(stylePath)
		
	# Zoom to selected feature of layer
	def zoomToSelected(self, layer, featureIDList):
		layer.removeSelection()
		for featureID in featureIDList:
			layer.select(featureID)
		cfg.cnvs.zoomToSelected(layer)
		layer.removeSelection()
		
	# Zoom to band set
	def zoomToBandset(self):
		if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
			try:
				b = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][3][0], 'Yes')
			except:
				b = None
		else:
			b = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8], 'Yes')
		if b is not None:
			cfg.utls.setMapExtentFromLayer(b)
			cfg.cnvs.refresh()
			
	# Add layer to map
	def addLayerToMap(self, layer):
		cfg.qgisCoreSCP.QgsProject.instance().addMapLayers([layer])
		
	# Add layer
	def addVectorLayer(self, path, name = None, format = None):
		if name is None:
			name = cfg.utls.fileNameNoExt(path)
		if format is None:
			format = 'ogr'
		l = cfg.qgisCoreSCP.QgsVectorLayer(path, name, format)
		return l
		
	# Add raster layer or band to band set
	def addRasterOrBand(self, path = None, name = None, bandSetNumber = None, wavelengthString = None):
		if path is None:
			image = cfg.utls.selectLayerbyName(name, 'Yes')
			if image is not None and bandSetNumber is not None:
				cfg.bst.addBandToBandSet(name, bandSetNumber, wavelengthString)
				return 'Yes'
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error not raster: ' + str(name) )
				return 'No'
		else:
			cfg.utls.addRasterLayer(path, name, bandSetNumber, wavelengthString)

	# Add raster layer
	def addRasterLayer(self, path, name = None, bandSetNumber = None, wavelengthString = None):
		if cfg.osSCP.path.isfile(path):
			if name is None:
				name = cfg.utls.fileNameNoExt(path)
			r = cfg.iface.addRasterLayer(path, name)
			r.setName(name)
			if bandSetNumber is not None:
				cfg.bst.addBandToBandSet(name, bandSetNumber, wavelengthString)
			return r
		else:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " not file: " + str(path) )
			return 'No'

	# Get QGIS project CRS
	def getQGISCrs(self):
		pCrs = cfg.cnvs.mapSettings().destinationCrs()
		return pCrs
		
	# Set QGIS project CRS
	def setQGISCrs(self, crs):
		cfg.cnvs.setDestinationCrs(crs)
		
	# layer source
	def layerSource(self, layer):
		s = layer.source().split("|layername=")[0]
		return s
		
	# save memory layer to shapefile
	def saveMemoryLayerToShapefile(self, memoryLayer, output, name = None, format = 'ESRI Shapefile', IDList = None, listFieldName = None):
		shpF = output
		try:
			if format == 'ESRI Shapefile':
				cfg.utls.createSCPShapefile(memoryLayer.crs(), shpF)
			else:
				cfg.utls.createSCPVector(memoryLayer.crs(), shpF, format = format)
			if name is None:
				name = cfg.utls.fileName(shpF)
			tSS = cfg.utls.addVectorLayer(shpF, name, 'ogr')
			tSS.updateFields()
			f = cfg.qgisCoreSCP.QgsFeature()
			tSS.startEditing()
			if IDList is None:
				for f in memoryLayer.getFeatures():
					tSS.addFeature(f)
			else:
				for f in memoryLayer.getFeatures():
					UID  = str(f[listFieldName])
					if UID in IDList:
						tSS.addFeature(f)
			tSS.commitChanges()
			tSS.dataProvider().createSpatialIndex()
			tSS.updateExtents()
			return tSS
		# in case of errors
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return None
			
	# duplicate memory layer
	def duplicateMemoryLayer(self, layer):
		# create memory layer
		provider = layer.dataProvider()
		fields = provider.fields().toList()
		pCrs = cfg.utls.getCrs(layer)
		dT = cfg.utls.getTime()
		mL2 = cfg.qgisCoreSCP.QgsVectorLayer('MultiPolygon?crs=' + str(pCrs.toWkt()), dT, 'memory')
		mL2.setCrs(pCrs)
		pr2 = mL2.dataProvider()
		pr2.addAttributes(fields)
		mL2.updateFields()
		f = cfg.qgisCoreSCP.QgsFeature()
		mL2.startEditing()
		for f in layer.getFeatures():
			mL2.addFeature(f)
		mL2.commitChanges()
		mL2.dataProvider().createSpatialIndex()
		mL2.updateExtents()
		return mL2
	
	# save features to shapefile
	def featuresToShapefile(self, idList):
		# create shapefile
		crs = cfg.utls.getCrs(cfg.shpLay)
		f = cfg.qgisCoreSCP.QgsFields()
		# add Class ID, macroclass ID and Info fields
		f.append(cfg.qgisCoreSCP.QgsField('fid', cfg.QVariantSCP.Int))
		f.append(cfg.qgisCoreSCP.QgsField(cfg.fldMacroID_class, cfg.QVariantSCP.Int))
		f.append(cfg.qgisCoreSCP.QgsField(cfg.fldROIMC_info, cfg.QVariantSCP.String))
		f.append(cfg.qgisCoreSCP.QgsField(cfg.fldID_class, cfg.QVariantSCP.Int))
		f.append(cfg.qgisCoreSCP.QgsField(cfg.fldROI_info, cfg.QVariantSCP.String))
		f.append(cfg.qgisCoreSCP.QgsField(cfg.fldSCP_UID, cfg.QVariantSCP.String))
		# shapefile
		shpF = cfg.utls.createTempRasterPath('shp')
		try:
			cfg.qgisCoreSCP.QgsVectorFileWriter(shpF, 'CP1250', f, cfg.qgisCoreSCP.QgsWkbTypes.MultiPolygon , crs, 'ESRI Shapefile')
			tSS = cfg.utls.addVectorLayer(shpF)
			f = cfg.qgisCoreSCP.QgsFeature()
			tSS.startEditing()
			count = 0
			for f in cfg.shpLay.getFeatures():
				SCP_UID  = str(f[cfg.fldSCP_UID])
				if SCP_UID in idList:
					a = tSS.addFeature(f)
					count = count + 1
			if count == 0:
				tSS.commitChanges()
				cfg.utls.removeLayerByLayer(tSS)
				return None
			tSS.commitChanges()
			tSS.dataProvider().createSpatialIndex()
			tSS.updateExtents()
			cfg.utls.removeLayerByLayer(tSS)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' vector exported ')
			return shpF	
		# in case of errors
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return None
		
##################################
	''' raster GDAL functions '''
##################################
			
	# Get the number of bands of a raster
	def getNumberBandRaster(self, raster):
		rD = cfg.gdalSCP.Open(raster, cfg.gdalSCP.GA_ReadOnly)
		number = rD.RasterCount
		rD = None
		return number
		
	# Raster no data value
	def imageNoDataValue(self, rasterPath):
		rD = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_ReadOnly)
		gBand = rD.GetRasterBand(1) 
		nd = gBand.GetNoDataValue()
		gBand = None
		rD = None
		return nd
			
	# Get CRS of a layer raster or vector
	def getCrsGDAL(self, layerPath):
		l = cfg.ogrSCP.Open(layerPath)
		if l is None:
			l = cfg.gdalSCP.Open(layerPath, cfg.gdalSCP.GA_ReadOnly)
			if l is None:
				crs = None
			else:
				try:
					# check projections
					crs = l.GetProjection()
					if len(crs) == 0:
						crs = None
				# in case of errors
				except Exception as err:
					crs = None
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		else:
			gL = l.GetLayer()
			# check projection
			lP = gL.GetSpatialRef()
			try:
				crs = lP.ExportToWkt()
				if len(crs) == 0:
					crs = None
			# in case of errors
			except Exception as err:
				crs = None
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' lyr ' + str(layerPath) + ' crs: ' + str(crs))
		return crs
		
	# raster sieve with GDAL
	def rasterSieve(self, inputRaster, outputRaster, pixelThreshold, connect = 4, outFormat = 'GTiff', quiet = 'No'):
		if cfg.sysSCPNm == 'Windows':
			gD = 'gdal_sieve.bat'
		else:
			gD = 'gdal_sieve.py'
		st = 'No'
		cfg.utls.getGDALForMac()
		# copy input to temp to prevent path issue
		dT = cfg.utls.getTime()
		tempRaster = cfg.osSCP.path.join(cfg.tmpDir, dT + cfg.osSCP.path.splitext(inputRaster)[1])
		cfg.shutilSCP.copy(inputRaster, tempRaster)
		tempOut = cfg.utls.createTempRasterPath('tif')
		a = cfg.gdalPath + gD + ' -st ' + str(pixelThreshold) + ' -' + str(connect) + ' ' + tempRaster + ' -of '+ outFormat + ' ' + tempOut
		if cfg.sysSCPNm != 'Windows':
			a = cfg.shlexSCP.split(a)
		tPMD = cfg.utls.createTempRasterPath('txt')
		stF = open(tPMD, 'a')
		sPL = len(cfg.subprocDictProc)
		if cfg.sysSCPNm == 'Windows':
			startupinfo = cfg.subprocessSCP.STARTUPINFO()
			startupinfo.dwFlags = cfg.subprocessSCP.STARTF_USESHOWWINDOW
			startupinfo.wShowWindow = cfg.subprocessSCP.SW_HIDE
			cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(a, shell=False, startupinfo = startupinfo, stdout=stF, stderr=cfg.subprocessSCP.PIPE, stdin = cfg.subprocessSCP.DEVNULL)
		else:
			cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(a, shell=False, stdout=stF, stderr=cfg.subprocessSCP.PIPE)
		while True:
			line = ''
			with open(tPMD, 'r') as rStF:
				for line in rStF:
					pass
			poll = cfg.subprocDictProc['proc_'+ str(sPL)].poll()
			if poll != None:
				break
			else:
				try:
					progress = int(line.split('...')[-1].strip('.'))
					try:
						dots = dots + '.'
						if len(dots) > 3:
							dots = ''
					except:
						dots = ''
					cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Sieve') + dots)
				except:
					pass
			cfg.QtWidgetsSCP.qApp.processEvents()
			if cfg.actionCheck != 'Yes':
				break
			cfg.timeSCP.sleep(1)
		stF.close()
		try:
			# get error
			out, err = cfg.subprocDictProc['proc_'+ str(sPL)].communicate()
			if len(err) > 0:
				st = 'Yes'
				if quiet == 'No': 
					cfg.mx.msgErr45()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " GDAL error: " + str(err) )
				return 'No'
		# in case of errors
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
		# copy output
		try:
			cfg.shutilSCP.move(tempOut, outputRaster)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
		# remove temp layers
		try:
			cfg.osSCP.remove(tempRaster)
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "sieve: " + str(outputRaster))
		return st
	
	# build band overviews
	def buildOverviewsBandSet(self, directory = 'Yes', quiet = 'No', bandSetNumber = None):
		if bandSetNumber is None:
			bandSetNumber = cfg.ui.Band_set_tabWidget.currentIndex()
		tW = eval('cfg.ui.tableWidget__' + cfg.bndSetTabList[bandSetNumber])
		c = tW.rowCount()
		# check if single raster
		if c > 0:
			if directory == 'Yes':
				a = 'Yes'
			else:
				# ask for confirm
				a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Build overviews'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Do you want to build the external overviews of bands?'))
			if a == 'Yes':	
				if quiet == 'No':
					cfg.uiUtls.addProgressBar()
				if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
					cfg.uiUtls.updateBar(20, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Building overviews'))
					b = 1
					for i in cfg.bndSetLst:
						# pool
						cfg.pool = cfg.poolSCP(processes=1)
						p = 0
						memVal = str(int(cfg.RAMValue * 0.8)*1000000)
						wrtP = [p, cfg.tmpDir, memVal]
						results = []
						c = cfg.pool.apply_async(self.buildOverviewsGDAL, args=(i, wrtP))
						results.append([c, p])
						cfg.QtWidgetsSCP.qApp.processEvents()
						while cfg.actionCheck == 'Yes':
							pR = []
							for r in results:
								pR.append(r[0].ready())
							if all(pR):
								break
							cfg.timeSCP.sleep(1)
							try:
								dots = dots + '.'
								if len(dots) > 3:
									dots = ''
							except:
								dots = ''
							cfg.uiUtls.updateBar('', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Building overviews') + dots)
							cfg.QtWidgetsSCP.qApp.processEvents()
						for r in results:
							if cfg.actionCheck == 'Yes':
								res = r[0].get()
								if len(str(res[1])) > 0:
									# logger
									cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error proc '+ str(p) + '-' + str(res[1]))
									return 'No'
							else:
								cfg.pool.close()
								cfg.pool.terminate()
								return 'No'
						cfg.pool.close()
						cfg.pool.terminate()
						b = b + 1
						cfg.uiUtls.updateBar(20 + b * 80 / (len(cfg.bndSetLst)), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Building overviews'))
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image: " + str(i))
				else:
					image = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
					i = cfg.utls.layerSource(image)
					cfg.uiUtls.updateBar(50, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Building overviews'))
					# pool
					cfg.pool = cfg.poolSCP(processes=1)
					p = 0
					memVal = str(int(cfg.RAMValue * 0.8)*1000000)
					wrtP = [p, cfg.tmpDir, memVal]
					results = []
					c = cfg.pool.apply_async(self.buildOverviewsGDAL, args=(i, wrtP))
					results.append([c, p])
					cfg.QtWidgetsSCP.qApp.processEvents()
					while cfg.actionCheck == 'Yes':
						pR = []
						for r in results:
							pR.append(r[0].ready())
						if all(pR):
							break
						cfg.timeSCP.sleep(1)
						try:
							dots = dots + '.'
							if len(dots) > 3:
								dots = ''
						except:
							dots = ''
						cfg.uiUtls.updateBar('', cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Building overviews') + dots)
						cfg.QtWidgetsSCP.qApp.processEvents()
					for r in results:
						if cfg.actionCheck == 'Yes':
							res = r[0].get()
							if len(str(res[1])) > 0:
								# logger
								cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error proc '+ str(p) + '-' + str(res[1]))
								return 'No'
						else:
							cfg.pool.close()
							cfg.pool.terminate()
							return 'No'
					cfg.pool.close()
					cfg.pool.terminate()
				cfg.uiUtls.updateBar(100)
				if quiet == 'No':
					cfg.utls.finishSound()
					cfg.uiUtls.removeProgressBar()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " all bands clicked")
				
	# build GDAL overviews
	def buildOverviewsGDAL(self, inputRaster, writerLog):
		from . import config as cfg
		import os
		import sys
		import inspect
		import time
		import datetime
		import numpy as np
		from osgeo import gdal
		from osgeo import ogr
		from osgeo import osr
		cfg.osSCP = os
		cfg.sysSCP = sys
		cfg.gdalSCP = gdal
		cfg.ogrSCP = ogr
		cfg.osrSCP = osr
		from .utils import Utils
		cfg.utls = Utils()
		wrtProc = str(writerLog[0])
		cfg.tmpDir = writerLog[1]
		memory = writerLog[2]
		# GDAL config
		try:
			cfg.gdalSCP.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'TRUE')
			cfg.gdalSCP.SetConfigOption('GDAL_CACHEMAX', memory)
			cfg.gdalSCP.SetConfigOption('VSI_CACHE', 'FALSE')
		except:
			pass
		try:
			rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
			rD.BuildOverviews('NEAREST', [8,16,32,64])
			rD = None
			return inputRaster, ''
		# in case of errors
		except Exception as err:
			# logger
			return inputRaster, err

	# Try to get GDAL for Mac
	def getGDALForMac(self):
		if cfg.sysSCPNm == 'Darwin':
			gdalLine = cfg.gdalPath
			if len(gdalLine) > 0:
				cfg.gdalPath = gdalLine.rstrip('/') + '/'
				if cfg.osSCP.path.isfile(cfg.gdalPath + 'gdal_translate'):
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' getGDALForMac: ' + str(cfg.gdalPath))
				else:
					cfg.gdalPath = ''
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' getGDALForMac: ERROR')
			else:
				v = cfg.utls.getGDALVersion()
				cfg.gdalPath = '/Library/Frameworks/GDAL.framework/Versions/' + v[0] + '.' + v[1] + '/Programs/'
				if cfg.osSCP.path.isfile(cfg.gdalPath + 'gdal_translate'):
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' getGDALForMac: ' + str(cfg.gdalPath))
				else:
					cfg.gdalPath = ''
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' getGDALForMac: ERROR')
				
	# Get GDAL version
	def getGDALVersion(self):
		v = cfg.gdalSCP.VersionInfo('RELEASE_NAME').split('.')
		return v
		
	# Get raster data type name
	def getRasterDataTypeName(self, inputRaster):
		rD = cfg.gdalSCP.Open(inputRaster, cfg.gdalSCP.GA_ReadOnly)
		b = rD.GetRasterBand(1)
		dType = cfg.gdalSCP.GetDataTypeName(b.DataType)
		b.FlushCache()
		b = None
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
		if cfg.macroclassCheck == 'Yes':
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
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), "" + str(rasterPath))
				
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
	def GDALCopyRaster(self, input, output, outFormat = 'GTiff', compress = 'No', compressFormat = 'DEFLATE', additionalParams = ''):
		outDir = cfg.osSCP.path.dirname(output)
		cfg.utls.makeDirectory(outDir)
		op = ' -co BIGTIFF=YES -co NUM_THREADS=' + str(cfg.threads) 
		if compress == 'No':
			op = op + ' -of ' + outFormat
		else:
			op = op + ' -co COMPRESS=' + compressFormat + ' -of ' + outFormat
		a = additionalParams + ' ' + op
		# pool
		cfg.pool = cfg.poolSCP(processes=1)
		p = 0
		manager = cfg.MultiManagerSCP()
		# progress queue
		pMQ = manager.Queue()
		memVal = str(int(cfg.RAMValue)*1000000)
		wrtP = [p, cfg.tmpDir, memVal, pMQ]
		results = []
		c = cfg.pool.apply_async(self.gdalTranslate, args=(input, output, a, wrtP))
		results.append([c, p])
		cfg.QtWidgetsSCP.qApp.processEvents()
		while cfg.actionCheck == 'Yes':
			pR = []
			for r in results:
				pR.append(r[0].ready())
			if all(pR):
				break
			try:
				pMQp = pMQ.get(False)
				try:
					dots = dots + '.'
					if len(dots) > 3:
						dots = ''
				except:
					dots = ''
				cfg.uiUtls.updateBar(int(pMQp[0]), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Writing file') + dots)
			except:
				try:
					dots = dots + '.'
					if len(dots) > 3:
						dots = ''
				except:
					dots = ''
				cfg.uiUtls.updateBar(message = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Writing file') + dots)
			cfg.timeSCP.sleep(1)
			cfg.QtWidgetsSCP.qApp.processEvents()
		for r in results:
			if cfg.actionCheck == 'Yes':
				res = r[0].get()
				if len(str(res[1])) > 0:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error proc '+ str(p) + '-' + str(res[1]))
					return 'No'
			else:
				cfg.pool.close()
				cfg.pool.terminate()
				return 'No'
		cfg.pool.close()
		cfg.pool.terminate()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image: " + str(output))
		return output		
			
	# interprocess
	def gdalTranslate(self, input = None, output = None, optionString = None, writerLog = None):
		from . import config as cfg
		import os
		import sys
		import inspect
		import time
		import datetime
		from osgeo import gdal
		from osgeo import ogr
		from osgeo import osr
		cfg.osSCP = os
		cfg.sysSCP = sys
		cfg.inspectSCP = inspect
		cfg.datetimeSCP = datetime
		cfg.gdalSCP = gdal
		cfg.ogrSCP = ogr
		cfg.osrSCP = osr
		from .utils import Utils
		cfg.utls = Utils()
		wrtProc = str(writerLog[0])
		cfg.tmpDir = writerLog[1]
		memory = writerLog[2]
		global progressQueue
		progressQueue = writerLog[3]
		# GDAL config
		try:
			cfg.gdalSCP.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'TRUE')
			cfg.gdalSCP.SetConfigOption('GDAL_CACHEMAX', memory)
			cfg.gdalSCP.SetConfigOption('VSI_CACHE', 'FALSE')
		except:
			pass
		cfg.logFile = cfg.tmpDir + '/log_' + 'gdal'
		# logger
		cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' process: ' + str(wrtProc))
		try:
			progressG = (lambda perc, m, d: progressQueue.put([perc * 100, m], False))
			to = gdal.TranslateOptions(gdal.ParseCommandLine(optionString), callback = progressG)
			gdal.Translate(output, input, options = to)	
			return output, ''
		# in case of errors
		except Exception as err:
			# logger
			return output, err	
			
	# interprocess
	def subprocessStdout(self, input = None, progressQueue = None):
		line = input.readline()
		return line
		
	# reproject raster with GDAL
	def GDALReprojectRaster(self, input, output, outFormat = 'GTiff', s_srs = None,  t_srs = None, additionalParams = None, resampleMethod = None, rasterDataType = None, noDataVal = None, compression = None):
		outDir = cfg.osSCP.path.dirname(output)
		cfg.utls.makeDirectory(outDir)
		if resampleMethod is None:
			resampleMethod = 'near'
		elif resampleMethod == 'sum':
			gdalV = cfg.utls.getGDALVersion()
			if float(gdalV[0] + '.' + gdalV[1]) < 3.1:
				cfg.mx.msgErr68()
				return 'No'
		op = ' --config GDAL_DISABLE_READDIR_ON_OPEN TRUE' + ' --config GDAL_CACHEMAX ' + str(int(cfg.RAMValue * 0.3)*1000000) + ' -co BIGTIFF=YES -co NUM_THREADS=' + str(cfg.threads) + ' -r ' + resampleMethod + ' -multi -wo NUM_THREADS=' + str(cfg.threads)
		if compression is None:
			if cfg.rasterCompression == 'Yes':
				op = op + ' -co COMPRESS=LZW'
		elif compression == 'Yes':
			op = op + ' -co COMPRESS=LZW'
		if s_srs is not None:
			op = op + ' -s_srs ' + s_srs 
		if t_srs is not None:
			op = op + ' -t_srs ' + t_srs 
		if rasterDataType is not None:
			op = op + ' -ot ' + rasterDataType 
		if noDataVal is not None:
			op = op + ' -dstnodata ' + str(noDataVal)
		op = op + ' -of ' + outFormat
		if additionalParams is None:
			pass
		else:
			op = ' ' + additionalParams + ' ' + op
		gD = 'gdalwarp'
		cfg.utls.getGDALForMac()
		a = cfg.gdalPath + gD + op
		if '"' in input:
			b = input
		else:
			b = '"' + input + '" '
		c = '"' + output + '" '
		d = a + ' ' + b + ' ' + c
		if cfg.sysSCPNm != 'Windows':
			d = cfg.shlexSCP.split(d)
		tPMD = cfg.utls.createTempRasterPath('txt')
		stF = open(tPMD, 'a')
		sPL = len(cfg.subprocDictProc)
		if cfg.sysSCPNm == 'Windows':
			startupinfo = cfg.subprocessSCP.STARTUPINFO()
			startupinfo.dwFlags = cfg.subprocessSCP.STARTF_USESHOWWINDOW
			startupinfo.wShowWindow = cfg.subprocessSCP.SW_HIDE
			cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(d, shell=False,startupinfo = startupinfo, stdout=stF, stderr=cfg.subprocessSCP.PIPE, stdin = cfg.subprocessSCP.DEVNULL)
		else:
			cfg.subprocDictProc['proc_'+ str(sPL)] = cfg.subprocessSCP.Popen(d, shell=False, stdout=stF, stderr=cfg.subprocessSCP.PIPE)
		while True:
			line = ''
			with open(tPMD, 'r') as rStF:
				for line in rStF:
					pass
			poll = cfg.subprocDictProc['proc_'+ str(sPL)].poll()
			if poll != None:
				break
			else:
				try:
					progress = int(line.split('...')[-1].strip('.'))
					try:
						dots = dots + '.'
						if len(dots) > 3:
							dots = ''
					except:
						dots = ''
					cfg.uiUtls.updateBar(progress, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Reprojecting') + dots)
				except:
					pass
			cfg.QtWidgetsSCP.qApp.processEvents()
			if cfg.actionCheck != 'Yes':
				break
			cfg.timeSCP.sleep(1)
		stF.close()
		try:
			# get error
			out, err = cfg.subprocDictProc['proc_'+ str(sPL)].communicate()
			if len(err) > 0:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' GDAL error: ' + str(err) )
		# in case of errors
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image: ' + str(output))
		
	# Merge raster bands
	def mergeRasterBands(self, bandList, output, outFormat = 'GTiff', compress = 'No', compressFormat = 'DEFLATE', additionalParams = ''):
		rEPSG = cfg.utls.getEPSGRaster(bandList[0])				
		if rEPSG is None:
			cfg.mx.msgWar28()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
			return 'No'
		for b in range(0, len(bandList)):
			EPSG = cfg.utls.getEPSGRaster(bandList[b])
			if str(EPSG) != str(rEPSG):
				nD = cfg.utls.imageNoDataValue(bandList[b])
				if nD is None:
					nD = cfg.NoDataVal
				tPMD = cfg.utls.createTempRasterPath('tif', name = str(b))
				cfg.utls.GDALReprojectRaster(bandList[b], tPMD, 'GTiff', None, 'EPSG:' + str(rEPSG), '-ot Float32 -dstnodata ' + str(nD))
				if cfg.osSCP.path.isfile(tPMD):
					bandList[b] = tPMD
				else:
					cfg.mx.msgErr60()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
					return 'No'
		tPMD1 = cfg.utls.createTempRasterPath('vrt')
		# create virtual raster					
		vrtCheck = cfg.utls.createVirtualRaster(bandList, tPMD1, 'No', 'Yes', 'Yes', 0)
		if cfg.osSCP.path.isfile(tPMD1):
			if compress == 'No':
				cfg.utls.GDALCopyRaster(tPMD1, output, 'GTiff', compress)
			else:
				cfg.utls.GDALCopyRaster(tPMD1, output, 'GTiff', compress, compressFormat, additionalParams)
			cfg.osSCP.remove(tPMD1)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' image: ' + str(output))
		else:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Error no image ')
			
	# Subset an image, given an origin point and a subset width
	def subsetImage(self, imageName, XCoord, YCoord, Width, Height, output = None, outFormat = 'GTiff', virtual = 'No'):
		if output is None:
			if virtual == 'No':
				output = cfg.utls.createTempRasterPath('tif')
			else:
				output = cfg.utls.createTempRasterPath('vrt')
		i = cfg.utls.selectLayerbyName(imageName, 'Yes')
		# output variable
		st = 'Yes'
		if i is not None:
			bandNumberList = []
			for bb in range(1, i.bandCount()+1):
				bandNumberList.append(bb)
			i = cfg.utls.layerSource(i)
			st = 'No'
			# raster top left origin and pixel size
			tLX, tLY, lRX, lRY, pSX, pSY = self.imageInformationSize(imageName)
			if pSX is None:
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " image none or missing")
			else:		
				try:
					dType = self.getRasterDataTypeName(i)
					# subset origin
					UX = tLX + abs(int((tLX - XCoord) / pSX )) * pSX - (Width -1 )/ 2 * pSX
					UY = tLY - abs(int((tLY - YCoord) / pSY )) * pSY + (Height -1 )/ 2 * pSY
					LX = UX + Width * pSX
					LY = UY - Height * pSY
					tPMD = cfg.utls.createTempRasterPath('vrt')
					bList = [i]
					if virtual == 'No':
						st = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, 'Yes', 'Yes', 0, 'No', 'Yes', [float(UX), float(UY), float(LX), float(LY)])
						cfg.utls.GDALCopyRaster(tPMD, output, 'GTiff', cfg.rasterCompression, 'DEFLATE -co PREDICTOR=2 -co ZLEVEL=1' + ' -a_nodata ' + str(cfg.NoDataVal))
						st = output
					else:
						st = cfg.utls.createVirtualRaster(bList, output, bandNumberList, 'Yes', 'Yes', 0, 'No', 'Yes', [float(UX), float(UY), float(LX), float(LY)])
				# in case of errors
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					st = 'Yes'
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "image: " + str(imageName) + " subset origin: (" + str(XCoord) + ","+ str(YCoord) + ") width: " + str(Width))
		return st
			
	# get values for vector field
	def getVectorFieldfValues(self, layerPath, fieldName):
		d = cfg.gdalSCP.OpenEx(layerPath, cfg.gdalSCP.OF_VECTOR | cfg.gdalSCP.OF_READONLY)
		if d is None:	
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error layer " + layerPath)
			return 'No'
		l = d.GetLayerByName(cfg.utls.fileNameNoExt(layerPath))
		l.ResetReading()
		fieldValues =[]
		try:
			for f in l:
				fieldValues.append(f.GetField(str(fieldName)))
		except Exception as err:
			# logger
			if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			return 'No'
		l.ResetReading()
		l = None
		dr = None
		values = cfg.np.unique(fieldValues).tolist()
		return values	
	
	# get EPSG for vector
	def getEPSGVector(self, layerPath):
		l = cfg.ogrSCP.Open(layerPath)
		if l is None:
			return 'No'
		gL = l.GetLayer()
		# check projection
		lP = cfg.osrSCP.SpatialReference()
		lP = gL.GetSpatialRef()
		if lP is None:
			lPRS = None
		else:
			lP.AutoIdentifyEPSG()
			lPRS = lP.GetAuthorityCode(None)
		# try with QGIS
		if lPRS is None:
			mL = cfg.utls.addVectorLayer(layerPath , "tempA", "ogr")
			lPRStr = mL.crs().authid()
			lPRStr = lPRStr.split(":")
			if lPRStr[0] == "EPSG":
				lPRS = lPRStr[1]
			cfg.utls.removeLayerByLayer(mL)
		try:
			epsg = int(lPRS)
		except Exception as err:
			epsg = None
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		l.Destroy()
		return epsg
			
	# get EPSG for vector QGIS
	def getEPSGVectorQGIS(self, layer):
		pCrs = cfg.utls.getCrs(layer)
		try:
			id = pCrs.authid()
			id = int(id.replace('EPSG:', ''))
		except:
			return None
		return id
		
	# get EPSG for raster
	def getEPSGRaster(self, layerPath):
		epsg = None
		rD = cfg.gdalSCP.Open(layerPath, cfg.gdalSCP.GA_ReadOnly)
		# check projections
		rP = rD.GetProjection()
		rPSys =cfg.osrSCP.SpatialReference(wkt=rP)
		rPSys.AutoIdentifyEPSG()
		rPRS = rPSys.GetAuthorityCode(None)
		rD = None
		# try with QGIS
		if rPRS is None:
			mL = self.addRasterLayer(layerPath)
			lPRStr = mL.crs().authid()
			lPRStr = lPRStr.split(':')
			if lPRStr[0] == 'EPSG':
				rPRS = lPRStr[1]
			cfg.utls.removeLayerByLayer(mL)
		try:
			epsg = int(rPRS)
		except Exception as err:
			cfg.mx.msgErr61(str(layerPath))
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		return epsg
		
	# convert reference layer to raster based on the resolution of a raster
	def vectorToRaster(self, fieldName, layerPath, referenceRasterName, outputRaster, referenceRasterPath=None, ALL_TOUCHED=None, outFormat = 'GTiff', burnValues = None, filter = None, extent = None, noDataValue = 0, backgroundValue =  0):
		if referenceRasterPath is None:
			# band set
			if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
				referenceRasterName = cfg.bandSetsList[cfg.bndSetNumber][3][0]
				# input
				r = cfg.utls.selectLayerbyName(referenceRasterName, 'Yes')
			else:
				if cfg.utls.selectLayerbyName(referenceRasterName, 'Yes') is None:
					cfg.mx.msg4()
					cfg.ipt.refreshRasterLayer()
				else:
					# input
					r = cfg.utls.selectLayerbyName(referenceRasterName, 'Yes')
			try:
				rS = cfg.utls.layerSource(r)
				ck = 'Yes'
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				ck = 'No'
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
			origX = rGT[0]
			origY = rGT[3]
		# in case of errors
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msg4()
			return 'No'
		if not layerPath.lower().endswith('.gpkg'):
			tVect = cfg.utls.createTempRasterPath('gpkg')
			v = cfg.utls.mergeAllLayers([layerPath], tVect)
			layerPath = tVect
		l = cfg.ogrSCP.Open(layerPath)
		try:
			gL = l.GetLayer()
		# in case of errors
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msgErr34()
			return 'No'
		# check projection
		vCrs = cfg.utls.getCrsGDAL(layerPath)
		lPRS = cfg.osrSCP.SpatialReference()
		lPRS.ImportFromWkt(vCrs)
		rPRS = cfg.osrSCP.SpatialReference()
		rPRS.ImportFromWkt(rP)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' rP: ' + str(rP))
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' vCrs: ' + str(vCrs))
		if lPRS is not None:
			# date time for temp name
			dT = cfg.utls.getTime()
			if lPRS.IsSame(rPRS) != 1:
				reprjShapefile = cfg.tmpDir + '/' + dT + cfg.utls.fileName(layerPath)
				try:
					cfg.utls.repojectShapefile(layerPath, lPRS, reprjShapefile, rPRS)
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					cfg.mx.msg9()
					return 'No'
				l.Destroy()
				l = cfg.ogrSCP.Open(reprjShapefile)
				gL = l.GetLayer()
			if filter is not None:
				gL.SetAttributeFilter(filter)
				d = cfg.ogrSCP.GetDriverByName('MEMORY')
				dS = d.CreateDataSource('memData')
				ou = dS.CopyLayer(gL,dS.GetName(),['OVERWRITE=YES'])
				minX, maxX, minY, maxY = ou.GetExtent()
			else:
				minX, maxX, minY, maxY = gL.GetExtent()
			if extent is None:
				origX = rGT[0] +  rGT[1] * int(round((minX - rGT[0]) / rGT[1]))
				origY = rGT[3] + rGT[5] * int(round((maxY - rGT[3]) / rGT[5]))
				rC = abs(int(round((maxX - minX) / rGT[1])))
				rR = abs(int(round((maxY - minY) / rGT[5])))
			tD = cfg.gdalSCP.GetDriverByName(outFormat)
			tPMD2 = cfg.utls.createTempRasterPath('tif')
			oR = tD.Create(tPMD2, rC, rR, 1, cfg.gdalSCP.GDT_Float32)
			if oR is None:
				oR = tD.Create(tPMD2, rC, rR, 1, cfg.gdalSCP.GDT_Int16)
			if oR is None:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: raster size')
				cfg.mx.msgErr65()
				return 'No'
			try:
				oRB = oR.GetRasterBand(1)
			# in case of errors
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				cfg.mx.msgErr34()
				return 'No'
			# set raster projection from reference
			oR.SetGeoTransform( [ origX , rGT[1] , 0 , origY , 0 , rGT[5] ] )
			oR.SetProjection(rP)
			# output rasters
			oM = []
			oM.append(outputRaster)
			oMR = cfg.utls.createRasterFromReference(oR, 1, oM, noDataValue, 'GTiff', cfg.rasterDataType, 0, None, 'No', constantValue =  backgroundValue)
			# close bands
			oRB = None
			# close rasters
			oR = None
			oMR = None
			oR2 = cfg.gdalSCP.Open(outputRaster, cfg.gdalSCP.GA_Update)
			# convert reference layer to raster
			if ALL_TOUCHED is None:
				if burnValues is None:
					oC = cfg.gdalSCP.RasterizeLayer(oR2, [1], gL, options = ['ATTRIBUTE=' + str(fieldName)])
				else:
					oC = cfg.gdalSCP.RasterizeLayer(oR2, [1], gL, burn_values=[burnValues])
			else:
				if burnValues is None:
					oC = cfg.gdalSCP.RasterizeLayer(oR2, [1], gL, options = ['ATTRIBUTE=' + str(fieldName), 'ALL_TOUCHED=TRUE'])
				else:
					oC = cfg.gdalSCP.RasterizeLayer(oR2, [1], gL, burn_values=[burnValues], options = ['ALL_TOUCHED=TRUE'])
			# close rasters
			oR2 = None
			rD = None
			l.Destroy()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'vector to raster check: ' + str(oC))
			return outputRaster
		else:
			cfg.mx.msg9()
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'Error None lPRS: ' + str(lPRS) + 'rPRS: ' + str(rPRS))
			return 'No'

	# merge dissolve two layers to new layer
	def createVirtualLayer(self, inputLayerList, targetLayer = None):
		# create virtual layer
		source = '''
		<OGRVRTDataSource>
		'''
		for layer in inputLayerList:
			i = cfg.ogrSCP.Open(layer)
			iL = i.GetLayer()
			iN = iL.GetName()
			xml = '''
				<OGRVRTLayer name="%s">
					<SrcDataSource>%s</SrcDataSource>
					<SrcLayer>%s</SrcLayer>
				</OGRVRTLayer>
			'''
			source = source + xml % (iN, layer, iN)
		source = source + '''
		</OGRVRTDataSource>
		'''
		if targetLayer is None:
			targetLayer = cfg.utls.createTempRasterPath('vrt')
		with open(targetLayer, 'w') as file:
			file.write(source)
		return targetLayer

	# merge dissolve layer to new layer
	def mergeDissolveLayer(self, inputLayer, targetLayer, column, xListCoordinates):
		# open virtual layer
		inputM = cfg.ogrSCP.Open(inputLayer)
		iL0 = inputM.GetLayer()
		iNm0 = iL0.GetName()
		iSR = iL0.GetSpatialRef()
		iLDefn = iL0.GetLayerDefn()
		# column fid
		fld = iLDefn.GetFieldIndex(column)
		iD = cfg.ogrSCP.GetDriverByName('GPKG')
		oS = iD.CreateDataSource(targetLayer)
		nm = cfg.utls.fileNameNoExt(targetLayer)
		oL = oS.CreateLayer(str(nm), iSR, cfg.ogrSCP.wkbMultiPolygon)
		# fields
		for f in range(0, iLDefn.GetFieldCount()):
			fDefn = iLDefn.GetFieldDefn(f)
			oL.CreateField(fDefn)
		oLDefn = oL.GetLayerDefn()
		# get unique values
		sql = 'SELECT DISTINCT "' + column +'" FROM "' + iNm0 + '"'
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'sql ' + sql)
		uniqueValues = inputM.ExecuteSQL(sql, dialect = 'SQLITE')
		uniqueValues
		values = []
		idList = []
		for i, f in enumerate(uniqueValues):
			values.append(f.GetField(0))
		sqlList = str(xListCoordinates)[1:-1].replace("'", '')
		# for each value
		for v in values:
			uVFL = None
			# to be replaced by cascaded ST_UNION when performance issues are solved, see https://groups.google.com/g/spatialite-users/c/FTO_cmLCfpE/
			sql = 'SELECT DISTINCT(ST_unaryunion(ST_COLLECT(geom))), GROUP_CONCAT(DISTINCT id) FROM (SELECT fid as id, geom FROM "' + iNm0 + '" WHERE ' + column + ' = ' + str(v) + ') INNER JOIN (SELECT DISTINCT id FROM "rtree_' + iNm0 + '_geom" WHERE minx IN (' + sqlList + ') OR maxx IN (' + sqlList + ') ) USING (id)'
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'sql ' + sql)
			uV = inputM.ExecuteSQL(sql, dialect = 'SQLITE')
			if uV is not None:
				uVF = uV.GetNextFeature()
				uVFL = uVF.GetField(0)
				geometryRef = uVF.GetGeometryRef()
				if geometryRef is not None:
					# geometry count
					cUG = geometryRef.GetGeometryCount()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' count geometries ' + str(cUG))
					if cUG > 1:
						for j in range(0, cUG):
							oL.StartTransaction()
							jg = geometryRef.GetGeometryRef(int(j))
							try:
								if jg is not None:
									if jg.IsValid() is False:
										jg = jg.Buffer(0.0)
									if jg.IsValid() is True:
										oF = cfg.ogrSCP.Feature(oLDefn)
										oFO = oF.SetGeometry(jg)
										oF.SetField(column, v)
										oLO = oL.CreateFeature(oF)
										oL.CommitTransaction()
									else:
										oL.RollbackTransaction()
										oL.CommitTransaction()
										oL.StartTransaction()
										oF = cfg.ogrSCP.Feature(oLDefn)
										oF.SetGeometry(geometryRef)
										oF.SetField(column, v)
										oL.CreateFeature(oF)
										oL.CommitTransaction()
										break
							except:
								oL.RollbackTransaction()
								oL.CommitTransaction()
								oL.StartTransaction()
								oF = cfg.ogrSCP.Feature(oLDefn)
								oF.SetGeometry(geometryRef)
								oF.SetField(column, v)
								oL.CreateFeature(oF)
								oL.CommitTransaction()
								break
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' added union cascade geometries ')	
					else:
						oL.StartTransaction()
						oF = cfg.ogrSCP.Feature(oLDefn)
						oF.SetGeometry(geometryRef)
						oF.SetField(column, v)
						oL.CreateFeature(oF)
						oL.CommitTransaction()	
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' added union geometries ')
			if uVFL is not None:
				idList1 = uVFL.split(',')
				idList.extend(idList1)
		iF = iL0.GetNextFeature()
		oL.StartTransaction()
		while iF:
			iFID = str(iF.GetFID())
			vF = iF.GetField(column)
			if str(iFID) not in idList:
				g = iF.GetGeometryRef()
				oF = cfg.ogrSCP.Feature(oLDefn)
				oF.SetGeometry(g)
				oF.SetField(column, vF)
				oL.CreateFeature(oF)
			iF = iL0.GetNextFeature()
		oL.CommitTransaction()
		inputM.Destroy()
		iL0 = None
		inputM = None
		oS.Destroy()
		oL = None
		oS = None
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'merged: ' + str(targetLayer))
		return targetLayer
		
	# merge all layers to new layer
	def mergeAllLayers(self, inputLayersList, targetLayer):
		tL = cfg.utls.createVirtualLayer(inputLayersList)
		# open virtual layer
		input = cfg.ogrSCP.Open(tL)
		iL0 = input.GetLayer()
		iNm0 = iL0.GetName()
		iSR = iL0.GetSpatialRef()
		iLDefn = iL0.GetLayerDefn()
		iD = cfg.ogrSCP.GetDriverByName('GPKG')
		oS = iD.CreateDataSource(targetLayer)
		nm = cfg.utls.fileNameNoExt(targetLayer)
		oL = oS.CreateLayer(str(nm), iSR, cfg.ogrSCP.wkbMultiPolygon)
		# fields
		for f in range(0, iLDefn.GetFieldCount()):
			fDefn = iLDefn.GetFieldDefn(f)
			oL.CreateField(fDefn)
		oLDefn = oL.GetLayerDefn()
		oLFcount = oLDefn.GetFieldCount()
		oL.StartTransaction()
		for i in input:
			iNm = i.GetName()
			iL0 = input.GetLayer(iNm)
			iF = iL0.GetNextFeature()
			while iF:
				g = iF.GetGeometryRef()
				oF = cfg.ogrSCP.Feature(oLDefn)
				oF.SetGeometry(g)
				for i in range(0, oLFcount):
					nmRef = iLDefn.GetFieldDefn(i).GetNameRef()
					field = iF.GetField(i)
					oF.SetField(nmRef, field)
				oL.CreateFeature(oF)
				iF = iL0.GetNextFeature()
		oL.CommitTransaction()
		input.Destroy()
		oS.Destroy()
		oS = None
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'merged: ' + str(targetLayer))
		return targetLayer
		
	# merge layers to new layer
	def mergeLayersToNewLayer(self, inputList, targetLayer, column = None, dissolveOutputOption = None):
		# input layers
		inputLayersList = []
		# x coordinates of polygons on borders
		xList = []
		for i in range(0, len(inputList)):
			vectorPath, minX, maxX = inputList[i]
			inputLayersList.append(vectorPath)
			if i > 0:
				if minX is not None:
					xList.append(str(minX))
			if i < len(inputList) - 1:
				if maxX is not None:
					xList.append(str(maxX))
		if dissolveOutputOption == 'Yes':
			tVect = cfg.utls.createTempRasterPath('gpkg')
		else:
			tVect = targetLayer
		v = cfg.utls.mergeAllLayers(inputLayersList, tVect)
		if dissolveOutputOption == 'Yes':
			r = cfg.utls.mergeDissolveLayer(v, targetLayer, column, xList)
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'merged: ' + str(targetLayer))
		return targetLayer
			
	# get image Geo Transform
	def imageGeoTransform(self, rasterPath):
		try:
			# open input with GDAL
			rD = cfg.gdalSCP.Open(rasterPath, cfg.gdalSCP.GA_ReadOnly)
			# number of x pixels
			rC = rD.RasterXSize
			# number of y pixels
			rR = rD.RasterYSize
			# check projections
			rP = rD.GetProjection()
			# pixel size and origin
			rGT = rD.GetGeoTransform()
			left = rGT[0]
			top = rGT[3]
			pX = rGT[1]
			pY = abs(rGT[5])
			right = rGT[0] + rGT[1] * rD.RasterXSize
			bottom = rGT[3] + rGT[5] * rD.RasterYSize
			cRSR = cfg.osrSCP.SpatialReference(wkt=rP)
			un = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unknown')
			if cRSR.IsProjected:
				un = cRSR.GetAttrValue('unit')
			rD = None
			return left, right, top, bottom, pX, pY, rP, un
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err) + ' rasterPath: ' + str(rasterPath))
			return 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No'
			
##################################
	''' vector functions '''
##################################
		
	# zip a directory
	def zipDirectoryInFile(self, zipPath, fileDirectory):
		try:
			zip = cfg.zipfileSCP.ZipFile(zipPath, 'w')
			for f in cfg.osSCP.listdir(fileDirectory):
				zip.write(fileDirectory + "/" + f)
			zip.close()
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			
	# create backup file
	def createBackupFile(self, filePath):
		try:
			cfg.shutilSCP.copy(filePath, filePath + "." + cfg.backupNm)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		
	# create a polygon shapefile with OGR
	def createEmptyShapefile(self, crsWkt, outputVector, format = 'ESRI Shapefile'):
		try:
			crsWkt = str(crsWkt.toWkt())
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'crsWkt: ' + str(crsWkt))
		d = cfg.ogrSCP.GetDriverByName(format)
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
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'outputVector: ' + str(outputVector))
		
	# create a polygon shapefile with OGR
	def createSCPShapefile(self, crsWkt, outputVector):
		try:
			crsWkt = str(crsWkt.toWkt())
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'crsWkt: ' + str(crsWkt))
		d = cfg.ogrSCP.GetDriverByName('ESRI Shapefile')
		dS = d.CreateDataSource(outputVector)
		# shapefile
		sR = cfg.osrSCP.SpatialReference()
		sR.ImportFromWkt(crsWkt)
		nm = cfg.utls.fileNameNoExt(outputVector)
		rL = dS.CreateLayer(nm, sR, cfg.ogrSCP.wkbMultiPolygon)
		fd0 = cfg.ogrSCP.FieldDefn('fid', cfg.ogrSCP.OFTInteger)
		rL.CreateField(fd0)
		fd1 = cfg.ogrSCP.FieldDefn(cfg.fldMacroID_class, cfg.ogrSCP.OFTInteger)
		rL.CreateField(fd1)
		fd2 = cfg.ogrSCP.FieldDefn(cfg.fldROIMC_info, cfg.ogrSCP.OFTString)
		rL.CreateField(fd2)
		fd3 = cfg.ogrSCP.FieldDefn(cfg.fldID_class, cfg.ogrSCP.OFTInteger)
		rL.CreateField(fd3)
		fd4 = cfg.ogrSCP.FieldDefn(cfg.fldROI_info, cfg.ogrSCP.OFTString)
		rL.CreateField(fd4)
		fd5 = cfg.ogrSCP.FieldDefn(cfg.fldSCP_UID, cfg.ogrSCP.OFTString)
		rL.CreateField(fd5)
		rL = None
		dS = None
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'outputVector: ' + str(outputVector))
		
	# create a polygon gpkg with OGR
	def createSCPVector(self, crsWkt, outputVector, format = 'GPKG'):
		try:
			crsWkt = str(crsWkt.toWkt())
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'crsWkt: ' + str(crsWkt))
		d = cfg.ogrSCP.GetDriverByName(format)
		dS = d.CreateDataSource(outputVector)
		# shapefile
		sR = cfg.osrSCP.SpatialReference()
		sR.ImportFromWkt(crsWkt)
		nm = cfg.utls.fileNameNoExt(outputVector)
		rL = dS.CreateLayer(nm, sR, cfg.ogrSCP.wkbMultiPolygon)
		fd1 = cfg.ogrSCP.FieldDefn(cfg.fldMacroID_class, cfg.ogrSCP.OFTInteger)
		rL.CreateField(fd1)
		fd2 = cfg.ogrSCP.FieldDefn(cfg.fldROIMC_info, cfg.ogrSCP.OFTString)
		rL.CreateField(fd2)
		fd3 = cfg.ogrSCP.FieldDefn(cfg.fldID_class, cfg.ogrSCP.OFTInteger)
		rL.CreateField(fd3)
		fd4 = cfg.ogrSCP.FieldDefn(cfg.fldROI_info, cfg.ogrSCP.OFTString)
		rL.CreateField(fd4)
		fd5 = cfg.ogrSCP.FieldDefn(cfg.fldSCP_UID, cfg.ogrSCP.OFTString)
		rL.CreateField(fd5)
		rL = None
		dS = None
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'outputVector: ' + str(outputVector))
		
	# Get extent of a shapefile
	def getShapefileRectangleBox(self, layerPath):
		try:
			dr = cfg.ogrSCP.Open(layerPath, 1)
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
			return centerX, centerY, width, heigth
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "roi bounding box: center " + str(r.center()) + " width: " + str(r.width())+ " height: " + str(r.height()))
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		
	# get ID by attributes
	def getIDByAttributes(self, layer, field, attribute):
		IDs = []
		fR = layer.getFeatures(cfg.qgisCoreSCP.QgsFeatureRequest().setFilterExpression('"' + str(field) + '" = \'' + str(attribute) + '\''))
		for f in fR:
			IDs.append(f.id())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID: " + str(IDs))
		return IDs
		
	# Get last feauture id
	def getLastFeatureID(self, layer):
		f = cfg.qgisCoreSCP.QgsFeature()
		try:
			for f in layer.getFeatures():
				ID = f.id()
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ID: " + str(ID))
			return ID
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return False
		
	# Get a feature from a shapefile by feature ID
	def getFeaturebyID(self, layer, ID):
		f = cfg.qgisCoreSCP.QgsFeature()
		# feature request
		fR = cfg.qgisCoreSCP.QgsFeatureRequest().setFilterFid(ID)
		try:
			f = layer.getFeatures(fR)
			f = next(f)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'get feature ' + str(ID) + ' from shapefile: ' + str(layer.name()))
			return f
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return False
				
	# Get a feature box by feature ID
	def getFeatureRectangleBoxbyID(self, layer, ID):
		try:
			d = cfg.ogrSCP.GetDriverByName('ESRI Shapefile')
			ql = cfg.utls.layerSource(layer)
			dr = d.Open(ql, 1)
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
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'roi bounding box: center ' + str(r.center()) + ' width: ' + str(r.width())+ ' height: ' + str(r.height()))
			return centerX, centerY, width, heigth
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		
	# Delete a feauture from a shapefile by its Id
	def deleteFeatureShapefile(self, layer, feautureIds):
		layer.startEditing()				
		res = layer.dataProvider().deleteFeatures(feautureIds)
		layer.commitChanges()
		res2 = layer.dataProvider().createSpatialIndex()
		layer.updateExtents()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'feauture deleted: ' + str(layer) + ' ' + str(feautureIds) )

	# Edit a feauture in a shapefile by its Id
	def editFeatureShapefile(self, layer, feautureId, fieldName, value):
		id = self.fieldID(layer, fieldName)
		layer.startEditing()				
		res = layer.changeAttributeValue(feautureId, id, value)
		layer.commitChanges()
		res2 = layer.dataProvider().createSpatialIndex()
		layer.updateExtents()
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'feauture edited: ' + str(layer) + ' ' + str(feautureId) )
		
### Copy feature by ID to layer
	def copyFeatureToLayer(self, sourceLayer, ID, targetLayer):
		f = self.getFeaturebyID(sourceLayer, ID)
		# get geometry
		fG = f.geometry()
		f.setGeometry(fG)
		try:
			sF = targetLayer.fields()
			f.initAttributes(sF.count())
			if f.hasGeometry() is not True:
				cfg.mx.msg6()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'feature geometry is none')			
			else:	
				# copy polygon to shapefile
				targetLayer.startEditing()
				targetLayer.addFeature(f)	
				targetLayer.commitChanges()
				targetLayer.dataProvider().createSpatialIndex()
				targetLayer.updateExtents()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'feature copied')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				
	# merge polygons
	def mergePolygons(self, targetLayer, idList, attributeList):
		f = cfg.utls.getFeaturebyID(targetLayer, idList[0])
		sg = cfg.qgisCoreSCP.QgsGeometry(f.geometry())
		for i in idList:
			if i != idList[0]:
				f = cfg.utls.getFeaturebyID(targetLayer, i)
				g = cfg.qgisCoreSCP.QgsGeometry(f.geometry())
				g.convertToMultiType()
				sg.addPartGeometry(g)
		pr = targetLayer.dataProvider()
		fields = pr.fields().toList()
		targetLayer.startEditing()
		f = cfg.qgisCoreSCP.QgsFeature()
		f.setGeometry(sg)
		f.setAttributes(attributeList)
		pr.addFeatures([f])
		targetLayer.commitChanges()
		targetLayer.dataProvider().createSpatialIndex()
		targetLayer.updateExtents()
		fs = cfg.qgisCoreSCP.QgsFeature()
		for fs in targetLayer.getFeatures():
			ID = fs.id()
		return targetLayer
		
	# merge polygons to new layer
	def mergePolygonsToNewLayer(self, targetLayer, idList, attributeList):
		# create memory layer
		provider = targetLayer.dataProvider()
		fields = provider.fields()
		pCrs = cfg.utls.getCrs(targetLayer)
		mL = cfg.qgisCoreSCP.QgsVectorLayer('MultiPolygon?crs=' + str(pCrs.toWkt()), 'memoryLayer', 'memory')
		mL.setCrs(pCrs)
		pr = mL.dataProvider()
		for fld in fields:
			pr.addAttributes([fld])
		mL.updateFields()
		f = cfg.utls.getFeaturebyID(targetLayer, idList[0])
		sg = cfg.qgisCoreSCP.QgsGeometry(f.geometry())
		for i in idList:
			if i != idList[0]:
				f = cfg.utls.getFeaturebyID(targetLayer, i)
				g = cfg.qgisCoreSCP.QgsGeometry(f.geometry())
				g.convertToMultiType()
				sg.addPartGeometry(g)
		mL.startEditing()		
		f.setGeometry(sg)
		f.setAttributes(attributeList)
		pr.addFeatures([f])
		mL.commitChanges()
		mL.dataProvider().createSpatialIndex()
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
		cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "deleted field: " + str(fieldName) + " for layer: " + str(l.name()))
				
### Find field ID by name
	def fieldID(self, layer, fieldName):
		try:
			fID = layer.fields().lookupField(fieldName)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'ID: ' + str(fID) + ' for layer: ' + str(layer.name()))
			return fID
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				
### Get field names of a shapefile
	def fieldsShapefile(self, layerPath):
		s = cfg.ogrSCP.Open(layerPath)
		l = s.GetLayer()
		lD = l.GetLayerDefn()
		fN = [lD.GetFieldDefn(i).GetName() for i in range(lD.GetFieldCount())]
		s = None
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'shapefile field ' + str(layerPath))
		return fN
				
	# get field attribute list
	def getFieldAttributeList(self, layer, field):
		fID = self.fieldID(layer, field)
		f = cfg.qgisCoreSCP.QgsFeature()
		l = []
		for f in layer.getFeatures():
			a = f.attributes()[fID]
			l.append(a)
		x = list(set(l))
		return x
		
	# reproject shapefile
	def repojectShapefile(self, inputShapefilePath, inputEPSG, outputShapefilePath, outputEPSG, type = 'wkbMultiPolygon'):
		# spatial reference
		iSR = cfg.osrSCP.SpatialReference()
		# EPSG or projection
		try:
			iSR.ImportFromEPSG(inputEPSG)
		except:
			iSR = inputEPSG
		oSR = cfg.osrSCP.SpatialReference()
		try:
			oSR.ImportFromEPSG(outputEPSG)
		except:
			oSR = outputEPSG
		# required by GDAL 3 coordinate order
		try:
			iSR.SetAxisMappingStrategy(cfg.osrSCP.OAMS_TRADITIONAL_GIS_ORDER)
			oSR.SetAxisMappingStrategy(cfg.osrSCP.OAMS_TRADITIONAL_GIS_ORDER)
		except:
			pass
		# Coordinate Transformation
		cT = cfg.osrSCP.CoordinateTransformation(iSR, oSR)
		# input shapefile
		iS = cfg.ogrSCP.Open(inputShapefilePath)
		iL = iS.GetLayer()
		# output shapefile
		iD = cfg.ogrSCP.GetDriverByName('ESRI Shapefile')
		oS = iD.CreateDataSource(outputShapefilePath)
		nm = cfg.utls.fileName(outputShapefilePath)
		if type == 'wkbMultiPolygon':
			oL = oS.CreateLayer(str(nm), oSR, cfg.ogrSCP.wkbMultiPolygon)
		elif  type == 'wkbPoint':
			oL = oS.CreateLayer(str(nm), oSR, cfg.ogrSCP.wkbPoint)
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
	''' raster color composite functions '''
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
				if check == 'Yes':
					listA = cfg.utls.getAllItemsInCombobox(cfg.rgb_combo)
					cfg.RGBList = listA
					cfg.utls.writeProjectVariable("SCP_RGBList", str(cfg.RGBList))
					cfg.RGBLT.RGBListTable(cfg.RGBList)
					return 'Yes'
				else:
					int(check)
			except Exception as err:
				if "string index" not in str(err):
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
	
	# create RGB color composite
	def createRGBColorComposite(self, colorComposite, bandSetNumber = None):
		if bandSetNumber is None or bandSetNumber is False:
			bandSetNumber = cfg.bndSetNumber
		try:
			a = cfg.tmpVrtDict[bandSetNumber]
		except:
			cfg.tmpVrtDict[bandSetNumber] = None
		if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
			# if bandset create temporary virtual raster
			tPMN = cfg.bndSetVrtNm + str(bandSetNumber + 1) 
			if cfg.tmpVrtDict[bandSetNumber] is None:
				try:
					self.removeLayer(tPMN)
				except:
					pass
				tPMD = cfg.utls.createTempRasterPath('vrt')
				ckB = cfg.utls.checkBandSet(bandSetNumber)
				vrtCheck = cfg.utls.createVirtualRaster(cfg.bndSetLst, tPMD, 'No', 'Yes', 'Yes', 0)
				cfg.timeSCP.sleep(1)
				i = self.addRasterLayer(tPMD, tPMN)
				cfg.utls.setRasterColorComposite(i, 3, 2, 1)
				cfg.tmpVrtDict[bandSetNumber] = i
			else:
				i = cfg.utls.selectLayerbyName(tPMN, 'Yes')
			c = str(colorComposite).split(',')
			if len(c) == 1:
				c = str(colorComposite).split('-')
			if len(c) == 1:
				c = str(colorComposite).split(';')
			if len(c) == 1:
				c = str(colorComposite)
			if i is not None:
				b = len(cfg.bandSetsList[bandSetNumber][3])
				if int(c[0]) <= b and int(c[1]) <= b and int(c[2]) <= b:
					cfg.utls.setRasterColorComposite(i, int(c[0]), int(c[1]), int(c[2]))
					return 'Yes'
				else:
					return 'No'
			else:
				cfg.tmpVrtDict[bandSetNumber] = None
		else:
			c = str(colorComposite).split(',')
			if len(c) == 1:
				c = str(colorComposite).split('-')
			if len(c) == 1:
				c = str(colorComposite).split(';')
			if len(c) == 1:
				c = str(colorComposite)
			i = cfg.utls.selectLayerbyName(cfg.bandSetsList[bandSetNumber][8], 'Yes')
			if i is not None:
				b = len(cfg.bandSetsList[bandSetNumber][3])
				if int(c[0]) <= b and int(c[1]) <= b and int(c[2]) <= b:
					self.setRasterColorComposite(i, int(c[0]), int(c[1]), int(c[2]))
					return 'Yes'
				else:
					return 'No'
					
	# set raster color composite
	def setRasterColorComposite(self, raster, RedBandNumber, GreenBandNumber, BlueBandNumber):
		# QGIS3
		#raster.setDrawingStyle('MultiBandColor')
		raster.renderer().setRedBand(RedBandNumber)
		raster.renderer().setGreenBand(GreenBandNumber)
		raster.renderer().setBlueBand(BlueBandNumber)
		cfg.utls.setRasterContrastEnhancement(raster, cfg.defaultContrast )
		
	# set local cumulative cut stretch
	def setRasterCumulativeStretch(self):
		if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
			i = cfg.tmpVrtDict[cfg.bndSetNumber]
		else:
			i = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8], 'Yes')
		cfg.utls.setRasterContrastEnhancement(i, cfg.cumulativeCutContrast)
		cfg.defaultContrast = cfg.cumulativeCutContrast
				
	# set local standard deviation stretch
	def setRasterStdDevStretch(self):
		if cfg.bandSetsList[cfg.bndSetNumber][0] == 'Yes':
			i = cfg.tmpVrtDict[cfg.bndSetNumber]
		else:
			i = cfg.utls.selectLayerbyName(cfg.bandSetsList[cfg.bndSetNumber][8], 'Yes')
		cfg.utls.setRasterContrastEnhancement(i, cfg.stdDevContrast)
		cfg.defaultContrast = cfg.stdDevContrast
		
	# set raster enhancement
	def setRasterContrastEnhancement(self, QGISraster, contrastType = cfg.cumulativeCutContrast):
		ext = cfg.cnvs.extent( )
		tLPoint = cfg.qgisCoreSCP.QgsPointXY(ext.xMinimum(), ext.yMaximum())
		lRPoint = cfg.qgisCoreSCP.QgsPointXY(ext.xMaximum(), ext.yMinimum())
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
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				point1 = tLPoint
				point2 = lRPoint
		if contrastType == cfg.stdDevContrast:
			contrast = cfg.qgisCoreSCP.QgsRasterMinMaxOrigin.StdDev
		elif contrastType == cfg.cumulativeCutContrast:
			contrast = cfg.qgisCoreSCP.QgsRasterMinMaxOrigin.CumulativeCut
		try:
			QGISraster.setContrastEnhancement(cfg.qgisCoreSCP.QgsContrastEnhancement.StretchToMinimumMaximum, contrast, cfg.qgisCoreSCP.QgsRectangle(point1, point2))
			QGISraster.triggerRepaint()
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))

##################################
	''' table functions '''
##################################
		
	# delete all items in a table
	def clearTable(self, table):
		table.clearContents()
		for i in range(0, table.rowCount()):
			table.removeRow(0)
		
	# set all items to state 0 or 2
	def allItemsSetState(self, tableWidget, value):
		tW = tableWidget
		tW.blockSignals(True)
		r = tW.rowCount()
		for b in range(0, r):
			if cfg.actionCheck == 'Yes':
				tW.item(b, 0).setCheckState(value)
				#cfg.uiUtls.updateBar((b+1) * 100 / r)
			else:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' cancelled')
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
		a = cfg.utls.questionBox(cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Remove rows'), cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Are you sure you want to remove highlighted rows from the table?'))
		if a == 'Yes':
			tW = table
			tW.blockSignals(True)
			c = tW.rowCount()
			# list of item to remove
			iR  = []
			for i in tW.selectedIndexes():
				iR.append(i.row())
			v = list(set(iR))
			# remove items
			for i in reversed(list(range(0, len(v)))):
				tW.removeRow(v[i])
			c = tW.rowCount()
			tW.blockSignals(False)
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' row removed')
			
	# select rows in table
	def selectRowsInTable(self, table, rowList):
		c = table.columnCount()
		for row in rowList:
			table.setRangeSelected(cfg.QtWidgetsSCP.QTableWidgetSelectionRange(row, 0, row, c-1), True)
			
	# table content to text
	def tableToText(self, table):
		try:
			tW = table
			r = tW.rowCount()
			c = tW.columnCount()
			text = ''
			for x in range(0, r):
				row = ''
				for y in range(0, c):
					it = tW.item(x, y).text()
					row = row + it
					if y < (c - 1):
						row = row + '\t' 
				text = text + row
				if x < (r - 1):
					text = text + '\n'
			return text		
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'	
			
	# text to table content
	def textToTable(self, table, text):
		try:
			tW = table
			c = tW.columnCount()
			nSplit = text.split('\n')
			for n in nSplit:
				# add item to table
				r = tW.rowCount()
				# add list items to table
				tW.setRowCount(r + 1)
				tSplit = n.split('\t')
				for t in range(0, c):
					cfg.utls.addTableItem(tW, str(tSplit[t]), r, t)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			return 'No'
			
	# add item to table
	def addTableItem(self, table, item, row, column, enabled = 'Yes', color = None, checkboxState = None, tooltip = None, foreground = None, bold = None):
		itMID = cfg.QtWidgetsSCP.QTableWidgetItem()
		if checkboxState != None:
			itMID.setCheckState(checkboxState)
		if enabled == 'No':
			itMID.setFlags(cfg.QtSCP.ItemIsEnabled)
		itMID.setData(cfg.QtSCP.DisplayRole, item)
		table.setItem(row, column, itMID)
		if color is not None:
			table.item(row, column).setBackground(color)
		if foreground is not None:
			table.item(row, column).setForeground(foreground)
		if tooltip is not None:
			itMID.setToolTip(tooltip)
		if bold is not None:
			font = cfg.QtGuiSCP.QFont()
			font.setBold(True)
			table.item(row, column).setFont(font)
			
	# set table item
	def setTableItem(self, table, row, column, value):
		table.item(row, column).setText(value)
							
	# insert table row
	def insertTableRow(self, table, row, height = None):
		table.insertRow(row)
		if height is not None:
			table.setRowHeight(row, height)
		
	# insert table column
	def insertTableColumn(self, table, column, name, width = None, hide = 'No'):
		table.insertColumn(column)
		table.setHorizontalHeaderItem(column, cfg.QtWidgetsSCP.QTableWidgetItem(name))
		if width is not None:
			table.setColumnWidth(column, width)
		if hide == 'Yes':
			table.hideColumn(column)
	
	# sort table column
	def sortTableColumn(self, table, column, ascending = False):
		table.sortItems(column, ascending)
		
	# set table column width
	def setColumnWidthList(self, table, list):
		for c in list:
			table.setColumnWidth(c[0], c[1])
			
	# set tree column width
	def setTreeColumnWidthList(self, tree, list):
		for c in list:
			tree.header().resizeSection(c[0], c[1])
	
##################################
	''' tab selection functions '''
##################################

### tab 0
	# select band set tab
	def bandSetTab(self):
		cfg.ui.SCP_tabs.setCurrentIndex(0)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
### tab 1
	# select tab 1 from Main Interface
	def selectTab2MainInterface(self, secondTab = None):
		cfg.ui.SCP_tabs.setCurrentIndex(1)
		if secondTab is not None:
			cfg.ui.tabWidget_5.setCurrentIndex(secondTab)
		
	# select basic tools tab
	def basicToolsTab(self):
		cfg.utls.selectTab2MainInterface()
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# RGB List tab
	def RGBListTab(self):
		cfg.utls.selectTab2MainInterface(0)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# Band Set List tab
	def BandSetListTab(self):
		cfg.utls.selectTab2MainInterface(1)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# algorithm weight tab
	def algorithmBandWeightTab(self):
		cfg.utls.selectTab2MainInterface(2)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()

	# select multiple roi tab
	def multipleROICreationTab(self):
		cfg.utls.selectTab2MainInterface(3)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# import library signatures tab
	def importSignaturesTab(self):
		cfg.utls.selectTab2MainInterface(4)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
				
	# export library signatures tab
	def exportSignaturesTab(self):
		cfg.utls.selectTab2MainInterface(5)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# signature threshold tab
	def signatureThresholdTab(self):
		cfg.utls.selectTab2MainInterface(6)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()

	# LCS threshold tab
	def LCSThresholdTab(self):
		cfg.utls.selectTab2MainInterface(7)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
### tab 2
	# select tab 2
	def selectTabDownloadImages(self):
		cfg.ui.SCP_tabs.setCurrentIndex(2)
		cfg.ipt.dockTabChanged(5)
		
	# select pre processing tab
	def downloadProductsTab(self):
		cfg.utls.selectTabDownloadImages()
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
### tab 4
	# select tab 4 from Main Interface
	def selectTab4MainInterface(self, secondTab = None):
		cfg.ui.SCP_tabs.setCurrentIndex(3)
		if secondTab is not None:
			cfg.ui.tabWidget_preprocessing.setCurrentIndex(secondTab)
		
	# select pre processing tab
	def preProcessingTab(self):
		cfg.utls.selectTab4MainInterface()
		cfg.ipt.dockTabChanged(6)

	# select Landsat tab
	def landsatTab(self):
		cfg.utls.selectTab4MainInterface(0)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Sentinel-1 tab
	def sentinel1Tab(self):
		cfg.utls.selectTab4MainInterface(1)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Sentinel-2 tab
	def sentinel2Tab(self):
		cfg.utls.selectTab4MainInterface(2)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Sentinel-3 tab
	def sentinel3Tab(self):
		cfg.utls.selectTab4MainInterface(3)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select ASTER tab
	def asterTab(self):
		cfg.utls.selectTab4MainInterface(4)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select MODIS tab
	def modisTab(self):
		cfg.utls.selectTab4MainInterface(5)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# Vector to raster tab
	def vectorToRasterTab(self):
		cfg.utls.selectTab4MainInterface(6)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Clip multiple rasters tab
	def clipMultipleRastersTab(self):
		cfg.utls.selectTab4MainInterface(7)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Reproject raster bands tab
	def reprojectrasterbandsTab(self):
		cfg.utls.selectTab4MainInterface(8)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Split raster bands tab
	def splitrasterbandsTab(self):
		cfg.utls.selectTab4MainInterface(9)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Stack raster bands tab
	def stackrasterbandsTab(self):
		cfg.utls.selectTab4MainInterface(10)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# Mosaic tab
	def mosaicBandSetsTab(self):
		cfg.utls.selectTab4MainInterface(11)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# cloud masking tab
	def cloudMaskingTab(self):
		cfg.utls.selectTab4MainInterface(12)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select GOES tab
	def GOESTab(self):
		cfg.utls.selectTab4MainInterface(13)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select neighbor pixels tab
	def neighborPixelsTab(self):
		cfg.utls.selectTab4MainInterface(14)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
### tab 5
	# select tab 5 from Main Interface
	def selectTab5MainInterface(self, secondTab = None):
		cfg.ui.SCP_tabs.setCurrentIndex(4)
		if secondTab is not None:
			cfg.ui.tabWidget_4.setCurrentIndex(secondTab)
		
	# select bandrefRstrDt processing tab
	def bandProcessingTab(self):
		cfg.utls.selectTab5MainInterface()
		cfg.ipt.dockTabChanged(7)
		
	# select Band combination tab
	def bandCombinationTab(self):
		cfg.utls.selectTab5MainInterface(0)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# PCA tab
	def PCATab(self):
		cfg.utls.selectTab5MainInterface(1)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# Clustering tab
	def clusteringTab(self):
		cfg.utls.selectTab5MainInterface(2)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
			
	# Spectral distance tab
	def spectralDistanceTab(self):
		cfg.utls.selectTab5MainInterface(3)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Classification tab
	def classificationTab(self):
		cfg.utls.selectTab5MainInterface(4)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Random forest tab
	def randomForestTab(self):
		cfg.utls.selectTab5MainInterface(5)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
### tab 5
	# select tab 5 from Main Interface
	def selectTab6MainInterface(self, secondTab = None):
		cfg.ui.SCP_tabs.setCurrentIndex(5)
		if secondTab is not None:
			cfg.ui.tabWidget_2.setCurrentIndex(secondTab)
		
	# select post processing tab
	def postProcessingTab(self):
		cfg.utls.selectTab6MainInterface()
		cfg.ipt.dockTabChanged(8)
		
	# select Accuracy tab
	def accuracyTab(self):
		cfg.utls.selectTab6MainInterface(0)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Land cover change tab
	def landCoverChangeTab(self):
		cfg.utls.selectTab6MainInterface(1)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Classification report tab
	def classificationReportTab(self):
		cfg.utls.selectTab6MainInterface(2)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Cross classification tab
	def crossClassificationTab(self):
		cfg.utls.selectTab6MainInterface(3)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Classification to vector tab
	def classSignatureTab(self):
		cfg.utls.selectTab6MainInterface(4)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
	
	# select Classification to vector tab
	def classificationToVectorTab(self):
		cfg.utls.selectTab6MainInterface(5)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
	
	# select Reclassification tab
	def reclassificationTab(self):
		cfg.utls.selectTab6MainInterface(6)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
			
	# select Edit raster tab
	def editRasterTab(self):
		cfg.utls.selectTab6MainInterface(7)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Classification sieve tab
	def classificationSieveTab(self):
		cfg.utls.selectTab6MainInterface(8)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Classification erosion tab
	def classificationErosionTab(self):
		cfg.utls.selectTab6MainInterface(9)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select Classification dilation tab
	def classificationDilationTab(self):
		cfg.utls.selectTab6MainInterface(10)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select zonal stat raster tab
	def zonalStatRasterTab(self):
		cfg.utls.selectTab6MainInterface(11)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
### tab 6
	# select Band calc tab
	def bandCalcTab(self):
		cfg.ui.SCP_tabs.setCurrentIndex(6)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
	
### tab 7
	# select tab 7 from Main Interface
	def selectTabBatch(self, secondTab = None):
		cfg.ui.SCP_tabs.setCurrentIndex(7)
		if secondTab is not None:
			cfg.ui.toolBox.setCurrentIndex(secondTab)
		
	# select batch tab
	def batchTab(self):
		cfg.utls.selectTabBatch()
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
### tab 8
	# select tab 8 from Main Interface
	def selectTabSettings(self, secondTab = None):
		cfg.ui.SCP_tabs.setCurrentIndex(8)
		if secondTab is not None:
			cfg.ui.settings_tabWidget.setCurrentIndex(secondTab)
		
	# select settings tab
	def settingsTab(self):
		cfg.utls.selectTabSettings()
		
	# select settings Processing tab
	def processingSettingTab(self):
		cfg.utls.selectTabSettings(0)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select settings interface tab
	def interfaceTab(self):
		cfg.utls.selectTabSettings(1)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
	# select settings debug tab
	def debugTab(self):
		cfg.utls.selectTabSettings(2)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()

### tab 9
	# select about tab
	def aboutTab(self):
		cfg.ui.SCP_tabs.setCurrentIndex(9)
		cfg.currentTab = str(cfg.inspectSCP.stack()[0][3])
		cfg.ipt.treeMenuTab()
		
### spectral signature plot tab
	def spectralPlotTab(self):
		cfg.spectralplotdlg.close()
		cfg.spectralplotdlg.show()
		
	# select tab in signature plot tab
	def selectSpectralPlotTabSettings(self, secondTab = None):
		if secondTab is not None:
			cfg.uisp.tabWidget.setCurrentIndex(secondTab)
		
### scatter plot tab
	def scatterPlotTab(self):
		cfg.scatterplotdlg.close()
		cfg.scatterplotdlg.show()
		
	# first install welcome tab
	def welcomeTab(self):
		cfg.welcomedlg.close()
		cfg.welcomedlg.show()
		
##################################
	''' notification functions '''
##################################

	# beep sound
	def beepSound(self, frequency, duration):
		if cfg.sysSCP.platform.startswith('win'):
			winsound.Beep(frequency, int(duration * 1000))
		elif cfg.sysSCP.platform.startswith('linux'):
			cfg.osSCP.system('play --no-show-progress --null --channels 1 synth ' + str(duration) + ' sine ' + str(frequency))
		else:
			cfg.sysSCP.stdout.write('\a')
			cfg.sysSCP.stdout.flush()
	
	# finish sound
	def finishSound(self):
		if cfg.soundVal == '2':
			try:
				self.beepSound(800, 0.2)
				self.beepSound(600, 0.3)
				self.beepSound(700, 0.5)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				
	# send SMTP message
	def sendSMTPMessage(self, subject = None, message = None):		
		if cfg.SMTPCheck == '2':
			try:
				if len(cfg.SMTPServer) > 0:
					s = cfg.smtplibSCP.SMTP_SSL(cfg.SMTPServer)
					s.login(cfg.SMTPUser, cfg.SMTPPassword)
					tolist = cfg.SMTPtoEmails.split(',')
					if subject is None:
						subject = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'SCP: completed process')
					if message is None:
						message = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'SCP: completed process')
					msg = 'From: SCP\nTo: \nSubject: ' + subject + '\n\n' + message + '\n\n---\nSemi-Automatic Classification Plugin\nhttps://fromgistors.blogspot.com/p/semi-automatic-classification-plugin.html'
					s.sendmail(cfg.SMTPUser, tolist, msg)
					s.quit()
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		
##################################
	''' clean functions '''
##################################

	# clean old temporary directory
	def cleanOldTempDirectory(self):
		t = cfg.datetimeSCP.datetime.now()
		inputDir = str(cfg.QDirSCP.tempPath() + '/' + cfg.tempDirName)
		try:
			for name in cfg.osSCP.listdir(inputDir):
				dStr = cfg.datetimeSCP.datetime.strptime(name, '%Y%m%d_%H%M%S%f')
				diff = (t - dStr)
				if diff.days > 3:
					cfg.shutilSCP.rmtree(inputDir + '/' + name, True)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			
##################################
	''' general functions '''
##################################
		
	# 32bit or 64bit
	def findSystemSpecs(self):
		if cfg.sysSCP.maxsize > 2**32:
			cfg.sysSCP64bit = 'Yes'
		else:
			cfg.sysSCP64bit = 'No'
		# file system encoding
		cfg.fSEnc = cfg.sysSCP.getfilesystemencoding()
		# system information
		cfg.sysSCPNm = cfg.platformSCP.system()
		# QGIS version
		cfg.QGISVer = cfg.qgisCoreSCP.Qgis.QGIS_VERSION_INT
			
	# read variables from project instance
	def readVariables(self):
		# read qml path from project instance	
		cfg.qmlFl = cfg.utls.readProjectVariable('qmlfile', '')
		# set qml line content
		cfg.ui.qml_lineEdit.setText(cfg.qmlFl)
		# read signature checkbox from project instance
		cfg.sigClcCheck = cfg.utls.readProjectVariable('calculateSignature', '2')
		# read save input checkbox from project instance
		cfg.saveInputCheck = cfg.utls.readProjectVariable('saveInput', '2')
		# read rapid ROI checkbox from project instance
		cfg.rpdROICheck = cfg.utls.readProjectVariable('rapidROI', '2')
		cfg.vegIndexCheck = cfg.utls.readProjectVariable('vegetationIndex', '2')
		cfg.ROIband = cfg.utls.readProjectVariable('rapidROIBand', str(cfg.ROIband))
		cfg.prvwSz = cfg.utls.readProjectVariable('previewSize', str(cfg.prvwSz))
		cfg.minROISz = cfg.utls.readProjectVariable('minROISize', str(cfg.minROISz))
		cfg.maxROIWdth = cfg.utls.readProjectVariable('maxROIWidth', str(cfg.maxROIWdth))
		cfg.rngRad = cfg.utls.readProjectVariable('rangeRadius', str(cfg.rngRad))
		cfg.ROIID = cfg.utls.readProjectVariable('ROIIDField', str(cfg.ROIID))
		cfg.ROIInfo = cfg.utls.readProjectVariable('ROIInfoField', str(cfg.ROIInfo))
		cfg.ROIMacroClassInfo = cfg.utls.readProjectVariable('ROIMacroclassInfoField', str(cfg.ROIMacroClassInfo))
		cfg.customExpression = cfg.utls.readProjectVariable('customExpression', str(cfg.customExpression))
		cfg.ROIMacroID = cfg.utls.readProjectVariable('ROIMacroIDField', str(cfg.ROIMacroID))
		# mask option
		cfg.mskFlPath = cfg.utls.readProjectVariable('maskFilePath', str(cfg.mskFlPath))
		cfg.mskFlState = cfg.utls.readProjectVariable('maskFileState', str(cfg.mskFlState))
		cfg.ui.mask_lineEdit.setText(str(cfg.mskFlPath))
		cfg.classTab.setMaskCheckbox()
		# band set
		bandSetsList = cfg.utls.readProjectVariable('bandSetsList', '[]')
		bndSetNumber = cfg.utls.readProjectVariable('bndSetNumber', str(cfg.bndSetNumber))		
		cfg.bandSetsList = eval(bandSetsList)
		bndSetMaxNumber = len(cfg.bandSetsList)
		if bndSetMaxNumber > 0:
			t = cfg.ui.Band_set_tabWidget.count()
			for index in reversed(list(range(0, t))):
				cfg.BandTabEdited = 'No'
				cfg.bst.deleteBandSetTab(index)
				cfg.BandTabEdited = 'Yes'
			# add band set tab
			for i in range(0, bndSetMaxNumber):
				cfg.BandTabEdited = 'No'
				cfg.bst.addBandSetTab('No')
				cfg.BandTabEdited = 'Yes'
				bndSetList = cfg.bandSetsList[i]
				# add band set to table
				bs = bndSetList[3]
				wlg = bndSetList[4]
				t = eval('cfg.ui.tableWidget__' + cfg.bndSetTabList[i])
				it = 0
				cfg.BandTabEdited = 'No'
				t.blockSignals(True)
				for x in sorted(wlg):
					# add item to table
					c = t.rowCount()
					# name of item of list
					iN = bs[it]
					# add list items to table
					t.setRowCount(c + 1)
					cfg.utls.addTableItem(t, iN, c, 0)
					cfg.utls.addTableItem(t, str(x), c, 1)
					try:
						cfg.utls.addTableItem(t, str(bndSetList[6][0][it]), c, 2)
					except:
						cfg.utls.addTableItem(t, '1', c, 2)
					try:
						cfg.utls.addTableItem(t, str(bndSetList[6][1][it]), c, 3)
					except:
						cfg.utls.addTableItem(t, '0', c, 3)
					cfg.utls.addTableItem(t, str(cfg.bst.unitNameConversion(bndSetList[5], 'Yes')), c, 4)
					try:
						cfg.utls.addTableItem(t, bndSetList[8], c, 5)
					except:
						cfg.utls.addTableItem(t, '', c, 5)
					try:
						cfg.utls.addTableItem(t, bndSetList[9], c, 6)
					except:
						cfg.utls.addTableItem(t, '', c, 6)
					it = it + 1
				t.blockSignals(False)
				cfg.BandTabEdited = 'Yes'					
		else:
			t = cfg.ui.Band_set_tabWidget.count()
			for index in reversed(list(range(0, t))):
				cfg.bst.deleteBandSetTab(index)
			cfg.bst.addBandSetTab('No')
		cfg.bst.readBandSet('Yes')
		cfg.bndSetNumber = int(bndSetNumber)
		if cfg.bndSetNumber < 0:
			cfg.bndSetNumber = 0
		cfg.utls.checkBandSet(cfg.bndSetNumber)
		cfg.BandTabEdited = 'No'
		cfg.ui.Band_set_tabWidget.setCurrentIndex(cfg.bndSetNumber)
		cfg.BandTabEdited = 'Yes'
		# read RGB list
		rgbList = cfg.utls.readProjectVariable('SCP_RGBList', str(cfg.RGBList))
		cfg.RGBList = eval(rgbList)
		try:
			if cfg.vrtRstProjVal == '0':
				cfg.rgb_combo.blockSignals(True)
			cfg.utls.setComboboxItems(cfg.rgb_combo, cfg.RGBList)
			cfg.rgb_combo.blockSignals(False)
		except:
			pass
		# logger
		cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' readVariables')
			
	# get temporary directory
	def getTempDirectory(self):
		# temp directory
		if cfg.tmpDir is None:
			tmpDir0 = str(cfg.QDirSCP.tempPath() + '/' + cfg.tempDirName)
		else:
			tmpDir0 = cfg.tmpDir
		if not cfg.QDirSCP(tmpDir0).exists():
			try:
				cfg.osSCP.makedirs(tmpDir0)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				cfg.utls.setQGISRegSetting(cfg.regTmpDir, tmpDir0)
				cfg.mx.msgWar17()
				cfg.tmpDir = str(cfg.QDirSCP.tempPath() + '/' + cfg.tempDirName)
				tmpDir0 = cfg.tmpDir
				if not cfg.QDirSCP(tmpDir0).exists():
					cfg.osSCP.makedirs(tmpDir0)
		try:
			dT = cfg.utls.getTime()
			cfg.osSCP.makedirs(tmpDir0 + '/' + dT)
			cfg.tmpDir = str(tmpDir0 + '/' + dT)
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.mx.msgWar17()
			if not cfg.QDirSCP(cfg.tmpDir).exists():
				cfg.osSCP.makedirs(cfg.tmpDir)
		return tmpDir0

	# check and create directory
	def makeDirectory(self, path):
		if not cfg.QDirSCP(path).exists():
			try:
				cfg.osSCP.makedirs(path)
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return None
		return path
			
	# find available RAM
	def findAvailableRAM(self):
		try:
			if cfg.sysSCP64bit == 'Yes':
				if cfg.sysSCPNm == 'Windows':
					class GlobalMemoryStatus(cfg.ctypesSCP.Structure):
						_fields_ = [('length', cfg.ctypesSCP.c_ulong),
							('memoryLoad', cfg.ctypesSCP.c_ulong),
							('totalRam', cfg.ctypesSCP.c_ulong),
							('availPhys', cfg.ctypesSCP.c_ulonglong),
							('totalPageFile', cfg.ctypesSCP.c_ulonglong),
							('availPageFile', cfg.ctypesSCP.c_ulonglong),
							('totalVirt', cfg.ctypesSCP.c_ulonglong),
							('availVirt', cfg.ctypesSCP.c_ulonglong),
							('availExVirt', cfg.ctypesSCP.c_ulonglong),
							]
					
					GMS = GlobalMemoryStatus()
					cfg.ctypesSCP.windll.kernel32.GlobalMemoryStatus(cfg.ctypesSCP.byref(GMS))
					tRam = GMS.totalRam
					ram = int((tRam / 1048576) / 2)
					cfg.ui.RAM_spinBox.setValue(ram)
				elif cfg.sysSCPNm == 'Darwin':
					cfg.ui.RAM_spinBox.setValue(1024)
				else:
					with open('/proc/meminfo') as t:
						for b in t:
							if b.startswith('MemTotal'):
								tRam = b.split()[1]
								break
					ram = int((int(tRam) / 1000) / 2)
					cfg.ui.RAM_spinBox.setValue(ram)
		except:
			pass
			
	# find file name without extension
	def fileNameNoExt(self, path):
		n = cfg.osSCP.path.basename(cfg.osSCP.path.splitext(path)[0])
		return n
	
	# find file name with extension
	def fileName(self, path):
		n = cfg.osSCP.path.basename(path)
		return n
	
	# find available processors
	def findAvailableProcessors(self):
		try:
			if cfg.sysSCP64bit == 'Yes':
				threads = cfg.osSCP.cpu_count()
				cfg.ui.CPU_spinBox.setValue(int((threads+1)/2))
		except:
			cfg.ui.CPU_spinBox.setValue(1)
