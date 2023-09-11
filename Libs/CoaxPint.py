#!/bin/env python 
import sys
import socket
import time
import datetime

# My library
from Received import *
from Motor import *


#
class CoaxPint:
    def __init__(self, server):
        self.s = server
        self.coaxx = Motor(self.s, "bl_32in_st2_coax_1_x", "pulse")
        self.sense = -1

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
