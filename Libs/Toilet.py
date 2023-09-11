import sqlite3, csv, os, sys, datetime
import ESA
import MyException

class EachESA():
    def __init__(self, cond):
        self.cond = cond
        self.isInit = False

    def read_params(cond):
        root_dir = cond['root_dir']
        p_index = cond['p_index']
        mode = cond['mode']
        puckid = cond['puckid']
        pinid = cond['pinid']
        sample_name = cond['sample_name']
        wavelength = cond['wavelength']
        raster_vbeam = cond['raster_vbeam']
        raster_hbeam = cond['raster_hbeam']
        att_raster = cond['att_raster']
        hebi_att = cond['hebi_att']
        exp_raster = cond['exp_raster']
        dist_raster = cond['dist_raster']
        loopsize = cond['loopsize']
        score_min = cond['score_min']
        score_max = cond['score_max']
        maxhits = cond['maxhits']
        total_osc = cond['total_osc']
        osc_width = cond['osc_width']
        ds_vbeam = cond['ds_vbeam']
        ds_hbeam = cond['ds_hbeam']
        exp_ds = cond['exp_ds']
        dist_ds = cond['dist_ds']
        dose_ds = cond['dose_ds']
        offset_angle = cond['offset_angle']
        reduced_fact = cond['reduced_fact']
        ntimes = cond['ntimes']
        meas_name = cond['meas_name']
        cry_min_size_um = cond['cry_min_size_um']
        cry_max_size_um = cond['cry_max_size_um']
        hel_full_osc = cond['hel_full_osc']
        hel_part_osc = cond['hel_part_osc']
        isSkip = cond['isSkip']
        isMount = cond['isMount']
        isLoopCenter = cond['isLoopCenter']
        isRaster = cond['isRaster']
        isDS = cond['isDS']
        scan_height = cond['scan_height']
        scan_width = cond['scan_width']
        n_mount = cond['n_mount']
        nds_multi = cond['nds_multi']
        nds_helical = cond['nds_helical']
        nds_helpart = cond['nds_helpart']
        t_meas_start = cond['t_meas_start']
        t_mount_end = cond['t_mount_end']
        t_cent_start = cond['t_cent_start']
        t_cent_end = cond['t_cent_end']
        t_raster_start = cond['t_raster_start']
        t_raster_end = cond['t_raster_end']
        t_ds_start = cond['t_ds_start']
        t_ds_end = cond['t_ds_end']
        t_dismount_start = cond['t_dismount_start']
        t_dismount_end = cond['t_dismount_end']

        print("%10s-%02d"%(puckid,pinid), end=' ')
        #print "MOUNT ENDS " , t_mount_end,
        #print "Measure start= %10d" % t_meas_start,
        #print "isMount=", isMount,
        #print "isRaster=", isRaster,
        #print "isDS=", isDS,
        #print "n_mount=", n_mount,
        #print "nds_multi=", nds_multi,
        #print "nds_helical=", nds_helical,
        # Confusing convertion
        str_start = "%s" % t_meas_start
        #print "str_start =", str_start
        if isSkip != 0:
            print("skipped.")
            return
        if t_meas_start == "none":
            print("Not measured.")
            return
        else:
            print("started. %-10s:  %15s " % (mode, t_meas_start), end=' ')
        if isMount == 0:
            print("Mount failed")
            return
        if t_mount_end !=0:
            print("Mounted. ", end=' ')
        if isLoopCenter != 0:
            print("Loop centered.", end=' ')
        if isRaster != 0:
            print("raster scanned. ", end=' ')
        if isRaster != 0 and isDS ==0:
            print("crystal cannot be found.", end=' ')
        if isDS != 0:
            print("data collected.", end=' ')
        print("")

    def init(self):
        # Flag for mount
        if (self.cond['isMount'] != 0):
            self.isMount = True
        else:
            self.isMount = False
        # Flag for data collection
        if (self.cond['isDS'] != 0):
            self.isDS = True
        else:
            self.isDS = False

        # Flag for raster scan
        if (self.cond['isRaster'] != 0):
            self.isRaster = True
        else:
            self.isRaster = False

        # Flag for raster scan
        if (self.cond['isLoopCenter'] != 0):
            self.isCenter = True
        else:
            self.isCenter = False

    def getPuckPin(self):
        return self.cond['puckid'], self.cond['pinid']

    def getRasterTime(self):
        return self.cond['puckid'], self.cond['pinid']

    def str2time(self, esa_time):
        if esa_time == None:
            print("No information")
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
            print("RETURN",type(ttime))
            return ttime
        except MyException as tttt:
            print("Something wrong")
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
                    print("MOUNT:", self.t_mount)
                if self.isCenter:
                    self.t_center = (self.t_center_end - self.t_center_start).seconds
                    print("centering", self.t_center)
                if self.isRaster:
                    self.t_raster = (self.t_raster_end - self.t_raster_start).seconds
                    print("Raster consumed time:", self.t_raster, "sec")
                if self.isDS:
                    self.t_ds = (self.t_ds_end - self.t_ds_start).seconds
                    print("DS",self.t_ds)
                #t_dismount = t_dismount_end - t_dismount_start
            except MyException as tttt:
                print("EEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRR")
                raise MyException(tttt)

class Toilet():
    def __init__(self, db_file):
        self.db_file = db_file
        self.isInit = False

    def init(self):
        self.esa = ESA.ESA(self.db_file)
        self.conds = self.esa.getDict()
        #datedata=sys.argv[1].replace("zoo_","").replace("db","").replace(".","").replace("/","")
        self.isInit = True

    def listAll(self):
        if self.isInit == False:
            self.init()
        for cond in self.conds:
            unko = EachESA(cond)
            print(unko.getPuckPin())
            try:
                print(unko.calcTime())
            except MyException as tttt:
                raise MyException   
            
            """
            logline=""
            logline+="PUCK:%s"%cond['puckid']
            logline+="-%02d "%cond['pinid']
            logline+="MODE=%8s "%cond['mode']
            logline+="isSkip=%8s "%cond['isSkip']
            logline+="isMount=%8s "%cond['isMount']
            logline+="isDS=%8s "%cond['isDS']
            if mode == "helical":
                nds_helical = cond['nds_helical']
                if nds_helical == "none" or nds_helical == 0:
                    logline+="Not-collected      "
                    isRaster = cond['isRaster']
                    logline+="isRaster = %5d"%isRaster
                    if isRaster == 0:
                        logline+="LOG: Raster scan was not conducted."
                    else:
                        check_com.write("echo Checking %s-%02d\n"%(cond['puckid'],cond['pinid']))
                        check_com.write("display %s/%s-%02d/scan00/2d/_spotfinder/2d_selected_map.png\n"%(cond['root_dir'],cond['puckid'],cond['pinid']))
                        check_com.write("display %s/%s-%02d/before.ppm \n"%(cond['root_dir'],cond['puckid'],cond['pinid']))
                else:
                    logline+="    Collected %5d"%nds_helical
                    #logline+="# of datasets:%s"%nds_helical
    
            if mode == "multi":
                nds_multi = cond['nds_multi']
                logline+="# of datasets:%s"%nds_multi
                
            logline+=" Finished %s"%cond['t_ds_end']
            ofile.write("%s\n"%logline)
            """


               
toilet = Toilet(sys.argv[1]) 
toilet.listAll()
