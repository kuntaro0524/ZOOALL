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

    dev.prepCenteringSideCamera()
    # Side camera background
    face_phi=dev.gonio.getPhi()
    if face_phi < 0.0:
        face_phi+=360.0
    for phi in [-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30]:
        abs_phi=face_phi+phi
        dev.gonio.rotatePhi(abs_phi)
        inocc.getImage("side","%s/sc_test_%05d.png"%(backpath,phi),binning=4,sc_exptime=2500)
