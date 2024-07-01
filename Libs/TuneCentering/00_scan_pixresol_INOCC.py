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
step = 20.0

scan_prot = "Vertical"

if scan_prot == "Horizontal" or scan_prot == "Both":
    ofile=open("scan_pixres_hori.dat","w")

    for i in range(0,10):
        gonio.moveTrans(step)
        cap.prep()
        filename = "%s/gpix_%02d.ppm" % (cappath,i)
        cap.capture(filename)
        cip.setBack(backfile)
        grav_x,grav_y,xwidth,ywidth,area,xedge = cip.getCenterInfo(filename,debug=True,loop_size="large")
    
        pstep = step*i
        ofile.write("%8.5f %8d\n"%(pstep, xedge))
    
    ofile.close()
    gonio.moveXYZmm(sx,sy,sz)

if scan_prot == "Vertical" or scan_prot == "Both":
    ofile=open("scan_pixres_vert.dat","w")
    
    for i in range(0,10):
        gonio.moveUpDown(step)
        cap.prep()
        filename = "%s/gpix_%02d.ppm" % (cappath,i)
        cap.capture(filename)
        cip.setBack(backfile)
        grav_x,grav_y,xwidth,ywidth,area,xedge = cip.getCenterInfo(filename,debug=True,loop_size="large")
    
        pstep = step*i
        ofile.write("%8.5f %8d\n"%(pstep, grav_y))
    ofile.close()
    gonio.moveXYZmm(sx, sy, sz)

