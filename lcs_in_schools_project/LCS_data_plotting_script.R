require(readxl)
require(lubridate)
require(dplyr)
require(ggplot2)
require(gridExtra)
require(grid)
require(fpc)
require(gdata)
require(data.table)
require(ggiraph)
library(hms)
require(sqldf)
require(plotly)

#Need a section here that makes a folder with the CO2 and CO data in UTC that are hour averaged and minute averaged.

setwd("H:/Decarbonisation_of_schools_project/")

URL_1 <- "http://128.32.208.8/node/237/measurements_all/csv?name=New%20Zealand%204&interval="
freq <- 60
URL_2 <- "&variables=co2_corrected_avg_t_drift_applied,co2_dry_sync&start=2023-06-01%2008:00:00&end="
end_date <- "2023-06-15"
URL_3 <- '%2009:00:00&chart_type=measurement'
species <- "co2"

average_type = "hour"

URL_total <- paste0(URL_1, as.character(freq), URL_2, end_date, URL_3)
filename <- paste0("data/", species, "_", freq, ".csv")

download.file(URL_total, filename, method = "auto", quiet = FALSE, mode = "w", cacheOK = TRUE)


#Reading in the data

LCS_data <-read.csv(filename) %>%
  select(datetime, co2_corrected_avg_t_drift_applied)

colnames(LCS_data) <- c("datetime", "co2")

LCS_data$datetime_utc <- ymd_hms(LCS_data$datetime)

LCS_data$datetime_utc <- force_tz(LCS_data$datetime_utc, tzone = "UTC")
LCS_data$datetime_nz <- with_tz(LCS_data$datetime_utc, tzone = "Pacific/Auckland")
LCS_data$day_type <- 

if(average_type == "hour"){
  
  LCS_data <- group_by(LCS_data, datetime_nz = cut(datetime_nz, breaks = "1 hour")) %>%
    summarise(co2 = mean(co2))
  
  
  
}

LCS_data$hour <- as_hms(LCS_data$datetime_nz)
LCS_data$day <- as.Date(LCS_data$datetime_nz)
LCS_data$wday <- wday(LCS_data$datetime_nz)

#create a data set for polygons with weekday days
weekdays <- filter(LCS_data, wday != 6 & wday != 7)
weekdays <- unique(weekdays$day)
weekdays_7_to_9 <- data.frame(start = weekdays + hours(7), end = weekdays + hours(9))
weekdays_2_to_4 <- data.frame(start = weekdays + hours(14), end = weekdays + hours(16))
weekday_rush_hour <- rbind(weekdays_7_to_9, weekdays_2_to_4)


#Want a function here just showing all of the data with the rush hour times highlighted
plot_all_data <- function(data, species, average_type, rush_hour_period) {
    
  
  CO2_plot <- plot_ly(x = data$datetime_nz, y = data$co2, type = 'scatter', mode = 'liness', 
                      line = list(width = 1, color = "blue"),
                      name = "CO<sub>2</sub>", width = 1000, height = 700) %>%
    layout(plot_bgcolor = '#F7F7F7',
           xaxis = list(title = "Date (NZST)", autorange = TRUE,
                        rangeselector = list(
                          type = "date",
                          buttons = list(
                            list(
                              count = 1, label = "1 day", step = "day", stepmode = "backward"),
                            list(
                              count = 7, label = "1 wk", step = "day", stepmode = "backward"),
                            list(
                              count = 1, label = "1 mo", step = "month", stepmode = "backward"),
                            list(
                              count = 3, label = "3 mo", step = "month", stepmode = "backward"),
                            list(
                              count = 6, label = "6 mo", step = "month", stepmode = "backward"),
                            list(
                              count = 1, label = "1 yr", step = "year", stepmode = "backward"),
                            list(step = "all")))), 
           yaxis = list(title = " CO<sub>2</sub> (ppm)"))
  
  for(period in 1:nrow(weekday_rush_hour)){
    
    CO2_plot <- add_polygons(CO2_plot, x = c(rush_hour_period$start[period], rush_hour_period$start[period],
                                             rush_hour_period$end[period], rush_hour_period$end[period]),
                             y = c(min(na.omit(data$co2)), max(na.omit(data$co2)), 
                                      max(na.omit(data$co2)), min(na.omit(data$co2))), 
                             color = I("grey"), showlegend = F, opacity = 0.5, hoverinfo = "none")
    
    
  }
  
  CO2_plot
  
  
}

plot_all_data(LCS_data, "co2", "hour", weekday_rush_hour)

#Want a function here plotting weekly averages

plot_weekly_averages <- function(data, species, average_type, rush_hour_period){
  
  data <- group_by(LCS_data, wday, hour) %>%
    summarise(co2 = mean(co2))
  
  
  
}

plot_weekly_averages(LCS_data, "co2", "hour", weekday_rush_hour)




print(plot_all_data)

#Want a section here showing weekly averages for each day, Monday through Sunday. 



#Want a section here just showing 24 hour averages

LCS_data <- group_by(LCS_data, datetime_nz = cut(datetime_nz, breaks = "20 min")) %>%
  summarise(co2 = mean(co2))
LCS_data$datetime_nz <- ymd_hms(LCS_data$datetime_nz)

class(LCS_data$datetime_nz)

LCS_data$wday <- wday(LCS_data$datetime_nz)
LCS_data$time <- as_hms(LCS_data$datetime_nz)

