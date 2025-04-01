#!/bin/env python 
import sys
import socket
import time
import math
from pylab import *

# My library
import Shutter
import Light

while True:
	#host = '192.168.163.1'
	host = '172.24.242.59'
	port = 10101
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))

##	Device definition
	shutter=Shutter.Shutter(s)
	light=Light.Light(s)

	# Backlight Off
	light.off()

	# Shutter close
	shutter.open()
	print "Shutter on Diffractometer was opened"

	# Slit close
	exs1.openV()
	print "Slit lower blade was opened"

	break
