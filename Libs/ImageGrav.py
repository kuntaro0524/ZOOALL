import sys
import datetime
from MyException import *
import Image
import ImageDraw,ImageFont
#from myfont import fontPath

class ImageGrav:

	def __init__(self,filename):
		self.filename=filename
		self.isInit=False

	def readFile(self):
		self.im=Image.open(self.filename)
		self.newi=self.im.convert("L")
		self.pix=self.newi.load()

	def getXline(self,xcode):
		# Initialization
		if self.isInit==False:
			self.readFile()
		# Return list
		ylist=[]
		value=[]
		for y in range(0,self.im.size[1]):
			ylist.append(y)
			value.append(self.pix[xcode,y])
		return ylist,value

	def getXY(self):
		im=Image.open(self.filename)
		newi=im.convert("L")
		pix=newi.load()

		# size=(width,height)

		sumpeak=0.0

	# Average
		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				if pix[x,y]<=255:
					sumpeak+=pix[x,y]

		npix=im.size[0]*im.size[1]
		ave=sumpeak/float(npix)

	# Threshold
		thresh=ave
		sumpeak=0.0
		sumx=0.0
		sumy=0.0
		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				if pix[x,y]<thresh:
					sumpeak+=pix[x,y]
					sumx+=pix[x,y]*x
					sumy+=pix[x,y]*y

		# Exception
		if sumpeak==0.0:
			raise MyException("Beam monitor did not catch your beam!!")

		cenx=sumx/sumpeak
		ceny=sumy/sumpeak

		# output log image
		draw=ImageDraw.Draw(im)

		# drawing circle at calculated position
		draw.ellipse((cenx-5,ceny-5,cenx+5,ceny+5),fill=(0,0,0))

		# Date
		dstr="%s"%datetime.datetime.now()
		font=ImageFont.truetype(fontPath,14)

		str2="Pixel    (Y,Z)=(%8.2f,%8.2f)[pix]"%(cenx,ceny)

		draw.text((10,420),str2,font=font)
		
		newfile=self.filename.replace(".ppm","_ana.png")
		im.save(newfile,"PNG")
		
		return cenx,ceny


if __name__=="__main__":
	p=ImageGrav(sys.argv[1])

	y,value=p.getXline(240)
	print(y,value)
