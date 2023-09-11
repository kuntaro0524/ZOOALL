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
import Gonio

if __name__=="__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))

    root_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TestImages3/"
    bfile = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/zoom_back.ppm"

    loop_size = 600.0
    option = "gravity"

    outfile = open("gonio.dat", "w")

    dev = Device.Device(ms)
    dev.init()

    s=0
    gonio = Gonio.Gonio(ms)
    x,y,z = gonio.getXYZmm()
    print(("current_xyz=",x,y,z))

    y_init = y

    step_h = 20.0 # um

    for i in range(0,20):
        d_hori_mm = i * step_h / 1000.0
        y_mod = y_init + d_hori_mm

        d_hori_um = d_hori_mm * 1000.0

        gonio.moveXYZmm(x, y_mod, z)

        time.sleep(1.0)
        filename = "%s/cap_%f.ppm"%(root_dir, d_hori_mm)
        logdir = "%s/%04d/" % (root_dir, i)

        dev.capture.capture(filename)
        cip = CryImageProc.CryImageProc(logdir = root_dir)
        cip.setImages(filename, bfile)
        cont = cip.getContour()
        xtarget, ytarget, area, hamidashi_flag = cip.getCenterInfo(loop_size = loop_size, option = "top")
        outimg = "top_%f.png" % d_hori_mm
        outimg_abs = os.path.join(root_dir, outimg)
        cip.drawTopOnTarget((xtarget, ytarget), outimg_abs)

        outfile.write("%s %6.3f TARGET X,Y = %5.1f %5.1f\n" % (filename, d_hori_um, xtarget, ytarget))
