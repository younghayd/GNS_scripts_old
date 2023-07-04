############################## LA_RCO_SCRIPT ##############################
# This script calculates the R_CO for LA flask data
# Author: Hayden Young
#
#


### PACKAGES ###

library(readr)
library(readxl)
library(dplyr)
library(ggplot2)
library(ggiraph)
library(ggpubr)
library(r2symbols)
library(dplR)
library(bfsl)
library(grid)
library(ggpmisc)
library(forcats)
library(htmltools)
library(htmlwidgets)
library(lubridate)
library(gridExtra)
library(zoo)
library(plotly)
library(hms)
library(ggmap)

setwd("H:/LA_flask_observations/Data")

#### Organising John Miller's data

LA_data <- read.csv("Allsites_2015_GML.csv")
LA_data$datetime <- make_datetime(year = LA_data$yr, month = LA_data$mo, day = LA_data$dy, hour = LA_data$hr, min = LA_data$mn)
LA_data <- select(LA_data, datetime, lat, lon, sp3val, COxs, CO2ff)
colnames(LA_data) <- c("datetime_utc", "lat", "lon", "CO", "COxs", "CO2ff")

LA_data$CO2ff_err <- 1.2 #From Miller 2020 supp
LA_data$CO_err <- 5
LA_data <- mutate(LA_data, CO_bg = CO - COxs, CO_bg_err = sd(CO_bg), COxs_err = sqrt(CO_bg_err^2 + CO_err^2))


LA_data$site[LA_data$lat == 34.0216] <- "USC"
LA_data$site[LA_data$lat == 34.2841] <- "GRA"
LA_data$site[LA_data$lat == 33.8802] <- "FUL"

LA_data <- select(LA_data, lat, lon,datetime_utc, COxs, COxs_err, CO2ff, CO2ff_err, site)

# 
# #### Organising Sally Newman and Heather Graven's data
# 
# # CO2ff data 
# Pasadena_data <- read.csv("ERL_13_065007_SD_datatable.csv") %>%
#   tail(-9)
# Pasadena_data <- Pasadena_data[, 0:12]
# 
# 
# colnames(Pasadena_data) <- c("Site", "Date", "CO2", "d13C", "D14C", "beta", "beta unc", "ffCO2", "ffCO2 unc",
#                              "prior ffCO2", "post ffCO2", "outlier")
# 
# Pasadena_data <- filter(Pasadena_data, Site == "CIT")
# 
# Pasadena_data$year <- substr(Pasadena_data$Date, 1, 4)
# Pasadena_data$month <- substr(Pasadena_data$Date, 5, 6)
# Pasadena_data$day <- substr(Pasadena_data$Date, 7, 8)
# Pasadena_data$hour <- substr(Pasadena_data$Date, 9, 10)
# Pasadena_data$minute <- substr(Pasadena_data$Date, 11, 12)
# Pasadena_data$datetime <- paste(paste(Pasadena_data$year, Pasadena_data$month, Pasadena_data$day, sep = "-"), paste(Pasadena_data$hour, Pasadena_data$minute, sep = ":"))
# Pasadena_data$datetime <- as.POSIXct(Pasadena_data$datetime)
# 
# # CO data
# 
# # CIT CO data
# Pasadena_CO_data <- read_excel("CO 2013-15 Pasadena for Jocelyn Turnbull.xlsx", sheet = "data")
# Pasadena_CO_data <- select(Pasadena_CO_data, "datetime PST...9", "CO (ppb)", "CO1rav stdev (ppm)")
# 
# colnames(Pasadena_CO_data) <- c("datetime", "CO", "CO_sd")
# Pasadena_CO_data$CO_sd <- Pasadena_CO_data$CO_sd * 1000
# 
# Pasadena_data <- full_join(Pasadena_data,Pasadena_CO_data, by = "datetime")
# Pasadena_data <- Pasadena_data[order(Pasadena_data$datetime),]
# Pasadena_data$CO_est <- na.approx(Pasadena_data$CO)
# Pasadena_data$CO_sd_est <- na.approx(Pasadena_data$CO_sd)
# Pasadena_data <- filter(Pasadena_data, is.na(ffCO2) == FALSE)
# 
# 
# # Backgroun La Jolla CO data
# jolla_CO_data <- read.csv("daily_flask_co2_isotopes_ljo.csv", quote = "", row.names = NULL, stringsAsFactors = FALSE) %>%
#   tail(-110)%>%
#   select(1,2,13)
# 
# colnames(jolla_CO_data) <- c("date", "time", "CO_bg")
# 
# jolla_CO_data <- jolla_CO_data[grepl("N", jolla_CO_data$CO_bg) == FALSE,]
# jolla_CO_data$datetime <- dmy_hm(paste(jolla_CO_data$date, jolla_CO_data$time))
# jolla_CO_data <- filter(jolla_CO_data, datetime < ymd("2015-02-28"))
# 
# Pasadena_data <- full_join(Pasadena_data,jolla_CO_data, by = "datetime")
# Pasadena_data <- Pasadena_data[order(Pasadena_data$datetime),]
# Pasadena_data$CO_bg_est <- na.approx(Pasadena_data$CO_bg)
# 
# Pasadena_data <- filter(Pasadena_data, is.na(ffCO2) == FALSE)
# Pasadena_data$CO_bg_sd_est <- 5
# 
# Pasadena_data <- select(Pasadena_data, datetime, ffCO2, "ffCO2 unc", CO_est, CO_sd_est, CO_bg_est, CO_bg_sd_est)
# Pasadena_data$COxs <- Pasadena_data$CO_est - Pasadena_data$CO_bg_est
# Pasadena_data$COxs_unc <- sqrt(Pasadena_data$CO_sd_est ^2 + Pasadena_data$CO_bg_sd_est^2)
# 
# Pasadena_data$site <- "PAS"
# 
# Pasadena_data <- select(Pasadena_data, datetime, COxs, COxs_unc, ffCO2,"ffCO2 unc", site)
# 
# colnames(Pasadena_data) <- c("datetime_utc", "COxs", "COxs_err", "CO2ff", "CO2ff_err", "site")
# Pasadena_data$lat <- 34.140000
# Pasadena_data$lon <- -118.120000
# 
# 
# LA_data <- rbind(LA_data, Pasadena_data)

