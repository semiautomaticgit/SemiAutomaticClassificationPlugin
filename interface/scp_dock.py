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


from copy import deepcopy
from datetime import datetime, timedelta
import shutil
import zipfile

import numpy
from PyQt5.QtCore import Qt, QVariant, QPoint, QPointF
from PyQt5.QtGui import (
    QColor, QFont, QCursor, QIcon, QPixmap, QPainter, QPolygonF
)
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QAbstractItemView, QCompleter, QMenu, QAction
)
from qgis.core import QgsGeometry, QgsFeature, QgsField
from qgis.gui import QgsVertexMarker, QgsHighlight

try:
    from remotior_sensus.core.spectral_signatures import (
        SpectralSignaturesCatalog, SpectralSignaturePlot, generate_signature_id
    )
    from remotior_sensus.tools import band_calc
    from remotior_sensus.util import raster_vector
except Exception as error:
    SpectralSignaturesCatalog = str
    str(error)

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

""" Class to manage signature catalog buffer """


class SignatureCatalogBuffer:

    def __init__(self, signature_catalog, max_size):
        cfg.logger.log.debug(
            'SignatureCatalogBuffer max_size: %s' % str(max_size)
        )
        self.max_size = max_size
        self.buffer = {}
        for key in range(-max_size, max_size + 1):
            self.buffer[key] = None
        self.buffer[0] = signature_catalog

    def set_catalog(self, signature_catalog):
        # delete files of undo max size that will be replaced
        if -self.max_size in self.buffer:
            if self.buffer[-self.max_size] is not None:
                try:
                    cfg.utils.remove_file(
                        self.buffer[-self.max_size].geometry_file
                    )
                    cfg.utils.remove_file(
                        self.buffer[-self.max_size].temporary_file
                    )
                except Exception as err:
                    str(err)
                self.buffer[-self.max_size] = None
        # remove redo keys
        for i in range(1, self.max_size + 1):
            if i in self.buffer:
                if self.buffer[i] is not None:
                    # delete temporary signature file
                    try:
                        cfg.utils.remove_file(
                            self.buffer[i].geometry_file
                        )
                        cfg.utils.remove_file(
                            self.buffer[i].temporary_file
                        )
                    except Exception as err:
                        str(err)
                # remove redo keys
                self.buffer[i] = None
                cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
        # replace undo keys
        for key in sorted(self.buffer):
            if key < 0:
                self.buffer[key] = self.buffer[key + 1]
        self.buffer[0] = signature_catalog

    def undo(self):
        for key in reversed(range(-self.max_size, self.max_size)):
            self.buffer[key + 1] = self.buffer[key]
            if self.buffer[key + 1] is not None:
                cfg.logger.log.debug(
                    'self.buffer[%s].geometry_file: %s'
                    % ((key + 1), str(self.buffer[key + 1].geometry_file))
                )
        cfg.logger.log.debug('self.buffer: %s' % self.buffer)
        cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(True)
        cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(False)
        if self.buffer[-1] is not None:
            cfg.logger.log.debug('self.buffer[-1]: %s' % self.buffer[-1])
            cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(True)
        return self.buffer[0]

    def redo(self):
        for key in range(-self.max_size + 1, self.max_size + 1):
            self.buffer[key - 1] = self.buffer[key]
            if self.buffer[key - 1] is not None:
                cfg.logger.log.debug(
                    'self.buffer[%s].geometry_file: %s'
                    % ((key - 1), str(self.buffer[key - 1].geometry_file))
                )
        cfg.logger.log.debug('self.buffer: %s' % self.buffer)
        cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(True)
        cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
        if self.buffer[1] is not None:
            cfg.logger.log.debug('self.buffer[1]: %s' % self.buffer[1])
            cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(True)
        return self.buffer[0]

    def set_max_size(self, max_size):
        self.max_size = max_size
        signature_catalog = self.buffer[0]
        self.buffer = {}
        for key in range(-max_size, max_size + 1):
            self.buffer[key] = None
        self.buffer[0] = signature_catalog


""" Class to manage signature catalog and vector input in QGIS """


