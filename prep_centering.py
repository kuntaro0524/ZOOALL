import sys,os,math,socket
import datetime
<<<<<<< HEAD
import BLFactory

if __name__ == "__main__":
    blf = BLFactory.BLFactory()
    blf.initDevice()
    blf.device.prepCentering(zoom_out=False)
=======
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
>>>>>>> zoo45xu/main
