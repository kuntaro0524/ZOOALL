import os,sys,glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
import time
import numpy as np
import socket
import Zoo
import Device
import IboINOCC


if __name__ == "__main__":
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    dev=Device.Device(s)
    dev.init()

    inocc=IboINOCC.IboINOCC(dev)
    backpath="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/Data/"

    dev.prepCenteringSideCamera()

    back_image = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/scbg4.png"

    # current phi 
    save_phi = dev.gonio.getPhi()
    dev.prepCenteringSideCamera()

    ofile = open("log.dat","w")
    ofile.write("# delphi,l_angle,l_score,l_meany,u_angle,u_score,u_meany,thick_mean,thick_std,diff_lu_angle\n")
    # Side camera background
    for delphi in range(-30,30,2):
        curr_phi = save_phi + delphi
        dev.gonio.rotatePhi(curr_phi)
        prefix = "rot%04d"%curr_phi
        imagefile = "%s/%s_%03d.png"%(backpath, prefix, curr_phi)
        inocc.getImage("side", imagefile, binning=4)
        l_angle, l_score, l_meany, u_angle, u_score, u_meany, thick_mean, thick_std =  \
             inocc.analyzePreciseSideCamera(imagefile, back_image, prefix=prefix)

        diff_lu_angle = l_angle - u_angle

        ofile.write("%5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f \n"%(
           curr_phi,l_angle,l_score,l_meany,u_angle,u_score,u_meany,thick_mean,thick_std,diff_lu_angle))

    dev.gonio.rotatePhi(save_phi)
