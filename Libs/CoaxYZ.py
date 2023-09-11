#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *
from AnalyzePeak import *
from File import *
from AxesInfo import *
from ConfigFile import *
from Count import *

class CoaxYZ:

	def __init__(self,server):
		self.s=server
		self.coax_z=Motor(self.s,"bl_32in_st2_slit_2_hall","pulse")
		self.coax_y=Motor(self.s,"bl_32in_st2_slit_2_ring","pulse")
		self.count=Count(self.s,3,0)
		self.sense=-1

	def moveZ(self,pulse):
		target=pulse*self.sense
		self.coax_z.move(target)

	def getZ(self):
		curr_z=self.sense*int(self.coax_z.getPosition()[0])
		return curr_z

	# DENGEROUS 140611
	def scan2D(self):
		#self.coax_z.move(-11926)
		#self.coax_y.move(22840)

		curr_z=int(self.coax_z.getPosition()[0])
		curr_y=int(self.coax_y.getPosition()[0])

		print(curr_z,curr_y)
		#print self.coax_y.getPosition()[0]

		# Scan width [0.5um/pls] 
		# 3mm ?
		# 3000um -> 6000pls

		start_z=curr_z-2000
		end_z=curr_z+2000

		start_y=curr_y-2000
		end_y=curr_y+2000

		print("Z",start_z,end_z)
		print("Y",start_y,end_y)

		# scan step
		step_pls=500

		ofile=open("coax.dat","w")
	
		print("Scan stage starts")

		for y in arange(start_y,end_y,step_pls):
			for z in arange(start_z,end_z,step_pls):
				self.coax_y.move(y)
				self.coax_z.move(z)
				cps=self.count.getCount(0.2)
				ofile.write("%5d %5d %10s %10s\n"%(y,z,cps[0],cps[1]))
				print("%5d %5d %10d"%(y,z))
				ofile.flush()
			ofile.write("\n")

		# position change
		curr_z=int(self.coax_z.getPosition()[0])

		# Initial value
		self.coax_z.move(curr_z)
		self.coax_y.move(curr_y)
		ofile.close()

if __name__=="__main__":
	#host = '192.168.163.1'
	host = '172.24.242.41'
	port = 10101
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))
	
	co=CoaxYZ(s)
	curr=co.getZ()
	print(curr)
	t=curr+10
	print(t)
	co.moveZ(t)
	time.sleep(10)
	co.moveZ(curr)

	s.close()
