<<<<<<< HEAD
# -*- coding: utf-8 -*-
=======
>>>>>>> zoo45xu/main
#!/bin/env python 
import sys
import socket
import time
import datetime
<<<<<<< HEAD
import WebSocketBSS
import os
=======
>>>>>>> zoo45xu/main

# My library
from Received import *
from Motor import *
<<<<<<< HEAD
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
        # beamline name
        self.beamline = self.config.get("beamline", "beamline")

        self.s = server
        # names of collimator axes
        self.coly_axis = ""
        self.colz_axis = ""
        # coly > section: axes, option: col_y_name
        try:
            self.coly_axis = self.config.get("axes", "col_y_name")
        except:
            # display 'warning' if the option is not found
            print("WARNING: col_y_name is not found in beamline.ini")

        try:
            # colz > section: axes, option: col_z_name
            self.colz_axis = self.config.get("axes", "col_z_name")
        except:
            # display 'warning' if the option is not found
            print("WARNING: col_z_name is not found in beamline.ini")

        # if 'coly' exists in the configuration file.
        if self.coly_axis != "":
            self.coly = Motor(self.s, "bl_%s_%s" %(self.bl_object, self.coly_axis), "pulse")
            # pulse information of each axis
            self.v2p_y, self.sense_y, self.home_y = self.bssconf.getPulseInfo(self.coly_axis)
        if self.colz_axis != "":
            self.colz = Motor(self.s, "bl_%s_%s" %(self.bl_object, self.colz_axis), "pulse")
            print("Searching %s" % self.colz_axis)
            # print("bl_%s_%s" %(self.bl_object, self.colz_axis))
            # pulse information of each axis
            self.v2p_z, self.sense_z, self.home_z = self.bssconf.getPulseInfo(self.colz_axis)

        # BL41XU web socket system
        self.websock = WebSocketBSS.WebSocketBSS()

        self.isInit = False
        # Evacuation axis list
        self.evac_axes = []

    # 退避する軸はビームラインごとに違っているのでそれを取得する必要がある。
    # 現時点では１軸しか取得できないのでそうでないビームライン（ビームストッパーをYZどちらも退避）が出てくると修正する必要がある
    def getEvacuate(self):
        self.evac_dict = {}

        if self.beamline == "BL41XU":
            print("BL41XU!!!")
            # The 1st evacuation information of collimator
            evacinfo = self.config.get("axes", "col_evacinfo")
            self.evac_axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateInfo(evacinfo)
            print("Evac axis:",self.evac_axis_name)
            print("ON (VME value):",self.on_pulse)
            print("OFF(VME value):",self.off_pulse)
            # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
            print("BLO=bl_%s_%s" % (self.bl_object, self.evac_axis_name))
            self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
            # dictionary of evacuation axes
            tmp_evac_dict = {"name":self.evac_axis_name, "on":self.on_pulse, "off":self.off_pulse, "axis":self.evac_axis}
            self.evac_axes.append(tmp_evac_dict)

            # 2nd collimator axis
            self.evac_axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateInfo(evacinfo, the_2nd=True)
            print("Evac axis:",self.evac_axis_name)
            print("ON (VME value):",self.on_pulse)
            print("OFF(VME value):",self.off_pulse)
            # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
            print("BLO=bl_%s_%s" % (self.bl_object, self.evac_axis_name))
            self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
            # dictionary of evacuation axes
            tmp_evac_dict = {"name":self.evac_axis_name, "on":self.on_pulse, "off":self.off_pulse, "axis":self.evac_axis}
            self.evac_axes.append(tmp_evac_dict)

            self.isInit = True
        # other beamlines: evacuation is a single axis
        # The codes should be checked at BL32XU/BL44XU especially after 2024/06/27
        else:
            evacinfo = self.config.get("axes", "col_evacinfo")
            self.evac_axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateInfo(evacinfo)
            print("Evac axis:",self.evac_axis_name)
            print("ON (VME value):",self.on_pulse)
            print("OFF(VME value):",self.off_pulse)
            # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
            print("BLO=bl_%s_%s" % (self.bl_object, self.evac_axis_name))
            self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
            tmp_evac_dict = {"name":self.evac_axis_name, "on":self.on_pulse, "off":self.off_pulse, "axis":self.evac_axis}
            self.evac_axes.append(tmp_evac_dict)
            self.isInit = True
