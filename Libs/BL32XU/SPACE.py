import sys
import socket
import time
from MyException import *

class SPACE:

	def __init__(self):
		host = '192.168.163.152'
		port = 3665
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((host,port))

	def cutQuery(self,recv):
		idx=recv.rfind("/")

		if idx+1==len(recv):
			newstr=recv[:idx]
			idx=newstr.rfind("/")

		rtn=recv[idx+1:].replace("/","")
		return rtn

	def queryAll(self):
		query_com="I/get/bl_32in_sc_all/query"
		self.s.sendall(query_com)
                tmpstr=self.s.recv(8000) # dummy acquisition
		judge_str=self.cutQuery(tmpstr)

		return judge_str

	def wait(self):
		time.sleep(1.0)
		cnt=0
		while(self.queryAll()=="active"):
			if cnt%60==0:
				print "another one second waiting..."
			time.sleep(1.0)
			cnt+=1

	def do(self,command):
		self.s.sendall(command)
                tmpstr=self.s.recv(8000) # dummy acquisition

		i=0
		self.wait()

	def goEvacuatePosition(self):
		com="I/put/bl_32in_sc_evacuate/on"
		self.do(com)

	def goMountPosition(self):
		com="I/put/bl_32in_sc_evacuate/off"
		self.do(com)

	def checkOnGonio(self):
		com="I/get/bl_32in_sc_all/ongonio"
		self.s.sendall(com)
                tmpstr=self.s.recv(8000) # dummy acquisition
		#Rsrv/put/bl_32in_sc_all/ongonio_none
		judge_str=self.cutQuery(tmpstr)

		# string analysis
		judge_str=judge_str[judge_str.find("_")+1:]
		print judge_str

		if judge_str=="none":
			return 0,0

		else:
			pi=judge_str.rfind("_")

			trayid=int(judge_str[:pi])
			sampleid=int(judge_str[pi+1:])
			return trayid,sampleid

	def mountSample(self,tray,sample):
		# Check gonio sample
		gonio_tray,gonio_sample=self.checkOnGonio()

		if gonio_tray!=0:
			raise MyException("Sample exists!")

		# Evacuate off
		self.goMountPosition()

		trayid=int(tray)
		sampleid=int(sample)
		# checking ID
		if trayid>4:
			raise MyException("Tray ID exceeds 4\n")
		if sampleid>16:
			raise MyException("Sample ID exceeds 16!\n")
	
		# Mounting sample
		com="I/put/bl_32in_sc_all/mount_%d_%d"%(trayid,sampleid)
		print com
		self.do(com)

		# Evacuate off
		# self.goEvacuatePosition()

	def dismountSample(self,tray,sample):
		# Evacuate off
		self.goMountPosition()

		# Checking the gonio sample 
		gonio_tray,gonio_sample=self.checkOnGonio()
		if gonio_tray==0:
			raise MyException("Gonio sample does not exist!!\n")

		# check if the ID matches each other
		trayid=int(tray)
		sampleid=int(sample)

		# Dismounting sample
		com="I/put/bl_32in_sc_all/unmount_%d_%d"%(trayid,sampleid)
		self.do(com)
		
		self.goEvacuatePosition()

	def skipSample(self):
		com="I/put/bl_32in_sc_all/next"
		self.do(com)

if __name__=="__main__":
	space=SPACE()
	#space.goMountPosition()
	#space.goEvacuatePosition()
	#try :
		#space.mountSample(1,1)
        #except MyException,ttt:
                #print ttt.args[0]

	#print space.checkOnGonio()
	print space.skipSample()
	#try :
		#space.dismountSample(1,1)
        #except MyException,ttt:
                #print ttt.args[0]
