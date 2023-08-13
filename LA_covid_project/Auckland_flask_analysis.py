#-- This script plots the Auckland flask data

#-- Load packages
library(reticulate)

import pandas as pd
import numpy as np
import os
import sys
sys.path.append("/code/functions/")
from plotting_functions import york_fit, fit_plot
import plotly.express as px
import plotly.graph_objects as go

import plotly.io as pio

#-- Set working directories and variables

raw_file_path = "H:/data/LA_covid_project/processed_data/AKL/akl_filtered_data.csv"
plot_path ="H:/figures/LA_covid_project/"
location = "baltimore"

site_type_list = ['Motorway', 'Urban', 'Suburban', 'Downwind', 'Industrial', 'Forest']

flask_data = pd.read_csv(raw_file_path, encoding='latin-1')

flask_data = flask_data.loc[:, ["Date.Collected", "Secondary_Site_Name", "Site.Type", "excess_CO", "excess_CO_error",
                               "CO2ff", "CO2ff_error"]]

flask_data.columns = ["date", "site", "site_type", "COxs", "COxs_err", "CO2ff", "CO2ff_err"]

flask_data = flask_data[flask_data["site_type"] != "Background"][:]

conditions = [
    (flask_data['site_type'] == "Motorway"),
    (flask_data['site_type'] == "Urban"),
    (flask_data['site_type'] == "Suburban"),
    (flask_data['site_type'] == "Downwind"),
    (flask_data['site_type'] == "Industrial"),
    (flask_data['site_type'] == "Forest")
]

values = ['black', 'red', 'yellow', 'blue', 'grey', 'green']

flask_data['colour'] = np.select(conditions, values)

#Plotting
fig = px.scatter(x = flask_data["CO2ff"], y = flask_data["COxs"],
                 error_x = flask_data["CO2ff_err"],
                 error_y = flask_data["COxs_err"],
                 color=flask_data["site_type"],
                 color_discrete_sequence=[
                 "grey", "black", "yellow", "blue", "red", "green"],
                 category_orders={"site_type":["Industrial", "Motorway", "Surburban", "Downwind",
                                                           "Urban", "Forest"]}
                 ).update_layout(yaxis_title="COxs (ppb)",
                                 xaxis_title="CO<sub>2</sub>ff (ppm)",
                                 title="Auckland flask data")

fig.update_traces(marker=dict{'size': 12})

# fig.data[0].error_y.thickness = err_bar_size
# fig.data[1].error_y.thickness = err_bar_size
# fig.data[2].error_y.thickness = err_bar_size
# fig.data[3].error_y.thickness = err_bar_size
# fig.data[4].error_y.thickness = err_bar_size
# fig.data[5].error_y.thickness = err_bar_size
# fig.data[6].error_y.thickness = err_bar_size
# fig.data[0].error_x.thickness = err_bar_size
# fig.data[1].error_x.thickness = err_bar_size
# fig.data[2].error_x.thickness = err_bar_size
# fig.data[3].error_x.thickness = err_bar_size
# fig.data[4].error_x.thickness = err_bar_size
# fig.data[5].error_x.thickness = err_bar_size
# fig.data[6].error_x.thickness = err_bar_size

for site_type in site_type_list:
    site_type_df = flask_data[flask_data["site_type"] == site_type][:]
    fit = york_fit(xi=site_type_df["CO2ff"], yi=site_type_df["COxs"], dxi=site_type_df["CO2ff_err"],
                   dyi=site_type_df["COxs_err"])
    exec(f'{site_type+"_fit"} = {fit}') #create a fit for each site_type

    fig.add_trace(
        go.Scatter(x=np.linspace(min(flask_data["CO2ff"]), max(flask_data["CO2ff"]), 100),
                   y=fit["grad"] * np.linspace(min(flask_data["CO2ff"]), max(flask_data["CO2ff"]), 100) + fit["int"],
                   name=site_type,
                   line_shape="linear",
                   marker=dict(color=site_type_df.iloc[1]["colour"]),
                   showlegend=False))


# fig.add_annotation(x=min(x) + 0.05*(max(x) - min(x)), y=1.1*max(y),
#                    text="y = " + str(round(fit["grad"], 1)) + "x + " + str(round(fit['int'], 1)),
#                    font=dict(size=30),
#                    showarrow=False)
#
# fig.add_annotation(x=min(x) + 0.05*(max(x) - min(x)), y=1*max(y),
#                    text="r<sup>2</sup> = " + str(round(fit["r"], 2)),
#                    font=dict(size=30),
#                    showarrow=False)
#
# fig.add_annotation(x=min(x) + 0.05*(max(x) - min(x)), y=.89*max(y),
#                    text="R<sub>CO</sub> = " + str(round(fit["grad"], 1)) + u" \u00B1 " +
#                         str(math.ceil(fit["grad_err"])),
#                    font=dict(size=30),
#                    showarrow=False)

fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline = False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline = False)

fig.update_layout(legend_title="",
                  legend=dict(
                                yanchor="top",
                                y=0.3,
                                xanchor="right",
                                x=0.99
                                ))

fig.layout.template = "presentation"
fig.show()

pio.write_image(fig, save_path+location.lower()+"_flasks"+".png", scale=1, width=1400, height=850)

fig.write_html(save_path+location.lower()+"_flasks"+".html")

