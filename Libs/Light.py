#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *

import BSSconfig
from configparser import ConfigParser, ExtendedInterpolation

# information of collision between BM and Gonio
class Light:
    def __init__(self, server):
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        # beamline.ini
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])

        self.s = server
        # names of collimator axes
        try:
            self.light_z_name = self.config.get("axes", "light_z_name")
        except:
            # 軸情報が取得できないのでエラーで終了すべき
            print("Error: cannot get axis information from beamline.ini")
            sys.exit(1)
        # 軸のインスタンスを作成する
        self.light_name = "bl_%s_%s" % (self.bl_object, self.light_z_name)
        print(self.light_name)
        self.light_z = Motor(self.s, self.light_name, "pulse")
        # 軸のパルス分解能を取得する
        self.v2p_z, self.sense_z, self.home_z = self.bssconf.getPulseInfo(self.light_z_name)
        print(self.v2p_z, self.sense_z)

    def getEvacuate(self):
        self.on_pulse, self.off_pulse = self.bssconf.getLightEvacuateInfo(self.light_z_name)
        print("ON (VME value):",self.on_pulse)
        print("OFF(VME value):",self.off_pulse)
        # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
        # print("BLO=bl_%s_%s" % (self.bl_object, self.evac_axis_name))
        # self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
        self.isInit = True

    def getPos(self):
        return self.light_z.getPosition()

    def on(self):
        print("Moving to %s" % self.on_pulse)
        self.light_z.move(self.on_pulse)

    def off(self):
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
    # light.off()
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
