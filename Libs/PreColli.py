# -*- coding: utf-8 -*-
#!/bin/env python 
import os
import sys
import socket
import time
import datetime

# My library
from Received import *
from Motor import *
import BSSconfig
from ZooMyException import *
from configparser import ConfigParser, ExtendedInterpolation

# BL44XU specific beam defining aperture before the 2nd collimator
class PreColli:
    def __init__(self, server):
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        # beamline.ini 
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])

        self.s = server
        # names of collimator axes
        self.pcoly_axis = ""
        self.pcolz_axis = ""
        # coly > section: axes, option: col_y_name
        try:
            self.pcoly_axis = self.config.get("axes", "precol_y_name")
        except:
            # display 'warning' if the option is not found
            print("WARNING: precol_y_name is not found in beamline.ini")

        try:
            # colz > section: axes, option: col_z_name
            self.pcolz_axis = self.config.get("axes", "precol_z_name")
        except:
            # display 'warning' if the option is not found
            print("WARNING: precol_z_name is not found in beamline.ini")

        # if 'coly' exists in the configuration file.
        if self.pcoly_axis != "":
            self.pcoly = Motor(self.s, "bl_%s_%s" %(self.bl_object, self.pcoly_axis), "pulse")
            # pulse information of each axis
            self.v2p_y, self.sense_y, self.home_y = self.bssconf.getPulseInfo(self.pcoly_axis)
        if self.pcolz_axis != "":
            self.pcolz = Motor(self.s, "bl_%s_%s" %(self.bl_object, self.pcolz_axis), "pulse")
            print("Searching %s" % self.pcolz_axis)
            # print("bl_%s_%s" %(self.bl_object, self.colz_axis))
            # pulse information of each axis
            self.v2p_z, self.sense_z, self.home_z = self.bssconf.getPulseInfo(self.pcolz_axis)

        # These two axes are moved just before centering crystals. 
        self.isInit = True

    # 退避する軸はビームラインごとに違っているのでそれを取得する必要がある。
    # 現時点では１軸しか取得できないのでそうでないビームライン（ビームストッパーをYZどちらも退避）が出てくると修正する必要がある
    def getEvacuate(self):
        evacinfo = self.config.get("axes", "col_evacinfo")
        self.evac_axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateInfo(evacinfo)
        print("Evac axis:",self.evac_axis_name)
        print("ON (VME value):",self.on_pulse)
        print("OFF(VME value):",self.off_pulse)
        # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
        print("BLO=bl_%s_%s" % (self.bl_object, self.evac_axis_name))
        self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
        self.isInit = True

    def setEvacuate(self):
        self.evac_y = self.config.getint("capture", "precol_y_off")
        self.evac_z = self.config.getint("capture", "precol_z_off")
        self.pcoly.move(self.evac_y)
        self.pcolz.move(self.evac_z)

    def getY(self):
        tmp = int(self.pcoly.getPosition()[0])
        return tmp

    def getZ(self):
        tmp = int(self.pcolz.getPosition()[0])
        return tmp

    def getEvacZ(self):
        tmp = self.evac_axis.getPosition()[0]
        return tmp

    def on(self):
        if self.isInit == False:
            self.getEvacuate()
        # sense 
        # pulse_to_move = self.on_pulse * self.sense_z
        # print(pulse_to_move)
        self.evac_axis.move(self.on_pulse)

    def off(self):
        if self.isInit == False:
            self.getEvacuate()
        self.evac_axis.move(self.off_pulse)

    # 2023/04/12 Temp mod.
    def offY(self):
        self.pcoly.move(self.evac_y_axis_off)

    def onY(self):
        self.pcoly.move(self.evac_y_axis_on)

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

    def moveY(self, pls):
        v = pls
        self.pcoly.move(v)

    def moveZ(self, pls):
        v = pls
        self.pcolz.move(v)

    def isMoved(self):
        isY = self.coly.isMoved()
        isZ = self.colz.isMoved()

        if isY == 0 and isZ == 0:
            return True
        if isY == 1 and isZ == 1:
            return False


if __name__ == "__main__":
    import configparser
    # read IP address for BSS connection from beamline.config 
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(config_path)
    # host = config.get("server", "bss_server")
    host = config.get("server", "blanc_address")
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    coli = PreColli(s)
    coli.getEvacuate()
    print((coli.getY()))
    print((coli.getZ()))

    coli.setEvacuate()
    s.close()
