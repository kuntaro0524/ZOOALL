#!/bin/env python 
import sys
import socket
<<<<<<< HEAD
import os
=======
>>>>>>> zoo45xu/main
import time

# My library
from Motor import *
<<<<<<< HEAD
import BSSconfig
from configparser import ConfigParser, ExtendedInterpolation
=======
from BSSconfig import *
>>>>>>> zoo45xu/main

class Cryo:
    def __init__(self, server):
        self.s = server
<<<<<<< HEAD

        # Read bemaline.ini 
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])
        # Cryo Z axis name is extracted from 'beamline.ini'
        # section: axes, option: cryo_z_name
        self.axis_name = self.config.get("axes", "cryo_z_name")

        self.bssconfig = BSSconfig.BSSconfig()
        self.bl_object = self.bssconfig.getBLobject()
        self.cryoz = Motor(self.s, f"bl_{self.bl_object}_{self.axis_name}", "pulse")

        self.isInit = False

        # pulse information of each axis
        self.v2p_z, self.sense_z, self.home_z= self.bssconfig.getPulseInfo(self.axis_name)

    # 退避する軸はビームラインごとに違っているのでそれを取得する必要がある。
    # 現時点では１軸しか取得できないのでそうでないビームライン（ビームストッパーをYZどちらも退避）が出てくると修正する必要がある
    def getEvacuate(self):
        evac_info = self.config.get("axes", "cryo_evacinfo")
        self.evac_axis_name, self.on_pulse, self.off_pulse = self.bssconfig.getEvacuateInfo(evac_info)
        print("ON (VME value):",self.on_pulse)
        print("OFF(VME value):",self.off_pulse)
        # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
        self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
        self.isInit = True
=======
        self.cryoz = Motor(self.s, "bl_45in_st2_cryo_1_x", "pulse")

        self.v2p = 500
        self.isInit = False
        self.sense = -1

        self.off_mon = 7500 # pulse
        self.off_pos = 2500  # pulse 
        self.on_pos = 0  # pulse 
>>>>>>> zoo45xu/main

    def getPosition(self):
        value = self.cryoz.getPosition()[0]
        return value

<<<<<<< HEAD
    def on(self):
        if self.isInit == False:
            self.getEvacuate()
        self.cryoz.move(self.on_pulse)
=======
    def getEvacuate(self):
        bssconf = BSSconfig()

        try:
            tmpon, tmpoff = bssconf.getCryo()
        except MyException, ttt:
            print ttt.args[0]

        self.on_pos = float(tmpon) * self.v2p
        self.off_pos = float(tmpoff) * self.v2p

        self.isInit = True
        print self.on_pos, self.off_pos

    def on(self):
        if self.isInit == False:
            self.getEvacuate()
        move_pulse = self.on_pos * self.sense
        self.cryoz.move(move_pulse)
>>>>>>> zoo45xu/main

    def off(self):
        if self.isInit == False:
            self.getEvacuate()
<<<<<<< HEAD
        self.cryoz.move(self.off_pulse)
=======
        move_pulse = self.off_pos * self.sense
        print move_pulse
        self.cryoz.move(move_pulse)

    def off4mon(self):
        move_pulse = self.off_mon * self.sense
        self.cryoz.move(move_pulse)
>>>>>>> zoo45xu/main

    def offFull(self):
        self.cryoz.nageppa(2000)

    def go(self, pvalue):
        self.cryoz.nageppa(pvalue)

    def goOn(self):
        if self.isInit == False:
            self.getEvacuate()
        self.cryoz.nageppa(self.on_pos)

    def goOff(self):
        if self.isInit == False:
            self.getEvacuate()
        self.cryoz.nageppa(self.off_pos)

    def safetyEvacuate(self):
        if self.isInit == False:
            self.getEvacuate()
        self.go_and_check(self.off_pos)

    def go_and_check(self, pvalue):
        index = 0
        while (1):
            self.cryoz.move(pvalue)
            value = self.cryoz.getPosition()[0]
            if value == pvalue:
                break
            index += 1
<<<<<<< HEAD
            print(index)
=======
            print index
>>>>>>> zoo45xu/main

    def moveTo(self, pls):
        self.cryoz.move(pls)

    def isMoved(self):
        isZ = self.cryoz.isMoved()

        if isZ == 0:
            return True
        if isZ == 1:
            return False


if __name__ == "__main__":
<<<<<<< HEAD
    host = '172.24.242.41'
=======
    host = '172.24.242.59'
>>>>>>> zoo45xu/main
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # bm=BM(s)
    # bm.on()
    # bm.off()

    cry = Cryo(s)
<<<<<<< HEAD
    print(cry.getEvacuate())
    pos = cry.getPosition()
    print(pos)
    cry.on()
    cry.off()
=======
    print cry.getPosition()
    #cry.on()
    cry.off()
    #print cry.getPosition()
    #cry.off4mon()
    #print cry.getPosition()
    #print cry.getEvacuate()
    # cry.go_and_check(0)
    # time.sleep(3)
    # cry.go_and_check(980)
    #cry.on()
    # coli.off()
>>>>>>> zoo45xu/main

    s.close()