=======
from BSSconfig import *
from MyException import *

#
class Colli:
    def __init__(self, server):
        self.s = server
        self.coly = Motor(self.s, "bl_45in_st2_col_1_y", "pulse")
        self.colz = Motor(self.s, "bl_45in_st2_col_1_z", "pulse")

        self.off_pos = -20000  # pulse
        self.on_pos = 0  # pulse

        self.y_v2p = 500  # pulse/mm
        self.z_v2p = 2000  # pulse/mm

        self.isInit = False

    def go(self, pvalue):
        self.colz.nageppa(pvalue)

    def getEvacuate(self):
        bssconf = BSSconfig()

        try:
            tmpon, tmpoff = bssconf.getColli()
        except MyException, ttt:
            print ttt.args[0]

        self.on_pos = float(tmpon) * self.z_v2p
        self.off_pos = float(tmpoff) * self.z_v2p

        self.isInit = True
        print self.on_pos, self.off_pos
>>>>>>> zoo45xu/main

    def getY(self):
        tmp = int(self.coly.getPosition()[0])
        return tmp

    def getZ(self):
        tmp = int(self.colz.getPosition()[0])
        return tmp

<<<<<<< HEAD
    def getEvacZ(self):
        tmp = self.evac_axis.getPosition()[0]
        return tmp

    def on(self):
        if self.beamline == "BL41XU":
            self.websock.collimator("on")
        else:
            if self.isInit == False:
                self.getEvacuate()
            # sense 
            for each_axis in self.evac_axes:
                on_pulse = each_axis["on"]
                print("on_pulse:",on_pulse)
                each_axis['axis'].move(on_pulse)

    def off(self):
        if self.beamline == "BL41XU":
            self.websock.collimator("off")
        else:
            if self.isInit == False:
                self.getEvacuate()
            for each_axis in self.evac_axes:
                off_pulse = each_axis["off"]
                print("off_pulse:",off_pulse)
                each_axis["axis"].move(off_pulse)

    # 2023/04/12 Temp mod.
    def offY(self):
        self.coly.move(self.evac_y_axis_off)

    def onY(self):
        self.coly.move(self.evac_y_axis_on)
=======
    def on(self):
        if self.isInit == False:
            self.getEvacuate()
        self.colz.move(self.on_pos)

    def off(self):
        if self.isInit == False:
            self.getEvacuate()
        self.colz.move(self.off_pos)
>>>>>>> zoo45xu/main

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
<<<<<<< HEAD
        print("Current value=%8d\n" % before_zp)
=======
        print "Current value=%8d\n" % before_zp
>>>>>>> zoo45xu/main

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
<<<<<<< HEAD
            print(fwhm, center)
            fwhm_z = fwhm / 2.0  # [um]
        except MyException as ttt:
=======
            print fwhm, center
            fwhm_z = fwhm / 2.0  # [um]
        except MyException, ttt:
>>>>>>> zoo45xu/main
            self.colz.move(0)
            err_log01 = "%s\n" % ttt.args[0]
            err_log02 = "Collimetor Z scan failed\n"
            err_all = err_log01 + err_log02
            raise MyException(err_all)

<<<<<<< HEAD
        print("setting collimeter Z")
        self.colz.move(center)
        self.colz.preset(0)
        print("setting collimeter Z")
=======
        print "setting collimeter Z"
        self.colz.move(center)
        self.colz.preset(0)
        print "setting collimeter Z"
>>>>>>> zoo45xu/main

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
<<<<<<< HEAD
        except MyException as ttt:
