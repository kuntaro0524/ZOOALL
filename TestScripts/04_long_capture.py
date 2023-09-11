import cv2,sys, time
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import CryImageProc
import Capture

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()

    picpath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LongSnap/"
    bfile="back_180517-10000-54000.ppm"

    cap = Capture.Capture()
    cap.prep()

    for i in range(0,10000):
        filename = "%s/cap%05d.ppm"%(picpath, i)
        cap.capture(filename)
        
        # set Target/Back images
        cip.setImages(filename, bfile)
        prefix = "%s/con_check_%05d"%(picpath, i)
        print(prefix)
        cont = cip.getContour(logprefix = prefix)

        time.sleep(1.0)
