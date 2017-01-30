load('Data/training_tcr_data.Rda')
load('Data/training_sens_data_final.Rda')
load('Data/training_difframp_unq_pe_final.Rda')
load('Data/hist_diffhist_unq_pe.Rda')

#Load the observations of the radiative forcing ensemble
hist_rf_ens <- read.csv('Data/obs_histforc_ens.csv',header=FALSE)
hist_rf_years <- c(1750.:2012.)


#Create dataframe of z umids and their TCR and ECS
zsens_data <- sens_data[,c('umid','ecs','frc')]
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

#Get distribution of forcing over last decade of simulation
obs_rf_period_dist <- rowMeans(hist_rf_ens[,hist_rf_years>= p_start & hist_rf_years<=p_end])

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


#Calculate the radiative forcing over the historical period
#Calculate average radiative forcing over a decade of the ramp
ramp_years <- c(0:80)
ave_forc <- ramp_years/70.
dec_start <- c(1,11,21,31,41,51,61,71)
dec_end <- c(10,20,30,40,50,60,70,80)
ave_forc_l <- c()
for (x in c(1:length(dec_start))){
    ave_forc_l <- c(ave_forc_l, mean(ave_forc[(ramp_years>=dec_start[x]) & (ramp_years<=dec_end[x])]))
    
}


#Fit a kappa model to the 1%/yr data using ERF from 2xCO2
zsens_data$rho <- NA
for (umid in unique(zsens_data$umid)) {
    if ((paste('y',substring(umid[[1]],2,5),sep='') %in% dramp_data$umid) & (length(zsens_data[zsens_data$umid==umid[[1]],'frc'])>=1)) {
        umid_data <- dramp_data[dramp_data$umid == paste('y',substring(umid[[1]],2,5),sep=''),]
        rho <- summary(lm(zsens_data[zsens_data$umid == umid[[1]],'frc'] * ave_forc_l[dec_start %in% umid_data$dec_start] ~ umid_data[,'field16']))$coefficients[2]
        zsens_data[zsens_data$umid == umid[[1]],'rho'] <- rho
    }
}
hist_data_a$frc_k <- NA
for (umid in unique(hist_data_a$umid)) {
    if (umid[[1]] %in% zsens_data$umid) {
        if (is.na(zsens_data[zsens_data$umid == umid[[1]],'rho'])==FALSE) {
            umid_data <- hist_data_a[hist_data_a$umid == umid[[1]],]
            hist_data_a[hist_data_a$umid == umid[[1]],'frc_k'] <- umid_data$gm_field16 * zsens_data[zsens_data$umid == umid[[1]],'rho']
        }
    }
}

#Use Forster et al 2013 method to get average decadal radiative forcing
dhist_data$frc <- NA
for (umid in unique(dhist_data$umid)) {
    if (umid %in% unique(sens_data$umid)) {
        lamb <- sens_data[sens_data$umid == umid,'fbp']
        forc_ts <- dhist_data[dhist_data$umid==umid,'nettoa'] - lamb*dhist_data[dhist_data$umid==umid,'field16']
        dhist_data[dhist_data$umid==umid,'frc'] <- forc_ts
    }
}

#Add the forcing anomalies over the period to the restart available data
zsens_data$frc <- NA
for (umid in unique(zsens_data$umid)) {
    if (paste('y',substring(umid[[1]],2,4),sep='') %in% dhist_data$umid) {
        yumid <- paste('y',substring(umid[[1]],2,4),sep='')
        yumid_data <- dhist_data[dhist_data$umid==yumid,]
        if (c(1991) %in% yumid_data$dec_start) {
            if (is.na(yumid_data[yumid_data$dec_start==1991,'frc'])!=TRUE) {
                zsens_data[zsens_data$umid == umid,'frc'] <- yumid_data[yumid_data$dec_start==1991,'frc']
            }
        }
    }
}

plot(zsens_data$frc,zsens_data$tcr)
abline(v=quantile(obs_rf_period_dist,0.5),col='black',lwd=3,lty=2)
abline(v=quantile(obs_rf_period_dist,0.95),col='grey',lwd=1.5,lty=2)
abline(v=quantile(obs_rf_period_dist,0.05),col='grey',lwd=1.5,lty=2)


png('Figures/z_trickles_gmst_kappaforc.png',width=1200,height=800,res=180)
plot(hist_data_a$year,hist_data_a$gm_field16,
col = NA,
#     type = "p",
#     xaxt = "n", yaxt = "n",
#     xlim = c(0,71),
ylim = c(-1,2),
xlab = expression("Year"),
ylab = 'Temperature anomaly (K)',
cex = 2.0,
)
grid()

for (umid in unique(hist_data_a$umid)) {
    umid_data <- hist_data_a[hist_data_a$umid == umid,]
    lines(umid_data$year[order(umid_data$year)],umid_data$frc[order(umid_data$year)],col=sample(colours(), 20),lwd=0.4)
}
#points(hc_years,hc_temps,col='black',pch=16,cex=0.5)
lines(hc_years,hc_temps,col='black',lwd=3)
legend('topleft', c('HadCRUT4'),pch=c(NA) ,lty=c(1),col=c('black'),lwd=c(3),cex=1.0)

dev.off()







