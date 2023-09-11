import sys
import pandas as pd
import numpy as np
import ESA
import logging, MyException, datetime

class ZooPandas():
    def __init__(self, zoodb):
        self.zoodb = zoodb
        esa = ESA.ESA(self.zoodb)
        self.zoodicts = esa.getDict()
        self.isPrep = False

        # Logging
        FORMAT = '%(asctime)-15s %(module)s %(levelname)-8s %(lineno)s %(message)s'

        logging.basicConfig(filename="./zoo_pandas.log", level=logging.DEBUG, format=FORMAT)
        self.logger = logging.getLogger('ZooPandas')
        self.isDebug = False

    def init(self):
        self.dict_all = {}
        self.pandadf = pd.DataFrame(self.zoodicts)

        self.logger.info("DataFrame:columns=%5d"%len(self.pandadf.columns))
        self.logger.info("DataFrame:index=%5d"%len(self.pandadf.index))
        self.logger.info(self.pandadf)

        # Remove time stamp columns
        self.pandadf = self.pandadf.drop("t_cent_end", axis=1)
        self.pandadf = self.pandadf.drop("t_mount_end", axis=1)
        self.pandadf = self.pandadf.drop("t_raster_start", axis=1)
        self.pandadf = self.pandadf.drop("t_raster_end", axis=1)
        self.pandadf = self.pandadf.drop("t_ds_start", axis=1)
        self.pandadf = self.pandadf.drop("t_ds_end", axis=1)

        # Remove 'non-completed' measurements
        self.logger.info("Before drop:columns=%5d"%len(self.pandadf.columns))
        self.logger.info("Before drop:index=%5d"%len(self.pandadf.index))
        selection = (self.pandadf['isDone']!=0)
        #print(selection)
        self.pandadf=(self.pandadf[selection])
        self.logger.info("After drop:columns=%5d"%len(self.pandadf.columns))
        self.logger.info("After drop:index=%5d"%len(self.pandadf.index))
        self.logger.info(self.pandadf)

        self.isPrep = True

    def calcTime(self):
        criteria1 = self.pandadf.isDS > 0
        criteria2 = self.pandadf.nds_multi > 1
        final_criteria = criteria1 & criteria2
        selected_items = self.pandadf[final_criteria]
        self.logger.info("Selected items=%5d"%len(selected_items))
        self.logger.info(self.pandadf[final_criteria])

    # Extract time information from timestr at the designated index
    # This is copied from DBinfo.py 2020/09/03 K.Hirata
    # It is not so good but I'd like to evaluate the usability/capability of Pandas for ZOODB.
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
    # This is copied from DBinfo.py 2020/09/03 K.Hirata
    # It is not so good but I'd like to evaluate the usability/capability of Pandas for ZOODB.
    def getTimeSeries(self):
        if not self.isPrep: self.prep()
        # Initial values are set to -999.999
        self.mount_time = -60.0
        self.center_time = -60.0
        self.raster_time = -60.0
        self.ds_time = -60.0
        self.meas_time = -60.0

        # Time string from each process
        n_mount = self.pandadf['n_mount']

        time_dict = {"t_mount_start":np.nan, "t_mount_end":np.nan, "t_center_start":np.nan,
                      "t_center_end":np.nan, "t_raster_start":np.nan, "t_raster_end":np.nan,
                      "t_ds_start":np.nan, "t_ds_end":np.nan, "t_meas_start":np.nan, "t_meas_end":np.nan}

        # Loop for each Loop
        for index, row in self.pandadf.iterrows():
            # Time str will be extracted
            timestr = row['t_meas_start']
            self.logger.info("TIME_STR=%s MOUNT=%s" % (timestr, n_mount))

            # Roughly well but I am not confident this 'break' is okay for all data
            if timestr==0:
                self.logger.info("0-TIMESTR: TIME_STR=%s MOUNT=%s" % (timestr, n_mount))
                continue

            # Extract time series data from each line
            time_cols = timestr.split(",")
            n_mount = row['n_mount']
            #self.logger.info(time_cols)

            # Loop for checking 'n-th' data collection
            # judged by 'n_mount'
            # the 1st measurement: n_mount=1
            # the 2nd measurement: n_mount=2
            # storing 'time information' of the 'latest' measurement
            for each_time in time_cols:
                # Split columns to each time
                tmpstr = each_time.replace("{","").replace("}","").split(":")
                if len(tmpstr) == 1:
                    continue
                # measurements were done
                else:
                    type_str,time_str = tmpstr
                    cols = type_str.split("_")
                    cut_index = type_str.rfind("_")
                    time_type = type_str[:cut_index]
                    d_index = int(cols[2])
                    record_type = cols[0]
                    start_or_end = cols[1]
                    time_array_str = []

                    # Dictionary
                    if d_index == n_mount:
                        for key in list(time_dict.keys()):
                            if key.rfind(time_type) != -1:
                                time_dict[key]=pd.to_datetime(time_str)
                                if self.isDebug: print(("TIME: %s is found %s " % (time_type, time_dict[key])))
                                break

            if self.isDebug: 
                print("<<<<<<<<<<<<<<LOOP ENDS>>>>>>>>>>>>>>")
                print(("TIME_DICT=", time_dict))
            # Convert dictionary to panda.DataFrame
            time_series = pd.Series(time_dict)
            #time_series['meas_start_to_meas_end']=(time_series['t_meas_end'] - time_series['t_meas_start']).astype('timedelta64[s]')
            time_series['meas_start_to_meas_end']=(time_series['t_meas_end'] - time_series['t_meas_start']).total_seconds()
            time_series['meas_start_to_mount_end']=(time_series['t_mount_end'] - time_series['t_meas_start']).total_seconds()
            time_series['mount_end_to_cent_start']=(time_series['t_center_start'] - time_series['t_mount_end']).total_seconds()
            time_series['cent_start_to_cent_end']=(time_series['t_center_end'] - time_series['t_center_start']).total_seconds()
            time_series['cent_end_to_raster_start']=(time_series['t_raster_start'] - time_series['t_center_end']).total_seconds()
            time_series['raster_start_to_raster_end']=(time_series['t_raster_end'] - time_series['t_raster_start']).total_seconds()
            time_series['raster_end_to_ds_start']=(time_series['t_ds_start'] - time_series['t_raster_end']).total_seconds()
            time_series['ds_start_to_ds_end']=(time_series['t_ds_end'] - time_series['t_ds_start']).total_seconds()

            # Merging the 'time_series' to the original row(index)
            df_concat = pd.concat([row, time_series])
            if self.isDebug: print(("df_concat gyousu=",type(df_concat),len(df_concat.index)))
            if index == 0:
                new_df = pd.DataFrame(df_concat)
                if self.isDebug: print(("NEW_DF: gyou,retsu=", len(new_df.index), len(new_df.columns)))
            else:
                new_df = pd.concat([new_df, df_concat],axis=1)
                if self.isDebug: print(("NEW_DF: gyou,retsu=", len(new_df.index), len(new_df.columns)))

            time_dict = {"t_mount_start":np.nan, "t_mount_end":False, "t_center_start":np.nan,
                      "t_center_end":np.nan, "t_raster_start":np.nan, "t_raster_end":np.nan,
                      "t_ds_start":np.nan, "t_ds_end":np.nan, "t_meas_start":np.nan, "t_meas_end":np.nan}

        self.logger.info("#######################################################")
        self.logger.info("NEW_DF: gyou,retsu= %5d %5d" %(len(new_df.index), len(new_df.columns)))
        self.logger.info(new_df.T)
        self.logger.info("#######################################################")

        # Diff time calculation
        new_df = new_df.T
        #new_df.to_csv("saigo.csv",na_rep="0")

        return new_df

    def calcMeanTimeByMode(self, pandaDF, mode):
        sel_data_collect = pandaDF.isDS > 0
        #print(sel_data_collect)
        sel_mode = (pandaDF['mode']==mode)
        #print("MODE=",sel_mode)
        # mode is okay and data was collected
        final_criteria = sel_data_collect & sel_mode
        #print ("FINAL_CRITERIA")
        selected_df = pandaDF[final_criteria]
        mean_time = selected_df['meas_start_to_meas_end'].mean()
        # Raster scan area
        mean_raster_height = selected_df['scan_height'].mean()
        mean_raster_width = selected_df['scan_width'].mean()
        if mode == "multi":
            mean_nds = selected_df['nds_multi'].mean()
        if mode == "helical":
            mean_nds = selected_df['nds_helical'].mean()
        print(("Average: mode=%s,n_ok_loops=%5d, raster_area=%8.1f x %8.1f, %8.1f datasets, meas_time=%5.2f sec"
              %(mode, len(selected_df), mean_raster_height, mean_raster_width, mean_nds, mean_time)))

        return selected_df

    def showVarious(self):
        if not self.isPrep: self.prep()

        start_time = self.pand_dict['t_mount_end']
        self.logger.info("")

    def getSampleNameGroup(self):
        if not self.isPrep: self.prep()
        # Group by
        print("Grouping by sample_name")
        indices = self.pandadf.groupby('sample_name').groups
        print(("Grouping indices=", indices))
        # Extracting grouping information like this
        sample_name_list = []
        for sample_name, group_df in self.pandadf.groupby('sample_name'):
            print(("#################### SAMPLE_NAME=",sample_name))
            print(("MODE=",group_df['sample_name']))
            sample_name_list.append(group_df)

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")
        for l in sample_name_list:
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            for puck,pin,root,sample in zip(l['puckid'], l['pinid'],l['root_dir'],l['sample_name']):
                print((puck,pin,root,sample))

    """
    new_pan=[]
    for s in sample_name_list:
        pan = mydict.groupby('sample_name').get_group(s)

        new_pan.append(pan)

    print "@@@@@@@@MODE GROUPING@@@@@@@@"

    for n in new_pan:
        for mode, group_df in n.groupby('mode'):
            print mode, group_df
    """

