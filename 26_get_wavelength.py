import sys, os
import socket

sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")

import BeamsizeConfig
import Zoo

if __name__ == "__main__":
    config_dir = "/isilon/blconfig/bl45xu/"
 
    zoo = Zoo.Zoo()
    zoo.connect()

    wavelength = zoo.getWavelength()
    print wavelength
    zoo.disconnect()
