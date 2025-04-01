import socket,os,sys,datetime,cv2,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Device
import IboINOCC
import Zoo
import MyException
import time
import numpy as np
import LargePlateMatchingBC


            self.getImage("side",target_image,binning=4)
            angle,score,ymean=self.tune_phi(target_image)
            print "Fitting pint score = ",score

            if score > 100.0:
                self.dev.gonio.rotatePhiRelative(180.0)
                ifail+=1

            print "LOG=",ymean,self.pint_ymean
            diff_y=ymean-self.pint_ymean
            move_um=diff_y/pix_resol

            print "Dpix(y)=",diff_y
            print "Dpint[um]=",move_um

            if numpy.fabs(move_um) < 3.0:
                break

            elif numpy.fabs(move_um) < 1500.0:
                self.dev.gonio.movePint(move_um)
                ifail+=1

            if ifail>5:
                self.dev.gonio.rotatePhiRelative(180.0)

        return True

