#!/bin/env python 
import sys
import socket
import time
from decimal import *

# My library
from Received import *
from Motor import *
from AnalyzePeak import *
from Count import *


class Stage:

    def __init__(self, server):
        self.s = server
        self.stage_z = Motor(self.s, "bl_45in_st2_stage_1_z", "pulse")
        self.stage_y = Motor(self.s, "bl_45in_st2_stage_1_y", "pulse")

        self.p2v_z = 15000.0  # 1mm/15000pls
        self.p2v_y = 20000.0  # 1mm/10000pls

    def getSpeed(self):
        print self.stage_z.getSpeed()
        print self.stage_y.getSpeed()

    def getZ(self):
        return self.stage_z.getPosition()[0]

    def getY(self):
        return self.stage_y.getPosition()[0]

    def moveZ(self, pulse):
        self.stage_z.move(pulse)

    def moveY(self, pulse):
        print "Recieved pulse ", pulse
        backlash = pulse - 500
        self.stage_y.move(backlash)
        self.stage_y.move(pulse)

    def setZmm(self, value):
        pvalue = int(value * self.p2v_z)
        self.moveZ(pvalue)

    def setYmm(self, value):
        pvalue = int(value * self.p2v_y)
        self.moveY(pvalue)

    def getZmm(self):
        pvalue = float(self.getZ())
        value = pvalue / self.p2v_z
        value = round(value, 4)
        return value

    def getYmm(self):
        pvalue = float(self.getY())
        value = pvalue / self.p2v_y
        value = round(value, 4)
        return value

    def moveYum(self, value):
        # um to mm
        vmm = value / 1000.0
        # mm to pulse
        vp = int(vmm * self.p2v_y)

        # back lash[10um]

        # diff from current value
        if vp >= 0.0:
            self.stage_y.relmove(vp)
        if vp < 0.0:
            # current position [pulse]
            curr_yp = self.getY()

            # final position [pulse]
            final_yp = curr_yp + vp

            # back lash position[pulse] 10um
            bl_pulse = int(-0.01 * self.p2v_y)
            bl_position = final_yp + bl_pulse
            self.stage_y.move(final_yp)

    def moveZum(self, value):
        # um to mm
        vmm = value / 1000.0
        # mm to pulse
        vp = int(vmm * self.p2v_z)

        self.stage_z.relmove(vp)

    #def scanY(self, option="STAY"):
    def scanY(self, option="STAY", scan_width_mm=3.0, cnt_ch =1, cnt_ch2=0, cnt_time=0.2):
        f = File("./")
        curr_y = self.getY()  # pulse

        # Hole diameter of coax-camera 1.5mm
        # 2mm width scan +-1.0mm
        width = scan_width_mm * self.p2v_y
        wing = int(width / 2.0)

        # Scan step = 0.05mm
        scan_step_p = int(0.05 * self.p2v_y)

        scan_start_p = curr_y - wing
        scan_end_p = curr_y + wing

        self.stage_y.setStart(scan_start_p)
        self.stage_y.setEnd(scan_end_p)
        self.stage_y.setStep(scan_step_p)

        print "Start scan"
        prefix = "%03d" % f.getNewIdx3()
        ofile = "%s_sty.scn" % prefix
        self.stage_y.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)
        print "end scan"

        # Moving to the gravity center
        outfig = prefix + "_sty.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()
        fwhm, center = ana.analyzeAll("Stage Y[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")

        # Unit convertion
        fwhm_mm = fwhm / self.p2v_y
        center_mm = center / self.p2v_y

        print "FWHM Center=", fwhm_mm
        print "Center     =", center_mm

        if option != "STAY":
            print "Moving to ", center_mm, " [mm]"
            self.setYmm(center_mm)

        return fwhm_mm, center_mm

    def scanZ(self, option="STAY", scan_width_mm=2.0, cnt_ch =3, cnt_ch2=0, cnt_time=0.2):
        f = File("./")
        curr_z = self.getZ()  # pulse

        # Hole diameter of coax-camera 1.5mm
        # 2mm width scan +-1.0mm
        width = scan_width_mm * self.p2v_z
        wing = int(width / 2.0)

        # Scan step = 0.01mm
        scan_step_p = int(0.01 * self.p2v_z)

        scan_start_p = curr_z - wing
        scan_end_p = curr_z + wing

        self.stage_z.setStart(scan_start_p)
        self.stage_z.setEnd(scan_end_p)
        self.stage_z.setStep(scan_step_p)

        print "Start scan"
        prefix = "%03d" % f.getNewIdx3()
        ofile = "%s_stz.scn" % prefix
        self.stage_z.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)
        print "end scan"

        # Moving to the gravity center
        outfig = prefix + "_stz.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()
        fwhm, center = ana.analyzeAll("Stage Z[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")

        # Unit convertion
        fwhm_mm = fwhm / self.p2v_z
        center_mm = center / self.p2v_z
        print "FWHM Center=", fwhm_mm
        print "Center     =", center_mm

        if option != "STAY":
            print "Moving to ", center_mm, " [mm]"
            self.setZmm(center_mm)

        return fwhm_mm, center_mm


if __name__ == "__main__":
    host = '172.24.242.59'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    stage = Stage(s)
    yyy= stage.getYmm()
    zzz= stage.getZmm()
    print yyy,zzz
    # stage.getSpeed()
    #stage.scanZ(option="STAY", scan_width_mm=3.0, cnt_ch =1, cnt_ch2=0, cnt_time=0.2)
    #stage.scanY(option="STAY", scan_width_mm=3.0, cnt_ch =1, cnt_ch2=0, cnt_time=0.2)
    #print yyy,zzz
    #stage.scanY("MOVE")
    s.close()
