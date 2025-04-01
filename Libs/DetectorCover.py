#!/bin/env python 
import sys
import socket
import time
import datetime

# My library
from Received import *
from Motor import *
from BSSconfig import *
import BaseAxis

class DetectorCover(BaseAxis.BaseAxis):
    def __init__(self, server):
        super.__init__(server, "det_cover", axis_type="pulse", isEvacuate=False)
        self.cov_z = self.motor

        self.isInit = False

    def isCover(self):
        pos = self.getPos()
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

if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    covz = Cover(s)
    # covz.move(-245000)
    # covz.on()
    covz.off()

    s.close()
