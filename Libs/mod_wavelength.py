import sqlite3, csv, os, sys, copy
import MyException
import re
import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()

    # input puck & pin IDs
    puck_in = sys.argv[2]
    pin_in = int(sys.argv[3])
    wave_in = float(sys.argv[4])

    print("BEFORE")
    ppp = esa.getDict()
    for p in ppp:
        oindex = p['o_index']
        isDone = p['isDone']
        if isDone == 0:
            puckid = p['puckid']
            pinid = p['pinid']
            "wavelength=",p['wavelength']
            if puckid == puck_in and pinid == pin_in:
                print(oindex,p['puckid'],p['pinid'],"wavelength=",p['wavelength'])
                print("Changing wavelength = %8.5f A"% float(wave_in))
                esa.updateValueAt(oindex,"wavelength", float(wave_in))
        
    ppp = esa.getDict()
    print("AFTER")
    for p in ppp:
        isDone = p['isDone']
        if isDone == 0:
            oindex = p['o_index']
            print(oindex,p['puckid'],p['pinid'],"wavelength=",p['wavelength'])
