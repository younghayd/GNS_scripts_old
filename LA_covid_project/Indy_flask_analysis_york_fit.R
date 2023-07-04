####################################################################
#  Indy_flask_analysis_york_fit.R
####################################################################

###################################################################
# NOTES
####################################################################
#-------------------------------------
# DESCRIPTION
#-------------------------------------
#Takes csv of Indy flasks and analyses emission ratio measured at different towers around Indy 
#Filters out flagged data.
#Plots CO:CO2ff emission ratio

#-------------------------------------
# FILE OUTPUTS
#-------------------------------------


####################################################################
# CODE BEGINS HERE
####################################################################

#Packages and Setup

library(readr)
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
# library(sf)
# library(mapview)
library(lubridate)
library(readxl)


# save_path <- paste0(location,"/Master's/Plots/Indy_flasks/")
# save_title <- "indy_CO2ff_ratio.png"

#Massive change in york fit when uncertainty in CO is changed (12.2 for 0.1, 8.4 for 1, 6.9 for 2, 6.4 for 5 and above)
#Also fairly big change for CO2ff

setwd("H:/LA_flask_observations/Final_outputs/")

#Reading the data, cutting down bad measurements, removing unneeded columns of data

indy_data <- read_excel("data/Indy_flask_data/towers_enhancements_bkgdT1_20230412.xlsx", skip = 14) %>%
  select(LOC, DATE, LAT, LON, CO2FFXS, CO2FFUNC, CO2C14FLAG, CO2XS, CO2, CO2FLAG, COXS, CO, COFLAG, BGTYPE, ID)%>%
  filter(CO2FFXS > -999, CO > -999)

indy_data <- filter(indy_data, indy_data$DATE < 2020.2)

indy_data$ID <- as.character(indy_data$ID)
# indy_data <- subset(indy_data, CO2FFDELTABG > -990)

indy_data <- subset(indy_data, COFLAG == '...')
indy_data <- subset(indy_data, CO2C14FLAG == '...'|CO2C14FLAG == '..M'|CO2C14FLAG == '..S')
# indy_data <- select(indy_data, c(LOC,ID, DATE,LAT,LON,CO2FFDELTABG, CO2FFUNC,CO2DELTABG,CO2,CODELTABG,CO, BGTYPE))

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


#York Fit
bfsl_fit <- bfsl(indy_data$CO2ff,indy_data$COxs,indy_data$CO2ff_unc,indy_data$COxs_unc)
print(bfsl_fit)
indy_data$fit <- indy_data$CO2ff*bfsl_fit$coefficients[2]+bfsl_fit$coefficients[1]
indy_data$lowfit <- indy_data$CO2ff*(bfsl_fit$coefficients[2]-bfsl_fit$coefficients[4])+(bfsl_fit$coefficients[1]-bfsl_fit$coefficients[3])
indy_data$highfit <- indy_data$CO2ff*(bfsl_fit$coefficients[2]+bfsl_fit$coefficients[4])+(bfsl_fit$coefficients[1]+bfsl_fit$coefficients[3])

#Calculating R^2

r_numerator <- sum((indy_data$fit-indy_data$COxs)^2)
ymean <- mean(indy_data$COxs)
r_denominator <- sum((indy_data$COxs - ymean)^2)
rsq <- 1-r_numerator/r_denominator

text_grad <-round(bfsl_fit$coefficients[2],1)
text_grad_unc <- round(bfsl_fit$coefficients[4],1)
text_int <-round(bfsl_fit$coefficients[1],1)
text_rsq <- round(rsq,2)

if(text_int >= 0){
  grob_text1 <- bquote('y = '*.(text_grad)*'x + '*.(text_int))
} else{
  grob_text1 <- bquote('y = '*.(text_grad)*'x - '*.(abs(text_int)))
}
grob_text2 <- bquote(r^2*'='*.(text_rsq))
grob_text3 <- bquote('Emission ratio = '*.(text_grad)*''%+-%''*.(text_grad_unc))

eq_label1 <- grobTree(textGrob(grob_text1,
                              x=0.05,  y=0.90, hjust=0,gp=gpar(col="black", fontsize=8)))
eq_label2 <- grobTree(textGrob(grob_text2,
                              x=0.05,  y=0.84, hjust=0,gp=gpar(col="black", fontsize=8)))
eq_label3 <- grobTree(textGrob(grob_text3,
                              x=0.05,  y=0.76, hjust=0,gp=gpar(col="black", fontsize=8)))



plot <- ggplot(data = indy_data, aes(x=CO2ff, y=COxs)) +theme_linedraw()+
  geom_point_interactive(aes(x =CO2ff, y = COxs, colour = Tower,  tooltip = tooltipinfo), size = 1)+ 
  labs(x = x_lab_ff, y = y_lab_ff, color = "Tower:")

plot <- plot + geom_line(aes(x = CO2ff, y = fit), color ='red') + #york fit
      annotation_custom(eq_label1) + annotation_custom(eq_label2) + annotation_custom(eq_label3)+
  geom_ribbon(aes(ymin=lowfit, ymax=highfit) ,fill="blue", alpha=0.2)

plot <- plot + scale_color_manual(values = c('purple','red','green','orange','blue','grey', 'yellow'), breaks = c('2','3','5','6','9','10','11'))


# plot <- plot + geom_errorbar(ymin = indy_data$COxs -indy_data$COxs_unc, ymax = indy_data$COxs + indy_data$COxs_unc,width = 0.1, linewidth = .5, alpha = 0.04,show.legend=FALSE)

# plot <- plot + geom_errorbar(xmin = indy_data$CO2ff - indy_data$CO2ff_unc, xmax = indy_data$CO2ff + indy_data$CO2ff_unc,width = 0.01, linewidth = .5, alpha = 0.04,show.legend=FALSE)
  


print(girafe(code=print(plot),height_svg=3.5, width_svg = 6))

ggsave("Indy_RCO.png", plot, path = "H:/LA_flask_observations/Final_outputs/plots/", width = 7, height = 4, dpi = 600)

