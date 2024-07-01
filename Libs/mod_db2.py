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
        if isDone == 0:
            print oindex,p['puckid'],p['pinid'],"dist_ds=",p['dist_ds']
            # p['total_osc'],p['osc_width'],p['isDone'],p['hebi_att'],p['isMount']
            esa.updateValueAt(oindex,"dist_ds", 300.0)
        
        """
        if p['isMount'] == 0 and p['isDone'] == 0:
            #esa.updateValueAt(oindex,"ds_hbeam", 10)
        """

    ppp = esa.getDict()
    print "AFTER"
    for p in ppp:
        isDone = p['isDone']
        if isDone == 0:
            oindex = p['o_index']
            print oindex,p['puckid'],p['pinid'],"dist_ds=",p['dist_ds']

        #if oindex == 31:
            #print oindex,p['puckid'],p['pinid'],p['total_osc'],p['osc_width'],p['isDone'],p['hebi_att'],p['isMount']

        #print oindex, p['puckid'],p['pinid'],p['ds_vbeam'],p['hebi_att']
