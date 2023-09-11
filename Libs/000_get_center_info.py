import cv2,sys,datetime, socket
import matplotlib.pyplot as plt
import numpy as np
import copy
from MyException import *
import CryImageProc
import Device

if __name__=="__main__":

    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    dev=Device.Device(s)
    dev.init()
    dev.capture.prep()
    dev.capture.unsetCross()
    
    for phi in [0,30,60,90,120,150,180,210]:
        dev.gonio.rotatePhi(phi)
        # set Target/Back images
        picpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/cap.ppm"
        dev.capture.capture(picpath)
        backimage = "/isilon/users/target/target/PPPP/10.Zoo//back_190518.ppm"
        cip = CryImageProc.CryImageProc()
        cip.setImages(picpath, backimage)
        print(cip.getCenterInfo())
