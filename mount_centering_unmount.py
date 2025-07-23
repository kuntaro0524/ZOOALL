import os, sys, glob
import time
import numpy as np
import socket

#sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
#import MXserver
import Zoo
import Date
import logging
import logging.config
import datetime
from configparser import ConfigParser, ExtendedInterpolation
import BLFactory
import INOCC

if __name__ == "__main__":
    config = ConfigParser(interpolation=ExtendedInterpolation())
    # read configure file(beamline.init)
    ini_file = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(ini_file)

    zoo = Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    # Logging setting
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "./mount_unmount_%s.log" % (time_str)

    logging_conf = config.get('files', 'logging_conf')
    logging.config.fileConfig(logging_conf, defaults={'logfile_name': logname})
    logger = logging.getLogger('SPACE')
    os.chmod(logname, 0o666)

    # Goniometer setting
    blf = BLFactory.BLFactory()
    blf.initDevice()

    zooroot = config.get('dirs', 'zooroot')
    test_dir = os.environ['PWD']
    inocc = INOCC.INOCC(blf, test_dir)
    picture="raster.png"
    inocc.setRasterPicture(os.path.abspath(test_dir + "/" + picture))
    phi_face = 90
    # back image path read from 'beamline.ini'
    backpath = config.get('dirs', 'backimage_dir')
    backimg = os.path.join(backpath, "back.ppm")
    inocc.setBack(backimg)

    num = 0
    total_pins = 0
    while num < 10:
        for trayid in ["CPS1023"]:
            for pinid in [6,7,8,9,10]:
                logger.info("Tray %s - Pin %02d mount started." % (trayid, pinid))
                try:
                    zoo.mountSample(trayid, pinid)
                    zoo.waitTillReady()
                    # def doAll(self, ntimes=3, skip=False, loop_size=600.0, offset_angle=0.0):
                    blf.device.prepCentering()
                    rwidth, rheight, phi_face, gonio_info = inocc.doAll(ntimes=2, skip=False, loop_size=500.0)
                except MyException as ttt:
                    exception_message = ttt.args[0]
                    #print("Sample mounting failed. Contact BL staff!")
                    #sys.exit(1)
                    # Accident case
                    if exception_message.rfind('-1005000003') != -1:
                        message = "SPACE accident occurred! Please contact a beamline scientist."
                        message += "Check if 'puckid' matches in CSV file and SPACE server."
                        #logger.error(message)
                        #logger.critical(message)
                        sys.exit()
                    if exception_message.rfind('-1005000004') != -1:
                        message = "SPACE accident occurred! Please contact a beamline scientist.\n"
                        message += "L-head value is negative in picking up the designated pin."
                        #logger.error(message)
                        #logger.critical(message)
                        sys.exit()
                    elif exception_message.rfind('-1005100001') != -1:
                        message = "'SPACE_WARNING_existense_pin_%s_%s'" % (trayid, pinid)
                        #logger.warning(message)
                        zoo.skipSample()
                        #logger.info("Go to the next sample...")
                        #logger.info("Breaking the loop of %s-%02d" % (trayid, pinid))
                        #return
                    elif exception_message.rfind('-1005100002') != -1:
                        message = "'SPACE_WARNING_push_too_much_%s_%s'" % (trayid, pinid)
                        #logger.warning(message)
                        zoo.skipSample()
                        #logger.info("Go to the next sample...")
                        #logger.info("Breaking the loop of %s-%02d" % (trayid, pinid))
                        #return
                    elif exception_message.rfind('-1005100003') != -1:
                        message = "'SPACE_WARNING_rotate_too_much_%s_%s'" % (trayid, pinid)
                        #logger.warning(message)
                        zoo.skipSample()
                        #logger.info("Go to the next sample...")
                        #logger.info("Breaking the loop of %s-%02d" % (trayid, pinid))
                        #return
                    # 220629 K.Hirata added from BSS log.
                    elif exception_message.rfind('-1005100007') != -1:
                        message = "'Failed to pickup the sample pin from the tray. %s_%s'" % (trayid, pinid)
                        #logger.warning(message)
                        zoo.skipSample()
                        #logger.info("Go to the next sample...")
                        #logger.info("Breaking the loop of %s-%02d" % (trayid, pinid))
                        #return
                    else:
                        message = "Unknown Exception: %s. Program terminates" % ttt
                        #logger.error(message)
                        sys.exit()

                logger.info("Tray %s - Pin %02d dismount started." % (trayid, pinid))
                time.sleep(25)
                zoo.dismountCurrentPin()
                logger.info("%s - %02d dismount finished." % (trayid, pinid))
                zoo.waitTillReady()
                total_pins += 1
                logger.info("%5d pins were finished." % total_pins)
        num += 1
    zoo.disconnect()


