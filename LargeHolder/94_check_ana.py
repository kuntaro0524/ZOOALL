import cv2,sys
import matplotlib.pyplot as plt
import numpy as np

# ROI definition
xmin=320
xmax=430

target = "Data/sc4_1902042358.png"
back = "../Images/scbg4.png"
prefix = "testing"

target_img = cv2.imread(target)
back_img = cv2.imread(back)

data_file = "%s.dat"%prefix
dfile = open(data_file,"w")

tg = cv2.cvtColor(target_img,cv2.COLOR_BGR2GRAY)
bg = cv2.cvtColor(back_img,cv2.COLOR_BGR2GRAY)
dimg=cv2.absdiff(tg,bg)
cv2.imwrite("diff.png",dimg)

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

def get_contours(contours):
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

def find_lower_edge(roi_xy):
    lower_edge=[]
    # Loop 1
    for xscan in range(xmin,xmax):
        ymax=0
        xsave=ysave=0
        # Loop2
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
        #print "CONTOUR=",xsave,ysave
        lower_edge.append((xsave,ysave))

    return lower_edge

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
        #print "CONTOUR=",xsave,ysave
        upper_edge.append((xsave,ysave))

    return upper_edge

# Fitting 1D for X,Y of lower-edge of the loop
# from side view camera
def fitting_pix_line(xy_array):
    # Making X,Y numpy array
    xlist=[]
    ylist=[]
    for x,y in xy_array:
        #print "OBS=,",x,y
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
        #print "FITTED= ",x,a*x+b
        residual=(a*x+b)-y
        score+=residual*residual

    final_score=score/float(len(xa))
    
    #print "a=",a
    #print "b=",b

    meany = ya.mean()

    angle=np.degrees(np.arctan(a))
    
    return angle,final_score,meany

def analyzeWidth(lower_contour, upper_contour):

    dy_list = []
    for each_lc in lower_contour:
        lx,ly = each_lc
        for each_uc in upper_contour:
            ux,uy = each_uc
            if ux == lx:
                dy = uy - ly
                dy_list.append(dy)
                continue

    dya = np.array(dy_list)
    thick_mean = dya.mean()
    thick_std = dya.std()
    print "Thick mean = ",thick_mean,thick_std
    return thick_mean, thick_std

##
for param in [20,30,50]:
    baseimg = cv2.imread(target)
    blur = cv2.bilateralFilter(dimg,15,param,param)
    cv2.imwrite("blur%02d.png"%param,blur)
    result1 = cv2.threshold(blur,10,150,0)[1]
    cv2.imwrite("bin%02d.png"%param,result1)
    # Contour finding
    cont1, hi1 = cv2.findContours(result1 ,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt=squeeze_contours(cont1)
    cv2.drawContours(baseimg,cont1,-1,(0,255,0),3)
    roi_xy=contour_roi(cnt)
    lower_edge=find_lower_edge(roi_xy)
    upper_edge = find_upper_edge(roi_xy)
    l_angle,l_score,l_meany=fitting_pix_line(lower_edge)
    u_angle,u_score,u_meany=fitting_pix_line(upper_edge)
    #print param,angle,"score=",score,"meany=",meany

    for lower in lower_edge:
        lx,ly = lower
        dfile.write("lower: %3d %3d\n"%(lx,ly))
    for upper in upper_edge:
        ux,uy = upper
        dfile.write("upper: %3d %3d\n"%(ux,uy))

    l_text = "Lower angle = %5.1f score = %5.1f meany = %5.3f"%(l_angle,l_score,l_meany)
    u_text = "Upper angle = %5.1f score = %5.1f meany = %5.3f"%(u_angle,u_score,u_meany)
    cv2.putText(baseimg, l_text, (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255,255,255), thickness=1)
    cv2.putText(baseimg, u_text, (20,50), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255,255,255), thickness=1)

    line_start_x = xmin
    line_end_x = xmax
    l_line_start_y = int(l_meany)
    u_line_start_y = int(u_meany)
    xlen = xmax - xmin

    l_diff_y = int(xlen*np.tan(np.radians(l_angle)))
    u_diff_y = int(xlen*np.tan(np.radians(u_angle)))

    print l_diff_y,u_diff_y

    thick_mean, thick_std = analyzeWidth(lower_edge, upper_edge)

    thick_text = "Thickness mean = %5.1f Thickness std = %5.3f"%(thick_mean, thick_std)
    #cv2.putText(baseimg, thick_text, (20,450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), thickness=1)
    cv2.putText(baseimg, thick_text, (20,450), cv2.FONT_HERSHEY_SIMPLEX, 0.70,(0,0,255),2)

    cv2.line(baseimg, (xmin,l_line_start_y), (xmax,l_line_start_y+l_diff_y),(0,0,255),3)
    cv2.line(baseimg, (xmin,u_line_start_y), (xmax,u_line_start_y+u_diff_y),(0,0,255),3)
    cv2.imwrite("%s_ana_%02d.png"%(prefix,param),baseimg)
