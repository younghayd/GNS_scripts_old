"""

This script reads in the Excel spreadsheet from Sebastian Naeher containing ramped pyrolysis data
from the GC-MS spectra. The GC-MS outputs a spectra of relative abundance against the retention time of the
GC-MS. Sebastian manually assigns each peak a corresponding compound name and then integrates the peak. Thus,
each peak has a retention time and an integration value. This is obtained for the sample over the full temperature
range, and also over individual temperature ranges. The script will read this data in and group each sample into
a sample category. By summing up the integrations of each category and then finding the relative abundance of each
sample group, the script will plot up the relative abundances for each of the sample types and then save these plot.

"""
# Import packages
import tkinter as tk
from tkinter import filedialog

import numpy as np
import pandas as pd



# Read in data
# add file explorer prompt?

# root = tk.Tk()
# root.withdraw()
#
# file_path = filedialog.askopenfilename()

file_path = "H:/data/GC-MS_script_project/GC-MS_output template.xlsx"
data = pd.read_excel(file_path, header=None)

# Acquire data parameters (number of temperature splits, list of temperature ranges, etc)

    # Number of ramps

total_ramps = data.iloc[5][0]
ramp_num_list = list(range(1, total_ramps+1))

# Saving parameters for full one-step pyrolysis
ramp_data = pd.DataFrame([{'ramp': 0,
                             'start_temp': data.iloc[16][0],
                             'end_temp': data.iloc[16][1],
                             'data_avail': True}])

# Adding parameters for each of the individual ramps
for ramp_num in ramp_num_list:
    ramp_start_temp = data.iloc[16][5+3*(ramp_num-1)]
    ramp_end_temp = data.iloc[16][6+3*(ramp_num-1)]
    data_avail = data.iloc[19][5+3*(ramp_num-1)]

    ramp_df = pd.DataFrame([{'ramp': ramp_num,
                             'start_temp': ramp_start_temp,
                             'end_temp': ramp_end_temp,
                             'data_avail': data_avail}])

    ramp_data = pd.concat([ramp_data, ramp_df], axis = 0, ignore_index = True)

GCMS_data_full = data[23:][:]

# Select relevant ramp data

GCMS_data = pd.DataFrame({'id': GCMS_data_full[:][2],
                          'full_area': GCMS_data_full[:][1]})

for ramp_num in ramp_num_list:
    ramp_data_subset = pd.DataFrame({ramp_num: GCMS_data_full[:][5+3*(ramp_num-1)]})
    GCMS_data = GCMS_data.assign(**{"ramp_"+str(ramp_num): ramp_data_subset})

GCMS_data = GCMS_data.fillna(0)

# Section here creating a new column next to the identification column called "category" where
# everything is either terrestrial alkane, marine alkanes, cyclic alkane and alkyl benzene, thiophene, phenol, pyrrole,
# PAH, furan, or unknown. Maybe create a drop down menu for the identification so that it has to be one of X things.
# Could also have an Excel spreadsheet that breaks down which identification goes into what category

# Have a couple of if statements here which

# Calculate integration sums for each category for each ramp
category_list = ["TA", "MA", "CA_AB", "TP", "Ph", "Py", "PAH", "Fur", "Unk"]

ramp_data["TA_int"] = ""
ramp_data["TA_frac"] = ""
ramp_data["MA_int"] = ""
ramp_data["MA_frac"] = ""
ramp_data["CA_AB_int"] = ""
ramp_data["CA_AB_frac"] = ""
ramp_data["TP_int"] = ""
ramp_data["TP_frac"] = ""
ramp_data["Ph_int"] = ""
ramp_data["Ph_frac"] = ""
ramp_data["Py_int"] = ""
ramp_data["Py_frac"] = ""
ramp_data["PAH_int"] = ""
ramp_data["PAH_frac"] = ""
ramp_data["Fur_int"] = ""
ramp_data["Fur_frac"] = ""
ramp_data["Unk_int"] = ""
ramp_data["Unk_frac"] = ""

for category in category_list:

    for ramp_num in ramp_num_list:
        ramp_data[category][ramp_num-1] = sum(GCMS_data.loc[GCMS_data['category'] == category, "ramp_"+ramp_num])



# Calculate relative abundances of each compound group

for category in category_list:

    for ramp_num in ramp_num_list:
        ramp_data[category][ramp_num-1] = X/Y)

# Plots up data

# Saves data

# import pandas library as pd
