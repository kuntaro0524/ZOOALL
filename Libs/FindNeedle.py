import sys
import math
import datetime
from Zoom import *
from Gonio import *
from Capture import *
from File import *
from TemplateMatch import *
from ImageGrav import *

class FindNeedle:

	def __init__(self,gonio,capture,zoom):
		self.gonio=gonio
		self.cap=capture
		self.zoom=zoom

		# Low magnification template image
		#self.tmplow_ppm="/isilon/BL32XU/BLsoft/PPPP/01.Data/00.CenteringPictures/TemplateFile/template_low.ppm"
		self.tmplow_ppm="/isilon/BL32XU/BLsoft/PPPP/01.Data/00.CenteringPictures/TemplateFile/hosoi_template.ppm"
		# Center cross position in pixels
		self.cross_low_y=276
		self.cross_low_z=240
		self.cross_high_z=274

		# Pixel resolution
		## Low magnification 
		self.pix2um_lowz= 0.6741  # [um/pixel]
		self.pix2um_lowy= 0.7056  # [um/pixel]

	def capana(self,filename):
                self.cap.capture(filename)
                tm=TemplateMatch(self.tmplow_ppm,filename)
                y0,z0=tm.getXY()
		return y0,z0

	def moveToCenter(self,curr_z):
                # first move pin to center
                zdiff_pix=curr_z-self.cross_low_z
                zdiff_um=zdiff_pix*self.pix2um_lowz
                self.gonio.moveUpDown(zdiff_um)

	def capGrav(self,filename):
		self.cap.capture(filename)
		ig=ImageGrav(filename)
		x,y=ig.getXY()

		return x,y

	def rotateAndCapture(self,phi,outdir):
		# Output ppm file
		filename="%s/phi_%03d.ppm"%(outdir,phi)

                self.gonio.rotatePhi(phi)
                self.cap.capture(filename)
                tm=TemplateMatch(self.tmplow_ppm,filename)
                y0,z0=tm.getXY()
	
		return y0,z0

	def findRough(self,outdir):
                for phistart in range(0,180,10):
                        # rotate and capture
                        y0,z0=self.rotateAndCapture(phistart,outdir)

                        if y0>5.0:
				return phistart
		return -999.999

	def gradualAlign(self,outdir,phibase):
		filename=outdir+"/"+"tmp.ppm"
		x0,z0=self.capGrav(filename)
		self.moveToCenter(z0)
		x0,z0=self.capGrav(filename)

		phiplus=phibase

		while(1):
			# rotate and capture and analysis
			phiplus+=5.0
                	self.gonio.rotatePhi(phiplus)
			xp,zp=self.capGrav(filename)
			self.moveToCenter(zp)

		return -1

	def do(self,outdir):
                # for low magnification
                self.zoom.zoomOut()

                # Alignment of needle
                phi=-999.999

		phi=self.findRough(outdir)

		if phi==-999.999:
			sys.exit(1)

                # Main loop
                while(1):
                        flag=self.gradualAlign(outdir,phi)
                        if flag==0:
                                break


	def mainLoop(self,outdir,phibase,phistep):
		filename=outdir+"/"+"tmp.ppm"
		x0,z0=self.capGrav(filename)
		self.moveToCenter(z0)
		x0,z0=self.capGrav(filename)

		# rotate and capture and analysis
		phiplus=phibase+phistep
                self.gonio.rotatePhi(phiplus)
		xp,zp=self.capGrav(filename)

		if fabs(z0-zp)<5.0:
			return  0
		elif zp>z0:
			self.gonio.movePint(-200)
		elif zp<z0:
			self.gonio.movePint(200)

		# DIFF 
                self.gonio.rotatePhi(phibase)
		x0,z0=self.capGrav(filename)
		self.moveToCenter(z0)

		return -1

	def collectData(self,outdir="/isilon/users/target/target/Staff/BLtune/"):
		# for low magnification
		self.zoom.zoomOut()

                # Alignment of needle
		phi=-9999.999

                for phistart in range(0,360,10):
			# rotate and capture
			y0,z0=self.rotateAndCapture(phistart,outdir)

			if y0>5.0:
				phi=phistart
				break

		if phi==-9999.999:
			raise MyException("Needle was not found")

		# Main loop
		while(1):
			flag=self.mainLoop(outdir,phi,1.0)
			if flag==0:
				break
		while(1):
			flag=self.mainLoop(outdir,phi,5.0)
			if flag==0:
				break


	def pintData(self,outdir="/isilon/users/target/target/Staff/BLtune/"):
		# Initial information
		d=datetime.datetime.now()

		# Pixel resolution
		## Low magnification 
		pix2um_lowz= 0.6741  # [um/pixel]
		pix2um_lowy= 0.7056  # [um/pixel]

		# Center cross position in pixels
		cross_low_y=276
		cross_high_z=274

		# for low magnification
		self.zoom.zoomOut()

		# log file
		logf=open("needle.txt","w")

                # Alignment of needle
                for pinposi in range(0,10):
			move=+100
			tmp="image_%08dum.ppm"%(pinposi*move)
			filename=outdir+"/"+tmp
			self.gonio.movePint(move)
			r1,r2,r3=self.howMatch(filename)
			logf.write("%8.2f %10.5f %10.5f %10.5f\n"%(pinposi*move,r1,r2,r3))

		logf.close()

if __name__=="__main__":
        #host = '192.168.163.1'
        host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

	f=File("./")
        gonio=Gonio(s)
        capture=Capture()
	zoom=Zoom(s)

        p=FindNeedle(gonio,capture,zoom)
	#p.do(f.getAbsolutePath())
	p.collectData(f.getAbsolutePath())
	capture.disconnect()
	#p.collectData(f.getAbsolutePath())
	#p.collectData(f.getAbsolutePath())
	#p.collectData(f.getAbsolutePath())
	#p.collectData(f.getAbsolutePath())
	#p.pintData(f.getAbsolutePath())
