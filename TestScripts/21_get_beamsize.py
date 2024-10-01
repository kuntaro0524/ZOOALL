import os,sys,glob, datetime
import time
import numpy as np
import socket

import Zoo
from configparser import ConfigParser, ExtendedInterpolation
import BeamsizeConfig
import logging

bss_port=5555

if __name__ == "__main__":
    # Logging setting
    # open configure file
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    print(config_path)
    config.read(config_path)

    zoo = Zoo.Zoo()
    zoo.connect()
    # zoo.setBeamsize(0)
    beamsize_index=zoo.getBeamsize()
    print("Beamsize index: %d" % beamsize_index)