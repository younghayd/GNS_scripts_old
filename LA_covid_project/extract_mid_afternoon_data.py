#-- This script selects only the hours corresponding to 1-4 pm from hestia hourly sector data

#-- Load packages

import os
import tarfile
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta


import csv

#-- Set working directories and variables

sector_list = ["Onroad", "Nonroad", "Residential", "Commercial", "Industrial", "Airport", "Rail", "ElecProd", "CMV",
               "Cement"]

raw_file_path = "H:/data/LA_covid_project/raw_data/inventory_CO2_data/LA/CO2_hestia_LA_megacity_hourly_data/"
processed_data_path ="H:/data/LA_covid_project/processed_data/LA/"

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

def extract_mid_afternoon(csv_file):
    """

    :param csv_file:
    :return:
    """
    # Creating a datetime dataframe for the year, in steps of 1 hour

    start_date = datetime(2015, 1, 1, 0, 00)
    end_date = datetime(2016, 1, 1, 0, 00)
    date_array = pd.DataFrame(columns=['datetime'])
    hour_start = 13
    hour_end = 16

    for single_date in daterange(start_date, end_date):
        day_array = pd.DataFrame(data=[single_date.strftime("%Y-%m-%d %H:%M")], columns=["datetime"])
        date_array = pd.concat([date_array, day_array])

    date_array['datetime'] = pd.to_datetime(date_array['datetime'])

    # Selecting datetimes in date_array that correspond to flask times (mid afternoon).
        # +1 on hour_start accounts for fact that hour 13 corresponds to the period of 12 pm to 1 pm, not 1 pm to 2 pm.
    selected_values = date_array[
        (date_array['datetime'].dt.hour >= hour_start) & (date_array['datetime'].dt.hour <= hour_end -1)
        ]


    selected_values['year'] = selected_values['datetime'].dt.year
    selected_values['start_of_year'] = pd.to_datetime(selected_values['year'], format='%Y')

    # Calculate the time difference in hours and convert into list of ints
    selected_values['hours_of_year'] = (selected_values['datetime'] - selected_values['start_of_year']).dt.total_seconds() / 3600
    selected_hours = selected_values['hours_of_year'].tolist()
    return selected_hours


file_list = os.listdir(raw_file_path)

excel_writer = pd.ExcelWriter(processed_data_path + "mid_afternoon_CO2ff_totals.xlsx")

# Saving processed values into multiple sheets within an Excel spreadsheet

for file_name in file_list:
    print(file_name)

    file = pd.read_csv(raw_file_path+file_name)
    # Finds CO2 over the full year

    selected_data = file.loc[extract_mid_afternoon(file_name)]
    # Save year data to an excel sheet
    selected_data.to_excel(excel_writer, sheet_name=file_name, index=False)


excel_writer.close()