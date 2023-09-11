import sys, os
import socket

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")

import BeamsizeConfig
import Zoo

if __name__ == "__main__":
    config_dir = "/isilon/blconfig/bl32xu/"
 
    zoo = Zoo.Zoo()
    zoo.connect()

    wavelength = float(sys.argv[1])
    if wavelength > 1.5 or wavelength < 0.8:
        print("wavelength 1.5 - 0.8A")
        sys.exit()

    zoo.setWavelength(wavelength)
    zoo.disconnect()
