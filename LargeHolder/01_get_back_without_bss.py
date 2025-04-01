import os,sys,glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
import time
import numpy as np
import socket
import Zoo
import Device
import Date
import IboINOCC

if __name__ == "__main__":
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    dev=Device.Device(s)
    dev.init()

    dtdt = Date.Date()
    dtstr = dtdt.getNowMyFormat(option="min")

    inocc=IboINOCC.IboINOCC(dev.gonio)

    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/"

    # Capture background (backcamera)
    dev.prepCenteringBackCamera()
    inocc.getImage("back","%s/bcbg_%s.png"%(backpath,dtstr),binning=2)

    dev.prepCenteringSideCamera()
    # Side camera background
    inocc.getImage("side","%s/scbg4_%s.png"%(backpath,dtstr),binning=4)
    inocc.getImage("side","%s/scbg2_%s.png"%(backpath,dtstr),binning=2)
