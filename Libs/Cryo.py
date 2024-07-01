#!/bin/env python 
import sys
import socket
import time

# My library
from Motor import *
from BSSconfig import *

class Cryo:
    def __init__(self, server):
        self.s = server
        self.cryoz = Motor(self.s, "bl_45in_st2_cryo_1_x", "pulse")

        self.v2p = 500
        self.isInit = False
        self.sense = -1

        self.off_mon = 7500 # pulse
        self.off_pos = 2500  # pulse 
        self.on_pos = 0  # pulse 

    def getPosition(self):
        value = self.cryoz.getPosition()[0]
        return value

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

    def off(self):
        if self.isInit == False:
            self.getEvacuate()
        move_pulse = self.off_pos * self.sense
        print move_pulse
        self.cryoz.move(move_pulse)

    def off4mon(self):
        move_pulse = self.off_mon * self.sense
        self.cryoz.move(move_pulse)

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
            print index

    def moveTo(self, pls):
        self.cryoz.move(pls)

    def isMoved(self):
        isZ = self.cryoz.isMoved()

        if isZ == 0:
            return True
        if isZ == 1:
            return False


if __name__ == "__main__":
    host = '172.24.242.59'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # bm=BM(s)
    # bm.on()
    # bm.off()

    cry = Cryo(s)
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

    s.close()
