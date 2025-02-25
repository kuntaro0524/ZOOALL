import os, sys, math, time, datetime

dmin = float(sys.argv[1])
comp_thresh = float(sys.argv[2])
min_redun = float(sys.argv[3])
n_max_cluster = int(sys.argv[4])

dc_csv = open("../data_proc.csv","r")
lines = dc_csv.readlines()

ttime = datetime.datetime.now()
timestr=datetime.datetime.strftime(ttime, '%y%m%d%H%M%S')

new_csv_name = "data_proc_%s.csv" % timestr
new_csv_file = open(new_csv_name, "w")

line_index = 0
new_csv_file.write("topdir,name,anomalous\n")

for line in lines:
    if line.rfind("topdir") != -1:
        continue
    else:
        new_csv_file.write(line)


comstrings = """
/oys/xtal/cctbx/snapshots/dials-v1-8-3-dev/build/bin2/kamo.auto_multi_merge \
  csv=%(new_csv_name)s \
  workdir=$PWD \
  prefix=merge_ccc_%(timestr)s_ \
  cell_method=reindex \
  merge.max_clusters=%(n_max_cluster)d \
  merge.d_min_start=%(dmin)s \
  merge.clustering=cc \
  merge.cc_clustering.min_acmpl=%(comp_thresh)s \
  merge.cc_clustering.min_aredun=%(min_redun)s \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging  &

/oys/xtal/cctbx/snapshots/dials-v1-8-3-dev/build/bin2/kamo.auto_multi_merge \
  csv=%(new_csv_name)s \
  workdir=$PWD \
  prefix=merge_blend_%(timestr)s_ \
  cell_method=reindex \
  merge.max_clusters=%(n_max_cluster)d \
  merge.d_min_start=%(dmin)s \
  merge.clustering=blend \
  merge.cc_clustering.min_acmpl=%(comp_thresh)s \
  merge.cc_clustering.min_aredun=%(min_redun)s \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging  &

""" % dict(new_csv_name = new_csv_name, timestr = timestr, min_redun = min_redun, comp_thresh = comp_thresh, n_max_cluster = n_max_cluster, dmin = dmin)

new_proc_sh = open("automerge_%s.sh" % timestr, "w")
new_proc_sh.write("%s"%comstrings)