class TrainingVectorLayer:

    # noinspection PyArgumentList
    def __init__(
            self, signature_catalog: SpectralSignaturesCatalog,
            output_path: str
    ):
        # vector layer
        self.vector = None
        self.layer = None
        # layer editing
        self.editing = False
        # dictionary of items of ROI and signatures in dock tree
        self.class_dock_tree = {}
        # dictionary of items of macroclasses in dock tree
        self.macroclass_dock_tree = {}
        self.collapse_tree = True
        # reset classification preview classifier
        cfg.classifier_preview = None
        cfg.dock_class_dlg.ui.button_Save_ROI.setEnabled(False)
        cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(False)
        cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
        # reset
        if signature_catalog is False:
            # reset table tree
            self.tree = self.clear_tree()
            project = cfg.util_qgis.get_qgis_project()
            # remove training input
            if cfg.scp_training is not None:
                try:
                    project.removeMapLayer(cfg.scp_training.layer)
                except Exception as err:
                    str(err)
            cfg.scp_training = None
            cfg.project_registry[cfg.reg_training_input_path] = ''
            cfg.dock_class_dlg.ui.trainingFile_lineEdit.setText('')
        # init
        else:
            cfg.logger.log.debug(
                'TrainingVectorLayer output_path: %s' % str(output_path)
            )
            # create buffer
            self.signature_catalog_buffer = SignatureCatalogBuffer(
                signature_catalog,
                max_size=cfg.qgis_registry[cfg.reg_max_train_buffer]
            )
            self.signature_catalog = signature_catalog
            cfg.logger.log.debug(
                'signature_catalog %s'
                % str(signature_catalog)
            )
            self.temporary_file = (
                cfg.rs.configurations.temp.temporary_file_path(
                    name_suffix='.scpx'
                )
            )
            cfg.logger.log.debug(
                'self.temporary_file: %s'
                % str(self.temporary_file)
            )
            # define output path
            self.output_path = output_path
            cfg.logger.log.debug(
                'self.output_path: %s'
                % str(self.output_path)
            )
            cfg.project_registry[cfg.reg_training_input_path] = output_path
            cfg.dock_class_dlg.ui.trainingFile_lineEdit.setText(output_path)
            # create self.layer in map
            self.add_vector_to_map()
            # connect project saved
            cfg.util_qgis.get_qgis_project().projectSaved.connect(
                self.project_saved
            )
            # connect to table tree
            self.tree = self.roi_signature_table_tree()

    # disable editing
    # noinspection PyPep8Naming
    def beforeEditingStarted(self):
        if self.editing is False:
            self.layer.commitChanges(stopEditing=True)
            cfg.mx.msg_inf_1()

    # set max size buffer
    def set_max_size_buffer(self, max_size):
        self.signature_catalog_buffer.max_size(max_size)

    # save signature catalog to file
    def signature_catalog_copy(self):
        cfg.logger.log.debug('signature_catalog_copy')
        signature_catalog = deepcopy(self.signature_catalog)
        # copy geometry file to temporary file
        geometry_temp_path = (
            cfg.rs.configurations.temp.temporary_file_path(
                name_suffix='.gpkg'
            )
        )
        cfg.rs.files_directories.copy_file(
            signature_catalog.geometry_file, geometry_temp_path
        )
        signature_catalog.geometry_file = geometry_temp_path
        return signature_catalog

    # save signature catalog to file
    def project_saved(self):
        self.save_signature_catalog(path=self.output_path)
        # save backup
        self.save_signature_catalog(
            path='%s%s' % (self.output_path, cfg.backup_name)
        )

    # reset signature catalog
    def reset_signature_catalog(self):
        cfg.logger.log.debug('reset_signature_catalog')
        project = cfg.util_qgis.get_qgis_project()
        try:
            project.removeMapLayer(self.layer)
        except Exception as err:
            str(err)
        cfg.map_canvas.setRenderFlag(False)
        cfg.map_canvas.setRenderFlag(True)
        self.signature_catalog_buffer = None
        self.signature_catalog = None
        self.vector = None
        self.layer = None
        self.output_path = ''
        cfg.dock_class_dlg.ui.trainingFile_lineEdit.setText('')
        cfg.project_registry[cfg.reg_training_input_path] = ''
        # reset table tree
        self.tree = self.clear_tree()
        self.macroclass_dock_tree = {}
        cfg.dock_class_dlg.ui.label_48.setText(
            cfg.translate(' ROI & Signature list')
        )

    # save signature catalog to file
    def save_signature_catalog(self, path=None, signature_id_list=None):
        if path is None:
            path = self.output_path
        if self.signature_catalog is not None:
            self.signature_catalog.save(
                output_path=path, signature_id_list=signature_id_list
            )
            cfg.logger.log.debug('save_signature_catalog: %s' % str(path))
        else:
            cfg.logger.log.debug('save_signature_catalog: catalog is None')

    # save signature catalog to temporary file
    def save_temporary_signature_catalog(self):
        cfg.logger.log.debug('save_temporary_signature_catalog')
        if self.signature_catalog is not None:
            self.signature_catalog.save(self.temporary_file)
            cfg.logger.log.debug(
                'save_temporary_signature_catalog: %s'
                % str(self.temporary_file)
            )
        else:
            cfg.logger.log.debug('save_signature_catalog: catalog is None')

    # set new signature catalog
    # noinspection PyArgumentList
    def set_signature_catalog(self, signature_catalog):
        cfg.logger.log.debug('set_signature_catalog')
        self.signature_catalog_buffer.set_catalog(signature_catalog)
        self.signature_catalog = signature_catalog
        # create self.layer in map
        self.add_vector_to_map()

    # edit vector
    def edit_vector(self, expression, field_name, value):
        self.editing = True
        cfg.util_qgis.edit_layer_features(
            layer=self.layer, expression=expression, field_name=field_name,
            value=value
        )
        self.editing = False

    # undo signature catalog
    def undo(self):
        cfg.logger.log.debug('undo')
        if self.signature_catalog is not None:
            cfg.logger.log.debug(
                'self.signature_catalog.geometry_file: %s'
                % str(self.signature_catalog.geometry_file)
            )
        self.signature_catalog = self.signature_catalog_buffer.undo()
        # connect to table tree
        self.tree = self.roi_signature_table_tree()
        # create self.layer in map
        self.add_vector_to_map()

    # redo signature catalog
    def redo(self):
        cfg.logger.log.debug('redo')
        if self.signature_catalog is not None:
            cfg.logger.log.debug(
                'self.signature_catalog.geometry_file: %s'
                % str(self.signature_catalog.geometry_file)
            )
        self.signature_catalog = self.signature_catalog_buffer.redo()
        # connect to table tree
        self.tree = self.roi_signature_table_tree()
        # create self.layer in map
        self.add_vector_to_map()

    # add vector to map
    def add_vector_to_map(self):
        project = cfg.util_qgis.get_qgis_project()
        cfg.map_canvas.setRenderFlag(False)
        if self.layer is not None:
            try:
                project.removeMapLayer(self.layer)
                self.vector = None
            except Exception as err:
                str(err)
        if self.signature_catalog is not None:
            cfg.logger.log.debug(
                'self.signature_catalog.geometry_file: %s'
                % str(self.signature_catalog.geometry_file)
            )
        self.vector = cfg.util_qgis.add_vector_layer(
            self.signature_catalog.geometry_file, cfg.scp_layer_name, 'ogr'
        )
        self.layer = project.addMapLayer(self.vector)
        table_config = self.layer.attributeTableConfig()
        try:
            table_config.setColumnHidden(0, True)
            table_config.setColumnHidden(1, True)
            self.layer.setAttributeTableConfig(table_config)
            cfg.util_qgis.training_symbol(self.layer)
        except Exception as err:
            cfg.logger.log.error(str(err))
        cfg.map_canvas.setRenderFlag(True)
        # disable layer editing
        self.layer.editingStarted.connect(self.beforeEditingStarted)

    # edit signature value
    def edit_signature_value(self, signature_id, field, value):
        self.signature_catalog.table[field][
            self.signature_catalog.table['signature_id'] == signature_id
            ] = value

    # create ROI and signature table tree
    def roi_signature_table_tree(self, tree=None):
        cfg.logger.log.debug('roi_signature_table_tree')
        # reset classification preview classifier
        cfg.classifier_preview = None
        self.tree = self.clear_tree(tree)
        self.tree.blockSignals(True)
        self.tree.setSortingEnabled(False)
        macroclass_list = []
        # macroclasses
        for macroclass in self.signature_catalog.macroclasses:
            macroclass_name = self.signature_catalog.macroclasses[macroclass]
            macroclass_list.append(macroclass_name)
            if macroclass in self.signature_catalog.macroclasses_color_string:
                macroclass_color = (
                    self.signature_catalog.macroclasses_color_string[
                        macroclass
                    ]
                )
            else:
                macroclass_color = cfg.rs.shared_tools.random_color()
                self.signature_catalog.macroclasses_color_string[
                    macroclass] = macroclass_color
            # add macroclass items
            self.add_macroclass_tree_item(
                macroclass=macroclass, macroclass_info=macroclass_name,
                color=macroclass_color, checkbox_state=None
            )
        cfg.logger.log.debug('macroclass_list: %s' % str(macroclass_list))
        # add spectral signatures and ROIs
        if self.signature_catalog.table is None:
            signatures = []
        else:
            signatures = self.signature_catalog.table.signature_id.tolist()
        class_name_list = []
        for signature in signatures:
            if signature != 'N/A':
                signature_array = self.signature_catalog.table[
                    self.signature_catalog.table['signature_id'] == signature]
                macroclass_id = signature_array.macroclass_id[0]
                class_id = signature_array.class_id[0]
                class_name = signature_array.class_name[0]
                class_name_list.append(class_name)
                selected = signature_array.selected[0]
                geometry_check = signature_array.geometry[0]
                signature_check = signature_array.signature[0]
                color = signature_array.color[0]
                if signature_check == 1 and geometry_check == 1:
                    type_info = cfg.roi_and_signature_type
                elif geometry_check == 1:
                    type_info = cfg.roi_type
                elif signature_check == 1:
                    type_info = cfg.signature_type
                else:
                    type_info = ''
                    cfg.logger.log.error('type_info empty')
                # replace for checkbox state
                if selected == 1:
                    selected = 2
                self.add_class_tree_item(
                    macroclass_id=macroclass_id, class_id=class_id,
                    class_info=class_name, type_info=type_info,
                    signature_id=signature, color=color,
                    checkbox_state=selected
                )
        cfg.logger.log.debug('class_name_list: %s' % str(class_name_list))
        self.tree.show()
        self.tree.setSortingEnabled(True)
        self.tree.blockSignals(False)
        # info completer
        class_info_completer(class_name_list)
        macroclass_info_completer(macroclass_list)
        # filter
        filter_tree()
        # connect signature threshold table
        cfg.signature_threshold.signature_thresholds_to_table()
        cfg.scp_training = self
        return self.tree

    # add signature item
    def add_class_tree_item(
            self, macroclass_id, class_id, class_info,
            type_info, signature_id, color=None, checkbox_state=None
    ):
        self.class_dock_tree[str(signature_id)] = QTreeWidgetItem()
        try:
            self.macroclass_dock_tree[macroclass_id].addChild(
                self.class_dock_tree[str(signature_id)]
            )
        except Exception as err:
            cfg.logger.log.error(str(err))
            self.add_macroclass_tree_item(
                macroclass=macroclass_id, macroclass_info=''
            )
        self.class_dock_tree[str(signature_id)].setFlags(
            Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable |
            Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        )
        if checkbox_state is not None:
            self.class_dock_tree[str(signature_id)].setCheckState(
                0, int(checkbox_state)
            )
        self.class_dock_tree[str(signature_id)].setData(
            0, 0, int(macroclass_id)
        )
        self.class_dock_tree[str(signature_id)].setData(
            1, 0, int(class_id)
        )
        self.class_dock_tree[str(signature_id)].setData(
            2, 0, str(class_info)
        )
        self.class_dock_tree[str(signature_id)].setData(
            3, 0, str(type_info)
        )
        self.class_dock_tree[str(signature_id)].setData(
            5, 0, str(signature_id)
        )
        if color is not None:
            self.class_dock_tree[str(signature_id)].setBackground(
                4, QColor(color)
            )

    # add macroclass item
    def add_macroclass_tree_item(
            self, macroclass, macroclass_info, color=None, checkbox_state=None
    ):
        row = self.tree.topLevelItemCount()
        self.macroclass_dock_tree[macroclass] = QTreeWidgetItem(row)
        self.tree.addTopLevelItem(self.macroclass_dock_tree[macroclass])
        self.macroclass_dock_tree[macroclass].setFlags(
            Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable |
            Qt.ItemIsDropEnabled
        )
        self.macroclass_dock_tree[macroclass].setExpanded(True)
        self.macroclass_dock_tree[macroclass].setData(
            0, 0, int(macroclass)
        )
        self.macroclass_dock_tree[macroclass].setData(
            2, 0, str(macroclass_info)
        )
        self.macroclass_dock_tree[macroclass].setData(
            5, 0, int(macroclass)
        )
        font = QFont()
        font.setBold(True)
        self.macroclass_dock_tree[macroclass].setFont(0, font)
        self.macroclass_dock_tree[macroclass].setFont(2, font)
        if checkbox_state is not None:
            self.macroclass_dock_tree[macroclass].setCheckState(
                0, checkbox_state
            )
        if color is not None:
            self.macroclass_dock_tree[macroclass].setBackground(
                4, QColor(color)
            )

    # clear tree
    # noinspection PyUnresolvedReferences
    def clear_tree(self, tree=None):
        cfg.logger.log.debug('clear_tree')
        self.class_dock_tree = {}
        self.macroclass_dock_tree = {}
        if tree is None:
            order = 0
            sorter = Qt.AscendingOrder
        else:
            order = tree.header().sortIndicatorOrder()
            sorter = tree.header().sortIndicatorSection()
            tree.deleteLater()
        cfg.dock_class_dlg.ui.signature_list_treeWidget = (
            QTreeWidget(cfg.dock_class_dlg.ui.tab_2)
        )
        tree_widget = cfg.dock_class_dlg.ui.signature_list_treeWidget
        tree_widget.setEditTriggers(
            QAbstractItemView.AnyKeyPressed | QAbstractItemView.SelectedClicked
        )
        tree_widget.setAlternatingRowColors(True)
        tree_widget.setSelectionMode(
            QAbstractItemView.MultiSelection
        )
        tree_widget.setIndentation(5)
        tree_widget.setExpandsOnDoubleClick(False)
        tree_widget.setObjectName('signature_list_treeWidget')
        cfg.dock_class_dlg.ui.gridLayout.addWidget(tree_widget, 1, 1, 1, 1)
        tree_widget.setSortingEnabled(True)
        tree_widget.headerItem().setText(0, cfg.translate('MC ID'))
        tree_widget.headerItem().setText(1, cfg.translate('C ID'))
        tree_widget.headerItem().setText(2, cfg.translate('Name'))
        tree_widget.headerItem().setText(3, cfg.translate('Type'))
        tree_widget.headerItem().setText(4, cfg.translate('Color'))
        tree_widget.headerItem().setText(5, 'signature_id')
        # tree list
        tree_widget.header().hideSection(5)
        tree_widget.header().setSortIndicator(sorter, order)
        cfg.util_qt.set_tree_column_width_list(
            tree_widget, [[0, 60], [1, 30], [2, 100], [3, 40], [4, 30]]
        )
        # connect to edited cell
        tree_widget.itemChanged.connect(self.edited_cell_tree)
        # connect to signature list double click
        tree_widget.itemDoubleClicked.connect(self.signature_tree_double_click)
        #  context menu
        tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        tree_widget.customContextMenuRequested.connect(context_menu)
        return tree_widget

    # edit macroclass value
    def edit_macroclass(self, macroclass_value):
        ids = self.get_highlighted_ids()
        for signature_id in ids:
            # set macroclass in table
            old_value = self.signature_catalog.table.macroclass_id[
                self.signature_catalog.table['signature_id'] == signature_id
                ]
            self.signature_catalog.table.macroclass_id[
                self.signature_catalog.table[
                    'signature_id'] == signature_id] = macroclass_value
            # add macroclass in dictionary
            if macroclass_value not in self.signature_catalog.macroclasses:
                self.signature_catalog.macroclasses[macroclass_value] = (
                    'macroclass'
                )
                macroclass_color = (
                    cfg.rs.shared_tools.random_color()
                )
                self.signature_catalog.macroclasses_color_string[
                    macroclass_value] = macroclass_color
            # check if isolated macroclass
            check_id = self.signature_catalog.table.macroclass_id[
                self.signature_catalog.table[
                    'macroclass_id'] == old_value]
            if len(check_id) == 0:
                try:
                    del self.signature_catalog.macroclasses[
                        old_value]
                    del self.macroclass_dock_tree[old_value]
                    cat = self.signature_catalog
                    del cat.macroclasses_color_string[old_value]
                except Exception as err:
                    str(err)
            # set macroclass in geometry
            expression = '"%s" = \'%s\'' % (
                cfg.rs.configurations.uid_field_name, signature_id
            )
            self.edit_vector(
                expression=expression, field_name='macroclass_id',
                value=macroclass_value
            )

    # edited cell
    def edited_cell_tree(self, item, column):
        table = cfg.dock_class_dlg.ui.signature_list_treeWidget
        table.setSortingEnabled(False)
        table.blockSignals(True)
        reload = False
        # items
        try:
            signature_id = list(self.class_dock_tree.keys())[
                list(self.class_dock_tree.values()).index(item)]
            macroclass_id = False
        except Exception as err:
            str(err)
            try:
                macroclass_id = list(self.macroclass_dock_tree.keys())[
                    list(self.macroclass_dock_tree.values()).index(item)]
                signature_id = False
            except Exception as err:
                cfg.logger.log.error(str(err))
                self.roi_signature_table_tree()
                return
        # item value
        value = item.text(column)
        cfg.logger.log.debug(
            'edited_cell_tree column: %s; value: %s'
            % (str(column), str(value))
        )
        cfg.logger.log.debug(
            'signature_id: %s; macroclass_id: %s'
            % (str(signature_id), str(macroclass_id))
        )
        # macroclass column
        if column == 0:
            # signature item
            if signature_id is not False:
                # get old value from table
                old_value = self.signature_catalog.table[
                    self.signature_catalog.table[
                        'signature_id'] == signature_id].macroclass_id[0]
                try:
                    value = int(value)
                except Exception as err:
                    str(err)
                    item.setData(column, old_value)
                    value = old_value
                if old_value != value:
                    if value < 0:
                        item.setData(column, old_value)
                    else:
                        # set macroclass in table
                        self.signature_catalog.table.macroclass_id[
                            self.signature_catalog.table[
                                'signature_id'] == signature_id] = value
                        # add macroclass in dictionary
                        if value not in self.signature_catalog.macroclasses:
                            self.signature_catalog.macroclasses[value] = (
                                'macroclass'
                            )
                            macroclass_color = (
                                cfg.rs.shared_tools.random_color()
                            )
                            self.signature_catalog.macroclasses_color_string[
                                value] = macroclass_color
                        # check if isolated macroclass
                        check_id = self.signature_catalog.table.macroclass_id[
                            self.signature_catalog.table[
                                'macroclass_id'] == old_value]
                        if len(check_id) == 0:
                            try:
                                del self.signature_catalog.macroclasses[
                                    old_value]
                                del self.macroclass_dock_tree[old_value]
                                cat = self.signature_catalog
                                del cat.macroclasses_color_string[old_value]
                            except Exception as err:
                                str(err)
                        # set macroclass in geometry
                        expression = '"%s" = \'%s\'' % (
                            cfg.rs.configurations.uid_field_name, signature_id
                        )
                        self.edit_vector(
                            expression=expression, field_name='macroclass_id',
                            value=value
                        )
                # set selected in table
                checked = item.checkState(0)
                if checked == 2:
                    self.signature_catalog.table.selected[
                        self.signature_catalog.table[
                            'signature_id'] == signature_id] = 1
                else:
                    self.signature_catalog.table.selected[
                        self.signature_catalog.table[
                            'signature_id'] == signature_id] = 0
                reload = True
            # macroclass item
            elif macroclass_id is not False:
                # get old value from table
                old_value = macroclass_id
                try:
                    value = int(value)
                except Exception as err:
                    str(err)
                    item.setData(column, old_value)
                    value = old_value
                if old_value != value:
                    if value < 0:
                        item.setData(column, old_value)
                        value = old_value
                    # add macroclass in dictionary
                    if value not in self.signature_catalog.macroclasses:
                        self.signature_catalog.macroclasses[value] = (
                            'macroclass'
                        )
                        macroclass_color = cfg.rs.shared_tools.random_color()
                        self.signature_catalog.macroclasses_color_string[
                            value] = macroclass_color
                    # change signature macroclass
                    self.signature_catalog.table.macroclass_id[
                        self.signature_catalog.table[
                            'macroclass_id'] == old_value] = value
                    # check if isolated macroclass
                    check_id = self.signature_catalog.table.macroclass_id[
                        self.signature_catalog.table[
                            'macroclass_id'] == old_value]
                    if len(check_id) == 0:
                        try:
                            del self.signature_catalog.macroclasses[
                                old_value]
                            del self.macroclass_dock_tree[old_value]
                            cat = self.signature_catalog
                            del cat.macroclasses_color_string[old_value]
                        except Exception as err:
                            str(err)
                    # set macroclass in geometry
                    expression = '"%s" = \'%s\'' % (
                        'macroclass_id', old_value
                    )
                    self.edit_vector(
                        expression=expression, field_name='macroclass_id',
                        value=value
                    )
                reload = True
            else:
                reload = True
        # class column
        elif column == 1:
            # signature item
            if signature_id is not False:
                # get old value from table
                old_value = self.signature_catalog.table[
                    self.signature_catalog.table[
                        'signature_id'] == signature_id].class_id[0]
                try:
                    value = int(value)
                except Exception as err:
                    str(err)
                    item.setData(column, old_value)
                    value = old_value
                if old_value != value:
                    if value < 0:
                        item.setData(column, old_value)
                    else:
                        # set class in table
                        self.signature_catalog.table.class_id[
                            self.signature_catalog.table[
                                'signature_id'] == signature_id] = value
                        # set class in geometry
                        expression = '"%s" = \'%s\'' % (
                            cfg.rs.configurations.uid_field_name, signature_id
                        )
                        self.edit_vector(
                            expression=expression, field_name='class_id',
                            value=value
                        )
                # set selected in table
                checked = item.checkState(0)
                if checked == 2:
                    self.signature_catalog.table.selected[
                        self.signature_catalog.table[
                            'signature_id'] == signature_id] = 1
                else:
                    self.signature_catalog.table.selected[
                        self.signature_catalog.table[
                            'signature_id'] == signature_id] = 0
                reload = True
        # info column
        elif column == 2:
            # signature item
            if signature_id is not False:
                # set class in table
                self.signature_catalog.table.class_name[
                    self.signature_catalog.table[
                        'signature_id'] == signature_id] = str(value)
            # macroclass item
            elif macroclass_id is not False:
                self.signature_catalog.macroclasses[
                    macroclass_id] = str(value)
        # type column
        elif column == 3:
            item.setData(column, '')
        # color column
        elif column == 4:
            item.setData(column, '')
            table.clearSelection()
        table.setSortingEnabled(True)
        table.blockSignals(False)
        if reload is True:
            self.roi_signature_table_tree()
        else:
            # info completer
            class_info = self.signature_catalog.table.class_name.tolist()
            class_info_completer(class_info)
            macroclass_info = self.signature_catalog.macroclasses.values()
            macroclass_info_completer(macroclass_info)

    # signature table double click
    def signature_tree_double_click(self, item, column):
        table = cfg.dock_class_dlg.ui.signature_list_treeWidget
        table.setSortingEnabled(False)
        table.blockSignals(True)
        reload = False
        # items
        try:
            signature_id = list(self.class_dock_tree.keys())[
                list(self.class_dock_tree.values()).index(item)]
            macroclass_id = False
        except Exception as err:
            str(err)
            macroclass_id = list(self.macroclass_dock_tree.keys())[
                list(self.macroclass_dock_tree.values()).index(item)]
            signature_id = False
        cfg.logger.log.debug(
            'signature_id: %s; macroclass_id: %s'
            % (str(signature_id), str(macroclass_id))
        )
        if column == 0 or column == 1 or column == 2 or column == 3:
            if macroclass_id is not False:
                item.setExpanded(not item.isExpanded())
            elif column == 2:
                expression = '"%s" = \'%s\' or ' % (
                    cfg.rs.configurations.uid_field_name, signature_id
                )
                expression = expression[:-4]
                cfg.logger.log.debug(
                    'zoom to expression: %s' % (str(expression))
                    )
                zoom_to_roi_polygons(expression)
        # color column
        elif column == 4:
            color = cfg.util_qt.select_color()
            if color is not None:
                # signature item
                if signature_id is not False:
                    for selected in table.selectedItems():
                        signature = selected.text(5)
                        # set color in table
                        self.signature_catalog.table.color[
                            self.signature_catalog.table[
                                'signature_id'] == signature] = str(
                            color.toRgb().name()
                        )
                # macroclass item
                elif macroclass_id is not False:
                    self.signature_catalog.macroclasses_color_string[
                        macroclass_id] = color.toRgb().name()
                reload = True
        table.setSortingEnabled(True)
        table.blockSignals(False)
        if reload is True:
            self.roi_signature_table_tree()

    # select all signatures
    def select_all_signatures(self, check=None, selected=None):
        # select all
        if check is True:
            self.all_items_set_state(1, selected)
        # unselect all
        else:
            self.all_items_set_state(0, selected)

    # set all items to state 0 or 2
    def all_items_set_state(self, value, only_selected=None):
        tree = cfg.dock_class_dlg.ui.signature_list_treeWidget
        if only_selected is False:
            # set same state for all
            self.signature_catalog.table.selected[
                self.signature_catalog.table[
                    'signature_id'] != '0'] = value
        else:
            for row in tree.selectedItems():
                # classes
                if len(row.text(1)) > 0:
                    signature = row.text(5)
                    # set selected
                    # noinspection PyUnresolvedReferences
                    self.signature_catalog.table.selected[
                        self.signature_catalog.table[
                            'signature_id'] == signature] = value
                # macroclasses
                else:
                    count = row.childCount()
                    for selected_row in range(0, count):
                        signature = row.child(selected_row).text(5)
                        # set selected
                        # noinspection PyUnresolvedReferences
                        self.signature_catalog.table.selected[
                            self.signature_catalog.table[
                                'signature_id'] == signature] = value
        self.roi_signature_table_tree()

    # change color
    def change_color(self, color):
        tree = cfg.dock_class_dlg.ui.signature_list_treeWidget
        if len(tree.selectedItems()) > 0:
            for item in tree.selectedItems():
                try:
                    signature_id = list(self.class_dock_tree.keys())[
                        list(self.class_dock_tree.values()).index(item)]
                    macroclass_id = False
                except Exception as err:
                    str(err)
                    macroclass_id = list(self.macroclass_dock_tree.keys())[
                        list(self.macroclass_dock_tree.values()).index(item)]
                    signature_id = False
                # set color in table
                # signature item
                if signature_id is not False:
                    # set color in table
                    self.signature_catalog.table.color[
                        self.signature_catalog.table[
                            'signature_id'] == signature_id] = str(
                        color.toRgb().name()
                    )
                # macroclass item
                elif macroclass_id is not False:
                    self.signature_catalog.macroclasses_color_string[
                        macroclass_id] = color.toRgb().name()
        self.roi_signature_table_tree()

    # add signature
    def add_spectral_signature_to_catalog(
            self, values, wavelengths, standard_deviations,
            macroclass_id=None, macroclass_name=None, class_id=None,
            class_name=None
    ):
        color_string = cfg.rs.shared_tools.random_color()
        unit = self.signature_catalog.bandset.get_wavelength_units()[0]
        if macroclass_id is None:
            macroclass_id = cfg.project_registry[cfg.reg_roi_macroclass_id]
        if macroclass_name is None:
            macroclass_name = cfg.project_registry[cfg.reg_roi_macroclass_name]
        if class_id is None:
            class_id = int(cfg.project_registry[cfg.reg_roi_class_id])
        if class_name is None:
            class_name = cfg.project_registry[cfg.reg_roi_class_name]
        value_list = []
        wavelength_list = []
        standard_deviation_list = []
        bandset_wavelength = self.signature_catalog.bandset.bands['wavelength']
        wavelength = numpy.array(wavelengths)
        for b in bandset_wavelength.tolist():
            arg_min = numpy.abs(wavelength - b).argmin()
            wavelength_list.append(b)
            value_list.append(values[arg_min])
            standard_deviation_list.append(standard_deviations[arg_min])
        self.signature_catalog.add_spectral_signature(
            value_list=value_list, macroclass_id=macroclass_id,
            class_id=class_id, macroclass_name=macroclass_name,
            class_name=class_name, wavelength_list=wavelength_list,
            standard_deviation_list=standard_deviation_list, geometry=0,
            signature=1, color_string=color_string, pixel_count=0,
            unit=unit
        )
        self.roi_signature_table_tree()

    # delete highlighted signatures
    def delete_selected_signatures(self):
        ids = self.get_highlighted_ids()
        for signature in ids:
            self.signature_catalog.remove_signature_by_id(
                signature_id=signature
            )

    # merge highlighted signatures
    def merge_selected_signatures(self):
        ids = self.get_highlighted_ids()
        random_color = cfg.rs.shared_tools.random_color()
        try:
            self.signature_catalog.merge_signatures_by_id(
                signature_id_list=ids, calculate_signature=True,
                macroclass_id=int(
                    cfg.project_registry[cfg.reg_roi_macroclass_id]
                ),
                class_id=int(cfg.project_registry[cfg.reg_roi_class_id]),
                macroclass_name=cfg.project_registry[
                    cfg.reg_roi_macroclass_name
                ],
                class_name=cfg.project_registry[cfg.reg_roi_class_name],
                color_string=random_color
            )
        except Exception as err:
            str(err)
            cfg.mx.msg_err_6()
            cfg.logger.log.error('signature ids: %s' % (str(ids)))

    # import spectral signature file
    def import_file(self, file_path):
        self.signature_catalog.import_file(file_path=file_path)
        self.roi_signature_table_tree()

    # import spectral signature file old version
    def import_scp_file(self, scp_file_path):
        with zipfile.ZipFile(scp_file_path) as open_file:
            for file_name in open_file.namelist():
                if file_name.endswith('.gpkg'):
                    unzip_file = open_file.open(file_name)
                    file_path = (
                        cfg.rs.configurations.temp.temporary_file_path(
                            name_suffix='.gpkg'
                        )
                    )
                    try:
                        unzip_temp_text = open(file_path, 'wb')
                        with unzip_file, unzip_temp_text:
                            shutil.copyfileobj(
                                unzip_file, unzip_temp_text
                            )
                        unzip_temp_text.close()
                    except Exception as err:
                        str(err)
                    break
        self.signature_catalog.import_vector(
            file_path=file_path,
            macroclass_field='MC_ID',
            macroclass_name_field='MC_name',
            class_field='C_ID', class_name_field='C_name',
            calculate_signature=True
        )
        self.roi_signature_table_tree()

    # import csv file to catalog
    def import_csv_file(self, file_path):
        random_color = cfg.rs.shared_tools.random_color()
        try:
            self.signature_catalog.import_spectral_signature_csv(
                csv_path=file_path,
                macroclass_id=int(
                    cfg.project_registry[cfg.reg_roi_macroclass_id]
                ),
                class_id=int(cfg.project_registry[cfg.reg_roi_class_id]),
                macroclass_name=cfg.project_registry[
                    cfg.reg_roi_macroclass_name],
                class_name=cfg.project_registry[cfg.reg_roi_class_name],
                color_string=random_color
            )
            self.roi_signature_table_tree()
        except Exception as err:
            str(err)
            cfg.mx.msg_err_6()
            cfg.logger.log.error('import_csv_file: %s' % (str(file_path)))

    # import vector file
    def import_vector(
            self, file_path, macroclass_field, macroclass_name_field,
            class_field, class_name_field, calculate_signature
    ):
        self.signature_catalog.import_vector(
            file_path=file_path, macroclass_field=macroclass_field,
            macroclass_name_field=macroclass_name_field,
            class_field=class_field, class_name_field=class_name_field,
            calculate_signature=calculate_signature
        )
        self.roi_signature_table_tree()

    # calculate signature of highlighted signatures
    def calculate_signature_of_selected_signatures(self):
        ids = self.get_highlighted_ids()
        for _id in ids:
            signature_array = self.signature_catalog.table[
                self.signature_catalog.table['signature_id'] == _id]
            geometry_check = signature_array.geometry[0]
            if geometry_check == 1:
                macroclass_id = signature_array.macroclass_id[0]
                class_id = signature_array.class_id[0]
                class_name = signature_array.class_name[0]
                color = signature_array.color[0]
                macroclass_name = self.signature_catalog.macroclasses[
                    macroclass_id
                ]
                try:
                    # calculate signature as merging one ROI
                    self.signature_catalog.merge_signatures_by_id(
                        signature_id_list=[_id], calculate_signature=True,
                        macroclass_id=macroclass_id, class_id=class_id,
                        macroclass_name=macroclass_name, class_name=class_name,
                        color_string=color
                    )
                    # remove original signature
                    self.signature_catalog.remove_signature_by_id(
                        signature_id=_id
                    )
                except Exception as err:
                    str(err)
                    cfg.mx.msg_err_6()
                    cfg.logger.log.error('signature id: %s' % (str(_id)))

    # get highlighted IDs
    def get_highlighted_ids(self, select_all=None, signatures=None):
        tree = cfg.dock_class_dlg.ui.signature_list_treeWidget
        if select_all is True:
            # get only signature
            if signatures is True:
                ids = self.signature_catalog.table.signature_id[
                    self.signature_catalog.table['signature'] == 1
                    ].tolist()
            else:
                ids = self.signature_catalog.table.signature_id.tolist()
        else:
            ids = []
            for row in tree.selectedItems():
                # classes
                if len(row.text(1)) > 0:
                    signature = row.text(5)
                    # set selected
                    # noinspection PyUnresolvedReferences
                    ids.append(
                        self.signature_catalog.table.signature_id[
                            self.signature_catalog.table[
                                'signature_id'] == signature][0]
                    )
                # macroclasses
                else:
                    count = row.childCount()
                    for selected_row in range(0, count):
                        signature = row.child(selected_row).text(5)
                        # set selected
                        # noinspection PyUnresolvedReferences
                        ids.append(
                            self.signature_catalog.table.signature_id[
                                self.signature_catalog.table[
                                    'signature_id'] == signature][0]
                        )
        cfg.logger.log.debug('get_highlighted_ids: %s' % (str(ids)))
        return ids

    # collapse menu
    def collapse(self):
        if self.collapse_tree is True:
            cfg.dock_class_dlg.ui.signature_list_treeWidget.collapseAll()
            self.collapse_tree = False
        else:
            cfg.dock_class_dlg.ui.signature_list_treeWidget.expandAll()
            self.collapse_tree = True

    # calculate unique class id to macroclass id
    def calculate_unique_c_id_mc_id(self):
        value_list = []
        for macroclass in self.signature_catalog.macroclasses:
            class_value = self.signature_catalog.table.class_id[
                self.signature_catalog.table['macroclass_id'] == macroclass][0]
            value_list.append([class_value, macroclass])
        return value_list


