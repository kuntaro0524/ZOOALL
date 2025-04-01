import sys,math,numpy,os
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
import Zoo
import datetime
import ZooNavigator
from MyException import *
import socket
import MyDate
import logging
import logging.config
import subprocess

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    # Logging setting
    d = MyDate.MyDate()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_%s.log" % time_str
    print "changing mode of %s" % logname
    logging.config.fileConfig('/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')
    os.chmod(logname, 0666)

    zoo=Zoo.Zoo()
    zoo.connect()

    # Threshold
    step_for_special_raster_scan = 25.0
    threshold_beamsize_for_special_raster_scan = 50.0

    total_pins = 0
    for input_file in sys.argv[1:]:
        logger.info("Start processing %s" % input_file)
        if input_file.rfind("csv") != -1:
            navi = ZooNavigator.ZooNavigator(zoo, ms, input_file, is_renew_db=True)
            navi.setRasterStep(step_for_special_raster_scan, threshold_beamsize_for_special_raster_scan)
            logger.info("10um raster scan version. Threshold=%5.2f um" % 20.0)
            n_pins = navi.goAround()

        elif input_file.rfind("db") != -1:
            esa_csv = "dummy.csv"
            navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=False)
            logger.info("10um raster scan version.")
            navi.setRasterStep(step_for_special_raster_scan, threshold_beamsize_for_special_raster_scan)
            logger.info("10um raster scan version. Threshold=%5.2f um" % 20.0)
            n_pins = navi.goAround(input_file)

        total_pins += n_pins

    if total_pins == 0:
        logger.info("ZOO did not process any pins")
    else:
        logger.info("Start cleaning after the measurements")
        zoo.dismountCurrentPin()
        zoo.cleaning()

    zoo.disconnect()
    ms.close()
