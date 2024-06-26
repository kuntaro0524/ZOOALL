import os,sys
import time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import AnaShika

"""
filename gx gy gz phi score
test_000452.img 0.1001 -1.894 0.2285 220.0 9
test_000771.img 0.1451 -1.714 0.1749 220.0 9
#scan_complete
"""

class SummarySHIKA:
	def __init__(self,path,prefix):
		self.path=path
		self.prefix=prefix
		self.sumdat="%s/_spotfinder/%s_selected.dat"%(self.path,self.prefix)
		print "Treating : %s "%self.sumdat

	def waitingForSummary(self):
		while(1):
			print "Waiting for generating %s"%self.sumdat
			if os.path.exists(self.sumdat)==False:
				time.sleep(1.0)
			else:
				return 1
		
	def readSummary(self):
		glist=[]
		while(1):
			print "waiting for readout %s"%self.sumdat
			lines=open(self.sumdat,"r").readlines()
			# is Finished?
			if len(lines)<1:
				continue
			if lines[len(lines)-1].rfind("scan_complete")==-1:
				time.sleep(1.0)
				continue
			# Scan completed but no crystals were found
			elif len(lines)==2:
				print "Oh my god!! No crystals!!"
				raise MyException("No crystals were found!")
				break
			else:
				for line in lines[1:]:
					cols=line.split()
					if len(cols)==6:
						#print cols
						gx=float(cols[1])
						gy=float(cols[2])
						gz=float(cols[3])
						phi=float(cols[4])
						score=float(cols[5])
						ginfo=gx,gy,gz,phi,score
						glist.append(ginfo)
				break
		return glist

	def readSummarySkip(self):
		glist=[]
		isCompleted=False
		i_wait=0
		while(1):
			print "waiting for readout %s"%self.sumdat
			lines=open(self.sumdat,"r").readlines()
			# is Finished?
			if len(lines)<1:
				continue
			if lines[len(lines)-1].rfind("scan_complete")!=-1:
				isCompleted=True
				if len(lines)==2:
					print "Oh my god!! No crystals!!"
					raise MyException("No crystals were found!")
				for line in lines[1:]:
					cols=line.split()
					if len(cols)==6:
						#print cols
						gx=float(cols[1])
						gy=float(cols[2])
						gz=float(cols[3])
						phi=float(cols[4])
						score=float(cols[5])
						ginfo=gx,gy,gz,phi,score
						glist.append(ginfo)
				return glist
			else:
				i_wait+=1
				time.sleep(10.0)

			if i_wait > 12: # 2.0 minutes # not completed cleanly (EIGER dropped)
				if len(lines)==1:
					print "Oh my god!! No crystals!!"
					raise MyException("No crystals were found!")
				for line in lines[1:]:
					cols=line.split()
					if len(cols)==6:
						#print cols
						gx=float(cols[1])
						gy=float(cols[2])
						gz=float(cols[3])
						phi=float(cols[4])
						score=float(cols[5])
						ginfo=gx,gy,gz,phi,score
						glist.append(ginfo)
				return glist

if __name__ == "__main__":
	import MultiCrystal
	mc=MultiCrystal.MultiCrystal()

	sshika=SummarySHIKA("/isilon/users/target/target/Yokoyama/thori160622BL32XU/hori-1096-01/scan/_spotfinder/","hori-1096-01_")
	sshika.waitingForSummary()
	#glist=sshika.readSummary()
	#gxyz_only_list=[]
	#for gxyz in glist:
		#x,y,z,phi,score=gxyz
		#gxyz=x,y,z
		#gxyz_only_list.append(gxyz)
		#print "%9.5f %9.5f %9.5f %5.2f %5.1f"%(x,y,z,phi,score)

        #sch_file="./pppp.sch"
        #mc.makeSchStr(sch_file,gxyz_only_list)
	#mc.makeMulti(sch_file,gxyz_only_list)

