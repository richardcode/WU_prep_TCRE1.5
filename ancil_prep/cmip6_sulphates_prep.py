import iris 
import numpy as np
import os
import iris.coord_categorisation
import cf_units as unit
import datetime
import subprocess

cmip6_data_dir = '/data/data/TCRE_data/orig_cmip6/'
cmip6_data_dir_regrid = '/data/data/TCRE_data/n48_cmip6_hist/'

os.system('ncatted -O -a calendar,time,m,c,"365_day" '+cmip6_data_dir+'SO2-em-anthro_input4MIPs_emissions_CMIP_CEDS-v2016-07-26-sectorDim_gr_200001-201412.nc')
cube = iris.load_cube(cmip6_data_dir+'SO2-em-anthro_input4MIPs_emissions_CMIP_CEDS-v2016-07-26-sectorDim_gr_200001-201412.nc')
cube.coord('time').bounds = None
first_time = unit.num2date(cube.coord('time').points[0],cube.coord('time').units.origin,cube.coord('time').units.calendar)
first_time_alt = unit.date2num(first_time,cube.coord('time').units.origin,'360_day')
cube.coord('time').points = np.arange(first_time_alt,first_time_alt + 30*len(cube.coord('time').points),step=30.)


cube.coord('longitude').var_name = 'longitude'
cube.coord('longitude').units = 'degrees_east'
cube.coord('latitude').var_name = 'latitude'
cube.coord('latitude').units = 'degrees_north'

#Add conversion factor into kg/m2/s of S as opposed to SO2
cube = 32.066 / 64.066 * cube
#Alternative conversion factor: 1TgSO2/yr = 16073668268528.676 kgm-2s-1 of SO2

#Half industry and all of energy go into high level SO2 emissions (Met Office convention)
surf_weights = np.array([1.0,0.0,0.5,1.0,1.0,1.0,1.0,1.0])
high_weights = np.array([0.0,1.0,0.5,0.0,0.0,0.0,0.0,0.0])

surf_cube = cube.collapsed('sector',iris.analysis.SUM,weights=np.ones(cube.shape)*surf_weights[np.newaxis,:,np.newaxis,np.newaxis])
high_cube = cube.collapsed('sector',iris.analysis.SUM,weights=np.ones(cube.shape)*high_weights[np.newaxis,:,np.newaxis,np.newaxis])

high_cube.rename('HIGH LEVEL  SO2 EMISSIONS KG/M2/S')
high_cube.long_name ='HIGH LEVEL  SO2 EMISSIONS KG/M2/S'
high_cube.var_name = 'field569_1'
high_cube.units='kg/m2/s'


surf_cube.rename('SULPHUR DIOXIDE EMISSIONS')
surf_cube.long_name ='SULPHUR DIOXIDE EMISSIONS'
surf_cube.var_name = 'field569'
surf_cube.units='kg/m2/s'

#Load the DMS fields
dms_nc = 'NMVOC-C2H6S-em-biomassburning_input4MIPs_emissions_CMIP_VUA-CMIP-BB4CMIP6-1-2_gn_185001-201512.nc'
os.system('ncatted -O -a calendar,time,m,c,"365_day" '+cmip6_data_dir+dms_nc)
dms_cube = iris.load_cube(cmip6_data_dir+dms_nc)
iris.coord_categorisation.add_year(dms_cube, 'time', name='year')
time_constraint = iris.Constraint(year=lambda y: 2000.0<=y<2015.0)
dms_cube = dms_cube.extract(time_constraint) 

dms_cube.coord('time').bounds = None
dms_cube.coord('time').convert_units(cube.coord('time').units)
dms_cube.coord('time').points = np.arange(first_time_alt,first_time_alt + 30*len(cube.coord('time').points),step=30.)
dms_cube.coord('time').attributes = {'realtopology': 'linear'}
dms_cube.coord('longitude').attributes = cube.coord('longitude').attributes
dms_cube.coord('latitude').attributes = cube.coord('latitude').attributes


