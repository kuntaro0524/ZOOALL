#!/usr/bin/python
import sys
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")
import Date
import sqlite3,time,numpy
import ESA
import DBinfo, datetime

time_date = Date.Date()

esa = ESA.ESA(sys.argv[1])
conds_dict = esa.getDict()

logline=""
lap_array = []
n_collected = 0
n_mounted = 0
n_meas = 0
n_planned = len(conds_dict)
total_time = 0.0

for each_db in conds_dict:
    isDone = each_db['isDone']
    if isDone == 0:
        continue

    dbinfo = DBinfo.DBinfo(each_db)
    pinstr = dbinfo.getPinStr()
    good_flag = dbinfo.getGoodOrNot()

    if dbinfo.isMount != 0:
        n_mounted += 1

    n_meas += 1
    mode = each_db['mode']
    nds = dbinfo.getNDS()
    constime = dbinfo.getMeasTime()

    if good_flag == True:
        logline += "%s OK. NDS(%8s) = %3d (%4.1f mins)\n" % (pinstr, mode, nds, constime)
    else:
        logline += "%s NG. %s\n" % (pinstr, dbinfo.getErrorMessage())

    total_time += constime

# Mean measure time
if n_meas != 0:
    mean_meas_time = total_time / float(n_meas)
else:
    mean_meas_time = -999.9999

n_remain = n_planned - n_mounted

# Residual time
residual_mins = mean_meas_time * n_remain
residual_time = mean_meas_time * n_remain / 60.0 # hours

logline+="Mean time/pin = %5.1f min.\n" % mean_meas_time
logline+="Planned pins: %3d, Mounted(all): %3d, Remained: %3d\n" % (n_planned, n_mounted, n_remain)
logline+="Expected remained time: %5.2f h  (%8.1f m)\n"%(residual_time, residual_mins)
nowtime = datetime.datetime.now()
exp_finish_time = nowtime + datetime.timedelta(hours = residual_time)
logline+="Expected finishing time: %s\n"%(exp_finish_time)

print(logline)

if n_remain <= 1:
    logline+="Finished\n"
