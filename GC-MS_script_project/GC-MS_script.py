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
from tkinter import filedialog as fd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import openpyxl


# Read in data
#
# # file_path = fd.askopenfilename(title = "Select .xlsx file")  # Why is this hidden?
file_path = "H:/data/GC-MS_script_project/GC-MS_output template.xlsx"
# key_path = "H:/data/GC-MS_script_project/GC-MS_id_keys.xlsx"


data = pd.read_excel(file_path, header=None)
# key_data = pd.read_excel(key_path)

# Acquire data parameters (number of temperature splits, list of temperature ranges, etc)
# Number of ramps

total_ramps = data.iloc[13][0]
ramp_num_list = list(range(1, total_ramps + 1))
title = data.iloc[5][0]

# Saving parameters for full one-step pyrolysis
ramp_data = pd.DataFrame([{'ramp': 0,
                           'start_temp': data.iloc[17][0],
                           'end_temp': data.iloc[17][1]}])

# Adding parameters for each of the individual ramps
for ramp_num in ramp_num_list:
    ramp_start_temp = data.iloc[17][5 + 3 * (ramp_num - 1)]
    ramp_end_temp = data.iloc[17][6 + 3 * (ramp_num - 1)]
    # data_avail = data.iloc[21][5+3*(ramp_num-1)]

    ramp_df = pd.DataFrame([{'ramp': ramp_num,
                             'start_temp': ramp_start_temp,
                             'end_temp': ramp_end_temp}])

    ramp_data = pd.concat([ramp_data, ramp_df], axis=0, ignore_index=True)

GCMS_data_full = data[22:][:]

# Select relevant ramp data
GCMS_data = pd.DataFrame({'category': GCMS_data_full[:][3],
                          'ramp_0': GCMS_data_full[:][1]})
GCMS_data["category"] = GCMS_data["category"].fillna("unknown_source/origin")

for ramp_num in ramp_num_list:
    ramp_data_subset = pd.DataFrame({ramp_num: GCMS_data_full[:][6 + 3 * (ramp_num - 1)]})
    GCMS_data = GCMS_data.assign(**{"ramp_" + str(ramp_num): ramp_data_subset})

GCMS_data = GCMS_data.fillna(0)

# Section here creating a new column next to the identification column called "category" where
# everything is either terrestrial alkane, marine alkanes, cyclic alkane and alkyl benzene, thiophene, phenol, pyrrole,
# PAHs, furan, or unknown. Maybe create a drop down menu for the identification so that it has to be one of X things.
# Could also have an Excel spreadsheet that breaks down which identification goes into what category

# Have a couple of if statements here which

# Calculate integration sums for each category for each ramp
category_list = ["terrestrial_alkanes", "marine_alkanes", "cyclic_alkanes_and_alkylbenzenes", "thiophenes",
                 "phenols", "pyrroles", "PAH", "furans", "unknown_source/origin"]


ramp_data["terrestrial_alkanes_int"] = 0
# ramp_data["terrestrial_alkanes_frac"] = 0
ramp_data["marine_alkanes_int"] = 0
# ramp_data["marine_alkanes_frac"] = 0
ramp_data["cyclic_alkanes_and_alkylbenzenes_int"] = 0
# ramp_data["cyclic_alkanes_and_alkylbenzenes_frac"] = 0
ramp_data["thiophenes_int"] = 0
# ramp_data["thiophenes_frac"] = 0
ramp_data["phenols_int"] = 0
# ramp_data["phenols_frac"] = 0
ramp_data["pyrroles_int"] = 0
# ramp_data["pyrroles_frac"] = 0
ramp_data["PAH_int"] = 0
# ramp_data["PAH_frac"] = 0
ramp_data["furans_int"] = 0
# ramp_data["furans_frac"] = 0
ramp_data["unknown_source/origin_int"] = 0
# ramp_data["unknown_source/origin_frac"] = 0

# ramp_data = ramp_data.fillna(0)

for category in category_list:

    for ramp_num in [0]+ ramp_num_list: #adding 0 to include full ramp
        ramp_data.loc[ramp_num, category + "_int"] = sum(GCMS_data.loc[GCMS_data['category'] == category,
                                                                              "ramp_" + str(ramp_num)])

ramp_data = ramp_data.T
int_data = ramp_data.iloc[3:, :]

# int_data.astype("int")

frac_data = pd.DataFrame(index = ["terrestrial_alkanes_frac", "marine_alkanes_frac",
                              "cyclic_alkanes_and_alkylbenzenes_frac",
                           "thiophenes_frac", "phenols_frac", "pyrroles_frac", "PAH_frac", "furans_frac",
                           "unknown_source/origin_frac"],
                  columns= np.arange(0,total_ramps + 1, 1))

frac_data = frac_data.fillna(float(0))

for ramp_num in ramp_num_list:
    frac_data.iloc[:, ramp_num-1] = int_data.iloc[:, ramp_num-1]/sum(int_data.iloc[:, ramp_num-1])

# Organising data to be plotted up
plot_data = pd.DataFrame(np.array(np.meshgrid(ramp_num_list, category_list)).T.reshape(-1, 2))
plot_data.loc[:, "frac"] = 0
plot_data.columns = ["ramp_num", "category", "frac"]


for ramp_num in ramp_num_list: #Assigning frac values for each ramp and each compound

    for category in category_list:

        plot_data.loc[(plot_data.loc[:,"ramp_num"] == str(ramp_num)) & (plot_data.loc[:,"category"] == category), "frac"] = frac_data.loc[category + "_frac", ramp_num]

plot_data.loc[:, "frac"] = plot_data["frac"]*100


#Plot data
pio.renderers.default = ""
fig = px.bar(plot_data, x="ramp_num", y="frac", color="category", title="Ramp plot").update_layout(
                                 xaxis_title="Ramp Number",
                                 yaxis_title="Fraction (%)",
                                 title=title,
                                 legend=dict(title = "Category"))

# fig = px.bar(df, x="day", y="total_bill", color="smoker", barmode="group", facet_col="sex",
#              category_orders={"day": ["Thur", "Fri", "Sat", "Sun"],
#                               "smoker": ["Yes", "No"],
#                               "sex": ["Male", "Female"]})
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)

fig.update_layout(
    font_size=20,
    title_x = 0.15,
    width = 1200,
    height = 800,
    uniformtext_minsize = 14
)
# pio.renderers.default = "browser"
# fig.show()


# Saves data
# fig.to_image(format="png", engine="kaleido")
# fig.to_image(format="png", engine="orca")
# plotly.io.orca.config.save()
# fig.write_image("title.png")
# pio.write_image(fig, os.path.dirname(file_path)+"/"+title+".png", format = "png")
# fig.write_image(os.path.dirname(file_path) + title+".png", engine='orca')
# fig.write_html(os.path.dirname(file_path)+"/"+title+".html")

fig.write_image("C:/Users/haydeny/Desktop/plot.png", format = "png")

#
# import pyimgkit
#
# pyimgkit.from_file(os.path.dirname(file_path)+"/"+title+".html", os.path.dirname(file_path)+"/"+'out.jpg')
