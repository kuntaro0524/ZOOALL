import cv2,sys,os
import numpy as np
import pylab as plt
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
from File import *

class CryImageProc():
	def __init__(self,imagefile):
		self.imagefile=imagefile
		#self.backfile="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_c1_z0_b4.ppm"
		# 160918
		#self.backfile="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_200_7500.ppm"
		self.backfile="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_200_7500_2.ppm"
		#self.backfile="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/./back_161008.ppm"
		#self.backfile="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_nopin_160926.ppm"
		#self.backfile="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_nopin_160926-2.ppm"
		self.logdir="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Log/"
		self.ff=File(self.logdir)
		# ROI for robust centering
		self.roi=False
		self.roi_startx=200
		self.roi_endx=640
		self.roi_starty=2
		self.roi_endy=480

	def setBack(self,backimg):
		self.backfile=backimg

	def canny2(self,c1=150,c2=200,aperture_size=3):
		im = cv2.imread(self.imagefile)
		im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
		cv2.GaussianBlur(im_gray, (3,3), 0, im_gray)
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(9,9))
		dilated = cv2.dilate(im_gray, kernel)
		im_edge = cv2.Canny(dilated, c1,c2,aperture_size)
		cv2.imshow("Show Image",im_edge)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		return im_edge

	def canny(self,low_thresh=50,high_thresh=200):
		gray = cv2.imread(self.imagefile,0)
		self.edge = cv2.Canny(gray,low_thresh,high_thresh)

		self.height,self.width=gray.shape
		print("Height:",self.height)	
		print("Width :",self.width)

		self.edge_min_max(self.edge)
		cv2.imshow("Show Image",self.edge)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def edge_min_max(self,np_image):
		saved_point=[]
		for x in np.arange(0,self.width):
			for y in np.arange(0,self.height):
				if np_image[y][x]>250:
					saved_point.append((x,y))
		nas=np.array(saved_point)
		#for e in nas:
			#print e
		#print nas
