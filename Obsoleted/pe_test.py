import os,sys,glob
import time, datetime
import numpy as np
import socket
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import *
import logging
import logging.config
import Zoo
import PuckExchanger

if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()

    pe=PuckExchanger.PuckExchanger(zoo)
    # print zoo.getSampleInformation()
    #zoo.exposeLN2()
    # zoo.runScriptOnBSS("BLTune")
    # zoo.pe_get_puck(1)

    # Puck mount
    # zoo.pe_mount_puck("a01")
    # zoo.isBusy()

    # zoo.pe_get_puck(2)
    # zoo.pe_mount_puck("a02")

    # zoo.pe_mount_puck("a03")

    # zoo.pe_unmount_puck("a03")
    # zoo.pe_query()

    # zoo.pe_exchange_pucks("a01", "a03")

    # zoo.pe_unmount_puck("a02")
    # zoo.pe_unmount_puck("a03")

    # Puck exchanger: gets all pucks in PE
    # puck_list=pe.getAllPuckInfoPE()
    # print(puck_list)
    # print(pe.isPuckIn("a01"))

    # Unmount all pucks
    # pe.unmounteAllpucksFromSPACE()

    # Mount all pucks defined in CSV files
    # pe.mountAllonCSV(sys.argv[1])

    # Unmount all pucks
    pe.unmounteAllpucksFromSPACE()

    # Read CSV file
    zoo.disconnect()
