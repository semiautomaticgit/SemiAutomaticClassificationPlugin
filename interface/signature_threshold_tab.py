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
"""Signature thresholds.

Allows for setting signature thresholds.
"""

from remotior_sensus.util import shared_tools

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# Create signature threshold table
def signature_thresholds_to_table():
    if cfg.scp_training is not None:
        table = cfg.dialog.ui.signature_threshold_tableWidget
        table.blockSignals(True)
        cfg.util_qt.clear_table(table)
        if cfg.scp_training.signature_catalog is not None:
            if cfg.scp_training.signature_catalog.table is not None:
                sig_table = cfg.scp_training.signature_catalog.table
                ids = sig_table.signature_id.tolist()
                row = 0
                for signature_id in ids:
                    signature_array = cfg.scp_training.signature_catalog.table[
                        cfg.scp_training.signature_catalog.table[
                            'signature_id'] == signature_id]
                    macroclass_id = signature_array.macroclass_id[0]
                    class_id = signature_array.class_id[0]
                    class_name = signature_array.class_name[0]
                    macroclass_name = (
                        cfg.scp_training.signature_catalog.macroclasses[
                            macroclass_id
                        ]
                    )
                    min_dist_thr = signature_array.min_dist_thr[0]
                    max_like_thr = signature_array.max_like_thr[0]
                    spec_angle_thr = signature_array.spec_angle_thr[0]
                    cfg.util_qt.insert_table_row(table, row)
                    cfg.util_qt.add_table_item(
                        table, int(macroclass_id), row, 0, False
                    )
                    cfg.util_qt.add_table_item(
                        table, str(macroclass_name), row, 1, False
                    )
                    cfg.util_qt.add_table_item(
                        table, int(class_id), row, 2, False
                    )
                    cfg.util_qt.add_table_item(
                        table, str(class_name), row, 3, False
                    )
                    cfg.util_qt.add_table_item(
                        table, str(min_dist_thr), row, 4
                    )
                    cfg.util_qt.add_table_item(
                        table, str(max_like_thr), row, 5
                    )
                    cfg.util_qt.add_table_item(
                        table, str(spec_angle_thr), row, 6
                    )
                    cfg.util_qt.add_table_item(
                        table, str(signature_id), row, 7, False
                    )
                    row += 1
        table.blockSignals(False)
        cfg.util_qt.sort_table_column(table, 7)


# reset thresholds
def reset_thresholds():
    answer = cfg.util_qt.question_box(
        cfg.translate('Reset thresholds'),
        cfg.translate('Are you sure you want to reset thresholds?')
    )
    if answer is True:
        table = cfg.dialog.ui.signature_threshold_tableWidget
        count = table.rowCount()
        for row in range(0, count):
            cfg.util_qt.set_table_item(table, row, 4, '0')
            cfg.util_qt.set_table_item(table, row, 5, '0')
            cfg.util_qt.set_table_item(table, row, 6, '0')


# set thresholds
def set_thresholds():
    table = cfg.dialog.ui.signature_threshold_tableWidget
    selection = []
    for selected in table.selectedIndexes():
        selection.append([selected.row(), selected.column()])
    if len(selection) > 0:
        value = cfg.dialog.ui.threshold_doubleSpinBox.value()
        table.setSortingEnabled(False)
        for item in reversed(selection):
            if item[1] == 6:
                if value > 90:
                    value = 90
                try:
                    cfg.util_qt.set_table_item(table, item[0], 6, str(value))
                except Exception as err:
                    str(err)
            elif item[1] == 5:
                if value > 100:
                    value = 100
                try:
                    cfg.util_qt.set_table_item(
                        table, item[0], 5,
                        str(value)
                    )
                except Exception as err:
                    str(err)
            else:
                try:
                    cfg.util_qt.set_table_item(table, item[0], 4, str(value))
                except Exception as err:
                    str(err)
        table.setSortingEnabled(True)


# set weights based on variance
def set_all_weights_from_variance():
    table = cfg.dialog.ui.signature_threshold_tableWidget
    selection = []
    for selected in table.selectedIndexes():
        selection.append([selected.row(), selected.column()])
    if len(selection) > 0:
        table.setSortingEnabled(False)
        for item in reversed(selection):
            signature_id = table.item(item[0], 7).text()
            values = cfg.scp_training.signature_catalog.signatures[
                signature_id].value
            standard_deviation = cfg.scp_training.signature_catalog.signatures[
                signature_id].standard_deviation
            mean_plus = []
            mean_minus = []
            for n in range(0, len(values)):
                mean_plus.append(values[n] + standard_deviation[n])
                mean_minus.append(values[n] - standard_deviation[n])
            # multiplicative factor
            fact = cfg.dialog.ui.multiplicative_threshold_doubleSpinBox.value()
            if item[1] == 6:
                angle_plus = shared_tools.calculate_spectral_angle(
                    values_x=cfg.utils.numpy_array_from_list(values),
                    values_y=cfg.utils.numpy_array_from_list(mean_plus)
                )
                angle_minus = shared_tools.calculate_spectral_angle(
                    values_x=cfg.utils.numpy_array_from_list(values),
                    values_y=cfg.utils.numpy_array_from_list(mean_minus)
                )
                try:
                    sam_value = fact * max([angle_plus, angle_minus])
                except Exception as err:
                    str(err)
                    sam_value = 0
                if sam_value > 90:
                    sam_value = 90
                cfg.scp_training.edit_signature_value(
                    signature_id=signature_id, field='spec_angle_thr',
                    value=sam_value
                )
                cfg.util_qt.set_table_item(table, item[0], 6, str(sam_value))
            elif item[1] == 4:
                distance_plus = shared_tools.calculate_euclidean_distance(
                    values_x=values, values_y=mean_plus
                )
                distance_minus = shared_tools.calculate_euclidean_distance(
                    values_x=values, values_y=mean_minus
                )
                try:
                    distance = fact * max([distance_plus, distance_minus])
                except Exception as err:
                    str(err)
                    distance = 0
                cfg.scp_training.edit_signature_value(
                    signature_id=signature_id, field='min_dist_thr',
                    value=distance
                )
                cfg.util_qt.set_table_item(table, item[0], 4, str(distance))
        table.setSortingEnabled(True)


# edited threshold table
def edited_threshold_table(row, column):
    table = cfg.dialog.ui.signature_threshold_tableWidget
    text = table.item(row, column).text()
    signature_id = table.item(row, 7).text()
    try:
        value = float(text)
    except Exception as err:
        str(err)
        value = 0
    if column == 4:
        cfg.scp_training.edit_signature_value(
            signature_id=signature_id, field='min_dist_thr', value=value
        )
    elif column == 5:
        if value > 100:
            table.blockSignals(True)
            cfg.util_qt.set_table_item(table, row, column, '100')
            table.blockSignals(False)
        cfg.scp_training.edit_signature_value(
            signature_id=signature_id, field='max_like_thr', value=value
        )
    elif column == 6:
        if value > 90:
            table.blockSignals(True)
            cfg.util_qt.set_table_item(table, row, column, '90')
            table.blockSignals(False)
        cfg.scp_training.edit_signature_value(
            signature_id=signature_id, field='spec_angle_thr', value=value
        )
