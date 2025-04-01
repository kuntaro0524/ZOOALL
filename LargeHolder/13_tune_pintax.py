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

    ycenter=289
    pix_resol=0.0319

    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"

    inocc=IboINOCC.IboINOCC(dev.gonio)
    target_image="%s/sc.png"%backpath

    while(1):
        inocc.getImage("side",target_image,binning=4)
        angle,score,ymean=inocc.tune_phi(target_image)
    
        print "LOG=",ymean
        diff_y=ymean-ycenter
        move_um=diff_y/pix_resol

        print "Dpix(y)=",diff_y
        print "Dpint[um]=",move_um

        if score > 100.0:
            continue

        if np.fabs(move_um) < 3.0:
            break
    
        elif np.fabs(move_um) < 1000.0:
            dev.gonio.movePint(move_um)
