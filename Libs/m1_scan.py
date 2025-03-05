import sys
import socket
import time
import numpy
from Received import *
from Motor import *
from IDparam import *
import Count
import M1

if __name__=="__main__":
    host = '172.24.242.59'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    
    m1=M1.M1(s)
    cnt=Count.Count(s,0,1)

    ofile = open("m1_scan.dat","w")
    imax = -9999
    ty_curr = m1.getTy()
    start = ty_curr - 0.5
    end = ty_curr + 0.5

    for ty in numpy.arange(start,end,0.01):
        m1.setTy(ty)
        count1,count2 = cnt.getCount(0.1)
        count = int(count1)
        if count > imax:
            savety = ty
            imax = count
        ofile.write("%8.5f %d\n"% (ty,count))

    m1.setTy(savety)
    ofile.close()
    s.close()
