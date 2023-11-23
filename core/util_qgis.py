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


from qgis.core import (
    QgsProject, QgsVectorFileWriter, QgsLayerTreeNode, QgsMapLayer,
    QgsRasterMinMaxOrigin, QgsContrastEnhancement, QgsRectangle, QgsPointXY,
    QgsVectorLayer, QgsFillSymbol, QgsFeatureRequest, QgsWkbTypes,
    QgsCoordinateReferenceSystem
)

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])


# get QGIS project instance
def get_qgis_project():
    return QgsProject.instance()


# get QGIS map raster layer
def get_qgis_map_raster():
    return QgsMapLayer.RasterLayer


# get QGIS map vector layer
def get_qgis_map_vector():
    return QgsMapLayer.VectorLayer


# get QGIS wkb types
def get_qgis_wkb_types():
    return QgsWkbTypes


# get QGIS Proxy settings
def get_qgis_proxy_settings():
    cfg.proxy_enabled = cfg.util_qt.read_registry_keys(
        'proxy/proxyEnabled', ''
    )
    cfg.proxy_type = cfg.util_qt.read_registry_keys('proxy/proxyType', '')
    cfg.proxy_host = cfg.util_qt.read_registry_keys('proxy/proxyHost', '')
    cfg.proxy_port = cfg.util_qt.read_registry_keys('proxy/proxyPort', '')
    cfg.proxy_user = cfg.util_qt.read_registry_keys('proxy/proxyUser', '')
    cfg.proxy_password = cfg.util_qt.read_registry_keys(
        'proxy/proxyPassword', ''
    )


# Get CRS of a layer by name thereof
def get_crs_qgis(layer):
    if layer is None:
        crs = None
    else:
        provider = layer.dataProvider()
        crs = provider.crs()
    return crs


# save memory layer to file
def save_memory_layer_to_geopackage(memory_layer, output):
    try:
        # QGIS > 3.20
        writer = QgsVectorFileWriter.writeAsVectorFormatV3
    except Exception as err:
        str(err)
        # QGIS < 3.20
        writer = QgsVectorFileWriter.writeAsVectorFormatV2
    save_vector_options = QgsVectorFileWriter.SaveVectorOptions()
    save_vector_options.driverName = 'GPKG'
    writer(
        layer=memory_layer, fileName=output,
        transformContext=get_qgis_project().transformContext(),
        options=save_vector_options
    )


# save memory layer to file
def save_qgis_memory_layer_to_file(
        memory_layer, output, name=None, file_format='ESRI Shapefile',
        id_list=None, field_name_list=None
):
    try:
        cfg.util_gdal.create_vector_ogr(
            memory_layer.crs(), output, vector_format=file_format
        )
        if name is None:
            name = cfg.rs.files_directories.file_name(output, suffix=True)
        vector = add_vector_layer(output, name)
        vector.updateFields()
        vector.startEditing()
        if id_list is None:
            for feature in memory_layer.getFeatures():
                vector.addFeature(feature)
        else:
            for feature in memory_layer.getFeatures():
                field = str(feature[field_name_list])
                if field in id_list:
                    vector.addFeature(feature)
        vector.commitChanges()
        vector.updateExtents()
        remove_layer_by_layer(vector)
        cfg.logger.log.debug('save_qgis_memory_layer_to_file: %s' % output)
        return True
    except Exception as err:
        cfg.logger.log.error(str(err))
        return False


# Find group by its name
def group_index(group_name):
    root = get_qgis_project().layerTreeRoot()
    group = root.findGroup(group_name)
    return group


# Layer ID by name thereof
def get_layer_id_by_name(layer_name):
    layers = get_qgis_project().mapLayers().values()
    for layer in layers:
        name = layer.name()
        if name == layer_name:
            return layer.id()


# read project variable
def read_project_variable(variable_name, value):
    value = get_qgis_project().readEntry(
        'SemiAutomaticClassificationPlugin',
        variable_name, str(value)
    )[0]
    cfg.util_qt.process_events()
    try:
        value = int(value)
    except Exception as err:
        str(err)
        try:
            value = eval(value)
        except Exception as err:
            str(err)
    return value


# write project variable
def write_project_variable(variable_name, value):
    get_qgis_project().writeEntry(
        'SemiAutomaticClassificationPlugin',
        variable_name, str(value)
    )
    cfg.util_qt.process_events()
    return True


