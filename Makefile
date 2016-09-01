#/**************************************************************************************************************************
# SemiAutomaticClassificationPlugin
#
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
# providing tools for the download, the preprocessing and postprocessing of images.
#
#                             -------------------
#        begin                : 2012-12-29
#        copyright            : (C) 2012-2017 by Luca Congedo
#        email                : ing.congedoluca@gmail.com
#**************************************************************************************************************************/
# 
#/**************************************************************************************************************************
# *
# *  This file is part of Semi-Automatic Classification Plugin
# * 
# *  Semi-Automatic Classification Plugin is free software: you can redistribute it and/or modify it under 
# *  the terms of the GNU General Public License as published by the Free Software Foundation, 
# *  version 3 of the License.
# * 
# *  Semi-Automatic Classification Plugin is distributed in the hope that it will be useful, 
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# *  FITNESS FOR A PARTICULAR PURPOSE. 
# *  See the GNU General Public License for more details.
# *  
# *  You should have received a copy of the GNU General Public License along with 
# *  Semi-Automatic Classification Plugin. If not, see <http://www.gnu.org/licenses/>. 
# *  
#**************************************************************************************************************************/

# CONFIGURATION
#PLUGIN_UPLOAD = $(CURDIR)/plugin_upload.py

# Makefile for a PyQGIS plugin 

# translation
SOURCES = semiautomaticclassificationplugin.py ui/ui_semiautomaticclassificationplugin.py ui/ui_semiautomaticclassificationplugin_scatter_plot.py ui/ui_semiautomaticclassificationplugin_signature_plot.py ui/ui_semiautomaticclassificationplugin_dock_class.py __init__.py ui/semiautomaticclassificationplugindialog.py
TRANSLATIONS = i18n/semiautomaticclassificationplugin_it.ts i18n/semiautomaticclassificationplugin_es.ts i18n/semiautomaticclassificationplugin_pt_BR.ts i18n/semiautomaticclassificationplugin_pt.ts i18n/semiautomaticclassificationplugin_el_GR.ts i18n/semiautomaticclassificationplugin_uk_UA.ts i18n/semiautomaticclassificationplugin_ar.ts i18n/semiautomaticclassificationplugin_zh_CN.ts i18n/semiautomaticclassificationplugin_fr.ts i18n/semiautomaticclassificationplugin_de.ts i18n/semiautomaticclassificationplugin_ja.ts i18n/semiautomaticclassificationplugin_pl.ts

# global

PLUGINNAME = SemiAutomaticClassificationPlugin

PY_FILES = semiautomaticclassificationplugin.py ui/semiautomaticclassificationplugindialog.py __init__.py

EXTRAS = semiautomaticclassificationplugin.png 

UI_FILES = ui/ui_semiautomaticclassificationplugin_scatter_plot.py ui/ui_semiautomaticclassificationplugin_signature_plot.py ui/ui_semiautomaticclassificationplugin_dock_class.py ui/ui_semiautomaticclassificationplugin.py

RESOURCE_FILES = ui/resources_rc.py

HELP = help/build/html

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<

%.py : %.ui
	pyuic4 -o $@ $<

%.qm : %.ts
	lrelease $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/.qgis2/python/plugins
deploy: compile doc transcompile
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
#	cp -vfr i18n $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
#	cp -vfr $(HELP) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/.qgis2/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/.qgis2/python/plugins/$(PLUGINNAME) -iname "*.directory" -delete
	find $(HOME)/.qgis2/python/plugins/$(PLUGINNAME) -iname "__0semiautomaticclass.log" -delete
	find $(HOME)/.qgis2/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;
	echo "firstrun" > $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/firstrun

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean 
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/.qgis2/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

# Create a zip package of the plugin named $(PLUGINNAME).zip. 
# This requires use of git (your plugin development directory must be a 
# git repository).
# To use, pass a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
package: compile
		rm -f $(PLUGINNAME).zip
		git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
		echo "Created package: $(PLUGINNAME).zip"

upload: zip
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

# transup
# update .ts translation files
transup:
	#pylupdate4 Makefile
	pylupdate4 -noobsolete *.py classificationdock/*.py core/*.py maininterface/*.py roidock/*.py spectralsignature/*.py ui/ui_utils.py ui/*.ui -ts i18n/semiautomaticclassificationplugin.ts 
	cp -vf $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/i18n/semiautomaticclassificationplugin.ts $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/i18n/models
	pylupdate4 -noobsolete *.py classificationdock/*.py core/*.py maininterface/*.py roidock/*.py spectralsignature/*.py ui/ui_utils.py ui/*.ui -ts i18n/semiautomaticclassificationplugin_pl.ts -ts $(TRANSLATIONS)

	
# transcompile
# compile translation files into .qm binary format
transcompile: $(TRANSLATIONS:.ts=.qm)

# transclean
# deletes all .qm files
transclean:
	rm -f i18n/*.qm

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

# build documentation with sphinx
doc: 
	cd help; make html
