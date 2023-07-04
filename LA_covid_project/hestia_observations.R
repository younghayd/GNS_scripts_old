#Code takes raw .nc hestia files, unzips them, and exports them into CSV format. This can then manually be summed to find sector totals.



library('ncdf4')
library('raster')
library('R.utils')
library('purrr')
library("rnaturalearth")
library("rnaturalearthdata")
library("terra")
library("oce")
library("dplyr")
library("ggmap")
library("plyr")


setwd("H:/LA_flask_observations/Data/LA_sector_data")

# data <- nc_open(gzfile("1km.LAbasin.v2.5.total.annual.local.2015.nc.gz"))

#Unzips .tar file
untar("1km.LABasin.v2.5.allsectors.annual.local.2011.nc.gz.tar", compressed = 'gzip', exdir = "LA_sector_data")
file_list <- list.files("LA_sector_data")

#UNZIPS THE .GZ FILE
setwd("H:/LA_flask_observations/Data/LA_sector_data")
for(file in file_list){
  walk(file, gunzip)  
}


#Start here

setwd("H:/LA_flask_observations/Final_outputs/data/Hestia_raw_data/")

file_list <- list.files()

csv_file <- data.frame(Latitude = numeric(0), Longitude = numeric(0))

for(file in file_list){
  
  map_object <- raster(file) %>%
    rasterToPoints(spatial = TRUE) %>%
    data.frame()
  
  sector <- gsub(".*5.(.+).annual.local.2011.nc*", "\\1", file)
  
  data = data.frame(x = 4000000, y = 0)
  
  # Convert the coordinates to a spatial object:
  coordinates(map_object) <- ~x+y
  
  # Specify the projection of the original data:
  #   This should be given with the dataset, or go to:
  #   http://spatialreference.org/ref/?search=florida and search
  proj4string(map_object) <- CRS("+init=epsg:2229")
  
  
  # Specify the transformation you want (i.e., the projection of the data you want to convert to)
  #   Note that lat/long (WGS84) is epsg:4326
  map_object <- spTransform(map_object, CRS("+init=epsg:4326")) #WGS84
  map_object <- as.data.frame(map_object)
  
  map_object <- select(map_object, x, y, Carbon.Emissions)
  
  #Removing 0 values
  map_object <- filter(map_object,map_object[,3] >0)

  colnames(map_object) <- c("Longitude", "Latitude", paste("kgC/yr", sector))
  csv_file <- rbind.fill(csv_file, map_object)
  # write.xlsx(map_object, paste0("H:/LA_flask_observations/Final_outputs/data/Hestia_final_data/", substr(file, 1, nchar(file) - 3), ".xlsx"))
  write.csv(map_object, paste0("H:/LA_flask_observations/Final_outputs/data/Hestia_final_data/", substr(file, 1, nchar(file) - 3), ".csv"))
  
}




