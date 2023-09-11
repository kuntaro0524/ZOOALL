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
        vbeam_raster = p['raster_vbeam']
        hbeam_raster = p['raster_hbeam']
        print("%8.2f %8.2f " % (vbeam_raster, hbeam_raster))
        if isDone == 0 and vbeam_raster == 5.0 and hbeam_raster == 5.0:
            print("Updating", p['puckid'],p['pinid'])
            esa.updateValueAt(oindex,"att_raster", 100.0)

    ppp = esa.getDict()
    print("AFTER")
    for p in ppp:
        oindex = p['o_index']
        print(oindex, p['raster_vbeam'],p['raster_hbeam'],p['puckid'],p['pinid'],"att_raster=",p['att_raster'])
