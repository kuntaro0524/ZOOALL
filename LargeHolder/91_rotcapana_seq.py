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

    puckid="CPS1923"
    pinid=1
    #### ZOO
    dev=Device.Device(s)
    dev.init()

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    for pinid in [2,3,4,5,6,7,8,9,10,11]:
        try:
            zoo.mountSample(puckid,pinid)
            zoo.waitTillReady()
        except MyException, ttt:
            print "Sample mounting failed. Contact BL staff!"
            sys.exit(1)
    
        inocc=IboINOCC.IboINOCC(dev)
        # preparation
        dev.prepCenteringBackCamera()
    
        #def captureMatchBackcam(self,picture_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/Templates/BackCamera/"):
        n_fail = 0
        while(1):
            max_similarity=inocc.captureMatchBackcam()
            if max_similarity > 0.80:
                break
            else:
                n_fail +=1
            if n_fail > 3:
                break

        # pin path
        pp = "%s-%02d"%(puckid,pinid)
        pin_path="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/LargeHolder/%s/"%pp
        if os.path.exists(pin_path)==False:
            os.makedirs(pin_path)
    
        dev.prepCenteringSideCamera()
        back_image = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Images/scbg4.png"
    
        # current phi 
        save_phi = dev.gonio.getPhi()
        dev.prepCenteringSideCamera()
    
        ofile = open("%s/log.dat"%pin_path,"w")
        ofile.write("# delphi,l_angle,l_score,l_meany,u_angle,u_score,u_meany,thick_mean,thick_std,diff_lu_angle\n")
        # Side camera background
        for delphi in range(-30,30,2):
            curr_phi = save_phi + delphi
            dev.gonio.rotatePhi(curr_phi)
            prefix = "rot%04d"%curr_phi
            imagefile = "%s/%s_%03d.png"%(pin_path, prefix, curr_phi)
            inocc.getImage("side", imagefile, binning=4)
            l_angle, l_score, l_meany, u_angle, u_score, u_meany, thick_mean, thick_std =  \
                inocc.analyzePreciseSideCamera(imagefile, back_image, prefix=prefix,proc_dir = pin_path)
    
            diff_lu_angle = l_angle - u_angle
    
            ofile.write("%5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f \n"%(
            curr_phi,l_angle,l_score,l_meany,u_angle,u_score,u_meany,thick_mean,thick_std,diff_lu_angle))
    
        dev.gonio.rotatePhi(save_phi)
