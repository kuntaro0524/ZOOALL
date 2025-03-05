import socket,os,sys,datetime,cv2,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Device
import IboINOCC
import Zoo
import MyException
import time
import numpy as np
import LargePlateMatchingBC

lpmbc=LargePlateMatchingBC.LargePlateMatchingBC()
lpmbc.getHoriVer(sys.argv[1])
