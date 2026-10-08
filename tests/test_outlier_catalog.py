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
# Outlier catalog tests.
# Unit tests for the catalog operations in core/outlier_catalog.py.
# The core module is independent of QGIS, so it is tested without launching
# QGIS. The tests build their own GeoPackage, once in GDAL memory and once on
# disk, so that both kinds of path are verified on real data sources instead of
# on a mock.
# Run with: python3 -m unittest discover -s tests -v
import os
import sys
import tempfile
import unittest

from osgeo import gdal, ogr, osr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import outlier_catalog

EPSG_CODE = 32633
SIDE = 10.0                     # 10 x 10 map unit square
MEMORY_PATH = "/vsimem/test_outlier_catalog.gpkg"


class _Catalog:
    # Stands in for a signature catalog: only the geometry path matters here.

    def __init__(self, geometry_file):
        self.geometry_file = geometry_file


def synthetic_geopackage(path):
    # Returns the path of a GeoPackage holding a single ROI, in the layout the
    # catalog operations expect: one polygon identified by a roi_id field.
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromEPSG(EPSG_CODE)
    data_source = ogr.GetDriverByName("GPKG").CreateDataSource(path)
    layer = data_source.CreateLayer("roi", srs=spatial_reference,
                                    geom_type=ogr.wkbPolygon)
    layer.CreateField(ogr.FieldDefn("roi_id", ogr.OFTString))
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetField("roi_id", "sig1")
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for x, y in ((0, 0), (SIDE, 0), (SIDE, SIDE), (0, SIDE), (0, 0)):
        ring.AddPoint(x, y)
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    feature.SetGeometry(polygon)
    layer.CreateFeature(feature)
    data_source.FlushCache()
    del data_source
    return path


class TestMaterializeGeometryFile(unittest.TestCase):
    # SCP 9.0 copies the catalog geometry to a /vsimem path, which belongs to
    # the calling process only. Classification reads the ROIs in worker
    # processes, so a cleaned catalog has to carry its geometry on disk.

    def setUp(self):
        self.temporary_files = []

    def tearDown(self):
        for path in self.temporary_files:
            if os.path.isfile(path):
                os.remove(path)

    def temporary_path(self):
        # Mimics a Remotior Sensus temporary path: an unused name that
        # the caller is free to create.
        handle, path = tempfile.mkstemp(suffix=".gpkg")
        os.close(handle)
        os.remove(path)
        self.temporary_files.append(path)
        return path

    def test_memory_geometry_is_moved_to_a_real_file(self):
        synthetic_geopackage(MEMORY_PATH)
        catalog = _Catalog(MEMORY_PATH)
        result = outlier_catalog.materialize_geometry_file(
            catalog, temp_path_fn=self.temporary_path
        )
        self.assertEqual(catalog.geometry_file, result)
        self.assertNotIn("vsimem", catalog.geometry_file)
        self.assertTrue(os.path.isfile(catalog.geometry_file))
        # the ROI survives the move
        data_source = ogr.Open(catalog.geometry_file)
        self.assertEqual(data_source.GetLayer().GetFeatureCount(), 1)
        del data_source
        # the copy in memory is released
        self.assertIsNone(gdal.VSIStatL(MEMORY_PATH))

    def test_file_geometry_is_left_untouched(self):
        # A geometry that already lives on disk is kept as it is.
        path = synthetic_geopackage(self.temporary_path())
        catalog = _Catalog(path)
        result = outlier_catalog.materialize_geometry_file(
            catalog, temp_path_fn=self.temporary_path
        )
        self.assertEqual(result, path)
        self.assertEqual(catalog.geometry_file, path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
