import sys
import socket
import time
import datetime

# My library
from File import *
from BS import *

if __name__=="__main__":
        host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

        f=File("./")
        prefix="%03d"%f.getNewIdx3()

        z_lower=int(sys.argv[1])
        z_upper=int(sys.argv[2])
        z_step=int(sys.argv[3])

        y_lower=int(sys.argv[4])
        y_upper=int(sys.argv[5])
        y_step=int(sys.argv[6])

        print("Y range: %5d - %5d step %5d"%(y_lower,y_upper,y_step))
        print("Z range: %5d - %5d step %5d"%(z_lower,z_upper,z_step))

        bs=BS(s)
        #bs.scan2D(prefix,-1000,1000,200,-1000,1000,100)
        #bs.scan2D(prefix,-500,500,100,-100,100,20)
        min_y,min_z=bs.scan2D(prefix,z_lower,z_upper,z_step,y_lower,y_upper,y_step)
        print("the minimum intensity: %5d %5d"%(min_y, min_z))
        s.close()

