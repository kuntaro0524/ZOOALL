import os,sys,socket
sys.path.append("../")
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
cip.setLogDir("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/TuneCentering/")

# gonio save position
sx, sy, sz = gonio.getXYZmm()

cappath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/TuneCentering/"
backfile = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/TuneCentering/back_re.ppm"

cap.prep()
filename = "%s/check.ppm"%cappath
cap.capture(filename)
cip.setBack(backfile)
grav_x,grav_y,xwidth,ywidth,area,xedge = cip.getCenterInfo(filename,debug=True,loop_size="large")
