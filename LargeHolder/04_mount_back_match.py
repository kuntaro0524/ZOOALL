import socket,os,sys,datetime,cv2,time,numpy
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Device
import IboINOCC
import Zoo
import MyException

if __name__ == "__main__":
    import Gonio
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    dev=Device.Device(s)
    dev.init()

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    try:
        zoo.mountSample("CPS0389",1)
        zoo.waitTillReady()
    except MyException, ttt:
        print "Sample mounting failed. Contact BL staff!"
        sys.exit(1)

    inocc=IboINOCC.IboINOCC(dev)

    # preparation
    dev.prepCenteringBackCamera()

    view="back"
    filename="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/b.png"
    inocc.getImage(view,filename,binning=2)
    inocc.anaImage(filename,view)
    
#     def captureMatchBackcam(self,picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/Templates/BackCamera/"):
    while(1):
        max_similarity=inocc.captureMatchBackcam()
        if max_similarity > 0.80:
            break
