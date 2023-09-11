import sys,os,math,cv2,socket
import datetime
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import * 
import CryImageProc 
import CoaxImage
import BSSconfig

from File import *

import matplotlib
import matplotlib.pyplot as plt

# Modified 2015/07/22
# Y translation is changed 500um -> 1000um when the loop is 
# not found by rotating 360 deg.

class FittingForFacing:
    def __init__(self,phis,areas):
        self.phis=phis # simple array (not numpy array)
        self.areas=areas
        self.isDone=False

    def prep(self):
        self.phi_list=np.array(self.phis)
        self.area_list=np.array(self.areas)

        # Mean value in amplitude
        self.mean=np.mean(self.area_list)

        # Scipy fitting
        import scipy.optimize
    
        # initial guess for the parameters
        parameter_initial = np.array([0.0, 0.0, self.mean]) #a, b
    
        param_opt, covariance = scipy.optimize.curve_fit(self.func, self.phi_list, self.area_list, p0=parameter_initial)
        print("parameter =", param_opt)
    
        """ # DEBUGGING PLOT
            phi_tmp = np.linspace(0, 360, 100)
            ny = self.func(phi_tmp,param_opt[0],param_opt[1],param_opt[2])
            plt.plot(self.phi_list, self.area_list, 'o')
            plt.plot(phi_tmp, ny, '-')
            plt.show()
        """ 
    
        self.isDone=True
        return param_opt

    def func(self,phi,a,b,c):
        return a*np.cos(np.pi/90.0*(phi+b))+c

    def findFaceAngle(self):
        if self.isDone==False:
            param_opt=self.prep()

        phi_tmp = np.linspace(0, 180, 36)
        ny = self.func(phi_tmp,param_opt[0],param_opt[1],param_opt[2])

        min_value=1000000.0
        for phi,value in zip(phi_tmp,ny):
            if value < min_value:
                min_value=value
                phi_min=phi

        face_angle=phi_min+90.0
        print("findFaceAngle=%5.1f deg."%face_angle)
        return face_angle

    def check(self):
        if self.isDone==False:
            self.prep()
        phi_tmp = np.linspace(0, 360, 100)
        print(phi_tmp)
        plt.figure()
        plt.plot(self.phi_list,self.area_list,'r-')
        plt.plot(phi_tmp, self.p1[0]*np.cos(np.pi/90.0*phi_tmp)+self.p1[1], 'o')
        plt.show()