#averaging weekday data over 24 hour period

weekday_data <- filter(LCS_data, wday != 6 & wday != 7)

day_data <- group_by(weekday_data, time = cut(time, breaks = "20 mins")) %>%
  summarize(co2 = mean(co2))

CO2_plot <- plot_ly(x = day_data$time, y = day_data$co2, type = 'scatter', mode = 'lines+markers', 
                    line = list(width = 1, color = "blue"),
                    name = "CO<sub>2</sub>", width = 1600, height = 700) %>%
  layout(plot_bgcolor = '#F7F7F7',
         xaxis = list(title = "Date (NZST)", autorange = TRUE,
                      rangeselector = list(
                        type = "date",
                        buttons = list(
                          list(
                            count = 1, label = "1 day", step = "day", stepmode = "backward"),
                          list(
                            count = 7, label = "1 wk", step = "day", stepmode = "backward"),
                          list(
                            count = 1, label = "1 mo", step = "month", stepmode = "backward"),
                          list(
                            count = 3, label = "3 mo", step = "month", stepmode = "backward"),
                          list(
                            count = 6, label = "6 mo", step = "month", stepmode = "backward"),
                          list(
                            count = 1, label = "1 yr", step = "year", stepmode = "backward"),
                          list(step = "all")))), 
         yaxis = list(title = " CO<sub>2</sub> (ppm)"))

CO2_plot

rush_hour_data <- filter(LCS_data, (time >= as_hms("07:00:00") & time <= as_hms("09:00:00")) | 
                         time >= as_hms("14:30:00") & time <= as_hms("15:30:00"))
rush_hour_data <- filter(rush_hour_data, wday != 6 & wday != 7 )

ymd(rush_hour_data$datetime_nz[1])
rush_hour_data$datetime_nz[length(rush_hour_data)]


non_rush_data <- anti_join(LCS_data, rush_hour_data)





CO2_plot <- plot_ly(x = LCS_data$datetime_nz, y = rush_hour_data$co2, type = 'scatter', mode = 'markers', 
                    line = list(width = 1, color = "blue"),
                    name = "CO<sub>2</sub>", width = 1600, height = 700) %>%
  layout(plot_bgcolor = '#F7F7F7',
         xaxis = list(title = "Date (NZST)", autorange = TRUE,
                      rangeselector = list(
                        type = "date",
                        buttons = list(
                          list(
                            count = 1, label = "1 day", step = "day", stepmode = "backward"),
                          list(
                            count = 7, label = "1 wk", step = "day", stepmode = "backward"),
                          list(
                            count = 1, label = "1 mo", step = "month", stepmode = "backward"),
                          list(
                            count = 3, label = "3 mo", step = "month", stepmode = "backward"),
                          list(
                            count = 6, label = "6 mo", step = "month", stepmode = "backward"),
                          list(
                            count = 1, label = "1 yr", step = "year", stepmode = "backward"),
                          list(step = "all")))), 
         yaxis = list(title = " CO<sub>2</sub> (ppm)"))





CO2_plot <- CO2_plot %>%
      add_trace(x = non_rush_data$datetime_nz, y = non_rush_data$co2, type = 'scatter', line = list(width = 1, color = "red"))




CO2_plot



plot <- ggplot() + theme_linedraw() +
  geom_point(data = LCS_data, aes(x=datetime_nz, y=co2)) +
  labs(y = "CO2 (ppm)", x = 'Time', title = "LCS at Meadowbank") 

print(girafe(code=print(plot),height_svg=4, width_svg = 7))

LCS_data$time <- as_hms(LCS_data$datetime_nz)

x <- group_by(LCS_data, time) %>%
  summarize(co2 = mean(co2))

CO2_plot <- plot_ly(x = day_data$time, y = day_data$co2, type = 'scatter', mode = 'lines+markers', 
                    line = list(width = 1, color = "blue"),
                    name = "CO<sub>2</sub>", width = 1600, height = 700) %>%
  layout(plot_bgcolor = '#F7F7F7',
         xaxis = list(title = "Date (NZST)", autorange = TRUE,
                      rangeselector = list(
                        type = "date",
                        buttons = list(
                          list(
                            count = 1, label = "1 day", step = "day", stepmode = "backward"),
                          list(
                            count = 7, label = "1 wk", step = "day", stepmode = "backward"),
                          list(
                            count = 1, label = "1 mo", step = "month", stepmode = "backward"),
                          list(
                            count = 3, label = "3 mo", step = "month", stepmode = "backward"),
                          list(
                            count = 6, label = "6 mo", step = "month", stepmode = "backward"),
                          list(
                            count = 1, label = "1 yr", step = "year", stepmode = "backward"),
                          list(step = "all")))), 
         yaxis = list(title = " CO<sub>2</sub> (ppm)"))

CO2_plot





tooltipinfo <- c(paste0('Time = ', LCS_data$time,
                        '\n CO2 (ppm) = ', LCS_data$co2))

plot <- ggplot() + theme_linedraw() +
  geom_point_interactive(data = LCS_data, aes(x=time, y=co2, tooltip = tooltipinfo)) +
  labs(y = "CO2 (ppm)", x = 'Time', title = "LCS at Meadowbank") 

print(girafe(code=print(plot),height_svg=4, width_svg = 7))







