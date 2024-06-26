import sys,math,numpy,os
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import datetime
import LoopMeasurement
import Zoo
import AttFactor
import AnaShika
import Condition
import MyException
import StopWatch
import CrystalSpot

class HITO:
    def __init__(self,zoo,lm,cxyz_2d,phi_face,hbeam,vbeam):
        # Important class
        self.zoo=zoo
        # LoopMeasurement class
        self.lm=lm
        
        # Face angle
        self.phi_face=phi_face

        # list of found crystals
        self.cxyz_2d=cxyz_2d

        # Attenuator factor
        self.attfactor=AttFactor.AttFactor()

        # Time out for waiting scan result (5mins)
        self.timeout=300.0

        # Completeness threshold in analysis for SHIKA result
        self.comp_thresh=0.99

        # Helical minimum/maximum size for mixed mode
        self.min_hel_size=0.045 # for choosing 'single crystal'
        self.max_hel_size=0.100 # for choosing 'clustered crystals'

        # Beam size used for 2D raster scan
        # unit [mm]
        self.hbeam=hbeam/1000.0
        self.vbeam=vbeam/1000.0

        # Distance for judging whether partial helical can be applied
        # Vertical distance
        self.dist_cry_thresh=self.vbeam*3.0 # 5 times longer than the vertical beamsize

    # Helical crystal size (minimum and maximum for mixed mode
    def setHelicalCrystalSize(self,minsize,maxsize):
        self.min_hel_size=minsize
        self.max_hel_size=maxsize
    def getGoodTrans(self):
        print "faceScan"
        return 1.0

        # Relating to the summary.dat
        # copied from LoopMeasurement

    def readSummaryDat(self,raster_path,scan_id,cxyz,phi,thresh_nspots=30,comp_thresh=0.95):
        # SHIKA analysis
        shika_dir="%s/_spotfinder/"%raster_path
        ashika=AnaShika.AnaShika(shika_dir,cxyz,phi)
        ashika.setSummaryFile("summary.dat")
        # scan_id & prefix are different each other
        prefix="%s"%scan_id
        print "Searching prefix is %s"%prefix

        # N grids on the 2D raster scan
        ngrids=self.lm.raster_n_height*self.lm.raster_n_width

        # SHIKA waiting for preaparation
        # 12 minutes
        try:
                ashika.readSummary(prefix,ngrids,comp_thresh=comp_thresh,timeout=self.timeout)

        except:
                raise MyException.MyException("shikaSumSkipStrong failed to wait summary.dat")

        return ashika

    # coded on 2016/06/27
    # using new AnaShika.py
    # max_ncry : max number of crystals for data collection
    # copied from LoopMeasurement and modified
    # "thresh_nspots" is normally 'cond.shika_minscore'
    def getCrystals(self,raster_path,scan_id,thresh_nspots=30,crysize=0.10,max_ncry=50):
        def compCryScore(x,y):
                a=x.score_total
                b=y.score_total
                print "SCORE COMPARE",a,b
                if a==b: return 0
                if a<b: return 1
                return -1
                print thresh_nspots,crysize

        # SHIKA analysis
        ashika=self.readSummaryDat(raster_path,scan_id,self.cxyz_2d,self.phi_face)
        # Setting threshold for searching
        ashika.setThresh(thresh_nspots)

        # Crystal finding
        print "Crystal size = %8.5f"%crysize
        crystals=ashika.findCrystals(scan_id,dist_thresh=crysize)
        n_cry=len(crystals)
        print "Crystals %5d\n"%n_cry

        # Sorting better crystals by total number of spots
        # The top of crystal is the best one
        # The bottom is the worst one
        crystals.sort(cmp=compCryScore)

        return crystals

        # getCrystals was modified on 2018/01/25
        # max_ncry : max number of crystals for data collection
        # copied from LoopMeasurement and modified
        # "thresh_nspots" is normally 'cond.shika_minscore'
    def getCrystalsMinMax(self,raster_path,scan_id,min_score=10,max_score=1000,crysize=0.10,max_ncry=50):
        def compCryScore(x,y):
            a=x.score_total
            b=y.score_total
            #print "SCORE COMPARE",a,b
            if a==b: return 0
            if a<b: return 1
            return -1
            print thresh_nspots,crysize

        # SHIKA analysis
        ashika=self.readSummaryDat(raster_path,scan_id,self.cxyz_2d,self.phi_face)

        # Setting min/max thresholds to find good crystals
        ashika.setMinMax(min_score,max_score)

        # Crystal finding
        print "Crystal size = %8.5f"%crysize
        crystals=ashika.findCrystals(scan_id,dist_thresh=crysize)
        n_cry=len(crystals)
        print "Crystals %5d\n"%n_cry

        # Sorting better crystals by total number of spots
        # The top of crystal is the best one
        # The bottom is the worst one
        crystals.sort(cmp=compCryScore)

        return crystals

    def logXYZ(self,xyz):
        strings="%9.4f %9.4f %9.4f"%(xyz[0],xyz[1],xyz[2])
        return strings

    def calcDist(self,xyz1,xyz2):
        x1,y1,z1=xyz1
        x2,y2,z2=xyz2

        dx=x1-x2
        dy=y1-y2
        dz=z1-z2

        distance=math.sqrt(dx*dx+dy*dy+dz*dz)

        return distance


    # 2016/12/10 added for detecting crystal size
    def checkCrysizeAt(self,scan_id,gxyz):
        scan_length=500.0
        # At face angle
        Lv_d=self.finalVscan(scan_id,gxyz,self.phi_face,scan_length)
        return 1

    # Inteligent crystal list maker for helical/small wedge data collection
    # 2018/01/24 large modification (min/max scores to select crystals)
        #single_crys,heli_crys,perfect_crys=hito.shiwakeru(raspath,scan_id,min_score=cond.shika_minscore,
                  #max_score=cond.shika_maxscore,crysize=crysize,max_ncry=cond.shika_maxhits)
    def shiwakeru(self,raster_path,scan_id,min_score,max_score,crysize,max_ncry):
        def compCryScore(x,y):
                a=x.score_total
                b=y.score_total
                #print "SCORE COMPARE",a,b
                if a==b: return 0
                if a<b: return 1
                return -1
                print thresh_nspots,crysize


        # SHIKA analysis
        ashika=self.readSummaryDat(raster_path,scan_id,self.cxyz_2d,self.phi_face)
        # Setting threshold for searching
        ashika.setMinMax(min_score,max_score)
        diffscan_path=raster_path

        # Crystal finding
        print "Crystal size = %8.5f"%crysize
        crystals=ashika.findCrystals(scan_id,dist_thresh=crysize)
        n_cry=len(crystals)
        print "Crystals %5d\n"%n_cry

        # Check overlap
        print "#########################"
        perfect_crystals=[]
        kabutteru_index_list=[]
        check_list=[0]*len(crystals)
        for index1 in range(0,len(crystals)):
            crystal1=crystals[index1]
            crystal1.setDiffscanLog(diffscan_path)
            for index2 in range(index1+1,len(crystals)):
                crystal2=crystals[index2]
                crystal2.setDiffscanLog(diffscan_path)
                # Left coordinate has larger Y value
                l1xyz,r1xyz=crystal1.findHoriEdges()
                l2xyz,r2xyz=crystal2.findHoriEdges()

                # Crystal 1 left & right edges
                l1=l1xyz[1]
                r1=r1xyz[1]
                # Crystal 2 left & right edges
                l2=l2xyz[1]
                r2=r2xyz[1]
                # one crystal overlaps with another
                if (l2>=r1 and l2<=l1) or (r2>=r1 and r2<=l1):
                    kabutteru_index_list.append((index1,index2))
                    # Flags for overlapped with other crystals
                    print "Flags for overlapped with other crystals: pattern1"
                    check_list[index1]=1
                    check_list[index2]=1
                    # one crystal is larger than one and completely overlapped
                elif (l1>=r2 and l1<=l2) or (r1>=r2 and l1<=l2):
                    print "Flags for overlapped with other crystals: pattern2"
                    kabutteru_index_list.append((index1,index2))
                    check_list[index1]=1
                    check_list[index2]=1
        # Calculation of vertical distance between overlapped crystals.
        kaburidat=open("%s/kabutteru.dat"%raster_path,"w")
        hontouni_kabutteru_index_list=[]
        for c1,c2 in kabutteru_index_list:
            print "INDEX=",c1,c2
            cry1=crystals[c1]
            cry2=crystals[c2]
            x1a,y1a=cry1.getXYlist()
            x2a,y2a=cry2.getXYlist()
            bad_flag=False
            for y1,y2 in zip(y1a,y2a):
                vert_distance=numpy.fabs(y1-y2)
                if vert_distance < self.dist_cry_thresh:
                    print " (%5d-%5d) vertical distance %8.5f mm is shorter than %8.5f mm"%(c1,c2,vert_distance,self.dist_cry_thresh)
                    hontouni_kabutteru_index_list.append((c1,c2))
                    for x1,y1 in zip(x1a,y1a):
                        kaburidat.write("%8.5f %8.5f\n"%(x1,y1))
                    kaburidat.write("\n\n")
                    for x2,y2 in zip(x2a,y2a):
                        kaburidat.write("%8.5f %8.5f\n"%(x2,y2))
                    kaburidat.write("\n\n")
                    # They are also clustered crystals
                    check_list[c1]=-1
                    check_list[c2]=-1
        ## Checking the size 
        index=0
        # Small crystal for small wedge: FLAG=10
        # Clustered crystal for small wedge: FLAG=-2
        for crystal in crystals:
            # Check crystal length along 'rotation axis'
            hsize,vsize=crystal.getDimensions(self.hbeam,self.vbeam)

            # Case: crystal size is not enough for helical data collection
            if hsize < self.min_hel_size:
                print "crystal size is smaller than threshold(%8.5f)"%self.min_hel_size
                check_list[index]=10
            # Case: crystal size is larger than set value for helical data collection
            else:
                print "Crystal size H,V=",hsize,vsize
                if hsize > self.max_hel_size or vsize > self.max_hel_size:
                    check_list[index]=-2
            index+=1

        # Clusterd crystals larger than crystal size)
        ngfile=open("%s/ng.dat"%raster_path,"w")
        ng_crystals=[]
        index=0
        # check_list: 
        # -2: very large crystal bunch in SHIKA heat map
        # -1: very near to the neighbor crystals
        for c in check_list:
            if c==-2 or c==-1:
                cry=crystals[index]
                x1a,y1a=cry.getXYlist()
                for x1,y1 in zip(x1a,y1a):
                    ngfile.write("%8.5f %8.5f\n"%(x1,y1))
                ngfile.write("\n\n")
                ng_crystals.append(cry)
            index+=1
        ngfile.close()

        # Zutazuta list
        zutazuta=[]
        index=0
        for c in check_list:
            if c<0:
                cry=crystals[index]
                zutazuta.append(cry)
            index+=1

        # Making crystal list for 'partial helical'
        gfile=open("%s/partial_helical.dat"%raster_path,"w")
        good_crystals=[]
        index=0
        for c in check_list:
            print "CHECKLIST=",c
            # check_list: c=10 -> single crystal (grid consists of 1)
            if c>0 and c!=10:
                cry=crystals[index]
                x1a,y1a=cry.getXYlist()
                for x1,y1 in zip(x1a,y1a):
                    gfile.write("%8.5f %8.5f\n"%(x1,y1))
                gfile.write("\n\n")
                good_crystals.append(cry)
            index+=1
        gfile.close()

        # Making crystal list for small wedge scheme
        singlefile=open("%s/single.dat"%raster_path,"w")
        single_crystals=[]
        index=0
        for c in check_list:
            if c==10:
                cry=crystals[index]
                x1a,y1a=cry.getXYlist()
                for x1,y1 in zip(x1a,y1a):
                    singlefile.write("%8.5f %8.5f\n"%(x1,y1))
                single_crystals.append(cry)
            index+=1
        singlefile.close()

        print "Initial single crystals",len(single_crystals)

        # make crycodes
        def makeCryCode(x,y,score,imgnum):
            # Adding this to the list of grids
            cx,cy,cz=self.cxyz_2d
            crycodes=CrystalSpot.CrystalSpot(cx,cy,cz,self.phi_face)
            crycodes.addXY(x,y,score,imgnum,isCheck=True)
            return crycodes

        # Clustered crystal -> divided to small wedge data collection
        # This list includes very large or overlapped crystal bunches
        # then "small wedge data collection" was applied 
        bad_index=[]
        # each crystal
        print "Clustered crystals=",len(zutazuta)
        # Loop for each crystal
        for cryindex in range(0,len(zutazuta)):
            x1a,y1a,scorea,imgna=zutazuta[cryindex].getInfo()
            bad_index=[0]*len(x1a)
            print "NUMBER OF GRIDS",cryindex,len(x1a)
            # each grid
            for index1 in range(0,len(x1a)):
                if bad_index[index1]==1:
                    continue
                x1=x1a[index1]
                y1=y1a[index1]
                score1=scorea[index1]
                imgnum1=imgna[index1]
                for index2 in range(index1+1,len(x1a)):
                    print "comparison cry1,cry2=",index1,index2
                    print "bad_index=",bad_index
                    if bad_index[index2]==1:
                        continue
                    x2=x1a[index2]
                    y2=y1a[index2]
                    score2=scorea[index2]
                    imgnum2=imgna[index2]
                    dx=x1-x2
                    dy=y1-y2
                    #print x1,y1,x2,y2,dx,dy
                    dist=math.sqrt(dx*dx+dy*dy)
                    print "distance(%d,%d)=%8.5f mm"%(index1,index2,dist)
                    if dist <= self.vbeam:
                        bad_index[index2]=1
            print "BAD",len(bad_index)
            print "Final bad index=",bad_index
            ncount=0
            for i in range(0,len(bad_index)):
                if bad_index[i]==0:
                    x1a,y1a,scorea,imgna=zutazuta[cryindex].getInfo()
                    x=x1a[i]
                    y=y1a[i]
                    score=scorea[i]
                    imgnum=imgna[i]
                    crycode=makeCryCode(x,y,score,imgnum)
                    single_crystals.append(crycode)
                    ncount+=1
            print "Small wedge points=",ncount
        print "SINGLE :",len(single_crystals)
        print "GOOD   :",len(good_crystals)
        print "PERFECT:",len(perfect_crystals)

        # Single crystal
        sss=open("%s/single_new.dat"%raster_path,"w")
        index=0
        for s in single_crystals:
            x1a,y1a=s.getXYlist()
            for x1,y1 in zip(x1a,y1a):
                sss.write("%8.5f %8.5f\n"%(x1,y1))
        sss.close()

        # Perfect OK crystal
        perfile=open("%s/perfect.dat"%raster_path,"w")
        index=0
        for c in check_list:
            if c==0:
                cry=crystals[index]
                x1a,y1a=cry.getXYlist()
                for x1,y1 in zip(x1a,y1a):
                    perfile.write("%8.5f %8.5f\n"%(x1,y1))
                perfile.write("\n\n")
                perfect_crystals.append(cry)
            index+=1
        perfile.close()

        return single_crystals,good_crystals,perfect_crystals

