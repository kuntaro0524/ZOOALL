import sys,os,math
from scipy.interpolate import splrep,splev,interp1d,splprep
import scipy,numpy

#from scipy.interpolate import splrep,splev,interp1d,splprep


sfile="/isilon/BL32XU/BLsoft/PPPP/07.IDparams/id32xu.tbl"

lines=open(sfile,"r").readlines()

xd=[]
yd=[]
for line in lines:
	cols=line.split()
	xd.append(float(cols[0]))
	yd.append(float(cols[1]))

nxa=numpy.array(xd)
nya=numpy.array(yd)

## Min & Max value of arrays
miny=nya.min()
maxy=nya.max()
minx=nxa.min()
maxx=nxa.max()

step_int=(maxx-minx)/0.1
half=(maxy-miny)/2.0

tck=scipy.splrep(px,py)
newx=arange(minx,maxx,step_int)
newy=splev(newx,tck,der=0)

return newx,newy



"""
px,py=ana.prepData2(0,1)
en_list,gap_list=ana.spline(px,py,100000)

i=0
for e in en_list:
        if math.fabs(energy-e) < 0.0001:
                rtn_gap=round(gap_list[i],3)
                return rtn_gap
        else :
                i+=1



"""
