import sqlite3, csv, os, sys, copy
import MyException
import re
import datetime

import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])

    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()

    ppp = esa.getDict()
    #print ppp

    def str2time(esa_time):
        if esa_time == None:
            print("No information")
            raise MyException("No information")
        #print "ESA_TIME=",esa_time
        try:
            strt = "%s" % esa_time
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
            print("Something wrong")
            raise MyException(ttt)

    def getTimeSeries(timestr, newest_index):
        print("##################")
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
                    mount_start_time = str2time(time_str)
                if start_or_end == "end":
                    mount_end_time = str2time(time_str)
                    mount_time = (mount_end_time - mount_start_time).seconds
                    print("Mount: %8d sec" % mount_time)
            if exp_seq == "center":
                if start_or_end == "start":
                    center_start_time = str2time(time_str)
                if start_or_end == "end":
                    center_end_time = str2time(time_str)
                    center_time = (center_end_time - center_start_time).seconds
                    print("Center: %8d sec" % center_time)
            if exp_seq == "raster":
                if start_or_end == "start":
                    center_start_time = str2time(time_str)
                if start_or_end == "end":
                    center_end_time = str2time(time_str)
                    center_time = (center_end_time - center_start_time).seconds
                    print("raster: %8d sec" % center_time)
            if exp_seq == "ds":
                if start_or_end == "start":
                    ds_start_time = str2time(time_str)
                if start_or_end == "end":
                    ds_end_time = str2time(time_str)
                    ds_time = (ds_end_time - ds_start_time).seconds
                    print("ds: %8d sec" % ds_time)
            if exp_seq == "meas":
                if start_or_end == "start":
                    meas_start_time = str2time(time_str)
                if start_or_end == "end":
                    meas_end_time = str2time(time_str)
                    meas_time = (meas_end_time - meas_start_time).seconds
                    print("meas: %8.2f min" % (meas_time/60.0))
        return rtn_array

    for p in ppp:
        pindex = p['p_index']
        mode = p['mode']
        root_dir = p['root_dir']
        puck = p['puckid']
        pin = p['pinid']
        isCenter = p['isLoopCenter']
        isDone = p['isDone']
        n_mount = p['n_mount']
        timestr = p['t_meas_start']
        isRaster=p['isRaster'] 
        isMount=p['isMount'] 
        flux = p['flux']
        roi_raster = p['raster_roi']

        # Complete done
        if isDone == 1:
            newest_index = n_mount
            print(getTimeSeries(timestr, newest_index))
        #print pindex,mode,root_dir,puck,pin,p['cry_max_size_um'],p['cry_min_size_um'],timestr, n_mount, "isCenter=",isCenter, "isDone=", isDone, "isRaster=",isRaster,"FLUX=%e"%flux
            print(pindex,mode,root_dir,puck,pin, "n_mount=",n_mount, "isCenter=",isCenter, "isDone=", isDone, "isRaster=",isRaster,"FLUX=%e"%flux)

    for p in ppp:
        pindex = p['p_index']
        mode = p['mode']
        root_dir = p['root_dir']
        puck = p['puckid']
        pin = p['pinid']
        isCenter = p['isLoopCenter']
        isDone = p['isDone']
        n_mount = p['n_mount']
        timestr = p['t_meas_start']
        isRaster=p['isRaster'] 
        isMount=p['isMount'] 
        flux = p['flux']
        roi_raster = p['raster_roi']
        if isDone != 1:
            print("%s-%02d failed. isDone:%5d: isMount %5d %5d" % (puck,pin,isDone,isMount,roi_raster))
        #print "isCenter",isCenter
        #getTimeSeries(timestr)
