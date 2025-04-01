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
    zoo.dismountCurrentPin()
    zoo.waitTillReady()

    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"

    # Capture background (backcamera)
    dev.prepCenteringBackCamera()
    inocc.getImage("back","%s/bcbg.png"%backpath,binning=2)

    dev.prepCenteringSideCamera()
    # Side camera background
    inocc.getImage("side","%s/scbg4.png"%backpath,binning=4,sc_exptime=2000)

    # Naname camera background
