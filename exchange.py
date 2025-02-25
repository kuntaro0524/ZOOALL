import os,sys,glob
import time
import numpy as np
import socket
import Zoo

if __name__ == "__main__":
	zoo=Zoo.Zoo()
	zoo.connect()
	zoo.getSampleInformation()
	time.sleep(2.0)
	#zoo.autoCentering()
	#zoo.stop()
	zoo.exchangeSample("CPS4479","3")
	zoo.waitTillReady()
	zoo.disconnect()
