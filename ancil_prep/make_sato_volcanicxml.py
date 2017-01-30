#Create xml file from the aod_array 

import numpy as np

outfile = 'sato_hist73lat_volcanic'
f_in = open('/home/jupiter/cpdn/millar/Data/forcings/regridded_sato.txt','r')
aod_month = []
for line in f_in:
  aod_month.append(line[:-1])



fout=open(outfile, 'w')

fout.write("<volcanic>\n")

start_year = 1850
end_year = 2012

year=start_year
month=0
i=0

fout.write("\t<forcing name='"+outfile+"' year='"+str(year)+"' value='\n")

while year<=end_year:

  if year==end_year and month==12:
    fout.write("</volcanic>")
    year=year+1
  elif month==12:
    year=year+1
    fout.write("\t<forcing name='"+outfile+"' year='"+str(year)+"' value='\n")
    month=0
    fout.write(2*"\t"+" "+aod_month[i]+","+"\n")
  elif month==11:
    fout.write(2*"\t"+" "+aod_month[i]+"'"+"\n"+"\t"+"/>"+"\n")
  else:
    
    fout.write(2*"\t"+" "+aod_month[i]+","+"\n")

  i=i+1
  month=month+1

fout.close()


