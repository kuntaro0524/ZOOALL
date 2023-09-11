import os,sys,math,numpy,socket,datetime
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import IboINOCC
import Zoo
import Gonio,BS
import Device
import LoopMeasurement
import StopWatch

if __name__ == "__main__":
        blanc = '172.24.242.41'
        b_blanc = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((blanc,b_blanc))

        # preparation
        dev=Device.Device(s)
        dev.init()

        dev.prepCenteringLargeHolderCam1()
