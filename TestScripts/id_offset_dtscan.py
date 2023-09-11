#!/bin/env python 
import sys
import socket
import time
import datetime

# My library
from FES import *
from ID import *
from Mono import *
from File import *
from TCS import *
from ExSlit1 import *
#from Count import *

host = '172.24.242.41'
port = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

while True:

# Filename
    en_list=arange(8.5,20,0.1)

# Rough scan
    idch1=0
    rough_step=0.10

# Devices
    id=ID(s)
    mono=Mono(s)
    fes=FES(s)
    f=File("./")
    tcs=TCS(s)
    exs1=ExSlit1(s)

    index=0

    # log file
    logf=open("id.log","w")

    for en in en_list :
	# 10min wait
    	#time.sleep(600)
	# file prefix
	enstr="%fkev"%(en)

	#moving the fisrt position
    	mono.changeE(en)
    	id.moveE(en)

	# ID offset
	prefix="%03d_%s_offset"%(f.getNewIdx3(),enstr)
	current_id=id.getE(en)
	start=current_id-rough_step*10
	end=current_id+rough_step*10

	if start<=7.4:
		start=7.4

	for gap in arange(start,end,rough_step):
		id.move(gap)

		# dtheta1 tune
		prefix="%03d_%s_%f"%(f.getNewIdx3(),enstr,gap)
		print(prefix)
		mono.scanDt1Config(prefix,"DTSCAN_LOWENERGY",tcs)
	
    exs1.closeV()
    s.close()

    break
