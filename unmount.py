import os,sys,glob
import time
import numpy as np
import socket
import Zoo
import logging
import logging.config
import Date

if __name__ == "__main__":
    # Logging setting
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/BL41XU/BLsoft/PPPP/10.Zoo/ZooLogs/zootest_%s.log" % time_str
    logging.config.fileConfig('/isilon/BL41XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')
    os.chmod(logname, 0666)   	

    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()
    zoo.dismountCurrentPin()
    zoo.waitTillReady()
    zoo.disconnect()
