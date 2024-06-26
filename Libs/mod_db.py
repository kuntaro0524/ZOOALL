import sqlite3, csv, os, sys, copy
import MyException
import re

import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()

    print "BEFORE"
    ppp = esa.getDict()
    for p in ppp:
        oindex = p['o_index']
        isDone = p['isDone']
        #if isDone == 0:

        if p['o_index'] == 31:
            #esa.updateValueAt(oindex,"hebi_att", 25)
            print oindex,p['puckid'], p['total_osc'],p['osc_width'],p['isDone'],p['hebi_att'],p['isMount']
            esa.updateValueAt(oindex,"osc_width", 0.1)
        
        """
        if p['isMount'] == 0 and p['isDone'] == 0:
            #esa.updateValueAt(oindex,"ds_hbeam", 10)
        """

    ppp = esa.getDict()
    print "AFTER"
    for p in ppp:
        oindex = p['o_index']
        if oindex == 31:
            print oindex,p['puckid'],p['pinid'],p['total_osc'],p['osc_width'],p['isDone'],p['hebi_att'],p['isMount']

        #print oindex, p['puckid'],p['pinid'],p['ds_vbeam'],p['hebi_att']
