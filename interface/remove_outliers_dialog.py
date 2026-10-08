# SemiAutomaticClassificationPlugin
# The Semi-Automatic Classification Plugin for QGIS allows for the supervised
# classification of remote sensing images, providing tools for the download,
# the preprocessing and postprocessing of images.
# begin: 2012-12-29
# Copyright (C) 2026 by Krzysztof Tyszko.
# Author: Krzysztof Tyszko
# Email: krzysztof_tyszko@outlook.com
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


from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QInputDialog,
    QTextBrowser,
    QTabWidget,
    QWidget,
)
from PyQt6.QtCore import Qt

FigCanvas = None
Figure = None
_matplotlib_available = False
try:
    import matplotlib

    matplotlib.use("Qt5Agg")
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanvas
    from matplotlib.figure import Figure

    _matplotlib_available = True
except Exception:
    pass

cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[""])


METHODS = {
    "MAD": {"threshold": 3.5},
    "Band Z-score": {"threshold": 3.0},
    "Percentile": {"lower_pct": 0.01, "upper_pct": 0.99},
    "IQR": {"factor": 1.5},
    "Mahalanobis": {"alpha": 0.025},
    "Robust Mahalanobis": {"alpha": 0.025},
    "HotellingT2": {"alpha": 0.05},
    "PCA Mahalanobis": {"variance_ratio": 0.95, "n_components": 3, "alpha": 0.025},
    "PCA Reconstruction": {
        "variance_ratio": 0.95, "n_components": 3, "contamination": 0.01,
    },
    "GMM": {"n_components": 2, "contamination": 0.01},
    "EllipticEnvelope": {"contamination": 0.01},
    "IsolationForest": {"contamination": 0.01},
    "LOF": {"n_neighbors": 20, "contamination": 0.01},
    "kNN": {"n_neighbors": 5, "contamination": 0.01},
    "OneClassSVM": {"nu": 0.01},
    "SAM": {"contamination": 0.01},
    "Erosion": {"iterations": 1},
}

_INT_PARAM_NAMES = {"n_components", "n_neighbors", "iterations", "sample_size"}

_FLOAT_PARAM_RANGES = {
    "contamination": (0.005, 4, 0.0, 0.5),
    "alpha": (0.005, 4, 0.0, 1.0),
    "nu": (0.005, 4, 0.0, 1.0),
    "lower_pct": (0.005, 4, 0.0, 1.0),
    "upper_pct": (0.005, 4, 0.0, 1.0),
    "threshold": (0.1, 3, 0.0, 100.0),
    "factor": (0.1, 3, 0.0, 100.0),
    # 0 < variance_ratio < 1 makes PCA select as many components as needed to
    # retain that share of variance; variance_ratio = 0 uses the fixed
    # n_components value instead
    "variance_ratio": (0.01, 2, 0.0, 0.999),
}

_INT_PARAM_RANGES = {
    "n_components": (1, 999),
    "n_neighbors": (2, 9999),
    "iterations": (1, 99),
    "sample_size": (100, 1000000),
}


_EROSION_METHOD = "Erosion"

# Step labels reported by the computational core are identifiers, kept in
# English so that they stay stable. Names of the detection methods are proper
# names and are shown as they are, while descriptive labels get a translated
# display form.
_METHOD_DISPLAY_NAMES = {
    "MajorityVoting": "Majority voting",
}


def method_display_name(method):
    return QApplication.translate(
        "semiautomaticclassificationplugin",
        _METHOD_DISPLAY_NAMES.get(method, method),
    )


def _coerce_params(method, raw_params):
    defaults = METHODS.get(method, {})
    out = dict(defaults)
    for key, val in raw_params.items():
        if key in _INT_PARAM_NAMES:
            try:
                out[key] = int(val)
            except (TypeError, ValueError):
                continue
        else:
            try:
                out[key] = float(val)
            except (TypeError, ValueError):
                continue
    return out


# detection reference scopes as (key, label) pairs; statistics are computed
# from the pixels of a single ROI, a whole class or a whole macroclass
_SCOPE_LABELS = (
    ("roi", "Single ROI"),
    ("class", "Entire class (class ID)"),
    ("macroclass", "Entire macroclass (macroclass ID)"),
)


