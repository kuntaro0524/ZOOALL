import sys, os, math, cv2, socket, time, copy
import traceback
import logging
import numpy as np

sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/")

import ESA
import LoopMeasurement
import Zoo
import HEBI

# Use this script after 2D scan of the crystal
# Prepare CSV file for ESA setting

if __name__ == "__main__":
    esa = ESA.ESA("zoo.db")
    esa.makeTable(sys.argv[1], force_to_make=True)
    cond = esa.getDict()[0]

    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))
    zoo=Zoo.Zoo()
    zoo.connect()

    log = open("hebi_test.log", "w")
    stopwatch = "sw"
    root_dir = cond['root_dir']
    prefix = "helitest"

    #def __init__(self, zoo, loop_measurement, logfile, stopwatch, phosec):

    lm = LoopMeasurement.LoopMeasurement(ms, root_dir, prefix)
    h2 = HEBI.HEBI(zoo, lm, log, stopwatch, 1E13)

    lm.prepDataCollection(99)
    raspath = "/isilon/users/tueno/tueno/JUNK/HSK0005-11/scan04/2d/"
    scan_id = "2d"
    n_crystals = h2.mainLoop(raspath, scan_id, 225.0, cond, precise_face_scan=False)
