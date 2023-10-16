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

    logname = "./inocc.log"
    logging_conf = config.get('files', 'logging_conf')
    logging.config.fileConfig(logging_conf, defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')
    os.chmod(logname, 0o666)

    test_dir = os.path.join(zooroot, "TestScripts")
    bfile = config.get('files', 'backimg')

    loop_size = 600.0
    option = "gravity"

    outfile = open("gonio.dat", "w")

    dev = blf.device
    dev.init()

    s=0
    gonio = blf.getGoniometer()
    x,y,z = gonio.getXYZmm()
    print(("current_xyz=",x,y,z))

    y_init = y

    step_h = 20.0 # um

    for i in range(0,20):
        d_hori_mm = i * step_h / 1000.0
        y_mod = y_init + d_hori_mm

        d_hori_um = d_hori_mm * 1000.0

        gonio.moveXYZmm(x, y_mod, z)

        time.sleep(1.0)
        filename = "%s/cap_%f.ppm"%(test_dir, d_hori_mm)
        logdir = "%s/%04d/" % (test_dir, i)

        dev.capture.capture(filename)
        cip = CryImageProc.CryImageProc(logdir = test_dir)
        cip.setImages(filename, bfile)
        cont = cip.getContour()
        xtarget, ytarget, area, hamidashi_flag = cip.getCenterInfo(loop_size = loop_size, option = "top")
        outimg = "top_%f.png" % d_hori_mm
        outimg_abs = os.path.join(test_dir, outimg)
        cip.drawTopOnTarget((xtarget, ytarget), outimg_abs)

        outfile.write("%s %6.3f TARGET X,Y = %5.1f %5.1f\n" % (filename, d_hori_um, xtarget, ytarget))
