import sys,math,numpy,os
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
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
    ms.connect(("172.24.242.41", 10101))

    # Read option from a command line
    import optparse, os, sys

    parser = optparse.OptionParser()
    
    parser.add_option("--z1", "--zoofile1", dest="filename1", help="ZOO csv/db File No.1.", metavar="FILE1")
    parser.add_option("--t1", "--time1", dest="timelimit1", type="float",help="data collection time in hours for file1.", metavar="TIME1")
    parser.add_option("--z2", "--zoofile2", dest="filename2", help="ZOO csv/db File No.2.", metavar="FILE2")
    parser.add_option("--t2", "--time2", dest="timelimit2", type="float",help="data collection time in hours for file2.", metavar="TIME2")
    parser.add_option("--z3", "--zoofile3", dest="filename3", help="ZOO csv/db File No.3.", metavar="FILE3")
    parser.add_option("--t3", "--time3", dest="timelimit3", type="float",help="data collection time in hours for file3.", metavar="TIME3")
    parser.add_option("--z4", "--zoofile4", dest="filename4", help="ZOO csv/db File No.4.", metavar="FILE4")
    parser.add_option("--t4", "--time4", dest="timelimit4", type="float",help="data collection time in hours for file4.", metavar="TIME4")
    #parser.add_option("--ff", "--from-file", dest="config_file", help="reads a file list", metavar="FILE")
    
    (options, args) = parser.parse_args()
    
    check_list=[options.filename1, options.filename2, options.filename3, options.filename4]
    time_list=[options.timelimit1, options.timelimit2, options.timelimit3, options.timelimit4]
    
    # Logging setting
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_%s.log" % time_str
    print("changing mode of %s" % logname)
    logging.config.fileConfig('/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')
    os.chmod(logname, 0o666)

    zoo=Zoo.Zoo()
    zoo.connect()

    # Minimum beam size for 10um raster scan
    min_beam_raster10um = 20.0
    total_pins = 0

    # ZOO input file and its time limit.
    for zoofile, timelimit in zip(check_list, time_list):
        if (zoofile is None)==False:
            if (timelimit is None)==False:
                pass
            else:
                print("the time limit is set as 99999 minutes because input value is 'None'")
                timelimit=99999

            logger.info("Start processing %s" % zoofile)
            if zoofile.endswith("csv"):
                navi = ZooNavigator.ZooNavigator(zoo, ms, zoofile, is_renew_db=True)
                #logger.info("10um raster scan version. Threshold=%5.2f um" % 20.0)
                #navi.setMinBeamsize10umRaster(min_beam_raster10um)
                navi.setTimeLimit(timelimit)
                n_pins = navi.goAround()

            elif zoofile.endswith("db"):
                esa_csv = "dummy.csv"
                navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=False)
                #logger.info("10um raster scan version. Threshold=%5.2f um" % 20.0)
                #navi.setMinBeamsize10umRaster(min_beam_raster10um)
                navi.setTimeLimit(timelimit)
                n_pins = navi.goAround(zoofile)

        total_pins += n_pins

    if total_pins == 0:
        logger.info("ZOO did not process any pins")
    else:
        logger.info("Start cleaning after the measurements")
        zoo.dismountCurrentPin()
        zoo.cleaning()

    zoo.disconnect()
    ms.close()
