require(readxl)
require(lubridate)
require(dplyr)
require(ggplot2)
require(bfsl)
require(grob)
require(ggiraph)
require(ggbreak)
library(plotly)

setwd("H:/LA_flask_observations/Final_outputs/data/Indy_flask_data/")

onroad_2015 <- 9.1
offroad_2015 <- 96.7
res_2015 <- 3.3
com_2015 <- 1.9
ind_2015 <- 1.2
air_2015 <- 8.5
rail_2015 <- 2.9
total_2015 <- 9.4

onroad_2011 <- 13.2
offroad_2011 <- 101.3
res_2011 <- 2.8
com_2011 <- 2.5
ind_2011 <- 1.3
air_2011 <- 9.3
rail_2011 <- 3.7
total_2011 <- 11.1


data <- data.frame(sector = c("offroad", "offroad","onroad", "onroad","total", "total","air", "air", "rail", "rail", "res", "res", "com", "com", "ind", "ind"),
                     year = c(2011, 2015,2011, 2015,2011, 2015,2011, 2015,2011, 2015,2011, 2015,2011, 2015,2011, 2015),
                     RCO = c(offroad_2011, offroad_2015, onroad_2011, onroad_2015,total_2011, total_2015, air_2011, air_2015, rail_2011, rail_2015, 
                             res_2011, res_2015, com_2011, com_2015, ind_2011, ind_2015))

cutinterval = c(15, 95)

plot <- plot_ly()

offroad_data <- filter(data, sector == "offroad")
main_data <- filter(data, sector != "offroad")


for(type in unique(main_data$sector)){
  type_data <- filter(main_data, sector == type)
  plot <- add_trace(plot, x =~year, y = ~RCO, data = type_data, type = "scatter", mode = "markers+lines", name = type)
  
}

plot2 <- plot_ly(data = offroad_data)
plot2 <- add_trace(plot2, x =~year, y = ~RCO, data = offroad_data, type = "scatter", mode = "markers+lines", name = "offroad") 
 
fig <- subplot(plot2, plot,nrows = 2, shareX=TRUE, margin = 0.02)

fig <- layout(fig, yaxis2 = list(range = c(0, cutinterval[1])),
              plot_bgcolor = "white",
              title = "LA flask RCO time series",
             yaxis = list(range = c(cutinterval[2], 102),
                          title = "RCO (ppb/ppm)"
                          ),
             xaxis = list(
               tickvals = list(2011, 2015),
               title = "Year"
             )
             
             )
fig 

