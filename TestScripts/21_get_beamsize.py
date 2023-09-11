import os,sys,glob, datetime
import time
import numpy as np
import socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

import Zoo
import BeamsizeConfig

bss_port=5555

if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()
    print(datetime.datetime.now())
    try:
        beamsize_index = zoo.getBeamsize()
        print(datetime.datetime.now())
        print("Beamsize index from BSS=", beamsize_index)
        config_dir = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooConfig/bss"
        bsc = BeamsizeConfig.BeamsizeConfig(config_dir)
        # bsc.readConfig()
        print(bsc.getBeamsizeAtIndex(beamsize_index))
        zoo.disconnect()
    except:
        print("Beamsize index cannot be got")
