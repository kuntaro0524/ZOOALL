import sqlite3, csv, os, sys, copy
import MyException
import re

import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()

    ppp = esa.getDict()
    for p in ppp:
        oindex = p['o_index']
        isDone = p['isDone']
        puckid = p['puckid']
        print oindex,p['puckid']
        
        if isDone == 0 and puckid == "15":
            esa.updateValueAt(oindex,"puckid", "'015'")
        if isDone == 0 and puckid == "20":
            esa.updateValueAt(oindex,"puckid", "'020'")
        
    ppp = esa.getDict()
    print "AFTER"
    for p in ppp:
        isDone = p['isDone']
        if isDone == 0:
            print oindex,p['puckid']
