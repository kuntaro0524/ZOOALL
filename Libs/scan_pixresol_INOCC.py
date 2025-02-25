import os,sys,socket
import Gonio
import CryImageProc
import Capture

host = '172.24.242.59'
port = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

gonio=Gonio.Gonio(s)
cap = Capture.Capture()
cip=CryImageProc.CryImageProc("test.ppm")

print gonio.getXYZmm()

# gonio save position
sx, sy, sz = gonio.getXYZmm()

cappath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs"
backfile = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/back.ppm"
cap = Capture()
step = 20.0

for i in range(0,20):
    gonio.moveTrans(step)
    cap.prep()
    filename = "%s/%s.ppm" % (cappath,sys.argv[1])
    cap.capture(filename)
    cip.setBack(backfile)
     cip.getCenterInfo(infile,debug=True,loop_size="large")

