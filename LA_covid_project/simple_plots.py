# This script creates a few simple plots for the LA Covid project

#-- Load packages
import pandas as pd
import numpy as np
import sys
sys.path.append("/code/functions/")
from plotting_functions import york_fit, fit_plot
from scipy import stats
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

save_path ="H:/figures/LA_covid_project/"

####
#Indianapolis traffic RCO decrease
####

date = ["2011", "2014", "2017"]
RCO = [30, 26, 19]

fig = px.bar(x=date, y=RCO, text=RCO).update_layout(xaxis_title="Year",
                                 yaxis_title="R<sub>CO</sub> (ppb/ppm)",
                                 title="Indianapolis Traffic R<sub>CO</sub>")
fig.update_traces(marker_color = "green")
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False, range=[0,65])

fig.update_layout(
    font_size=20,
    title_x=0.5,
    width=600,
    height=800,
    uniformtext_minsize=14
)
pio.renderers.default = "browser"

fig.show()
pio.write_image(fig, save_path+"Auckland_traffic_bar_graph"+".png", scale=1, width=1400, height=850)



####
#Auckland traffic RCO decrease
###

date = ["2001", "2006", "2011", "2016"] #2019
RCO = [64, 47, 30, 20] #16


fig = px.bar(x=date, y=RCO, text=RCO).update_layout(xaxis_title="Year",
                                 yaxis_title="R<sub>CO</sub> (ppb/ppm)",
                                 title="Auckland Traffic R<sub>CO</sub>")
fig.update_traces(marker_color = "blue")
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False, range=[0,65])

fig.update_layout(
    font_size=20,
    title_x = 0.5,
    width = 600,
    height = 800,
    uniformtext_minsize = 18
)
pio.renderers.default = "browser"
fig.show()
pio.write_image(fig, save_path+"Auckland_traffic_bar_graph"+".png", scale=1, width=1400, height=850)

####
#LA traffic RCO decrease CARB
####

date = ["2011", "2015", "2019"]
RCO = [13, 9, 7]

fig = px.bar(x=date, y=RCO, text=RCO).update_layout(xaxis_title="Year",
                                 yaxis_title="R<sub>CO</sub> (ppb/ppm)",
                                 title="LA CARB Traffic R<sub>CO</sub>")

fig.update_traces(marker_color = "red")
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False, range=[0,65])

fig.update_layout(
    font_size=20,
    title_x = 0.5,
    width = 600,
    height = 800,
    uniformtext_minsize = 14
)

fig.show()
pio.write_image(fig, save_path+"Auckland_traffic_bar_graph"+".png", scale=1, width=1400, height=850)

####
#LA traffic RCO decrease NEI
####

date = ["2011", "2014", "2017"]
RCO = [13, 8, 6]

fig = px.bar(x=date, y=RCO, text=RCO).update_layout(xaxis_title="Year",
                                 yaxis_title="R<sub>CO</sub> (ppb/ppm)",
                                 title="LA NEI Traffic R<sub>CO</sub>")

fig.update_traces(marker_color = "purple")
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False, range=[0,65])

fig.update_layout(
    font_size=20,
    title_x = 0.5,
    width = 600,
    height = 800,
    uniformtext_minsize = 14
)

fig.show()
pio.write_image(fig, save_path+"Auckland_traffic_bar_graph"+".png", scale=1, width=1400, height=850)

####
#NEC traffic RCO decrease CARB
####

date = ["2011", "2014", "2017"]
RCO = [18, 19, 13]

fig = px.bar(x=date, y=RCO, text=RCO).update_layout(xaxis_title="Year",
                                 yaxis_title="R<sub>CO</sub> (ppb/ppm)",
                                 title="NEC NEI Traffic R<sub>CO</sub>")

fig.update_traces(marker_color = "orange")
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False, range=[0,65])

fig.update_layout(
    font_size=20,
    title_x=0.5,
    width=600,
    height=800,
    uniformtext_minsize=14
)

