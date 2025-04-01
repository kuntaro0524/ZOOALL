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

    inocc=IboINOCC.IboINOCC(dev.gonio)

    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"

    #dev.prepCenteringSideCamera()

    inocc.getImage("side",sys.argv[1],binning=4,sc_exptime=2500)
    angle,score,ymean=inocc.tune_phi(sys.argv[1])
    print "ANGLE,Score=",angle,score
