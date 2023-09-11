import sys,os,math,numpy,scipy
import scipy.spatial as ss
import MyException
import time
import datetime
import DiffscanLog
import SummaryDat
import CrystalSpot

class AnaHeatmap:
    def __init__(self,scan_path,cxyz,phi):
        self.scan_path=scan_path
        self.isRead=False
        self.isKind=False
        self.isList=False
        self.isScoreAbove=False
        self.diffscan_path="%s/"%self.scan_path
        self.summarydat_path="%s/_spotfinder/"%self.scan_path
        self.DEBUG=False
        self.cen_xyz=cxyz # Goniometer coordinate of this scan
        self.phi=phi

        # DEBUG option
        self.debug=True

        # Threshold for min/max score
        # Crystals with core ranging self.min_score to self.max_score
        # data collection is applied
        self.min_score=10
        self.max_score=100

        # prep flag
        self.isPrep=False

    def getDiffscanPath(self):
        return self.diffscan_path

    def prep(self,prefix):
        dl=DiffscanLog.DiffscanLog(self.diffscan_path)
        dl.prep()
        # NDarray (V x H) map from diffscan.log
        # The 1st scan result will be analyzed
        dlmap=dl.getNumpyArray(scan_index=0)
        self.nv,self.nh=dl.getScanDimensions()
        #print "Vertical  =",self.nv
        #print "Horizontal=",self.nh
        # in [mm] steps
        self.v_step,self.h_step=dl.getScanSteps()
        print self.v_step,self.h_step
        nimages_all=self.nv*self.nh

        # From summary.dat
        # score heat map will be extracted
        sumdat=SummaryDat.SummaryDat(self.summarydat_path,self.cen_xyz,self.phi,self.nv,self.nh)
        sumdat.readSummary(prefix,nimages_all,1.00,timeout=120)
        # Score is arrayed to numpy.ndarray[N_Vertical,N_Horizontal]
        tmp_heatmap=sumdat.process("n_spots")

        # Checking the heat map
        new_list=[]
        for v in range(0,self.nv):
            for h in range(0,self.nh):
                # diffscan.log map
                scanindex,imgnum,x,y,z=dlmap[v,h]
                new_list.append((scanindex,imgnum,x,y,z,tmp_heatmap[v,h]))
                #print h,v,tmp_heatmap[v,h]

        # ND array for XYZ coordinate(from diffscan.log)
        aa=numpy.array(new_list)
        self.heatmap=numpy.reshape(aa,(self.nv,self.nh,6))

        return self.heatmap

    def findRegions(self,um_square,score_thresh=10):
        # Horizontal step in mm
        h_step=self.h_step
        v_step=self.v_step
        print h_step,v_step

        # From center coordinate
        # half of um_square  in [mm]
        h_half=um_square/2.0/1000.0
        v_half=um_square/2.0/1000.0
        nh_half=int(h_half/h_step)+1
        nv_half=int(v_half/v_step)+1

        print nh_half,nv_half

        n_skip=0
        n_good=0
        # Finding good center
        cen_cand=[]
        # for all v,h grids
        for v in range(0,self.nv):
            for h in range(0,self.nh):
                if self.debug==True:
                    scanindex,imgnum,x,y,z,score=self.heatmap[v,h]
                    print "All ",x,y,z,score
                cenv=v
                cenh=h
                # crystal edge and cannot get region
                if cenv-nv_half < 0:
                    n_skip+=1
                    continue
                if cenh-nh_half < 0:
                    n_skip+=1
                    continue
                if cenv+nv_half >= self.nv:
                    n_skip+=1
                    continue
                if cenh+nh_half >= self.nh:
                    n_skip+=1
                    continue
                # grids those are not in 'edge' of the heatmap
                scanindex,imgnum,x,y,z,score=self.heatmap[v,h]
                # checking the score 
                if score > score_thresh:
                    n_good+=1
                    # Center candidate list is updated
                    cen_cand.append((v,h))
                    print "Center candidate=",v,h,imgnum,x,y,z,score
        print n_skip,n_good
        # Check if all of surrounded pixels are good or not
        good_center=[]
        # still grid coordinates are 'integer indices'
        for cenv,cenh in cen_cand:
            # grid coordinates at the corners
            ed_h1=cenh-nh_half # horizontal left edge
            ed_h2=cenh+nh_half # horizontal right edge
            ed_v1=cenv-nv_half # vertical bottom edge
            ed_v2=cenv+nv_half # vertical top edge

            # All points 
            n_points=(ed_v2-ed_v1+1)*(ed_h2-ed_h1+1)
            print "Square info(center,corners,npoints)=",cenv,cenh,ed_h1,ed_h2,ed_v1,ed_v2,n_points
            n_goods=0
            # Vertical loop
            for v in range(ed_v1,ed_v2+1):
                # Horizontal loop
                for h in range(ed_h1,ed_h2+1):
                    # Get grid information
                    scanindex,imgnum,x,y,z,score=self.heatmap[v,h]
                    #print "CURRENT_GRID=",cenv,cenh,v,h,score
                    # Even if one pixel has score under the threshold
                    # this candidate is not good square
                    if score < score_thresh:
                        print "NG=",v,h,score
                        break
                    # Still good pixel
                    else:
                        # Count grids
                        n_goods+=1
                        continue
                #break  # required?? 2018/05/30 removed

            # Really good center
            if n_goods==n_points:
                print "GOOD_CENTER=",cenv,cenh,n_goods
                scanindex,imgnum,x,y,z,score=self.heatmap[cenv,cenh]
                good_center.append((x,y,z))
                # Flag is turned off when this is good square 
                for v in range(ed_v1,ed_v2+1):
                    for h in range(ed_h1,ed_h2+1):
                        scanindex,imgnum,x,y,z,score=self.heatmap[v,h]
                        self.heatmap[v,h]=scanindex,imgnum,x,y,z,-1
                        if score < score_thresh:
                            print "Something wrong",x,y,z,score
                            sys.exit(1)
                        else:
                            print "GOOOOD",x,y,z,score

        return good_center
        #self.isPrep=True

    # mode: Multi
    def searchMulti(self,prefix,score_tresh,dist_thresh):
        if self.isPrep==False:
            self.prep(prefix)

        # For searching good crystals for v in range(0,self.nv):
        multi_tmp=[]
        kdtree_map=[]
        for h in range(0,self.nh):
            for v in range(0,self.nv):
                scanindex,imgnum,x,y,z,score=self.heatmap[v,h]
                if score>score_thresh:
                    print self.heatmap[v,h]

        aa=numpy.array(new_list)
        self.heatmap=numpy.reshape(aa,(self.nv,self.nh,6))

    def checkMulti(self,v,h,dist_thresh):
        # horizontal check
        # if horizontal step is 0.01 mm and dist_thresh is 0.015mm
        # what should we treat?
        # CASE1: threshold = 0.015 mm
        # horizontal 1 grids      -> 0.01  mm crystal -> Okay
        # horizontal 2 grids      -> 0.02  mm crystal -> NG
        # vertical   1 grids      -> 0.015 mm crystal -> NG but should be okay
        # vertical   2 grids      -> 0.030 mm crystal -> NG

        # CASE2: threshold = 0.020 mm
        # horizontal 2 grids -> 0.02 mm crystal -> Okay
        # horizontal 3 grids -> 0.03 mm crystal -> NG
        # vertical   2 grids -> 0.03 mm crystal -> NG
        # CASE3: threshold = 0.020 mm
        # horizontal 3 grids -> 0.03 mm crystal -> not exceeds 0.020 mm -> 2 grids as single crystal
        print "TEST"

    def getCorners(self,prefix,kind="n_spots"):
        self.min_score=0.0
        self.reProcess(prefix,kind)
        
        # corner coordinate
        ymin=xmin=9999.9999
        ymax=xmax=-9999.9999

        # All of grids in this scan will be analyzed
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum1=self.score_good[i]
            if x1 <= xmin:
                xmin=x1
            if x1 > xmax:
                xmax=x1
            if y1 <= ymin:
                ymin=y1
            if y1 > ymax:
                ymax=y1
        # L: Left   U: Down
        # R: Right  D: Up
        lu=(xmin,ymax)
        ld=(xmin,ymin)
        ru=(xmax,ymax)
        rd=(xmax,ymin)

        return lu,ld,ru,rd

    def getMaxScore(self,prefix,kind="n_spots"):
        self.min_score=0.0
        self.reProcess(prefix,kind)

        # All of grids in this scan will be analyzed
        max_score=-9999.9999
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum=self.score_good[i]
            if score1 > max_score:
                max_score=score1
        return max_score

    def getMaxScoreImageNum(self,prefix,kind="n_spots"):
        self.min_score=0.0
        self.reProcess(prefix,kind)

        # All of grids in this scan will be analyzed
        max_score=-9999.9999
        i_max=-99999
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum=self.score_good[i]
            if score1 > max_score:
                max_score=score1
                i_max=imgnum
        return i_max,max_score

    def getTotalScore(self,prefix,kind="n_spots"):
        print "AnaSHIKA.getTotalScore starts"
        self.min_score=0.0
        self.reProcess(prefix,kind)
        total_score=0

        # All of grids in this scan will be analyzed
        max_score=-9999.9999
        print "SCORE_GOOD len=",len(self.score_good)
        for i in numpy.arange(0,len(self.score_good)):
                x1,y1,score1,imgnum=self.score_good[i]
        total_score+=score1

        print "AnaSHIKA.getTotalScore ends"

        return total_score

    def getGravCenter(self,prefix,kind="n_spots"):
        self.min_score=0.0
        self.reProcess(prefix,kind)

        # All of grids in this scan will be analyzed
        sum_score=0.0
        sum_x_score=0.0
        sum_y_score=0.0
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum1=self.score_good[i]
            sum_score+=score1
            sum_x_score+=x1*score1
            sum_y_score+=y1*score1

        grav_x=sum_x_score/sum_score
        grav_y=sum_y_score/sum_score

        return (grav_x,grav_y)

    def getTargetCorner(self,lu,ld,ru,rd,grav_xy):
        def calcDistance(code1,code2):
            x1,y1=code1
            x2,y2=code2
            dx=x1-x2
            dy=y1-y2
            dist=math.sqrt(dx*dx+dy*dy)
            return dist

        print "GRAV",grav_xy

        smallest_dist=999.999
        co="none"
        for co_name,corner in zip(["LU","LD","RU","RD"],[lu,ld,ru,rd]):
            tmp_dist=calcDistance(grav_xy,corner)
            if tmp_dist < smallest_dist:
                smallest_dist=tmp_dist
                co=co_name
                print smallest_dist,co_name
        print "Gravity center is near by ",co
        if co == "LU":
            target_corner=rd
        if co == "LD":
            target_corner=ru
        if co == "RU":
            target_corner=ld
        if co == "RD":
            target_corner=lu
        return target_corner

    def findNearestGrid(self,thresh_score,prefix,target_corner,raster_path,kind="n_spots"):
        def calcDistance(code1,code2):
            x1,y1=code1
            x2,y2=code2
            dx=x1-x2
            dy=y1-y2
            dist=math.sqrt(dx*dx+dy*dy)
            return dist

        # Picking grids above thresh_score
        self.min_score=thresh_score
        self.reProcess(prefix,kind)

        print "LENGTH of GOOD SCORES=",len(self.score_good)
        if len(self.score_good)==0:
                        raise MyException.MyException("findNearestGrid: No good grids.")

                # All of grids in this scan will be analyzed
        shortest_dist=9999.9999
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum=self.score_good[i]
            curr_xy=x1,y1
            tmp_dist=calcDistance(curr_xy,target_corner)
            print "Checked and distance",x1,y1,tmp_dist
            if tmp_dist < shortest_dist:
                real_x=x1
                real_y=y1
                real_i=imgnum
                shortest_dist=tmp_dist

                x,y,z=self.cen_xyz
                crycode=CrystalSpot.CrystalSpot(x,y,z,self.phi)
        crycode.setDiffscanLog(raster_path)
        fx,fy,fz=crycode.getXYZ(real_i)

        print "findNearestGrid:",fx,fy,fz
        return fx,fy,fz

    def make2Dmap(self):
        # step x
        self.step_x=self.x[0]-self.x[1]
        # step y
        for tmpy in self.y:
            print tmpy
        print self.step_x
        nx=numpy.array(self.x)
        minx=nx.min()
        maxx=nx.max()
        stepx=maxx-minx
        print minx,maxx

        ny=numpy.array(self.y)
        miny=ny.min()
        maxy=ny.max()
        stepy=maxy-miny
        print miny,maxy

        print stepx,stepy

    def listScoreAbove(self,prefix,kind="n_spots"):
        if self.isList==False:
            self.makeList(prefix,kind)

        if self.DEBUG: print self.x,self.y,self.v
        self.zero_pad_list=[]

        self.score_good=[]
        for x,y,score,imgnum in zip(self.x,self.y,self.v,self.imgNumList):
            #print x,y,score
            if score >= self.min_score:
                xyzsi=x,y,score,imgnum
                self.score_good.append(xyzsi)
                self.zero_pad_list.append(xyzsi)
            else:
                score=0
                xyzs=x,y,score,imgnum
                self.zero_pad_list.append(xyzs)
        self.isScoreAbove=True

    def listScoreBetween(self,prefix,kind="n_spots"):
        if self.isList==False:
            self.makeList(prefix,kind)

        if self.DEBUG: print self.x,self.y,self.v
        self.zero_pad_list=[]

        self.score_good=[]
        #print "LISTSCOREBETWEEN",self.min_score,self.max_score
        #print "LENX=",len(self.x)
        for x,y,score,imgnum in zip(self.x,self.y,self.v,self.imgNumList):
            if score >= self.min_score and score <= self.max_score:
                xyzsi=x,y,score,imgnum
                self.score_good.append(xyzsi)
                self.zero_pad_list.append(xyzsi)
                #print "BETWEEN",x,y,score
            else:
                score=0
                xyzs=x,y,score,imgnum
                self.zero_pad_list.append(xyzs)

        self.isScoreAbove=True

    def calcDist(self,x1,y1,x2,y2):
        dx=numpy.fabs(x1-x2)
        dy=numpy.fabs(y1-y2)
        dist=numpy.sqrt(dx*dx+dy*dy)
        return dist

    def analyzeDistance(self,prefix,kind="n_spots",dist_thresh=0.010):
        if self.isScoreAbove==False:
            self.listScoreAbove(prefix,kind)
        i=0
        llll=len(self.score_good)
        for s in self.score_good:
            for j in numpy.arange(0,llll):
                x1,y1,score1,imgnum1=s
                x2,y2,score2,imgnum2=self.score_good[j]
                dist=self.calcDist(x1,y1,x2,y2)

                if 0 < dist and dist < dist_thresh:
                    print "GOOD",x1,y1,x2,y2
            i+=1

    def analFromOneGrid(self,x1,y1,score1,imgnum1,dist_thresh):
        # Adding this to the list of grids
        x,y,z=self.cen_xyz
        crycodes=CrystalSpot.CrystalSpot(x,y,z,self.phi)

        # This is the first grid of this crystal
        print "The first coordinate=",x1,y1
        crycodes.addXY(x1,y1,score1,imgnum1,isCheck=True)

        # Good score list : self.score_good
        # x1,y1,score1=each_compo_of_score_good
        print "LEN GOOD_SCORE=%5d"%len(self.score_good)
        nscore_good=len(self.score_good)

        # DEBUGGING making a list of good score
        #for j in numpy.arange(0,nscore_good):
            #x,y,score,imgnum=self.score_good[j]
            #print "LLLL: %8.3f %8.3f %5d"%(x,y,score)

        # From the first grid (given x1,y1 coordinate)
        # near grids are searched in this loop
        n_count=0
        for i in numpy.arange(0,nscore_good):
            x2,y2,score2,imgnum2=self.score_good[i]
            if score2==0.0:
                continue
            else:
                tmp_dist=self.calcDist(x1,y1,x2,y2)
            d_dist=tmp_dist-float(dist_thresh)
            #print "GRID1=",x1,y1,"GRID2=",x2,y2,"TMP_DIST=",tmp_dist," DIST_THRESH=",dist_thresh," DIFF=",d_dist
            if d_dist < 0.0:
                print "Adding: The second coordinate=",x2,y2
                crycodes.addXY(x2,y2,score2,imgnum2,isCheck=False)
                self.score_good[i]=x2,y2,0,imgnum2
                n_count+=1
            else:
                continue
        print "Grids nearby the first one:%5d"%n_count
        print "Start into the second"

        # After finding near grids on the initial 'one point' (x1,y1)
        # Extended crystal grids will be investigated in the following
        # grids.
        while(1):
            if self.DEBUG: print "Unchecked list loop!(Top of while)"
            unchecked_list=crycodes.getUnchecked()
            print "Unchecked list loop : length=",len(unchecked_list)
            #crycodes.printAll()
            if self.DEBUG: print "### All of them will be investigated ########"
            if self.DEBUG: print unchecked_list,len(unchecked_list)
            if self.DEBUG: print "##################"
            if len(unchecked_list)==0: 
                crycodes.getTotalScore()
                return crycodes
            for un in unchecked_list:
                x1,y1,score1=un
            if self.DEBUG: print "KITEN is now: ",x1,y1
            if self.DEBUG: print "Searching ",x1,y1," grids"
            for i in numpy.arange(0,nscore_good):
                x2,y2,score2,imgnum2=self.score_good[i]
                if score2==0.0:
                    continue
                else:
                    tmp_dist=self.calcDist(x1,y1,x2,y2)
                d_dist=tmp_dist-float(dist_thresh)
                if self.DEBUG: print "KITEN=",x1,y1,"COMP=",x2,y2," DIFF=",d_dist
                if d_dist < 0.0:
                    if self.DEBUG: print "Adding: The second coordinate=",x2,y2
                    crycodes.addXY(x2,y2,score2,imgnum2,isCheck=False)
                    self.score_good[i]=x2,y2,0,imgnum2
                    # This code is already checked -> Flag is turned off
                    crycodes.check(x1,y1)

    # Small wedge scheme: crystal picking is conducted from LoopMeasurement
    # 2018/01/25 score between min/max is implemented
    # this routine calls: reProcessMinMax for making the look-up table
    def findCrystals(self,scan_id,kind="n_spots",dist_thresh=0.01001):
        # Crystal list
        self.crystals=[]

        # prefix
        prefix="%s_"%scan_id

        # Threshold for finding crystals
        self.reProcessMinMax(prefix,kind)

        cnt=0
        llll=len(self.score_good)
        print "LENGTH OF GOOD:",llll

        for i in numpy.arange(0,llll):
            x1,y1,score1,imgnum1=self.score_good[i]
            print "THE TARGET GRID(findCrystals):",x1,y1,score1,imgnum1
            if score1==0.0:
                continue
            score_save=score1
            self.score_good[i]=x1,y1,0.0,imgnum1
            crycodes=self.analFromOneGrid(x1,y1,score_save,imgnum1,dist_thresh)
            self.crystals.append(crycodes)

            print "####### findCrystals %2d crystals were found ################"%len(self.crystals)
            for crycodes in self.crystals:
                crycodes.printAll()
                print "\n\n"
            print "#####################################"
        return self.crystals

    def trees(self):
        xy_array=[]
        for data in self.score_good:
            x,y,s,imgnum=data
            xy_array.append((x,y))
            print "data number=",len(self.score_good)
            rlp3d=numpy.array(xy_array)

            # Making the tree for all RLPs
            self.tree=ss.cKDTree(rlp3d)

            tlist=[]
            # Grouping near reflection list
            for rlp in rlp3d: # For all of independent reflections
                proclist=[]
                dist,idx=self.tree.query(
                    rlp,k=300,p=1,distance_upper_bound=0.011)
            # Bunch of processing
            print "RLP=",rlp
            print "DIST=",dist
            print "INDX=",idx
            for (d,i) in zip(dist,idx):
                    if d==float('inf'):
                            break
                    else:
                            proclist.append(i)
            tlist.append(proclist)

        print "##############################"
        for t in tlist:
            for i in t:
                print rlp3d[i]
            print "END"

    def aroundTargetPix(self):
        tmp_list=[]
        for j in self.score_good:
            x1,y1,score1=j
            print x1,y1

    def setThresh(self,threshold):
        self.min_score=threshold

    def setMinMax(self,min_score,max_score):
        self.min_score=min_score
        self.max_score=max_score

if __name__=="__main__":

    cxyz=(0.7379,   -11.5623,    -0.0629)
    phi=0.0
    prefix="xi-KLaT006-12"
    #scan_path="/isilon/users/target/target/AutoUsers/180123/xiangyu/xi-KLaT006-12/scan/"
    scan_path=sys.argv[1]

    ahm=AnaHeatmap(scan_path,cxyz,phi)

    score_thresh=10
    dist_thresh=0.05
    ahm.searchMulti("CPS0298-01",score_thresh,dist_thresh)

    #lll= ahm.findRegions(50,score_thresh=20)
    #def findRegions(self,um_square,score_thresh=10):
    #for l in lll:
        #print l
