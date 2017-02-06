import iris 
import numpy as np
import os
import iris.coord_categorisation
import cf_units as unit
import datetime
import subprocess

cmip6_data_dir = '/data/data/TCRE_data/orig_cmip6/'
cmip6_data_dir_regrid = '/data/data/TCRE_data/n48_cmip6_hist/'
ozone_nc = 'vmro3_input4MIPs_ozone_CMIP_UReading-CCMI-1-0_gr_200001-201412.nc'
ozone_moddate_nc = 'vmro3_input4MIPs_ozone_moddate_CMIP_UReading-CCMI-1-0_gr_200001-201412.nc'

subprocess.call(['cp',cmip6_data_dir+ozone_nc,cmip6_data_dir+ozone_moddate_nc]) 
os.system('ncatted -O -a units,time,o,c,"days since 1850-01-01 00:00" '+cmip6_data_dir+ozone_moddate_nc)

cube = iris.load_cube(cmip6_data_dir + ozone_moddate_nc)
cube.coord('time').bounds = None
cube.coord('time').points = 30*cube.coord('time').points 
iris.coord_categorisation.add_month(cube, 'time', name='month')

cube.rename('OZONE')
cube.long_name ='OZONE'
cube.var_name = '03'
cube.standard_name = 'mass_fraction_of_ozone_in_air' 
cube.units='kg kg-1'

cube.coord('longitude').var_name = 'longitude'
cube.coord('longitude').standard_name = 'longitude'
cube.coord('longitude').long_name = 'longitude'
cube.coord('longitude').units = 'degrees_east'
cube.coord('latitude').var_name = 'latitude'
cube.coord('latitude').standard_name = 'latitude'
cube.coord('latitude').long_name = 'latitude'
cube.coord('latitude').units = 'degrees_north'
cube.coord('air_pressure').var_name = 'hybrid_p_x1000'
cube.coord('air_pressure').long_name = 'Hybrid pressure multiplied by 1000'
cube.coord('air_pressure').standard_name = 'atmosphere_hybrid_sigma_pressure_coordinate'
#cube.coord('atmosphere_hybrid_sigma_pressure_coordinate').units = 'level'
cube.coord('time').var_name = 't'

#Do the regridding in the vertical
v_grid_points = [996.998906,974.955916,930.416763,869.832277,792.228485,699.574389,599.503256,
 504.521860,422.103124,354.697737,299.751623,249.701774,199.626818,149.501249,
 99.246776,56.854244,29.594331,14.797166,4.605880]
v_samp = [('atmosphere_hybrid_sigma_pressure_coordinate',v_grid_points)]
mcube = iris.analysis.interpolate.linear(cube, v_samp, extrapolation_mode='linear')

#Convert to O3 mass mixing ration using molecular weight of air (dry) = 0.029kg/mol
#mcube = 0.048 / 0.029 * mcube

#Zonally mean the cubes 
grid_areas = iris.analysis.cartography.area_weights(mcube)
mcube = mcube.collapsed(['longitude'],iris.analysis.MEAN,weights=grid_areas) 

out_nc_vregrid = 'vmro3_input4MIPs_ozone_moddatevgrid_CMIP_UReading-CCMI-1-0_gr_200001-201412.nc'

#Save the cube and do the regridding
mcube.rename('O3')
mcube.long_name ='O3'
mcube.var_name = '03'
#mcube.standard_name = 'mass_fraction_of_ozone_in_air' 
#mcube.units='kg kg-1'

#Do linear interpolation in latitude
lat_samp = [('latitude',np.arange(-90.0,92.5,step=2.5))]
mcube = iris.analysis.interpolate.linear(mcube, lat_samp, extrapolation_mode='linear')


out_nc_regrid = out_nc_vregrid[:-3]+'_n48.nc'
iris.fileformats.netcdf.save(mcube,filename=cmip6_data_dir_regrid+out_nc_regrid,netcdf_format='NETCDF4')



#os.system('cdo remapcon,$HOME/WU_prep_TCRE1.5/ancil_prep/N48_grid '+cmip6_data_dir+out_nc_vregrid+' '+cmip6_data_dir_regrid+out_nc_regrid)
os.system('ncatted -O -a calendar,t,m,c,"360-day" '+cmip6_data_dir_regrid+out_nc_regrid)

#Include final name that is short enough for CPDN filename restrictions
final_anc = 'ozone_cmip6hist_2000_2014'



#Adapt mkancil template
subprocess.call(['cp','working_ozone_conv_cmip6.namelist','temp_working_ozone_conv_cmip6.namelist'])
os.system("sed -i '/  NCFILES = /c"+r"\ "+" NCFILES = \""+cmip6_data_dir_regrid+out_nc_regrid+"\""+r"' "+" temp_working_ozone_conv_cmip6.namelist")
os.system("sed -i '/  OZONE_FILEIN = /c"+r"\ "+" OZONE_FILEIN = \""+cmip6_data_dir_regrid+out_nc_regrid+"\""+r"' "+" temp_working_ozone_conv_cmip6.namelist")
os.system("sed -i '/  OZONE_FILEOUT = /c"+r"\ "+" OZONE_FILEOUT = \""+cmip6_data_dir_regrid+final_anc+"\""+r"' "+" temp_working_ozone_conv_cmip6.namelist")
#Convert to ancil using xancil
os.system('$HOME/software/mkancil0.56 < temp_working_ozone_conv_cmip6.namelist')

subprocess.call(['gzip',cmip6_data_dir_regrid+final_anc])
subprocess.call(['rm','temp_working_ozone_conv_cmip6.namelist'])




