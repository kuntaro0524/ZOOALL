#!/bin/env python 
import sys
import socket
import time
import datetime 

# My library
from Received import *
from Motor import *
from BSSconfig import *
from MyException import *

#
class Colli:
	def __init__(self,server):
		self.s=server
    		self.coly=Motor(self.s,"bl_32in_st2_collimator_1_y","pulse")
    		self.colz=Motor(self.s,"bl_32in_st2_collimator_1_z","pulse")
		
		self.off_pos=-60000 # pulse
		self.on_pos=0 # pulse
		
		self.y_v2p=500 # pulse/mm
		self.z_v2p=2000 # pulse/mm

		self.isInit=False

	def go(self,pvalue):
		self.colz.nageppa(pvalue)

        def getEvacuate(self):
                bssconf=BSSconfig()

                try:
                        tmpon,tmpoff=bssconf.getColli()
                except MyException,ttt:
                        print ttt.args[0]

                self.on_pos=float(tmpon)*self.z_v2p
                self.off_pos=float(tmpoff)*self.z_v2p

                self.isInit=True
                print self.on_pos,self.off_pos

	def getY(self):
                tmp=int(self.coly.getPosition()[0])
		return tmp

	def getZ(self):
                tmp=int(self.colz.getPosition()[0])
		return tmp
	
	def on(self):
		if self.isInit==False:
			self.getEvacuate()
		self.colz.move(self.on_pos)

	def off(self):
		if self.isInit==False:
			self.getEvacuate()
		self.colz.move(self.off_pos)

	def goOn(self):
		if self.isInit==False:
			self.getEvacuate()
		self.go(self.on_pos)

	def goOff(self):
		if self.isInit==False:
			self.getEvacuate()
		self.go(self.off_pos)

	def compareOnOff(self,ch):
		# counter initialization
                counter=Count(self.s,ch,0)

		# off position
		self.off()
		cnt_off=float(counter.getCount(1.0)[0])

		# on position
		self.on()
		cnt_on=float(counter.getCount(1.0)[0])

		# transmission
		trans=cnt_on/cnt_off*100.0

		return trans,cnt_on

	def scanCore(self,prefix,ch):
		ofile="%s_colliz.scn"%prefix
		before_zp=self.colz.getPosition()[0]
		before_zm=before_zp
		print "Current value=%8d\n"%before_zp

		###
		# Scan setting
		###
		cnt_ch=ch
		cnt_ch2=0
		cnt_time=0.1
		unit="pulse"

		####
		# Z scan condition [mm]
		####
		#scan_start=-0.25
		#scan_end=0.25
		#scan_step=0.005

		scan_start=-0.10
		scan_end=0.10
		scan_step=0.002

		####
		# Z scan condition [pulse]
		####
		scan_start_p=scan_start*self.z_v2p
		scan_end_p=scan_end*self.z_v2p
		scan_step_p=scan_step*self.z_v2p

		####
		# Set scan condition
		####
		self.colz.setStart(scan_start_p)
		self.colz.setEnd(scan_end_p)
		self.colz.setStep(scan_step_p)

        	self.colz.axisScan(ofile,cnt_ch,cnt_ch2,cnt_time)

        	# Analysis and Plot
        	outfig=prefix+"_colliz.png"
        	ana=AnalyzePeak(ofile)
                strtime=datetime.datetime.now()

		try :
                	fwhm,center=ana.analyzeAll("colliZ[pulse]","Intensity",outfig,strtime,"OBS","JJJJ")
			print fwhm,center
                	fwhm_z=fwhm/2.0 # [um]
		except MyException,ttt:
			self.colz.move(0)
			err_log01="%s\n"%ttt.args[0]
			err_log02="Collimetor Z scan failed\n"
			err_all=err_log01+err_log02
			raise MyException(err_all)

		print "setting collimeter Z"
		self.colz.move(center)
		self.colz.preset(0)
		print "setting collimeter Z"

		cenz=float(center)

		####
		# Y scan condition[mm]
		####
		scan_start=-0.1
		scan_end=0.1
		scan_step=0.002

		####
		# Y scan condition [pulse]
		####
		scan_start_p=scan_start*self.y_v2p
		scan_end_p=scan_end*self.y_v2p
		scan_step_p=scan_step*self.y_v2p

		####
		# Set scan condition
		####
		self.coly.setStart(scan_start_p)
		self.coly.setEnd(scan_end_p)
		self.coly.setStep(scan_step_p)

		ofile="%s_colliy.scn"%prefix
        	self.coly.axisScan(ofile,cnt_ch,cnt_ch2,cnt_time)

        	# Analysis and Plot
        	outfig=prefix+"_colliy.png"
        	ana=AnalyzePeak(ofile)
                strtime=datetime.datetime.now()

		try :
                	fwhm,center=ana.analyzeAll("colliY[pulse]","Intensity",outfig,strtime,"OBS","JJJJ")
                	fwhm_y=fwhm*2.0 # [um]
		except MyException,ttt:
			self.coly.move(0)
			err_log01="%s\n"%ttt.args[0]
			err_log02="Collimetor Y scan failed\n"
			err_all=err_log01+err_log02
			raise MyException(err_all)

		self.coly.move(center)
		self.coly.preset(0)
		ceny=float(center)

		print "FWHM Z:%8.2f[um] Y:%8.2f[um]"%(fwhm_z,fwhm_y)
		return fwhm_y,fwhm_z,ceny,cenz

        def scanWithoutPreset(self,prefix,ch,width_mm):
                ofile="%s_colliz.scn"%prefix

                before_zp=self.colz.getPosition()[0]
                before_zm=before_zp
                print "Current value=%8d\n"%before_zp

                ###
                # Scan setting
		

	def scan(self,prefix,ch):
		ofile="%s_colliz.scn"%prefix

		before_zp=self.colz.getPosition()[0]
		before_zm=before_zp
		print "Current value=%8d\n"%before_zp

		###
		# Scan setting
		###
		cnt_ch=ch
		cnt_ch2=0
		cnt_time=0.2
		unit="pulse"

		####
		# Z scan condition [mm]
		####
		#scan_start=-0.25
		#scan_end=0.25
		#scan_step=0.005

		scan_start=-0.10
		scan_end=0.10
		scan_step=0.002

		####
		# Z scan condition [pulse]
		####
		scan_start_p=scan_start*self.z_v2p
		scan_end_p=scan_end*self.z_v2p
		scan_step_p=scan_step*self.z_v2p

		####
		# Set scan condition
		####
		self.colz.setStart(scan_start_p)
		self.colz.setEnd(scan_end_p)
		self.colz.setStep(scan_step_p)

        	self.colz.axisScan(ofile,cnt_ch,cnt_ch2,cnt_time)

        	# Analysis and Plot
        	outfig=prefix+"_colliz.png"
        	ana=AnalyzePeak(ofile)
                strtime=datetime.datetime.now()

        	fwhm,center=ana.analyzeAll("colliZ[pulse]","Intensity",outfig,strtime,"OBS","JJJJ")
		fwhm_z=fwhm/2.0 # [um]
		self.colz.move(center)
		self.colz.preset(0)

		cenz=float(center)

		####
		# Y scan condition[mm]
		####
		scan_start=-0.1
		scan_end=0.1
		scan_step=0.002

		####
		# Y scan condition [pulse]
		####
		scan_start_p=scan_start*self.y_v2p
		scan_end_p=scan_end*self.y_v2p
		scan_step_p=scan_step*self.y_v2p

		####
		# Set scan condition
		####
		self.coly.setStart(scan_start_p)
		self.coly.setEnd(scan_end_p)
		self.coly.setStep(scan_step_p)

		ofile="%s_colliy.scn"%prefix
        	self.coly.axisScan(ofile,cnt_ch,cnt_ch2,cnt_time)

        	# Analysis and Plot
        	outfig=prefix+"_colliy.png"
        	ana=AnalyzePeak(ofile)
                strtime=datetime.datetime.now()

        	fwhm,center=ana.analyzeAll("colliY[pulse]","Intensity",outfig,strtime,"OBS","JJJJ")
		fwhm_y=fwhm*2.0 # [um]
		self.coly.move(center)
		self.coly.preset(0)
		ceny=float(center)

		print "FWHM Z:%8.2f[um] Y:%8.2f[um]"%(fwhm_z,fwhm_y)
		return ceny,cenz

        def scanWithoutPreset(self,prefix,ch,width_mm):
                ofile="%s_colliz.scn"%prefix

                before_zp=self.colz.getPosition()[0]
                before_zm=before_zp
                print "Current value=%8d\n"%before_zp

                ###
                # Scan setting
                ###
                cnt_ch=ch
                cnt_ch2=1
                cnt_time=0.2
                unit="pulse"

                ####
                # Z scan condition [mm]
                ####
                scan_start=-width_mm
                scan_end=width_mm
                scan_step=0.002

                ####
                # Z scan condition [pulse]
                ####
                scan_start_p=scan_start*self.z_v2p
                scan_end_p=scan_end*self.z_v2p
                scan_step_p=scan_step*self.z_v2p

                ####
                # Set scan condition
                ####
                self.colz.setStart(scan_start_p)
                self.colz.setEnd(scan_end_p)
                self.colz.setStep(scan_step_p)

                self.colz.axisScan(ofile,cnt_ch,cnt_ch2,cnt_time)

                # Analysis and Plot
                outfig=prefix+"_colliz.png"
                ana=AnalyzePeak(ofile)
                strtime=datetime.datetime.now()

		try :
                	fwhm,center=ana.analyzeAll("colliZ[pulse]","Intensity",outfig,strtime,"OBS","JJJJ")
                	fwhm_z=fwhm/2.0 # [um]
		except MyException,ttt:
			print "Collimeter scan failed"
			print ttt.args[0]
			return 0,0,30,30

                self.colz.move(center)
                cenz=float(center)

                ####
                # Y scan condition[mm]
                ####
                scan_start=-width_mm
                scan_end=width_mm
                scan_step=0.002

                ####
                # Y scan condition [pulse]
                ####
                scan_start_p=scan_start*self.y_v2p
                scan_end_p=scan_end*self.y_v2p
                scan_step_p=scan_step*self.y_v2p

                ####
                # Set scan condition
                ####
                self.coly.setStart(scan_start_p)
                self.coly.setEnd(scan_end_p)
                self.coly.setStep(scan_step_p)

                ofile="%s_colliy.scn"%prefix
                self.coly.axisScan(ofile,cnt_ch,cnt_ch2,cnt_time)

                # Analysis and Plot
                outfig=prefix+"_colliy.png"
                ana=AnalyzePeak(ofile)
                strtime=datetime.datetime.now()

                fwhm,center=ana.analyzeAll("colliY[pulse]","Intensity",outfig,strtime,"OBS","JJJJ")
                fwhm_y=fwhm*2.0 # [um]
                self.coly.move(center)
                ceny=float(center)

                #print "FWHM Z:%8.2f[um] Y:%8.2f[um]"%(fwhm_z,fwhm_y)
		try :
                	fwhm,center=ana.analyzeAll("colliY[pulse]","Intensity",outfig,strtime,"OBS","JJJJ")
                	fwhm_y=fwhm*2.0 # [um]
		except MyException,ttt:
			print "Collimeter scan failed"
			print ttt.args[0]
			return 0,0,30,30

                return ceny,cenz,fwhm_z,fwhm_y

        def moveY(self,pls):
                v=pls
                self.coly.move(v)

        def moveZ(self,pls):
                v=pls
                self.colz.move(v)

        def scan2D(self,prefix,startz,endz,stepz,starty,endy,stepy):
                counter=Count(self.s,3,0)
                oname="%s_colli_2d.scn"%prefix
                of=open(oname,"w")

		save_y=self.getY()
		save_z=self.getZ()

		print save_y,save_z

                for z in arange(startz,endz+stepz,stepz):
                        self.moveZ(z)
                        for y in range(starty,endy+stepy,stepy):
                                self.moveY(y)
                                cnt=int(counter.getCount(0.2)[0])
                                of.write("%5d %5d %12d\n"%(y,z,cnt))
                                of.flush()
                        of.write("\n")
                of.close()

		self.moveY(save_y)
		self.moveZ(save_z)


        def isMoved(self):
                isY=self.coly.isMoved()
                isZ=self.colz.isMoved()

                if isY==0 and isZ==0:
                        return True
                if isY==1 and isZ==1:
                        return False


if __name__=="__main__":
	host = '172.24.242.41'
	port = 10101

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))

	coli=Colli(s)
	#coli.getEvacuate()
	#coli.off()
	#coli.scan("colllli",0)

	#print coli.getY()
	#coli.moveZ(1000)
	#coli.moveZ(0)
	#coli.scan2D()
	#coli.scanCore("test",3)
	print(coli.getY())
	#coli.on()
	#coli.off()
        #def scan2D(self,prefix,startz,endz,stepz,starty,endy,stepy):
	#coli.goOff()
	s.close()
