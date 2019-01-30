import rasterio
import rasterio.features
import rasterio.warp
import rasterio.env
import rasterio.plot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
from fiona.transform import transform_geom
from fiona.crs import from_string
from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point, LineString
import pickle
from bulletin import Bulletin
import itertools

from geodesiclinestogis.geodesicline2gisfile import GeodesicLine2Gisfile
line_builder = GeodesicLine2Gisfile(loglevel='ERROR')

colors = {'WARM': 1, 'COLD': 2, 'STNRY': 3, 'OCFNT': 4, 'TROF': 5}

with rasterio.open('example.grib') as example:
    crs = example.crs
    tf = example.transform
    width = example.width
    height = example.height
project = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:4326'),  # source coordinate system
    pyproj.Proj(crs))  # destination coordinate system
inf = open('data.bin', 'rb')
bulletins = pickle.load(inf)
for date, bulletin in bulletins.items():
    # print(date)
    result = np.zeros((height, width), dtype=np.uint8)
    for front in bulletin.fronts:
        if front[0] == 'TROF':
            continue
        color = colors[front[0]]
        shape = []
        for a, b in zip(front[1], front[1][1:]):
            line = transform(project, LineString(line_builder.gdlComp((a[1], a[0], b[1], b[0]), km_pts=20)))
            shape.append(line.buffer(50000))
        result = rasterio.features.rasterize(shapes=shape, transform=tf, all_touched=True, default_value=color, out=result)
    # cmap = matplotlib.colors.ListedColormap(['black', 'red', 'blue', 'green', 'purple'])
    # plt.imshow(result, cmap=cmap, interpolation='nearest', origin='lower')
    # with rasterio.open('netcdf:/mnt/ldm_vol_DESKTOP-DSIGH25-Dg0_Volume1/DiplomData2/NARR/air.2m.nc:air') as tmp:
    #     a = tmp.read(2913)
    #     a = np.ma.masked_where(a == tmp.nodata, a)
    # plt.imshow(a, alpha=0.5)
    # plt.show()
    # exit()

