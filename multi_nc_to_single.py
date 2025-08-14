# create a single NetCDF file from multiple Hourly NetCDF files
import xarray as xr
import os
import glob
import pandas as pd
from datetime import datetime
def combine_nc_files(storm_name, out_dir):
    # Create output directory if it doesn't exist
    os.makedirs(out_dir, exist_ok=True)

    # Find all NetCDF files for the storm
    file_pattern = os.path.join(out_dir, f"{storm_name}/*.nc4")
    nc_files = sorted(glob.glob(file_pattern))

    if not nc_files:
        print(f"No NetCDF files found for storm: {storm_name}")
        return

    # Load and combine all NetCDF files
    ds_list = [xr.open_dataset(nc_file) for nc_file in nc_files]
    combined_ds = xr.concat(ds_list, dim="time")

    # Save the combined dataset to a new NetCDF file
    output_file = os.path.join(out_dir, f"{storm_name}_combined.nc4")
    combined_ds.to_netcdf(output_file)

    print(f"Combined NetCDF file saved as: {output_file}")

if __name__ == "__main__":
    # Define storms and output directory
    storms = ["LMRFC Apr2011", "LMRFC Dec2015"]
    out_dir = "output/nc"

    # Combine NetCDF files for each storm
    for storm in storms:
        combine_nc_files(storm, out_dir)