""" Interface functions """


# reset input
def reset_input():
    answer = cfg.util_qt.question_box(
        cfg.translate('Remove training input'),
        cfg.translate('Are you sure you want to remove training input?')
    )
    if answer is True:
        reset_input_dock()


# reset input
def reset_input_dock():
    cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(False)
    cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
    if cfg.scp_training is not None:
        cfg.scp_training.reset_signature_catalog()


# calculate signatures
def calculate_signatures():
    ids = cfg.scp_training.get_highlighted_ids(select_all=False)
    if len(ids) == 0:
        return 0
    answer = cfg.util_qt.question_box(
        cfg.translate('Calculate signatures'),
        cfg.translate('Calculate signatures for highlighted items?')
    )
    if answer is True:
        # save previous catalog file
        cfg.scp_training.save_temporary_signature_catalog()
        signature_catalog = cfg.scp_training.signature_catalog_copy()
        cfg.scp_training.set_signature_catalog(
            signature_catalog=signature_catalog
        )
        cfg.ui_utils.add_progress_bar()
        cfg.scp_training.calculate_signature_of_selected_signatures()
        cfg.ui_utils.remove_progress_bar(sound=False)
        cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(True)
        cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
        # create table tree
        cfg.scp_training.roi_signature_table_tree()
        # save training input
        if cfg.project_registry[cfg.reg_save_training_input_check] == 2:
            cfg.scp_training.save_signature_catalog()


