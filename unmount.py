import os,sys,glob
import time
import numpy as np
import socket
import Zoo

if __name__ == "__main__":
	zoo=Zoo.Zoo()
	zoo.connect()
	zoo.getSampleInformation()
	zoo.dismountCurrentPin()
	zoo.waitTillReady()
	zoo.disconnect()
