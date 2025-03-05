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

    img_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"
    
    dev=Device.Device(s)
    dev.init()
    inocc=IboINOCC.IboINOCC(dev.gonio)

    dtdt = Date.Date()
    dtstr = dtdt.getNowMyFormat(option="min")

    inocc=IboINOCC.IboINOCC(dev.gonio)

    # Capture background (backcamera)
    dev.prepCenteringBackCamera()
    inocc.getImage("back","%s/bc_%s.png"%(img_path,dtstr),binning=2)

    dev.prepCenteringSideCamera()
    # Side camera background
    inocc.getImage("side","%s/sc4_%s.png"%(img_path,dtstr),binning=4)
    inocc.getImage("side","%s/sc2_%s.png"%(img_path,dtstr),binning=2)
