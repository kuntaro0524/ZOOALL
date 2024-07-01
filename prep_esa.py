import sys,os,path
import ESA

print "Preparation of ZOO database file."
# Root directory from CSV file
root_dir = os
if os.path.exists(root_dir) == False:
    os.makedirs(root_dir)
# zoo.db file check and remake and save
d = Date.Date()
time_str = d.getNowMyFormat(option="sec")
dbfile = "%s/zoo_%s.db" % (root_dir, time_str)
esa = ESA.ESA(dbfile)
esa.makeTable(esa_csv, force_to_make=is_renew_db)
