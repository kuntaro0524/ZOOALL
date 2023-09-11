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

    root_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TestImages2/"
    bfile = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_201002.ppm"

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
        for j in range(0,5):
            filename = "%s/stop5_%f_%02d.ppm"%(root_dir, d_hori_mm,j)
            logdir = "%s/%04d/" % (root_dir, i)
            dev.capture.capture(filename)
