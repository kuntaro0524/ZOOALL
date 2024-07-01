#!/bin/env python 
import sys
import socket
import time
import math
from decimal import *
from MyException import *

# My library
from Received import *
from Motor import *
from AnalyzePeak import *
from File import *


class Mirror:

    def __init__(self, server):
        self.s = server
        self.hfm_y = Motor(self.s, "bl_32in_st2_mh_1_y", "pulse")
        self.vfm_z = Motor(self.s, "bl_32in_st2_mv_1_z", "pulse")
        self.hfm_z = Motor(self.s, "bl_32in_st2_mh_1_z", "pulse")
        self.vfm_y = Motor(self.s, "bl_32in_st2_mv_1_y", "pulse")
        self.hfm_tz = Motor(self.s, "bl_32in_st2_mh_1_tz", "pulse")
        self.vfm_ty = Motor(self.s, "bl_32in_st2_mv_1_ty", "pulse")

        # Evacuation
        self.evac_y = 30000
        self.evac_z = -30000

        # Offset of VFM-z
        # self.VFM_Z_OFFSET=0 -100pls offset of dtheta1 at energy lower than 10 keV: Obsoleted tuning method
        self.VFM_Z_OFFSET = 0

        # Counter channel
        self.count_channel = 1

        # File
        self.f = File("./")

    def getVFM_y(self):
        return int(self.vfm_y.getPosition()[0])

    def getHFM_z(self):
        return int(self.hfm_z.getPosition()[0])

    def getVFMin(self):
        return int(self.vfm_ty.getPosition()[0])

    def getHFMin(self):
        return int(self.hfm_tz.getPosition()[0])

    def setVFMin(self, abspls):
        # move the VFM incident angle
        self.vfm_ty.move(abspls)

    def setHFMin(self, abspls):
        # move the HFM incident angle
        self.hfm_tz.move(abspls)

    def setVFMinRelative(self, relpls):
        # check
        curr_pls = self.getVFMin()
        # absolute value
        abs = curr_pls + relpls
        # move the incident angle
        self.vfm_ty.move(abs)

    def setHFMinRelative(self, relpls):
        # check
        curr_pls = self.getHFMin()
        # absolute value
        abs = curr_pls + relpls
        # move the incident angle
        self.hfm_tz.move(abs)

    ### Translational axes
    def getHFM_y(self):
        rtn = self.hfm_y.getPosition()
        value = int(rtn[0])
        return value

    def getVFM_z(self):
        rtn = self.vfm_z.getPosition()
        value = int(rtn[0])
        return value

    def getYZ(self):
        y = self.getHFM_y()
        z = self.getVFM_z()
        return y, z

    def setHFM_y(self, pulse):
        self.hfm_y.move(pulse)

    def setVFM_z(self, pulse):
        self.vfm_z.move(pulse)

    def setVFM_y(self, pulse):
        self.vfm_y.move(pulse)

    def setHFM_z(self, pulse):
        self.hfm_z.move(pulse)

    def evacVFM_z(self):
        curr_z = self.getVFM_z()
        print "Current position VFM-z:", curr_z
        target_position = curr_z + self.evac_z
        self.setVFM_z(target_position)
        curr_z = self.getVFM_z()
        print "Current position VFM-z:", curr_z

    def evacHFM_y(self):
        curr_y = self.getHFM_y()
        print "Current position HFM-y:", curr_y
        target_position = curr_y + self.evac_y
        self.setHFM_y(target_position)
        curr_y = self.getHFM_y()
        print "Current position HFM-y:", curr_y

    def tuneVFM_z(self, center_pulse):
        # VFM tune range
        # Aperture to the beam is 3.5mrad * 0.4m = 1.4mm
        # Cover range : rough_center (+)(-)1.5mm
        # 1mm = 15,000 pulse for VFM_z
        scan_start_p = center_pulse - 20000
        scan_end_p = center_pulse + 20000
        scan_step_p = 1000
        print "Scan condition of VFM_z"
        print scan_start_p, scan_end_p, scan_step_p

        self.vfm_z.setStart(scan_start_p)
        self.vfm_z.setEnd(scan_end_p)
        self.vfm_z.setStep(scan_step_p)
        cnt_ch2 = 0
        cnt_time = 0.2

        print "Start scan"
        prefix = "%03d" % self.f.getNewIdx3()
        ofile = "%s_vfm_z.scn" % prefix
        self.vfm_z.axisScan(ofile, self.count_channel, cnt_ch2, cnt_time)
        print "end scan"

        # Moving to the gravity center
        outfig = prefix + "_vfm_z.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()
        fwhm, center = ana.analyzeAll("VFM Z[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")

        # Offset for Low Energy focusing
        # 100um downer from the FWHM center of peak
        target_pos = int(center) - self.VFM_Z_OFFSET

        # Center difference
        diff = math.fabs(center - center_pulse)

        # Initial center and Current center difference
        # is smaller than 1.0mm
        if diff < 10000:
            print "Center pulse = ", target_pos
            print "Now moving to ", target_pos, " pulse"
            self.vfm_z.move(target_pos)

    def tuneHFM_y(self, center_pulse):
        # HFM tune range
        # Aperture to the beam is 3.5mrad * 0.4m = 1.4mm
        # Cover range : rough_center (+)(-)1.5mm
        # 1mm = 15,000 pulse for HFM_y
        scan_start_p = center_pulse - 20000
        scan_end_p = center_pulse + 20000
        scan_step_p = 1000
        print "Scan condition of HFM_y"
        print scan_start_p, scan_end_p, scan_step_p

        self.hfm_y.setStart(scan_start_p)
        self.hfm_y.setEnd(scan_end_p)
        self.hfm_y.setStep(scan_step_p)
        cnt_ch2 = 0
        cnt_time = 0.2

        print "Start scan"
        prefix = "%03d" % self.f.getNewIdx3()
        ofile = "%s_hfm_y.scn" % prefix
        self.hfm_y.axisScan(ofile, self.count_channel, cnt_ch2, cnt_time)
        print "end scan"

        # Moving to the gravity center
        outfig = prefix + "_hfm_y.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()
        fwhm, center = ana.analyzeAll("HFM Y[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")

        target_pos = int(center)

        # Center difference
        diff = math.fabs(center - center_pulse)

        # Initial center and Current center difference
        # is smaller than 1.0mm
        if diff < 10000:
            print "Center pulse = ", int(center), "pulse"
            print "Now moving to ", target_pos, " pulse"
            self.hfm_y.move(target_pos)


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    mirror = Mirror(s)

    # mirror.setVFM_y(self,pulse):
    # mirror.setHFM_z(self,pulse):
    # self.hfm_z.move(pulse)

    valu = mirror.getVFM_y()
    mirror.setVFM_y(valu + 100)
    print mirror.getVFM_y()
    mirror.setVFM_y(valu)
    print mirror.getVFM_y()

    # print mirror.getHFM_z()

    s.close()
