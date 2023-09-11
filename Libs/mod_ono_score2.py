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
        #print oindex,p['ds_vbeam'],p['ds_hbeam'],p['isDone'],"SCORE_MIN=",p['score_min']
        if p['puckid'] == "CPS2034" and (p['pinid'] >= 2 and p['pinid'] <=16):
            esa.updateValueAt(oindex,"score_min", 10)
        if p['puckid'] == "CPS2035" and (p['pinid'] >= 1 and p['pinid'] <=7):
            esa.updateValueAt(oindex,"score_min", 10)

    ppp = esa.getDict()
    print("AFTER")
    for p in ppp:
        oindex = p['o_index']
        print(oindex, p['puckid'],p['pinid'],"SCORE_MIN=",p['score_min'],p['maxhits'])
