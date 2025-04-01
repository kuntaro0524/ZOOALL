import socket,os,sys,datetime,cv2,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Device
import IboINOCC
import Zoo
import MyException
import time
import numpy as np
import LargePlateMatchingBC

base_imgdir="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"
backimg="%s/bcbg.png"%base_imgdir
bc_otehon_bin="%s/bc_otehon_bin.png"%base_imgdir

target_img = cv2.imread(sys.argv[1])
back_img = cv2.imread(backimg)

# GRAY SCALE First this is modified from BL32XU version
gim = cv2.cvtColor(target_img,cv2.COLOR_BGR2GRAY)
gbk = cv2.cvtColor(back_img,cv2.COLOR_BGR2GRAY)
dimg=cv2.absdiff(gim,gbk)

# Gaussian blur
blur = cv2.GaussianBlur(dimg,(3,3),0)
sgb = cv2.threshold(blur,15,150,0)[1]

cv2.imwrite("bin.png",sgb)

#lpmbc=LargePlateMatchingBC.LargePlateMatchingBC()
#lpmbc.getHoriVer(sys.argv[1])
template=cv2.imread(bc_otehon_bin)
h,w=template.shape[0],template.shape[1]

tttt = cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)

result=cv2.matchTemplate(tttt,sgb,cv2.TM_CCOEFF_NORMED)
min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)

top_left=max_loc
print top_left
print template.shape

bottom_right=(top_left[0]+w,top_left[1]+h)
print "MAX_LOC=",max_loc
print top_left,bottom_right
cv2.rectangle(target_img,top_left,bottom_right,(255,0,0),2)
cv2.imwrite("result.jpg",target_img)
