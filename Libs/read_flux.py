import sqlite3, csv, os, sys, numpy
import DBinfo,ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()
    conds = esa.getDict()

    for each_db in conds:
        p=each_db
        if p['isDone'] == 0:
            print "skipping"
            continue
        print p['puckid'], p['pinid'], p['flux']
