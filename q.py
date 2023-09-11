import cv2,sys

im = cv2.imread(sys.argv[1])
# Gray scale
gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
# Gaussian blur
blur = cv2.GaussianBlur(gray,(3,3),0)
# 2 valuize
th = cv2.threshold(blur,127,255,0)[1]

cv2.imshow("SHIKAKU",th)
cv2.waitKey(0)
cv2.destroyAllWindows()

