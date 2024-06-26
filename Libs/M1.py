#!/bin/env python 
import sys
import socket
import time
import math
from decimal import *
from MyException import *

# My library
from Received import *
from Motor import *
from AnalyzePeak import *
from File import *

class M1:
    def __init__(self, server):
        self.s = server
        self.m1_tx = Motor(self.s, "bl_45in_tc1_mh_1_tx", "mrad")
        self.m1_ty = Motor(self.s, "bl_45in_tc1_mh_1_ty", "mrad")
        self.m1_y = Motor(self.s, "bl_45in_tc1_mh_1_y", "mm")
        self.m1_x = Motor(self.s, "bl_45in_tc1_mh_1_x", "mm")

        # Counter channel
        self.count_channel = 1

        # File
        self.f = File("./")

    def getTx(self):
        return float(self.m1_tx.getAngle()[0])

    def getTy(self):
        return float(self.m1_ty.getAngle()[0])

    def getY(self):
        return int(self.m1_y.getPosition()[0])

    def getX(self):
        return int(self.m1_x.getPosition()[0])

    def setTx(self, val_mrad):
        self.m1_tx.move(val_mrad)

    def setTy(self, val_mrad):
        self.m1_ty.move(val_mrad)

    def setX(self, val_mm):
        self.m1_x.move(val_mm)

    def setY(self, val_mm):
        self.m1_y.move(val_mm)

# self.hfm_y.move(pulse)

if __name__ == "__main__":
    host = '172.24.242.59'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    mirror = M1(s)
    print mirror.getTx()
    print mirror.getTy()
    print mirror.getX()
    print mirror.getY()
    #mirror.setTx(0.0)
    for ty in [-3.7,-3.6,-3.5,-3.4,-3.3]:
        mirror.setTy(ty)
    #mirror.setX(-0.416)
    #mirror.setY(0.0)

    s.close()
