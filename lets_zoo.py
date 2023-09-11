import sys,math,numpy,os
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import LoopMeasurement
import Zoo
import AttFactor
import AnaShika
import Condition
import Hebi
import datetime
import ZooNavigator
from MyException import *
import socket
import Date
import logging
import logging.config
import subprocess

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))

    # Logging setting
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_%s.log" % time_str
    print("changing mode of %s" % logname)
    os.chmod(logname, 0o666)
    logging.config.fileConfig('/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    zoo=Zoo.Zoo()
    zoo.connect()

    esa_db=sys.argv[1]
    esa_csv = "dummy.csv"
    navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=False)
    navi.goAround(esa_db)

    zoo.disconnect()
    ms.close()
