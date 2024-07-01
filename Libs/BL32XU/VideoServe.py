#!/bin/env python 
import errno
import sys
import socket
import time
import datetime
import os
import numpy
import subprocess
from socket import error as socket_error
from MyException import *

# My library
from BeamCenter import *

class VideoServe:
	def __init__(self):
		#self.host='192.168.163.6' # for BL32XU videosrv 
		self.host='192.168.163.6' # for BL32XU videosrv  130407 modified
		self.port = 10101
		self.open_sig=0 # network connection to videoserv
		self.isPrep=0
		self.user=os.environ["USER"]
		self.videosrv="/isilon/Common/CentOS4/videosrv_jul02_2015a"

	# BL32XU VIDEOSRV (artray)
	def isRunning(self):
		command="ssh 192.168.163.6 \"ps aux | grep video | grep artray\" > ./tmp"
		os.system(command)
		cnt=0
		lines=open("./tmp","r").readlines()
		for line in lines:
			cnt+=1
		print cnt

	def killVideosrv(self):
		command="ssh 192.168.163.6 \"killall %s\""%(self.videosrv)
		os.system(command)
		time.sleep(5.0)

	def startVideosrv(self):
		command="ssh 192.168.163.6 \"%s --artray 3\""%(self.videosrv)
		os.system(command)
		time.sleep(5.0)

	def reboot(self):
		command="ssh 192.168.163.6 \"reboot\""
		os.system(command)

	def isBooting(self):
		idx=0
		while(1):
			command="ssh 192.168.163.6 \"date\""
			os.system(command)
			if idx==0:
				self.killVideosrv()
				self.reboot()
				print "rebooting"
			time.sleep(10.0)
			idx+=1
			
if __name__=="__main__":
	vsrv=VideoServe()
	starttime=datetime.datetime.now()
	
	vsrv.isBooting()
	#print vsrv.isRunning()
	#endtime=datetime.datetime.now()
	#t_delta=endtime-starttime
	#print "%8.5f"%(t_delta.milliseconds())
	#print starttime,endtime
	#print t_delta.seconds
	#print t_delta.microseconds/1E6
