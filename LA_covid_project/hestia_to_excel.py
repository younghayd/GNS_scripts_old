#-- This script converts the hourly .nc.tar.gz files into usable sector totals and outputs it in Excel

#-- Load packages

import os
import tarfile
import netCDF4
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta
import openpyxl


#-- Set working directories and variables

city = "baltimore"

year_list =  ["2010", "2011", "2012", "2013", "2014", "2015"]
sector_list = ["Onroad", "Nonroad", "Residential", "Commercial", "Industrial", "Airport", "Rail", "ElecProd", "CMV",
               "Cement"]

raw_file_path = "H:/data/LA_covid_project/raw_data/inventory_CO2_data/baltimore/hestia_nc_files/hourly/zipped/"
nc_file_path = "H:/data/LA_covid_project/raw_data/inventory_CO2_data/baltimore/hestia_nc_files/hourly/nc/"
processed_data_path = "H:/data/LA_covid_project/processed_data/baltimore/"

def tar_gz_unzip(raw_data_loc, proc_data_loc):
    """
    tar_gz_unzip takes raw .tar.gz files from Hestia and unzips them.
    Since the hourly files are so large, this can take a while.
    Raw files are downloaded from https://hestia.rc.nau.edu/Data.html.
    Username and password are "hestiauser" and "hestia2019"

    :param raw_data_loc: Folder location of all raw .tar.gz files
    :param proc_data_loc: Folder location where all annual .nc files for each sector will be saved (at hourly res)
    """
    tar_gz_list = os.listdir(raw_data_loc)

    for tar_gz_filename in tar_gz_list:
        file = tarfile.open(tar_gz_filename)
        file.extractall(proc_data_loc)
        file.close()

def daterange(start_date, end_date):
    """
    daterange returns a range that beings at start_date, ends at end_date, and iterates in hour steps.
    yield is used in the place of "return" to conserve memory.
    This is used to create a datetime data frame for the observed year, in steps of 1 hour.

    :param start_date: datetime that data frame begins
    :param end_date: datetime that data frame ends
    :return:
    """

    delta = timedelta(hours=1)
    while start_date < end_date:
        yield start_date
        start_date += delta

def calculate_co2_totals(nc_file, hour_start, hour_end):
    """

    calculate_co2_totals takes in the 4-D data (lat, lon, time, and kgC) for a given year. It calculates the total kgC
    measured during a certain time range (likely between 1 pm (13) and 4 pm (16)). This is for better comparison
    between inventory and flasks measured during mid afternoon. While CO data won't be measured by hour, can use
    sector totals to see which sectors are more dominant at this time and can infer whether this would increase
    the RCO of the inventory data when comparing to flasks.

    :param nc_file: .nc file, specific for a year and sector.
    :param hour_start: beginning hour of data range
    :param hour_end: end hour of data range
    :return:
    """

    start_date = datetime(int(year), 1, 1, 0, 00)
    end_date = datetime(int(year) + 1, 1, 1, 0, 00)

    date_array = pd.DataFrame(columns = ['datetime'])

    #Creating a datetime dataframe for the year, in steps of 1 hour
    for single_date in daterange(start_date, end_date):
        day_array = pd.DataFrame(data=[single_date.strftime("%Y-%m-%d %H:%M")], columns=["datetime"])
        date_array = pd.concat([date_array, day_array])

    date_array['datetime'] = pd.to_datetime(date_array['datetime'])

    #Selecting datetimes in date_array that correspond to flask times (mid afternoon).
        #+1 on hour_start accounts for fact that hour 13 corresponds to the period of 12 pm to 1 pm, not 1 pm to 2 pm.
    selected_values = date_array[
        (date_array['datetime'].dt.hour >= hour_start + 1) & (date_array['datetime'].dt.hour <= hour_end)
        ]

    #Converting selected datetimes to hours of year to match with Hestia

    selected_values['year'] = selected_values['datetime'].dt.year
    selected_values['start_of_year'] = pd.to_datetime(selected_values['year'], format='%Y')

    # Calculate the time difference in hours
    selected_values['hours_of_year'] = (selected_values['datetime'] - selected_values['start_of_year']).dt.total_seconds() / 3600

    selected_hours = selected_values['hours_of_year'].tolist()
    selected_hours = [int(i) for i in selected_hours]
    selected_hours = [i -1 for i in selected_hours]

    time_series = nc_file.sum(dim=["X", "Y"])
    time_series = time_series.to_dataframe()

    selected_times = time_series.iloc[selected_hours]

    co2_3_hour = selected_times.sum().item()




#-- Load in files
os.chdir(raw_file_path)
#
# #Define functions
def daterange(start_date, end_date):
    delta = timedelta(hours=1)
    while start_date < end_date:
        yield start_date
        start_date += delta

# Unzips the files
# tar_gz_list = os.listdir()
#
# for tar_gz_filename in tar_gz_list:
#     file = tarfile.open(tar_gz_filename)
#     file.extractall('../nc/')
#     file.close()
#
# # Convert .nc map object to data frame for the chosen year
os.chdir(nc_file_path)


