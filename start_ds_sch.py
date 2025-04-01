import os,sys,glob
import time
import numpy as np
import socket
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

import Zoo

if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()

    zoo.getSampleInformation()
    zoo.doDataCollection(sys.argv[1])
    zoo.disconnect()
