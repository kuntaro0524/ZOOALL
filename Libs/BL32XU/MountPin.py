import sys
import socket
import time

# my classes
from MyException import *
from SPACE import *
from Gonio import *
from Colli import *
from BS import *
from Cryo import *

#####
# 100715 coded by kuntaro
#####
# space	: initialized SPACE class pointer
# colli	: initialized Colli class pointer
# bs	: initialized BS class pointer
# cryoz	: initialized Cryo class pointer
# gonio	: initizlied Gonio class pointer

class MountPin:

	def __init__(self,space,colli,bs,cryoz,gonio):
		self.space=space
		self.colli=colli
		self.bs=bs
		self.cryoz=cryoz
		self.gonio=gonio

	def prep(self):
		# Evacuate
		## cryo
		self.cryoz.off()

		## collimator
		self.colli.off()

		## beam stopper
		self.bs.off()

		# Mount position
		self.gonio.goMountPosition()

	def mount(self,trayid,pinid):
		# cast
		trayid=int(trayid)
		pinid=int(pinid)

		# evacuate devices
		self.prep()

		# Mount pin
        	try :
                	self.space.mountSample(trayid,pinid)
        	except MyException,ttt:
                	print ttt.args[0]
			sys.exit()

	def dismount(self,trayid,pinid):
		# cast
		trayid=int(trayid)
		pinid=int(pinid)

		# evacuate devices
		self.prep()

		# dismount pin
        	try :
                	self.space.dismountSample(trayid,pinid)
        	except MyException,ttt:
                	print ttt.args[0]
			sys.exit()
	
if __name__=="__main__":
        host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

	space=SPACE()
	gonio=Gonio(s)
	colli=Colli(s)
	cryo=Cryo(s)
	bs=BS(s)

	mp=MountPin(space,colli,bs,cryo,gonio)
	
	#mp.mount(2,1)
	mp.dismount(2,1)