class PipelineDialog(QDialog):

    # configure_only=True: OK confirms the pipeline configuration without
    # invoking the callback; the caller reads it through the getters after
    # exec() == Accepted;
    # scope_options: the permitted reference scopes; a single-element list
    # forces one scope and disables the combo box
    def __init__(self, removeOutliersCallback=None, signature_mode=False,
                 configure_only=False,
                 scope_options=("roi", "class", "macroclass")):
        super().__init__(None)
        self.removeOutliersCallback = removeOutliersCallback
        self._signature_mode = signature_mode
        self._configure_only = configure_only
        self._scope_options = tuple(scope_options)
        self.setWindowTitle(
            QApplication.translate(
                "semiautomaticclassificationplugin", "Pipeline Builder"
            )
        )
        self.resize(460, 520)
        layout = QVBoxLayout(self)

        # detection reference scope (statistics: ROI / class / macroclass)
        scope_layout = QHBoxLayout()
        scope_layout.addWidget(
            QLabel(
                QApplication.translate(
                    "semiautomaticclassificationplugin",
                    "Detect outliers relative to:"
                )
            )
        )
        self.scope_combo = QComboBox()
        for scope_key, scope_label in _SCOPE_LABELS:
            if scope_key in self._scope_options:
                self.scope_combo.addItem(
                    QApplication.translate(
                        "semiautomaticclassificationplugin", scope_label
                    ),
                    scope_key,
                )
        if self.scope_combo.count() <= 1:
            self.scope_combo.setEnabled(False)
        scope_layout.addWidget(self.scope_combo, stretch=1)
        layout.addLayout(scope_layout)

        layout.addWidget(
            QLabel(
                QApplication.translate("semiautomaticclassificationplugin", "Pipeline")
            )
        )

        self.pipeline_list = QListWidget()
        layout.addWidget(self.pipeline_list)

        btn_layout = QHBoxLayout()

        btn_add = QPushButton(
            QApplication.translate("semiautomaticclassificationplugin", "Add")
        )
        btn_add.clicked.connect(self.add_method)

        btn_remove = QPushButton(
            QApplication.translate("semiautomaticclassificationplugin", "Remove")
        )
        btn_remove.clicked.connect(self.remove_method)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)

        layout.addLayout(btn_layout)

        vote_layout = QHBoxLayout()
        self.vote_checkbox = QCheckBox(
            QApplication.translate(
                "semiautomaticclassificationplugin", "Use majority voting"
            )
        )
        self.vote_checkbox.stateChanged.connect(self.toggle_vote_threshold)
        self.vote_threshold_widget = QSpinBox()
        self.vote_threshold_widget.setRange(1, 1)
        self.vote_threshold_widget.setValue(1)
        self.vote_threshold_widget.setEnabled(False)
        # The threshold follows the majority until the user sets it manually.
        # Without this it would stay at 1 regardless of pipeline length, which
        # for pipelines longer than two methods would mean unanimity instead of
        # a majority (see majority_vote_threshold).
        self._vote_threshold_touched = False
        self._setting_vote_threshold = False
        self.vote_threshold_widget.valueChanged.connect(
            self._on_vote_threshold_changed
        )

        vote_layout.addWidget(self.vote_checkbox)
        vote_layout.addWidget(
            QLabel(
                QApplication.translate(
                    "semiautomaticclassificationplugin", "Vote threshold:"
                )
            )
        )
        vote_layout.addWidget(self.vote_threshold_widget)

        layout.addLayout(vote_layout)

        layout.addWidget(
            QLabel(
                QApplication.translate(
                    "semiautomaticclassificationplugin", "Parameters"
                )
            )
        )

        self.param_form = QFormLayout()
        layout.addLayout(self.param_form)

        self.pipeline_list.itemClicked.connect(self.show_parameters)

        self.current_item = None
        self.param_widgets = {}

        self.run_btn = QPushButton(
            QApplication.translate("semiautomaticclassificationplugin", "Run pipeline")
        )
        self.run_btn.clicked.connect(self.execute_pipeline)
        layout.addWidget(self.run_btn)

    def add_method(self):
        available = [
            m for m in METHODS if not (self._signature_mode and m == _EROSION_METHOD)
        ]
        method, ok = QInputDialog.getItem(
            self,
            QApplication.translate("semiautomaticclassificationplugin", "Add method"),
            QApplication.translate("semiautomaticclassificationplugin", "Method:"),
            available,
            0,
            False,
        )

        if not ok:
            return

        item = QListWidgetItem(method)
        item.setData(Qt.ItemDataRole.UserRole, _coerce_params(method, METHODS[method]))
        self.pipeline_list.addItem(item)
        self.update_vote_threshold_limit()

    def remove_method(self):
        for item in self.pipeline_list.selectedItems():
            self.pipeline_list.takeItem(self.pipeline_list.row(item))
        self.clear_params()
        self.update_vote_threshold_limit()

    def clear_params(self):
        while self.param_form.rowCount():
            self.param_form.removeRow(0)

    def show_parameters(self, item):

        self.current_item = item
        self.clear_params()

        params = item.data(Qt.ItemDataRole.UserRole) or {}
        self.param_widgets = {}

        for key, val in params.items():

            if key in _INT_PARAM_NAMES:
                widget = QSpinBox()
                lo, hi = _INT_PARAM_RANGES.get(key, (0, 999999))
                widget.setRange(lo, hi)
                widget.setValue(int(val))
            else:
                widget = QDoubleSpinBox()
                step, decimals, lo, hi = _FLOAT_PARAM_RANGES.get(
                    key, (0.1, 6, 0.0, 1.0e9)
                )
                widget.setDecimals(decimals)
                widget.setRange(lo, hi)
                widget.setSingleStep(step)
                widget.setValue(float(val))

            widget.valueChanged.connect(self.update_params)

            self.param_widgets[key] = widget
            self.param_form.addRow(QLabel(key), widget)

    def update_params(self):

        if self.current_item is None:
            return

        params = {}
        for key, widget in self.param_widgets.items():
            value = widget.value()
            params[key] = int(value) if key in _INT_PARAM_NAMES else float(value)

        self.current_item.setData(Qt.ItemDataRole.UserRole, params)

    def toggle_vote_threshold(self, _state):
        self.vote_threshold_widget.setEnabled(self.vote_checkbox.isChecked())
        self.update_vote_threshold_limit()

    def _on_vote_threshold_changed(self, _value):
        # Records that the threshold was set by the user, not by the code.
        if not self._setting_vote_threshold:
            self._vote_threshold_touched = True

    def _set_vote_threshold(self, value):
        # Sets the threshold programmatically, without marking it as manually
        # changed.
        self._setting_vote_threshold = True
        self.vote_threshold_widget.setValue(value)
        self._setting_vote_threshold = False

    def majority_vote_threshold(self):
    # vote_threshold counts votes FOR KEEPING a pixel, not for removing it. A
    # pixel is kept when at least vote_threshold methods consider it valid, so
    # the LOWER the threshold, the fewer pixels are removed. Requiring a
    # majority against a pixel, that is floor(k/2)+1 of k methods, means
    # ceil(k/2) votes for keeping: 1 for two methods, 2 for three, 3 for five.
        return (max(self.pipeline_list.count(), 1) + 1) // 2

    def update_vote_threshold_limit(self):
        count = max(self.pipeline_list.count(), 1)
        self.vote_threshold_widget.setRange(1, count)
        if not self._vote_threshold_touched:
            # majority by default, consistent with the check box label
            self._set_vote_threshold(self.majority_vote_threshold())
        elif self.vote_threshold_widget.value() > count:
            # manually set value, but the pipeline has become shorter
            self._set_vote_threshold(count)
        self.vote_threshold_widget.setEnabled(self.vote_checkbox.isChecked())

    def get_pipeline(self):

        steps = []

        for i in range(self.pipeline_list.count()):
            item = self.pipeline_list.item(i)
            steps.append((item.text(), item.data(Qt.ItemDataRole.UserRole)))

        return steps

    def get_voting(self):
        return self.vote_checkbox.isChecked()

    def get_vote_threshold(self):
        return self.vote_threshold_widget.value()

    def get_scope(self):
        return self.scope_combo.currentData()

    def execute_pipeline(self):
        pipeline = self.get_pipeline()

        if len(pipeline) == 0:
            cfg.mx.msg_war_outliers_pipeline_empty()
            return

        use_majority_voting = self.get_voting()
        vote_threshold = self.get_vote_threshold()
        scope = self.get_scope()

        if use_majority_voting and vote_threshold > len(pipeline):
            cfg.mx.msg_war_outliers_vote_threshold()
            return

        # in class scope a whole ROI may turn out to be an outlier and be
        # dropped from the catalog, which requires explicit user confirmation
        if scope in ("class", "macroclass") and not self._configure_only:
            answer = cfg.util_qt.question_box(
                QApplication.translate(
                    "semiautomaticclassificationplugin", "Remove outliers"
                ),
                QApplication.translate(
                    "semiautomaticclassificationplugin",
                    "Detection relative to an entire class or macroclass may "
                    "remove some ROIs completely from the training input. "
                    "Continue?"
                ),
            )
            if answer is not True:
                return

        if self._configure_only:
            self.accept()
            return

        try:
            result = self.removeOutliersCallback(
                pipeline, use_majority_voting, vote_threshold, scope
            )
        except Exception as err:
            cfg.mx.msg_err_outliers_pipeline_failed(err)
            return

        self.accept()
        if result is not None:
            ReportDialog(result).exec()


