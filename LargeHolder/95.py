import socket,os,sys,datetime,cv2,time,numpy
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")

import Device
import IboINOCC
import Date

if __name__ == "__main__":
    import Gonio
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    img_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Junk/"
    
    dev=Device.Device(s)
    dev.init()
    inocc=IboINOCC.IboINOCC(dev.gonio)

    # preparation
    #dev.prepCenteringBackCamera()
    dev.prepCenteringSideCamera()

    initial_phi=dev.gonio.getPhi()

    # Date directory
    dt = Date.Date()
    timestr = dt.getNowMyFormat(option = "min")

    imgname = "%s/sc4_%s.png"%(img_path, timestr)

    inocc.getImage("side",imgname,binning=4,sc_exptime=2500)
    angle,score,ymean=inocc.tune_phi(imgname)

    print "ANGLE,Score,ymean = ",angle,score,ymean
