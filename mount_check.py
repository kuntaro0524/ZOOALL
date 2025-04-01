import sys,os,math,cv2,socket
import datetime
import numpy as np
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
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
    ms.connect(("172.24.242.59", 10101))

    # puckID
    #pucks = ["385","734","785","1089","1091","737","1092","1093"]
    pucks = ["23", "17", "25", "20", "19", "21", "24", "13"]

    for puck in pucks:
        for i in range(0, 16):
            pin = i + 1
            try:
                zoo.mountSample(puck, pin)
            except MyException,ttt:
                print "Sample mount failed!!"
                zoo.skipSample()
                continue
