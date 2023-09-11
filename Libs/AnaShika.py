import sys,os,math,numpy,scipy
import scipy.spatial as ss
import MyException
import time
import datetime
import CrystalSpot

class AnaShika:
    def __init__(self,summary_dat_path,cxyz,phi):
        self.path=summary_dat_path
        self.isRead=False
        self.isKind=False
        self.isList=False
        self.isScoreAbove=False
        self.summary_file="%s/summary.dat"%self.path
        self.DEBUG=False
        self.cen_xyz=cxyz # Goniometer coordinate of this scan
        self.phi=phi

        # DEBUG option
        self.debug=False

        # Threshold for min/max score
        # Crystals with core ranging self.min_score to self.max_score
        # data collection is applied
        self.min_score=10
        self.max_score=1000

    def setSummaryFile(self,filename):
        self.summary_file="%s/%s"%(self.path,filename)

    def waitTillSummary(self):
        print("waitTillSummary")

    def getNgrids(self,prefix,kind="n_spots"):
        # self.score_lines should be obtained
        self.makeList(prefix,kind)
        return len(self.score_lines)

    # 2016/06/27
    # completeness: = (n images in summary.dat / n images collected)
    # timeout: waiting time of output file
    def readSummary(self,scan_id,nimages_all,comp_thresh,timeout=120):
        starttime=datetime.datetime.now()
        prefix="%s_"%scan_id
        # Waitinf for the generation of summary.dat file
        while(1):
            print("Waiting for generating %s"%self.summary_file)
            if os.path.exists(self.summary_file)==False:
                    time.sleep(3.0)
            else:
                print("%s can be read now!!"%self.summary_file)
                break

        # Checking completeness
        while(1):
            self.lines=open(self.summary_file,"r").readlines()
            self.isRead=True
            self.extractKind(kind="n_spots")
            n_read=len(self.score_lines)
            current_ngrids=self.getNgrids(prefix)
            print("Current=",current_ngrids,"All=",nimages_all)
            completeness=float(current_ngrids)/float(nimages_all)
            print("cmp=",completeness)
            if completeness > comp_thresh:
                break
            else:
                currtime=datetime.datetime.now()
                print(currtime)
                if (currtime-starttime).seconds > timeout:
                    raise MyException.MyException("readSummary: summary.dat was not filled < 80%")
                else:
                    time.sleep(10.0)
        self.isRead=True

    def extractKind(self,kind="n_spots"):
        if self.isRead==False:
            self.readSummary()
        # score_lines:
        # lines including targeted "kind"
        # kind: scores on SHIKA
        self.score_lines=[]
        for line in self.lines:
            #print "extractKind:",line
            if line.rfind(kind)!=-1:
                self.score_lines.append(line)
        if self.DEBUG: print(self.score_lines)
        self.isKind=True

    # summary.dat includes "x y score imagename"
    # From 'imagename' in summary.dat, image number can be
    # extracted.
    def getImgNumFromImgName(self,imgname):
        i=imgname.rfind("_")
        j=imgname.rfind(".")
        numchar=imgname[i+1:j]
        num=int(numchar)
        return num

    def makeList(self,prefix,kind="n_spots"):
        # self.score_lines should be obtained
        if self.isKind==False:
            self.extractKind(kind)
        if self.DEBUG: print(self.score_lines)
        self.x=[]
        self.y=[]
        self.v=[]
        self.imgNumList=[]
        for line in self.score_lines:
            cols=line.split()
            tmp_prefix=cols[0]
            if self.DEBUG: print("DEBUG:",tmp_prefix,prefix)
            if tmp_prefix!=prefix:
                if self.debug==True:
                    print("skip: sum:%s and input:%s"%(tmp_prefix,prefix))
                continue
            tmp_x=float(cols[1])
            tmp_y=float(cols[2])
            tmp_score=float(cols[4])
            self.x.append(tmp_x)
            self.y.append(tmp_y)
            self.v.append(tmp_score)
            self.imgNumList.append(self.getImgNumFromImgName(cols[5]))
        self.isList=True

    def reProcess(self,prefix,kind):
        self.score_good=[]
        self.extractKind(kind)
        self.makeList(prefix,kind)
        self.listScoreAbove(prefix,kind)

    # 2018/01/25 range setting for many overlapped crystals
    def reProcessMinMax(self,prefix,kind):
        self.score_good=[]
        self.extractKind(kind)
        self.makeList(prefix,kind)
        self.listScoreBetween(prefix,kind)

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
        print("AnaSHIKA.getTotalScore starts")
        self.min_score=0.0
        self.reProcess(prefix,kind)
        total_score=0

        # All of grids in this scan will be analyzed
        max_score=-9999.9999
        print("SCORE_GOOD len=",len(self.score_good))
        for i in numpy.arange(0,len(self.score_good)):
                x1,y1,score1,imgnum=self.score_good[i]
                total_score+=score1

        print("AnaSHIKA.getTotalScore ends")

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

        print("GRAV",grav_xy)

        smallest_dist=999.999
        co="none"
        for co_name,corner in zip(["LU","LD","RU","RD"],[lu,ld,ru,rd]):
            tmp_dist=calcDistance(grav_xy,corner)
            if tmp_dist < smallest_dist:
                smallest_dist=tmp_dist
                co=co_name
                print(smallest_dist,co_name)
        print("Gravity center is near by ",co)
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

        print("LENGTH of GOOD SCORES=",len(self.score_good))
        if len(self.score_good)==0:
            raise MyException.MyException("findNearestGrid: No good grids.")
        # All of grids in this scan will be analyzed
        shortest_dist=9999.9999
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum=self.score_good[i]
            curr_xy=x1,y1
            tmp_dist=calcDistance(curr_xy,target_corner)
            print("Checked and distance",x1,y1,tmp_dist)
            if tmp_dist < shortest_dist:
                real_x=x1
                real_y=y1
                real_i=imgnum
                shortest_dist=tmp_dist

                x,y,z=self.cen_xyz
                crycode=CrystalSpot.CrystalSpot(x,y,z,self.phi)
        crycode.setDiffscanLog(raster_path)
        fx,fy,fz=crycode.getXYZ(real_i)

        print("findNearestGrid:",fx,fy,fz)
        return fx,fy,fz

    def make2Dmap(self):
        # step x
        self.step_x=self.x[0]-self.x[1]
        # step y
        for tmpy in self.y:
            print(tmpy)
        print(self.step_x)
        nx=numpy.array(self.x)
        minx=nx.min()
        maxx=nx.max()
        stepx=maxx-minx
        print(minx,maxx)

        ny=numpy.array(self.y)
        miny=ny.min()
        maxy=ny.max()
        stepy=maxy-miny
        print(miny,maxy)
        print(stepx,stepy)

    def listScoreAbove(self,prefix,kind="n_spots"):
        if self.isList==False:
            self.makeList(prefix,kind)

        if self.DEBUG: print(self.x,self.y,self.v)
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

        if self.DEBUG: print(self.x,self.y,self.v)
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
                    print("GOOD",x1,y1,x2,y2)
            i+=1

    def analFromOneGrid(self,x1,y1,score1,imgnum1,dist_thresh):
        # Adding this to the list of grids
        x,y,z=self.cen_xyz
        crycodes=CrystalSpot.CrystalSpot(x,y,z,self.phi)

        # This is the first grid of this crystal
        print("The first coordinate=",x1,y1)
        crycodes.addXY(x1,y1,score1,imgnum1,isCheck=True)

        # Good score list : self.score_good
        # x1,y1,score1=each_compo_of_score_good
        print("LEN GOOD_SCORE=%5d"%len(self.score_good))
        nscore_good=len(self.score_good)

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
                if d_dist < 0.0:
                    print("Adding: The second coordinate=",x2,y2)
                    crycodes.addXY(x2,y2,score2,imgnum2,isCheck=False)
                    self.score_good[i]=x2,y2,0,imgnum2
                    n_count+=1
                else:
                    continue
        print("Grids nearby the first one:%5d"%n_count)
        print("Start into the second")

        # After finding near grids on the initial 'one point' (x1,y1)
        # Extended crystal grids will be investigated in the following
        # grids.
        while(1):
            if self.DEBUG: print("Unchecked list loop!(Top of while)")
            unchecked_list=crycodes.getUnchecked()
            print("Unchecked list loop : length=",len(unchecked_list))
            #crycodes.printAll()
            if self.DEBUG: print("### All of them will be investigated ########")
            if self.DEBUG: print(unchecked_list,len(unchecked_list))
            if self.DEBUG: print("##################")
            if len(unchecked_list)==0: 
                crycodes.getTotalScore()
                return crycodes
            for un in unchecked_list:
                x1,y1,score1=un
                if self.DEBUG: print("KITEN is now: ",x1,y1)
                if self.DEBUG: print("Searching ",x1,y1," grids")
                for i in numpy.arange(0,nscore_good):
                    x2,y2,score2,imgnum2=self.score_good[i]
                    if score2==0.0:
                        continue
                    else:
                        tmp_dist=self.calcDist(x1,y1,x2,y2)
                        d_dist=tmp_dist-float(dist_thresh)
                        if self.DEBUG: print("KITEN=",x1,y1,"COMP=",x2,y2," DIFF=",d_dist)
                        if d_dist < 0.0:
                            if self.DEBUG: print("Adding: The second coordinate=",x2,y2)
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
        print("LENGTH OF GOOD:",llll)

        for i in numpy.arange(0,llll):
            x1,y1,score1,imgnum1=self.score_good[i]
            print("THE TARGET GRID(findCrystals):",x1,y1,score1,imgnum1)
            if score1==0.0:
                continue
            score_save=score1
            self.score_good[i]=x1,y1,0.0,imgnum1
            crycodes=self.analFromOneGrid(x1,y1,score_save,imgnum1,dist_thresh)
            self.crystals.append(crycodes)

        print("####### findCrystals %2d crystals were found ################"%len(self.crystals))
        for crycodes in self.crystals:
            crycodes.printAll()
            print("\n\n")
        print("#####################################")
        return self.crystals

    def trees(self):
        xy_array=[]
        for data in self.score_good:
            x,y,s,imgnum=data
            xy_array.append((x,y))
        print("data number=",len(self.score_good))

        rlp3d=numpy.array(xy_array)

        # Making the tree for all RLPs
        self.tree=ss.cKDTree(rlp3d)

        tlist=[]
        # Grouping near reflection list
        for rlp in rlp3d: # For all of independent reflections
            proclist=[]
            dist,idx=self.tree.query(rlp,k=300,p=1,distance_upper_bound=0.011)
            # Bunch of processing
            print("RLP=",rlp)
            print("DIST=",dist)
            print("INDX=",idx)
            for (d,i) in zip(dist,idx):
                    if d==float('inf'):
                            break
                    else:
                            proclist.append(i)
            tlist.append(proclist)

        print("##############################")
        for t in tlist:
            for i in t:
                print(rlp3d[i])
        print("END")

    def aroundTargetPix(self):
        tmp_list=[]
        for j in self.score_good:
            x1,y1,score1=j
            print(x1,y1)

    def setThresh(self,threshold):
        self.min_score=threshold

    def setMinMax(self,min_score,max_score):
        self.min_score=min_score
        self.max_score=max_score

