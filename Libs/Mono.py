#!/bin/env python 
import sys
import socket
import time

# My library
from AnalyzePeak import *
from Motor import *
from AxesInfo import *
from ConfigFile import *
from MyException import *

class Mono:
 
    def __init__(self,srv):
        self.m_dtheta1=Motor(srv,"bl_45in_tc1_mono_1_dtheta","pulse")
        self.m_energy=Motor(srv,"bl_45in_tc1_mono_1","kev")
        self.m_theta=Motor(srv,"bl_45in_tc1_mono_1_theta","angle")
        #self.m_wave=  Motor(srv,"bl_45in_tc1_mono_1","angstrom")
        #self.m_theta=Motor(srv,"bl_45in_tc1_mono_1_dtheta","pulse")
        #self.m_theta=Motor(srv,"bl_45in_tc1_mono_1_dtheta","pulse")
        #self.m_energy=Motor(srv,"bl_45in_tc1_stmono_1","kev")
        self.s=srv
        self.BL = "bl45xu"

    def setBL(self,BL):
        # komoji
        self.BL = BL.lower()
        if self.BL != "bl45xu":
            print "Mono: unknown beamline!!!"

    def getE(self):
        return(self.m_energy.getEnergy()[0])

    def getTheta(self):
        return(self.m_theta.getPosition()[0])

    def getDt1(self):
        return(int(self.m_dtheta1.getPosition()[0]))

    def changeE(self,energy):
        self.m_energy.move(energy)

    def changeWL(self,wavelength):
        energy = 12.3984 / wavelength
        self.m_energy.move(energy)

    def moveDt1(self,position):
        self.m_dtheta1.move(position)

    def moveDt1withBL(self,position):
        back_l = -2000
        back_pos = position + back_l
        self.m_dtheta1.move(back_pos)
        self.m_dtheta1.move(position)

    def moveDt1Rel(self,value):
        self.m_dtheta1.relmove(value)

    def moveTy1(self,position):
        self.m_thetay1.move(position)

    def moveZ2(self,position):
        self.m_z2.move(position)

    def moveZt(self,position):
        if position < -5000 or position > 5000:
            print "Zt error!"
            return False

        self.m_zt.move(position)

    def scanEnergy(self,prefix,start,end,step,cnt_ch1,cnt_ch2,time):
        # Setting
        ofile=prefix+"_escan.scn"

        # Condition
        self.m_energy.setStart(start)
        self.m_energy.setEnd(end)
        self.m_energy.setStep(step)
        maxval=self.m_energy.axisScan(ofile,cnt_ch1,cnt_ch2,time)

    def scanDt1(self,prefix,start,end,step,cnt_ch1,cnt_ch2,time):
        # Setting
        ofile=prefix+"_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        maxval=self.m_dtheta1.axisScan(ofile,cnt_ch1,cnt_ch2,time)

        # Analysis and Plot
        outfig=prefix+"_dtheta1.png"
        ana=AnalyzePeak(ofile)
        comment=AxesInfo(self.s).getLeastInfo()
        #comment="during debugging : sorry...\n"

        fwhm,center=ana.analyzeAll("dtheta1[pulse]","Intensity",outfig,comment,"OBS","FCEN")

        self.m_dtheta1.move(int(center))
        return fwhm,center

    def scanDt1Peak(self,prefix,start,end,step,cnt_ch1,cnt_ch2,sec):
        # Setting
        ofile=prefix+"_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        backlash=2000

        maxval=self.m_dtheta1.axisScan(ofile,cnt_ch1,cnt_ch2,sec)

        counter_1_max=maxval[0]
        print "Peak: %5d\n"%counter_1_max

        # Analysis and Plot
        outfig=prefix+"_dtheta1.png"
        ana=AnalyzePeak(ofile)
        #comment=AxesInfo(self.s).getLeastInfo()
        comment = "DT scan"
        fwhm,center=ana.analyzeAll("dtheta1[pulse]","Intensity",outfig,comment,"OBS","PEAK")

        # back lash position
        bl_pos=counter_1_max-backlash

        # back lash
        self.m_dtheta1.move(bl_pos)
        n_move=backlash/step

        # Setting the actual value
        for i in range(0,n_move):
            self.m_dtheta1.relmove(step)

        #print self.m_dtheta1.getPosition()
        return fwhm,center

    def scanDt1PeakNoAna(self,prefix,start,end,step,cnt_ch1,cnt_ch2,sec):
        # Setting
        ofile=prefix+"_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        backlash=2000

        maxval=self.m_dtheta1.axisScan(ofile,cnt_ch1,cnt_ch2,sec)

        peak_position=maxval[0]
        print "Peak: %5d\n"%peak_position

        # back lash position
        bl_pos=peak_position-backlash

        # back lash
        self.m_dtheta1.move(bl_pos)
        n_move=backlash/step

        # Setting the actual value
        for i in range(0,n_move):
            self.m_dtheta1.relmove(step)

        return peak_position

    # Code was largely modified 2019/04/23
    def scanDt1Config(self,prefix,confchar,tcs="NULL"):
        backlash = 2000
        conf=ConfigFile(self.BL)
        try :
                ## Dtheta 1
                ch1=int(conf.getCondition2(confchar,"ch1"))
                ch2=int(conf.getCondition2(confchar,"ch2"))
                start=int(conf.getCondition2(confchar,"start"))
                end=int(conf.getCondition2(confchar,"end"))
                step=int(conf.getCondition2(confchar,"step"))
                time=conf.getCondition2(confchar,"time")
                if self.BL == "bl32xu":
                    tcsv=conf.getCondition2(confchar,"tcsv")
                    tcsh=conf.getCondition2(confchar,"tcsh")
                    detune_pls=int(conf.getCondition2(confchar,"detune"))
                    # Setting tcs
                    tcs.setApert(tcsv,tcsh)
                else:
                    detune_pls = 0

        except MyException,ttt:
                print ttt.args[0]
                print "Check your config file carefully.\n"

        # Setting
        ofile=prefix+"_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        backlash=2000+detune_pls

        bl_start = start - backlash

        # Remove backlash to the starting position
        self.m_dtheta1.move(bl_start)
        maxval=self.m_dtheta1.axisScan(ofile,ch1,ch2,time)

        counter_1_max=maxval[0]+detune_pls
        print "Peak: %5d\n"%counter_1_max

        # back lash position
        bl_pos=counter_1_max-backlash

        # back lash
        self.m_dtheta1.move(bl_pos)
        #print self.m_dtheta1.getPosition()
        n_move=int(backlash/step)

        # Setting the actual value
        for i in range(0,n_move):
            self.m_dtheta1.relmove(step)

        return counter_1_max

    def scanDt1PeakConfig(self,prefix,confchar,tcs = "NULL"):
        conf=ConfigFile()
        try :
                ## Dtheta 1
                ch1=int(conf.getCondition2(confchar,"ch1"))
                ch2=int(conf.getCondition2(confchar,"ch2"))
                start=int(conf.getCondition2(confchar,"start"))
                end=int(conf.getCondition2(confchar,"end"))
                step=int(conf.getCondition2(confchar,"step"))
                time=conf.getCondition2(confchar,"time")
                tcsv=conf.getCondition2(confchar,"tcsv")
                tcsh=conf.getCondition2(confchar,"tcsh")
                detune_pls=int(conf.getCondition2(confchar,"detune"))

        except MyException,ttt:
                print ttt.args[0]
                print "Check your config file carefully.\n"

        # Setting tcs
        tcs.setApert(tcsv,tcsh)

        # Setting
        ofile=prefix+"_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        backlash=2000

        maxval=self.m_dtheta1.axisScan(ofile,ch1,ch2,time)

        counter_1_max=maxval[0]+detune_pls
        print "Peak: %5d pls\n"%maxval[0]
        print "detune: %5d pls\n"%detune_pls
        print "target pos: %5d pls\n"%counter_1_max

        # Analysis and Plot
        outfig=prefix+"_dtheta1.png"
        ana=AnalyzePeak(ofile)
        comment=AxesInfo(self.s).getLeastInfo()
        try:
            fwhm,center=ana.analyzeAll("dtheta1[pulse]","Intensity",outfig,comment,"OBS","PEAK")
        except MyException,ttt:
            raise MyException("Dtheta1 tune peak analysis failed.%s"%ttt.args[0])

        if fwhm==0.0:
            raise MyException("Bad peak shape!!")

        # back lash position
        bl_pos=counter_1_max-backlash

        # back lash
        self.m_dtheta1.move(bl_pos)
        #print self.m_dtheta1.getPosition()
        n_move=backlash/step

        # Setting the actual value
        for i in range(0,n_move):
                self.m_dtheta1.relmove(step)

        #print self.m_dtheta1.getPosition()

        return fwhm,center

    def scanDt1PeakConfigExceptForDetune(self,prefix,confchar,tcs,detune):
        conf=ConfigFile()
        try :
                ## Dtheta 1
                ch1=int(conf.getCondition2(confchar,"ch1"))
                ch2=int(conf.getCondition2(confchar,"ch2"))
                start=int(conf.getCondition2(confchar,"start"))
                end=int(conf.getCondition2(confchar,"end"))
                step=int(conf.getCondition2(confchar,"step"))
                time=conf.getCondition2(confchar,"time")
                tcsv=conf.getCondition2(confchar,"tcsv")
                tcsh=conf.getCondition2(confchar,"tcsh")
                detune_pls=int(conf.getCondition2(confchar,"detune"))

        except MyException,ttt:
                print ttt.args[0]
                print "Check your config file carefully.\n"

        detune_pls=detune
        # Setting tcs
        tcs.setApert(tcsv,tcsh)

        # Setting
        ofile=prefix+"_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        backlash=2000

        maxval=self.m_dtheta1.axisScan(ofile,ch1,ch2,time)

        counter_1_max=maxval[0]+detune_pls
        print "Peak: %5d\n"%counter_1_max

        # Analysis and Plot
        outfig=prefix+"_dtheta1.png"
        ana=AnalyzePeak(ofile)
        comment=AxesInfo(self.s).getLeastInfo()
        try:
            fwhm,center=ana.analyzeAll("dtheta1[pulse]","Intensity",outfig,comment,"OBS","PEAK")
        except MyException,ttt:
            raise MyException("Dtheta1 tune peak analysis failed.%s"%ttt.args[0])

        if fwhm==0.0:
            raise MyException("Bad peak shape!!")

        # back lash position
        bl_pos=counter_1_max-backlash

        # back lash
        self.m_dtheta1.move(bl_pos)
        #print self.m_dtheta1.getPosition()
        n_move=backlash/step

        # Setting the actual value
        for i in range(0,n_move):
            self.m_dtheta1.relmove(step)

        #print self.m_dtheta1.getPosition()
        return fwhm,counter_1_max
  
if __name__=="__main__":
    host = '172.24.242.59'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    print "Connection OKAY"
    mono=Mono(s)
    print mono.getE()
    #energy = 12.3984 / 1.04
    #mono.changeE(energy)
    #mono.getTheta()
    #print self.m_dtheta1.getPosition()
    #prefix = "dttune"
    #confchar = "DTSCAN_NORMAL"
    #mono.scanDt1Config(prefix,confchar)
    s.close()
