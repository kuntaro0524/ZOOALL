import os,sys,socket
sys.path.append("../")
import Gonio
import CryImageProc
import Capture
import CoaxImage

host = '172.24.242.59'
port = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

gonio=Gonio.Gonio(s)
cap = Capture.Capture()
cip=CryImageProc.CryImageProc("test.ppm")
coi = CoaxImage.CoaxImage(s)

print gonio.getXYZmm()

# gonio save position
sx, sy, sz = gonio.getXYZmm()
phi = gonio.getPhi()

cappath = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs"
backfile = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/back.ppm"

for phi in [0,45,90]:
    gonio.rotatePhi(phi)

    cap.prep()
    filename = "%s/centest.ppm" % (cappath)
    cap.capture(filename)
    cip.setBack(backfile)
    grav_x,grav_y,xwidth,ywidth,area,xedge = cip.getCenterInfo(filename,debug=True,loop_size="large")
    x,y,z=coi.calc_gxyz_of_pix_at(xedge,grav_y,sx,sy,sz,phi)
        
    print sx,sy,sz
    print x,y,z
    gonio.moveXYZmm(x,y,z)
