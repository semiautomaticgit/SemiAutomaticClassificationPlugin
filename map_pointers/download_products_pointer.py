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

from PyQt5.QtCore import Qt, pyqtSignal
from qgis.gui import QgsMapTool

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# noinspection PyArgumentList,PyPep8Naming
class DownloadProductsPointer(QgsMapTool):
    rightClicked = pyqtSignal(['QgsPointXY'])
    leftClicked = pyqtSignal(['QgsPointXY'])

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas

    def canvasReleaseEvent(self, event):
        point = self.canvas.getCoordinateTransform().toMapCoordinates(
            event.pos()
        )
        # click
        if event.button() == Qt.RightButton:
            self.rightClicked.emit(point)
        else:
            self.leftClicked.emit(point)
