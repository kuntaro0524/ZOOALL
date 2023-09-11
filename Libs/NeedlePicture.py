import sys
import Image
import numpy
from numpy import *
from AnalyzePeak import *

class NeedlePicture:
	def __init__(self,filename):
		self.filename=filename
		self.isPrep=False

	#self readAsArray(self):
	def prep(self):
                self.im=Image.open(self.filename)
                self.newi=self.im.convert("L")
                self.pix=self.newi.load()
		self.hsize=self.im.size[0]
		self.vsize=self.im.size[1]
		self.isPrep=True

	def getSize(self):
		return self.im.size

        def getGreyPix(self):
                #total+=self.pix[x,y]
		return self.pix

	def getVertLine(self,horipix):
		if self.isPrep==False:
			self.prep()

		#print self.hsize,self.vsize
		xlist=[]
		ylist=[]
		for j in range(0,self.vsize):
			x=j+1
			y=-self.pix[horipix,j]
			xlist.append(x)
			ylist.append(y)

		return xlist,ylist

	def getCenterFWHM(self):
		x,y=self.getVertLine(320)
		ana=AnalyzePeak("test")

		px=ana.getPylabArray(x)
		ty=ana.getPylabArray(y)
		minI=ty.min()

		newy=[]
		for y in ty:
			newy.append(y-minI)

		py=ana.getPylabArray(newy)

		# For DEBUG
		#for x,y in zip(px,py):
			#print x,y

		######################################################
		# NOTE 140528
		# FWHM & Center are calculated from line profile
		# at 320 pix coordinate in horizontal axis.
		# And profile is very noisy on PPM file captured
		# with VIDEOSRV.
		# Smoothing the profile should give more accurate
		# position but now it is not implemented.
		# Current version find a half value of the
		# peak profile, thus, 2 points.
		# Found x coordinates are averaged and utilized 
		# as center position.
		# Additionally, FWHM is a distance of the 2 codes.
		######################################################
		fwhm,center=ana.calcFWHM_PPM(px,py)
		print("FWHM=",fwhm,"Center=",center)

		# Obsoleted on 140528 by K.Hirata
		#fwhm,center=ana.calcFWHM(px,py)
		#fwhm,center=ana.newFWHM2(px,py)
		return fwhm,center

if __name__=="__main__":
	np=NeedlePicture(sys.argv[1])
	fwhm,center=np.getCenterFWHM()

	#print fwhm,center
	print(center)

        # Pixel resolution
        pix2um_highz=0.07125   # [um/pixel]
        pix2um_highy=0.07327   # [um/pixel]

	fwhm_um=pix2um_highz*fwhm
	center_um=pix2um_highz*(center-240)

	print("%12.5f %12.5f"%(fwhm_um,center_um))
