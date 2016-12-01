#Process the trickle data to use in the analysis
hist_data <- read.table('Data/z_trickles_pd.txt',fill=TRUE)
hist_data <- hist_data[complete.cases(hist_data),]

colnames(hist_data) <- c('umid','year','gm_field37','gm_field34','gm_field30','gm_field16','gm_field259','gm_field108','gm_field118','gm_field119','gm_field97','gm_field184','gm_field687','gm_field211','gm_field210','gm_field207','gm_field205','gm_field203','gm_field200','gm_field208','gm_field90', 'gm_field95','gm_field98','gm_field99','gm_field88','gm_field56','gm_field57','gm_field187','gm_field8','gm_field40',
'rm_n34_field187','rm_n34_field184','rm_n34_field37',
'rm_n34_field34','rm_n34_field30','rm_n34_field40',
'rm_n34_field259','rm_n34_field57','rm_n34_field56',
'rm_n34_field208','rm_n34_field205','rm_n34_field207',
'rm_n34_field200','rm_n34_field203','rm_n34_field119',
'rm_n34_field118','rm_n34_field687','rm_n34_field88',
'rm_n34_field210','rm_n34_field211','rm_n34_field108',
'rm_n34_field95','rm_n34_field97','rm_n34_field90',
'rm_n34_field99','rm_n34_field98','rm_n34_field8',
'rm_n34_field16')


#REMOVE OUTLIERS, WHEN DISOCOVERED
hist_data <- hist_data[(hist_data$gm_field16 > 280),]
hist_data <- hist_data[(hist_data$gm_field16 < 350),]

#Save in R dataframe format
save(hist_data, file='Data/z_trickles_pd.Rda')

#Load in the z trickles
load('Data/z_trickles_pd.Rda')

#Express temperature as anomalies from a base-period
base_start <- 1881
base_end <- 1900
hist_data_a <- data.frame(matrix(nrow=0,ncol=ncol(hist_data)))
for (umid in unique(hist_data$umid)) {
    umid_data <- hist_data[hist_data$umid == umid,]
    base_mean <- colMeans(umid_data[umid_data$year <= base_end & umid_data$year >= base_start,c(-1,-2)])
    anom <- sweep(umid_data[,c(-1,-2)],2,c(base_mean))
    anom_df <- data.frame(matrix(nrow=nrow(umid_data),ncol=ncol(umid_data)))
    anom_df[,c(-1,-2)] <- anom
    anom_df[,c(1,2)] <- umid_data[,c(1,2)]
    colnames(anom_df) <- colnames(umid_data)
    hist_data_a <- rbind(hist_data_a,anom_df)
}

same_umid <- function (x) { return (paste('z',substring(x,2,4),sep='')) }
hist_data_a$umid <- lapply(hist_data_a$umid, same_umid)


save(hist_data_a, file='Data/z_trickles_pd_anomaly.Rda')
