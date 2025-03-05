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
    x0=251
    y0=275
    
    trans_resol=0.006727
    vert_resol=0.0092727

    ###
    inocc=IboINOCC.IboINOCC(dev)

    inocc.fit_side()
    inocc.fit_tateyoko()
    inocc.fit_side()
    inocc.fit_tateyoko()
