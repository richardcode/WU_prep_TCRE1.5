import iris
import numpy as np
import iris.analysis.cartography
import iris.coord_categorisation
import matplotlib.pyplot as plt
import os
import subprocess

import iris.coords

files_in = ['/data/data/TCRE_data/n48_cmip6_hist/vmro3_input4MIPs_ozone_moddatevgrid_CMIP_UReading-CCMI-1-0_gr_200001-201412_n48.nc',
            '/network/aopp/ares/mad/millar/rcp26_ancils/n48/DMSSO2NH3_18502100_RCP26.nc']

global_cubes =[]
for f in files_in:
    
    if f == '/data/data/TCRE_data/n48_cmip6_hist/vmro3_input4MIPs_ozone_moddatevgrid_CMIP_UReading-CCMI-1-0_gr_200001-201412_n48.nc':
    os.system('ncatted -O -a calendar,t,m,c,"360_day" '+f)
 
