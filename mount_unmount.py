import os,sys,glob
import time
import numpy as np
import socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import MXserver
import Zoo

if __name__ == "__main__":
	zoo=Zoo.Zoo()
	zoo.connect()
	zoo.getSampleInformation()

	for trayid in ["YUK0001","YUK0003","YUK0004"]:
		for pinid in [1,2]:
			try:
				zoo.mountSample(trayid,pinid)
				zoo.waitTillReady()
			except MyException, ttt:
				print "Sample mounting failed. Contact BL staff!"
				sys.exit(1)
		
			time.sleep(30)
			zoo.dismountCurrentPin()
			zoo.waitTillReady()

	zoo.disconnect()
