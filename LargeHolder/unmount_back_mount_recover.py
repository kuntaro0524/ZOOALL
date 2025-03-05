import os,sys,glob
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

    # Capture background
    dev.prepCenteringLargeHolderCam2()
    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"
    #inocc.getImage("side","%s/side_bin4_bg.png"%backpath,binning=4)
    #inocc.getImage("side","%s/side_bin2_bg.png"%backpath,binning=2)
    #inocc.getImage("naname","%s/naname_bg.png"%backpath,binning=2)
    #inocc.getImage("back","%s/bc_bg_bin1.png"%backpath,binning=1)

    # Mount and recover
    zoo.mountSample("CPS0293","3")
    zoo.waitTillReady()
    zoo.disconnect()

    while(1):
        #max_similarity=inocc.captureNanamecamMatching()
        max_similarity=inocc.captureBackcamMatchingBin1()
        if max_similarity > 0.90:
            break

    #inocc.getImage("side","%s/side_bin4_bg.png"%backpath,binning=4)
    #inocc.getImage("side","%s/side_bin2_bg.png"%backpath,binning=2)
