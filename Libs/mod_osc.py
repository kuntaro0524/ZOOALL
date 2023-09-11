import sqlite3, csv, os, sys, copy
import MyException
import re

import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()

    #print "BEFORE"
    ppp = esa.getDict()
    for p in ppp:
        oindex = p['o_index']
        isDone = p['isDone']
        if p['mode'] == "multi":
            print(oindex,p['total_osc'],p['pinid'])
            # p['total_osc'],p['osc_width'],p['isDone'],p['hebi_att'],p['isMount']
            #esa.updateValueAt(oindex,"maxhits", 100)
        
    """
    ppp = esa.getDict()
    print "AFTER"
    for p in ppp:
        isDone = p['isDone']
        if isDone == 0:
            oindex = p['o_index']
            print oindex,p['puckid'],p['pinid'],"maxhits=",p['maxhits']
    """
