import sqlite3, csv, os, sys, copy
import re

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")
import MyException

import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])

    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()

    try:
        ppp = esa.getPriorPin()
        o_index = ppp['o_index']
        new_index = o_index + 10000
        esa.updateValueAt(o_index, "p_index", new_index)

    except:
        print("Failed.")
