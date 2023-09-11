import ESA, sys
import Date

if __name__ == "__main__":
    d = Date.Date()

    time_str = d.getNowMyFormat(option="sec")
    dbfile = "zoo_%s.db" % time_str

    esa = ESA.ESA(dbfile)
    esa.makeTable(sys.argv[1],force_to_make=True)
