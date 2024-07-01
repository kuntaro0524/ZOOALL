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

    #bright=[500,1000,1500,2500,5000,10000,20000,30000,40000,50000]
    #contrast=[5000, 9000,18000,27000,36000,45000,54000]

    bright=[2500]
    contrast=[30000,32000,34000,36000,38000,40000]

    cap = Capture.Capture()
    cap.prep()
    cappath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/TestImages2/"

    # prefix should be 'back' or 'loop'
    prefix = "nilon3"

    for br in bright:
        for cn in contrast:
            filename="%s/%s_180517-%d-%d.ppm"%(cappath,prefix,br,cn)
            cap.setBright(br)
            cap.setContrast(cn)
            cap.capture(filename)
