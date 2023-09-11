import os, sys, glob
import time
import numpy as np
import socket

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import MXserver
import Zoo
import Date
import logging

if __name__ == "__main__":
    zoo = Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    # Logging setting
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "./mount_unmount_%s.log" % (time_str)

    print("changing mode of %s" % logname)
    logging.config.fileConfig('/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('SPACE')

    total_pins = 0

    num = 0
    while num < 5:
        for trayid in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            for pinid in range(1, 17):
                logger.info("Tray %s - Pin %02d mount started." % (trayid, pinid))
                try:
                    zoo.mountSample(trayid, pinid)
                    zoo.waitTillReady()
                except MyException as ttt:
                    print("Sample mounting failed. Contact BL staff!")
                    sys.exit(1)
                logger.info("Tray %s - Pin %02d mount finished." % (trayid, pinid))
                logger.info("Waiting for 2 minutes from now")

                time.sleep(120)
                logger.info("Tray %s - Pin %02d dismount started." % (trayid, pinid))
                zoo.dismountCurrentPin()
                logger.info("%s - %02d dismount finished." % (trayid, pinid))
                zoo.waitTillReady()
                total_pins += 1
                logger.info("%5d pins were finished." % total_pins)

        num += 1

    zoo.disconnect()
