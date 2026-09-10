import sys,math,numpy,os
from configparser import ConfigParser, ExtendedInterpolation

# Get information from beamline.ini file.
config = ConfigParser(interpolation=ExtendedInterpolation())
config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
print(config_path)
config.read(config_path)

zoologdir = config.get("dirs", "zoologdir")
beamline = config.get("beamline", "beamline")
blanc_address = config.get("server", "blanc_address")
logging_conf = config.get("files", "logging_conf")

import Zoo
import datetime
import ZooNavigator
from ZooMyException import *
import socket
import MyDate
import logging
import logging.config
import subprocess
import BLFactory

import logging.config

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("connecting %s" % blanc_address)
    ms.connect((blanc_address, 10101))
    print("Success")

    # Logging setting
    d = MyDate.MyDate()
    time_str = d.getNowMyFormat(option="date")
    logname = "%s/zoo_%s.log" % (zoologdir, time_str)
    print("changing mode of %s" % logname)

    logging_config = {
    "version": 1,
    "formatters": {
        "f1": {
            "format": "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "f1",
            "stream": "ext://sys.stdout",
        },
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "f1",
            "filename": logname,  # 動的に設定
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["consoleHandler", "fileHandler"],
        }
    },
    }

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger("Zoo")
    logger.info("Start ZOO")

    # Initialize BLFactory
    blf = BLFactory.BLFactory()
    blf.initDevice()

    # BL44XU specific
    if beamline == "BL44XU":
        blf.zoo.setBeamsize(1)

    total_pins = 0
    for input_file in sys.argv[1:]:
        logger.info("Start processing %s" % input_file)
        if input_file.rfind("csv") != -1:
            navi = ZooNavigator.ZooNavigator(blf, input_file, is_renew_db=True)
            # it is possible that a current beamsize is 'undefined' in beamsize.config for ZOO
            # blf.zoo.setBeamsize(1)
            num_pins = navi.goAround()
        elif input_file.rfind("db") != -1:
            esa_csv = "dummy.csv"
            navi=ZooNavigator.ZooNavigator(blf, esa_csv, is_renew_db=False)
            # it is possible that a current beamsize is 'undefined' in beamsize.config for ZOO
            blf.zoo.setBeamsize(1)
            num_pins = navi.goAround(input_file)
        total_pins += num_pins

    if total_pins == 0:
        logger.info("ZOO did not process any pins")
    else:
        logger.info("Start cleaning after the measurements")
        blf.zoo.dismountCurrentPin()
        # zoo.cleaning()

    blf.zoo.disconnect()
    ms.close()
