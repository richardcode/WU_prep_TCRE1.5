from xml.etree.ElementTree import *
import numpy as np
import sys
import os
import subprocess

def read_paramtable():

  param_file = '../Data/y_series_params_total.dat'

  dt = np.dtype({'names':['umid', 'vf1', 'ct', 'cw_land', 'cw_sea', 'rhcrit01', 'rhcrit02', 'rhcrit03', 'rhcrit04', 'rhcrit05', 'rhcrit06', 'rhcrit07', 'rhcrit08', 'rhcrit09', 'rhcrit10', 'rhcrit11', 'rhcrit12', 'rhcrit13', 'rhcrit14', 'rhcrit15', 'rhcrit16', 'rhcrit17', 'rhcrit18', 'rhcrit19', 'eacf01', 'eacf02', 'eacf03', 'eacf04', 'eacf05', 'eacf06', 'eacf07', 'eacf08', 'eacf09', 'eacf10', 'eacf11', 'eacf12', 'eacf13', 'eacf14', 'eacf15', 'eacf16', 'eacf17', 'eacf18', 'eacf19', 'entcoef', 'alpham', 'dtice', 'ice_size', 'isopyc', 'vertvisc', 'vdiffsurf', 'vdiffdepth', 'mllam', 'mldel', 'l0', 'l1', 'so2_high_level', 'volsca', 'anthsca', 'start_level_gwdrag', 'kay_gwave', 'kay_lee_gwave', 'asym_lambda', 'charnock', 'z0fsea', 'g0', 'r_layers01', 'r_layers02', 'r_layers03', 'r_layers04', 'DIFF_COEFF01', 'DIFF_COEFF02', 'DIFF_COEFF03', 'DIFF_COEFF04', 'DIFF_COEFF05', 'DIFF_COEFF06', 'DIFF_COEFF07', 'DIFF_COEFF08', 'DIFF_COEFF09', 'DIFF_COEFF10', 'DIFF_COEFF11', 'DIFF_COEFF12', 'DIFF_COEFF13', 'DIFF_COEFF14', 'DIFF_COEFF15', 'DIFF_COEFF16', 'DIFF_COEFF17', 'DIFF_COEFF18', 'DIFF_COEFF19', 'DIFF_COEFF_Q01', 'DIFF_COEFF_Q02', 'DIFF_COEFF_Q03', 'DIFF_COEFF_Q04', 'DIFF_COEFF_Q05', 'DIFF_COEFF_Q06', 'DIFF_COEFF_Q07', 'DIFF_COEFF_Q08', 'DIFF_COEFF_Q09', 'DIFF_COEFF_Q10', 'DIFF_COEFF_Q11', 'DIFF_COEFF_Q12', 'DIFF_COEFF_Q13', 'DIFF_COEFF_Q14', 'DIFF_COEFF_Q15', 'DIFF_COEFF_Q16', 'DIFF_COEFF_Q17', 'DIFF_COEFF_Q18', 'DIFF_COEFF_Q19', 'DIFF_EXP01', 'DIFF_EXP02', 'DIFF_EXP03', 'DIFF_EXP04', 'DIFF_EXP05', 'DIFF_EXP06', 'DIFF_EXP07', 'DIFF_EXP08', 'DIFF_EXP09', 'DIFF_EXP10', 'DIFF_EXP11', 'DIFF_EXP12', 'DIFF_EXP13', 'DIFF_EXP14', 'DIFF_EXP15', 'DIFF_EXP16', 'DIFF_EXP17', 'DIFF_EXP18', 'DIFF_EXP19', 'DIFF_EXP_Q01', 'DIFF_EXP_Q01.1', 'DIFF_EXP_Q03', 'DIFF_EXP_Q04', 'DIFF_EXP_Q05', 'DIFF_EXP_Q06', 'DIFF_EXP_Q07', 'DIFF_EXP_Q08', 'DIFF_EXP_Q09', 'DIFF_EXP_Q10', 'DIFF_EXP_Q11', 'DIFF_EXP_Q12', 'DIFF_EXP_Q13', 'DIFF_EXP_Q14', 'DIFF_EXP_Q15', 'DIFF_EXP_Q16', 'DIFF_EXP_Q17', 'DIFF_EXP_Q18', 'DIFF_EXP_Q19'], 'formats':['S4']+144*[np.float] } )

  param_data = np.loadtxt(param_file, skiprows=1, dtype= dt, delimiter=',')

  return param_data

