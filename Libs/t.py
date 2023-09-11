#!/bin/env python 
import sys
import socket
import time
import datetime
import subprocess
#from Count import *

class MXserver:
	def __init__(self):
		self.host = '192.168.163.32'
        	self.port = 2222
        	self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.isConnect=False

	def isRunning(self):
		print("isRunnning")
		command="ssh %s ps -el | grep hss"%self.host
		check = subprocess.getoutput(command)
		print(check)

		if check.rfind("hsserver_legacy")!=-1:
			return True
		else:
			return False

	def connect(self):
		if self.isRunning==True:
        		self.s.connect((self.host,self.port))
			self.isConnect=True
			return True
		else:
			print("Server program is not running")
			return False

        def startServer(self):
                com="ssh %s hsserver_legacy &"%(self.host)
                os.system(com)

	def isReady(self):
		if self.isConnect==False:
			print(self.connect())
		message="get_state"
		self.s.sendall(message)
		rec=self.s.recv(8000)
		return rec
	
	def getState(self):
		message="get_state"
		self.s.sendall(message)
		rec=self.s.recv(8000)
		return rec

	def abort(self): # stop data collection
		message="abort"
		self.s.sendall(message)
		print(self.s.recv(8000)) # dummy buffer

	def end_automation(self): # stop the server program
		message="end_automation"
		self.s.sendall(message)
		print(self.s.recv(8000)) # dummy buffer

	def close(self):
		self.s.close()

if __name__=="__main__":
	mxs=MXserver()
	option=sys.argv[1]

	print(mxs.isReady())

	mxs.close()