# merge highlighted signatures
def merge_signatures():
    table = cfg.dock_class_dlg.ui.signature_list_treeWidget
    selected = table.selectedItems()
    if len(selected) > 0:
        answer = cfg.util_qt.question_box(
            cfg.translate('Merge signatures'),
            '%s MC ID: %s and C ID:%s?' % (
                cfg.translate('Merge highlighted signatures into'),
                cfg.project_registry[cfg.reg_roi_class_id],
                cfg.project_registry[cfg.reg_roi_macroclass_id],
            )
        )
        if answer is True:
            # save previous catalog file
            cfg.scp_training.save_temporary_signature_catalog()
            signature_catalog = cfg.scp_training.signature_catalog_copy()
            cfg.scp_training.set_signature_catalog(
                signature_catalog=signature_catalog
            )
            cfg.ui_utils.add_progress_bar()
            cfg.scp_training.merge_selected_signatures()
            cfg.ui_utils.remove_progress_bar(sound=False)
            cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(True)
            cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
            # create table tree
            cfg.scp_training.roi_signature_table_tree()
            # save training input
            if cfg.project_registry[cfg.reg_save_training_input_check] == 2:
                cfg.scp_training.save_signature_catalog()


# remove selected signatures
def remove_selected_signatures():
    table = cfg.dock_class_dlg.ui.signature_list_treeWidget
    selected = table.selectedItems()
    if len(selected) > 0:
        answer = cfg.util_qt.question_box(
            cfg.translate('Delete signatures'),
            cfg.translate(
                'Are you sure you want to delete highlighted ROIs '
                'and signatures?'
            )
        )
        if answer is True:
            # save previous catalog file
            cfg.scp_training.save_temporary_signature_catalog()
            signature_catalog = cfg.scp_training.signature_catalog_copy()
            cfg.scp_training.set_signature_catalog(
                signature_catalog=signature_catalog
            )
            cfg.scp_training.delete_selected_signatures()
            cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(True)
            cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
            # create table tree
            cfg.scp_training.roi_signature_table_tree()
            # save training input
            if cfg.project_registry[cfg.reg_save_training_input_check] == 2:
                cfg.scp_training.save_signature_catalog()


# zoom to clicked ROI
def zoom_to_roi_polygons(expression):
    if cfg.scp_training is not None:
        cfg.map_canvas.setRenderFlag(False)
        zoom_to_selected(cfg.scp_training.layer, expression)
        cfg.util_qgis.set_layer_visible(cfg.scp_training.layer, True)
        cfg.util_qgis.move_layer_to_top(cfg.scp_training.layer)
        cfg.map_canvas.setRenderFlag(True)


# Zoom to selected feature of layer
def zoom_to_selected(layer, expression):
    layer.removeSelection()
    layer.selectByExpression(expression)
    cfg.map_canvas.zoomToSelected(layer)
    layer.removeSelection()


# Activate signature calculation
def signature_checkbox():
    if cfg.dock_class_dlg.ui.signature_checkBox.isChecked() is True:
        cfg.project_registry[cfg.reg_signature_calculation_check] = 2
        cfg.dialog.ui.signature_checkBox2.blockSignals(True)
        cfg.dialog.ui.signature_checkBox2.setCheckState(2)
        cfg.dialog.ui.signature_checkBox2.blockSignals(False)
    else:
        cfg.project_registry[cfg.reg_signature_calculation_check] = 0
        cfg.dialog.ui.signature_checkBox2.blockSignals(True)
        cfg.dialog.ui.signature_checkBox2.setCheckState(0)
        cfg.dialog.ui.signature_checkBox2.blockSignals(False)


# properties menu
def properties_menu():
    add_signature_to_spectral_plot(1)


# collapse menu
def collapse_menu():
    cfg.scp_training.collapse()


# change macroclass menu
def change_macroclass_menu():
    dock_tree = cfg.dock_class_dlg.ui.signature_list_treeWidget
    if len(dock_tree.selectedItems()) > 0:
        answer = cfg.util_qt.question_box(
            cfg.translate('Change Macroclass ID'),
            cfg.translate(
                'Change the Macroclass ID for highlighted items to'
            )
            + ' %s ?' % str(cfg.project_registry[cfg.reg_roi_macroclass_id])
        )
        if answer is True:
            cfg.scp_training.edit_macroclass(
                cfg.project_registry[cfg.reg_roi_macroclass_id]
            )
            cfg.scp_training.roi_signature_table_tree()


# change color menu
def change_color_menu():
    color = cfg.util_qt.select_color()
    if color is not None:
        cfg.scp_training.change_color(color)


# clear selection menu
def clear_selection_menu():
    cfg.dock_class_dlg.ui.signature_list_treeWidget.clearSelection()


# zoom to menu
def zoom_to_menu():
    ids = cfg.scp_training.get_highlighted_ids(
        select_all=False, signatures=False
    )
    expression = ''
    for _id in ids:
        expression += '"%s" = \'%s\' or ' % (
            cfg.rs.configurations.uid_field_name, _id
        )
    expression = expression[:-4]
    cfg.logger.log.debug('zoom_to_menu expression: %s' % (str(expression)))
    zoom_to_roi_polygons(expression)