class ReportDialog(QDialog):

    def __init__(self, result, parent=None):
        super().__init__(parent)
        self._result = result
        self.setWindowTitle(
            QApplication.translate(
                "semiautomaticclassificationplugin", "Outlier Removal Report"
            )
        )
        self.resize(640, 520)

        layout = QVBoxLayout(self)

        browser = QTextBrowser()
        browser.setHtml(self._build_html(result))
        layout.addWidget(browser)

        btn_layout = QHBoxLayout()
        if _matplotlib_available:
            chart_btn = QPushButton(
                QApplication.translate(
                    "semiautomaticclassificationplugin", "Show chart"
                )
            )
            chart_btn.clicked.connect(self._show_chart)
            btn_layout.addWidget(chart_btn)
        btn_layout.addStretch()
        close_btn = QPushButton(
            QApplication.translate("semiautomaticclassificationplugin", "Close")
        )
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _show_chart(self):
        ChartDialog(self._result, self).exec()

    def _build_html(self, result):
        if isinstance(result, tuple) and len(result) == 3:
            _, _, report = result
            return self._html_drawing_roi(report)

        if isinstance(result, list):
            return self._html_catalog(result)

        return "<p>%s</p>" % QApplication.translate(
            "semiautomaticclassificationplugin", "No report data available"
        )

    def _html_drawing_roi(self, report):
        steps = report.get("steps", []) if isinstance(report, dict) else []
        total_raster = (
            report.get("total_raster_pixels") if isinstance(report, dict) else None
        )
        valid_px = report.get("valid_pixels") if isinstance(report, dict) else None

        if not steps:
            return "<p>%s</p>" % QApplication.translate(
                "semiautomaticclassificationplugin", "No steps executed"
            )

        last = steps[-1]
        total_removed = last["removed_pixels"]
        total_pct = last["removed_percent"]

        html = [
            "<h3>%s</h3>"
            % QApplication.translate(
                "semiautomaticclassificationplugin",
                "Outlier Removal Report – Current ROI",
            ),
            "<table border='0' cellpadding='3'>",
        ]
        if total_raster is not None:
            html.append(
                "<tr><td>%s</td><td>%d</td></tr>"
                % (
                    QApplication.translate(
                        "semiautomaticclassificationplugin",
                        "Total pixels (raster):",
                    ),
                    total_raster,
                )
            )
        if valid_px is not None:
            html.append(
                "<tr><td>%s</td><td>%d</td></tr>"
                % (
                    QApplication.translate(
                        "semiautomaticclassificationplugin", "Valid pixels:"
                    ),
                    valid_px,
                )
            )
        html += [
            "<tr><td><b>%s</b></td>"
            "<td><b>%d px (%.2f%%)</b></td></tr>"
            % (
                QApplication.translate(
                    "semiautomaticclassificationplugin", "Total removed:"
                ),
                total_removed,
                total_pct,
            ),
            "</table><br>",
            self._steps_table(steps),
        ]
        return "".join(html)

    def _html_catalog(self, report):
        if not report:
            return "<p>%s</p>" % QApplication.translate(
                "semiautomaticclassificationplugin", "No ROIs were processed"
            )

        total_removed = sum(r["removed_pixels"] for r in report)
        total_valid = sum(r["valid_pixels"] for r in report)
        total_raster = sum(r["total_raster_pixels"] for r in report)
        total_pct = 100.0 * total_removed / total_valid if total_valid > 0 else 0.0

        html = [
            "<h3>%s</h3>"
            % QApplication.translate(
                "semiautomaticclassificationplugin", "Outlier Removal Report"
            ),
            "<table border='0' cellpadding='3'>",
            "<tr><td><b>%s</b></td><td>%d</td></tr>"
            % (
                QApplication.translate(
                    "semiautomaticclassificationplugin", "ROIs processed:"
                ),
                len(report),
            ),
            "<tr><td><b>%s</b></td><td>%d</td></tr>"
            % (
                QApplication.translate(
                    "semiautomaticclassificationplugin",
                    "Total pixels (raster):",
                ),
                total_raster,
            ),
            "<tr><td><b>%s</b></td><td>%d</td></tr>"
            % (
                QApplication.translate(
                    "semiautomaticclassificationplugin", "Valid pixels:"
                ),
                total_valid,
            ),
            "<tr><td><b>%s</b></td><td><b>%d px (%.2f%%)</b></td></tr>"
            % (
                QApplication.translate(
                    "semiautomaticclassificationplugin", "Total removed:"
                ),
                total_removed,
                total_pct,
            ),
            "</table><hr>",
        ]

        for entry in report:
            sig_id = entry["sig_id"]
            removed = entry["removed_pixels"]
            valid = entry["valid_pixels"]
            raster_px = entry["total_raster_pixels"]
            pct = entry["removed_percent"]
            steps = entry.get("steps", [])

            html.append(
                "<h4>%s &nbsp; id: %s</h4>"
                % (
                    QApplication.translate("semiautomaticclassificationplugin", "ROI"),
                    sig_id,
                )
            )
            html.append(
                "<table border='0' cellpadding='3'>"
                "<tr><td>%s</td><td>%d</td></tr>"
                "<tr><td>%s</td><td>%d</td></tr>"
                "<tr><td>%s</td><td><b>%d px (%.2f%%)</b></td></tr>"
                "</table>"
                % (
                    QApplication.translate(
                        "semiautomaticclassificationplugin",
                        "Total pixels (raster):",
                    ),
                    raster_px,
                    QApplication.translate(
                        "semiautomaticclassificationplugin", "Valid pixels:"
                    ),
                    valid,
                    QApplication.translate(
                        "semiautomaticclassificationplugin", "Removed:"
                    ),
                    removed,
                    pct,
                )
            )

            if steps:
                html.append("<br>")
                html.append(self._steps_table(steps))

            html.append("<hr>")

        return "".join(html)

    # Builds an HTML table with per-step removal numbers.
    def _steps_table(self, steps):
        rows = [
            "<table border='1' cellpadding='4' cellspacing='0'>"
            "<tr>"
            "<th>%s</th>"
            "<th>%s</th>"
            "<th>%s</th>"
            "<th>%s</th>"
            "<th>%s</th>"
            "</tr>"
            % (
                QApplication.translate("semiautomaticclassificationplugin", "Step"),
                QApplication.translate("semiautomaticclassificationplugin", "Method"),
                QApplication.translate(
                    "semiautomaticclassificationplugin",
                    "Removed&nbsp;this&nbsp;step",
                ),
                QApplication.translate(
                    "semiautomaticclassificationplugin", "Cumul.&nbsp;removed"
                ),
                QApplication.translate(
                    "semiautomaticclassificationplugin", "Cumul.&nbsp;%"
                ),
            )
        ]
        prev_removed = 0
        for s in steps:
            step_removed = s["removed_pixels"] - prev_removed
            rows.append(
                "<tr>"
                "<td align='center'>%d</td>"
                "<td>%s</td>"
                "<td align='right'>%d px</td>"
                "<td align='right'>%d px</td>"
                "<td align='right'>%.2f%%</td>"
                "</tr>"
                % (
                    s["step"],
                    method_display_name(s["method"]),
                    step_removed,
                    s["removed_pixels"],
                    s["removed_percent"],
                )
            )
            prev_removed = s["removed_pixels"]
        rows.append("</table>")
        return "".join(rows)


