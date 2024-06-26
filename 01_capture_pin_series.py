import sys,os,math,socket
import datetime
import numpy as np
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

from File import *
import Capture
import Device

if __name__ == "__main__":
    cap = Capture.Capture()
    cap.prep()
    cap.setBright(15000)
    cap.setGain(1500)
