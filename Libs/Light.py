#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *


# information of collision between BM and Gonio

#
class Light:
    def __init__(self, server):
        self.s = server
        self.light_z = Motor(self.s, "bl_32in_st2_light_1_z", "pulse")

        self.off_pos = 10000  # pulse
        self.on_pos = 0  # pulse

    def goDown(self):
        curr_pos = self.light_z.getPosition()[0]
        target_pos = curr_pos + 1000
        self.light_z.move(target_pos)

    def relDown(self):
        curr_pos = self.light_z.getPosition()[0]
        target_pos = curr_pos - 100
        self.light_z.move(target_pos)

    def on(self):
        self.light_z.move(self.on_pos)

    def off(self):
        self.light_z.move(self.off_pos)

    def goOn(self):
        self.light_z.nageppa(self.on_pos)

    def go(self, value):
        self.light_z.nageppa(value)

    def goOff(self):
        self.light_z.nageppa(self.off_pos)


if __name__ == "__main__":
    host = '172.24.242.41'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    light = Light(s)
    # light.relDown()
    # light.go(int(argv[1])
    light.on()
    # time.sleep(20.0)
    # light.off()
    # time.sleep(20.0)
    # light.on()
    # time.sleep(20.0)

    s.close()
