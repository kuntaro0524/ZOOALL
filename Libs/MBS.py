#!/bin/env python 
import os
import sys
import socket
import time

# My library
from Received import *
from Motor import *

import BaseAxis
from configparser import ConfigParser, ExtendedInterpolation

class MBS(BaseAxis.BaseAxis):
    def __init__(self, server):
        self.s = server
        # axis name for MBS
        # read beamline.ini
        self.config= ConfigParser(interpolation=ExtendedInterpolation())
        config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.config.read(config_path)
        bl_object = self.config.get("beamline", "bl_object")
        mbs_str = self.config.get("axes", "mbs")
        # axis name
        self.axis_name = f"bl_{bl_object}_{mbs_str}"
        #super().__init__(server, axis_config, axis_type="plc")
        self.full_axis_name = f"bl_{bl_object}_{mbs_str}"

    def anaRes(self, recbuf):
        #	bl_32in_plc_mbs/get/1128_blrs_root_blanc4deb/open/0
        cols = recbuf.split("/")
        ncol = len(cols)
        status = cols[ncol - 2]
        return status

    def isLocked(self):
        status = self.getStatus()
        if status == "locked":
            return True
        else:
            return False

    # # String to bytes
    # def communicate(self, comstr):
    #     sending_command = comstr.encode()
    #     print(type(sending_command))
    #     self.s.sendall(sending_command)
    #     recstr = self.s.recv(8000)
    #     return repr(recstr)

    def getStatus(self):
        com = f"get/{self.full_axis_name}/status"
        print("Result: MBS getStatus: %s" % com)
        # counter clear
        recbuf = self.communicate(com)
        status = self.anaRes(recbuf)
        # return value: lock/moving/open/close
        return status

    def open(self):
        com = "put/{self.full_axis_name}/open"
        recbuf = self.communicate(com)
        # 30 sec trials
        for i in range(0, 10):
            if self.getStatus() == "open":
                print("OPEN Okay")
                return True
            time.sleep(3.0)
        print("Remote control is okay?")
        return False

    def close(self):
        com = "put/{self.full_axis_name}/close"
        # counter clear
        recbuf = self.communicate(com)

        # 30 sec trials
        for i in range(0, 10):
            if self.getStatus() == 0:
                print("CLOSE Okay")
                return True
            time.sleep(3.0)
        print("Remote control is okay?")
        return False

    # wait_interval [sec]
    def openTillOpen(self, wait_interval=300, ntrial=150):
        for i in range(0, ntrial):
            if self.isLocked() == True:
                tstr = datetime.datetime.now()
                print("MBS %s: waiting for 'unlocked'" % tstr)
                time.sleep(wait_interval)
            else:
                self.open()
                break

        for i in range(0, 50):
            if self.getStatus() == "open":
                return True
            else:
                time.sleep(5)
        return False

if __name__ == "__main__":
    # host = '192.168.163.1'
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    mbs = MBS(s)
    print(mbs.getStatus())
    print(mbs.isLocked())
    # mbs.openTillOpen(wait_interval=10,ntrial=30)
    # time.sleep(10)
    #mbs.close()
    # time.sleep(15)
    # mbs.getStatus()
    # mbs.open()
    # time.sleep(15)
    # mbs.getStatus()

    s.close()
