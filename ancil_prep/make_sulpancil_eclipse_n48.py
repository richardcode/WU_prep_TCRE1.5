import os
import sys
import subprocess

def regrid_split_ancil():

  dir_n96 = '/network/aopp/ares/mad/millar/eclipse_ancils/n96/'
  dir_n48 = '/network/aopp/ares/mad/millar/eclipse_ancils/n48/'
  dir_rcp_n48 = '/network/aopp/ares/mad/millar/rcp26_ancils/n48/'

  #Get the list of n96 .nc files
  files = [f for f in os.listdir(dir_n96) if '.nc' not in f]

  #Loop over the different types of .nc files
  for i in range(0,len(files)):
    
    #Unzip
    subprocess.call(['gunzip',dir_n96+files[i]])
    #Turn into .nc
    unzip_file = files[i][:-3]
    os.system('$HOME/software/convsh1.93 $HOME/WU_prep_TCRE1.5/ancil_prep/conv2nc_1to1.tcl '+dir_n96+unzip_file)
    #Regrid with cdo
    unzip_file_nc = files[i][:-3]+'.nc'
    name_n48 = unzip_file_nc[:-3]+'_n48.nc'
    os.system('cdo remapcon,$HOME/WU_prep_TCRE1.5/ancil_prep/N48_grid '+unzip_file_nc+' '+dir_n48+name_n48)
    #Rezip N96 version
    subprocess.call(['gzip',dir_n96+unzip_file])

    subprocess.call(['rm',unzip_file_nc])

    #Split the N48 file into 10 year chunks
    start_years = [1999,2009,2019,2029]
    end_years = [2010,2020,2030,2040]
    out_nc_names = []
    subprocess.call(['cp','working_DMSSO2NH3_conv_addNH3.namelist','temp_working_DMSSO2NH3_conv_addNH3.namelist'])
    for y in range(0,len(start_years)):
      start_year = start_years[y]
      end_year = end_years[y]
      num_start = str(12*( start_year-1990))
      num_end = str(12*(start_year-1990) + 12*(end_year-start_year+1) - 1)
      out_nc = name_n48.split('_')
      out_nc[3] = str(start_year)
      out_nc[4] = str(end_year)
      out_nc = '_'.join(out_nc)
      os.system('ncks -d t,'+num_start+','+num_end+' '+dir_n48+name_n48+' '+dir_n48+out_nc)
      out_nc_names.append(out_nc)

      #Unzip the RCP2.6 .nc to get the NH3 field
      nc_name_nh3 = 'DMSSO2NH3_'+str(start_year)+str(end_year)+'_RCP26_monthly.nc'
      subprocess.call(['gunzip',dir_rcp_n48+nc_name_nh3+'.gz'])

      #Adapt mkancil template
      os.system("sed -i '/  NCFILES = /c"+r"\ "+" NCFILES = \""+dir_n48+out_nc+"\""+","+"\""+dir_rcp_n48+nc_name_nh3+"\""+r"' "+" temp_working_DMSSO2NH3_conv_addNH3.namelist")
      os.system("sed -i '/  GENANC_FILEOUT(1) = /c"+r"\ "+" GENANC_FILEOUT(1) = \""+dir_n48+'nh3'+out_nc[:-3]+"\""+r"' "+" temp_working_DMSSO2NH3_conv_addNH3.namelist")
      #Convert to ancil using xancil
      os.system('$HOME/software/mkancil0.56 < temp_working_DMSSO2NH3_conv_addNH3.namelist')

      #Rezip everything
      subprocess.call(['gzip',dir_n48+'nh3'+out_nc[:-3]])
      subprocess.call(['gzip',dir_n48+out_nc])
      subprocess.call(['gzip',dir_rcp_n48+nc_name_nh3])

    subprocess.call(['rm','temp_working_DMSSO2NH3_conv_addNH3.namelist'])


  return 

  



















     


