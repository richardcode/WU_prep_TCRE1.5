import numpy as np

sim_start_year = 2014
sim_end_year = 2024

outfile = 'latvolc_zeros_'+str(sim_start_year)+str(sim_end_year+1)


aod_month = []
#Append two years of zeros on the end to get to end of 2014
add_zeros = np.zeros((73))
inline = ','.join(["{:.18e}".format(f) for f in add_zeros])
counter=1
while counter<=12*(sim_end_year-sim_start_year+2):
    aod_month.append(inline)
    counter = counter + 1


fout=open(outfile, 'w')

fout.write("<volcanic>\n")


year=sim_start_year
month=0
i= 0

fout.write("\t<forcing name='"+outfile+"' year='"+str(year)+"' value='\n")

while year<=(sim_end_year+1):

  if year==(sim_end_year+1) and month==12:
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
