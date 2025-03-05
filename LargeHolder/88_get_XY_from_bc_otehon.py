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

    print "OTEHON XY = ",x,y
