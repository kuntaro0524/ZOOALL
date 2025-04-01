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
sgb = cv2.threshold(blur,15,150,0)[1]

#sgb = cv2.threshold(dimg,15,150,0)[1]
cv2.imwrite("sgb.png",sgb)

# Contour finding
contours, hierarchy = cv2.findContours(sgb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

cv2.drawContours(gim,contours,-1,(0,255,0),3)
cv2.imwrite("contour.png",gim)

def draw_contours(axes, img, contours):
    print "Position1"
    from matplotlib.patches import Polygon
    axes.imshow(img)
    axes.axis('off')
    #print "TYPE CONTOURS=",contours
    for i, cnt in enumerate(contours):
        #print "I,CNT=",i,cnt
        #for j in cnt:
            #print "C=",j
        if cnt.shape[0]==1:
            continue
        # Delete un-required dimension
        cnt = np.squeeze(cnt)
        axes.add_patch(Polygon(cnt, fill=None, lw=0.1, color='b'))
        print "XAX=",cnt[:,0]
        print "YAX=",cnt[:,1]
        axes.plot(cnt[:, 0], cnt[:, 1],
                  marker='o', ms=4., mfc='red', mew=0., lw=0.)
