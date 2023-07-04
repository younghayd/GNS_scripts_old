library(dplyr)
library(ggplot2)
require(readxl)
require(ggpubr)
require(ggiraph)

setwd("H:/XCAMS/")

kapuni_data <- read_excel("kapuni_hist.xlsx")%>%
  select(TW, TP, wtgraph, "Ratio to standard", "Ratio to standard error")%>%
  tail(n = 100)%>%
  mutate(RCM_10 = FALSE)
  
colnames(kapuni_data) <- c("TW", "TP", "mass", "RTS", "RTS_err", "RCM_10")

kapuni_data$RCM_10[kapuni_data$TP == 85791 | kapuni_data$TP == 85792 | kapuni_data$TP == 85793] <- TRUE

mean_kapuni <- mean(kapuni_data$RTS[kapuni_data$RCM_10 == FALSE])
std_kapuni <- sd(kapuni_data$RTS[kapuni_data$RCM_10 == FALSE])
  
kapuni_data$RCM_10 <- factor(kapuni_data$RCM_10, levels = c("TRUE", "FALSE"))

kapuni_plot <- ggplot(kapuni_data) + theme_linedraw() +
  geom_point(aes(x = TW, y = RTS, colour = RCM_10)) +
  geom_hline(yintercept = mean_kapuni) +
  annotate('ribbon', x = c(-Inf, Inf), ymin = mean_kapuni - std_kapuni, ymax = mean_kapuni + std_kapuni, alpha = 0.1, fill = 'red') +
  geom_hline(yintercept = mean_kapuni - 2*std_kapuni, linetype = "dotted") +
  geom_hline(yintercept = mean_kapuni + 2*std_kapuni, linetype = "dotted") +
  labs(title = "Kapuni Samples", x = "TW", y = "RTS", colour = "RCM 10") +
  theme(plot.title = element_text(hjust = 0.5))+
  scale_colour_manual(values = c("red", "blue"))


print(girafe(code=print(kapuni_plot),height_svg=4, width_svg = 7))




ox_data <- read_excel("ox_1_hist.xlsx")%>%
  select(TW, TP, wtgraph, "Ratio to standard", "Ratio to standard error")%>%
  tail(n = 100)%>%
  mutate(RCM_10 = FALSE)

colnames(ox_data) <- c("TW", "TP", "mass", "RTS", "RTS_err", "RCM_10")

ox_data$RCM_10[ox_data$TP == 85776 | ox_data$TP == 85758 | ox_data$TP == 85748] <- TRUE

mean_ox <- mean(ox_data$RTS[ox_data$RCM_10 == FALSE])
std_ox <- sd(ox_data$RTS[ox_data$RCM_10 == FALSE])

ox_data$RCM_10 <- factor(ox_data$RCM_10, levels = c("TRUE", "FALSE"))

ox_plot <- ggplot(ox_data) + theme_linedraw() +
  geom_point(aes(x = TW, y = RTS, colour = RCM_10)) +
  geom_hline(yintercept = mean_ox) +
  annotate('ribbon', x = c(-Inf, Inf), ymin = mean_ox - std_ox, ymax = mean_ox + std_ox, alpha = 0.1, fill = 'red') +
  geom_hline(yintercept = mean_ox - 2*std_ox, linetype = "dotted") +
  geom_hline(yintercept = mean_ox + 2*std_ox, linetype = "dotted") +
  labs(title = "Ox Samples", x = "TW", y = "RTS", colour = "RCM 10") +
  theme(plot.title = element_text(hjust = 0.5))+
  scale_colour_manual(values = c("red", "blue"))


print(girafe(code=print(ox_plot),height_svg=4, width_svg = 7))


combined_plot <- ggarrange(kapuni_plot, ox_plot, ncol = 1, nrow = 2, common.legend = TRUE, legend = "bottom")

print(girafe(code=print(combined_plot),height_svg=9, width_svg = 9))
ggsave("plot.png", combined_plot, width = 9, height = 9)


kapuni_subset <- filter(kapuni_data, RCM_10 ==TRUE)

kapuni_mass_plot <- ggplot(kapuni_subset) + theme_linedraw() +
  geom_point(aes(x = 1/mass, y = RTS), size = 4, colour = "red") +
  stat_smooth(aes(x = 1/mass, y = RTS), method = "lm", se = F) +
  labs(title = "Kapuni Samples", x = "1/mass (1/mg)", y = "RTS") +
  theme(plot.title = element_text(hjust = 0.5)) +
  annotate("text",x=-
             2,y=0.0012,label=(paste0("slope==",coef(lm(kapuni_subset$RTS~1/kapuni_subset$mass))[2])),parse=TRUE)

print(girafe(code=print(kapuni_mass_plot),height_svg=9, width_svg = 9))


ox_subset <- filter(ox_data, RCM_10 ==TRUE)

ox_mass_plot <- ggplot(ox_subset) + theme_linedraw() +
  geom_point(aes(x = mass, y = RTS), size = 4, colour = "red") +
  stat_smooth(aes(x = mass, y = RTS), method = "lm", se = F) +
  labs(title = "Ox Samples", x = "mass (mg)", y = "RTS") +
  theme(plot.title = element_text(hjust = 0.5)) +
  annotate("text",x=-
             0,y=1,label=(paste0("slope==",coef(lm(ox_subset$RTS~ox_subset$mass))[2])),parse=TRUE)

print(girafe(code=print(ox_mass_plot),height_svg=9, width_svg = 9))





