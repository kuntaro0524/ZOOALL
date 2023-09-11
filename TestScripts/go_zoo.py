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
import logging, logging.config
import argparse

if __name__ == "__main__":

    # Parse option on a command line
    parser = argparse.ArgumentParser(description='getget')
    # Primory csv file
    parser.add_argument('--csv',help='1st CSV file')
    parser.add_argument('--csv2', help='2nd CSV file')
    parser.add_argument('--csv3', help='3rd CSV file')
    parser.add_argument('--dbfile', help='definition of the database file')
    parser.add_argument('--dbfile2', help='definition of the database file')
    parser.add_argument('--dbfile3', help='definition of the database file')
    
    args = parser.parse_args()
    
    csvlist = []
    
    if args.csv != None:
        csv_name = args.csv
        csvlist.append(csv_name)
    
    if args.csv2 != None:
        csv2_name = args.csv2
        csvlist.append(csv2_name)
    
    if args.csv3 != None:
        csv3_name = args.csv3
        csvlist.append(csv3_name)
    
    if args.csv3 != None:
        csv3_name = args.csv3
        csvlist.append(csv3_name)

    db_list = []
    if args.dbfile != None:
        dbname = args.dbfile
        db_list.append(dbname)

    if args.dbfile2 != None:
        dbname = args.dbfile2
        db_list.append(dbname)

    if args.dbfile3 != None:
        dbname = args.dbfile3
        db_list.append(dbname)
    
    # ZOO setting
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.41", 10101))

    # kuntaro_log
    d = Date.Date()
    time_str = d.getNowMyFormat(option="date")
    logname = "/isilon/BL32XU/BLsoft/PPPP/10.Zoo/ZooLogs/zoo_%s.log" % time_str
    logging.config.fileConfig('/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/logging.conf', defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    zoo=Zoo.Zoo()
    zoo.connect()

    # CSV files: sequential processing
    for esa_csv in csvlist:
        navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=True)
        navi.goAround()

    for dbname in db_list:
        dbname = args.dbfile
        esa_csv = "dummy.csv"
        navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=False)
        navi.goAround()

    zoo.disconnect()
    ms.close()
