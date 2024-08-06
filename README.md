# AORC_downloader
https://github.com/mylesmc123/AORC_downloader/tree/LWI
This script can be used to download hourly AORC precip data from the web.
It is currently setup to download from the AORC_LMRFC_4km repository for a large list of LWI runs:
['Isidore', 'Oct-02', 'Feb-03', 'Feb-04', 'May-04', 'Ivan', 'Katrina', 'May-08', 'Gustav', 'Mar-09', 'Oct-09', 'Lee', 'Isaac', 'Jan-13', 'Jul-15', 'Oct-15', 'May-16', 'May-17', 'Jun-17', 'Jun-18', 'Harvey', 'Nate', 'Mar-18', 'May-19', 'Jun-19', 'Barry', 'Aug-19', 'Imelda', 'May-20', 'Cristobal', 'Laura', 'Beta_Sally', 'Delta']

## Convert to DSS
The AORC Downloader will download the files for each monthly archive and unzip them to folders for each storm name that will contain the right temporal extent of netCDF files.
The nc_to_dss_precip jython file used the Vortex API to create DSS files for each storm.
