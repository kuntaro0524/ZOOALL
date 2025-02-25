import sys,os,math,cv2,socket
import datetime, time
import numpy as np
import Zoo
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

from File import *
import Capture
import Device
import Date

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    dev = Device.Device(ms)
    dev.init()
#    dev.prepCentering()

    cap = Capture.Capture()
#    cap.prep()
    cappath = "/isilon/users/admin45/admin45/191004_BL45XU_Elong/air_4L/"

    dt = Date.Date()

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    # prefix should be 'back' or 'loop'
    sample_list = {
        "SPINEReuse":[1, 3, 6, 7, 10, 13, 14, 16],
        "HumpCuMicro":[3, 4, 5, 6, 10, 11, 12, 14],
    }

    for key in sample_list:
        for cnt in sample_list[key]:
            puckid = key
            pinid = cnt
            print(puckid, pinid)
            try:
                zoo.mountSample(puckid, pinid)
                zoo.waitTillReady()
            except MyException, ttt:
                print "Failed", ttt.args[0]

            dev.prepCentering()
            cap.prep()

            for nx in range(30):
                dtstr = dt.getNowMyFormat(option="sec")
                prefix = "%s-%s_%s" % (puckid, pinid, dtstr)
                filename="%s/%s.ppm"%(cappath, prefix)
                print "Captureing..",filename
                cap.capture(filename)
                time.sleep(10.0)

            zoo.getSampleInformation()
            zoo.dismountCurrentPin()
            zoo.waitTillReady()

    zoo.disconnect()
    ms.close()

#    while(1):
#        dtstr = dt.getNowMyFormat(option="sec")
#        prefix = "%s_%s" % (pprefix,dtstr)
#        filename="%s/%s.ppm"%(cappath,prefix)
#        print "Captureing..",filename
#        cap.capture(filename)
#        time.sleep(10.0)
