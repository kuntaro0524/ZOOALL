import cv2,sys
import matplotlib.pyplot as plt
import numpy as np

#img = cv2.imread(sys.argv[1])

target_img = cv2.imread(sys.argv[1])
back_img = cv2.imread(sys.argv[2])

# GRAY SCALE First this is modified from BL32XU version
gim = cv2.cvtColor(target_img,cv2.COLOR_BGR2GRAY)
gbk = cv2.cvtColor(back_img,cv2.COLOR_BGR2GRAY)
dimg=cv2.absdiff(gim,gbk)

# Gaussian blur
blur = cv2.GaussianBlur(dimg,(3,3),0)
sgb = cv2.threshold(blur,30,150,0)[1]

cv2.imwrite("bc_otehon_bin.png",sgb)
