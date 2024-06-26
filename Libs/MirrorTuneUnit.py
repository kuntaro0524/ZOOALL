50  # !/bin/env python
import sys
import socket
import time
import os

# My library
from Motor import *


class MirrorTuneUnit:
    def __init__(self, server):
        self.s = server
        # Motorized axes
        self.stage_y = Motor(self.s, "bl_45in_st2_motor_2_1", "pulse")
        self.stage_z = Motor(self.s, "bl_45in_st2_motor_2_2", "pulse")

        # Initial settings
        self.pin_to_bm_y = -300
        self.pin_to_bm_z = 34500
        self.y = 0
        self.z = 0

        self.hori_reflect = 1000
        self.vert_reflect = -5000

    def setPulse(self, option):
        # set up parameters
        if option == "dire_pin":
            self.y = 0
            self.z = 0
            return self.y,self.z

        elif option == "hfm_pin":
            self.y = self.hori_reflect
            self.z = 0
            return self.y,self.z

        elif option == "vfm_pin":
            self.y = 0
            self.z = self.vert_reflect
            return self.y,self.z

        elif option == "both_pin":
            self.y = self.hori_reflect
            self.z = self.vert_reflect
            return self.y,self.z

        elif option == "dire_bm":
            self.y = 0 + self.pin_to_bm_y
            self.z = 0 + self.pin_to_bm_z
            return self.y,self.z

        elif option == "hfm_bm":
            self.y = self.hori_reflect + self.pin_to_bm_y
            self.z = 0 + self.pin_to_bm_z
            return self.y,self.z

        elif option == "vfm_bm":
            self.y = 0 + self.pin_to_bm_y
            self.z = self.vert_reflect + self.pin_to_bm_z
            return self.y,self.z

        elif option == "both_bm":
            self.y = self.hori_reflect + self.pin_to_bm_y
            self.z = self.vert_reflect + self.pin_to_bm_z
            return self.y,self.z

        else:
            self.y = -1
            self.z = -1
            return 0

    def moveY(self, ypos):
        self.stage_y.move(ypos)

    def moveZ(self, zpos):
        self.stage_z.move(zpos)

    def move(self):
        print "Parameters: Moving stage to (x,y)=(%5d, %5d)\n" % (self.y, self.z)
        if self.y != -1 and self.z != -1:
            self.stage_y.move(self.y)
            self.stage_z.move(self.z)
        else:
            print "Pulse value is wrong"

    def monDirPIN(self):
        self.setPulse("dire_pin")
        self.move()

    def monVFMPIN(self):
        self.setPulse("vfm_pin")
        self.move()

    def monBothPIN(self):
        self.setPulse("both_pin")
        self.move()

    def getPos(self):
        ypos = self.stage_y.getPosition()[0]
        zpos = self.stage_z.getPosition()[0]
        print ypos,zpos
        return ypos,zpos

if __name__ == "__main__":
    host = '172.24.242.59'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    mu = MirrorTuneUnit(s)
    mu.getPos()

    print "Type: dire_pin/hfm_pin/vfm_pin/both_pin"
    print "    : dire_bm/hfm_bm/vfm_bm/both_bm"
    msg = raw_input()
    y,z=mu.setPulse(msg)
    mu.moveY(y)
    mu.moveZ(z)

    s.close()
