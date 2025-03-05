#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *
from AnalyzePeak import *
from File import *
from AxesInfo import *

<<<<<<< HEAD

=======
>>>>>>> zoo45xu/main
class ExSlit1:

    def __init__(self, server):
        self.s = server
<<<<<<< HEAD
        self.blade_upper = Motor(self.s, "bl_32in_st2_slit_1_upper", "pulse")
        self.blade_ring = Motor(self.s, "bl_32in_st2_slit_1_ring", "pulse")
        self.blade_lower = Motor(self.s, "bl_32in_st2_slit_1_lower", "pulse")

    def getVpos(self):
        pos = self.blade_lower.getPosition()
        print(pos)
=======
        self.blade_width = Motor(self.s, "bl_45in_st2_slit_1_width", "mm")
        self.blade_height = Motor(self.s, "bl_45in_st2_slit_1_height", "mm")
        self.blade_horizontal = Motor(self.s, "bl_45in_st2_slit_1_horizontal", "mm")
        self.blade_vertical = Motor(self.s, "bl_45in_st2_slit_1_vertical", "mm")

        # Each blade
        self.blade_upper = Motor(self.s, "bl_45in_st2_slit_1_upper", "pulse")
        self.blade_lower = Motor(self.s, "bl_45in_st2_slit_1_lower", "pulse")
        self.blade_ring = Motor(self.s, "bl_45in_st2_slit_1_ring", "pulse")
        self.blade_hall = Motor(self.s, "bl_45in_st2_slit_1_hall", "pulse")

    def getBladePos(self):
        u = self.blade_upper.getPosition()
        l = self.blade_lower.getPosition()
        r = self.blade_ring.getPosition()
        h = self.blade_hall.getPosition()

        return u,l,r,h

    def getVpos(self):
        pos = self.blade_lower.getPosition()
        print pos
>>>>>>> zoo45xu/main

    def openV(self):
        # self.blade_upper.move(18000)
        self.blade_lower.move(-18000)

    def closeV(self):
        # self.blade_upper.move(300)
        self.blade_lower.move(-300)

    def fullOpen(self):
        self.blade_upper.move(18000)
        self.blade_lower.move(-18000)
        self.blade_ring.move(-18000)

    def scanV(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # Scan setting
        #                self.blade_upper.setStart(start)
        #                self.blade_upper.setEnd(end)
        #                self.blade_upper.setStep(step)
        self.blade_lower.setStart(start)
        self.blade_lower.setEnd(end)
        self.blade_lower.setStep(step)

        # output file
        ofile = "%s_slit1_vert.scn" % prefix
        #		self.blade_upper.axisScan(ofile,cnt_ch1,cnt_ch2,time)
        self.blade_lower.axisScan(ofile, cnt_ch1, cnt_ch2, time)

        # Analysis and Plot
        comment = AxesInfo(self.s).getLeastInfo()
        ana = AnalyzePeak(ofile)
        fwhm, center = ana.anaK("slit1 upper[pulse]", "intensity[cnt]", comment)
        return fwhm, center

    def scanVquick(self, prefix, cnt_ch1, cnt_ch2, time):
        counter = Count(self.s, cnt_ch1, cnt_ch2)

        # Rough scan
        save_i = 0.0
        for vtmp in range(-18000, 0, 2000):
            self.blade_lower.move(vtmp)
            value0 = int(counter.getCount(1.0)[0])
<<<<<<< HEAD
            print(vtmp, value0)
=======
            print  vtmp, value0
>>>>>>> zoo45xu/main
            if value0 < save_i / 2.0:
                roughv = vtmp
                break
            save_i = value0

<<<<<<< HEAD
        print(vtmp)
=======
        print vtmp
>>>>>>> zoo45xu/main
        save_i = 0.0
        for vtmp in range(roughv - 2000, roughv + 2000, 400):
            self.blade_lower.move(vtmp)
            value0 = int(counter.getCount(1.0)[0])
<<<<<<< HEAD
            print(vtmp, value0)
=======
            print  vtmp, value0
>>>>>>> zoo45xu/main
            if value0 < save_i / 2.0:
                roughv = vtmp
                break
            save_i = value0
<<<<<<< HEAD
        print(roughv)
=======
        print roughv
>>>>>>> zoo45xu/main

        self.scanV(prefix, roughv - 2000, roughv + 2000, 100, cnt_ch1, cnt_ch2, 1.0)

    def scanH(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # Scan setting
        self.blade_ring.setStart(start)
        self.blade_ring.setEnd(end)
        self.blade_ring.setStep(step)

        # output file
        ofile = "%s_slit1_hori.scn" % prefix
        self.blade_ring.axisScan(ofile, cnt_ch1, cnt_ch2, time)

        # Analysis and Plot
        comment = AxesInfo(self.s).getLeastInfo()

        ana = AnalyzePeak(ofile)
        fwhm, center = ana.anaK("slit1 ring[pulse]", "intensity[cnt]", comment)
        return fwhm, center


if __name__ == "__main__":
<<<<<<< HEAD
    host = '172.24.242.41'
=======
    host = '172.24.242.59'
>>>>>>> zoo45xu/main
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

<<<<<<< HEAD
    print("prog PREFIX CHANNEL")
    test = ExSlit1(s)
    f = File("./")
    test.openV()
# test.closeV()
# test.scanVquick("TEST",3,0,0.2)

# prefix="%03d"%f.getNewIdx3()
# test.scanV(prefix,15000,500,-500,3,0,0.2)

# prefix="%03d"%f.getNewIdx3()
# test.scanH(prefix,-18010,-10,50,3,0,0.2)
=======
    print "prog PREFIX CHANNEL"
    test = ExSlit1(s)
    print test.getBladePos()
>>>>>>> zoo45xu/main