# select all menu
def select_all_menu():
    checked = None
    if len(
            cfg.dock_class_dlg.ui.signature_list_treeWidget.selectedItems()
    ) > 0:
        selected = True
        items = cfg.dock_class_dlg.ui.signature_list_treeWidget.selectedItems()
    else:
        selected = False
        items = []
        checked = cfg.scp_training.signature_catalog.table.selected[0]
    # get check value
    for i in items:
        # classes
        if len(i.text(1)) > 0:
            checked = i.checkState(0)
        # macroclasses
        else:
            count = i.childCount()
            for r in range(0, count):
                checked = i.child(r).checkState(0)
        break
    if checked == 2 or checked == 1:
        cfg.scp_training.select_all_signatures(
            check=False,
            selected=selected
        )
    elif checked == 0:
        cfg.scp_training.select_all_signatures(
            check=True,
            selected=selected
        )


# filter tree
def filter_tree():
    text = cfg.dock_class_dlg.ui.ROI_filter_lineEdit.text()
    tree = cfg.dock_class_dlg.ui.signature_list_treeWidget
    root = tree.invisibleRootItem()
    tree.blockSignals(True)
    if len(text) > 0:
        tree.expandAll()
        tree.findItems(text, cfg.util_qt.get_match_contains())
        for i in range(0, root.childCount()):
            child_x = root.child(i)
            child_x.setHidden(False)
            for child in range(0, child_x.childCount()):
                if text.lower() in child_x.child(child).text(2).lower():
                    child_x.child(child).setHidden(False)
                elif text.lower() in child_x.child(child).text(1).lower():
                    child_x.child(child).setHidden(False)
                elif text.lower() in child_x.child(child).text(0).lower():
                    child_x.child(child).setHidden(False)
                else:
                    child_x.child(child).setHidden(True)
    else:
        tree.expandAll()
        for i in range(0, root.childCount()):
            child_x = root.child(i)
            child_x.setHidden(False)
            for child in range(0, child_x.childCount()):
                if text in child_x.child(child).text(0):
                    child_x.child(child).setHidden(False)
    tree.blockSignals(False)


""" Context menu """


# add item to menu
def add_menu_item(menu, function, icon_name, name, tooltip=''):
    try:
        action = QAction(
            QIcon(
                ':/plugins/semiautomaticclassificationplugin/icons/%s'
                % icon_name
            ), name, cfg.iface.mainWindow()
        )
    except Exception as err:
        str(err)
        action = QAction(name, cfg.iface.mainWindow())
    action.setObjectName('action')
    action.setToolTip(tooltip)
    action.triggered.connect(function)
    menu.addAction(action)
    return action


# menu
def context_menu(event):
    menu = QMenu()
    menu.setToolTipsVisible(True)
    add_menu_item(
        menu, zoom_to_menu,
        'semiautomaticclassificationplugin_zoom_to_ROI.svg',
        cfg.translate('Zoom to')
    )
    add_menu_item(
        menu, select_all_menu,
        'semiautomaticclassificationplugin_options.svg',
        cfg.translate('Check/uncheck')
    )
    add_menu_item(
        menu, clear_selection_menu,
        'semiautomaticclassificationplugin_select_all.svg',
        cfg.translate('Clear selection')
    )
    add_menu_item(
        menu, collapse_menu, 'semiautomaticclassificationplugin_docks.svg',
        cfg.translate('Collapse/expand all')
    )
    menu.addSeparator()
    add_menu_item(
        menu, change_macroclass_menu,
        'semiautomaticclassificationplugin_enter.svg',
        cfg.translate('Change MC ID')
    )
    add_menu_item(
        menu, change_color_menu, 'semiautomaticclassificationplugin_enter.svg',
        cfg.translate('Change color')
    )
    menu.addSeparator()
    add_menu_item(
        menu, merge_signatures,
        'semiautomaticclassificationplugin_merge_sign_tool.svg',
        cfg.translate('Merge items')
    )
    add_menu_item(
        menu, calculate_signatures,
        'semiautomaticclassificationplugin_add_sign_tool.svg',
        cfg.translate('Calculate signatures')
    )
    add_menu_item(
        menu, remove_selected_signatures,
        'semiautomaticclassificationplugin_remove.svg',
        cfg.translate('Delete items')
    )
    menu.addSeparator()
    add_menu_item(
        menu, add_signature_to_spectral_plot,
        'semiautomaticclassificationplugin_sign_tool.svg',
        cfg.translate('Add to spectral plot')
    )
    add_menu_item(
        menu, add_roi_to_scatter_plot,
        'semiautomaticclassificationplugin_scatter_tool.svg',
        cfg.translate('Add to scatter plot')
    )
    add_menu_item(
        menu, properties_menu,
        'semiautomaticclassificationplugin_accuracy_tool.svg',
        cfg.translate('Properties')
    )
    menu.addSeparator()
    add_menu_item(
        menu, cfg.input_interface.import_signatures_tab,
        'semiautomaticclassificationplugin_import_spectral_library.svg',
        cfg.translate('Import')
    )
    add_menu_item(
        menu, cfg.input_interface.export_signatures_tab,
        'semiautomaticclassificationplugin_export_spectral_library.svg',
        cfg.translate('Export')
    )
    menu.exec_(
        cfg.dock_class_dlg.ui.signature_list_treeWidget.mapToGlobal(event)
    )


""" Toolbar functions """


# create a ROI in the same point
def redo_roi():
    if cfg.last_roi_point is not None:
        roi = create_region_growing_roi(cfg.last_roi_point)
        if roi is False:
            cfg.redo_ROI_Button.setEnabled(False)


# show hide ROI radio button
def show_hide_roi():
    try:
        if cfg.show_ROI_radioButton.isChecked():
            # training layer
            if cfg.scp_training is not None:
                cfg.util_qgis.set_layer_visible(cfg.scp_training.layer, True)
                cfg.util_qgis.move_layer_to_top(cfg.scp_training.layer)
            # rubber roi polygon
            if cfg.scp_dock_rubber_roi is not None:
                cfg.scp_dock_rubber_roi.show()
            # roi polygon
            if cfg.roi_map_polygon is not None:
                cfg.roi_map_polygon.show()
            # roi center
            if cfg.roi_center_vertex is not None:
                cfg.roi_center_vertex.show()
        else:
            # training layer
            if cfg.scp_training is not None:
                cfg.util_qgis.set_layer_visible(cfg.scp_training.layer, False)
            # rubber roi polygon
            if cfg.scp_dock_rubber_roi is not None:
                cfg.scp_dock_rubber_roi.hide()
            # roi polygon
            if cfg.roi_map_polygon is not None:
                cfg.roi_map_polygon.hide()
            # roi center
            if cfg.roi_center_vertex is not None:
                cfg.roi_center_vertex.hide()
        cfg.map_canvas.refresh()
    except Exception as err:
        str(err)


# pointer moved
def moved_pointer(point):
    calculate_pixel_expression(point)


# calculate pixel expression
def calculate_pixel_expression(point):
    cursor = QCursor(QPixmap(':/pointer/icons/pointer/ROI_pointer.svg'))
    if cfg.project_registry[cfg.reg_index_calculation_check] == 2:
        point = cfg.utils.check_point_in_image(point=point)
        if point is not False and point is not None:
            bandset_x = cfg.bandset_catalog.get(
                cfg.project_registry[cfg.reg_active_bandset_number]
            )
            if (cfg.dock_class_dlg.ui.vegetation_index_comboBox.currentText()
                    == 'NDVI'):
                expression = cfg.rs.configurations.variable_ndvi_expression
            elif (cfg.dock_class_dlg.ui.vegetation_index_comboBox.currentText()
                  == 'EVI'):
                expression = cfg.rs.configurations.variable_evi_expression
            else:
                expression = cfg.project_registry[
                    cfg.reg_roi_custom_expression
                ]
            cfg.logger.log.debug(
                'calculate_pixel_expression: %s' % str(expression)
            )
            if len(expression) > 0:
                bandset_x.calc(
                    expression_string=expression,
                    point_coordinates=[point.x(), point.y()]
                )
                cfg.rs.configurations.multiprocess.multiprocess_pixel_value()
                value = cfg.rs.configurations.multiprocess.output
                cfg.rs.configurations.multiprocess.output = False
                if value is not False:
                    cursor = cursor_creation(value)
    cfg.map_canvas.setCursor(cursor)


def cursor_creation(value):
    num = str(value)[0:6]
    pmap = QPixmap(
        ["48 48 3 1",
         "      c None",
         ".     c #ffffff",
         "+     c #000000",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "................................................",
         "                                                ",
         "                      ++++                      ",
         "                      +..+                      ",
         "                      +..+                      ",
         "                      +..+                      ",
         "                      +..+                      ",
         "                +++++++..+++++++                ",
         "                +..............+                ",
         "                +..............+                ",
         "                +++++++..+++++++                ",
         "                      +..+                      ",
         "                      +..+                      ",
         "                      +..+                      ",
         "                      +..+                      ",
         "                      ++++                      ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         "                                                ",
         ]
    )
    painter = QPainter()
    painter.begin(pmap)
    painter.setPen(QColor(0, 0, 0))
    painter.setFont(QFont('Monospace', 9))
    painter.drawText(QPoint(2, 12), num)
    painter.end()
    return QCursor(pmap)


# set custom expression
# noinspection PyProtectedMember
def custom_expression_edited():
    custom_expression = str(cfg.dock_class_dlg.ui.custom_index_lineEdit.text())
    # check expression
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    bandset_x = cfg.bandset_catalog.get(bandset_number)
    # create list of band names from band sets
    raster_variables = band_calc._bandset_names_alias(bandset=bandset_x)
    (exp_list, all_out_name_list,
     output_message) = band_calc._check_expression_bandset(
        custom_expression, raster_variables, bandset_x
    )
    if output_message is not None:
        cfg.project_registry[cfg.reg_roi_custom_expression] = ''
        cfg.dock_class_dlg.ui.custom_index_lineEdit.setStyleSheet(
            'color : red'
        )
    else:
        cfg.project_registry[cfg.reg_roi_custom_expression] = str(
            custom_expression
        )
        cfg.dock_class_dlg.ui.custom_index_lineEdit.setStyleSheet(
            'color : green'
        )


# Activate pointer for ROI creation
def pointer_manual_roi_active():
    cfg.roi_points = []
    cfg.qgis_vertex_item_list = []
    cfg.map_canvas.setMapTool(cfg.manual_roi_pointer)
    cursor = QCursor()
    cursor.setShape(Qt.CrossCursor)
    cfg.map_canvas.setCursor(cursor)


# Activate pointer for ROI creation
def pointer_region_growing_roi_active():
    cfg.map_canvas.setMapTool(cfg.region_growing_pointer)
    cursor = QCursor(QPixmap(':/pointer/icons/pointer/ROI_pointer.svg'))
    cfg.map_canvas.setCursor(cursor)


# set min ROI size
def roi_min_size():
    cfg.project_registry[cfg.reg_roi_min_size] = int(
        cfg.roi_min_size_spin.value()
    )
    # auto refresh ROI
    if cfg.roi_time is None:
        cfg.roi_time = datetime.now() - timedelta(seconds=2)
    if cfg.dock_class_dlg.ui.auto_refresh_ROI_checkBox.isChecked():
        if datetime.now() > (
                cfg.roi_time + timedelta(seconds=1)):
            cfg.roi_time = datetime.now()
            redo_roi()


