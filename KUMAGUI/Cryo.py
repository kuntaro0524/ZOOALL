#!/bin/env python 
import sys
import socket
import time

# My library
from Motor import *
from BSSconfig import *

class Cryo:
	def __init__(self,server):
		self.s=server
    		self.cryoz=Motor(self.s,"bl_32in_st2_cryo_1_z","pulse")
		
		self.v2p=1250
		self.isInit=False

#kawano (20100726)
#		self.off_pos=800 # pulse
#		self.on_pos=200 # pulse
		self.off_pos=1000 # pulse (add kawano@100726)
		self.on_pos=600 # pulse (add kawano@100726)

        def getEvacuate(self):
                bssconf=BSSconfig()

                try:
                        tmpon,tmpoff=bssconf.getCryo()
                except MyException,ttt:
                        print ttt.args[0]

                self.on_pos=float(tmpon)*self.v2p
                self.off_pos=float(tmpoff)*self.v2p

                self.isInit=True
                print self.on_pos,self.off_pos

        def getPosition(self):
			value=self.cryoz.getPosition()[0]
			return value
 

        def on(self):
                if self.isInit==False:
                        self.getEvacuate()
                self.cryoz.move(self.on_pos)

        def off(self):
                if self.isInit==False:
                        self.getEvacuate()
                self.cryoz.move(self.off_pos)

        def offFull(self):
                self.cryoz.nageppa(2000)

        def go(self,pvalue):
                self.cryoz.nageppa(pvalue)

        def goOn(self):
                if self.isInit==False:
                        self.getEvacuate()
                self.cryoz.nageppa(self.on_pos)

        def goOff(self):
                if self.isInit==False:
                        self.getEvacuate()
                self.cryoz.nageppa(self.off_pos)

	def safetyEvacuate(self):
                if self.isInit==False:
                        self.getEvacuate()
		self.go_and_check(self.off_pos)

        def go_and_check(self,pvalue):
		index=0
		while(1):
                	self.cryoz.move(pvalue)
			value=self.cryoz.getPosition()[0]
			if value==pvalue:
				break
			index+=1
			print index

	def moveTo(self,pls):
		self.cryoz.move(pls)

        def isMoved(self):
                isZ=self.cryoz.isMoved()

                if isZ==0:
                        return True
                if isZ==1:
                        return False

if __name__=="__main__":
	host = '172.24.242.41'
	port = 10101

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))

	#bm=BM(s)
	#bm.on()
	#bm.off()

	cry=Cryo(s)
	pos = cry.getPosition()
	print pos
	print cry.getEvacuate()
	#cry.go_and_check(0)
	#cry.moveTo(-10000)
	#time.sleep(3)
	#cry.go_and_check(980)
	cry.on()
	#coli.off()

	s.close()
