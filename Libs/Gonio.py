#!/bin/env python 
import sys
import socket
import time
import math
#from pylab import *

# My library
from Motor import *
from BSSconfig import *

class Gonio:

    def __init__(self,server):
        self.s=server
        self.goniox=Motor(self.s,"bl_45in_st2_gonio_1_x","pulse")
        self.gonioy=Motor(self.s,"bl_45in_st2_gonio_1_y","pulse")
        self.gonioz=Motor(self.s,"bl_45in_st2_gonio_1_z","pulse")
        self.goniozz=Motor(self.s,"bl_45in_st2_gonio_1_zz","pulse")
        self.phi=Motor(self.s,"bl_45in_st2_gonio_1_omega","pulse")
        #self.enc=Enc()
        #self.enc.openPort()

        self.v2p_x = 4000
        self.v2p_y = 10000
        self.v2p_z = 4000
        self.v2p_omega = 5000
        self.v2p_zz = 10000

        self.sense_x = 1
        self.sense_y = 1
        self.sense_z = -1
        self.base=0.0

    def goMountPosition(self):
        bssconf=BSSconfig()
        mountx=bssconf.getValue("Cmount_Gonio_X")
        mounty=bssconf.getValue("Cmount_Gonio_Y")
        mountz=bssconf.getValue("Cmount_Gonio_Z")

        print mountx,mounty,mountz

        self.rotatePhi(0.0)
        self.moveXYZmm(mountx,mounty,mountz)

    def setSpeed(self):
        com="put/bl_45in_st2_gonio_1_phi_speed/1200000pps"
        return 0

    def getPhi(self):
        phi_pulse=self.phi.getPosition()
        #print phi_pulse
        phi_deg=float(phi_pulse[0])/float(self.v2p_omega)+self.base

        phi_deg=round(phi_deg,3)
        #print phi_deg
        return phi_deg

    def movePint(self,value_um):
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

    def moveTrans(self,trans):
        # current pulse
        curr_y=int(self.getY()[0])

        # relative movement unit [um]
        move_y=-trans

        # marume[um]
        move_y=round(move_y,5)
        #print "round %8.4f "%(move_y)

        # [um] to [pulse]
        move_y=int(move_y*10)

        # final position
        final_y=curr_y+move_y

        #print curr_y,final_y

        # final position
        #print "final %8d\n"%(final_y)
        self.moveY(final_y)

    def moveUpDown(self,height):
        curr_phi=self.getPhi()
        #print "PHI:%12.5f" % curr_phi
        curr_phi_rad=math.radians(curr_phi)

        # current pulse
        curr_x=int(self.getX()[0])
        curr_z=int(self.getZ()[0])
        #print curr_x,curr_z

        # unit [um]
        # Goniometer X should be (-) for going up
        move_x=-self.sense_x*height*math.sin(curr_phi_rad)
        move_z=self.sense_z*height*math.cos(curr_phi_rad)

        # marume[um]
        move_x=round(move_x,5)
        move_z=round(move_z,5)
        print "move_x,z %8.4f %8.4f %5.2f[deg]\n"%(move_x,move_z,curr_phi)

        # [um] to [pulse]
        # mm_to_pulse : self.v2p_x
        um_to_pulse_x = self.v2p_x/1000.0
        um_to_pulse_z = self.v2p_z/1000.0
        move_x=int(move_x*um_to_pulse_x)
        move_z=int(move_z*um_to_pulse_z)

        # final position
        final_x=curr_x+move_x
        final_z=curr_z+move_z

        # final position
        #print "final %8d %8d\n"%(final_x,final_z)
        self.moveXZ(final_x,final_z)

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

    def rotatePhiRelative(self,relphi):
        curr_deg=self.getPhi()
        final_deg=curr_deg+relphi
        print "FINAL=",final_deg
        self.rotatePhi(final_deg)

    def rotatePhi(self,phi):
        self.setSpeed()
        if phi>720.0:
            phi=phi-720.0
        if phi<-720.0:
            phi=phi+720.0

        dif=phi*self.v2p_omega

        orig=self.base*self.v2p_omega
        pos_pulse=-(orig+-dif)

        self.phi.move(pos_pulse)
        #print pos_pulse

    def getXmm(self):
        pls=float(self.goniox.getPosition()[0])
        xmm = self.sense_x*pls/self.v2p_x
        return xmm

    def getYmm(self):
        pls=float(self.gonioy.getPosition()[0])
        ymm = self.sense_y*pls/self.v2p_y
        return ymm

    def getZmm(self):
        pls=float(self.gonioz.getPosition()[0])
        zmm = self.sense_z*pls/self.v2p_z
        return zmm

    def getZZmm(self):
        pls=float(self.goniozz.getPosition()[0])
        zmm = pls/self.v2p_zz
        return zmm

    def getZZ(self):
        tmp=int(self.goniozz.getPosition()[0])
        return tmp

    def moveZZpulse(self,value):
        self.goniozz.move(value)

    def moveZZrel(self,value): ## value is in [um]
        move_pulse=value*4

        # current ZZ [pulse]
        curr_zz=self.goniozz.getPosition()[0]

        # final position [pulse]
        final=curr_zz+move_pulse

        # backlush 5[um]
        if value<0.0:
            bl_pos=final-20
            self.goniozz.move(bl_pos)

        # move
        self.goniozz.move(final)

    def getX(self):
        return self.goniox.getPosition()

    def getY(self):
        return self.gonioy.getPosition()

    def getZ(self):
        return self.gonioz.getPosition()

    def moveZ(self,value):
        self.gonioz.move(value)

    def moveY(self,value):
        self.gonioy.move(value)

    def moveXYZ(self,movex,movey,movez):
        # UNIT: [pulse]
        self.goniox.move(movex)
        self.gonioy.move(movey)
        self.gonioz.move(movez)

    def getXYZmm(self):
        x=self.getXmm()
        y=self.getYmm()
        z=self.getZmm()

        return x,y,z

    def moveXYZmm(self,movex,movey,movez):
        # convertion
        xpulse=self.sense_x*movex*self.v2p_x
        ypulse=self.sense_y*movey*self.v2p_y
        zpulse=self.sense_z*movez*self.v2p_z
        # UNIT: [pulse]
        self.goniox.move(xpulse)
        self.gonioy.move(ypulse)
        self.gonioz.move(zpulse)

    def goXYZmm(self,movex,movey,movez):
        # convertion
        xpulse=self.sense_x*movex*self.v2p_x
        ypulse=self.sense_y*movey*self.v2p_y
        zpulse=self.sense_z*movez*self.v2p_z
        # UNIT: [pulse]
        self.goniox.nageppa(xpulse)
        self.gonioy.nageppa(ypulse)
        self.gonioz.nageppa(zpulse)

    def moveXmm(self,movex):
        # convertion
        xpulse=self.sense_x*movex*self.v2p_x
        # UNIT: [pulse]
        self.goniox.move(xpulse)

    def moveYmm(self,movey):
        ypulse=self.sense_y*movey*self.v2p_y
        # UNIT: [pulse]
        self.gonioy.move(ypulse)

    def moveZmm(self,movez):
        zpulse=self.sense_z*movez*self.v2p_z
        # UNIT: [pulse]
        self.gonioz.move(zpulse)

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

if __name__=="__main__":
    host = '172.24.242.59'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    gonio=Gonio(s)
    #print gonio.rotatePhi(90)
    print gonio.moveXYZmm(-0.750, 8.5, 0.020)
    #print gonio.getXYZmm()
    #gonio.moveUpDown(200)
    #gonio.moveTrans(20)
    #for phi in [0,45,90,135]:
        #gonio.rotatePhi(phi)
        #gonio.moveUpDown(20)
        #print gonio.getXYZmm()
    #print gonio.getPhi()
    #print gonio.getZZmm()
    #gonio.rotatePhiRelative(90.0)

    s.close()
