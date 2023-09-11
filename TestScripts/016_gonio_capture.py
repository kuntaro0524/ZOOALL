import cv2,sys, time, os
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
import CryImageProc
import Capture
import DirectoryProc


if __name__=="__main__":

    picpath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/TestImages2/"

    bright=[10000,20000,30000,40000,50000]
    contrast=[1000,5000,9000,18000,27000,36000,45000,50000]

    loop_size = 400.0
    option = "gravity"

    outfile = open("long_scan.dat", "w")

    for i in range(0,10000):
        filename = "%s/cap%05d.ppm"%(picpath, i)
        logdir = "%s/%04d/" % (picpath, i)

        # Making today's directory
        if os.path.exists(logdir):
            print("%s already exists"%logdir)
        else:
            os.makedirs(logdir)
            os.system("chmod a+rw %s" % logdir)

        #print dp.getRoundHeadPrefix(dir_prefix, "png", ndigit = 4)
        #prefix = dp.getRoundHeadPrefix(ndigit = 4)
        #print prefix
        
        cip = CryImageProc.CryImageProc(logdir = logdir)
        # set Target/Back images
        cip.setImages(filename, bfile)
        cont = cip.getContour()
        xtarget, ytarget, area, hamidashi_flag = cip.getCenterInfo(loop_size = loop_size, option = option)
        outfile.write("%s TARGET X,Y = %5.1f %5.1f\n" % (filename, xtarget, ytarget))
