require(readxl)
require(lubridate)
require(dplyr)
require(ggplot2)
require(bfsl)
require(grob)
require(plotly)

setwd("H:/LA_flask_observations/Final_outputs/data/Indy_flask_data/")

year_boundary <- 2016

#Reading in and organising data
flask_data <- read_excel("towers_enhancements_bkgdT1_20230412.xlsx", skip = 14) %>%
  select(LOC, YR, MO, DY, HR, MN, DATE, CO2FFXS, CO2FFUNC, CO2C14FLAG, COXS, CO, COFLAG, ID)%>%
  filter(CO2FFXS > -999, CO > -999)

#Need to York fit for all flasks 
df <- flask_data
xdata <- flask_data$CO2FFXS
ydata <- flask_data$COXS
xerror <- flask_data$CO2FFUNC 
yerror <- flask_data$CO2FFUNC*10
xlabel <- "a"
ylabel <- "b"
title <- "a"

flask_data$CO_unc <- 12 #Uncertainty from the standard deviation of hourly avg picarro data from tower 2 in Indy

flask_data$COxs_unc <- flask_data$CO_unc*2/sqrt(2)

flask_data <- subset(flask_data, ID != '3058-09')
flask_data <- subset(flask_data, ID != '3151-05')
flask_data <- subset(flask_data, ID != '3057-01')
flask_data <- subset(flask_data, ID != '3503-03')
flask_data <- subset(flask_data, ID != '3033-03')
flask_data <- subset(flask_data, ID != '3154-01')

flask_data$RCO <- flask_data$COXS/flask_data$CO2FFXS

plot <- ggplot(data = flask_data) + theme_linedraw() +geom_point(aes(x = DATE, y = RCO, color = LOC)) + ylim(-150, 150) +
  labs(color = "Location", x = "Year")

print(girafe(code=print(plot),height_svg=4, width_svg = 7))





gradient_function <- function(df,xdata,ydata,title,xlabel,ylabel,xerror = NULL, yerror = NULL) 
{
  
  #### Setting up tooltip, York fit, r^2 ####
  
  # #Tooltip
  tooltipinfo <- c(paste0('ID = ', df$ID))
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
  
  results_tbl <- c(text_grad, text_grad_unc, text_int, text_rsq, rsq)
  
  return(results_tbl)
  
}

year_list <- unique(flask_data$YR)

results <- data.frame(matrix(ncol = 6, nrow = 0))

#For yearly averages
for(year in year_list){

  year_flasks <- filter(flask_data, YR == year)

  stats <- gradient_function(df = year_flasks, xdata = year_flasks$CO2FFXS, ydata = year_flasks$COXS, xerror = year_flasks$CO2FFUNC, yerror = year_flasks$COxs_unc)
  stats <- c(stats, year, length(year_flasks$YR))
  results <- rbind(results, stats) #Need to convert this into a dataframe

  # results <- as.data.frame(results, stats)

  #Results look way too scattered. Try calculate each RCO for each point individually and then plot that to have more points.
}

colnames(results) <- c("text_grad", "text_grad_unc", "text_int", "text_rsq", "rsq", "year", "flask_total")


plot <- ggplot(data = results) + theme_linedraw() +geom_point(aes(x = year, y = text_grad)) + labs(x = "Year", y = " RCO")

print(girafe(code=print(plot),height_svg=4, width_svg = 7))

#plotting average RCO per year - looks very scattered, small upward trend

year_list <- unique(flask_data$YR)

results <- data.frame(matrix(ncol = 6, nrow = 0))



#For yearly averages
for(year in year_list){

  year_flasks <- filter(flask_data, YR == year)

  stats <- gradient_function(df = year_flasks, xdata = year_flasks$CO2FFXS, ydata = year_flasks$COXS, xerror = year_flasks$CO2FFUNC, yerror = year_flasks$COxs_unc)
  stats <- c(stats, year, length(year_flasks$YR))
  results <- rbind(results, stats) #Need to convert this into a dataframe

  # results <- as.data.frame(results, stats)

  #Results look way too scattered. Try calculate each RCO for each point individually and then plot that to have more points.
}

#For 5-yearly averages

