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

cv2.imwrite("sgb.png",sgb)

fig, axes = plt.subplots(1, 1, figsize=(8, 5))

method_names = ['cv2.CHAIN_APPROX_NONE']
methods = [cv2.CHAIN_APPROX_NONE]
fig, axes_list = plt.subplots(2, 2, figsize=(10, 10))

# ROI definition
#xmin=330
#xmax=450
xmin=292
xmax=398

# This routine squeeze contours 
# Reduce the dimensions
def squeeze_contours(contours):
    new_array=[]
    # contours structure
    # found contours are included in 'contours'
    # This loop is a treatment for each 'found contour'.
    print "Found contours=",len(contours)
    if len(contours)!=1:
        print "Found contours are not single."

    for i, cnt in enumerate(contours):
        #print "Before squeeze:",cnt.shape
        # Delete non-required dimension
        cnt = np.squeeze(cnt)
        #print "after squeeze:",cnt.shape
        #cnt=cnt[cnt[:,0].argsort()]
        new_array.append(cnt)

    return new_array

def ana_contours(contours):
    for contour in contours:
        if len(contour.shape) == 1:
            print contour
            continue
        else:
            ndata,dummy=contour.shape
            for i in range(0,ndata):
                print contour[i]

def contour_roi(contours):
    roi_xy=[]
    def isInRange(x):
        if x >= xmin and x <= xmax:
            return True
        else:
            return False
    for contour in contours:
        if len(contour.shape) == 1:
            x,y=contour
            if isInRange(x):
                roi_xy.append((x,y))
            continue
        else:
            ndata,dummy=contour.shape
            for i in range(0,ndata):
                x,y=contour[i]
                if isInRange(x):
                    roi_xy.append((x,y))
    return roi_xy

def find_under_edge(roi_xy):
    under_edge=[]
    for xscan in range(xmin,xmax):
        ymax=0
        xsave=ysave=0
        for x,y in roi_xy:
            if xscan==x:
                if y > ymax:
                    ymax=y
                    xsave=x
                    ysave=y
                else:
                    continue
            else:
                continue
        print "CONTOUR=",xsave,ysave
        under_edge.append((xsave,ysave))

    return under_edge

def find_upper_edge(roi_xy):
    upper_edge=[]
    for xscan in range(xmin,xmax):
        ymin=999
        xsave=ysave=0
        for x,y in roi_xy:
            if xscan==x:
                if y < ymin:
                    ymin=y
                    xsave=x
                    ysave=y
                else:
                    continue
            else:
                continue
        print "CONTOUR=",xsave,ysave
        upper_edge.append((xsave,ysave))

    return upper_edge

# Fitting 1D for X,Y of under-edge of the loop
# from side view camera
def fitting_pix_line(xy_array):
    # Making X,Y numpy array
    xlist=[]
    ylist=[]
    for x,y in xy_array:
        xlist.append(x)
        ylist.append(y)
    
    xa=np.array(xlist)
    ya=np.array(ylist)

    # Linear arregression
    a,b=np.polyfit(xa,ya,1)
    
    # scoring the fitting
    score=0.0
    
    # Print log
    for x,y in zip(xa,ya):
        print "FITTED=,",x,a*x+b
        residual=(a*x+b)-y
        score+=residual*residual

    final_score=score/float(len(xa))
    
    print "a=",a
    print "b=",b

    angle=np.degrees(np.arctan(a))
    
    return angle,final_score

for axes, method, name in zip(axes_list.ravel(), methods, method_names):
    contours, hierarchy = cv2.findContours(sgb, cv2.RETR_EXTERNAL, method)
    cnt=squeeze_contours(contours)
    cv2.drawContours(gim,contours,-1,(0,255,0),3)
    roi_xy=contour_roi(cnt)
    under_edge=find_under_edge(roi_xy)
    angle,score=fitting_pix_line(under_edge)
    cv2.imwrite("contour.png",gim)
    print sys.argv[1],angle,score
