#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *
import BSSconfig

# information of collision between BM and Gonio
class Light:
    def __init__(self, server):
        self.bssconf = BSSconfig.BSSconfig('/isilon/blconfig/bl41xu/bss/bss.config')
        self.bl_object = self.bssconf.getBLobject()

        self.s = server
        self.axis_name = "st2_light_1_z"
        self.light_z = Motor(self.s, "bl_%s_%s"%(self.bl_object, self.axis_name),"pulse")
        self.v2p_x, self.sense_x = self.bssconf.getPulseInfo(self.axis_name)

        self.isPrep = False

    def getEvacuate(self):
        self.on_pulse, self.off_pulse = self.bssconf.getLightEvacuateInfo(self.axis_name)

        self.isPrep = True

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
        if self.isPrep == False: 
            self.getEvacuate()
        self.light_z.move(self.on_pulse)

    def off(self):
        if self.isPrep == False: 
            self.getEvacuate()
        self.light_z.move(self.off_pulse)

    def intensityMonitorOn(self):
        self.light_z.move(self.sense_x*12000)

    def intensityMonitorOff(self):
        self.light_z.move(self.sense_x*500)

    def goOn(self):
        self.light_z.nageppa(self.on_pos)

    def go(self, value):
        self.light_z.nageppa(value)

    def goOff(self):
        self.light_z.nageppa(self.off_pos)

if __name__ == "__main__":
    host = '172.24.242.54'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    light = Light(s)
    light.intensityMonitorOn()
    time.sleep(1)
    light.intensityMonitorOff()

    s.close()
