#!/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket
import time

# My library
from Received import *
from Motor import *
from MyException import *
import BSSconfig
from Count import *

class BS:
    def __init__(self, server):
        self.bssconf = BSSconfig.BSSconfig('/isilon/blconfig/bl41xu/bss/bss.config')
        self.s = server
        self.bs_y = Motor(self.s, "bl_41in_st2_bs_1_y", "pulse")
        self.bs_z = Motor(self.s, "bl_41in_st2_bs_1_z", "pulse")
        self.bl_object = self.bssconf.getBLobject()
        self.sense_y = -1
        self.sense_z = 1

        self.isInit = False
        self.v2p = 1000

        # Default value
        self.off_pos = -24990  # pulse
        self.on_pos = 42625  # pulse
        self.evac_large_holder = -10000

    # 退避する軸はビームラインごとに違っているのでそれを取得する必要がある。
    # 現時点では１軸しか取得できないのでそうでないビームライン（ビームストッパーをYZどちらも退避）が出てくると修正する必要がある
    def getEvacuate(self):
        self.evac_axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateInfo("beam stop")
        print("ON (VME value):",self.on_pulse)
        print("OFF(VME value):",self.off_pulse)
        # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
        self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
        self.isInit = True

    def getZ(self):
        return self.sense_z * int(self.bs_z.getPosition()[0])

    def getY(self):
        return int(self.bs_y.getPosition()[0])

    def moveY(self, pls):
        v = pls * self.sense_y
        self.bs_y.move(v)

    def moveZ(self, pls):
        v = pls * self.sense_z
        self.bs_z.move(v)

    def scan2D(self, prefix, startz, endz, stepz, starty, endy, stepy):
        counter = Count(self.s, 1, 0)
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
        self.bs_y.nageppa(pvalue)

    def evacLargeHolder(self):
        self.bs_y.nageppa(self.evac_large_holder)

    def evacLargeHolderWait(self):
        self.bs_y.move(self.evac_large_holder)

    def on(self):
        if self.isInit == False:
            self.getEvacuate()
        self.evac_axis.move(self.on_pulse)

    def off(self):
        if self.isInit == False:
            self.getEvacuate()
        self.evac_axis.move(self.off_pulse)

    def isMoved(self):
        isY = self.bs_y.isMoved()
        isZ = self.bs_z.isMoved()

        if isY == 0 and isZ == 0:
            return True
        if isY == 1 and isZ == 1:
            return False


if __name__ == "__main__":
    host = '172.24.242.54'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # print "Moving BS"
    # print "type on/off:"
    # option=raw_input()
    bs = BS(s)

    bs.getEvacuate()
    print("#########################################")
    bs.on()
    print bs.getY()
    print("#########################################")
    bs.off()
    print bs.getY()
    #print bs.getZ()
    #print bs.getY()

    #def scan2D(self, prefix, startz, endz, stepz, starty, endy, stepy):
    #bs.scan2D("bs_scan",-2000,2000,200,-500,500,50)

    # bs.on()
    # bs.evacLargeHolder()

    # print z,y
    # bs.go(-30000)

    # bs.getEvacuate()
    # if option=="on":
    # bs.on()
    # elif option=="off":
    #bs.off()
    #bs.on()
    #bs.off()
    #bs.goOn()
    #bs.goOff()
    s.close()