if __name__=="__main__":

	cxyz=(0.7379,   -11.5623,    -0.0629)
	phi=0.0
	prefix="xi-KLaT006-12"
	#summary_dat_path="/isilon/users/target/target/AutoUsers/180123/xiangyu/xi-KLaT006-12/scan/_spotfinder/"
	prefix="2d"
	summary_dat_path="/isilon/users/target/target/AutoUsers/180521/test1/CPS0294-02/scan00/2d/_spotfinder/"

	ashika=AnaShika(summary_dat_path,cxyz,phi)
	nimages_all=100
	completeness=0.95

	ashika.setMinMax(15,100)
	ashika.readSummary(prefix,nimages_all,completeness,timeout=120)
	ashika.reProcessMinMax(prefix,"n_spots")
	crystals=ashika.findCrystals(prefix,kind="n_spots",dist_thresh=0.005)
	#for crystal in crystals:
		#crystal.setDiffscanLog("~/AutoUsers/180521/test1/CPS0294-02/scan00/2d/")
		#crystal.printAll()
        	#print crystal.getPeakCode()

"""
	#def __init__(self,summary_dat_path,cxyz,phi):
	cxyz=(0.7379,   -11.5623,    -0.0629)
	phi=35.0

	spot_finder="./"
	prefix="2d_"
	asss=AnaShika(spot_finder,cxyz,phi)
	nimages_all=10
	completeness=0.95
	asss.readSummary(prefix,nimages_all,completeness,timeout=120)
	dist_thresh=0.0151
	asss.setThresh(5.0)
	crystals=asss.findCrystals(prefix,kind="n_spots",dist_thresh=dist_thresh)

        def compCryScore(x,y):
                a=x.score_total
                b=y.score_total
                #print "SCORE COMPARE",a,b
                if a==b: return 0
                if a<b: return 1
                return -1

        # Sorting better crystals
        # The top of crystal is the best one
        # The bottom is the worst one
        crystals.sort(cmp=compCryScore)

	for crystal in crystals:
		crystal.printAll()
		#print crystal.findCrystalEdge()
		print "\n"
"""
