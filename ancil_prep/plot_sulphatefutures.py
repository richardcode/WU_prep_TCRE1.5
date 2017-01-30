import iris
import numpy as np
import iris.analysis.cartography
import iris.coord_categorisation
import matplotlib.pyplot as plt

import iris.coords

dir_path = '/home/millar/Downloads/'
files_in = ['so2dms_ev5a_baseCLE_1990_2050.nc','so2dms_ev5a_climCLE_1990_2050.nc',
            'so2dms_ev5a_redMFR_1990_2050.nc','DMSSO2_18502100_RCP26.nc']

global_cubes =[]
for f in files_in:

  cube = iris.load_cube(dir_path + f,'SULPHUR DIOXIDE EMISSIONS')
  if f == 'DMSSO2_18502100_RCP26.nc':
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
  global_cubes.append(annual_mean)


cols = ['green','purple','brown','blue']
names = ['ECLIPSE Baseline','ECLIPSE Climate','ECLIPSE MFR','RCP2.6']
for i in range(0,len(global_cubes)):
  plt.plot(global_cubes[i].coord('year').points,global_cubes[i].data,color=cols[i],label=names[i],linewidth=3)

plt.legend()
plt.ylabel('SO$_{2}$ Emissions (kgm$^{-2}$s$^{-1}$)',fontsize=15)
plt.xlim(1980,2070)

plt.grid()

plt.show()



















