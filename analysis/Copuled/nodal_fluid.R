####nodal fluid mass balance ####
library(dplyr)
library(ggplot2)
test_flow=NULL
# check 1 and multiple zones 
#ZONE 1
setwd("C:\\Users\\glogow0000\\HGS-DSSAT\\model\\HGS\\stand_alone\\lys\\hgs_onezone")
list=dir(pattern = "lys_Eo.nodal_fluid_mass_balance.test.dat")
# 1. Read all lines
lines <- readLines(list)

# 2. Find where the numeric data starts (after 'Zone ...')
start <- grep("^Zone", lines) + 1

# 3. Extract only the numeric part
data_lines <- lines[start:length(lines)]

# 4. Read into a data.frame
df <- read.table(text = data_lines, header = FALSE)

# 5. Get variable names from the VARIABLES line
vars_line <- grep("^VARIABLES", lines, value = TRUE)
vars <- gsub('"', '', sub("^VARIABLES=", "", vars_line))
vars <- strsplit(vars, ",")[[1]]

# 6. Assign names
colnames(df) <- vars 
df%>%
  select(Time,`QVU-12`,`QVD+12`)%>%
  group_by(time_d=ceiling(Time))%>%
  summarise(QU12=sum(`QVU-12`),
            QD12=sum(`QVD+12`))%>%
  mutate(net_Q12=QD12-QU12,
         zone=0)%>%
  select(time_d,zone,net_Q12)->tmp
test_flow=rbind(test_flow,tmp)

#MULTIPLE
setwd("C:\\Users\\glogow0000\\HGS-DSSAT\\model\\HGS\\stand_alone\\lys\\hgs_multi_from_one_shp")
list=dir(pattern = "lys_Eo.nodal_fluid_mass_balance.*")

for (i in 1:length(list)) {
  # 1. Read all lines
  lines <- readLines(list[i])
  
  # 2. Find where the numeric data starts (after 'Zone ...')
  start <- grep("^Zone", lines) + 1
  
  # 3. Extract only the numeric part
  data_lines <- lines[start:length(lines)]
  
  # 4. Read into a data.frame
  df <- read.table(text = data_lines, header = FALSE)
  
  # 5. Get variable names from the VARIABLES line
  vars_line <- grep("^VARIABLES", lines, value = TRUE)
  vars <- gsub('"', '', sub("^VARIABLES=", "", vars_line))
  vars <- strsplit(vars, ",")[[1]]
  
  # 6. Assign names
  colnames(df) <- vars 
  df%>%
    select(Time,`QVU-12`,`QVD+12`)%>%
    group_by(time_d=ceiling(Time))%>%
    summarise(QU12=sum(`QVU-12`),
              QD12=sum(`QVD+12`))%>%
    mutate(net_Q12=QD12-QU12,
           zone=i)%>%
    select(time_d,zone,net_Q12)->tmp
  test_flow=rbind(test_flow,tmp)
}
ggplot(test_flow,aes(x=time_d,y=net_Q12,col=as.factor(zone)))+
  geom_line()
test_flow%>%
  group_by(zone)%>%
  summarise(flow=sum(net_Q12))->flow_All
# Done! You have a data.frame
head(df)
df%>%
  select()