class ChartDialog(QDialog):

    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            QApplication.translate(
                "semiautomaticclassificationplugin", "Outlier Removal Charts"
            )
        )
        self.resize(750, 520)

        layout = QVBoxLayout(self)

        if not _matplotlib_available:
            layout.addWidget(
                QLabel(
                    QApplication.translate(
                        "semiautomaticclassificationplugin",
                        "matplotlib is not available",
                    )
                )
            )
            btn = QPushButton(
                QApplication.translate("semiautomaticclassificationplugin", "Close")
            )
            btn.clicked.connect(self.accept)
            layout.addWidget(btn)
            return

        tabs = QTabWidget()
        layout.addWidget(tabs)

        if isinstance(result, tuple) and len(result) == 3:
            _, _, report = result
            steps = report.get("steps", [])
            valid_px = report.get("valid_pixels", 0)
            tab_label = QApplication.translate(
                "semiautomaticclassificationplugin", "Current ROI"
            )
            tabs.addTab(self._step_chart(tab_label, steps, valid_px), tab_label)

        elif isinstance(result, list) and result:
            summary_label = QApplication.translate(
                "semiautomaticclassificationplugin", "Summary"
            )
            tabs.addTab(self._summary_chart(result), summary_label)
            for entry in result:
                sig_id = entry["sig_id"]
                steps = entry.get("steps", [])
                valid_px = entry.get("valid_pixels", 0)
                label = sig_id[-14:] if len(sig_id) > 14 else sig_id
                tabs.addTab(self._step_chart(sig_id, steps, valid_px), label)

        close_btn = QPushButton(
            QApplication.translate("semiautomaticclassificationplugin", "Close")
        )
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _step_chart(self, title, steps, valid_pixels):
        fig = Figure(figsize=(6, 4), tight_layout=True)
        ax = fig.add_subplot(111)

        if not steps:
            ax.text(
                0.5,
                0.5,
                QApplication.translate("semiautomaticclassificationplugin", "No steps"),
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            return FigCanvas(fig)

        methods = [method_display_name(s["method"]) for s in steps]
        prev = 0
        deltas = []
        for s in steps:
            deltas.append(s["removed_pixels"] - prev)
            prev = s["removed_pixels"]

        x = list(range(len(methods)))
        bars = ax.bar(x, deltas, color="#d9534f", edgecolor="white", zorder=3)
        ax.set_xticks(x)
        ax.set_xticklabels(methods, rotation=20, ha="right", fontsize=9)
        ax.set_ylabel(
            QApplication.translate(
                "semiautomaticclassificationplugin",
                "Removed pixels (this step)",
            )
        )
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)

        if valid_pixels > 0:
            ax.axhline(
                valid_pixels,
                color="#5bc0de",
                linestyle="--",
                linewidth=1.2,
                label="%s (%d)"
                % (
                    QApplication.translate(
                        "semiautomaticclassificationplugin", "Valid pixels"
                    ),
                    valid_pixels,
                ),
            )
            ax.legend(fontsize=8)

        for bar, val in zip(bars, deltas):
            if val > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(valid_pixels * 0.005, 0.5),
                    str(val),
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        return FigCanvas(fig)

    def _summary_chart(self, report):
        fig = Figure(figsize=(6, 4), tight_layout=True)
        ax = fig.add_subplot(111)

        sig_ids = [e["sig_id"] for e in report]
        removed = [e["removed_pixels"] for e in report]
        valid = [e["valid_pixels"] for e in report]
        remaining = [v - r for v, r in zip(valid, removed)]

        x = list(range(len(sig_ids)))
        ax.bar(
            x,
            remaining,
            label=QApplication.translate(
                "semiautomaticclassificationplugin", "Remaining"
            ),
            color="#5cb85c",
            edgecolor="white",
            zorder=3,
        )
        ax.bar(
            x,
            removed,
            bottom=remaining,
            label=QApplication.translate(
                "semiautomaticclassificationplugin", "Removed"
            ),
            color="#d9534f",
            edgecolor="white",
            zorder=3,
        )

        labels = [s[-12:] if len(s) > 12 else s for s in sig_ids]
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
        ax.set_ylabel(
            QApplication.translate("semiautomaticclassificationplugin", "Pixels")
        )
        ax.set_title(
            QApplication.translate(
                "semiautomaticclassificationplugin",
                "Summary — removed per ROI",
            ),
            fontsize=10,
        )
        ax.legend(fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)

        for i, (rem, val) in enumerate(zip(removed, valid)):
            pct = 100.0 * rem / val if val > 0 else 0.0
            if rem > 0:
                ax.text(
                    i,
                    val + max(val * 0.01, 0.5),
                    "%.1f%%" % pct,
                    ha="center",
                    va="bottom",
                    fontsize=7,
                )

        return FigCanvas(fig)
