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

    beamsize_index= int(sys.argv[1])
    # Logging setting
    # open configure file
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
    config.read(config_path)


    zoo = Zoo.Zoo()
    zoo.connect()

    previous_index=zoo.getBeamsize()
    print("Current beamsize index: %d" % previous_index)

    zoo.setBeamsize(beamsize_index)
    print("Set was completed")

    curr_index=zoo.getBeamsize()
    print("Current beamsize index: %d" % curr_index)