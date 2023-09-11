#!/bin/csh
unset autologout
/oys/xtal/cctbx/snapshots/upstream/build/bin/yamtbx.python /oys/xtal/cctbx/snapshots/upstream/modules/yamtbx/dataproc/auto/command_line/multi_prep_merging.py \
xdsdir=fukuda/12/multi_101-200/  \
xdsdir=fukuda/12/multi_101-200/ \
xdsdir=fukuda/12/multi_1-100/ \
xdsdir=fukuda/12/multi_201-300/ \
xdsdir=fukuda/12/multi_301-400/ \
xdsdir=fukuda/1266/01/ \
xdsdir=fukuda/1266/02/ \
xdsdir=fukuda/1266/03/ \
xdsdir=fukuda/1266/04/ \
xdsdir=fukuda/1266/05/ \
xdsdir=fukuda/1266/06/ \
xdsdir=fukuda/1266/07/ \
xdsdir=fukuda/1266/08/ \
xdsdir=fukuda/1266/09/ \
xdsdir=fukuda/1266/11/ \
xdsdir=fukuda/1266/12/ \
xdsdir=fukuda/1266/14/ \
xdsdir=fukuda/1266/15/ \
xdsdir=fukuda/1266/16/ \
workdir=merge_manual \
