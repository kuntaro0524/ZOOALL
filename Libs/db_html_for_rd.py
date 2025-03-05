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
<<<<<<< HEAD
    <th>puckid</th> <th>pinid</th> <th>Wavelength</th> <th>ds_vbeam</th> <th>ds_hbeam</th> <th>input_exptime</th>
                <th>dose_ds</th> <th>reduced_fact</th> <th>n_times</th> <th>NH(raster)</th> <th>NumDS</th> <th>Summary</th>
=======
    <th>puckid</th> <th>pinid</th> <th>mount</th> <th>center</th> <th>raster</th> <th>meas</th>
                <th>DStime</th> <th>RasterSQ</th> <th>NV(raster)</th> <th>NH(raster)</th> <th>NumDS</th> <th>Summary</th>
>>>>>>> zoo45xu/main
    </tr>"""

    ofile.write(title)

<<<<<<< HEAD
    print("Number of crystals processed", len(conds))
=======
    print "Number of crystals processed", len(conds)
>>>>>>> zoo45xu/main
    n_good = 0
    dpfile = open("automerge.csv","w")
    dpfile.write("topdir,name,anomalous\n")

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
<<<<<<< HEAD

            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = dbinfo.getRasterConditions()
            nds = dbinfo.getNDS()

            dichtml = dict(puck_pin=dbinfo.puck_pin, mode=dbinfo.mode, wavelength=dbinfo.wavelength,
                           ds_vbeam=dbinfo.ds_vbeam, ds_hbeam=dbinfo.ds_hbeam,
                           input_exptime=dbinfo.exp_ds, dose_ds=dbinfo.dose_ds, nds=nds,
                           reduced_fact=dbinfo.reduced_fact, ntimes=dbinfo.ntimes, nv_raster=nv_raster,
                           nh_raster=nh_raster, raster_vbeam=raster_vbeam,
=======
            puckid,pinid = dbinfo.getPinInfo()

            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = dbinfo.getRasterConditions()

            print "##### %10s - %2s ####" % (puckid, pinid)
            nds = dbinfo.getNDS()
            #print "RASTER", height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster

            t_sukima_raster = (raster_time * 60.0 - nv_raster * exp_raster * nh_raster) / (nv_raster - 1)
            print "SUKIMA = " , t_sukima_raster

            dichtml = dict(puckid=puckid, pinid=pinid, mount_time=mount_time, center_time=center_time, raster_time=raster_time, ds_time=ds_time, total_time=meas_time, nds=nds,
                           raster_height=height, raster_width=width, nv_raster=nv_raster, nh_raster=nh_raster, raster_vbeam=raster_vbeam,
>>>>>>> zoo45xu/main
                           raster_hbeam=raster_hbeam, att_raster=att_raster, exp_raster=exp_raster, comment=log_comment)

            good_str = """
         <tr>
<<<<<<< HEAD
          <td>%(puck_pin)s</td> <td>%(mode)s</td> <td>%(wavelength).4f</td> <td>%(ds_vbeam).2f</td> 
          <td>%(ds_hbeam).2f</td> <td>%(input_exptime).2f</td> <td>%(dose_ds).2f</td>
          <td>%(reduced_fact).2f</td><td>%(ntimes)d</td><td>%(nds)d</td> <td>%(comment)s</td>
=======
          <td>%(puckid)s</td> <td>%(pinid)s</td> <td>%(mount_time).2f</td> <td>%(center_time).2f</td> <td>%(raster_time).2f</td> <td>%(ds_time).2f</td> <td>%(total_time).2f</td> <td>%(raster_height).1f&times;%(raster_width).1f</td> <td>%(nv_raster)d</td> <td>%(nh_raster)d</td> <td>%(nds)d</td> <td>%(comment)s</td>
>>>>>>> zoo45xu/main
         </tr>
        """ % dichtml
            ofile.write("%s\n" % good_str)

        # Not good pins
        else:
<<<<<<< HEAD
            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = \
                dbinfo.getRasterConditions()

            input_exptime = 0.0

            dichtml = dict(puck_pin=dbinfo.puck_pin, mode=dbinfo.mode, wavelength=dbinfo.wavelength,
                           ds_vbeam=dbinfo.ds_vbeam, ds_hbeam=dbinfo.ds_hbeam,
                           input_exptime=dbinfo.exp_ds, dose_ds=dbinfo.dose_ds, nds=nds,
                           reduced_fact=dbinfo.reduced_fact, ntimes=dbinfo.ntimes, nv_raster=nv_raster,
                           nh_raster=nh_raster, raster_vbeam=raster_vbeam,
                           raster_hbeam=raster_hbeam, att_raster=att_raster, exp_raster=exp_raster, comment=log_comment)

            bad_str = """
         <tr>
          <td>%(puck_pin)s</td> <td>%(mode)s</td> <td>%(wavelength).4f</td> <td>%(ds_vbeam).2f</td> 
          <td>%(ds_hbeam).2f</td> <td>%(input_exptime).2f</td> <td>%(dose_ds).2f</td>
           <td>%(reduced_fact).2f</td><td>%(ntimes)d</td><td>%(nds)d</td> <td>%(comment)s</td>
         </tr>
        """ % dichtml
            
            ofile.write("%s\n" % bad_str)

    print("NDS processed = ", n_good)
=======
            puckid, pinid = dbinfo.getPinInfo()
            print "##### %10s - %2s ####" % (puckid, pinid)
            print "isDone code=", dbinfo.getIsDone()
            meas_time = dbinfo.getMeasTime()
            mount_time = dbinfo.getMountTime()
            raster_time = dbinfo.getRasterTime()
            center_time = dbinfo.getCenterTime()
            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = dbinfo.getRasterConditions()

            print "##### %10s - %2s ####" % (puckid, pinid)
            print "MOUNT =%6.2f min" % mount_time,
            print "CENTER=%6.2f min" % center_time,
            print "RASTER=%6.2f min" % raster_time,
            ds_time = 0.0
            print "MEAS  =%6.2f min" % meas_time,
            print "RASTER", height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster

            t_sukima_raster = (raster_time * 60.0 - nv_raster * exp_raster * nh_raster) / (nv_raster - 1)
            print "SUKIMA = ", t_sukima_raster

            dichtml = dict(puckid=puckid, pinid=pinid, mount_time=mount_time, center_time=center_time,
                           raster_time=raster_time, total_time=meas_time,
                           raster_height=height, raster_width=width, nv_raster=nv_raster, nh_raster=nh_raster,
                           raster_vbeam=raster_vbeam,
                           raster_hbeam=raster_hbeam, att_raster=att_raster, exp_raster=exp_raster, comment=log_comment)

            bad_str = """
             <tr>
              <td>%(puckid)s</td> <td>%(pinid)s</td> <td>%(mount_time).2f</td> <td>%(center_time).2f</td> <td>%(raster_time).2f</td> <td>--</td> <td>%(total_time).2f</td> <td>%(raster_height).1f&times;%(raster_width).1f</td> <td>%(nv_raster)d</td> <td>%(nh_raster)d</td> <td>--</td> <td>%(comment)s</td>
             </tr>
            """ % dichtml
            ofile.write("%s\n" % bad_str)

    print "NDS processed = ", n_good
>>>>>>> zoo45xu/main
        #if flag == True:
        #    dpfile.write("%s/_kamoproc/%s/,%s,no\n" % (rootdir,prefix,sample_name))


