import cv2,sys
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
import CryImageProc

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()

    bright=[10000,20000,30000,40000,50000]
    contrast=[9000,18000,27000]

    picpath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/TestImages/"

    for br in bright:
        for cn in contrast:
            bfile="%s/back_180517-%4d-%4d.ppm"%(picpath,br,cn)
            cfile="%s/loop_180517-%4d-%4d.ppm"%(picpath,br,cn)
            print bfile, cfile
            # set Target/Back images
            cip.setImages(bfile, cfile)
            prefix = "con_check_%s_%s"%(br,cn)
            cont = cip.getContour(logprefix = prefix)
            #cip.getDiffImages(outimage)

