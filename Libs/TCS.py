#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *
from AnalyzePeak import *
from AxesInfo import *
import BaseAxis

class TCS:
    def __init__(self,server):
        # TCS axis
        # axis name on 'beamline.ini'
        tcs_height_class = BaseAxis.BaseAxis(server, "tcs_height", axis_type="motor")
        tcs_width_class = BaseAxis.BaseAxis(server, "tcs_width", axis_type="motor")
        tcs_vert_class = BaseAxis.BaseAxis(server, "tcs_vert", axis_type="motor")
        tcs_hori_class = BaseAxis.BaseAxis(server, "tcs_hori", axis_type="motor")

        self.tcs_height=tcs_height_class.motor
        self.tcs_width=tcs_width_class.motor
        self.tcs_vert=tcs_vert_class.motor
        self.tcs_hori=tcs_hori_class.motor

    def saveInit(self):
        self.getApert()
        self.getPosition()

    def getApert(self):
        # get values
        self.ini_height=self.tcs_height.getApert()
        self.ini_width=self.tcs_width.getApert()
        return float(self.ini_height[0]),float(self.ini_width[0])

    def getPosition(self):
        # get values
        vert=self.tcs_vert.getPosition()[0]
        hori=self.tcs_hori.getPosition()[0]
        return vert,hori

    def setPosition(self,vert,hori):
        # get values
        self.tcs_vert.move(vert)
        self.tcs_hori.move(hori)

    def setApert(self,height,width):
        self.tcs_height.move(height)
        self.tcs_width.move(width)
        print("current tcs aperture : %8.5f %8.5f\n" %(height,width))

    def scanBoth(self,prefix,scan_width,another_width,start,end,step,cnt_ch1,cnt_ch2,time):
        vfwhm,vcenter=self.scanV(prefix,scan_width,another_width,start,end,step,cnt_ch1,cnt_ch2,time)
        hfhwm,hcenter=self.scanH(prefix,another_width,scan_width,start,end,step,cnt_ch1,cnt_ch2,time)

        return vcenter,hcenter

    def scanVrel(self,prefix,height,width,swidth,step,cnt_ch1,cnt_ch2,time):
        curr_pos=self.tcs_vert.getPosition()[0]
        half_width=fabs(float(swidth))/2.0

        start=curr_pos-half_width
        end=curr_pos+half_width
        fwhm,center=self.scanV(prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time)

        return fwhm,center

    def scanHrel(self,prefix,height,width,swidth,step,cnt_ch1,cnt_ch2,time):
        curr_pos=self.tcs_hori.getPosition()[0]
        half_width=fabs(float(swidth))/2.0

        start=curr_pos-half_width
        end=curr_pos+half_width
        fwhm,center=self.scanH(prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time)
        
        return fwhm,center

    def scanV(self,prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time):
        # Vertical scan setting
        ofile=prefix+"_tcs_vert.scn"
    
        # Aperture setting
        self.setApert(height,width)

        # Scan setting 
        self.tcs_vert.setStart(start)
        self.tcs_vert.setEnd(end)
        self.tcs_vert.setStep(step)

        self.tcs_vert.axisScan(ofile,cnt_ch1,cnt_ch2,time)

        # AnalyzePeak
        ana=AnalyzePeak(ofile)
        outfig=prefix+"_tcs_vert.png"

        comment=AxesInfo(self.s).getLeastInfo()
        fwhm,center=ana.analyzeAll("TCS vert[mm]","Intensity",outfig,comment,"OBS")

        self.tcs_vert.move(center)
        print("Final position: %smm" % (center))
        return fwhm,center

    def scanH(self,prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time):
        # Horizontal scan setting
        ofile=prefix+"_tcs_hori.scn"

        # Aperture setting
        self.setApert(height,width)

        # Scan setting 
        self.tcs_hori.setStart(start)
        self.tcs_hori.setEnd(end)
        self.tcs_hori.setStep(step)
        
        self.tcs_hori.axisScan(ofile,cnt_ch1,cnt_ch2,time)

        # AnalyzePeak
        ana=AnalyzePeak(ofile)
        outfig=prefix+"_tcs_hori.png"

        comment=AxesInfo(self.s).getLeastInfo()
        fwhm,center=ana.analyzeAll("TCS hori[mm]","Intensity",outfig,comment,"OBS")

        self.tcs_hori.move(center)

        return fwhm,center

    def checkZeroV(self,prefix,start,end,step,cnt_ch1,cnt_ch2,time):
        # Counter
        counter=Count(self.s,cnt_ch1,cnt_ch2)
        # Setting aperture
        self.setApert(1.00,1.00)
        ofile=prefix+"_vert_zero.scn"

        scan_start=start
        scan_end=end
        scan_step=step
        cnt_time=time

        ndata=int((scan_end-scan_start)/scan_step)+1
        if ndata <=0 :
            print("Set correct scan step!!\n")
            return 1

        outfile=open(ofile,"w")

        for x in range(0,ndata):
            value=scan_start+x*scan_step
            self.setApert(value,1.0)
            count1,count2=counter.getCount(cnt_time)
            count1=float(count1)
            count2=float(count2)
            outfile.write("%12.5f %12.5f %12.5f\n"%(value,count1,count2))

        self.setApert(1.0,1.0)
        return 1

    def checkZeroH(self,prefix,start,end,step,cnt_ch1,cnt_ch2,time):
        # Counter
        counter=Count(self.s,cnt_ch1,cnt_ch2)

        # Setting aperture
        self.setApert(1.0,1.0)

        ofile=prefix+"_hori_zero.scn"

        scan_start=start
        scan_end=end
        scan_step=step
        cnt_time=time
        unit="mm"

        ndata=int((scan_end-scan_start)/scan_step)+1
        if ndata <=0 :
            print("Something wrong")
            return 1

        outfile=open(ofile,"w")

        for x in range(0,ndata):
            value=scan_start+x*scan_step
            self.setApert(1.0,value)
            count1,count2=counter.getCount(cnt_time)
            count1=float(count1)
            count2=float(count2)
            outfile.write("%12.5f %12.5f %12.5f\n"%(value,count1,count2))

        self.setApert(1.0,1.0)
        return 1

    def scan2d(self,prefix,width,step,cnt_ch1,cnt_ch2,time):
        # save current position
        self.saveCurr()
        counter=Count(self.s,cnt_ch1,cnt_ch2)
        # Setting aperture
        self.setApert(0.05,0.05)
        ofile=prefix+"_test.scn"
        minus=-width/2.0
        plus=width/2.0

        # Current position
        scan_start=start
        scan_end=end
        scan_step=step
        cnt_time=time
        unit="mm"

        ndata=int((scan_end-scan_start)/scan_step)+1
        if ndata <=0 :
            print("Something wrong")
            return 1

        outfile=open(ofile,"w")

        for x in range(0,ndata):
            value=scan_start+x*scan_step
            self.setApert(1.0,value)
            count1,count2=counter.getCount(cnt_time)
            count1=float(count1)
            count2=float(count2)
            outfile.write("%12.5f %12.5f %12.5f\n"%(value,count1,count2))

        self.setApert(1.0,1.0)
        return 1

if __name__=="__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    tcs=TCS(s)

    #tcs.checkZeroV("TEST",1.0,0.5,-0.1,0.2,1)

    #tcs.getApert()
    #tcs.setApert(0.1,0.1)
    #tcs.setPosition(1.000,-1.000)

    #tcs.scanBoth("VVVV",0.05,0.50,-1.0,1.0,0.05,0,1,0.2)
    #def scanVrel(self,prefix,height,width,swidth,cnt_ch1,cnt_ch2,time):
    vsave,hsave=tcs.getPosition()
    print(vsave,hsave)
    #tcs.scanVrel("test",0.05,0.50,1.0,0.05,0,1,0.2)
    tcs.scanHrel("test",0.50,0.05,1.0,0.05,0,1,0.2)

    tcs.setPosition(vsave,hsave)

    #tcs.setPosition(0.00052,0.00302)
    #prefix=raw_input()
        #tcs.checkZeroH("TEST",1.0,0.1,-0.1,1,2,0.2)
        #tcs.checkZeroV("TEST",1.0,0.1,-0.1,1,2,0.2)
    #def checkZeroH(self,prefix,start,end,step,time,cnt_ch1):

    s.close()
