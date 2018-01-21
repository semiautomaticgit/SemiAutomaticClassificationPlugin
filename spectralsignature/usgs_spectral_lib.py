# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2018 by Luca Congedo
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



cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

class USGS_Spectral_Lib:

	def __init__(self):
		pass
			
	# add library list to combo
	def addLibrariesToCombo(self):
		cfg.ui.usgs_library_comboBox.blockSignals(True)
		cfg.ui.usgs_library_comboBox.clear()
		cfg.ui.usgs_library_comboBox.addItem("")
		for i in self.usgsLibNm:
			cfg.ui.usgs_library_comboBox.addItem(i)
		cfg.ui.usgs_library_comboBox.blockSignals(False)
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "add libraries")
				
	# add signature to list
	def addSignatureToList(self):
		if self.library is not None:
			if len(self.library) > 0:
				r = self.downloadLibrary(self.library)
				if r is not None:
					cfg.sigImport.USGSLibrary(r)
					# logger
					cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "signature added: " + str(r))
				
	# add chapter list to combo
	def addSpectralLibraryToCombo(self, libraryDB):
		for i in cfg.usgs_lib_list:
			cfg.ui.usgs_chapter_comboBox.addItem(i)
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "chapters added")
		
	# selection of chapter
	def chapterChanged(self):
		self.usgsLibNm = []
		self.usgsLib = []
		ch = cfg.ui.usgs_chapter_comboBox.currentText()
		if ch == cfg.usgs_C1:
			usgsList = cfg.usgs_C1p
		elif ch == cfg.usgs_C2:
			usgsList = cfg.usgs_C2p
		elif ch == cfg.usgs_C3:
			usgsList = cfg.usgs_C3p
		elif ch == cfg.usgs_C4:
			usgsList = cfg.usgs_C4p
		elif ch == cfg.usgs_C5:
			usgsList = cfg.usgs_C5p
		elif ch == cfg.usgs_C6:
			usgsList = cfg.usgs_C6p
		else:
			cfg.ui.usgs_library_comboBox.clear()
			return 1
		l = open(usgsList, 'r')
		for i in l.readlines( ):
			c = eval(i)
			self.usgsLibNm.append(c[0])
			self.usgsLib.append([c[1], c[2]])
		self.addLibrariesToCombo()
		cfg.ui.USGS_library_textBrowser.setHtml("")
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "chapter: " + str(ch))
		
	# download signature file
	def downloadLibrary(self, link):
		# date time for temp name
		dT = cfg.utls.getTime()
		try:
			check = cfg.utls.downloadFile(link, cfg.tmpDir + "/" + dT + ".asc", "query")
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "library downloaded: " + str(link))
			if check == "Yes":
				return cfg.tmpDir + "/" + dT + ".asc"
			else:
				raise ValueError('No')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr21()
		
	# download signature description and display
	def getSignatureDescription(self, link):
		# date time for temp name
		dT = cfg.utls.getTime()
		try:
			check = cfg.utls.downloadFile(link, cfg.tmpDir + "/" + dT + ".html", "query")
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "library downloaded: " + str(link))
			if check == "Yes":
				f =  open(cfg.tmpDir + "/" + dT + ".html", 'r')
				dHtml = f.read()
				cfg.ui.USGS_library_textBrowser.setHtml(dHtml)
			else:
				raise ValueError('No')
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr21()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "library description: " + str(link))
		
	# selection of library
	def libraryChanged(self):
		self.library = None
		lNm = cfg.ui.usgs_library_comboBox.currentText()
		if len(lNm) > 0:
			i = self.usgsLibNm.index(lNm)
			d, l = self.usgsLib[i]
			self.getSignatureDescription(d)
			self.library = l
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "library: " + str(l))
		else:
			cfg.ui.USGS_library_textBrowser.setHtml("")
