import iris
import numpy as np
import iris.coord_categorisation
import matplotlib.pyplot as plt

cube = iris.load_cube('solarforcing-ref-mon_input4MIPs_solar_CMIP_SOLARIS-HEPPA-3-2_gn_18500101-22991231.nc','solar_irradiance')
iris.coord_categorisation.add_year(cube, 'time', name='year')
ycube = cube.aggregated_by(['year'],iris.analysis.MEAN)

cmip_soldata = ycube.data
cmip_solyears = ycube.coord('year').points

#Scale down the CMIP6 solar data to have the same forcing in 2000 as CMIP5
cmip_soldata_rs = cmip_soldata - cmip_soldata[cmip_solyears==2000] + 1366.10544

#Load the CMIP5 data
f_in = open('solar_cmip5','r')
cmip5_soldata = []
cmip5_year= []
counter = 0
for line in f_in:
    if counter>=3 and line!='</solar>':
      cmip5_year.append(float(line[-8:-4]))
      cmip5_sol = line.split('"')[3]
      cmip5_soldata.append(float(cmip5_sol))
    counter = counter + 1
f_in.close()

cmip5_soldata = np.array(cmip5_soldata) + 1365.0

#Plot the timeseries

plt.plot(cmip_solyears,cmip_soldata,color='black',linewidth=3,label='CMIP6')
plt.plot(cmip_solyears,cmip_soldata_rs,color='red',linewidth=3,label='CMIP6-rescaled')
plt.plot(cmip5_year,cmip5_soldata,color='blue',linewidth=3,label='CMIP5')
plt.xlim(1980,2100)
ax = plt.gca()
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.ylabel(r'Solar constant (Wm$^{2}$)',fontsize=15)
plt.grid()
plt.legend(loc='best')
plt.savefig('../Figures/solarcomparison.png',dpi=300)