{

flask_data <- filter(flask_data, YR >= 2013)
flask_data <- filter(flask_data, YR <= 2019)
  
year_range_1 <- filter(flask_data, YR <= year_boundary)
year_range_2 <- filter(flask_data, YR > year_boundary)

stats_range_1 <- gradient_function(df = year_range_1, xdata = year_range_1$CO2FFXS, ydata = year_range_1$COXS, xerror = year_range_1$CO2FFUNC, yerror = year_range_1$COxs_unc)
stats_range_1 <- c(stats_range_1, 2010, length(year_range_1$YR))
stats_range_2 <- gradient_function(df = year_range_2, xdata = year_range_2$CO2FFXS, ydata = year_range_2$COXS, xerror = year_range_2$CO2FFUNC, yerror = year_range_2$COxs_unc)
stats_range_2 <- c(stats_range_2, 2016, length(year_range_2$YR))


results <- rbind(stats_range_1, stats_range_2)

results<- as.data.frame(results)

}


colnames(results) <- c("text_grad", "text_grad_unc", "text_int", "text_rsq", "rsq", "year", "flask_total")

#Plotly data here

#Plot gradients

plot <- plot_ly(data = results)

plot <- add_trace(plot, x =~year, y = ~text_grad,
                  data = results, type = "scatter", mode = "markers+lines",
                  text = c(results$rsq),
                  text2 = c(results$flask_total),
                  hovertemplate = paste('Year: %{y}',
                                        '<br>RCO: %{y}',
                                        '<br>r2: %{text:.2f}',
                                        '<br>total: %{text2}'),
                  showlegend = FALSE)
                  

plot <- layout(plot,
              title = "Indy flask RCO time series",
              yaxis = list(title = "RCO (ppb/ppm)"
              ),
              xaxis = list(title = "Year"
              )
)
plot

#Plotting individual RCO values for each flask over time - similar upward trend. Maybe because Indy's cars get worse with age, LA gets better?

flask_data$RCO <- flask_data$COXS/flask_data$CO2FFXS
flask_data <- filter(flask_data, RCO < 100, RCO > -100)
plot(flask_data$DATE, flask_data$RCO)
lm(flask_data$RCO~flask_data$DATE)

print(results)

######################################


#Plotting points
# flask_data$site <- factor(flask_data$site, levels = c("GRA", "FUL", "USC", "PAS"))

# flask_data <- filter(flask_data, site == "PAS", CO2ff<30)


flask_data$ymin = flask_data$COXS - flask_data$COxs_unc
flask_data$ymax = flask_data$COXS + flask_data$COxs_unc
flask_data$xmin = flask_data$CO2FFXS - flask_data$CO2FFUNC
flask_data$xmax = flask_data$CO2FFXS + flask_data$CO2FFUNC

# flask_data$site = "USC"

plot <- ggplot(data = flask_data, aes(x = CO2FFXS, y = COXS)) + theme_linedraw()+
  geom_point_interactive(aes(x =CO2FFXS, y = COXS, color = LOC)) + 
  labs(title = "Indy Flask Data", x = "CO2FFXS (ppm)", y = "COXS (ppb)") +
  # geom_errorbar(aes(ymin = ymin, ymax = ymax), width = 0.2, alpha = 0.2) +
  # geom_errorbar(aes(xmin = xmin, xmax = xmax), width = 0.2, alpha = 0.2) +
  labs(color = "Tower")

plot
#Adding fits

ypos = 0.82


bfsl_fit <- bfsl(flask_data$CO2FFXS,flask_data$COXS,flask_data$CO2FFUNC,flask_data$COxs_unc)
print((bfsl_fit))
fit_df <- NULL
fit_df$fit <- flask_data$CO2FFXS*bfsl_fit$coefficients[2]+bfsl_fit$coefficients[1]
fit_df$lowfit <- flask_data$CO2FFXS*(bfsl_fit$coefficients[2]-bfsl_fit$coefficients[4])+(bfsl_fit$coefficients[1]-bfsl_fit$coefficients[3])
fit_df$highfit <- flask_data$CO2FFXS*(bfsl_fit$coefficients[2]+bfsl_fit$coefficients[4])+(bfsl_fit$coefficients[1]+bfsl_fit$coefficients[3])

r_numerator <- sum((fit_df$fit-flask_data$COXS)^2)
ymean <- mean(flask_data$COXS)
r_denominator <- sum((flask_data$COXS - ymean)^2)
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
                              x=0.05,  y=ypos, hjust=0,gp=gpar(fontsize=11)))
eq_label2 <- grobTree(textGrob(grob_text2,
                               x=0.30,  y=ypos + 0.015, hjust=0,gp=gpar(fontsize=11)))


plot <- plot + geom_abline(slope = bfsl_fit$coefficients[2], intercept = bfsl_fit$coefficients[1], color = point_col) +
  annotation_custom(eq_label) + annotation_custom(eq_label2)



print(girafe(code=print(plot),height_svg=4, width_svg = 7))






