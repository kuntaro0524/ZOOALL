import sys
import os
import argparse
import logging.handlers
import glob
import sqlite3
import numpy
from datetime import datetime

script_tmp = """#!/bin/sh
# 2 dmin values should be evaluated.
# Merging process will be applied to datasets with better thresholds
# of completeness/redundancy.
# When a "wrongly" shorter dmin(higher resolution) is set here, 
# completeness value becomes very low for bad datasets and this 
# process does not reach to merging/scaling stages.
dmin_start_1={half_corner_res:.2f}

# dmin for CC calculation
# this should be set for each dmin values
# Very simple calculation (modify 'cc_margin' if you need)
# cc_dmin = dmin_start + cc_margin
cc_dmin={cc_dmin:.2f}

# Minimum normal/anomalous completeness
# Normal completeness
min_cmpl=10
# Anomalous completeness
min_acmpl=10

# Minimum anomalous redundancy
min_aredun=2.0

# Maximum number of cluster
max_clusters=10

# Memory disk
use_ramdisk=true

# Number of cores
nproc=8

kamo.auto_multi_merge \
filtering.choice=cell filtering.cell_iqr_scale=2.5 \
csv="{csv_file}" \
workdir={workdir}/ \
prefix=merge_blend_${{dmin_start_1}}S_ \
cell_method=reindex \
reject_method=framecc+lpstats \
rejection.lpstats.stats=em.b+bfactor \
merge.max_clusters=${{max_clusters}} \
merge.d_min_start=$dmin_start_1 \
merge.clustering=blend \
merge.blend.min_cmpl=$min_cmpl \
merge.blend.min_acmpl=$min_acmpl \
merge.blend.min_aredun=$min_aredun \
xscale.degrees_per_batch={degrees_per_batch:.1f} \
xscale.reference=bmin \
batch.engine=sge \
merge.batch.engine=slurm \
merge.batch.par_run=merging \
merge.nproc=$nproc \
merge.batch.nproc_each=$nproc \
xscale.use_tmpdir_if_available=${{use_ramdisk}} \
batch.sge_pe_name=par &

kamo.auto_multi_merge \
filtering.choice=cell filtering.cell_iqr_scale=2.5 \
csv="{csv_file}" \
workdir={workdir}/ \
prefix=merge_ccc_${{dmin_start_1}}S_ \
cell_method=reindex \
reject_method=framecc+lpstats \
rejection.lpstats.stats=em.b+bfactor \
merge.max_clusters=${{max_clusters}} \
xscale.reference=bmin \
merge.d_min_start=$dmin_start_1 \
merge.clustering=cc \
merge.cc_clustering.d_min=${{cc_dmin}} \
merge.cc_clustering.min_cmpl=$min_cmpl \
merge.cc_clustering.min_acmpl=$min_acmpl \
merge.cc_clustering.min_aredun=$min_aredun \
xscale.degrees_per_batch={degrees_per_batch:.1f} \
batch.engine=sge \
merge.batch.engine=slurm \
merge.batch.par_run=merging \
merge.nproc=$nproc \
merge.batch.nproc_each=$nproc \
xscale.use_tmpdir_if_available=${{use_ramdisk}} \
batch.sge_pe_name=par &
"""


