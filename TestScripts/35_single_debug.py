import sys, os, math, cv2, socket, time, copy
import traceback
import logging
import numpy as np

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")

import ESA
import LoopMeasurement
import Zoo
import ZooNavigator
import HEBI
import logging, logging.config
import Date

# Use this script after 2D scan of the crystal
# Prepare CSV file for ESA setting

if __name__ == "__main__":
    esa = ESA.ESA("zoo.db")
    esa.makeTable(sys.argv[1], force_to_make=True)
    cond = esa.getDict()[0]

    # kuntaro_log
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_%s.log" % time_str
    logging.config.fileConfig('/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))
    zoo=Zoo.Zoo()
    zoo.connect()

    log = open("single.log", "w")
    stopwatch = "sw"
    root_dir = cond['root_dir']
    prefix = "helitest"

    #def __init__(self, zoo, loop_measurement, logfile, stopwatch, phosec):

    lm = LoopMeasurement.LoopMeasurement(ms, root_dir, prefix)

    zn = ZooNavigator.ZooNavigator(zoo, ms, sys.argv[1], is_renew_db=False)
    zn.prepESA()
    zn.lm = lm
    zn.rheight = 300
    zn.rwidth = 400
    zn.center_xyz = 1.4193, -10.6132, -0.9929
    zn.lm.raster_dir = "%s/test02" % root_dir
    zn.collectSingle(cond['puckid'], cond['pinid'], prefix, cond, 270.0)
