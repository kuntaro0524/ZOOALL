import cv2,sys, os
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
sys.path.append("/staff/bl41xu/BLsoft/PPPP/10.Zoo/Libs/")
import CryImageProc

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()

    #bright=[1500,2500,5000,10000,20000,30000,40000,50000]
    #contrast=[5000, 9000,18000,27000,36000,45000,54000]
    #bright=[500,1000,1500,2500,5000,10000,20000,30000,40000,50000]
    #contrast=[5000, 9000,18000,27000,36000,45000,54000]
    bright=[14000, 14200, 14400, 14600, 14800, 15000, 15200, 15400, 15600, 15800, 16000]
    #contrast=[30000,32000,34000,36000,38000,40000]
    contrast=[18000]
    gain = [900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]

    picpath = "/staff/bl41xu/TestImg_231010/"

    for br in bright:
        for gn in gain:
            bfile="%s/back_180517-%d-%d.ppm"%(picpath,br,gn)
            cfile="%s/loop_180517-%d-%d.ppm"%(picpath,br,gn)
            print bfile, cfile
            # set Target/Back images
            cip.setImages(cfile, bfile)
            cont = cip.getContour()
            orig_file = "./cont.png"
            mv_file = "%s/loop_thresh10_%s_%s.png" % (picpath, br, gn)
            print orig_file, mv_file
            os.system("mv %s %s" % (orig_file, mv_file))
            #cip.getDiffImages(outimage)

