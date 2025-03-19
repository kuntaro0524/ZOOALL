#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *
import BaseAxis

class DSS(BaseAxis.BaseAxis):
    def __init__(self, server):
        # axis name for DSS
        axis_config = "dss"
        BaseAxis.__init__(self, server, axis_config, axis_type="plc")

    def anaRes(self, recbuf):
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

    # String to bytes
    def communicate(self, comstr):
        sending_command = comstr.encode()
        print(type(sending_command))
        self.s.sendall(sending_command)
        recstr = self.s.recv(8000)
        return repr(recstr)

    def getStatus(self):
        com = "get/{self.full_axis_name}/status"
        # counter clear
        recbuf = self.communicate(com)
        # print recbuf
        status = self.anaRes(recbuf)
        # return value: lock/moving/open/close
        return status

    def open(self):
        com = "put/{self.full_axis_name}/open"
        # counter clear
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
        self.s.sendall(com)
        recbuf = self.s.recv(8000)

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
                print("DSS %s: waiting for 'unlocked'" % tstr)
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

    dss = DSS(s)
    # print dss.getStatus()
    # dss.isLocked()
    dss.openTillOpen(wait_interval=5, ntrial=10)
    # time.sleep(10)
    # print dss.close()
    # time.sleep(15)
    # dss.getStatus()
    # dss.open()
    # time.sleep(15)
    # dss.getStatus()

    s.close()
