import sys,os,math,cv2,socket
import datetime
import numpy as np
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

from File import *
import Capture
import Device
import Date

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    dev = Device.Device(ms)
    dev.init()
    dev.prepCentering()

    cap = Capture.Capture()
    cap.prep()
    cappath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Elongate/"

    dt = Date.Date()

    # prefix should be 'back' or 'loop'
    pprefix = "CPS0734-09"

    while(1):
        dtstr = dt.getNowMyFormat(option="sec")
        prefix = "%s_%s" % (pprefix,dtstr)
        filename="%s/%s.ppm"%(cappath,prefix)
        print "Captureing..",filename
        cap.capture(filename)
        time.sleep(10.0)
