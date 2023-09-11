import cv2,sys, time, os, socket
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Device
import CryImageProc
import Capture
import DirectoryProc
import INOCC

if __name__=="__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))

    dev = Device.Device(ms)
    dev.init()

    root_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TestImages/"
    bfile = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/BackImages/back_210120.ppm"

    inocc = INOCC.INOCC(ms, root_dir)

    loop_size = 600.0
    #option = "gravity"
    option = "top"

    outfile = open("gonio.dat", "w")

    x,y,z = dev.gonio.getXYZmm()

    print(x,y,z)
    y_init = y
    
    sum_dist = 0.0 # um
    for i in range(0,20):
        d_hori_mm = i * 0.01
        sum_dist += 10 # um
        y_mod = y_init + d_hori_mm

        dev.gonio.moveXYZmm(x, y_mod, z)
        
        filename = "%s/cap_%f.ppm"%(root_dir, d_hori_mm)
        logdir = "%s/%04d/" % (root_dir, i)

        print(filename)
        dev.capture.capture(filename)
        cip = CryImageProc.CryImageProc(logdir = root_dir)
        cip.setImages(filename, bfile)
        cont = cip.getContour()
        top_xy = cip.find_top_x(cont)
        topimage = "%s/top_%f.png" % (root_dir, sum_dist)
        cip.drawTopOnTarget(top_xy, topimage)
        #xtarget, ytarget, area, hamidashi_flag = cip.getCenterInfo(loop_size = loop_size, option = option)
        #outfile.write("%s TARGET X,Y = %5.1f %5.1f\n" % (filename, xtarget, ytarget))
        outfile.write("%s TARGET X,Y = %5.1f %5.1f\n" % (filename, top_xy[0], top_xy[1]))
