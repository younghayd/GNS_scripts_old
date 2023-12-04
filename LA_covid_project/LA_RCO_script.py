# This script plots the LA flask data and calculated RCO for each site

import pandas as pd
import numpy as np
import statistics
import os
import sys
sys.path.append("/code/functions/")
from plotting_functions import york_fit, fit_plot
import plotly.express as px
import plotly.graph_objects as go

import plotly.io as pio


#-- Set working directories and variables

raw_file_path = "H:/data/LA_covid_project/raw_data/flask_data/LA_flask_data.csv"
save_path ="H:/figures/LA_covid_project/"
location = "LA"

flask_data = pd.read_csv(raw_file_path, encoding='latin-1')

flask_data = flask_data.loc[:, ["lat", "lon", "sp3val", "COxs", "CO2ff"]]

flask_data["site"] = ""

flask_data.loc[flask_data["lat"] == 34.0216, "site"] = "USC"
flask_data.loc[flask_data["lat"] == 34.2841, "site"] = "GRA"
flask_data.loc[flask_data["lat"] == 33.8802, "site"] = "FUL"


flask_data.columns = ["lat", "lon", "CO", "COxs", "CO2ff", "site"]

flask_data["CO2ff_err"] = 1.2 #From Miller 2020 supp
flask_data["CO_err"] = 5
flask_data["CO_bg"] = flask_data["CO"] - flask_data["COxs"]
flask_data["CO_bg_err"] = statistics.stdev(flask_data["CO_bg"])
flask_data["COxs_err"] = flask_data["CO_bg_err"]

flask_data = flask_data.loc[:, ["site", "CO", "COxs", "COxs_err", "CO2ff", "CO2ff_err"]]

# Setting IDs for easy removal
flask_data["ID"] = flask_data.index
flask_data = flask_data.loc[flask_data["ID"] != 376, :]
flask_data = flask_data.loc[flask_data["ID"] != 372, :]

#Calculating york fits
USC_data = flask_data.loc[flask_data["site"] == "USC", :]
GRA_data = flask_data.loc[flask_data["site"] == "GRA", :]
FUL_data = flask_data.loc[flask_data["site"] == "FUL", :]

USC_fit = york_fit(xi=USC_data["CO2ff"], yi=USC_data["COxs"], dxi=USC_data["CO2ff_err"], dyi=USC_data["COxs_err"])
GRA_fit = york_fit(xi=GRA_data["CO2ff"], yi=GRA_data["COxs"], dxi=GRA_data["CO2ff_err"], dyi=GRA_data["COxs_err"])
FUL_fit = york_fit(xi=FUL_data["CO2ff"], yi=FUL_data["COxs"], dxi=FUL_data["CO2ff_err"], dyi=FUL_data["COxs_err"])


#Plotting
fig = px.scatter(x = flask_data["CO2ff"], y = flask_data["COxs"],
                 error_x = flask_data["CO2ff_err"],
                 error_y = flask_data["COxs_err"],
                 color=flask_data["site"],
                 color_discrete_sequence= ["red", "blue", "green"]
                 ).update_layout(yaxis_title="COxs (ppb)",
                                 xaxis_title="CO<sub>2</sub>ff (ppm)",
                                 title="LA flask data")

fig.update_traces(marker = {'size': 12})

for site_name in ["USC", "GRA", "FUL"]:
    site_df = flask_data[flask_data["site"] == site_name][:]
    fit = york_fit(xi=site_df["CO2ff"], yi=site_df["COxs"], dxi=site_df["CO2ff_err"],
                   dyi=site_df["COxs_err"])
    exec(f'{site_name+"_fit"} = {fit}') #create a fit for each site_type

    fig.add_trace(
        go.Scatter(x=np.linspace(min(flask_data["CO2ff"]), max(flask_data["CO2ff"]), 100),
                   y=fit["grad"] * np.linspace(min(flask_data["CO2ff"]), max(flask_data["CO2ff"]), 100) + fit["int"],
                   name=site_name,
                   line_shape="linear",
                   showlegend=False))


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