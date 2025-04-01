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
        isDone = p['att_raster']
        mode = p['mode']
        print mode

        if p['isMount'] == 0 and p['isDone'] == 0 and mode=="multi":
            esa.updateValueAt(oindex,"raster_vbeam", 10)
            esa.updateValueAt(oindex,"raster_hbeam", 10)
            esa.updateValueAt(oindex,"ds_vbeam", 10)
            esa.updateValueAt(oindex,"ds_hbeam", 10)
            esa.updateValueAt(oindex,"att_raster", 10)

    ppp = esa.getDict()
    print "AFTER"
    for p in ppp:
        oindex = p['o_index']
        mode = p['mode']
        if p['isMount'] == 0 and p['isDone'] == 0 and mode=="multi":
            print oindex, p['puckid'],p['pinid'],p['raster_vbeam'],p['raster_hbeam'],p['ds_vbeam'],p['ds_hbeam'],p['att_raster']
