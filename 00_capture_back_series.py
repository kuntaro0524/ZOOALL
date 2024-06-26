import sys,os,math,cv2,socket
import datetime
import numpy as np
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

from File import *
import Capture
import Device

import time

if __name__ == "__main__":
    #ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #ms.connect(("172.24.242.54", 10101))

    #dev = Device.Device(ms)
    #dev.init()
    #dev.prepCentering()

    #bright=[1500,2500,5000,10000,20000,30000,40000,50000]
    #contrast=[5000, 9000,18000,27000,36000,45000,54000]
    #bright=[500,1000,1500,2500,5000,10000,20000,30000,40000,50000]
    #contrast=[5000, 9000,18000,27000,36000,45000,54000]
    bright=[14000, 14200, 14400, 14600, 14800, 15000, 15200, 15400, 15600, 15800, 16000]
    #contrast=[30000,32000,34000,36000,38000,40000]
    contrast=[18000]
    gain = [900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]

    cap = Capture.Capture()
    cap.prep()
    cappath = "/staff/bl41xu/TestImg_231010/"

    # prefix should be 'back' or 'loop'
    prefix = "loop"

    for br in bright:
        # for cn in contrast:
        for gn in gain:
            filename="%s/%s_180517-%d-%d.ppm"%(cappath, prefix, br, gn)
            print "Captureing..", filename
            cap.setBright(br)
            # cap.setContrast(cn)
            cap.setGain(gn)
            time.sleep(1.0)
            cap.capture(filename)
