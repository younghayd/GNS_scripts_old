#-- This script converts the hourly .nc.tar.gz files into usable sector totals and outputs it in Excel

#-- Load packages

import os
import tarfile
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta


#-- Set working directories and variables

unzip = True # Set true if you want to start from .nc.tar.gz files. Set False if you are starting from .nc files

city = "baltimore"

year_list =  ["2010", "2011", "2012", "2013", "2014", "2015"]
sector_list = ["Onroad", "Nonroad", "Residential", "Commercial", "Industrial", "Airport", "Rail", "ElecProd", "CMV",
               "Cement"]

raw_file_path = "H:/data/LA_covid_project/raw_data/inventory_CO2_data/baltimore/hestia_nc_files/hourly/zipped/"
nc_file_path = "H:/data/LA_covid_project/raw_data/inventory_CO2_data/baltimore/hestia_nc_files/hourly/nc/"
processed_data_path = "H:/data/LA_covid_project/processed_data/baltimore/"

#-- Define function
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
        file = tarfile.open(raw_data_loc + tar_gz_filename)
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

def calculate_co2_totals_during_flask_collection_period(nc_file, hour_start, hour_end):
    """
    calculate_co2_totals takes in the 4-D data (lat, lon, time, and kgC) for a given year. It calculates the total kgC
    measured during a certain time range (likely between 1 pm (13) and 4 pm (16)). This is for better comparison
    between inventory and flasks measured during mid afternoon. While CO data won't be measured by hour, can use
    sector totals to see which sectors are more dominant at this time and can infer whether this would increase
    the RCO of the inventory data when comparing to flasks.

    :param nc_file: .nc file, specific for a year and sector.
    :param hour_start: beginning hour of data range
    :param hour_end: end hour of data range
    :return: kgC of CO2 over the year only between 
    """
    
    start_date = datetime(int(year), 1, 1, 0, 00)
    end_date = datetime(int(year) + 1, 1, 1, 0, 00)

    date_array = pd.DataFrame(columns = ['datetime'])

    # Creating a datetime dataframe for the year, in steps of 1 hour
    for single_date in daterange(start_date, end_date):
        day_array = pd.DataFrame(data=[single_date.strftime("%Y-%m-%d %H:%M")], columns=["datetime"])
        date_array = pd.concat([date_array, day_array])

    date_array['datetime'] = pd.to_datetime(date_array['datetime'])

    # Selecting datetimes in date_array that correspond to flask times (mid afternoon).
        # +1 on hour_start accounts for fact that hour 13 corresponds to the period of 12 pm to 1 pm, not 1 pm to 2 pm.
    selected_values = date_array[
        (date_array['datetime'].dt.hour >= hour_start + 1) & (date_array['datetime'].dt.hour <= hour_end)
        ]

    #Converting selected datetimes to hours of year to match with Hestia

    selected_values['year'] = selected_values['datetime'].dt.year
    selected_values['start_of_year'] = pd.to_datetime(selected_values['year'], format='%Y')

    # Calculate the time difference in hours and convert into list of ints
    selected_values['hours_of_year'] = (selected_values['datetime'] - selected_values['start_of_year']).dt.total_seconds() / 3600
    selected_hours = selected_values['hours_of_year'].tolist()
    selected_hours = [int(i) for i in selected_hours]
    
    # Subtract 1 since Hestia starts at hour 1 and python starts on index 0
    selected_hours = [i -1 for i in selected_hours]

    #sum over lon and lat across time so you are left with a time series of kgC across space
    time_series = nc_file.sum(dim=["X", "Y"])
    time_series = time_series.to_dataframe()

    #select flask hours from Hestia using selected_hours and sum over those hours for the whole year
    selected_times = time_series.iloc[selected_hours]
    co2_3_hour = selected_times.sum().item()

    return co2_3_hour

#-- Running code begins here

# Unzipping .nc.tar.gz files
if unzip == True:
    tar_gz_unzip(raw_file_path, nc_file_path)   


nc_list = os.listdir(nc_file_path)

# Filter out annual files
nc_list = [filename for filename in nc_list if "hourly" in filename]

# Saving processed values into multiple sheets within an Excel spreadsheet
with pd.ExcelWriter(processed_data_path + city + "_hestia_co2_sector_totals.xlsx") as writer:
    
    for year in year_list:

        print(year)
        
        # Initialising data frame that will be saved as an Excel sheet and row of total kgC
        all_sector_data = pd.DataFrame(columns = ["Sector", "CO2_24_hr (kgC)", "CO2_1pm-4pm (kgC)"])
        total_24_hour = 0
        total_3_hour = 0
        
        # Filtering for chosen year
        file_list = [filename for filename in nc_list if year in filename]

        for sector in sector_list:

            print(sector)
            file_address = next(filename for filename in file_list if sector in filename)

            nc_file = xr.open_dataset(nc_file_path + file_address)
            
            # Finds CO2 over the full year
            co2_24_hour = nc_file["Carbon Emissions"].sum().item()

            co2_3_hour =  calculate_co2_totals_during_flask_collection_period(nc_file, 13, 16)

            # Add data for this sector and year into dataframe
            all_sector_data.loc[len(all_sector_data)] = [sector, co2_24_hour, co2_3_hour]
            
            total_3_hour = co2_3_hour + total_3_hour
            total_24_hour = co2_24_hour + total_24_hour

        # Sum total across all sectors
        all_sector_data.loc[len(all_sector_data)] = ["Total", total_24_hour, total_3_hour]

        # Save year data to an excel sheet
        all_sector_data.to_excel(writer, sheet_name = year, index = False)

