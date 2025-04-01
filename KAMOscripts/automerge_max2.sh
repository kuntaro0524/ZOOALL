#!/bin/sh
dmin_start_1=1.7
dmin_start_2=5.0
cc_margin=1.5

# dmin for CC calculation
cc_dmin_1=`echo "$dmin_start_1 + $cc_margin" | bc`
cc_dmin_2=`echo "$dmin_start_2 + $cc_margin" | bc`

# Minimum cnomalous completeness
min_acmpl=90.0
# Minimum anomalous redundancy
min_aredun=2.0
# Memory disk
use_ramdisk=true
# CSV file for automatic merging
csv_file="./data_proc.csv"

kamo.auto_multi_merge \
  filtering.choice=cell filtering.cell_iqr_scale=2.5 \
  csv=$csv_file \
  workdir=$PWD/ \
  prefix=merge_blend_start_${$dmin_start_1}A_ \
  cell_method=reindex \
  reject_method=framecc+lpstats \
  rejection.lpstats.stats=em.b+bfactor \
  merge.max_clusters=50 \
  merge.d_min_start=$dmin_start_1 \
  merge.clustering=blend \
  merge.cc_clustering.min_acmpl=$min_acmpl \
  merge.cc_clustering.min_aredun=$min_aredun \
  xscale.degrees_per_batch=1.0 \
  xscale.reference=bmin \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
  xscale.use_tmpdir_if_available=${use_ramdisk} \
  batch.nproc_each=8 \
  batch.sge_pe_name=par &

kamo.auto_multi_merge \
  filtering.choice=cell filtering.cell_iqr_scale=2.5 \
  csv=$csv_file \
  workdir=$PWD/ \
  prefix=merge_ccc_start_${$dmin_start_1}A_ \
  cell_method=reindex \
  reject_method=framecc+lpstats \
  rejection.lpstats.stats=em.b+bfactor \
  merge.max_clusters=50 \
  xscale.reference=bmin \
  merge.d_min_start=$dmin_start_1 \
  merge.clustering=cc \
  merge.cc_clustering.d_min=${cc_dmin_1} \
  merge.cc_clustering.min_acmpl=$min_acmpl \
  merge.cc_clustering.min_aredun=$min_aredun \
  xscale.degrees_per_batch=1.0 \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
  xscale.use_tmpdir_if_available=${use_ramdisk} \
  batch.nproc_each=8 \
  batch.sge_pe_name=par &

kamo.auto_multi_merge \
  filtering.choice=cell filtering.cell_iqr_scale=2.5 \
  csv=$csv_file \
  workdir=$PWD/ \
  prefix=merge_blend_start_${$dmin_start_2}A_ \
  cell_method=reindex \
  reject_method=framecc+lpstats \
  rejection.lpstats.stats=em.b+bfactor \
  merge.max_clusters=50 \
  merge.d_min_start=$dmin_start_2 \
  merge.clustering=blend \
  merge.cc_clustering.min_acmpl=$min_acmpl \
  merge.cc_clustering.min_aredun=$min_aredun \
  xscale.degrees_per_batch=1.0 \
  xscale.reference=bmin \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
  xscale.use_tmpdir_if_available=${use_ramdisk} \
  batch.nproc_each=8 \
  batch.sge_pe_name=par &

kamo.auto_multi_merge \
  filtering.choice=cell filtering.cell_iqr_scale=2.5 \
  csv=$csv_file \
  workdir=$PWD/ \
  prefix=merge_ccc_start_${$dmin_start_2}A_ \
  cell_method=reindex \
  reject_method=framecc+lpstats \
  rejection.lpstats.stats=em.b+bfactor \
  merge.max_clusters=50 \
  xscale.reference=bmin \
  merge.d_min_start=$dmin_start_2 \
  merge.clustering=cc \
  merge.cc_clustering.d_min=${cc_dmin_2} \
  merge.cc_clustering.min_acmpl=$min_acmpl \
  merge.cc_clustering.min_aredun=$min_aredun \
  xscale.degrees_per_batch=1.0 \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
  xscale.use_tmpdir_if_available=${use_ramdisk} \
  batch.nproc_each=8 \
  batch.sge_pe_name=par &

