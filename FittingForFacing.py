import cv2,sys,datetime, socket, time
import matplotlib.pyplot as plt
import numpy as np
import copy

sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")

from MyException import *
import CryImageProc
import Device

# Modified 2015/07/22
# Y translation is changed 500um -> 1000um when the loop is 
# not found by rotating 360 deg.

class FittingForFacing:
    def __init__(self,phis,areas,logpath= "./"):
        self.phis=phis # simple array (not numpy array)
        self.areas=areas
        self.isDone=False
        self.logpath = logpath

    def prep(self):
        self.phi_list=np.array(self.phis)
        self.area_list=np.array(self.areas)

        # Observed min phi & area
        imin = self.area_list.argmin()
        self.phi_min_obs = self.phi_list[imin]
        self.area_min_obs = self.area_list[imin]

        # Mean value in amplitude
        self.mean=np.mean(self.area_list)

        # Scipy fitting
        import scipy.optimize

        # initial guess for the parameters
        parameter_initial = np.array([0.0, 0.0, self.mean]) #a, b

        param_opt, covariance = scipy.optimize.curve_fit(self.func, self.phi_list, self.area_list, p0=parameter_initial)

        print "phi_list = ", self.phi_list
        print "area_list = ", self.area_list
        print "parameter =", param_opt

        # DEBUGGING PLOT
        plt.cla()
        plt.clf()
        phi_tmp = np.linspace(0, 360, 100)
        ny = self.func(phi_tmp,param_opt[0],param_opt[1],param_opt[2])
        plt.plot(self.phi_list, self.area_list, 'o')
        plt.plot(phi_tmp, ny, '-')
        plt.savefig("%s/fitted.png" % self.logpath)

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

        print "PHI  Fitted = %10.2f Obs = %10.2f"%(phi_min, self.phi_min_obs)
        print "Area Fitted = %10.2f Obs = %10.2f"%(min_value, self.area_min_obs)

        if min_value > self.area_min_obs:
            phi_min = self.phi_min_obs

        face_angle=phi_min+90.0
        print "findFaceAngle=%5.1f deg."%face_angle
        return face_angle

    def check(self):
        if self.isDone==False:
            self.prep()
        phi_tmp = np.linspace(0, 360, 100)
        print phi_tmp
        plt.figure()
        plt.plot(self.phi_list,self.area_list,'r-')
        plt.plot(phi_tmp, self.p1[0]*np.cos(np.pi/90.0*phi_tmp)+self.p1[1], 'o')
        plt.show()
    
if __name__=="__main__":
    lines = open(sys.argv[1], "r").readlines()

    phis = []
    areas = []

    logpath = sys.argv[2]

    for line in lines:
        cols = line.split()
        phi = float(cols[0])
        area = float(cols[1])
        phis.append(phi)
        areas.append(area)

    ffff = FittingForFacing(phis, areas, logpath = logpath)
    face_angle = ffff.findFaceAngle()

    print "eog %s/fitted.png" % logpath
