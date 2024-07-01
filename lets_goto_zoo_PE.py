import sys,math,numpy,os
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
import Zoo
import datetime
import ZooNavigator
from MyException import *
import socket
import Date
import logging
import logging.config
import subprocess
import PuckExchanger

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    # isDebug
    isSkipNoPins = False

    # Logging setting
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_%s.log" % time_str
    print "changing mode of %s" % logname
    logging.config.fileConfig('/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')
    os.chmod(logname, 0666)

    zoo=Zoo.Zoo()
    zoo.connect()

    # Puck exchanger preparation
    pe = PuckExchanger.PuckExchanger(zoo)

    total_pins = 0
    # Currently only CSV files
    for input_file in sys.argv[1:]:
        logger.info("Start processing %s" % input_file)
        if input_file.rfind("csv") != -1:
            # pe.mountAllonCSV(input_file)
            pe.checkCurrentPucksAndMount(input_file)
            navi = ZooNavigator.ZooNavigator(zoo, ms, input_file, is_renew_db=True)
            n_pins = navi.goAround()
        elif input_file.rfind("db") != -1:
            print("Currently, DB restart function is not available. Wait for the next release!")
            sys.exit()
            # esa_csv = "dummy.csv"
            # navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=False)
            # n_pins = navi.goAround(input_file)
        total_pins += n_pins
        # The final pin should be unmounted before changing CSV file.
        zoo.dismountCurrentPin()
        # SPACE cleaning after 1 CSV file
        zoo.cleaning()

    if total_pins == 0 and isSkipNoPins:
        logger.info("ZOO did not process any pins")
    else:
        logger.info("Start cleaning after the measurements")
        # Dismount the last pin on the goniometer
        zoo.dismountCurrentPin()
        # Dismount all pucks in SPACE
        pe.unmountAllpucksFromSPACE()
        # SPACE cleaning
        zoo.cleaning()

    zoo.disconnect()
    ms.close()
