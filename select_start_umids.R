load('Data/training_tcr_data.Rda')
load('Data/training_sens_data_final.Rda')

#Create dataframe of z umids and their TCR and ECS
zsens_data <- sens_data[,c('umid','ecs')]
zsens_data$tcr <- NA
for (umid in zsens_data$umid) {
    if (umid %in% upload_tcr$umid) {
        zsens_data[zsens_data$umid == umid,'tcr'] <- upload_tcr[upload_tcr$umid == umid,'field16']
    }
}
same_umid <- function (x) { return (paste('z',substring(x,2,4),sep='')) }
zsens_data$umid <- lapply(zsens_data$umid, same_umid)


#Load the historical z series data and calculate the trends over the historical period
p_start <- 1991
p_end<- 2000
load('Data/z_trickles_pd_anomaly.Rda')

zsens_data$trend <- NA
zsens_data$anom <- NA
for (umid in unique(hist_data_a$umid)) {
    umid_data <- hist_data_a[hist_data_a$umid == umid[[1]],]
    trend_fit <- lm(gm_field16 ~ year, data=umid_data)
    trend <- trend_fit$coefficients['year']
    anom <- mean(umid_data[(umid_data$year>=p_start & umid_data$year<=p_end),'gm_field16'])
    if (umid[[1]] %in% zsens_data$umid) {
        zsens_data[zsens_data$umid==umid[[1]],'trend'] <- trend
        zsens_data[zsens_data$umid==umid[[1]],'anom'] <- anom
    }
}

#Read in the HadCRUT4 observations and calculate observed trend
hc_data <- read.table('Data/HadCRUT.4.4.0.0.annual_ns_avg.txt',fill=TRUE)
hc_years <- hc_data[,1]
hc_temps <- hc_data[,2]
base_start <- 1881
base_end <- 1900
hc_temps <- hc_temps - mean(hc_temps[hc_years>=base_start & hc_years<=base_end])
hc_trend_fit <- lm(hc_temps ~ hc_years)
hc_trend <- hc_trend_fit$coefficients['hc_years']

#Find distribution of HadCRUT trends from ensemble
hc_trends <- c()
hadcrut_dir <- '/Users/richardmillar/Documents/Thesis_Mac_work/HadCRUT/'
hc_files <- list.files(hadcrut_dir)
hc_ens <- matrix(nrow=166,ncol=100)
hc_stds <- matrix(nrow=166,ncol=100)
for (f in c(1:100)) {
    data <- read.table(paste(hadcrut_dir,hc_files[f],sep=''))
    hc_temps_e <- data[,2]
    hc_std <- data[,3]
    hc_years_e <- data[,1]
    
    fit <- lm(hc_temps_e ~ hc_years[-c(length(hc_years))])
    hc_trends <- c(hc_trends,fit$coefficients[2])
    
    hc_ens[,f] <- hc_temps_e
    hc_stds[,f] <- hc_std
    
    
}
hc_trends <- as.vector(hc_trends)


#Find the mean and std of the reference period
hc_ens_b <- hc_ens[(hc_years_e>=base_start & hc_years_e<=base_end),]
#Calculate the ensemble covariance matrix for base period (observations are ensemble members at each point in time
cov_b <- cov(t(hc_ens_b))
#Add a diagnoal matrix for variance within each ensemble member due to global averaging
cov_b <- cov_b + diag(x=(hc_std[(hc_years_e>=base_start & hc_years_e<=base_end)])**2)
#Average both ensemble members and over time for both values and covariances
base_mean <- mean(rowMeans(hc_ens_b))
std_base <-  sqrt(mean(rowMeans(cov_b)))

#Do the same for the period of interest for selecting restarts
hc_ens_p <- hc_ens[(hc_years_e>=p_start & hc_years_e<=p_end),]
cov_p <- cov(t(hc_ens_p))
cov_p <- cov_p + diag(x=(hc_std[(hc_years_e>=p_start & hc_years_e<=p_end)])**2)
p_mean <- mean(rowMeans(hc_ens_p))
std_p <-  sqrt(mean(rowMeans(cov_p)))

#Calculate the observational anomalies and the std (assuming adding in quadrature)
p_anom = p_mean - base_mean
#Include an additional 0.08 error to represent internal variability (Otto et al 2013)
p_std = sqrt(std_base**2 + std_p**2 + 0.08**2)



plot(zsens_data$trend,zsens_data$tcr)
abline(v=hc_trend,col='black',lwd=3,lty=2)
abline(v=quantile(hc_trends,0.95),col='grey',lwd=1.5,lty=2)
abline(v=quantile(hc_trends,0.05),col='grey',lwd=1.5,lty=2)

plot(zsens_data$anom,zsens_data$tcr)
abline(v=p_anom,col='black',lwd=3,lty=2)
abline(v=p_anom-2*p_std,col='grey',lwd=1.5,lty=2)
abline(v=p_anom+2*p_std,col='grey',lwd=1.5,lty=2)


