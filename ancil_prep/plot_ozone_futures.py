import numpy as np
import matplotlib.pyplot as plt
import seaborn

rcp_conc_files = ['/Users/richardmillar/Documents/Thesis_Mac_work/RCPs/8.5/RCP85_MIDYEAR_RADFORCING.csv',
                  '/Users/richardmillar/Documents/Thesis_Mac_work/RCPs/6/RCP6_MIDYEAR_RADFORCING.csv',
                  '/Users/richardmillar/Documents/Thesis_Mac_work/RCPs/4.5/RCP45_MIDYEAR_RADFORCING.csv',
                  '/Users/richardmillar/Documents/Thesis_Mac_work/RCPs/3-PD/RCP3PD_MIDYEAR_RADFORCING.csv']
rcp_cols = ['red','orange','cornflowerblue','navy']

dt = np.dtype({'names':["YEARS","TOTAL_INCLVOLCANIC_RF","VOLCANIC_ANNUAL_RF","SOLAR_RF","TOTAL_ANTHRO_RF","GHG_RF","KYOTOGHG_RF","CO2CH4N2O_RF","CO2_RF","CH4_RF","N2O_RF","FGASSUM_RF","MHALOSUM_RF","CF4","C2F6","C6F14","HFC23","HFC32","HFC43_10","HFC125","HFC134a","HFC143a","HFC227ea","HFC245fa","SF6","CFC_11","CFC_12","CFC_113","CFC_114","CFC_115","CARB_TET","MCF","HCFC_22","HCFC_141B","HCFC_142B","HALON1211","HALON1202","HALON1301","HALON2402","CH3BR","CH3CL","TOTAER_DIR_RF","OCI_RF","BCI_RF","SOXI_RF","NOXI_RF","BIOMASSAER_RF","MINERALDUST_RF","CLOUD_TOT_RF","STRATOZ_RF","TROPOZ_RF","CH4OXSTRATH2O_RF","LANDUSE_RF","BCSNOW_RF"],'formats':54*["f8"]})



rcp_ozone = []
for i in range(0,len(rcp_conc_files)):
  forc_data = np.genfromtxt(rcp_conc_files[i],skip_header=59,delimiter=',',dtype=dt)
  tot_oz_forc = forc_data["STRATOZ_RF"] + forc_data["TROPOZ_RF"]
  rcp_ozone.append(tot_oz_forc)

years = forc_data["YEARS"]

for i in range(0,len(rcp_conc_files)):
  plt.plot(years,rcp_ozone[i],color=rcp_cols[i])

plt.xlim(2000,2050)
plt.ylim(0.3,0.4)

plt.ylabel(r'Ozone radiative forcing (Wm$^{-2}$)',fontsize=15)

plt.show()

