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


""" init """
iface = map_canvas = dialog = dock_class_dlg = input_interface = utils = None
scp_dock = edit_raster = bst = mx = ui_utils = spectral_plot_dlg = None
scatter_plot_dlg = widget_dialog = settings = system_platform = logger = None
util_qgis = rs = bandset_catalog = plugin_dir = temp_dir = accuracy = None
dialog_accepted = class_report = class_vector = script = band_calc = None
cross_classification = dilation = rgb_combo = neighbor = clustering = None
reclassification = band_combination = pca_tab = vector_to_raster = sieve = None
stack_bandset = split_bands = reproject_bands = masking_bands = erosion = None
spectral_distance = raster_zonal_stats = None
image_conversion = clip_bands = clip_bands_pointer = mosaic_bandsets = None
download_products = download_products_pointer = util_qt = translate = None
classification = working_toolbar = classification_preview_pointer = None
rgb_composite = signature_threshold = calc_raster_variables = None
first_install = signature_plot = spectral_signature_plotter = None
scatter_plot = scatter_plotter = scp_processing_provider = None
signature_importer = usgs_spectral_lib = multiple_roi = None
smtp_notification = smtp_server = smtp_user = smtp_password = None
smtp_recipients = main_menu = None
# welcome url
first_reply = second_reply = second_url = None
# QGIS proxy
proxy_enabled = proxy_type = proxy_host = proxy_port = None
proxy_user = proxy_password = None
# temporary directory name
temp_dir_name = 'semiautomatic_classification'
# bandset tabs
bandset_tabs = {}
current_tab = 'bandset_tab'
variable_bandset_name = 'bandset'
# bandset virtual raster
virtual_bandset_name = bandset_tab_name = None
virtual_bandset_dict = {}
# clip rubber poly
clip_rubber_poly = download_rubber_poly = None
# empty field name
empty_field_name = 'DN'
# table object
download_table = preprocess_band_table = None
# classification preview layer
classification_preview = classifier_preview = preview_point = None
# edit raster
edit_old_array = edit_column_start = edit_row_start = None
# saved directory
last_saved_dir = ''
project_path = ''
settings_tab_index = 0
backup_name = '.backup'

""" scp dock """
scp_training = ctrl_click = temporary_roi = second_temporary_roi = None
region_growing_pointer = manual_roi_pointer = roi_map_polygon = None
roi_center_vertex = scp_dock_rubber_roi = scp_layer_name = roi_time = None
last_roi_point = None
temp_roi_name = 'temp_roi'
roi_and_signature_type = 'R&S'
roi_type = 'ROI'
signature_type = 'SIG'
roi_points = []
qgis_vertex_item_list = []
# contrast type
cumulative_cut_contrast = 'cumulative_cut'
std_dev_contrast = 'std_dev'
default_contrast = cumulative_cut_contrast

""" Spectral signature plot"""
signature_id_column_name = 'id'

