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
        self.stage_z = Motor(self.s, "bl_32in_st2_stage_1_z", "pulse")
        self.stage_y = Motor(self.s, "bl_32in_st2_stage_1_y", "pulse")

        self.p2v_z = 15000.0  # 1mm/15000pls
        self.p2v_y = 10000.0  # 1mm/10000pls

    def getSpeed(self):
        print(self.stage_z.getSpeed())
        print(self.stage_y.getSpeed())

    def getZ(self):
        return self.stage_z.getPosition()[0]

    def getY(self):
        return self.stage_y.getPosition()[0]

    def moveZ(self, pulse):
        self.stage_z.move(pulse)

    def moveY(self, pulse):
        print("Recieved pulse ", pulse)
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

    def scanZneedleMove(self, prefix, step_mm, num_half, ch1, ch2, time):
        ofile = prefix + "_stagez.scn"
        of = open(ofile, "w")
        counter = Count(self.s, ch1, ch2)

        # save position
        savep = self.getZ()

        # Scan condition [mm]
        curr = self.getZmm()
        width_half = float(step_mm) * float(num_half)
        print("WIDTH:%8.5f" % width_half)
        start = curr - width_half

        # move to the start position
        self.moveZum(-width_half * 1000.0)
        step_um = step_mm * 1000.0

        for idx in range(0, num_half * 2):
            val1, val2 = counter.getCount(time)
            zpos = self.getZmm()
            of.write("1234 %9.5f %10s %10s\n" % (zpos, val1, val2))
            self.moveZum(step_um)

        of.close()

        ana = AnalyzePeak(ofile)
        outfig = "%s_stagez.png" % prefix
        comment = "Stage Z needle scan"
        fwhm, center = ana.analyzeAll("stageZ[mm]", "Intensity", outfig, comment, "OBS", "FCEN")

        # Center
        diff_dist = math.fabs(center - curr) * 1000.0
        #		if diff_dist > 10.0:
        if diff_dist > 100.0:
            raise MyException("Stage Z movement is quite large. (>10.0um)")
        else:
            self.setZmm(center)
        return fwhm, center

    def scanZneedle(self, prefix, step_mm, num_half, ch1, ch2, time):
        ofile = prefix + "_stagez.scn"
        of = open(ofile, "w")
        counter = Count(self.s, ch1, ch2)

        # save position
        savep = self.getZ()

        # Scan condition [mm]
        curr = self.getZmm()
        width_half = float(step_mm) * float(num_half)
        print("WIDTH:%8.5f" % width_half)
        start = curr - width_half

        # move to the start position
        self.moveZum(-width_half * 1000.0)
        step_um = step_mm * 1000.0

        for idx in range(0, num_half * 2):
            val1, val2 = counter.getCount(time)
            zpos = self.getZmm()
            of.write("1234 %9.5f %10s %10s\n" % (zpos, val1, val2))
            self.moveZum(step_um)

        of.close()

    def scanYwire(self, prefix, step_mm, num_half, ch1, ch2, time):
        ofile = prefix + "_stagey.scn"
        of = open(ofile, "w")
        counter = Count(self.s, ch1, ch2)

        # save position
        savep = self.getY()

        # Scan condition [mm]
        curr = self.getYmm()
        width_half = float(step_mm) * float(num_half)
        print("WIDTH:%8.5f" % width_half)
        start = curr - width_half

        # move to the start position
        self.moveYum(-width_half * 1000.0)
        step_um = step_mm * 1000.0

        for idx in range(0, num_half * 2):
            val1, val2 = counter.getCount(time)
            zpos = self.getYmm()
            of.write("1234 %9.5f %10s %10s\n" % (zpos, val1, val2))
            self.moveYum(step_um)

        of.close()

        ana = AnalyzePeak(ofile)
        outfig = "%s_stagey.png" % prefix
        ##		outfig="stagey.png"
        comment = "TEST"
        fwhm, center = ana.analyzeAll("stageZ[mm]", "Intensity", outfig, comment, "OBS", "FCEN")

        # Center
        diff_dist = math.fabs(center - curr) * 1000.0
        #		if diff_dist > 50.0:
        if diff_dist > 100.0:
            raise MyException("Stage Y movement is quite large. (>50.0um)")
            self.moveY(savep)
        else:
            self.setYmm(center)

        return fwhm, center

    def scanYneedle(self, prefix, step_mm, num_half, ch1, ch2, time):
        ofile = prefix + "_stagey.scn"
        of = open(ofile, "w")
        counter = Count(self.s, ch1, ch2)

        # save position
        savep = self.getY()
        print("start:saved position", savep)

        # Scan condition [mm]
        curr = self.getYmm()
        width_half = float(step_mm) * float(num_half)
        print("WIDTH:%8.5f" % width_half)
        start = curr - width_half

        # move to the start position
        self.moveYum(-width_half * 1000.0)
        step_um = step_mm * 1000.0

        for idx in range(0, num_half * 2):
            val1, val2 = counter.getCount(time)
            ypos = self.getYmm()
            of.write("1234 %9.5f %10s %10s\n" % (ypos, val1, val2))
            self.moveYum(step_um)

        of.close()

        print("After scan", self.getY())
        self.moveY(savep)
        print("finish:saved position", savep)
        print("After moved", self.getY())

        return 10, 10

    def scanY(self, option="STAY"):
        f = File("./")
        curr_y = self.getY()  # pulse

        # Hole diameter of coax-camera 1.5mm
        # 2mm width scan +-1.0mm
        width = 2.0 * self.p2v_y
        wing = int(width / 2.0)

        # Scan step = 0.05mm
        scan_step_p = int(0.05 * self.p2v_y)

        scan_start_p = curr_y - wing
        scan_end_p = curr_y + wing

        self.stage_y.setStart(scan_start_p)
        self.stage_y.setEnd(scan_end_p)
        self.stage_y.setStep(scan_step_p)
        cnt_ch = 3
        cnt_ch2 = 0
        cnt_time = 0.2

        print("Start scan")
        prefix = "%03d" % f.getNewIdx3()
        ofile = "%s_sty.scn" % prefix
        self.stage_y.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)
        print("end scan")

        # Moving to the gravity center
        outfig = prefix + "_sty.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()
        fwhm, center = ana.analyzeAll("Stage Y[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")

        # Unit convertion
        fwhm_mm = fwhm / self.p2v_y
        center_mm = center / self.p2v_y

        print("FWHM Center=", fwhm_mm)
        print("Center     =", center_mm)

        if option != "STAY":
            print("Moving to ", center_mm, " [mm]")
            self.setYmm(center_mm)

        return fwhm_mm, center_mm

    def scanZ(self, option="STAY"):
        f = File("./")
        curr_z = self.getZ()  # pulse

        # Hole diameter of coax-camera 1.5mm
        # 2mm width scan +-1.0mm
        width = 2.0 * self.p2v_z
        wing = int(width / 2.0)

        # Scan step = 0.01mm
        scan_step_p = int(0.01 * self.p2v_z)

        scan_start_p = curr_z - wing
        scan_end_p = curr_z + wing

        self.stage_z.setStart(scan_start_p)
        self.stage_z.setEnd(scan_end_p)
        self.stage_z.setStep(scan_step_p)
        cnt_ch = 3
        cnt_ch2 = 0
        cnt_time = 0.2

        print("Start scan")
        prefix = "%03d" % f.getNewIdx3()
        ofile = "%s_stz.scn" % prefix
        self.stage_z.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)
        print("end scan")

        # Moving to the gravity center
        outfig = prefix + "_stz.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()
        fwhm, center = ana.analyzeAll("Stage Z[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")

        # Unit convertion
        fwhm_mm = fwhm / self.p2v_z
        center_mm = center / self.p2v_z
        print("FWHM Center=", fwhm_mm)
        print("Center     =", center_mm)

        if option != "STAY":
            print("Moving to ", center_mm, " [mm]")
            self.setZmm(center_mm)

        return fwhm_mm, center_mm


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    stage = Stage(s)
    yyy = stage.getYmm()
    zzz = stage.getZmm()
    # stage.getSpeed()
    print(yyy, zzz)
    # stage.scanY("MOVE")
    s.close()
