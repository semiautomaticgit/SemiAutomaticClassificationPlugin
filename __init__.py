# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
                                 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
 providing a tool for the region growing of image pixels, creating polygon shapefiles intended for
 the collection of training areas (ROIs), and rapidly performing the classification process (or a preview).
                             -------------------
        begin                : 2012-12-29
        copyright            : (C) 2012-2015 by Luca Congedo
        email                : ing.congedoluca@gmail.com
**************************************************************************************************************************/
 
/**************************************************************************************************************************
 *
 *  This file is part of Semi-Automatic Classification Plugin
 * 
 *  Semi-Automatic Classification Plugin is free software: you can redistribute it and/or modify it under 
 *  the terms of the GNU General Public License as published by the Free Software Foundation, 
 *  version 3 of the License.
 * 
 *  Semi-Automatic Classification Plugin is distributed in the hope that it will be useful, 
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
 *  FITNESS FOR A PARTICULAR PURPOSE. 
 *  See the GNU General Public License for more details.
 *  
 *  You should have received a copy of the GNU General Public License along with 
 *  Semi-Automatic Classification Plugin. If not, see <http://www.gnu.org/licenses/>. 
 *  
**************************************************************************************************************************/

"""


def name():
    return "Semi-Automatic Classification Plugin"


def description():
    return "A plugin which allows for the semi-automatic supervised classification of remote sensing images, providing a tool for the region growing of image pixels, creating polygon shapefiles intended for the collection of training areas (ROIs), and rapidly performing the classification process (or a preview)."


def version():
    return "Version 4.1.0 - Frascati"


def icon():
    return "semiautomaticclassificationplugin.png"


def qgisMinimumVersion():
    return "2.0"

def author():
    return "Luca Congedo"

def email():
    return "ing.congedoluca@gmail.com"

def category():
    return "Raster"

def classFactory(iface):
    from semiautomaticclassificationplugin import SemiAutomaticClassificationPlugin
    return SemiAutomaticClassificationPlugin(iface)

def homepage():
    return "http://fromgistors.blogspot.com/p/semi-automatic-classification-plugin.html"

def tracker():
    return "http://hub.qgis.org/projects/semi-automatic-class/issues"
	
def repository():
	return "https://github.com/semiautomaticgit/SemiAutomaticClassificationPlugin"

