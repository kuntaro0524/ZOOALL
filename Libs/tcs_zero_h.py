#!/bin/env python 
import sys
import socket
import time

# My library
from File import *
from TCS import *

while True:
    host = '172.24.242.59'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    # Initialization
    tcs=TCS(s)
    f=File("./")

# Counter channel
    cnt_ch1=0
    cnt_ch2=3

    prefix="%03d"%f.getNewIdx3()

# check zero parameters
    start_apert=1.0
    end_apert=-1.0
    step=-0.05
    cnt_time=0.2

# TCS full open
    tcs.setApert(1.0)

# TCS zero-aperture check
    prefix="%03d"%f.getNewIdx3()
    tcs.checkZeroH(prefix,start_apert,end_apert,step,cnt_ch1,cnt_ch2,cnt_time)

    s.close()
    break
