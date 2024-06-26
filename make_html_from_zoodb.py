import sys, datetime, time
from html_log_maker import ZooHtmlLog
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")

import ESA

dbfile = sys.argv[1]
esa = ESA.ESA(dbfile)
esa.getDict()
conds=esa.getDict()

name = "test"
html_maker = ZooHtmlLog(conds[0]['root_dir'], name, online=False)

loginfo = []

for cond in conds:
    if cond['mode'].lower() == "multi":
        nds = cond['nds_multi']
    elif cond['mode'].lower() == "helical":
        nds = cond['nds_helical']
    else:
        nds = 9999

    meas_start = "%s" % cond['t_meas_start']
    Y = meas_start[0:4]
    M = meas_start[4:6]
    d = meas_start[6:8]
    h = meas_start[8:10]
    m = meas_start[10:12]
    meas_start = "%s/%s/%s %02s:%02s" % (Y, M, d, h, m)
    shika_workdir = "%s/%s-%02d/scan00/_spotfinder/" % (cond['root_dir'], cond['puckid'], cond['pinid'])

    print meas_start
    start_time = datetime.datetime.strptime(meas_start, '%Y/%m/%d %H:%M')

        s = """
<h3>%(uname)s's sample</h3>
<h4>Conditions</h4>
<table class="dataset_table">
 <tr>
  <th>Beam size [&mu;m]</th> <td>h=%(h_beam).2f, v= %(v_beam).2f</td>
 </tr>
 <tr>
  <th>Raster scan</th> <td>Att= %(att_raster).1f%% trans., Exp= %(raster_exp).3f [s], Loop size= %(loop_size)s</td>
 </tr>
 <tr>
  <th>SHIKA criteria</th> <td>min_score= %(shika_minscore)s, min_dist= %(shika_mindist)s [&mu;m]</td>
 </tr>
 <tr>
  <th>Data collection</th> <td>&Delta;&phi;= %(osc_width).3f&deg;, &phi;-range= %(total_osc).2f&deg;, ExpHenderson= %(exp_henderson).2f [sec], ExpTime= %(exp_time).2f [sec], Distance= %(distance).2f [mm]</td>
 </tr>
 <tr>
  <th>Samples (%(totalpins)d pins)</th> <td>%(samples)s</td>
 </tr>
</table>
""" % info
        self.conditions.append([s])

    #def add_result(self, puckname, pin, h_grid, v_grid, nhits, shika_workdir, prefix, start_time):
    html_maker.add_result(
        cond['puckid'],
        cond['pinid'],
        cond['scan_height'],
        cond['scan_width'],
        nds,
        shika_workdir,
        "2d",
        meas_start)
        
        

"""
    root_dir = cond['root_dir']
    cond['p_index']
    cond['mode']
    cond['puckid']
    cond['pinid']
    cond['sample_name']
    cond['wavelength']
    cond['raster_vbeam']
    cond['raster_hbeam']
    cond['att_raster']
    cond['hebi_att']
    cond['exp_raster']
    cond['dist_raster']
    cond['loopsize']
    cond['score_min']
    cond['score_max']
    cond['maxhits']
    cond['total_osc']
    cond['osc_width']
    cond['ds_vbeam']
    cond['ds_hbeam']
    cond['exp_ds']
    cond['dist_ds']
    cond['dose_ds']
    cond['offset_angle']
    cond['reduced_fact']
    cond['ntimes']
    cond['meas_name']
    cond['cry_min_size_um']
    cond['cry_max_size_um']
    cond['hel_full_osc']
    cond['hel_part_osc']
    cond['isSkip']
    cond['isMount']
    cond['isLoopCenter']
    cond['isRaster']
    cond['isDS']
    cond['scan_height']
    cond['scan_width']
    cond['n_mount']
    cond['nds_multi']
    cond['nds_helical']
    cond['nds_helpart']
    cond['t_meas_start']
    cond['t_mount_end']
    cond['t_cent_start']
    cond['t_cent_end']
    cond['t_raster_start']
    cond['t_raster_end']
    cond['t_ds_start']
    cond['t_ds_end']
    cond['t_dismount_start']
    cond['t_dismount_end']
"""

"""
self.html_maker.add_result(puckname=trayid, pin=pinid,
        h_grid=self.lm.raster_n_width, v_grid=self.lm.raster_n_height,
        nhits=nhits, shika_workdir=os.path.join(self.lm.raster_dir, "_spotfinder"),
        prefix=self.lm.prefix, start_time=raster_start_time)
self.html_maker.write_html()
"""
