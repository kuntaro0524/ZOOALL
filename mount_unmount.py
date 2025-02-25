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

	for trayid in ["SP81046"]:
		for pinid in [8,9,10,11,12,13,14,15,16]:
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
