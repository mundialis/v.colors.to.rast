#!/usr/bin/env python3

############################################################################
#
# MODULE:       v.colors.to.rast test
#
# AUTHOR(S):    Anika Weinmann
#
# PURPOSE:      Tests v.colors.to.rast inputs.
#               Uses NC full sample data set.
#
# COPYRIGHT:    (C) 2020-2022 by mundialis GmbH & Co. KG and the GRASS Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#############################################################################

import os

from grass.gunittest.case import TestCase
from grass.gunittest.main import test
from grass.gunittest.gmodules import SimpleModule


class TestVColorsToRast(TestCase):
    map = "landclass96"
    refmap_file = "data/ref_dataset_landclass96_epsg4326.geojson"
    ref_column_cat = "classname"
    ref_column_values = "classnum"
    ref_column_values_with_dash = "class-Num"
    ref_column_notexisting = "not_existing_categories"
    color_column = "color"
    ref_color = "1 255:127:0\n2 255:255:0\n3 200:255:0\n4 0:255:0\n5 20:130:70\n6 0:191:191\n7 191:127:63\nnv 255:255:255\ndefault 255:255:255\n"
    red_color = "1 255:255:255\n7 255:0:0\nnv 255:255:255\ndefault 255:255:255\n"
    pid_str = str(os.getpid())
    refmap = "refmap_%s" % pid_str
    tmpmap = "map_copy_%s" % pid_str
    region = "region_%s" % pid_str

    @classmethod
    def setUpClass(self):
        """Ensures expected computational region and generated data"""
        # import general area
        self.runModule("v.import", input=self.refmap_file, output=self.refmap)
        # set temp region
        self.runModule("g.region", save=self.region)
        # set region to area
        self.runModule("g.region", raster=self.map)
        # copy map
        self.runModule("g.copy", raster=[self.map, self.tmpmap])

    @classmethod
    def tearDownClass(self):
        """Remove the temporary region and generated data"""
        self.runModule("g.remove", type="raster", name=self.tmpmap, flags="f")
        self.runModule("g.remove", type="vector", name=self.refmap, flags="f")
        self.runModule("g.region", region=self.region)
        self.runModule("g.remove", type="region", name=self.region, flags="f")

    # def tearDown(self):
    #     """Remove the outputs created
    #     This is executed after each test run.
    #     """
    #     self.runModule(
    #         'g.remove', type='vector', name=self.vectormap, flags='f')

    def compare_color(self, color):
        """ """
        r_colors_out = SimpleModule("r.colors.out", map=self.tmpmap)
        self.assertModule(r_colors_out)
        stdout = r_colors_out.outputs.stdout
        self.assertTrue(stdout)
        self.assertEquals(color, stdout)

    def set_red_color(self):
        """Set raster color to red"""
        # set raster color to red
        self.runModule("r.colors", map=self.tmpmap, color="reds")
        self.compare_color(self.red_color)

    def test_color_with_category_use(self):
        """Test color with using category values"""
        # set color to red
        self.set_red_color()

        # test v.colors.to.rast
        v_colors_to_rast = SimpleModule(
            "v.colors.to.rast",
            map=self.tmpmap,
            referencemap=self.refmap,
            color_column=self.color_column,
            class_column=self.ref_column_cat,
        )
        self.assertModule(v_colors_to_rast)
        # test that error output is not empty
        stderr = v_colors_to_rast.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertEquals(
            "Using colors from column <%s>\nColor set\n" % (self.color_column), stderr
        )
        # compare colors
        self.compare_color(self.ref_color)

    def test_color_without_category_use(self):
        """Test color without using category values"""
        # set color to red
        self.set_red_color()

        # test v.colors.to.rast
        v_colors_to_rast = SimpleModule(
            "v.colors.to.rast",
            map=self.tmpmap,
            referencemap=self.refmap,
            color_column=self.color_column,
            class_column=self.ref_column_values,
        )
        self.assertModule(v_colors_to_rast)
        # test that error output is not empty
        stderr = v_colors_to_rast.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertEquals(
            "Using colors from column <%s>\nColor set\n" % (self.color_column), stderr
        )
        # compare colors
        self.compare_color(self.ref_color)

    def test_color_with_notexisting_category_use_error(self):
        """Test color with not existing category values"""
        # set color to red
        self.set_red_color()

        # test v.colors.to.rast
        v_colors_to_rast = SimpleModule(
            "v.colors.to.rast",
            map=self.tmpmap,
            referencemap=self.refmap,
            color_column=self.color_column,
            class_column=self.ref_column_notexisting,
        )
        self.assertModuleFail(v_colors_to_rast)
        # test that error output is not empty
        stderr = v_colors_to_rast.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertEquals(
            "Using colors from column <%s>\nFEHLER: Class <water> is not in reference map <%s>\n"
            % (self.color_column, self.refmap),
            stderr,
        )
        # compare colors
        self.compare_color(self.red_color)

    def test_color_without_category_with_dash(self):
        """Test color without using category values with dash in reference column"""
        # set color to red
        self.set_red_color()

        # test v.colors.to.rast
        v_colors_to_rast = SimpleModule(
            "v.colors.to.rast",
            map=self.tmpmap,
            referencemap=self.refmap,
            color_column=self.color_column,
            class_column=self.ref_column_values_with_dash,
        )
        self.assertModule(v_colors_to_rast)
        # test that error output is not empty
        stderr = v_colors_to_rast.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertEquals(
            "Using colors from column <%s>\nColor set\n" % (self.color_column), stderr
        )
        # compare colors
        self.compare_color(self.ref_color)


if __name__ == "__main__":
    test()
