import socket,os,sys,datetime,cv2,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Device
import IboINOCC
import Zoo
import MyException
import time
import numpy as np

if __name__ == "__main__":
    import Gonio
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    dev=Device.Device(s)
    dev.init()

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    try:
        #zoo.mountSample("CPS1754",2)
        zoo.mountSample("CPS1024",10)
        zoo.waitTillReady()
    except MyException, ttt:
        print "Sample mounting failed. Contact BL staff!"
        sys.exit(1)

    inocc=IboINOCC.IboINOCC(dev)

    inocc.fit_side()
    inocc.fit_tateyoko()
    inocc.fit_pint_direction()
    inocc.fit_tateyoko()
