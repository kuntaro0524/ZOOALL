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
import argparse

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    zoo=Zoo.Zoo()
    zoo.connect()

    # Logging setting
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/BL45XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_%s.log" % time_str
    print "changing mode of %s" % logname
    logging.config.fileConfig('/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')
    os.chmod(logname, 0666)

    # Argument analysis
    parser = argparse.ArgumentParser(description='This is for running ZOO by feeding zoo.db or zoo.csv')

    parser.add_argument('ZOOIN', help='csv/DB file 1')
    parser.add_argument('--ZOOIN2', '-z2', help='2nd CSV/DB file')
    parser.add_argument('--ZOOIN3', '-z3', help='3rd CSV/DB file')
    parser.add_argument('-t1', '--time1', help='Time for 1st ZOO[hrs]')
    parser.add_argument('-t2', '--time2', help='Time for 2nd ZOO[hrs]')
    parser.add_argument('-t3', '--time3', help='Time for 3rd ZOO[hrs]')

    # Debugging mode
    parser.add_argument('--debug', '-d', action='store_true', help='for debugging')
    parser.add_argument('--no-clean', '-nc', action='store_true', help='for debugging')

    args = parser.parse_args()

    # List of file and planned time for data collection
    file_and_time = []


    # Check if the file suffix is '.db' or '.csv'
    def check_suffix(zoo_file):
        if zoo_file.rfind(".csv") != -1:
            return "CSV"
        elif zoo_file.rfind(".db") != -1:
            return "DB"
        else:
            print "Please input "

    # Set 1
    if args.time1 is None:
        dc_time1 = 99999
    else:
        dc_time1 = args.time1

    file_and_time.append((args.ZOOIN, dc_time1))

    # Set 2
    isSecond = False
    if args.ZOOIN2 is not None:
        isSecond = True
        if isSecond:
            if args.time2 is None:
                dc_time2 = 99999
            else:
                dc_time2 = args.time2
    else:
        pass

    # if the second file is added
    if isSecond:
        file_and_time.append((args.ZOOIN2, dc_time2))

    total_pins = 0
    n_pins = 0
    # Processing input files
    for zoofile, time_for_dc in file_and_time:
        logger.info("Start processing %s" % zoofile)
        # input file is CSV
        if check_suffix(zoofile) == "CSV":
            navi = ZooNavigator.ZooNavigator(zoo, ms, zoofile, is_renew_db=True)
        # input file is DB file
        elif check_suffix(zoofile) == "DB":
            esa_csv = "dummy.csv"
            navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=False)
        # data collection by ZOO
        n_pins = navi.goAround(zoofile)
        total_pins += n_pins

    if total_pins == 0:
        logger.info("ZOO did not process any pins")
    elif args.nc != True:
        logger.info("Start cleaning after the measurements")
        zoo.dismountCurrentPin()
        zoo.cleaning()

    zoo.disconnect()
    ms.close()
