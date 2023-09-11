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

host = '172.24.242.41'
port = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

cnt_ch1=2 # PIN photodiode
cnt_ch2=1 # IC

while True:

# Filename
    en_list=[8.5,9.5,10.0,10.5,11.0,11.5,12.0,12.5,13.0,13.5,14.0,14.5,15.0,15.5,16.5,17.0,17.5,18.0,18.5,19.0,19.5,20.0]

# Dtheta1 range
    dtstart=	-93000
    dtend=	-86000
    dtstep=	50
    dtcnt=	0.2
    dtch1=	0
    dtch2=	3

# Rough scan
    idch1=	3
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

    for en in en_list :
	# file prefix
	enstr="%fkev"%en
	prefix="%02d_%s"%(f.getNewIdx(".scn"),enstr)
	print(enstr)

	#moving the fisrt position
    	mono.changeE(en)
    	id.moveE(en)

	# dtheta1 tune
	prefix="%02d_%s"%(f.getNewIdx(".scn"),enstr)
        center=mono.scanDt1(prefix,dtstart,dtend,dtstep,dtch1,dtch2,dtcnt)

	# Rough scan
	prefix="%02d_%s_coarse"%(f.getNewIdx(".scn"),enstr)
	current_id=id.getE(en)
	start=current_id-rough_step*10
	end=current_id+rough_step*10

	if start<=7.4:
		start=7.4

	max1=id.scanID(prefix,start,end,rough_step,idch1,0,0.2)

	# Fine scan
	prefix="%02d_%s_fine"%(f.getNewIdx(".scn"),enstr)
	current_id=max1[0]
	start=current_id-fine_step*10.0
	end=current_id+fine_step*10.0

	if start<=7.4:
		start=7.4

	max2=id.scanID(prefix,start,end,fine_step,idch1,0,0.2)

	# Superfine scan
	prefix="%02d_%s_sfine"%(f.getNewIdx(".scn"),enstr)
	current_id=max2[0]
	start=current_id-sfine_step*10.0
	end=current_id+sfine_step*10.0

	if start<=7.4:
		start=7.4

	max3=id.scanID(prefix,start,end,sfine_step,idch1,0,0.2)

	# dtheta1 tune @ TCS 3.0,3.0
	tcs.setApert(3.0,3.0)
	prefix="%02d_%s"%(f.getNewIdx(".scn"),enstr)
        center=mono.scanDt1(prefix,dtstart,dtend,dtstep,dtch1,dtch2,dtcnt)

	# TCS scan
	prefix="%02d_%s"%(f.getNewIdx(".scn"),enstr)
	vcenter,hcenter=tcs.scanBoth(prefix,0.05,0.5,-1.0,1.0,0.05,idch1,0,0.2)
	tcs.setApert(3.0,3.0)
	tcs.setPosition(0.052,0.062)

	# Writing log file
	logf.write("%8.3f keV ID %8.5f Dtheta1 %8d TCS (V,H)=(%8.5f, %8.5f) \n"%(en,max1[0],int(center),vcenter,hcenter))
	
    s.close()

    break
