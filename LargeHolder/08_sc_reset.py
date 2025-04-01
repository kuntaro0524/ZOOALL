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

    # renaming for this modification
    rename="exp2500"

    # Dismount
    zoo.dismountCurrentPin()
    zoo.waitTillReady()

    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"

    # Side camera background
    dev.prepCenteringSideCamera()
    inocc.getImage("side","%s/scbg4_%s.png"%(backpath,rename),binning=4,sc_exptime=2500)

    # Mount pin
    try:
        zoo.mountSample("CPS1024",3)
        zoo.waitTillReady()
    except MyException, ttt:
        print "Sample mounting failed. Contact BL staff!"
        sys.exit(1)

    # preparation
    dev.prepCenteringBackCamera()

    while(1):
        max_similarity=inocc.captureMatchBackcam()
        if max_similarity > 0.70:
            break
