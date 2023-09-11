import sys,os,math,numpy

class AnaShika:
	def __init__(self,path):
		self.path=path
		self.thresh=10.0
		self.isRead=False
		self.isKind=False
		self.isList=False
		self.isScoreAbove=False

	def readSummary(self):
		summ_file="%s/summary.dat"%self.path
		self.lines=open(summ_file,"r").readlines()
		self.isRead=True

	def extractKind(self,kind="n_spots"):
		if self.isRead==False:
			self.readSummary()
		self.score_lines=[]
		for line in self.lines:
			if line.rfind(kind)!=-1:
				self.score_lines.append(line)
		self.isKind=True

	def makeList(self,prefix,kind="n_spots"):
		if self.isKind==False:
			self.extractKind(kind)
		#print self.score_lines
		self.x=[]
		self.y=[]
		self.v=[]
		for line in self.score_lines:
			cols=line.split()
			tmp_prefix=cols[0]
			#print tmp_prefix,prefix
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

		#print self.x,self.y,self.v
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

	def analyzeDistance(self,prefix,kind="n_spots"):
		if self.isScoreAbove==False:
			self.listScoreAbove(prefix,kind)
		i=0
		llll=len(self.score_good)
		print llll
		for s in self.score_good:
			for j in numpy.arange(i+1,llll):
				x1,y1,score1=s
				x2,y2,score2=self.score_good[j]
				dist=self.calcDist(x1,y1,x2,y2)
				#print dist

				if 0 < dist <= 0.010:
					print "GOOD",x1,y1,x2,y2
			i+=1

	def aroundTargetPix(self):
		tmp_list=[]
		for j in self.score_good:
			x1,y1,score1=j
			print x1,y1

	def test(self,prefix,kind="n_spots"):
		if self.isScoreAbove==False:
			self.listScoreAbove(prefix,kind)
		i=0
		nsize=len(self.zero_pad_list)
		for s in self.zero_pad_list:
			x1,y1,score1=s
			print x1,y1,score1

	def setThresh(self,threshold):
		self.thresh=threshold

if __name__=="__main__":
	#asss=AnaShika("/isilon/users/target/target/Staff/kuntaro/Brian/150920/xi-KLaT012-16/scan/_spotfinder")
	asss=AnaShika("./")
	#asss.makeList()
	asss.analyzeDistance("toyoda-1010-05_")
	asss.make2Dmap()
	#asss.test("toyoda-1010-05_")
