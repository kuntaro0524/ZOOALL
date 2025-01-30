import os
import sys
import logging.handlers
import argparse
import glob
import sqlite3
import numpy
import time
import subprocess
import matplotlib.pyplot as plt
from datetime import datetime

from yamtbx.dataproc.xds.command_line import xds2mtz
from libtbx import easy_mp

header_note = """
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
</head>
<body>
<h4>Results</h4>
<table class="dataset_table">
  <tr>
    <th>puckid</th><th>pinid</th><th>sample_name</th><th>mode</th>
    <th>wavelength</th><th>total phi</th><th>osc width</th>
    <th>raster beam</th><th>raster area(grids)</th><th>#DS</th>
    <th>log comment</th>
    <th>meas time[min]</th>
    <th>loop</th>
    <th>2D scan</th>
    <th>SHIKA</th>
  </tr>
"""

footer_note = """
</table>
<h6>
#DS: number of datasets collected from the pin.<br> "log comment" : Log comment from ZOO (easy check).<br />
loop: a link to the picture of a loop before raster scan.<br />
2D scan: a link to the picture of 2D raster heatmap.if<br />
'X' appears on "loop" or "2D scan", there would not be crystals on the loop.<br />
</h6>
</body>
</html>
"""

xds_header = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title> KAMO scaling results </title>
    <style>
      h1 {
        color: red;
        font-size:18px;
        font-family: "Courier New";
      }
      h2 {
        color: blue;
        font-size:18px;
        font-family: "Courier New";
      }
      div {
        background: #FFFACD; 
        width:1000px; 
        border: 1px solid #D3D3D3; 
        height:100%;
        padding-left:10px;
        padding-right:10px; 
        padding-top:10px; 
        padding-bottom:10px;
      }
      pre {
        background: #FFFACD;
        font-size:15px;
        font-family: "Courier New";
      }
        
      p1 {
        background: yellow;
        border: 2px solid orange; 
        height:100%; 
        padding-left:5px; 
        padding-right:5px; 
        padding-top:5px; 
        padding-bottom:5px;
        line-height: 200%
      }
      p2 {
        height:100%; 
        border-bottom: solid 3px orange;
        padding-left:2px; 
        padding-right:2px; 
        padding-top:2px; 
        font-size:18px;
        font-family:"Courier New";
        line-height:20px;
        line-height: 150%
      }
      p3 {
        border-bottom: solid 3px #87CEFA;
        height:100%;
        padding-left:2px; 
        padding-right:2px; 
        padding-top:2px; 
        font-size:18px;
        font-family:"Courier New";
        line-height:20px;
        line-height: 150%
      }
      hr {
        border-top: 10px solid #bbb;
        border-bottom: 3px solid #fff;
      }
      body {
        line-height: 1.2;
      }
    </style>
  </head>
  <body>
