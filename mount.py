import os,sys,glob
import time
import numpy as np
import socket
import Zoo
import MyDate
import BLFactory

import logging, logging.config

if __name__ == "__main__":

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    # beamline configure
    blf = BLFactory.BLFactory()

    logdir = blf.config.get("dirs", "zoologdir")
    logging_conf = blf.config.get("files", "logging_conf")

    # kuntaro_log
    d = MyDate.MyDate()
    time_str = d.getNowMyFormat(option="date")
    logname = f"{logdir}/zoo_{time_str}.log"
    logging.config.fileConfig(logging_conf, defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    zoo.mountSample(sys.argv[1],sys.argv[2])
    zoo.waitTillReady()
    zoo.disconnect()