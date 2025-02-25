import numpy
import scipy
import sys
import os
from MyException import *
from numpy import *

class GonioVec:

	def __init__(self):
		self.test=1
		self.vertVec=numpy.array((0,0,0))
		self.horiVec=numpy.array((0,0,0))
		self.origVec=numpy.array((0,0,0))

	def setVertVec(self,x,y,z):
		vec=numpy.array((x,y,z))
		self.vertVec=vec

	def setHoriVec(self,x,y,z):
		vec=numpy.array((x,y,z))
		self.horiVec=vec

	def getHoriLen(self):
		dist=self.calcDist(self.ori_hori)
		return dist

	def setOrigVec(self,x,y,z):
		vec=numpy.array((x,y,z))
		self.origVec=vec

	def calcDist(self,vec):
		return numpy.linalg.norm(vec)

	def makeVecFromXYZ(self,xyz):
		# xyz is 3D array
		vector=numpy.array((xyz[0],xyz[1],xyz[2]))
		return vector

	def makeLineVec(self,start,end):
		# start (x1,y1,z1), end (x2,y2,z2)
		startvec=self.makeVecFromXYZ(start)
		endvec=self.makeVecFromXYZ(end)
		# start -> end vector
		vector=endvec-startvec
		
		return vector

	def makeRDstudy(self,start,end,nstep):
		# 3D vec for horizontal scan
		vector=self.makeLineVec(start,end)
		# step
		uvec=vector/float(nstep)
		# Slow
		start_list=[]
		for idx in range(0,nstep):
			slow_start=idx*uvec+start
			start_list.append(slow_start)
		return start_list

        def makeRotMat(self,phi):
                phirad=numpy.radians(phi)
                rtn=numpy.matrix( (
                        ( cos(phirad), 0.,-sin(phirad)),
                        (     0., 1.,     0.),
                        ( sin(phirad), 0., cos(phirad))
                ) )

                return rtn

        def dot(self,mat,vec):
                return numpy.dot(mat,vec)

        # xyz: coordinate array
        def rotXYZ(self,xyz,phi):
                vec=numpy.array(xyz)
                rotated=self.rotVector(vec,phi)
                idx=0
                newxyz=[]
                for element in rotated.flat:
                        newxyz.append(element)
                return newxyz

        def rotVector(self,vec,phi):
                # vec: numpy vector
                rotmat=self.makeRotMat(phi)
                rotated=dot(rotmat,vec)
                # rotated : numpy vector
                return rotated

	def yattane(self,orig,fast,slow,nfast,nslow):
		if nfast<=1 or nslow<=1:
			raise MyException("Scan number is grater than 1\n")

		# make origin vector
		orivec=self.makeVecFromXYZ(orig)

		# make 2 vectors
		self.fastvec=self.makeLineVec(orig,fast)
		self.slowvec=self.makeLineVec(orig,slow)

		# make unit vector
		self.fast_uvec=self.fastvec/float(nfast-1)
		self.slow_uvec=self.slowvec/float(nslow-1)

		# length of the vectors
		self.fastlen=self.calcDist(self.fast_uvec)
		self.slowlen=self.calcDist(self.slow_uvec)

		if self.fastlen < 0.0005 or self.slowlen <0.0005:
			raise MyException("Scan length is longer than 0.5um\n")

		# make start points
		start_list=[]
		end_list=[]
		for idx in range(0,nslow):
			slow_start=idx*self.slow_uvec+orivec
			start_list.append(slow_start)
			slow_end=slow_start+self.fastvec
			end_list.append(slow_end)

		return start_list,end_list,self.fastlen,self.slowlen

	# coded 2012/06/12 for SACLA experiments
	def testing(self,orig,fast,slow):
		# orig: x,y,z array
		# fast: x,y,z array
		# slow: x,y,z array
		self.fastvec=self.makeLineVec(orig,fast)

		fast_uvec=self.fastvec/10.0

		origlist=[]
		for i in range(0,11):
			origlist.append(orig+float(i)*fast_uvec)
			#print type(orig+float(i)*fast_uvec)

		tmplist=numpy.array(origlist)
		origlist=tmplist.reshape(3,11)
		rotlist=self.rotVector(origlist,30)

		print "ORIG:",origlist.shape,rotlist.shape

		print origlist
		print rotlist

		for i in range(0,11):
			print origlist[:,i]
			print rotlist[:,i]

		#rotlist=[]
		#for i in range(0,1001):
			#print type(self.rotVector(origlist[i],30))
			#rotlist.append(self.rotVector(origlist[i],30))
		#print rotlist

		#for i in range(0,1001):
			#for j in range(0,3):
				#print origlist[i][j],
			#print i,origlist[i],rotlist[i]
			

	def makePlane(self,vstep,hstep):
		self.ori_vert=self.vertVec-self.origVec
		self.ori_hori=self.horiVec-self.origVec

		#print self.calcDist(self.ori_vert)
		#print self.calcDist(self.ori_hori)

		# div step
		div_vert=self.ori_vert/float(vstep-1)
		div_hori=self.ori_hori/float(hstep-1)

		if self.calcDist(div_vert) < 0.0005 or self.calcDist(div_hori) < 0.0005:
			raise MyException("Scan step should be greater than 0.5um!")

		start_points=[]
		end_points=[]
		for i in range(0,vstep):
			vert_origin=self.origVec+div_vert*float(i)
			hori_end=vert_origin+self.ori_hori

			start_points.append(vert_origin)
			end_points.append(hori_end)

		dv=self.calcDist(div_vert)
		dh=self.calcDist(div_hori)
		print "DIV: %8.4f %8.4f [mm]" % (dv,dh)

		return start_points,end_points,dv,dh

	def getXYZ(self,vec):
		print vec[0],vec[1],vec[2]

if __name__=="__main__":

	vecg=GonioVec()

	center=[0,0,0]
	#horiv=

	orig=[0,0,0]
	fast=[0.0,0.00,1.0]
	slow=[0.0,0.21,1.0]

	vecg.testing(orig,fast,slow)

	

	#list=vecg.makeRDstudy(orig,fast,21)
	
	#for comp in list:
		#print comp

####	line vec
	#slow=[0.10,0.0,0.0]

	#nf=11
	#ns=11

	#try :
		
		#slist,elist,flen,slen=vecg.yattane(orig,fast,slow,nf,ns)
		#for i in range(0,len(slist)):
			#print slist[i],elist[i],flen,slen
	#except MyException,e:
		#print e.args[0]


	#for i in range(0,len(start_points)):
		#print start_points[i],end_points[i]

	#try:
		#start_points,end_points=vecg.makePlane(ori,v1,v2,5)
	#except MyException,e:
		#print e.args[0]
		#sys.exit(1)
