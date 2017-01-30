load('Data/z_trickles_pd_anomaly.Rda')

#Read in the HadCRUT4 observations
hc_data <- read.table('Data/HadCRUT.4.4.0.0.annual_ns_avg.txt',fill=TRUE)
hc_years <- hc_data[,1]
hc_temps <- hc_data[,2]
base_start <- 1881
base_end <- 1900

hc_temps <- hc_temps - mean(hc_temps[hc_years>=base_start & hc_years<=base_end])

png('Figures/z_trickles_gmst_anom.png',width=1200,height=800,res=180)
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
    lines(umid_data$year[order(umid_data$year)],umid_data$gm_field16[order(umid_data$year)],col=sample(colours(), 20),lwd=0.4)
}
#points(hc_years,hc_temps,col='black',pch=16,cex=0.5)
lines(hc_years,hc_temps,col='black',lwd=3)
legend('topleft', c('HadCRUT4'),pch=c(NA) ,lty=c(1),col=c('black'),lwd=c(3),cex=1.0)

dev.off()

