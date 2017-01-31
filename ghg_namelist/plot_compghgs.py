import numpy as np
import matplotlib.pyplot as plt

#Load in the .csv file for the historical concentrations
ghg_infile = '/Users/richardmillar/Documents/TCRE1p5/WU_prep_TCRE1.5/ghg_namelist/cmip6_histGHGConcentrations.csv'

ghg_data = np.genfromtxt(ghg_infile,skip_header=22,delimiter=",")
years = ghg_data[:,0]

#Select the required gases for the namelist
#CO2, CH4, N2O, CFC11, CFC12, , , CFC113, HCFC22, HFC125 (not complex specified), HFC134A (equivalent)
ghg_data = ghg_data[:,[1,2,3,28,27,29,32,7,4]]


#Load the CMIP5 historical concentrations
rcp_files = ['/Users/richardmillar/Documents/Thesis_Mac_work/RCPs/8.5/RCP85_MIDYEAR_CONCENTRATIONS.csv','/Users/richardmillar/Documents/Thesis_Mac_work/RCPs/6/RCP6_MIDYEAR_CONCENTRATIONS.csv','/Users/richardmillar/Documents/Thesis_Mac_work/RCPs/4.5/RCP45_MIDYEAR_CONCENTRATIONS.csv','/Users/richardmillar/Documents/Thesis_Mac_work/RCPs/3-PD/RCP3PD_MIDYEAR_CONCENTRATIONS.csv']

rcp_data=[]
for cmip5_infile in rcp_files:
  cmip5_data = np.genfromtxt(cmip5_infile,skip_header=39,delimiter=",")
  cmip5_years_all = cmip5_data[:,0]
  cmip5_data = cmip5_data[:,[3,4,5,20,21,22,27,14,15]]
  cmip5_data = cmip5_data[np.logical_and(cmip5_years_all>=years[0],cmip5_years_all<=years[-1]),:]
  rcp_data.append(cmip5_data)

#Plot the differences of the timeseries over the historical period
col_rcp = ['red','orange','lightblue','blue']
titles=[r'CO$_{2}$',r'CH$_{4}$',r'N$_{2}$O','CFC11','CFC12','CFC113','HCFC22','HFC125','HFC134A']
units = ['ppm','ppb','ppb','ppt','ppt','ppt','ppt','ppt','ppt']
scens= ['RCP8.5','RCP6.0','RCP4.5','RCP2.6']
lowy = [350,1600,305,200,450,60,70,0,0]
highy=[410,1900,330,280,550,90,250,16,90]
fig = plt.figure(figsize=(10,10))
fig.subplots_adjust(left=0.06,right=0.95,top=0.95,bottom=0.05,wspace=0.28)
for i in range(0,ghg_data.shape[1]):
  ax_i = fig.add_subplot(3,3,i+1)
  for x in range(0,len(rcp_data)):
    ax_i.plot(years,rcp_data[x][:,i],color=col_rcp[x],linewidth=1,label=scens[x])
  ax_i.plot(years,ghg_data[:,i],color='black',linewidth=1,label='CMIP6')
  ax_i.set_xlim(1990,2015)
  ax_i.set_ylim(lowy[i],highy[i])
  ax_i.set_ylabel(units[i],fontsize=12)
  ax_i.set_title(titles[i],fontsize=15)
  plt.grid()
  if i==0:
    plt.legend(loc='best',fontsize=10)

fig.savefig('../Figures/compghgs.png',dpi=300)
