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


import numpy as np
from osgeo import gdal, ogr, osr

cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

""" GDAL functions """


# read a block of band as array
def read_array_block(
        gdal_band, start_column, start_row, block_columns, block_rows,
        calc_data_type=None
):
    if calc_data_type is None:
        calc_data_type = np.float32
    try:
        offset = gdal_band.GetOffset()
        scale = gdal_band.GetScale()
        if offset is None:
            offset = 0.0
        if scale is None:
            scale = 1.0
    except Exception as err:
        str(err)
        offset = 0.0
        scale = 1.0
    offset = np.asarray(offset).astype(calc_data_type)
    scale = np.asarray(scale).astype(calc_data_type)
    try:
        array = np.asarray(
            gdal_band.ReadAsArray(
                start_column, start_row, block_columns, block_rows
            ) * scale + offset
        ).astype(calc_data_type)
    except Exception as err:
        str(err)
        return None
    return array


# read raster
def read_raster(raster_path):
    _r_d = gdal.Open(raster_path, gdal.GA_ReadOnly)
    if _r_d is None:
        return False
    x_count = _r_d.RasterXSize
    y_count = _r_d.RasterYSize
    band = _r_d.GetRasterBand(1)
    data_type = gdal.GetDataTypeName(band.DataType)
    calc_data_type = cfg.rs.shared_tools.data_type_conversion(data_type)
    scale = band.GetScale()
    if scale is not None:
        if scale < 1 or scale > 1:
            calc_data_type = np.float32
    r_array = read_array_block(
        gdal_band=band, start_column=0, start_row=0, block_columns=x_count,
        block_rows=y_count, calc_data_type=calc_data_type
    )
    return r_array


# Get pixel size of a raster
def get_pixel_size(path):
    # open input_raster
    _input_raster = gdal.Open(path, gdal.GA_ReadOnly)
    # get input_raster geotransformation
    gt = _input_raster.GetGeoTransform()
    p_x_size = abs(gt[1])
    p_y_size = abs(gt[5])
    _input_raster = None
    return p_x_size, p_y_size


# Get CRS of a raster or vector
def get_crs_gdal(path):
    # try vector
    opened_vector = ogr.Open(path)
    # if raster
    if opened_vector is None:
        opened_vector = gdal.Open(path, gdal.GA_ReadOnly)
        if opened_vector is None:
            crs = None
        else:
            try:
                # check projections
                crs = opened_vector.GetProjection()
                crs = crs.replace(' ', '')
                if len(crs) == 0:
                    crs = None
            except Exception as err:
                str(err)
                crs = None
    # if vector
    else:
        layer = opened_vector.GetLayer()
        # check projection
        proj = layer.GetSpatialRef()
        try:
            crs = proj.ExportToWkt()
            crs = crs.replace(' ', '')
            if len(crs) == 0:
                crs = None
        except Exception as err:
            str(err)
            crs = None
    return crs


# compare two crs
def compare_crs(first_crs, second_crs):
    try:
        first_sr = osr.SpatialReference()
        first_sr.ImportFromWkt(first_crs)
        second_sr = osr.SpatialReference()
        second_sr.ImportFromWkt(second_crs)
        if first_sr.IsSame(second_sr) == 1:
            same = True
        else:
            same = False
        return same
    except Exception as err:
        str(err)
        return False


# Get GDAL version
def get_gdal_version():
    v = gdal.VersionInfo('RELEASE_NAME').split('.')
    return v


# create a polygon shapefile with OGR
def create_empty_shapefile_ogr(
        crs_wkt, output_path, vector_format='ESRI Shapefile'
):
    try:
        crs_wkt = str(crs_wkt.toWkt())
    except Exception as err:
        str(err)
    driver = ogr.GetDriverByName(vector_format)
    _source = driver.CreateDataSource(output_path)
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromWkt(crs_wkt)
    name = cfg.rs.files_directories.file_name(output_path)
    _layer = _source.CreateLayer(
        name, spatial_reference, ogr.wkbMultiPolygon
    )
    field = ogr.FieldDefn(cfg.empty_field_name, ogr.OFTInteger)
    _layer.CreateField(field)
    _layer = None
    _source = None
    cfg.logger.log.debug('create_vector_ogr: %s' % output_path)


# create a polygon gpkg with OGR
def create_vector_ogr(crs_wkt, output_path, vector_format='GPKG'):
    try:
        crs_wkt = str(crs_wkt.toWkt())
    except Exception as err:
        str(err)
    driver = ogr.GetDriverByName(vector_format)
    _source = driver.CreateDataSource(output_path)
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromWkt(crs_wkt)
    name = cfg.rs.files_directories.file_name(output_path)
    _layer = _source.CreateLayer(name, spatial_reference, ogr.wkbMultiPolygon)
    field = ogr.FieldDefn(cfg.empty_field_name, ogr.OFTInteger)
    _layer.CreateField(field)
    _layer = None
    _source = None
    cfg.logger.log.debug('create_vector_ogr: %s' % output_path)


# Get field names of a vector
def vector_fields(path):
    _s = ogr.Open(path)
    _layer = _s.GetLayer()
    definition = _layer.GetLayerDefn()
    fields = [definition.GetFieldDefn(i).GetName() for i in
              range(definition.GetFieldCount())]
    _layer = None
    _s = None
    return fields


# Open a vector
def open_vector(path):
    _s = ogr.Open(path)
    return _s


# get polygon from vector and return memory layer
def get_polygon_from_vector(vector_path, output, attribute_filter=None):
    # open input vector
    vector = ogr.Open(vector_path)
    # get layer
    try:
        _v_layer = vector.GetLayer()
    except Exception as err:
        str(err)
        return False
    # attribute filter
    _v_layer.SetAttributeFilter(attribute_filter)
    d = ogr.GetDriverByName('GPKG')
    _d_s = d.CreateDataSource(output)
    _d_s.CopyLayer(_v_layer, _v_layer.GetName(), ['OVERWRITE=YES'])
    _v_layer = None
    _d_s = None
    return output
