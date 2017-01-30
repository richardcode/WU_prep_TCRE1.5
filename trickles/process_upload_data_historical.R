hist_data <- read.table('Data/z_upload_decmeans_raw_pe.txt',header=TRUE)
#cont_data <- read.table('Data/y_upload_decmeans_raw_pe.txt',header=TRUE)
load('Data/training_cont_unq_pe.Rda')

hist_data <- hist_data[complete.cases(hist_data),]
cont_data <- cont_data[complete.cases(cont_data),]


same_umid <- function (x) { return (paste('y',substring(x,2,4),sep='')) } 
hist_data$umid <- lapply(hist_data$umid, same_umid) 

#Remove the outliers and dodgey data 
hist_data <- hist_data[hist_data$field16 > 0.0,] 
hist_data <- hist_data[hist_data$field184 > -5.0e+33,]
hist_data <- hist_data[hist_data$field56 > -2.0e+8,]
hist_data <- hist_data[hist_data$field260 < -3.08e+8,]
hist_data <- hist_data[hist_data$field207 < 70.0,]
hist_data <- hist_data[hist_data$field200 < 341.65,]
hist_data <- hist_data[hist_data$field1371_1 > -1.0e+5,]
hist_data <- hist_data[hist_data$field1371_1 < 1.0e-07,]
hist_data <- hist_data[hist_data$field1370_1 < 1.0e+30,]
hist_data <- hist_data[hist_data$field1373_1 < 1.0e-10,]
hist_data <- hist_data[hist_data$field8 > 100500,]
hist_data <- hist_data[hist_data$field1372_1 < 1.0e-11,]
hist_data <- hist_data[hist_data$field1374_1 < 2.0e-10,]
hist_data <- hist_data[hist_data$field57 > -5.0e+13,]
hist_data <- hist_data[hist_data$field186_1 > -3.15e+8,]
hist_data <- hist_data[hist_data$field186_1 < -3.05e+8,]
hist_data <- hist_data[hist_data$field187_1 < -3.05e+8,]

hist_data_unq <- data.frame(matrix(ncol = 54, nrow = 0))
for (umid in unique(hist_data$umid)) { 
     umid_data <- hist_data[hist_data$umid==umid,]
     for (year in unique(umid_data$dec_start)) {
          umid_data_year <- umid_data[umid_data$dec_start==year,]
          #Mean across any duplicates here
          umid_row <- data.frame(matrix(ncol = 54, nrow = 1))
          colnames(umid_row) <- colnames(hist_data)
          umid_row[1,1] <- as.character(umid)
          umid_row[1,-1] <- apply(umid_data_year[,-1],2,mean)
          hist_data_unq<-rbind(hist_data_unq,umid_row)
     }
}
save(hist_data_unq, file='Data/hist_hist_unq_pe.Rda')



#Calculate the net toa imbalances
hist_data_unq$nettoa <- hist_data_unq$field200 - hist_data_unq$field201 - hist_data_unq$field206
cont_data_unq$nettoa <- cont_data_unq$field200 - cont_data_unq$field201 - cont_data_unq$field206

#Do the differences 
dhist_data <- data.frame(matrix(ncol = 55, nrow = 0))
for (umid in unique(hist_data_unq$umid)) {
     print(umid)
     if (umid %in% cont_data_unq$umid){ 
        dumid_data <- hist_data_unq[hist_data_unq$umid==umid,]
        cumid_data <- cont_data_unq[cont_data_unq$umid == umid,] 
        for (year in unique(dumid_data$dec_start)) {
            if (year %in% cumid_data$dec_start) {
                dumid_data_year <- dumid_data[dumid_data$dec_start==year,]
                cumid_data_year <- cumid_data[cumid_data$dec_start==year,]
                #Do the differences here any duplicates here
                umid_row <- data.frame(matrix(ncol = 55, nrow = 1))
                colnames(umid_row) <- colnames(cont_data_unq)
                umid_row[1,1] <- as.character(umid)
                umid_row[1,2] <- year
                umid_row[1,c(-1,-2)] <- dumid_data_year[1,c(-1,-2)] - cumid_data_year[1,c(-1,-2)]
                dhist_data<-rbind(dhist_data,umid_row)
            }
        }
     }
}
dhist_data$dec_start <- dhist_data$dec_start
save(dhist_data, file='Data/hist_diffhist_unq_pe.Rda')