dms_cube.coord('longitude').var_name = 'longitude'
dms_cube.coord('longitude').units = 'degrees_east'
dms_cube.coord('latitude').var_name = 'latitude'
dms_cube.coord('latitude').units = 'degrees_north'
dms_cube.rename('DIMETHYL SULPHIDE EMISSIONS (ANCIL)')
dms_cube.long_name ='DIMETHYL SULPHIDE EMISSIONS (ANCIL)'
dms_cube.var_name = 'field570'
dms_cube.units='kg/m2/s'
del dms_cube.attributes['title']



cubes = iris.cube.CubeList([dms_cube,surf_cube,high_cube]) 
out_nc_raw = 'SO2DMS-em-anthro_input4MIPs_emissions_CMIP_CEDS-v2016-07-26-gr_200001-201412.nc'

out_nc_raw_names = ['DMS-em-anthro_input4MIPs_emissions_CMIP_CEDS-v2016-07-26-gr_200001-201412.nc','SO2surf-em-anthro_input4MIPs_emissions_CMIP_CEDS-v2016-07-26-gr_200001-201412.nc','SO2high-em-anthro_input4MIPs_emissions_CMIP_CEDS-v2016-07-26-gr_200001-201412.nc']
out_nc_regrid = out_nc_raw[:-3]+'_n48.nc'
for i in range(0,len(out_nc_raw_names)):
  iris.fileformats.netcdf.save(cubes[i],filename=cmip6_data_dir+out_nc_raw_names[i],netcdf_format='NETCDF4')
  os.system('$HOME/.local/cdo/bin/cdo remapcon,$HOME/WU_prep_TCRE1.5/ancil_prep/N48_grid '+cmip6_data_dir+out_nc_raw_names[i]+' '+cmip6_data_dir_regrid+out_nc_raw_names[i][:-3]+'_n48.nc')

#Can't find any CMIP6 specification for ocean DMS (only biomass burning), maybe because
#this is generated interactively by ocean biochemistry?
#sub in RCP2.6 DMS emissions in here instead  
os.system('cp '+cmip6_data_dir_regrid+'DMS_rcp26_20002014.nc ' +cmip6_data_dir_regrid + out_nc_regrid)
os.system('ncrename -d t,time -v t,time ' +cmip6_data_dir_regrid + out_nc_regrid)
os.system('ncks -A '+cmip6_data_dir_regrid+out_nc_raw_names[1][:-3]+'_n48.nc '+cmip6_data_dir_regrid+out_nc_regrid)
os.system('ncks -A '+cmip6_data_dir_regrid+out_nc_raw_names[2][:-3]+'_n48.nc '+cmip6_data_dir_regrid+out_nc_regrid)

os.system('ncatted -O -a calendar,time,m,c,"360-day" '+cmip6_data_dir_regrid+out_nc_regrid)

#Adapt mkancil template
subprocess.call(['cp','working_so2dms_conv.namelist','temp_working_so2dms_conv.namelist'])
os.system("sed -i '/  NCFILES = /c"+r"\ "+" NCFILES = \""+cmip6_data_dir_regrid+out_nc_regrid+"\""+r"' "+" temp_working_so2dms_conv.namelist")
os.system("sed -i '/  GENANC_FILEOUT(1) = /c"+r"\ "+" GENANC_FILEOUT(1) = \""+cmip6_data_dir_regrid+out_nc_regrid[:-3]+"\""+r"' "+" temp_working_so2dms_conv.namelist")#Convert to ancil using xancil
os.system('$HOME/software/mkancil0.56 < temp_working_so2dms_conv.namelist')

subprocess.call(['gzip',cmip6_data_dir_regrid+out_nc_regrid[:-3]])
subprocess.call(['rm','temp_working_so2dms_conv.namelist'])