if __name__ == "__main__":
    zoop = ZooPandas(sys.argv[1])
    zoop.init()

    #zoop.pickupMode("multi")
    #zoop.calcTime()
    #zoop.getSampleNameGroup()

    df=zoop.getTimeSeries()

    # # Helical and nds is not 0
    # sel_helical = df[(df['mode'] == 'helical')]
    # print("helical mean time=",sel_helical["meas_start_to_meas_end"].mean())
    # sel_helical = df[(df['mode'] == 'helical') & (df['nds_helical'] != 0)]
    # sel_helical.to_csv("helical.csv")
    # print("helical mean time=",sel_helical["meas_start_to_meas_end"].mean())
    #
    # # Multiple and nds is not 0
    # multi_multi = df[(df['mode'] == "multi")]
    # multi_multi.to_csv("multi.csv")
    # print("multi mean time=",multi_multi["meas_start_to_meas_end"].mean())
    # multi_multi = multi_multi[(df['mode'] == "multi")]
    # multi_multi.to_csv("multi.csv")
    # print("multi mean time=",multi_multi["meas_start_to_meas_end"].mean())

    column_order = ['pinid', 'puckid', 'mode', 'sample_name', 'ds_hbeam', 'ds_vbeam', 'exp_ds', 'exp_raster', 'flux', 'hebi_att',
         'isDS', 'isDone', 'isMount', 'ln2_flag', 'loopsize', 'maxhits', 'meas_name', 'n_mount', 'n_mount_fails',
         'nds_helical', 'nds_helpart', 'nds_multi', 'o_index', 'osc_width', 'raster_hbeam', 'raster_vbeam',
         'scan_height', 'scan_width', 'score_max', 'score_min', 'total_osc', 'warm_time', 'wavelength', 't_meas_start',
         't_mount_start', 't_mount_end', 't_center_start', 't_center_end', 't_raster_start', 't_raster_end', 't_ds_start', 't_ds_end',
         't_meas_end', 'meas_start_to_meas_end', 'meas_start_to_mount_end', 'mount_end_to_cent_start',
         'cent_start_to_cent_end', 'cent_end_to_raster_start', 'raster_start_to_raster_end', 'raster_end_to_ds_start',
         'ds_start_to_ds_end',
         'dist_raster', 'dist_ds'
        ]

    #multi_df = zoop.calcMeanTimeByMode(df, "multi")
    #helical_df = zoop.calcMeanTimeByMode(df, "helical")
    #single_df = zoop.calcMeanTimeByMode(df, "single")

    #df[column_order].to_csv("all_time.csv", na_rep='NULL',date_format='%Y%m%d%h%m%s')
    df[column_order].to_csv("all_time.csv", na_rep='NULL')
    print("Please check 'all_time.csv'")

    #multi_df[column_order].to_csv("multi_ok.csv")
    #helical_df[column_order].to_csv("helical_ok.csv")
    #single_df[column_order].to_csv("single_ok.csv")
