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


cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[""])


def remove_outliers_drawing_roi():
    if cfg.temporary_roi is None:
        cfg.mx.msg_war_4()
        return

    # drawn ROI: the reference scope is forced to a single area
    def _callback(pipeline, use_majority_voting, vote_threshold, _scope):
        return cfg.remove_outliers.remove_outliers_drawing_roi(
            pipeline, use_majority_voting, vote_threshold
        )

    cfg.remove_outliers_dialog.PipelineDialog(
        _callback, scope_options=("roi",)
    ).exec()


def remove_outliers_selected_signatures():
    if cfg.scp_training is None or cfg.scp_training.signature_catalog is None:
        cfg.mx.msg_war_outliers_no_training()
        return

    signatures_selected, macroclass_ids = (
        cfg.scp_training.get_highlighted_selection_types()
    )

    # only macroclass nodes are selected: the scope is forced to macroclass
    if macroclass_ids and not signatures_selected:
        def _mc_callback(pipeline, use_majority_voting, vote_threshold,
                         _scope):
            return cfg.remove_outliers.remove_outliers_macroclasses(
                macroclass_ids, pipeline, use_majority_voting, vote_threshold
            )

        cfg.remove_outliers_dialog.PipelineDialog(
            _mc_callback, scope_options=("macroclass",)
        ).exec()
        return

    sig_ids = cfg.scp_training.get_highlighted_ids()

    catalog = cfg.scp_training.signature_catalog
    tbl = catalog.table
    sig_ids = [
        s
        for s in sig_ids
        if (tbl["signature_id"] == s).any()
        and tbl[tbl["signature_id"] == s]["geometry"][0] == 1
    ]

    if not sig_ids:
        cfg.mx.msg_war_outliers_no_selection()
        return

    def _callback(pipeline, use_majority_voting, vote_threshold, scope):
        return cfg.remove_outliers.remove_outliers_selected_signatures(
            sig_ids, pipeline, use_majority_voting, vote_threshold, scope
        )

    cfg.remove_outliers_dialog.PipelineDialog(
        _callback, scope_options=("roi", "class", "macroclass")
    ).exec()


def remove_outliers_all_signatures():
    if cfg.scp_training is None or cfg.scp_training.signature_catalog is None:
        cfg.mx.msg_war_outliers_no_training()
        return

    def _callback(pipeline, use_majority_voting, vote_threshold, scope):
        return cfg.remove_outliers.remove_outliers_all_signatures(
            pipeline, use_majority_voting, vote_threshold, scope
        )

    cfg.remove_outliers_dialog.PipelineDialog(
        _callback, scope_options=("roi", "class", "macroclass")
    ).exec()


def get_pipeline_config():
    dialog = cfg.remove_outliers_dialog.PipelineDialog(
        signature_mode=True, configure_only=True,
        scope_options=("roi", "class", "macroclass"),
    )
    if not dialog.exec():
        return None

    pipeline = dialog.get_pipeline()
    if not pipeline:
        return None

    return (
        pipeline, dialog.get_voting(), dialog.get_vote_threshold(),
        dialog.get_scope(),
    )
