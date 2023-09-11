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

        bs=BS(s)
        #bs.scan2D(prefix,-1000,1000,200,-1000,1000,100)
        bs.scan2D(prefix,-1000,1000,100,-250,250,20)

        s.close()

