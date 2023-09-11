#!/bin/sh
# 2 dmin values should be evaluated.
# Merging process will be applied to datasets with better thresholds
# of completeness/redundancy.
# When a "wrongly" shorter dmin(higher resolution) is set here, 
# completeness value becomes very low for bad datasets and this 
# process does not reach to merging/scaling stages.
dmin_start_1=2.0
dmin_start_2=4.0
cc_margin=1.5

# false : only 'dmin_start_1' is used
do_lowreso=true

# false: small wedge data collection
# true: merging large wedge data
is_large_wedge=false

# dmin for CC calculation
# this should be set for each dmin values
# Very simple calculation (modify 'cc_margin' if you need)
# cc_dmin = dmin_start + cc_margin
cc_dmin_1=`echo "$dmin_start_1 + $cc_margin" | bc`
cc_dmin_2=`echo "$dmin_start_2 + $cc_margin" | bc`

# Minimum normal/anomalous completeness
# Normal completeness
min_cmpl=80
# Anomalous completeness
min_acmpl=80

# Minimum anomalous redundancy
min_aredun=2.0

# Maximum number of cluster
max_clusters=10

# Memory disk
use_ramdisk=true
# CSV file for automatic merging
csv_file="./data_proc.csv"

# Number of cores
nproc=8

# Initial setting for degrees_per_batch in XSCALE
if $is_large_wedge; then
degrees_per_batch=5.0
else
degrees_per_batch=1.0
fi

kamo.auto_multi_merge \
  filtering.choice=cell filtering.cell_iqr_scale=2.5 \
  csv=$csv_file \
  workdir=$PWD/ \
  prefix=merge_blend_${dmin_start_1}S_ \
  cell_method=reindex \
  reject_method=framecc+lpstats \
  rejection.lpstats.stats=em.b+bfactor \
  merge.max_clusters=${max_clusters} \
  merge.d_min_start=$dmin_start_1 \
  merge.clustering=blend \
  merge.blend.min_cmpl=$min_cmpl \
  merge.blend.min_acmpl=$min_acmpl \
  merge.blend.min_aredun=$min_aredun \
  xscale.degrees_per_batch=$degrees_per_batch \
  xscale.reference=bmin \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
  merge.nproc=$nproc \
  merge.batch.nproc_each=$nproc \
  xscale.use_tmpdir_if_available=${use_ramdisk} \
  batch.sge_pe_name=par &

kamo.auto_multi_merge \
  filtering.choice=cell filtering.cell_iqr_scale=2.5 \
  csv=$csv_file \
  workdir=$PWD/ \
  prefix=merge_ccc_${dmin_start_1}S_ \
  cell_method=reindex \
  reject_method=framecc+lpstats \
  rejection.lpstats.stats=em.b+bfactor \
  merge.max_clusters=${max_clusters} \
  xscale.reference=bmin \
  merge.d_min_start=$dmin_start_1 \
  merge.clustering=cc \
  merge.cc_clustering.d_min=${cc_dmin_1} \
  merge.cc_clustering.min_cmpl=$min_cmpl \
  merge.cc_clustering.min_acmpl=$min_acmpl \
  merge.cc_clustering.min_aredun=$min_aredun \
  xscale.degrees_per_batch=$degrees_per_batch \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
  merge.nproc=$nproc \
  merge.batch.nproc_each=$nproc \
  xscale.use_tmpdir_if_available=${use_ramdisk} \
  batch.sge_pe_name=par &

if $do_lowreso; then

kamo.auto_multi_merge \
  filtering.choice=cell filtering.cell_iqr_scale=2.5 \
  csv=$csv_file \
  workdir=$PWD/ \
  prefix=merge_blend_${dmin_start_2}S_ \
  cell_method=reindex \
  reject_method=framecc+lpstats \
  rejection.lpstats.stats=em.b+bfactor \
  merge.max_clusters=${max_clusters} \
  merge.d_min_start=$dmin_start_2 \
  merge.clustering=blend \
  merge.blend.min_cmpl=$min_cmpl \
  merge.blend.min_acmpl=$min_acmpl \
  merge.blend.min_aredun=$min_aredun \
  xscale.degrees_per_batch=$degrees_per_batch \
  xscale.reference=bmin \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
  xscale.use_tmpdir_if_available=${use_ramdisk} \
  merge.nproc=$nproc \
  merge.batch.nproc_each=$nproc \
  batch.sge_pe_name=par &

kamo.auto_multi_merge \
  filtering.choice=cell filtering.cell_iqr_scale=2.5 \
  csv=$csv_file \
  workdir=$PWD/ \
  prefix=merge_ccc_${dmin_start_2}S_ \
  cell_method=reindex \
  reject_method=framecc+lpstats \
  rejection.lpstats.stats=em.b+bfactor \
  merge.max_clusters=${max_clusters} \
  xscale.reference=bmin \
  merge.d_min_start=$dmin_start_2 \
  merge.clustering=cc \
  merge.cc_clustering.d_min=${cc_dmin_2} \
  merge.cc_clustering.min_cmpl=$min_cmpl \
  merge.cc_clustering.min_acmpl=$min_acmpl \
  merge.cc_clustering.min_aredun=$min_aredun \
  xscale.degrees_per_batch=$degrees_per_batch \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
  xscale.use_tmpdir_if_available=${use_ramdisk} \
  merge.nproc=$nproc \
  merge.batch.nproc_each=$nproc \
  batch.sge_pe_name=par &

else
echo "low resolution merging is skipped."
fi