# Remove layer from map
def remove_layer_by_name(layer_name):
    try:
        get_qgis_project().removeMapLayer(
            get_layer_id_by_name(layer_name)
        )
    except Exception as err:
        str(err)


# Remove layer from map
def remove_layer_by_layer(layer):
    try:
        get_qgis_project().removeMapLayer(layer.id())
    except Exception as err:
        str(err)


# Create group
def create_group(group_name):
    root = get_qgis_project().layerTreeRoot()
    group = root.insertGroup(0, group_name)
    return group


# Remove layer from map
def remove_group(group_name):
    root = get_qgis_project().layerTreeRoot()
    group = root.findGroup(group_name)
    try:
        if group is not None:
            root.removeChildNode(group)
    except Exception as err:
        str(err)


# Set group visible
def set_group_visible(group_id, visible=False):
    try:
        QgsLayerTreeNode.setItemVisibilityChecked(group_id, visible)
    except Exception as err:
        str(err)


# Set group expanded
def set_group_expanded(group_id, expanded=False):
    try:
        QgsLayerTreeNode.setExpanded(group_id, expanded)
    except Exception as err:
        str(err)


# Move layer to top layers
def move_layer_to_top(layer):
    try:
        root = get_qgis_project().layerTreeRoot()
        layer = root.findLayer(layer.id())
        parent = layer.parent()
        layer_clone = layer.clone()
        root.insertChildNode(0, layer_clone)
        parent.removeChildNode(layer)
    except Exception as err:
        str(err)


# Move layer in group
def move_layer(layer, group_name):
    try:
        root = get_qgis_project().layerTreeRoot()
        layer_x = root.findLayer(layer.id())
        group = root.findGroup(group_name)
        group.insertLayer(0, layer)
        root.removeChildNode(layer_x)
    except Exception as err:
        str(err)


# Set layer visible
def set_layer_visible(layer, visible=True):
    root = get_qgis_project().layerTreeRoot()
    layer_x = root.findLayer(layer.id())
    QgsLayerTreeNode.setItemVisibilityChecked(layer_x, visible)


# Refresh layer symbology
def refresh_layer_symbology(layer):
    root = get_qgis_project().layerTreeRoot()
    model = cfg.iface.layerTreeView().model()
    try:
        layer_x = root.findLayer(layer.id())
        model.refreshLayerLegend(layer_x)
    except Exception as err:
        str(err)
        cfg.iface.layerTreeView().refreshLayerSymbology(layer.id())


# Select layer by name thereof
def select_layer_by_name(layer_name, filter_raster=None):
    layers = get_qgis_project().mapLayers().values()
    for layer in layers:
        layer_x_name = layer.name()
        if layer_x_name == layer_name:
            if filter_raster is None:
                return layer
            else:
                try:
                    if layer.type().value == 1:
                        return layer
                except Exception as err:
                    str(err)
                    if layer.type() == QgsMapLayer.RasterLayer:
                        return layer


# file path
def get_file_path(layer_name):
    try:
        layer = select_layer_by_name(layer_name)
        path = cfg.util_qgis.qgis_layer_source(layer)
        return path
    except Exception as err:
        str(err)


# set map extent from layer
def set_map_extent_from_layer(layer):
    ext = layer.extent()
    upper_left_point = create_qgis_point(ext.xMinimum(), ext.yMaximum())
    lower_right_point = create_qgis_point(ext.xMaximum(), ext.yMinimum())
    point_1 = upper_left_point
    point_2 = lower_right_point
    # project extent
    crs = get_crs_qgis(layer)
    qgis_crs = get_qgis_crs()
    if crs is None:
        crs = qgis_crs
    # projection of input point from raster's crs to project's crs
    if qgis_crs != crs:
        try:
            point_1 = cfg.utils.project_qgis_point_coordinates(
                upper_left_point, crs, qgis_crs
            )
            point_2 = cfg.utils.project_qgis_point_coordinates(
                lower_right_point, crs, qgis_crs
            )
            if point_1 is False:
                point_1 = upper_left_point
                point_2 = lower_right_point
        # Error latitude or longitude exceeded limits
        except Exception as err:
            str(err)
            point_1 = upper_left_point
            point_2 = lower_right_point
    cfg.map_canvas.setExtent(QgsRectangle(point_1, point_2))


