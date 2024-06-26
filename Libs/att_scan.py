import os,sys,math,socket
from File import *
from AnalyzePeak import *
from Count import *
import Att
import Count

#2014/04/12 The first code by K.Hirata

if __name__=="__main__":
	# Establishing MS server connection
	host = '172.24.242.59'
	port = 10101
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))

	# Attenuator motor drive
	att=Att.Att(s)
	# Counter 
	counter=Count.Count(s,1,0)

	# ofile
	of=open("att_fac.scn","w")

	idx=0
	for pls in arange(0,3600,100):
		att.move(pls)
		istr=counter.getPIN(1.0)
		of.write("%5d, %5d, %s\n"%(idx,pls,istr))
		print istr
		of.flush()
		idx+=1
	of.close()
	s.close()
