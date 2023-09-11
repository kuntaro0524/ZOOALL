import os,sys,glob
import time
import numpy as np
import socket
import Zoo

if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()
    time.sleep(2.0)
    zoo.cleaning()
    zoo.waitSPACE()
    zoo.disconnect()
