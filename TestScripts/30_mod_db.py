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

    ppp = esa.getDict()
    for p in ppp:
        o_index = p['o_index']
        if o_index == int(sys.argv[2]):
            print(p['o_index'], p['p_index'],p['puckid'],p['pinid'])
            esa.updateValueAt(o_index,"p_index", 1)
