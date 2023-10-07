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


# Import PyQt libraries
from PyQt5.QtWidgets import QWidget, QGridLayout

# Import FigureCanvas
try:
    import matplotlib

    matplotlib.use('Qt5Agg')
except Exception as error:
    str(error)
try:
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvasQTAgg as FigCanvas
    )
    # Import Figure
    from matplotlib.figure import Figure
except Exception as error:
    str(error)
    FigCanvas = QWidget


# noinspection PyMissingConstructor
class SigCanvas(FigCanvas):

    def __init__(self):
        try:
            # Figure
            self.figure = Figure()
            # Add subplot for plot and legend
            self.ax = self.figure.add_axes([0.1, 0.15, 0.9, 0.9])
            # Canvas initialization
            FigCanvas.__init__(self, self.figure)
            # Set empty ticks
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.ax.set_aspect('equal', 'datalim')
        except Exception as err:
            str(err)


class ScatterWidget2(QWidget):

    # noinspection PyArgumentList
    def __init__(self, parent=None):
        try:
            # Widget initialization
            QWidget.__init__(self, parent)
            # Widget canvas
            self.sigCanvas = SigCanvas()
            # Create grid layout
            self.gridLayout = QGridLayout()
            # Add widget to grid
            self.gridLayout.addWidget(self.sigCanvas)
            # Set layout
            self.setLayout(self.gridLayout)
        except Exception as err:
            str(err)
            return
