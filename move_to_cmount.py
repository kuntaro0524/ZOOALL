import cv2,sys, time, os, socket
import matplotlib.pyplot as plt
import numpy as np
import copy, glob
import CryImageProc
import BLFactory
from configparser import ConfigParser, ExtendedInterpolation
import logging

if __name__=="__main__":
    blf = BLFactory.BLFactory()
    blf.initDevice()

    # read configure file(beamline.init)
    config = ConfigParser(interpolation=ExtendedInterpolation())
    ini_file = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(ini_file)
    zooroot = config.get('dirs', 'zooroot')

    dev = blf.device
    dev.init()
    gonio = blf.getGoniometer()
    x,y,z = gonio.getXYZmm()
    print(("current_xyz=",x,y,z))

    # move to Cmount position
    # Cmount position
    x,y,z=blf.bss_config.getCmount()
    gonio.moveXYZmm(x,y,z)

    x,y,z = gonio.getXYZmm()
    print(("current_xyz=",x,y,z))