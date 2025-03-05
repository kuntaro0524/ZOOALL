import socket,os,sys,datetime,cv2,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Device
import IboINOCC
import Zoo
import MyException
import time
import numpy as np
import LargePlateMatchingBC

if __name__ == "__main__":
    import Gonio
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))
    
    dev=Device.Device(s)
    dev.init()

    ###
    inocc=IboINOCC.IboINOCC(dev.gonio)
    lpmbc=LargePlateMatchingBC.LargePlateMatchingBC()

    # preparation
    dev.prepCenteringBackCamera()
    initial_phi=dev.gonio.getPhi()

    img_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"
    
    y_step=200.0 #[um]
    n_times=10

    # Save position
    sx,sy,sz=dev.gonio.getXYZmm()

    imgname="%s/bctest.png"%(img_path)
    for i in range(0,n_times):
        dev.gonio.moveTrans(y_step)
        inocc.getImage("back",imgname,binning=2)
        max_loc=lpmbc.getHoriVer(imgname)
        x,y=max_loc
        print i*y_step,x,y

    dev.gonio.moveXYZmm(sx,sy,sz)

    # Vertical direction
    z_step=200.0
    imgname="%s/bctest.png"%(img_path)
    for i in range(0,n_times):
        dev.gonio.moveUpDown(z_step)
        inocc.getImage("back",imgname,binning=2)
        max_loc=lpmbc.getHoriVer(imgname)
        x,y=max_loc
        print i*z_step,x,y

    dev.gonio.moveXYZmm(sx,sy,sz)
