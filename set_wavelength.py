import os,sys,glob
import time
import numpy as np
import socket
import Zoo
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *

if __name__ == "__main__":
    wavelength = float(sys.argv[1])

    if 0.775 <= wavelength <=1.9:
        zoo=Zoo.Zoo()
        zoo.connect()
        zoo.setWavelength(float(sys.argv[1]))
    else:
        print("invalid wavelength")
