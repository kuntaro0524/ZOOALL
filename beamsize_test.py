import os, sys, glob
import time, datetime
import numpy as np
import socket

from MyException import *
import logging
import logging.config
from configparser import ConfigParser, ExtendedInterpolation

import Zoo

if __name__ == "__main__":
    # Logging setting
    # open configure file
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(config_path)
    logging_conf_file = config.get("files", "logging_conf")
    logname = os.path.join(config.get("dirs","zoologdir"), "Zoo.log")
     
    logging.config.fileConfig(logging_conf_file,defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    zoo = Zoo.Zoo()
    zoo.connect()
    # print beamsize_index to console
    beamsize_index=zoo.getBeamsize()
    print("before beamsize index=%5d"%beamsize_index)
    #beamsize_index=zoo.getBeamsize()
    zoo.setBeamsize(int(sys.argv[1]))
    # print beamsize_index to console
    beamsize_index=zoo.getBeamsize()
    print("after beamsize index=%5d"%beamsize_index)
    
    zoo.waitTillReady()
    zoo.disconnect()