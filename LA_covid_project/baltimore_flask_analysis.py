#-- This script plots the Baltimore flask data

#-- Load packages

import os
import tarfile
import xarray as xr
import pandas as pd
import numpy as np
import os
import sys
sys.path.append("/code/functions/")
from plotting_functions import york_fit


#-- Set working directories and variables

raw_file_path = "H:/data/LA_covid_project/raw_data/flask_data/baltimore_flask_data.xlsx"
plot_path ="H:/figures/LA_covid_project/"

flask_data = pd.read_excel(raw_file_path, skiprows=1)

flask_data["CO_err"] = 12 #arbitrary number from hourly std of Indy picarro data, might need to change this
flask_data["COxs_err"] = (2 * flask_data["CO_err"] ** 2 ) **0.5

flask_data = flask_data[["CODE", "DATE", "ID", "LAT", "LON", "CO2FFXS", "CO2FFUNC", "CO2C14FLAG", "CO2FLAG", "COXS",
                         "COxs_err", "COFLAG"]]

flask_data.columns = ["site", "date", "id", "lat", "lon", "CO2ff", "CO2ff_err", "CO2C14_flag", "CO2_flag", "COxs",
                         "COxs_err", "CO_flag"]

flask_data = flask_data.loc[(flask_data['CO2C14_flag'] == "...") & (flask_data['CO2_flag'] == "...") &
               (flask_data['CO_flag'] == "...") & (flask_data['site'] != "TMD")
               & (flask_data["CO2ff"] > -990) & (flask_data["COxs"] > -990)]

flask_data = flask_data.loc[(flask_data["id"] != "3124-03") & (flask_data["id"] != "3006-03")]

york_fit = york_fit(flask_data["CO2ff"], flask_data["COxs"], flask_data["CO2ff_err"], flask_data["COxs_err"])
