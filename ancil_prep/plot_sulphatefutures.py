import iris
import numpy as np
import iris.analysis.cartography
import iris.coord_categorisation
import matplotlib.pyplot as plt
import os

import iris.coords

files_in = ['/data/data/TCRE_data/n48_cmip6_hist/SO2DMS-em-anthro_input4MIPs_emissions_CMIP_CEDS-v2016-07-26-gr_200001-201412_n48.nc',
            '/network/aopp/ares/mad/millar/rcp26_ancils/n48/DMSSO2NH3_18502100_RCP26.nc']


global_cubes =[]
for f in files_in:

  if f == '/data/data/TCRE_data/n48_cmip6_hist/SO2DMS-em-anthro_input4MIPs_emissions_CMIP_CEDS-v2016-07-26-gr_200001-201412_n48.nc':
    os.system('ncatted -O -a calendar,time,m,c,"360_day" '+f)
  cube = iris.load_cube(f,'SULPHUR DIOXIDE EMISSIONS')
  if f == '/network/aopp/ares/mad/millar/rcp26_ancils/n48/DMSSO2NH3_18502100_RCP26.nc':
    new_lat_coords = iris.coords.DimCoord(np.arange(90.0,-92.5,step=-2.5),standard_name=u'latitude',units= coords[1].units, long_name=u'latitude', var_name='latitude')
    new_lon_coords = iris.coords.DimCoord(np.arange(0.0,356.25+3.75,step=3.75),standard_name=u'longitude',units= coords[2].units, long_name=u'longitude', var_name='longitude')
    cube.add_dim_coord(new_lat_coords,2)
    cube.add_dim_coord(new_lon_coords,3)
    cube = cube[:,0]
    cube.coords()[0].standard_name = u'time'
    cube.coords()[0].long_name = u'time'
    cube.coords()[0].var_name = 'time'
    

  coords = cube.coords()
  cube.coord('latitude').guess_bounds()
  cube.coord('longitude').guess_bounds()
  grid_areas = iris.analysis.cartography.area_weights(cube)
  mean_cube = cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=grid_areas)
  iris.coord_categorisation.add_year(mean_cube, 'time', name='year')
  annual_mean = mean_cube.aggregated_by(['year'],iris.analysis.MEAN)


  cube_h = iris.load_cube(f,'HIGH LEVEL  SO2 EMISSIONS KG/M2/S')
  if f == '/network/aopp/ares/mad/millar/rcp26_ancils/n48/DMSSO2NH3_18502100_RCP26.nc':
    new_lat_coords = iris.coords.DimCoord(np.arange(90.0,-92.5,step=-2.5),standard_name=u'latitude',units= coords[1].units, long_name=u'latitude', var_name='latitude')
    new_lon_coords = iris.coords.DimCoord(np.arange(0.0,356.25+3.75,step=3.75),standard_name=u'longitude',units= coords[2].units, long_name=u'longitude', var_name='longitude')
    cube_h.add_dim_coord(new_lat_coords,2)
    cube_h.add_dim_coord(new_lon_coords,3)
    cube_h = cube_h[:,0]
    cube_h.coords()[0].standard_name = u'time'
    cube_h.coords()[0].long_name = u'time'
    cube_h.coords()[0].var_name = 'time'
    

  coords = cube_h.coords()
  cube_h.coord('latitude').guess_bounds()
  cube_h.coord('longitude').guess_bounds()
  grid_areas = iris.analysis.cartography.area_weights(cube_h)
  mean_cube_h = cube_h.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=grid_areas)
  iris.coord_categorisation.add_year(mean_cube_h, 'time', name='year')
  annual_mean_h = mean_cube_h.aggregated_by(['year'],iris.analysis.MEAN)

  #Add the emissions from the high and low levels and convert to Tg/yr
  conv_fac  = 16073668268528.676 / (32.066 / 64.066)
  global_cubes.append(conv_fac*(annual_mean+annual_mean_h))



cols = ['black','blue']
names = ['CMIP6','RCP2.6']
for i in range(0,len(global_cubes)):
    plt.plot(global_cubes[i].coord('year').points,global_cubes[i].data,color=cols[i],label=names[i],linewidth=3) 

plt.legend()
plt.ylabel('SO$_{2}$ Emissions (TgSO$_{2}$/yr)',fontsize=15)
plt.xlim(1980,2070)

plt.grid()

plt.savefig('../Figures/sulphatefutures.png')



