nc_list = os.listdir()
# Since there are some annual files in there by mistake
nc_list = [filename for filename in nc_list if "hourly" in filename]

with pd.ExcelWriter(processed_data_path + city + "_hestia_co2_sector_totals.xlsx") as writer:

    for year in year_list:

        print(year)

        all_sector_data = pd.DataFrame(columns = ["Sector", "CO2_24_hr (kgC)", "CO2_1pm-4pm (kgC)"])

        file_list = [filename for filename in nc_list if year in filename]

        total_24_hour = 0
        total_3_hour = 0

        for sector in sector_list:

            print(sector)
            file_address = next(filename for filename in file_list if sector in filename)

            #This section is the totalling of CO2

            # nc_file = netCDF4.Dataset(file_address, mode='r')
            nc_file = xr.open_dataset(file_address)

            co2_24_hour = nc_file["Carbon Emissions"].sum().item()


            #Selecting hours between 1pm and 4pm only

            start_date = datetime(int(year), 1, 1, 0, 00)
            end_date = datetime(int(year) + 1, 1, 1, 0, 00)

            date_array = pd.DataFrame(columns = ['datetime'])

            for single_date in daterange(start_date, end_date):
                day_array = pd.DataFrame(data=[single_date.strftime("%Y-%m-%d %H:%M")], columns=["datetime"])
                date_array = pd.concat([date_array, day_array])

            date_array['datetime'] = pd.to_datetime(date_array['datetime'])
            selected_values = date_array[
                (date_array['datetime'].dt.hour >= 14) & (date_array['datetime'].dt.hour <= 16)
                ]

            #Converting selected datetimes to hours of year

            selected_values['year'] = selected_values['datetime'].dt.year

            # Create a new column for the start of the year
            selected_values['start_of_year'] = pd.to_datetime(selected_values['year'], format='%Y')

            # Calculate the time difference in hours
            selected_values['hours_of_year'] = (selected_values['datetime'] - selected_values['start_of_year']).dt.total_seconds() / 3600

            selected_hours = selected_values['hours_of_year'].tolist()
            selected_hours = [int(i) for i in selected_hours]
            selected_hours = [i -1 for i in selected_hours]

            time_series = nc_file.sum(dim=["X", "Y"])
            time_series = time_series.to_dataframe()

            selected_times = time_series.iloc[selected_hours]

            co2_3_hour = selected_times.sum().item()

            # sector_data = pd.DataFrame([sector, co2_24_hour, co2_3_hour], columns = ["Sector", "CO2_24_hr (kgC)", "CO2_1pm-4pm (kgC)"])
            # all_sector_data = pd.concat([all_sector_data, sector_data])

            all_sector_data.loc[len(all_sector_data)] = [sector, co2_24_hour, co2_3_hour]

            total_3_hour = co2_3_hour + total_3_hour
            total_24_hour = co2_24_hour + total_24_hour
            #This section is saving it to an excel
            #Think best way is to make pandas dataframe and then append the sector and co2 value for each loop

            #set total co2 value equal to "total_co2"

            #Need to separate and only include co2 between 1pm and 4pm maybe?

            #Section here appending sector name, total co2, and specific co2 values to data frame

        all_sector_data.loc[len(all_sector_data)] = ["Total", total_24_hour, total_3_hour]

        all_sector_data.to_excel(writer, sheet_name = year, index = False)

    #save to excel sheet


#
# nc_list = [string for string in nc_list if "2014" in string]
#
# for nc_filename in nc_list:
#     nc_file = netCDF4.Dataset(nc_filename, mode='r')
#     nc_file.variables.keys()
#     lat = nc_file.variables['lat'][:]
#     lon = nc_file.variables['lon'][:]
#     time = nc_file.variables['time']
#     datetime = netCDF4.num2date(time[:],time.units)
#     co2 = nc_file.variables['']
#
#     hestia_co2 = pd.Series(co2, index = )
#
#     #want to create a 3d matrix with lat, long, time, and co2 value.
#     # Want to add up all co2 values for the year then add this to an excel spreadsheet.
#     # For baltimore, want to have a sheet for every year, and then a dataframe with sector as the first column name,
#     # co2_24hr, then co2_3hr. co2_3hr will be the co2 added up just between say 1 and 4.
#     #Try to make this all a function then repeat this for hestia LA when Geoff sends the data
#
#
# precip_nc_file = 'file_path'
# nc = netCDF4.Dataset(precip_nc_file, mode='r')
#
# nc.variables.keys()
#
# lat = nc.variables['lat'][:]
# lon = nc.variables['lon'][:]
# time_var = nc.variables['time']
# dtime = netCDF4.num2date(time_var[:],time_var.units)
# precip = nc.variables['precip'][:]
#
# #
#
# # a pandas.Series designed for time series of a 2D lat,lon grid
# precip_ts = pd.Series(precip, index=dtime)
#
# precip_ts.to_csv('precip.csv',index=True, header=True)
#
#
# # Select only relevant times
#
# #Export .xlsx