import sys
import socket
import time
import Device
import File
import ConfigFile

class RecoverDamp():
	def __init__(self):
        	#host = '192.168.163.1'
        	host = '172.24.242.41'
        	port = 10101
        	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        	s.connect((host,port))
		self.dev=Device.Device(s)
		self.dev.init()

	def recoverAtEn(self,en):
		# MBS open
        	self.dev.mbs.openTillOpen(wait_interval=300,ntrial=150)
		# DSS open
        	self.dev.dss.openTillOpen(wait_interval=300,ntrial=150)
		# Set gap at energy
		gap=self.dev.id.getGapAtE(en)
		self.dev.id.moveTillMove(gap,wait_interval=10,ntrial=10)
    		self.dev.mono.changeE(en)

        	f=File.File("/tmp/")
        	conf=ConfigFile.ConfigFile()
        	prefix="%03d"%f.getNewIdx3()
        	self.dev.mono.scanDt1PeakConfig(prefix,"DTSCAN_NORMAL",self.dev.tcs)
        	dtheta1=int(self.mono.getDt1())
        	print("Final dtheta1 = %d pls"%dtheta1)

		print("OKAY")

if __name__ == '__main__':
	rd=RecoverDamp()
	en=float(sys.argv[1])
	rd.recoverAtEn(en)
