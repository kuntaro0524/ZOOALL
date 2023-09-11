import sys
import socket
import time
import datetime
import math
import timeit

from Procedure import *

if __name__=="__main__":
	host = '172.24.242.41'
	port = 10101
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))
	
	proc=Procedure(s)

	#####
	## Set energy & dtheta1 determination
	#####

	if len(sys.argv)!=2:
		print("[Usage]: id_detune.py ENERGY")
		sys.exit(1)
	en=float(sys.argv[1])
        #proc.detuneID(energy,cnt1,cnt2,inttime,nback=30):
        proc.detuneID(en,3,0,1.0)

	s.close()

