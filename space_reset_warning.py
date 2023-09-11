import os,sys,glob 
import time, datetime
import numpy as np
import socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import logging
import logging.config
import Zoo

# 150722 AM4:00
# Debug: when SPACE has some troubles Zoo stops immediately

bss_srv="192.168.163.2"
bss_port=5555

if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()
    print(zoo.getSampleInformation())
    zoo.skipSample()
    zoo.waitTillReady()
    zoo.disconnect()