fig.show()
pio.write_image(fig, save_path+"Auckland_traffic_bar_graph"+".png", scale=1, width=1400, height=850)

####
#Traffic RCO decrease plot all cities
####

AKL_data = pd.DataFrame({"date" : [2001, 2006, 2011, 2016, 2019], "RCO" : [64, 47, 30, 20, 16]})
LA_CARB_data = pd.DataFrame({"date" : [2011, 2015, 2019], "RCO" : [13, 9, 7]})
LA_NEI_data = pd.DataFrame({"date" : [2011, 2014, 2017], "RCO" : [13, 8, 6]})
INDY_data = pd.DataFrame({"date" : ["2011", "2014", "2017"], "RCO" : [30, 26, 19]})
NEC_data = pd.DataFrame({"date" : ["2011", "2014", "2017"], "RCO" : [18, 19, 13]})

fig = px.scatter().update_layout(yaxis_title="R<sub>CO</sub> (ppm/ppb)",
                                 xaxis_title="Year",
                                 title="Traffic R<sub>CO</sub> decrease")

fig.add_trace(go.Scatter(x=AKL_data["date"], y=AKL_data["RCO"], line=dict(color="blue"), name="AKL (2016)"))
fig.add_trace(go.Scatter(x=INDY_data["date"], y=INDY_data["RCO"], line=dict(color="green"), name="IND (NEI 2014)"))
fig.add_trace(go.Scatter(x=NEC_data["date"], y=NEC_data["RCO"], line=dict(color="orange"), name="NEC (NEI 2014)"))
fig.add_trace(go.Scatter(x=LA_CARB_data["date"], y=LA_CARB_data["RCO"], line=dict(color="red"), name="LA (CARB "
                                                                                                       "2015)"))
fig.add_trace(go.Scatter(x=LA_NEI_data["date"], y=LA_NEI_data["RCO"], line=dict(color="purple"), name="LA (NEI 2014)"))


fig.update_traces(marker={'size': 16})


fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)

fig.update_layout(
    font_size=20,
    title_x=0.5,
    width=1300,
    height=800,
    uniformtext_minsize=14,
    legend=dict(
                      yanchor="top",
                      y=0.99,
                      xanchor="right",
                      x=0.99
                  )
)

####
# Stacked bar graph of all emissions
####

sectors = ["On-road", "Off-road", "Domestic", "Industrial", "Airport", "Rail", "Total"]

fig = go.Figure(data=[
    go.Bar(name='Auckland (2016)', x=sectors, y=[20, 6, 64, 2, 4, 9, 20]),
    go.Bar(name='Indianapolis (NEI 2014)', x=sectors, y=[26, 71, 2, 2, 9, 1, 14]),
    go.Bar(name='LA (NEI 2014)', x=sectors, y=[8, 72, 1, 1, 6, 4, 8]),
    go.Bar(name='LA (CARB 2015)', x=sectors, y=[9, 88, 2, 1, 8, 3, 9]),
    go.Bar(name='NEC (NEI 2017)', x=sectors, y=[13, 154, 2, 1, 6, 11, 8])
])

fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_layout(xaxis_title = "Emission Sector",
                  yaxis_title="RCO (ppb/ppm)",
                  barmode='group',
                  font_size=20,
                  title_x=0.5,
                  width=1600,
                  height=1000,
                  uniformtext_minsize=14,
                  legend=dict(
                      yanchor="top",
                      y=0.99,
                      xanchor="right",
                      x=0.99
                  )
                  )
fig.show()



###
#Flask to inventory (corrected) bar plot
###

pio.renderers.default = ""
category = ["Auckland (2016)", "Indianapolis (NEI 2014)", "LA (CARB 2015)", "NEC (NEI 2017)"]
category2 = ["Auckland (2016)", "Indianapolis (NEI 2014)"]

fig = go.Figure(data=[
    go.Bar(name='Original Inventory R<sub>CO</sub>', x=category, y=[20, 14, 9, 8]),
    go.Bar(name='Corrected Inventory R<sub>CO</sub>', x=category, y=[12, 8, 9, 8]),
    go.Bar(name='Flask R<sub>CO</sub>', x=category, y=[11, 7, 10.5, 7], error_y=dict(type='data', array=[1, 1, 1, 1]))
])

