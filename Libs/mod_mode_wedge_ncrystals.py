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
        print(oindex, p['ds_vbeam'],p['ds_hbeam'],p['isDone'],p['hebi_att'],p['isMount'])
        if p['isMount'] == 0 and p['isDone'] == 0:
            #esa.updateValueAt(oindex,"mode", "'multi'")
            #esa.updateValueAt(oindex,"total_osc", 10.0)
            #esa.updateValueAt(oindex,"maxhits", 100)
            esa.updateValueAt(oindex,"mode", "'helical'")
            esa.updateValueAt(oindex,"total_osc", 360.0)
            esa.updateValueAt(oindex,"maxhits", 5)
            esa.updateValueAt(oindex,"ds_vbeam", 10)
            esa.updateValueAt(oindex,"ds_hbeam", 5)
            esa.updateValueAt(oindex,"raster_vbeam", 10)
            esa.updateValueAt(oindex,"raster_hbeam", 5)

    ppp = esa.getDict()
    print("AFTER")
    for p in ppp:
        print(oindex, p['puckid'],p['pinid'],p['total_osc'],p['maxhits'],p['mode'])
        print(p['raster_vbeam'],p['raster_hbeam'],p['ds_vbeam'],p['ds_hbeam'])
