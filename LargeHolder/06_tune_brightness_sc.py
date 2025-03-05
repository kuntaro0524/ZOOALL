import socket,os,sys,datetime,cv2,time,numpy
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")

import Device
import IboINOCC

if __name__ == "__main__":
    import Gonio
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    img_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/"
    
    dev=Device.Device(s)
    dev.init()
    inocc=IboINOCC.IboINOCC(dev.gonio)

    # preparation
    dev.prepCenteringBackCamera()
    initial_phi=dev.gonio.getPhi()

    inocc.getImage("side","%s/sctest.png"%img_path,binning=4)
