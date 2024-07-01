import os
import sys
import math
#from  pylab import *
import socket
import pylab
import numpy
#from numpy import *
from pylab import *
from MyException import *

class DiffscanLog:
	def __init__(self,path,filename="diffscan.log"):
		self.filename="%s/%s"%(path,filename)
		self.lines=[]
		self.nscan=0
		self.allblocks=[] 	# strings of XYZ information
		self.allxyz=[]		# list of (scanID,pointindex,x,y,z)
		self.allstep=[]		# list of (Nv,Nh,step(v),step(h))
		self.isInit=False
		self.debug=False

	########################################3
	# this routine should be called whenever a log is read
	# process
	# 1. read lines
	# 2. count scan jobs
	# 3. make a list of jobs
	########################################3
	def prep(self):
		# Just to read
        	self.readfile()
		# Count number of scans in this diffscan.log
        	self.countScan()
		print "N scan=",self.nscan
		# Making the list of all xyz data
        	self.storeList()
		self.isInit=True
		# Scan dimensionts
		self.storeDimension()
		return self.nscan

	#)
	#) A simple function to read lines
	#)
	def readfile(self):
		print "Reading %s"%self.filename
		ifile=open(self.filename,"r")
		self.lines=ifile.readlines()
		ifile.close()

	# --------
	#) This class function 
	#) 1) compiles each diffraction scan information 
	#)    to a list of a list of strings
	#  --> Brief description
	#  a list "blockline[]" includes lines of each scan
	#  a class variant "self.allblocks[]" include "blockline"
	#
	#  2) Count a number of all jobs
	#  3) make a list of 
	# =======
	# Data access
	# =======
	# self.allblocks[0] -> a list of string lines of the '1st' scan
	# --------
	def countScan(self):
		blockline=[]
		readflag=False

		for line in self.lines:
			if line.find("Diffraction scan")!=-1:
				readflag=True
			# count scan
				self.nscan+=1
				#print "TRUE"
				continue

			if readflag==True and line.find("======")!=-1:
				readflag=False
				#blockline.append(line)
				self.allblocks.append(blockline)
				blockline=[]
				
			if readflag==True:
				blockline.append(line)

		### Acquire nscan
		#print "Current scan #:= %5d"%self.nscan

	#####
	# This class function 'storeList'
	# 1) extracts gonio XYZ information from stored 'string' information 'allblocks'
	# 2) stored float values into the class variant 'allxyz' 
	#    (Data structure) list of '[scan number],[scan index],[x],[y],[z]'
	#####
	def storeList(self):
		#print self.allblocks
		#print len(self.allblocks)
		code=[]
		for i in range(0,len(self.allblocks)):
			readflag=False
			#print "=====SCAN NO. %d ====="%i
			for line in self.allblocks[i]:
				#if line.find("Camera")!=-1:
				if line.find("Frame")!=-1:
					readflag=True
					continue
				if readflag:
					cols=line.split()
					if len(cols)==4:
						#print line
						idx=int(cols[0])
						cx=float(cols[1])
						cy=float(cols[2])
						cz=float(cols[3])
						ds=i,idx,cx,cy,cz
						code.append(ds)
			self.allxyz.append(code)
			code=[]

		#print "GETLIST"
		##print self.allxyz
		#print "GETLIST"

	def storeDimension(self):
		if self.isInit==False:
			self.prep()
		
		for i in range(0,len(self.allblocks)):
			readflag=False
			for line in self.allblocks[i]:
				if line.find("Vertical")!=-1:
					cols=line.split()
					nv= int(cols[5])
					#sstep=cols[7][:len(cols[7])-2]
					sstep=cols[7]
					vs= float(sstep)
					
				elif line.find("Horizontal")!=-1:
					cols=line.split()
					nh= int(cols[5])
					sstep=cols[7]
					hs= float(sstep)
					break
			ll=nv,nh,vs,hs
			self.allstep.append(ll)

	# return the 'index'th block (IDX,X,Y,Z)
	def getBlock(self,index):
		tmpxyz=[]
		for block in self.allxyz:
			for xyz in block:
				if xyz[0]==index:
					scan_index=int(xyz[0])
					tmp_imgnum=int(xyz[1])
					tx=float(xyz[2])
					ty=float(xyz[3])
					tz=float(xyz[4])
					list=scan_index,tmp_imgnum,tx,ty,tz
					tmpxyz.append(list)
					#print "%5d %8.4f %8.4f %8.4f"%(ti,tx,ty,tz)
		return tmpxyz

	def getNewestScan(self):
		if self.isInit==False:
			self.prep()
		#print self.allblocks
		idx=self.nscan-1
		#print self.allstep[idx]
		#print self.allxyz[idx]
		return self.allstep[idx],self.getBlock(idx)

	def get2Didx(self,ipoint,nv,nh):
		v=ipoint/(nh+1)+1
		h=ipoint-((v-1)*nh)
		#print v,h
		return v,h

	def getCodeList(self,iscan):
		return(self.getBlock(iscan))

	def getPosition(self,iscan,ipoint):
		iscan=iscan-1
		ipoint=ipoint-1

		xyzlist=self.getBlock(iscan)

		x=y=z=0.0
		for i in range(0,len(xyzlist)):
			#if xyzlist[1]==ipoint:
			print xyzlist[1]
			if int(xyzlist[i][1])==ipoint:
				x= xyzlist[i][2]
				y= xyzlist[i][3]
				z= xyzlist[i][4]
				break

		return float(x),float(y),float(z)

	def getPrevious(self):
		idx=self.nscan-2
		if idx<0:
			print "You may not have a previous scan yet."
			return
		else:
			self.getBlock(idx)

	def getXYZindex(self,frame_index,scan_index=0):
		if self.debug==True:
			print "getXYZindex: Finding FRAME_INDEX=",frame_index
		if self.isInit==False:
			self.prep()
		xyzlist=self.getCodeList(scan_index)
		n_xyz=len(xyzlist)

		if self.debug==True:
			print "getXYZindex: n_xyz=",n_xyz
			print "getXYZindex: frame_index=",frame_index

		if frame_index > n_xyz or frame_index < 0:
			raise MyException("getXYZindex: invalid index number")

		else:
			for xyz in xyzlist:
				frame_index_tmp=xyz[1]
				if frame_index_tmp==frame_index:
					s_index,score,x,y,z=xyz
					gxyz=x,y,z
					return gxyz

	def getScanDimensions(self):
		nv,nh,stepv,steph=self.allstep[0]
		return nv,nh

	def getScanSteps(self):
		if self.isInit==False:
			self.prep()
		nv,nh,stepv,steph=self.allstep[0]
		return stepv,steph

	def getNumpyArray(self,scan_index=0):
		if self.isInit==False:
			self.prep()
		xyzlist=self.getCodeList(scan_index)
		nv,nh,stepv,steph=self.allstep[0]
		print self.allstep[0]
		print "horizontal=",nh,stepv
		print "vertical  =",nv,steph

		ar=numpy.array(xyzlist)
		ma=numpy.reshape(ar,(nv,nh,5))

                # Vertical direction
                for iv in range(0,nv):
                        if iv % 2 != 0:
                                hline=ma[iv,]
                                #print "ORIG=",ma[iv,],ma[iv,].shape
                                #newline=numpy.fliplr([hline])[0]
                                newline=hline[::-1,]
                                ma[iv,]=newline
                                #print "INV=",ma[iv,]

		"""
		for v in range(0,nv):
			for h in range(0,nh):
                                scan_index,tmp_imgnum,tx,ty,tz=ma[v,h]
				print "GNA:(H,V)=(%5d,%5d) %5d %8.3f %8.3f %8.3f"%(h,v,tmp_imgnum,tx,ty,tz)
		"""

		return ma

if __name__=="__main__":
	diffpath="/isilon/users/target/target/AutoUsers/180123/xiangyu/xi-KLaT005-04/scan/"
	#dl=DiffscanLog("/isilon/users/target/target/Staff/kuntaro/160726/JidoHeli//klys9-CPS1013-01/scan/lv-fin-02/")
	dl=DiffscanLog(diffpath)
	dl.prep()
	ma=dl.getNumpyArray(scan_index=0)

	print ma.shape

	#print dl.getXYZindex(7)

	#p,q= dl.getNewestScan()
	#xyzlist=dl.getCodeList(0)

	#for xyz in xyzlist:
		#print xyz

#map(lambda x: x[1][:-1], table) # last indexes will be alive

#lambda x: 3*math.exp(-(30-x)**2/20.)

		#print "%8.5f"%(xyz[3])

	#dl.storeDimension()
	#nv,nh,sv,sh=p
	#print nv,nh,sv,sh

	#n=nv*nh
	#for i in range(1,n+1):
		#print i
		#dl.get2Didx(i,nv,nh)
	#print dl.getPosition(3,5)

	#print "PREVIOUS"
	#dl.getPrevious()
