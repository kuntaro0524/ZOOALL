import sys
import datetime
from MyException import *
from PIL import Image
from PIL import ImageDraw,ImageFont

class BeamCenter:
	def __init__(self,filename):
		self.filename=filename

	def damp(self):
		im=Image.open(self.filename)
		newi=im.convert("L")
		pix=newi.load()
		
		cnt=0

		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				if pix[x,y]<200:
					pix[x,y]=0
				print(x,y,pix[x,y])
			print("")

	def countSaturated(self):
		im=Image.open(self.filename)
		newi=im.convert("L")
		pix=newi.load()
		
		cnt=0

		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				if pix[x,y]>=240:
					cnt+=1
		return cnt

	def getSummed(self):
		im=Image.open(self.filename)
		newi=im.convert("L")
		pix=newi.load()
		
		isum=0

		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				if pix[x,y]>70:
					isum+=int(pix[x,y])

		return isum

	def getParams(self):
		im=Image.open(self.filename)
		newi=im.convert("L")
		pix=newi.load()

		isum=0
		satcnt=0

		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				if pix[x,y]>=240:
					satcnt+=1
				if pix[x,y]>70:
					isum+=int(pix[x,y])
		# Average
		npix=im.size[0]*im.size[1]
		ave=float(isum)/float(npix)
		thresh=ave*3.0

		if thresh > 240:
			print("THRESH > 240")
			thresh=ave

		ithresh=0
		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				if pix[x,y]>thresh:
					ithresh+=1
		return satcnt,ave,ithresh

	def check(self):
		im=Image.open(self.filename)
		newi=im.convert("L")
		pix=newi.load()

		isum=0
		satcnt=0
		isum_all=0

		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				isum_all+=int(pix[x,y])

				if pix[x,y]>=200:
					satcnt+=1
				if pix[x,y]>=200:
					isum+=int(pix[x,y])

		# Saturated count
		npix=im.size[0]*im.size[1]
		perc=float(satcnt)/float(npix)*100.0

		print("SAT %5d SATURATED_AREA_PERCENT=%8.3f"%(satcnt,perc))
		return satcnt,perc,isum_all
		
	def find2(self):
		time.sleep(1.0)
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
		thresh=ave*3.0
		sumpeak=0.0
		sumx=0.0
		sumy=0.0
		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				if pix[x,y]>thresh:
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
		fontPath="/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono-Bold.ttf"
		font=ImageFont.truetype(fontPath,14)

		str2="Pixel    (Y,Z)=(%8.2f,%8.2f)[pix]"%(cenx,ceny)

		# um convertion
		yum=cenx*5.0/67.0
		zum=ceny/26.75

		str3="Position (Y,Z)=(%8.3f,%8.3f)[um]"%(yum,zum)

		draw.text((10,400),dstr,font=font)
		draw.text((10,420),str2,font=font)
		draw.text((10,440),str3,font=font)
		
		newfile=self.filename.replace(".ppm","_ana.png")
		im.save(newfile,"PNG")

		return(cenx,ceny)

	def find(self):
		im=Image.open(self.filename)
		newi=im.convert("L")
		pix=newi.load()

		if im.size[0]==0:
			raise MyException("Image size is 0!!!!")

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
		thresh=ave*3.0
		if thresh > 255:
			thresh=255
		sumpeak=0.0
		sumx=0.0
		sumy=0.0
		for x in range(0,im.size[0]):
			for y in range(0,im.size[1]):
				if pix[x,y]>=thresh:
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
		fontPath="/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono-Bold.ttf"
		font=ImageFont.truetype(fontPath,14)

		str2="Pixel    (Y,Z)=(%8.2f,%8.2f)[pix]"%(cenx,ceny)

		# um convertion
		yum=cenx*5.0/67.0
		zum=ceny/26.75

		str3="Position (Y,Z)=(%8.3f,%8.3f)[um]"%(yum,zum)

		draw.text((10,400),dstr,font=font)
		draw.text((10,420),str2,font=font)
		draw.text((10,440),str3,font=font)
		
		newfile=self.filename.replace(".ppm","_ana.png")
		im.save(newfile,"PNG")
		
		return cenx,ceny

	def averageImage(self,image):
		newi=image.convert("L")
		pix=newi.load()

		sumpeak=0
		for x in range(0,image.size[0]):
			for y in range(0,image.size[1]):
				if pix[x,y]<=255:
					sumpeak+=pix[x,y]
		npix=image.size[0]*image.size[1]
		ave=sumpeak/float(npix)
		return ave

	def gravAbove(self,image,thresh,two_flag=False):
		newi=image.convert("L")
		pix=newi.load()

		sumpeak=0.0
		sumx=0.0
		sumy=0.0
		for x in range(0,image.size[0]):
			for y in range(0,image.size[1]):
				if pix[x,y]>=thresh:
					if two_flag==False:
						sumpeak+=pix[x,y]
						sumx+=pix[x,y]*x
						sumy+=pix[x,y]*y
					else :
						sumpeak+=100
						sumx+=100*x
						sumy+=100*y
		cenx=sumx/sumpeak
		ceny=sumy/sumpeak
		return cenx,ceny

	def findRobust(self):
		im=Image.open(self.filename)
		newi=im.convert("L")
		pix=newi.load()

		if im.size[0]==0:
			raise MyException("Image size is 0!!!!")

		# Original protocol
		othresh=self.averageImage(im)*3.0
		if othresh > 200:
			othresh=200
			
		ox,oy=self.gravAbove(im,othresh)

		# Test protocol 1
		tx1,ty1=self.gravAbove(im,200)

		# Test protocol 2
		tx2,ty2=self.gravAbove(im,200,two_flag=True)

		print("Compare O:%5d%5d, T1:%5d%5d, T2:%5d%5d"%(ox,oy,tx1,ty1,tx2,ty2))
		cenx=tx1
		ceny=ty1

		# output log image
		draw=ImageDraw.Draw(im)

		# drawing circle at calculated position
		draw.ellipse((cenx-5,ceny-5,cenx+5,ceny+5),fill=(0,0,0))

		# Date
		dstr="%s"%datetime.datetime.now()
		#fontPath="/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono-Bold.ttf"
		fontPath="/usr/share/fonts/dejavu/DejaVuSansMono.ttf"
		font=ImageFont.truetype(fontPath,14)

		str2="Pixel    (Y,Z)=(%8.2f,%8.2f)[pix]"%(cenx,ceny)

		# um convertion
		yum=cenx*5.0/67.0
		zum=ceny/26.75

		str3="Position (Y,Z)=(%8.3f,%8.3f)[um]"%(yum,zum)

		draw.text((10,400),dstr,font=font)
		draw.text((10,420),str2,font=font)
		draw.text((10,440),str3,font=font)
		
		newfile=self.filename.replace(".ppm","_ana.png")
		im.save(newfile,"PNG")
		
		return cenx,ceny

if __name__=="__main__":
	p=BeamCenter(sys.argv[1])

	#print p.countSaturated()
	#print p.getSummed()
	#print p.find2()
	#print p.damp()
	print(p.findRobust())
