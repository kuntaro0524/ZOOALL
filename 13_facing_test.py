import cv2,sys,datetime, socket, time
import matplotlib.pyplot as plt
import numpy as np
import copy

sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")

from MyException import *
import CryImageProc
import Device
import FittingForFacing

if __name__=="__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    dev = Device.Device(ms)
    dev.init()
    
    roi_len_um = 600.0
    phis = []
    areas = []
    idx = 0

    for phi in [0, 45, 90, 135]:
        dev.gonio.rotatePhi(phi)
        testimage = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/%03d_%05.2fdeg.ppm"% (idx,phi)
        dev.capture.capture(testimage)
        cip = CryImageProc.CryImageProc()
        cip.setImages(testimage,"back_180517-10000-54000.ppm")
        time.sleep(0.1)

        prefix = "tttt"
        cont = cip.getContour()

        #top_xy = cip.find_top_x(cont)
        #roi_xy = cip.selectHoriROI(cont, top_xy, 300)

        top_xy = cip.find_top_x(cont)
        roi_xy = cip.selectHoriROI(cont, top_xy, roi_len_um)

        outimage = "%03d_topcontour.png" % idx
        cip.drawContourOnTarget(roi_xy, outimage)

        outimage = "%03d_minbox.png" % idx
        cip.getMinArea(loop_size = roi_len_um, filepath = outimage)

        area = cip.getArea(loop_size = roi_len_um)

        phis.append(phi)
        areas.append(area)

        print "Area = %5.2f"% area
        idx += 1

phis.append(180)
phis.append(phis[0])
ffff = FittingForFacing.FittingForFacing(phis, areas)
#ffff.prep()
face_angle = ffff.findFaceAngle()

yoko = face_angle - 90.0

dev.gonio.rotatePhi(yoko)
