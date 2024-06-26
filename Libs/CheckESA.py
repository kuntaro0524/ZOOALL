import sqlite3, csv, os, sys, datetime
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")
import ESA
import MyException
import glob

# Analyze 
class CheckESA():
    def __init__(self, cond):
        self.cond = cond
        self.isInit = False

    def read_params(self):
        self.root_dir = self.cond['root_dir']
        self.p_index = self.cond['p_index']
        self.mode = self.cond['mode']
        self.puckid = self.cond['puckid']
        self.pinid = self.cond['pinid']
        self.sample_name = self.cond['sample_name']
        self.wavelength = self.cond['wavelength']
        self.raster_vbeam = self.cond['raster_vbeam']
        self.raster_hbeam = self.cond['raster_hbeam']
        self.att_raster = self.cond['att_raster']
        self.hebi_att = self.cond['hebi_att']
        self.exp_raster = self.cond['exp_raster']
        self.dist_raster = self.cond['dist_raster']
        self.loopsize = self.cond['loopsize']
        self.score_min = self.cond['score_min']
        self.score_max = self.cond['score_max']
        self.maxhits = self.cond['maxhits']
        self.total_osc = self.cond['total_osc']
        self.osc_width = self.cond['osc_width']
        self.ds_vbeam = self.cond['ds_vbeam']
        self.ds_hbeam = self.cond['ds_hbeam']
        self.exp_ds = self.cond['exp_ds']
        self.dist_ds = self.cond['dist_ds']
        self.dose_ds = self.cond['dose_ds']
        self.offset_angle = self.cond['offset_angle']
        self.reduced_fact = self.cond['reduced_fact']
        self.ntimes = self.cond['ntimes']
        self.meas_name = self.cond['meas_name']
        self.cry_min_size_um = self.cond['cry_min_size_um']
        self.cry_max_size_um = self.cond['cry_max_size_um']
        self.hel_full_osc = self.cond['hel_full_osc']
        self.hel_part_osc = self.cond['hel_part_osc']
        self.isSkip = self.cond['isSkip']
        self.isMount = self.cond['isMount']
        self.isLoopCenter = self.cond['isLoopCenter']
        self.isRaster = self.cond['isRaster']
        self.isDS = self.cond['isDS']
        self.scan_height = self.cond['scan_height']
        self.scan_width = self.cond['scan_width']
        self.n_mount = self.cond['n_mount']
        self.nds_multi = self.cond['nds_multi']
        self.nds_helical = self.cond['nds_helical']
        self.nds_helpart = self.cond['nds_helpart']
        self.t_meas_start = self.cond['t_meas_start']
        self.t_mount_end = self.cond['t_mount_end']
        self.t_cent_start = self.cond['t_cent_start']
        self.t_cent_end = self.cond['t_cent_end']
        self.t_raster_start = self.cond['t_raster_start']
        self.t_raster_end = self.cond['t_raster_end']
        self.t_ds_start = self.cond['t_ds_start']
        self.t_ds_end = self.cond['t_ds_end']
        self.t_dismount_start = self.cond['t_dismount_start']
        self.t_dismount_end = self.cond['t_dismount_end']
        self.isInit = True

    def analyzeExperiment(self):
        if self.isInit == False:
            self.read_params()
        self.comment = ""
        self.puckinfo = "%10s-%02d: "%(self.puckid, self.pinid)
        self.comment += self.puckinfo
        # Confusing convertion
        str_start = "%s" % self.t_meas_start

        # Initial flags
        self.isSuccess = False
        self.failedScan = True
        self.isMeasured = True

        if self.isSkip != 0:
            self.comment += "skipped."
            return self.comment
        if self.t_meas_start == "none":
            self.isMeasured = False
            self.comment += "not measured."
            return self.comment
        else:
            strtime = self.str2time(self.t_meas_start)
            self.comment += "started. %-10s:  %15s " % (self.mode, strtime)
        if self.isMount == 0:
            self.comment += "Not mounted / Mount failure."
            return self.comment
        if self.t_mount_end !=0:
            self.comment += "Mounted."
        if self.isLoopCenter != 0:
            self.comment += "Loop centered."
        if self.isRaster != 0:
            self.comment += "raster scanned. "
        if self.isRaster != 0 and self.isDS ==0:
            self.comment += "crystal cannot be found."
            self.failedScan = True
            return self.comment
        if self.isDS != 0:
            self.comment += "data collected."
            self.ds_dir = "%s/%s-%02d" %(self.root_dir, self.puckid, self.pinid)
            #n_frames =
            print "TESTETEST",self.ds_dir
            self.isSuccess = True

        return self.comment

    def countScanDSdires(self, sample_path):
        print "count scan"

    def str2time(self, esa_time):
        if esa_time == None:
            print "No information"
            raise MyException("No information")
        #print "ESA_TIME=",esa_time
        try:
            strt = "%s" % esa_time
            #print "STRTIME",strt
            year = strt[0:4]
            #print year
            month = strt[4:6]
            date = strt[6:8]
            hour = strt[8:10]
            mins = strt[10:12]
            secs = strt[12:14]
            timestr = "%s-%s-%s %s:%s:%s" % (year, month, date, hour, mins, secs)
            #print year, month, date, hour, mins
            ttime=datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')
            #print "RETURN",type(ttime)
            return ttime
        except MyException,tttt:
            print "Something wrong"
            raise MyException(ttt)

    def calcTime(self):
        if self.isInit == False:
            self.init()

        if self.isDS == True:
            try:
                self.t_meas_start = self.str2time(self.cond['t_meas_start'])
                self.t_mount_end = self.str2time(self.cond['t_mount_end'])
                self.t_center_start = self.str2time(self.cond['t_cent_start'])
                self.t_center_end = self.str2time(self.cond['t_cent_end'])
                self.t_raster_start = self.str2time(self.cond['t_raster_start'])
                self.t_raster_end = self.str2time(self.cond['t_raster_end'])
                self.t_ds_start = self.str2time(self.cond['t_ds_start'])
                self.t_ds_end = self.str2time(self.cond['t_ds_end'])
                #t_dismount_start = self.str2time(self.cond['t_dismount_start'])
                #t_dismount_end = self.str2time(self.cond['t_dismount_end'])
        
                if self.isMount:
                    self.t_mount = (self.t_mount_end - self.t_meas_start).seconds
                    print "MOUNT:", self.t_mount
                if self.isCenter:
                    self.t_center = (self.t_center_end - self.t_center_start).seconds
                    print "centering", self.t_center
                if self.isRaster:
                    self.t_raster = (self.t_raster_end - self.t_raster_start).seconds
                    print "Raster", self.t_raster
                if self.isDS:
                    self.t_ds = (self.t_ds_end - self.t_ds_start).seconds
                    print "DS",self.t_ds
                #t_dismount = t_dismount_end - t_dismount_start
            except MyException,tttt:
                print "EEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRR"
                raise MyException(tttt)

if __name__=="__main__":
    esa = ESA.ESA(sys.argv[1])
    # print esa.getTableName()
    # esa.listDB()
    conds_dict = esa.getDict()

    datedata = sys.argv[1].replace("zoo_", "").replace("db", "").replace(".", "").replace("/", "")
    progress_file = "check_%s.dat" % datedata
    ofile = open(progress_file, "w")

    # Check all conditions in ZOO database file
    for cond in conds_dict:
        ce = CheckESA(cond)
        logstr = ce.analyzeExperiment()
        if ce.isMeasured == True and ce.isSkip == 0:
            print logstr