"""


class Logger:
    def __init__(self, log_path, name="toilet"):
        log_form = logging.Formatter(fmt="[%(asctime)s.%(msecs)03d][%(name)s][%(levelname)s] %(message)s",
                                     datefmt="%Y-%m-%d %H:%M:%S")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_form)
        self.logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(log_form)
        self.logger.addHandler(file_handler)

        return


class DBInfo:
    def __init__(self, cond):
        self.log = logs.getChild("dbinfo")

        self.root_dir = cond['root_dir']
        self.oindex = cond['o_index']
        self.pindex = cond['p_index']
        self.mode = cond['mode']
        self.puckid = cond['puckid']
        self.pinid = cond['pinid']
        self.sample_name = cond['sample_name']
        self.wavelength = cond['wavelength']

        self.raster_vbeam = cond['raster_vbeam']
        self.raster_hbeam = cond['raster_hbeam']
        self.att_raster = cond['att_raster']
        self.hebi_att = cond['hebi_att']
        self.exp_raster = cond['exp_raster']
        self.dist_raster = cond['dist_raster']
        self.loopsize = cond['loopsize']
        self.score_min = cond['score_min']
        self.score_max = cond['score_max']
        self.maxhits = cond['maxhits']

        self.total_osc = cond['total_osc']
        self.osc_width = cond['osc_width']
        self.ds_vbeam = cond['ds_vbeam']
        self.ds_hbeam = cond['ds_hbeam']
        self.exp_ds = cond['exp_ds']
        self.dist_ds = cond['dist_ds']
        self.dose_ds = cond['dose_ds']
        self.offset_angle = cond['offset_angle']
        self.reduced_fact = cond['reduced_fact']
        self.ntimes = cond['ntimes']
        self.meas_name = cond['meas_name']
        self.cry_min_size_um = cond['cry_min_size_um']
        self.cry_max_size_um = cond['cry_max_size_um']
        self.hel_full_osc = cond['hel_full_osc']
        self.hel_part_osc = cond['hel_part_osc']

        self.raster_roi = cond['raster_roi']
        self.ln2_flag = cond['ln2_flag']
        self.cover_scan_flag = cond['cover_scan_flag']
        self.zoomcap_flag = cond['zoomcap_flag']
        self.warm_time = cond['warm_time']

        self.isSkip = cond['isSkip']
        self.isMount = cond['isMount']
        self.isLoopCenter = cond['isLoopCenter']
        self.isRaster = cond['isRaster']
        self.isDS = cond['isDS']
        self.isDone = cond['isDone']

        self.scan_height = cond['scan_height']
        self.scan_width = cond['scan_width']

        self.n_mount = cond['n_mount']

        self.nds_multi = cond['nds_multi']
        self.nds_helical = cond['nds_helical']
        self.nds_helpart = cond['nds_helpart']

        self.t_meas_start = cond['t_meas_start']
        self.t_mount_end = cond['t_mount_end']
        self.t_cent_start = cond['t_cent_start']
        self.t_cent_end = cond['t_cent_end']
        self.t_raster_start = cond['t_raster_start']
        self.t_raster_end = cond['t_raster_end']
        self.t_ds_start = cond['t_ds_start']
        self.t_ds_end = cond['t_ds_end']
        self.t_dismount_start = cond['t_dismount_start']
        self.t_dismount_end = cond['t_dismount_end']

        self.data_index = cond['data_index']
        self.n_mount_fails = cond['n_mount_fails']
        self.log_mount = cond['log_mount']
        self.hel_cry_size = cond['hel_cry_size']
        self.flux = cond['flux']
        self.phs_per_deg = cond['phs_per_deg']

        self.prefix = "{}-{:02d}".format(self.puckid, self.pinid)

        if self.t_meas_start == 0:
            self.mount_time = -60.0
            self.center_time = -60.0
            self.raster_time = -60.0
            self.ds_time = -60.0
            self.meas_time = -60.0
        else:
            ts = {}
            times = self.t_meas_start.split(",")
            for etime in times:
                time_str = etime.replace("{", "").replace("}", "").split(":")
                if len(time_str) == 2:
                    k, t = time_str
                    date_time_str = "{}-{}-{} {}:{}:{}".format(t[0:4], t[4:6], t[6:8], t[8:10], t[10:12], t[12:14])
                    date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                    ks = k.split("_")
                    key = "_".join(ks[0:2])
                    if int(ks[2]) == self.n_mount:
                        print(key, int(ks[2]), self.n_mount, date_time)
                        ts[key] = date_time

            print(ts)

            self.mount_time = (ts["mount_end"] - ts["mount_start"]).seconds
            self.center_time = (ts["center_end"] - ts["center_start"]).seconds
            self.raster_time = (ts["raster_end"] - ts["raster_start"]).seconds
            try:
                self.ds_time = (ts["ds_end"] - ts["ds_start"]).seconds
            except Exception as e:
                self.log.warning("ds_time cannot be calculated: {}".format(e.args))
            self.meas_time = (ts["meas_end"] - ts["meas_start"]).seconds

        self.log_comment = "no comment"

    def get_good_flag(self):
        error_msgs = {
            0: "Not finished.",
            4001: "Multi-small wedge: failed to find crystal in 2D scan",
            4002: "Single: No crystals found in a raster scan",
            4003: "Helical: failed to find crystal in 2D scan",
            4004: "Helical: failed to find crystal",
            4005: "Single: failed to find crystal in 2D scan",
            4006: "Single: failed to find crystal in vertical scan",
            5001: "SPACE Warning",
            5002: "Loop centering failed(INOCC)",
            9998: "SPACE unknown error",
            9999: "SPACE accident"
        }

        if self.isDone in error_msgs:
            self.log_comment = error_msgs[self.isDone]
            return False
        else:
            self.log_comment = "Normal Termination"
            return True

    def get_nds(self):
        if self.mode == "helical":
            return self.nds_helical
        elif self.mode == "multi":
            return self.nds_multi
        elif self.mode == "single":
            return self.isDS
        else:
            self.log.warning("mode is not [helical, multi, single]")
            return 0.0

    def get_ds_time(self, unit="min"):
        if unit == "min":
            return self.ds_time / 60.0
        else:
            return self.ds_time


class Unko:
    def __init__(self, root_dir):
        self.log = logs.getChild("unko")
        self.root_dir = os.path.abspath(root_dir)
        self.required_files = ["CORRECT.LP", "XDS_ASCII.HKL"]
        self.good_large_wedge_dirs = []
        self.dir_dict = {
            "merge": [],
            "each_procd": [],
            "small_wedge": [],
            "large_wedge": []
        }
        self.get_process_dirs()

    def get_process_dirs(self):
        proc_dirs = [d for d in os.listdir(self.root_dir) if os.path.isdir(os.path.join(self.root_dir, d))]
        for d in proc_dirs:
            d_abs = os.path.join(self.root_dir, d)
            if d.startswith("merge"):
                self.dir_dict["merge"].append(d_abs)
            pin_dirs = [dd for dd in os.listdir(d_abs) if os.path.isdir(os.path.join(d_abs, dd))]
            for dd in pin_dirs:
                if dd.startswith("data"):
                    dd_abs = os.path.join(d_abs, dd)
                    self.dir_dict["each_procd"].append(dd_abs)
                else:
                    self.log.debug("No data processed: {}".format(dd))
        for d in self.dir_dict["each_procd"]:
            data_dirs = [dd for dd in os.listdir(d) if os.path.isdir(os.path.join(d, dd))]
            for dd in data_dirs:
                if dd.count("multi"):
                    self.dir_dict["small_wedge"].append(os.path.join(d, dd))
                else:
                    self.dir_dict["large_wedge"].append(os.path.join(d, dd))

        return self.dir_dict

    def make_report_large_wedge(self, mtz_option=True):
        arc_large_wedge = []
        to_be_made = []

        self.good_large_wedge_dirs = []
        for d in self.dir_dict["large_wedge"]:
            correct_path = os.path.join(d, "CORRECT.LP")
            if os.path.exists(correct_path) is True:
                self.good_large_wedge_dirs.append(d)

        for xds_proc_dir in self.good_large_wedge_dirs:
            for required_file in self.required_files:
                required_path = os.path.join(xds_proc_dir, required_file)
                if os.path.exists(required_path) is True:
                    required_rel_path = os.path.relpath(required_path)
                    if required_file == "XDS_ASCII.HKL":
                        if mtz_option is True:
                            mtz_generate_path = os.path.relpath(os.path.join(xds_proc_dir, "ccp4/XDS_ASCII.mtz"))
                            arc_large_wedge.append(mtz_generate_path)
                            if os.path.exists(mtz_generate_path) is True:
                                self.log.warning("XDS_ASCII.mtz already exists {}".format(mtz_generate_path))
                            else:
                                to_be_made.append((xds_proc_dir, required_rel_path))
                        else:
                            arc_large_wedge.append(required_rel_path)
                    else:
                        arc_large_wedge.append(required_rel_path)

        if len(to_be_made) > 0:
            easy_mp.pool_map(fixed_func=self.multi_gen_mtz, args=to_be_made, processes=8)
            self.log.info("# waiting for 10 seconds to generate mtz")
            time.sleep(10.0)

        return arc_large_wedge

    def multi_gen_mtz(self, params):
        xds_proc_dir, xds_ascii_path = params

        mtz_generate_path = os.path.join(xds_proc_dir, "ccp4")
        self.log.info("generating mtz in {}".format(mtz_generate_path))

        if os.path.exists(mtz_generate_path):
            self.log.info("ccp4 path already exists {}".format(mtz_generate_path))
            mtz_paths = glob.glob("{}/**/*.mtz".format(xds_proc_dir), recursive=True)
            if len(mtz_paths) > 0:
                self.log.warning("MTZ file already exists {}".format(mtz_paths[0]))
                if len(mtz_paths) > 1:
                    self.log.warning("two or more MTZ files were found")
                    self.log.warning("the routine returns the first MTZ file path")
                return mtz_paths[0]

        try:
            xds_file = os.path.join(xds_proc_dir, "XDS_ASCII.HKL")
            ccp4_path = os.path.join(xds_proc_dir, "ccp4")
            xds2mtz.xds2mtz(xds_file, ccp4_path)
        except Exception as e:
            self.log.error(e.args)

        generated_mtz_path = xds_ascii_path.replace(".HKL", ".mtz")
        return generated_mtz_path

    def get_list_finished_merge_dirs(self):
        fin_paths = []
        ok_paths = []
        for check_path in self.dir_dict["merge"]:
            first_layers = [d for d in os.listdir(check_path) if os.path.isdir(os.path.join(check_path, d))]
            for fdir in first_layers:
                if fdir.count("_final"):
                    final_path = os.path.abspath(os.path.join(check_path, fdir))
                    self.log.debug("merge final path: {}".format(final_path))
                    kamo_merge_log = os.path.join(final_path, "multi_merge.log")
                    self.log.info("{} if checking.".format(kamo_merge_log))
                    if os.path.exists(kamo_merge_log) is True:
                        status = 0
                        with open(kamo_merge_log, "r") as fin:
                            for line in fin:
                                if line.count("ERROR: No clusters satisfied the specified conditions for merging"):
                                    self.log.error("merge error: {}".format(kamo_merge_log))
                                    status = 1001
                                if line.count("Normal exit at") and status == 0:
                                    ok_paths.append(final_path)
                                    break
                    fin_paths.append(final_path)
                else:
                    continue
        self.log.info("number of final paths: {:5d}".format(len(fin_paths)))
        self.log.info("number of final paths: {:5d}".format(len(ok_paths)))

        return ok_paths

    def get_final_result_paths(self, ok_paths):
        final_run_paths = []

        for ok_path in ok_paths:
            self.log.debug("searching in {}".format(ok_path))
            cluster_paths = [d for d in os.listdir(ok_path)
                             if os.path.isdir(os.path.join(ok_path, d)) and d.count("cluster_")]
            max_num = 0
            max_cluster_path = ok_path
            for cluster_path in cluster_paths:
                num = int(cluster_path.split("_")[1])
                if max_num < num:
                    max_num = num
                    max_cluster_path = os.path.join(ok_path, cluster_path)

            self.log.debug("searching in {}".format(max_cluster_path))
            run_paths = [d for d in os.listdir(max_cluster_path)
                         if os.path.isdir(os.path.join(max_cluster_path, d)) and d.count("run_")]
            max_run = 0
            max_run_path = max_cluster_path
            for run_path in run_paths:
                try:
                    num_run = int(run_path.replace("run_", ""))
                    if num_run > max_run:
                        max_run = num_run
                        max_run_path = os.path.join(max_cluster_path, run_path)
                except Exception as e:
                    self.log.error("something wrong in {}: {}".format(run_path, e))

            final_run_paths.append(max_run_path)

        return final_run_paths

    def get_report_html_paths(self, ok_paths):
        html_report_paths = []
        for ok_path in ok_paths:
            self.log.debug("searching in {}".format(ok_path))
            report_html_path = os.path.join(ok_path, "report.html")
            if os.path.exists(report_html_path) is True:
                report_html_rel_path = os.path.relpath(report_html_path)
                html_report_paths.append(report_html_rel_path)
            else:
                continue

        return html_report_paths

    def get_reflection_paths(self, run_paths, check_list=None, is_mtz=True):
        if check_list is None:
            check_list = ["XSCALE.LP", "XSCALE.INP", "aniso.log", "pointless.log"]

        reflection_paths = []
        for run_path in run_paths:
            for check_path in check_list:
                check_abs_path = os.path.join(run_path, check_path)
                if os.path.exists(check_abs_path) is True:
                    rel_path = os.path.relpath(str(check_abs_path))
                    self.log.debug("[ok] checking existence: {}".format(check_abs_path))
                    reflection_paths.append(rel_path)

            if is_mtz is True:
                mtz_path = os.path.join(run_path, "ccp4/xscale.mtz")
                mtz_rel_path = os.path.relpath(mtz_path)
                if os.path.exists(mtz_rel_path) is True:
                    reflection_paths.append(mtz_rel_path)

        return reflection_paths


class AnaCORRECT:
    def __init__(self, fname):
        self.log = logs.getChild("ana_correct")
        self.ndata = 0

        self.dmin = []
        self.ds2 = []
        self.nrefl = []
        self.nuniq = []
        self.compl = []
        self.rmeas = []
        self.isigi = []
        self.redun = []
        self.cchalf = []

        self.unit_cell = 0, 0, 0, 0, 0, 0
        self.spg_num = 0
        self.spg_name = ""
        self.isa = 0

        with open(fname, "r") as lp:
            lines = lp.readlines()

        start = 0
        end = -1
        for i, ln in enumerate(lines):
            if ln.count("INPUT_FILE="):
                self.ndata += 1

            elif ln.count("SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION"):
                start = i
            elif start > 0 and ln.count("total"):
                end = i

            elif ln.count("UNIT_CELL_CONSTANTS="):
                c = ln.split()
                self.unit_cell = (float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5]), float(c[6]))

            elif ln.count("SPACE_GROUP_NUMBER="):
                c = ln.split()
                self.spg_num = int(c[1])

            elif ln.count("ISa"):
                c = lines[i+1].split()
                if len(c) < 4:
                    self.isa = float(c[2])

        if os.environ['CLIBD'] != "":
            clibd_path = os.environ['CLIBD']
        else:
            clibd_path = os.path.join(os.environ['DIALS'], "modules/ccp4io/libccp4/data")
        clibd = os.path.join(clibd_path, "symop.lib")
        with open(clibd, "r") as symop:
            for ln in symop:
                c = ln.split()
                if len(c) > 5 and self.spg_num == int(c[0]):
                    self.spg_name = c[3]

        self.lp_table = lines[start:end + 1]
        if end == -1:
            self.log.error("failed: something wrong in CORRECT.LP/XSCALE.LP")
        else:
            for ln in self.lp_table[4:]:
                cols = ln.split()
                print("#{}".format(ln.rstrip()))
                if cols[0] == "total":
                    # self.total_compl = float(cols[4].replace("%", ""))
                    # self.total_rfact = float(cols[5].replace("%", ""))
                    # self.total_isigi = float(cols[8])
                    # self.total_cc_half = float(cols[10].replace("*", ""))
                    self.total_compl = float(ln[39:50])
                    self.total_rfact = float(ln[51:61])
                    self.total_isigi = float(ln[81:89])
                    self.total_cc_half = float(ln[99:107])
                else:
                    dmin = float(cols[0])
                    ds2 = 1.0 / dmin / dmin
                    nobs = int(cols[1])
                    nuniq = int(cols[2])
                    redun = float(nobs) / float(nuniq) if nuniq != 0 else 0.0

                    self.dmin.append(dmin)
                    self.ds2.append(ds2)
                    self.nrefl.append(nobs)
                    self.nuniq.append(nuniq)
                    # self.compl.append(float(cols[4].replace("%", "")))
                    # self.rmeas.append(float(cols[5].replace("%", "")))
                    # self.isigi.append(float(cols[8]))
                    # self.cchalf.append(float(cols[10].replace("*", "")))
                    self.compl.append(float(ln[39:50]))
                    self.rmeas.append(float(ln[51:61]))
                    self.isigi.append(float(ln[81:89]))
                    self.cchalf.append(float(ln[99:107]))
                    self.redun.append(redun)

    def make_plot(self, out_fig, dpi=60):
        ds2 = numpy.array(self.ds2)
        cchalf = numpy.array(self.cchalf)
        isigi = numpy.array(self.isigi)
        rmeas = numpy.array(self.rmeas)
        compl = numpy.array(self.compl)

        fig = plt.figure(facecolor="lightgreen", figsize=(15, 3), dpi=dpi)
        ax1 = fig.add_axes([0.05, 0.15, 0.14, 0.75])
        ax2 = fig.add_axes([0.25, 0.15, 0.14, 0.75])
        ax3 = fig.add_axes([0.45, 0.15, 0.14, 0.75])
        ax4 = fig.add_axes([0.65, 0.15, 0.14, 0.75])
        ax5 = fig.add_axes([0.85, 0.15, 0.14, 0.75])

        ax1.grid()
        ax2.grid()
        ax3.grid()
        ax4.grid()
        ax5.grid()
        ax1.set_xlabel("$d^{*2}$")
        ax2.set_xlabel("$d^{*2}$")
        ax3.set_xlabel("$d^{*2}$")
        ax4.set_xlabel("$d^{*2}$")
        ax5.set_xlabel("<I/sigI>")
        ax1.set_ylim(0, 100)
        ax1.set_title("$d*{^2}$ .vs. Completeness")
        ax2.set_title("$d*{^2}$ .vs. Rmeas")
        ax3.set_title("$d*{^2}$ .vs. <I/sigI>")
        ax4.set_title("$d*{^2}$ .vs. CC(1/2)")
        ax4.set_ylim(0, 100)
        ax5.set_title("<I/sigI> .vs. CC(1/2)")
        ax5.set_xscale('log')

        ax1.plot(ds2, compl, label="Completeness", color="brown", marker="o")
        ax1.set_ylabel("Completeness[%]")
        ax2.plot(ds2, rmeas, label="Rmeas", color="black", marker="h")
        ax2.set_ylabel("Rmeas")
        ax3.plot(ds2, isigi, label="<I/sigI>", color="red", marker="<")
        ax3.set_ylabel("<I/sigI>")
        ax4.plot(ds2, cchalf, label="CC(1/2)", color="blue", marker=">")
        ax4.set_ylabel("CC(1/2) [%]")
        ax5.plot(isigi, cchalf, label="CC(1/2)", color="green", marker="D")
        ax5.set_ylabel("CC(1/2)")

        ax1.legend()
        ax2.legend()
        ax3.legend()
        ax4.legend(loc="center left")
        ax5.legend()
        fig.savefig(out_fig)

        self.log.info("written figure: {}".format(out_fig))


class XDSReporter:
    def __init__(self, root_path, logfile="CORRECT.LP"):
        self.log = logs.getChild("xds_repo")
        self.root_path = os.path.abspath(root_path)

        self.log_list = glob.glob("{}/**/{}".format(root_path, logfile), recursive=True)
        self.log_list.sort()

    def make_html(self, html_name="correct.html", fig_dpi=60, skip_multi=True):
        html_path = os.path.join(self.root_path, html_name)
        contents_path = os.path.join(self.root_path, "contents")
        if os.path.exists(contents_path) is False:
            os.makedirs(contents_path)

        out_log = ""
        figure_data = []
        for correct in self.log_list:
            fig_name = "{}.png".format(os.path.dirname(os.path.relpath(correct)).replace("/", "-"))
            fig_path = os.path.join(contents_path, fig_name)

            if skip_multi is True:
                if correct.count("multi_"):
                    self.log.info("skipping {} because it is multiple small wedge data".format(correct))
                    continue

            ac = AnaCORRECT(correct)
            if os.path.exists(fig_path) is True:
                self.log.info("skipping {} generation because it already exists".format(fig_path))
            else:
                self.log.info("multi_make_plots: {} {}".format(correct, fig_path))
                figure_data.append((correct, fig_path, fig_dpi))

            wpx = int(fig_dpi * 18)
            hpx = int(wpx * 3 / 15)

            out_log += "<p1>{}</p1><br />\n".format(os.path.relpath(correct, self.root_path))
            out_log += ("<p2>Space group(XDS) = {}, cell: {:8.3f} {:8.3f} {:8.3f} {:8.2f} {:8.2f} {:8.2f}</p2><br />\n"
                        .format(ac.spg_name, *ac.unit_cell))
            out_log += "<p3>ISa(XDS) = {:5.1f}</p3><br />".format(ac.isa)
            out_log += "<pre>\n"
            for ln in ac.lp_table:
                out_log += "{}".format(ln)
            out_log += "</pre>\n"
            out_log += ("<img src='{}' width='{}px' height='{}px' alt='XDS stats'>\n<hr>\n"
                        .format(os.path.join("contents", fig_name), wpx, hpx))

        out_log += "  </body>\n</html>"

        with open(html_path, "w") as fout:
            fout.write(xds_header)
            fout.write(out_log)

        if len(figure_data) > 0:
            easy_mp.pool_map(fixed_func=self.multi_make_plot, args=figure_data, processes=8)
            self.log.info("# waiting for 10 seconds to generate figure")
            time.sleep(10.0)

    def multi_make_plot(self, params):
        correct, fig_path, fig_dpi = params
        self.log.info("multiple making plots: {}".format(fig_path))
        ac = AnaCORRECT(correct)
        ac.make_plot(fig_path, fig_dpi)


class ZOOReporter:
    def __init__(self, zoodb, beamline, zoom_flg=None):
        self.log = logs.getChild("zoo_repo")
        self.n_good = 0
        self.zoodb = zoodb
        self.imgindex = 0
        self.beamline = beamline.lower()
        self.crystal_report_paths = []
        self.zoom_flg = zoom_flg

        self.conds = []
        db = sqlite3.connect(zoodb)
        cur = db.cursor()
        cur.execute("select * from ESA")
        for row in cur.fetchall():
            x = dict(zip([d[0] for d in cur.description], row))
            self.conds.append(x)

    def make_html(self, html_prefix):
        html_filename = "report_{}.html".format(html_prefix)

        html_conds = ""
        for cond in self.conds:
            html_cond = self.make_html_for_cond(cond)
            if html_cond == "NO_INFO":
                continue
            else:
                html_conds += html_cond

        with open(html_filename, "w") as html_out:
            html_out.write(header_note)
            html_out.write(html_conds)
            html_out.write(footer_note)

        return os.path.abspath(html_filename)

    def make_on_mouse(self, img_path, height, button):
        rtn_str = f"""
    <td>
      <a href={img_path} onmouseover=\"document.getElementById('ph-{self.imgindex:d}s').style.display='block';\"
      onmouseout=\"document.getElementById('ph-{self.imgindex:d}s').style.display='none';\"> {button} </a>
      <div style=\"position:absolute;\">
        <img src=\"{img_path}\" height=\"{height:d}\" id=\"ph-{self.imgindex:d}s\"
        style=\"zindex: 10; position: absolute; top: 50px; display:none;\" />
      </div>
    </td>"""

        return rtn_str

    def make_html_for_cond(self, cond):
        d = DBInfo(cond)

        if d.get_good_flag() is True:
            nds = int(d.get_nds())
            button = "O"
            # ds_time = d.get_ds_time()
        else:
            nds = 0
            button = "X"
            # ds_time = 0.0

        nv_raster = int(d.scan_height/d.raster_vbeam)
        nh_raster = int(d.scan_width/d.raster_hbeam)

        good_str = f"""
  <tr>
    <td>{d.puckid}</td><td>{d.pinid}</td><td>{d.sample_name}</td><td>{d.mode}</td>
    <td>{d.wavelength:.4f}</td><td>{d.total_osc:.1f}</td><td>{d.osc_width:.2f}</td>
    <td>{d.raster_hbeam:.0f}&times;{d.raster_vbeam:.0f} (um)</td>
    <td>{d.scan_height:.0f}&times;{d.scan_width:.0f} ({nv_raster:d}&times;{nh_raster:d} grids)</td>
    <td>{nds:d}</td><td>{d.log_comment}</td><td>{d.meas_time/60:.2f}</td>"""

        # Add file paths to the common list object
        raster_png = "{}/scan{:02d}/2d/_spotfinder/plot_2d_n_spots.png".format(d.prefix, d.n_mount)
        raster_tmp = "{}/scan{:02d}/2d/_spotfinder/2d_selected_map.png".format(d.prefix, d.n_mount)
        if self.beamline == "bl32xu" and os.path.exists(raster_tmp):
            raster_png = raster_tmp
        if os.path.exists(raster_png) is True:
            self.crystal_report_paths.append(raster_png)
        else:
            self.log.warning("raster spots figure is not found: {}".format(raster_png))

        # Crystal capture
        cap_image = "{}/raster.jpg".format(d.prefix)
        if os.path.exists(cap_image) is True:
            self.crystal_report_paths.append(cap_image)
        else:
            self.log.warning("scan area capture image is not found: {}".format(cap_image))

        good_str += self.make_on_mouse(cap_image, 400, button)
        self.imgindex += 1
        good_str += self.make_on_mouse(raster_png, 400, button)
        self.imgindex += 1

        if self.zoom_flg:
            zoom_image = "{}/loop_zoom.ppm".format(d.prefix)
            zoom_ln2_image = "{}/loop_zoom_ln2.ppm".format(d.prefix)
            if os.path.exists(zoom_ln2_image):
                self.crystal_report_paths.append(zoom_ln2_image)
            elif os.path.exists(zoom_image):
                self.crystal_report_paths.append(zoom_image)

        shika_repo_file = "{}/{}/scan{:02d}/2d/_spotfinder/report.html".format(d.root_dir, d.prefix, d.n_mount)
        if self.beamline == "bl32xu":
            shika_repo_file = "{}/{}/scan{:02d}/2d/_spotfinder/report_zoo.html".format(d.root_dir, d.prefix, d.n_mount)
        shika_rel_path = os.path.relpath(shika_repo_file, ".")
        if os.path.exists(shika_rel_path) is True:
            self.crystal_report_paths.append(shika_rel_path)
        else:
            self.log.warning("shika report html is not found: {}".format(shika_rel_path))

        thum_path = "{}/{}/scan{:02d}/2d/_spotfinder/thumb_2d/".format(d.root_dir, d.prefix, d.n_mount)
        thum_rel_path = os.path.relpath(thum_path, ".")
        if os.path.exists(thum_rel_path) is True:
            self.crystal_report_paths.append(thum_rel_path)
        else:
            self.log.warning("spotfinder thumbnail directory is not found: {}".format(thum_rel_path))

        good_str += f"""
    <td><a href="{shika_rel_path}">MAP</a></td>
  </tr>
        """

        if d.isDone != 0:
            return good_str
        else:
            return "NO_INFO"


class Toilet:
    def __init__(self, zoo_path, prefix, beamline):
        self.log = logs.getChild("toilet")
        self.zoo_path = zoo_path
        self.prefix = prefix
        self.beamline = beamline
        self.arc_files = []

    def multi_merge_log_kamo(self):
        merge_dirs = glob.glob("{}/**/merge_*/".format(self.zoo_path), recursive=True)
        output = ""
        for merge_dir in merge_dirs:
            log_paths = glob.glob("{}/**/multi_merge.log".format(merge_dir), recursive=True)
            if len(log_paths) > 0:
                for log_path in log_paths:
                    with open(log_path, "r") as fin:
                        proc_flag = 0
                        for line in fin:
                            if line.count("ERROR: No clusters satisfied the specified conditions for merging"):
                                proc_flag = 1001
                            if line.count("Normal exit at"):
                                ok_dir = os.path.dirname(os.path.relpath(log_path))
                                self.log.info("ok_dir: {} {}".format(ok_dir, proc_flag))
                                output += "{}\n".format(ok_dir)
                                break
        with open("send_data.csv", "w") as fout:
            fout.write(output)

    def make_html(self, inc_cry_info=False, zoom_capture=False):
        zoo_files = glob.glob("{}/*.db".format(self.zoo_path))

        if len(zoo_files) == 0:
            self.log.error("no zoo.db file")
            return

        html_files = []
        for ix, zoo_file in enumerate(zoo_files):
            zoo_size = os.path.getsize(zoo_file)
            if zoo_size < 1000:
                self.log.warning("too small: skipped {} {}".format(zoo_size, zoo_file))
            else:
                self.log.info("zoo_file: {}".format(zoo_file))
                zoo_repo = ZOOReporter(zoo_file, self.beamline, zoom_capture)
                html_files.append(zoo_repo.make_html("{}_{:02d}".format(self.prefix, ix)))
                if inc_cry_info is True:
                    # SHIKA report & crystal captured images
                    self.arc_files += zoo_repo.crystal_report_paths
                    self.log.debug(self.arc_files)

        return html_files

    def make_all_archive(self, mtz_option=True, inc_cry_info=False, zoom_capture=False):
        now_min = datetime.now().strftime("%Y%m%d%H%M")
        arc_out = "{}_{}.tgz".format(now_min, self.prefix)

        html_files = self.make_html(inc_cry_info, zoom_capture)

        for html_file in html_files:
            html_file_rel_path = os.path.relpath(html_file, ".")
            self.arc_files.append(html_file_rel_path)

        kamo_path = "{}/_kamoproc/".format(self.zoo_path)
        kamo_abs_path = os.path.abspath(kamo_path)

        if os.path.exists(kamo_abs_path) is True:
            # making report for large wedge
            unko = Unko(kamo_abs_path)
            reflection_files = unko.make_report_large_wedge(mtz_option=mtz_option)
            self.log.info("reflection files = {}".format(reflection_files))

            self.arc_files += reflection_files

            xds_repo = XDSReporter(kamo_abs_path)
            xds_repo.make_html()

            self.arc_files.append(os.path.relpath(os.path.join(kamo_abs_path, "correct.html")))
            self.arc_files.append(os.path.relpath(os.path.join(kamo_abs_path, "contents")))

        dirs = [d for d in os.listdir(self.zoo_path) if os.path.isdir(os.path.join(self.zoo_path, d))]

        if mtz_option is True:
            check_list = ["XSCALE.LP", "XSCALE.INP", "aniso.log", "pointless.log"]
        else:
            check_list = ["xscale.hkl", "XSCALE.LP", "XSCALE.INP", "aniso.log", "pointless.log"]

        for each_dir in dirs:
            if each_dir == "_kamoproc" or each_dir.count("_kamo_"):
                abs_kamo = os.path.abspath(os.path.join(self.zoo_path, each_dir))
                unko = Unko(abs_kamo)
                ok_paths = unko.get_list_finished_merge_dirs()
                final_run_paths = unko.get_final_result_paths(ok_paths)
                html_report_paths = unko.get_report_html_paths(ok_paths)
                self.arc_files += html_report_paths
                reflection_paths = unko.get_reflection_paths(final_run_paths, check_list=check_list, is_mtz=mtz_option)
                self.arc_files += reflection_paths

        with open(os.path.join(self.zoo_path, "arc.lst"), "w") as fout:
            for arc_target in self.arc_files:
                fout.write("{}\n".format(arc_target))

        command = "tar czvf {} --files-from={}/arc.lst".format(arc_out, self.zoo_path)
        self.log.info("command={}".format(command))
        subprocess.run(command, shell=True)


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix", nargs="?")
    parser.add_argument("-b", "--beamline", choices=["BL32XU", "BL45XU", "BL41XU"],
                        help="type of input method")
    parser.add_argument("-u", "--unmerged_hkl", action="store_true", default=False,
                        help="option to choose mode to archive 'unmerged hkl' files instead of MTZ file")
    parser.add_argument("-c", "--with_crystal_info", action='store_true', default=False,
                        help="option to choose whether crystal information is included or not.")
    parser.add_argument("-z", "--zoom_capture", action='store_true', default=False,
                        help="option to choose whether zoom capture image is included or not.")
    rcv_args = parser.parse_args()
    return rcv_args


if __name__ == "__main__":
    logs = Logger("goto_toilet.log").logger
    argv = getargs()

    if os.path.isdir("./_kamoproc") is False:
        logs.error("not found _kamoproc")
        sys.exit()

    cwd = os.getcwd()
    if argv.prefix is None:
        argv.prefix = os.path.basename(cwd)

    toilet = Toilet(cwd, argv.prefix, argv.beamline)
    toilet.multi_merge_log_kamo()

    toilet.make_all_archive(
        mtz_option=(not argv.unmerged_hkl),
        inc_cry_info=argv.with_crystal_info,
        zoom_capture=argv.zoom_capture
    )
