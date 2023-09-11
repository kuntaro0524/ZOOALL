import cv2,sys
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import CryImageProc

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()

    picpath = sys.argv[1]
    backpath = sys.argv[2]

    bin_thresh = int(sys.argv[3])

    cip.setImages(picpath, backpath)
    cip.setBinThresh(bin_thresh)
    prefix = "./anatest"
    cont = cip.getContour()