# save a qml style
def save_qml_style(layer, style_path):
    layer.saveNamedStyle(style_path)


# edit features of layer
def edit_layer_features(layer, expression, field_name, value):
    if layer is not None:
        layer.removeSelection()
        layer.startEditing()
        layer.selectByExpression(expression)
        fields = layer.fields()
        for feature in layer.selectedFeatures():
            layer.changeAttributeValue(
                feature.id(), fields.indexFromName(field_name), value
            )
        layer.commitChanges()
        layer.removeSelection()
        return True
    else:
        return False


# zoom to band set
def zoom_to_bandset():
    bandset_number = cfg.project_registry[cfg.reg_active_bandset_number]
    bandset_x = cfg.bandset_catalog.get(bandset_number)
    band_count = bandset_x.get_band_count()
    if band_count == 0:
        return
    try:
        crs = cfg.bandset_catalog.get_bandset(bandset_number).bands[0].crs
        left = cfg.bandset_catalog.get_bandset(bandset_number).bands[0].left
        top = cfg.bandset_catalog.get_bandset(bandset_number).bands[0].top
        right = cfg.bandset_catalog.get_bandset(bandset_number).bands[0].right
        bottom = cfg.bandset_catalog.get_bandset(bandset_number).bands[
            0].bottom
        upper_left_point = create_qgis_point(left, top)
        lower_right_point = create_qgis_point(right, bottom)
        point_1 = upper_left_point
        point_2 = lower_right_point
    except Exception as err:
        cfg.logger.log.error(str(err))
        return
    qgis_crs = get_qgis_crs()
    if crs is None:
        crs = qgis_crs
    # projection of input point from raster's crs to project's crs
    if cfg.util_gdal.compare_crs(crs, qgis_crs) is False:
        try:
            point_1 = cfg.utils.project_qgis_point_coordinates(
                upper_left_point, crs, qgis_crs
            )
            point_2 = cfg.utils.project_qgis_point_coordinates(
                lower_right_point, crs, qgis_crs
            )
            if point_1 is False:
                point_1 = upper_left_point
                point_2 = lower_right_point
        # Error latitude or longitude exceeded limits
        except Exception as err:
            str(err)
            point_1 = upper_left_point
            point_2 = lower_right_point
    cfg.map_canvas.setExtent(QgsRectangle(point_1, point_2))

    cfg.map_canvas.refresh()


# Add layer to map
def add_layer_to_map(layer):
    get_qgis_project().addMapLayers([layer])


# Add layer
def add_vector_layer(path, name=None, vector_format=None):
    if name is None:
        name = cfg.rs.files_directories.file_name(path)
    if vector_format is None:
        vector_format = 'ogr'
    layer = QgsVectorLayer(path, name, vector_format)
    return layer


# add raster layer
def add_raster_layer(path, name=None):
    if cfg.utils.check_file(path):
        if name is None:
            name = cfg.rs.files_directories.file_name(path)
        raster = cfg.iface.addRasterLayer(path, name)
        raster.setName(name)
        return raster
    else:
        return False


# Get QGIS project CRS
def get_qgis_crs():
    crs = cfg.map_canvas.mapSettings().destinationCrs()
    return crs


# Set QGIS project CRS
def set_qgis_crs(crs):
    cfg.map_canvas.setDestinationCrs(crs)


# create QGIS point
def create_qgis_point(x, y):
    return QgsPointXY(x, y)


# create reference system from wkt string
def create_qgis_reference_system_from_wkt(wkt):
    return QgsCoordinateReferenceSystem.fromWkt(wkt)


# layer source
def qgis_layer_source(layer):
    source = layer.source().split("|layername=")[0]
    return source


# set layer color for ROIs
def training_symbol(layer):
    style = {
        'color': '0,0,0,230', 'color_border': '255,255,255,230',
        'style': 'solid', 'style_border': 'dash'
    }
    symbol = QgsFillSymbol.createSimple(style)
    renderer = layer.renderer()
    renderer.setSymbol(symbol)
    refresh_layer_symbology(layer)


# get ID by attributes
def get_id_by_attributes(layer, field, attribute):
    ids = []
    features = layer.getFeatures(
        QgsFeatureRequest().setFilterExpression(
            '"%s" = \'%s\'' % (str(field), str(attribute))
        )
    )
    for feature in features:
        ids.append(feature.id())
    return ids


