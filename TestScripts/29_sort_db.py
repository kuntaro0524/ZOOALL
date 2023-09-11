import sqlite3, csv, os, sys, copy
import re

sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")
import MyException

import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])

    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()

    ppp = esa.getSortedDict(order="ASC")
    for p in ppp:
        print("O=%d P=%d SKIP=%d DS=%d %s-%s @%s"%(p['o_index'],p['p_index'], p['isSkip'], p['isDS'],p['puckid'],p['pinid'],p['root_dir']))
