#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *

class MBS:
	def __init__(self,server):
		self.s=server

	def anaRes(self,recbuf):
	#	bl_32in_plc_mbs/get/1128_blrs_root_blanc4deb/open/0
		cols=recbuf.split("/")
		ncol=len(cols)
		status=cols[ncol-2]
		return status

	def isLocked(self):
		status=self.getStatus()
		if status=="locked":
			return True
		else:
			return False

	def getStatus(self):
		com="get/bl_32in_plc_mbs/status"
                # counter clear
                self.s.sendall(com)
                recbuf=self.s.recv(8000)
		#print recbuf
		status=self.anaRes(recbuf)
		# return value: lock/moving/open/close
		return status

	def open(self):
		com="put/bl_32in_plc_mbs/open"
                # counter clear
                self.s.sendall(com)
                recbuf=self.s.recv(8000)
		# 30 sec trials
		for i in range(0,10):
			if self.getStatus()=="open":
				print "OPEN Okay"
				return True
			time.sleep(3.0)
		print "Remote control is okay?"
		return False

	def close(self):
		com="put/bl_32in_plc_mbs/close"
                # counter clear
                self.s.sendall(com)
                recbuf=self.s.recv(8000)

		# 30 sec trials
		for i in range(0,10):
			if self.getStatus()==0:
				print "CLOSE Okay"
				return True
			time.sleep(3.0)
		print "Remote control is okay?"
		return False

	# wait_interval [sec]
	def openTillOpen(self,wait_interval=300,ntrial=150):
		for i in range(0,ntrial):
			if self.isLocked()==True:
				tstr=datetime.datetime.now()
				print "MBS %s: waiting for 'unlocked'"%tstr
				time.sleep(wait_interval)
			else:
				self.open()
                                break

		for i in range(0,50):
                        if self.getStatus()=="open":
				return True
			else:
				time.sleep(5)
		return False

if __name__=="__main__":
        #host = '192.168.163.1'
        host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

        mbs=MBS(s)
	print mbs.getStatus()
	print mbs.isLocked()
	#mbs.openTillOpen(wait_interval=10,ntrial=30)
	#time.sleep(10)
	#print mbs.close()
	#time.sleep(15)
	#mbs.getStatus()
	#mbs.open()
	#time.sleep(15)
	#mbs.getStatus()

        s.close()
