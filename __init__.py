# SemiAutomaticClassificationPlugin
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised 
# classification of remote sensing images, providing tools for the download, 
# the preprocessing and postprocessing of images.
# begin: 2012-12-29
# Copyright (C) 2012-2023 by Luca Congedo.
# Author: Luca Congedo
# Email: ing.congedoluca@gmail.com
#
# This file is part of SemiAutomaticClassificationPlugin.
# SemiAutomaticClassificationPlugin is free software: you can redistribute it 
# and/or modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation, 
# either version 3 of the License, or (at your option) any later version.
# SemiAutomaticClassificationPlugin is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with SemiAutomaticClassificationPlugin. 
# If not, see <https://www.gnu.org/licenses/>.


def name():
    return 'Semi-Automatic Classification Plugin'


def description():
    return (
        'A plugin that integrates tools for easing the download, '
        'the preprocessing, processing, and postprocessing of '
        'remote sensing images.'
    )


def version():
    return 'Version 8.0.7 - Infinity'


def icon():
    return 'semiautomaticclassificationplugin.png'


# noinspection PyPep8Naming
def qgisMinimumVersion():
    return '3.00'


def author():
    return 'Luca Congedo'


def email():
    return 'ing.congedoluca@gmail.com'


def category():
    return 'Raster'


# noinspection PyPep8Naming
def classFactory(iface):
    from .semiautomaticclassificationplugin import (
        SemiAutomaticClassificationPlugin
    )
    return SemiAutomaticClassificationPlugin(iface)


def homepage():
    return (
        'https://fromgistors.blogspot.com/p'
        '/semi-automatic-classification-plugin.html')


def tracker():
    return (
        'https://github.com/semiautomaticgit/SemiAutomaticClassificationPlugin'
        '/issues')


def repository():
    return ('https://github.com/semiautomaticgit'
            '/SemiAutomaticClassificationPlugin')
