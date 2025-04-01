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

    # Basic information
    # ROI center for ideal position 
    x0=254
    y0=274
    
    trans_resol=0.006727
    vert_resol=0.0092727

    ###
    inocc=IboINOCC.IboINOCC(dev.gonio)
    lpmbc=LargePlateMatchingBC.LargePlateMatchingBC()

    # preparation
    dev.prepCenteringBackCamera()
    initial_phi=dev.gonio.getPhi()

    img_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"
    
    # Save position
    sx,sy,sz=dev.gonio.getXYZmm()

    imgname="%s/bctest.png"%(img_path)
    inocc.getImage("back",imgname,binning=2)
    max_loc=lpmbc.getHoriVer(imgname)
    x,y=max_loc

    # diff
    diffx=x-x0
    diffy=y-y0

    # movement
    trans_um=diffx/trans_resol
    vert_um=diffy/vert_resol

    print "TRANS=",diffx,trans_um
    print "VERT =",diffy,vert_um

    if np.fabs(trans_um) < 2000.0:
        dev.gonio.moveTrans(trans_um)
    if np.fabs(vert_um) < 2000.0:
        dev.gonio.moveUpDown(vert_um)

    #time.sleep(10.0)

    #dev.gonio.moveXYZmm(sx,sy,sz)
