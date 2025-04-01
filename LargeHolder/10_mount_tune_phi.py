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
        zoo.mountSample("CPS0296",5)
        zoo.waitTillReady()
    except MyException, ttt:
        print "Sample mounting failed. Contact BL staff!"
        sys.exit(1)

    inocc=IboINOCC.IboINOCC(dev.gonio)

    # preparation
    dev.prepCenteringBackCamera()

    while(1):
        max_similarity=inocc.captureMatchBackcam()
        if max_similarity > 0.60:
            break

    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"
    dev.prepCenteringSideCamera()

    # Side camera background
    face_phi=dev.gonio.getPhi()
    if face_phi < 0.0:
        face_phi+=360.0

    target_image="%s/sc_curr.png"%backpath

    ifail=0
    while(1):
        inocc.getImage("side",target_image,binning=4,sc_exptime=2500)
        angle,score,ymean=inocc.tune_phi(target_image)
        print angle,score,ymean
        if score > 100.0:
            continue
        elif np.fabs(angle) < 45.0 and np.fabs(angle) > 1.0:
            dev.gonio.rotatePhiRelative(-angle)
            ifail=0
        else:
            break
        if ifail > 10:
            dev.gonio.rotatePhiRelative(180.0)
            ifail=0

    dev.gonio.rotatePhiRelative(-5.0)
