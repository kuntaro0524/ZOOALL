import sys,math,numpy,os
from configparser import ConfigParser, ExtendedInterpolation

# Get information from beamline.ini file.
config = ConfigParser(interpolation=ExtendedInterpolation())
config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
config.read(config_path)

zoologdir = config.get("dirs", "zoologdir")
beamline = config.get("beamline", "beamline")
blanc_address = config.get("server", "blanc_address")
logging_conf = config.get("files", "logging_conf")

import Zoo
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
    print("connecting %s" % blanc_address)
    ms.connect((blanc_address, 10101))
    print("Success")

    # Logging setting
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "%s/zoo_%s.log" % (zoologdir, time_str)
    print("changing mode of %s" % logname)
    logging.config.fileConfig(logging_conf, defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')
    os.chmod(logname, 0o666)

    zoo=Zoo.Zoo()
    zoo.connect()

    total_pins = 0
    for input_file in sys.argv[1:]:
        logger.info("Start processing %s" % input_file)
        if input_file.rfind("csv") != -1:
            navi = ZooNavigator.ZooNavigator(zoo, ms, input_file, is_renew_db=True)
            num_pins = navi.goAround()
        elif input_file.rfind("db") != -1:
            esa_csv = "dummy.csv"
            navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=False)
            num_pins = navi.goAround(input_file)
        total_pins += num_pins

    if total_pins == 0:
        logger.info("ZOO did not process any pins")
    else:
        logger.info("Start cleaning after the measurements")
        zoo.dismountCurrentPin()
        zoo.cleaning()

    zoo.disconnect()
    ms.close()
