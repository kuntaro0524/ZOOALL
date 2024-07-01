import os
import sys
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/")
from pylab import *
from scipy import *
from Gauss import *
from AttFactor import *
import numpy
import scipy
import math

# FWHMs of RD profiles
#  1.0um  2.8 um
#  5.0um  7.8 um
# 10.0um 12.8 um
# Fitting line of (FWHM of RD profile)=1.106*beamsize+1.898 @ 12.3984 keV

class RDprop:
	def __init__(self,beamsize,hstep):
		self.beamsize=float(beamsize)
		self.hstep=float(hstep)
		self.isInit=False

	def setBeamsize(self,beamsize):
		self.beamsize=float(beamsize)

	def setHstep(self,hstep):
		self.hstep=float(hstep)

	def getAttFac(self,clt,nframe,wavelength):
		attfac=AttFactor()
		# CLT : 1.0 for FullFlux 1.0sec exposure
		ard=self.getARD()*float(nframe)
		trans=clt/ard
                thickness=attfac.calcThickness(wavelength,trans)

		return ard,trans,thickness

	def getARD(self):
		# beamsize -> RDprop distribution
		rd_fwhm=1.106*self.beamsize+1.898 # see above

		# RD propagation gaussian function
		gauss_rd=Gauss(20.0,0.0)
		gauss_rd.setSigmaFromFWHM(rd_fwhm)
		#print gauss_rd.getSig()

		# integration range 
		# 3*sigma covers 99.7% in gaussian distribution
		# Observed area(crystal volume) is -3sigma <= x <= +3sigma
		# origin is set to 0.0
		# IMPORTANT: this should be independent from the 
		# RD propagation gaussian function because volume illuminated
		# by the beam is not determined by RDP
		# Only to see the crystal region to be exposed at the
		# REAL exposure
		sigma=self.beamsize/2.35
		three_sigma=sigma*3.0
		intstart=-three_sigma
		intend=three_sigma 

		# Beam movements in helical data collection
		hstart=-60*self.hstep
		hend=0.0
		#print "HRANGE:",hstart,hend
		sum=0.0
		for offset in arange(hstart,hend+self.hstep,self.hstep):
			gauss_rd.setMu(offset)
			value=gauss_rd.integrate(intstart,intend)
			sum+=value
			#print "%5.2f %8.3f %8.3f"%(offset,value,sum)
			#gauss_rd.getGauss()
			#print ""
			#print ""
		sum+=1.0
		#print "%8.5f, %8.5f" %(self.hstep,sum)
		return sum

	# 2012/03/04 coded for RD7 preparation
        def virtualCrystal(self,length):
                # set 0.1um for integrating RDD (radiation damage decay)
                nstep=int(length/0.100000)

                # gauss
                gauss=Gauss(20.0,0.0)
                # beamsize -> RDprop distribution
                rd_fwhm=1.106*self.beamsize+1.898 # see above
                gauss.setSigmaFromFWHM(rd_fwhm)

                # virtual crystal volume array
                # center position
                vcry=[]
		dpd=[]
                for i in range(0,nstep):
			value=float(i+1)*0.1
			print value
                        vcry.append(value)
			dpd.append(0.0)

                # step movement of gaussian distribution
                for cen in arange(0,length,self.hstep):
                	gauss.setMu(cen)
                	#value=gauss_rd.integrate(intstart,intend)
			# for each beam position
			print "##### %8.3f #####"%cen

                	sum=0.0
			idx=0
                	for cryvol in vcry:
                        	area=gauss.calc(cryvol)*0.1
				print "AREA %12.5f"%area
				dpd[idx]+=area
                        	sum+=area
				idx+=1
                	print "SUM=:%8.5f"%sum

		for idx in arange(0,nstep):
			print "TEST %8.5f %8.5f"%(vcry[idx],dpd[idx])


if __name__=="__main__":
	beamsize=float(sys.argv[1])
	step=float(sys.argv[2])

	beamsize=1.0
	step=0.56
	rdp1=RDprop(beamsize,step)
	print "GET",rdp1.getARD()

	step=0.50
	rdp2=RDprop(beamsize,step)
	print "GET",rdp2.getARD()

        #bs_list=[1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0]
        #hs_list=arange(0.5,15.5,0.5)
	#for beamsize in bs_list:
		#for hstep in hs_list:
			#rdp.setBeamsize(beamsize)
			#rdp.setHstep(hstep)
			#print "%5.1f[um] %5.1f[um] %5.1f[um]"%(beamsize,hstep,rdp.getARD())
