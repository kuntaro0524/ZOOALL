#!/bin/env python 
import sys
import socket
import time
import math
from pylab import *

from Motor import *
import BSSconfig
from configparser import ConfigParser, ExtendedInterpolation

class Gonio:
    def __init__(self,server):
        self.s=server
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        # beamline name is extracted from beamline.ini
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])
        # section: beamline, option: beamline
        self.beamline = self.config.get("beamline", "beamline")

        # axis names
        # Read from beamline.ini 
        # gonio x > section: axes, option: gonio_x_name
        self.x_name = self.config.get("axes", "gonio_x_name")
        # gonio y > section: axes, option: gonio_y_name
        self.y_name = self.config.get("axes", "gonio_y_name")
        # gonio z > section: axes, option: gonio_z_name
        self.z_name = self.config.get("axes", "gonio_z_name")
        # gonio zz > section: axes, option: gonio_zz_name
        self.zz_name = self.config.get("axes", "gonio_zz_name")
        # gonio rotation axis > section: axes, option: gonio_rot_name
        self.rot_name = self.config.get("axes", "gonio_rot_name")

        # axes definitions
        self.goniox=Motor(self.s,"bl_%s_%s" % (self.bl_object, self.x_name),"pulse")
        self.gonioy=Motor(self.s,"bl_%s_%s" % (self.bl_object, self.y_name),"pulse")
        self.gonioz=Motor(self.s,"bl_%s_%s" % (self.bl_object, self.z_name),"pulse")
        self.goniozz=Motor(self.s,"bl_%s_%s" % (self.bl_object, self.zz_name),"pulse")
        self.phi=Motor(self.s,"bl_%s_%s" % (self.bl_object, self.rot_name),"pulse")
        self.base = 0.0

        # initialization flag
        self.isPrep = False

        # BL32XU specific sense parameter for a rotation axis: mysterious setting
        if self.beamline == "BL32XU":
            self.sense_phi_bl32xu = -1.0
        else:
            self.sense_phi_bl32xu = 1.0

        # Read bss.config 
        self.v2p_x, self.sense_x = self.bssconf.getPulseInfo(self.x_name)
        self.v2p_y, self.sense_y = self.bssconf.getPulseInfo(self.y_name)
        self.v2p_z, self.sense_z = self.bssconf.getPulseInfo(self.z_name)
        self.v2p_zz, self.sense_zz = self.bssconf.getPulseInfo(self.zz_name)
        self.v2p_rot, self.sense_phi = self.bssconf.getPulseInfo(self.rot_name)
        self.isPrep = True

    def goMountPosition(self):
        bssconf=BSSconfig()
        mountx=bssconf.getValue("Cmount_Gonio_X")
        mounty=bssconf.getValue("Cmount_Gonio_Y")
        mountz=bssconf.getValue("Cmount_Gonio_Z")

        print(mountx,mounty,mountz)

        self.rotatePhi(0.0)
        self.moveXYZmm(mountx,mounty,mountz)

    def setSpeed(self):
        com="put/bl_41in_st2_gonio_1_phi_speed/1200000pps"
        return 0

    def getPhi(self):
        phi_pulse=self.phi.getPosition()
        phi_deg=self.sense_phi*float(phi_pulse[0])/float(self.v2p_rot)+self.base
        phi_deg=round(phi_deg,3)

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
        # move_y=int(move_y*10)
        um_to_pulse_y = self.v2p_y/1000.0
        move_y=int(move_y*um_to_pulse_y)

        # final position
        final_y=curr_y+move_y

        #print curr_y,final_y

        # final position
        #print "final %8d\n"%(final_y)
        self.moveY(final_y)

    def moveUpDown(self,height):
        curr_phi=self.getPhi()
        print("PHI:%12.5f"% curr_phi)
        curr_phi_rad=math.radians(curr_phi)

        # current pulse
        curr_x=int(self.getX()[0])
        curr_z=int(self.getZ()[0])
        #print curr_x,curr_z

        # unit [um]
        # Goniometer X should be (-) for going up
        # BL41XU code ?? 230516 -> incorrect movement at BL32XU
        # move_x=-self.sense_x*height*math.sin(curr_phi_rad)
        move_x=self.sense_x*height*math.sin(curr_phi_rad)
        move_z=self.sense_z*height*math.cos(curr_phi_rad)

        # marume[um]
        move_x=round(move_x,5)
        move_z=round(move_z,5)
        print("move_x,z %8.4f %8.4f %5.2f[deg]\n"%(move_x,move_z,curr_phi))

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
        print("PPPPPPPPPPPPPPPPPPPPPPPPPPPHIIIIIIIIIIIIIIIIIi:%12.5f" % curr_phi)
        curr_phi=math.radians(curr_phi)

        # unit [um]
        # Correct at BL41XU? This line is not suitable for BL32XU.
        #move_x=-height*math.sin(curr_phi)
        move_x=height*math.sin(curr_phi)
        move_z=height*math.cos(curr_phi)

        # marume[um]
        move_x=round(move_x,5)
        move_z=round(move_z,5)

        # unit conv[mm]
        mm_x=move_x/1000.0
        mm_z=move_z/1000.0

        return mm_x,mm_z

    def calcUpDown(self,height,phi):
        phi=math.radians(phi)

        # unit [um]
        # Correct at BL41XU? This line is not suitable for BL32XU.
        # The code is now same with BL41XU. 2023/05/24
        # sense.phi is correctly used in 'getPhi' method.
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
        print("FINAL=",final_deg)
        self.rotatePhi(final_deg)

    def rotatePhi(self,phi):
        self.setSpeed()
        if phi>720.0:
            phi=phi-720.0
        if phi<-720.0:
            phi=phi+720.0

        dif=phi*self.v2p_rot

        orig=self.base*self.v2p_rot
        pos_pulse=self.sense_phi*self.sense_phi_bl32xu*(orig+-dif)
        self.phi.move(pos_pulse)

    def scan2D(self, prefix, zrange, yrange, ch, time):
        # output file
        ofile = prefix + "_gonio2D.scn"
        of = open(ofile, "w")

        # zrange, yrange unit[um]
        start_i = 0
        end_i = 1
        step_i = 2

        # loop
        for zd in arange(zrange[start_i], zrange[end_i], zrange[step_i]):
            zd_pulse = int(zd * 10)
            self.moveZ(zd_pulse)

            for yd in arange(yrange[start_i], yrange[end_i], yrange[step_i]):
                yd_pulse = int(yd * 10)
                self.moveY(yd_pulse)

                # get Count at each position
                cnt = self.goniox.getCount(ch, time)

                of.write("%8.5f %8.5f %8d\n" % (zd, yd, cnt))
                of.flush()
            of.write("\n\n")

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

    def wireRoughZ(self, ch1):
        # current position
        x, y, z = self.getXYZmm()

        # note wire default position should be left/lower compared to the X-ray center
        x1, y1, z1 = self.findZhalf(0, 500, 10, 3)

        print("Found Z=%10.5f" % z1)
        print("Found X=%10.5f" % x1)

        vdiff = math.sqrt(math.pow((x - x1), 2) + math.pow((y - y1), 2) + math.pow((z - z1), 2))
        print("Distance between found and initial position:%8.3f\n" % (vdiff))

        ## Next scan range
        # Rough edge of Z=z1
        # Start point: 50um before the edge
        newz = z1 - 0.05
        print("Next scan start Z=%10.5f " % newz)

        # note wire default position should be left/lower compared to the X-ray center
        self.moveXYZmm(x, y, newz)
        x1, y1, z1 = self.findZhalf(0, 100, 5, 3)

        ## Movement to half position
        # Rough edge of Z=z1
        # Start point: 25um before the edge
        newz = z1 - 0.025

        # note wire default position should be left/lower compared to the X-ray center
        self.moveXYZmm(x, y, newz)
        x1, y1, z1 = self.findZhalf(0, 50, 2, 3)

        self.moveXYZmm(x, y, z)

        return x1, z1

    def wireRoughY(self, ch1):
        # current position
        x, y, z = self.getXYZmm()

        # note wire default position should be left/lower compared to the X-ray center
        x1, y1, z1 = self.findYhalf(0, 500, 10, 3)

        hdiff = y1 - y
        print("hdiff:%8.3f\n" % (hdiff))

        ## Movement to half position
        newy = y1 - 0.05

        # note wire default position should be left/lower compared to the X-ray center
        self.moveXYZmm(x, newy, z)
        x1, y1, z1 = self.findYhalf(0, 100, 5, 3)

        ## Movement to half position
        newy = y1 - 0.025
        self.moveXYZmm(x, newy, z)
        x1, y1, z1 = self.findYhalf(0, 50, 2, 3)

        self.moveXYZmm(x, y, z)

        return y1

    def wireRoughScan(self, ch1):
        # current position
        x, y, z = self.getXYZmm()

        # note wire default position should be left/lower compared to the X-ray center
        x1, y1, z1 = self.findZhalf(0, 200, 10, 3)
        x2, y2, z2 = self.findYhalf(0, 200, 10, 3)

        vdiff = math.sqrt(math.pow((x - x1), 2) + math.pow((y - y1), 2) + math.pow((z - z1), 2))
        hdiff = y2 - y
        print("Vdiff:%8.3f Hdiff:%8.3f\n" % (vdiff, hdiff))

        ## Movement to half position
        newx = (x + x1) / 2.0
        newz = (z + z1) / 2.0
        newy = (y + y2) / 2.0

        # note wire default position should be left/lower compared to the X-ray center
        self.moveXYZmm(newx, y, newz)
        x1, y1, z1 = self.findZhalf(0, 100, 5, 3)
        self.moveXYZmm(x, newy, z)
        x2, y2, z2 = self.findYhalf(0, 100, 5, 3)

        self.moveXYZmm(x, y, z)

        return x1, y1, z1, x2, y2, z2

    def findZhalf(self, start, end, step, ch1):
        counter = Count(self.s, ch1, 0)
        save = float(counter.getCount(0.1)[0])

        # current position
        x, y, z = self.getXYZmm()

        ## find z
        isFound = False
        for i in arange(start, end, step):
            self.moveUpDown(step)
            x2, y2, z2 = self.getXYZmm()
            pincnt = float(counter.getCount(0.1)[0])
            print(x2, y2, z2, pincnt, save)

            if pincnt < (save / 2.0):
                print("FIND!!: %8.5f\n" % pincnt)
                isFound = True
                break

        if isFound == False:
            print("No found")
            return 0, 0, 0

        # move to the initial position
        self.moveXYZmm(x, y, z)

        return x2, y2, z2

    def findYhalf(self, start, end, step, ch1):
        # start,end,step [um]
        # ch1: counter channel

        counter = Count(self.s, ch1, 0)
        save = float(counter.getCount(0.1)[0])

        # current position
        x, y, z = self.getXYZmm()

        ## find y
        isFound = False
        for i in arange(start, end, step):
            self.moveTrans(step)
            x2, y2, z2 = self.getXYZmm()
            pincnt = float(counter.getCount(0.1)[0])
            print(x2, y2, z2, pincnt, save)

            if pincnt < (save / 2.0):
                print("FIND!!: %8.5f\n" % pincnt)
                isFound = True
                break

        if isFound == False:
            print("No found")
            return 0, 0, 0

        # move to the initial position
        self.moveXYZmm(x, y, z)

        return x2, y2, z2

    def scanZenc(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # start,end,step [um]
        # Counter
        counter = Count(self.s, cnt_ch1, cnt_ch2)

        # Output file
        ofile = prefix + "_gonioz.scn"
        of = open(ofile, "w")

        # scan range
        range = end - start
        ndata = int(range / step) + 1

        if ndata < 0:
            print("range trouble")
            return -1

        # plot preparation
        ax = []
        i1 = []
        i2 = []
        pylab.cla()
        pylab.clf()
        pylab.ion()

        for idx in arange(1, ndata):
            ## [um]
            tpos = start + idx * step

            ## pulse
            tpos_pulse = tpos * 10

            ## move
            self.gonioz.move(tpos_pulse)
            enc_z = self.enc.getZ()

            # Counter
            val1, val2 = counter.getCount(time)

            ax.append(enc_z)
            i1.append(val1)
            i2.append(val2)
            # inorm=val1/val2
            # pylab.plot(ax,i1,ax,i2)
            pylab.plot(ax, i1, "o-")
            pylab.draw()
            # print enc_z
            of.write("12345 %8.5f %8d %8d\n" % (enc_z, val1, val2))

        of.close()

        # Analysis and Plot
        ana = AnalyzePeak(ofile)
        comment = "TEST"
        outfig = prefix + "_gonioz.png"
        drvfile = "%s_gonioz_drv.scn" % prefix

        # Analysis and Plot
        ana = AnalyzePeak(ofile)
        fwhm, center = ana.analyzeKnife("gonio Z[um]", "intensity[cnt]", drvfile, outfig, "", "PEAK")

        return fwhm, center

    def scanVert2(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # XYZ [mm]
        curr_x, curr_y, curr_z = self.getXYZmm()

        # start,end,step[um]
        counter = Count(self.s, cnt_ch1, cnt_ch2)

        # Output file
        ofile = prefix + "_gonioV.scn"
        of = open(ofile, "w")

        # Move to start position
        self.moveUpDown(start)
        work_height = start

        for ud in arange(start, end + step, step):
            self.moveUpDown(step)
            work_height += step

            # Counter
            val1, val2 = counter.getCount(time)

            # Phi
            phi = self.getPhi()

            x, y, z = self.getXYZmm()
            of.write("12345 %10.5f %8d %8d %10.2f %10.5f %10.5f %10.5f\n"
                     % (work_height, val1, val2, phi, x, y, z))
            of.flush()

        of.close()

        # XYZ [mm]
        self.moveXYZmm(curr_x, curr_y, curr_z)
        return 1

    def scanVertical(self, prefix, npts, step, cnt_ch1, cnt_ch2, time):
        # XYZ [mm]
        curr_x, curr_y, curr_z = self.getXYZmm()

        # start,end,step[um]
        counter = Count(self.s, cnt_ch1, cnt_ch2)

        # Output file
        ofile = prefix + "_gonioV.scn"
        of = open(ofile, "w")

        # Scan range
        scan_katagawa = npts / 2 + 1
        start = -float(scan_katagawa) * step
        end = float(scan_katagawa) * step
        range = end - start
        ndata = int(range / step) + 1

        if ndata < 0:
            print("range trouble")
            return -1

        # plot preparation
        ax1 = []
        ax2 = []
        i1 = []
        i2 = []

        # Move to start position
        self.moveUpDown(start)

        work_height = start

        for idx in arange(1, ndata):
            ## [um]
            # print "LOOP1"
            self.moveUpDown(step)
            work_height += step

            enc_x = self.enc.getX()
            enc_y = self.enc.getY()
            enc_z = self.enc.getZ()

            # Counter
            val1, val2 = counter.getCount(time)

            # Phi
            phi = self.getPhi()

            # of.write("12345 %10.5f %10.5f %10.5f %10.5f %8.2f %8d %8d\n"%(enc_x,enc_y,enc_z,work_height,phi,val1,val2))
            # of.write("12345 %10.5f %8d %8d %10.2f\n"%(work_height,val1,val2,phi))
            x, y, z = self.getXYZmm()
            of.write("12345 %10.5f %8d %8d %10.2f %10.5f %10.5f %10.5f\n"
                     % (work_height, val1, val2, phi, x, y, z))
            of.flush()

        of.close()

        # XYZ [mm]
        self.moveXYZmm(curr_x, curr_y, curr_z)
        return 1

    def scanZencNoAna(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # self.prepScan()
        # Counter
        counter = Count(self.s, cnt_ch1, cnt_ch2)

        # Output file
        ofile = prefix + "_gonioz.scn"
        of = open(ofile, "w")

        # scan range
        range = end - start
        ndata = int(range / step) + 1

        if ndata < 0:
            print("range trouble")
            return -1

        # plot preparation
        ax = []
        i1 = []
        i2 = []

        pylab.cla()
        pylab.clf()
        pylab.ion()

        for idx in arange(1, ndata):
            ## [um]
            tpos = start + idx * step

            ## pulse
            tpos_pulse = tpos * 10

            ## move
            self.gonioz.move(tpos_pulse)
            enc_z = self.enc.getZ()

            # Counter
            val1, val2 = counter.getCount(time)

            ax.append(enc_z)
            i1.append(val1)
            i2.append(val2)
            # inorm=val1/val2
            # pylab.plot(ax,i1,ax,i2)
            pylab.plot(ax, i1, "o-")
            pylab.draw()
            of.write("12345 %8.5f %8d %8d\n" % (enc_z, val1, val2))

        of.close()

    def scanXencNoAna(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # self.prepScan()
        # Counter
        counter = Count(self.s, cnt_ch1, cnt_ch2)

        # Output file
        ofile = prefix + "_goniox.scn"
        of = open(ofile, "w")

        # scan range
        range = end - start
        ndata = int(range / step) + 1

        if ndata < 0:
            print("range trouble")
            return -1

        # plot preparation
        ax = []
        i1 = []
        i2 = []
        pylab.cla()
        pylab.clf()
        pylab.ion()

        for idx in arange(1, ndata):
            ## [um]
            tpos = start + idx * step

            ## pulse
            tpos_pulse = tpos * 10

            ## move
            self.goniox.move(tpos_pulse)
            enc_x = self.enc.getX()

            # Counter
            val1, val2 = counter.getCount(time)

            ax.append(enc_x)
            i1.append(val1)
            i2.append(val2)
            # inorm=val1/val2
            pylab.plot(ax, i1, "o-")
            pylab.draw()
            of.write("12345 %8.5f %8d %8d\n" % (enc_x, val1, val2))

        of.close()

    def scanYenc(self, prefix, start, end, step, cnt_ch1, cnt_ch2, time):
        # gonioY is -1
        start = -start
        end = -end
        step = -step

        # Counter
        counter = Count(self.s, cnt_ch1, cnt_ch2)

        # Output file
        ofile = prefix + "_gonioy.scn"
        of = open(ofile, "w")

        # scan range
        range = end - start
        ndata = int(range / step) + 1

        if ndata < 0:
            print("range trouble")
            return -1

        # plot preparation
        ax = []
        i1 = []
        i2 = []
        pylab.cla()
        pylab.clf()
        pylab.ion()

        for idx in arange(1, ndata):
            ## [um]
            tpos = start + idx * step

            ## pulse
            tpos_pulse = tpos * 10

            ## move
            self.gonioy.move(tpos_pulse)
            enc_y = self.enc.getY()
            # print enc_y

            # Counter
            val1, val2 = counter.getCount(time)

            ax.append(enc_y)
            i1.append(val1)
            i2.append(val2)
            # inorm=val1/val2
            # pylab.plot(ax,i1,ax,i2)
            pylab.plot(ax, i1, "o-")
            pylab.draw()
            of.write("12345 %8.5f %8d %8d\n" % (enc_y, val1, val2))

        of.close()

        # Analysis and Plot
        ana = AnalyzePeak(ofile)
        outfig = prefix + "_gonioy.png"
        drvfile = "%s_gonioy_drv.scn" % prefix

        # Analysis and Plot
        ana = AnalyzePeak(ofile)
        fwhm, center = ana.analyzeKnife("gonio Y[um]", "intensity[cnt]", drvfile, outfig, "", "PEAK")

        return fwhm, center

    def findCenter(self, ofile, start, end, step, time, unit):
        # Set step
        # maxvalue=self.gonioz.axisScan(ofile,start,end,step,self.cnt_ch,self.cnt_ch-1,time,unit)
        # return(maxvalue)
        print("find center")

    def getEnc(self):
        # Unit of return value is [um]
        enc_x = self.enc.getX() / 1000.0
        enc_y = self.enc.getY() / 1000.0
        enc_z = self.enc.getZ() / 1000.0
        return enc_x, enc_y, enc_z

    def kill(self):
        del self

if __name__ == "__main__":
    # host = '192.168.163.1'
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    gonio = Gonio(s)
    #print((gonio.getXYZmm()))
    #gonio.moveXYZmm(-1.0,0.5,-0.3)
    #gonio.rotatePhi(135.0)
    #gonio.moveUpDown(100.0)
    print(gonio.getPhi())

    s.close()