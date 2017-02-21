import iris
import iris.coord_categorisation
import numpy as np
import iris.analysis.cartography
import cf_units
from iris.coords import DimCoord

#data_dir = '~/Data/'
data_dir = '/data/data/TCRE_data/n48_cmip6_hist/'

def calc_perc_reducts():
    
  """
      Calculate the year on year proportional changes in RCP2.6
      sulphate emissions (high and surface) for monthly data
      from 2009 onwards
  """
  #Load RCP2.6 datq
  cubes = iris.load(data_dir+'DMSSO2NH3_18502100_RCP26_monthly.nc')
  #Get the surface and high level SO2 emissions
  surf_cube = cubes[3][:,0]
  high_cube = cubes[1][:,0]
  cubes = iris.cube.CubeList([surf_cube,high_cube])

  for i in range(0,len(cubes)):
    #Add the year and month to the cube and extract for 2009 onwards
    iris.coord_categorisation.add_year(cubes[i],'time',name='year')
    iris.coord_categorisation.add_month(cubes[i],'time',name='month')
    cubes[i] = cubes[i].extract(iris.Constraint(year = lambda y: y >=2009))

  #Make the year-on-year reduction rates
  yoy_rates = []
  for cube in cubes:
    #Calculate the global mean timeseries
    cube.coord('latitude').guess_bounds()
    cube.coord('longitude').guess_bounds()
    area_weights = iris.analysis.cartography.area_weights(cube)
    cube_mean = cube.collapsed(['latitude','longitude'],iris.analysis.MEAN,weights=area_weights)

    cube_rates = np.ones((cube_mean.shape))
    #Loop over the months and calculate the changes from the previous year
    #Calculate the year on year proportional changes in the global mean
    for i in range(12,cube_mean.shape[0]):
        cube_rates[i] = cube_mean[i].data / cube_mean[(i-12)].data

    yoy_rates.append(cube_rates)

  return yoy_rates

def apply_per_reducts_cmip6():

    
  """
     Apply the year-on-year monthly proportional reductions 
     from RCP2.6 to the end of the CMIP6 historical
  """

  #Load the CMIP6 historical
  cubes = iris.load(data_dir+'SO2DMS-em-anthro_input4MIPs_emissions_CMIP_CEDS-v2016-07-26-gr_200001-201412_n48.nc')
  #Get low and high level emissions just in the last year (2014)
  cubes = iris.cube.CubeList([cubes[2],cubes[1]])
  final_cubes = iris.cube.CubeList()
  for cube in cubes:
      final_cube = cube[-12:]
      final_cubes.append(final_cube)
  
  #Get the year-on-year proportional reductions in RCP2.6
  yoy_rates = calc_perc_reducts()
  yoy_rates = np.array(yoy_rates)

  #Create coordinates for new nc file between 2014 and 2100
  lat_coord = cubes[0].coord('latitude')
  lon_coord = cubes[0].coord('longitude')
  time_coord = DimCoord(np.arange(95055.,95055.+(2100-2014+1)*360.,30.),standard_name=u'time', units=cf_units.Unit('days since 1750-1-1 00:00:00', calendar='360_day'), long_name=u'time', var_name='time')

  #Create the cube date
  cube_data_surf = np.zeros((len(time_coord.points),cubes[0].shape[1],cubes[0].shape[2]))
  cube_data_high = np.zeros((len(time_coord.points),cubes[0].shape[1],cubes[0].shape[2]))
  #Set first year equal to 2014 in CMIP6 historical
  cube_data_surf[:12,...] = final_cubes[0].data
  cube_data_high[:12,...] = final_cubes[1].data
  #Apply year on year proportional reductions (globally uniform) from RCP2.6 in 2015 onwards
  for i in range(12,cube_data_surf.shape[0]):
    cube_data_surf[i,...] = cube_data_surf[(i-12),...] * yoy_rates[0,i]
    cube_data_high[i,...] = cube_data_high[(i-12),...] * yoy_rates[1,i]
  #Make the output cubes
  fut_cube_surf = iris.cube.Cube(cube_data_surf,dim_coords_and_dims=[(time_coord,0),(lat_coord, 1),(lon_coord, 2)],standard_name=final_cubes[0].standard_name, long_name=final_cubes[0].long_name, var_name=final_cubes[0].var_name, units=final_cubes[0].units, attributes=final_cubes[0].attributes)
  fut_cube_high = iris.cube.Cube(cube_data_high,dim_coords_and_dims=[(time_coord,0),(lat_coord, 1),(lon_coord, 2)],standard_name=final_cubes[1].standard_name, long_name=final_cubes[1].long_name, var_name=final_cubes[1].var_name, units=final_cubes[1].units, attributes=final_cubes[1].attributes)

  #Load the DMS cube from standard RCP2.6
  dms_cube = iris.load(data_dir+'DMSSO2NH3_18502100_RCP26_monthly.nc')[0]
  iris.coord_categorisation.add_year(dms_cube,'time',name='year')
  dms_cube = dms_cube.extract(iris.Constraint(year = lambda y: y>=2014))

  #Save the final cubes as netcdf
  iris.save(iris.cube.CubeList([dms_cube,fut_cube_high,fut_cube_surf]),data_dir+ "SO2DMS_rcp262015.nc")

  return

if __name__=='__main__':
  apply_per_reducts_cmip6()

















