"""
SCP Dependency Install Dialog — Non-blocking.

Non-modal QDialog that installs dependencies in a background QThread
while keeping QGIS fully responsive.

Easy-Install feature contributed by TerraLab (https://terralab.fr).
"""

import traceback

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton,
)
from qgis.core import QgsMessageLog, Qgis

LOG_TAG = "SCP"


class InstallWorker(QThread):
    """Background thread that runs the full dependency installation."""

    progress = pyqtSignal(int, str)   # percent, message
    finished = pyqtSignal(bool, str)  # success, message

    def run(self):
        try:
            from .venv_manager import create_venv_and_install
            success, msg = create_venv_and_install(
                progress_callback=self._progress_callback,
                cancel_check=None,
            )
            self.finished.emit(success, msg)
        except Exception as e:
            tb = traceback.format_exc()
            QgsMessageLog.logMessage(
                "Install worker exception:\n{}".format(tb),
                LOG_TAG, level=Qgis.Critical,
            )
            self.finished.emit(False, str(e))

    def _progress_callback(self, percent, message):
        self.progress.emit(percent, message)


class SCPInstallDialog(QDialog):
    """Non-modal dialog for SCP dependency installation."""

    install_finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SCP \u2014 Install Dependencies")
        self.setMinimumWidth(520)
        self.setMinimumHeight(200)
        self.setWindowFlags(
            self.windowFlags()
            & ~Qt.WindowType.WindowContextHelpButtonHint
        )
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._worker = None

        layout = QVBoxLayout(self)

        self._info_label = QLabel(
            "The Semi-Automatic Classification Plugin needs to install\n"
            "Python dependencies (remotior-sensus, scipy, scikit-learn,\n"
            "matplotlib, PyTorch CPU, torchvision).\n\n"
            "This will download ~500 MB and may take a few minutes.\n"
            "You can continue using QGIS during installation."
        )
        layout.addWidget(self._info_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        self._status_label = QLabel("Ready to install.")
        layout.addWidget(self._status_label)

        self._install_button = QPushButton("Install Dependencies")
        self._install_button.clicked.connect(self._start_install)
        layout.addWidget(self._install_button)

        self._close_button = QPushButton("OK")
        self._close_button.setVisible(False)
        self._close_button.clicked.connect(self.close)
        layout.addWidget(self._close_button)

        self.setLayout(layout)

    def _start_install(self):
        """Launch the install worker thread."""
        self._install_button.setVisible(False)
        self._progress_bar.setVisible(True)
        self._status_label.setText("Starting installation...")
        self._info_label.setText(
            "Installing required Python packages for the\n"
            "Semi-Automatic Classification Plugin.\n\n"
            "This may take a few minutes.\n"
            "You can continue using QGIS."
        )
        QgsMessageLog.logMessage(
            "Starting dependency installation...", LOG_TAG, level=Qgis.Info,
        )
        self._worker = InstallWorker(self)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    # -- slots --

    def _on_progress(self, percent, message):
        self._progress_bar.setValue(percent)
        self._status_label.setText(message)

    def _on_finished(self, success, message):
        self._worker = None

        if success:
            self._progress_bar.setValue(100)
            self._status_label.setText("Installation complete!")
            self._info_label.setText(
                "All dependencies installed successfully.\n\n"
                "Please restart QGIS to complete setup."
            )
            QgsMessageLog.logMessage(
                "Dependency installation succeeded.", LOG_TAG, level=Qgis.Info,
            )
        else:
            self._status_label.setText("Installation failed.")
            self._info_label.setText(
                "Error: {}\n\n"
                "Check the QGIS log for details:\n"
                "View \u2192 Panels \u2192 Log Messages \u2192 SCP".format(message)
            )
            QgsMessageLog.logMessage(
                "Dependency installation failed: {}".format(message),
                LOG_TAG, level=Qgis.Critical,
            )

        self._close_button.setVisible(True)
        self.install_finished.emit(success, message)

    # Prevent accidental close while installing
    def closeEvent(self, event):
        if self._worker is not None and self._worker.isRunning():
            event.ignore()
        else:
            super().closeEvent(event)
