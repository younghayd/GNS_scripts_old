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

setwd("H:/XCAMS/Variation_for_last_10_wheels")

#Read files in designated folder and combine into single dataframe
file_list <- list.files()

ox_data <- NULL
overall_sum <- 0

for(file in file_list){
  wheel_data <- read.table(file, sep = "", skip = 6)
  colnames(wheel_data) <- c("E","Item", "Run", "month", "day", "time", "year", "Pos",  "Meas", "SmType", "Sample_Name", "Cycles", "12Cle", "13Cle", "12Che", "13Che", "CntTotS",  "CntTotGT", "ltf_hw", "CntTotBG", "CntTotI1", "CntTotI2", "(13/12)he", "ratio_1412C", "(14/13)he")
  wheel_data <- select(wheel_data, month, day, time, year, SmType, ratio_1412C) %>%
    filter(SmType == 'OxI')
  wheel_data$TW <- substr(file, 3,8)
  wheel_data$avg <- mean(wheel_data$ratio_1412C)
  overall_sum <- overall_sum + wheel_data$avg[1]
  ox_data <- rbind(ox_data, wheel_data) 
}

overall_mean <- overall_sum/length(file_list)


#Plot 14C/12C for all wheels

plot <- ggplot() + theme_linedraw() +
  geom_point(data = ox_data, aes(x=TW, y=ratio_1412C, color = "red")) +
  geom_point(data = ox_data, aes(x=TW, y=avg, color = "blue")) +
  geom_hline(yintercept = overall_mean) +
  labs(y = "14/12C ratio", x = 'TW', title = "14C/12C Time Series") +
  theme(legend.position = "none", axis.text.x = element_text(size = 7.5, angle = 90, vjust = 0.5, hjust = 1), plot.title = element_text(hjust = 0.5))


print(girafe(code=print(plot),height_svg=4, width_svg = 7))

