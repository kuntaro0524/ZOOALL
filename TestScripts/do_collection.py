import os,sys,glob
import time
import numpy as np
import socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import Zoo

if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()

    # data collection using the defined schedule file
    zoo.doDataCollection(sys.argv[1])
    zoo.waitTillReady()
    zoo.disconnect()
