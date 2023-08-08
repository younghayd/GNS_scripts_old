#-- This script plots the Indianapolis flask data

#-- Load packages
import pandas as pd
import sys
sys.path.append("/code/functions/")
from plotting_functions import york_fit, fit_plot

#-- Set working directories and variables
raw_file_path = "H:/data/LA_covid_project/raw_data/flask_data/indy_flask_data.xlsx"
plot_path ="H:/figures/LA_covid_project/"
location = "indy"

flask_data = pd.read_excel(raw_file_path, skiprows=14)

#flask_data["CO_err"] = 5 #arbitrary number from average CO error for AKL flasks, might need to change this
#flask_data["COxs_err"] = (2 * flask_data["CO_err"] ** 2 ) **0.5

flask_data["CO2_unc"] = 0.05 #Uncertainty from Jocelyn's email
flask_data["CO_unc"] = 12 #Uncertainty from the standard deviation of hourly avg picarro data from tower 2 in Indy

flask_data["CO2xs_unc"] = flask_data["CO2_unc"]
flask_data["COxs_unc"] = flask_data["CO_unc"]*2/(2**0.5)

flask_data = flask_data[['LOC', 'DATE', 'LAT', 'LON', 'CO2FFXS', 'CO2FFUNC', 'CO2C14FLAG',
                         'CO2XS', 'CO2xs_unc', 'CO2', 'CO2_unc', 'CO2FLAG', 'COXS', 'COxs_unc',
                         'CO', 'CO_unc', 'COFLAG', 'BGTYPE', 'ID']]

flask_data.columns = ["site", "date", "lat", "lon", "CO2ff", "CO2ff_err", "CO2C14_flag",
                      "CO2xs", "CO2xs_err", "CO2", "CO2_err", "CO2_flag", "COxs", "COxs_err",
                      "CO", "CO_err", "CO_flag", "bg", "ID"]


flask_data = flask_data.loc[(flask_data['CO_flag'] == "...")]
flask_data = flask_data.loc[(flask_data['CO2C14_flag'] == "...")|  (flask_data["CO2C14_flag"]  == '..M') | (flask_data["CO2C14_flag"]
                                                                                                  == '..S')]
flask_data = flask_data.loc[(flask_data['COxs'] > -900)]
flask_data = flask_data.loc[(flask_data['CO2ff'] > -900)]


flask_data = flask_data[flask_data['ID'] != '3058-09']
flask_data = flask_data[flask_data['ID'] != '3151-05']
flask_data = flask_data[flask_data['ID'] != '3057-01']
flask_data = flask_data[flask_data['ID'] != '3503-03']
flask_data = flask_data[flask_data['ID'] != '3033-03']
flask_data = flask_data[flask_data['ID'] != '3154-01']


fit = york_fit(xi=flask_data["CO2ff"], yi=flask_data["COxs"], dxi=flask_data["CO2ff_err"], dyi=flask_data["COxs_err"])

plot = fit_plot(df=flask_data,
                x=flask_data["CO2ff"], x_err=flask_data["CO2ff_err"],
                y=flask_data["COxs"],  y_err=flask_data["COxs_err"],
                fit=fit, location=location,
                save_path=plot_path,
                marker_size = 8,
                err_bar_size = 0.3)








indy_data <- read_excel("data/Indy_flask_data/towers_enhancements_bkgdT1_20230412.xlsx", skip = 14) %>%
  select(LOC, DATE, LAT, LON, CO2FFXS, CO2FFUNC, CO2C14FLAG, CO2XS, CO2, CO2FLAG, COXS, CO, COFLAG, BGTYPE, ID)%>%
  filter(CO2FFXS > -999, CO > -999)

indy_data <- filter(indy_data, indy_data$DATE < 2020.2)

indy_data$ID <- as.character(indy_data$ID)

colnames(indy_data) <- c("Tower","date","lat","lon","CO2ff","CO2ff_unc","CO2C14_flag" , "CO2xs", "CO2", "CO2_flag", "COxs", "CO", "COFLAG", "bg_type", "ID")
indy_data$Tower <- as.numeric(substring(indy_data$Tower,2))
indy_data <- indy_data[order(indy_data$Tower),]
indy_data$Tower <- as.character(indy_data$Tower)

indy_data$CO2_unc <- 0.05 #Uncertainty from Jocelyn's email
indy_data$CO_unc <- 12 #Uncertainty from the standard deviation of hourly avg picarro data from tower 2 in Indy

indy_data$CO2xs_unc <- indy_data$CO2_unc
indy_data$COxs_unc <- indy_data$CO_unc*2/sqrt(2)



#Removing outliers
indy_data <- subset(indy_data, ID != '3058-09')
indy_data <- subset(indy_data, ID != '3151-05')
indy_data <- subset(indy_data, ID != '3057-01')
indy_data <- subset(indy_data, ID != '3503-03')
indy_data <- subset(indy_data, ID != '3033-03')
indy_data <- subset(indy_data, ID != '3154-01')

tooltipinfo <- c(paste0('Tower = ', indy_data$Tower,
                        '\n Date = ', indy_data$date,
                        '\n CO2xs = ', round(indy_data$CO2xs,2),
                        '\n COxs = ', round(indy_data$COxs,2),
                        '\n CO2ff = ', round(indy_data$CO2ff,2),
                        '\n ID = ', indy_data$ID))


x_lab_ff <- expression('CO'['2']*'ff (ppm)')
y_lab_ff <- "COxs (ppb)"