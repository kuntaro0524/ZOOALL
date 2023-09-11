#!/bin/env python 
import sys
import socket
import time

# My library
from Motor import *
import BSSconfig
from configparser import ConfigParser, ExtendedInterpolation

class Cryo:
    def __init__(self, server):
        self.s = server

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
        self.v2p_z, self.sense_z = self.bssconfig.getPulseInfo(self.axis_name)
        print(self.sense_z)

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

    def getPosition(self):
        value = self.cryoz.getPosition()[0]
        return value

    def on(self):
        if self.isInit == False:
            self.getEvacuate()
        self.cryoz.move(self.on_pulse)

    def off(self):
        if self.isInit == False:
            self.getEvacuate()
        self.cryoz.move(self.off_pulse)

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
            print(index)

    def moveTo(self, pls):
        self.cryoz.move(pls)

    def isMoved(self):
        isZ = self.cryoz.isMoved()

        if isZ == 0:
            return True
        if isZ == 1:
            return False


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # bm=BM(s)
    # bm.on()
    # bm.off()

    cry = Cryo(s)
    print(cry.getEvacuate())
    pos = cry.getPosition()
    print(pos)
    cry.on()
    cry.off()

    s.close()
