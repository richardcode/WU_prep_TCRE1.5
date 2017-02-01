import iris
import numpy as np
import iris.coord_categorisation

cube = iris.load_cube('solarforcing-ref-mon_input4MIPs_solar_CMIP_SOLARIS-HEPPA-3-2_gn_18500101-22991231.nc','solar_irradiance')
iris.coord_categorisation.add_year(cube, 'time', name='year')
ycube = cube.aggregated_by(['year'],iris.analysis.MEAN)

cmip_soldata = ycube.data - 1365.0
cmip_solyears = ycube.coord('year').points

#Scale down the CMIP6 solar data to have the same forcing in 2000 as z_series forcing
cmip_soldata = cmip_soldata - cmip_soldata[cmip_solyears==2000] + 1.0666

#Write to an xml
f_out = open('solar_cmip6_rescale_f','w')

f_out.write('<?xml version="1.0" encoding="utf-8"?>\n')
f_out.write('<!--CMIP6 solar forcing values. HadCM3 requies values relative to 1365, so they have been adjusted accordingly and data has been rescaled to match CMIP5 solar forcing in 2000. RJ Millar Jan 2017-->\n')
f_out.write('<solar>\n')

for i in range(0,len(cmip_solyears)):
  f_out.write('   <forcing name="solar_cmip6_rescale_v2" value="'+"{:.5e}".format(cmip_soldata[i])+'" year="' +str(int(cmip_solyears[i]))+ '"/>\n')

f_out.write('</solar>')
f_out.close()


