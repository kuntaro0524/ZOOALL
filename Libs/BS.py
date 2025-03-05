#!/bin/env python 
import sys
import socket
import time
import os

# My library
from Received import *
from Motor import *
from MyException import *
from Count import *
import BSSconfig
from configparser import ConfigParser, ExtendedInterpolation
import WebSocketBSS

class BS:
    def __init__(self, server):
        self.s = server
<<<<<<< HEAD
        
        # Beamline object
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        # configure file "beamline.ini"
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path="%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.config.read(config_path)

        # 初期値を入れておく（軸が定義されているかされていないかわからない）
        self.bs_y_name = ""
        self.bs_z_name = ""

        try:
            # beam stopper axis definition
            # beam stopper axis name > section: axes, option: bs_y_name
            self.bs_y_name = self.config.get("axes", "bs_y_name")
        except:
            # 軸情報が取得できないのでWargningを出す
            print("beam stopper y")
            print("Warning: cannot get axis information from beamline.ini")

        try: 
            # beam stopper axis name > section: axes, option: bs_z_name
            self.bs_z_name = self.config.get("axes", "bs_z_name")
        except:
            # 軸情報が取得できないのでWarningを出す
            print("Error: cannot get axis information from beamline.ini")

        # Motor objectを作成する
        # どちらの名前も空の場合はエラーで終了する
        if self.bs_y_name == "" and self.bs_z_name == "":
            print("BS check")
            print("Error: cannot get axis information from beamline.ini")
            sys.exit(1) 
        
        if self.bs_y_name != "":
            self.bs_y = Motor(self.s, f"bl_{self.bl_object}_{self.bs_y_name}", "pulse")
            self.bs_y_v2p, self.bs_y_sense, self.bs_y_home = self.bssconf.getPulseInfo(self.bs_y_name)
        if self.bs_z_name != "":
            self.bs_z = Motor(self.s, f"bl_{self.bl_object}_{self.bs_z_name}", "pulse")
            self.bs_z_v2p, self.bs_z_sense, self.bs_z_home = self.bssconf.getPulseInfo(self.bs_z_name)

        # BL41XU -> Websocket
        self.isWwebsocket = False
        self.beamline = self.config.get("beamline", "beamline")
        if self.beamline == "BL41XU":
            self.websock = WebSocketBSS.WebSocketBSS()
            self.isWwebsocket = True

        # Read configure file and get parameters
        self.isInit = False

    # 退避する軸はビームラインごとに違っているのでそれを取得する必要がある。
    # 現時点では１軸しか取得できないのでそうでないビームライン（ビームストッパーをYZどちらも退避）が出てくると修正する必要がある
    def getEvacuate(self):
        evacinfo = self.config.get("axes", "bs_evacinfo")
        self.evac_axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateInfo(evacinfo)
        print("ON (VME value):",self.on_pulse)
        print("OFF(VME value):",self.off_pulse)
        # 退避軸を自動認識してそれをオブジェクトとして設定してしまう
        self.evac_axis = Motor(self.s, "bl_%s_%s" % (self.bl_object, self.evac_axis_name), "pulse")
        self.isInit = True

    def getZ(self):
        return self.bs_z_sense * int(self.bs_z.getPosition()[0])

    def getY(self):
        return self.bs_y_sense * int(self.bs_y.getPosition()[0])

    def moveY(self, pls):
        v = pls * self.bs_y_sense
        self.bs_y.move(v)

    def moveZ(self, pls):
        v = pls * self.bs_z_sense
        self.bs_z.move(v)

    def scan2D(self, prefix, startz, endz, stepz, starty, endy, stepy):
        counter = Count(self.s, 3, 0)
=======
        self.bs_y = Motor(self.s, "bl_45in_st2_bs_1_y", "pulse")
        self.bs_z = Motor(self.s, "bl_45in_st2_bs_1_z", "pulse")
        self.bs_evacuate = Motor(self.s, "bl_45in_st2_bs_1_y", "pulse") # N.Mizuno 2021/11/22
        self.sense_y = -1
        self.sense_z = 1
        self.sense_evacuate = -1 # N.Mizuno 2021/11/22

        self.isInit = False
        # self.v2p = 2000 # bl_45in_st2_bs_1_z
        self.v2p = 500 # bl_45in_st2_bs_1_y by N.Mizuno 2021/11/22

        # Default value
        # self.off_pos = 30000  # pulse of bs_1_z
        self.off_pos = 4500  # pulse of bs_1_y by N.Mizuno 2021/11/22
        self.on_pos = 0  # pulse
        self.evac_large_holder = -10000

    def getEvacuate(self):
        bssconf = BSSconfig()

        try:
            tmpon, tmpoff = bssconf.getBS()
        except MyException, ttt:
            print ttt.args[0]

        # self.on_pos = float(tmpon) * self.v2p
        # self.off_pos = float(tmpoff) * self.v2p
        # by N.Mizuno 2021/11/22
        self.on_pos = float(tmpon) * self.v2p * self.sense_evacuate
        self.off_pos = float(tmpoff) * self.v2p * self.sense_evacuate

        self.isInit = True
        print self.on_pos, self.off_pos

    def getZ(self):
        return self.sense_z * int(self.bs_z.getPosition()[0])

    def getY(self):
        return self.sense_y * int(self.bs_y.getPosition()[0])

    def moveY(self, pls):
        v = pls * self.sense_y
        self.bs_y.move(v)

    def moveZ(self, pls):
        v = pls * self.sense_z
        self.bs_z.move(v)

    def scan2D(self, prefix, startz, endz, stepz, starty, endy, stepy):
        counter = Count(self.s, 1, 0)
