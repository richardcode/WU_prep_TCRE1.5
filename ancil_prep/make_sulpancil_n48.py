import sys 
import os
import subprocess 

def make_n48_sulpancil():

  #List the sulphate files in the n96 directory 
  dir_n96 = '/network/aopp/ares/mad/millar/rcp26_ancils/n96/'
  dir_n48 = '/network/aopp/ares/mad/millar/rcp26_ancils/n48/'
  files = os.listdir(dir_n96)
  paths_n96 = []
  for f in files:
    if f[0] == 's':
      paths_n96.append(dir_n96 + f)

  #Create temporary mkancil namelist template for editing
  subprocess.call(['cp','working_DMSSO2NH3_conv_addNH3.namelist','temp_working_DMSSO2NH3_conv_addNH3.namelist'])
  #Loop over the paths, unzip and execute cdo commands and then rezip 
  for p in paths_n96: 
    unzip_file =  p.split('/')[-1][:-3]
    subprocess.call(['gunzip',p])

    #Convert to .nc with convsh
    os.system('$HOME/software/convsh1.93 $HOME/WU_prep_TCRE1.5/ancil_prep/conv2nc_1to1.tcl '+dir_n96+unzip_file)

    #Rezip the orginal file 
    subprocess.call(['gzip',dir_n96+unzip_file])

    #Regrid using cdo 
    unzip_file_nc = unzip_file + '.nc'
    name_n48 = unzip_file_nc.split('_')
    name_n48[2] = 'N48'
    name_n48 = '_'.join(name_n48)
    os.system('cdo remapcon,$HOME/WU_prep_TCRE1.5/ancil_prep/N48_grid '+unzip_file_nc+' '+dir_n48+name_n48)

    #Remove the N96 converted .nc 
    subprocess.call(['rm',unzip_file_nc])

    #Unzip and use NH3 ancil from .nc from other RCP2.6 series
    start_year = name_n48.split('_')[-2]
    end_year = name_n48.split('_')[-1][:-3]
    nc_name_nh3 = 'DMSSO2NH3_'+str(start_year)+str(end_year)+'_RCP26_monthly.nc'
    subprocess.call(['gunzip',dir_n48+nc_name_nh3+'.gz'])

    #Adapt mkancil template
    os.system("sed -i '/  NCFILES = /c"+r"\ "+" NCFILES = \""+dir_n48+name_n48+"\""+","+"\""+dir_n48+nc_name_nh3+"\""+r"' "+" temp_working_DMSSO2NH3_conv_addNH3.namelist")
    os.system("sed -i '/  GENANC_FILEOUT(1) = /c"+r"\ "+" GENANC_FILEOUT(1) = \""+dir_n48+'nh3'+name_n48[:-3]+"\""+r"' "+" temp_working_DMSSO2NH3_conv_addNH3.namelist")
    #Convert to ancil using xancil
    os.system('$HOME/software/mkancil0.56 < temp_working_DMSSO2NH3_conv_addNH3.namelist')

    #Zip up the outputs
    subprocess.call(['gzip',dir_n48+'nh3'+name_n48[:-3]])
    subprocess.call(['gzip',dir_n48+name_n48])
    subprocess.call(['gzip',dir_n48+nc_name_nh3])

  subprocess.call(['rm','temp_working_DMSSO2NH3_conv_addNH3.namelist'])

  return


     
    









