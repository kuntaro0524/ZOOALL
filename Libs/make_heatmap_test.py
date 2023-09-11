import sys, os, math, numpy, scipy
import scipy.spatial as ss
import MyException
import time
import datetime
import DiffscanLog
import SummaryDat
import Crystal
import cv2
import copy
import logging
import LogString
import AnaHeatmap

if __name__ == "__main__":
    phi = 0.0
    prefix = "2d"
    scan_path = sys.argv[1]
    ahm = AnaHeatmap.AnaHeatmap(scan_path)

    min_score = int(sys.argv[2])
    max_score = int(sys.argv[3])
    dist_thresh = float(sys.argv[4])

    ahm.setMinMax(min_score, max_score)
    hm = ahm.prep(prefix)

    print((hm.shape))

    # ahm.searchPixelBunch(prefix, True)
    #
    # ahm.vectorTest2()
    # ahm.makeBinMap(prefix, "summary2binMap.png")
    # # ahm.polygonSearch("summary2binMap.png", prefix="kakudai")
    #
    """
    crystal_array = ahm.searchPixelBunch(prefix, True)
    print "%5d crystals were found" % len(crystal_array)
    for cry in crystal_array:
        #print "CRYCRYCRYCRYCRYCRYCRYCRY"
        cry.printAll()
        #print cry.getTotalScore(), cry.getRoughEdges(), cry.getCryHsize()
        #print "CRYCRYCRYCRYCRYCRYCRYCRY"

    # ahm.ana1Dscan(prefix)
    # def getBestCrystalCode(self,option="gravity"):
    """
