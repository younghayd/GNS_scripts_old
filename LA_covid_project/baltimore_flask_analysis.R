#Script plots up Baltimore flask data

require(readxl)
require(lubridate)
require(dplyr)
require(ggplot2)
require(ggiraph)
require(bfsl)
require(grob)
require(plotly)

raw_data_directory <- "H:/data/LA_covid_project/raw_data/flask_data/"
figures_directory <- "H:/figures/LA_covid_project/"


setwd(raw_data_directory)


#Organising Data 
flask_data <- read_excel(path = "baltimore_flask_data.xlsx", skip = 1)
  

flask_data$date <- make_date(year = flask_data$YR, month = flask_data$MO, day = flask_data$DY)

flask_data$CO_unc <- 12 #arbitrary number from hourly std of Indy picarro data, need to change this
flask_data$COxs_unc <- flask_data$CO_unc*2/sqrt(2)


flask_data <- select(flask_data, CODE, date, ID, LAT, LON, CO2FFXS, CO2FFUNC, CO2C14FLAG, CO2FLAG, COXS, COxs_unc, COFLAG)
colnames(flask_data) <- c("site", "date", "id", "lat", "lon", 
                          "CO2ff", "CO2ff_unc", "CO2C14_flag", "CO2_flag", 
                          "COxs", "COxs_unc", "CO_flag")
flask_data <- mutate_at(flask_data, c("CO2ff", "CO2ff_unc", "COxs", "COxs_unc"), as.numeric)


flask_data <- filter(flask_data, CO2C14_flag == "..." & CO2_flag == "..." & CO_flag == "..." & 
                       site != "TMD" & CO2ff >= -999 & COxs >= -999)

flask_data <- filter(flask_data, id != "3124-03")
flask_data <- filter(flask_data, id != "3006-03")

# flask_data <- filter(flask_data, date < ymd("2021 01 01") & date > ymd("2020 03 01"))



#Calculating York fit


gradient_function <- function(df,xdata,ydata,title,xlabel,ylabel,xerror = NULL, yerror = NULL) 
{
  
  #### Setting up tooltip, York fit, r^2 ####
  
  #Tooltip
  tooltipinfo <- c(paste0('site = ', df$site,
                          '\n CO2ff = ', df$CO2ff,
                          '\n COxs = ', df$COxs,
                          '\n ID = ', df$id))
  
  #York Fit
  bfsl_fit <- bfsl(xdata,ydata,xerror,yerror)
  print((bfsl_fit))
  df$fit <- xdata*bfsl_fit$coefficients[2]+bfsl_fit$coefficients[1]
  df$lowfit <- xdata*(bfsl_fit$coefficients[2]-bfsl_fit$coefficients[4])+(bfsl_fit$coefficients[1]-bfsl_fit$coefficients[3])
  df$highfit <- xdata*(bfsl_fit$coefficients[2]+bfsl_fit$coefficients[4])+(bfsl_fit$coefficients[1]+bfsl_fit$coefficients[3])
  
  #Calculating R^2
  
  r_numerator <- sum((df$fit-ydata)^2)
  ymean <- mean(ydata)
  r_denominator <- sum((ydata - ymean)^2)
  rsq <- 1-r_numerator/r_denominator
  
  #### Sorting out annotations and point colours and plotting ####
  
  #Adding annotation with gradient and r^2 value to plot
  
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
  
  #
  # eq_label <- grobTree(textGrob(grob_text,
  #                               x=0.05,  y=0.92, hjust=0,gp=gpar(fontsize=11)))
  # eq_label2 <- grobTree(textGrob(grob_text2,
  #                                x=0.05,  y=0.84 + 0.015, hjust=0,gp=gpar(fontsize=11)))
  #
  plot <- ggplot(data = flask_data, aes(x = CO2ff, y = COxs)) + theme_linedraw()+
    geom_point_interactive(aes(x =CO2ff, y = COxs, color = site), tooltip = tooltipinfo) + 
    labs(title = "Baltimore Flask Data", x = "CO2ff (ppm)", y = "COxs (ppb)")
    # geom_errorbar(aes(ymin = ymin, ymax = ymax), width = 0.2, alpha = 0.2) +
    # geom_errorbar(aes(xmin = xmin, xmax = xmax), width = 0.2, alpha = 0.2) +
    
  
  
  
  plot <- plot + geom_abline(slope = bfsl_fit$coefficients[2], intercept = bfsl_fit$coefficients[1])# +
    #annotation_custom(eq_label) + annotation_custom(eq_label2)
  
  
  print(girafe(code=print(plot),height_svg=4, width_svg = 7))
  
}

stats <- gradient_function(df = flask_data, xdata = flask_data$CO2ff, ydata = flask_data$COxs, 
                           xerror = flask_data$CO2ff_unc, yerror = flask_data$COxs_unc)


