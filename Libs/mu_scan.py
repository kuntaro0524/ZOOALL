import sys
import socket
import time
import numpy
from Received import *
from Motor import *
from IDparam import *
import Count
import M1
import MirrorTuneUnit

if __name__=="__main__":
    host = '172.24.242.59'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    orig_y = 23100
    orig_z = -20500
    
    m1=MirrorTuneUnit.MirrorTuneUnit(s)
    cnt=Count.Count(s,0,1)

    ofile = open("mu_z.dat","w")
    imax = -9999

    y_curr,z_curr = m1.getPos()
    start_z = z_curr - 4000
    end_z = z_curr + 4000

    for zpos in numpy.arange(start_z,end_z,300):
        m1.moveZ(zpos)
        count1,count2 = cnt.getCount(0.1)
        count = int(count1)
        if count > imax:
            savez = zpos
            imax = count
        ofile.write("%8.5f %s %s\n"% (zpos,count1,count2))

    m1.moveZ(z_curr)
    ofile.close()

    ofile = open("mu_y.dat","w")
    start_y = y_curr - 800
    end_y = y_curr + 800

    for ypos in numpy.arange(start_y,end_y,80):
        m1.moveY(ypos)
        count1,count2 = cnt.getCount(0.1)
        count = int(count1)
        if count > imax:
            savey = y
            imax = count
        ofile.write("%8.5f %s %s\n"% (ypos,count1,count2))

    #m1.setTy(savety)
    m1.moveY(y_curr)
    ofile.close()
    s.close()
