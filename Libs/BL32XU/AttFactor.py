import sys
import socket
import time
import math
from numpy import *

class AttFactor:
	def __init__(self,config_file="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/bss/bss.config"):
		dummy=1
		self.isInit=False
		
	def cnFactor(self,wl):
		cnfac=0.028*math.pow(wl,5)-0.188*math.pow(wl,4)+0.493*math.pow(wl,3)-0.633*math.pow(wl,2)+0.416*math.pow(wl,1)+0.268
		return cnfac

	def calcMu(self,wl,cnfac):
		mu=38.851*math.pow(wl,3)-2.166*math.pow(wl,4)+1.3*cnfac
		return mu

	def calcAttFac(self,wl,thickness,material="Al"):
		# thickness [um]
		if material=="Al":
			cnfac=self.cnFactor(wl)
			mu=self.calcMu(wl,cnfac)
			attfac=math.exp(-mu*thickness/10000)
			return attfac
		else:
			return -1

	# 2017/07/30 temporarly coded for round robin experiments
	# The list includes 'observed transmission' for each attenuator 
	# thickness.
	def getAttFacObs(self,wl,thickness,material="Al"):
		trans_dict={}
		att_1A_list=[(0.0,1.0),
			(100,0.75665000),
			(150,0.51251000),
			(200,0.42646000),
			(250,0.36450000),
			(300,0.30556000),
			(350,0.25597000),
			(400,0.21321000),
			(450,0.17684000),
			(500,0.14668000),
			(550,0.12115000),
			(600,0.10074000),
			(650,0.08238000),
			(700,0.06808000),
			(750,0.05642000),
			(800,0.04632000),
			(850,0.03817000),
			(900,0.03120000),
			(950,0.02539109),
			(1000,0.02094779),
			(1100,0.01395710),
			(1200,0.00926078),
			(1300,0.00606512),
			(1400,0.00400391),
			(1500,0.00265436),
			(1600,0.00174093),
			(1700,0.00114660),
			(1800,0.00075670),
			(2000,0.00032176),
			(2500,0.00003615),
			(3000,0.00000356)]

		for each_compo in att_1A_list:
			thick,trans=each_compo
                	trans_dict[thick]=trans

		attfac=trans_dict[thickness]
		return attfac

	def calcThickness(self,wl,transmission,material="Al"):
		# thickness [um]
		print "Trans=",transmission
		if material=="Al":
			cnfac=self.cnFactor(wl)
			mu=self.calcMu(wl,cnfac)
			thickness=(-1.0*math.log(transmission)/mu)*10000
			return thickness
		else:
			return -1

	def getBestAtt(self,wl,transmission):
		print transmission
		if self.isInit == False:
			self.readAttConfig()

		cnfac=self.cnFactor(wl)
		mu=self.calcMu(wl,cnfac)
		thickness=(-1.0*math.log(transmission)/mu)*10000

		print "IDEAL thickness: %8.3f[um]"%thickness

		if thickness <= 0.0:
			return 0.0
		for att in self.att_thick:
			if thickness < att:
				return att

	# 150528 Mainly for shutterless measurement
	# wl		: wavelength
	# transmission	: transmission
	# exptime	: intended exposure time for each frame
	def chooseBestConditions(self,wl,transmission,exptime):
		if self.isInit == False:
			self.readAttConfig()

		cnfac=self.cnFactor(wl)
		mu=self.calcMu(wl,cnfac)
		real_transmission=transmission/exptime

		while (1):
			# The first estimation of the transmission by the defined 'exptime'
			thickness=self.calcThickness(wl,real_transmission)
			print thickness,exptime

			if thickness<0.0:
				exptime+=0.01
				print "Exptime=",exptime
			else:
				break

		print "Exposure time:",exptime
		bestatt=self.getBestAtt(wl,real_transmission)
		attfac=self.calcAttFac(wl,bestatt)
		print "BESTATT/ATTFAC=",bestatt,attfac

		ppp=real_transmission/attfac
		final_exptime=exptime*ppp
		print "Final exposure time:",final_exptime

		print attfac*final_exptime,real_transmission

		#for att in self.att_thick:
			#if thickness < att:
				#return att

	def readAttConfig(self):
		self.bssconfig="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/bss/bss.config"
		#self.bssconfig="./bss.config"
		confile=open(self.bssconfig,"r")
		lines=confile.readlines()
		confile.close()

		self.att_idx=[]
		self.att_thick=[]

		for line in lines:
			if line.find("Attenuator_Menu_Label")!=-1:
				line=line.replace("[","").replace("]","").replace("{","").replace("}","")
				cols=line.split()
				ncols=len(cols)
				if ncols == 4:
					if cols[2].find("um")!=-1:
						tmp_thick=float(cols[2].replace("um",""))
						tmp_attidx=int(cols[3])
						# storage
						self.att_idx.append(tmp_attidx)
						self.att_thick.append(tmp_thick)

		self.att_idx=array(self.att_idx)
		self.att_thick=array(self.att_thick)

		# DEBUG
		#for i,thick in zip(self.att_idx,self.att_thick):
			#print i,thick

		# flag on
		self.isInit=True

	def getAttIndexConfig(self,t):
		if self.isInit == False:
			self.readAttConfig()
		if t<=0.0:
			return 0
		for i,thick in zip(self.att_idx,self.att_thick):
			if thick==t:
				return i
		print "Something wrong: No attenuator at this beamline"
		return -9999

if __name__=="__main__":
	att=AttFactor()

        print att.getAttFacObs(1.0,600)

	#best_thick=att.getBestAtt(1.0,float(sys.argv[1]))
	#print best_thick
	#def calcThickness(self,wl,transmission,material="Al"):
	#print best_thick,att.calcAttFac(1.0,best_thick)
	#def calcAttFac(self,wl,thickness,material="Al"):
	#def getBestAtt(self,wl,transmission):
        #print ick,att.getAttIndexConfig(best_thick)
	#print att.getAttIndexConfig(1200)
