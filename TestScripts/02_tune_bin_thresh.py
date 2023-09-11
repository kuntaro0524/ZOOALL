import cv2,sys, os
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import CryImageProc

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()

    bright=[5000,10000,20000,30000,40000,50000]
    gain=[500,1000,1500,2000]

    picpath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TestImages/"

    for br in bright:
        for ga in gain:
            cfile="%s/%s_%d-%d.ppm"%(picpath,"loop",br,ga)
            bfile="%s/%s_%d-%d.ppm"%(picpath,"back",br,ga)

            print(bfile, cfile)
            # set Target/Back images
            cip.setImages(cfile, bfile)
            cont = cip.getContour()
            orig_file = "./cont.png"
            mv_file = "%s/nilon3_thresh10_%s_%s.png" % (picpath, br, ga)
            print(orig_file, mv_file)
            os.system("mv %s %s" % (orig_file, mv_file))
            #cip.getDiffImages(outimage)
