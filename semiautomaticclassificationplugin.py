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


import multiprocessing
import platform
import sys
from os import path, makedirs

import qgis.utils as qgis_utils
# import the PyQt libraries
from PyQt5.QtCore import (
    Qt, QFileInfo, QSettings, QSize, qVersion, QTranslator, QCoreApplication,
    QDir, QDate
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QApplication, QHeaderView, QLineEdit
# import the QGIS libraries
from qgis.core import (
    Qgis, QgsWkbTypes, QgsApplication, QgsProject, QgsSettings
)
from qgis.gui import QgsRubberBand

# import plugin version
from .__init__ import version as semiautomaticclass_version
# import SemiAutomaticClassificationPlugin
from .core import config as cfg, util_qgis, util_qt, utils, util_gdal, messages
from .core.ui_utils import UiUtils
from .interface import (
    input_interface, scp_dock, bandset_tab, accuracy_tab, stack_bandset_tab,
    classification_report_tab, classification_to_vector_tab, split_bands_tab,
    cross_classification_tab, band_dilation_tab, band_erosion_tab, settings,
    band_sieve_tab, band_combination_tab, band_calc_tab, band_neighbor_tab,
    band_pca_tab, reclassification_tab, vector_to_raster_tab, clip_bands_tab,
    reproject_bandset_tab, masking_bands_tab, download_products_tab,
    mosaic_bandsets_tab, image_conversion_tab, script_tab, classification_tab,
    rgb_composite_tab, signature_threshold_tab, multiple_roi_tab
)
from .map_pointers.classification_preview_pointer import ClassificationPreview
from .map_pointers.clip_bands_pointer import ClipBandsPointer
from .map_pointers.download_products_pointer import DownloadProductsPointer
from .map_pointers.manual_roi_pointer import ManualROIPointer
from .map_pointers.region_growing_pointer import RegionGrowingPointer
from .qgis_processing.scp_algorithm_provider import SCPAlgorithmProvider
from .spectral_signature import (
    spectral_signature_plot, scatter_plot, signature_importer
)
# initialize Qt ui
from .ui.semiautomaticclassificationplugindialog import (
    SemiAutomaticClassificationPluginDialog, SpectralSignatureDialog,
    ScatterPlotDialog, DockClassDialog, WidgetDialog
)

global plugin_check
try:
    import remotior_sensus

    plugin_check = True
except Exception as error:
    str(error)
    plugin_check = False
    # noinspection PyTypeChecker
    qgis_utils.iface.messageBar().pushMessage(
        'Semi-Automatic Classification Plugin', QApplication.translate(
            'semiautomaticclassificationplugin',
            'Error. Please, install the required Python library '
            'remotior_sensus'
        ),
        level=Qgis.Critical
    )

try:
    multiprocessing.set_start_method('spawn')
except Exception as error:
    str(error)


# noinspection PyPep8Naming
class SemiAutomaticClassificationPlugin:

    # noinspection PyArgumentList,PyTypeChecker
    def __init__(self, iface):
        # system information
        cfg.system_platform = platform.system()
        # QGIS version
        qgis_ver = Qgis.QGIS_VERSION_INT
        if plugin_check is True:
            # set multiprocess path
            python_path = None
            if cfg.system_platform == 'Windows':
                try:
                    python_path = path.abspath(
                        path.join(sys.exec_prefix, 'pythonw.exe')
                    )
                    if path.isfile(python_path):
                        multiprocessing.set_executable(python_path)
                    else:
                        # from https://trac.osgeo.org/osgeo4w/ticket/392
                        python_path = path.abspath(
                            path.join(sys.exec_prefix, '../../bin/pythonw.exe')
                        )
                        if path.isfile(python_path):
                            multiprocessing.set_executable(python_path)
                        else:
                            qgis_utils.iface.messageBar().pushMessage(
                                'Semi-Automatic Classification Plugin',
                                QApplication.translate(
                                    'semiautomaticclassificationplugin',
                                    'Error. Python library not found'
                                ),
                                level=Qgis.Info
                            )
                except Exception as err:
                    str(err)
            # reference to QGIS interface
            cfg.iface = iface
            # reference to map canvas
            cfg.map_canvas = iface.mapCanvas()
            # locale
            locale_settings = QSettings().value('locale/userLocale')[0:2]
            # locale
            locale_path = ''
            if QFileInfo(cfg.plugin_dir).exists():
                locale_path = (
                        '%s/i18n/semiautomaticclassificationplugin_%s.qm'
                        % (cfg.plugin_dir, locale_settings)
                )
            if QFileInfo(locale_path).exists():
                transl = QTranslator()
                transl.load(locale_path)
                if qVersion() > '4.3.3':
                    QCoreApplication.installTranslator(transl)
            cfg.ui_utils = UiUtils()
            cfg.translate = cfg.ui_utils.translate
            try:
                # create the dialog
                cfg.dialog = SemiAutomaticClassificationPluginDialog()
                # class dock dialog
                cfg.dock_class_dlg = DockClassDialog(
                    cfg.iface.mainWindow(), cfg.iface
                )
                cfg.input_interface = input_interface
                # welcome dialog
                cfg.widget_dialog = WidgetDialog()
            except Exception as err:
                str(err)
                qgis_utils.iface.messageBar().pushMessage(
                    'Semi-Automatic Classification Plugin',
                    QApplication.translate(
                        'semiautomaticclassificationplugin',
                        'Please, restart QGIS for executing the '
                        'Semi-Automatic Classification Plugin'
                    ),
                    level=Qgis.Info
                )
            cfg.utils = utils
            cfg.util_qgis = util_qgis
            cfg.util_qt = util_qt
            cfg.util_gdal = util_gdal
            # spectral signature plot dialog
            cfg.spectral_plot_dlg = SpectralSignatureDialog()
            # scatter plot dialog
            cfg.scatter_plot_dlg = ScatterPlotDialog()
            cfg.settings = settings
            cfg.bst = bandset_tab
            cfg.signature_plot = spectral_signature_plot
            cfg.scatter_plot = scatter_plot
            cfg.signature_importer = signature_importer
            cfg.usgs_spectral_lib = signature_importer.USGSSpectralLib()
            cfg.accuracy = accuracy_tab
            cfg.class_report = classification_report_tab
            cfg.class_vector = classification_to_vector_tab
            cfg.cross_classification = cross_classification_tab
            cfg.rgb_composite = rgb_composite_tab
            cfg.signature_threshold = signature_threshold_tab
            cfg.multiple_roi = multiple_roi_tab
            cfg.band_calc = band_calc_tab
            cfg.dilation = band_dilation_tab
            cfg.stack_bandset = stack_bandset_tab
            cfg.split_bands = split_bands_tab
            cfg.reproject_bands = reproject_bandset_tab
            cfg.masking_bands = masking_bands_tab
            cfg.image_conversion = image_conversion_tab
            cfg.clip_bands = clip_bands_tab
            cfg.clip_bands_pointer = ClipBandsPointer(cfg.map_canvas)
            cfg.classification_preview_pointer = ClassificationPreview(
                cfg.map_canvas
            )
            cfg.download_products = download_products_tab
            cfg.download_products_pointer = DownloadProductsPointer(
                cfg.map_canvas
            )
            cfg.region_growing_pointer = RegionGrowingPointer(cfg.map_canvas)
            cfg.manual_roi_pointer = ManualROIPointer(cfg.map_canvas)
            cfg.mosaic_bandsets = mosaic_bandsets_tab
            cfg.vector_to_raster = vector_to_raster_tab
            cfg.erosion = band_erosion_tab
            cfg.sieve = band_sieve_tab
            cfg.neighbor = band_neighbor_tab
            cfg.pca_tab = band_pca_tab
            cfg.reclassification = reclassification_tab
            cfg.band_combination = band_combination_tab
            cfg.classification = classification_tab
            cfg.script = script_tab
            cfg.scp_dock = scp_dock
            # roi rubber band
            cfg.scp_dock_rubber_roi = QgsRubberBand(
                cfg.map_canvas, QgsWkbTypes.LineGeometry
            )
            cfg.scp_dock_rubber_roi.setColor(QColor(0, 255, 255))
            cfg.scp_dock_rubber_roi.setWidth(2)
            # set font
            try:
                q_set = QgsSettings()
                f = q_set.value('qgis/stylesheet/fontFamily')
                s = q_set.value('qgis/stylesheet/fontPointSize')
                font = QFont()
                font.setFamily(f)
                font.setPointSize(int(s))
                cfg.dialog.setFont(font)
                cfg.dialog.ui.menu_treeWidget.setFont(font)
            except Exception as err:
                str(err)
            # plugin directory
            cfg.plugin_dir = ('%s/python/plugins/%s' % (
                QFileInfo(
                    QgsApplication.qgisUserDatabaseFilePath()
                ).path(), str(__name__).split('.')[0])
                              )
            registry_keys()
            # temporary directory
            cfg.temp_dir = get_temporary_directory()
            cfg.mx = messages
            try:
                cfg.rs = remotior_sensus.Session(
                    n_processes=cfg.qgis_registry[cfg.reg_threads_value],
                    log_level=20, temporary_directory=cfg.temp_dir,
                    available_ram=cfg.qgis_registry[cfg.reg_ram_value],
                    multiprocess_module=multiprocessing,
                    progress_callback=cfg.ui_utils.update_bar,
                    messages_callback=cfg.mx
                )
            except Exception as err:
                str(err)
                qgis_utils.iface.messageBar().pushMessage(
                    'Semi-Automatic Classification Plugin',
                    QApplication.translate(
                        'semiautomaticclassificationplugin',
                        'Error starting Remotior Sensus'
                    ),
                    level=Qgis.Info
                )
            if cfg.rs is not None:
                # logger
                cfg.logger = cfg.rs.configurations.logger
                # create BandSet Catalog
                cfg.bandset_catalog = cfg.rs.bandset_catalog()
                cfg.dialog.ui.temp_directory_label.setText(cfg.temp_dir)
                cfg.spectral_signature_plotter = (
                    cfg.signature_plot.SpectralSignaturePlot()
                )
                cfg.scatter_plotter = (
                    cfg.scatter_plot.ScatterPlot()
                )
                # info
                sys_info = str(
                    'SCP %s; QGIS v. %s; L: %s; OS: %s; python: %s'
                    % (semiautomaticclass_version(), str(qgis_ver),
                       locale_settings, cfg.system_platform, str(python_path))
                )
                cfg.scp_processing_provider = SCPAlgorithmProvider()
                cfg.logger.log.info(sys_info)

    # init GUI
    # noinspection PyArgumentList,PyTypeChecker
    def initGui(self):
        if plugin_check is True and cfg.rs is not None:
            try:
                cfg.iface.addDockWidget(
                    Qt.LeftDockWidgetArea,
                    cfg.dock_class_dlg
                )
            except Exception as err:
                str(err)
                qgis_utils.iface.messageBar().pushMessage(
                    'Semi-Automatic Classification Plugin',
                    QApplication.translate(
                        'semiautomaticclassificationplugin',
                        'Please restart QGIS for installing the '
                        'Semi-Automatic Classification Plugin'
                    ),
                    level=Qgis.Info
                )
            # bandset tab
            cfg.bst.add_satellite_to_combo(cfg.rs.configurations.sat_band_list)
            cfg.bst.add_unit_to_combo(cfg.rs.configurations.unit_list)
            cfg.input_interface.load_input_toolbar()
            ''' menu '''
            cfg.input_interface.load_menu()
            # set plugin version
            cfg.dialog.ui.plugin_version_label.setText(
                semiautomaticclass_version()
            )
            cfg.dock_class_dlg.ui.plugin_version_label2.setText(
                'SCP %s' % semiautomaticclass_version()
            )
            # row height
            cfg.dialog.ui.download_images_tableWidget.verticalHeader(
            ).setDefaultSectionSize(24)
            cfg.dialog.ui.tableWidget_band_calc.verticalHeader(
            ).setDefaultSectionSize(24)
            cfg.dialog.ui.tableWidget_band_calc.setColumnHidden(1, True)
            cfg.band_calc.add_functions_to_table(cfg.band_calc_functions)
            cfg.band_calc.add_functions_to_table(
                cfg.qgis_registry[cfg.reg_custom_functions]
            )
            cfg.dialog.ui.bands_tableWidget.verticalHeader(
            ).setDefaultSectionSize(24)
            # spectral signature threshold table
            cfg.util_qt.insert_table_column(
                cfg.dialog.ui.signature_threshold_tableWidget, 7,
                cfg.signature_id_column_name, 20, True
            )
            sig_table = cfg.dialog.ui.signature_threshold_tableWidget
            sig_table.verticalHeader(
            ).setDefaultSectionSize(24)
            cfg.dialog.ui.point_tableWidget.verticalHeader(
            ).setDefaultSectionSize(24)
            sig_list = cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget
            # spectral signature plot list
            cfg.util_qt.insert_table_column(
                sig_list, 6, cfg.signature_id_column_name, 20, True
            )
            cfg.util_qt.sort_table_column(sig_list, 3)
            cfg.util_qt.set_column_width_list(
                sig_list, [[0, 20], [1, 40], [2, 120], [3, 40], [4, 120],
                           [5, 20]]
            )
            sig_list.verticalHeader().setDefaultSectionSize(24)
            # scatter plot table
            sc_p_list = cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget
            cfg.util_qt.insert_table_column(
                sc_p_list, 6, cfg.signature_id_column_name, None, True
            )
            try:
                sig_list.horizontalHeader().setSectionResizeMode(
                    2, QHeaderView.Stretch
                )
                sig_list.horizontalHeader().setSectionResizeMode(
                    4, QHeaderView.Stretch
                )
            except Exception as err:
                str(err)
            # passwords
            cfg.dialog.ui.smtp_password_lineEdit.setEchoMode(
                QLineEdit.Password
            )
            cfg.dialog.ui.password_earthdata_lineEdit.setEchoMode(
                QLineEdit.Password
            )
            scatter = cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget
            # scatter plot list
            cfg.util_qt.insert_table_column(
                scatter, 6, cfg.signature_id_column_name, None, True
            )
            cfg.util_qt.sort_table_column(scatter, 3)
            cfg.util_qt.set_column_width_list(
                scatter, [[0, 30], [1, 40], [2, 100], [3, 40], [4, 100],
                          [5, 30]]
            )
            try:
                scatter.horizontalHeader().setSectionResizeMode(
                    2, QHeaderView.Stretch
                )
                scatter.horizontalHeader().setSectionResizeMode(
                    4, QHeaderView.Stretch
                )
            except Exception as err:
                str(err)
            # signature threshold
            cfg.util_qt.insert_table_column(
                sig_table, 7,
                cfg.signature_id_column_name, None, True
            )
            cfg.util_qt.set_column_width_list(
                sig_table, [[4, 100], [5, 100], [6, 100]]
            )
            try:
                sig_table.horizontalHeader().setSectionResizeMode(
                    1, QHeaderView.Stretch
                )
                sig_table.horizontalHeader().setSectionResizeMode(
                    3, QHeaderView.Stretch
                )
            except Exception as err:
                str(err)
            # product download tab
            cfg.util_qt.set_column_width_list(
                cfg.dialog.ui.download_images_tableWidget,
                [[0, 100], [1, 400]]
            )
            # set log state
            cfg.dialog.ui.log_checkBox.setCheckState(
                int(cfg.qgis_registry[cfg.reg_log_key])
            )
            if cfg.rs is not None:
                if cfg.qgis_registry[cfg.reg_log_key] == 2:
                    # debug
                    cfg.rs.set(log_level=10)
                    cfg.mx.msg_inf_3()
                else:
                    # info
                    cfg.rs.set(log_level=20)
            cfg.logger.log.debug(
                'logger: %s' % cfg.qgis_registry[cfg.reg_log_key]
            )
            # set download news state
            cfg.dialog.ui.download_news_checkBox.setCheckState(
                int(cfg.qgis_registry[cfg.reg_download_news])
            )
            # set raster compression
            cfg.dialog.ui.raster_compression_checkBox.setCheckState(
                int(cfg.qgis_registry[cfg.reg_raster_compression])
            )
            # set ROI transparency
            cfg.dialog.ui.transparency_Slider.setValue(
                int(cfg.qgis_registry[cfg.reg_roi_transparency])
            )
            # gdal path
            cfg.dialog.ui.gdal_path_lineEdit.setText(
                cfg.qgis_registry[cfg.reg_gdal_path]
            )
            # ROI color
            cfg.dialog.ui.change_color_Button.setStyleSheet(
                'background-color :' + cfg.qgis_registry[cfg.reg_roi_color]
            )
            cfg.dialog.ui.transparency_Label.setText(
                QApplication.translate(
                    'semiautomaticclassificationplugin', 'Transparency '
                ) + str(cfg.qgis_registry[cfg.reg_roi_transparency]) + '%'
            )
            cfg.dialog.ui.transparency_Slider.setValue(
                cfg.qgis_registry[cfg.reg_roi_transparency]
            )
            # set SMTP checkbox state
            cfg.dialog.ui.smtp_checkBox.setCheckState(
                int(cfg.qgis_registry[cfg.reg_smtp_check])
            )
            if cfg.qgis_registry[cfg.reg_smtp_check] == 2:
                cfg.smtp_notification = True
            else:
                cfg.smtp_notification = False
            # set sound state
            cfg.dialog.ui.sound_checkBox.setCheckState(
                int(cfg.qgis_registry[cfg.reg_sound])
            )
            # raster variable name
            cfg.dialog.ui.variable_name_lineEdit.setText(
                cfg.qgis_registry[cfg.reg_raster_variable_name]
            )
            # group name
            cfg.dialog.ui.group_name_lineEdit.setText(
                cfg.qgis_registry[cfg.reg_group_name]
            )
            # hide tabs
            cfg.dialog.ui.SCP_tabs.setStyleSheet(
                'QTabBar::tab {padding: 0px; max-height: 0px;}'
            )
            # set window size
            cfg.dialog.blockSignals(True)
            cfg.dialog.resize(
                int(cfg.qgis_registry[cfg.reg_window_size_w]),
                int(cfg.qgis_registry[cfg.reg_window_size_h])
            )
            cfg.dialog.blockSignals(False)
            cfg.dialog.ui.widget.setMinimumSize(QSize(50, 0))
            cfg.dialog.ui.widget.setMaximumSize(QSize(400, 16777215))
            cfg.dialog.ui.splitter.setSizes(
                cfg.qgis_registry[cfg.reg_splitter_sizes]
            )
            cfg.dialog.ui.splitter.splitterMoved.connect(
                cfg.input_interface.moved_splitter
            )
            # set RAM value
            cfg.dialog.ui.RAM_spinBox.setValue(
                int(cfg.qgis_registry[cfg.reg_ram_value])
            )
            # set CPU value
            cfg.dialog.ui.CPU_spinBox.setValue(
                cfg.qgis_registry[cfg.reg_threads_value]
            )
            try:
                # set SMTP server
                cfg.dialog.ui.smtp_server_lineEdit.setText(
                    cfg.qgis_registry[cfg.reg_smtp_server]
                )
                # set SMTP to emails
                cfg.dialog.ui.to_email_lineEdit.setText(
                    cfg.qgis_registry[cfg.reg_smtp_emails]
                )
                # set SMTP user and password
                cfg.dialog.ui.smtp_user_lineEdit.setText(
                    cfg.qgis_registry[cfg.reg_smtp_user]
                )
                if len(cfg.qgis_registry[cfg.reg_smtp_password]) > 0:
                    smtp_password = cfg.utils.decrypt_password(
                        cfg.qgis_registry[
                            cfg.reg_smtp_password].decode('UTF-8')
                    )
                    cfg.dialog.ui.smtp_password_lineEdit.setText(
                        smtp_password.decode('UTF-8')
                    )
                    # overwrite registry
                    cfg.qgis_registry[
                        cfg.reg_smtp_password] = cfg.utils.encrypt_password(
                        smtp_password.decode('UTF-8')
                    )
                    cfg.smtp_password = (
                        smtp_password.decode('UTF-8')
                    )
            except Exception as err:
                str(err)
            cfg.smtp_user = cfg.qgis_registry[
                cfg.reg_smtp_user]
            cfg.smtp_recipients = cfg.qgis_registry[
                cfg.reg_smtp_emails]
            cfg.smtp_server = cfg.qgis_registry[
                cfg.reg_smtp_server]
            try:
                # set earthdata user and password
                cfg.dialog.ui.user_earthdata_lineEdit.setText(
                    cfg.qgis_registry[cfg.reg_earthdata_user]
                )
                if cfg.qgis_registry[cfg.reg_earthdata_pass] is not None:
                    earthdata_pass = cfg.utils.decrypt_password(
                        cfg.qgis_registry[
                            cfg.reg_earthdata_pass].decode('UTF-8')
                    )
                    cfg.dialog.ui.password_earthdata_lineEdit.setText(
                        earthdata_pass.decode('UTF-8')
                    )
            except Exception as err:
                str(err)
            cfg.dialog.ui.dateEdit_to.setDate(QDate.currentDate())
            cfg.dialog.ui.dateEdit_from.setDate(
                QDate.currentDate().addDays(-365)
            )
            # add satellite list to combo
            for product in cfg.rs.configurations.product_list:
                cfg.dialog.ui.landsat_satellite_combo.addItem(product)
            # add color list to combo
            cfg.scatter_plot.add_colormap_to_combo(cfg.scatter_color_map)
            cfg.usgs_spectral_lib.add_spectral_library_to_combo()
            cfg.neighbor.load_statistic_combo()
            # bandset virtual raster
            cfg.virtual_bandset_name = cfg.translate('Virtual Band Set ')
            cfg.bandset_tab_name = cfg.translate('Band set ')
            cfg.scp_layer_name = cfg.translate('SCP training layer')
            # connect to project loaded
            QgsProject.instance().readProject.connect(
                self.project_loaded
            )
            # connect to project saved
            QgsProject.instance().projectSaved.connect(
                self.project_saved
            )
            cfg.iface.newProjectCreated.connect(self.new_project_loaded)
            cfg.dialog.ui.help_textBrowser.setSearchPaths([cfg.temp_dir])
            registry = QgsApplication.instance().processingRegistry()
            registry.addProvider(cfg.scp_processing_provider)
            # welcome message
            if cfg.first_install == 1:
                cfg.input_interface.welcome_text(
                    'https://semiautomaticgit.github.io'
                    '/SemiAutomaticClassificationPluginWelcome/changelog.html'
                )
            else:
                date_string = cfg.utils.get_date()
                cfg.input_interface.welcome_text(
                    'https://semiautomaticgit.github.io'
                    '/SemiAutomaticClassificationPluginWelcome/welcome_%s.html'
                    % date_string,
                    'https://semiautomaticgit.github.io'
                    '/SemiAutomaticClassificationPluginWelcome/welcome.html'
                )
            cfg.logger.log.debug('init GUI')
            connect_gui()
        else:
            dock_class_dlg = DockClassDialog(
                qgis_utils.iface.mainWindow(), qgis_utils.iface
            )
            qgis_utils.iface.removeDockWidget(dock_class_dlg)

    # save tables when saving project
    # noinspection PyArgumentList
    @staticmethod
    def project_saved():
        cfg.logger.log.debug('project_saved')
        cfg.project_registry[
            cfg.reg_bandset_count] = cfg.bandset_catalog.get_bandset_count()

        # download table
        cfg.download_products.save_download_table()
        for r in cfg.project_registry:
            cfg.util_qgis.write_project_variable(r, cfg.project_registry[r])
        # save bandset table
        for bandset_number in range(
                1, cfg.project_registry[cfg.reg_bandset_count] + 1
        ):
            xml = cfg.bandset_catalog.export_bandset_as_xml(
                bandset_number=bandset_number
            )
            xml = xml.replace('\n', '')
            cfg.util_qgis.write_project_variable(
                '%s%s' % (cfg.reg_bandset, bandset_number), xml
            )

    # new project
    @staticmethod
    def new_project_loaded():
        cfg.logger.log.debug('new_project_loaded')
        reset_scp()

    # read project variables
    @staticmethod
    def project_loaded():
        cfg.logger.log.debug('project_loaded')
        reset_scp()

    # remove plugin menu and icon
    # noinspection PyTypeChecker
    @staticmethod
    def unload():
        # write registry keys
        try:
            for r in cfg.qgis_registry:
                cfg.util_qt.write_registry_keys(r, cfg.qgis_registry[r])
        except Exception as err:
            try:
                cfg.logger.log.error(str(err))
            except Exception as err:
                str(err)
        try:
            cfg.logger.log.debug('unload')
            cfg.rs.close()
        except Exception as err:
            str(err)
        try:
            if cfg.dock_class_dlg is not None:
                qgis_utils.iface.removeDockWidget(cfg.dock_class_dlg)
            cfg.working_toolbar.deleteLater()
            cfg.main_menu.deleteLater()
            cfg.dialog.deleteLater()
            QgsApplication.processingRegistry().removeProvider(
                cfg.scp_processing_provider
            )
            """
            if cfg.dialog is not None:
                qgis_utils.iface.removeDockWidget(cfg.dialog)
            """
        # remove temp files
        except Exception as err:
            str(err)
            if plugin_check is True:
                qgis_utils.iface.messageBar().pushMessage(
                    'Semi-Automatic Classification Plugin',
                    QApplication.translate(
                        'semiautomaticclassificationplugin',
                        'Please, restart QGIS for executing the '
                        'Semi-Automatic Classification Plugin'
                    ),
                    level=Qgis.Info
                )


# get first installation
# noinspection PyArgumentList
def get_first_installation():
    cfg.first_install = cfg.util_qt.read_registry_keys(
        cfg.reg_first_install, 1
    )
    if cfg.first_install == 1:
        cfg.util_qt.write_registry_keys(cfg.reg_first_install, 0)
        cfg.utils.find_available_ram()
        cfg.utils.find_available_processors()


# get temporary directory
# noinspection PyArgumentList
def get_temporary_directory():
    if cfg.temp_dir is None:
        temp_dir = str(QDir.tempPath() + '/' + cfg.temp_dir_name)
    else:
        temp_dir = cfg.temp_dir
    if not QDir(temp_dir).exists():
        try:
            makedirs(temp_dir)
        except Exception as err:
            str(err)
            cfg.util_qt.write_registry_keys(cfg.reg_temp_dir, temp_dir)
            cfg.temp_dir = str(QDir.tempPath() + '/' + cfg.temp_dir_name)
            temp_dir = cfg.temp_dir
            if not QDir(temp_dir).exists():
                makedirs(temp_dir)
    return temp_dir


# read registry keys
def registry_keys():
    cfg.temp_dir = cfg.util_qt.read_registry_keys(
        cfg.reg_temp_dir, cfg.temp_dir
    )
    for r in cfg.qgis_registry:
        cfg.qgis_registry[r] = cfg.util_qt.read_registry_keys(
            r, cfg.qgis_registry[r]
        )
    get_first_installation()


def connect_gui():
    cfg.clip_bands_pointer.leftClicked.connect(
        cfg.clip_bands.pointer_left_click
    )
    cfg.clip_bands_pointer.rightClicked.connect(
        cfg.clip_bands.pointer_right_click
    )
    cfg.classification_preview_pointer.leftClicked.connect(
        cfg.classification.pointer_left_click
    )
    cfg.classification_preview_pointer.rightClicked.connect(
        cfg.classification.pointer_right_click
    )
    cfg.download_products_pointer.leftClicked.connect(
        cfg.download_products.pointer_left_click
    )
    cfg.download_products_pointer.rightClicked.connect(
        cfg.download_products.pointer_right_click
    )
    cfg.region_growing_pointer.leftClicked.connect(
        cfg.scp_dock.left_click_region_growing
    )
    cfg.region_growing_pointer.rightClicked.connect(
        cfg.scp_dock.right_click_region_growing
    )
    cfg.region_growing_pointer.moved.connect(
        cfg.scp_dock.calculate_pixel_expression
    )
    cfg.manual_roi_pointer.leftClicked.connect(
        cfg.scp_dock.left_click_manual
    )
    cfg.manual_roi_pointer.rightClicked.connect(
        cfg.scp_dock.right_click_manual
    )
    cfg.manual_roi_pointer.moved.connect(
        cfg.scp_dock.calculate_pixel_expression
    )
    cfg.dialog.resizeEvent = cfg.input_interface.resize_event
    cfg.dialog.ui.SCP_tabs.currentChanged.connect(
        cfg.input_interface.scp_tab_changed
    )
    cfg.dialog.ui.main_tabWidget.currentChanged.connect(
        cfg.input_interface.main_tab_changed
    )
    cfg.dialog.ui.menu_treeWidget.itemSelectionChanged.connect(
        cfg.input_interface.menu_index
    )
    cfg.dialog.ui.f_filter_lineEdit.textChanged.connect(
        cfg.input_interface.filter_tree
    )
    """ Band set"""
    cfg.dialog.ui.toolButton_input_raster.clicked.connect(
        cfg.bst.add_file_to_band_set_action
    )
    # add loaded bands question box
    cfg.widget_dialog.ui.buttonBox.accepted.connect(cfg.bst.check_accepted)
    cfg.widget_dialog.ui.select_all_toolButton.clicked.connect(
        cfg.bst.select_all_bands
    )
    cfg.dialog.ui.add_loaded_bands_pushButton.clicked.connect(
        cfg.bst.add_loaded_band_to_bandset
    )
    cfg.dialog.ui.toolButton_custom_wavelength.clicked.connect(
        cfg.bst.set_custom_wavelength_action
    )
    cfg.dialog.ui.clear_bandset_toolButton.clicked.connect(
        cfg.bst.clear_bandset_action
    )
    cfg.dialog.ui.move_up_toolButton.clicked.connect(cfg.bst.move_up_band)
    cfg.dialog.ui.move_down_toolButton.clicked.connect(cfg.bst.move_down_band)
    cfg.dialog.ui.sort_by_name_toolButton.clicked.connect(
        cfg.bst.sort_bands_by_name
    )
    cfg.dialog.ui.remove_toolButton.clicked.connect(cfg.bst.remove_band)
    cfg.dialog.ui.add_band_set_toolButton.clicked.connect(
        cfg.bst.add_bandset_tab_action
    )
    cfg.dialog.ui.import_bandset_toolButton.clicked.connect(
        cfg.bst.import_bandset
    )
    cfg.dialog.ui.export_bandset_toolButton.clicked.connect(
        cfg.bst.export_bandset
    )
    cfg.dialog.ui.wavelength_sat_combo.currentIndexChanged.connect(
        cfg.bst.satellite_wavelength
    )
    cfg.dialog.ui.unit_combo.currentIndexChanged.connect(
        cfg.bst.satellite_unit
    )
    cfg.dialog.ui.bandset_dateEdit.dateChanged.connect(
        cfg.bst.set_bandset_date
    )
    cfg.dialog.ui.band_set_process_toolButton.clicked.connect(
        cfg.bst.perform_bandset_tools
    )
    cfg.dialog.ui.band_set_filter_lineEdit.textChanged.connect(
        cfg.bst.filter_table
    )
    cfg.dialog.ui.bandset_number_spinBox.valueChanged.connect(
        cfg.bst.change_bandset_tab_action
    )
    cfg.dialog.ui.bandset_tableWidget.doubleClicked.connect(
        cfg.bst.change_bandset_table_action
    )
    cfg.dialog.ui.bandset_date_lineEdit.editingFinished.connect(
        cfg.bst.edit_bandset_date
    )
    cfg.dialog.ui.root_dir_lineEdit.editingFinished.connect(
        cfg.bst.edit_bandset_root
    )
    cfg.dialog.ui.remove_bandset_toolButton.clicked.connect(
        cfg.bst.remove_bandsets
    )
    cfg.dialog.ui.move_down_toolButton_4.clicked.connect(
        cfg.bst.move_down_bandset
    )
    cfg.dialog.ui.move_up_toolButton_4.clicked.connect(cfg.bst.move_up_bandset)
    cfg.dialog.ui.sort_by_date.clicked.connect(cfg.bst.sort_bandsets_by_date)
    cfg.dialog.ui.rgb_toolButton.clicked.connect(cfg.bst.add_composite)

    """ SCP dock """
    cfg.dock_class_dlg.ui.bandset_toolButton.clicked.connect(
        cfg.input_interface.bandset_tab
    )
    cfg.dock_class_dlg.ui.band_processing_toolButton.clicked.connect(
        cfg.input_interface.band_processing_tab
    )
    cfg.dock_class_dlg.ui.preprocessing_toolButton_2.clicked.connect(
        cfg.input_interface.pre_processing_tab
    )
    cfg.dock_class_dlg.ui.postprocessing_toolButton_2.clicked.connect(
        cfg.input_interface.post_processing_tab
    )
    cfg.dock_class_dlg.ui.bandcalc_toolButton_2.clicked.connect(
        cfg.input_interface.band_calc_tab
    )
    cfg.dock_class_dlg.ui.download_images_toolButton_2.clicked.connect(
        cfg.input_interface.select_download_products_tab
    )
    cfg.dock_class_dlg.ui.basic_tools_toolButton.clicked.connect(
        cfg.input_interface.basic_tools_tab
    )
    cfg.dock_class_dlg.ui.batch_toolButton.clicked.connect(
        cfg.input_interface.script_tab
    )
    cfg.dock_class_dlg.ui.userguide_toolButton_2.clicked.connect(
        cfg.input_interface.quick_guide
    )
    cfg.dock_class_dlg.ui.help_toolButton_2.clicked.connect(
        cfg.input_interface.ask_help
    )
    cfg.dock_class_dlg.ui.tabWidget_dock.currentChanged.connect(
        cfg.input_interface.dock_tab_changed
    )
    cfg.dock_class_dlg.ui.button_new_input.clicked.connect(
        cfg.scp_dock.create_training_input
    )
    cfg.dock_class_dlg.ui.button_reset_input.clicked.connect(
        cfg.scp_dock.reset_input
    )
    cfg.dock_class_dlg.ui.button_Save_ROI.clicked.connect(
        cfg.scp_dock.save_roi_to_training
    )
    cfg.dock_class_dlg.ui.undo_save_Button.clicked.connect(
        cfg.scp_dock.undo_saved_roi
    )
    cfg.dock_class_dlg.ui.redo_save_Button.clicked.connect(
        cfg.scp_dock.redo_saved_roi
    )
    cfg.dock_class_dlg.ui.signature_checkBox.stateChanged.connect(
        cfg.scp_dock.signature_checkbox
    )
    cfg.dock_class_dlg.ui.scatterPlot_toolButton.clicked.connect(
        cfg.scp_dock.add_roi_to_scatter_plot
    )
    cfg.dock_class_dlg.ui.save_input_checkBox.stateChanged.connect(
        cfg.scp_dock.save_input_checkbox
    )
    cfg.dock_class_dlg.ui.trainingFile_toolButton.clicked.connect(
        cfg.scp_dock.open_training_input_file
    )
    cfg.dock_class_dlg.ui.export_signature_list_toolButton.clicked.connect(
        cfg.input_interface.export_signatures_tab
    )
    cfg.dock_class_dlg.ui.import_library_toolButton.clicked.connect(
        cfg.input_interface.import_signatures_tab
    )
    cfg.dock_class_dlg.ui.signature_spectral_plot_toolButton.clicked.connect(
        cfg.scp_dock.add_signature_to_spectral_plot
    )
    cfg.dock_class_dlg.ui.ROI_filter_lineEdit.textChanged.connect(
        cfg.scp_dock.filter_tree
    )
    cfg.dock_class_dlg.ui.delete_Signature_Button.clicked.connect(
        cfg.scp_dock.remove_selected_signatures
    )
    cfg.dock_class_dlg.ui.merge_signature_toolButton.clicked.connect(
        cfg.scp_dock.merge_signatures
    )
    cfg.dock_class_dlg.ui.calculate_signature_toolButton.clicked.connect(
        cfg.scp_dock.calculate_signatures
    )
    cfg.dock_class_dlg.ui.ROI_Macroclass_ID_spin.valueChanged.connect(
        cfg.scp_dock.roi_macroclass_id_value
    )
    cfg.dock_class_dlg.ui.max_buffer_spinBox.valueChanged.connect(
        cfg.scp_dock.max_buffer
    )
    cfg.dock_class_dlg.ui.ROI_Macroclass_line.editingFinished.connect(
        cfg.scp_dock.roi_macroclass_name_info
    )
    cfg.dock_class_dlg.ui.custom_index_lineEdit.editingFinished.connect(
        cfg.scp_dock.custom_expression_edited
    )
    cfg.dock_class_dlg.ui.ROI_ID_spin.valueChanged.connect(
        cfg.scp_dock.roi_class_id_value
    )
    cfg.dock_class_dlg.ui.ROI_Class_line.editingFinished.connect(
        cfg.scp_dock.roi_class_name_info
    )
    cfg.dock_class_dlg.ui.display_cursor_checkBox.stateChanged.connect(
        cfg.scp_dock.vegetation_index_checkbox
    )
    cfg.dock_class_dlg.ui.rapid_ROI_checkBox.stateChanged.connect(
        cfg.scp_dock.rapid_roi_checkbox
    )
    cfg.dock_class_dlg.ui.rapidROI_band_spinBox.valueChanged.connect(
        cfg.scp_dock.rapid_roi_band
    )

    """ Download product"""
    cfg.dialog.ui.find_images_toolButton.clicked.connect(
        cfg.download_products.find_images
    )
    cfg.dialog.ui.selectUL_toolButton_3.clicked.connect(
        cfg.download_products.pointer_active
    )
    cfg.dialog.ui.toolButton_display.clicked.connect(
        cfg.download_products.display_images
    )
    cfg.dialog.ui.toolButton_OSM.clicked.connect(
        cfg.download_products.display_osm
    )
    cfg.dialog.ui.remove_image_toolButton.clicked.connect(
        cfg.download_products.remove_image_from_table
    )
    cfg.dialog.ui.clear_table_toolButton.clicked.connect(
        cfg.download_products.clear_table
    )
    cfg.dialog.ui.download_images_Button.clicked.connect(
        cfg.download_products.download_images_action
    )
    cfg.dialog.ui.export_links_Button.clicked.connect(
        cfg.download_products.export_links
    )
    cfg.dialog.ui.import_table_pushButton.clicked.connect(
        cfg.download_products.import_table_text
    )
    cfg.dialog.ui.export_table_pushButton.clicked.connect(
        cfg.download_products.export_table_to_text
    )
    cfg.dialog.ui.show_area_radioButton_2.clicked.connect(
        cfg.download_products.show_hide_area
    )
    cfg.dialog.ui.check_toolButton_2.clicked.connect(
        cfg.download_products.check_all_bands
    )
    cfg.dialog.ui.remember_user_checkBox_3.stateChanged.connect(
        cfg.download_products.remember_user_earthdata_checkbox
    )
    cfg.dialog.ui.user_earthdata_lineEdit.editingFinished.connect(
        cfg.download_products.remember_user_earthdata
    )
    cfg.dialog.ui.password_earthdata_lineEdit.editingFinished.connect(
        cfg.download_products.remember_user_earthdata
    )
    cfg.dialog.ui.download_images_tableWidget.itemSelectionChanged.connect(
        cfg.download_products.table_click
    )
    cfg.dialog.ui.products_filter_lineEdit.textChanged.connect(
        cfg.download_products.filter_table
    )

    """ Basic tools """

    """ RGB composite """
    cfg.dialog.ui.RGB_tableWidget.cellChanged.connect(
        cfg.rgb_composite.edited_table
    )
    cfg.dialog.ui.add_RGB_pushButton.clicked.connect(
        cfg.rgb_composite.add_composite_to_table
    )
    cfg.dialog.ui.remove_RGB_toolButton.clicked.connect(
        cfg.rgb_composite.remove_composite_from_table
    )
    cfg.dialog.ui.sort_by_name_toolButton_2.clicked.connect(
        cfg.rgb_composite.sort_composite_names
    )
    cfg.dialog.ui.clear_RGB_list_toolButton.clicked.connect(
        cfg.rgb_composite.clear_table_action
    )
    cfg.dialog.ui.move_up_toolButton_3.clicked.connect(
        cfg.rgb_composite.move_up_composite
    )
    cfg.dialog.ui.move_down_toolButton_3.clicked.connect(
        cfg.rgb_composite.move_down_composite
    )
    cfg.dialog.ui.all_RGB_list_toolButton.clicked.connect(
        cfg.rgb_composite.calculate_all_composites_action
    )
    cfg.dialog.ui.export_RGB_List_toolButton.clicked.connect(
        cfg.rgb_composite.export_rgb_list
    )
    cfg.dialog.ui.import_RGB_List_toolButton.clicked.connect(
        cfg.rgb_composite.import_rgb_list_from_file
    )
    """ Signature threshold """
    cfg.dialog.ui.signature_threshold_tableWidget.cellChanged.connect(
        cfg.signature_threshold.edited_threshold_table
    )
    cfg.dialog.ui.automatic_threshold_pushButton.clicked.connect(
        cfg.signature_threshold.set_all_weights_from_variance
    )
    cfg.dialog.ui.set_threshold_value_pushButton.clicked.connect(
        cfg.signature_threshold.set_thresholds
    )
    cfg.dialog.ui.reset_threshold_pushButton.clicked.connect(
        cfg.signature_threshold.reset_thresholds
    )
    """ Export spectral signature """
    cfg.dialog.ui.export_SCP_pushButton.clicked.connect(
        cfg.scp_dock.export_signature_file
    )
    cfg.dialog.ui.export_SHP_pushButton.clicked.connect(
        cfg.scp_dock.export_signature_vector
    )
    cfg.dialog.ui.export_CSV_library_toolButton.clicked.connect(
        cfg.scp_dock.export_signature_as_csv
    )

    """ Import spectral signature """
    cfg.dialog.ui.open_library_pushButton.clicked.connect(
        cfg.scp_dock.import_library_file
    )
    cfg.dialog.ui.open_shapefile_pushButton.clicked.connect(
        cfg.scp_dock.open_vector
    )
    cfg.dialog.ui.import_shapefile_pushButton.clicked.connect(
        cfg.scp_dock.import_vector
    )
    cfg.dialog.ui.usgs_chapter_comboBox.currentIndexChanged.connect(
        cfg.usgs_spectral_lib.chapter_changed
    )
    cfg.dialog.ui.usgs_library_comboBox.currentIndexChanged.connect(
        cfg.usgs_spectral_lib.library_changed
    )
    cfg.dialog.ui.add_usgs_library_pushButton.clicked.connect(
        cfg.usgs_spectral_lib.add_signature_to_catalog
    )
    """ Multiple ROI """
    cfg.dialog.ui.add_point_pushButton.clicked.connect(
        cfg.multiple_roi.add_row_to_table
    )
    cfg.dialog.ui.add_random_point_pushButton.clicked.connect(
        cfg.multiple_roi.create_random_point
    )
    cfg.dialog.ui.remove_point_pushButton.clicked.connect(
        cfg.multiple_roi.remove_row_from_table
    )
    cfg.dialog.ui.save_point_rois_pushButton.clicked.connect(
        cfg.multiple_roi.create_roi_from_points
    )
    cfg.dialog.ui.import_point_list_pushButton.clicked.connect(
        cfg.multiple_roi.import_points_csv
    )
    cfg.dialog.ui.export_point_list_pushButton.clicked.connect(
        cfg.multiple_roi.export_point_list
    )
    cfg.dialog.ui.signature_checkBox2.stateChanged.connect(
        cfg.multiple_roi.signature_checkbox_2
    )
    cfg.dialog.ui.stratified_lineEdit.textChanged.connect(
        cfg.multiple_roi.expression_text_edited
    )

    """ Preprocessing """

    """ Clip raster bands """
    cfg.dialog.ui.clip_Button.clicked.connect(cfg.clip_bands.clip_bands_action)
    cfg.dialog.ui.clip_multiple_rasters.clicked.connect(
        cfg.clip_bands.set_script
    )
    cfg.dialog.ui.selectUL_toolButton.clicked.connect(
        cfg.clip_bands.pointer_active
    )
    cfg.dialog.ui.toolButton_reload_8.clicked.connect(
        cfg.clip_bands.refresh_layers
    )
    cfg.dialog.ui.show_area_radioButton_3.clicked.connect(
        cfg.clip_bands.show_hide_area
    )
    cfg.dialog.ui.vector_radioButton.toggled.connect(
        cfg.clip_bands.vector_changed
    )
    cfg.dialog.ui.temporary_ROI_radioButton.toggled.connect(
        cfg.clip_bands.roi_changed
    )
    cfg.dialog.ui.coordinates_radioButton.toggled.connect(
        cfg.clip_bands.coordinates_changed
    )
    cfg.dialog.ui.shapefile_comboBox.currentIndexChanged.connect(
        cfg.clip_bands.reference_layer_name
    )
    """ Image conversion """
    cfg.dialog.ui.toolButton_directoryInput.clicked.connect(
        cfg.image_conversion.input_image
    )
    cfg.dialog.ui.toolButton_directoryInput_MTL.clicked.connect(
        cfg.image_conversion.input_metadata
    )
    cfg.dialog.ui.pushButton_Conversion.clicked.connect(
        cfg.image_conversion.perform_conversion
    )
    cfg.dialog.ui.landsat_conversion.clicked.connect(
        cfg.image_conversion.set_script
    )
    cfg.dialog.ui.pushButton_remove_band.clicked.connect(
        cfg.image_conversion.remove_highlighted_band
    )
    """ Masking bands """
    cfg.dialog.ui.cloud_mask_toolButton.clicked.connect(
        cfg.masking_bands.mask_action
    )
    cfg.dialog.ui.toolButton_reload_23.clicked.connect(
        cfg.utils.refresh_raster_layer
    )
    cfg.dialog.ui.cloud_masking.clicked.connect(cfg.masking_bands.set_script)
    cfg.dialog.ui.cloud_mask_classes_lineEdit.textChanged.connect(
        cfg.masking_bands.text_changed
    )
    """ Mosaic band sets """
    cfg.dialog.ui.mosaic_bandsets_toolButton.clicked.connect(
        cfg.mosaic_bandsets.mosaic_action
    )
    cfg.dialog.ui.mosaic_bandsets.clicked.connect(
        cfg.mosaic_bandsets.set_script
    )
    cfg.dialog.ui.mosaic_band_sets_lineEdit.textChanged.connect(
        cfg.mosaic_bandsets.text_changed
    )
    """ Vector to Raster"""
    cfg.dialog.ui.toolButton_reload_16.clicked.connect(
        cfg.vector_to_raster.reload_vector_list
    )
    cfg.dialog.ui.toolButton_reload_17.clicked.connect(
        cfg.utils.refresh_raster_layer
    )
    cfg.dialog.ui.convert_vector_toolButton.clicked.connect(
        cfg.vector_to_raster.convert_to_raster_action
    )
    cfg.dialog.ui.vector_to_raster.clicked.connect(
        cfg.vector_to_raster.set_script
    )
    cfg.dialog.ui.vector_name_combo.currentIndexChanged.connect(
        cfg.utils.refresh_vector_fields
    )
    """ Stack raster bands """
    cfg.dialog.ui.stack_Button.clicked.connect(cfg.stack_bandset.stack_action)
    cfg.dialog.ui.stack_raster_bands.clicked.connect(
        cfg.stack_bandset.set_script
    )
    """ Split """
    cfg.dialog.ui.toolButton_reload_9.clicked.connect(
        cfg.split_bands.refresh_reference_layer
    )
    cfg.dialog.ui.split_Button.clicked.connect(cfg.split_bands.split_raster)
    cfg.dialog.ui.split_raster_bands.clicked.connect(
        cfg.split_bands.set_script
    )
    """ Reproject raster bands """
    cfg.dialog.ui.toolButton_reload_25.clicked.connect(
        cfg.reproject_bands.refresh_reference_layer
    )
    cfg.dialog.ui.align_radioButton.toggled.connect(
        cfg.reproject_bands.radio_align_changed
    )
    cfg.dialog.ui.epsg_radioButton.toggled.connect(
        cfg.reproject_bands.radio_epsg_changed
    )
    cfg.dialog.ui.reproject_Button.clicked.connect(
        cfg.reproject_bands.reproject_bands_action
    )
    cfg.dialog.ui.reproject_raster_bands.clicked.connect(
        cfg.reproject_bands.set_script
    )

    """ Band processing """

    """ Classification """
    cfg.dialog.ui.toolBox_classification.currentChanged.connect(
        cfg.classification.changed_tab
    )

    cfg.dialog.ui.macroclass_radioButton.toggled.connect(
        cfg.classification.macroclass_radio
    )
    cfg.dialog.ui.class_radioButton.toggled.connect(
        cfg.classification.class_radio
    )
    cfg.dialog.ui.linear_scaling_radioButton.toggled.connect(
        cfg.classification.linear_scaling_radio
    )
    cfg.dialog.ui.z_score_radioButton.toggled.connect(
        cfg.classification.z_scaling_radio
    )
    cfg.dialog.ui.signature_threshold_button_2.clicked.connect(
        cfg.input_interface.signature_threshold_tab
    )
    cfg.dialog.ui.signature_threshold_button_4.clicked.connect(
        cfg.input_interface.signature_threshold_tab
    )
    cfg.dialog.ui.signature_threshold_button_3.clicked.connect(
        cfg.input_interface.signature_threshold_tab
    )
    cfg.dialog.ui.load_classifier_Button.clicked.connect(
        cfg.classification.open_classifier
    )
    cfg.dialog.ui.button_classification.clicked.connect(
        cfg.classification.run_classification_action
    )
    cfg.dialog.ui.save_classifier_button.clicked.connect(
        cfg.classification.save_classifier_action
    )
    cfg.dialog.ui.classification.clicked.connect(cfg.classification.set_script)
    """ Band set combination"""
    cfg.dialog.ui.calculateBandSetComb_toolButton.clicked.connect(
        cfg.band_combination.calculate_band_combination
    )
    cfg.dialog.ui.band_combination.clicked.connect(
        cfg.band_combination.set_script
    )
    """ Band dilation"""
    cfg.dialog.ui.band_dilation_toolButton.clicked.connect(
        cfg.dilation.dilation_action
    )
    cfg.dialog.ui.dilation_classes_lineEdit.textChanged.connect(
        cfg.dilation.text_changed
    )
    cfg.dialog.ui.band_dilation.clicked.connect(cfg.dilation.set_script)
    """ Band erosion"""
    cfg.dialog.ui.class_erosion_toolButton.clicked.connect(
        cfg.erosion.band_erosion_action
    )
    cfg.dialog.ui.erosion_classes_lineEdit.textChanged.connect(
        cfg.erosion.text_changed
    )
    cfg.dialog.ui.classification_erosion.clicked.connect(
        cfg.erosion.set_script
    )
    """ Band sieve"""
    cfg.dialog.ui.sieve_toolButton.clicked.connect(cfg.sieve.band_sieve)
    cfg.dialog.ui.classification_sieve.clicked.connect(cfg.sieve.set_script)
    """ Band neighbor"""
    cfg.dialog.ui.class_neighbor_toolButton.clicked.connect(
        cfg.neighbor.band_neighbor_action
    )
    cfg.dialog.ui.neighbor_pixels.clicked.connect(cfg.neighbor.set_script)
    cfg.dialog.ui.toolButton_input_matrix.clicked.connect(
        cfg.neighbor.input_matrix_file
    )
    """ Band PCA"""
    cfg.dialog.ui.pca_Button.clicked.connect(cfg.pca_tab.calculate_pca_action)
    cfg.dialog.ui.pca.clicked.connect(cfg.pca_tab.set_script)

    """ Post processing"""

    """ Accuracy"""
    cfg.dialog.ui.toolButton_reload_4.clicked.connect(
        cfg.utils.refresh_raster_layer
    )
    cfg.dialog.ui.reference_name_combo.currentIndexChanged.connect(
        cfg.accuracy.reference_layer_name
    )
    cfg.dialog.ui.buttonReload_shape_4.clicked.connect(
        cfg.accuracy.refresh_reference_layer
    )
    cfg.dialog.ui.calculateMatrix_toolButton.clicked.connect(
        cfg.accuracy.calculate_error_matrix
    )
    cfg.dialog.ui.accuracy.clicked.connect(cfg.accuracy.set_script)
    """ Classification report """
    cfg.dialog.ui.toolButton_reload_10.clicked.connect(
        cfg.utils.refresh_raster_layer
    )
    cfg.dialog.ui.calculateReport_toolButton.clicked.connect(
        cfg.class_report.calculate_classification_report
    )
    cfg.dialog.ui.classification_report.clicked.connect(
        cfg.class_report.set_script
    )
    """ Classification to vector """
    cfg.dialog.ui.toolButton_reload_11.clicked.connect(
        cfg.utils.refresh_raster_layer
    )
    cfg.dialog.ui.convert_toolButton.clicked.connect(
        cfg.class_vector.convert_classification_to_vector_action
    )
    cfg.dialog.ui.classification_to_vector.clicked.connect(
        cfg.class_vector.set_script
    )
    """ Cross classification"""
    cfg.dialog.ui.toolButton_reload_21.clicked.connect(
        cfg.utils.refresh_raster_layer
    )
    cfg.dialog.ui.reference_name_combo_2.currentIndexChanged.connect(
        cfg.cross_classification.reference_layer_name
    )
    cfg.dialog.ui.buttonReload_shape_5.clicked.connect(
        cfg.cross_classification.refresh_reference_layer
    )
    cfg.dialog.ui.calculatecrossClass_toolButton.clicked.connect(
        cfg.cross_classification.cross_classification_action
    )
    cfg.dialog.ui.cross_classification.clicked.connect(
        cfg.cross_classification.set_script
    )
    """ Reclassification """
    cfg.dialog.ui.toolButton_reload_12.clicked.connect(
        cfg.utils.refresh_raster_layer
    )
    cfg.dialog.ui.reclassify_toolButton.clicked.connect(
        cfg.reclassification.reclassify_action
    )
    cfg.dialog.ui.calculate_unique_values_toolButton.clicked.connect(
        cfg.reclassification.calculate_unique_values
    )
    cfg.dialog.ui.incremental_new_values_toolButton.clicked.connect(
        cfg.reclassification.incremental_new_values
    )
    cfg.dialog.ui.add_value_pushButton.clicked.connect(
        cfg.reclassification.add_row
    )
    cfg.dialog.ui.remove_row_pushButton.clicked.connect(
        cfg.reclassification.remove_row
    )
    cfg.dialog.ui.import_reclass_toolButton.clicked.connect(
        cfg.reclassification.import_reclass
    )
    cfg.dialog.ui.export_reclass_toolButton.clicked.connect(
        cfg.reclassification.export_reclass
    )
    cfg.dialog.ui.reclass_values_tableWidget.cellChanged.connect(
        cfg.reclassification.edited_cell
    )
    cfg.dialog.ui.reclassification.clicked.connect(
        cfg.reclassification.set_script
    )

    """ Band Calc"""
    cfg.dialog.ui.toolButton_reload_13.clicked.connect(
        cfg.band_calc.raster_band_table
    )
    cfg.dialog.ui.plainTextEdit_calc.textChanged.connect(
        cfg.band_calc.text_changed
    )
    cfg.dialog.ui.tableWidget_band_calc.doubleClicked.connect(
        cfg.band_calc.double_click
    )
    cfg.dialog.ui.bandcalc_filter_lineEdit.textChanged.connect(
        cfg.band_calc.filter_table
    )
    cfg.dialog.ui.toolButton_import_expression.clicked.connect(
        cfg.band_calc.import_expression_list
    )
    cfg.dialog.ui.band_calc_function_tableWidget.doubleClicked.connect(
        cfg.band_calc.set_function
    )
    cfg.dialog.ui.toolButton_calculate.clicked.connect(
        cfg.band_calc.calculate_button
    )

    """ Script"""
    cfg.dialog.ui.clear_batch_toolButton.clicked.connect(cfg.script.clear_text)
    cfg.dialog.ui.copy_script.clicked.connect(cfg.script.copy_text)
    cfg.dialog.ui.save_script_button.clicked.connect(cfg.script.save_script)

    """ Settings"""
    cfg.dialog.ui.variable_name_lineEdit.textChanged.connect(
        cfg.settings.raster_variable_name_change
    )
    cfg.dialog.ui.group_name_lineEdit.textChanged.connect(
        cfg.settings.group_name_change
    )
    cfg.dialog.ui.smtp_server_lineEdit.textChanged.connect(
        cfg.settings.smtp_server_change
    )
    cfg.dialog.ui.to_email_lineEdit.textChanged.connect(
        cfg.settings.smtp_to_emails_change
    )
    cfg.dialog.ui.smtp_user_lineEdit.editingFinished.connect(
        cfg.settings.remember_user
    )
    cfg.dialog.ui.smtp_password_lineEdit.editingFinished.connect(
        cfg.settings.remember_user
    )
    cfg.dialog.ui.remeber_settings_checkBox.stateChanged.connect(
        cfg.settings.remember_user_checkbox
    )
    cfg.dialog.ui.smtp_checkBox.stateChanged.connect(
        cfg.settings.smtp_checkbox
    )
    cfg.dialog.ui.reset_variable_name_Button.clicked.connect(
        cfg.settings.reset_raster_variable_name
    )
    cfg.dialog.ui.reset_group_name_Button.clicked.connect(
        cfg.settings.reset_group_name
    )
    cfg.dialog.ui.log_checkBox.stateChanged.connect(
        cfg.settings.log_checkbox_change
    )
    cfg.dialog.ui.download_news_checkBox.stateChanged.connect(
        cfg.settings.download_news_change
    )
    cfg.dialog.ui.sound_checkBox.stateChanged.connect(
        cfg.settings.sound_checkbox_change
    )
    cfg.dialog.ui.raster_compression_checkBox.stateChanged.connect(
        cfg.settings.raster_compression_checkbox
    )
    cfg.dialog.ui.temp_directory_Button.clicked.connect(
        cfg.settings.change_temp_dir
    )
    cfg.dialog.ui.reset_temp_directory_Button.clicked.connect(
        cfg.settings.reset_temp_dir
    )
    cfg.dialog.ui.exportLog_Button.clicked.connect(cfg.settings.copy_log_file)
    cfg.dialog.ui.test_dependencies_Button.clicked.connect(
        cfg.settings.test_dependencies
    )
    cfg.dialog.ui.RAM_spinBox.valueChanged.connect(
        cfg.settings.ram_setting_change
    )
    cfg.dialog.ui.CPU_spinBox.valueChanged.connect(
        cfg.settings.threads_setting_change
    )
    cfg.dialog.ui.gdal_path_lineEdit.textChanged.connect(
        cfg.settings.gdal_path_change
    )
    cfg.dialog.ui.change_color_Button.clicked.connect(
        cfg.settings.change_roi_color
    )
    cfg.dialog.ui.reset_color_Button.clicked.connect(
        cfg.settings.reset_roi_style
    )
    cfg.dialog.ui.transparency_Slider.valueChanged.connect(
        cfg.settings.change_roi_transparency
    )

    """ Spectral signature plot """
    cfg.spectral_plot_dlg.ui.band_lines_checkBox.stateChanged.connect(
        cfg.spectral_signature_plotter.refresh_plot
    )
    cfg.spectral_plot_dlg.ui.grid_checkBox.stateChanged.connect(
        cfg.spectral_signature_plotter.grid_checkbox
    )
    cfg.spectral_plot_dlg.ui.sigma_checkBox.stateChanged.connect(
        cfg.spectral_signature_plotter.sigma_checkbox
    )
    cfg.spectral_plot_dlg.ui.add_signature_list_pushButton.clicked.connect(
        cfg.spectral_signature_plotter.add_to_signature_list
    )
    cfg.spectral_plot_dlg.ui.remove_Signature_Button.clicked.connect(
        cfg.spectral_signature_plotter.remove_signature
    )
    cfg.spectral_plot_dlg.ui.fitToAxes_pushButton.clicked.connect(
        cfg.spectral_signature_plotter.fit_plot_to_axes
    )
    button_1 = cfg.spectral_plot_dlg.ui.calculate_spectral_distance_Button
    button_1.clicked.connect(
        cfg.spectral_signature_plotter.calculate_spectral_distances
    )
    cfg.spectral_plot_dlg.ui.plot_text_spinBox.valueChanged.connect(
        cfg.spectral_signature_plotter.set_plot_legend_length
    )
    cfg.spectral_plot_dlg.ui.save_plot_pushButton.clicked.connect(
        cfg.spectral_signature_plotter.save_plot
    )
    table_1 = cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget
    table_1.doubleClicked.connect(
        cfg.spectral_signature_plotter.signature_list_double_click
    )
    table_1.cellChanged.connect(cfg.spectral_signature_plotter.edited_cell)

    """ Scatter plot"""
    cfg.scatter_plot_dlg.ui.scatter_ROI_Button.clicked.connect(
        cfg.scatter_plotter.calculate_scatter_plot
    )
    cfg.scatter_plot_dlg.ui.bandX_spinBox.valueChanged.connect(
        cfg.scatter_plotter.band_x_plot
    )
    cfg.scatter_plot_dlg.ui.bandY_spinBox.valueChanged.connect(
        cfg.scatter_plotter.band_y_plot
    )
    table_w = cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget
    table_w.doubleClicked.connect(
        cfg.scatter_plotter.scatter_plot_double_click
    )
    cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget.cellChanged.connect(
        cfg.scatter_plotter.edited_cell
    )
    cfg.scatter_plot_dlg.ui.remove_Signature_Button.clicked.connect(
        cfg.scatter_plotter.remove_scatter
    )
    cfg.scatter_plot_dlg.ui.save_plot_pushButton_2.clicked.connect(
        cfg.scatter_plotter.save_plot
    )
    cfg.scatter_plot_dlg.ui.fitToAxes_pushButton_2.clicked.connect(
        cfg.scatter_plotter.fit_plot_to_axes
    )
    cfg.scatter_plot_dlg.ui.plot_temp_ROI_pushButton.clicked.connect(
        cfg.scatter_plotter.add_temp_roi_to_scatter_plot
    )
    cfg.scatter_plot_dlg.ui.colormap_comboBox.currentIndexChanged.connect(
        cfg.scatter_plotter.color_plot
    )
    cfg.logger.log.debug('GUI connected')


# reset all variables and interface
def reset_scp():
    cfg.logger.log.debug('reset_scp')
    cfg.ui_utils.set_interface(False)
    # clear band set
    t = cfg.dialog.ui.Band_set_tabWidget.count()
    for index in reversed(list(range(0, t))):
        cfg.bst.delete_bandset_tab(index)
    cfg.bandset_catalog = cfg.rs.bandset_catalog()
    cfg.dock_class_dlg.ui.label_48.setText(
        cfg.translate(' ROI & Signature list')
    )
    cfg.utils.refresh_vector_layer()
    # reset tabs
    count = cfg.dialog.ui.Band_set_tabWidget.count()
    for i in list(reversed(range(0, count))):
        cfg.bst.delete_bandset_tab(i)
    cfg.bst.add_band_set_tab()
    cfg.dialog.ui.Band_set_tabWidget.blockSignals(True)
    cfg.project_path = QgsProject.instance().fileName()
    cfg.last_saved_dir = path.dirname(cfg.project_path)
    cfg.util_qt.clear_table(
        cfg.spectral_plot_dlg.ui.signature_list_plot_tableWidget
    )
    cfg.util_qt.clear_table(
        cfg.scatter_plot_dlg.ui.scatter_list_plot_tableWidget
    )
    cfg.util_qt.clear_table(cfg.dialog.ui.signature_threshold_tableWidget)
    cfg.util_qt.clear_table(cfg.dialog.ui.download_images_tableWidget)
    cfg.scp_dock.TrainingVectorLayer(signature_catalog=False, output_path=None)
    # read variables
    cfg.project_registry = cfg.project_registry_default.copy()
    cfg.utils.read_project_variables()
    cfg.ui_utils.set_interface(True)
