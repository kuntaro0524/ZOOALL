import cv2,sys,os
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
import CryImageProc

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()

    #bright=[500,1000,2000,2500,3000,3500,4000,4500,5000]
    #gain=[500,1000,1500,2000]
    #bright=[1000,2000,2500,3000,3500,4000,4500,5000]
    #gain=[1000,1500,2000,2500]
    bright=[4000,4100,4200,4300,4400,4500]
    gain=[1000,1100,1200,1300,1400,1500]
    #bright=[1600,1700,1800,1900,2000,2100,2200,2300,2400,2500]
    #gain=[500,600,700,800,900,1000,1100,1200,1300,1400,1500]
    #bright=[3000,3100,3200,3300,3400,3500,3600,3700,3800,3900,4000]
    #gain=[500,600,700,800,900,1000,1100,1200,1300,1400,1500]
    #bright=[3500,3600,3700,3800,3900,4000,4100,4200,4300,4400,4500]
    #gain=[1000,1100,1200,1300,1400,1500,1600,1700,1800,1900]
    #bright=[1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000]
    #gain=[1400,1500,1600,1700,1800,1900,2000]

    #cappath = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TestImages210302/"
    cappath = "/isilon/users/target/target/Staff/2021A/210302/INOCC/TestImage-4700-center/"

    # BIN
    ibin = 0
    for br in bright:
        for cn in gain:
            bfile="%s/back_%d-%d.ppm"%(cappath,br,cn)
            cfile="%s/loop_%d-%d.ppm"%(cappath,br,cn)
            print(bfile, cfile)
            # set Target/Back images
            cip.setImages(cfile, bfile)
            prefix = "%s/con_check_%s_%s"%(cappath, br, cn)
            print(prefix)
            cont = cip.getContour()
            prep_str = "%4d-%4d" % (br,cn)
            bin_name = "%s/bin_%s.png" % (cappath, prep_str)
            con_name = "%s/con_%s.png" % (cappath, prep_str)
            command = "mv bin.png %s" % bin_name
            os.system(command)
            command = "mv cont.png %s" % con_name
            os.system(command)
            #cip.getDiffImages(outimage)
            ibin+=1
