#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *
from MyException import *
from Count import *
import BSSconfig
from configparser import ConfigParser, ExtendedInterpolation

class BS:
    def __init__(self, server):
        self.s = server
        
        # Beamline object
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        # configure file "beamline.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path="%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.config.read(config_path)

        # beam stopper axis definition
        # beam stopper axis name > section: axes, option: bs_y_name
        self.bs_y_name = self.config.get("axes", "bs_y_name")
        # beam stopper axis name > section: axes, option: bs_z_name
        self.bs_z_name = self.config.get("axes", "bs_z_name")

        print(self.bs_y_name)
        
        self.bs_y = Motor(self.s, f"bl_{self.bl_object}_{self.bs_y_name}", "pulse")
        self.bs_z = Motor(self.s, f"bl_{self.bl_object}_{self.bs_z_name}", "pulse")

        # Read configure file and get parameters
        self.bs_y_v2p, self.bs_y_sense = self.bssconf.getPulseInfo(self.bs_y_name)
        self.bs_z_v2p, self.bs_z_sense = self.bssconf.getPulseInfo(self.bs_z_name)

        self.isInit = False

    # 退避する軸はビームラインごとに違っているのでそれを取得する必要がある。
    # 現時点では１軸しか取得できないのでそうでないビームライン（ビームストッパーをYZどちらも退避）が出てくると修正する必要がある
    def getEvacuate(self):
        evacinfo = self.config.get("axes", "bs_evacinfo")
        self.evac_axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateInfo(evacinfo)
        print("ON (VME value):",self.on_pulse)
        print("OFF(VME value):",self.off_pulse)
        # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
        self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
        self.isInit = True

    def getZ(self):
        return self.bs_z_sense * int(self.bs_z.getPosition()[0])

    def getY(self):
        return self.bs_y_sense * int(self.bs_y.getPosition()[0])

    def moveY(self, pls):
        v = pls * self.bs_y_sense
        self.bs_y.move(v)

    def moveZ(self, pls):
        v = pls * self.bs_z_sense
        self.bs_z.move(v)

    def scan2D(self, prefix, startz, endz, stepz, starty, endy, stepy):
        counter = Count(self.s, 3, 0)
        oname = "%s_bs_2d.scn" % prefix
        of = open(oname, "w")

        for z in arange(startz, endz, stepz):
            self.moveZ(z)
            for y in range(starty, endy, stepy):
                self.moveY(y)
                cnt = int(counter.getCount(0.2)[0])
                of.write("%5d %5d %12d\n" % (y, z, cnt))
                of.flush()
            of.write("\n")
        of.close()

    def go(self, pvalue):
        self.bs_z.nageppa(pvalue)

    def evacLargeHolder(self):
        self.bs_z.nageppa(self.evac_large_holder)

    def evacLargeHolderWait(self):
        self.bs_z.move(self.evac_large_holder)

    def on(self):
        if self.isInit == False:
            self.getEvacuate()
        self.bs_z.move(self.on_pulse)

    def off(self):
        if self.isInit == False:
            self.getEvacuate()
        self.bs_z.move(self.off_pulse)

    def goOn(self):
        if self.isInit == False:
            self.getEvacuate()
        self.go(self.on_pos)

    def goOff(self):
        if self.isInit == False:
            self.getEvacuate()
        self.go(self.off_pos)

    def isMoved(self):
        isY = self.bs_y.isMoved()
        isZ = self.bs_z.isMoved()

        if isY == 0 and isZ == 0:
            return True
        if isY == 1 and isZ == 1:
            return False


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # print "Moving BS"
    # print "type on/off:"
    # option=raw_input()
    bs = BS(s)

    print(bs.getZ())
    bs.getEvacuate()
    bs.on()
    bs.off()
    bs.on()
    s.close()
