import sys,os,math,numpy
#import scipy.spatial

class CrystalSpot:
	# 2D coordinates and score
	def __init__(self,cx,cy,cz,phi):
		self.cenx=cx
		self.ceny=cy
		self.cenz=cz
		self.phi=phi

		self.x_list=[]
		self.y_list=[]
		self.score_list=[]
                self.check_list=[]
		self.DEBUG=True

        def printAll(self):
                for i in numpy.arange(0,len(self.x_list)):
                    x=self.x_list[i]
                    y=self.y_list[i]
                    s=float(self.score_list[i])
                    print "%8.4f %8.4f %5.2f"%(x,y,s)

        def check(self,x1,y1):
                for i in numpy.arange(0,len(self.x_list)):
                    x=self.x_list[i]
                    y=self.y_list[i]
                    if self.DEBUG: print "CrystalSpot.check",x,y,x1,y1,self.check_list[i]
                    if x==x1 and y==y1:
                        if self.DEBUG: print "CrystalSpot.check True=",x1,y1
                        self.check_list[i]=True
                        if self.DEBUG: print "Atta!"
                        return 1

                print "something wrong"
                sys.exit(1)

	def addXY(self,x,y,score,isCheck=True):
		self.x_list.append(x)
		self.y_list.append(y)
		self.score_list.append(score)
                self.check_list.append(isCheck)
		return len(self.x_list)

        def getUnchecked(self):
            uncheck_list=[]
            for i in numpy.arange(0,len(self.check_list)):
                if(self.check_list[i]==False):
                    compo=self.x_list[i],self.y_list[i],self.score_list[i]
                    #print "UNUNUNUN",compo
                    uncheck_list.append(compo)
    
            if self.DEBUG: print uncheck_list
            return uncheck_list

	def getGrav(self):
		sum_xbunshi=0.0
		sum_xbunbo=0.0
		sum_ybunshi=0.0
		sum_ybunbo=0.0
		score_sum=0.0

            	for i in numpy.arange(0,len(self.x_list)):
                	x=self.x_list[i]
                	y=self.y_list[i]
			score=self.score_list[i]

			sum_xbunshi+=x*score
			sum_ybunshi+=y*score
			score_sum+=score

		# Calculation of gravity center
		xgrav=sum_xbunshi/score_sum
		ygrav=sum_ybunshi/score_sum

		print "GRAV:",xgrav,ygrav

		return xgrav,ygrav

	def getPeak(self):
                score_max=-9999.9999
		max_x=0.0000
		max_y=0.0000

                for i in numpy.arange(0,len(self.x_list)):
                        x=self.x_list[i]
                        y=self.y_list[i]
                        score=self.score_list[i]

			if score > score_max:
				score_max=score
				max_x=x
				max_y=y

		print "PEAK:",max_x,max_y
                return max_x,max_y

	def findHoriEdges(self):
                score_max=-9999.9999
		max_x=-9999.9999
		min_x=9999.9999
		max_y=-9999.9999
		min_y=9999.9999

                for i in numpy.arange(0,len(self.x_list)):
                        x=self.x_list[i]
                        y=self.y_list[i]
			if x > max_x:
				max_x=x
				max_y=y
			if x < min_x:
				min_x=x
				min_y=y

		print "Horizontal_edges:",max_x,max_y
		print "Horizontal_edges:",min_x,min_y
                return max_x,min_x
		
	def isThere(self,x,y):
		for rx,ry in zip(self.x_list,self.y_list):
			if x==rx and y==ry:
				return True
		return False

