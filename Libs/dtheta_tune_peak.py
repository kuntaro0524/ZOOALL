#!/bin/env python 
import sys
import socket
import time
from  File import *
from  Mono import *
from TCS import *

# My library
from Motor import *

if __name__=="__main__":
	host = '172.24.242.59'
	port = 10101
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))

	f=File("./")
	conf=ConfigFile()
	prefix="%03d"%f.getNewIdx3()
	tcs=TCS(s)
	mono=Mono(s)

	mono.scanDt1PeakConfig(prefix,"DTSCAN_NORMAL",tcs)
	#mono.scanDt1PeakConfig(prefix,"DTSCAN_FULLOPEN",tcs)
	dtheta1=int(mono.getDt1())
	print "Final dtheta1 = %d pls"%dtheta1
	s.close()
