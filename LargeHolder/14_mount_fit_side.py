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
        zoo.mountSample("CPS1024",9)
        zoo.waitTillReady()
    except MyException, ttt:
        print "Sample mounting failed. Contact BL staff!"
        sys.exit(1)

    inocc=IboINOCC.IboINOCC(dev.gonio)

    # preparation
    dev.prepCenteringBackCamera()

    # Rough facing 
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

    target_image="%s/sc.png"%backpath

    # Precise facing
    ifail=0
    while(1):
        inocc.getImage("side",target_image,binning=4,sc_exptime=2500)
        angle,score,ymean=inocc.tune_phi(target_image)
        print angle,score,ymean
        if score > 100.0:
            dev.gonio.rotatePhiRelative(180.0)
            ifail+=1
            continue
        elif np.fabs(angle) < 45.0 and np.fabs(angle) > 1.0:
            dev.gonio.rotatePhiRelative(-angle)
            ifail+=1
        else:
            break
        if ifail > 10:
            dev.gonio.rotatePhiRelative(180.0)
            ifail=0

    dev.gonio.rotatePhiRelative(-5.0)

    ycenter=289
    pix_resol=0.0319

    inocc=IboINOCC.IboINOCC(dev.gonio)

    ifail=0
    while(1):
        inocc.getImage("side",target_image,binning=4)
        angle,score,ymean=inocc.tune_phi(target_image)

        if score > 50.0:
            dev.gonio.rotatePhiRelative(180.0)
            ifail+=1
    
        print "LOG=",ymean
        diff_y=ymean-ycenter
        move_um=diff_y/pix_resol

        print "Dpix(y)=",diff_y
        print "Dpint[um]=",move_um

        if np.fabs(move_um) < 3.0:
            break
    
        elif np.fabs(move_um) < 1000.0:
            dev.gonio.movePint(move_um)
            ifail+=1

        if ifail>5:
            dev.gonio.rotatePhiRelative(180.0)
