#!/bin/env python import sys
import socket
import time
import os

# My library
import Received
import Motor
import WebSocketBSS

import BSSconfig
from configparser import ConfigParser, ExtendedInterpolation

import BaseAxis

# information of collision between BM and Gonio
class Light(BaseAxis.BaseAxis):
    def __init__(self, server):
        # Light axis
        # axis name on 'beamline.ini'
        conf_name = "light_z_name"
        super().__init__(server, conf_name, axis_type="motor", isEvacuate=True)
        self.light_z = self.motor

        # web socket or not
        self.isWebsocket = False

        # 250307: 今はまだBL41XUのみだが、ゆくゆくは WebSocketで退避制御などを
        # 行いたいので、そのための準備
        # beamlin.ini, [control] section: isWebsocket = True
        if self.config.has_option("control", "isWebsocket"):
            self.isWebsocket = self.config.getboolean("control", "isWebsocket")
            if self.isWebsocket:
                self.websock = WebSocketBSS.WebSocketBSS()

        # initialization flag
        self.isInit = False

    def getEvacuate(self):
        print("ON (VME value):",self.on_pulse)
        print("OFF(VME value):",self.off_pulse)
        # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
        # print("BLO=bl_%s_%s" % (self.bl_object, self.evac_axis_name))
        # self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
        self.isInit = True

    def getPos(self):
        return self.light_z.getPosition()

    def on(self):
        if self.isWebsocket:
            self.websock.light("on")
        else:
            if self.isInit == False: 
                self.getEvacuate()
            print("Moving to %s" % self.on_pulse)
            self.light_z.move(self.on_pulse)

    def off(self):
        if self.isWebsocket:
            self.websock.light("off")
        else:
            if self.isInit == False: 
               self.getEvacuate()
            print("Moving to %s" % self.off_pulse)
            self.light_z.move(self.off_pulse)

if __name__ == "__main__":
    from configparser import ConfigParser, ExtendedInterpolation

    # read IP address for BSS connection from beamline.config 
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(config_path)
    # host = config.get("server", "bss_server")
    host = config.get("server", "blanc_address")
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    light = Light(s)
    light.getEvacuate()
    # print(light.getPos())
    light.on()
    light.off()
    # print(light.light_z.getPosition())
    # light.getEvacuate()
    # light.relDown()
    # light.go(int(argv[1])
    # time.sleep(20.0)
    # light.off()
    # time.sleep(20.0)
    # light.on()
    # time.sleep(20.0)

    s.close()
