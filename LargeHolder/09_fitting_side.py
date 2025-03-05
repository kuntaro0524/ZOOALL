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

    target_image="%s/sc_curr.png"%backpath

    while(1):
        inocc.getImage("side",target_image,binning=4,sc_exptime=2500)
        angle,score,ymean=inocc.tune_phi(target_image)
        print "ANGLE,Score=",angle,score
        if np.fabs(angle) < 45.0 and np.fabs(angle) > 1.0:
            dev.gonio.rotatePhiRelative(-angle)
        else:
            break

    dev.gonio.rotatePhiRelative(5.0)
    #print angle
