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

    inocc=IboINOCC.IboINOCC(dev.gonio)

    # preparation
    dev.prepCenteringBackCamera()

    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"
    dev.prepCenteringSideCamera()

    # Side camera background
    face_phi=dev.gonio.getPhi()
    if face_phi < 0.0:
        face_phi+=360.0

    target_image="%s/sc_curr.png"%backpath
    sx,sy,sz=dev.gonio.getXYZmm()

    ntimes=10
    step=50.0 #[um]
    whole_width=ntimes*step

    initial_move=-whole_width/2.0
    dev.gonio.movePint(initial_move)
    
    for i in range(0,ntimes,1):
        dev.gonio.movePint(step)
        inocc.getImage("side",target_image,binning=4,sc_exptime=2500)
        angle,score,ymean=inocc.tune_phi(target_image)
        x,y,z=dev.gonio.getXYZmm()
        print "LOG=",i,ymean,x,y,z

    dev.gonio.moveXYZmm(sx,sy,sz)
    #dev.gonio.rotatePhiRelative(5.0)
