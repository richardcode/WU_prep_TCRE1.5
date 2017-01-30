import numpy as np

def print_line_len(full_line,f_out,max_length=75):

  if len(full_line)>max_length:
    proc_line = full_line
    while len(proc_line)>=max_length:
      lens = np.array([len(f) for f in proc_line.split(',')])
      log = np.cumsum(lens)<=max_length
      num_com = np.sum(log)-1
      cut = np.cumsum(lens)[log][-1]
      print_line = proc_line[:(cut+num_com+1)]
      f_out.write(print_line+'\n')
      proc_line='  '+proc_line[(cut+num_com+1):]
    f_out.write(proc_line)
  else:
    f_out.write(full_line)

  return

#Load in the .csv file for the historical concentrations
ghg_infile = '/Users/richardmillar/Documents/TCRE1p5/WU_prep_TCRE1.5/ghg_namelist/cmip6_histGHGConcentrations.csv'

ghg_data = np.genfromtxt(ghg_infile,skip_header=22,delimiter=",")
years = ghg_data[:,0]

#Select the required gases for the namelist
#CO2, CH4, N2O, CFC11, CFC12, , , CFC113, HCFC22, HFC125 (not complex specified), HFC134A (equivalent) 
ghg_data = ghg_data[:,[1,2,3,28,27,29,32,7,45]]
ghg_data=ghg_data[np.logical_and(years>=1999,years<=2015),:]

sim_years = years[np.logical_and(years>=1999,years<=2015)]

#Convert to mass mixing ratios
mmr_const = 1.0/28.8*np.array([44.01/1e6,16.04/1e9,44.013/1e9,137.36/1e12,120.91/1e12,187.376/1e12,86.47/1e12,120.02/1e12,84.04/1e12])

ghg_mmr = mmr_const[np.newaxis,:] * ghg_data

#Write the um GHG namelist
max_len = 60
f_out = open('ghg_cmip6_hist_19992015_nsy','w')
for i in range(0,ghg_mmr.shape[1]):
  if i==4:
    f_out.write(' CLIM_FCG_NYEARS('+str(i+1)+')= '+str(ghg_mmr.shape[0])+',\n')
    print_line_len(' CLIM_FCG_YEARS(1,'+str(i+1)+')= '+','.join([str(int(f)) for f in sim_years])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_LEVLS(1,'+str(i+1)+')= '+','.join(["{:.6e}".format(f) for f in ghg_mmr[:,i]])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_RATES(1,'+str(i+1)+')= '+','.join([str(f) for f in -32768.0*np.ones_like(ghg_mmr[:,i])])+',\n',f_out,max_length=max_len)

    f_out.write(' CLIM_FCG_NYEARS('+str(6)+')= 0,\n')
    f_out.write(' CLIM_FCG_NYEARS('+str(7)+')= 0,\n')
  elif i==7:
    f_out.write(' CLIM_FCG_NYEARS('+str(10)+')= 0,\n')
  elif i>4 and i<(ghg_mmr.shape[1]-2):
    f_out.write(' CLIM_FCG_NYEARS('+str(i+3)+')= '+str(ghg_mmr.shape[0])+',\n')
    print_line_len(' CLIM_FCG_YEARS(1,'+str(i+3)+')= '+','.join([str(int(f)) for f in sim_years])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_LEVLS(1,'+str(i+3)+')= '+','.join(["{:.6e}".format(f) for f in ghg_mmr[:,i]])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_RATES(1,'+str(i+3)+')= '+','.join([str(f) for f in -32768.0*np.ones_like(ghg_mmr[:,i])])+',\n',f_out,max_length=max_len)
  elif i>4 and i==(ghg_mmr.shape[1]-1):
    f_out.write(' CLIM_FCG_NYEARS('+str(i+3)+')= '+str(ghg_mmr.shape[0])+',\n')
    print_line_len(' CLIM_FCG_YEARS(1,'+str(i+3)+')= '+','.join([str(int(f)) for f in sim_years])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_LEVLS(1,'+str(i+3)+')= '+','.join(["{:.6e}".format(f) for f in ghg_mmr[:,i]])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_RATES(1,'+str(i+3)+')= '+','.join([str(f) for f in -32768.0*np.ones_like(ghg_mmr[:,i])])+',',f_out,max_length=max_len)
  else:
    f_out.write(' CLIM_FCG_NYEARS('+str(i+1)+')= '+str(ghg_mmr.shape[0])+',\n')
    print_line_len(' CLIM_FCG_YEARS(1,'+str(i+1)+')= '+','.join([str(int(f)) for f in sim_years])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_LEVLS(1,'+str(i+1)+')= '+','.join(["{:.6e}".format(f) for f in ghg_mmr[:,i]])+',\n',f_out,max_length=max_len)
    print_line_len(' CLIM_FCG_RATES(1,'+str(i+1)+')= '+','.join([str(f) for f in -32768.0*np.ones_like(ghg_mmr[:,i])])+',\n',f_out,max_length=max_len)

f_out.write('\n /\n')

f_out.close()

