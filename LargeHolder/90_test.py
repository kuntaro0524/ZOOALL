import os,sys,glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
import time
import numpy as np
import socket
import Zoo
import Device
import IboINOCC

if __name__ == "__main__":
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    puckid="CPS0296"
    #pinid=2
    #### ZOO
    dev=Device.Device(s)
    dev.init()

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    for pinid in [2]:
        try:
            zoo.mountSample(puckid,pinid)
            zoo.waitTillReady()
        except MyException, ttt:
            print "Sample mounting failed. Contact BL staff!"
            sys.exit(1)
    
        inocc=IboINOCC.IboINOCC(dev)
        # preparation
        dev.prepCenteringBackCamera()
    
        #def captureMatchBackcam(self,picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/Templates/BackCamera/"):
        while(1):
            max_similarity=inocc.captureMatchBackcam()
            if max_similarity > 0.80:
                break