class Centering:
    def __init__(self,ms,sample_name="sample"):
        self.coi=CoaxImage.CoaxImage(ms)
        self.fname="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/test.ppm"
        self.isInit=False
        self.debug=False
        self.logdir="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Log/"
        self.backimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/BackImages/back-1811211645.ppm"
        self.bssconfig_file="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/bss/bss.config"

        self.sample_name=sample_name

        # Yamagiwa threshold
        # Longest distance threshold from Cmount position during Centering
        self.ddist_thresh=4.5 # [mm]

    def init(self):
        # Log directory is making for Today
        tds="%s"%(datetime.datetime.now().strftime("%y%m%d"))
        self.todaydir="%s/%s"%(self.logdir,tds)
        if os.path.exists(self.todaydir):
            print("%s already exists"%self.todaydir)
        else:
            os.makedirs(self.todaydir)
        self.ff=File(self.todaydir)
        print("Coax camera information will be acquired!")
        self.cip=CryImageProc.CryImageProc("test.ppm")
        self.cip.setBack(self.backimg)
        self.coi.set_zoom(14.0)
        # This is for Zoom -48000, 4x4 binning image
        self.cenx,self.ceny=self.coi.get_cross_pix()
        # 170425-Yamagiwa safety
        # Configure file for reading gonio mount position
        self.bssconfig=BSSconfig.BSSconfig(self.bssconfig_file)
        # Read Cmount position from configure file
        self.mx,self.my,self.mz=self.bssconfig.getCmount()

        # Force to remove the existing "test.ppm"
        try:
            os.system("\\rm -Rf %s"%self.fname)
        except MyException as ttt:
            raise MyException("Centering:init fails to remove the previous 'test.ppm'")
        return

        self.isInit=True

    def setYamagiwaSafety(self,largest_movement):
        self.ddist_thresho=largest_movement

    def setBack(self,backimg):
        print("setting back ground image to %s"%backimg)
        self.backimg=backimg

    def capture(self,image_name_abs_path):
        self.coi.get_coax_image(image_name_abs_path)

    def closeCapture(self):
        self.coi.closeCapture()

    def getGXYZphi(self):
        return self.coi.getGXYZphi()

    def moveGXYZphi(self,x,y,z,phi):
        self.coi.moveGXYZphi(x,y,z,phi)

    def fitAndFace(self,phi_list=[0,45,90,135]):
        #print phi_list
        area_list=[]

        #for phi,area in zip(self.phi_list,self.area_list):
            #print "DDDDDDDDDDDDDDDD:",phi,area

        for phi in phi_list:
            self.coi.rotatePhi(phi)

            # Make arrays
            ##self.coi.get_coax_image(self.fname, 200)
            self.coi.get_coax_image(self.fname, 40)     # for DFK72 YK@190315

            try:
                area=self.cip.getArea(self.fname,self.debug)
                print("PHI=",phi," AREA=",area)
                area_list.append(area)

            except MyException as ttt:
                raise MyException("fitAndFace: self.cip.getArea failed")

        # Fitting
        fff=FittingForFacing(phi_list,area_list)
        face_angle=fff.findFaceAngle()
        #self.coi.rotatePhi(face_angle-90.0)
        return float(face_angle)

    def coreCentering(self,phi_list,loop_size="small"):
        self.isFoundEdge=False
        if self.isInit==False:
            self.init()
        phi_area_list=[]
        n_good=0
        if self.debug: print("DEBUG LOOP in coreCentering")
        for phi in phi_list:
            self.coi.rotatePhi(phi)
            # Gonio current coordinate
            cx,cy,cz,phi=self.coi.getGXYZphi()
            # This background captured with speed=200
            # 4x4 binning zoom -48000pls
            try:
                for repetition in range(0,3):
                    # Capture
                    print("Capturing %s"%self.fname)
                    #self.coi.get_coax_image(self.fname, 200)
                    self.coi.get_coax_image(self.fname, 40)      # for DFK72 YK@190315
                    print("TTTTTTTTTTTTTTTTT",self.cip.backimg)
                    print("SETTINGGGGGG=",self.backimg)
                    grav_x,grav_y,xwidth,ywidth,area,xedge=self.cip.getCenterInfo(self.fname,self.debug,loop_size=loop_size)
                    print("RECENTERING XEDGE=",repetition,xedge)
                    if xedge==200:
                        gx,gy,gz,phi=self.coi.getGXYZphi()
                        cy=gy+0.5
                        self.coi.moveGXYZphi(gx,cy,gz,phi)
                    else:
                        self.isFoundEdge=True
                    if self.isFoundEdge==True:
                        break
                    time.sleep(1.0)
            except MyException as ttt:
                #raise MyException("edgeCentering failed")
                print("Go to next phi")
                continue

            #self.coi.get_coax_image(self.fname, 200)
            print("########### FINAL XEDGE=",xedge)
            x,y,z=self.coi.calc_gxyz_of_pix_at(xedge,grav_y,cx,cy,cz,phi)
            self.coi.moveGXYZphi(x,y,z,phi)
            l=phi,area
            phi_area_list.append(l)
            n_good+=1
        if n_good==0:
            raise MyException("coreCentering failed")
        return n_good,grav_x,grav_y,xwidth,ywidth,area,xedge

    def isYamagiwaSafe(self,gx,gy,gz):
        # Distance from mount position
        #print gx,gy,gz
        #print self.mx,self.my,self.mz
        dista=math.sqrt(pow((gx-self.mx),2.0)+pow((gy-self.my),2.0)+pow(gz-self.mz,2.0))
        if dista > self.ddist_thresh:
            print("deltaDistance=%5.2f mm"%dista)
            return False
        else:
            return True

    def edgeCentering(self,phi_list,ntimes,challenge=False,loop_size="small"):
        print("################### EDGE CENTERING ######################")
        n_good=0
        for i in range(0,ntimes):
            try:
                n_good,grav_x,grav_y,xwidth,ywidth,area,xedge=self.coreCentering(phi_list,loop_size=loop_size)
                print("NGOOD=",n_good)
                # Added 160514     
                # A little bit dangerous modification
                if challenge==True and n_good == len(phi_list):
                    break
            except MyException as tttt:
                print("Moving Y 2000um")
                gx,gy,gz,phi=self.coi.getGXYZphi()
                newgy=gy-2.0
                self.coi.moveGXYZphi(gx,newgy,gz,phi)
                if self.isYamagiwaSafe(gx,gy,gz)==False:
                    raise MyException("Movement was larger than threshold (Yamagiwa safety)")
        if n_good==0:
            raise MyException("edgeCentering failed")

        if self.debug==True:
            im = cv2.imread(self.fname)
            cv2.circle(im,(xedge,grav_y),2,(0,0,255),2)
            #img_log="edgeCentering_debug.jpg"
            img_log="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ec_debug.jpg"
            cv2.imwrite(img_log,im)

        print("################### EDGE CENTERING ENDED ######################")
        return n_good,grav_x,grav_y,xwidth,ywidth,area,xedge

    def facing(self,phi_list):
        if self.isInit==False:
            self.init()
        n_good=0
        min_area=9999999999.0
        for phi in phi_list:
            self.coi.rotatePhi(phi)
            ##self.coi.get_coax_image(self.fname, 200)
            self.coi.get_coax_image(self.fname, 40)   # for DFK72 YK@190315
            # Gonio current coordinate
            cx,cy,cz,phi=self.coi.getGXYZphi()
            # This background captured with speed=200  for ARTRAY
            # This background captured with speed=40 dor DFK72
            # 4x4 binning zoom -48000pls
            try:
                grav_x,grav_y,xwidth,ywidth,area,xedge= \
                    self.cip.getCenterInfo(self.fname,debug=False)
                print("PHI AREA=",phi,area)
            except MyException as ttt:
                #print ttt.args[1]
                continue
            if min_area > area:
                min_area=area
                saved_phi=phi
        phi_face=saved_phi+90.0
        self.coi.rotatePhi(phi_face)
        return phi_face

    # Final raster width/height are determined here
    # 2015/11/21 For Large loop : option "loop_size" is added to the argurments
    # small: -> roi_option=True for getCenterInfo
    def cap4width(self,loop_size="small"):
        if self.isInit==False:
            self.init()

        # Capture 
        ##self.coi.get_coax_image(self.fname, 200)
        self.coi.get_coax_image(self.fname, 40)    #for DFK72 YK@190315

        # For small loop
        grav_x,grav_y,xwidth,ywidth,area,xedge=self.cip.getCenterInfo(self.fname,loop_size=loop_size)

        # "SUPER" loop for takeshita3
        if loop_size=="super":
            xwidth=286 # 800um

        # Raster scan start/end x,y
        start_x=xedge
        cenx=grav_x
        end_x=int(xedge+xwidth)
        start_y=int(grav_y-int(ywidth/2.0))
        end_y=int(grav_y+int(ywidth/2.0))

        raster_cenx=cenx
        raster_ceny=grav_y

        im = cv2.imread(self.fname)
        cv2.rectangle(im,(start_x,start_y),(end_x,end_y),(0,255,0),1)
        cv2.circle(im,(cenx,grav_y),2,(0,0,255),2)
        img_log="%s/%04d_%s_raster.jpg"%(self.todaydir,self.ff.getNewIdx4(),self.sample_name)
        cv2.imwrite(img_log,im)
        #cv2.imshow("SHIKAKU",im)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        return xwidth,ywidth,raster_cenx,raster_ceny

    def doAll(self,ntimes=3,skip=False,loop_size="small",offset_angle=0.0):
        print("Start doAll")
        if self.isInit==False:
            self.init()
        phi_face=0.0

        print("Centering.doAll: self.cip.setBck!! backimage=%s"% self.backimg)
        self.cip.setBack(self.backimg)
        
        # Initial goniometer coordinate
        ix,iy,iz,iphi=self.coi.getGXYZphi()

        # Main loop
        if skip==False:
            # First centering
            phi_list=[0,45,90,135]
            # Loop centering for initial stages
            # ROI should be wider 
            try:
                self.edgeCentering(phi_list,2,challenge=True,loop_size="large")
            except MyException as ttt:
                try:
                    self.edgeCentering(phi_list,2,challenge=True,loop_size="large")
                except MyException as tttt:
                    raise MyException("Loop cannot be found")

            phi_list=[0,45,90,135]
            phi_face=self.fitAndFace(phi_list)

            # adds offset angles for plate-like crystals
            phi_face=phi_face+offset_angle
            phi_small=phi_face+90.0
            phi_list=[phi_small,phi_face]
            self.edgeCentering(phi_list,1)

        # Final centering
        cx,cy,cz,phi=self.coi.getGXYZphi()
        xwidth,ywidth,r_cenx,r_ceny=self.cap4width(loop_size)
        x,y,z=self.coi.calc_gxyz_of_pix_at(r_cenx,r_ceny,cx,cy,cz,phi)
        self.coi.moveGXYZphi(x,y,z,phi)
        cx,cy,cz,phi=self.coi.getGXYZphi()
        gonio_info=cx,cy,cz,phi
        #print xwidth,ywidth,cenx,ceny
        pix_size_um=self.coi.get_pixel_size()
        #print pix_size_um
        #if loop_size=="super":
            #raster_width=800.0
        #else:
            #raster_width=pix_size_um*float(xwidth)

        raster_width=pix_size_um*float(xwidth)
        raster_height=pix_size_um*float(ywidth)

        print("Width  = %8.1f[um]"%raster_width)
        print("Height = %8.1f[um]"%raster_height)
        print("Centering.doAll finished.")

        return raster_width,raster_height,phi_face,gonio_info

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #ms.connect(("192.168.163.1", 10101))
    ms.connect(("172.24.242.41", 10101))
    cnt=Centering(ms)
    phi_face=90

    start_time=datetime.datetime.now()
    #backimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/red_50000_back.ppm"
    backimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/BackImages/back-1904150917.ppm"
    backimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/back.ppm"

    cnt.setBack(backimg)
    rwidth,rheight,phi_face,gonio_info=cnt.doAll(ntimes=2,skip=False,loop_size="small")
    print(gonio_info,rwidth,rheight)
    end_time=datetime.datetime.now()
    cons_time=end_time-start_time
    print(start_time,end_time,cons_time)

    """
    start_time=datetime.datetime.now()
    #phi_list=[0,30,60,90,120,150,180,210,240,270,300,330,360]
    phi_list=[0,45,90,135]
    #cnt.edgeCentering(phi_list,4)
    cnt.init()
    cnt.fitAndFace(phi_list=phi_list)
    end_time=datetime.datetime.now()
    cons_time=end_time-start_time
    print start_time,end_time,cons_time
    """

    #phi_list=[0,30,60,90,120]
    #phi_face=cnt.facing(phi_list)
    #phi_usui=phi_face-90.0
    #phi_precise=np.arange(phi_usui-10.0,phi_usui+15,5)
    #print phi_precise
    #phi_face=cnt.facing(phi_precise)

    #phi_list=[phi_face,phi_face+90.0]
    #n_good,grav_x,grav_y,xwidth,ywidth,area,xedge=cnt.edgeCentering(phi_list,1)
    #xwidth,ywidth,cenx,ceny=cnt.cap4width()
    #print xwidth,ywidth,cenx,ceny
    #x,y,z=cnt.coi.calc_gxyz_of_pix_at(xcen,grav_y,cx,cy,cz,phi)
    #cnt.coi.moveGXYZphi(x,y-0.25,z,phi)
    #cnt.cip.getCenterInfo(cnt.fname)

    ms.close()
