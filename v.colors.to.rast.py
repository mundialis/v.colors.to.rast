#!/usr/bin/env python3

############################################################################
#
# MODULE:       v.colors.to.rast
#
# AUTHOR(S):    Anika Weinmann and Guido Riembauer
#
# PURPOSE:      Sets raster colors to color from color_column of referencemap
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

# %Module
# % description: Sets raster colors to colors from a color_column of a reference vector map.
# % keyword: vector
# % keyword: raster
# % keyword: colors
# %end

# %option G_OPT_R_INPUT
# % key: map
# % required: yes
# % label: Name of input land cover raster map
# %end

# %option G_OPT_V_INTPUT
# % key: referencemap
# % required: yes
# % label: Name for input vector map
# % description: Needs a column with class information. If a color column is given these colors are written to the raster
# %end

# %option G_OPT_DB_COLUMN
# % key: color_column
# % required: yes
# % label: Name of color column in reference vector map
# % description: Color have to be given in format like r:g:b e.g. 255:255:255
# %end

# %option G_OPT_DB_COLUMN
# % key: class_column
# % required: yes
# % label: Name of class information column in referencemap
# % description: Takes class information as string or integer
# %end


import grass.script as grass


def get_key(my_dict, val):
    for key, value in my_dict.items():
        if val == value:
            return key
    return None


def main():

    # parameters
    referencemap = options["referencemap"]
    map = options["map"]
    color_column = options["color_column"].replace("-", "_")
    class_column = options["class_column"].replace("-", "_")

    grass.message(_("Using colors from column <%s>") % color_column)
    color_class = list(
        grass.parse_command(
            "v.db.select",
            map=referencemap,
            columns=[color_column, class_column],
            flags="c",
        ).keys()
    )
    color_dict = dict()
    classname_is_int = True
    for cc in color_class:
        color, classname = cc.split("|")
        try:
            int(classname)
        except Exception as e:
            del e
            classname_is_int = False
        if color not in color_dict:
            color_dict[color] = classname
        elif color_dict[color] != classname:
            grass.fatal(
                _(
                    "Colors and classes are not unambiguously assigned for color <%s> and class <%s>"
                )
                % (color, classname)
            )

    # String class names
    if not classname_is_int:
        color_dict_vals = [val for key, val in color_dict.items()]
        map_classes = grass.parse_command("r.category", map=map, separator="pipe")
        for mc in map_classes:
            if "|" not in mc:
                grass.fatal(_("Classes have no category labels in map <%s>") % (map))
            classnum, classname = mc.split("|")
            if classname == "":
                grass.fatal(
                    _("Class <%s> has no category label in map <%s>") % (classnum, map)
                )
            elif classname not in color_dict_vals:
                grass.fatal(
                    _("Class <%s> is not in reference map <%s>")
                    % (classname, referencemap)
                )
            else:
                color_dict[get_key(color_dict, classname)] = classnum

    # modify the color table:
    colors_str = [
        "%s %s" % (val, key.replace(":", " ")) for key, val in color_dict.items()
    ]
    bc = grass.feed_command("r.colors", quiet=True, map=map, rules="-")
    bc.stdin.write(grass.encode("\n".join(colors_str)))
    bc.stdin.close()
    bc.wait()

    grass.message(_("Color set"))


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
