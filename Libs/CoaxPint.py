#!/bin/env python 
import sys,os
import socket
import time
import datetime

# My library
from Received import *
from Motor import *
from configparser import ConfigParser, ExtendedInterpolation
import BSSconfig

class CoaxPint:
    def __init__(self, server):
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        self.s = server
        # beamline.ini 
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH']) 

        # axis name of CoaxPint
        self.coax_name = self.config.get("axes", "coax_x_axis")
        axis_name = "bl_%s_%s" % (self.bl_object, self.coax_name)
        self.coaxx = Motor(self.s, axis_name, "pulse")

        # get pulse information from bss.config
        self.v2p, self.sense, self.home = self.bssconf.getPulseInfo(self.coax_name)

    def move(self, pls):
        value = self.sense * int(pls)
        self.coaxx.move(value)

    def relmove(self, pls):
        value = int(self.sense * pls)
        self.coaxx.relmove(pls)

    def getPosition(self):
        curr_value = self.sense * self.coaxx.getPosition()[0]
        return curr_value

    def readCameraInf(self):
        print("read camera inf")

if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    coa = CoaxPint(s)
    print(coa.getPosition())
    # coa.relmove(10)
    #coa.move(22819)
    #print coa.getPosition()

    s.close()
