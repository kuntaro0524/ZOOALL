#!/bin/env python
import sys
import os
import socket
import time
import datetime
from numpy import *

# My library
import Singleton
import File
import BM
import Capture
import Count
import Mono
import ConfigFile
import Att
import BeamCenter
import Stage
import Zoom
import BS
import Shutter
import Cryo
import ID
import ExSlit1
import Light
import AnalyzePeak
import Colli
import Cover
import CCDlen
import CoaxPint
import MBS
import DSS
import BeamsizeConfig
import Flux
import PreColli
from configparser import ConfigParser, ExtendedInterpolation
import WebSocketBSS
import MyException

class Device(Singleton.Singleton):
    def __init__(self, ms_port):
        # ms_port is 'a instance of an opened port for Message server'
        self.s=ms_port
        # beamline.ini is a configure file.
        # reading config file.
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.config.read(config_path)
        # PIN diode channel
        self.pin_channel = self.config.getint("experiment", "pin_channel")
        # coax x pulse is read from 'beamline.ini'
        # section: inocc, option: zoom_pintx
        self.coax_pintx_pulse = int(self.config.get("inocc", "zoom_pintx"))
        # beamline name
        self.beamline = self.config.get("beamline", "beamline")
        # web socket for BSS
        self.websock = WebSocketBSS.WebSocketBSS()

    def setGonio(self, instance_of_gonio):
        self.gonio = instance_of_gonio

    def readConfig(self):
        conf=ConfigFile.ConfigFile()
        # Reading config file
        try :
            ## Dtheta 1
            self.scan_dt1_ch1=int(conf.getCondition2("DTSCAN","ch1"))
            self.scan_dt1_ch2=int(conf.getCondition2("DTSCAN","ch2"))
            self.scan_dt1_start=int(conf.getCondition2("DTSCAN","start"))
            self.scan_dt1_end=int(conf.getCondition2("DTSCAN","end"))
            self.scan_dt1_step=int(conf.getCondition2("DTSCAN","step"))
            self.scan_dt1_time=conf.getCondition2("DTSCAN","time")

            ## Fixed point parameters
            self.fixed_ch1=int(conf.getCondition2("FIXED_POINT","ch1"))
            self.fixed_ch2=int(conf.getCondition2("FIXED_POINT","ch2"))
            self.block_time=conf.getCondition2("FIXED_POINT","block_time")
            self.total_num=conf.getCondition2("FIXED_POINT","total_num")
            self.count_time=conf.getCondition2("FIXED_POINT","time")

        except MyException.MyException as ttt:
            print(ttt.args[0])
            print("Check your config file carefully.\n")
            sys.exit(1)

    def init(self):
        # settings
        print("Initialization starts")
        self.mono=Mono.Mono(self.s)
        self.bm=BM.BM(self.s)
        self.f=File.File("./")
        self.capture=Capture.Capture()
        self.att=Att.Att(self.s)
        self.zoom=Zoom.Zoom(self.s)
        self.bs=BS.BS(self.s)
        self.cryo=Cryo.Cryo(self.s)
        self.id=ID.ID(self.s)
        self.light=Light.Light(self.s)
        print("DDDDD")
        self.colli=Colli.Colli(self.s)
        self.coax_pint=CoaxPint.CoaxPint(self.s)
        self.clen=CCDlen.CCDlen(self.s)
        self.covz=Cover.Cover(self.s)
        self.shutter=Shutter.Shutter(self.s)
        # Optics
        self.mbs=MBS.MBS(self.s)
        self.dss=DSS.DSS(self.s)
        # BL32XU specific
        # BL44XU specific
        if self.beamline.lower() == "bl44xu":
            self.precolli = PreColli.PreColli(self.s)
        elif self.beamline.lower()=="bl32xu":
            self.slit1 = ExSlit1.ExSlit1(self.s)

        print("Device. initialization finished")
        self.isInit=True

    def tuneDt1(self,logpath):
        if os.path.exists(logpath)==False:
            os.makedirs(logpath)
        self.f=File.File(logpath)
        prefix="%s/%03d"%(logpath,self.f.getNewIdx3())
        self.mono.scanDt1PeakConfig(prefix,"DTSCAN_NORMAL",self.tcs)
        dtheta1=int(self.mono.getDt1())
        print("Final dtheta1 = %d pls"%dtheta1)

    def changeEnergy(self,en,isTune=True,logpath="/isilon/BL32XU/BLsoft/Logs/Zoo/"):
        # Energy change
        self.mono.changeE(en)
        # Gap
        self.id.moveE(en)
        if isTune==True:
            self.tuneDt1(logpath)
            
    def measureFlux(self):
        en=self.mono.getE()
        # Prep scan
        self.prepScan()
        # Measurement
        ipin,iic=self.countPin(pin_ch=self.pin_channel)
        print(ipin,iic)
        pin_uA=ipin/100.0
        iic_nA=iic/100.0
        # Photon flux estimation
        ff=Flux.Flux(en)
        phosec=ff.calcFluxFromPIN(pin_uA)
        self.finishScan(cover_off=True)
        print("PHOSEC: %e"%phosec)
        return phosec

    def getBeamsize(self):
        tcs_vmm,tcs_hmm=self.tcs.getApert()
        bsf=BeamsizeConfig.BeamsizeConfig()
        hbeam,vbeam=bsf.getBeamsizeAtTCS_HV(tcs_hmm,tcs_vmm)
        return hbeam,vbeam

    def bsOff(self):
        if self.isInit==False:
            self.init()
        self.bs.off()

    def prepCentering(self,zoom_out=False):
        if zoom_out==True:
            self.zoom.zoomOut()
            if self.beamline == "BL32XU":
                # Currently, the value is read from 'beamline.ini'
                # Finally, it should be read from 'bss.config'
                self.coax_pint.move(self.coax_pintx_pulse)
        if self.config.getboolean("capture", "beamstopper_off"):
            self.bs.off()
        else:
            self.bs.on()

        print("Collimator Off")
        self.colli.off()

        # BL44XU PreColli off
        # PreColli: beam defining aperture related to 'beamsize.conf'
        if self.beamline.lower() == "bl44xu":
            self.precolli.setEvacuate()
        self.light.on()

    def prepCenteringBackCamera(self,zoom_out=True):
        if zoom_out==True:
            self.zoom.zoomOut()
        self.bs.evacLargeHolderWait()
        #self.bs.off()
        self.cryo.on()
        self.colli.off()
        self.light.on()

    def prepCenteringSideCamera(self,zoom_out=True):
        if zoom_out==True:
            self.zoom.zoomOut()
        self.bs.off()
        self.cryo.on()
        self.colli.off()
        self.light.on()

    def prepCenteringLargeHolderCam1(self,zoom_out=True):
        if zoom_out==True:
            self.zoom.zoomOut()
        #self.bs.evacLargeHolder()
        self.bs.evacLargeHolderWait()
        self.cryo.on()
        self.colli.off()
        self.light.on()

    def prepCenteringLargeHolderCam2(self,zoom_out=True):
        if zoom_out==True:
            self.zoom.zoomOut()
        self.bs.on()
        self.cryo.on()
        self.colli.off()
        self.light.on()

    def prepScan(self):
        # Prep scan
        self.clen.evac()
        ## Cover on
        if self.beamline=="BL32XU":
            self.covz.on()
            time.sleep(2.0)
        ## Cover check
        if self.beamline=="BL32XU":
            self.covz.isCover()

        self.light.off()
        self.shutter.open()

        # intensity monitor on
        if self.beamline=="BL41XU":
            self.websock.intensityMonitor("on")

        if self.beamline == "BL32XU":
            self.slit1.openV()

        ## Attenuator
        self.att.setNoAtt()
        # collimator on
        self.colli.on()
        # Beamstopper off
        self.bs.off()

    def finishScan(self,cover_off=True):
        if self.beamline=="BL32XU":
            self.slit1.closeV()
        self.shutter.close()
        # collimator on
        self.colli.off()
        if self.beamline=="BL32XU" and cover_off==True:
            ## Cover off
            self.covz.off()

        # intensity monitor off
        if self.beamline == "BL41XU":
            self.websock.intensityMonitor("off")

    def closeAllShutter(self):
        self.shutter.close()
        self.slit1.closeV()

    def countPin(self,pin_ch=3):
        counter=Count.Count(self.s,pin_ch,0)
        i_pin,i_ion=counter.getCount(1.0)
        return i_pin,i_ion

    def setAttThick(self,thick):
        if self.isInit==False:
            self.init()
        self.att.setAttThick(thick)
    
    def calcAttFac(self,wl,thickness):
        self.att.calcAttFac(wl,thickness)
    
    def prepView(self):
        if self.isInit==False:
            self.init()
        self.closeShutters()
        self.light.on()
    
