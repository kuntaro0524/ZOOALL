#!/bin/env python 
import sys
import socket
import time
import datetime

# My library
from Received import *
from Motor import *
import BSSconfig
from MyException import *
from configparser import ConfigParser, ExtendedInterpolation

class Colli:
    def __init__(self, server):
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        # beamline.ini 
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])

        self.s = server
        # names of collimator axes
        # coly > section: axes, option: col_y_name
        self.coly_axis = self.config.get("axes", "col_y_name")
        # colz > section: axes, option: col_z_name
        self.colz_axis = self.config.get("axes", "col_z_name")

        self.coly = Motor(self.s, "bl_%s_%s" %(self.bl_object, self.coly_axis), "pulse")
        self.colz = Motor(self.s, "bl_%s_%s" %(self.bl_object, self.colz_axis), "pulse")
        # pulse information of each axis
        self.v2p_y, self.sense_y = self.bssconf.getPulseInfo(self.coly_axis)
        self.v2p_z, self.sense_z = self.bssconf.getPulseInfo(self.colz_axis)

        print(self.v2p_y, self.sense_y, self.v2p_z, self.sense_z)

        self.isInit = False

    # 退避する軸はビームラインごとに違っているのでそれを取得する必要がある。
    # 現時点では１軸しか取得できないのでそうでないビームライン（ビームストッパーをYZどちらも退避）が出てくると修正する必要がある
    def getEvacuate(self):
        evacinfo = self.config.get("axes", "col_evacinfo")
        self.evac_axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateInfo(evacinfo)
        print("ON (VME value):",self.on_pulse)
        print("OFF(VME value):",self.off_pulse)
        # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
        self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
        self.isInit = True

    def getY(self):
        tmp = int(self.coly.getPosition()[0])
        return tmp

    def getZ(self):
        tmp = int(self.colz.getPosition()[0])
        return tmp

    def on(self):
        if self.isInit == False:
            self.getEvacuate()
        self.evac_axis.move(self.on_pulse)

    def off(self):
        if self.isInit == False:
            self.getEvacuate()
        self.evac_axis.move(self.off_pulse)

    # 2023/04/12 Temp mod.
    def offY(self):
        self.coly.move(self.evac_y_axis_off)
        #self.coly.move(-4000)

    def onY(self):
        self.coly.move(self.evac_y_axis_on)

    def goOn(self):
        if self.isInit == False:
            self.getEvacuate()
        self.go(self.on_pos)

    def goOff(self):
        if self.isInit == False:
            self.getEvacuate()
        self.go(self.off_pos)

    def compareOnOff(self, ch):
        # counter initialization
        counter = Count(self.s, ch, 0)

        # off position
        self.off()
        cnt_off = float(counter.getCount(1.0)[0])

        # on position
        self.on()
        cnt_on = float(counter.getCount(1.0)[0])

        # transmission
        trans = cnt_on / cnt_off * 100.0

        return trans, cnt_on

    def scanCore(self, prefix, ch):
        ofile = "%s_colliz.scn" % prefix
        before_zp = self.colz.getPosition()[0]
        before_zm = before_zp
        print("Current value=%8d\n" % before_zp)

        ###
        # Scan setting
        ###
        cnt_ch = ch
        cnt_ch2 = 0
        cnt_time = 0.1
        unit = "pulse"

        ####
        # Z scan condition [mm]
        ####
        # scan_start=-0.25
        # scan_end=0.25
        # scan_step=0.005

        scan_start = -0.10
        scan_end = 0.10
        scan_step = 0.002

        ####
        # Z scan condition [pulse]
        ####
        scan_start_p = scan_start * self.z_v2p
        scan_end_p = scan_end * self.z_v2p
        scan_step_p = scan_step * self.z_v2p

        ####
        # Set scan condition
        ####
        self.colz.setStart(scan_start_p)
        self.colz.setEnd(scan_end_p)
        self.colz.setStep(scan_step_p)

        self.colz.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)

        # Analysis and Plot
        outfig = prefix + "_colliz.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()

        try:
            fwhm, center = ana.analyzeAll("colliZ[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")
            print(fwhm, center)
            fwhm_z = fwhm / 2.0  # [um]
        except MyException as ttt:
            self.colz.move(0)
            err_log01 = "%s\n" % ttt.args[0]
            err_log02 = "Collimetor Z scan failed\n"
            err_all = err_log01 + err_log02
            raise MyException(err_all)

        print("setting collimeter Z")
        self.colz.move(center)
        self.colz.preset(0)
        print("setting collimeter Z")

        cenz = float(center)

        ####
        # Y scan condition[mm]
        ####
        scan_start = -0.1
        scan_end = 0.1
        scan_step = 0.002

        ####
        # Y scan condition [pulse]
        ####
        scan_start_p = scan_start * self.y_v2p
        scan_end_p = scan_end * self.y_v2p
        scan_step_p = scan_step * self.y_v2p

        ####
        # Set scan condition
        ####
        self.coly.setStart(scan_start_p)
        self.coly.setEnd(scan_end_p)
        self.coly.setStep(scan_step_p)

        ofile = "%s_colliy.scn" % prefix
        self.coly.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)

        # Analysis and Plot
        outfig = prefix + "_colliy.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()

        try:
            fwhm, center = ana.analyzeAll("colliY[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")
            fwhm_y = fwhm * 2.0  # [um]
        except MyException as ttt:
            self.coly.move(0)
            err_log01 = "%s\n" % ttt.args[0]
            err_log02 = "Collimetor Y scan failed\n"
            err_all = err_log01 + err_log02
            raise MyException(err_all)

        self.coly.move(center)
        self.coly.preset(0)
        ceny = float(center)

        print("FWHM Z:%8.2f[um] Y:%8.2f[um]" % (fwhm_z, fwhm_y))
        return fwhm_y, fwhm_z, ceny, cenz

    def scanWithoutPreset(self, prefix, ch, width_mm):
        ofile = "%s_colliz.scn" % prefix

        before_zp = self.colz.getPosition()[0]
        before_zm = before_zp
        print("Current value=%8d\n" % before_zp)

        ###
        # Scan setting

    def scan(self, prefix, ch):
        ofile = "%s_colliz.scn" % prefix

        before_zp = self.colz.getPosition()[0]
        before_zm = before_zp
        print("Current value=%8d\n" % before_zp)

        ###
        # Scan setting
        ###
        cnt_ch = ch
        cnt_ch2 = 0
        cnt_time = 0.2
        unit = "pulse"

        ####
        # Z scan condition [mm]
        ####
        # scan_start=-0.25
        # scan_end=0.25
        # scan_step=0.005

        scan_start = -0.10
        scan_end = 0.10
        scan_step = 0.002

        ####
        # Z scan condition [pulse]
        ####
        scan_start_p = scan_start * self.z_v2p
        scan_end_p = scan_end * self.z_v2p
        scan_step_p = scan_step * self.z_v2p

        ####
        # Set scan condition
        ####
        self.colz.setStart(scan_start_p)
        self.colz.setEnd(scan_end_p)
        self.colz.setStep(scan_step_p)

        self.colz.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)

        # Analysis and Plot
        outfig = prefix + "_colliz.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()

        fwhm, center = ana.analyzeAll("colliZ[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")
        fwhm_z = fwhm / 2.0  # [um]
        self.colz.move(center)
        self.colz.preset(0)

        cenz = float(center)

        ####
        # Y scan condition[mm]
        ####
        scan_start = -0.1
        scan_end = 0.1
        scan_step = 0.002

        ####
        # Y scan condition [pulse]
        ####
        scan_start_p = scan_start * self.y_v2p
        scan_end_p = scan_end * self.y_v2p
        scan_step_p = scan_step * self.y_v2p

        ####
        # Set scan condition
        ####
        self.coly.setStart(scan_start_p)
        self.coly.setEnd(scan_end_p)
        self.coly.setStep(scan_step_p)

        ofile = "%s_colliy.scn" % prefix
        self.coly.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)

        # Analysis and Plot
        outfig = prefix + "_colliy.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()

        fwhm, center = ana.analyzeAll("colliY[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")
        fwhm_y = fwhm * 2.0  # [um]
        self.coly.move(center)
        self.coly.preset(0)
        ceny = float(center)

        print("FWHM Z:%8.2f[um] Y:%8.2f[um]" % (fwhm_z, fwhm_y))
        return ceny, cenz

    def scanWithoutPreset(self, prefix, ch, width_mm):
        ofile = "%s_colliz.scn" % prefix

        before_zp = self.colz.getPosition()[0]
        before_zm = before_zp
        print("Current value=%8d\n" % before_zp)

        ###
        # Scan setting
        ###
        cnt_ch = ch
        cnt_ch2 = 1
        cnt_time = 0.2
        unit = "pulse"

        ####
        # Z scan condition [mm]
        ####
        scan_start = -width_mm
        scan_end = width_mm
        scan_step = 0.002

        ####
        # Z scan condition [pulse]
        ####
        scan_start_p = scan_start * self.z_v2p
        scan_end_p = scan_end * self.z_v2p
        scan_step_p = scan_step * self.z_v2p

        ####
        # Set scan condition
        ####
        self.colz.setStart(scan_start_p)
        self.colz.setEnd(scan_end_p)
        self.colz.setStep(scan_step_p)

        self.colz.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)

        # Analysis and Plot
        outfig = prefix + "_colliz.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()

        try:
            fwhm, center = ana.analyzeAll("colliZ[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")
            fwhm_z = fwhm / 2.0  # [um]
        except MyException as ttt:
            print("Collimeter scan failed")
            print(ttt.args[0])
            return 0, 0, 30, 30

        self.colz.move(center)
        cenz = float(center)

        ####
        # Y scan condition[mm]
        ####
        scan_start = -width_mm
        scan_end = width_mm
        scan_step = 0.002

        ####
        # Y scan condition [pulse]
        ####
        scan_start_p = scan_start * self.y_v2p
        scan_end_p = scan_end * self.y_v2p
        scan_step_p = scan_step * self.y_v2p

        ####
        # Set scan condition
        ####
        self.coly.setStart(scan_start_p)
        self.coly.setEnd(scan_end_p)
        self.coly.setStep(scan_step_p)

        ofile = "%s_colliy.scn" % prefix
        self.coly.axisScan(ofile, cnt_ch, cnt_ch2, cnt_time)

        # Analysis and Plot
        outfig = prefix + "_colliy.png"
        ana = AnalyzePeak(ofile)
        strtime = datetime.datetime.now()

        fwhm, center = ana.analyzeAll("colliY[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")
        fwhm_y = fwhm * 2.0  # [um]
        self.coly.move(center)
        ceny = float(center)

        # print "FWHM Z:%8.2f[um] Y:%8.2f[um]"%(fwhm_z,fwhm_y)
        try:
            fwhm, center = ana.analyzeAll("colliY[pulse]", "Intensity", outfig, strtime, "OBS", "JJJJ")
            fwhm_y = fwhm * 2.0  # [um]
        except MyException as ttt:
            print("Collimeter scan failed")
            print(ttt.args[0])
            return 0, 0, 30, 30

        return ceny, cenz, fwhm_z, fwhm_y

    def moveY(self, pls):
        v = pls
        self.coly.move(v)

    def moveZ(self, pls):
        v = pls
        self.colz.move(v)

    def scan2D(self, prefix, startz, endz, stepz, starty, endy, stepy):
        counter = Count(self.s, 3, 0)
        oname = "%s_colli_2d.scn" % prefix
        of = open(oname, "w")

        save_y = self.getY()
        save_z = self.getZ()

        print(save_y, save_z)

        for z in arange(startz, endz + stepz, stepz):
            self.moveZ(z)
            for y in range(starty, endy + stepy, stepy):
                self.moveY(y)
                cnt = int(counter.getCount(0.2)[0])
                of.write("%5d %5d %12d\n" % (y, z, cnt))
                of.flush()
            of.write("\n")
        of.close()

        self.moveY(save_y)
        self.moveZ(save_z)

    def isMoved(self):
        isY = self.coly.isMoved()
        isZ = self.colz.isMoved()

        if isY == 0 and isZ == 0:
            return True
        if isY == 1 and isZ == 1:
            return False


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    coli = Colli(s)
    coli.getEvacuate()
    coli.off()
    coli.on()
    # coli.scan("colllli",0)

    # print coli.getY()
    # coli.moveZ(1000)
    # coli.moveZ(0)
    # coli.scan2D()
    # coli.scanCore("test",3)
    print((coli.getY()))
    # coli.on()
    # coli.off()
    # def scan2D(self,prefix,startz,endz,stepz,starty,endy,stepy):
    # coli.goOff()
    s.close()