class Nikudango:
    def __init__(self, zoo_root_path, beamline, logger):
        self.log = logger
        self.zoo_root_path = os.path.abspath(zoo_root_path)
        self.beamline = beamline

        self.isPrep = False
        self.debug = False

        # Default processing directories and modes
        self.kamo_options = [('_kamoproc', 'multi'), ('_kamo_30deg', 'all')]
        # self.kamo_options = [('_kamo_10deg','all')]

        self.run_output = ["#!/bin/sh\n"]
        self.multi_dict_for_procs = {}

    def set_conds(self, kamoroot_list, mode_list):
        self.kamo_options = []
        for kamoroot, mode in zip(kamoroot_list, mode_list):
            self.kamo_options.append((kamoroot, mode))
        self.log.info("KAMO Options: {}".format(self.kamo_options))

    def is_kamo_proc_finished(self, kamo_proc_dir):
        check_file = os.path.join(kamo_proc_dir, "decision.log")
        if os.path.exists(check_file) is True:
            error_message = None
            with open(check_file, "r") as fin:
                for ln in fin:
                    if ln.rfind("error:") != -1:
                        error_message = ln.replace("error:", "").strip()
                    if ln.rfind("failed") != -1:
                        error_message = ln.strip()
                    if ln.rfind("finished") != -1:
                        # self.log.info("KAMO done")
                        return True
                self.log.warning(error_message)
        return False

    def calc_half_corner(self, cond):
        wavelength = cond['wavelength']
        dist_ds = cond['dist_ds']

        min_dim = 500.0
        if self.beamline.lower() == "bl32xu":
            min_dim = 233.0
        elif self.beamline.lower() == "bl45xu":
            min_dim = 311.2
        elif self.beamline.lower() == "bl41xu":
            min_dim = 311.2

        # half corner resolution
        half_corner_radius = numpy.sqrt(5.0) / 2.0 * (min_dim / 2.0)
        theta_re = 0.5 * numpy.arctan(half_corner_radius / dist_ds)

        dmin_re = wavelength / 2.0 / numpy.sin(theta_re)
        return dmin_re

    def get_data_dir_list_from_zoodb(self, kamo_path, merge_mode):
        # KAMO absolute path
        kamo_abs = os.path.abspath(kamo_path)
        self.log.info("data processing in {}".format(kamo_abs))
        self.log.info("processing mode={}".format(merge_mode))

        # checking list

        if merge_mode == 'all':
            acceptable_modes = ['multi', 'single', 'helical', 'mixed']
        elif merge_mode == 'multi':
            acceptable_modes = ['multi']
        else:
            return []

        conds = []
        zoodbs = glob.glob("{}/zoo*db".format(self.zoo_root_path))
        for zoodb in zoodbs:
            con = sqlite3.connect(zoodb)
            cur = con.cursor()
            cur.execute("SELECT * FROM ESA")
            for row in cur.fetchall():
                cond = dict(zip([d[0] for d in cur.description], row))
                if cond["isDone"] != 0:
                    conds.append(cond)

        dict_for_procs = {}
        n_data = 0
        n_finished = 0
        for cond in conds:
            data_dir = "{}-{:0>2d}/data{:0>2d}".format(cond["puckid"], cond["pinid"], cond["n_mount"])
            data_abs = os.path.join(cond["root_dir"], data_dir)
            logfiles = glob.glob("{}/*.log".format(data_abs))
            if len(logfiles) == 0:
                self.log.warning("data was not collected: {}".format(data_dir))
                continue
            if cond["mode"] in acceptable_modes:
                self.log.info("exp_mode is included: {}".format(data_abs))
            else:
                self.log.warning("exp_mode is not included: {}".format(data_abs))
                continue

            kamo_data_dir = os.path.join(kamo_abs, data_dir)
            self.log.info("%s is checking" % kamo_data_dir)
            if os.path.exists(kamo_data_dir) is False:
                self.log.error("{} does not exist".format(kamo_data_dir))
                sys.exit()
            else:
                self.log.info("{} is done".format(kamo_data_dir))

            half_corner_resol = self.calc_half_corner(cond)

            if half_corner_resol in dict_for_procs:
                if cond["sample_name"] in dict_for_procs[half_corner_resol]:
                    dict_for_procs[half_corner_resol][cond["sample_name"]].append(
                        (kamo_data_dir, half_corner_resol, cond["sample_name"], cond["meas_name"], cond["mode"])
                    )
                else:
                    dict_for_procs[half_corner_resol][cond["sample_name"]] = [
                        (kamo_data_dir, half_corner_resol, cond["sample_name"], cond["meas_name"], cond["mode"])
                    ]
            else:
                dict_for_procs[half_corner_resol] = {
                    cond["sample_name"]: [
                        (kamo_data_dir, half_corner_resol, cond["sample_name"], cond["meas_name"], cond["mode"])
                    ]
                }

            for layer in os.listdir(kamo_data_dir):
                n_data += 1
                kamo_proc_dir = os.path.join(kamo_data_dir, layer)
                if os.path.exists(kamo_proc_dir) is True:
                    try:
                        if self.is_kamo_proc_finished(kamo_proc_dir) is True:
                            n_finished += 1
                    except Exception as e:
                        self.log.error(e)
                else:
                    self.log.info("skipping to check now: {}".format(kamo_proc_dir))

        if n_data != n_finished or n_finished == 0:
            self.log.error("There's a process that's not finished.: {}".format(merge_mode))
        else:
            self.log.info("all of procs completed")

        if merge_mode == "multi":
            self.multi_dict_for_procs = dict_for_procs
        if merge_mode == "all":
            remove_dict_for_procs = {}
            for reso, list_sample in dict_for_procs.items():
                remove_dict_for_procs[reso] = {}
                for sample_name, list_data in list_sample.items():
                    multi_flag = False
                    other_flag = False
                    for data in list_data:
                        if data[4] == "multi":
                            multi_flag = True
                        elif data[4] != "multi":
                            other_flag = True
                    if multi_flag is True and other_flag is False:
                        continue
                    else:
                        remove_dict_for_procs[reso][sample_name] = list_data
            return remove_dict_for_procs

        return dict_for_procs

    # KAMO automatic data merging requires 2 files for each.
    # 1) CSV file containing reflection file list for each group of same resolution limit.
    # 2) .sh file for running kamo.automerge with 'defined resolution limit'
    # isLargeWedge: defining ''
    def prep_merge_files(self, kamo_path, dict_for_procs, merge_prefix, script_dir="merge_inputs",
                         is_large_wedge=False):
        # Absolute directory of "KAMO" data processing
        kamo_abs = os.path.abspath(kamo_path)

        # Script files are stored into 'script_dir'
        scripts_dir = os.path.join(self.zoo_root_path, script_dir)
        if os.path.exists(scripts_dir) is False:
            os.makedirs(scripts_dir)
        self.log.info("All scripts for KAMO auto-merging will be made in %s" % scripts_dir)

        ix = 0
        for res, sample_names in dict_for_procs.items():
            csv_path = os.path.join(scripts_dir, "{}_merge_{:0>3d}.csv".format(merge_prefix, ix))
            csv_output = ["topdir,name,anomalous\n"]
            for sample_name, conds in sample_names.items():
                for cond in conds:
                    phasing_flg = "yes" if cond[3] == "phasing" else "no"
                    csv_output.append("{},{},{}\n".format(cond[0], sample_name, phasing_flg))
            print(csv_path, csv_output)
            with open(csv_path, "w") as csv_out:
                csv_out.writelines(csv_output)

            cc_dmin = res + 1.5
            degrees_per_batch = 5.0 if is_large_wedge is True else 1.0

            sh_path = os.path.join(scripts_dir, "{}_merge_{:0>3d}.sh".format(merge_prefix, ix))
            sh_output = script_tmp.format(
                half_corner_res=res,
                cc_dmin=cc_dmin,
                csv_file=csv_path,
                workdir=kamo_abs,
                degrees_per_batch=degrees_per_batch
            )
            with open(sh_path, "w") as sh_out:
                sh_out.write(sh_output)

            self.run_output.append("sh {}\n".format(sh_path))

            ix += 1

        return

    def makemake(self):
        # 'merge_mode' is used to select datasets
        # 'multi': merging multiple small wedge datasets
        # 'helical' : merging helical datasets only
        # 'single' : merging single datasets only
        # 'all' : merging all datasets having same 'sample_name' tags.

        for kamo_path, merge_mode in self.kamo_options:
            self.log.info("path={}, option={}".format(kamo_path, merge_mode))
            # Check an existence of the directory
            if os.path.exists(kamo_path) is False:
                self.log.info("{} does not exist...".format(kamo_path))
                continue

            dict_for_procs = self.get_data_dir_list_from_zoodb(kamo_path, merge_mode)
            if len(dict_for_procs) == 0:
                self.log.warning("No dataset [{}]: {}".format(merge_mode, kamo_path))
                continue

            self.prep_merge_files(kamo_path, dict_for_procs, "giri_{}".format(merge_mode))

        run_path = os.path.join(self.zoo_root_path, "all_run_test.sh")
        with open(run_path, "w") as run_out:
            run_out.writelines(self.run_output)

        return


