#!/bin/env python 
import sys
import socket
import time
import datetime

# My library
from Mono import *
from FES import *
from ID import *
from TCS import *
from ExSlit1 import *
from AxesInfo import *
from File import *

host = '172.24.242.41'
port = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

while True:

# Conditions
    en_list=[12.3984]

# TCS scan range 110406
    scan_apert=0.05
    scan_another_apert=0.5
    scan_start=-2.0
    scan_end=2.0
    scan_step=0.05
    scan_time=0.2

# St2Slit1 knife edge scan
    slit1_start=18000
    slit1_end=100
    slit1_step=-100
    slit1_ch0=3
    slit1_ch1=0

# Detector number
    cnt_ch1=3
    cnt_ch2=0

# Devices
    id=ID(s)
    mono=Mono(s)
    tcs=TCS(s)
    exs=ExSlit1(s)
    axes=AxesInfo(s)
    f=File("./")

    index=0
    sizei=0

    # Log file
    logf=open("bp.log","w")
    logf.write("# EN VFWHM VCEN HFWHM HCEN\n")

    for en in en_list :
	# Axes information 
	prefix="%03d"%f.getNewIdx3()
	enstr="%fkev"%en
	ofile=prefix+"_"+enstr+"_axes.dat"
	axes.all(ofile)

	# Changing Energy
    	id.moveE(en)
    	mono.changeE(en)

	# Waiting for a thermal equilibrium
	if en<12.398:
		print("Energy < 12.3984")
		time.sleep(600)

	# TCS aperture 0.1x0.1mm
	tcs.setApert(0.1,0.1)

	# Slit1 vertical & horizontal scan
    	prefix="%03d"%f.getNewIdx3()
	exs.fullOpen()

	slit1_vfwhm,slit1_vcenter=exs.scanV(prefix,-slit1_start,-slit1_end,-slit1_step,slit1_ch0,slit1_ch1,0.5)
	slit1_hfwhm,slit1_hcenter=exs.scanH(prefix,-slit1_start,-slit1_end,-slit1_step,slit1_ch0,slit1_ch1,0.5)

	# Log string
	#("Gap[mm],Energy[kev],Dtheta1[pulse],Ty1[pulse],TCS_v,TCS_h,Eslit1_h")
	logstr="%8.4f %8.4f %8.4f %8.4f %8.4f"%(en,slit1_vfwhm,slit1_vcenter,slit1_hfwhm,slit1_hcenter)

	logf.write("%s\n"%logstr)
	logf.flush()

    logf.close()
    s.close()

    break
