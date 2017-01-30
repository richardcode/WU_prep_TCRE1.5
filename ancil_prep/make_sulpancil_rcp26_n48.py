import os
import sys
import subprocess

def interp_split_ancil(): 

  ancil_dir = '/network/aopp/ares/mad/millar/rcp26_ancils/n48/'
  orig_ancil = 'DMSSO2NH3_18502100_RCP26.anc'

  #Convert original ancil to netcdf 
  os.system('$HOME/software/convsh1.93 $HOME/WU_prep_TCRE1.5/ancil_prep/conv2nc_1to1.tcl '+ancil_dir+orig_ancil)

  #Move the file to the destination dir
  subprocess.call(['mv',orig_ancil[:-4]+'.nc',ancil_dir+orig_ancil[:-4]+'.nc'])
  nc_name = orig_ancil[:-4]+'.nc'

  #Linearly interpolate to monthly data 
  mon_nc_name = nc_name[:-3]+'_monthly.nc'
  os.system('cdo inttime,1850-01-16,00:00:00,1month '+ancil_dir+nc_name+' '+ancil_dir+mon_nc_name)

  #Convert overall file to ancil 
  os.system('$HOME/software/mkancil0.56 < working_DMSSO2NH3_conv.namelist')

  #Split the .nc file into 10 year chunks post 2000
  #Need to run from e.g 1999-01-16,00:00:00 to 2010-12-16,00:00:00
  start_years = [1999,2009,2019,2029,2039,2049,2059,2069,2079]
  end_years = [2010,2020,2030,2040,2050,2060,2070,2080,2090]
  out_nc_names = []
  for i in range(0,len(start_years)):
    start_year = start_years[i]
    end_year = end_years[i]
    num_start = str(12*(start_year-1850))
    num_end = str(12*(start_year-1850) + 12*(end_year-start_year+1) - 1)
    out_nc = mon_nc_name.split('_')
    out_nc[1] = str(start_year)+str(end_year)
    out_nc = '_'.join(out_nc)
    os.system('ncks -d t,'+num_start+','+num_end+' '+ancil_dir+mon_nc_name+' '+ancil_dir+out_nc)
    out_nc_names.append(out_nc)

  #Convert the nc files into ancils (copy mkancil namelist and edit to change filenames)
  subprocess.call(['cp','working_DMSSO2NH3_conv.namelist','temp_working_DMSSO2NH3_conv.namelist'])
  for i in range(0,len(out_nc_names)):
    os.system("sed -i '/  NCFILES = /c"+r"\ "+" NCFILES = \""+ancil_dir+out_nc_names[i]+"\""+r"' "+" temp_working_DMSSO2NH3_conv.namelist")
    os.system("sed -i '/  GENANC_FILEOUT(1) = /c"+r"\ "+" GENANC_FILEOUT(1) = \""+ancil_dir+out_nc_names[i][:-3]+"\""+r"' "+" temp_working_DMSSO2NH3_conv.namelist")

    os.system('$HOME/software/mkancil0.56 < temp_working_DMSSO2NH3_conv.namelist')
    

    #Gzip the ancils and .ncs
    subprocess.call(['gzip',ancil_dir+out_nc_names[i][:-3]])
    subprocess.call(['gzip',ancil_dir+out_nc_names[i]])

  subprocess.call(['rm','temp_working_DMSSO2NH3_conv.namelist'])

  return



  

  

