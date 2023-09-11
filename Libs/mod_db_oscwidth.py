import sqlite3, csv, os, sys, copy
import MyException
import re

import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()

    print("BEFORE")
    ppp = esa.getDict()
    for p in ppp:
        oindex = p['o_index']
        isDone = p['isDone']
        #if isDone == 0:
        print(oindex, p['ds_vbeam'],p['ds_hbeam'],p['osc_width'])
        if p['isMount'] == 0 and p['isDone'] == 0:
            esa.updateValueAt(oindex,"osc_width", 0.25)

    ppp = esa.getDict()
    print("AFTER")
    for p in ppp:
        oindex = p['o_index']
        print(oindex, p['puckid'],p['pinid'],p['osc_width'])
