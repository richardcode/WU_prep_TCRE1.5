import numpy as np
import sys
import os 
import subprocess
import zipfile
import os.path
from scipy.io import netcdf

def proc_oldtrickle_list():

  #Correct the old file to have the correct server location
  old_file = 'Data/z_trickles_list.txt'
  f_in = open(old_file,'r')
  f_out = open('Data/z_trickles_list_corserv.txt','w')
  for line in f_in:
    f_line = line[-50:-1]
    f_out.write('http://upload2.cpdn.org/results/hadcm3n/trickle/'+f_line+'\n')

  f_out.close()
  f_in.close()

  return

def collect_trickle_umidsyears():

  in_file = 'Data/z_trickles_list_corserv.txt'
  f_in = open(in_file,'r')

  coll_data = []

  for line in f_in:
    #Make list of umid, year and url
    coll_data.append([line[-34:-30],line[-9:-5],line[:-1]])

  f_in.close()

  coll_d = np.array(coll_data)
  uni_umids = list(set(coll_d[:,0]))

  full_years = range(1881,2001)
  a_data = []
  full_umids=[]
  for umid in uni_umids:

   umid_years = (coll_d[coll_d[:,0]==umid,1]).tolist()
   log_years = [i in [int(y) for y in umid_years] for i in full_years]
   if np.sum(log_years) == len(full_years):
     full_umids.append(umid)

   a_data.append([umid,umid_years])

  #Make a list of urls from the full umids
  wanted_urls = []
  full_years_s = [str(f) for f in full_years]
  for umid in full_umids:
    umid_data = coll_d[coll_d[:,0]==umid]
    for year in full_years_s:
      targ_url = umid_data[umid_data[:,1] == year,2][0]
      wanted_urls.append(targ_url)

  #Print the wanted urls to a file
  f_out = open('Data/z_trickles_list_complete.txt','w')
  for i in wanted_urls:
    f_out.write(i+'\n')
  f_out.close()

  return

def download_trickles():

  #Download and store the wanted streams of the trickles
  wanted_dls_f = 'Data/z_trickles_list_complete.txt'
  f_in = open(wanted_dls_f,'r')
  wanted_dls = (f_in.read().split('\n'))[:-1]


  working_dir = '/data/trickles/tcre1p5_trickles/working/'
  output_dir = '/data/trickles/tcre1p5_trickles/z_trickles/'

  #Load the ones that have already been pulled down. 
  files_exist = [ [f[:4],f[5:9],f[-5:-3]] for f in os.listdir(output_dir+'pd/') ] 
  

  #Loop over the download urls in both lists
  for i in range(0,len(wanted_dls)):
    #Check to see if it has already been downloaded
    if ( (['z'+wanted_dls[i][-32:-29],wanted_dls[i][-8:-4],'pd'] not in files_exist) ):
      print(wanted_dls[i]) 
      #Clean up the working directory
      #subprocess.call('rm '+working_dir+'*', shell=True)
      try: 
        #Wget both the zip directories 
        subprocess.call('wget -nc -T 30 --tries=1 -P '+working_dir+' '+wanted_dls[i],shell=True)
  
        #Check the pd files are there in both directories
        streams = ['pd.nc','pg.nc','pj.nc']
        delta_zipn = working_dir+wanted_dls[i][-49:]
        delta_arch = zipfile.ZipFile(delta_zipn,'r')
    
        for stream in streams:
          try:
            nc_name_delta = [s for s in delta_arch.namelist() if stream in s][0]
            if nc_name_delta: 
              delta_arch.extract(nc_name_delta, path = working_dir)


              os.system('mv '+working_dir+nc_name_delta+' '+output_dir+stream[:2]+'/'+'z'+nc_name_delta[9:13] + nc_name_delta[-10:])
              #os.system('rm '+working_dir+nc_name_delta)

          except:
            pass 


        os.system('rm '+delta_zipn) 

      
    
      except:
        pass 

  return

def nc_data_totext(nc_file,f_out): 

  #Get the decadal means for the nc_file
  f_nc = netcdf.netcdf_file(nc_file,'r')

  umid = 'x'+nc_file[-14:-11]
  year = nc_file[-10:-6]

  f_out.write(umid+'\t'+year+'\t')

  field_keys = [f for f in f_nc.variables.keys() if f[:3]=='gm_']

  for key in field_keys:
    data = np.mean(f_nc.variables[key].data)
    f_out.write(str(data)+'\t')

  regional_keys = [f for f in f_nc.variables.keys() if f[:6]=='rm_n34']
  for key in regional_keys:
    data = np.mean(f_nc.variables[key].data)
    f_out.write(str(data)+'\t')

  f_out.write('\n')

  return 

def list_trickles(stream): 

  diffs_dir = '/data/trickles/tcre1p5_trickles/z_trickles/'+stream+'/'

  diffs_paths = []
  diffs_umids = []
  diffs_years = []
  for i in os.listdir(diffs_dir): 
    diffs_paths.append(diffs_dir + i)
    diffs_umids.append(i[-14:-11])
    diffs_years.append(i[-10:-6]) 

  return diffs_paths, diffs_umids, diffs_years 

def analy_trickles(stream): 

  #Load the trickles 
  diffs_paths, diffs_umids, diffs_years = list_trickles(stream)

  f_out_file = 'Data/z_trickles_'+stream+'.txt'
  #f_out_file = '/network/aopp/ares/mad/millar/latest_averages/trickle_data/z_trickles_'+stream+'.txt'


  if os.path.isfile(f_out_file):
    #Find the trickles that have been analysed already
    f_in = open(f_out_file,'r')
    comp_umids = []
    for line in f_in: 
      comp_umids.append([line[:4],line[5:9]])
    f_in.close()
  
    f_out = open(f_out_file,'a')
  
  else:
    f_out = open(f_out_file,'w')
    comp_umids = []

  for ncf in diffs_paths: 
    if [ncf[-15:-11],ncf[-10:-6]] not in comp_umids: 
      #Call module that opens the netcdf and extracts the numbers from it
      print(ncf)
      try:
        nc_data_totext(ncf,f_out)
      except:
        pass

  f_out.close()

  return 


if __name__ == '__main__':

  analy_trickles('pd')
  analy_trickles('pg')
  analy_trickles('pj')


