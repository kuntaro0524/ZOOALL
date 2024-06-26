#!/bin/env python
# -*- coding: utf-8 -*-
from cmath import log
import sys
import os
import socket
import time
import datetime

import Env

# sys.path.append("/isilon/BL41XU/BLsoft/PPPP/")

# My library
import Singleton
import File
# import TCS
import BM
import Capture
import Count
import Mono
import ConfigFile
import Att
import Stage
import Zoom
import BS
import Shutter
import Cryo
import ID
import ExSlit1
import Light
# import AnalyzePeak
import Gonio
import Colli
import CCDlen
import CoaxPint
import MBS
import DSS
import BeamsizeConfig
import Flux
import Mirror
import MirrorTuneUnit
import MyException
import DetectorCover
import IntensityMonitor

class Device(Singleton.Singleton):
    def __init__(self, ms_port, bl="BL41XU"):
        self.s = ms_port
        self.BL = bl.lower()
        self.env = Env.Env()
        print(self.env.beamline_lower)

        self.isDebug = True

    def readConfig(self):
        conf = ConfigFile.ConfigFile()
        # Reading config file
        try:
            ## Dtheta 1
            self.scan_dt1_ch1 = int(conf.getCondition2("DTSCAN", "ch1"))
            self.scan_dt1_ch2 = int(conf.getCondition2("DTSCAN", "ch2"))
            self.scan_dt1_start = int(conf.getCondition2("DTSCAN", "start"))
            self.scan_dt1_end = int(conf.getCondition2("DTSCAN", "end"))
            self.scan_dt1_step = int(conf.getCondition2("DTSCAN", "step"))
            self.scan_dt1_time = conf.getCondition2("DTSCAN", "time")

            ## Fixed point parameters
            self.fixed_ch1 = int(conf.getCondition2("FIXED_POINT", "ch1"))
            self.fixed_ch2 = int(conf.getCondition2("FIXED_POINT", "ch2"))
            self.block_time = conf.getCondition2("FIXED_POINT", "block_time")
            self.total_num = conf.getCondition2("FIXED_POINT", "total_num")
            self.count_time = conf.getCondition2("FIXED_POINT", "time")

        except MyException, ttt:
            print ttt.args[0]
            print "Check your config file carefully.\n"
            sys.exit(1)

    def init(self):
        # settings
        self.mono = Mono.Mono(self.s)
        if self.BL == "bl32xu":
            import Cover
            import DetectorStage
            self.tcs = TCS.TCS(self.s)
            self.covz = Cover.Cover(self.s)
            self.det_y = DetectorStage.DetectorStage(self.s)

        if self.BL == "bl45xu":
            self.covz = DetectorCover.DetectorCover(self.s)

        self.bm = BM.BM(self.s)
        self.f = File.File("./")
        self.capture = Capture.Capture()
        self.slit1 = ExSlit1.ExSlit1(self.s)
        self.att = Att.Att(self.s)
        self.stage = Stage.Stage(self.s)
        self.zoom = Zoom.Zoom(self.s)
        self.bs = BS.BS(self.s)
        self.cryo = Cryo.Cryo(self.s)
        self.id = ID.ID(self.s)
        self.light = Light.Light(self.s)
        self.gonio = Gonio.Gonio(self.s)
        self.gonio.prepprep()
        self.colli = Colli.Colli(self.s)
        self.coax_pint = CoaxPint.CoaxPint(self.s)
        self.clen = CCDlen.CCDlen(self.s)
        self.shutter = Shutter.Shutter(self.s)
        self.mirror = Mirror.Mirror(self.s)
        self.intensity_monitor= IntensityMonitor.IntensityMonitor(self.s)
        self.mtu = MirrorTuneUnit.MirrorTuneUnit(self.s)

        # self.readConfig()
        # Optics
        self.mbs = MBS.MBS(self.s)
        self.dss = DSS.DSS(self.s)

        print "Device. initialization finished"
        self.isInit = True

    # comment out by YK 161031
    # def waitAndOpenOptShutters(self):

    def getServer(self):
        return self.s

    def calcFlux(self, en, pin_uA):
        fluxer = Flux.Flux(en)
        flux = fluxer.calcFluxFromPIN(pin_uA)
        return flux

    def tuneDt1(self, logpath):
        ## SKIPPING ALL 2019/04/21 K.Hirata
        ## BL45XU
        if os.path.exists(logpath) == False:
            os.makedirs(logpath)
        self.f = File.File(logpath)
        prefix = "%s/%03d" % (logpath, self.f.getNewIdx3())

        if self.BL == "bl32xu":
            self.mono.scanDt1PeakConfig(prefix, "DTSCAN_NORMAL", self.tcs)
        else:
            self.mono.scanDt1Config(prefix, "DTSCAN_NORMAL")

        dtheta1 = int(self.mono.getDt1())
        print "Final dtheta1 = %d pls" % dtheta1

    def changeEnergy(self, en, isTune=True, logpath="/isilon/BL41XU/BLsoft/Logs/Zoo/"):
        # Energy change
        self.mono.changeE()
        # Gap
        self.id.moveE(energy)
        if self.isTune == True:
            self.tuneDt1(logpath)

    def measureFlux(self, pin_ch=1):
        print("Device.measureFlux")
        en = self.mono.getE()
        # preparation
        if self.isDebug: print("prep measuring flux")
        self.prepMeasureFlux()
        # Measurement
        ipin, iic = self.countPin(pin_ch=pin_ch)

        if self.BL == "bl45xu":
            pin_uA = ipin / 10.0
            iic_nA = iic / 100.0
            pin_uA = 2.0 * pin_uA

        elif self.BL == "bl41xu":
            if self.isDebug: print("PIN=", ipin)
           # pin_uA = ipin / 100.0
            pin_uA = ipin / 10.0

        ff = Flux.Flux(en)
        phosec = ff.calcFluxFromPIN(pin_uA)
        self.finishMeasureFlux()

        return phosec

    def getBeamsize(self, config_dir="/isilon/blconfig/bl32xu/"):
        tcs_vmm, tcs_hmm = self.tcs.getApert()
        bsf = BeamsizeConfig.BeamsizeConfig(config_dir)
        hbeam, vbeam = bsf.getBeamsizeAtTCS_HV(tcs_hmm, tcs_vmm)
        return hbeam, vbeam

    def bsOff(self):
        if self.isInit == False:
            self.init()
        self.bs.off()

    def setPin(self, on_or_off):
        if on_or_off.lower() == "on":
            self.light.setPosition(-800)
        else:
            self.light.off()

    # BL45XU measuring flux
    def prepMeasureFlux(self):
        # 2023/04/12
        # pin photo diode insert with Light Z-axis
        self.light.intensityMonitorOn()
        self.bs.off()
        print("collll")
        self.colli.on()
        print("collll")
        self.shutter.open()
        self.att.setAttThick(0.0)

    def finishMeasureFlux(self):
        # 2023/04/12
        # pin photo diode insert with Light Z-axis
        self.light.intensityMonitorOff()
        self.shutter.close()
        self.colli.off()
        self.att.setAttThick(0.0)

    def prepScan(self):
        self.light.off()
        self.shutter.open()

    def prepScanCoaxCam(self):
        # Prep scan
        self.clen.evac()
        ## Cover on
        self.covz.on()
        time.sleep(2.0)
        ## Cover check
        self.covz.isCover()
        self.light.off()
        # self.slit1.openV()
        ## BS off
        self.bs.off()
        self.colli.off()
        self.shutter.open()

    def finishScan(self, cover_off=True):
        self.shutter.close()
        if self.BL == "bl32xu":
            self.slit1.closeV()
            if cover_off == True:
                ## Cover off
                self.covz.off()
        self.colli.off()

    def closeAllShutter(self):
        self.shutter.close()
        # self.slit1.closeV()

    def countPin(self, pin_ch=2):
        counter = Count.Count(self.s, pin_ch, 0)
        i_pin, i_ion = counter.getCount(1.0)
        return i_pin, i_ion

    def countOneSec(self, ch=0):
        counter = Count.Count(self.s, ch, 1)
        t_value, dummy = counter.getCount(1.0)
        return t_value

    def setAttThick(self, thick):
        if self.isInit == False:
            self.init()
        self.att.setAttThick(thick)

    def calcAttFac(self, wl, thickness):
        self.att.calcAttFac(wl, thickness)

    def closeShutters(self):
        # self.slit1.closeV()
        self.shutter.close()

    def openShutters(self):
        # self.slit1.openV()
        self.shutter.open()

    def prepView(self):
        if self.isInit == False:
            self.init()
        self.closeShutters()
        self.light.on()

    def moveGonioXYZ(self, x, y, z):
        self.gonio.moveXYZmm(x, y, z)

    # This routine is exceedingly important for robust centering
    # Device evacuation defined here governs background of a background image for crystal centering.
    # From evaluation stage of centering procedures, the same function should be used before capturing background image of OAV.
    def prepCentering(self):
        self.colli.off()
        # BL41XU以外はBeamstopperをオフにしている→不要なのでは・・・
        if self.BL!="bl41xu":
            self.bs.off()
        self.light.on()
        self.zoom.zoomOut()

    ################################
    # Last modified 120607
    # for XYZ stage implemtented to the monitor
    ################################
    def prepCapture(self):
        if self.isInit == False:
            self.init()
        ## Zoom in
        self.zoom.zoomIn()
        ## Cryo go up
        self.cryo.off4mon()
        ## BM on
        self.bm.on()
        ## BS on
        self.bs.on()
        self.shutter.open()

    ###########################
    # Last modified 120607
    # for XYZ stage implemtented to the monitor
    ###########################
    def finishCapture(self):
        if self.isInit == False:
            self.init()
        self.shutter.close()
        self.bm.off()
        self.bm.off()
        self.cryo.off()
        self.zoom.zoomOut()

    # Attenuator thickness tune for beam monitor
    def tuneAttThick(self):
        perflag=False
        threflag=False
        for thick in self.att.getAttList():
            tmpfile="%s/thick_%04d.ppm"%(self.curr_dir,int(thick))
            self.setAtt(thick)
            #self.cap.captureWithSpeed(tmpfile,4000)    #  For ARTRAY by YK@190311
            self.cap.capture(tmpfile,1000)      # 190417 same value at the header 'self.speed'
            bc=BeamCenter(tmpfile)
            satcnt,perc,isum_all=bc.check()
            aveall=float(isum_all)/480.0/640.0

            # I saw a weak scintillation by using perc<3.0
            # I gave a larger value for the threshold.
            # I gave a larger value for the threshold 4 -> 5 on 2016/06/23
            # I gave a larger value for the threshold 5 -> 6 on 2016/06/27
            if perc < 6.0:
                perflag=True

            if aveall <= 60:
                threflag=True

            # K. Hirata 160512 added
            print "RE ",thick,satcnt,perc,isum_all,aveall
            if perflag==True and threflag==True:
                break
        return thick


    def captureBM(self, prefix, isTune=True):
        if self.isInit == False:
            self.init()

        # Attenuator setting
        if isTune == True:
            # Tune gain
            gain = self.cap.tuneGain()

        print "##### GAIN %5d\n" % gain

        ### averaging center x,y
        path = os.path.abspath("./")
        prefix = "%s/%s" % (path, prefix)
        x, y = self.cap.aveCenter(prefix, gain, 5)

        return x, y

    def prepMirrorHalf(self):
        self.det_y.evacuate()
        self.stage.stageEvac()

    def finishMirrorHalf(self):
        curr_ymm = self.stage.getYmm()
        target_ymm = curr_ymm - 200.0
        self.stage.setYmm(target_ymm)
        self.det_y.moveToOrigin()

    def evacuate(self):
        self.moveY(self.evacuate_position)

    def moveToOrigin(self):
        self.moveY(self.in_position)

    # usage: after shutter
    def simpleCountBack(self, ch1, ch2, inttime, ndata):
        if self.isInit == False:
            self.init()
        # shutter close
        print "Shutter close: estimation of background"
        self.closeShutters()
        # average back ground
        ave1, ave2 = self.simpleCount(ch1, ch2, inttime, ndata)

        # shutter open
        self.openShutters()
        print "Shutter open: estimation of actual count"
        ave3, ave4 = self.simpleCount(ch1, ch2, inttime, ndata, ave1, ave2)

        print "Average ch1: %8d ch2: %8d\n" % (ave3, ave4)
        return ave3, ave4

    """
    def simpleCount(self, ch1, ch2, inttime, ndata, back1=0, back2=0):
        if self.isInit == False:
            self.init()
        counter = Count.Count(self.s, ch1, ch2)
        f = File.File("./")

        prefix = "%03d" % f.getNewIdx3()
        ofilename = "%s_count.scn" % prefix
        of = open(ofilename, "w")

        # initialization
        starttime = time.time()
        strtime = datetime.datetime.now()
        of.write("#### %s\n" % starttime)
        of.write("#### %s\n" % strtime)
        ttime = 0
        for i in arange(0, ndata, 1):
            currtime = time.time()
            ttime = currtime - starttime
            ch1, ch2 = counter.getCount(inttime)
            ch1 = ch1 - back1
            ch2 = ch2 - back2
            of.write("12345 %8.4f %12d %12d\n" % (ttime, ch1, ch2))
        of.close()

        # file open
        ana = AnalyzePeak.AnalyzePeak(ofilename)
        x, y1, y2 = ana.prepData3(1, 2, 3)

        py1 = ana.getPylabArray(y1)
        py2 = ana.getPylabArray(y2)

        mean1 = py1.mean()
        mean2 = py2.mean()
        std1 = py1.std()
        std2 = py2.std()

        of = open(ofilename, "a")

        of.write("COUNTER1:%5d Average: %12.5f Std.:%12.5f (%8.3f perc.)\n" % (
        ch1, py1.mean(), py1.std(), py1.std() / py1.mean() * 100.0))
        of.write("COUNTER2:%5d Average: %12.5f Std.:%12.5f (%8.3f perc.)\n" % (
        ch2, py2.mean(), py2.std(), py2.std() / py2.mean() * 100.0))

        of.close()
        return mean1, mean2
    """


