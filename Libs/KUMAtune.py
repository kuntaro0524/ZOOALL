import socket
import time
import datetime
import sys,os
import Device

class KUMAtune :
	def __init__(self):
		bglogname="TTT"
		basedir="/isilon/BL32XU/BLsoft/Logs/"
		# Beam position log
		self.bplogname="/isilon/BL32XU/BLsoft/Logs/beam.log"
		self.isInit=False

	def time_now(self):
		strtime=datetime.datetime.now().strftime("%H:%M:%S")
		return strtime

	def date_now(self):
		strtime=datetime.datetime.now().strftime("%Y%m%d-%H%M")
		return strtime

	def today(self):
		strtime=datetime.datetime.now().strftime("%Y%m%d")[2:]
		return strtime

	def time_str(self):
		strtime=datetime.datetime.now().strftime("%H%M")
		return strtime

	def prepTune(self):
		# Setting for logfile
		dirname="/isilon/BL32XU/BLsoft/Logs/%s/"%(self.today())
		try:
        		os.stat(dirname)
		except:
        		os.mkdir(dirname)
		# Change mode
		command="chmod a+rw -R %s"%dirname
		os.system(command)
	
		# Setting for logfile
		self.dirname="/isilon/BL32XU/BLsoft/Logs/%s/%s/"%(
        		self.today(),self.time_str())
		try:
        		os.stat(self.dirname)
		except:
        		os.mkdir(self.dirname)

		command="chmod a+rw -R %s"%self.dirname
		os.system(command)

		# Change wavelegnt
		#host = '192.168.163.1'
		host = '172.24.242.41'
		port = 10101
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host,port))
		self.devctr=Device.Device(s)

	def changeWL(self,wl):
		en=12.3984/wl # keV
		self.devctr.changeE(en)

	def getCurrentWL(self):
		en=self.devctr.getE()
		wl=12.3984/en # keV
		return wl

	def autoTune(self,wavelength=1.0):
		if self.isInit==False:
			self.prepTune()

		# change energy
		self.changeWL(wavelength)

		# Beam position log
		# KUMA should not write the beam position log file
		# Deleted 140616 by K.Hirata from Morning Tune
		# bplog=open(self.bplogname,"aw")
		# Morning log file
		tstr=datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
		fname="%s/MT_%s.dat"%(self.dirname,tstr)
		logf=open(fname,"w")
		dt_fwhm,dt_final=self.monoTune(logf)
		logf.write("Dtheta1 Peak=%5d FWHM=%8.3f\n"%(dt_final,dt_fwhm))

		# Prep camera, collimator
		self.tuneStage(logf)
		self.tuneCollimator(logf,wavelength)

		# Finish tuning
		self.devctr.finishExposure()
		self.devctr.allFin()
		logf.close()
		# Finally flag is OFF for the next tune
		self.isInit=False

	def monoTune(self,logf):
		# TCS aperture should be set to 0.1mm sq
		print("TCS is set to 0.1mm square")
		self.devctr.setTCSapert(0.1,0.1)

		# Dtheta1 tune : added on 140629 K.Hirata
		dt_fwhm,dt_final=self.devctr.dttunePeakE()
		return dt_fwhm,dt_final

	def tuneStage(self,logf,wait=30.0):
		#######################
		# Evacuate needle or pin
		#######################
		logf.write("Evacuate goniometer\n")
		sx,sy,sz=self.devctr.evacNeedle(15)

		# Scintillator set position
		self.devctr.prepBCtune()

		#######################
		# Wait for 180 sec
		#######################
		logf.write("Waiting for thermal equilibrium of scintillator stage\n")
		time.sleep(wait)

		# Open shutter
		self.devctr.prepScan()

		# ST-YZ tune
		ini_sty,curr_sty,ini_stz,curr_stz=self.devctr.stageYZtuneCapture()
		dy=(curr_sty-ini_sty)*1000.0 #[um]
		dz=(curr_stz-ini_stz)*1000.0 #[um]
		logf.write("%10s %10s Final Y=%10.4f Z=%10.4f (Dy,Dz)=(%8.2f,%8.2f)[um]\n"%(
			self.time_now(),"St-YZ tune",curr_sty,curr_stz,dy,dz))
		logf.flush()

		logf.write("%10s Capture analysis starts\n"%self.time_now())
		# picy,picz=mng.doCapAna("confirm") # 140711 K.Hirata modified
		picy,picz=self.devctr.doCapAna("morning",10,1,False)
		logf.write("%10s Capture analysis ends\n"%self.time_now())
		logf.write("%10s %10s code (Y,Z) = (%5d,%5d)\n"%(self.time_now(),"BeamCen",picy,picz))
		logf.flush()

		print("Remove beam monitor")
		# Finish (remove beam monitor)
		self.devctr.closeShutter()
		self.devctr.finishBCtune()
		# Gonio move
		self.devctr.moveXYZmm(sx,sy,sz)

	def tuneCollimator(self,logf,wavelength=1.0):
		print("Start collimator scan")
		# Collimator scan
        	self.devctr.prepScan()
		logstr=self.devctr.colliScan(wavelength=wavelength)
		logf.write("%s"%logstr)
		logf.flush()

	def tttt(self):
		#self.devctr.prepScan()
		#self.devctr.prepBCtune()
		#self.devctr.tuneAttThick()
		#self.devctr.tuneAttThick()
		print("DDDD")

if __name__=="__main__":
	kt=KUMAtune()
	kt.prepTune()
	kt.autoTune(wavelength=1.0000)
	#kt.tttt()
	#logf=open("./log.log","w")
	#kt.tuneCollimator(logf,1.2000)
