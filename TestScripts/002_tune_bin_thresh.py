import cv2,sys,os
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
import CryImageProc

if __name__=="__main__":
    cip = CryImageProc.CryImageProc()

    bright=[1500,2500,3500]
    gain=[4000,10000,16000]

    cappath = "/staff/bl44xu/BLsoft/TestZOO/TestScripts"

    ibin = 0
    for br in bright:
        for cn in gain:
            bfile="%s/back_%d-%d.ppm"%(cappath,br,cn)
            cfile="%s/pin_%d-%d.ppm"%(cappath,br,cn)
            print(bfile, cfile)
            # set Target/Back images
            cip.setImages(cfile, bfile)
            prefix = "%s/con_check_%s_%s"%(cappath, br, cn)
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