LA_data$CO2ff <- as.numeric(LA_data$CO2ff)
LA_data$CO2ff_err <- as.numeric(LA_data$CO2ff_err)


# Setting IDs for easy removal
LA_data <- mutate(LA_data, ID = row_number())
# LA_data <- filter(LA_data, ID != 426)
# LA_data <- filter(LA_data, site == "PAS")
LA_data <- filter(LA_data, ID != 431)

LA_data <- filter(LA_data, ID != 427)




### Calculating York fits



#Plotting points
# LA_data$site <- factor(LA_data$site, levels = c("GRA", "FUL", "USC", "PAS"))
LA_data$site <- factor(LA_data$site, levels = c("GRA", "FUL", "USC"))

# LA_data <- filter(LA_data, site == "PAS", CO2ff<30)

tooltipinfo <- c(paste0('Location = ', LA_data$site,
                        '\n Date = ', LA_data$datetime_utc,
                        '\n COxs = ', round(LA_data$COxs,2),
                        '\n CO2ff = ', round(LA_data$CO2ff,2),
                        '\n ID = ', LA_data$ID))

LA_data$ymin = LA_data$COxs - LA_data$COxs_err
LA_data$ymax = LA_data$COxs + LA_data$COxs_err
LA_data$xmin = LA_data$CO2ff - LA_data$CO2ff_err
LA_data$xmax = LA_data$CO2ff + LA_data$CO2ff_err

# LA_data$site = "USC"

plot <- ggplot(data = LA_data, aes(x = CO2ff, y = COxs)) + theme_linedraw()+
  geom_point_interactive(aes(x =CO2ff, y = COxs, tooltip = tooltipinfo, color = site)) + 
  labs(title = "LA Flask Data", x = "CO2ff (ppm)", y = "COxs (ppb)") +
  geom_errorbar(aes(ymin = ymin, ymax = ymax), width = 0.2, alpha = 0.2) +
  geom_errorbar(aes(xmin = xmin, xmax = xmax), width = 0.2, alpha = 0.2)+

  # geom_errorbar(aes(ymin = LA_data$COxs - LA_data$COxs_err, ymax = LA_data$COxs + LA_data$COxs_err),width = 1, size = 5, alpha = 1) +
  # geom_errorbar(aes(xmin = LA_data$CO2ff - LA_data$CO2ff_err, xmax = LA_data$CO2ff + LA_data$CO2ff_err), width = 0.1, size = .5, alpha = 0.4,show.legend=FALSE) +
  scale_color_manual(values = c("green", "red", "blue", "orange")) +
  labs(color = "Site Code")

plot
#Adding fits

