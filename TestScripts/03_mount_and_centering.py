import sys,os,math,cv2,socket
import datetime
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

from File import *
import Zoo
import Device
import INOCC

if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    # MS server
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))

    # Device
    dev = Device.Device(ms)
    dev.init()

    # Background image
    dev.prepCentering()
    backimg = os.path.join(os.path.abspath("./"), "back.ppm")
    dev.capture.capture(backimg)

    import os, sys, glob
    import time
    import numpy as np
    import socket

    sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
    from MyException import *
    import MXserver
    import Zoo
    import Date
    import logging

    # Trying pucks
    puckpin_list = [("YHuangLab005", 4), ("lin006", 6), ("Hattori010", 13)]

    num = 0
    for puck, pin in puckpin_list:
        try:
            zoo.mountSample(puck, pin)
        except MyException as ttt:
            print("Sample mount failed!!")
            zoo.skipSample()
            continue

        dev.prepCentering()
        root_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Test/"
        sample_name = "%s-%02d" % (puck, pin)
        inocc=INOCC.INOCC(ms, root_dir, sample_name = sample_name)

        start_time=datetime.datetime.now()
        inocc.setBack(backimg)

        # For each sample raster.png
        raster_img = "%s-%s.png" % (puck, pin)
        raster_picpath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/%s" % raster_img
        inocc.setRasterPicture(raster_picpath)

        rwidth,rheight,phi_face,gonio_info=inocc.doAll(ntimes=2,skip=False,loop_size=400.0)
        inocc.closeCapture()