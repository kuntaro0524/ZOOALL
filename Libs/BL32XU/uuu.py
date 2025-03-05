import sys,os,math,numpy
from MyException import *
import time
#from AnaShika import CrystalSpot
import AnaShika

if __name__=="__main__":
        #def __init__(self,summary_dat_path,cxyz,phi):
        cxyz=(0.7379,   -11.5623,    -0.0629)
        phi=35.0

        #spot_path=sys.argv[1]
        #prefix=sys.argv[2]
        #dist_thresh=sys.argv[3]
        #prefix="rasmas_"
        #spot_path="/isilon/users/target/target/Staff/kuntaro/Brian/150920/xi-KLaT012-16/scan/_spotfinder"
        #prefix="xiangyu-KLaT003-08_"

        #def __init__(self,summary_dat_path,cxyz,phi):
        spot_finder="/isilon/users/target/target/AutoUsers/160520/KLaT003/15/scan/_spotfinder/"
        prefix="scan01_"
        asss=AnaShika.AnaShika(spot_finder,cxyz,phi)
        #asss.setSummaryFile(prefix)
        dist_thresh=0.0101

        #asss.makeList(prefix,kind="n_spots")
        #asss.listScoreAbove(prefix,kind="n_spots")
        #asss.anadis(prefix)
        #asss.findCrystals(prefix)
        #asss.make2Dmap()
        #asss.test("toyoda-1010-05_")
        #asss.anadis(prefix)
        #def findCrystals(self,prefix,kind="n_spots",dist_thresh=0.01001):

        asss.setThresh(10)
        crystals=asss.findCrystals(prefix,dist_thresh=dist_thresh)

        pfile=open("peak.dat","w")
        gfile=open("grav.dat","w")
        for crystal in crystals:
                print "======= START ======"
                #print "<< EDGES >>"
                #crystal.findHoriEdges()
                #print "<< EDGES >>"
                gx,gy,gz=crystal.getGrav()
                print "Gravity of this crystal",gx,gy,gz
                #print "getPeakCode!!!"
                #px,py,pz=crystal.getPeakCode()
                #pfile.write("%8.5f %8.5f %8.5f\n"%(px,py,pz))
                #gfile.write("%8.5f %8.5f %8.5f\n"%(gx,gy,gz))
                print "======= END ======"

        pfile.close()
        gfile.close()

