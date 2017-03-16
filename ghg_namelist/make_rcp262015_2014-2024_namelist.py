import numpy as np
from make_cmip6_hist_ghgnamelist import print_line_len

#Load the RCP2.6 concentration timeseries and get the year-on-year changes
cmip5_infile = '/Users/rm604/Documents/Thesis_Mac_work/RCPs/3-PD/RCP3PD_MIDYEAR_CONCENTRATIONS.csv'

cmip5_data = np.genfromtxt(cmip5_infile,skip_header=39,delimiter=",")
cmip5_years_all = cmip5_data[:,0]
cmip5_data = cmip5_data[:,[3,4,5,20,21,22,27,14,15]]
cmip5_data = cmip5_data[np.logical_and(cmip5_years_all>=2009,cmip5_years_all<=2100),:]

yoy_rates = np.ones_like(cmip5_data)
for i in range(1,cmip5_data.shape[0]):
  yoy_rates[i] = cmip5_data[i] / cmip5_data[i-1]
                                       
                                       
ghg_infile = '/Users/rm604/Documents/TCRE1p5/WU_prep_TCRE1.5/ghg_namelist/cmip6_histGHGConcentrations.csv'

ghg_data = np.genfromtxt(ghg_infile,skip_header=22,delimiter=",")
years = ghg_data[:,0]

#Select the required gases for the namelist
#CO2, CH4, N2O, CFC11, CFC12, , , CFC113, HCFC22, HFC125 (not complex specified), HFC134A
ghg_data = ghg_data[:,[1,2,3,28,27,29,32,7,4]]
ghg_data=ghg_data[years==2014,:]


#Convert to mass mixing ratios
mmr_const = 1.0/28.8*np.array([44.01/1e6,16.04/1e9,44.013/1e9,137.36/1e12,120.91/1e12,187.376/1e12,86.47/1e12,120.02/1e12,84.04/1e12])

ghg_mmr = mmr_const[np.newaxis,:] * ghg_data

#Create the data for the rest of the century
years = np.arange(2014,2101)
adj_mmr = np.zeros((years.shape[0],9))
adj_mmr[0] = ghg_mmr
for i in range(1,adj_mmr.shape[0]):
  adj_mmr[i] = adj_mmr[i-1] * yoy_rates[i]

sim_years = years[np.logical_and(years>=2014,years<=2025)]
adj_mmr = adj_mmr[np.logical_and(years>=2014,years<=2025),:]


#Write the um GHG namelist
max_len = 60
f_out = open('ghg_rcp262015_20142025','w')
for i in range(0,adj_mmr.shape[1]):
  if i==4:
    f_out.write(' CLIM_FCG_NYEARS('+str(i+1)+')= '+str(adj_mmr.shape[0])+',\n')
    print_line_len(' CLIM_FCG_YEARS(1,'+str(i+1)+')= '+','.join([str(int(f)) for f in sim_years])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_LEVLS(1,'+str(i+1)+')= '+','.join(["{:.6e}".format(f) for f in adj_mmr[:,i]])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_RATES(1,'+str(i+1)+')= '+','.join([str(f) for f in -32768.0*np.ones_like(adj_mmr[:,i])])+',\n',f_out,max_length=max_len)

    f_out.write(' CLIM_FCG_NYEARS('+str(6)+')= 0,\n')
    f_out.write(' CLIM_FCG_NYEARS('+str(7)+')= 0,\n')
  elif i==7:
    #f_out.write(' CLIM_FCG_NYEARS('+str(10)+')= 0,\n')
    f_out.write(' CLIM_FCG_NYEARS('+str(i+3)+')= '+str(adj_mmr.shape[0])+',\n')
    print_line_len(' CLIM_FCG_YEARS(1,'+str(i+3)+')= '+','.join([str(int(f)) for f in sim_years])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_LEVLS(1,'+str(i+3)+')= '+','.join(["{:.6e}".format(f) for f in adj_mmr[:,i]])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_RATES(1,'+str(i+3)+')= '+','.join([str(f) for f in -32768.0*np.ones_like(adj_mmr[:,i])])+',\n',f_out,max_length=max_len)
  elif i>4 and i<(adj_mmr.shape[1]-2):
    f_out.write(' CLIM_FCG_NYEARS('+str(i+3)+')= '+str(adj_mmr.shape[0])+',\n')
    print_line_len(' CLIM_FCG_YEARS(1,'+str(i+3)+')= '+','.join([str(int(f)) for f in sim_years])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_LEVLS(1,'+str(i+3)+')= '+','.join(["{:.6e}".format(f) for f in adj_mmr[:,i]])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_RATES(1,'+str(i+3)+')= '+','.join([str(f) for f in -32768.0*np.ones_like(adj_mmr[:,i])])+',\n',f_out,max_length=max_len)
  elif i>4 and i==(adj_mmr.shape[1]-1):
    f_out.write(' CLIM_FCG_NYEARS('+str(i+3)+')= '+str(adj_mmr.shape[0])+',\n')
    print_line_len(' CLIM_FCG_YEARS(1,'+str(i+3)+')= '+','.join([str(int(f)) for f in sim_years])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_LEVLS(1,'+str(i+3)+')= '+','.join(["{:.6e}".format(f) for f in adj_mmr[:,i]])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_RATES(1,'+str(i+3)+')= '+','.join([str(f) for f in -32768.0*np.ones_like(adj_mmr[:,i])])+',',f_out,max_length=max_len)
  else:
    f_out.write(' CLIM_FCG_NYEARS('+str(i+1)+')= '+str(adj_mmr.shape[0])+',\n')
    print_line_len(' CLIM_FCG_YEARS(1,'+str(i+1)+')= '+','.join([str(int(f)) for f in sim_years])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_LEVLS(1,'+str(i+1)+')= '+','.join(["{:.6e}".format(f) for f in adj_mmr[:,i]])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_RATES(1,'+str(i+1)+')= '+','.join([str(f) for f in -32768.0*np.ones_like(adj_mmr[:,i])])+',\n',f_out,max_length=max_len)

f_out.write('\n /\n')

f_out.close()



