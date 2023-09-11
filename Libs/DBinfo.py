import sqlite3, csv, os, sys, copy
import MyException
import re
import datetime

import ESA

# version 1.0.0 completed on 2019/11/03 by K. Hirata

# This class should treat 'one' information in ZOODB
class DBinfo():
    def __init__(self, dbinfo):
        self.cond = dbinfo
        self.isRead = False
        self.isGood = False
        self.isWarn = False
        self.isError = False
        self.isComplete = False
        self.isJudged = False

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
        # Initial values are set to -999.999
        self.mount_time = -60.0
        self.center_time = -60.0
        self.raster_time = -60.0
        self.ds_time = -60.0
        self.meas_time = -60.0

        if timestr == 0:
            #print "this pin was not treated."
            return []

        else:
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

        # DEBUG
        #print "TIMESTR=", timestr

        # Estimating consumed time
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
                    #print "self.meas_time", self.meas_time

        #print "RETURN_ARRAY=", rtn_array
        return rtn_array

    def getRasterConditions(self):
        # Grids for 2D raster scan
        height, width = self.getScanSquare()

        nv_raster = int(height / self.raster_vbeam)
        nh_raster = int(width / self.raster_hbeam)

        info = height, width, nv_raster, nh_raster, self.raster_vbeam, self.raster_hbeam, self.att_raster, self.exp_raster

        return info

    def getMeasTime(self, unit="min"):
        return self.meas_time / 60.0

    def getMountTime(self, unit="min"):
        if unit == "sec":
            return self.mount_time
        elif unit == "min":
            return self.mount_time / 60.0

    def getRasterTime(self, unit="min"):
        if unit == "sec":
            return self.raster_time
        elif unit == "min":
            return self.raster_time / 60.0

    def getDStime(self, unit="min"):
        if unit == "sec":
            return self.ds_time
        elif unit == "min":
            return self.ds_time / 60.0

    def getCenterTime(self, unit="min"):
        if unit == "sec":
            return self.center_time
        elif unit == "min":
            return self.center_time / 60.0

    def getWavelength(self):
            return self.wavelength

    def prepParams(self):
        self.pindex = self.cond['p_index']
        self.oindex = self.cond['o_index']

        self.mode = self.cond['mode']
        self.root_dir = self.cond['root_dir']
        self.puck = self.cond['puckid']
        self.pin = self.cond['pinid']
        self.puck_pin = "%s-%02d" % (self.puck, self.pin)
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
        self.hel_cry_size = self.cond['hel_cry_size']
        #print self.puck, self.pin, self.n_mount
        self.getTimeSeries(self.timestr, self.n_mount)
        self.prefix = "%s-%02d"%(self.puck,self.pin)
        self.sample_name = self.cond['sample_name']
        self.nds_helical = self.cond['nds_helical']
        self.nds_multi = self.cond['nds_multi']
        self.scan_height = self.cond['scan_height']
        self.scan_width = self.cond['scan_width']
        self.data_index = self.cond['data_index']
        self.raster_vbeam = self.cond['raster_vbeam']
        self.raster_hbeam = self.cond['raster_hbeam']
        self.exp_ds = self.cond['exp_ds']
        self.exp_raster = self.cond['exp_raster']
        self.exp_ds = self.cond['exp_ds']
        self.ds_vbeam = self.cond['ds_vbeam']
        self.ds_hbeam = self.cond['ds_hbeam']
        self.att_raster = self.cond['att_raster']
        self.wavelength = self.cond['wavelength']
        self.total_osc = self.cond['total_osc']
        self.osc_width = self.cond['osc_width']
        self.dose_ds = self.cond['dose_ds']
        self.reduced_fact = self.cond['reduced_fact']
        self.ntimes = self.cond['ntimes']

        #print "ISDONE=",selEAf.isDone

        self.isRead = True

    def store2dict(self):
        if self.isRead == False: self.prepParams()

        conds_dict = {}
        for key, value in zip(list(self.__dict__.keys()), list(self.__dict__.values())):
            if key == "conds_dict":
                continue
            conds_dict[key] = value

        return conds_dict

    def getIsDone(self):
        if self.isRead == False:
            self.prepParams()
        return self.isDone

    def getErrorMessage(self):
        message = "None"
        #print "isDone == ", self.isDone
        if self.isDone == 0:
            message = "Not processed yet."
        elif self.isDone == 9999:
            message = "SPACE accident."
        elif self.isDone == 5001:
            message = "SPACE Warning."
        elif self.isDone == 9998:
            message = "SPACE unknown error."
        elif self.isDone == 5002:
            message = "Centering failed."
        elif self.isDone == 4001:
            message = "Multi-small wedge: 0 crystals"
        elif self.isDone == 4002:
            message = "Single: 0 crystals."
        elif self.isDone == 4003:
            message = "Helical: failed"
        elif self.isDone == 4004:
            message = "Helical: (Exception in diffraction centering)"
        elif self.isDone == 4005:
            message = "Single: failed to find crystal in 2D scan"
        elif self.isDone == 4006:
            message = "Single: failed to find crystal in vertical scan"
        else:
            message = "Unknown error: isDone = %d" % self.isDone

        return message

    def getScanSquare(self):
        if self.isRead == False:
            self.prepParams()
        return self.scan_height, self.scan_width

    def getMeasStartTime(self):
        if self.isRead == False:
            self.prepParams()
        return self.meas_start_time

    def getNDS(self):
        if self.isRead == False:
            self.prepParams()
            #print "NDENDS"
            #print self.mode
        if self.mode == "helical":
            #print "HELICAL=", self.nds_helical
            return self.nds_helical
        if self.mode == "multi":
            #print "SINGLE=", self.nds_multi
            return self.nds_multi
        if self.mode == "single":
            return self.isDS
        else:
            print("EEEEEEEEEEEEEEEEEEEEEEE")

    def getPrefix(self):
        if self.isRead == False:
            self.prepParams()
        return self.prefix

    def getLoopDir(self):
        if self.isRead == False:
            self.prepParams()
        loop_dir = "%s/%s/" % (self.root_dir, self.prefix)
        return loop_dir

    def getMode(self):
        if self.isRead == False:
            self.prepParams()
        return self.mode

    def getStatus(self):
        if self.isRead == False:
            self.prepParams()
        #print self.prefix,self.meas_start_time, self.meas_end_time, self.isMount, self.isLoopCenter, self.isRaster, self.isDS

        if self.isDS == 1:
            return 1
        else:
            return 0

    def getSHIKAdir(self):
        if self.isRead == False:
            self.prepParams()
        loopdir = self.getLoopDir()
        d_index = self.n_mount
        shikapath = "%s/scan%02d/2d/_spotfinder/" % (loopdir, d_index)
        return shikapath

    def getOindex(self):
        if self.isRead == False:
            self.prepParams()
        return int(self.oindex)

    def getPinInfo(self):
        if self.isRead == False:
            self.prepParams()

        #print type(self.pin)

        return self.puck, self.pin

    def getPinStr(self):
        if self.isRead == False:
            self.prepParams()
        return self.puck_pin

    def getKAMOinfo(self):
        if self.isRead == False:
            self.prepParams()

        if self.isDS == 1:
            return True,self.root_dir, self.prefix, self.sample_name
        else:
            return False,1,1,1,

    def getGoodOrNot(self):
        if self.isRead == False:
            self.prepParams()
        # Log strings (default)
        log_mount = "Not mounted."
        log_error = "Unidentified errors."
        #log_finish = "Not finished."
        log_collect = "Not collected."
        # comment for LOG HTML
        self.log_comment = "Normal termination"
        # isMounted?
        if self.isMount != 0:
            log_mount = "Mounted"
            if self.isMount > 1:
                log_mount+= "%5d times mounted." % self.isMount
        if self.isDone == 0:
            log_error = "Not finished."
        elif self.isDone != 0:
            if self.isDone == 4001:
                log_error = "No crystals found in a raster scan."
                self.isWarn = True
            elif self.isDone == 4002:
                log_error = "No crystals found in a raster scan."
                self.isWarn = True
            elif self.isDone == 4003:
                log_error = "No crystals found in a raster scan."
                self.isWarn = True
            elif self.isDone == 4004:
                log_error = "X-ray centering failed."
                self.isWarn = True
            elif self.isDone == 4005:
                log_error = "Crystals were not found in a raster scan."
                self.isWarn = True
            elif self.isDone == 4006:
                log_error = "X-ray centering failed."
                self.isWarn = True
            elif self.isDone == 5002:
                log_error = "Loop centering failed(INOCC)."
                self.isError = True
            else:
                log_error = "Normal termination"
                #print "%d" % self.isDone
                self.isGood = True

        if log_error == "Unidentified errors.":
            print("EEEEEEEEEEEEEEEEEEEEEEEEEE",self.isDone)

        self.isJudged = True
        self.log_comment = log_error

        if self.isDS != 0:
            log_collect = "Collected"

        # The first raster scan only
        if self.isWarn == True or self.isDS == 0:
            self.isComplete = False
        else:
            self.isComplete = True

        #print log_mount, log_error, log_collect, self.isComplete, self.isRaster

        return self.isComplete

    def getLogComment(self):
        if self.isJudged == False:
            self.getGoodOrNot()

        return self.log_comment

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()
    conds = esa.getDict()

    for each_db in conds:
        isDone = each_db['isDone']

        if isDone == 0:
            continue
        dbinfo = DBinfo(each_db)
        pinstr=dbinfo.getPinStr()
        good_flag = dbinfo.getGoodOrNot()

        constime = dbinfo.getMeasTime()

        if good_flag == True:
            mode = each_db['mode']
            nds = dbinfo.getNDS()
            #print "%s GOOD. NDS(%8s) = %3d (%4.1f mins)" %(pinstr, mode, nds, constime)
        else:
            print("%s ERROR=%s"%(pinstr,dbinfo.getErrorMessage()))
        #dbinfo.getGoodOrNot()
        #dbinfo.getKAMOinfo()

        #self.timestr = self.cond['t_meas_start']
        dbinfo.getGoodOrNot()
        meas_time = dbinfo.getMeasTime()
        #print "MEAS=%5.1f min" % meas_time
        if flag == True:
            dpfile.write("%s/_kamoproc/%s/,%s,no\n" % (rootdir,prefix,sample_name))
        wavelength = dbinfo.getWavelength()
        print(p['puckid'], p['pinid'], "WAVEL=", wavelength)

    print("Number of crystals processed", len(conds))
    print("Number of datasets " ,n_good)
    print("Failed crystals")
