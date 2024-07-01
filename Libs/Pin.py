#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *

# information of collision between BM and Gonio
class Pin:
    def __init__(self, server):
        self.s = server
        self.light_z = Motor(self.s, "bl_45in_st2_light_1_z", "pulse")

        self.sense = -1

        self.off_pos = -24000  # pulse
        self.on_pos = 0  # pulse

    def getPosition(self):
        curr_pos = self.sense*self.light_z.getPosition()[0]
        return curr_pos

    def goDown(self):
        curr_pos = self.sense*self.light_z.getPosition()[0]
        target_pos = curr_pos + self.sense*1000
        self.light_z.move(target_pos)

    def setPosition(self, def_position):
        self.light_z.move(def_position*self.sense)

    def relDown(self):
        curr_pos = self.light_z.getPosition()[0]
        target_pos = curr_pos - 100
        self.light_z.move(target_pos)

    def on(self):
        self.light_z.move(self.on_pos*self.sense)

    def off(self):
        self.light_z.move(self.off_pos*self.sense)

    def goOn(self):
        self.light_z.nageppa(self.on_pos)

    def go(self, value):
        self.light_z.nageppa(value)

    def goOff(self):
        self.light_z.nageppa(self.off_pos)

if __name__ == "__main__":
    host = '172.24.242.59'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    light = Light(s)
    print light.on()

    s.close()