# set Range radius
def range_radius():
    cfg.project_registry[cfg.reg_roi_range_radius] = float(
        cfg.Range_radius_spin.value()
    )
    # auto refresh ROI
    if cfg.roi_time is None:
        cfg.roi_time = datetime.now() - timedelta(seconds=2)
    if cfg.dock_class_dlg.ui.auto_refresh_ROI_checkBox.isChecked():
        if datetime.now() > (
                cfg.roi_time + timedelta(seconds=1)):
            cfg.roi_time = datetime.now()
            redo_roi()


# set Max ROI size
def max_roi_width():
    cfg.project_registry[cfg.reg_roi_max_width] = int(
        cfg.max_roi_width_spin.value()
    )
    # auto refresh ROI
    if cfg.roi_time is None:
        cfg.roi_time = datetime.now() - timedelta(seconds=2)
    if cfg.dock_class_dlg.ui.auto_refresh_ROI_checkBox.isChecked():
        if datetime.now() > (
                cfg.roi_time + timedelta(seconds=1)):
            cfg.roi_time = datetime.now()
            redo_roi()


# set rapid ROI band
def rapid_roi_band():
    cfg.project_registry[cfg.reg_roi_main_band] = (
        cfg.dock_class_dlg.ui.rapidROI_band_spinBox.value()
    )
    # auto refresh ROI
    if cfg.dock_class_dlg.ui.auto_refresh_ROI_checkBox.isChecked():
        if datetime.now() > (
                cfg.roi_time + timedelta(seconds=1)):
            cfg.roi_time = datetime.now()
            redo_roi()


# Activate rapid ROI creation
def rapid_roi_checkbox():
    if cfg.dock_class_dlg.ui.rapid_ROI_checkBox.isChecked() is True:
        cfg.project_registry[cfg.reg_rapid_roi_check] = 2
    else:
        cfg.project_registry[cfg.reg_rapid_roi_check] = 0
    # auto refresh ROI
    if cfg.dock_class_dlg.ui.auto_refresh_ROI_checkBox.isChecked():
        if datetime.now() > (
                cfg.roi_time + timedelta(seconds=1)):
            cfg.roi_time = datetime.now()
            redo_roi()


# Activate vegetation index checkbox
def vegetation_index_checkbox():
    if cfg.dock_class_dlg.ui.display_cursor_checkBox.isChecked() is True:
        cfg.project_registry[cfg.reg_index_calculation_check] = 2
    else:
        cfg.project_registry[cfg.reg_index_calculation_check] = 0


# ROI macroclass ID
def roi_macroclass_id_value():
    value = cfg.dock_class_dlg.ui.ROI_Macroclass_ID_spin.value()
    cfg.project_registry[cfg.reg_roi_macroclass_id] = value
    # set macroclass name if existing
    if cfg.scp_training is not None:
        if value in cfg.scp_training.signature_catalog.macroclasses:
            macroclass = cfg.scp_training.signature_catalog.macroclasses[value]
            cfg.dock_class_dlg.ui.ROI_Macroclass_line.setText(macroclass)
            cfg.project_registry[cfg.reg_roi_macroclass_name] = macroclass


def roi_macroclass_name_info():
    cfg.project_registry[cfg.reg_roi_macroclass_name] = str(
        cfg.dock_class_dlg.ui.ROI_Macroclass_line.text()
    )


# set ROI class ID
def roi_class_id_value():
    cfg.project_registry[
        cfg.reg_roi_class_id] = cfg.dock_class_dlg.ui.ROI_ID_spin.value()


# set ROI class info
def roi_class_name_info():
    cfg.project_registry[cfg.reg_roi_class_name] = str(
        cfg.dock_class_dlg.ui.ROI_Class_line.text()
    )


# class info completer
def class_info_completer(class_info_list):
    try:
        # class names
        completer_class_name = QCompleter(class_info_list)
        cfg.dock_class_dlg.ui.ROI_Class_line.setCompleter(
            completer_class_name
        )
    except Exception as err:
        str(err)


# macroclass info completer
def macroclass_info_completer(macroclass_list):
    # class names
    completer_macroclass_name = QCompleter(macroclass_list)
    cfg.dock_class_dlg.ui.ROI_Macroclass_line.setCompleter(
        completer_macroclass_name
    )


# Activate save input file
def save_input_checkbox():
    if cfg.dock_class_dlg.ui.save_input_checkBox.isChecked() is True:
        cfg.project_registry[cfg.reg_save_training_input_check] = 2
    else:
        cfg.project_registry[cfg.reg_save_training_input_check] = 0


# max buffer checkbox
def max_buffer():
    value = cfg.dock_class_dlg.ui.max_buffer_spinBox.value()
    cfg.qgis_registry[cfg.max_train_buffer_default] = value
    if cfg.scp_training is not None:
        cfg.scp_training.set_max_size_buffer(value)


""" Map functions """


# add roi polygon
def add_roi_polygon_to_map(source_layer, feature_id):
    color = QColor(cfg.qgis_registry[cfg.reg_roi_color])
    try:
        value = 255 - int(
            int(cfg.qgis_registry[cfg.reg_roi_transparency]) * 255 / 100
        )
        color.setAlpha(value)
    except Exception as err:
        str(err)
        color.setAlpha(100)
    feature = cfg.util_qgis.get_feature_by_id(source_layer, feature_id)
    cfg.roi_map_polygon = QgsHighlight(
        cfg.map_canvas, feature.geometry(), source_layer
    )
    cfg.roi_map_polygon.setWidth(2)
    cfg.roi_map_polygon.setColor(QColor('#53d4e7'))
    try:
        cfg.roi_map_polygon.setFillColor(color)
    except Exception as err:
        str(err)
    cfg.map_canvas.refresh()
    cfg.roi_map_polygon.show()
    cfg.show_ROI_radioButton.setChecked(True)
    cfg.ctrl_click = None


# clear scp dock rubber
def clear_scp_dock_rubber():
    for point in cfg.roi_points:
        try:
            cfg.map_canvas.scene().removeItem(point)
        except Exception as err:
            str(err)
    cfg.roi_points = []
    cfg.scp_dock_rubber_roi.hide()
    cfg.scp_dock_rubber_roi.reset()
    if cfg.roi_map_polygon is not None:
        cfg.roi_map_polygon.hide()
    if cfg.roi_map_polygon is not None:
        cfg.map_canvas.scene().removeItem(cfg.roi_map_polygon)
        cfg.roi_map_polygon = None
    for point in cfg.qgis_vertex_item_list:
        cfg.map_canvas.scene().removeItem(point)
        del point
    if cfg.roi_center_vertex is not None:
        cfg.roi_center_vertex.hide()
    cfg.qgis_vertex_item_list = []
    cfg.map_canvas.refresh()


""" Training input functions """


# Save last ROI to training
def save_roi_to_training(bandset_number=None):
    # bandset_number is False when triggered by action
    if bandset_number is None or bandset_number is False:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    if cfg.scp_training is None or cfg.scp_training.signature_catalog is None:
        cfg.mx.msg_war_5()
        return False
    elif cfg.temporary_roi is None:
        cfg.mx.msg_war_4()
    else:
        cfg.ui_utils.add_progress_bar()
        # get vector from ROI
        roi_path = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix='.gpkg'
        )
        cfg.util_qgis.save_memory_layer_to_geopackage(
            cfg.temporary_roi, roi_path
        )
        # calculate signature
        if cfg.project_registry[cfg.reg_signature_calculation_check] == 2:
            calculate_signature = True
        else:
            calculate_signature = False
        cfg.logger.log.debug(
            'bandset number: %s; bandset catalog: %s; '
            'bandset count: %s; bandset: %s'
            % (str(bandset_number), str(cfg.bandset_catalog),
               str(cfg.bandset_catalog.get_bandset_count()),
               str(cfg.bandset_catalog.get(bandset_number))
               )
        )
        # save previous catalog file
        cfg.scp_training.save_temporary_signature_catalog()
        signature_catalog = cfg.scp_training.signature_catalog_copy()
        # save roi to new catalog
        signature_catalog.import_vector(
            file_path=roi_path, macroclass_value=int(
                cfg.project_registry[cfg.reg_roi_macroclass_id]
            ),
            class_value=int(cfg.project_registry[cfg.reg_roi_class_id]),
            macroclass_name=cfg.project_registry[cfg.reg_roi_macroclass_name],
            class_name=cfg.project_registry[cfg.reg_roi_class_name],
            calculate_signature=calculate_signature
        )
        if cfg.rs.configurations.action:
            cfg.scp_training.set_signature_catalog(
                signature_catalog=signature_catalog
            )
            clear_scp_dock_rubber()
            cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(True)
            cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
            # increase C_ID
            cfg.dock_class_dlg.ui.ROI_ID_spin.setValue(
                int(cfg.project_registry[cfg.reg_roi_class_id]) + 1
            )
            # create table tree
            cfg.scp_training.roi_signature_table_tree()
            # save training input
            if cfg.project_registry[cfg.reg_save_training_input_check] == 2:
                cfg.scp_training.save_signature_catalog()
        cfg.ui_utils.remove_progress_bar(sound=False)


# undo training modifications
def undo_saved_roi():
    answer = cfg.util_qt.question_box(
        cfg.translate('Undo save ROI'), cfg.translate(
            'Are you sure you want to undo?'
        )
    )
    if answer is True:
        cfg.logger.log.debug('undo')
        # training input undo
        cfg.scp_training.undo()
        # save training input
        if cfg.project_registry[cfg.reg_save_training_input_check] == 2:
            cfg.scp_training.save_signature_catalog()


# restore training buffered
def redo_saved_roi():
    answer = cfg.util_qt.question_box(
        cfg.translate('Redo save ROI'), cfg.translate(
            'Are you sure you want to redo?'
        )
    )
    if answer is True:
        cfg.logger.log.debug('redo')
        # training input redo
        cfg.scp_training.redo()
        # save training input
        if cfg.project_registry[cfg.reg_save_training_input_check] == 2:
            cfg.scp_training.save_signature_catalog()


# left click
def left_click_manual(point):
    qgis_crs = cfg.util_qgis.get_qgis_crs()
    point = cfg.utils.check_point_in_image(point=point, output_crs=qgis_crs)
    if point is False:
        cfg.mx.msg_war_3()
        return False
    time = cfg.utils.get_time()
    name = '%s%s' % (cfg.temp_roi_name, time)
    # crs
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    bandset_x = cfg.bandset_catalog.get(bandset_number)
    band_count = bandset_x.get_band_count()
    if band_count == 0:
        return False
    memory_layer = cfg.util_qgis.add_vector_layer(
        'MultiPolygon?crs=%s' % qgis_crs.toWkt(), name, 'memory'
    )
    memory_layer.setCrs(qgis_crs)
    cfg.roi_points.append(point)
    # rubber band polygon to store vertices
    cfg.scp_dock_rubber_roi.addPoint(point)
    geometry = cfg.scp_dock_rubber_roi.asGeometry()
    vertex = QgsVertexMarker(cfg.map_canvas)
    vertex.setCenter(point)
    cfg.qgis_vertex_item_list.append(vertex)
    cfg.scp_dock_rubber_roi.setToGeometry(geometry, qgis_crs)
    cfg.scp_dock_rubber_roi.show()