# Get last feature id
def get_last_feature_id(layer):
    *_, last_feature = layer.getFeatures()
    return last_feature.id()


# Get a feature from a shapefile by feature ID
def get_feature_by_id(layer, feature_id):
    feature_filter = QgsFeatureRequest().setFilterFid(feature_id)
    try:
        feature = layer.getFeatures(feature_filter)
        return next(feature)
    except Exception as err:
        str(err)
        return False


# copy feature by ID to layer
def copy_feature_to_qgis_layer(source_layer, feature_id, target_layer):
    feature = get_feature_by_id(source_layer, feature_id)
    # get geometry
    geometry = feature.geometry()
    feature.setGeometry(geometry)
    try:
        fields = target_layer.fields()
        feature.initAttributes(fields.count())
        if feature.hasGeometry() is not True:
            pass
        else:
            # copy polygon to vector
            target_layer.startEditing()
            target_layer.addFeature(feature)
            target_layer.commitChanges()
            target_layer.dataProvider().createSpatialIndex()
            target_layer.updateExtents()
    except Exception as err:
        str(err)


# set raster color composite
def set_raster_color_composite(
        raster, red_band_number, green_band_number, blue_band_number
):
    raster.renderer().setRedBand(red_band_number)
    raster.renderer().setGreenBand(green_band_number)
    raster.renderer().setBlueBand(blue_band_number)
    set_raster_contrast_enhancement(raster, cfg.default_contrast)


# set raster enhancement
def set_raster_contrast_enhancement(
        qgis_raster_layer, contrast_type=None
):
    if contrast_type is None:
        contrast_type = cfg.cumulative_cut_contrast
    extent = cfg.map_canvas.extent()
    top_left_point = create_qgis_point(extent.xMinimum(), extent.yMaximum())
    lower_right_point = create_qgis_point(extent.xMaximum(), extent.yMinimum())
    point_1 = top_left_point
    point_2 = lower_right_point
    # raster crs
    raster_crs = get_crs_qgis(qgis_raster_layer)
    # project crs
    project_crs = get_qgis_crs()
    if raster_crs is None:
        raster_crs = project_crs
    # projection of input point from project's crs to raster's crs
    if project_crs != raster_crs:
        try:
            point_1 = cfg.utils.project_qgis_point_coordinates(
                top_left_point, project_crs, raster_crs
            )
            point_2 = cfg.utils.project_qgis_point_coordinates(
                lower_right_point, project_crs, raster_crs
            )
            if point_1 is False:
                point_1 = top_left_point
                point_2 = lower_right_point
        # Error latitude or longitude exceeded limits
        except Exception as err:
            str(err)
            point_1 = top_left_point
            point_2 = lower_right_point
    if contrast_type == cfg.std_dev_contrast:
        contrast = QgsRasterMinMaxOrigin.StdDev
    elif contrast_type == cfg.cumulative_cut_contrast:
        contrast = QgsRasterMinMaxOrigin.CumulativeCut
    else:
        contrast = QgsRasterMinMaxOrigin.StdDev
    try:
        qgis_raster_layer.setContrastEnhancement(
            QgsContrastEnhancement.StretchToMinimumMaximum, contrast,
            QgsRectangle(point_1, point_2)
        )
        qgis_raster_layer.triggerRepaint()
    except Exception as err:
        cfg.logger.log.error(str(err))


# set local cumulative cut stretch
def set_raster_cumulative_stretch():
    if (cfg.project_registry[cfg.reg_active_bandset_number]
            in cfg.virtual_bandset_dict):
        layer = cfg.virtual_bandset_dict[
            cfg.project_registry[cfg.reg_active_bandset_number]
        ]
        set_raster_contrast_enhancement(layer, cfg.cumulative_cut_contrast)
        cfg.default_contrast = cfg.cumulative_cut_contrast


# set local standard deviation stretch
def set_raster_std_dev_stretch():
    if (cfg.project_registry[cfg.reg_active_bandset_number]
            in cfg.virtual_bandset_dict):
        layer = cfg.virtual_bandset_dict[
            cfg.project_registry[cfg.reg_active_bandset_number]
        ]
        set_raster_contrast_enhancement(layer, cfg.std_dev_contrast)
        cfg.default_contrast = cfg.std_dev_contrast
