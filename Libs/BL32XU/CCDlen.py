#!/bin/env python 
import sys
import socket
import time
import datetime 

# My library
from Received import *
from Motor import *
from BSSconfig import *

#
class CCDlen:
	def __init__(self,server):
		self.s=server
    		self.ccdlen=Motor(self.s,"bl_32in_st2_detector_1_x","pulse")
		
		self.off_pos=0 # pulse
		self.on_pos=-245000 # pulse
		self.homevalue=692.290
		
		self.isInit=False

	def getPos(self):
                return self.ccdlen.getPosition()[0]

	def getLen(self):
		pls=-float(self.getPos())
		len=pls/5000.0+self.homevalue
                return len

	def moveCL(self,len):
		if len > 600.0 or len < 120.0:
			print "Do nothing because CL should be in 110-600mm"
			return False
		tmp=len-self.homevalue
		pls=int(tmp*5000.0)
		sense_pls=-pls
		#print sense_pls
		#print self.getPos()
		self.move(sense_pls)
		print "Current Camera distance %8.2fmm"% self.getLen()

	def move(self,pls):
		self.ccdlen.move(pls)

	def evac(self):
		self.moveCL(300.0)
#		self.moveCL(500.0)

        def isMoved(self):
                isY=self.coly.isMoved()
                isZ=self.colz.isMoved()

                if isY==0 and isZ==0:
                        return True
                if isY==1 and isZ==1:
                        return False


if __name__=="__main__":
	host = '172.24.242.41'
	port = 10101

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))

	clen=CCDlen(s)
	print clen.getLen()
	#clen.moveCL(300.0)
	#clen.evac()

	s.close()