################################
# Last modified 120607
# for XYZ stage implemtented to the monitor
################################
    def prepCapture(self):
        if self.isInit==False:
            self.init()
        ## Zoom in
        self.zoom.go(0)
    
        ## Cryo go up
        self.cryo.off()
    
        ## BM on
        self.bm.onPika()
    
        ## BS on
        self.bs.on()

    def closeCapture(self):
        self.capture.disconnect()

    ###########################
    # Last modified 120607
    # for XYZ stage implemtented to the monitor
    ###########################
    def finishCapture(self):
        if self.isInit==False:
            self.init()
        ## BM off
        self.bm.offXYZ()
        ## BS off
        self.bs.off()
    
    def captureBM(self,prefix,isTune=True):
        if self.isInit==False:
            self.init()
    
        # Attenuator setting
        if isTune==True:
            # Tune gain
            gain=self.cap.tuneGain()
    
        print("##### GAIN %5d\n"%gain)
    
        ### averaging center x,y
        path=os.path.abspath("./")
        prefix="%s/%s"%(path,prefix)
        x,y=self.cap.aveCenter(prefix,gain,5)
    
        return x,y
    
    def checkRingCurrent(self,current_threshold=50.0):
        self.get_current_str="get/bl_dbci_ringcurrent/present"
        self.s.sendall(self.get_current_str)
        recbuf = self.s.recv(8000)
        strs=recbuf.split("/")
        ring_current=float(strs[len(strs)-2].replace("mA",""))
    
        if ring_current > current_threshold:
            print("Ring current %5.1f"%ring_current)
            return True
        else:
            print("Ring aborted.")
            print("Ring current %5.1f"%ring_current)
            return False

if __name__=="__main__":
    from configparser import ConfigParser, ExtendedInterpolation
    # read IP address for BSS connection from beamline.config 
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(config_path)
    host = config.get("server", "blanc_address")
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    dev=Device(s)
    dev.init()

    # dev.prepCentering()
    dev.bs.on()
    #dev.measureFlux()
    # dev.prepScan()
    # dev.finishScan()
