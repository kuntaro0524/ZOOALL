#from opencv.cv import LoadImageM
#from opencv.highgui import *

import Image
import os,glob
import sys
import cv2
import socket,os,sys,datetime,cv2,time,numpy
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
import Device
import IboINOCC
import LargePlateMatchingCam2

if __name__=="__main__":

	tm=LargePlateMatchingCam2.LargePlateMatchingCam2("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TemplateImages/","holder01")
	back="bs_on_cam2_image.png"

        blanc = '172.24.242.41'
        b_blanc = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((blanc,b_blanc))


        dev=Device.Device(s)
        dev.init()
	inocc=IboINOCC.IboINOCC(dev.gonio)

        # preparation
        dev.prepCenteringLargeHolderCam2()
	ix,iy,iz=dev.gonio.getXYZmm()

	#((316, 143), 0.97274786233901978)
	# um/pixel=0.0135
	template="./cam2_0deg_otehon.png"

	path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/171212-Okkotonushi/MakingPictures2/FocusByCam2"
	filename="%s/capture.png"%path
      	inocc.getCam2Image(filename)

        max_loc,max_value=tm.matchPosition(filename,back,template,gauss=5,prefix="pint")
	
	print("MAX=",max_value)
	hori=max_loc[0]
	vert=max_loc[1]
	print(hori,vert)
	dhori=hori-316
	dvert=vert-143

	move_um=dhori/0.0135
	print(move_um)
	dev.gonio.movePint(-move_um)

	#dev.gonio.moveXYZmm(ix,iy,iz)
