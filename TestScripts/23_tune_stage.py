import os,sys,glob, datetime
import time
import numpy as np
import socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

import Zoo
import Device
import BeamsizeConfig

bss_port=5555

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    dev = Device.Device(ms)
    dev.init()

    zoo=Zoo.Zoo()
    zoo.connect()

    print(datetime.datetime.now())
    beamsize_index = zoo.getBeamsize()
    print(datetime.datetime.now())
    print("DISCO",datetime.datetime.now())
    print("Beamsize index from BSS=",beamsize_index)
    config_dir = "/isilon/blconfig/bl32xu/"
    bsc = BeamsizeConfig.BeamsizeConfig(config_dir)
    # bsc.readConfig()
    print(bsc.getBeamsizeAtIndex(beamsize_index))

    # Prep scintillator tuning
    dev.prepCapture()
    dev.finishCapture()

    zoo.disconnect()
