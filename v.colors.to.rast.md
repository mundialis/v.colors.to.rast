## DESCRIPTION

*v.colors.to.rast* sets raster colors to color from **color_column** of
**referencemap**.

## EXAMPLE

### Assign color from color column in referencemap

```sh
v.colors.to.rast referencemap=incora_dortmund_LULC_training_points_color map=classification color_column=color class_column=lulc_int
```

## SEE ALSO

*[r.colors](https://grass.osgeo.org/grass-stable/manuals/r.colors.html),
[v.db.select](https://grass.osgeo.org/grass-stable/manuals/v.db.select.html)*

## AUTHORS

Anika Weinmann and Guido Riembauer,
[mundialis](https://www.mundialis.de/), Germany
