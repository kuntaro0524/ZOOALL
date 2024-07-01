#!/bin/env python 
import os,sys
import socket
import time
import datetime
import commands
#from Count import *

class MXserver:
	def __init__(self):
		self.host = '192.168.163.32'
        	self.port = 2222
        	self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.isConnect=False
		self.isRunning=False

	def checkRunning(self):
		command="ssh %s ps -el | grep hss"%self.host
		#print command
		check = commands.getoutput(command)
		#print check
		if check.rfind("hsserver_legacy")!=-1:
			return True
		else:
			return False

	def connect(self):
		if self.checkRunning()==True:
        		self.s.connect((self.host,self.port))
			self.isConnect=True
			return True
		else:
			print "Server program is not running"
			return False

        def startServer(self):
                #com="ssh %s hsserver_legacy &"%(self.host)
		com="ssh %s \"hsserver_legacy>&/dev/null\" &"%(self.host)
		print com
                os.system(com)

	def isReady(self):
		print self.isConnect
		if self.isConnect==False:
			self.connect()
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
		print self.s.recv(8000) # dummy buffer

	def end_automation(self): # stop the server program
		if self.isConnect==False:
			self.connect()
		message="end_automation"
		self.s.sendall(message)
		print self.s.recv(8000) # dummy buffer

	def close(self):
		self.s.close()

if __name__=="__main__":
	mxs=MXserver()
	#option=sys.argv[1]
	if mxs.checkRunning()==True:
		mxs.end_automation()
		time.sleep(10)
		mxs.startServer()
	else:
		mxs.startServer()
	#mxs.close()
