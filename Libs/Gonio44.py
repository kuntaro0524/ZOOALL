#!/bin/env python 
import os
import sys
import socket
import time
import math
#from pylab import *

# My library
from Motor import *
import BSSconfig
import datetime
import Zoo
from configparser import ConfigParser, ExtendedInterpolation

# This is very special code for BL44XU

class Gonio44:
    def __init__(self, bss_server_port):
        # This is BSS server port
        self.s = bss_server_port
        self.debug = False

        # beamline name is extracted from beamline.ini
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])
        # section: beamline, option: beamline
        self.beamline = self.config.get("beamline", "beamline")

    def communicate(self, comstr):
        sending_command = comstr.encode()
        self.s.sendall(sending_command)
        recstr = self.s.recv(8000)
        return repr(recstr)

    def waitTillFinish(self):
        query_command = "get/measurement/query"
        while (1):
            self.s.sendall(query_command)
            recstr=self.s.recv(8000)
            svoc_c=self.getSVOC_C(recstr)
            if svoc_c.rfind("ready")!=-1:
                break
            elif svoc_c.rfind("fail")!=-1:
                raise MyException("Something failed.")
            else:
                time.sleep(2.0)
                continue

    def waitTillReady(self):
        query_command = "get/measurement/query"

        while (1):
            recstr = self.communicate(query_command)
            if self.debug: print("Received buffer in isBusy: %s" % recstr)
            svoc_c = self.getSVOC_C(recstr)
            if svoc_c.rfind("ready") != -1:
                break
            elif svoc_c.rfind("fail") != -1:
                raise MyException("Something failed.")
            else:
                time.sleep(0.1)
                continue

    def goMountPosition(self):
        bssconf=BSSconfig()
        mountx=bssconf.getValue("Cmount_Gonio_X")
        mounty=bssconf.getValue("Cmount_Gonio_Y")
        mountz=bssconf.getValue("Cmount_Gonio_Z")

        self.rotatePhi(0.0)
        self.moveXYZmm(mountx,mounty,mountz)

    def setSpeed(self):
        com="put/bl_45in_st2_gonio_1_phi_speed/1200000pps"
        return 0

    def getPhi(self):
        command="get/gonio_spindle/position"

        start_time = datetime.datetime.now()
        recstr = self.communicate(command)
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        print(time_diff)
        value = float(recstr.split('/')[3].replace("degree",""))
        print(value)

        return value

    def getSVOC_C(self,recmes):
        cols=recmes.split("/")
        return cols[3]

    def rotatePhi(self,phi):
        if phi>720.0:
            phi=phi-720.0
        if phi<-720.0:
            phi=phi+720.0

        command="put/gonio_spindle/abs_%fdegree" % phi
        recstr=self.communicate(command)

        start_time = datetime.datetime.now()
        self.waitTillReady()
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time

    def rotatePhiRelative(self, relphi):
        if relphi>720.0:
            relphi=relphi-720.0
        if relphi<-720.0:
            relphi=relphi+720.0

        curr_phi = self.getPhi()
        final_phi = curr_phi + relphi
        command="put/gonio_spindle/rel_%fdegree" % relphi

        self.s.sendall(command)
        self.waitTillFinish()
        recstr=self.s.recv(8000)

    def getXmm(self):
        command="get/gonio_x/position"
        recstr=self.communicate(command)
        self.waitTillReady()
        xmm = float(recstr.split('/')[3].replace("mm",""))
        return xmm

    def getYmm(self):
        command="get/gonio_y/position"
        recstr=self.communicate(command)
        self.waitTillReady()
        ymm = float(recstr.split('/')[3].replace("mm",""))
        return ymm

    def getZmm(self):
        command="get/gonio_z/position"
        recstr=self.communicate(command)
        self.waitTillReady()
        zmm = float(recstr.split('/')[3].replace("mm",""))
        return zmm

    def moveXmm(self, move_xmm):
        command="put/gonio_x/abs_%fmm" % move_xmm
        recstr=self.communicate(command)
        start_time = datetime.datetime.now()
        self.waitTillReady()
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        return True

    def moveYmm(self,move_ymm):
        command="put/gonio_y/abs_%fmm" % move_ymm
        recstr=self.communicate(command)
        start_time = datetime.datetime.now()
        self.waitTillReady()
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        return True

    def moveZmm(self, move_zmm):
        command="put/gonio_z/abs_%fmm" % move_zmm
        recstr=self.communicate(command)
        start_time = datetime.datetime.now()
        self.waitTillReady()
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        return True

    def getXYZmm(self):
        x=self.getXmm()
        y=self.getYmm()
        z=self.getZmm()
        return x,y,z

    def getXYZPhi(self):
        x=self.getXmm()
        y=self.getYmm()
        z=self.getZmm()
        phi=self.getPhi()
        return x,y,z,phi

    def moveXYZmm(self,movex,movey,movez):
        self.moveXmm(movex)
        self.moveYmm(movey)
        self.moveZmm(movez)

        return True

    def moveXYZPhi(self,movex,movey,movez,phi):
        self.moveXmm(movex)
        self.moveYmm(movey)
        self.moveZmm(movez)
        self.rotatePhi(phi)

        return True

    def movePint(self, value_um):
        curr_phi=self.getPhi()
        #print "PHI:%12.5f" % curr_phi
        curr_phi=math.radians(curr_phi)

        # current pulse
        curr_x=int(self.getX()[0])
        curr_z=int(self.getZ()[0])

        # unit [um]
        move_x=value_um*math.cos(curr_phi)
        move_z=value_um*math.sin(curr_phi)

        # marume [um]
        move_x=round(move_x,5)
        move_z=round(move_z,5)

        # marume value[pulse]
        # 1mm/4000pulse
        move_x=int(move_x*10)
        move_z=int(move_z*10)

        #print move_x,move_z

        # final position
        final_x=curr_x+move_x
        final_z=curr_z+move_z

        #print final_x,final_z

        self.moveXZ(final_x,final_z)

        #print move_x,move_z
        #return move_x,move_z

    def moveTrans(self, trans_um):
        # current pulse
        curr_y = self.getYmm()

        # final position
        final_y=curr_y+trans_um/1000.0

        # final position
        self.moveYmm(final_y)

    def moveUpDown(self, height_um):
        curr_phi=self.getPhi()
        cxmm,cymm,czmm = self.getXYZmm()

        # radian convertion
        curr_phi_rad=math.radians(curr_phi)

        # unit [um]
        # Goniometer X should be (-) for going up
        move_x_mm = -height_um*math.sin(curr_phi_rad)/1000.0
        move_z_mm = height_um*math.cos(curr_phi_rad)/1000.0

        # final position
        final_xmm=cxmm+move_x_mm
        final_zmm=czmm+move_z_mm

        print("CURR=", cxmm, cymm, czmm)
        print("TOBE=", final_xmm, cymm, final_zmm)

        # final position
        self.moveXYZmm(final_xmm, cymm, final_zmm)

    # height : height in unit of [um]
    def calcUpDown(self,height):
        curr_phi=self.getPhi()
        #print "PHI:%12.5f" % curr_phi
        curr_phi=math.radians(curr_phi)

        # unit [um]
        move_x=-height*math.sin(curr_phi)
        move_z=height*math.cos(curr_phi)

        # marume[um]
        move_x=round(move_x,5)
        move_z=round(move_z,5)

        # unit conv[mm]
        mm_x=move_x/1000.0
        mm_z=move_z/1000.0

        return mm_x,mm_z

    # height : height in unit of [um]
    # phi : current gonio phi degrees
    def calcUpDown(self,height,phi):
        phi=math.radians(phi)

        # unit [um]
        move_x=-height*math.sin(phi)
        move_z=height*math.cos(phi)

        # marume[um]
        move_x=round(move_x,5)
        move_z=round(move_z,5)

        # unit conv[mm]
        mm_x=move_x/1000.0
        mm_z=move_z/1000.0
        return mm_x,mm_z

    def moveXZ(self,movex,movez):
        self.goniox.move(movex)
        self.gonioz.move(movez)

    def move(self,x,y,z):
        self.goniox.move(x)
        self.gonioy.move(y)
        self.gonioz.move(z)

    def getEnc(self):
        # Unit of return value is [um]
        enc_x=self.enc.getX()/1000.0
        enc_y=self.enc.getY()/1000.0
        enc_z=self.enc.getZ()/1000.0
        return enc_x,enc_y,enc_z

    def kill(self):
        del self

if __name__ == "__main__":
    # Zoo.py construction
    import Zoo
    zoo=Zoo.Zoo()
    zoo.connect()

    zoo_port = zoo.getBSSr()

    # s=""
    # gonio = Gonio44(s, bl="BL44XU")
    # gonio.setBSSport(zoo_port)

    # phi=gonio.getPhi()
    # print("Current phi=", phi)
    # gonio.rotatePhi(0.0)
    # print("GOGOGOGOGO")
    # phi=gonio.getPhi()
    # print("Current phi=", phi)
    # gonio.rotatePhiRelative(90.0)
    # phi=gonio.getPhi()
    # print("Current phi=", phi)

    # xyz=gonio.getXYZmm()
    # print(xyz)

    # xyz=gonio.moveXYZmm(-0.091,5.679,-0.161)

    # gonio.moveZmm(0.1)
    # xyz=gonio.getXYZmm()

    # gonio.moveTrans(0.1)
    # xyz=gonio.getXYZmm()
    # gonio.moveUpDown(100)

    # xyz=gonio.getXYZmm()
    # print(xyz)
