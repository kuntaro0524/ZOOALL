import sys,os,math
import DiffscanLog

class ScanData:

	def __init__(self,diffscanlog,summarydat):
		self.diffscanlog=diffscanlog
		self.summarydat=summarydat
		self.isInit=False

	def init(self,scan_index=0):
		dl=DiffscanLog.DiffscanLog(self.diffscanlog)
		xyzlist=dl.getCodeList(scan_index)

		lines=open(self.summarydat,"r").readlines()
		plines=open(self.diffscanlog,"r").readlines()

		self.datalist=[]
		for line in lines:
			if line.rfind("n_spots")!=-1:
				cols=line.split()
				#print cols
				prefix=cols[0]
				rx=float(cols[1])
				ry=float(cols[2])
				score=int(cols[4])
				img=cols[5]
				imgnum=int(img.replace(prefix,"").replace(".img",""))
				dddd=xyzlist[imgnum-1]
				p,q,x,y,z=dddd
				self.datalist.append((prefix,rx,ry,x,y,z,score,img,imgnum))
		
		self.datalist.sort(key=lambda x:x[8])
		for data in self.datalist:
			print data

	# anatype=""
	def makeGoodGridList(self,threshold):
		self.good_grids=[]
		for d in self.datalist:
			prefix,rx,ry,x,y,z,score,img,imgnum=d
			if score > threshold:
				self.good_grids.append(d)

		print len(self.good_grids)

	def findGridBunch(self):

if __name__=="__main__":
	sd=ScanData("./diffscan.log","./summary.dat")
	sd.init()
	sd.makeGoodGridList(10)
