import sys,os,math,cv2,socket
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

    #bright=[500,1000,2000,2500,3000,3500,4000,4500,5000]
    #gain=[500,1000,1500,2000]
    #bright=[1000,2000,2500,3000,3500,4000,4500,5000]
    #gain=[1000,1500,2000,2500]
    bright=[4000,4100,4200,4300,4400,4500]
    gain=[1000,1100,1200,1300,1400,1500]
    #bright=[1600,1700,1800,1900,2000,2100,2200,2300,2400,2500]
    #bright=[3000,3100,3200,3300,3400,3500,3600,3700,3800,3900,4000]
    #gain=[500,600,700,800,900,1000,1100,1200,1300,1400,1500]
    #bright=[3500,3600,3700,3800,3900,4000,4100,4200,4300,4400,4500]
    #gain=[1000,1100,1200,1300,1400,1500,1600,1700,1800,1900]
    #bright=[1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000]
    #gain=[1400,1500,1600,1700,1800,1900,2000]

    cap = Capture.Capture()
    cap.prep()
    #cappath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TestImages210302/"
    cappath = "/isilon/users/target/target/Staff/2021A/210302/INOCC/TestImage-4700-center/"

    # prefix should be 'back' or 'loop'
    prefix = "back"

    for br in bright:
        for ga in gain:
            filename="%s/%s_%d-%d.ppm"%(cappath,prefix,br,ga)
            print("Captureing..",filename)
            time.sleep(1)
            cap.setBright(br)
            time.sleep(1)
            cap.setGain(ga)
            time.sleep(1)
            cap.capture(filename)
