import cv2,sys, os
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
import CryImageProc

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()

    #bright=[10000,20000,30000,40000,50000]
    #contrast=[9000,18000,27000,36000,45000,54000]

    #bright=[1500,2500,5000,10000,20000,30000,40000,50000]
    #contrast=[5000, 9000,18000,27000,36000,45000,54000]

    bright=[1500,2500,5000,10000,20000,30000,40000,50000]
    contrast=[5000, 9000,18000,27000,36000,45000,54000]
    #bright=[500,1000,1500,2500,5000,10000,20000,30000,40000,50000]
    #contrast=[5000, 9000,18000,27000,36000,45000,54000]

    #bright=[3500]
    #contrast=[10000,15000,20000,25000,30000,35000]

    #bright=[2500]
    #contrast=[30000,32000,34000,36000,38000,40000]

    picpath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/TestImages4/"

    for br in bright:
        for cn in contrast:
            bfile="%s/back_210326-%d-%d.ppm"%(picpath,br,cn)
            cfile="%s/nilon3_210326-%d-%d.ppm"%(picpath,br,cn)
            print bfile, cfile
            # set Target/Back images
            cip.setImages(cfile, bfile)
            cont = cip.getContour()
            orig_file = "./cont.png"
            mv_file = "%s/nilon3_thresh10_%s_%s.png" % (picpath, br, cn)
            print orig_file, mv_file
            os.system("mv %s %s" % (orig_file, mv_file))
            #cip.getDiffImages(outimage)

