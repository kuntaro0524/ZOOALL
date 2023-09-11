import sys,os,math,numpy
from MyException import *
import time
import datetime
import DiffscanLog
#import scipy.spatial
# coded 2018/06/27

class Crystal:
    # initialize with 3D coordinate
    def __init__(self,scan_h_step,scan_v_step):
        self.xyzs_list=[]
        self.score_total=0.0
        self.code_list=[]
        self.isEdged=False
        # scan step in [mm]
        self.h_step=scan_h_step
        self.v_step=scan_v_step

        # Flag of preparation
        self.isPrep=False
        # Single grid
        self.isSingle=False

        self.DEBUG=False

    # x,y,z: goniometer coordinate
    # h,v: horizontal & vertical grid points
    def addGrid(self,x,y,z,h,v,score):
        #print score,type(score)
        self.code_list.append((x,y,z,h,v,score))

    def printAll(self):
        index=0
        for x,y,z,h,v,score in self.code_list:
            print("%5d %8.4f %8.4f %8.4f %5d %5d %5d Total=%5d"%(index,x,y,z,h,v,score,self.score_total))
            index+=1
        print("\n\n")

    def getTotalScore(self):
        if self.isPrep==False:
            #print "getTotalScore isPrep:False"
            self.prepInfo()
        return self.score_total

    def getXYZlistAsLines(self):
        lines=""
        for x,y,z,h,v,score in self.code_list:
            lines+=("%8.4f %8.4f %8.4f %5d %5d %5d\n"%(x,y,z,h,v,score))
        lines+="\n\n"
        return lines

    def getPeakCode(self):
        score_max=-9999.9999

        for x,y,z,h,v,score in self.code_list:
            #print x,y,z,score
            if score > score_max:
                score_max=score
                max_xyz=x,y,z

        #print "Max=",max_xyz
        return max_xyz

    # return goniometer coordinate
    # coded on 2016/07/26
    # renewed on 2018/12/09
    def getGrav(self):
        sum_xscore=0.0
        sum_yscore=0.0
        sum_zscore=0.0
        sum_score=0.0

        for x,y,z,h,v,score in self.code_list:
            # For gravity calculation
            sum_xscore+=score*x
            sum_yscore+=score*y
            sum_zscore+=score*z
            sum_score+=score

        gv_x=sum_xscore/sum_score
        gv_y=sum_yscore/sum_score
        gv_z=sum_zscore/sum_score

        gv_xyz=gv_x,gv_y,gv_z

        return gv_xyz

    def prepInfo(self):
        max_h=-9999
        min_h= 9999
        max_v=-9999
        min_v= 9999

        for x,y,z,h,v,score in self.code_list:
            self.score_total+=score
            if h > max_h:
                max_h=h
                self.xyz_maxh=x,y,z
            if h < min_h:
                min_h=h
                self.xyz_minh=x,y,z
            if v > max_v:
                max_v=v
                self.xyz_maxv=x,y,z
            if v < min_v:
                min_v=v
                self.xyz_minv=x,y,z

        if self.DEBUG==True:
            print("Maxh=",self.xyz_maxh)
            print("Minh=",self.xyz_minh)
            print("Maxv=",self.xyz_maxv)
            print("Minv=",self.xyz_minv)

        min_h_y=self.xyz_minh[1]
        max_h_y=self.xyz_maxh[1]

        # Crystal length along horizontal 
        self.cry_hsize_grid=numpy.fabs(min_h-max_h)
        if self.cry_hsize_grid==0:
            self.isSingle=True
            self.edges=self.xyz_minh,self.xyz_maxh
        else:
            self.isSingle=False
            self.edges=self.xyz_minh,self.xyz_maxh

        self.cry_hsize=(self.cry_hsize_grid+1)*self.h_step

        # Flag on
        self.isEdged=True
        self.isPrep=True
        
        if self.DEBUG==True:
            print("Score of this crystal=",self.score_total)
            print("H crystal size=",self.cry_hsize,self.isSingle)

        return self.cry_hsize,self.isSingle,self.score_total,self.edges

    # Left Lower on the left scan
    # math.sqrt(h*h+v*v) -> Maximum
    def getLLedge(self):
        max_dist=0.0
        for x,y,z,h,v,score in self.code_list:
            index_distance=math.sqrt(h*h+v*v)
            if index_distance > max_dist:
                rx=x
                ry=y
                rz=z
                max_dist=index_distance

        return rx,ry,rz

    # Upper right on the right scan
    # math.sqrt(h*h+v*v) -> Maximum
    def getRUedge(self):
        min_dist=999999.9
        for x,y,z,h,v,score in self.code_list:
            index_distance=math.sqrt(h*h+v*v)
            if index_distance < min_dist:
                rx=x
                ry=y
                rz=z
                min_dist=index_distance

        return rx,ry,rz

    def getCryHsize(self):
        if self.isPrep==False:
            self.prepInfo()
        return self.cry_hsize

    def getRoughEdges(self):
        if self.isPrep==False:
            self.prepInfo()
        print(self.cry_hsize,self.isSingle,self.score_total,self.edges)
        return self.edges

if __name__=="__main__":
    import Map2Crystal
    cxyz=(0.7379,   -11.5623,    -0.0629)
    phi=0.0
    prefix="xi-KLaT006-12"
    scan_path=sys.argv[1]

    m2c=Map2Crystal.Map2Crystal(scan_path,cxyz,phi)

    min_score=20
    max_score=80
    cry_size=float(sys.argv[2])
    m2c.setCrystalSize(cry_size)
    crystal_list=m2c.searchPixelBunch("CPS0298-01",score_thresh,cry_size)
    #crystal_list=m2c.searchMulti("CPS0298-01",min_score,max_score,cry_size)

    
    print(len(crystal_list))
    index=0
    for cry in crystal_list:
        #x,y,z= cry.getPeakCode()
        #cry.printAll()
        cry_hsize,isSingle,score_total,edges = cry.prepInfo()
        print(cry_hsize,isSingle,score_total,edges)
