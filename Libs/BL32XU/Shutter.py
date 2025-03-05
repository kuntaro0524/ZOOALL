#!/bin/env python 
import sys
import socket
import time
import datetime
#from Count import *

# My library

class Shutter:
	def __init__(self,server):
		self.s=server
		self.openmsg="put/bl_32in_st2_shutter_1/on"
		self.clsmsg="put/bl_32in_st2_shutter_1/off"
		self.qmsg="get/bl_32in_st2_shutter_1/status"

	def open(self):
		self.s.sendall(self.openmsg)
		print self.s.recv(8000) # dummy buffer
		#self.query()

	def close(self):
		self.s.sendall(self.clsmsg)
		print self.s.recv(8000) # dummy buffer
		#self.query()

	def query(self):
		self.s.sendall(self.qmsg)
		return self.s.recv(8000) # dummy buffer

	def isOpen(self):
		strstr=self.query()
		cutf=strstr[:strstr.rfind("/")]
		final=cutf[cutf.rfind("/")+1:]
		if final=="off":
			return 0
		else :
			return 1

if __name__=="__main__":
	#host = '192.168.163.1'
	host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

	#pin_ch=int(raw_input())

	shutter=Shutter(s)
	#print shutter.isOpen()
	#shutter.open()
	#print shutter.isOpen()
	#time.sleep(10.0)
	#shutter.open()
	shutter.close()
	#time.sleep(10.0)
	s.close()
