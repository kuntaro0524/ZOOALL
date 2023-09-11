import sys,os,math,cv2,socket
import datetime
import numpy as np
from MyException import * 
import CryImageProc 
import CoaxImage
import BSSconfig

from File import *

import matplotlib
import matplotlib.pyplot as plt
import INOCC

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))
    root_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Test/"
    inocc=INOCC.INOCC(ms, root_dir)
    phi_face=90

    start_time=datetime.datetime.now()
    backimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/BackImages/back-1905182237.ppm"
    backimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo//back_190518.ppm"
    inocc.setBack(backimg)
    # For each sample raster.png
    raster_picpath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/raster.png"
    inocc.setRasterPicture(raster_picpath)

    phi = inocc.fitAndFace_till190514()

    ms.close()
