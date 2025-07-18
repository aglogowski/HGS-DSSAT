library(dplyr)
library(tidyr)
library(lubridate)
library(readxl)
library(ggplot2)

setwd("C:\\Users\\glogow0000\\HGS-DSSAT\\analysis\\DSSAT_no_inflow_satflow")
dssat_drn=read_xlsx("dssat-hgs.xlsx",sheet = "DRN layer DSSAT wheat",skip = 1)
colnames(dssat_drn)=c("time","3.0","2.95","2.85","2.7","2.55","2.4","2.25","2.1","1.8")

setwd("C:\\Users\\glogow0000\\HGS-DSSAT\\model\\HGS\\stand_alone\\lys\\hgs")
hgs_drn=readLines("lys_Eo.nodal_fluid_mass_balance.test.dat")

# Find line with VARIABLES
var_line_index <- grep("^VARIABLES=", hgs_drn)
var_line <- hgs_drn[var_line_index]

# Extract variable names
# Remove 'VARIABLES=' and split on comma
var_names <- gsub('^VARIABLES=', '', var_line)
var_names <- gsub('"', '', var_names)  # remove quotes
var_names <- trimws(unlist(strsplit(var_names, ",")))

# Find the first line of actual data (starts after 'zone t=' line)
zone_line_index <- grep("^zone",hgs_drn, ignore.case = TRUE)
data_start_index <- zone_line_index + 1

# Read the data portion only
data_lines <- hgs_drn[data_start_index:length(hgs_drn)]
data <- read.table(text = paste(data_lines, collapse = "\n"))
colnames(data)=var_names


up_inf=seq.int(23,by=16,length.out = 13)
down_inf=seq.int(25,by=16,length.out = 13)
all=c(1,up_inf,down_inf)
all=sort(all)
hgs_drain_sel=data[,all]
hgs_drain_sel$time_d=hgs_drain_sel$Time[1]
hgs_drain_sel$time_d[2:116]=hgs_drain_sel$Time[2:116]-hgs_drain_sel$Time[1:115]
hgs_drain_sel%>%
  mutate(L13=(`QVU+13`+`QVD+13`)*time_d/4*100,
         L12=(`QVU+12`+`QVD+12`)*time_d/4*100,
         L11=(`QVU+11`+`QVD+11`)*time_d/4*100,
         L10=(`QVU+10`+`QVD+10`)*time_d/4*100,
         L09=(`QVU+09`+`QVD+09`)*time_d/4*100,
         L08=(`QVU+08`+`QVD+08`)*time_d/4*100,
         L07=(`QVU+07`+`QVD+07`)*time_d/4*100,
         L06=(`QVU+06`+`QVD+06`)*time_d/4*100,
         L05=(`QVU+05`+`QVD+05`)*time_d/4*100,
         L04=(`QVU+04`+`QVD+04`)*time_d/4*100,         
         L03=(`QVU+03`+`QVD+03`)*time_d/4*100,  
         L02=(`QVU+02`+`QVD+02`)*time_d/4*100,  
         L01=(`QVU+01`+`QVD+01`)*time_d/4*100,
         time_d=floor(Time)+1)%>%
  group_by(time_d)%>%
  summarise(L13=sum(L13),
            L12=sum(L12),
            L11=sum(L11),
            L10=sum(L10),
            L09=sum(L09),
            L08=sum(L08),
            L07=sum(L07),
            L06=sum(L06),
            L05=sum(L05),
            L04=sum(L04),
            L03=sum(L03),
            L02=sum(L02),
            L01=sum(L01))->hgs_test
hgs_comp=hgs_test[c(1:103),c(1,3:11)]
colnames(hgs_comp)=c("time","3.0","2.95","2.85","2.7","2.55","2.4","2.25","2.1","1.8")

#### cum summ ####
cumsum_hgs <- data.frame(
  day = hgs_comp$time,
  apply(hgs_comp[, -1], 2, cumsum)
)

cumsum_dssat<- data.frame(
  day =dssat_drn$time,
  apply(dssat_drn[, -1], 2, cumsum))
colnames(cumsum_dssat)=c("time","3.0","2.95","2.85","2.7","2.55","2.4","2.25","2.1","1.8")
colnames(cumsum_hgs)=c("time","3.0","2.95","2.85","2.7","2.55","2.4","2.25","2.1","1.8")
hgs_comp$model="hgs"
dssat_drn$model="dssat"
cumsum_dssat$model="dssat"
cumsum_hgs$model="hgs"
df_test=rbind(hgs_comp,dssat_drn)
df_test=df_test[,c(1,11,2:10)]
df_test%>%
  gather("Depth","Drain",`3.0`:`1.8`)->df_plot

df_cumsum=rbind(cumsum_hgs,cumsum_dssat)
df_cumsum=df_cumsum[,c(1,11,2:10)]
df_cumsum%>%
  gather("Depth","Drain",`3.0`:`1.8`)->df_cumsum_plot


ggplot() +
  geom_line(data = df_plot, aes(x = time, y = Drain, col = model), size = 1) +
  labs(x = "Time", y = "Drained (mm/d)", color = "model") +
  facet_wrap(~Depth)+
  theme_minimal()

ggplot() +
  geom_line(data = df_cumsum_plot, aes(x = time, y = Drain, col = model), size = 1) +
  labs(x = "Time", y = "Drained (mm/d)", color = "model") +
  facet_wrap(~Depth)+
  theme_minimal()
