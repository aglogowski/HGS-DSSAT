#### HGS stand alone well observation#### 
setwd("C:\\Users\\glogow0000\\HGS-DSSAT\\model\\HGS\\stand_alone\\lys\\hgs")

library(ggplot2)
library(tidyr)
library(dplyr)
options(scipen=999)
file_path <- "lys_Eo.observation_well_flow.sat_prof.dat"
lines <- readLines(file_path)
# Find the line with VARIABLES
var_line <- grep("^VARIABLES=", lines)
variables <- gsub('^VARIABLES=|\"', '', lines[var_line])
var_names <- strsplit(variables, ",")[[1]]
var_names <- trimws(var_names)


# Find the start lines of ZONE blocks
zone_lines <- grep("^ZONE", lines)
zone_starts <- zone_lines
zone_ends <- c(zone_lines[-1] - 1, length(lines))

# Initialize a list to store zone data
zone_data_list <- list()

for (i in seq_along(zone_starts)) {
  zone_header <- lines[zone_starts[i]]
  
  # Extract SOLUTIONTIME from ZONE header
  sol_time <- as.numeric(sub(".*SOLUTIONTIME=([0-9.Ee+-]+).*", "\\1", zone_header))
  
  # Extract number of rows in this zone (from I=13)
  num_rows <- as.numeric(sub(".*I=([0-9]+).*", "\\1", zone_header))
  
  # Extract the raw data block
  data_lines <- lines[(zone_starts[i] + 1):zone_ends[i]]
  data_values <- as.numeric(unlist(strsplit(paste(data_lines, collapse = " "), "\\s+")))
  
  # Convert to data.frame
  zone_df <- as.data.frame(matrix(data_values, ncol = length(var_names), byrow = TRUE))
  colnames(zone_df) <- var_names
  zone_df$time <- sol_time
  
  # Store it
  zone_data_list[[i]] <- zone_df
}
final_data <- do.call(rbind, zone_data_list)



#### HGS stand alone water balance ####
lines_w=readLines("lys_Eo.water_balance.dat")
# Find line with VARIABLES
var_line_index <- grep("^VARIABLES=", lines_w)
var_line <- lines_w[var_line_index]

# Extract variable names
# Remove 'VARIABLES=' and split on comma
var_names <- gsub('^VARIABLES=', '', var_line)
var_names <- gsub('"', '', var_names)  # remove quotes
var_names <- trimws(unlist(strsplit(var_names, ",")))

# Find the first line of actual data (starts after 'zone t=' line)
zone_line_index <- grep("^zone",lines_w, ignore.case = TRUE)
data_start_index <- zone_line_index + 1

# Read the data portion only
data_lines <- lines_w[data_start_index:length(lines_w)]
data <- read.table(text = paste(data_lines, collapse = "\n"), col.names = var_names)

data$time_d=data$Time[1]
data$time_d[2:length(data$Time)]=data$Time[2:length(data$Time)]-data$Time[1:(length(data$Time)-1)]
data=data[,c(1,21,2:20)]


setwd("C:\\Users\\glogow0000\\HGS-DSSAT\\analysis\\HGS_standalone")
write.table(data,"hgs_watbal.csv",col.names = T,row.names = F,sep = ",",dec = ".")

data[,c(3:21)]=data[,c(3:21)]/4*data$time_d*1000
data_stand_alone=data
#colSums(data[,c(3:21)])
#### dssat ####
setwd("C:\\Users\\glogow0000\\HGS-DSSAT\\analysis\\DSSAT_no_inflow_satflow")
library(readxl)
dssat=read_xlsx(path = "dssat-hgs.xlsx",sheet = "Sat layer DSSAT wheat",skip = 1)
dssat[,c(2:10)]= dssat[,c(2:10)]/0.44
dssat
colnames(dssat)=c("time","2.95","2.85","2.7","2.55","2.4","2.25","2.1","1.8","1.5")
dssat%>%
  gather("Zsurf","VWC",`2.95`:`1.5`)->dssat
dssat$Zsurf=as.numeric(dssat$Zsurf)
dssat$model="dssat"
final_data%>%
  select(time,Zsurf,VWC)%>%
  filter(Zsurf>1&Zsurf<3 )->hgs
