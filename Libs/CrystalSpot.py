import sys, os, math, numpy
from MyException import *
import time
import datetime
import DiffscanLog


# import scipy.spatial

class CrystalSpot:
    # 2D coordinates and score
    # cx,cy,cz : center of raster scan : unit [mm]
    def __init__(self, cx, cy, cz, phi):
        self.cenx = cx
        self.ceny = cy
        self.cenz = cz
        self.phi = phi

        self.x_list = []
        self.y_list = []
        self.imgNumList = []
        self.score_list = []
        self.check_list = []
        self.DEBUG = False

        self.score_thresh = 5
        self.score_total = 0.0

    def getDimensions(self, hbeam, vbeam):
        xa = numpy.array(self.x_list)
        ya = numpy.array(self.y_list)

        print(xa)

        # horizontal dimensions
        xmin = xa.min()
        xmax = xa.max()
        ymin = ya.min()
        ymax = ya.max()

        print(xmin, xmax, ymin, ymax)

        self.h_size = numpy.fabs(xmax - xmin) + hbeam
        self.v_size = numpy.fabs(ymax - ymin) + vbeam

        return self.h_size, self.v_size

    def setDiffscanLog(self, path):
        self.difflog = DiffscanLog.DiffscanLog(path)

    def getTotalScore(self):
        for i in numpy.arange(0, len(self.x_list)):
            s = float(self.score_list[i])
            self.score_total += s
        return self.score_total

    def printAll(self):
        for i in numpy.arange(0, len(self.x_list)):
            x = self.x_list[i]
            y = self.y_list[i]
            s = float(self.score_list[i])
            imgnum = self.imgNumList[i]
            print("%8.4f %8.4f %5.2f %5d" % (x, y, s, imgnum))

    def getXYlist(self):
        return self.x_list, self.y_list

    def getInfo(self):
        return self.x_list, self.y_list, self.score_list, self.imgNumList

    def getSize(self):
        return len(self.x_list)

    def check(self, x1, y1):
        for i in numpy.arange(0, len(self.x_list)):
            x = self.x_list[i]
            y = self.y_list[i]
            if self.DEBUG: print("CrystalSpot.check", x, y, x1, y1, self.check_list[i])
            if x == x1 and y == y1:
                if self.DEBUG: print("CrystalSpot.check True=", x1, y1)
                self.check_list[i] = True
                if self.DEBUG: print("Atta!")
                return 1

        print("something wrong")
        sys.exit(1)

    def addXY(self, x, y, score, imgnum, isCheck=True):
        self.x_list.append(x)
        self.y_list.append(y)
        self.imgNumList.append(imgnum)
        self.score_list.append(score)
        self.check_list.append(isCheck)
        return len(self.x_list)

    def getUnchecked(self):
        uncheck_list = []
        for i in numpy.arange(0, len(self.check_list)):
            if (self.check_list[i] == False):
                compo = self.x_list[i], self.y_list[i], self.score_list[i]
                # print "UNUNUNUN",compo
                uncheck_list.append(compo)

        if self.DEBUG: print(uncheck_list)
        return uncheck_list

    def getPeakCode(self, score_thresh=10):
        self.score_thresh = score_thresh
        score_max = -9999.9999
        max_x = 0.0000
        max_y = 0.0000

        for i in numpy.arange(0, len(self.x_list)):
            x = self.x_list[i]
            y = self.y_list[i]
            score = self.score_list[i]
            imgnum = self.imgNumList[i]

            if score > score_max:
                score_max = score
                max_x = x
                max_y = y
                max_i = imgnum

        gxyz = self.getXYZ(max_i)
        return gxyz

    # return goniometer coordinate
    # coded on 2016/07/26
    def getGrav(self, score_thresh=5):
        self.score_thresh = score_thresh
        score_max = -9999.9999
        max_x = 0.0000
        max_y = 0.0000

        sum_xscore = 0.0
        sum_yscore = 0.0
        sum_zscore = 0.0
        sum_score = 0.0

        for i in numpy.arange(0, len(self.imgNumList)):
            # GXYZ
            imgnum = self.imgNumList[i]
            gx, gy, gz = self.getXYZ(imgnum)
            # SCORE
            score = self.score_list[i]
            # For gravity calculation
            sum_xscore += score * gx
            sum_yscore += score * gy
            sum_zscore += score * gz
            sum_score += score

        gv_x = sum_xscore / sum_score
        gv_y = sum_yscore / sum_score
        gv_z = sum_zscore / sum_score

        print(gv_x, gv_y, gv_z)
        self.gv_xyz = gv_x, gv_y, gv_z

        return self.gv_xyz

    def findHoriEdges(self):
        score_max = -9999.9999
        max_x = -9999.9999
        min_x = 9999.9999
        max_y = -9999.9999
        min_y = 9999.9999

        for i in numpy.arange(0, len(self.x_list)):
            x = self.x_list[i]
            y = self.y_list[i]
            imgnum = self.imgNumList[i]
            if x > max_x:
                max_x = x
                max_y = y
                max_i = imgnum
            if x < min_x:
                min_x = x
                min_y = y
                min_i = imgnum

        # Convert 2D relative coordinate -> 3D GXYZ coordinate
        gxyz = self.difflog.getXYZindex(imgnum)

        # Right edge
        rxyz = self.difflog.getXYZindex(max_i)
        # Left edge
        lxyz = self.difflog.getXYZindex(min_i)

        # print "Crystal edges(L,R))=(%8.3f,%8.3f,%8.3f)-(%8.3f,%8.3f",lxyz,rxyz

        return lxyz, rxyz

    # rx,ry,rz : relative coordinates
    def calcXYZ_obsoleted(self, rx, ry):
        # Convertion unit [mm]
        d_hori = rx
        d_vert = ry
        print("Relative=", d_hori, d_vert, self.phi)

        # Convertion to GXYZ
        dx, dz = self.calcVlenAtPhi(d_vert, self.phi)

        # Each coordinate
        # For BL32XU settings
        x = self.cenx + dx
        y = self.ceny - d_hori
        z = self.cenz + dz

        gxyz = x, y, z

        return gxyz

    def getXYZ(self, imgnum):
        gxyz = self.difflog.getXYZindex(imgnum)

        return gxyz

    def calcVlenAtPhi(self, vlen, phi):
        phi_rad = math.radians(phi)

        # For BL32XU settings
        # unit [mm]
        move_x = vlen * math.sin(phi_rad)
        move_z = -vlen * math.cos(phi_rad)

        # marume[mm]
        move_x = round(move_x, 5)
        move_z = round(move_z, 5)

        return move_x, move_z

    def isThere(self, x, y):
        for rx, ry in zip(self.x_list, self.y_list):
            if x == rx and y == ry:
                return True
        return False
