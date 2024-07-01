import sys
import datetime
from Zoom import *
from Gonio import *
from Capture import *
from File import *
from TemplateMatch import *
from FindNeedle import *

class CenteringNeedle:

	def __init__(self,gonio,capture,zoom):
		self.gonio=gonio
		self.cap=capture
		self.zoom=zoom

	def findNeedle(self):
		fn=FindNeedle(self.gonio,self.cap,self.zoom)
        	fn.collectData("/isilon/users/target/target/Staff/BLtune/")

	def centeringLow(self,outdir="/isilon/users/target/target/Staff/BLtune/"):
		# Low magnification template image
		tmplow_ppm="/isilon/BL32XU/BLsoft/PPPP/01.Data/00.CenteringPictures/TemplateFile/template_low.ppm"


		# Output ppm file
		tmpfile="needle_low.ppm"
		ofile=outdir+tmpfile

		# Initial information
		d=datetime.datetime.now()
		init_zz=self.gonio.getZZmm()*1000.0

		# Pixel resolution
		## Low magnification 
		pix2um_lowz= 0.6741  # [um/pixel]
		pix2um_lowy= 0.7056  # [um/pixel]

		# Center cross position in pixels
		cross_low_y=276
		cross_high_z=274

		# for low magnification
		self.zoom.zoomOut()

                # Alignment of needle
                for i in range(0,3):
                        for phistart in [0.0, 90.0]:

                                # first phi
                                self.gonio.rotatePhi(phistart)
                                self.cap.capture(ofile)
                                tm=TemplateMatch(tmplow_ppm,ofile)
                                y0,z0=tm.getXY()

                                # phi 180 relative
                                self.gonio.rotatePhi(phistart+180.0)
                                self.cap.capture(ofile)
                                tm=TemplateMatch(tmplow_ppm,ofile)
                                y1,z1=tm.getXY()

                                # average y0,y1 position
                                yave=(y0+y1)/2.0

                                movey_pix=cross_low_y-yave
                                movey_um=movey_pix*pix2um_lowy

                                self.gonio.moveTrans(movey_um)

                                diff1=(z1-z0)
                                dist=diff1*pix2um_lowz/2.0
                                self.gonio.moveUpDown(dist)

	def centeringHigh(self):
		# High magnification template image
		tmphigh_ppm="/isilon/BL32XU/BLsoft/PPPP/01.Data/00.CenteringPictures/TemplateFile/template_high2.ppm"

		# Output ppm file
		odir="/isilon/users/target/target/Staff/"
		tmpfile="high_needle.ppm"
		ofile=odir+tmpfile

		# Pixel resolution
		pix2um_highz=0.07125   # [um/pixel]
		pix2um_highy=0.07327   # [um/pixel]
		pix2um_highzz=0.0362   # [um/pixel]

		z1=0

		# Initial information
		d=datetime.datetime.now()
		init_zz=self.gonio.getZZmm()*1000.0

		# Center cross position in pixels
		cross_low_y=300
		cross_high_z=240

		# for high magnification
		self.zoom.zoomIn()

		# Y axis tune first
		self.cap.capture(ofile)
		tm=TemplateMatch(tmphigh_ppm,ofile)
		y0,z0=tm.getXY()
		#tm.show()
		movey_pix=cross_low_y-y0
		movey_um=movey_pix*pix2um_highy
		self.gonio.moveTrans(movey_um)

		# Alignment of needle at High magnification factor
		for i in range(0,3):
			for phistart in [0.0, 90.0]:
				# first phi
				self.gonio.rotatePhi(phistart)
        			self.cap.capture(ofile,17000)
				tm=TemplateMatch(tmphigh_ppm,ofile)
				y0,z0=tm.getXY()
	
				# phi 180 relative
				self.gonio.rotatePhi(phistart+180.0)
        			self.cap.capture(ofile,17000)
				tm=TemplateMatch(tmphigh_ppm,ofile)
				y1,z1=tm.getXY()
	
				# average y0,y1 position
				#yave=(y0+y1)/2.0
	        		#movey_pix=originy-yave
	        		#movey_um=movey_pix*pix2um_highy
	        		#gonio.moveTrans(movey_um)
		
				diff1=(z1-z0)
				dist=diff1*pix2um_highz/2.0
				self.gonio.moveUpDown(dist)

		# ZZ alignment
		z_00=0.0
		z_90=0.0
		for i in range(0,3):
			# 0 deg
			self.gonio.rotatePhi(0.0)
			self.cap.capture(ofile,17000)
			tm=TemplateMatch(tmphigh_ppm,ofile)
			z_00+=tm.getXY()[1]
			#tm.show()

			# 90 deg
			self.gonio.rotatePhi(90.0)
			self.cap.capture(ofile,17000)
			tm=TemplateMatch(tmphigh_ppm,ofile)
			z_90+=tm.getXY()[1]
			#tm.show()

		zero_ave=z_00/3.0
		nine_ave=z_90/3.0

		curr_z_center=(zero_ave+nine_ave)/2.0

		hari_center=curr_z_center+110

		diffp=cross_high_z-hari_center

		movep=-diffp*pix2um_highzz
		self.gonio.moveZZrel(movep)
	
		# final information
		final_zz=self.gonio.getZZmm()*1000.0
		diff=final_zz-init_zz

		# Output log file
		zz_db_file="/isilon/users/target/target/Staff/zz_db.txt"
		zzf=open(zz_db_file,"a")
		date=datetime.datetime.now()
		zzf.write("%s %12.5f -> %12.5f [um] d=%12.5f[um]\n"%(date,init_zz,final_zz,diff))
		zzf.close()

if __name__=="__main__":
        host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

        gonio=Gonio(s)
        capture=Capture()
	zoom=Zoom(s)

        p=CenteringNeedle(gonio,capture,zoom)
	#p.centeringLow()
	p.centeringHigh()

