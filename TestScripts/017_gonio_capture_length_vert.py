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

    root_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TestImages2/"
    bfile = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/BackImages/back_210120.ppm"

    inocc = INOCC.INOCC(ms, root_dir)

    loop_size = 600.0
    option = "top"

    outfile = open("gonio_v.dat", "w")

    x,y,z = dev.gonio.getXYZmm()

    print(x,y,z)
    y_init = y

    sum_dist = 0.0
    for i in range(0,20):
        d_height_um = 20.0
        sum_dist += d_height_um
        print("moving up %8.3f" % d_height_um)
        dev.gonio.moveUpDown(d_height_um)
        
        filename = "%s/cap_%f.ppm"%(root_dir, d_height_um)
        logdir = "%s/%04d/" % (root_dir, i)

        print(filename)
        dev.capture.capture(filename)
        cip = CryImageProc.CryImageProc(logdir = root_dir)
        cip.setImages(filename, bfile)
        cont = cip.getContour()
        top_xy = cip.find_top_x(cont)
        topimage = "%s/top_%f.png"%(root_dir, sum_dist)
        cip.drawTopOnTarget(top_xy,topimage)
        outfile.write("%s height,X,Y = %8.3f %5.1f %5.1f\n" % (filename, sum_dist, top_xy[0], top_xy[1]))