# fig = go.Figure(data=[
#     go.Bar(name='Original Inventory RCO', x=category, y=[20, 14]),
#     go.Bar(name='Corrected Inventory RCO', x=category, y=[12, 8]),
#     go.Bar(name='Flask RCO', x=category, y=[11, 7], error_y=dict(type='data', array=[1, 1]))
# ])
#
# fig2 = go.Figure(data=[
#     go.Bar(name='Original Inventory RCO', x=category, y=[9, 8]),
#     go.Bar(name='Flask RCO', x=category, y=[10.5, 7], error_y=dict(type='data', array=[1, 1]))
# ])
#
# fig3 = go.Figure(data=[fig, fig2])



fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_layout(xaxis_title="",
                  yaxis_title="R<sub>CO</sub> (ppb/ppm)",
                  barmode='group',
                  font_size=20,
                  title_x=0.5,
                  width=1600,
                  height=1000,
                  uniformtext_minsize=14,
                  legend=dict(
                      yanchor="top",
                      y=0.99,
                      xanchor="right",
                      x=0.99
                  )
                  )

pio.renderers.default = "browser"
fig.show()

# # Hide a specific bar by setting its opacity to 0 (e.g., hide the second bar in Category 1)
# fig.update_traces(marker=dict(opacity=1), selector=dict(name='Corrected Inventory RCO'))
# fig.update_traces(marker=dict(opacity=0), selector=dict(name='Corrected Inventory RCO["LA (CARB 2015)]'))
#
# # Show the chart
# fig.show()


####
#Plotting Harding Street Powerplant
####

data = pd.read_csv("H:/data/LA_covid_project/raw_data/harding_street_unit_data_aggregated.csv")

# data = data.loc[(data["Hour"] >1) & (data["Hour"] <7),:]
data['datetime'] = pd.to_datetime(data.Date.astype(str) + " " + data.Hour.astype(str), format='%d/%m/%Y %H')
data = data[["datetime","CO2 Mass (short tons)"]]
total_data = data.groupby(['datetime'], axis=0, as_index=False).sum()
counts = data.groupby(['datetime'], axis=0, as_index=False).count()

total_data = pd.merge(total_data, counts, on="datetime")

total_data.rename(columns = {"CO2 Mass (short tons)_x":'CO2', "CO2 Mass (short tons)_y": "counts"}, inplace = True)
total_data["CO2_avg"] = total_data.loc[:,"CO2"]/total_data.loc[:,"counts"]

#try find a way to split this up by month

fig = px.scatter(x=total_data["datetime"], y=total_data["CO2"]
                 ).update_layout(xaxis_title="Date",
                                 yaxis_title="CO<sub>2</sub> (tons)",
                                 title="Harding Street Power Plant")
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)

fig.update_layout(
    font_size=20,
    title_x = 0.5,
    width = 1000,
    height = 800
)


fig.show()


#####
#Harding Street CO2 data
#####

####
#NEC traffic RCO decrease CARB
####

month = ["1", "2", "3", "4", "5", "6", "7", "8",  "9", "10", "11", "12"]
CO2 = [294, 386, 83, 132, 97, 203, 233, 222, 232, 148, 185, 147]

fig = px.bar(x=month, y=CO2, text=CO2).update_layout(xaxis_title="Month (2016)",
                                 yaxis_title="Average CO<sub>2</sub> (Tons)",
                                 title="Harding Street Power Plant CO<sub>2</sub> Production")

fig.update_traces(marker_color = "orange")
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline=False)

fig.update_layout(
    font_size=20,
    title_x=0.5,
    width=800,
    height=800,
    uniformtext_minsize=14
)

fig.show()
pio.write_image(fig, save_path+"Auckland_traffic_bar_graph"+".png", scale=1, width=1400, height=850)
