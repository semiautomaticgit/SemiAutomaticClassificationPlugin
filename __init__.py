# SemiAutomaticClassificationPlugin
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised 
# classification of remote sensing images, providing tools for the download, 
# the preprocessing and postprocessing of images.
# begin: 2012-12-29
# Copyright (C) 2012-2026 by Luca Congedo.
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
    return 'Version 9.0.0'


def icon():
    return 'semiautomaticclassificationplugin.png'


# noinspection PyPep8Naming
def qgisMinimumVersion():
    return '3.99'


def author():
    return 'Luca Congedo'


def email():
    return 'ing.congedoluca@gmail.com'


def category():
    return 'Raster'


# noinspection PyPep8Naming
def classFactory(iface):
    # Easy-Install: fast filesystem check — never block QGIS
    # (contributed by TerraLab — https://terralab.fr)
    deps_ready = False
    try:
        from .core.venv_manager import (
            _quick_check_packages, ensure_venv_packages_available,
        )
        is_ready, msg = _quick_check_packages()
        if is_ready:
            ensure_venv_packages_available()
            deps_ready = True
    except Exception as e:
        try:
            from qgis.core import QgsMessageLog, Qgis
            QgsMessageLog.logMessage(
                "SCP path setup error: {}".format(e),
                "SCP", level=Qgis.Warning
            )
        except Exception:
            pass

    if deps_ready:
        try:
            from .semiautomaticclassificationplugin import (
                SemiAutomaticClassificationPlugin
            )
            return SemiAutomaticClassificationPlugin(iface)
        except Exception as e:
            try:
                from qgis.core import QgsMessageLog, Qgis
                QgsMessageLog.logMessage(
                    "SCP import failed despite deps present: {}".format(e),
                    "SCP", level=Qgis.Warning
                )
            except Exception:
                pass

    # Dependencies missing or import failed — return lightweight stub
    return _SCPStubPlugin(iface)


class _SCPStubPlugin:
    """Minimal QGIS plugin stub shown when dependencies are not installed.

    Only uses PyQt6/qgis imports (always available). Does NOT import any
    SCP core module that depends on scipy/torch/etc.
    """

    def __init__(self, iface):
        self._iface = iface
        self._install_dialog = None

    def initGui(self):
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, self._show_install_dialog)

    def _show_install_dialog(self):
        from .core.install_dialog import SCPInstallDialog
        self._install_dialog = SCPInstallDialog(self._iface.mainWindow())
        self._install_dialog.install_finished.connect(
            self._on_install_finished
        )
        self._install_dialog.show()

    def _on_install_finished(self, success, message):
        from qgis.core import Qgis
        if success:
            self._iface.messageBar().pushMessage(
                'Semi-Automatic Classification Plugin',
                'Dependencies installed. Please restart QGIS.',
                level=Qgis.Info, duration=0
            )
        else:
            self._iface.messageBar().pushMessage(
                'Semi-Automatic Classification Plugin',
                'Dependency install failed. See log: View > Panels > '
                'Log Messages > SCP',
                level=Qgis.Warning, duration=0
            )

    def unload(self):
        if self._install_dialog is not None:
            try:
                self._install_dialog.close()
            except Exception:
                pass
            self._install_dialog = None


def homepage():
    return (
        'https://fromgistors.blogspot.com/p'
        '/semi-automatic-classification-plugin.html')


def tracker():
    return (
        'https://github.com/semiautomaticgit/SemiAutomaticClassificationPlugin'
        '/issues')


def repository():
    return (
        'https://github.com/semiautomaticgit/SemiAutomaticClassificationPlugin'
    )
