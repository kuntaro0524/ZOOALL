#!/bin/env python 
import sys
import socket
import time
import datetime 

# My library
import Colli 
import File

if __name__=="__main__":
	host = '172.24.242.59'
	port = 10101

	f=File.File("./")

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))

        prefix="%03d"%f.getNewIdx3()
	coli=Colli.Colli(s)
	log=coli.scan(prefix,1)
	print log
	trans,pin=coli.compareOnOff(1)
	print "Transmission %5.2f percent (Counter:%d)\n"%(trans,pin)

	s.close()
