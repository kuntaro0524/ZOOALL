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
        pindex = p['p_index']
        print(p['p_index'], p['isSkip'])
        esa.updateValueAt(pindex,"isSkip", 1)

    ppp = esa.getDict()
    print("AFTER")
    for p in ppp:
        print(p['p_index'], p['isSkip'])
