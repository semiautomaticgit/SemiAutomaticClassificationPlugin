# SemiAutomaticClassificationPlugin
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised 
# classification of remote sensing images, providing tools for the download, 
# the preprocessing and postprocessing of images.
# begin: 2012-12-29
# Copyright (C) 2012-2024 by Luca Congedo.
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
class RegionGrowingPointer(QgsMapTool):
    rightClicked = pyqtSignal(['QgsPointXY'])
    leftClicked = pyqtSignal(['QgsPointXY'])
    moved = pyqtSignal(['QgsPointXY'])

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas

    def canvasMoveEvent(self, event):
        point = self.canvas.getCoordinateTransform().toMapCoordinates(
            event.pos()
        )
        self.moved.emit(point)

    def canvasReleaseEvent(self, event):
        pnt = self.canvas.getCoordinateTransform().toMapCoordinates(
            event.pos()
        )
        # click
        if event.button() == Qt.RightButton:
            self.rightClicked.emit(pnt)
        else:
            self.leftClicked.emit(pnt)

    @staticmethod
    def keyPressEvent(event):
        if event.key() == Qt.Key_Control:
            cfg.ctrl_click = True
        elif event.key() == (Qt.Key_Control and Qt.Key_Z):
            cfg.scp_dock.delete_last_roi()
