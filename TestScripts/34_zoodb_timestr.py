import sqlite3, csv, os, sys, copy, datetime
import re

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")
import MyException

import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])

    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()
    #def addTimeStrAt(self, o_index, param_name, value):

    #esa.updateValueAt(12, 't_meas_start', "190633")
    #esa.updateValueAt(12, 't_mount_end', "190633")

    try:
        ppp = esa.getPriorPinCond()
        o_index = ppp['o_index']
        event_name = "mount_start"
        esa.addEventTimeAt(o_index, event_name)
        event_name = "mount_end"
        esa.addEventTimeAt(o_index, event_name)

        ppp = esa.getPriorPinCond()

    except:
        print("Failed.")
