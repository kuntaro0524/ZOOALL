import sys,os,math,numpy
from MyException import *
import time
import datetime
import DiffscanLog
import Crystal
#import scipy.spatial

# coded 2018/06/27
# modified 2018/11/26 K.Hirata on MBP13 Sandbox
# /Users/kuntaro0524/Dropbox/PPPP/Sandbox/10.HEBI2

class CrystalList:
    # initialize with 3D coordinate
    def __init__(self,array_of_CrystalClass):
        self.debug=False
        self.crystals=array_of_CrystalClass
        self.scores=[]
        self.isSorted=False

    def storeScores(self,):
        for crystal in self.crystals:
            crystal.printAll()

    def addXYZS(self,x,y,z,score):
        #print "ADDING:",x,y,z,score
        self.xyzs_list.append((x,y,z,score))

    def getSortedCrystalList(self):
        # a,b: an object of 'Crystal' class
        def compCryScore(x,y):
            a=x.getTotalScore()
            b=y.getTotalScore()
            if self.debug==True:
                print "SCORE COMPARE",a,b
            if a==b: return 0
            if a<b: return 1
            return -1

        if self.debug==True:
            print "OOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
            for c in self.crystals:
                c.printAll()
            #print self.crystals
            print "OOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
    
        # Sorting better crystals
        # The top of crystal is the best one
        # The bottom is the worst one
        self.crystals.sort(cmp=compCryScore)

        if self.debug==True:
            print "NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"
            for c in self.crystals:
                c.printAll()
            #print self.crystals
            print "NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"

        self.isSorted=True

        return self.crystals

    # Find the best crystal and return the Gravity 
    def getBestCrystalCode(self,option="gravity"):
        if self.isSorted==False:
            self.getSortedCrystalList()

        if len(self.crystals)==0:
            raise MyException("CrystalList.getBestCrystalCode: No good crystals")

        best_crystal=self.crystals[0]
        if option=="gravity":
            gxyz=best_crystal.getGrav()

        if option=="peak":
            gxyz=best_crystal.getPeakCode()

        return gxyz

    def getTotalScore(self):
        for xyzs in self.xyzs_list:
            x,y,z,score=xyzs
            self.score_total+=s
        return self.score_total

    def printAll(self):
        index=0
        for x,y,z,score in self.xyzs_list:
            print "%5d %8.4f %8.4f %8.4f %5d"%(index,x,y,z,score)
            index+=1
        print "\n\n"

    def getXYlist(self):
        return self.xyzs_list
    
    def getInfo(self):
        return self.x_list,self.y_list,self.score_list,self.imgNumList

    def getSortedPeakCodeList(self):
        # sorting with scores
        self.getSortedCrystalList()

        rtn_list=[]
        # convert crystal -> gonio XYZ
        for crystal in self.crystals:
            xyz=crystal.getPeakCode()
            rtn_list.append(crystal.getPeakCode())
        return rtn_list

    def getSize(self):
        return len(self.x_list)

if __name__=="__main__":
    import AnaHeatmap
    cxyz=(0.7379,   -11.5623,    -0.0629)
    phi=0.0
    prefix="xi-KLaT006-12"
    scan_path=sys.argv[1]

    ahm=AnaHeatmap.AnaHeatmap(scan_path,cxyz,phi)

    score_thresh=10
    cry_size=float(sys.argv[2])
    ahm.setCrystalSize(cry_size)
    crystal_list=ahm.searchMulti("CPS0298-01",score_thresh,cry_size)
    crystalist=CrystalList(crystal_list)
    crystalist.storeScores()
