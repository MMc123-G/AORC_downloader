# for each storm directory in /output/nc, 
# create a movie of the hourly precipitation data using xarray and rasterio.
# The movie will be saved as an mp4 file in the same directory.
# %%

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import imageio
import glob
import os

# %%
# open a sample NetCDF file to check variable names in xarray
ds = xr.open_dataset("output/nc/Apr2025/AORC_APCP_ABRFC_2025040600.nc4")
ds
# %%
# Settings
storm = "Jun2021"  # change as needed
netcdf_folder = f"output/nc/{storm}"
output_video = f"{storm}.mp4"
varname = "APCP_surface"  # change as needed
vmin, vmax = -2, 2  # adjust color range
dpi = 150

# Collect all NetCDF files
file_list = sorted(glob.glob(os.path.join(netcdf_folder, "*.nc4")))
file_list

# %%

# Temporary directory for frames
frame_dir = f"output/frames/{storm}"
os.makedirs(frame_dir, exist_ok=True)
frame_paths = []

# %%
import geopandas as gpd

# Load GeoJSON area of interest (AOI)
geojson_path = "maps/HMS_Coarse_Model_BB.geojson"
aoi = gpd.read_file(geojson_path)

# load the subbasins shapefile
subbasins_path = "maps\Subbasins_HMS_Coarse.shp"
subbasins = gpd.read_file(subbasins_path)
# reproject subbasins to match the AOI
subbasins = subbasins.to_crs(aoi.crs)
# Plot the AOI and subbasins
fig, ax = plt.subplots(figsize=(10, 10))
aoi.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)
subbasins.plot(ax=ax, color='none', edgecolor='red', linewidth=0.5)
plt.title("Area of Interest and Subbasins")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
# plt.savefig("output/maps/aoi_subbasins.png", dpi=dpi, bbox_inches='tight')
plt.show()

# %%

# Loop through NetCDFs and generate frames
for i, file in enumerate(file_list):
    ds = xr.open_dataset(file)
    data = ds[varname][0]  # assume single time step per file
    lon = ds["longitude"]
    lat = ds["latitude"]

    # print the extent of the data
    # print(lon.min(), lon.max(), lat.min(), lat.max())

    fig = plt.figure(figsize=(8, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-98, -99, 34, 35], crs=ccrs.PlateCarree())

    # ax.coastlines()
    # ax.add_feature(cfeature.BORDERS, linestyle=':')
    # ax.add_feature(cfeature.STATES, edgecolor='gray')
    # Plot subbasins
    subbasins.plot(ax=ax, edgecolor="red", facecolor="none", linewidth=1, transform=ccrs.PlateCarree())

    contour = ax.pcolormesh(lon, lat, data, vmin=vmin, vmax=vmax, cmap="viridis", alpha=0.6, transform=ccrs.PlateCarree())
    plt.colorbar(contour, ax=ax, label=varname)

    timestamp = str(ds['time'].values[0]) if 'time' in ds else f"Frame {i}"
    plt.title(f"{varname} at {timestamp}")

    frame_path = f"{frame_dir}/frame_{i:03d}.png"
    plt.savefig(frame_path, dpi=dpi, bbox_inches='tight')
    frame_paths.append(frame_path)
    plt.close()

# Generate video
with imageio.get_writer(output_video, fps=4) as writer:
    for frame_path in frame_paths:
        writer.append_data(imageio.imread(frame_path))

print(f"Video saved to: {output_video}")

# %%