for(site_name in c("USC", "GRA", "FUL")){

  if(site_name == "USC"){
    point_col = "blue"
    ypos = 0.82
  } else if(site_name == "GRA"){
    point_col = "green"
    ypos = 0.9
  } else if(site_name == "FUL") {
    point_col = "red"
    ypos = 0.74
  } else {
    point_col = "orange"
    ypos = 0.66
  }
  
  site_data <- filter(LA_data, site == site_name)
  
  bfsl_fit <- bfsl(site_data$CO2ff,site_data$COxs,site_data$CO2ff_err,site_data$COxs_err)
  print((bfsl_fit))
  fit_df <- NULL
  fit_df$fit <- site_data$CO2ff*bfsl_fit$coefficients[2]+bfsl_fit$coefficients[1]
  fit_df$lowfit <- site_data$CO2ff*(bfsl_fit$coefficients[2]-bfsl_fit$coefficients[4])+(bfsl_fit$coefficients[1]-bfsl_fit$coefficients[3])
  fit_df$highfit <- site_data$CO2ff*(bfsl_fit$coefficients[2]+bfsl_fit$coefficients[4])+(bfsl_fit$coefficients[1]+bfsl_fit$coefficients[3])
  
  r_numerator <- sum((fit_df$fit-site_data$COxs)^2)
  ymean <- mean(site_data$COxs)
  r_denominator <- sum((site_data$COxs - ymean)^2)
  rsq <- 1-r_numerator/r_denominator
  
  
  text_grad <-round(bfsl_fit$coefficients[2],1)
  text_grad_unc <- round(bfsl_fit$coefficients[4],1)
  text_int <-round(bfsl_fit$coefficients[1],1)
  text_rsq <- round(rsq,2)
  
  if(text_int >= 0){
    grob_text <- bquote('y = '*.(text_grad)*'x + '*.(text_int))
  } else{
    grob_text <- bquote('y = '*.(text_grad)*'x - '*.(abs(text_int)))
  }
  
  grob_text2 <- bquote(r^2* '='*.(text_rsq))
  
  
  eq_label <- grobTree(textGrob(grob_text,
                                x=0.05,  y=ypos, hjust=0,gp=gpar(col= point_col, fontsize=11)))
  eq_label2 <- grobTree(textGrob(grob_text2,
                                x=0.30,  y=ypos + 0.015, hjust=0,gp=gpar(col= point_col, fontsize=11)))
  
  
  plot <- plot + geom_abline(slope = bfsl_fit$coefficients[2], intercept = bfsl_fit$coefficients[1], color = point_col) +
    annotation_custom(eq_label) + annotation_custom(eq_label2)
  
}

print(girafe(code=print(plot),height_svg=4, width_svg = 7))

# ggsave("Flask_RCO_plot.png", plot, path = "H:/LA_flask_observations/Final_outputs/", width = 7, height = 4)





### Plotting Newman Data

# c14_data <- read_xlsx("Pas PV SBC 14C for Jocelyn Turnbull.xlsx")
# colnames(C14_data) <- c("site", "w")
# 
# 
# co_data <- read_xlsx("CO 2013-15 Pasadena for Jocelyn Turnbull.xlsx", sheet = "data")
# 
# 


####Pasadena data

