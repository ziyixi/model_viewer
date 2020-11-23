import numpy as np
import pygmt
import xarray as xr
from shapely.geometry import Point, Polygon

from pyapp.utils import get_data, get_figures
import pyproj
from spherical_geometry.polygon import SphericalPolygon


def gmt_get_data(name):
    return f'"{get_data(name)}"'


def plot_map(startlon, startlat, endlon, endlat, filename):
    startlon, startlat, endlon, endlat = map(
        float, [startlon, startlat, endlon, endlat])
    # check if the points are within the simulation region
    coords = [(91.3320117152011, 9.37366242174489), (144.284491292185, 2.08633373396527),
              (174.409435753150, 48.6744705245903), (74.6060844556399, 61.1396992149365), (91.3320117152011, 9.37366242174489)]
    # poly = Polygon(coords)
    # if(not poly.contains(Point(startlon, startlat))):
    #     return None
    # if(not poly.contains(Point(endlon, endlat))):
    #     return None
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    coords_xyz = []
    for each_coord in coords:
        x, y, z = pyproj.transform(
            lla, ecef, each_coord[0], each_coord[1], 0, radians=False)
        coords_xyz.append([x, y, z])
    start_xyz = pyproj.transform(
        lla, ecef, startlon, startlat, 0, radians=False)
    end_xyz = pyproj.transform(
        lla, ecef, endlon, endlat, 0, radians=False)
    sphr = SphericalPolygon(coords_xyz)
    if(not sphr.contains_point(start_xyz)):
        return None
    if(not sphr.contains_point(end_xyz)):
        return None

    fig = pygmt.Figure()
    # basemap
    with pygmt.config(MAP_FRAME_TYPE="plain", MAP_TICK_LENGTH="0p"):
        fig.basemap(region=[70, 160, 0, 62], projection="M8i",
                    frame=["WSen", "xafg", "yafg"])
    # load topo
    grd_topo = pygmt.datasets.load_earth_relief(
        resolution="02m", region=[70, 160, 0, 62])
    # plot
    fig.coast(water="167/194/223")
    fig.grdimage(grd_topo, cmap=gmt_get_data("land_sea.cpt"),
                 I=gmt_get_data("topo_gradient.nc"))
    fig.plot(data=gmt_get_data("nuvel1_boundaries"), pen="2p,red")
    fig.plot(data=gmt_get_data("block2d_mod.txt"), pen="0.5p")
    fig.plot(data=gmt_get_data("China_Basins"), pen="0.5p")
    vol = np.loadtxt(get_data("ChinaVolcano.xy"), usecols=[1, 2])
    fig.plot(x=vol[:, 1], y=vol[:, 0], style="kvolcano/0.3", color="magenta")
    fig.plot(x=[91.3320117152011, 144.284491292185, 174.409435753150, 74.6060844556399, 91.3320117152011], y=[
        9.37366242174489, 2.08633373396527, 48.6744705245903, 61.1396992149365, 9.37366242174489], pen="2p,magenta")
    # plot the line
    fig.plot(x=[startlon, endlon], y=[startlat, endlat], pen="2p,magenta")

    fig.grdcontour(gmt_get_data("izu_slab2_depth.grd"),
                   interval=100, pen="1.5p,navyblue")
    fig.grdcontour(gmt_get_data("kur_slab2_depth.grd"),
                   interval=100, pen="1.5p,navyblue")
    fig.grdcontour(gmt_get_data("phi_slab2_depth.grd"),
                   interval=100, pen="1.5p,navyblue")
    fig.grdcontour(gmt_get_data("ryu_slab2_depth.grd"),
                   interval=100, pen="1.5p,navyblue")
    fig.grdcontour(gmt_get_data("man_slab2_depth.grd"),
                   interval=100, pen="1.5p,navyblue")

    fig.text(x=101, y=28, text="CDB", font="8p,Helvetica,black", angle=-60)
    fig.text(x=87, y=45, text="JGB", font="8p,Helvetica,black", angle=10)
    fig.text(x=94, y=37.5, text="QDB", font="8p,Helvetica,white", angle=-20)
    fig.text(x=105, y=30, text="SCB", font="8p,Helvetica,black", angle=0)
    fig.text(x=93, y=42, text="TLFB", font="8p,Helvetica,black", angle=-10)
    fig.text(x=101, y=33, text="SGFB", font="8p,Helvetica,black", angle=-10)
    fig.text(x=73, y=10, text="Arabian Sea",
             font="8p,Helvetica,black", angle=-60)
    fig.text(x=91, y=13, text="Andaman T.",
             font="8p,Helvetica-Bold,black", angle=70)
    fig.text(x=90, y=19, text="Bay of Bengal",
             font="8p,Helvetica,black", angle=0)
    fig.text(x=80, y=25, text="India Plate",
             font="12p,Helvetica-Bold,black", angle=-30)
    fig.text(x=93, y=23, text="Burma T.",
             font="8p,Helvetica-Bold,black", angle=80)
    fig.text(x=80, y=28, text="Main Boundary Thrust",
             font="8p,Helvetica,black", angle=-30)
    fig.text(x=82, y=29.5, text="Himalaya Block",
             font="8p,Helvetica,black", angle=-30)
    fig.text(x=86, y=30, text="Lhasa Block",
             font="8p,Helvetica,black", angle=-30)
    fig.text(x=89, y=33, text="Qiangtang Block",
             font="8p,Helvetica,black", angle=-20)
    fig.text(x=73, y=37, text="Pamirs", font="8p,Helvetica,black", angle=0)
    fig.text(x=82, y=39, text="Tarim Basin",
             font="8p,Helvetica,black", angle=0)
    fig.text(x=79, y=42.5, text="Tianshan",
             font="8p,Helvetica,white", angle=10)
    fig.text(x=76.5, y=49, text="Kazakhstan",
             font="12p,Helvetica-Bold,black", angle=0)
    fig.text(x=110, y=60, text="Russia",
             font="12p,Helvetica-Bold,black", angle=0)
    fig.text(x=97.5, y=50.5, text="Sayan", font="8p,Helvetica,white", angle=0)
    fig.text(x=97.5, y=47, text="Altay", font="8p,Helvetica,white", angle=0)
    fig.text(x=101, y=42, text="Nanshan", font="8p,Helvetica,black", angle=0)
    fig.text(x=101, y=41, text="Basin", font="8p,Helvetica,black", angle=0)
    fig.text(x=99, y=38, text="Qilian Fold",
             font="8p,Helvetica,white", angle=-10)
    fig.text(x=103.5, y=25.5, text="Tengchong V.",
             font="8p,Helvetica,white", angle=0)
    fig.text(x=95.5, y=23, text="Burma",
             font="12p,Helvetica-Bold,black", angle=80)
    fig.text(x=115, y=15, text="South China Sea",
             font="12p,Helvetica-Bold,black", angle=60)
    fig.text(x=113.5, y=20.5, text="Hainan V.",
             font="8p,Helvetica,black", angle=0)
    fig.text(x=113, y=27, text="South China Block",
             font="12p,Helvetica-Bold,black", angle=0)
    fig.text(x=117, y=36.5, text="North China",
             font="12p,Helvetica-Bold,black", angle=-30)
    fig.text(x=117, y=34.5, text="Block",
             font="12p,Helvetica-Bold,black", angle=-30)
    fig.text(x=109, y=38, text="Ordos", font="8p,Helvetica,black", angle=0)
    fig.text(x=109, y=37, text="Block", font="8p,Helvetica,black", angle=0)
    fig.text(x=120.5, y=39, text="Bohai Bay",
             font="8p,Helvetica,black", angle=0)
    fig.text(x=120, y=48, text=r"Xing'an-East Mongolia",
             font="12p,Helvetica-Bold,black", angle=30)
    fig.text(x=125, y=45, text="Songliao Basin",
             font="8p,Helvetica,black", angle=30)
    fig.text(x=133, y=42, text="Changbai V.",
             font="8p,Helvetica,black", angle=0)
    fig.text(x=132, y=49, text="Wudalianchi V.",
             font="8p,Helvetica,black", angle=0)
    fig.text(x=134, y=40, text="Japan Sea",
             font="12p,Helvetica-Bold,black", angle=30)
    fig.text(x=126.5, y=26, text="Okinawa Trough",
             font="8p,Helvetica,black", angle=40)
    fig.text(x=130, y=26, text="Ryukyu T.",
             font="8p,Helvetica-Bold,white", angle=50)
    fig.text(x=134, y=15, text="Philippine Sea Plate",
             font="12p,Helvetica-Bold,white", angle=60)
    fig.text(x=150, y=54, text="Sea of Okhotsk",
             font="12p,Helvetica-Bold,black", angle=60)
    fig.text(x=157, y=38, text="Pacific Plate",
             font="12p,Helvetica-Bold,white", angle=60)
    fig.text(x=123, y=20, text="Malina T.",
             font="8p,Helvetica-Bold,white", angle=-80)
    fig.text(x=126, y=12, text="Philippine T.",
             font="8p,Helvetica-Bold,white", angle=-60)
    fig.text(x=137.5, y=7.5, text="Yap T.",
             font="8p,Helvetica-Bold,white", angle=30)
    fig.text(x=148.5, y=17, text="Mariana T.",
             font="8p,Helvetica-Bold,white", angle=92)
    fig.text(x=143.5, y=30, text="Izu-Bonin T.",
             font="8p,Helvetica-Bold,white", angle=102)
    fig.text(x=145, y=38, text="Japan T.",
             font="8p,Helvetica-Bold,white", angle=60)
    fig.text(x=153, y=44, text="Kuril T.",
             font="8p,Helvetica-Bold,white", angle=30)
    fig.text(x=110, y=54, text="Lake Baikai",
             font="8p,Helvetica-Bold,black", angle=60)
    fig.text(x=158, y=55, text="Kamchatka Peninsula",
             font="8p,Helvetica-Bold,black", angle=80)
    fig.colorbar(
        # justified inside map frame (j) at Top Center (TC)
        position="JBC+w18c/0.35c+o0i/0.3i",
        box=False,
        frame=[f'"+LTopography (km)"'],
        scale=0.001,
        C=gmt_get_data("land_sea.cpt"))
    with pygmt.config(MAP_FRAME_TYPE="inside", MAP_TICK_LENGTH_PRIMARY="10p"):
        fig.basemap(region=[70, 160, 0, 62], projection="M8i",
                    frame=["wsen", "xaf", "yaf"])
    # * a bug in pygmt when containing space, this func can only be called from the base
    fig.savefig(f"./pyapp/map/figures/{filename}.png")
    return f"{filename}.png"
