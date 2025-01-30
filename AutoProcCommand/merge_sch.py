# (c) RIKEN & JASRI
# Author: Nobuhiro Mizuno

import os
import pandas
import glob
import re
import time
import subprocess
import yaml
import argparse
import shutil
import math
import logging.handlers


class Logger:
    def __init__(self, log_path, name="stbio"):
        log_form = logging.Formatter(fmt="[%(asctime)s.%(msecs)03d][%(name)s][%(levelname)s] %(message)s",
                                     datefmt="%Y-%m-%d %H:%M:%S")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_form)
        self.logger.addHandler(stream_handler)

        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_path, when="midnight", interval=1, encoding="utf-8"
        )
        file_handler.setFormatter(log_form)
        self.logger.addHandler(file_handler)

        return


class SchMerge:
    def __init__(self, logger, interval=60, limit=5):
        self.log = logger
        self.interval = interval
        self.limit = limit

        self.name_list = {}

        self.keep = None
        self.run_list = {}
        self.error_list = []

    def run(self, work_dir):
        if self.log is not None:
            self.log.info("merge scheduling start.")

        self.keep = True
        while self.keep:
            run_num = 0
            for key, item in self.run_list.items():
                status = item["status"]
                sample_name = item["sample_name"]
                sh_path = item["sh_path"]
                csv_path = item["csv_path"]
                out_dir = item["out"]
                csv_in = pandas.read_csv(csv_path)
                data_paths = csv_in["topdir"].unique().tolist()
                print(data_paths)
                cutoff_flag = None
                if status == "finished":
                    continue
                if status == "running" or status == "waiting":
                    log_list = glob.glob("{}/{}/merge_*_{}/slurm-*.out".format(work_dir, out_dir, sample_name))
                    log_list += glob.glob("{}/{}/merge_*_{}/multimerge.sh.o*".format(work_dir, out_dir, sample_name))
                    log_list += glob.glob("{}/{}/merge_*_{}/par.o*".format(work_dir, out_dir, sample_name))
                    cnt_log = len(log_list)
                    self.log.debug(cnt_log)
                    if cnt_log != 0:
                        cnt_fin = 0
                        for log_path in log_list:
                            with open(log_path, "r") as log_inp:
                                for line in log_inp:
                                    if line.count("Error in unpickling result in"):
                                        e_msg = "Ignorable errors [{}] {}".format(key, sh_path)
                                        self.log.warning(e_msg)
                                    elif line.count("IOError: [Errno 2]"):
                                        e_msg = "Ignorable errors [{}] {}".format(key, sh_path)
                                        self.log.warning(e_msg)
                                    elif line.count("IndexError: list index out of range"):
                                        e_msg = "Ignorable errors [{}] {}".format(key, sh_path)
                                        self.log.warning(e_msg)
                                    elif line.count("UnboundLocalError: local variable"):
                                        e_msg = "Not enough data [{}] {}".format(key, sh_path)
                                        self.log.error(e_msg)
                                        if e_msg not in self.error_list:
                                            self.error_list.append("{}\n".format(e_msg))
                                            for data_dir in data_paths:
                                                self.error_list.append("    {}\n".format(data_dir))
                                    elif line.count("RuntimeWarning: invalid value encountered in sqrt"):
                                        cutoff_flag = True
                                        e_msg = "Cutoff error [{}] {}".format(key, sh_path)
                                        self.log.error(e_msg)
                                        if e_msg not in self.error_list:
                                            self.error_list.append("{}\n".format(e_msg))
                                            for data_dir in data_paths:
                                                self.error_list.append("    {}\n".format(data_dir))
                                    elif line.count("ERROR"):
                                        e_msg = "Comp and Redundancy error [{}] {}".format(key, sh_path)
                                        self.log.error(e_msg)
                                        if e_msg not in self.error_list:
                                            self.error_list.append("{}\n".format(e_msg))
                                            for data_dir in data_paths:
                                                self.error_list.append("    {}\n".format(data_dir))
                                    elif line.count("Error"):
                                        e_msg = "Unknown error [{}] {}".format(key, sh_path)
                                        self.log.warning(e_msg.strip())
                                        if e_msg not in self.error_list:
                                            self.error_list.append("{}\n".format(e_msg))
                                            for data_dir in data_paths:
                                                self.error_list.append("    {}\n".format(data_dir))
                                    elif line.find("finished at") == 0:
                                        cnt_fin += 1
                        print(sample_name, cnt_log, cnt_fin, self.run_list[key]["status"])
                        if cutoff_flag is True:
                            for log_path in log_list:
                                msg = None
                                if log_path.count("slurm-"):
                                    job_id = log_path[(log_path.find("slurm-") + 6):log_path.find(".out")]
                                    msg = "scancel %s" % job_id
                                elif log_path.count("multimerge.sh.o"):
                                    job_id = log_path[(log_path.find("multimerge.sh.o") + 15):]
                                    msg = "qdel %s" % job_id
                                elif log_path.count("par.o"):
                                    job_id = log_path[(log_path.find("par.o") + 5):]
                                    msg = "qdel %s" % job_id
                                if msg is not None:
                                    subprocess.call(msg, shell=True)
                                merge_dir = os.path.dirname(log_path)
                                kamo_dir = os.path.dirname(merge_dir)
                                error_dir = "%s/errors" % kamo_dir
                                error_merge = "%s/%s" % (error_dir, os.path.basename(merge_dir))
                                if not os.path.exists(error_dir):
                                    os.makedirs(error_dir)
                                if os.path.exists(error_merge):
                                    self.run_list[key]["status"] = "error"
                                    status = "error"
                                else:
                                    shutil.move(merge_dir, error_dir)
                                    self.change_sh_resolution(sh_path)
                                    self.run_list[key]["status"] = "waiting"
                                    status = "waiting"
                        elif cnt_log == cnt_fin:
                            self.log.info("finished merge job: {}".format(key))
                            self.run_list[key]["status"] = "finished"
                            status = "finished"
                        elif status == "running":
                            run_num += 1
                        elif status == "waiting":
                            self.run_list[key]["status"] = "running"
                            status = "running"
                            run_num += 1
                if run_num >= self.limit:
                    break
                if status == "waiting":
                    self.log.info("started merge job [{}] {}".format(key, sh_path))
                    subprocess.call(["sh", sh_path])
                    self.run_list[key]["status"] = "running"
                    status = "running"
                    run_num += 1
            self.log.info("run number: %d" % run_num)
            # self.log.info(self.run_list)

            # error_list = set(self.error_list)
            error_list = self.error_list
            with open("merge_sch.yaml", "w") as f_yaml:
                yaml.dump(self.run_list, f_yaml, default_flow_style=False)
            with open("merge_sch.error", "w") as f_error:
                f_error.writelines(error_list)

            if run_num == 0:
                self.log.info("all job is finished.")
                break

            time.sleep(self.interval)

        return self.error_list

    def change_sh_resolution(self, sh_path):
        r_high = 100
        csv_path = sh_path.replace(".sh", ".csv")
        with open(csv_path, "r") as fin:
            for line in fin:
                if line.count("_kamo_30deg"):
                    data_path = line.strip().split(",")[0].split("_kamo_30deg/")[1]
                    report_dir = "_kamo_30deg"
                elif line.count("_kamoproc"):
                    data_path = line.strip().split(",")[0].split("_kamoproc/")[1]
                    report_dir = "_kamoproc"
                else:
                    continue

                print(report_dir, data_path)

                with open("%s/report.html" % report_dir, "r") as f_report:
                    for ln in f_report:
                        if ln.count(data_path) and ln.count("<td>"):
                            r_cnt = ln.strip().split("<td>")
                            r_cut = r_cnt[8].replace("</td>", "")
                            if r_cut != "nan":
                                r_cut = float(r_cut)
                                if r_cut < r_high:
                                    r_high = r_cut

        cc_cut = math.floor(r_high) if r_high >= 3.0 else r_high - 0.2
        blend_cut = cc_cut - 1 if cc_cut >= 3.0 else cc_cut - 0.2

        output = []
        with open(sh_path, "r") as fin:
            for line in fin:
                if line.count("dmin_start_1="):
                    output.append("dmin_start_1=%.2f\n" % blend_cut)
                elif line.count("cc_dmin="):
                    output.append("cc_dmin=%.2f\n" % cc_cut)
                else:
                    output.append(line)

        print(output)

        with open(sh_path, "w") as fout:
            fout.writelines(output)

        if self.log is not None:
            self.log.info("high resolution: %f" % r_high)
        return r_high

    def slice_input(self, current_dir, merge_path="merge_inputs", slice_path="merge_inputs_slice"):
        merge_abspath = os.path.join(current_dir, merge_path)
        slice_abspath = os.path.join(current_dir, slice_path)
        if not os.path.exists(current_dir) or not os.path.exists(merge_abspath):
            if self.log is not None:
                self.log.error("directory not found..")
            return {"status": "error", "message": "directory not found"}
        if not os.path.exists(slice_abspath):
            os.makedirs(slice_abspath)

        csv_files = glob.glob("{}/*.csv".format(merge_abspath))
        all_data = pandas.DataFrame()
        multi_data = pandas.DataFrame()
        for csv_name in csv_files:
            csv_inp = pandas.read_csv(csv_name)
            self.log.debug("{}\n{}".format(csv_name, csv_inp))
            if csv_name.count("multi"):
                multi_data = pandas.concat([multi_data, csv_inp], ignore_index=True)
            else:
                all_data = pandas.concat([all_data, csv_inp], ignore_index=True)

        self.log.debug("All\n{}".format(all_data))
        self.log.debug("Multi\n{}".format(multi_data))

        for csv_name in csv_files:
            csv_inp = pandas.read_csv(csv_name)
            csv_root = os.path.splitext(csv_name)[0]
            with open("{}.sh".format(csv_root), "r") as fin:
                sh_inp = fin.readlines()

            csv_uniques = csv_inp["name"].unique().tolist()
            for uname in csv_uniques:
                uname_org = uname
                if type(uname) is "str":
                    uname = uname.replace("/", "-")

                if csv_name.count("multi"):
                    out_base = "multi_{}".format(uname)
                else:
                    out_base = "all_{}".format(uname)
                csv_out = os.path.join(slice_abspath, "{}.csv".format(out_base))
                sh_out = os.path.join(slice_abspath, "{}.sh".format(out_base))
                if out_base not in self.name_list:
                    self.name_list[out_base] = {"dmin": 100}

                output = []
                out_dir = None
                for line in sh_inp:
                    if line.count("dmin_start_1="):
                        dmin = float(line.split("=")[1].strip())
                        if self.name_list[out_base]["dmin"] > dmin:
                            self.name_list[out_base]["dmin"] = dmin
                            out_tmp = "dmin_start_1={:.2f}\n".format(dmin)
                        else:
                            break
                    elif line.count("kamo.auto_multi_merge"):
                        out_tmp = re.sub('csv="(.*)"', 'csv="{}"'.format(csv_out), line)
                        if line.count("_kamoproc"):
                            out_dir = "_kamoproc"
                        else:
                            out_dir = "_kamo_30deg"
                    elif line.count("nproc="):
                        #out_tmp = re.sub('nproc=[0-9]+', 'nproc=1', line)
                        out_tmp = line
                    elif line.count("min_aredun=2.0"):
                        out_tmp = "min_aredun=1.5\n"
                    else:
                        out_tmp = line
                    output.append(out_tmp)

                if out_dir is None:
                    continue

                with open(sh_out, "w") as f_out:
                    f_out.writelines(output)

                if csv_name.count("multi"):
                    csv_tmp = multi_data[multi_data["name"] == uname_org]
                else:
                    csv_tmp = all_data[all_data["name"] == uname_org]
                csv_tmp.to_csv(csv_out, index=False)

                self.run_list[out_base] = {
                    "status": "waiting",
                    "sample_name": uname,
                    "sh_path": sh_out,
                    "csv_path": csv_out,
                    "out": out_dir
                }

        self.log.debug("\n{}".format(self.run_list))

    def slice_schedule(self, current_dir, merge_path="merge_inputs", slice_path="merge_inputs_slice"):
        merge_abspath = os.path.join(current_dir, merge_path)
        slice_abspath = os.path.join(current_dir, slice_path)
        if not os.path.exists(current_dir) or not os.path.exists(merge_abspath):
            if self.log is not None:
                self.log.error("directory not found..")
            return {"status": "error", "message": "directory not found"}
        if not os.path.exists(slice_abspath):
            os.makedirs(slice_abspath)

        csv_files = glob.glob("{}/*.csv".format(merge_abspath))
        for csv_name in csv_files:
            csv_inp = pandas.read_csv(csv_name)

            csv_root = os.path.splitext(csv_name)[0]
            csv_base = os.path.basename(csv_root)

            with open("{}.sh".format(csv_root), "r") as fin:
                sh_inp = fin.readlines()

            csv_uniques = csv_inp["name"].unique().tolist()
            for uname in csv_uniques:
                uname_org = uname 
                if type(uname) is "str":
                    uname = uname.replace("/", "-")
                output = []
                out_base = "{}_{}".format(csv_base, uname)
                csv_out = os.path.join(slice_abspath, "{}_{}.csv".format(csv_base, uname))
                sh_out = os.path.join(slice_abspath, "{}_{}.sh".format(csv_base, uname))

                out_dir = "_kamo_30deg"
                for line in sh_inp:
                    if line.count("kamo.auto_multi_merge"):
                        out_tmp = re.sub('csv="(.*)"', 'csv="{}"'.format(csv_out), line)
                        if line.count("_kamoproc"):
                            out_dir = "_kamoproc"
                    elif line.count("nproc="):
                        out_tmp = re.sub('nproc=[0-9]+', 'nproc=1', line)
                    elif line.count("min_aredun=2.0"):
                        out_tmp = "min_aredun=1.5\n"
                    else:
                        out_tmp = line
                    output.append(out_tmp)

                if not os.path.exists(csv_out):
                    with open(sh_out, "w") as f_out:
                        f_out.writelines(output)

                    csv_tmp = csv_inp[csv_inp["name"] == uname_org]
                    csv_tmp.to_csv(csv_out, index=False)

                self.run_list[out_base] = {
                    "status": "waiting",
                    "sample_name": uname,
                    "sh_path": sh_out,
                    "csv_path": csv_out,
                    "out": out_dir
                }

        with open("merge_sch.yaml", "w") as f_yaml:
            yaml.dump(self.run_list, f_yaml, default_flow_style=False)

        return


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--limit", default=5)
    parser.add_argument("-i", "--interval", default=60)
    rcv_args = parser.parse_args()
    return rcv_args


if __name__ == "__main__":
    args = getargs()
    parent = os.getcwd()
    logs = Logger(name="sp8auto", log_path=os.path.join(parent, "merge_sch.log")).logger
    sch_merge = SchMerge(logger=logs, interval=args.interval, limit=args.limit)
    sch_merge.slice_input(parent)
    sch_merge.run(parent)