hgs$model="hgs"


ggplot() +
  geom_line(data = hgs, aes(x = time, y = VWC, col = model), size = 1) +
  geom_point(data = dssat, aes(x = time, y = VWC, color = model), size = 1, shape = 16)+
  ylim(0,1)+
  labs(x = "Time", y = "Volumetric Water Content (VWC)", color = "Zsurf") +
  facet_wrap(~as.factor(Zsurf))+
  
  theme_minimal()

colSums(data[,c(3:21)])

#### dssat Copuled####
setwd("C:\\Users\\glogow0000\\HGS-DSSAT\\model\\coupled_v1\\dssat\\1")
library(readr)

lines <- readLines("SoilWat.OUT")
header_line <- grep("^@YEAR", lines)[1]   # take only the first match

# Extract the header, clean it
header <- strsplit(trimws(lines[header_line]), "\\s+")[[1]]
header[1] <- sub("^@", "", header[1])  # remove @

# Read the data starting after the header line
df <- read_table2("SoilWat.OUT", skip = header_line)

# Apply cleaned column names
names(df) <- header

# Keep YEAR, DOY, DAS and SW columns
sw_df <- df[, c("YEAR", "DOY", "DAS", grep("^SW[0-9]+D$", names(df), value = TRUE))]
sw_df[] <- lapply(sw_df, function(x) as.numeric(as.character(x)))
head(sw_df)
dssat_coup=sw_df[,c(3:12)]
dssat_coup[,c(2:10)]= dssat_coup[,c(2:10)]/0.44
dssat_coup
colnames(dssat_coup)=c("time","2.95","2.85","2.7","2.55","2.4","2.25","2.1","1.8","1.5")
dssat_coup%>%
  gather("Zsurf","VWC",`2.95`:`1.5`)->dssat_coup
dssat_coup$Zsurf=as.numeric(dssat_coup$Zsurf)
dssat_coup$model="copuled_dssat"
 #### HGS-DSSAT copuled ####
setwd("C:\\Users\\glogow0000\\HGS-DSSAT\\model\\coupled_v1\\hgs")
files <- list.files(pattern = "\\.observation_well_flow.sat_prof.dat$", ignore.case = TRUE)
 
day_numbers <- as.numeric(sub(".*lys_e_day([0-9]+)o.*", "\\1", files))

# Sort by the extracted numbers
files_sorted <- files[order(day_numbers)]


all_data_list <- list()
for (file_idx in seq_along(files_sorted)) {
  # Read file
  lines <- readLines(files[file_idx])
  
  # --- Extract variable names ---
  var_line <- grep("^VARIABLES=", lines)
  variables <- gsub('^VARIABLES=|\"', '', lines[var_line])
  var_names <- strsplit(variables, ",")[[1]]
  var_names <- trimws(var_names)
  
  # --- Find ZONE blocks ---
  zone_lines <- grep("^ZONE", lines)
  zone_starts <- zone_lines
  zone_ends <- c(zone_lines[-1] - 1, length(lines))
  
  # Initialize list for this file's zones
  zone_data_list <- list()
  
  for (i in seq_along(zone_starts)) {
    zone_header <- lines[zone_starts[i]]
    
    # Extract SOLUTIONTIME
    sol_time <- as.numeric(sub(".*SOLUTIONTIME=([0-9.Ee+-]+).*", "\\1", zone_header))
    
    # Extract number of rows (I=...)
    num_rows <- as.numeric(sub(".*I=([0-9]+).*", "\\1", zone_header))
    
    # Extract raw data block
    data_lines <- lines[(zone_starts[i] + 1):zone_ends[i]]
    data_values <- as.numeric(unlist(strsplit(paste(data_lines, collapse = " "), "\\s+")))
    
    # Create data.frame
    zone_df <- as.data.frame(matrix(data_values, ncol = length(var_names), byrow = TRUE))
    colnames(zone_df) <- var_names
    zone_df$time <- sol_time
    zone_df$file <- basename(files[file_idx])  # Keep track of source file
    day_num <- as.numeric(sub(".*lys_e_day([0-9]+).*", "\\1", zone_df$file))
    # Create mod_time column as time + extracted number
    zone_df$mod_time <- zone_df$time + day_num
    # Store
    zone_data_list[[i]] <- zone_df
  }
  
  # Combine zones from this file
  file_data <- do.call(rbind, zone_data_list)
  all_data_list[[file_idx]] <- file_data
}

