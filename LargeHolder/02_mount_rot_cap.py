import os,sys,glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
import time
import numpy as np
import socket
import Zoo
import Device
import IboINOCC


if __name__ == "__main__":
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    dev=Device.Device(s)
    dev.init()

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    inocc=IboINOCC.IboINOCC(dev.gonio)

    # Dismount
    try:
        zoo.mountSample("CPS0863",1)
        zoo.waitTillReady()
    except MyException, ttt:
        print "Sample mounting failed. Contact BL staff!"
        sys.exit(1)

    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"

    # Capture background (backcamera)
    dev.prepCenteringBackCamera()
    for phi in [0,45,90,135,180]:
        dev.gonio.rotatePhi(phi)
        inocc.getImage("back","%s/bc_%05d.png"%(backpath,phi),binning=2)

    dev.prepCenteringSideCamera()
    # Side camera background
    for phi in [0,45,90,135,180]:
        dev.gonio.rotatePhi(phi)
        inocc.getImage("side","%s/sc_%05d.png"%(backpath,phi),binning=4)
