#from opencv.cv import LoadImageM
#from opencv.highgui import *

from Gonio import *
from Capture import *

import Image
import os
import sys
from opencv.cv import *
from opencv.highgui import *

class TemplateMatch:
	def __init__(self,template_ppm,target_ppm):
		self.template_ppm=template_ppm
		self.target_ppm=target_ppm

	def setNewTarget(self,target_ppm):
		self.target_ppm=target_ppm

	def getMatch(self):
		self.tmp_img=cvLoadImage(self.template_ppm,CV_LOAD_IMAGE_GRAYSCALE)
		self.obj_img=cvLoadImage(self.target_ppm,CV_LOAD_IMAGE_GRAYSCALE)
		dst_size=cvSize(self.obj_img.width-self.tmp_img.width+1,self.obj_img.height-self.tmp_img.height+1)
		#dst_img=cvCreateImage(dst_size,IPL_DEPTH_32F,1)

		r1= cvMatchShapes(self.obj_img,self.tmp_img,CV_CONTOURS_MATCH_I1,0)
		r2= cvMatchShapes(self.obj_img,self.tmp_img,CV_CONTOURS_MATCH_I1,0)
		r3= cvMatchShapes(self.obj_img,self.tmp_img,CV_CONTOURS_MATCH_I1,0)

		#print result
		return r1,r2,r3

	def getXY(self):
		self.tmp_img=cvLoadImage(self.template_ppm)
		self.obj_img=cvLoadImage(self.target_ppm)
		dst_size=cvSize(self.obj_img.width-self.tmp_img.width+1,self.obj_img.height-self.tmp_img.height+1)
		dst_img=cvCreateImage(dst_size,IPL_DEPTH_32F,1)
		cvMatchTemplate(self.obj_img,self.tmp_img,dst_img,CV_TM_CCOEFF_NORMED)
		#cvMatchTemplate(self.obj_img,self.tmp_img,dst_img,CV_TM_SQDIFF_NORMED)

		self.p1=CvPoint()
		self.p2=CvPoint()
		status=cvMinMaxLoc(dst_img,self.p1,self.p2)

		return self.p2.x,self.p2.y

	def show(self):
		corner_point=cvPoint(self.p2.x+self.tmp_img.width,self.p2.y+self.tmp_img.height)
		cvRectangle(self.obj_img,self.p2,corner_point,CV_RGB(255,0,0),2)
		cvCircle(self.obj_img,self.p2,5,CV_RGB(255,0,0),2)
		cvNamedWindow("image",1)
		cvShowImage("image",self.obj_img)
		cvWaitKey(0)

if __name__=="__main__":

        host = '172.24.242.41'
        port = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

	tmplowppm="/isilon/BL32XU/BLsoft/PPPP/01.Data/00.CenteringPictures/TemplateFile/template_low.ppm"

	gonio=Gonio(s)
        cap=Capture()

	tm=TemplateMatch(tmplowppm,"/isilon/users/target/target/image005.ppm")
	print tm.getXY()
