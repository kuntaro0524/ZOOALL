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
        puckid = p['puckid']
        print(oindex, puckid)
        if puckid.rfind("-") != -1:
            new_id = "'%s'"%puckid.replace("-","")
            #print new_id
            esa.updateValueAt(oindex, "puckid", new_id)

    new_esa = esa.getDict()
    print("AFTER")
    for p in new_esa:
        oindex = p['o_index']
        print(oindex, p['puckid'],p['pinid'])