#Need to import Pasadena 14C data here
# Pasadena_data <- read.csv("ERL_13_065007_SD_datatable.csv") %>%
#   tail(-9)
# Pasadena_data <- Pasadena_data[, 0:12]
# 
# 
# colnames(Pasadena_data) <- c("Site", "Date", "CO2", "d13C", "D14C", "beta", "beta unc", "ffCO2", "ffCO2 unc",
#                                 "prior ffCO2", "post ffCO2", "outlier")
# 
# Pasadena_data <- filter(Pasadena_data, Site == "SIO")
# 
# #Finding datetime
# 
# Pasadena_data$year <- substr(Pasadena_data$Date, 1, 4)
# Pasadena_data$month <- substr(Pasadena_data$Date, 5, 6)
# Pasadena_data$day <- substr(Pasadena_data$Date, 7, 8)
# Pasadena_data$hour <- substr(Pasadena_data$Date, 9, 10)
# Pasadena_data$minute <- substr(Pasadena_data$Date, 11, 12)
# Pasadena_data$datetime <- paste(paste(Pasadena_data$year, Pasadena_data$month, Pasadena_data$day, sep = "-"), paste(Pasadena_data$hour, Pasadena_data$minute, sep = ":"))
# Pasadena_data$datetime <- as.POSIXct(Pasadena_data$datetime)
# 
# 
# 
# #Importing CO data
# Pasadena_CO_data <- read_excel("CO 2013-15 Pasadena for Jocelyn Turnbull.xlsx", sheet = "data")
# Pasadena_CO_data <- select(Pasadena_CO_data, "datetime PST...9", "CO (ppb)", "CO1rav stdev (ppm)")
# 
# colnames(Pasadena_CO_data) <- c("datetime", "CO", "CO_sd")
# Pasadena_CO_data$CO_sd <- Pasadena_CO_data$CO_sd * 1000
# 
# Pasadena_data <- full_join(Pasadena_data,Pasadena_CO_data, by = "datetime")
# Pasadena_data <- Pasadena_data[order(Pasadena_data$datetime),]
# Pasadena_data$CO_est <- na.approx(Pasadena_data$CO)
# Pasadena_data$CO_sd_est <- na.approx(Pasadena_data$CO_sd)
# Pasadena_data <- filter(Pasadena_data, is.na(ffCO2) == FALSE)
# 
# #Need to bind this to Pasadena data based on the
# 
# #Maybe whats best here would be to do a for loop and select time that is the closest and add.
# # Also include the times though so you can manually go through and figure out which ones are best
# 
# 
# 
# 
# 
# 
# # Importing bg CO
# jolla_CO_data <- read.csv("daily_flask_co2_isotopes_ljo.csv", quote = "", row.names = NULL, stringsAsFactors = FALSE) %>%
#   tail(-110)%>%
#   select(1,2,13)
# 
# colnames(jolla_CO_data) <- c("date", "time", "CO_bg")
# 
# jolla_CO_data <- jolla_CO_data[grepl("N", jolla_CO_data$CO_bg) == FALSE,]
# jolla_CO_data$datetime <- dmy_hm(paste(jolla_CO_data$date, jolla_CO_data$time))
# jolla_CO_data <- filter(jolla_CO_data, datetime < ymd("2015-02-28"))
# 
# Pasadena_data <- full_join(Pasadena_data,jolla_CO_data, by = "datetime")
# Pasadena_data <- Pasadena_data[order(Pasadena_data$datetime),]
# Pasadena_data$CO_bg_est <- na.approx(Pasadena_data$CO_bg)
# 
# Pasadena_data <- filter(Pasadena_data, is.na(ffCO2) == FALSE)
#       Pasadena_data$CO_bg_sd_est <- 5
# 
# Pasadena_data <- select(Pasadena_data, datetime, ffCO2, "ffCO2 unc", CO_est, CO_sd_est, CO_bg_est, CO_bg_sd_est)
# Pasadena_data$COxs <- Pasadena_data$CO_est - Pasadena_data$CO_bg_est
# Pasadena_data$COxs_unc <- sqrt(Pasadena_data$CO_sd_est ^2 + Pasadena_data$CO_bg_sd_est^2)
# 
# colnames(Pasadena_data) <- c("datetime", "CO2ff", "CO2ff_unc", "CO", "CO_sd", "CO_bg", "CO_bg_sd", "COxs", "COxs_unc")
# 
# 


# 
# CO_bg_df <- select(jolla_CO_data, datetime, CO_est)
# colnames(CO_bg_df) <- c("datetime", "CO_bg")
# 
# pasadena_data <- merge(Pasadena_CO_data, CO_bg_df, by = "datetime") %>%
#   select(datetime, )
# 
# 
# 
# 
# 
# #add line labelling site as bg or normal, actually maybe dont need this,just need to join based on datetime 
# 
# a <- jolla_CO_data[1,]
# as.vector(a)
# colnames(jolla_CO_data) <- a
# # 
# osp psbbox = c(left = -119.274006,
#          bottom = 33.527332,
#          right = -117.512390,
#          top = 34.598510)
# get_map(location = sbbox, maptype = "satellite", source = "google")
# ggmap(basemap) 
# 
# 
# 
# library(tmaptools)
# library(tmap)
# data(NLD_muni)
#  osm_NLD <- read_osm(NLD_muni, ext=1.1)
# tm_shape(osm_NLD) + tm_rgb()
# 
# 
# data("NLD_prov")
# 
# tmap_mode('view')
# 
# tm_shape(NLD_prov) + tm_polygons('population') + tm_layout(basemaps = c('OpenStreetMap'))


#### Mapping

points <- select(LA_data, site, lat, lon) %>%
  unique()
points$site <- as.character(points$site)

points <- rbind(points, c("MWO", 34.22528, -118.05729))
points <- rbind(points, c("PAS", 34.14, -118.12))
points <- rbind(points, c("SBC", 34.09, -117.31))

points$lat <- as.numeric(points$lat)
points$lon <- as.numeric(points$lon)

basemap <- get_stamenmap(bbox = c(left = -118.8,
                                bottom = 33.527332,
                                right = -118.1,
                                top = 34.4),
                       maptype = "terrain",
                       crop = FALSE,
                       zoom = 8)

ggmap(basemap, darken = c(0.1, "white"), extent = "device") +
  geom_point(data = points, aes(x = lon, y = lat, colour = site), size = 5) +
  scale_colour_manual(values = c("red", "green", "purple","black","orange", "blue" )) +
  geom_text(data = points, aes(x=lon, y=lat, label=site), colour = "black", hjust=-0.5, size = 4.5)