# Example
#http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html

	def contours(self,imagefile):
		img = cv2.imread(imagefile,0)
		ret,thresh = cv2.threshold(img,127,255,0)
		contours,hierarchy = cv2.findContours(thresh, 1, 2)
		cnt = contours[0]
		M = cv2.moments(cnt)
		print(M)

	def rotatedRectangle(self):
		img = cv2.imread(self.imagefile,0)
		ret,thresh = cv2.threshold(img,127,255,0)
		contours,hierarchy = cv2.findContours(thresh, 1, 2)
		cnt = contours[0]
		M = cv2.moments(cnt)
		print(M)

		x,y,w,h=cv2.boundingRect(cnt)
		imim=cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
		rect = cv2.minAreaRect(cnt)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		im = cv2.drawContours(im,[box],0,(0,0,255),2)

	def labeling(self):
    		im = cv2.imread(self.imagefile)
		gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) # Gray trans
		th = cv2.threshold(gray,127,255,0)[1]       # 2 chika
		# Edge extraction
		cnts = cv2.findContours(th,1,2)[0]          # Rinkaku
		cv2.drawContours(im,cnts,-2,(255,0,0),-1)   # Max rinkaku
		# Results
		cv2.imshow("Show Image",im)                 # display
		cv2.waitKey(0)                              # Wait keys
		cv2.destroyAllWindows()                     # Window destroy

	def labeling2(self):
		im = cv2.imread(self.imagefile)
		gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
		th = cv2.threshold(gray,30,150,0)[1]
		cnts = cv2.findContours(th,1,2)[0]		
		areas = [cv2.contourArea(cnt) for cnt in cnts]
		cnt_max = [cnts[areas.index(max(areas))]][0]
		cv2.drawContours(im,[cv2.convexHull(cnt_max)],0,(255),-1)   
		cv2.imshow("Show Image",im)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def rinkaku(self):
		im = cv2.imread(self.imagefile)
		im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
		#im_gray_smooth=cv2.GaussianBlur(im_gray,(11,11),0)
		ret,th1 = cv2.threshold(im_gray,130,255,cv2.THRESH_BINARY)
		contours, hierarchy = cv2.findContours(th1,cv2.RETR_TREE,\
                                       cv2.CHAIN_APPROX_SIMPLE)
		cv2.drawContours(im,contours,-1,(0,255,0),3)
		plt.title('input image')
		plt.subplot(2,2,2),plt.imshow(im,'gray')
		plt.title('output image')
		#plt.subplot(2,2,3),plt.imshow(im_gray_smooth,'gray')
		#plt.title("Gray+gauss")
		plt.subplot(2,2,4),plt.imshow(th1,'gray')
		plt.title('Nichika')
		plt.show()

	def gauss_binarization(self,filename):
		im = cv2.imread(filename)
		# Gray scale
		gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
		# Gaussian blur
		blur = cv2.GaussianBlur(gray,(3,3),0)
		# 2 valuize
		th = cv2.threshold(blur,127,255,0)[1]
		#self.image_show(th)
		return th

	def image_show(self,image_bunch):
		cv2.imshow("Show Image",image_bunch)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def get_edge_after_bin(self,filename):
		th=self.gauss_binarization(filename)
		return self.edge_bin_codes(th)

	def calcEdge(self,infile,debug=False):
		inum=0
		print("input file=",infile)
		im = cv2.imread(infile)
		print("Backfile=%s"%self.backfile)
		bk = cv2.imread(self.backfile)

		self.image_show(im)

		dimg=cv2.absdiff(im,bk)
		self.image_show(dimg)

		newidx=self.ff.getNewIdx3()
		log_img="%s/calcEdge_diff.jpg"%(self.logdir)
		cv2.imwrite(log_img,dimg)
		# Gray scale
		gray = cv2.cvtColor(dimg,cv2.COLOR_BGR2GRAY)
		# Gaussian blur
		blur = cv2.GaussianBlur(gray,(3,3),0)
		# 2 valuize
		th = cv2.threshold(blur,20,150,0)[1]
		log_img="%s/calcEdge_bin.jpg"%(self.logdir)
		cv2.imwrite(log_img,th)
		try:
			edge_data=self.edge_bin_codes(th)
		except MyException as ttt:
			raise MyException("No good points were found:%s"%ttt.args[0])

		if debug:
			self.height,self.width=th.shape
			for x in np.arange(0,self.width-1):
				for y in np.arange(0,self.height-1):
					print(x,y,th[y][x])
		return edge_data

	def getGravity(self,codes):
		count=0
		xsum=0.0
		ysum=0.0
		for code in codes:
			x,ymin,ymax=code
			xsum+=x
			ysum+=((ymin+ymax)/2.0)
			count+=1
		xcode=int(xsum/float(count))
		ycode=int(ysum/float(count))
		return xcode,ycode

	def getGravWidthArea(self,codes):
		count=0
		xsum=0.0
		ysum=0.0
		area=0.0
		yw_list=[]
		for code in codes:
			x,ymin,ymax=code
			#print x,ymin,ymax
			xsum+=x
			ysum+=((ymin+ymax)/2.0)
			# Y width
			ywidth=ymax-ymin
			yw_list.append(ywidth)
			area+=ywidth
			count+=1

		# Y width max
		ya=np.array(yw_list)
		ywmax=ya.max()
		xmin,dum,dum2=codes[0]
		xmax,dum,dum2=codes[len(codes)-1]
		xwidth=xmax-xmin
		xedge=xmin

		grav_x=int(xsum/float(count))
		grav_y=int(ysum/float(count))
		return grav_x,grav_y,ywmax,xedge,area

	def getParams(self,codes):
		count=0
		# For gravity calculation
		xsum=0.0
		ysum=0.0
		# Area of the binarized
		area=0.0
		x_list=[]
		yw_list=[]
		# This code includes "Rinkaku" of binarized data
		# This list includes 
		# x: horizontal pixel coordinate
		# y: vertical pixel coordinate
		for code in codes:
			# Unzipped information
			x,ymin,ymax=code
			#print x,ymin,ymax
			# For gravity calculation
			xsum+=x
			ysum+=((ymin+ymax)/2.0)
			# Y width (Vertial width for estimating length for raster scan)
			ywidth=ymax-ymin
			x_list.append(x)
			yw_list.append(ywidth)
			area+=ywidth
			count+=1

		# Y width max (Vertical raster scan length)
		ya=np.array(yw_list)
		ywmax=ya.max()
		xmin,dum,dum2=codes[0]
		xmax,dum,dum2=codes[len(codes)-1]
		
		# The top of the Loop (the most left point)
		xwidth=xmax-xmin
		xedge=xmin

		#print "##########"
		#for x,y in zip(x_list,yw_list):
			#print x,y
		#print "##########"
		#print xwidth,ywmax

		grav_x=int(xsum/float(count))
		grav_y=int(ysum/float(count))

		print("Gravity =",grav_x,grav_y)


		return grav_x,grav_y,ywmax,xedge,area

	def edge_bin_codes(self,imdata):
		### EDGE coordinates
		# Normal videosrv output
        	# height=480, width=640
		height,width=imdata.shape
		# videoserv sometimes includes "strange values" in 
		# y=0 line (Top of the image on videosrv)
		# Then this 
		print("Read image consits of %d x %d pixels"%(height,width))
		print("RANGE X: %d - %d"%(self.roi_startx,self.roi_endx-1))
		print("RANGE y: %d - %d"%(self.roi_starty,self.roi_endy-1))
		n_good=0

		x_ymin_ymax=[]
        	for x in np.arange(self.roi_startx,self.roi_endx-1):
                	ya=[]
                	for y in np.arange(self.roi_starty,self.roi_endy-1):
                        	if imdata[y][x] > 0:
                                	ya.append(y)
                	if len(ya)>2:
                        	yna=np.array(ya)
                        	ymin=yna.min()
                        	ymax=yna.max()
				x_ymin_ymax.append((x,ymin,ymax))
				n_good+=1
		if n_good>2:
			return np.array(x_ymin_ymax)
		else:
			raise MyException("No good points!")

        def getArea(self,imgfile,debug=False,loop_size="small"):
                # ROI setting for the robust centering 
                # at the final centering
                if loop_size=="small":
                        self.roi_startx=200
                        self.roi_endx=510
                        self.roi_starty=2
                        self.roi_endy=480
                # Large loop
                elif loop_size=="large":
                        self.roi_startx=200
                        self.roi_endx=640
                        self.roi_starty=2
                        self.roi_endy=480
                # Large loop
                elif loop_size=="very_small":
                        self.roi_startx=200
                        self.roi_endx=500
                        self.roi_starty=2
                        self.roi_endy=480
                try:
                        edge_codes=self.calcEdge(imgfile,debug)
                except MyException as tttt:
                        raise MyException("No loop was found!")

                grav_x,grav_y,ywmax,xedge,area=self.getParams(edge_codes)
		return area

	# 2015/11/21 K.Hirata modified
	# final_roi -> loop_size
	# small: cut X region
	# large: no-cut X region
	# very_small: Center only
	def getCenterInfo(self,imgfile,debug=False,loop_size="small"):
		# ROI setting for the robust centering 
		# at the final centering
		if loop_size=="small":
			self.roi_startx=200
			self.roi_endx=510
			self.roi_starty=2
			self.roi_endy=480
		# Large loop
		elif loop_size=="large":
			self.roi_startx=200
			self.roi_endx=640
			self.roi_starty=2
			self.roi_endy=480
		# Large loop
		elif loop_size=="medium":
			self.roi_startx=200
			self.roi_endx=575
			self.roi_starty=2
			self.roi_endy=480
		# Large loop
		elif loop_size=="very_small":
			self.roi_startx=200
			self.roi_endx=500
			self.roi_starty=2
			self.roi_endy=480
		try:
			edge_codes=self.calcEdge(imgfile,debug)
		except MyException as tttt:
			raise MyException("No loop was found!")

		grav_x,grav_y,ywmax,xedge,area=self.getParams(edge_codes)

		if debug: 
			print("XEDGE:",xedge)
			print("YWMAX:",ywmax)
		# X/Y width
		if loop_size=="large":
			print("NORMAL ROI")
			dist_cenx_edgex=np.fabs(grav_x-xedge)
			xwidth=2*int(dist_cenx_edgex)
			ywidth=ywmax

		elif loop_size=="small" or loop_size=="medium":
			print("FINAL ROI")
			xwidth=np.fabs(self.roi_endx-xedge)
			ywidth=ywmax
			grav_x=int((self.roi_endx+xedge)/2.0)

		elif loop_size=="very_small":
			print("VERY SMALL ROI")
			# manually defined
			# 2.78 um / pixel on captured file
			# 60.0 um = ~21 pixels
			# Center region : Edge -> 300um right
			xwidth=21
			ywidth=21
			pix_for_300um_right=int(300/2.78)
			grav_x=xedge+pix_for_300um_right

		if debug==True:
			# Raster scan start/end x,y
			start_x=xedge
			end_x=int(xedge+xwidth)
			start_y=int(grav_y-int(ywmax/2.0))
			end_y=int(grav_y+int(ywmax/2.0))

			im = cv2.imread(imgfile)
			cv2.rectangle(im,(start_x,start_y),(end_x,end_y),(0,255,0),1)
			cv2.circle(im,(grav_x,grav_y),2,(0,0,255),2)
			cv2.imshow("DEBUG SHIKAKU",im)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		# KUNIO
		im = cv2.imread(imgfile)
		cv2.circle(im,(grav_x,grav_y),2,(0,0,255),2)
		cv2.imshow("DEBUG",im)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

		return grav_x,grav_y,xwidth,ywidth,area,xedge
 
if __name__ == "__main__":
	cip=CryImageProc(sys.argv[1])
	im = cv2.imread(sys.argv[1])
	cv2.imshow("DEBUG SHIKAKU",im)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	#cip.canny()
	#cip.rotatedRectangle()
	#cip.labeling()
	#cip.labeling2()
	#cip.rinkaku()
	#th=cip.gauss_binarization()
	#a=cip.edge_bin_codes(th)
	#edge_codes=cip.calcEdge(sys.argv[1],backfile)
	#edge_codes=cip.get_edge_after_bin(sys.argv[1])
	#grav_x,grav_y,ywmax,xedge,area=cip.getParams(edge_codes)

	#edge_codes=cip.calcEdge(sys.argv[1])
	"""
	try:
		print "Current 2015/11/21:",cip.getArea(sys.argv[1],debug=False,loop_size="small")
		print "New     2015/11/21:",cip.getArea(sys.argv[1],debug=False,loop_size="very_small")
	except MyException,ttt:
		sys.exit(0)
	"""
