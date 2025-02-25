import sys,os,math,cv2,socket,time
import numpy as np

gx=1.0
gy=0.0
gz=0.0

px=0.0
py=1.0
pz=0.0

v1=np.array((gx,gy,gz))
v2=np.array((px,py,pz))

print v1-v2
