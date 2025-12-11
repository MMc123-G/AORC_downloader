# This script can be used to download hourly AORC precip data from the web.
# It is currently setup to download from the AORC_LMRFC_4km repository for Hurricane Ida Aug 26, 2021 – Sep 4, 2021.
# The zip files are compressed hourly netCDF files by month.
# Ex: AORC_APCP_4KM_LMRFC_202101.zip will contain every hourly netcdf file for January, 2021.
# %%
import zipfile
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import glob, os
import pandas as pd

# %%
# open the Validation_Calibration_Storm_Selection.xlsx as a dataframe
# df = pd.read_excel(r"LWI_Validation_Calibration_Storm_Selection.xlsx", sheet_name="Sheet1")

# if the column 'End Date' is NaT, use the Start Date + 21 days as the End Date.
# df["End Date"] = df["End Date"].fillna(df["Start Date"] + pd.DateOffset(days=21))
# df

# %%

#rfc office LMRFC, ABRFC, WGRFC, NERFC, SERFC, OHRFC, MARFC, CARFC, NCRFC, PBRFC
rfc= "WGRFC"

#  20DEC2015 - 10JAN2016
#  15APR2011 - 07MAY2011
calibration_storms = {
    # "Dec2015": {
    #     "Start Date": datetime.strptime("20DEC2015", "%d%b%Y"),
    #     "End Date": datetime.strptime("10JAN2016", "%d%b%Y")
    # },
    # "Apr2011": {
    #     "Start Date": datetime.strptime("15APR2011", "%d%b%Y"),
    #     "End Date": datetime.strptime("07MAY2011", "%d%b%Y")
    # },
    "2024toCurrent": {
        "Start Date": datetime.strptime("01JUN2024", "%d%b%Y"),
        "End Date": datetime.strptime("01DEC2025", "%d%b%Y")
    },
}
# Convert the dictionary to a dataframe
df = pd.DataFrame.from_dict(calibration_storms, orient='index')
# Reset the index to have a column for storm name
df.reset_index(inplace=True)
# Rename the columns
df.columns = ["Name", "Start Date", "End Date"]
# Print the dataframe
df

#%%
# Iterate the rows of the dataframe and print the storm name and start and end dates.
for index, row in df.iterrows():
# iterate just the first two rows for testing
# for index, row in df.head(2).iterrows():

    print('\nProcessing: ', row["Name"], row["Start Date"], row["End Date"])

# stormName = "RTF_05JUL2022"
    stormName = row["Name"]
    outDir = rf"output\nc\{rfc} {stormName}"
    # outDir = rf"V:\projects\p00659_dec_glo_phase3\02_analysis\nonTropical Calibration Event Selection\aorc\{stormName}"
    # Convert string date to to datetime objects for iterating
    # startDate = datetime.strptime("01OCT2005", "%d%b%Y")
    # endDate = datetime.strptime("15OCT2005", "%d%b%Y")
    startDate = row["Start Date"]
    endDate = row["End Date"]

    # Iterate by months from startdate to endDate
    date = startDate
    while date <= (endDate):
        # Convert date to format needed for URL
        date_str = datetime.strftime(date, "%Y%m")
        # Download each days zip file.
        # URL = f"https://hydrology.nws.noaa.gov/pub/AORC/V1.1/LMRFC_4km/precipitation/AORC_APCP_4KM_LMRFC_{date_str}.zip"
        URL = f"https://hydrology.nws.noaa.gov/pub/AORC/V1.1/{rfc}_4km/precipitation/AORC_APCP_4KM_{rfc}_{date_str}.zip"
        
        response = requests.get(URL, verify=False)
        open(f"AORC_APCP_4KM_{rfc}_{date_str}.zip", "wb").write(response.content)
        
        # Unzip hourly netCDF files to a single directory. 
        with zipfile.ZipFile(f"AORC_APCP_4KM_{rfc}_{date_str}.zip", 'r') as zip_ref:
            zip_ref.extractall(outDir)
        
        # Go to next month
        date = date + relativedelta(months=+1)
        # set the date to the first of the month
        date = date.replace(day=1)

    # Trim unzipped data to start - end dates
    for file in os.listdir(outDir):
        # Get all *.nc4 files
        if file.endswith(".nc4"):
            filepath = os.path.join(outDir, file)
            # get the date string
            filedate = file.split(".")[0][-10:-2]
            # convert the date string to a datetime object
            filedate_dt = datetime.strptime(filedate, "%Y%m%d")
            # delete file if date of the file is out of our starDate to EndDate range.
            if (filedate_dt < startDate) or (filedate_dt > endDate):
                os.remove(filepath)
        

# %%
