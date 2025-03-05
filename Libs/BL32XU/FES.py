import sys
import socket
import time
import math

# My library
from Motor import *
from AnalyzePeak import *
from AxesInfo import *
from Count import *

class FES:

	def __init__(self,server):
		self.s=server
    		self.fes_height=Motor(self.s,"bl_32in_fe_slit_1_height","mm")
    		self.fes_width=Motor(self.s,"bl_32in_fe_slit_1_width","mm")
    		self.fes_vert=Motor(self.s,"bl_32in_fe_slit_1_vertical","mm")
    		self.fes_hori=Motor(self.s,"bl_32in_fe_slit_1_horizontal","mm")

	def getApert(self):
		# get values
		self.ini_height=self.fes_height.getApert()
		self.ini_width=self.fes_width.getApert()
		return self.ini_height,self.ini_width

	def getPosition(self):
		curr_vert=self.fes_vert.getPosition()
		curr_hori=self.fes_hori.getPosition()
		return curr_vert,curr_hori

	def setPosition(self,vert,hori):
		# get values
    		self.fes_vert.move(vert)
    		self.fes_hori.move(hori)

	def setApert(self,height,width):
		self.fes_height.move(height)
		self.fes_width.move(width)
		print "current fes aperture : %8.5f %8.5f\n" %(height,width)

	def scanBothNoAnal(self,prefix,scan_width,another_width,start,end,step,cnt_ch1,cnt_ch2,time):
		self.scanVNoAnal(prefix,scan_width,another_width,start,end,step,cnt_ch1,cnt_ch2,time)
		self.scanHNoAnal(prefix,another_width,scan_width,start,end,step,cnt_ch1,cnt_ch2,time)

	def scanBoth(self,prefix,scan_width,another_width,start,end,step,cnt_ch1,cnt_ch2,time):
		self.scanV(prefix,scan_width,another_width,start,end,step,cnt_ch1,cnt_ch2,time)
		self.scanH(prefix,another_width,scan_width,start,end,step,cnt_ch1,cnt_ch2,time)

	def dummy(self):
		ax=AxesInfo(self.s)
		comment=ax.getLeastInfo()
		sys.exit(1)

	def scanV(self,prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time):
		# Vertical scan setting
    		ofile=prefix+"_fes_vert.scn"
	
		# Aperture setting
		self.setApert(height,width)

		# Scan setting 
		self.fes_vert.setStart(start)
		self.fes_vert.setEnd(end)
		self.fes_vert.setStep(step)

    		self.fes_vert.axisScan(ofile,cnt_ch1,cnt_ch2,time)

		# Analysis and Plot
        	ana=AnalyzePeak(ofile)
		comment=AxesInfo(self.s).getLeastInfo()
		#comment="during debugging : sorry...\n"
                outfig=prefix+"_fes_vert.png"

		fwhm,center=ana.analyzeAll("FES-v[mm]","Intensity",outfig,comment)
		center=round(center,4)
        	self.fes_vert.move(center)

        	print "Final position: %smm" % center
		# Aperture setting
		self.setApert(0.3,0.3)

		return fwhm,center

	def scanH(self,prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time):
		# Horizontal scan setting
    		ofile=prefix+"_fes_hori.scn"

		# Aperture setting
		self.setApert(height,width)

		# Scan setting 
		self.fes_hori.setStart(start)
		self.fes_hori.setEnd(end)
		self.fes_hori.setStep(step)
		
    		self.fes_hori.axisScan(ofile,cnt_ch1,cnt_ch2,time)

                # Analysis and Plot
                ana=AnalyzePeak(ofile)
		#comment="during debugging : sorry...\n"
                comment=AxesInfo(self.s).getLeastInfo()
                outfig=prefix+"_fes_hori.png"

                fwhm,center=ana.analyzeAll("FES-h[mm]","Intensity",outfig,comment)
                center=round(center,4)
                self.fes_hori.move(center)

                print "Final position: %smm" % center
		self.setApert(0.3,0.3)

		return fwhm,center
		
	def scanVNoAnal(self,prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time):
		# Vertical scan setting
    		ofile=prefix+"_fes_vert.scn"

		# Get Current Position
		curr_vert,curr_hori = self.getPosition()
	
		# Aperture setting
		self.setApert(height,width)

		# Scan setting 
		self.fes_vert.setStart(start)
		self.fes_vert.setEnd(end)
		self.fes_vert.setStep(step)

    		self.fes_vert.axisScan(ofile,cnt_ch1,cnt_ch2,time)

		# Analysis and Plot
