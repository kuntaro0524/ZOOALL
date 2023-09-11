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

    try:
        ppp = esa.getPriorPinCond()
        o_index = ppp['o_index']
        #esa.updateValueAt(o_index, 't_mount_end', "190633")
        esa.addTimeStrAt(o_index, 't_mount_end', "%s" % datetime.datetime.now())
    except:
        print("Failed.")
