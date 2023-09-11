import sys,os,math,cv2,socket
import datetime
import numpy as np
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

    # puckID
    pucks = ["CPS4491"]

    for ii in range(1,10):
        for puck in pucks:
            for i in range(1, 5):
                pin = i + 1
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
                backimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/BackImages/back-1906232240.ppm"
                inocc.setBack(backimg)
                # For each sample raster.png
                raster_img = "%s-%s.png" % (puck, pin)
                raster_picpath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/%s" % raster_img
                inocc.setRasterPicture(raster_picpath)
    
                #def doAll(self, ntimes=3, skip=False, loop_size=600.0, offset_angle=0.0):
                rwidth,rheight,phi_face,gonio_info=inocc.doAll(ntimes=2,skip=False,loop_size=400.0)
                inocc.closeCapture()
        #zoo.cleaning()
