#!/bin/env python 
import sys
import socket
import time
import datetime
import os

# My library
from Received import *
from Motor import *
from configparser import ConfigParser, ExtendedInterpolation
import BSSconfig

class CCDlen:
    def __init__(self, server):
        self.s = server

        # beamline.ini file
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])

        # axis definition is read from 'beamline.ini' file
        # section: axes, option: ccdlen
        self.ccdlen_name = self.config.get('axes', 'ccdlen')

        # BSSconfig file
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()
        self.ccdlen = Motor(self.s, f"bl_{self.bl_object}_{self.ccdlen_name}", "pulse")

        # Pulse, home and limit parameters
        self.ccdlen_v2p, self.ccdlen_sense,self.ccdlen_home = self.bssconf.getPulseInfo(self.ccdlen_name)
        self.low_limit, self.upper_limit = self.bssconf.getLimit(self.ccdlen_name)

        self.isInit = False

    def getPos(self):
        return self.ccdlen.getPosition()[0]

    def getLen(self):
        pls = self.ccdlen_sense*float(self.getPos())
        len = pls / self.ccdlen_v2p + self.ccdlen_home
        return len

    def moveCL(self, len):
        if len > self.upper_limit or len < self.low_limit:
            print("Do nothing because CL should be in 110-600mm")
            return False
        tmp = len - self.ccdlen_home
        pls = int(tmp * self.ccdlen_v2p) * self.ccdlen_sense
        self.move(pls)
        print("Current Camera distance %8.2fmm" % self.getLen())

    def move(self, pls):
        self.ccdlen.move(pls)

    def evac(self):
        self.moveCL(300.0)

    def isMoved(self):
        isY = self.coly.isMoved()
        isZ = self.colz.isMoved()

        if isY == 0 and isZ == 0:
            return True
        if isY == 1 and isZ == 1:
            return False


if __name__ == "__main__":
    import BLFactory

    blf = BLFactory.BLFactory()
    blf.initDevice()

    # read configure file(beamline.init)
    config = ConfigParser(interpolation=ExtendedInterpolation())
    ini_file = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(ini_file)
    zooroot = config.get('dirs', 'zooroot')

    dev = blf.device
    dev.init()
    # clen.moveCL(400.0)
    dev.clen.moveCL(800.0)
    # clen.evac()

    s.close()
