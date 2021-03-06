import tempfile

import numpy as np
import pygmt
import xarray as xr
from obspy.geodetics.base import locations2degrees
from pygmt.clib import Session

from pyapp.utils import get_data_vc
from pyapp.vc.utils import gmt_project, model_interp, topo_interp


def gmt_get_data_vc(name):
    return f'"{get_data_vc(name)}"'


def plot_vc(startlon, startlat, endlon, endlat, models, parameter, x_axis_label, depth, colorbar_range, threshold, filename):
    # fix the problem of possible -R failure
    if((x_axis_label == "lon" and startlon > endlon) or (x_axis_label == "lat" and startlat > endlat)):
        startlon, endlon = endlon, startlon
        startlat, endlat = endlat, startlat

    fig = pygmt.Figure()
    pygmt.config(FONT_LABEL="15p", MAP_LABEL_OFFSET="12p",
                 FONT_ANNOT_PRIMARY="12p", MAP_FRAME_TYPE="plain")
    pygmt.makecpt(cmap=gmt_get_data_vc("dvs_6p.cpt"),
                  series=f"{colorbar_range[0]/100:.3f}/{colorbar_range[1]/100:.3f}/0.01", continuous=True, D="o")

    # load
    izu = xr.open_dataset(
        get_data_vc("izu_slab2_depth.grd"))
    kur = xr.open_dataset(
        get_data_vc("kur_slab2_depth.grd"))
    phi = xr.open_dataset(
        get_data_vc("phi_slab2_depth.grd"))
    ryu = xr.open_dataset(
        get_data_vc("ryu_slab2_depth.grd"))
    man = xr.open_dataset(
        get_data_vc("man_slab2_depth.grd"))
    if(models == "eara2020"):
        data = xr.open_dataset(
            get_data_vc("per_m20_ref.nc"))
    elif(models == "Initial"):
        data = xr.open_dataset(
            get_data_vc("per_m00_ref.nc"))
    else:
        raise Exception(f"not supported model {models}")

    # generate the file to plot
    to_interp_data = data[parameter].copy()
    to_interp_data.data[to_interp_data.data > 9e6] = np.nan
    grd_topo = pygmt.datasets.load_earth_relief(
        resolution="02m", region=[70, 170, 0, 70])
    deps = np.linspace(0, depth, 1001)
    lons, lats = gmt_project(startlon, startlat, endlon, endlat, x_axis_label)
    cross_section = model_interp(to_interp_data, lons, lats, deps)

    # start to plot the figure
    if(x_axis_label == "lon"):
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlon-endlon)}i/-{depth/1000*2.7}i",
                        region=f"{startlon}/{endlon}/0/{depth}", frame=["wsen", 'yaf', 'xaf'])
        cross_section_xarray = xr.DataArray(cross_section, dims=(
            'h', "v"), coords={'h': lons, "v": deps})
    elif(x_axis_label == "lat"):
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlat-endlat)}i/-{depth/1000*2.7}i",
                        region=f"{startlat}/{endlat}/0/{depth}", frame=["wsen", 'yaf', 'xaf'])
        cross_section_xarray = xr.DataArray(cross_section, dims=(
            'h', "v"), coords={'h': lats, "v": deps})
    elif(x_axis_label == "dist"):
        # get distance
        distmax = locations2degrees(startlat, startlon, endlat, endlon)
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*distmax}i/-{depth/1000*2.7}i",
                        region=f"0/{distmax}/0/{depth}", frame=["wsen", 'yaf', 'xaf'])
        dists = np.linspace(0, distmax, 1001)
        cross_section_xarray = xr.DataArray(cross_section, dims=(
            'h', "v"), coords={'h': dists, "v": deps})
    else:
        raise Exception("not supported x_axis_label")
    fig.grdimage(cross_section_xarray.T, cmap=True)
    for interval in ["+-0.1", "+-0.08", "+-0.06", "+-0.04", "+-0.02"]:
        fig.grdcontour(cross_section_xarray.T, interval=interval,
                       pen="0.5p,black", cut=300, A=interval+"+f6p+u")
    for interval in ["+0.02", "+0.04", "+0.06", "+0.08", "+0.1"]:
        fig.grdcontour(cross_section_xarray.T, interval=interval,
                       pen="0.5p,white", cut=300, A=interval+"+f6p+u")
    if(threshold != 0):
        # project the events
        fo = tempfile.NamedTemporaryFile()
        # use gmt project to select events
        with Session() as lib:
            lib.call_module(
                module="project", args=f"{gmt_get_data_vc('ehb.txt')} -C{startlon}/{startlat} -E{endlon}/{endlat} -Fxyzpq -W-{threshold}/{threshold} > {fo.name}")
        project_generated = np.loadtxt(fo.name)
        used_lons = project_generated[:, 0]
        used_lats = project_generated[:, 1]
        used_deps = project_generated[:, 3]
        # used_distances = project_generated[:, 5]
        used_mags = project_generated[:, 2]
        used_x = project_generated[:, 4]

        used_x_small = used_x[used_mags < 6]
        used_x_large = used_x[used_mags >= 6]
        used_deps_small = used_deps[used_mags < 6]
        used_deps_large = used_deps[used_mags >= 6]
        used_lons_small = used_lons[used_mags < 6]
        used_lons_large = used_lons[used_mags >= 6]
        used_lats_small = used_lats[used_mags < 6]
        used_lats_large = used_lats[used_mags >= 6]
        if(x_axis_label == "lon"):
            fig.plot(
                x=used_lons_small,
                y=used_deps_small,
                color="white",
                style="c0.075c",
                pen="black"
            )
            fig.plot(
                x=used_lons_large,
                y=used_deps_large,
                color="red",
                style="a0.3c",
                pen="black"
            )
        elif(x_axis_label == "lat"):
            fig.plot(
                x=used_lats_small,
                y=used_deps_small,
                color="white",
                style="c0.075c",
                pen="black"
            )
            fig.plot(
                x=used_lats_large,
                y=used_deps_large,
                color="red",
                style="a0.3c",
                pen="black"
            )
        elif(x_axis_label == "dist"):
            fig.plot(
                x=used_x_small,
                y=used_deps_small,
                color="white",
                style="c0.075c",
                pen="black"
            )
            fig.plot(
                x=used_x_large,
                y=used_deps_large,
                color="red",
                style="a0.3c",
                pen="black"
            )
        fo.close()

    if(x_axis_label == "lon"):
        y_410 = np.zeros_like(lons)
        y_410[:] = 410
        fig.plot(x=lons, y=y_410, pen="0.5p,black,dashed")
        y_650 = np.zeros_like(lons)
        y_650[:] = 650
        fig.plot(x=lons, y=y_650, pen="0.5p,black,dashed")
        with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlon-endlon)}i/-{depth/1000*2.7}i",
                        region=f"{startlon}/{endlon}/0/{depth}", frame=["wsen", 'yaf', 'xaf'])
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlon-endlon)}i/-{depth/1000*2.7}i",
                        region=f"{startlon}/{endlon}/0/{depth}", frame=["WSen", 'yaf+l"Depth (km)"', 'xaf+l"Longitude (degree)"'])
        fig.colorbar(
            # justified inside map frame (j) at Top Center (TC)
            position="JBC+w15c/0.8c+h+o0i/2c",
            box=False,
            frame=["a1f", f'"+L@~d@~ln{parameter}(%)"'],
            scale=100,)
    elif(x_axis_label == "lat"):
        y_410 = np.zeros_like(lats)
        y_410[:] = 410
        fig.plot(x=lats, y=y_410, pen="0.5p,black,dashed")
        y_650 = np.zeros_like(lats)
        y_650[:] = 650
        fig.plot(x=lats, y=y_650, pen="0.5p,black,dashed")
        with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlat-endlat)}i/-{depth/1000*2.7}i",
                        region=f"{startlat}/{endlat}/0/{depth}", frame=["wsen", 'yaf', 'xaf'])
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlat-endlat)}i/-{depth/1000*2.7}i",
                        region=f"{startlat}/{endlat}/0/{depth}", frame=["WSen", 'yaf+l"Depth (km)"', 'xaf+l"Latitude (degree)"'])
        fig.colorbar(
            # justified inside map frame (j) at Top Center (TC)
            position="JBC+w15c/0.8c+h+o0i/2c",
            box=False,
            frame=["a1f", f'"+L@~d@~ln{parameter}(%)"'],
            scale=100,)
    elif(x_axis_label == "dist"):
        y_410 = np.zeros_like(dists)
        y_410[:] = 410
        fig.plot(x=dists, y=y_410, pen="0.5p,black,dashed")
        y_650 = np.zeros_like(dists)
        y_650[:] = 650
        fig.plot(x=dists, y=y_650, pen="0.5p,black,dashed")
        with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
            fig.basemap(projection=f"X{0.3*distmax}i/-{depth/1000*2.7}i",
                        region=f"0/{distmax}/0/{depth}", frame=["wsen", 'yaf', 'xaf'])
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*distmax}i/-{depth/1000*2.7}i",
                        region=f"0/{distmax}/0/{depth}", frame=["WSen", 'yaf+l"Depth (km)"', 'xaf+l"Distance (degree)"'])
        fig.colorbar(
            # justified inside map frame (j) at Top Center (TC)
            position="JBC+w15c/0.8c+h+o0i/2c",
            box=False,
            frame=["a1f", f'"+L@~d@~ln{parameter}(%)"'],
            scale=100,)
    # ***********************
    grd_interp_result = topo_interp(grd_topo, lons, lats)
    if(x_axis_label == "lon"):
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlon-endlon)}i/1i",
                        region=f"{startlon}/{endlon}/-5000/5000", frame=["wsen", 'ya2500f', 'xaf'], Y=f"a{depth/1000*2.7+0.4}i")
        fig.plot(x=lons, y=np.zeros_like(lons), pen="black",
                 L="+yb", G="lightblue", Y=f"a{depth/1000*2.7+0.4}i")
        fig.plot(x=lons, y=grd_interp_result, pen="black",
                 L="+yb", G="gray", Y=f"a{depth/1000*2.7+0.4}i")
        with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlon-endlon)}i/1i",
                        region=f"{startlon}/{endlon}/-5000/5000", frame=["wsen", 'ya2500f', 'xaf'], Y=f"a{depth/1000*2.7+0.4}i")
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlon-endlon)}i/1i",
                        region=f"{startlon}/{endlon}/-5000/5000", frame=["Wsen", 'ya2500f+l"Elevation (m)"', 'xaf'], Y=f"a{depth/1000*2.7+0.4}i")
    elif(x_axis_label == "lat"):
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlat-endlat)}i/1i",
                        region=f"{startlat}/{endlat}/-5000/5000", frame=["wsen", 'ya2500f', 'xaf'], Y=f"a{depth/1000*2.7+0.4}i")
        fig.plot(x=lats, y=np.zeros_like(lats), pen="black",
                 L="+yb", G="lightblue", Y=f"a{depth/1000*2.7+0.4}i")
        fig.plot(x=lats, y=grd_interp_result, pen="black",
                 L="+yb", G="gray", Y=f"a{depth/1000*2.7+0.4}i")
        with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlat-endlat)}i/1i",
                        region=f"{startlat}/{endlat}/-5000/5000", frame=["wsen", 'ya2500f', 'xaf'], Y=f"a{depth/1000*2.7+0.4}i")
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*np.abs(startlat-endlat)}i/1i",
                        region=f"{startlat}/{endlat}/-5000/5000", frame=["wsen", 'ya2500f+l"Elevation (m)"', 'xaf'], Y=f"a{depth/1000*2.7+0.4}i")
    elif(x_axis_label == "dist"):
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*distmax}i/1i",
                        region=f"0/{distmax}/-5000/5000", frame=["wsen", 'ya2500f', 'xaf'], Y=f"a{depth/1000*2.7+0.4}i")
        fig.plot(x=dists, y=np.zeros_like(dists), pen="black",
                 L="+yb", G="lightblue", Y=f"a{depth/1000*2.7+0.4}i")
        fig.plot(x=dists, y=grd_interp_result, pen="black",
                 L="+yb", G="gray", Y=f"a{depth/1000*2.7+0.4}i")
        with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
            fig.basemap(projection=f"X{0.3*distmax}i/1i",
                        region=f"0/{distmax}/-5000/5000", frame=["wsen", 'ya2500f', 'xaf'], Y=f"a{depth/1000*2.7+0.4}i")
        with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
            fig.basemap(projection=f"X{0.3*distmax}i/1i",
                        region=f"0/{distmax}/-5000/5000", frame=["wsen", 'ya2500f+l"Elevation (m)"', 'xaf'], Y=f"a{depth/1000*2.7+0.4}i")
    fig.savefig(f"./pyapp/vc/figures/{filename}.png")
    return f"{filename}.png"
