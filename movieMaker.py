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
ds = xr.open_dataset("output/nc/WGRFC Apr2017/AORC_APCP_WGRFC_2021042900.nc4")
ds
# %%
plot_title = "Fredericksburg, TX Rainfall April 29 - May 3, 2021"
# NetCDF Settings
storm = "WGRFC Apr2017"  # change as needed
netcdf_folder = f"output/nc/{storm}"
output_video = f"{storm}.mp4"
varname = "APCP_surface"  # change as needed

# GIS shapes for map overlays
subbasins_bool = False
# subbasins are optional as an overlay
if subbasins_bool:
    subbasins_path = "maps/Subbasins_HMS_Coarse.shp"
geojson_path = "maps/Fredericksburg_TX_20mi_buffer.geojson"

# baselayer map is optional
baselayer_bool = True

vmin, vmax = 0, 2  # adjust color range (min set to 0)
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
aoi = gpd.read_file(geojson_path)
    
# Plot the AOI and subbasins
fig, ax = plt.subplots(figsize=(10, 10))
aoi.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)
if baselayer_bool:
    try:
        import contextily as ctx
        ctx.add_basemap(ax, source=ctx.providers.Esri.WorldStreetMap, crs=aoi.crs, attribution=False)
    except ImportError:
        print("contextily is not installed. Baselayer will not be shown.")
    except Exception as e:
        print(f"Error adding baselayer: {e}")
if subbasins_bool:
    subbasins = gpd.read_file(subbasins_path)
    # reproject subbasins to match the AOI
    subbasins = subbasins.to_crs(aoi.crs)
    subbasins.plot(ax=ax, color='none', edgecolor='red', linewidth=0.5)
plt.title(plot_title)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
# plt.savefig("output/maps/aoi_subbasins.png", dpi=dpi, bbox_inches='tight')
plt.show()

# %%

# Loop through NetCDFs and generate frames
for i, file in enumerate(file_list):
    ds = xr.open_dataset(file)
    data = ds[varname][0] * 0.0393701  # convert mm to inches
    lon = ds["longitude"]
    lat = ds["latitude"]

    # print the extent of the data
    # print(lon.min(), lon.max(), lat.min(), lat.max())


    fig = plt.figure(figsize=(8, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    # Set extent based on AOI if baselayer is used, else use default
    if baselayer_bool:
        try:
            # Get AOI bounds
            minx, miny, maxx, maxy = aoi.total_bounds
            ax.set_extent([minx, maxx, miny, maxy], crs=ccrs.PlateCarree())
            import contextily as ctx
            # contextily expects Web Mercator, so skip for Cartopy, but could add rasterio basemap if needed
        except Exception as e:
            print(f"Error setting baselayer extent: {e}")
    else:
        ax.set_extent([-98, -99, 34, 35], crs=ccrs.PlateCarree())

    # ax.coastlines()
    # ax.add_feature(cfeature.BORDERS, linestyle=':')
    # ax.add_feature(cfeature.STATES, edgecolor='gray')

    # Plot subbasins
    if subbasins_bool:
        subbasins.plot(ax=ax, edgecolor="red", facecolor="none", linewidth=1, transform=ccrs.PlateCarree())

    # Add basemap if requested
    if baselayer_bool:
        try:
            import contextily as ctx
            # contextily expects Web Mercator, so we need to convert the axis
            # This works if ax is a GeoAxes (not Cartopy), so fallback if error
            ctx.add_basemap(ax, source=ctx.providers.Esri.WorldStreetMap, attribution=False, crs=aoi.crs)
        except Exception as e:
            print(f"Error adding baselayer to frame {i}: {e}")

    contour = ax.pcolormesh(lon, lat, data, vmin=vmin, vmax=vmax, cmap="viridis", alpha=0.6, transform=ccrs.PlateCarree())
    plt.colorbar(contour, ax=ax, label="Precipitation (inches)")

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