# right click
def right_click_manual(point):
    qgis_crs = cfg.util_qgis.get_qgis_crs()
    left_click_manual(point)
    feature = QgsFeature()
    time = cfg.utils.get_time()
    name = '%s%s' % (cfg.temp_roi_name, time)
    # crs
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    bandset_x = cfg.bandset_catalog.get(bandset_number)
    band_count = bandset_x.get_band_count()
    if band_count == 0:
        return False
    memory_layer = cfg.util_qgis.add_vector_layer(
        'MultiPolygon?crs=%s' % qgis_crs.toWkt(), name, 'memory'
    )
    memory_layer.setCrs(qgis_crs)
    if not len(cfg.roi_points) >= 3:
        cfg.mx.msg_inf_2()
        clear_scp_dock_rubber()
        return
    q_point = QPointF()
    f_polygon = QPolygonF()
    for v in cfg.roi_points:
        q_point.setX(v.x())
        q_point.setY(v.y())
        f_polygon.append(q_point)
    q_point.setX(cfg.roi_points[0].x())
    q_point.setY(cfg.roi_points[0].y())
    f_polygon.append(q_point)
    q_geometry = QgsGeometry().fromQPolygonF(f_polygon)
    memory_layer.addTopologicalPoints(q_geometry)
    data_provider = memory_layer.dataProvider()
    # create temp ROI
    memory_layer.startEditing()
    # add fields
    data_provider.addAttributes(
        [QgsField(cfg.empty_field_name, QVariant.Int)]
    )
    # add a feature
    if cfg.ctrl_click is not None:
        q_geometry = add_part_to_roi(q_geometry)
    feature.setGeometry(q_geometry)
    feature.setAttributes([1])
    data_provider.addFeatures([feature])
    memory_layer.commitChanges()
    memory_layer.updateExtents()
    cfg.temporary_roi = memory_layer
    clear_scp_dock_rubber()
    add_roi_polygon_to_map(cfg.temporary_roi, 1)
    # calculate temporary spectral signature
    if cfg.dock_class_dlg.ui.auto_calculate_ROI_signature_checkBox.isChecked():
        temporary_roi_spectral_signature()
    cfg.dock_class_dlg.ui.button_Save_ROI.setEnabled(True)


# add multipart ROI
def add_part_to_roi(part):
    if cfg.temporary_roi is not None and cfg.ctrl_click is True:
        features = cfg.temporary_roi.getFeatures()
        feature = QgsFeature()
        features.nextFeature(feature)
        geometry = QgsGeometry(feature.geometry())
        geometry.convertToMultiType()
        part.convertToMultiType()
        geometry.addPartGeometry(part)
        cfg.second_temporary_roi = cfg.temporary_roi
        return geometry
    else:
        return part


def delete_last_roi():
    cfg.temporary_roi = cfg.second_temporary_roi
    try:
        add_roi_polygon_to_map(cfg.temporary_roi, 1)
    except Exception as err:
        str(err)


# left click
def left_click_region_growing(point):
    point = cfg.utils.check_point_in_image(point=point)
    cfg.last_roi_point = point
    if point is False:
        cfg.mx.msg_war_3()
        return False
    create_region_growing_roi(point)


# left click
def right_click_region_growing(point):
    point = cfg.utils.check_point_in_image(point=point)
    if point is False:
        cfg.mx.msg_war_3()
        return False
    calculate_pixel_signature(point)


# right click to calculate point (pixel) signature
# noinspection PyArgumentList
def calculate_pixel_signature(point, bandset_number=None):
    if point is not None:
        if bandset_number is None:
            bandset_number = cfg.project_registry[
                cfg.reg_active_bandset_number]
    cfg.rs.configurations.action = True
    cfg.ui_utils.add_progress_bar()
    try:
        # region growing to get pixel
        roi_path = cfg.rs.shared_tools.region_growing_polygon(
            coordinate_x=point.x(), coordinate_y=point.y(),
            input_bands=bandset_number,
            max_width=1, max_spectral_distance=1000000,
            minimum_size=1, bandset_catalog=cfg.bandset_catalog
        )
    except Exception as err:
        cfg.logger.log.error(str(err))
        cfg.mx.msg_err_6()
        cfg.ui_utils.remove_progress_bar(sound=False)
        return False
    bandset = cfg.bandset_catalog.get(bandset_number)
    if bandset is None:
        return False
    else:
        band_list = bandset.get_absolute_paths()
    temp_bandset = deepcopy(bandset)
    bands = temp_bandset.bands
    # create virtual raster of input
    vrt_check = raster_vector.create_temporary_virtual_raster(band_list)
    if bands is not None:
        for band in bands:
            if cfg.rs.configurations.action is False:
                break
            path = raster_vector.create_temporary_virtual_raster(
                [vrt_check], band_number_list=[[int(band['band_number'])]]
            )

            band['path'] = path
    temp_bandset.root_directory = None
    signature_catalog = cfg.rs.spectral_signatures_catalog(
        bandset=temp_bandset
    )
    (value_list, standard_deviation_list, wavelength_list,
     pixel_count) = signature_catalog.calculate_signature(roi_path)
    cfg.ui_utils.remove_progress_bar(sound=False)
    plot_catalog = cfg.spectral_signature_plotter.plot_catalog
    signature_id = generate_signature_id()
    color_string = cfg.rs.shared_tools.random_color()
    vector_plot = SpectralSignaturePlot(
        value=value_list, wavelength=wavelength_list, pixel_count=pixel_count,
        standard_deviation=standard_deviation_list, signature_id=signature_id,
        macroclass_name=cfg.temp_roi_name,
        class_name='point (X=%s; Y=%s)' % (str(point.x()), str(point.y())),
        color_string=color_string, selected=1
    )
    plot_catalog.catalog[signature_id] = vector_plot
    cfg.spectral_signature_plotter.signature_list_plot_table()
    cfg.input_interface.spectral_plot_tab()


# create a region growing ROI
# noinspection PyArgumentList
def create_region_growing_roi(point, bandset_number=None):
    if point is not None:
        cfg.rs.configurations.action = True
        if bandset_number is None:
            bandset_number = cfg.project_registry[
                cfg.reg_active_bandset_number]
        # bands
        if cfg.project_registry[cfg.reg_rapid_roi_check] == 2:
            bands = int(cfg.project_registry[cfg.reg_roi_main_band])
        else:
            bands = None
        cfg.ui_utils.add_progress_bar()
        # region growing
        try:
            region_path = cfg.rs.shared_tools.region_growing_polygon(
                coordinate_x=point.x(), coordinate_y=point.y(),
                input_bands=bandset_number, band_number=bands,
                max_width=int(cfg.project_registry[cfg.reg_roi_max_width]),
                max_spectral_distance=float(
                    cfg.project_registry[cfg.reg_roi_range_radius]
                ),
                minimum_size=int(cfg.project_registry[cfg.reg_roi_min_size]),
                bandset_catalog=cfg.bandset_catalog
            )
        except Exception as err:
            cfg.logger.log.error(str(err))
            cfg.mx.msg_err_6()
            cfg.ui_utils.remove_progress_bar(sound=False)
            return False
        # create memory temp ROI
        region_crs = cfg.util_gdal.get_crs_gdal(region_path)
        d_t = cfg.utils.get_time()
        temp_name = cfg.temp_roi_name + d_t
        memory_layer = cfg.util_qgis.add_vector_layer(
            'MultiPolygon?crs=%s' % str(region_crs), temp_name, 'memory'
        )
        crs = cfg.util_qgis.create_qgis_reference_system_from_wkt(region_crs)
        memory_layer.setCrs(crs)
        memory_layer.startEditing()
        # add fields
        provider = memory_layer.dataProvider()
        provider.addAttributes(
            [QgsField(cfg.empty_field_name, QVariant.Int)]
        )
        roi_layer = cfg.util_qgis.add_vector_layer(region_path)
        # add a feature
        feature_id = cfg.util_qgis.get_last_feature_id(roi_layer)
        feature_x = cfg.util_qgis.get_feature_by_id(roi_layer, feature_id)
        # get geometry
        geometry = feature_x.geometry()
        # add a feature
        if cfg.ctrl_click is not None:
            geometry = add_part_to_roi(geometry)
        else:
            cfg.second_temporary_roi = cfg.temporary_roi
        copied_feature = QgsFeature()
        copied_feature.setGeometry(geometry)
        copied_feature.setAttributes([1])
        provider.addFeatures([copied_feature])
        memory_layer.commitChanges()
        memory_layer.updateExtents()
        # add ROI layer
        clear_scp_dock_rubber()
        cfg.temporary_roi = memory_layer
        add_roi_polygon_to_map(cfg.temporary_roi, 1)
        cfg.roi_center_vertex = QgsVertexMarker(cfg.map_canvas)
        cfg.roi_center_vertex.setCenter(point)
        cfg.roi_center_vertex.setIconType(1)
        cfg.roi_center_vertex.setColor(QColor(0, 255, 255))
        cfg.roi_center_vertex.setIconSize(12)
        cfg.roi_points.append(cfg.roi_center_vertex)
        # calculate temporary spectral signature
        button = cfg.dock_class_dlg.ui.auto_calculate_ROI_signature_checkBox
        if button.isChecked():
            temporary_roi_spectral_signature(bandset_number=bandset_number)
        cfg.dock_class_dlg.ui.button_Save_ROI.setEnabled(True)
        cfg.redo_ROI_Button.setEnabled(True)
        cfg.ui_utils.remove_progress_bar(sound=False)


# calculate temporary ROI spectral signature
def temporary_roi_spectral_signature(bandset_number=None, roi_path=None):
    cfg.rs.configurations.action = True
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    # get ROI polygons
    if roi_path is None:
        # get vector from ROI
        roi_path = cfg.rs.configurations.temp.temporary_file_path(
            name_suffix='.gpkg'
        )
        cfg.util_qgis.save_memory_layer_to_geopackage(
            cfg.temporary_roi, roi_path
        )
    signature_catalog = cfg.rs.spectral_signatures_catalog(
        bandset=cfg.bandset_catalog.get(bandset_number)
    )
    cfg.ui_utils.add_progress_bar()
    # add signature to plot
    (value_list, standard_deviation_list, wavelength_list,
     pixel_count) = signature_catalog.calculate_signature(roi_path)
    cfg.ui_utils.remove_progress_bar(sound=False)
    plot_catalog = cfg.spectral_signature_plotter.plot_catalog
    signature_id = generate_signature_id()
    color_string = cfg.rs.shared_tools.random_color()
    vector_plot = SpectralSignaturePlot(
        value=value_list, wavelength=wavelength_list, pixel_count=pixel_count,
        standard_deviation=standard_deviation_list, signature_id=signature_id,
        macroclass_name=cfg.temp_roi_name, class_name=cfg.temp_roi_name,
        color_string=color_string, selected=1
    )
    plot_catalog.catalog[signature_id] = vector_plot
    cfg.spectral_signature_plotter.signature_list_plot_table()
    cfg.input_interface.spectral_plot_tab()


""" Training input """


# Create new input
def create_training_input():
    output_path = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Create training input'), '', '*.scpx', 'scpx'
    )
    if output_path is not False:
        if output_path.lower().endswith('.scpx'):
            pass
        elif not output_path.lower().endswith('.scpx'):
            output_path += '.scpx'
        reset_input_dock()
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
        cfg.project_registry[cfg.reg_training_bandset_number] = bandset_number
        cfg.dock_class_dlg.ui.label_48.setText(
            cfg.translate(' ROI & Signature list') + ' ('
            + cfg.translate('band set') + ' ' + str(bandset_number) + ')'
        )
        bandset_x = cfg.bandset_catalog.get(bandset_number)
        band_count = bandset_x.get_band_count()
        cfg.logger.log.debug('bandset band count: %s' % (str(band_count)))
        if band_count == 0:
            cfg.mx.msg_war_6(bandset_number)
            return
        signature_catalog = cfg.rs.spectral_signatures_catalog(
            bandset=cfg.bandset_catalog.get(bandset_number)
        )
        # load vector in QGIS
        cfg.scp_training = TrainingVectorLayer(
            signature_catalog=signature_catalog, output_path=output_path
        )
        cfg.scp_training.save_signature_catalog()
        # connect signature threshold table
        cfg.signature_threshold.signature_thresholds_to_table()


