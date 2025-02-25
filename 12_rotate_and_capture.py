import sys,os,math,socket
import datetime
import numpy as np
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

from File import *
import Capture
import Device

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    dev = Device.Device(ms)
    dev.init()
    dev.prepCentering()

    cap = Capture.Capture()
    cap.prep()
    cappath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/TestImages3/"

    for phi in [0,30,60,90,120,150,180]:
        dev.gonio.rotatePhi(phi)
        prefix = "phi%05.2f" % phi
        filename="%s/%s.ppm"%(cappath,prefix)
        print filename
        cap.capture(filename)
