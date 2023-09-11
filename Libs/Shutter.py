#!/bin/env python 
import sys
import socket
import time
import datetime


# from Count import *

# My library

class Shutter:
    def __init__(self, server):
        self.s = server
        self.openmsg = "put/bl_32in_st2_shutter_1/on"
        self.clsmsg = "put/bl_32in_st2_shutter_1/off"
        self.qmsg = "get/bl_32in_st2_shutter_1/status"

    # String/Bytes communication via a socket
    def communicate(self, comstr):
        sending_command = comstr.encode()
        self.s.sendall(sending_command)
        recstr = self.s.recv(8000)
        return repr(recstr)

    def open(self):
        recbuf=self.communicate(self.openmsg)

    def close(self):
        # self.s.sendall(self.clsmsg)
        recbuf=self.communicate(self.clsmsg)

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
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # pin_ch=int(raw_input())

    shutter = Shutter(s)
    # print shutter.isOpen()
    # shutter.open()
    # print shutter.isOpen()
    # time.sleep(10.0)
    # shutter.open()
    shutter.close()
    # time.sleep(10.0)
    s.close()
