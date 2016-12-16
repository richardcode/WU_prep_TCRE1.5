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

  #Loop over the paths, unzip and execute cdo commands and then rezip 
  for p in paths_n96: 
    unzip_file =  p.split('/')[-1][:-3]
    subprocess.call(['gunzip',p])

    #Convert to .nc with convsh

    #Regrid using cdo 

    #Convert to ancil using xancil 

    name_n48 = unzip_file.split('_')
    name_n48[2] = 'N48'
    name_n48 = '_'.join(name_n48)
    subprocess.call(['cdo remapcon,N48_grid',dir_n96+unzip_file,dir_n48+name_n48]) 
