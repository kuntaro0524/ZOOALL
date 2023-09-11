#-*- coding:utf-8 -*-
import sys
import cv
import time
import v4l2
from fcntl import ioctl

cv.NamedWindow("camera", 1)

# チャンネル選択(Composite3)
fd=open('/dev/video0', 'rw')
ioctl(fd, v4l2.VIDIOC_S_INPUT, v4l2.c_int(2))

capture = cv.CaptureFromCAM(0)

capimage=sys.argv[1]

img = cv.QueryFrame(capture)
cv.SaveImage(capimage,img);
