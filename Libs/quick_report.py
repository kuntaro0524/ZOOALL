import os, sys, math
import DBinfo
import ESA

beamline = "BL32XU"

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()
    conds = esa.getDict()

    prefix_html = sys.argv[2]

    ofile = open("report_%s.html" % prefix_html,"w")

    ###########################################yyp
    def makeOnMouse(imgindex, picture, height, button):
        string = ""
        string += "<td><a href=%s " % picture
        string += "onmouseover=\"document.getElementById('ph-%ds').style.display='block';\" " % imgindex
        string += "onmouseout=\"document.getElementById('ph-%ds').style.display='none'; \"> %s </a> " % (imgindex, button)
        string += "<div style=\"position:absolute;\"> "
        string += "<img src=\"%s\" height=\"%d\" id=\"ph-%ds\"" % (picture, height, imgindex)
        string += " style=\"zindex: 10; position: absolute; top: 50px; display:none;\" /></td></div>"
    
        return string

    def pngFile(ppmfile, pngfile):
        command = "convert %s %s" % (ppmfile, pngfile)
        os.system(command)
    ###########################################yyp

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
    <th>puckid</th> <th>pinid</th> <th>sample_name</th> <th>mode</th> <th>wavelength</th> <th>total phi</th>
    <th>osc width</th> <th>raster beam</th> <th>raster area(grids)</th> <th>#DS</th> <th>log comment</th> <th>meas time[min]</th>
    <th>loop</th><th>2D scan</th><th>SHIKA</th>
    </tr>

    """

    footer_note = """
    </table>
    <h6>
    #DS: number of datasets collected from the pin.<br> "log comment" : Log comment from ZOO (easy check).<br>
    loop: a link to the picture of a loop before raster scan.<br>
    2D scan: a link to the picture of 2D raster heatmap.if<br>
    'X' appears on "loop" or "2D scan", there would not be crystals on the loop.<br>
    </h6></table>
    """

    ofile.write(title)

    print("Number of crystals processed", len(conds))
    n_good = 0
    #dpfile = open("automerge.csv","w")
    #dpfile.write("topdir,name,anomalous\n")

    # All pin information will be analyzed from zoo.db information
    # p -> each pin information
    imgindex = 0
    for p in conds:
        dbinfo = DBinfo.DBinfo(p)
        # 'isDS' is evaluated. -> normal termination : return 1
        n_good += dbinfo.getStatus()

        # is data collection completed?
        good_flag = dbinfo.getGoodOrNot()
        log_comment = dbinfo.getLogComment()

        # Common information for failed/succeeded pins
        puckid, pinid = dbinfo.getPinInfo()
        sample_name = dbinfo.sample_name
        wavelength = dbinfo.wavelength
        mode = dbinfo.mode

        total_osc = dbinfo.total_osc
        osc_width = dbinfo.osc_width

        # Writing common information
        dichtml = dict(puckid=puckid, pinid=pinid, sample_name=sample_name, wavelength=wavelength, mode=mode, total_osc=total_osc, osc_width=osc_width)

        good_str = """
         <tr>
          <td>%(puckid)s</td> <td>%(pinid)s</td> <td>%(sample_name)s</td> <td>%(mode)s</td> <td>%(wavelength).4f</td> 
          <td>%(total_osc).1f</td> <td>%(osc_width).2f</td>
        """ % dichtml

        if good_flag == True:
            ds_time = dbinfo.getDStime()
            mode = dbinfo.mode
            meas_time = dbinfo.getMeasTime()
            mount_time = dbinfo.getMountTime()
            raster_time = dbinfo.getRasterTime()
            center_time = dbinfo.getCenterTime()
            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = dbinfo.getRasterConditions()
            sample_name = dbinfo.sample_name
            wavelength = dbinfo.wavelength
            mode = dbinfo.mode
            hel_cry_size = dbinfo.hel_cry_size
            if beamline == "BL45XU":
                raster_png = "%s-%02d/scan00/2d/_spotfinder/plot_2d_n_spots.png" % (puckid,pinid)
            elif beamline == "BL32XU":
                raster_png = "%s-%02d/scan00/2d/_spotfinder/2d_selected_map.png" % (puckid,pinid)

            # Crystal capture
            cap_image = "%s-%02d/raster.jpg" % (puckid, pinid)

            nds = dbinfo.getNDS()
            t_sukima_raster = (raster_time * 60.0 - nv_raster * exp_raster * nh_raster) / (nv_raster - 1)

            dichtml = dict(puckid=puckid, pinid=pinid, sample_name=sample_name, wavelength=wavelength, mount_time=mount_time,
                           center_time=center_time, raster_time=raster_time, ds_time=ds_time, total_time=meas_time, nds=nds,
                           raster_height=height, raster_width=width, nv_raster=nv_raster, nh_raster=nh_raster, raster_vbeam=raster_vbeam,
                           raster_hbeam=raster_hbeam, att_raster=att_raster, exp_raster=exp_raster, comment=log_comment, hel_cry_size=hel_cry_size,
                           total_osc=total_osc, osc_width=osc_width, raster_png=raster_png)

            on_mouse_str = ""
            on_mouse_str += makeOnMouse(imgindex, cap_image, 400, "O")
            imgindex += 1
            on_mouse_str += makeOnMouse(imgindex, raster_png, 400, "O")
            imgindex += 1

            #print "ONMOUSE=",on_mouse_str

            good_str += """
              <td>%(raster_hbeam).0f&times;%(raster_vbeam).0f (um) <td>%(raster_height).0f&times;%(raster_width).0f 
              (%(nv_raster)d&times;%(nh_raster)d grids)</td> <td>%(nds)d</td> <td>%(comment)s</td> <td>%(total_time).2f</td>\n""" % dichtml
            good_str += on_mouse_str

            # SHIKA report file
            if beamline == "BL45XU":
                shika_report_file = "%s/report.html" % dbinfo.getSHIKAdir()
            elif beamline == "BL32XU":
                shika_report_file = "%s/report_zoo.html" % dbinfo.getSHIKAdir()
                
            rel_path = os.path.relpath(shika_report_file)
            good_str += "\n<td><a href=\"%s\">MAP</a></td>" % rel_path

            good_str += "\n</tr>\n"

            ofile.write("%s\n" % good_str)

        # Not good pins
        else:
            meas_time = dbinfo.getMeasTime()
            mount_time = dbinfo.getMountTime()
            raster_time = dbinfo.getRasterTime()
            center_time = dbinfo.getCenterTime()
            height, width, nv_raster, nh_raster, raster_vbeam, raster_hbeam, att_raster, exp_raster = dbinfo.getRasterConditions()
            nds = 0
            ds_time = 0.0
            if beamline == "BL45XU":
                raster_png = "%s-%02d/scan00/2d/_spotfinder/plot_2d_n_spots.png" % (puckid,pinid)
            elif beamline == "BL32XU":
                raster_png = "%s-%02d/scan00/2d/_spotfinder/2d_selected_map.png" % (puckid,pinid)

            dichtml = dict(puckid=puckid, pinid=pinid, mount_time=mount_time, center_time=center_time,
                           raster_time=raster_time, total_time=meas_time,
                           raster_height=height, raster_width=width, nv_raster=nv_raster, nh_raster=nh_raster,
                           raster_vbeam=raster_vbeam,
                           raster_hbeam=raster_hbeam, att_raster=att_raster, exp_raster=exp_raster, comment=log_comment,nds=nds,
                           raster_png=raster_png)

            # Crystal capture
            cap_image = "%s-%02d/raster.jpg" % (puckid, pinid)

            on_mouse_str = ""
            on_mouse_str += makeOnMouse(imgindex, cap_image, 400, "X")
            imgindex += 1
            on_mouse_str += makeOnMouse(imgindex, raster_png, 400,"X")
            imgindex += 1

            good_str += """
              <td>%(raster_hbeam).0f&times;%(raster_vbeam).0f (um) <td>%(raster_height).0f&times;%(raster_width).0f 
              (%(nv_raster)d&times;%(nh_raster)d grids)</td> <td>%(nds)d</td> <td>%(comment)s</td> <td>%(total_time).2f</td>""" % dichtml
            good_str += on_mouse_str
            # SHIKA report file
            if beamline == "BL45XU":
                shika_report_file = "%s/report.html" % dbinfo.getSHIKAdir()
            elif beamline == "BL32XU":
                shika_report_file = "%s/report_zoo.html" % dbinfo.getSHIKAdir()
            rel_path = os.path.relpath(shika_report_file)
            good_str += "\n<td><a href=\"%s\">???</a></td>" % rel_path
            good_str += "\n</tr>\n"

            if dbinfo.isDone != 0:
                ofile.write("%s\n" % good_str)

    ofile.write("%s\n" % footer_note)
    print("NDS processed = ", n_good)
        #if flag == True:
        #    dpfile.write("%s/_kamoproc/%s/,%s,no\n" % (rootdir,prefix,sample_name))


