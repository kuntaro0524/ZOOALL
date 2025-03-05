#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *


class DSS:
    def __init__(self, server):
        self.s = server

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

<<<<<<< HEAD
    # String to bytes
    def communicate(self, comstr):
        sending_command = comstr.encode()
        print(type(sending_command))
        self.s.sendall(sending_command)
        recstr = self.s.recv(8000)
        return repr(recstr)

    def getStatus(self):
        com = "get/bl_32in_plc_dss_1/status"
        # counter clear
        recbuf = self.communicate(com)
=======
    def getStatus(self):
        com = "get/bl_45in_plc_dss_1/status"
        # counter clear
        self.s.sendall(com)
        recbuf = self.s.recv(8000)
>>>>>>> zoo45xu/main
        # print recbuf
        status = self.anaRes(recbuf)
        # return value: lock/moving/open/close
        return status

    def open(self):
<<<<<<< HEAD
        com = "put/bl_32in_plc_dss_1/open"
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
        com = "put/bl_32in_plc_dss_1/close"
=======
        com = "put/bl_45in_plc_dss_1/open"
        # counter clear
        self.s.sendall(com)
        recbuf = self.s.recv(8000)
        # 30 sec trials
        for i in range(0, 10):
            if self.getStatus() == "open":
                print "OPEN Okay"
                return True
            time.sleep(3.0)
        print "Remote control is okay?"
        return False

    def close(self):
        com = "put/bl_45in_plc_dss_1/close"
>>>>>>> zoo45xu/main
        # counter clear
        self.s.sendall(com)
        recbuf = self.s.recv(8000)

        # 30 sec trials
        for i in range(0, 10):
            if self.getStatus() == 0:
<<<<<<< HEAD
                print("CLOSE Okay")
                return True
            time.sleep(3.0)
        print("Remote control is okay?")
=======
                print "CLOSE Okay"
                return True
            time.sleep(3.0)
        print "Remote control is okay?"
>>>>>>> zoo45xu/main
        return False

    # wait_interval [sec]
    def openTillOpen(self, wait_interval=300, ntrial=150):
        for i in range(0, ntrial):
            if self.isLocked() == True:
                tstr = datetime.datetime.now()
<<<<<<< HEAD
                print("DSS %s: waiting for 'unlocked'" % tstr)
=======
                print "DSS %s: waiting for 'unlocked'" % tstr
>>>>>>> zoo45xu/main
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
<<<<<<< HEAD
    # host = '192.168.163.1'
    host = '172.24.242.41'
=======
    host = '172.24.242.59'
>>>>>>> zoo45xu/main
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    dss = DSS(s)
<<<<<<< HEAD
    # print dss.getStatus()
    # dss.isLocked()
    dss.openTillOpen(wait_interval=5, ntrial=10)
=======
    print dss.getStatus()
    dss.isLocked()
    #dss.openTillOpen(wait_interval=5, ntrial=10)
>>>>>>> zoo45xu/main
    # time.sleep(10)
    # print dss.close()
    # time.sleep(15)
    # dss.getStatus()
    # dss.open()
    # time.sleep(15)
    # dss.getStatus()

    s.close()
