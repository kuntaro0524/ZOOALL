#from opencv.cv import LoadImageM
#from opencv.highgui import *

#import Image
import os,glob
import sys
import cv2

class LargePlateMatchingCam2:
	def __init__(self,template_path,template_prefix):
		self.template_path=template_path
		self.template_prefix=template_prefix
		self.isSeiri=False
	
		self.xstart=320
		self.ystart=120
		self.xend=540
		self.yend=400

	def setNewTarget(self,target_ppm):
		self.target_ppm=target_ppm

	def basicProc(self,target_pic,back_pic,gauss=5,prefix="test"):
                pinimage=cv2.imread(target_pic,0)
                back=cv2.imread(back_pic,0)

		print(pinimage.shape)
                dimg=cv2.absdiff(pinimage,back)
                cv2.imwrite("./diff.jpg",dimg)

                # Gaussian blur
                blur = cv2.GaussianBlur(dimg,(gauss,gauss),0)

                # 2 valuize
                th = cv2.threshold(blur,20,150,0)[1]
                cv2.imwrite("./%s_bin.jpg"%prefix,th)

		return th

	def getROI(self,th_cv2_img,prefix="test"):
                #ROI
                self.roi=th_cv2_img[self.ystart:self.yend,self.xstart:self.xend]
                cv2.imwrite("%s_binroi.jpg"%(prefix),self.roi)
		return self.roi

	def getContRight(self,target_pic,back_pic,gauss=5,prefix="test"):
                self.roi=self.basicProc(target_pic,back_pic)

                # find contours
                newimage=cv2.imread("%s_binroi.jpg"%prefix)
                contours,hierarchy=cv2.findContours(self.roi,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(newimage,contours,0,(0,255,0),1)

                max_hori=0
                max_vert=-999
                for d in contours[0]:
                        for i in d:
                                hori=i[0]
                                vert=i[1]
                                print("CONT:",hori,vert)
                                if hori >= max_hori:
                                        print("MAX!",hori,vert)
                                        max_hori=hori
                                        max_vert=vert
                print(max_hori,max_vert)
                cv2.circle(self.roi,(max_hori,max_vert),3,(0,0,255),3)
                cv2.imwrite("cont.jpg",self.roi)
		return max_hori,max_vert

	def makeOtehon(self,otehon,back_pic):
		th=self.basicProc(otehon,back_pic,gauss=5,prefix="otehon_make")
		roi=self.getROI(th,"otehon_make")
                cv2.imwrite("otehon_make.jpg",self.roi)

	def test2(self,target_pic,back_pic,gauss=5,prefix="test"):
		# find contours
		max_hori,max_vert=self.getContRight(target_pic,back_pic,gauss,prefix)

	def matchPosition(self,target_pic,back_pic,template_pic,gauss=5,prefix="test"):
		th=self.basicProc(target_pic,back_pic,gauss=gauss,prefix=prefix)
		#self.roi=self.basicProc(target_pic,back_pic,gauss=gauss,prefix=prefix)

		# Otehon at 0 deg.
		otehon=cv2.imread(template_pic,0)

		# TemplateMatching
                result=cv2.matchTemplate(otehon,th,cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
                top_left=max_loc
                w,h=otehon.shape[::-1]
                bottom_right=(top_left[0]+w,top_left[1]+h)
                print("MAX_LOC=",max_loc)
                print(top_left,bottom_right)
                cv2.rectangle(th,top_left,bottom_right,(255,0,0),2)
                cv2.circle(th,top_left,2,(255,0,0),2)
                cv2.imwrite("%s_result.jpg"%prefix,th)

                return max_loc,max_val

	def test(self,target_pic,back_pic,gauss=5,prefix="test"):
		pinimage=cv2.imread(target_pic,0)
		back=cv2.imread(back_pic,0)

                dimg=cv2.absdiff(pinimage,back)
                cv2.imwrite("./diff.jpg",dimg)

                # Gaussian blur
                blur = cv2.GaussianBlur(dimg,(gauss,gauss),0)

                # 2 valuize
                th = cv2.threshold(blur,20,150,0)[1]
                cv2.imwrite("./%s_bin.jpg"%prefix,th)

                #ROI
                self.roi=th[self.ystart:self.yend,self.xstart:self.xend]
                cv2.imwrite("%s_binroi.jpg"%(prefix),self.roi)

		#Contours
		newimage=cv2.imread("%s_binroi.jpg"%prefix)
                contours,hierarchy=cv2.findContours(self.roi,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(newimage,contours,0,(0,255,0),1)
		cv2.imwrite("cont.jpg",newimage)

		"""
		#cv2.imwrite("result0.jpg",result)

		min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
		top_left=max_loc
		w,h=template.shape[::-1]
		bottom_right=(top_left[0]+w,top_left[1]+h)

		result=cv2.imread(target_pic)
		cv2.rectangle(result,top_left,bottom_right,(255,0,0),2)
		cv2.imwrite("result.jpg",result)
		"""

	def simple(self,target_pic,template_pic):
		template=cv2.imread(template_pic,0)
		target=cv2.imread(target_pic,0)
		result=cv2.matchTemplate(template,target,cv2.TM_CCOEFF_NORMED)
		cv2.imwrite("result0.jpg",result)

		min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
		top_left=max_loc
		w,h=template.shape[::-1]
		bottom_right=(top_left[0]+w,top_left[1]+h)

		result=cv2.imread(target_pic)
		cv2.rectangle(result,top_left,bottom_right,(255,0,0),2)
		cv2.imwrite("result.jpg",result)

	def getPosition(self,target_image,phi=0.0):
		if self.isSeiri==False:
			self.fileSeiri()
		zero_template=self.template_list[0][0]
		target_cvimage=cv2.imread(target_image,0)
                template=cv2.imread(zero_template,0)

		cv2.imwrite("zero.png",template)
		cv2.imwrite("target.png",target_cvimage)

                result=cv2.matchTemplate(template,target_cvimage,cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
		top_left=max_loc
		w,h=template.shape[::-1]
		bottom_right=(top_left[0]+w,top_left[1]+h)
		result=cv2.imread(target_image)
		cv2.rectangle(result,top_left,bottom_right,(255,0,0),2)
		cv2.imwrite("result.jpg",result)

		print("MAX_LOC=",max_loc)
		return max_loc

        def getPosition2(self,target_roi,phi=0.0):
                if self.isSeiri==False:
                        self.fileSeiri()

                zero_template=self.template_list[0][0]
                template=cv2.imread(zero_template,0)

                cv2.imwrite("zero.png",template)
                cv2.imwrite("target.png",target_roi)

                result=cv2.matchTemplate(template,target_roi,cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
                top_left=max_loc
                w,h=template.shape[::-1]
                bottom_right=(top_left[0]+w,top_left[1]+h)
                print("MAX_LOC=",max_loc)
		print(top_left,bottom_right)
		print("ROI shape",target_roi.shape)
                cv2.rectangle(target_roi,top_left,bottom_right,(255,0,0),2)
                cv2.imwrite("result.jpg",target_roi)

                return max_loc

	def getSimilarity(self,target_cvimage,template_pic):
                template=cv2.imread(template_pic,0)
                result=cv2.matchTemplate(template,target_cvimage,cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
		
		return max_val

	def fileSeiri(self):
		lll="%s/%s*template*"%(self.template_path,self.template_prefix)
		#print lll
		filelist=glob.glob(lll)
		self.template_list=[]
		for f in filelist:
			filename=f.split('/')[-1]
			phi=float(filename.split('_')[1])
			#print filename,phi
			self.template_list.append((f,phi))

		self.template_list=sorted(self.template_list, key=lambda x: x[1],reverse=False)
		#print self.template_list

	def match(self,target_pic):
		print("Matching")
		if self.isSeiri==False:
			self.fileSeiri()
		print(self.template_list)
		max_sim=0.0
		ok_file=""
		for f,phi in self.template_list:
			max_val=self.getSimilarity(target_pic,f)
			print(f,max_val)
			if max_val > max_sim:
				max_sim=max_val
				ok_file=f
				ok_phi=phi
		#self.simple(target_pic,ok_file)
	
		return ok_file,ok_phi

if __name__=="__main__":

	tm=LargePlateMatchingCam2("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TemplateImages/","holder01")
	back="bs_on_cam2_image.png"
	#template_pic="cam2_0deg_otehon.png"

	#template_pic="./TemplateImages/cam2_0deg_otehon.png"
	#back="TemplateImages/bs_on_cam2_image.png"

	#template_pic="./TemplateImages/cam2_0deg_otehon.png"
	#back="back2.png"

	template_pic="./TemplateImages/cam2_0deg_otehon.png"
	back="back2.png"

	#171212-Okkotonushi/FinalCam2Otehon/cam2.png
	target_pic="171212-Okkotonushi/FinalCam2Otehon/cam2.png"

	th=tm.basicProc(target_pic,back,gauss=5,prefix="otehon")
	cv2.imwrite("otehon.png",th)
	#print tm.matchPosition(sys.argv[1],back,template_pic,gauss=5,prefix="test")

	#tm.makeOtehon(sys.argv[1],back)
	#tm.match(sys.argv[1])
	#tm.fileSeiri()
	#tm.getXY()
	#tm.show()
