import sys,os,math,socket
import datetime
import numpy as np
from MyException import *

from File import *
import Capture
import Device

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))

    dev = Device.Device(ms)
    dev.init()
    dev.prepCentering()

    bright=[5000,10000,20000,30000,40000,50000]
    gain=[500,1000,1500,2000]

    cap = Capture.Capture()
    cap.prep()
    cappath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TestImages/"

    # prefix should be 'back' or 'loop'
    prefix = "back"

    for br in bright:
        for ga in gain:
            filename="%s/%s_%d-%d.ppm"%(cappath,prefix,br,ga)
            print("Captureing..",filename)
            cap.setBright(br)
            cap.setGain(ga)
            cap.capture(filename)
