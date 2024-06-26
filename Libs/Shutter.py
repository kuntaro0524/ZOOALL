#!/bin/env python 
import sys,os
import socket
import time
import datetime

from configparser import ConfigParser, ExtendedInterpolation
import BSSconfig

# from Count import *
# My library

class Shutter:
    def __init__(self, server):
        self.s = server

        # configure file "beamline.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])
        # axis name of shutter on VME
        axisname = self.config.get("axes", "shutter")

        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        # axis name of 'counter' on VME
        self.ax_name = f"bl_{self.bl_object}_{axisname}"
        self.beamline = self.config.get("beamline", "beamline")

        # The 2nd shutter at BL44XU
        if self.beamline =="BL44XU":
            # The 1st shutter for every beamline
            shutter1_axname = "%s_1" % self.ax_name
            self.openmsg1 = "put/%s/on" % shutter1_axname
            self.clsmsg1 = "put/%s/off" % shutter1_axname
            self.qmsg1 = "get/%s/status" % shutter1_axname

            shutter2_axname = "%s_2" % self.ax_name
            self.openmsg2 = "put/%s/on" % shutter2_axname
            self.clsmsg2 = "put/%s/off" % shutter2_axname
            self.qmsg2 = "get/%s/status" % shutter2_axname
        
        elif self.beamline == "BL32XU":
            self.openmsg1 = "put/%s/on" % self.ax_name
            self.clsmsg1 = "put/%s/off" % self.ax_name
            self.qmsg = "get/%s/status" % self.ax_name  

    # String/Bytes communication via a socket
    def communicate(self, comstr):
        sending_command = comstr.encode()
        self.s.sendall(sending_command)
        recstr = self.s.recv(8000)
        return repr(recstr)

    def open(self):
        recbuf1=self.communicate(self.openmsg1)
        # print(recbuf1)
        if self.beamline == "BL44XU":
            recbuf2=self.communicate(self.openmsg2)

    def close(self):
        recbuf1=self.communicate(self.clsmsg1)
        if self.beamline == "BL44XU":
            recbuf2=self.communicate(self.clsmsg2)
        else:
            recbuf2 = self.communicate(self.clsmsg1)

    # self.query()
    def query(self):
        # self.s.sendall(self.qmsg)
        recbuf=self.communicate(self.qmsg)

    def isOpen(self):
        strstr = self.query()
        cutf = strstr[:strstr.rfind("/")]
        final = cutf[cutf.rfind("/") + 1:]
        if final == "off":
            return 0
        else:
            return 1


if __name__ == "__main__":
    # host = '192.168.163.1'
    host = '172.24.242.57'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # pin_ch=int(raw_input())

    shutter = Shutter(s)
    # print shutter.isOpen()
    shutter.close()
    shutter.open()
    time.sleep(5.0)
    shutter.close()
    # print shutter.isOpen()
    # time.sleep(10.0)
    # shutter.open()
    # shutter.close()
    s.close()
