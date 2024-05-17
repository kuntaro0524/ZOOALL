import sys, os, math, cv2, socket
import datetime
import numpy as np

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import CryImageProc
import CoaxImage
import BSSconfig
import DirectoryProc
import FittingForFacing

from File import *

import matplotlib
import matplotlib.pyplot as plt

import INOCC
import Device

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))
    root_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Test/"
    inocc = INOCC.INOCC(ms, root_dir)
    phi_face = 90

    # Device
    dev = Device.Device(ms)
    dev.init()

    dev.prepCentering()

    start_time = datetime.datetime.now()
    backimg = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_190529.ppm"
    inocc.setBack(backimg)
    # For each sample raster.png
    raster_picpath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/raster.png"
    inocc.setRasterPicture(raster_picpath)

    # def doAll(self, ntimes=3, skip=False, loop_size=600.0, offset_angle=0.0):
    rwidth, rheight, phi_face, gonio_info = inocc.doAll(ntimes=2, skip=False, loop_size=400.0)

    ms.close()
