import cv2,sys
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
import CryImageProc

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()

    bfile="back_180517-10000-54000.ppm"
    cfile="test3.ppm"
    # set Target/Back images
    cip.setImages(cfile, bfile)
    prefix = "tttt"
    print prefix
    cont = cip.getContour()
    area = cip.getArea()
    print area
