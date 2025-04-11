import os, sys, math
import DBinfo
import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    #esa.getTableName()
    #esa.listDB()
    conds = esa.getDict()

    csv_filename = sys.argv[1].replace(".db","_dump.csv")
    csvfile = open(csv_filename,"w")

    csvfile.write("%5d pins in data base file.\n" % len(conds))
    csvfile.write("puck,pin,mode,raster_v,raster_h,raster_hgrids,raster_vgrids,"
                  "raster_vbeam,raster_hbeam,att_rater,exp_raster,mount_time,center_time,raster_time,nds,meas_time,log_comment\n")
    n_good = 0
    n_ng = 0
    # All pin information will be analyzed from zoo.db information
    # p -> each pin information
    for p in conds:
        dbinfo = DBinfo.DBinfo(p)
        # 'isDS' is evaluated. -> normal termination : return 1
        n_good += dbinfo.getStatus()

        # is data collection completed?
        good_flag = dbinfo.getGoodOrNot()
        log_comment = dbinfo.getLogComment()
        mode = dbinfo.mode

        if good_flag == True:
            puckid,pinid = dbinfo.getPinInfo()
            ds_time = dbinfo.getDStime()
            meas_time = dbinfo.getMeasTime()
            mount_time = dbinfo.getMountTime()
            raster_time = dbinfo.getRasterTime()
            center_time = dbinfo.getCenterTime()
            wavelength = dbinfo.getWavelength()
            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = dbinfo.getRasterConditions()
            nds = dbinfo.getNDS()
            sample_name = dbinfo.sample_name
            csvfile.write("%10s,%02d,%s,%s" % (puckid,pinid,mode,sample_name))
            csvfile.write("%8.5f," % wavelength)
            csvfile.write("%5.1f, %5.1f, %5d, %5d, %5.1f, %5.1f, %5.2f,%5.3f," % (height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster))
            csvfile.write("%5.2f, %5.2f, %5.2f, %5d,%6.2f,%20s,\n" % (mount_time, center_time, raster_time, nds, meas_time,log_comment))

        # Not good pins
        else:
            meas_time = dbinfo.getMeasTime()
            mount_time = dbinfo.getMountTime()
            raster_time = dbinfo.getRasterTime()
            center_time = dbinfo.getCenterTime()
            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = dbinfo.getRasterConditions()
            nds = dbinfo.getNDS()

            n_ng += 1
            puckid, pinid = dbinfo.getPinInfo()
            sample_name = dbinfo.sample_name
            csvfile.write("%10s,%02d,%s,%s" % (puckid,pinid,mode,sample_name))
            csvfile.write("%5.1f, %5.1f, %5d, %5d, %5.1f, %5.1f, %5.2f,%5.3f," % (height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster))
            csvfile.write("%5.2f, %5.2f, %5.2f, %5d,%6.2f,%20s,\n" % (mount_time, center_time, raster_time, nds, meas_time,log_comment))


            #print "MOUNT =%6.2f min" % mount_time,
            #print "CENTER=%6.2f min" % center_time,
            #print "RASTER=%6.2f min" % raster_time,
            ds_time = 0.0
            #print "MEAS  =%6.2f min" % meas_time,
            #print "RASTER", height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster
            t_sukima_raster = (raster_time * 60.0 - nv_raster * exp_raster * nh_raster) / (nv_raster - 1)
            #print "SUKIMA = ", t_sukima_raster

    print("NDS processed = ", n_good)