=======
        except MyException, ttt:
>>>>>>> zoo45xu/main
            self.coly.move(0)
            err_log01 = "%s\n" % ttt.args[0]
            err_log02 = "Collimetor Y scan failed\n"
            err_all = err_log01 + err_log02
            raise MyException(err_all)

        self.coly.move(center)
        self.coly.preset(0)
        ceny = float(center)

<<<<<<< HEAD
        print("FWHM Z:%8.2f[um] Y:%8.2f[um]" % (fwhm_z, fwhm_y))
=======
        print "FWHM Z:%8.2f[um] Y:%8.2f[um]" % (fwhm_z, fwhm_y)
>>>>>>> zoo45xu/main
        return fwhm_y, fwhm_z, ceny, cenz

    def scanWithoutPreset(self, prefix, ch, width_mm):
        ofile = "%s_colliz.scn" % prefix

        before_zp = self.colz.getPosition()[0]
        before_zm = before_zp
<<<<<<< HEAD
        print("Current value=%8d\n" % before_zp)
=======
        print "Current value=%8d\n" % before_zp
>>>>>>> zoo45xu/main

        ###
        # Scan setting

    def scan(self, prefix, ch):
        ofile = "%s_colliz.scn" % prefix

        before_zp = self.colz.getPosition()[0]
        before_zm = before_zp
<<<<<<< HEAD
        print("Current value=%8d\n" % before_zp)
=======
        print "Current value=%8d\n" % before_zp
>>>>>>> zoo45xu/main

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

<<<<<<< HEAD
        print("FWHM Z:%8.2f[um] Y:%8.2f[um]" % (fwhm_z, fwhm_y))
=======
        print "FWHM Z:%8.2f[um] Y:%8.2f[um]" % (fwhm_z, fwhm_y)
>>>>>>> zoo45xu/main
        return ceny, cenz

    def scanWithoutPreset(self, prefix, ch, width_mm):
        ofile = "%s_colliz.scn" % prefix

        before_zp = self.colz.getPosition()[0]
        before_zm = before_zp
<<<<<<< HEAD
        print("Current value=%8d\n" % before_zp)
=======
        print "Current value=%8d\n" % before_zp
>>>>>>> zoo45xu/main

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
<<<<<<< HEAD
        except MyException as ttt:
            print("Collimeter scan failed")
            print(ttt.args[0])
=======
        except MyException, ttt:
            print "Collimeter scan failed"
            print ttt.args[0]
>>>>>>> zoo45xu/main
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
<<<<<<< HEAD
        except MyException as ttt:
            print("Collimeter scan failed")
            print(ttt.args[0])
=======
        except MyException, ttt:
            print "Collimeter scan failed"
            print ttt.args[0]
>>>>>>> zoo45xu/main
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

<<<<<<< HEAD
        print(save_y, save_z)
=======
        print save_y, save_z
>>>>>>> zoo45xu/main

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
<<<<<<< HEAD
    import configparser
    # read IP address for BSS connection from beamline.config 
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    print(config_path)
    config.read(config_path)
    host = config.get("server", "blanc_address")
=======
    host = '172.24.242.59'
>>>>>>> zoo45xu/main
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    coli = Colli(s)
<<<<<<< HEAD
    coli.getEvacuate()

    coli.on()
    coli.off()
    # coli.off()
=======

    coli.getY()
    coli.getZ()
    
    #coli.compareOnOff(1)
    coli.on()
    #coli.off()

    #coli.getY()
    #coli.getZ()
    # coli.scan("colllli",0)

    # print coli.getY()
    # coli.moveZ(1000)
    # coli.moveZ(0)
    # coli.scan2D()
    # coli.scanCore("test",3)
    # coli.on()
    #coli.off()
>>>>>>> zoo45xu/main
    # def scan2D(self,prefix,startz,endz,stepz,starty,endy,stepy):
    # coli.goOff()
    s.close()