""" QGIS Project variables """
project_registry = {}
# roi cursor index calculation check
reg_index_calculation_check = 'scp_roi_index_calculation_check'
project_registry[reg_index_calculation_check] = 0
# roi cursor custom index
reg_custom_index_calculation = 'scp_custom_index_calculation'
project_registry[reg_custom_index_calculation] = ''
# RGB list
reg_rgb_list = 'scp_rgb_list'
project_registry[reg_rgb_list] = ['-', '3-2-1', '4-3-2', '7-3-2']
# signature calculation check
reg_signature_calculation_check = 'scp_signature_calculation_check'
project_registry[reg_signature_calculation_check] = 2
# rapid ROI check
reg_rapid_roi_check = 'scp_rapid_roi_check'
project_registry[reg_rapid_roi_check] = 2
# automatic save training input
reg_save_training_input_check = 'scp_save_training_input_check'
project_registry[reg_save_training_input_check] = 2
# rapid ROI main band
reg_roi_main_band = 'scp_roi_main_band'
project_registry[reg_roi_main_band] = 1
# ROI max width
reg_roi_max_width = 'scp_roi_max_width'
project_registry[reg_roi_max_width] = 100
# ROI min size
reg_roi_min_size = 'scp_roi_min_size'
project_registry[reg_roi_min_size] = 60
# ROI range radius
reg_roi_range_radius = 'scp_roi_range_radius'
project_registry[reg_roi_range_radius] = 0.01
# ROI pointer custom expression
reg_roi_custom_expression = 'scp_roi_custom_expression'
project_registry[reg_roi_custom_expression] = ''
# classification preview size
reg_preview_size = 'scp_reg_preview_size'
project_registry[reg_preview_size] = 200
preview_size = 200
# ROI class id
reg_roi_class_id = 'scp_roi_class_id'
project_registry[reg_roi_class_id] = 1
# ROI class name
reg_roi_class_name = 'scp_roi_class_name'
project_registry[reg_roi_class_name] = 'Class 1'
# ROI macroclass id
reg_roi_macroclass_id = 'scp_roi_macroclass_id'
project_registry[reg_roi_macroclass_id] = 1
# ROI macroclass name
reg_roi_macroclass_name = 'scp_roi_macroclass_name'
project_registry[reg_roi_macroclass_name] = 'Macroclass 1'
# training input path
reg_training_input_path = 'scp_training_input_path'
project_registry[reg_training_input_path] = ''
# active bandset number
reg_active_bandset_number = 'scp_active_bandset_number'
project_registry[reg_active_bandset_number] = 1
# training bandset number
reg_training_bandset_number = 'scp_training_bandset_number'
project_registry[reg_training_bandset_number] = 1
# download product table
reg_download_product_table = 'scp_download_product_table'
project_registry[reg_download_product_table] = ''
# bandset count
reg_bandset_count = 'scp_bandset_count'
project_registry[reg_bandset_count] = 1
project_registry_default = project_registry.copy()

""" bandset registry standard """
reg_bandset = 'SemiAutomaticClassification_Plugin/scp_bandset_'

""" QGIS registry keys """
qgis_registry = {}
# first installation
reg_first_install = 'SemiAutomaticClassification_Plugin/first_install'
# log setting
reg_log_key = 'SemiAutomaticClassification_Plugin/log_setting'
qgis_registry[reg_log_key] = 0
# sound
reg_sound = 'SemiAutomaticClassification_Plugin/use_sound'
qgis_registry[reg_sound] = 2
# registry key for temporary directory
reg_temp_dir = 'SemiAutomaticClassification_Plugin/temp_dir'
# registry key for RAM value setting
reg_ram_value = 'SemiAutomaticClassification_Plugin/ram_value'
qgis_registry[reg_ram_value] = 512
# registry key for CPU threads value setting
reg_threads_value = 'SemiAutomaticClassification_Plugin/threads_value'
qgis_registry[reg_threads_value] = 2
reg_earthdata_user = 'SemiAutomaticClassificationPlugin/earthdata_user'
qgis_registry[reg_earthdata_user] = ''
reg_earthdata_pass = 'SemiAutomaticClassificationPlugin/earthdata_pass'
qgis_registry[reg_earthdata_pass] = ''
reg_copernicus_user = 'SemiAutomaticClassificationPlugin/copernicus_user'
qgis_registry[reg_copernicus_user] = ''
reg_copernicus_pass = 'SemiAutomaticClassificationPlugin/copernicus_pass'
qgis_registry[reg_copernicus_pass] = ''
# registry key for ROI color setting
reg_roi_color = 'SemiAutomaticClassificationPlugin/roi_color'
roi_color_default = '#ffaa00'
qgis_registry[reg_roi_color] = roi_color_default
# registry key for ROI transparency setting
reg_roi_transparency = 'SemiAutomaticClassificationPlugin/roi_transparency'
roi_transparency_default = 45
qgis_registry[reg_roi_transparency] = roi_transparency_default
# registry key for ROI transparency setting
reg_max_train_buffer = 'SemiAutomaticClassificationPlugin/max_train_buffer'
max_train_buffer_default = 5
qgis_registry[reg_max_train_buffer] = max_train_buffer_default
# gdal path setting
reg_gdal_path = 'SemiAutomaticClassificationPlugin/gdal_path'
qgis_registry[reg_gdal_path] = ''
reg_download_news = 'SemiAutomaticClassificationPlugin/download_news'
qgis_registry[reg_download_news] = 2
reg_raster_compression = 'SemiAutomaticClassificationPlugin/raster_compression'
qgis_registry[reg_raster_compression] = 2
# smtp server
reg_smtp_check = 'SemiAutomaticClassificationPlugin/smtp_check'
qgis_registry[reg_smtp_check] = 2
reg_smtp_server = 'SemiAutomaticClassificationPlugin/smtp_server'
qgis_registry[reg_smtp_server] = ''
reg_smtp_emails = 'SemiAutomaticClassificationPlugin/smtp_emails'
qgis_registry[reg_smtp_emails] = ''
reg_smtp_user = 'SemiAutomaticClassificationPlugin/smtp_user'
qgis_registry[reg_smtp_user] = ''
reg_smtp_password = 'SemiAutomaticClassificationPlugin/smtp_password'
qgis_registry[reg_smtp_password] = ''
# raster variable name
reg_raster_variable_name = 'SemiAutomaticClassificationPlugin/raster_var_name'
raster_variable_name_def = 'raster'
qgis_registry[reg_raster_variable_name] = raster_variable_name_def
# group name
reg_group_name = 'SemiAutomaticClassificationPlugin/group_name'
group_name_def = 'scp_class_temp_group'
qgis_registry[reg_group_name] = group_name_def
# band calc functions
reg_custom_functions = 'SemiAutomaticClassificationPlugin/custom_functions'
custom_functions_def = []
qgis_registry[reg_custom_functions] = custom_functions_def
# window size
reg_window_size_w = 'SemiAutomaticClassificationPlugin/window_size_width'
qgis_registry[reg_window_size_w] = 700
reg_window_size_h = 'SemiAutomaticClassificationPlugin/window_size_height'
qgis_registry[reg_window_size_h] = 500
reg_splitter_sizes = 'SemiAutomaticClassificationPlugin/splitter_sizes'
qgis_registry[reg_splitter_sizes] = [100, 100]

