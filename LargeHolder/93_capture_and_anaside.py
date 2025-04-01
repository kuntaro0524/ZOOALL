import os,sys,glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
import time
import numpy as np
import socket
import Zoo
import Device
import IboINOCC
import MyDate

if __name__ == "__main__":
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    dev=Device.Device(s)
    dev.init()

    dt = MyDate.MyDate()
    timestr = dt.getNowMyFormat(option="sec")

    inocc=IboINOCC.IboINOCC(dev.gonio)
    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"

    dev.prepCenteringSideCamera()

    target_image="%s/sc_%s.png"%(backpath,timestr)
    back_image = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/scbg4.png"

    inocc.getImage("side",target_image,binning=4)
    inocc.analyzePreciseSideCamera(target_image,back_image)
