#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *
from AnalyzePeak import *
from AxesInfo import *

class TCS:
    # tcslit in opt hutch
    def __init__(self, server):
        self.s = server
        self.tcs_width = Motor(self.s, "bl_45in_tc1_slit_2_width", "mm")
        self.tcs_hori = Motor(self.s, "bl_45in_tc1_slit_2_horizontal", "mm")
        self.tcs_x = Motor(self.s, "bl_45in_tc1_slit_2_x", "pulse")

        # each blade
        self.tcs_ring = Motor(self.s, "bl_45in_tc1_slit_2_ring", "mm")
        self.tcs_hall = Motor(self.s, "bl_45in_tc1_slit_2_hall", "mm")

        # pulse2mm
        self.p2mm_tcsx = 1000.0

    def saveInit(self):
        self.getApert()
        self.getPosition()

    def getTest(self):
        ring_pos = self.tcs_ring.getPosition()[0]
        hall_pos = self.tcs_hall.getPosition()[0]

        print ring_pos, hall_pos

    def setTest2(self):
        # RING BLADE
        self.tcs_ring.move(-15000)
        self.tcs_ring.move(-16000)

    def getApert(self):
        # get values
        self.ini_width=self.tcs_width.getApert()
        return float(self.ini_width[0])

    def getPosition(self):
        # get values
        hori = self.tcs_hori.getPosition()[0]
        return hori

    def getTrans(self):
        x=self.tcs_x.getPosition()[0]/self.p2mm_tcsx
        return x

    def setTrans(self,abspos_mm):
        abs_pulse = abspos_mm * self.p2mm_tcsx
        self.tcs_x.move(abs_pulse)
        self.getTrans()
        return True

    def setPosition(self,vert,hori):
        # get values
        self.tcs_hori.move(vert)
        self.tcs_x.move(hori)

    def setApert(self,width):
        self.tcs_width.move(width)
        print "current tcs aperture : %8.5f\n" %(width)

    def scanBoth(self,prefix,scan_width,another_width,start,end,step,cnt_ch1,cnt_ch2,time):
        vfwhm,vcenter=self.scanV(prefix,scan_width,another_width,start,end,step,cnt_ch1,cnt_ch2,time)
        hfhwm,hcenter=self.scanH(prefix,another_width,scan_width,start,end,step,cnt_ch1,cnt_ch2,time)

        return vcenter,hcenter

    def scanVrel(self,prefix,height,width,swidth,step,cnt_ch1,cnt_ch2,time):
        curr_pos=self.tcs_hori.getPosition()[0]
        half_width=fabs(float(swidth))/2.0

        start=curr_pos-half_width
        end=curr_pos+half_width
        fwhm,center=self.scanV(prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time)

        return fwhm,center

    def scanHrel(self,prefix,height,width,swidth,step,cnt_ch1,cnt_ch2,time):
        curr_pos=self.tcs_x.getPosition()[0]
        half_width=fabs(float(swidth))/2.0

        start=curr_pos-half_width
        end=curr_pos+half_width
        fwhm,center=self.scanH(prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time)

        return fwhm,center

    def scanH(self,prefix,height,width,start,end,step,cnt_ch1,cnt_ch2,time):
        # Horizontal scan setting
        ofile=prefix+"_tcs_x.scn"

        # Aperture setting
        self.setApert(height,width)

        # Scan setting
        self.tcs_x.setStart(start)
        self.tcs_x.setEnd(end)
        self.tcs_x.setStep(step)

        self.tcs_x.axisScan(ofile,cnt_ch1,cnt_ch2,time)

        # AnalyzePeak
        ana=AnalyzePeak(ofile)
        outfig=prefix+"_tcs_x.png"

        comment=AxesInfo(self.s).getLeastInfo()
        fwhm,center=ana.analyzeAll("TCS hori[mm]","Intensity",outfig,comment,"OBS")

        self.tcs_x.move(center)
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
            print "Set correct scan step!!\n"
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
        self.setApert(1.0)

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
            self.setApert(value)
            count1,count2=counter.getCount(cnt_time)
            count1=float(count1)
            count2=float(count2)
            outfile.write("%12.5f %12.5f %12.5f\n"%(value,count1,count2))

        self.setApert(1.0)
        return 1

    def scan2d(self,prefix,width,step,cnt_ch1,cnt_ch2,time):
        # save current position
        self.saveCurr()
        # Counter
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
            print "Something wrong"
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
        host = '172.24.242.59'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

        tcs=TCS(s)
        apert= tcs.getApert()
        hori = tcs.getPosition()
        x= tcs.getTrans()
        tcs.setApert(6.0)
        #tcs.setTrans(10.0)
        print hori,apert,x

        s.close()
