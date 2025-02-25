import os,sys,glob
import time
import numpy as np
import socket
import Zoo
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import logging
import logging.config


if __name__ == "__main__":

    logname="test.log"
    logging.config.fileConfig('/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()
    time.sleep(2.0)
    #zoo.autoCentering()
    #zoo.stop()
    puckid = sys.argv[1]
    pinid = sys.argv[2]
    try:
        zoo.mountSample(puckid, pinid)
        zoo.waitTillReady()
    except MyException, ttt:
        print "Failed", ttt.args[0]
    zoo.disconnect()
