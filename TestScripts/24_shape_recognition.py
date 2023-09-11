import numpy as np
import cv2, sys

img = cv2.imread(sys.argv[1])
gray = cv2.imread(sys.argv[1],0)

ret,thresh = cv2.threshold(gray,30,150,0)
cv2.imwrite("test.png",thresh)

"""
for x in range(0,thresh.shape[0]):
    for y in range(0,thresh.shape[1]):
        print x,y,thresh[x,y]
"""

#contours,h = cv2.findContours(thresh,1,2)
contours,h = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

for cnt in contours:
    approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
    print(len(approx))
    if len(approx)==5:
        print("pentagon")
        cv2.drawContours(img,[cnt],0,255,-1)
    elif len(approx)==3:
        print("triangle")
        cv2.drawContours(img,[cnt],0,(0,255,0),-1)
    elif len(approx)==4:
        print("square")
        cv2.drawContours(img,[cnt],0,(0,0,255),-1)
    elif len(approx) == 9:
        print("half-circle")
        cv2.drawContours(img,[cnt],0,(255,255,0),-1)
    elif len(approx) > 15:
        print("circle")
        cv2.drawContours(img,[cnt],0,(0,255,255),-1)

cv2.imwrite("cont.png",img)

#cv2.imshow('img',img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