# import training file
def import_library_file(path=None):
    if path is None or path is False:
        file_path = cfg.util_qt.get_open_file(
            None, cfg.translate('Select a training input'), '',
            'Signature catalog package (*.scpx);; '
            'Signature catalog package old version (*.scp);;'
            'USGS library (*.zip);;ASTER library (*.txt);;CSV file (*.csv)'
        )
    else:
        file_path = path
    if len(file_path) > 0:
        cfg.ui_utils.add_progress_bar()
        # save previous catalog file
        cfg.scp_training.save_temporary_signature_catalog()
        signature_catalog = cfg.scp_training.signature_catalog_copy()
        cfg.scp_training.set_signature_catalog(
            signature_catalog=signature_catalog
        )
        if file_path.endswith('.scpx'):
            cfg.scp_training.import_file(file_path)
        elif file_path.endswith('.scp'):
            cfg.scp_training.import_scp_file(file_path)
        elif file_path.endswith('.zip'):
            cfg.signature_importer.import_usgs_library(file_path)
        elif file_path.endswith('.csv'):
            cfg.scp_training.import_csv_file(file_path)
        elif file_path.endswith('.txt'):
            cfg.signature_importer.aster_library(file_path)
        cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(True)
        cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
        cfg.ui_utils.remove_progress_bar()


# open training file
def open_training_input_file(path=None):
    if path is None or path is False:
        file_path = cfg.util_qt.get_open_file(
            None, cfg.translate('Select a training input'), '',
            'Signature catalog package (*.scpx)'
        )
    else:
        file_path = path
    if len(file_path) > 0:
        open_signature_catalog_file(file_path)


# open signature file
def open_signature_catalog_file(file_path=None, bandset_number=None):
    cfg.logger.log.info('open_signature_catalog_file: %s' % (str(file_path)))
    if bandset_number is None:
        bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    bandset_x = cfg.bandset_catalog.get(bandset_number)
    band_count = bandset_x.get_band_count()
    cfg.project_registry[cfg.reg_training_bandset_number] = bandset_number
    cfg.logger.log.debug('bandset band count: %s' % (str(band_count)))
    if band_count == 0:
        cfg.mx.msg_war_6(bandset_number)
    # copy file to temporary file
    temp_path = cfg.rs.configurations.temp.temporary_file_path(
        name_suffix='.scpx'
    )
    cfg.rs.files_directories.copy_file(file_path, temp_path)
    signature_catalog = cfg.rs.spectral_signatures_catalog(
        bandset=cfg.bandset_catalog.get(bandset_number)
    )
    cfg.dock_class_dlg.ui.label_48.setText(
        cfg.translate(' ROI & Signature list') + ' ('
        + cfg.translate('band set') + ' ' + str(bandset_number) + ')'
    )
    signature_catalog.load(file_path=temp_path)
    # remove training input
    project = cfg.util_qgis.get_qgis_project()
    if cfg.scp_training is not None:
        try:
            project.removeMapLayer(cfg.scp_training.layer)
        except Exception as err:
            str(err)
    # load vector in QGIS
    cfg.scp_training = TrainingVectorLayer(
        signature_catalog=signature_catalog, output_path=file_path
    )
    # connect signature threshold table
    cfg.signature_threshold.signature_thresholds_to_table()


# export signature to vector
def export_signature_vector():
    output_path = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Export SCP training input'), '',
        'SHP file (*.shp);;GPKG file (*.gpkg)'
    )
    if output_path is not False:
        if str(output_path).endswith('.shp'):
            vector_format = 'ESRI Shapefile'
        elif str(output_path).endswith('.gpkg'):
            vector_format = 'GPKG'
        else:
            output_path += '.gpkg'
            vector_format = 'GPKG'
        ids = cfg.scp_training.get_highlighted_ids()
        if len(ids) > 0:
            cfg.ui_utils.add_progress_bar()
            cfg.scp_training.signature_catalog.export_vector(
                signature_id_list=ids, output_path=output_path,
                vector_format=vector_format
            )
            cfg.ui_utils.remove_progress_bar()
            cfg.mx.msg_inf_4()


# export signature file
def export_signature_file():
    output_path = cfg.util_qt.get_save_file_name(
        None, cfg.translate('Export SCP training input'), '',
        'Training file (*.scpx)'
    )
    if output_path is not False:
        if output_path.lower().endswith('.scpx'):
            pass
        elif not output_path.lower().endswith('.scpx'):
            output_path += '.scpx'
        ids = cfg.scp_training.get_highlighted_ids()
        if len(ids) > 0:
            cfg.ui_utils.add_progress_bar()
            cfg.scp_training.save_signature_catalog(
                path=output_path, signature_id_list=ids
            )
            cfg.ui_utils.remove_progress_bar()


# export signature file
def export_signature_as_csv():
    output_path = cfg.util_qt.get_existing_directory(
        None, cfg.translate('Select a directory')
    )
    if output_path is not False:
        ids = cfg.scp_training.get_highlighted_ids()
        if len(ids) > 0:
            cfg.ui_utils.add_progress_bar()
            cfg.scp_training.signature_catalog.export_signatures_as_csv(
                signature_id_list=ids, output_directory=output_path
            )
            cfg.ui_utils.remove_progress_bar()
            cfg.mx.msg_inf_4()


# open a vector
def open_vector():
    vector = cfg.util_qt.get_open_file(
        None, cfg.translate('Select a vector'), '',
        'SHP file (*.shp);;GPKG file (*.gpkg)'
    )
    if len(vector) > 0:
        cfg.dialog.ui.select_shapefile_label.setText(vector)
        fields = cfg.util_gdal.vector_fields(vector)
        cfg.dialog.ui.MC_ID_combo.clear()
        cfg.dialog.ui.MC_ID_combo.addItems(fields)
        cfg.dialog.ui.MC_Info_combo.clear()
        cfg.dialog.ui.MC_Info_combo.addItems(fields)
        cfg.dialog.ui.C_ID_combo.clear()
        cfg.dialog.ui.C_ID_combo.addItems(fields)
        cfg.dialog.ui.C_Info_combo.clear()
        cfg.dialog.ui.C_Info_combo.addItems(fields)
    else:
        cfg.dialog.ui.select_shapefile_label.setText('')
        cfg.dialog.ui.MC_ID_combo.clear()
        cfg.dialog.ui.MC_Info_combo.clear()
        cfg.dialog.ui.C_ID_combo.clear()
        cfg.dialog.ui.C_Info_combo.clear()


# import vector file from selected path in cfg.dialog.ui.select_shapefile_label
def import_vector():
    if len(cfg.dialog.ui.select_shapefile_label.text()) > 0:
        macroclass_field = cfg.dialog.ui.MC_ID_combo.currentText()
        macroclass_name_field = cfg.dialog.ui.MC_Info_combo.currentText()
        class_field = cfg.dialog.ui.C_ID_combo.currentText()
        class_name_field = cfg.dialog.ui.C_Info_combo.currentText()
        if cfg.dialog.ui.signature_checkBox_2.isChecked() is True:
            calculate_signature = True
        else:
            calculate_signature = False
        if cfg.scp_training is None:
            cfg.mx.msg_war_5()
        else:
            cfg.ui_utils.add_progress_bar()
            cfg.scp_training.save_temporary_signature_catalog()
            signature_catalog = cfg.scp_training.signature_catalog_copy()
            cfg.scp_training.set_signature_catalog(
                signature_catalog=signature_catalog
            )
            cfg.scp_training.import_vector(
                file_path=cfg.dialog.ui.select_shapefile_label.text(),
                macroclass_field=macroclass_field,
                macroclass_name_field=macroclass_name_field,
                class_field=class_field, class_name_field=class_name_field,
                calculate_signature=calculate_signature
            )
            cfg.dock_class_dlg.ui.undo_save_Button.setEnabled(True)
            cfg.dock_class_dlg.ui.redo_save_Button.setEnabled(False)
            cfg.ui_utils.remove_progress_bar()


""" Plot """


# add signatures to spectral plot
def add_signature_to_spectral_plot(tab_index=0):
    if cfg.scp_training is not None:
        ids = cfg.scp_training.get_highlighted_ids(
            select_all=False, signatures=True
        )
        if len(ids) > 0:
            plot_catalog = cfg.spectral_signature_plotter.plot_catalog
            signature_catalog = cfg.scp_training.signature_catalog
            cfg.ui_utils.add_progress_bar()
            for _id in ids:
                if cfg.rs.configurations.action:
                    signature_catalog.export_signature_values_for_plot(
                        signature_id=_id, plot_catalog=plot_catalog
                    )
            cfg.ui_utils.remove_progress_bar(sound=False)
            cfg.spectral_signature_plotter.signature_list_plot_table()
            cfg.input_interface.spectral_plot_tab()
            cfg.input_interface.select_spectral_plot_settings_tab(tab_index)
        else:
            cfg.input_interface.spectral_plot_tab()
            cfg.input_interface.select_spectral_plot_settings_tab(tab_index)


# add ROI to scatter plot
def add_roi_to_scatter_plot():
    cfg.logger.log.debug('add_roi_to_scatter_plot')
    ids = cfg.scp_training.get_highlighted_ids(select_all=False)
    if len(ids) > 0:
        plot_catalog = cfg.scatter_plotter.plot_catalog
        signature_catalog = cfg.scp_training.signature_catalog
        cfg.ui_utils.add_progress_bar()
        for _id in ids:
            geometry = signature_catalog.table[
                signature_catalog.table['signature_id'] == _id].geometry[0]
            if geometry == 1:
                signature_catalog.export_signature_values_for_plot(
                    signature_id=_id, plot_catalog=plot_catalog
                )
                temp_path = cfg.rs.configurations.temp.temporary_file_path(
                    name_suffix='.gpkg'
                )
                # export geometry
                cfg.util_gdal.get_polygon_from_vector(
                    vector_path=signature_catalog.geometry_file,
                    output=temp_path, attribute_filter="%s = '%s'" % (
                        cfg.rs.configurations.uid_field_name, _id
                    )
                )
                plot_catalog.catalog[_id].attributes[
                    'geometry_path'] = temp_path
            else:
                cfg.logger.log.debug(
                    'no geometry for signature_id: %s' % str(_id)
                )
        cfg.scatter_plotter.scatter_plot_list_table()
        cfg.input_interface.scatter_plot_tab()
    else:
        cfg.input_interface.scatter_plot_tab()


# export symbology
def export_symbology(macroclass=True):
    if macroclass is True:
        value_color_dictionary = (
            cfg.scp_training.signature_catalog.macroclasses_color_string
        )
        value_name_dictionary = (
            cfg.scp_training.signature_catalog.macroclasses
        )
    else:
        classes = cfg.scp_training.signature_catalog.table.class_id.tolist()
        names = cfg.scp_training.signature_catalog.table.class_name.tolist()
        colors = cfg.scp_training.signature_catalog.table.color.tolist()
        value_name_dictionary = {}
        value_color_dictionary = {}
        for class_i in range(len(classes)):
            value_name_dictionary[classes[class_i]] = names[class_i]
            value_color_dictionary[classes[class_i]] = colors[class_i]
    return value_name_dictionary, value_color_dictionary
