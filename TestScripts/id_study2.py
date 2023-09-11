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
#from Count import *

host = '172.24.242.41'
port = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

while True:

# Energy range
    en_start=12.4
    en_end=12.5
    en_step=0.1

# Filename
    #en_list=[8.5,10.0,11.0,12.0,12.398,14.0,15.0,16.0,17.0,18.0,19.0,20.0]
    #en_list=[12.398]

# Rough scan
    idch1=3
    rough_step=0.10
    fine_step=0.005
    sfine_step=0.001

# Devices
    id=ID(s)
    mono=Mono(s)
    fes=FES(s)
    f=File("./")
    tcs=TCS(s)

    index=0
   
    # log file
    logf=open("id.log","w")

    # Energy range
    width=en_end-en_start
    npoint=int(width/en_step)+1

    for idx in range(0,npoint) :

	# energy
	en=en_start+float(idx)*float(en_step)

	if en==8.0:
		print("wainting")
		time.sleep(1800)

    	# Set TCS aperture full open
    	tcs.setApert(3.0,3.0)

	# file prefix
	enstr="%fkev"%(en)

	#moving the fisrt position
    	mono.changeE(en)
    	id.moveE(en)

	# dtheta1 tune
	prefix="%03d_%s_dt1"%(f.getNewIdx3(),enstr)
	mono.scanDt1PeakConfig(prefix,"DTSCAN_AUTOTUNE",tcs)

	# Rough scan
	prefix="%03d_%s_coarse"%(f.getNewIdx3(),enstr)
	current_id=id.getE(en)
	start=current_id-rough_step*10
	end=current_id+rough_step*10

	if start<=7.4:
		start=7.4

	max1=id.scanID(prefix,start,end,rough_step,idch1,0,0.2)

	# Fine scan
	prefix="%03d_%s_fine"%(f.getNewIdx3(),enstr)
	current_id=max1[0]
	start=current_id-fine_step*10.0
	end=current_id+fine_step*10.0

	if start<=7.4:
		start=7.4

	max2=id.scanID(prefix,start,end,fine_step,idch1,0,0.2)

	# Superfine scan
	prefix="%03d_%s_superfine"%(f.getNewIdx3(),enstr)
	current_id=max2[0]
	start=current_id-sfine_step*10.0
	end=current_id+sfine_step*10.0

	if start<=7.4:
		start=7.4

    	counter=Count(s,3,0)
    	pin_value=counter.getPIN(5)

	max3=id.scanID(prefix,start,end,sfine_step,idch1,0,0.2)
	print(max3)

	# Writing log file
	logf.write("%8.3f keV ID %8.5f PIN: %8s uA\n"%(en,max3[0],pin_value))
	
    s.close()

    break
