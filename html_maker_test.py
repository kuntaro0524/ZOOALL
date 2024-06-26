import sys
from html_log_maker import ZooHtmlLog
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")

import Condition

root_dir="/isilon/users/target/target/iwata/151209BL32XU/Auto2/"

name = "kuntaro"

conditions = [Condition.Condition(uname="suno",
          pucks_and_pins=[
                          ["CPS1901", [8,10,11,12,13,14,15]],
                          ["CPS1902", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                          ["CPS1903", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                          ["CPS1904", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                          ["CPS1908", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                         ],
          mode="multi",
          wavelength=1.0000, # wavelength
          h_beam=10.0, #[um square shaped]
          v_beam=15.0, #[um square shaped]
          raster_exp=0.02, # [sec.] normally 0.02sec
          osc_width=0.1, #[deg.]
          total_osc=5.0, #[deg.]
          exp_henderson=0.467, #[sec] 10 MGy
          exp_time=0.1, #Fixed value
          distance=250.0, #[mm] len 10um width 1um
          att_raster=50.0, #[%] from 2016/10/04 # Raster attenuator transmission
          shika_minscore=15,
          shika_mindist=15,
          loop_size="large",
          helical_hbeam=10.0,
          helical_vbeam=15.0,
          phosec=1.5E10,
          ntimes=1,)]


html_maker = ZooHtmlLog(root_dir, name, online=False)

for cond in conditions:
    html_maker.add_condition(cond)

html_maker.write_html()

def make_offline(module_name, root_dir, name):
    md = __import__(module_name)
    zhl = ZooHtmlLog(root_dir, name, online=False)

    for cond in md.conditions:
        zhl.add_condition(cond)
        for trayid, pin_list in cond.pucks_and_pins:
            for pinid in pin_list:
                print "doing", trayid, pinid
                scan_dir = os.path.join(root_dir, "%s-%s-%.2d" % (cond.uname, trayid, pinid), "scan")
                shika_workdir = os.path.join(scan_dir, "_spotfinder")
                raster_log = os.path.join(scan_dir, "diffscan.log")
                if not os.path.exists(raster_log): continue
                h_grid, v_grid, scanstart = read_diffscanlog(raster_log)
                prefix, nhits = read_nhits(shika_workdir)
                zhl.add_result(puckname=trayid, pin=pinid,
                               h_grid=h_grid, v_grid=v_grid,
                               nhits=nhits,
                               shika_workdir=shika_workdir,
                               prefix=prefix,
                               start_time=scanstart)
                zhl.write_html()
# make_offline()