# Iwata root
if __name__ == "__main__":
    import time
    import socket
    import Zoo
    import LoopMeasurement
    import Beamsize
    from html_log_maker import ZooHtmlLog
    import traceback

    sx=0.5925
    sy=-10.5494
    sz=0.1419
    sphi=90.0

    zoo=Zoo.Zoo()
    zoo.connect()
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #ms.connect(("192.168.163.1", 10101))
    ms.connect(("172.24.242.41", 10101))

    #root_dir="/isilon/users/target/target/Staff/kuntaro/171218-kohebi/test14-CPS1010-07/"
    #root_dir="/isilon/users/target/target/Staff/kuntaro/180120-hito/hito-debug3-CPS1010-04/"
    root_dir="/isilon/users/target/target/AutoUsers/180123/xiangyu/xi-KLaT006-15/scan/2d/"
    raster_path="%s/"%root_dir
    
    scan_id="2d"
    lm=LoopMeasurement.LoopMeasurement(ms,root_dir,scan_id)
    cxyz=sx,sy,sz
    #def __init__(self,zoo,lm,cxyz_2d,phi_face,hbeam,vbeam):
    hito=HITO(zoo,lm,cxyz,sphi,10,15)

    raster_path="%s/scan/2d/"%root_dir
    raster_path=root_dir

    #def shiwakeru(self,raster_path,scan_id,thresh_nspots,crysize,max_ncry):
    hito.shiwakeru(raster_path,scan_id,min_score=20,max_score=100,crysize=0.0151,max_ncry=100)

    zoo.disconnect()
    ms.close()