def anc(old):
  """ This is a function that updates the alphanumeric umid value """
  
  #Convert alphanumeric string into numeric string
  charlist=list(old)
  i=len(charlist)-1
  num=[]
  for c in charlist:
    num.append(ord(c))
    
  while i>0:
    #If character has value '9', set next value to 'a'
    if num[i]==57:
      num[i]=97
      i=0
    #If character has value 'z', set next value to '0' and transition to the next column
    elif num[i]==122:
      num[i]=48
      i=i-1
    #Else add one to the value  
    else:
      num[i]=num[i]+1
      i=0

  #Convert back into a alphanumeric string
  new=[]  
  for n in num:
    new.append(chr(n))
  out=''.join(new)

  return out

def xmlgen():
  """ Generation of xml for TCRE experiment CMIP6 forced update between 2000 and 2014"""

  #Start year of the model integrations 
  model_start_year=2000

  #File containing XML template
  templatefile='./headers/main_site_header_hadcm3.xml'
  #Output XML filename
  outxmlfile='./hadcm3s_tcre_cmip6hist20002014_v2.xml'
  

  #Read the parameter lookup table 
  param_dataset = read_paramtable()

  #Values for the initial conditions perturbation 
  theta_list = [0.0,0.91172, 0.81401, 0.57357, 0.10328 , 0.66696, 0.88091, 0.42442, 0.20873, 0.16564, 0.29675]
  num_ic = 4
  theta_list = theta_list[:num_ic]
  #MAIN CODE

  #Create the element tree for the xml to be output
  outtreeroot=Element('WorkGen')
  outtree=ElementTree(outtreeroot)
  
  
  #Read-in elemenet tree of the template file
  temptree=parse(templatefile)
  temproot=temptree.getroot()

  #Append the template tree structure to the root of the output tree
  for child in temproot:
    outtreeroot.append(child) 

  #Load in the umids of the restart files
  f_restart_umids = open('../Data/z_restart_umids.txt','r')
  old_umids = [line[:-1] for line in f_restart_umids]

  #Set xml tags that are the same for all workunits
  file_sulphox='sulpc_oxidants_19_A2_1990'
  file_ozone='ozone_cmip6hist_2000_2014_n48'
  file_solar='solar_cmip6_rescale_f'
  file_so2dms='SO2DMS_cmip6hist_2000_2014_n48_f'
  file_ghg='ghg_cmip6_hist_19992015_f'
  file_flux = 'waterfix.ancil.be.32'
  file_spec_sw = 'spec3a_sw_3_asol2c_hadcm3'
  file_spec_lw = 'spec3a_lw_3_asol2c_hadcm3'
  file_volc = 'NAT_VOLC'
  file_volcanic = 'sato_hist73lat_volc_20002015'
  run_years='14'
  file_stash = 'xabnk.stashc.monthly_TCRE_full'

  #Starting umid
  umid='7000'


  count  =0

  outtreeroot.find('batch_name').text = 'HadCM3S TCRE historical integration'
  outtreeroot.find('batch_owner').text = 'Richard Millar &lt;richard.millar@physics.ox.ac.uk&gt;, Sarah Sparrow &lt;sarah.sparrow@oerc.ox.ac.uk&gt;'
  outtreeroot.find('batch_first_start_year').text = str(model_start_year)
  outtreeroot.find('batch_last_start_year').text = str(model_start_year)
  outtreeroot.find('batch_umid_start').text = umid
  outtreeroot.find('global_stashc').text = file_stash
  outtreeroot.find('batch_tech_info').text = 'TCRE main experiments - historical integration 2000-2014 with CMIP6 forcing data'
  outtreeroot.find('batch_proj').text = 'TCRE'
  outtreeroot.find('batch_desc').text = 'HadCM3S Main Experiment'

  #Write the new old old umis to a record file
  f_out = open('./dicts/umiddict_tcre_main_'+str(model_start_year)+'.txt','w')

  #Loop over the old umids
  for old_umid in old_umids:

       #print old_umid
      
       param_data = param_dataset[param_dataset['umid']=='y'+old_umid[1:]]

       for theta in theta_list:
    
         try:
           
           count = count +1 
           print(count)
           #Include all xml tags that are constant to each experiment in experiment tree structure
           Experiment=Element('experiment')
           experimenttree=ElementTree(Experiment)
           Parameters = SubElement(Experiment, 'parameters')

           SubElement(Parameters, 'file_flux').text=file_flux
           SubElement(Parameters, 'file_so2dms').text=file_so2dms
           SubElement(Parameters, 'file_volc').text=file_volc
           SubElement(Parameters, 'file_volcanic').text=file_volcanic
           SubElement(Parameters, 'file_sulphox').text=file_sulphox
           SubElement(Parameters, 'file_spec_sw').text=file_spec_sw
           SubElement(Parameters, 'file_spec_lw').text=file_spec_lw
           SubElement(Parameters, 'file_ozone').text=file_ozone
           SubElement(Parameters, 'file_solar').text=file_solar
           SubElement(Parameters, 'file_ghg').text=file_ghg
           SubElement(Parameters, 'run_years').text=run_years
           #SubElement(Parameters, 'run_months').text=run_months
           SubElement(Parameters, 'model_start_year').text=str(model_start_year)

           #Include all xml tags that are unique to each experiment in tree structure
        
           SubElement(Parameters, 'exptid').text=umid
           if old_umid == old_umids[-1]:
             outtreeroot.find('batch_umid_end').text = umid
           f_out.write(old_umid+','+umid+'\n')
           
           umid=anc(umid)  #Update umid using anc function
      
           SubElement(Parameters, 'file_atmos').text= old_umid+'_2000.astart'
           SubElement(Parameters, 'file_ocean').text= old_umid+'_2000.ostart'

           #Input the parameters 
           SubElement(Parameters, 'vf1').text=str(param_data['vf1'][0])
           SubElement(Parameters, 'ct').text=str(param_data['ct'][0])
           SubElement(Parameters, 'cw_land').text=str(param_data['cw_land'][0])
           SubElement(Parameters, 'cw_sea').text=str(param_data['cw_sea'][0])
           SubElement(Parameters, 'rhcrit').text=np.array_str(param_data[['rhcrit01', 'rhcrit02', 'rhcrit03', 'rhcrit04', 'rhcrit05', 'rhcrit06', 'rhcrit07', 'rhcrit08', 'rhcrit09', 'rhcrit10', 'rhcrit11', 'rhcrit12', 'rhcrit13', 'rhcrit14', 'rhcrit15', 'rhcrit16', 'rhcrit17', 'rhcrit18', 'rhcrit19']])[3:-2]
           SubElement(Parameters, 'eacf').text=np.array_str(param_data[['eacf01', 'eacf02', 'eacf03', 'eacf04', 'eacf05', 'eacf06', 'eacf07', 'eacf08', 'eacf09', 'eacf10', 'eacf11', 'eacf12', 'eacf13', 'eacf14', 'eacf15', 'eacf16', 'eacf17', 'eacf18', 'eacf19']])[3:-2]
           SubElement(Parameters, 'entcoef').text=str(param_data['entcoef'][0])
           SubElement(Parameters, 'alpham').text=str(param_data['alpham'][0])
           SubElement(Parameters, 'dtice').text=str(param_data['dtice'][0])
           SubElement(Parameters, 'ice_size').text= str(param_data['ice_size'][0])
           SubElement(Parameters, 'dtheta').text= str(theta)
           SubElement(Parameters, 'isopyc').text= str(param_data['isopyc'][0])
           SubElement(Parameters, 'vertvisc').text= str(param_data['vertvisc'][0])
           SubElement(Parameters, 'vdiffsurf').text= str(param_data['vdiffsurf'][0])
           SubElement(Parameters, 'vdiffdepth').text= str(param_data['vdiffdepth'][0])
           SubElement(Parameters, 'mllam').text= str(param_data['mllam'][0])
           SubElement(Parameters, 'mldel').text= str(param_data['mldel'][0])
           SubElement(Parameters, 'l0').text = str(param_data['l0'][0])
           SubElement(Parameters, 'l1').text= str(param_data['l1'][0])
           SubElement(Parameters, 'so2_high_level').text= str(param_data['so2_high_level'][0])
           SubElement(Parameters, 'volsca').text= str(param_data['volsca'][0])
           SubElement(Parameters, 'anthsca').text= str(param_data['anthsca'][0])
           SubElement(Parameters, 'start_level_gwdrag').text= str(param_data['start_level_gwdrag'][0])
           SubElement(Parameters, 'kay_gwave').text= str(param_data['kay_gwave'][0])
           SubElement(Parameters, 'kay_lee_gwave').text= str(param_data['kay_lee_gwave'][0])
           SubElement(Parameters, 'asym_lambda').text= str(param_data['asym_lambda'][0])
           SubElement(Parameters, 'charnock').text= str(param_data['charnock'][0])
           SubElement(Parameters, 'z0fsea').text= str(param_data['z0fsea'][0])
           SubElement(Parameters, 'g0').text= str(param_data['g0'][0])
           SubElement(Parameters, 'r_layers').text= np.array_str(param_data[['r_layers01', 'r_layers02', 'r_layers03', 'r_layers04']])[2:-2]
           SubElement(Parameters, 'diff_coeff').text= np.array_str(param_data[['DIFF_COEFF01', 'DIFF_COEFF02', 'DIFF_COEFF03', 'DIFF_COEFF04', 'DIFF_COEFF05', 'DIFF_COEFF06', 'DIFF_COEFF07', 'DIFF_COEFF08', 'DIFF_COEFF09', 'DIFF_COEFF10', 'DIFF_COEFF11', 'DIFF_COEFF12', 'DIFF_COEFF13', 'DIFF_COEFF14', 'DIFF_COEFF15', 'DIFF_COEFF16', 'DIFF_COEFF17', 'DIFF_COEFF18', 'DIFF_COEFF19']])[3:-2]
           SubElement(Parameters, 'diff_coeff_q').text= np.array_str(param_data[['DIFF_COEFF_Q01', 'DIFF_COEFF_Q02', 'DIFF_COEFF_Q03', 'DIFF_COEFF_Q04', 'DIFF_COEFF_Q05', 'DIFF_COEFF_Q06', 'DIFF_COEFF_Q07', 'DIFF_COEFF_Q08', 'DIFF_COEFF_Q09', 'DIFF_COEFF_Q10', 'DIFF_COEFF_Q11', 'DIFF_COEFF_Q12', 'DIFF_COEFF_Q13', 'DIFF_COEFF_Q14', 'DIFF_COEFF_Q15', 'DIFF_COEFF_Q16', 'DIFF_COEFF_Q17', 'DIFF_COEFF_Q18', 'DIFF_COEFF_Q19']])[3:-2]
           SubElement(Parameters, 'diff_exp').text= np.array_str(param_data[['DIFF_EXP01', 'DIFF_EXP02', 'DIFF_EXP03', 'DIFF_EXP04', 'DIFF_EXP05', 'DIFF_EXP06', 'DIFF_EXP07', 'DIFF_EXP08', 'DIFF_EXP09', 'DIFF_EXP10', 'DIFF_EXP11', 'DIFF_EXP12', 'DIFF_EXP13', 'DIFF_EXP14', 'DIFF_EXP15', 'DIFF_EXP16', 'DIFF_EXP17', 'DIFF_EXP18', 'DIFF_EXP19']])[3:-2]
           SubElement(Parameters, 'diff_exp_q').text= np.array_str(param_data[['DIFF_EXP_Q01', 'DIFF_EXP_Q01.1', 'DIFF_EXP_Q03', 'DIFF_EXP_Q04', 'DIFF_EXP_Q05', 'DIFF_EXP_Q06', 'DIFF_EXP_Q07', 'DIFF_EXP_Q08', 'DIFF_EXP_Q09', 'DIFF_EXP_Q10', 'DIFF_EXP_Q11', 'DIFF_EXP_Q12', 'DIFF_EXP_Q13', 'DIFF_EXP_Q14', 'DIFF_EXP_Q15', 'DIFF_EXP_Q16', 'DIFF_EXP_Q17', 'DIFF_EXP_Q18', 'DIFF_EXP_Q19']])[3:-2]
  
           #Update overall tree structure
           outtreeroot.append(Experiment)

         except:
           print(old_umid)



  #Write overall tree stucture to output xml
  
  outtree.write(outxmlfile)
  f_out.close()


  subprocess.call('xmllint --format '+outxmlfile+' > test.xml',shell=True)
  subprocess.call('mv test.xml '+outxmlfile,shell=True)




def main():
  xmlgen()

if __name__=="__main__":
  main()
