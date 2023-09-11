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
        print(oindex,isDone)
        if p['isMount'] == 0 and p['isDone'] == 9998:
            esa.updateValueAt(oindex,"isDone", 0)

    ppp = esa.getDict()
    print("AFTER")
    for p in ppp:
        oindex = p['o_index']
        print(oindex, p['puckid'],p['pinid'],"SCORE_MIN=",p['score_min'])
