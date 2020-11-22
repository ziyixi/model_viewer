import numpy as np
import pyproj
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import KDTree


def gmt_project(startlon, startlat, endlon, endlat, thetype, npts=1001):
    g = pyproj.Geod(ellps='WGS84')
    if(thetype == "dist"):
        result = g.npts(startlon, startlat, endlon, endlat, npts)
        result = np.array(result)
        # result_lons, result_lats
        return result[:, 0], result[:, 1]
    elif(thetype == "lon"):
        # we divide 10 more times points using npts and find nearest lon
        test_points = g.npts(startlon, startlat, endlon, endlat, (npts-1)*10+1)
        test_points = np.array(test_points)
        tree = KDTree(test_points[:, 0].reshape(test_points.shape[0], -1))
        # evenly distributed lons
        result_lons = np.linspace(startlon, endlon, npts)
        _, pos = tree.query(result_lons.reshape(npts, -1))
        result_lats = test_points[:, 1][pos]
        return result_lons, result_lats
    elif(thetype == "lat"):
        # we divide 10 more times points using npts and find nearest lat
        test_points = g.npts(startlon, startlat, endlon, endlat, (npts-1)*10+1)
        test_points = np.array(test_points)
        tree = KDTree(test_points[:, 1].reshape(test_points.shape[0], -1))
        # evenly distributed lons
        result_lats = np.linspace(startlat, endlat, npts)
        _, pos = tree.query(result_lats.reshape(npts, -1))
        result_lons = test_points[:, 0][pos]
        return result_lons, result_lats
    else:
        raise Exception("not supported type")


def model_interp(to_interp_data, lons, lats, deps):
    """
    Give an xarray model, interp it based on the given lats, lons, deps and construct a new xarray dataset.
    mainly used to generate the vertical cross-sections
    """
    # * len(lons) should be the same as len(lats)
    profile_list = []
    for idep in range(len(deps)):
        for ilon in range(len(lons)):
            profile_list.append([lons[ilon], lats[ilon], deps[idep]])
    model_interpolating_function = RegularGridInterpolator(
        (to_interp_data.longitude.data, to_interp_data.latitude.data, to_interp_data.depth.data), to_interp_data.data)
    interp_result = model_interpolating_function(profile_list)
    cross_section = np.zeros((len(lons), len(deps)))

    icount = 0
    for idep in range(len(deps)):
        for ilon in range(len(lons)):
            cross_section[ilon, idep] = interp_result[icount]
            icount += 1

    # cross_section_xarray = xr.DataArray(cross_section, dims=(
    #     'h', "v"), coords={'h': lons, "v": deps})

    return cross_section


def topo_interp(to_interp_data, lons, lats):
    """
    Give the xarray topography model, interp the elevation line along the given (lons,lats) pair.
    """
    profile_list = []
    for ilon in range(len(lons)):
        profile_list.append([lons[ilon], lats[ilon]])
    # the names and the transverse might be adjusted, this is the gmt format
    grd_interpolating_function = RegularGridInterpolator(
        (to_interp_data.lon.data, to_interp_data.lat.data), to_interp_data.data.T)

    grd_interp_result = grd_interpolating_function(profile_list)

    # * return the 1d array
    return grd_interp_result