class AnaShika:
	def __init__(self,summary_dat_path):
		self.path=summary_dat_path
		self.thresh=10.0
		self.isRead=False
		self.isKind=False
		self.isList=False
		self.isScoreAbove=False
		self.summary_file="%s/summary.dat"%self.path
		self.DEBUG=False

	def setSummaryFile(self,filename):
		self.summary_file=filename

	def readSummary(self):
		self.lines=open(self.summary_file,"r").readlines()
		self.isRead=True

	def extractKind(self,kind="n_spots"):
		if self.isRead==False:
			self.readSummary()
		# score_lines:
		# lines including targeted "kind"
		# kind: scores on SHIKA
		self.score_lines=[]
		for line in self.lines:
			if line.rfind(kind)!=-1:
				self.score_lines.append(line)
		if self.DEBUG: print self.score_lines
		self.isKind=True

	def makeList(self,prefix,kind="n_spots"):
		# self.score_lines should be obtained
		if self.isKind==False:
			self.extractKind(kind)
		if self.DEBUG: print self.score_lines
		self.x=[]
		self.y=[]
		self.v=[]
		for line in self.score_lines:
			cols=line.split()
			tmp_prefix=cols[0]
			if self.DEBUG: print tmp_prefix,prefix
			if tmp_prefix!=prefix:
				print "skip"
				continue
			tmp_x=float(cols[1])
			tmp_y=float(cols[2])
			tmp_score=float(cols[4])
			self.x.append(tmp_x)
			self.y.append(tmp_y)
			self.v.append(tmp_score)
		#for x,y,z in zip(self.x,self.y,self.v):
			#print x,y,z
		self.isList=True

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
		for x,y,score in zip(self.x,self.y,self.v):
			if score >= self.thresh:
				xyzs=x,y,score
				self.score_good.append(xyzs)
				self.zero_pad_list.append(xyzs)
			else:
				score=0
				xyzs=x,y,score
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
				x1,y1,score1=s
				x2,y2,score2=self.score_good[j]
				dist=self.calcDist(x1,y1,x2,y2)

				if 0 < dist and dist < dist_thresh:
					print "GOOD",x1,y1,x2,y2
			i+=1

	def search(self,rx,ry):
		for c1 in self.score_good:
			cx,cy,cs=c1
			dist=self.calcDist(x1,y1,x2,y2)

			if 0 < dist and dist < dist_thresh:
				if crycodes.isThere(x2,y2)==False:
					crycodes.addXY(x2,y2,score2)

        def analFromOneGrid(self,x1,y1,score,dist_thresh):
		crycodes=CrystalSpot(0.0,0.0,0.0,90.0)

                # This is the first grid of this crystal
                crycodes.addXY(x1,y1,score,isCheck=True)

                # Good score list : self.score_good
                # x1,y1,score1=each_compo_of_score_good
		nscore_good=len(self.score_good)

                for i in numpy.arange(0,nscore_good):
                    x2,y2,score2=self.score_good[i]
                    if score2==0.0:
                        continue
                    else:
                        tmp_dist=self.calcDist(x1,y1,x2,y2)
                        if tmp_dist!=0 and tmp_dist < dist_thresh:
                            print "Adding the code!"
                            print crycodes.addXY(x2,y2,score2,isCheck=False)
                            self.score_good[i]=x2,y2,0

                while(1):
                    if self.DEBUG: print "Unchecked list loop!(Top of while)"
                    unchecked_list=crycodes.getUnchecked()
                    crycodes.printAll()
                    if self.DEBUG: print "### All of them will be investigated ########"
                    if self.DEBUG: print unchecked_list
                    if self.DEBUG: print "##################"
                    if len(unchecked_list)==0: 
                        return crycodes
                    for un in unchecked_list:
                        x1,y1,score1=un
                        if self.DEBUG: print "Searching ",x1,y1," grids"
                        for i in numpy.arange(0,nscore_good):
                            x2,y2,score2=self.score_good[i]
                            if score2==0.0:
                                continue
                            else:
                                tmp_dist=self.calcDist(x1,y1,x2,y2)
                                if tmp_dist!=0 and tmp_dist < dist_thresh:
                                    if self.DEBUG: print "Adding the code!"
                                    if self.DEBUG: print crycodes.addXY(x2,y2,score2,isCheck=False)
                                    self.score_good[i]=x2,y2,0
                        # This code is already checked -> Flag is turned off
                        crycodes.check(x1,y1)

	def findCrystals(self,prefix,kind="n_spots",dist_thresh=0.01001,score_thresh=10):
		# Crystal list
		self.crystals=[]
		self.thresh=score_thresh

		if self.isScoreAbove==False:
			self.listScoreAbove(prefix,kind)

		cnt=0
		llll=len(self.score_good)

		for i in numpy.arange(0,llll):
			x1,y1,score1=self.score_good[i]
                        if score1==0.0:
                            continue
                        score_save=score1
                        self.score_good[i]=x1,y1,0.0
                        crycodes=self.analFromOneGrid(x1,y1,score_save,dist_thresh)
                        self.crystals.append(crycodes)

                print "#####################################"
                for crycodes in self.crystals:
                    crycodes.printAll()
                    print "\n\n"
                print "#####################################"
		return self.crystals

	def trees(self):
		xy_array=[]
		for data in self.score_good:
			x,y,s=data
			xy_array.append((x,y))

                rlp3d=numpy.array(xy_array)

                # Making the tree for all RLPs
                self.tree=scipy.spatial.cKDTree(rlp3d)

                tlist=[]
                # Grouping near reflection list
                for rlp in rlp3d: # For all of independent reflections
                        proclist=[]
                        dist,idx=self.tree.query(
                                rlp,k=300,p=1,distance_upper_bound=0.011)
                        # Bunch of processing
			print rlp,dist,idx

                        for (d,i) in zip(dist,idx):
                                if d==float('inf'):
                                        break
                                else:
                                        proclist.append(i)
                        tlist.append(proclist)

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
		self.thresh=threshold

if __name__=="__main__":
	#asss=AnaShika("/isilon/users/target/target/Staff/kuntaro/Brian/150920/xi-KLaT012-16/scan/_spotfinder")

	asss=AnaShika("./")
	asss.setSummaryFile(sys.argv[1])
	prefix="toyoda-1010-05_"
	prefix="xiangyu-KLaT003-08_"
	prefix="rasmas_"

	#asss.makeList(prefix,kind="n_spots")
	#asss.listScoreAbove(prefix,kind="n_spots")
	#asss.anadis(prefix)
	#asss.findCrystals(prefix)
	#asss.make2Dmap()
	#asss.test("toyoda-1010-05_")
	#asss.anadis(prefix)
	#def findCrystals(self,prefix,kind="n_spots",dist_thresh=0.01001):
	asss.setThresh(15)
	crystals=asss.findCrystals(prefix,dist_thresh=0.20)

	pfile=open("peak.dat","w")
	gfile=open("grav.dat","w")
	for crystal in crystals:
		print "======= START ======"
	        crystal.findHoriEdges()
		gx,gy=crystal.getGrav()
		px,py=crystal.getPeak()
	        pfile.write("%8.5f %8.5f\n"%(px,py))
	        gfile.write("%8.5f %8.5f\n"%(gx,gy))
		print "======= END ======"

	pfile.close()
	gfile.close()
