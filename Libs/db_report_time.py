import os, sys, math
import DBinfo
import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()
    conds = esa.getDict()

    ofile = open("brief.html","w")

    title="""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
.dataset_table {
    font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
    width: 100%%;
    border-collapse: collapse;
}

.dataset_table td, .dataset_table th {
    font-size: 1em;
    border: 1px solid #98bf21;
    text-align: center;
    padding: 3px 7px 2px 7px;
}

.dataset_table th {
    font-size: 1.1em;
    text-align: center;
    padding-top: 5px;
    padding-bottom: 4px;
    background-color: #A7C942;
    color: #ffffff;
}

.dataset_table tr.alt td {
    color: #000000;
    background-color: #EAF2D3;
}   
    </style>
    <h4>Results</h4>
    <table class="dataset_table">
    <tr>
    <th>puckid</th> <th>pinid</th> <th>mount</th> <th>center</th> <th>raster</th> <th>meas</th>
                <th>DStime</th> <th>RasterSQ</th> <th>NV(raster)</th> <th>NH(raster)</th> <th>NumDS</th> <th>Summary</th>
    </tr>"""

    ofile.write(title)

    print("Number of crystals processed", len(conds))
    n_good = 0
    repfile = open("meas_time.csv","w")
    repfile.write("puckid,pinid,mount_min,center_min,raster_min,sukima_sec,ds_min,total_min,ras_height_um,ras_width_um,ras_height_grids,ras_width_grids,nds,comment")
          #%(puckid)s,%(pinid)s,%(mount_time).2f,%(center_time).2f,%(raster_time).2f,%(sukima_time).2f,%(ds_time).2f,%(total_time).2f,%(raster_height).1f,%(raster_width).1f,%(nv_raster)d,%(nh_raster)d,%(nds)d,%(comment)s """ % dichtml

    # All pin information will be analyzed from zoo.db information
    # p -> each pin information
    for p in conds:
        dbinfo = DBinfo.DBinfo(p)
        # 'isDS' is evaluated. -> normal termination : return 1
        n_good += dbinfo.getStatus()

        # is data collection completed?
        good_flag = dbinfo.getGoodOrNot()
        log_comment = dbinfo.getLogComment()

        if good_flag == True:
            puckid,pinid = dbinfo.getPinInfo()

            ds_time = dbinfo.getDStime()
            meas_time = dbinfo.getMeasTime()
            mount_time = dbinfo.getMountTime()
            raster_time = dbinfo.getRasterTime()
            center_time = dbinfo.getCenterTime()
            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = dbinfo.getRasterConditions()

            print("##### %10s - %2s ####" % (puckid, pinid))
            print("MOUNT =%6.2f min" % mount_time, end=' ')
            print("CENTER=%6.2f min" % center_time, end=' ')
            print("RASTER=%6.2f min" % raster_time, end=' ')
            print("DS    =%6.2f min" % ds_time, end=' ')
            print("TOTAL =%6.2f min" % (mount_time + center_time + raster_time + ds_time), end=' ')
            print("MEAS  =%6.2f min" % meas_time, end=' ')
            nds = dbinfo.getNDS()
            print("NDS   =%6d" % nds)
            print("NMOUNT = %6d" % dbinfo.n_mount)
            print("RASTER", height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster)

            t_sukima_raster = (raster_time * 60.0 - nv_raster * exp_raster * nh_raster) / (nv_raster - 1)
            print("SUKIMA = " , t_sukima_raster)

            dichtml = dict(puckid=puckid, pinid=pinid, mount_time=mount_time, center_time=center_time, raster_time=raster_time, ds_time=ds_time, total_time=meas_time, nds=nds,
                           raster_height=height, raster_width=width, nv_raster=nv_raster, nh_raster=nh_raster, raster_vbeam=raster_vbeam,
                           raster_hbeam=raster_hbeam, att_raster=att_raster, exp_raster=exp_raster, comment=log_comment,sukima_time=t_sukima_raster)

            good_str = """
         <tr>
          <td>%(puckid)s</td> <td>%(pinid)s</td> <td>%(mount_time).2f</td> <td>%(center_time).2f</td> <td>%(raster_time).2f</td> <td>%(ds_time).2f</td> <td>%(total_time).2f</td> <td>%(raster_height).1f&times;%(raster_width).1f</td> <td>%(nv_raster)d</td> <td>%(nh_raster)d</td> <td>%(nds)d</td> <td>%(comment)s</td>
         </tr>
        """ % dichtml
            good_str_csv = """
          %(puckid)s,%(pinid)s,%(mount_time).2f,%(center_time).2f,%(raster_time).2f,%(sukima_time).2f,%(ds_time).2f,%(total_time).2f,%(raster_height).1f,%(raster_width).1f,%(nv_raster)d,%(nh_raster)d,%(nds)d,%(comment)s """ % dichtml
            repfile.write("%s"%good_str_csv)
            ofile.write("%s\n" % good_str)

        # Not good pins
        else:
            puckid, pinid = dbinfo.getPinInfo()
            print("##### %10s - %2s ####" % (puckid, pinid))
            print("isDone code=", dbinfo.getIsDone())
            meas_time = dbinfo.getMeasTime()
            mount_time = dbinfo.getMountTime()
            raster_time = dbinfo.getRasterTime()
            center_time = dbinfo.getCenterTime()
            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = dbinfo.getRasterConditions()

            print("##### %10s - %2s ####" % (puckid, pinid))
            print("MOUNT =%6.2f min" % mount_time, end=' ')
            print("CENTER=%6.2f min" % center_time, end=' ')
            print("RASTER=%6.2f min" % raster_time, end=' ')
            ds_time = 0.0
            print("MEAS  =%6.2f min" % meas_time, end=' ')
            print("RASTER", height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster)

            t_sukima_raster = (raster_time * 60.0 - nv_raster * exp_raster * nh_raster) / (nv_raster - 1)
            print("SUKIMA = ", t_sukima_raster)

            dichtml = dict(puckid=puckid, pinid=pinid, mount_time=mount_time, center_time=center_time,
                           raster_time=raster_time, total_time=meas_time,
                           raster_height=height, raster_width=width, nv_raster=nv_raster, nh_raster=nh_raster,
                           raster_vbeam=raster_vbeam,
                           raster_hbeam=raster_hbeam, att_raster=att_raster, exp_raster=exp_raster, comment=log_comment,
                            sukima_time=t_sukima_raster)

            bad_str = """
             <tr>
              <td>%(puckid)s</td> <td>%(pinid)s</td> <td>%(mount_time).2f</td> <td>%(center_time).2f</td> <td>%(raster_time).2f</td> <td>--</td> <td>%(total_time).2f</td> <td>%(raster_height).1f&times;%(raster_width).1f</td> <td>%(nv_raster)d</td> <td>%(nh_raster)d</td> <td>--</td> <td>%(comment)s</td>
             </tr>
            """ % dichtml
            bad_str_csv = """
          %(puckid)s,%(pinid)s,%(mount_time).2f,%(center_time).2f,%(raster_time).2f,%(sukima_time).2f,--,%(total_time).2f,%(raster_height).1f,%(raster_width).1f,%(nv_raster)d,%(nh_raster)d,0,%(comment)s """ % dichtml
            repfile.write("%s"%bad_str_csv)
            ofile.write("%s\n" % bad_str)

    print("NDS processed = ", n_good)
        #if flag == True:
        #    dpfile.write("%s/_kamoproc/%s/,%s,no\n" % (rootdir,prefix,sample_name))