if __name__ == "__main__":
    host = '172.24.242.54'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    dev = Device(s, bl="bl41xu")
    dev.init()

    # dev.prepCapture()
    # dev.finishCapture()

    # en = dev.mono.getE()
    # print "EN=",en
    #dev.prepMeasureFlux()
    #print (dev.countPin(pin_ch = 1))
    #print (dev.countPin(pin_ch = 2))
    dev.prepMeasureFlux()
    # dev.closeShutters()
    # print (dev.countPin(pin_ch = 3))
    # dev.openShutters()
    # print (dev.countPin(pin_ch = 3))
    # print dev.measureFlux(pin_ch = 1)
    # print dev.measureFlux()
    # print dev.countPin(1)
    # print dev.countPin(2)
    # print dev.countPin(3)
    # counts = dev.countPin(pin_ch=3)
    # print(counts)
    # pin_uA = float(counts[0])/100.0
    # print("%e"%dev.calcFlux(12.3984, pin_uA))
    print("%e"%dev.measureFlux(3))
    dev.closeShutters()

    dev.finishMeasureFlux()

    #dev.prepCentering()
    # print phosec

    # print en

    # logpath="/isilon/users/target/target/Staff/2016B/161003/03.Test/"

    # count_time = 1.0
    # dev.simpleCountBack(3, 0, count_time, 1)
