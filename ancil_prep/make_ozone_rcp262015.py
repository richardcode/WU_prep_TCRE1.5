import iris
import iris.coord_categorisation
import numpy as np
import iris.analysis.cartography
import cf_units
from iris.coords import DimCoord
import os
import subprocess

#data_dir = '~/Data/'
data_dir = '/data/data/TCRE_data/n48_cmip6_hist/'

def make_single_ozone():
    
    ozone_dir = '/network/aopp/ares/mad/millar/rcp26_ancils/n48/'
    ozone_files = [ozone_dir + f for f in os.listdir(ozone_dir) if f[-8:] == 'v2.nc.gz']

    for i in ozone_files:
      os.system('gunzip '+i)

    ozone_files_c = [f[:-3] for f in ozone_files]
    ozone_files_c = sorted(ozone_files_c, key=lambda item: (int(item.partition(' ')[0]) if item[0].isdigit() else float('inf'), item))
    os.system('ncrcat '+' '.join(ozone_files_c)+' '+data_dir+'ozone_rcp26_N48_1999_2110v2.nc')

    for i in ozone_files_c:
      os.system('gzip '+i)

    return

def calc_perc_reducts():
    
    """
        Calculate the year on year proportional changes in RCP2.6
        ozone concentrations (at all levels) for monthly data
        from 2009 onwards
    """
    rcp26_ozone_f = 'ozone_rcp26_N48_1999_2110v2.nc'
    cube = iris.load(data_dir+rcp26_ozone_f)[0]
    
    iris.coord_categorisation.add_year(cube,'t',name='year')
    iris.coord_categorisation.add_month(cube,'t',name='month')
    cube = cube.extract(iris.Constraint(year = lambda y: y >=2009))

    cube_rates = np.ones((cube.shape))
    #Loop over the months and calculate the changes from the previous year
    #Calculate the year on year proportional changes in the global mean
    for i in range(12,cube.shape[0]):
        cube_rates[i] = cube[i].data / cube[(i-12)].data


    return cube_rates

def apply_per_reducts_cmip6():

    
  """
     Apply the year-on-year monthly proportional reductions 
     from RCP2.6 to the end of the CMIP6 historical
  """

  #Load the CMIP6 historical
  cube = iris.load(data_dir+'vmro3_input4MIPs_ozone_moddatevgrid_CMIP_UReading-CCMI-1-0_gr_200001-201412_n48.nc')[0]
  final_cube = cube[-12:]

  #Get the year-on-year proportional reductions in RCP2.6
  yoy_rates = calc_perc_reducts()

  lat_coord = cube.coord('latitude')
  lon_coord = cube.coord('longitude')
  vert_coord = cube.coord('atmosphere_hybrid_sigma_pressure_coordinate')
  time_coord = DimCoord(np.arange(95055.,95055.+(2100-2014+1)*360.,30.),standard_name=u'time', units=cf_units.Unit('days since 1750-1-1 00:00:00', calendar='360_day'), long_name=u'time', var_name='time')

  #Create the cube data
  cube_data = np.zeros((len(time_coord.points),cube.shape[1],cube.shape[2]))
  cube_data[:12,...] = final_cube.data
  for i in range(12,cube_data.shape[0]):
    cube_data[i,...] = cube_data[(i-12),...] * yoy_rates[i,...,0]

  fut_cube = iris.cube.Cube(cube_data,dim_coords_and_dims=[(time_coord,0),(vert_coord,1),(lat_coord, 2)],standard_name=final_cube.standard_name, long_name=final_cube.long_name, var_name=final_cube.var_name, units=final_cube.units, attributes=final_cube.attributes)
  fut_cube.coord('time').var_name = 't'

  #Save the final cubes as netcdf
  iris.save(fut_cube,data_dir+ "ozone_rcp262015.nc")

  return

def make_ancil():

  cmip6_data_dir = '/data/data/TCRE_data/n48_cmip6_hist/'
  ozone_nc = 'ozone_rcp262015.nc'
  final_anc = 'ozone_rcp262015'


  first_year = np.array([2014,2024,2034,2044,2054,2064,2074,2084])
  last_year = np.array([2025,2035,2045,2055,2065,2075,2085,2095])
  first_time = 95055.0 + (first_year - 2014.0)*12*30
  last_time =  95055.0 + (last_year - 2014.0)*12*30 + 11*30
  

  #Cut to make the 10-year segments for distribution
  for i in range(0,len(first_year)):
    cut_nc_name = 'ozone_rcp262015_'+str(first_year[i])+'_'+str(last_year[i])+'.nc'
    cut_anc_name = 'ozone_rcp262015_'+str(first_year[i])+'_'+str(last_year[i])
    os.system('ncks -d t,'+str(first_time[i])+','+str(last_time[i])+' '+cmip6_data_dir+'ozone_rcp262015.nc'+' '+cmip6_data_dir+cut_nc_name)


    #Adapt mkancil template
    subprocess.call(['cp','working_ozone_conv_cmip6.namelist','temp_working_ozone_conv_cmip6.namelist'])
    os.system("sed -i '/  NCFILES = /c"+r"\ "+" NCFILES = \""+cmip6_data_dir+cut_nc_name+"\""+r"' "+" temp_working_ozone_conv_cmip6.namelist")
    os.system("sed -i '/  OZONE_FILEIN = /c"+r"\ "+" OZONE_FILEIN = \""+cmip6_data_dir+cut_nc_name+"\""+r"' "+" temp_working_ozone_conv_cmip6.namelist")
    os.system("sed -i '/  OZONE_FILEOUT = /c"+r"\ "+" OZONE_FILEOUT = \""+cmip6_data_dir+cut_anc_name+"\""+r"' "+" temp_working_ozone_conv_cmip6.namelist")
    #Convert to ancil using xancil
    os.system('$HOME/software/mkancil0.56 < temp_working_ozone_conv_cmip6.namelist')

    subprocess.call(['gzip',cmip6_data_dir+cut_anc_name])
    subprocess.call(['rm','temp_working_ozone_conv_cmip6.namelist'])

  return


if __name__=='__main__':
  apply_per_reducts_cmip6()





















