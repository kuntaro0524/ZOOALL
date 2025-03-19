import sqlite3, csv, os, sys, copy
import MyException
import re
import datetime

import ESA

# version 1.0

# This class should treat 'one' information in ZOODB
class DBinfo():
    def __init__(self, dbinfo):
        self.cond = dbinfo
    #print ppp
        self.isRead = False

    def getConds(self):
        return self.conds

    def str2time(self, esa_timestr):
        if esa_timestr == None:
            print("No information")
            raise MyException("No information")
        #print "esa_timestr=",esa_timestr
        try:
            strt = "%s" % esa_timestr
            year = strt[0:4]
            month = strt[4:6]
            date = strt[6:8]
            hour = strt[8:10]
            mins = strt[10:12]
            secs = strt[12:14]
            timestr = "%s-%s-%s %s:%s:%s" % (year, month, date, hour, mins, secs)
            ttime=datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')
            return ttime
        except MyException as tttt:
            message = "Something wrong to read %s" % esa_timestr
            print(message)
            raise MyException(ttt)

    # Extract time information from timestr at the designated index
    def getTimeSeries(self, timestr, newest_index):
        times = timestr.split(",")
        rtn_array = []
        for each_time in times:
            tmpstr = each_time.replace("{","").replace("}","").split(":")
            if len(tmpstr) == 1:
                continue
            else:
                type_str,time_str = tmpstr
                cols = type_str.split("_")
                d_index = int(cols[2])
                record_type = cols[0]
                start_or_end = cols[1]

                if d_index == newest_index:
                    rtn_array.append((record_type, start_or_end, time_str))
                    #print "Data = %5d Type = %10s %10s : %s" % (d_index, record_type, start_or_end, time_str)

        # Estimating consumed time
        # Mount
        for info in rtn_array:
            exp_seq, start_or_end, time_str = info
            if exp_seq == "mount":
                if start_or_end == "start":
                    self.mount_start_time = self.str2time(time_str)
                if start_or_end == "end":
                    self.mount_end_time = self.str2time(time_str)
                    self.mount_time = (self.mount_end_time - self.mount_start_time).seconds
                    #print "Mount: %8d sec" % self.mount_time
            if exp_seq == "center":
                if start_or_end == "start":
                    self.center_start_time = self.str2time(time_str)
                if start_or_end == "end":
                    self.center_end_time = self.str2time(time_str)
                    self.center_time = (self.center_end_time - self.center_start_time).seconds
                    #print "Center: %8d sec" % self.center_time
            if exp_seq == "raster":
                if start_or_end == "start":
                    self.raster_start_time = self.str2time(time_str)
                if start_or_end == "end":
                    self.raster_end_time = self.str2time(time_str)
                    self.raster_time = (self.raster_end_time - self.raster_start_time).seconds
                    #print "raster: %8d sec" % self.raster_time
            if exp_seq == "ds":
                if start_or_end == "start":
                    self.ds_start_time = self.str2time(time_str)
                if start_or_end == "end":
                    self.ds_end_time = self.str2time(time_str)
                    self.ds_time = (self.ds_end_time - self.ds_start_time).seconds
                    #print "ds: %8d sec" % self.ds_time
            if exp_seq == "meas":
                if start_or_end == "start":
                    self.meas_start_time = self.str2time(time_str)
                if start_or_end == "end":
                    self.meas_end_time = self.str2time(time_str)
                    self.meas_time = (self.meas_end_time - self.meas_start_time).seconds
                    #print "meas: %8.2f min" % (self.meas_time/60.0)
        return rtn_array

    def getMeasTime(self, unit="min"):
        return self.meas_time / 60.0

    def prepParams(self):
        self.pindex = self.cond['p_index']
        self.mode = self.cond['mode']
        self.root_dir = self.cond['root_dir']
        self.puck = self.cond['puckid']
        self.pin = self.cond['pinid']
        self.isLoopCenter = self.cond['isLoopCenter']
        self.isDone = self.cond['isDone']
        self.n_mount = self.cond['n_mount']
        self.timestr = self.cond['t_meas_start']
        self.isRaster=self.cond['isRaster']
        self.isMount=self.cond['isMount']
        self.flux = self.cond['flux']
        self.isMount = self.cond['isMount']
        self.isRaster = self.cond['isRaster']
        self.isDS = self.cond['isDS']
        self.getTimeSeries(self.timestr, self.n_mount)
        self.prefix = "%s-%02d"%(self.puck,self.pin)
        self.sample_name = self.cond['sample_name']

        self.isRead = True

    def getStatus(self):
        if self.isRead == False:
            self.prepParams()
        print(self.prefix,self.meas_start_time, self.meas_end_time, self.isMount, self.isLoopCenter, self.isRaster, self.isDS)

        if self.isDS == 1:
            return 1
        else:
            return 0

    def getKAMOinfo(self):
        if self.isRead == False:
            self.prepParams()

        if self.isDS == 1:
            return True,self.root_dir, self.prefix, self.sample_name
        else:
            return False,1,1,1,

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()
    conds = esa.getDict()

    print("Number of crystals processed", len(conds))
    n_good = 0
    dpfile = open("automerge.csv","w")
    dpfile.write("topdir,name,anomalous\n")
    for p in conds:
        dbinfo = DBinfo(p)
        n_good += dbinfo.getStatus()
        flag,rootdir,prefix,sample_name = dbinfo.getKAMOinfo()
        meas_time = dbinfo.getMeasTime()
        print("MEAS=%5.1f min" % meas_time)
        if flag == True:
            dpfile.write("%s/_kamoproc/%s/,%s,no\n" % (rootdir,prefix,sample_name))

    print("Number of crystals processed", len(conds))
    print("Number of datasets " ,n_good)
    print("Failed crystals")