""" band calc """
map_extent = '\'Map extent\''
union_extent = '\'Union\''
intersection_extent = '\'Intersection\''
custom_extent = '\'Custom\''
default_align = '\'Default\''
band_calc_functions = [
    ['+', ' + '], ['-', ' - '], ['/', ' / '], ['*', ' * '], ['==', ' == '],
    ['!=', ' != '], ['<', ' < '], ['>', ' > '], ['(', '('], [')', ')'],
    ['^', '^'], ['√', 'sqrt('], ['Conditional'], ['where', 'where('],
    ['Logical'], ['AND', '&'], ['OR', '|'], ['XOR', '^'], ['NOT', '~'],
    ['Statistics'], ['max', 'max('], ['min', 'min('], ['mean', 'mean('],
    ['median', 'median('], ['percentile', 'percentile('], ['std', 'std('],
    ['sum', 'sum('], ['Operations'], ['sin', 'sin('], ['cos', 'cos('],
    ['tan', 'tan('], ['asin', 'asin('], ['acos', 'acos('], ['atan', 'atan('],
    ['exp', 'exp('], ['ln', 'ln('], ['log10', 'log10('], ['Indices'],
    ['NDVI', '( "#NIR#" - "#RED#" ) / ( "#NIR#" + "#RED#" ) @NDVI'],
    ['EVI', '2.5# ( "#NIR#" - "#RED#" ) / '
            '( "#NIR#" + 6# "#RED#" - 7.5# "#BLUE#" + 1) @EVI'
     ], ['NBR', '( "#NIR#" - "#SWIR2#" ) / ( "#NIR#" + "#SWIR2#" ) @NBR'],
    ['Variables'], ['nodata', 'nodata('],
    ['forbandsets', 'forbandsets[ ]'],
    ['forbandsinbandset', 'forbandsinbandset[ ]'],
    ['#BAND#', '#BAND#'], ['#BANDSET#', '#BANDSET#'],
    ['#DATE#', '#DATE#'], ['@', '@'], ['Custom']
]

""" Scatter plot """
# noinspection SpellCheckingInspection
scatter_color_map = [
    '', 'rainbow', 'gist_rainbow', 'jet', 'afmhot', 'bwr', 'gnuplot',
    'gnuplot2', 'BrBG', 'coolwarm', 'PiYG', 'PRGn', 'PuOr', 'RdBu', 'RdGy',
    'RdYlBu', 'RdYlGn', 'Spectral', 'seismic', 'ocean', 'terrain', 'Blues',
    'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu',
    'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr',
    'YlOrRd'
]
