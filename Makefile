# CONFIGURATION
#PLUGIN_UPLOAD = $(CURDIR)/plugin_upload.py

# Makefile for a PyQGIS plugin

# translation
SOURCES = semiautomaticclassificationplugin.py ui/ui_semiautomaticclassificationplugin.py ui/ui_semiautomaticclassificationplugin_widget.py ui/ui_semiautomaticclassificationplugin_scatter_plot.py ui/ui_semiautomaticclassificationplugin_signature_plot.py ui/ui_semiautomaticclassificationplugin_dock_class.py __init__.py ui/semiautomaticclassificationplugindialog.py
TRANSLATIONS = i18n/semiautomaticclassificationplugin_it.ts i18n/semiautomaticclassificationplugin_es.ts i18n/semiautomaticclassificationplugin_pt_BR.ts i18n/semiautomaticclassificationplugin_pt.ts i18n/semiautomaticclassificationplugin_el_GR.ts i18n/semiautomaticclassificationplugin_uk_UA.ts i18n/semiautomaticclassificationplugin_ar.ts i18n/semiautomaticclassificationplugin_zh_CN.ts i18n/semiautomaticclassificationplugin_fr.ts i18n/semiautomaticclassificationplugin_de.ts i18n/semiautomaticclassificationplugin_ja.ts i18n/semiautomaticclassificationplugin_pl.ts

# global

PLUGINNAME = SemiAutomaticClassificationPlugin

PY_FILES = semiautomaticclassificationplugin.py ui/semiautomaticclassificationplugindialog.py __init__.py

EXTRAS = semiautomaticclassificationplugin.png

UI_FILES = ui/ui_semiautomaticclassificationplugin_scatter_plot.py ui/ui_semiautomaticclassificationplugin_signature_plot.py ui/ui_semiautomaticclassificationplugin_dock_class.py ui/ui_semiautomaticclassificationplugin.py ui/ui_semiautomaticclassificationplugin_widget.py

RESOURCE_FILES = ui/resources_rc.py

HELP = help/build/html

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc5 -o $*_rc.py  $<

%.py : %.ui
	pyuic5 -o $@ $< --from-imports

%.qm : %.ts
	lrelease $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/.qgis3/python/plugins
deploy: compile transcompile
	mkdir -p $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vfr i18n $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
#	cp -vfr $(HELP) $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)/help
	cp -vfr core $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vfr interface $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vfr spectral_signature $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vfr ui $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -vf metadata.txt $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME) -iname "__pycache__" -delete
	find $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME) -iname "*.directory" -delete
	find $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME) -iname "*.zip" -delete
	find $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME) -iname "remotior_sensus" -exec rm -rv {} +
	find $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/.qgis3/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

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
	#pylupdate5 Makefile
	pylupdate5 -noobsolete *.py core/*.py interface/*.py spectral_signature/*.py ui/*.ui -ts i18n/semiautomaticclassificationplugin.ts
	cp -vf $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)/i18n/semiautomaticclassificationplugin.ts $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)/i18n/models
	pylupdate5 -noobsolete *.py core/*.py interface/*.py spectral_signature/*.py ui/*.ui -ts i18n/semiautomaticclassificationplugin_pl.ts -ts $(TRANSLATIONS)


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