# Combine all files into final dataframe
final_data <- do.call(rbind, all_data_list)
final_data%>%
  arrange(mod_time)%>%
  select("time"=mod_time,Zsurf,VWC)%>%
  mutate(model="copuled_HGS")%>%
  filter(Zsurf>1 & Zsurf<3)->hgs_dssat_coup

ggplot() +
  geom_line(data = hgs, aes(x = time, y = VWC, col = model), size = 0.3) +
  geom_point(data = dssat, aes(x = time, y = VWC, color = model), size = 1, shape = 16) +
  geom_point(data = dssat_coup, aes(x = time, y = VWC, color = model), size = 1, shape = 16) +
  geom_line(data = hgs_dssat_coup, aes(x = time, y = VWC, color = model), size = 1) +
  labs(x = "Time", y = "Volumetric Water Content (VWC)", color = "Models") +
  facet_wrap(~as.factor(Zsurf))+
  theme_minimal()

files_wat_bal=list.files(pattern = "\\.water_balance.dat$", ignore.case = TRUE)

all_data_list_wb <- list()

for (file_idx in seq_along(files_wat_bal)) {
  # Read file
  lines_w <- readLines(files_wat_bal[file_idx])
  
  # --- Extract variable names ---
  var_line_index <- grep("^VARIABLES=", lines_w)
  var_line <- lines_w[var_line_index]
  var_names <- gsub('^VARIABLES=', '', var_line)
  var_names <- gsub('"', '', var_names)
  var_names <- trimws(unlist(strsplit(var_names, ",")))
  
  # --- Locate and read data ---
  zone_line_index <- grep("^zone", lines_w, ignore.case = TRUE)
  data_start_index <- zone_line_index + 1
  data_lines <- lines_w[data_start_index:length(lines_w)]
  
  data <- read.table(text = paste(data_lines, collapse = "\n"),
                     col.names = var_names)
  if (file_idx == 1 && !("Fnodal_2" %in% names(data))) {
    data <- data.frame(
      data[, 1:2],               # first two columns
      `Fnodal_2` = 0,            # insert zero column
      data[, 3:ncol(data)]       # rest of the columns
    )
    names(data)[4] <- "Rain_3"
  } 
  # --- Calculate time_d ---
  data$time_d <- data$Time[1]
  data$time_d[2:length(data$Time)] <- data$Time[2:length(data$Time)] - data$Time[1:(length(data$Time)-1)]
  
  # --- Extract day number from filename ---
  day_num <- as.numeric(sub(".*lys_e_day([0-9]+).*", "\\1", basename(files_wat_bal[file_idx])))
  
  # --- Add file and mod_time columns ---
  data$file <- basename(files_wat_bal[file_idx])
  data$mod_time <- data$time_d + day_num
  
  # Store in list
  all_data_list_wb[[file_idx]] <- data
}

# Combine all
rm(final_data_wb)
final_data_wb <- do.call(rbind, all_data_list_wb)
final_data_wb%>%
  arrange(mod_time)->final_data_wb

final_data_wb[,c(2:12)]=final_data_wb[,c(2:12)]/4*final_data_wb$time_d*1000
final_data_wb%>%
  group_by(ceiling(mod_time))%>%
  summarise(nflux=sum(Fnodal_2))->test
sum(test$nflux)
colSums(final_data_wb[,c(2:12)])
colSums(data_stand_alone[,c(3:21)])
coup_wat_bal_sum=colSums(final_data_wb[,c(2:12)])
stand_alone_wat_bal_sum=colSums(data_stand_alone[,c(3:21)])
write.table(coup_wat_bal_sum,"C:\\Users\\glogow0000\\HGS-DSSAT\\analysis\\Copuled\\coup_wat_bal.csv",sep = ";")
write.table(stand_alone_wat_bal_sum,"C:\\Users\\glogow0000\\HGS-DSSAT\\analysis\\Copuled\\stand_alone_wat_bal.csv",sep = ";")