class Logger:
    def __init__(self, log_path, name="NIKUDANGO"):
        log_form = logging.Formatter(fmt="[%(asctime)s.%(msecs)03d][%(name)s][%(levelname)s] %(message)s",
                                     datefmt="%Y-%m-%d %H:%M:%S")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_form)
        self.logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(log_form)
        self.logger.addHandler(file_handler)

        return


class DictDotNotation(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--beamline", choices=["BL32XU", "BL45XU", "BL41XU"], default="BL45XU")
    parser.add_argument("-k", "--dir", nargs="+", default=["_kamoproc", "_kamo_30deg"])
    parser.add_argument("-o", "--mode", nargs="+", default=["multi", "all"])
    parser.add_argument("-s", "--single", action='store_true', default=False)
    rcv_args = parser.parse_args()
    return rcv_args


if __name__ == "__main__":
    date = datetime.now().strftime("%y%m%d")
    logs = Logger("nikudango_{}.log".format(date)).logger
    argv = getargs()

    # Entire path
    zoo_root = "."

    if argv.single is False:
        logs.info("Normal data processing: BL={}".format(argv.beamline))
        nikudango = Nikudango(zoo_root, argv.beamline, logger=logs)
        nikudango.set_conds(argv.dir, argv.mode)
        nikudango.makemake()

    else:
        logs.info("Single data processing: BL={}".format(argv.beamline))
        nikudango = Nikudango(zoo_root, argv.beamline, logger=logs)
        nikudango.set_conds(argv.dir[:1], argv.mode[:1])
        nikudango.makemake()
