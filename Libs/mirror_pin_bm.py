#!/bin/env python 
import sys
import socket
import time
import os

# My library
from Motor import *

host = '172.24.242.59'
port = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

while True:
    print time.clock()
    print "Type: dire_pin/hfm_pin/vfm_pin/both_pin"
    print "    : dire_bm/hfm_bm/vfm_bm/both_bm"
    msg = raw_input()

# Constructer
    stage_y=Motor(s,"bl_32in_st2_motor_1","pulse")
    stage_z=Motor(s,"bl_32in_st2_motor_2","pulse")

# distance from PIN to BM [pulse]
    pin_to_bm_y=28750
    pin_to_bm_z=10000

# set up parameters
    if msg=="dire_pin":
	y=0
	z=0

    elif msg=="hfm_pin":
	y=6300
	z=0

    elif msg=="vfm_pin":
    	y=0
    	z=79800

    elif msg=="both_pin":
    	y=6300
    	z=79800

    elif msg=="dire_bm":
    	y=0+pin_to_bm_y
    	z=0+pin_to_bm_z

    elif msg=="hfm_bm":
    	y=6300+pin_to_bm_y
    	z=0+pin_to_bm_z

    elif msg=="vfm_bm":
    	y=0+pin_to_bm_y
    	z=79800+pin_to_bm_z

    elif msg=="both_bm":
    	y=6300+pin_to_bm_y
    	z=79800+pin_to_bm_z

    else :
	print "Input correct option."
	system.exit(1)

    print "Parameters: Moving stage to (x,y)=(%5d, %5d)\n"%(y,z)

# Moving axes
    stage_y.move(y)
    stage_z.move(z)

    s.close()

    break
