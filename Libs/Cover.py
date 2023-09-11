#!/bin/env python 
import sys
import socket
import time
import datetime

# My library
from Received import *
from Motor import *
from BSSconfig import *


#
class Cover:
    def __init__(self, server):
        self.s = server
        self.cov_z = Motor(self.s, "bl_32in_st2_cover_1_z", "pulse")

        #		self.off_pos=245000 # pulse
        self.off_pos = 210000  # pulse
        self.on_pos = 0  # pulse

        self.isInit = False

    def isCover(self):
        pos = self.getPos()
        print(pos)
        if pos == 0:
            return True
        else:
            return False

    def getPos(self):
        return self.cov_z.getPosition()[0]

    def move(self, pls):
        self.cov_z.move(pls)

    def on(self):
        self.cov_z.move(self.on_pos)

    def off(self):
        self.cov_z.move(self.off_pos)

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

    covz = Cover(s)
    # covz.move(-245000)
    # covz.on()
    # covz.off()
    print(covz.getPos())

    s.close()
