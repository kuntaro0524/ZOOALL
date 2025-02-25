import sqlite3, csv, os, sys, numpy
import ESA


if __name__ == "__main__":
    n_meas = 0
    n_collected = 0

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

        print "%10s-%02d"%(puckid,pinid),
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
            print "skipped."
            return
        if t_meas_start == "none":
            print "Not measured."
            return
        else:
            print "started. %-10s:  %15s " % (mode, t_meas_start),
        if isMount == 0:
            print "Mount failed"
            return
        if t_mount_end !=0:
            print "Mounted. ",
        if isLoopCenter != 0:
            print "Loop centered.",
        if isRaster != 0:
            print "raster scanned. ",
        if isRaster != 0 and isDS ==0:
            print "crystal cannot be found.",
        if isDS != 0:
            print "data collected.",
        print ""

    esa = ESA.ESA(sys.argv[1])
    #print esa.getTableName()
    #esa.listDB()
    conds_dict = esa.getDict()

    datedata=sys.argv[1].replace("zoo_","").replace("db","").replace(".","").replace("/","")
    progress_file="check_%s.dat"%datedata
    ofile=open(progress_file,"w")

    for cond in conds_dict:
        read_params(cond)
