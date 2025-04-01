import os,sys,glob
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
import time
import numpy as np
import socket
import Zoo
import Device
import IboINOCC
import LargePlateMatchingBC

if __name__ == "__main__":
    blanc = '172.24.242.41'
    b_blanc = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((blanc,b_blanc))

    puckid="CPS0296"
    #pinid=1
    #### ZOO
    dev=Device.Device(s)
    dev.init()

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    x0 = 254
    y0 = 274
    trans_resol=0.006727
    vert_resol=0.0092727

    lpmbc=LargePlateMatchingBC.LargePlateMatchingBC()

    for pinid in [6]:
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
                print "Program could not align the loop"
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
        min_thick = 9999.9999
        l_angle_set = 0.0
        l_mean_set = 0.0
        l_score_set = 0.0
        diff_angle_set = 0.0
        for delphi in range(-10,12,2):
            curr_phi = save_phi + delphi
            dev.gonio.rotatePhi(curr_phi)
            prefix = "rot%04d"%curr_phi
            imagefile = "%s/%s_%03d.png"%(pin_path, prefix, curr_phi)
            inocc.getImage("side", imagefile, binning=4)
            l_angle, l_score, l_meany, u_angle, u_score, u_meany, thick_mean, thick_std =  \
                inocc.analyzePreciseSideCamera(imagefile, back_image, prefix=prefix,proc_dir = pin_path)

            print "L score = ", l_score
            if min_thick > thick_mean:
                min_thick = thick_mean
                l_angle_set = l_angle
                l_meany = l_mean_set
                l_score_set = l_score
                # Angle based on horizontal axis of the coax image
                # Absolute phi angle for facing is ....
                diff_angle_set = 2.8 - l_angle_set
                abs_target_phi = curr_phi + diff_angle_set
                print"Lower angle = %s D(angle) = %s Final = %s"%(l_angle_set, diff_angle_set,abs_target_phi)
            
            diff_lu_angle = l_angle - u_angle
    
            ofile.write("%5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f \n"%(
            curr_phi,l_angle,l_score,l_meany,u_angle,u_score,u_meany,thick_mean,thick_std,diff_lu_angle))
    
        dev.gonio.rotatePhi(abs_target_phi)
        imagefile = "%s/%s_%s_final.png"%(pin_path, prefix, abs_target_phi)
        inocc.getImage("side", imagefile, binning=4)

        # Center of otehon holder Y mean
        target_pint_y = 263.0
        pix_resol=0.0319

        diff_y = l_mean_set - target_pint_y
        move_um = diff_y / pix_resol

        print "Dpix(y)=",diff_y
        print "Dpint[um]=",move_um

        if numpy.fabs(move_um) < 3.0:
            continue

        elif numpy.fabs(move_um) < 500.0:
            self.dev.gonio.movePint(move_um)
            ifail+=1

        # Translational alignment 
        dev.prepCenteringBackCamera()
        initial_phi=dev.gonio.getPhi()

        # Save position
        sx,sy,sz=dev.gonio.getXYZmm()

        for i in range(0,3):
            imgname="%s/bc_align.png"%(pin_path)
            inocc.getImage("back",imgname,binning=2)
            max_loc=lpmbc.getHoriVer(imgname)
            x,y=max_loc
    
            # diff
            diffx=x-x0
            diffy=y-y0
    
            # movement
            trans_um=diffx/trans_resol
            vert_um=diffy/vert_resol
        
            print "TRANS=",diffx,trans_um
            print "VERT =",diffy,vert_um
        
            if np.fabs(trans_um) < 2000.0:
                dev.gonio.moveTrans(trans_um)
            if np.fabs(vert_um) < 2000.0:
                dev.gonio.moveUpDown(vert_um)