#        	ana=AnalyzePeak(ofile)
#		comment=AxesInfo(self.s).getLeastInfo()
		#comment="during debugging : sorry...\n"
#                outfig=prefix+"_fes_vert.png"

#		fwhm,center=ana.analyzeAll("FES-v[mm]","Intensity",outfig,comment)
#		center=round(center,4)
#        	self.fes_vert.move(center)

#        	print "Final position: %smm" % center
		# Aperture setting
		self.setApert(0.3,0.3)

#		return fwhm,center

	def scanHNoAnal(self,prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time):
		# Horizontal scan setting
    		ofile=prefix+"_fes_hori.scn"

		# Get Current Position
		curr_vert,curr_hori = self.getPosition()

		# Aperture setting
		self.setApert(height,width)

		# Scan setting 
		self.fes_hori.setStart(start)
		self.fes_hori.setEnd(end)
		self.fes_hori.setStep(step)
		
    		self.fes_hori.axisScan(ofile,cnt_ch1,cnt_ch2,time)

                # Analysis and Plot
#                ana=AnalyzePeak(ofile)
		#comment="during debugging : sorry...\n"
#                comment=AxesInfo(self.s).getLeastInfo()
#                outfig=prefix+"_fes_hori.png"

#                fwhm,center=ana.analyzeAll("FES-h[mm]","Intensity",outfig,comment)
#                center=round(center,4)
#         	self.fes_hori.move(center)

#                print "Final position: %smm" % center
		self.setApert(0.3,0.3)

#		return fwhm,center
		
	def checkZeroV(self,prefix,start,end,step,cnt_ch1,cnt_ch2,time):
		# Counter
		counter=Count(self.s,cnt_ch1,cnt_ch2)

		# Setting aperture
		self.setApert(0.50,0.50)

		ofile=prefix+"_vert_zero.scn"

    		scan_start=start
    		scan_end=end
    		scan_step=step
    		cnt_time=time

		ndata=int((scan_end-scan_start)/scan_step)+1
		if ndata <=0 :
			print "Set correct scan step!!\n"
			return 1

		outfile=open(ofile,"w")

		for x in range(0,ndata):
			value=scan_start+x*scan_step
			self.setApert(value,0.5)
			count1,count2=counter.getCount(cnt_time)
			count1=float(count1)
			count2=float(count2)
			outfile.write("%12.5f %12.5f %12.5f\n"%(value,count1,count2))

		self.setApert(0.5,0.5)
		return 1

	def checkZeroH(self,prefix,start,end,step,cnt_ch1,cnt_ch2,time):

		# Counter
		counter=Count(self.s,cnt_ch1,cnt_ch2)

		self.setApert(0.5,0.5)

		ofile=prefix+"_hori_zero.scn"
    		scan_start=start
    		scan_end=end
    		scan_step=step
    		cnt_time=time
    		unit="mm"

		ndata=int((scan_end-scan_start)/scan_step)+1
		if ndata <=0 :
			print "Something wrong"
			return 1

		outfile=open(ofile,"w")

		for x in range(0,ndata):
			value=scan_start+x*scan_step
			self.setApert(0.5,value)
			count1,count2=counter.getCount(cnt_time)
			count1=float(count1)
			count2=float(count2)
			outfile.write("%12.5f %12.5f %12.5f\n"%(value,count1,count2))

		self.setApert(0.5,0.5)
		return 1

if __name__=="__main__":
        host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

        fes=FES(s)

	fes.setPosition(0.42917, 0.22554)


        s.close()