>>>>>>> zoo45xu/main
        oname = "%s_bs_2d.scn" % prefix
        of = open(oname, "w")

        for z in arange(startz, endz, stepz):
            self.moveZ(z)
            for y in range(starty, endy, stepy):
                self.moveY(y)
                cnt = int(counter.getCount(0.2)[0])
                of.write("%5d %5d %12d\n" % (y, z, cnt))
                of.flush()
            of.write("\n")
        of.close()

<<<<<<< HEAD
    def evacLargeHolder(self):
        self.bs_z.nageppa(self.evac_large_holder)

    def evacLargeHolderWait(self):
        self.bs_z.move(self.evac_large_holder)

    def on(self):
        if self.isWwebsocket:
            self.websock.beamstopper("on")
        else:
            if self.isInit == False:
                self.getEvacuate()
            self.bs_z.move(self.on_pulse)

    def off(self):
        if self.isWwebsocket:
            self.websock.beamstopper("off")
        else:
            if self.isInit == False:
                self.getEvacuate()
            self.bs_z.move(self.off_pulse)
=======
    def go(self, pvalue):
        # self.bs_z.nageppa(pvalue)
        self.bs_evacuate.nageppa(pvalue) # by N.Mizuno 2021/11/22

    def evacLargeHolder(self):
        # self.bs_z.nageppa(self.evac_large_holder)
        self.bs_evacuate.nageppa(self.evac_large_holder) # by N.Mizuno 2021/11/22

    def evacLargeHolderWait(self):
        # self.bs_z.move(self.evac_large_holder)
        self.bs_evacuate.move(self.evac_large_holder) # by N.Mizuno 2021/11/22

    def on(self):
        if self.isInit == False:
            self.getEvacuate()
        # self.bs_z.move(self.on_pos)
        self.bs_evacuate.move(self.on_pos) # by N.Mizuno 2021/11/22

    def off(self):
        if self.isInit == False:
            self.getEvacuate()
        # self.bs_z.move(self.off_pos)
        self.bs_evacuate.move(self.off_pos) # by N.Mizuno 2021/11/22

    def goOn(self):
        if self.isInit == False:
            self.getEvacuate()
        self.go(self.on_pos)

    def goOff(self):
        if self.isInit == False:
            self.getEvacuate()
        self.go(self.off_pos)
>>>>>>> zoo45xu/main

    def isMoved(self):
        isY = self.bs_y.isMoved()
        isZ = self.bs_z.isMoved()

        if isY == 0 and isZ == 0:
            return True
        if isY == 1 and isZ == 1:
            return False


if __name__ == "__main__":
<<<<<<< HEAD
    from configparser import ConfigParser, ExtendedInterpolation
    # read IP address for BSS connection from beamline.config 
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(config_path)
    host = config.get("server", "blanc_address")
=======
    host = '172.24.242.59'
>>>>>>> zoo45xu/main
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

<<<<<<< HEAD
    bs = BS(s)
    bs.getEvacuate()

    # print(bs.getZ())
    # bs.on()
    bs.off()

=======
    # print "Moving BS"
    # print "type on/off:"
    # option=raw_input()
    bs = BS(s)

    #print bs.getZ()
    #print bs.getY()

    #def scan2D(self, prefix, startz, endz, stepz, starty, endy, stepy):
    #bs.scan2D("bs_scan",-2000,2000,200,-500,500,50)

    # bs.on()
    # bs.evacLargeHolder()

    # print z,y
    # bs.go(-30000)

    # bs.getEvacuate()
    # if option=="on":
    #bs.on()
    # elif option=="off":
    #bs.off()
    bs.on()
    bs.off()
>>>>>>> zoo45xu/main
    s.close()
