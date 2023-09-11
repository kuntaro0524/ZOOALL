#!/bin/env python 
z2corr = False  # 150918 Monochromator Z2 flag #Read 'calcZ2' part
import sys
import socket
import time

# My library
from AnalyzePeak import *
from Motor import *
from AxesInfo import *
from ConfigFile import *
from TCS import *
from MyException import *


class Mono:

    def __init__(self, srv):
        self.m_dtheta1 = Motor(srv, "bl_32in_tc1_stmono_1_dtheta1", "pulse")
        self.m_theta = Motor(srv, "bl_32in_tc1_stmono_1", "pulse")
        self.m_thetay1 = Motor(srv, "bl_32in_tc1_stmono_1_thetay1", "pulse")
        self.m_zt = Motor(srv, "bl_32in_tc1_stmono_1_zt", "pulse")
        self.m_z2 = Motor(srv, "bl_32in_tc1_stmono_1_z2", "pulse")

        self.m_energy = Motor(srv, "bl_32in_tc1_stmono_1", "kev")
        self.m_wave = Motor(srv, "bl_32in_tc1_stmono_1", "angstrom")
        self.s = srv

    def getE(self):
        return (self.m_energy.getEnergy()[0])

    def getDt1(self):
        return (int(self.m_dtheta1.getPosition()[0]))

    def changeE(self, energy):
        if z2corr == True:
            z2 = self.calcZ2(energy)
            self.moveZ2(z2)
        self.m_energy.move(energy)

    def calcZ2_till_151021(self, energy):
        # 150918 K.Hirata wrote
        # At this time, monochromator dt2 cannot be tuned.
        # Data collection of correlation among Energy, Z2,
        # and vertical beam position just before mirror
        # chamber (ExSlit1 vertical knife edge scan).
        # Then the following equation can be utilized for
        # estimation of Z2 for each energy.
        # Please see 150917/04..../Matome/*.png
        z2float = 213.2 * energy + 412
        z2int = int(z2float)
        print("estimated Z2 is ", z2int)
        return z2int

    def calcZ2(self, energy):
        # 151021 K.Hirata wrote
        # At this time, monochromator dt2 cannot be tuned.
        # Data collection of correlation among Energy, Z2,
        # and vertical beam position just before mirror
        # chamber (ExSlit1 vertical knife edge scan).
        # Then the following equation can be utilized for
        # estimation of Z2 for each energy.
        # Please see /isilon/users/target/target/Staff/2015B/151020/03.MakeTableTy1Z2/Z2.plt
        z2float = 269.65 * energy - 279.715
        z2int = int(z2float)
        print("estimated Z2 is ", z2int)
        return z2int

    def changeWL(self, wavelength):
        self.m_wave.move(wavelength)

    def moveDt1(self, position):
        self.m_dtheta1.move(position)

    def moveDt1Rel(self, value):
        self.m_dtheta1.relmove(value)

    def moveTy1(self, position):
        self.m_thetay1.move(position)

    def moveZ2(self, position):
        self.m_z2.move(position)

    def moveZt(self, position):
        if position < -5000 or position > 5000:
            print("Zt error!")
            return False

        self.m_zt.move(position)

    def scanEnergy(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # Setting
        ofile = prefix + "_escan.scn"

        # Condition
        self.m_energy.setStart(start)
        self.m_energy.setEnd(end)
        self.m_energy.setStep(step)
        maxval = self.m_energy.axisScan(ofile, cnt_ch1, cnt_ch2, time)

    def scanDt1(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # Setting
        ofile = prefix + "_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        maxval = self.m_dtheta1.axisScan(ofile, cnt_ch1, cnt_ch2, time)

        # Analysis and Plot
        outfig = prefix + "_dtheta1.png"
        ana = AnalyzePeak(ofile)
        comment = AxesInfo(self.s).getLeastInfo()
        # comment="during debugging : sorry...\n"

        fwhm, center = ana.analyzeAll("dtheta1[pulse]", "Intensity", outfig, comment, "OBS", "FCEN")

        self.m_dtheta1.move(int(center))
        return fwhm, center

    def scanDt1Peak(self, prefix, start, end, step, cnt_ch1, cnt_ch2, sec):
        # Setting
        ofile = prefix + "_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        backlash = 2000

        maxval = self.m_dtheta1.axisScan(ofile, cnt_ch1, cnt_ch2, sec)

        counter_1_max = maxval[0]
        print("Peak: %5d\n" % counter_1_max)

        # Analysis and Plot
        outfig = prefix + "_dtheta1.png"
        ana = AnalyzePeak(ofile)
        comment = AxesInfo(self.s).getLeastInfo()
        fwhm, center = ana.analyzeAll("dtheta1[pulse]", "Intensity", outfig, comment, "OBS", "PEAK")

        # back lash position
        bl_pos = counter_1_max - backlash

        # back lash
        self.m_dtheta1.move(bl_pos)
        n_move = int(backlash / step)

        # Setting the actual value
        for i in range(0, n_move):
            self.m_dtheta1.relmove(step)

        # print self.m_dtheta1.getPosition()

        return fwhm, center

    def scanDt1Config(self, prefix, confchar, tcs):
        conf = ConfigFile()
        try:
            ## Dtheta 1
            ch1 = int(conf.getCondition2(confchar, "ch1"))
            ch2 = int(conf.getCondition2(confchar, "ch2"))
            start = int(conf.getCondition2(confchar, "start"))
            end = int(conf.getCondition2(confchar, "end"))
            step = int(conf.getCondition2(confchar, "step"))
            time = conf.getCondition2(confchar, "time")
            tcsv = conf.getCondition2(confchar, "tcsv")
            tcsh = conf.getCondition2(confchar, "tcsh")
            detune_pls = int(conf.getCondition2(confchar, "detune"))

        except MyException as ttt:
            print(ttt.args[0])
            print("Check your config file carefully.\n")

        # Setting tcs
        tcs.setApert(tcsv, tcsh)

        # Setting
        ofile = prefix + "_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        backlash = 2000 + detune_pls

        maxval = self.m_dtheta1.axisScan(ofile, ch1, ch2, time)

        counter_1_max = maxval[0] + detune_pls
        print("Peak: %5d\n" % counter_1_max)

        return counter_1_max

    def scanNEW(self, prefix, confchar, tcs):
        conf = ConfigFile()
        try:
            ## Dtheta 1
            ch1 = int(conf.getCondition2(confchar, "ch1"))
            ch2 = int(conf.getCondition2(confchar, "ch2"))
            start = int(conf.getCondition2(confchar, "start"))
            end = int(conf.getCondition2(confchar, "end"))
            step = int(conf.getCondition2(confchar, "step"))
            time = conf.getCondition2(confchar, "time")
            tcsv = conf.getCondition2(confchar, "tcsv")
            tcsh = conf.getCondition2(confchar, "tcsh")
            detune_pls = int(conf.getCondition2(confchar, "detune"))

        except MyException as ttt:
            print(ttt.args[0])
            print("Check your config file carefully.\n")

        # Setting tcs
        tcs.setApert(tcsv, tcsh)

        # Setting
        ofile = prefix + "_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(100)

        backlash = 2000 + detune_pls

        # Find max of channel 1
        print(self.m_dtheta1.findMax(ch1, time))
        print("Peak: %5d\n" % maxval)

        return maxval

    def scanDt1PeakConfig(self, prefix, confchar, tcs):
        conf = ConfigFile()
        try:
            ## Dtheta 1
            ch1 = int(conf.getCondition2(confchar, "ch1"))
            ch2 = int(conf.getCondition2(confchar, "ch2"))
            start = int(conf.getCondition2(confchar, "start"))
            end = int(conf.getCondition2(confchar, "end"))
            step = int(conf.getCondition2(confchar, "step"))
            time = conf.getCondition2(confchar, "time")
            tcsv = conf.getCondition2(confchar, "tcsv")
            tcsh = conf.getCondition2(confchar, "tcsh")
            detune_pls = int(conf.getCondition2(confchar, "detune"))

        except MyException as ttt:
            print(ttt.args[0])
            print("Check your config file carefully.\n")

        # Setting tcs
        tcs.setApert(tcsv, tcsh)

        # Setting
        ofile = prefix + "_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        backlash = 2000

        maxval = self.m_dtheta1.axisScan(ofile, ch1, ch2, time)

        counter_1_max = maxval[0] + detune_pls
        #        print "Peak: %5d\n"%counter_1_max
        print("Peak: %5d pls\n" % maxval[0])
        print("detune: %5d pls\n" % detune_pls)
        print("target pos: %5d pls\n" % counter_1_max)

        # Analysis and Plot
        outfig = prefix + "_dtheta1.png"
        ana = AnalyzePeak(ofile)
        comment = AxesInfo(self.s).getLeastInfo()
        try:
            fwhm, center = ana.analyzeAll("dtheta1[pulse]", "Intensity", outfig, comment, "OBS", "PEAK")
        except MyException as ttt:
            raise MyException("Dtheta1 tune peak analysis failed.%s" % ttt.args[0])

        if fwhm == 0.0:
            raise MyException("Bad peak shape!!")

        # back lash position
        bl_pos = counter_1_max - backlash

        # back lash
        self.m_dtheta1.move(bl_pos)
        # print self.m_dtheta1.getPosition()
        n_move = int(backlash / step)

        # Setting the actual value
        for i in range(0, n_move):
            self.m_dtheta1.relmove(step)

        # print self.m_dtheta1.getPosition()

        return fwhm, center

    def scanDt1PeakConfigExceptForDetune(self, prefix, confchar, tcs, detune):
        conf = ConfigFile()
        try:
            ## Dtheta 1
            ch1 = int(conf.getCondition2(confchar, "ch1"))
            ch2 = int(conf.getCondition2(confchar, "ch2"))
            start = int(conf.getCondition2(confchar, "start"))
            end = int(conf.getCondition2(confchar, "end"))
            step = int(conf.getCondition2(confchar, "step"))
            time = conf.getCondition2(confchar, "time")
            tcsv = conf.getCondition2(confchar, "tcsv")
            tcsh = conf.getCondition2(confchar, "tcsh")
            detune_pls = int(conf.getCondition2(confchar, "detune"))

        except MyException as ttt:
            print(ttt.args[0])
            print("Check your config file carefully.\n")

        detune_pls = detune
        # Setting tcs
        tcs.setApert(tcsv, tcsh)

        # Setting
        ofile = prefix + "_dtheta1.scn"

        # Condition
        self.m_dtheta1.setStart(start)
        self.m_dtheta1.setEnd(end)
        self.m_dtheta1.setStep(step)

        backlash = 2000

        maxval = self.m_dtheta1.axisScan(ofile, ch1, ch2, time)

        counter_1_max = maxval[0] + detune_pls
        print("Peak: %5d\n" % counter_1_max)

        # Analysis and Plot
        outfig = prefix + "_dtheta1.png"
        ana = AnalyzePeak(ofile)
        comment = AxesInfo(self.s).getLeastInfo()
        try:
            fwhm, center = ana.analyzeAll("dtheta1[pulse]", "Intensity", outfig, comment, "OBS", "PEAK")
        except MyException as ttt:
            raise MyException("Dtheta1 tune peak analysis failed.%s" % ttt.args[0])

        if fwhm == 0.0:
            raise MyException("Bad peak shape!!")

        # back lash position
        bl_pos = counter_1_max - backlash

        # back lash
        self.m_dtheta1.move(bl_pos)
        # print self.m_dtheta1.getPosition()
        n_move = int(backlash / step)

        # Setting the actual value
        for i in range(0, n_move):
            self.m_dtheta1.relmove(step)

        # print self.m_dtheta1.getPosition()

        return fwhm, counter_1_max


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    mono = Mono(s)
    mono.moveZ2(1627)
    s.close()
