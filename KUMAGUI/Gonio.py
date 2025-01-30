#!/bin/env python 
import sys
import socket
import time
import math
from pylab import *

# My library
# from Received import *
from Motor import *
# from AnalyzePeak import *
# from Capture import *
# from File import *
# from Enc import *
from BSSconfig import *

#
class Gonio:

    def __init__(self, server):
        self.s = server
        self.goniox = Motor(self.s, "bl_32in_st2_gonio_1_x", "pulse")
        self.gonioy = Motor(self.s, "bl_32in_st2_gonio_1_y", "pulse")
        self.gonioz = Motor(self.s, "bl_32in_st2_gonio_1_z", "pulse")
        self.goniozz = Motor(self.s, "bl_32in_st2_gonio_1_zz", "pulse")
        self.phi = Motor(self.s, "bl_32in_st2_gonio_1_phi", "pulse")
        # self.enc=Enc()
        # self.enc.openPort()

        #self.convertion = 6667 # YK@230406
        #self.base = 210.0 # YK@230406
        self.sense_phi = -1 # YK@230406
        self.convertion = 5000
        self.base = 0.0

    def goMountPosition(self):
        bssconf = BSSconfig()
        mountx = bssconf.getValue("Cmount_Gonio_X")
        mounty = bssconf.getValue("Cmount_Gonio_Y")
        mountz = bssconf.getValue("Cmount_Gonio_Z")

        print mountx, mounty, mountz

        self.rotatePhi(0.0)
        self.moveXYZmm(mountx, mounty, mountz)

    def setSpeed(self):
        com = "put/bl_32in_st2_gonio_1_phi_speed/1200000pps"
        return 0

    def prepScan(self):
        ##      Preparing gonio information
        curr_gx = self.getX()[0]
        curr_gy = self.getY()[0]
        curr_gz = self.getZ()[0]
        print "Current gonio[pulse]:%5d %5d %5d\n" % (curr_gx, curr_gy, curr_gz)

        ##	Encoder reset
        self.enc.resetEnc(curr_gx, curr_gy, curr_gz)
        return True

    def getPhi(self):
        phi_pulse = self.phi.getPosition()
        # print phi_pulse
        #phi_deg = float(phi_pulse[0]) / float(self.convertion) + self.base
        phi_deg = float(self.sense_phi) * float(phi_pulse[0]) / float(self.convertion) + self.base # YK@230406

        phi_deg = round(phi_deg, 3)
        # print phi_deg
        return phi_deg

    def presetPhi(self):
        self.phi.preset(0)

    def movePint(self, value_um):
        curr_phi = self.getPhi()
        # print "PHI:%12.5f" % curr_phi
        curr_phi = math.radians(curr_phi)

        # current pulse
        curr_x = int(self.getX()[0])
        curr_z = int(self.getZ()[0])

        # unit [um]
        move_x = value_um * math.cos(curr_phi)
        move_z = value_um * math.sin(curr_phi)

        # marume [um]
        move_x = round(move_x, 5)
        move_z = round(move_z, 5)

        # marume value[pulse]
        move_x = int(move_x * 10)
        move_z = int(move_z * 10)

        # print move_x,move_z

        # final position
        final_x = curr_x + move_x
        final_z = curr_z + move_z

        # print final_x,final_z

        self.moveXZ(final_x, final_z)

    # print move_x,move_z
    # return move_x,move_z

    def moveTrans(self, trans):
        # current pulse
        curr_y = int(self.getY()[0])

        # relative movement unit [um]
        move_y = -trans

        # marume[um]
        move_y = round(move_y, 5)
        # print "round %8.4f "%(move_y)

        # [um] to [pulse]
        move_y = int(move_y * 10)

        # final position
        final_y = curr_y + move_y

        # print curr_y,final_y

        # final position
        # print "final %8d\n"%(final_y)
        self.moveY(final_y)

    def moveUpDown(self, height):
        curr_phi = self.getPhi()
        print "PHI:%12.5f" % curr_phi

        curr_phi = math.radians(curr_phi)

        # current pulse
        curr_x = int(self.getX()[0])
        curr_z = int(self.getZ()[0])
        # print curr_x,curr_z

        # unit [um]
        move_x = -height * math.sin(curr_phi)
        move_z = height * math.cos(curr_phi)

        # marume[um]
        move_x = round(move_x, 5)
        move_z = round(move_z, 5)
        # print "rount %8.4f %8.4f\n"%(move_x,move_z)

        # [um] to [pulse]
        move_x = int(move_x * 10)
        move_z = int(move_z * 10)

        # final position
        final_x = curr_x + move_x
        final_z = curr_z + move_z

        # final position
        # print "final %8d %8d\n"%(final_x,final_z)
        self.moveXZ(final_x, final_z)

    # 2020/01/21 Hyottoshite Chigaunjanai?
    # height should be defined in [um]
    def moveUpDown_obsoleted(self, height_um):
        curr_phi = self.getPhi()
        while (curr_phi > 360.0):
            curr_phi = curr_phi - 360.0

        print "PHI:%12.5f" % curr_phi
        curr_rad = math.radians(curr_phi)

        height = height_um
        if curr_phi >= 0.0 and curr_phi < 90.0:
            dz = -height * math.cos(curr_rad)
            dx = height * math.sin(curr_rad)
        elif curr_phi >= 90.0 and curr_phi < 180.0:
            dz = height * math.cos(curr_rad)
            dx = height * math.sin(curr_rad)
        elif curr_phi >= 180.0 and curr_phi < 270.0:
            dz = -height * math.cos(curr_rad)
            dx = -height * math.sin(curr_rad)
        elif curr_phi >= 270. and curr_phi <= 360.0:
            dz = height * math.cos(curr_rad)
            dx = -height * math.sin(curr_rad)

        # current pulse
        curr_x = int(self.getX()[0])
        curr_z = int(self.getZ()[0])

        # marume[um]
        move_x = -round(dx, 5)
        move_z = -round(dz, 5)
        print "Moving %8.4f um %8.4f um\n"%(move_x,move_z)

        # [um] to [pulse]
        move_x = int(move_x * 10)
        move_z = int(move_z * 10)

        # final position
        final_x = curr_x + move_x
        final_z = curr_z + move_z

        # final position
        # print "final %8d %8d\n"%(final_x,final_z)
        self.moveXZ(final_x, final_z)

    # height : height in unit of [um]
    def calcUpDown(self, height):
        curr_phi = self.getPhi()
        # print "PHI:%12.5f" % curr_phi
        curr_phi = math.radians(curr_phi)

        # unit [um]
        move_x = -height * math.sin(curr_phi)
        move_z = height * math.cos(curr_phi)

        # marume[um]
        move_x = round(move_x, 5)
        move_z = round(move_z, 5)

        # unit conv[mm]
        mm_x = move_x / 1000.0
        mm_z = move_z / 1000.0

        return mm_x, mm_z

    # height : height in unit of [um]
    # phi : current gonio phi degrees
    def calcUpDown(self, height, phi):
        phi = math.radians(phi)

        # unit [um]
        move_x = -height * math.sin(phi)
        move_z = height * math.cos(phi)

        # marume[um]
        move_x = round(move_x, 5)
        move_z = round(move_z, 5)

        # unit conv[mm]
        mm_x = move_x / 1000.0
        mm_z = move_z / 1000.0

        return mm_x, mm_z

    def rotatePhiRelative(self, relphi):
        curr_deg = self.getPhi()
        final_deg = curr_deg + relphi
        self.rotatePhi(final_deg)

    def rotatePhi(self, phi):
        self.setSpeed()
        if phi > 720.0:
            phi = phi - 720.0
        if phi < -720.0:
            phi = phi + 720.0

        #convertion = 6667  # deg2pulse # YK@230406
        convertion = 5000 # deg2pulse
        #dif = phi * convertion # YK@230406
        dif = self.sense_phi * phi * convertion

        #base = 210 # YK@230406
        base = 0

        orig = base * convertion
        pos_pulse = -(orig + -dif)

        self.phi.move(pos_pulse)

    # print pos_pulse

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
        tmp = float(self.goniox.getPosition()[0])
        # print "GETXMM:%8.3f"%tmp
        return tmp / 10.0 / 1000.0

    def getYmm(self):
        tmp = float(self.gonioy.getPosition()[0])
        return -tmp / 10.0 / 1000.0

    def getZmm(self):
        tmp = float(self.gonioz.getPosition()[0])
        return tmp / 10.0 / 1000.0

    def getZZmm(self):
        tmp = float(self.goniozz.getPosition()[0])
        return tmp * 0.25 / 1000.0

    def getZZ(self):
        tmp = int(self.goniozz.getPosition()[0])
        return tmp

    def moveZZpulse(self, value):
        self.goniozz.move(value)

    def moveZZrel(self, value):  ## value is in [um]
        move_pulse = value * 4

        # current ZZ [pulse]
        curr_zz = self.goniozz.getPosition()[0]

        # final position [pulse]
        final = curr_zz + move_pulse

        # backlush 5[um]
        if value < 0.0:
            bl_pos = final - 20
            self.goniozz.move(bl_pos)

        # move
        self.goniozz.move(final)

    def getX(self):
        return self.goniox.getPosition()

    def getY(self):
        return self.gonioy.getPosition()

    def getZ(self):
        return self.gonioz.getPosition()

    def moveZ(self, value):
        self.gonioz.move(value)

    def moveY(self, value):
        self.gonioy.move(value)

    def moveXYZ(self, movex, movey, movez):
        # UNIT: [pulse]
        self.goniox.move(movex)
        self.gonioy.move(movey)
        self.gonioz.move(movez)

    def getXYZmm(self):
        x = self.getXmm()
        y = self.getYmm()
        z = self.getZmm()

        return x, y, z

    def moveXYZmm(self, movex, movey, movez):
        # convertion
        xpulse = movex * 10000.0
        ypulse = -movey * 10000.0
        zpulse = movez * 10000.0
        # UNIT: [pulse]
        self.goniox.move(xpulse)
        self.gonioy.move(ypulse)
        self.gonioz.move(zpulse)

    def goXYZmm(self, movex, movey, movez):
        # convertion
        xpulse = movex * 10000.0
        ypulse = -movey * 10000.0
        zpulse = movez * 10000.0
        # UNIT: [pulse]
        self.goniox.nageppa(xpulse)
        self.gonioy.nageppa(ypulse)
        self.gonioz.nageppa(zpulse)

    def moveXmm(self, movex):
        # convertion
        xpulse = movex * 10000.0
        # UNIT: [pulse]
        self.goniox.move(xpulse)

    def moveYmm(self, movey):
        # convertion
        ypulse = -movey * 10000.0
        # UNIT: [pulse]
        self.gonioy.move(ypulse)

    def moveZmm(self, movez):
        # convertion
        zpulse = movez * 10000.0
        # UNIT: [pulse]
        self.gonioz.move(zpulse)

    def moveXZ(self, movex, movez):
        self.goniox.move(movex)
        self.gonioz.move(movez)

    def move(self, x, y, z):
        self.goniox.move(x)
        self.gonioy.move(y)
        self.gonioz.move(z)

    def wireRoughZ(self, ch1):
        # current position
        x, y, z = self.getXYZmm()

        # note wire default position should be left/lower compared to the X-ray center
        x1, y1, z1 = self.findZhalf(0, 500, 10, 3)

        print "Found Z=%10.5f" % z1
        print "Found X=%10.5f" % x1

        vdiff = math.sqrt(math.pow((x - x1), 2) + math.pow((y - y1), 2) + math.pow((z - z1), 2))
        print "Distance between found and initial position:%8.3f\n" % (vdiff)

        ## Next scan range
        # Rough edge of Z=z1
        # Start point: 50um before the edge
        newz = z1 - 0.05
        print "Next scan start Z=%10.5f " % newz

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
        print "hdiff:%8.3f\n" % (hdiff)

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
        print "Vdiff:%8.3f Hdiff:%8.3f\n" % (vdiff, hdiff)

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
            print x2, y2, z2, pincnt, save

            if pincnt < (save / 2.0):
                print "FIND!!: %8.5f\n" % pincnt
                isFound = True
                break

        if isFound == False:
            print "No found"
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
            print x2, y2, z2, pincnt, save

            if pincnt < (save / 2.0):
                print "FIND!!: %8.5f\n" % pincnt
                isFound = True
                break

        if isFound == False:
            print "No found"
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
            print "range trouble"
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
            print "range trouble"
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
            print "range trouble"
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
            print "range trouble"
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
            print "range trouble"
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
        print "find center"

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

    #print gonio.getXYZmm()
    #print gonio.getZZmm()
    #gonio.moveZZpulse(6032)

    # gonio.rotatePhi(120.0)
    # phirange=180.0

    # for phirange in [90.0,180.0,270.0,360.0]:
    # gonio.rotatePhi(0.0)

    # for i in range (0,5):
    # starttime=time.time()
    # gonio.rotatePhiRelative(phirange)
    # endtime=time.time()
    # diff=endtime-starttime
    # print phirange,diff,phirange/diff

    # print gonio.getEnc()
    # print gonio.getXmm()
    # gonio.move(px,py,pz)

    # gonio.scanYenc("test",-13242,-13220,0.5,0,3,0.2)
    # gonio.moveXYZmm(3.6571,-13.3491,-0.6753)
    # gonio.scanZenc("test2",-470,-450,0.5,0,3,0.2)
    ##gonio.scanEncZ("test",-900,-800,0.5,2,0,0.2)

    # print "####"
    # curr_x= gonio.getX()[0]/10000.0
    # curr_y=-gonio.getY()[0]/10000.0
    # curr_z= gonio.getZ()[0]/10000.0

    # print "final %8.4f %8.4f %8.4f\n"%(curr_x,curr_y,curr_z)

    # gonio.rotatePhi(90)
    # print gonio.getXmm()

    # value=float(raw_input())
    # gonio.movePint(value)

    # file=File("./")
    # dir=file.getAbsolutePath()

    # savex=gonio.getX()[0]
    # savey=gonio.getY()[0]
    # savez=gonio.getZ()[0]

    # print savex,savey,savez

    # index=0
    # cap=Capture()
    # for pint in arange(-10,10,1.0): # unit[um]
    # index+=1
    # print "pint=%5d\n"%pint
    # gonio.movePint(savex,savez,pint)
    # prefix="%02d"%index
    #
    # file="%s/%s.ppm"%(dir,prefix)
    # print file
    ##cap.capture(file)
    # gonio.move(savex,savey,savez,"pulse")

    # zrange=[-292,-1092,-100]
    # yrange=[13329,14129,100]
    # gonio.scan2D("TEST2",zrange,yrange,2,0.5)

    # gonio.moveUpDown(5)

    # cap.disconnect()

    # coordinates [Y,Z]
    # normal_position=[176400,-100]
    # vscan_position= [176400,-100]
    # hscan_position= [175000,-460]

    # move normal position
    # gonio.move(normal_position[0],normal_position[1],"pulse")

    # vertical scan
    # gonio.move(vscan_position[0],vscan_position[1],"pulse")
    # gonio.scanZ("gz",300,500,10,0.2,"pulse")

    # gonio.move(hscan_position[0],hscan_position[1],"pulse")
    # gonio.scanY("gy",172640,173040,10,0.2,"pulse")
    #gonio.presetPhi()

    print(gonio.getXYZmm())

    s.close()
